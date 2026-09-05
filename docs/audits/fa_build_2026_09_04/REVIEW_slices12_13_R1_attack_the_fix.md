# FA slices 12+13 review round - lens report R1_attack_the_fix

Transcribed VERBATIM from the agent return value. Review fleet run at
master 43691f14 against a git-archive snapshot; 3 lenses x 2 refuters per
finding, 53 agents, 0 errors.

## Verdict

Every load-bearing NUMBER in both landing records is true — I re-ran the 40-turn instrumented replica on a snapshot of 43691f14 and got the recorded series byte-for-byte with zero top-ups, zero graces and one WAR-exit break at turn 25 — but two real defects survive inside the fixes: an unrelated second peace silently overrules the FA-N61 refusal and marches a corps the Emperor pulled off the road (reproduced, P2), and FA-N56 advertises Alt+Tab, which the Windows shell eats, so the one key the row exists to rescue is shipped in a form that cannot work (P2). Plus: the umbrella licence file — the third credit surface, and the one FA-N84's own mechanism names — was never touched and still points at a path the zip lacks; and one amended pin is measurably WEAKER than what it replaced while its own comment claims the opposite.

## Findings

### [P2] Slice 13 (FA-N56) advertises Alt+Tab as the focus-safe terminal key; Alt+Tab is the Windows shell's window switcher and never reaches the game — the row's own defect, re-created by its fix

- **inside the slice:** True
- **seam:** godot-client/project-sovereign/scripts/main.gd::_alt_game_key (KEY_TAB arm) · deploy/README_TESTER.txt:92 · docs/SYSTEMS_REFERENCE.md §35 rule 3 · tests/test_fa_slice13_shipping_2026_09_05.py::ADVERTISED

**Measured**

Landed tree `deploy/README_TESTER.txt:92`: `  Tab       — Collapse/restore the terminal (Alt+Tab while typing)`. Landed `main.gd::_alt_game_key` binds `KEY_TAB:` only (measured, lines 952-955). `SYSTEMS_REFERENCE.md` §35 rule 3 enumerates "E, Tab, M, Home and +/−" as the keys given a working Alt form. The slice's own `ADVERTISED` census dict in `tests/test_fa_slice13_shipping_2026_09_05.py` contains `"Tab": "KEY_TAB"`, so `test_every_advertised_key_survives_terminal_focus` is GREEN about a key that cannot arrive. `test_the_readme_advertises_the_focus_safe_form` loops only over T/G/D/R/L/N/E and never checks Tab. I did NOT run a Windows GUI test — this is a platform fact (Alt+Tab is handled by the shell before any ordinary window sees it; Godot registers no low-level keyboard hook) plus independent corroboration: the repo's working tree at review time carries an UNCOMMITTED follow-up adding `KEY_TAB, KEY_QUOTELEFT:` with the comment "Alt+Tab is the OS window switcher on Windows and never reaches the game", and a README rewrite to `Tab / Alt+\` `. So the builder reached the same conclusion after the commit.

**Repro**

On Windows, run the exported build (or the editor client), click into the command line so it holds focus, and press Alt+Tab. The OS switches windows; the terminal does not collapse. The README and §35 both say it should.

**Fix**

Bind a second, non-OS-reserved keycode for the terminal toggle under Alt (the concurrent follow-up uses `KEY_TAB, KEY_QUOTELEFT`), advertise THAT form in README_TESTER and the boot help, and add Tab to `test_the_readme_advertises_the_focus_safe_form`'s loop under its real advertised form so the pin binds. Correct §35 rule 3 so a future builder does not re-enshrine Alt+Tab.

### [P2] Slice 12 (FA-N61): an unrelated second peace wipes the refusal record, so the treaty's road IS re-issued to a corps the Emperor pulled off it — and a peace that opens no corridor at all does it too

- **inside the slice:** True
- **seam:** backend/game_logic/withdrawal.py::open_evacuation_corridor (the unconditional `road_home_offered = False` loop) · ::offer_road_home (nation-scoped, not pair-scoped)

**Measured**

