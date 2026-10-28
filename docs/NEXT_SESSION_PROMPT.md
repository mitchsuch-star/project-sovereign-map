# NEXT SESSION PROMPT — Pre-Deploy S15: the deploy (the build, the clean-machine run, the release record)

> Overwritten each time a session hands off. Current hand-over: **October 26, 2026, after S14h part 2 — S14h COMPLETE**:
> the third measure's twenty-one P3s S14G-13 … 33 and the instrument row S14G-I1 FIXED, D4 and D5 BUILT as recommended,
> the five mentions filed and closed (four fixed, the Swiss petition refuted), the sweep's S14G-X56 … X172 fixed or
> closed, the closing re-play of every sighting from fourteen crafted scenes on the DD-B instrument
> (`docs/audits/dd_b/replay_2026_10_26/`), `BASELINE_SERIES` byte-identical on every arm, the parse harness green on
> 80 scripts and 17 scenes, the ratchet held. `SYSTEMS_REFERENCE.md` §155 (part 1) and §156 (part 2);
> `BUG_FIXES.md` §S14G; `DESIGN_REFINEMENT.md` §S14G; commits through the hook (`git log --format=%h -5`).
> **The census: 0 open S14G rows — 0 open defect rows. The deploy gate's own condition holds.**
>
> **Landed after S14h, October 27, 2026 — the enemy-AI sweep** (`SYSTEMS_REFERENCE.md` §157; `BUG_FIXES.md` §OCT27 — fifty-one
> rows FIXED at the cause: the enemy diplomacy AI's coalition, intent ladder, AI-to-AI table, proposal rungs, the courts'
> answers, the other instruments, and twelve classes of AI orders the executor refused; the repeat-ask governor; the
> ambient series re-recorded and attributed by `tools/_oct27_series_arms.py`). **Its thirteen design questions were
> taken as recommended and BUILT in S14i (`SYSTEMS_REFERENCE.md` §158 — part 1 D1 … D7, part 2 D8 … D13; S14I-1 … 3
> fixed beside them); the census reads 0 open defect rows and 0 open design rows. Three choices made under the
> delegation stand for your review: D4 read between neighbours, D10(ii) the war's credit folded with its total kept
> (measured against the settlement table), D10(iv) a held province priced at half its fresh cession.**
>
> **Landed after S14i, October 27, 2026 — S14j, the economy rebalance, by the user's word ("lets actually fix this economy
> before build … it shouldnt run away like this")** (`SYSTEMS_REFERENCE.md` §159; the record
> `docs/audits/ECONOMY_REBALANCE_2026_10_27.md`): a corps detached into a garrison keeps its pay; conquered soil costs 0.15
> more of its base in every stability tier; the Charges' crown term 30 → 250 with the AI's purse reading the Net before the
> Charges. The opening is untouched (France's turn-1 bill 2,834). France's chest now levels off at 16–40k and the courts'
> purses at 146–193k together on the commanded arms (were 43–75k and 380–453k); `BASELINE_SERIES` re-pinned (J3 alone at
> [12]); the census still 0 / 0. **Nothing in it holds S15** — the crown's level (250, measured band 200–250) is yours to move.
>
> **Landed after S14j, October 28, 2026 — S14k part 1, the courts take the field, by the user's word ("they should get armies
> or the ability to make them, we want the game dynamic")** (`SYSTEMS_REFERENCE.md` §160; the record
> `docs/audits/COURTS_IN_ARMS_2026_10_28.md`): Saxony and Portugal boot with their 1805 field corps; every court that fought
> in the period has a bench (eleven, twelve Commons portraits on the user's yes); a court with no general is called to arms
> by a design priced against it; a satellite fights its lord's war by its contingent; the force limit reads the court's
> tier. Like for like no checklist item flips; `BASELINE_SERIES` re-pinned (K2 + K3 at [11]). **S14k part 2 — the courts'
> goals and the Ottoman New Order (`PRE_DEPLOY_PLAN.md` §2 S14k) — lands before S15**; if this prompt is read before it
> has, run part 2 first.
>
> **What the last session delivered, in one breath:** every cause the three fresh players met is closed at the cause, each
> fixed sentence carried to every surface where its choice is made — the band names the unscouted provinces and gives
> both readings; the caret is released on every Esc road and every key pointer says the typing form; the Admiralty says
> why a corps may embark and what every chip costs, and the Emperor's verb refuses him as its counsel always said; the
> peril clause reads the live field; no corridor opens for a pair never at war and a corridor serves the pair's own
> stranded corps; a counter-offer marks what the court added or cut and who pays; the truce has one wording with the
> courtship counted; a send says the courtship pauses; a draft lasts the turn and the war's title is never a raw id; a
> quiet enemy phase is one line; the expedition's card names the prize and the camp's blockade comes back with its cause;
> a tie goes to own soil on both sides' roads; the instrument names a glyph link; the fortify reply says the first dawn's
> front-load, the muster prices a win's alarm and the morning names what moved it, the levy line names the capital's
> quote and the order, the pooled sail's departure is announced with the window's true need.
>
> **Traps the last session paid for:**
> - **`-m "not engine"` filters NOTHING** — "engine" is an xdist group in `tests/conftest.py`, not a registered marker;
>   five builders launched headless Godot by accident. Deselect `ENGINE_GROUP_MODULES` by name (`--deselect` / `-k`).
> - **A class name with a suffix escapes the renumbering regex** (`TestS14GX28_1TheTruceCure`, `TestS14GX32_6b`) —
>   normalise names before the merge; `rowI1` has no digits to sort by.
> - **The machine ran out of memory at 8 pytest workers once** (2.4 GB free): 4 workers then.
> - **A builder's own-file sibling goes back to the builder**; a sibling in another builder's file waits for the next wave.
> - The series tool chains from the prior record's arm "0" (the shipped tree); the Godot exe sits inside a folder of the
>   same name; the Bash heredoc eats quotes; `ruff` / `python` are not on the Bash PATH (`.venv\Scripts\python.exe -m ruff`).
>
> **For the user:** the certificate (not on this machine — the build is unsigned until it arrives); S14d's A1 as applied,
> AO's three questions (`REFORMS_SPEC.md` §5a), SF-NAV-1-D1.
> Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S15 — the deploy — on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log --format=%h -5` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP; `SYSTEMS_REFERENCE.md` §153 (the walk, the certificate's absence §153.3, the build and the clean run HELD §153.4) and §152.11 (the signing seam in `deploy\build.bat`: `INK_IRON_SIGNTOOL_ARGS` / `SIGNTOOL`, `release_smoke.py --expect-signed`); `docs/UX_UI_REVIEW_PLAN.md` §UXR-4 (the landing); `docs/PRE_DEPLOY_PLAN.md` §2 S15 (the deploy gate: 0 open defect rows — it holds, read `.venv/Scripts/python.exe tools/defect_census.py --open`); `docs/audits/RELEASE_TEMPLATE.md` (the record's shape); `tools/clean_env_run.ps1` (the clean-environment instrument, PREPARED and untested); `docs/PLAYTESTING.md` Mode C; CLAUDE.md's Golden Rules.

Scope: **S15's deploy.** (1) **The build:** `deploy\build.bat` on the head — UNSIGNED unless the certificate has arrived (check the two variables and the stores first; if present, the signed road and `--expect-signed`); the export, the smoke (`release_smoke.py`), the stamp. (2) **The clean-environment run** (`tools/clean_env_run.ps1`: the build unpacked outside the repo, a system-only PATH, no `.env`, its own `APPDATA`, `launch.bat` the one door, the window read by PrintWindow and driven by messages to its own handle) — the first time it runs: expect the instrument itself to need fixes; fix them in the tool, never in the game, and record each. (3) **The walk on the built client** (not the editor's): the DD-B instrument's stops (§153's list: the School of War end to end, the Generals and Settings on the lesson board, a battle at Swabia with the muster at its head, the enemy phase, the dispatch, the peace table through the war HUD, the Generals on the campaign board) — 0 script errors; any new row is filed and fixed before the record is written (the gate is 0 open rows). (4) **The release record** `docs/audits/RELEASE_<version>.md` from the template: the stamp, the signing found or absent, the smoke, the export, the clean run, the walk, what the build waits on. Done when the record is written, the census reads 0 open defect rows, and `docs/STATUS.md`, `SYSTEMS_REFERENCE.md` §157, `PRE_DEPLOY_PLAN.md` §2 (S15 LANDED), `UX_UI_REVIEW_PLAN.md` and this prompt (for what follows the deploy — the user's call) are written; the full suite green through the hook. **No fourth measure** unless the user calls one (S14G-D7).
