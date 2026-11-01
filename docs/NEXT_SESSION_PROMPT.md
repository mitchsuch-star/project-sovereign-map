# NEXT SESSION PROMPT — Row RE "Affairs of State": RE-3 the three armed (after the user's review of RE-2)

> Overwritten each time a session hands off. Current hand-over: **October 31, 2026 — RE-2 the client and the dress LANDED**
> (`SYSTEMS_REFERENCE.md` §162; the record `RECURRING_EVENTS_SPEC.md` §20; two commits — A the backend half `5ca1ae56`, B the
> client half; the row before S15 by the user's ruling of October 31 — §0c). RE-1 (§19, §161) landed the same day. The deck is
> STILL UNARMED: the shipped scenario authors no `affairs` key; the four shipped moments wear the dress today, the affairs
> are exercised through `tests/fixtures/affairs_block.json` in the pins and the frames. Seven series arms byte-identical;
> the deck hash and the ratchet unchanged; the readability census RED 0 / P1 0 on the five letters; the parse harness green.
>
> **The user owes a review of RE-2's twelve readings and RE-1's six** (STATUS's two entries say each plainly; each is a line
> to reverse): line 2 in the body; the dress a pass; the derived button line cut at 40; the first affair's slot; the head
> swap; `correspondence` at RE-C; the Watch on the Dispatch alone; the cream sheet under High contrast; the hedera; the
> counsel's face; the host's minister; the sheet filling PC-F46's box — and RE-1's lone-candidate preference, pulse/desk,
> `grace`, the tier set, `ends`.
>
> **Traps the row has paid for (do not re-discover):** `build_letter` / `refresh_letter` pass every letter's STATUS ROW as
> `occ` — the register is the occurrence id's, never `bool(occ)` (RE2-1); the Decree is priced in AUTHORITY (a derived
> line that assumes gold lies); `set(MO.OPS)` is pinned (9; RE-H takes it to 10); the four shipped moment ids are pinned;
> HC-0 (no calendar read in mechanics); the S14c deck hash (`mechanical_block` descends into `affairs.deck`; arming
> anything in the scenario reds `test_moments_pacing.py` until the S14c sweep is re-recorded); no seed read in
> `moments.py`; `pick_marshal_voice` picks `bank[key % len(bank)]`; the event log rolls at 500 rows; every number to Godot
> an `int`; the first-open line ≤ 220; every answer a button; the override diet (no `[font_size=]`, no size override) and
> the layout law (no `CanvasLayer.new()` in a script; no new sibling of a popup's PanelContainer); a `static var` holding
> a Resource is forbidden (S14E-X207); a 10-px `[img]` of a large SVG aliases — use a glyph; the harness records a
> button's text cut at 60 (the frame is the proof); `-X utf8` for Python that prints a "−"; the hook runs the full suite
> (~10 min) — commit from Bash in the background with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>`, never edit
> tracked files while it runs, and a hook run that dies with the session reads as a worker crash (re-run it before
> reading the test); the capture harness must run alone (one engine per machine); CLAUDE.md's cap has 4 bytes of headroom.
>
> **For the user:** the review of RE-2 and RE-1; the certificate (the build is unsigned until it arrives); S14d's A1 as
> applied, AO's three questions (`REFORMS_SPEC.md` §5a), SF-NAV-1-D1.
> Paste everything below the line as the opening message of a fresh session.

---

Row RE "Affairs of State" — **RE-3 the three armed, with H0** — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log --format=%h -5` for the head). Plan Mode first; build on approval; land green through the hook; commit; a STATUS session entry; this prompt rewritten for RE-H; then STOP for the user's review before RE-H.

