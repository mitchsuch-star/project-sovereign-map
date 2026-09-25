# Playtest digest — gev-played-c5

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "grant", "settlement": "decline", "decline_from": "Hanover"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 7 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` (dirty) · content `ccdea5f5afcf` · driver `196c4ee545c1`
  - loaded save `save_c4.json` → Loaded: Autosave - Turn 7

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #8 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #14 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_proposal #17 → grant the petition
  - POPUP diplomatic_dialogue: Switzerland, client_petition → (stale passthrough — #17 already answered this chain)
  - POPUP diplomatic_dialogue: Prussia, open_borders #14 → accept
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond -15 → 5 (+0 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #17 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `invest in Hesse` → ✓ Invested in Hesse: +10 loyalty (48 → 58). Cost: 1 DP + 200g. Cooldown: 3 turns.
- CMD `Deroy, attack Archduke Charles` → ✓ MUSTER — Deroy (20,896) vs Archduke Charles (19,842 men) at Tyrol — the balance of force looks even.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Deroy (lost 2999) vs Archduke Charles (lost 1295) — Not one corps reached Deroy. Bernadotte was expected; Deroy fought the battle single-handed.
- CMD `Soult, attack Hanover` → ✓ Soult assaults the Hanover garrison! Garrison: 10,000 -> 5,000 (-5,000). Soult loses 2,173 troops. Garrison holds — 5,000 defenders remain.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: shadow_command, Marshal Davout asks for a command → detach
  -     ↳ Davout straightens. "You will not regret it, Sire." March him to Lyonnais and the front is his — the order is…
  - POPUP diplomatic_dialogue: Hanover, armistice_losing #18 → reject
  - POPUP proposal_result: You have rejected Hanover's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Hanover armistice losing
- LEDGER treasury 15220 · net +2024 · threat 85 · provinces 29 · ceiling 29507 · army 118031 · vassals Bavaria 88 · Hesse 51 · Holland 94 · Saxony 48 · Switzerland 94
  - NET income 3425 · trade 387 · admin 50 · tribute 1256 · upkeep 904 · charges 1871 · occupation 35 · blockade 194 · admiralty 90
- DISPATCH: Sire — Deroy, crowned three turns ago, has been beaten in the field — and the laurels sit vacant.
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Hanover has arrived with a proposal.
  - TURN EVENTS 10
- DIPLO +5 medium/low (diplomatic_treaty_signed ×3, diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Hanover's armistice proposal
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Spain swears to retake Aragon and 1 more — Britain is not forgiven
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Prussia are rebuffed (open borders agreement)
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
finished: **completed** · commands 5 · popups 13 · battles 1
