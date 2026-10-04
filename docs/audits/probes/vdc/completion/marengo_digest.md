# Playtest digest — vdc_final2-marengo

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `f3ce1b57a0d2` (dirty) · content `c60e8146a928` · driver `d93820e75501`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 85,373 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 3461, own corps) vs Mack (lost 9416) — Reinforcements from Davout and Napoleon bolstered Ney's position — though Soult, Lannes, Murat and Bernadotte never arr… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Mack.
- CMD `Lannes, move to Rhineland` → ✓ Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' Berthier adds: Ney and Murat would answer the guns — Lannes 18,000, 48,940 with the muster commi…
  - POPUP strategic_interrupt: Lannes, contact_bad_odds, Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' Berthier adds: Ney and Murat would answer the guns — Lannes 18,000, 48,940 with the muster committed, against Mack (42,584 men). → attack_anyway
  - ↳ Lannes attacks Mack and wins! Continuing his march. MUSTER — Lannes (18,000; expect about 48,940 with the corps likely to arrive, up to 52,502 if all march) vs Mack (42,584 men) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 2049, own corps) vs Mack (lost 9663) — Ney, Murat and Bernadotte's timely arrival aided Lannes. Soult, however, was conspicuously absent. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Deroy. Casualties: Archduke…
  - ⚔ Archduke Charles (lost 2449) vs Deroy (lost 7616) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
- ORDER Lannes [active]: Lannes is marching to Rhineland (3 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 1671 · net +1503 · threat 67 · provinces 28 · ceiling 35549 · army 173226 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2134 · blockade 250 · admiralty 90
- DISPATCH: Supply cost you 3,331 men, at Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,914; expect about 92,431 with the corps likely to arrive, up to 98,114 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 724, own corps) vs Mack (lost 20909) — Lannes, Massena and Teulie arrived to reinforce Ney, but Murat and Bernadotte failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✓ Davout pursues Mack (at Munich). Moves to Swabia. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interrupt…
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Dumonceau, move to Flanders` → ✓ Dumonceau moves from Amsterdam to Flanders
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria
  - verbs: attack×1, form_square×1, move×1, wait×1
- ORDER Davout [active]: Davout is pursuing Mack (0 turns remaining).
- ORDER Lannes [active]: Lannes answered the guns this turn and stands at Munich; his march resumes next turn.
- ENVOYS WAITING 2 · Portugal open borders · Denmark non aggression
- LEDGER treasury 3350 · net +1732 · threat 73 · provinces 28 (+0) · ceiling 38544 · army 164749 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 425 · admin 50 · tribute 937 · upkeep 1848 · charges 66 · blockade 266 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 5
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (15,837; expect about 75,665 with the corps likely to arrive, up to 79,553 if all march) vs Mack (small force) at Tyrol — the balance of force looks favorab…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 460, own corps) vs Mack (lost 7907, own corps) — Lannes, Massena and Teulie's timely arrival bolstered Ney's position. Well-coordinated, Sire. — The corps system brought Teulie in.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (22,871; expect about 36,192 with the corps likely to arrive, up to 44,970 if all march) vs Mack (2,228 men) at Franconia — the balance of force looks fa…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 3005, own corps) vs Archduke Charles (lost 3714) — Ney and Murat arrived in time to steady Davout's position. The field was held, nothing further. — The corps system brought Ney in. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Lannes, move to Swabia` → ✓ Lannes: 'Mack bars the way!' Engaging!
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 3864, own corps) vs Archduke Charles (lost 2997) — Reinforcements from Davout bolstered Lannes's position — though Bernadotte never arrived, Sire.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 682 gold (×3 at war) (×1.14 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- SPENT 682g on this turn's orders
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,125 troops. G…
  - ⚔ Archduke Charles (lost 1233) vs Deroy (lost 5517) — Even the favorable ground could not save Deroy, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×2, wait×2, stance_change×1, fortify×1
- ORDER Lannes [active]: Lannes is marching to Swabia (3 turns remaining).
  - ⚡ AUTONOMOUS: [Shield] Archduke Charles steps forward to cover Mack's retreat! "Mack is in no condition to fight - I'll handle this!"
  - ⚔ Murat (lost 6696) vs Archduke Charles (lost 2103) — A grievous defeat for Murat, Sire. The losses are severe.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Saxony open borders · Hesse non aggression
