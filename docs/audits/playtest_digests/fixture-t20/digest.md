# Playtest digest — fixture-t20

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - loaded save `fixture_t20_ambient.json` → Loaded: fixture-gen_t20

## Turn 20 — Early July 1806
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #8 already answered this chain)
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 9 actions, 7 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Berry into Gascony unopposed! (95 lost to march) Captured: France → Britain · Paget marches from Gascony into Guyenne unopposed! (46 lost to march) Captured: France → Britain · Paget marches from Guyenne into Anjou unopposed! (46 lost to march) Captured: France → Britain · ArchdukeCharles assaults the Moravia garrison! Garrison collapses (1 -> 0). ArchdukeCharles loses 0 troops in the assau…
  - 🏴 Britain: Paget marches from Berry into Gascony unopposed! (95 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Gascony into Guyenne unopposed! (46 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Guyenne into Anjou unopposed! (46 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeCharles loses 0 troops in the assault. ArchdukeCharles marches into Moravia! (147 lost to march) Captured: Bavaria -> Austria
  - 🏴 Austria: ArchdukeJohn marches from Milan into Munich unopposed! (108 lost to march — forward supply lines reduce losses) Captured: Bavaria → Austria
  - 🏴 Austria: Both armies remain in the field. ArchdukeJohn advances into Franche-Comte. (104 lost to march) Franche-Comte has been captured by Austria!
  - ⚔ Archduke John (lost 331) vs Bernadotte (lost 328) — Lannes arrived to reinforce Bernadotte, but Soult failed to reach the field in time. And Bernadotte was taken on that f…
  - verbs: attack×7, move×1, wait×1
- ORDER Lannes [retired]: Lannes's question is overtaken, Sire — Lannes has marched clear of Franche-Comte. He awaits new orders.
- ENVOYS WAITING 2 · Hesse non aggression · Britain settlement offer
- LEDGER treasury 16314 · net -881 · threat 17 · provinces 17
  - NET income 1900 · trade 350 · tribute 487 · upkeep 964 · charges 2439 · blockade 175 · admiralty 90
- DISPATCH: Sire — Gascony has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 6950 gold.
  - RAIL third_party_peace: THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes …
  - TURN EVENTS 1
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG coalition_dissolved: Coalition against France has dissolved.
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal KingdomOfItaly joined France's war.
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 34% of active European bloc power.
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG design_promoted: REVANCHE: Spain swears to retake Aragon and 2 more — Britain is not forgiven
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)

## Turn 21 — Late July 1806
  - MAILBOX #22 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #23 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #23 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #24 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #23 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #24 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 8 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Anjou into Maine unopposed! (45 lost to march) Captured: France → Britain · Paget marches from Maine into Brittany unopposed! (45 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Anjou into Maine unopposed! (45 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Maine into Brittany unopposed! (45 lost to march) Captured: France → Britain
  - verbs: attack×2, form_square×1, stance_change×1, fortify×1, grant_dotation×1, wait×1, recruit×1
- LEDGER treasury 15185 · net -933 · threat 14 · provinces 15 (-2)
  - NET income 1700 · trade 350 · tribute 487 · upkeep 972 · charges 2283 · blockade 175 · admiralty 90
- DISPATCH: Sire — Maine has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - TURN EVENTS 2
  - LOG third_party_peace: THE CONGRESS: Austria and Bavaria make peace without France
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Limousin into Lyonnais unopposed! (43 lost to march) Captured: France → Britain · Paget marches from Lyonnais into Provence unopposed! (43 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Limousin into Lyonnais unopposed! (43 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Lyonnais into Provence unopposed! (43 lost to march) Captured: France → Britain
  - verbs: attack×2, wait×1
- ENVOYS WAITING 4 · Russia armistice losing · Switzerland settlement offer · Prussia open borders · Denmark non aggression
- LEDGER treasury 13680 · net -1214 · threat 11 · provinces 13 (-2)
  - NET income 1400 · trade 350 · tribute 487 · upkeep 980 · charges 2256 · blockade 175 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 2

## Turn 23 — Late August 1806
  - MAILBOX #24 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #27 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - MAILBOX #25 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #26 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #25 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Denmark. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #27 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Russia, armistice_losing #25 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #26 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - POPUP diplomatic_dialogue: Prussia, open_borders #26 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - POPUP diplomatic_dialogue: Denmark, non_aggression #27 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 2 actions, 2 attacks — Russia, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Provence into Languedoc unopposed! (42 lost to march) Captured: France → Britain · Paget marches from Lyonnais into Savoy unopposed! (83 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Provence into Languedoc unopposed! (42 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Lyonnais into Savoy unopposed! (83 lost to march) Captured: France → Britain
  - verbs: attack×2
- LEDGER treasury 12250 · net -1154 · threat 10 · provinces 11 (-2)
  - NET income 1200 · trade 350 · tribute 487 · upkeep 996 · charges 1980 · blockade 175 · admiralty 90
- DISPATCH: Sire — Languedoc has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - TURN EVENTS 2
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 11108 · net -921 · threat 9 · provinces 11 (+0)
  - NET income 1200 · trade 350 · tribute 487 · upkeep 984 · charges 1759 · blockade 175 · admiralty 90
- DISPATCH: Supply cost you 839 men, at Lorraine.
  - TURN EVENTS 2

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 6 actions, 3 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Limousin into Champagne unopposed! (40 lost to march) Captured: France → Britain · Paget marches from Champagne into Artois unopposed! (39 lost to march) Captured: France → Britain · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Massena. Casualties: Archduke…
  - 🏴 Britain: Paget marches from Limousin into Champagne unopposed! (40 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Champagne into Artois unopposed! (39 lost to march) Captured: France → Britain
  - ⚔ Archduke Charles (lost 954) vs Massena (lost 5453) — The hills were ours, but Archduke Charles took them. Massena's position was overrun.
  - verbs: attack×3, move×2, recruit×1
- ORDER Massena [awaiting_response]: Massena is cornered at Piedmont with 15,614 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Piedmont with 15,614 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 9653 · net -767 · threat 8 · provinces 9 (-2)
  - NET income 1000 · trade 350 · tribute 337 · upkeep 740 · charges 1499 · blockade 175 · admiralty 90
- DISPATCH: Sire — Champagne has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - RAIL balance_of_europe_shifted: Vienna System leads the current largest alignment at 50% of active European bloc power.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 4334 gold.
  - TURN EVENTS 1
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 26 — Early October 1806
  - MAILBOX #28 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #29 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #29 already answered this chain)
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 4 actions, 3 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Artois into Picardy unopposed! (39 lost to march) Captured: France → Britain · Paget marches from Picardy into Ile-de-France unopposed! (38 lost to march) Captured: France → Britain · Paget marches from Ile-de-France into Ardennes unopposed! (38 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Artois into Picardy unopposed! (39 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Picardy into Ile-de-France unopposed! (38 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Ile-de-France into Ardennes unopposed! (38 lost to march) Captured: France → Britain
  - verbs: attack×3, move×1
- LEDGER treasury 8720 · net -751 · threat 0 · provinces 6 (-3)
  - NET income 850 · trade 375 · tribute 337 · upkeep 768 · charges 1317 · blockade 188 · admiralty 90
- DISPATCH: Sire — Picardy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - TURN EVENTS 2
  - LOG ai_ai_proposal_refused: Spain, Sardinia and Holland rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG balance_of_europe_shifted: Vienna System leads the current largest alignment at 50% of active European bloc power.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 3 actions, 0 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, move×1, fortify×1
- ENVOYS WAITING 2 · Hesse non aggression · Switzerland settlement offer
- LEDGER treasury 7952 · net -617 · threat 0 · provinces 6 (+0)
  - NET income 850 · trade 375 · tribute 300 · upkeep 748 · charges 1166 · blockade 188 · admiralty 90
- DISPATCH: Sire — Brabant has been taken by Britain.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 2
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 28 — Early November 1806
  - MAILBOX #29 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #30 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #30 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #30 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 7309 · net -517 · threat 0 · provinces 6 (+0)
  - NET income 850 · trade 375 · tribute 262 · upkeep 736 · charges 1040 · blockade 188 · admiralty 90
- DISPATCH: Sire — Gelderland has been taken by Britain.
  - TURN EVENTS 2
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, garrison×1
- ENVOYS WAITING 3 · Russia armistice losing · Prussia open borders · Denmark non aggression
- LEDGER treasury 6800 · net -409 · threat 0 · provinces 6 (+0)
  - NET income 850 · trade 375 · tribute 262 · upkeep 728 · charges 940 · blockade 188 · admiralty 90
- DISPATCH: Supply cost you 759 men, at Lorraine.
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - TURN EVENTS 2
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Austria (defensive alliance)

## Turn 30 — Early December 1806
  - MAILBOX #31 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #32 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #33 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #32 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Denmark. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #34 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #32 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #33 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #33 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - POPUP diplomatic_dialogue: Denmark, non_aggression #34 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 7 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, move×1, unfortify×1, fortify×1, form_square×1, wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 6395 · net -326 · threat 0 · provinces 6 (+0)
  - NET income 850 · trade 375 · tribute 262 · upkeep 724 · charges 861 · blockade 188 · admiralty 90
- DISPATCH: Supply cost you 743 men, at Lorraine.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 2720 gold.
  - TURN EVENTS 2
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 31 — Late December 1806
  - MAILBOX #34 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #35 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #35 already answered this chain)
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 action(s) unused) Turn 32 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 6081 · net -252 · threat 0 · provinces 6 (+0)
  - NET income 850 · trade 375 · tribute 262 · upkeep 712 · charges 799 · blockade 188 · admiralty 90
- DISPATCH: Supply cost you 727 men, at Lorraine.
  - RAIL diplomatic_ai_proposal: A Austria envoy has arrived with a proposal.
  - TURN EVENTS 2
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)

---
finished: **completed** · commands 12 · popups 37 · battles 2
