# Playtest digest — PROP-M

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → confirm
  - POPUP proposal_result: Talleyrand departs for the Austrian court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte
  - ⚔ Archduke Charles (lost 1777) vs Bernadotte (lost 6424) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 1557 · net +1078 · threat 64 · provinces 28 · ceiling 10068 · army 182467 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2540 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 6,424 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - TURN EVENTS 2
- DIPLO +10 medium/low (diplomatic_proposal_sent, law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. Prussia paid 30 gold into the treasury. → display-only
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #4 → confirm
  - POPUP proposal_result: Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte · Mack attacks Bernadotte
  - 🏴 Austria: Archduke Charles attacks Bernadotte — Franconia CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 702) vs Bernadotte (lost 6534) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Mack (lost 7910) vs Bernadotte (lost 409, own corps) — Lannes, Massena and Teulie's timely arrival bolstered Bernadotte's position. Well-coordinated, Sire. — Berthier: the corps marched apart and arrived together.
  - verbs: attack×2, move×1, wait×1
  - POPUP proposal_result: Britain has rejected our Peace Treaty. → display-only
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 2 · Portugal open borders · Denmark non aggression
- LEDGER treasury 2013 · net +951 · threat 62 · provinces 28 (+0) · ceiling 8520 · army 169215 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 93
  - NET income 2590 · trade 425 · admin 50 · tribute 937 · upkeep 2694 · charges 1 · blockade 266 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Britain with a response.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — joining the stronger side for pay is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, law_enacted_abroad, province_changed_hands, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #7 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russian court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 7 actions, 2 attacks — Russia, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte · Archduke John attacks Munich
  - 🏴 Austria: Archduke John attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 99) vs Bernadotte (lost 2069) — The hills were ours, but Archduke Charles took them. Bernadotte's position was overrun. And Bernadotte was taken on tha…
  - verbs: stance_change×2, attack×2, fortify×1, naval_expedition×1, unfortify×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1448, own corps) vs Mack (lost 33337) — Reinforcements! Ney, Davout, Lannes, Massena, Napoleon and Teulie marched onto the field beside Murat. The enemy's adva… — The corps system brought Lannes in. — The corps system brought Teulie in. — Berthier: the corps marched apart and arrived together.
  - POPUP proposal_result: Russia has rejected our Peace Treaty. → display-only
- ENVOYS WAITING 2 · Saxony open borders · Hesse non aggression
- LEDGER treasury 2472 · net +617 · threat 68 · provinces 28 (+0) · ceiling 6462 · army 153355 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 90
  - NET income 2590 · trade 500 · admin 50 · tribute 937 · upkeep 2986 · charges 72 · blockade 312 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - TURN EVENTS 6
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_we_threshold, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `propose peace with Austria` → ✗ Talleyrand advises patience, Sire. Austria refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Munich
  - 🏴 Bavaria: Deroy attacks Munich — The last 2,000 of the garrison of Munich give way. · Region captured: Munich (was Austria) (secured)
  - verbs: attack×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 57, own corps) vs Mack (lost 10700) — Ney, Davout, Murat, Massena, Napoleon and Teulie's timely arrival bolstered Lannes's position. Well-coordinated, Sire.
