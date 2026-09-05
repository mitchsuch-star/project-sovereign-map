# REPRO J3 - slice 14 singles (FA-N77, FA-N76, FA-N46, FA-R4, FA-42, FA-N78)

Read-only reproduction pass, master `a1ed5c9d`. Every verdict below is backed by a
probe run in `<scratchpad>/repro/j3/` against the SHIPPED boards (europe_1805.json
and tutorial_1805.json) through the real seams.

## Summary

| Row | Verdict | Measured mechanism (one line) |
|-----|---------|-------------------------------|
| FA-N77 | **REPRODUCED** (and it is worse than P2 reads) | `get_field_marshals` returns 8 while ONE French marshal stands; the audience offers `dismiss` on the last man and dismissing him leaves France with **zero** standing marshals. |
| FA-N76 | **REPRODUCED, both arms** | `POST /respond_to_redemption` accepted `dismiss` when the event offered `['grant_autonomy']` ONLY, and accepted `administrative_role` when it was not offered - producing **two** admin marshals and `bonus_actions = 2`. |
| FA-N46 | **REPRODUCED to the digit** | At an IDENTICAL 40g/turn payment: rente arm reads `eroding: True, grace_turns_left: 0` the instant he wins again and bleeds trust 85->75 in 5 turns; estate arm reads `eroding: False, grace_turns_left: 4` and bleeds 85->83. |
| FA-R4 | **REPRODUCED** | `Berthier, end turn` / `Sire, end turn` shrug (turn 1 -> 1) while `Berthier, status` and `Berthier, help` both work; the arm reads the RAW `command_lower`, its two desk siblings read `_desk_text`. |
| FA-42 | **REPRODUCED, and stronger than filed** | Under the card's own first-named answer `trust`, Ney attacks (8,000 -> 469) **and marches to Swabia**; one follow-up in the SAME turn captures Kienmayer; card VII (gate 4) still reads "Kienmayer's screen still stands... Then occupy Swabia". |
| FA-N78 | **REPRODUCED** | The only two `tutorial_overlay.observe(` sites are in `_on_command_result` (:2573) and `_on_interrupt_response` (:5134); `_on_objection_response` (:4132) and `_on_capture_choice_response` (:4587) have zero references, and both answer payloads WOULD satisfy their predicates. |

## Per row

---

### FA-N77 - Last Marshal Protection counts prisoners

Probes: `p1_fa_n77.py`, `p3_fa_n76_armA.py`, `p7_side_effects.py` (arm B), `j3_patch.py`.

**Evidence (p1, 1805 boot, every French marshal but Lannes captured by Austria):**

```
STANDING: ['Lannes']
get_field_marshals -> 8 ['Ney', 'Davout', 'Soult', 'Lannes', 'Murat', 'Bernadotte', 'Massena', 'Napoleon']
get_marshals_by_nation('France') -> 1
captured survivor sanity: 0 'Austria'
OFFERED OPTION IDS: ['grant_autonomy', 'administrative_role', 'dismiss']
```

**VERDICT: REPRODUCED** exactly as filed, and the player consequence is worse than
the row states. Through the REAL endpoint (p3), with the roster reduced so that
Lannes is the only field marshal and the event correctly offers only
`grant_autonomy`, the dismissal still goes through and:

```
STANDING FRENCH MARSHALS AFTER: []
```

Note the two rows compound: in p2 arm A the destroy sweep CAPTURED the sovereign
(`destroy_marshal` converts a sovereign removal to a capture - `world_state.py`
:2620), and that single prisoner was enough to make `field_count == 2` and put
`dismiss` back on the card. FA-N77 alone is sufficient to reach the empty roster.

**(a) True seam by symbol.** `WorldState.get_field_marshals`
(`backend/models/world_state.py`, currently line 3593 - the row's 3582 is stale by
+11). The three siblings the row cites are confirmed verbatim:

- `WorldState.get_marshals_by_nation` (:3676): `if marshal.nation == nation and marshal.strength > 0`
- `WorldState.find_nearest_marshal_within_range` (:3619) - filters inside the loop
- `clarification.py` (:139): `if m.strength > 0 and m.name != target and ...`

Also present and already guarded, which the row does not name:
`delegation.py` (:293-295) - `if marshal is None or getattr(marshal, "strength", 0) <= 0: return None` sits two lines ABOVE its `get_field_marshals` read.

**Full caller census (AST-equivalent grep over the whole backend, 6 live callers):**

