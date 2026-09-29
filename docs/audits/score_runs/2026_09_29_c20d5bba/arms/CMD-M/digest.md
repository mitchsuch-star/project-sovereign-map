# Playtest digest — CMD-M

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.11.15 · Linux-6.18.44-fc-v37-x86_64-with-glibc2.39 (x86_64) · PYTHONHASHSEED `0` · engine `c20d5bba3ca1` (dirty) · content `8f597da58501` · driver `302c81c650ed`
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
- LEDGER treasury 1635 · net +1454 · threat 67 · provinces 28 · ceiling 34455 · army 174905 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2164 · blockade 219 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (18,578; expect about 80,289 with the corps likely to arrive, up to 92,807 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 630, own corps) vs Mack (lost 16138) — Lannes and Massena arrived to reinforce Ney, but Murat and Bernadotte failed to reach the field in time.
- CMD `Davout, attack Mack` → ✓ Davout pursues Mack (at Munich). Moves to Swabia. Davout: "Pursuit, then. I do not intend to be led into anything."
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Davout. Casualties: ArchdukeCharles's… · ArchdukeJohn holds them at Swabia while allies attack from Franconia! (+1 coordination) · ArchdukeCharles holds them at Swabia while allies attack from Franconia! (+1 coordination) · ArchdukeJohn holds them at Swabia while allies attack from Franconia! (+1 coordination)
  - ⚔ Archduke Charles (lost 1962, own corps) vs Davout (lost 4338, own corps) — Reinforcements from Napoleon bolstered Davout's position — though Ney, Soult and Murat never arrived, Sire.
  - ⚔ Archduke John (lost 181, own corps) vs Deroy (lost 5642) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1194, own corps) vs Bernadotte (lost 6699) — Bernadotte stood alone, Sire. Ney and Soult never came.
  - ⚔ Archduke John (lost 815, own corps) vs Davout (lost 3252) — Not one corps reached Davout. Ney, Soult and Murat were expected; Davout fought the battle single-handed.
  - verbs: attack×4
- ORDER Davout [active]: Davout is pursuing Mack (0 turns remaining).
- ORDER Lannes [active]: Lannes answered the guns this turn and stands at Munich; his march resumes next turn.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2929 · net +2102 · threat 73 · provinces 28 (+0) · ceiling 36394 · army 152193 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2590 · trade 450 · admin 50 · tribute 937 · upkeep 1496 · charges 58 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +9 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 14 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,074; expect about 83,023 with the corps likely to arrive, up to 83,871 if all march) vs Mack (15,302 men) at Franconia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 94, own corps) vs Mack (lost 14284) — Lannes and Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Mack was taken on that field …
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 686 gold (×3 at war) (×1.14 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 actions unused) Turn 4 begins!
- SPENT 686g on this turn's orders
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Davout. Casualties: Archd… · ArchdukeJohn launches a decisive assault. ArchdukeJohn gains the advantage over Davout. Casualties: ArchdukeJohn's army… · ArchdukeJohn delivers an effective strike. Brutal stalemate between ArchdukeJohn and Murat. Heavy casualties on both si…
  - 🏴 Austria: Casualties: ArchdukeJohn's army 1,409, Davout 5,058. Both armies remain in the field. Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 2100, own corps) vs Davout (lost 1857, own corps) — Ney and Napoleon arrived to reinforce Davout, but Soult and Murat failed to reach the field in time.
  - ⚔ Archduke John (lost 398, own corps) vs Davout (lost 5058) — Davout stood alone, Sire. Soult and Murat never came.
  - ⚔ Archduke John (lost 1017, own corps) vs Murat (lost 3749) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×3, form_square×1
- ORDER Lannes [active]: Lannes answered the guns this turn and stands at Franconia; his march resumes next turn.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4152 · net +2322 · threat 81 · provinces 29 (+1) · ceiling 25805 · army 137838 · vassals Holland 94 · Kingdom of Italy 94 · Switzerland 89
  - NET income 2621 · trade 525 · admin 50 · tribute 937 · upkeep 1092 · charges 230 · occupation 70 · blockade 329 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✗ Davout is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Franconia to Tyrol. Tyrol falls to France! (was Austria) (2,298 lost to march)
  - POPUP capture_choice[capture]: Tyrol, Massena → secure
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 3 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh…
  - ⚔ Archduke Charles (lost 2004) vs Murat (lost 4439, own corps) — Reinforcements from Napoleon bolstered Murat's position — though Soult never arrived, Sire.
  - verbs: move×2, attack×1, fortify×1
