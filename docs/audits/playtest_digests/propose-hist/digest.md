# Playtest digest — propose-hist

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Massena. Heavy casual…
  - ⚔ Archduke Charles (lost 4431) vs Massena (lost 5919) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2485 · net +1962 · threat 68 · provinces 28
  - NET income 3400 · trade 350 · tribute 895 · upkeep 2450 · charges 18 · blockade 175 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: A Prussia envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Ottoman envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Portugal envoy has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 1
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: PEACE → OPEN_BORDERS with Prussia. → display-only
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #5 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 action(s) unused) Turn 3 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles … · Mack engages in solid combat. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,166, Lan… · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: Casualties: ArchdukeCharles's army 1,209, Deroy 8,256. Both armies remain in the field. Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 2437) vs Deroy (lost 5959) — The battle unfolded without particular distinction.
  - ⚔ Mack (lost 5166) vs Lannes (lost 1487) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 844, own corps) vs Deroy (lost 8256) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×4, stance_change×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4493 · net +2060 · threat 66 · provinces 28 (+0)
  - NET income 3382 · trade 450 · tribute 901 · upkeep 2300 · charges 108 · blockade 225 · admiralty 90
- DISPATCH: Sire — Carniola has been taken by Austria.
  - RAIL diplomatic_ai_proposal: A Denmark envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A Saxony envoy has arrived with a proposal.
  - TURN EVENTS 1
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #8 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's assault collapses into chaos! ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archdu… · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination) · Mack launches a devastating assault! Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 4,0… · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: Casualties: ArchdukeJohn's army 910, Bernadotte 4,562. Both armies remain in the field. Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1192, own corps) vs Bernadotte (lost 6439) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke John (lost 97, own corps) vs Deroy (lost 3383) — Deroy's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Mack (lost 4064) vs Lannes (lost 1982) — Lannes fought without Soult and Napoleon's support. The roads, or the will, proved insufficient.
  - ⚔ Archduke John (lost 280, own corps) vs Bernadotte (lost 4562) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - verbs: attack×4, wait×1, recruit×1
  - POPUP proposal_result: Russia has rejected our Peace Treaty. → display-only
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6357 · net +2401 · threat 64 · provinces 28 (+0)
  - NET income 3364 · trade 525 · tribute 905 · upkeep 1834 · charges 256 · blockade 263 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: A Hesse envoy has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: A PapalStates envoy has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 2
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #11 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #12 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (7 pair(s) resolved). → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: grant_dotation×2, stance_change×1, fortify×1, wait×1, recruit×1
- LEDGER treasury 9524 · net +3025 · threat 64 · provinces 28 (+0)
  - NET income 3366 · trade 623 · tribute 910 · upkeep 1834 · charges 90
- DISPATCH: Bernadotte's army is recovering. Effectiveness penalty: -15%.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia: settlement ratified.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 2
  - LOG ai_ai_proposal_refused: 18 approaches rebuffed, chiefly from Austria and Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria, Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved.

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, wait×1
- LEDGER treasury 12555 · net +2995 · threat 64 · provinces 28 (+0)
  - NET income 3368 · trade 623 · tribute 914 · upkeep 1834 · charges 126
- DISPATCH: Bernadotte's army has fully recovered and is combat ready.
  - TURN EVENTS 2
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 6 — Early December 1805
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3
- LEDGER treasury 15557 · net +2966 · threat 64 · provinces 28 (+0)
  - NET income 3370 · trade 623 · tribute 919 · upkeep 1834 · charges 162
- DISPATCH: 2 satellites drifted — Holland and Switzerland.
  - TURN EVENTS 1

## Turn 7 — Late December 1805
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 18529 · net +2936 · threat 64 · provinces 28 (+0)
  - NET income 3372 · trade 623 · tribute 923 · upkeep 1834 · charges 198
- DISPATCH: 2 satellites drifted — Holland and Switzerland.
  - TURN EVENTS 1
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 8 — Early January 1806
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3
- LEDGER treasury 21472 · net +2908 · threat 64 · provinces 28 (+0)
  - NET income 3374 · trade 623 · tribute 928 · upkeep 1834 · charges 233
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - TURN EVENTS 1
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Ottoman, Sweden, Naples, Hanover, Sardinia alarmed (threat: 64)

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 24386 · net +2879 · threat 64 · provinces 28 (+0)
  - NET income 3376 · trade 623 · tribute 932 · upkeep 1834 · charges 268
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - TURN EVENTS 1