- LEDGER treasury 4195 · net +2246 · threat 81 · provinces 29 (+1) · ceiling 27010 · army 142737 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 93
  - NET income 2624 · trade 500 · admin 50 · tribute 937 · upkeep 1196 · charges 215 · occupation 52 · blockade 312 · admiralty 90
- DISPATCH: Sire — Lannes was mauled at Franconia: a quarter of his corps — 3,864 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (13,203; expect about 81,276 with the corps likely to arrive, up to 86,020 if all march) vs Mack (2,228 men) at Franconia — the balance of force looks favor…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 12, own corps) vs Mack (lost 1907) — Reinforcements from Davout, Lannes, Murat, Massena and Teulie bolstered Ney's position — though Bernadotte never arrive… — The corps system brought Teulie in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, fortify` → ✗ Davout cannot fortify while engaged with enemy forces! Enemy present: Archduke Charles, Archduke John. Attack or retreat first.
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Franconia to Tyrol (2,157 lost to march)
- CMD `Teulie, move to Tyrol` → ✓ Teulie moves from Franconia to Tyrol (127 lost to march)
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, move×1, wait×1, recruit×1
- ORDER Lannes [active]: Lannes answered the guns this turn and stands at Franconia; his march resumes next turn.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 1 · PapalStates open borders
- LEDGER treasury 6714 · net +2163 · threat 82 · provinces 29 (+0) · ceiling 27911 · army 136880 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 92
  - NET income 2625 · trade 562 · admin 50 · tribute 937 · upkeep 1088 · charges 480 · requisitions 50 · occupation 52 · blockade 351 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is taken at Franconia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,164g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 5 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (12,277; expect about 89,897 with the corps likely to arrive, up to 93,865 if all march) vs Archduke Charles (34,936 men) at Franconia — the balance of forc…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 719, own corps) vs Archduke Charles (lost 9972) — Massena and Teulie's timely arrival aided Ney. Bernadotte, however, was conspicuously absent.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✗ Cannot advance while engaged with Archduke Charles at Franconia. He may fall back to friendly ground — Tyrol — or fight.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Lannes [continues]: Lannes hears cannon fire at Franconia but cannot answer it — no road leads there. His march continues.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #9 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 43g a turn — 36g of income forfeited, 52g of occupation relieved, 27g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 8929 · net +2259 · threat 88 · provinces 28 (-1) · ceiling 38341 · army 127980 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2590 · trade 587 · admin 50 · tribute 964 · upkeep 992 · charges 532 · requisitions 50 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Massena and Teulie stand 78,027 men at Franconia, which feeds 32,000. 46,027 too many. 7,983 men lost in 2 turns. Living off the land: this stripped country feeds a…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL crisis_passed: Prussia stands down over Hanover, Sire — the moment passed — opportunism decayed.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 10 courts rebuff Austria (non-aggression pact)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Bohemia, just one region away.
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Bohemia instead.) → trust
  - ↳ MUSTER — Lannes (7,678; expect about 55,017 with the corps likely to arrive, up to 57,236 if all march) vs Archduke Charles (substantial force) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 523, own corps) vs Archduke Charles (lost 6889) — Ney, Davout, Massena and Teulie arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy marches from Munich into Franconia unopposed! (171 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: Deroy marches from Munich into Franconia unopposed! (171 lost to march) Captured: Austria → Bavaria
  - verbs: attack×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10820 · net +1567 · threat 89 · provinces 28 (+0) · ceiling 24858 · army 122249 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 587 · admin 50 · tribute 794 · upkeep 952 · charges 984 · contributions 110 · requisitions 50 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (10,331; expect about 55,807 with the corps likely to arrive, up to 58,200 if all march) vs Archduke Charles (substantial force) at Vienna — the balance of …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 572, own corps) vs Archduke Charles (lost 7148) — Reinforcements! Davout, Lannes, Massena and Teulie marched onto the field beside Ney. The enemy's advantage melted away.
