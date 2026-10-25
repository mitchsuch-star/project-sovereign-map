<!-- The frames cited below are under frames/NNNN.jpg (1600 px wide); the crops named crops/<file> in the text are frames/crop_<file>. -->

# S14f part 2 — the closing re-play on the DD-B instrument (October 25, 2026)

Run folder: `scratchpad/replay_run` (the eleven scene saves; the engine at 5120x1440, backend 8006, mock parser, never 8005).
`start --road replay` is refused by the driver's argparse (`choices=conquest|diplomacy|sea`; `ROADS` has no `replay`), so the run was started with `--road sea` — `meta.json` carries road `sea`; the road is a label only, the scenes are the loaded saves. No source file touched.

Boot: `click Looks right` (#1), `click Begin the 1805 Campaign` (#2), `click Confirm — begin anew` (#3, "Begin anew? The autosave of your running campaign is replaced." — the sandbox autosave).

## BOOT scene (Turn 1 — Late September 1805)

### S14E-24 — diplomacy #2 (scene boot)
Actions #3 (the opening dispatch + Commands block, printed in the command window), #4.
Frame 0003 shows (command window, dispatch TODAY block): "Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing." and (the Commands list) `• "what if Ney attacks Mack" — free: it names who marches with him before you commit`.
The map attack-card half (`click Swabia`) is recorded below under the map click.

### S14E-2 — conquest #1 / sea #1 (scene boot)
Action #4 `type what if Ney attacks Mack` (meant: question). Frame 0004. Under "Materiel: every 1,000 men we lose costs 50g …" the next line reads "Swabia is Bavaria's soil — the corps standing there are fed by contract, about −1,200g more a turn." Verdict **SEEN**.

### S14E-12 — sea #4 (scene boot)
Same reply (#4, frame 0004): "MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force) at Swabia". Verdict **SEEN**.

### S14E-17 — conquest #3 (scene boot)
Action #5 `type what if Massena attacks Archduke John` (question). Frame 0005. Reply: "MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable." then "The band weighs a force of his you have not scouted within reach of Tyrol — scout the provinces round it." Verdict **SEEN**.

### S14E-16 — conquest #2 (scene boot)
Action #6 `type how do I get to Vienna` (question). Frame 0006. Reply: "Yes, Sire — Bernadotte can reach Vienna from Franconia in 2 turns: Franconia -> Bohemia -> Vienna. The order is 'Bernadotte, march to Vienna'." (a marshal, the road, the order; not the manual). Verdict **SEEN**.

### S14E-32 — sea #9 (scene boot)
Action #7 `type Murat, march to Swabia` (move Murat): the first step meets Mack, so the free ask came (frame 0007, "MURAT REPORTS — 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' Berthier adds: …" with [Commit the Attack] [Go Around] [Hold Position] [Cancel Order]; nothing fought — S14E-1's ask). #8 `click Go Around` left him "awaiting orders" (no standing march), so to have a march to cancel #9 `type Murat, march to Flanders` ("Murat begins march to Flanders. Route: Orleanais → Flanders.") then #10 `type Murat, cancel` (meant: other: cancel his march). Frame 0010: reply "Murat halts his march and awaits new orders." Verdict **SEEN** (the bare tail parses; the march is recalled).

### S14E-33 — sea #9 (scene boot)
Action #11 `type lay down two ships` (naval_build). Frame 0011: "Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). …" Verdict **SEEN**.

### S14E-8 — diplomacy #6 (scene boot)
#12 `key F1`, #14/#15 scrolled the Cabinet, #16 `click Britain`: row "Propose Armistice — 6 of 50 ✗ (1 DP)". #17 `click Propose Armistice` (frame 0017): "Acceptance Estimate / Score: 6 - REJECT" — equal. Repeated on Austria (#21 row "Propose Armistice — 12 of 50 ✗ (1 DP)"; #22 frame 0022 preview "Score: 12 - REJECT"). Verdict **SEEN** (two courts).
D7 (boot reading): the Cabinet's row text is "Open Settlement with Britain alone — -8 of 50 ✗" (Austria's "Open Settlement with Austria alone — -8 of 50 ✗"); Talleyrand's counsel at boot quotes no gold sum, so the "Offer N gold to Britain" row was not exercised here.

### S14E-25 — diplomacy #3 (scene boot, Austria armistice preview, #22 frame 0022)
No "(N more concern…)" line; the preview prints Political Consequences in full (four bullets, scrollable); "the war score reads 0 for France" equals "War score: 0 ->"; the title line "The War with the Third Coalition: nothing taken yet on either side." — a quiet war (turn 1, 0 battles), which is the one case the row allows; the "1 battle fought; no ground taken yet" wording needs a war with a battle — see the later scenes. Verdict on the boot sighting: **SEEN for the concern line, the score equality and the quiet-war title; the battle-fought title is checked below**.

### S14E-19 — conquest #5 (scene boot)
#23 `click Not Now`, #24 `key F1`, #25 scroll, #26 `click Austria`, #27 `click Propose Peace` (preview "PEACE PREVIEW - Austria", Score: 0 - REJECT), #28 `click Adjust terms`. Frame 0028 shows the settlement TABLE over Austria alone: "This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia" with `+ Add demand`, `Demand more of Austria`, `Ease Austria`, `Bring Britain to the table`, `Submit for Review`, `Back Out`. NOT "Shall we discuss concessions, Sire?". Verdict **SEEN**.
Observation (not a row): at the table `key Escape` (#29) did nothing — the table has no X and no Esc; `Back Out` (#30) leaves it. 

### S14E-3 — conquest #6 (scene boot, the sweeteners road)
France is not behind at boot, so Austria's Adjust terms opens the table (above); the wizard steps were read on a court at peace. #34 F1 → Denmark, #35 `click Propose Open Borders`, #36 `click Adjust terms` → step 1 (frame 0036): `"I suggest offering 25 gold per turn."` buttons Offer 25 gold / Offer more / Offer less / Skip gold / **Never mind** ("Set the offer aside. Nothing is sent and nothing is spent.") and the X "Close (Esc)". #37 `click Skip gold` → step 2 (frame 0037): "Offering an Action Point is extraordinary …" buttons Offer the AP / Too costly / **Back** ("Return to the last step. The answer given there is undone.") / **Never mind**. #38 `key Escape` left the wizard (no popup open after). Verdict **SEEN** on the sweeteners road; the concessions road (France behind) was not reachable from the boot — see the scene notes.

### S14E-26 — diplomacy #4 (scene boot, turn 1)
#43 Sweden's page: `[Buy Off Their Design (1368g)] … (disabled: "Their price is 1368g — the treasury holds 400g.")`; #46 Prussia's: `Buy Off Their Design (1128g)` disabled, "the treasury holds 400g" (I had spent 400g on the keel at #11). Not reachable at turn 1; retried at turn 2 with gold (below).

### S14E-14 — sea #10 (scene boot)
#48 `key T`, #49 `key 7` (frame 0049, the Admiralty book). Orders block: "The Grand Diversion  44 in 100 at readiness 69 — and again 4 turns after, whatever the outcome; … if she is caught she meets Britain's 110 effective against our 49 — a decisive defeat is the likely result: about half of every pooled fleet (France 46→~21, Spain 30→~14, Holland 12→~5) is lost; Britain's side loses ~4%." and the same sentence again in the "The Grand Diversion (the button below)" block. Verdict **SEEN**.

### S14E-21 — conquest #9 (placeholder half, scene boot)
#48 (frame 0048, the Ledger open, the line unfocused and empty): the command line's placeholder reads "Esc: menu · click to type" (crop `crops/0048_0_930_800x90.jpg`; also the BottomLeftUI line list). Esc-closes-in-one-press half: #55/#56 — the enemy-phase battle replay (the Great Battle of Milan, "click anywhere to skip ▸") was closed by ONE `key Escape` (frame 0056: popups no longer list battle_diorama). The player-attack replay half (#57 `type Ney, attack Mack`) — see below.

### S14E-23 — diplomacy #1 (scene boot, turn 2 — Prussia's own letter at boot)
#57 (frame 0057): modal "DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia" — "Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court"; "Terms: - Proposal: Open Borders Agreement - Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade". Verdict **SEEN** (also re-checked on the letters scene).

### S14E-20 — conquest #7 (scene boot, #57)
The modal's buttons are `Accept`, `Reject`, `Not Now` — no "Let Talleyrand haggle" on this courtesy letter (hidden: Rule 9). Re-checked on the letters scene.

### Notes at turn 2 (boot)
- War panel: "War for Swabia" / tooltip "The War for Swabia: Austria holds Swabia of ours." after "Swabia passes from Bavaria to Austria": one of Bavaria's four homes is a quarter, so the S14E-31 floor is met — consistent, no row.
- The Cabinet button's tooltip while letters stand: "The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered or the turn ends." (#54-#57).
- Not Now's tooltip on the letter: "Set this letter aside — the Cabinet stays shut until it is answered or the turn ends. The envoy badge reopens it."

### S14E-18 — conquest #4 (scene boot, turn 2; the letters scene re-checks it)
#58 `click Not Now` on Prussia's Open Borders letter → the command window echoes "Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit." #59 `key F1` → the locked Cabinet (frame 0059): "An unanswered envoy awaits your reply — the Cabinet stays shut until it is answered or the turn ends. Reopen Envoys to answer it." with [Open Envoys (3)]. The Cabinet button's tooltip and Not Now's tooltip carry the same clause. Verdict **SEEN**.

### S14E-27 — diplomacy #5 (scene boot, turn 2: Prussia, Ottoman Empire, Portugal letters)
#60 (frame 0060, crop `crops/0060_1900_270_420x60.jpg`): the Envoys panel subtitle "Every envoy still awaiting your answer — … Routine letters from the lesser courts answer in place; every other letter opens in full."; every row has a gold flat "Open ▸" button (tooltip "Open this letter"); every row a "Terms:" line (Prussia: "Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade"); the great court's row carries the reason line "A great court's letter is answered in full — open to accept, haggle or refuse."; the lesser courts' rows carry Accept / Decline and "or click the letter to reply in full". Verdict **SEEN**. (Turn 3 and 4 letters, same panel: Denmark "Terms: Proposal: Non-Aggression Pact"; Hesse likewise.)

### S14E-28 — sea #2 (scene boot, turns 2-3: Portugal's and Saxony's letters)
Turn 2: Portugal's row "Terms: … · Portugal pays you 60 gold at the signing" (#60); #62 `click#2 Accept` → "You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury." Turn 3: Saxony's row (#84) "… · Saxony pays you 82 gold at the signing"; #85 `click#2 Accept` → "You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury." Turn 4: the Papal States "… · The Papal States pays you 105 gold at the signing" → "The Papal States paid 105 gold into the treasury." Never "Offer: Gold payment - 82". Verdict **SEEN** (3 instances).

### S14E-29 — sea #3 (scene boot)
Frame 0062 (#62, Portugal accepted from the letter-book): Gold readout 734 → 794 (+60, in the same frame as the accept). Frame 0085 (#85, Saxony): Gold 885 → 967 (+82). Verdict **SEEN** (2 instances).

### S14E-21 — conquest #9 (complete, scene boot)
One `key Escape` closed the battle replay five times (#56 the enemy-phase Great Battle of Milan, #66 and #77 the replays of Ney's attacks on Mack/Swabia, #80, #93). After the replay's Esc the line is unfocused: frame 0081's command line (crop `crops/0081_0_930_800x90.jpg`, no overlay) reads "Esc: menu · click to type"; the next Esc opened the pause menu (#82, popups list `pause_menu`), the next closed it (#83). Verdict **SEEN**.

### S14E-24 — diplomacy #2, the map half (scene boot, turn 2)
The opening Commands block and the TODAY line were seen at #3 (above). The map half: a click on a label opens the REGION PANEL, not the marshal-first card (clicking marshal label text lands on the region; I could not select a marshal token by `click_at`); #73 `click_at 1850 520` opened Swabia's panel: under each marshal "Attack Mack: Davout, Lannes and Napoleon would answer the guns — weighed together, the balance of force looks favorable." (the panel's Berthier line, one line, who joins). #75 `click#1 Attack Mack` ran the attack at once (it is a typed-command chip; it took Swabia — "REGION CAPTURED! Ney has taken Swabia"). The marshal-click-then-province "card" route was not exercised. Verdict **SEEN for the panel's one-line muster; the map card route NOT REACHED (instrument could not select a token)**.

### S14E-26 — diplomacy #4 (scene boot, turn 4)
Buy Off needed gold (Prussia 1,200g at turn 4; Sweden 1,368g). Turn 4, treasury 1,563: #110 F1 → Prussia ("Buy Off Their Design (1200g) (1 DP + 1200g)" enabled), #111 `click Buy Off Their Design` → the clarification popup (frame 0111): "Buy off Prussia's design — The Hanoverian Prize: 1,200 gold and 1 diplomatic point. The treasury holds 1,563 gold and would hold 363 after. The want sleeps 15 turns; it does not die — marching on Prussia inside the term is reneging, and it returns the heavier: their will against us +15, relations -25 and the strongest casus belli in Europe. Buying it wakes Armed Neutrality next (600g to buy off in turn). Buy it off? (yes / no)" with [Buy it off] [Not now] [Cancel Order]. #112 `click Not now` → Gold 1,563 and DP 7/7 unchanged. Verdict **SEEN**. Observation: the third button of the quote reads "Cancel Order" though no order is pending.

## FIRSTSTEP scene (`replay_firststep`, turn 4) — loaded twice (#116 and #135)

### S14E-30 — sea #7 (PARTLY — the Soult interrupt did not arise on this board)
First load (#116): #117 `click End Turn` (passed; no gate). Turn 5's morning (#118): the enemy phase and four battle replays (Mack on Lannes at Franche-Comte, Archduke Charles on Massena at Bohemia, …) came first; no interrupt popup followed (#119-#122 Escape ×4; the fourth opened the pause menu). Soult's standing march did NOT halt at Tyrol: the dispatch row read "> Soult — Franconia — 28,480 — Moving to Milan — 2 turns out. (to the letter)" and the report "Soult holds at Franconia, per your orders — the guns at Bohemia did not move him." At turn 6 (#126-#127) "Soult: Soult adjusts route to avoid enemy at Tyrol. Moves to Swabia." — a route-around, not an interrupt. Second load (#135, after Massena's deed at #136, #142 `click End Turn`, #143 `click Continue`): the same (turn 5 "Moving to Milan — 2 turns out", no interrupt). So the sighting's state (a standing order that halts on contact and RAISES the question at the morning) was not reachable from this save. 
The fixed ORDER was seen on another interrupt that rides the same `_on_strategic_report_dismissed` path: boot turn 4 (#89-#92) — after #88 `click End Turn` and #89 `click Continue` the terminal printed the whole Morning Dispatch (its MARSHAL STATUS row "? Teulie — Milan — 3,751 — Hunted by Archduke Charles on consecutive turns — holds Milan with 3,751 men. Morale:24%") and ended "Teulie awaits your orders!" while the InterruptPopup "TEULIE REPORTS" stood open ("Fight to the Last" / "Attempt a Breakout"); #92 `click Attempt a Breakout` then logged "> Teulie: attempt breakout / Teulie cuts his way out! Teulie falls back on Piedmont …" AFTER the dispatch — briefing, question, answer in truth order. The re-read after the answer (`key R`) on that case was not taken (the autosave was gone by the time I thought of it); on the firststep board the re-read (#145 `click Dispatch`) reads "> Soult — Franconia — 28,480 — Moving to Milan — 2 turns out. (to the letter)" and "> Massena — Bohemia — 28,375 — Moving to Milan — 2 turns out. ⚠ IN PERIL — an enemy force of ~45,885 shares the field (Bohemia)." Verdict **PARTLY** (the order seen on Teulie's interrupt; Soult's HALTED row and the stale-headline half NOT reached).

### S14E-1 — sea #6 (second load, turn 4, before any End Turn)
(The first load's Massena order at turn 5 was refused: "Massena is engaged with Archduke Charles and cannot begin a strategic march. Deal with the engagement first." — #123, because the enemy phase had already engaged him.) Second load #136 `type Massena, march to Milan` (move Massena), frame 0136: the reply and the log open with "⚔ The Great Battle of Tyrol ⚔" then "Massena: 'Archduke John bars the way at Tyrol, Sire — I can take him.' Massena engages him on the road, on his own judgment." then the MUSTER block ("MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable. WILL NOT — Soult … WILL NOT — Bernadotte … Archduke John does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. …"), the battle ("Brutal stalemate between Massena and Archduke John. Heavy casualties on both sides: Massena 7,673, Archduke John 6,020"), and Berthier's closing line "Berthier: an inconclusive affair of his own making — nothing gained, nothing charged." (a stalemate: no laurel, no trust change — the rule's third arm). #138/#140 the campaign log (opened by the Event Log button — `key L` after the Escape typed an "l" into the focused line): "The Great Battle of Tyrol: Massena (France) attacked Archduke John (Austria) — stalemate (7,673 / 6,020 casualties) — on his own judgment, on the road — Archduke John: "Neither yields. The Alps are patient, and so am I."" Verdict **SEEN** (the stalemate arm; the win laurel/+2 and the loss −5 arms were not exercised — a stalemate came up).
Observation: after a battle replay's Esc the command line is focused, so a bare hotkey (`key L`) is typed into it ("command line: 'l' (focused)") — the hotkey is blocked while the line holds focus (by design: "the bare keys work whenever you are not typing").

## CLOCK scene (`replay_clock`, turn 19; loaded at #149)

### S14E-35 — sea #13 (NOT SEEN on the client; the number checked by a read-only backend call)
#150 `click End Turn` (no gate), #151 `click Continue`, #152 Escape (replay). The turn-20 dispatch (terminal at #151) reads "COALITION THREAT / Threat: 58/100 [Formed] / ACTIVE: Third Coalition — Leader: Britain / Berthier: "Ground lost can be retaken, Sire …"" — NO "Europe has watched us 7 quiet turns …" line. Cause: `league_summary_line` returns "" while a league is formed (`forecast.formed`), and the scene's Third Coalition IS formed (save: `active_coalition` Britain/Austria/Russia; `armed_peace_reading` reason "league"); the sea player's sighting stood on a board with no formed league. #153 the war panel's coalition detail has no such line either. A read-only in-process load of `saves/replay_clock.json` (no file written): `hegemon_quiet_turns(world, "France")` = 6 at turn 19 (store 13) — so 7 at turn 20, not the roster's 15/16 — i.e. the DATA is fixed, but the sentence can only be seen on a board with no formed league. Verdict **NOT SEEN** (premise of the scene wrong; the fix's number confirmed backend-side only).

## SEA scene (`replay_sea`, turn 6; loaded at #157)

### S14E-31 — sea #8
Frame 0157: the war panel reads "War with the Third Coalition" (not "War for Munster") and the card's tooltip "The War with the Third Coalition: France holds Munster of Britain's." (#163 the war detail repeats it: "The War with the Third Coalition: France holds Munster of Britain's."). Verdict **SEEN**.

### D10 — the camp wash
Frame 0158 / crop `crops/0158_1300_300_700x450.jpg`: the camp provinces (the Flanders–Artois block and Brittany) are washed salmon-pink; Artois' region panel (#159, frame 0159) and hover tooltip read "Descent camp: 46,500 men, 2 turns — staged". Verdict **SEEN** — BUT in this scene the whole rest of the map is BLACK (every non-camp province unfilled) through #157-#163, across `alt+m` (#160, "Map view: political") and after a typed line (#161). The firststep scene's map after a load was coloured (frame 0136). See NEW ROW 1.

### S14E-13 — sea #5
#162 `type Soult, march to Normandy` (move Soult), frame 0162: "Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy. / Picardy feeds 22,500; the 56,500 men standing there would lose ~1,844 a turn to short supply. / Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end. "Soult, march to Normandy." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)" The same line sits on the region panel's march chip (#159, Artois: "Soult · 1 AP · 2 turns  Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end."). Verdict **SEEN**.

### S14E-15 — sea #12
The war card's held line (#163 war detail): "A peace signed now is on the held line: Munster stays ours by the treaty — and closes the Ireland carve, Ulster not yet held." (the hover tooltip is cut at 200 characters by the instrument: "… closes the Ireland carve, Uls"). F1 → Britain → `click Propose Peace` (#168): the bilateral PEACE PREVIEW (frame 0168) carries no road line; `click Adjust terms` (#169) opens the table over Britain alone and its text reads "White Peace — on the held line: each side keeps what it holds. / What the treaty titles / * Status quo: Munster stays ours by the treaty — titled. / This peace ends the war and closes the Ireland carve — Ulster not yet held." The Congress clock "(1 held, unsettled: Munster — on the road to Ireland)": the dispatch (#157) has no Congress section, so not shown here. Verdict **SEEN** (war card, table review); the preview's own text has no such line (the row names the offer and ratification review, which is the table).

### S14E-14 — sea #10 (second reading)
#171 `click Ledger`, #172 `click ADMIRALTY`: "The Grand Diversion  45 in 100 at readiness 70 — and again 4 turns after, whatever the outcome; a success opens London-Normandy for both turns of the window; if she is caught she meets Britain's 110 effective against our 49 — a decisive defeat is the likely result: about half of every pooled fleet (France 45→~20, Spain 30→~14, Holland 12→~5) is lost; Britain's side loses ~4%." and again in "The Grand Diversion (the button below)". Verdict **SEEN**.

### S14E-8 / D7 (sea scene, Britain)
F1 → Britain: "Propose Armistice — 15 of 50 ✗ (1 DP)", "Open Settlement with Britain alone — -8 of 50 ✗", "the whole table — -8 of 50 ✗" (#167). No counsel sum quoted ("Propose Peace comes nearest at 2 of 50").

## MISSION scene (`replay_mission`, turn 14; loaded at #176 — the map here is fully coloured, frame 0176)

### S14E-9 — diplomacy #7
#177-#180 F1 → scroll → `click Austria` (the list row reads "Austria — Peace | -40 (Hostile) [MISSION]"). Frame 0180: the mission row "Cancel: Improve Relations — Hostile (+20 over 4 turns) — +32 earned, -15 from Prussia's declaration, drift +3" — the parts sum to the headline (32 − 15 + 3 = 20). The row says "-15 from Prussia's declaration" without the brief's "on Hanover" and shows no "paused N turns" part (the scene's shock has no target named / no pause). Verdict **SEEN** (parts sum; the optional "on Hanover" / "paused" words not present in this scene).

### S14E-34 — sea #11
#183-#184 F1 → Prussia (scrolled the page to its foot): `Improve Relations (1 DP) — +8 relation/turn` DISABLED with the tooltip "Talleyrand is at Austria's court — F1 → Austria → Cancel"; the counsel above reads "Improve Relations is shut while Talleyrand is at Austria's court — recall Talleyrand from Austria first (the Cabinet's Recall is free)." (frame 0184). #186 `click End Turn` (no gate): the turn log and the dispatch (#186/#187) carry "Austria and France are at peace — Talleyrand is home."; the top bar's Talleyrand button went "Talleyrand: Improving Relations..." → "Talleyrand: Idle"; after answering four letters (#188-#195) the Cabinet's Austria page (#199) offers a FREE "Improve Relations (1 DP) — +8 relation/turn" in place of "Cancel: Improve Relations". Verdict **SEEN**. (A rail chip "Talleyrand at Austria — Improving Relations" was still listed in the top bar at #187, the morning of the completion — a stale notice; see NEW ROW 3.)

### S14E-27 — extra reading (turn 15 letters)
The Switzerland petition's row (#192): "Incoming proposal: Client's Petition" with "Terms: Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections …" and the reason line "A client's petition is granted or refused in full — open to decide." Verdict **SEEN** (the petition variant).

## SPAIN scene (`replay_spain`, turn 11; loaded at #204 — the load list scrolls: Autosave, clock, firststep, sea, mission, then spain, detour, peril, beira, …)

### S14E-11 — diplomacy #9
#205-#209 F1 → scroll → `click Spain` (the list row "Spain — Alliance | +2 (Neutral)"), frame 0209: "Our alliance with Spain frays, Sire — relations stand at 2, short of the 40 it holds on. Talleyrand recommends: Reassure Ally — +4 a turn on relations, 1 DP a turn." and the row "Reassure Ally (1 DP) — +4 relation/turn". Verdict **SEEN**.

### S14E-10 — diplomacy #8 / D8
#210-#213 F1 → Britain → `click Propose Peace` (the bilateral preview), frame 0213, Political Consequences: "Mark one thing, Sire: Spain's war with Britain ends in this instrument; she takes nothing by it and is left out: -18 relation and a grievance; Make Amends (400g + 2 DP) clears it." — before any send. Verdict **SEEN** (the cost stated, the lever named, the peace-ends-her-war pass reaching her). The sentence is printed TWICE (NEW ROW 2).

## DETOUR scene (`replay_detour`, turn 19; loaded at #218)

### S14E-22 — conquest #12
#219 `type Soult, march to Vienna` (move Soult), frame 0219: a free ask on the clarification channel, "BERTHIER ASKS: "The direct road to Vienna via Bohemia is closed by the truce with Austria; the lawful road is 7 provinces, 7 turns, through Prussia and Russia — march, or cancel?"" with [March (1 AP)] and [Cancel Order]. #220 `click Cancel Order`: "Order cancelled. Berthier nods. "Very well, Sire — the order is withdrawn."" — the Actions readout 4/4 before (#219) and after (#220). Verdict **SEEN** (the brief's "(or the cancel option)" — the button reads "Cancel Order", not "cancel").

## PERIL scene (`replay_peril`, turn 8; loaded at #224)

### S14E-7 — conquest #13
#225 `click End Turn`, frame 0225 (visible in the command window): "⚠ Soult's corps (10,000) stands in peril — an enemy force of ~32,000 shares the field (Hungary). 3 corps stand below 40% morale beside Buxhowden (32,000, Hungary) — end the turn anyway? / Press End Turn again, Enter, or type end turn again to end the turn anyway." (the turn did not advance). The scene's board names Buxhowden at Hungary (32,000) rather than the brief's Kutuzov (~38,000, Moravia); the shape — peril line, then one "N corps stand below 40% morale beside <enemy> (<strength>, <province>) — end the turn anyway?" line — is as promised. Verdict **SEEN** (names differ from the brief: Buxhowden/Hungary for Kutuzov/Moravia). The gate was left standing (not confirmed).

## BEIRA scene (`replay_beira`, turn 6; loaded at #228 — war panel "Shared war: Britain + Austria + Portugal + Russia")

### S14E-6 — conquest #11 and D5 (NOT SEEN — the clause on Portugal could not be authored on this board)
#229 the war card, #230 `click Open Settlement` (frame 0230): the table seats "Austria + Britain + Russia - Separate settlement … Covered enemies: Austria, Britain, Russia / Still at war: Portugal"; Portugal is not seated and the table offers no "Bring Portugal to the table" control (the boot's table had "Bring Britain/Russia to the table"; here the Coverage row is absent), so no demand on Portugal (Beira) can be added: the `+ Add demand` lists offer only "Take Tyrol from Austria / Demand 200 gold / … / Austria joins the Continental System" (Austria, #233), "Take Wessex from Britain / … / Erect Ireland from Britain's lands — unavailable (requires Ulster, Munster)" (Britain, #238). `Harsher terms` (#239-#241) only withdrew concessions. The Blocker lines that showed read "Blocker: National design / Metternich regrets that Austria must remain… unconvinced — it would seal their national design out of reach." (Austria 33/50), "Blocker: Settlement legitimacy / Castlereagh declines for Britain: …" and Russia's "National design" — never the promised "… reads as a claim of victory the field has not delivered — remove it, or drop Portugal." `click More generous` (#231, #234-#236) bought acceptance with gold (Austria 33→41→55, committed 300→800) and, with the chest spent, stopped at "Treasury 800 gold: committed 800 / reserve 0 / remaining 0" with Russia 35/50 holding out on "National design" — the "Gold cannot buy this, Sire — …" refusal (every holdout blocked on legitimacy) was not reached. Verdict **NOT SEEN** (unreachable from this scene: Portugal has no seat at the table; the fix's blocker and refusal wording not shown).
Observation: the table's row for Britain reads "Holding out (14/50) / Blocker: Settlement legitimacy" while the headline says "Russia is the holdout." (Britain is "covered, not consulted").

## RUMP scene (`replay_rump`, turn 11; loaded at #248 — the load list's third scroll: … beira, rump, sanctuary, letters, "Unknown (Turn ?)")

### S14E-5 — conquest #10
#249-#253 F1 → scroll → `click Hanover` (list row "Hanover — Peace | -50 (Hostile)"), frame 0253: the assessment opens "Status: Peace   Relation: -50 (Hostile) / Hanover holds 1 province (Osnabruck); the rest are Prussia's." #254-#256 scrolling the page: `Declare War (1 DP)` DISABLED, tooltip and line "Prussia holds Hanover, Hanover's capital; this purpose scores only while we hold it." (frame 0256). Verdict **SEEN**.

## SANCTUARY scene (`replay_sanctuary`, turn 5; loaded at #261)

### S14E-4 — conquest #8 (PARTLY)
#262-#267 F1 → Austria → `click Propose Peace` (frame 0267, PEACE PREVIEW): Political Consequences include "Kutuzov (Russia) stands at Moravia, Austria's soil — after this peace no corps of ours may take the field against him there." — SEEN. (The same preview prints "Mark one thing, Sire: Bavaria's war with Austria ends in this instrument; she takes nothing by it." and the plain sentence again — NEW ROW 2's third sighting.) #268 `click Not Now`, #269 `type what if Murat attacks Kutuzov` (question): the reply is the plain muster — "MUSTER — Murat (22,000) vs Kutuzov (substantial force) at Moravia — the balance of force looks unfavorable. … Nothing has been ordered, and nothing spent." — NOT "The order would be refused, Sire: …": France is still AT WAR with Austria, so Moravia is lawful ground and nothing yet forbids the order (the sanctuary is a consequence of the peace). To reach the refusal I sent the peace (#270-#274 `Send as suggested`, 3 DP): the next turn's log (#275-#276) read "Talleyrand returns from Austria empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was the war is barely begun — no court signs away a province over one skirmish." — no peace, so no sanctuary, and the refusal wording could not be seen. (Turn 6 then opened with "MURAT REPORTS — Murat is cornered at Vienna with 6,647 men" and a Murat interrupt.) Verdict **PARTLY** (the preview's consequence seen; the typed what-if's refusal NOT reached — it needs a signed peace with Austria).

## LETTERS scene (`replay_letters`, turn 2; loaded at #284 — the mailbox panel opened on the load, Prussia's letter ACTIVE)

### S14E-27 / S14E-23 / S14E-20 / S14E-18 / S14E-28 / S14E-29 (the second reading, same sentences as the boot's turn 2)
- #284: the panel's subtitle "… Routine letters from the lesser courts answer in place; every other letter opens in full."; Prussia's row "Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade" and "A great court's letter is answered in full — open to accept, haggle or refuse."; Saxony's "… · Saxony pays you 82 gold at the signing"; each row an "Open ▸" button. **S14E-27 SEEN.**
- #285 `click#1 Open ▸` (frame 0285): "DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia / Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: - Proposal: Open Borders Agreement - Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade". **S14E-23 SEEN.**
- The modal's buttons: Accept / Reject / Not Now — no "Let Talleyrand haggle" on this courtesy letter (hidden). **S14E-20: SEEN as hidden; the greyed "Prussia has nothing to trade at this price." and the "— no point spent" result line did not arise (no haggle option to press).**
- #286 `click Not Now`: "Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit." #287 F1 (the Cabinet button): "An unanswered envoy awaits your reply — the Cabinet stays shut until it is answered or the turn ends. Reopen Envoys to answer it." with [Open Envoys (3)]. **S14E-18 SEEN.**
- #288 `click Open Envoys`, #289 `click#1 Accept` (Saxony): the log "You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury." and the Gold readout 800 → 882 in the same frame. **S14E-28 and S14E-29 SEEN.**

## Closing notes

- The firststep scene was loaded a third time (#301) for S14E-25: after the player's stalemate at Tyrol (#302) the Austria armistice preview (#307) and the war card read "nothing taken yet on either side" / "Battles: 0W / 0L" — a stalemate is not recorded as a battle (see NEW ROW 5). The boot's turn-4 war tooltip (frame 0115) reads "The War with the Third Coalition: France retook Swabia for Bavaria; 5 battles fought." — the fix's wording for won battles.
- The Tyrol battle reproduced exactly on the second and third load (7,673 / 6,020 casualties both times): the sandbox is deterministic.
- S14E-24's marshal-first card route: selecting Ney at his token (`click_at` one label-height below his name, #291 "Ney selected — click a province: march · an enemy …") works, but the follow-up click on Swabia (#295) opened the region panel, not the card; the panel's own one-line muster is what was read.

## NEW ROWS filed (rows.json): five
1. #157 P2 — the sea scene's map is black outside the camp wash.
2. #213 P3 — "Mark one thing, Sire: …" and the plain separate-peace sentence printed twice in the Political Consequences (frames 0027, 0168, 0213, 0267).
3. #199 P3 — the "Talleyrand at Austria — Improving Relations" rail chip survives the mission's completion for the whole turn.
4. #111 P3 — the Buy Off quote carries a "Cancel Order" third button.
5. #307 P3 — a stalemate fought battle leaves the war title and the preview at "nothing taken yet on either side".

## The verdict table

| row | scene | frame | verdict | the sentence / control seen |
|---|---|---|---|---|
| S14E-1 | firststep | 0136, 0140 | SEEN (stalemate arm) | "Massena: 'Archduke John bars the way at Tyrol, Sire — I can take him.' Massena engages him on the road, on his own judgment." then the MUSTER; Berthier "an inconclusive affair of his own making — nothing gained, nothing charged"; log "— on his own judgment, on the road" |
| S14E-2 | boot | 0004 | SEEN | "Swabia is Bavaria's soil — the corps standing there are fed by contract, about −1,200g more a turn." |
| S14E-3 | boot | 0036, 0037 | SEEN (sweeteners road) | gold step: Offer 25 gold / … / Never mind; AP step: Back + Never mind; Esc leaves |
| S14E-4 | sanctuary | 0267, 0269 | PARTLY | preview: "Kutuzov (Russia) stands at Moravia, Austria's soil — after this peace no corps of ours may take the field against him there."; the typed what-if gave the plain muster (still at war; the peace sent at #274 was rejected) |
| S14E-5 | rump | 0253, 0256 | SEEN | "Hanover holds 1 province (Osnabruck); the rest are Prussia's."; Declare War disabled "Prussia holds Hanover, Hanover's capital; this purpose scores only while we hold it." |
| S14E-6 | beira | 0230–0241 | NOT SEEN | Portugal has no seat at the table and no Bring-Portugal control; no clause on Portugal could be authored; the tier-mismatch Blocker / "Gold cannot buy this" lines not shown |
| S14E-7 | peril | 0225 | SEEN | "3 corps stand below 40% morale beside Buxhowden (32,000, Hungary) — end the turn anyway?" after "Soult's corps (10,000) stands in peril — an enemy force of ~32,000 shares the field (Hungary)." |
| S14E-8 | boot, sea | 0017, 0022, 0167 | SEEN | wizard "Propose Armistice — 6 of 50" / preview "Score: 6"; "12 of 50" / "Score: 12" |
| S14E-9 | mission | 0180 | SEEN | "Cancel: Improve Relations — Hostile (+20 over 4 turns) — +32 earned, -15 from Prussia's declaration, drift +3" |
| S14E-10 | spain | 0213 | SEEN | "… she takes nothing by it and is left out: -18 relation and a grievance; Make Amends (400g + 2 DP) clears it." (printed twice — row 2) |
| S14E-11 | spain | 0209 | SEEN | "Our alliance with Spain frays, Sire — relations stand at 2, short of the 40 it holds on. Talleyrand recommends: Reassure Ally — +4 a turn on relations, 1 DP a turn." |
| S14E-12 | boot | 0004 | SEEN | "expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017" |
| S14E-13 | sea | 0162 | SEEN | "Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end." |
| S14E-14 | boot, sea | 0049, 0172 | SEEN | "If she is caught she meets Britain's 110 effective against our 49 — a decisive defeat is the likely result: about half of every pooled fleet (France 46→~21, Spain 30→~14, Holland 12→~5) is lost; Britain's side loses ~4%." |
| S14E-15 | sea | 0163, 0169 | SEEN | war card "… Munster stays ours by the treaty — and closes the Ireland carve, Ulster not yet held."; table review "This peace ends the war and closes the Ireland carve — Ulster not yet held." (Congress clock not shown) |
| S14E-16 | boot | 0006 | SEEN | "Yes, Sire — Bernadotte can reach Vienna from Franconia in 2 turns: Franconia -> Bohemia -> Vienna. The order is 'Bernadotte, march to Vienna'." |
| S14E-17 | boot | 0005 | SEEN | "The band weighs a force of his you have not scouted within reach of Tyrol — scout the provinces round it." |
| S14E-18 | boot, letters | 0058, 0059, 0286, 0287 | SEEN | "Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit."; locked Cabinet says the same |
| S14E-19 | boot | 0028 | SEEN | the table "the table with Austria - Separate settlement", not "Shall we discuss concessions, Sire?" |
| S14E-20 | boot, letters | 0057, 0285 | SEEN (hidden) | no "Let Talleyrand haggle" on a courtesy letter; the greyed / "no point spent" arms not reached |
| S14E-21 | boot | 0056, 0066, 0081 | SEEN | one Esc closes the replay; placeholder "Esc: menu · click to type" |
| S14E-22 | detour | 0219, 0220 | SEEN | "The direct road to Vienna via Bohemia is closed by the truce with Austria; the lawful road is 7 provinces, 7 turns, through Prussia and Russia — march, or cancel?"; cancel leaves Actions 4/4 |
| S14E-23 | boot, letters | 0057, 0285 | SEEN | "Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade"; "Proposes: Open Borders Agreement (free military passage)" |
| S14E-24 | boot | 0003, 0073 | PARTLY | Commands line + TODAY line seen; the panel's one-line muster seen; the marshal-first map card not reached |
| S14E-25 | boot, firststep | 0022, 0115, 0307 | PARTLY | no "(N more concern…)" line, score equals War score, quiet-war title "nothing taken yet…", "France retook Swabia for Bavaria; 5 battles fought."; a stalemate battle is not counted (row 5) |
| S14E-26 | boot | 0111, 0112 | SEEN | the quote "Buy off Prussia's design — … 1,200 gold and 1 diplomatic point. The treasury holds 1,563 gold and would hold 363 after. The want sleeps 15 turns; …"; Not now leaves Gold 1,563 |
| S14E-27 | boot, letters | 0060, 0192, 0284 | SEEN | "Open ▸" flat button, a Terms line, "A great court's letter is answered in full — open to accept, haggle or refuse.", petition "… is granted or refused in full — open to decide.", the subtitle |
| S14E-28 | boot, letters | 0062, 0085, 0289 | SEEN | "Saxony pays you 82 gold at the signing"; "Saxony paid 82 gold into the treasury." |
| S14E-29 | boot, letters | 0062, 0085, 0289 | SEEN | Gold 734→794, 885→967, 800→882 in the accept's own frame |
| S14E-30 | firststep, boot | 0118, 0089–0092 | PARTLY | the Soult interrupt never arose (Soult "Moving to Milan — 2 turns out"; at turn 6 "adjusts route to avoid enemy at Tyrol"); dispatch → question → answer order seen on Teulie's interrupt |
| S14E-31 | sea | 0157, 0163 | SEEN | "War with the Third Coalition"; "France holds Munster of Britain's." |
| S14E-32 | boot | 0010 | SEEN | "Murat halts his march and awaits new orders." |
| S14E-33 | boot | 0011 | SEEN | "Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips." |
| S14E-34 | mission | 0184, 0186, 0199 | SEEN | Improve Relations disabled "Talleyrand is at Austria's court — F1 → Austria → Cancel"; "Austria and France are at peace — Talleyrand is home."; the Cabinet's mission row free |
| S14E-35 | clock | 0151 | NOT SEEN | no "Europe has watched us … quiet turns" line: the save's Third Coalition is formed and `league_summary_line` returns ""; backend read: 6 quiet turns at turn 19 (store), not the roster's |
| D10 | sea | 0158, 0159 | SEEN, with a P2 defect | camp washed, tooltip "Descent camp: 46,500 men, 2 turns — staged" — but the rest of the map black (row 1) |
| D7 | boot, sea | 0017, 0167 | PARTLY | row text "Open Settlement with Britain alone — -8 of 50 ✗" read; the counsel quoted no sum, so "Offer N gold to Britain" not exercised |
| D5 / D8 | beira / spain | — / 0213 | D5 NOT SEEN / D8 SEEN | see S14E-6 / S14E-10 |

Run totals: 309 actions (run.json n_actions; the boot state is 0000, the last is the quit), 3,131 s wall, engine exit 0, run.json `n_script_errors` 0. The engine log carries 21 plain `ERROR:` lines that the driver's SCRIPT ERROR regex does not match: 18 × "Lambda capture at index 0 was freed. Passed "null" instead.", 2 × "Cannot clear the font 'normal_font' because it does not exist.", 1 × "2 resources still in use at exit". Road label in meta.json: `sea` (the driver refuses `--road replay`).
