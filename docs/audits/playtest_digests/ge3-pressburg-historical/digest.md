# Playtest digest — ge3-pressburg-historical

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 28 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7515213964dd` (dirty) · content `84c37838fe8e` · driver `c29de0d04ee3`
  - loaded save `fixture_ge3_pressburg.json` → Loaded: GE-3 staged — after Pressburg and Tilsit (turn 28, 55 titled)

## Turn 28 — Early November 1806
- CMD `summon the congress` → ✓ The Emperor summons the powers of Europe to Paris. The Congress sits for 8 turns, to the end of turn 36. Britain SHUT OUT; Russia RECOGNIZES; Austria RECOGNIZES; Prussia…
  - POPUP diplomatic_dialogue: Bavaria, client_petition #1 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to Bavaria. Loyalty +10 (60 → 70); bond 60 → 60 (+3 a turn). Cost: 1 DP. Our net falls by 30g a turn — 150g of income forfeited, 15g of occupation relieved, 113g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- CMD `offer Prussia 1200 gold for recognition` → ✓ 1,200g is laid before Berlin (+12). Prussia now RECOGNIZES the order.
  - POPUP diplomatic_dialogue: Hesse, client_petition #2 → grant the petition
  - POPUP proposal_result: Brunswick is ceded to Hesse. Loyalty +10 (60 → 70); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 63g a turn — 0g of income forfeited, 75g of occupation relieved, 0g returned as tribute at today's 75% rate, the force limit falls 2,500 (+12g surcharge). → display-only
- CMD `invest in saxony` → ✗ Insufficient diplomatic points (0/1 required).
  - POPUP diplomatic_dialogue: Holland, client_petition #3 → (left standing — disabled: Grant the petition)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Holland, client_petition #3 → (left standing — disabled: Grant the petition)
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- SPENT 1200g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, garrison×1, wait×1
- LAPSED Holland client petition · KingdomOfItaly client petition · Saxony client petition · Switzerland client petition
- ENVOYS WAITING 2 · Denmark open borders · Britain settlement offer
- LEDGER treasury 9713 · net +2748 · threat 51 · provinces 40 · ceiling 51846 · army 188548 · vassals Bavaria 71 · Hesse 69 · Holland 89 · Kingdom of Italy 89 · Saxony 71 · Switzerland 87
  - NET income 4060 · trade 387 · admin 50 · tribute 2052 · upkeep 2480 · charges 502 · occupation 535 · blockade 194 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 1 of 8 · 55 of 50 titled · Britain SHUT OUT · Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Sire — THE EMPEROR SUMMONS THE POWERS TO PARIS. The Congress sits 8 turns, to the end of turn 36; every great power must sign, be shut out, or be gone. No court refuses today.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL +3 more
  - TURN EVENTS 9
- DIPLO +9 medium/low (diplomatic_dp_regen, sovereign_takes_field, cs_tier_shift, blockade_begins ×6)
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Bavaria and Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Ottoman Empire and Sweden rebuff Austria (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Carniola and 2 more — France is not forgiven
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 100 to 61; Britain remains at war with us.
  - LOG balance_of_europe_shifted: French System leads the current largest alignment at 50% of active European bloc power. Spain is the decisive non-France slice of the bloc; letting t…
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG nation_eliminated: Hanover has been eliminated from the war.
  - LOG nation_eliminated: Naples has been eliminated from the war.
  - LOG nation_eliminated: Portugal has been eliminated from the war.

## Turn 29 — Late November 1806
  - LETTER Denmark: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #9 → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace #10 → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm #11 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `invest in saxony` → ✓ Invested in Saxony: +10 loyalty (71 → 81). Cost: 1 DP + 200g. Cooldown: 3 turns.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 12362 · net +2654 · threat 52 · provinces 40 (+0) · ceiling 51152 · army 188548 · vassals Bavaria 72 · Hesse 68 · Holland 88 · Kingdom of Italy 88 · Saxony 77 · Switzerland 84
  - NET income 4060 · trade 424 · admin 50 · tribute 2145 · upkeep 2480 · charges 708 · occupation 535 · blockade 212 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 2 of 8 · 55 of 50 titled · Britain SHUT OUT · Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Garrison at Lisbon reinforced: 12,000 -> 14,000
  - TURN EVENTS 4
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 5 approaches from Austria and Bavaria are rebuffed (open borders agreement)

## Turn 30 — Early December 1806
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (2 turns remaining).
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 14983 · net +2433 · threat 53 · provinces 40 (+0) · ceiling 48955 · army 188548 · vassals Bavaria 73 · Hesse 67 · Holland 87 · Kingdom of Italy 87 · Saxony 73 · Switzerland 81
  - NET income 4060 · trade 424 · admin 50 · tribute 2145 · upkeep 2480 · charges 929 · occupation 535 · blockade 212 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 3 of 8 · 55 of 50 titled · Britain SHUT OUT · Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Garrison at Lisbon reinforced: 14,000 -> 16,000
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Prussia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 8 approaches from Austria, Denmark and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 32 approaches rebuffed among the courts (open borders agreement)

## Turn 31 — Late December 1806
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (1 turns remaining).
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 17374 · net +2213 · threat 54 · provinces 40 (+0) · ceiling 46946 · army 188548 · vassals Bavaria 74 · Hesse 66 · Holland 86 · Kingdom of Italy 86 · Saxony 69 · Switzerland 78
  - NET income 4060 · trade 424 · admin 50 · tribute 2145 · upkeep 2480 · charges 1149 · occupation 535 · blockade 212 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 4 of 8 · 55 of 50 titled · Britain SHUT OUT · Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Garrison at Lisbon reinforced: 16,000 -> 18,000
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Bavaria (open borders agreement)

## Turn 32 — Early January 1807
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `invest in saxony` → ✓ Invested in Saxony: +10 loyalty (69 → 79). Cost: 1 DP + 200g. Cooldown: 3 turns.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 19365 · net +2020 · threat 55 · provinces 40 (+0) · ceiling 45256 · army 188548 · vassals Bavaria 75 · Hesse 65 · Holland 85 · Kingdom of Italy 85 · Saxony 75 · Switzerland 75
  - NET income 4060 · trade 449 · admin 50 · tribute 2145 · upkeep 2480 · charges 1354 · occupation 535 · blockade 225 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 5 of 8 · 55 of 50 titled · Britain SHUT OUT · Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Garrison at Lisbon reinforced: 18,000 -> 20,000
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)

## Turn 33 — Late January 1807
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (2 turns remaining).
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 22846 · net +3303 · threat 56 · provinces 40 (+0) · ceiling 87351 · army 188548 · vassals Bavaria 76 · Hesse 64 · Holland 84 · Kingdom of Italy 84 · Saxony 71 · Switzerland 72
  - NET income 4785 · trade 449 · admin 50 · tribute 2201 · upkeep 2480 · charges 1067 · occupation 320 · blockade 225 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 6 of 8 · 55 of 50 titled · Britain SHUT OUT · Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Garrison at Lisbon reinforced: 20,000 -> 22,000
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Prussia against France (200g/turn)

## Turn 34 — Early February 1807
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #14 → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace #15 → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm #16 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (1 turns remaining).
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 26082 · net +3060 · threat 57 · provinces 40 (+0) · ceiling 82330 · army 188548 · vassals Bavaria 77 · Hesse 63 · Holland 83 · Kingdom of Italy 83 · Saxony 67 · Switzerland 69
  - NET income 4785 · trade 449 · admin 50 · tribute 2201 · upkeep 2480 · charges 1310 · occupation 320 · blockade 225 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 7 of 8 · 55 of 50 titled · Britain SHUT OUT · Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Garrison at Lisbon reinforced: 22,000 -> 24,000
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 12 approaches from Austria and Bavaria are rebuffed (open borders agreement)

## Turn 35 — Late February 1807
- CMD `invest in saxony` → ✓ Invested in Saxony: +10 loyalty (67 → 77). Cost: 1 DP + 200g. Cooldown: 3 turns.
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- SPENT 200g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, naval_expedition×1, wait×1
- ENVOYS WAITING 1 · Bavaria client petition
- LEDGER treasury 28877 · net +2822 · threat 58 · provinces 40 (+0) · ceiling 77868 · army 188548 · vassals Bavaria 78 · Hesse 62 · Holland 82 · Kingdom of Italy 82 · Saxony 73 · Switzerland 66
  - NET income 4785 · trade 449 · admin 50 · tribute 2201 · upkeep 2480 · charges 1548 · occupation 320 · blockade 225 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 8 of 8 · 55 of 50 titled · Britain SHUT OUT · Russia, Austria, Prussia RECOGNIZE
- DISPATCH: Garrison at Lisbon reinforced: 24,000 -> 25,000
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Copenhagen.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Ottoman Empire and Sweden rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Spain, Ottoman Empire and Sweden rebuff Bavaria (open borders agreement)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 33 approaches rebuffed among the courts (open borders agreement)

## Turn 36 — Early March 1807
  - MAILBOX #11 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #17 → grant the petition
  - POPUP proposal_result: Carniola is ceded to Bavaria. Loyalty +10 (78 → 88); bond 60 → 60 (+3 a turn). Cost: 1 DP. Our net falls by 34g a turn — 150g of income forfeited, 15g of occupation relieved, 113g returned as tribute at today's 75% rate, the force limit falls 2,500 (+12g surcharge). → display-only
- CMD `invest in saxony` → ✗ Investment in Saxony on cooldown (2 turns remaining).
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - ENDING — THE IMPERIAL PEACE: Europe accepts the order of the French Empire. [THE ASCENDANT EMPIRE]
  -     ↳ Early March 1807 (turn 36) · register `imperial_peace` · marked — the campaign continues
  -     ↳ THE VERDICT — THE ASCENDANT EMPIRE: The Empire stands larger and surer than it began. / The great powers have signed the order at Paris. / History will call it a rising star — not yet fixed in the heavens.
  -     ↳ The Verdict of History: an empire ascendant.
  -     ↳ THE RECORD — battles 0 (0 won, 0 lost) · men lost 0, inflicted 0 · provinces taken 11, lost 0 · marshals fallen 0, taken 0 · coalitions faced 1 · peaces signed 0
  -     ↳ THE CONGRESS (congress) — Britain SHUT OUT · Russia SIGNED · Austria SIGNED · Prussia SIGNED · 55 of 50 titled
  -     ↳ THE SITTING — t29✓ t30✓ t31✓ t32✓ t33✓ t34✓ t35✓ t36✓
  -     ↳ LE MONITEUR — Paris, Early March 1807: The powers of Europe have signed at Paris. The Imperial Peace is proclaimed.
- ENVOYS WAITING 1 · Hesse client petition
- LEDGER treasury 31579 · net +2538 · threat 59 · provinces 39 (-1) · ceiling 73315 · army 188548 · vassals Bavaria 89 · Hesse 61 · Holland 81 · Kingdom of Italy 81 · Saxony 69 · Switzerland 63
  - NET income 4635 · trade 449 · admin 50 · tribute 2314 · upkeep 2492 · charges 1798 · occupation 305 · blockade 225 · admiralty 90
- DISPATCH: THE IMPERIAL PEACE — Europe signs at Paris. Russia, Austria and Prussia sign; Britain is shut out. The order the Emperor made is the order Europe recognizes.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria, Denmark and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 25 approaches rebuffed, chiefly from Spain and Bavaria (open borders agreement)
  - ENDING reached — stopping (--stop-on-ending)

---
finished: **ending-reached** · commands 21 · popups 18 · battles 0
