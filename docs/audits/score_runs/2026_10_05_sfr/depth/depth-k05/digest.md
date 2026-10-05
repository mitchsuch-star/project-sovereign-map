# Playtest digest — depth-k05

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 25 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - loaded save `depth-k04_t3.json` → Loaded: depth-k04_t3

## Turn 25 — Late September 1806
- CMD `how much gold do we have?` → ✓ The treasury holds 14,466 gold, Sire. In: the provinces 2,744, trade 622, vassal tribute 225, the administration 50. Out: the army 952, the laws 650, the Charges of Empi…
- CMD `what are we paying Sardinia?` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `grant Massena a rente` → ✓ By Imperial decree, Marshal Massena is granted a rente of 40g/turn upon the treasury. With fees and arrears it will cost the crown 60g/turn — paper is dearer than land, …
- CMD `Masena, move to Limousin` → ✓ Massena moves from Lyonnais to Limousin
- CMD `Soult, march to Burgundy and then fortify` → ✓ Soult begins march to Burgundy. Moves to Burgundy. "Soult, march to Burgundy and then fortify." It will be done exactly, Sire. (1 AP — Soult executes precise orders with…
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Britain.
  - POPUP diplomatic_dialogue: mission #40 → start_mission
- CMD `how do I keep Austria out of the next league?` → ✓ Sire — Austria — relations −26: she would join. Russia and Britain pay her 800 gold a turn against us. The price to keep her out: Talleyrand brings her to −10 in 2 turns…
- CMD `Napoleon, review the troops` → ✗ "Sire, the Emperor Napoleon awaits your command, but I cannot parse this order. Might you mean 'Napoleon, scout' or 'Napoleon, defend'?" Berthier asks carefully.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 3 actions unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Davout [continues]: Davout fortifies Franche-Comte.
- ORDER Ney [completed]: Ney arrives at Lyonnais. Ney: "It is done. Point me at something that shoots back, Sire."
- ORDER Soult [active]: Soult is marching to Burgundy (0 turns remaining).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: Murat turns openly discontent (trust -3; expect defiance).
- LEDGER treasury 15964 · net +1705 · threat 35 · provinces 28 · ceiling 158000 · army 122427 · vassals Holland 87 · Switzerland 86
  - NET income 2751 · trade 622 · admin 50 · tribute 225 · upkeep 936 · charges 167 · occupation 30 · infrastructure 40 · rentes 120 · laws 650
- MISSION Improving Relations — Austria · net +8 a turn · ≈17 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
  - RAIL expedition_landed: THE LANDING: Paget has put 6,278 men ashore at Estonia.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Russia the loss of Uleaborg and 1 more province. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_auto_downgrade, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
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
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 26 — Early October 1806
- CMD `what happened last turn?` → ✓ This morning's dispatch leads with: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits. Overnight: Davout's fortifications decay: 5% → …
- CMD `how much gold do we have?` → ✓ The treasury holds 15,964 gold, Sire. In: the provinces 2,751, trade 622, vassal tribute 225, the administration 50. Out: the army 936, the laws 650, the Charges of Empi…
- CMD `Murat, move to Provence` → ✓ Murat moves from Lyonnais to Provence (54 lost to march)
- CMD `is Sardinia still in play?` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [continues]: Davout fortifies Franche-Comte.
- ORDER Soult [completed]: "Soult, march to Burgundy and then fortify" — executed as written. Soult arrives at Burgundy. Awaiting your next word.
- LEDGER treasury 17485 · net +1703 · threat 38 · provinces 28 (+0) · ceiling 159333 · army 120986 · vassals Holland 86 · Switzerland 86
  - NET income 2759 · trade 622 · admin 50 · tribute 225 · upkeep 928 · charges 185 · occupation 30 · infrastructure 40 · rentes 120 · laws 650
- MISSION Improving Relations — Austria · net +8 a turn · ≈16 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Russia would now join a league against us — relations −51. The price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design costs 1,368 gold and shortens the ro…
  - TURN EVENTS 3
- DIPLO +6 medium/low (law_enacted_abroad ×3, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG design_promoted: REVANCHE: Sweden swears to retake Uleaborg and 1 more — Russia is not forgiven
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 27 — Late October 1806
  - saved `depth-k05_t3` → Game saved: depth-k05_t3
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 5 actions unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Davout [continues]: Davout fortifies Franche-Comte.
- LEDGER treasury 19012 · net +2045 · threat 40 · provinces 28 (+0) · ceiling 189416 · army 119640 · vassals Holland 85 · Switzerland 86
  - NET income 2767 · trade 622 · admin 50 · tribute 562 · upkeep 912 · charges 204 · occupation 30 · infrastructure 40 · rentes 120 · laws 650
- MISSION Improving Relations — Austria · net +8 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the establishment stands 10,360 men under the ordinance, and the depots hold 99,130. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

---
finished: **completed** · commands 16 · popups 2 · battles 0
