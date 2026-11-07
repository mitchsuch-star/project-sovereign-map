# Playtest digest — REACH-AAR

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "client_petition": "grant"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory #1 → expand_options
  - POPUP diplomatic_dialogue: proposal_confirm #2 → confirm
  - POPUP proposal_result: Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `Marshal Ney, you have the honour of the first blow. Fall upon Mack at Ulm before the Russians can reach him, and do not let him slip away down the Danube.` → ✓ MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force)…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1968, own corps) vs Mack (lost 20822) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Napoleon, attack Mack` → ✓ MUSTER — Napoleon (9,509; expect about 145,680 with the corps likely to arrive) vs Mack (31,178 men) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 184, own corps) vs Mack (lost 31178) — An exemplary engagement by Napoleon. The outcome was never in doubt.
- CMD `Soult, march to Swabia` → ✓ Soult begins march to Swabia. Moves to Swabia.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 1 action unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena
  - ⚔ Archduke Charles (lost 4241) vs Massena (lost 6645) — The margin was slim. Training and preparation would serve Massena well.
  - verbs: attack×1, wait×1
- ORDER Soult [completed]: As ordered: "Soult, march to Swabia". Soult arrives at Swabia.
  - POPUP proposal_result: Britain has rejected our Peace Treaty. → display-only
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #3 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 231 · net +121 · threat 84 · provinces 28 · ceiling 2881 · army 167031 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 3474 · blockade 250 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is destroyed at Swabia — his corps annihilated, his name struck from their order of battle.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Britain with a response.
  - TURN EVENTS 4
- DIPLO +11 medium/low (diplomatic_proposal_sent, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `build ships` → ✗ A ship of the line costs 400g — the treasury holds 264g.
- CMD `court Prussia` → ✓ Sire, I shall begin efforts to court and charm Prussia. This will cost 2 DP per turn. Starting this courtship shuts Reassure Ally; Spain, at 39, is under the 40 line and…
  - POPUP diplomatic_dialogue: mission #6 → start_mission
- CMD `Ney, move to Franconia` → ✓ Ney moves from Swabia to Franconia (206 lost to march)
- CMD `Davout, move to Munich` → ✓ Davout moves from Swabia to Munich (723 lost to march)
- CMD `Murat, scout Tyrol` → ✓ Murat scouts Tyrol: Controlled by Austria. Terrain: Mountains (+25% defense). Enemy forces: Archduke Charles (Austria): ~48,273 troops; Archduke John (Austria): ~19,403 …
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, fortify×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 538 · net +274 · threat 82 · provinces 28 (+0) · ceiling 3940 · army 163745 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 450 · admin 50 · tribute 901 · upkeep 3346 · blockade 281 · admiralty 90
- MISSION Courting — Prussia · net +8 a turn · 4 funded turns to the full +10; the favour holds while he stays · beat running
- DISPATCH: Sire — Soult, Lannes, Murat and Napoleon stand 69,295 men at Swabia, which feeds 60,000. 9,295 too many. 9,673 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too lar…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 2
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +6 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `buy off Austria` → ✗ Talleyrand: "We are at WAR with Austria, Sire — not across a battlefield: at the peace table her design can be pointed elsewhere — The Eastern Question (Albania)."
- CMD `recruit` → ✗ Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.' Recruits join a marshal who can reach the depot: Ney (out of range - 6 regions …
- CMD `build market at Paris` → ✓ Construction started: Market in Paris (2 turns, 350 gold)
- CMD `Ney, attack Bohemia` → ✓ Ney marches from Franconia into Bohemia unopposed! (199 lost to march) Captured: Austria → France
  - POPUP capture_choice[capture]: Bohemia, Ney → secure
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles a…
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Tyrol instead.) → insist
- CMD `license Prussia against Hanover` → ✓ License Prussia's design against Hanover: no gold, 1 diplomatic point. France blesses it and pledges non-interference for 10 turns. The compact binds France: marching on…
  - POPUP clarification: The Cabinet, License Prussia's design against Hanover: no gold, 1 diplomatic point. France blesses it and pledges non-interference for 10 turns. The compact binds France: marching on Prussia before it lapses, or guaranteeing Hanover, is reneging — relations -25 and the strongest casus belli in Europe. If Prussia then declares on Hanover, her relations with every court, France's included, fall 15 (France–Prussia now -2, +3 once this compact is struck, -12 after her declaration); the Court mission running with Prussia is set back the same 15. License it? (yes / no) → 1 (first option: Grant the licence)
- CMD `Lannes, move to Munich` → ✓ Lannes moves from Swabia to Munich (302 lost to march)
- CMD `Massena, fortify` → ✗ Not enough actions! Need 1, have 0 — Massena cannot fortify today.
- CMD `Davout, fortify` → ✗ Not enough actions! Need 1, have 0 — Davout cannot fortify today.
- CMD `Davout, fortify` → ✗ Not enough actions! Need 1, have 0 — Davout cannot fortify today.
- CMD `end turn` → ✓ Turn 3 ended. Turn 4 begins!
- SPENT 350g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Russia, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, fortify×1, naval_expedition×1
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 834 · net +577 · threat 82 · provinces 29 (+1) · ceiling 5293 · army 162162 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2640 · trade 525 · admin 50 · tribute 905 · upkeep 3024 · occupation 100 · blockade 329 · admiralty 90
- MISSION Courting — Prussia · net +8 a turn · 3 funded turns to the full +10; the favour holds while he stays · beat running
- DISPATCH: Sire — Bohemia has fallen to our arms. The tricolor flies over it this morning.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, province_changed_hands, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: France licences Prussia's design against Hanover
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `build supply depot in Bohemia` → ✗ Cannot build in Bohemia — region stability too low (35/100). Need 51+.
- CMD `build watchtower in Bohemia` → ✗ Cannot build in Bohemia — region stability too low (35/100). Need 51+.
- CMD `Ney, scout Vienna` → ✓ Ney scouts Vienna: Controlled by Austria. Terrain: Plains. No field army stands there. Garrison: 25,000 — it must be assaulted — a march halts before it; it breaks below…
- CMD `Soult, move to Franconia` → ✓ Soult moves from Swabia to Franconia (566 lost to march)
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (188 lost to march)
- CMD `Bernadotte, move to Bohemia` → ✓ Bernadotte moves from Franconia to Bohemia (170 lost to march)
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 5 actions, 0 attacks — Austria, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, stance_change×1, unfortify×1, garrison×1
- ENVOYS WAITING 1 · Prussia non aggression
- LEDGER treasury 1878 · net +894 · threat 80 · provinces 29 (+0) · ceiling 6988 · army 161238 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2695 · trade 587 · admin 50 · tribute 910 · upkeep 2790 · occupation 100 · blockade 368 · admiralty 90
- MISSION Courting — Prussia · net +8 a turn · 2 funded turns to the full +10; the favour holds while he stays · beat blowback
- DISPATCH: Sire — London now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1…
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, province_changed_hands, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_mission_blowback, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG moment: Britain decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Russia decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign an Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign an Open Borders Agreement

## Turn 5 — Late November 1805
  - MAILBOX #8 Prussia incoming_proposal: Prussia — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Prussia, non_aggression #13 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 54 gold into the treasury. → display-only
- CMD `Talleyrand, assess Austria` → ✓ I am confident in this assessment, Sire. My sources are reliable. We are at war with Austria, Sire. War score stands at 35 from our perspective. In the field we outmatch…
  - POPUP diplomatic_dialogue: advisory #14 → assess_terms
  - POPUP diplomatic_dialogue: feasibility #15 → execute_proposal
  - POPUP proposal_result: Talleyrand departs for the Austrian court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Court Nation at Prussia pauses until he is home (about 1 turn). → display-only
- CMD `recruit for Lannes` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `Soult, move to Bohemia` → ✓ Soult moves from Franconia to Bohemia (525 lost to march)
- CMD `Ney, attack Vienna` → ✓ Berthier stays the order a moment, Sire: before Ney marches on Kutuzov, read the muster.
  - POPUP strategic_interrupt: Ney, muster_confirm, Berthier stays the order a moment, Sire: before Ney marches on Kutuzov, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Ney attacks Kutuzov' to read the muster before you commit — it costs nothing.
MUSTER — Ney (19,719) vs Kutuzov (32,932 men) at Vienna — the balance of force looks unfavorable.
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL NOT — Bernadotte: will not lift a finger for Marshal Ney
  Standing modifiers, already in the band: Kutuzov stands +21% on the defense (his stance, his character and his works).
  Vienna feeds 50,000 — the whole muster can stand there fed.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 19,719 we muster) would cost ~148g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 80/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Ney (19,719) vs Kutuzov (32,932 men) at Vienna — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 4729) vs Kutuzov (lost 2319) — Ney was close. A period of drilling could have changed the outcome.
- CMD `Napoleon, move to Franconia` → ✓ Napoleon moves from Swabia to Franconia (83 lost to march)
- CMD `Davout, fortify` → ✗ Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
- CMD `Davout, go defensive` → ✓ Davout shifts from NEUTRAL to DEFENSIVE stance. Effect: -10% attack, +15% defense.
- CMD `buy substitutes for Ney` → ✗ Berthier shakes his head. 'Substitutes are 3,410 gold the battalion, Sire — 3,410 for 1. The treasury holds 1,696.'
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 5 actions, 1 attacks — Prussia, Spain, the Ottoman Empire and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Hungary
  - 🏴 Austria: Archduke John attacks Hungary — Region captured: Hungary (was Bavaria) (secured)
  - verbs: move×2, unfortify×1, wait×1, attack×1
- ENVOYS WAITING 2 · Austria peace · Switzerland client petition
- LEDGER treasury 3205 · net +1321 · threat 78 · provinces 29 (+0) · ceiling 11623 · army 155901 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 2795 · trade 599 · admin 50 · tribute 914 · upkeep 2314 · charges 188 · occupation 70 · blockade 375 · admiralty 90
- MISSION Courting — Prussia · net +8 a turn · 2 funded turns to the full +10; the favour holds while he stays · beat running
- DISPATCH: Sire — Hungary has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - TURN EVENTS 2
- DIPLO +8 medium/low (diplomatic_treaty_signed, diplomatic_proposal_sent, province_changed_hands, law_enacted_abroad ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)

## Turn 6 — Early December 1805
  - MAILBOX #10 Austria counter_offer_response: Austria — Peace Treaty → activated
  - MAILBOX #9 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, peace #17 → accept_counter_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #16 → grant the petition
  - POPUP diplomatic_dialogue: Austria, peace #17 → accept_counter_offer
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - RATIFIED Austria · PEACE · french_victory
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Soult, attack Vienna` → ✗ Soult cannot march on Kutuzov: Vienna is Austria's soil, and we are at peace with Austria — no corps of ours may take the field there.
- CMD `Murat, attack Vienna` → ✗ Murat cannot march on Kutuzov: Vienna is Austria's soil, and we are at peace with Austria — no corps of ours may take the field there.
- CMD `Napoleon, move to Bohemia` → ✓ Napoleon moves from Franconia to Bohemia (82 lost to march)
- CMD `Napoleon, move to Bohemia` → ✗ Napoleon is already in Bohemia.
- CMD `Ney, move to Vienna` → ✗ Cannot move into Vienna - enemy forces present! Use ATTACK to engage Kutuzov.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2
- LEDGER treasury 4362 · net +977 · threat 77 · provinces 29 (+0) · ceiling 10750 · army 153799 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2795 · trade 599 · admin 50 · tribute 694 · treaty -100 · upkeep 2166 · charges 360 · occupation 70 · blockade 375 · admiralty 90
- MISSION Courting — Prussia · net +8 a turn · 1 funded turn to the full +10; the favour holds while he stays · beat running
- DISPATCH: Sire — peace with Austria is signed. The war is over.
  - RAIL peace_ratified: Peace ratified between France and Austria.
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 4
- DIPLO +6 medium/low (status_quo_titled, diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 7 — Late December 1805
- CMD `Ney, attack Hungary` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #19 → 1
  -     ↳ refused: Our peace with Austria is fresh: no war may be declared on her for 4 more turns.
- CMD `Lannes, attack Tyrol` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #20 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #21 → 1
  -     ↳ refused: Our peace with Austria is fresh: no war may be declared on her for 4 more turns.
- CMD `Napoleon, move to Vienna` → ✗ Cannot move into Vienna - enemy forces present! Use ATTACK to engage Kutuzov.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified.…
- CMD `commission Marmont` → ✗ Commissioning Marmont costs 4,500g — the treasury holds 4,362g.
- CMD `Lannes, attack Tyrol` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #22 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #23 → 1
  -     ↳ refused: Our peace with Austria is fresh: no war may be declared on her for 4 more turns.
- CMD `Napoleon, move to Vienna` → ✗ Not enough actions! Need 1, have 0 — Napoleon cannot march to Vienna today.
- CMD `Davout, fortify` → ✗ Not enough actions! Need 1, have 0 — Davout cannot fortify today.
- CMD `commission Marmont` → ✗ Commissioning Marmont costs 4,500g — the treasury holds 4,362g.
- CMD `Napoleon, move to Vienna` → ✗ Not enough actions! Need 1, have 0 — Napoleon cannot march to Vienna today.
- CMD `Davout, fortify` → ✗ Not enough actions! Need 1, have 0 — Davout cannot fortify today.
- CMD `commission Marmont` → ✗ Commissioning Marmont costs 4,500g — the treasury holds 4,362g.
- CMD `propose common peace with Austria` → ✗ We are not at war with Austria, Sire.
- CMD `end turn` → ✓ Turn 7 ended. Turn 8 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 4 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: Prussia, defensive_alliance #24 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Prussia. → display-only
  - POPUP diplomatic_dialogue: moment_letter #25 → reject_ai_proposal
- ENVOYS WAITING 2 · Prussia defensive alliance · The Secretariat moment letter
- LEDGER treasury 5403 · net +871 · threat 76 · provinces 29 (+0) · ceiling 10980 · army 151874 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2795 · trade 599 · admin 50 · tribute 698 · treaty -100 · upkeep 2106 · charges 530 · occupation 70 · blockade 375 · admiralty 90
- MISSION Courting — Prussia · net +8 a turn · the favour stands at +10 and holds while he stays — recall him once the treaty is signed · beat blowback
- DISPATCH: Sire — Ney, Soult, Bernadotte and Napoleon stand 60,853 men at Bohemia, which feeds 60,000. 853 too many. 3,945 men lost in 2 turns. A supply depot at Bohemia would ease it; Franconia can feed 41,345…
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_mission_blowback, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her

## Turn 8 — Early January 1806
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Massena, attack Archduke Charles` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #26 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #27 → 1
  -     ↳ refused: Our peace with Austria is fresh: no war may be declared on her for 3 more turns.
- CMD `recruit for Marmont` → ✗ Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.' Recruits join a marshal who can reach the depot: Ney (out of range - 6 regions …
- CMD `Lannes, move to Milan` → ✓ Lannes moves from Munich to Milan (148 lost to march)
- CMD `Soult, move to Vienna` → ✗ Cannot move into Vienna - enemy forces present! Use ATTACK to engage Kutuzov.
- CMD `Lannes, retreat` → ✗ Lannes is not in danger. No retreat necessary.
- CMD `Murat, attack Moravia` → ✗ Murat cannot attack Bavaria — they are our ally, Sire, and we are not at war with them.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 4 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 6577 · net +976 · threat 75 · provinces 29 (+0) · ceiling 12703 · army 149889 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 95
  - NET income 2845 · trade 599 · admin 50 · tribute 703 · treaty -100 · upkeep 1878 · charges 728 · occupation 50 · blockade 375 · admiralty 90
- MISSION Courting — Prussia · net +8 a turn · the favour stands at +10 and holds while he stays — recall him once the treaty is signed · beat blowback
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,272g — you can afford it); guarantee Hanover (1 DP — 5 in hand); or let the w…
  - TURN EVENTS 2
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as joining the stronger side for pay.
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_mission_blowback)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)

## Turn 9 — Late January 1806
- CMD `Soult, attack Kutuzov` → ✗ Soult cannot march on Kutuzov: Vienna is Austria's soil, and we are at peace with Austria — no corps of ours may take the field there.
- CMD `Massena, march to Vienna` → ✓ The direct road to Vienna via Tyrol is closed — Austria keeps its frontier shut; the lawful road is 4 provinces, 4 turns, through Bavaria — march, or cancel?
  - POPUP clarification: Berthier, march_detour_ask, The direct road to Vienna via Tyrol is closed — Austria keeps its frontier shut; the lawful road is 4 provinces, 4 turns, through Bavaria — march, or cancel? → 1 (first option: March (2 AP))
- CMD `Bernadotte, move to Vienna` → ✗ Cannot move into Vienna - enemy forces present! Use ATTACK to engage Kutuzov.
- CMD `recruit for Marmont` → ✗ Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.' Recruits join a marshal who can reach the depot: Ney (out of range - 6 regions …
- CMD `recruit for Marmont` → ✗ Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.' Recruits join a marshal who can reach the depot: Ney (out of range - 6 regions …
- CMD `buy substitutes for Soult` → ✓ Soult takes 3,000 substitutes into the line at Bohemia — 2,676 gold, and not a man off the rolls. Morale 100% -> 91% (bought men muster at 25%). They come up in drafts o…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- SPENT 2676g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 4 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [active]: Massena is marching to Vienna (3 turns remaining).
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 4960 · net +906 · threat 74 · provinces 29 (+0) · ceiling 10534 · army 148133 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2845 · trade 599 · admin 50 · tribute 707 · treaty -100 · upkeep 2200 · charges 480 · occupation 50 · blockade 375 · admiralty 90
- MISSION Courting — Prussia · net +8 a turn · the favour stands at +10 and holds while he stays — recall him once the treaty is signed · beat blowback
- DISPATCH: Sire — Ney, Soult, Bernadotte and Napoleon stand 60,126 men at Bohemia, which feeds 60,000. 126 too many. 5,652 men lost in 3 turns. A supply depot at Bohemia would ease it; Franconia can feed 41,345…
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Carniola.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle the War with the Third Coalition — Britain + Russia.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 2
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- DIPLO +8 medium/low (enemy_marshal_commissioned ×2, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_mission_blowback, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)

## Turn 10 — Early February 1806
  - MAILBOX #13 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #29 → reject_settlement_offer
- CMD `build ships` → ✓ A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 50 (new crews come aboard green at 40, but she is green enough already — this keel cost her n…
- CMD `recruit 3000 artillery for Marmont at Paris` → ✗ Berthier checks the order of battle. 'No marshal of artillery can reach Paris, Sire — none of ours stands within reach.' No commander of guns serves us — commission Marm…
- CMD `Ney, retreat` → ✓ Ney firmly objects: 'Retreat? We can still fight!' (Trust him and he will attack Kutuzov at Carniola instead.)
  - POPUP objection: Ney, Ney firmly objects: 'Retreat? We can still fight!' (Trust him and he will attack Kutuzov at Carniola instead.) → insist
- CMD `Lannes, retreat` → ✗ Lannes is not in danger. No retreat necessary.
- CMD `Soult, attack Kutuzov` → ✗ Soult cannot march on Kutuzov: Carniola is Austria's soil, and we are at peace with Austria — no corps of ours may take the field there.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Munich to Franconia (301 lost to march)
- CMD `Marmont, move to Normandy` → ✗ There is no 'Marmont' in the order of battle, Sire. Whom did you intend?
- CMD `invest in Switzerland` → ✓ Invest in Switzerland: 200 gold and 1 diplomatic point. Her loyalty rises +10 (94 → 100), and Switzerland cannot be invested in again for 3 turns. The treasury holds 4,5…
  - POPUP clarification: The Cabinet, Invest in Switzerland: 200 gold and 1 diplomatic point. Her loyalty rises +10 (94 → 100), and Switzerland cannot be invested in again for 3 turns. The treasury holds 4,560 gold and would hold 4,360 after. Invest? (yes / no) → 1 (first option: Invest)
- CMD `propose armistice to Russia` → ✓ Sire, regarding the Armistice proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #31 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russian court with your Armistice proposal. Expect a response by next turn. (1 DP spent) Talleyrand carries this letter; his Court Nation at Prussia pauses until he is home (about 1 turn). → display-only
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! Kutuzov is at Carniola, just one region away.
- CMD `recruit for Marmont` → ✗ Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.' Recruits join a marshal who can reach the depot: Ney (out of range - 6 regions …
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 4 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [continues]: Massena marches to Franconia. 2 regions to Vienna.
- ENVOYS WAITING 1 · Russia armistice
- LEDGER treasury 5391 · net +878 · threat 73 · provinces 29 (+0) · ceiling 10689 · army 143691 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2845 · trade 599 · admin 50 · tribute 712 · treaty -100 · upkeep 2150 · charges 561 · occupation 50 · blockade 375 · admiralty 92
- MISSION Courting — Prussia · net +8 a turn · the favour stands at +10 and holds while he stays — recall him once the treaty is signed · beat running
- DISPATCH: Sire — Austria would now join a league against us — relations −75. Her war would reopen the titles she ceded: Bohemia. Russia and Britain pay her 400 gold a turn against us. A league stands declared …
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover — Prussia's relations with every court, France's included, fall 15.
  - TURN EVENTS 3
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as an ultimatum.
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- COURTS: And Prussia stirs at its own design.
- DIPLO +5 medium/low (diplomatic_proposal_sent, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain binds Russia to the war against France — no separate peace for 10 turns (300g/turn)

## Turn 11 — Late February 1806
  - MAILBOX #14 Russia counter_offer_response: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice #32 → accept_counter_offer
  - POPUP proposal_result: You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia. You paid Russia 1,000 gold from the treasury. → display-only
- CMD `recall Talleyrand` → ✓ Talleyrand's mission to Prussia has been cancelled.
- CMD `improve relations with Russia` → ✓ Sire, I shall begin efforts to improve relations with Russia. This will cost 1 DP per turn. Starting this courtship shuts Reassure Ally; Bavaria, at 27, is under the 40 …
  - POPUP diplomatic_dialogue: mission #33 → start_mission
- CMD `invest in Kingdom of Italy` → ✗ The Kingdom of Italy's loyalty is already full (100/100) — the investment would buy nothing, so nothing is charged.
- CMD `recruit for Marmont` → ✗ Berthier scans the dispatches. 'No marshal is available to receive reinforcements, Sire.' Recruits join a marshal who can reach the depot: Ney (out of range - 6 regions …
- CMD `Napoleon, march to Paris` → ✓ Napoleon begins march to Paris. Route: Franconia → Swabia → Lorraine → Orleanais → Burgundy → Limousin → Paris. Arrives in 7 turns. Moves to Franconia.
- CMD `Soult, move to Dresden` → ✓ Soult moves from Bohemia to Dresden (635 lost to march)
- CMD `Bernadotte, move to Dresden` → ✓ Bernadotte moves from Bohemia to Dresden (193 lost to march)
- CMD `Talleyrand, cancel mission with Prussia` → ✗ Talleyrand is in Russia, not Prussia. Recall him from Russia, or leave him to his work.
- CMD `improve relations with Russia` → ✓ Sire, I shall begin efforts to improve relations with Russia. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Russia. …
  - POPUP diplomatic_dialogue: mission #34 → start_mission
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 8 actions, 0 attacks — Britain, Spain, the Ottoman Empire and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3, recruit×2, fortify×1, unfortify×1, garrison×1
- ORDER Massena [continues]: Massena marches to Bohemia. 1 region to Vienna.
- ORDER Napoleon [active]: Napoleon is marching to Paris (6 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 1 · Naples open borders
- LEDGER treasury 5365 · net +801 · threat 72 · provinces 29 (+0) · ceiling 10110 · army 140067 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2845 · trade 599 · admin 50 · tribute 712 · treaty -100 · upkeep 2220 · charges 568 · occupation 50 · blockade 375 · admiralty 92
- MISSION Improving Relations — Russia · net +11 a turn · he comes home when the peace is signed — recall him sooner if you would · beat running
- DISPATCH: Sire — a truce with Russia is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns. The ledger stands: the war score reads 0 for France (1 battle, 0 decisives kept); the war is 10 …
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 4
- DIPLO +7 medium/low (diplomatic_treaty_signed, province_changed_hands, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, diplomatic_ai_ai_treaty, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG diplomatic_ai_ai_treaty: Russia and Sweden sign a Defensive Alliance
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → accept
- CMD `recruit infantry in Vienna` → ✗ Berthier frowns. 'We do not control Vienna, Your Majesty. Recruitment is impossible there.'
- CMD `guarantee Kingdom of Italy` → ✗ Kingdom of Italy is already under French protection as a vassal.
- CMD `land Marmont in Munster` → ✗ Choose who embarks, Sire — click a coastal province on the map for its landing chip. A corps of 15,000 or fewer sails; THE ADMIRALTY (press T, then 7; Alt+T, then Alt+7 …
- CMD `yes` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — 'Ney, march to Bohemia', perha…
- CMD `Massena, move to Munich` → ✓ Massena begins marching to Munich (distance: 2). Moved to Franconia. Route: Franconia -> Munich. Massena's march to Vienna is set aside.
- CMD `Soult, move to Franconia` → ✓ Soult moves from Dresden to Franconia (405 lost to march)
- CMD `build supply depot in Vienna` → ✗ Cannot build in Vienna — not controlled by France
- CMD `buy substitutes for Murat` → ✗ There is no market in cavalry, Sire — a substitute may carry a musket, not ride a trooper's horse nor serve a gun. Murat commands cavalry; the class must be called.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 8 actions, 2 attacks — Britain, Spain, the Ottoman Empire and 6 other courts stirred as well, but their formations remain beyond our sight. — Brunswick attacks Wallmoden · Brunswick attacks Hanover
  - 🏴 Prussia: Brunswick attacks Wallmoden — Osnabruck CAPTURED! (was Hanover) (secured)
  - ⚔ Brunswick (lost 338) vs Wallmoden (lost 1282) — A grievous defeat for Wallmoden, Sire. The losses are severe. And Wallmoden was taken on that field — Prussia holds him. — Frederick's Drill +10% (Brunswick)
  - verbs: wait×3, attack×2, move×2, recruit×1
- ORDER Massena [active]: Massena is marching to Munich (2 turns remaining).
- ORDER Napoleon [continues]: Napoleon marches to Swabia. 5 regions to Paris.
- LEDGER treasury 6089 · net +464 · threat 71 · provinces 29 (+0) · ceiling 8784 · army 133461 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2845 · trade 624 · admin 50 · tribute 712 · treaty -100 · upkeep 2432 · charges 703 · occupation 50 · blockade 390 · admiralty 92
- MISSION Improving Relations — Russia · net +11 a turn · he comes home when the peace is signed — recall him sooner if you would · beat running
- DISPATCH: Sire — Ney, Davout, Soult, Murat and Massena stand 97,635 men at Franconia, which feeds 60,000. 37,635 too many. 10,060 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simpl…
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - RAIL crisis_brewing: THE BREWING CRISIS: Hesse will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the war…
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as an ultimatum.
- DIPLO +8 medium/low (diplomatic_treaty_signed, province_changed_hands, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 13 — Late March 1806
- CMD `Massena, march to Provence` → ✓ Massena begins march to Provence. Route: Munich → Milan → Piedmont → Provence. Arrives in 4 turns. Moves to Munich. He will drop this order for any battle within two pro…
- CMD `Marmont, march to Provence` → ✗ There is no 'Marmont' in the order of battle, Sire. Whom did you intend?
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory #36 → execute_suggestion
  - POPUP proposal_result: I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches. → display-only
- CMD `commission Oudinot` → ✓ Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- SPENT 3500g on this turn's orders
- enemy phase: 10 actions, 2 attacks — Spain, the Ottoman Empire, Sweden and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Ney · Shrapnel bombards Davout
  - verbs: wait×3, attack×2, recruit×2, unfortify×1, fortify×1, drill×1
- ORDER Massena [active]: Massena is marching to Provence (3 turns remaining).
- ORDER Napoleon : Berthier: 'Cannon fire at Franconia, Sire. Investigate?'
  - POPUP strategic_interrupt: Napoleon, cannon_fire, Berthier: 'Cannon fire at Franconia, Sire. Investigate?' → investigate
- ENVOYS WAITING 2 · Britain armistice losing · Britain settlement offer
- LEDGER treasury 3710 · net +1172 · threat 72 · provinces 29 (+0) · ceiling 10363 · army 132964 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2845 · trade 624 · admin 50 · tribute 937 · treaty -100 · upkeep 2352 · charges 300 · occupation 50 · blockade 390 · admiralty 92
- MISSION Improving Relations — Russia · net +11 a turn · he comes home when the peace is signed — recall him sooner if you would · beat running
- DISPATCH: Sire — Ney, Davout, Soult and Murat stand 65,474 men at Franconia, which feeds 60,000. 5,474 too many. 9,124 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large…
  - RAIL balance_of_europe_shifted: French System leads the current largest alignment at 50% of active European bloc power. Prussia is the decisive non-France slice of the bloc; letting…
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle the War with the Third Coalition — Britain + Russia.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,850 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 2
- COURTS: The court of Saxony eases over The Wettin Crown — joining the stronger side for pay is now the length of its tether.
- COURTS: The court of Hesse eases over The Westphalian Duchy — joining the stronger side for pay is now the length of its tether.
- DIPLO +9 medium/low (province_changed_hands ×2, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, coercive_demand, agenda_shift ×2, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between France and Prussia lapses
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 1 more — Prussia is not forgiven

## Turn 14 — Early April 1806
  - MAILBOX #16 Britain incoming_proposal: Britain — Armistice → activated
  - MAILBOX #17 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #37 → accept_ai_proposal
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #38 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Britain, armistice_losing #37 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #38 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 16.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 16.
- CMD `Oudinot, march to Provence` → ✓ Oudinot begins march to Provence. Route: Limousin → Lyonnais → Provence. Arrives in 3 turns. Moves to Limousin. He will drop this order for any battle within two provinc…
- CMD `buy substitutes for Ney` → ✓ Ney takes 3,000 substitutes into the line at Franconia — 922 gold, and not a man off the rolls. Morale 61% -> 53% (bought men muster at 25%). They come up in drafts of 3…
- CMD `end turn` → ✓ Turn 14 ended. Turn 15 begins!
- SPENT 922g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- ORDER Massena [continues]: Massena marches to Milan. 2 regions to Provence.
- ORDER Oudinot [active]: Oudinot is marching to Provence (2 turns remaining).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Soult and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: Holland, client_petition #39 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 2 · Holland client petition · The Secretariat moment letter
- LEDGER treasury 5917 · net +2339 · threat 73 · provinces 29 (+0) · ceiling 21221 · army 132043 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 2845 · trade 624 · admin 50 · tribute 600 · treaty -100 · upkeep 1032 · charges 598 · occupation 50
- MISSION Improving Relations — Russia · net +11 a turn · he comes home when the peace is signed — recall him sooner if you would · beat running
- DISPATCH: Sire — a truce with Britain holds the guns silent — the war is paused, not over. The truce grants safe passage home.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -9 for France (1 battle, 0 decisives kept); the war is 1…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL crisis_passed: Hesse stands down over Hanover, Sire — the moment passed — opportunism decayed.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 7
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: And Austria and Saxony stir at their own designs.
- DIPLO +9 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_vassal_contingent, paymaster_subsidy, diplomatic_ai_ai_treaty, blockade_broken ×2, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG diplomatic_ai_ai_treaty: Saxony and Austria sign a Non-Aggression Pact
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG moment: The Arch-Chancellor's Letters — an affair of state is laid before the Emperor
  - LOG balance_of_europe_shifted: French System leads the current largest alignment at 50% of active European bloc power. Prussia is the decisive non-France slice of the bloc; letting…
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 15 — Late April 1806
  - MAILBOX #19 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #40 → reject_ai_proposal
- CMD `Massena, march to Provence` → ✓ Massena is already carrying out that order. No change.
- CMD `Lannes, move to Dresden` → ✓ Lannes begins marching to Dresden (distance: 3). Moved to Munich. Route: Munich -> Franconia -> Dresden.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Franconia to Swabia (219 lost to march)
- CMD `build market in Vienna` → ✗ Cannot build in Vienna — not controlled by France
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 1 action unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, stance_change×1
- ORDER Lannes [active]: Lannes is marching to Dresden (3 turns remaining).
- ORDER Massena [continues]: Massena marches to Piedmont. 1 region to Provence.
- ORDER Oudinot [continues]: Oudinot marches to Lyonnais. 1 region to Provence.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 6953 · net +838 · threat 73 · provinces 29 (+0) · ceiling 11626 · army 128827 · vassals Holland 99 · Kingdom of Italy 98 · Switzerland 94
  - NET income 2845 · trade 624 · admin 50 · tribute 600 · treaty -100 · upkeep 2152 · charges 887 · occupation 50 · admiralty 92
- MISSION Improving Relations — Russia · net +8 a turn · he comes home when the peace is signed — recall him sooner if you would · beat running
- DISPATCH: Sire — the truce with Russia has collapsed — the war resumes where it stood, at its age, with its ledger.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 4
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as joining the stronger side for pay.
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, blockade_broken, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG moment: The Arch-Chancellor's Letters — the Emperor answers: Let the Council act

## Turn 16 — Early May 1806
  - MAILBOX #20 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #41 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Kutuzov is at Tyrol, just one region away.
- CMD `Murat, drill` → ✗ Murat cannot drill with enemy forces nearby! Kutuzov is at Tyrol, just one region away.
- CMD `Bernadotte, move to Franconia` → ✓ Bernadotte moves from Dresden to Franconia (143 lost to march)
- CMD `build training ground at Paris` → ✓ Construction started: Training Ground in Paris (2 turns, 250 gold)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 3 actions unused) Turn 17 begins!
- SPENT 250g on this turn's orders
- enemy phase: 4 actions, 0 attacks — Britain, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, form_square×1, recruit×1, wait×1
- ORDER Lannes [continues]: Lannes marches to Franconia. 1 region to Dresden.
- ORDER Massena [completed]: Massena arrives at Provence. Massena: "Accomplished. The men want a battle, not another road."
- ORDER Oudinot [completed]: Oudinot arrives at Provence. Oudinot: "Accomplished. The men want a battle, not another road."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult demands to be heard → acknowledge
  -     ↳ Soult's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #42 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +7 (93 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7286 · net +261 · threat 73 · provinces 29 (+0) · ceiling 8716 · army 124261 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 100
  - NET income 2845 · trade 624 · admin 50 · treaty -100 · upkeep 2052 · charges 964 · occupation 50 · admiralty 92
- MISSION Improving Relations — Russia · net +8 a turn · he comes home when the peace is signed — recall him sooner if you would · beat running
- DISPATCH: Sire — St Petersburg now pays Sweden 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 4 turns (4 DP); buying off her design …
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Sweden against France (400g/turn)
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 17 — Late May 1806
- CMD `Talleyrand, cancel mission with Russia` → ✓ Talleyrand's mission to Russia has been cancelled.
- CMD `improve relations with Britain` → ✓ Sire, I shall begin efforts to improve relations with Britain. This will cost 1 DP per turn. Starting this courtship shuts Reassure Ally; Bavaria, at 21, is under the 40…
  - POPUP diplomatic_dialogue: mission #43 → start_mission
- CMD `Marmont, attack Wellesley` → ✗ There is no 'Marmont' in the order of battle, Sire. Whom did you intend?
- CMD `Oudinot, attack Wellesley` → ✗ Cannot attack Wellesley — armistice with Britain (2 turns remaining).
- CMD `Massena, march to Paris` → ✓ Massena begins march to Paris. Route: Lyonnais → Limousin → Paris. Arrives in 3 turns. Moves to Lyonnais. He will drop this order for any battle within two provinces in …
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 2 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Austria, Prussia and 10 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Russia: Kutuzov moves to Bohemia — Bohemia falls (was France)
  - verbs: move×1
- ORDER Lannes [completed]: Lannes arrives at Dresden. Lannes: "It is done. Point me at something that shoots back, Sire."
- ORDER Massena [active]: Massena is marching to Paris (2 turns remaining).
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 7417 · net +90 · threat 71 · provinces 28 (-1) · ceiling 7899 · army 121651 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 100
  - NET income 2645 · trade 624 · admin 50 · treaty -100 · upkeep 1992 · charges 1005 · admiralty 92 · infrastructure 40
- MISSION Improving Relations — Britain · net +11 a turn · he comes home when the peace is signed — recall him sooner if you would · beat running
- DISPATCH: Sire — Bohemia has been taken by Russia.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 2
- DIPLO +6 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, hegemony_relaxation_aside, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG moment: The Throne of Holland — a letter of the record is laid before the Emperor

## Turn 18 — Early June 1806
  - MAILBOX #22 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #44 → reject_ai_proposal
- CMD `Oudinot, attack Provence` → ✗ Provence is already controlled by France
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Austria, Prussia and 10 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden attacks Lannes · Kutuzov attacks Lannes
  - ⚔ Buxhowden (lost 2172) vs Lannes (lost 3793) — Lannes stood alone, Sire. Davout and Bernadotte never came. — Slow to concentrate's orders reached Kutuzov too late.
  - ⚔ Kutuzov (lost 898) vs Lannes (lost 2754) — Not one corps reached Lannes. Bernadotte was expected; Lannes fought the battle single-handed.
  - verbs: attack×2
- ORDER Massena [continues]: Massena marches to Limousin. 1 region to Paris.
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 7417 · net +247 · threat 37 · provinces 28 (+0) · ceiling 8689 · army 111744 · vassals Holland 92 · Kingdom of Italy 93 · Switzerland 96
  - NET income 2645 · trade 624 · admin 50 · treaty -100 · upkeep 1792 · charges 1048 · admiralty 92 · infrastructure 40
- MISSION ended: Improving Relations — Britain, the peace was signed
- DISPATCH: Sire — Lannes's corps has been broken at Dresden. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Russia has offered terms to settle the War with the Third Coalition — Britain + Russia.
  - RAIL diplomatic_armistice_expired_peace: The armistice between Britain and France has concluded. Peace declared.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_coalition_dissolved, diplomatic_mission_completed, diplomatic_relation_shift)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 71 to 35; Russia remains at war with us.
  - LOG instrument_lapsed: The bond between Britain and Russia lapses — Britain left the war first
  - LOG moment: The Throne of Holland — the Emperor answers: Keep the Republic

## Turn 19 — Late June 1806
  - MAILBOX #23 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #45 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Russia, Britain, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [completed]: Massena arrives at Paris. Massena: "Accomplished. The men want a battle, not another road."
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 7684 · net +197 · threat 39 · provinces 28 (+0) · ceiling 8681 · army 108639 · vassals Holland 91 · Kingdom of Italy 92 · Switzerland 96
  - NET income 2645 · trade 624 · admin 50 · treaty -100 · upkeep 1772 · charges 1118 · admiralty 92 · infrastructure 40
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 20 — Early July 1806
  - MAILBOX #24 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #46 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Russia, Britain, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 9077 · net +1151 · threat 41 · provinces 28 (+0) · ceiling 15703 · army 105716 · vassals Holland 90 · Kingdom of Italy 91 · Switzerland 96
  - NET income 2645 · trade 624 · admin 50 · treaty -100 · upkeep 800 · charges 1228 · infrastructure 40
- DISPATCH: Sire — a truce with Russia is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns. The ledger stands: the war score reads -10 for France (2 battles, 0 decisives kept); the war is …
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 4
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Redeem Italy — joining the stronger side for pay is now the length of its tether.
- COURTS: And Sardinia and Saxony stir at their own designs.
- DIPLO +3 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Russia, Britain, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10244 · net +964 · threat 43 · provinces 28 (+0) · ceiling 15796 · army 102938 · vassals Holland 89 · Kingdom of Italy 90 · Switzerland 96
  - NET income 2645 · trade 624 · admin 50 · treaty -100 · upkeep 784 · charges 1431 · infrastructure 40
- DISPATCH: Sire — the levy has stood open 4 turns. 172 gold puts 10,000 foot in the line at Paris under Massena — 'recruit infantry in Paris'; the conscripts do not improve with keeping.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Russia, Britain, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 11224 · net +1147 · threat 45 · provinces 28 (+0) · ceiling 17829 · army 100300 · vassals Holland 88 · Kingdom of Italy 89 · Switzerland 96
  - NET income 2645 · trade 624 · admin 50 · tribute 337 · treaty -100 · upkeep 768 · charges 1601 · infrastructure 40
- DISPATCH: Sire — Europe has watched us 5 quiet turns. At this pace the courts consult on turn 40 and declare on turn 43: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain. Held b…
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor

## Turn 23 — Late August 1806
  - MAILBOX #25 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #47 → reject_ai_proposal
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Russia, Britain, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 12395 · net +1343 · threat 45 · provinces 28 (+0) · ceiling 20127 · army 97793 · vassals Holland 87 · Kingdom of Italy 88 · Switzerland 96
  - NET income 2645 · trade 624 · admin 50 · tribute 712 · treaty -100 · upkeep 744 · charges 1804 · infrastructure 40
- DISPATCH: Sire — Britain would now join a league against us — relations −54. The price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design costs 1,248 gold (+5 relations; she…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Prussia.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land

## Turn 24 — Early September 1806
  - MAILBOX #26 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #48 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (87 → 97); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 14182 · net +1833 · threat 45 · provinces 28 (+0) · ceiling 32510 · army 95411 · vassals Holland 97 · Kingdom of Italy 87 · Switzerland 96
  - NET income 2645 · trade 624 · admin 50 · tribute 600 · treaty -100 · upkeep 728 · charges 1218 · infrastructure 40
- DISPATCH: Sire — peace with Russia is signed. The truce has ripened into peace, signed on the held line.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL diplomatic_armistice_expired_peace: The armistice between France and Russia has concluded. Peace declared.
  - TURN EVENTS 1
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
  - MAILBOX #27 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #49 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (87 → 97); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15664 · net +1334 · threat 45 · provinces 28 (+0) · ceiling 29000 · army 93148 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 624 · admin 50 · tribute 225 · treaty -100 · upkeep 704 · charges 1366 · infrastructure 40
- DISPATCH: Sire — London now pays Vienna 300 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1…
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16998 · net +1201 · threat 45 · provinces 28 (+0) · ceiling 29000 · army 91000 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 624 · admin 50 · tribute 225 · treaty -100 · upkeep 704 · charges 1499 · infrastructure 40
- DISPATCH: Sire — the ordinance allows 39,000 more men to the establishment, and the depots hold 100,000. 10,000 foot cost 172 gold at Paris under Massena — 'recruit infantry in Paris'.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 18185 · net +1068 · threat 45 · provinces 28 (+0) · ceiling 28860 · army 88958 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 586 · admin 50 · tribute 225 · treaty -100 · upkeep 680 · charges 1618 · infrastructure 40
- DISPATCH: Sire — relations between Bavaria and France have collapsed: Alliance → Defensive Alliance.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Bavaria–France (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG moment: The Arch-Chancellor's Letters — an affair of state is laid before the Emperor

## Turn 28 — Early November 1806
  - MAILBOX #28 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #50 → reject_ai_proposal
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 19269 · net +976 · threat 45 · provinces 28 (+0) · ceiling 29020 · army 87018 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 586 · admin 50 · tribute 225 · treaty -100 · upkeep 664 · charges 1726 · infrastructure 40
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +9% this morning; the courts have begun to notice that he can be beaten.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Arch-Chancellor's Letters — the Emperor answers: Let the Council act
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Russia open borders
- LEDGER treasury 20261 · net +892 · threat 45 · provinces 28 (+0) · ceiling 29180 · army 85174 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 586 · admin 50 · tribute 225 · treaty -100 · upkeep 648 · charges 1826 · infrastructure 40
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 41 and declare on turn 44: Austria, Britain and 3 lesser courts would march.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 30 — Early December 1806
  - MAILBOX #29 Russia incoming_proposal: Russia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Russia, open_borders #51 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: Peace → Open Borders with Russia. → display-only
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21202 · net +847 · threat 45 · provinces 28 (+0) · ceiling 29670 · army 83424 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 611 · admin 50 · tribute 225 · treaty -100 · upkeep 624 · charges 1920 · infrastructure 40
- DISPATCH: Sire — London now pays St Petersburg 400 gold a turn against us. The coalition has its paymaster; it lacks only its armies.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22049 · net +1100 · threat 45 · provinces 28 (+0) · ceiling 33040 · army 81761 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 611 · admin 50 · tribute 562 · treaty -100 · upkeep 624 · charges 2004 · infrastructure 40
- DISPATCH: Sire — St Petersburg now pays Vienna 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design …
  - RAIL allegiance_settled: The bidding for Hesse is closed in our favour, but our relations are too cool for any pact the table can sign.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 32 — Early January 1807
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 23165 · net +1379 · threat 45 · provinces 28 (+0) · ceiling 36950 · army 80181 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 611 · admin 50 · tribute 937 · treaty -100 · upkeep 608 · charges 2116 · infrastructure 40
- DISPATCH: Sire — the ordinance allows 49,819 more men to the establishment, and the depots hold 100,000. 10,000 foot cost 172 gold at Paris under Massena — 'recruit infantry in Paris'.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor

## Turn 33 — Late January 1807
  - MAILBOX #30 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #52 → reject_ai_proposal
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24560 · net +1255 · threat 45 · provinces 28 (+0) · ceiling 37110 · army 78680 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 611 · admin 50 · tribute 937 · treaty -100 · upkeep 592 · charges 2256 · infrastructure 40
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 41 and declare on turn 44: Austria, Britain and 3 lesser courts would march.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 25773 · net +1092 · threat 45 · provinces 28 (+0) · ceiling 36690 · army 77255 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 561 · admin 50 · tribute 937 · treaty -100 · upkeep 584 · charges 2377 · infrastructure 40
- DISPATCH: Sire — relations between France and Spain have collapsed: Alliance → Defensive Alliance.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (Alliance → Defensive Alliance)

## Turn 35 — Late February 1807
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 26873 · net +990 · threat 45 · provinces 28 (+0) · ceiling 36770 · army 75901 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 561 · admin 50 · tribute 937 · treaty -100 · upkeep 576 · charges 2487 · infrastructure 40
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 41 and declare on turn 44: Austria, Britain and 3 lesser courts would march.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 36 — Early March 1807
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 27871 · net +898 · threat 45 · provinces 28 (+0) · ceiling 36850 · army 74614 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 561 · admin 50 · tribute 937 · treaty -100 · upkeep 568 · charges 2587 · infrastructure 40
- DISPATCH: Sire — London now pays Vienna 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design costs 1…
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 37 — Late March 1807
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 28777 · net +816 · threat 49 · provinces 28 (+0) · ceiling 36930 · army 73392 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 561 · admin 50 · tribute 937 · treaty -100 · upkeep 560 · charges 2677 · infrastructure 40
- DISPATCH: Sire — the allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegiance.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Austria, …
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Remounts — an affair of state is laid before the Emperor

## Turn 38 — Early April 1807
  - MAILBOX #31 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #53 → reject_ai_proposal
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 29609 · net +749 · threat 53 · provinces 28 (+0) · ceiling 37090 · army 72231 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 561 · admin 50 · tribute 937 · treaty -100 · upkeep 544 · charges 2760 · infrastructure 40
- DISPATCH: Sire — Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
  - TURN EVENTS 1
- COURTS: The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG moment: The Remounts — the Emperor answers: Let the depots wait

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 30366 · net +681 · threat 57 · provinces 28 (+0) · ceiling 37170 · army 71128 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 561 · admin 50 · tribute 937 · treaty -100 · upkeep 536 · charges 2836 · infrastructure 40
- DISPATCH: Sire — the moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Prussia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 31055 · net +620 · threat 60 · provinces 28 (+0) · ceiling 37250 · army 70080 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2645 · trade 561 · admin 50 · tribute 937 · treaty -100 · upkeep 528 · charges 2905 · infrastructure 40
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sweden → Bid for Their Allegi…
  - TURN EVENTS 1
- DIPLO +6 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, diplomatic_coalition_brewing, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Alliance → Defensive Alliance)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Austria, Sweden and Sardinia alarmed (threat: 60)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Saxony (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - ⚠ SCRIPT PRECONDITION — every expedition line in the script was refused (1); this digest is NOT evidence about naval expeditions

---
finished: **completed** · commands 155 · popups 87 · battles 7
