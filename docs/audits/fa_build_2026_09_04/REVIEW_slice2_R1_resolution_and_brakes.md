REVIEW R1 — aa6faa01 "No Word Came" — lens: the resolution and the brakes
Scratch: ...\scratchpad\reviewR1\  (all scripts, .out files, arm_on.json / arm_off.json)
Probes import the WORKING TREE; the brakes-ON 40-turn series reproduced the commit's new
BASELINE_SERIES byte-for-byte (…78,65,62,59,56,53,50,47), so the seams I measured match aa6faa01.

================================================================================
F1  P2  THE BRAKES TRADE THE GRIND FOR A FREEZE — an engaged corps whose P0 list is emptied
        falls through to an order the executor refuses, and the 2-turn cooldown is keyed on
        ACTION TYPE, so next turn he cannot attack the man he is standing on.
Repro (shipped ambient board, both lever arms): ambient_probe.py -> analyze_arms.py, trace_charles.py
  writes: brakes ON = 16, brakes OFF (FA-1 still on) = 10 on the same WO-10-gated board.
  ON arm, t26: Charles attacks Ney @Tyrol (Ney flees to Milan, Charles advances) -> pair
  (Charles,Ney) stamped -> re-evaluated: "[P0 ENGAGEMENT] ... enemies = []" -> falls through to
  `attack -> Piedmont` from Milan with Ney standing there -> REFUSED "Cannot attack elsewhere
  while engaged with enemy forces! Ney must be dealt with first." -> cooldowns
  {'ArchdukeCharles': {'attack': 2}}.  t27: Charles takes NO action at all (still on Ney).
  t28: same shape (attack Ney, then `attack -> Provence` refused). t29: no action again.
  OFF arm: Charles acts every turn 24-32 (the old grind, no cooldowns).
Deterministic: probe_freeze.py (Charles 30k + Ney 15k at Milan, first `attack Ney` stubbed so the
  pair is stamped): brakes ON -> `attack -> Munich` REFUSED -> {'attack': 2}; turn 2: P0 prints
  "-> ATTACK Ney" but no action line follows — `_select_next_marshal_action` skips him on
  cooldown; "still engaged? True". Brakes OFF -> attacks Ney 4x in turn 1 and again in turn 2.
Why it is structural, not board noise: the executor's engaged rule (combat_executor.py:4922-4942,
  `m.strength > 0`, NO floor; movement_executor.py:193-205 for advances) refuses every
  attack-elsewhere/advance by ANY corps co-located with ANY at-war enemy, remnant included.
  So the record's "the remaining corps now fall to P4.5 / P7 and go somewhere useful" cannot be
  true for attack/advance orders while the stub stands; only retreat-to-friendly (P0's own arm,
  now skipped) and free actions are legal. The 7 co-located non-attack actions in the ON arm
  (form_square x4, unfortify x3; 0 in OFF) are that fall-through landing on free actions.
  GR5 mirror: probe_gr5.py counterfactual with a pre-stamped pair -> autonomous Ney decides
  `move -> Swabia`, refused "Cannot advance while engaged" (production builds a fresh EnemyAI,
  so the player side never reaches it — but it shows the brake is engagement-blind).
