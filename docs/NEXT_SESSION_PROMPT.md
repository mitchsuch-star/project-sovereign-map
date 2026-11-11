# NEXT SESSION PROMPT — Session F: Recognition and the gate's reading — DY-7 + Tier 8's close + Tier 7 evaluated (ONE session, ONE commit)

> Overwritten each time a session hands off. Current hand-over: **November 10, 2026 — SESSION E ✅ LANDED:
> TIER 8'S GATE RULED (`DYNAMISM_SPEC.md` §6a, under the user's delegation — "code commit and push what it tells
> you is next") AND DY-6 BUILT (`SYSTEMS_REFERENCE.md` §205; `DYNAMISM_SPEC.md` §6b the landing record, §2 the
> Tier 8 row, §8 row DY-6).** Three rules behind their own seams (T8-CROWN / T8-KING / T8-AI), ONE sweep with four
> arms (0 / CROWN / AI / ALL) on three surfaces, the series re-read, ONE commit.
> **DY-6 as built:** a crown is a `formable_nations` template with a `crown` block — ONE catalogue (`crowns.py`:
> `title`, `ai_carvers`, `since`; the first province the seat); six authored (the Kingdom of Naples — the
> one-province Bourbon court erased by the treaty —, Westphalia, Hungary, the Illyrian Provinces, the Grand Duchy of
> Finland for Russia, the Duchy of Milan for Austria; the four plain carves stay plain). The crown rides the existing
> `create_client` term end to end and adds its teeth at the ONE apply site (`formations.apply_create_client_clause`
> → `create_client_nation(clause=…)` → `crowns.on_crown_erected`, BEFORE the Proclamation): the title and
> `recognized_by` on the client's row, the boot house written for EVERY carve (`awakening.adopt_court` — the C3
> sibling fix), the Alarm (`ALARM_CAPITAL` 12 on the carver's house slot, the player's included), the beat
> (`nation_formed` + `crown` / `king` / `reign`; the dispatch `crown_erected`; the card's `crowns.card_lines`).
> **The marshal king:** `king_candidates` (laurels ≥ `KING_MIN_GLORY` 3 or the crown of glory; the store's
> princes), the guided row's `king_options` / `king_labels` / `terms_display` (`_crown_row_extras`), the confirm
> popup's picker (the `vassal_options` idiom), the add verb's `king` (`stamp_king_on_clause`, the refusals in words);
> `enthrone` — the marshal re-homed WITH HIS CORPS to the seat (`doctrines.set_marshal_nation`, THE setter; the
> removal's hygiene), loyalty = his trust clamped 30–95, the passed-over with laurels take envy toward him
> (`apply_jealousy` forced) and trust −5; a prince seeds loyalty 50, the slight trust −8, no envy; a regency
> otherwise. **The AI's road:** `settlement_third_party.erect_a_crown_in_the_terms` on both aim roads (the aim
> peace and the lock through `_cede_the_held_aim`) — the first authored crown the winner's house may erect, its
> soil all among the cessions, eligible by THE predicate, one `create_client` clause, a regency. **The `crowns`
> block** (`{"princes": [...], "recognition": {"legitimists": [...], "until": "beaten"}}`) in
> `world.moments["crowns"]` — `install` / `backfill` / the sibling carry; `withholding_courts` and the card's line
> ("Austria, Russia and Britain withhold recognition of the crown") are DY-6's WORDS, the teeth DY-7's.
>
> > **The measure (`tools/_t8_measure.py`, `_t8_series_arms.py`; the pins `TestTheSessionEMeasure`):** arm 0
> reproduces session D byte for byte on both surfaces; the band 28 / 27 / 26 and story classes 10 of 10 on every
> arm; the series unmoved with the seams read on the rig. **The seams are reached on every arm and NO crown is
> erected on any measured arm in forty turns** — the ambient AI peaces are Prussia's over Hanover (no crown
> authored for Prussia: 1806 annexed it), the courts' crowns (Russia's Finland, Austria's Milan) wait on wars the
> idle France never frees them to fight, the harness France's wars are the player's (the AI–AI road never runs for
> them), the scripted France authors no carve. The crown's proof is the test file's crafted boards (Naples under
> Murat end to end; Joseph's Naples; the regency; Finland under Russia on both AI roads). **The raised gate:
> clause 1 MET (10 of 10), clauses 2 and 3 UNMET** (no crown taken; the Kingdom of Italy alone on all ten, no
> ambient formation) — THIS session's reading, then the user's with no default (§7).
>
> **What session E leaves with the user (none blocks F; the readings, honest; §6b's levers):** (a) **the AI road's
> ambient silence** — the honest road to clause 3 is a court whose war the idle France does not own (§4a's content
> levers: a second great-power war), not a crown for Prussia's Hanover peace (ahistorical, and it would vary nothing);
> (b) **the marshal king's corps** — the whole corps goes with him; a royal guard of a fixed size with the rest
> returned to the depots is one line; (c) **the prince's loyalty 50** against a king's trust; (d) session D's three
> and session C's five stand.

**NOW — SESSION F (`DYNAMISM_SPEC.md` §2b): Recognition and the gate's reading — DY-7 (§6, the gate's Q4 as ruled
at §6a: the numbers N-DY7, tuneable; the shape the user's) + Tier 8's close + Tier 7 evaluated against the gate
(§7). Nothing new to rule at the head unless Tier 7 is needed; build, measure once with arms, commit once.**

**DY-7 the contract (`DYNAMISM_SPEC.md` §6; §6a Q4; row DY-7 of §8; tests `tests/test_dy7_recognition.py`):**
- **The legitimists withhold** (`crowns.withholding_courts` — built; DY-7 adds the CONDITION's read: `until:
  "beaten"` — a legitimist that has signed a peace as the LOSER with the crown's lord since the erection recognizes
  it (the Tilsit reading: Russia recognized Warsaw by the treaty that beat her); the `recognized_by` list on the row
  is the record, written at the peace chokepoint (`_record_common_peace_treaties` / the bilateral `_ratify_treaty`),
  never a scan; a Congress may GRANT it (the same instrument that rules a Question — `congress.py`'s sitting tick
  beside `questions.congress_rules`; the grant writes every sitting legitimist into `recognized_by`); a grant or a
  refusal is a beat (one log row — `recognition`, the census 185 → 186, the sixteen `== N` pins and `test_iq7`'s
  rationale move together — and a HIGH dispatch line in words, never a figure).
- **The price of a crown unrecognized** (one read, `crowns.recognition_terms(world, tag)` or its like): at the
  table — an acceptance malus with each withholding court (the lord's proposals to it; `settlement_scoring`'s
  component, named, N-DY7 ≈ −5 per unrecognized crown of the proposer's house, capped); in trade — the client's
  income with a withholding court halved (`diplomacy.process_trade_income`'s blockade arm is the idiom — one factor,
  one site); on awakened soil — the dial's −2 becomes −3 while unrecognized (`awakening.client_dial` reads
  `crowns.unrecognized(world, client)`; the §5 interplay DY-7 owns). The AI's crowns pay the same (GR5): Russia's
  Finland unrecognized by Austria and Britain.
- **The words:** the Diplomatic Ledger's nations tab (a crown's row names who withholds), the Proclamation card
  (built), Talleyrand's counsel (a reading, not a lookup — [[feedback-talleyrand-counsel-alive]]).
- **Seams:** one per rule — `crowns.the_legitimists_withhold` (the condition + the record + the Congress's grant),
  `crowns.an_unrecognized_crown_pays` (the three prices); rows T8-RECOG / T8-PRICE in `tests/_t3_seams.py`.
- **The measure:** clone `tools/_t8_measure.py` → `_t8b_measure.py`; arm 0 MUST reproduce
  `tools/_dy_signature_t8_2026_11_10.json` and arm ALL of `tools/_t8_chain_d_2026_11_10.json` byte for byte (no
  measured arm erects a crown, so the prices bite on no measured arm — say so plainly, and prove the teeth on the
  crafted boards: Naples under Murat unrecognized by Austria/Russia/Britain → the table's malus, the trade, the
  dial; the Congress's grant clears them).
- **Tier 8's close:** the §2 row, the §8 rows, `SYSTEMS_REFERENCE.md` §206, the landing record §6c.
- **Tier 7 evaluated (§7, Q5 of §6a — a rule, not a question):** the story-class count after DY-6 and DY-7 reads
  10 of 10 → clause 1 MET, the bounded dice are NOT built. Clauses 2 and 3 — UNMET on every record since Tier 4
  (no `rank_promotion`, the Kingdom of Italy alone) — **go to the user as an explicit question with NO default**
  (§0's standing rule; §7): the content levers are §4a's (a second great-power war on the 1805 board), §6b's (the
  AI road's ambient silence), the promotion crowns' six-turn hold (`SYSTEMS_REFERENCE.md` §201), the levée's reach
  (§5b). Put them in one batch at F's close, beside S15.

**The commit:** run the touched families (never the engine lanes), then COMMIT — the hook IS the one full-suite
run (about 8.5 minutes; do not pre-run the suite). If the hook is red, its failure list is the re-pin list.
Push: the user's "code commit and push" of session E stands for that session alone — ask.

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

**Open with the user beyond session F's head (none blocks it):** session E's four readings above; session D's three
(the letter's floor; the levée's reach; the dial's ambient road); session C's five (the march does not visibly bleed
— the ulcer's teeth; the letters' seat at the desk; the bands' pace; the raised gate's clauses 2 and 3; the pacing
record's drift); session B's three (the envy's cap at the coerce floor too; the crowns after the gift; no second
great-power war on the 1805 board — the content levers); GRD-38; GRD-37; the design rows of `DESIGN_REFINEMENT.md`
§GRD; the flip's two readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18);
the road record's readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions (`REFORMS_SPEC.md` §5a);
the crown term's level; SF-NAV-1-D1; Britain's letter without contact; the hook's remaining levers; `test_ep_f4`'s
flake; the two hash-seed orderings with no reader yet checked.

**After session F — the session plan (`docs/DYNAMISM_SPEC.md` §2b; no cuts without consent, spec §0):** **G: S15
the deploy, the user's own** (the gate checks, the build, the clean-environment run, the release record; signing
waits on the certificate). **After the deploy:** S14k-3 (Spain alone), S16, S17c.

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
