# Playtest digest — rf1-q0-gev-a-staff

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `6ceadabe3009` (dirty) · content `c3429ce4d4d0` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `declare war on Hanover` → ✓ Choose your war purpose against Hanover.
  - POPUP diplomatic_dialogue: war_purpose_selection #1 → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Hanover. Our threat level stands at 70 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Hanover → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #2 → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Hanover! Holland follows France into the war against Hanover! KingdomOfItaly follows France into the war against Hanover! Switzerland follows France into the war against Hanover! → display-only
- CMD `vassalize Bavaria` → ✓ Bavaria has become a Satellite vassal of France (loyalty: 60). Marshals assimilated: Deroy.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1850, own corps) vs Mack (lost 15045) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat, Bernadotte and Deroy ne…
- CMD `Davout, attack Mack` → ✓ Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will adopt DEFENSIVE stance instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will adopt DEFENSIVE stance instead.) → trust
- CMD `Lannes, attack Mack` → ✓ MUSTER — Lannes (16,612; expect about 75,679 with the corps likely to arrive, up to 91,899 if all march) vs Mack (36,955 men) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 714, own corps) vs Mack (lost 23117) — Soult, Murat, Bernadotte and Deroy never reached the guns. The battle was decided without them, Sire. And Mack was take…
- CMD `Murat, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 1 action unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Massena. Heavy casual…
  - ⚔ Archduke Charles (lost 3624, own corps) vs Massena (lost 6504) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 2 · Denmark open borders · Hesse open borders
- LEDGER treasury 2108 · net +2083 · threat 97 · provinces 28 · ceiling 50310 · army 192878 · vassals Bavaria 64 · Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 3400 · trade 200 · admin 50 · tribute 1339 · upkeep 2712 · charges 4 · blockade 100 · admiralty 90
- DISPATCH: Sire — Marshal Mack of Austria is taken at Swabia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_war_declared: France has declared war on Hanover, with 2 allied courts poised to follow.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +7 medium/low (diplomatic_carved_vassal_created, diplomatic_we_threshold, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

## Turn 2 — Early October 1805
  - LETTER Denmark: Open Borders Agreement → accept
  - LETTER Hesse: Open Borders Agreement → accept
- CMD `vassalize Saxony` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: PEACE).
- CMD `Soult, move to Brabant` → ✓ Soult moves from Lorraine to Brabant (900 lost to march)
- CMD `Bernadotte, move to Swabia` → ✓ Bernadotte moves from Franconia to Swabia (170 lost to march)
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles a…
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Tyrol instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 9417) vs Archduke Charles (lost 2406, own corps) — Massena stood alone, Sire. Deroy never came.
- CMD `Deroy, move to Munich` → ✓ Deroy moves from Franconia to Munich (616 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles marches from Piedmont into Provence unopposed! (1,216 lost to march) Captured: France → Austria
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Milan. (1,334 lost to march) Milan has been captured by Austria!
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (1,216 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 2010) vs Massena (lost 7190) — Where was Deroy? Massena held the field alone — reinforcement never came.
  - verbs: attack×2
- LEDGER treasury 3632 · net +2193 · threat 85 · provinces 27 (-1) · ceiling 39224 · army 170020 · vassals Bavaria 64 · Holland 97 · Switzerland 95
  - NET income 3200 · trade 337 · admin 50 · tribute 1009 · upkeep 2044 · charges 100 · blockade 169 · admiralty 90
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - TURN EVENTS 3
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 13 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 5 approaches from Austria and Prussia are rebuffed (defensive alliance)

## Turn 3 — Late October 1805
- CMD `vassalize Saxony` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: PEACE).
- CMD `vassalize Hesse` → ✓ Hesse has become a Satellite vassal of France (loyalty: 60).
- CMD `Soult, move to Flanders` → ✓ Soult moves from Brabant to Flanders
- CMD `Ney, move to Munich` → ✓ Ney moves from Swabia to Munich (385 lost to march)
- CMD `Davout, move to Munich` → ✓ Davout moves from Swabia to Munich (526 lost to march)
- CMD `Lannes, move to Munich` → ✓ Lannes moves from Swabia to Munich (293 lost to march)
- CMD `end turn` → ✓ Turn 3 ended. Turn 4 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Provence into Lyonnais unopposed! (1,180 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Provence into Lyonnais unopposed! (1,180 lost to march) Captured: France → Austria
  - verbs: move×3, attack×1
- LEDGER treasury 6172 · net +2375 · threat 88 · provinces 26 (-1) · ceiling 42817 · army 163202 · vassals Bavaria 68 · Hesse 57 · Holland 98 · Switzerland 94
  - NET income 3100 · trade 300 · admin 50 · tribute 1273 · upkeep 1838 · charges 270 · blockade 150 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_carved_vassal_created, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Naples are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 15 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 4 — Early November 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 6,172.
- CMD `vassalize Hesse` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: VASSAL).
- CMD `Soult, move to Oldenburg` → ✓ Soult moves from Flanders to Oldenburg. Oldenburg falls to France! (was Hanover) (809 lost to march)
  - POPUP capture_choice[capture]: Oldenburg, Soult → secure
- CMD `Ney, attack Archduke John` → ✓ MUSTER — Ney (17,779; expect about 36,970 with the corps likely to arrive, up to 52,482 if all march) vs Archduke John (16,857 men) at Tyrol — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 3121, own corps) vs Archduke John (lost 1342, own corps) — Reinforcements from Lannes bolstered Ney's position — though Davout and Deroy never arrived, Sire.
- CMD `Davout, attack Archduke John` → ✓ Davout notes the risks but prepares the attack. Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be …
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be told twice than bury them once."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (19,439; expect about 25,179 with the corps likely to arrive, up to 31,636 if all march) vs Archduke John (15,515 men) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Ney: will march to the sound of the guns — may make it from the mountains at Munich in time (about 47%); order 'Ney, support Davout' and it rises to about 99%
  WILL NOT — Lannes: has already marched this turn
  WILL NOT — Massena: is in no condition to fight
  WILL NOT — Deroy: awaits explicit orders and will NOT march — order 'Deroy, support Davout' and he will march
  ArchdukeJohn does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him.
  The band weighs more than the men: Davout attacks from a defensive stance (−10%); all told, Davout's own modifiers weigh 10% against the attack; the ground favors the defender (+25%, mountains); Archduke John stands +42% on the defense (his stance, his character and his works).
  Tyrol feeds 20,000 — the whole muster standing there would lose ~700 men a turn to short supply.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - POPUP objection: Davout, Davout firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.) → trust
- CMD `Murat, move to Munich` → ✓ Murat moves from Franche-Comte to Munich (616 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×2, unfortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Denmark, non_aggression #6 → accept
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 8535 · net +2370 · threat 88 · provinces 27 (+1) · ceiling 31950 · army 150051 · vassals Bavaria 72 · Hesse 54 · Holland 99 · Switzerland 93
  - NET income 3125 · trade 300 · admin 50 · tribute 1275 · upkeep 1444 · charges 661 · occupation 35 · blockade 150 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Massena and Deroy stand 97,670 men at Munich, which feeds 37,500. 60,170 too many. 12,287 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is …
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 9
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia and Naples (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 5 — Late November 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 8,535.
- CMD `vassalize Hesse` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: VASSAL).
- CMD `Soult, attack Hanover` → ✓ ASSAULT — Soult storms the works at Hanover alone: 28,163 men, 32,387 in the assault's reckoning, against a garrison of 10,000. the garrison breaks below 5,000.
  - ↳ Soult assaults the Hanover garrison! Garrison: 10,000 -> 5,000 (-5,000). Soult loses 2,173 troops. Garrison holds — 5,000 defenders remain. It regains up to 2,000 a turn…
- CMD `Ney, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `Davout, move to Tyrol` → ✗ Davout is fortified at Munich and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Lannes, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 3 actions unused) Turn 6 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, fortify×1, wait×1
- ENVOYS WAITING 3 · Denmark non aggression · Hanover armistice losing · Switzerland client petition
- LEDGER treasury 11033 · net +2328 · threat 86 · provinces 27 (+0) · ceiling 32911 · army 142020 · vassals Bavaria 74 · Hesse 49 · Holland 98 · Switzerland 90
  - NET income 3125 · trade 300 · admin 50 · tribute 1277 · upkeep 1188 · charges 961 · occupation 35 · blockade 150 · admiralty 90
