# Playtest digest — amb-wagram

seed `wagram` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's attack meets fierce resistance. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualtie…
  - ⚔ Archduke Charles (lost 4458) vs Massena (lost 5336) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Naples open borders
- LEDGER treasury 2514 · net +1961 · threat 68 · provinces 28
  - NET income 3400 · trade 350 · tribute 895 · upkeep 2450 · charges 19 · blockade 175 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Ottoman envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Naples envoy has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 1
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Naples: Open Borders Agreement → decline
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #1 already answered this chain)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 action(s) unused) Turn 3 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCh… · Mack's forces advance steadily. Mack gains the advantage over Bernadotte. Casualties: Mack 2,862, Bernadotte 4,715. Bot… · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: Casualties: ArchdukeCharles's army 1,071, Deroy 9,096. Both armies remain in the field. Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 2316) vs Deroy (lost 6866) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Mack (lost 2862) vs Bernadotte (lost 4715) — The margin was slim. Training and preparation would serve Bernadotte well.
  - ⚔ Archduke Charles (lost 748, own corps) vs Deroy (lost 9096) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×4
- ENVOYS WAITING 2 · Portugal open borders · Denmark non aggression
- LEDGER treasury 4403 · net +2028 · threat 66 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 901 · upkeep 2300 · charges 108 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,715 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: A Portugal envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - TURN EVENTS 1
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 22 approaches from Bavaria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Naples's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Non-Aggression Pact → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Mack gains the advantage over Bernadotte. Casualties: Mack's army 1,609, Bernadotte 6,0… · ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles 15… · ArchdukeJohn launches a decisive assault. Bernadotte holds the line. Casualties: ArchdukeJohn 6,012, Bernadotte's army … · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,670 troops. Ga…
  - 🏴 Austria: Casualties: Mack's army 1,609, Bernadotte 6,068. Both armies remain in the field. Franconia has been captured by Austria!
  - ⚔ Mack (lost 1141, own corps) vs Bernadotte (lost 6068) — Bernadotte's army has been badly mauled. Mack proved the stronger force today.
  - ⚔ Archduke Charles (lost 158) vs Deroy (lost 2918) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - ⚔ Archduke John (lost 6012) vs Bernadotte (lost 170) — Lannes and Massena arrived to reinforce Bernadotte! The timely arrival swung the battle in our favor, Sire.
  - verbs: attack×4, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 3 · Saxony non aggression · Britain settlement offer · Hesse non aggression
- LEDGER treasury 6308 · net +2166 · threat 64 · provinces 28 (+0)
  - NET income 3400 · trade 350 · tribute 859 · upkeep 1992 · charges 236 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte, crowned last turn, has been hunted across the frontier by Mack.
  - RAIL diplomatic_ai_proposal: A Saxony envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 24 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Saxony: Non-Aggression Pact → decline
  - LETTER Hesse: Non-Aggression Pact → decline
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #8 already answered this chain)
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack delivers an effective strike. Lannes holds the line. Casualties: Mack 6,710, Lannes's army 3,867. Both armies rema…
  - ⚔ Mack (lost 6710) vs Lannes (lost 1273) — A standard affair. Nothing unusual to report.
  - verbs: fortify×1, attack×1, move×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 8136 · net +1899 · threat 52 · provinces 28 (+0)
  - NET income 3400 · trade 375 · tribute 562 · upkeep 1842 · charges 368 · blockade 188 · admiralty 90
- DISPATCH: Sire — Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - TURN EVENTS 6
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_proposal_rejected: We rejected Saxony's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 7 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack delivers an effective strike. Brutal stalemate between Mack and Bernadotte. Heavy casualties on both sides: Mack 5… · ArchdukeCharles marches from Piedmont into Provence unopposed! (1,049 lost to march) Captured: France → Austria · ArchdukeCharles marches from Provence into Lyonnais unopposed! (1,017 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (1,049 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Provence into Lyonnais unopposed! (1,017 lost to march) Captured: France → Austria
  - ⚔ Mack (lost 5525) vs Bernadotte (lost 421) — Stalemate. Bernadotte and Mack glare at each other across the field.
  - verbs: attack×3, retreat×1, stance_change×1, grant_dotation×1, wait×1
