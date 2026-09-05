# REPRO G2 -- "the offering side consents" (FA-3), Sept 5, 2026

Read-only reproduction against master `a1ed5c9d`, mock parser, sandboxed saves,
every arm driven through the real routes (`POST /mailbox/activate`,
`POST /respond_to_diplomatic_dialogue`, the real producer
`ai_diplomacy.process_settlement_offer_phase` + `settlement_offers.promote_pending_settlement_offers`).
Both Sept-2 verifier readings are truncated in every record (rows file, the
machine JSON, the verification report table), so the narrowing below is
RE-DERIVED BY MEASUREMENT, not quoted.

## Summary

- **FA-3 -- NARROWED (the headline geometry REPRODUCES; the universality clause is FALSE; the mechanism is mis-attributed).**
  Accepting the AI's incoming offer pops the offer and re-stages its package as a
  France-PROPOSED review whose accepting side is the offering courts, so the
  scorer prices the author's own terms as the author's reluctance to sign them:
  on the shipped boot (t4) and the committed t20 fixture the white peace stages
  `can_ratify=False` / "Settlement legitimacy" / no `confirm_settlement`
  (Austria 5, Britain -2, Russia -2 at t4; 18/10/10 at t20). But the
  block is NOT universal and NOT primarily the -10 tier base: (a) a bare peace
  CARRIES when the proposer side's (best-ally) pressure is >= ~45 with war
  exhaustion at cap (measured +60 whole-side: 74/66/66), (b) the winning arm's
  REAL offer dies on `term_harshness_penalty` (the purse-priced 3,770g
  Britain->France indemnity saturates at -45 and fails even at +100: 45/37/37;
  a 500g indemnity at +60 carries 62/54/54 -- EWC-F1 exactly), (c) the losing
  arm's real offer (France pays 6,994g) reaches 52 for the no-agenda court at
  -20 but never for the two agenda courts (44/44), and dies on
  `base_side_pressure` below that (-60: 36/28/28) -- the scorer's "why would
  the winner settle" term charged against the very court that wrote the offer.
  The dead review is NOT the offer's end: no cooldown is written on accept and
  Britain re-offers on the next AI phase with CURRENT terms. The row's
  fix_shape breaks in three places (below). The minimal correct fix is a
  dialogue-carried `consenting_courts` set honoured at BOTH scoring seams
  (`build_settlement_preview`/`compute_per_court_acceptance` AND
  `ratify_settlement_confirm`), plus staleness re-validation of the offer
  against the live war -- everything downstream already works (probe 7
  ratified the accepted package through the real confirm route with the
  scorer short-circuited: 6 pairs resolved, all three courts PEACE).

## Per row

### FA-3 (P1, Sept-2 NARROWED)

**Row text read first** (`_corrected` before title): the claim is that
`accept_settlement_offer` forwards `actor_nation=player` and drops the
offer's `proposer_side` (true, and DOCUMENTED at the seam: "Forwarding the AI
side here would fail `not_side_leader`"), that the scorer's white-peace -10
tier base plus agenda -8 keeps EVERY offering court under 50 "winning or
losing", that the staged `settlement_confirm` therefore carries
`ratify_blocked_reason` and no ratify option, that the producer never scores
its own package, and that the offer is popped BEFORE staging so "the dead
review is the offer's end".

**What I ran**: `repro/g2/probe_1.py` (boot t1->t4, activate the queued offer via
`/mailbox/activate`, accept), `probe_2.py` (t20 fixture, offer current, accept;
stale-coverage census), `probe_3.py` (t20 fixture with stored pair scores
rewritten +/-60/+/-100 France-only and whole-side, the REAL producer re-emitting,
plus bare-peace isolation arms at +60/+40/+30/-60), `probe_4.py` (design
questions 5a/5c/5d), `probe_5.py` + `probe_7.py` (stale coverage through
`set_diplomatic_state` alone and through the real `cleanup_war_end(world, key)`
seam; feasibility of consent-by-construction through the real confirm route),
`probe_6.py` (indemnity-amount boundary, the losing arm at -20/-25/-30/-40, the
producer/scorer divergence arm, the boot-WE arm). Shared helpers `g2_common.py`.

