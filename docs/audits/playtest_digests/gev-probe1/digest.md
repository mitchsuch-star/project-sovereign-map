# Playtest digest — gev-probe1

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` · content `ccdea5f5afcf` · driver `c29de0d04ee3`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `vassalize Austria` → ✓ Austria has been subjugated as a Puppet vassal of France (loyalty: 20). Marshals assimilated: Mack, ArchdukeCharles, ArchdukeJohn.
- CMD `vassalize Bavaria` → ✓ Bavaria has become a Satellite vassal of France (loyalty: 60). Marshals assimilated: Deroy.
- CMD `vassalize Hanover` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: PEACE).
- CMD `propose open borders with Saxony` → ✓ Sire, regarding the Open Borders Agreement proposal to Saxony, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → confirm
  - POPUP proposal_result: Talleyrand departs for the Saxony court with your Open Borders Agreement proposal. Expect a response by next turn. (1 DP spent) → display-only
- CMD `declare war on Hanover` → ✗ Talleyrand is currently en route to a foreign court. He cannot negotiate until he returns.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: nothing visible — Britain, Russia, Prussia and 5 other courts stirred, but their formations remain beyond our sight.
- ORDER Mack [continues]: Mack marches to Franconia. 1 region to Bohemia.
- ENVOYS WAITING 4 · Saxony open borders · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury -534 · net +2400 · threat 97 · provinces 28 · ceiling 70181 · army 332994 · vassals Austria 12 · Bavaria 61 · Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 3400 · trade 200 · admin 50 · tribute 2674 · upkeep 3734 · blockade 100 · admiralty 90
- DISPATCH: Supply cost you 2,446 men, at Franconia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Saxony with a response.
  - TURN EVENTS 2
- DIPLO +10 medium/low (diplomatic_carved_vassal_created ×2, diplomatic_proposal_sent, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_unrest, cs_tier_shift, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
  - MAILBOX #4 Saxony counter_offer_response: Saxony — Open Borders Agreement → activated
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Saxony, open_borders #5 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Prussia. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #2 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Saxony, open_borders #5 → reject
  - POPUP proposal_result: You have rejected Saxony's counter-proposal. Relations cooled slightly. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `vassalize Hanover` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: PEACE).
- CMD `invest in Bavaria` → ✗ Insufficient gold (-534/200 required).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: nothing visible — Britain, Russia, Prussia and 5 other courts stirred, but their formations remain beyond our sight.
- ORDER Mack [completed]: The order was "the road home — safe passage granted by the peace". Mack arrives at Bohemia. I await further instruction.
- ENVOYS WAITING 2 · Denmark non aggression · Hesse non aggression
- LEDGER treasury 2707 · net +1571 · threat 85 · provinces 28 (+0) · ceiling 43614 · army 209934 · vassals Bavaria 52 · Holland 90 · Kingdom of Italy 90 · Switzerland 86
  - NET income 3400 · trade 200 · admin 50 · tribute 1424 · upkeep 3286 · charges 27 · blockade 100 · admiralty 90
- DISPATCH: Sire — Austria is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Austria has rebelled against France. It is war.
  - TURN EVENTS 2
- DIPLO +6 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_ai_ai_treaty, cs_tier_shift, agenda_shift, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Bavaria joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Austria has broken free of France. War.
  - LOG ai_ai_proposal_refused: 2 approaches from Britain and Prussia are rebuffed (defensive alliance)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Russia and Austria (Non-Aggression Pact)
  - LOG ai_ai_proposal_refused: 14 approaches from Prussia, Naples and Denmark are rebuffed (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Ottoman's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

---
finished: **completed** · commands 11 · popups 10 · battles 0