- ORDER Lannes [interrupted]: Lannes hears cannon fire! Abandoning orders — rushing to Franche-Comte! Lannes moves from Franconia to Swabia. Swabia falls to France! (was Austria) …
  - POPUP marshal_audience: shadow_command, Marshal Soult asks for a command → detach
  -     ↳ Soult straightens. "You will not regret it, Sire." March him to Franconia and the front is his — the order is…
- LEDGER treasury 6321 · net +2080 · threat 83 · provinces 31 (+2) · ceiling 24369 · army 126537 · vassals Holland 92 · Kingdom of Italy 92 · Switzerland 85
  - NET income 2670 · trade 587 · admin 50 · tribute 937 · upkeep 976 · charges 497 · contributions 59 · occupation 174 · blockade 368 · admiralty 90
- DISPATCH: Sire — Napoleon's corps has been broken at Franche-Comte. He must reform before he fights again.
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ Ney pursues Archduke Charles (at Franche-Comte). Moves to Swabia. Ney: "He is already beaten — he merely has not been told. I will tell him."
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (914 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (138 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franche-Comte where he stands! (912 lost to march) Captured: France → Austria · ArchdukeCharles launches a decisive assault. Massena holds the line. Casualties: ArchdukeCharles 4,368, Massena 2,520. … · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,777 troops. Ga…
  - 🏴 Austria: ArchdukeCharles takes Franche-Comte where he stands! (912 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 4368) vs Massena (lost 2520) — A standard affair. Nothing unusual to report.
  - verbs: attack×3, move×1
- ORDER Ney [active]: Ney is pursuing Archduke Charles (0 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #10 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +7 (93 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 44g a turn — 30g of income forfeited, 52g of occupation relieved, 22g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 8300 · net +1882 · threat 81 · provinces 29 (-2) · ceiling 23983 · army 120062 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2576 · trade 587 · admin 50 · tribute 941 · upkeep 936 · charges 756 · occupation 122 · blockade 368 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. Archduke Charles's corps of 30,431 stands there. A garrison you detach (3,000 men) holds a province against a march, as d…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Munich, just one region away.
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Munich instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1029, own corps) vs Archduke Charles (lost 3598, own corps) — Reinforcements from Ney and Massena bolstered Lannes's position — though Soult and Murat never arrived, Sire.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles marches from Milan into Piedmont unopposed! (298 lost to march) Captured: KingdomOfItaly → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -87g, Kingdom of Italy -175g. Captured: KingdomOfItaly → Austria
  - 🏴 Austria: ArchdukeCharles marches from Milan into Piedmont unopposed! (298 lost to march) Captured: KingdomOfItaly → Austria
  - verbs: attack×2, stance_change×1, move×1
- ORDER Ney [active]: Ney answered the guns this turn and stands at Swabia; the pursuit resumes next turn.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10046 · net +1767 · threat 79 · provinces 29 (+0) · ceiling 28527 · army 112959 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 82
  - NET income 2714 · trade 587 · admin 50 · tribute 585 · upkeep 872 · charges 769 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- COURTS: The court of Prussia eases over The Hanoverian Prize — gold is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 7 — Late December 1805
  - MAILBOX #9 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke Charles` → ✓ Ney: 'ArchdukeJohn bars the way!' Engaging!
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 646, own corps) vs Archduke John (lost 2390, own corps) — Reinforcements from Lannes and Massena bolstered Ney's position — though Soult and Murat never arrived, Sire.
- CMD `Davout, move to Bohemia` → ✓ Davout begins marching to Bohemia (distance: 3). Moved to Swabia. Route: Swabia -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ Cannot charge through Munich - ArchdukeJohn blocks the path! Engage them first.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action unused) Turn 8 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turns remaining).
- ORDER Ney [active]: Ney is pursuing Archduke Charles (1 turn remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 11492 · net +1406 · threat 80 · provinces 29 (+0) · ceiling 25486 · army 106970 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2720 · trade 587 · admin 50 · tribute 361 · upkeep 832 · charges 952 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Supply cost you 2,788 men, at Swabia and Munich.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 8 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Davout can give chase.
- CMD `Ney, fortify` → ✗ Ney cannot fortify while engaged with enemy forces! Enemy present: Archduke John. Attack or retreat first.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! Archduke John is at Munich, just one region away.
- CMD `Massena, move to Milan` → ✗ Cannot advance while engaged with enemy forces. You may retreat to friendly territory.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 8 actions, 1 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos launches a decisive assault. Castanos gains the advantage over Paget. Casualties: Castanos 632, Paget 1,893. B…
  - ⚔ Castanos (lost 632) vs Paget (lost 1893) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - verbs: move×4, retreat×1, stance_change×1, unfortify×1, attack×1
- ORDER Davout [continues]: Davout marches to Franconia. 1 region to Bohemia.
- ORDER Ney [breaks]: Order cancelled: The trail has gone cold, Sire — Archduke Charles was last making for Munich, and Ney has no further word of him. Scout for him to ta…
- LEDGER treasury 12491 · net +835 · threat 78 · provinces 29 (+0) · ceiling 18736 · army 105811 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2712 · trade 587 · admin 50 · tribute 361 · upkeep 808 · charges 1401 · contributions 138 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Berry. No French corps stands in his path.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✓ Lannes begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Murat, drill` → ✗ Murat cannot drill with enemy forces nearby! Archduke John is at Franche-Comte, just one region away.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 155…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- SPENT 1552g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [completed]: Davout arrives at Bohemia. Davout: "It is done. I took the liberty of posting pickets."
- ORDER Lannes [active]: Lannes is marching to Bohemia (2 turns remaining).
- LEDGER treasury 12138 · net +1032 · threat 78 · provinces 30 (+1) · ceiling 19675 · army 108635 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2844 · trade 587 · admin 50 · tribute 412 · upkeep 832 · charges 1386 · contributions 80 · occupation 105 · blockade 368 · admiralty 90
- DISPATCH: Sire — Archduke John has crossed into Nivernais. No French corps stands in his path.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +6 medium/low (law_enacted_abroad ×3, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Munich to Franconia
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, m…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich.
  - saved `CMD-M_t10` → Game saved: CMD-M_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 1 action unused) Turn 11 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [completed]: Lannes arrives at Bohemia. Lannes: "Done — and I trust the next order has more fire in it."
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13182 · net +865 · threat 76 · provinces 30 (+0) · ceiling 19357 · army 108528 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2854 · trade 587 · admin 50 · tribute 414 · upkeep 832 · charges 1565 · contributions 80 · occupation 105 · blockade 368 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 2889 gold.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven

## Turn 11 — Late February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #13 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Bohemia, Franconia and Swabia stay ours by the treaty — titled. Status quo: Franche-Comte stays Austrian by the treaty. Status quo: Tyrol stays ours by the treaty — titled. Status quo: Milan and Piedmont stay Austrian by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, unfortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #14 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +8 (92 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 19049 · net +2605 · threat 38 · provinces 30 (+0) · ceiling 236083 · army 108528 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 88
  - NET income 2965 · trade 623 · admin 50 · tribute 78 · upkeep 832 · charges 204 · occupation 75
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia: Gold indemnity: 2889 gold from Britain to France.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, status_quo_titled ×2, diplomatic_dp_regen, blockade_broken ×3)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 76 to 38.

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Bohemia (field levy — no depot; capped at 3,000) - Cost: 300 gold (unstable region premium). Morale: 75% -> 67%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 300g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21322 · net +2567 · threat 38 · provinces 30 (+0) · ceiling 235166 · army 111528 · vassals Holland 99 · Kingdom of Italy 98 · Switzerland 87
  - NET income 2975 · trade 623 · admin 50 · tribute 81 · upkeep 856 · charges 231 · occupation 75
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Bohemia to Franconia
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 23897 · net +2544 · threat 38 · provinces 30 (+0) · ceiling 235833 · army 110868 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 86
  - NET income 2982 · trade 623 · admin 50 · tribute 82 · upkeep 856 · charges 262 · occupation 75
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 70).
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (open borders agreement)

## Turn 14 — Early April 1806
  - MAILBOX #12 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #15 → grant the petition
  - POPUP proposal_result: Franconia is ceded to the Kingdom of Italy. Loyalty +3 (97 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. Our net falls by 28g a turn — 192g of income forfeited, 20g of occupation relieved, 144g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Mack …
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Mack at Vienna instead.) → trust
  - POPUP diplomatic_dialogue: war_purpose_selection #16 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #17 → reconsider
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Brunswick at Berlin in…
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Brunswick at Berlin instead.) → trust
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #19 → reconsider
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Munich and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 26527 · net +2823 · threat 38 · provinces 29 (-1) · ceiling 261750 · army 110220 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 85
  - NET income 2843 · trade 623 · admin 50 · tribute 484 · upkeep 848 · charges 294 · occupation 35
- DISPATCH: Soult's fortifications strengthen: +11% defense (max 12%)
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 94% -> 88%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 29110 · net +2774 · threat 38 · provinces 29 (+0) · ceiling 260250 · army 112585 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2846 · trade 623 · admin 50 · tribute 487 · upkeep 872 · charges 325 · occupation 35
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #20 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia
- CMD `Lannes, unfortify` → ✗ Lannes is not currently fortified.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 31662 · net +2522 · threat 38 · provinces 29 (+0) · ceiling 241750 · army 112585 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2849 · trade 623 · admin 50 · tribute 262 · upkeep 872 · charges 355 · occupation 35
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 10).
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Boh…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 17 ended. Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 34187 · net +2494 · threat 38 · provinces 29 (+0) · ceiling 242000 · army 112585 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2852 · trade 623 · admin 50 · tribute 262 · upkeep 872 · charges 386 · occupation 35
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - TURN EVENTS 5
- DIPLO +5 medium/low (law_enacted_abroad ×3, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 36684 · net +2467 · threat 38 · provinces 29 (+0) · ceiling 242250 · army 112585 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2855 · trade 623 · admin 50 · tribute 262 · upkeep 872 · charges 416 · occupation 35
- DISPATCH: Ney's fortifications strengthen: +8% defense (MAX)
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Bohemia to Franconia (136 lost to march)
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 39154 · net +2778 · threat 38 · provinces 29 (+0) · ceiling 270583 · army 111760 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2858 · trade 623 · admin 50 · tribute 599 · upkeep 872 · charges 445 · occupation 35
- DISPATCH: Soult's fortifications decay: 12% → 11%
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-M_t20` → Game saved: CMD-M_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 41942 · net +2754 · threat 36 · provinces 29 (+0) · ceiling 271416 · army 111085 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2860 · trade 623 · admin 50 · tribute 599 · upkeep 864 · charges 479 · occupation 35
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 21 — Late July 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #21 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 1 action unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 44367 · net +2396 · threat 34 · provinces 29 (+0) · ceiling 244000 · army 110424 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2860 · trade 623 · admin 50 · tribute 262 · upkeep 856 · charges 508 · occupation 35
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 80).
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 22 — Early August 1806
  - MAILBOX #15 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #22 → grant the petition
  - POPUP proposal_result: Bohemia is ceded to the Kingdom of Italy. Loyalty +0 (100 → 100, already full); bond 40 → 40 (+2 a turn). Cost: 1 DP. Our net falls by 30g a turn — 200g of income forfeited, 20g of occupation relieved, 150g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Munich. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 46741 · net +2346 · threat 32 · provinces 28 (-1) · ceiling 242166 · army 109776 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2660 · trade 623 · admin 50 · tribute 412 · upkeep 848 · charges 536 · occupation 15
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 20).
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 49087 · net +2542 · threat 30 · provinces 28 (+0) · ceiling 260916 · army 109140 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2660 · trade 623 · admin 50 · tribute 637 · upkeep 848 · charges 565 · occupation 15
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 98% -> 92%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 51399 · net +2507 · threat 28 · provinces 28 (+0) · ceiling 260250 · army 111518 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2660 · trade 623 · admin 50 · tribute 637 · upkeep 856 · charges 592 · occupation 15
- DISPATCH: Massena's fortifications have crumbled completely!
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 53906 · net +2477 · threat 26 · provinces 28 (+0) · ceiling 260250 · army 110908 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2660 · trade 623 · admin 50 · tribute 637 · upkeep 856 · charges 622 · occupation 15
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 56383 · net +2447 · threat 24 · provinces 28 (+0) · ceiling 260250 · army 110310 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2660 · trade 623 · admin 50 · tribute 637 · upkeep 856 · charges 652 · occupation 15
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 90).
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 58830 · net +2418 · threat 22 · provinces 28 (+0) · ceiling 260250 · army 109724 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2660 · trade 623 · admin 50 · tribute 637 · upkeep 856 · charges 681 · occupation 15
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
  - MAILBOX #16 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #23 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Munich. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 61256 · net +2733 · threat 20 · provinces 28 (+0) · ceiling 289000 · army 109150 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2660 · trade 623 · admin 50 · tribute 974 · upkeep 848 · charges 711 · occupation 15
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 30).
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
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 63997 · net +2709 · threat 18 · provinces 28 (+0) · ceiling 289666 · army 108587 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2660 · trade 623 · admin 50 · tribute 974 · upkeep 840 · charges 743 · occupation 15
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)