## Turn 10 — Early February 1806
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3
- LEDGER treasury 27272 · net +2851 · threat 64 · provinces 28 (+0)
  - NET income 3378 · trade 623 · tribute 937 · upkeep 1834 · charges 303
- DISPATCH: 2 satellites drifted — Holland and Switzerland.
  - TURN EVENTS 1
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 29200 · net +1866 · threat 64 · provinces 28 (+0)
  - NET income 3380 · trade 587 · tribute 937 · upkeep 1834 · charges 870 · blockade 294 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. He tears up the Peace Treaty to do it.
  - RAIL diplomatic_ai_proposal: A Naples envoy has arrived with a proposal.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_alliance_cascade: Bavaria enters the war via alliance with France.
  - RAIL diplomatic_offensive_cascade: Russia has joined Britain's war against France, honoring their alliance.
  - RAIL diplomatic_offensive_cascade: Austria has joined Britain's war against France, honoring their alliance.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 4 allied courts poised to follow.
  - RAIL +16 more
  - TURN EVENTS 1
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG diplomatic_treaty_broken: Austria was forced to break the Peace Treaty with France (cascade).
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal KingdomOfItaly joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG coalition_declared: The Fourth Austria Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Naples, Russia, Sardinia, Sweden
  - LOG ai_ai_proposal_refused: Austria, Spain and Bavaria rebuff Prussia (defensive alliance)

## Turn 12 — Early March 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #14 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Bernadotte. Heavy casualties … · Mack's forces advance steadily. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack 4,446, Mu… · ArchdukeJohn attacks with overwhelming force. Brutal stalemate between ArchdukeJohn and Lannes. Heavy casualties on bot…
  - ⚔ Archduke Charles (lost 3318) vs Bernadotte (lost 582) — Massena arrived to reinforce Bernadotte, but Lannes failed to reach the field in time.
  - ⚔ Mack (lost 4446) vs Murat (lost 1724) — Reinforcements from Napoleon bolstered Murat's position — though Soult never arrived, Sire.
  - ⚔ Archduke John (lost 2619) vs Lannes (lost 803) — Soult failed to arrive in time. Lannes's army fought without expected support.
  - verbs: attack×3, move×1, wait×1
  - POPUP proposal_result: Russia has rejected our Peace Treaty. → display-only
- LEDGER treasury 30664 · net +1880 · threat 62 · provinces 28 (+0)
  - NET income 3352 · trade 587 · tribute 937 · upkeep 1504 · charges 1158 · blockade 294 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 3
  - LOG ai_ai_proposal_refused: 12 approaches from Denmark and Bavaria are rebuffed (open borders agreement)

## Turn 13 — Late March 1806
- CMD `propose peace with Sardinia` → ✓ Sire, regarding the Peace Treaty proposal to Sardinia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #15 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Sardinia while allied with Spain (who is …)
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 action(s) unused) Turn 14 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn faces a difficult fight. Lannes holds the line. Casualties: ArchdukeJohn 3,249, Lannes's army 1,145. Both … · Mack struggles in a costly engagement. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack's… · ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Lannes. Casualties: ArchdukeCharles…
  - ⚔ Archduke John (lost 3249) vs Lannes (lost 392) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Mack (lost 2585, own corps) vs Lannes (lost 1097) — Soult failed to arrive in time. Lannes's army fought without expected support.
  - ⚔ Archduke Charles (lost 1955) vs Lannes (lost 1273) — Lannes fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×3, move×2, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 31091 · net +764 · threat 60 · provinces 27 (-1)
  - NET income 3139 · trade 587 · tribute 937 · upkeep 1234 · charges 2292 · contributions 39 · blockade 294 · admiralty 90