Fix (one line in P0): keep the RAW list; if raw is non-empty and `_engageable_enemies` empties
  it, do NOT fall through — return `(None, 999)` / add to `_marshals_done_this_turn` (this corps is
  finished with this engagement; the round-robin spends the nation's actions elsewhere), so no
  executor refusal ever writes an `attack`/`move` cooldown on an engaged corps.

F2  P2  P0 NO LONGER PRICES THE FIELD (CA9-N6 re-created). `_engageable_enemies` filters the list
        BEFORE `_defending_strength_in_region` sums it, so a pair-braked corps leaves the pricing
        pool while it still stands there and still reinforces.
Repro: probe_p0_pricing.py — Charles 30k vs Ney 20k + Massena 8k at Milan, pair (Charles,Ney)
  stamped. Real field: `_defender_muster(massena)` -> Ney joins, committed defender 20,700.
  brakes ON : "enemies = ['Massena'] ... ratio=3.75, threshold=1.28" -> ATTACK Massena.
  brakes OFF: "enemies = ['Ney','Massena'] ... ratio=1.07, threshold=1.34" -> RETREAT to Tyrol.
  The AI charges a field it mispriced 3.5x — the exact defect CA9-N6 closed.
Fix (one line): choose the TARGET from the braked list, price `defenders` over the RAW list.

F3  P2  TYPED STRATEGIC ORDERS BYPASS THE FA-16 GUARD. The guard sits under
        `should_check_objection` (executor.py:1438-1449), which excludes `is_strategic`
        commands; `_execute_strategic_command` has no standing-ask refusal (its head refuses only
        retreat_recovery/broken). The landing record's "the executor refuses every order but
        cancel" and "no other order can reach him" are false for march/pursue/hold.
Repro: probe_strategic_bypass2.py (Ney cornered at Berry, ask standing):
  (i) enemy ADJACENT (Mack at Gascony): "Ney, march to Paris" -> success, Ney moved Berry->Paris
      with the ask STANDING, order MOVE_TO, 2 AP. End turn 1: the issued-this-turn skip reports
      'active'; pass 3 skips him (`in_strategic_mode`) so the dead ask is NOT retired. End turn 2:
      step 0a emits requires_input `last_stand` — "Ney is cornered at Berry with 3,000 men" —
      while he stands in Paris, and the MOVE_TO is frozen behind the stale popup. (The stale
      question FA-16 exists to kill, back through the front door; the answer arm retires it.)
  (ii) enemy CO-LOCATED, Ney morale 20: "Ney, pursue Mack" -> "They're right here! Engaging!"
      -> attack under `_strategic_execution` -> BROKEN -> forced retreat -> standing ask ->
      "[!] No word came for Ney, cornered at Berry — the enemy did not wait. [!] LAST STAND …
      MARSHAL CAPTURED" — in the PLAYER phase, on the player's own typed order. The player gave
      an order and was told no word came; the fight/breakout choice was taken from him.
  (iii) "Ney, hold position" -> reaches the strategic objection ("Ney firmly objects") — the HOLD
      creation is one 'proceed' away (harmless mechanically, but the guard is not there).
  (Co-located MOVE_TO is refused, but by the engaged check, not the guard.)
Fix: add the identical standing-`last_stand` refusal at the head of `_execute_strategic_command`
  (beside the retreat_recovery/broken arms), and run `last_stand_is_live` in step 0a (or let pass
  3 retire dead asks on ordered marshals too — it only skips them today).

F4  P3  LIVENESS IS KEYED TO THE NAMED ENEMY; THE RESOLUTION TO THE CURRENT ONE. A player who
        answers is refused while still cornered.
Repro: probe_misc.py §E — ask raised by Mack; Mack draws off to Vienna; Charles (40k) now ON Ney.
  `last_stand_is_live` -> (False, 'Mack has drawn off to Vienna'); "fight to the last" ->
  "Ney's question is overtaken … He awaits new orders." Ney is still cornered at Rhineland by
  Charles; the next defeat re-raises the identical question (and a second defeat in that phase
  auto-resolves it). The player's word was discarded, then decided for him.
Fix: in `last_stand_is_live`, "the enemy" = any at-war corps ON or adjacent (re-key the ask to
  the current attacker), not the name recorded at the ask.

F5  P3  NO END-TURN SOFT-STOP FOR A STANDING LAST STAND raised in the player phase.
Repro: probe_player_phase2.py (isolated Berry, Ney morale 20, via /command): the player's own
  failed attack raises the ask and the reply DOES carry requires_input + pending_interrupt (so my
  "never saw a popup" attack FAILED — the client is shown the choice). Then "end turn"
  unanswered: no warning key, no lapse notice; enemy phase -> Ney captured (Vienna, 0 men),
  strategic_reports None. UX23 built exactly this soft-stop for envoys; the marshal has none.
Fix: fold a standing `last_stand` into the end-turn lapse warning (`pending_lapsing_count` idiom).

F6  P4  The `test_it_measurably_decreases_them` re-record (11 -> 16) is attributed to "a few of
        those orders are refused on the moved board". Measured: 2 of the +6 are F1's engaged
        refusals; the rest are divergence, incl. FOUR "Cannot attack X — Russia/Britain/Austria
        is a coalition ally" refusals at t30-35 (Shrapnel->Bagration, Bagration->Wellesley,
        Wellesley->Hiller, Shrapnel->Liechtenstein) — the AI target filter admits a coalition
        partner as at-war. Pre-existing, out of this slice's scope; deserves its own row.
        Also: the fa2 suite has no pin driving a braked corps' fall-through THROUGH the executor
        (grep: no `_record_failed_action`/`Cannot attack elsewhere`/typed-strategic assertions),
        which is why F1 and F3 shipped green.

