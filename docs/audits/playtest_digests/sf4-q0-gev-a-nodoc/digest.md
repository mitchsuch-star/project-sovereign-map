# Playtest digest — sf4-q0-gev-a-nodoc

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `e631f4bd4a79` (dirty) · content `c4151b82bd80` · driver `f7650c682a9c`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `declare war on Hanover` → ✓ Choose your war purpose against Hanover.
  - POPUP diplomatic_dialogue: war_purpose_selection #1 → 1
  - POPUP diplomatic_objection: diplomatic_declare_war, Hanover → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #2 → ally_entry_proceed_without
- CMD `vassalize Bavaria` → ✓ Sire, regarding the Vassalage proposal to Bavaria, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #3 → confirm
  - POPUP proposal_result: Talleyrand departs for the Bavaria court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2595, own corps) vs Mack (lost 12882) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✓ Davout notes the risks but prepares the attack. MUSTER — Davout (24,315; expect about 88,473 with the corps likely to arrive, up to 101,081 if all march) vs Mack (39,118…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1522, own corps) vs Mack (lost 12294) — Davout fought without Soult and Murat's support. The roads, or the will, proved insufficient. And Mack was taken on tha…
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Murat, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu…
  - ⚔ Archduke Charles (lost 4182) vs Massena (lost 6271) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
  - POPUP proposal_result: Bavaria was not entirely opposed, but could not agree to any terms. → display-only
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 2 · Denmark open borders · Hesse open borders
- LEDGER treasury 1532 · net +1532 · threat 97 · provinces 28 · ceiling 34735 · army 170524 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2044 · blockade 219 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is taken at Swabia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_war_declared: France has declared war on Hanover, with 2 allied courts poised to follow.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Bavaria with a response.
  - TURN EVENTS 3
- DIPLO +8 medium/low (diplomatic_proposal_sent, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

## Turn 2 — Early October 1805
  - LETTER Denmark: Open Borders Agreement → accept
  - LETTER Hesse: Open Borders Agreement → accept
- CMD `vassalize Saxony` → ✓ Sire, regarding the Vassalage proposal to Saxony, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #6 → confirm
  - POPUP proposal_result: Talleyrand departs for the Saxony court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `Soult, move to Brabant` → ✓ Soult moves from Lorraine to Brabant (900 lost to march)
- CMD `Bernadotte, move to Swabia` → ✓ Bernadotte moves from Franconia to Swabia (170 lost to march)
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles a…
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Tyrol instead.) → trust
  - ↳ MUSTER — Massena (35,729) vs Archduke Charles (large force) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 9931) vs Archduke Charles (lost 2272, own corps) — The terrain heavily favored Archduke Charles. Massena's men paid the price.
- CMD `Deroy, move to Munich` → ✗ Marshal Deroy commands for Bavaria, Sire — he does not answer to us. To move against him: 'attack Deroy' or 'pursue Deroy'; for word of him, ask 'where is Deroy'.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending!
  - ⚔ Archduke Charles (lost 2280) vs Deroy (lost 5846) — A standard affair. Nothing unusual to report.
  - verbs: attack×1
  - POPUP proposal_result: Saxony has rejected our Vassalage. → display-only
- LEDGER treasury 3120 · net +1959 · threat 95 · provinces 28 (+0) · ceiling 36421 · army 155626 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 425 · admin 50 · tribute 901 · upkeep 1586 · charges 65 · blockade 266 · admiralty 90
- DISPATCH: Sire — Massena was mauled at Tyrol: a quarter of his corps — 9,931 men — lost in a single action.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Saxony with a response.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 22 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
- CMD `vassalize Saxony` → ✗ Talleyrand advises patience, Sire. Saxony refused us; the court will not receive another envoy for 3 more turns.
- CMD `vassalize Hesse` → ✓ Sire, regarding the Vassalage proposal to Hesse, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #7 → confirm
  - POPUP proposal_result: Talleyrand departs for the Hesse court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `Soult, move to Flanders` → ✓ Soult moves from Brabant to Flanders
- CMD `Ney, move to Munich` → ✓ Ney moves from Swabia to Munich (375 lost to march)
- CMD `Davout, move to Munich` → ✓ Davout moves from Swabia to Munich (510 lost to march)
- CMD `Lannes, move to Munich` → ✓ Lannes moves from Swabia to Munich (294 lost to march)
- CMD `end turn` → ✓ Turn 3 ended. Turn 4 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria · Archduke Charles struggles in a costly engagement. Archduke Charles gains the advantage over Massena. Casualties: Archd…
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 2660) vs Massena (lost 3770, own corps) — Lannes's timely arrival aided Massena. Ney and Davout, however, were conspicuously absent.
  - verbs: attack×2, move×2, stance_change×1, wait×1
  - POPUP proposal_result: Hesse has rejected our Vassalage. → display-only
