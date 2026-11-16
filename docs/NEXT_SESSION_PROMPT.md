# NEXT SESSION PROMPT — Row BA, BA-4: the roads and the fog (before Session H)

> Overwritten each time a session hands off. Current hand-over: **November 16, 2026 — ROW BA, BA-3 "THE DAY'S
> POINTS" ✅ LANDED** (`BATTLE_DIORAMA_SPEC.md` §15.14 the gate, §15.15 the stop of its first pass, §15.16 the
> ruling on the measure and what its finish found, §15.17 the landing record, §15.18 its review; the rules
> `SYSTEMS_REFERENCE.md` §221; the ledger `BUG_FIXES.md` §BA3; the pins `tests/test_ba3_the_rounds.py`,
> `tests/test_ba3_the_days_panel.py`, `tests/test_ba3_the_review.py`,
> `tests/test_ws16_the_same_order_draws_the_same_temper.py`).
> **What landed:** a GREAT battle (80,000 men) the player is party to that does not decide the day is fought in
> turns on points that are the battle's own — 2, or 3 under a commander of command 8 or more; a word is an
> order the game already has and costs points, never an action; the enemy answers by the rule his AI already
> follows; two silences, both purses spent or a side leaving, and night falls; a small battle is one clash,
> told as before. With it: WS-16 (the same order from the same save draws the same temper), NP-D1 (the
> Guard's two morale numbers), the varied telling, BA2-X14 and BA2-X17.
> **The measure:** the plan's stop rule fired on the session's own `sense` bot (28 / 22 / 23); on the user's
> "do whatever is best not easiest" it was re-read as eight seeds by nine arms against a rule written before
> the data (§15.16). **The deploy gate reads the commanded arms as `score_run` runs them — silent on a day:
> 28 / 27 / 27.** Arm 0 (every new seam down) is 26 / 27 / 28. No rule and no number was changed for it.
> **The lesson of its finish, for every session after it:** the backend was whole and pinned at the stop, and
> finishing still found thirty defects — by reading the code whole, playing the real board, looking at
> the frames, and above all by pressing the REAL client against a real server (the table that rises at dawn
> had no chips; the action counter read 5 of 4; a fanfare played under "the day hangs"). An in-process check
> reads the pool; the client reads the response. A staged scene is fought through the executor; the game's own
> road may carry another payload.

**FIRST — in this order:**

0. `git log`: BA-3's commit is the one after `da68ad7f`; the tree should be clean. **BA-3's one review is
   done** (§15.18: six readers on a frozen copy, before the commit; twenty-five findings; thirteen rows
   fixed in it, four filed for this session — scope 7c to 7f; the pins are `tests/test_ba3_the_review.py`).
1. Then **BA-4: THE ROADS AND THE FOG**, opening in Plan Mode with a slice plan. Read first: `STATUS.md`
   ▶ NEXT UP, the spec's §15.13 to §15.18 (before the code), `SYSTEMS_REFERENCE.md` §219 to §221 (the rules
   and the traps).

