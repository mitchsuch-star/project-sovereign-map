# NEXT SESSION PROMPT — Row WO, Slice 4 "The Capital Speaks" (+WO-11)

> Overwritten each time a session hands off. Paste the block below as the
> opening message of a fresh session. Current hand-off: August 21, 2026 —
> slices **15** ("The Capture Question Holds") and **16** ("The Objection
> Channel Pays Honestly") both LANDED that day, on top of 1/1b/2/3/13/7.
> Landing records = `docs/WEIRD_OUTCOMES_SPEC.md` §3, per slice.
>
> **The row's three hand-verified P1s (WO-17, WO-21, WO-22) are now all
> closed.** The user-directed lift that pulled 15 and 16 ahead of the
> legibility work is spent; §5's blessed order resumes from slice 4, and the
> remaining queue is written at the bottom of this file.
>
> **Three visual sign-offs are owed and none has been seen on screen:**
> slice 7's Berthier redirect line + its ⚜ Cabinet link, the wizard opening
> from that link, and slice 15's `/load` capture-modal raise. All three are
> client-side; every backend half was verified over HTTP or by probe.

---

Build **slice 4 ("The Capital Speaks")** of the Weird-Outcomes program —
WO-D6 plus WO-11 in the same edit. Then, if the session has room, **slice 5
("Berthier Names the Peace")**, which is est 0.3 and touches one strict
inequality.

**Read first, in this order:**
1. `docs/WEIRD_OUTCOMES_SPEC.md` §3 slice 4 — the six-point contract,
   verbatim, AUTHORITATIVE, and its "Done when". Note point 1 carries a
   correction the eval never made (the top of the weight table) and point 6
   explicitly pushes `own_mauled` to slice 12.
2. `docs/BUG_FIXES.md` §Weird-Outcomes row **WO-11**, and
   `docs/DESIGN_REFINEMENT.md` §Weird-Outcomes **WO-D6**.
3. `docs/WEIRD_OUTCOMES_SPEC.md` §2 D-10 and D-15 — the two pins the naive
   version of this slice breaks.

**The defect in one breath:** the fall of the player's own capital has no
voice of its own. Paris can be crowded off its own dispatch by three
ordinary `home_captured` rows; an ALLY liberating Paris fires the wound
anyway (the direction guard the sibling arm at `dispatch.py:435` carries is
missing on both classes — that is WO-11); and the Gazette captions the loss
in the victor's words.

**Harness:** dispatch is display. M1–M7 and `BASELINE_SERIES` are
structurally unreachable here (the weights are documented "display only,
tunable freely"), and the slice touches zero `.gd` and zero serialized
fields — **but say "measured", not "predicted", and run them.** Slice 15
predicted the series could not move and it moved: the ambient board's France
IS `world.player_nation`, so anything gated on the player nation is live
there. The spec's §5 harness paragraph now carries that amendment.

**Landing discipline:** work directly on master; the pre-commit hook runs
ruff + the full suite (green at hand-off: **18,347/3**). Update: the spec
(✅ landing record on §3 slice 4), `STATUS.md` top entry, `BUG_FIXES.md`
WO-11 → FIXED and the WO-D6 design row → disposed. Commit as
`fix(wo): slice 4 — the capital speaks …` and push. Overwrite this file with
the next hand-off (slice 5 if not done, else slice 6).

**A method note this row has now earned four times, and the correction that
finally worked.** Every review round so far has found that the slice's OWN
tests were the weak point, not the code: slice 13's census pin was blind to
three relocation seams; slice 7's drift pin never parsed anything while its
docstring claimed it did; slice 15's first sweep found two INERT pins, both
the tests' fault; and slice 16 found **two existing pins in the suite that
had never asserted anything** — each wrapped in `if result.get("success"):`
around an action id the dispatch has no arm for — which are precisely the
pins that should have caught the AP double-charge it fixed. Before trusting
a pin, ask what it would fail on, then break the code deliberately and watch
it fail. **A mutation sweep is cheap and has been worth its cost every time**
(`tools/mutation_sweep.py`, `tools/_sweep_wo1{5,6}.json` for the shape).

**And the review-fleet correction that paid off in slice 16:** point the
fleet at a **committed SHA with a clean tree**, not a tree you are editing.
Slice 15's refuters spent part of their budget re-discovering the author's
own uncommitted diff and twice reported "already fixed" for work committed
nowhere. Slice 16 committed first, and its refuters caught a wrong probe
before it reached the code.

**Standing context:** **slice 7 retired typed diplomacy** — the terminal
redirects the whole diplomatic verb family to the F1 Cabinet, so do NOT add
a typed diplomatic sentence to a test, a tutorial suggest chip, or a playtest
script expecting it to execute through the client (raw HTTP and the playtest
driver still type diplomacy by design). Its drift pin
(`test_wo_slice7_cabinet_door.py`) MIRRORS the mock parser's diplomatic
funnel: if you add or change a diplomatic keyword in
`llm_client._parse_command`, the mirror in `main.gd` must gain it too. Slice
13's two census pins bind `can_enter_territory` / `passable_for` call shapes;
its review already gave the movement law to three census-invisible relocation
seams, **so slice 17's WO-24 scope is the CHARGE/auto-charge family only.**
Slice 15 added a **one-writer census** over `pending_capture_choice` and a
**blocking-state surface census** keyed on the client's modal route table —
if you add a modal route or a `pending_*` field, expect to classify it.
Slice 16 added a **dispatch-coverage census**: an objection option whose
`action` the post-objection dispatch cannot route will red it. The G2(b)
shelf decision stands (1b addendum); the playtest driver is deterministic
(Mode A/mock) and `--archive` is the citation rule (`docs/PLAYTESTING.md`);
never set `PYTHONIOENCODING` when running the tests (it fakes 6
subprocess-test errors — the ambient shell may have it exported; clear it
first).

**The queue after this slice** (§5 order, the P1 lift now spent): **4** → 5
"Berthier Names the Peace" → 6 "The Admiralty Speaks Plainly" → 8 "The Panel
States Its Terms" → 9 the courting cap → 10 the enemy-direction gate → 17 the
frontier halts the charge (charge family only) → 11 the typed-route residue
(smaller now — slice 7 covers the player surface) → 12 the copy sweep → 14
"The Clock and the Flag". **The row is DONE when** all seventeen have landed
with their done-when lines green, `BUG_FIXES.md` §WO rows WO-1..WO-31 plus
WO-33..WO-37 are all FIXED/CLOSED with pointers to their landing records,
WO-32 is confirmed closed by its owner PC15-10, and the WO-D8/D9/D10/D11
design rows are either gated or explicitly carried.

**Newly filed by slices 15 and 16, needing owners at the row's exit:**
WO-34 (fixed), WO-35 and WO-36 (`pending_objection` / `pending_interrupt` /
`redemption_event` survive a save and raise nothing at load — declared as
KNOWN gaps in slice 15's census pin, so the pin is honest rather than green
by omission), WO-37 (fixed), and WO-D11 (a mid-march auto-secure forfeits an
enemy marshal's estate for nothing — the comment claiming otherwise is
corrected in place).