Reproduced on the LANDED snapshot (git archive of 43691f14), driving the real `POST /command`:
  ["after France-Austria peace", is_road_home=true, road_home_offered=true]
  ["after typed cancel", is_road_home=false, offered=true, "Davout halts his march and awaits new orders."]
  ["after 1 end turn (refusal must hold)", is_road_home=false, offered=true, loc=Vienna]   <- the fix works
  ["after France-Russia peace (unrelated)", is_road_home=TRUE, offered=true, loc=Vienna]   <- the road is BACK, immediately
  ["after next end turn", is_road_home=true, loc=Bohemia, target=Franche-Comte]            <- he marched
Cause, read at `withdrawal.open_evacuation_corridor` (snapshot lines 577-581): the clear loops `for marshal in world.marshals.values(): if marshal.nation in (nation_a, nation_b): marshal.road_home_offered = False` unconditionally, then calls `_issue_road_home_orders`, whose `offer_road_home(world, "France")` is NATION-scoped and re-offers to every stranded French corps regardless of which treaty stranded him. Worse: that clear sits BELOW the rollback branch (lines 556-575) that pops the provisional grant when nobody is marching — so a peace that opens NO corridor at all still wipes the record for every marshal of both signatories. Corroborated: the uncommitted working tree carries the fix (`_nation_has_standing_grant(world, nation, exclude=key)`) plus two new pins, so slice 12 landed at 39 pins and the tree now has 41.

**Repro**

France–Austria peace with Davout at Vienna; `Davout, cancel orders`; end turn (refusal correctly holds); then `set_diplomatic_state(world, "France", "Russia", "PEACE")`; the Austrian road-home order is on Davout again before any further end turn, and the next end turn marches him to Bohemia.

**Fix**

Clear `road_home_offered` only when the nation goes from NO standing passage to some — i.e. gate the clear on `not _nation_has_standing_grant(world, nation, exclude=key)` — and site it ABOVE, not below, the rollback branch so a corridor-less peace never clears it either. (This is exactly the uncommitted follow-up; it needs the rollback-path arm pinned as well as the concurrent-treaty one.)

### [P3] Slice 13 (FA-N84): the umbrella licence file is the THIRD credit surface and the one the row's own mechanism names — it was not touched and still points at `assets/fonts/`, a path the zip does not contain

- **inside the slice:** True
- **seam:** THIRD_PARTY_LICENSES.md (lines 29, 58-59, 72-73, 130, 170) · tests/test_fa_slice13_shipping_2026_09_05.py::TestTheLicencesShip::test_both_credit_surfaces_point_at_the_shipped_copy

**Measured**