- ENVOYS WAITING 1 · PapalStates open borders
- LEDGER treasury 3157 · net +511 · threat 64 · provinces 28 (+0) · ceiling 6397 · army 145534 · vassals Holland 97 · Switzerland 89
  - NET income 2590 · trade 562 · admin 50 · tribute 562 · upkeep 2630 · charges 182 · blockade 351 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is destroyed at Franconia — his corps annihilated, his name struck from their order of battle.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 4
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +9 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, province_changed_hands ×3, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG moment: Britain decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Russia decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG ai_ai_proposal_refused: Britain rebuffs Portugal (open borders agreement)

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `propose peace with Britain` → ✗ Talleyrand advises patience, Sire. Britain refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Provence
  - 🏴 Austria: Archduke John attacks Provence — Region captured: Provence (was France) (secured)
  - verbs: attack×1, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 3898 · net +491 · threat 62 · provinces 27 (-1) · ceiling 6931 · army 138605 · vassals Holland 97 · Switzerland 87
  - NET income 2440 · trade 587 · admin 50 · tribute 562 · upkeep 2384 · charges 306 · blockade 368 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. Archduke John's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, …
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +4 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (200g/turn)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign an Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign an Open Borders Agreement

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Russia` → ✗ Talleyrand advises patience, Sire. Russia refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Lyonnais
  - 🏴 Austria: Archduke John attacks Lyonnais — Region captured: Lyonnais (was France) (secured)
  - verbs: attack×1, wait×1
  - POPUP marshal_audience: shadow_command, Marshal Ney asks for a command → detach
  -     ↳ Ney straightens. "You will not regret it, Sire." March him to Savoy and the front is his — the order is yours…
- LEDGER treasury 4219 · net +260 · threat 60 · provinces 26 (-1) · ceiling 5783 · army 132092 · vassals Holland 97 · Switzerland 96
  - NET income 2360 · trade 587 · admin 50 · tribute 337 · upkeep 2248 · charges 368 · blockade 368 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. Archduke John's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, …
  - TURN EVENTS 3
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Austria rebuffs Saxony (defensive alliance)

## Turn 7 — Late December 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #12 → confirm
  - POPUP proposal_result: Talleyrand departs for the Austrian court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Savoy
  - 🏴 Austria: Archduke John attacks Savoy — Region captured: Savoy (was France) (secured)
  - verbs: attack×1
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
  - POPUP marshal_audience: shadow_command, Marshal Davout asks for a command → detach
  -     ↳ Davout straightens. "You will not regret it, Sire." March him to Lyonnais and the front is his — the order is…
  - POPUP diplomatic_dialogue: moment_letter #13 → reject_ai_proposal
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 4521 · net +232 · threat 58 · provinces 26 (+0) · ceiling 5680 · army 125969 · vassals Holland 97 · Switzerland 95
  - NET income 2300 · trade 587 · admin 50 · tribute 337 · upkeep 2080 · charges 504 · blockade 368 · admiralty 90
- DISPATCH: Sire — Savoy has fallen to Austria. Enemy colours fly over French homeland soil. Archduke John's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as …
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_proposal_sent, law_enacted_abroad ×2, province_changed_hands ×2, diplomatic_dp_regen)
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her

## Turn 8 — Early January 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #14 → confirm
  - POPUP proposal_result: Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Piedmont · Archduke Charles attacks Franche-Comte
  - 🏴 Austria: Archduke John attacks Piedmont — Region captured: Piedmont (was Bavaria) (secured)
  - 🏴 Austria: Archduke John moves to Milan — Milan falls (was Bavaria) and is secured
  - 🏴 Austria: Archduke Charles attacks Franche-Comte — Region captured: Franche-Comte (was France) (secured)
  - verbs: attack×2, move×1
  - POPUP proposal_result: Britain has rejected our Peace Treaty. → display-only
- LEDGER treasury 4752 · net +173 · threat 56 · provinces 25 (-1) · ceiling 5593 · army 120310 · vassals Holland 97 · Switzerland 94
  - NET income 2220 · trade 587 · admin 50 · tribute 337 · upkeep 2000 · charges 563 · blockade 368 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a…
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Provence.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Britain with a response.
  - RAIL third_party_peace: THE CONGRESS: Bavaria and Austria have made their peace without France. Bavaria, beaten (-28), sues for peace and Austria takes it on the held line; …
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_proposal_sent, province_changed_hands ×4, diplomatic_dp_regen, paymaster_subsidy)

## Turn 9 — Late January 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #15 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russian court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 2 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Russia peace · Austria settlement offer
- LEDGER treasury 4915 · net +117 · threat 54 · provinces 25 (+0) · ceiling 5470 · army 115112 · vassals Holland 97 · Switzerland 93
  - NET income 2220 · trade 587 · admin 50 · tribute 337 · upkeep 1900 · charges 609 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Franche-Comte, Provence and Savoy lie in enemy hands. Austria holds them.
  - RAIL settlement_offer_arrival: Austria, for Britain, Austria and Russia, has offered terms to settle the War for Franche-Comte — Britain + Austria + Russia.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,188g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 1
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- DIPLO +6 medium/low (diplomatic_proposal_sent, enemy_marshal_commissioned ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG third_party_peace: THE CONGRESS: Bavaria and Austria make peace without France
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 10 — Early February 1806
  - MAILBOX #11 Russia counter_offer_response: Russia — Peace Treaty → activated
  - MAILBOX #10 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Russia, peace #17 → accept_counter_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Austria. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #18 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Franche-Comte — the table with Austria + Britain + Russia (5 pairs resolved). Status quo: Franche-Comte, Provence and Savoy stay Austrian by the treaty. Prisoners: Bernadotte comes home to Paris under this peace. → display-only
  - POPUP diplomatic_dialogue: Russia, peace #17 → reject_counter_offer
  - POPUP proposal_result: You have rejected Russia's counter-proposal. Relations cooled slightly. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → accept_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: nothing visible — Britain, Austria, Spain and 2 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #19 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +5 (95 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 6835 · net +1333 · threat 30 · provinces 25 (+0) · ceiling 17084 · army 115325 · vassals Holland 100 · Switzerland 92
  - NET income 2220 · trade 587 · admin 50 · upkeep 896 · charges 628
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Massena and Napoleon have been 6 turns over what Franconia can feed. 35,209 men dead. The country will ask where the army went. Bavaria's magazines feed us as our o…
  - RAIL status_quo_conceded: Franche-Comte, Provence and Savoy — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Sire, the white peace of the War for Franche-Comte — the table with Austria + Britain + Russia takes nothing and gives nothing. Spain is left out: -7…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, coercive_demand, blockade_broken ×3, agenda_shift)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 54 to 27.
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Austria, Spain and 2 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Lannes: They settle into cold war.
- LEDGER treasury 8208 · net +1194 · threat 33 · provinces 25 (+0) · ceiling 17392 · army 110905 · vassals Holland 99 · Switzerland 91
  - NET income 2220 · trade 587 · admin 50 · upkeep 856 · charges 807
- DISPATCH: Sire — 3 turns now with Franche-Comte, Provence and Savoy in enemy hands. The country counts every one of them.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover — Prussia's relations with every court, France's included, fall 15.
  - TURN EVENTS 4
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as an ultimatum.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: And Saxony stirs at its own design.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_relation_shift)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Austria, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 9661 · net +1307 · threat 36 · provinces 25 (+0) · ceiling 22730 · army 106811 · vassals Holland 98 · Switzerland 90
  - NET income 2260 · trade 587 · admin 50 · upkeep 824 · charges 766
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Massena and Napoleon have been 6 turns over what Franconia can feed. 30,281 men dead. The country will ask where the army went. Bavaria's magazines feed us as our o…
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Austria.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 1
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as an ultimatum.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as alliance.
- DIPLO +3 medium/low (province_changed_hands, enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia and Hesse (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia and Hesse (design ask)

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Austria, Spain and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10992 · net +1423 · threat 39 · provinces 25 (+0) · ceiling 25220 · army 103011 · vassals Holland 97 · Switzerland 89
  - NET income 2260 · trade 587 · admin 50 · tribute 225 · upkeep 800 · charges 899
- DISPATCH: Sire — Hesse moves toward war with Hanover. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Hesse will move on Hanover. You may compensate (1,284g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war…
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 3 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 12447 · net +1310 · threat 42 · provinces 25 (+0) · ceiling 25540 · army 99478 · vassals Holland 96 · Switzerland 88
  - NET income 2260 · trade 587 · admin 50 · tribute 225 · upkeep 768 · charges 1044
- DISPATCH: Sire — Austria, Britain and Russia would now join a league against us (relations −75, −85 and −80). The Balance of Europe names the price to keep each out.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,610 gold. Prussia is now free to look elsewhere.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 1
- COURTS: The court of Saxony eases over The Wettin Crown — alliance is now the length of its tether.
- DIPLO +7 medium/low (law_enacted_abroad, province_changed_hands ×2, diplomatic_dp_regen, coercive_demand, agenda_shift ×2)
  - LOG ai_ai_proposal_refused: Russia and Austria rebuff Saxony (defensive alliance)

## Turn 15 — Late April 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #20 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13564 · net +1005 · threat 45 · provinces 25 (+0) · ceiling 23610 · army 96185 · vassals Holland 95 · Switzerland 98
  - NET income 2260 · trade 587 · admin 50 · upkeep 736 · charges 1156
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria, Prussia and 4 lesser courts would march.
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - RAIL crisis_passed: Hesse stands down over Hanover, Sire — the moment passed — opportunism decayed.
  - TURN EVENTS 1
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: And Austria stirs at its own design.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 14569 · net +905 · threat 45 · provinces 25 (+0) · ceiling 23610 · army 93110 · vassals Holland 94 · Switzerland 98
  - NET income 2260 · trade 587 · admin 50 · upkeep 736 · charges 1256
- DISPATCH: Sire — Hesse stands down over Hanover; the moment passed.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Throne of Holland — a letter of the record is laid before the Emperor

## Turn 17 — Late May 1806
  - MAILBOX #14 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #21 → reject_ai_proposal
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15534 · net +868 · threat 45 · provinces 25 (+0) · ceiling 24210 · army 90207 · vassals Holland 93 · Switzerland 98
  - NET income 2280 · trade 587 · admin 50 · upkeep 696 · charges 1353
- DISPATCH: Sire — the ordinance allows 32,293 more men to the establishment, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris under Bernadotte — 'recruit infantry in Paris'.
  - TURN EVENTS 1
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as joining the stronger side for pay.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG moment: The Throne of Holland — the Emperor answers: Keep the Republic
  - LOG moment: Britain decrees the Remounts for 8 turns (1,500 gold)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16418 · net +1133 · threat 45 · provinces 25 (+0) · ceiling 27740 · army 87449 · vassals Holland 92 · Switzerland 98
  - NET income 2280 · trade 587 · admin 50 · tribute 337 · upkeep 680 · charges 1441
- DISPATCH: Sire — the enemy has held Franche-Comte, Provence and Savoy 10 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 1
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 17583 · net +1048 · threat 45 · provinces 25 (+0) · ceiling 28060 · army 84829 · vassals Holland 91 · Switzerland 98
  - NET income 2280 · trade 587 · admin 50 · tribute 337 · upkeep 648 · charges 1558
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia, Austria, Prussia and 4 lesser courts would march.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18302 · net +647 · threat 45 · provinces 25 (+0) · ceiling 24770 · army 82340 · vassals Holland 100 · Switzerland 98
  - NET income 2280 · trade 587 · admin 50 · upkeep 640 · charges 1630
- DISPATCH: Sire — Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Saxony (defensive alliance)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

---
finished: **completed** · commands 30 · popups 47 · battles 6
