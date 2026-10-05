# Playtest digest — depth-c06

seed `historical` · llm `anthropic` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "continue", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 11 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - loaded save `depth-c05_t3.json` → Loaded: depth-c05_t3

## Turn 11 — Late February 1806
- CMD `who can I commission as a new marshal?` → ✓ The bench, Sire — each at his price, one administrative action apiece, the treasury holding 4,674: Mortier 4,000g; Grouchy 4,500g; Suchet 5,500g (Commissioning Suchet co…
- CMD `commission Augereau` → ✓ Marshal Augereau accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Massena (Friendly).
- CMD `Napoleon, drill` → ✗ Napoleon cannot drill with enemy forces nearby! Archduke Charles is at Tyrol, just one region away.
- CMD `Ney, march to Gascony and drive Paget out` → ✓ Ney begins march to Gascony. Route: Lorraine → Orleanais → Burgundy → Limousin → Gascony. Moves to Lorraine. Ney: "Good. An army rots standing still."
- CMD `Lannes, unfortify and march on Bohemia` → ✓ Lannes abandons fortified position at Munich. Army is now mobile.
- CMD `who deserves a reward?` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `how is Murat's morale?` → ✓ Murat's morale is 11 — low, Sire. A turn of drill, out of the enemy's reach, restores it.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- SPENT 3500g on this turn's orders
- enemy phase: 6 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget attacks with overwhelming force. Brutal stalemate between Paget and Augereau. Heavy casualties on both sides: Pag… · Wellesley marches from Piedmont into Provence unopposed! (50 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley marches from Piedmont into Provence unopposed! (50 lost to march) Captured: France → Britain
  - ⚔ Paget (lost 696) vs Augereau (lost 898) — Neither Augereau nor Paget could claim the field. The armies remain locked.
  - verbs: attack×2, form_square×2, unfortify×1, move×1
- ORDER Napoleon [continues]: The Emperor holds Munich. He will not move until you say so.
- ORDER Ney [active]: Ney is marching to Gascony (4 turns remaining).
- LEDGER treasury 2751 · net +1534 · threat 56 · provinces 28 · ceiling 13002 · army 115374 · vassals Holland 84 · Switzerland 78
  - NET income 2566 · trade 611 · admin 50 · tribute 337 · upkeep 896 · charges 112 · contributions 40 · occupation 60 · blockade 382 · admiralty 90 · laws 450
- MISSION Improving Relations — Prussia · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Provence has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (open borders agreement)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 14 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 12 — Early March 1806
- CMD `what orders are standing?` → ✓ Standing orders, Sire: Ney: March Gascony (4 turns left); Napoleon: Hold at Munich.
- CMD `where is Wellesley?` → ✓ Wellesley of Britain was reported at Provence — screening force.
- CMD `Massena, drill` → ✗ Massena cannot drill with enemy forces nearby! Mack is at Tyrol, just one region away.
- CMD `Murat, drill` → ✗ Murat cannot drill with enemy forces nearby! Mack is at Tyrol, just one region away.
- CMD `what does the Train des Equipages do?` → ✓ The laws of state, Sire. In force: the Grand Quartier Général, the Anticipated Class. The Train des Équipages: 3,500 gold, then 200 gold a turn — the treasury holds 2,75…
- CMD `Talleyrand, propose a white peace to Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #22 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 5 actions unused) Turn 13 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget's forces advance steadily. Brutal stalemate between Paget and Augereau. Heavy casualties on both sides: Paget 544…
  - ⚔ Paget (lost 544) vs Augereau (lost 752) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×1
- ORDER Napoleon : Berthier: 'Cannon fire at Swabia, Sire. Investigate?'
- ORDER Ney [interrupted]: Ney hears cannon fire! Abandoning orders — rushing to Swabia! Ney moves from Lorraine to Swabia (344 lost to march, 452 to enemy harassment)
  - POPUP strategic_interrupt: Napoleon, cannon_fire, Berthier: 'Cannon fire at Swabia, Sire. Investigate?' → investigate
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 4303 · net +1344 · threat 54 · provinces 28 (+0) · ceiling 13070 · army 112827 · vassals Holland 84 · Switzerland 77
  - NET income 2602 · trade 611 · admin 50 · tribute 337 · upkeep 872 · charges 352 · contributions 80 · occupation 30 · blockade 382 · admiralty 90 · laws 450
- MISSION Improving Relations — Prussia · net +7 a turn · ≈8 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Provence lies in enemy hands. Britain holds it.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: Spain rebuffs Bavaria (open borders agreement)

## Turn 13 — Late March 1806
  - MAILBOX #12 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #23 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
  - saved `depth-c06_t3` → Game saved: depth-c06_t3
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 5 actions unused) Turn 14 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Swabia garrison! Garrison: 750 -> 375 (-375). ArchdukeJohn loses 197 troops. Garrison holds —… · ArchdukeJohn assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,824 troops in the assa…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -91g, Bavaria -122g. Captured: Bavaria → Austria
  - verbs: attack×2, fortify×1, break_square×1
- ENVOYS WAITING 1 · Prussia alliance
- LEDGER treasury 5674 · net +1374 · threat 52 · provinces 28 (+0) · ceiling 14455 · army 111771 · vassals Holland 84 · Switzerland 76
  - NET income 2606 · trade 611 · admin 50 · tribute 562 · upkeep 856 · charges 574 · contributions 73 · occupation 30 · blockade 382 · admiralty 90 · laws 450
- MISSION Improving Relations — Prussia · net +7 a turn · ≈7 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the enemy has stood on our ground 8 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,792 gold. Prussia is now free to look elsewhere.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

---
finished: **completed** · commands 16 · popups 4 · battles 2