`THIRD_PARTY_LICENSES.md` has NO hunk in the slice diff (`grep -n '^diff --git.*THIRD_PARTY' slices_12_13.diff` returns nothing). In the landed snapshot it still reads, verbatim: line 29 "the `.ttf` in `assets/fonts/`"; line 72 "`assets/ui/icons/phosphor/` (51 SVG) ... Retain `LICENSE`"; line 73 "`assets/ui/icons/game-icons/`". build.bat copies the notices to `deploy\dist\ink_iron_server\licenses\` (and `licenses\fonts\`), and the exported zip has no `assets/` tree at all — assets live inside the .pck. The other two surfaces WERE fixed and I verified them: README_TESTER:256-257 "per-family notices in licenses\." and settings_panel.gd:312 "...with the per-family notices in licenses\\.". The slice's own pin `test_both_credit_surfaces_point_at_the_shipped_copy` checks exactly those two and not the umbrella. FA-N84's stated mechanism is "THIRD_PARTY_LICENSES.md satisfies the font obligation by POINTING AT assets/fonts/, which is not in the zip either" — the notices are now in the zip, but the pointer still is not.

**Repro**

Unzip a build. Open THIRD_PARTY_LICENSES.md at the root; it directs the reader to `assets/fonts/` for the OFL text and to `assets/ui/icons/phosphor/LICENSE`. Neither path exists in the zip; the files are at `licenses/fonts/` and `licenses/phosphor-LICENSE.txt`.

**Fix**

Add a short "in this distribution the per-family notices are in `licenses/`" line to THIRD_PARTY_LICENSES.md (or make each path row name both the source-tree and shipped location), and widen the pin from two credit surfaces to three, asserting the umbrella names `licenses` and does not send the reader to a path absent from the zip.

### [P3] An amended pin is WEAKER than what it replaced, and its own amendment comment says the opposite — `test_hotkeys_match_main_gd` no longer pins the key→screen mapping it claims to pin

- **inside the slice:** True
- **seam:** tests/test_prebuild_fixes_2026_08_14.py::TestReadmeTesterCurrent::test_hotkeys_match_main_gd

**Measured**

I applied the pin's own stated killer by hand to a copy of the landed README and ran both assertion sets verbatim.
  Killer: swap the screens on R and D (`R / Alt+R — Diplomatic Ledger`, `D / Alt+D — Morning Dispatch`).
  AMENDED pin on the scrambled README: **GREEN**.
  OLD pin (`"R   — Morning Dispatch" in text` etc.) on the equivalent scramble: **RED**.
The amended body asserts `"Morning Dispatch" in text` (satisfiable by any prose mention anywhere in the file) and, in a SEPARATE loop, `"R / Alt+R" in text` — the two are never joined, so the key and the screen are no longer tied. The amendment's own comment states: "The mapping is what this test was ever about, so it asserts the mapping." It does not. This is the pin that would catch the README drifting again, which is the row FA-N56 exists for.

**Repro**

Edit deploy/README_TESTER.txt so the R row reads `R / Alt+R — Diplomatic Ledger (nations, treaties, Talleyrand)` and the D row reads `D / Alt+D — Morning Dispatch (re-read the turn briefing)`. Run `pytest tests/test_prebuild_fixes_2026_08_14.py::TestReadmeTesterCurrent::test_hotkeys_match_main_gd`. It passes.

**Fix**

Assert the joined form: `for key, screen in (...): assert f"{key} / Alt+{key} — {screen}" in text`. That is column-independent (the amendment's stated reason for re-pointing) AND still binds key to screen.

### [P3] SYSTEMS_REFERENCE §34 states the L3-2 defect as the design rule, so a future builder will re-create it

- **inside the slice:** True
- **seam:** docs/SYSTEMS_REFERENCE.md §34 · docs/SAVE_FORMAT_REFERENCE.md:686 · the SLICE 12 block in docs/BUG_FIXES.md

**Measured**

§34, "The refusal is remembered, and its siting is the design": "Cleared when a new corridor opens for his nation (a new treaty is a new offer) and when he reaches home." The code is broader than that sentence in two ways I measured: it clears for EITHER signatory's whole roster regardless of which treaty stranded the corps (L3-2), and it clears even when the opener rolls its own grant back and no corridor opens at all (`open_evacuation_corridor` lines 556-581 in the snapshot — the rollback branch precedes the clear). The same sentence appears in the BUG_FIXES landing record and in the SAVE_FORMAT_REFERENCE row for `road_home_offered`.

**Repro**

Read §34's clearing rule, then read `open_evacuation_corridor`. The rule describes a per-nation, per-corridor lapse; the code performs an unconditional per-signatory wipe on any call, corridor or not.

**Fix**

Once L3-2 is fixed, restate the rule as what the code then does: "cleared when a nation goes from NO standing passage to some — never when it merely gains a second, and never by a peace that opens no corridor at all." Update all three copies of the sentence.

### [P4] Slice 12's GR5 claim is a two-arm identity guarded by a one-arm pin

- **inside the slice:** True
- **seam:** tests/test_fa_slice12_the_road_home_2026_09_05.py::TestTheTreatyClaimsNoFirstStep::test_the_ai_mirror_is_unchanged

**Measured**

The record says "Measured identical before and after (Mack: Orleanais → Lorraine, both arms)". `test_the_ai_mirror_is_unchanged` drives only the lever-UP arm. I ran BOTH on the working tree before it was mutated: {'lever_up': True, 'issued_turn': None, 'Mack': 'Lorraine', 'Davout': 'Bohemia'} and {'lever_up': False, 'issued_turn': 1, 'Mack': 'Lorraine', 'Davout': 'Vienna'}. The record's CLAIM is TRUE. The pin is simply weaker than the evidence behind it: it would not detect a future change that moved the AI arm and the player arm together.

**Repro**

Read the test: it sets the lever nowhere and asserts one location. Compare with its sibling `test_the_lever_down_reproduces_the_lost_turn`, which does carry a control arm.

**Fix**

Parametrise it over `THE_TREATY_CLAIMS_NO_FIRST_STEP` in {True, False} and assert Mack lands at Lorraine in both — that is the GR5 statement the record actually makes.

### [P4] Slice 12: the anti-vacuity explanation in `test_a_cut_off_corps_is_still_refused_honestly` is a dead expression statement, not the docstring

- **inside the slice:** True
- **seam:** tests/test_fa_slice12_the_road_home_2026_09_05.py::TestTheGuardsAreShared::test_a_cut_off_corps_is_still_refused_honestly

**Measured**

The function opens with TWO consecutive string literals: `"""No road is invented for a corps with none — §5, gate Q4."""` followed immediately by `"""The corridor's own file stages this with the Ionian Islands..."""`. Only the first is `__doc__`; the second is an evaluated-and-discarded expression. The second is the one carrying the FA-S12-1 lesson, so it is invisible to `pytest -v`, `--collect-only` docstring output and any doc-scraping tool.

**Repro**

Run `python -c "import ast,inspect; ..."` or simply read the function — the second triple-quoted block sits after the docstring with no assignment.

**Fix**

Merge the two blocks into one docstring.

### [P3] ENVIRONMENT HAZARD, not caused by these slices: the repo working tree is not at 43691f14 and `backend/game_logic/withdrawal.py` is being rewritten in place by a concurrent mutation sweep

- **inside the slice:** False
- **seam:** tools/mutation_sweep.py (writes production sources in place) · backend/game_logic/withdrawal.py:810 in the working tree at review time

**Measured**

At 17:53 EDT the working tree carried 7 modified files against HEAD, including `backend/game_logic/withdrawal.py` line 810 reading `        if False:` where the landed tree reads `        if not THE_TREATY_CLAIMS_NO_FIRST_STEP:` — i.e. a live mutation-sweep mutation still applied to a production source file, which makes the FA-33 lever dead in the tree. It also carried in-flight follow-up code (the L3-2 fix and an Alt+` binding) and two extra pins (slice-12 file: 39 tests landed, 41 in the tree). My own first two probes ran against that tree before I noticed; every load-bearing measurement in this report was re-run against the `git archive` snapshot of 43691f14 and is reported from there. This is the hazard CLAUDE.md records slice 10 retiring for TESTS ("no test writes under backend/ or godot-client/") — `tools/mutation_sweep.py` itself still does it, so any concurrent read of the repo during a sweep is unsound.

