# Playtest digest — rf3-cmd-off-ulm

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `3d1157842721` (dirty) · content `c696461ccc07` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1767, own corps) vs Mack (lost 16826) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl…
  - ⚔ Archduke Charles (lost 2053) vs Bernadotte (lost 5685) — Bernadotte stood alone, Sire. Ney never came.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Naples open borders
- LEDGER treasury 2507 · net +2282 · threat 72 · provinces 28 · ceiling 55310 · army 175239 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 3400 · trade 400 · admin 50 · tribute 937 · upkeep 2194 · charges 21 · blockade 200 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 5,685 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Naples: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (21,161; expect about 88,309 with the corps likely to arrive, up to 98,912 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 500, own corps) vs Mack (lost 25069) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
- CMD `Davout, attack Mack` → ✓ Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (22,709) vs Mack (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Ney: will march to the sound of the guns — he will NOT make it from the mountains at Munich in time; order 'Ney, support Davout' and it rises to about 76%
  WILL NOT — Bernadotte: is pinned by enemies before his own front
  WILL NOT — Massena: has already marched this turn
  WILL NOT — Napoleon: has already marched this turn
  Mack does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him.
  The band weighs more than the men: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 3164) vs Archduke John (lost 1660) — Not one corps reached Davout. Ney was expected; Davout fought the battle single-handed.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archd… · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharle… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh…
  - 🏴 Austria: Casualties: ArchdukeCharles's army 738, Bernadotte 6,795. Both armies remain in the field. Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,421 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 539, own corps) vs Bernadotte (lost 6795) — Where was Ney? Bernadotte held the field alone — reinforcement never came. And Bernadotte was taken on that field — Aus…
  - ⚔ Archduke Charles (lost 1550) vs Deroy (lost 8518) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2289) vs Murat (lost 6118) — Murat stood alone, Sire. Ney and Soult never came.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Portugal open borders · Denmark non aggression
- LEDGER treasury 4699 · net +2858 · threat 78 · provinces 28 (+0) · ceiling 35760 · army 146487 · vassals Holland 94 · Kingdom of Italy 95 · Switzerland 90
  - NET income 3382 · trade 450 · admin 50 · tribute 937 · upkeep 1316 · charges 248 · contributions 82 · blockade 225 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- COURTS: The court of Prussia eases over The Hanoverian Prize — alliance is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (18,983; expect about 73,801 with the corps likely to arrive, up to 85,273 if all march) vs Mack (8,179 men) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 70, own corps) vs Mack (lost 7338) — Davout and Massena's timely arrival aided Ney. Napoleon, however, was conspicuously absent.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (18,305; expect about 25,822 with the corps likely to arrive, up to 48,139 if all march) vs Mack (837 men) at Franconia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1641, own corps) vs Archduke John (lost 2344) — Reinforcements from Napoleon bolstered Davout's position — though Ney never arrived, Sire.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (166 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 636 gold (×3 at war) (×1.06 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- SPENT 636g on this turn's orders
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a devastating assault! ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCha… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCh… · ArchdukeCharles holds them at Munich while allies attack from Franche-Comte! (+1 coordination)
  - 🏴 Austria: Casualties: ArchdukeCharles 1,670, Murat's army 8,609. Both armies remain in the field. Franche-Comte has been captured by Austria!
  - 🏴 Austria: [!] Napoleon's troops are BROKEN (morale 0%)! FORCED RETREAT! Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 1670) vs Murat (lost 4196, own corps) — Lannes arrived to reinforce Murat, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 519) vs Deroy (lost 6570) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - ⚔ Archduke Charles (lost 723) vs Napoleon (lost 3139) — Napoleon stood alone, Sire. Ney never came.
  - verbs: attack×3, stance_change×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Saxony open borders · Hesse non aggression
- LEDGER treasury 6660 · net +2881 · threat 83 · provinces 29 (+1) · ceiling 33529 · army 127993 · vassals Holland 91 · Kingdom of Italy 92 · Switzerland 85
  - NET income 3355 · trade 449 · admin 50 · tribute 937 · upkeep 992 · charges 499 · occupation 104 · blockade 225 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 12
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,548; expect about 26,016 with the corps likely to arrive, up to 28,622 if all march) vs Mack (837 men) at Franconia — the balance of force looks favorab…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 523, own corps) vs Mack (lost 324, own corps) — Reinforcements from Davout bolstered Ney's position — though Massena never arrived, Sire. And Mack was taken on that fi…
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn,…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 1 · PapalStates open borders
- LEDGER treasury 9592 · net +2556 · threat 86 · provinces 30 (+1) · ceiling 32575 · army 125151 · vassals Holland 92 · Kingdom of Italy 93 · Switzerland 84
  - NET income 3383 · trade 524 · admin 50 · tribute 937 · upkeep 968 · charges 844 · occupation 174 · blockade 262 · admiralty 90
