# Playtest digest — depth-c00-recon

seed `historical` · llm `anthropic` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `help` → ✓ COMMAND REFERENCE
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `who are we at war with?` → ✓ We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +0 (evenly matched), declared this turn. Our purpose: the defense of the homeland …
- CMD `where are my marshals?` → ✓ Our army stands at 189,000 men under 8 marshals, Sire:
  - ↳ Massena — 42,000 at Milan (morale 100) / Soult — 30,000 at Lorraine (morale 100)
- CMD `where is the enemy?` → ✓ Sire — Austria: Archduke John at Tyrol (substantial force); Mack at Swabia (large force); no word of Archduke Charles. Britain: no word of Moore. Russia: no word of Buxh…
- CMD `where is Mack?` → ✓ Mack of Austria was reported at Swabia — large force.
- CMD `how is the treasury?` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `what does Austria want?` → ✓ Austria pursues Redeem Italy, Sire. The priority theater of 1805 - Charles holds the main army in Italy; the losses of Campo Formio and Luneville must be undone. The pro…
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory #1 → dismiss
- CMD `what can I do` → ✓ These orders would be carried out today, Sire:
  - ↳ Ney, attack Mack / Davout, march to Lorraine
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu…
  - ⚔ Archduke Charles (lost 4431) vs Massena (lost 5819) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1636 · net +1126 · threat 68 · provinces 28 · ceiling 29330 · army 183181 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2450 · blockade 219 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

---
finished: **completed** · commands 11 · popups 1 · battles 1