**Repro**

`git -C project-sovereign-map diff backend/game_logic/withdrawal.py` during a sweep run shows `if False:` substituted for the lever condition.

**Fix**

Not a code fix for these slices. Reviewers and any parallel agent must measure against a `git archive`/worktree snapshot of the commit under review, never the live tree; and the sweep should copy the tree rather than mutate it in place (or take an exclusive lock and refuse to start when the tree is dirty).

## Record corrections

- §34 of SYSTEMS_REFERENCE, the SLICE 12 block in BUG_FIXES.md, and SAVE_FORMAT_REFERENCE.md:686 all state the clearing rule as "Cleared when a new corridor opens for his nation (a new treaty is a new offer) and when he reaches home." The code is broader in two measured ways: `open_evacuation_corridor` clears `road_home_offered` for EVERY marshal of BOTH signatories on any call, and the clear sits BELOW the rollback branch, so a peace that strands nobody and opens no corridor at all still wipes the record. Measured on the landed snapshot: after a France-Austria peace and a typed cancel, an unrelated France-Russia peace put the Austrian road back on Davout immediately and marched him to Bohemia the next turn (finding L3-2).

- The SLICE 13 block says "the two credit surfaces now point at the shipped location". There are three, and the third — THIRD_PARTY_LICENSES.md itself — is the one FA-N84's own mechanism names, and it has no hunk in the slice diff. It still directs the reader to `assets/fonts/` (line 29), `assets/ui/icons/phosphor/` (line 72) and `assets/ui/icons/game-icons/` (line 73), none of which exist in the zip. README_TESTER and settings_panel.gd WERE corrected and I verified both.

