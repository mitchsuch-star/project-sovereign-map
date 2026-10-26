# DD-B — the third measure (Pre-Deploy S14g, October 25–26, 2026)

*Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2 row S14g. The first measure
(`docs/audits/DD_B_FRESH_EYES_2026_10_14.md`) found 69 causes in 60 turns —
11.5 rows per 10 turns, 3 P1; the second (`DD_B_RE_MEASURE_2026_10_24.md`) found
35 — 5.8 and 1 P1 — and S14f fixed every row it filed (three parts, October
24–25) with the nine rulings D12 … D22 and S15's head on top. This measure reads
the build the testers will get: master `a47bc116`.*

**Verdict.** Three fresh players, the same brief and the same roads, 20 turns
each in the real client at 5120×1440. Their 37 rows de-duplicate to **33 causes:
5.5 rows per 10 turns, none of them P1.** The done-when (under 5 per 10 turns and
0 P1) is **NOT met on the rate** — by four causes (33 against 29) — and is
**met on the P1 bar for the first time** (3 → 1 → 0). Against the second measure
the rate barely moved (5.8 → 5.5): **none of its 35 rows was sighted again as
filed**, five came back in part (S14E-11, 13, 15, 17, 18 — the sentence fixed, a
neighbouring surface or a withheld half drawing the same confusion), and **27 of
the 33 causes are siblings of, or partial returns of, a row an earlier slice
fixed**; six are new. Every road reached Turn 21 without a script error. As the
plan's rule requires, every row is filed and homed:

- the 33 causes go to a new row, **S14h "the third measure's rows"**
  (`BUG_FIXES.md` §S14G, S14G-1 … S14G-33, plus the instrument row S14G-I1), the
  twelve P2s first;
- the six design halves and the done-when's own question go to
  `DESIGN_REFINEMENT.md` §S14G (S14G-D1 … D7), each with a recommendation, for the
  user at S14h's head;
- the release build (S15) **waits** for S14h: the plan's gate is 0 open defect
  rows, and this measure files 34.

Nothing in the game was changed in S14g. The instrument changed in one small way
(§6, §7): the judge learned the reply "already carrying out that order".

---

## 1. The instrument

