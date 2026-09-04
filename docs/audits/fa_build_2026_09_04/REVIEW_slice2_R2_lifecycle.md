REVIEW R2 — attacking the FA-16 / FA-1 / FA-N13 / FA-N68 fix at aa6faa01 (lifecycle lens)

METHOD. The working tree has backend/commands/strategic.py and strategic_executor.py mid-edit
(slice 3, +398 lines), so probes importing the working tree would NOT test aa6faa01. Every probe
ran against a `git archive aa6faa01` snapshot at reviewR2/tree (sys.path + cwd pointed at it),
through the REAL endpoints (POST /command, /strategic_response, /save, /load, end turn) with
CommandParser(use_real_llm=False) swapped into backend.main and use_real_api asserted False.
Scripts + captured output: p1_typed_and_gate.py (p1.out.txt), p1b_followups.py (p1b.out.txt),
p2_lifecycle.py (p2.out.txt), p3_liveness_edges.py (p3.out.txt), p4_muster_endturn.py (p4.out.txt).
Mutation copies: tree_mut (all three levers off), tree_mut2 (end-turn promotion deleted).

F1 — P1 — THE GATE DOES NOT COVER STRATEGIC VERBS; the fix's own headline example still reproduces.
  Repro: p1_typed_and_gate.py / p1b_followups.py §1, §7 (order-free last stand on Massena at
  Belgium, Mack 40k ADJACENT at Rhineland — the ordinary post-defeat geometry, and one that
  last_stand_is_live explicitly counts as LIVE):
    'Massena, march to Vienna'    -> success, MOVE_TO order, AP 4->3, ask OVERWRITTEN by
                                     contact_bad_odds ("Mack blocks the path at Rhineland")
    'Massena, advance to Rhineland' -> same
    'Massena, hold Belgium'       -> success, HOLD order, AP 4->2, ask parked underneath
    'Massena, pursue Mack' (intel) -> PURSUE order + first-step ENGAGEMENT, 3,000 -> 1,830,
                                     ask STILL STANDING, rail row standing
  Then (p1b §7) after the march overwrote the ask: typed 'fight to the last' is no longer an
  answer — it parses as ATTACK, the strategic override clears the contact question, and he
  fights 3,000 vs 40,000 ("Massena (3,000 troops) attacks! MUSTER ..."). The CRITICAL rail row
  is now ORPHANED (rail=1, ask=None): dismiss_marshal_ask never runs because the question was
  overwritten, not answered or retired — the FA-N68 family, re-opened one seam over.
  Cause: the gate sits under should_check_objection, whose predicate contains
  `not is_strategic_command` — the identical exclusion NPC-2's docstring records as what made
  TUT-F4a unreachable. The landing record's method note saw the exclusion ("already excludes
  both") and read it as making the exemption dead, not as making the gate unreachable for
  "Ney, march to Vienna" — the very sentence the executor comment cites as fixed. When Mack is
  CO-LOCATED the marches are refused by an unrelated "engaged" guard, which is why the slice's
  four tactical dict-command pins never saw it.
  Fix: check standalone_decision(marshal) for last_stand at the head of
  StrategicExecutor._execute_strategic_command (same refusal dict), or hoist the gate above
  should_check_objection keyed on marshal_name alone.