- CMD `Davout, move to Bohemia` → ✗ Cannot advance while engaged with Archduke John at Vienna. No friendly province adjoins him: he must fight or stand.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (10,422) vs Archduke Charles (strength unknown) at Moravia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 1548) vs Archduke Charles (lost 8001) — Complete dominance on the field. Archduke Charles crumbled before Murat.
  - POPUP capture_choice[capture]: Moravia, Murat → secure
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 7 actions, 3 attacks — Britain, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden delivers an effective strike. Buxhowden gains the advantage over Murat. Casualties: Buxhowden 608, Murat 5,82… · Deroy delivers an effective strike. Deroy gains the advantage over Archduke Charles. Casualties: Deroy 933, Archduke Ch… · Deroy holds them at Hungary while allies attack from Bohemia! (+1 coordination)
  - 🏴 Bavaria: Deroy moves from Franconia to Bohemia. Bohemia falls to Bavaria!
  - ⚔ Buxhowden (lost 608) vs Murat (lost 5827) — A grievous defeat for Murat, Sire. The losses are severe.
  - ⚔ Deroy (lost 933) vs Archduke Charles (lost 2883) — The line gave way. Archduke Charles is falling back, and not in good order.
  - ⚔ Deroy (lost 801) vs Archduke John (lost 1995) — Even Archduke John's fortifications could not hold, Sire. Deroy overran the position.
  - verbs: attack×3, move×2, retreat×1, stance_change×1
- ORDER Murat [awaiting_response]: Murat is cornered at Moravia with 2,959 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Moravia with 2,959 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
  - POPUP diplomatic_dialogue: Russia, armistice_losing #12 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 11918 · net +1394 · threat 95 · provinces 29 (+1) · ceiling 23299 · army 108023 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 587 · admin 50 · tribute 796 · upkeep 848 · charges 1213 · contributions 110 · requisitions 75 · occupation 75 · blockade 368 · admiralty 90
- DISPATCH: Sire — Murat was mauled at Moravia: a third of his corps — 1,548 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 29 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 8 approaches to Britain and Russia are rebuffed (open borders agreement)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Russia (Open Borders Agreement)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Naples and Russia (Open Borders Agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Davout can give chase.
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Hunga…
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Hungary instead.) → trust
  - ↳ MUSTER — Ney (9,759; expect about 45,999 with the corps likely to arrive, up to 47,907 if all march) vs Archduke John (8,492 men) at Hungary — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 115, own corps) vs Archduke John (lost 5923) — Reinforcements! Davout, Lannes, Massena and Teulie marched onto the field beside Ney. The enemy's advantage melted away.
  - POPUP capture_choice[capture]: Hungary, Ney → secure
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena begins marching to Milan (distance: 3). Moved to Bohemia. Route: Bohemia -> Tyrol -> Milan.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy delivers an effective strike. Brutal stalemate between Deroy and Archduke Charles. Heavy casualties on both sides… · Deroy delivers an effective strike. Deroy gains the advantage over Archduke John. Casualties: Deroy 102, Archduke John …
  - 🏴 Bavaria: FORCED RETREAT! ArchdukeCharles retreats! Deroy pursues into Carniola. (164 lost to march) Carniola has been captured by Bavaria!
  - 🏴 Bavaria: [!] MARSHAL CAPTURED — ArchdukeJohn is taken by Bavaria at Croatia!
  - ⚔ Deroy (lost 1206) vs Archduke Charles (lost 1780) — Archduke Charles was driven from the field. His men are scattered.
  - ⚔ Deroy (lost 102) vs Archduke John (lost 900) — The walls were not enough. Deroy broke through Archduke John's prepared defenses. And Archduke John was taken on that f…
  - verbs: wait×2, attack×2, move×1
- ORDER Massena [active]: Massena is marching to Milan (3 turns remaining).
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 13206 · net +1116 · threat 97 · provinces 30 (+1) · ceiling 22087 · army 106184 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2617 · trade 587 · admin 50 · tribute 796 · upkeep 832 · charges 1407 · contributions 110 · occupation 127 · blockade 368 · admiralty 90
- DISPATCH: Sire — Marshal Murat has been taken. Russia holds him prisoner.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, diplomatic_ai_ai_treaty, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 9 approaches from Russia and Prussia are rebuffed (defensive alliance)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Russia and Naples (Non-Aggression Pact)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 2 more — France is not forgiven

