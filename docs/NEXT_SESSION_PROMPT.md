# NEXT SESSION PROMPT — Session H: S15 the deploy — the user's own walk (the gate reads MET)

> Overwritten each time a session hands off. Current hand-over: **November 11, 2026 — SESSION G ✅ LANDED: THE GATE
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
> roster in two readings; `annexations_outside_aim` 0 on both surfaces; the band inside 23–28; 0 open GR rows.**
>
> **What session G leaves with the user (none blocks the deploy):** (a) **the understudy's reach** — a Naples at war
> with Austria has no authored aim against her, so the conduct rule leaves her free to plunder Piedmont, Lyonnais and
> Limousin from Austria's hands (`captures_outside_aim` 251 → 269): a reading on a court at war without an aim;
> (b) **the chest's number** — the price alone (built), or a half-reserve; (c) **the commanded middle arm** 26 → 25;
> (d) **jena's Pope under Vienna's wing** — the deterrence working, or an understudy's ask-ladder one refusal short
> (`REFUSAL_MEMORY_TURNS`); (e) session F's three, session E's four, session D's three and session C's five stand.

**NOW — SESSION H (`DYNAMISM_SPEC.md` §2b): S15 THE DEPLOY — the user's own walk.** The order: **(1) the gate
checks, each against its record file** (`PRE_DEPLOY_PLAN.md` §2 S15; `DYNAMISM_SPEC.md` §2 the S15 row, §7):
0 open GR rows (`.venv/Scripts/python.exe tools/defect_census.py --open`); story classes ≥ 6 — 10
(`_dy_signature_gate_2026_11_11.json`); a minor at secondary rank by promotion on ≥ 1 seed — lodi 33, marengo 40
(`_gate_census_2026_11_11.json` `rank_promotions`); the roster varying — wagram's {Kingdom of Italy, Papal States}
against {Kingdom of Italy} (the signature's `eliminations`); `annexations_outside_aim` 0 on both surfaces (the gate
census and `_gate_chain_d_2026_11_11.json`); the France band 23–28 — 28 / 27 / 25 (`_gate_band_2026_11_11.json`);
the historian test green on every seed (the suite's pins); the ratchet (`tests/test_code_health_ratchet.py`); the
parse harness green; **(2) the build** — `deploy\build.bat`, UNSIGNED until the certificate arrives
(`SYSTEMS_REFERENCE.md` §153.3–§153.4, `UX_UI_REVIEW_PLAN.md` §UXR-4: nothing on this machine — no signtool, no
certificate in either store; the day it arrives, `INK_IRON_SIGNTOOL_ARGS` / `SIGNTOOL` and the same script);
**(3) the clean-environment run** (a fresh clone, the venv from `requirements`, the hook installed with `Copy-Item
scripts/git-hooks/pre-commit .git/hooks/pre-commit`, the backend as `-m backend.main`, the client from the export, one
forty-turn Mode C walk by the user — `docs/PLAYTESTING.md`); **(4) the release record** (the commit SHA, the gate's
readings with their record files, the certificate's state, the user's walk's notes — `SYSTEMS_REFERENCE.md` §208,
`STATUS.md`). **After the deploy** (`PRE_DEPLOY_PLAN.md` §2; no cuts without consent, spec §0): S14k-3 (Spain alone),
S16, S17c.

**The commit:** session H's commits are the user's walk's — the release record and any gate fix each its own commit
through the hook (about 10 minutes; never `--no-verify`); push only on the user's word.

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

**Open with the user beyond session H's head (none blocks the deploy):** session G's four readings above; session F's three levers (`DYNAMISM_SPEC.md` §6c); session E's four readings (`DYNAMISM_SPEC.md` §6b); session D's three
(the letter's floor; the levée's reach; the dial's ambient road); session C's five (the march does not visibly bleed
— the ulcer's teeth; the letters' seat at the desk; the bands' pace; the raised gate's clauses 2 and 3; the pacing
record's drift); session B's three (the envy's cap at the coerce floor too; the crowns after the gift; no second
great-power war on the 1805 board — the content levers); GRD-38; GRD-37; the design rows of `DESIGN_REFINEMENT.md`
§GRD; the flip's two readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18);
the road record's readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions (`REFORMS_SPEC.md` §5a);
the crown term's level; SF-NAV-1-D1; Britain's letter without contact; the hook's remaining levers; `test_ep_f4`'s
flake; the two hash-seed orderings with no reader yet checked.

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
