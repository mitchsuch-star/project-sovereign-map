# The open calls, ruled — November 17, 2026 (row BA, session BA-6, and row MC)

> **The user's words:** "ba-5 is done please assure its good dont leave any open items" and, after,
> "commit and push when done leave no open calls or anything make decisions yourself soundlt with
> research". **What this record is:** every call an earlier session left "for the user" — the readings,
> the "one line to reverse" defaults, the "recommended, not built" lists, the design rows waiting on a
> word — gathered by nine read-only readers across the specs, STATUS and the next prompt, and RULED
> here, each with its reason. **Nothing below waits on the user.** A ruling is one of four kinds:
>
> - **KEEP** — the built default stands; the reason is its measure or its design.
> - **BUILT** — built in this session, behind its own seam (`tests/_ba6_seams.py`), with its test.
> - **HOMED** — built before the deploy in a named slice, with a done-when and a strict-xfail pin
>   (`tests/test_oc_the_rulings_to_build.py`, or the row's own pin for Session H's head).
> - **CLOSED** — not built, by design, with the reason; no surface of the game promises it.
>
> The method: each item's own record was read (its measure, its evidence, the earlier
> recommendation); the user's standing rulings were applied first (`diplomacy has no fog`, `events
> appear, authority bites`, `no cuts without consent`, `personality is character`, `history with teeth`);
> a measured default was kept unless a defect or an unbuilt ruling of the user's stood against it; a
> new mechanic was built only where it is small, in the feature this session owns, and clearly better.

## 1. Row BA — the battle

| Item | Ruling | Reason |
|---|---|---|
| The reserve (BA-5's form, parked) | **CLOSED** | Failed the rule written before its data (nine in ten of the men it took were ours). |
| The reserve, the attacker-only form (BA-5's recommendation) | **CLOSED** — built, measured, not armed | Measured by the same rule on the same ladder (`tools/_ba6_reserve_rule_2026_11_17.json`): pick **none** — 22 of 23 pursuits fell on a French corps (70,639 / 87,987 / 100,702 of ours against 2,000 / 3,000 / 5,000 of his). The cause is the purse: his AI keeps points by its rule, a France that spends to win holds none. Whoever keeps points harvests. Both forms failed; the hand stays as BA-3 made it. The seam stays down in the game (`BA6_CLOSED`). |
| Blücher's "Vorwärts!" in the 1805 game | **CLOSED** | "Marschall Vorwärts" is 1813's name (the Katzbach, the Wars of Liberation); in 1805–06 Blücher is a Prussian cavalry general of a court at peace with France. An 1805 ability for it would be an anachronism, and the gate never ticked it. |
| A riposte council on defence; marshals settling a hanging day alone | **CLOSED** (confirming §15.11) | The hand is the Emperor's in every battle (the user's agency ruling); defence is played in turns as his turn opens (BA-3 ruling 10); "Leave it to him" hands a day to the lead. |
| The four weighed at BA-3's gate (ordinary battles settled by tempers; courts' points against each other; stopping the enemy phase to ask; a standing instruction per corps) | **CLOSED** | Courts' battles between themselves are unseen — points spent there are invisible to the player; stopping the enemy phase breaks the turn the game is built on; "Leave it to him" already is the standing instruction for a day. |
| The plinth's name (BA-1) | **KEEP** — above the men | Ruled by BA-5 (ruling 12); on the slab it would be 9 px at the fourth rank, under the readability floor. |
| A typed `historical` seed keeps re-rollable dice | **KEEP** | `historical` is the fixed reference table — every seeded rule is off there; a player's rolled seed (the menu's default) seeds the dice. |
| "· 0" on a free chip; pips for the larger purse | **KEEP** | BA-5's exits say "free" (no "· 0" is printed on any word that costs nothing); the pips show the larger purse on both rows so they align — the wire never carries a purse's start. |
| BA-2's seven, BA-3's list, BA-4's choices, BA-4's five improvements, BA-4's bar | **KEEP** | Ruled by BA-5 (§15.22 rulings 2–12) — STATUS still listed them; struck there. |
| BA-5's departures and delegated decisions (Replay and Close in their corner; the head at the panel's top; the speed switch in Close's room; the verdict's lines; `DAY_TAG_ORDER`; `DAY_LIFT`; …) | **KEEP** | Each was driven by a blind reading or a measured overlap. |
| BA-5's "may", not "will", where unseen fitness forbids the strike | **KEEP** | "Will" would publish a promise the rule can break (fog §4.4). |
| The sign-ability sweep not re-recorded; BA-3's six boards not re-walked | **KEEP** | The keyed probe is identical on every key, so the sweep stands; BA-4's live boards walk the same panel in its current form. |
| The reserve rule's clauses iv / v (review #19) | **CLOSED** | Moot — the reserve is closed; clause iii decided both forms. |
| Lever 2 — a numeric chance on the cards ("8 in 10") | **CLOSED** — built as words instead | An honest probability needs the resolver's dice and variance priced apart from its draws (golden rule 1) and an exact sighting (fog); a number the engine cannot stand behind would be a lie. Built instead: every own word says what it RISKS in words (`battle_telling.risk_of`), the free words their stakes. |
| Levers 1, 3, 4, 5, 6 (a taller tray and three-line cards; the free words' stakes; fewer chips on a crowded day; luck against margin; a legend) | **BUILT** | §15.25. |
| The blind-reading bar (agency and clarity 7) | Measured again on the finished table | §15.25 records the fourth reading; whatever it reads is reported, and the levers past it are named there. |
| WS-13 — "outnumbered" read on the two leads | **BUILT** | `combat_executor.outnumbered_is_read_on_the_field` — the men each side put on the field, the very figures "numbers told" reads; and its sibling, the aggressive marshal's no-stomp win (EC-K). |
| WS-15 — a refused attack cancels a drill | **BUILT** | `combat_executor.a_refused_attack_spends_nothing` — on every road, a blow not struck puts back the drill, the counter-punch, and its sibling the square (and what breaking it cleared); a corps that marched keeps them spent. |
| BA4-BOMB — bombardment payloads byte-unstable | **BUILT** | `battle_script` writes the cannonade's names in a fixed order. |
| BA-5's ruling 1 — T3-6's law of peace not extended to a third court's ground ("built before the gate is read if the ambient line ever reads above 0") | **BUILT**, as it pre-decided | The session's final measure read the ambient annexation line at 1 (rivoli: Saxony kept Swabia — Bavaria's homeland, held by Austria — by the Austria–Saxony peace's retention). `game_end.a_peace_evacuates_a_third_courts_ground` (row PEACE, BA6-X8): ground the holder took from the ceder outside what it may keep goes back to the ceder. |

## 2. Row MC — the marshals

| Item | Ruling | Reason |
|---|---|---|
| GRD-17 — the audience's acknowledge says what follows | **BUILT** | `precedence.an_audience_names_its_cause` ("X's grievance stands: …"). |
| GRD-17 — four aggressive marshals share one objection line | **BUILT** | `strategic_executor.each_aggressive_man_objects_in_his_own_voice` — Ney, Murat, Lannes and Masséna each in his own words (the real man's character); the lines that carry a reading are unchanged. |
| GRD-31 — a cautious marshal who defies a PURSUE sulks | **BUILT** | `defiance.a_cautious_man_defies_a_pursuit_by_fortifying` — a pursuit is an advance; he fortifies, as he does an attack. |
| GRD-32 — literal / loyalist / dove objections carry no Trust arm | **CLOSED** — none by design | Their objections are concerns, not counter-plans: the literal man awaits orders by character, the loyalist's counsel is obedience, the dove's is to hold. A Trust arm would invent a counsel the man does not have. |
| GRD-38 — a full-authority Emperor (≥ 80) is never defied | **KEEP** | Obedience is what authority buys (the user's "authority bites": spent, it falls, and defiance returns). |
| The court count's find — the Auerstedt rule never fired for France (BA6-X9) | **BUILT** | `precedence.a_silence_is_remembered_when_pressed` (row SILENCE): a Hostile comrade's silence is remembered when the lead was hard pressed, won or not — Auerstedt itself was a victory won outnumbered. By a rule written before its data (`tools/_ba6_court_rule_2026_11_17.json`): 0 → 2 French silences in ten campaigns, at most a quarter of the rescues, the court alive on every seed, the band and the gate unmoved. |

## 3. The weak-spot rows (WS)

| Item | Ruling | Home |
|---|---|---|
| WS-10 — who owns the bare digits while a ledger is docked | **The war room keeps the digits**; a docked ledger's tabs move to Alt+1–8 and its lead line says so | One rule for every docked screen (UI-6 gave it to the Generals screen). **HOMED: Session H's head** (its strict-xfail pin `TestWS10TwoSurfacesClaimTheBareDigits`). |
| WS-12 — the live model's `strategic_score` moves morale, trust and attack | **Retired: the model's number moves nothing**; the literal marshal's buff and clarification read the fast parser's own deterministic ambiguity | Golden rule 6 is the user's law; every measure was taken in mock mode, where the bonus never fires, so live play was an unmeasured, easier game (+15 morale and +10 % attack per well-phrased line, repeatable on a refused order). Not a cut of content: no surface promised it. **HOMED: Session H's head** (pin `TestWS12AModelsNumberMovesAMarshal`), with GRD-33 (below). |
| WS-14, WS-R, UI6-X70 / X73 / X74 / X75 | Defects, not calls | Session H's head, as filed (their pins). |
| GRD-33 — the literal marshal's ambiguity buff never expires | **It expires at the turn's end** (Iron Resolve's no-banking) | **HOMED: Session H's head**, with WS-12 (the same code). |
| GRD-16 — "Did you mean Ney?" for a marshal-name typo | **Offer the nearest of the player's own marshals** (never a fogged name) | **HOMED: Session H's head**, with UI6-X70…X75 (the typed order road). |

## 4. The design rows and the older readings

| Item | Ruling | Reason / home |
|---|---|---|
| GRD-2 — a third-party declaration of war rides only on PARTIAL sight | **BUILT** | The user's ruling: diplomacy has no fog (`diplomacy.a_declaration_of_war_is_public`). |
| GRD-5 — "An envoy has arrived with a proposal", eight identical rows | **BUILT** | The user's ruling: name the letter (`ai_diplomacy.an_envoy_names_his_letter`). |
| GRD-30 — recruit-morale laws void at a training ground | **BUILT** | The user's ruling: say it on the line (`reforms.a_law_says_where_it_is_void`). |
| GRD-18 — a repeated morning headline | **KEEP** | Built (demoted when unchanged). |
| GRD-1 — an ally's hand-back of a French province | **KEEP** | Built (`liberation_line`, S14G-1). |
| GRD-15 + GRD-37 / GRD-14 / GRD-28 — the courts buy laws they never use; the Staff and its cure unreachable after S14j | **HOMED: row OC, slice OC-1 (the courts' purse)** | A defect: Prussia pays upkeep for a law whose cure can never fire. A law's upkeep must buy something used (a demand read), and an at-war court saves for its Staff without the five-turns-of-upkeep reserve; T8 re-read on the post-S14j economy. Pins in `tests/test_oc_the_rulings_to_build.py`. |
| GRD-21 — the courts' cheap rungs spend the chest to nothing | **HOMED: OC-1** | Every purchase rung keeps one turn of upkeep in hand. |
| GRD-29 — a 3-authority trade edict strands Britain's cure law | **HOMED: OC-1** | A cure law is not stranded by an edict. |
| GRD-20 — a deficit every third turn is never remembered | **HOMED: row OC, slice OC-2 (the Emperor's purse)** | An exploit: arrears decay so fast that a chest below zero one turn in three never deserts. A deficit one turn in three for twelve turns accrues its consequence. |
| GRD-19 — the restless interior is binary (1 and 32 provinces cost alike) | **HOMED: OC-2** | Priced by the province, capped — the marginal signal a binary term cannot give. |
| GRD-11 — the crown term is flat whatever the empire's size | **KEEP** | S14j measured 250 as the lowest value holding both targets; the empire's growth is braked by occupation, by the restlessness OC-2 now prices, and by the coalition's alarm. |
| BRIT-1 — a strangled Britain cannot write without contact for 15 turns | **HOMED: row OC, slice OC-3 (the Strangulation's letter)** | The Strangulation arc's whole design (NAVAL_SPEC §5.1) is Britain suing without invasion — and Amiens (1802) was signed by a Britain no French corps had touched. A closed-port Britain past exhaustion 80 may write. |
| GRD-34 — golden rule 1's residue (terrain-scaled recklessness, coordination constants) | **HOMED: row OC, slice OC-4** | The user's own rule; byte-identical, held by the keyed probe. |
| GRD-35 / GRD-36 — map_data on every response; coordination pricing rescans | **CLOSED** | The server is this machine (localhost); 19 ms of a 48 ms reply and 11 % of an AI turn sit inside the G4 tripwires. |
| GRD-25 — the enemy phase's fixed order | **KEEP** — recorded as deliberate | `EUROPE_ROSTER` order, great powers first, deterministic; a rotation would perturb every trace for no player-visible gain. |
| GRD-12 / GRD-22, GRD-23 / GRD-24, GRD-3…GRD-10, GRD-13, GRD-26, GRD-27 | **KEEP** | Each already ruled where its record says (EC-2; Tier 3's gate; AI-France mode not planned; DYNAMISM_SPEC §7d). |
| Session G5's four (Switzerland bought on six unattended seeds; friedland's kingdom falls; the gate's corrected count; the ally's branch) | **KEEP** | The bribe works on an idle France as it should — a played France keeps Switzerland on every band arm; the gate is met either way; the corrected count is the instrument's; an ally's policy is its own (a client is bound, an ally is sovereign). |
| Session G's four (the understudy's reach; the chest's number; 26 → 25; jena's Pope) | **KEEP** | Emergent and seeded (seeded paths, not laws); price-alone earned clause 2; 25 is inside 23–28; the deterrence working (D5). |
| Session F's three, E's four, D's three, C's five, B's three | **KEEP** | Each a measured default; the people's-stir letters keep RE's desk order (the user's own design); the 1805 board's single ambient great-power war stands — authoring a second for the idle board would fabricate history; the march's bleeding is the cap tax (its done-when amended to read so); the AI levée and AI-AI vassalage stay France's instruments of the age. |
| The flip's two readings (the courts' Decree in authority; AU-5's alternative removed) | **KEEP** | Built by the user's "Flip, flat grip". |
| The Crown's four readings; the road record's three | **KEEP** | Each the user's "loyalty pays" / "the teeth are the point" applied. |
| S14d's A1; S14i's three; SF-NAV-1-D1; the crown term 250; AO-Q1 (two provinces) | **KEEP** | Each measured under its delegation. |
| AO-Q2 — a "name the two who matter" card for a short pool | **CLOSED** | The fan-out already sends in roster order and names who did not go; a second card is a second click for the same answer. |
| AO-Q3 — the courts' AI using the army order | **CLOSED** | The courts issue no standing orders by design (CC D8); a rung would be a new AI behaviour for Austria's five corps alone. |
| UI-5's eighteen decisions | **KEEP** | Each a Settings switch. |
| The UI levers past 7 (UI-5, UI-6) | **CLOSED** | Three passes held 7 / 7 / 7 after their levers (UI-3, UI-4, UI-6); several mean cutting copy, which is the user's word to give, not mine. |
| UI-5's look and listen; UI-6's look | Not a call | The user's own experience of the client, whenever the user plays it; nothing waits on it (the blind readers measured both). |
| The code-signing certificate | Not a call | A purchase and an identity check only the user can make; the first build ships unsigned with the testers' SmartScreen note (`deploy\build.bat`), and nothing in the code waits for it. |
| The hook's remaining lever | **CLOSED** | The gate stays and 9:51 is the wait; trimming the ten heaviest modules is no game work. |
| The two hash-seed orderings | **BUILT** | Checked: no game code reads either in an order-sensitive way (`co_location_turns` is read by key; two distinct court forms of one length cannot match one whole word); the court forms now tie alphabetically, so the list no longer differs between processes. |

## 5. Row OC — "the rulings built" (before Session H)

Each slice is one seam row and one measure; each item's pin is a strict xfail in
`tests/test_oc_the_rulings_to_build.py` that turns red the day it lands. STATUS ▶ NEXT UP names the row.

| Slice | Items | Done when |
|---|---|---|
| **OC-1 the courts' purse** | GRD-15 (a law buys what is used), GRD-37 / 14 / 28 (the Staff saved for without the upkeep reserve), GRD-21 (a cheap rung keeps a turn of upkeep), GRD-29 (a cure law is never stranded by an edict) | Prussia buys no law it never uses; at least one doctrine-cure court reaches its Staff inside forty turns on some seed; no court's chest ends a passive run under one turn of upkeep; BASELINE_SERIES re-pinned with its attribution |
| **OC-2 the Emperor's purse** | GRD-20 (a deficit one turn in three accrues), GRD-19 (restlessness priced by the province, capped) | the D-S-S pattern deserts inside twelve turns; 1 and 32 restless provinces cost differently; S14j's chest bands re-read on the commanded arms |
| **OC-3 the Strangulation's letter** | BRIT-1 | a closed-port Britain past exhaustion 80 writes for an armistice with no contact, on the benchmark's NAV1 arm |
| **OC-4 golden rule 1** | GRD-34 | terrain-scaled recklessness read in `marshal.get_attack_modifier`; the keyed probe identical on every key |
