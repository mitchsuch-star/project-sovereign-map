# The ambient baseline row IQ-1 had been missing

`docs/IMPROVEMENT_QUEUE_SPEC.md` §0.6 recorded, as an instrument caveat, that
there was **no post-SW-0 archived AMBIENT arm** — so the ambient half of row
IQ-1's completion definition had no baseline at all, and §0.5.3 named taking one
as an IQ1-5 landing. It is taken here, because IQ1-3's own measurement needed
something to say about the arm it does NOT grade on.

    40 turns · seed `historical` · no script · no diplomacy dial
    turn 40: 5 provinces · 2,593 gold · army 105,000 · 23 treasury falls
    treasury peak ≈ 24,682 around turns 15-20, then down

**⚠ READ THE 23 TREASURY FALLS CORRECTLY.** They are **collapse, not spending**:
an unattended France is being overrun (the FA-D27 shape), and by turn 40 holds
five provinces. That is exactly why completion item (i) had to be re-stated in
§0.7 — "the treasury is not monotonic" is satisfied here for the wrong reason,
and a predicate that accepted it would score an annihilated empire as a
converted one.

So this arm's job is **exclusion, not scoring**. IQ1-3's acceptance predicate
declines to grade it (`the_chest_is_convertible`'s `GROSS_FLOOR` and the
growing-chest guard), and `test_a_collapsing_arm_is_excluded_not_scored` plus
`test_the_gross_floor_rejects_a_rump_that_converted_everything` pin that in both
directions.

Archived WITH its `digest.jsonl`, which `--archive` now carries (IQ1-3D) — the
per-nation `purses` and `net_residual` live only there.
