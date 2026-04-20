# MP v2.4.3 — Block 1: Doc-Only Trim Cleanup

> **Source:** [MP_V243_AUDIT_COMBINED.md](docs/audits/MP_V243_AUDIT_COMBINED.md) — Block 1 (~3 hours, one session, doc-only).
>
> **Ships as:** single atomic commit. Do not split — the edits all anchor on the v0.5.1 trim decision; splitting creates a window where §12 and §8.8.10 disagree.
>
> **Pre-merge gate for:** B-Hegemony (needs U1/U5/U8/U9/U10/U15), B-B1-lite (needs U1/U5), C-lite (needs U1/U5/U8).

---

## Scope

13 unified findings, all documentation. No code changes. No test runs needed (nothing executable moves).

| # | Finding | Primary files | Est. |
|---|---------|---------------|------|
| 1 | U1 — v0.5.1 trim leak (§12 + DG-4 + cross-refs) | `COMMITMENTS_PRESENTATION_SPEC.md` §8.1/§9.2/§12.1/§12.2/§12.3/§13; `RELIABILITY_COMMITMENTS_SPEC.md` §8.8.5/§8.8.10; `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` | 90 min |
| 2 | U5 — Commitments routing table | `COMMITMENTS_PRESENTATION_SPEC.md` §8.1 (new join-table) | 20 min |
| 3 | U7 — Save format refresh | `SAVE_FORMAT_REFERENCE.md` | 30 min |
| 4 | U8 — Voice Bible v0.3 → v0.5.1 | `DIPLOMAT_VOICE_BIBLE.md` | 10 min |
| 5 | U9 — HIGH-tier note | `COMMITMENTS_PRESENTATION_SPEC.md` §9.2 | 5 min |
| 6 | U10 — B-Hegemony test bullet | `RELIABILITY_IMPLEMENTATION_PLAN.md` line 132 | 5 min |
| 7 | U11 — §11.1 Case 1 rewrite | `RELIABILITY_COMMITMENTS_SPEC.md` lines 1018-1021 | 5 min |
| 8 | U12 — §11.1 Case 2 gate | `RELIABILITY_COMMITMENTS_SPEC.md` line 1026 | 5 min |
| 9 | U13 — hegemony_target_mod comment | `RELIABILITY_COMMITMENTS_SPEC.md` lines 843-848 | 2 min |
| 10 | U14 — §10.3 self-ref | `COMMITMENTS_PRESENTATION_SPEC.md` line 402 | 2 min |
| 11 | U15 — Runtime-behavior note | `RELIABILITY_COMMITMENTS_SPEC.md` §319/§996; `COMMITMENTS_PRESENTATION_SPEC.md` §415 | 15 min |
| 12 | U16 — Non-cast nation fallback | `COMMITMENTS_PRESENTATION_SPEC.md` §10.3 | 5 min |
| 13 | U17 — Arithmetic | `RELIABILITY_IMPLEMENTATION_PLAN.md` line 329 | 2 min |

**Subtotal: ~3 hours.**

---

## Execution checklist

Work the items in the order below. The first two are the structural edits that everything else depends on; the rest are independent and can be landed in any order.

### 1. U1 — v0.5.1 trim leak (the big one)

#### 1a. Presentation spec §8.1 event routing table — add DG-4 rows

[`docs/COMMITMENTS_PRESENTATION_SPEC.md`](docs/COMMITMENTS_PRESENTATION_SPEC.md:213), lines ~213-220. Append three rows:

| Event | Primary surface | Tier | Voice |
|-------|-----------------|------|-------|
| `call_to_arms_refused_offensive` | single-voice notice | CRITICAL | `envoy` → victim's diplomat |
| `call_to_arms_refused_defensive` | single-voice notice | CRITICAL | `envoy` → victim's diplomat |
| `call_to_arms_honored_costly` | single-voice notice | CRITICAL | `foreign_office` → "The Chancery of France" (Talleyrand register) |

#### 1b. Presentation spec §9.2 icon/label table — add DG-4 icons and labels

