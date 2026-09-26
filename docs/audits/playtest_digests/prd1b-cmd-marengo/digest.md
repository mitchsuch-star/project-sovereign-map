# Playtest digest — prd1b-cmd-marengo

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `759414f922cb` (dirty) · content `f797f1101c51` · driver `196c4ee545c1`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2629, own corps) vs Mack (lost 9416) — Reinforcements from Davout and Napoleon bolstered Ney's position — though Soult, Lannes, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Mack.
- CMD `Lannes, move to Rhineland` → ✓ Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?'
  - POPUP strategic_interrupt: Lannes, contact_bad_odds, Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' → attack_anyway
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1858, own corps) vs Mack (lost 9277) — Ney and Bernadotte's timely arrival aided Lannes. Soult and Murat, however, were conspicuously absent.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles'…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Franconia. (1,573 lost to march) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1538, own corps) vs Deroy (lost 9954) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - verbs: stance_change×2, move×1, attack×1, wait×1
- ORDER Lannes [active]: Lannes is marching to Rhineland (3 turns remaining).
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
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (18,578; expect about 80,289 with the corps likely to arrive, up to 92,807 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 607, own corps) vs Mack (lost 16736) — Lannes and Massena arrived to reinforce Ney, but Murat and Bernadotte failed to reach the field in time.
- CMD `Davout, attack Mack` → ✓ Davout pursues Mack (at Munich). Moves to Swabia. Davout: "Pursuit, then. I do not intend to be led into anything."
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Davout. Casualties: ArchdukeChar… · ArchdukeJohn holds them at Swabia while allies attack from Franconia! (+1 coordination) · ArchdukeCharles holds them at Swabia while allies attack from Franconia! (+1 coordination) · ArchdukeJohn holds them at Swabia while allies attack from Franconia! (+1 coordination)
  - ⚔ Archduke Charles (lost 2212, own corps) vs Davout (lost 3849, own corps) — Reinforcements from Napoleon bolstered Davout's position — though Ney, Soult and Murat never arrived, Sire.
  - ⚔ Archduke John (lost 197, own corps) vs Deroy (lost 5519) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1031, own corps) vs Bernadotte (lost 7183) — Bernadotte stood alone, Sire. Ney and Soult never came.
  - ⚔ Archduke John (lost 723, own corps) vs Davout (lost 3757) — Not one corps reached Davout. Ney, Soult and Murat were expected; Davout fought the battle single-handed.
  - verbs: attack×4
- ORDER Davout [active]: Davout is pursuing Mack (0 turns remaining).
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4660 · net +2890 · threat 73 · provinces 28 (+0) · ceiling 53140 · army 151977 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 94
  - NET income 3400 · trade 450 · admin 50 · tribute 937 · upkeep 1474 · charges 158 · blockade 225 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×3, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 14 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,095; expect about 83,124 with the corps likely to arrive, up to 83,972 if all march) vs Mack (14,707 men) at Franconia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 82, own corps) vs Mack (lost 13728) — Lannes and Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Mack was taken on that field …
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 685 gold (×3 at war) (×1.14 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 actions unused) Turn 4 begins!
- SPENT 685g on this turn's orders
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. Brutal stalemate between ArchdukeCharles and Davout. Heavy casualties on bot… · ArchdukeJohn's forces advance steadily. ArchdukeJohn gains the advantage over Davout. Casualties: ArchdukeJohn's army 1…
  - ⚔ Archduke Charles (lost 2749, own corps) vs Davout (lost 1061, own corps) — Ney, Murat and Napoleon arrived to reinforce Davout, but Soult failed to reach the field in time.
  - ⚔ Archduke John (lost 445, own corps) vs Davout (lost 4514) — Davout stood alone, Sire. Soult never came.
  - verbs: attack×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 6745 · net +2861 · threat 81 · provinces 29 (+1) · ceiling 35578 · army 142915 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 91
  - NET income 3438 · trade 525 · admin 50 · tribute 937 · upkeep 1196 · charges 470 · occupation 70 · blockade 263 · admiralty 90
- DISPATCH: Sire — Marshal Mack of Austria is taken at Franconia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✗ Davout cannot fortify while engaged with enemy forces! Enemy present: ArchdukeCharles, ArchdukeJohn. Attack or retreat first.
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Franconia to Tyrol. Tyrol falls to France! (was Austria) (2,301 lost to march)
  - POPUP capture_choice[capture]: Tyrol, Massena → secure
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 3 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: retreat×2, stance_change×2
  - POPUP marshal_petition: shadow_command, Marshal Soult asks for a command → detach
  -     ↳ Soult straightens. "You will not regret it, Sire." March him to Franconia and the front is his — the order is…
