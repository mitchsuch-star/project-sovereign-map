# Slice 10 review round — R2 — GR5, fog, the enemy AI, serialization

Read-only adversarial review of master `f1fe18ab` (FA slice 10, "The
Offer on the Desk"), September 5, 2026. Every finding below was put to
TWO independent refuters whose default verdict was REFUTED — one asked
to reproduce it, one asked whether it is already guarded, unreachable,
or pre-existing. Both verdicts are transcribed under each finding.

Transcribed verbatim from the agent's structured return value.

## The lens's own summary

I read the full production diff and the surrounding code, then probed the tree at f1fe18ab. On GR5 the slice is clean: consent, mount_over_mail and the elimination pair-resolution are all reached only by player-facing surfaces, the AI's own settlement route (settlement_third_party.attempt_third_party_settlement) calls calculate_common_peace_acceptance and never touches compute_per_court_acceptance or consent, _live_covered_for_offer's apparent side inversion is correct (it passes the accepting side as get_coverable_enemy_participants' proposer_side, which is symmetric), and burden_on_nation is direction-correct in both _ratify_treaty arms (the penalty block is inside `if is_player_treaty`). On serialization the consent keys survive to_dict/json/from_dict intact, including with gold and territory terms (probes A and B), and test_serialization_enforcement.py is green; the elimination fix's resolved_diplo_keys/diplo_key_meta writes round-trip and assert_war_instance_invariants passes after an elimination (probe C). I censused every consumer of resolved_diplo_keys and active_diplo_keys and found none that now misreads a resolved pair. On int-to-Godot, amount and amount_offered are both int(), and the only client reader of the mutated snapshot["harshness"] is the harshness_label line the fix targets. What I did find is one regression the slice introduced on its own FA-3 path, proved with a control arm, plus one piece of dead player-facing copy.

## Surviving findings (2 of 2 raw)

### [P2 → NARROWED] FA-3's departed-court drop narrows the COVERAGE but not the TERMS, so the accept draws a Ratify button that the ratification refuses — and the offer is already consumed

**Seam:** `backend/game_logic/settlement_offers.py` :: `handle_incoming_settlement_offer_action (accept_settlement_offer arm) / _live_covered_for_offer`

**Evidence**

Probe G (scratchpad/agent_probes/probe_g_proposer_eliminated.py), on the committed t20 fixture, with the offer carrying the shipped producer's own AUD-c shape ([{'type':'peace'},{'type':'gold_indemnity','from':<proposer>,'to':'France','amount':900}] — _settlement_offer_build_terms always names proposer_nation as payer or payee). Eliminate the proposer (Britain), then accept:
  accept success: True
  departed_courts: ['Britain']
  staged covered   : ['Austria', 'Russia']
  staged terms     : [{"type":"peace"},{"type":"gold_indemnity","from":"Britain","to":"France","amount":900}]
  can_ratify: True | blocked: ''
  options: ['confirm_settlement', 'open_war_detail', 'back_out_settlement']
  RATIFY success: False | error: submitted_terms_failed_revalidation
  validation_error: clause_target_uncovered
  error_display: 'The submitted terms failed validation; review and correct them.'
  pending_settlement_dialogues: []   queue types: []   (the letter is gone)

Probe H (probe_h_without_the_drop.py) is the control: the identical board with _live_covered_for_offer stubbed to return (covered, []) — i.e. the pre-slice shape — stages `can_ratify: False` with `options: ['back_out_settlement']`, no confirm_settlement. So the drop is what creates the button. Reading confirms the mechanism: the accept arm rewrites covered_enemies = live_covered and passes that as both covered_enemy_participants and consenting_courts, but forwards `offered_terms` whole to stage_kwargs['settlement_terms'] and to consent_terms; settlement_ratify's staged_revalidation then runs validate_settlement_terms against the narrowed covered set and rejects the clause whose party was dropped.

**Failure scenario**

A settlement offer is persistent and can stand in the mailbox for many turns. The offering court is then eliminated (the slice's own landing note measures Bavaria eliminated at turn 9 and KingdomOfItaly at turn 10 of the seeded ambient run), or otherwise leaves the war's sides. The player clicks Accept: the review opens, the band reads 'Their own terms', and Ratify is enabled. Pressing it returns 'The submitted terms failed validation; review and correct them.' — but the review was staged with caller_kind='ai_system', so by the slice's own design it advertises no Revise Terms editor (options are confirm/open_war_detail/back_out), and _consume_offer_dialogue plus _remove_pending_settlement_offer already ran on the successful stage, so the letter is gone from both the queue and pending_settlement_dialogues. The player is told to correct terms they cannot reach, on a peace they can no longer re-open. This is the exact 'a Ratify button that was true when it was drawn and false when it is pressed' class that consenting_courts_for_ratification's own docstring exists to close.

**Suggested fix**

Drop the departed court's CLAUSES with its coverage, in the same place: filter offered_terms to terms whose from/to (and vassal/lord/liberator/tag parties) are still in live_covered or the player, and pass the filtered list as both settlement_terms and consent_terms. If filtering would empty or materially change the package, refuse the accept with a stated reason (the offer_courts_all_settled sibling) and leave the letter standing, rather than staging a review that cannot ratify.

**Refuter 1 — NARROWED (severity P3)**

The defect is real and reproduces on the player-reachable route, but its trigger is much narrower than filed and one consequence clause is false.

TRUE STATEMENT: When the offering side-LEADER is ELIMINATED while its settlement offer still stands, AND that offer carries a clause naming the proposer (the producer's decisive-band `gold_indemnity`, or the `create_client` carve — both name `proposer_nation`), `handle_incoming_settlement_offer_action(accept_settlement_offer)` narrows `covered_enemy_participants` to the live courts via `_live_covered_for_offer` but forwards `offered_terms` whole into both `stage_kwargs["settlement_terms"]` and `consent_terms`. The consent path then makes every remaining court read "consented", so the staged review comes back `can_ratify: True`, `ratify_blocked_reason: ''`, with "Ratify Settlement" in `options` and no `disabled_reason_display`. Pressing it fails — validate_settlement_terms V2 rejects the clause whose party is no longer in the narrowed covered set — after `_consume_offer_dialogue` + `_remove_pending_settlement_offer` have already destroyed the letter, on an `ai_system` review that advertises no Revise Terms route. So the button is true when drawn and false when pressed. The slice's drop IS the cause: with `_live_covered_for_offer` stubbed to the pre-slice shape, `can_ratify` is False and `confirm_settlement` is absent from `options` entirely.

FOUR CORRECTIONS to the finding:

1. "eliminated ... OR OTHERWISE LEAVES THE WAR'S SIDES" is wrong — only elimination reaches this. The proposer is always the opposing side LEADER (`ai_diplomacy._settlement_offer_opposing_side_leader`), and `get_coverable_enemy_participants` unconditionally re-adds `_side_leader(...)` if it is still in the side list; the only writer that removes a nation from `war["attackers"]/["defenders"]` anywhere in the backend is `settlement_helpers.mark_participant_eliminated_in_all_wars` (grepped: no other `.remove`/rebuild of a side list exists). A leader that signs its own separate peace therefore stays coverable and never departs. And a departed NON-leader court — FA-3's own motivating Russia case — is never named in any producer-written clause, so it cannot trigger this at all.

2. The frequency evidence is misapplied. The landing record's Bavaria (t9) and KingdomOfItaly (t10) eliminations are on FRANCE'S OWN side of `war_1` (attackers = France, Holland, Bavaria, KingdomOfItaly), so neither can ever be the proposer of an offer to France. The trigger needs an enemy side-leader (here Britain, `defender_leader`) eliminated.

3. The fixture's REAL standing offer carries `settlement_terms: [{"type":"peace"}]` — an even war settles as a white peace with no indemnity clause — and on that package the accept→ratify SUCCEEDS end to end (`Settlement Ratified: France vs Austria + Russia (4 pair(s) resolved)`). The failure needs the decisive-band arm (`|accepter_war_score| >= SETTLEMENT_OFFER_DECISIVE_WAR_SCORE`) or a carve. The finding's own probe hand-wrote its terms; I re-ran it with `_settlement_offer_build_terms` output for the same board and it does reproduce, so the shape claim survives — but only in the decisive band.

4. "on a peace they can no longer re-open" is overstated. `back_out_settlement` returns success cleanly (the letter is not restored, but nothing is corrupted), and the ordinary common-peace route for the same war still stages afterwards: `stage_settlement_confirm(war_id="war_1", actor_nation="France")` → success True, covered ['Austria','Russia']. What is unrecoverably destroyed is the AI's own consenting letter — i.e. the cheap consented band — not the ability to settle the war.

SEVERITY: P3, not P2. The class is right (an enabled Ratify that lies) but it needs an eliminated enemy side-leader with a standing decisive-band offer, causes no state corruption, and leaves a working exit. Note also that the pre-slice arm is a dead end too (no Ratify option, and the ratify would have failed anyway with `clause_side_mismatch`), so the regression is specifically "no button" → "enabled button that fails", not "working" → "broken".

<details><summary>What the refuter ran or read</summary>

Read first, in the snapshot at f1fe18ab: settlement_offers._live_covered_for_offer, the accept_settlement_offer arm of handle_incoming_settlement_offer_action (covered_enemies = live_covered is passed as covered_enemy_participants AND consenting_courts, while offered_terms goes whole into settlement_terms and consent_terms), settlement_validation.validate_settlement_terms V2 (`clause_target_uncovered`), get_coverable_enemy_participants (the unconditional `leader in enemies` re-add), ai_diplomacy._settlement_offer_build_terms + its caller (proposer = opposing side leader; indemnity only outside the even band), settlement_helpers.mark_participant_eliminated_in_all_wars, and dialogue_manager.clear_stale (offers are SOFT_STOP_MAILBOX_TYPES, so a standing offer is never swept).

Probes (all read-only, written under scratchpad/agent_probes, run with .venv/Scripts/python.exe from the repo root, INK_IRON_SAVE_DIR redirected, SOVEREIGN_SCENARIO popped, built from tests/fixtures/playtest_saves/fixture_t20_ambient.json):

ref_a_inspect.py — the fixture's standing offer: proposer Britain, proposer_side defenders, accepting_side attackers, covered ['Britain','Austria','Russia'], settlement_terms [{"type":"peace"}]. war_1: attackers ['France','Holland','Bavaria','KingdomOfItaly'], defenders ['Britain','Austria','Russia'], defender_leader Britain.

ref_b_repro.py — three arms after world._eliminate_nation("Britain") (which leaves war_1 active: defenders ['Austria','Russia'], leader re-picked to Austria, 4 pairs still active, war not archived):
  ARM 1, the fixture's real terms [{"type":"peace"}]: accept True, departed ['Britain'], can_ratify True, RATIFY True — no defect.
  ARM 2, the finding's hand-written indemnity: RATIFY False / clause_target_uncovered.
  ARM 3, terms from the SHIPPED producer for this exact board — _settlement_offer_build_terms(accepter="France", proposer_nation="Britain", war_age_turns=20, accepter_war_score=60, world=w) = [{"type":"peace"},{"type":"gold_indemnity","from":"Britain","to":"France","amount":3770}]: accept True, staged covered ['Austria','Russia'], staged terms unchanged, can_ratify True, RATIFY False / clause_target_uncovered, queue [] and pending_settlement_dialogues [] (letter gone). At war_score 0 the producer returns [{"type":"peace"}] only; at -60 it returns from France to Britain — also proposer-named, also fatal.

ref_c_options.py — the drawn options and the control. Shipped: options confirm_settlement / open_war_detail / back_out_settlement, none carrying `available` or `disabled_reason_display`, can_ratify True, ratify_blocked_reason '', per-court bands Austria "consented", Russia "consented". Control (only `_live_covered_for_offer` monkeypatched to the pre-slice (covered, []) shape): covered ['Austria','Britain','Russia'], Britain "reject", can_ratify False, options = ['back_out_settlement'] only — no Ratify drawn. So the drop is what draws the button.

ref_d_aftermath.py — ratify #1 and #2 both fail with the same error; the review stays mounted with can_ratify still True; back_out_settlement succeeds and leaves current None, queue [], pending []; a fresh stage_settlement_confirm for war_1 succeeds (covered ['Austria','Russia']).

ref_e_player_route.py — the player-reachable route, not the raw ratifier: handle_settlement_dialogue_action(action="confirm_settlement") → success False, error submitted_terms_failed_revalidation, validation_error clause_target_uncovered, error_display "The submitted terms failed validation; review and correct them.", message "Sire, the terms we staged no longer hold against the present situation — this settlement cannot be ratified as written.", France|Austria still WAR. The white-peace arm on the same board → success True, France|Austria PEACE.

</details>

**Refuter 2 — NARROWED (severity P3)**

REAL, and this commit is responsible for the false affordance — but the trigger is materially narrower than filed, and part of the harm is pre-existing.

WHAT IS CONFIRMED. In `settlement_offers.handle_incoming_settlement_offer_action` (accept_settlement_offer arm), `_live_covered_for_offer` narrows `covered_enemies` and that narrowed list is passed as BOTH `covered_enemy_participants` and `consenting_courts`, while `offered_terms` is forwarded whole as `settlement_terms`/`consent_terms`. `stage_settlement_confirm` does not validate caller-supplied terms (the `validate_settlement_terms` calls in settlement_baseline guard GENERATED baselines; the one in settlement_staging is inside `_restage_settlement_confirm`, not the stage path), so the review stages with a clause naming a court no longer covered. `settlement_ratify` then re-validates and rejects with `clause_target_uncovered`.

Measured with the SHIPPED producer's own terms (not hand-written): `_settlement_offer_build_terms` at accepter_war_score=35 emits `[{"type":"peace"},{"type":"gold_indemnity","from":"Britain","to":"France","amount":3770}]`. Button label is literally "Ratify Settlement", enabled; pressing it returns "The submitted terms failed validation; review and correct them."; the review stays mounted with the identical options, so it can be pressed again indefinitely.

THE COMMIT IS RESPONSIBLE. Three-arm comparison on one board (z_parent_shape.py): PARENT shape (no drop, no consent) → can_ratify False, options ['back_out_settlement']; drop absent + consent present → can_ratify False; SHIPPED (drop + consent) → can_ratify True, options ['confirm_settlement','open_war_detail','back_out_settlement']. It takes BOTH new mechanisms — the drop makes the clause uncovered, the consent overrides the reject bands — and both are this commit's.

FIRST NARROWING — the trigger is elimination of the war LEADER, not "a court departs". The producer only ever names `proposer_nation` in a clause (gold_indemnity from/to, create_client to), and `proposer_nation` is by construction the opposing side's leader (`_settlement_offer_opposing_side_leader` reads the same `defender_leader`/`attacker_leader` key `_side_leader` reads). `get_coverable_enemy_participants` unconditionally re-adds the side leader if it is still in `war_instance[accepting_side]`. Measured four departures on the t20 fixture: proposer's pair resolved by `resolve_pair_to_resolved` (an ordinary separate peace) → NOT dropped, live=['Britain','Austria','Russia'], and accept→ratify SUCCEEDS; proposer ELIMINATED → dropped. So the finding's "eliminated ... or otherwise leaves the war's sides" is wrong for the separate-peace case, and its citation of routine minor eliminations (Bavaria t9, KingdomOfItaly t10) does not by itself qualify — those must be the war's leader. Full trigger: (a) |war score| ≥ SETTLEMENT_OFFER_DECISIVE_WAR_SCORE = 20 at offer time, (b) the proposer/leader is ELIMINATED, (c) at least one other covered court still at war (otherwise the slice's own honest `offer_courts_all_settled` refusal fires), (d) the player answers the stale letter afterwards.

SECOND NARROWING — the harm. The letter's destruction is PRE-EXISTING: the parent arm ran `_remove_pending_settlement_offer` + `dialogue_manager.pop()` unconditionally BEFORE staging. The terms being unratifiable is also pre-existing (parent ratify fails too, with `clause_side_mismatch`). What is new is only the enabled button. And the player is not stranded on "a peace they can no longer re-open": "Back Out" is offered, and war-detail / the F1 wizard still reach a settlement — only the LETTER is unrecoverable, which it also was pre-slice.

NOT GUARDED. No staging-time validation on caller-supplied terms; no sweep removes a standing offer when its proposer leaves the war (measured: elimination leaves the letter current); `incoming_settlement_offer` is in SOFT_STOP_MAILBOX_TYPES and exempt from both `clear_stale` and `lapse_pending_offers`, so it persists indefinitely; the review is `caller_kind="ai_system"` by design so no editor is advertised. The slice's own FA-3 test (`test_a_court_that_has_made_its_own_peace_is_dropped_and_named`) drops `covered[-1]` = Russia, a non-leader, on the fixture's bare `[{"type":"peace"}]` package — it can never touch a clause-bearing package.

REACHABLE from the player: `accept_settlement_offer` and `confirm_settlement` are both in `main.gd`'s dialogue-action list, so the popup buttons drive this path.

SEVERITY: P3, not P2. The class is exactly what the slice exists to close (a button true when drawn, false when pressed), but it needs an eliminated war leader plus a decisive-score offer plus a stale letter, and the outcome is a repeatable honest error message plus a letter that was already being destroyed before this commit.

<details><summary>What the refuter ran or read</summary>

All probes read-only against the working tree at f1fe18ab, on the committed fixture tests/fixtures/playtest_saves/fixture_t20_ambient.json, INK_IRON_SAVE_DIR redirected to the scratchpad, no parser touched.

1) z_inspect_offer.py — the fixture's real standing offer: type incoming_settlement_offer, war_1, proposer Britain, accepting_side attackers, covered ['Britain','Austria','Russia'], settlement_terms [{'type': 'peace'}] (a BARE white peace — the probe-G terms were injected). After world._eliminate_nation('Britain'): current dialogue is STILL incoming_settlement_offer, pending_settlement_dialogues [], war_1 still present, Britain's pairs moved to resolved_diplo_keys (FA-S10-1 working), Britain gone from side_by_nation. => no sweep removes the letter.

2) Reading: ai_diplomacy._settlement_offer_build_terms — payer/payee are only `accepter` and `proposer_nation`; _settlement_offer_carve_clause writes {"type":"create_client","from":player,"to":proposer_nation}. SETTLEMENT_OFFER_DECISIVE_WAR_SCORE = 20. _settlement_offer_opposing_side_leader reads war['defender_leader']/['attacker_leader']; settlement_validation._side_leader reads the same keys; get_coverable_enemy_participants ends with `leader = _side_leader(...); if leader in enemies: coverable.add(leader)`.

3) z_after_failure.py — SHIPPED path, terms from the real producer, proposer eliminated:
   REAL producer terms: [{"type":"peace"},{"type":"gold_indemnity","from":"Britain","to":"France","amount":3770}]
   Britain still a war participant: False
   accept: True  departed: ['Britain']
   note shown to player: Britain has already made her own peace; these terms now bind the courts that remain.
   can_ratify: True
   options offered: ['confirm_settlement', 'open_war_detail', 'back_out_settlement']
   labels: ['Ratify Settlement', 'Open War Detail', 'Back Out']
   RATIFY: False submitted_terms_failed_revalidation clause_target_uncovered
   told the player: The submitted terms failed validation; review and correct them.
   after failure -> mounted: settlement_confirm options: ['confirm_settlement', 'open_war_detail', 'back_out_settlement']
   offer recoverable: [] []
   France|Britain state: PEACE ; France|Austria state: WAR

4) z_parent_shape.py — attribution, three arms on one board:
   PARENT shape (no drop, no consent): can_ratify False | options ['back_out_settlement'] | bands Austria/Britain/Russia all reject | RATIFY False clause_side_mismatch
   no drop, WITH consent:              can_ratify False | options ['back_out_settlement'] | Austria/Russia consented, Britain reject | RATIFY False clause_side_mismatch
   SHIPPED (drop + consent):           can_ratify True  | options ['confirm_settlement','open_war_detail','back_out_settlement'] | RATIFY False clause_target_uncovered
   git show a1ed5c9d:backend/game_logic/settlement_offers.py confirms the parent arm: covered_enemies = full list, _remove_pending_settlement_offer + dialogue_manager.pop() BEFORE stage_settlement_confirm, caller_kind 'ai_system', no consent kwargs.