- DISPATCH: Sire — 3 turns of famine at Munich now. 17,704 men gone, and not one of them to the enemy. Bavaria's magazines feed us as our own — the army is simply too large for the province. Franconia can feed 6…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hanover has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #4 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - MAILBOX #5 Hanover incoming_proposal: Hanover — Armistice → activated
  - MAILBOX #6 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #7 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #9 → grant the petition
  - POPUP diplomatic_dialogue: Denmark, non_aggression #7 → accept
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond -15 → 5 (+0 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Hanover, armistice_losing #8 → accept
  - POPUP proposal_result: You have accepted Hanover's proposal. Treaty signed: At War → Armistice with Hanover. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `enact the Staff` → ✓ The Grand Quartier Général is in force — enacted for 9,000 gold. It costs 300 gold a turn from now on. From the next refill, one more order each day.
- CMD `vassalize Hesse` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: VASSAL).
- CMD `Soult, attack Hanover` → ✓ Choose your war purpose against Hanover. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #10 → 1
  -     ↳ refused: The armistice with Hanover holds for 5 more turns. We cannot declare war until it expires.
- CMD `Ney, move to Bohemia` → ✓ Ney begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Davout, move to Bohemia` → ✗ Davout is fortified at Munich and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Bernadotte, move to Rhineland` → ✓ Bernadotte moves from Swabia to Rhineland
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 6 ended. Turn 7 begins!
- SPENT 9000g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- ORDER Ney [active]: Ney is marching to Bohemia (2 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Deroy seeks an audience → acknowledge
  -     ↳ Deroy's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #11 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 4 · Prussia open borders · Portugal open borders · Denmark non aggression · Holland client petition
- LEDGER treasury 4926 · net +2706 · threat 84 · provinces 27 (+0) · ceiling 38909 · army 137434 · vassals Bavaria 78 · Hesse 41 · Holland 97 · Switzerland 98
  - NET income 3175 · trade 337 · admin 50 · tribute 1055 · upkeep 1100 · charges 232 · occupation 20 · blockade 169 · admiralty 90 · laws 300
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL armistice_ratified: A truce with Hanover: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 8
- COURTS: The court of Prussia eases over The Hanoverian Prize — alliance is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Holland rebuffs Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (open borders agreement)

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #9 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - MAILBOX #10 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #13 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #14 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +3 (97 → 100); bond -15 → 5 (+0 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #14 → grant the petition
  -     ↳ refused: Sire, another matter has arrived since — this concerns Denmark. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #13 → accept_ai_proposal
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `vassalize Hesse` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: VASSAL).
- CMD `Soult, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Ney, attack Vienna` → ✗ Ney cannot reach Vienna from Franconia! Range: 1, Distance: 2
- CMD `Davout, attack Vienna` → ✗ Davout is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Lannes, move to Bohemia` → ✓ Lannes begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [active]: Lannes is marching to Bohemia (2 turns remaining).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Lannes: They settle into cold war.
  - POPUP diplomatic_dialogue: Denmark, non_aggression #15 → accept
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 7470 · net +2196 · threat 82 · provinces 27 (+0) · ceiling 33980 · army 134672 · vassals Bavaria 82 · Hesse 33 · Holland 100 · Switzerland 96
  - NET income 3175 · trade 362 · admin 50 · tribute 720 · upkeep 1068 · charges 452 · occupation 20 · blockade 181 · admiralty 90 · laws 300
- DISPATCH: Sire — Davout, Murat, Massena and Deroy have been 5 turns over what Munich can feed. 12,985 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 10
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Prussia (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 8 — Early January 1806
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Soult, move to Osnabruck` → ✗ Cannot enter Osnabruck — it is controlled by Hanover (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Ney, attack Vienna` → ✗ Ney cannot reach Vienna from Franconia! Range: 1, Distance: 2
- CMD `Davout, attack Vienna` → ✗ Davout is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Lannes, attack Vienna` → ✗ Lannes cannot reach Vienna from Franconia! Range: 1, Distance: 2
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 5 actions unused) Turn 9 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, form_square×1
- ENVOYS WAITING 2 · Denmark non aggression · PapalStates open borders
- LEDGER treasury 9827 · net +2017 · threat 80 · provinces 27 (+0) · ceiling 33279 · army 132178 · vassals Bavaria 86 · Hesse 25 · Holland 100 · Switzerland 94
  - NET income 3175 · trade 387 · admin 50 · tribute 722 · upkeep 1040 · charges 673 · occupation 20 · blockade 194 · admiralty 90 · laws 300
