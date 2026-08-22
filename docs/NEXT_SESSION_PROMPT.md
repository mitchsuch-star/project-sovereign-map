# NEXT SESSION PROMPT — Row WO, Slice 15 "The Capture Question Holds" (P1)

> Overwritten each time a session hands off. Paste the block below as the
> opening message of a fresh session. Current hand-off: August 21, 2026 —
> slices 13 ("The Corridor Has a Direction") and 7 ("The Cabinet Is The
> Only Door") LANDED that day on top of 1/1b/2/3 (landing records =
> `docs/WEIRD_OUTCOMES_SPEC.md` §3, per slice; the 1b addendum =
> `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md` §9).
>
> **The order changed by user direction, and this is the second time:**
> the two remaining hand-verified P1s (slices 15 and 16) are pulled ahead
> of the legibility/copy slices 4/5/6/8, on the same reasoning that moved
> slice 7 — clear the dangerous defects before the polish. §5's blessed
> order is otherwise intact and the remaining queue is written at the
> bottom of this file.
>
> **Two visual sign-offs are owed and neither has been seen on screen:**
> slice 7's Berthier redirect line + its ⚜ Cabinet link, and the wizard
> opening from that link. Both are client-side; the backend halves were
> live-verified over HTTP.

---

Build **slice 15 ("The Capture Question Holds")** of the Weird-Outcomes
program — the hand-verified P1 WO-22 and the four sibling holes in the
same lifecycle. Then, if the session has room, **slice 16 ("The
Objection Channel Pays Honestly")**, the other P1 (WO-21 + WO-23).

**Read first, in this order:**
1. `docs/WEIRD_OUTCOMES_SPEC.md` §3 slice 15 — the five-point contract,
   verbatim, AUTHORITATIVE, and its "Done when". §6 never-do 19 binds
   it (**do not double-build WO-32** — the vassal-rebellion popup's
   refusal-path destruction is PC15-10's, owned by
   `PETITION_POPUP_REVISIT_SPEC.md`; this row only CHECKS it at exit).
2. `docs/BUG_FIXES.md` §Weird-Outcomes rows **WO-22, WO-26, WO-27,
   WO-29, WO-30** — the filed seams with line numbers.
3. `docs/WEIRD_OUTCOMES_SPEC.md` §3 slice 16, so you can see whether the
   two fit in one session.

**The defect in one breath:** the single-slot `pending_capture_choice`
can be created, crossed, clobbered, misapplied and dropped without the
player ever being told. The headline (WO-22, P1): the auto-end-turn
defer at `executor.py:1966` checks only
`dialogue_manager.has_current_turn_offers()` and never
`pending_capture_choice`, while the TYPED `end turn` path blocks on it
(`:597-602`) — so a last-AP attack that captures auto-advances across
the unanswered question, the enemy phase can retake the province, and
the answer then dies on the holder-re-validation lapse with the plunder
gold (`income × 4`) silently forfeited.

**Contract (spec slice 15, five points, verbatim there):** WO-22 — the
auto-advance defers on `pending_capture_choice` exactly as it defers on
unanswered envoys, with the same explicit notice · WO-26 — the
attack-capture site (`combat_executor.py:7853`) and occupation-completion
site (`world_state.py:3937-3938`) are BARE writes to the single slot;
extend the PF-3 save/restore guard the move path already carries
(`movement_executor.py:546-551/589`) to all three producers · WO-27 —
the dotation prune (`world_state.py:5891-5896`) gains the
`_capture_choice_pending` carve-out its three siblings have · WO-29 —
thread `dialogue_id` onto the TYPED capture answer (`main.py:2263-2264`)
so the W6-0 stale guard stops being inert on that path · WO-30 — add the
capture entry to `PopupQueue.RESPONSE_KEYS` so `/load` re-raises the
modal, **and a census pin so the next new slot cannot silently drop**
(the queue's own `to_dict`/`from_dict` are dead code — it round-trips via
hand-enumerated keys, which is the structural cause).

**Done when:** a last-AP capture defers the auto-advance with the notice;
a second capture in the same strategic loop cannot clobber an unanswered
first; the estate *respect* answer is never a paid no-op across a turn
boundary; a typed answer with a stale id refuses; a loaded save re-raises
the capture modal; **the PF-3 pin
(`test_pf3_uncontested_occupation.py:224-248`) stays green.**

**Harness impact:** WO-26 touches capture producers the AI reaches, so
**prove `BASELINE_SERIES` by a real subprocess run** (`_run_series_
subprocess` — a passing in-process suite is vacuous for that pin) and run
M1–M7. If either moves, take a flip-attributed re-record and say which
lever caused it.

**Landing discipline:** work directly on master; the pre-commit hook runs
ruff + the full suite (green at hand-off: **18,297/3**). Update: the spec
(✅ landing record on §3 slice 15), `STATUS.md` top entry, `BUG_FIXES.md`
WO-22/26/27/29/30 → FIXED. Commit as
`fix(wo): slice 15 — the capture question holds …` and push. Overwrite
this file with the next hand-off (slice 16 if not done, else slice 4).

**A method note this row has now earned twice.** Both review rounds this
session found that the slice's OWN tests were the weak point, not the
code — slice 13's census pin was blind to three relocation seams because
it censused *calls* and those seams make none; slice 7's drift pin never
parsed anything while its docstring claimed it did, hiding eight leaks
behind a green 30/30. Before trusting a pin here, ask what it would fail
on, then break the code deliberately and watch it fail. A mutation sweep
is cheap and both rounds were worth their cost.

**Standing context:** **slice 7 retired typed diplomacy** — the terminal
redirects the whole diplomatic verb family to the F1 Cabinet, so do NOT
add a typed diplomatic sentence to a test, a tutorial suggest chip, or a
playtest script expecting it to execute through the client (raw HTTP and
the playtest driver still type diplomacy by design). Its drift pin
(`test_wo_slice7_cabinet_door.py`) is a MIRROR of the mock parser's
diplomatic funnel: **if you add or change a diplomatic keyword in
`llm_client._parse_command`, the mirror in `main.gd` must gain it too**,
and `TestTheMirrorAgreesWithTheParser` will red until it does. Slice 13
added TWO census pins
(`test_wo_slice13_corridor_direction.py::TestTheCensusPin`) — any new
`can_enter_territory` call must pass `mover_location=` (relocation) or be
consciously audited into the allowlist, and any `passable_for` pathfind
must start at `marshal.location`; its review round already gave the
movement law to three census-invisible relocation seams (bare-`attack`
move-toward, explicit-destination retreat, the 2-tile cavalry connector),
**so slice 17's WO-24 scope is the CHARGE/auto-charge family only — do
not re-fix those three.** The G2(b) shelf decision stands (1b addendum —
read it before touching anything funnel-adjacent); the playtest driver is
deterministic (Mode A/mock) and `--archive` is the citation rule
(`docs/PLAYTESTING.md`); never set `PYTHONIOENCODING` when running the
tests (it fakes 6 subprocess-test errors — the ambient shell may have it
exported; clear it first).

**The queue after this slice** (§5 order, with the user-directed P1 lift
applied): **15 → 16** → 4 "The Capital Speaks" (+WO-11) → 5 "Berthier
Names the Peace" → 6 "The Admiralty Speaks Plainly" → 8 "The Panel States
Its Terms" → 9 the courting cap → 10 the enemy-direction gate → 17 the
frontier halts the charge (charge family only) → 11 the typed-route
residue (smaller now — slice 7 covers the player surface) → 12 the copy
sweep → 14 "The Clock and the Flag". **The row is DONE when** all
seventeen have landed with their done-when lines green, `BUG_FIXES.md`
§WO rows WO-1..WO-33 are all FIXED/CLOSED with pointers to their landing
records, WO-32 is confirmed closed by its owner PC15-10, and the WO-D8/
D9/D10 design rows are either gated or explicitly carried.
