# NEXT SESSION PROMPT — Session E: Crowns & Recognition, first half — Tier 8's gate + DY-6 the crown erected (ONE session, ONE commit)

> Overwritten each time a session hands off. Current hand-over: **November 10, 2026 — SESSION D ✅ LANDED:
> DY-5 BUILT, TIER 6 COMPLETE (`SYSTEMS_REFERENCE.md` §204; `DYNAMISM_SPEC.md` §5b the landing record, §2 the
> Tier 6 row closed, §8 row DY-5).** Five rules behind their own seams, ONE sweep with six arms (0 / LEVEE / DIAL /
> REVANCHE / LIBERATORS / ALL) on three surfaces, the pacing chain re-recorded (the deck changed), the series
> re-read, ONE commit. **Nothing was ruled at the head** (the prompt pre-decided it; your "code commit push").
> **DY-5 as built:** the liberation levée (`awakening.levee_terms` — a court ≥ stirring, at war, home soil
> contested by the last tick's count: infantry regen ×1.5 at `get_manpower_regen_rates` after the war exhaustion
> and before the laws, the draft ×0.75 at the ONE recruit pricer after the doctrine's term; the AI reads the same
> pricer; the National Guard doubles it for a term; a `levee` log row — the census 184 → 185 — and a HIGH line);
> the client dial (`client_dial` — an awakened client −2 a turn at autonomy ≤ 1, +1 at ≥ 2; one read for the
> tick, the forecast and the debug breakdown; a rebellion names its cause on every exit); a risen people's
> revanche (`risen_grievance` — the partition bar waived at `risen`, the event's `cause`); the liberators'
> friction (`coalition_friction_step` — 1 a turn, not 2, while the league frees an awakened people); the third
> letter *The Nation in Arms* (`nation_in_arms`; Moncey writes; Accept 800 gold + an action + the `national_guard`
> op — the thirteenth, Accept-only, `turns` 3–12; Decline authority −3/−4/−5 on `bites: "floor"` — an
> authority-alone Decline keeps the floor by the validator's rule).
>
> > **The measure (`tools/_t6b_measure.py`, `_t6b_series_arms.py`, the pacing chain under
> `tools/playtest_runs/t6b_pacing_2026_11_10/`):** arm 0 reproduces session C byte for byte on both surfaces; the
> band 28 / 27 / 26 and story classes 10 of 10 on every arm; the series unmoved; the pacing record re-recorded
> with NO arm's letter timings moved and the road record standing (session C's note). **Every DY-5 seam bites
> where its condition holds and NOT ONE measured world-line moves in forty turns:** the levée rises on every
> ambient seed (France's at 25–33 under the coalition's garrisons, Bavaria's on five at 36–41; fifteen beats) and
> on eight harness seeds (Russia's at 26–39; Austria's never — erased by turn 11, and a levée needs a standing
> court), but the idle France recruits nothing, Bavaria's comes with turns to spare in single figures and Russia's
> last recruit (9–17) falls before its levée; the dial, the revanche and the liberators' ease never bite on a
> measured arm; *The Nation in Arms* arrived on the scripted France alone (T38 at grip 100, "Authority 100 → 97")
> and was never due on seventeen arms whose premise held — the floor (the idle France's grip 95 → 67 → 22 over
> turns 25–32). The raised gate: clause 1 MET, clauses 2 and 3 UNMET — Tier 8's to earn.
>
> **What session D leaves with the user (none blocks E; the readings, honest):**
> > (a) **the letter's floor** — an authority-alone Decline keeps `bites: "floor"` by the validator's rule (clamped it
> would cost nothing), and an invaded France is a bled France (grip 22 by turn 32 on the ambient boards), so the
> levée's own letter is silent where the levée matters most; the honest road to `"clamp"` is a SECOND Decline price
> — the people's temper RAISED by the refusal, which re-opens DY-4's Accept-only rule for the `awakening` op (its
> bounds −30..−1); your call, nothing pre-recommended; (b) **the levée's reach** — the AI courts recruit by their
> rungs' own gates (treasury, the force limit, the reserve), and a cheaper draft changed none in the window (Russia's
> last recruit at 9–17, its levée at 26–39): a rung that READS the levée (recruit MORE while it holds — the 1813
> surge as behaviour) is content's to earn, if wanted; (c) **the dial's ambient road** — no AI court vassalizes
> another on the ambient board, so the dial bites on the player's road (Spain under Joseph) and the road arms'
> Pressburg by subjugation alone; (d) session C's readings stand (the ulcer's teeth, the letters' seat, the bands'
> pace, the pacing drift).
>
> **NOW — SESSION E (`DYNAMISM_SPEC.md` §2b): Crowns & Recognition, first half — Tier 8's gate (the questions
> below, ONE batch, in Plan Mode at the head) + DY-6 the crown erected and the marshal king; build, measure once
> with arms, commit once. Session F takes DY-7 Recognition, Tier 8's close and Tier 7's evaluation (the raised
> gate's clauses 2 and 3 read there; the bounded dice built only if the story-class count falls short of 6).**
>
> **Tier 8's gate — the questions to put to the user in one batch (the §2b idiom), with the reading as it
> stands and NO default where the taste is the user's (`DYNAMISM_SPEC.md` §6 the contract; §0 no cuts without
> consent):**
> - **Q1 the crowns that may be erected.** The `create_client` term (already in `CANONICAL_CLAUSE_TYPES`,
>   `settlement_scoring.py`) promoted to a first-class GUIDED settlement term — never typed. The reading: an
>   AUTHORED `crowns` block in `europe_1805.json` (D7's principle — content reviewable in the file, validator-
>   clamped): each crown its name, the provinces that may carve it (Naples from the Neapolitan provinces,
>   Westphalia from Hanover + Hesse + Brunswick, Warsaw from Prussian and Austrian Poland, Illyria from the
>   Adriatic coast …), its seat, its boot house — against the alternative, any carve of ceded provinces named at
>   the table. The authored list keeps the historian test (no state the era could not have made); the open carve
>   keeps the player's hand free. The user's call.
> - **Q2 the marshal king.** Who may be crowned: the roster's marshals with glory above a bar (Murat in Naples,
>   Bernadotte in Pontecorvo — the stand-down machinery exists, `WorldState.stand_down_marshal`) and whether the
>   Emperor's BROTHERS (Joseph, Louis, Jérôme — not on the roster) sit in the pool as "a prince" at no roster cost.
>   The costs as §6 names them: the roster loses its man, his glory satisfied permanently (the jealousy ladder's
>   release valve, `JEALOUSY_SPEC.md`), the client's loyalty seeded from his trust, the passed-over marshals'
>   grievances AUTHORED (the §6 grievance triggers). History with teeth: a crown costs you your best sword. No
>   default on the brothers.
> - **Q3 the AI's road — ambient formations.** The raised gate's third clause reads the TEN AMBIENT seeds
>   (`formations` ∪ `eliminations` varying), so an AI court must be able to erect a crown in ITS OWN peace: the
>   reading is the same guided term in the AI–AI peace writer (T3-4's terms road, `settlement_third_party` —
>   a court holding an aim beyond the punitive bar may carve a client of the ceded soil: Prussia's Hanover as a
>   client, Austria's Bavaria), bounded by the authored crowns (Q1) and by the Alarm (a carve alarms Europe like a
>   capture). Without it clause 3 is content's to earn by eliminations alone — the user's call whether the AI
>   erects crowns at all.
> - **Q4 recognition's price (DY-7, session F — ruled now so DY-6 authors the fields).** The legitimists
>   authored per scenario (a `recognition` block: the courts that withhold and the condition — Austria, Russia,
>   Britain while unbeaten); the price of a crown unrecognized by a court: the table (an acceptance malus with the
>   withholding court), trade (the client's income with it halved), and on awakened soil the client drifts worse
>   (the §5 interplay DY-7 owns — the dial's −2 becomes −3 while unrecognized); the Congress may grant it (the
>   same instrument that rules a Question, `questions.py` / `congress.py`); a grant or a refusal is a beat. The
>   numbers are N-DY7's, tuneable; the shape the user's.
> - **Q5 (a rule, not a question — recorded so it is not re-opened):** Tier 7's bounded dice are built at F ONLY
>   if the story-class count falls short of 6 after DY-6 and DY-7; a clause still unmet after F goes to the user
>   with NO default (§7).
>
> **The build (the contract `DYNAMISM_SPEC.md` §6; §8 row DY-6; tests `tests/test_dy6_the_crown_erected.py`):**
> the `crowns` block and its validator; the guided term (the wizard's step, the staging layer
> `settlement_staging` → `settlement_ratify` — the client carve rides `formations`' existing carve and the
> `create_client` clause; the new court's boot house written into the Awakening's web — a crown erected on
> awakened soil is a court subjugated LATER by §5a C2's rule, its people keep their boot house); the marshal king
> (stand-down, the glory satisfied, the loyalty seed, the authored grievances); the AI's road (Q3) if ruled; the
> beats (`nation_formed` exists — a crown's beat rides it with a `crown` field, no new log type unless the Gazette
> needs one); DY-0's `formations` column reads the formed states already. Seams: one per rule (the guided term,
> the marshal king, the AI's road), rows T8-* in `tests/_t3_seams.py`. The measure: clone `tools/_t6b_measure.py`
> → `_t8_measure.py`; arm 0 MUST reproduce `tools/_dy_signature_t6b_2026_11_10.json` and arm ALL of
> `tools/_t6b_chain_d_2026_11_10.json` byte for byte; the pacing chain again only if the deck changes.
>
> **The commit:** run the touched families (never the engine lanes), then COMMIT — the hook IS the one full-suite
> run (about 8.5 minutes; do not pre-run the suite). If the hook is red, its failure list is the re-pin list.
> Push: the user's "code commit push" of session D stands for that session alone — ask.
>
> **Session D's own traps (fresh):** a people set by hand (`AW.move`) does not write the levée's bit — the bit is
> the TICK's (set the level, then tick once more; `levee_terms` reads the condition live, the row's bit is for the
> beat); the levée reads the STORE's count (`AW.occupied`, the last tick's), never `occupied_count` — a province
> taken this turn counts next morning; `_austria_contested`'s idiom: take Tyrol / Carniola / Moravia (Vienna kept
> — a court's LAST province walks T4-2's road), tick, set the level minus the band, tick; the dispatch formatter's
> table is `_DIPLOMATIC_EVENT_TEMPLATES` and its priority table `_DIPLOMATIC_EVENT_PRIORITY` (the R7 forms come
> from `_with_nation_forms`); a new log type's category must be one of combat / territory / economy / command /
> diplomacy (`test_category_mapping_complete`), and the sixteen `== N` census pins plus `test_iq7_satellites`'s
> rationale docstring and its `value != N` line all move together; the OPS count is pinned five times (the two
> `len(MO.OPS)` lines and three set-equality lines) and the deck's tail is sliced in six tests (`[-2:]`, `[-4:]`,
> `[-5:]` — re-index by id, never by position, when the deck grows); the `bites` rule: an authority-alone Decline
> MUST read `"floor"` (the validator refuses `"clamp"` beside it) and arrives only with the grip at the floor + the
> loss (71 + 3 = 74 at tier 1); a letter's `{seat}` is the HOST's seat when a host is bound — the lord's own lines
> use `{court}` / `{Court}` and the Moniteur's press carries no dateline; `python` is not on the Bash PATH — run
> everything through `.venv/Scripts/python.exe`, ruff through `-m ruff`; the frozen-board proof answers the OTHER
> letters "decline" each morning and leaves the measured letter standing (the Proclamation arrives at 13 and the
> Bavarian match at 8 ahead of it on this board).
>
> **Session C's, B's, A's and the earlier traps:** unchanged from the prior prompts — read them in the archive's
> copies (`git show 2589f3c1:docs/NEXT_SESSION_PROMPT.md` for session C's, `git show 93f82fb2:docs/NEXT_SESSION_PROMPT.md`
> for the earlier), every one still binding.
>
> **Open with the user beyond session E's head (none blocks it):** session D's readings above; session C's five
> (the march does not visibly bleed — the ulcer's teeth; the letters' seat at the desk; the bands' pace; the raised
> gate's clauses 2 and 3; the pacing record's drift); session B's three (the envy's cap at the coerce floor too; the
> crowns after the gift; no second great-power war on the 1805 board — the content levers); GRD-38; GRD-37; the
> design rows of `DESIGN_REFINEMENT.md` §GRD; the flip's two readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the
> Crown's readings (`EVENTS_SPEC.md` §18); the road record's readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's
> three questions (`REFORMS_SPEC.md` §5a); the crown term's level; SF-NAV-1-D1; Britain's letter without contact;
> the hook's remaining levers; `test_ep_f4`'s flake; the two hash-seed orderings with no reader yet checked.
>
> **After session E — the session plan (`docs/DYNAMISM_SPEC.md` §2b; no cuts without consent, spec §0):** **F**
> Recognition and the gate's reading (DY-7 + Tier 8's close + Tier 7 evaluated) → **G: S15 the deploy, the user's
> own**. **After the deploy:** S14k-3 (Spain alone), S16, S17c.
>
> **Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231
> (seams are named functions, zero-arg, in the module they gate), functions over 500 lines 28 of 28,
> `WorldState.to_dict` 497 of 500 (every new field in an existing store), CLAUDE.md within 62,000 LF bytes
> (86 bytes of headroom — session D's edit was byte-neutral), STATUS at most 7 "▶ ▶ ▶" entries (archive the oldest
> to the top of `docs/archive/STATUS_2026_Q4.md`); every `except Exception` must speak; a measure chain runs
> ALONE and no backend, test or deck edit lands while it runs; **a sweep or driver PARENT runs PLAIN, never
> `-X utf8`**; **never pipe a measure's output through `tail` into the task file**; a probe itself runs under
> `python -X utf8` when IT prints; the recorded boards' hold-list is `tests/_oct27_seams.py` (it folds
> `tests/_t3_seams.py`'s rows — a new seam goes THERE); **a record superseded but still pinned is KEPT under a
> dated or named file and its pins re-pointed**; the rig-record pins in `test_ai_drill_fix_2026_09_27.py`
> re-link through `SERIES_BEFORE_*` constants when the live constant moves on; the bytecode pins fail under
> the shell's `PYTHONDONTWRITEBYTECODE=1` (run pytest and the commit with `env -u PYTHONDONTWRITEBYTECODE`);
> the driver reads `--seam`, never `INK_IRON_SEAMS`; every rig shim passes through `*a, **k`; a rig re-run
> writes its OWN record (`--out`); the scenario and every asset sidecar sit under the ignored `assets/` —
> `git add -f` them; the docs are CRLF or LF per file (STATUS, SYSTEMS_REFERENCE, MODDING_FORMAT, the archive
> CRLF — patched on bytes; DYNAMISM_SPEC and this prompt LF); the deck JSON files and the golden corpus are
> hand-formatted — insert text, never re-dump; the three decks are one deck, in lockstep; commit with `env -u
> PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the background (the hook runs ruff and the full
> suite, about 8.5 minutes; never `--no-verify`) and read the log's EXIT line; a test module that opens a
> Godot WINDOW or starts a sandboxed backend joins `ENGINE_LANES["engine"]`; a `.gd` edit with the morning's
> parse report FAILS the hook (regenerate `tools/godot_parse_report.json`); `tools/playtest_runs/` is
> gitignored; `get_visible_enemies` is the PLAYER's fog; a rung's structured field reaches the executor only
> through `enemy_ai.execute_admin_phase`'s whitelist; an UNQUOTED Bash heredoc runs every backticked name in
> its body as a command — write every script with the Write tool; the cheapest proof that a change moves
> nothing is the keyed world probe (`to_dict` per turn, one hash per top-level key, against a `git archive
> HEAD` copy, `PYTHONHASHSEED=0`).