5) z_reach.py — which departures drop the proposer (t20 fixture):
   A. proposer pair resolved (separate peace) live=['Britain','Austria','Russia'] departed=[]   defenders ['Britain','Austria','Russia']
   B. Russia pair resolved (non-leader)       live=['Britain','Austria']          departed=['Russia']
   C. proposer eliminated                     live=['Austria','Russia']           departed=['Britain']
   D. Russia eliminated (non-leader)          live=['Britain','Austria']          departed=['Russia']
   z_ordinary_path.py separately confirms arm A end to end: real producer terms, set_diplomatic_state(France,Britain,PEACE), accept -> departed None, can_ratify True, RATIFY: True (no defect).

6) Guard search: grep for _remove_pending_settlement_offer / remove_matching / pending_settlement_dialogues outside settlement_offers.py finds no departure-driven sweep; DialogueManager.CURRENT_TURN_OFFER_TYPES excludes incoming_settlement_offer (so lapse_pending_offers never touches it) and clear_stale `continue`s on SOFT_STOP_MAILBOX_TYPES in both the queue sweep and the active slot. tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py::test_a_court_that_has_made_its_own_peace_is_dropped_and_named uses covered[-1] (Russia, non-leader) on the bare white-peace fixture. godot-client/.../main.gd lines ~54 and ~126 list confirm_settlement and accept_settlement_offer.