## Turn 9 — Late January 1806
  - MAILBOX #11 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #14 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✓ Lannes moves from Hungary to Bohemia (60 lost to march)
- CMD `Murat, drill` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier checks the order of battle. 'No marshal of cavalry can reach Paris, Sire — none of ours stands within reach.' No commander of horse serves us, and none waits on…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy takes Croatia where he stands! Captured: Austria → Bavaria · Deroy's forces press forward aggressively. Deroy gains the advantage over Archduke Charles. Casualties: Deroy 721, Arch…
  - 🏴 Bavaria: Deroy takes Croatia where he stands! Captured: Austria → Bavaria
  - ⚔ Deroy (lost 721) vs Archduke Charles (lost 2567) — Even the favorable ground could not save Archduke Charles, Sire. Deroy overcame the terrain.
  - verbs: wait×2, attack×2, retreat×1, stance_change×1
- ORDER Massena : Massena: 'Cannon fire at Carniola, Sire. Bavaria and Austria are at war; France is not in it. Investigate?'
  - POPUP strategic_interrupt: Massena, cannon_fire, Massena: 'Cannon fire at Carniola, Sire. Bavaria and Austria are at war; France is not in it. Investigate?' → investigate
- LEDGER treasury 14283 · net +910 · threat 95 · provinces 30 (+0) · ceiling 21347 · army 105171 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 98
  - NET income 2618 · trade 587 · admin 50 · tribute 796 · upkeep 824 · charges 1582 · contributions 150 · occupation 127 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 2
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed, law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 6 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 17 approaches from Denmark, Bavaria and Austria are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney begins marching to Franconia (distance: 2). Moved to Bohemia. Route: Bohemia -> Franconia.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Hungary. Defense bonus: +7% (grows +3% per turn, m…
- CMD `Soult, move to Bavaria` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 10 ended. Turn 11 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy engages in solid combat. Deroy gains the advantage over Archduke Charles. Casualties: Deroy 451, Archduke Charles…
  - ⚔ Deroy (lost 451) vs Archduke Charles (lost 2415) — The line gave way. Archduke Charles is falling back, and not in good order.
  - verbs: attack×1, wait×1
- ORDER Ney [active]: Ney is marching to Franconia (2 turns remaining).
- ORDER Teulie : Teulie: 'Cannon fire at Bohemia, Sire. Bavaria and Austria are at war; France is not in it. Investigate?'
  - POPUP strategic_interrupt: Teulie, cannon_fire, Teulie: 'Cannon fire at Bohemia, Sire. Bavaria and Austria are at war; France is not in it. Investigate?' → investigate
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 15338 · net +877 · threat 93 · provinces 30 (+0) · ceiling 21977 · army 105081 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 97
  - NET income 2710 · trade 587 · admin 50 · tribute 796 · upkeep 816 · charges 1760 · contributions 150 · occupation 82 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Ukraine.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,188g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #12 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #16 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain (6 pairs resolved). Status quo: Hungary, Moravia and Tyrol stay ours by the treaty — titled. Status quo: Bohemia, Carniola and Croatia stay Bavarian by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #17 → 1
  -     ↳ refused: The armistice with Austria holds for 5 more turns. We cannot declare war until it expires.
- CMD `Lannes, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  -     ↳ refused: The armistice with Austria holds for 5 more turns. We cannot declare war until it expires.
- CMD `Murat, move to Franconia` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. Turn 12 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2, drill×1, stance_change×1
- ORDER Ney [completed]: Ney arrives at Franconia. Ney: "Done — and I trust the next order has more fire in it."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #19 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 18040 · net +2244 · threat 45 · provinces 30 (+0) · ceiling 68116 · army 104992 · vassals Holland 100 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2712 · trade 611 · admin 50 · tribute 487 · upkeep 816 · charges 718 · occupation 82
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 5
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +8 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent, coercive_demand, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: 7 approaches from Britain and Prussia are rebuffed (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 93 to 46.
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Prussia are rebuffed (defensive alliance)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Bohemia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3, recruit×2, drill×1
- ORDER Dumonceau [completed]: Dumonceau arrives at Amsterdam. Dumonceau: "Accomplished as ordered. The army is intact."
- ORDER Teulie [continues]: Teulie marches to Tyrol. 1 region to Milan.
- LEDGER treasury 19826 · net +1607 · threat 45 · provinces 30 (+0) · ceiling 42393 · army 104992 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 95
  - NET income 2716 · trade 611 · admin 50 · tribute 487 · upkeep 816 · charges 1269 · occupation 82 · admiralty 90
- DISPATCH: Sire — Marshal Davout has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: And Prussia stirs at its own design.
- DIPLO +7 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent ×2, diplomatic_relation_shift)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Davout, move to Franconia` → ✓ Davout begins marching to Franconia (distance: 2). Moved to Bohemia. Route: Bohemia -> Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: 7 actions, 1 attacks — Britain, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen marches from Podolia into Moravia unopposed! (44 lost to march) Captured: France → Russia
  - 🏴 Russia: Bennigsen marches from Podolia into Moravia unopposed! (44 lost to march) Captured: France → Russia
  - 🏴 Russia: Bennigsen moves from Moravia to Hungary. Hungary falls to Russia!
  - verbs: wait×3, attack×1, move×1, drill×1, recruit×1
- ORDER Davout [active]: Davout is marching to Franconia (2 turns remaining).
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 21924 · net +1948 · threat 45 · provinces 28 (-2) · ceiling 65783 · army 104885 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 94
  - NET income 2590 · trade 611 · admin 50 · tribute 487 · upkeep 816 · charges 884 · admiralty 90
- DISPATCH: Sire — Moravia has been taken by Russia.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 14 — Early April 1806
  - MAILBOX #14 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #20 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (3896g forgone). Loyalty +1 (99 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'We outnumber them! Let me attack!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Bennigse…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'We outnumber them! Let me attack!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Bennigsen at Hungary instead.) → trust
  - ↳ MUSTER — Lannes (6,017; expect about 11,693 with the corps likely to arrive, up to 11,830 if all march) vs Bennigsen (screening force) at Hungary — the balance of force looks even — a hard fight that may go against us.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 533, own corps) vs Bennigsen (lost 788) — The reinforcement arrived, Sire. The verdict of the field went against us regardless. — Slow to concentrate's orders reached Kutuzov too late.
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Carniola and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 23318 · net +1546 · threat 45 · provinces 28 (+0) · ceiling 54991 · army 103558 · vassals Holland 95 · Kingdom of Italy 98 · Switzerland 91
  - NET income 2590 · trade 611 · admin 50 · tribute 225 · upkeep 800 · charges 1040 · admiralty 90