- DISPATCH: Sire — Davout, Murat, Massena and Deroy have been 6 turns over what Munich can feed. 9,621 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply t…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (defensive alliance)

## Turn 9 — Late January 1806
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #13 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #17 → accept
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `Ney, attack Vienna` → ✗ Ney cannot reach Vienna from Franconia! Range: 1, Distance: 2
- CMD `Davout, attack Vienna` → ✗ Davout is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Lannes, attack Vienna` → ✗ Lannes cannot reach Vienna from Franconia! Range: 1, Distance: 2
- CMD `Bernadotte, move to Brabant` → ✓ Bernadotte moves from Rhineland to Brabant (160 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 3 actions, 0 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, unfortify×1, form_square×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 12046 · net +1884 · threat 78 · provinces 27 (+0) · ceiling 33165 · army 129684 · vassals Bavaria 90 · Hesse 17 · Holland 100 · Switzerland 92
  - NET income 3200 · trade 412 · admin 50 · tribute 724 · upkeep 1000 · charges 896 · occupation 10 · blockade 206 · admiralty 90 · laws 300
- DISPATCH: Sire — Davout, Murat, Massena and Deroy have been 7 turns over what Munich can feed. 7,498 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply t…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)

## Turn 10 — Early February 1806
  - MAILBOX #15 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #19 → accept
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #20 → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `Ney, move to Vienna` → ✓ Ney: 'ArchdukeCharles blocks the path at Bohemia. Odds unfavorable. Your orders?'
  - POPUP strategic_interrupt: Ney, contact_bad_odds, Ney: 'ArchdukeCharles blocks the path at Bohemia. Odds unfavorable. Your orders?' → attack_anyway
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2523, own corps) vs Archduke Charles (lost 1709, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Davout, move to Hungary` → ✗ Davout is fortified at Munich and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke Charles, Hiller.
- CMD `Bernadotte, move to Flanders` → ✓ Bernadotte moves from Brabant to Flanders
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `rf1-q0-gev-a-staff_t10` → Game saved: rf1-q0-gev-a-staff_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 10 actions, 4 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles holds them at Franconia while allies attack from Tyrol! (+1 coordination) · Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 565, Paget … · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - ⚔ Archduke Charles (lost 2096) vs Ney (lost 975, own corps) — Reinforcements from Massena and Napoleon bolstered Ney's position — though Murat and Deroy never arrived, Sire.
  - ⚔ Archduke Charles (lost 598, own corps) vs Lannes (lost 2489, own corps) — Lannes fought without Deroy's support. The roads, or the will, proved insufficient.
  - ⚔ Castanos (lost 565) vs Paget (lost 1577) — Paget's aggressive posture left the troops exposed when Castanos's attack came.
  - ⚔ Castanos (lost 249) vs Paget (lost 1006) — Paget was caught in an aggressive posture when Castanos struck, Sire. A defensive stance would have served better.
  - verbs: move×5, attack×4, break_square×1
