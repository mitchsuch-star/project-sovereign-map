# Playtest digest — ge3-premature-historical

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7515213964dd` (dirty) · content `84c37838fe8e` · driver `c29de0d04ee3`
  - loaded save `fixture_ge3_premature.json` → Loaded: GE-3 staged — the Premature summons (exactly 50 titled, turn 1)

## Turn 1 — Late September 1805
- CMD `summon the congress` → ✓ The Emperor summons the powers of Europe to Paris. The Congress sits for 8 turns, to the end of turn 9. Britain REFUSES — at war with us (our war score 0 — it sues at +4…
  - POPUP diplomatic_dialogue: Holland, client_petition #1 → refuse the petition
  - POPUP proposal_result: Holland's petition for Brunswick is refused: loyalty −10 (100 → 90); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Switzerland, client_petition #2 → refuse the petition
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (100 → 90); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on …
  - ⚔ Archduke Charles (lost 4875) vs Massena (lost 5379) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 4255 · net +3663 · threat 69 · provinces 43 · ceiling 100631 · army 183621 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 87
  - NET income 5200 · trade 350 · admin 50 · tribute 895 · upkeep 2302 · charges 85 · occupation 180 · blockade 175 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 1 of 8 · 50 of 50 titled · Britain REFUSES (at war) · Russia REFUSES (at war) · Austria REFUSES (at war) · Prussia REFUSES (Hanover)
- DISPATCH: Sire — THE EMPEROR SUMMONS THE POWERS TO PARIS. The Congress sits 8 turns, to the end of turn 9; every great power must sign, be shut out, or be gone. Vienna, London, Berlin and St Petersburg refuse …
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Portugal will not forgive France the loss of Beira and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_dp_regen, sovereign_takes_field, cs_tier_shift, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - MAILBOX #3 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #3 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties… · Mack engages in solid combat. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,166, Lan… · ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archduke…
  - ⚔ Archduke Charles (lost 3902) vs Massena (lost 5293) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 5166) vs Lannes (lost 1487, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 1757) vs Bernadotte (lost 4559) — The engagement proceeded as one might expect, Sire.
  - verbs: attack×3
- ENVOYS WAITING 2 · Portugal open borders · Saxony open borders
- LEDGER treasury 7600 · net +3839 · threat 68 · provinces 43 (+0) · ceiling 84380 · army 169638 · vassals Holland 86 · Kingdom of Italy 100 · Switzerland 82
  - NET income 5182 · trade 350 · admin 50 · tribute 856 · upkeep 1874 · charges 280 · occupation 180 · blockade 175 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 2 of 8 · 50 of 50 titled · Britain REFUSES (at war) · Russia REFUSES (at war) · Austria REFUSES (at war) · Prussia REFUSES (Hanover)
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,559 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Portugal swears to retake Beira and 2 more — France is not forgiven
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Bernadotte. Casualties: A… · Mack engages in solid combat. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 4,438, Lan… · ArchdukeCharles faces a difficult fight. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles 1,… · Mack delivers an effective strike. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack 3,839,…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 982) vs Bernadotte (lost 7071) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 4438) vs Lannes (lost 1427, own corps) — Reinforcements from Napoleon bolstered Lannes's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 1811) vs Deroy (lost 4964) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - ⚔ Mack (lost 3839) vs Murat (lost 2224, own corps) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×4, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 11054 · net +3938 · threat 67 · provinces 43 (+0) · ceiling 72578 · army 153859 · vassals Holland 83 · Kingdom of Italy 100 · Switzerland 77
  - NET income 5152 · trade 350 · admin 50 · tribute 860 · upkeep 1450 · charges 579 · occupation 180 · blockade 175 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 3 of 8 · 50 of 50 titled · Britain REFUSES (at war) · Russia REFUSES (at war) · Austria REFUSES (at war) · Prussia REFUSES (at war)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_alliance_cascade: Bavaria enters the war via alliance with France.
  - RAIL +1 more
  - TURN EVENTS 5
- DIPLO +5 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 11 courts rebuff Bavaria (open borders agreement)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG ai_ai_proposal_refused: 11 approaches from Prussia and Naples are rebuffed (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #9 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Brutal stalemate between Mack and Bernadotte. Heavy casualties on both sides: Mack 4,794,… · Mack engages in solid combat. Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack 3,427, Ma…
  - 🏴 Austria: Bernadotte retreats! Mack pursues into Munich. (1,932 lost to march) Munich has been captured by Austria!
  - ⚔ Mack (lost 4794) vs Bernadotte (lost 400, own corps) — Reinforcement from Lannes and Massena kept Bernadotte standing, Sire — but neither side yielded the ground.
  - ⚔ Mack (lost 3427) vs Massena (lost 3124) — Stalemate. Massena and Mack glare at each other across the field.
  - verbs: attack×2, retreat×1, stance_change×1, form_square×1
- LEDGER treasury 14719 · net +3724 · threat 66 · provinces 43 (+0) · ceiling 67014 · army 146303 · vassals Holland 84 · Kingdom of Italy 100 · Switzerland 76
  - NET income 5154 · trade 237 · admin 50 · tribute 829 · upkeep 1252 · charges 905 · occupation 180 · blockade 119 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 4 of 8 · 50 of 50 titled · Britain REFUSES (at war) · Russia REFUSES (at war) · Austria REFUSES (at war) · Prussia REFUSES (at war)
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, sovereign_takes_field, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Prussia
  - LOG sponsorship_granted: Britain sponsors Prussia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Britain, Russia and Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Spain rebuffs Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected PapalStates's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack executes a brilliant maneuver! Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack 3,4… · Mack delivers an effective strike. Mack gains the advantage over Bernadotte. Casualties: Mack 1,196, Bernadotte's army …
  - ⚔ Mack (lost 3424) vs Massena (lost 3084) — Neither Massena nor Mack could claim the field. The armies remain locked.
  - ⚔ Mack (lost 1196) vs Bernadotte (lost 939, own corps) — Bernadotte fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×2
- ENVOYS WAITING 1 · Ottoman open borders
- LEDGER treasury 18216 · net +3514 · threat 65 · provinces 43 (+0) · ceiling 62799 · army 139113 · vassals Holland 83 · Kingdom of Italy 100 · Switzerland 73
  - NET income 5152 · trade 237 · admin 50 · tribute 829 · upkeep 1088 · charges 1277 · occupation 180 · blockade 119 · admiralty 90
- CONGRESS THE CONGRESS SITS — turn 5 of 8 · 50 of 50 titled · Britain REFUSES (at war) · Russia REFUSES (at war) · Austria REFUSES (at war) · Prussia REFUSES (at war)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franche-Comte. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (defensive alliance)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Spain rebuffs Prussia and Naples (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn attacks with overwhelming force. Brutal stalemate between ArchdukeJohn and Lannes. Heavy casualties on bot… · ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Lannes. Casualties: ArchdukeCharles…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Franche-Comte. (956 lost to march) Franche-Comte has been captured by Austria!
  - ⚔ Archduke John (lost 2316) vs Lannes (lost 653, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 671, own corps) vs Lannes (lost 2248, own corps) — Lannes fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×2, move×1
- ENVOYS WAITING 3 · Portugal open borders · Prussia settlement offer · Saxony open borders
- LEDGER treasury 20757 · net +2603 · threat 79 · provinces 42 (-1) · ceiling 42734 · army 128539 · vassals Holland 82 · Kingdom of Italy 100 · Switzerland 70
  - NET income 5100 · trade 237 · admin 50 · tribute 833 · upkeep 1008 · charges 2220 · occupation 180 · blockade 119 · admiralty 90
- CONGRESS THE CONGRESS OF PARIS — dissolved on turn 6; it may be summoned again on turn 16 (9 turns remain) · 49 of 50 titled
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. ArchdukeJohn's corps of 16,364 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL settlement_offer_arrival: Prussia has offered terms to settle Prussia vs France.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Saxony: Open Borders Agreement → decline
  - MAILBOX #13 Prussia incoming_settlement_offer: Prussia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×2
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 23321 · net +2252 · threat 80 · provinces 42 (+0) · ceiling 41835 · army 126310 · vassals Holland 83 · Kingdom of Italy 100 · Switzerland 69
  - NET income 5100 · trade 237 · admin 50 · tribute 838 · upkeep 992 · charges 2592 · occupation 180 · blockade 119 · admiralty 90
- CONGRESS THE CONGRESS OF PARIS — dissolved on turn 6; it may be summoned again on turn 16 (8 turns remain) · 49 of 50 titled
- DISPATCH: Lannes's army is recovering. Effectiveness penalty: -15%.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal

## Turn 8 — Early January 1806
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Murat. Casualties: Archdu…
  - ⚔ Archduke Charles (lost 2603, own corps) vs Murat (lost 696, own corps) — Ney and Davout marched to Murat's guns as ordered. It was not enough.
  - verbs: move×2, attack×1
- ENVOYS WAITING 2 · Britain settlement offer · Holland client petition
- LEDGER treasury 24395 · net +1177 · threat 81 · provinces 42 (+0) · ceiling 31713 · army 117417 · vassals Holland 82 · Kingdom of Italy 100 · Switzerland 66
  - NET income 5088 · trade 237 · admin 50 · tribute 842 · upkeep 912 · charges 3601 · contributions 138 · occupation 180 · blockade 119 · admiralty 90
- CONGRESS THE CONGRESS OF PARIS — dissolved on turn 6; it may be summoned again on turn 16 (7 turns remain) · 49 of 50 titled
- DISPATCH: Sire — Murat's corps has been broken at Lorraine. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 5178 gold.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected PapalStates's open borders agreement proposal

## Turn 9 — Late January 1806
  - MAILBOX #16 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #17 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → reject_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #17 → refuse the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → reject_settlement_offer
  - POPUP proposal_result: Holland's petition for Brunswick is refused: loyalty −10 (82 → 72); bond -20 → -40 (-2 a turn). Nothing is charged. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #17 → refuse the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Ottoman open borders · Switzerland client petition
- LEDGER treasury 26319 · net +1666 · threat 82 · provinces 42 (+0) · ceiling 38746 · army 116252 · vassals Holland 72 · Kingdom of Italy 100 · Switzerland 65
  - NET income 5091 · trade 237 · admin 50 · tribute 847 · upkeep 912 · charges 3258 · occupation 180 · blockade 119 · admiralty 90
- CONGRESS THE CONGRESS OF PARIS — dissolved on turn 6; it may be summoned again on turn 16 (6 turns remain) · 49 of 50 titled
- DISPATCH: Murat's army is recovering. Effectiveness penalty: -15%.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 10 — Early February 1806
  - LETTER Ottoman: Open Borders Agreement → decline
  - MAILBOX #19 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #19 → refuse the petition
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (65 → 55); bond -20 → -40 (-2 a turn). Nothing is charged. → display-only
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Portugal open borders · Saxony open borders
- LEDGER treasury 27930 · net +1390 · threat 83 · provinces 42 (+0) · ceiling 38056 · army 115121 · vassals Holland 72 · Kingdom of Italy 100 · Switzerland 53
  - NET income 5094 · trade 237 · admin 50 · tribute 851 · upkeep 896 · charges 3557 · occupation 180 · blockade 119 · admiralty 90
- CONGRESS THE CONGRESS OF PARIS — dissolved on turn 6; it may be summoned again on turn 16 (5 turns remain) · 49 of 50 titled
- DISPATCH: Murat's army has fully recovered and is combat ready.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal

---
finished: **completed** · commands 12 · popups 26 · battles 15
