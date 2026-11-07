# Playtest digest — rev1106-end-pressburg

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 28 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - loaded save `fixture_ge3_pressburg.json` → Loaded: GE-3 staged — after Pressburg and Tilsit (turn 28, 55 titled)

## Turn 28 — Early November 1806
- CMD `summon the congress` → ✓ The Emperor summons the powers of Europe to Paris. The Congress sits for 8 turns, to the end of turn 36. Britain SHUT OUT; Russia RECOGNIZES; Austria RECOGNIZES; Prussia…
  - POPUP diplomatic_dialogue: Bavaria, client_petition #1 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to Bavaria. Loyalty +10 (60 → 70); bond 60 → 60 (+3 a turn). Cost: 1 DP. Our net falls by 8g a turn — 150g of income forfeited, 37g of occupation relieved, 113g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- CMD `offer Prussia 1200 gold for recognition` → ✗ Prussia already recognizes the order (62 of 50) — its signature is taken at this end turn; no gold is needed.
  - POPUP diplomatic_dialogue: Hesse, client_petition #2 → grant the petition
  - POPUP proposal_result: Brunswick is ceded to Hesse. Loyalty +10 (60 → 70); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 85g a turn — 0g of income forfeited, 97g of occupation relieved, 0g returned as tribute at today's 75% rate, the force limit falls 2,500 (+12g surcharge). → display-only
- CMD `invest in saxony` → ✓ Invest in Saxony: 200 gold and 1 diplomatic point. Her loyalty rises +10 (85 → 95), and Saxony cannot be invested in again for 3 turns. The treasury holds 8,000 gold and…
  - POPUP clarification: The Cabinet, Invest in Saxony: 200 gold and 1 diplomatic point. Her loyalty rises +10 (85 → 95), and Saxony cannot be invested in again for 3 turns. The treasury holds 8,000 gold and would hold 7,800 after. Invest? (yes / no) → 1 (first option: Invest)
  - POPUP diplomatic_dialogue: Holland, client_petition #3 → (left standing — disabled: Grant the petition)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Holland, client_petition #3 → (left standing — disabled: Grant the petition)
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: garrison×1, wait×1
- LAPSED Holland client petition · Saxony client petition · Switzerland client petition
- ENVOYS WAITING 3 · Denmark open borders · Britain settlement offer · The Secretariat moment letter
- LEDGER treasury 8971 · net +994 · threat 53 · provinces 40 · ceiling 15324 · army 189000 · vassals Bavaria 71 · Hesse 69 · Holland 89 · Kingdom of Italy 100 · Saxony 81 · Switzerland 87
  - NET income 3250 · trade 350 · admin 50 · tribute 2052 · upkeep 2510 · charges 1090 · occupation 799 · blockade 219 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 1 of 8 · 55 titled, 45 needed · Britain SHUT OUT · Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Sire — THE EMPEROR SUMMONS THE POWERS TO PARIS. The Congress sits 8 turns, to the end of turn 36; every great power must sign, be shut out, or be gone. No court refuses today.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL +2 more
  - TURN EVENTS 7
- DIPLO +11 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent, cs_tier_shift, blockade_begins ×6)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG design_promoted: REVANCHE: Austria swears to retake Carniola and 2 more — France is not forgiven
  - LOG moment: The Remounts — an affair of state is laid before the Emperor
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 100 to 61; Britain remains at war with us.
  - LOG balance_of_europe_shifted: French System leads the current largest alignment at 50% of active European bloc power. Spain is the decisive non-France slice of the bloc; letting t…
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG nation_eliminated: Hanover has been eliminated from the war.
  - LOG nation_eliminated: Naples has been eliminated from the war.
  - LOG nation_eliminated: Portugal has been eliminated from the war.

## Turn 29 — Late November 1806
  - LETTER Denmark: Open Borders Agreement → accept
  - MAILBOX #7 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #8 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #9 → reject_ai_proposal
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #10 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with Britain — the table with Britain (3 pairs resolved). → display-only
  - POPUP diplomatic_dialogue: moment_letter #9 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (2 turns remaining).
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 10601 · net +1418 · threat 56 · provinces 40 (+0) · ceiling 21507 · army 189000 · vassals Bavaria 72 · Hesse 68 · Holland 86 · Kingdom of Italy 100 · Saxony 77 · Switzerland 84
  - NET income 3250 · trade 400 · admin 50 · tribute 2145 · upkeep 2510 · charges 1118 · occupation 799