- DISPATCH: Sire — Lannes's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 10
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (non-aggression pact)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Bavaria (open borders agreement)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✗ Davout is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 24864 · net +1398 · threat 45 · provinces 28 (+0) · ceiling 51730 · army 103558 · vassals Holland 94 · Kingdom of Italy 98 · Switzerland 90
  - NET income 2590 · trade 611 · admin 50 · tribute 225 · upkeep 800 · charges 1188 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 9 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,222 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, agenda_shift)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 16 — Early May 1806
  - MAILBOX #15 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #21 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia (88 lost to march)
- CMD `Lannes, unfortify` → ✗ Lannes is not currently fortified.
- CMD `Murat, fortify` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 3 actions unused) Turn 17 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden delivers an effective strike. Buxhowden gains the advantage over Ney. Casualties: Buxhowden 1,460, Ney's army…
  - ⚔ Buxhowden (lost 1460) vs Ney (lost 2089, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - verbs: attack×1, wait×1
- LEDGER treasury 25806 · net +995 · threat 45 · provinces 28 (+0) · ceiling 42839 · army 99579 · vassals Holland 91 · Kingdom of Italy 96 · Switzerland 98
  - NET income 2590 · trade 611 · admin 50 · upkeep 776 · charges 1390 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (non-aggression pact)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Kutuzov at Vienna instead.)
  - POPUP objection: Ney, Ney respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Kutuzov at Vienna instead.) → trust
  - ↳ MUSTER — Ney (6,721) vs Kutuzov (substantial force) at Vienna — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2822) vs Kutuzov (lost 326, own corps) — Attacking prepared positions cost Ney dearly. The fortifications held.