- DISPATCH: Sire — Marshal Mack of Austria is taken at Franconia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 9
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (16,855; expect about 17,659 with the corps likely to arrive, up to 18,012 if all march) vs Archduke Charles (35,767 men) at Munich — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1695, own corps) vs Archduke Charles (lost 1564) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (950 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (110 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 12129 · net +2368 · threat 84 · provinces 30 (+0) · ceiling 31991 · army 115880 · vassals Holland 90 · Kingdom of Italy 91 · Switzerland 80
  - NET income 3452 · trade 549 · admin 50 · tribute 937 · upkeep 896 · charges 1207 · occupation 152 · blockade 275 · admiralty 90
- DISPATCH: Sire — Ney, crowned three turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 10
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)

## Turn 6 — Early December 1805
  - MAILBOX #9 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #12 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +9 (91 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 5g a turn — 99g of income forfeited, 30g of occupation relieved, 74g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (78 → 88); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 14947 · net +2332 · threat 82 · provinces 29 (-1) · ceiling 40181 · army 114144 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3465 · trade 549 · admin 50 · tribute 787 · upkeep 888 · charges 1196 · occupation 70 · blockade 275 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (153 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Davout → secure
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (10,291; expect about 28,691 with the corps likely to arrive, up to 30,570 if all march) vs Archduke Charles (33,364 men) at Munich — the balance of force…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 3098, own corps) vs Archduke Charles (lost 1235, own corps) — Massena and Napoleon's timely arrival aided Murat. Soult, however, was conspicuously absent.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn's forces advance steadily. Brutal stalemate between ArchdukeJohn and Davout. Heavy casualties on both side… · ArchdukeCharles strikes back after successfully defending!
  - ⚔ Archduke John (lost 489, own corps) vs Davout (lost 1853) — Neither Davout nor Archduke John could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 1023) vs Davout (lost 2639) — A narrow defeat for Davout, Sire. Better-prepared troops might have tipped the balance.
  - verbs: attack×2, unfortify×1, move×1
- ORDER Napoleon [retired]: Napoleon's question is overtaken, Sire — Napoleon has marched clear of Munich. He awaits new orders.
- LEDGER treasury 15876 · net +1559 · threat 82 · provinces 30 (+1) · ceiling 26915 · army 93897 · vassals Holland 86 · Kingdom of Italy 97 · Switzerland 83
  - NET income 3470 · trade 549 · admin 50 · tribute 712 · upkeep 728 · charges 1959 · occupation 170 · blockade 275 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Swabia. He must reform before he fights again.
  - TURN EVENTS 9
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.) → trust
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Swa…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Not enough actions for a strategic march! Need 2, have 1.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Davout. Casualties: Archd…
  - 🏴 Austria: [!] Davout's troops are BROKEN (morale 0%)! FORCED RETREAT! Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 552) vs Davout (lost 4054) — Davout's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×1
  - POPUP marshal_audience: shadow_command, Marshal Soult asks for a command → detach
  -     ↳ Soult straightens. "You will not regret it, Sire." March him to Swabia and the front is his — the order is yo…
