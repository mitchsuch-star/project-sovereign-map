<!-- Frames are under frames/NNNN.jpg where the run exported them (the full set lives in the run folder); the action numbers below are the instrument's action numbers = frame numbers. -->

# S14h — the closing re-play on the DD-B instrument (October 26, 2026)

Run folder: `scratchpad/replay_run` (fourteen scene saves from `tools/_s14h_replay_scenes.py`; the engine at 5120x1440, backend 8006, mock parser, never 8005). `start --road sea` (the road is a label only). No source file touched; no git state changed.

Boot: `click Looks right` (#1), `click Load a Campaign…` (#2), then each scene loaded from the list (the list is ordered by save time and scrolls; `scroll 1828 500 down|up` found each save). Scenes were driven in the order opening, liberation, aggressive, support, petition, envoys, truce_offer, counter, truce_mission, design_peace, guarded, table, sea_camp, sea_landing; truce_offer and table were loaded a second time (#360+) for a retry and for a badge check. The engine never died; no restart.

## Scene opening (turn 1) — S14G-8, 13, 14, 15, 16, 20, 22

### S14G-8 — the "Satisfy their design" counsel
The counsel sits behind the Talleyrand button (top bar) > "Assess the Situation" (#20, #21), not on the Cabinet's first page. #21 lists the option "Satisfy their design (Britain)"; #22 clicks it. Frame 0022/0024: "PEACE PREVIEW - Britain / Proposed Terms / France concedes: • France cedes Flanders to Britain / Mutual: • Peace Treaty …", "Assessment: GENEROUS", "Acceptance Estimate / Score: 21 - REJECT", and the closing line "I have set its cession beside the peace: the design is on the table, and the court's own reading of the package, with its price, is below. Nothing leaves until you send it." Nothing sent (#26 Not Now). The DP price line was not located in the scrolled crops (#24, #25). **SEEN** (cession, acceptance estimate, nothing sent; the 3-DP figure itself not read).

### S14G-13 — who am I fighting
#28 `type who am I fighting` (question): "Each war is on the ACTIVE WARS banner in the lower right (click the war)". **SEEN**.

### S14G-14 — the muster's unscouted provinces
#29 `what if Massena attacks Archduke John`: "The band weighs a force of his you have not scouted — scout Carniola." and "On the men in view alone the odds read 'favorable' (42,000 against a substantial force)." **SEEN**.

### S14G-15 — the tall reply and the province panel
#31 `click_at 2078 600` (Hungary) while the tall reply was up: frame 0031 — the command window had dropped to a short strip ("Esc: menu · click to type") and the Region Panel kept its full body, the "MARCH HERE" list in view. **SEEN**.

### S14G-16 — Esc releases the line
#33 `key G` (Generals open), #34 `key Escape` (closed), #36 `key q`: the command line stayed empty ('') and unfocused, placeholder "Esc: menu · click to type" (frame 0031 and the #36 crop); #38 the Generals header reads "Esc closes it (Alt+G while you type)". **SEEN**.

### S14G-22 — the Cabinet's size
#4 (boot): the window shows a resize grip at its lower right and the list is scrollable ("▼ more below"). The "Your courts" row is omitted by design when no court has business (it appeared on replay_truce_mission, #183: "Your courts (1)" with "Austria — Armistice | -57 [MISSION]"). The width could only be judged by eye (the window is still a narrow column, about 305 of 2000 view px). **SEEN** for the row and the grip; the width is the reader's call.

### S14G-20 — the peril clause at the gate
#41 `Ney, attack Mack` (the army joins), #46 End Turn: the dice took the battle to a capture ("MARSHAL CAPTURED — Mack is taken by France at Swabia!"), and End Turn went through with no gate at all, so there was no peril clause to read. **NOT SEEN** (the scene's limit: the dice decide; the row's clause needs Mack to hold the field).

## Scene liberation (turn 3) — S14G-1, S14G-4 (dispatch half)

### S14G-1
#58 `Ney, attack Mack` at Munich: reply "Ney advances into Munich. … Munich, Bavaria's capital, retaken — handed back to Bavaria." and "[Alarm] Europe's alarm rises +3 — Won a battle +3." — no "+15", no "+2", no plunder question; client line "⚑ Munich — handed back to Bavaria ⚑". Threat 84 (muster line "now 84/100") became 87 (#59 top bar). #61 `key L`: "Munich, Bavaria's capital, retaken by France — handed back to Bavaria." The war card tooltip reads "France retook Munich for Bavaria". The map repaint was not read; the AI's own road is not stageable (read TestS14G1, TestS14GX10, TestS14GX12). **SEEN**.

### S14G-4 — the dispatch half
#63 End Turn, #64: "Berthier: 'Cannon fire at Munich, Sire. Investigate?'" and the dispatch line "Napoleon — Lorraine — 10,000 — HALTED at Lorraine — awaiting your word." #65 Continue as Ordered ("Napoleon reluctantly continues his march"); #72 the dispatch re-read: "> Napoleon — Orleanais — 10,000 — Moving to Flanders — arrives next turn." — no longer "awaiting your word". The stored "answered: continued" wording was not itself on screen (the live re-read shows his road, as the manifest says). **SEEN** (the free-refusal half: see scene guarded).

## Scene aggressive (turn 6) — S14G-2, S14G-19

### S14G-2
#78 `Massena, support Napoleon`: "He will drop this order for any battle within two provinces in a war of ours." #79 End Turn, the gate: "⚠ Lannes (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle within two provinces in a war of ours. Massena (aggressive) holds a standing order … Massena's corps stands below 40% morale beside Kutuzov (~27,500, Hungary) — end the turn anyway?" The same sentence also rides the march chips of the region panel (frame 0031: "He will drop this order for any battle within two provinces in a war of ours.") and the move reply (#145, Murat). The interrupt itself is NOT STAGEABLE. **SEEN**.

### S14G-19
#80 `click_at 2024 456` on the "Ney +5" stack label over Bohemia: the order strip opened "Ney selected — click a province: march · an enemy: attack · a marshal: support", no Bohemia province panel. **SEEN**.

## Scene support (turn 9) — S14G-3
#86 `Soult, support Napoleon`: "He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Soult, follow Napoleon' keeps him at Napoleon's side." #87 End Turn; #88: "Davout: Napoleon is secure", "Lannes: Napoleon is secure", "Ney: Ney moves to support Napoleon. Napoleon is secure"; positions: Davout Paris, Lannes Paris, Ney Limousin, Napoleon "Moving to Lyonnais — arrives next turn"; only Soult (ordered this turn) is "Supporting Napoleon". A second tick was not driven (the next End Turn met a battle diorama and a gate). **SEEN**.

## Scene petition (turn 4) — S14G-5
#103 the notice rail icon did nothing; #104 `click Generals (G)`, #105 `click Hear him`: Murat's card, option "Give him a command [2 AP]" with the tooltip "Mack has left Swabia — send him against Archduke Charles into Munich instead (substantial force against his 18,920)?". #106 first click: nothing spent (4/4), "Mack has left Swabia; Archduke Charles at Munich (substantial force against his 18,920) is what stands in his reach now. Berthier reads the odds favorable. Send him?" #107 second click commits: "'Archduke Charles, then.' Murat takes the command and goes. Murat pursues Archduke Charles (at Munich)." **SEEN**. (The Generals book stayed open under the fight.)

## Scene envoys (turn 5) — S14G-6
#116 the scene opens on the mailbox: Austria's row reads "Shuts the Cabinet"; #119 the letter: "Not Now (Cabinet stays shut)" with "Set aside — the Cabinet stays shut until it is answered or the turn ends." under the buttons. #120 Not Now; #121: the Cabinet button's face "⚖ The Cabinet — shut" (tooltip "Austria's letter stands unanswered — the Cabinet stays shut …"), the Envoys badge tooltip says the same. #122 F1: "An unanswered envoy awaits your reply (Austria's letter) — the Cabinet stays shut until it is answered or the turn ends. Reopen Envoys to answer it." #124-126 reopened the Envoys and Rejected Austria; #127 F1 opened THE CABINET with the Ottoman and Portuguese courtesies still pending. **SEEN**.

## Scene truce_offer (turn 3) — S14G-7
#134-138: F1 > Austria > Propose Armistice. Frame 0139: the Political Consequences open "Bavaria stays at war with Austria under this truce — an ally, not a client: her war runs on, and 3 French corps stand on Bavarian soil under the truce. Your corps will not fight for her under the truce; Austria may take her provinces where your corps stand, and ground that changes hands puts them on the road home — Berthier marches them out (up to 5 turns of safe passage) and none may enter it again." — the Bavaria row leads the consequences. Sent (#140), End Turn (#141): "Talleyrand returns from Austria empty-handed. The proposal was rejected. … deep-seated hostility." Repeated from a fresh load (#368-374): rejected again, though the card read "Score: 51 - ACCEPT". With no truce running, #145 `Murat, march to Swabia` printed no front-line sentence (it would only after an accept) and no stranded-corps dispatch line exists. **PARTLY** (the confirm half SEEN; the march's front clause and the dispatch half NOT SEEN; new find NF-1).

## Scene counter (turn 5) — S14G-21, S14G-23
#158 Envoys; frame 0159: "COUNTER-OFFER … Revised Terms: - Proposal: Vassalage - Added by Bavaria: you pay 300 gold more (442 at the signing)". **S14G-23 SEEN**. #162 Accept Terms ("Treaty signed: Alliance → Vassal with Bavaria"); #164-168 F1 > Prussia > "Skip ahead: Non-Aggression" > Send; #169-172 End Turn x2 and Continue: "Treaty signed: Peace → Non-Aggression with Prussia." The new lines carry no "war with Bavaria and Prussia is over", no "hold under your own orders … not moved"; the corps' road home ("Deroy is on the wrong side of the frontier at Franconia … he has 3 turns of safe passage", for the truce with Austria) appears once. **S14G-21 SEEN** (absence read in the turn's printed lines).

## Scene truce_mission (turn 6) — S14G-24, 25, 28
### S14G-24
#183-184: Austria's assessment (Armistice, -57): "At expiry: the war resumes where it stood — Austria is bound by Britain's bond not to sign alone; a peace with her runs through the table, where the bond is priced." No "short of the line", no "ripens into peace". The courtship projection with "+8 a turn" was not in this text (the Cancel row reads "Cancel: Improve Relations — Hostile (+20 over 3 turns)"). **PARTLY**.
### S14G-25
#187 the preview: "Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn)." #188 the send reply says the same; the top bar button "Talleyrand: Improving... (paused)" and the summary "Talleyrand at Austria — Improving Relations (paused — carrying a letter)". **SEEN**.
### S14G-28
Taken from a fresh load (#198-201), because the send at #188 changes the reason. Spain: "Reassure Ally is shut while Talleyrand is at Austria's court — recall Talleyrand from Austria first (the Cabinet's Recall is free). Recalling forfeits Austria's remaining courtship (+8 a turn, until the peace is signed); left alone it slides 1 a turn and the alliance lapses in about 30 turns." The button tooltip repeats it. The Improve Relations confirm's warning was not opened. **SEEN** (the shut-row half).

## Scene design_peace (turn 7) — S14G-9, 10, 27
### S14G-9
#232 Austria: "Buy Off Their Design (1128g) … +5 relations (−50 → −45); she still counts toward a league until relations reach −10." #228 the Balance page: Britain and Russia read "Design bought off, 15 turns left; her league place is her relations."; the footer: "a buy-off … puts the design to sleep 15 turns — +5 relations; she still counts toward a league until relations reach −10." **SEEN** (the same clause also on Britain's page at turn 1, #19).
### S14G-10
Typed (#235) `license Prussia against Hanover` is refused at the line ("Matters of state are conducted at the table … F1 → Prussia → Sponsor Their Design — Licence"); through the Cabinet (#237-240): "License Prussia's design against Hanover: no gold, 1 diplomatic point … If Prussia then declares on Hanover, her relations with every court, France's included, fall 15 (France–Prussia now +10, +15 once this compact is struck, 0 after her declaration); the Improve Relations mission running with Prussia is set back the same 15. License it?" Answered Not now (#241). **SEEN**.
### S14G-27
#242 End Turn: no popup (popups=[]); "Britain, Spain and Bavaria stirred, but their formations remain beyond our sight." **SEEN**.

## Scene guarded (turn 12) — S14G-11, 33, 4 (free-refusal half)
#256 `Soult, march to Flanders`: "Berlin and Brunswick are Prussia's guarded ground (Armed Neutrality) — standing in them costs −25 with Prussia — march, go round or cancel?" with [March (1 AP)] [Go round (1 AP, 5 provinces)] [Cancel Order]; actions still 4/4. **S14G-11 SEEN**. #257 Cancel Order; #258 `Napoleon, march to Flanders`: "Napoleon already stands at Flanders — nothing spent." (4/4). **S14G-4 SEEN**. #259 `Napoleon, march to Paris`: "Route: Picardy → Artois → Paris. Arrives in 3 turns." (our own soil). **S14G-33 SEEN**.

## Scene table (turn 16) — S14G-12, 26, I1
### S14G-12
#274 war banner > "War for Munster", #275 Open Settlement: header "This draft will not carry as it stands", the hint's Britain half "Gold is at its ceiling for Britain (26 of 50); what weighs on her is the erection of Ireland (-23) — remove it, offer land (a province weighs about 875g), or drop Britain." #276 More generous: the header now carries "Gold past 1,000 buys nothing more from Britain at this table, Sire." #277-278 the gold [+] stopped: "…— set to 1,000." But the same hint still opens "Austria and Russia won't accept these terms yet. Use 'More generous' (or ease a court) until each accepts" for two courts whose blocker is the war objective (new find NF-2); the "more below" cue was not read. **PARTLY**.
### S14G-26
#279 Back Out: "Settlement draft kept until the turn ends — reopen Settlement this turn to continue." #280-281 End Turn: "Your unratified settlement draft with Britain (5 clauses) was set aside at turn's end (a draft lasts one turn)." #391 (fresh load, war card reopened after Back Out): "▸ Draft kept until turn's end — Open Settlement resumes your terms." **SEEN**.
### S14G-I1 — the instrument row
#277 `click +` lists the gold controls as "icon: + Britain · Conceded · France pays 1000 gold (yours) up to 1,000 …" with their tooltip, `click#2 +` pressed it (#278). **SEEN**.

## Scene sea_camp (turn 8) — S14G-17 (failed half), 29, 30, 32
#318-319 Ledger (T), book 7. S14G-17: "Dumonceau, march to Normandy (2 AP · 4 turns) · … Dumonceau at Amsterdam — inland; nearest shore 2 provinces (Hanover)". S14G-29: every chip names its price in the book ("Blockade the enemy (1 AP)", "Lay down ships (1 Admin AP)", "(2 AP · 4 turns)"); #320 the chip: "[2/4 actions remaining]", route Flanders → Picardy → Artois → Normandy, the camp lines. S14G-32: #322 `Soult, march to Orleanais`: "Orleanais lies outside the camp — this takes 30,000 men out of it; the 2-turn count resets at the turn's end — Britain's squadrons, held home by the camp, go back to the blockade (trade −50%, crews rot 5 a turn, about −175g a turn) from the turn after next." Turn 9's income (#325) has no Blockade term; turn 10's (#330) reads "Blockade: -219g". The rail/notice naming the broken camp as the cause was not found in the printed lines. S14G-30: #325/#330: "Morale failing (0) … Recovering from the rout, 2 turns — drill once he has reformed." (and Massena "Recovers T11"). **17 SEEN, 29 SEEN, 30 SEEN, 32 PARTLY** (the order's reply and the late landing SEEN, the return's cause line NOT SEEN).

## Scene sea_landing (turn 10) — S14G-17 (ready half), 18, 31
#353-354: "Ready to embark: Davout (14,000 at Moravia — an allied shore), Ney (13,000 at Moravia — an allied shore), Lannes (12,500 at Moravia — an allied shore), Dumonceau (6,500 at Normandy — a dockyard of ours)"; Napoleon not listed; the landing chips name Dumonceau only. **S14G-17 SEEN**. #356 `recruit infantry in Normandy`: "Dumonceau commands our foot here, but Holland pays its men — recruit into one of our own corps. … Nothing was spent." — never "marched within reach" for the man at the province. #357 `Dumonceau, recruit infantry`: "Dumonceau's men belong to Holland, Sire — it raises and pays them. Recruit into one of our own corps." **S14G-18 SEEN**. #358 `Dumonceau, land at Ulster`: the confirm prices the throw (75 in 100), the failure (30% intercepted, 5% turned back, the fleet's −10, the fleet action) and the prize ("Ulster is half of the Ireland carve (with Munster) — hold both while the war with Britain runs and Britain can be made to erect it at a table; what waits ashore is unscouted"); the "under 5,000 men holds no ground" clause is not in the text. Answered Stand down (#359). **S14G-31 SEEN**.

## New finds
- **NF-1 (P3, row 1 in rows.json, #373)** — the armistice's confirm card on replay_truce_offer reads "Score: 51 - ACCEPT" and Austria rejects it both times ("deep-seated hostility"); the S14G-7 truce clauses on the march and the dispatch could not be staged.
- **NF-2 (P3, row 2 in rows.json, #276)** — the table's standing hint kept its generic "Use 'More generous' (or ease a court) until each accepts" for Austria and Russia, whose blocker is the war objective (gold cannot move it): the sibling of S14G-12's Britain sentence.
- Observation, not filed: after a loaded save or a battle diorama closes, the command line is focused, so a bare hotkey (`g`, `r`) is typed into it (#70, #101) — the row 16 fix covers screens closed with Esc, not these two entries.
- No SCRIPT ERROR, no engine error; the judge classed 15 typed lines (10 as meant, 2 answered, 1 honest refusal, 2 unjudged) and no `misread` or `executed_when_refusal_meant`; the one unsent line (#143) was typed under a battle diorama and resent at #145.

## VERDICT TABLE

| Row | Verdict | Scene | Frame(s) |
|---|---|---|---|
| S14G-1 | SEEN | liberation | 58, 59, 61 |
| S14G-2 | SEEN | aggressive | 78, 79, 145 |
| S14G-3 | SEEN | support | 86, 88 |
| S14G-4 | SEEN | liberation + guarded | 64, 65, 72; 258 |
| S14G-5 | SEEN | petition | 105, 106, 107 |
| S14G-6 | SEEN | envoys | 119, 121, 122, 127 |
| S14G-7 | PARTLY | truce_offer | 139 (confirm); 373 (rejected) |
| S14G-8 | SEEN | opening | 22, 24 |
| S14G-9 | SEEN | design_peace | 228, 232 |
| S14G-10 | SEEN | design_peace | 240 |
| S14G-11 | SEEN | guarded | 256 |
| S14G-12 | PARTLY | table | 275, 276, 278 |
| S14G-13 | SEEN | opening | 28 |
| S14G-14 | SEEN | opening | 29 |
| S14G-15 | SEEN | opening | 31 |
| S14G-16 | SEEN | opening | 33-38 |
| S14G-17 | SEEN | sea_camp + sea_landing | 319; 354 |
| S14G-18 | SEEN | sea_landing | 356, 357 |
| S14G-19 | SEEN | aggressive | 80 |
| S14G-20 | NOT SEEN | opening | 46 |
| S14G-21 | SEEN | counter | 171, 172 |
| S14G-22 | SEEN | opening + truce_mission | 4; 183 |
| S14G-23 | SEEN | counter | 159 |
| S14G-24 | PARTLY | truce_mission | 184 |
| S14G-25 | SEEN | truce_mission | 187, 188 |
| S14G-26 | SEEN | table | 279, 281, 391 |
| S14G-27 | SEEN | design_peace | 242 |
| S14G-28 | SEEN | truce_mission | 201 |
| S14G-29 | SEEN | sea_camp | 319, 320 |
| S14G-30 | SEEN | sea_camp | 330 |
| S14G-31 | SEEN | sea_landing | 358 |
| S14G-32 | PARTLY | sea_camp | 322, 325, 330 |
| S14G-33 | SEEN | guarded | 259 |
| S14G-I1 | SEEN | table | 277, 278 |

Totals (34 rows): **29 SEEN, 4 PARTLY, 1 NOT SEEN**.

Run figures (`run.json`): 393 actions, 2199.6 seconds wall, engine exit 0, n_script_errors 0, n_engine_errors 0, turn reached 16 (Early May 1806); judge: 15 typed lines, no P1 proxy.