- ORDER Lannes [awaiting_response]: Lannes is cornered at Franconia with 4,208 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Franconia with 4,208 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 3 · Austria peace · Britain settlement offer · Denmark non aggression
- LEDGER treasury 13159 · net +1653 · threat 76 · provinces 27 (+0) · ceiling 28982 · army 108257 · vassals Bavaria 88 · Hesse 3 · Holland 94 · Switzerland 84
  - NET income 3200 · trade 412 · admin 50 · tribute 577 · upkeep 816 · charges 1164 · occupation 10 · blockade 206 · admiralty 90 · laws 300
- DISPATCH: Sire — Massena's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Hesse is on the verge of rebellion!
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Hanover has collapsed. War resumes!
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as service to the strong.
- DIPLO +3 medium/low (diplomatic_proposal_sent, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_ai_proposal_refused: 4 approaches from Britain, Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 11 — Late February 1806
  - MAILBOX #18 Austria counter_offer_response: Austria — Peace Treaty → activated
  - MAILBOX #17 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #16 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Austria, peace #24 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Denmark. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #21 → accept_ai_proposal
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
  - POPUP vassal_rebellion_imminent: Hesse #23 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Hesse's loyalty reaches zero, rebellion will follow. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #22 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #25 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Hanover + Russia (9 pairs resolved). Status quo: Lyonnais and Provence stay Austrian by the treaty. Status quo: Oldenburg stays ours by the treaty — titled. → display-only
  - POPUP diplomatic_dialogue: Austria, peace #24 → accept
  -     ↳ refused: Austria's counter-terms could not be ratified: We already have Peace with Austria. A Peace treaty would be a …
  - POPUP diplomatic_dialogue: incoming_settlement_offer #22 → accept_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - POPUP diplomatic_dialogue: Denmark, non_aggression #21 → accept
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `Davout, move to Moravia` → ✗ Davout is fortified at Munich and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Murat, move to Carniola` → ✗ Cannot enter Carniola — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Bernadotte, move to Westphalia` → ✗ Cannot enter Westphalia — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 5 actions unused) Turn 12 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, fortify×2, unfortify×1
- LEDGER treasury 15672 · net +2424 · threat 48 · provinces 27 (+0) · ceiling 84528 · army 110393 · vassals Bavaria 80 · Holland 82 · Switzerland 72
  - NET income 3200 · trade 460 · admin 50 · tribute 443 · upkeep 848 · charges 481 · occupation 10 · admiralty 90 · laws 300
