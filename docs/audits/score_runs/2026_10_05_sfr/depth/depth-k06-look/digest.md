# Playtest digest — depth-k06-look

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 27 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - loaded save `depth-k05_t3.json` → Loaded: depth-k05_t3

## Turn 27 — Late October 1806
- CMD `where is Soult?` → ✓ Marshal Soult stands at Burgundy with 20,426 men (morale 87).
- CMD `is Soult fortified?` → ✓ No, Sire — Soult — 20,426 men at Burgundy, morale 87.
- CMD `where is Massena?` → ✓ Marshal Massena stands at Limousin with 11,819 men (morale 15).
- CMD `how is Massena's morale?` → ✓ Massena's morale is 15 — low, Sire. A turn of drill, out of the enemy's reach, restores it.
- CMD `who holds Provence?` → ✓ Provence is held by Spain.
- CMD `where is Murat?` → ✓ Marshal Murat stands at Provence with 5,444 men (morale 21).
- CMD `what orders are standing?` → ✓ Standing orders, Sire: Davout: Hold at Franche-Comte.
- CMD `how many diplomatic points do I have?` → ✓ Talleyrand holds 6 diplomatic points of 6; what he leaves unspent carries one turn, to at most 7. Today 5 of 5 orders remain, and 2 of 2 administrative actions.
- CMD `what is the sponsorship of Sardinia costing us?` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `how many actions do I have left?` → ✓ Talleyrand holds 6 diplomatic points of 6; what he leaves unspent carries one turn, to at most 7. Today 5 of 5 orders remain, and 2 of 2 administrative actions.
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 5 actions unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Davout [continues]: Davout fortifies Franche-Comte.
- LEDGER treasury 19012 · net +2045 · threat 40 · provinces 28 · ceiling 189416 · army 119640 · vassals Holland 85 · Switzerland 86
  - NET income 2767 · trade 622 · admin 50 · tribute 562 · upkeep 912 · charges 204 · occupation 30 · infrastructure 40 · rentes 120 · laws 650
- MISSION Improving Relations — Austria · net +8 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the establishment stands 10,360 men under the ordinance, and the depots hold 99,130. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG design_promoted: REVANCHE: Sweden swears to retake Uleaborg and 1 more — Russia is not forgiven
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG sponsorship_granted: France sponsors Sardinia against Austria (200g/turn)
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 45 to 22.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Prussia sign a Defensive Alliance
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Austria (defensive alliance)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

---
finished: **completed** · commands 11 · popups 0 · battles 0
