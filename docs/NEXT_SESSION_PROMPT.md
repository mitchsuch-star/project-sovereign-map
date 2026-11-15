# NEXT SESSION PROMPT — Row BA, BA-3: the rounds (before Session H, the deploy)

> Overwritten each time a session hands off. Current hand-over: **November 15, 2026 — ROW BA, BA-2 ✅ LANDED: THE
> BOARD, THE WALLS AND THE GUNS** (`BATTLE_DIORAMA_SPEC.md` §15.11 the session's gate — the user's words on battle
> agency, the measure behind them and seven decisions taken under delegation — and §15.12 the landing record;
> `SYSTEMS_REFERENCE.md` §220; `BUG_FIXES.md` §BA2; `tests/test_ba2_the_walls_and_the_guns.py`,
> `tests/test_ba2_backend_walls_guns_plan.py`). The user asked for battles like "watching an inetretsing
> strtagic battle with flanks and movements unfold but the player has abstrtact interactions think black and
> white", said "Plan on it", then "we dont ened to use emperor framing the concept is to make battles an enaging
> autobattler with abtract player feedback you are playing the emperor thew whole time" and "they should mvoe in
> napolenic stile". The concept as ruled: **the player sets the board; the battle plays itself, moving as armies
> of the period moved; between rounds the table offers abstract commands.** BA-2 built the first two: the order
> of battle (three seats a side — a lead and two wings — and a reserve), the movement (column into line, the
> charge and the recoil, the square, the flank's column, field works), a garrison assault's tableau (the wall
> held, stormed or capitulated), a bombardment's (the cannonade alone), the plan named in Act I, and the "bring
> him" chips at the attack row and on the attack card (the existing SUPPORT order at its own price). Seven finds:
> BA2-X1, X3, X4, X5 fixed; **BA2-X2 and BA2-X7 open, THIS session's** (a court's turn lost to a `KeyError` when a
> corps is raised mid-phase — seed jena, Prussia, Yorck; and Berthier's muster naming a written order for
> Bernadotte and for Murat on the opening battle, when the order marches the one out of reach and stops the
> other on his question); **BA2-X6 open at Session H's head** (the province panel, scrolled, can rest on a cut line).

**NOW — BA-3: THE ROUNDS** (`BATTLE_DIORAMA_SPEC.md` §15.11 "What BA-3 becomes", §15.5.6 as amended, §15.5.7,
§15.7). Open in Plan Mode with a slice plan. Read first: `STATUS.md` ▶ NEXT UP, the spec's §15.11 and §15.12
(before the code), `SYSTEMS_REFERENCE.md` §219 and §220 (the rules and the traps).

**Three questions go to the user at its head** (§15.7 — put content-first, co-equal, nothing pre-recommended in
the question itself; the answers below are the ones §15.11 recommends when asked):

1. **The round's price.** §15.11 decision 4: a round costs what an attack costs (priced rounds cannot be
   cheesed, so the hinge may be offered on any hanging day). The plan of record before it said no action; the
   design review flagged a near-free second attack after a narrow win.
2. Whether a pursuit by a commander who ARRIVED includes a corps already standing on the field (§15.5.7).
3. One round a lead a turn, or as many as the actions allow.

**Scope.**

1. **A battle the player fights is played in rounds.** When a day hangs (both leads standing, the enemy still
   on the field — 180 of 350 field battles on five measured seeds) the table stays up and offers, on the pieces
   themselves, the EXISTING orders at their ordinary prices: **Press** (the lead attacks again, with the penalty
   his second attack already carries), **Commit** (a chip per corps an order would still bring — the very rows
   BA-2's `order_quotes.bring_quotes` returns; the Guard when the Emperor's own corps is at hand, with the two
   morale numbers ruled for NP-D1: the enemy lead −10 as it goes in, every French corps that fought −10 if it
   is beaten), **Hold**. The lead answers through the objection road as it stands (the concern evaluators, the
   insist penalty and trust gain, the defiance chance, roll and fallback, "By my word", vindication). **No rule
   hangs on where the Napoleon piece stands** (§15.11 decision 1: the hand is in every battle the player fights).
