# SF-RR6 — "the instrument reads what the player sees": the re-reads and their deltas

> October 21, 2026, Score Finish Step 9 (`docs/SCORE_FINISH_SPEC.md` §3 Step 9, §6 row 23). Rules
> `docs/SYSTEMS_REFERENCE.md` §141; rows `docs/BUG_FIXES.md` §Score Finish Step 8 (SFR-I2, I4, I5, I6, I7),
> §The Economy Audit (EA-2), §The Economy Gate (EG-X4), §RR6 (the siblings); `docs/DESIGN_REFINEMENT.md` EG-D1;
> pins `tests/test_sf_rr6_the_instrument.py`; the checklist `docs/SCORE_CHECKLIST_V1_2.json`.
>
> **The frozen readings stand as measured (§4.4).** Every archive below keeps its `checklist.json`; the corrected
> readers' reading sits BESIDE it as `checklist_v1_2.json` / `scores_v1_2.json` (`tools/score_reread.py`). Nothing
> here is claimed as a score.

## What this folder holds

- `entry/` — the arms the corrected readers read, on the entry tree (`d940b5bc`, the old driver): CMD-H, CMD-A,
  CMD-M, OP, FLD, DL, LAW, VOLTE. `checklist.json` = the frozen readers (checklist v1.1); `checklist_v1_2.json` =
  the v1.2 re-read beside it.
- `slice/` — the same arms on the slice's tree (the new driver, the re-staged DL script, EG-X4's store).
  `checklist_v1_1.json` = the frozen readers on these arms; `checklist.json` = the v1.2 reading.