- LEDGER treasury 17732 · net +1815 · threat 80 · provinces 29 (-1) · ceiling 33110 · army 87808 · vassals Holland 84 · Kingdom of Italy 96 · Switzerland 80
  - NET income 3475 · trade 549 · admin 50 · tribute 712 · upkeep 680 · charges 1856 · occupation 70 · blockade 275 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - TURN EVENTS 11
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 1…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos engages in solid combat. Castanos gains the advantage over Paget. Casualties: Castanos 588, Paget 1,877. Both … · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - ⚔ Castanos (lost 588) vs Paget (lost 1877) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - ⚔ Castanos (lost 256) vs Paget (lost 1469) — Paget's aggressive posture left the troops exposed when Castanos's attack came. And Paget was taken on that field — Spa…
  - verbs: attack×2, move×1
- LEDGER treasury 18655 · net +1746 · threat 78 · provinces 29 (+0) · ceiling 33056 · army 88900 · vassals Holland 84 · Kingdom of Italy 97 · Switzerland 79
  - NET income 3541 · trade 549 · admin 50 · tribute 712 · upkeep 688 · charges 2018 · occupation 35 · blockade 275 · admiralty 90
- DISPATCH: Sire — 3 turns of famine at Swabia now. 6,013 men gone, and not one of them to the enemy. A supply depot at Swabia would ease it; Rhineland can feed 60,000 more and Franconia can feed 53,426 more — a…
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Swabia to Franconia
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Soult, move to Bavaria` → ✗ Region 'Bavaria' not found. Did you mean 'Balearics'?
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #15 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 20371 · net +1502 · threat 76 · provinces 29 (+0) · ceiling 32442 · army 87949 · vassals Holland 84 · Kingdom of Italy 98 · Switzerland 78
  - NET income 3548 · trade 549 · admin 50 · tribute 712 · upkeep 672 · charges 2285 · occupation 35 · blockade 275 · admiralty 90
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 14 approaches rebuffed, chiefly from Prussia (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ Cannot attack ArchdukeJohn — armistice with Austria (5 turns remaining).
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Lorraine and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Lorraine to Franconia
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 21829 · net +1272 · threat 74 · provinces 29 (+0) · ceiling 31796 · army 86426 · vassals Holland 84 · Kingdom of Italy 97 · Switzerland 77
  - NET income 3555 · trade 549 · admin 50 · tribute 712 · upkeep 664 · charges 2530 · occupation 35 · blockade 275 · admiralty 90
- DISPATCH: Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (open borders agreement)

## Turn 12 — Early March 1806
  - MAILBOX #12 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #17 → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace #18 → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm #19 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 15% -> 20%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22490 · net +1121 · threat 72 · provinces 29 (+0) · ceiling 31059 · army 87933 · vassals Holland 84 · Kingdom of Italy 96 · Switzerland 76
  - NET income 3562 · trade 549 · admin 50 · tribute 712 · upkeep 672 · charges 2680 · occupation 35 · blockade 275 · admiralty 90
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Spain rebuffs Denmark and Bavaria (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ Cannot attack ArchdukeJohn — armistice with Austria (3 turns remaining).
- CMD `Davout, move to Franconia` → ✗ Davout is already in Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 23561 · net +927 · threat 70 · provinces 29 (+0) · ceiling 30477 · army 86470 · vassals Holland 84 · Kingdom of Italy 95 · Switzerland 75
  - NET income 3569 · trade 549 · admin 50 · tribute 712 · upkeep 664 · charges 2889 · occupation 35 · blockade 275 · admiralty 90
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 31).
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 14 — Early April 1806
  - MAILBOX #13 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #20 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +5 (95 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Lorraine (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24067 · net +662 · threat 68 · provinces 29 (+0) · ceiling 28887 · army 85036 · vassals Holland 84 · Kingdom of Italy 100 · Switzerland 74
  - NET income 3576 · trade 549 · admin 50 · tribute 562 · upkeep 648 · charges 3027 · occupation 35 · blockade 275 · admiralty 90
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 93%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 3 · Britain armistice losing · Russia armistice losing · Switzerland client petition
- LEDGER treasury 24117 · net +583 · threat 66 · provinces 29 (+0) · ceiling 28267 · army 86570 · vassals Holland 84 · Kingdom of Italy 100 · Switzerland 73
  - NET income 3583 · trade 549 · admin 50 · tribute 562 · upkeep 656 · charges 3105 · occupation 35 · blockade 275 · admiralty 90
- DISPATCH: Sire — Britain and Spain have made peace without us.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 6
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_broken)

## Turn 16 — Early May 1806
  - MAILBOX #14 Britain incoming_proposal: Britain — Armistice → activated
  - MAILBOX #15 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #16 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #21 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #23 → grant the petition
  - POPUP diplomatic_dialogue: Britain, armistice_losing #21 → accept
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (73 → 83); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #22 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #23 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (116 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Ney → secure
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 16 ended. Turn 17 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Ney. Casualties: ArchdukeCharles'… · ArchdukeJohn engages in solid combat. ArchdukeJohn gains the advantage over Murat. Casualties: ArchdukeJohn's army 807,… · ArchdukeCharles holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles advances into Bohemia. (396 lost to march — forward supply lines reduce losses) Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 468, own corps) vs Ney (lost 6214) — Ney's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke John (lost 226, own corps) vs Murat (lost 2802, own corps) — Napoleon marched to Murat's guns as ordered. It was not enough.
  - ⚔ Archduke Charles (lost 73, own corps) vs Ney (lost 2735) — A grievous defeat for Ney, Sire. The losses are severe.
  - verbs: attack×3, move×1
- ORDER Napoleon [retired]: Napoleon's question is overtaken, Sire — Napoleon has marched clear of Franconia. He awaits new orders.
- ORDER Ney [awaiting_response]: Ney is cornered at Franconia with 2,607 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Franconia with 2,607 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 23155 · net -205 · threat 66 · provinces 29 (+0) · ceiling 22048 · army 67792 · vassals Holland 76 · Kingdom of Italy 96 · Switzerland 77
  - NET income 3550 · trade 549 · admin 50 · tribute 337 · upkeep 520 · charges 3934 · contributions 112 · occupation 35 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 8
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy, blockade_broken ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 9 approaches from Britain, Russia and Prussia are rebuffed (defensive alliance)
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 17 — Late May 1806
  - MAILBOX #17 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #25 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (76 → 86); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✗ Davout is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Swabia (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 3 actions unused) Turn 18 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! (299 lost to march — forward supply lines reduce losses) Captured: Fra…
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! (299 lost to march — forward supply lines reduce losses) Captured: France → Austria
  - verbs: form_square×2, attack×1, move×1
- LEDGER treasury 23252 · net +82 · threat 64 · provinces 28 (-1) · ceiling 23765 · army 65667 · vassals Holland 85 · Kingdom of Italy 98 · Switzerland 77
  - NET income 3441 · trade 549 · admin 50 · upkeep 496 · charges 3357 · occupation 15 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 510 gold (×3 at war) (Davout's intendance: -15%). Morale: 10% -> 23%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- SPENT 510g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×1
- LEDGER treasury 22874 · net +136 · threat 62 · provinces 28 (+0) · ceiling 23734 · army 66507 · vassals Holland 84 · Kingdom of Italy 100 · Switzerland 77
  - NET income 3444 · trade 549 · admin 50 · upkeep 504 · charges 3298 · occupation 15 · admiralty 90
- DISPATCH: DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 30).
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: Hanover, Papal States and Sardinia rebuff Prussia (defensive alliance)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, move to Franconia` → ✗ Cannot move into Franconia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John, Hiller.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Hiller launches a decisive assault. Murat holds the line. Casualties: Hiller 1,854, Murat's army 873. Both armies remai…
  - ⚔ Hiller (lost 1854) vs Murat (lost 74, own corps) — Lannes's timely arrival bolstered Murat's position. Well-coordinated, Sire.
  - verbs: wait×1, attack×1, fortify×1