2. **On defence:** nothing new resolves inside the enemy's phase (it cannot stop to ask). Once it has ended, a
   defended day that hung offers **Riposte** — the ordinary attack order at its ordinary price, free where the
   lead already holds a counter-punch (`attack_quote` quotes 0 when `has_counter_punch()`).
3. **NP-D1 closed** (the Guard's two numbers); **the two rules the user ticked** (§15.5.7: a pursuit ability
   fires for an arrived commander when the lead has none; an arrival won by 5 points or fewer brings three
   quarters of its weight) — each behind a FUNCTION seam (the ratchet caps module levers).
4. **WS-16** — the reload's other dice (the objection's mood, the defiance roll, the diplomatic defiance, four
   smaller sites): a round needs the defiance roll seeded.
5. **BA2-X7** — the muster's lever sentences (`combat_executor.muster_row_hint`, `_arrival_odds_row`) name an
   order only when sending it brings the corps: read from where the order's first march leaves him, as
   `order_quotes.bring_quotes` now is (`_stop_this_turn`, `_odds_under_the_order`). The Commit chips of
   scope 1 are these rows, so it lands with them (`_build_muster_preview` is 419 lines — a seam, not more
   body). **One rule goes to the user with it** (recommended in §15.12, not built): a SUPPORT order whose
   road's first province holds the very corps the friend is to attack halts at the approach and joins the
   next attack there — the arm the order already has when the foe holds the friend's own province — so a
   corps like Murat (road through Mack: today the order stops him on "Your orders?") can be committed at
   all. The strict-xfail pin
   `tests/test_ba2_the_walls_and_the_guns.py::TestBA2X7TheMusterPromisesWhatTheOrderDelivers` turns red then.
6. **BA2-X2** — the AI turn's fairness tally takes a corps that was not on the phase's opening roster
   (`enemy_ai.py`, `actions_used[selected_marshal.name] += 1`), behind a seam, with the sweep of every other
   per-marshal dict built from that roster; the strict-xfail pin
   `tests/test_ba2_the_walls_and_the_guns.py::TestBA2X2ACourtsTurnIsNotLost` turns red the day it lands.
7. **ONE measure with arms**, reported per seed: arm 0 = every seam at HEAD's answer, byte-identical on the
   standing series; then each rule; then BA2-X2's fix (the jena world-line moves from the turn Prussia's phase
   is no longer lost); then the rounds answered each way. The "seeded dice" arm calls
   `campaign_variance.serve_campaign` on the harness's own world. The commanded band's arm 0 is BA-1's shipped
   record (`tools/_ba1_band_2026_11_14.json`, arm ALL: 26 / 27 / 28).

**Named tests** (Golden Rule 9): `tests/test_ba3_the_rounds.py` (it supersedes §15.7's
`test_ba3_the_crisis.py`: the table offers a round only where the day hangs, each answer goes through the
objection road and the battle plays on, the pending slot round-trips and an old save reads empty, the Guard's
two morale numbers, the pursuer among the arrived, the last hour's three quarters, a corps raised mid-phase
takes its turn, the muster names the lever only for a corps the order brings) and
`tests/test_ws16_the_same_order_draws_the_same_temper.py`.