- DISPATCH: Sire — Marshal Lannes has been taken. Austria holds him prisoner.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Switzerland vs Britain + Austria + Russia + Hanover: settlement ratified.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Hesse has rebelled against France. It is war.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_vassal_courting, diplomatic_dp_regen, blockade_broken ×3, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG vassal_auto_join_war: Vassal Bavaria joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Hesse has broken free of France. War.
  - LOG ai_ai_proposal_refused: 11 approaches from Britain, Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 76 to 58.

## Turn 12 — Early March 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `Bernadotte, move to East Frisia` → ✗ Cannot enter East Frisia — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, move to Croatia` → ✗ Cannot enter Croatia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Davout, fortify` → ✗ Davout is already fortified at Munich (+11% defense).
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will conduct dril…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will conduct drill training instead.) → trust
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18089 · net +2325 · threat 48 · provinces 27 (+0) · ceiling 78614 · army 107733 · vassals Bavaria 84 · Holland 82 · Switzerland 72
  - NET income 3200 · trade 460 · admin 50 · tribute 448 · upkeep 816 · charges 617 · occupation 10 · admiralty 90 · laws 300
- DISPATCH: Sire — Hesse is no longer ours. They have rebelled, and it is war.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, sovereign_takes_field)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Britain, Russia and Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Holland and Switzerland rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria and Denmark rebuff Prussia (open borders agreement)

## Turn 13 — Late March 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `Soult, move to Hanover` → ✗ Cannot enter Hanover — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Deroy, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Deroy fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max…
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 1 action unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 20383 · net +2424 · threat 48 · provinces 27 (+0) · ceiling 78634 · army 105256 · vassals Bavaria 88 · Holland 82 · Switzerland 72
  - NET income 3200 · trade 460 · admin 50 · tribute 678 · upkeep 800 · charges 764 · occupation 10 · admiralty 90 · laws 300
- DISPATCH: Sire — Ney, Davout, Murat, Massena and Deroy have been 11 turns over what Munich can feed. 8,001 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is si…
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: 6 courts rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Britain (defensive alliance)

## Turn 14 — Early April 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Bavaria` → ✓ Invested in Bavaria: +10 loyalty (88 → 98). Cost: 1 DP + 200g. Cooldown: 3 turns.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Oldenburg. Defense bonus: +2% (grows +2% per turn, …
- CMD `Bernadotte, move to Flanders` → ✗ Bernadotte is already in Flanders.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Hesse settlement offer
- LEDGER treasury 22570 · net +2617 · threat 48 · provinces 27 (+0) · ceiling 80973 · army 102944 · vassals Bavaria 100 · Holland 82 · Switzerland 72
  - NET income 3200 · trade 460 · admin 50 · tribute 1020 · upkeep 792 · charges 921 · occupation 10 · admiralty 90 · laws 300
- DISPATCH: Sire — Ney, Davout, Murat, Massena and Deroy have been 12 turns over what Munich can feed. 7,449 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is si…
  - RAIL settlement_offer_arrival: Hesse has offered terms to settle Hesse vs France.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 15 — Late April 1806
  - MAILBOX #19 Hesse incoming_settlement_offer: Hesse — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #27 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #28 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Hesse (5 pairs resolved). → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Saxony` → ✗ Saxony is not a vassal.