</details>

### [P3 → CONFIRMED] departed_courts_note is written into the result and read by nothing — and when it is read it will misdescribe an eliminated court as having made peace

**Seam:** `backend/game_logic/settlement_offers.py` :: `_departed_courts_note (and the two result['departed_courts_note'] writes in handle_incoming_settlement_offer_action)`

**Evidence**

Whole-repo census: `grep -rn "departed_courts" --include=*.py --include=*.gd .` returns only the producer in settlement_offers.py (the def, the two _live_covered_for_offer call sites, and the four result-key writes) plus the slice's own test file. No backend consumer folds it into `message`, and no .gd reads it — `grep -rn "amount_offered\|departed_courts\|consent_display" godot-client/ --include=*.gd` returns nothing. So FA-3's stated promise ('It is dropped from the coverage, and the player is told which') is not delivered. Separately, probe C (probe_c_elimination_and_departed.py) eliminated Russia on the t20 fixture and then accepted the standing offer; the produced sentence was verbatim: 'Russia has already made her own peace; these terms now bind the courts that remain.' Russia had been annihilated, not settled — the elimination path is precisely the one the slice's own FA-S10-1 fix makes ordinary (resolve_reason 'participant_eliminated' was stamped on the pair in the same probe).

**Failure scenario**

A coalition offer covers a court that is subsequently conquered. The player accepts; the coverage silently shrinks and nothing on any surface says so, so the terms they thought they were signing are not the terms that bind. If a later slice wires the sentence up as written, it then tells the player that a nation France destroyed 'has already made her own peace'.

