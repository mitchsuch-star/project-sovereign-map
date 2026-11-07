# Playtest digest — rev1106-end-soil

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - loaded save `fixture_ge2_soil_or_sword.json` → Loaded: GE-2 staged — the Empire without soil (Brittany alone, at war)

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena
  - ⚔ Archduke Charles (lost 4611) vs Massena (lost 4941) — Stalemate. Massena and Archduke Charles glare at each other across the field. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 4 · Austria peace · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury -1498 · net -433 · threat 67 · provinces 1 · army 182887 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 100 · trade 350 · admin 50 · tribute 895 · upkeep 1618 · requisitions 99 · blockade 219 · admiralty 90
- DISPATCH: Sire — France holds a single province: Brittany. Paris is in Austria's hands. 10 corps still stand under our colours — Massena, Soult, Davout, Ney, Murat, Lannes, Bernadotte, the Emperor, Teulie and …
  - RAIL balance_of_europe_shifted: Vienna System leads the current largest alignment at 58% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +9 medium/low (law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
  - MAILBOX #1 Austria incoming_proposal: Austria — Peace Treaty → activated
  - MAILBOX #2 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Austria, peace #1 → reject_ai_proposal
  -     ↳ refused: Sire, another matter has arrived since — this concerns Prussia. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #2 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, peace #1 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Mack attacks Lannes · Archduke Charles attacks Teulie
  - ⚔ Archduke Charles (lost 4572) vs Massena (lost 4401, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Mack (lost 5026) vs Lannes (lost 2662, own corps) — Reinforcement from Napoleon kept Lannes standing, Sire — but neither side yielded the ground.
  - ⚔ Archduke Charles (lost 2631) vs Teulie (lost 1386, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×3, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury -2502 · net -257 · threat 66 · provinces 1 (+0) · army 168792 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 94
  - NET income 100 · trade 350 · admin 50 · tribute 829 · upkeep 1376 · requisitions 99 · blockade 219 · admiralty 90
- DISPATCH: Sire — France holds a single province: Brittany. Paris is in Austria's hands. 10 corps still stand under our colours — Soult, Massena, Davout, Ney, Murat, Bernadotte, Lannes, the Emperor, Dumonceau a…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +6 medium/low (law_enacted_abroad ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG balance_of_europe_shifted: Vienna System leads the current largest alignment at 58% of active European bloc power.
  - LOG ai_proposal_rejected: We rejected the Ottoman Empire's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 5 actions, 5 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore attacks Brittany · Archduke Charles attacks Massena · Mack attacks Lannes · Archduke Charles attacks Teulie
  - 🏴 Britain: Moore attacks Brittany — Region captured: Brittany (was France) (secured)
  - ⚔ Archduke Charles (lost 2837) vs Massena (lost 4255, own corps) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Mack (lost 4574) vs Lannes (lost 2234, own corps) — Napoleon arrived in time to steady Lannes's position. The field was held, nothing further.
  - ⚔ Archduke Charles (lost 1662) vs Teulie (lost 1429, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 3605) vs Murat (lost 3745, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×5
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 3,656 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last…
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 3,656 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury -3542 · net -95 · threat 65 · provinces 0 (-1) · army 150906 · vassals Holland 94 · Kingdom of Italy 90 · Switzerland 88
  - NET trade 350 · admin 50 · tribute 799 · upkeep 1084 · requisitions 99 · blockade 219 · admiralty 90
- DISPATCH: Sire — Brittany has fallen to Britain. Enemy colours fly over French homeland soil.
  - RAIL balance_of_europe_shifted: Vienna System leads the current largest alignment at 60% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Mack attacks Lannes · Archduke Charles attacks Bernadotte · Mack attacks Murat
  - ⚔ Mack (lost 3287) vs Lannes (lost 1964, own corps) — Napoleon reached the field beside Lannes, Sire — it saved the line, no more.
  - ⚔ Archduke Charles (lost 1725) vs Bernadotte (lost 4464) — The engagement proceeded as one might expect, Sire.
  - ⚔ Mack (lost 2454) vs Murat (lost 3716, own corps) — A narrow defeat for Murat, Sire. Better-prepared troops might have tipped the balance.
  - verbs: attack×3
- LEDGER treasury -3970 · net +202 · threat 64 · provinces 0 (+0) · ceiling 2679 · army 130234 · vassals Holland 90 · Kingdom of Italy 74 · Switzerland 82
  - NET trade 350 · admin 50 · tribute 802 · upkeep 790 · requisitions 99 · blockade 219 · admiralty 90
- DISPATCH: Sire — the Empire has stood reduced 4 turns, and every province retaken would pay again. France holds no province of her own. Paris is in Austria's hands. 9 corps still stand under our colours — Soul…
  - TURN EVENTS 3
- DIPLO +5 medium/low (province_changed_hands ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG balance_of_europe_shifted: Vienna System leads the current largest alignment at 60% of active European bloc power.
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected the Papal States' open borders agreement proposal
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 12 actions, 6 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack attacks Lannes · Archduke Charles attacks Bernadotte · Mack attacks Murat · Archduke Charles attacks Murat
  - 🏴 Austria: Archduke Charles attacks Bernadotte — Franconia CAPTURED! (was Bavaria) (secured)
  - 🏴 Spain: Castanos attacks Aragon — Region captured: Aragon (was Britain) (secured)
  - 🏴 Spain: Castanos attacks Madrid — Region captured: Madrid (was Britain) (secured)
  - ⚔ Mack (lost 2244) vs Lannes (lost 1749, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Archduke Charles (lost 926) vs Bernadotte (lost 4857) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 1794) vs Murat (lost 5083) — The toll on Murat's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 1506) vs Murat (lost 3186, own corps) — Ney and Davout marched to Murat's guns as ordered. It was not enough. — The corps system brought Ney in.
  - verbs: attack×6, move×1, fortify×1, retreat×1, stance_change×1, wait×1, recruit×1
  - ENDING — THE FALL OF THE EMPIRE: No soil remains to the Emperor — his armies fight on for a realm that is gone. [THE ECLIPSE]
  -     ↳ Late November 1805 (turn 5) · register `fall` · TERMINAL — Load / Main Menu
  -     ↳ THE VERDICT — THE ECLIPSE: The Empire is smaller and poorer than it began. / Its enemies have learned that it can be beaten. / History will call it the beginning of the end.
  -     ↳ The Verdict of History: the eclipse.
  -     ↳ THE RECORD — battles 15 (0 won, 9 lost) · men lost 71,716, inflicted 43,454 · provinces taken 0, lost 1 · marshals fallen 1, taken 1 · coalitions faced 1 · peaces signed 0
  -     ↳ THE EXILE (abdication) — In late November 1805, with no soil left to govern, the Emperor signed his abdication at Fontainebleau. Austria and its allies sent him to Elba — a small island, a small court, and a sovereign who had once governed a continent.
  -     ↳ Davout and Murat followed him to the boat. Teulie was still a prisoner of the enemy. Bernadotte had long since stopped answering his letters.
  -     ↳ In 15 battles the Empire won 0 and lost 9; 43,454 of the enemy fell against 71,716 of our own. The Great Battle of Swabia was the worst day. One province was lost, to Britain. One coalition stood against him — the Third Coalition.
  -     ↳ The successor government signs the peace with Austria at Frankfurt's terms — 4,190 gold and 419 a turn for 10 turns (Paris, Berry, Corsica held until paid) — recognition of the new government the term that bought the leniency (Châtillon's terms were the Emperor's to refuse).
  -     ↳ The Verdict of History: the eclipse. Talleyrand, who had served every government France had ever had, served the next one too.
- LEDGER treasury -4603 · net +377 · threat 63 · provinces 0 (+0) · ceiling 3224 · army 103927 · vassals Holland 84 · Kingdom of Italy 68 · Switzerland 74
  - NET trade 350 · admin 50 · tribute 806 · upkeep 594 · requisitions 74 · blockade 219 · admiralty 90
- DISPATCH: Sire — the Empire has stood reduced 5 turns, and every province retaken would pay again. France holds no province of her own. Paris is in Austria's hands. 8 corps still stand under our colours — Soul…
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +7 medium/low (diplomatic_we_threshold, province_changed_hands ×5, diplomatic_dp_regen)
  - GAME OVER reported — stopping

---
finished: **game-over** · commands 5 · popups 13 · battles 15
