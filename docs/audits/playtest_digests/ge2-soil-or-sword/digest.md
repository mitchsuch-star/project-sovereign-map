# Playtest digest — ge2-soil-or-sword

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `da91683b56dc` (dirty) · content `4fdb803f0fdd` · driver `296621f2139c`
  - loaded save `fixture_ge2_soil_or_sword.json` → Loaded: GE-2 staged — the Empire without soil (Brittany alone, at war)

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on …
  - ⚔ Archduke Charles (lost 5094) vs Massena (lost 5387) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury -1256 · net -279 · threat 67 · provinces 1 · army 182441 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 100 · trade 350 · admin 50 · tribute 895 · upkeep 1508 · requisitions 99 · blockade 175 · admiralty 90
- DISPATCH: Sire — France holds a single province: Brittany. Paris is in Austria's hands. 8 corps still stand under our colours — Massena, Soult, Davout, Ney, Murat, Lannes, Bernadotte and the Emperor, 182,441 m…
  - RAIL balance_of_europe_shifted: Vienna System leads the current largest alignment at 58% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 21 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Ottoman Empire, Sweden and Naples rebuff Prussia (defensive alliance)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on both… · Mack's forces advance steadily. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,112, L… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archd…
  - ⚔ Archduke Charles (lost 4245) vs Massena (lost 4624) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 5112) vs Lannes (lost 1649, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 1774) vs Bernadotte (lost 5125) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - verbs: attack×3
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury -2031 · net -59 · threat 64 · provinces 1 (+0) · army 167065 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 100 · trade 350 · admin 50 · tribute 856 · upkeep 1249 · requisitions 99 · blockade 175 · admiralty 90
- DISPATCH: Sire — France holds a single province: Brittany. Paris is in Austria's hands. 8 corps still stand under our colours — Massena, Soult, Davout, Ney, Murat, Lannes, Bernadotte and the Emperor, 167,065 m…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches from Prussia, Naples and Denmark are rebuffed (open borders agreement)
  - LOG balance_of_europe_shifted: Vienna System leads the current largest alignment at 58% of active European bloc power.
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCha… · Mack's forces advance steadily. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 4,859, L… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu… · Mack faces a difficult fight. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack 3,133, Mura…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 851) vs Bernadotte (lost 6538) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 4859) vs Lannes (lost 1303, own corps) — Reinforcements from Napoleon bolstered Lannes's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 2211) vs Deroy (lost 4543) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - ⚔ Mack (lost 3133) vs Murat (lost 2368, own corps) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×4, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury -2544 · net +209 · threat 61 · provinces 1 (+0) · ceiling 3833 · army 151832 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 90
  - NET income 100 · trade 350 · admin 50 · tribute 860 · upkeep 985 · requisitions 99 · blockade 175 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as alliance.
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces strike with perfect coordination! Brutal stalemate between Mack and Lannes. Heavy casualties on both side… · Mack's forces advance steadily. Mack gains the advantage over Murat. Casualties: Mack 2,283, Murat's army 4,264. Both a…
  - ⚔ Mack (lost 3447) vs Lannes (lost 1366, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - ⚔ Mack (lost 2283) vs Murat (lost 2345, own corps) — Soult failed to arrive in time. Murat's army fought without expected support.
  - verbs: attack×2, move×1, wait×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury -2504 · net +449 · threat 58 · provinces 1 (+0) · ceiling 5644 · army 135327 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 86
  - NET income 100 · trade 350 · admin 50 · tribute 865 · upkeep 750 · requisitions 99 · blockade 175 · admiralty 90
- DISPATCH: Sire — the Empire has stood reduced 4 turns, and every province retaken would pay again. France holds a single province: Brittany. Paris is in Austria's hands. 8 corps still stand under our colours —…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected PapalStates's open borders agreement proposal

## Turn 5 — Late November 1805
  - MAILBOX #9 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #9 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Mack gains the advantage over Lannes. Casualties: Mack 1,964, Lannes's army 3,517. Both a… · Mack struggles in a costly engagement. Mack gains the advantage over Murat. Casualties: Mack 1,109, Murat's army 4,266.…
  - ⚔ Mack (lost 1964) vs Lannes (lost 1159, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Mack (lost 1109) vs Murat (lost 2346, own corps) — Soult never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×2, wait×1
  - ENDING — THE FALL OF THE EMPIRE: The Empire is reduced to Brittany alone — a province, not a realm. [THE ECLIPSE]
  -     ↳ Late November 1805 (turn 5) · register `fall` · TERMINAL — Load / Main Menu
  -     ↳ THE VERDICT — THE ECLIPSE: The Empire is smaller and poorer than it began. / Its enemies have learned that it can be beaten. / History will call it the beginning of the end.
  -     ↳ The Verdict of History: the eclipse.
  -     ↳ THE RECORD — battles 11 (0 won, 5 lost) · men lost 50,185, inflicted 33,871 · provinces taken 0, lost 0 · marshals fallen 0, taken 0 · coalitions faced 1 · peaces signed 0
  -     ↳ THE EXILE (abdication) — In late November 1805, with only Brittany left to govern, the Emperor signed his abdication at Fontainebleau. Austria and its allies sent him to Elba — a small island, a small court, and a sovereign who had once governed a continent.
  -     ↳ Davout and Lannes followed him to the boat. Bernadotte had long since stopped answering his letters.
  -     ↳ In 11 battles the Empire won 0 and lost 5; 33,871 of the enemy fell against 50,185 of our own. The Second Battle of Franconia was the worst day. One coalition stood against him — the Third Coalition.
  -     ↳ The Verdict of History: the eclipse. Talleyrand, who had served every government France had ever had, served the next one too.
- LEDGER treasury -2344 · net +548 · threat 57 · provinces 1 (+0) · ceiling 6114 · army 120052 · vassals Holland 90 · Kingdom of Italy 98 · Switzerland 80
  - NET income 100 · trade 350 · admin 50 · tribute 869 · upkeep 630 · requisitions 74 · blockade 175 · admiralty 90
- DISPATCH: Sire — the Empire has stood reduced 5 turns, and every province retaken would pay again. France holds a single province: Brittany. Paris is in Austria's hands. 8 corps still stand under our colours —…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Bavaria (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal
  - LOG ai_ai_proposal_refused: Spain, Ottoman Empire and Sweden rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia, Naples and Denmark (open borders agreement)
  - LOG ai_ai_proposal_refused: 14 approaches from Bavaria and Austria are rebuffed (open borders agreement)
  - GAME OVER reported — stopping

---
finished: **game-over** · commands 5 · popups 11 · battles 12