- CMD `Davout, fortify` → ✗ Davout is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Carniola (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 2 actions unused) Turn 18 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden delivers an effective strike. Buxhowden gains the advantage over Ney. Casualties: Buxhowden 184, Ney 1,770. B…
  - ⚔ Buxhowden (lost 184) vs Ney (lost 1770) — A grievous defeat for Ney, Sire. The losses are severe.
  - verbs: wait×4, attack×1, grant_dotation×1
- LEDGER treasury 26541 · net +825 · threat 45 · provinces 28 (+0) · ceiling 39193 · army 94296 · vassals Holland 86 · Kingdom of Italy 92 · Switzerland 94
  - NET income 2590 · trade 611 · admin 50 · upkeep 736 · charges 1600 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Bohemia. He must reform before he fights again.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Sardinia lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Carniola, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, fortify×1, recruit×1
- LEDGER treasury 27374 · net +698 · threat 45 · provinces 28 (+0) · ceiling 37570 · army 93630 · vassals Holland 85 · Kingdom of Italy 92 · Switzerland 94
  - NET income 2590 · trade 611 · admin 50 · upkeep 728 · charges 1735 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 12 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Sardinia against France (300g/turn)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
- CMD `Murat, drill` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 28080 · net +911 · threat 45 · provinces 28 (+0) · ceiling 40798 · army 92979 · vassals Holland 84 · Kingdom of Italy 92 · Switzerland 94
  - NET income 2590 · trade 611 · admin 50 · tribute 337 · upkeep 720 · charges 1867 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Carniola. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden engages in solid combat. Buxhowden gains the advantage over Ney. Casualties: Buxhowden 2,307, Ney's army 4,12…
  - ⚔ Buxhowden (lost 2307) vs Ney (lost 335, own corps) — The hills were ours, but Buxhowden took them. Ney's position was overrun.
  - verbs: move×1, attack×1, garrison×1, wait×1
- ORDER Ney [awaiting_response]: Ney is cornered at Carniola with 1,659 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Carniola with 1,659 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 27952 · net -5 · threat 45 · provinces 28 (+0) · ceiling 27900 · army 87127 · vassals Holland 81 · Kingdom of Italy 90 · Switzerland 92
  - NET income 2590 · trade 611 · admin 50 · tribute 337 · upkeep 680 · charges 2823 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Carniola. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
  - MAILBOX #16 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (81 → 91); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Davout, drill` → ✗ Davout is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Napoleon commands our foot at Lorraine — march hi…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden's forces press forward aggressively. Brutal stalemate between Buxhowden and Massena. Heavy casualties on both…
  - ⚔ Buxhowden (lost 2322) vs Massena (lost 2064) — The enemy's repeated assaults have leveled our defenses. We fight without cover.
  - verbs: attack×1, wait×1, recruit×1
- LEDGER treasury 27513 · net +107 · threat 45 · provinces 28 (+0) · ceiling 28453 · army 85063 · vassals Holland 91 · Kingdom of Italy 90 · Switzerland 92
  - NET income 2590 · trade 611 · admin 50 · tribute 487 · upkeep 664 · charges 2877 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Russia holds him prisoner.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Carniola. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 27620 · net +13 · threat 45 · provinces 28 (+0) · ceiling 27724 · army 85063 · vassals Holland 91 · Kingdom of Italy 90 · Switzerland 92
  - NET income 2590 · trade 611 · admin 50 · tribute 487 · upkeep 664 · charges 2971 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 28401 · net +855 · threat 45 · provinces 28 (+0) · ceiling 37975 · army 85063 · vassals Holland 91 · Kingdom of Italy 90 · Switzerland 92
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 664 · charges 2354 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Carniola. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden's forces advance steadily. Buxhowden gains the advantage over Massena. Casualties: Buxhowden 1,890, Massena 3…
  - ⚔ Buxhowden (lost 1890) vs Massena (lost 3123) — Even Massena's fortifications could not hold, Sire. Buxhowden overran the position.
  - verbs: move×2, wait×2, attack×1, recruit×1
