# Playtest digest — AGD

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `88cd6378f016` (dirty) · content `08fe8a7fc9ef` · driver `2cbaf8455dd8`
  - loaded save `fixture_agd_tilsit.json` → Loaded: fixture_agd_tilsit

## Turn 1 — Late September 1805
- CMD `Davout, move to Posen` → ✓ Davout moves from Silesia to Posen. Posen falls to France! (was Prussia) (572 lost to march)
  - POPUP capture_choice[capture]: Posen, Davout → secure
  - saved `AGD_t1` → Game saved: AGD_t1
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 actions unused) Turn 2 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, garrison×1, wait×1
- ENVOYS WAITING 2 · Denmark open borders · Hesse open borders
- LEDGER treasury 20352 · net +270 · threat 66 · provinces 31 · ceiling 24295 · army 187976 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 3127 · trade 387 · admin 50 · tribute 937 · upkeep 2542 · charges 1255 · occupation 102 · blockade 242 · admiralty 90
- DISPATCH: Sire — General Hohenlohe of Prussia is destroyed at Silesia — his corps annihilated, his name struck from their order of battle.
  - RAIL diplomatic_offensive_cascade: Spain has joined France's war against Prussia, honoring their alliance.
  - RAIL diplomatic_offensive_cascade: Bavaria has joined France's war against Prussia, honoring their alliance.
  - RAIL diplomatic_war_declared: France has declared war on Prussia, with 2 allied courts poised to follow.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Prussia will not forgive France the loss of Silesia and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +12 medium/low (diplomatic_coalition_dissolved, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, diplomatic_ai_ai_treaty, cs_tier_shift, blockade_begins ×3)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 18 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign a Open Borders Agreement
  - LOG ai_ai_proposal_refused: 13 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 90 to 65; Britain and Prussia remain at war with us.

## Turn 2 — Early October 1805
  - LETTER Denmark: Open Borders Agreement → accept
  - LETTER Hesse: Open Borders Agreement → accept
- CMD `propose common peace with Prussia` → ✓ Sire, a white peace for France vs Britain + Prussia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent,…
  - POPUP diplomatic_dialogue: settlement_confirm #4 → (held for the script's own clicks)
  - TERMS (settlement_confirm PROPOSE): peace
- CMD `@settlement_demand_add {"nation": "Prussia", "group": "demand", "clause_type": "create_client", "tag": "DuchyOfWarsaw"}` → ✓ Demanded the erection of Duchy of Warsaw.
  - POPUP diplomatic_dialogue: settlement_confirm #5 → (held for the script's own clicks)
  - TERMS (settlement_confirm PROPOSE): peace, Duchy of Warsaw from Prussia (Posen)
- CMD `@settlement_demand_add {"nation": "Prussia", "group": "offer", "clause_type": "gold_indemnity", "amount": 6000}` → ✓ Offered 6000 gold from France.
  - POPUP diplomatic_dialogue: settlement_confirm #6 → (held for the script's own clicks)
  - TERMS (settlement_confirm PROPOSE): peace, Duchy of Warsaw from Prussia (Posen), gold_indemnity
- CMD `@submit_settlement_for_review` → ✓ Sire, the settlement of France vs Britain + Prussia cannot be ratified now: the terms claim a victory the field has not delivered. Revise terms or stand down before pres…
  - POPUP diplomatic_dialogue: settlement_confirm #7 → (held for the script's own clicks)
  - TERMS (settlement_confirm REVIEW): peace, Duchy of Warsaw from Prussia (Posen), gold_indemnity
- CMD `@seek_bilateral_peace` → ✓ Sire, this sets aside the joint settlement of France vs Britain + Prussia to treat with Prussia alone — every other court keeps its war. Shall I proceed?
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace #8 → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm #9 → confirm
  - POPUP proposal_result: Talleyrand departs for the Prussia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
  - saved `AGD_t2` → Game saved: AGD_t2
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP nation_proclamation: DuchyOfWarsaw → display-only
  - POPUP proposal_result: Prussia has accepted our Peace Treaty! → display-only
  - RATIFIED Prussia · PEACE · french_victory
- LEDGER treasury 15522 · net +1024 · threat 62 · provinces 30 (-1) · ceiling 40125 · army 187976 · vassals Duchy of Warsaw 60 · Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 3090 · trade 461 · admin 50 · tribute 964 · upkeep 2550 · charges 562 · occupation 50 · blockade 289 · admiralty 90
- DISPATCH: Sire — the war with Prussia is over. 1 corps stands on the wrong side of the new frontier. Berthier has given them the road home — Davout to Berlin. They have safe passage for 5 turns while they marc…
  - RAIL nation_created: By the fortune of arms and the pen at the table — Duchy of Warsaw is erected upon the map, a client of France.
  - RAIL peace_ratified: Peace ratified between France and Prussia.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Prussia with a response.
  - TURN EVENTS 1
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, status_quo_titled)
  - LOG ai_ai_proposal_refused: Prussia, Ottoman Empire and Sweden rebuff Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Spain and Duchy of Warsaw rebuff Austria (open borders agreement)
  - LOG design_promoted: REVANCHE: Prussia swears to retake Silesia and 2 more — France is not forgiven

## Turn 3 — Late October 1805
  - saved `AGD_t3` → Game saved: AGD_t3
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 16603 · net +989 · threat 61 · provinces 30 (+0) · ceiling 38674 · army 187976 · vassals Duchy of Warsaw 62 · Holland 99 · Kingdom of Italy 99 · Switzerland 95
  - NET income 3090 · trade 461 · admin 50 · tribute 1021 · upkeep 2550 · charges 654 · occupation 50 · blockade 289 · admiralty 90
- DISPATCH: Sire — Davout is no nearer home, and the safe passage leaves 2 turns to spare. After that his corps will be interned where it stands.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent ×2)
  - LOG ai_ai_proposal_refused: 4 approaches from Austria and Naples are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 4 approaches from Austria, Naples and Denmark are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Spain and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (defensive alliance)

---
finished: **completed** · commands 9 · popups 12 · battles 0
