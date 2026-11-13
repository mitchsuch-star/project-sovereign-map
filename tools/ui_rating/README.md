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
5. **Pairs**: `python -I make_pairs.py <before_mapping.json> <after_mapping.json> docs/audits/<dir> [<prefix>]`
   writes the before / after composites (`<prefix>` names the files: UIGILT2 by default, Session UI-3's UIGILT3).

Session UI-2's readings: baseline (HEAD `20ee32ff`) 7 / 7 / 7, mean 6.77; after 7 / 7 / 7, mean 6.93 — the record and
what holds the frames at 7 are `docs/UI_VISUAL_FOUNDATION_SPEC.md` §10; the baseline readers' digest is
`BASELINE_DIGEST_UI2.md`.

Session UI-3's readings (`scores_ui3.py`, its BASE UI-2's after reading): interim (two readers; a third set aside) mean 6.65; final 7 / 7 / 7, mean 7.00 — the record is
`docs/UI_VISUAL_FOUNDATION_SPEC.md` §11. Two traps it paid for: a reader's labels can slip a frame (its F15 describing
F16, an F30 that does not exist) — check each report's lines against the frames' content before tabulating, and set a
slipped report aside rather than re-map it; shoot the physical frames with the same `--date` tag as the scaled run,
or `make_rating_set.py` finds no war room at 5120.

Session UI-4's readings (`scores_ui4.py`, its BASE UI-3's final reading): interim 7 / 7 / 7, mean 7.06; final 7 / 7 / 7, mean 7.11 (on the 27 frames whose staging never moved, 7.09 → 7.10) — the
record is `docs/UI_VISUAL_FOUNDATION_SPEC.md` §12. From UI-4 on, three frames are shot as the game shows them
(`make_rating_set.STAGED_UI4`: F24 the province panel over the live map, F25 the war detail over the turn-20 war room,
F27 the menu with the war office answering; `--old-stagings` maps them to UI-2's and UI-3's alone shots): report the
score on all 30 frames and on the 27 whose staging never moved (`scores_ui4.py` prints both). One trap it paid for: a
fit diff that compares counts misses a frame whose controls went further off-screen than HEAD's (the same count, a
worse overflow: the end card's buttons wholly below a 450-px view where HEAD's were cut by 20 px) — read the frames as
well as the counts.