Same file, §9.2. Suggested (final wording at author's discretion):

- `call_to_arms_refused_offensive` → icon `icon_call_refused_offensive`, label "Pact Dishonoured"
- `call_to_arms_refused_defensive` → icon `icon_call_refused_defensive`, label "Ally Abandoned"
- `call_to_arms_honored_costly` → icon `icon_call_honored_costly`, label "Oath Kept"

#### 1c. Presentation spec §13 core tasks — add DG-4 template stubs

Same file, §13. Add a bullet naming the three `commitments_notice_*` template stubs to author.

#### 1d. Presentation spec §12.1/§12.2/§12.3 — retrofit worked examples

Same file, lines ~526-554, ~571-603, ~615-653.

- Relabel "spotlight" → "CRITICAL notice" throughout.
- Collapse "two-beat split-voice card" to "single-voice card with named-diplomat inline attribution."
- **Delete** the `Next-morning callback` and `Optional N+1 aside` blocks. Preserve the exact prose in [`COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md`](docs/COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md) under a new appendix titled "v0.3 deferred prose (moved here by v0.5.1 trim — retained as design intent for WB-D)".
- Keep the Hardenberg / Metternich / Einsiedel lead-line exemplars verbatim — only the staging and callback framing need to go.

#### 1e. Commitments spec §8.8.5 — fix cross-ref and tier

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md:692), line 692. Current text: *"Emits `call_to_arms_honored_costly` spotlight through C3-lite presentation (see §8.8.8)"*. Replace with: *"Emits `call_to_arms_honored_costly` CRITICAL notice through C3-lite presentation (see §8.8.10)"*.

#### 1f. Commitments spec §8.8.10 — strip "spotlight" language

Same file, lines 758-768. Current text says *"Each needs authored spotlight and notice copy in `diplomatic_templates.py`"* and *"Victim's diplomat leads the refusal spotlight"*. Replace:

- "authored spotlight and notice copy" → "CRITICAL notice copy (no spotlight tier in C3-lite v0.5.1)"
- "Victim's diplomat leads the refusal spotlight" → "Victim's diplomat voices the CRITICAL notice"

#### 1g. Verify

```bash
grep -n spotlight docs/RELIABILITY_COMMITMENTS_SPEC.md docs/COMMITMENTS_PRESENTATION_SPEC.md
```

**Expected:** only historical/changelog/stub references remain. Any live-contract use of "spotlight" is a bug.

---

### 2. U5 — Commitments routing join-table

[`docs/COMMITMENTS_PRESENTATION_SPEC.md`](docs/COMMITMENTS_PRESENTATION_SPEC.md:213) §8.1. After the existing event-routing table (now augmented by 1a), add one explicit join-table that is the **single source of truth** for implementers:

| Event family | Priority | Icon key | Player label | Template key | Speaker resolver | Review target |
|--------------|----------|----------|--------------|--------------|------------------|---------------|
| `commitment_paradox` | HARD_STOP (popup) | `icon_paradox` | "Conflicting Oaths" | `commitments_notice_paradox` | `talleyrand` | `ledger_commitments` |
| `hard_reject_posture_triggered` | CRITICAL | `icon_hard_reject` | "The Chancery Shut" | `commitments_notice_hard_reject_triggered` | `foreign_office` → "The Chancery of {nation}" | Open Ledger |
| `hard_reject_posture_cleared` | NORMAL | `icon_chancery_reopened` | "The Chancery Reopens" | `commitments_notice_hard_reject_cleared` | `foreign_office` → "The Chancery of {nation}" | Open Ledger |
| `diplomatic_treaty_broken` (`french_breach`) | CRITICAL | `icon_treaty_broken` | "Word Broken" | `commitments_notice_breach_french` | `envoy` → victim's diplomat | "Review the broken treaty" |
| `diplomatic_treaty_broken` (other families) | NORMAL | `icon_treaty_dragged` | "Treaty Dragged Apart" | `commitments_notice_breach_other` | `foreign_office` → context-dependent | Open Ledger |
| `commitment_paradox_resolved` | NORMAL | `icon_paradox_resolved` | "The Wound Chosen" | `commitments_notice_paradox_resolved` | `talleyrand` (notice) / `system` (log) | — |
| `witness_strike_recorded` | NORMAL | `icon_witness_strike` | "Europe Is Aware" | `commitments_notice_witness_strike` | `system` / `foreign_office` per scope | — |
| `call_to_arms_refused_offensive` | CRITICAL | `icon_call_refused_offensive` | "Pact Dishonoured" | `commitments_notice_call_refused_offensive` | `envoy` → victim's diplomat | Open Ledger |
| `call_to_arms_refused_defensive` | CRITICAL | `icon_call_refused_defensive` | "Ally Abandoned" | `commitments_notice_call_refused_defensive` | `envoy` → victim's diplomat | Open Ledger |
| `call_to_arms_honored_costly` | CRITICAL | `icon_call_honored_costly` | "Oath Kept" | `commitments_notice_call_honored_costly` | `foreign_office` → "The Chancery of France" | Open Ledger |

