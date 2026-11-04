# NEXT SESSION PROMPT — Row AU "Authority as a currency": AU-2b the lumps and the Show (the third of seven slices, before S15)

> Overwritten each time a session hands off. Current hand-over: **November 4, 2026 — AU-2a the hits ✅ LANDED**
> (`docs/AUTHORITY_CURRENCY_SPEC.md` §6.2 the landing record; the rules `SYSTEMS_REFERENCE.md` §170; AU-1 the
> books ✅ LANDED the same day, `6b9d61c4`, §6.1 / §169). The bills are offered in every campaign, never forced,
> each through the one writer with its cause: the Arch-Chancellor's letter at any standing (`bites: "floor"`,
> `bites_since: "AU-2a"`), the Host's Complaint (the Host's Decline priced −2 / −3 / −4 by tier, `since: "AU-2a"`,
> at the floor), the Claims of the Army (`standing.claims_of_the_army` on the dotation tick: fourteen turns
> unpaid while the chest holds twenty turns of his rente, −3 per marshal once per claim, never under 80 on the
> grip after, Berthier presenting on the morning's line), the word broken (`standing.breach` at the end of
> `diplomacy._record_treaty_breach`: −3 a strike, −6 an episode, the debt kept per court) and Make Amends
> repaying it (`standing.amends`, +2 of the debt, never beyond it, the ceiling 95), the quote on the
> war-declaration confirm (`standing.breach_confirm_clause`), the stakes told in figures (`standing.insist_stake_line`
> on both objection paths and the dialog; the vindication's sentences carry their figures). The three seams
> `standing.hits_armed` / `claims_armed` / `breach_armed` (arms AUP / AUK / AUW in `tests/_standing_seams.py`); the
> reach record and the standing record re-measured (the Chancellor 11 → 21 of 58 runs, the Host 20 → 9 — the
> floor's cost —, the Claims 22 bills on 13 runs, the hoarder CMD-A ends at 72); `BASELINE_SERIES` byte-identical
> on six arms (0, AUB, AUP, AUK, AUW, ALL).
>
> **Then the clamp (the user's "Clamp it first", November 4, 2026 — §6.2.5):** the Host's Claims arrive at any
> standing (`bites: "clamp"`, the third mode — allowed only beside a Decline priced besides authority; the
> Chancellor and the Marine keep `"floor"`), the plan takes what lies above 71 and says the rest (AU-7: the
> partial clamp and the grip under the floor said), and the word broken is quoted on every choice that breaks a
> treaty — the manual break's confirm and the alliance paradox beside the declaration (AU-8). Re-measured on the
> same chain; `BASELINE_SERIES` byte-identical on six arms.
>
> **FIRST — the user's review** of AU-2a's seven remaining readings (§6.2.3, 2–8 — reading 1 ruled by the clamp) and
> the clamp's readings (§6.2.5.3) — each one line to reverse. Then AU-2b.
>
> **THEN — AU-2b the lumps and the Show (§5.5, §6; about 1.1 sessions; one commit through the hook; then stop for
> the user's review).** Standing comes back by play, never by waiting — every lump through `standing.regrow`
> (the ceiling 95, the keyed cooldowns in `held`), each parked for the courts behind `standing.courts_move()`:
> 1. **The Te Deum** — in `diplomacy.cleanup_war_end` (the one exit every peace road passes; read before
>    `war_scores` is popped, guarded on `war_over`): a war ended with the lord's war score ≥ +25 gives +4, once per
>    twelve turns per lord (`regrow(..., "te_deum", "te_deum", every=12)`); a truce and a level peace nothing; the
>    Moniteur's line generic ("a Te Deum sung at Notre-Dame"). Key `te_deum`: "the Te Deum for the peace with
>    {court}". Pins: a truce pays nothing; a three-pair settlement pays once; the twelve-turn cooldown.
> 2. **The Bulletin of the Field** — a laurel victory (`jealousy.is_laurel`: out-bled two to one or flawless; never
>    a garrison or a bombardment) gives +4 and repays the field's dents of the last ten turns (+1 per point up to
>    +8, each dent once — the ring's `field_*` / `own_hand_lost` / `assault_repulsed` keys, the repaid marks in
>    `held["bulletin_paid"]`), never a price; one bulletin per three turns; at battle step 12
>    (`combat_executor._post_combat_pipeline`), the garrison seam and the auto-charge mirror. Keys `bulletin`,
>    `bulletin_repaid`.
> 3. **The Return** — the sovereign re-entering his held capital (`diplomacy.sovereign_seat_bonus`'s read) after
>    eight turns afield repays the Council's dents (the `letter_declined` moves whose letter is the Chancellor's),
>    up to 5, each once (`held["return_paid"]`); the morning read of the seat. Key `return`.
> 4. **The honour pays back** +2 when the man honoured wins within eight turns — the honour itself is AU-3a's;
>    land the payback's seam now (`held["honoured:<marshal>"]` read at step 12), inert until AU-3a writes the mark.
> 5. **The Show** — two Acts of the Empire in the scenario's `acts`: the Feast of Saint Napoleon (the decree of 19
>    February 1806: 2,500 gold and one action, +5) and the Arc de Triomphe (18 February 1806: 5,000, +8), once
>    each on a proclaimed road, with a `ceiling` key (95) the validator checks and `imperial_designs.decree` honours
>    through `regrow`; the Temple alone reaches 100 (it keeps `move`).
> 6. **The ceremonies' +2** — the Bavarian Match and the Throne of Holland accepted: a positive `authority` op on
>    the moments' Accept side (the "no rise" guard in `moments._plan_authority` lifted for the MOMENTS alone, bound
>    +5, the ceiling 95 — the affairs' op bound stays −10..0 in the validator).
> 7. The series arm AUS (`standing.sources_armed`) in `tests/_standing_seams.py` and the rig; the records: spec
>    §6.3, `SYSTEMS_REFERENCE.md` §171, `BUG_FIXES.md` §AU's new rows, STATUS's AU-2b line, the plan and the
>    roadmap, this prompt rewritten for AU-2c; the standing record re-measured (`_standing_final.json`); the
>    series expected unmoved (no player battle on the passive board) — measured, not assumed.
>
> **Traps the row has paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231 (seams are
> named functions), functions over 500 lines 28 of 28 (`_execute_diplomatic_declare_war` sits at 497 — compose
> text in `standing`, not in the executor), `WorldState.to_dict` 497 of 500 (every new field on the tracker's
> `held`), CLAUDE.md within 62,000 LF bytes (pay a row by a trim); every `except Exception` must speak
> (`backend.errors.report`); a deck op or clause a slice adds carries `since` / `bites_since` naming its row, so the
> series rig can hold the slice down to the tree before it (`affairs.op_armed`, `affairs.floor_mode`; the validator
> accepts `AU-2a` alone today — extend `affairs.SINCE_ROWS` and `row_armed` for a new row); the validator counts a
> `button_line`'s slots at four and caps the line at 40 (`"auth {a} → {b} · {Host} {c} → {d}"` fits, the full word
> does not); a dispatch event's payload sits under `template_vars`; `_affairs_measure.py --driver-flags` must be
> passed as `--driver-flags="--standing-trace"`; `GET /test` does not pass `build_base_response`; the plan-homing
> pin's SESSION regex knows row AU; the docs are CRLF on disk (LF in the index) — edit through Python on bytes
> with the file's own ending and assert each replacement matches once; `Path.write_text` turns LF into CRLF — write
> bytes; the shell heredoc eats `\b` and `\n` — write patch scripts with the Write tool; the deck JSON files are
> hand-formatted — insert text, never re-dump; the series rig's `prior` is HEAD's baseline (`git show`); attribute
> a series move by event; commit with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the
> background (the hook runs ruff and the full suite, about ten minutes; never `--no-verify`); a Godot engine run is
> one per machine; a cp1252 stdout kills a "→" print — run a probe under `python -X utf8`, never set
> `PYTHONIOENCODING` for pytest; a staged board's letter schedule can move when a hit lands between two letters (the
> Host's Decline at T12 closed the Chancellor's tier-two letter at T17 on the engine's staged board) — attribute,
> never silence.