- SYSTEMS_REFERENCE §35 rule 3 lists "E, Tab, M, Home and +/−" as the game keys given a working Alt form, with no caveat. Alt+Tab is the Windows shell's window switcher and never reaches an ordinary application, so the Tab entry is false on the only shipping platform. The README's own line (`Tab — Collapse/restore the terminal (Alt+Tab while typing)`) is the player-facing form of the same error, and the slice's `ADVERTISED` census pin blesses it. The builder's own uncommitted follow-up reaches the same conclusion in its comment.

- The amendment comment on `test_hotkeys_match_main_gd` (tests/test_prebuild_fixes_2026_08_14.py) states "The mapping is what this test was ever about, so it asserts the mapping." MEASURED FALSE: I applied the swap-two-screens killer by hand and the amended assertion set is GREEN on a README that maps R to the Diplomatic Ledger and D to the Morning Dispatch, while the pin it replaced is RED on the same scramble. It is the one amended pin in these two slices that is weaker than what it replaced.

- The slice-12 record's GR5 sentence "Measured identical before and after (Mack: Orleanais → Lorraine, both arms)" is TRUE — I re-measured both arms — but `test_the_ai_mirror_is_unchanged` drives only one arm, so the shipped evidence is stronger than the pin that guards it. Worth saying on the record, because a reader will assume the two-arm claim is pinned.

## Unverified