Flag the table as *"Single source of truth: notifications, dispatch formatter, campaign log, popups, and ledger MUST derive priority/icon/label/template/voice/review-target from this row — do not hardcode elsewhere."*

---

### 3. U7 — `SAVE_FORMAT_REFERENCE.md` refresh

[`docs/SAVE_FORMAT_REFERENCE.md`](docs/SAVE_FORMAT_REFERENCE.md:12).

- Line 12: `Format version: 1.0` → `Format version: 1.1`.
- Line 14: `Compatible with: Phase 4 Commands/QoL/Popups + Diplomacy Button Session A` → `Compatible with: Memory and Pressure v2.4.3 substrate (betrayal_history, next_episode_id, nation-level diplomatic_reliability) + Diplomacy Button Session A`.
- Lines 107-109: update sample to show nation-level `diplomatic_reliability` (not per-pair); add `betrayal_history: []`; add `next_episode_id: 1`; add note above `alliance_paradox_popup` → *"**Legacy alias.** Canonical key is `commitment_paradox_popup` (v2.4.3). `from_dict` accepts both for backward compat."*
- Line 190: update the `pending_dialogue_queue` line to reference `commitment_paradox` (with `alliance_paradox` alias note) rather than `alliance_paradox` as a first-class priority item.
- Lines 224-226: rewrite the `diplomatic_reliability` row to nation-level, not per-pair. Keep the legacy per-pair note as a "v1.0 schema" footnote.
- Lines 874-875: update the sample `game_version` to current.
- Add a new row (or footnote) reserving `reparations_cooldown` with status "Planned (B-B7)" so the shape can be locked later without another schema edit.

---

### 4. U8 — Voice Bible version bump

[`docs/DIPLOMAT_VOICE_BIBLE.md`](docs/DIPLOMAT_VOICE_BIBLE.md:4).

- Line 4: `v0.3 scope note (Apr 16, 2026)` → `v0.5.1 scope note (2026-04-20)`.
- Line 6: `COMMITMENTS_PRESENTATION_SPEC.md v0.3 §10.3` → `COMMITMENTS_PRESENTATION_SPEC.md v0.5.1 §10.3`.
- Status line: `v1 draft — Apr 15, 2026` → `v1.1 — v0.5.1 aligned — 2026-04-20`.
- Line 203 heading: `Required for C3-lite (v0.3 — must land in this phase)` → `Required for C3-lite (v0.5.1 — must land in this phase)`.
- Add a one-line changelog entry: *"v1.1 (2026-04-20): header version labels realigned to presentation v0.5.1. No cast or line-count changes; 4-line minimum still matches v0.5.1 §10.3."*

---

### 5. U9 — HIGH-tier clarifying note

[`docs/COMMITMENTS_PRESENTATION_SPEC.md`](docs/COMMITMENTS_PRESENTATION_SPEC.md) §9.2. After the existing priority tier table, add:

> Commitments events use **CRITICAL** or **NORMAL** only. The `HIGH` tier (used by `MARSHAL_DEFIED_ORDER` in `backend/notifications.py:19-21`) is intentionally not used by this pass to keep the three live commitments events visually distinct from military urgency.

---

### 6. U10 — B-Hegemony test bullet

[`docs/RELIABILITY_IMPLEMENTATION_PLAN.md`](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:132), line 132. Pick one of:

- **Option A (recommended):** remove the Balance-of-Europe bullet from B-Hegemony entirely, noting that all four state-case tests live in C-lite §14 (line ~741).
- **Option B:** expand the bullet from three cases to four: *"Balance of Europe headline composition across all four §11.1 state cases: no hegemon, hegemon without coalition, coalition BREWING without leader, coalition DECLARED with leader"*. If Option B, confirm C-lite does not double-test.

---

### 7. U11 — §11.1 Case 1 rewrite

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md:1018), lines 1018-1021. Replace the contradictory prose with:

> The equilibrium line is standalone. If a coalition is independently brewing from event-based threat (battles, captures), a BREWING line from Case 3 may still render below it; the equilibrium and BREWING lines are composable.