Read first: `docs/STATUS.md` ▶ NEXT UP; `docs/RECURRING_EVENTS_SPEC.md` §0c (the re-route), §19 and §20 (RE-1's and RE-2's records — what RE-3 inherits is §20.7: the deck's arming, the writers' lines and the four moments' counsel lines, the moments' authored `button_line`s, `exhibit_from` for RE-H), §16 "RE-3 — the three armed" and §16b's RE-3 row (1.5: T2 at two corps with the `{host}` / `{seat}` / `{minister}` slots and the tenure guard — P6; the writers' lines, counsel and reaction copy for T1–T3 and the four moments' counsel lines — P12; the reach re-measured on the live tree — ERR-3; the lockstep of `tests/fixtures/moments_block.json` and the frame names), §6.1 (the three templates as authored), §6.5 (H0 — the Haiti letter's bill alone is RE-H's first step, NOT RE-3's), §12c (the reaction copy's keys — RE-R renders them; RE-3 authors the lines), §14 (the band the totals must sit in), §17b (Rule 9 — nothing deferred without an owner); `SYSTEMS_REFERENCE.md` §161 and §162; `backend/game_logic/affairs.py` and `moments.py` (`letter_payload`'s dress keys; `_derived_button_line` — an authored `button_line` wins); `backend/modding/validator.py::_validate_affairs`; `tests/fixtures/affairs_block.json` (the deck to copy into `godot-client/project-sovereign/assets/maps/europe_1805.json` under `moments.affairs`); `tools/_s14c_sweep_record.py` (the deck hash re-recorded the moment the scenario arms), `tools/_affairs_series_arms.py` (the rig; arm 0 the shipped tree), `tools/_affairs_first_arrival_probe.py` (the ten-seed probe), `tools/playtest_driver.py` (`--affair`), `tests/conftest.py` (the suite-wide pins); the suite-reach head recorded at §19.5 — `test_moments_armed.py:72-75, 117, 232-254`, `test_moments_reich.py:84-86, 140`, `test_ai_intent_assurance.py` (the signature's `affair_turns`), `test_serialization_played_world_census.py`, `BASELINE_SERIES`, `test_moments_pacing.py`'s deck hash; CLAUDE.md's Golden Rules.

Scope: **RE-3 as §16 and §16b write it.** (1) **Arm the deck:** T1–T3 copied from the fixture into the shipped scenario's `moments.affairs` with each `source` and `watch`; T2 at two corps with the slots and the tenure guard (P6). (2) **The suite-reach head FIRST:** arm on a scratch tree and run the suite; about fifty test files boot a scenario and advance turns directly — list every reactor, then re-seat each consciously or keep it dormant with a conftest pin, and record the choice in the landing record. (3) **The copy (P12):** the writers' lines (`line`), the counsel lines for T1–T3 and the four moments, the reaction copy (`echo`, `press`, `remember`) for T1–T3, the moments' authored `button_line`s where the derived ones fall short (the Decree's drops its action token at 40); `DISPLAY_KEYS` widened as §16b says; the Match and the Decree re-shot with their counsel under the buttons; `tests/fixtures/moments_block.json` and the frame names in lockstep. (4) **The series arms, the attribution and the re-pin:** `BASELINE_SERIES` moves by the arming — attribute every mover to a seam with the rig, re-pin consciously; the S14c sweep re-recorded (`tools/_s14c_sweep_record.py`) and the deck hash re-pinned. (5) **The measure (ERR-3):** CMD-H, CMD-A and CMD-M; the Rhine road on three seeds; REACH-AAR; the ten-seed sweep's ceilings; the six hand-played saves as `--from-save` starts — every template's reach reported per seed and per save; none fires with its premise false; the ceilings hold; **the Rhine road's end turns unmoved with the lapse default**; the totals in §14's band. Done when: every template's reach is reported per seed and per save; none fires with its premise false; the ceilings hold; the Rhine road's end turns are unmoved; the totals sit in §14's band; the dressed frames re-shot with the counsel lines; every `.gd` edit grep-verified; the full suite green through the hook. Pins: `tests/test_affairs_pacing.py` re-recorded; `tests/test_affairs_nondominance.py` per §16 (three boards per template; each answer strictly better than the other on at least one delivered axis; the Decline free of every purse; no alarm; the letter absent where `bites` fails); `tests/test_moments_client.py` extended. Then the STATUS entry (archive the oldest entry if the seven-entry cap bites), `SYSTEMS_REFERENCE.md` §163, `RECURRING_EVENTS_SPEC.md` §21, this prompt rewritten for RE-H, and the review pause.
