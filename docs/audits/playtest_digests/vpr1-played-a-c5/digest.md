# Playtest digest — vpr1-played-a-c5

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "breakout", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "decline_from": "Hanover,Austria"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 7 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `08ed3d374c35` (dirty) · content `ac2f6d51ede2` · driver `196c4ee545c1`
  - loaded save `A2_save_4.json` → Loaded: Autosave - Turn 7

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #8 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #10 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #12 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Denmark. Your earlier answer was not delivered; the ma…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_proposal #14 → accept_ai_proposal
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
  - POPUP diplomatic_dialogue: Denmark, non_aggression → (stale passthrough — #14 already answered this chain)
  - POPUP diplomatic_dialogue: Prussia, open_borders #12 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
  - POPUP diplomatic_dialogue: Denmark, non_aggression #14 → accept
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `invest in Hesse` → ✓ Invested in Hesse: +10 loyalty (52 → 62). Cost: 1 DP + 200g. Cooldown: 3 turns.
- CMD `Deroy, attack Archduke Charles` → ✓ Deroy pursues Archduke Charles (at Tyrol). Moves to Tyrol. "Deroy attack ArchdukeCharles." Understood to the letter. (1 AP — Deroy executes precise orders with fewer cou…
- CMD `Soult, attack Hanover` → ✓ Soult assaults the Hanover garrison! Garrison: 10,000 -> 5,000 (-5,000). Soult loses 2,173 troops. Garrison holds — 5,000 defenders remain.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles delivers an effective strike. Deroy holds the line. Casualties: ArchdukeCharles 5,286, Deroy's army 1,9…
  - ⚔ Archduke Charles (lost 5286) vs Deroy (lost 566, own corps) — Lannes, Bernadotte, Massena and Napoleon's timely arrival bolstered Deroy's position. Well-coordinated, Sire.
  - verbs: attack×1
- ORDER Deroy [active]: Deroy is pursuing Archduke Charles (0 turns remaining).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Denmark, non_aggression #15 → accept
  -     ↳ refused: Denmark's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
  - POPUP diplomatic_dialogue: Hanover, armistice_losing #16 → reject
  - POPUP proposal_result: You have rejected Hanover's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 4 · Denmark non aggression · Hanover armistice losing · PapalStates open borders · Bavaria client petition
- LEDGER treasury 16177 · net +2067 · threat 97 · provinces 30 · ceiling 30771 · army 115109 · vassals Bavaria 80 · Hesse 58 · Holland 99 · Kingdom of Italy 100 · Saxony 53 · Switzerland 99
  - NET income 3425 · trade 350 · admin 50 · tribute 1512 · upkeep 888 · charges 2007 · occupation 110 · blockade 175 · admiralty 90
- DISPATCH: Sire — Tyrol has fallen to our arms. The tricolor flies over it this morning.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hanover has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Hanover's armistice proposal
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: Denmark rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 11 approaches from Prussia, Naples and Denmark are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

---
finished: **completed** · commands 5 · popups 12 · battles 1
