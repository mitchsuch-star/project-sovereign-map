# The blind UI rating (Session UI-2, November 2026)

How the client's UI is scored by blind readers, so the measure can be run again on a later tree and compared.

1. **Shoot** every surface at Interface Scale 1.0 and 2.0 (`tools/iq10_run_captures.py --payload-dir <dir>
   --out-dir <run> --png-dir <run>/frames --scales 1.0,2.0 --date <TAG>`), and the war room at the five physical sizes
   (`--physical --only war_room_boot`).
2. **Build the set**: `python -I make_rating_set.py <run>/frames <phys_run>/frames <TAG> <out>/frames_N` copies the
   30 fixed frames (F01–F30, listed in the script) under neutral names; the name → frame mapping is written beside
   the folder, never inside it.
3. **Read**: three fresh readers (cheaper models), each given ONLY `RUBRIC.md` (frozen November 11, 2026 — do not
   edit it, or the scores stop being comparable) and the 30 frames, with the prompt in `READER_PROMPT.md`.
4. **Score**: per-frame median and spread, per-reader median, the overall median and the mean of the 90 marks
   (`scores_ui2.py` holds Session UI-2's two readings and prints the table).
5. **Pairs**: `python -I make_pairs.py <before_mapping.json> <after_mapping.json> docs/audits/<dir>` writes the
   before / after composites.

Session UI-2's readings: baseline (HEAD `20ee32ff`) 7 / 7 / 7, mean 6.77; after 7 / 7 / 7, mean 6.93 — the record and
what holds the frames at 7 are `docs/UI_VISUAL_FOUNDATION_SPEC.md` §10; the baseline readers' digest is
`BASELINE_DIGEST_UI2.md`.