- CMD `Bernadotte, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Bernadotte fortifies position at Flanders. Defense bonus: +7% (grows +3% per tu…
- CMD `Massena, drill` → ✓ Massena begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 26002 · net +3390 · threat 48 · provinces 27 (+0) · ceiling 308500 · army 100783 · vassals Bavaria 100 · Holland 80 · Switzerland 70
  - NET income 3200 · trade 472 · admin 50 · tribute 1026 · upkeep 760 · charges 288 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 5 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL settlement_summary: Settlement of Hesse vs France + Spain + Holland + Switzerland + Bavaria: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 9
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
  - MAILBOX #20 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #29 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (80 → 90); bond 5 → 25 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 5 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 29060 · net +3022 · threat 48 · provinces 27 (+0) · ceiling 280833 · army 98757 · vassals Bavaria 100 · Holland 89 · Switzerland 68
  - NET income 3200 · trade 472 · admin 50 · tribute 694 · upkeep 760 · charges 324 · occupation 10 · laws 300
- DISPATCH: Sire — Ney, Davout, Murat, Massena and Deroy have been 14 turns over what Munich can feed. 6,499 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is si…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — alliance is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)

## Turn 17 — Late May 1806
  - MAILBOX #21 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #30 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (68 → 78); bond 5 → 25 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Bavaria` → ✗ Bavaria's loyalty is already full (100/100) — the investment would buy nothing, so nothing is charged.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 5 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 31894 · net +2800 · threat 48 · provinces 27 (+0) · ceiling 265166 · army 96857 · vassals Bavaria 100 · Holland 88 · Switzerland 77
  - NET income 3200 · trade 472 · admin 50 · tribute 474 · upkeep 728 · charges 358 · occupation 10 · laws 300