`tools/dd_b_client.gd` and `tools/dd_b_play.py` as the second measure ran them
(`SYSTEMS_REFERENCE.md` §115): the game as it launches (the title screen, a first
launch, Interface Scale 1.4 derived for the screen), a sandboxed backend on 8006
(the mock parser, the historical seed, its own saves; the user's 8005 never
touched), real input events one action at a time, the full frame and the state
record after each. Each player got `docs/audits/dd_b/PLAYER_BRIEF.md` verbatim
(the road, the goal and the run directory filled in) and nothing else; the
players were general-purpose agents on a lower model (sonnet), one at a time; two
engines never ran at once. The working tree was `a47bc116` under all three engines
(another session, which held its `.gd` edits until the third engine was down,
edited the instruments' readers afterwards).

| Road | Goal given | Turn reached | Actions | Typed lines sent | Wall time | SCRIPT ERRORs |
|---|---|---|---|---|---|---|
| conquest | win the war in the field; take Vienna | Turn 21 (July 1806) | 344 | 91 (2 typed under a modal, never sent) | 46 min | 0 |
| diplomacy-first | end the war at the table before fighting it out | Turn 21 | 299 | 27 | 37 min | 0 |
| the sea | make the navy count: break the blockade, raise Ireland, or carry the war across the Channel | Turn 21 | 347 | 123 (8 typed under a modal, never sent) | 41 min | 0 |

Settling took about 3 s an action. The 990 actions raised no SCRIPT ERROR (the
diplomacy and sea engines each printed one plain `ERROR: 2 resources still in use
at exit`, which the instrument counts apart as `n_engine_errors` — the S14E-X202
class). The records are
`docs/audits/dd_b/{conquest,diplomacy,sea}_2026_10_25/` (rows, the judge, the
actions, every action's summary, the players' notes, each cited frame).

## 2. The three campaigns, in the players' words

- **Conquest.** Mack smashed at Swabia with two attacks on turn 1; Charles took
  Munich and Ney retook it on turn 3; Charles and John broken at Tyrol on turn 4;
  the field army beaten at Vienna's gates on turn 6 and the capital taken by three
  assaults on turn 7 (Davout, Ney, then Murat for the glory); Massena took Hungary
  and captured the Archduke the same turn. Austria's peace was taken on turn 8,
  Russia's white peace on turn 9, Britain's on turn 19; between times envoys,
  petitions, the Grand Quartier General and the Train des Equipages, one expedition
  (Bernadotte to East Anglia, intercepted: 4,244 men and 26 sail) and a Channel camp
  staged on turn 18 whose window never opened (Spain's sail left when she made
  peace with Britain). The player's verdict: supply is the real enemy and the
  warning comes late; several orders "quietly keep acting".
- **Diplomacy-first.** Talleyrand's one piece of advice cost 3 of 5 DP on a plain
  peace letter; two battles on turn 1 and two on turn 2 (Mack captured) lifted the
  war score to +39; the Austria armistice was accepted on turn 3 (51 of 50) and
  Austria took Munich and Swabia under it on turn 4. On turn 6 "Open Settlement
  with Britain alone" and "with Russia" each read "Will sign" for about 950–975
  gold and both were ratified — the Third Coalition dissolved (threat 95 → 47).
  The Austrian truce ripened into peace on turn 9; then buy-offs of Britain's,
  Russia's and Austria's designs, a licence for Prussia, Bavaria and Hesse made
  vassals, the small courts' letters. At Turn 21 France is at peace with every court,
  holds five vassals and 22,609 gold. The player called the dispatch and the Balance
  of Europe page "the best thing in the game for the diplomatic road".
- **The sea.** The Admiralty book taught the camp: Soult and Napoleon to Flanders
  staged it by itself and the blockade lifted — for a few turns, until Soult left
  the camp to chase Paget. The first Ulster landing (72 in 100) was caught at sea
  (the fleet 46 → 20 sail); the second (Dumonceau, 4,550 men) landed and could not
  hold — a corps under 5,000 holds no homeland province; a commissioned 5,000-man
  Oudinot (69 in 100) took Ulster, then Munster, and the Formable Nations page
  showed Ireland with every requirement ticked and an "Open negotiations — Britain"
  button. At the table "Erect Ireland" stood at 26 of 50 after "More generous" had
  stopped at 1,000 gold. The Grand Diversion and the Channel descent never opened
  (the effective fleet stayed under the 44–51 the page asked for); the homeland
  collapsed late (18 of 28 provinces, Massena and Murat prisoners, Austria and
  Russia deep in France).

Their notes are `docs/audits/dd_b/<road>_2026_10_25/player_notes.md`.

## 3. The metric

**How it is counted** (the first measure's rule): each road counts each cause once,
at its worst sighting on that road; the total across the three counts each cause
once, at its worst. Severity is the players' own. The figures are read off the
records by ONE tool, `tools/dd_b_metric.py` (`--check` passes: every player row a
sighting of a cause, every sighting a row whose frame is in the repository);
`metric_2026_10_25.json` holds them.

| | Player rows filed | Causes | P1 | P2 | P3 | Rows per 10 turns | Second measure |
|---|---|---|---|---|---|---|---|
| conquest | 12 | 12 | 0 | 5 | 7 | **6.0** | 6.5 |
| diplomacy-first | 16 | 15 | 0 | 4 | 11 | **7.5** | 4.5 |
| the sea | 9 | 9 | 0 | 4 | 5 | **4.5** | 7.0 |
| **the three** | 37 | **33** | **0** | **12** | **21** | **5.5** (P1 0.0 · P2 2.0 · P3 3.5) | 5.8 (1 P1) |

Four rows are duplicates, none struck: the stale peril warning is two rows of the
diplomacy road (#2, #3); the Cabinet's lock is conquest #6 and diplomacy #11; the
bare-key hints are conquest #4 and diplomacy #14; the truce that leaves Bavaria's
war running is diplomacy #7 and the sea #6. 37 rows − 4 = 33 causes.

**The done-when** is under 5 rows per 10 turns and 0 P1: **NOT met** — the rate
reads 5.5, four causes over the bar (29 would read 4.8). The sea road alone meets
it (4.5), conquest is two causes over (6.0) and diplomacy five (7.5 — it was the
best road last time at 4.5): the roads trade
places because each fresh player walks different surfaces: **the rate is a property
of how many surfaces a campaign touches that the last fix did not reach, not of
how well the last fix held** (§5, and the question S14G-D7).

## 4. No P1 — and what the players met most

No player filed a P1, and by the judge every sent line of the three roads read as
meant, asked, answered or refused honestly: **0 P1 proxies** (§6). The closest the
players came is sea #2 ("Continue as Ordered" — a misreading, §7) and the two
corps-sent-home rows (diplomacy #7, sea #6), where a game action the player did not
order (Berthier's road home) followed a truce the player did accept; both rows are
the player's own P2s, and the road home is the standing rule (WIN-D3) — the
price was in the preview as a count and not as a consequence.

The 33 causes fall into three families:

1. **A price or a consequence not stated at the point of choice** (13). An aggressive
   marshal on a standing order will leave it for another man's guns (S14G-2); a
   "support" order follows a moving ally, or lapses, by the supporter's NAME
   (S14G-3); a truce lets the ally's ground fall under the French corps and
   Berthier march them home (S14G-7); two buy-offs leave the court in the league
   (S14G-9); a licence's war costs the licensee's relations with Europe (S14G-10); a
   march crosses a neutral's guarded ground (S14G-11); sending any letter pauses
   the courtship (S14G-25); "draft kept" means one turn (S14G-26); Reassure Ally and
   a courtship share one diplomat (S14G-28); an Admiralty link spends 2 of 4 actions
   unsaid (S14G-29); an expedition's prize (S14G-31); breaking the camp brings the
   blockade back (S14G-32); a march's road and turns (S14G-33).
2. **Two readings of one fact — the advice, the card or the record against the act**
   (11). The dispatch advises a drill the executor refuses (S14G-30); an audience
   card names a quarry that has gone (S14G-5); the recruit remedy names a man the
   levy refuses (S14G-18); the counsel reads −57 "short of the line" beside a −60
   rule (S14G-24); the peril warning names an army that has left (S14G-20); the
   dispatch announces a war that never was (S14G-21); the war banner "on the left"
   is bottom right (S14G-13); a counter marks only what it struck (S14G-23); the
   Admiralty readies an inland corps and then asks for a march (S14G-17); the band
   weighs an army the note will not locate (S14G-14); retaking an ally's capital
   scores as conquering an enemy's (S14G-1).
3. **A control or surface that does something other than it says, or hides its
   answer** (9). "Not Now" shuts the Cabinet (S14G-6); the bare key the screen
   prints dies in the command line (S14G-16); a counsel button opens a blank menu
   whose "Propose peace" sends a 3-DP treaty (S14G-8); the table's gold ceiling is
   stated on a line the header never shows (S14G-12); a same-province march spends
   an action (S14G-4); the province panel squeezed to 120 px (S14G-15); a stack's
   label that is not clickable (S14G-19); the Cabinet window that cannot grow
   (S14G-22); an empty ENEMY PHASE box every peacetime turn (S14G-27).

By pillar: diplomacy 12, command 6, naval 4, ui_ux 4, combat_legibility 2,
narration 2, economy 1, first_contact 1, living_balance 1.

## 5. What came back

**None of the second measure's 35 rows was sighted again as filed.** Five came back
in PART — the fix is in the tree and fired exactly as built, and the player asked
for what it withheld, or met the same confusion one surface over:

| Earlier row | Back as | What the fix did / what it left |
|---|---|---|
| S14E-18 (the Cabinet shut by an unanswered letter) | S14G-6 (two roads) | the sentence is on the tooltip and the post-click echo; not on the button's face, the letter, or the Envoys badge; a routine lesser-court letter still locks |
| S14E-17 (the fog-honest "a force you have not scouted") | S14G-14 | the note fires as built; it names no province and gives no reading on the men in view |
| S14E-11 (the ally's slide counselled) | S14G-28 | the busy sentence names the lever and the remedy; it does not weigh the recall |
| S14E-15 (the Ireland road at the points of action) | S14G-31 | `road_notes` covers a road already begun; a first landing has no pointer |
| S14E-13 (the camp a march leaves) | S14G-32 | the reply says the count resets; not that the blockade returns |

Four older fixes are back in the same way: S14E-X31 (IN PERIL at the click) as
S14G-20 — the clause reads the frozen snapshot; SFR-D28 (the truce that leaves an
ally's war running) as S14G-7 — a count, not a consequence; S14D-X13 / S14E-28 (the
counter's Struck lines) as S14G-23 — struck only; DDB-33 (the table's gold ceiling)
as S14G-12 — the note is authored and not shown. **Nine partial returns, 18
siblings, 6 new** (S14G-3, 4, 5, 13, 21, 27). The 18 siblings are named in each row
(S14E-7, 9, 22, 26, 13, DDB-9, 21, 42, 57, SF5-RV1, PF-2, FA-D9, PC-X61, UXR3-78,
SF7-X24 …): the sibling sweep (Rule 10) found each fix's class on the surface the
player was on, and not on the surface beside it. The shape the partial returns
share is **a fix that states the consequence in one place — a tooltip, a reply, a
page — while the player decides in another**; S14h's sweep is told to carry each
sentence to every surface where its choice is made.

## 6. The judge

Every sent typed line was classified by the ONE judge (`tools/_score_probes.py`
through `unrehearsed_census.classify_order` / `classify_question`); the players
stated each line's intent with `--meant`.

| Road | Lines sent | as_meant | answered | asked | board_refusal | honest_refusal | shrug | misread / executed-when-refusal-meant |
|---|---|---|---|---|---|---|---|---|
| conquest | 91 | 57 | 28 | 0 | 4 | 2 | 0 | **0** |
| diplomacy-first | 27 | 21 | 6 | 0 | 0 | 0 | 0 | **0** |
| the sea | 123 | 79 | 23 | 3 | 6 | 11 | 1 | **0** |

**One reply shape the judge did not know** was corrected in `_score_probes`
(`ALREADY_HELD_RX`, read in `classify_order` AFTER the action words fail): the sea
road's "Davout, march to Lorraine" (action 187), typed a second time on the turn
the first (action 173) had stood, answers "Davout is already carrying out that
order. No change." — `strategic_executor.py:1040`, free, the idempotent no-op — and
the judge read it as a `misread`, the road's one P1 proxy. By hand: the board read
the line right and said so; the class is `board_refusal`. The same phrase rides the
second measure's conquest line #244 inside a multi-line group order whose other
corps "begin march": it reads `as_meant` by the action words and stays so (a
`BOARD_GATE_RX` entry would have moved it — the reason the shape is its own regex,
checked after). 0 of the 4,350 committed census orders hold the phrase; the 319
tests that re-judge the committed records pass unchanged.

**Lines never sent.** Ten lines were typed while a modal held the command line (an
interrupt, an incoming proposal) and never reached the game (`ok: false`); the
judge lists them under `unsent` and does not judge them.

**Read by hand.** Sea #2's "Continue as Ordered" and sea #8's "the [+] would not
respond" are the two rows in which the player's account is not what happened (§7);
no typed line ran something other than it said.

## 7. Where the player was wrong, and instrument notes

The metric counts the players' rows as filed and their severities as filed; the
trace found the following, none of which struck a row:

- **Sea #2 (P2).** "Continue as Ordered" did NOT halt Napoleon: he arrived at
  Flanders (action 33). The dispatch (action 31) was built after the advance
  raised the cannon-fire interrupt and says HALTED; S14E-30 puts the dispatch
  before the question on purpose. What the player's follow-up exposed is real:
  "Napoleon, march to Flanders" for the province he already stood in was accepted
  and cost an action (S14G-4).
- **Sea #8 (P2).** The gold `[+]` was not dead: the player clicked a guessed point
  that missed it. The instrument could not name it — `dd_b_client.gd` strips
  bracketed link text, so `[+]` and `[-]` read as empty and are not listed
  (S14G-I1). The ceiling's note and the false standing hint are real (S14G-12).
- **Conquest #6, diplomacy #10, #11, #8, #16, sea #7** were each half right: the
  Not Now tooltip does say the Cabinet stays shut; the licence lowers PRUSSIA's
  relations with Europe, not everyone's with France; the greyed Cabinet button of
  action 42 was a modal disabling input, the lock only changed a tooltip; the
  tribute the player missed in Bavaria's counter was removed by their own "More
  generous"; the player could have recalled Talleyrand in one free click; sea #7's
  reply DID carry the camp-leave line (action 134, not 140) and omitted only the
  price. Each row's cause as traced is in `BUG_FIXES.md` §S14G.
- **Action numbers.** The sea player mis-numbered two rows (#3 → 0059 for 0060;
  #7 → 0140 for 0134); the true frames are exported beside the cited ones
  (`frames/0060.jpg`, `0134.jpg`, and `0031.jpg`, `0266.jpg` for #2 and #8).
- **Rule breaks**, all inside the players' own run directories: the diplomacy
  player ran one `python -c` over a state file; the sea player a few `python -c`
  readers and pipes through `sed`/`head` before Turn 3. None changed what they saw.
- **Notes from the players' tool messages, unverified:** the view JPEG sometimes
  lags one action behind a pop-up (the sea player); `type` and `look` replies are
  cut near 1,000 characters in the console summary (the conquest player — the state
  files hold the whole text, as §115.3 records); the map-piece centres the summary
  prints for a stack's label are not the clickable icon (that is S14G-19's cause).

## 8. Seen and not filed

Five mentions in the players' notes and final messages that no row carries; each is
owned by S14h part 2's sweep, which reproduces it on the boot board or a crafted
save and files it as an S14G-X row or refutes it in one line (completion: five
dispositions in `tests/test_s14h_the_third_measure_rows.py::TestTheMentions`):

1. the dispatch's "Soult, fortify" advice against the order's reply (conquest);
2. the Switzerland petition recurring (conquest);
3. each win's +8 alarm noticed only in the Threat figure (diplomacy);
4. "24,382 men waiting at Paris — nobody has gone to collect them" and no road to
   raise them (the sea);
5. the Descent's window closing because Spain's sail left on her peace with Britain,
   named only on the Admiralty page (conquest).

## 9. Where the rows go

- **S14h "the third measure's rows"** — 33 rows + the instrument row, the twelve P2s
  first, each with its decided fix, its test
  (`tests/test_s14h_the_third_measure_rows.py::TestS14G<n>`), its STATUS line and
  the tag `⟨SF step=pre-deploy S14g · DD-B third measure · pillar=…⟩`. Sized at
  **2.0 sessions**: part 1 the twelve P2s with the four rulings' builds (D1 the
  liberation, D2 the support interrupt, D3 which letters lock, D6 the bought-off
  court); part 2 the twenty-one P3s with D4 and D5, S14G-I1, the five mentions
  (§8) and the closing re-play of every sighting on the instrument from crafted
  saves (`tools/_s14f_replay_scenes.py`, as S14f part 2 did). The sibling sweep in
  force (Rule 10) — and this time it carries each fixed sentence to every surface
  where its choice is made (§5).
- **`DESIGN_REFINEMENT.md` §S14G** — 7 rows, for the user at S14h's head:
  - S14G-D1 retaking an ally's ground: liberation, handed back at once;
  - S14G-D2 the aggressive marshal's interrupt: keep it, say it at the order;
  - S14G-D3 which letters shut the Cabinet: a great court's and an ultimatum;
  - S14G-D4 the band's fog policy: name the provinces, give both readings;
  - S14G-D5 one diplomat slot: keep it, price the trade;
  - S14G-D6 a bought-off court in the league table: keep the predicate, state it;
  - S14G-D7 what the done-when gates after three measures: the P1 bar is the release
    gate and the rate the trend — fix every row, then deploy on the census, with no
    fourth measure before the deploy.
  Each lands its defect half as written whatever the ruling.
- **The deploy.** The plan's rule — the release build waits for 0 open defect rows —
  holds S15's build and clean-machine run until S14h's rows are FIXED; the user's
  walk is done (reported by the S15 session: seven ✓, UXR3-2 closed, UXR3-82 and 83
  fixed and re-shot) and the certificate is not yet on the machine, so the build
  would be unsigned in any case.
- **A fourth measure** is not in the plan's rule. S14G-D7 recommends against one
  before the deploy: three measures read one stable rate (11.5, 5.8, 5.5 with all-new
  rows each time) and a fresh player's rows fall with the sibling sweep, not with
  another sample. If the user wants the rate bar read literally, a fourth is a 1.0
  session after S14h and its expected value is the same ~5.