**Raw evidence (excerpts).**

ARM 1, shipped boot, turn 4 (the offer is QUEUED behind Hesse's and the Papal
letters; I activated it with `POST /mailbox/activate {"mailbox_id": 8}` -- an
accept sent while a letter was current is correctly refused `stale_dialogue`):
```
offer settlement_offer:war_1:3:1  proposer Britain/defenders  accepting France/attackers
covered ['Britain','Austria','Russia']  terms [{'type':'peace'}]
France stored vs: Britain -1, Austria -12, Russia 0   (sum -13)   WE 24/24/24
accept -> success True, dialogue_type settlement_confirm (id 10), dialogue_mode REVIEW, caller_kind ai_system
staged proposer_side attackers / accepting_side defenders / white_peace True
can_ratify False | ratify_blocked_reason 'Settlement legitimacy'
options [seek_bilateral_peace, seek_armistice_instead, open_war_detail, back_out_settlement]
Austria total 5  direct 9  comps {war_exhaustion 16, settlement_tier_legitimacy -10, agenda_settlement_mod -8, leader_own_losses 5, base_side_pressure 2}
Britain total -2 direct -1 comps {tier -10, WE 9, agenda -8, leader 5, base 2}
Russia  total -2 direct 0  comps {tier -10, WE 9, agenda -8, leader 5, base 2}
message: "Sire, a white peace for France vs Austria + Britain + Russia cannot be sealed as it stands: the terms claim a victory the field has not delivered."
after: current = settlement_confirm 10; queue = [incoming_proposal 8, incoming_proposal 7]; pending_settlement_dialogues []
```

ARM 2, t20 fixture (offer current, created turn 3, i.e. 17 turns stale):
```
France stored vs: Britain -54, Austria -26, Russia 0   (sum -80)   WE 154/154/152
scorer direct_score column: Austria 25, Britain -9, Russia 0   <- MAX over proposer-side members, not France
can_ratify False | 'Settlement legitimacy' | Austria 18 / Britain 10 / Russia 10
```

ARM 3, the real producer re-run on the t20 fixture with rewritten scores
(`world.war_scores[diplo_key]`, orientation handled; cooldown + promoted offer cleared):
```
W60 whole-side  producer terms: peace + gold_indemnity Britain->France 3770
   can_ratify False 'Term harshness'   Austria 19 / Britain 11 / Russia 11
   comps: term_harshness_penalty -45, base_side_pressure 39, WE 20, leader 5, (agenda -8 B/R), tier 0
W100 whole-side same 3770g:  45 / 37 / 37  (base 60, tier +5 = total_victory 15 minus ceiling mismatch 10, harshness -45)
L60 France-only  producer terms: peace + gold_indemnity France->Britain 6994
   can_ratify False 'Settlement legitimacy'  35 / 27 / 27   tier -20 (!) = white_peace -10 + mismatch -10 on a PROPOSER-PAID clause
L60 whole-side:  36 / 28 / 28  'Base side pressure'  comps: concession_credit 40, base -39, WE 20, tier +10, leader 5
L100 whole-side: 30 / 22 / 22  (base -50, concession 40, tier 15, WE 20, leader 5)
BARE PEACE forced (hand-built offer, same accept handler):
   +60 whole-side: can_ratify TRUE  74 / 66 / 66   options [confirm_settlement, open_war_detail, back_out_settlement]
   +40 whole-side: 56 / 48 / 48  (Britain/Russia miss on agenda -8)      +30: 45 / 37 / 37      -60: -4 / -12 / -12
```