- CONGRESS THE CONGRESS SITS — turn 2 of 8 · 55 titled, 45 needed · Britain, Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Sire — peace with Britain is signed. A white peace — the map stands as it was.
  - RAIL settlement_summary: Settlement of the War with Britain — the table with Britain: a white peace.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Naples–Tripoli crossing stands open to our armies.
  - TURN EVENTS 4
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: And Sweden, Austria and Sardinia stir at their own designs.
- DIPLO +8 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, cs_tier_shift, blockade_broken ×3)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG moment: The Remounts — the Emperor answers: Let the depots wait

## Turn 30 — Early December 1806
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (1 turns remaining).
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 12019 · net +1234 · threat 59 · provinces 40 (+0) · ceiling 21507 · army 189000 · vassals Bavaria 73 · Hesse 67 · Holland 83 · Kingdom of Italy 100 · Saxony 73 · Switzerland 81
  - NET income 3250 · trade 400 · admin 50 · tribute 2145 · upkeep 2510 · charges 1302 · occupation 799
- CONGRESS THE CONGRESS SITS — turn 3 of 8 · 55 titled, 45 needed · Britain, Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Sire — St Petersburg now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design …
  - RAIL agenda_violation: Prussia seethes: Denmark's columns cross Westphalia in defiance of its declared neutrality.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `invest in saxony` → ✓ Invest in Saxony: 200 gold and 1 diplomatic point. Her loyalty rises +10 (73 → 83), and Saxony cannot be invested in again for 3 turns. The treasury holds 12,019 gold an…
  - POPUP clarification: The Cabinet, Invest in Saxony: 200 gold and 1 diplomatic point. Her loyalty rises +10 (73 → 83), and Saxony cannot be invested in again for 3 turns. The treasury holds 12,019 gold and would hold 11,819 after. Invest? (yes / no) → 1 (first option: Invest)
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- SPENT 200g on this turn's orders
- enemy phase: 4 actions, 0 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, naval_expedition×1, wait×1, recruit×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 13079 · net +1096 · threat 62 · provinces 40 (+0) · ceiling 21507 · army 189000 · vassals Bavaria 74 · Hesse 66 · Holland 80 · Kingdom of Italy 100 · Saxony 79 · Switzerland 78
  - NET income 3250 · trade 400 · admin 50 · tribute 2145 · upkeep 2510 · charges 1440 · occupation 799
- CONGRESS THE CONGRESS SITS — turn 4 of 8 · 55 titled, 45 needed · Britain, Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Sire — Paget has put 5,000 men ashore at Copenhagen.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Copenhagen.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Russia and Sweden rebuff Britain (armistice)
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 32 — Early January 1807
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (2 turns remaining).
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 2 · Ottoman open borders · PapalStates open borders
- LEDGER treasury 14200 · net +975 · threat 65 · provinces 40 (+0) · ceiling 21700 · army 189000 · vassals Bavaria 75 · Hesse 65 · Holland 77 · Kingdom of Italy 100 · Saxony 75 · Switzerland 75
  - NET income 3250 · trade 425 · admin 50 · tribute 2145 · upkeep 2510 · charges 1586 · occupation 799
- CONGRESS THE CONGRESS SITS — turn 5 of 8 · 55 titled, 45 needed · Britain, Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +8 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, diplomatic_coalition_brewing, diplomatic_ai_ai_treaty ×2, blockade_broken ×2)
  - LOG coalition_brewing_started: Coalition brewing — the Ottoman Empire, Sweden and Sardinia alarmed (threat: 65)
  - LOG diplomatic_ai_ai_treaty: Britain and Russia sign an Armistice
  - LOG diplomatic_ai_ai_treaty: Britain and Sweden sign an Armistice

## Turn 33 — Late January 1807
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (1 turns remaining).
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 16862 · net +2126 · threat 68 · provinces 40 (+0) · ceiling 38120 · army 189000 · vassals Bavaria 76 · Hesse 64 · Holland 74 · Kingdom of Italy 100 · Saxony 71 · Switzerland 72
  - NET income 3975 · trade 475 · admin 50 · tribute 2201 · upkeep 2510 · charges 1486 · occupation 579
- CONGRESS THE CONGRESS SITS — turn 6 of 8 · 55 titled, 45 needed · Britain, Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Sire — London now pays St Petersburg 200 gold a turn against us. The coalition has its paymaster; it lacks only its armies.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG moment: The Magazines — an affair of state is laid before the Emperor