- `attribution.json` — `tools/_sf_rr6_arm_attribution.py` over entry → the slice with EG-X4's seam held down →
  the slice as shipped (the seam-down arms are reproducible with the driver's `--seam
  backend.models.world_state:scouted_view_expired=False`).
- Beside this folder: `../2026_09_29_c20d5bba/` (the baseline), `../2026_10_05_sfr/` (the final reading) and
  `../2026_10_05_econ_gate/` (the gate's, EG-X4's own) each gained `checklist_v1_2.json` and `scores_v1_2.json`.
  `tools/_sf_rr6_series_arms_final.json` holds the `BASELINE_SERIES` attribution.

## 1. Every misread, reproduced on the digest that carries it

| Row | Item | The misread, as the archive shows it |
|---|---|---|
| SFR-I7 + I2 | combat C5 | every raw key counted sat in the enemy-phase `message`: 124 (baseline), 46 (final), 37 (gate), 34 (entry); the ⚔ and MUSTER lines carried none |
| SFR-I4 | drama C5 | "Lannes's claim is 8 turns in arrears" carries no "Marshal" — unmeasured on the final reading and at entry; the notice lives in the Unmet Marshals block no digest recorded |
| SFR-I5 | AI C6 | the final reading's CMD-M 11/39: "Prussia has declared war on Hanover", the turn France signed, opened 22 peace turns as war |
| SFR-I6 | combat C4, economy C5 | `Davout, fortify` → "requires 2 actions … only 1 remaining"; the levy → "We do not control Swabia" (final) / "Franconia … foreign ground" (entry) |
| RR6-X1 | first contact C4 | at entry RS-15 asked with actions in hand: "Davout, attack Archduke Charles / Ney, march to Munich" |
| EA-2 | economy F1 | net_residual 0 on every record, by construction (808 on the final reading); the audit's sponsorship, rebuilt on today's boot with EA-1's lever down, reads ✓ |
| EG-X4 | narration C4 | the gate's CMD-M t20: Kutuzov "at Vienna" on the row, "Bohemia" in the store — the STORE stale (Bohemia FULL, `scout`, turn 17, six French corps next door reading it PARTIAL) |
| EG-D1 | AI C1 | 20 / 19 / 19 laws with 0 lapses read ✗ against "13–18" (entry) |

## 2. The deltas — each archive re-read under v1.2 beside its record

"Whose" tells SF-RR6's moves from v1.1's (October 5, 2026), which a v1.2 re-read repeats.

### 2026_09_29_c20d5bba — directional 6.71 over 13/14 → 6.6 over 12/14 (v1.2 re-read)

| Item | Recorded | v1.1 re-read | v1.2 re-read | Whose | The v1.2 evidence |
|---|---|---|---|---|---|
| economy.F1 | ✓ | ✓ | · | SF-RR6 | an archive that predates the chest's measure (EA-2): the driver never read a treasury, so an off-books flow could not be seen — v1's net_residual is zero by construction |
| economy.C5 | ✗ | ✗ | · | SF-RR6 | SCRIPT PRECONDITION (AAR-6, read off the levy's reply): Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.' |
| combat_legibility.C4 | ✗ | ✗ | · | SF-RR6 | SCRIPT PRECONDITION (RS-12, read off the staging line): `Davout, fortify` → Davout cannot fortify while engaged with enemy forces! Enemy present: Mack. Attack or retreat first. |
| combat_legibility.C5 | ✗ | ✗ | ✓ | SF-RR6 | raw keys in the combat text the player sees: 0 {}; not read — the unrendered enemy-phase message of an older digest: 146 {"ArchdukeCharles": 100, "ArchdukeChar": 2, "ArchdukeJohn": 34, "ArchdukeCharl": 2, "ArchdukeCharle": 1, "ArchdukeCh": 3, "KingdomOfItaly": |
| marshal_drama.F1 | ✓ | · | · | v1.1's | the FLAG probe did not write its record |
| marshal_drama.C5 | ✓ | ✓ | · | SF-RR6 | an archive that predates the Unmet Marshals block's record — the notice lives there; erosions seen (every copy of the page read): ['OP Lannes t10', 'CMD-H Lannes t11'] |

Pillar readings: economy 7.00 → 5.75–7.50; combat_legibility 5.50–5.75 → 5.75–6.00; marshal_drama 7.00–8.00 → NOT EXERCISED

### 2026_10_05_sfr — directional 7.5 over 13/14 → 7.5 over 13/14 (v1.2 re-read)

| Item | Recorded | v1.1 re-read | v1.2 re-read | Whose | The v1.2 evidence |
|---|---|---|---|---|---|
| economy.F1 | ✓ | ✓ | · | SF-RR6 | an archive that predates the chest's measure (EA-2): the driver never read a treasury, so an off-books flow could not be seen — v1's net_residual is zero by construction |
| economy.C1 | ✗ | ✓ | ✓ | v1.1's | the Staff enacted at loop 10 (T1: turns 10–15): The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquar |
| economy.C5 | ✗ | ✗ | · | SF-RR6 | SCRIPT PRECONDITION (AAR-6, read off the levy's reply): Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.' |
| combat_legibility.C4 | ✗ | ✗ | · | SF-RR6 | SCRIPT PRECONDITION (RS-12, read off the staging line): `Davout, fortify` → Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining. |
| combat_legibility.C5 | ✗ | ✗ | ✓ | SF-RR6 | raw keys in the combat text the player sees: 0 {}; not read — the unrendered enemy-phase message of an older digest: 65 {"ArchdukeCharles": 36, "ArchdukeJohn": 25, "KingdomOfItaly": 4} |
| marshal_drama.F1 | ✗ | ✓ | ✓ | v1.1's | petition modals 5 (≤ 9) on turns [5, 6, 13, 15, 19], the longest run of consecutive turns 2 (≤ 2), silent losses 0, petition moments 19 |
| ai_aliveness.C5 | ✗ | ✓ | ✓ | v1.1's | 23 acts, no dither in place; excused (moved or fought between): ['CMD-H ArchdukeCharles t8–t11 (Bohemia→Carniola; between: attack@t9, attack@t9, attack@t9, attack@t10)', 'CMD-H ArchdukeCharles t33–t36 (Bohemia→Swabia; between: attack@t34, attack@t34, move@t35, |

Pillar readings: economy 7.00 → 6.00–8.00; combat_legibility 7.00–7.50 → 7.50–8.50; ai_aliveness 7.00 → 7.50

### 2026_10_05_econ_gate — directional 7.43 over 14/14 → 7.43 over 14/14 (v1.2 re-read)

| Item | Recorded | v1.1 re-read | v1.2 re-read | Whose | The v1.2 evidence |
|---|---|---|---|---|---|
| economy.F1 | ✓ | — | · | SF-RR6 | an archive that predates the chest's measure (EA-2): the driver never read a treasury, so an off-books flow could not be seen — v1's net_residual is zero by construction |
| economy.C5 | ✗ | — | · | SF-RR6 | SCRIPT PRECONDITION (AAR-6, read off the levy's reply): Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.' |
| combat_legibility.C4 | ✗ | — | · | SF-RR6 | SCRIPT PRECONDITION (RS-12, read off the staging line): `Davout, fortify` → Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining. |
| combat_legibility.C5 | ✗ | — | ✓ | SF-RR6 | raw keys in the combat text the player sees: 0 {}; not read — the unrendered enemy-phase message of an older digest: 54 {"ArchdukeCharles": 18, "ArchdukeJohn": 33, "KingdomOfItaly": 3} |
| narration.C4 | ✗ | — | ✓ | SF-RR6 | 74 intel rows, each where the store last saw the man or where he stands in full view; 6 morning rows whose province the store re-read later that turn: ['CMD-H t20: Archduke Charles at Milan (row t8, province re-read t20)', 'CMD-H t30: Archduke Charles at Milan |
| ai_aliveness.C6 | ✗ | — | ✓ | SF-RR6 | turns with a visible AI attack over the turns France stood at war (France's war and peace rows): {'CMD-H': '9/15', 'CMD-A': '13/18', 'CMD-M': '7/11'} |

Pillar readings: economy 7.50 → 6.00–8.00; combat_legibility 7.00 → 7.50–8.00; narration 6.50–7.00 → 7.00–7.50; ai_aliveness 8.00 → 8.50

### 2026_10_21_rr6/entry — directional 6.7 over 5/14 → 6.5 over 5/14 (v1.2 re-read)

| Item | Recorded | v1.1 re-read | v1.2 re-read | Whose | The v1.2 evidence |
|---|---|---|---|---|---|
| first_contact.C4 | ✗ | — | · | SF-RR6 | SCRIPT PRECONDITION (RS-15, read off the counsel's reply): military actions remained — - ↳ Davout, attack Archduke Charles / Ney, march to Munich |
| economy.F1 | ✓ | — | · | SF-RR6 | an archive that predates the chest's measure (EA-2): the driver never read a treasury, so an off-books flow could not be seen — v1's net_residual is zero by construction |
| economy.C5 | ✗ | — | · | SF-RR6 | SCRIPT PRECONDITION (AAR-6, read off the levy's reply): Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.' |
| combat_legibility.C4 | ✗ | — | · | SF-RR6 | SCRIPT PRECONDITION (RS-12, read off the staging line): `Davout, fortify` → Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining. |
| combat_legibility.C5 | ✗ | — | ✓ | SF-RR6 | raw keys in the combat text the player sees: 0 {}; not read — the unrendered enemy-phase message of an older digest: 47 {"ArchdukeCharles": 18, "ArchdukeJohn": 28, "KingdomOfItaly": 1} |
| ai_aliveness.C1 | ✗ | — | ✓ | SF-RR6 | laws enacted abroad (enacted, lapsed) per seed: {'CMD-H': (20, 0), 'CMD-A': (19, 0), 'CMD-M': (19, 0)} — at least 13 of the decks' 20, 0 lapses |

Pillar readings: economy 7.50 → 6.00–8.00; combat_legibility 6.50–7.00 → 7.00–8.00; ai_aliveness 6.00–8.00 → 6.00–8.50


**Read so:** the readers no longer count text the player never sees (combat C5 ✗ → ✓ everywhere), no longer read a
board the script never staged (the DL items → unmeasured on every older archive), no longer pass a check that could
not fail (economy F1 → unmeasured until the chest was measured), and count France's wars only (the gate's AI C6
✗ → ✓); the gate's narration C4 re-reads ✓ through the fixed store. AI C1's band reads the baseline ✓ (18 / 18 / 18),
the final reading ✗ (CMD-M's two lapses — the lapse clause binds) and the gate's ✓ (17 / 13 / 17): both archives read
it the same way.

## 3. The slice's own reading — the same arms, the frozen readers and v1.2

| Item | v1.1 (the frozen readers) | v1.2 | The v1.2 evidence |
|---|---|---|---|
| first contact C4 | ✓ | ✓ | "end turn — no military actions remain today / build supply depot in Rhineland — 300g" (RS-15 at zero military actions) |
| economy F1 | ✓ (blind) | ✓ | 201 end turns: the chest's change, less one-shots and the Butcher's Bill, against the applied Net — off the books none |
| economy C5 | ✓ | ✓ | "Davout recruits 3,000 infantry at Rhineland (field levy …)" at zero military actions |
| combat C4 | ✓ | ✓ | "The order would be refused, Sire: Davout is fortified — unfortify first. Nothing spent." |
| combat C5 | ✓ | ✓ | 0 raw keys in the combat text the player sees (the digest prints the dialog's lines, so even v1 reads clean) |
| drama C5 | · | ✓ | 5 eroding claims, each announced before the erosion (CMD-H Lannes: rise t6, patience 2 → 1, erosion t10) |
| vassals C5 | · | ✗ | Milan, taken by Austria on CMD-A turn 5 (the garrison destroyed), not contested within two turns — the baseline's reading of the same fall, restored; the old reader never saw it (the scripted France never marches on Milan; a reading, not claimed) |
| narration C4 | ✓ | ✓ | 93 intel rows, each where the store last saw the man or where he stands in full view |
| AI C1 | ✗ | ✓ | 20 / 19 / 19 laws, 0 lapses — at least 13 of the decks' 20 |
| AI C6 | ✓ | ✓ | 17/21, 12/23, 16/21 over the turns France stood at war (the driver's war record) |

## 4. Attribution — what moved the game, and what only moved the record

- **`BASELINE_SERIES`** (the 40-turn ambient sim): byte-identical with EG-X4's seam up and down; the lever bites (66
  views held down, 11 expiries shipped) — `tools/_sf_rr6_series_arms_final.json`.
- **The arms** (`attribution.json`): the GAME stream (the chest, the Net, the provinces, the army, every command's
  outcome) is byte-identical entry → seam down on every arm but DL (its re-staged script, by design), and seam down →
  shipped on every arm but FLD, where turn 7's `Ney, attack Archduke John` stops chasing the stale Tyrol view and
  reads the store honestly ("No intelligence on Archduke John's position") — the desk's "at Provence" disagrees:
  RR6-X3, heading S14b. The VIEW stream (the enemy phase's visible actions and battles) moves seam down → shipped on
  every arm: the stale FULL labels had shown enemy actions from provinces the player no longer saw at FULL.
- **EG-X4's cause on its own archive**: the gate's narration C4 re-reads ✓ with the seam up, the frozen ✗ (Kutuzov)
  with it down.