## Turn 30 — Early December 1806
  - MAILBOX #17 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #24 → grant the petition
  - POPUP proposal_result: Swabia is ceded to the Kingdom of Italy. Loyalty +0 (100 → 100, already full); bond 40 → 40 (+2 a turn). Cost: 1 DP. Our net falls by 22g a turn — 150g of income forfeited, 15g of occupation relieved, 113g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-M_t30` → Game saved: CMD-M_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 66684 · net +2654 · threat 16 · provinces 27 (-1) · ceiling 287833 · army 108036 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 623 · admin 50 · tribute 1087 · upkeep 840 · charges 776
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 100).
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Prussia (defensive alliance)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Mack at Vienna instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Mack at Vienna instead.) → trust
  - POPUP diplomatic_dialogue: war_purpose_selection #25 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #26 → reconsider
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 69346 · net +2630 · threat 14 · provinces 27 (+0) · ceiling 288500 · army 107496 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 623 · admin 50 · tribute 1087 · upkeep 832 · charges 808
- DISPATCH: Soult's fortifications strengthen: +7% defense (max 12%)
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 32 — Early January 1807
  - MAILBOX #18 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #27 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 71976 · net +2599 · threat 12 · provinces 27 (+0) · ceiling 288500 · army 106966 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 623 · admin 50 · tribute 1087 · upkeep 832 · charges 839
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 74591 · net +2583 · threat 10 · provinces 27 (+0) · ceiling 289833 · army 106447 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 623 · admin 50 · tribute 1087 · upkeep 816 · charges 871
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Munich. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 77136 · net +2515 · threat 8 · provinces 27 (+0) · ceiling 286666 · army 105938 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 585 · admin 50 · tribute 1087 · upkeep 816 · charges 901
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
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 79651 · net +2485 · threat 6 · provinces 27 (+0) · ceiling 286666 · army 105439 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 585 · admin 50 · tribute 1087 · upkeep 816 · charges 931
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)

## Turn 36 — Early March 1807
  - MAILBOX #19 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #28 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 82136 · net +2455 · threat 4 · provinces 27 (+0) · ceiling 286666 · army 104951 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 585 · admin 50 · tribute 1087 · upkeep 816 · charges 961
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 84599 · net +2433 · threat 2 · provinces 27 (+0) · ceiling 287333 · army 104472 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 585 · admin 50 · tribute 1087 · upkeep 808 · charges 991
- DISPATCH: Ney's fortifications decay: 7% → 5%
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 87032 · net +2404 · threat 0 · provinces 27 (+0) · ceiling 287333 · army 104003 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 585 · admin 50 · tribute 1087 · upkeep 808 · charges 1020
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 89444 · net +2383 · threat 0 · provinces 27 (+0) · ceiling 288000 · army 103543 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 585 · admin 50 · tribute 1087 · upkeep 800 · charges 1049
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
  - MAILBOX #20 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #29 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Munich (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-M_t40` → Game saved: CMD-M_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 91827 · net +2355 · threat 0 · provinces 27 (+0) · ceiling 288000 · army 103093 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2510 · trade 585 · admin 50 · tribute 1087 · upkeep 800 · charges 1077
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

---
finished: **completed** · commands 200 · popups 55 · battles 17
