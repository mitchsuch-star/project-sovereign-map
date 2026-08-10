# CA9 row 3 — next session: finish the queue, then play the whole thing

> **CONSUME-ONCE DOC.** This is a session handoff, not a spec. When the work
> below lands, strike this file's rows in place or delete it — a stale
> handoff is worse than none. The durable records are named in §0.
>
> Written August 9, 2026 at the end of the session that landed rows 1 and 2
> and four batches of row 3.

---

## §0 Authority — read these first, in this order

| Doc | What it is |
|---|---|
| `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md` | **Authoritative** for row 3. 27-agent audit. §4 is the item list, §5 the rulings, **§6 is seven things NOT to do and why** — read §6 before proposing anything. |
| `docs/audits/CA9_GATE_ANSWERS_2026_08_09.md` | The user's three CA9 answers + the landing records for rows 1 and 2. |
| `docs/STATUS.md` top block | Live state: what landed, what remains. |
| `docs/BUG_FIXES.md` §Creative Audit CA9 | The 31 rows landed Aug 9 that have never been played. |

**All five §5 rulings are TAKEN**, at the memo's recommendations, on the
user's instruction *"proceed at all recommendations"*:

- **Q1(b)** an arm HOLDS the escalation level at a cost — ✅ BUILT
- **Q2(a)** build the excluded council-command "to my tent" arm — ⬜ TODO
- **Q3(b)** a second fire required on stored −1 pairs — ⬜ TODO
- **Q4(a)** permanent Hostile is intended; clamp the mend arms — ✅ BUILT
- **Q5(c)** fix the visible symptoms only; **do NOT touch the
  `modify_relationship` writer** — a refuter MEASURED that fixing it diverges
  `BASELINE_SERIES` at index 20, 21 of 41 readings, tail collapsing to 0.
  Re-open only after the playtest.

Landed this session: `075982e` (row 2) · `e069894` (row 1) · `361d991`
(audit + A1) · `8100b11` (A2/A3/A4/A9/A10) · `bc3c448` (A5/A6/A8) ·
`3f8468c` (Q1b + §3 + Q4a) · `de97d42` (status). Suite **17,000 / 3 skipped**.

---

## §1 PART ONE — finish the queue, in this order

Each item is its own commit. Verification protocol in §3.

### A7 — `jealousy_note` reaches every battle *(small)*

Composed in `_execute_attack` only, so a grievance healed on DEFENCE or in
the enemy phase is never reported where it happened.

- Add it to `_format_berthier_report`'s field whitelist in
  `enemy_phase_dialog.gd` — the payload is already there (`:259-260` reads
  `battle_report`).
- Lift the composition out of `_execute_attack` (`combat_executor.py`
  ~`5809-5851`) onto the shared post-combat seam.
- **Name which of the three `check_battle_resolution` call sites get an arm**:
  `combat_executor.py:1830`, `:5239`, `world_state.py:10968` — the last has
  **no `battle_report` in scope**, so decide and say so rather than crashing.
- **Pick ONE surface** and suppress the next-morning bullet; that closes N36.
- Touches `.gd` → §3's client protocol applies.

### A11 — the three sentences that teach the system *(small, `.gd`)*

The audit found **no primer anywhere**, and the one sentence in the product
that states the causal rule is wrong twice.

1. `marshal_management.gd:225` says *"glory, last 5 turns"* against
   `GLORY_WINDOW = 8` (`jealousy.py:49`, pinned at 8 by
   `test_drama_glory_from_attrition.py:148`). **Add `glory_window` to
   `build_glory_ladder_payload` and interpolate it** — do not re-hardcode.
   Also state the rival-memory rule (envy re-fixes on a remembered man, not
   the adjacent rung).
2. `marshal_management.gd:202` tells the player to *"reward them before they
   ask"* — false twice: `_threshold_for` reads relationship/idle/authority
   and **no** satisfaction/expectation/estate term, and the chip is gated shut
   until he *has* asked. Conscious flip of `test_tutorial_position7.py:251`
   plus an R159 re-word.
