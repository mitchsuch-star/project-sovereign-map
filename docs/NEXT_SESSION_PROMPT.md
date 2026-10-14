# NEXT SESSION PROMPT — Pre-Deploy S13b part 1: DD-B fixes — the three P1s and the table

> Overwritten each time a session hands off. Current hand-off: **October 14,
> 2026, after S13 (DD-B "The fresh-eyes campaign") closed.**
>
> S13 landed in four commits on master:
> - **The instrument** (`a4fd195b`): a player's hands on the real client.
>   It boots the title screen of a first launch at 5120×1440 (scale 1.4)
>   against a sandboxed backend, takes real keys and clicks, and records a
>   frame and a state for every action (`SYSTEMS_REFERENCE.md` §115).
> - **Three campaigns** (`2ca0fed5`, `fb6d751e`, the close): conquest,
>   diplomacy-first and the sea, 20 turns each, played by players who had
>   read nothing. 96 rows came to **69 causes: 11.5 per 10 turns, 3 P1**.
>   DD-B's done-when (under 5, 0 P1) is not met.
> - **Every row is filed and homed.** 62 defects went to `BUG_FIXES.md`
>   §DD-B for S13b; 9 design questions went to `DESIGN_REFINEMENT.md`
>   §DD-B for the user at S15. The write-up is
>   `docs/audits/DD_B_FRESH_EYES_2026_10_14.md`.
>
> **Nothing waits on the user.** On October 13 the user ruled "make all
> decisions … nothing hanging", and every fork this session can meet is
> decided below. DDB-D1 … D9 are the user's at S15 (UXR-4); no slice here
> depends on them.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S13b part 1 — DD-B fixes: the three P1s (S13b-1), then the table (S13b-2, 23 rows).**

Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S13b (three parts):
- part 1 = S13b-1 + S13b-2;
- part 2 = S13b-3 the field + S13b-4 the voice;
- part 3 = S13b-5 the client + S13b-6 the sea + the re-measure.

The rows, each with its cause (file:line) and its **decided fix**, are `docs/BUG_FIXES.md` §DD-B. A row's decided fix is the spec; implement it as written.

How to work:
- Work directly on master per `CLAUDE.md`. Commit and push each slice.
- Run `git fetch origin` first and read `git log -8 --stat` before touching anything.
- **Every decision is already made** (the user's ruling, October 13, 2026: "make all decisions … nothing hanging"). This prompt is the approved plan.
  - Do not stop for Plan Mode approval, and do not pause between slices.
  - The rules below settle every fork; ask the user nothing.
- **The head:** a CODE-1 lever batch runs only if the session starts on or after November 1, 2026 (the November batch). Before then there is none.

Read first:
- `BUG_FIXES.md` §DD-B, its preamble and the rows DDB-1 … DDB-12 and DDB-22 … DDB-35;
- `docs/audits/DD_B_FRESH_EYES_2026_10_14.md` §4 (the three P1s);
- the frames each row cites (`docs/audits/dd_b/<road>/frames/NNNN.jpg`) and the players' own words (`docs/audits/dd_b/<road>/rows.json`, `summaries.md`);
- `CLAUDE.md` "Before Modifying" for the diplomacy, settlement, vassal and dialogue rows;
- `docs/RELIABILITY_COMMITMENTS_SPEC.md` §8.8 (the call-to-arms episodes) before DDB-2;
- `docs/VASSAL_DEEPENING_SPEC.md` §9 (VD-C, the Contingent) before DDB-3.

**The tests.** One module per slice:
- `tests/test_ddb_s13b_the_p1s.py` and `tests/test_ddb_s13b_the_table.py`.
- One class per row, `TestDDB<n>`, as each row's completion names it.
- Through the real endpoints (the in-process TestClient on the 1805 boot or the board the row was seen on), never a mocked executor.
- A client row is pinned on the source and, where it renders, a headless frame.
- When a row lands, mark it FIXED in its Status cell with the commit and the test, and keep its tag.

**Slice 1 — S13b-1, the three P1s** (one commit).

**DDB-1 — the objection arrives with the proposal.**
- The objection's popup carries the proposal dialogue's `dialogue_id`, so it rides the proposal's FIRST response, beside the preview, before anything is sent.
- "Use Talleyrand's suggestion" APPLIES a draft; it does not send. The draft:
  - step the demanded tribute down the existing generous rounds until the pre-proposal objection (`diplomatic_defiance`) would not fire;
  - if no round passes, it is the vassalage with no tribute, and its line says so;
  - Send stays the player's next click.
- The objection's answers:
  - **Proceed Anyway** sends as drafted;
  - **Modify** returns to the draft: nothing sent, no DP spent, nothing in transit;
  - **Cancel** drops it at no cost.
- "Not Now" closes the proposal without raising the objection.
- Harsher, More generous and Adjust survive the objection's rebuild.
- The Cabinet's band word on Propose Vassal is scored on the draft the click opens (the deterministic suggested terms).
- **Test:** the Spain vassal on the 1805 boot:
  - the objection is in the first response, with the id;
  - DP is unchanged until Send;
  - Modify leaves no proposal in transit;
  - the suggestion's terms pass the objection check.

**DDB-2 — legibility only; the rule is DDB-D8's.**
- The full-alliance proposal lists "Binds France to <ally>'s wars, offensive and defensive" among its terms, plus one line per live design of the ally ("<ally>'s design: <design> on <court>").
- The line that carries France into an ally's war (the `display_names.py:953` family) names:
  - the alliance clause;
  - the war's target;
  - when France does not lead, that it cannot settle while <ally> leads.
- No mechanic changes: the cascade still joins.
- **Test:**
  - Prussia's full-alliance preview carries the clause and her Hanover design;
  - a cascade join's line names the clause, the target and the exit rule.

**DDB-3 — legibility only; the rule is DDB-D9's.**
- A dry run, `contingents_released_by_armistice(world, a, b)`, reports which contingents would lose every shared enemy if the pair went to ARMISTICE. It works on a copy of the pair's state and never mutates the world.
- The court's armistice offer popup and France's own armistice preview carry one line per such contingent: "Dumonceau's Dutch contingent (6,500) leaves Ulster for Amsterdam when this truce is signed".
- The withdrawal message recognises a contingent's march home ("marching home under Holland's colours"), never "not moved".
- **Test:** the sea road's shape, with Holland's contingent posted in a conquered province. The offer's popup names it; after acceptance the message names the march.

**Slice 2 — S13b-2's P2s: DDB-4 … DDB-12** (one commit; each row's decided fix as written). The forks, decided:

