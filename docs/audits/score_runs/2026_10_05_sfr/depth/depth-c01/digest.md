# Playtest digest — depth-c01

seed `historical` · llm `anthropic` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `Massena, dig in at Milan and hold the line` → ✓ Massena will hold Milan. Holding position. Massena: "I will hold. They had best not come close enough to tempt me." (2 AP — a standing strategic order to hold this groun…
- CMD `Davout, attack Mack at Swabia` → ✓ Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.) → trust
- CMD `Soult, attack Mack as well` → ✗ Not enough actions! Need 1, have 0 — Soult cannot attack Mack today.
- CMD `Ney, attack Mack if he is still standing` → ✗ Berthier sets down his pen. "Sire, that is a contingency, not an order — I have no way to hold a dispatch until 'if he is still standing' comes to pass. Nothing has been…
- CMD `what does Prussia want?` → ✓ Prussia pursues The Hanoverian Prize, Sire. Napoleon dangles the Electorate at Schoenbrunn; Berlin covets it openly. The buy-Prussia lever. The provinces in question: Ha…
- CMD `Talleyrand, improve relations with Prussia` → ✓ Sire, I shall begin efforts to improve relations with Prussia. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #1 → start_mission
- CMD `enact the Anticipated Class` → ✓ The Anticipated Class (the senatus-consultes calling the class early, 1806–07): The Senate calls each year's conscripts before their time: infantry manpower returns 25% …
  - POPUP clarification: The Council of State, The Anticipated Class (the senatus-consultes calling the class early, 1806–07): The Senate calls each year's conscripts before their time: infantry manpower returns 25% faster. 15 authority now, then 150 gold a turn. Authority 100 → 85 — the marshals' calm holds above 70. The treasury holds 800 gold. Enact it? (yes / no) → 1 (first option: Enact the Anticipated Class)
- CMD `end turn` → ✓ Turn 1 ended. Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Brutal stalemate between Archduke Charles and Massena. Heavy casualties o…
  - ⚔ Archduke Charles (lost 4747) vs Massena (lost 5557) — Stalemate. Massena and Archduke Charles glare at each other across the field. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: attack×1, wait×1
- ORDER Massena [active]: Massena is holding position at Milan.
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1474 · net +976 · threat 68 · provinces 28 · ceiling 25689 · army 183443 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2450 · blockade 219 · admiralty 90 · laws 150
- MISSION Improving Relations — Prussia · net +8 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +9 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_mission_progress, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #3 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `what happened at Swabia?` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `where is Mack now?` → ✓ Mack of Austria was reported at Swabia — large force.
- CMD `Murat, pursue Mack` → ✓ Murat pursues Mack (at Swabia). Mack spotted at Swabia! Engaging!
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 4252, own corps) vs Mack (lost 9810) — Reinforcements from Ney and Lannes bolstered Murat's position — though Soult and Napoleon never arrived, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `Lannes, march to Swabia` → ✓ Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' Berthier adds: Murat and Napoleon would answer the guns — Lannes 16,957, 35,833 with the muster …
  - POPUP strategic_interrupt: Lannes, contact_bad_odds, Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' Berthier adds: Murat and Napoleon would answer the guns — Lannes 16,957, 35,833 with the muster committed, against Mack (42,190 men). → attack_anyway
  - ↳ Lannes attacks Mack and wins! Continuing his march. MUSTER — Lannes (16,957; expect about 42,734 with the corps likely to arrive, up to 43,430 if all march) vs Mack (42,190 men) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 2594, own corps) vs Mack (lost 9502) — Murat and Napoleon's timely arrival aided Lannes. Soult and Bernadotte, however, were conspicuously absent. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Napoleon, march to Swabia and take command there` → ✗ Napoleon is engaged with Mack and cannot begin a strategic march. Deal with the engagement first.
- CMD `Bernadotte, scout Munich` → ✓ Bernadotte scouts Munich: Controlled by Bavaria. Terrain: Mountains (+25% defense). No field army stands there. Garrison: 10,000 (Bavaria's).
- CMD `how is the treasury?` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Massena. Casualties: Archdu… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Ch… · Deroy marches from Franconia into Swabia unopposed! (308 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: Deroy marches from Franconia into Swabia unopposed! (308 lost to march) Captured: Austria → Bavaria
  - ⚔ Archduke Charles (lost 3717) vs Massena (lost 5310, own corps) — Massena was close. A period of drilling could have changed the outcome. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 2800) vs Teulie (lost 1425, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×3, retreat×1, stance_change×1, wait×1
- ORDER Lannes [active]: Lannes is marching to Swabia (1 turn remaining).
- ORDER Murat [active]: Murat is pursuing Mack (0 turns remaining).
- ORDER Massena [continues]: Massena hears cannon fire at Swabia but cannot answer it — Cannot move into Munich - enemy forces present! Use ATTACK to engage Mack. His position co…
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2034 · net +1622 · threat 74 · provinces 28 (+0) · ceiling 28887 · army 161645 · vassals Holland 97 · Kingdom of Italy 95 · Switzerland 93
  - NET income 2590 · trade 450 · admin 50 · tribute 829 · upkeep 1774 · charges 2 · blockade 281 · admiralty 90 · laws 150
- MISSION Improving Relations — Prussia · net +7 a turn · ≈14 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +9% this morning; the courts have begun to notice that he can be beaten.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 14 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
  - saved `depth-c01_t3` → Game saved: depth-c01_t3
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Bernadotte. Casualties:…
  - ⚔ Archduke Charles (lost 1961) vs Bernadotte (lost 5025) — The engagement proceeded as one might expect, Sire.
  - verbs: attack×1, wait×1
- ORDER Lannes [active]: Lannes answered the guns this turn and stands at Munich; his march resumes next turn.
- ORDER Massena [active]: Massena answered the guns this turn and stands at Munich; his position resumes next turn.
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1275, own corps) vs Mack (lost 20266) — Lannes, Massena, Napoleon and Teulie arrived to reinforce Murat! The timely arrival swung the battle in our favor, Sire. — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 3694 · net +1875 · threat 80 · provinces 28 (+0) · ceiling 30471 · army 150010 · vassals Holland 96 · Kingdom of Italy 93 · Switzerland 90
  - NET income 2590 · trade 525 · admin 50 · tribute 833 · upkeep 1436 · charges 118 · blockade 329 · admiralty 90 · laws 150
- MISSION Improving Relations — Prussia · net +7 a turn · ≈13 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 5,025 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 8
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

---
finished: **completed** · commands 17 · popups 14 · battles 7
