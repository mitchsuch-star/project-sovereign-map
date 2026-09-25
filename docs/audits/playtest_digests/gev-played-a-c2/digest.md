# Playtest digest — gev-played-c2

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "grant", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 3 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` (dirty) · content `ccdea5f5afcf` · driver `339f0de8623d`
  - loaded save `save_c1.json` → Loaded: Autosave - Turn 3

## Turn 3 — Late October 1805
- CMD `propose open borders with Hesse` → ✓ Sire, regarding the Open Borders Agreement proposal to Hesse, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #5 → confirm
  - POPUP proposal_result: Talleyrand departs for the Hesse court with your Open Borders Agreement proposal. Expect a response by next turn. (1 DP spent) → display-only
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (18,889; 73,021 if all march, up to 101,782 if every corps arrives) vs Archduke Charles (large force) at Tyrol — the balance of force looks even.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1949, own corps) vs Archduke Charles (lost 5769, own corps) — Davout, Lannes and Massena's timely arrival aided Ney. Murat and Deroy, however, were conspicuously absent.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (20,398) vs Archduke Charles (41,728 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 10016) vs Archduke Charles (lost 1142, own corps) — Murat stood alone, Sire. Ney and Deroy never came.
- CMD `Lannes, attack Archduke Charles` → ✓ MUSTER — Lannes (12,901; 21,254 if all march, up to 30,653 if every corps arrives) vs Archduke Charles (40,586 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 5805) vs Archduke Charles (lost 964, own corps) — Lannes stood alone, Sire. Ney, Bernadotte and Deroy never came.
- CMD `Davout, attack Archduke Charles` → ✓ Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.'
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' → trust
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 3 ended. Turn 4 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending!
  - ⚔ Archduke Charles (lost 3670) vs Massena (lost 3833) — Not one corps reached Massena. Ney was expected; Massena fought the battle single-handed.
  - verbs: break_square×1, attack×1, stance_change×1, fortify×1
- ENVOYS WAITING 2 · Hesse open borders · Britain settlement offer
- LEDGER treasury 5950 · net +2811 · threat 93 · provinces 28 · ceiling 45426 · army 158425 · vassals Bavaria 68 · Holland 97 · Kingdom of Italy 99 · Switzerland 94
  - NET income 3400 · trade 200 · admin 50 · tribute 1308 · upkeep 1676 · charges 281 · blockade 100 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Munich. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 1358 gold.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Hesse with a response.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_proposal_sent, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 15 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Hesse's open borders agreement proposal
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

---
finished: **completed** · commands 7 · popups 6 · battles 4