- LEDGER treasury 28266 · net -66 · threat 45 · provinces 28 (+0) · ceiling 27740 · army 81940 · vassals Holland 89 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 640 · charges 3299 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 actions unused) Turn 26 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden delivers an effective strike. Buxhowden gains the advantage over Massena. Casualties: Buxhowden 1,827, Massen…
  - ⚔ Buxhowden (lost 1827) vs Massena (lost 2590, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless. — The corps system brought Davout in.
  - verbs: attack×1, wait×1
- LEDGER treasury 28008 · net -157 · threat 45 · provinces 28 (+0) · ceiling 26810 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 608 · charges 3422 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Carniola. He must reform before he fights again.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Massena is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 27851 · net -219 · threat 45 · provinces 28 (+0) · ceiling 26221 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 608 · charges 3484 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 28407 · net +414 · threat 45 · provinces 28 (+0) · ceiling 32231 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 608 · charges 2851 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Murat, fortify` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 28821 · net +620 · threat 45 · provinces 28 (+0) · ceiling 34392 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 1049 · upkeep 608 · charges 2982 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 22 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 29441 · net +463 · threat 45 · provinces 28 (+0) · ceiling 33486 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 1049 · upkeep 608 · charges 3139 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 29904 · net +321 · threat 45 · provinces 28 (+0) · ceiling 32629 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 1049 · upkeep 608 · charges 3281 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 24 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 2 actions unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 30225 · net +193 · threat 45 · provinces 28 (+0) · ceiling 31817 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 1049 · upkeep 608 · charges 3409 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 30418 · net +79 · threat 45 · provinces 28 (+0) · ceiling 31048 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 1049 · upkeep 608 · charges 3523 · admiralty 90
- DISPATCH: Sire — Marshal Davout's claim is 26 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
  - MAILBOX #17 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #23 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Napoleon commands our foot at Lorraine — march hi…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 33349 · net +2852 · threat 45 · provinces 28 (+0) · ceiling 139761 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 1049 · upkeep 608 · charges 840
- DISPATCH: Sire — a truce with Russia is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +2 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 36163 · net +2739 · threat 45 · provinces 28 (+0) · ceiling 138343 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 573 · admin 50 · tribute 1049 · upkeep 608 · charges 915
- DISPATCH: Sire — Marshal Davout's claim is 28 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (open borders agreement)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 38902 · net +2666 · threat 45 · provinces 28 (+0) · ceiling 138343 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 573 · admin 50 · tribute 1049 · upkeep 608 · charges 988
- DISPATCH: Sire — Marshal Davout's claim is 29 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 41568 · net +2594 · threat 45 · provinces 28 (+0) · ceiling 138343 · army 78292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 573 · admin 50 · tribute 1049 · upkeep 608 · charges 1060
- DISPATCH: Sire — Marshal Davout's claim is 30 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Marshal Murat is a prisoner of Russia, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 44680 · net +3074 · threat 45 · provinces 28 (+0) · ceiling 300833 · army 88292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 585 · admin 50 · tribute 1049 · upkeep 688 · charges 512
- DISPATCH: Sire — the establishment stands 41,708 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - RAIL diplomatic_armistice_expired_peace: The armistice between France and Russia has concluded. Peace declared.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, agenda_shift)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 47754 · net +3037 · threat 45 · provinces 28 (+0) · ceiling 300833 · army 88292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 585 · admin 50 · tribute 1049 · upkeep 688 · charges 549
- DISPATCH: Sire — Marshal Davout's claim is 32 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. Turn 40 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 50791 · net +3001 · threat 45 · provinces 28 (+0) · ceiling 300833 · army 88292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 585 · admin 50 · tribute 1049 · upkeep 688 · charges 585
- DISPATCH: Sire — Marshal Davout's claim is 33 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 53792 · net +2965 · threat 45 · provinces 28 (+0) · ceiling 300833 · army 88292 · vassals Holland 87 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 585 · admin 50 · tribute 1049 · upkeep 688 · charges 621
- DISPATCH: Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,188g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (open borders agreement)

---
finished: **completed** · commands 200 · popups 65 · battles 30