**Scope** (every row is one seam or one line to reverse; the recommendations of §15.13 and of BA-2's hand-over
stand, and this session's plan gate may still overrule any of them):

1. **BA2-X2 (P1) — a court's turn lost to a corps raised again mid-phase.** `backend/ai/enemy_ai.py`: the
   fairness tally (`actions_used[selected_marshal.name] += 1`) takes a corps that was not on the phase's
   opening roster. Seed jena, Prussia, Yorck. Done when the keyed probe's jena arm runs its 40 turns with no
   court's turn lost; the jena world-line moves from that turn — report it. The strict-xfail pin and the plain
   pin on the literal are in `tests/test_ba2_the_walls_and_the_guns.py`.
2. **BA2-X7 (P2) — the muster promises what a support order does not deliver**, WITH **the support order's
   approach rule — IN** and **BA2-X10** (a road round keeps to provinces the corps may enter; where none goes
   round, the order ends at the approach and says so): one change to the SUPPORT order's first step
   (`_handle_first_step_blocked`, `_strategic_first_step`), two seams. BA-3's "a corps is brought up" chip is a
   bring row — it inherits whatever this fixes.
3. **BA2-X12 (P3)** — no bombardment's collateral names its own battery on any road.
4. **BA2-X20 (P2) — a battle lights its field for those who fought in it**, with the Gazette's news of a great
   foreign battle (who fought, where, who held the field, no figures). Behind a seam, an arm of the measure:
   the commanded arms play France by what France sees, so the band may move — report it per seed.
5. **BA2-X21 (P3)** — a quote names the men its first march costs (`march_cost` on the march, support, follow,
   pursue and move-to quotes; the bring rows and BA-3's day chips inherit it). It moves no number.
6. **§15.5.7's two rules**, each behind a function seam: a pursuit ability fires for any corps of the victor
   that FOUGHT on the field (the head's second question — yes); the last hour's three quarters.
7. **BA3-X2 (P3)** — at text size 1.3 BA-2's board lays three corps a side as the file where its claim asks
   the wedge (`battle_acts.gd`'s seat layout; reproduce:
   `tools/ba1_acts_walk.py --only ulm_full,the_reserve --headless --time-scale 8 --text-size 1.3`).
7b. **BA3-X5 (P3) — a quote says a word's price.** While a day is open the surfaces outside the day's own
   chips still price a word as "1 action" (the attack card, the plan's `bring` rows, the relay's note,
   the province's ordinary attack row, the readback); the order then takes a point and no action. ONE
   source: where `battle_day.classify_word` would take the quoted order, the quote says `ap: 0` and the
   price in the day's points; the province panel drops the ordinary attack row for the day's enemy. It
   sits with BA2-X7 and BA2-X21 (the other quote rows). Done when the chip census's oracle (send, then
   read the pool) holds with a day open and CRT-11's relay pins run with the day's seam up again; the
   strict-xfail pin is `tests/test_ba3_the_rounds.py::TestAQuoteSaysAWordsPrice`.
7c. **BA3-X13 (P3) — a day that died before night bars no strike.** `battle_day.night_falls` writes the
   pair's bar for every day open when the night began, also one already over because its lead marched off:
   walking away buys a phase in which that corps cannot be struck by him. Bar only a day that was alive
   when its night began. Behind a seam, an arm of the measure.
7d. **BA3-X14 (P3) — his word leaves the phase's stream where it was.** `EnemyAI._execute_action` scores
   every order it runs with a draw from the court's `ai_rng` — the phase's stream, which no save carries —
   so a word of his shifts his phase, and a save and a load after it replay the phase otherwise. Score a
   day's word from the day's own stream (or without a draw). Behind a seam, an arm of the measure: it
   changes every campaign in which he speaks before his phase, so THE SWEEP OF §15.16 IS READ AGAIN WITH
   IT (`tools/_ba3_measure.py`, the sweep's own command) and its rule checked again.
7e. **BA3-X15 (P3) — a lead holds one day at a time: a rule for the plan gate.** Two corps of his can each
   fight one lead of ours to a hanging great battle in one phase: two days, one lead, whose `digs in` is
   one order (since BA3-X11 it binds to the first day that can take it — never an action, but perhaps not
   the day whose chip was pressed). BA-3's recommendation: a second great battle against a lead whose day
   is open opens no day of its own and is told as the one clash it is. The alternative: one word answers
   every day of his at once. Put both to the user; build the one chosen behind a seam.
7f. **BA3-X16 (P3) — two stance orders draw their own moods.** WS-16's stream is keyed on the order's
   `target`; a stance order carries `target_stance` (`executor.py`'s mood, `severity.py`). Add the order's
   own distinguishing field, and sweep for the class. Behind a seam, an arm of the measure.
8. **ONE measure with arms**, reported per seed: arm 0 = every seam at HEAD's answer (the keyed probe
   IDENTICAL on jena and marengo, the standing series unmoved, the commanded band = 28 / 27 / 27, BA-3's
   record `tools/_ba3_sweep_2026_11_15.json` arm `S`); then BA2-X2's fix; then X12, X10 with the approach
   rule, X20, each behind its seam; then the two ticked rules; then BA3-X13, BA3-X16 and — last, with the
   whole sweep — BA3-X14. `tools/_ba3_measure.py` is the pattern; the day's arms are run again where a row
   moves a day (BA3-X13, X14 and X15 do).

**Named test** (Golden Rule 9): `tests/test_ba4_the_roads_and_the_fog.py` (the spec's §15.7 says what it
holds). The strict-xfail pins of the six BA2 rows are in `tests/test_ba2_the_walls_and_the_guns.py` and
`tests/test_ba2_the_review.py`: each turns red the day its row lands and is then made a plain test.

**Verification, as BA-3 learned it** (§15.17, `SYSTEMS_REFERENCE.md` §221.9): play each rule by hand through
the server; then PRESS every new or changed control in the real client against a real server
(`tools/ba3_mode_c_walk.py` is the pattern — three boards, `--export`) BEFORE the walk of record; read any
new figure off the RESPONSE, not the world; look at the frames yourself; then, once, with every hashed source
frozen: the parse harness, the staged payloads, the windowed walk of record, the live walks, the captures at
the five sizes and the four instruments; then ONE full-suite run. **And from BA-3's review (§15.18):** a
client fix is not verified by the parse check — its own first cut failed at run time on
`bool(<Dictionary>)`, which parses — so every client fix gets a live step that FAILED before it; a "same
save, same answer" pin needs ambient streams that disagree and a twin that proves it can fail; a review
before the commit works on a frozen copy rebuilt from a bundle outside the repository (the readers never
see the checkout), and a reader's finding in the client is pressed before it is believed — one read as a
delay was a table that never came.

**To put to the user at the plan gate — recommended by BA-3, not built, none blocks:**

- **A first-open line for the day's panel** — the game's own rule (S14d, `first_open.py`: an action screen
  names its mechanic the first time it opens) has ten screens and the day's panel is not one. Drafted: "The
  day hangs, Sire: each side holds points for the rest of it. A word costs points, never an action; he answers
  each in turn. Two silences, or both purses spent, and night falls." The table's blank band above the stage
  takes one line.
- **Digits for the day's chips** (1–9, as the selection card has): the chips are mouse-only today, so Esc,
  Enter and Space keep their meaning. Who owns the bare digits is WS-10's ruling (Session H's head).
- **A line in the morning's telling for a night that fell with no clash** — the end-turn gate says it
  beforehand; nothing says it afterwards. BA2-X20's Gazette news is its natural home.
- **One name for a day of battle** in the record, its clashes told as its phases. Today each later clash is
  a battle of its own on the plate and in the log ("The Great Second Battle of Swabia"), as any second
  attack in a turn has always been named. Recommended: yes, with BA2-X20's news (both are how the record
  tells a battle); a change to the telling, meant to move no number — the plan gate reads what else keys
  on a battle's name first.
- **The key bar** — at 50,000 men the three commanded campaigns open twelve days against seven
  (`battle_day.key_bar`, one function). Recommended: it stands at 80,000 — the game's own bar for a great
  battle, and the days stay rare as the user asked; the user's own play is the reading.
- **Weighed and not built** (§15.14): ordinary battles settled by the marshals' own tempers; courts spending
  points against each other; stopping the enemy's phase to ask; a standing instruction per corps.

**Open with the user from BA-3** (none blocks BA-4; §15.17 "Left with the user", each one line to reverse):
he draws off only when the last clash went against him on points, and only by a road to his rear (never onto
the soil of a court he is at war with); a purse spent is not a wall (a further attack is an ordinary order
again at its ordinary price); the field is where the last clash was fought; the Guard is any sovereign's
renewed assault and nothing else, and with one point left the sovereign's attack is an ordinary order without
the Guard's numbers; the table goes on to his clash by itself after 2.5 seconds; the end-turn gate stops once
for a day that awaits your word; a day's later clashes are battles of their own in the record (the
recommendation above would change it); the deploy gate's reading (the commanded arms as run, silent on a
day).

