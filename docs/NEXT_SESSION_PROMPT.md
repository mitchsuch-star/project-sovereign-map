# NEXT SESSION PROMPT — Tier 4, session 2: T4-2 sign at the last (the gate ✅ RULED §3c; T4-1 the Alarm ✅)

> Overwritten each time a session hands off. Current hand-over: **November 9, 2026 — TIER 4'S GATE ✅ RULED
> (`DYNAMISM_SPEC.md` §3c, in Plan Mode; the user's "your call" on all three questions — the erasure rule, Q5,
> Q6) and T4-1 THE ALARM OF EUROPE ✅ LANDED (`SYSTEMS_REFERENCE.md` §199)**: an AI court's capture writes
> Europe's alarm against its house at the one chokepoint (`alarm.sound_the_alarm` — 6 / a capital 12 / a third
> court's client 8, on top of the +2 every conqueror already paid; the player's house nothing new); an alarmed
> neighbour pledges the existing D5 guarantee for the likely next victim (`alarm.process_alarm_guarantees`, in the
> AI-AI phase, only where the word binds against the conqueror alone); the words in Talleyrand, the Balance tab
> and Le Moniteur, never a figure. The measure: the control reproduced T3-6 byte for byte; story classes 8 → 10;
> Prussia's word for Bavaria against Austria at turn 7 on austerlitz, lodi and ulm; eight movers named; the kept
> debt **7** ambient (friedland, historical, marengo, rivoli: Austria keeps Franconia; jena: Hesse Swabia,
> Prussia Franconia, Switzerland Piedmont) and **7** for the AI courts of the AI-France harness (eylau Bavaria
> Vienna, friedland Bavaria Bohemia, jena Bavaria four Dutch/Swiss provinces + Spain Friesland). After T3-6
> (§198), Tier 3 COMPLETE (§193–§197), Tier 2 COMPLETE (§186–§192), Tier 1 (§185), Tier 0 (§178–§184). **The
> deploy (S15) follows the Concert Tiers 1–8: no cuts without consent (`DYNAMISM_SPEC.md` §0).**
>
> **NOW — T4-2, SIGN AT THE LAST (row DY-1c; the contract RULED at `DYNAMISM_SPEC.md` §3c G5 — build it as
> written, Plan Mode for the build's shape only):**
> - **Where:** `WorldState.capture_region`'s elimination check (`world_state.py`, "R81: Check for elimination") —
>   the one MILITARY erasure point; erasures by treaty (`_eliminate_nation(by_treaty=True)`) are untouched.
> - **The test:** the victim is erased only when no AI court AT WAR with it holds its homeland outside that
>   holder's keepable set (`war_council.keepable_regions(holder, victim)`).
> - **Otherwise it signs:** (1) those provinces go home FIRST (`game_end._return_home` — the court must hold
>   ground again before anything reads `get_active_nations`); (2) a pair peace with each such holder, reason
>   `last_refuge` added to `game_end.SIGNED_PEACE_REASONS` so the titling pass runs (T3-6's handback, SR-1a for
>   the keepable), T3-5's lock (`held_aim_lock` — the held aim by name), `declared_goals.settle_at_peace`,
>   `PAIR_EXIT_TRUCE_FLOOR_TURNS`, the Road Home corridor, `follow_the_lord` — factor the single-pair close out of
>   `settlement_third_party._process_exhausted_pair_exits` and reuse it, never a copy; (3) one event with the
>   words ("Bavaria signs at the last — Austria keeps Munich and Swabia by treaty; Austria evacuates
>   Franconia.").
> - **Exempt:** a client victim (its war is its lord's) and the player's house on either side; the player's
>   holdings never move. **D2 is narrowed, not deleted** — annotate `AI_INTENT_SPEC.md` §6 D2 (dated).
> - **Seam** `a_crown_falls_only_by_treaty` in `tests/_t3_seams.py` row T4-2; pins ride
>   `tests/test_dy1_the_alarm_of_europe.py`.
> - **Watch for jena's shape:** its 3 are spoils changing hands AFTER the erasure (Hesse takes Swabia from
>   Austria). If Bavaria survives, Swabia is Austria's by treaty and a later Hesse–Austria peace keeps it under
>   SR-1a (T3-6 hands back only the LOSER's homeland) — measure, then rule each remaining province with the
>   user (the done-when's own way out), never a silent widening.
> - **Done when:** the crafted board (Bavaria lives in Franconia at peace; the Kingdom-of-Italy shape still
>   erases); `annexations_outside_aim` 0 ambient and for the AI courts of the AI-France harness (or each
>   remaining province put to the user); the eliminations column varies; movers named against
>   `tools/_dy_signature_t4_1_2026_11_09.json` and `_t4_1_chain_d_2026_11_09.json` (the control with T4-2's seam
>   down must reproduce them).
> - Then **T4-3** promotion (§3c G6 — the 1806 crowns, rank derived from a `rank` law, `rank_promotion` the new
>   log type) and the tier's close (the France band re-read on the commanded arms, the landing record).
>
> **T4-1's own traps (fresh):** a guarantee binds against EVERY attacker of a defending ward — an AI word must
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
