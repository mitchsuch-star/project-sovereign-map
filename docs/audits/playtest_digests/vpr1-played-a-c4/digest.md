# Playtest digest — vpr1-played-a-c4

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "breakout", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "decline_from": "Hanover,Austria"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 5 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `08ed3d374c35` (dirty) · content `ac2f6d51ede2` · driver `196c4ee545c1`
  - loaded save `A2_save_3.json` → Loaded: Autosave - Turn 5

## Turn 5 — Late November 1805
  - MAILBOX #4 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #6 → accept
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `propose open borders with Saxony` → ✓ Sire, regarding the Open Borders Agreement proposal to Saxony, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #7 → confirm
  - POPUP proposal_result: Talleyrand departs for the Saxony court with your Open Borders Agreement proposal. Expect a response by next turn. (1 DP spent) → display-only
- CMD `Deroy, attack Archduke John` → ✓ MUSTER — Deroy (21,560; expect about 39,151 with the corps likely to arrive, up to 42,963 if all march) vs Archduke John (11,903 men) at Tyrol — the balance of force loo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Deroy (lost 1535, own corps) vs Archduke John (lost 1419, own corps) — Reinforcements from Massena and Napoleon bolstered Deroy's position — though Bernadotte never arrived, Sire.
- CMD `Soult, move to Flanders` → ✓ Soult moves from Brabant to Flanders
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Franche-Comte. Defense bonus: +7% (grows +3% per t…
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn strikes back after successfully defending!
  - ⚔ Archduke John (lost 2763) vs Massena (lost 1028) — An exemplary engagement by Massena. The outcome was never in doubt.
  - verbs: attack×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Saxony, open_borders #10 → accept
  - POPUP proposal_result: You have accepted Saxony's counter-proposal. Treaty signed: Peace → Open Borders with Saxony. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression #8 → accept
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond -15 → 5 (+0 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 3 · Saxony open borders · Denmark non aggression · Switzerland client petition
- LEDGER treasury 11248 · net +2876 · threat 94 · provinces 28 · ceiling 39441 · army 126124 · vassals Bavaria 75 · Hesse 55 · Holland 98 · Kingdom of Italy 100 · Switzerland 100
  - NET income 3400 · trade 325 · admin 50 · tribute 1265 · upkeep 968 · charges 943 · blockade 163 · admiralty 90
- DISPATCH: Sire — Marshal Massena holds the field at Milan — Archduke John's corps is driven from Milan yet again — broken, and fleeing.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Saxony with a response.
  - TURN EVENTS 10
- DIPLO +3 medium/low (diplomatic_proposal_sent, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Prussia (open borders agreement)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 11 approaches from Prussia, Naples and Denmark are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

## Turn 6 — Early December 1805
- CMD `vassalize Saxony` → ✓ Saxony has become a Satellite vassal of France (loyalty: 60).
- CMD `Deroy, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Bernadotte, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Soult, move to Oldenburg` → ✓ Soult moves from Flanders to Oldenburg. Oldenburg falls to France! (was Hanover) (809 lost to march)
  - POPUP capture_choice[capture]: Oldenburg, Soult → secure
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #12 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Portugal open borders · Denmark non aggression
- LEDGER treasury 14026 · net +2428 · threat 97 · provinces 29 (+1) · ceiling 31977 · army 123886 · vassals Bavaria 79 · Hesse 52 · Holland 99 · Kingdom of Italy 100 · Saxony 57 · Switzerland 100
  - NET income 3425 · trade 325 · admin 50 · tribute 1501 · upkeep 960 · charges 1625 · occupation 35 · blockade 163 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_carved_vassal_created, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Prussia (defensive alliance)

---
finished: **completed** · commands 13 · popups 14 · battles 2
