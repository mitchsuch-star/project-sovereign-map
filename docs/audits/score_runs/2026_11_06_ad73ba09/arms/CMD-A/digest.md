# Playtest digest — CMD-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force)…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2375, own corps) vs Mack (lost 18369) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Murat and Bernadotte never arrived, S… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte
  - ⚔ Archduke Charles (lost 2589) vs Bernadotte (lost 4959, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 897 · net +749 · threat 75 · provinces 28 · ceiling 7475 · army 174114 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2888 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,959 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (18,814; expect about 123,684 with the corps likely to arrive, up to 128,570 if all march; certain 18,814; a bad day (1 in 10) 107,284) vs Mack (substantial…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 419, own corps) vs Mack (lost 31817) — Davout, Massena, Napoleon and Teulie arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franconia — shall Davout engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franconia — shall Davout engage him? → 1 (first option: Archduke Charles at Franconia)
  - ↳ MUSTER — Davout (23,236; expect about 35,154 with the corps likely to arrive) vs Archduke Charles (48,961 men) at Franconia — the balance of force looks unfavorable.
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Davout attacks Archduke Charles' to read the muster before you commit — it costs nothing.
MUSTER — Davout (23,236; expect about 35,154 with the corps likely to arrive) vs Archduke Charles (48,961 men) at Franconia — the balance of force looks unfavorable.
  WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
  WILL NOT — Massena: has already marched this turn
  WILL NOT — Napoleon: has already marched this turn
  WILL NOT — Teulie: has already marched this turn
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Franconia would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  The band weighs more than the men: all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +3% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster can stand there fed.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 53,179 we muster) would cost ~399g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 83/100.
  Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Davout (23,236; expect about 35,154 with the corps likely to arrive) vs Archduke Charles (48,961 men) at Franconia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 4578, own corps) vs Archduke Charles (lost 2367) — Ney marched to Davout's guns as ordered. It was not enough.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte · Archduke Charles attacks Deroy
  - 🏴 Austria: Archduke Charles attacks Bernadotte — Franconia CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 911) vs Bernadotte (lost 7804) — A grievous defeat for Bernadotte, Sire. The losses are severe. And Bernadotte was taken on that field — Austria holds h…
  - ⚔ Archduke Charles (lost 1681) vs Deroy (lost 6940) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 1480 · net +1356 · threat 81 · provinces 28 (+0) · ceiling 10759 · army 148351 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 92
  - NET income 2590 · trade 450 · admin 50 · tribute 937 · upkeep 2300 · blockade 281 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, province_changed_hands, diplomatic_dp_regen)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Swabia — shall Ney engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Swabia — shall Ney engage him? → 1 (first option: Archduke Charles at Swabia)