**DDB-4 — Counter.**
- The button reads "Let Talleyrand haggle (1 DP)". Its tooltip: "He sends a counter of his own choosing; if he finds none, nothing is spent and the offer stands".
- A dry run of `generate_counter_offer` runs before any DP is charged. When it returns None:
  - the offer stays;
  - no DP is spent;
  - the line reads "Talleyrand finds no counter <court> could take — the offer stands".
- The popup's war score is re-read whenever the letter is shown.

**DDB-5 — what the review lists.** It lists the provinces whose title the treaty fixes, computed by the same `status_quo_retentions` the ratifier runs (a preview call, no mutation). A French homeland province held by another court comes first.

**DDB-6 — Ease.** `_has_non_trivial_terms` skips every term France pays.
- **Test:** each Ease on a white peace raises (never lowers) the eased court's score.

**DDB-7 — the court's list.**
- First come the counsel's recommended action, then a running mission's Cancel.
- A list taller than its pane shows a "▼ more below" caption on the existing Caption step and token.
- **Test:** the payload's order for an OPEN_BORDERS court whose counsel recommends Improve Relations.

**DDB-8 — the per-court peace.**
- The eligibility runs `get_peace_commitment_conflicts`.
- The button is disabled with the conflict's reason via `Utils.set_available` ("Bavaria is still at war with Austria").
- The block text quotes the armistice's own likelihood.

**DDB-9 — the refused send.**
- `_build_content` renders `transient_error_display`.
- The generic menu's Propose peace is disabled with its reason under a paradox HARD_STOP.

**DDB-10 — the Cabinet door.**
- The Recall chip sends the structured `cancel_mission`.
- The help's COMPACTS section and the Congress table name the Cabinet control ("F1 → <court> → Buy off their design"); the typed buy-off stays refused.
- The door lets "bid for <court>, <N> gold" through as a priced order.
- The refusal line names the control the player wanted.

**DDB-11 — the per-court chip.** It shows the bilateral preview's own score and band for the terms it hands off; the joint table's number is not used there.

**DDB-12 — a co-belligerent's home province.**
- A province of France's homeland (its `starting_controller` is France), retaken from the enemy by a co-belligerent ally, is titled back to France by the status quo.
- The same holds for any co-belligerent's homeland.
- The review lists it.

**Slice 3 — S13b-2's P3s: DDB-22 … DDB-35** (one commit; each row's decided fix as written). The forks, decided:
- **DDB-23:** a stream's line reads "for as long as the treaty stands". No stream gains a term.
- **DDB-24:** label the war's sides by court ("France" against "The Third Coalition"), never attacker/defender.
- **DDB-30:** "Less generous" restores exactly the previous round's terms, and is absent on round 1.
- **DDB-33:** Ease stops at the scorer's gold ceiling, with "more gold buys nothing now". The promised-region check reads `create_client` provinces.
- **DDB-34:** the auction's dispatch line names "F1 → <court> → Bid for Their Allegiance". The advice menu offers the bid while an auction is open.
- **DDB-35:** Propose Peace stands in the WAR state with the ally-at-war hard stop used in ARMISTICE.