- DISPATCH: Sire — Corsica has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Corsica.
  - TURN EVENTS 8
  - LOG british_subsidy: Britain's gold: 300g reaches Sardinia
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Sardinia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG ai_ai_proposal_refused: 5 approaches from Britain and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 15 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG ai_ai_proposal_refused: 15 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Britain and Sweden (Open Borders Agreement)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 14 — Early April 1806
- CMD `propose peace with Sweden` → ✓ Sire, regarding the Peace Treaty proposal to Sweden, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #16 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Sweden while allied with Spain (who is st…)
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn faces a difficult fight. Brutal stalemate between ArchdukeJohn and Bernadotte. Heavy casualties on both si… · Mack engages in solid combat. Mack gains the advantage over Lannes. Casualties: Mack's army 1,372, Lannes's army 4,320.… · ArchdukeJohn holds them at Franche-Comte while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: Casualties: ArchdukeJohn's army 1,115, Murat 4,197. Both armies remain in the field. Franche-Comte has been captured by Austria!
  - ⚔ Archduke John (lost 1031) vs Bernadotte (lost 524) — Soult never reached the guns. The battle was decided without them, Sire.
  - ⚔ Mack (lost 1044, own corps) vs Lannes (lost 2433) — Soult never reached the guns. The battle was decided without them, Sire.
  - ⚔ Archduke John (lost 273, own corps) vs Murat (lost 4197) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×3, grant_pension×1, wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 31256 · net +602 · threat 58 · provinces 26 (-1)
  - NET income 3100 · trade 587 · tribute 937 · upkeep 1032 · charges 2656 · blockade 294 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. Mack's corps of 28,389 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garr…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle Britain vs France.
  - TURN EVENTS 8
  - LOG british_subsidy: Britain's gold: 300g reaches Sardinia
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 15 — Late April 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #18 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Hanover + Naples + Russia + Sardinia + Sweden (32 pair(s) resolved). → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 action(s) unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 34655 · net +3359 · threat 58 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 1008 · charges 391
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of Britain + Russia + Austria + Sweden + Naples + Hanover + Sardinia vs France + Spain + Bavaria + Holland + KingdomOfItaly + Switzerland:…
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 8
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Sweden has left the coalition.
  - LOG coalition_member_left: Naples has left the coalition.
  - LOG coalition_member_left: Hanover has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved.

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 38042 · net +3346 · threat 58 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 980 · charges 432
- DISPATCH: Lannes's army has fully recovered and is combat ready.
  - TURN EVENTS 6
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (defensive alliance)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 41400 · net +3318 · threat 58 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 968 · charges 472
- DISPATCH: Sire — Marshal Murat's household goes unpaid. His patience erodes with his purse.
  - TURN EVENTS 4
  - LOG ai_ai_proposal_refused: Austria, Spain and Bavaria rebuff Prussia (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 44726 · net +3286 · threat 58 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 960 · charges 512
- DISPATCH: Sire — Marshal Murat's household goes unpaid. His patience erodes with his purse.
  - TURN EVENTS 3
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Austria (defensive alliance)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 48020 · net +3254 · threat 58 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 952 · charges 552
- DISPATCH: Sire — Marshal Murat has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Bavaria (open borders agreement)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Lannes: They settle into cold war.
- LEDGER treasury 51290 · net +3231 · threat 58 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 936 · charges 591
- DISPATCH: Sire — 7 turns without settlement on Marshal Murat. A rente would close it today; the arrears will not close themselves.
  - TURN EVENTS 5

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 54537 · net +3208 · threat 58 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 920 · charges 630
- DISPATCH: Sire — Marshal Murat's claim is 8 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 57753 · net +3177 · threat 58 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 912 · charges 669
- DISPATCH: Sire — Marshal Murat's claim is 9 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (defensive alliance)

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 60954 · net +3163 · threat 58 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 888 · charges 707
- DISPATCH: Sire — Marshal Murat's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Sardinia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: Austria, Spain and Bavaria rebuff Prussia (defensive alliance)

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 64117 · net +3125 · threat 56 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 888 · charges 745
- DISPATCH: Sire — Marshal Murat's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 67258 · net +3103 · threat 54 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 872 · charges 783
- DISPATCH: Sire — Marshal Murat's claim is 12 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 70369 · net +3074 · threat 52 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 864 · charges 820
- DISPATCH: Sire — Marshal Murat's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 73451 · net +3045 · threat 50 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 856 · charges 857
- DISPATCH: Sire — Marshal Murat's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 76504 · net +3016 · threat 48 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 848 · charges 894
- DISPATCH: Sire — Marshal Murat's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 79528 · net +2988 · threat 46 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 840 · charges 930
- DISPATCH: Sire — Marshal Murat's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: Austria, Spain and Bavaria rebuff Prussia (defensive alliance)

## Turn 30 — Early December 1806
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 82524 · net +2960 · threat 44 · provinces 26 (+0)
  - NET income 3100 · trade 671 · tribute 937 · upkeep 832 · charges 966
- DISPATCH: Sire — Marshal Murat's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2

---
finished: **completed** · commands 38 · popups 27 · battles 17