================================================================================
ATTACKS THAT FOUND NOTHING
- "co-located AI corps issues a `move` OUT that the executor refuses": 0 such moves in either
  arm (analyze_arms.py). The refused fall-throughs are attacks-elsewhere (F1), not marches.
- GR5 production path: probe_gr5.py — autonomous French Ney (20k) co-located with Mack (3k)
  under brakes ON attacks and destroys him (`_process_autonomous_marshals` builds a fresh
  EnemyAI, so the pair/stub sets are empty by construction).
- `_fate_note`: set and consumed in the same `_apply_forced_retreat_or_break` call (line 3629-
  3631, only caller of `_check_marshal_fate`); to_dict() has no such key; a stale value is dropped
  by from_dict (probe_misc.py §C). `get_safe_retreat_destination` is RNG-free, so `encircled`
  agrees across the two calls of one resolution and the note cannot land on the surrounded branch.
- Sovereign arms (probe_misc.py §A, probe_misc2.py §G): encircled + standing -> "No word came …
  LAST STAND … THE EAGLE IN CHAINS", captured; cornered-not-encircled + standing -> Guard toll
  1,200 of 4,000 + normal retreat, ask retired — as the record says.
- Won breakout onto desperation soil (probe_misc2.py §H, Ney at Swabia, all exits at-war):
  "cuts his way out! … falls back on Lorraine" (Austrian-held) — the same tier-5 destination the
  AI's own won-roll path takes (Mack -> Munich via the forced retreat). WAD under the W6-1
  doctrine; the attrition call `(marshal, destination, world, is_retreat=True)` matches the
  forced-retreat caller at combat_executor.py:3674, and `is_retreat=True` is the same halved rate.
- Different-attacker resolution: `_resolve_unanswered_last_stand` correctly captures for the
  CURRENT attacker's nation (not the ask's named enemy).
- `context="overrun_unanswered"` only rides the log event; one-liner/headline render generically.
- Q5 vacuity: the four files pass 123/123 on the working tree and none is vacuous by reading —
  w6/np4/pc3 `handle_response` pins build LIVE asks (co-located, at war, no `location` key so the
  location clause is skipped) and assert on strength/capture/notice, which the new liveness gate
  lets through; `test_p0_engagement_still_fires` uses a fresh AI with no pair set, so the brakes
  are inert there by construction. Caveat: fixtures lacking `location` can never exercise the
  "marched clear" retirement — not their intent.
- Not re-run: the eight-arm attribution. My two arms are consistent with it (ON == new series;
  OFF == the arm-A shape diverging at index 19).

Severity roll-up: F1 + F2 + F3 are P2 regressions the fix introduced (F1/F2 in the brakes, F3
in the guard's coverage); F4/F5 are P3 gaps in the new liveness/decision surface; F6 is a record
correction plus a pre-existing AI row.
