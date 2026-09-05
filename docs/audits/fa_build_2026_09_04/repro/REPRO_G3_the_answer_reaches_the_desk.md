# REPRO G3 -- "the answer reaches the desk" (FA-17 + FA-N44)

Tree: master `a1ed5c9d`, read-only. Harness: `probe_env` (mock parser, sandboxed saves,
all three seams swapped). Every probe line is prefixed `G3|`; raw outputs are quoted below.

## Summary

- **FA-17 -- NARROWED (a second time).** The counter to France's own overture IS starved
  behind Britain's persistent settlement offer, gets no popup and no player cooldown, and
  lapses next end turn -- but (a) it is NOT unseen: its full text rides the end-turn
  `tactical_events` (printed in the terminal), it is a WAITING row in the letter-book
  (activatable and answerable from there -- accept signs the peace), the badge counts it,
  the end-turn lapse warning counts it, and the next dispatch names it under
  `lapsed_offers`; (b) the persistent offer is NOT the mechanism: `_process_ai_diplomatic_phase`
  (turn_manager ~:259) delivers the turn's letters BEFORE `advance_turn` (~:292) resolves
  the in-transit proposal, so the counter is always `push()`ed behind whatever mail arrived
  that turn -- the control arm with the offer REJECTED starved identically behind a Hesse
  letter and Britain's immediately re-sent offer; (c) even a counter that later becomes
  current gets no popup on any response (the `incoming_proposal` safety valve's type tuple
  excludes `counter_offer_response`); only `/pending_envoy` exposes it. What survives of the
  row: no popup with Accept/Reject buttons, no player-side cooldown on lapse (the 3-DP
  treadmill is real and measured), and a contentless dispatch line shared by every outcome.
- **FA-N44 -- NARROWED.** The misroute in the title is CLOSED by the FA-N5 gate: the paradox
  popup is written unconditionally at declaration but now carries `dialogue_id`, `status`
  WITHHOLDS it while a letter is current, and it is delivered on the very response that
  promotes the paradox. What survives: `declare_war` `push()`es a priority-0 HARD_STOP behind
  a SOFT-STOP mailbox current and nothing ever preempts, so behind a persistent settlement
  offer the crisis is invisible (no key on any response, not a mailbox row) for
  `BLOCKING_TIMEOUT_TURNS` and is then DESTROYED by `clear_stale`'s queue sweep with no
  event; the zombie popup is reaped silently on the next drain; France stays allied to both
  belligerents with no choice ever made. The row's fix (write the slot only when current) is
  a no-op for the misroute and a REGRESSION for delivery.

## Per row

### FA-17

**What I ran.** `probe_1_fa17_counter_behind_offer.py` (boot, turn 4), `probe_2_fa17_arms.py`
(boot, three arms), `probe_4_fa17_fixture_t20.py` (t20 fixture, natural/force/control),
`probe_5_fa17_forced_counter_t20.py` (t20, forced COUNTER, force/control),
`probe_6_fa17_promotion.py` (does a promoted counter ever reach the client),
`probe_7_fa17_wire_shape.py` (which key carries the counter text; popup-button keywords).

**The row's repro line cannot be followed on the shipped board.** `propose peace with
Austria` is refused at turn 4 (boot), turn 10 and turn 20 (both committed fixtures) by the
BPH-C paradox guard `diplomacy.get_peace_commitment_conflicts` (diplomatic_executor,
`proposal_type == "peace"` arm): Bavaria, France's ally, is still at war with Austria:

```
G3| [confirm] answered proposal_confirm#9 with 'execute_proposal' -> success=False
    msg='Making peace with Austria while allied with Bavaria (who is still at war with Austria)
         creates a diplomatic contradiction.'
