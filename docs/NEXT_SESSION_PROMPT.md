# NEXT SESSION PROMPT — Tier 0 of the November 6 review: T0-D "small fixes and the books" (T0-A, T0-B, T0-C ✅ landed), then T0-E … T0-I, then the dynamism tiers, then the deploy

> Overwritten each time a session hands off. Current hand-over: **November 6, 2026 — the whole-game review ✅ LANDED
> (Step 0 committed `75d66cd4`); T0-A "the turn's recovery" ✅ LANDED (`SYSTEMS_REFERENCE.md` §178); T0-B "Rule 4 and
> the drill" ✅ LANDED (§179); T0-C "the command road's silences" ✅ LANDED (§180)**
> (`docs/audits/GAME_REVIEW_2026_11_06.md`; the rows `BUG_FIXES.md` §GR and
> `DESIGN_REFINEMENT.md` §GRD; the plan `PRE_DEPLOY_PLAN.md` §2 row S15-R). The user's words, in order: *"send out sub
> agents (sonet) and lets do a review of the games sections … go off"*, *"i want the game to be dyanamic are you saying
> its determinsitic?"*, *"do tiered implementation of all of these make this happen after the bugs fixes all these"*,
> then *"code this"* for T0-C. The plan was approved in Plan Mode (the user's plan file `functional-growing-whale.md`;
> its content is mirrored in the S15-R row). **The deploy (S15) now follows Tier 0 and Tiers 1–3.**
>
> **NOW — Tier 0, slice T0-D "small fixes and the books"** (twenty-three GR rows, each `OPEN — owner S15-R Tier 0
> slice T0-D` in `BUG_FIXES.md` §GR; one commit through the hook, or two if the books' half runs long — the user's
> review between). Grouped by seam: **(1) the books (Golden Rule 8)** — GR-33 `ledger._build_economy` scans every
> region twice per call and is called 17–22 times a turn (cache the per-turn reading, invalidate with the active-nations
> cache); GR-59 the AI chest forecast runs the whole economy builder per nation, several times a turn (read the cached
> figure); GR-60 law and edict effect reads rebuild the affairs deck on every call, once per region in the supply cap
> (`reforms.py` effect reader — memoise the deck per turn); GR-62 the API summary scans every marshal once per province
> and every refresh rebuilds the marshal index; GR-61 `war_instances[*].offer_history` is an unbounded append (cap it,
> keep the last N, say so in `SAVE_FORMAT_REFERENCE.md`). Measure before and after with the G4 tripwires
> (`tests/test_scale_readiness_phase2.py`) and a timed 1805 turn; a read-only cache moves no series. **(2) the quotes
> that disagree with the applied value (ACH-1's class)** — GR-20 the grant-autonomy reply prints the nominal loyalty
> change, not the applied one, and buys nothing at the cap without a word (`vassal.py` ~2557); GR-40 the AI's
> settlement letter quotes an indemnity the payer cannot pay (the comment and docstring still say a bankrupt payer pays
> nothing); GR-42 `sell_neutrality` offers a token lump — all of a poor court's gold — because it lacks `friendly_gift`'s
> minimum (`ai_diplomacy._build_proposal_terms`); GR-13 the white-peace summary says "takes nothing and gives nothing"
> one line above the dispatch that lists the provinces conceded (the Talleyrand template predates S14E-10's
> titled-status-quo rule); GR-19 "the 1792 frontiers's terms" (`DICTATED_TIER_LABELS[3]` + an apostrophe-s on a plural,
> `ai_diplomacy.py` ~1628). **(3) the courts** — GR-18 (**P2**) Britain's turn-8 sue-path no longer fires on the
> shut-out arm (no offer by T12 on two seeds at war exhaustion above 90; VP-1's "Britain sues turn 8 on every seed" is
> stale — find the cause before the fix, and if the fix MOVES `BASELINE_SERIES`, hold it for T0-E/F/G's chain and say
> so); GR-12 Austria ends turn 1 with a negative treasury on every historical run and the digest never says "bankrupt"
> (the turn-1 spend gate, `enemy_ai._court_arms_with_its_purse`); GR-5 a court re-adopts the same design with the same
> `agenda_shift` beat twice (`agendas.py`'s emit — AMB-5); GR-34 a treaty manpower transfer bypasses the pool cap and
> the next regen silently deletes the surplus (`world_state.py` ~15383, `diplomatic_executor.py` ~4634); GR-38 the
> hard-coded `"France"` fallback in the counter-offer relation check (`ai_diplomacy.py` ~3891 — `player_nation` is in
> hand); GR-45 `statecraft._ASK_FAMILY` has no ask-ordering effect for "reaches_first: sponsor" and Prussia's "folds,
> then resents" (make the two traits bite, or strike the docstring claims — the user's call if it is a design); GR-7
> an AI-driven France issues attacks refused for third-party soil it is at peace with (the steward arm — not a planned
> mode; the honest fix is the AI's candidate filter reading `pursuit_capture_block` for the PLAYER's France only, or the
> row disposed as "AI France is not a mode" with the memo's §6 — the user's call). **(4) the narration** — GR-63 the
> `home_captured` headline repeats its garrison lecture (6 of 10 mornings on CMD-H; say the lecture once, the fact every
> time — `dispatch.py`'s class). **(5) the docs and the dead code** — GR-16 / GR-48 the docs and a comment say the AI
> never repeals (SFR-B14's repeal rung; `REFORMS_SPEC.md` §7, `ENEMY_AI_REFERENCE.md` row 1.78, `enemy_ai.py` ~7048);
> GR-43 the post-break-states comment contradicts the map and the spec (`diplomacy.py` ~14386 vs `DIPLOMACY_SPEC.md`
> ~1370 — one truth, three places); GR-49 `reforms.recruit_morale_bonus` is dead code (tests only); GR-50 `naval.py`
> recomputes the blockade cut inline instead of calling `blockade_cut_percent`. Then the GR rows struck FIXED,
> SYSTEMS_REFERENCE §181, STATUS (archive the oldest ▶ ▶ ▶ entry — seven stand), this prompt for T0-E/F/G.
> **Then T0-E/F/G together** (the sibling sweep of FA-N72 through `_engageable_enemies` — P3.9, P4.25, the surrounded
> arm; the eclipse brew reading the league's own formation gate; the Staff's save gated on reachability and the gold
> edicts held while saving — these MOVE the series), **T0-H** one re-record chain run alone on the final tree
> (`BASELINE_SERIES` by event, the reach, the probe, the standing and road records, the rig, the flip record, the
> benchmark compared), **T0-I** the benchmark's own arms (SEA's commission re-staged at loop 7; VOLTE's Austrian defeat
> re-staged; `commanded_provoke40.json`; the digest rows DIP-3 and AIF-10; ECON-1 play, LAW-5 play, AIF-9). Each slice
> its own commit and the user's review; Plan Mode for each tier's gate (Tier 2 → `AI_INTENT_SPEC.md` §3.8.2, Tier 3 →
> §13).
>
> **T0-C, landed (for the record; `SYSTEMS_REFERENCE.md` §180):** the objection's alternative asks the executor's own
> peace-soil predicate (`disobedience.field_is_barred` → `combat_executor.field_on_peace_soil(None, …)`;
> `pursuit_capture_block` module-level); a march to the province the corps stands in WITH an attack leg is refused free
> and the leg handed back as `remedy_command` ('Lannes, pursue Mack'), a real march's reply names its second leg;
> `stance_change` joins the stationary arms; on `move`/`scout` a province named before a commander keeps the slot
> (`_match_known_name_at`); the army named after the verb fans out and "everybody at <place>" goes to the corps there
> (`group_orders.collective_head` with `places`); the send-marshal rewrite carries its tail; "hold ney" is Ney's hold;
> the Emperor in subject position; "bring the Army of Italy to Piedmont and hold the passes" is a march with an arrival
> hold and a terrain noun is never fuzzed; `war_purpose_bar` read before any War Purpose card (the attack site and the
> three pursuit-capture sites through `_stage_or_bar_war_purpose`); `unbound_levy_recipient` names the levy's man;
> "probe" → scout, the bare "appoint" → the Marshalate (`routed_order_words.py` regenerated); the driver refuses a
> script with an unknown top-level key (`unknown_script_keys`, exit 2) and prints a MARSHALS row a turn
> (`THE_DIGEST_SEES_THE_MARSHALS`). Twelve GR rows FIXED (GR-21 … GR-32, CMDFEEL-6 and -7 among them by their owner
> line); 85 pins in `tests/test_t0c_the_command_roads_silences.py`; twelve corpus rows `t0c-*`; five pins re-seated (the hook found the third "probe routes nowhere" pin and an unseeded battle pin that asserted the win — SYSTEMS_REFERENCE §180.7).
> CMDFEEL-8/11/12 stay GRD-16 … GRD-18 for the user.
>
> **After Tier 0:** Tier 1 the seed rolled and shown at New Game (`NewGameRequest.seed`; `campaign_variance.roll_campaign_seed()`;
> a `LineEdit` on the menu; the env and the suite's pin untouched) → Tier 2 the bands widened (the story signature FIRST
> and its baseline archived; peace closes the theatre; Prussia's hook; Russia's two shores and an arbiter that sleeps;
> Prussia's second design; the measure) → Tier 3 the strategist (the march metric first; `war_council.war_aim`; one leash
> predicate for the four movement rungs; the home front; the terms; chains C and D) → Tier 4 gated on Tier 2's story-class
> count → **S15 the deploy, the user's own** (the UXR-4 walk, the certificate — `INK_IRON_SIGNTOOL_ARGS` / `SIGNTOOL` for
> the session, never in a file — `deploy\build.bat`, `tools/clean_env_run.ps1`, the release record from
> `docs/audits/RELEASE_TEMPLATE.md`). **After the deploy:** S14k part 3, S16, S17c.
>
> **Open with the user (none blocks Tier 0):** the design rows of `DESIGN_REFINEMENT.md` §GRD (each with its default —
> GRD-16 … GRD-18 are T0-C's three: the roster did-you-mean, the marshals' voices, the headline); the flip's two readings
> (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18); the road record's readings
> (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions (`REFORMS_SPEC.md` §5a); the crown term's level
> (`docs/audits/ECONOMY_REBALANCE_2026_10_27.md` §4.2); SF-NAV-1-D1; Britain's letter without contact (GRD, NAVVAS-1);
> GR-45 and GR-7 if T0-D reads them as design.
>
> **Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are
> named functions), functions over 500 lines 28 of 28 (T0-C's third war-purpose site pushed `_execute_glorious_charge`
> over by nine lines; the three sites share one helper now — a new line in `_post_combat_pipeline`, `_execute_glorious_charge`,
> `_chain_read_action`, `_parse_text` or `_apply_fuzzy_matching` goes in a helper), `WorldState.to_dict` 497 of 500
> (every new field in an existing store), CLAUDE.md within 62,000 LF bytes (19 bytes of headroom: pay a row by a trim),
> STATUS at most 7 "▶ ▶ ▶" entries (archive the oldest to the top of `docs/archive/STATUS_2026_Q4.md`); every `except
> Exception` must speak; the honorific is spelled ONCE (`clause_guards.HONORIFIC` — a regex that writes `(?:marshal\s+)?`
> by hand fails `test_fa_slice7…::test_the_census_no_address_regex_spells_marshal_alone`); a mock keyword added or widened
> needs `python -m tools.gen_routed_order_words` and may re-seat a "routes nowhere" pin (CX-R1's hand list, DD0's
> desks); a measure chain runs ALONE and no backend or deck edit lands while it runs — and NO backend or test edit lands
> while a commit's hook is running the suite in the working tree; `tests/test_fa_slice8…::TestAMutationIsNeverMaskedByStaleBytecode`
> fails under `PYTHONDONTWRITEBYTECODE=1` (the shell's, not the tree's — run pytest and the commit with
> `env -u PYTHONDONTWRITEBYTECODE`); the driver reads `--seam`, never `INK_IRON_SEAMS`; an instrument drifts under the
> slices — check each measure's flags against its record's note; every rig shim passes through `*a, **k`; a record diff
> is read WHOLE and a move is attributed by a second run with the one flag or seam changed; a rig re-run writes its OWN
> record (`--out`); the scenario and every asset sidecar sit under the ignored `assets/` — `git add -f` them; the docs
> are CRLF or LF per file (edit through Python on bytes, asserting each replacement matches once; write patch scripts
> with the Write tool — the heredoc eats backslashes); the deck JSON files and the golden corpus are hand-formatted —
> insert text, never re-dump; the three decks (the scenario, `tests/fixtures/moments_block.json`,
> `tests/fixtures/affairs_block.json`) are one deck, in lockstep; a moments op added reds `tests/test_moments_pacing.py`
> until the chain re-records; commit with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the
> background (the hook runs ruff and the full suite, about 10 minutes; never `--no-verify`) and read the log's EXIT
> line; Godot: one engine at a time, `--log-file` and every capture path ABSOLUTE; a `.gd` edit with the morning's parse
> report FAILS the hook (regenerate `tools/godot_parse_report.json`); `tools/playtest_runs/` is gitignored; run a probe
> under `python -X utf8`; `tools/ai_v_sweep.py --run` needs `PYTHONPATH=.` from the shell (AIF-9 fixes it in T0-I);
> the blind `unrehearsed_*.json` are census inputs (an `orders` key) — the driver refuses them by name now (CMDFEEL-13);
> a review probe that ends a turn through `/command` MUST set `INK_IRON_SAVE_DIR` first — the review's own probe
> overwrote the player's `saves/autosave.json`; a workflow's result lands in its task file as `{"result": …}` JSON —
> parse it, never read 700 KB raw; `get_visible_enemies` is the PLAYER's fog (a court's sight is
> `get_live_visible_enemies`); `field_on_peace_soil` is the PLAYER's rule (the AI keeps PT-F1); a rung's structured
> field reaches the executor only through `enemy_ai.execute_admin_phase`'s whitelist; the AI's law and edict rungs, the
> shore-up rung and `process_diplomatic_phase` are France-literal by design (an AI France is not a mode).