F2 — P2 — THE UN-ADDRESSED GENERAL RETREAT IS A FREE, RISK-FREE ESCAPE FROM THE DECISION.
  Repro: p1b_followups.py §5–§6. 'retreat', 'fall back', 'everyone retreat', 'general retreat',
  'retreat to Paris' all -> "General retreat ordered! Massena falling back!": Belgium -> Paris,
  0 men lost, 0 AP, ask left standing, rail standing; the next end turn retires it ("marched
  clear of Belgium"). The addressed 'Massena, retreat' is refused by the gate. The breakout roll
  in the identical state captured him (3,000 lost). The aggressive ask is raised precisely when a
  retreat destination exists (FA-N25's own note), so this dominates the W6-7 choice every time.
  Cause: general_retreat carries no marshal, so should_check_objection is False;
  _execute_general_retreat iterates every in-danger marshal.
  Fix: in _execute_general_retreat skip (and name) marshals with a standing last stand.

F3 — P2 — `charge` BYPASSES THE GATE.
  Repro: p1b_followups.py §3: cornered cavalry Murat (recklessness 3, Mack co-located),
  'Murat, charge Mack' -> "GLORIOUS CHARGE!" executes, AP 4->3, 3,000 -> 660, ask standing.
  charge (and bombard) are not in objection_actions. Fix: gate on "any marshal-bearing action
  except cancel", not on the objection list.

F4 — P3 — AFTER A BYPASSING ORDER THE QUESTION VANISHES FOR A TURN, THEN RETURNS CONTEXT-FREE.
  Repro: p2_lifecycle.py §E: 'Massena, hold' (Mack adjacent) executes; end turn 1 -> step 0a
  "SKIP - order issued this turn" emits status=active, NO requires_input, pass 3 skips him
  (in_strategic_mode) -> response pending_interrupt=None; end turn 2 -> step 0a row
  command='HOLD', message "Massena awaits your orders.", options = the last-stand pair, no
  nested pending_interrupt — the popup shows two fate buttons under a HOLD header with no
  cornered/enemy/location text, and step 0a never runs last_stand_is_live (only the answer arm
  does). Fix: step 0a should emit the parked decision's own message/payload for STANDALONE types,
  and the issued-this-turn skip should still surface a standing decision.

F5 — P3 — "muster_confirm ... re-validates itself" is half true.
  Repro: p4_muster_endturn.py. Pass 3 surfaces and promotes the muster and the driver answers
  attack_anyway. (A) target marched to Vienna: the question is CONSUMED by "No intelligence on
  Mack's position, Sire. Scout for him before Davout can give chase." — a pursuit refusal, no
  battle, no AP. (B) target DESTROYED: success=True with "Davout firmly objects: 'Sire, the
  enemy is too strong. We need reinforcements.'" — an objection dialog about a marshal who no
  longer exists (objection runs before target validation on the _muster_confirmed re-issue).
  Pre-existing on the typed route; pass 3 makes it reachable from the popup/driver. Fix: validate
  the muster's target (exists, hostile, in range) in handle_response's muster arm and retire
  with a reason, as the last_stand arm now does.

F6 — P4 — THE SLICE'S PROMOTION PIN IS VACUOUS FOR ITS TITLE.
  Repro: tree_mut2 = snapshot with `response["pending_interrupt"] = awaiting` and
  `response["requires_input"] = True` deleted from _include_command_strategic_reports:
  test_the_end_turn_response_promotes_it_for_headless_clients stays GREEN (class 5/5, whole
  slice file 61/61). Its fixture sets mack.strength=0 so the row is `retired` and it never reads
  reply["pending_interrupt"]. (The promotion itself works — p2 §A measured
  pending_interrupt={last_stand/Massena}, requires_input=True.) Fix: add a live-enemy arm
  asserting the promoted key.

F7 — P4 — parser refusals pre-empt the gate's copy.
  Repro: p1.out.txt: 'Massena, cut your way out' / 'break through' / 'surrender' / 'escape to
  Normandy' -> "Might you mean 'Massena, scout' or 'Massena, defend'?" — Berthier suggests orders
  the gate will refuse instead of the two answers. Fix: when the addressed marshal holds a
  standalone decision and the parse fails, the clarification names the two answers.

ATTACKS THAT FAILED (the fix held):
  Q1 typed answers: 'fight to the last', 'attempt breakout', 'Massena, attempt a breakout',
  'Massena, fight', 'Massena, break out', 'Massena, escape', 'Massena, stand and fight',
  'Massena, fight Mack' all route through main.py's interrupt route before any executor gate
  (routed=True, ask cleared, rail cleared). The gate refuses the whole tactical family free and
  names both answers: move/move to/attack/wait/defend/recruit/fortify/dig in/drill/form
  square/scout/Massena, retreat. 'Massena, halt' and "cancel Massena's orders" are free and name
  the question (FA-N13). 'Davout, support Massena' executes untouched. unfortify/garrison/build
  reach their own refusals in this fixture (garrison: "too depleted", so the un-gated seam is
  real but harmless below 8,000 men).
  Q2/Q3 lifecycle (p2 §A–§D): the pass-3 row rides strategic_reports AND is promoted;
  tools/playtest_driver._interrupt_report picks fight_to_the_last (first option); /save then
  /load re-attaches the ask with location=Belgium; a second end turn re-emits the SAME unanswered
  question (one standing ask, not a duplicate); the first /strategic_response resolves it and the
  second is refused "no pending interrupt". FA-1 and pass 3 cannot both fire in one end turn:
  turn_manager.end_turn runs the enemy phase BEFORE process_strategic_orders, so a promoted row
  is never stale on arrival. The retired row renders sanely in strategic_report_popup.gd
  ("[ ] Massena (Last stand)" + reason; the log line is the same text). p2 §F also confirmed
  the retirement firing live ("Mack has drawn off to Lyon") with the rail cleared.
  Q4 last_stand_is_live (p3): the real producer stores the marshals-dict KEY and location
  (ArchdukeCharles/Belgium) and get_marshal resolves it; enemy captured BY FRANCE, peace, the
  marshal teleported, enemy two hops off, enemy destroyed, missing location (tolerated), a
  900-man stub (live) all answer correctly with the right reason; capture_marshal clears ask +
  rail; pass 3 clears a 0-strength uncaptured survivor + rail; a second attacker of ANOTHER nation
  resolves FA-1 (captor = Russia); a reinforced marshal's stale ask retires "the road has
  opened". Only a hand-authored display-form key ("Archduke Charles") retires as "no longer
  stands" — no producer writes that. An autonomous marshal hits the autonomy refusal first (fine).
  Q7 pins: tests/test_pc0_interrupt_router_guards.py, test_wo_slice18_answer_finds_its_question.py
  and test_strategic_executor.py::TestCancelCommand are green on the snapshot AND green with all
  three levers OFF (71/71) — insensitive to the slice, not vacuous (they pin behaviour the slice
  never touched; the slice file goes 18 red under the same flip, so its own pins bind — except F6).
  Also checked: capture_marshal sets pending_interrupt=None directly, so a captured marshal never
  carries an ask into main.py's per-marshal interrupt route; the auto-advance path copies
  strategic_reports, so promotion covers it too.

ONE-LINE SUMMARY: the lifecycle plumbing (pass 3 -> promotion -> driver/popup -> /save -> /load ->
answer -> retire) is sound; the gate is not — it was placed under a predicate that excludes the
strategic commands the fix names as its own measured defect, and the un-addressed retreat family
and charge walk around it, one of them for free.
