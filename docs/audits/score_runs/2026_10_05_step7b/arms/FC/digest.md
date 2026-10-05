# Playtest digest — FC

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `88cd6378f016` (dirty) · content `08fe8a7fc9ef` · driver `2cbaf8455dd8`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `help` → ✓ COMMAND REFERENCE
- CMD `what can I do` → ✓ These orders would be carried out today, Sire:
  - ↳ Ney, attack Mack / Davout, march to Lorraine
- CMD `who am I fighting and why` → ✓ We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +0 (evenly matched), declared this turn. Our purpose: the defense of the homeland …
- CMD `who are we at war with` → ✓ We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +0 (evenly matched), declared this turn. Our purpose: the defense of the homeland …
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory #1 → dismiss
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `hello` → ✓ Berthier bows. "Sire. The army stands ready for your orders. This morning, 'Ney, attack Mack' would be carried out at once. Type 'what can I do' for the orders this boar…
- CMD `what now` → ✓ These orders would be carried out today, Sire:
  - ↳ Ney, attack Mack / Davout, march to Lorraine
- CMD `how do I win` → ✓ Berthier unrolls the map. "The reign is WON at the Congress of Paris, Sire: hold 45 TITLED provinces — homeland, ceded by treaty, a client's soil, or held 12 quiet turns…
- CMD `is Paris safe` → ✓ Paris is ours, Sire, held by a garrison of 25,000. No enemy corps stands within two marches of it, so far as our intelligence reaches — it looks safe today.
- CMD `is Vienna safe` → ✓ Vienna is Austria's, Sire; we have no intelligence on what holds it. Corps at war with Austria within two marches: Deroy of Bavaria is at Franconia, two marches off (22,…
- CMD `how many men do I have` → ✓ Our army stands at 189,000 men under 8 marshals, Sire:
  - ↳ Massena — 42,000 at Milan (morale 100) / Soult — 30,000 at Lorraine (morale 100)
- CMD `is Mack strong` → ✓ Mack of Austria was reported at Swabia — large force.
- CMD `what does Kutuzov have with him` → ✓ We have no word of Kutuzov's whereabouts, Sire.
- CMD `who are my allies` → ✓ Our allies, Sire: Spain (alliance) and Bavaria (alliance). Our clients: Holland, Kingdom of Italy and Switzerland. Every treaty is in the Diplomatic Ledger (press D).
- CMD `what can I build` → ✓ At Rhineland we may build: supply depot (300g), fortification (400g), training ground (250g), market (350g), stables (300g).
- CMD `what are Ney's odds against Vienna` → ✓ Ney stands at Rhineland, beyond reach of Vienna this turn, Sire — the order would be refused, and nothing spent.
- CMD `what happened last turn` → ✓ This morning's dispatch leads with: Sire — a quiet morning on the front. The marshals await your word. The whole briefing is on this morning's dispatch (press R); the re…
- CMD `undo` → ✓ Berthier shakes his head. "There is no unsaying an order once relayed, Sire — what has gone out has gone out. A standing march or hold can be stood down with 'cancel <ma…
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1847, own corps) vs Mack (lost 24408) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Soult and Bernadotte never arr… — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 actions unused) Turn 2 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Massena. Casualties: Archduke Charl… · Deroy delivers an effective strike. Deroy gains the advantage over Mack. Casualties: Deroy 983, Mack 8,861. Both armies…
  - ⚔ Archduke Charles (lost 3964) vs Massena (lost 6353) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Deroy (lost 983) vs Mack (lost 8861) — Mack stood alone, Sire. Archduke John never came.
  - verbs: attack×2, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1703 · net +1472 · threat 76 · provinces 28 · ceiling 33452 · army 172678 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2104 · blockade 219 · admiralty 90
- DISPATCH: Sire — Marshal Ney holds the field at Swabia — Mack's corps is broken and flees.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +9 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `what happened last turn` → ✓ This morning's dispatch leads with: Sire — Marshal Ney holds the field at Swabia — Mack's corps is broken and flees. Overnight: Supply cost you 4,602 men, at Swabia; Swi…
- CMD `who is winning` → ✓ War score, Sire — the Third Coalition (Britain, Austria and Russia) +16 (evenly matched). The breakdown is on the war banner on the left (click the war).
- CMD `how is the war effort` → ✓ France's war weariness stands at 14 (rising), Sire. Of the courts at war with us: Austria 36 (rising). Britain and Russia we cannot read. It climbs while the war lasts a…
- CMD `how long until the armistice with Russia expires` → ✓ There is no armistice with Russia, Sire — France and Russia are at war.
- CMD `what can I do` → ✓ These orders would be carried out today, Sire:
  - ↳ Bernadotte, attack Mack / Ney, march to Franconia
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu… · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Charle…
  - ⚔ Archduke Charles (lost 4330) vs Massena (lost 4342, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 2676) vs Teulie (lost 1357, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×2, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2982 · net +1718 · threat 74 · provinces 28 (+0) · ceiling 33013 · army 160394 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 93
  - NET income 2590 · trade 350 · admin 50 · tribute 829 · upkeep 1736 · charges 56 · blockade 219 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes, Murat and Napoleon stand 85,757 men at Swabia, which feeds 60,000. 25,757 too many. 8,876 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply …
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_proposal_rejected: We rejected the Ottoman Empire's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal

---
finished: **completed** · commands 28 · popups 7 · battles 5