**The close.**
- **Rows:** S13b-1 and S13b-2 FIXED in `BUG_FIXES.md` §DD-B (commits and tests); the section heading's count updated.
- **`PRE_DEPLOY_PLAN.md` §2:** S13b part 1 noted landed.
- **`STATUS.md` ▶ NEXT UP:** a new block. Seven are kept; the oldest goes to the top of `docs/archive/STATUS_2026_Q4.md`.
- **`CLAUDE.md`:** the LIVE STATE line. The cap is ≤ 62,000 B and it stands at 61,963, so trim the oldest line as you add one.
- **`SYSTEMS_REFERENCE.md`:** any rule a fix changed (the objection's road, the per-court peace eligibility, Counter's dry run, the status quo's homeland clause).
- **This file:** rewritten for S13b part 2 (S13b-3 the field + S13b-4 the voice), with every decision made in it.

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Check `tasklist | grep -ci godot` before any engine start. The hook drives Godot (the engine group), so start no engine during a commit, and never commit while a DD-B run plays.
- **Never touch the user's live 8005 backend.** A driven check runs on `SOVEREIGN_PORT=8006` or above with `INK_IRON_SAVE_DIR` set; `uxr3_action_probe.start_backend` does both.
- **The hook tests the working tree, not the index.** Park a later slice's test edits outside `tests/` before committing an earlier slice; an untracked test in `tests/` runs in the hook. Do not edit files the tests read while a commit's hook runs.
- **`PYTHONDONTWRITEBYTECODE=1`** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING`.
- **The hook** runs ruff and the full parallel suite (about 6:20; 30,973 tests at S13's end). Commit with `run_in_background: true` from Bash, with a message file and never `--no-verify`. Read the log's `[pre-commit]` and `EXIT=` lines before believing a commit.
  - The G4 timing pin can fail under load (`test_scale_readiness_phase2.py::test_g4_turn_resolution_map_cost_within_2x_baseline`). Re-run it alone; if it passes, re-commit unchanged.
- **A byte-pinned series.** If a decided fix moves one (`BASELINE_SERIES`, the M-pins, a seeded digest), re-pin it in the same slice with the row named as the reason in the pin's comment. A move no row explains is a bug in the slice.
- **The judge is shared.** `tools/_score_probes.py` is read by the census records and the score archive. Any edit there is checked first against every committed census record (`docs/audits/unrehearsed/`) and the HOLD arms; none may move.
- **Dialogue and popup wiring** (`CLAUDE.md` "Adding a new popup/dialog"):
  - every POST handler goes through `build_base_response`;
  - a new dtype must be on the `main.gd` whitelist;
  - a popup that must arrive with its dialogue carries the dialogue's id (DDB-1's whole defect).
- **Monkeypatch the type, never a method on `M.executor` / `M.parser`.** In a TestClient world swap, swap `M.world`, `M.game_state` and `M.parser` together.
- **Shell:**
  - Bash heredocs mangle backslashes, and a Python script piped on stdin is decoded as cp1252. Write scripts with the Write tool and run them with `-X utf8`.
  - GDScript `:=` cannot infer from an untyped value; type such locals explicitly.
- **Git:** never `git add -A`; stage by name. **Line endings:** normalise records to LF.
- **Docs caps.** `CLAUDE.md` ≤ 62,000 B. `STATUS.md` keeps seven ▶ blocks.

**Code-health rules in force:**
- A new font size is a theme step, not an override (`RAW_RATCHET` 1).
- A grey is a named palette token.
- A control that cannot act is disabled with its reason (`Utils.set_available`).
- A fix lands in the stage that owns it (`_attack_*`, `_strategic_*`, `_oneliner_*`, `_choice_*`, `_ratify_*`).
- Golden Rule 6: the LLM never affects mechanics.
- Golden Rule 8: no per-region scan in a hot path.

**Open with the user:**
- UXR-4 at S15 (S12's eleven R2 marks, S12b's frames);
- DD-B's nine design rows (`DESIGN_REFINEMENT.md` §DD-B, DDB-D1 … D9), at S15 or any time before.

Nothing in part 1 waits on either.

**Do not:**
- edit `docs/UX_CHECKLIST_V1.json`;
- re-score, add a lever, or weaken a gate or a ratchet;
- change a rule a row does not name;
- build a DDB-D row before the user rules it;
- touch the Score Finish residue or start S14.
