# NEXT SESSION PROMPT — Session D: the Awakening, second half — DY-5 + the tier's close (ONE session, ONE commit)

> Overwritten each time a session hands off. Current hand-over: **November 10, 2026 — SESSION C ✅ LANDED:
> THE TIER-6 GATE RULED AND DY-4 BUILT (`SYSTEMS_REFERENCE.md` §203; `DYNAMISM_SPEC.md` §5a the gate record,
> §7 the gate RAISED, §8 row DY-4).** Three rules behind their own seams, ONE sweep with four arms
> (0 / STIR / ULCER / ALL) on three surfaces, the pacing chain re-recorded (the deck changed), ONE commit.
> **The three rulings, delegated by the user ("rule yourself be rigioprous make it good") and made in Plan
> Mode:** Q2 the per-court scalar in `world.moments["awakening"]`, armed by the scenario's `awakening` block
> (the two thresholds authored, 40 / 70); Q3 the ulcer bleeds France too, no player exemption, the player's
> own people stir when invaded; **THE GATE RISES** — story classes ≥ 6 of 10, at least one ambient seed with
> a minor at secondary rank by promotion, the map's roster varying (two distinct (fallen courts, formed
> states) readings) — the second and third UNMET today and content's to earn; a clause still unmet after
> session F goes to the user with no default. **DY-4 as built:** `backend/game_logic/awakening.py` — the
> derived occupied count (never a maintained counter — fifteen writers set `controller` outside the
> chokepoint), the HOUSE read with the boot web (a boot client's soil under its lord is home; a court
> subjugated LATER keeps its boot house, so its new lord's holdings are foreign — Spain under Joseph), the
> bands +1/+2/+3, the cool −1, the lump −10, the dictated peace by rank (+15/+10/+5 inside
> `record_punitive_cessions`), the sovereign captured (+10 in `capture_marshal`), the client squeezed (+5 in
> `change_vassal_autonomy`), the one writer `move` with the beat on a phase crossing (`awakening` log type,
> the census 183 → 184), the ulcer ×0.75 at `_supply_multiplier` before the doctrine's last step, the two
> letters *The People Stir* and *The Ulcer* on the affairs deck (`since: "DY-4"`, `bites: "clamp"`, the
> `awakening` op the twelfth).
>
> **What session C leaves with the user (none blocks D; the readings, honest):** (a) **the march does
> not visibly bleed** — the ulcer taxes the CAP (×0.75 on risen soil) and a corps under the reduced cap
> pays nothing; on the AI-France harness Austria's people rise at 29–31 and Russia's at 36–40 on every
> seed the march reaches, the Estonia turns stand on every arm, France's bill falls 2.2% net (re-routed on
> austerlitz and eylau); the lever, if wanted: a flat attrition on risen soil ("every convoy needs a
> brigade") that bites a lone corps too — session D's option, nothing pre-recommended; (b) **the letters
> never arrive on a measured arm** — no measured France holds a people's soil fourteen turns (the
> commanded arms end with their 28 boot provinces; the Danube script returns Austria's soil at its
> peace), and in the harness the desk's own rule (RE §7: the pick by the LONGEST-STANDING premise, the
> crowding past grace, the cooldown re-armed) seats a people's late-arising stir behind the standing
> bills; the frozen-board pin proves the road (stir at 15, the letter at 18, risen at 25, The Ulcer at 30);
> the lever: a crisis-class priority in the pick, or the letters recast as causal moments anchored on the
> beat — RE's ruled design, the user's call; (c) **the bands' pace** on the ambient board — two provinces
> at +1 a turn: Bavaria stirs at 36–41, the Kingdom of Italy (two provinces under Austria) never in forty
> — N-DY4's numbers, tuneable; (d) **the raised gate's second and third clauses stand UNMET** (no crown
> on any seed; the Kingdom of Italy alone falls, on all ten) — content's to earn in D (the levée: a court
> at war on contested home soil keeps its ground) and Tier 8; (e) **the pacing record's drift**: four
> tiers of world-lines moved 48 of 55 arms' letter timings since November 7 — attributed to the tiers,
> not the Awakening (the attribution arms); the Throne road at austerlitz ends at 36 against its
> control's 40 on the letters arm — the letters alone move ONE road on this tree, where §14 read none.
>
> **NOW — SESSION D (`DYNAMISM_SPEC.md` §2b): the Awakening's second half — DY-5 (the levée, the client
> dial, the interplays), the third letter, the tier's measure chain and close. Nothing new to rule at the
> head beyond the readings above; the plan in Plan Mode; build, measure once with arms, commit once.**
>
> **The build (the contract `DYNAMISM_SPEC.md` §5; §8 row DY-5; tests `tests/test_dy5_the_tiger_ridden.py`):**
> - **The liberation levée** at `get_manpower_regen_rates` (`world_state.py` ~8364; war exhaustion already
>   scales it; laws apply LAST via `reforms.apply_manpower_regen`): the awakened court (≥ `stirring`, 40),
>   at war, home soil contested (`awakening.occupied_count` > 0): infantry regen ×1.5; and the recruit price
>   ×0.75 (the recruit road's price site — `economy_executor._execute_recruit` and the AI's P1 rung read ONE
>   price source; find it, never a second copy). Its own zero-arg seam in `awakening.py`.
> - **The client dial** at `process_vassal_loyalty` (`vassal.py` ~1144) beside `AUTONOMY_DRIFT`: a client
>   whose people are awakened (≥ stirring): loyalty −2 a turn at autonomy ≤ 1, +1 a turn at autonomy ≥ 2 —
>   the tiger ridden; written through the drift's own site, one seam; a rebellion whose cause is the
>   awakening NAMES it (the rebellion's cause field / line — find the producer; `vassal_broke_free`'s words).
> - **The third letter — *The Nation in Arms*** (session C's gate named it, §5a): the player's OWN people at
>   `risen` against an invader — the levée's own letter (Accept: arm the National Guard — the levée's bonus
>   doubled for N turns or a gold cost; Decline: authority); authored in the three-deck lockstep; a moments
>   op added reds `test_moments_pacing.py` until the pacing chain re-records (the deck changes anyway).
> - **The interplays** (§5): awakening ≥ risen as the emergent-designs trigger (`emergent_designs` —
>   Prussia after Jena: a people risen promotes a grievance into a design); an awakened nation lowers
>   coalition friction among its would-be liberators (`coalition.py`'s friction site); an unrecognized
>   crown on awakened soil drifts worse is Tier 8's (DY-7).
> - **The boot-web boundary** (§5a C2) if the client dial needs it: a client that broke free reads its old
>   lord's holdings as foreign already; a client vassalized later by its boot lord again reads home.
> - **The measure chain and the tier's close:** the DY signature (`awakening_events`, `awakened`), chain D's
>   France entry (the Estonia march; France's supply bill per seed), the band, the series; the gate's three
>   clauses read against the record; §2's Tier 6 row and §8's DY-5 row closed; `SYSTEMS_REFERENCE.md` §204.
>
> **The measure — ONE sweep with arms** (clone `tools/_t6_measure.py` → `_t6b_measure.py`; `_t6_series_arms.py`
> → `_t6b_series_arms.py`): arm 0, every DY-5 seam down, MUST reproduce `tools/_dy_signature_t6_2026_11_10.json`
> and arm `ALL` of `tools/_t6_chain_d_2026_11_10.json` byte for byte; one more arm a seam. The pacing chain
> again if the deck changes (`tools/playtest_runs/t6_pacing_2026_11_10/chain.sh` — phases 1–3 and `record`;
> `_affairs_first_arrival_probe.py` rides phase 3; the whole chain ran in 7½ minutes; the reach pins that read
> seeded counts re-seat to the record's truth with the cause attributed by a seams-down phase-1 run).
>
> **The commit:** run the touched families (never the engine lanes), then COMMIT — the hook IS the one
> full-suite run (about 8.5 minutes; do not pre-run the suite). If the hook is red, its failure list is the
> re-pin list. Push is the user's call — ask.
>
> **Session C's own traps (fresh):** a test that takes a court's LAST province walks T4-2's road (the court
> signs at the last, the peace writes the dictated raise) — raise a people on a court with provinces to spare;
> the ulcer composes with France's doctrine clause in Spain (living off the land) — read the ulcer's share
> against the seam held down, never against 1.5 × 0.75; `from_dict` loads `vassals` AFTER the moments install
> (the Europe boot seeds its web in `__init__` and the file carries no `vassals` key) — the boot web is
> snapshotted at the END of `from_dict` (`ensure_houses`), lazily on a hand-built world; Python's `write_text`
> on Windows writes CRLF — the deck JSON files are LF, restore them on bytes; a pytest path that does not exist
> makes xdist collect NOTHING (exit 5, "9 warnings in 3s") — the modding tests are
> `tests/test_modding_validator.py`, not a directory; the driver's `--save-at` files are wrapped
> (`{"metadata", "world_state"}`) and load under `SOVEREIGN_MAP=europe`; the commanded arms (`commanded_full40`)
> end with France's 28 boot provinces and hold NO foreign soil, the Danube script returns Austria's soil at its
> peace, and a passive board retakes a hand-set occupation within four turns — the letters' proof is the FROZEN
> board (the map held, `current_turn` advanced by hand, `awakening.tick` then `moments.tick`, the post read
> each morning through `MO.answer(world, letter, "decline")`); the desk's `pick` goes to the LONGEST-STANDING
> premise and a due letter is crowded out past its grace with its cooldown re-armed — a late-arising premise
> (a people's rising) waits behind the standing bills (RE §7, ruled); `bites: "floor"` needs the Emperor's grip
> at 73 or better, `"clamp"` beside a Decline priced besides authority arrives anywhere; `_s14c_sweep_record.
> mechanical_block` descends into `affairs` — ANY deck edit reds the reach, the pacing and the probe pins until
> the chain re-records, and the reach's seeded-count pins (the Host's 15 on the scripted arms; the Haiti
> squadron's fate line; the armb_scripted sets) move with the world-lines — attribute with a seams-down
> phase-1 run before re-seating; the harness's France (chain D) answers its letters through the AI's dial and
> its `moments_open` column reads the desk; the `awakening` op's quote is in words (phase names), the
> button line "{Host} cools"; the pacing record had not been re-run since T0-H (November 7) and four tiers of
> world-lines had moved 48 of its 55 arms' letter timings under pins that only read the record against itself
> — a forced re-record surfaces every tier's drift at once, so ATTRIBUTE before re-seating (the seams-down
> phase-1 arms `tools/playtest_runs/t6_pacing_2026_11_10/attrib.sh`, the single-road arms for a road that
> moved); Road I answered runs with `--moment accept --affair accept` (the au4 chain.sh lacks `--moment
> accept` — the Crown read "declined" on the accept arms until it was restored); the road record is
> re-recorded by `_vp1_road_arms.py --record tools/_vp1_road_arms_final.json --note "…"` from the SAME armed
> run the reach record's `road_control` reads (the prior kept dated, its bytes pinned); the Throne road at
> austerlitz ends at 36 against its control's 40 with the letters alone on this tree (§14 read none on
> November 7) — attributed to the tiers, with every Awakening seam down.
>
> **Session B's, A's and the earlier traps:** unchanged from the prior prompt — read them in `docs/archive/`'s
> copy of the November 10 hand-over (`git show 93f82fb2:docs/NEXT_SESSION_PROMPT.md`), every one still binding.
>
> **Open with the user beyond session D's head (none blocks it):** session C's readings above; session B's
> three (the envy's cap at the coerce floor too; the crowns after the gift; no second great-power war on the
> 1805 board — the content levers); GRD-38; GRD-37; the design rows of `DESIGN_REFINEMENT.md` §GRD; the
> flip's two readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18); the
> road record's readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions (`REFORMS_SPEC.md`
> §5a); the crown term's level; SF-NAV-1-D1; Britain's letter without contact; the hook's remaining levers;
> `test_ep_f4`'s flake; the two hash-seed orderings with no reader yet checked.
>
> **After session D — the session plan (`docs/DYNAMISM_SPEC.md` §2b; no cuts without consent, spec §0):**
> **E** and **F** Crowns & Recognition (Tier 8's gate + DY-6, then DY-7 + the gate's reading — the raised
> gate's clauses 2 and 3 read there; Tier 7's bounded dice only if the count falls short of 6) → **G: S15 the
> deploy, the user's own**. **After the deploy:** S14k-3 (Spain alone), S16, S17c.
>
> **Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231
> (seams are named functions, zero-arg, in the module they gate), functions over 500 lines 28 of 28,
> `WorldState.to_dict` 497 of 500 (every new field in an existing store), CLAUDE.md within 62,000 LF bytes
> (86 bytes of headroom — session C left it untouched), STATUS at most 7 "▶ ▶ ▶" entries (archive the oldest
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