- LEDGER treasury 5036 · net +2020 · threat 93 · provinces 28 (+0) · ceiling 35263 · army 147583 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 425 · admin 50 · tribute 859 · upkeep 1346 · charges 202 · blockade 266 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Hesse with a response.
  - TURN EVENTS 3
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia, Naples and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 24 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
- CMD `vassalize Hesse` → ✗ Talleyrand advises patience, Sire. Hesse refused us; the court will not receive another envoy for 3 more turns.
- CMD `Soult, move to Oldenburg` → ✓ Soult moves from Flanders to Oldenburg. Oldenburg falls to France! (was Hanover) (809 lost to march)
  - POPUP capture_choice[capture]: Oldenburg, Soult → secure
- CMD `Ney, attack Archduke John` → ✓ MUSTER — Ney (17,941; expect about 46,761 with the corps likely to arrive, up to 65,000 if all march) vs Archduke John (18,265 men) at Tyrol — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 3499, own corps) vs Archduke John (lost 1553, own corps) — Reinforcements from Lannes and Massena bolstered Ney's position — though Davout never arrived, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Archduke John` → ✓ Davout notes the risks but prepares the attack. Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be …
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be told twice than bury them once."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (20,016; expect about 25,249 with the corps likely to arrive, up to 31,136 if all march) vs Archduke John (16,712 men) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Ney: will march to the sound of the guns — may make it from the mountains at Munich in time (about 47%); order 'Ney, support Davout' and it rises to about 99%
  WILL NOT — Lannes: has already marched this turn
  WILL NOT — Massena: is in no condition to fight
  Archduke John does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him.
  The band weighs more than the men: the ground favors the defender (+25%, mountains); Archduke John stands +42% on the defense (his stance, his character and his works).
  Tyrol feeds 20,000 — the whole muster standing there would lose ~718 men a turn to short supply.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Davout (20,016; expect about 25,249 with the corps likely to arrive, up to 31,136 if all march) vs Archduke John (16,712 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 5289) vs Archduke John (lost 825, own corps) — Not one corps reached Davout. Ney was expected; Davout fought the battle single-handed.
