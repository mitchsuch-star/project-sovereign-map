# REPRO G1 -- "The offer on the desk" (the SC-26 settlement-collision family)

Rows: FA-4 (P1), FA-N17 (P2), FA-N18 (P2), FA-N15 (P2), FA-N4 staging half (P1).
Tree: master `a1ed5c9d`, read-only. Every measurement below drove the REAL
`POST /respond_to_diplomatic_dialogue` and `POST /command` routes (TestClient,
mock parser) on `tests/fixtures/playtest_saves/fixture_t20_ambient.json`
(Britain's `war_1` offer `settlement_offer:war_1:3:1`, dialogue_id 8, CURRENT;
`war_2` = Switzerland vs a France-led five-court side, created turn 20). The
second offer in every probe was authored by the REAL producer
(`ai_diplomacy._emit_settlement_offer_for_war`) and promoted through the REAL
`settlement_offers.promote_pending_settlement_offers` (it carries NO
`selected_target_nation`, exactly as the rows say).

## Summary

| Row | Verdict | Measured mechanism (one sentence) |
|---|---|---|
| FA-4 | REPRODUCED (and it is worse than filed) | The accept arm pops the offer, `pop()` promotes the queued `war_2` offer, `stage_settlement_confirm` reads that promoted item as `_mounted_settlement_dialogue` and refuses `cross_war_settlement_collision`; Britain's offer is destroyed, the reopen budget is burned, and the `must_reopen` the client obeys collides AGAIN (`message ""` on the /command route). |
| FA-N17 | REPRODUCED | FA-4's reorder as written leaves the offer mounted, the SAME-WAR arm reads the enemy's letter as our draft (`_dialogue_scope_values` picks `Austria` = sorted covered[0] vs incoming `Britain`), `_scope_changed` fires and the ordinary accept becomes the scope-replace chooser; its "smaller equivalent" (gate :3405 on type) is NOT equivalent -- it falls to the second gate and refuses `settlement_dialogue_active`. |
| FA-N18 | REPRODUCED | Opening Settlement on `war_1` over the standing offer (the war-detail button and the F1 wizard send the identical structured command) mounts the chooser with two identical scope strings, `replace()`s the offer away, "Keep" restores the ENEMY'S letter as "the current draft", and "Replace" lands a blocking REVIEW with EMPTY terms (the chooser drops `dialogue_mode`). |
| FA-N15 | REPRODUCED | Submit pops the PROPOSE, the promoted `war_1` offer trips the cross-war arm, `_enforce_settlement_response_shape` re-attaches the dead PROPOSE (id 24) while the head is the offer (id 8); every button on the re-mounted popup is refused `stale_dialogue`; the `return_to_settlement_terms` twin (reachable -- it IS on the REVIEW's options) collides identically. |
| FA-N4 (staging half) | REPRODUCED | Request Revision pops first exactly like accept; `cross_war_settlement_collision`, offer destroyed, `must_reopen` re-collides; the Sept-2 copy half holds (`message == error_display`, no success voice). |

The whole family is ONE defect: an `incoming_settlement_offer` is treated as a
mounted DRAFT by three readers that must agree and do not (the collision read,
the second gate, the staging tail), and four arms re-stage over the dialogue
they are answering by popping it first. The design simulation (probe 8,
in-process monkeypatch only) shows ONE rule closes all five rows with the
ordinary paths byte-stable and exactly ONE pin flipping consciously.

## Per row

### FA-4 -- REPRODUCED (understated in two places)

Probes: `probe_1_fa4_accept.py`, `probe_2_control_accept.py`, `probe_10_pop_after_stage.py`.

Evidence (probe 1, accept dialogue_id 8 with the producer-built `war_2` offer queued):
```
dm BEFORE: current ('incoming_settlement_offer', 8, 'war_1', ...:war_1:3:1)  queue [('incoming_settlement_offer', 23, 'war_2', ...:war_2:20:1)]
RESPONSE: success False, error cross_war_settlement_collision,
  message "Sire, the settlement of war_2 is already on the table; resolve it before opening a separate review for war_1."
  must_reopen True, reopen_target {war_id war_1, target_nation Britain, diagnostic_fallback_target True,
    error_display "This settlement lost its selected court. Reopen from war detail."}
dm AFTER: current ('incoming_settlement_offer', 23, 'war_2', ...)  queue []
Britain's offer still anywhere in manager? False      reopen_attempts: {'war_1': {20: 1}}
raw war ids in message? True
```
The client-side consequence, driven (probe 1, third block): `must_reopen` makes
`main.gd._on_war_settlement_clicked(war_1, Britain)` POST
`propose_common_peace war_1`, which now collides against the promoted `war_2`
offer -- `success False, error cross_war_settlement_collision, message ""`,
`talleyrand_text "Sire, the settlement of war_2 is already on the table..."`.
Control (probe 2, nothing queued): accept stages a REVIEW (`dialogue_id 23,
dialogue_mode REVIEW, caller_kind ai_system, blocking True, can_ratify False,
ratify_blocked_reason "Settlement legitimacy"`, options `seek_bilateral_peace /
seek_armistice_instead / open_war_detail / back_out_settlement`), head is the
returned dialogue, `pending_settlement_dialogues []`. A queued NON-settlement
item (an advisory) does not trip it: accept succeeds, advisory stays queued.

Seam (by symbol): `settlement_offers.handle_incoming_settlement_offer_action`
accept arm (`_remove_pending_settlement_offer` + `_is_offer_active_dialogue`
-> `world.dialogue_manager.pop()` BEFORE `stage_settlement_confirm`);
`DialogueManager.pop` -> `_promote` (mailbox_priority 2 beats everything
non-settlement); `settlement_staging.stage_settlement_confirm` reading
`settlement_routes._mounted_settlement_dialogue`, whose docstring says queued
items must not count -- and they do not: the pop MADE it current.

Understated: (1) the SC-14b reopen budget is burned by `_safe_reopen_response`
-> `record_reopen_attempt` on every failed click (`{'war_1': {20: 1}}`); (2) the
`reopen_target` is a `diagnostic_fallback_target` because a producer offer has
no `selected_target_nation`, and acting on it collides again with an EMPTY
`message` on the /command route (see cross-row 2).

What the filed fix breaks:
- "run `stage_settlement_confirm` first" on the shipped tree = FA-N17 (probe 3):
  the ordinary accept becomes `settlement_scope_replace_confirm`.
- "pop/remove only when staging succeeds" (probe 10): after a successful
  stage-first the branch's own guard `_is_offer_active_dialogue` reads False
  (the chooser/review is current), so the guarded pop is a no-op; an UNGUARDED
  pop removes the newly staged dialogue -- measured under the rule: `after an
  unguarded pop(): current ('incoming_settlement_offer', 8, 'war_1') ...` i.e.
  the REVIEW is gone and the NEXT offer promoted. Staging CONSUMES the offer
  via the tail's `replace`; the arm must never pop afterwards.
- "humanize the two `{war_label}` slots via `_war_label_for_id`":
  `_settlement_collision_payload` has no `world` parameter; it must be
  threaded (every caller has one).

Minimal correct fix: the ONE rule (end of report) plus this arm: stage FIRST;
on success `dialogue_manager.remove_matching(lambda d: d.get("dialogue_id") ==
offer_id)` + `_remove_pending_settlement_offer`; on failure return the offer
RE-ATTACHED as `diplomatic_dialogue` -- no `must_reopen`, no
`record_reopen_attempt`. The SC-7b defensive arms (empty/unknown/archived war)
may keep removing first: they are refusals by construction.

Pins that exercise this arm (all HOLD under the rule -- offer consumed on
success, review current):
- `tests/test_settlement_incoming_offers.py::test_incoming_offer_accept_preserves_offer_id_and_settlement_terms_through_live_preview` -- `staged = world.dialogue_manager._current ... assert staged.get("dialogue_type") == "settlement_confirm"`, `assert world.pending_settlement_dialogues == []`
- `...::test_incoming_offer_accept_stages_settlement_confirm_for_correct_war_id_and_covered_scope` -- `assert staged.get("selected_target_nation") == "Austria"`
- `...::test_promoted_offer_accept_resolves_and_stages_review_through_wire` -- `assert str(staged.get("dialogue_type") or staged.get("type")) == "settlement_confirm"`
- `tests/test_incoming_offer_deferral_no_leaks.py::test_incoming_offer_accept_through_active_mailbox_pops_offer_and_stages_confirm` -- `current = dm.peek(); assert current.get("type") == "settlement_confirm"` ("Offer is no longer in dialogue manager")
- `...::test_incoming_offer_accept_preserves_offer_identity_and_terms_through_live_preview` -- `assert staged["settlement_terms"] == offer["settlement_terms"]`
- `tests/test_settlement_ui_slice_f_behavior.py::test_handle_incoming_offer_accept_stages_settlement_confirm_after_sc5_reversal` -- `assert world.pending_settlement_dialogues == []` "Whatever the staging outcome". Probe 9: staging SUCCEEDS in that synthetic geometry, so removal-gated-on-success keeps it green; if the geometry ever fails, this is the pin that reds.
- `tests/test_settlement_sc5r1_backend_contract.py::...::test_accepting_incoming_ai_offer_stages_non_player_caller_without_editor_keys` -- `assert dialogue["caller_kind"] == "ai_system"`
- `tests/test_ai_intent_mediation.py::...::test_accept_opens_the_review_and_credits_the_mediator` -- `assert result.get("mediator") == "Russia"` (credit stays on the success branch)

### FA-N17 -- REPRODUCED; its "smaller equivalent" is refuted

Probe: `probe_3_fan17_reorder.py`.

Evidence (the accept arm's EXACT `stage_kwargs`, offer still mounted):
```
stage_kwargs: war_id war_1, actor_nation France, caller_kind ai_system, settlement_terms [{'type':'peace'}],
  covered_enemy_participants ['Britain','Austria','Russia'], selected_target_nation 'Britain'
offer's _dialogue_scope_values: ('Austria', ['Austria','Britain','Russia'])   _scope_changed(...)? True
RESULT: success True, dialogue_type settlement_scope_replace_confirm,
  message "Sire, France vs Britain already has a settlement draft for Austria, Britain, Russia. Shall I replace it with the new scope, Austria, Britain, Russia, or keep the current draft?"
chooser current_scope display 'Austria, Britain, Russia' | incoming 'Austria, Britain, Russia'   (selected: Austria vs Britain)
chooser current_dialogue is the OFFER (type)? incoming_settlement_offer      offer survives anywhere? False
```
Answering "Replace" on that chooser (FA-N17c) lands the REVIEW the accept
should have produced (`caller_kind ai_system`) one modal late; "Keep" would
restore the enemy's letter (see FA-N18).

The row's alternative ("Equivalent and smaller if finding 3 lands first: fixing
:3405 to require `mounted['type'] == 'settlement_confirm'`") is FALSE (probe 3,
FA-N17b): with the offer excluded from the same-war arm, `is_same_war_refresh`
stays False, `build_settlement_preview(ignore_active_dialogue=False)` runs
`evaluate_open_settlement_eligibility`, and `_settlement_dialogue_active`
(current + QUEUE, types `settlement_confirm` AND `incoming_settlement_offer`)
refuses:
```
_settlement_dialogue_active(world, war_1): True
preview success: False error: settlement_dialogue_active error_display: Resolve the current settlement review first.
preview (ignore_active_dialogue=True) success: True
```
So there are TWO gates, and the FA-N4 Sept-2 status is right that the second
must move with the first.

Seam: `settlement_staging.stage_settlement_confirm` same-war arm ->
`_scope_changed` / `_dialogue_scope_values` (a producer offer has no
`selected_target_nation`, so its "selected" is `sorted(covered)[0]`);
`settlement_routes._settlement_dialogue_active` via
`settlement_validation.evaluate_open_settlement_eligibility`.

What its own fix would break: a `for_war_id` / `ignore_mounted_offer`
parameter closes FA-4/FA-N4 but leaves FA-N18 standing (an offer NOT being
acted upon is still read as a draft) and leaves the second gate refusing the
FA-N18 open. Its pin ("with an offer for war X mounted, staging X in
`ai_system` mode returns a REVIEW") is the right pin and is satisfied by the
ONE rule (probe 8 SIM 2).

Pins: `tests/test_settlement_scope_replace_confirm.py::test_same_war_different_scope_restage_returns_scope_replace_confirm` (`assert chooser["type"] == "settlement_scope_replace_confirm"` for two DRAFTS) HOLDS under the rule (SIM 8); it does not pin an offer as the mounted side.

### FA-N18 -- REPRODUCED (wider: both chooser answers are wrong, and the availability surfaces lie)

Probes: `probe_4_fan18_open_settlement.py` (+ `probe_4.out`), `probe_11_availability.py` (+ `probe_11.out`), `probe_7_design.py`.

Evidence (a), `POST /command {"action":"propose_common_peace","target_nation":"Britain","war_id":"war_1"}` -- the structured command BOTH `main.gd._on_war_settlement_clicked` and
`diplomacy_wizard.gd._structured_payload_for_action("open_settlement")` send:
```
RESPONSE: success True, dialogue_type settlement_scope_replace_confirm, message "...already has a settlement draft for Austria, Britain, Russia. Shall I replace it with the new scope, Austria, Britain, Russia..."
chooser current_dialogue type: incoming_settlement_offer -- the ENEMY's offer read as our draft; its terms [{'type':'peace'}]
dm AFTER: current chooser 23, queue []     offer survives anywhere? False     mailbox items now: []
[keep_current_scope_draft]   -> head incoming_settlement_offer 8   (the enemy's letter restored as "the current draft")
[replace_current_scope_draft] -> head settlement_confirm 24, mode REVIEW, caller_kind player_editor, terms [],
                                ratify_blocked_reason "No settlement terms have been authored.", options author_gold_indemnity_terms/author_gold_per_turn_terms/seek_bilateral_peace/seek_armistice_instead/open_war_detail/back_out_settlement
```
(b) cross-war, open `war_2` over the standing `war_1` offer:
`success False, error cross_war_settlement_collision, message "", talleyrand_text "Sire, the settlement of war_1 is already on the table; resolve it before opening a separate review for war_2."` -- offer survives.
(c) control, the SAME open with the offer merely QUEUED (advisory current):
`success True`, PROPOSE `war_2` current, queue `[offer 8, advisory 23]` -- the
`preempt` tail already preserves mail when it is not current.
(probe 11) the two availability surfaces disagree today while the offer is current:
```
war_1 eligibility available: False error: settlement_dialogue_active display: Resolve the current settlement review first.   <- the F1 wizard row for Britain
war row war_1 ... "settlement_available": true                                                                            <- the war-detail row (war_status.py passes ignore_active_dialogue=True)
Switzerland wizard open_settlement available: true  (and the click then refuses, see (b))
```
So the war-detail button advertises an open it then turns into the chooser,
and the wizard refuses with a string naming "the current settlement review"
that is the enemy's letter.

Seam: `settlement_routes._mounted_settlement_dialogue` admits every
`SETTLEMENT_FAMILY_DIALOGUE_TYPES` member (`incoming_settlement_offer`
included) against its own docstring; `stage_settlement_confirm` same-war arm
(`existing_terms = mounted terms`, `_scope_changed`, then
`world.dialogue_manager.replace(replace_dialogue)` -- `DialogueManager.replace`
never re-queues a displaced mailbox item when the new type is not mail, probe
7(b)); `settlement_actions._apply_scope_replace_confirm` builds the replacement
with `build_settlement_confirm_dialogue(...)` and NO `dialogue_mode` (default
`REVIEW`, probe 9) because `incoming_request` never carries it.

What the filed fix breaks: gating :3405 on `mounted.get('type') ==
'settlement_confirm'` alone -> the second gate refuses
`settlement_dialogue_active` (measured, FA-N17b), so the row's own test
("assert the returned dialogue_type is settlement_confirm ... the offer is
still answerable") FAILS under the row's own fix. The row's "Do NOT narrow
`_mounted_settlement_dialogue` itself" keeps the cross-war arm treating a
letter as a review -- which is (b) above and the empty red line the player
sees for it.

Minimal correct fix: the ONE rule -- the offer is never a draft in any of the
three readers; the tail PREEMPTS it (re-queued to the mailbox, as (c) already
does). Under the rule (probe 8 SIM 5/5b): `war_1` open -> PROPOSE current,
`mailbox: [('incoming_settlement_offer','WAITING'), ...]`; `war_2` open ->
PROPOSE `war_2` current, offer WAITING. Plus cross-row 1 (carry
`dialogue_mode` through the chooser) since the two-draft chooser stays reachable.

Pins that FLIP (consciously): `tests/test_settlement_continuity_slice.py::test_collision_protection_treats_incoming_offer_as_settlement_family` -- `assert result["error"] == "cross_war_settlement_collision"`, `assert result["active_dialogue_type"] == "incoming_settlement_offer"` (its docstring is the SC-26 "family scope" decision this rule retires). If the family set itself is narrowed instead of adding a draft-type set, two more flip: `tests/test_settlement_continuity_slice.py::test_settlement_family_dialogue_types_match_canonical_set` and `tests/test_incoming_offer_deferral_no_leaks.py::test_settlement_family_set_keeps_offer_for_defensive_guards` (both `assert SETTLEMENT_FAMILY_DIALOGUE_TYPES == frozenset({... "incoming_settlement_offer" ...})`). Pins that HOLD: `test_cross_war_settlement_collision_returns_humanized_rejection` (two drafts, SIM 7), the scope-replace file (SIM 8).

### FA-N15 -- REPRODUCED (the return twin IS reachable and collides too)

Probes: `probe_5_fan15_submit.py` (+ `probe_5.out`), `probe_12_stagefirst_unpatched.py`.

Evidence (advisory current, Britain's offer queued, PROPOSE `war_2` mounted via `preempt`, then `submit_settlement_for_review` with dialogue_id 24):
```
dm after open: current ('settlement_confirm', 24, 'war_2')  queue [('incoming_settlement_offer', 8, 'war_1'), ('advisory', 23)]
is_hard_stop (PROPOSE): False
submit RESPONSE: success False, error cross_war_settlement_collision, message "Sire, the settlement of war_1 is already on the table; resolve it before opening a separate review for war_2."
  diplomatic_dialogue: type settlement_confirm, dialogue_id 24, mode PROPOSE, caller_kind player_editor   <- re-attached by _enforce_settlement_response_shape
dm AFTER submit: current ('incoming_settlement_offer', 8, 'war_1')  queue [('advisory', 23)]
re-attached id 24 | manager head id 8      same object/id? False      PROPOSE (id 24) still anywhere in manager? False
scoped drafts: ['settlement_draft:war_2:Switzerland:a4aa1a2d9139be4d']       <- the draft survives ONLY in the scoped store
second answers with id 24 (submit / suspend / back_out) -> success False, stale_dialogue True,
  "Sire, another matter has arrived since -- this concerns Britain. Your earlier answer was not delivered..." + diplomatic_dialogue = the OFFER (id 8)
```
(b) the twin: a REVIEW for `war_2` (staged directly, `caller_kind
player_editor`) DOES carry `return_to_settlement_terms` on its options
(`['return_to_settlement_terms', 'seek_bilateral_peace', ...]`), so the row's
"I could not reach" is a harness limit, not a fact; the arm pops, the offer
promotes, `cross_war_settlement_collision`, re-attached REVIEW 24 vs head 8.
(c) control, nothing queued: submit -> REVIEW 24 current, queue [].

Client consequence, read from `main.gd`: `_route_proposal_confirm_response`
re-mounts the ghost PROPOSE with `transient_error_display` = "Resolve the
active settlement review before opening another war's settlement."; every
button sends dialogue_id 24, the W6-0 guard answers `stale_dialogue` with the
OFFER re-attached, and the `incoming_settlement_offer` route then shows
Britain's offer -- a one-click-deep wedge, and the war_2 draft is recoverable
only by reopening Settlement on war_2 (the scoped store restore in
`_execute_propose_common_peace`). `stale_dialogue` has NO client handler
(zero hits under `godot-client/`); the client recovers only because the
re-attached dialogue is routed.

Seam: `settlement_actions._action_submit_settlement_for_review` (`pop()` then
`stage_settlement_confirm(dialogue_mode="REVIEW")`) and
`_action_return_to_settlement_terms` (same shape, PROPOSE); the pop promotes
the mail; `_enforce_settlement_response_shape` re-attaches the dict it was
handed, which the manager no longer holds.

What the filed fix breaks: "stage the REVIEW first and pop the PROPOSE only
when staging succeeds" -- stage-first ALONE is complete on the shipped tree
(probe 12, nothing patched): the mounted dialogue IS the one being answered,
so the same-war same-scope refresh runs and the LEGB-F2 tail `replace`s it
(`UNPATCHED stage-first submit: True ... mode REVIEW | PROPOSE 24 gone? True`;
return -> `mode PROPOSE`). A pop after that success removes the NEW dialogue
(`a pop() now would remove: settlement_confirm PROPOSE`). So: stage first,
never pop. (And under the ONE rule even the shipped pop-first submit stops
colliding -- probe 8 SIM 6 -- because the promoted mail no longer counts; the
reorder is owed for the FAILURE path, where a staging refusal after the pop
strands the player exactly as measured.)

Pins that exercise these arms (expected to HOLD under stage-first; read before building):
- `tests/test_settlement_sc5r2_godot_editor.py::TestBackendDraftRoundTrip::test_submit_for_review_from_guided_propose_lands_review_without_editor_mount` -- `assert review.get("dialogue_mode") == "REVIEW"`, `assert 275 in amounts`
- `tests/test_settlement_gate4_leg1_fixes.py::TestGate4SmokeSameWarRestageNeverStacks::test_back_out_after_same_war_refresh_discards_for_real` -- `assert "settlement_confirm" not in queued_types` after a same-war refresh; `assert world.pending_diplomatic_dialogue is None` after back out (the LEGB-F2 pin that FORBIDS re-queueing a same-war DRAFT -- the tail's replace arm must stay for drafts)
- `tests/test_settlement_carry_guidance_ux.py::test_return_to_terms_restages_propose_preserving_draft`, `tests/test_settlement_refront_slice3.py::test_submit_revalidation_enforces_uncovered_court_defense_in_depth`, `tests/test_settlement_gate4_preflight_pf1.py::...::test_generated_baseline_is_validated_before_staging_propose_and_submit` -- exercise submit/return; not read line by line here.

### FA-N4 (staging half) -- REPRODUCED; copy half confirmed fixed

Probe: `probe_6_fan4_revision.py`.

Evidence (`request_settlement_revision`, dialogue_id 8, `war_2` offer queued):
```
RESPONSE: success False, error cross_war_settlement_collision,
  message "Resolve the active settlement review before opening another war's settlement."   (== error_display; success voice leaked? False)
  must_reopen True, reopen_target {war_1, Britain, diagnostic_fallback_target True}
dm AFTER: current ('incoming_settlement_offer', 23, 'war_2')  queue []     Britain's offer survives anywhere? False
must_reopen chain (propose_common_peace war_1) -> success False, cross_war_settlement_collision (active war_2), message ""
```
Naive stage-first on this arm (PROPOSE, `player_editor`) -> the chooser again
(probe 6 third block) -- the FA-N17 shape on the revision arm.

Seam: the `request_settlement_revision` branch of
`handle_incoming_settlement_offer_action` ("Remove the offer first so the
mailbox no longer renders it" -> `_remove_pending_settlement_offer` +
`pop()`), then `stage_settlement_confirm(caller_kind="player_editor",
dialogue_mode="PROPOSE")`; identical to the accept arm 190 lines later.

The Sept-2 corrected three-seam design is right about the hazards and about
`submit_settlement_for_review` / `return_to_settlement_terms` being owed
(measured: after a rule-fixed revision the shipped submit works -- probe 8
SIM 4 -- but its FAILURE path still pops). Its "(1) opt-in
`consuming_offer_id`" is a parameter the ONE rule makes unnecessary: with the
offer never a draft, the tail preempts it and the arm removes it by
`dialogue_id` on success (probe 8 SIM 4: PROPOSE current, offer gone, `war_2`
offer + petition queued).

Pins that exercise this arm (HOLD under the rule): `tests/test_settlement_incoming_offers.py::test_incoming_offer_request_revision_opens_counter_editor_seeded_from_offered_terms` (`assert len(world.pending_settlement_dialogues) == 0`, `assert current.get("type") == "settlement_confirm"`); `tests/test_settlement_continuity_slice.py::test_request_revision_routes_to_guided_propose_counter_surface` (`assert current.get("dialogue_mode") == "PROPOSE"`, `"counter draft" in ... talleyrand_text` -- note its fixture offer CARRIES `selected_target_nation`, which is why it never tripped FA-N17); `tests/test_settlement_sc5r2_godot_editor.py::TestIncomingOfferLabelsMatchBehavior::test_request_revision_routes_to_guided_propose_seeded_from_offer` (`assert staged.get("dialogue_mode") == "PROPOSE"`); `tests/test_settlement_ui_slice_f_behavior.py::test_handle_incoming_offer_revise_opens_counter_editor_after_sc5_reversal_commit2` (`assert result["counter_to_offer_id"] == "offer_x"`); `tests/test_settlement_agency_cuts_g2c_g2f.py::test_request_revision_remains_only_counter_flow_for_incoming_offers`; `tests/test_incoming_offer_deferral_no_leaks.py::test_incoming_offer_blocked_recovery_uses_request_revision_counteroffer_framing` (`assert current.get("type") == "settlement_confirm"`). Text pin to KEEP satisfied: `tests/test_fa_n_p1_cluster_2026_09_02.py::TestFAN4TheRefusalSpeaksAsARefusal::test_a_failed_revision_does_not_report_a_counter_draft` -- `assert 'if result.get("success"):' in branch` and `assert 'result["message"] = result.get("error_display")' in branch` (a source-text pin on the revision branch; the reorder must leave both literals in place or update the pin).

## Design questions (7), answered from code + measurement

(a) Yes. `DialogueManager.remove_matching(predicate)` filters the queue AND the
current slot (auto-promoting only when the current was removed). Probe 7(a):
removing the queued `war_2` offer by `dialogue_id` -> `removed 1`, current
untouched; removing the CURRENT offer by `offer_id` -> `removed 1` and the
advisory promoted. So an arm that has already replaced/preempted the offer can
delete it wherever it sits without disturbing the head.

(b) At the tail, when the current is an `incoming_settlement_offer` for the
SAME war, `replace` DROPS it: `DialogueManager.replace` re-queues nothing and
carries mailbox metadata only when BOTH old and new are mail types (probe 7(b):
`Britain's offer re-queued? False`; `mailbox_id in review: False`). `preempt`
re-queues it (`offer re-queued: True`). Nothing else re-queues.

(c) `main.gd`: dialogue-popup answers are sent with `send_dialogue_response(...,
_on_command_result, dialogue_id)`, so `/respond_to_diplomatic_dialogue`
responses run the SAME handler as `/command`. In `_on_command_result` the
`_post_hud_response_routes` table runs first and RETURNS on a match: a
response carrying `diplomatic_dialogue` is routed -- `incoming_settlement_offer`
type -> `_route_incoming_settlement_offer_response` (offer popup);
anything else -> `_route_proposal_confirm_response`, which on `success == false`
re-mounts the dialogue with `transient_error_display` = `error_display` or
`message`. Only when NO route matched does it reach `must_reopen` (line ~2631):
it prints "Reopening settlement review for <nation>..." and calls
`_on_war_settlement_clicked(war_id, nation)` -> POST `propose_common_peace`
(structured) -> `_on_command_result` again; an empty target prints "Settlement
review needs to reopen, but the backend did not provide a valid target."
`stale_dialogue` is NOT read anywhere in the client; the endpoint copies it
into the response, and the client recovers only because the CURRENT dialogue
rides `diplomatic_dialogue` and is routed. A failed `/command` with no
dialogue prints `str(response.get("message", "An error occurred"))` in red --
which for every `stage_settlement_confirm` refusal is `""` (cross-row 2).

(d) `caller_kind="ai_system"` (probe 7(d)): the staged REVIEW is a blocking
HARD_STOP (`is_hard_stop True`) with options `seek_bilateral_peace /
seek_armistice_instead / open_war_detail / back_out_settlement` -- no
`return_to_settlement_terms` (the `player_editor` staging adds it), no editor
keys (`can_edit_terms` absent), no Revise route; and
`_enforce_settlement_response_shape` does NOT re-attach an `ai_system`
dialogue on a failed action (`SETTLEMENT_EDITOR_CALLER_KIND == "player_editor"`),
so a refused action on the accepted-offer review reaches the client with no
`diplomatic_dialogue` and falls to the red terminal line.

## The ONE rule (proposed, not built)

**An incoming settlement offer is mail, never a draft.** For SC-26, a "mounted
draft" is the CURRENT dialogue of an AUTHORING type -- `settlement_confirm`,
`settlement_scope_replace_confirm`, `settlement_pair_substitute_confirm` --
and never `incoming_settlement_offer`. Exactly three readers consult that
predicate and they must agree: (1) `_mounted_settlement_dialogue` (the
cross-war collision and the same-war refresh/chooser), (2)
`_settlement_dialogue_active` (the second gate inside
`evaluate_open_settlement_eligibility`, current + queue), (3) the staging
tail's replace-vs-preempt choice (`replace` a same-war DRAFT -- the LEGB-F2
contract -- and `preempt` everything else, so mail is re-queued). Keep
`SETTLEMENT_FAMILY_DIALOGUE_TYPES` as the family label and add
`SETTLEMENT_DRAFT_DIALOGUE_TYPES = family - {incoming_settlement_offer}` for
those three readers (then only one pin flips).

Then every arm that re-stages over the dialogue it is answering stages FIRST
and never pops:
- accept / request_revision: `stage_settlement_confirm(...)`; on SUCCESS
  `remove_matching(dialogue_id == offer's)` (the tail preempted it into the
  queue) + `_remove_pending_settlement_offer`; on FAILURE the offer is
  untouched and current -- re-attach it as `diplomatic_dialogue`, drop
  `must_reopen`, do not `record_reopen_attempt`. The SC-7b defensive arms keep
  their remove-first.
- submit_settlement_for_review / return_to_settlement_terms: drop the `pop()`;
  the same-war same-scope refresh + the tail's `replace` already consume the
  mounted twin (probe 12); on failure the mounted dialogue and the re-attached
  one are the same object.
- The chooser's `_apply_scope_replace_confirm` must carry `dialogue_mode`
  (cross-row 1) because the two-draft chooser remains reachable.

Measured consequences (probe 8, all three readers patched in-process):
- FA-4 geometry -> REVIEW current, `war_2` offer WAITING (SIM 1); even the
  shipped pop-first accept succeeds under the rule (SIM 1b) -- the reorder is
  for the failure path (SIM 3: `selected_target_not_covered` leaves the offer
  current). Pin the failure path on a real refusal, not on the collision.
- ordinary accept, nothing queued: byte-identical (SIM 2). ordinary revision:
  PROPOSE current, offer gone, petition queued (SIM 4), and the following
  submit works.
- FA-N18: same-war open -> PROPOSE over the offer, offer WAITING in the
  mailbox (SIM 5); cross-war open -> PROPOSE `war_2`, offer WAITING (SIM 5b).
  The wizard row for Britain flips from "Resolve the current settlement
  review first." to available and now agrees with the war-detail row.
- FA-N15: shipped pop-first submit works (SIM 6); stage-first submit/return
  work (SIM 6b, and unpatched in probe 12).
- Regression guards: the two-DRAFT cross-war collision still fires (SIM 7);
  the two-DRAFT same-war chooser still fires (SIM 8); LEGB-F2's "never stack a
  same-war draft" holds (replace kept for drafts).
- Behaviour that changes on purpose: a standing letter for war_1 no longer
  blocks opening Settlement on war_2, nor the pair-substitute CTAs /
  war-detail actionability for another war (`settlement_validation:427`,
  `settlement_routes:215` read the same predicate). The SC-5 "cross-war family
  guards keep catching it" comment in `dialogue_manager.py` and the one
  flipping pin record the retired decision.

## Cross-row findings

1. **The scope-replace chooser drops `dialogue_mode`.** `stage_settlement_confirm`'s `incoming_request` never carries it and `_apply_scope_replace_confirm` calls `build_settlement_confirm_dialogue` without it (default `REVIEW`, probe 9). A PROPOSE-opened flow that answers "Replace" lands a blocking REVIEW hard stop -- measured with EMPTY terms, `ratify_blocked_reason "No settlement terms have been authored."`, and no Return-to-terms option (probe 4 a2). Pre-existing; reachable today for two real drafts.
2. **Every `stage_settlement_confirm` refusal reaching `/command` prints an empty red line.** `_settlement_collision_payload` / `_blocked_payload` carry no `message`; `_build_result_response` derives `message ""` (probe 9: `message repr ''`, reason only in `error_display` / `talleyrand_text`); `main.gd._on_command_result`'s failure branch prints `response.message` only. The war-detail "Open Settlement" button and the F1 wizard (both hand off to `_on_command_result`) therefore refuse silently.
3. **The two availability surfaces disagree** (probe 11): `war_status.py` evaluates with `ignore_active_dialogue=True` (`settlement_available: true` for war_1 while the offer stands) while `diplomacy.get_available_diplomatic_actions` evaluates without it (`open_settlement` unavailable, "Resolve the current settlement review first.") -- and neither click does what its row advertises.
4. **`_safe_reopen_response` on the offer arms burns the SC-14b reopen budget** (`record_reopen_attempt`, measured `{'war_1': {20: 1}}` per failed click) and emits a `diagnostic_fallback_target` because producer offers carry no `selected_target_nation`; the client acts on it by POSTing `propose_common_peace`, which under the shipped tree collides again and under the rule would mount a PROPOSE the player did not ask for. The offer arms should re-attach the offer, not reopen.
5. **`stale_dialogue` has no client handler** (zero hits under `godot-client/`); the wedge in FA-N15 is one click deep only because the re-attached current dialogue is routed to its popup. Any producer that answers `stale_dialogue` WITHOUT re-attaching a dialogue would soft-lock the client.
6. **Raw war ids:** `_settlement_collision_payload` formats `settlement_collision_active_review_talleyrand` with the raw ids because it has no `world`; the fix needs `world` threaded to `_war_label_for_id` (all callers have it). On the dialogue route the raw-id sentence is the `message`; on the /command route it is `talleyrand_text` (unprinted, finding 2).
7. **`_scope_display` hides the selected court when it is inside the coverage**, so ANY same-war chooser whose only difference is the selected target renders two identical strings -- the "identical string" of FA-N18 is a general display weakness, not only the offer case.
8. **Row corrections:** FA-N15's "I could not reach `return_to_settlement_terms`" -- it IS on the options of a `player_editor` REVIEW and collides identically (probe 5b). FA-4's `already_filed: none` -- FA-N4 is the same seam one arm over, and FA-3's body carries the same pop-before-stage sentence. FA-N17's "equivalent and smaller" alternative is refuted (second gate).
9. **Harness note:** `_emit_settlement_offer_for_war` writes into the `pending` list and `cooldowns` dict it is HANDED, not into the world; to route a synthetic offer through the real promotion you must assign the list back to `world.pending_settlement_dialogues` before `promote_pending_settlement_offers` (see `g1_common.queue_second_offer`). The chooser is in no taxonomy set (`is_hard_stop False`), so `active_blocker_type` names it for the mailbox but typed commands pass through it (PC15-3's class) -- not measured further.

## Probe inventory

All under `<scratchpad>\repro\g1\`:
- `g1_common.py` -- shared helpers (real-producer second offer + promotion, endpoint answer, response summariser)
- `probe_0_recon.py` -- fixture geometry (dm, offer keys, war_instances)
- `probe_1_fa4_accept.py` -- FA-4 accept with a queued war_2 offer; advisory-queued variant; the client's must_reopen chain
- `probe_2_control_accept.py` -- ordinary accept and ordinary revision, nothing queued
- `probe_3_fan17_reorder.py` -- FA-4's reorder with the offer mounted; the second gate; answering the chooser
- `probe_4_fan18_open_settlement.py` (+ `probe_4.out`) -- open Settlement same-war / cross-war / offer-queued control; both chooser answers
- `probe_5_fan15_submit.py` (+ `probe_5.out`) -- submit and return with an offer queued; stale second answers; control
- `probe_6_fan4_revision.py` -- request revision with a queued offer; must_reopen chain; naive reorder
- `probe_7_design.py` -- remove_matching, replace vs preempt at the tail, caller_kind ai_system vs player_editor, taxonomy reads
- `probe_8_design_sim.py` (+ `probe_8.out`) -- the ONE rule simulated by in-process monkeypatch across all five geometries + two regression guards
- `probe_9_pin_geometry.py` -- staging succeeds in the slice-F synthetic accept pin; chooser default dialogue_mode; /command message derivation
- `probe_10_pop_after_stage.py` -- "pop only when staging succeeds" pops the new dialogue
- `probe_11_availability.py` (+ `probe_11.out`) -- war-detail vs wizard availability while the offer is current
- `probe_12_stagefirst_unpatched.py` -- stage-first submit/return on the shipped tree
