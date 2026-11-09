# NEXT SESSION PROMPT — Tier 4's head: the Alarm of Europe (TIER 3 ✅ COMPLETE; T3-6 occupation is not annexation ✅)

> Overwritten each time a session hands off. Current hand-over: **November 9, 2026 — T3-6 OCCUPATION IS NOT
> ANNEXATION ✅ LANDED (row T3-6, ruled by the user's "make best call, best design not easiest";
> `SYSTEMS_REFERENCE.md` §198): at a peace between AI courts the winner keeps what the treaty cedes and what it
> may keep (`war_council.keepable_regions` — its house's authored aims and its declared articles) and hands the
> rest of the loser's homeland back (`game_end.aim_evacuations`, inside the one titling pass; the player's
> peaces keep SR-1a whole; a corps left standing walks home by the Road Home corridor); the deploy gate now
> measures ANNEXATION, not occupation (`war_council.annexations_outside_aim`, recorded at the run's end — a new
> signature column, never the story class; `captures_outside_aim` the war's footprint); the control reproduced
> T3-5's chain C, the kept debt fell **42 → 7** ambient (Franconia alone — the spoils of Bavaria's elimination
> on seven seeds), the AI courts of the AI-France harness keep **8**, story classes held at 8 (Saxony survives
> on austerlitz, Hanover on marengo)**, after T3-5 TIER 3 COMPLETE (§197: the terms made consistent, the
> harness France bound, chains C and D), T3-4 (§196), T3-3 (§195), T3-2 (§194), the gate + T3-1 (§193), Tier 2
> COMPLETE (§186–§192), Tier 1 (§185), Tier 0 (§178–§184). **The deploy (S15) follows the Concert Tiers 1–8: no
> cuts without consent (`DYNAMISM_SPEC.md` §0).**
>
> **NOW — TIER 4, THE ALARM OF EUROPE (`DYNAMISM_SPEC.md` §3, DY-1) + PROMOTION'S FIRST TEETH (§3b, DY-1b), ITS
> GATE IN PLAN MODE AT THE TIER'S HEAD** (the §8 law: author the tier's gate record before a line is built — the
> user approves the plan):
> - **The Alarm:** every AI court's annexation writes threat against the CONQUEROR at the ONE capture
>   chokepoint (`coalition.add_threat(world, amount, source_key="alarm:<region>", target=…)`; N-DY1: a province 6,
>   a capital 12, a third court's vassal or formation-peer 8; the player's captures write NOTHING new); felt only
>   through existing instruments (the brew, the eclipse, a NEW guarantee rung in the AI's diplomatic phase issuing
>   the existing D5 guarantee for the likely next victim); in WORDS only (Q6 — Talleyrand, the Balance tab).
> - **Promotion's teeth (§3b):** a minor that fulfils its design and holds its grounds enacts its promotion law;
>   the tier MUST emit `rank_promotion` events (DY-0's future column, `rank_promotions`).
> - **The T3-6 residual is Tier 4's (Rule 9, §3's done-when):** the deploy gate's `annexations_outside_aim` reads
>   7 ambient (Franconia — Bavaria eaten by Austria on seven seeds) and 8 for the AI courts of the AI-France
>   harness; the Alarm is what makes eating a minor cost — done when both read 0 (or each remaining province is
>   ruled by the user). Measure with `tools/_t3_4_measure.py` (signature + census) and `tools/_t3_5_chain_d.py
>   --arms D`, against the T3-6 records (`tools/_dy_signature_t3_6_2026_11_09.json`, `_t3_6_chain_d_…`).
> - Done when §3's list holds; test `tests/test_dy1_the_alarm_of_europe.py`; the STATUS line "Tier 4 the Alarm —
>   conquest pays in standing" with the sweep columns.
>
> **T3-6's own traps (fresh):** a new rule at the peace belongs in the ONE titling pass
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
> **Open with the user (none blocks Tier 3):** **GRD-38 — should a full-authority Emperor ever be defied?**
> (`tools/_t0i_benchmark_arms.json` `drama.defiance_pricing`); **GRD-37 — T8 vs the post-S14j war economy**;
> the design rows of `DESIGN_REFINEMENT.md` §GRD (GRD-16 … GRD-36); the flip's two readings
> (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18); the road record's
> readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions (`REFORMS_SPEC.md` §5a); the
> crown term's level (`docs/audits/ECONOMY_REBALANCE_2026_10_27.md` §4.2); SF-NAV-1-D1; Britain's letter
> without contact (GRD, NAVVAS-1).
>
> **After Tier 3 — the Concert (`docs/DYNAMISM_SPEC.md`; no cuts without consent, spec §0):** Tier 4 the
> Alarm of Europe + promotion's teeth → Tier 5 the Questions of Europe → Tier 6 the Awakening (the
> story-class gate's raise question goes to the user at its head, no default — spec §7) → Tier 8 Crowns &
> Recognition (Tier 7's bounded dice only if the count still falls short at the gate) → **S15 the deploy,
> the user's own** (the UXR-4 walk, the certificate — `INK_IRON_SIGNTOOL_ARGS`/`SIGNTOOL` for the session,
> never in a file — `deploy\\build.bat`, `tools/clean_env_run.ps1`, the release record from
> `docs/audits/RELEASE_TEMPLATE.md`). **After the deploy:** S14k-3 (Spain alone), S16, S17c.
>
> **Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are
> named functions; the seven T0-EFG seams are the pattern: zero-arg, in the module they gate), functions over 500
> lines 28 of 28, `WorldState.to_dict` 497 of 500 (every new field in an existing store), CLAUDE.md within 62,000 LF
> bytes (19 bytes of headroom), STATUS at most 7 "▶ ▶ ▶" entries (archive the oldest to the top of
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
> suite, about 10 minutes; never `--no-verify`) and read the log's EXIT line; Godot: one engine at a time,
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
