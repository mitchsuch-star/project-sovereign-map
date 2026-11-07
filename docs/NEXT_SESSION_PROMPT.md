# NEXT SESSION PROMPT — Tier 0 of the November 6 review: T0-B "Rule 4 and the drill" (T0-A ✅ landed), then T0-C … T0-I, then the dynamism tiers, then the deploy

> Overwritten each time a session hands off. Current hand-over: **November 6, 2026 — the whole-game review ✅ LANDED
> (Step 0 committed `75d66cd4`) and T0-A "the turn's recovery" ✅ LANDED (the commit after `75d66cd4`; `SYSTEMS_REFERENCE.md` §178)**
> (`docs/audits/GAME_REVIEW_2026_11_06.md`; the rows `BUG_FIXES.md` §GR and
> `DESIGN_REFINEMENT.md` §GRD; the plan `PRE_DEPLOY_PLAN.md` §2 row S15-R). The user's words, in order: *"send out sub
> agents (sonet) and lets do a review of the games sections … go off"*, *"i want the game to be dyanamic are you saying
> its determinsitic?"*, *"do tiered implementation of all of these make this happen after the bugs fixes all these"*.
> The plan was approved in Plan Mode (the user's plan file `functional-growing-whale.md`; its content is mirrored in the
> S15-R row). **The deploy (S15) now follows Tier 0 and Tiers 1–3.**
>
> **NOW — Tier 0, slice T0-B "Rule 4 and the drill"** (no measured series expected to move; measured all the same;
> one commit through the hook): (1) **COMBAT-1** (filed P1, verified P2): one helper `Marshal.consume_drill()` that
> resets `shock_bonus`, `drilling`, `drilling_locked`, `drill_complete_turn`, called by `combat.py` (the inline clear at
> the field battle, ~564-568, replaced) AND by `combat_executor._resolve_garrison_combat` right after its
> `get_attack_modifier()` (~5926) when the drill was read — a drilled corps kept its +20% through every garrison
> assault (Golden Rule 4: read, use, THEN clear). Pin: a drilled Mack assaults Paris → `shock_bonus` 0 after; the
> muster preview (`consume=False`) leaves it; the field-battle path unchanged (existing pins). (2) **COMBAT-2**
> `defiance.py:134` / `strategic_executor.py:3963`: the fallback table is keyed lowercase and the strategic road passes
> the type UPPERCASE ("HOLD") — compare `.upper()` against an uppercase table; keep `literal → None`. Pins:
> `get_defiant_action(aggressive, "HOLD") == "attack"`; the end-to-end strategic defiance of HOLD attacks.
> (3) **COMBAT-5** `marshal.py:1670`: `base = min(8, base + 1)` LOWERS a 9 — `base = max(base, min(8, base + 1))`;
> pin: Soult's tactical 9 stays 9 under Precision Execution. (4) COMBAT-3 (PURSUE in neither defiance table),
> COMBAT-4 (literal/loyalist/dove popups without a Trust arm), COMBAT-6 (the Grouchy buff never expires), COMBAT-7
> (the Rule 1 residue) STAY design rows for the user (`DESIGN_REFINEMENT.md` §GRD GRD-31 … GRD-34 carry the defaults).
> Then the GR rows COMBAT-1/2/5 struck FIXED, SYSTEMS_REFERENCE §179, STATUS, this prompt. **Then T0-C** (the
> command road's silences: CMDFEEL-1/2/3/4/5/9/10/15, CMDFEEL-13/14 harness), **T0-D** (small fixes and the books),
> **T0-E/F/G together** (the sibling sweep of FA-N72, the eclipse brew, the Staff and the Edicts — these MOVE the
> series), **T0-H** one re-record chain run alone, **T0-I** the benchmark's own arms (SEA's commission at loop 7;
> VOLTE's defeat re-staged; `commanded_provoke40.json`; the digest rows). Each slice its own commit and the user's
> review; Plan Mode for each tier's gate (Tier 2 → `AI_INTENT_SPEC.md` §3.8.2, Tier 3 → §13).
>
> **T0-A, landed (for the record):** TURN-2 `WorldState.advance_turn` rolls the R20 stamp back on an exception and
> raises the transient `_advance_failed`; `turn_manager.end_turn` resumes the close alone (`_resuming` guards the
> signing, the lapse, the glory attacks, the enemy phase, the AI letter, the standing orders and the grievance pass)
> and the reply says so; TURN-1 the crash row passes the fog, names its court, has its dialog arm and its rail type
> `court_turn_failed` (the two `.gd` maps; the parse report regenerated); TURN-4 the fourteen handlers report (the
> ratchet caps `logs` at 0); AIDIP-6 `_hegemony_reading` + the honest labels; TURN-3/5 the two docs.
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
> **Open with the user (none blocks Tier 0):** the design rows of `DESIGN_REFINEMENT.md` §GRD (each with its default);
> the flip's two readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18); the road
> record's readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions (`REFORMS_SPEC.md` §5a); the crown
> term's level (`docs/audits/ECONOMY_REBALANCE_2026_10_27.md` §4.2); SF-NAV-1-D1; Britain's letter without contact
> (GRD, NAVVAS-1).
>
> **Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are
> named functions), functions over 500 lines 28 of 28, `WorldState.to_dict` 497 of 500 (every new field in an existing
> store), CLAUDE.md within 62,000 LF bytes (19 bytes of headroom after Step 0: pay a row by a trim), STATUS at most 7
> "▶ ▶ ▶" entries (archive the oldest to the top of `docs/archive/STATUS_2026_Q4.md`); every `except Exception` must
> speak; a measure chain runs ALONE and no backend or deck edit lands while it runs — and NO backend or test edit lands
> while a commit's hook is running the suite in the working tree; the driver reads `--seam`, never `INK_IRON_SEAMS`; an
> instrument drifts under the slices — check each measure's flags against its record's note; every rig shim passes
> through `*a, **k`; a record diff is read WHOLE and a move is attributed by a second run with the one flag or seam
> changed; a rig re-run writes its OWN record (`--out`); the scenario and every asset sidecar sit under the ignored
> `assets/` — `git add -f` them; the docs are CRLF or LF per file (edit through Python on bytes, asserting each
> replacement matches once; write patch scripts with the Write tool — the heredoc eats backslashes); the deck JSON files
> are hand-formatted — insert text, never re-dump; the three decks (the scenario, `tests/fixtures/moments_block.json`,
> `tests/fixtures/affairs_block.json`) are one deck, in lockstep; a moments op added reds `tests/test_moments_pacing.py`
> until the chain re-records; commit with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the
> background (the hook runs ruff and the full suite, about 10 minutes; never `--no-verify`) and read the log's EXIT
> line; Godot: one engine at a time, `--log-file` and every capture path ABSOLUTE; a `.gd` edit with the morning's parse
> report FAILS the hook (regenerate `tools/godot_parse_report.json`); `tools/playtest_runs/` is gitignored; run a probe
> under `python -X utf8`; `tools/ai_v_sweep.py --run` needs `PYTHONPATH=.` from the shell (AIF-9 fixes it in T0-I);
> the blind `unrehearsed_*.json` are census inputs (an `orders` key), not driver scripts (CMDFEEL-13); a review probe
> that ends a turn through `/command` MUST set `INK_IRON_SAVE_DIR` first — the review's own probe overwrote the
> player's `saves/autosave.json`; a workflow's result lands in its task file as `{"result": …}` JSON — parse it, never
> read 700 KB raw; `get_visible_enemies` is the PLAYER's fog (a court's sight is `get_live_visible_enemies`); a rung's
> structured field reaches the executor only through `enemy_ai.execute_admin_phase`'s whitelist; the AI's law and edict
> rungs, the shore-up rung and `process_diplomatic_phase` are France-literal by design (an AI France is not a mode).