- CMD `Davout, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Swabia — shall Davout engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Swabia — shall Davout engage him? → 1 (first option: Archduke Charles at Swabia)
  - ↳ MUSTER — Davout (17,539; expect about 119,850 with the corps likely to arrive, up to 129,769 if all march; certain 17,539; a bad day (1 in 10) 106,875) vs Archduke Charles (42,640 men) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 952, own corps) vs Archduke Charles (lost 9790) — Lannes, Murat, Massena, Napoleon and Teulie arrived to reinforce Davout! The timely arrival swung the battle in our fav… — The corps system brought Murat in. — The corps system brought Teulie in. — Berthier: the corps marched apart and arrived together.
- CMD `Lannes, move to Swabia` → ✗ Lannes is already in Swabia.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 667 gold (×3 at war) (×1.11 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 actions unused) Turn 4 begins!
- SPENT 667g on this turn's orders
- enemy phase: 8 actions, 0 attacks — Russia, Prussia, Spain and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×2, wait×2, fortify×1, naval_expedition×1, retreat×1, move×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 1932 · net +1237 · threat 87 · provinces 28 (+0) · ceiling 9692 · army 141729 · vassals Holland 97 · Kingdom of Italy 96 · Switzerland 91
  - NET income 2590 · trade 525 · admin 50 · tribute 937 · upkeep 2446 · blockade 329 · admiralty 90
- DISPATCH: Sire — Davout, Lannes, Murat, Massena, Napoleon and Teulie stand 100,207 men at Swabia, which feeds 60,000. 40,207 too many. 8,196 men lost in 2 turns. Bavaria's magazines feed us as our own — the ar…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franconia — shall Ney engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franconia — shall Ney engage him? → 1 (first option: Archduke Charles at Franconia)
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Swabia. Defense bonus: +7% now, 12% at dawn (the m…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1083, own corps) vs Archduke Charles (lost 18861) — Reinforcements! Lannes, Massena, Napoleon and Teulie marched onto the field beside Murat. The enemy's advantage melted …
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 3364 · net +1217 · threat 93 · provinces 28 (+0) · ceiling 10707 · army 135122 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 90
  - NET income 2590 · trade 587 · admin 50 · tribute 937 · upkeep 2264 · charges 225 · blockade 368 · admiralty 90
- DISPATCH: Sire — Marshal Murat holds the field at Franconia — Archduke Charles's corps is driven from Franconia yet again — broken, and fleeing.
  - TURN EVENTS 6
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG moment: Britain decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (14,795; expect about 99,459 with the corps likely to arrive, up to 107,104 if all march; certain 14,795; a bad day (1 in 10) 84,679) vs Archduke Charles (s…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 636, own corps) vs Archduke Charles (lost 5017, own corps) — Lannes, Massena, Napoleon and Teulie's timely arrival aided Ney. Murat, however, was conspicuously absent.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Lannes, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Bohemia — shall Lannes engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Bohemia — shall Lannes engage him? → 1 (first option: Archduke Charles at Bohemia)
  - ↳ MUSTER — Lannes (13,555; expect about 32,409 with the corps likely to arrive) vs Archduke Charles (small force) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 113, own corps) vs Archduke Charles (lost 4173) — Reinforcements! Ney and Murat marched onto the field beside Lannes. The enemy's advantage melted away. And Archduke Cha… — Berthier: the corps marched apart and arrived together.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✗ Cannot advance while engaged with Archduke John at Bohemia. He may withdraw onto friendly ground — Franconia, Tyrol — with 'Murat, retreat to Franconia' (free, −45% effe…
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 3 actions, 0 attacks — Russia, Prussia, Spain and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, unfortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #14 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #15 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +1 (99 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 66g a turn — 34g of income forfeited, 75g of occupation relieved, 25g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- ENVOYS WAITING 2 · Austria armistice losing · KingdomOfItaly client petition
- LEDGER treasury 5155 · net +1138 · threat 97 · provinces 28 (+0) · ceiling 11829 · army 127635 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 587 · admin 50 · tribute 962 · upkeep 2056 · charges 537 · blockade 368 · admiralty 90
- DISPATCH: Sire — the Archduke Charles of Austria is taken at Bohemia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 8
- DIPLO +6 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, diplomatic_ai_ai_treaty ×2)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Austria and the Ottoman Empire sign a Non-Aggression Pact
  - LOG diplomatic_ai_ai_treaty: Saxony and Austria sign a Non-Aggression Pact
  - LOG moment: Russia decrees the Magazines for 8 turns (5 authority)
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign an Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign an Open Borders Agreement

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Kutuzov is at Vienna, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Kutuz…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Kutuzov at Vienna instead.) → trust
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, move×1
- ORDER Murat [completed]: Murat arrives at Tyrol.
- ORDER Ney [completed]: Ney arrives at Tyrol.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 6686 · net +1030 · threat 95 · provinces 28 (+0) · ceiling 12616 · army 122960 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 587 · admin 50 · tribute 738 · upkeep 1664 · charges 813 · blockade 368 · admiralty 90
- DISPATCH: Sire — Lannes is no nearer home, and the safe passage leaves no turn to spare — he must march today. After that his corps will be interned where it stands.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +47 for France (9 battles, 2 decisives kept); the war is…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 8
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Archduke Charles is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, move to Bohemia` → ✗ Cannot enter Bohemia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Davout can already reach the body of the realm from wh…
- CMD `Murat, attack Archduke Charles` → ✗ Archduke Charles is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov attacks Lannes
  - ⚔ Kutuzov (lost 1245) vs Lannes (lost 4037) — Not one corps reached Lannes. Murat was expected; Lannes fought the battle single-handed.
  - verbs: wait×2, break_square×1, attack×1
  - POPUP marshal_audience: shadow_command, Marshal Massena asks for a command → detach
  -     ↳ Massena straightens. "You will not regret it, Sire." March him to Normandy and the front is his — the order i…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity, territory_compensate
  - POPUP diplomatic_dialogue: settlement_confirm #18 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with the Third Coalition — the table with Austria + Russia (4 pairs resolved). Status quo: Tyrol stays ours by the treaty — titled. Prisoners: Bernadotte comes home to Paris under this peace. Prisoners: Archduke Charles, our captive, goes home to Vienna under this peace — an Austrian commander back in the field. → display-only
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 10431 · net +688 · threat 93 · provinces 28 (+0) · ceiling 14784 · army 119499 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 95
  - NET income 2590 · trade 587 · admin 50 · tribute 739 · upkeep 1488 · charges 1332 · blockade 368 · admiralty 90