| Caller | Effect of the fix |
|--------|-------------------|
| `disobedience.py:1572` (`_get_available_redemption_options`) | **the fix** - Last Marshal Protection becomes true |
| `meta_executor.py:1520` (debug `dismiss` cheat) | correct: "last field marshal" now counts standing men |
| `meta_executor.py:1574` (debug `admin` cheat) | same |
| `clarification.py:139` | **byte-identical** - already re-filters `m.strength > 0` |
| `delegation.py:295` | **byte-identical** - already gated two lines above |
| `context_carryover.py:331` (`_field_marshal_names`) | the only real behaviour change (below) |

**(b) What the row's own fix would break.** Nothing measured, but the row does not
name the one hazard I looked for: `_field_marshal_names` feeds
`_match_roster_name`, which falls back to `_closest_by_edit_distance` over the
roster - so a SHRINKING roster could turn an exact hit into a fuzzy hit on a
DIFFERENT marshal (the WO slice-10 class). Measured (p7 arm B, Ney captured):

```
WITH FIX  _field_marshal_names: ['Davout','Soult','Lannes','Murat','Bernadotte','Massena','Napoleon']
   _match_roster_name('Ney')         -> None
   _match_roster_name('Marshal Ney') -> None
   _match_roster_name('Nye')         -> None
```

No mis-guess. The behaviour change is that `not you, Ney` (Ney a prisoner) falls
through to the ordinary road instead of re-addressing a prisoner - an improvement,
and the slice-7 `prisoners.py` refusal names him there.

The row's parenthetical ("add the explicit `not getattr(marshal,'captured_by','')`
if you want the intent readable") is worth taking: a capture zeroes strength TODAY,
but the two conditions are not the same rule and the explicit one documents itself.

**(c) Minimal correct fix.** One line in `get_field_marshals`:
`and marshal.strength > 0 and not getattr(marshal, 'captured_by', '')`.

**(d) Existing tests that pin today's behaviour.** I simulated the fix with a pytest
plugin (`j3_patch.py`, `J3_FIX=n77`) and ran every consumer's file:

```
tests/test_administrative_role.py + test_autonomy.py + test_redemption_v2b.py
  + test_wo41_redemption_survives_the_save.py           98 passed
tests/test_command_robustness_cr2_clarification.py
  + ..._cr4_context_carryover.py + ..._cr5_personality_disambiguation.py  239 passed
```

**Zero flips.** The closest pins all use standing marshals:
- `tests/test_administrative_role.py::TestFieldAndAdminHelpers::test_get_field_marshals_excludes_admin` :357 - `assert len(world.get_field_marshals()) == 3`
- `tests/test_administrative_role.py::TestLastMarshalOnlyAutonomy::test_last_marshal_only_autonomy_available` :260 - `assert len(world.get_field_marshals()) == 1` (reached by `del world.marshals[...]`, not by capture)

So the fix needs a NEW pin, not an amended one - the row's suggested two-arm test is right.

---

### FA-N76 - the endpoint validates against a static list

Probes: `p2_fa_n76.py`, `p3_fa_n76_armA.py`, `p7_side_effects.py` (arm C), `j3_patch.py`.

**ARM A (p3) - options == `['grant_autonomy']` only, POST `dismiss`:**

```
field marshals: ['Lannes']
admin marshals: ['Napoleon']
OFFERED: ['grant_autonomy']
HTTP 200 success: True
message: Lannes has been relieved of command. 18,000 troops dispersed ... (+10 Authority)
Lannes still in world.marshals? False
cooldown 0 -> 6
STANDING FRENCH MARSHALS AFTER: []
```

**ARM B (p2) - an admin already appointed, POST `administrative_role`:**

```
admin marshals: ['Massena']
OFFERED: ['grant_autonomy', 'dismiss']          <-- administrative_role NOT offered
HTTP 200 success: True
message: Lannes has been transferred to administrative duties. ... You now have 6 actions per turn.
admin marshals AFTER: ['Lannes', 'Massena']
bonus_actions: 2
```

