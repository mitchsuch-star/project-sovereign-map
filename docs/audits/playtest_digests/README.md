# Archived playtest digests — the citable record

`tools/playtest_runs/` is gitignored and overwritten; a digest there is a
local artifact, not evidence. **A memo may only cite a digest archived
here** (`playtest_driver.py --archive`, WO-H slice 1, Aug 21 2026). Each
directory holds `digest.md` + `meta.json`, and since IQ1-3D (September
13, 2026) `digest.jsonl` too.

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
- **`iq8-cmd-historical`, `iq8-cmd-austerlitz`, `iq8-cmd-marengo`** (September
  17, 2026) are the COMMANDED arm (`commanded_full40.json --diplomacy accept`,
  40 turns, `PYTHONHASHSEED=0`) on the IQ-8 tree — the first archives whose
  `meta.json` carries `requested` / `resolved` / `platform` /
  `engine_revision` and the `ap_available` / `ap_spent` / `cmd_refused`
  counters, and the row `docs/PLAYTESTING.md`'s commanded table cites.
- ⚠ **Every archive dated before September 17, 2026 carries a RAW-bytes
  `driver_revision`**; IQ-8 LF-normalised the stamp. Attribute an old one by
  hashing a commit's driver in the line ending of the machine that ran it:
  `cmd-*` / `fix-cmd-*` (Linux, LF) = the driver of `4094eb4a`; `iq7-*`
  (Windows, CRLF) = the driver of `7d10e20c`. None of them records a
  platform, an engine commit or what the world resolved — read the memo that
  cites them for that, and treat a figure with no archive as UNCITABLE.