**BA-3's traps (fresh; `SYSTEMS_REFERENCE.md` §221.9 has them in full):** a day exists only in a campaign the
game server holds — a `WorldState()` or a harness world has none, so a test must go through `TestClient`
(`tests/test_ba3_the_rounds.py::Table`) or call `campaign_variance.serve_campaign(world)`; a served TestClient
board is bare Europe (Rhineland beside Lorraine), a `WorldState()` the legacy map (Belgium beside Waterloo);
every seam is a zero-argument function read through its module (`--seam
backend.game_logic.battle_day:points_high=2`); a word is LENT its actions (`battle_day.lending`) and the
temper's stream subtracts the lend, so a chip's counsel is the temper the word meets — never read
`actions_remaining` inside a word's run without `campaign_variance.lent_now()`, and any figure the executor
writes onto a result inside the lend must be rewritten in `battle_day.settle` (`action_summary` was not: the
HUD read 5 of 4); a clash won on points carries the attacker INTO the field's province, so the day re-reads
both grounds at every clash; a deciding clash closes the day before its word's order returns; the tableau the
enemy phase carries is the table the client raises by itself, so it must read the day at DAWN
(`dawn_on_the_tableaux`), and a night's close is written on his last clash's tableau; a pin that fights the 1805 opening through the server on the `historical` seed is flaky beside the day (unseeded battle dice: Ulm's day hangs on some runs) — seed it, or hold `the_day_has_points` down with the reason; a stage that places
corps by hand must read the fog again (`world.calculate_visibility()`); `WorldState.to_dict` stands at 497 of
500 lines, `turn_manager.end_turn` at 499, `meta_executor.handle_objection_response` at 500 — fold, do not add
lines; `AttackContext` takes no new field; the host `battle_diorama.gd` keeps its pinned bodies and exactly
five `_acts.` hooks; `CLAUDE.md` stands a few bytes under its cap; the driver's `rounds` policy key is ABSENT
unless passed (`POLICY_DEFAULTS` is pinned); a tool that prints a scene's line must set its output's encoding
(the stager died on "−" when redirected); foreground `sleep` is blocked in this harness — run long jobs in the
background and wait for the notice; a Bash heredoc eats backslashes and chokes on `'''` — write every patch
script with the Write tool.

**The standing rules** (unchanged): commit on master through the pre-commit hook only when the user asks;
never `--no-verify`; no branches, no worktrees, no stash; nothing pushed unless asked; no player-facing cut or
deferral without the user's word; the model never moves a number; subagents run on Sonnet or Haiku; play
every new rule out before the long measure; one commit and one review a session. If it will not fit, stop and
say what is built and what is not.

---

## After row BA — Session H: S15 the deploy (the prompt as it stood on November 13–14, 2026)

> Two things changed since it was written: **WS-11 is closed** (row BA's BA-1) and **WS-16 is BA-3's**, so the
> weak-spot review brings SIX rows to Session H's head, not seven; and **BA1-X4** and **BA1-X8** join that head,
> with **BA2-X6** (row BA's BA-2: the province panel, scrolled, on a cut line) and **BA2-X16** (its review: the
> four older live-client walk tools and the mutation sweep's missing lock).
>
> The hand-over before row BA: **November 13, 2026 — SESSION UI-6 ✅ LANDED: THE
> LAST READING** (`UI_VISUAL_FOUNDATION_SPEC.md` §14; `SYSTEMS_REFERENCE.md` §217; `BUG_FIXES.md` §UI6;
> `tests/test_ui6_*.py`, `tests/test_parse_preview*.py`). The user's "this is last scoring make all deicisons and fix
> this, while at it please analyze if there are better ways to interact with gernals as well and to make typing
> clicking etc cleaner": every decision ruled (UI-5's eighteen kept, N1–N12 new); the generals rebuilt for play (the
> selection card with seven fixed slots and digits 1–7, right-click orders, the next idle marshal after an order, the
> marshal row, the Generals screen as roster + detail with its orders pinned); typing (the readback line,
> `GET /parse_preview`, never executed; the history's offers on today's board); the fog ruled by the recorded doctrine
> (name and side public, place secret) with every position leak in the live order road fixed (four compound-subject rows left open, at session H's head — (0) below); the crash the measure
> found (a scroll flipping its bar forever in one frame — every ScrollContainer keeps its gutter); blind readers
> 7 / 7 / 7, the mean of the marks 7.07 → 7.43 (every UI-5 six now 7 or 8 but the war room at 2.0). **Session H's walk now includes the user's own look at UI-6:** the frames in `docs/audits/ui_gilt6/`,
> the live walk's in `docs/audits/ui6_mode_c_2026_11_13/`; each decision one switch or one line; the levers the final
> readers name (§14 "What holds it now"), the user's to rule.
>
> The sessions before it: **Session UI-5 (November 13) — the full measure** (§13; sound, pictures, Help & Keys,
> saves; 7 / 7 / 7, mean 7.07) and Sessions UI, UI-2, UI-3, UI-4 (November 11–12, the client's re-skin; §9–§12).
>
> The session before the UI sessions: **November 11, 2026 — SESSION G5 ✅ LANDED: A
> CLIENT RALLIES AGAINST THE HOUSE** (`DYNAMISM_SPEC.md` §7e the landing record, §2b session G5, §8 rows G5-*;
> `SYSTEMS_REFERENCE.md` §211; `tests/test_session_g5_a_client_rallies.py`; ONE sweep with three arms 0 / RALLY /
> ALL on three surfaces, the series re-read). The user's "do what you deem best then tell me what next", to
> session G4's five readings: the commission ceiling, the band and Italy's numbers STAND; the neutral client is
> re-cut — where her lord already fights the aggressor's house a client takes up his war with it and marches on
> its client (`diplomacy.a_client_rallies_against_the_house`), staying out only where her lord is at peace with
> that house; and the sweep's catch — the gate's annexation read counts a house's AUTHORED aims though it stands
> under the survival override (`war_council.the_gate_reads_the_authored_aims`; marengo read 2 on the voice, 0 as
> authored). **Measured:** arm 0 == session G4 byte for byte on both surfaces; the rally moves six ambient seeds
> and the harness's lodi; classes 10 of 10; **the promotion clause MET on TWO seeds again (lodi 33, marengo
> 39)**; the roster in TWO readings (friedland's kingdom falls again); annexations 0 on both surfaces; **the band
> 26 / 26 / 25**; the series unmoved.
>
> The session before it: **November 11, 2026 — SESSION G4 ✅ LANDED: THE
> OPEN READINGS, RULED AND BUILT** (`DYNAMISM_SPEC.md` §7d the landing record, §2b session G4, §8 rows G4-*;
> `SYSTEMS_REFERENCE.md` §210; `tests/test_session_g4_the_open_readings.py`; ONE sweep with eleven arms 0 / FORM /
> WON / LAPSE / REAR / CEILING / ALLY / GUNS / WAGON / HOUSE / ALL on three surfaces, the series re-read; drafted in
> Plan Mode and approved). The user's "evaluate options choose the best", then "and decide and do these":
> fourteen rulings — a nation proclaimed on what it HOLDS at its authored bar (`forms.at`, Italy 3 of 5;
> `forms.first`, Rome then Naples; `formations.backfill_forms` at load); an ally's soil is not won; a pact lapses
> at the vassalage; a backer is no menace; the people drive out a foreign king (and a king named in the treaty is
> seated though his laurels fade); a commission reads the arming ceiling; the Emperor's ally takes no separate
> peace while it wins; no guns from a sanctuary; a bandwagoner joins a neighbour's war; a client joins no war
> against a client of a house it is at peace with (the DD-1 fuzzer's catch); the dispatch drops an overtaken
> capture; the crown row leads the demands; no "§" in the chip. **Measured:** arm 0 == session G3 byte for byte
> on both surfaces; six rules move no ambient seed; classes 10 of 10 on every arm; **the promotion clause MET on
> ONE seed (lodi 33 — marengo's turn-40 crown falls out of the window on CEILING's arm)**; the roster in THREE
> readings; annexations 0 on both surfaces; **the band 26 / 26 / 25** (28 / 27 / 25 before ALLY and GUNS); the
> series unmoved.
>
> Before that: **November 11, 2026 — SESSION G3 ✅ LANDED: A
> CLIENT SWEARS NO PACT OF ITS OWN** (`DYNAMISM_SPEC.md` §7c the landing record, §2b session G3, §8 row G3-CLIENT;
> `SYSTEMS_REFERENCE.md` §209; `tests/test_session_g3_a_client_swears_no_pact.py`; ONE sweep with two arms 0 /
> CLIENT on three surfaces, the series re-read; drafted in Plan Mode and approved). The user's "Rule on clients
> first", then "make best cal for game": **a client's foreign policy is its lord's** — no defensive alliance and no
> alliance is proposed to or from a court that answers to a lord (`ai_diplomacy.a_client_swears_no_pact_of_its_own`;
> `client_in_the_pair` the one read, at the poll's gate and the recipient-addressed road's guard, `reason: client`;
> every lord's clients alike; a non-aggression pact, open borders, the player's own proposals and a standing pact
> untouched); the Vassals card says it (`diplomatic_ledger.CLIENT_POLICY_LINE`). **Measured:** arm 0 == session G2
> byte for byte on both surfaces; ambient no seed moves; **the AI-France harness's annexation line 4 → 0** (the
> Kingdom of Italy is never called into Naples' Roman war; client pacts 19 → 0); the band 28 / 27 / 25; the series
> unmoved (735 bites on the rig); every gate clause as session G2 left it. **Reported:** a freed Kingdom of Italy no
> longer proclaims Italy on the pacts it signed as a client (four harness seeds → none) — put to the user, with
> two smaller readings (a pact brought into a vassalage; a client's non-aggression pacts).
>
> The session before it: **November 11, 2026 — SESSION G2 ✅ LANDED: THE
> PLAYED CAMPAIGN** (`DYNAMISM_SPEC.md` §7b the landing record, §2b session G2, §8 rows G2-*; `SYSTEMS_REFERENCE.md`
> §208; `tests/test_session_g2_the_played_campaign.py`; ONE sweep with four arms 0 / ASK / LADDER / ALL on three
> surfaces, the series re-read; drafted in Plan Mode and approved). A France was played by hand on a fresh seed and
> five defects were fixed at the cause: the king survives the separate peace (`_pair_substitute_seed_terms` carries
> `crowns.CROWN_CLAUSE_KEYS`); the war names the beaten (`crowns.the_war_names_the_beaten` — the pair's score, then
> the burden; the ceding court recognizes the crown it signs); a court at `fight` still asks
> (`ai_diplomacy.a_court_at_fight_still_asks`); the ladder outlasts the rest
> (`ai_diplomacy.the_ladder_outlasts_the_rest`, 24 turns); a backed design dares (`intent.a_backed_design_dares`,
> +10 — the one new mechanic). The marshals' side told (the pick's price, the Generals screen's REIGNING block, the
> rebel king named); the crown row's name opens the king list. **The gate on the shipped tree:** classes 10 of 10;
> Hesse promoted on lodi (33) and marengo (40); the roster {Kingdom of Italy, Papal States} on jena and wagram;
> `annexations_outside_aim` 0 AMBIENT; the band 28 / 27 / 25; the series unmoved. **CORRECTED:** the AI-France
> harness reads 4 provinces kept outside aim (jena and wagram — the cast Naples keeps Milan and Piedmont, the soil of
> the player's own erased client; session G's tree read 2 and its record said 0) — pinned at what it reads, the
> cure the user's ruling on his own clients and "sign at the last" (never a silent 0).
>
> The session before it: **November 11, 2026 — SESSION G ✅ LANDED: THE GATE
> EARNED** (`DYNAMISM_SPEC.md` §7a the landing record, §7 the gate's reading, §2b session G, §8 rows G-PACT / G-CHEST;
> `SYSTEMS_REFERENCE.md` §207; `tests/test_session_g_the_gate_earned.py`, 19 pins; the seams G-PACT / G-CHEST in
> `tests/_t3_seams.py`; ONE sweep with three arms (0 / PACT / ALL) on three surfaces, the series re-read, ONE commit;
> drafted in Plan Mode and approved). The user's word at session F's close: **"Earn them first."**
> **As built:** **no pact with the coveted** (`ai_diplomacy.no_pact_with_the_coveted`; `pact_with_the_coveted` the one
> read; `_evaluate_ai_ai_proposal` wraps `_evaluate_ai_ai_triggers`, `_resolve_ai_ai_proposal` refuses with `reason:
> covets`) — the defect that defused the cast Naples' Roman Expedition at turn 3 (jena, wagram) and Hesse's Westphalian
> Duchy at turn 16 (marengo): an AI court allied the very court whose province it coveted and the ally clause read the
> want as "won". **A crown is bought with the whole chest** (`reforms.a_crown_is_bought_with_the_whole_chest`;
> `_purse_bar` returns the price for `is_promotion` rows; every other law keeps the reserve).
> **The measure (`tools/_gate_measure.py`, `_gate_series_arms.py`; the pins `TestTheSessionGMeasure`):** arm 0
> reproduces session F byte for byte on both surfaces; PACT alone moves jena / lodi / marengo / wagram and earns both
> clauses — **lodi: Hesse's Grand Ducal Title at 33** (Westphalia 25, the aim peace 26); **wagram: the Papal States
> erased at 31** by the cast Naples (the crisis 27, the declaration 29, Rome stormed 30–31), then her war runs on to
> Sardinia and Austria; marengo: Hesse holds Westphalia from 25 under the old bar; jena: Austria's pact with the Pope at
> 23 deters Naples. ALL adds **marengo's crown at 40**. Classes 10 of 10 on every arm; the band 28 / 27 / 26 → **28 /
> 27 / 25**; the harness moves six seeds, promotes nobody; the series unmoved (the pact seam biting 105 times on the rig).
> **THE DEPLOY GATE READS MET IN FULL (§7): classes 10 ≥ 6; a minor at secondary rank by promotion on two seeds; the
> roster in two readings; `annexations_outside_aim` 0 on the ambient record (the harness read 2 — corrected by
> session G2, above); the band inside 23–28; 0 open GR rows.**
>
> **What session G leaves with the user (none blocks the deploy):** (a) **the understudy's reach** — a Naples at war
> with Austria has no authored aim against her, so the conduct rule leaves her free to plunder Piedmont, Lyonnais and
> Limousin from Austria's hands (`captures_outside_aim` 251 → 269): a reading on a court at war without an aim;
> (b) **the chest's number** — the price alone (built), or a half-reserve; (c) **the commanded middle arm** 26 → 25;
> (d) **jena's Pope under Vienna's wing** — the deterrence working, or an understudy's ask-ladder one refusal short
> (`REFUSAL_MEMORY_TURNS`); (e) session F's three, session E's four, session D's three and session C's five stand.

**THEN — SESSION H (`DYNAMISM_SPEC.md` §2b): S15 THE DEPLOY — the user's own walk.** The order: **(0) Session UI-6's
four open rows** (and one note from BA-3's review, not a row: the enemy phase's filter blanks the structured
origin of a march seen to arrive (PT-E5) but leaves the action's `message` string — "… moves from Hungary
to Bohemia" — on the wire; the client never prints it; decide whether the wire should carry it)
(`BUG_FIXES.md` §UI6 — UI6-X70, X73, X74, X75: a report subject naming a friend or a title, a third
clause after an arrival, a friend-only report subject, a title-first list; nothing spent wrongly by any): each is a
strict-xfail pin in `tests/test_ui6_fog_siblings.py` that turns red the day it lands — fix each at its cause, sweep
the class on both roads (`/command` and `GET /parse_preview`; rule 10), re-point the pin to the landing's words, and
the census reads 0 open defect rows before (1) — counting **the weak-spot review's six still open** (`BUG_FIXES.md` §WS, November 14, 2026: WS-10 and WS-12 are the user's rulings, put to them first — WS-11 was ruled and closed by row BA's BA-1, and WS-16 is BA-3's; WS-13, WS-14 and WS-15 fixed at their cause; WS-R's twelve finds each confirmed or refuted; pins in `tests/test_ws_weak_spot_review_2026_11_13.py`) and **BA1-X4** (`BUG_FIXES.md` §BA1: the tableau's lines at Text size 150 % and over; the strict-xfail pin `tests/test_ba1_the_battle_in_acts.py::TestBA1X4TheTableAtLargeType`); **(1) the gate
checks, each against its record file** (`PRE_DEPLOY_PLAN.md` §2 S15; `DYNAMISM_SPEC.md` §2 the S15 row, §7):
0 open GR rows (`.venv/Scripts/python.exe tools/defect_census.py --open`); story classes ≥ 6 — 10
(`_dy_signature_g5_2026_11_11.json`, session G5's shipped arm); a minor at secondary rank by promotion on ≥ 1 seed —
lodi 33 and marengo 39, TWO seeds (`_g5_census_2026_11_11.json` `rank_promotions`); the roster varying — two
readings: jena's and wagram's {Kingdom of Italy, Papal States}, {Kingdom of Italy} on eight (the signature's
`eliminations`); `annexations_outside_aim` 0 on the AMBIENT record (`_g5_census_2026_11_11.json` — by session G5's
corrected read; the old read counts 2 on marengo, `_g5_rally_census_2026_11_11.json`) and 0 on the AI-France
harness (`_g5_chain_d_2026_11_11.json` arm ALL), reported, never gated; the France band 23–28 — 26 / 26 / 25
(`_g5_band_2026_11_11.json`), **26 / 27 / 28 since row BA's BA-1 seeded the battle's dice
(`_ba1_band_2026_11_14.json`; read the band against the latest row-BA record — BA-3 will re-read it)**;
the historian test green on every seed (the suite's pins); the ratchet (`tests/test_code_health_ratchet.py`); the
parse harness green; **(2) the build** — `deploy\build.bat`, UNSIGNED until the certificate arrives
(`SYSTEMS_REFERENCE.md` §153.3–§153.4, `UX_UI_REVIEW_PLAN.md` §UXR-4: nothing on this machine — no signtool, no
certificate in either store; the day it arrives, `INK_IRON_SIGNTOOL_ARGS` / `SIGNTOOL` and the same script);
**(3) the clean-environment run** (a fresh clone, the venv from `requirements`, the hook installed with `Copy-Item
scripts/git-hooks/pre-commit .git/hooks/pre-commit`, the backend as `-m backend.main`, the client from the export, one
forty-turn Mode C walk by the user — `docs/PLAYTESTING.md`; the walk is also the user's first look at row BA's battle table in motion (the readers' blind marks were not taken for it: his look is the reading) and at Session
UI's new skin — the gilt frame, the desk, the books as cards, End Turn gilt on a spent day — its before / after pairs
in `docs/audits/ui_gilt/`, its reversals one line each, `UI_VISUAL_FOUNDATION_SPEC.md` §9); **(4) the release record** (the commit SHA, the gate's
readings with their record files, the certificate's state, the user's walk's notes — `SYSTEMS_REFERENCE.md` §211,
`STATUS.md`). **After the deploy** (`PRE_DEPLOY_PLAN.md` §2; no cuts without consent, spec §0): S14k-3 (Spain alone),
S16, S17c.

**The commit:** session H's commits are the user's walk's — the release record and any gate fix each its own commit
through the hook (about 10 minutes; never `--no-verify`); push only on the user's word.

**Session G5's own traps (fresh):** a gate number that moves is READ TO ITS CAUSE before it is believed — replay
both arms and put the read's inputs side by side (marengo's 2 was the instrument: a court under the survival
override has no design voice, so `_house_aims` read empty; `authored=True` is the deck as written); the three-arm
sweep on three surfaces takes about seven minutes — re-run it WHOLE on the final tree; a rule that removes a war
pair to keep an invariant has a sibling that completes the war instead — play the real road
(`vassal._client_takes_the_field`) before choosing; session G4's own neutral-client pin holds G5-RALLY down; an
ally's branch of the cascade is untouched (the fuzzer exempts a bought client's pairs — it leads its own war);
`( cmd & )` in a shell loop is not waited on by `wait`; STATUS holds 7 "▶ ▶ ▶" entries (session D archived).

**Session G4's own traps (fresh):** PLAY THE RULES OUT BEFORE THE SWEEP — three restarts here, each for a
fix the played checks found mid-measure (a freed Italy aimed at France, not Rome; a king's laurels fading before
ratification; the fuzzer's latent I2); the deck rides the save — a new authored key on an existing deck entry
needs `formations.backfill_forms` (entries are never added: the AI-0d precedent stands for goals), and only the
client walk on an OLD save shows it; an acquire design's obstacle is the FIRST unmet target in its order
(`forms.first` leads it for a forming design); `_court_demand_suggestions` sits at exactly 500 lines — wrap at
its call; a rebelling client still carries its lord's row while the war cascade runs; the treaty fuzzer's ledger
is a zero ratchet and a shifted world-line can reach a latent class — bisect by holding each seam down
(`treaty_fuzzer.run_seed`); the glob `_dy_signature_g4_*_2026_11_11.json` does not match the shipped arm's
record; T2-3's, T3-4's and T3-5's own stagings hold G4-WAGON / G4-ALLY down by autouse fixtures; CLAUDE.md is
patched on bytes under its script's 62,000 assert; STATUS holds 7 "▶ ▶ ▶" entries (session C archived).

**Session G3's own traps (fresh):** the AMBIENT surface cannot see a client rule — the idle France's kingdom is
gone by turn 23 on every seed; the harness and a commanded France are its surfaces; the harness's France refuses
every petition and loses its clients (`final.vassals` is empty on most seeds) — read a client's story off the events
(`vassal_broke_free`, `vassal_defected` with `outcome: free_*` or `transfer`, `vassal_transferred`); a harness
`formations` entry is a proclamation a freed client can reach through the ally clause (`agendas.region_coveted`
reads a target in an ally's bloc as met) — read the design's list before believing it gathered anything;
`_UPGRADE_ORDER` starts at WAR and the first step above PEACE is OPEN_BORDERS; `tools/dd_b_play.py` loads a save
copied into `<run>/saves/` before `start` ("Load a Campaign…" lists it); CLAUDE.md is patched on bytes and held
under 62,000 LF bytes by its own script's assert; STATUS holds 7 "▶ ▶ ▶" entries (session B archived); **stopping a
background commit orphans the hook** — git dies, `sh .git/hooks/pre-commit`, the pytest controller, its workers and
any headless engine run on (27 processes): find them by `ParentProcessId` from the hook's `sh` and stop the tree
before committing again, or let the commit finish; `test_ep_f4`'s `_decisive_win` rolls on `DECISIVE_ROLL` since
this session (unseeded, seed 261 left 69 of Mack's 900 to escape and failed the hook's first run).

**Session G's own traps (fresh):** the AI–AI poll's body is `_evaluate_ai_ai_triggers` — a gate on its outcomes wraps
it, never sits inside it (0a's alignment arm must still exclude the obstacle, the design ask must still pass);
`get_agenda_covets` already excludes an ALLY's soil, so `pact_with_the_coveted` reads the live deck and never undoes a
pact already standing; a `crisis_passed` with `cause: satisfied` after a treaty is the ally clause speaking — check
the pair's state before believing the want was won; `spawn_run(seed, 10000, 40)` from `tools.ai_v_sweep` gives a
seed's whole story in five seconds — the digest's `intents` (per court: design, against, weight, rung) and
`wars_opened` rows are the diagnosis; the census's `signed_cessions` consequence lines carry the indemnity ("Hanover
pays 243 gold"); `test_sf_lb2`'s caller census names the poll's body by function name; the Awakening's beats move
when a people's court is erased (the Pope's gone with Rome); CLAUDE.md sat at 61,988 LF bytes after this session's
trims (12 bytes of headroom — the next row trims first); STATUS holds 7 "▶ ▶ ▶" entries (session A archived).

**Session F's own traps (fresh):** a `gold` clause prices ZERO burden — the dialect's names are `gold_lump` (bilateral)
and `gold_indemnity` (settlement), `territory_cede` with `regions`; Russia's seat on the drawn map is **Vilna** (the
Alarm's `_seat` → `seat_as_metonym`), never St Petersburg; a vassal pair trades nothing (`calculate_trade_breakdown`
skips it) — a client-side trade price is an empty set; `filter_campaign_log` sits at EXACTLY 500 lines — a new
court-knowledge type joins `levee`'s line, never its own; `calculate_acceptance` is already 630+ lines (counted among
the 28); the Net components have a cross-file tripwire (`test_economy_ledger_reconciliation.EXPECTED_NET_SIGNS`) and
the scorer's components three set pins (`test_ca8_gate_closeout`, `test_common_peace_acceptance`,
`test_settlement_guided_terms_slice3`); the census pins are SEVENTEEN now (the sixteen `== N  # …` lines plus
`test_dy5`'s bare one) and `test_iq7`'s unexplained check names every slice tag; the carved people's scalar lives under
the vassal row's `carved_from`; the Neapolitans are already stirred by the carve (`AW.move` adds to a live row); a
Python patch script that inserts after an anchor is NOT idempotent when the new text begins with the anchor — guard
with `if new in text`; the Godot parse report regenerates with `Start-Process … --headless --quit --path
godot-client/project-sovereign --script ../../tools/godot_parse_check.gd` AFTER the `.gd` edits (exit 0, 13 KB).

**Session E's own traps (fresh):** the guided rows hang on `per_court_acceptance[]` (the confirm popup's
`_per_court_row`), each court's `demand_suggestions[]` — not on a `per_court_rows` key; `_demand_clause_label` is
the table's clause-words function in `settlement_actions`; `world._starting_controllers` is the Europe map's
starting-controller read (`get_starting_controllers()` bare is the legacy world's); a peace treaty has its OWN
trust reactions (Soult −5 on the Naples peace) — a trust pin reads against a control carve of the same board; the
threat slot caps at 100 (`min(100, before + 12)`); `display_nation` does not know a formed name — use
`formations.formed_display_name`; `formable_nations` templates are validated in the `validate_scenario` loop
(`_validate_crown_block` beside the `seeds` check), the top-level block in `_validate_crowns`; a new heraldry SVG
needs its `.svg.import` sidecar — a headless `--import` pass writes it (`Start-Process … --headless --import --path
godot-client/project-sovereign`), then `git add -f` both (the ignored `assets/`) and a line in
`THIRD_PARTY_LICENSES.md`; the parse report regenerates with `--script ../../tools/godot_parse_check.gd` AFTER the
`.gd` edits; the gift's two pins (`test_dy2` `TestTheEmperorsGift`) hold `a_victor_erects_a_crown` down — their
board is the AI road's live case; `CARVE_TAGS` + `CROWN_TAGS` in `test_nation_agendas_formables` (the catalogue
census 10, the Formables page 12); the jealousy council's stash is `world._pending_jealousy_turn_events`; the
seam-down strike keys on `crown.since == "DY-6"` (an older template keeps its place, its block struck); a
measure's four arms with ten harness seeds each ran 28 minutes alone, the series 3 beside it.

**Session D's, C's, B's, A's and the earlier traps:** unchanged from the prior prompts — read them in the archive's
copies (`git show 90bada87:docs/NEXT_SESSION_PROMPT.md` for session D's, `git show 2589f3c1:docs/NEXT_SESSION_PROMPT.md`
for session C's, `git show 93f82fb2:docs/NEXT_SESSION_PROMPT.md` for the earlier), every one still binding.

**Open with the user beyond session H's head (none blocks the deploy):** session G5's readings
(`DYNAMISM_SPEC.md` §7e — Switzerland bought on six unattended seeds; friedland's kingdom falls again; the gate's
read corrected in the session that tripped it; the ally's branch); session G4's five are RULED (§7e), session
G3's three and session G2's list are RULED (§7d); session G's four
readings above; session F's three levers (`DYNAMISM_SPEC.md` §6c); session E's four readings (`DYNAMISM_SPEC.md` §6b); session D's three
(the letter's floor; the levée's reach; the dial's ambient road); session C's five (the march does not visibly bleed
— the ulcer's teeth; the letters' seat at the desk; the bands' pace; the raised gate's clauses 2 and 3; the pacing
record's drift); session B's three (the envy's cap at the coerce floor too; the crowns after the gift; no second
great-power war on the 1805 board — the content levers); GRD-38; GRD-37; the design rows of `DESIGN_REFINEMENT.md`
§GRD; the flip's two readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18);
the road record's readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions (`REFORMS_SPEC.md` §5a);
the crown term's level; SF-NAV-1-D1; Britain's letter without contact; the hook's remaining levers; the two
hash-seed orderings with no reader yet checked. (`test_ep_f4`'s flake is CLOSED — session G3's hook caught it and
its helper now rolls on a fixed seed.)

**After session H — the session plan (`docs/DYNAMISM_SPEC.md` §2b; no cuts without consent, spec §0):** the deploy
is the last session of the plan. **After the deploy:** S14k-3 (Spain alone), S16, S17c (`PRE_DEPLOY_PLAN.md` §2).

**Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231
(seams are named functions, zero-arg, in the module they gate), functions over 500 lines 28 of 28,
`WorldState.to_dict` 497 of 500 (every new field in an existing store), CLAUDE.md within 62,000 LF bytes
(27 bytes of headroom after session E's `crowns.py` row — the next row trims first), STATUS at most 7 "▶ ▶ ▶"
entries (archive the oldest to the top of `docs/archive/STATUS_2026_Q4.md` — session E archived THE LEDGER);
every `except Exception` must speak; a measure chain runs ALONE and no backend, test or deck edit lands while it
runs; **a sweep or driver PARENT runs PLAIN, never `-X utf8`**; **never pipe a measure's output through `tail`
into the task file**; a probe itself runs under `python -X utf8` when IT prints; the recorded boards' hold-list is
`tests/_oct27_seams.py` (it folds `tests/_t3_seams.py`'s rows — a new seam goes THERE); **a record superseded but
still pinned is KEPT under a dated or named file and its pins re-pointed**; the rig-record pins in
`test_ai_drill_fix_2026_09_27.py` re-link through `SERIES_BEFORE_*` constants when the live constant moves on; the
bytecode pins fail under the shell's `PYTHONDONTWRITEBYTECODE=1` (run pytest and the commit with `env -u
PYTHONDONTWRITEBYTECODE`); the driver reads `--seam`, never `INK_IRON_SEAMS`; every rig shim passes through `*a,
**k`; a rig re-run writes its OWN record (`--out`); the scenario and every asset sidecar sit under the ignored
`assets/` — `git add -f` them; the docs are CRLF or LF per file (STATUS, SYSTEMS_REFERENCE, MODDING_FORMAT, CLAUDE.md,
the archive CRLF — patched on bytes; DYNAMISM_SPEC, SAVE_FORMAT_REFERENCE and this prompt LF); the deck JSON files,
the scenario and the golden corpus are hand-formatted — insert text, never re-dump; the three decks are one deck,
in lockstep; commit with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the background (the
hook runs ruff and the full suite, about 8.5 minutes; never `--no-verify`) and read the log's EXIT line; a test
module that opens a Godot WINDOW or starts a sandboxed backend joins `ENGINE_LANES["engine"]`; a `.gd` edit with
the morning's parse report FAILS the hook (regenerate `tools/godot_parse_report.json`); `tools/playtest_runs/` is
gitignored; `get_visible_enemies` is the PLAYER's fog; a rung's structured field reaches the executor only
through `enemy_ai.execute_admin_phase`'s whitelist; an UNQUOTED Bash heredoc runs every backticked name in
its body as a command — write every script with the Write tool; the cheapest proof that a change moves
nothing is the keyed world probe (`to_dict` per turn, one hash per top-level key, against a `git archive
HEAD` copy, `PYTHONHASHSEED=0`).