G3| peace-guard blockers per target: {'Britain': ['Spain'], 'Russia': [], 'Austria': ['Bavaria']}   (t10)
G3| peace-guard blockers per target: {'Britain': [], 'Russia': [], 'Austria': ['Bavaria'], ...}     (t20)
```
Russia is the only coalition court the guard lets through on both fixtures, so the overture
goes to Russia; the row's mechanism is target-agnostic. At t20 Russia ACCEPTS (score 84) on
both the natural and the "force" arm (the forced counter generator is never consulted when
the outcome is ACCEPT), so the viable-counter arm was reached by patching the three call-time
imports `_process_proposal_in_transit` makes: `diplomacy.calculate_acceptance` -> 40 /
COUNTER_OFFER, `ai_diplomacy.ai_should_accept_liberation_peace` -> True,
`ai_diplomacy.generate_counter_offer` -> the proposal + a 1000g sweetener.

**Row geometry (Britain's `settlement_offer:war_1:3:1` CURRENT, probe_5 force):**
```
G3| [confirm] ... msg='Talleyrand departs for the Russia court with your Peace Treaty proposal.
    Expect a response by next turn. (3 DP spent)'
G3| DP 5 -> 2 | in transit: {'target': 'Russia', 'turn_sent': 20, 'acceptance_snapshot': 40}
G3| == END TURN (answer returns) -> turn 21 == DP 5
G3| diplomatic_proposal_returned on the end-turn response: [('COUNTER_OFFER', 'Talleyrand returns
    from Russia with a counter-proposal. They could not accept our terms, but offer an alternative:
    / Peace Treaty between France and Russia /   - France offers infantry manpower (5174) / ...')]
G3| popups delivered on end-turn response: {} | deferred_dialogue: None | pending_lapsing_count: 2
G3| dm: {'current': ('incoming_settlement_offer', 8, ...), 'queue': [('incoming_proposal', 24, ..),
    ('counter_offer_response', 25, ..)]}
G3| counter dialogue: {'dialogue_id': 25, 'mailbox_id': 23, 'mailbox_priority': 3, 'turn_created': 21,
    'blocking': True} | is CURRENT: False
G3| proposal_result_popup: None
G3| incoming_proposal_popup: None
G3| popup queue slots: {}
G3| player_proposal_cooldowns: {} | ai cooldowns Russia {'Russia|armistice': 1} | nation_dp Russia: 4
G3| /mailbox items: [('incoming_settlement_offer','ACTIVE','Britain',8,..), ('incoming_proposal',
    'WAITING','Hesse',22,..), ('counter_offer_response','WAITING','Russia',23,'Russia ? Peace Treaty')]
G3| /pending_envoy: {'has_pending': True, 'dialogue_type': 'incoming_settlement_offer',
    'pending_envoy_count': 3, 'pending_lapsing_count': 2}
G3| dispatch near 'Talleyrand returns': ... "text": "Talleyrand returns from Russia with a response."
G3| popups delivered on `status`: {} | diplomatic_dialogue on status: None
G3| /mailbox/activate counter -> {'success': True, 'activation_blocked': None,
    'dialogue_type': 'counter_offer_response'} | popups: {'incoming_proposal': 'dict'}
    | incoming_proposal.is_counter_offer: True
G3| [(copy) accept counter] ... -> success=True msg="You have accepted Russia's counter-proposal.
    Treaty signed: WAR ? PEACE with Russia."
G3| == END TURN #2 -> turn 22 == DP 5
G3| offer_lapsed (turn>=20): [('Hesse','incoming_proposal','opportunistic',21),
    ('Russia','counter_offer_response','peace',21)]
G3| player_proposal_cooldowns: {} | ai cooldowns Russia {'Russia|nation': 1, 'Russia|peace': 5}
G3| dispatch #2 near 'Russia': ... "lapsed_offers": [{"nation": "Hesse", ...}, {"nation": "Russia",
    "proposal_type": "peace"}] ...