- LEDGER treasury 22986 · net +130 · threat 60 · provinces 28 (+0) · ceiling 23805 · army 62262 · vassals Holland 84 · Kingdom of Italy 100 · Switzerland 78
  - NET income 3432 · trade 549 · admin 50 · upkeep 472 · charges 3324 · occupation 15 · admiralty 90
- DISPATCH: Sire — Davout, Soult, Lannes, Murat, Massena and Napoleon stand 62,262 men at Swabia, which feeds 60,000. 2,262 too many. 7,657 men lost in 3 turns. A supply depot at Swabia would ease it; Rhineland …
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, fortify×1
- LEDGER treasury 22868 · net -99 · threat 58 · provinces 28 (+0) · ceiling 22239 · army 59117 · vassals Holland 83 · Kingdom of Italy 100 · Switzerland 78
  - NET income 3435 · trade 549 · admin 50 · upkeep 448 · charges 3305 · occupation 15 · blockade 275 · admiralty 90
- DISPATCH: Soult's fortifications decay: 11% → 10%
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and France has collapsed. War resumes!
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_begins ×2)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Hiller is at Franconia, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke John at Munich instead.)
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke John at Munich instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 2065, own corps) vs Archduke John (lost 1269) — Davout and Napoleon arrived to reinforce Lannes, but Murat failed to reach the field in time.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 actions unused) Turn 22 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeCharles loses 1,869 troops in the… · ArchdukeCharles marches from Milan into Piedmont unopposed! (1,118 lost to march) Captured: KingdomOfItaly → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -93g, Kingdom of Italy -175g. Captured: KingdomOfItaly → Austria
  - 🏴 Austria: ArchdukeCharles marches from Milan into Piedmont unopposed! (1,118 lost to march) Captured: KingdomOfItaly → Austria
  - verbs: attack×2, move×2, recruit×2
