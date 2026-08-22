# NEXT SESSION PROMPT — Row WO: validate the designs, then build the WO-35/36/38 slice

> Overwritten each time a session hands off. Paste the block below as the
> opening message of a fresh session. Current hand-off: August 21, 2026 —
> slices **15** and **16** landed that day (the row's three hand-verified P1s
> are closed), and the session then cleared row WO's **exit items**: the
> visual-sign-off evidence is captured, WO-D7..D11 are carried under hard
> contracts, and WO-35/36 were verified, spec'd and **deliberately not
> built**.
>
> **Read the user's instruction for this session literally: make sure the
> designs are good BEFORE doing the next slice.** There is now a concrete
> docket to validate, not a vague review.

---

**Do these two things, in this order.**

## 1. Validate the design dispositions (first, before any code)

Three things were disposed on August 21 without a user gate, and the user
asked this session to check them:

1. **`docs/DESIGN_REFINEMENT.md` §WO-D7..D11 CARRY CONTRACTS** — five design
   rows given an owner spec/row, landing slice, completion definition and
   behaviour test each. Two were SPLIT (WO-D10's refusal copy went into
   **slice 12's contract**; WO-D9's correctness half is already closed by
   slice 16). **Exactly one is GATE-PENDING — WO-D9**, the objection
   economy's shape, with a recommended default that costs one call:
   `authority.get_trust_gain_modifier` exists, is applied at exactly one seam
   (`vindication.py`), and is wired to nothing on the objection path, so the
   UI shows a damper no objection ever pays. **Put WO-D9 to the user** with
   that recommendation; the other four need only a sanity read.
2. **The three visual sign-offs** — evidence captured, sign-off NOT given.
   `docs/audits/WO_SIGNOFF_{1_CABINET_REDIRECT,2_WIZARD_FROM_LINK,3_LOAD_CAPTURE}_2026_08_21.png`,
   harness `tools/wo_signoff_screenshot.gd` (boots the REAL `main.tscn`
   against `SOVEREIGN_PORT=8006` and drives the client's own entry points).
   **A captured screenshot is not a sign-off** — the row's DoD says so. Ask
   the user to look, or re-run the harness if they want a different frame.
3. **The WO-35/36/38 build order** in
   `docs/audits/WO_35_36_38_VERIFICATION_2026_08_21.md`. Read it before
   touching anything; it contradicts both filed rows.

## 2. Build the WO-35 / WO-36 / WO-38 slice

**Read first:** the memo above (authoritative), then `docs/BUG_FIXES.md` rows
**WO-35, WO-36, WO-38, WO-39, WO-40** — all five now carry the corrected
text, not the original filed claims.

**The defect in one breath:** a stale strategic objection hijacks the answer
to a *different* marshal's objection — measured, answering "trust" with Ney's
objection on screen gave **Davout +8 trust and fortified Davout** — and a
save/load is its delivery mechanism, because a restored objection raises no
modal at all so the player cannot know the slot is occupied.

**Build order (from the memo; it is not the order the rows imply):**

1. **WO-39 FIRST — it blocks everything else.** `main.gd`
   `_on_commitment_paradox_choice` disables input unconditionally before a
   two-branch send; ESC cannot open the pause menu over a visible modal, so a
   third emitted choice would be unrecoverable. One line. Any world-swap
   modal raise puts weight on it.
2. **WO-38 (the P1).** Decide between: the TACTICAL objection wins when both
   are pending (it is the one that blocks commands, so it is the one the
   player is being told to answer — a one-condition reorder at
   `meta_executor`'s router), and/or an unanswered strategic objection lapses
   at the turn boundary. Slice 16 established the order is never created at
   objection time, so a lapse loses nothing that was not already lost — but
   it must be TOLD. Recommend both; the reorder alone leaves a narrower
   version of the hijack.
3. **WO-35's `pending_interrupt` half only.** It is the one key that earns a
   `/load` attach and the memo audits it safe. **Do NOT attach
   `pending_objection` without a tactical/strategic discriminator** — the
   saved dict records none, and the strategic arm would render a modal with
   no buttons and no ESC exit. That is the filed fix, and it is a soft-lock.
4. **WO-36 + WO-40 together, client-side, zero backend change.** Reset
   `_redemption_recheck_turn` (and the sibling stashes) in
   `_reset_frontend_state_for_world_swap`, beside the `_envoy_digest_shown_turn`
   line IGR-F added for the identical reason. Give `redemption_event` a
   FOURTH census classification ("recovered by poll") rather than moving it
   to `LOAD_REATTACHED`.

**Harness:** measure, do not predict. Slice 15 moved `BASELINE_SERIES` on a
"player-gated therefore inert" prediction, because the ambient board's France
IS `world.player_nation`. Run `tests/test_ai_intent_threat_migration.py`
(real subprocess) and `tests/test_combat_sweep_metrics.py`.

**Landing discipline:** work directly on master; the pre-commit hook runs
ruff + the full suite (green at hand-off: **18,347/3**). `.gd` is touched, so
the XR-1 rule applies: parse harness EXIT=0 plus a war-room boot smoke
grepping `SCRIPT ERROR` (`--path … res://scenes/main.tscn`; a plain boot only
loads the menu and proves nothing). Then **slice 4 "The Capital Speaks"** is
next in §5 order.

**The method notes this row has earned, and which keep paying:**

- **Point review fleets at a COMMITTED SHA with a clean tree.** Slice 15's
  refuters spent budget re-discovering the author's own uncommitted diff;
  slice 16 and this verification committed first and caught two wrong fixes
  before they reached the code.
- **Mutation-sweep every pin** (`tools/mutation_sweep.py`;
  `tools/_sweep_wo1{5,6}.json` for the shape). Four rounds running, the
  slice's OWN tests were the weak point — slice 16 found two pins already in
  the suite that had never asserted anything.
- **Verify the MECHANISM, not just the outcome.** Four of the last six filed
  rows had the right outcome and the wrong mechanism, and following the
  prescribed fix would have been a no-op, unbuildable, harmful, or a
  soft-lock. WO-35 is the sharpest example yet.

**Standing context:** slice 7 retired typed diplomacy (do not add a typed
diplomatic sentence to a test, tutorial chip or playtest script expecting it
to execute through the client; its drift pin mirrors the mock parser's
diplomatic funnel). Slice 13's census pins bind `can_enter_territory` /
`passable_for` call shapes, and slice 17's WO-24 scope is the CHARGE family
only. Slice 15 added a one-writer census over `pending_capture_choice` and a
blocking-state surface census keyed on the client's modal route table — **the
WO-35 build will have to re-classify keys in it**. Slice 16 added a
dispatch-coverage census. The playtest driver is deterministic (Mode A/mock)
and `--archive` is the citation rule (`docs/PLAYTESTING.md`). Never set
`PYTHONIOENCODING` when running the tests — it fakes six subprocess-test
errors, and the ambient shell may have it exported; clear it first.

**The queue after this slice** (§5 order): **4** "The Capital Speaks" (+WO-11)
→ 5 → 6 → 8 → 9 → 10 → 17 → 11 → 12 → 14. **The row is DONE when** all
seventeen slices have landed with their done-when lines green,
`BUG_FIXES.md` §WO rows WO-1..WO-31 plus WO-33..WO-40 are all FIXED/CLOSED
with pointers to landing records, WO-32 is confirmed closed by its owner
PC15-10, the WO-D7..D11 contracts are discharged, and **the user has signed
the three visual sign-offs** — the row does not close on frames nobody has
looked at.