- CMD `Murat, move to Munich` → ✓ Murat moves from Franche-Comte to Munich (616 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, form_square×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 6391 · net +1783 · threat 83 · provinces 29 (+1) · ceiling 22367 · army 128062 · vassals Holland 95 · Switzerland 89
  - NET income 2615 · trade 437 · admin 50 · tribute 562 · upkeep 992 · charges 490 · occupation 35 · blockade 274 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Tyrol. He must reform before he fights again.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - TURN EVENTS 8
- DIPLO +4 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Naples and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 15 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `vassalize Hesse` → ✗ Talleyrand advises patience, Sire. Hesse refused us; the court will not receive another envoy for 2 more turns.
- CMD `Soult, attack Hanover` → ✓ ASSAULT — Soult storms the works at Hanover alone: 28,163 men, 32,387 in the assault's reckoning, against a garrison of 10,000. the garrison breaks below 5,000.
  - ↳ Soult assaults the Hanover garrison! Garrison: 10,000 -> 5,000 (-5,000). Soult loses 2,173 troops. Garrison holds — 5,000 defenders remain. It regains up to 2,000 a turn…
- CMD `Ney, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Davout, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Lannes, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 3 actions unused) Turn 6 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Provence unopposed! (730 lost to march) Captured: France → Austria · ArchdukeCharles marches from Provence into Lyonnais unopposed! (671 lost to march) Captured: France → Austria · Deroy marches from Swabia into Franconia unopposed! (77 lost to march — forward supply lines reduce losses) Captured: A… · Deroy faces a difficult fight. Brutal stalemate between Deroy and Archduke John. Heavy casualties on both sides: Deroy …
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (730 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Provence into Lyonnais unopposed! (671 lost to march) Captured: France → Austria
  - 🏴 Bavaria: Deroy marches from Swabia into Franconia unopposed! (77 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - ⚔ Deroy (lost 1693) vs Archduke John (lost 1360) — Neither Archduke John nor Deroy could claim the field. The armies remain locked.
  - verbs: attack×4, move×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 3540) vs Archduke John (lost 1563) — Murat stood alone, Sire. Ney, Davout and Lannes never came.
- ENVOYS WAITING 2 · Hanover armistice losing · Switzerland client petition
- LEDGER treasury 7750 · net +1433 · threat 81 · provinces 27 (-2) · ceiling 19691 · army 118750 · vassals Holland 92 · Switzerland 84
  - NET income 2385 · trade 437 · admin 50 · tribute 562 · upkeep 912 · charges 690 · occupation 35 · blockade 274 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Hanover has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 6 — Early December 1805
  - MAILBOX #3 Hanover incoming_proposal: Hanover — Armistice → activated
  - MAILBOX #4 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Hanover, armistice_losing #9 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #10 → grant the petition
  - POPUP diplomatic_dialogue: Hanover, armistice_losing #9 → accept
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond -15 → 5 (+0 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `vassalize Hesse` → ✗ Talleyrand advises patience, Sire. Hesse refused us; the court will not receive another envoy for 1 more turn.
- CMD `Soult, attack Hanover` → ✓ Choose your war purpose against Hanover. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #11 → 1
  -     ↳ refused: The armistice with Hanover holds for 5 more turns. We cannot declare war until it expires.
- CMD `Ney, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Davout, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Bernadotte, move to Rhineland` → ✓ Bernadotte moves from Swabia to Rhineland
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Lyonnais into Limousin unopposed! (619 lost to march) Captured: France → Austria · Deroy's forces advance steadily. Archduke John holds the line. Casualties: Deroy 1,765, Archduke John 970. Both armies …
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Limousin unopposed! (619 lost to march) Captured: France → Austria
  - ⚔ Deroy (lost 1765) vs Archduke John (lost 970) — The prepared defenses proved their worth. Deroy could not dislodge Archduke John.
  - verbs: attack×2, fortify×1, move×1, wait×1, recruit×1
- ENVOYS WAITING 3 · Prussia open borders · Portugal open borders · Holland client petition
- LEDGER treasury 8827 · net +926 · threat 78 · provinces 26 (-1) · ceiling 16342 · army 115411 · vassals Holland 91 · Switzerland 92
  - NET income 2325 · trade 437 · admin 50 · tribute 337 · upkeep 888 · charges 841 · contributions 110 · occupation 20 · blockade 274 · admiralty 90
- DISPATCH: Sire — Limousin has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL armistice_ratified: A truce with Hanover: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Britain (defensive alliance)

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #5 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #7 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #12 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #14 → grant the petition
  - POPUP diplomatic_dialogue: Prussia, open_borders #12 → accept
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond -15 → 5 (+0 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #14 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `vassalize Hesse` → ✗ Talleyrand advises patience, Sire. Hesse refused our Vassalage proposal; she will not hear it again for 2 more turns.
- CMD `Soult, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Ney, attack Vienna` → ✗ Ney cannot reach Vienna from Munich! Range: 1, Distance: 3
- CMD `Davout, attack Vienna` → ✗ Davout cannot reach Vienna from Munich! Range: 1, Distance: 3
- CMD `Lannes, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Limousin into Berry unopposed! (368 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Normandy garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 3,333 troops.… · ArchdukeCharles assaults the Normandy garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,851 troops in …
  - 🏴 Austria: ArchdukeCharles marches from Limousin into Berry unopposed! (368 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -92g, France -150g. Captured: France → Austria
  - verbs: attack×3, fortify×1, wait×1, recruit×1
- ENVOYS WAITING 1 · Saxony open borders
- LEDGER treasury 9123 · net +458 · threat 75 · provinces 24 (-2) · ceiling 12581 · army 112305 · vassals Holland 100 · Switzerland 90
  - NET income 2135 · trade 487 · admin 50 · upkeep 856 · charges 943 · occupation 20 · blockade 305 · admiralty 90
- DISPATCH: Sire — Berry has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Britain and Prussia rebuff Bavaria (open borders agreement)

## Turn 8 — Early January 1806
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Soult, move to Osnabruck` → ✗ Cannot enter Osnabruck — it is controlled by Hanover (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Ney, attack Vienna` → ✗ Ney cannot reach Vienna from Munich! Range: 1, Distance: 3
- CMD `Davout, attack Vienna` → ✗ Davout cannot reach Vienna from Munich! Range: 1, Distance: 3
- CMD `Lannes, attack Vienna` → ✗ Lannes cannot reach Vienna from Munich! Range: 1, Distance: 3
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 12 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore engages in solid combat. Moore gains the advantage over Castanos. Casualties: Moore's army 1,419, Castanos 3,010.… · Paget holds them at Normandy while allies attack from London! (+1 coordination) · ArchdukeCharles marches from Normandy into Artois unopposed! (170 lost to march) Captured: France → Austria · ArchdukeCharles marches from Artois into Champagne unopposed! (168 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Normandy into Artois unopposed! (170 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Artois into Champagne unopposed! (168 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles moves from Champagne to Burgundy. Burgundy falls to Austria!
  - 🏴 Austria: ArchdukeCharles moves from Burgundy to Savoy. Savoy falls to Austria!
  - ⚔ Moore (lost 1304, own corps) vs Castanos (lost 3010) — The walls were not enough. Moore broke through Castanos's prepared defenses.
  - ⚔ Paget (lost 201, own corps) vs Castanos (lost 5540) — The walls were not enough. Paget broke through Castanos's prepared defenses.
  - verbs: move×4, attack×4, unfortify×2, wait×1, recruit×1
- ENVOYS WAITING 1 · PapalStates open borders
- LEDGER treasury 9468 · net +145 · threat 72 · provinces 20 (-4) · ceiling 10532 · army 109411 · vassals Holland 100 · Switzerland 88
  - NET income 1865 · trade 512 · admin 50 · upkeep 840 · charges 1012 · occupation 20 · blockade 320 · admiralty 90
- DISPATCH: Sire — Artois has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing t…
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +9 medium/low (diplomatic_treaty_signed, diplomatic_we_threshold, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×3, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 7 courts rebuff Bavaria (open borders agreement)

## Turn 9 — Late January 1806
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Vienna` → ✗ Ney cannot reach Vienna from Munich! Range: 1, Distance: 3
- CMD `Davout, attack Vienna` → ✗ Davout cannot reach Vienna from Munich! Range: 1, Distance: 3
- CMD `Lannes, attack Vienna` → ✗ Lannes cannot reach Vienna from Munich! Range: 1, Distance: 3
- CMD `Bernadotte, move to Brabant` → ✓ Bernadotte moves from Rhineland to Brabant (154 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 10 actions, 6 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Moore executes a brilliant maneuver! Moore gains the advantage over Castanos. Casualties: Moore's army 159, Castanos 2,… · Paget attacks with overwhelming force. Paget decisively defeats Castanos! Castanos's army is destroyed. Paget's army su… · Moore marches from Anjou into Guyenne unopposed! (551 lost to march) Captured: France → Britain · Deroy engages in solid combat. Brutal stalemate between Deroy and Archduke John. Heavy casualties on both sides: Deroy …
  - 🏴 Britain: Both armies remain in the field. Moore advances into Maine. (600 lost to march) Maine has been captured by Britain!
  - 🏴 Britain: Paget's army suffered 74 casualties. Castanos's army is destroyed! Paget advances into Anjou. (39 lost to march) Anjou has been captured by Britain!
  - 🏴 Britain: Moore marches from Anjou into Guyenne unopposed! (551 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeJohn moves from Bohemia to Franconia. Franconia falls to Austria!
  - ⚔ Moore (lost 131, own corps) vs Castanos (lost 2523) — Even Castanos's fortifications could not hold, Sire. Moore overran the position.
  - ⚔ Paget (lost 12, own corps) vs Castanos (lost 2637) — The terrain heavily favored Paget. Castanos's men paid the price.
  - ⚔ Deroy (lost 1758) vs Archduke John (lost 1493) — Stalemate. Archduke John and Deroy glare at each other across the field.
  - ⚔ Deroy (lost 1421) vs Archduke John (lost 1332) — Neither Archduke John nor Deroy could claim the field. The armies remain locked.
  - ⚔ Deroy (lost 1263) vs Archduke John (lost 1232) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×6, move×3, unfortify×1
- LEDGER treasury 9494 · net -131 · threat 69 · provinces 17 (-3) · ceiling 8548 · army 106554 · vassals Holland 100 · Switzerland 86
  - NET income 1590 · trade 537 · admin 50 · upkeep 832 · charges 1040 · occupation 10 · blockade 336 · admiralty 90
- DISPATCH: Sire — Maine has fallen to Britain. Enemy colours fly over French homeland soil. Paget's corps of 3,984 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any g…
  - RAIL design_promoted: REVANCHE: Hanover will not forgive France the loss of Brunswick and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 11 courts rebuff Bavaria (open borders agreement)

## Turn 10 — Early February 1806
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #17 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `Ney, move to Vienna` → ✓ Ney: 'ArchdukeJohn bars the way!' Engaging!
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 369, own corps) vs Archduke John (lost 4629) — Lannes, Massena and Napoleon arrived to reinforce Ney, but Davout and Murat failed to reach the field in time. And Arch… — Berthier: the corps marched apart and arrived together.
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, move to Hungary` → ✓ Davout begins marching to Hungary (distance: 3). Moved to Franconia. Route: Franconia -> Bohemia -> Hungary.
- CMD `Murat, move to Bohemia` → ✓ Murat moves from Munich to Bohemia. Bohemia falls to France! (was Austria) (261 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Murat → secure
- CMD `Bernadotte, move to Flanders` → ✗ Not enough actions! Need 1, have 0.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `sf4-q0-gev-a-nodoc_t10` → Game saved: sf4-q0-gev-a-nodoc_t10
- CMD `end turn` → ✓ Turn 10 ended. Turn 11 begins!
- enemy phase: 8 actions, 4 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Guyenne into Gascony unopposed! (1,023 lost to march) Captured: France → Britain · Archduke Charles attacks with overwhelming force. Brutal stalemate between Archduke Charles and Murat. Heavy casualties… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Murat. Casualties: Archduke Cha… · Deroy faces a difficult fight. Archduke Charles holds the line. Casualties: Deroy 2,152, Archduke Charles 747. Both arm…
  - 🏴 Britain: Moore marches from Guyenne into Gascony unopposed! (1,023 lost to march) Captured: France → Britain
  - ⚔ Archduke Charles (lost 1709) vs Murat (lost 1572, own corps) — Ney and Davout arrived in time to steady Murat's position. The field was held, nothing further.
  - ⚔ Archduke Charles (lost 1045) vs Murat (lost 2081) — The margin was slim. Training and preparation would serve Murat well.
  - ⚔ Deroy (lost 2152) vs Archduke Charles (lost 747) — An exemplary engagement by Archduke Charles. The outcome was never in doubt.
  - verbs: attack×4, move×2, fortify×1, wait×1
- ORDER Davout [active]: Davout is marching to Hungary (0 turns remaining).
- ORDER Ney [active]: Ney is marching to Vienna (0 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #21 → confirm_settlement
  - POPUP nation_proclamation: Normandy → display-only
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Hanover + Russia (10 pairs resolved). Status quo: Anjou, Gascony, Guyenne and Maine stay British by the treaty. Status quo: Bohemia and Franconia stay ours by the treaty — titled. Status quo: Artois, Berry, Burgundy, Champagne, Limousin, Lyonnais, Provence and Savoy stay Austrian by the treaty. Status quo: Leon stays British by the treaty. Status quo: Oldenburg stays ours by the treaty — titled. Status quo: Brunswick, Hanover and Osnabruck stay Prussian by the treaty. → display-only
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 4950 · net +1092 · threat 73 · provinces 18 (+1) · ceiling 30928 · army 98062 · vassals Holland 99 · Switzerland 83
  - NET income 1512 · trade 585 · admin 50 · upkeep 752 · charges 123 · occupation 180
- DISPATCH: Sire — Gascony has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3688 gold.
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Hanover has collapsed. War resumes!
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: Hanover rebuffs Britain and Austria (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 42% of active European bloc power.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 73 to 56.
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 1 more — France is not forgiven
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Prussia (defensive alliance)

## Turn 11 — Late February 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `Davout, move to Moravia` → ✓ Davout begins marching to Moravia (distance: 2). Moved to Dresden. Route: Dresden -> Moravia. Davout's march to Paris is set aside.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Murat, move to Carniola` → ✗ Not enough actions! Need 1, have 0.
- CMD `Bernadotte, move to Westphalia` → ✗ Not enough actions! Need 1, have 0.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 11 ended. Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Bernadotte [continues]: Bernadotte marches to Orleanais. 3 regions to Paris.
- ORDER Davout [active]: Davout is marching to Moravia (2 turns remaining).
- ORDER Lannes [continues]: Lannes marches to Swabia. 5 regions to Paris.
- ORDER Massena [continues]: Massena marches to Swabia. 5 regions to Paris.
- ORDER Murat [continues]: Murat marches to Milan. 4 regions to Paris.
- ORDER Napoleon [continues]: Napoleon marches to Swabia. 5 regions to Paris.
- ORDER Soult [continues]: Soult marches to Westphalia. 2 regions to Paris.
- LEDGER treasury 6059 · net +1062 · threat 54 · provinces 18 (+0) · ceiling 31333 · army 95985 · vassals Holland 97 · Switzerland 81
  - NET income 1513 · trade 585 · admin 50 · upkeep 736 · charges 170 · occupation 180
- DISPATCH: Sire — Anjou, Artois and Berry and 10 more lie in enemy hands. Britain, Austria and Duchy of Normandy hold them.
  - RAIL nation_created: By the fortune of arms and the pen at the table — Duchy of Normandy is erected upon the map, a client of Britain.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Hanover + Russia: Gold indemnity: 3688 gold from France to Britain.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +10 medium/low (balance_of_europe_shifted, diplomatic_coalition_dissolved, status_quo_titled ×2, law_enacted_abroad, diplomatic_dp_regen, blockade_broken ×3, agenda_shift)
  - LOG ai_ai_proposal_refused: 24 approaches from Britain, Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Sardinia are rebuffed (design ask)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: Hanover rebuffs Britain, Russia and Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)

## Turn 12 — Early March 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `Bernadotte, move to East Frisia` → ✓ Bernadotte begins marching to East Frisia (distance: 3). Moved to Flanders. Route: Flanders -> Oldenburg -> East Frisia. Bernadotte's march to Paris is set aside.
- CMD `Murat, move to Croatia` → ✓ Murat begins marching to Croatia (distance: 3). Moved to Tyrol. Route: Tyrol -> Carniola -> Croatia. Murat's march to Paris is set aside.
- CMD `Davout, fortify` → ✗ Not enough actions! Need 1, have 0.
- CMD `Lannes, fortify` → ✗ Not enough actions! Need 1, have 0.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 12 ended. Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Bernadotte [active]: Bernadotte is marching to East Frisia (3 turns remaining).
- ORDER Davout [completed]: Davout arrives at Moravia. Davout: "It is done. I took the liberty of posting pickets."
- ORDER Lannes [continues]: Lannes marches to Lorraine. 4 regions to Paris.
- ORDER Massena [continues]: Massena marches to Lorraine. 4 regions to Paris.
- ORDER Murat [active]: Murat is marching to Croatia (2 turns remaining).
- ORDER Napoleon [continues]: Napoleon marches to Lorraine. 4 regions to Paris.
- ORDER Soult [continues]: Soult marches to Artois. 1 region to Paris.
- LEDGER treasury 7236 · net +1200 · threat 52 · provinces 18 (+0) · ceiling 35785 · army 84947 · vassals Holland 95 · Switzerland 79
  - NET income 1582 · trade 585 · admin 50 · upkeep 648 · charges 219 · occupation 150
- DISPATCH: Sire — Marshal Davout's corps was interned at Moravia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, coercive_demand)
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `Soult, move to Hanover` → ✓ Soult begins marching to Hanover (distance: 3). Moved to Westphalia. Route: Westphalia -> Oldenburg -> Hanover. Soult's march to Paris is set aside.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Deroy, fortify` → ✗ Marshal Deroy commands for Bavaria, Sire — he does not answer to us. To move against him: 'attack Deroy' or 'pursue Deroy'; for word of him, ask 'where is Deroy'.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 1 action unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Bernadotte [continues]: Bernadotte marches to Oldenburg. 1 region to East Frisia.
- ORDER Lannes [continues]: Lannes marches to Orleanais. 3 regions to Paris.
- ORDER Massena [continues]: Massena marches to Orleanais. 3 regions to Paris.
- ORDER Napoleon [continues]: Napoleon marches to Orleanais. 3 regions to Paris.
- ORDER Soult [active]: Soult is marching to Hanover (3 turns remaining).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
- LEDGER treasury 8447 · net +1385 · threat 50 · provinces 18 (+0) · ceiling 41404 · army 83716 · vassals Holland 93 · Switzerland 77
  - NET income 1585 · trade 585 · admin 50 · tribute 225 · upkeep 640 · charges 270 · occupation 150
- DISPATCH: Sire — 3 turns now with Anjou, Artois and Berry and 10 more in enemy hands. The country counts every one of them.
  - RAIL diplomatic_offensive_cascade: Britain has joined Russia's war against Sweden, honoring their alliance.
  - RAIL diplomatic_offensive_cascade: Austria has joined Russia's war against Sweden, honoring their alliance.
  - RAIL diplomatic_war_declared: Russia has declared war on Sweden, shattering the Open Borders Agreement, with 2 allied courts poised to follow.
  - RAIL broken_bargain: The compact with Sweden lies torn — Britain is named the breaker in every chancery of Europe.
  - TURN EVENTS 8
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_dp_regen, blockade_begins, agenda_shift, diplomatic_relation_shift)
  - LOG diplomatic_treaty_broken: Russia has broken the Open Borders Agreement with Sweden by declaring war.
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Britain tears up its sponsorship with Sweden

## Turn 14 — Early April 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Bavaria` → ✗ Bavaria is not a vassal.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Westphalia. Defense bonus: +2% (grows +2% per turn,…
- CMD `Bernadotte, move to Flanders` → ✓ Bernadotte moves from Oldenburg to Flanders Bernadotte's march to East Frisia is set aside.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [continues]: Lannes marches to Burgundy. 2 regions to Paris.
- ORDER Massena [continues]: Massena marches to Burgundy. 2 regions to Paris.
- ORDER Napoleon [continues]: Napoleon marches to Burgundy. 2 regions to Paris.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 9851 · net +1754 · threat 48 · provinces 18 (+0) · ceiling 51595 · army 73028 · vassals Holland 91 · Switzerland 75
  - NET income 1588 · trade 585 · admin 50 · tribute 562 · upkeep 552 · charges 329 · occupation 150
- DISPATCH: Sire — Marshal Ney's corps was interned at Franconia by Bavaria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_ai_proposal_refused: 16 approaches from Britain and Austria are rebuffed (defensive alliance)

## Turn 15 — Late April 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #22 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (75 → 85); bond 5 → 25 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Saxony` → ✗ Saxony is not a vassal.
- CMD `Bernadotte, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Bernadotte fortifies position at Flanders. Defense bonus: +7% (grows +3% per tu…
- CMD `Massena, drill` → ✓ Massena begins intensive drill exercises at Burgundy. Troops will be locked in training next turn, bonus ready turn 17. Massena's march to Paris is set aside.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 1 action unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2
- ORDER Lannes [continues]: Lannes marches to Limousin. 1 region to Paris.
- ORDER Napoleon [continues]: Napoleon marches to Limousin. 1 region to Paris.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 11440 · net +1586 · threat 46 · provinces 18 (+0) · ceiling 49190 · army 63384 · vassals Holland 89 · Switzerland 84
  - NET income 1628 · trade 585 · admin 50 · tribute 337 · upkeep 488 · charges 396 · occupation 130
- DISPATCH: Sire — Marshal Murat's corps was interned at Tyrol by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 10
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 43% of active European bloc power.

## Turn 16 — Early May 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #23 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 5 → 25 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [completed]: Lannes arrives at Paris. Lannes: "It is done. Point me at something that shoots back, Sire."
- ORDER Napoleon [completed]: Napoleon arrives at Paris.
- LEDGER treasury 12760 · net +1265 · threat 44 · provinces 18 (+0) · ceiling 42857 · army 63184 · vassals Holland 98 · Switzerland 83
  - NET income 1669 · trade 585 · admin 50 · upkeep 488 · charges 451 · occupation 100
- DISPATCH: Sire — Bernadotte, Massena and Soult are no nearer home, and the safe passage runs out in 0 turns. After that their corps will be interned where they stand.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Britain and Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 17 — Late May 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Bavaria` → ✗ Bavaria is not a vassal.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 14030 · net +1336 · threat 42 · provinces 18 (+0) · ceiling 45833 · army 47717 · vassals Holland 97 · Switzerland 82
  - NET income 1674 · trade 585 · admin 50 · upkeep 368 · charges 505 · occupation 100
- DISPATCH: Sire — Marshal Bernadotte's corps was interned at Flanders by Holland — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 2
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Britain (defensive alliance)

## Turn 18 — Early June 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Saxony` → ✗ Saxony is not a vassal.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15379 · net +1557 · threat 40 · provinces 18 (+0) · ceiling 52428 · army 12662 · vassals Holland 96 · Switzerland 81
  - NET income 1679 · trade 585 · admin 50 · upkeep 96 · charges 561 · occupation 100
- DISPATCH: Sire — Marshal Soult's corps was interned at Westphalia by Hanover — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16903 · net +1460 · threat 38 · provinces 18 (+0) · ceiling 51642 · army 12662 · vassals Holland 95 · Switzerland 80
  - NET income 1684 · trade 547 · admin 50 · upkeep 96 · charges 625 · occupation 100
- DISPATCH: Sire — Marshal Massena's corps was interned at Burgundy by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Bavaria (open borders agreement)

## Turn 20 — Early July 1806
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `sf4-q0-gev-a-nodoc_t20` → Game saved: sf4-q0-gev-a-nodoc_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18368 · net +1403 · threat 35 · provinces 18 (+0) · ceiling 51761 · army 12662 · vassals Holland 94 · Switzerland 79
  - NET income 1689 · trade 547 · admin 50 · upkeep 96 · charges 687 · occupation 100
- DISPATCH: Sire — the levy has stood open 6 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 20381 · net +1989 · threat 32 · provinces 18 (+0) · ceiling 186083 · army 12662 · vassals Holland 93 · Switzerland 78
  - NET income 1778 · trade 547 · admin 50 · upkeep 96 · charges 220 · occupation 70
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 11 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22377 · net +2197 · threat 29 · provinces 18 (+0) · ceiling 205416 · army 12662 · vassals Holland 92 · Switzerland 77
  - NET income 1785 · trade 547 · admin 50 · tribute 225 · upkeep 96 · charges 244 · occupation 70
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 12 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 24581 · net +2515 · threat 26 · provinces 18 (+0) · ceiling 234083 · army 12662 · vassals Holland 91 · Switzerland 76
  - NET income 1792 · trade 547 · admin 50 · tribute 562 · upkeep 96 · charges 270 · occupation 70
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 13 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Britain and Bavaria rebuff Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 24 — Early September 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #24 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (76 → 86); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 26878 · net +2269 · threat 23 · provinces 18 (+0) · ceiling 215916 · army 12662 · vassals Holland 90 · Switzerland 86
  - NET income 1799 · trade 547 · admin 50 · tribute 337 · upkeep 96 · charges 298 · occupation 70
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 14 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Bavaria (open borders agreement)

## Turn 25 — Late September 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #25 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (90 → 100); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 28817 · net +1916 · threat 20 · provinces 18 (+0) · ceiling 188416 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1806 · trade 547 · admin 50 · upkeep 96 · charges 321 · occupation 70
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 15 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Papal States, Sardinia and Holland rebuff Bavaria (open borders agreement)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 30807 · net +1966 · threat 17 · provinces 18 (+0) · ceiling 194583 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1860 · trade 547 · admin 50 · upkeep 96 · charges 345 · occupation 50
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 16 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 32781 · net +1950 · threat 14 · provinces 18 (+0) · ceiling 195250 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1868 · trade 547 · admin 50 · upkeep 96 · charges 369 · occupation 50
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 17 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 34739 · net +1935 · threat 11 · provinces 18 (+0) · ceiling 195916 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1876 · trade 547 · admin 50 · upkeep 96 · charges 392 · occupation 50
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 18 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 36678 · net +1915 · threat 8 · provinces 18 (+0) · ceiling 196250 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1880 · trade 547 · admin 50 · upkeep 96 · charges 416 · occupation 50
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 19 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 30 — Early December 1806
  - saved `sf4-q0-gev-a-nodoc_t30` → Game saved: sf4-q0-gev-a-nodoc_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 38593 · net +1892 · threat 5 · provinces 18 (+0) · ceiling 196250 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1880 · trade 547 · admin 50 · upkeep 96 · charges 439 · occupation 50
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 20 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 40485 · net +2095 · threat 2 · provinces 18 (+0) · ceiling 215000 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1880 · trade 547 · admin 50 · tribute 225 · upkeep 96 · charges 461 · occupation 50
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 21 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 42580 · net +2407 · threat 0 · provinces 18 (+0) · ceiling 243083 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1880 · trade 547 · admin 50 · tribute 562 · upkeep 96 · charges 486 · occupation 50
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 22 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Russia the loss of Uleaborg and 1 more province. A new design hardens in their court.
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 44987 · net +2378 · threat 0 · provinces 18 (+0) · ceiling 243083 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1880 · trade 547 · admin 50 · tribute 562 · upkeep 96 · charges 515 · occupation 50
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 23 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Sweden swears to retake Uleaborg and 1 more — Russia is not forgiven

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Russia broker peace
- LEDGER treasury 47365 · net +2349 · threat 0 · provinces 18 (+0) · ceiling 243083 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1880 · trade 547 · admin 50 · tribute 562 · upkeep 96 · charges 544 · occupation 50
- DISPATCH: Sire — the enemy has held Anjou, Artois and Berry and 10 more 24 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 35 — Late February 1807
  - MAILBOX #15 Russia incoming_proposal: Russia — Brokered Peace → activated
  - POPUP diplomatic_dialogue: Russia, broker_peace #26 → accept
  - POPUP proposal_result: Peace concluded between Russia and Sweden without France. A white peace; both courts are free to look elsewhere. → display-only
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 49714 · net +2321 · threat 0 · provinces 18 (+0) · ceiling 243083 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1880 · trade 547 · admin 50 · tribute 562 · upkeep 96 · charges 572 · occupation 50
- DISPATCH: Sire — Austria moves toward war with Bavaria. The design is open; the timing is not.
  - RAIL third_party_peace: THE CONGRESS: Russia and Sweden have made their peace without France. A white peace; both courts are free to look elsewhere.
  - RAIL crisis_brewing: THE BREWING CRISIS: Austria will move on Bavaria. You may compensate (1,248g — you can afford it); guarantee Bavaria (1 DP — 7 in hand); or let the w…
- COURTS: The court of Russia eases over The Gulf and the Straits — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Revanche — alliance is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, blockade_broken)
  - LOG ai_ai_proposal_refused: Britain and Bavaria rebuff Sweden (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 36 — Early March 1807
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 52035 · net +2293 · threat 0 · provinces 18 (+0) · ceiling 243083 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1880 · trade 547 · admin 50 · tribute 562 · upkeep 96 · charges 600 · occupation 50
- DISPATCH: Sire — Austria moves toward war with Bavaria. The design is open; the timing is not.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, coercive_demand)
  - LOG third_party_peace: THE CONGRESS: Russia and Sweden make peace without France

## Turn 37 — Late March 1807
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 53225 · net +988 · threat 0 · provinces 18 (+0) · ceiling 81289 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1880 · trade 535 · admin 50 · tribute 562 · upkeep 96 · charges 1803 · occupation 50 · admiralty 90
- DISPATCH: Sire — the establishment stands 92,338 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL diplomatic_alliance_cascade: France enters the war against Austria via its alliance with Bavaria.
  - RAIL diplomatic_war_declared: Austria has declared war on Bavaria, shattering the Peace Treaty, with 1 allied court poised to follow.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: The court of Sweden hardens over Revanche — prepared now to go as far as service to the strong.
- DIPLO +4 medium/low (diplomatic_dp_regen, witness_strike_recorded, diplomatic_treaty_broken, diplomatic_relation_shift)
  - LOG diplomatic_treaty_broken: France was forced to break the Peace Treaty with Austria (cascade).
  - LOG defensive_cascade: Defensive cascade: France joins war via Bavaria

## Turn 38 — Early April 1807
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Vienna into Bohemia unopposed! (815 lost to march — forward supply lines reduce losses) Ca… · Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charl…
  - 🏴 Austria: ArchdukeCharles marches from Vienna into Bohemia unopposed! (815 lost to march — forward supply lines reduce losses) Captured: France → Austria
  - ⚔ Archduke Charles (lost 1602) vs Deroy (lost 4982) — A grievous defeat for Deroy, Sire. The losses are severe.
  - verbs: attack×2
- LEDGER treasury 50760 · net -2386 · threat 0 · provinces 17 (-1) · ceiling 26502 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1644 · trade 535 · admin 50 · tribute 562 · upkeep 96 · charges 4797 · contributions 164 · occupation 30 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with Bavaria by declaring war.
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Sardinia are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Sardinia are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Sardinia are rebuffed (design ask)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: 15 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Sardinia are rebuffed (design ask)

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! Captured: France → Austria · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Cha… · ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,782 troops. G…
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! Captured: France → Austria
  - ⚔ Archduke Charles (lost 1755) vs Deroy (lost 9447) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×3, grant_dotation×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 49806 · net -1041 · threat 0 · provinces 16 (-1) · ceiling 35254 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1480 · trade 485 · admin 50 · tribute 562 · upkeep 96 · charges 3422 · occupation 10 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
- DIPLO +4 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Bavaria–France (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 40 — Early May 1807
  - MAILBOX #16 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #27 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
  - saved `sf4-q0-gev-a-nodoc_t40` → Game saved: sf4-q0-gev-a-nodoc_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charl…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,326 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 457) vs Deroy (lost 9747) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×1, fortify×1
- LEDGER treasury 44193 · net +1977 · threat 0 · provinces 16 (+0) · ceiling 208916 · army 12662 · vassals Holland 100 · Switzerland 86
  - NET income 1480 · trade 497 · admin 50 · tribute 562 · upkeep 96 · charges 506 · occupation 10
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL third_party_peace: THE CONGRESS: Bavaria and Austria have made their peace without France. Bavaria pays 4,356 gold. Austria is now free to look elsewhere.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)

---
finished: **completed** · commands 139 · popups 60 · battles 25