- ORDER Napoleon [retired]: Napoleon's question is overtaken, Sire — Napoleon has marched clear of Munich. He awaits new orders.
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 21570 · net -68 · threat 46 · provinces 27 (-1) · ceiling 21143 · army 52857 · vassals Holland 82 · Switzerland 76
  - NET income 3238 · trade 561 · admin 50 · upkeep 400 · charges 3131 · occupation 15 · blockade 281 · admiralty 90
- DISPATCH: Sire — Corsica has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Corsica.
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)

## Turn 22 — Early August 1806
  - MAILBOX #18 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #26 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×2
- ENVOYS WAITING 1 · Naples non aggression
- LEDGER treasury 20826 · net -602 · threat 44 · provinces 27 (+0) · ceiling 17652 · army 51601 · vassals Holland 83 · Switzerland 76
  - NET income 3241 · trade 561 · admin 50 · upkeep 392 · charges 3576 · contributions 100 · occupation 15 · blockade 281 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Lyonnais. No French corps stands in his path.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Piedmont.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 23 — Late August 1806
  - MAILBOX #19 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #27 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✗ Marshal Davout is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, unfortify` → ✗ Lannes is not currently fortified.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 3 actions unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · Naples non aggression
- LEDGER treasury 20243 · net -248 · threat 42 · provinces 27 (+0) · ceiling 18936 · army 50382 · vassals Holland 84 · Switzerland 76
  - NET income 3244 · trade 561 · admin 50 · tribute 225 · upkeep 376 · charges 3466 · contributions 100 · occupation 15 · blockade 281 · admiralty 90
- DISPATCH: Sire — Marshal Murat's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 24 — Early September 1806
  - MAILBOX #20 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #28 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 98% -> 90%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Naples non aggression
- LEDGER treasury 19463 · net +217 · threat 40 · provinces 27 (+0) · ceiling 20600 · army 52110 · vassals Holland 85 · Switzerland 76
  - NET income 3247 · trade 561 · admin 50 · tribute 562 · upkeep 400 · charges 3317 · contributions 100 · occupation 15 · blockade 281 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 25 — Late September 1806
  - MAILBOX #21 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #29 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✗ Marshal Davout is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 actions unused) Turn 26 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- ENVOYS WAITING 1 · Naples non aggression