- LEDGER treasury 9786 · net +2635 · threat 81 · provinces 30 (+1) · ceiling 35515 · army 139593 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 89
  - NET income 3476 · trade 587 · admin 50 · tribute 937 · upkeep 1112 · charges 797 · occupation 122 · blockade 294 · admiralty 90
- DISPATCH: Sire — Tyrol has fallen to our arms. The tricolor flies over it this morning.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (15,287; expect about 79,853 with the corps likely to arrive, up to 89,571 if all march) vs Archduke Charles (34,307 men) at Munich — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 735, own corps) vs Archduke Charles (lost 6047) — Reinforcement from Davout, Lannes, Murat and Massena kept Ney standing, Sire — but neither side yielded the ground.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (933 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (194 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 12248 · net +2400 · threat 79 · provinces 30 (+0) · ceiling 34462 · army 133055 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 87
  - NET income 3556 · trade 587 · admin 50 · tribute 937 · upkeep 1048 · charges 1106 · contributions 100 · occupation 92 · blockade 294 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Munich. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #8 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #10 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 42g a turn — 37g of income forfeited, 52g of occupation relieved, 27g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 8.
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action unused) Turn 7 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Franche-Comte into Franche-Comte unopposed! (660 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,645 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,543 troops in the…
  - 🏴 Austria: ArchdukeCharles marches from Franche-Comte into Franche-Comte unopposed! (660 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -77g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - verbs: attack×3, move×1, fortify×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 14750 · net +2299 · threat 77 · provinces 28 (-2) · ceiling 43059 · army 132269 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 85
  - NET income 3422 · trade 587 · admin 50 · tribute 739 · upkeep 1040 · charges 1035 · occupation 40 · blockade 294 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. ArchdukeJohn's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- COURTS: The court of Prussia eases over The Hanoverian Prize — gold is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 7 — Late December 1805
  - MAILBOX #9 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (85 → 95); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke Charles` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 7.
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (82 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Davout → secure
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (19,245; expect about 50,708 with the corps likely to arrive, up to 50,988 if all march) vs Archduke Charles (20,836 men) at Milan — the balance of force …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 1116, own corps) vs Archduke Charles (lost 4341) — Massena arrived in time to steady Murat's position. The field was held, nothing further.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Provence unopposed! (161 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (161 lost to march) Captured: France → Austria
  - verbs: move×1, form_square×1, attack×1
- LEDGER treasury 15962 · net +1207 · threat 77 · provinces 28 (+0) · ceiling 26329 · army 129060 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3276 · trade 587 · admin 50 · tribute 421 · upkeep 1008 · charges 1625 · occupation 110 · blockade 294 · admiralty 90
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout respectfully raises concerns: 'I have concerns about this order, Sire.'
  - POPUP objection: Davout, Davout respectfully raises concerns: 'I have concerns about this order, Sire.' → trust
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! ArchdukeJohn is at Munich, just one region away.
- CMD `Massena, move to Milan` → ✓ Massena moves from Tyrol to Milan. Milan falls to France! (was Austria) (962 lost to march)
  - POPUP capture_choice[capture]: Milan, Massena → secure
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Lyonnais unopposed! (156 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Lyonnais unopposed! (156 lost to march) Captured: France → Austria
  - verbs: attack×1
- LEDGER treasury 16983 · net +899 · threat 67 · provinces 28 (+0) · ceiling 24491 · army 128098 · vassals Holland 96 · Switzerland 93
  - NET income 3289 · trade 599 · admin 50 · tribute 337 · upkeep 1000 · charges 1791 · occupation 195 · blockade 300 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Franconia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos launches a devastating assault! Castanos gains the advantage over Paget. Casualties: Castanos 672, Paget 1,840… · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - ⚔ Castanos (lost 672) vs Paget (lost 1840) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - ⚔ Castanos (lost 338) vs Paget (lost 1633) — Paget's aggressive posture left the troops exposed when Castanos's attack came. And Paget was taken on that field — Spa…
  - verbs: attack×2, move×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 17969 · net +865 · threat 65 · provinces 28 (+0) · ceiling 25004 · army 128098 · vassals Holland 96 · Switzerland 92
  - NET income 3394 · trade 599 · admin 50 · tribute 337 · upkeep 1000 · charges 1960 · occupation 165 · blockade 300 · admiralty 90
- DISPATCH: Lannes's fortifications decay: 8% → 6%
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Ney is already in Franconia.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, m…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich, Swabia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 1661, own corps) vs Archduke John (lost 1955) — Ney reached the field beside Massena, Sire — it saved the line, no more.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 19343 · net +1349 · threat 63 · provinces 28 (+0) · ceiling 33213 · army 125692 · vassals Holland 96 · Switzerland 91
  - NET income 3542 · trade 599 · admin 50 · tribute 337 · upkeep 984 · charges 1685 · occupation 120 · blockade 300 · admiralty 90
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Piedmont.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 6
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #14 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #15 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Bohemia, Franconia and Milan stay ours by the treaty — titled. Status quo: Franche-Comte, Lyonnais and Provence stay Austrian by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #16 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #17 → reconsider
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Franconia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. Turn 12 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, unfortify×1, fortify×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 22621 · net +3239 · threat 31 · provinces 28 (+0) · ceiling 292500 · army 124808 · vassals Holland 94 · Switzerland 90
  - NET income 3552 · trade 635 · admin 50 · tribute 337 · upkeep 968 · charges 247 · occupation 120
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria vs Britain + Austria + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +6 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 63 to 31.

## Turn 12 — Early March 1806
  - MAILBOX #11 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #18 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +6 (94 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 80% -> 72%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 25354 · net +2923 · threat 31 · provinces 28 (+0) · ceiling 268916 · army 126881 · vassals Holland 99 · Switzerland 89
  - NET income 3610 · trade 635 · admin 50 · upkeep 992 · charges 280 · occupation 100
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #19 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #20 → reconsider
- CMD `Davout, move to Franconia` → ✓ Davout moves from Bohemia to Franconia
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, fortify×1
- LEDGER treasury 28413 · net +3023 · threat 31 · provinces 28 (+0) · ceiling 280250 · army 125273 · vassals Holland 98 · Switzerland 88
  - NET income 3692 · trade 635 · admin 50 · upkeep 968 · charges 316 · occupation 70
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 85).
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Franconia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Tyrol instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Tyrol instead.) → trust
  - POPUP diplomatic_dialogue: war_purpose_selection #21 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #22 → reconsider
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×2, recruit×1
- LEDGER treasury 31448 · net +3223 · threat 31 · provinces 28 (+0) · ceiling 300000 · army 123714 · vassals Holland 97 · Switzerland 87
  - NET income 3696 · trade 635 · admin 50 · tribute 225 · upkeep 960 · charges 353 · occupation 70
- DISPATCH: Soult's fortifications strengthen: +11% defense (max 12%)
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 34683 · net +3196 · threat 31 · provinces 28 (+0) · ceiling 301000 · army 122203 · vassals Holland 96 · Switzerland 86
  - NET income 3700 · trade 635 · admin 50 · tribute 225 · upkeep 952 · charges 392 · occupation 70
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #23 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (86 → 96); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 16 ended. Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2
- LEDGER treasury 37662 · net +2944 · threat 31 · provinces 28 (+0) · ceiling 282916 · army 121458 · vassals Holland 95 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · upkeep 944 · charges 427 · occupation 70
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 32).
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×2
- LEDGER treasury 40606 · net +2908 · threat 31 · provinces 28 (+0) · ceiling 282916 · army 120728 · vassals Holland 94 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · upkeep 944 · charges 463 · occupation 70
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 32% -> 34%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- SPENT 170g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 43313 · net +2868 · threat 31 · provinces 28 (+0) · ceiling 282250 · army 122952 · vassals Holland 93 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · upkeep 952 · charges 495 · occupation 70
- DISPATCH: Ney's fortifications strengthen: +8% defense (MAX)
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, recruit×1
- LEDGER treasury 46189 · net +3178 · threat 31 · provinces 28 (+0) · ceiling 311000 · army 122191 · vassals Holland 92 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 337 · upkeep 944 · charges 530 · occupation 70
- DISPATCH: Soult's fortifications decay: 12% → 11%
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_ai_ai_treaty)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 38% of active European bloc power.
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×2, recruit×2
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 49367 · net +3140 · threat 28 · provinces 28 (+0) · ceiling 311000 · army 121446 · vassals Holland 91 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 337 · upkeep 944 · charges 568 · occupation 70
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 37% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 21 — Late July 1806
  - MAILBOX #13 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #24 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Franconia (field levy — no depot; capped at 3,000) (recruitment is drafted in fix…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 51780 · net +2750 · threat 26 · provinces 28 (+0) · ceiling 280916 · army 123656 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · upkeep 968 · charges 597 · occupation 70
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 54538 · net +2725 · threat 24 · provinces 28 (+0) · ceiling 281583 · army 122881 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · upkeep 960 · charges 630 · occupation 70
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 44).
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 57279 · net +2933 · threat 22 · provinces 28 (+0) · ceiling 301666 · army 122122 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 225 · upkeep 944 · charges 663 · occupation 70
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_ai_ai_treaty)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 38% of active European bloc power.
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 60212 · net +2898 · threat 19 · provinces 28 (+0) · ceiling 301666 · army 121379 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 225 · upkeep 944 · charges 698 · occupation 70
- DISPATCH: Massena's fortifications have crumbled completely!
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 37% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 63118 · net +2871 · threat 17 · provinces 28 (+0) · ceiling 302333 · army 120649 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 225 · upkeep 936 · charges 733 · occupation 70
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 65989 · net +2837 · threat 15 · provinces 28 (+0) · ceiling 302333 · army 119934 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 225 · upkeep 936 · charges 767 · occupation 70
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +5 (now 100).
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 92% -> 81%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 68587 · net +2789 · threat 13 · provinces 28 (+0) · ceiling 301000 · army 122174 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 225 · upkeep 952 · charges 799 · occupation 70
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
  - MAILBOX #14 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #25 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 71384 · net +3101 · threat 11 · provinces 28 (+0) · ceiling 329750 · army 121429 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 562 · upkeep 944 · charges 832 · occupation 70
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 54).
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 74493 · net +3072 · threat 9 · provinces 28 (+0) · ceiling 330416 · army 120699 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 562 · upkeep 936 · charges 869 · occupation 70
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 54% -> 50%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- SPENT 170g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 77348 · net +3013 · threat 7 · provinces 28 (+0) · ceiling 328416 · army 122923 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 562 · upkeep 960 · charges 904 · occupation 70
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Mack at Vienna instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Mack at Vienna instead.) → trust
  - POPUP diplomatic_dialogue: war_purpose_selection #26 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #27 → reconsider
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 80377 · net +2993 · threat 5 · provinces 28 (+0) · ceiling 329750 · army 122164 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 562 · upkeep 944 · charges 940 · occupation 70
- DISPATCH: Soult's fortifications strengthen: +7% defense (max 12%)
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)
  - LOG balance_of_europe_shifted: Russian-led alignment leads the current largest alignment at 38% of active European bloc power.

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: garrison×1, recruit×1
- LEDGER treasury 83370 · net +2957 · threat 2 · provinces 28 (+0) · ceiling 329750 · army 121419 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 562 · upkeep 944 · charges 976 · occupation 70
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 37% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Franconia (field levy — no depot; capped at 3,000) (recruitment is drafted in fix…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 85937 · net +2902 · threat 0 · provinces 28 (+0) · ceiling 327750 · army 123629 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 635 · admin 50 · tribute 562 · upkeep 968 · charges 1007 · occupation 70
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 88817 · net +2846 · threat 0 · provinces 28 (+0) · ceiling 325916 · army 122854 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 597 · admin 50 · tribute 562 · upkeep 952 · charges 1041 · occupation 70
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 91671 · net +2819 · threat 0 · provinces 28 (+0) · ceiling 326583 · army 122095 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 597 · admin 50 · tribute 562 · upkeep 944 · charges 1076 · occupation 70
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: Russian-led alignment leads the current largest alignment at 38% of active European bloc power.
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 94490 · net +2786 · threat 0 · provinces 28 (+0) · ceiling 326583 · army 121351 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 597 · admin 50 · tribute 562 · upkeep 944 · charges 1109 · occupation 70
- DISPATCH: Ney's fortifications have crumbled completely!
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 37% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 97276 · net +2752 · threat 0 · provinces 28 (+0) · ceiling 326583 · army 120623 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 597 · admin 50 · tribute 562 · upkeep 944 · charges 1143 · occupation 70
- DISPATCH: Ney's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 100036 · net +2727 · threat 0 · provinces 28 (+0) · ceiling 327250 · army 119909 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 597 · admin 50 · tribute 562 · upkeep 936 · charges 1176 · occupation 70
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 87%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 102532 · net +2689 · threat 0 · provinces 28 (+0) · ceiling 326583 · army 122150 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 597 · admin 50 · tribute 562 · upkeep 944 · charges 1206 · occupation 70
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: Russian-led alignment leads the current largest alignment at 38% of active European bloc power.

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 105221 · net +2657 · threat 0 · provinces 28 (+0) · ceiling 326583 · army 121406 · vassals Holland 100 · Switzerland 96
  - NET income 3700 · trade 597 · admin 50 · tribute 562 · upkeep 944 · charges 1238 · occupation 70
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 37% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

---
finished: **completed** · commands 200 · popups 47 · battles 16
