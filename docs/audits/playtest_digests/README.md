# Archived playtest digests — the citable record

`tools/playtest_runs/` is gitignored and overwritten; a digest there is a
local artifact, not evidence. **A memo may only cite a digest archived
here** (`playtest_driver.py --archive`, WO-H slice 1, Aug 21 2026). Each
directory holds `digest.md` + `meta.json` — never the raw jsonl.

## Provenance notes

- The `weird-*` and `weird_longquiet` directories are the **original
  Aug-16, 2026 weird-campaign digests** cited by
  `docs/audits/PLAYTEST_WEIRD_OUTCOMES_2026_08_16.md` and
  `docs/audits/WO_EVAL_2026_08_17.md`, archived retroactively on
  Aug 21, 2026. ⚠ They predate the instrument fixes — read
  `docs/PLAYTESTING.md` §Known-bad digests before trusting any number in
  them (option-id blindness, blind battle counter, estate wedge,
  unseeded RNG).
- ⚠ **`weird-tyrant` and `weird-world-burns` are NOT the originals.** The
  Aug-16 originals were destroyed before archiving by the slice-1
  acceptance re-runs (the script's `name` key silently overrode `--name`
  and `--fresh` deleted the dirs — the precedence defect fixed in the
  same landing). These two directories hold the **Aug-21 fixed-driver
  re-runs** (their `meta.json` carries the `rng` block the originals
  lacked — that is the marking).
- The `1b-*` directories and `wo_1b_results.json` are the **slice-1b
  sweep** (10 arms × 3 seeds × 3 repeats on the fixed driver; runner =
  `tools/wo_1b_sweep.py`); the addendum table in the weird-outcomes memo
  is derived from `wo_1b_results.json`. Mock (arm, seed) repeat-triples
  are byte-identical (the determinism proof), so one representative
  repeat per (arm, seed) is archived rather than all three.