## Turn 34 — Early February 1807
  - MAILBOX #12 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #15 → reject_ai_proposal
- CMD `invest in saxony` → ✓ Invest in Saxony: 200 gold and 1 diplomatic point. Her loyalty rises +10 (71 → 81), and Saxony cannot be invested in again for 3 turns. The treasury holds 16,862 gold an…
  - POPUP clarification: The Cabinet, Invest in Saxony: 200 gold and 1 diplomatic point. Her loyalty rises +10 (71 → 81), and Saxony cannot be invested in again for 3 turns. The treasury holds 16,862 gold and would hold 16,662 after. Invest? (yes / no) → 1 (first option: Invest)
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 18808 · net +1932 · threat 71 · provinces 40 (+0) · ceiling 38120 · army 189000 · vassals Bavaria 77 · Hesse 63 · Holland 71 · Kingdom of Italy 100 · Saxony 77 · Switzerland 69
  - NET income 3975 · trade 475 · admin 50 · tribute 2201 · upkeep 2510 · charges 1680 · occupation 579
- CONGRESS THE CONGRESS SITS — turn 7 of 8 · 55 titled, 45 needed · Britain, Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Sire — London now pays Sweden 300 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design costs 1…
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Stockholm.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Magazines — the Emperor answers: Let the army forage

## Turn 35 — Late February 1807
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (2 turns remaining).
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Bavaria client petition
- LEDGER treasury 20740 · net +1738 · threat 73 · provinces 40 (+0) · ceiling 38120 · army 189000 · vassals Bavaria 78 · Hesse 62 · Holland 68 · Kingdom of Italy 100 · Saxony 73 · Switzerland 66
  - NET income 3975 · trade 475 · admin 50 · tribute 2201 · upkeep 2510 · charges 1874 · occupation 579
- CONGRESS THE CONGRESS SITS — turn 8 of 8 · 55 titled, 45 needed · Britain, Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Sire — Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 36 — Early March 1807
  - MAILBOX #13 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #17 → grant the petition
  - POPUP proposal_result: Carniola is ceded to Bavaria. Loyalty +10 (78 → 88); bond 60 → 60 (+3 a turn). Cost: 1 DP. Our net falls by 8g a turn — 150g of income forfeited, 37g of occupation relieved, 113g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (1 turns remaining).
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - ENDING — THE IMPERIAL PEACE: Europe accepts the order of the French Empire. [THE ASCENDANT EMPIRE]
  -     ↳ Early March 1807 (turn 36) · register `imperial_peace` · marked — the campaign continues
  -     ↳ THE VERDICT — THE ASCENDANT EMPIRE: The Empire stands larger and surer than it began. / The great powers have signed the order at Paris. / History will call it a rising star — not yet fixed in the heavens.
  -     ↳ The Verdict of History: an empire ascendant.
  -     ↳ THE RECORD — battles 0 (0 won, 0 lost) · men lost 0, inflicted 0 · provinces taken 11, lost 0 · marshals fallen 0, taken 0 · coalitions faced 1 · peaces signed 1
  -     ↳ THE CONGRESS (congress) — Britain SIGNED · Russia SIGNED · Austria SIGNED · Prussia SIGNED · 55 of 45 titled
  -     ↳ THE SITTING — t29✓ t30✓ t31✓ t32✓ t33✓ t34✓ t35✓ t36✓
  -     ↳ LE MONITEUR — Paris, Early March 1807: The powers of Europe have signed at Paris. The Imperial Peace is proclaimed.
- ENVOYS WAITING 1 · Hesse client petition
- LEDGER treasury 22470 · net +1557 · threat 45 · provinces 39 (-1) · ceiling 38040 · army 189000 · vassals Bavaria 89 · Hesse 61 · Holland 65 · Kingdom of Italy 100 · Saxony 69 · Switzerland 63
  - NET income 3825 · trade 475 · admin 50 · tribute 2314 · upkeep 2518 · charges 2047 · occupation 542
- DISPATCH: THE IMPERIAL PEACE — Europe signs at Paris. Britain, Russia, Austria and Prussia sign. The order the Emperor made is the order Europe recognizes. A peace buys time, not immunity, Sire: it bought the …
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG coalition_brewing_cancelled: The Imperial Peace dismisses the league brewing among Ottoman Empire, Sardinia and Sweden — the lesser courts signed nothing
  - ENDING reached — stopping (--stop-on-ending)

---
finished: **ending-reached** · commands 21 · popups 22 · battles 0