Probe 6 boundaries:
```
WIN +60  Britain->France  500g: CARRIES 62/54/54 (harshness -12, tier +10)   1000g: 40/32/32 (harshness -24, tier 0 = mismatch)   1875g+: 19/11/11 (-45)
WIN +100 Britain->France  500g: 88/80/80   1000g: 76/68/68 CARRIES   1875g+: 45/37/37
LOSE -20 real producer (France->Britain 6473g): Austria 52 ACCEPT / Britain 44 / Russia 44  -> blocked 'Base side pressure'
LOSE -25: 49/41/41   -30: 45/37/37   -40: 44/36/36
DIVERGENCE (France +5 each, sum 15 -> producer emits a BARE peace; allies +60): Austria 57 / Britain 49 / Russia 49 -> blocked 'National design' (one point on agenda -8)
DIVERGENCE with WE 24 (boot exhaustion): 45 / 37 / 37
```
Gold harshness is `0.08 per 100g` (`diplomatic_templates._accumulate_raw_treaty_harshness`), so
1,875g = 1.5 = the -45 saturation; the producer's EC-W4 purse pricing
(`SETTLEMENT_OFFER_TREASURY_FRACTION` 0.15 .. `MAX_TREASURY_FRACTION` 0.40 of the
payer's chest) put 3,770g on the table = Britain's 40% cap.

Probe 4 (design questions):
```
5(a1) evaluate_open_settlement_eligibility(actor=France, proposer_side=defenders) -> available False, error 'not_side_leader'   [the code comment is TRUE]
      stage_settlement_confirm(proposer_side=defenders, actor=France) with the offer still mounted -> 'settlement_scope_replace_confirm'  [FA-N18's same-war arm fires BEFORE eligibility]
5(a2) from Britain's seat (actor=Britain, proposer_side=defenders, covered=[France]): France as the accepting court scores 65, "Will carry"  [the scorer says FRANCE accepts]
5(c)  staged dialogue with can_ratify FORCED True + confirm_settlement -> error 'acceptance_rejected', score 10; the re-attached dialogue still echoes can_ratify True / ratify_blocked_reason ''  [a staging-only flag is dead at ratify AND leaves a lying button]
5(d)  after accept: pending [], cooldown {'war_1': 8} (the turn-3 stamp, long expired), producer eligibility None -> end turn -> turn 21: Britain re-offers settlement_offer:war_1:20:1 = peace + France->Britain 6994g, QUEUED behind an incoming_proposal
```

Probes 5/7 (stale coverage): after France-Russia PEACE the standing offer still
covers Russia. Through the REAL seam (`cleanup_war_end(world, "France|Russia")`):
```
instance: active_participants drops Russia (exit_path separate_peace), pair -> resolved_diplo_keys, side_by_nation no longer lists Russia
get_coverable_enemy_participants(live) = ['Austria','Britain']   the producer's NEXT offer covers ['Britain','Austria']
the STANDING offer still covers ['Britain','Austria','Russia'] -> accept stages:
   Russia total None, hard_stops [{'reason':'no_direct_war_score_for_covered_enemy','enemy':'Russia'}], row "(no terms can move them)"
   can_ratify False | ratify_blocked_reason ''  (BLANK) | Talleyrand: "...cannot be sealed as it stands: no single dominant pressure."
```

Probe 7 (feasibility): with `settlement_scoring.calculate_common_peace_acceptance`
patched (the stable test seam) to return accept for the offer's courts, the SAME
accept route stages `can_ratify True` + `confirm_settlement`, and the SAME
confirm route ratifies: `Settlement Ratified: France vs Austria + Britain +
Russia (6 pair(s) resolved)`, Britain/Austria/Russia -> PEACE, `war_1.ended_turn 20`,
`active_participants []`, dialogue manager empty, `settlement_result_feedback`
present. Everything downstream of the two scoring seams works for the
`caller_kind="ai_system"` REVIEW.

**Verdict: NARROWED.** The true shape:

1. The accept-staged review scores the OFFERING courts as the accepting side of
   a package France proposed. That part of the row is exact
   (`handle_incoming_settlement_offer_action` accept branch -> `stage_settlement_confirm(actor_nation=player, caller_kind="ai_system")`
   -> `build_settlement_preview` -> `evaluate_open_settlement_eligibility` infers `proposer_side=attackers`).
2. "No offering court reaches the 50 threshold" is FALSE. A bare peace carries
   at proposer-side pressure >= ~45 with WE at cap; the winning arm carries with a
   small indemnity (<= ~1,000g at +100, <= ~500g at +60); the losing arm reaches
   52 for a court with no agenda term at exactly the band edge. What is true is
   that EVERY AMBIENT state measured (boot t4, fixture t20, the row's own t15/t23/t24)
   is dead, and the REAL producer's package is dead at every pressure on this
   fixture: the purse-priced indemnity saturates harshness (winning arm) and
   `base_side_pressure` turns negative (losing arm).
3. The blocker is mis-attributed. `settlement_tier_legitimacy -10` is the top
   blocker only for the white peace inside the dead band; the winning arm dies
   on `term_harshness_penalty -45` (EWC-F1, already OPEN) and the losing arm on
   `base_side_pressure` -- the scorer's "why settle while winning" term
   (`settlement_third_party.py` names it "the victor's-consent arm") charged
   against the court that AUTHORED the offer. The agenda -8 is decisive only at
   the margin (the +40 / -20 / divergence arms all miss by <= 8 on it).
4. "The dead review is the offer's end" is true of THAT letter and false of the
   affordance: accept writes no cooldown, so the producer re-emits on the next
   AI phase with current terms (probe 4d).
5. Two verifiers landing on NARROWED "for opposite reasons" is consistent with
   this: one can read "universality false" as (2) above (states exist where the
   courts consent) and the other as (3) (the tier base is not the mechanism).
   Both hold; the row's mechanism sentence is wrong twice and its consequence
   sentence is right.

**Seam by symbol.**
- `backend/game_logic/settlement_offers.py::handle_incoming_settlement_offer_action`, accept branch:
  `_remove_pending_settlement_offer` (a no-op after promotion -- the store is drained by `promote_pending_settlement_offers`) + `world.dialogue_manager.pop()` (the consequential removal), THEN `stage_settlement_confirm(actor_nation=player, caller_kind="ai_system", settlement_terms=<offer terms>, covered_enemy_participants=<offer's FROZEN list>, selected_target_nation=<proposer if covered else covered[0]>)`.
- `backend/game_logic/settlement_staging.py::stage_settlement_confirm` -> `build_settlement_preview` -> `settlement_validation.evaluate_open_settlement_eligibility` (`_infer_actor_side` + `_side_leader != actor -> not_side_leader`) -> `settlement_scoring.calculate_common_peace_acceptance` (leader) + `settlement_baseline.compute_per_court_acceptance` (one scorer call per covered court, `accepting_leader=<court>`) -> `build_settlement_confirm_dialogue` (`can_ratify = not hard_stops and verdict ok and score>=threshold and (white_peace or per_court_carries)`; `ratify_blocked_reason` from `hard_stops[0].get("display"/"detail"/"code")` else the top blocker).
- `backend/game_logic/settlement_ratify.py::ratify_settlement_confirm`: `revalidate_staged_settlement` -> `validate_settlement_terms` -> the leader-level `fresh_acceptance = settlement_scoring.calculate_common_peace_acceptance(proposer_side=dialogue["proposer_side"], ...)` (runs for white peace too) -> the per-court `compute_per_court_acceptance` gate (skipped for white peace) -> `_build_pair_ratification_plan` / `_apply_settlement_terms` / `_resolve_pair_state_transitions` / `_record_common_peace_treaties`.
- Scorer terms that decide: `settlement_scoring.calculate_base_side_pressure` (0.65 x the power-weighted average of `select_direct_score` = MAX over proposer-side members at war with each court, clamp -50..60), `calculate_settlement_tier_legitimacy` (`TIER_LEGITIMACY_BASE` keyed on abs(side pressure); `_has_non_trivial_terms` is direction-blind), `calculate_term_harshness_penalty` (0.08/100g, -45 at 1,875g), `calculate_concession_credit` (amount//25 cap 40), `calculate_war_exhaustion_component` (WE//3 cap 20), `agendas.agenda_settlement_mod` (-8 ENTRENCH for Britain/Russia on every arm).
- Producer: `backend/game_logic/ai_diplomacy.py::_emit_settlement_offer_for_war` (zero scorer calls -- confirmed by reading the body; direction from `sum_stored_side_score(player, covered)` / `get_war_score_for`, i.e. FRANCE's stored scores, while the review reads the best ALLY's), `_settlement_offer_build_terms`, `_settlement_offer_eligible_for_war` (no cooldown is written by accept; cooldown only at emission).

**What the row's own `fix_shape` would break.**
1. "Stage the review with the OFFER's own `proposer_side`": measured
   `not_side_leader` (5a1). If the leader check were bypassed, `proposer_side=defenders`
   would make FRANCE the accepting leader and every direction-partitioned consumer
   would invert -- `compute_settlement_package_raw_harshness` would price a
   France-pays indemnity as a demand on France's OWN side, `calculate_concession_credit`
   would credit Britain's payment to Britain, `_apply_settlement_terms`/`_build_pair_ratification_plan`
   would resolve the wrong side's pairs, and `agenda_settlement_mod` would score the wrong court.
2. "Only pop/remove the offer after staging succeeds": measured (5a1) --
   with the offer still mounted, `stage_settlement_confirm`'s SC-26 same-war arm reads the
   offer as a draft and returns `settlement_scope_replace_confirm` (FA-N17/FA-N18's trap,
   filed against FA-4's identical reorder); `settlement_routes._settlement_dialogue_active`
   would also refuse `settlement_dialogue_active` unless `ignore_active_dialogue`.
3. "Ratify the offered package directly through `settlement_ratify` on the player's confirm"
   is FEASIBLE (probe 7) -- but a consent flag honoured only at STAGING is killed by
   `ratify_settlement_confirm`'s fresh leader re-score and leaves a lying re-attached
   button (5c); and a flag that skips the scorer ENTIRELY would also skip the hard stops,
   so a stale court (Russia at peace) would be "ratified" into a peace it already has
   (`_build_pair_ratification_plan` has no pair for it). Skipping the REVIEW (one-click
   ratify on accept) flips the sc5r2 pins listed below.
4. "Have `_emit_settlement_offer_for_war` pre-score its package (the EWC-F1 shape)":
   the scorer rejects the producer's own package in EVERY ambient state measured
   (white peace -2..18, AI-pays 11..45, France-pays 22..52 with two courts at 44),
   so pre-scoring would suppress nearly every offer -- the affordance goes from
   dead to absent. The scorer prices the ACCEPTER's reluctance; the accepter here
   is the author. Stepping the indemnity down until it scores (EWC-F1's proposed
   shape) would also step a purse-priced 3,770g down to ~500g at +60, gutting EC-W4.

**Minimal correct fix (not built).**
- Consent by construction, carried ON THE DIALOGUE (already serialized inside the
  manager; zero new WorldState fields): the accept branch stamps
  `consenting_courts = offer["covered_enemy_participants"]`, `consent_offer_id`,
  and a hash of the offered terms onto the staged `settlement_confirm`.
- Honour it at BOTH seams: (a) `build_settlement_preview`/`compute_per_court_acceptance`
  take `consenting_courts`; a consenting court WITH an active cross-side pair renders
  "consents -- their own terms" and counts as carrying regardless of its score
  (hard stops still apply); the leader-level `acceptance` is likewise treated as
  consenting when the leader is in the set. (b) `ratify_settlement_confirm` reads the
  same keys, verifies the staged terms hash still matches the offer (the ai_system
  REVIEW exposes no dials/cover actions, so the hash is a cheap invariant, not a
  guess), and skips the leader + per-court re-score for consenting courts while
  KEEPING `revalidate_staged_settlement`, `validate_settlement_terms`, the hard-stop
  path and the pair plan. Probe 7 shows everything below that line already works.
- Staleness, at accept AND at ratify: (i) a consenting court with no active pair
  against the proposer side has ALREADY made its peace -- drop it from `covered`
  and say so ("Russia has made her own peace; the offer now binds Austria and
  Britain"), refuse only when no consenting court remains; (ii) direction drift --
  stamp the producer's `accepter_war_score` on the offer at emission and let the
  offer LAPSE (voiced, no cooldown, so the producer re-emits next phase as it
  already does) when the live `sum_stored_side_score` has crossed a
  `SETTLEMENT_OFFER_DECISIVE_WAR_SCORE` band since emission; better still, retire
  such offers in the turn loop beside `promote_pending_settlement_offers` so the
  mailbox never shows a dead letter.
- Do NOT pre-score in the producer; do NOT touch `TIER_LEGITIMACY_BASE["white_peace"]`
  (it correctly prices the PLAYER's own white peace claimed at parity and is pinned).
- Pop the offer only after staging succeeds ONLY if the mounted-offer collision
  arms (FA-N17/FA-N18) land first; otherwise keep the pop-then-stage order and
  re-push the offer on staging failure.

**Existing tests that pin the current accept-path behaviour (none asserts `can_ratify` False on it):**
- `tests/test_settlement_incoming_offers.py::test_incoming_offer_accept_preserves_offer_id_and_settlement_terms_through_live_preview`
  -- `assert staged.get("settlement_terms") == offer["settlement_terms"]`, `assert world.pending_settlement_dialogues == []` (hold under the fix; the hash invariant reuses the first).
- `tests/test_settlement_incoming_offers.py::test_incoming_offer_accept_stages_settlement_confirm_for_correct_war_id_and_covered_scope`
  -- `assert staged_covered == sorted(offer["covered_enemy_participants"])` (would FLIP under the staleness rule when a court has left the war -- only in that geometry; the fixture's courts are all at war).
- `tests/test_settlement_sc5r1_backend_contract.py::test_accepting_incoming_ai_offer_stages_non_player_caller_without_editor_keys`
  -- patches `backend.game_logic.settlement_scoring.calculate_common_peace_acceptance` with `side_effect=_acceptance_accepts` and asserts `dialogue["caller_kind"] == "ai_system"` + no `can_edit_terms`/`available_clause_types`/`clause_control_schema`/`editor_route` (holds; the consent keys must not be editor keys).
- `tests/test_settlement_sc5r2_godot_editor.py::test_review_settlement_offer_label_replaces_accept_settlement` (`labels.get("accept_settlement_offer") == "Review Settlement Offer"`) and `::test_review_settlement_offer_description_promises_review_not_ratification` (`"review" in description`, must not promise one-click ratify) -- FLIP only if the fix ratifies directly on accept.
- `tests/test_settlement_sc5r2_godot_editor.py::test_request_revision_routes_to_guided_propose_seeded_from_offer` (patches the scorer on the revision path; untouched).
- Scorer pins that flip if anyone "fixes" the constant instead: `tests/test_common_peace_acceptance.py::test_settlement_tier_legitimacy_white_peace_zero_terms_only_base` (`assert result["score"] == -10`), `::test_settlement_tier_legitimacy_white_peace_with_term_exceeds`; the ratify-gate pins `tests/test_settlement_refront_slice1.py::test_ratify_requires_all_covered_courts_at_or_above_threshold_not_just_leader`, `::test_overall_carries_false_when_any_covered_court_hard_stopped_total_null`, `::test_holdout_court_offers_ease_or_drop_not_dead_end` (all player-authored dialogues -- no `consenting_courts` -- so they hold under the minimal fix).
- `already_filed` on the row is CORRECT for once: EWC-F1 (`docs/BUG_FIXES.md` ~5177, OPEN, the winning-arm harshness half) and CA8-3 (FIXED Aug 7 at the CA8-D2 close-out; its "-10 white peace" half is live, as measured).

## Cross-row findings

1. **The scorer's `direct_score` is the MAX over proposer-side members at war with each court, not France's own** (`settlement_scoring.compute_direct_scores_by_enemy` + `select_direct_score`, spec s6.3). On the t20 fixture France is at -54 vs Britain and the review reads -9 (Holland). The producer prices the SAME package off France's stored score (`sum_stored_side_score(player, covered)`), so producer and review disagree by construction: the divergence arm (France +5, allies +60) has the producer emit a bare peace that the review scores at pressure 60. Any consent design should key its drift check to the producer's number, not the review's.
2. **`_has_non_trivial_terms` is direction-blind** (`settlement_scoring.py`): a PROPOSER-PAID indemnity trips the white-peace "claims a victory" mismatch, so inside the dead band the player's own concession is charged -20 tier legitimacy (L60 France-only arm) while `compute_settlement_package_raw_harshness` correctly excludes it (G4F-1). A player who sweetens a parity peace with gold is punished for it. Worth its own row.
3. **A hard-stopped covered court yields a BLANK `ratify_blocked_reason`** and the Talleyrand line "no single dominant pressure" (`build_settlement_confirm_dialogue` reads `first_stop.get("display") or "detail" or "code"`, but the scorer's hard-stop dicts carry `reason`/`enemy`); the per-court row says "(no terms can move them)". Reachable on the ordinary player PROPOSE path whenever a covered court has left the war. Copy defect, own row.
4. **Nothing retires a standing offer when a covered court leaves the war** (census: no consumer of `pending_settlement_dialogues`/`incoming_settlement_offer` in `diplomacy.py`, `world_state.py`, `turn_manager.py`, `dialogue_manager.py` reacts to a pair resolving). The producer's NEXT offer is correct (covers only live courts); only the standing letter is stale. Same class for direction drift: the t20 fixture's letter is 17 turns old and offers a white peace while its author leads by 54.
5. **The accept writes no cooldown**, so the dead review is followed by a fresh offer on the next AI phase (t20 -> t21: France pays 6,994g), queued behind a minor's letter -- FA-17's starvation class, and the reason the player sees the "same" letter come back reworded.
6. **A `can_ratify` flag forced at staging survives a blocked ratify**: `_blocked_ratify_reattach` re-attaches the dialogue with `can_ratify True` / `ratify_blocked_reason ''` after `acceptance_rejected` (5c). Any dialogue-flag fix must be honoured at ratify or the Ratify button lies forever.
7. **`stage_settlement_confirm` runs the SC-26 collision arms BEFORE eligibility**, so a `proposer_side` mismatch on a mounted offer surfaces as `settlement_scope_replace_confirm`, not `not_side_leader` (5a1) -- the FA-N18 shape, confirmed from a second direction.
8. Harness traps: `/mailbox` rows key on `item_type` (not `type`); an accept sent while a letter is current is refused `stale_dialogue` (W6-0, correct); `cleanup_war_end(world, diplo_key, *, ...)` takes a KEY (calling it with two nations raises, and `quiet()` swallows the traceback); `set_diplomatic_state` alone does not touch the war instance -- only `cleanup_war_end` -> `resolve_pair_to_resolved` does.

## Probe inventory

- `repro/g2/g2_common.py` -- shared helpers (offer lookup, mailbox activation, accept + summarize, war-state report)
- `repro/g2/probe_1.py` -- ARM 1, shipped boot t4 (activate queued offer, accept)
- `repro/g2/probe_2.py` -- ARM 2, t20 fixture (stored scores, stale census, accept)
- `repro/g2/probe_3.py` -- winning/losing arms via the real producer (+/-60, +/-100, France-only vs whole-side) + bare-peace isolation arms
- `repro/g2/probe_4.py` -- design questions 5(a) proposer_side / not_side_leader / Britain's seat, 5(c) forced can_ratify at ratify, 5(d) the offer's fate after the dead review
- `repro/g2/probe_5.py` -- stale coverage via `set_diplomatic_state` alone + a census of who touches the offer store
- `repro/g2/probe_6.py` -- indemnity-amount boundary (500/1000/1875/3770g at +60/+100), the losing arm at -20/-25/-30/-40, the producer/scorer divergence arm, the boot-WE arm
- `repro/g2/probe_7.py` -- feasibility (scorer short-circuited -> real accept + confirm ratifies) + stale coverage through the real `cleanup_war_end` seam + the producer's next offer