**Suggested fix**

Either wire the note into a surface the player sees (append it to the staged review's message / talleyrand_text, or render it on the settlement_confirm popup) or delete the producer. Whichever way, derive the phrasing from why the court left — participant_meta[nation]['exit_path'] is already stamped 'eliminated' by mark_participant_eliminated_in_all_wars — so an annihilated court is not described as having settled.

**Refuter 1 — CONFIRMED (severity P3)**

CONFIRMED on both halves, with one narrowing to the stated failure scenario.

TRUE STATEMENT (half a — the dead key): `settlement_offers._departed_courts_note` is produced at both `handle_incoming_settlement_offer_action` success tails (the accept arm and the request-revision arm) and stamped onto the result as `departed_courts_note` / `departed_courts`. It is never folded into `result["message"]` and it is never written onto the staged `diplomatic_dialogue`. `main._build_result_response` does pass it to the wire as a top-level key (`**extra`), so it is not stripped — but the Godot client renders the settlement review from `response.diplomatic_dialogue` (`main.gd::_show_proposal_confirm_popup` / `PROPOSAL_CONFIRM_DIALOGUE_TYPES`) and the terminal renders `message`. Neither carries the sentence, and `grep -rn "departed_courts" godot-client/` is empty. So the docstring promise in `_live_covered_for_offer` — "It is dropped from the coverage, and the player is told which" — is not delivered on any surface. The slice's own pin (`test_a_court_that_has_made_its_own_peace_is_dropped_and_named`) asserts only the result key, so it is green while the promise is unkept. The key is also not homed anywhere: `grep -rn "departed_courts" docs/` returns nothing, so there is no owner row or landing slice for the missing wiring (GR9).

TRUE STATEMENT (half b — the wrong sentence): the copy is unconditional ("X has already made her own peace"), while `_live_covered_for_offer` derives departure from `get_coverable_enemy_participants`, which drops a nation the moment it is off the war's side lists. `mark_participant_eliminated_in_all_wars` does exactly that and stamps `resolve_reason: "participant_eliminated"`, so an ANNIHILATED court is narrated as having made its own peace. This is not a hypothetical geometry: `world._eliminate_nation` does not touch pending settlement offers or the dialogue manager, so a standing offer survives the elimination of a court it covers.

NARROWING of the failure scenario as filed: "the coverage silently shrinks and nothing on any surface says so, so the terms they thought they were signing are not the terms that bind" over-states it. The staged review DOES show the surviving coverage — in my probe the staged dialogue's `covered_enemy_participants` was `['Austria', 'Britain']` and the success message read "the white peace for France vs Austria + Britain". So the player can see WHO is bound; what is missing is any statement that a court was dropped and why. The defect is legibility (an unkept promise plus a latent wrong sentence), not a mis-signed treaty, and the mechanical drop itself is correct.

Severity P3 is correct and I hold it. There is no mechanical harm, and the wrong sentence is presently undisplayable — but it becomes player-visible the instant anyone wires the key up as written, and the elimination path is precisely the one FA-S10-1 makes ordinary in this same commit.

<details><summary>What the refuter ran or read</summary>

READING (snapshot at f1fe18ab):
* `backend/game_logic/settlement_offers.py::_departed_courts_note` — the sentence is unconditional: `f"{names[0]} has already made her own peace; these terms now bind the courts that remain."` No branch on why the court departed.
* `::_live_covered_for_offer` — departure = "not in `get_coverable_enemy_participants(war, accepting_side)`". `settlement_validation.get_coverable_enemy_participants` builds `enemies` from `war_instance[accepting_side]`, so any nation taken off the side lists is "departed".
* `settlement_helpers.mark_participant_eliminated_in_all_wars` removes the nation from `attackers`/`defenders`/`active_participants`/`side_by_nation` and (new in this commit, behind ELIMINATION_RESOLVES_ITS_PAIRS) stamps `resolve_reason = "participant_eliminated"`.
* `world_state._eliminate_nation` (lines 3952-4060) touches marshals, treaties, vassals, diplomatic_states and calls the helper above — it never touches `dialogue_manager` or pending settlement offers.
* `main._build_result_response` forwards unknown result keys via `**extra`; `main.gd` renders `response.diplomatic_dialogue` (line ~2473, `PROPOSAL_CONFIRM_DIALOGUE_TYPES`) and `message`.

CENSUS (run against the working tree at the same SHA, not just the snapshot):
  grep -rn "departed_courts" --include=*.py --include=*.gd --include=*.tscn .
  -> only settlement_offers.py (def + 2 `_live_covered_for_offer` call sites + 4 result-key writes) and 2 asserts in tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py.
  grep -rn "departed_courts|consent_display|amount_offered" godot-client/  -> EMPTY.
  grep -rn "departed_courts" docs/  -> EMPTY (not homed).

PROBE 1 — scratchpad/agent_probes/refute_departed.py, on tests/fixtures/playtest_saves/fixture_t20_ambient.json, mock parser, INK_IRON_SAVE_DIR redirected, no turn ended. Loaded the fixture, took the CURRENT `incoming_settlement_offer` (war_1, covered ['Britain','Austria','Russia']), eliminated Russia via `mark_participant_eliminated_in_all_wars`, then accepted the offer. Output:
  offer still standing after elimination: True
  success: True
  departed_courts: ['Russia']
  departed_courts_note: 'Russia has already made her own peace; these terms now bind the courts that remain.'
  NOTE IN MESSAGE: False
  NOTE IN STAGED DIALOGUE: False
  staged keys containing 'depart': []
  staged covered: ['Austria', 'Britain']
  pair meta France|Russia -> {... 'pair_status': 'resolved', 'resolved_turn': 20, 'resolve_reason': 'participant_eliminated'}

PROBE 2 — scratchpad/agent_probes/refute_departed2.py, same fixture, but through the REAL entry point `world._eliminate_nation("Russia")` (to close the "you used a helper, not the production path" refutation), then through `main._build_result_response`:
  offer survives real _eliminate_nation: True
  still covers Russia: True
  note: 'Russia has already made her own peace; these terms now bind the courts that remain.'
  note key present on wire: True
  wire message: 'Sire, the white peace for France vs Austria + Britain is ready: ...'
  note inside wire message: False
  note anywhere inside diplomatic_dialogue (what the popup renders): False

So: the branch is reachable through production elimination, the sentence is produced verbatim as filed, and it reaches the wire but no surface the client renders. No mutating git command was run; no file under the repo was edited; the full suite and mutation_sweep were not run.

</details>

**Refuter 2 — NARROWED (severity P4)**

Real but much smaller, and the filed failure scenario is refuted. TRUE: `settlement_offers._departed_courts_note` is new in f1fe18ab and its output reaches no surface — one producer, zero consumers in backend/ and godot-client/, not folded into `message`, not on the staged dialogue, and not on `result["diplomatic_dialogue"]`. TRUE: if it were ever wired, an ELIMINATED court is described as having "already made her own peace" — though the cause is `_live_covered_for_offer` equating "not coverable" with "settled", NOT FA-S10-1's pair move (mark_participant_eliminated_in_all_wars already strips the nation from attackers/defenders, and get_coverable_enemy_participants starts from that side list, so the court departs coverage with or without the pair change).

REFUTED: "the coverage silently shrinks and nothing on any surface says so, so the terms they thought they were signing are not the terms that bind." Measured control-vs-treatment on the t20 fixture — the review the player ratifies names the live courts twice over. Control message: "the white peace for France vs Austria + Britain + Russia"; per_court_acceptance rows [Austria, Britain, Russia]. After Russia departs: message "for France vs Austria + Britain"; rows [Austria, Britain]. per_court_acceptance is rendered by proposal_confirm_popup.gd. So the binding coverage IS on screen, by name, before signature; the mechanically load-bearing half of FA-3 (drop the unscoreable court) lands and is visible, and it is pinned by the slice's own test via the staged dialogue assertion. What is missing is only the causal sentence naming which court left and why.

So the residue is a dead result key carrying unreachable copy — P4 cosmetic/hygiene, not P3. Two mitigating precedents: `accepted_offer_terms` (blames to c38e9e7b, June 10, 2026) and `counter_seed_terms` are sibling result-dict echoes with zero production consumers, i.e. the established house pattern for audit/provenance keys, and this key is consumed by the slice's test. The one point that survives against the commit is that `_live_covered_for_offer`'s docstring over-claims ("the player is told WHICH") relative to what the key delivers, and an orphaned player-facing note is a class this project has previously recorded as a defect (`arc_note`, CA8-9). Recommended disposition: either delete the note (the coverage enumeration already carries the meaning) or wire it and fix the wording to distinguish a court that made peace from one that was destroyed — not a fix that blocks the slice.

<details><summary>What the refuter ran or read</summary>

READING (1) Whole-repo census confirming zero consumers: `grep -rn "departed_courts" --include=*.py --include=*.gd .` -> only settlement_offers.py (def _departed_courts_note; two _live_covered_for_offer call sites; four result-key writes) plus tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py:553-554. `grep -rn "departed" godot-client/` -> no output.
(2) Novelty: `git show a1ed5c9d:backend/game_logic/settlement_offers.py | grep -n "_live_covered_for_offer\|_departed_courts_note\|offer_courts_all_settled"` -> empty. Machinery is new in f1fe18ab.
(3) Precedent: `git blame -L 2965,2975 backend/game_logic/settlement_offers.py` -> `result["accepted_offer_terms"]` is c38e9e7b (2026-06-10), also zero production consumers.
(4) `get_coverable_enemy_participants` (settlement_validation.py) computes enemies from war_instance[accepting_side]; `mark_participant_eliminated_in_all_wars` (settlement_helpers.py) removes the nation from attackers/defenders — so elimination drops it from coverage independent of FA-S10-1's active_diplo_keys move.
(5) `grep -rn "per_court_acceptance" godot-client/` -> proposal_confirm_popup.gd (lines 272, 543-544, 760, 822): the per-court table is client-rendered.

PROBE A (scratchpad/agent_probes/probe_departed_note.py; t20 fixture via WorldState.from_dict, SOVEREIGN_SCENARIO popped, INK_IRON_SAVE_DIR set, no parser touched):
  offer found from fixture: True / war: war_1 / covered: ['Britain','Austria','Russia']
  ELIMINATED: Russia
  live: ['Britain','Austria'] / departed: ['Russia']
  NOTE: Russia has already made her own peace; these terms now bind the courts that remain.
  accept success: True / result departed_courts: ['Russia'] / result note: <same sentence>
  result message: "Sire, the white peace for France vs Austria + Britain is ready: no terms exchanged, no map redrawn - only the war ends. Ratify and the field falls quiet."
  note appears in message?: False
  staged has depart keys: []  |  staged covered: ['Austria','Britain']  |  staged per-court: ['Austria','Britain']
  result.diplomatic_dialogue depart keys: []

PROBE B (probe_control_no_elim.py, same fixture, NO elimination — the control the finding lacked):
  covered: ['Britain','Austria','Russia']
  CONTROL message: "Sire, the white peace for France vs Austria + Britain + Russia is ready..."
  staged covered: ['Austria','Britain','Russia'] / per-court rows: ['Austria','Britain','Russia']

The A-vs-B delta is the refutation: both the headline sentence and the client-rendered per-court table shrink from three named courts to two, so the reduced binding coverage is disclosed on the ratification surface. No git mutation, no suite run, no mutation sweep, no repo file written.

</details>
