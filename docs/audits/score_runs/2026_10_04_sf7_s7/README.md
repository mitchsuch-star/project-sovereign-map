# Score Finish Step 7 slice 7 — the evidence (October 4, 2026)

The name census (`tools/_name_census.py`, `tools/playtest_driver.py --name-census`),
historical seed, 40 turns each:

| arm | script | pre-slice `ca4192a1` | slice 7 |
|---|---|---|---|
| CMD-H | `tools/playtest_scripts/commanded_full40.json` (`--diplomacy accept`) | `s7b-names-cmdh/` — FAIL, 68 leaks | `s7-names-cmdh/` — PASS, 0 leaks (771 responses, 844,236 strings, 2,452 with the display name) |
| the Jena road | `tools/playtest_scripts/dc_jena_road.json` | `s7b-names-jena/` — FAIL, 96 leaks | `s7-names-jena/` — PASS, 0 leaks (556 responses, 597,849 strings, 1,821) |

The pre-slice arms ran the slice's census and driver over the pre-slice backend
(a worktree at `ca4192a1` with `tools/_name_census.py` and `tools/playtest_driver.py`
copied in), so the instrument is the same on both sides.

`s7-jena/` — SF5-X3's done-when on the Jena road arm: the capture dispatch reads
"Sire — General Teulie has been taken. Austria holds him prisoner."
