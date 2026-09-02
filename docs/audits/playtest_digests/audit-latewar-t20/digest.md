# Playtest digest — audit-latewar-t20

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - loaded save `fixture_t20_ambient.json` → Loaded: fixture-gen_t20

## Turn 20 — Early July 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory #23 → expand_options
  - POPUP diplomatic_dialogue: proposal_options #24 → execute_proposal
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 4 actions, 4 attacks — Paget marches from Berry into Gascony unopposed! (95 lost to march) Captured: France → Britain · Paget marches from Gascony into Guyenne unopposed! (46 lost to march) Captured: France → Britain · Paget marches from Guyenne into Anjou unopposed! (46 lost to march) Captured: France → Britain · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Britain: Paget marches from Berry into Gascony unopposed! (95 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Gascony into Guyenne unopposed! (46 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Guyenne into Anjou unopposed! (46 lost to march) Captured: France → Britain
  - ⚔ Archduke John (lost 1627) vs Deroy (lost 750) — Complete dominance on the field. Archduke John crumbled before Deroy.
  - verbs: attack×4
  - POPUP proposal_result: Russia has accepted our Peace Treaty! → display-only
- LEDGER treasury 16046 · net -1170 · provinces 16
- DISPATCH: Sire — Gascony has fallen. Enemy colours fly over French homeland soil.

## Turn 21 — Late July 1806
- CMD `invest in Switzerland` → ✗ Switzerland is not a vassal.
- CMD `Talleyrand, request terms from Austria` → ✗ Their terms are already on the desk, Sire — answer the offer in the mailbox.
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 action(s) unused) Turn 22 begins!
- enemy phase: 5 actions, 5 attacks — Paget marches from Anjou into Maine unopposed! (45 lost to march) Captured: France → Britain · Paget marches from Maine into Brittany unopposed! (45 lost to march) Captured: France → Britain · [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense) · ArchdukeJohn marches from Milan into Tyrol unopposed! (92 lost to march — forward supply lines reduce losses) Captured:…
  - 🏴 Britain: Paget marches from Anjou into Maine unopposed! (45 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Maine into Brittany unopposed! (45 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeJohn marches from Milan into Tyrol unopposed! (92 lost to march — forward supply lines reduce losses) Captured: Bavaria → Austria
  - ⚔ Mack (lost 1303) vs Deroy (lost 2061) — Deroy was close. A period of drilling could have changed the outcome.
  - ⚔ Mack (lost 828) vs Deroy (lost 2183) — Deroy's army has been badly mauled. Mack proved the stronger force today.
  - verbs: attack×5
- LEDGER treasury 14623 · net -1150 · provinces 14 (-2)
- DISPATCH: Sire — Maine has fallen. Enemy colours fly over French homeland soil.

## Turn 22 — Early August 1806
- CMD `propose peace to Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #26 → confirm
  -     ↳ refused: Making peace with Austria while allied with Bavaria (who is still at war with Austria) creates a diplomatic c…
  - POPUP diplomatic_dialogue: proposal_confirm → (stale passthrough — #26 already answered this chain)
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 action(s) unused) Turn 23 begins!
- enemy phase: 5 actions, 3 attacks — Paget marches from Limousin into Lyonnais unopposed! (43 lost to march) Captured: France → Britain · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · ArchdukeCharles marches from Hungary into Bohemia unopposed! (461 lost to march — forward supply lines reduce losses) C…
  - 🏴 Britain: Paget marches from Limousin into Lyonnais unopposed! (43 lost to march) Captured: France → Britain
  - 🏴 Austria: [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: ArchdukeCharles marches from Hungary into Bohemia unopposed! (461 lost to march — forward supply lines reduce losses) Captured: Bavaria → Austria
  - ⚔ Archduke John (lost 260) vs Deroy (lost 1877) — A grievous defeat for Deroy, Sire. The losses are severe.
  - verbs: attack×3, fortify×1, wait×1
- LEDGER treasury 13368 · net -1014 · provinces 13 (-1)
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil.

## Turn 23 — Late August 1806
- CMD `guarantee Bavaria` → ✓ France guarantees Bavaria. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility st…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #29 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → accept_settlement_offer
  -     ↳ refused: Sire, the settlement of war_2 is already on the table; resolve it before opening a separate review for war_1.
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 3 action(s) unused) Turn 24 begins!
- enemy phase: 4 actions, 2 attacks — Paget marches from Lyonnais into Provence unopposed! (43 lost to march) Captured: France → Britain · Paget marches from Provence into Languedoc unopposed! (42 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Lyonnais into Provence unopposed! (43 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Provence into Languedoc unopposed! (42 lost to march) Captured: France → Britain
  - verbs: attack×2, unfortify×1, wait×1
- LEDGER treasury 12038 · net -1075 · provinces 11 (-2)
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil.

## Turn 24 — Early September 1806
- CMD `sponsor Austria's design` → ✗ Talleyrand: "We are at WAR with Austria, Sire — one does not bankroll the court one is fighting."
  - POPUP diplomatic_dialogue: incoming_settlement_offer #30 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #29 → request_settlement_revision
  -     ↳ refused: Sire, I shall lay the offered terms for Switzerland vs France on our own table, court by court. We answer the…
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 action(s) unused) Turn 25 begins!
- enemy phase: 6 actions, 0 attacks
  - verbs: recruit×3, move×2, wait×1
- LEDGER treasury 10975 · net -859 · provinces 11 (+0)
- DISPATCH: Supply cost you 874 men, at Lorraine.

## Turn 25 — Late September 1806
- CMD `grant Switzerland more autonomy` → ✗ Switzerland is not a vassal.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 3 action(s) unused) Turn 26 begins!
- enemy phase: 8 actions, 5 attacks — Paget marches from Lyonnais into Savoy unopposed! (82 lost to march) Captured: France → Britain · [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · ArchdukeJohn holds them at Piedmont while allies attack from Milan! (+1 coordination) · Deroy assaults the Bern garrison! Garrison: 10,000 -> 5,000 (-5,000). Deroy loses 3,472 troops. Garrison holds — 5,000 …
  - 🏴 Britain: Paget marches from Lyonnais into Savoy unopposed! (82 lost to march) Captured: France → Britain
  - 🏴 Bavaria: Deroy assaults the Bern garrison! Garrison collapses (5,000 -> 0). Deroy loses 1,736 troops in the assault. Deroy marches into Bern! (333 lost to mar…
  - ⚔ Mack (lost 1006) vs Massena (lost 5664) — Massena held superior ground, yet Mack prevailed. A grim day, Sire.
  - ⚔ Archduke John (lost 21) vs Massena (lost 6076) — Even the favorable ground could not save Massena, Sire. Archduke John overcame the terrain.
  - verbs: attack×5, move×3
- LEDGER treasury 9505 · net -708 · provinces 10 (-1)
- DISPATCH: Sire — Savoy has fallen. Enemy colours fly over French homeland soil.

## Turn 26 — Early October 1806
- CMD `buy off Britain's design` → ✗ Talleyrand: "We are at WAR with Britain, Sire. Designs are bought off at the peace table, not across a battlefield."
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 3 action(s) unused) Turn 27 begins!
- enemy phase: 5 actions, 4 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 258) vs Massena (lost 4489) — The hills were ours, but Archduke Charles took them. Massena's position was overrun.
  - ⚔ Archduke John (lost 5) vs Massena (lost 1971) — The hills were ours, but Archduke John took them. Massena's position was overrun.
  - ⚔ Mack (lost 112) vs Massena (lost 1060) — The hills were ours, but Mack took them. Massena's position was overrun.
  - ⚔ Archduke Charles (lost 37) vs Massena (lost 593) — The hills were ours, but Archduke Charles took them. Massena's position was overrun.
  - verbs: attack×4, wait×1
- LEDGER treasury 8278 · net -631 · provinces 10 (+0)
- DISPATCH: Sire — Massena was mauled at Piedmont: three-quarters of his corps — 4,489 men — lost in a single action.

## Turn 27 — Late October 1806
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory #32 → expand_options
  - POPUP diplomatic_dialogue: proposal_options #33 → execute_proposal
  - POPUP proposal_result: Talleyrand departs for the Britain court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 3 action(s) unused) Turn 28 begins!
