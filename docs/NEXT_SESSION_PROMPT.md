# NEXT SESSION PROMPT — Session C: the Awakening, first half — the gate + DY-4 (ONE session, ONE commit)

> Overwritten each time a session hands off. Current hand-over: **November 10, 2026 — SESSION B ✅ LANDED:
> TIER 5 COMPLETE (`SYSTEMS_REFERENCE.md` §202; `DYNAMISM_SPEC.md` §4a the gate record and its landing
> note; §8 rows DY-2, DY-3, DY-1e, DY-1f, DY-1g).** Five rules behind their own seams, ONE sweep with six
> arms (0 / Q / QC / BERN / GIFT / ALL) on three surfaces, ONE commit: **DY-2 the Questions of Europe**
> (`backend/game_logic/questions.py` — the four tables ruled "Four on the drawn map", the latch at the
> capture chokepoint and its auto-charge mirror, the envy term in `intent._derive_weight`, the beat
> `question_turns` (the log census 182 → 183), the Balance tab's `question_lines`, the store inside
> `world.moments["questions"]`, the guarantee rung's Question arm); **DY-3 the Congress rules a Question**
> (on the sitting's tick, the holder recognized, the latch cleared, the unseated claimants −10); **DY-1e
> Bern's road home** (the user's "Road home": a client at its last province signs through its AI lord —
> `a_lord_signs_for_its_client`); **DY-1f the Emperor's gift** (the user's "best solution no corner
> cutting": the crowns' levers never bit — the ally petition asks for its AUTHORED design's provinces and
> its prevalidation reads the validator's occupied-homeland rule, so Pressburg's Tyrol reaches Bavaria;
> an AI aim peace signs for its allies' delivered aims — `a_leader_signs_for_its_allies`); **DY-1g the
> Emperor's treaty moves a seat** (the user's "reason best solution for gameplay": boundary (2) reversed,
> the Congress reading the HISTORIC capital through `congress._historic`; boundary (1) kept). The
> measure's figures are in §202 (arm 0 reproduces session A's records byte for byte; the movers per arm
> named per seed; `annexations_outside_aim`; the France band; `questions_turned`; `rank_promotions`;
> the standing series).
>
> **NOW — SESSION C (`DYNAMISM_SPEC.md` §2b: the gate OPENS the session and the build follows in it). Put
> the rulings below to the user ONCE, in one batch, at the head; then the gate in Plan Mode; then build,
> measure once with arms, commit once.**
>
> **The rulings session C opens with (nothing here is decided; content-first options co-equal, no speed
> option recommended — spec §0):**
> 1. **Q2 — the Awakening's grain.** The default stands until ruled: a PER-COURT scalar 0–100, regional
>    expression DERIVED (a per-region store costs save size and Rule 8 care for no v1 behavior the scalar
>    cannot express). Inside an EXISTING serialized store — `WorldState.to_dict` stands at 497 of 500;
>    survey the candidates at the head (the T5 precedent: `world.moments["questions"]`) and say which.
> 2. **Q3 — does the ulcer bleed France too?** The default: YES — Spain is the point; the player feels
>    the mechanic he inflicts. An AI-only ulcer would be a rule the player reads about and never meets.
> 3. **THE RAISE-THE-GATE QUESTION — NO DEFAULT (spec §7).** The deploy gate reads story classes ≥ 4 of
>    10. The Awakening and the Crowns now ship PRE-deploy (Q1 reversed, spec §0). Should the gate RISE
>    (the post-Awakening reading: ≥ 6 of 10, at least one seed with a minor at secondary rank, the
>    eliminations column varying)? Put it with NO default marked; until the user rules, ≥ 4 stands.
> 4. **The three expressions and N-DY4/5** (spec §5): the ulcer ×0.75 on an occupier's supply cap on soil
>    whose boot owner stands at `AWAKE_RISEN` (70); the liberation levée ×1.5 infantry regen and ×0.75
>    recruit cost for an awakened court (≥ `AWAKE_STIRRING`, 40) at war on contested home soil; client
>    drag −2/turn at autonomy ≤ 1, +1/turn at autonomy ≥ 2 (the tiger ridden). The raises (+1/+2/+3 per
>    turn by occupied-count band; +15 a dictated peace, tier-scaled; +10 the sovereign captured; +5 a
>    client squeezed) and the cools (−1/turn with no home province occupied; −10 lump on home rule
>    restored). All tuneable at the gate.
> 5. **What session B leaves with the user (none blocks C):** (a) the envy honours the ladder in three
>    stages (`questions._below_the_floors`: below the coerce floor until the court's ladder has
>    climbed, below the fight floor until its crisis stands, whole once it stands or at war — applied
>    after the jitter) — the session's own catch, measured on both the historical seed and the driven
>    austerlitz; the knobs left are `ENVY_WINDOW` (8) and the addend (+15), both tuneable; (b) **THE
>    TIER'S SIGNATURE CHANGE WAS NOT MET — said plainly:** no second great-power war appears on the 1805
>    board (§202's war column: unchanged on eight seeds; rivoli trades the honour war for the Hanover
>    war; ulm calms). The tables turn 26 times — for Austria, who is at war already and feels no envy
>    of her own gains; the courts seated against her are France (the words and the latch, never the
>    envy), Prussia (her Hanover design, already live — hastened two turns) and armyless minors; nobody
>    takes from Russia at the Polish table and the Eastern table never turns. The levers are CONTENT,
>    co-equal, nothing pre-recommended: a second German design for Prussia (the Fürstenbund — Dresden
>    and Frankfurt — seated behind the Hanoverian Prize, the T2-5 idiom); a Russian design on a table
>    Austria turns (Galicia is not drawn — the Polish table's Russian side is hers already); the Eastern
>    table's designs made boot-live (Austria's `the_eastern_question` or the Porte's shore); Saxony or
>    Hesse armed enough to take what they ask for; or the numbers. Each is authored content on its own
>    seed-measured arm, not a rule; (c) the crowns — none taken on any seed (the Grand Ducal Title the
>    first run showed on lodi came with a defect); the roads are pinned and wait for a played game — if
>    the played game shows none either, the AI's purse rung (100 a turn of upkeep on a minor's Net) is
>    the next lever, not K or the price.
>
> **The build (the contract `DYNAMISM_SPEC.md` §5; §8 row DY-4; tests `tests/test_dy4_the_awakening.py`):**
> the store (inside an existing serialized store — name it at the head); the raises at the existing
> chokepoints — the occupied-home counter at capture/liberation off the boot owner
> (`world._starting_controllers`; `is_own_soil_recapture`), the turn tick's band add (O(nations), never
> O(regions)), the settlement ratify's +15, the sovereign's capture +10, the vassal verbs' +5 — and the
> cools; the ulcer at `_supply_multiplier` (where home 1.5×, war damage and doctrine already compose);
> the letters on the affairs engine (`affairs.py` `PREDICATES` + `PREDICATE_PARAMS`; the THREE decks in
> lockstep — the scenario, `tests/fixtures/moments_block.json`, `tests/fixtures/affairs_block.json`; a
> moments op added reds `tests/test_moments_pacing.py` until the pacing chain re-records; `alarm` is a
> BARRED affair op — the Awakening's letters carry their own); the Gazette names the stirring; "events
> appear" — the letters' conditions are the scalar's own thresholds, never rare gates. Each rule its own
> zero-arg seam in the module it gates, its row in `tests/_t3_seams.py` (the recorded boards' hold-list
> folds it). DY-5 (the levée, the client dial, the measure chain) is session D's.
>
> **The measure — ONE sweep with arms** (clone `tools/_t5_measure.py` — six arms on three surfaces ran in
> about forty minutes; `tools/_t5_series_arms.py` for the standing series): arm 0, every Tier-6 seam
> down, MUST reproduce `tools/_dy_signature_t5_2026_11_10.json` and arm `ALL` of
> `tools/_t5_chain_d_2026_11_10.json` byte for byte; one more arm a seam. The AI-France march to Estonia
> is the ulcer's own measure (chain D's France entry against the November 6 review's run). The standing
> series: arm 0 = HEAD's `BASELINE_SERIES` (session B re-pinned it — the prior kept as `SERIES_BEFORE_T5`,
> the drill-fix records re-linked); if it moves, `SERIES_BEFORE_T6`, re-link, re-measure wo_slice9.
>
> **The commit:** run the touched families (never the engine lanes), then COMMIT — the hook IS the one
> full-suite run (about 8.5 minutes; do not pre-run the suite). If the hook is red, its failure list is
> the re-pin list. Push is the user's call — ask.
>
> **Session B's own traps (fresh):** the chokepoint's ONE writer idiom has a twin — `congress.note_capture`
> is the Congress's titled-province count, so a census that counts `note_capture(` by substring counts
> both (count `questions.note_capture(`); the auto-charge mirror's alias `_ac_questions` CONTAINS the
> substring `_questions`; the guarantee's join refusal reads WAR INSTANCES, not states — in 1805 Russia
> and Austria stand on one side of the coalition's instance, so a crafted "Russia at peace" board must
> strip her from the instance (`active_participants`, `side_by_nation`, `active_diplo_keys`) as well as
> flip her states; a scorer patch whose side effect imports the real function AFTER the patch recurses
> (import it at module level, the Slice H idiom); the ally petition's prevalidation was STRICTER than
> the validator (the payer had to still hold the province) — the validator's `occupied_homeland_cession_ok`
> is the ONE rule, now read through `_occupied_homeland_ok`; a crown's refusal reads the purse too ("costs
> 3,000 gold; the treasury holds 800") — give the court gold before asserting the grounds clear; under the
> gift's seam a junior's aim in its leader's hands goes HOME to the loser (T3-6), never to the leader; a
> province set by `controller =` carries no title record (`province_title.get`, never `[]`); the
> Questions' plurality is read among the CLAIMANT houses only, STRICT (a tie turns nothing), and "where
> it was not before" means before THIS capture (the board with the captured province read as the old
> controller's — no baseline seeded at install); a moments-store sibling key must be written only on an
> armed world (the bare flag world's `moments` is pinned `{}`), and `_backfill_moments` must read the
> deck (`block`), not the store's truthiness, or a store carrying the sibling alone blocks the deck's own
> backfill; `store_from_data` whitelists its keys — a sibling store is carried by its own `install` on
> `from_dict`, after the moments line; the dispatch's `{line}` template renders a backend-composed
> sentence whole (R7), and a watchers clause excludes the player's house (his reading is his own); the
> Godot parse report is regenerated with the memory recipe (`Start-Process … --headless --quit --path
> godot-client/project-sovereign --script ../../tools/godot_parse_check.gd`, exit 0, the report's mtime
> past the edited `.gd`'s); the campaign-log census flip is ONE script over the fourteen pins plus
> `test_iq7`'s docstring, its `!= N` and its `unexplained` list — and `test_estate_second_pass.py`'s
> `== 182` is a rente bill, not the census; the three live-historical-board pins in
> `test_ai_intent_assurance.py` (the standing series, Prussia's in-character observables, the live
> board's Prussian crisis) went red on the sweep's FIRST run and named two defects, not re-seats —
> the envy carrying a court past the ultimatum before its crisis stood (fixed: the cap), and a
> mid-turn flush of the turn's intent cache at the latch (fixed: removed — intent is turn-granular
> by `intent.py`'s contract; the chokepoint's own region-control flush is the engine's) — and the
> hook's first run named a third on the SF-LB-2 DRIVEN board (`test_sf_lb2_the_defenceless_prize.py`
> `TestTheDrivenBoard`, a live board the probe re-plays): the envy lifted Prussia off its ASKING
> rungs (align, bandwagon) to the ultimatum, where nothing is asked of an AI court, so the two refused
> asks the crisis needs never accrued in time, and the seeded jitter applied AFTER the cap pushed 84
> to 85 (fixed: three stages, the envy applied after the jitter) — the diagnosis was a HEAD worktree
> (`git worktree add <scratch> <sha>`, PYTHONPATH there, the same probe) against this tree's rows,
> never a guess; all held green once fixed, the standing series byte for byte; a live-board pin that
> moves is a DEFECT first, a re-seat last; the Edit tool matches LF text — a CRLF doc (STATUS, SYSTEMS_REFERENCE, MODDING_FORMAT,
> AI_INTENT_SPEC, CLAUDE.md, the archive) is patched on BYTES by a script written with the Write tool,
> each replacement asserted once; a seat under the player's treaty moves the commanded arms' boards —
> the France band is re-read, never assumed.
>
> **Session A's own traps:** a SEAT IS A CAPITAL in every read — the conduct rule's "enemy's seat", a
> bare declaration's default object, the AI's 100-value pick, the Alarm's 12, the tables' never-demand —
> so making a province a seat made it a target and moved all ten seeds: measure, never assume; "the
> capital" is TWO reads now — the seat (`world.get_nation_capital`) and the grievance's
> (`game_end.historic_capital`: the punitive bar, the partition manner, the Revanche — and from session B
> the Congress's recognition by defeat, `congress._historic`) — a new reader picks deliberately, and a
> reader that prints the capital's NAME for the court uses `game_end.seat_as_metonym`; a reader that
> runs AFTER a treaty's clauses apply sees the moved seat; the Congress's hold (RS-D1, `game_end` ~2434,
> `congress.py`) reads a court's capital in the Emperor's BLOC; a cession is applied BEFORE the same
> treaty's evacuations, so any rule at the title chokepoint that chooses among what a court holds must
> settle inside the turn (`_removal_this_turn`); `WorldState.get_power_tier` is called during `__init__`
> — read attributes with `getattr`; `filter_campaign_log` and `to_dict` are at their caps — a new
> always-visible type rides an existing line of its tuple, a new store rides an existing key; the
> campaign-log count is 183 now and its flip is fourteen pins plus the census; the laws store carries
> ELEVEN decks; the validator run on the BARE scenario file knows no armyless minor — a new block for the
> minors must not error on "unknown nation"; a pre-reform save's backfill reads the boot's seams; the
> Bash heredoc eats backslashes — write every script with the Write tool; autocrlf is on — patch on
> bytes and keep the file's own endings.
>
> **T4-2's, T4-1's, T3-6's, T3-5's, T3-4's, T3-3's, T3-2's, T3-1's, Tier 2's and DY-0's own traps:**
> unchanged from the prior prompt — read them in `docs/archive/`'s copy of the November 10 hand-over
> (`git show ac1e3b0e:docs/NEXT_SESSION_PROMPT.md`), every one still binding: `get_bloc_members` is the
> ALLIANCE bloc, never the house (`war_council._house_of`); both capture callers act on the province
> AFTER `capture_region` returns (`capture_was_signed_home`); `region_captured` producers are censused
> (11, `captured_from` required); a guarantee binds against EVERY attacker of a defending ward
> (`instruments.guarantee_exposure` ⊆ {its target}); `declare_war` brings the aggressor's allies by
> cascade (`suppress_unresolved_offensive_cascade=True` for a lone war) and a lord's CLIENTS follow it
> regardless (`vassal_auto_join`); a quieter world floods the page with its lone filler; every
> `add_threat` source needs a label row; a new rule at the peace belongs in the ONE titling pass
> (`game_end.title_status_quo_retentions`); the pair road runs the unheld-homeland return; "kept" is
> `game_end.holds_by_title`; the spoils of an ELIMINATED court never meet a peace; order peace roads by
> WHO IS BREAKING; `held_aim_lock`; independent command runs the AI's rungs for the player's marshals;
> the AI-France child prints UTF-8; "held" is a DELIVERED gain (`war_aim_delivered`); a bare
> declaration's objective defaults to the enemy capital — skip the seat wherever "owed" is read; a new
> diplomatic rung goes ABOVE P8's header; the front page's driven arms can die of Windows socket
> exhaustion under the full suite (re-run the module alone); a conduct-style rule binds only where its
> RECORD exists; the four aim reads are SEPARATE; marches capture on ENTRY; re-pinning `BASELINE_SERIES`
> needs the attribution rig; the boot DEFENSE objectives put a court's OWN soil in its core; the runner
> PRE-SEEDS `_war_ids`; verify region ids against the LIVE world; a deck entry seated ABOVE a guard
> kills the guard; a validator clause on a seam-filtered block WARNS; the suite's output NEVER pipes
> through tail; a refreshed instrument's nonzero is a DEFECT first; the three future-tier columns read
> event types the owning tiers MUST emit (`awakening_*` — Tier 6 is NEXT); `story_class` is
> sets-never-turns; a sweep or driver PARENT runs PLAIN.
>
> **Open with the user beyond session C's own batch (none blocks it):** the three session B readings
> above (5a–5c); **GRD-38 — should a full-authority Emperor ever be defied?**; **GRD-37 — T8 vs the
> post-S14j war economy**; the design rows of `DESIGN_REFINEMENT.md` §GRD (GRD-16 … GRD-36); the flip's
> two readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18); the
> road record's readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions
> (`REFORMS_SPEC.md` §5a); the crown term's level (`docs/audits/ECONOMY_REBALANCE_2026_10_27.md` §4.2);
> SF-NAV-1-D1; Britain's letter without contact (GRD, NAVVAS-1); the hook's remaining levers (the three
> fixtures' independent campaigns side by side, ~120 s of worker time — a concurrency change on a
> memory-bound suite); `test_ep_f4`'s decisive-victory pin, an unseeded ~1-in-1,500 flake; the two
> hash-seed orderings (`co_location_turns`, `_KNOWN_COURT_FORMS`) with no reader yet checked.
>
> **After session C — the session plan (`docs/DYNAMISM_SPEC.md` §2b; no cuts without consent, spec §0):**
> **D** the Awakening's second half (DY-5 the levée, the client dial, the interplays; the tier's measure
> chain and close) → **E** and **F** Crowns & Recognition (Tier 7's bounded dice only if the count still
> falls short, read in F) → **G: S15 the deploy, the user's own** (the UXR-4 walk, the certificate —
> `INK_IRON_SIGNTOOL_ARGS`/`SIGNTOOL` for the session, never in a file — `deploy\\build.bat`,
> `tools/clean_env_run.ps1`, the release record from `docs/audits/RELEASE_TEMPLATE.md`). **After the
> deploy:** S14k-3 (Spain alone), S16, S17c.
>
> **Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231
> (seams are named functions; the seven T0-EFG seams are the pattern: zero-arg, in the module they gate),
> functions over 500 lines 28 of 28, `WorldState.to_dict` 497 of 500 (every new field in an existing
> store), CLAUDE.md within 62,000 LF bytes (86 bytes of headroom), STATUS at most 7 "▶ ▶ ▶" entries
> (archive the oldest to the top of `docs/archive/STATUS_2026_Q4.md`); every `except Exception` must
> speak; a measure chain runs ALONE and no backend, test or deck edit lands while it runs; **a sweep or
> driver PARENT runs PLAIN, never `-X utf8`**; **never pipe a measure's output through `tail` into the
> task file**; a probe itself runs under `python -X utf8` when IT prints; the recorded boards' hold-list
> is `tests/_oct27_seams.py` (it folds `tests/_t3_seams.py`'s rows — a new seam goes THERE); **a record
> superseded but still pinned is KEPT under a dated or named file and its pins re-pointed**; **the
> benchmark run dir is committed in the precedent's shape ONLY**; the rig-record pins in
> `test_ai_drill_fix_2026_09_27.py` re-link through `SERIES_BEFORE_*` constants when the live constant
> moves on; the bytecode pins fail under the shell's `PYTHONDONTWRITEBYTECODE=1` (run pytest and the
> commit with `env -u PYTHONDONTWRITEBYTECODE`); the driver reads `--seam`, never `INK_IRON_SEAMS`;
> every rig shim passes through `*a, **k`; a rig re-run writes its OWN record (`--out`); the scenario and
> every asset sidecar sit under the ignored `assets/` — `git add -f` them; the docs are CRLF or LF per
> file; the deck JSON files and the golden corpus are hand-formatted — insert text, never re-dump; the
> three decks are one deck, in lockstep; commit with `env -u PYTHONDONTWRITEBYTECODE git commit -F
> <file>` from Bash in the background (the hook runs ruff and the full suite, about 8.5 minutes; never
> `--no-verify`) and read the log's EXIT line; a test module that opens a Godot WINDOW or starts a
> sandboxed backend joins `ENGINE_LANES["engine"]`; Godot by hand: one engine at a time, `--log-file` and
> every capture path ABSOLUTE; a `.gd` edit with the morning's parse report FAILS the hook (regenerate
> `tools/godot_parse_report.json`); `tools/playtest_runs/` is gitignored; a workflow's result lands in
> its task file as `{"result": …}` JSON; `get_visible_enemies` is the PLAYER's fog; `field_on_peace_soil`
> is the PLAYER's rule; a rung's structured field reaches the executor only through
> `enemy_ai.execute_admin_phase`'s whitelist; the AI's law and edict rungs, the shore-up rung and
> `process_diplomatic_phase` are France-literal by design; `_build_economy` takes a keyword (`rows`); an
> UNQUOTED Bash heredoc runs every backticked name in its body as a command; the cheapest proof that a
> change moves nothing is the keyed world probe — `to_dict` per turn, one hash per top-level key,
> against a `git archive HEAD backend godot-client/project-sovereign/assets/maps` copy, the
> notifications' random ids stripped, `PYTHONHASHSEED=0`.
