# Design Refinement

> **Design items and addons for evaluation.** This is the design-refinement backlog; execution routes through `docs/ROADMAP.md`'s current phase queue. (The old "work begins after `BUG_FIXES.md` is clear" gate cleared April 2026.)
>
> **Last Updated:** August 21, 2026 — **WO-D7..D10 filed** (the zero-battle war that bills both treasuries → EC-2 pass 2; the player's missing truce floor; the objection-economy shape; the exiled Marshalate) by the WO spec-authoring session — **build contract = `docs/WEIRD_OUTCOMES_SPEC.md`**. Prior: August 16, 2026 — **Weird-Outcomes design questions filed (WO-D1..D6, the WO-EVAL docket)**: the funnel (every non-military strategy loses the map), the 1:13.9 battle exchange, vassals and naval as primary strategies, the reward for not fighting, whether a war ever ends on its own, and the missing `capital_lost` headline class; memo `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md`. Prior: August 15, 2026 — **Comprehensive Playtest questions filed** (PC15-D1..D4: neutrality vs broken armies, ally-soil supply, tutorial expectation-dormancy, the exhausted-pair truce floor; memo `docs/audits/PLAYTEST_COMPREHENSIVE_2026_08_15.md`). Prior: August 1, 2026 — **Live-Playthrough design items filed** (PT-D1..D4, from the played-world creative-audit re-measure; memo `docs/audits/AI_V_SWEEP_2026_08_01.md` §10 — PT-D1/D2/D4 share the PT-F6 enemy-phase slice, PT-D3 is copy-level). Prior: July 11, 2026 — **Estate Second Pass deferrals filed** (ESP-1..4, from the ES-7 second-pass design conversation; owner spec `ECONOMY_REVISIT_SPEC.md` §0.6.8). Prior: July 10, 2026 — **Wave 6 APPROVED IN FULL same day it was filed** (+2 gate additions: Dynamic Battle Naming, Literal Doctrine); the build-ready owner is **`docs/WAVE6_FUN_FACTOR_SPEC.md`** (12 slices, blessed default numbers recorded there). Wave 6 items came from `docs/audits/CREATIVE_AUDIT_2026_07_10.md`; live-evidence revisions recorded on R154, R59/R153 (now SUPERSEDED by W6-5), R129/R131/R132, R155/R156, R117 (absorbed into W6-9). Prior: July 2, 2026 present-tense pass. April 16, 2026 rescope context preserved below as history.

---

## Verification-Pass Tie-Ins (FA-N) — filed September 2, 2026 (**ALL OPEN**)

> Found by the verification pass's neighbourhood sweeps. **Both rows below are
> defects in the AUDIT'S OWN prescribed fixes** — applied as written they would
> have shipped as regressions. Report of record =
> `docs/audits/FINAL_AUDIT_VERIFICATION_2026_09_02.md`.

| id | P | item | seam(s) | build shape | behaviour test |
|---|---|---|---|---|---|
| **FA-N17** | P2 | FA-4's own fix_shape, applied as written, breaks the ordinary accept: staging before the pop leaves the offer mounted, so the same-war arm answers with the scope-replace chooser instead of the ratification review verified by running: scratchpad/nb/p11_fixshape.py rebuilds settlement_offers.py:2718-2733's exact `stage_kwargs` for the fixture's real Britain offer (`selected_target = proposer_nation if in covered else covered[0]` -> 'Britain', `caller_kind='ai_system'`, the offer's own terms and covered set) and calls `stage_settlement_confirm` with the offer STILL mounted, i.e. FA-4's reorder: result is `success True, dialogue_type 'settlement_scope_replace_confirm'`, message "Sire, France vs Britain already has a settlement draft for Austria, Britain, Russia. Shall I replace it with the new scope, Austria, Britain, Russia, or keep the current draft?", and `dm.peek()` is the chooser. verified by opening: settlement_staging.py:3392-3404 is the collision arm (different war) and :3405 the same-war arm; … | `backend/game_logic/settlement_offers.py:2734` | ONE seam: settlement_staging.py:3391-3404 — give `stage_settlement_confirm` an explicit `for_war_id` / `ignore_mounted_offer` contract so the collision test is asked about the offer's own war rather than about whatever the queue promoted, and so an offer being accepted is not mistaken for a rival draft. FA-4's accept branch (and finding 1's revision branch) then reorder safely on top of it. Equivalent and smaller if finding 3 lands first: fixing :3405 to require `mounted['type'] == 'settlement_c… | The pin that makes FA-4's reorder safe, written BEFORE the reorder: with an `incoming_settlement_offer` for war X mounted, `stage_settlement_confirm(world, war_id=X, caller_kind='ai_system', settlement_terms=<the offer's terms>, covered_enemy_participants=<the offer's covered set>, selected_target_nation=<the offer's leader>)` must return `dialogue_type == 'settlement_confirm'` in REVIEW mode carr… |
| **FA-N23** | P3 | FA-7's own fix, applied as written, stops bare `next turn` from ending the turn — the trailing-adverb refusal collides with a pinned end-turn synonym the client mirrors verified by opening the row's fix_shape (`plus a trailing-adverb refusing condition (\b(?:later|for now|next turn|tomorrow)\s*[.!]?$)`), backend/ai/llm_client.py:1063-1069 (the clause-guard battery runs at the top of _parse_with_mock) and :1411 (`elif "end turn" in command_lower or "end_turn" in command_lower or "next turn" in command_lower: action = "end_turn"`, ~350 lines BELOW the guards, so a refusal pre-empts it); tests/test_review_2026_08_30.py:688 and :1279-1290 (the three-keyword pin, both backend and client mirror); godot-client/project-sovereign/scripts/main.gd:1288-1301 `_is_end_turn_phrasing` (the client copy, which would not change); tests/data/parser_golden_corpus.json ('end turn' -> action end_turn). Verified by RUNNING, not argued: I monkeypatched strip_condition_clauses wi… | `backend/ai/clause_guards.py:148` | ONE seam, still inside FA-7's own change: anchor the trailing-adverb refusal so it cannot claim a line that IS the whole command. Either require a preceding order clause (the adverb must follow at least one other word that is not part of the phrase — `Ney, attack Mack later` yes, bare `next turn` no), or simply exclude a line whose stripped text is one of the end-turn synonyms before testing the adverb. Do not drop `next turn` from the adverb list: `Ney, attack Mack next turn` must still stop at… | Add to whichever slice builds FA-7: bare `next turn`, `end turn`, `end_turn` and ` END TURN ` still parse to action 'end_turn' with success True and no `refusal` key (this is the existing REV/Aug-30 pin, restated as a regression gate on the new arm); `Ney, attack Mack later`, `Ney, delay the attack` and `recruit later` refuse. Plus a drift pin that the backend's three end-turn keywords and main.gd… — ✅ **BUILT September 2, 2026** with FA-7 (slice 1): a clause that is nothing but the adverb, and is the whole command, is not a deferral — it IS the order. Pinned both ways in `tests/test_fa_slice1_the_two_words_2026_09_02.py` and in the golden corpus. |

| **FA-N38** | P2 | FA-27's own proposed fix is inert on the counter-punch producer — and collides with the standing PT-F6 pin that asserts form_square→attack Verified by running. FA-27's fix_shape is `and self._find_attack_opportunity(marshal, nation, world) is None` at the form condition (enemy_ai.py:1835). That method exists (enemy_ai.py:2673) with exactly that signature — but it is only ONE of the two attack producers that reach `_auto_break_square`. On the counter-punch shape lifted verbatim from `tests/test_ai_square_thrash.py::_counter_punch_shape` (Moore at Normandy, Murat's 40,000 cavalry at Maine, DEFENSIVE, counter_punch_available): `_find_attack_opportunity(Moore,'Britain',world)` → **None**, while `_get_counter_punch_action(Moore,'Britain',world)` → `{'marshal':'Moore','action':'attack','target':'Murat'}`, and the real phase still runs `form_square, attack, fortify, unfortify, attack, attack`. So the gate would not fire and the squa… | `backend/ai/enemy_ai.py:1835` | Still ONE seam (enemy_ai.py:1835), but the predicate must cover BOTH attack producers, not one: `and self._find_attack_opportunity(...) is None and self._get_counter_punch_action(...) is None`. Best extracted as a single named helper (`_will_strike_this_phase(marshal, nation, world)`) so a third attack producer cannot drift in ungated — the same discipline the S5-1 fortify guards already have at all three fortify sites. And reconcile `tests/test_ai_square_thrash.py:176-178` in the same commit: i… | Extend `tests/test_ai_square_thrash.py`: (a) the inertness pin — on `_counter_punch_shape`, assert `_find_attack_opportunity(...) is None` while `_get_counter_punch_action(...)` is not None, so any future gate keyed on the former alone is provably vacuous on this shape; (b) the behaviour pin — after the fix, on BOTH shapes (Moore counter-punch and the FA-27 Charles/Tyrol shape) no `form_square` by… · **FIXED September 4, 2026 — FA slice 4 "The AI Reads the Board" (the square is the LAST word of a phase: P3's postures yield to a wanted square, a formed square ends the corps' phase, `_auto_break_square` sets the cooldown; the filed two-producer gate was NOT built — it double-draws the RNG; landing record `BUG_FIXES.md` §Final Whole-Game Audit, SLICE 4 block; the slice-4 claims audit found this row unmarked)** |
| **FA-N51** | P3 | FA-21's own fix makes the demand SMALLER: the EC-W4 figure collapses through _reduce_p8_demands to a flat 200g with _force_send, because the bilateral acceptance formula prices gold linearly and uncapped while the settlement path caps its harshness term at -45 Verified by opening: `DEMAND_VALUES['gold_lump'] = -3/100` (diplomacy.py:312) summed into `deal_balance = sweetener_total + demand_total` (:7307) and entering the score unclamped (:7499) - a linear, purse-blind, uncapped term; the settlement path by contrast caps its equivalent at -45 (`term_harshness_penalty = -min(45, ...)`, documented at diplomatic_templates.py:4342-4343), which is exactly why EC-W4's purse-scaled figure is affordable there and unaffordable here. `_reduce_p8_demands` (ai_diplomacy.py:913-959) offers exactly one halving (:929-935) and then replaces the whole package with a hard-coded {'gold_lump': 200} plus `_force_send` (:947-958). Verified by running on fixture_t20_ambient: acceptance measured at gold_lump 270 -> 53, 1000 -> -7, 2000 -> -37, 3000 -> -67, 6233 -> -164; … | `backend/game_logic/ai_diplomacy.py:947` | FA-21 needs a second half before it can land, and the honest ONE seam is the acceptance term, not the builder: `DEMAND_VALUES['gold_lump']`'s contribution to `deal_balance` must either be capped (mirroring the settlement path's -45 ceiling) or scaled to the payer's purse, so a purse-proportional indemnity costs a purse-proportional amount of acceptance. Only then does repricing the P8 arm (ai_diplomacy.py:896) produce a LARGER demand rather than a trip to the 200g fallback. `_reduce_p8_demands`'… | Add to tests/test_econ_war_coupling.py beside FA-21's own test, as a precondition that must pass first: on fixture_t20_ambient assert that after `_reduce_p8_demands` the surviving gold_lump is >= 0.15 x France's treasury AND `_force_send` is falsy - this fails today at 200/True and is the falsifiable statement that the acceptance seam has been fixed. Plus a monotonicity pin on the formula: for a f… |

| **FA-N63** | P2 | FA-36's own fix, applied where it says, makes the end-turn interrupt popup swallow the entire turn report — the WIN-H1 defer guard only knows about order-BOUND asks by construction The guard is `_response_has_interrupt_route` (main.gd:2403-2419). Its ONLY defer condition is a loop over `response.strategic_reports` for one with `requires_input` (:2417-2419) — which is the order-BOUND promote at main.py:1316-1321 and nothing else. An order-free ask produces no strategic report at all (`_execute_strategic_turn` returns None at strategic.py:874-876 before the pending-interrupt re-emit at :878-886), so the loop is vacuously satisfied and the predicate returns true. Route order verified by reading: `_post_hud_response_routes` is built at main.gd:1924-1936 with `{"id": "interrupt"}` at index 8 (:1933); `_route_response_ui(response, _post_hud_response_routes)` runs at :2514 and `return`s on a match (:2515 "Don't re-enable input until choice made"); the enemy-phase branch is … | `godot-client/project-sovereign/scripts/main.gd:2403` | ONE seam, chosen so the two halves cannot drift again: main.gd:2403 `_response_has_interrupt_route` — defer on the response carrying a turn report at all (`response.has('enemy_phase')` or a non-empty `strategic_reports`), not on a strategic report happening to want input, and let the reports/enemy-phase flow raise the ask on control return. Equivalently and preferably on the backend side: FA-36's attach should NOT land on `pending_interrupt` for the end-turn response but on a stash-shaped key th… | Two halves, in the WO-35 / WIN-H1 family. Backend (tests/test_wo35_*.py sibling): raise a last_stand on an order-free player marshal, POST 'end turn' through TestClient, and assert the response carries the ask AND still carries `enemy_phase`/`morning_dispatch` — plus a negative control with a MOVE_TO order where the ask rides the strategic report and the key is not duplicated. Client half (the exi… |

| **FA-N88** | P4 | `calculate_state_charges` — documented as "the SINGLE source for the income phase, the treasury report and the ledger (shown = applied)" — has ZERO production callers; the applied path re-derives the formula inline, and all twelve tests pin the dead copy Verified by AST census (`ast.walk` for `ast.Call` over every .py in backend/, tests/, tools/, matching func.attr/func.id): `calculate_state_charges` has 0 callers under backend/ and 12 under tests/ (test_econ_balance_eb.py:178/189/208/210, test_econ_war_coupling.py:239/295/305/320/341/361/369, test_tutorial_scenario.py:82). Verified by opening: world_state.py:5434-5459 is the documented single source, whose docstring at :5444-5447 reads "the SINGLE source for the income phase, the treasury report and the ledger (shown = applied)"; world_state.py:5621-5627 is the income path and re-derives the same arithmetic inline (`_chest = nation_gold - CHARGES_HOARD_FLOOR`; `state_charges = int(_chest * charges_rate["rate"] // WAR_EFFORT_DIVISOR)`) rather than calling it; economy_executor.py:141 and :2… | `backend/models/world_state.py:5434` | ONE seam: `world_state.py:5621-5627`. Give `calculate_state_charges` an optional `rate=None` parameter (defaulting to `self.get_state_charges_rate(nation)["rate"]`, so its 12 existing call sites are byte-identical) and have the income path call `self.calculate_state_charges(nation, rate=charges_rate["rate"])` instead of re-deriving the product — the rate is passed in, so the G4 "never walk the nation's regions twice" note the inline copy exists to honour is preserved. The equally valid alternati… | A join pin that the mutation above currently kills: monkeypatch `WorldState.calculate_state_charges` to return a sentinel (e.g. 12345) and assert that `calculate_turn_income(nation)['state_charges']`, `process_income_phase(nation)['state_charges']` and the applied treasury delta all carry the sentinel — i.e. the applied number is PRODUCED BY the documented single source, not merely equal to it. Pa… |

## FA slice 2 — design item (filed September 4, 2026, from the "No Word Came" build)

| id | P | item | seam(s) | build shape | behaviour test |
|---|---|---|---|---|---|
| **FA-S2-D1** | P3 | **"The Enemy Waits One Turn" — the W6-7 choice is still unreachable when a marshal is cornered in the ENEMY phase.** Slice 2 ended the grind (FA-1: a second defeat with the question standing is answered by the marshal's own character), but the next AI action in the same phase is what answers it, so the player only ever CHOOSES after his own failed attacks. Measured on the shipped board: six Austrian actions in one phase, the question raised by the first and resolved by the second. | `enemy_ai._engageable_enemies` (the P0/P4/P8 predicate slice 2 built) + `_check_marshal_fate`'s ask (stamp `raised_turn` and `raised_by_ai`) | A freshly-asked player marshal (`raised_by_ai and raised_turn == current_turn`) is a non-target for the REST of that enemy phase — every court's phase, since all run in the same `end_turn` — so the question survives to the player's turn; an ask still standing at the NEXT enemy phase is resolved by FA-1's rule as today. Bounded to one turn by construction (never-answer is not an exploit: the province is denied for one turn, then the enemy decides). Changes AI behaviour: a beaten corps at bay is invested, not stormed, for the remainder of the phase. **User gate** — put beside the ROADMAP position-10 queue. Owner: this row; landing slice = one session on the P0 predicate; STATUS line on landing. | `test_fa_slice2_no_word_came_2026_09_04.py` gains: (1) on the shipped board, Massena cornered by Austria's first action survives the phase with the ask standing and ≥1 Austrian action spent elsewhere; (2) the same ask standing at the NEXT phase is resolved (captured or broken out) — the FA-1 pin unchanged; (3) lever False reproduces the slice-2 series byte-for-byte. |

## Final Whole-Game Audit — design & tie-in items (FA-D) — filed September 1, 2026

> **Memo of record = `docs/audits/FINAL_AUDIT_2026_09_01.md` §3d/§3e
> (authoritative); untruncated record =
> `docs/audits/final_audit_2026_09_01_findings.json`.** These are the audit's
> answer to the user's question *"anything that can be added to make things tie
> better"*: 26 joins where one system computes a value correctly and no other
> system reads it. Each row names its two seams and a one-session build shape.
> None is gated on a user ruling; they are sized to be taken opportunistically
> when a slice is already in the file they name.
>
> **⚠ Verification status is per-row in the memo.** The refuter pass ran out of
> budget (memo §0): treat any row the memo marks UNVERIFIED as a lead with cited
> evidence, and reproduce before building.

| id | item | what it would tie together | seam(s) | build shape | behaviour test | verdict (Sept 2) |
|---|---|---|---|---|---|---|
| **FA-D1** | **'The interior is restless' fires on every fresh conquest (capture sets stability 25) and taxes the whole chest without naming the province.** capture_region sets stability = 25 (world_state.py:3877); get_state_charges_rate flags `restless_interior` (+75 rate) when ANY held province sits at/below CHARGES_UNREST_STABILITY 50 (world_state.py:5395-5410, :260). Growth is +5/turn (+10 with a marshal present, :6329-6332), so every conquest opens 3-6 turns of +75 rate on the entire treasury above 2,000. Measured: at a 20,000 chest taking Tyrol raised the Charges of Empire 576 → 1,116 (+540/turn) while the province yielded 0 and billed 75 occupation. The term carries no region (:5407-5409 dict has only key/label/amount) and strategic_ledger.… | The turn the player takes a province, Net falls by ~500-700g with the ledger saying only 'the interior is restless +75'. The visible cost of the conquest is the 75g occupation line; the invisible one is ~7x larger and cannot be traced to the province. In the ambient probe the same term flipped on at turn 12 when an autonomous attack took one provin… | `backend/models/world_state.py:5399` | ONE seam: get_state_charges_rate — collect the triggering region names while scanning (`restless_regions`) and put them on the term dict + label ('the interior is restless — Tyrol'); render in strategic_ledger.gd:455-460 and the end-turn banner. Design half for the EC-2 pass-2 gate: exempt provinces captured within the growth window (stability rising from the capture baseline), or count only homeland/settled provinces, so a conquest's cost is the… | After capture_region of a stable enemy province, assert the restless_interior term dict carries that region's name and the ledger's state_charges_terms label contains it; a second test asserts the charge delta from ONE c… | **NARROWED** (was UNVERIFIED) |
| **FA-D2** | **A war purpose set against Austria ticks into the coalition war score but is invisible on the panel — the row resolves the objective through the LEADER pair only.** `calculate_side_war_score` sums the `ticking` component across EVERY opponent pair of a coalition war (`diplomacy.py:3259-3281`), but `build_active_wars` resolves the row's `objective`/`enemy_objective` through `diplo_key = _make_diplo_key(france, opponent)` where `opponent` is the coalition leader (`war_status.py:56`, `:157`). Verified by running: `set war purpose` vs Austria → `war_objectives == {'Austria\|France': ['France']}` and the row still shows `objective None`; vs Britain (the leader) → `objective {'type':'conquest','target_regions':['London'],...}` renders. So the only renderable Fre… | A player who does discover `set war purpose against Austria` (finding 1) sees nothing change on the War Status panel: no Objective block, no Enemy Objective, no ticking progress line, even though the score is moving. Two implementations of 'which pair carries the war' disagree — the CA9 through-line (the executor computes one answer and the surface… | `backend/game_logic/war_status.py:157` | ONE seam: `war_status.py:152-172` — for a coalition row, walk `row['opponents']` (the pair set the score already sums) and take the first non-concluded player objective, labelling the court it targets (`objective['against']`), and likewise the first enemy objective; single-opponent rows reduce byte-identically. `war_detail_popup.gd:395-407` renders the extra 'against <court>' word. | `tests/test_war_status_coalition_objective.py`: on the 1805 boot, set purpose vs Austria → `wars[0]['objective']['target_regions'] == ['Vienna']` and `objective['against'] == 'Austria'`; set vs Britain → unchanged from t… | **NARROWED** (was UNVERIFIED) |
| **FA-D3** | **An ordinary captured marshal is priced at the peace table and applied by a ratified clause, but no producer ever puts him on it — only a sovereign is.** The `prisoner_return` clause is complete end to end: registered (`diplomacy.py:246`, `:327`), priced per held marshal at 500g / 800g for a major's marshal at the gold-lump rate (`diplomacy.py:7266-7281`), applied on ratification (`world_state.py:10633-10645`) and auto-returned at peace. But the ONLY producer is the NP-4 Brétigny arm in `generate_suggested_terms` (`diplomatic_templates.py:3598-3620`), which `continue`s past every marshal that is not `is_sovereign`. Verified by running: with `ArchdukeJohn.captured_by='France'`, `generate_suggested_terms('Austria','peace',w)` carries zero `prison… | Capturing an enemy commander (the game's own headline: 'their order of battle is one commander shorter') changes nothing at the negotiating table; a captured French marshal's card says only 'held prisoner — his rewards await his release' (`marshal_management.gd:558`) with no route named. The player's one move is full peace, which returns everyone f… | `backend/game_logic/diplomatic_templates.py:3607` | ONE seam: the loop at `diplomatic_templates.py:3607` — drop the sovereign gate and insert a `prisoner_return` for every held marshal of the two courts (sovereign FIRST, then majors' marshals, then the rest, so the Brétigny ordering pin holds); the acceptance formula already prices each one. Optionally mirror in the AI's incoming-offer generator so Austria asks for John back. No new state, no new clause type, no `.gd` change (the clause already re… | `tests/test_prisoner_return_producer.py`: (1) with an ordinary Austrian marshal captured by France, `generate_suggested_terms('Austria','peace',w)['sweeteners']` contains `{'type':'prisoner_return','marshal':'ArchdukeJoh… | **NARROWED** (was AUTHOR_VERIFIED) |
| **FA-D4** | **The campaign's spine war has no purpose — the shipped War Purpose machinery is never staged for the boot coalition war, and the only verb that could set one has no UI home and no counsel.** WPS (war objectives + ticking 5th component + the Objective/Casus-belli block on the war-detail popup) is live for wars the player DECLARES, but `starting_wars` are seeded through `ensure_war_instance_for_pair` without ever calling `create_war_objective` or stamping `stated_reason`, so the Third Coalition — the war every 1805 campaign is about — boots with `world.war_objectives == {}`, `objective: None`, `enemy_objective: None`, `stated_reason: ''` and `ticking: 0` (verified by running `build_active_wars` on the 1805 boot). The player CAN repair this by typing `set war purpose against Austria`… | For 24 turns the War Status panel of the campaign's only war shows no objective, no enemy objective and no casus belli (the popup renders those blocks only when present, `war_detail_popup.gd:395-421`), the war score has no ticking component toward anything, and 'what would winning look like' is never stated. In the flagship digest the player asks `… | `backend/models/world_state.py:8419` | ONE seam: the `starting_wars` loader at `world_state.py:8419-8440`. For each entry, (a) when the player is a belligerent, stage the existing `war_purpose_selection` dialogue on turn 1 by calling `_set_war_purpose_inner(target, '', world)`'s open_flow path (the client already renders it via `proposal_confirm_popup.gd:1277`), and give the AI belligerents `_auto_assign_defense_objective`; (b) stamp `war_instances[...]['stated_reason']` from each AI… | `tests/test_boot_war_purpose.py`: (1) on the 1805 boot the dialogue manager's head is `war_purpose_selection` naming the coalition war, and answering Conquest makes `build_active_wars(w)['wars'][0]['objective']` non-None… | **VERIFIED** (was UNVERIFIED) |
| **FA-D5** | **The redemption audience cannot address its own cause: no arm settles an unpaid expectation, and 'grant autonomy' (+40) is eroded back below 20 in 7 turns.** `_get_available_redemption_options` (disobedience.py:1490-1530) offers only grant_autonomy / administrative_role / dismiss and the event message reads 'trust in you has broken completely. The relationship must be addressed.' (disobedience.py:1561-1564) — it never reads `dotation.get_shortfall` and never offers the rente that `rente_action_keys` (dotation.py:1042) already knows how to build for the rail. Verified by running: after the erosion probe drove Lannes to 0, simulating the spectacular autonomy outcome (`trust.modify(+40)`, turn_manager.py:811) put him at 40 and the unpaid 120g shortfal… | The player is handed the game's gravest marshal decision (dismiss him permanently, shelve him, or release him for three turns) about a cause the card never names and none of the arms can fix; the 'right' answer — pay him — is on a different screen. Choosing autonomy replays the audience within ~12 turns; choosing dismiss deletes a marshal whose onl… | `backend/commands/disobedience.py:1490` | ONE seam: `_get_available_redemption_options` — when `dotation.is_dotation_world(world)` and `dotation.get_shortfall(marshal, world) > 0` and `not dotation.rente_grant_would_not_help(marshal, world)`, prepend a `settle_account` arm whose detail quotes `build_rente_offer` (face + treasury cost) and whose handler in `handle_redemption_response` dispatches the same `{'action':'grant_pension','marshal':name}` dict the UX23-A rail and the AI rung send… | tests/test_redemption_names_its_cause.py: marshal at trust 15 with shortfall 120 -> event carries `settle_account` quoting the rente face; answering it sets `pension`, clears `redemption_pending`, and 10 further `_proces… | **VERIFIED** (was UNVERIFIED) |
| **FA-D6** | **The treaty's road-home order is abandoned by the cannon-fire redirect and never re-issued — a stranded corps wanders and is interned.** WIN-D3 hands every stranded corps an ordinary MOVE_TO (withdrawal.py:654-704, `original_command == ROAD_HOME_COMMAND`). It is an ordinary order to the interrupt system too: `_check_interrupts` (backend/commands/strategic.py:2247-2296) has no `is_road_home_order` exemption and no belligerent filter, and the aggressive redirect (:2298-2307) sets `marshal.strategic_order = None` and marches him toward ANY battle within 2 provinces. The WO-17 direction term (withdrawal.py:141-192, keyed on `is_stranded_at`) admits any step by a corps stranded where it stands, so the 'rush' can go DEEPER into the p… | Verified by running (probe_strategic3.py R): Lannes stranded at Volhynia, peace with Russia → road-home MOVE_TO Franche-Comte (7 marches, grant expiry 11). A Prussia-vs-Russia battle at Estonia (both at PEACE with France): 'Lannes hears cannon fire! Abandoning orders — rushing to Estonia! Lannes moves from Volhynia to White Russia (180 lost to marc… | `backend/commands/strategic.py:2262` | ONE seam: in `_check_interrupts` (strategic.py:2262, beside the literal exemption) `if is_road_home_order(marshal.strategic_order): return None` — the treaty's road is literal by nature. (Belt: have `process_evacuation_grants` re-issue via `_issue_road_home_orders` for an order-less stranded PLAYER corps, so a player-cancelled road is offered again rather than silently lapsing.) | tests: stranded aggressive player marshal with the road-home order + a third-party battle within 2 → after `process_strategic_orders` the order still stands (`is_road_home_order`), the marshal moved one province HOMEWARD… | **VERIFIED** (was AUTHOR_VERIFIED) |
| **FA-D7** | **`propose peace with X` ignores the coalition's settlement offer already on the desk that covers X — drafts, estimates and charges 3 DP while `request terms` refuses for exactly that reason.** `evaluate_request_terms_affordance` returns `offer_already_pending` and the typed route answers 'Their terms are already on the desk, Sire — answer the offer in the mailbox' (settlement_routes.py:318-325; display_names.py:877-884; audit-latewar-t20 T21 verbatim). The bilateral `proposal_confirm` mount (diplomatic_dialogue.py:760-898) checks cooldowns, DP, the ratify gate and the alliance paradox but never `_settlement_offer_already_pending` for the war covering the target, and the send gate (diplomatic_executor.py:680-696, 3919-3936) doesn't either — so with Britain's settlement offer covering… | Two verbs for 'end this war' disagree: one tells the player the answer is in the mailbox, the other takes their DP and sends Talleyrand to Vienna for a bilateral treaty the coalition's own offer already covers. Under the driver's propose policy this cost 3 DP on 12 of 22 turns; a human doing the same is never pointed at the mailbox. | `backend/game_logic/diplomatic_dialogue.py:858` | ONE seam: at the `proposal_confirm` mount (diplomatic_dialogue.py ~858, beside the paradox block) call `_settlement_offer_already_pending(world.pending_settlement_dialogues, war_id=<war covering target>)` / the dialogue-manager equivalent and, when true, disable `execute_proposal` with the same `offer_already_pending` copy the request-terms route uses (honest availability, WIN-1 pattern). | With an `incoming_settlement_offer` current whose `covered_enemy_participants` includes Austria, build the peace `proposal_confirm` for Austria; assert the `execute_proposal` option has `enabled False` and its reason con… | **NARROWED** (was UNVERIFIED) |
| **FA-D8** | **'Gascony has fallen' names no lever while the game has one: an unopposed march captures a homeland province instantly and only a >= 5,000 garrison detachment makes the AI stop.** CONFIRMED mechanism: an unfortified province is captured instantly (combat_executor.py:8287 `_attempt_region_capture`, instant-capture branch at :8328-8330), the AI's march-capture rung already refuses a target with `garrison_strength >= 5000` OR any nonzero `garrison_detachment` (enemy_ai.py ~:3449-3453 — the detachment check makes the counter cheaper than stated), and the player's `garrison` command (economy_executor.py:940-953) is that lever. `home_captured`'s template (dispatch.py:273, sole call site dispatch.py:522) is bare — no captor, no corps strength, no counter-advice. DUPLICATE-ADJA… | A player watching a 4k corps walk Berry→Gascony→Guyenne→Anjou in one phase concludes the map is porous and there is nothing to do; the counter (detach 5,000 into the threatened province, or fortify) is discoverable only by reading the help. | `backend/game_logic/dispatch.py:273` | ONE seam: the `home_captured` template (dispatch.py:273) gains a lever clause built the way VS-1's recovery_hint is — name the enemy corps' strength (fog-banded) and the two counters ('a 5,000-man garrison holds a province against a march; a corps standing there forces a battle'). | tests/test_dispatch_*: the home_captured headline for a province lost to an unopposed march contains the word 'garrison'; a province lost by battle keeps the current sentence. | **NARROWED** (was NARROWED) |
| **FA-D9** | **A corps can stand at morale 0 for eight turns with no cue to the remedy — and then breaks at first contact.** A player-standing corps parked at morale 0 gets the same toothless dispatch line every turn forever, with no auto-recovery and no named remedy. Verified: marshal.py has no per-turn morale regen (only combat.py:704/716 victory bonus and world_state.py:4503-4515 _apply_drill_morale restore it — plus a third, narrower path, backend/ai/feedback.py:126-150's live-mode-only strategic-order bonus, which never fires for an idle/unaddressed marshal). A victor is never routed by the fight he wins (combat.py:796-816, the W6-11 guard), so a corps can sit at floor morale indefinitely without ever being for… | The player reads 'the men waver' turn after turn with no verb attached, does nothing, and loses a 21,000-man corps to the first skirmish it loses; the drill verb that would have fixed it in two turns is never connected to the warning. | `backend/game_logic/dispatch.py:1690` | ONE seam: dispatch.py:1690-1691 appends the lever ('— two turns of drill would steady them' or, with a training ground present, the +15 figure) using the same constants the drill executor applies, shown = applied. | tests/test_dispatch_*: a standing player marshal with morale < 40 and no drill state produces a status line containing 'drill'; one already drilling does not. | **NARROWED** (was PLAUSIBLE) |
| **FA-D10** | **Ally standing rows (contribution_share) live only in the HUD hover tooltip; the War Detail screen never shows them.** war_status.py:241-247 (not 244-249) ships contribution_share/contribution_overflow_count/standing_status_display on every war row; war_status_panel.gd:302-341 (_build_war_tooltip, wired at line 242 as row_btn.tooltip_text) is the ONLY reader; war_detail_popup.gd's _render_war_detail (line 350), which receives the identical war_data dict via show_war() at line 91, never reads these keys despite docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md §16.2 explicitly listing "contribution shares" as required content for the war detail popup surface, not just the war status panel. | Who is carrying the coalition war — the figure that gates who may settle for the side and drives the DG-4 ally petitions — is discoverable only by mouse-hovering a 16px HUD row, and the detail screen the player actually opens omits it. | `godot-client/project-sovereign/scripts/war_detail_popup.gd:349` | ONE seam: war_detail_popup.gd `_render_war_detail` — add a 'Standing' block built from `contribution_share`/`standing_status_display`, extracting the tooltip's row formatter into a shared Utils helper so both surfaces read the same rows. | .gd regex pin that war_detail_popup.gd reads 'contribution_share' inside `_render_war_detail`; backend pin already exists for the producer cap (WAR_SETTLEMENT_ALLY_PARTICIPATION §16.2). | **NARROWED** (was NARROWED) |
| **FA-D11** | **Balance of Europe computes the threat projection (wars until a coalition brews/instant-forms) and never shows it.** diplomatic_ledger.py:1041 (war_exhaustion_trend build), :1061-1074 (threat_projection dict, matches coalition.py:41-42 THREAT_BREWING_MIN=60/THREAT_INSTANT_MIN=80), and :1115 (dissolution_threat_threshold, not :1096-1103 as originally cited) build threat_projection/wars_until_brewing/wars_until_instant/war_exhaustion_trend/hegemony_band/power_basis and a duplicate top-level coalition_posture key that godot-client/project-sovereign/scripts/diplomatic_ledger.gd's _render_balance_of_europe() (func at line 749) never reads (0 grep hits for any of those keys). Fix seam gd:846 (right after the threa… | The tab says 'Threat Level: 47 / 100 [MODERATE]' and lists this turn's sources, but never the one number a player plans around — 'one more war of conquest and a coalition brews; two and it forms at once' — nor which coalition member is tiring. The system knows; the screen withholds it. | `godot-client/project-sovereign/scripts/diplomatic_ledger.gd:846` | ONE seam: diplomatic_ledger.gd `_render_balance_of_europe`, after the threat bar (~:846): one line from `threat_projection` ('Next war of conquest: 47 → 67 · brews at 60 (1 war away) · forms at once at 80 (2) · dissolves below 20') and a ▲/▼/– glyph from `war_exhaustion_trend` beside each member's WE bar. Before rendering `after_next_war`, confirm the +20 literal at diplomatic_ledger.py:1063 equals the `war_declaration` threat increment so the li… | Backend pin: `build_diplomatic_ledger(world)['balance_of_europe']['threat_projection']['wars_until_brewing'] == max(0, ceil((60-threat)/20))` and `brewing_threshold == coalition.THREAT_BREWING_MIN`; client: .gd regex pin… | **VERIFIED** (was PLAUSIBLE) |
| **FA-D12** | **No headline class for the player's OWN peace — the war's end leads the briefing only when a corps happens to be stranded.** CONFIRMED and strengthened. `_build_headline`'s event-window loop (backend/game_logic/dispatch.py:429-1050ish, scanning `world.event_log`) has no `elif etype == ...` branch for `diplomatic_treaty_signed`, `peace_ratified`, or `armistice_expired_peace` — verified by reading the whole loop (region_captured/nation_eliminated/marshal_captured/marshal_destroyed/retreat/battle/war_declaration/evacuation_granted/evacuation_lapsing/crisis_brewing/crisis_passed/third_party_peace/coalition_formed are the only cases; the state-based candidates that follow — enemy_on_our_soil/estate_eroding/supply_strain/… | The player who spends three turns of DP suing for peace can sign it and open a briefing whose first line is a supply nag; whether 'the war is over' ever leads depends on where his marshals happen to be standing, not on the peace. | `backend/game_logic/dispatch.py:806` | ONE seam — `_build_headline`: raise a `peace_signed` class (weight ≈70, the mirror of `war_touches_us`) from the same `peace_ratification_log` entry `_build_peace_settlement_section` already reads (dispatch.py:3661-3672) or the treaty event, when the pair includes the player and the new state is PEACE/ARMISTICE; let `road_home` absorb it by identity when both exist. | tests/test_dispatch_headline.py: ratify a bilateral PEACE with no French corps abroad and no other events → `_build_headline` returns class `peace_signed` naming the counterpart; with a stranded corps only `road_home` re… | **VERIFIED** (was PLAUSIBLE) |
| **FA-D13** | **No per-corps march cadence: one AI corps captures three homeland provinces per enemy phase while the player's own standing march moves one.** DUPLICATE-ADJACENT to PT-D4 (`DESIGN_REFINEMENT.md`, LANDED Aug 1 2026, `backend/main.py:1020 _collapse_enemy_move_chains`): P4.5's undefended-capture chain (enemy_ai.py:1039 round-robin loop → `_find_undefended_capture` enemy_ai.py:3380, single-hop scan of `adjacent_regions`, returns `{"action":"attack",...}` at :3498; prose at combat_executor.py:5034 inside `_execute_attack` def :4112) is mechanically confirmed and reproducible (player chain of 3 tactical `move`s costs AP 4→1 with no per-hop cap — GR5 holds; France boots with garrison only at Paris/Normandy/Flanders across 28 provinces). The… | A 5,000-man landing party overruns nine French homeland provinces in five turns with the dispatch reading 'X has fallen' every morning, while the player's own 'march to' orders crawl one province a turn; the only counter — a 2-AP garrison detachment per province — is invisible as such. It reads as the AI cheating even though the executor is symmetr… | `backend/ai/enemy_ai.py:1039` | A design ruling, then ONE seam either way: (a) cap tactical relocations per marshal per turn at `movement_range` in `_execute_move` and the unopposed-attack arm using the existing `acted_this_turn`/`moved_this_turn` flags (both sides inherit, P4.5 falls through to the next marshal); or (b) extend `occupation_started` (the fortified-province cadence at combat_executor.py:5037) to a nation's HOMELAND provinces so a walk-in flips control on the next… | tests/test_enemy_ai_*: an AI nation with 4 AP and one corps adjacent to three undefended enemy provinces ends its phase having captured at most `movement_range` of them; player mirror: the third chained `move` of the sam… | **DUPLICATE** (was NARROWED) |
| **FA-D14** | **One corps flips a homeland province per AP with no resistance — Paget's 3-province walks are the game's capture cadence, symmetric for the player.** An `attack` on an empty at-war province is `move_to` + instant `_attempt_region_capture` (backend/commands/combat_executor.py:5006-5051; :8306-8330 — instant unless a `fortification` building), costing 1 AP and ~1% march attrition. The enemy AI's P4.5 (`_find_undefended_capture`, enemy_ai.py:3380-3470) is re-evaluated every action of the nation's 4-AP loop (:945, :1039-1215) whose `sort_key` (:1409-1418) is fairness-only — no per-marshal cap — so Britain's single continental corps spends all four. Nothing about a province (stability, homeland, garrison-less capital neighbour) slows the flip. P… | Archived: audit-latewar-t20 lines 13-16 — 'Paget marches from Berry into Gascony unopposed! (95 lost to march) … from Gascony into Guyenne … (46 lost) … from Guyenne into Anjou … (46 lost)' in ONE enemy phase; lines 108-111 Normandy→Artois→Picardy→Ile-de-France likewise. Verified by running the player side at boot: Lannes (17,820 men) at Franconia… | `backend/commands/combat_executor.py:8313` | A design ruling first, then ONE seam: `_attempt_region_capture` (combat_executor.py:8313-8326) already owns a 1–2-turn occupation timer for fortified provinces; key that same timer on a high-stability province (`region.stability >= 76` is already 'friendly stable' at movement_executor.py:75-78) or on homeland/capital-adjacent soil, so a stable province takes a turn to fall (both sides, GR5) and the defender gets a response turn. Presentation comp… | tests (after the ruling): a corps attacking an empty stability-80 enemy province gets `occupation_started` (1 turn) rather than an instant flip, for the player AND for an AI marshal through the shared executor; a stabili… | **DUPLICATE** (was UNVERIFIED) |
| **FA-D15** | **Settlement-unavailable reason is computed for the War Detail row and never rendered — 'Open Settlement' just vanishes.** war_status.py:250-264 attaches settlement_eligibility/settlement_disabled_reason/settlement_disabled_reason_display/war_detail_actionability to every war row, and no .gd file (0 of 55) reads any of them; war_detail_popup.gd:108-109's `if settlement_available: _add_settlement_button(...)` has no else, so the button silently vanishes with no rendered reason (confirmed against the Request Terms disabled+tooltip idiom at :556-569, which the settlement button lacks). BUT the reason this fires is never 'settlement_dialogue_active' — war_status.py:773 always passes `ignore_active_dialogue=True` into… | When a settlement review is already open for another war, when France is not her side's leader, or when the war instance changed under the open review, the Open Settlement button silently disappears from the war detail with no sentence anywhere; the player concludes settlement is impossible with that court rather than 'resolve the other review firs… | `godot-client/project-sovereign/scripts/war_detail_popup.gd:108` | ONE seam: war_detail_popup.gd `show_war` — in the else-branch of :108, when `settlement_tier_display` is non-empty (settlement-tier war) render a disabled 'Open Settlement' button whose tooltip_text is `settlement_disabled_reason_display` (the :561-567 Request Terms idiom); keep bilateral codes (`one_to_one_war`, `not_at_war`) absent since Negotiate is their route. | Backend: `build_active_wars` on a coalition war with an active settlement dialogue → row.settlement_available False and settlement_disabled_reason_display == 'Resolve the current settlement review first.' (pin the join).… | **VERIFIED** (was NARROWED) |
| **FA-D16** | **The 15,000 lift makes the Emperor's Guard the only French expedition corps — and the Marshalate, the real road, is never named.** At boot every French corps but Napoleon (10,000) exceeds the lift, so `over_lift_refusal` (naval.py:597 `eligible`) says 'Send a corps of 15,000 or fewer instead — Napoleon stands at 10,000' and the Admiralty expedition term (naval.py:2157-2168) says 'march Napoleon (10,000) to a yard'; the comment at :2160 promises the copy 'says plainly when the only one is the sovereign' but no code does, and the executor has no sovereign gate. Meanwhile `recruit_marshal` fields a 5,000-man corps (recruitment.py:32 `RECRUIT_MARSHAL_CORPS = 5000`) at the capital — the one verb that MAKES an under-lift corps… | The only expedition advice a French player receives is to ship the Emperor to Ireland at 64% odds with a 30% interception loss; the affordable, historical road (commission Mortier/Suchet for 3,500–6,000g, march 5,000 men to Brittany, sail) is discoverable only by accident. WO-D3's 'zero naval operations in 30 turns' has this as a cause. | `backend/game_logic/naval.py:597` | In the ONE builder both surfaces read (`over_lift_refusal` and the `_under` list feeding term 2), exclude `personality == sovereign` from the offered corps and append the commission road from `recruitment.first_affordable_commission(world, nation)` ('commission Mortier — 5,000 men for 4,000g — and march him to Brittany'); optionally the same helper on the Generals bench chip ('under the transports' lift'). | test_expedition_counsel_names_the_marshalate_not_the_emperor: at boot the over-lift refusal and expedition term never name Napoleon, and name the cheapest affordable bench marshal with '5,000'; with an under-lift non-sov… | **NARROWED** (was UNVERIFIED) |
| **FA-D17** | **The alliance-paradox block names a route France cannot execute and omits the one the executor exempts; the Cabinet's 'Propose Peace' row stays green while its send is structurally blocked.** CONFIRMED core mechanism, NARROWED framing: propose_peace never appears as a wizard action while state=="WAR" (diplomacy.py:10987 shows propose_armistice is the ONLY proposal row added in that branch; verified by running get_available_diplomatic_actions on the 1805 boot). The real gap is one state later: once the player follows the game's own counsel and signs an ARMISTICE (Bavaria remaining allied to France and at war with Austria), get_available_diplomatic_actions's `elif state == "ARMISTICE":` branch (diplomacy.py:11093) adds propose_peace via `_proposal_action` (diplomacy.py:10839-10944),… | Every player who tries to make peace with Austria while Bavaria is an ally at war with Austria (the 1805 boot) picks a live green Cabinet row, drafts terms, and is stopped at the confirm with one executable route (the settlement table) and one non-executable one; the cheapest working door — a bilateral armistice whose expiry auto-peaces — goes unme… | `backend/game_logic/diplomatic_dialogue.py:870` | ONE seam: the block-text builder at diplomatic_dialogue.py:868-873 — name the armistice explicitly ('propose an armistice — a truce carries no contradiction, and its expiry makes the peace — or settle jointly at the table') and drop the non-executable 'resolve X's war first'. Companion (same discipline as the settlement row): `_proposal_action('propose_peace')` marks the row unavailable with the paradox reason. | tests/test_bph_c_fallout_conflicts.py: with Bavaria allied to France and at WAR with Austria, the peace mount's `commitment_block_warning` contains 'armistice'; `get_diplomatic_preview(world,'Austria')['actions']` has `p… | **NARROWED** (was NARROWED) |
| **FA-D18** | **The armistice preview promises a peace the thaw arithmetic cannot deliver: from the boot relations a single 5-turn truce always collapses back into war.** backend/game_logic/diplomacy.py:4368-4410 (build_war_context_snapshot's armistice_mechanics block) AND backend/game_logic/war_status.py:373-374 (armistice_projected_outcome, feeding war_status_panel.gd:359 / war_detail_popup.gd:511, the per-turn HUD) both project an armistice's outcome from relation_now >= ARMISTICE_AUTO_PEACE_RELATION alone, ignoring the turns remaining and the ARMISTICE_THAW_PER_TURN=3 thaw that runs every turn a truce is active (diplomacy.py:10411). Verified live: 3 turns into an Austria armistice (relation -71, 2 turns remaining), both the shipped check and a naive multipl… | The player takes the counselled armistice with Austria (−80), reads 'unless they heal to −60 or better', watches five turns pass with nothing to do, and gets 'The armistice with Austria has collapsed. War resumes!' — the war score and battle records having been struck at the truce (the preview's own line says so). The number that would have told th… | `backend/game_logic/diplomacy.py:4370` | ONE seam: the projection block at diplomacy.py:4368-4380 — compute `projected = relation_now + ARMISTICE_THAW_PER_TURN * ARMISTICE_DURATION`, set `projected_outcome` from it, and say it: 'Relations stand at −80 and will thaw to −65 by expiry — short of −60; the war resumes unless relations improve by other means, or a second truce follows.' | For relation −80 the armistice snapshot's `projected_outcome` is 'war' and a display line contains '-65'; for −72 it is 'peace' (−72 + 15 = −57 ≥ −60); pin `ARMISTICE_THAW_PER_TURN * ARMISTICE_DURATION` is what the copy… | **NARROWED** (was NARROWED) |
| **FA-D19** | **The player's `garrison` verb feeds no stability — the 'garrison bonus' in stability growth reads marshals only, while the vassal-loyalty garrison predicate DOES count a detachment.** `process_stability_growth` documents 'Garrison bonus: +5 if a friendly marshal is present' and implements it via `_has_marshal_in_region` (`world_state.py:6330`, `:6648-6653`), which ignores `region.garrison_detachment` — the flag the `garrison` verb sets (`economy_executor.py:976-979`). VP-D1's `lord_garrison_present` (`vassal.py:444-452`) explicitly counts 'a real garrison (`garrison_strength` > 0 — the detachment corner)'. Verified by running on the 1805 boot: a France province at 40 with a 5,000-man detachment and no marshal grows to 45 (same as nothing); with a marshal, 50; Austria's deta… | On a fresh conquest (stability 25–35) the depot gate needs 51+ (`region.py:185-187`) and recruits refuse below 51 (`economy_executor.py:619-623`); the flagship dispatch at t10 (line 166) says 'No depot may be laid at Tyrol — region stability too low (35/100). Need 51+.' The one verb literally named for the job — leave a garrison — does nothing for… | `backend/models/world_state.py:6330` | ONE seam: `world_state.py:6330` — `garrison_bonus = 5 if (self._has_marshal_in_region(...) or (region.garrison_detachment and region.garrison_strength > 0)) else 0`, sharing the detachment arm with `lord_garrison_present` (extract one `has_friendly_garrison(world, region, nation)` predicate both read). Mechanic change on both sides: expect a `BASELINE_SERIES` attribution run (flip lever idiom) since the AI garrisons at P6.75. | `tests/test_stability_garrison_detachment.py`: a detachment-only France province grows +10/turn; the same for an Austria province (GR5); a detachment with `garrison_strength == 0` grows +5; the vassal predicate and the s… | **NARROWED** (was AUTHOR_VERIFIED) |
| **FA-D20** | **The strategic parser knows join / link up with / aid / assist / bolster as SUPPORT, but the mock chain only fires on reinforce/support — so "Ney, join Davout" is Unknown and "Ney, protect Davout" becomes a 2-AP HOLD 'at' a man.** strategic_parser.py:302-308 (dict key at 302, verb entries 304-308) lists \"come to the aid of\"/\"link up with\"/\"assist\"/\"aid\"/\"bolster\"/\"join\"/\"back up\"/\"shore up\"/\"rally to\"/\"combine with\" under SUPPORT, and the near-identical SUPPORT_OBJECT_PREFIX_RE (llm_client.py:101-105, not 104-109) recognizes the same verbs for CR-2 object-prefix stripping — but the mock action chain's only SUPPORT arm, llm_client.py:1598 (`elif \"reinforce\" in command_lower or re.search(r'\\bsupport\\b', command_lower): action = \"move\"`), only fires on \"reinforce\" or bare \"support\". parser.py'… | Verified by running: `Ney, join Davout`, `Ney, link up with Davout`, `Ney, aid Davout`, `Ney, help Davout`, `Ney, go help Davout`, `Ney, cover Davout`, `Ney, cover Davout's flank`, `Ney, screen Davout`, `Ney, follow Davout` → "Unknown action"; `Ney, protect Davout` → "Ney will hold Davout. Ney: 'Standing guard while others win laurels…' (2 AP — a s… | `backend/ai/llm_client.py:1598` | ONE seam: make the llm_client.py:1598 arm read the SAME verb tuple strategic_parser's SUPPORT table uses (export it from strategic_parser and reference it), and let the hold arm yield to SUPPORT when the object after guard/protect/cover is a friendly marshal name. | each of join/link up with/aid/assist/bolster/come to the aid of/cover/screen + Davout → strategic_type SUPPORT, target Davout; `Ney, protect Davout` → SUPPORT not HOLD; `Ney, protect Rhineland` / `guard Lorraine` stay HO… | **✅ BUILT September 4, 2026 (FA slice 7)** (was NARROWED) |
| **FA-D21** | **Trafalgar cannot lead the Morning Dispatch.** Naval beats ('trafalgar'/'fleet_action', logged by `naval._log_fleet_action`, naval.py:1246-1261) reach the player ONLY through `queue_dispatch_event` → `world.pending_dispatch_events` → `_build_diplomatic_events_section` (dispatch.py:4339) as a DIPLOMATIC EVENTS rail line at priority HIGH (`_DIPLOMATIC_EVENT_PRIORITY["trafalgar"]`, dispatch.py:4073). The separate headline scorer `_build_headline` (dispatch.py:429) has no `_add()` call site for either event type and `HEADLINE_WEIGHTS` (dispatch.py:57) has no naval class at all, so a decisive fleet action can never be the morning headline — con… | The campaign-defining naval catastrophe reads as a footnote below 'Leon has been taken by Britain'; the war's biggest single loss of the run has no lead sentence. | `backend/game_logic/dispatch.py:57` | ONE seam: add a `trafalgar` headline class to HEADLINE_WEIGHTS (~90, between region_lost 75 and marshal_captured 95) built by `_add` from the `trafalgar` event when the loser is the player's side; keep the rail line as the sub-beat. | After a decisive fleet action lost by the player, `build_morning_dispatch(world)['headline']['text']` contains 'TRAFALGAR'; after a non-decisive action it does not. | **DUPLICATE** (was PLAUSIBLE) |
| **FA-D22** | **'Grievance' means two different things on two adjacent surfaces.** The dispatch's terminal ES-7 dotation-shortfall escalation line (dispatch.py:234-235, the THIRD variant in `_STANDING_ESCALATION[\"estate_eroding\"]`, reached and then clamped-persistent for any neglect streak >=5 turns per the selector at dispatch.py:1172-1180) says \"Marshal {marshal}'s grievance is {turns} turns old\" for a dotation/pension shortfall — reusing jealousy's established term-of-art: \"grievance is satisfied/settled\" (jealousy.py:1188,1340; campaign_log.py:1466) and the Generals card's \"GLORY & GRIEVANCES\" / \"GRIEVANCE: envious of X\" row (marshal_management.gd:481,495), whi… | The player looks for a rival to appease and finds none; the actual remedy (rente/estate) is a different verb on a different surface. | `backend/game_logic/dispatch.py:233` | ONE seam: the three `estate_eroding` escalation strings in dispatch.py:229-235 — use the dotation vocabulary the rail already uses ('arrears', 'unrewarded', 'claim') and reserve 'grievance' for jealousy. | tests/test_dispatch_vocabulary.py: render the third `estate_eroding` variant and assert 'grievance' is absent; render a jealousy confrontation title and assert the word is present there. | **VERIFIED** (was NARROWED) |
| **FA-D23** | **AI marshals' trust is read by nothing on the AI path, yet the AI pays rentes and gives away provinces to stop an erosion that never bites it.** `_process_dotation_state` erodes ALL nations' marshals (world_state.py:6075 loop, GR5) and enemy_ai.py spends on `grant_dotation`/`grant_pension` to close shortfalls (enemy_ai.py:5722-5760; ambient40 digest lines 37, 47, 232 show the AI verbs firing). But trust's only mechanical readers are player-side: objections skip enemy marshals (`is_player_action_check`, executor.py:1130-1175), defiance rides objections (defiance.py:41-47), severity.py:118-125 feeds objections, and `grep -n trust backend/ai/enemy_ai.py` finds only a comment (line 194). Coordination/arrival read jealousy and relationships… | Invisible today, but the asymmetry means an enemy court with a dozen unpaid, Broken-trust marshals fights exactly like one with Loyal ones; the player cannot exploit or even perceive an enemy army's disaffection, and the AI treasury is drained for a stake that does not exist — 'same systems, different input values' holds on the cost side only. | `backend/ai/enemy_ai.py:5722` | Give trust ONE consequence both sides share, at the seam that already scales a marshal's contribution by his grievance: `CombatExecutor._pair_contribution_scale` (the jealousy weight the petition card quotes) gains a HOSTILE-tier (trust<30, objection_v2.get_trust_tier) factor, so a Broken marshal brings less to a colleague's field on either side; the AI rung then buys something real and the player can read enemy disaffection off the same rule. | tests/test_trust_contributes_both_sides.py: two-marshal reinforcement, Austria: the committed effective strength with the reinforcer at trust 10 is lower than at 70; identical for France; M1-M7 harness re-measured and re… | **VERIFIED** (was UNVERIFIED) |
| **FA-D24** | **Berthier's battle observation is drawn with unseeded `random.choice`, so one enemy phase can print the same observation twice while enemy voice rotates.** `_pick_observation` (backend/game_logic/battle_report.py:617, invoked from combat.py:1022/1463 inside the world-independent `CombatResolver.resolve_battle`) draws Berthier's after-battle line via unseeded `random.choice` across ~30 priority-branch banks, causing verbatim repeats within one enemy phase when the same priority branch fires twice for the same marshal pair — reproduced in docs/audits/playtest_digests/audit-latewar-t20/digest.md:112 and :115, identical "lost_despite_terrain" line against Archduke Charles. XR-5 (BUG_FIXES.md:2995, closed) fixed the identical class of defect in `enemy… | On a multi-attack night the staff's one editorial line per battle repeats verbatim under consecutive battles, which reads as a stuck record in the very dialog CA8-7 made the antagonist's stage. | `backend/game_logic/battle_report.py:748` | ONE seam: pick by index `(world.battle_counts.get(pair_key,0)) % len(bank)` through a small `_rotate(bank, key)` helper in `_pick_observation`, the XR-5 idiom, passing the existing `battle_result` pair key. | tests/test_marshal_voice_tier1.py (or a new battle_report test): two consecutive battles between the same pair with the same outcome yield two different observations from the same bank, and the sequence is byte-identical… | **VERIFIED** (was NARROWED) |
| **FA-D25** | **Every question dumps the whole COMMAND REFERENCE — "where is Mack?" / "who is at Swabia?" / "what is Davout doing?" get help text although `status` already answers them.** DUPLICATE of CR-8/CR-6 (COMMAND_ROBUSTNESS_SPEC.md:57 and :317-319): backend/ai/llm_client.py:1258 routing every question to `help` is a documented, INTENTIONAL, gated design decision, not an overlooked join — the spec states verbatim that a question-answering Berthier (CR-8's advisory desk, or CR-6's classifier) is what replaces the `help` route, and both sit behind their own USER DESIGN GATE, still unbuilt. Verified live: all 7 repro questions ('where is Mack?' through 'should Ney attack Mack?') do return the COMMAND REFERENCE text; 'can Ney attack Mack' (no '?') fires a real attack confirm;… | Verified by running: `where is Mack?`, `who is at Swabia?`, `what is Davout doing?`, `is Mack fortified?`, `how far is Vienna from Ney?`, `Ney, can you reach Munich this turn?`, `should Ney attack Mack?` → all print '═══ COMMAND REFERENCE ═══ MILITARY COMMANDS: attack…'. Meanwhile `can Ney attack Mack` (no '?') and `will Ney attack Mack?` are execu… | `backend/ai/llm_client.py:1258` | Cheap join at the same seam: when `is_question` fires AND the sentence names a known marshal/enemy/region, return action `status` (or the intel report filtered to that name) instead of `help`; keep `help` for questions naming nothing. The CR-8 two-way channel remains the full answer. | `where is Mack?` → action status and a fog-honest line naming Swabia at boot; `how do I attack?` still → help; `will Ney attack Mack?` is treated as a question (no battle). | **✅ BUILT (the fact half) September 4, 2026 (FA slice 7) — advice and feasibility stay CR-8's** (was DUPLICATE) |
| **FA-D26** | **The Ledger economy tab's Net omits the Materiel bill — the only component the applied identity needs, and the ledger screen has no row for it.** DUPLICATE-IN-SUBSTANCE of N11/PT-C4 (docs/BUG_FIXES.md:1399, tier-2-landed per :1360; docs/PLAYTEST_FIXES_SPEC.md:242 "not fully closed"), narrowed to the one surface that fix left untouched. `backend/game_logic/dispatch.py:2271-2290` already fixed the identical gap for the Morning Dispatch by calling `_build_economy` in APPLIED mode and labeling the result `treasury_delta_label = "by the accounts"`, with an explicit comment that the EC-W3 Materiel bill is "charged outside Net by design (the plunder-gold precedent)" — a deliberate, tested exclusion (`tests/test_economy_ledger_reconciliation.py… | The player opens the ledger, reads 'Net +2,131', ends the turn and finds the chest up 1,764; nothing on that screen explains the 367 (the banner does, once, in a scrolling terminal). Over a 24-turn fighting campaign the gap compounds into thousands of gold the ledger never accounted for. | `backend/game_logic/ledger.py:411` | ONE seam: _build_economy returns `materiel` (read from world.materiel_spent_this_turn in applied mode, 0 in projection mode) as a signed informational line; strategic_ledger.gd renders 'Materiel (last turn): -Ng' under Net with the note that it is charged at the battle, not in the accounts. | After one fought turn, _build_economy(world, player, income_data=applied)['materiel'] equals world.materiel_spent_this_turn[player], and treasury delta == net − materiel exactly. | **NARROWED** (was NARROWED) |
| **FA-D27** | **GATE (slice-4 review round, Sept 4, 2026): does the AI now beat an unattended France, and is that wrong?** Measured by the round's balance lens (`docs/audits/fa_build_2026_09_04/REVIEW_slice4_R2_balance_measurement.md`) on the slice-4 board: an unattended France is overrun on 8/8 seeds (≤ 5 provinces by turn 23–27, threat zero by 28–33; seed means Fr@30 16.2 → 3.9, Fr@40 9.5 → 2.2) and a scripted, fighting France on 5/5 arms (turn-40 provinces {27, 29, 27, 16, 27} → {14, 8, 11, 6, 10}); the slice-4 levers act JOINTLY (B alone 6, the other eight together 27, all nine 2). The round's own eight defect fixes then moved the passive board back to France 5 with no French corps captured, touching no number. The reviewer's reading stands: nothing shows the AI "too strong" rather than "finally not wasting a third of its actions". | Balance is the user's call. Options on the table, none built: (a) leave it — the next PLAYED campaign (a human recalls corps, sues for peace, answers landings; the scripts cannot) is the measurement that matters; (b) a France-side lever (starting AP, treasury, or the CR/strategic AP cost) rather than dulling the AI; (c) an AI aggression dial keyed to difficulty. Whatever is chosen, re-run `tools/ai_v_sweep.py` and the balance lens's three scripts before and after. | `docs/audits/fa_build_2026_09_04/REVIEW_slice4_R2_balance_measurement.md` §1–§3 | **OPEN — GATE**, filed by the slice-4 review round |
| **FA-D28** | **GATE (slice-4 review round, Sept 4, 2026): a detachment garrison costs ⌈log₂ N⌉+1 assaults and a fifth to a half of the ATTACKER however large he is.** Pre-existing; `combat_executor.py::_resolve_garrison_combat` caps `garrison_damage_ratio` at 0.50 per assault and floors the attacker's losses at 2% of his OWN strength (WO-3 fixed only the 1-man stall). Lever A (slice 4) now steers the AI into exactly these fights. Measured (`garrison_repro.py`, `PYTHONHASHSEED=0`): a 40,000-man Kutuzov vs a French detachment of 3,000 → 13 assaults, 40,000 → 29,844; of 12,000 → 15 assaults, → 24,973; of 25,000 → 16 assaults, → 16,570. A corps that outnumbers the garrison 13:1 loses more men than the garrison had; live, thirteen assaults over two turns by three corps of two nations to clear one 3,000-man detachment. | Combat-balance change → gated. Fix shape: scale the garrison damage with the odds (≥ 4:1 → the detachment falls in one assault; the 0.50 cap keeps only for a capital's own garrison) and floor the attacker's losses on the GARRISON's size, not his own. Golden Rule 1 territory: the numbers live in `_resolve_garrison_combat`, shown = applied on the garrison line. Pin: the three measured cases above as a before/after table; M1–M7 unaffected (the harness never resolves a garrison). | `backend/commands/combat_executor.py::_resolve_garrison_combat` | **OPEN — GATE**, filed by the slice-4 review round (R2 defect 1) |
| **FA-D29** | **A 500-man stub in a garrisoned province is a P4 sink and the garrison is never assaulted while it stands** — P4 prices the province's visible field, never the CO-1 reinforcement that arrives: a 100k Wellington attacks a 500-man Ney in Paris (garrison 15k, a French corps adjacent), Davout's 48k relocates as a reinforcement, Ney loses 2 men, Wellington −1,331; next turn the same (100,000 → 88,113 over two turns, the stub at 495). With no adjacent friend the stub dies in two blows and P4.25 fires. Not a regression (the old rung's garrison assault resolved as the same field battle); FA-8's skip makes "a stub shields the garrison" absolute. | Larger than a review round: P4's field price should include what `_calculate_reinforcements` will commit from adjacent provinces — the player's muster preview already computes exactly this. Same price seam as FA-8 / CA9-N6 (`_defending_strength_in_region` at P0/P4/P3.25/P7.5). | `backend/ai/enemy_ai.py` P4 (`_find_attack_opportunity`) vs `combat_executor._calculate_reinforcements` | **OPEN**, filed by the slice-4 review round (R1-9) |
| **FA-R3** | **A standing order is created at 0 AP when the sentence's BASE action is a free verb.** Pre-existing root, measured by the slice-7 review round (R3-2) on the PARENT tree: `Davout, hold Rhineland and wait` → AP 4→4 with a HOLD order standing and "(2 AP — a standing strategic order…)" in the reply; `march to Lorraine and wait there` → marched + MOVE_TO at 0 AP. The mock chain's WAIT arm sits above hold/move (it must stay above the reinforce arm — "wait for reinforcements"), so the BASE action is `wait`, and the executor charges the strategic cost off the base action's `free_actions` membership. Slice 7 had WIDENED this with `stay put` / `rest your men` (`hold Rhineland and stay put` 4→2 → 4→4); the review round relocated stay-put below the order verbs, which removes the widening and leaves the root. | The player gets a two-turn standing order for nothing whenever the sentence also says "wait"; the reply prices it at 2 AP. | `backend/commands/executor.py` (the strategic pre-gate reads `free_actions`) / `backend/ai/llm_client.py` (the wait arm above hold/move) | Charge the strategic cost from the ORDER in `_execute_strategic_command`, or refuse the strategic upgrade when the base action is free; pin AP 4→2 for "hold Rhineland and wait". A balance-adjacent change (AP economy) — measure before landing. | `hold Rhineland and wait` → AP 4→2 and a HOLD order; `march to Lorraine and wait there` → 4→2; `wait for reinforcements` still WAITS (free). | **OPEN** (filed Sept 5, 2026 by the slice-7 review round) |
| **FA-R4** | **`Berthier, end turn` / `Sire, end turn` shrug while `Berthier, status` and `Berthier, help` work.** Slice 7's `_DESK_ADDRESS_RE` strips the chief-of-staff address on the two exact-match desk routes but deliberately NOT on `is_bare_end_turn`: the client's lapse-confirm gate (`main.gd::_is_end_turn_phrasing`) mirrors the backend's bare end-turn vocabulary word for word, so widening only the backend would advance the turn behind the client's unanswered-envoys confirm (the UX23 soft-lock class). | A player who addresses Berthier to end the turn is shrugged at, once, and types `end turn`. | `backend/ai/clause_guards.py` (`is_bare_end_turn`) + `godot-client/project-sovereign/scripts/main.gd` (`_is_end_turn_phrasing`) | Widen BOTH gates from ONE vocabulary (the `.gd` gate's comment already demands parity) in a slice that boots the engine. | `Berthier, end turn` ends the turn on the server AND arms the client's lapse confirm; a `.gd`-touching slice. | **OPEN** (filed Sept 5, 2026 by the slice-7 review round, R1-13) |
| **FA-S7-D1** | **The live parser reads "Ney, fix bayonets" and "Ney, cover the retreat" as a cavalry CHARGE.** Measured once on the live Anthropic parser while landing FA-73's `live_only` twins (both pass — they pin `not_action: repair` / `retreat`): the model maps an infantry bayonet order and a screening order to `charge`, a real order the executor can run (recklessness-gated). The prompt has no rule for a deed no action models (the mock refuses both; PS18-5's harm was the fast parser's RETREAT). | On the live parser, "fix bayonets" may launch a Glorious Charge the player never ordered, when recklessness allows. | `backend/ai/prompt_builder.py` (Valid Actions rules) | One prompt line under Valid Actions: "an order naming a deed no listed action models (screening, drill, fixing bayonets, restoring order) → unknown"; then flip the two live twins to `action: unknown`. CR-6/CR-8's gate owns the model-side vocabulary. | Both live twins parse `unknown` on the live parser (a deliberate two-call live eval). | **OPEN** (filed Sept 5, 2026 by the slice-7 review round, R3-13) |

---

## Live UX Report — the reward curve (August 23, 2026, rows UX23-D1..D4)

> Filed from the Aug-23 live turn-3 France/1805 report (*"it happens so early
> in the war them wanting raises etc. whole ux is off"*). The **delay** half
> was fixed in-band the same day — `GRACE_TURNS` 2 → 4, landing record
> `BUG_FIXES.md` §Live UX Report. These four are the **shape** half: each
> changes the curve rather than the deadline, each is structural, and none is
> built.
>
> Two measured facts belong in front of whichever gate takes these:
>
> * Across all 8 battles in the live campaign log, **Davout and Lannes appear
>   in none of them** — and each holds 2 battle wins and an 80g/turn
>   expectation. Both sit at Munich. One tactical victory credited the whole
>   stack. (UX23-D4 attacks exactly this.)
> * **`battles_won` is a monotonic ratchet.** All 7 write sites are `+= 1`;
>   nothing anywhere decrements it. That is why every scaling lever inherits a
>   curve that can only rise. `glory` is already graded, already gives
>   participants only +1, already excludes garrison stomps, and already decays
>   over 8 turns. (UX23-D2.)
>
> Not on this list, deliberately: a `REP_STEP` retune. It is technically
> in-band, but it is the ONLY dotation constant that moves `BASELINE_SERIES`
> at a plausible balance magnitude (measured: index 21; ~19 test failures plus
> the sanctioned re-record + flip-attribution ritual). If it is ever taken, it
> goes alone.

| id | item | why it is gated |
|---|---|---|
| **UX23-D1** | **The free-wins floor.** `expectation = REP_STEP × max(0, wins − N)`. A marshal's first N victories raise no claim. | A new mechanic, not a retune. ~~Measured at N=1 it clears all four live notifications *at that instant*~~ — **that clause is FALSE and is struck (see the correction block below)**; three of the four marshals held 2 wins, so N=1 leaves them at expectation 40 against satisfaction 0 and the row still posts. It buys one battle, not the class of complaint. Cheap, and probably too small alone. |
| **UX23-D2** | **Key expectation to `glory`, not `battles_won`.** | Structural: changes the field the entire reward economy is priced off. Also the most *designed* answer — glory already has every property the curve wants (graded, decaying, participation-aware, garrison-stomp-proof) and `battles_won` has none of them. |
| **UX23-D3** | **A war-age / conquest damper** — the Empire does not owe estates it has not yet conquered. | Structural, and `get_expectation` **takes no `world`** — **12** production call sites would have to pass one (the row said 11), *and there is a second entry point to the same curve* (see the correction block below). Strongest candidate for the principle *"the game should not ask before the player can pay"*, which is the actual complaint: at turn 3 France holds no conquered province, so the estate instrument does not exist and only the rente does. |
| **UX23-D4** | **Stop crediting non-ordering co-locators.** A marshal standing in the province where someone else won should not bank the win. | ~~Reverses an explicitly blessed W6-1 assumption (`combat_executor.py`, the comment is deliberate).~~ **Wrong seam and wrong date — struck; see the correction block below, which also re-prices the row.** **Attacks the root**: it would have turned the live turn-3 burst from four simultaneous claims into one or two, which is the difference between a demand and a pile-on. |

**Recommended reading of the four:** D4 then D2. D4 removes the pile-on that
made four claims arrive at once; D2 replaces a ratchet with a curve that can
fall. D1 is a palliative and D3 is the largest change for the clearest reason.
Whoever takes the gate should decide whether "too early" meant *too soon* or
*too many at once* — the report says both, and they have different fixes.

### Corrections to this section (August 23, 2026) — record only, the gate is untouched

> Found by the pre-build research fleet for **UX23-A** (the one-click reward
> rail, `BUG_FIXES.md` §UX23-A), which read this section to make sure the
> affordance slice did not collide with it. It does not — all four rows are
> curve items and none gates the button. But three of the rows' own assertions
> are wrong against the code, and two of them would mis-aim a build. Recorded
> here rather than quietly amended, because two are load-bearing to the
> *recommendation order* above.

1. **D1's "clears all four live notifications" is false.** The rail row posts
   on ANY shortfall ≥ 1 — `world_state.py:6009-6042` has no floor. An
   unrewarded marshal's satisfaction is 0 (France holds no conquered province
   at the 1805 boot, so no estates), so under `REP_STEP × max(0, wins − 1)` a
   2-win marshal still has expectation 40 against satisfaction 0: the row
   posts and erosion still runs at `min(3, ceil(40/50))` = 1 trust/turn. The
   row's own next clause ("three of the four already held 2 wins") contradicts
   the first, and the live measurement in `BUG_FIXES.md` — *"each holds 2
   battle wins and an 80g/turn expectation"* — supports the second. **N=1
   clears one of four, not four of four.** The parallel lever list in
   `BUG_FIXES.md` never carried the false sentence; the error is unique to
   this copy.

2. **D3 undercounts, and misses a second entry point.** There are **12**
   `get_expectation` call sites, not 11 (`combat_executor.py:6824`;
   `economy_executor.py:1136,1429`; `dispatch.py:923,2235`;
   `dotation.py:272,531,558`; `jealousy.py:2423,2428`;
   `marshal_overview.py:373`; `world_state.py:6011`). More importantly the
   curve has a **second door**: `expectation_for_wins` (`dotation.py:198`) is
   called directly at `combat_executor.py:6827` for the battle report's
   "victory raises his expectation" line. A damper installed inside
   `get_expectation` alone would leave that line on the undamped curve — a
   shown≠applied divergence in the exact seam whose single-sourcing
   (`expectation_for_wins`) exists *because it already diverged once*.
   Also: the eligibility rule is **non-homeland**, not "conquered"
   (`nation_starting_regions`), so a province gained by treaty cession or an
   NA-6 carve qualifies too. At boot the two sets coincide, so D3's conclusion
   survives its paraphrase.

3. **D4 names the wrong seam, the wrong date, and is under-priced.** The
   co-locator credit is at `combat_executor.py:5755-5771`, inside
   `if is_coordinated_battle:`. *(Second correction, same day: the first cut
   of this paragraph cited `c5d808c1`, **2026-03-28** — which is the R10A
   executor SPLIT, a pure file move, and is simply what plain `git blame`
   attributes a moved line to. It also contradicted itself by calling that
   date "Session 62". `git blame -C -C -C` resolves the move and gives
   `70ab5099`, **2026-02-23**, "Session 62: Casualty Distribution (Phase 7b)",
   in the pre-split `backend/commands/executor.py`. A correction about a wrong
   date had a wrong date; it is fixed here rather than quietly.)* The model is
   the Session-62 casualty-participant one (`MULTI_MARSHAL_SPEC.md:568-570`,
   *"Participating | All same-nation marshals in region at time of combat"*).
   That is nearly five months BEFORE W6-1 (July 10), whose own loop at `:6081`
   *cites* the older model rather than establishing it — and which CA9-N1
   documented as inert (`is_coordinated_battle` is always True when that loop
   has an arrival, so seam A always fires first and the `:6081` increment is
   guarded by `_already_tallied`). **Reversing W6-1 would change nothing.**
   Three further re-pricings: "non-ordering" overstates it, because
   `_get_casualty_participants` already filters a hostile relationship without
   a SUPPORT order; `atk_participants` is not a bystander list but the combat
   roster, feeding **three** consumers — win credit, proportional casualties,
   and CO-1 committed strength — so D4 must split or shrink that list and
   therefore **moves combat math and `BASELINE_SERIES`**, which the row prices
   as neither; and arriving reinforcements are relocated into the region
   *before* the participant scan, so the predicate has to be "was already here
   and gave no order", never "is here".

None of this changes the gate's shape, and D4 remains the row that attacks the
root. It is a larger, better-understood piece of work than the table said.

---

## WO slice 8 in-game pass — recorded, not fixed (August 22, 2026)

> Found by driving the real client for the slice 6 + 8 visual pass
> (record = `WEIRD_OUTCOMES_SPEC.md` §3 slice 8, in-game addendum). Three
> defects were fixed in-session; these two are design calls, deliberately
> left for a gate rather than patched on the spot.

| row | finding | why it is a design call |
|---|---|---|
| **WO-V-D1** ⚠ **worsened Aug 22** | **The region panel's build rows fall below the fold.** Slice 8 grew the Build section from ONE chips row to a header plus six terms rows; the panel is terminal-clamped (the July UX pass) so only ~2 rows show at the default height. The terms the slice exists to state need a scroll — the wheel works, and the pattern is discoverable, but the headline content is not on first sight. **AMENDED: the damage-legibility follow-up ([V-4]/[V-5], same day) added up to three MORE lines to this same panel** — a war-damage line, a watchtower condition row, and a second repair chip. The fold problem is now more acute, and it was made worse knowingly rather than discovered later. | The remedies trade against each other and against a landed contract: raise the panel's clamp (re-opens the July UX pass), render terms on hover only (loses the at-a-glance comparison the slice was built for), or compact to two chips per line (loses the delivered-terms alignment). A fourth option now worth weighing: collapse the whole ACTIONS block behind a disclosure row, since it has grown from 3 rows to ~12. Owner: the next UI pass. |
| **WO-V-D2** | **`Intel: Partial (reports only)` prints on the player's OWN capital**, directly above four exact figures (Income 300g / Stability 100% / Supply 75,000 / Garrison 25,000) that the same surface is happy to state. Pre-existing, not slice 8 — own soil is econ-visible by ownership while its intel level stays PARTIAL until a marshal stands there. | The label is not wrong (no army is reporting from Paris) but it reads as a hedge on figures that carry none. Fixing it means either a second label vocabulary for own soil or suppressing the line where `region_econ_visible` is true by ownership — a fog-copy decision, not a bug fix. |

---

## Weird-Outcomes design questions — filed August 16, 2026 (**the WO-EVAL docket**)

> **Evidence memo = `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md`
> (authoritative).** Ten campaigns, ~290 turns, each built to push a DIFFERENT
> system past its designed shape rather than to win. Correctness rows are
> `BUG_FIXES.md` §Weird-Outcomes Playtest (WO). **All OPEN — no gate has been
> held on these.** These six rows are the docket for the **WO-EVAL** pass (the
> ▶ NEXT UP entry in `docs/STATUS.md`): *how do we make the game better, given
> what ten deliberately strange campaigns revealed?*
>
> **The finding underneath all six — THE FUNNEL.** Every arm that fought ended
> at 29–31 provinces. Every arm that pursued a non-military strategy ended at
> 5–12. There is no middle. The game does not refuse the other strategies; it
> makes them **quietly unavailable**, and in three arms reported them as
> working. A player who wants to be Napoleon-the-statesman, Napoleon-the-
> administrator, or Napoleon-the-admiral currently discovers that the only
> verb the game truly implements is *attack*.

> ### ✅ BUILD CONTRACT AUTHORED August 21, 2026 — **`docs/WEIRD_OUTCOMES_SPEC.md` is authoritative for slice scope/seams/acceptance/order** (17 slices; its §2 verification corrects the eval where marked). Rows WO-D7..D10 below were filed by that session's defect hunt.
>
> ### ⚖ THE FUNNEL CLAIM IS FORMALLY WITHDRAWN — slice 1b, August 21, 2026 (addendum = `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md` §9, authoritative)
>
> The original sentence — *"France wins overwhelmingly whenever it fights and
> is dismembered whenever it tries anything else. There is no middle."* — was
> re-measured on the FIXED instrument (10 arms × 3 seeds × 3 repeats, mock
> repeats byte-identical): **it does not survive.** The worst fighting-arm
> median does not exceed the best non-military-arm median and the min–max
> bands overlap massively under every defensible grouping — the SEED, not the
> strategy, is the dominant variable in ambient-driven outcomes (the same
> fighting script ends at 30, 27 or 7 provinces across three authored seeds).
> **Per the G2 re-open condition, `BUILDING_SLOT_LIMITS["town"] = 1` STAYS
> SHELVED** — the non-military arms do not "still show collapsing." What the
> original table measured was mostly instrument blindness plus single-draw
> noise. The real non-military gaps remain the QUALITATIVE ones the eval
> already framed: built, unpriced, unreachable and invisible — in that order.
>
> ### ✅ WO-EVAL HELD August 17, 2026 — **memo of record = `docs/audits/WO_EVAL_2026_08_17.md`, AUTHORITATIVE where it amends the rows below.**
>
> **Read the table below WITH the memo's §8.** Eight investigations, each
> adversarially verified: **WO-D2 and WO-D5 were overturned outright**, four
> materially corrected, **24 claims killed**. Per-row verdicts:
>
> | row | verdict | what changed |
> |---|---|---|
> | **WO-D1** | PARTLY WRONG | the 1:13.9 is a **harness artifact** (`attacker_casualties` is the lead corps only; whole-side is **1:4.31**); lever (b) **already shipped**; lever (a) measures **backwards**. Real gap = the muster never states its supply price. → memo §3 |
> | **WO-D2** | **WRONG** | the on-ramp **exists** — `propose_vassal` is emitted at three states, priced 3 DP, scored, and already rendered by the wizard. Real gap = four small items + an **unpriced typed backdoor** worth +37,000 men on turn 1 → **gate G1** |
> | **WO-D3** | PARTLY WRONG | the Descent **runs end to end** (~13 turns, ~5,200g, 4 corps) and the arm's timing was already right — **it never typed the confirm**, which is a *harness* blindness. Real gaps = WO-14 at two producers; blockading is dominated by doing nothing |
> | **WO-D4** | PARTLY WRONG on numbers, **RIGHT on structure** | depot dominance is **11 of 12 provinces** (13 was slots); do **not** re-price. The row's real content: a full build-out **plus 100,000 gold** moves `power_score` by **0.000** → **gate G2** |
> | **WO-D5** | **WRONG** | two AI-vs-AI peaces fire on **every** seed; France→Russia scores **ACCEPT** at every measured turn from t16. Exhaustion saturates its only consumer at **WE 60**, so 60→200 is inert. Real gap = one strict `<` in Berthier's counsel rung. ~0.3 session |
> | **WO-D6** | PARTLY WRONG, remedy is a **regression** | `home_captured` is already weight **100** > `capital_stormed` 92 — "at or above 92" demotes Paris below `marshal_captured`. Real defect = a class collision that keeps Paris off the page. Fold WO-11 in the same edit |
> | " | ✅ **BUILT August 22, 2026 (row WO slice 4)** | the number settled at **`capital_lost` 100 / `home_captured` 99**, under `sovereign_captured` 101 — NP-4 intact. The class collision is what was actually wrong and it is measured in the landing record: with Paris logged LAST the page carried three other provinces and **not Paris**. WO-11 folded in the same edit as promised |
>
> ### ✅ AND THE GATE WAS HELD THE SAME DAY — three rulings, record = memo §6 (authoritative)
>
> - **G1 (WO-D2's real question) — the typed diplomatic verbs are RETIRED as a
>   player surface.** User ruling, verbatim: *"the diplo screen should be only
>   path for these actions typing commands should just have it tell them to go to
>   the diplo room or something thematic."* Not priced, not routed — redirected in
>   character. ⚠ It lands on the **terminal input path in `main.gd`**, never as a
>   backend refusal: the wizard itself executes by sending typed commands
>   (`diplomacy_wizard.gd:12` → `main.gd:4938` → `api_client.send_command`, no
>   marker). **This also absorbs WO-4 and most of WO-5.**
> - **G2 (WO-D4b) — neither arm now.** The requirement list goes to the Victory
>   pass; `BUILDING_SLOT_LIMITS["town"] = 1` is held as the cheap purchase if the
>   re-measured funnel still shows collapse.
> - **G3 (WO-D1's third lever) — DESIGN, and the game says so.** Every corps in
>   the battle province fights; the exclusion is taught for adjacent corps only.
>   **WO-D1 Option 3 is closed by ruling; CA9-D2 is not re-opened.**
>
> **And the docket's own framing is superseded.** The funnel's *magnitude* is
> unmeasured: the driver never seeds the module RNG, so the same script at the
> same seed ends at **30 / 28 / 27** provinces (hand-measured) and **4 · 28 · 17
> · 16 · 14** over 30 turns. Three of the four non-military systems are **built
> and working when driven by hand**. The accurate sentence is *"the non-military
> strategies are built, unpriced, unreachable and invisible — in that order of
> severity."*

| # | Question | Evidence | Recommendation to evaluate |
|---|---|---|---|
| **WO-D1** | **Should the battle be a decision?** 33 player-initiated battles across seven campaigns: France lost **22,212** and inflicted **307,712** — overall exchange **1:13.9**; worst single battle Napoleon lost **9 men** and destroyed **28,650**. The cause is legible in the game's own muster line — `Ney (24,000; 78,676 if all march)` — the WHOLE army reinforces every attack, so the corps you name is never the corps that fights, while the defender is whichever single corps stands there. Austria's 52,000-strong main army was annihilated **on turn 1** by three attacks in one turn. Stated honestly: France's real losses come from supply attrition and enemy-phase captures, so the difficulty is real — it lives in **logistics and geography, not in combat**, and the battles themselves carry no tension. | absurdist/tyrant/eagle arms; exchange table in memo §3 F6 | Three levers to weigh, not one: (a) cap auto-reinforcement by relationship/order so "who marches" is a *decision* the player makes before the fight, not a default; (b) let the defender concentrate symmetrically; (c) leave it and accept that this game's tension is logistical — but then STOP printing an all-march figure that makes every fight look like a choice. **Do not tune the damage numbers first** — the shape is structural. |
| **WO-D2** | **Is the vassal layer a strategy or a decoration?** The Kingmaker arm spent 30 turns trying to build an empire of clients and had nearly every constructive order refused while France fell **28 → 5 provinces**. `vassalize Saxony` → *"requires WAR or OPEN_BORDERS+"* (correct, but no route offered); `invest in bavaria` → *"Bavaria is not a vassal"* while the turn-1 dispatch is simultaneously advising *"Invest in them"* about a satellite; `increase autonomy` → *"Specify which vassal"* with no list. And the layer punishes use: WO-8 has all 19 courts hit one satellite in a single tick for −95 loyalty. | Kingmaker arm; memo §3 F9 | Decide whether client-building is a **supported win route** or a flavour system. If supported: the refusals must name the route (the pattern already exists — `request terms from Austria` answers *"the coalition's terms are the leader's to name, not each court's own"*), the honest-availability chips must reach the typed surface, and WO-8's pile-on needs a per-target cap. If flavour: say so, and stop advising levers that refuse. |
| **WO-D3** | **Is naval a strategy or a wall to admire?** A 30-turn dedicated naval campaign executed **zero** naval operations while France fell 28 → 12. The expedition needs a marshal standing at a dockyard and nothing in the naval surface suggests moving him there; the Grand Diversion reported success three times without ever firing (quote-then-confirm, never confirmed, and the pending question evaporates on the next command). One mechanic in there is genuinely elegant and should be the model: building ships LOWERS readiness (69 → 50 over ten keels) and the message says why. | Admiral arm; memo §3 F18 | Evaluate a naval **on-ramp**: the expedition chip should offer to move the marshal, and a soft-stop that evaporates silently should either persist or say it lapsed. Also worth asking whether "ignore Germany and fight at sea" should be survivable at all in 1805 — if not, say it in Talleyrand's voice rather than by attrition. |
| **WO-D4** | **What is the reward for not fighting?** The Merchant arm never attacked and ended exactly where it started (28 → 28) — survived, but with nothing to show; meanwhile **its ALLY Bavaria went 3 → 11 provinces and annihilated Austria and the Kingdom of Italy**. The economy itself is in good order (a hoarder's net fell +2,095 → +150 over 30 turns; the charge curve converges on its design figure), but the *market is strictly dominated by the supply depot* on 10 of France's 13 buildable provinces — cheaper, higher income, and it adds supply capacity. | Merchant arm; memo §4 F17 | Two separable questions: (a) re-price the market vs depot so building is a real choice; (b) decide whether an economically dominant France should be able to WIN by that dominance — today the answer is no, and the Victory pass (ROADMAP 12–13) is where that belongs. |
| **WO-D5** | **Does the war ever end on its own?** War exhaustion sat pegged at its **200 cap for France, Britain, Russia AND Austria at turn 46**, with Austria delivering armistice proposals on six separate turns and no peace concluded. Related: enemy commanders are effectively indestructible — Archduke John was *"broken and flees"* in **seven separate dispatch headlines** and ended at 9,443 men. | Long Quiet arm (45 turns ambient, seed `austerlitz`) | Ask whether exhaustion at cap should FORCE something (a mediated congress, a forced armistice, a collapse) rather than idling. ⚠ Caveat to test first: the driver declines by policy, so France's own pairs are policy-frozen — the AI-vs-AI half is the real question. |
| **WO-D6** ✅ **BUILT August 22, 2026 — row WO slice 4 "The Capital Speaks"; landing record = `WEIRD_OUTCOMES_SPEC.md` §3 slice 4** | **The game cannot narrate your own catastrophe.** The fall of **Paris** — capital, Emperor's seat — is narrated with the exact template Brittany gets three turns later; `capital_stormed` (weight 92) exists only for France taking an ENEMY capital, with no symmetric class for losing your own. Meanwhile `own_mauled` led a briefing with a **26-man** casualty on a turn a vassal defected, a homeland province fell, and the army stood at 24% of boot strength. | Kingmaker + Tyrant arms; memo §4 | ~~A `capital_lost` headline class at or above 92~~ — **built at 100**, not 92: the eval's own number would have demoted the capital below `marshal_captured` (95), which the WO-EVAL row above already caught. The relative-vs-absolute question the row raises second is **`own_mauled`'s floor, and it is NOT here** — it stays row WO slice 12 (WO-16), per spec §3 slice 4 item 6. |
| **WO-D7** *(filed Aug 21, 2026 — the eval recorded it and routed it nowhere)* | **A war in which nothing happens bills both treasuries.** France\|Russia sit at war score exactly **0** for thirty turns — the two powers never fight — while both accrue WE to the 200 cap and pay the EB-1 ill/war charge rates and the war recruit premium. | WO-EVAL §3 WO-D5 "New finding, recorded" | Should a contactless war COOL (pair-scoped WE decay when no battle for N turns / charge rate keyed to contact) rather than bill like a shooting war? **Owner: EC-2 pass 2** (charges shape); near-term mitigation = spec slice 5 (the ACCEPT-able peace becomes visible). |
| **WO-D8** *(filed Aug 21, 2026, from the spec session's hunt)* | **The player faces no re-declaration time floor after a truce or peace.** The exhausted-pair 8-turn floor skips player pairs by construction; leaving ARMISTICE pops the 5-turn hold; a direct WAR→PEACE settlement writes none. Re-declaration is priced only in DP / −30 relations / threat / the CA9 war-age acceptance penalty. The AI faces a floor the player never does. | spec §3 slice 13 (the corridor P1's enabling half) | Should the PLAYER face a truce floor at all, or is price-not-time the design? PT-J2's demobilize-on-peace is a gate ruling and STANDS either way. Future diplomacy gate; do not build uninvited (spec never-do 21). |
| **WO-D9** *(filed Aug 21, 2026)* | **The objection economy has no per-marshal cooldown and a farmable authority band.** After spec slice 16 fixes the correctness half (free trust on the bail; the load-refresh), the SHAPE remains: +3..+12 trust per objection with only a per-turn cap; authority pays +1/answer in the 0.30–0.60 trust-ratio band while the penalty starts at 0.65, and compromise counts toward neither ratio. | spec §4 (hunt, WO-21/WO-23 context) | Gate question: per-marshal objection cooldown? diminishing trust returns? close the authority band asymmetry? The anti-pushover damper `get_trust_gain_modifier` exists and is wired to nothing on this path — wiring it is the natural first lever. |
| **WO-D10** *(filed Aug 21, 2026)* | **The exiled empire cannot rebuild its Marshalate.** `find_spawn_region` considers only the capital and `nation_starting_regions` — never held conquests — so a player who lost the homeland but holds a dozen rich provinces is refused with *"No soil remains on which X could raise his corps"*, false on the map they are looking at; a dead roster in exile is permanently unrecoverable while income/DP/tribute continue. | spec §4 (hunt) | Let commissioning spawn at the richest HELD province when no home soil remains (Victory-pass adjacent — the exile game only matters once losing is a state the game recognizes), and fix the refusal copy either way. |
| **WO-D11** *(filed Aug 21, 2026, by the slice-15 build)* | **A mid-march capture forfeits an enemy marshal's estate for nothing.** An automated capture auto-secures (IGR-X5's march policy, and now the WO-26 collision arm too), which means no plunder/secure question mounts — so the WO-27 carve-out does not apply, and the estate prune strips the holder's title on the same advance with an `estate_lost` event. We take no windfall, buy no goodwill, and the player is never asked. `movement_executor`'s own comment claimed the opposite for a month ("the holder simply keeps his title — indistinguishable from 'respect' minus the goodwill entry"); slice 15 corrected the comment rather than quietly changing the rule. | `movement_executor.py` march arm; `world_state.mount_or_auto_secure_capture`; the prune's carve-out | Either write a RESPECT entry on an auto-secured capture (the courtesy a passing column would plausibly extend, and it makes the comment true), or keep the forfeit and say so on the surface the player reads. Estate-economy adjacent — EC-2 pass 2 or the W6-8 owner. |
| **WO-D12** *(filed AND BUILT September 1, 2026 — slice 9)* | ✅ **CLOSED.** **The anti-pushover damper is invisible, and no surface could show it.** Slice 9 wired `get_trust_gain_modifier` at the objection quote, so a player who always answers "trust" now earns half the trust per objection. Shown == applied — the button quotes what is paid — but **nothing tells the player the figure has been halved or why**. `affects_trust_gains` (`main.py:3855`) and `trust_modifier` (`main.py:3761`) have ZERO consumers in `godot-client/`, and `/authority_status` has no Godot caller at all; the objection payload does not even carry the modifier, so a client surface is not merely unwritten but currently unbuildable. What the player sees is the trust number quietly halving next to an unrelated-looking `"Authority: %d"` line (`objection_dialog.gd:113/137/139`) with no causal link drawn. | `executor.py:1627-1644` + `strategic_executor.py:1105-1120` (the objection dicts) · `objection_dialog.gd:113-139` | **Small and owed.** Add `"trust_gain_modifier"` to both objection dicts and one conditional line in `objection_dialog.gd` when it is `< 1.0` — *"(halved — your marshals have taken your measure)"*. ~4 lines plus the XR-1 boot smoke. NOT built in slice 9 because the WO-D9 gate scoped the build to wiring the existing modifier and explicitly ruled out new mechanics; this is a discoverability surface, not a re-gate. **BUILT in slice 9 rather than deferred.** Both objection dicts stamp a display-only `trust_gain_modifier`, read through the NEW single source `authority.objection_trust_modifier` — the same read the damper multiplies by, so the explanation cannot itself become a shown-vs-applied bug — and `objection_dialog.gd` spends it on the line that already carries the cause: *"Authority: 62 — they have taken your measure (trust rewards x0.50)"*, rendered only below 1.0. This also makes the compromise-vs-trust inversion legible: the player can see WHY the trust arm shrank beneath the flat compromise figure. Pinned by `test_wo_slice9_the_courting_cap.py::TestTheDamperExplainsItself` (4) + sweep WO9-32/33/34; parse harness EXIT=0, boot smoke 0 SCRIPT ERROR. |

### ▶ WO-D7..D11 — CARRY CONTRACTS (recorded August 21, 2026, at the user's direction)

> **Why this block exists.** Row WO cannot close with five design rows in the
> vague state Golden Rule 9 forbids ("future gate", "econ pass 2 adjacent").
> Each row below now names an **owner spec/row**, a **landing slice**, a
> **completion definition**, a **STATUS tracking line**, and a **behaviour
> test** — or is explicitly struck. Nothing here is a build; the carry IS the
> disposition. **Exactly one of the five (WO-D9) needs a user ruling before
> its owner can act**, and it is marked GATE-PENDING rather than carried
> silently.
>
> Two of the five were split, because half of each is a copy bug fixable
> inside row WO and half is a mechanic that is not:

| row | disposition | owner + landing slice | completion definition | behaviour test |
|---|---|---|---|---|
| **WO-D7** contactless war bills both treasuries | **CARRIED, mechanic** | `ECONOMY_REVISIT_SPEC.md` **EC-2 pass 2**, the charges-shape slice | A France\|Russia pair at war score exactly 0 with **zero battles for N turns** either stops accruing WE or bills at a contact-keyed rate. Measured as a named delta on the ambient 40-turn board, with the un-fought pair's charge total falling and a shooting war's unchanged. | `test_econ_*`: a zero-contact war pair's per-turn charge is strictly less than an identically-aged pair that fought; and the shooting pair is byte-identical to today. |
| " | **near-term mitigation — ✅ DISCHARGED August 22, 2026, and RE-EARNED the same day by the review round** | row WO **slice 5** + its review round (`WEIRD_OUTCOMES_SPEC.md` §3 slice 5 = the landing record; the review-round addendum is authoritative where it amends it) | Berthier names the ACCEPT-able peace, so a contactless war is at least *visible* as endable. **Measured at landing:** at t16 of the `austerlitz` reproduction the war room named Russia — pair score 0, both courts past the exhaustion floor, her plain peace scoring ACCEPT 54 — where before it named Britain's design. **Corrected by the review:** as landed the rung named the *deadest* war, not the ACCEPT-able one, and rung 1 pre-empted it on **7 of 13** measured snapshots with a court the scorer refused at 21–28 while a stuck court in the same row would have signed at 64–69. Rung 1 now ranks every candidate by what the game's own scorer says a bare peace would meet (flip flag `COUNSEL_RANKS_BY_ACCEPTANCE`), and the counsel STATES that verdict instead of promising one: **0 of 13** after. The predicate is contact-blind, so WO-D7's own zero-battle war passes it trivially. **Does not fix the billing**, which stays carried to EC-2 pass 2 above, untouched (verified: no economy file in either diff). | `tests/test_wo_slice5_berthier_names_the_peace.py` (57) + `tests/test_wo_slice5_review_2026_08_22.py` (38); mutation sweeps `tools/_sweep_wo5.json` 23/23 and `tools/_sweep_wo5r.json` 21/21, 0 inert |
| **WO-D8** the player faces no re-declaration truce floor | **CARRIED, uninvited-build forbidden** | a **future diplomacy gate** (never-do 21 stands) | Either a player floor exists symmetric with the AI's `PAIR_EXIT_TRUCE_FLOOR_TURNS = 8`, or the row is **struck** with "price, not time" recorded as the design and the asymmetry documented at the seam. Both are acceptable closes; silence is not. | on the "floor" arm: a player re-declaration inside the floor is refused by the same predicate the AI faces. On the "struck" arm: a pin that the asymmetry is deliberate, sited at `settlement_third_party`'s player skip. |
| **WO-D9** the objection economy's shape | ✅ **GATE RULED August 22, 2026 — the user took the recommended default: WIRE THE EXISTING DAMPER.** The three questions answered in writing: (a) per-marshal objection cooldown — **NO** (no new mechanic); (b) diminishing trust returns — **YES, via `authority.get_trust_gain_modifier` as it stands** (≥5 recorded answers; trust-ratio >0.80 → ×0.5, >0.60 → ×0.75); (c) the authority-band asymmetry (+1 in the 0.30–0.60 ratio band, penalty only from 0.65, compromise counting toward neither) — **RECORDED AS DELIBERATE, not closed**. | **✅ LANDED September 1, 2026 in row WO slice 9** (commit `59befa22`; landing record `WEIRD_OUTCOMES_SPEC.md` §3 slice 9). **The landing instruction in this row was WRONG in three ways and the build corrects it:** (1) there is no single "trust-pay seam" — six positive-gain sites across two handlers that never meet, `meta_executor.py:1635` forking between them; (2) all six read the figure back off the objection dict, and the objection dialog puts that same figure on its button, so damping at the PAYMENT would have made the button lie — it is applied at the QUOTE instead (`executor.py:1619`, `strategic_executor.py:971`), which damps all six and keeps shown == applied; (3) `main.py:3835` is `:3855` (plus an unlisted `:3761`), and **nothing in `godot-client/` renders either field**, so the ruled test anchors on the objection dialog's button, not on the HUD. Also corrected: the stated "+3..+12" is **+2..+12** (`int(3 × 0.7) = 2`). Nothing re-gated — no per-marshal cooldown, the modifier's own thresholds, the band asymmetry left alone. | the ruled behaviour test stands: a pushover player's objection trust gain is strictly less than a balanced player's for the same press; and the value the UI shows equals the value paid. |
| " | *correctness half* | **CLOSED** by slice 16 | the free trust and the load-refresh are fixed; only the SHAPE remains | `test_wo_slice16_objection_pays_honestly.py` |
| **WO-D10** the exiled empire cannot rebuild its Marshalate | **SPLIT — copy half CARRIED INTO ROW WO** | row WO **slice 12** (the copy sweep) | The refusal stops asserting something false about the map the player is looking at: *"No soil remains on which X could raise his corps"* is printed while the player holds a dozen rich conquests. The copy names the real rule (home soil, not held soil) whichever way the mechanic is later decided. | slice 12: a player holding conquests but no home soil gets a refusal that does NOT claim there is no soil, and that names the actual gate. |
| " | *mechanic half* | **CARRIED** to the **Victory & Objectives Pass** (ROADMAP positions 12–13) | `find_spawn_region` considers held provinces when no home soil remains — deliberately downstream of Victory, because the exile game only matters once losing is a state the game recognizes. | at the Victory pass: an exiled nation with held soil can commission; one with none still cannot, and says why. |
| **WO-D11** a mid-march capture forfeits an estate for nothing | **CARRIED** | `ECONOMY_REVISIT_SPEC.md` **EC-2 pass 2** (estate economy), co-owned with the **W6-8** estate owner | Either an auto-secured capture writes a RESPECT entry (the courtesy a passing column would extend — and it makes `movement_executor`'s comment true) or the forfeit stands and is **stated on the surface the player reads**. The comment is already corrected in place, so the code no longer lies either way. | on the respect arm: a mid-march capture of an enemy marshal's estate leaves the title standing and the +5 acceptance term live. On the forfeit arm: the capture message names the forfeit. |
| **WO-D12** *(filed Aug 22, 2026 by the slice-5 review)* rung 1's LOSING arm is still row-scoped | **CARRIED, deliberate for now** | row WO **slice 12** (the copy sweep) for the wording; a **future war-room gate** for the qualification | A collapsed row carries the WAR-level side score and its LEADER's name, so a court France is genuinely losing to inside a winning war is invisible to rung 1 (measured: Britain at pair −16 and −19 while the only row read +31 and +3). Widening it per court was TRIED and reverted: it pre-empted the NA-1 design counsel over a trivial −5 pair and moved turn 12, which the slice-5 done-when pins. The review's ranking removes the HARM (the leader no longer outranks a court that would sign); what remains is that such a court gets no counsel of its own. Close by widening the qualification with a meaningful-deficit floor, or by striking the row with "the ranking is the fix" recorded. | a per-court losing candidate on a row-winning board is either named, or a pin states that it deliberately is not |
| **WO-D13** *(filed Aug 22, 2026)* rung 1 is ABSORBING once war exhaustion saturates | **CARRIED** | a **future war-room gate** (the rung tier is the blessed slice-5 contract — do not move it uninvited) | WE rises +8/turn at war and decays only at peace, so from ~t15 every belligerent is permanently past the floor and the stalemate arm holds the single recommendation slot for the rest of the campaign (measured t16→t40: the same sentence, `age` the only variable). Rungs 1.5/2/3 lose their BUTTON — their content still prints in the advisory body, so no information is lost. Close by latching the rung (fire once per court per N turns) or by recording the precedence as deliberate. | a board with a vassal near revolt AND a stuck war either surfaces the vassal option within N turns, or a pin states the stalemate keeps the slot on purpose |
| **WO-D14** *(filed Aug 22, 2026)* `seek_bilateral_peace` is offered while unaffordable | **CARRIED, pre-existing** | the **honest-availability owner** (`settlement_validation.evaluate_pair_peace_substitute_eligibility`) | The eligibility computation has no DP term, so the option is emitted `available: True` and the executor refuses it with `insufficient_resources` WITHOUT popping the dialogue — the proximate cause of the `--diplomacy propose` wedge, and a plain honest-availability gap of the kind this project has an explicit idiom against. A human is not soft-locked (`back_out_settlement` remains). | the option is disabled with its DP cost stated when the purse cannot pay it |
| **WO-D15** *(filed Aug 22, 2026)* an elimination leaves GHOST pairs in the war instance | **CARRIED, pre-existing** | the **war-instance owner** (`settlement_helpers.mark_participant_eliminated_in_all_wars`) | A dead nation's pairs are transited to PEACE by `world_state.py` while `diplo_key_meta` / `active_diplo_keys` keep them at `pair_status: "war"` — measured on the shipped scenario by turn 3–5. `assert_war_instance_invariants` raises on exactly this and has a production caller (`merge_war_instances` step 10); `WarInstanceInvariantError` is caught nowhere in `backend/`. No merge was observed in 476 probe-turns, so the crash is unproven — the invariant breach is not. | after an elimination, no `active_diplo_keys` entry names a pair whose `diplomatic_states` is not WAR |

> **Carried, not forgotten:** each row above has a STATUS tracking line in
> `docs/STATUS.md` under the row-WO exit block, and row WO's own definition of
> done (`WEIRD_OUTCOMES_SPEC.md` §5) requires all five to be gated or
> explicitly carried — which this block discharges for four of them and marks
> the fifth GATE-PENDING.

> **What NOT to change — recorded so a later pass does not "fix" it.** The
> sovereign-protection design held (25 turns of deliberate suicide failed to
> lose Napoleon, and Massena stepped in front of him); the CR-5 delegation split
> is the best surface in the build; the marshals out-extorted the tyrant; a
> pacifist France won its war through eleven autonomous jealousy attacks; the
> AI runs the estate/rente economy on itself unprompted; plunder's bill is real
> and shown; and the input surface refused a prompt injection, null bytes, RTL
> text, SQL and path traversal in Berthier's own voice with zero crashes across
> a 15,115-line console.

---

## Win-Attempt Campaign design questions — filed August 16, 2026

> **Evidence memo = `docs/audits/PLAYTEST_WIN_CAMPAIGN_2026_08_16.md`
> (authoritative), §5.** A France/1805 campaign played to WIN: 23 turns,
> Austria's army annihilated at Ulm turn 1, Austria out of the war turn 13,
> Russia at peace turn 21. Correctness rows are `BUG_FIXES.md` §WIN.
> **All OPEN — no gate has been held on these.**
>
> **The finding underneath all five:** the game's *war* systems are strong
> and its *consequence* systems do not pay them off. Every row below is a
> different face of "you won and nothing changed."
>
> ### ✅ GATE RECORD — WIN-D2 RULED AND BUILT August 16, 2026
> ### under the user's delegated grant ("make any fixes needed including
> ### [WIN-D2]"). AUTHORITATIVE. The other six rows stay OPEN.
>
> **Ruling: the player keeps what the player's army is placed to take —
> "The Spoils of War."** An AI will not take an undefended enemy province
> out from under a **co-belligerent who is better placed to take it**:
> if a nation allied to the AI, and itself at war with that province's
> owner, has strictly MORE strength adjacent to it, the AI passes.
>
> **Why this shape and not the alternatives.** A *war-aim reservation*
> system (claim provinces at declaration) and a *contribution-weighted
> post-war partition* were both considered and rejected for this pass:
> each needs new serialized state, new UI and its own gate, and neither
> addresses the actual measured moment — a single allied corps walking
> into provinces a French victory had emptied *while French armies stood
> next to them*. The chosen rule needs **zero new serialized fields**,
> lives in ONE predicate at ONE call site, and restores the missing
> agency directly: break the army, march up, and the ground is yours.
>
> **Properties, each pinned:** strictly-greater so the best-placed
> partner always acts and the rung cannot deadlock · adjacency-scoped so a
> distant ally never blocks · co-belligerent-scoped so a neutral or an
> enemy massing next door is never a reason to hold back · **symmetric by
> construction (GR5)** — it reads co-belligerents, not "the player", so
> an AI defers to another AI exactly as it defers to France · behind the
> flip lever `enemy_ai.SPOILS_DEFERENCE_ACTIVE` for BASELINE_SERIES
> attribution · GR8-safe (walks the target's own adjacency list, never
> `world.regions.values()`).
>
> **Measured.** The campaign's own phase 1, replayed: allied Bavaria went
> from **7 provinces at turn 6 (Vienna, Bohemia, Moravia, Hungary taken)
> to 3 — its boot count — with Austria's 7 still on the table for France
> to take.** `BASELINE_SERIES` and M1–M7 are byte-identical *without*
> re-record, which is a fact about the ambient harness (it never puts a
> stronger co-belligerent beside an undefended province), not proof of
> safety — so the behaviour is pinned directly instead, including a
> both-directions test on the real rung with a real `WorldState`.
>
> ### ✅ WIN-D3 + WIN-D5 RULED August 16, 2026 (user)
>
> **WIN-D3 — "ending war should send troops back to borders with free
> march orders."** Design authored as **`docs/WAR_WITHDRAWAL_SPEC.md`
> ("The Road Home")**; ⚠ **build gate pending at its §7** (four
> questions, all at recommended defaults). Shape: a temporary right of
> transit granted at the `set_diplomatic_state` chokepoint (PT-J1's
> lesson — `cleanup_war_end` is not reached by every ending), read by the
> ONE movement predicate `can_enter_territory` so all ~25 seams inherit
> it, plus an automatic 0-AP MOVE_TO home for every stranded marshal, on
> both sides (GR5). ONE new serialized field. The corridor **stays open
> while you march and closes if you stop**, which makes the duration
> number non-load-bearing and turns "what if it expires" into "you
> loitered".
>
> **WIN-D5 — the Emperor starts closer.** Ruled: boot Napoleon at
> **Lorraine**, adjacent to Swabia, beside Soult — whose corps his Guard
> was carved from — and historically where he was in late September 1805.
> ⚠ **the row's premise is corrected**: he CAN reach the front from Paris;
> it costs ~10 turns. A sovereign movement allowance was considered and
> rejected. Costs are stated in spec §9.2, including that the Seat is not
> active at boot and that `BASELINE_SERIES` will likely need ONE
> attributed re-record.
>
> **What this does NOT fix, deliberately:** an ally still takes provinces
> the player is not placed to take (correct — Bavaria took Tyrol in the
> verification run with no French corps adjacent, and that is the rule
> working). WIN-D4's rente insolvency is still downstream of how much
> conquest actually pays, so **the standing instruction holds: do not
> tune the rente constants until a played campaign re-measures income
> under this rule.**

| # | Question | Measured evidence | Notes toward an answer |
|---|---|---|---|
| **WIN-D1** | **Should the 1805 campaign have any victory condition, and what should it be?** | `turn_manager._check_victory_conditions` returns `{"game_over": False}` unconditionally — the `sandbox_mode` guard is the method's first statement. I knocked a great power out of the war and signed two peaces; **no surface anywhere — dispatch, ledger, gazette — treated it as progress toward anything.** No score, no objective list, no "what would winning look like" screen | Already owned by the **Victory & Objectives Pass (ROADMAP positions 12–13)** — this row is evidence for that gate, not a new one. What the campaign adds: the absence is felt most at the moment a war *ends well*, which suggests objectives should be readable mid-campaign, not only scored at the end |
| ✅ **WIN-D2** | **RULED + BUILT** — should the player be able to keep what the player conquers? ⭐ headline | France annihilated Austria's field army and gained **Tyrol**. Allied **Bavaria took Vienna, Bohemia, Moravia and Hungary** — going 3 → 9 provinces while France went 28 → 30. The mechanism is not a bug: French battles emptied those provinces, and the Bavarian AI walked into the vacuum | There is currently **no lever at all**: no way to reserve a war aim, claim a province before an ally reaches it, or partition in the player's favour after the war. Note the interaction with ES-7 — the estate/reward economy assumes conquest produces spoils to distribute, and here it produced almost none. Options worth arguing: war-aim reservation at declaration; an ally-restraint diplomatic instrument; post-war partition weighted by contribution (the `campaign_ledgers` PT-J2 substrate already measures contribution) |
| ✅ **WIN-D3** | **RULED Aug 16 — no. ✅ GATED AND BUILT Aug 16, 2026 as "The Road Home"; gate + landing record = `docs/WAR_WITHDRAWAL_SPEC.md` §7a, authoritative. All four §7 questions taken at the recommended default.** Should making peace strand the army that won it? | The turn Russia accepted peace: *"Cannot enter Podolia — it is controlled by Russia (diplomatic state: PEACE). Open borders or higher required."* Four corps left deep in the east, bleeding supply attrition, with no route home but a multi-turn march across newly-sovereign soil | Mechanically consistent with the D2 "Ally's Table" ruling (only ALLY-tier states grant passage). The question is whether a peace treaty should carry an automatic **withdrawal grace** — N turns of transit for forces already inside the signatory's territory — which is also the historically normal clause |
| **WIN-D4** | **Is the reward economy affordable at the rate victory generates claims?** | Two rentes cost **1,260 g/turn**. Net income fell **+2,456 → −215** across the campaign. Marshals demanded rewards *because* they kept winning; paying them is what made France insolvent. The loop reads: win → marshals demand → pay → go broke | Interacts with WIN-D2 — the reward economy is priced for an empire that grows, and conquest currently does not grow it. Fixing D2 may fix D4 without touching a constant. Do not tune the rente numbers before D2 is answered |
| ✅ **WIN-D5** | **RULED Aug 16 — start him closer (Lorraine), not a movement allowance. ✅ BUILT Aug 16, 2026 alongside WIN-D3; record `WAR_WITHDRAWAL_SPEC.md` §7a + §9. He boots at Lorraine beside Soult, one march from Mack at Swabia; the Seat is consciously NOT active at boot and two AI-Intent pins were amended on the record.** ⚠ the row's premise is CORRECTED: he *can* reach the front from Paris — measured, he arrives — it costs ~10 turns. Should the Emperor be able to reach his own war? | Paris is 5 provinces from the German front; marshals move 1/turn. Napoleon left Paris turn 2, had not reached the front by turn 11, and **fought in zero battles across 23 turns**. Row NP's whole kit — Presence, Shadow, Peril — is gated behind that march | Owner = row NP / its exit review. Options: a sovereign movement allowance, a capital-to-front posting action, or authoring him forward at boot. Note NP-6's memo is already open and this is cheaper than it |
| **WIN-D6** | *(measurement only — no new question)* | Jealousy confrontations fired **~1 per turn** through phases 1–2 (Murat, Davout, Lannes, Bernadotte, Murat, Soult, Ney…), in a campaign that was winning constantly | Feeds **CA9-D3** (the grievances-and-popups revisit, spec `PETITION_POPUP_REVISIT_SPEC.md`) — one more measurement, not a new row. The tutorial world was made jealousy-dormant for exactly this (TUT-F5) |
| **WIN-D7** | **Is a concentrated multi-marshal attack too cheap?** | Ulm, one turn: Ney lost 878 / Mack 14,334 · Davout 340 / 17,664 · Murat **60** / 18,802 — a 313:1 exchange on the last, ~40:1 overall. **50,800 of 52,000 Austrians for 1,278 Frenchmen**, ending a great power's army in a single turn | Balance, not correctness — and it is *dramatic*, which is worth protecting. But it is the reason the campaign's central decision (concentrate everything) has no counterplay. Any change belongs in the combat-sweep harness (M1–M7) with a re-record, not an ad-hoc constant |

---

## Comprehensive Playtest design questions — filed August 15, 2026

> **Evidence memo = `docs/audits/PLAYTEST_COMPREHENSIVE_2026_08_15.md`**
> (digest named per row). Design questions only — the correctness rows are
> `BUG_FIXES.md` §Comprehensive Playtest PC15.
>
> ### ✅ GATE RECORD — all four questions RULED + BUILT August 15, 2026
> ### under the user's delegated grant ("make decisions for design gate
> ### items … consult other agents"). Three design-counsel agents argued
> ### the options; the rulings below are AUTHORITATIVE. Tests =
> ### `tests/test_pc15_d_rulings_2026_08_15.py`.
>
> **D1 RULED: "The Closed Frontier" — option (a), the movement law.** The
> forced-retreat scan was the ONE mover exempt from `can_enter_territory`;
> it now admits a foreign candidate only under `OPEN_MOVEMENT_STATES`
> (PEACE/ARMISTICE soil drops below tier 5 — never chosen), in both the
> main scan and the Corunna sea-exit re-check; flip flag
> `RETREAT_MOVEMENT_LAW_ACTIVE` (the HOST_RULE_ACTIVE idiom). A cornered
> army capitulates in place — the fate machinery's capture arm, which is
> the historically exact 1805 outcome (Ulm, Prenzlau, Ratekau; even
> Blücher's neutral-soil crossing at Lübeck ended in surrender to the
> FRENCH). "Internment" is a 1907 institution (Hague V) — REJECTED for
> 1805 as a mechanic, and homed instead: **"The Interned Column" rider →
> owner = the row NP exit review** (rides the capture-worth/captivity
> machinery NP-5/NP-6 builds; completion = an army that would be captured
> on strictly-neutral soil is held by the NEUTRAL court and released at
> peace or by clause, behavior test named at filing).
>
> ⚠ **STATUS August 15, 2026 — the owner arrived, and the rider is PUT TO
> THE USER rather than silently carried.** The row NP promise audit
> surfaced it (record `docs/audits/NP_PROMISE_AUDIT_2026_08_15.md` §6)
> with a finding that changes the question: **D1's own ruling
> substantially narrowed the premise.** The forced-retreat scan now obeys
> the movement law, so an army can no longer retreat ONTO neutral soil at
> all — measured live, the scan prints *"Skip: neutral court (PEACE) — the
> frontier is closed"* and falls through either to a desperation retreat
> into at-war soil or to capitulation in place. The rider's case therefore
> survives only for an army ALREADY STANDING on neutral soil when it is
> cornered (it entered legally under `OPEN_MOVEMENT_STATES` and the state
> then changed) — rare. Live options: **(a)** build it for that narrow
> case; **(b)** CLOSE the row — capitulation in place is the 1805-exact
> outcome D1 already blessed, and a neutral-court holder adds a party with
> no other mechanics attached to it; **(c)** re-home to the Victory Pass,
> which owns endings and prisoners. **Recommendation: (b)**, with (c) as
> the fallback if the flavour is wanted later.
>
> ✅ **RULED August 15, 2026 (user): CLOSE THE ROW — option (b).** The
> rider is CLOSED, not deferred: capitulation in place is the 1805-exact
> outcome D1 already blessed (Ulm, Prenzlau, Ratekau — even Blücher's
> neutral-soil crossing at Lübeck ended in surrender to the French), and
> a neutral-court holder would add a party with no other mechanics
> attached to it. GR9 is satisfied by closure rather than by an owner:
> there is no remaining player-facing promise. Re-open only if a played
> campaign produces the narrow surviving case (an army already standing
> on neutral soil when it is cornered) and it reads wrong.
>
> Option (c)
> neutral-protest REJECTED outright (redundant under (a); deliberate entry
> is already illegal at the movement seam; the Ansbach trap keeps its
> authored scope). Riders built with it: the jealousy glory-hunt skips an
> enemy standing on soil the marshal can neither fight on nor legally
> enter (Berlin is safe from Lannes); a jealousy-AUTONOMOUS attack never
> stages the war-purpose dialogue (PT-F1's own principle — war decisions
> never ride a pursuit's momentum; the frontier line still prints); and
> the DP-shortage declaration refusal now rides `proposal_result_popup`
> so the modal chain always ENDS on screen (the "three modals of theater,
> no receipt" case). Pre-existing shape pinned consciously: the
> auto-charge combat copy shatters where the executor path would capture
> (no fate check there — the combat-copy-unification backlog owns it).
>
> **D2 RULED: "The Ally's Table" — hybrid of (ii)-collapsed-into-the-state
> + (iii); option (i) ally-depot REJECTED as dominated** (slow, weakest in
> mountains where the wound is, unfixable for the tutorial, new machinery
> for a number the multiplier reaches free). The alliance already opens
> the border (`OPEN_MOVEMENT_STATES`); it now opens the granary:
> `ALLY_SUPPLY_STATES = {ALLIANCE, DEFENSIVE_ALLIANCE, VASSAL}` soil feeds
> a guest army at the home `HOME_SUPPLY_MULTIPLIER` (1.5×, single-sourced)
> in `get_effective_supply_cap` — DELIBERATELY narrower than open
> movement: NON_AGGRESSION/OPEN_BORDERS hosts feed nobody (transit rights
> are not magazines — the Ansbach line). The naval verdicts follow the fed
> predicate (a strangled allied coast starves the guest; the lifeline arm
> unchanged for non-fed landings). The counsel half: Berthier's famine
> headline now NAMES the legal dispersal split with numbers ("X can feed
> N more — a corps marched there ends it"), headroom from the SAME
> effective cap the attrition applies and legality from the executor's own
> `move_refusal_probe` (CA9-F10 discipline); on fed ally soil the "not
> controlled by France" depot refusal is replaced by the honest "their
> magazines feed us as our own — the army is simply too large". Rider:
> the AI's P6.5 dispersal rung reads `get_effective_supply_cap` (its raw
> read was a pre-existing shown≠applied gap — it fled provinces that fed
> it). The tutorial's scripted famine ends with ZERO script edits (the
> lesson already authors France|Bavaria ALLIANCE; Swabia now feeds
> 60,000). The measured 4-corps Munich death-ball still starves at ~5.5%
> — the concentration tax is DESIGN and stands; what changed is that the
> remedy is named. Both `is_fed` flows are GR5-symmetric by construction.
> Deferred with owners: negotiable supply rights with a NEUTRAL host + the
> fund-an-ally's-depot verb → the next diplomacy/instruments (D5-family)
> gate; a region-panel "feeds your army: N" line → the standing visual
> sign-off pass.
>
> **D3 RULED: gate the STATE, not the beats.** The counsel's decisive
> finding: the expectation machine has real TEETH inside the 12-turn
> lesson (grace opens at 2 turns, `modify_trust` then erodes up to
> −3/turn — Ney's "9 turns old" escalation ≈ −15..−21 trust, which is
> exactly why his objection cited unrewarded victories), so a
> display-only mute would keep the bleed and remove its explanation.
> Built as the TUT-F5 PATTERN extended, not the TUT-F5 function:
> `dotation.dotation_dormant(world)` (the serialized `scenario_name ==
> "tutorial"` discriminator, same as TUT-F2/F5) folded into the ONE
> existing chokepoint `is_dotation_world` — every ES-7 surface (both
> dispatch blocks, the battle note, the card block, the reward/rente
> dialogs, the AI grant rung, the ESP arm) inherits the dormancy in one
> line — and `_process_dotation_state`'s inline duplicate of the rule
> replaced by the chokepoint call (the CA9 two-implementations trap,
> closed). Glory and `battles_won` still accrue (TUT-F5's own honesty
> rule: the record stays true, the claim DERIVED from it sleeps). NO
> reward beat added to the lesson — the syllabus is over-full and the
> school's doctrine for un-taught systems is dormancy; deliberately no
> player-facing promise, so nothing is deferred (GR9).
>
> **D4 RULED: the floor is necessary but was treating the SYMPTOM — four
> pieces built.** The counsel reconstructed the actual re-declaration
> from the committed run artifacts: the white peace left Bavaria holding
> MORAVIA (Austrian homeland, a 1-troop garrison detachment, no army),
> and P3.7 homeland defense — the ONLY AI attack rung with no
> diplomatic filter (its three siblings all gate on war) — marched back
> through the peace to the combat-seam auto-declaration the same turn.
> The filed hint's "war-entry reroll memory" is the WRONG store (a
> same-turn determinism cache); the RIGHT one is `armistice_cooldowns`,
> already consulted by every war-entry gate. Built: **(1)** the truce
> floor — `PAIR_EXIT_TRUCE_FLOOR_TURNS = 8` (4 months at HC-0's
> half-month turn; longer than a negotiated armistice's 5 — a collapse
> holds longer than a choice; worst-case churn ≥ 18 turns, a campaign
> season) written into `armistice_cooldowns` at the [r5] exit — one
> write floors every channel, zero new serialized fields,
> GR5-symmetric; **(2)** P3.7 gets its siblings' filter (recovering
> peace-held homeland belongs to the war council, never a pursuit rung —
> §4.3a-4); **(3)** status-quo-ante-lite — at the exit each court
> returns the OTHER's homeland provinces it holds with NO standing army
> (the Moravia shape), built as `territory_cede` terms through the
> negotiated path's own applier (`_apply_settlement_terms` — garrison /
> cache / threat / event invariants inherited); army-occupied ground
> stays (uti possidetis), and the congress beat now names what returned;
> **(4)** the dispatch dedupe — advance-stamped `third_party_peace`
> beats render exactly once (the T22–23 verbatim repeat). Deferred with
> owners: the declare-war ally CASCADE does not read the pair cooldown
> (a floored pair can be re-welded by a third court's fresh war —
> documented at the constant, owner = this row's residual); extending
> the floor to NEGOTIATED third-party peaces (same exposure, own quick
> check, same owner); `_pair_exit_this_turn` unserialized (pre-existing
> one-line note); the crisis_brewing/crisis_passed beats share the
> advance-stamped double-render SHAPE but carry pin-21 obligations —
> checked, left to their own owner if measured live.
>
> **BASELINE_SERIES: re-recorded ONCE for the whole gate slice** with a
> TWO-STAGE flip-experiment attribution (record = the constant's comment
> block in `test_ai_intent_threat_migration.py`): stage 1 proved the
> D1/D2 lever census complete (all-off reproduces the prior series
> byte-for-byte; the index-8 jump is the P6.5 shown≠applied
> unification); stage 2 attributes the D4 delta the same way. M1–M7
> byte-identical throughout (fixture single-front worlds — a fact about
> the harness, verified not assumed).

| Row | Question | Evidence | Notes |
|---|---|---|---|
| **PC15-D1** | **Should neutrality stop a broken army?** Mack's forced retreats toured Frankfurt→Berlin→Dresden (three neutral courts, two of them great powers) because the retreat scan only checks `allies=0, enemies=0`. Historical answer: internment. Cheapest honest answer: exclude neutral-controlled provinces from the forced-retreat scan (break in place if nothing else is legal). Interacts with PC15-5's whole family — an autonomous pursuer follows him in. | variance_jena T17–18, flagship-1805 T2 | The war-purpose ghost-chain (PC15-5c) mostly disappears if routed armies cannot enter neutral soil in the first place |
| **PC15-D2** | **What should a French army standing on an ALLY'S province be able to do about supply?** Four corps starved 14,610 men at Munich — Bavaria's own capital, France's ally in the war they were fighting — and the only counsel was "move a corps, or continue to pay." No ally-depot, no requisition-from-ally, no counsel to disperse ACROSS the two adjacent owned provinces. EC-7/ES-6 was cut with its intent re-homed to this headline; the headline is honest but the campaign shape (the liberating army cannot be fed on the liberated ally's soil) reads as a hole once armies mass forward. | flagship-1805 T6–T11; ulm/jena famine arcs; tutorial-lesson T6–T11 (the school's own beats park corps in famine) | Candidates: ally-soil depot at a premium · a Bavarian supply convention clause · or the headline counseling the LEGAL dispersal split explicitly |
| **PC15-D3** | **Should the dotation-expectation nag run inside the School of War?** TUT-F5 made the lesson jealousy-dormant, but the expectation producer is separate: "Ney's grievance is 9 turns old… a question of the army" fired twice in the 12-turn lesson and Ney's T9 objection cited "his victories remain unrewarded" — teaching a system the school never introduces. | tutorial-lesson T8/T12/T9 | One-line dormancy gate on the expectation beats under `scenario_name == "tutorial"`, or an explicit reward beat in the lesson |
| **PC15-D4** | **Does the exhausted-pair peace need a truce floor?** Same-turn peace-and-redeclare (austerlitz T17) makes the congress beat weightless — the [r5] exhausted-pair exit and the AI war ladder don't read each other's cooldowns. | variance_austerlitz/jena saves | A pair that white-peaced out of exhaustion should not re-enter for N turns (the war-entry reroll memory exists — point it here) |


## CA9 Design Answers — ✅ ANSWERED Aug 9, BUILT Aug 9–10, REGRESSIONS CLOSED BY ROW PT

> **Record = `docs/audits/CA9_GATE_ANSWERS_2026_08_09.md` (authoritative).**
> **Routing reconciled Aug 14, 2026 (health-check gate):** all three WERE
> built before the Aug-10 playtest that then measured them (the war-age
> penalty PASSED live −30/−15/0; the D2 gate's input defect and the D3
> delivery-seam AP refresher were the playtest's row-2/row-3 findings, both
> closed by row PT Aug 12–14, with PT-J2 landing D1's battle/territory
> re-weight). **The only outstanding acceptance is the played 20-turn
> campaign showing the D2 gate arm fire once — owned by row PT / the HC
> queue** (`docs/audits/HEALTH_CHECK_DESIGN_GATE_2026_08_14.md` §8). The
> table below is the historical contract:

| Row | Decision | Owner / landing | Done when |
|---|---|---|---|
| **CA9-D1** peace terms | F14 STAYS; the cheese is the cheap SCORE, not the recommendation. Battles + decisive are ±50 of ±100 with zero territory (EU4 caps battles at 25%); no term reads the war's AGE. Recommended: war-age penalty on acceptance FIRST, battle/territory re-weight after the playtest | `diplomacy.calculate_war_score` + `settlement_scoring`; next session | A short war cannot be settled for cash; a genuinely won war still has an exit (watch the TERRITORY arm); acceptance breakdown NAMES the new term; `BASELINE_SERIES` re-recorded with flip-experiment attribution |
| **CA9-D2** attack confirm popup | Arm only when band is `unfavorable` (not `even`) AND the marshal is `cautious`. Preview still prints honest numbers on every attack; only the BLOCK narrows | `combat_executor._execute_attack` muster gate; next session | An aggressive marshal charges bad odds unasked (in character); a cautious one asks; one predicate decides both the popup and the copy; CR-5's own bad-odds gate untouched |
| **CA9-D3** grievances + popups | A REVISIT slice, NOT a TTL on N4. Audit every popup producer, queue slot, blocking class and retirement path, then fix. **AUDIT + FIX DESIGN COMPLETE Aug 15, 2026 (PC15-10 attached the number: 19 petition modals in 24 flagship turns) AND THE §6 GATE RULED THE SAME DAY at the recommended defaults under the user's delegated grant ("establish recommendation yourself"): spec + gate record = `docs/PETITION_POPUP_REVISIT_SPEC.md` v1.1, authoritative** — §2 ledgers what already landed (N4 half-fixed by A3/PT-A1, N8 fixed by A9, N21 half-fixed by A13, A4/A10 done, the objection-leak item REFUTED on master), §4 designs the remainder (F1 "The Antechamber" tier split · F2 subject-linked retirement · F5 four latents incl. the cappable mutual-spiral beat · F6 W7 preempt · F7 three surviving drains + census pin · F8 justified queue order · F9 stash-and-raise chokepoint · F10 load validity), §6 = the RULED gate (Q1(a)/Q2(a)/Q3/Q4/Q5 + the Q1 L1-liveness re-open condition riding §8) | **BUILD-READY** — next session builds per spec §9 (B0 → B1 → … B5, all clear). Old starting list superseded by spec §2/§4 | Every producer has a retirement path; nothing blocks a channel indefinitely; the queue order is justified rather than accreted — mapped to fixes in spec §4 preamble; acceptance = spec §8 (≤9 modals/24 flagship turns, zero silent losses) |

**Then ONE playtest** covering the three new slices AND the 31 rows landed
August 9 — which also discharges the owed visual sign-off on `Supply: Unknown`
(region panel + map tooltip) and the per-court fog line.

---

## HC-D1 — Glory as a diplomatic TERM (the mechanical half of HC-3)

> **Filed August 14, 2026 by the health-check design gate**
> (`docs/audits/HEALTH_CHECK_DESIGN_GATE_2026_08_14.md` §4). HC-3 built the
> FLAVOR half only: envoy refusal/capitulation variants naming the opposing
> crowned (★) marshal (`diplomatic_templates.crowned_name_clause` /
> `crowned_incoming_clause`, display-only, GR6). **The mechanical half — an
> acceptance/intent term that READS glory (a crowned marshal on the border
> pricing into a court's willingness to sign or to fight) — is deliberately
> NOT built.**

| Row | Owner / landing | Done when |
|---|---|---|
| **HC-D1** glory → acceptance/intent term | **The Victory & Objectives Pass gate (ROADMAP positions 12–13)** rules it in or out | A gate ruling that BUILDS it (named acceptance component + shown-in-breakdown + test file named there) or REJECTS it with reasons recorded in that gate's record; either disposition closes this row |

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Player Feedback (Wave 3 remaining) | 7 | Open — R129/R128 → 8.EVAL triage; R131/R132/R17d-f → queue item 6 (8.EVAL) |
| Nation Rivalry System (EU4-inspired) | 1 | Superseded by Memory and Pressure v2.4.3 (COMPLETE); dynamic-agenda residual → queue item 5 |
| Territorial Promises (Wave 3) | 1 | ✅ LANDED April 2026 as war bargains (`WAR_BARGAIN_SPEC.md`) |
| War System Overhaul (EU4-inspired) | 4 | ✅ LANDED — war_objectives / power cap / forced_alliance / liberation live in code |
| AI Diplomacy Improvements | 3 | N1 verified live; A4 historical note; A3 residual rides queue item 5 (8.EVAL) |
| Gold Sink Options (B4) | 1 | Re-pointed → `docs/ECONOMY_REVISIT_SPEC.md` EC-2 |
| Wave 4 — New Features | 19 | **✅ DISPOSED at 8.EVAL July 16, 2026** (`docs/audits/EVAL_8_2026_07_16.md` §2): R117/R59/R153/R154 already handled; R26 → EC-5, R161 → EC-8, R158 → CR-7, R162 stays gated behind the Nation-Agendas gate; R22/R25/R27/R35/R118/R127/R133 → the Pre-EA Diplomacy & Flavor Content Menu row; R32/power_score/R24/R33/R36 DROPPED with reasons |
| Wave 5 — Game Review Findings | 8 | **✅ DISPOSED at 8.EVAL July 16, 2026** — routed items verified: R155/R157 residuals ride the promoted Nation-Agendas core + landed voice work; R152 residual folds into the closed queue-item-6 record; R158 → `docs/COMMAND_ROBUSTNESS_SPEC.md` CR-7 |
| Jealousy System | 1 | Separate design gate; Marshal Content Pass MC-3 now an effective prerequisite |
| **Wave 6 — Creative Capstone (July 10, 2026)** | 14 | **✅ APPROVED IN FULL July 10** (6 expansions + 6 escalations + 2 gate additions: Dynamic Battle Naming, Literal Doctrine); owner = `WAVE6_FUN_FACTOR_SPEC.md` (12 build slices W6-0..W6-11) |
| **Estate Second Pass deferrals (July 11, 2026)** | 4 | **ESP-1 + ESP-2 + ESP-4 ✅ LANDED July 11, 2026 with the Jealousy v3.2 build** (ESP-4 folded per its own row's fold-in clause; record = `JEALOUSY_SPEC.md` §0.3/§0.4, tests `test_estate_riders_esp.py`); ESP-3 respect-by-treaty → diplomacy gate (unchanged) |
| **Total** | **63** | |

---

## Health-Check Design Gate — Deferred Riders (August 14, 2026)

> **Gate record = `docs/audits/HEALTH_CHECK_DESIGN_GATE_2026_08_14.md`
> (authoritative — row HC, six slices HC-1..HC-6, queued NEXT).** These are
> the halves that gate DEFERRED with owners (GR9):

### HC-D1: Glory as a Diplomatic Term (the mechanical half)
- **Category:** Diplomacy depth
- **Summary:** An acceptance/intent modifier reading the opposing side's
  top-glory (★ crowned) marshal on the relevant front — courts genuinely
  priced Napoleon's marshals into negotiations. The FLAVOR half (envoy
  lines naming the crowned marshal) is HC-3, building now; this row is
  the term that would move numbers.
- **Owner / landing:** the Victory & Objectives Pass gate (ROADMAP
  positions 12–13) — glory pricing belongs with the campaign-arc pass.
  Fits the existing `agenda_settlement_mod` pattern (a named ±N component
  on the acceptance breakdown, shown = applied).
- **Done when:** that gate builds it (named component + breakdown row +
  `test_hc_d1_glory_term.py`) or explicitly rejects it with the reason
  recorded here.

*(HC-5's "The Congress" second lesson is homed on the Pre-EA Onboarding &
Teaching Pass row below; HC-6 Seasons & Weather is not a deferral — it is
queue position 6 of row HC, ending in its own USER gate.)*

---

## Creative Audit — Design Items (August 4, 2026 — **GATES HELD August 7, 2026**)

> Source: `docs/audits/CREATIVE_AUDIT_2026_08_04.md` (17-turn live France/1805 campaign at
> master `e450b02`, 80-agent find→refute fleet). These are **design calls that need a gate** —
> the defects from the same audit are routed to `BUG_FIXES.md` §Creative Audit.
> Per **GR9** each row names an owner; none may be built inside an audit.
>
> **⚖ CLOSE-OUT August 7, 2026 (user-delegated; gate record =
> `CREATIVE_AUDIT_2026_08_04.md` §10, authoritative): D2, D4 and D6 were HELD and their
> rows BUILT the same session** (landing record `BUG_FIXES.md` §Creative Audit close-out
> block; tests `test_ca8_gate_closeout_2026_08_07.py`, 46). **D1 and D5 transfer to the
> re-planned roadmap's ECON BALANCE position** (the pre-build EC-P3 gate+build the user
> ordered Aug 7 — "econ is still unbalanced"); **D3 attaches to the Marshal Voice Tier 1
> slot's gate** (the next marshal-content gate, now also pre-build).

| id | the finding | owner row | the question the gate must answer |
|---|---|---|---|
| **CA8-D1** | The conquest-free gold sink is **13 building slots for the whole game** (`region.py:107-113` × France's 1 capital / 4 major_city / 7 city; `BUILDING_TYPES` tops out at 400g) → lifetime sink 3,250–5,200g, **under two turns of net income**. Measured: treasury 671g → **29,496g** (44×) in 13 turns, with **88% of everything France earned unspendable** | **row EC-P3** (existing econ backlog owner) | What does gold buy after turn 6? Landing slice must define completion. The plunder prompt quoting a flat 600g for every 150-income city is downstream of this, not a separate row |
| ~~**CA8-D2**~~ ✅ **HELD + BUILT Aug 7, 2026** (§10.1: leverage keys to the WAR — `calculate_side_war_score` / `sum_stored_side_score` / `get_side_war_score_for`, three consumers; a cession requires `war_score < -20` STRICTLY) | Settlement leverage keys to a **pair**, not the war. `compute_side_pressure_score` already knew Austria sat at **43** while the war-status row and the offer producer both read the raw France↔Britain **0**. CA8-27 is the outgoing mirror: the peace generator concedes territory whenever `relation < -50`, i.e. in every war | **Pre-EA Victory & Objectives Pass** (existing open gate — war score → terms → ending is exactly its business) | Should the counterparty's leverage key to the war the player is actually fighting, and should a cession require a losing war score rather than hostile relations? Both have blessed-number consequences on acceptance and offer generation |
| ~~**CA8-D3**~~ ✅ **HELD + BUILT Aug 8, 2026 at the position-9 slot** (user-delegated; **gate record = `JEALOUSY_SPEC.md` §0.5, authoritative**): both questions YES — Q1 rival MEMORY in `find_jealousy_target` (a man his envy already fired on is preferred while still above; no history = one-rung-up byte-identical; `JEALOUSY_RIVAL_MEMORY` flip flag; GR5 through the single source) + Q2 the §6 confrontation latch widened to once per (pair, escalation level), keys `A|B@Ln` in the existing seen-list, legacy bare keys = level-0 seen, bounded 4/pair/campaign, level-register body clauses; M1–M7 + `BASELINE_SERIES` byte-identical without re-record; `test_ca8_d3_rival_permanence.py` (19) | The rival is not a person. `find_jealousy_target` (`jealousy.py:268`) recomputes from a rolling 8-turn window with no bias from `jealousy_history`; Murat's rival changed **four times** in twelve turns. One petition per pair per campaign, ever (`jealousy.py:558-563`) — one fired, on turn 1, and was re-served fifteen times | ~~new row, next marshal-content gate~~ **CLOSED** | Should a marshal's grievance object have permanence, and should a petition re-fire when the escalation level rises? **YES + YES** |
| ~~**CA8-D4**~~ ✅ **HELD + bounded build LANDED Aug 7, 2026** (§10.4: three non-fear frames — arithmetic/interest, opportunity, history/law; a third variant in all 24 hegemony banks; full roster authoring across the other four reasons stays DEF-1's) | `hegemony_pressure` monoculture, rotated by `(turn + len(name)) % len(variants)`. **Row corrected Aug 4, 2026 (CA8 sweep 4) — three of its own facts were wrong, and the correction changes what the gate is for.** It is **19 named speakers + 5 registers over 24 banks = 48 lines, of which 38 are bespoke**, not "8 courts" — the authored surface is twice what the row credited and it is good. It is pinned **once**, on one bank (`test_w6_incoming_voice.py:118`), not twice: a third variant injected into all 24 banks runs the FULL suite at `1 failed / 16,280 passed`, so **all 19 bespoke banks grow with zero pin flips** and the "growing the banks is a conscious flip" cost model was false. And the **re-key is cosmetic churn — do NOT build it**: with two variants the key's image is `{0,1}`, so any turn-independent term is a phase shift, and the 19 courts hold DISJOINT banks so `len(nation_name)` decorrelates nothing. The measurement that settles the row is neither lexical nor structural: **72% of all diplomat lines composed in a 40-turn campaign are exact repeats** (Ottoman: 12 asks, 2 distinct lines), so bank SIZE is the only lever. Two gate-free defects were split out and FIXED in sweep 4 (Hardenberg's first line was the generic register line with `{nation}` pre-filled; a named envoy lost his authored attribution — `Araujo, measuring the room:` → `Araujo:` — whenever his reason had no bespoke bank, which is 16 of 19 courts on `agenda_pursuit`) | **DEF-1 Roster Voices** for the authoring; the 6-turn cooldown numbers (`ai_diplomacy.py:49-50`) are W6-10's, blessed, and carry AI-behaviour exposure — not DEF-1's to fold in | **Question rewritten.** The old one (*"Does the enemy phase get its own voice register?"*) aims at `enemy_phase_dialog.gd`, which is CA8-6/CA8-21's surface, not `compose_incoming_diplomat_line`. The open question is: **what else may `hegemony_pressure` sound like besides fear?** 85% of the 48 lines say "France is big"; writing 24 more in that frame spends the budget and measurably changes nothing. Exactly one line already escapes it — Castlereagh's *"London does not negotiate from fear; it negotiates from arithmetic"* — and it is the model |
| **CA8-D5** (→ the pre-build **ECON BALANCE position**, Aug 7, 2026 re-plan; CA8-18 landed Aug 4) | The threat bar sat at **91–97 for all 12 turns**, so position 3.5's new `military_establishment` term (`coalition.py:729-762`) was **unmeasurable in play** — it fired into a bar already at its ceiling | **row EC-P3**, now scheduled as the pre-build econ position | Does anything new need to be measurable on a bar that boots near its ceiling? |
| ~~**CA8-D6**~~ ✅ **HELD + BUILT Aug 7, 2026** (§10.2: the briefing MAY lead with a victory — `enemy_eliminated` 93 / `capital_stormed` 92 / `victory_won` 73 / `region_taken` 68; at equal scale the wound still leads) | **The morning dispatch has no headline class for a French success.** `HEADLINE_WEIGHTS` = 15 classes raised from 17 `_add()` sites; every one is a wound, an opportunity ranked below every wound *by comment* (`dispatch.py:71-73`: *"an opportunity never outranks a wound"*), or another power's business. There is no `region_taken`, `battle_won`, `capital_stormed` or `enemy_eliminated`. **14 of 14 headlines this campaign were misfortunes.** On the turn France stormed Vienna **and** Austria was eliminated, the lead was `stand more men over what Bohemia can feed`. The good news exists, but only in a notification bar where **8 of 20** entries are the same `dotation_erosion` nag — and the best-written sentence of the campaign (*"Austria has seized Carniola, the estate that funded Marshal Ney's honor. He will not forget it, Sire."*) is a notification title | **new row, next narration gate** — pairs with the Aug-3 enemy-phase-as-theater dissent that moved the composition slice to position 3 | Should the briefing be able to lead with a victory, and at what weight against a wound? The decision to revisit is that comment. Note this is the standing explanation for why narration scores 6 while event generation scores 8 — the events are good and the editor only publishes bad news |

**Not deferred, closed at filing:** CA8-20's player half is **XR-4**; its AI half belongs beside
IGR-X4 / IGR-X9 at **EC-P3**'s next econ tuning gate and needs no new row.

---

## Live-Playthrough — Design Items (August 1, 2026 — ✅ ALL FOUR LANDED same day, second session)

From the played-world creative-audit re-measure (memo = `docs/audits/AI_V_SWEEP_2026_08_01.md`
§10). **All four landed August 1, 2026 (second session) under the user's delegated grant,
alongside PT-F1/PT-F6** (whose struck rows in `BUG_FIXES.md` §Live-Playthrough carry their
records). Struck rows below carry these landings.

| ID | Item | Why it matters | Landing / completion |
|---|---|---|---|
| ~~PT-D1~~ ✅ **LANDED Aug 1, 2026** | ~~**Muster one-voice odds.** The muster header states joint-force odds while the personality line in the SAME message states solo odds.~~ | Both frames now labelled. | **Landed exactly as specified:** the header names the committed joint figure ("Ney (24,000; 41,000 with the muster committed) … the balance of force looks favorable" — the figure the CO-2 verdict is actually priced on, `_format_muster_lines`), and the cautious solo line says "at unfavorable odds **alone**" whenever `committed_attacker > 0` (`combat.py` — the −10% stays priced on the solo ratio, which is the blessed mechanic; the copy names its frame). Legacy solo copy byte-stable. Tests: `test_enemy_phase_presentation.py` §TestMusterOneVoiceOdds (5). |
| ~~PT-D2~~ ✅ **LANDED Aug 1, 2026** | ~~**Diorama contingent taxonomy.** Soult (REFUSED to march) rendered `failed_arrive`; Murat (promised, failed his roll) absent entirely.~~ | Refusal, failed roll and silent drop are different dramas. | **Landed as specified:** statuses {refused, failed_arrive, out_of_reach} — refusal keyed on the Session-61a trust-dock taxonomy (`literal_personality`/`eyes_on_a_crown` → `refused`; `low_score`/`fate_intervened` keep `failed_arrive`); **muster-promise parity** via `_inject_muster_promises` (the WILL JOIN rows ride into `build_battle_diorama`; a promised name the resolve ladder silently dropped shelves as `out_of_reach`); `_cap_side` + the two `.gd` predicates read the absence family as a set. Spec vocabulary updated (`BATTLE_DIORAMA_SPEC.md` §7). Tests: `test_battle_diorama.py` §TestContingentTaxonomyPTD2 (5) + 2 flipped pins. |
| ~~PT-D3~~ ✅ **LANDED Aug 1, 2026** | ~~**Letter-book label coherence.** Digest rows titled "Gift of Friendship" whose own clauses read "Proposal: Open Borders Agreement".~~ | Header/body mismatch erodes trust in the letter-book. | **Landed:** the row title follows the terms-derived `proposal_type_display` the payload already carries (falls back to the context label), so the title always matches the lead clause; the STABLE `proposal_type` stays untouched for the batching predicate (the smuggling guard test still pins it). Tests: `test_igr_f_envoy_digest.py` +2. |
| ~~PT-D4~~ ✅ **LANDED Aug 1, 2026** | ~~**Move-chain presentation.** One corps chaining 3–4 moves per enemy phase reads as teleportation.~~ | The loudest contributor to "enemy phase as theater: 5.5". | **Landed as specified:** `main._collapse_enemy_move_chains` — after the fog filter, chains of 3+ hop-continuous moves per marshal collapse into ONE `forced_march` entry (stages named = the destinations today's bullets already disclosed; ORIGIN named only at FULL intel — the one name the old bullets never leaked; attrition summed; conquest events preserved so a recapture chain still lists each fall under the one march line; a marshal's own non-move action or a hop discontinuity breaks the chain; other marshals' interleaved entries don't). Presentation only — runs at the view layer, moves untouched; totals/summary invariants kept. `enemy_phase_dialog.gd` gained the render arm. Tests: `test_enemy_phase_presentation.py` §TestMoveChainCollapse (8). |

---

## In-Game Review — Design Items (July 25, 2026)

From the live NA-6c/6d + AI-3r cross-element pass. Memo:
`docs/audits/INGAME_REVIEW_2026_07_25.md`. Correctness defects went to `BUG_FIXES.md`
§ In-Game Review July 25; these three are design calls, not bugs.

**All three are owned by row IGR, `docs/INGAME_REVIEW_FIXES_SPEC.md` (v1.0, ✅ GATE BLESSED
July 25, 2026 — gate record = spec §5, authoritative):** IGR-D1 is DECIDED at
`PLUNDER_INCOME_MULTIPLIER = 4` (blessed, in-band tunable, with a falsifiable acceptance test and a
recorded dissent that the stability-vs-authority re-cut is the better design if the number fails
twice); IGR-D3 is DECIDED as the `create_client`-carries split. Mapping: IGR-D1 → **IGR-E** (gate Q4) ·
IGR-D2 → **IGR-F** (gate-free) · IGR-D3 → **IGR-D** (gate Q2 — the same question as `BUG_FIXES.md`
IGR-3). **✅ ALL THREE HAVE LANDED** — IGR-D July 25, IGR-F July 26, IGR-E July 26 — and the rows
below are struck accordingly. *(Spec §3 requires routed rows to be struck on landing; IGR-D2 and
IGR-D3 had been left un-struck by their own sessions and are closed here too.)*

| ID | Item | Why it matters | Landing |
|---|---|---|---|
| ~~**IGR-D1**~~ | ~~**Plunder is economically irrelevant.** Plundering Nassau yielded **87 gold** against 3,085/turn income and a 5,177g treasury. Secure (stability 25) is strictly correct in every situation I met, so the post-capture choice has no tension.~~ **✅ LANDED July 26, 2026 as IGR-E** (landing record `INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-E, commits `c7e30b9` + `88e2707`). | ~~A per-conquest decision the game stops to ask about should cost the player something to answer.~~ **Done both ways the row asked for:** priced (`PLUNDER_INCOME_MULTIPLIER` 1.75 → **4.0**; Nassau 87 → 200g, the median province 262 → 600g) **and made legible** — no surface stated what Plunder would pay before the choice; now the modal button, the terminal sentence and both refusal restatements quote it, from the same expression that pays it. ⚠ The gate's worked example ("Nassau ~450–750g") is WRONG and is corrected in the landing record: 450–750 is the MEDIAN province, Nassau is the map minimum. | ✅ LANDED — `tests/test_igr_e_plunder_prompt.py` (30). **⚠ THE RECORDED DISSENT LIVES ON:** option (b), the stability-vs-authority re-cut, is arguably the better *design*; **if the falsifiable acceptance test fails at TWO different multipliers, re-open at (b) rather than tuning a third time. Attempts used: ONE of two (×4, PASSED).** |
| ~~**IGR-D2**~~ ✅ **LANDED July 26 as IGR-F** | **Minor-court envoy spam.** Turns 2–5 delivered ~3–5 near-identical Open Borders / Non-Aggression proposals per turn from minors, each a blocking modal that interrupts a command already in flight (the typed order echoes, then its result is deferred behind the popup). The voices are genuinely good — Reis Efendi, Einsiedel, Consalvi all distinct — but volume flattens them. | The per-nation voice work is some of the best writing in the game and it is being spent on a queue the player learns to click through. | Batch into a single "the small courts write" digest with per-row accept/decline; owner = the next diplomacy polish slice |
| ~~**IGR-D3**~~ ✅ **LANDED July 25 as IGR-D** | **Should identity clauses survive the bilateral substitution?** (mirror of `BUG_FIXES.md` IGR-3.) The blocked-settlement path offers "Make peace with X only", promises the drafted terms carry, and drops `create_client` / vassalage / liberation by design. | This is the difference between the NA-6 carve being a headline feature and a feature most players will never complete. | Needs a user gate — carry identity clauses, or steer back to the joint route when one is drafted |

---

## Econ War-Coupling — Deferred Riders (July 17, 2026)

> From the EC-W research pass + build (gate record `docs/audits/ECON_WAR_COUPLING_RESEARCH_2026_07_17.md` §5;
> the build landed EC-W1..W5 the same session). These riders were considered and
> consciously deferred with owners — not silent scope.

| ID | Pri | Item | Design shape | Owner / landing |
|----|-----|------|--------------|-----------------|
| ~~EWC-D1~~ ✅ **BUILT Aug 7, 2026 at the Econ Balance gate** (EB-5a "Requisitions of War", `ECON_BALANCE_GATE_2026_08_07.md` §3; `REQUISITION_RATE = 0.25` × base income to the STRONGEST disruptor, its own positive "Requisitions" Net component, GR5 both directions — boot: Austria +37 from Mack@Swabia. The snowball objection was structurally dissolved by EB-1: extraction lands in a chest taxed at the war rate while the war lasts. `test_econ_balance_eb.py::TestRequisitions`) | P2 | **Occupier-side extraction** — EC-W1 suspends a disrupted province's income to its owner but credits the invader nothing ("consumed in place"). The historical rider: a fraction flows to the occupier's treasury ("la guerre doit nourrir la guerre") | One constant (e.g. 30% of base income) + a positive "Contributions" ledger component on the invader's side, riding the same `get_disrupted_regions` substrate; deliberately NOT in v1 because crediting the winner accelerates the offensive snowball the pass was correcting | ~~Next econ tuning gate~~ ✅ landed |
| EWC-D2 | P2 | **Casualty→manpower-pool drain** — battle deaths never touch the pools (root-cause 5), so a nation bled white re-raises its army from an untouched reserve | Battle casualties drain the loser's (or both) infantry/cavalry pools at some fraction; needs an AI-impact study first (P1 recruit + P1.75 commission rungs must keep functioning at low pools) | Pre-EA Balance Pass; test = pool depletion + AI-rung survival |
| EWC-D3 | P3 | **Captured-marshal ransom** — Bernadotte sat captured with zero economic consequence; historically ransom/exchange negotiations carried real prices | A ransom demand event on the W6-7 capture substrate (petition/notification channel), priced to the captor's leverage | Future diplomacy/drama gate |
| PTJ-D1 | P3 | **Pooled allied dead bill the primary nations' pensions** (PT-J review round [P3-5], Aug 14 2026) — the campaign ledger's casualty accrual reads the battle producers' POOLED side totals (the CA8-1 whole-army figure incl. allied reinforcements' dead), attributed to the two primary nations, so France's `pensions_of_the_fallen` term can bill Bavarian dead and the blood differential skews with them. Figure shape pre-existing; PT-J2/J3 make it economically visible for the first time | Thread `casualty_distribution` (already computed for the diorama) through `record_campaign_casualties` so each participant nation's ledger row takes its own dead; completion = a coordinated battle's ledger rows sum per-nation to the distribution, pinned both sides | **EC-2 pass 2** (the econ gate that owns ES-4/ES-7b); test lands with the slice |

**Cut with reasons (memo §5):** loans/inflation spiral (anti-sandbox), a separate battle-devastation slice (battles already write `war_damage`), home-front stability drag keyed on war score (double-dips EC-W2 illegibly), flat `WE × rate` drain (Austria's +18 boot margin — superseded by the treasury-fraction form), recurring-rails indemnity restructuring (lump + existing recurring presets suffice).

---

## Sweep-5 — Design Items (July 16, 2026)

> From the Combat Overhaul Sweep-5 12-component review (memo
> `docs/audits/SWEEP_5_2026_07_16.md` §5). CONFIRMED, adversarially verified,
> pre-existing (not Sweep-5 regressions). Correctness-tier siblings live in
> `BUG_FIXES.md` §Sweep-5.
>
> **Dispositions set at 8.EVAL July 16, 2026 (`docs/audits/EVAL_8_2026_07_16.md`):
> S5-D1 → ✅ **BLESSED + LANDED July 16, 2026** via the CR-6 mini-gate (record
> `COMMAND_ROBUSTNESS_SPEC.md` §7) · S5-D2 → KEEP 8.5 Batch Q · S5-D3 → DEFER to the next refactoring
> slice (row in §8.EVAL Dispositions below; VS-4 single-sourcing is the priority
> element).**

| ID | Pri | Item | Design shape | Owner / landing |
|----|-----|------|--------------|-----------------|
| S5-D1 | ✅ **LANDED** | **Bare "attack" bypasses every gate** — with no marshal named, `_execute_general_attack` auto-picks a never-addressed marshal into a real battle, skipping CR-2 clarification, the W6-4 muster gate (no `command` kwarg at the resolve call), AND the objection gate (needs `marshal_name`). Long-standing WAD (pre-CR-2), but by post-CR-2/W6-4 standards the most ambiguous lethal order gets the fewest gates; four independent Sweep-5 reviews converged on the same fix | **✅ BLESSED + BUILT July 16, 2026 via the CR-6 mini-gate.** Resolve-and-rewrite at the dispatch seam (`CombatExecutor.resolve_auto_attack` in `executor.execute`): (a) >1 commandable marshal in enemy contact → `build_contact_attack_clarification`; single-contact keeps the instant pick; (b) rewrite to a named `attack` so the W6-4 muster gate arms; (c) the auto-picked marshal flows through the objection block; E-CA-4 subsumed. GR5 carve-out for AI/strategic/autonomous. NO pins flipped — gating is at the dispatch seam, so `test_auto_assign_attack.py` stays green; new pins in `test_cr6_bare_attack_gating.py`. | ✅ LANDED — gate record `COMMAND_ROBUSTNESS_SPEC.md` §7; `test_cr6_bare_attack_gating.py` (12) |
| ~~S5-D2~~ ✅ **LANDED July 16, 2026** (Batch Q Chunk 1 — `strategic_executor.py`:604, pinned `test_batch_q_fixes.py`) | P2 | **PF-8 issuance-time passability honesty** — "march to Copenhagen" printed a route through neutral Prussia/Sweden; the closed-border stall fires only at the border hop, so the player spends 2 AP + a turn to learn what the game knew at issuance | Issuance rider naming the closed crossings ("via closed Prussian territory — requires open borders or war") when the formed path fails `_region_passable_for`; no pin conflicts | PF-8 follow-on row; lands with the next parser/UX batch |
| S5-D3 | P3 | **Architecture hygiene batch** — duplicated `_edit_distance_le2` (validation.py local vs parser helper, deliberate to avoid a leaf→layer import), the byte-mirrored VS-4 withholding predicate (combat_executor ↔ muster preview), leaf→layer lazy imports (authority→diplomacy) | Consolidation pass: a shared leaf util module for edit-distance; single-source the VS-4 predicate; document-or-lift the lazy imports | Architecture hygiene row; batch with the next refactoring slice |

---

## Vassal Playtest — Design Items (July 14, 2026)

> Routed (not bugs) from the July 14 vassal playtest + 14-agent verification. Bug fixes landed the same session (`docs/BUG_FIXES.md` §Vassal Playtest Findings); memo `docs/audits/VASSAL_PLAYTEST_2026_07_14.md`. These are intent/legibility/enhancement calls, not defects.

| ID | Pri | Item | Detail | Owner / gate |
|----|-----|------|--------|--------------|
| VP-D1 | P3 | ✅ **WIRED July 16, 2026 (Vassal Depth Slice 0)** — Garrison-as-a-real-loyalty lever | Wired **presence-based, flat +2** (`GARRISON_LOYALTY_BONUS`, single-source `lord_garrison_present` in `vassal.py`): a lord-nation corps standing in the vassal capital OR a lord-CONTROLLED capital holding real `garrison_strength`; the vassal's own boot garrison never counts. The authored +5..+8 ladder was deliberately DISCARDED (at −2 drift it made the loyalty economy decorative). Full value in the VS-R spiral band (a deed, not a cheap one-shot). Healthy `recovery_hint` re-advertises it; `/debug/vassal_loyalty` mirrors the same predicate. Tests: `test_vassal_slice0_substrate.py` + 4 reworked garrison test sites. | ✅ done (Slice 0, commit `1082382`) |
| VP-D2 | P3 | **Muster odds band omits the defender baseline edge** | The muster "odds"/"balance of force" band (`objection_v2.inferred_attack_odds_band`) folds terrain + fort but NOT the always-on +20% `defender_bonus`, defender DEFENSE skill, ±10% variance, or the 2d6 — so "favorable" reflects force balance, not the casualty exchange (playtest: a "favorable" attack lost 8,819 to inflict 469 into mountains vs a cautious defender). F2 reworded the label to "the balance of force looks …"; the deeper fix (fold the defender baseline into the ratio, and/or a wider band) touches the CR-5 inferred-attack gate threshold → needs re-tuning + a combat sweep, not a silent change. | Combat legibility pass / next combat sweep (escalate the threshold) |
| VP-D3 | P3 | **Committed defensive reinforcers valued by offensive potential** | `_committed_reinforcement_strength` uniformly uses `get_attack_modifier` (combat_executor.py), incl. for the committed DEFENDER — so a cautious/defensive corps reinforcing a defense is systematically undervalued (folds the defensive-stance ×0.90 + attack personality mods). GR5-symmetric (same fn both sides), so a modeling inconsistency, not an exploit — possibly intended as one generic "combat contribution" metric. **Verify intent first.** | Combat review — confirm intent before any change |
| VP-D4 | trivial | **grip recomputed per enemy in the courting loop** | `attempt_vassal_courting` calls `get_imperial_grip(world, player)` once per enemy-nation call each turn (each re-scans homeland + war scores). `process_vassal_loyalty` already memoizes grip per lord; the courting path doesn't. Bounded by N enemies (not a per-region inner loop) — a GR8 cache-per-turn nit, deliberately NOT micro-optimized (staleness risk on a pure derived read outweighs the negligible gain). | Perf nit — fix only if a scale tripwire flags it |

> Routed from **Sweep 4** (July 15, 2026 — `docs/audits/SWEEP_4_2026_07_15.md`). Vassals cleared 6.0→6.5 (target MET, at the floor); these are the CONFIRMED ceiling items the review named. VP-D1 above is the P0 restated by Sweep 4. **Two fixed same day (July 15):** the "grant X **more** autonomy" parse shrug (`_apply_fuzzy_matching` was matching the direction word "more"→"Murat"; now skips marshal-matching for vassal-family actions, `parser.py`) and **VP-D5 below**.

| ID | Pri | Item | Detail | Owner / gate |
|----|-----|------|--------|--------------|
| VP-D5 | P2 | ✅ **FIXED July 15, 2026 — Autonomy change now surfaces its permanent tribute trade-off** | `change_vassal_autonomy` now shows the tribute DELTA directionally: up = "Tribute rate: 75% → 50% (a permanent income cut)", down = "50% → 75% (you collect more of their income)". The player following the "grant autonomy" recovery hint is told the recurring cost at the decision point. Tests in `test_playtest_fixes_2026_07_14.py::TestAutonomyTributeLegibility`. | ✅ done (copy fix, `vassal.py`) |
| VP-D6 | P2 | ✅ **LANDED July 16, 2026 (Vassal Depth Slice 5)** — Enemy-AI grip-awareness | **P1.6 vassal shore-up rung** in `_pick_admin_action` (between P1.5 dotation and P1.75 commission): triggers when the AI lord's weakest satellite slips under 40 loyalty OR its `get_imperial_grip` spirals (<30); arms in escalating desperation — invest (1 nation-DP + 200g) → **VS-3 land grant** (loyalty <30, via the same lord-neutral `list_grantable_regions`) → autonomy-up (loyalty <25, structured `new_level`). All through the shared executor at player prices (Slice-0 substrate); fees in domain functions; **"subsidize" deliberately dropped** (not an action — same reason the recovery hint stopped naming it). Latent at the 1805 boot; live the moment an AI acquires a vassal. The offensive piece (bribe payer) is VS-6's `attempt_vassal_bribe` in the diplomatic phase. Tests: `test_vpd6_ai_vassal_shore_up.py` (12). | ✅ done (Slice 5) |
| VP-D7 | P3 | **Dual authority-derivation tables risk future divergence** | `get_imperial_grip` (VS-R, graded 75/40/25/15, `authority.py:414`) and `get_authority_proxy` (jealousy, bucketed 75/50/25) are parallel derivations of the same "how strong is the court" idea. Both anchor the shared 30 breakpoint today, so there is **no present divergence** — but two tables of the same concept will drift under future tuning. Reconcile to one graded source, or document the intentional split. Tech-debt, not a defect. | Vassal/jealousy tidy — reconcile before either is retuned |
| VP-D8 | P3 | **AI-authored settlement dependency clauses (VS-5 parity scope-down)** | VS-5 (July 16, 2026) shipped accept-side pricing parity for `vassalage`/`subjugation`/`liberation`/`vassal_transfer` (the AI prices them via the shared scoring seams), but the AI never AUTHORS a dependency clause: `ai_diplomacy.py` offers are peace+gold only and there are no AI↔AI common-peace settlements. An AI demanding the player's vassalage (or claiming the player's satellite at the table) is a NEW fantasy needing its own design gate — victory/defeat framing, player-consent UX, and WPS-B cap policy all open. | Needs its own gate; candidate owner = 8.EVAL war-LLM/diplomacy triage |
| VP-D9 | P3 | **Player-facing defection-bribe verb (VS-6 symmetry)** | VS-6 (July 16, 2026) built `attempt_vassal_bribe` lord-neutral, so the PLAYER bribing an enemy lord's satellite works at the domain layer — but it is structurally latent (no enemy lord holds a satellite at the 1805 boot, and no AI creates one today; VP-D8 or a settlement `vassalage` imposed BY the AI would change that). When enemy satellites become reachable, the player needs a typed/wizard verb ("bribe Saxony away from Prussia"), cost preview copy, and the parser/corpus wiring — a small slice riding the existing helper. | Vassal-depth follow-on once enemy lords hold satellites; pairs with VP-D6/VP-D8 |

---

## Post-Fix Routing Update

The old bug-phase gate is now cleared. Sessions 1-7 in `docs/BUG_FIXES.md` are complete, and the diplomacy contract is now stable enough to plan legitimacy and strategy work on top of it.

### Live foundations now documented

- `PL-27`, `PL-34`, and `PL-32` are complete.
- The Envoys inbox / mailbox panel is live, including `GET /mailbox`, `POST /mailbox/activate`, stable mailbox identity, and `dialogue_manager.get_mailbox_count()` as the badge source.
- `world.diplomatic_queue` is gone; the shipped follow-up refactor replaced the old cross-turn mailbox persistence with current-turn envoy items (`Not Now`, same-turn reopen, end-turn lapse).
- Proposal / clause display ownership is centralized in backend formatters, so popup payloads and reopen flows use the same labels.
- Session 6 contract refactors are complete: `/command` starts from `build_base_response()`, remaining diplomacy popups use typed response paths, and `main.gd` routes modals through the registry/dispatcher layer.

### Historical spec queue (April 16, 2026 rescope; superseded by April 28 status)

This queue records the April 16 diplomacy rescope. It is no longer the live implementation queue. Current status is tracked in `docs/STATUS.md`; items 1-4 below are ALL LANDED — BPH, WPS, and WB landed, and Ally Participation + Common Peace LANDED as the Imperial Settlement system, complete through Slice G1 (July 2, 2026, commit `1a9da53`).

1. `Memory and Pressure` (renamed from `Reliability + Commitments` April 16)
   **✅ COMPLETE — Memory and Pressure v2.4.3, all slices landed (see `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`). The remaining-work list and the "~68-74 tests, ~3 sessions remaining" estimate below are historical v2.2-era text.**
   Substrate (betrayal memory, concern witness scope, hard-reject posture, episode_id, structured warnings) is **shipped**. Remaining work this phase: seed `nation_concerns` (4 authored pairs), wire `direct_concern_mod` + `concern_conflict_mod` + graduated `bilateral_betrayal_mod` into acceptance, wire third-party anger on ratification, redemption tick (`actor_honored_turns` +3 / 5 honored turns at OPEN_BORDERS+), rename `alliance_paradox` → `commitment_paradox`, ship C3-lite presentation pass (spotlight tier, split-voice render, named-diplomat resolution per Voice Bible). See `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.2, `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` v0.4 (C3-lite). ~68-74 tests, ~3 sessions remaining (Slice C split into Godot-surfaces + tests/mock-prose sessions; v2.2 renames rivalry→concern for balance-of-power scale architecture + adds auto-downgrade rule + France-Austria concern pair + Make Amends verb).
   **Scale note (v2.2):** `nation_concerns` is named for the target dynamic balance-of-power architecture (see spec §7.7). v0.1 ships static seeded values; dynamic concern evaluation is `Nation Agendas` scope (queue item 5).
2. `Bilateral Peace Hardening`
   **✅ LANDED — shipped per `docs/BILATERAL_PEACE_HARDENING_SPEC.md`.**
   Tighten separate peace / bilateral peace preview, explicit term ownership, promise-breach warnings, and peace-treaty legibility before any ally-aware settlement system exists. **Needs dedicated spec.**
3. `War Purpose + Score Semantics`
   **✅ LANDED — shipped per `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`; `war_objectives`, forced alliance, and liberation are live in code.**
   Collapse war objectives, ticking war score, vassalage power cap, forced alliance, and liberation into one war-goal / score-legibility spec. **Needs dedicated spec.**
3.5. `War Bargains` — `docs/WAR_BARGAIN_SPEC.md`
   **✅ LANDED April 2026 — the `war_bargain` mechanic shipped per the spec.**
   The named-enemy bilateral promise mechanic split out of `Reliability + Commitments` v1.0 in the April 16 rescope. Adds `war_bargain` clause type, lifecycle (active / triggered / fulfilled / void / breached), `join_opportunity` ally-entry contract, counter-bargains, `war_entry_score`, Bargain Review surface, and the WB-D presentation extension (bargain spotlights, scope-branched copy, response routes). **Depends on items 1-3.** Implementable as a single Peace Deals phase precursor before item 4. ~80-90 tests.
4. `Ally Participation + Common Peace`
   **✅ LANDED — shipped as the Imperial Settlement system, complete through Slice G1 (July 2, 2026, commit `1a9da53`); see `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 and `docs/STATUS.md`.**
   Build contribution, consultation, ally beneficiaries, and common peace as a separate wartime-flow system. **Current state:** the dedicated spec and implementation plan now own the active Slice A handoff; this item is no longer merely a later-direction draft.
5. `Nation Agendas + Motive Legibility`
   **✅ DESIGN GATE HELD July 17, 2026 — the agenda core is SPECCED and owned: `docs/NATION_AGENDAS_SPEC.md` (§0 gate record; authored decks + dynamic activation, full coupling in pass 1, R162 owned as slice NA-5). R123/R124/A3/R155-residual/R156 all consume through that spec's §5 seams; this queue item is CLOSED as a routing row.**
   **✅ RE-SCOPED + PROMOTED at 8.EVAL (July 16, 2026 — record `docs/audits/EVAL_8_2026_07_16.md` §1).** The motive-LEGIBILITY half is LANDED piecemeal (W6-9 war room + assess chip, W6-10 register bank + ask variety, UI-6 surfaces, DEF-1 voices; verified with file:line evidence in the gate record) and the `nation_concerns`-to-dynamic sub-item is OBSOLETE (zero code presence — superseded by the live hegemony/bloc-share machinery). **What survives is the AGENDA core — `R123` (econ-strategy triggers), `R124` (isolation/alliance-splitting plays), `A3` (enemy-AI war-vs-diplomacy choice), the `R155` residual (personality-driven timing/persistence/target choice), `R156` (diplomacy strategically optional) — and it is PROMOTED to the Phase 8.5 design-gate centerpiece** (8.5 = Events, Goals & National Identity; the agenda system IS the "Goals & National Identity" diplomacy pillar). Needs its user design gate at 8.5; propose-then-build.
6. `Talleyrand Desk + Explanation Layer`
   **✅ CLOSED at 8.EVAL (July 16, 2026 — DROPPED as landed; record `EVAL_8_2026_07_16.md` §1).** ~6 of the 7 collapsed items shipped piecemeal: R131 cooldown pre-check (`diplomatic_executor.py:270-286`), R132 vassal transparency (W6-3/W6-9 + the UI-6 ledger trend), R17d DP breakdown, R17e trend arrows, R17f mission projection (all in `diplomatic_ledger.py`), R157 voice depth (PL-25 + C3-lite + W6-10 + DEF-1). The sole live residual **R159 (screens should teach mechanics) is RE-HOMED to the Pre-EA Onboarding & Teaching Pass row (§8.EVAL Dispositions below)** — GR9 satisfied, no unowned promise survives.
7. `Economic Diplomacy`
   **RE-POINTED — owner: `docs/ECONOMY_REVISIT_SPEC.md` EC-8 (economic diplomacy, incl. R161). Original text kept as historical context.**
   Collapse `R161` plus diplomacy-facing B4 candidates into one reciprocal-trade / subsidy / pressure spec.

**Diplo-wide ledger rows `DWL-DIP-E7` + `DWL-DIP-METTERNICH`:** ~~their "settlement final gate closes" trigger goes LIVE when the user confirms the Gate 4 visual half~~ **✅ BOTH DECIDED at 8.EVAL July 16, 2026 and ✅ BOTH BUILT + LANDED July 16, 2026 (Batch Q Chunk 2 — see STATUS top entry): E7 = authority-banded defiance floor** — `diplomatic_defiance._defiance_floor_for_authority`: 5% at authority ≥70 (single source `STRONG_EMPEROR_DEFIANCE_FLOOR`), easing to the ordinary 2% below; the whole sabotage arc is reachable again; `DIPLOMACY_SPEC.md §3a` trust-term drift removed in the same slice (`test_session6_diplomacy.py` re-anchored). **Metternich = BUILT small** — `coalition.record_schemer_peace_rejection` at the reject seam plants a once-per-rejection, 5-turn-expiring war-pressure marker (`+2`/marker, cap `+4`) summed in `process_coalition_turn`; anti-stacking (dict keyed by nation); new serialized `WorldState.schemer_rejection_pressure`; `DIPLOMACY_SPEC.md §5c` updated to the landed mechanic; `test_batch_q_metternich_dd8.py` (12). BOTH ROWS CLOSED.

### 8.EVAL Dispositions (July 16, 2026) — the pre-EA rows this gate created

> Gate record = `docs/audits/EVAL_8_2026_07_16.md` (authoritative; §4 = this list's charter). Each row is a GR9 home: owner = the named pass, landing = that pass's build session, completion = the referenced item's own definition.

| Row | Contents | Completion definition |
|-----|----------|----------------------|
| **Pre-EA Balance Pass** | DW-2 war-score-credit calibration (bilateral ×0.3 vs settlement ×0.65 — one constant + dependent-pin retune); co-homed with the STATUS:537 Europe-balance items | Bilateral acceptance credits war dominance consistently with the settlement scorer's felt weight; G4F-9 ladder re-verified |
| **Pre-EA AI Correctness Pass** | AUD-f `_evaluate_marshal` deferred-commit refactor (threat-responder claims + serialized `ai_refortify_cooldown` writes during candidate evaluation) | Evaluation is side-effect-free; M1–M7 harness + `test_ai_audit_2026_07.py` green |
| **Pre-EA AI Depth Pass** | MC-V-4 cautious force-husbanding (design gate FIRST — must coexist with the anti-stagnation machinery); the ROADMAP 8c trio (AI-AI wars, AI vassalization, cross-AI threat) stays at its own 8c row | Gate-blessed design lands with liveness metrics held; **if no pass materializes pre-EA, drop cleanly — no player promise outstanding** |
| **Pre-EA Dialogue Robustness** | S5-4 queue-cap overflow-to-mailbox (push + preempt together) | No dialogue silently dropped at cap; docstring already fixed in Batch Q |
| **Pre-EA Onboarding & Teaching Pass** | R159 (screens teach mechanics) — companion to `TUTORIAL_SCRIPT.md`; **+ "The Congress" candidate (Aug 14 health-check gate, HC-5 deferral): a second authored lesson — a diplomacy/settlement miniature — considered at this pass's gate** | Each core screen names the mechanic it displays; new-player path verified; The Congress built or explicitly dropped at the gate |
| **Pre-EA Diplomacy Polish Pass** | AUD-d M3 territory-sweetener rebuild (reuse VS-3 worth-scaling + the BPH `territory_cede` seam; delete the 2 dead `NATION_DESIRES` territory rows either way) | AI counters can cede real regions with correct direction; ratification live-verified |
| **Pre-EA Diplomacy & Flavor Content Menu** | R22 marriage alliances · R25 vassal personality events · R27 secret treaties · R35 player counter-offers on bilateral incoming offers · R118 acceptance preview · R127 nation-specific advisory intel · R133 point-of-no-return popup · Gneisenau Staff Work | Per-item R-row definitions; user picks the menu at the pass's gate |
| **Next refactoring slice** | S5-D3 hygiene batch (edit-distance triplication, VS-4 predicate single-sourcing = priority, lazy-import documentation, AUD-a's dead `QUEUE_MAX_SIZE`) | Byte-identical behavior, existing VS-4/muster pins green |

**DROPPED at 8.EVAL (explicit strikes, reasons in the gate record §1–§2):** DR-6/queue-item-6 as chartered (landed) · AUD-a envoy flood (fixed twice over, measured 4→7) · AUD-e behavior half (shipped sort canonized; Enemy AI 8.0 held — docs reconciled instead) · arch-plan #23 fixed nation order (canonized; harness-load-bearing) · R32 peace conferences · numeric `power_score` · R24 signing ceremonies · R33 puppet rulers · R36 personal summits · the battle/war narration toggle (narration measured 8.0).

### Still lower priority

- `R162: AI Ultimatums to Player` is no longer blocked by the old attention contract, but it should still wait until the commitment and agenda specs above are written. It adds interruption surface before the core diplomacy has enough political weight. **(July 2, 2026: R162 stays gated behind queue items 5-6, which are owned by the 8.EVAL evaluation gate.)**
- Presentation-only diplomacy polish remains downstream of the grouped spec work above, except for the narrow post-commitments presentation pass proposed in `docs/COMMITMENTS_PRESENTATION_SPEC.md`.

---

## Secondary Post-Fix Items

These refine existing systems and are still implementation-ready later, but they should not displace the grouped spec tracks above.

### R119: Nations Remember Betrayal — **COVERED**
- **Category:** Player Feedback
- **Status:** **Fully covered** by the Memory and Pressure substrate (shipped April 15-16, 2026). `world.betrayal_history` with severity-scaled decay, per-episode strike caps, bilateral `bilateral_betrayal_mod` in acceptance formula, hard-reject posture at 3 active strikes, witness scoping, Make Amends active-redemption verb (v2.1). The original R119 design (flat -10/-20/-30 with half-witness, 20-turn redemption) was superseded by the spec's graded model. No further work needed on R119 itself.
- **Files:** `diplomacy.py`

### ~~R131: Cooldown Pre-Check Warning~~ ✅ LANDED
- **Status:** **LANDED** (`diplomatic_executor.py` cooldown pre-check — recorded shipped at 8.EVAL queue-item-6 below; this row was left open by drift, reconciled Aug 2026 health-check audit).
- **Category:** Player Feedback
- **Summary:** Warn player of proposal cooldowns before opening negotiation dialogue.
- **Details:** Pre-check cooldown before dialogue opens. Show remaining turns + Talleyrand message.
- **Files:** `diplomatic_executor.py`

### R129: Override Feedback in Dispatch
- **Category:** Player Feedback
- **Owner (July 2, 2026):** 8.EVAL triage.
- **Summary:** Add feedback when diplomatic override actions succeed/fail.
- **Details:** Success: +2 trust + dispatch note. Failure: +1 concern boost + dispatch note. Fix timing bug at diplomatic_defiance.py:741.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R128: Sabotage Consequence Feedback
- **Category:** Player Feedback
- **Owner (July 2, 2026):** 8.EVAL triage.
- **Summary:** Track and report sabotage outcomes with Talleyrand feedback.
- **Details:** Track in `world.sabotage_history`. Dispatch note next turn. Trust +3 if Talleyrand was correct.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R132: Vassal Loyalty Transparency — **80/20 LANDED July 10, 2026 (W6-3 `reason` field + W6-9 war-room trend/cause block)**
- **Category:** Player Feedback
- **Summary:** Real-time vassal loyalty deltas and trend tracking.
- **Details:** Lower warning threshold to 30. Show delta when |change| >= 2. Store `prev_loyalty`. Trend arrow in ledger. **Landed shape:** `vassal_loyalty` events carry the dominant-cause `reason` at emission (W6-3 §5.4); the W6-9 assessment renders loyalty + drift trend + the most recent cause per vassal. The residual (ledger trend arrow, threshold tune) stays queue-item-6 (8.EVAL).
- **Files:** `dispatch.py`, `vassal.py`, `diplomatic_ledger.py`, `diplomatic_advisory.py`

### ~~R17d: DP Breakdown Display~~ ✅ LANDED
- **Status:** **LANDED** in `diplomatic_ledger.py` (recorded shipped at 8.EVAL queue-item-6 below; row reconciled Aug 2026 health-check audit).
- **Category:** QoL
- **Summary:** Show DP source/cost components in ledger.

### ~~R17e: Relation Trend Arrows~~ ✅ LANDED
- **Status:** **LANDED** in `diplomatic_ledger.py` (same 8.EVAL record; reconciled Aug 2026).
- **Category:** QoL
- **Summary:** 3-turn history showing direction of relationships in ledger.

### ~~R17f: Mission Progress Projection~~ ✅ LANDED
- **Status:** **LANDED** in `diplomatic_ledger.py` (same 8.EVAL record; reconciled Aug 2026).
- **Category:** QoL
- **Summary:** Estimated completion turn for active missions.

### Memory and Pressure interaction notes (updated for v2.4.3)

These are not new items — they annotate existing items whose scope or interaction changes now that Memory and Pressure v2.4.3 is the active spec.

- **R162 (AI Ultimatums to Player):** Hard-reject posture (3+ bilateral strikes) still informs ultimatum behavior, but the surrounding political pressure is now hegemony-driven rather than rivalry-seeded. A nation at hard-reject posture toward France is both more likely to issue ultimatums (anger-driven) and less likely to accept French counter-offers. Wire this interaction when R162 ships.
- **R123 / R124 (Economic Strategy & Diplomatic Isolation AI):** These collapse into queue item 5 (Nation Agendas + Motive Legibility). AI should now read `hegemony_target_mod`, `bilateral_betrayal_mod`, and (when DG-4 lands) `grievance_modifier` plus bloc geometry to drive subsidy offers, alliance-breaking proposals, and isolation strategy. Static `nation_rivalries` / `rival_conflict_mod` are no longer the data source.
- **R17d (DP Breakdown Display):** Show the live Memory and Pressure acceptance components individually rather than reviving the old composite term: `hegemony_target_mod`, `bilateral_betrayal_mod`, `reliability_modifier`, and later `grievance_modifier` / `composite_floor` when DG-4 is active.
- **R155 / R157 (AI Proposal Voice / Talleyrand Voice Depth):** The C3-lite presentation pass (`COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1) now commits named-diplomat CRITICAL / NORMAL notices, the paradox popup, Balance-of-Europe threshold beats, and Make Amends acknowledgments per `DIPLOMAT_VOICE_BIBLE.md`. The broader scope (personality-driven proposal timing, AI-initiated proposal voice, deep Talleyrand commentary across all diplomacy) remains open and routes to queue items 5-6.

---

## Focused Audit Validation (Apr 10, 2026)

The focused attention / AI diplomacy audit tightened which diplomacy legitimacy items are already justified, which ones need bug-fix prerequisites, and which old notes are now stale.

### Already justified by current evidence

- **R160: Nation Rivalry System** — confirmed as the highest-leverage legitimacy upgrade. Current diplomacy still lets France drift toward broad friendship without enough forced political choice. *(Since SUPERSEDED by Memory and Pressure v2.4.3 — see the R160 row below.)*
- **R155: AI Proposal Personality Voice** — needs to expand from flavor text into motive legibility. The audit confirmed that AI personality currently changes a few constants, but not enough of proposal timing, persistence, target choice, or player-facing explanation.
- **R156: Diplomacy Strategic Optionality** — confirmed. Proposals happen, but they do not create enough meaningful branching until rivalry / exclusion pressure exists.

### Prerequisites now satisfied (Apr 12)

- **R160 / R155 / R156** are no longer blocked by the old diplomacy contract prerequisites. `PL-27`, `PL-34`, and `PL-32` are closed, and the Envoys inbox / current-turn offer lifetime / typed popup-response foundations are live.
- **R162: AI Ultimatums to Player** no longer waits on the mailbox/recovery transport fix, but it remains intentionally sequenced after the stronger commitment and agenda specs.
- Presentation-only diplomacy polish should still follow the grouped spec work above, not precede it.

### Current legitimacy stack

- Completed foundation: Envoys inbox / same-turn offer lifetime / backend-owned display labels / typed response routing.
- `Reliability + Commitments`: make alliances politically costly, promises meaningful, and betrayal cumulative.
- `Bilateral Peace Hardening`: make separate peace and bilateral settlement review legible before multilateral settlement exists.
- `War Purpose + Score Semantics`: make wars resolve toward recognizable political outcomes instead of generic pressure alone.
- `Ally Participation + Common Peace`: active wartime settlement layer; implementation starts from `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice A.
- `Nation Agendas + Motive Legibility`: make AI motives and strategic branching legible to the player.

---

## Needs Design Gate

### R160: Nation Rivalry System (EU4-Inspired) — **SUPERSEDED BY Memory and Pressure v2.4.3**
- **Category:** Diplomacy — Balance
- **Status:** Static rivalry seed and the old rivalry-specific acceptance terms were dropped in the v2.4 hegemony refactor. The live political-pressure layer is now `hegemony_target_mod` + `bilateral_betrayal_mod`, with `grievance_modifier` joining later via DG-4. The original R160 design is therefore superseded by `RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3 rather than partially awaiting completion.
- **Remaining (unshipped):** any future dynamic rivalry / agenda system must grow out of bloc geometry, betrayal memory, grievance persistence, and AI agendas rather than restoring `nation_rivalries` / `direct_rivalry_mod` / `rival_conflict_mod`. That work still belongs to queue item 5 (`Nation Agendas + Motive Legibility`).
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_ledger.py`, `world_state.py`

### R151: Territorial Promise Clauses — **LANDED via WAR_BARGAIN_SPEC (April 2026)**
- **Category:** Diplomacy Feature
- **Disposition (July 2, 2026):** ✅ LANDED — the `war_bargain` mechanic shipped April 2026; the "scheduled in the Peace Deals phase" text below is historical.
- **Status:** The broader concept (France makes named-enemy promises to allies, tracking obligation, breach/fulfillment, betrayal consequences) is now fully designed as the `war_bargain` clause type in `docs/WAR_BARGAIN_SPEC.md`. The spec covers creation, validation, lifecycle, fulfillment, breach/void, war-entry integration, and the Bargain Review surface. Scheduled in the Peace Deals phase after `Bilateral Peace Hardening` + `War Purpose + Score Semantics` (queue items 2-3.5).
- **Files:** `diplomacy.py`, `ai_diplomacy.py`, `diplomatic_executor.py`

### Jealousy System (v3.1 spec)
- **Category:** Marshal Feature
- **Summary:** Glory Ladder targeting, personality expressions, escalation, confrontation popups.
- **Details:** Full spec at `docs/JEALOUSY_SPEC.md`. Core design settled. Top of ladder: +1 all core stats while #1. Defeats cost glory. DO NOT CODE WITHOUT USER APPROVAL.
- **Sequencing note July 2, 2026:** the Marshal Content Pass (`docs/MARSHAL_CONTENT_PASS_SPEC.md`, MC-3 relationship authoring) is effectively a prerequisite — the shipped 21-marshal roster has zero authored relationships; a v3.2 addendum must re-derive scenario impact/tuning against that roster before the gate.

---

## War System Overhaul (EU4-Inspired — Design Gate) — **✅ LANDED**

**Disposition (July 2, 2026):** this entire section LANDED via the War Purpose + Score Semantics work (`docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`) — `world.war_objectives` ticking score, the vassalage power cap, the `forced_alliance` clause type, and the liberation mechanic are all live in code. The text below is preserved as historical design intent.

Full design spec in `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` lines 215-722. Addresses core balance problem: defensive play is overwhelmingly superior because no ticking score incentivizes holding territory over time.

### War Objectives + Ticking War Score (5th Component)
- **Summary:** Player-chosen war goals at war declaration (Conquest, Subjugation, Forced Alliance) and auto-assigned goals (Defense, Liberation). Each goal has a ticking target region — holding it accumulates war score over time (±25 cap).
- **Ticking rates:** Conquest +2/turn (enemy capital), Subjugation +3/turn (enemy capital, power cap gated), Forced Alliance +2/turn (enemy capital), Defense +1/turn (any enemy region), Liberation +1/turn per vassal capital.
- **New field:** `world.war_objectives: Dict[str, Dict]` — diplo_key to `{type, target, accumulated}`
- **Files:** `diplomacy.py` (calculate_war_score 5th component), `world_state.py` (field + per-turn accumulation), `war_status.py` + `war_detail_popup.gd` (display), `diplomatic_executor.py` (war goal selection dialogue)
- **Est. sessions:** 2-3, ~20 tests

### Vassalage Power Cap
- **Summary:** Gate vassalization on National Power ratio: target must be ≤ 50% of player's power. Power = sum of base income of controlled regions + partial vassal contribution.
- **Why:** Prevents France from vassalizing Austria at war_score 80 — only small nations should be vassalizable.
- **Files:** `vassal.py`, `diplomacy.py`, `diplomatic_ledger.py`, `diplomatic_templates.py`
- **Est. sessions:** 1, ~10 tests

### Forced Alliance Clause Type
- **Summary:** New clause type — war goal forces enemy into ALLIANCE + Continental System on peace. Follows vassalage pattern for wiring (acceptance values, harshness, keywords, display names, state mapping).
- **Historical:** Napoleon's primary war objective (Austerlitz, Tilsit, Jena).
- **Files:** `diplomacy.py`, `diplomatic_dialogue.py`, `diplomatic_executor.py` (4 state maps), `display_names.py`, `diplomatic_templates.py`, `world_state.py`
- **Est. sessions:** 1-2, ~10 tests

### Liberation Mechanic
- **Summary:** Coalition war goal — liberating vassals. On peace: `release_vassal()` + auto `DEFENSIVE_ALLIANCE` with liberator.
- **Files:** `world_state.py` (_ratify_treaty), `vassal.py` (release reason)
- **Est. sessions:** 1, ~6 tests

---

## AI Diplomacy Improvements (Ready — Small Fixes)

### N1: AI Preemptive Alliance Against Rising Threat
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 69-130
- **Summary:** Trigger 5 in AI-AI diplomatic evaluation. When threat > 40, nations with negative relations toward France form defensive alliances with each other. Creates diplomatic web before coalitions.
- **Audit status (Apr 10):** Already implemented in `ai_diplomacy.py` Trigger 5. Keep as verified reference, not as a pending refinement unless the behavior needs expansion.
- **Files:** `ai_diplomacy.py`
- **Est. tests:** ~7

### A3: AI War Exhaustion Integration
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 55-61
- **Disposition (July 2, 2026):** the proposal-side integration is LANDED in `ai_diplomacy.py`; the residual (the `enemy_ai.py` war-vs-diplomacy choice) rides queue item 5 (`Nation Agendas + Motive Legibility`), per the Memory and Pressure interaction note above.
- **Summary:** Proposal-side war exhaustion integration is already partially landed in `ai_diplomacy.py` (`effective_p1_threshold`, `effective_stalemate_turns`). Remaining work, if any, is broader war-exhaustion integration in `enemy_ai.py` and diplomacy-vs-war choice, so this item now needs re-scope rather than blind implementation.
- **Files:** `ai_diplomacy.py`, `enemy_ai.py`
- **Est. tests:** ~4

### A4: AI Harsh Peace Gold Formula Rebalance
- **Source:** `docs/archive/DIPLOMACY_DESIGN_FIXES.md` lines 47-53
- **Summary:** Historical note only: the focused audit confirmed the live formula already uses `max(200, int(war_score * 5 * gold_mult))` in `ai_diplomacy.py`. Keep this item only if further rebalance is desired.
- **Files:** `ai_diplomacy.py`
- **Est. tests:** ~2

---

## Wave 4 — Decide Gate (Per-Item Approval)

These are new feature designs. Each needs individual approval before implementation.

**July 2, 2026:** per-item user approval is still required. Items already re-pointed above have new owners: R26 → `docs/ECONOMY_REVISIT_SPEC.md` EC-5 (Continental System); R161 → `ECONOMY_REVISIT_SPEC.md` EC-8; R162 → gated behind queue items 5-6 (8.EVAL).

| ID | Item | Summary |
|----|------|---------|
| R22 | Marriage Alliances | Dynastic bonds: +20 rel, block war 5 turns, 3 DP |
| R32 | Peace Conferences | Multi-nation negotiations, 3 DP, +15 acceptance |
| R117 | Advisory Actionability — **✅ LANDED July 10, 2026 via W6-9** (the war-room assessment's ONE recommendation ends in an executable option: `execute_suggestion` / `expand_options`) | Advisory ends with executable options |
| R123 | Economic Strategy AI (P9) | Gold > 600 triggers subsidy offers, trade pressure |
| R124 | Diplomatic Isolation AI (P10) | Split enemy alliances with generous terms |
| R133 | Point of No Return Event | One-time Talleyrand popup at threat 40 |
| R28 | Talleyrand Voice Bank | 5-8 variants per situation type |
| R127 | Nation-Specific Intelligence | Per-nation personality lines in advisory |
| R24 | Treaty Signing Ceremonies | Talleyrand ceremony text on ratification |
| R25 | Vassal Personality Events | 3-4 random loyalty-gated events per game |
| R26 | Continental System Buff | Backend exists, needs player command + creative rebalance |
| R27 | Secret Treaties | Hidden treaties, 10%/turn discovery chance |
| R33 | Puppet Rulers | Named rulers with personality, events |
| R35 | Player Counter-Offer Terms | Player specifies clauses (Godot popup) |
| R36 | Personal Summits | Face-to-face meetings, +15 acceptance 3 turns |
| R59 | ~~Literal Personality Triggers~~ | **SUPERSEDED by W6-5 The Literal Doctrine (user call, July 10, 2026):** literal marshals never object BY DESIGN — the fantasy is "generals who do what they're ordered." Engagement = order echo + fidelity beat + precision captions + muster-preview warnings (`WAVE6_FUN_FACTOR_SPEC.md` §7; triggers converted to a doctrine comment in `personality.py`, pinned by `test_w6_literal_doctrine.py`). |
| R118 | Enhanced Acceptance Preview | Top 3 positive/negative components + Talleyrand hints |
| R161 | One-Time Trade | Trade gold, manpower, territory directly without ultimatum or state change |
| R162 | AI Ultimatums to Player | Building Blocks: AI uses same ultimatum system as player. Needs popup, response flow, AI decision tree |

---

### R161: One-Time Trade (Expanded)
- **Category:** Diplomacy Feature
- **Owner (July 2, 2026):** re-pointed to `docs/ECONOMY_REVISIT_SPEC.md` EC-8 (economic diplomacy, alongside queue item 7). Original design text kept as historical context.
- **Summary:** Voluntary, consensual resource exchange between nations — no state change, no coercion. The "carrot" complement to ultimatums (the "stick").
- **Details:** Player proposes a trade (gold, manpower, territory) to any nation at OPEN_BORDERS or better. Both sides give and receive. Uses existing conversational diplomacy flow with `generate_trade_terms()`. Acceptance via full formula. No threat increase, no relation penalty — pure commerce.
- **Building Blocks principle:** Reuses `_ratify_treaty` clause processing, `calculate_acceptance()`, dialogue enrichment, splash damage (none for trades). Same executor path as proposals but with `type: "trade"` and no state transition.
- **Distinction from ultimatums:** Trades are voluntary (both sides benefit), ultimatums are coercive (one-sided demands with diplomatic cost).
- **Gates needed:** Trade balance formula (what's fair?), AI trade evaluation, frequency limits.
- **Files:** `diplomatic_executor.py`, `diplomatic_templates.py`, `diplomacy.py` (new base disposition for trade), `diplomatic_dialogue.py`
- **Est. sessions:** 1-2, ~8 tests

### R162: AI Ultimatums to Player
- **Category:** AI Diplomacy — Building Blocks
- **Status (July 17, 2026):** ✅ **OWNED — slice NA-5 of `docs/NATION_AGENDAS_SPEC.md` (§8 answers the gate questions: trigger rung, agenda-target terms, rejection → bounded expiring coalition-pressure marker not a free war, mailbox transport + dtype whitelist).** Built after NA-0..NA-3 land and are verified live; no further gate. The details below are historical context.
- **Status (July 2, 2026):** stays gated behind queue items 5-6 (Nation Agendas + Talleyrand Desk), which are owned by the 8.EVAL evaluation gate.
- **Summary:** AI nations issue ultimatums to the player using the same ultimatum system the player uses. Building Blocks principle (§23): same systems, different input values.
- **Details:** AI evaluates ultimatum opportunity in `enemy_ai.py` decision tree (new P-trigger). Conditions: military superiority over player in a region, low relations, not in coalition with player. Generates terms via `generate_ultimatum_terms()` (same function player uses). Delivered as popup with [Accept][Reject] options. Rejection gives AI casus belli. Same splash damage, threat (reduces player threat if AI is aggressor), and cooldown mechanics.
- **Building Blocks reuse:** `generate_ultimatum_terms()`, `calculate_acceptance()` (inverted — player is target), `_ratify_treaty` clause processing, splash damage formula, global cooldown (separate AI cooldown counter).
- **Gates needed:** AI trigger conditions (when is ultimatum better than war declaration?), player response popup design, threat direction (does AI ultimatum reduce or increase player threat?).
- **Files:** `enemy_ai.py` (new P-trigger), `diplomatic_executor.py` (AI ultimatum handler), `main.gd` (new popup), `ai_diplomacy.py`
- **Est. sessions:** 2-3, ~12 tests

### National Power Tiers (Great Power / Secondary / Minor) — Design Gate
- **SUPERSEDED — April 17, 2026.** Canonical `power_tier` is now defined in `docs/SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy". Under the canonical definition, `power_tier` is **authored scenario data** with values `major / secondary / minor` and is **never recomputed at runtime**. The dynamic numeric-tier model below is superseded and must not be implemented. If a numeric strength-derived signal is needed for AI threat weighting, coalition calculations, or dispatch priority, it lives in a separate `power_score` field that does not overwrite `power_tier`. The original text is preserved below as historical design intent.
- **Residual disposition (July 2, 2026):** the tier model stays SUPERSEDED — Phase 0's authored `power_tier` shipped with the real-map cutover. The optional numeric `power_score` idea: evaluate at the 8.EVAL gate, else drop.
- **Category:** Diplomacy + War — Balance + Immersion
- **Summary:** Dynamic numeric power tiers (`great_power / secondary_power / minor_power`) calculated from controlled regions, income, military strength, and partial vassal contribution. Affects acceptance formula (great powers resist vassalization), coalition formation (great powers lead coalitions, minor powers join), war settlement (consultation rights scale with tier), and AI threat assessment (great powers escalate coalition faster).
- **Origin:** Conceptual three-tier model exists in `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §8.3. Data fields (`nation_power_scores`, `nation_power_tiers`) listed as deferred in `RELIABILITY_COMMITMENTS_SPEC.md` §12.3.
- **Design decision from WAR_SETTLEMENT spec (superseded):** "These tiers come from numbers, not authored nation labels. The map can create a new quadrangle if power shifts." — This position is reversed by the Phase 0 canonicalization: tiers are now authored, not numeric. A separate `power_score` may still be derived from numbers for non-tier uses.
- **Interaction with Memory and Pressure:** great powers could have different rivalry intensity defaults (primary only between great powers; secondary between great-and-minor), betrayal tolerance thresholds (great powers hold grudges longer), and Make Amends cost scaling (reparations to a great power should cost more than to a minor).
- **Gates needed:** numeric formula for calculating power scores, threshold ranges (what income/strength makes a "great power"), whether tiers are recalculated per turn or per-war, how tiers interact with the acceptance formula's existing modifier caps.
- **Natural home:** alongside `War Purpose + Score Semantics` (queue item 3) since power tiers inform war objectives and settlement legitimacy. Or as a sub-item of the later `Ally Participation + Common Peace` (queue item 4).
- **Files:** `world_state.py` (data), `diplomacy.py` (formula + tiers), `diplomatic_ledger.py` (display), `ai_diplomacy.py` (threat evaluation)
- **Est. sessions:** 1-2 for the data layer + formula, plus formula-integration touches across existing systems

---

## Gold Sink Options (B4 Balance — Design Gate)

**Priority:** MEDIUM | **Phase:** Pre-EA refinement

**RE-POINTED (July 2, 2026):** owner is `docs/ECONOMY_REVISIT_SPEC.md` EC-2 (the B4 gold-sinks gate). The candidates below are re-cost candidates for the ~3.4k/turn 1805 economy — France income is ~3.4k/turn on 28 provinces, upkeep ~950g, and the whole building stock costs ~1.85k — so this section's "~700g vs ~250g" numbers are legacy (19-region map). Original text kept as historical context.

Gold accumulation is a known design gap (~700g/turn income vs ~250g upkeep). Manpower-gated recruitment means gold piles up with no meaningful spending options. This section tracks candidate gold sinks for evaluation.

**Forced march REJECTED** — trivializes cavalry's 2-region movement advantage, which is cavalry's core identity.

### Leading Candidate: Province Development
- **Cost:** Variable (200-500g per investment)
- **Effect:** Invest gold in controlled region to boost supply cap, income, or repair war damage faster
- **Design appeal:** Creates invest-now-vs-save tension, rewards holding territory, ties gold to strategic positioning
- **Needs:** Investment tiers, per-region cooldown, diminishing returns formula, AI investment priority

### Other Candidates (evaluate after Province Development)

| Option | Cost | Effect | Notes |
|--------|------|--------|-------|
| Diplomatic gifts/bribes | 200g | +5 relation (once/turn/nation) | Gold becomes diplomacy tool |
| Mercenary garrisons | 400g | Defensive garrison without stationing marshal | Frees marshals for offense |
| Recruitment bounties | 300g | Double manpower regen for 1 turn | Accelerates rebuilding |

---

## Enemy AP Rebalancing (Deferred — Post Full Map)

**Priority:** LOW | **Phase:** After full 1805 map implementation

**RE-POINTED (July 2, 2026):** owner is `docs/ECONOMY_REVISIT_SPEC.md` EC-4 (enemy AP). The revisit trigger fired July 2, 2026 — the full 1805 map shipped with the real-map cutover. NOTE: the EC-0 AP-reset defect must land first. Original text kept as historical context.

Enemy AI action budget (currently 4 paid AP per nation) may need rebalancing once the full map is implemented with all nations, regions, and marshal counts at scale. Current 4-nation, 19-region map doesn't stress the action economy the same way a full campaign will. Revisit AP values, per-nation scaling, and aggregate action counts after full map playtesting.

---

## Wave 5 — Game Review Findings (Design Gate)

Cross-system findings from comprehensive review. Needs design gate as a batch.

**July 2, 2026:** per-item user approval is still required. Items already re-pointed above have new owners: R158 → `docs/COMMAND_ROBUSTNESS_SPEC.md` CR-7 (parser confidence feedback).

**Diplomatic Term Novelty — PARTIALLY ABSORBED into PL-25 (BUG_FIXES.md).** PL-25 covers the 80/20: amount jitter, personality-biased pen nudge, nation desire profile bias in `_build_base_terms()`, situational flavor lines. R155/R157 retain the remaining full scope: hawk/dove personality weight table for ALL AI proposals (not just Talleyrand's pen nudge), deep `TALLEYRAND_COMMENTARY` integration, and AI-initiated proposal personality voice.

**Focused audit routing (updated July 2, 2026):** R155 / R156 remain validated by code evidence and route to queue items 5-6 (8.EVAL). R160 is SUPERSEDED by Memory and Pressure v2.4.3 (see its row above) — it is no longer a pending upgrade. The diplomacy mailbox / recovery surface LANDED long since; R162 is not transport-blocked, it stays gated behind queue items 5-6.

| ID | Item | Summary |
|----|------|---------|
| R152 | Authority System UI Visibility | Authority impact not visible enough to players |
| R153 | ~~Literal Personality Triggers~~ | **SUPERSEDED by W6-5 The Literal Doctrine (user call, July 10, 2026)** — see the R59 row; literal never objects by design. |
| R154 | Combat Morale Spiral | Morale death spiral needs circuit breaker |
| R155 | AI Proposal Personality Voice | Partially absorbed into PL-25. Remaining: visible motive / personality in timing, terms, persistence, and player-facing explanation |
| R156 | Diplomacy Strategic Optionality | Diplomacy feels optional vs military path |
| R157 | Talleyrand Voice Depth | Partially absorbed into PL-25 (situational flavor, personality pen nudge). Remaining: deep commentary integration |
| R158 | NL Parser Confidence Feedback | Show parse confidence to player |
| R159 | Information Screen Teaching | Screens don't teach mechanics |

---

## Wave 6 — Creative Capstone (July 10, 2026) — **✅ APPROVED IN FULL; owner = `docs/WAVE6_FUN_FACTOR_SPEC.md`**

> Source: `docs/audits/CREATIVE_AUDIT_2026_07_10.md` (the AUDIT_GUIDELINE §8 fun-factor capstone — live 5-turn 1805 playtest under `LLM_MODE=anthropic` + two code-evidence sweeps). **GATE (July 10, 2026, same day): the user approved EVERY item below in full — plus two additions scoped at the gate: Dynamic Battle Naming (→ spec slice W6-2) and the Literal Doctrine hone (→ W6-5; user steer: literal marshals need not object — the fantasy is "generals who do what they're ordered").** The build-ready plan — slice order, seams, blessed default numbers, tests — is **`docs/WAVE6_FUN_FACTOR_SPEC.md`** (authoritative over the sketches below where they differ). Rows below map: EXP-N1→W6-3 · EXP-M1→W6-7 · EXP-C1→W6-4 · EXP-E1→W6-8 · EXP-M2→W6-6 · EXP-D1→W6-9 · E-CA-1/3→W6-11 · E-CA-2→W6-1 · E-CA-4→W6-4 · E-CA-5/6→W6-10.

### Gate additions (scoped at the July-10 approval; full designs in the spec)

| ID | Item | One-line mechanic | Spec slice |
|----|------|-------------------|------------|
| W6-ADD-1 | **Dynamic Battle Naming** | Serialized per-region battle counts → "Second Battle of Swabia", "The Great Battle of X" at ≥80k engaged; one naming site (`combat_executor` battle_name), consumed everywhere `battle_name` already flows. | W6-2 |
| W6-ADD-2 | **The Literal Doctrine** | Literal = "generals who do exactly what they're ordered": never objects **by design** (supersedes R59/R153's literal-objection TODOs), order echo + completion reports quoting the verbatim order, doctrine tells on card/dispatch/muster, per-turn **fidelity beats** ("Soult holds at Lorraine, per your orders — the guns did not move him"), precision rewards captioned. Builds on the existing Grouchy Rule (`combat_executor._calculate_reinforcements`) and SUPPORT standing orders. | W6-5 |

### Ranked expansions (by depth-per-unit-complexity — full designs in the memo §4; build detail in the spec)

| ID | Item | One-line mechanic | Owner / gate | Est. |
|----|------|-------------------|--------------|------|
| EXP-N1 | **The Dispatch Rewrite — "Berthier tells the story"** | Deterministic narrative-priority layer over existing events: headline selection, per-marshal danger flags, arc memory ("Bernadotte, hunted across three frontiers…"). No LLM, no new mechanics. | Standalone slice; **top-ranked item of the audit** | 1–2 sessions |
| EXP-M1 | **Marshal Fates: capture, parole, last stand** | Forced-retreat fate roll (escape/capture/personality-gated last stand); captured marshals become ransom/exchange clauses in existing settlement machinery; Building Blocks — Mack at Ulm becomes capturable. | Own design gate (thresholds, AI prisoner valuation) | 2–3 sessions |
| EXP-C1 | **March to the Guns, surfaced: muster preview + standing order** | Pre-battle muster block naming WILL JOIN / WILL NOT per marshal *with the personality reason*; cheap `"Soult, support Ney"` standing order; substrate the re-homed **Grouchy Moment** lands on. | Own gate; foundation for the Grouchy Moment gate | 1–2 sessions |
| EXP-E1 | **The Spoils of War: estate confiscation** — **✅ LANDED July 10, 2026 via W6-8** (`WAVE6_FUN_FACTOR_SPEC.md` §10; `test_w6_estate_confiscation.py`) | Conquering an enemy marshal's estate opens confiscate (windfall + grudge + own-cautious-marshal trust cost) vs respect (court acceptance bonus); confiscated estates become grantable (rides ES-7 as landed). Resolves the live "Swabia already sustains Marshal Mack's household" dead end. | ~~EC pass 2 gate (numbers)~~ numbers blessed at the July-10 Wave-6 gate (in-band tunable) | ~1 session |
| EXP-M2 | **Enemy marshals speak** | Deterministic one-liner bank keyed to (enemy personality × outcome × situation) at the battle-report seam; complements DEF-1 (diplomat voices), which does not own enemy marshals. | Content slice; MC-adjacent | <1 session |
| EXP-D1 | **"What does Europe intend?" — strategic assessment verb** — **✅ LANDED July 10, 2026 via W6-9** (`WAVE6_FUN_FACTOR_SPEC.md` §11; `test_w6_assessment_verb.py`) | `assess our situation` (dead-ends live today) returns per-war trajectory, **coalition posture** (computed, never shown), top threat sources, vassal trend + cause, one executable recommendation (absorbs R117's shape). | ~~Recommended first slice of queue item 6 (Talleyrand Desk)~~ landed via W6-9; queue item 6 owns the residual desk items | ~1 session |

### Escalations (gate-owned; no code)

| ID | Finding | Owner |
|----|---------|-------|
| E-CA-1 | Attacker morale-grind asymmetry (defender morale ~static through 15k casualties while attackers/reinforcers bleed to 47) — the live shape of the meat-grinder, post-EC. — **✅ LANDED July 10, 2026 via W6-11** (symmetric casualty-scaled morale in both combat copies, winner delta = bonus − loss; `test_w6_balance_duo.py` incl. the battle-2 replay) | ~~Combat balance gate (user)~~ landed at the blessed W6 numbers (defender curve 1.0, band ≥0.75) |
| E-CA-2 | Retreat agency + direction doctrine (honor stated destination or narrate substitution; homeward bias; never into an at-war nation with alternatives). Mechanical half = BUG-CA-2. | Combat/movement gate |
| E-CA-3 | War-priced recruitment: 10,000 men for 200g keeps gold free mid-war; scale per-soldier gold cost by force-limit ratio + war status. — **✅ LANDED July 10, 2026 via W6-11** (×3 at war composed with ×(1+overage), Europe-scoped, AI same-priced incl. its admin pre-checks; two-sided 1805 solvency pinned; `test_w6_balance_duo.py`) | ~~EC pass 2 (blessed numbers)~~ landed at the blessed W6 numbers (war ×3, band 2–4) |
| E-CA-4 | Explicit bad-odds `attack` gets no warning while vague delegation gets a lethal-odds interrupt — decide whether direct orders deserve a one-line odds note. | CR-6 gate |
| E-CA-5 | Settlement offers must state territorial consequences ("Britain retains Flanders") — "Peace" is illegible while home soil is occupied. — **✅ LANDED July 10, 2026 via W6-10** (`terms_summary` status-quo line; `test_w6_incoming_voice.py`) | ~~Settlement presentation (narrow, post-arc)~~ landed |
| E-CA-6 | Incoming-proposal voice + AI proposal variety (5 identical open-borders/"hegemony pressure" offers in 5 turns; named diplomat never speaks). — **✅ LANDED July 10, 2026 via W6-10** (`diplomat_line` register bank + 6-turn lapse/reject type cooldown + P3 relation-band diversification; `test_w6_incoming_voice.py`). The deeper R155/R156 scope (personality-driven timing/persistence/target choice, strategic optionality) stays with queue items 5–6. | ~~Queue items 5–6 (8.EVAL), with R155/R156~~ voice+variety landed; residual scope stays 8.EVAL |

### Revisions to prior items (live-evidence pass, July 10, 2026)

- **R154 (Combat Morale Spiral) — REVISED:** the claimed missing circuit breaker **exists and works** (`combat.py` FORCED_RETREAT_THRESHOLD=25 floor; +5/+10 victory recovery). The real, live-confirmed issue is the attacker/defender morale **asymmetry** — re-scoped as E-CA-1; do not build a second breaker.
- **R59 / R153 (Literal Personality Triggers) — RESOLVED July 10, 2026: SUPERSEDED by W6-5 The Literal Doctrine (user call at the Wave 6 gate).** Literal marshals never object BY DESIGN; the inert triggers were converted to a doctrine comment and the never-objects behavior is pinned (`test_w6_literal_doctrine.py`). The niche the triggers aimed at is owned by the CR-2/CR-5 clarification arms + the W6-5 fidelity surfaces (order echo, fidelity beat, muster warnings). |
- **R129 / R131 / R132 — LIVE EVIDENCE ADDED:** R132 is the strongest of the three — three vassals bleeding −4/−6/−8 loyalty per turn with no cause attached anywhere was a top-5 confusion of the playtest. Recommend R132 rides EXP-D1/queue-item-6 rather than waiting for a standalone slice.
- **R155 / R156 — CONFIRMED, EVIDENCE UPGRADED:** proposal monotony measured live (5 nations, identical proposal+reason, 5 turns); the *outgoing* surface (terms prep, acceptance estimate, ratification gate, motive commentary) is the register benchmark the incoming surface should be held to. Folded into E-CA-6.
- **R117 (Advisory Actionability) — ABSORBED into EXP-D1** (the strategic-assessment verb ends with an executable option).

---

## Historical Precision (1805 Campaign — Future Refinement)

These items are conscious trade-offs where v0.1 chose recognizability, immersion, or implementation speed over strict period accuracy. Each has an audit trail, not a bug. Track for EA scope when the full 1805 campaign lands. Added April 16, 2026 from the Memory and Pressure creative audit.

### P1: Period-accurate diplomat roster for 1805
- **Summary:** The four foreign diplomats in `backend/models/diplomat.py` (Hardenberg / Metternich / Castlereagh / Einsiedel) are recognizable Napoleonic-era names but historically took their depicted roles **after** the 1805 campaign start: Hardenberg as Prussian chancellor from 1810, Metternich as Austrian foreign minister from 1809, Castlereagh as British foreign secretary from 1812, Einsiedel as Saxon minister from 1813. The actual 1805 ministers were Haugwitz (Prussia), Stadion or Cobenzl (Austria), Mulgrave (Britain), and Bose or Löss (Saxony).
- **Design trade-off (deliberate):** recognizability was prioritized for v0.1 because the four chosen figures are well known to strategy players and the Voice Bible's Hawk / Schemer / Dove register distinctions were drawn from their historical voices. Swapping them in v0.1 would lose the established register voices without adding mechanical value and would force the Voice Bible exemplars to be re-authored before any useful commitments work shipped.
- **When to revisit:** once the full 1805 campaign ships (Early Access) and the game claims period fidelity as a feature. Swap to the 1805-accurate ministers and port the register notes. The Voice Bible's "Characteristic openings" / "Never says" framework should transfer cleanly — Haugwitz was a Prussian Hawk in the Hardenberg mold, Stadion a Schemer adjacent to Metternich, Mulgrave less distinctive than Castlereagh but workable, Bose closer to Einsiedel's dove register.
- **Revisit condition MET July 2, 2026:** the full 1805 campaign shipped (real-map cutover complete). Still EA-scope; interacts with DEF-1 Roster Voices register authoring.
- **Files:** `backend/models/diplomat.py`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `backend/game_logic/diplomatic_templates.py`, any committed breach / hard-reject mock prose
- **Est. sessions:** 1 (cast swap + voice port + test refresh)

### P2: Britain reactive bloc pressure (continental-hegemon pattern)
- **Summary:** The v0.1 rivalry model has Britain as France's direct rival but gives Britain no *reactive* posture when France deepens ties with a continental power. Historically Britain opposed any continental hegemon on principle, paying subsidies to any continental power willing to fight France. Flagged in `RELIABILITY_COMMITMENTS_SPEC.md` v2.1 §7.4.C as the #1 historical-texture debt for Memory and Pressure.
- **When to land:** `Coalition Generalization` (D2, follow-up after Memory and Pressure). D2 should include continental-hegemon reactive threat accumulation — not just bloc-target parameterization — so Britain gains automatic threat against any power approaching continental hegemony, not only France by name.
- **Owner (updated July 2, 2026):** the `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` deferred-ledger D2 row. The previously-named "Coalition Generalization (D2)" is not a landed slice — this item rides that deferred-ledger row.
- **Files:** `backend/game_logic/coalition.py`, `backend/game_logic/diplomacy.py`
- **Est. sessions:** folded into D2 spec work

### P3: Diplomatic Ledger sort / filter at scale
- **Summary:** The Diplomatic Ledger's Nations tab currently renders one row per nation. At 5 nations this is clean; at 6-8 full 1805 nations with multiple rivals each, the list becomes dense. Commitments rows (active rivals, betrayal warnings, posture markers) multiply the cell count.
- **When to land:** Pre-EA polish alongside Map Renderer UX pass, or absorbed into the Talleyrand Desk + Explanation Layer spec (diplomacy queue item 6).
- **Urgency raised (July 2, 2026):** 20 nations render now in the shipped 1805 campaign. Owner: queue item 6 (Talleyrand Desk + Explanation Layer) or pre-EA polish.
- **Files:** `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`
- **Est. sessions:** 1 as a standalone UX slice, or folded into the Talleyrand Desk pass

---

## Estate Second Pass deferrals (July 11, 2026)

Filed at the ES-7 second-pass build (`ECONOMY_REVISIT_SPEC.md` §0.6.8 — the estates+rentes reward portfolio). Historically grounded in the July-11 design conversation (Domaine Extraordinaire rentes/arrears; Fontainebleau April 1814; Murat's January-1814 Austria treaty).

> **✅ ESP-1, ESP-2, and ESP-4 LANDED July 11, 2026** with the Jealousy v3.2 build (`JEALOUSY_SPEC.md` §0.3 rider contracts + §0.4 landing record; `tests/test_estate_riders_esp.py`, 22). ESP-2 landed at the declare-war seam via the marshal-petition channel rather than objection_v2 — recorded deviation, §0.3. ESP-3 remains open with its diplomacy-gate owner below.

### ESP-1: The Fontainebleau beat (collective marshal petition) — ✅ LANDED
- **Summary:** When several marshals are eroding simultaneously (shortfall past grace), the system today runs parallel silent trust bleeds. History says this moment *speaks*: at Fontainebleau the marshals collectively told Napoleon "the army will not march" and forced the abdication. Fire a collective dialogue when ≥3 marshals are eroding on the same turn — a petition demanding estates, rentes, or peace, with real player choices (concede / refuse with trust cost / partial). Converts the death spiral from a punishment into the game's best scene.
- **When to land:** Jealousy v3.1 gate (next queue item) — the gate already owns marshal-collective emotional mechanics; this is its natural marquee event.
- **Completion definition:** the petition fires under the trigger in a live game, is answerable via popup, each arm has deterministic effects and tests, and STATUS records the landing.
- **Files:** `backend/models/world_state.py` (`_process_dotation_state` trigger), `backend/models/dialogue_manager.py`, `backend/game_logic/dotation.py`, Godot dialogue whitelist (per the dialogue-popup-wiring rule).
- **Est. sessions:** 1

### ESP-2: War-weary rich marshals (satisfaction objects to new wars) — ✅ LANDED
- **Summary:** Historically the *endowed* marshals were the peace party — by 1812–13 the men with duchies begged Napoleon to stop. Mechanically: a marshal whose expectation is fully met and large (satisfaction ≥ a floor) gains an objection trigger against NEW aggressive war declarations ("I have my duchy, Sire — why do we march again?"). Rides the existing objection_v2 ConcernLevel machinery; no new dialogue plumbing.
- **When to land:** Jealousy v3.1 gate, same personality/emotion review.
- **Completion definition:** objection fires for a rich marshal on a player war declaration, never for poor marshals, GR5-checked where applicable, behavior tests.
- **Files:** `backend/commands/objection_v2.py`, `backend/game_logic/dotation.py` (satisfaction query), `backend/game_logic/diplomacy.py` (war-declaration seam).
- **Est. sessions:** 0.5 (folded into the Jealousy build)

### ESP-3: Respect-by-treaty (the Murat clause)
- **Summary:** Treaty transfers of estate provinces currently strip silently on the next tick; only military capture offers the confiscate/respect choice (W6-8). Historically treaty-preserved dotations were real furniture — Murat kept Naples by treaty with Austria (Jan 1814). On ratification of a settlement/treaty that hands YOU a province funding an enemy marshal's estate, fire the same confiscate/respect choice (AI uses its existing at-war rule); respect feeds the existing `respected_estate_mod` +5 acceptance term.
- **When to land:** a future diplomacy gate — touches ratification flow and acceptance math, so it must NOT land ad hoc. Candidate venue: 8.EVAL's diplomacy triage or a Settlement addendum gate.
- **Completion definition:** choice fires at the ratify seam for player-received estate provinces, AI symmetric, acceptance term verified, tests for both arms + the third-party-cede no-choice case.
- **Files:** `backend/game_logic/settlement_ratify.py`, `backend/models/world_state.py` (treaty-clause transfer), `backend/game_logic/dotation.py`, `godot-client/.../capture_choice_dialog.gd` (estate stage reuse).
- **Est. sessions:** 1

### ESP-4: Rente arrears/default beat — ✅ LANDED (folded into the Jealousy build per this row's fold-in clause)
- **Summary:** §0.6.8 pass-1 rentes charge like upkeep with no bankruptcy mercy. The historical texture — rentes chronically in arrears, marshals resenting unpaid paper — is a drama beat: when the treasury cannot cover the rente bill, rentes lapse (auto-revoke) with a notification ("the treasury defaults on his rente — he holds worthless paper, Sire") and the shortfall machinery reopens. Cheap, legible, and makes deficit-financing marshal loyalty a real risk.
- **When to land:** Economy pass 2 (EC-1 successor work), or fold into the Fontainebleau slice if the Jealousy gate takes ESP-1.
- **Completion definition:** insolvency lapses rentes deterministically at one defined seam, notification + dispatch line, both sides GR5, tests incl. the recovery case (re-grant after solvency returns).
- **Files:** `backend/models/world_state.py` (income/bankruptcy seam), `backend/game_logic/dotation.py`, `backend/notifications.py`.
- **Est. sessions:** 0.5


## §NA-6d Audit — routed behaviours (July 19, 2026)

Surfaced by the design-coherence lens of the NA-6d audit-of-the-audit
(record `NATION_AGENDAS_SPEC.md` §21.1). Both are KNOWN, deliberate v1
behaviours homed here so neither is an unowned loose end (GR9).

### NAD-1: Named grievances starved to zero by the shared cap
- **Summary:** `formation_grudge:<tag>` rows share `AGENDA_GRUDGE_CAP` (2)
  with `agenda_grudge`, which emits FIRST at its own value. Two denied
  post-peace courts therefore take the whole budget and **every** named
  question ("The Polish Question", "The Roman Question") vanishes from the
  threat panel with no explanation — the turn after the player watched
  them accrue. This is the same legibility failure the audit's D1 fixed,
  one level up, and it is more reachable than the multi-formation case.
  The mechanical split is correct (the cap is a real ceiling); what is
  missing is the player-facing account of WHY a named row disappeared.
- **When to land:** the next diplomacy/coalition legibility pass, or
  alongside NAD-2 (same surface, same fix shape).
- **Completion definition:** a starved-out contributor is either rendered
  at 0 with an honest "outweighed this turn" note, or named in a single
  overflow line; the panel never silently drops a grievance the player
  has already been shown. Test: build a world with `agenda_grudge` at the
  cap plus one standing formation, assert the panel still accounts for the
  formation.
- **Files:** `backend/game_logic/coalition.py` (step 2 budget split),
  `backend/game_logic/diplomatic_ledger.py` (`_build_balance_of_europe`),
  `godot-client/.../diplomatic_ledger.gd`.
- **Est. sessions:** 0.5

### NAD-2: A third formation emits nothing, silently
- **Summary:** With the cap at 2 and a flat +1 per standing formation, a
  campaign carrying three or more live formations drops the surplus. It is
  debug-logged and pinned
  (`test_grievances_beyond_the_cap_are_dropped_not_silently_merged`), so
  the behaviour is deliberate and not a merge-into-a-neighbour bug — but
  the player sees no trace. Unreachable in shipped data (only Poland and
  the Roman Republic author `aggrieved`), so this is a modding-surface and
  future-content row rather than a live defect.
- **When to land:** with NAD-1 (identical surface), or when a scenario
  authors a third `aggrieved` formable — whichever comes first.
- **Completion definition:** either a validator warning when authored
  `aggrieved` formables exceed `AGENDA_GRUDGE_CAP`, or the NAD-1 overflow
  line covering it. Test: three standing formations, assert the third is
  accounted for on the panel rather than absent.
- **Files:** `backend/game_logic/formations.py`
  (`get_formation_grudge_contributions`), `backend/modding/validator.py`.
- **Est. sessions:** 0.25

### NAD-3: The Duchy of Normandy is a flag with no story
- **Summary:** The coalition-side mirror carve lands on the most
  emotionally loaded moment in the campaign — the player's own homeland
  dismembered — and then the game never mentions it again. Its sibling
  templates both carry more: Warsaw has `commonwealth_restored` (→ Poland)
  plus `guard_the_vistula`; the Roman Republic blocks Italy's risorgimento
  and drags two great powers. Normandy has no deck, no `aggrieved`, no
  follow-on. Related: §11.8 authors WITNESS and AUTHOR subtitles for the
  Proclamation, but the Normandy path creates a third perspective —
  VICTIM — with no authored arm, so a player watching a duchy carved out
  of France reads "A new power takes its seat in Europe."
  (The empty `aggrieved` list itself is CORRECT and settled — §21.1 D3.)
- **When to land:** the next content/authoring pass on NA-6, or whenever
  the naval phase brings DEF-5's Free Ireland carve in (same machinery,
  same victim-perspective gap).
- **Completion definition:** a one-entry Normandy deck authored in
  `europe_1805.json` (pure data, no code) AND a victim-perspective
  subtitle arm on `build_proclamation_card` for a carve from the viewing
  player's own soil; both pinned.
- **Files:** `godot-client/project-sovereign/assets/maps/europe_1805.json`,
  `backend/game_logic/formations.py` (`build_proclamation_card` subtitle).
- **Est. sessions:** 0.5


### NAD-4: A Formables deep link can land on the wrong war
- **Summary:** `build_formables_payload` runs the real eligibility
  predicate PER WAR and knows exactly which war a carve qualifies in
  (`deep_link.war_id`). When the player has TWO OR MORE wars with that
  court, following the link lands on step 2 where `open_settlement` is
  disabled with `multi_war_ambiguity` and a per-war picker — and the
  player can pick the war where the carve is refused, immediately after a
  row told them it was available. The NA-6d audit's first attempt threaded
  the qualifying `war_id` through as a fallback; the audit-of-the-audit
  proved that INERT (an available `open_settlement` always carries its own
  war_id, so the fallback never fires) and the dead machinery was removed.
  The gap itself is untouched and real.
- **When to land:** the next diplomacy-wizard pass, or whenever the
  ambiguity picker is next opened for other reasons.
- **Completion definition:** the ambiguity picker, when reached from a
  Formables deep link, MARKS the qualifying war (or orders it first) so
  the player cannot silently pick a war the carve is refused in. Test:
  two live wars with one court, deep link followed, assert the qualifying
  war is distinguishable in the picker payload.
- **Files:** `godot-client/.../diplomacy_wizard.gd` (picker render),
  `backend/game_logic/formations.py` (`deep_link` already carries it).
- **Est. sessions:** 0.5


---

## Napoleon Campaign — design items (filed August 16, 2026)

> Evidence memo = `docs/audits/PLAYTEST_NAPOLEON_CAMPAIGN_2026_08_16.md`.
> Defects went to `BUG_FIXES.md` §Napoleon Campaign (NPC); these four are
> design calls, not bugs. **None is coded.**

### NPC-D1 — the myth cracks in silence (the §15.4 amendment's missing half)

**What play measured.** Over 22 turns the Emperor's aura fell from **+10% to
+4%**: France lost 13 homeland provinces including Paris, so `get_imperial_grip`
went 100 → **52** and `sovereign_aura_strength` 1.000 → **0.400**. The
mechanic the user asked for ("his losses have weight") is built, correct, and
**was never once narrated**. The only surface that carries it is a modifier
row inside a battle report — and none of the four campaign arms produced one,
because the arc that cracks the aura (losing ground at home) is the arc in
which you stop fighting battles.

Compounding it: **`authority` — the number the card and the briefing show —
never moved off 100** through the whole collapse (NPC-27). The player is shown
the number that did not change and not the number that did.

**The design question.** §15.4 gave the aura a decay curve and one sentence at
the moment of an emperor-led defeat. It has no beat for the *state*. Options,
cheapest first: a standing dispatch producer keyed on the aura crossing a band
("Europe has begun to notice that he can be beaten" as a **briefing** line, not
only a battle tail) · the Generals apex card showing the Presence at its
current strength rather than its authored one · the Gazette treating a crossed
band as a forced special. **Owner: the next narration slice. Completion: the
aura's current value is legible on at least one non-combat surface, and a
crossing is a beat.**

### NPC-D2 — the Seat is a correct v1 and a thin one

`+1 DP` while he holds court in the capital is the whole §8 mechanic. It pays,
it is legible (`seat_bonus: 1`, "+1 the Emperor holds court in the capital"),
and across arm 3's twelve turns it never once made me want him there — because
the alternative is ~30% more army in every battle he attends. This is not a
defect; it is a mechanic that does not yet reach the threshold of a decision.
**Owner: the Victory & Objectives pass** (positions 12–13), which is where
staying home acquires a reason. Completion: a stated reason to keep him at
Paris that is not the DP.

### NPC-D3 — §7 is content nobody will meet

Capture happened **zero times in 68 played turns, on either side**. That is
correct per §7 (true encirclement is meant to be rare) and it means the Eagle
in Chains — the three roads home, the ransom, the Captive Eagle war-score
component, the whole arc — is machinery the median campaign never sees. The
row is not "make it commoner"; it is **decide whether §7 is a rare jewel or
dead weight**, and if the former, whether anything should *tell* the player
the wager exists before it is taken. Related: the enemy-side capture is the
only realistic route, which NP-6 would supply. **Owner: the NP-6 gate.**

### NPC-D4 — what a pursuit should promise (REDUCED, after its premise was killed)

**This row was filed on a false premise and is kept, much smaller, only
because one real question survives it.** The session claimed `attack <distant
marshal>` closes at zero and is therefore a null action; two independent
refuters and a third measurement killed that (~~`BUG_FIXES.md` NPC-4~~) — the
pursuit closes at the pursuer's own `movement_range`, and reached combat in 2
of 5 refuter samples. Nothing about the pursuit RATE needs designing.

What survives is narrower and is a **disclosure** question, not a balance one:
`attack <marshal>` at range silently becomes a multi-turn PURSUE, and the
player is told "Napoleon pursues Mack (at Swabia)" without being told that
this is now a standing order that may take five turns, may be diverted by an
interrupt, and may self-cancel if intelligence lapses (the last of which is
NPC-5's live P1). **The question: should the auto-upgrade announce its own
terms at issue time** — the honest-availability convention this project
already applies to naval chips and the Reward chip — rather than reading like
an attack order that happened to move? **Owner: whoever takes NPC-5**, since
both live at the same acceptance seam (`strategic_executor.py:1400-1403`).

---

## Source Documents (Archived Reference)

| Document | Items Moved Here |
|----------|-----------------|
| `docs/DIPLO_REFINEMENT.md` | Wave 3-5 open items, all R-IDs |
| `docs/DIPLOMACY_DESIGN_FIXES.md` | Design discussion items, N1/A3/A4 AI fixes |
| `docs/archive/PLAYTEST_AUDIT_2026_03_29.md` | War Objectives, Ticking War Score, Vassalage Power Cap, Forced Alliance, Liberation (lines 215-722) |
| `docs/JEALOUSY_SPEC.md` | Jealousy pointer (spec kept as-is) |