- enemy phase: 8 actions, 7 attacks — Paget marches from Normandy into Artois unopposed! (38 lost to march) Captured: France → Britain · Paget marches from Artois into Picardy unopposed! (38 lost to march) Captured: France → Britain · Paget marches from Picardy into Ile-de-France unopposed! (37 lost to march) Captured: France → Britain · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Britain: Paget marches from Normandy into Artois unopposed! (38 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Artois into Picardy unopposed! (38 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget marches from Picardy into Ile-de-France unopposed! (37 lost to march) Captured: France → Britain
  - ⚔ Archduke Charles (lost 19) vs Massena (lost 356) — The hills were ours, but Archduke Charles took them. Massena's position was overrun.
  - ⚔ Archduke John (lost 0) vs Massena (lost 163) — The hills were ours, but Archduke John took them. Massena's position was overrun.
  - ⚔ Mack (lost 9) vs Massena (lost 82) — Massena held superior ground, yet Mack prevailed. A grim day, Sire.
  - ⚔ Archduke Charles (lost 3) vs Massena (lost 41) — The hills were ours, but Archduke Charles took them. Massena's position was overrun.
  - verbs: attack×7, wait×1
- LEDGER treasury 7603 · net -514 · provinces 7 (-3)
- DISPATCH: Sire — Artois has fallen. Enemy colours fly over French homeland soil.

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 action(s) unused) Turn 29 begins!
- enemy phase: 5 actions, 2 attacks — Paget marches from Ile-de-France into Ardennes unopposed! (37 lost to march) Captured: France → Britain · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Britain: Paget marches from Ile-de-France into Ardennes unopposed! (37 lost to march) Captured: France → Britain
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 1) vs Massena (lost 58) — Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×2, fortify×2, wait×1
- LEDGER treasury 7003 · net -477 · provinces 6 (-1)
- DISPATCH: Sire — Ardennes has fallen. Enemy colours fly over French homeland soil.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 3 action(s) unused) Turn 30 begins!
- enemy phase: 5 actions, 0 attacks
  - verbs: move×1, unfortify×1, grant_dotation×1, wait×1, recruit×1
- LEDGER treasury 6050 · net -731 · provinces 6 (+0)
- DISPATCH: Sire — Archduke John has crossed into Paris. No French corps stands in his path.

---
finished: **completed** · commands 20 · popups 13 · battles 15