- LEDGER treasury 9628 · net +1575 · threat 49 · provinces 26 (-2)
  - NET income 3100 · trade 375 · tribute 562 · upkeep 1734 · charges 500 · blockade 188 · admiralty 90
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - TURN EVENTS 4
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - LOG ai_ai_proposal_refused: 15 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 6 — Early December 1805
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Lyonnais into Limousin unopposed! (987 lost to march) Captured: France → Austria · ArchdukeCharles marches from Limousin into Berry unopposed! (957 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Normandy garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 3,000 troops.…
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Limousin unopposed! (987 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Limousin into Berry unopposed! (957 lost to march) Captured: France → Austria
  - verbs: attack×3, grant_dotation×1, defend×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 10312 · net +884 · threat 46 · provinces 24 (-2)
  - NET income 2746 · trade 375 · tribute 562 · upkeep 1724 · charges 847 · blockade 188 · admiralty 90
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Spain will not forgive Britain the loss of Aragon and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 7
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)

## Turn 7 — Late December 1805
  - MAILBOX #9 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #9 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (stale passthrough — #9 already answered this chain)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Normandy garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,500 troops in … · ArchdukeCharles marches from Normandy into Artois unopposed! (561 lost to march) Captured: France → Austria · ArchdukeCharles marches from Artois into Champagne unopposed! (520 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -75g, France -150g. Captured: France -> Austria
  - 🏴 Austria: ArchdukeCharles marches from Normandy into Artois unopposed! (561 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Artois into Champagne unopposed! (520 lost to march) Captured: France → Austria
  - verbs: attack×3
- ENVOYS WAITING 2 · Saxony non aggression · Hesse non aggression
- LEDGER treasury 10734 · net +510 · threat 43 · provinces 21 (-3)
  - NET income 2500 · trade 375 · tribute 562 · upkeep 1756 · charges 943 · blockade 188 · admiralty 90
- DISPATCH: Sire — Normandy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: A Saxony envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - TURN EVENTS 3
  - LOG design_promoted: REVANCHE: Spain swears to retake Aragon and 2 more — Britain is not forgiven
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 8 — Early January 1806
  - MAILBOX #10 Saxony incoming_proposal: Saxony — Non-Aggression Pact → activated
  - MAILBOX #11 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Saxony, non_aggression #10 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #11 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Saxony, non_aggression #10 → reject
  - POPUP proposal_result: You have rejected Saxony's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #11 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 14 actions, 5 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore's forces advance steadily. Moore gains the advantage over Castanos. Casualties: Moore's army 1,445, Castanos 3,58… · Wellesley holds them at Normandy while allies attack from London! (+1 coordination) · ArchdukeCharles marches from Champagne into Burgundy unopposed! (481 lost to march) Captured: France → Austria · ArchdukeCharles marches from Burgundy into Savoy unopposed! (898 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Champagne into Burgundy unopposed! (481 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Burgundy into Savoy unopposed! (898 lost to march) Captured: France → Austria
  - 🏴 Bavaria: Deroy marches from Swabia into Franconia unopposed! (9 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - ⚔ Moore (lost 1239, own corps) vs Castanos (lost 3586) — The walls were not enough. Moore broke through Castanos's prepared defenses.
  - ⚔ Wellesley (lost 133, own corps) vs Castanos (lost 2996) — Castanos's fortified position was overwhelmed. A costly investment lost, Sire.
  - verbs: attack×5, unfortify×2, stance_change×2, grant_pension×2, fortify×1, retreat×1, recruit×1
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Lannes (80g/turn); Bernadotte (40g/turn); Massena (80g/turn). Th…
  - POPUP diplomatic_dialogue: Prussia, open_borders #12 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → reject_settlement_offer
- ENVOYS WAITING 2 · Prussia open borders · Britain settlement offer
- LEDGER treasury 11076 · net +4 · threat 40 · provinces 19 (-2)
  - NET income 2350 · trade 375 · tribute 562 · upkeep 1746 · charges 1009 · blockade 188 · admiralty 90 · rentes 300
- DISPATCH: Sire — Burgundy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3900 gold.
  - TURN EVENTS 4
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's non-aggression pact proposal
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Galicia into Bordelais unopposed! (94 lost to march) Captured: France → Britain · Moore marches from Maine into Anjou unopposed! (583 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Galicia into Bordelais unopposed! (94 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Maine into Anjou unopposed! (583 lost to march) Captured: France → Britain
  - verbs: attack×2, unfortify×1, wait×1
- LEDGER treasury 10671 · net -358 · threat 37 · provinces 16 (-3)
  - NET income 2000 · trade 375 · tribute 562 · upkeep 1776 · charges 991 · blockade 188 · admiralty 90 · rentes 300
- DISPATCH: Sire — Maine has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - TURN EVENTS 3
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 5 actions, 4 attacks — Russia, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Bordelais into Gascony unopposed! (92 lost to march) Captured: France → Britain · Moore marches from Anjou into Guyenne unopposed! (540 lost to march) Captured: France → Britain · Paget marches from Gascony into Bearn unopposed! (90 lost to march) Captured: France → Britain · Mack marches from Bohemia into Franconia unopposed! (768 lost to march) Captured: Bavaria → Austria
  - 🏴 Britain: Paget marches from Bordelais into Gascony unopposed! (92 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Anjou into Guyenne unopposed! (540 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Gascony into Bearn unopposed! (90 lost to march) Captured: France → Britain
  - 🏴 Austria: Mack marches from Bohemia into Franconia unopposed! (768 lost to march) Captured: Bavaria → Austria
  - verbs: attack×4, move×1
- LEDGER treasury 9639 · net -890 · threat 34 · provinces 13 (-3)
  - NET income 1600 · trade 375 · tribute 562 · upkeep 1848 · charges 1051 · blockade 188 · admiralty 90 · rentes 300
- DISPATCH: Sire — Gascony has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL balance_of_europe_shifted: Vienna System leads the current largest alignment at 51% of active European bloc power.
  - TURN EVENTS 2
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces press forward aggressively. Lannes holds the line. Casualties: Mack's army 6,058, Lannes's army 2,939. Bo… · ArchdukeJohn's forces advance steadily. Brutal stalemate between ArchdukeJohn and Deroy. Heavy casualties on both sides… · Mack's forces advance steadily. Bernadotte holds the line. Casualties: Mack 4,700, Bernadotte's army 1,786. Both armies… · Mack's forces advance steadily. Brutal stalemate between Mack and Deroy. Heavy casualties on both sides: Mack 1,462, De…
  - ⚔ Mack (lost 4236, own corps) vs Lannes (lost 862) — Bernadotte arrived to reinforce Lannes, but Murat failed to reach the field in time.
  - ⚔ Archduke John (lost 1671) vs Deroy (lost 1185) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 4700) vs Bernadotte (lost 195) — A decisive victory for Bernadotte! Mack was thoroughly outmatched.
  - ⚔ Mack (lost 1462) vs Deroy (lost 1470) — Neither Deroy nor Mack could claim the field. The armies remain locked.
  - verbs: attack×4, wait×1
- LEDGER treasury 8831 · net -502 · threat 31 · provinces 13 (+0)
  - NET income 1600 · trade 375 · tribute 562 · upkeep 1670 · charges 841 · blockade 188 · admiralty 90 · rentes 300
- DISPATCH: Sire — Bernadotte was mauled at Munich: a quarter of his corps — 1,786 men — lost in a single action.
  - TURN EVENTS 3
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: Vienna System leads the current largest alignment at 51% of active European bloc power.
  - LOG ai_ai_proposal_refused: Britain rebuffs Naples, Denmark and Bavaria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack struggles in a costly engagement. Bernadotte holds the line. Casualties: Mack's army 5,445, Bernadotte's army 1,33…
  - ⚔ Mack (lost 3662, own corps) vs Bernadotte (lost 145) — An exemplary engagement by Bernadotte. The outcome was never in doubt.
  - verbs: move×2, attack×1, fortify×1
- LEDGER treasury 8304 · net -402 · threat 28 · provinces 13 (+0)
  - NET income 1600 · trade 375 · tribute 562 · upkeep 1610 · charges 801 · blockade 188 · admiralty 90 · rentes 300
- DISPATCH: Sire — Marshal Bernadotte holds the field at Munich — Mack's corps is driven from Munich yet again — broken, and fleeing.
  - TURN EVENTS 4

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ENVOYS WAITING 2 · Denmark non aggression · Britain settlement offer
- LEDGER treasury 7300 · net -823 · threat 25 · provinces 13 (+0)
  - NET income 1600 · trade 375 · tribute 562 · upkeep 1576 · charges 956 · contributions 300 · blockade 188 · admiralty 90 · rentes 300
- DISPATCH: Sire — Wellesley has crossed into Paris. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3321 gold.
  - TURN EVENTS 4
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 14 — Early April 1806
  - MAILBOX #14 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - MAILBOX #15 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #14 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Denmark, non_aggression #14 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- ENVOYS WAITING 2 · Saxony non aggression · Hesse non aggression
- LEDGER treasury 6502 · net -651 · threat 22 · provinces 13 (+0)
  - NET income 1600 · trade 375 · tribute 562 · upkeep 1534 · charges 826 · contributions 300 · blockade 188 · admiralty 90 · rentes 300
- DISPATCH: Sire — Wellesley has crossed into Paris. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: A Saxony envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - TURN EVENTS 2
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 15 — Late April 1806
  - MAILBOX #16 Saxony incoming_proposal: Saxony — Non-Aggression Pact → activated
  - MAILBOX #17 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Saxony, non_aggression #16 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #17 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Saxony, non_aggression #16 → reject
  - POPUP proposal_result: You have rejected Saxony's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #17 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Hiller marches from Vienna into Hungary unopposed! (25 lost to march — forward supply lines reduce losses) Captured: Ba… · ArchdukeCharles marches from Milan into Tyrol unopposed! (1,934 lost to march) Captured: Bavaria → Austria · Hiller marches from Hungary into Carniola unopposed! (59 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: Hiller marches from Vienna into Hungary unopposed! (25 lost to march — forward supply lines reduce losses) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles marches from Milan into Tyrol unopposed! (1,934 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: Hiller marches from Hungary into Carniola unopposed! (59 lost to march) Captured: Bavaria → Austria
  - verbs: attack×3, unfortify×1
- ENVOYS WAITING 2 · Russia armistice losing · Prussia open borders
- LEDGER treasury 5855 · net -527 · threat 19 · provinces 13 (+0)
  - NET income 1600 · trade 375 · tribute 562 · upkeep 1516 · charges 720 · contributions 300 · blockade 188 · admiralty 90 · rentes 300
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes …
  - TURN EVENTS 2
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG coalition_dissolved: Coalition against France has dissolved.
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's non-aggression pact proposal

## Turn 16 — Early May 1806
  - MAILBOX #18 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #19 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #18 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Prussia. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #19 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #18 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #19 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 6 actions, 1 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Gascony into Languedoc unopposed! (274 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Gascony into Languedoc unopposed! (274 lost to march) Captured: France → Britain
  - verbs: move×5, attack×1
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Lannes (200g/turn); Bernadotte (160g/turn); Massena (200g/turn).…
- LEDGER treasury 5697 · net -676 · threat 18 · provinces 12 (-1)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1528 · charges 517 · blockade 188 · admiralty 90 · rentes 840
- DISPATCH: Sire — Languedoc has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - TURN EVENTS 3
  - LOG third_party_peace: THE CONGRESS: Austria and Bavaria make peace without France
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal
  - LOG ai_ai_proposal_refused: KingdomOfItaly rebuffs Bavaria (open borders agreement)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack faces a difficult fight. Bernadotte holds the line. Casualties: Mack 5,182, Bernadotte's army 1,402. Both armies r… · Hiller engages in solid combat. Bernadotte holds the line. Casualties: Hiller 1,625, Bernadotte's army 429. Both armies…
  - ⚔ Mack (lost 5182) vs Bernadotte (lost 153) — Complete dominance on the field. Mack crumbled before Bernadotte.
  - ⚔ Hiller (lost 1625) vs Bernadotte (lost 46) — A decisive victory for Bernadotte! Hiller was thoroughly outmatched.
  - verbs: attack×2, recruit×2, move×1, wait×1
- LEDGER treasury 4542 · net -858 · threat 17 · provinces 12 (+0)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1434 · charges 493 · contributions 300 · blockade 188 · admiralty 90 · rentes 840
- DISPATCH: Sire — Bernadotte was mauled at Munich: a quarter of his corps — 1,402 men — lost in a single action.
  - TURN EVENTS 1

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeC… · Hiller launches a decisive assault. Lannes holds the line. Casualties: Hiller 981, Lannes's army 192. Both armies remai… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Lannes. Casualties: Archd…
  - ⚔ Archduke Charles (lost 2062) vs Bernadotte (lost 391) — The hills were ours, but Archduke Charles took them. Bernadotte's position was overrun.
  - ⚔ Hiller (lost 981) vs Lannes (lost 63) — Lannes fought without Murat's support. The roads, or the will, proved insufficient.
  - ⚔ Archduke Charles (lost 1806) vs Lannes (lost 1209) — Lannes fought without Murat's support. The roads, or the will, proved insufficient.
  - verbs: attack×3, move×1, wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 3547 · net -497 · threat 16 · provinces 12 (+0)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1252 · charges 314 · contributions 300 · blockade 188 · admiralty 90 · rentes 840
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 1668 gold.
  - TURN EVENTS 5

## Turn 19 — Late June 1806
  - MAILBOX #20 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #20 already answered this chain)
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Lannes. Casualties: Archd…
  - ⚔ Archduke Charles (lost 1285) vs Lannes (lost 826) — Murat reached Lannes in time, Sire — but even together, the field could not be held.
  - verbs: attack×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 2974 · net -327 · threat 15 · provinces 12 (+0)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1192 · charges 204 · contributions 300 · blockade 188 · admiralty 90 · rentes 840
- DISPATCH: Sire — Lannes's corps has been broken at Munich. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: A Austria envoy has arrived with a proposal.
  - TURN EVENTS 5

## Turn 20 — Early July 1806
  - MAILBOX #21 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #21 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (stale passthrough — #21 already answered this chain)
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 2656 · net -250 · threat 14 · provinces 12 (+0)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1180 · charges 139 · contributions 300 · blockade 188 · admiralty 90 · rentes 840
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - TURN EVENTS 5
  - LOG coalition_brewing_started: Coalition brewing against Austria — Bavaria consulting (their alarm: 69)
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 21 — Late July 1806
  - MAILBOX #22 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #22 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (stale passthrough — #22 already answered this chain)
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- ENVOYS WAITING 2 · Saxony non aggression · Hesse non aggression
- LEDGER treasury 2424 · net -182 · threat 13 · provinces 12 (+0)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1160 · charges 91 · contributions 300 · blockade 188 · admiralty 90 · rentes 840
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: A Saxony envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - TURN EVENTS 3
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 22 — Early August 1806
  - MAILBOX #23 Saxony incoming_proposal: Saxony — Non-Aggression Pact → activated
  - MAILBOX #24 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Saxony, non_aggression #23 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #24 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Saxony, non_aggression #23 → reject
  - POPUP proposal_result: You have rejected Saxony's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #24 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- ENVOYS WAITING 2 · Russia armistice losing · Prussia open borders
- LEDGER treasury 2253 · net -134 · threat 12 · provinces 12 (+0)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1148 · charges 55 · contributions 300 · blockade 188 · admiralty 90 · rentes 840
- DISPATCH: Sire — Marshal Massena's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - TURN EVENTS 2
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's non-aggression pact proposal

## Turn 23 — Late August 1806
  - MAILBOX #25 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #26 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #25 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Prussia. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #26 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #25 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #26 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 2131 · net -95 · threat 13 · provinces 12 (+0)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1136 · charges 28 · contributions 300 · blockade 188 · admiralty 90 · rentes 840
- DISPATCH: Sire — the enemy has stood on our ground 7 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 901 gold.
  - TURN EVENTS 2
  - LOG coalition_brewing_started: Coalition brewing against Austria — Bavaria consulting (their alarm: 69)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 24 — Early September 1806
  - MAILBOX #27 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #27 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #27 already answered this chain)
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Lannes (300g/turn); Bernadotte (240g/turn); Massena (300g/turn).…
  - POPUP diplomatic_dialogue: Britain, peace #28 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Britain peace
- LEDGER treasury 2048 · net -485 · threat 12 · provinces 12 (+0)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1124 · charges 10 · contributions 300 · blockade 188 · admiralty 90 · rentes 1260
- DISPATCH: Sire — the enemy has stood on our ground 8 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: A Britain envoy has arrived with a proposal.
  - TURN EVENTS 3
  - LOG ai_proposal_rejected: We rejected Britain's peace treaty proposal

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- LEDGER treasury 1575 · net -463 · threat 11 · provinces 12 (+0)
  - NET income 1500 · trade 375 · tribute 562 · upkeep 1112 · contributions 300 · blockade 188 · admiralty 90 · rentes 1260
- DISPATCH: Sire — the enemy has stood on our ground 9 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 5

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 2 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Burgundy into Ile-de-France unopposed! (42 lost to march) Captured: France → Britain · Wellesley marches from Ile-de-France into Picardy unopposed! (42 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley marches from Burgundy into Ile-de-France unopposed! (42 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley marches from Ile-de-France into Picardy unopposed! (42 lost to march) Captured: France → Britain
  - verbs: attack×2
- LEDGER treasury 996 · net -579 · threat 10 · provinces 10 (-2)
  - NET income 1400 · trade 375 · tribute 562 · upkeep 1128 · contributions 300 · blockade 188 · admiralty 90 · rentes 1260
- DISPATCH: Sire — Ile-de-France has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - TURN EVENTS 3
  - LOG coalition_brewing_started: Coalition brewing against Austria — Bavaria consulting (their alarm: 69)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 445 · net -551 · threat 7 · provinces 10 (+0)
  - NET income 1400 · trade 375 · tribute 562 · upkeep 1100 · contributions 300 · blockade 188 · admiralty 90 · rentes 1260
- DISPATCH: Sire — the enemy has stood on our ground 11 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - TURN EVENTS 2

## Turn 28 — Early November 1806
  - MAILBOX #29 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #29 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (stale passthrough — #29 already answered this chain)
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- ENVOYS WAITING 3 · Saxony non aggression · Britain settlement offer · Hesse non aggression
- LEDGER treasury 123 · net -322 · threat 0 · provinces 10 (+0)
  - NET income 1325 · trade 375 · tribute 337 · upkeep 1096 · contributions 225 · blockade 188 · admiralty 90 · rentes 810
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_ai_proposal: A Saxony envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 178 gold.
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - RAIL diplomatic_alliance_cascade: Bavaria enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Switzerland has rebelled against France. It is war.
  - TURN EVENTS 2
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 29 — Late November 1806
  - MAILBOX #30 Saxony incoming_proposal: Saxony — Non-Aggression Pact → activated
  - MAILBOX #32 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #31 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Saxony, non_aggression #30 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #31 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #32 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Saxony, non_aggression #30 → reject
  - POPUP proposal_result: You have rejected Saxony's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #32 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - POPUP diplomatic_dialogue: Hesse, non_aggression #31 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 4 actions, 0 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Britain: Wellesley moves from Picardy to Orleanais. Orleanais falls to Britain!
  - verbs: move×2, garrison×1, recruit×1
- ENVOYS WAITING 2 · Russia armistice losing · Prussia open borders
- LEDGER treasury 447 · net +324 · threat 0 · provinces 9 (-1)
  - NET income 1300 · trade 375 · tribute 337 · upkeep 1100 · blockade 188 · admiralty 90 · rentes 360
- DISPATCH: Sire — Orleanais has fallen. Enemy colours fly over French homeland soil. Wellesley's corps of ~2,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any gar…
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - TURN EVENTS 2
  - LOG coalition_brewing_started: Coalition brewing against Austria — Bavaria consulting (their alarm: 69)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's non-aggression pact proposal

## Turn 30 — Early December 1806
  - MAILBOX #33 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #34 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #34 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Prussia. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #35 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #34 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #35 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Orleanais into Ardennes unopposed! (41 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley marches from Orleanais into Ardennes unopposed! (41 lost to march) Captured: France → Britain
  - verbs: attack×1, wait×1
- LEDGER treasury 692 · net +245 · threat 0 · provinces 8 (-1)
  - NET income 1250 · trade 375 · tribute 300 · upkeep 1092 · blockade 188 · admiralty 90 · rentes 360
- DISPATCH: Sire — Ardennes has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 2
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 action(s) unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Switzerland settlement offer
- LEDGER treasury 941 · net +249 · threat 0 · provinces 8 (+0)
  - NET income 1250 · trade 375 · tribute 300 · upkeep 1088 · blockade 188 · admiralty 90 · rentes 360
- DISPATCH: Supply cost you 876 men, at Franche-Comte.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 2

## Turn 32 — Early January 1807
  - MAILBOX #35 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #36 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #36 already answered this chain)
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 action(s) unused) Turn 33 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy assaults the Bern garrison! Garrison: 10,000 -> 5,000 (-5,000). Deroy loses 3,472 troops. Garrison holds — 5,000 … · Deroy assaults the Bern garrison! Garrison collapses (5,000 -> 0). Deroy loses 1,929 troops in the assault. Deroy march…
  - 🏴 Bavaria: [Materiel] Guns, horses and stores lost with the fallen: Bavaria -96g, Switzerland -125g. Captured: Switzerland -> Bavaria
  - verbs: attack×2, move×1
- LEDGER treasury 908 · net -33 · threat 0 · provinces 8 (+0)
  - NET income 1250 · trade 387 · tribute 300 · upkeep 1076 · contributions 300 · blockade 194 · admiralty 90 · rentes 360
- DISPATCH: Sire — Switzerland is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: Switzerland has been eliminated from the war.
  - TURN EVENTS 1
  - LOG coalition_brewing_started: Coalition brewing against Austria — Bavaria consulting (their alarm: 69)

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 action(s) unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 2 · Britain peace · Britain settlement offer
- LEDGER treasury 887 · net -21 · threat 0 · provinces 8 (+0)
  - NET income 1250 · trade 387 · tribute 300 · upkeep 1064 · contributions 300 · blockade 194 · admiralty 90 · rentes 360
- DISPATCH: Sire — Moore has crossed into Paris. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: A Britain envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 363 gold.
  - TURN EVENTS 1
  - LOG nation_eliminated: Switzerland has been eliminated from the war.

## Turn 34 — Early February 1807
  - MAILBOX #36 Britain incoming_proposal: Britain — Peace Treaty → activated
  - MAILBOX #37 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Britain, peace #37 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #38 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Britain, peace #37 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #38 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 action(s) unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 867 · net -20 · threat 0 · provinces 8 (+0)
  - NET income 1250 · trade 349 · tribute 300 · upkeep 1044 · contributions 300 · blockade 175 · admiralty 90 · rentes 360
- DISPATCH: Sire — Marshal Lannes's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - TURN EVENTS 1
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_proposal_rejected: We rejected Britain's peace treaty proposal

## Turn 35 — Late February 1807
  - MAILBOX #38 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #39 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (stale passthrough — #39 already answered this chain)
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 action(s) unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 2 · Saxony non aggression · Hesse non aggression
- LEDGER treasury 1155 · net +288 · threat 0 · provinces 8 (+0)
  - NET income 1250 · trade 349 · tribute 300 · upkeep 1036 · blockade 175 · admiralty 90 · rentes 360
- DISPATCH: Sire — Marshal Lannes has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - RAIL diplomatic_ai_proposal: A Saxony envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - TURN EVENTS 1
  - LOG coalition_brewing_started: Coalition brewing against Austria — Bavaria consulting (their alarm: 69)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 36 — Early March 1807
  - MAILBOX #39 Saxony incoming_proposal: Saxony — Non-Aggression Pact → activated
  - MAILBOX #40 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Saxony, non_aggression #40 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Hesse. Your earlier answer was not delivered; the matt…
  - POPUP diplomatic_dialogue: incoming_proposal #41 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Saxony, non_aggression #40 → reject
  - POPUP proposal_result: You have rejected Saxony's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #41 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 action(s) unused) Turn 37 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 2 · Russia armistice losing · Prussia open borders
- LEDGER treasury 1447 · net +292 · threat 0 · provinces 8 (+0)
  - NET income 1250 · trade 349 · tribute 300 · upkeep 1032 · blockade 175 · admiralty 90 · rentes 360
- DISPATCH: Sire — 7 turns without settlement on Marshal Lannes. A rente would close it today; the arrears will not close themselves.
  - RAIL diplomatic_ai_proposal: A Russia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - TURN EVENTS 1
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's non-aggression pact proposal

## Turn 37 — Late March 1807
  - MAILBOX #41 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #42 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #42 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Prussia. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #43 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #42 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #43 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 action(s) unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 1743 · net +296 · threat 0 · provinces 8 (+0)
  - NET income 1250 · trade 349 · tribute 300 · upkeep 1028 · blockade 175 · admiralty 90 · rentes 360
- DISPATCH: Sire — Marshal Lannes's claim is 8 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 38 — Early April 1807
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 action(s) unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 2021 · net +275 · threat 0 · provinces 8 (+0)
  - NET income 1250 · trade 349 · tribute 262 · upkeep 1008 · charges 3 · blockade 175 · admiralty 90 · rentes 360
- DISPATCH: Sire — Brabant has been taken by Britain.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 697 gold.
  - TURN EVENTS 1
  - LOG coalition_brewing_started: Coalition brewing against Austria — Bavaria consulting (their alarm: 69)

## Turn 39 — Late April 1807
  - MAILBOX #43 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #44 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #44 already answered this chain)
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 action(s) unused) Turn 40 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack assaults the Paris garrison! Garrison: 25,000 -> 12,537 (-12,463). Mack loses 6,944 troops. Garrison holds — 12,53… · Mack assaults the Paris garrison! Garrison: 12,537 -> 6,269 (-6,268). Mack loses 3,869 troops. Garrison holds — 6,269 d… · Mack assaults the Paris garrison! Garrison collapses (6,269 -> 0). Mack loses 2,176 troops in the assault. Mack marches…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -108g, France -156g. Captured: France -> Austria
  - verbs: attack×3, wait×1
- LEDGER treasury 862 · net -67 · threat 0 · provinces 7 (-1)
  - NET income 950 · trade 349 · tribute 225 · upkeep 1016 · blockade 175 · admiralty 90 · rentes 360
- DISPATCH: Sire — Paris HAS FALLEN. Our capital is in Austria's hands, and every courier in Europe is already carrying the news.
  - TURN EVENTS 1
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 action(s) unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 595 · net -267 · threat 0 · provinces 7 (+0)
  - NET income 950 · trade 349 · tribute 225 · upkeep 1016 · contributions 200 · blockade 175 · admiralty 90 · rentes 360
- DISPATCH: Sire — Paget has crossed into Flanders. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: A Austria envoy has arrived with a proposal.
  - TURN EVENTS 1

---
finished: **completed** · commands 40 · popups 110 · battles 22