"COULD NOT VERIFY (forbidden or impractical, stated rather than assumed):\n\n1. The mutation-sweep RESULT counts. The record claims slice 12 \"26 mutations, 26 killed, 0 INERT, 0 BROKEN\" and slice 13 \"23/23 killed, 0 INERT, 0 BROKEN, three came back INERT on a first pass\". I confirmed only the SPECS: tools/_sweep_fa_slice12.json is a 26-entry list and tools/_sweep_fa_slice13.json a 23-entry list, both well-formed with real mutations. Re-running the sweep rewrites production sources and is out of scope for this lens, so the kill/INERT verdicts are unchecked. (I did apply ONE pin's own stated killer by hand — the amended README pin — and it survived; see L3-4.)\n\n2. \"the editor binary reports editor=true / template=false\". Verifying this needs a .gd script inside the Godot project to reach the `Utils` autoload, and I am forbidden to write into the repo (I created one such file by mistake and deleted it immediately; `git status` confirms nothing of mine remains). The editor half is standard Godot semantics; the TEMPLATE half is unverifiable by anyone without producing an export, and the record does not claim to have produced one. Nothing in these slices depends on it beyond the branch existing, which is pinned.\n\n3. Alt+Tab's behaviour on Windows was NOT measured by driving the client — I reasoned from platform semantics plus the builder's own concurrent follow-up comment. If that matters, the check is one minute in the running game.\n\n4. Godot parse harness EXIT=0 and the boot smoke: not re-run. `tools/godot_parse_report.json` is one of the files a concurrent session is rewriting, so running the harness would have written into the user's repo.\n\n5. The full suite (20,493/4) was not re-run — out of scope by instruction. I ran, on the LANDED snapshot: test_fa_slice12 (39), test_fa_slice13 (25), test_win_d3_road_home (43), test_main_menu_and_ux_pass, test_prebuild_fixes_2026_08_14, test_pc15_16_18_visual_fixes → 181 passed, 2 skipped.\n\nVERIFIED TRUE, each re-measured on the git-archive snapshot of 43691f14 (these are the claims the brief asked me to attack, and they all held):\n • BASELINE_SERIES byte-identical: my instrumented 40-turn replica emits exactly the recorded 41-element series.\n • \"zero mid-treaty top-ups, zero standing-question graces, exactly one vassal break — Switzerland at turn 25, the WAR exit\": TOPUPS=[] , GRACES total 0, BREAKS=[{world_turn 25, Switzerland, lord France, state WAR, via vassal.py:1193 check_vassal_rebellion}].\n • FA-33 table: home turn 6→5, warnings four→none, surplus 2 (turns-of-passage minus distance)→3 = the full EVACUATION_SLACK_TURNS. Lever-down path Vienna,Vienna,Bohemia,Franconia,Swabia,Franche-Comte with lapsing on t2/t3/t4/t5; lever-up path Vienna,Bohemia,Franconia,Swabia,Franche-Comte with zero warnings.\n • \"two French marshals destroyed in six turns\": peace at turn 1, Bernadotte and Massena both interned at turn 7 — six turns, counted. Warned 2/1/0 on t4/t5/t6 exactly.\n • The AI mirror IS identical in both arms (Mack Orleanais→Lorraine both ways) — see L3-6 for the pin-strength caveat.\n • The corrected comment about warning-on-the-same-tick: lever-up shows evacuation_granted for Massena on t4 AND evacuation_lapsing for Massena on t4. The record's self-correction is right.\n • \"interned at Vienna on turn 5 having marched nothing\" (the rider's regression arm): measured — with A_STANDING_QUESTION_IS_NOT_LOITERING False, Davout is GONE at turn 5; with it True he stands at Vienna with a live cannon_fire interrupt and the grant offset holds at a constant 7 while the int walks 9→17.\n • M1–M7: `tests/test_combat_sweep_metrics.py` contains 0 occurrences each of end_turn, withdrawal, advance_turn.\n • Licences: 16 tracked third-party notice files under assets/ (13 OFL + kenney-license.txt + 2 extension-less LICENSE), plus THIRD_PARTY_LICENSES.md; `export_filter=\"all_resources\"` with `include_filter=\"\"`; build.bat at f2b40ce3 had zero licence copies and now has five with a [WARN] arm each and no xcopy.\n • README \"Alt\" count 0 (f2b40ce3) → 12 (landed). Exactly as claimed.\n • FA-N73's refutation and FA-S12-2: KingdomOfItaly leaves at world turn 11 by ELIMINATION (0 regions), complete_vassal_break never called; Holland 92 on turn 10 and 92 on turn 11 (no sibling shock); Switzerland 74→72, its normal drift; the pop is at world_state.py:4042 in the `_lord_of_the_fallen` block. Every figure in FA-S12-2 is exact.\n • FA-S12-1's mechanism: the rollback at open_evacuation_corridor (lines 556-575) restores/pops the provisional grant when `marching` is empty, and process_evacuation_grants returns at `if not grants:`. Confirmed by reading, and consistent with my ambient corridor trace (openings at turns 1/9/10/15 with marching=0, cut_off=0).\n • Supporting counts: 35 `command_input.grab_focus()` sites in main.gd; boot-help map line at 741 vs `set_input_enabled(true)` at 745 (four lines); `_respond_blocked_path` clears `strategic_order = None` at exactly 5 places; slice-12 pins 39, corridor file 43; `tools/fa_row_tally.py` prints 110 open / 105 closed / 16 disposed / 231 total and 82 defect + 28 design, matching the STATUS table digit for digit.\n\nBOTH ROWS FILED UNDER GR9 ARE ACCURATE. FA-S12-2's three measurements reproduce exactly and its owner (slice 14) and completion definition (call the shared tail or state per-arm which of the four it declines, with a re-recorded series attributed to the reduce_threat lever alone) are adequate. FA-S12-1 is accurate and its completion definition is adequate; its owner is the weaker of the two — \"slice 14 (the singles), or a gate if (a) is preferred\" is a conditional owner, which GR9 tolerates only because both branches are named with their own done-when."
