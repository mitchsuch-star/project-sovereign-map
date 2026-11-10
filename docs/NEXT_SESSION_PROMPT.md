# NEXT SESSION PROMPT — Session B: Tier 5 whole — the Questions of Europe + the Congress rules a Question (ONE session, ONE commit)

> Overwritten each time a session hands off. Current hand-over: **November 10, 2026 — SESSION A ✅ LANDED:
> TIER 4 COMPLETE (`SYSTEMS_REFERENCE.md` §201; `DYNAMISM_SPEC.md` §3c "The seat landed" / "G6 landed" /
> "The tier's close").** Two rules behind their own seams, ONE sweep with three arms, ONE commit:
> **T4-2b the court removes** (`game_end.a_court_removes_its_seat`, row T4-2b — a court whose seat a treaty
> of its own house titles to another AI court removes to the richest homeland province in its hands and
> returns with its authored capital; the moved seat rides `Region.is_capital`, no new field; the player's
> house exempt on either side) and **T4-3 promotion** (`reforms.a_minor_may_rise`, row T4-3 — rank DERIVED
> from a `rank` law in force; the five crowns of 1806 on their designs' grounds held six turns;
> `rank_promotion` the one new log type, the count 182). The measure: arm 0 reproduces the T4-2 records byte
> for byte on both surfaces; **the seat ALONE moves all ten seeds** (story classes 9 → 10; Bavaria's court in
> Franconia on every seed, Hanover's in Brunswick on six; Prussia's word for Bavaria honoured on seven
> seeds; Switzerland falls on ulm); **the crowns move NOTHING — no court took one on either surface**; the
> France band on the commanded arms 28 / 27 / 26; the standing series unmoved (`BASELINE_SERIES` stands);
> `annexations_outside_aim` 0 in the harness and **1 ambient (Bern, kept by Bavaria on ulm — a fallen
> client's spoils), put to the user**. The hook's banner and CLAUDE.md read 8:22.
>
> **NOW — SESSION B (`DYNAMISM_SPEC.md` §2b: the gate OPENS the session and the build follows in it). Put
> the rulings below to the user ONCE, in one batch, at the head; then the gate in Plan Mode; then build,
> measure once with arms, commit once.**
>
> **The rulings session B opens with (nothing here is decided; content-first options co-equal, no speed
> option recommended — spec §0):**
> 1. **Q4 — the Questions.** The default stands until ruled: FOUR (German, Italian, Eastern, Polish); the
>    Maritime Question stays folded into the blockade machinery `NAVAL_SPEC.md` owns.
> 2. **Their provinces — the draft lists do not fit the map** (read against `europe.json` on November 10):
>    `Saxony` is drawn as `Dresden`; `Venetia`, `Moldavia`, `Wallachia` and `Warsaw` are NOT drawn;
>    `Galicia` on this map is SPAIN's. As drafted the Polish Question holds `Posen` alone and the Eastern
>    Question `Rumelia` and `Albania`. Two ways, both whole: (a) four Questions on the provinces the map
>    does draw — the Polish Question from the partition shares that are drawn (Prussia's `Posen`; Russia's
>    `Lithuania`, `Volhynia`, `Podolia`, `Vilna`), the Eastern from `Rumelia`, `Albania`, `Epirus`,
>    `Constantinople` and Russia's `New Russia`; (b) three Questions now, the Polish one authored the day
>    the map draws Warsaw. The user's to choose; the claimants per Question go with it.
> 3. **The latch's store.** `{question_id: {nation, turn}}` must live inside an EXISTING serialized store
>    (`WorldState.to_dict` is at 497 of 500). Survey the candidates at the head and say which and why;
>    it is plumbing unless a candidate shows in play.
> 4. **The numbers (N-DY2):** `ENVY_WINDOW` 8 turns, `WEIGHT_QUESTION_ENVY` +15 — tuneable at the gate.
> 5. **DY-3, the Congress rules a Question.** The spec calls it the tier's "cut-first tail"; under the
>    standing rule on cuts it is BUILT in session B. If the session cannot hold it, that goes to the user
>    as a question with no default — never a silent slip.
> 6. **Three things session A leaves with the user:**
>    (a) **Bern** — the one province on the deploy gate's annexation line. A client that falls signs
>    nothing (T4-2's exemption), so its last province stays with an AI taker outside that taker's aims.
>    Leave it, or rule a road home for a fallen client's ground.
>    (b) **The crowns were not seen.** No court held its grounds six turns in forty on any seed. The levers
>    are K (6) and the price (3,000 gold) — or Tier 5's envy may bring the wars that deliver grounds; the
>    measure after B will say.
>    (c) **The seat's two boundaries**, each one line to reverse: the player's own court never removes; a
>    court whose capital the PLAYER's house holds by treaty does not remove (reversing this one needs the
>    Congress's recognition-by-defeat reads moved to `game_end.authored_capital` first).
>
> **The build (the contract `DYNAMISM_SPEC.md` §4; §8 rows DY-2 and DY-3; tests
> `tests/test_dy2_the_questions_of_europe.py`):** the `questions` scenario block and its validator (every
> province exists, every claimant boots active, at least two claimants — and the T2-6 lesson: a clause on a
> seam-filtered block WARNS); the latch at the ONE capture chokepoint and nowhere else; the envy term in
> `intent._derive_weight` (a claimant's gain quickens the OTHER claimants' designs at that table, inside the
> window, never a non-claimant's); the "Question turns" beat (the `question_turns` log type — DY-0's column
> reads it; the count pin flips 182 → 183 with the fourteen-line idiom and the census in `test_iq7`); the
> Balance tab's Questions panel in sentences (client pass — if it does not fit beside the engine, §2b names
> the split: engine and words first, the panel second); the Alarm's guarantee rung's Question arm (§3c G2);
> DY-3 (a sitting Congress recognizes the holder, the latch clears, the unseated claimants take a relation
> write). Each rule its own zero-arg seam in the module it gates, its row in `tests/_t3_seams.py`.
>
> **The measure — ONE sweep with arms** (clone `tools/_t4_3_measure.py`: it runs three arms on three
> surfaces in about a quarter of an hour): arm 0, every Tier-5 seam down, MUST reproduce
> `tools/_dy_signature_t4_3_2026_11_10.json` and arm `ALL` of `tools/_t4_3_chain_d_2026_11_10.json` byte
> for byte; one more arm a seam. The standing series: clone `tools/_t4_3_series_arms.py` (arm 0 = HEAD's
> series); if it moves, re-pin with `SERIES_BEFORE_T5`, re-link the drill-fix records, re-measure
> wo_slice9. The tier's close reads the second-war count per seed (Tier 5's signature change: "the war
> column stops reading Prussia–Hanover alone" — at session A's close five seeds already open NO council war
> at all: the honour war for Bavaria stands in its place) and `questions_turned`.
>
> **The commit:** run the touched families (113 modules ran in under four minutes at eight workers — never
> the engine lanes), then COMMIT — the hook IS the one full-suite run (about 8.5 minutes; do not pre-run
> the suite). If the hook is red, its failure list is the re-pin list. Push is the user's call — ask.
>
> **Session A's own traps (fresh):** a SEAT IS A CAPITAL in every read — the conduct rule's "enemy's
> seat", a bare declaration's default object, the AI's 100-value pick, the Alarm's 12, the tables'
> never-demand — so making a province a seat made it a target and moved all ten seeds: measure, never
> assume; "the capital" is TWO reads now — the seat (`world.get_nation_capital`) and the grievance's
> (`game_end.historic_capital`: the punitive bar, the partition manner, the Revanche) — a new reader picks
> deliberately, and a reader that prints the capital's NAME for the court uses `game_end.seat_as_metonym`;
> a reader that runs AFTER a treaty's clauses apply sees the moved seat (`record_punitive_cessions` wrote no
> record for a ceded capital until it read the grievance's); the Congress's hold (RS-D1, `game_end` ~2434,
> `congress.py`) reads a court's capital in the Emperor's BLOC — ten pins fell when the rule bound the
> player's treaties; a cession is applied BEFORE the same treaty's evacuations, so any rule at the title
> chokepoint that chooses among what a court holds must settle inside the turn (`_removal_this_turn`);
> `WorldState.get_power_tier` is called during `__init__` (`_setup_initial_control`) — read attributes
> with `getattr`; `filter_campaign_log` stands at 499 of 500 lines and `to_dict` at 497 — a new
> always-visible type rides an existing line of its tuple; the campaign-log count is 182 and its flip is
> fourteen pins (`== N  # N-1->N flipped consciously:` — one script) plus the census's docstring and its
> `unexplained` list in `test_iq7`; the laws store carries ELEVEN decks — a pin that equates the decks
> with `REFORM_DECKS` reads the non-promotion decks (`reforms.is_promotion`); the validator run on the
> BARE scenario file (no injected provinces) knows no armyless minor — a new block for the minors must not
> error on "unknown nation" (a court with an agenda deck has already drawn that warning); a pre-reform
> save's backfill reads the boot's seams (`reforms.standing_deck`); a DoD pin on the LIVE historical
> world-line (`test_ai_intent_assurance.TestArmAAmbientDoD`) re-reads whenever the ambient board moves — a
> forced peace (`last_refuge`) is no weary peace; `tools/_t3_5_chain_d.py` pops `INK_IRON_SEAMS` for arm D
> — hold an arm's seams with `--arm-seams ARM=SPEC;SPEC`; the Bash heredoc eats backslashes even behind a
> quoted delimiter (a patch script written through it lost a line continuation, and a failed step chained
> by a NEWLINE let the next step run and append a section twice) — write every script with the Write tool
> and chain with `&&`; autocrlf is on, so a file's working copy may be CRLF while its blob is LF — patch
> on bytes and keep the file's own endings.
>
> **T4-2's own traps:** `get_bloc_members` is the ALLIANCE bloc, never the house — a title or
> "keeps by treaty" read uses `war_council._house_of` (the first words gave France Frankfurt "by treaty" for
> her ally's peace); both capture callers act on the province AFTER `capture_region` returns (plunder,
> secure, the estate rule, the row) — a rule that can move the controller inside the chokepoint must be
> answered in BOTH AI arms (`capture_was_signed_home`); `region_captured` producers are censused
> (`test_wo_slice4`: the count pinned at 11, `captured_from` required) — one writer per new row; a court
> that lives on moves the standing series through France's BLOC weight (`hegemony_passive`), not through
> the rule's own writes — spy `coalition.add_threat` / `reduce_threat` per arm to name the mover; a crafted
> board that needs a court truly GONE holds the T4-2 seam down (two S14G-D1 pins do); `declare_war(France,
> X)` brings France's clients with her (a "player's house holds the ground" board uses Holland); a
> conqueror with no authored aim on its victim hands everything back at the last province — as ruled;
> the reckless auto-charge settles a court without ground AFTER its loop (the battle's bookkeeping still
> reads the beaten corps); a bare WAR state with no instance binds nothing; the ambient records reproduce
> byte-identically on a re-run — do it after any late refactor; `_rebellion_turn(flips)` takes
> `MODULE:NAME=lambda *a, **k: False` to hold a seam in its child.
>
> **T4-1's own traps:** a guarantee binds against EVERY attacker of a defending ward — an AI word must
> check `instruments.guarantee_exposure` ⊆ {its target} or it declares war on courts nobody meant (the Porte
> marched on France before the fix); `declare_war` brings the aggressor's allies by cascade — stage a lone war
> with `suppress_unresolved_offensive_cascade=True`; raising AI slots moves the standing series through the
> BATTLES (the levy price, Mack's assaults), not the rung — attribute with `tools/_t4_1_series_arms.py`, and a
> `BASELINE_SERIES` re-pin is the rig + `SERIES_BEFORE_*` + the drill-fix re-links; a quieter world floods the
> page with its lone filler (fixed: `dispatch.a_lone_filler_yields_to_the_quiet_floor`) — read the front-page
> driven arms after any change that calms the board; `coalition._eclipse_candidate` returns `(court, slot)`;
> every `add_threat` source needs a label row (the AST census in `test_moments_engine.py`) — a dynamic family
> needs a prefix arm in `_threat_source_label`; the words read the STORE, so `alarm_lines` speaks of any AI slot
> ≥ 30 even with the write held down.
>
> **T3-6's own traps:** a new rule at the peace belongs in the ONE titling pass
> (`game_end.title_status_quo_retentions`) — every signed road runs it, and the Road Home corridor opens right
> after it on the same setter; the pair road ALSO runs the unheld-homeland return (`_return_unheld_homeland`,
> PC15-D4) regardless of aims or titles — isolate a peace rule in a pin by standing a corps on the ground (and
> Mack boots at Ulm, in Swabia — moving him strips Swabia); "kept" is `game_end.holds_by_title` (a retention or a
> conquest past its 12-turn quiet clock), never mere control — an ongoing war's ground is occupation; the spoils
> of an ELIMINATED court never meet a peace, so no peace rule reaches them; the instrument's end-of-run reads go in
> `RunCapture.capture_final` (a run fact — never the boot block, the IQ-7 graft control's law).
>
> **T3-5's own traps:** a lenient offer that runs first in a pass pre-empts the loser's own road —
> order peace roads by WHO IS BREAKING, never by which function the pass calls first; a peace that ends a war
> whose aim is held signs it by name (`held_aim_lock`) or the lightly held province walks home with the
> unheld-homeland return; "the player's rungs never run here" was false — independent command
> (`EnemyAI.decide_single_action`) runs the AI's rungs for the player's marshals, so any rule that exempts the
> player nation must read the acting marshal; the AI-France sweep's child prints UTF-8 — its parent now
> decodes `utf-8`, never cp1252; a census detector that reads WORDS must exclude a pair exit's own phrasing
> ("takes it on the held line" is no cession); chain C re-runs byte-identically — a re-run to enrich a census
> is cheap and lawful before the commit.
>
> **T3-4's own traps:** "held" is a DELIVERED gain — the live design arm counts only provinces the
> enemy still holds (a captured design province leaves `war_aim_core` the turn it falls, and the satisfied
> design hands the deck to the next), so any consumer asking "was the aim achieved" reads
> `war_aim_delivered`, never the live core; a bare declaration's objective defaults to the enemy capital
> (`declare_war`'s road; the council overwrites it with its design's provinces) — skip the seat wherever
> "owed" is read; `_apply_settlement_terms` eliminates a ceder left with no region, so ceding HELD ground
> from a court that holds nothing is an elimination (the guard: 90, a great power never); a new diplomatic
> rung goes ABOVE P8's header (`test_pc_rulings` slices 900 characters from it); a sub-pair exit's cession
> precedes `_return_unheld_homeland` and passes `keep=` (it would hand a lightly-held ceded province back);
> the three source-pinned lines in `_process_exhausted_pair_exits` (`test_sr1b`) stay verbatim; an AI–AI
> peace's TERMS move world-lines through purses even at the same turn (the indemnity's absence saved
> Hanover on marengo and re-timed austerlitz's league war) — read the gold and strength rows when naming a
> mover; the front page's driven arms (four driver children inside one worker) can die of Windows socket
> exhaustion under the full suite (WinError 10055 — every TestClient request opens a loopback socket pair;
> TIME_WAIT lingers minutes) — re-run the module alone to clear the code, let `netstat` TIME_WAIT drain
> before the commit, never touch the system's TCP settings; the measure runner `tools/_t3_4_measure.py`
> writes the signature record AND a census from the same digests (one chain, two files) — clone it for any
> slice whose own events want counting.
>
> **T3-3's own traps:** a conduct-style rule must bind only where its RECORD exists (the legacy world's
> wars are diplomatic states with 0 instances — a rule reading instances froze the AI there); the four reads
> are SEPARATE — words and pull read the stated object, the conduct rule adds the enemy's seat, the metric
> credits it — a new aim consumer picks its read deliberately; the capital default is PER PAIR (the enemy's
> own seat), never the opposing side's leader's; marches capture on ENTRY (the movement executor), so a rung
> filter does not stop a march from taking ground — measure, don't assume; re-pinning `BASELINE_SERIES` needs
> the attribution rig (arm 0 must reproduce HEAD's series byte for byte — clone `tools/_t3_3_series_arms.py`),
> the prior kept as `SERIES_BEFORE_*`, and every kept record re-linked in `test_ai_drill_fix_2026_09_27.py`;
> wo_slice9's courting cap is a re-measured pin with a dated history (`_rebellion_turn(flips)` evals its flips —
> `lambda: False` holds a seam); IQ-6's drives hold seams through `_PRE_SR1D_LEAGUE` + the CLI list; the sweep's
> children apply `INK_IRON_SEAMS` (the AU-2c hook) — a control chain is `INK_IRON_SEAMS=... _dy0_baseline.py`;
> mechanics pins on 1805 boards hold the conduct seam down with their cause (their subject is the mechanic);
> the class count can FALL under discipline — report it as the honest cost, never hide it.
>
> **T3-2's own traps:** the boot DEFENSE objectives put a court's OWN soil in its core — right for the metric,
> noise for words (speak the OUTSTANDING object); the boot war room renders ONE row (Britain the leader) plus
> the coalition — per-belligerent speech lives in the peace table's lines; a `type_display` fold breaks
> `endswith` pins (re-seat to `in` with cause); a words slice expects zero movers and pins it.
>
> **T3-1's own traps:** the runner PRE-SEEDS `_war_ids` with the boot instances — boot wars never reach
> `wars_opened` (their aims now ride the FIRST ROW's `boot_wars`; the boot block is the old-digest fallback
> only); a baseline runner stores the full per-seed SIGNATURE (the compatibility pin needs it); crafted digests
> for `derive_metrics` reuse `test_dy0_the_signature._row/_digest`, never hand-rolled; the aim-set is read AT
> THE WAR'S OPENING (deliberate — §13.2 R2); the honesty counter means walk-in captures from
> non-belligerents always count (watch it when staging).
>
> **Tier 2's standing traps (condensed):** verify region ids against the LIVE world; a deck entry seated
> ABOVE a guard kills the guard; new deck entries APPEND (index 0 = the emergent prepend contract);
> content slices need NO seam and their re-seat class is the deck-runs-out pin; the validator's health
> check is the warnings COUNT (11); a pin that AGES a freed arbiter ≥ 8 turns crosses the T2-4 quiet
> window (hold `T2_SEAMS_BY_ROW["T2-4"]` down or re-stage); staged quiet-window sleeps need an ENDED war
> instance (old ends in `archived_war_instances`); new dormancy clauses stay OUT of `_entry_satisfied`;
> the `_sign_peace` idiom (end the live war AND set PEACE); an in-process `advance_turn` loop is NOT the
> chain's world-line — replay ONE `spawn_run` child; no new log types (14 pins); quota-like AI state rides
> `participant_meta`; a validator clause on a seam-filtered block WARNS, never errors; the suite's output
> NEVER pipes through tail; a refreshed instrument's nonzero is a DEFECT first (the dd1 twin-letter
> precedent — `restamp_pending_treaty_letters` at the ratify chokepoint); the dd1 full run excludes
> SEED-quick (re-record it with `--arms SEED-quick`).
>
> **DY-0's own traps:** the three future-tier columns read event types the owning tiers MUST emit
> (`question_turns` Tier 5 / `rank_promotion` Tier 4 / `awakening_*` Tier 6 — Tier 4 is NEXT AFTER THIS
> TIER); `story_class` is sets-never-turns; the assurance controls (same-seed EQUAL, variance-off EQUAL)
> stay green on any widening; a sweep or driver PARENT runs PLAIN.
>
> **Open with the user beyond session B's own batch (none blocks it):** **GRD-38 — should a full-authority
> Emperor ever be defied?** (`tools/_t0i_benchmark_arms.json` `drama.defiance_pricing`); **GRD-37 — T8 vs the
> post-S14j war economy**; the design rows of `DESIGN_REFINEMENT.md` §GRD (GRD-16 … GRD-36); the flip's two
> readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18); the road
> record's readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions (`REFORMS_SPEC.md` §5a);
> the crown term's level (`docs/audits/ECONOMY_REBALANCE_2026_10_27.md` §4.2); SF-NAV-1-D1; Britain's letter
> without contact (GRD, NAVVAS-1).
>
> **After session B — the session plan (`docs/DYNAMISM_SPEC.md` §2b; no cuts without consent, spec §0):**
> **C** and **D** the Awakening (the story-class gate's raise question goes to the user at C's head, no
> default — spec §7) → **E** and **F** Crowns & Recognition (Tier 7's bounded dice only if the count still
> falls short, read in F) → **G: S15 the deploy, the user's own** (the UXR-4 walk, the certificate —
> `INK_IRON_SIGNTOOL_ARGS`/`SIGNTOOL` for the session, never in a file — `deploy\\build.bat`,
> `tools/clean_env_run.ps1`, the release record from `docs/audits/RELEASE_TEMPLATE.md`). **After the
> deploy:** S14k-3 (Spain alone), S16, S17c.
>
> **Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are
> named functions; the seven T0-EFG seams are the pattern: zero-arg, in the module they gate), functions over 500
> lines 28 of 28, `WorldState.to_dict` 497 of 500 (every new field in an existing store), CLAUDE.md within 62,000 LF
> bytes (86 bytes of headroom), STATUS at most 7 "▶ ▶ ▶" entries (archive the oldest to the top of
> `docs/archive/STATUS_2026_Q4.md`); every `except Exception` must speak; a measure chain runs ALONE and no backend,
> test or deck edit lands while it runs; **a sweep or driver PARENT runs PLAIN, never `-X utf8` — the children print
> cp1252 and a utf8 parent's pipe reader dies silently (stdout None, rc 0)**; **never pipe a measure's output
> through `tail` into the task file — the EXIT line survives, the evidence does not**; a probe itself runs under
> `python -X utf8` when IT prints; the T8 probe takes `--out` and reads `INK_IRON_SEAMS` in its child; the recorded
> boards' hold-list is `tests/_oct27_seams.py` — a slice that re-times them APPENDS its seams there, never per-test;
> **a record superseded but still pinned is KEPT under a dated or named file and its pins re-pointed — never re-run
> a later slice's measure into an earlier slice's record file** (`_standing_series_arms_flip.json`,
> `_vp1_road_arms_2026_11_06.json` are the precedents); **the benchmark run dir is committed in the
> precedent's shape ONLY — per arm `digest.jsonl`/`digest.md`/`meta.json` and the top-level jsons, never `saves/`,
> `server_console.log` or `_probe_saves` (224M raw vs 22M committed)**; the rig-record pins in
> `test_ai_drill_fix_2026_09_27.py` re-link through `SERIES_BEFORE_*` constants when the live constant moves on;
> `tests/_t0efg_seams.py` holds the seven seams for `--seam`/`INK_IRON_SEAMS`/`hold_down`; the bytecode pins fail
> under the shell's `PYTHONDONTWRITEBYTECODE=1` (run pytest and the commit with `env -u PYTHONDONTWRITEBYTECODE`);
> the driver reads `--seam`, never `INK_IRON_SEAMS`; every rig shim passes through `*a, **k`; a rig re-run writes
> its OWN record (`--out`); the scenario and every asset sidecar sit under the ignored `assets/` — `git add -f`
> them; the docs are CRLF or LF per file (edit through Python on bytes, asserting each replacement matches once;
> write patch scripts with the Write tool — the heredoc eats backslashes); the deck JSON files and the golden corpus
> are hand-formatted — insert text, never re-dump; the three decks (the scenario,
> `tests/fixtures/moments_block.json`, `tests/fixtures/affairs_block.json`) are one deck, in lockstep; a moments op
> added reds `tests/test_moments_pacing.py` until the chain re-records; commit with
> `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the background (the hook runs ruff and the full
> suite, about 9 minutes at ten workers; never `--no-verify`) and read the log's EXIT line; a test module that
> opens a Godot WINDOW or starts a sandboxed backend joins `ENGINE_LANES["engine"]` in `tests/conftest.py`
> (the census in `tests/test_the_engine_lanes.py` reds otherwise; a headless harness needs no lane); never run
> a full suite with `PYTHONDONTWRITEBYTECODE` set (two bytecode pins red); Godot by hand: one engine at a time,
> `--log-file` and every capture path ABSOLUTE; a `.gd` edit with the morning's parse report FAILS the hook
> (regenerate `tools/godot_parse_report.json`); `tools/playtest_runs/` is gitignored (the chains live there as local
> evidence; the records and the §-sections are the committed truth); the blind `unrehearsed_*.json` are census
> inputs — the driver refuses them by name (CMDFEEL-13); a review probe that ends a turn through `/command` MUST set
> `INK_IRON_SAVE_DIR` first; a workflow's result lands in its task file as `{"result": …}` JSON — parse it, never
> read 700 KB raw; `get_visible_enemies` is the PLAYER's fog (a court's sight is `get_live_visible_enemies`);
> `field_on_peace_soil` is the PLAYER's rule (the AI keeps PT-F1); a rung's structured field reaches the executor
> only through `enemy_ai.execute_admin_phase`'s whitelist; the AI's law and edict rungs, the shore-up rung and
> `process_diplomatic_phase` are France-literal by design (an AI France is not a mode); `_build_economy` takes a
> keyword (`rows`) — every shim that patches it takes `**k`; an UNQUOTED Bash heredoc runs every backticked name in
> its body as a command — write scripts with the Write tool or quote the delimiter; the cheapest proof that a change
> moves nothing is the keyed world probe — `to_dict` per turn, one hash per top-level key, against a
> `git archive HEAD backend godot-client/project-sovereign/assets/maps` copy, the notifications' random ids
> stripped, `PYTHONHASHSEED=0` — it names the keys that move and the turn they first do.