- DISPATCH: Sire — Ney, Davout, Murat, Massena and Deroy have been 15 turns over what Munich can feed. 6,087 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is si…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 18 — Early June 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Saxony` → ✗ Saxony is not a vassal.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 5 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 34708 · net +2780 · threat 48 · provinces 27 (+0) · ceiling 266333 · army 95070 · vassals Bavaria 100 · Holland 87 · Switzerland 76
  - NET income 3200 · trade 472 · admin 50 · tribute 480 · upkeep 720 · charges 392 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 8 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 5 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 37451 · net +2710 · threat 48 · provinces 27 (+0) · ceiling 263250 · army 93386 · vassals Bavaria 100 · Holland 86 · Switzerland 75
  - NET income 3200 · trade 422 · admin 50 · tribute 485 · upkeep 712 · charges 425 · occupation 10 · laws 300
- DISPATCH: Sire — Ney, Davout, Murat, Massena and Deroy have been 17 turns over what Munich can feed. 5,371 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is si…
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 20 — Early July 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `rf1-q0-gev-a-staff_t20` → Game saved: rf1-q0-gev-a-staff_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 5 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 40187 · net +2703 · threat 46 · provinces 27 (+0) · ceiling 265416 · army 91799 · vassals Bavaria 100 · Holland 85 · Switzerland 74
  - NET income 3200 · trade 422 · admin 50 · tribute 487 · upkeep 688 · charges 458 · occupation 10 · laws 300
- DISPATCH: Sire — Ney, Davout, Murat, Massena and Deroy have been 18 turns over what Munich can feed. 5,058 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is si…
  - TURN EVENTS 3
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 5 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 42890 · net +2671 · threat 44 · provinces 27 (+0) · ceiling 265416 · army 90301 · vassals Bavaria 100 · Holland 84 · Switzerland 73
  - NET income 3200 · trade 422 · admin 50 · tribute 487 · upkeep 688 · charges 490 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 11 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 5 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 45577 · net +2655 · threat 42 · provinces 27 (+0) · ceiling 266750 · army 88863 · vassals Bavaria 100 · Holland 83 · Switzerland 72
  - NET income 3200 · trade 422 · admin 50 · tribute 487 · upkeep 672 · charges 522 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 12 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 5 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 48240 · net +2968 · threat 40 · provinces 27 (+0) · ceiling 295500 · army 87482 · vassals Bavaria 100 · Holland 82 · Switzerland 71
  - NET income 3200 · trade 422 · admin 50 · tribute 824 · upkeep 664 · charges 554 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 13 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 5 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 51224 · net +3173 · threat 38 · provinces 27 (+0) · ceiling 315583 · army 86157 · vassals Bavaria 100 · Holland 81 · Switzerland 70
  - NET income 3200 · trade 422 · admin 50 · tribute 1049 · upkeep 648 · charges 590 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 14 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 25 — Late September 1806
  - MAILBOX #22 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #31 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (81 → 91); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 5 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 54068 · net +2810 · threat 36 · provinces 27 (+0) · ceiling 288166 · army 84883 · vassals Bavaria 100 · Holland 91 · Switzerland 69
  - NET income 3200 · trade 422 · admin 50 · tribute 712 · upkeep 640 · charges 624 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 15 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
  - MAILBOX #23 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #32 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (69 → 79); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 5 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 56669 · net +2569 · threat 34 · provinces 27 (+0) · ceiling 270750 · army 83661 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 487 · upkeep 624 · charges 656 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 16 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 5 actions unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 59238 · net +2539 · threat 32 · provinces 27 (+0) · ceiling 270750 · army 82489 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 487 · upkeep 624 · charges 686 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 17 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 5 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 61785 · net +2516 · threat 30 · provinces 27 (+0) · ceiling 271416 · army 81364 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 487 · upkeep 616 · charges 717 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 18 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 5 actions unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 64309 · net +2494 · threat 28 · provinces 27 (+0) · ceiling 272083 · army 80283 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 487 · upkeep 608 · charges 747 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 19 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
  - saved `rf1-q0-gev-a-staff_t30` → Game saved: rf1-q0-gev-a-staff_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 5 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 66819 · net +2480 · threat 26 · provinces 27 (+0) · ceiling 273416 · army 79245 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 487 · upkeep 592 · charges 777 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 20 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 5 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 69299 · net +2450 · threat 24 · provinces 27 (+0) · ceiling 273416 · army 78250 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 487 · upkeep 592 · charges 807 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 21 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 5 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 71757 · net +2765 · threat 22 · provinces 27 (+0) · ceiling 302166 · army 77294 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 824 · upkeep 584 · charges 837 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 22 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 5 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 74522 · net +2957 · threat 20 · provinces 27 (+0) · ceiling 320916 · army 76376 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 1049 · upkeep 584 · charges 870 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 23 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 5 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 77503 · net +2945 · threat 18 · provinces 27 (+0) · ceiling 322916 · army 75495 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 1049 · upkeep 560 · charges 906 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 24 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 35 — Late February 1807
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 5 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 80456 · net +2918 · threat 16 · provinces 27 (+0) · ceiling 323583 · army 74648 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 1049 · upkeep 552 · charges 941 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 25 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 5 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 83382 · net +2891 · threat 14 · provinces 27 (+0) · ceiling 324250 · army 73836 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 1049 · upkeep 544 · charges 976 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 26 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 5 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 86273 · net +2856 · threat 12 · provinces 27 (+0) · ceiling 324250 · army 73057 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 1049 · upkeep 544 · charges 1011 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 27 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 5 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 89129 · net +2822 · threat 10 · provinces 27 (+0) · ceiling 324250 · army 72308 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 1049 · upkeep 544 · charges 1045 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 28 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 5 actions unused) Turn 40 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 91959 · net +2796 · threat 8 · provinces 27 (+0) · ceiling 324916 · army 71589 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 1049 · upkeep 536 · charges 1079 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 29 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: Russian-led alignment leads the current largest alignment at 39% of active European bloc power.

## Turn 40 — Early May 1807
  - saved `rf1-q0-gev-a-staff_t40` → Game saved: rf1-q0-gev-a-staff_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 5 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 94763 · net +2770 · threat 5 · provinces 27 (+0) · ceiling 325583 · army 70900 · vassals Bavaria 100 · Holland 91 · Switzerland 79
  - NET income 3200 · trade 422 · admin 50 · tribute 1049 · upkeep 528 · charges 1113 · occupation 10 · laws 300
- DISPATCH: Sire — the levy has stood open 30 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 37% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…

---
finished: **completed** · commands 144 · popups 69 · battles 11