- LEDGER treasury 19649 · net +150 · threat 38 · provinces 27 (+0) · ceiling 20436 · army 50877 · vassals Holland 86 · Switzerland 76
  - NET income 3250 · trade 561 · admin 50 · tribute 562 · upkeep 384 · charges 3353 · contributions 150 · occupation 15 · blockade 281 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_ai_ai_treaty)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Britain (Defensive Alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 26 — Early October 1806
  - MAILBOX #22 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #30 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- ENVOYS WAITING 1 · Naples non aggression
- LEDGER treasury 20548 · net +772 · threat 37 · provinces 27 (+0) · ceiling 25978 · army 64680 · vassals Holland 87 · Switzerland 76
  - NET income 3250 · trade 573 · admin 50 · tribute 562 · upkeep 488 · charges 2633 · contributions 150 · occupation 15 · blockade 287 · admiralty 90
- DISPATCH: Sire — 7 turns without settlement on Marshal Murat. A rente would close it today; the arrears will not close themselves.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL diplomatic_armistice_expired_peace: The armistice between Austria and France has concluded. Peace declared.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (NON AGGRESSION → OPEN BORDERS)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 27 — Late October 1806
  - MAILBOX #23 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #31 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Paget is at Limousin, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 10% -> 16%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- SPENT 600g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · Naples non aggression
- LEDGER treasury 20780 · net +739 · threat 36 · provinces 27 (+0) · ceiling 25978 · army 66219 · vassals Holland 88 · Switzerland 76
  - NET income 3250 · trade 573 · admin 50 · tribute 562 · upkeep 488 · charges 2666 · contributions 150 · occupation 15 · blockade 287 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 6 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sweden against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 28 — Early November 1806
  - MAILBOX #24 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #32 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Naples non aggression
- LEDGER treasury 21427 · net +555 · threat 35 · provinces 27 (+0) · ceiling 25330 · army 64799 · vassals Holland 89 · Switzerland 76
  - NET income 3250 · trade 573 · admin 50 · tribute 562 · upkeep 480 · charges 2758 · contributions 250 · occupation 15 · blockade 287 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 7 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 29 — Late November 1806
  - MAILBOX #25 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #33 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Paris. Defense bonus: +7% (grows +3% per turn, max…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Naples non aggression
- LEDGER treasury 22090 · net +569 · threat 34 · provinces 27 (+0) · ceiling 26091 · army 63419 · vassals Holland 90 · Switzerland 76
  - NET income 3250 · trade 573 · admin 50 · tribute 562 · upkeep 472 · charges 2852 · contributions 150 · occupation 15 · blockade 287 · admiralty 90
- DISPATCH: Sire — Marshal Murat's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 30 — Early December 1806
  - MAILBOX #26 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #34 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 10,000 infantry at Paris - Cost: 382 gold (capital discount) (×3 at war) (Davout's intendance: -15%). Morale: 50% -> 43%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- SPENT 382g on this turn's orders
- enemy phase: 2 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Davout · BOMBARDMENT: Shrapnel → Ney
  - verbs: attack×2
- ENVOYS WAITING 1 · Naples non aggression
- LEDGER treasury 22092 · net +354 · threat 33 · provinces 27 (+0) · ceiling 24577 · army 70481 · vassals Holland 91 · Switzerland 76
  - NET income 3250 · trade 573 · admin 50 · tribute 562 · upkeep 528 · charges 2861 · contributions 300 · occupation 15 · blockade 287 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 9 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 31 — Late December 1806
  - MAILBOX #27 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #35 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Castanos at Artois ins…
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Castanos at Artois instead.) → trust
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 2 actions unused) Turn 32 begins!
- enemy phase: 3 actions, 1 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Ney
  - verbs: attack×1, wait×1, recruit×1
- ENVOYS WAITING 2 · Naples non aggression · Britain settlement offer
- LEDGER treasury 22404 · net +268 · threat 32 · provinces 27 (+0) · ceiling 24282 · army 68819 · vassals Holland 92 · Switzerland 76
  - NET income 3250 · trade 573 · admin 50 · tribute 562 · upkeep 520 · charges 2905 · contributions 350 · occupation 15 · blockade 287 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 10 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal

