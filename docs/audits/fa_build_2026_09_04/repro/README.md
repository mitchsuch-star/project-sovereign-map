# Reproduction reports — the FA audit build, September 2026

Fourteen read-only reproduction passes, each run BEFORE the slice it belongs
to was written, against the shipped 1805 board with a mock parser. They exist
because the audit's own rows are frequently wrong about their seam, their
magnitude, or their fix: the Sept-2 verification pass measured that **~80% of
rows carry a stale line number, ~44% a wrong `already_filed`, and ~25% a title
that over-reaches its own body**, and six rows carry a `fix_shape` their own
corrected summary rejects.

Every slice built so far that used one of these was corrected by it — usually
in three or four places, twice in ways that changed what got built. They are
committed so the next session does not re-earn ~40 agent-runs of measurement
that is already done.

**Read the report for a row before you read the row.** Where the two disagree,
the report was measured and the row was not.

| report | rows | slice |
|---|---|---|
| `REPRO_G1_the_offer_on_the_desk.md` | FA-4, FA-N4, FA-N15, FA-N17, FA-N18 | 10 ✅ |
| `REPRO_G2_the_offering_side_consents.md` | FA-3 | 10 ✅ |
| `REPRO_G3_the_answer_reaches_the_desk.md` | FA-17, FA-N44 | 10 ✅ |
| `REPRO_G4_the_price_and_the_voice.md` | FA-N16, FA-N43, FA-N45, FA-21 | 10 ✅ / FA-21 → 14 |
| `REPRO_H1_the_briefing_tells_the_truth.md` | FA-2, FA-N19, FA-N74, FA-12, FA-N14, FA-53, FA-38, FA-25, FA-32 | 11 ✅ |
| `REPRO_H2_the_enemy_phase_reads_the_field.md` | FA-23, FA-N21, FA-N33, FA-N75 | 11 ✅ |
| `REPRO_I1_the_road_home_and_the_peace.md` | FA-33, FA-N61, FA-N73 | **12 — next** |
| `REPRO_J1_shipping.md` | FA-29, FA-43, FA-N84, FA-N56, FA-57 | 13 |
| `REPRO_J2_the_garrison_and_the_free_verb.md` | FA-D28, FA-R3 | 14 |
| `REPRO_J3_the_singles.md` | FA-42, FA-N46, FA-N77, FA-31, FA-N76, FA-N78, FA-35 | 14 |
| `REPRO_J4_the_diversion_and_the_recall.md` | FA-S9-D1, FA-R4, FA-S7-D1 | 14 |
| `REPRO_J5_the_instrument.md` | the harness rows | 15 |
| `REPRO_J6_copy_sweep_N.md` | the FA-N P3/P4 remainder | 16 |
| `REPRO_J7_copy_sweep_FA.md` | the FA-n P3/P4 remainder | 16 |

**⚠ The J-series has not been read in detail yet.** G1–G4, H1, H2 and I1 were
read and used; J1–J7 were produced by the same sweep and are unverified
against the tree since. Treat their measurements the way you would treat a
row: reproduce the specific claim you are about to build on.

Line numbers in these reports were accurate on `a1ed5c9d` and are now stale by
eleven slices. **Navigate by the symbol a report names, never by its line.**
