# Playtest digest — depth-c05

seed `historical` · llm `anthropic` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "continue", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 9 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - loaded save `depth-c04_t3.json` → Loaded: depth-c04_t3

## Turn 9 — Late January 1806
- CMD `what borders Nivernais?` → ✓ Nivernais borders Bern, Burgundy, Franche-Comte, Lorraine and Orleanais, Sire.
- CMD `what borders Burgundy?` → ✓ Burgundy borders Bern, Champagne, Ile-de-France, Limousin, Lyonnais, Nivernais, Orleanais and Savoy, Sire.
- CMD `Davout, move to Munich` → ✓ Davout moves from Franconia to Munich (1,282 lost to march)
- CMD `Lannes, move to Munich` → ✓ Lannes moves from Franconia to Munich (245 lost to march)
- CMD `Napoleon, move to Munich and stay with Davout` → ✓ Napoleon moves from Swabia to Munich (110 lost to march)
- CMD `Soult, fortify Milan` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max …
- CMD `Ney, move to Swabia` → ✗ Not enough actions! Need 1, have 0 — Ney cannot march to Swabia today.
- CMD `Soult, recruit infantry at Milan` → ✗ Berthier advises caution. 'Milan is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `how is Napoleon's morale?` → ✓ Napoleon's morale is 0 — low, Sire. A turn of drill, out of the enemy's reach, restores it.
- CMD `end turn` → ✓ Turn 9 ended. Turn 10 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×1
- LEDGER treasury 3109 · net +1553 · threat 60 · provinces 29 · ceiling 13981 · army 113076 · vassals Holland 84 · Switzerland 80
  - NET income 2725 · trade 611 · admin 50 · tribute 337 · upkeep 880 · charges 158 · contributions 150 · occupation 60 · blockade 382 · admiralty 90 · laws 450
- MISSION Improving Relations — Prussia · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, coercive_demand)
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
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `where is Archduke Charles?` → ✓ Archduke Charles of Austria is at Tyrol — 26,827 men, confirmed.
- CMD `is Munich safe?` → ✓ Munich is Bavaria's, Sire; Davout's 25,062, Lannes's 11,766 and Napoleon's 5,311 stand there beside a garrison of 10,000. Threats we can see: Archduke Charles of Austria…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attac…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Tyrol instead.) → insist
- CMD `Napoleon, drill your guard` → ✓ Napoleon will hold Munich. Holding position. (1 AP — the Emperor commands in his own name.)
- CMD `Ney, defend Swabia` → ✓ Ney grumbles about defensive orders but complies. Ney shifts to DEFENSIVE stance at Rhineland. Effect: -10% attack, +15% defense.
- CMD `Massena, drill his corps back into shape` → ✗ Not enough actions! Need 1, have 0 — Massena cannot drill today.
- CMD `what would Britain accept for peace?` → ✓ A bare peace put to Britain today scores 30 — COUNTER_OFFER, Sire. The sticking point appears to be the weight of the bloc pressing against them. The settlement table (F…
- CMD `end turn` → ✓ Turn 10 ended. Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ORDER Napoleon [active]: Napoleon is holding position at Munich.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 4674 · net +1333 · threat 58 · provinces 29 (+0) · ceiling 13801 · army 112156 · vassals Holland 84 · Switzerland 79
  - NET income 2729 · trade 611 · admin 50 · tribute 337 · upkeep 872 · charges 390 · contributions 150 · occupation 60 · blockade 382 · admiralty 90 · laws 450
- MISSION Improving Relations — Prussia · net +7 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Piedmont.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 7
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 11 — Late February 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #21 → reject_settlement_offer
  - saved `depth-c05_t3` → Game saved: depth-c05_t3
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 5 actions unused) Turn 12 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Piedmont into Provence unopposed! (50 lost to march) Captured: France → Britain · Mack struggles in a costly engagement. Murat holds the line. Casualties: Mack 8,069, Murat's army 1,438. Both armies re…
  - 🏴 Britain: Wellesley marches from Piedmont into Provence unopposed! (50 lost to march) Captured: France → Britain
  - ⚔ Mack (lost 8069) vs Murat (lost 268, own corps) — Reinforcements! Napoleon marched onto the field beside Murat. The enemy's advantage melted away.
  - verbs: attack×2, unfortify×1, form_square×1
- ORDER Napoleon [active]: Napoleon answered the guns this turn and stands at Milan; his position resumes next turn.
- LEDGER treasury 5848 · net +1050 · threat 56 · provinces 28 (-1) · ceiling 12846 · army 109158 · vassals Holland 85 · Switzerland 79
  - NET income 2561 · trade 611 · admin 50 · tribute 337 · upkeep 840 · charges 577 · contributions 110 · occupation 60 · blockade 382 · admiralty 90 · laws 450
- MISSION Improving Relations — Prussia · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Provence has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

---
finished: **completed** · commands 20 · popups 2 · battles 1