## Turn 32 — Early January 1807
  - MAILBOX #28 Naples incoming_proposal: Naples — Non-Aggression Pact → activated
  - MAILBOX #29 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Naples, non_aggression #36 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #37 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #38 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Britain + Russia (3 pairs resolved). Status quo: Corsica stays British by the treaty. → display-only
  - POPUP diplomatic_dialogue: Naples, non_aggression #36 → accept
  -     ↳ refused: Naples's terms could not be ratified: Relations with France are insufficient for NON_AGGRESSION.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #37 → accept_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Austria ultimatum demand · Holland client petition
- LEDGER treasury 26100 · net +3651 · threat 16 · provinces 27 (+0) · ceiling 330333 · army 67392 · vassals Holland 91 · Switzerland 76
  - NET income 3250 · trade 597 · admin 50 · tribute 562 · upkeep 504 · charges 289 · occupation 15
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France + Holland vs Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +4 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×2)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 32 to 16.
  - LOG ai_proposal_rejected: We rejected Naples's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: Papal States and Sardinia rebuff Austria (defensive alliance)

## Turn 33 — Late January 1807
  - MAILBOX #30 Austria incoming_ultimatum: Austria — Ultimatum → activated
  - MAILBOX #31 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, ultimatum_demand #39 → defy
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #40 → grant the petition
  - POPUP diplomatic_dialogue: Austria, ultimatum_demand #39 → defy
  - POPUP proposal_result: You have defied Austria's ultimatum. Their court will not forget it — expect their weight behind the next coalition. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #40 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 29032 · net +3263 · threat 18 · provinces 27 (+0) · ceiling 300916 · army 68913 · vassals Holland 100 · Switzerland 76
  - NET income 3250 · trade 597 · admin 50 · tribute 225 · upkeep 520 · charges 324 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 32253 · net +3182 · threat 20 · provinces 27 (+0) · ceiling 297416 · army 67476 · vassals Holland 100 · Switzerland 76
  - NET income 3250 · trade 547 · admin 50 · tribute 225 · upkeep 512 · charges 363 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Paris. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 35459 · net +3168 · threat 22 · provinces 27 (+0) · ceiling 299416 · army 66077 · vassals Holland 100 · Switzerland 76
  - NET income 3250 · trade 547 · admin 50 · tribute 225 · upkeep 488 · charges 401 · occupation 15
- DISPATCH: Sire — the levy has stood open 10 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Par…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 90%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 1 action unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 38388 · net +3117 · threat 23 · provinces 27 (+0) · ceiling 298083 · army 67625 · vassals Holland 100 · Switzerland 76
  - NET income 3250 · trade 547 · admin 50 · tribute 225 · upkeep 504 · charges 436 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 41513 · net +3087 · threat 24 · provinces 27 (+0) · ceiling 298750 · army 66212 · vassals Holland 100 · Switzerland 76
  - NET income 3250 · trade 547 · admin 50 · tribute 225 · upkeep 496 · charges 474 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Primacy in Germany — service to the strong is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 44608 · net +3058 · threat 25 · provinces 27 (+0) · ceiling 299416 · army 64838 · vassals Holland 100 · Switzerland 76
  - NET income 3250 · trade 547 · admin 50 · tribute 225 · upkeep 488 · charges 511 · occupation 15
- DISPATCH: Sire — the levy has stood open 13 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 36% -> 36%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 47436 · net +3016 · threat 26 · provinces 27 (+0) · ceiling 298750 · army 66502 · vassals Holland 100 · Switzerland 76
  - NET income 3250 · trade 547 · admin 50 · tribute 225 · upkeep 496 · charges 545 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Swabia (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 50460 · net +3325 · threat 25 · provinces 27 (+0) · ceiling 327500 · army 65202 · vassals Holland 100 · Switzerland 76
  - NET income 3250 · trade 547 · admin 50 · tribute 562 · upkeep 488 · charges 581 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)

---
finished: **completed** · commands 200 · popups 77 · battles 25
