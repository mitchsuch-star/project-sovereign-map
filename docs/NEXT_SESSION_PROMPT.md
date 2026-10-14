# NEXT SESSION PROMPT — Pre-Deploy S13b part 1: DD-B fixes — the three P1s (with D8 / D9 built) and the table's P2s

> Overwritten each time a session hands off. Current hand-off: **October 14,
> 2026, after S13 (DD-B "The fresh-eyes campaign") closed and its design rows
> were ruled.**
>
> **What S13 delivered** (four commits on master):
> - the instrument: a player's hands on the real client (`SYSTEMS_REFERENCE.md` §115);
> - three 20-turn campaigns by players who had read nothing: 69 causes, 11.5 per 10 turns, 3 P1;
> - every row filed and homed: `BUG_FIXES.md` §DD-B, and the write-up `docs/audits/DD_B_FRESH_EYES_2026_10_14.md`.
>
> **The rulings, the same day.** The user asked: "make design calls please do research and assure the plan has
> all errors fixed in coming sessions and any similar errors they find while working". All nine design rows
> (`DESIGN_REFINEMENT.md` §DD-B) were ruled after research; the record is `docs/audits/DD_B_RULINGS_2026_10_14.md`.
> - The builds are DDB-R1 … R7, plus the mechanics now carried by the P1 rows DDB-2 and DDB-3.
> - Four siblings were found while ruling: DDB-X1 … X4.
> - SFR-B3 (the Imperial Peace's morning) was re-homed from after the deploy to S14's head.
>
> **The plan now guarantees every error is fixed before the deploy** (`PRE_DEPLOY_PLAN.md` §2, the rule above
> the table):
> - every open row has a session;
> - the sibling sweep holds in every part;
> - the re-measure feeds S13c if needed;
> - the release build waits for 0 open defect rows.
>
> **Nothing waits on the user.** Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S13b part 1 — DD-B fixes: the three P1s (S13b-1, with DDB-D8 and DDB-D9's mechanics built), then the table's P2s (DDB-4 … 12).**

Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S13b (five parts):
- **part 1** — this prompt;
- **part 2** — the table's P3s and the field (DDB-13 … 20, 22 … 44);
- **part 3** — the rulings and their siblings (DDB-R1 … R7, X1 … X3);
- **part 4** — the voice, the client and the sea (DDB-21, 45 … 62);
- **part 5** — the re-measure.

Each row in `docs/BUG_FIXES.md` §DD-B carries its cause (file:line) and its **decided fix**: that is the spec, so implement it as written. The rulings' research is `docs/audits/DD_B_RULINGS_2026_10_14.md` §2; read the D8 and D9 sections before DDB-2 and DDB-3.

**How to work:**
- Work directly on master per `CLAUDE.md`. Commit and push each slice.
- Run `git fetch origin` first and read `git log -8 --stat` before touching anything.
- **Every decision is already made.** The user's rulings ("make all decisions … nothing hanging", October 13; "make design calls …", October 14) make this prompt the approved plan.
  - Do not stop for Plan Mode approval, and do not pause between slices.
  - The rules below settle every fork; ask the user nothing.
- **The head:** a CODE-1 lever batch runs only if the session starts on or after November 1, 2026 (the November batch). Before then there is none.

**The sibling sweep (the user's ruling, October 14 — it holds for every row):**
- Every fix ends with a search for its class: the same mechanism on the other courts, dialogues, popups and roads, and the AI's side of the same executor.
- Each sibling found is filed in §DD-B's second table as `DDB-X<n>`, with its tag `⟨SF step=pre-deploy S13 · DD-B · pillar=…⟩`.
- It is fixed in the same slice with its own test (`tests/test_ddb_s13b_the_rulings.py::TestDDBX<n>`).
- A sibling too large for the slice heads part 2. Nothing found is homed after the deploy.
- Each commit message names its sweep: what was searched, and what was found.

**Read first:**
- `BUG_FIXES.md` §DD-B, its preamble and the rows DDB-1 … DDB-12;
- `docs/audits/DD_B_RULINGS_2026_10_14.md` §2 (D8, D9) and §4;
- `docs/audits/DD_B_FRESH_EYES_2026_10_14.md` §4;
- the cited frames (`docs/audits/dd_b/<road>/frames/NNNN.jpg`) and the players' words (`rows.json`, `summaries.md`);
- `CLAUDE.md` "Before Modifying": diplomacy, settlement, vassals, dialogue state, the popup recipe;
- `RELIABILITY_COMMITMENTS_SPEC.md` §8.8 and `SCALE_READINESS_PLAN.md` §DG-4 (for DDB-2);
- `VASSAL_DEEPENING_SPEC.md` §9 and `WAR_WITHDRAWAL_SPEC.md` §5 (for DDB-3).

**Tests** — one module per slice:
- `tests/test_ddb_s13b_the_p1s.py` and `tests/test_ddb_s13b_the_table.py`;
- found rows go in `tests/test_ddb_s13b_the_rulings.py`.

Each row gets one class, `TestDDB<n>`, as its completion names it. Drive the real endpoints (the in-process TestClient on the 1805 boot or the board the row was seen on), never a mocked executor. When a row lands, mark it FIXED in its Status cell with the commit and the test, and keep its tag.

### Slice 1 — S13b-1, the three P1s (one commit, or one per P1 if a hook run is long)

**DDB-1 — the objection arrives with the proposal.**
- The objection's popup carries the proposal dialogue's `dialogue_id`. It rides the proposal's FIRST response, beside the preview, before anything is sent.
- "Use Talleyrand's suggestion" APPLIES a draft and does not send. The draft:
  - Step the demanded tribute down the existing generous rounds until the pre-proposal objection (`diplomatic_defiance`) would not fire.
  - If no round passes, it is the vassalage with no tribute, and its line says so.
  - Send stays the player's next click.
- The objection's three answers:
  - **Proceed Anyway** sends as drafted.
  - **Modify** returns to the draft: nothing sent, no DP spent, nothing in transit.
  - **Cancel** drops it at no cost.
- "Not Now" closes the proposal without raising the objection.
- Harsher, More generous and Adjust survive the objection's rebuild.
- The Cabinet's band word on Propose Vassal is scored on the draft the click opens (the deterministic suggested terms).
- **Test:** the Spain vassal on the 1805 boot.
  - The objection is in the first response, with the dialogue's id.
  - DP is unchanged until Send.
  - Modify leaves no proposal in transit.
  - The suggestion's terms pass the objection check.

**DDB-2 — France is asked (DDB-D8's ruling).**

*The rule — for the player as callee only:*
- In the OFFENSIVE cascade (`diplomacy.py:9795-9976`), when the callee is the player nation and `offensive_call_bar` does not bar it, France is NOT joined.
- Instead a letter goes out on the incoming-proposal transport as proposal type **`call_to_arms`**, using the broker-ask idiom (`settlement_third_party.py:551-601`).
- Its context carries the ally, the target and the ally's war-instance id.
- Its words: "Prussia calls on her ally to join her war on Hanover — join, or refuse at a price: reliability −N with every witness; unanswered in two turns, it is refused".
- Its answers are **Join** (Accept) and **Refuse** (Reject), with no Counter.

*What each answer does:*
- **Join** does what the honored path does today:
  - attach France to the ally's war instance (`attach_pair_to_war_instance` with the stored id);
  - WAR with reason `offensive_cascade_accepted`;
  - the −20 relation with the target;
  - `congress.note_joined`;
  - the war-entry bargains;
  - `player_drew_the_sword` still reads it: France chose to draw.
- **Refuse** emits `emit_call_to_arms_refused_offensive(world, breaker=France, victim=ally, call_context=…)`.
- **Unanswered:** the letter lapses after `GUARANTEE_GRACE_TURNS` (2) as a refusal, at the same price.

*The surfaces:*
- Display names in `display_names.py` (PROPOSAL_TYPE_DISPLAY).
- The mailbox type, and the `main.gd` dtype list if the popup needs it. Popup recipe: `build_base_response`; the letter arrives with its own response.

*The exit:*
- A pair France entered by an accepted call is marked in `war_entry_ledger` (path `call_accepted`).
- For that pair, the paradox HARD_STOP on a bilateral peace (`diplomacy.py:5300-5305`) is lifted.
- The per-court bilateral road is allowed past `not_side_leader`.
- The existing separate-peace penalty (`diplomacy.py:4987-5080`) prices it.

*Legibility:*
- The full-alliance proposal lists "Binds France to <ally>'s wars, offensive and defensive" among its terms.
- It adds one line per live design of the ally ("<ally>'s design: <design> on <court>").

*Unchanged:*
- An AI ally of an AI aggressor: `_resolve_offensive_call_path` still decides.
- The defensive call.
- The League's suppression.

*The series:* `BASELINE_SERIES` is re-measured with an attribution arm (the `tools/_vdc_series_arms.py` idiom: the rule on and off). With the passive France, letters lapse to refusals, so the series may move. Re-pin it in the same slice with "DDB-2 (DDB-D8)" as the stated reason. M1–M7 must hold.

*Test:* the diplomacy #29 shape (Prussia's design war on Hanover with a full alliance):
- the letter is posted and France is not at war;
- Join → at war, attached to Prussia's instance;
- Refuse → the refusal episode, with its strike and witness penalties;
- two turns unanswered → refused, at the same price;
- after Join, a bilateral peace with Hanover is offered and priced;
- an AI-AI cascade is unchanged.

**DDB-3 — a truce pauses the shared war (DDB-D9's ruling).**

*The predicate:*
- Add a war-family predicate in `contingent.py`: the lord and the satellite both stand in WAR **or ARMISTICE** with the same court.
- It is read where the contingent decides to keep serving (`contingent.py:771` and `:798`).
- The raise stays WAR-only (`:831`).
- The renewed-war recall (SF5-RV2) is unchanged.
- A contingent standing on its own soil during the truce keeps today's stand-down (`:793`).

*The Road Home:* a serving contingent is exempt from the Road Home's issuance and its stranding judge while its lord's pair with that court is in ARMISTICE (`withdrawal.py`: road-home issuance ~955-1000, the stranding judge 354-392 / 422-477, the warnings and internment 1184-1188).

*Golden Rule 5:* every lord, player or AI.

*Legibility:*
- The PEACE preview and a court's peace offer name every contingent the peace releases, and the post it leaves.
- The withdrawal message recognises a contingent's march home (`is_contingent_home_order`): "marching home under Holland's colours", never "not moved".

*The series:* measure `BASELINE_SERIES` with an arm (the economy-gate arms say no court is in a truce with the passive France, so it likely holds). If it moves, re-pin it with the row named.

*Test:* the sea #19 shape (Holland's contingent posted in a conquered province):
- Britain's truce keeps it at its post, with no home order and no Road Home order;
- the peace walks it home with the right line;
- an AI lord's contingent behaves alike.

### Slice 2 — S13b-2's P2s: DDB-4 … DDB-12 (one commit; each row's decided fix as written)

**DDB-4 (Counter):**
- The button reads "Let Talleyrand haggle (1 DP)". Its tooltip: "He sends a counter of his own choosing; if he finds none, nothing is spent and the offer stands".
- A dry run of `generate_counter_offer` runs before any DP is charged. When it finds none:
  - the offer stays;
  - no DP is spent;
  - the line is "Talleyrand finds no counter <court> could take — the offer stands".
- The popup's war score is re-read whenever the letter is shown.

**DDB-5:** the review lists the provinces whose title the treaty fixes, computed by the same `status_quo_retentions` the ratifier runs (a preview call, no mutation). A French homeland province held by another court comes first.

**DDB-6:** `_has_non_trivial_terms` skips every term France pays. Each Ease on a white peace raises the eased court's score, never lowers it.

**DDB-7:**
- The counsel's recommended action and a running mission's Cancel stand first in the court's list.
- A list taller than its pane shows a "▼ more below" caption, on the Caption step and its token.

**DDB-8:**
- The per-court peace eligibility runs `get_peace_commitment_conflicts`.
- The button is disabled with the conflict's reason via `Utils.set_available`.
- The block text quotes the armistice's own likelihood.

**DDB-9:**
- `_build_content` renders `transient_error_display`.
- The generic menu's Propose peace is disabled with its reason under a paradox HARD_STOP.

**DDB-10:**
- The Recall chip sends the structured `cancel_mission`.
- The help's COMPACTS section and the Congress table name the Cabinet control ("F1 → <court> → Buy off their design"). A typed buy-off stays refused.
- The door lets "bid for <court>, <N> gold" through as a priced order.
- The refusal names the control the player wanted.

**DDB-11:** the per-court chip shows the bilateral preview's own score and band for the terms it hands off.

**DDB-12:** a co-belligerent's homeland province, retaken from the enemy by an ally, is titled back to its home nation by the status quo. A province's home nation is its `starting_controller`. The review lists it.

### The close

**Rows:**
- S13b-1 and DDB-4 … 12 FIXED in `BUG_FIXES.md` §DD-B (commits and tests).
- `DESIGN_REFINEMENT.md` DDB-D8 / D9: "✅ BUILT" with the commit.
- Any found rows FIXED.

**Docs:**
- `PRE_DEPLOY_PLAN.md` §2: S13b part 1 noted landed.
- `STATUS.md` ▶ NEXT UP: a new block (seven kept; the oldest to the top of `docs/archive/STATUS_2026_Q4.md`).
- `CLAUDE.md` LIVE STATE: the cap is ≤ 62,000 B, so trim the oldest line as you add one.
- `SYSTEMS_REFERENCE.md`: the new rules (the call-to-arms letter, the truce rule for contingents, the objection's road, Counter's dry run, the status quo's homeland clause).
- This file, rewritten for **S13b part 2**: the table's P3s (DDB-22 … 35) and the field (DDB-13 … 20, 36 … 44), with every decision made in it. Carry over these part-2 forks, already decided:
  - **DDB-23:** "for as long as the treaty stands".
  - **DDB-24:** the war's sides are labelled by court.
  - **DDB-30:** "Less generous" restores exactly the previous round, and is absent on round 1.
  - **DDB-33:** Ease stops at the scorer's gold ceiling, saying so; the promised-region check reads `create_client` provinces.
  - **DDB-34:** the auction line names "F1 → <court> → Bid for Their Allegiance", and the advice menu offers the bid while an auction is open.
  - **DDB-35:** Propose Peace stands in the WAR state, with the ARMISTICE state's ally-at-war hard stop.
  - **The field:** each row's decided fix as written.

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Check `tasklist | grep -ci godot` before any engine start. The hook drives Godot (the engine group), so start no engine during a commit.
- **Never touch the user's live 8005 backend.** A driven check runs on `SOVEREIGN_PORT=8006` or above with `INK_IRON_SAVE_DIR` set; `uxr3_action_probe.start_backend` does both.
- **The hook tests the working tree, not the index.**
  - Park a later slice's test edits outside `tests/` before committing an earlier slice. An untracked test in `tests/` runs in the hook.
  - Do not edit files the tests read while a commit's hook runs.
- **`PYTHONDONTWRITEBYTECODE=1`** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING`.
- **The hook** runs ruff and the full parallel suite (about 6:20; 30,976 tests at S13's end).
  - Commit with `run_in_background: true` from Bash, with a message file, and never `--no-verify`.
  - Read the log's `[pre-commit]` and `EXIT=` lines before believing a commit.
  - The G4 timing pin can fail under load. Re-run it alone; if it passes, re-commit unchanged.
- **A byte-pinned series.** If a decided fix moves one (`BASELINE_SERIES`, the M-pins, a seeded digest), re-pin it in the same slice, naming the row as the reason, with its attribution arm recorded. A move no row explains is a bug in the slice.
- **The judge is shared.** `tools/_score_probes.py` is read by the census records and the score archive. Check any edit against every committed census record (`docs/audits/unrehearsed/`) and the HOLD arms first.
- **The census reads closing words.** In a Status cell, an uppercase FIXED / RULED / BUILT / RE-HOMED closes a row. Write them only when the row is truly closed, and keep them lowercase in an OPEN row's prose.
- **Dialogue and popup wiring** (`CLAUDE.md` "Adding a new popup/dialog"):
  - every POST handler goes through `build_base_response`;
  - a new dtype goes on the `main.gd` whitelist;
  - a popup that must arrive with its dialogue carries the dialogue's id (DDB-1's whole defect).
- **Monkeypatch the type, never a method on `M.executor` / `M.parser`.** In a TestClient world swap, swap `M.world`, `M.game_state` and `M.parser` together.
- **Shell:**
  - Bash heredocs mangle backslashes, and a Python script piped on stdin is decoded as cp1252. Write scripts with the Write tool and run them with `-X utf8`.
  - GDScript `:=` cannot infer from an untyped value; type such locals explicitly.
- **Git:** never `git add -A`; stage by name. **Line endings:** normalise records to LF.
- **Docs caps:** `CLAUDE.md` ≤ 62,000 B; `STATUS.md` keeps seven ▶ blocks.

**Code-health rules in force:**
- A new font size is a theme step, not an override (`RAW_RATCHET` 1).
- A grey is a named palette token.
- A control that cannot act is disabled with its reason (`Utils.set_available`).
- A fix lands in the stage that owns it.
- Golden Rule 5: player and AI share systems; the rulings name where they differ.
- Golden Rule 6: the LLM never affects mechanics.
- Golden Rule 8: no per-region scan in a hot path.
- Golden Rule 9: nothing deferred without a home.

**Open with the user:** UXR-4 at S15: S12's eleven R2 marks, and S12b's and DD-B's frames. Nothing in part 1 waits on it.

**Do not:**
- edit `docs/UX_CHECKLIST_V1.json`;
- re-score, add a lever, or weaken a gate or a ratchet;
- change a rule no row or ruling names;
- touch the Score Finish residue or start S14.