**VERDICT: REPRODUCED, both arms.** Last Marshal Protection AND the one-admin rule
are presentation-only. The row's static list is confirmed at
`backend/main.py:3940` (the row's :3581 is stale by +359):
`valid_choices = ['grant_autonomy', 'administrative_role', 'dismiss']`, and
`redemption_event['options']` is never consulted before the handler call at :3946.

**(a) True seam by symbol.** `DisobedienceSystem.handle_redemption_response`
(`backend/commands/disobedience.py:1723`), immediately after the
`marshal = world.get_marshal(marshal_name)` lookup and **before** the two mutations
at the top of the body:

```python
marshal.redemption_pending = False
marshal.redemption_cooldown_until = getattr(world, 'current_turn', 0) + 5
```

Siting it there is correct and the row is right about why: it is the ONLY function
`main.py:3946` and every future caller share (census: 1 production caller, 22 test
call sites across 4 files).

**(b) What the row's own fix would break - and a sibling defect it must also close.**
The handler ALREADY has an invalid-choice fall-through at
`disobedience.py:1877-1880`, and it sits AFTER the latch clear and cooldown stamp.
Measured (p7 arm C, calling the handler directly with `demand_obedience`):

```
before: redemption_pending=True  cooldown=0
result success=False  message='Invalid choice: demand_obedience. Valid options: ...'
after : redemption_pending=False cooldown=6
```

So today an unrecognised choice **destroys the question and buys a 5-turn cooldown
while reporting failure**. The endpoint's static list is currently the only thing
shielding that path - so a fix that REMOVES the static list and relies on the new
handler guard must place the guard above the mutations, or it opens a wider hole
than it closes. `tests/test_administrative_role.py::TestDemandObedienceRemoved::test_demand_obedience_returns_invalid`
(:471) asserts `'Invalid choice' in result['message']`, so the new refusal must keep
that phrase.

**(c) Minimal correct fix.** At the top of `handle_redemption_response`, after the
marshal lookup and before `marshal.redemption_pending = False`:

```python
offered = {o.get('id') for o in (redemption_event or {}).get('options', [])}
if offered and choice not in offered:
    return {'success': False,
            'message': f"Invalid choice: {choice}. Valid options: {', '.join(sorted(offered))}"}
```

`if offered` keeps hand-built events (tests, drivers) working. This also subsumes the
existing tail fall-through and fixes the latch/cooldown burn for free. `main.py`'s
static list may stay (defence in depth) or go; if it stays it must not be narrower
than the offered set.

**(d) Existing tests.** Simulated exactly this guard (`j3_patch.py`, `J3_FIX=n76`)
and ran all four redemption files: **98 passed, zero flips**, including
`test_demand_obedience_returns_invalid`. The 22 direct handler call sites all build
their event via `_create_redemption_event`, which fills `options` from
`_get_available_redemption_options`, and every one of them chooses an offered id.

---

### FA-N46 - the rente-paid marshal's frozen grace clock

Probes: `p4_fa_n46.py` (first cut - confounded), `p5_fa_n46_fair.py` (the A/B).

The first cut was NOT a fair comparison: an estate big enough to cover 40 also
covered the risen 120, so the estate arm never entered the unmet branch. `p5` shrinks
the estate so **both arms pay exactly 40g/turn**, which is the row's real claim.

```
ARM: rente   (paid 40g/turn)
  clock opens              turn= 2 grace=  2 short= 40 eroding=False trust=85
  1st paid turn            turn= 3 grace=  2 short=  0 eroding=False trust=85   <-- FROZEN at 2
  after 9 quiet paid turns turn=11 grace=  2 short=  0 eroding=False trust=85
  -> he WINS AGAIN: expectation 120 satisfaction 40 shortfall 80
  UNMET ROW (the instant he wins): {'eroding': True, 'grace_turns_left': 0, ...}
  tick #1 turn=12 eroding=True trust=83
  ...
  TRUST 85 -> 75 over 5 turns

ARM: estate  (paid 40g/turn)
  1st paid turn            turn= 3 grace= -1 short=  0 eroding=False trust=85   <-- RESET
  -> he WINS AGAIN: expectation 120 satisfaction 40 shortfall 80
  UNMET ROW (the instant he wins): {'eroding': False, 'grace_turns_left': 4, ...}
  tick #1..#4  eroding=False trust=85
  tick #5      eroding=True  trust=83
  TRUST 85 -> 83 over 5 turns
```

**VERDICT: REPRODUCED.** Identical payment, 5x the trust bleed, and the player-facing
Unmet-Marshals row says `eroding: True, grace_turns_left: 0` before a single turn has
passed. The row's characterisation of WO-18's own safety argument is also confirmed
correct: the comment at `dotation.py:100-102` ("A marshal genuinely kept on a rente
never erodes anyway...") is false the moment `battles_won` moves.

**(a) True seam by symbol.** `WorldState._process_dotation_state`
(`backend/models/world_state.py:6036`), the met branch's freeze at **:6164**
(the row's :6144-6146 is stale by ~+19):

```python
_estate_covers = get_estate_income(marshal, self) >= expectation
if not PENSION_CHURN_GUARD_ACTIVE or _estate_covers:
    marshal.expectation_grace_turn = -1
```

The stale anchor is read at the unmet branch (`elapsed = self.current_turn - marshal.expectation_grace_turn`, currently :6196).

**(b) Does the fix need a new serialized field?** **Yes, or an equivalent stamp - I
could not derive it.** The met branch has to distinguish "the shortfall re-opened
because he was UN-PAID" (the WO-18 dodge) from "because expectation ROSE". Nothing
in today's serialized state records the expectation at freeze time: `battles_won` is
monotonic and un-snapshotted, `pension` is the live face, and `last_expectation_seen`
is owned by the dispatch's `expectation_rises` beat (overloading it would recreate
the CA9 two-owners-one-field trap). A `pension > 0` test is NOT safe - a dodger can
re-grant a 1g rente for 2g/turn and reset the clock.

**The one field-free alternative I found - and why it must not be built as-is.**
A *sliding* freeze (`expectation_grace_turn += 1` on each frozen met turn, so
`elapsed` holds instead of growing) preserves WO-18's real invariant ("unmet turns
accumulate") and needs no new field. It FLIPS the slice's own pin:

- `tests/test_wo_slice14_the_clock_and_the_flag.py::test_churn_now_erodes_after_grace_regardless_of_the_toggle` :143-145
  - `assert first_unmet == 11`
  - `assert m.expectation_grace_turn == first_unmet`  <-- the anchor must not move

and it changes WO-18's semantics from "GRACE_TURNS calendar turns after the first
unmet turn" to "GRACE_TURNS cumulative unmet turns". That is a re-gate, not a fix.

**(c) Minimal correct fix.** The row's shape, with one correction to its acceptance
test. Stamp the covered expectation when freezing (`Marshal.expectation_covered_at_freeze`,
one serialized int, `.get()`-defaulted like `expectation_grace_turn`, reset to 0
wherever the clock resets to -1); at the unmet branch, if
`expectation > expectation_covered_at_freeze` **and** `satisfaction` has not fallen
below what it was covering (i.e. he is still being paid what he was paid), the
shortfall re-opened because he WON - restart the clock at the current turn.
**Correction to the row's own test:** it demands `grace_turns_left == GRACE_TURNS`.
That is right for the stamp-based fix (a fresh window) - but state it as the CHOSEN
rule, because the alternative honest answer is "he keeps the unmet turns he had
banked", and the two differ by exactly the elapsed count at freeze (1 in my probe).

**(d) Existing tests that pin today's behaviour.**
- `tests/test_wo_slice14_the_clock_and_the_flag.py::test_a_genuinely_kept_rente_never_erodes_and_charges_the_bill` :105-118 - the row is right that it holds `battles_won` fixed (`m.battles_won = 5` in `_owed_marshal`, :97) AND it starts from `expectation_grace_turn = -1`, so it never exercises the freeze branch at all. It stays green under the fix.
- `tests/test_wo_slice14_the_clock_and_the_flag.py::test_churn_now_erodes_after_grace_regardless_of_the_toggle` :143-145 - green under the stamp fix (the toggle never raises expectation), RED under the sliding-freeze alternative.
- `tests/test_wo_slice14_the_clock_and_the_flag.py::test_estate_income_that_covers_him_still_resets_the_clock` :200-206 - `assert m.expectation_grace_turn == -1`; unaffected.
- `tests/test_wo_slice14_the_clock_and_the_flag.py::test_a_single_grant_then_revoke_still_opens_the_clock` :147-160 - unaffected.

---

### FA-R4 - `Berthier, end turn` (design row, blessed)

Probes: `p6_fa_r4.py`, `p7_side_effects.py` (arm A).

**Backend gate, measured:**

```
END_TURN_PHRASINGS = ('end turn', 'end_turn', 'next turn')
  is_bare_end_turn('end turn')           = True
  is_bare_end_turn('Berthier, end turn') = False
  is_bare_end_turn('Sire, end turn')     = False
  is_bare_end_turn('next turn')          = True

--- POST /command (mock parser) ---
  'Berthier, end turn'  turn 1 -> 1  success=False
       "Sire, I must confess this order eludes me," Berthier admits. "Shall I relay an order to Ney? ..."
  'Sire, end turn'      turn 1 -> 1  success=False
       Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. ..."
  'Berthier, status'    turn 1 -> 1  success=True   (intelligence report)
  'Berthier, help'      turn 1 -> 1  success=True   (command reference)
  'end turn'            turn 1 -> 2  success=True
```

**VERDICT: REPRODUCED**, with one addition the row does not note: the two addressed
forms shrug **differently** (the `Berthier,` form gets the marshal-relay shrug, the
`Sire,` form the generic one), so a player gets two different unhelpful answers.

**(a) True seams by symbol.**
- Backend: `backend/ai/clause_guards.is_bare_end_turn` (:132) + `END_TURN_PHRASINGS` (:129); the CONSUMER is `llm_client.py`'s mock chain, currently `elif is_bare_end_turn(command_lower):`. Its two desk siblings on either side of it read `_desk_text` (the `_DESK_ADDRESS_RE`-stripped form, `llm_client.py:168` = `^\s*(?:berthier|sire)\s*[,:]\s*`); **the end-turn arm alone reads the raw `command_lower`.** That asymmetry is the whole row, and it is one token wide.
- Client: `godot-client/project-sovereign/scripts/main.gd::_is_end_turn_phrasing` (:1297), consumed once at :1404 inside the lapse-confirm branch of `_execute_command`. It hardcodes the three strings (`return c == "end turn" or c == "end_turn" or c == "next turn"`); it is a MIRROR, not a shared source.

**The row's warning is mechanically correct.** :1404 is the ONLY route from a typed
phrasing into `_execute_end_turn()` (which raises `_show_lapse_confirmation`,
:1357). Widen the backend alone and `Berthier, end turn` travels as an ordinary
command, the server advances the turn, and the unanswered-envoy confirm never
appears - the UX23 soft-lock class, inverted.

**(b) The ONE vocabulary and where it must live.** Do **not** add phrasings to
`END_TURN_PHRASINGS`; add the ADDRESS STRIP on both sides:
- backend: `is_bare_end_turn` strips `_DESK_ADDRESS_RE` before the membership test (or the chain calls `is_bare_end_turn(_desk_text)`), so the vocabulary tuple is untouched;
- client: `_is_end_turn_phrasing` gains the same leading-address strip.

There is no shared file between Python and GDScript, so parity has to stay a PIN.
One already exists and is good: `tests/test_fa_slice1_the_two_words_2026_09_02.py::TestTheClientGateSpeaksTheSameVocabulary::_client_gate`
re-derives the client predicate out of `main.gd` by regexing `c == "..."` needles
(:250-265) and `test_both_gates_agree` (:267-270) evaluates BOTH gates on one fixture
list. **That harness must be extended**, because today it only re-derives equality
needles - it cannot see an address strip, so `("Berthier, end turn", True)` would
pass the backend half and fail the client half even after the `.gd` is fixed.

**(c) What the fix must not break.**
- `test_the_vocabulary_itself_is_unchanged` (:283-286): `assert END_TURN_PHRASINGS == ("end turn","end_turn","next turn")` - stays green under the strip approach, RED if you add a phrasing.
- The FIXTURES list (:239-248) contains `("Davout, fortify until next turn", False)`. `_DESK_ADDRESS_RE` only matches `berthier|sire`, so a marshal address is untouched. Verified safe.
- Negation: measured (p7 arm A) `do not end turn`, `Berthier, do not end turn` and `Berthier, end turn please` all leave turn 1 -> 1. The strip must run BEFORE the bare test but the bare test must stay WHOLE-command, or `Berthier, end turn please` would start ending turns.
- `tests/test_ux_fixes_2026_08_23.py:467` pins the dispatch line `"if _is_end_turn_phrasing(command):"` - unaffected by a body change.
- `tests/test_review_2026_08_30.py` :691, :707-710, :1303, :1314 - grep-style pins over the same `.gd` body and over `"elif is_bare_end_turn(command_lower):"` in `llm_client.py`. **:710 asserts that exact source line**, so a change to `is_bare_end_turn(_desk_text)` at the call site would flip it; changing the FUNCTION body instead keeps it green. Prefer the function body.

**(d) Full pin list (grep `is_end_turn_phrasing|END_TURN_PHRASINGS|is_bare_end_turn` in tests/):**
`tests/test_fa_slice1_the_two_words_2026_09_02.py` (:41-42, :250-286, :687-695),
`tests/test_review_2026_08_30.py` (:691, :707-710, :1303, :1314),
`tests/test_ux_fixes_2026_08_23.py` (:467).

---

### FA-42 - the tutorial's promised trust-branch pivot

Probes: `p8_fa42_payload.py`, `p9_fa42_keys.py`, `p11_fa42_trust.py`.

**The trust branch, driven on the shipped tutorial board (p11):**

```
TRUST answer: success=True
  message: You defer to Ney's judgment. | Ney executes their alternative plan. |
           [Combat] Ney leads the charge! (Aggressive: +15% attack) ...
           Casualties: Ney's army 527, Kienmayer 7,529.
  Kienmayer 8000 -> 469  captured_by=''
  Ney stance/location: Stance.NEUTRAL Swabia
  actions_remaining: 3
  follow-up attack #1: turn=1 Kienmayer strength=0 captured_by='France'
  game_state.enemies now: {'Kienmayer': {'location': 'Paris', 'strength': 0, 'nation': 'Austria'}}
```

**VERDICT: REPRODUCED, and stronger than the row states.** `trust` does not merely
make Ney "attack early" - he attacks, wins overwhelmingly, **and marches into
Swabia**. One follow-up attack in the SAME turn (3 AP left) captures Kienmayer. So
card VII at `turn_gate` 4 is stale in TWO ways: it names a prisoner as a standing
screen, and its recovery line ("Then occupy Swabia") names a province Ney already
holds.

**Structural claims, all confirmed at current line numbers:**
- `STEPS` is `const` (`tutorial_overlay.gd:52`) with no branch on the objection answer; `_note_observations` (:346) latches only `_saw_objection` and `_saw_capture`.
- `first_battle` `turn_gate: 4` (:113), body "Kienmayer's screen still stands across the Rhine", chip `Ney, attack Kienmayer`.
- `objection_answer` (V) names `trust` FIRST (:91-93).
- `_maybe_catch_up` (:365-373): `_turn > gate+1 and _turn >= next_gate` -> release at turn 6 for this step.
- `_render` overdue line (:403-405): `turn_gate < _turn` -> appears from T5.

**The TUTORIAL_SCRIPT.md table vs STEPS - the row found two stale rows; there is a THIRD.**

| Doc row (`docs/TUTORIAL_SCRIPT.md` :336-352) | STEPS | Stale? |
|---|---|---|
| T2 "Trust branch = Ney attacks early and the next card pivots" (:342) | no pivot exists | **the promise itself** |
| T3 "First blood - `Ney, attack Kienmayer`" (:343) | `first_battle` gate **4** | stale |
| T4 "The guns speak - `Senarmont, bombard Jellacic`" (:344) | `bombardment` gate **2** | stale, **and the ORDER is inverted** (STEPS runs guns VI before blood VII; the doc runs blood before guns) |
| T6 "Conquest - `Ney, attack Jellacic`" (:346) | `capture` gate 6 suggests **`Davout, move to Bohemia`** | **stale - row missed this one** (wrong marshal, wrong enemy, wrong province) |

All other rows agree with their gates.

**(a) True seam by symbol.** `tutorial_overlay.gd::_note_observations` (:346) for the
latch, `::_render` (:386) for the branch, and `::_pred_battle_happened` (:513) if the
pivot re-targets the advance.

**(b) What the row's own fix would break / cannot do.** The row says to set
`_kienmayer_gone` "when a battle_report/conquest names Kienmayer as the beaten side
or a dispatch event of type capture names him". **Measured, neither key carries it:**

```
battle_report keys: ['casualty_summary','enemy_voice','marshal_voice','modifier_breakdown','observation']
events: [('battle', 'None')]
```

There is no structured defender/outcome field and the event's `message` is `None` in
the response. The only Kienmayer mentions are inside PROSE
(`observation` = "Complete dominance on the field. Kienmayer crumbled before Ney.",
`enemy_voice` = 'Kienmayer: "Withdrawal conducted in order..."') - and `enemy_voice`
names him even when he SURVIVES, so a substring latch on it would fire on every
battle. Building the row's fix as written gives a false latch.

**(c) What `_kienmayer_gone` must actually key on - by response key.** The overlay's
own `_marshal_location` reads `game_state.marshals`, which is **player-only**
(measured: `names: ['Davout','Ney','Senarmont','Soult']` - Kienmayer never appears,
before or after capture). The key the overlay does not read yet is
**`game_state.enemies`**, built by `WorldState.get_game_state_summary`'s fog filter
(`world_state.py:9027-9044`):

```
BOOT (PARTIAL fog):  {'Kienmayer': {'location':'Swabia','strength':0,'nation':'Austria',
                                    'strength_band':'small force','fog_level':'partial'}}
CAPTURED (at Paris, FULL): {'Kienmayer': {'location':'Paris','strength':0,'nation':'Austria'}}
```

Note the trap: at PARTIAL the filter writes `strength: 0` deliberately, so a bare
`strength == 0` test fires at boot. The honest discriminator is the FULL-visibility
shape - the record loses `strength_band` and `fog_level`:

> `_kienmayer_gone` = `"Kienmayer"` is ABSENT from `game_state.enemies`
> (destroyed / out of intel), **or** present with `strength == 0` AND **no**
> `fog_level` key (reported at FULL visibility, i.e. the 0 is a fact).

**(d) Existing tests that would flip.**
- `tests/test_tutorial_school_fixes_2026_08_08.py::test_suggest_chips_unchanged` :294-295 - `assert '"suggest": "Ney, attack Kienmayer"' in overlay`. Stays green ONLY if the pivot keeps the Kienmayer chip as the default arm and adds the alternative under a different key.
- `tests/test_tutorial_position7.py::test_b1_every_suggest_mock_parses_to_its_action` :410-436 - regexes `"suggest":` and `"suggest_action":` and `assert len(suggests) == len(actions)`. **A second `"suggest":` key inside the pivoted step dict desyncs the zip and reds this.** Name the alternative `"suggest_alt"` / `"suggest_alt_action"` and extend the harness, or the pin fails for the wrong reason.
- `tests/test_tutorial_scenario.py::test_kienmayer_has_no_friendly_exit` :180-189 - the "breaks in place or dies" premise. Not flipped by FA-42's fix, but see cross-row note (FA-9 already falsifies it under the lesson layout).
- `tests/test_wo_slice7_cabinet_door.py:896` - `"Ney, attack Kienmayer"` in a must-NOT-be-claimed list; unaffected.

---

### FA-N78 - the School goes blind at both popup beats

Probes: `p10_fa_n78.py`; source read of `main.gd` and `tutorial_overlay.gd`.

**Census (grep `tutorial_overlay` in `main.gd`, current line numbers):**

```
319  var tutorial_overlay = null
507  register(...)                        509 suggest_command.connect(...)
711  on_world_swap(response)              4737 on_world_swap(response)
2573 tutorial_overlay.observe(response)   <- inside _on_command_result (:2556)
4511 on_control_returned()
5134 tutorial_overlay.observe(response)   <- inside _on_interrupt_response (:5116)
```

`_on_objection_response` (**:4132**, row filed :4010 - stale by +122) and
`_on_capture_choice_response` (**:4587**, row filed :4459 - stale by +128) have
**zero** references. Neither delegates to `_on_command_result`; the objection handler
calls `_display_result` three times and `_display_result` (:2759) does not observe.

**VERDICT: REPRODUCED.** The row's proof is the comment sitting directly above the
one observe site (`main.gd:2566-2568`): *"the School of War reads every response
ahead of routing so an early-returning route (objection, capture) still reaches the
tutor"* - which is true of the response that RAISES the question and false of the
response that ANSWERS it, because the answers arrive on
`/respond_to_objection` and `/capture_choice` through different callbacks.

**The fix is measurably load-bearing** - both answer payloads satisfy their step's
predicate today (p10, tutorial board):

```
=== beat IV/V ===
pending_objection? True | state= awaiting_player_choice
ANSWER response: success=True pending_objection=None has game_state=True
  _pred_objection_resolved would be: True

=== beat IX/X ===
pending_capture_choice? True
ANSWER response: success=True capture_choice='secure' pending=None
  _pred_capture_resolved would be: True
  has game_state: True
```

Both carry `game_state`, so `_turn` tracking is preserved through the call.

**(a) True seam by symbol.** `main.gd::_on_objection_response` (:4132) and
`main.gd::_on_capture_choice_response` (:4587). The call must sit at the TOP of each
body, above every early return - `_on_capture_choice_response`'s first statement
after `set_input_enabled(true)` is
`if _response_has_capture_choice_route(response): _show_capture_choice_dialog(response); return`,
so a call placed lower would miss the chained second question (the W6-8 estate
stage / a stale-token re-attach).

**(b) One claim in the row is wrong.** The row asserts "the overlay is observe-only
and **idempotent per response**, [so] adding the call cannot route, block, or send."
Observe-only is TRUE and verified: `observe()` (:313) does `_note_observations` ->
predicate -> `_advance_one`/`_maybe_catch_up` -> `_render` + `AudioManager.play`;
the only sender is `_on_meta_clicked` (:420), which is user-driven. **Idempotent is
FALSE**: `observe()` advances whenever the CURRENT step's predicate holds, so two
calls with the same response can advance twice (e.g. `_pred_any_success` is true for
any successful response). It is safe here only because neither handler's response
reaches any other observe site - which is a fact to state in the fix, not an
invariant to assume.

**(c) Minimal correct fix.** One helper (`_school_observe(response)`) carrying the
null guard, called at the head of both handlers. If it is extended further, the
other handlers that resolve a blocking question and never observe are:
`_on_redemption_response` (:4363), `_on_glorious_charge_response` (:4909),
`_on_marshal_petition_result` (:6103), `_on_mailbox_row_action_result` (:5695),
`_on_mailbox_activate_result` (:5756) - plus the four chip-route callbacks
`_on_reward_command_result` (:5938), `_on_vassal_command_result` (:5981),
`_on_naval_command_result` (:6004), `_on_region_panel_command_result` (:6077).
The tutorial's own beats need only the two named; the census pin below is what stops
the next one being missed.

**(d) The pin that must change.**
`tests/test_tutorial_position7.py::TestClientStructuralPins::test_g2_nonmodal_registration_and_observe_only`
:197 -

```python
assert gd.count("tutorial_overlay.observe(") >= 2
```

This is the blind pin the row names, and it is satisfied by ANY two call sites. The
delegation-aware census the row asks for is the right replacement: build every `func`
body from `main.gd`, compute the transitive closure of functions that reach
`tutorial_overlay.observe(` (so a helper counts for its callers), and assert that
every handler answering a blocking question is in the closure. Sibling pin
`test_g3_observe_before_routing` :201-206 (`body.index("tutorial_overlay.observe(") < body.index("_route_response_ui(")`)
is scoped to `_on_command_result` and stays green.

---

## Cross-row findings

1. **FA-N77 and FA-N76 compound into an empty French roster.** Measured end to end
   (p2 arm A): with every other French marshal a prisoner, the prisoners keep the
   field count at 2, `dismiss` is offered, the endpoint accepts it, and
   `STANDING FRENCH MARSHALS AFTER: []`. Either fix alone closes that particular
   road; both are needed for the rule to be true in general. Fix them in ONE slice.

2. **A third, unfiled defect in the same seam.** `handle_redemption_response`'s
   existing invalid-choice fall-through (`disobedience.py:1877-1880`) sits AFTER
   `marshal.redemption_pending = False` and the `+5` cooldown stamp, so an
   unrecognised choice reports failure while retiring the question for five turns
   (measured, p7 arm C: `redemption_pending True -> False`, `cooldown 0 -> 6`).
   Today the endpoint's static list hides this. FA-N76's guard closes it only if it
   is placed above the mutations.

3. **A sibling hardcoded-choice list.** `backend/main.py:4031` -
   `valid_choices = ['charge', 'restrain']` on the glorious-charge endpoint - is the
   same pattern as FA-N76's :3940. I did not probe whether its offered set can
   differ, but it is the obvious neighbour to check while the fix is open.

4. **`destroy_marshal` converts a sovereign removal into a CAPTURE**
   (`world_state.py:2620, NP-4`) and returns False. Any probe or fix that "removes
   every French marshal" leaves Napoleon standing as a prisoner - which is exactly
   the state FA-N77 mis-counts. Worth a pin in the FA-N77 test.

5. **`game_state.marshals` is player-only; `game_state.enemies` is the fogged enemy
   view.** The tutorial overlay's `_marshal_location` (:470) reads the former, so it
   is structurally incapable of seeing an enemy - which is why FA-42's fix cannot be
   written against it. And in `enemies`, `strength: 0` means "fogged" at PARTIAL and
   "gone" at FULL; the `fog_level`/`strength_band` keys are the only discriminator.

6. **`tests/test_tutorial_scenario.py::test_kienmayer_has_no_friendly_exit` (:180-189)
   and `docs/TUTORIAL_SCRIPT.md:343** both still assert "a beaten Kienmayer breaks in
   place or dies". FA-9 already narrows that; my p11 measurement adds that under
   `trust` he is CAPTURED, not broken and not dead - a third outcome neither the pin
   nor the doc admits.

7. **Line-number drift confirmed on 5 of 6 rows** (FA-N77 +11, FA-N76 +359,
   FA-N46 +19, FA-N78 +122/+128, FA-42 ~+1). FA-R4 was accurate (it is a Sept-5 row).
   Navigating by symbol was necessary every time.

8. **Harness note:** simulating a backend fix as a pytest plugin on `PYTHONPATH`
   (`-p j3_patch`) measures "which pins flip" without a single repo write. Both
   FA-N77 and FA-N76 fixes came back **337 tests green, zero flips**, which is
   evidence the fixes need NEW pins rather than amended ones.

## Probe inventory

All under `<scratchpad>/repro/j3/`:

| File | What it measures |
|------|------------------|
| `p1_fa_n77.py` | FA-N77: `get_field_marshals` counts prisoners; the offered option ids |
| `p2_fa_n76.py` | FA-N76 arm A (first cut - the sovereign survived as a prisoner) + arm B (double admin) |
| `p3_fa_n76_armA.py` | FA-N76 arm A clean: offered `['grant_autonomy']`, POST `dismiss` succeeds, roster emptied |
| `p4_fa_n46.py` | FA-N46 first cut (estate arm confounded - kept as the record of the mistake) |
| `p5_fa_n46_fair.py` | FA-N46 the fair A/B at an identical 40g/turn payment |
| `p6_fa_r4.py` | FA-R4: `is_bare_end_turn` table + five commands through the real `/command` |
| `p7_side_effects.py` | FA-R4 negation forms; FA-N77's carryover edit-distance hazard; the latch/cooldown burn |
| `p8_fa42_payload.py` | `game_state.marshals` is player-only; the tutorial roster |
| `p9_fa42_keys.py` | FA-42: `battle_report` / `events` / `enemies` keys before and after capture |
| `p10_fa_n78.py` | FA-N78: the two answer payloads and their predicates |
| `p11_fa42_trust.py` | FA-42: the `trust` branch driven live - attack, march to Swabia, capture |
| `j3_patch.py` | pytest plugin simulating the FA-N77 and FA-N76 fixes (repo untouched) |