3. The marshal card prints "Ney: Friendly" two lines under "GRIEVANCE:
   envious of Ney" — `marshal_overview.py:479-492` iterates the RAW stored
   dict. Make it read `get_relationship`.
4. A six-line `help` block (`meta_executor.py:614-627`) whose **load-bearing
   sentence is that estates and rentes cannot touch jealousy** (the audit
   measured players being pointed at gold that does nothing). State the solo
   bonus as *"with no marshal of yours counted on the field beside him"*, and
   include the defeat + out-bled-stalemate halves. Pin by source grep
   (precedent `test_naval_ui_clarity.py:208`).

### A12 — de-duplicate the briefing *(own commit + flip experiment)*

⚠ **Moves `BASELINE_SERIES`** — touches enemy `jealous_of`.

**Do NOT cap first.** Half the volume is duplication and self-contradiction,
so a cap preserves the wrongness and collapses the correct lines (memo §6 #3).

- Suppress the same-turn cool-then-refire for a pair (`jealousy.py` ~`1706-1734`
  vs ~`1739-1789`, whose only exclusion is `if marshal.jealous_of: continue`).
  Measured: **24 of 40 turns carry both a clear and a fire in the same pass**,
  and 4 of 4 cooling turns re-fired the same pair in the same briefing.
- Drop the duplicate escalation line; stop level-1 escalation co-emitting with
  its own fire (`jealousy.py:755`).
- Fix `dispatch.py:2441-2452`'s dict-order `jealous[0]` / `jealous[:2]` — it
  is not ranked, and 12 of 12 turns in one trace fell to the fallback. Make
  the ranking key **total**.
- **Add a positive-reach pin**: the rung is wrapped in a bare
  `try/except: pass` at `:2429` / `:2454-2455`, so a ranking bug silently
  swallows it and the suite stays green.

### Q2(a) — the council-command arm *(medium, the design item)*

`JEALOUSY_SPEC.md:983` excludes *"Council command ('to my tent')"* with **no
owner row** — a GR9 orphan — and it is *literally what the petition body asks
for*: **"He requests a command worthy of his talents."**

The memo's judgement: **the only proposal that makes the modal a decision AND
answers "why does this exist" in the same stroke.** He asks for a command; you
give or refuse a command.

- Cheapest shape: the arm issues an **existing** strategic order
  (PURSUE / MOVE_TO) at its existing AP price rather than inventing a verb.
  **UNVERIFIED that the `strategic_executor` seam is that clean — verify
  before scoping.**
- Resolution then flows through the existing per-personality predicate he
  already satisfies (`jealousy.py` ~`950-1022`) **and pays the +10% surge**,
  so the paid arm stops being dominated on the resolution side too.
- Retire the spec's exclusion line in the same commit.

### Q3(b) — a first grievance gets a first act *(own commit + flip experiment)*

⚠ **Moves `BASELINE_SERIES`**, the CA8-D3 latch sequence and tier-2 timing.

Today `qualifies = stored_rel <= -1 or fires >= 3` (`jealousy.py` ~`783`), so
**12 of 17 authored French edges reach escalation level 1 on fire 1** and the
player's very first card opens with *"this is no longer a passing mood"*.

- Require a **second fire when `stored_rel == -1`**; keep `<= -2` immediate.
- It must move the level, the card register **and** the `pair@Ln` latch
  together — that is the only version that actually delivers a first act.
- **Do NOT** ship the "gate the level-1 announcement on `fires >= 2`"
  variant: it is inert and backwards (memo §6 #5 explains why).

### A13 — cap the routine drama lines *(Phase B; after A12 measures clean)*

Prerequisite **already landed**: `by_action` rides the `jealousy_resolved`
event (A2), so an earned resolution and a timer expiry are finally
distinguishable.

- AI-6 shape: the cap lives in the **PRODUCER** so beats are structurally
  exempt. Key the exemption on `(type, by_action)`.
- Exempt: the crown, escalation-to-permanent, the autonomous warning, the
  petition arrival.
- ⚠ `test_jealousy_v32.py:823` asserts `jealousy_separation_warning` is
  present — a naive cap reds it.
- Ship a **mutation-tested never-collapsed pin**.

### A14 — the petition modal renders the marshal *(Phase B)*

- Render the `speaker` field the backend already sets at four sites
  (`jealousy.py` — the confrontation, rivalry, Fontainebleau and war-weary
  builders) and which **zero `.gd` files read**. Use
  `objection_dialog.gd:47-52`'s tone-scaled header idiom.
- Author first-person bodies **in `jealousy.py`**, NOT `marshal_voice.py` —
  its banks are keyed to five battle situations with no consumer joining them
  to the petition. `war_weary` already does this (*"I have my duchy, Sire.
  Why do we march again?"*) and is the only petition that reads as drama.
- **Do not duplicate a stat block** — the Generals card owns the character
  sheet. Unblock the lookup instead: the modal registers `modal=true`
  (`main.gd:365-367`), which gates KEY_G at `:4337-4339`.
- The portrait is a **separate layout slice**: `portrait_locket.gd` is a
  shader-bearing diorama `Control`, `marshal_management.gd:626` is a BBCode
  `[img]` emitter, and the panel is a fixed 680×480 needing the IGR-G
  `clamp_ceiling_override` treatment.

### Explicitly OUT (memo §6 + the OUT list) — do not build

Moving the petition off `_post_hud_response_routes` (file as a **list-wide
contract question**) · the enemy mirror (docs-only: retire the §9b promise and
correct `campaign_log.py:934-945`'s comment) · restoring v3's Promise Glory
deadline · a campaign-wide petition rarity budget · capping drama lines before
A12 · deleting Acknowledge · a typed "reconcile X and Y" verb · changing the
SUPPORT/hostile mechanic.

---

## §2 PART TWO — the playtest

**Only after the queue above lands.** This is the playtest the user asked for
when the rulings were taken: *"one playtest covering all of it."*

### Scope

1. **The three CA9 design rows** — row 1 (war-age peace), row 2 (attack
   confirm), row 3 (everything above).
2. **The 31 CA9 rows landed August 9** (`8100b11` and earlier;
   `BUG_FIXES.md` §Creative Audit CA9). **None has ever been played.**
3. **The owed visual sign-offs**: `Supply: Unknown` on the region panel and
   the map tooltip, and F7's per-court fog line.

### Watch specifically

| Thing | Why |
|---|---|
| Does a won war stay **exitable**? | Row 1 makes wars harder to end and CA9's own campaign closed on *"a war with no way out"*. The white-peace waiver is the escape — check it works in play. |
| Is Talleyrand's silence in a young war **legible** or just confusing? | He now recommends nothing for a 1-turn war. |
| A **non-cautious marshal charging bad odds with no warning at all** | Row 2's intended consequence. Does it read as character or as the game hiding something? |
| Does **"Let it stand"** read as a real choice? | §3. The price is stated in men now. |
| Does the **hold** feel like the promise mattered? | Q1(b) — 6 turns of "cannot harden". |
| **Grievance frequency and drama-line volume** after A12/A13 | Baselines to beat: 107 player grievances / 3 runs, 66% at threshold 1, ~15 drama lines per answerable decision, **1 petition served of 32**. |
| The **"Later"** button | A1 — it used to brick the turn. |

### Method notes (learned the hard way)

- **Port 8005 may be held by the user's own client.** Check
  `netstat -ano | grep :8005` before starting a backend; drive over HTTP on a
  second port if a client is open.
- **The shipped client does NOT render the enemy-action `message` field** —
  `enemy_phase_dialog.gd` rebuilds each line from `action_type`. Check that
  key list, not an HTTP transcript.
- The `event_log` is **500-capped** and evicts. Two separate CA9/IGR findings
  were missed because a probe read a truncated log. Read from the source, not
  the tail.

### Deliverable

A memo in `docs/audits/`, pillar re-scores against the CA9 baseline
(directional ≈6.3; narration was the only pillar that rose), defects routed to
`BUG_FIXES.md`, design items to `DESIGN_REFINEMENT.md`, and a STATUS update.

---

## §3 Verification protocol — non-negotiable, per commit

1. `".venv\Scripts\python.exe" -m ruff check backend/`
2. Full suite: `".venv\Scripts\python.exe" -m pytest tests/ -q`
   (the pre-commit hook runs both — **never `--no-verify` on a code commit**)
3. **M1–M7 + `BASELINE_SERIES`**:
   `pytest tests/test_combat_sweep_metrics.py tests/test_ai_intent_assurance.py`
   — and if byte-identical, **say WHY**, do not just assert it.
4. **A mutation sweep on every new pin.** Two of mine this session passed for
   the wrong reason and only a mutation caught it.
5. `.gd` touched → regenerate the **tracked** `tools/godot_parse_report.json`
   via `tools/godot_parse_check.gd` (harness EXIT=0) **and** boot headless and
   grep `SCRIPT ERROR` (the XR-1 rule).
6. New serialized field → `to_dict` + `from_dict` + `SAVE_FORMAT_REFERENCE.md`
   + `pytest tests/test_serialization_enforcement.py`.
7. `BASELINE_SERIES` movers get their **own commit** and a **multi-arm flip
   experiment** attributing the delta.

---

## §4 Traps this session paid for — carry them

1. **`jealousy.process_turn` appends into a PERSISTENT list**
   (`world._pending_jealousy_turn_events`) that `advance_turn` collects and
   clears. Calling it twice in a test and reading the return value hands you
   turn 1's events again. **Read the delta** (`_new_events` helper in
   `test_ca9_row3_phase_a.py`).
2. **`objection_v2.apply_mood_variance` promotes a concern one level 10% of
   the time**, which can turn a non-blocking advisory into a blocking modal.
   Its own docstring says to mock it. Three test files neutralise it; any
   test that depends on concern level must too. **It also means no
   popup-frequency measurement is reproducible without pinning it.**
3. **Co-located enemies always return FULL visibility**
   (`objection_v2.py:485`, the Step-0 rule). A fog test needs a
   non-co-located fixture, which routes through a different combat path.
4. **A cautious marshal at ≥2:1 raises a V2a objection BEFORE the muster
   gate.** The gate's real window is 1.43–2.0:1. Fixtures at 2.5:1 test the
   objection system, not the gate.
5. **`test_serialization_enforcement.py` filters `_`-prefixed names** out of
   the field set it derives. **Never introduce a `_`-prefixed state field** —
   that is how four latches hid until A10.
6. **Never `git checkout --` during a mutation sweep.** Copy backups to the
   scratchpad and restore from those. Mine discarded real edits.
7. **TestClient fixtures must swap `main_module.executor`**, not just
   `world`/`game_state`/`parser` — it carries per-turn objection state
   (`DisobedienceSystem.major_objections_this_turn`) across tests, which
   *downgrades a major objection to a mild one*. Filed for the popup audit as
   the same class of defect as the queue slots.
8. `marshal_petition_dialog.gd` **is now in the parse harness's staleness
   list**. It was parsed but not staleness-guarded, which is how the A1
   soft-lock shipped.
9. **`len(CAMPAIGN_LOG_TYPES) == 157`**, pinned in five files. CLAUDE.md's two
   mentions of 156 are historical statements about CA8 and are correct as
   dated — do not "fix" them.
10. **`Marshal.modify_relationship` reads DERIVED and writes STORED.** Q5(c)
    says fix symptoms at their own seams (`stored_moved` is the pattern) and
    leave the writer alone until after the playtest.