G3| repeat overture -> success True ... | DP 5
G3| [confirm #2] ... msg='Talleyrand departs for the Russia court ... (3 DP spent)'
G3| DP after second send: 2 | in transit: True
```
Where the counter text travels (probe_7 force): it rides BOTH `events` and
`tactical_events` of the end-turn response (`proposal_returned here: 1` in each);
`main.gd` `_display_result` prints only `events[0]` (the turn change) but the
`tactical_events` loop right after it (main.gd ~2664-2672) prints EVERY message, so the
counter's full text reaches the terminal transcript on the end-turn response.

**Control (offer REJECTED first, then the same forced counter, probe_5 control):**
```
G3| dm after rejecting the offer: {'current': None, 'queue': []}
G3| == END TURN (answer returns) -> turn 21 == DP 5
G3| dm: {'current': ('incoming_proposal', 24, ..), 'queue': [('incoming_settlement_offer', 25,
    'war_1', 'settlement_offer:war_1:20:1'), ('counter_offer_response', 26, ..)]}
G3| counter dialogue: {... 'mailbox_priority': 3 ...} | is CURRENT: False
G3| incoming_proposal_popup: {'proposal_type': 'non_aggression', 'dialogue_id': '24', ...}   (Hesse's)
G3| popups delivered on `status`: {'incoming_proposal': 'dict'}   (Hesse's letter, not the counter)
```
Same starvation with NO persistent offer in the slot: the dialogue ids are monotonic
(24 < 25 < 26), so the counter was pushed LAST -- `_process_ai_diplomatic_phase`
(turn_manager ~:259) delivers the turn's mail before `advance_turn` (~:292) calls
`_process_proposal_in_transit` (world_state ~:9505). Britain also re-sent a settlement offer
(`:20:1`) on the very turn its `:3:1` offer was rejected, so the "persistent" slot refills
immediately.

**Promotion (probe_6):** answer Hesse -> Britain's fresh offer is promoted (priority 2 < 3);
reject it -> the counter is promoted:
```
G3| [reject Britain's fresh offer] ... popups on that response: {} | diplomatic_dialogue on response: None#None
G3| counter is CURRENT now? True | incoming_proposal_popup on world: False | popup queue: {}
G3| status -> popups: {} | diplomatic_dialogue on status: None | pending_lapsing_count: 1
G3| /pending_envoy: {'has_pending': True, 'dialogue_type': 'counter_offer_response', ...}
    | incoming_proposal.is_counter_offer: True
G3| [answer counter with index 2 ...] -> success=True msg="You have rejected Russia's
    counter-proposal. Relations cooled slightly." ... cooldowns: {'Russia': 3, 'Russia_peace': 5}
```
A current counter is never re-derived into a popup: the IGR-F conditional write fires only at
push time, and the `incoming_proposal` safety valve in `main._include_popup_passthroughs`
re-derives only `("incoming_proposal", "incoming_ultimatum")`. Only the envoy button
(`GET /pending_envoy`) shows it.

**The four outcome arms (parity, read at `world_state._process_proposal_in_transit`):**

| arm | player_proposal_cooldowns | AI-side cooldown | record_diplomatic_refusal | proposal_result_popup | other |
|---|---|---|---|---|---|
| stale-REJECT | 4 / type 6 | apply_rejection_cooldowns | no | yes (REJECT) | |
| ACCEPT | **none** (measured `{}`) | apply_acceptance_cooldown | no | yes (ACCEPT) | treaty |
| COUNTER viable | **none** | none | no | **none** | push counter dialogue; `incoming_proposal_popup` only if it became current |
| COUNTER failed | 4 / type 6 | apply_rejection_cooldowns | yes | yes (REJECT) | |
| REJECT | 4 / type 6 | apply_rejection_cooldowns | yes | yes (REJECT) | |

The Sept-2 corrected reading's "the only one of the four outcome arms that sets no
`player_proposal_cooldowns`" is off by one: ACCEPT sets none either (benign -- a re-proposal
is refused as "We already have Peace with Russia"). The viable counter is the only non-ACCEPT
arm without one; its cooldown is deferred to the ANSWER (`reject_counter_offer` sets 3/5),
and a LAPSED counter applies only the AI-side `apply_acceptance_cooldown` +
`apply_lapse_type_cooldown` (`Russia|nation`, `Russia|peace: 5`), never a player one.

**The row's five claims on the shipped tree:**
- (i) starved behind the persistent offer, never becomes current -- TRUE as measured, but the
  persistent offer is incidental (control arm) and "never" is wrong: `/mailbox/activate` makes
  it current and answerable.
- (ii) no `incoming_proposal_popup` written -- TRUE (the IGR-F conditional write, by design),
  and no other popup either.
- (iii) lapses next end turn unseen -- HALF: it lapses (CURRENT_TURN_OFFER_TYPES) whether seen
  or not; "unseen" is FALSE -- terminal text on the end-turn response, letter-book row,
  badge (`pending_envoy_count` 3), lapse warning (`pending_lapsing_count` 2 -> main.gd:1364
  "You have 2 unanswered envoy(s) that will lapse..."), dispatch `lapsed_offers` naming
  Russia/peace (main.gd:3636 "Russia's peace offer lapsed unanswered").
- (iv) no cooldown on the counter arm -- TRUE for the player side; the repeat overture is
  accepted the turn after the lapse at 3 DP again (measured DP 5 -> 2 twice).
- (v) dispatch line contentless -- TRUE, and it is the SAME line for ACCEPT
  ("Talleyrand returns from Russia with a response." measured on the accept arm too); the
  template is outcome-blind by construction (`dispatch._DIPLOMATIC_EVENT_TEMPLATES`).
  For ACCEPT/REJECT the `proposal_result` popup carries the content; for a counter nothing does.

**Verdict: NARROWED.** True residue = (1) the counter to the player's own overture never
claims the modal slot on arrival (any same-turn mail outranks it) and never gets a popup when
promoted later; (2) an unanswered counter lapses with no player-side cooldown -- the treadmill;
(3) the outcome-blind dispatch line. Seam by symbol: `world_state._process_proposal_in_transit`
(viable-counter arm, the `dialogue_manager.push(counter_dialogue)` + conditional write),
`main._include_popup_passthroughs` (safety-valve type tuple), `turn_manager.end_turn` (the
lapse loop after `lapse_pending_offers`), `dispatch._DIPLOMATIC_EVENT_TEMPLATES`.

**What the row's fix would break.** (a) A `proposal_result_popup` with outcome COUNTER_OFFER
is an INFORMATIONAL modal: the client derives its register by substring
(`REJECT/DECLIN` vs `ACCEPT/APPROV/SUCCESS`; COUNTER_OFFER matches neither) and it has no
Accept/Reject affordance -- the player would be told about a counter by a modal that cannot
answer it while the real answer surface stays in the letter-book; it would also be delivered
beside `enemy_phase` (the PL-5A carve-out) while the actual counter is still queued. (b) A
per-court cooldown set at counter time blocks every NEW proposal to that court for 4 turns
while the counter is pending and after it is accepted (the treaty makes a re-proposal moot,
so the cooldown only ever bites a different-type ask). (c) The secondary shape --
"`lapse_pending_offers` should not lapse an item that was never current" -- reds
`tests/test_offer_lifetime.py::test_lapse_clears_all_three_offer_types` and
`::test_lapse_returns_structured_info` (both push a counter behind a current and expect it
lapsed) and re-creates the immortal-queued-dialogue class PC15-3 closed.

**Minimal correct fix as I see it.**
1. In the viable-counter arm, mount the counter with `preempt()` when the current dialogue is
   in `SOFT_STOP_MAILBOX_TYPES` (or the slot is empty), `push()` otherwise -- the manager's
   documented use of `preempt` ("a newly-created dialogue must surface immediately while an
   existing one should not be dropped"); the displaced letter/offer returns to the queue. The
   existing IGR-F conditional write then fires, `incoming_proposal_popup` (with
   `is_counter_offer`) is deferred beside `enemy_phase` and delivered on the first command of
   the new turn with real Accept/Reject buttons -- the row's intent ("regardless of the
   mailbox slot") through the existing popup that already renders counters.
2. Add `counter_offer_response` (and `counter_offer`) to the safety valve's type tuple in
   `main._include_popup_passthroughs` so a counter promoted later is re-derived like a letter
   (`_build_pending_envoy_popup_from_dialogue` already handles the type -- `/pending_envoy`
   uses it).
3. In the `turn_manager.end_turn` lapse loop, treat a lapsed `counter_offer_response` as a
   declined counter: `player_proposal_cooldowns[nation] = 3`, `[f"{nation}_{ptype}"] = 5`
   (the `reject_counter_offer` numbers), which closes the 3-DP treadmill without touching the
   manager. No pin asserts an empty player cooldown after a lapse.
4. Optional: pass `outcome` into the `diplomatic_proposal_returned` dispatch template so a
   counter reads "...returns with a counter-proposal -- see the letter-book".

**Existing pins that touch this behaviour.**
- `tests/test_settlement_gate4_leg1_fixes.py::test_player_sent_counter_band_proposal_yields_counter_dialogue`
  -- empty slot; asserts `peek().type == "counter_offer_response"`, `world.incoming_proposal_popup`
  truthy, `talleyrand_state == "IDLE"`. Holds under fixes 1-3.
- `tests/test_settlement_gate4_leg1_fixes.py::test_counter_degrades_honestly_when_payer_cannot_bridge`
  -- failed-counter arm sets `proposal_result_popup` REJECT. Untouched.
- `tests/test_phase1_critical_wiring.py::test_process_proposal_counter_offer` (~:515-545) --
  mocks `calculate_acceptance` to COUNTER_OFFER, asserts the current dialogue type. Holds.
- `tests/test_bugfix_popup_chain.py::test_counter_offer_popup_has_from_nation`, `_has_all_required_fields`,
  `_is_counter_offer_flag`, `_uses_backend_display_names`, `_clauses_are_list`, `_diplomat_info`
  (:48-316) -- empty slot; assert the popup payload shape. Hold.
- `tests/test_bugfix_popup_chain.py::test_end_turn_not_blocked_by_counter_offer_dialogue` (:518).
- `tests/test_audit_2_3.py::test_rejected_proposal_sets_cooldown` (:1596) and
  `::test_rejection_sets_cooldowns` (:1881) -- assert `player_proposal_cooldowns["Prussia"] == 4`
  and `"Prussia_peace" == 6` for outcome in ("REJECT", **"COUNTER_OFFER"**). They pass today
  only because their fixture never yields a VIABLE counter (a failed counter takes the REJECT
  arm); they already encode the row's expectation and would red the moment the fixture
  produced a viable counter -- any cooldown built into the viable arm must use 4/6 there or
  the pins be amended.
- `tests/test_offer_lifetime.py::test_counter_offer_response_is_offer_type` (:125),
  `::test_lapse_returns_structured_info` (:226), `::test_lapse_clears_all_three_offer_types` (:285)
  -- pin that a queued counter LAPSES (flip under the row's secondary shape, hold under mine).
- `tests/test_audit_part1.py::test_popup_safety_valve_rederives_incoming_proposal` (:190) --
  pins the valve for `incoming_proposal`; widening the tuple keeps it green.
- `tests/test_mailbox_system.py::test_counter_offer_response_counted` (:114) -- badge count.

### FA-N44

**What I ran.** `probe_3_fan44_paradox.py letter` (the row's recipe) and
`probe_3_fan44_paradox.py stale` (paradox queued behind Britain's persistent offer, end turn x4).

**The row's recipe (letter arm):**
```
G3| letter delivered: incoming_proposal # 1 | dm: {'current': ('incoming_proposal', 1, ..), 'queue': []}
G3| declare_war -> {'success': True, 'message': 'Prussia declares war on Denmark!'}
G3| paradox popup AFTER declare_war: present= True | dialogue_id= 2
G3| popup queue: {'commitment_paradox_popup': 'dialogue_id=2'}
G3| dm: {'current': ('incoming_proposal', 1, ..), 'queue': [('commitment_paradox', 2, ..)]} | is_hard_stop: False
G3| == status #1 == success True | commitment_paradox_popup on response: False | diplomatic_dialogue: None
G3| world.commitment_paradox_popup after status #1: True | popup queue: {'commitment_paradox_popup': 'dialogue_id=2'}
G3| [decline letter] body={'choice': 'reject_ai_proposal', 'dialogue_id': 1} ... -> success=True
G3| [decline letter] popup keys on answer response: {... 'commitment_paradox_popup': 'dict' ...}
G3| dm after decline: {'current': ('commitment_paradox', 2, ..), 'queue': []} | is_hard_stop: True
G3| == status #2 == success False | diplomatic_dialogue: commitment_paradox # 2   (already delivered above)
```
So on the shipped tree: the popup IS written unconditionally at declaration
(`diplomacy.declare_war`, the `has_paradox` block: `push(paradox_dialogue)` then
`paradox_popup["dialogue_id"] = ...; world.commitment_paradox_popup = paradox_popup`), it
carries the id, the FA-N5 gate (`main._pop_deliverable_popup` / `_popup_dialogue_is_current`)
withholds it while the letter is current (held, not dropped), and it is delivered on the
response that promotes the paradox. The title's misroute needs the modal to be on screen over
the letter, which can no longer happen; the client's paradox handler now also sends the id
(main.gd:5450/5453). The bare `choice: 1` with no id while the letter is current does accept
the letter (`"You have accepted Saxony's proposal..."`) -- but no client surface sends that
any more.

**Behind a PERSISTENT offer (stale arm; Britain's offer current from turn 4):**
```
G3| dm: {'current': ('incoming_settlement_offer', 8, ..), 'queue': [('incoming_proposal', 7, ..),
    ('commitment_paradox', 9, ..)]} | is_hard_stop: False
G3| queued paradox:  [(9, 4, True)]
G3| == status #1 == ... commitment_paradox_popup on response: False | diplomatic_dialogue: None | deferred_dialogue: None
G3| BLOCKING_TIMEOUT_TURNS = 2
G3| == END TURN -> turn 5 == ... queued paradox: [(9, 4)] | world.commitment_paradox_popup: True
G3| == END TURN -> turn 6 == ... queued paradox: [(9, 4)] | world.commitment_paradox_popup: True
G3| == END TURN -> turn 7 == ... queued paradox: []      <- clear_stale queue sweep (4 + 2 < 7)
G3|    world.commitment_paradox_popup: True | popup queue: {'commitment_paradox_popup': 'dialogue_id=9'}
G3|    status -> ... paradox on response: False | world slot after: False | popup queue: {}   <- reaped as dead
G3| final states F-P/F-D: ALLIANCE ALLIANCE | P-D: WAR
G3| paradox events in log: []
```
`push()` sets current only when the slot is empty; `_promote` runs only on pop / lapse /
remove / `promote_if_empty`; a persistent offer never vacates, so a priority-0 HARD_STOP sits
queued -- with no key on any response (`deferred_dialogue` rides only when the CURRENT is a
hard stop; `get_mailbox_items` lists only SOFT_STOP_MAILBOX_TYPES; the end-turn guard
`meta_executor` reads `is_hard_stop()` = current only) -- until `world_state.advance_turn`'s
`clear_stale(current_turn)` sweeps the QUEUE (the PC15-3 arm: a blocking item with
`turn_created + 2 < current_turn` is dropped, no event, no return value) and the popup
becomes a zombie that `_pop_deliverable_popup` reaps on the next drain, silently. Promotion
order itself is right (a paradox behind a letter is promoted first on pop; pinned in
`tests/test_dialogue_manager.py::test_pop_auto_promotes_by_priority`) -- the slot just never
clears.

**Verdict: NARROWED.** The misroute is closed; the residue is (1) a HARD_STOP raised while a
soft-stop mailbox item is current does not interrupt it and is invisible while queued, and
(2) the queue sweep destroys an unanswered crisis without a trace. The row's own fix shape
("write the slot only when current") is now a no-op for the misroute and would REGRESS
delivery: today the held popup is delivered on the promoting response (measured on the
decline response above); with the conditional write a paradox promoted later would have NO
popup -- `_respond_to_dialogue_sync` re-attaches `diplomatic_dialogue` only when the handler
returns one (probe_6: none on a promoting answer), so the player would meet the crisis only
as the next refused command's re-attached generic dialogue (rendered by `_build_content`
via the main.gd:50 whitelist), never the dedicated modal. The row's test rider (b)
("assert `commitment_paradox_popup is None` while queued") would pin that regression.

**Minimal correct fix as I see it.**
1. Producer seam, `diplomacy.declare_war` paradox block: mount with
   `dialogue_manager.preempt(paradox_dialogue)` when the current is `None` or in
   `SOFT_STOP_MAILBOX_TYPES` (the letter/offer returns to the queue, nothing is lost), keep
   `push()` when the current is another HARD_STOP or a staged LOCAL_PLANNING surface. Keep the
   unconditional popup write and the `paradox_popup["dialogue_id"]` stamp -- with the paradox
   current on arrival the FA-N5 gate delivers it on the next response. Do NOT use `open_flow`
   verbatim (its else-arm `replace()`s, which would destroy a hard-stop current).
2. `DialogueManager.clear_stale`, queue arm: never silently drop a `HARD_STOP_TYPES` item;
   either exempt them from the queue sweep (the active-slot 2-turn valve stays -- and with fix 1
   a queued paradox only arises over another hard stop) or log a `commitment_paradox_lapsed`
   event + dispatch line and clear the paired popup explicitly. Today's outcome (both alliances
   kept, no choice, no record) is a silent default.

**Existing pins that touch this behaviour.**
- `tests/test_commitment_paradox_rename.py::test_declare_war_paradox_emits_canonical_popup` (:39),
  `::test_declare_war_paradox_pushes_canonical_dialogue_type` (:50), `::test_paradox_pushes_exactly_one_dialogue`
  (:128, `queue_size == 0`), `::test_paradox_fills_only_canonical_popup_slot` -- all empty-slot
  fixtures; hold under fix 1.
- `tests/test_phase4_batch4_ledger.py::TestR12CommitmentParadox::test_paradox_detected` (:177),
  `::test_paradox_not_triggered_if_not_allied` (:190), `::test_paradox_creates_dialogue`,
  `::test_honor_defender_*` (:240-256, guards `promote_if_empty` if queued) -- hold.
- `tests/test_fa_n_p1_cluster_2026_09_02.py::TestFAN5ProducersStampIdentity::test_every_modal_producer_binds_popup_to_dialogue`
  (:646, source marker `paradox_popup["dialogue_id"]` must survive), and the delivery-gate pins
  `TestFAN37TheModalIsNotShownOverAnotherDialogue::test_the_delivery_gate_stands_on_its_own` (:696,
  notes the paradox variant was inert because paradox sits BELOW incoming_proposal in
  `PopupQueue.PRIORITY_ORDER`), `::test_the_held_popup_is_delivered_when_its_dialogue_is_current` (:720),
  `::test_a_swept_dialogue_does_not_silence_the_channel_forever`, `::test_an_orphan_that_reaches_the_queue_directly_is_reaped_too`
  (:790) -- the reaper pins; a `clear_stale` exemption for hard stops must keep the rebellion
  (non-hard-stop) sweep intact.
- `tests/test_dialogue_manager.py::test_pop_auto_promotes_by_priority` (:294),
  `::test_pop_promotes_with_correct_priority_order` (:307), `::test_noop_when_current_exists` (:479)
  -- manager-level push/promote semantics; untouched by a producer-side preempt.
- `tests/test_audit_part1.py::test_safety_valve_clears_stale_blocking_dialogue` (:219, a CURRENT
  `force_declare_war_confirmation` 3 turns old is cleared by `advance_turn`) and
  `tests/test_dialogue_manager.py` :406-452 (`clear_stale` arms) -- a queue-only hard-stop
  exemption leaves the active-slot valve pins green; check :406-452 for a queued-blocking case.

## Cross-row findings

- **Same-turn ordering is the real starvation mechanism** (FA-17): `_process_ai_diplomatic_phase`
  runs before `advance_turn` resolves the in-transit proposal, so the answer to the player's
  own 3-DP overture is always the LAST dialogue pushed that turn and never claims the slot
  when any envoy arrived (the IGR-F drip is ~2/turn). Britain also re-sends a settlement offer
  the same turn one is rejected (`settlement_offer:war_1:20:1` immediately after `:3:1`).
- **A promoted counter is popup-less** (probe_6): the answer response that promotes it carries
  no `diplomatic_dialogue`, `status` carries no `incoming_proposal` (safety-valve type tuple),
  only `GET /pending_envoy` builds it (`is_counter_offer: True`, empty `options` -- the popup's
  fixed buttons answer by keyword/index and index 2 / "reject" resolve correctly).
- **Backend keyword oddity, unreachable from the client:** `choice="counter"` on a
  `counter_offer_response` dialogue ACCEPTS it (label-containment on "Accept counter-offer",
  probe_7). The popup hides and disables its Counter button on a counter
  (incoming_proposal_popup.gd:124-125), so only a hand-built request reaches it.
- **The Sept-2 corrected reading's "only one of the four arms" is off by one:** the ACCEPT arm
  sets no `player_proposal_cooldowns` either (measured `{}` after Russia accepted); benign,
  since a re-proposal is refused as already possessed.
- `diplomatic_proposal_returned` is never written to `world.event_log` (only onto the response
  `events`/`tactical_events`), so the campaign log never records the court's answer.
- **The paradox honor arm reported success while the declaration failed** (letter arm, after
  the paradox was current): `"France honors its alliance with Denmark and declares war on
  Prussia! Cannot declare war: war_instance_side_conflict (both nations live in war_instance
  'war_1' ...)"` with `success=True` and France-Prussia still ALLIANCE. Low confidence that
  this is reachable naturally -- my `set_diplomatic_state(..., "ALLIANCE")` on Prussia while
  France sits in `war_1` may be the cause; recorded, not filed.
- **Wrong in the rows:** FA-17's repro line (`propose peace with Austria`) is refused by the
  BPH-C paradox guard on the boot board and both committed fixtures (Bavaria at war with
  Austria); the archived campaign's Austria overtures presuppose Bavaria out of that war.
  FA-N44's headline ("'Honor the alliance' is applied to option 1 of whatever is current") and
  its "no dialogue_id" measurement describe the pre-FA-N5 tree; both are false on `a1ed5c9d`.
- **Harness traps:** (1) the ambient board's combat RNG is not covered by the campaign seed --
  probe_2's arms diverged at turn 4 and a pending capture choice ("You must decide how to
  handle the captured region first!") blocked `end turn` so the turn never advanced;
  `random.seed()` after boot plus a `secure` guard fixed it. (2) The end-turn response defers
  every CHOICE popup (`_include_popup_passthroughs` is skipped beside `enemy_phase`; only
  `proposal_result`, the Proclamation, `deferred_dialogue` and the petition ride it), so
  "no popup key on the end-turn response" is expected for letters and counters alike -- the
  measurement that matters is the next `/command`. (3) `tests/test_audit_2_3.py`'s two
  cooldown pins guard `outcome in ("REJECT","COUNTER_OFFER")` on a fixture that never yields
  a viable counter -- vacuous for the arm the row is about.

## Probe inventory

All under `<scratchpad>\repro\g3\`:
- `probe_1_fa17_counter_behind_offer.py` -- first pass (boot, turn 4); found the Austria guard and the two-space filter mistake.
- `probe_2_fa17_arms.py` -- boot, arms natural / force / force_control (per-arm save dirs `saves_<arm>`).
- `probe_3_fan44_paradox.py` -- arms letter / stale (`saves_n44_<arm>`).
- `probe_4_fa17_fixture_t20.py` -- t20 fixture, arms natural / force / control, target Russia (`saves_t20_<arm>`).
- `probe_5_fa17_forced_counter_t20.py` -- t20, forced COUNTER, arms force / control (`saves_t20c_<arm>`).
- `probe_6_fa17_promotion.py` -- promoted-counter delivery (`saves_t20_promo`).
- `probe_7_fa17_wire_shape.py` -- response keys carrying the counter text; popup keyword answers (`saves_t20w_<arm>`).
Raw outputs are in the session's `tasks\*.output` files quoted above.