---

### 8. U12 — §11.1 Case 2 gate

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md:1026), line 1026. Add:

> When `threat_level < 30` with a hegemon present, render only the hegemon line; the flavor line is suppressed.

---

### 9. U13 — hegemony_target_mod comment

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md:843), lines 843-848. Change *"clamped at -20 from 63.33%+ onward"* → *"clamped at -20 from ~63.34%+ onward (integer truncation of raw = 20 clamps to max ceiling)"*.

---

### 10. U14 — §10.3 self-ref

[`docs/COMMITMENTS_PRESENTATION_SPEC.md`](docs/COMMITMENTS_PRESENTATION_SPEC.md:402), line 402. Drop the `per §10.3` qualifier, or move the rule inline into §10.3 proper and reference it from the table without the circular cite.

---

### 11. U15 — Runtime-behavior note

Add a compact "Runtime contracts" subsection to [`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md) (near §996, per-turn bloc cache). Write exactly:

**Logger for non-France hegemon guard** (§319):
- Channel: `logging.getLogger("backend.game_logic.coalition")`, level `INFO`.
- Message format: `[hegemony] non-France hegemon detected ({hegemon_nation} @ {share:.2f}); skipping add_threat (threat scalar France-targeted in v0.1)`.
- Rate: once per turn per actor (not per call) — implementers should deduplicate against a per-turn set.

**Fail-loud shape for unsupported diplomat personalities** (presentation §10.3 / §415 loyalist note):
- Raise `ValueError(f"loyalist register unsupported: {nation}/{personality}")` so unit tests can assert on it instead of matching log output.

**Per-turn bloc cache** (§996):
- Field: `WorldState._bloc_members_cache: Dict[str, Set[str]]` (leader nation → set of bloc members).
- Invalidation: `invalidate_bloc_members_cache()`, called from the same seams as `invalidate_active_nations_cache()` (diplomatic state changes, vassal changes).

Add the corresponding rule to presentation §10.3 (U14's target area): *"When `speaker='envoy'` cannot resolve to a named diplomat (see §7.7 scale note), raise `ValueError` per U15; do not silently fall back to `system`."*

---

### 12. U16 — Non-cast nation fallback scope note

[`docs/COMMITMENTS_PRESENTATION_SPEC.md`](docs/COMMITMENTS_PRESENTATION_SPEC.md:413) §10.3. Add:

> **v0.1 scope:** assumes the 5-nation roster (France + Britain + Austria + Prussia + Saxony). If a future event targets a non-cast nation, the render falls back to `foreign_office` → "The Chancery of {nation}" with no personality register until the cast expands. The fail-loud `ValueError` (see U15) fires only for the named-diplomat resolver path (`speaker='envoy'` + cast nation); it does not fire on the non-cast fallback path.

---

### 13. U17 — Arithmetic

[`docs/RELIABILITY_IMPLEMENTATION_PLAN.md`](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:329), line 329. Either correct the total row to `~46-53` to match the row sum, or keep `~45-54` and annotate the cell with `(approx. — rows sum to 46-53)`.

---

## Definition of done

- [ ] All 13 items above applied.
- [ ] `grep -n spotlight docs/RELIABILITY_COMMITMENTS_SPEC.md docs/COMMITMENTS_PRESENTATION_SPEC.md` returns only historical/changelog/stub references.
- [ ] No unresolved cross-reference targets (scan §8.8.5 cross-ref chain in particular).
- [ ] `SAVE_FORMAT_REFERENCE.md` documents v2.4.3 substrate fields + alias policy.
- [ ] `DIPLOMAT_VOICE_BIBLE.md` header reads "v1.1 — v0.5.1 aligned".
- [ ] `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` has the deferred v0.3 prose (Next-morning callback, Optional N+1 aside) preserved under a new "v0.3 deferred prose" appendix.
- [ ] Single atomic commit titled approximately: *"MP v2.4.3 Block 1: trim cleanup — §12 retrofit + DG-4 routing + save format refresh + Voice Bible v0.5.1 + runtime contracts"*.

## Out of scope

- No code changes (those are Block 2).
- No new artifacts (those come in their scheduled plan slices: B-Hegemony / B-B1-lite / B-B3 / B-B4 / B-B7 / C-lite).
- No test authoring or test runs (no executable code is moving).
