# NEXT SESSION PROMPT — Row WO, Slice 1 "The Instrument" (+ 1b)

> Overwritten each time a session hands off. Paste the block below as the
> opening message of a fresh session. Current hand-off: August 21, 2026,
> master `4c265d9`.

---

Build **slice 1 (WO-H "The Instrument")** and then **slice 1b (the re-run)**
of the Weird-Outcomes program.

**Read first, in this order:**
1. `docs/WEIRD_OUTCOMES_SPEC.md` — the build contract, AUTHORITATIVE. Your
   scope is §3 slice 1 + slice 1b, verbatim. §2 is the verified seam record
   (trust its line numbers over any other doc); §6 is the never-do list.
2. `docs/PLAYTESTING.md` — the harness doc this slice amends.
3. `docs/BUG_FIXES.md` §Weird-Outcomes — rows WO-H1/H2/H3 and the Aug-21
   verification block (WO-H3's precision correction matters: the driver DOES
   answer a bare-`True` capture prompt; it loses the sibling `capture_data`).
4. Context only, never re-open: the gate record
   `docs/audits/WO_EVAL_2026_08_17.md` §6.

**Scope — zero production code.** Everything lands in `tools/` and `docs/`;
`backend/` is untouched. The ten contract items, from spec §3 slice 1:

1. `_option_id` widened to `id/choice/keyword/action/command/value` — never
   `label`.
2. Bare-`True` `pending_capture_choice` → read the sibling `capture_data`
   payload WITH its `dialogue_id`; answer the ESTATE stage with a valid
   token (the measured wedge: `"plunder"` to the estate stage is refused
   without clearing and blocks the rest of the campaign).
3. `battles` counted from `jealousy_attacks[*]` (`turn_manager.py:405-415`)
   AND every enemy-phase battle row.
4. An `awaiting_clarification` arm — the driver reads `response["state"]`
   and answers by stated, logged policy.
5. An `envoy_digest` arm on `POST /mailbox/respond` — default `decline`,
   now explicit and counted.
6. Determinism: module RNG seeded at every turn boundary
   (`random.seed(sha256(f"{seed}:{turn}"))` or equivalent, recorded in
   `meta.json`). Sufficiency is established — backend has ZERO
   `random.Random()` instances (spec §2 H-1). **PYTHONHASHSEED must be
   pinned too**: re-exec the driver with `PYTHONHASHSEED=0` when unset and
   record the value in `meta.json` (the eval omitted this; the spec added
   it — an "instrument fixed" claim without it is still nondeterministic).
7. Mode scope in `PLAYTESTING.md`: determinism = Mode A only; `--http`
   digests carry a nondeterministic banner in `meta.json`.
8. A `--archive` flag copying `digest.md` + `meta.json` to
   `docs/audits/playtest_digests/<run-name>/` (committed). Memos may only
   cite archived digests; archive the runs the WO memos cite retroactively.
9. `PLAYTESTING.md` *Known-bad digests* gains WO-H1/H2/H3 + run-to-run
   nondeterminism + the method rule (a passing in-process suite is vacuous
   evidence for `BASELINE_SERIES`; byte-identity claims need a real
   source-edit run through `_run_series_subprocess`).
10. Correct the falsified *"causally inert"* refutation on the NPC harness
    row in `BUG_FIXES.md` §Napoleon Campaign (WO-H1 proved it load-bearing).

**Hard rules (spec §6):** no `random.seed` in `backend/` production code
(never-do 13 — it would collide with the BASELINE runner's own discipline);
the driver KEEPS executing typed diplomatic verbs (never-do 12 / eval §7.12 —
gating them in the driver deletes diplomacy from every future unattended
evaluation); do not match option labels.

**Done when (spec §3 slice 1):** a run answers an estate prompt without
wedging; `capture_choice[estate]` appears in a digest for the first time;
declare-war ceremonies declare (the A/B was `0 → 8` in 8 turns); two
invocations of the same script at the same seed produce identical
`provinces`/`treasury` series; `meta.json` records the RNG scheme +
PYTHONHASHSEED; the archived-digest directory exists with the cited runs.

**Then slice 1b (0.25, machine time), protocol verbatim from the spec:**
each committed `weird_*.json` arm runs 3 seeds (`historical` + 2 banded) ×
3 repeats on the fixed driver. Per-arm median final provinces + min–max.
**The funnel claim STANDS only if the worst fighting-arm median exceeds the
best non-military-arm median AND the bands do not overlap** — otherwise the
STATUS/`DESIGN_REFINEMENT` funnel sentence is formally withdrawn and G2(b)
(`BUILDING_SLOT_LIMITS["town"] = 1`) stays shelved. A wedged variance-seed
arm reports `blocked`, never silently dropped. Results = an addendum table
in `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md` + a STATUS line +
the G2(b) shelf decision answered.

**Landing discipline:** work directly on master; the pre-commit hook runs
ruff + the full suite (green at hand-off: 18,178/3). Update: the spec (✅
landing record on §3 slices 1/1b), `STATUS.md` top entry, `BUG_FIXES.md`
(WO-H1/H2/H3 → FIXED), `PLAYTESTING.md`. Commit as
`harness(wo): slice 1 — the instrument ...` and push. Overwrite this file
with the next hand-off (slice 2 WO-N "The Names" — unless the user pulls
slice 13, the Trojan Corridor P1, forward; that option is theirs alone).