**How.** The rounds are orders the game already has: quote them with `order_quotes` (the chips' rows are
`bring_quotes`'), send them down the typed road, and let the next battle's tableau play — the table "stays up"
by offering the chips on the settled frame and raising the next tableau when the order's answer lands. New
beats in `battle_script.py` take one of the three fog cases before they are written (§219.2, and §220's table
for BA-2's). Client verbs go in `battle_acts.gd`; `battle_diorama.gd`'s pinned bodies stay untouched and its
four hooks stay four. New scenes in `tools/ba1_stage_battles.py`, new claims in `tools/ba1_acts_walk.py`, each
watched failing with its fix switched off (`tools/ba2_switch_off.py` is the pattern). Run the headless walk
(`--headless --time-scale 8`) until the claims hold; then, ONCE on the final tree, the windowed walk of record,
the IQ-10 captures and the four instruments at the five sizes, and the parse harness. ONE suite run before the
commit; commit on master through the hook only when the user asks; never `--no-verify`.

**Open with the user from BA-2** (none blocks BA-3; §15.12 "Left with the user"): three seats a side and a
reserve in every battle, the great ones included (the fallback — the wedge to three, the old file at four — is
one line); a garrison that yields is drawn fallen with CAPITULATED under it; a garrison under the collapse
line that gives way without a fight is a march in and has no tableau; a bombardment opens by itself when it
destroys its target or levels his works ("breaks" read as the works: guns never break a corps); the province
panel says the order once on the line ("Bring up to support Ney:") with each chip the man and the price, behind
one fold when several corps could lead, and the attack card prints the chip whole; a chip on the attack card
sends the order and closes the card; a chip stands only where its order brings the man (Bernadotte has none on
the opening battle); Berthier no longer speaks of an enemy battery's fire (BA2-X1). From BA-1,
as before: the plinth's name, a typed `historical` seed's re-rollable dice, Blücher's "Vorwärts!" in 1805.

**BA-2's own traps (fresh; §220.5 has them in full):** the tableau payload's `kind` says which table to lay —
a new kind needs its arm in the walk's kind-aware claims (a wall is not rolled for; guns throw no dice);
`_execute_bombardment` logs the very dict it returns as `events[0]` — a tableau goes on a COPY of the event or
every bombardment writes its picture into the campaign log and the save; four test files replace
`_execute_bombardment` with fixed-arity doubles — wrap its STANDALONE call sites, never its body, and never the
supporting salvo; `_resolve_garrison_combat` stands 16 lines under the 500-line ratchet (484) — wrap its returns; a
garrison under the collapse line gives way without a fight (a conquest event, no assault): stage a stormed
wall with 6,000 men, not 3,000; a bombardment's script is told WHOLE (the brief form keeps one head beat an
act, which would drop the works and a bystander); Berthier's bombardment line is PICKED before it is blanked —
skipping the pick moves the ambient stream and every measured series after it; the reserve's dead, the wall as
it ended and the works as the battle left them are RESULT marks — held back in `_set_opening` (two safeguards:
a claim's fix is switched off only when both are); the played end and the settled frame must agree on
everything, standards included (BA2-X5); the walk's end shot waits for the verdict to finish being written; the
host's recoil puts each man back where he stood when it was SCHEDULED, so a verb that moves men as the fight
opens waits it out (`AFTER_THE_RECOIL`); an order's first march MOVES the corps — price any lever from where the
order leaves him and hold the offer to the game (send it on a fresh board, read the muster after it — AND the game for a question the order raised: the muster counts a man
whose order stands behind "Your orders?"); press every new control in the real client (`tools/ba2_mode_c_walk.py`
is the pattern — its first run found what the tests and the walk had passed); a chip row
in the narrow province panel wraps — say the order once on the line and keep the chip to the man and
the price; a long province's panel scrolls on a short screen and the frame census reads its fold (set the
window on a whole line); the IQ-10 runner's `--only region_` also matches captures whose payload groups you
did not record (they are skipped with a note, not failed); a Bash heredoc eats backslashes — write every patch
script with the Write tool.

---

## After row BA — Session H: S15 the deploy (the prompt as it stood on November 13–14, 2026)

> Two things changed since it was written: **WS-11 is closed** (row BA's BA-1) and **WS-16 is BA-3's**, so the
> weak-spot review brings SIX rows to Session H's head, not seven; and **BA1-X4** and **BA1-X8** join that head.
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
four open rows** (`BUG_FIXES.md` §UI6 — UI6-X70, X73, X74, X75: a report subject naming a friend or a title, a third
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
forty-turn Mode C walk by the user — `docs/PLAYTESTING.md`; the walk is also the user's first look at Session
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