- DISPATCH: Sire — Lannes's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Austria, for Austria and Russia, has offered terms to settle the War with the Third Coalition — Britain + Austria + Russia. Offering 2680 gold. Its a…
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)
  - LOG sponsorship_granted: France licences Austria's design against Ottoman Empire
  - LOG design_bought_off: The peace points Austria elsewhere: France licenses The Eastern Question (Albania) — her other designs sleep
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 93 to 46; Britain remains at war with us.

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Archduke Charles stands at Vienna, three marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Davout, pursuit_ask, Archduke Charles stands at Vienna, three marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Tyr…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena moves from Tyrol to Milan (680 lost to march)
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, drill×1, wait×1, recruit×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 11143 · net +571 · threat 45 · provinces 28 (+0) · ceiling 14679 · army 117389 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 94
  - NET income 2590 · trade 587 · admin 50 · tribute 739 · upkeep 1464 · charges 1473 · blockade 368 · admiralty 90
- DISPATCH: Sire — 4 turns of famine at Tyrol now. 11,353 men gone, and not one of them to the enemy. Kingdom of Italy's magazines feed us as our own — the army is simply too large for the province. Milan can fe…
  - RAIL settlement_summary: Sire, the settlement of the War with the Third Coalition — the table with Austria + Russia is not a curtain call; it is an accounting. Bavaria must b…
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 8
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- DIPLO +7 medium/low (status_quo_titled, diplomatic_coalition_dissolved, law_enacted_abroad, diplomatic_dp_regen, diplomatic_ai_ai_treaty, agenda_shift ×2)
  - LOG diplomatic_ai_ai_treaty: Russia and Naples sign a Non-Aggression Pact
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty — Murat stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Spain, Bavaria and 1 other court stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 11779 · net +502 · threat 45 · provinces 28 (+0) · ceiling 14828 · army 116037 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 93
  - NET income 2590 · trade 587 · admin 50 · tribute 796 · upkeep 1456 · charges 1607 · blockade 368 · admiralty 90
- DISPATCH: Sire — Napoleon has been 5 turns over what Tyrol can feed. 12,705 men dead. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army is simply too large fo…
  - RAIL allegiance_settled: The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 4
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 10 — Early February 1806
  - MAILBOX #12 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #20 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Tyrol to Franconia (107 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified.…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Franconia, Munich, Swabia.
  - saved `CMD-A_t10` → Game saved: CMD-A_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 5 actions, 0 attacks — Russia, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, naval_expedition×1, garrison×1, wait×1
