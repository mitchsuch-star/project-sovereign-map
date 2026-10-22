# RR6-X3 — "one sighting rule": the slice's arms, read beside SF-RR6's

> October 21, 2026, Pre-Deploy S14b's head. Rules `docs/SYSTEMS_REFERENCE.md` §142; rows `docs/BUG_FIXES.md`
> §RR6 (RR6-X3 … X11) and §UXR-3 (UXR3-F11); pins `tests/test_rr6_x3_one_sighting_rule.py`,
> `tests/test_uxr3_f11_the_titled_tally.py`. **A reading of eight arms, not a score** (5 of 14 pillars exercised).

## What this folder holds

- `arms/` — the eight arms SF-RR6 read (CMD-H, CMD-A, CMD-M, OP, FLD, DL, LAW, VOLTE), driven on the slice's tree
  by `tools/score_run.py run` with the SF-RR6 archive's own argv (`run.json`); VOLTE carries its one-line re-script.
- `checklist.json`, `scores.json`, `census_by_pillar.json`, `findings_rate.json` — `score_run.py check
  --checklist docs/SCORE_CHECKLIST_V1_2.json` on those arms (the readers SF-RR6 left, with RR6-X9's economy C3
  reader and the C4 probe's live row in sight).
- `attribution.json` — `tools/_rr6_x3_arm_attribution.py`: each arm's GAME stream against the SF-RR6 slice archive
  (`../2026_10_21_rr6/slice/`) on the shipped tree, with the rule held down, with RR6-X8 held down, and with both.
  Taken before VOLTE's re-script (its arm parts at the re-scripted line thereafter, by design).

## 1. Who moved, and why

| Arm | GAME vs the SF-RR6 archive | With the rule down | RR6-X8 down alone |
|---|---|---|---|
| CMD-A, CMD-M, OP, DL | equal | equal | equal |
| FLD | parts at turn 7: `Ney, attack Archduke John` asks the pursuit ("Archduke John stands at Provence, three marches off") the store alone refused | equal | parts at turn 7 (the rule's) |
| CMD-H, LAW | parts at turn 7: `Ney, attack Archduke Charles` asks the pursuit (Charles in sight at Piedmont, a label read before he came) | equal | parts at turn 7 (the rule's) |
| VOLTE | as CMD-H before its re-script; re-scripted (turn 7 asks Ney's odds instead of ordering the chase), it parts at that line and re-times by a roll from turn 8 (the refused order had drawn on the objection's dice, the question does not) | — | — |

Every game movement is the rule's line; RR6-X8 moves none; the display changes (the dispatch's live rows at PARTIAL,
the map's STALE ghosts, the status report, the desk's wording, the muster's band) reach no GAME stream.

## 2. The reading, beside SF-RR6's slice (checklist v1.2)

| Item | SF-RR6 slice | This slice | Why |
|---|---|---|---|
| living balance F1 | ✓ (France 25 / 27 / 28) | ✗ (France **9** / 27 / 28) | CMD-H re-timed from turn 7; from turn 20 Bennigsen and Shrapnel walk an undefended France on the lawful road — EG-D2's own shape, RULED keep (October 13): read as the benchmark's scripted France never coming home, never by re-scripting the commanded arm (§4.2) |
| living balance C4 | ✓ (Austria re-declares at 36) | ✗ (no re-declaration after the peaces with Britain, t16, and Russia, t21) | the same re-timed campaign |
| narration C1 | ✓ (worst 4 of 10) | ✗ (`home_captured` 10 of 10 on CMD-H) | a homeland province falls nearly every morning and the page leads with it — event news, the rotation rule's own exemption (EG-D2's narration half); the front page's driven pin exempts it, any other class flooding still fails |
| economy C3 | ✓ | ✓ | before RR6-X9 the moved CMD-H read ✗ — turn 30 quoted 331 and billed 375: two walk-ins under the quote dropped the Emperor's grip under 70 and the "grip falters" term billed +50 rate points; the reader now counts the end turn's captures as it counts battles |
| diplomacy C3 | ✓ (the volte-face at 29) | ✓ (at 30) | VOLTE's pursuit had lost the courted peace (0 beats in forty turns); its one-line re-script restores it (RS-27's pin) |

Narration's range on these arms: 7.50–8.50 → 7.00–8.00; nothing else exercised moves. Seeded paths, not laws:
the readings are recorded per seed and claimed as no defect of the rule.
