# Playtest digest — depth-c05-look

seed `historical` · llm `anthropic` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 9 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - loaded save `depth-c04_t3.json` → Loaded: depth-c04_t3

## Turn 9 — Late January 1806
- CMD `where is Napoleon?` → ✓ the Emperor Napoleon stands at Swabia with 5,541 men (morale 0).
- CMD `where is Davout?` → ✓ Marshal Davout stands at Franconia with 26,913 men (morale 93).
- CMD `where is Lannes?` → ✓ Marshal Lannes stands at Franconia with 12,278 men (morale 61).
- CMD `where is Murat?` → ✓ Marshal Murat stands at Milan with 7,119 men (morale 11).
- CMD `where is Massena?` → ✓ Marshal Massena stands at Milan with 15,631 men (morale 0).
- CMD `where is Soult?` → ✓ Marshal Soult stands at Milan with 25,578 men (morale 100).
- CMD `where is Ney?` → ✓ Marshal Ney stands at Rhineland with 22,609 men (morale 94).
- CMD `where is Archduke Charles?` → ✓ Archduke Charles of Austria is at Tyrol — 27,166 men, confirmed.
- CMD `where is Mack?` → ✓ Mack of Austria is at Tyrol — 19,491 men, confirmed.
- CMD `where is Archduke John?` → ✓ Archduke John of Austria is at Tyrol — 7,858 men, confirmed.
- CMD `where is Paget?` → ✓ Paget of Britain was reported at Gascony — screening force.
- CMD `who is winning the war?` → ✓ War score, Sire — the Third Coalition (Britain, Austria and Russia) -3 (evenly matched). The breakdown is on the war banner on the left (click the war).
- CMD `what borders Paris?` → ✓ Paris borders Artois, Berry, Champagne, Limousin and Normandy, Sire.
- CMD `what borders Orleanais?` → ✓ Orleanais borders Ardennes, Brabant, Burgundy, Flanders, Ile-de-France, Lorraine, Nivernais and Picardy, Sire.
- CMD `what borders Lorraine?` → ✓ Lorraine borders Brabant, Franche-Comte, Nivernais, Orleanais, Rhineland and Swabia, Sire.
- CMD `is Paris safe?` → ✓ Paris is ours, Sire, held by a garrison of 25,000. Threats we can see: Paget of Britain is at Gascony, two marches off (screening force). It is safe for a turn or two, n…
- CMD `how many actions do I have left?` → ✓ Talleyrand holds 7 diplomatic points of 7; what he leaves unspent carries one turn, to at most 7. Today 5 of 5 orders remain, and 2 of 2 administrative actions.
- CMD `what orders are standing?` → ✓ No standing order is in force, Sire — every marshal awaits the day's orders.
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 5 actions unused) Turn 10 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Munich into Franche-Comte unopposed! (269 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Munich into Franche-Comte unopposed! (269 lost to march) Captured: France → Austria
  - verbs: move×1, attack×1
- LEDGER treasury 3013 · net +1471 · threat 60 · provinces 28 · ceiling 13309 · army 115669 · vassals Holland 84 · Switzerland 80
  - NET income 2645 · trade 611 · admin 50 · tribute 337 · upkeep 896 · charges 144 · contributions 150 · occupation 60 · blockade 382 · admiralty 90 · laws 450
- MISSION Improving Relations — Prussia · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a…
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Munich. A new design hardens in their court.
  - TURN EVENTS 4
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, coercive_demand, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
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

---
finished: **completed** · commands 19 · popups 0 · battles 0