- LEDGER treasury 12169 · net +293 · threat 45 · provinces 28 (+0) · ceiling 13915 · army 115389 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2590 · trade 587 · admin 50 · tribute 796 · upkeep 1568 · charges 1704 · blockade 368 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 6,000 men ashore at Andalusia.
  - TURN EVENTS 7
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as joining the stronger side for pay.
- DIPLO +2 medium/low (province_changed_hands, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #21 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #22 → 1
  -     ↳ refused: Our peace with Austria is fresh: no war may be declared on her for 2 more turns.
- CMD `Lannes, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #23 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #24 → 1
  -     ↳ refused: Our peace with Austria is fresh: no war may be declared on her for 2 more turns.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Tyrol to Franconia (138 lost to march)
- CMD `Massena, fortify` → ✗ Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 7 actions, 4 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Cuesta · Shrapnel bombards Blake · Cuesta attacks Andalusia · Blake attacks Shrapnel
  - ⚔ Cuesta (lost 764) vs Shrapnel (lost 735) — Neither Shrapnel nor Cuesta could claim the field. The armies remain locked. — The Line Holds +15% (Shrapnel)
  - ⚔ Blake (lost 408) vs Shrapnel (lost 523) — Stalemate. Shrapnel and Blake glare at each other across the field. — The Line Holds +15% (Shrapnel)
  - verbs: attack×4, unfortify×1, recruit×1, wait×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Davout and Murat: Murat turns openly discontent (trust -3; expect defiance).
- LEDGER treasury 12306 · net +81 · threat 45 · provinces 28 (+0) · ceiling 12778 · army 115251 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2590 · trade 587 · admin 50 · tribute 796 · upkeep 1724 · charges 1760 · blockade 368 · admiralty 90
- DISPATCH: Sire — the allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegiance.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 2
- COURTS: The court of Austria hardens over The Eastern Question — prepared now to go as far as joining the stronger side for pay.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as alliance.
- DIPLO +3 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the nex…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 6 actions, 5 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Cuesta · Shrapnel bombards Blake · Blake attacks Shrapnel · Cuesta attacks Andalusia
  - ⚔ Blake (lost 660) vs Shrapnel (lost 742) — An inconclusive affair. Both sides bloodied but unbroken. — The Line Holds +15% (Shrapnel)
  - ⚔ Cuesta (lost 403) vs Shrapnel (lost 641) — The margin was slim. Training and preparation would serve Shrapnel well. — The Line Holds +15% (Shrapnel)
  - ⚔ Cuesta (lost 278) vs Shrapnel (lost 643) — Hardly an engagement, Sire — a brush between Shrapnel and Cuesta, and the day moved on. — The Line Holds +15% (Shrapnel)
  - verbs: attack×5, wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 12387 · net +34 · threat 45 · provinces 28 (+0) · ceiling 12580 · army 115251 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 587 · admin 50 · tribute 796 · upkeep 1724 · charges 1807 · blockade 368 · admiralty 90
- DISPATCH: Sire — Austria and Russia would now join a league against us (relations −59 and −75). The Balance of Europe names the price to keep each out.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle the War with Britain.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,284g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 6
- COURTS: The court of Austria hardens over The Eastern Question — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses

## Turn 13 — Late March 1806
  - MAILBOX #13 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #25 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #26 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with Britain — the table with Britain (3 pairs resolved). Status quo: Andalusia stays British by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #27 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #28 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #29 → reconsider
- CMD `Davout, move to Franconia` → ✓ Davout moves from Swabia to Franconia (151 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: 5 actions, 0 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×2, wait×2, move×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14484 · net +1887 · threat 45 · provinces 28 (+0) · ceiling 33350 · army 113889 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 587 · admin 50 · tribute 796 · upkeep 888 · charges 1248
- DISPATCH: Sire — peace with Britain is signed. A white peace — the map stands as it was.
  - RAIL settlement_summary: Sire, the white peace of the War with Britain — the table with Britain takes nothing and gives nothing. Spain is left out: -18 relation and a grievan…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 5
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, diplomatic_auto_downgrade, coercive_demand, blockade_broken ×3)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Britain (Alliance → Defensive Alliance)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 14 — Early April 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #30 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Aggres…
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Milan to Tyrol (1,254 lost to march)
- CMD `end turn` → ✓ Turn 14 ended. Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 2 · KingdomOfItaly client petition · The Secretariat moment letter
- LEDGER treasury 16094 · net +1674 · threat 45 · provinces 28 (+0) · ceiling 32830 · army 110559 · vassals Holland 99 · Kingdom of Italy 99 · Switzerland 88
  - NET income 2590 · trade 587 · admin 50 · tribute 712 · upkeep 856 · charges 1409
- DISPATCH: Sire — Prussia would now join a league against us — relations −25. The price to keep her out: Talleyrand brings her to −10 in 2 turns (2 DP); buying off her design costs 1,356 gold (+5 relations; she…
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL allegiance_settled: The bidding for Saxony is closed in our favour, but our relations are too cool for any pact the table can sign.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover — Prussia's relations with every court, France's included, fall 15.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_auto_downgrade, diplomatic_relation_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Alliance → Defensive Alliance)
  - LOG moment: The Arch-Chancellor's Letters — an affair of state is laid before the Emperor

## Turn 15 — Late April 1806
  - MAILBOX #15 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - MAILBOX #16 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #31 → grant the petition
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #32 → reject_ai_proposal
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #31 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (3896g forgone). Loyalty +1 (99 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: moment_letter #32 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 17289 · net +1076 · threat 45 · provinces 28 (+0) · ceiling 28040 · army 108574 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 587 · admin 50 · tribute 225 · upkeep 848 · charges 1528
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. The ordinance allows 21,426 more; 10,000 foot cost 150 gold at Paris under Bernadotte — 'recruit infantry i…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +3 medium/low (province_changed_hands, enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG moment: The Arch-Chancellor's Letters — the Emperor answers: Let the Council act
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 16 — Early May 1806
  - MAILBOX #17 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #33 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Tyrol. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 18164 · net +787 · threat 45 · provinces 28 (+0) · ceiling 26030 · army 106658 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 587 · admin 50 · upkeep 824 · charges 1616
- DISPATCH: Sire — Europe has watched us 10 quiet turns. At this pace the courts consult on turn 29 and declare on turn 32: Russia, Austria, Prussia and 5 lesser courts would march. Bound for now by a fresh peac…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Aggres…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 18929 · net +689 · threat 45 · provinces 28 (+0) · ceiling 25810 · army 104809 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · upkeep 808 · charges 1692
- DISPATCH: Sire — Britain would now join a league against us — relations −85. The price to keep her out: Talleyrand brings her to −10 in 9 turns (9 DP); buying off her design costs 1,200 gold and shortens the r…
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,880 gold. Prussia is now free to look elsewhere.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 3 more provinces. A new design hardens in their court.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
- COURTS: The court of Hesse eases over The Westphalian Duchy — gold is now the length of its tether.
- DIPLO +10 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, province_changed_hands ×3, diplomatic_dp_regen, diplomatic_auto_downgrade, agenda_shift ×2)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG ai_ai_proposal_refused: Russia and Bavaria rebuff Saxony (defensive alliance)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 19634 · net +634 · threat 45 · provinces 28 (+0) · ceiling 25970 · army 103024 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · upkeep 792 · charges 1763
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Britain, Russia, Austria, Prussia and 5 lesser courts would march.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Russia and Austria rebuff Hanover (open borders agreement)
  - LOG moment: The Throne of Holland — a letter of the record is laid before the Emperor
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 3 more — Prussia is not forgiven

## Turn 19 — Late June 1806
  - MAILBOX #18 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #34 → reject_ai_proposal
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Tyrol to Franconia (66 lost to march)
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 20284 · net +585 · threat 45 · provinces 28 (+0) · ceiling 26130 · army 101368 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · upkeep 776 · charges 1828
- DISPATCH: Sire — the ordinance allows 28,632 more men to the establishment, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris under Bernadotte — 'recruit infantry in Paris'.
  - TURN EVENTS 2
- COURTS: The court of Austria eases over The Eastern Question — joining the stronger side for pay is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Defensive Alliance → Non-Aggression)
  - LOG moment: The Throne of Holland — the Emperor answers: Keep the Republic

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✓ Massena begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 22.
  - saved `CMD-A_t20` → Game saved: CMD-A_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 2 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 20869 · net +527 · threat 45 · provinces 28 (+0) · ceiling 26130 · army 99864 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · upkeep 776 · charges 1886
- DISPATCH: Sire — the allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegiance.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Ottoman rebuffs Austria (design ask)
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (…
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Davout commands ours at Franconia, ground that takes no levy — mar…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 21412 · net +825 · threat 45 · provinces 28 (+0) · ceiling 29660 · army 98417 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 337 · upkeep 760 · charges 1941
- DISPATCH: Sire — Europe has watched us 15 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Russia, Austria, Prussia and 5 lesser courts would march. The cheapest court t…
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Massena is not currently fortified.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 22253 · net +1244 · threat 45 · provinces 28 (+0) · ceiling 34690 · army 97031 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 824 · upkeep 744 · charges 2025
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Russia, Austria, Prussia and 5 lesser courts would march.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG instrument_lapsed: The bargain between France and Austria is served in full — the design wakes

## Turn 23 — Late August 1806
  - MAILBOX #19 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #35 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 23160 · net +1041 · threat 45 · provinces 28 (+0) · ceiling 33570 · army 95701 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 744 · charges 2116
- DISPATCH: Sire — Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
  - TURN EVENTS 3
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as joining the stronger side for pay.
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Austria are rebuffed (design ask)
  - LOG sponsorship_expired: The compact between France and Austria lapses
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 2 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 24225 · net +959 · threat 45 · provinces 28 (+0) · ceiling 33810 · army 94423 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 720 · charges 2222
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Russia, Austria, Prussia and 5 lesser courts would march.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 25192 · net +870 · threat 45 · provinces 28 (+0) · ceiling 33890 · army 93197 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 712 · charges 2319
- DISPATCH: Sire — Europe has watched us 19 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Russia, Austria, Prussia and 4 lesser courts would march. The cheapest court t…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 26 — Early October 1806
  - MAILBOX #20 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #36 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 26070 · net +790 · threat 49 · provinces 28 (+0) · ceiling 33970 · army 92019 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 704 · charges 2407
- DISPATCH: Sire — the ordinance allows 37,981 more men to the establishment, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris under Bernadotte — 'recruit infantry in Paris'.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 26868 · net +719 · threat 53 · provinces 28 (+0) · ceiling 34050 · army 90889 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 696 · charges 2486
- DISPATCH: Sire — Europe has watched us 21 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Russia, Austria, Prussia and 4 lesser courts would march. The cheapest court t…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 27595 · net +654 · threat 57 · provinces 28 (+0) · ceiling 34130 · army 89804 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 688 · charges 2559
- DISPATCH: Sire — Europe has watched us 22 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Russia, Austria, Prussia and 3 lesser courts would march. The cheapest court t…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 28257 · net +596 · threat 60 · provinces 28 (+0) · ceiling 34210 · army 88763 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 680 · charges 2625
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sweden → Bid for Their Allegi…
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover and Sardinia alarmed (threat: 60)
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG moment: The Arch-Chancellor's Letters — an affair of state is laid before the Emperor

## Turn 30 — Early December 1806
  - MAILBOX #21 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #37 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
  - saved `CMD-A_t30` → Game saved: CMD-A_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 28861 · net +880 · threat 58 · provinces 28 (+0) · ceiling 37660 · army 87763 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 1049 · upkeep 672 · charges 2686
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +9% this morning; the courts have begun to notice that he can be beaten.
  - RAIL crisis_brewing: THE BREWING CRISIS: Austria will move on Bavaria. You may compensate (1,308g — you can afford it); guarantee Bavaria (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 4
- DIPLO +2 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Hesse (design ask)
  - LOG moment: The Arch-Chancellor's Letters — the Emperor answers: Let the Council act
  - LOG ai_ai_proposal_refused: Prussia rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Hesse (design ask)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Aggres…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 29749 · net +800 · threat 56 · provinces 28 (+0) · ceiling 37740 · army 86802 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 1049 · upkeep 664 · charges 2774
- DISPATCH: Sire — St Petersburg now pays Sweden 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 3 turns (3 DP); buying off her design …
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, coercive_demand)
  - LOG sponsorship_granted: Russia sponsors Sweden against France (400g/turn)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 28956 · net -784 · threat 54 · provinces 28 (+0) · ceiling 22584 · army 85881 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 1049 · upkeep 1268 · charges 3320 · blockade 344 · admiralty 90
- DISPATCH: Sire — Britain, Russia, Austria, Sweden, Hanover and Sardinia are at war with France. Britain tears up the Peace Treaty to do it. Russia tears up the Peace Treaty to do it. Austria tears up the Peace…
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Sweden, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL +8 more
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: And Britain, Sweden and Sardinia stir at their own designs.
- DIPLO +15 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, diplomatic_treaty_broken, blockade_begins ×4, diplomatic_relation_shift ×6)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Russia has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Bavaria was forced to break the Peace Treaty with Austria (cascade).
  - LOG coalition_declared: The Fourth British Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia and Sweden

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Kutuzov is at Bohemia, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Davout commands ours at Franconia, ground that takes no levy — mar…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- enemy phase: 14 actions, 6 attacks — Austria, Prussia, the Ottoman Empire and 7 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Cuesta · Shrapnel bombards Blake · Blake attacks Shrapnel · Deroy attacks Bennigsen
  - ⚔ Blake (lost 1104, own corps) vs Shrapnel (lost 2067) — A narrow defeat for Shrapnel, Sire. Better-prepared troops might have tipped the balance. — The Line Holds +15% (Shrapnel)
  - ⚔ Deroy (lost 1521) vs Bennigsen (lost 433, own corps) — Bennigsen's square formation provided a solid defensive anchor, Sire.
  - ⚔ Deroy (lost 1151) vs Bennigsen (lost 432, own corps) — The square held its ground. Bennigsen's infantry stood like a fortress on the field.
  - ⚔ Deroy (lost 1107) vs Bennigsen (lost 310, own corps) — Bennigsen's men formed square and weathered the storm. Discipline held the line.
  - verbs: attack×6, move×3, form_square×2, recruit×2, unfortify×1
- LEDGER treasury 28192 · net -754 · threat 52 · provinces 28 (+0) · ceiling 22221 · army 84996 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 1049 · upkeep 1248 · charges 3310 · blockade 344 · admiralty 90
- DISPATCH: Sire — the ordinance allows 45,004 more men to the establishment, and the depots hold 100,000. 10,000 foot cost 450 gold at Paris under Bernadotte — 'recruit infantry in Paris'.
  - TURN EVENTS 4
- DIPLO +7 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).
  - LOG moment: Britain decrees the Remounts for 8 turns (1,500 gold)
  - LOG moment: Russia decrees the Magazines for 8 turns (2,500 gold)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Hanover (open borders agreement)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Kutuzov is at Bohemia, just one region away.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 10 actions, 5 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Tyrol · Cuesta attacks Andalusia · Blake attacks Shrapnel · Castanos attacks Shrapnel
  - 🏴 Spain: Cuesta attacks Andalusia — Region captured: Andalusia (was Britain) (secured)
  - ⚔ Archduke Charles (lost 5260) vs Massena (lost 2084, own corps) — Ney, Murat and Teulie's timely arrival aided Massena. Davout, however, was conspicuously absent. — The Hofkriegsrat's orders reached Archduke John too late. — Berthier: the corps marched apart and arrived together.
  - ⚔ Blake (lost 311, own corps) vs Shrapnel (lost 5294) — The toll on Shrapnel's forces is heavy, Sire. This defeat will be felt. — The Line Holds +15% (Shrapnel)
  - ⚔ Castanos (lost 276) vs Shrapnel (lost 2685) — Even the favorable ground could not save Shrapnel, Sire. Castanos overcame the terrain. — The Line Holds +15% (Shrapnel)
  - ⚔ Alten (lost 912) vs Dumonceau (lost 452) — A costly day for Alten: the losses ran two to one in Dumonceau's favour, and Alten is still in the field.
  - verbs: attack×5, move×3, unfortify×1, recruit×1
- LEDGER treasury 26160 · net -1610 · threat 50 · provinces 28 (+0) · ceiling 16269 · army 81097 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 1010 · upkeep 1212 · charges 3933 · contributions 230 · blockade 344 · admiralty 90
- DISPATCH: Sire — the Emperor's star burns full again. The Presence stands at +10%, and Europe remembers what it feared.
  - TURN EVENTS 2
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 7 actions, 2 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Tyrol · Archduke John attacks Wrede
  - ⚔ Archduke Charles (lost 4208, own corps) vs Massena (lost 1597, own corps) — Reinforcements! Ney, Lannes, Murat and Teulie marched onto the field beside Massena. The enemy's advantage melted away. — Berthier: the corps marched apart and arrived together.
  - ⚔ Archduke John (lost 294, own corps) vs Wrede (lost 4276) — The toll on Wrede's forces is heavy, Sire. This defeat will be felt. And Wrede was taken on that field — Austria holds …
  - verbs: attack×2, form_square×2, move×1, fortify×1, grant_pension×1
- LEDGER treasury 24524 · net -1312 · threat 48 · provinces 28 (+0) · ceiling 16695 · army 76510 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 996 · upkeep 1028 · charges 3775 · contributions 260 · blockade 344 · admiralty 90
- DISPATCH: Sire — Shrapnel has crossed into Gascony. No French corps stands in his path.
  - EXPECTS: Massena's victories raise his expectation — he now looks for 40g/turn (holds 0g).
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Bohemia instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Bohemia instead.) → trust
  - ↳ MUSTER — Ney (3,802; expect about 43,259 with the corps likely to arrive, up to 47,420 if all march; certain 3,802; a bad day (1 in 10) 34,914) vs Archduke Charles (42,895 men) at Bohemia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 852, own corps) vs Archduke Charles (lost 3167, own corps) — Lannes, Massena, Napoleon and Teulie arrived in time to steady Ney's position. The field was held, nothing further. — The corps system brought Teulie in.
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Bohemia instead.)
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Bohemia instead.) → trust
  - ↳ MUSTER — Massena (15,484; expect about 17,948 with the corps likely to arrive, up to 26,756 if all march; certain 15,484, and a bad day (1 in 10) is no better) vs Archduke Charles (39,728 men) at Bohemia — the balance of force looks unfavor
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 4824, own corps) vs Archduke Charles (lost 1714, own corps) — Murat arrived to reinforce Massena, but Ney failed to reach the field in time. — The corps system brought Murat in.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: 7 actions, 5 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Davout · Archduke John attacks Lannes · Hiller attacks Lannes · Archduke Charles attacks Tyrol
  - ⚔ Archduke Charles (lost 801) vs Davout (lost 2017, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Archduke John (lost 1004, own corps) vs Lannes (lost 550, own corps) — Neither Lannes nor Archduke John could claim the field. The armies remain locked.
  - ⚔ Hiller (lost 2015) vs Lannes (lost 216, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 1258, own corps) vs Lannes (lost 442, own corps) — Even the favorable ground could not save Lannes, Sire. Archduke Charles overcame the terrain.
  - ⚔ Archduke John (lost 492, own corps) vs Teulie (lost 2033, own corps) — The hills were ours, but Archduke John took them. Teulie's position was overrun.
  - verbs: attack×5, move×1, wait×1
- ORDER Teulie [awaiting_response]: Teulie is cornered at Tyrol with 2,478 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last…
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Tyrol with 2,478 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 21763 · net -1256 · threat 46 · provinces 28 (+0) · ceiling 15274 · army 50494 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 100
  - NET income 2581 · trade 549 · admin 50 · tribute 928 · upkeep 804 · charges 3826 · contributions 300 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_we_threshold ×3, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Hesse (design ask)
  - LOG moment: The Squadron for Santo Domingo — an affair of state is laid before the Emperor
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 37 — Late March 1807
  - MAILBOX #22 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #38 → reject_ai_proposal
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Lannes is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `Murat, unfortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 9 actions, 3 attacks — Britain, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Tyrol · Deroy attacks Bennigsen · Deroy attacks Hiller
  - 🏴 Austria: Archduke Charles attacks Tyrol — Region captured: Tyrol (was Kingdom of Italy) (secured)
  - ⚔ Deroy (lost 434) vs Bennigsen (lost 705) — Bennigsen was close. A period of drilling could have changed the outcome.
  - ⚔ Deroy (lost 3683) vs Hiller (lost 2063) — A wise investment in fortification. Hiller's position was impregnable to Deroy's assault.
  - verbs: attack×3, fortify×3, move×1, wait×1, recruit×1
- LEDGER treasury 20653 · net -954 · threat 44 · provinces 28 (+0) · ceiling 15800 · army 50494 · vassals Holland 100 · Kingdom of Italy 95 · Switzerland 100
  - NET income 2572 · trade 549 · admin 50 · tribute 933 · upkeep 804 · charges 3670 · contributions 150 · blockade 344 · admiralty 90
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - UNMET: Massena expects 40g/turn, holds 0g — patience holds 2 more turns
  - TURN EVENTS 7
- DIPLO +6 medium/low (province_changed_hands, diplomatic_dp_regen, diplomatic_vassal_contingent, diplomatic_auto_downgrade ×2, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Britain (Defensive Alliance → Non-Aggression)
  - LOG moment: The Squadron for Santo Domingo — the Emperor answers: Ferrand must hold alone

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Massena is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Lannes, fortify` → ✗ Lannes is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight. — Alten attacks Dumonceau
  - ⚔ Alten (lost 746) vs Dumonceau (lost 446) — The engagement proceeded as one might expect, Sire.
  - verbs: wait×1, attack×1
- LEDGER treasury 19647 · net -847 · threat 42 · provinces 28 (+0) · ceiling 15410 · army 50494 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2574 · trade 499 · admin 50 · tribute 915 · upkeep 804 · charges 3529 · contributions 150 · blockade 312 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - UNMET: Massena expects 40g/turn, holds 0g — patience holds 1 more turn
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Bavaria–France (Alliance → Defensive Alliance)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Milan, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Alten attacks Dumonceau
  - ⚔ Alten (lost 774) vs Dumonceau (lost 288) — Alten bled two men for each of Dumonceau's. A clear exchange, not yet a decision.
  - verbs: move×1, wait×1, attack×1
- LEDGER treasury 18765 · net -748 · threat 40 · provinces 28 (+0) · ceiling 15089 · army 50494 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2576 · trade 499 · admin 50 · tribute 896 · upkeep 804 · charges 3413 · contributions 150 · blockade 312 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 6 turns. Every turn of it is worth a province to their recruiting sergeants.
  - UNMET: Massena expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-A_t40` → Game saved: CMD-A_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Lannes · Deroy attacks Bohemia · Deroy attacks Bennigsen
  - 🏴 Bavaria: Deroy attacks Bohemia — The garrison of Bohemia is destroyed. · Region captured: Bohemia (was Austria) (secured)
  - ⚔ Archduke John (lost 402) vs Lannes (lost 379, own corps) — The toll on Lannes's forces is heavy, Sire. This defeat will be felt. — The Hofkriegsrat's orders reached Archduke Charles too late.
  - ⚔ Deroy (lost 266) vs Bennigsen (lost 506) — A skirmish, Sire. Bennigsen's men traded shots with Deroy; there was no battle to speak of. — the Russian army would not break: Stubborn softened the rout (−2 morale, not −3)
  - verbs: attack×3, move×2
- ORDER Lannes [awaiting_response]: Lannes is cornered at Milan with 581 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: …
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Milan — 989 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Milan with 581 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Milan — 989 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 17898 · net -1435 · threat 38 · provinces 28 (+0) · ceiling 12351 · army 46340 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2579 · trade 499 · admin 50 · tribute 883 · upkeep 780 · charges 4114 · contributions 150 · blockade 312 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - UNMET: Massena expects 40g/turn, holds 0g — loyalty eroding
  - RAIL settlement_offer_arrival: Austria, for Austria, Sweden, Hanover and Sardinia, has offered terms to settle the War with The Fourth British Coalition — Britain + Russia + Austri…
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_we_threshold, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)

---
finished: **completed** · commands 200 · popups 73 · battles 39
