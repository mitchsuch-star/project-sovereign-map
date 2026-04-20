# MP v2.4.3 — Block 1: Doc-Only Trim Cleanup

> **Source:** [MP_V243_AUDIT_COMBINED.md](docs/audits/MP_V243_AUDIT_COMBINED.md) — Block 1 (~3 hours, one session, doc-only). **Addendum (2026-04-20):** follow-up meta-audit added items A1-A12 (see [Addendum](#addendum--follow-up-findings-2026-04-20)) — doc-only, same commit.
>
> **Ships as:** single atomic commit. Do not split — the edits all anchor on the v0.5.1 trim decision; splitting creates a window where §12 and §8.8.10 disagree.
>
> **Pre-merge gate for:** B-Hegemony (needs U1/U5/U8/U9/U10/U15 + A3/A4), B-B1-lite (needs U1/U5 + A2), C-lite (needs U1/U5/U8 + A6/A7).

---

## Scope

13 unified findings + 12 addendum items, all documentation. No code changes. No test runs needed (nothing executable moves).

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

---

## Addendum — follow-up findings (2026-04-20)

Second-pass meta-audit surfaced additional drift the combined audit under-sampled. Items A1-A12 ship in the **same atomic commit** as U1-U17 (all doc-only). Priority above minors U11-U17.

| # | Finding | Severity | Primary file | Est. |
|---|---------|----------|--------------|------|
| A1 | §905 internal contradiction — "together with or immediately before the floor is removed" flips direction against §905's own second-sentence prohibition and Plan Option A | BLOCKER | `RELIABILITY_COMMITMENTS_SPEC.md:905` | 10 min |
| A2 | `CLAUDE.md` Up Next Remaining list omits B-B4; test-count pinned at pre-B-B4 total; C-lite slice unversioned | MAJOR | `CLAUDE.md:26` | 10 min |
| A3 | `CLAUDE.md` File Reference row for Memory-and-Pressure substrate missing `COMMITMENTS_PRESENTATION_SPEC.md` / `DIPLOMAT_VOICE_BIBLE.md` / `COALITION_SPEC.md` | MAJOR | `CLAUDE.md:164` | 5 min |
| A4 | `COALITION_SPEC §2a` `hegemony_passive` row does not name the 30/40/50/60% bucket boundaries | MAJOR | `COALITION_SPEC.md:62` | 10 min |
| A5 | §11.1 Balance-of-Europe state machine missing the coalition-cooldown case (post-dissolution 5-turn window per COALITION_SPEC §7d) | MINOR | `RELIABILITY_COMMITMENTS_SPEC.md:1018-1040` | 10 min |
| A6 | Voice Bible `Minimum cast coverage` doesn't cover §12.3 beat-2 paradox-resolved after-choice aside or §12.4 reactive "Summon {envoy}" one-exchange response | MINOR | `DIPLOMAT_VOICE_BIBLE.md:205-212` | 10 min |
| A7 | `SCALE_READINESS_PLAN §DG-4 Amendment` event-type constants are scenario-configurable, but neither that doc nor `RELIABILITY_COMMITMENTS_SPEC §8.8.10` cross-reference each other on the configuration seam | MINOR | `SCALE_READINESS_PLAN.md` + `RELIABILITY_COMMITMENTS_SPEC.md §8.8.10` | 10 min |
| A8 | U6 (Balance-of-Europe payload block) has no Block 1 doc task — the audit §U6 step 1 is a schema-lock, which is doc-only and belongs here | MAJOR | `COMMITMENTS_PRESENTATION_SPEC.md` §11 (new) | 15 min |
| A9 | Block 1 §1b ("icon/label table") and §2 ("routing join-table") duplicate the DG-4 icon/label strings — conflict risk if an author edits one without the other | MAJOR | this work order §1b | 5 min |
| A10 | Block 1 §1d ("retrofit §12.1/§12.2/§12.3") is ambiguous about §12.3 beat-3 **in-popup** aside — risk of over-delete when implementer reads "delete N+1 callback" | MINOR | this work order §1d | 5 min |
| A11 | Block 1 Definition-of-done omits U15 runtime-contract acceptance items | MAJOR | this work order DoD | 5 min |
| A12 | "C-lite ship-checklist" — verified live-code drift that belongs to C-lite §13/§14 scope, but needs to be catalogued now so C-lite doesn't miss them | reference | this work order (new appendix) | 15 min |

**Addendum subtotal: ~2 hours. Combined with U1-U17: ~5 hours.** Still fits a single session and a single atomic commit.

---

### A1 — §905 internal contradiction

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md:905), line 905.

**Current text:**
> **Plan ordering (cross-slice constraint):** `RELIABILITY_IMPLEMENTATION_PLAN.md` must ship B-B4 (DG-4 grievance_modifier) together with or immediately **before** the floor is removed. Under no circumstance may B-B1-lite's no-floor collapse land in code while B-B4's `grievance_modifier` is already live — see plan Execution Order "Merge ordering" paragraph.

The first sentence says "immediately before" (B-B4 lands **before** B-B1-lite's floor removal). The second sentence prohibits exactly that (B-B4 already live while B-B1-lite's no-floor collapse lands). Plan Option A (preferred) at [`RELIABILITY_IMPLEMENTATION_PLAN.md:281`](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:281) says "B-B4 lands **AFTER** or **SIMULTANEOUSLY** with B-B1-lite". CLAUDE.md line 26 says "B-B4 must land **AT or AFTER** B-B1-lite". Both match the second sentence; the first sentence contradicts them.

**Fix:** Replace "together with or immediately **before** the floor is removed" → "together with or immediately **after** B-B1-lite's no-floor collapse lands". The sentence is now internally consistent and matches plan Option A + CLAUDE.md.

---

### A2 — CLAUDE.md Up Next corrections

[`CLAUDE.md`](CLAUDE.md:26), line 26.

Three sub-fixes:

1. **Add B-B4 to Remaining list.** Current: *"Remaining: B-Hegemony … + B-B1-lite … + B-B3 … + B-B7 … + trimmed C-lite presentation (~45-54 tests, ~1.5 sessions — down from v2.3 68-74 / 3 sessions)."* Change to: *"Remaining: B-Hegemony … + B-B1-lite … + B-B3 … + B-B4 (DG-4 call-to-arms + grievance_modifier + composite floor reintroduction) + B-B7 … + trimmed C-lite presentation (v0.5.1) (~70-83 tests incl. B-B4's 25-29, ~2 sessions — down from v2.3 68-74 / 3 sessions)"*.
2. **Pin C-lite to v0.5.1** (was unversioned in Up Next; row 166 has the pin).
3. **Verify merge-gate sentence** after A1 edits (should now read "B-B4 must land AT or AFTER B-B1-lite" on CLAUDE.md — spec §905 and CLAUDE.md + plan now agree).

---

### A3 — CLAUDE.md File Reference row

[`CLAUDE.md`](CLAUDE.md:164), line 164. "Memory and Pressure substrate" row currently lists: spec, scale plan, implementation plan, four code files. Missing:

- `docs/COMMITMENTS_PRESENTATION_SPEC.md` — the C-lite notice/icon/template contract
- `docs/DIPLOMAT_VOICE_BIBLE.md` — the named-envoy register contract
- `docs/COALITION_SPEC.md` — the `hegemony_passive` threat-ladder row and dissolution/cooldown states

Row 166 (C3-lite presentation) already covers presentation spec + Voice Bible for that slice, but row 164 is the entry point for **substrate** implementers (B-Hegemony reads COALITION_SPEC for the ladder interaction). Add all three paths to the row 164 cell.

---

### A4 — COALITION_SPEC §2a breakpoints

[`docs/COALITION_SPEC.md`](docs/COALITION_SPEC.md:62), line 62 (and surrounding note at line ~69). The `hegemony_passive` threat-table row currently reads *"+1/+3/+5/+8/turn (share-scaled ladder)"* with outputs that imply four buckets, but the companion table cell says only "bloc share ≥ 30%". Implementer cannot tell which share bucket produces which output without opening RELIABILITY_COMMITMENTS_SPEC §7.3.

**Fix:** Replace the cell with *"+1 (30% ≤ share < 40%) / +3 (40% ≤ share < 50%) / +5 (50% ≤ share < 60%) / +8 (share ≥ 60%) — per RELIABILITY_COMMITMENTS_SPEC §7.3 ladder; threat ramps with bloc share of continental power"*.

---

### A5 — §11.1 COOLDOWN state case

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md:1018), lines 1018-1040. Current four cases cover no-hegemon, hegemon+no-coalition, BREWING, DECLARED. Missing: COOLDOWN (post-dissolution, 5-turn cool per [COALITION_SPEC.md:491-497](docs/COALITION_SPEC.md:491)). The headline should distinguish *"no coalition yet forming"* (Case 2) from *"coalition just dissolved — hiatus before any can re-form"* (new Case 5).

**Fix:** Add Case 5 to the §11.1 state machine:

> **Case 5 — coalition cooldown:** `coalition_state == COOLDOWN` AND a hegemon may or may not still exceed 30% share. Line reads: *"The last coalition has disbanded. Europe takes breath — no new coalition can form for {turns_remaining} turns."* If `threat_level > 0`, append residual-pressure flavor. BREWING tests must respect cooldown gating (§3 COALITION_SPEC).

---

### A6 — Voice Bible cast-minimums extension

[`docs/DIPLOMAT_VOICE_BIBLE.md`](docs/DIPLOMAT_VOICE_BIBLE.md:203) §Minimum cast coverage (line 203 area). v0.5.1 presentation spec authors two surfaces not listed in the Voice Bible minimum:

1. **§12.3 beat-2 after-choice aside** (line 640-642 of presentation spec): the **spurned** envoy speaks one line after the paradox choice. All four foreign diplomats (Hardenberg, Metternich, Einsiedel, Castlereagh) are candidates depending on which alliance is spurned.
2. **§12.4 reactive "Summon {named_envoy}"** (line 676 of presentation spec): one-exchange foreign-court response to the reactive summon affordance — any foreign cast member may be summoned.

**Fix:** Add to §Minimum cast coverage list (under the existing 4 lead-line templates): *"(5) paradox after-choice aside — one per foreign diplomat, fires when their alliance is the one spurned. (6) reactive summon one-exchange — per foreign cast member."* Note this is additive, not a reduction; the 4-line minimum still holds for lead-lines.

---

### A7 — SCALE_READINESS ↔ RELIABILITY_COMMITMENTS scenario-config seam

[`docs/SCALE_READINESS_PLAN.md`](docs/SCALE_READINESS_PLAN.md) §DG-4 Amendment lines ~321-323 author three scenario-config keys (`refusal_event_type_offensive/defensive`, `honored_costly_event_type`). [`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md:760) §8.8.10 lines 760-762 enumerate the three event types as if hard-coded. Neither cross-references the other.

**Fix:** In RELIABILITY_COMMITMENTS_SPEC §8.8.10, add: *"Event type strings are scenario-configurable via the `cascade_profile.refusal_event_type_offensive / _defensive / honored_costly_event_type` keys in `scenario_schema_version: 1` — see SCALE_READINESS_PLAN §DG-4 Amendment. The defaults above are the canonical strings."* In SCALE_READINESS_PLAN §DG-4 Amendment, add: *"Per RELIABILITY_COMMITMENTS_SPEC §8.8.10 these three events gate the `commitments_notice_call_*` template family."*

---

### A8 — U6 Balance-of-Europe payload schema lock

Combined audit §U6 suggested-fix step 1 is **doc-only** and belongs in Block 1 (not Block 3 / plan-deferred). Add new subsection to presentation spec §11 locking the payload contract:

```
balance_of_europe: {
  hegemon: Optional[str],
  share: float,                      # 0.0-1.0
  threat_level: int,                 # 0-100
  coalition_state: Literal["NONE", "BREWING", "DECLARED", "COOLDOWN"],
  qualifying_nations: List[str],     # nations ≥ 15% share (coalition candidates)
  leader: Optional[str],             # coalition leader if DECLARED
}
```

[`docs/COMMITMENTS_PRESENTATION_SPEC.md`](docs/COMMITMENTS_PRESENTATION_SPEC.md) §11. Add the schema block + note: *"Populated by `build_diplomatic_ledger()` from B-Hegemony engine output; rendered by the Nations-tab headline in C-lite §14. Four state cases per RELIABILITY_COMMITMENTS_SPEC §11.1 (+ Case 5 COOLDOWN per this audit A5)."*

---

### A9 — Dedup §1b ↔ §2 icon/label strings

This work order §1b lists icon keys + labels for the three DG-4 events (`icon_call_refused_offensive` / "Pact Dishonoured", etc.). §2 (U5 routing table) also lists them in the full join-table. Any future edit of one without the other creates a conflict.

**Fix:** Rewrite §1b to read: *"Add DG-4 rows to §9.2 using the icon keys + labels defined in §2's routing join-table (single source of truth — do not restate strings here)."* Delete the bulleted restatement.

---

### A10 — Clarify §1d §12.3 popup fate

This work order §1d says "Delete the `Next-morning callback` and `Optional N+1 aside` blocks". The audit matrix row 6 (`commitment_paradox_resolved`) shows a "§12.3 beat-3 in-popup aside" as a **live surface**. An implementer could over-delete and remove the in-popup aside too.

**Fix:** Append to §1d: *"**Keep** the §12.3 beat-3 **in-popup** aside (rendered inside the paradox popup itself after the player chooses). Only the **post-popup** Next-morning callback and N+1 Talleyrand aside were cut by v0.5.1 — those fire on the turn after the popup closes. The in-popup aside is not a `notification_bar` surface; it is part of `commitment_paradox_popup.gd`'s beat-3 rendering."*

---

### A11 — Block 1 DoD — U15 acceptance items

Current DoD (line 219-227) has no items verifying U15's three runtime-contract additions actually landed. Add:

- [ ] `RELIABILITY_COMMITMENTS_SPEC §319` (or adjacent) contains the logger channel + level + message format for non-France hegemon guard.
- [ ] `COMMITMENTS_PRESENTATION_SPEC §10.3` (or adjacent to §415) contains the `ValueError(f"loyalist register unsupported: {nation}/{personality}")` contract.
- [ ] `RELIABILITY_COMMITMENTS_SPEC §996` (per-turn bloc cache) names the field as `WorldState._bloc_members_cache: Dict[str, Set[str]]` with `invalidate_bloc_members_cache()` invalidator.

Also add:

- [ ] `balance_of_europe` payload schema block present in presentation §11 (per A8).
- [ ] `RELIABILITY_COMMITMENTS_SPEC §905` no longer contains "immediately before the floor is removed" (per A1 — verify with `grep -n "immediately before the floor" docs/RELIABILITY_COMMITMENTS_SPEC.md`).
- [ ] `CLAUDE.md:26` Remaining list contains "B-B4" explicitly (per A2).
- [ ] `CLAUDE.md:164` File Reference row includes `COMMITMENTS_PRESENTATION_SPEC.md`, `DIPLOMAT_VOICE_BIBLE.md`, `COALITION_SPEC.md` (per A3).

---

### A12 — C-lite ship-checklist (verified live-code drift to fix in C-lite §13/§14)

The following live-code gaps are **C-lite scope** (per audit §334, plan row 326) — documented here so C-lite implementer hits them deterministically. All are derived from the §2 routing join-table (the single source of truth).

**In `backend/notifications.py:24-61`:** Add `COMMITMENT_PARADOX_RESOLVED`, `HARD_REJECT_POSTURE_TRIGGERED`, `HARD_REJECT_POSTURE_CLEARED`, `WITNESS_STRIKE_RECORDED`, `CALL_TO_ARMS_REFUSED_OFFENSIVE`, `CALL_TO_ARMS_REFUSED_DEFENSIVE`, `CALL_TO_ARMS_HONORED_COSTLY` notification type constants. Wire each emit site in `diplomacy.py` to create a rail notification (today they emit dispatch entries + event_log only).

**In `godot-client/project-sovereign/scripts/notification_bar.gd:30-42`:** Add `TYPE_ICONS` entries for `icon_paradox`, `icon_paradox_resolved`, `icon_hard_reject`, `icon_chancery_reopened`, `icon_treaty_broken`, `icon_treaty_dragged`, `icon_witness_strike`, `icon_call_refused_offensive`, `icon_call_refused_defensive`, `icon_call_honored_costly`.

**In `backend/game_logic/diplomacy.py:789`:** Replace the unconditional `NotificationPriority.HIGH` for `diplomatic_treaty_broken` with a family-conditional: CRITICAL when `end_reason_family == FRENCH_BREACH`, NORMAL otherwise.

**In `backend/game_logic/dispatch.py:1082, 1111, 1112`:** Correct the `_DIPLOMATIC_EVENT_PRIORITY` map — `hard_reject_posture_triggered` should be CRITICAL (not HIGH); `hard_reject_posture_cleared` should be NORMAL (not MEDIUM); `diplomatic_treaty_broken` must branch on family. Add entries for `witness_strike_recorded` (NORMAL) and `commitment_paradox_resolved` (NORMAL) — currently they fall through to MEDIUM default at line 1303.

**New helper at `backend/game_logic/diplomatic_templates.py` or `speaker_resolver.py`:** `resolve_named_diplomat(speaker: str, nation: str) -> str` — resolves `"foreign_office"` → `"The Chancery of {nation}"` and `"envoy"` → named cast member per Voice Bible. Called by notifications, dispatch, campaign log, popups. Must raise `ValueError` (per U15 contract) when `speaker="envoy"` + non-cast nation.

**New field on rail notifications:** `review_target: Optional[str]` — defaults to `None`; commitments events set per the §2 routing table (e.g., `"ledger_commitments"`). Godot click-handler dispatches to ledger filter action.

**Campaign log dedup:** `backend/campaign_log.py` lines 504-518 vs 673-687 (and 520-530 vs 689-692) have duplicate event-type branches. The second pair is dead code (first return wins). Delete the second pair.

**This checklist is a C-lite pre-merge contract**, not a Block 1 or Block 2 task. Copying it here now ensures the C-lite implementer's file list is complete.

---

## Addendum v2 — third-pass findings (2026-04-20)

Third meta-audit (test-suite + Godot + spec-internal cross-refs) surfaced **one CRITICAL** structural defect plus additional doc drift. Still fits the same atomic Block 1 commit — all doc-only.

| # | Finding | Severity | Primary file | Est. |
|---|---------|----------|--------------|------|
| **CR1** | **`§8.7` has no header** — content orphaned between §8.6.1a and §8.8; 6 cross-references dangle | **CRITICAL** | `RELIABILITY_COMMITMENTS_SPEC.md` ~lines 613-628 | 15 min |
| CR2 | `§12.5` referenced in presentation spec but sections only reach §12.4; paradox scene is at §12.3 | MAJOR | `COMMITMENTS_PRESENTATION_SPEC.md:45, 214` | 5 min |
| CR3 | §11.1 Case 2 silent for `threat_level ∈ [40, 60)` Murmurs band (only [30, 40) has copy) | MINOR | `RELIABILITY_COMMITMENTS_SPEC.md:1023-1026` | 5 min |
| CR4 | §9.3 composite worst-case arithmetic omits `reliability_modifier` (-128 raw should be -134 raw) | MINOR | `RELIABILITY_COMMITMENTS_SPEC.md:901` | 2 min |
| CR5 | `scenario_schema_version: 1` not cross-cited in `RELIABILITY_IMPLEMENTATION_PLAN.md` B-Hegemony slice | MINOR | `RELIABILITY_IMPLEMENTATION_PLAN.md:94` | 5 min |
| G1+G2+G4+G5 | Expanded C-lite ship-checklist (A12) — Godot-side gaps in `diplomatic_ledger.gd` + `dispatch_view.gd` + `incoming_proposal_popup.gd` | reference | A12 expansion | 10 min |

**Addendum v2 subtotal: ~45 min. Combined Block 1: ~5.75 hours.** Still one atomic commit.

---

### CR1 — §8.7 missing section header (CRITICAL)

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md) — the document jumps from `### 8.6.1 Active redemption: Make Amends` (line 539) → `#### 8.6.1a` (grievance variant) → directly to `### 8.8 Call-to-arms refusal episodes` (line 629). **There is no `### 8.7` section header.** Content that should be under §8.7 (hard-reject posture: 3-strike threshold, survival-exception, `hard_reject_posture_triggered` emit contract) is orphaned after §8.6.1a and reads as if it belongs to the grievance variant.

**Six internal cites dangle:**
- Line 698: *"parallel in shape to §8.7 `hard_reject_posture` but keyed on refusal history"*
- Line 878: *"§8.7 survival-exception path with 4+ strikes computes -24+"*
- Line 883: *"the 3-strike hard-reject (§8.7, already shipped)"*
- Line 886: *"reachable only via the §8.7 survival-exception path"*
- Line 958: *"per §9.2 + §8.7 hard-reject posture"*
- Line 1382 (changelog): *"Survival-exception proposals (§8.7) with 4+ strikes compute -24+"*

**Fix:** Locate the orphaned content (between the end of §8.6.1a and line 629) and insert a `### 8.7 Hard-reject posture` header immediately before it. The section body is already written; only the header is missing. Verify by running:
```bash
grep -n "^### 8\." docs/RELIABILITY_COMMITMENTS_SPEC.md
```
Expected: `8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.6.1, 8.6.1a, 8.7, 8.8`. Currently the output shows no `8.7`.

**This is the single most important Block 1 fix** — every other §8.7 cite in the spec, plan, and downstream artifacts points into a structural void.

---

### CR2 — §12.5 dangling reference

[`docs/COMMITMENTS_PRESENTATION_SPEC.md`](docs/COMMITMENTS_PRESENTATION_SPEC.md:45) lines 45 and 214 reference `§12.5` for paradox staging. The §12.x sections only reach §12.4 (Reactive affordances at line 667). The paradox scene lives at §12.3 (line 608, "Commitment paradox (3-beat staged)").

**Line 45 current:** *"**Paradox §12.5 staging simplifies from 5 beats to 3 beats** — Talleyrand framing → blocking body → spurned-envoy + Talleyrand after-choice."*
**Fix:** `§12.5` → `§12.3`.

**Line 214 current:** *"Three-beat staged scene per §12.5; the after-choice aside renders inside the popup, not as a later callback."*
**Fix:** `§12.5` → `§12.3`.

**Line 807** (changelog) is historical — references the old 5-beat staging that got narrowed back in v0.3 rescope. Leave as-is (audit history).

---

### CR3 — §11.1 Case 2 Murmurs-band silence

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md:1023), lines 1023-1026. Case 2 (hegemon without coalition) gates the "European courts have taken note" line on `30 ≤ threat_level < 40` (the Tension band per COALITION_SPEC §3a). The `[40, 60)` Murmurs band still matches Case 2 (no coalition yet formed) but has no secondary-line template — the player sees only the bare hegemon-share line despite notable threat.

**Fix:** Extend the gate to cover the full Tension-to-Murmurs range, or author a distinct Murmurs-band line:
- Option A: change the gate to `30 ≤ threat_level < 60`; reuse the Tension copy.
- Option B: add a second flavor line template for `40 ≤ threat_level < 60` — stronger wording (e.g., *"European courts exchange quiet letters — nothing yet agreed"*).

Authoring choice at spec-writer's discretion. Whichever way, the `threat_level` state space must partition without silence.

---

### CR4 — §9.3 worst-case arithmetic

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md:901), line 901 worst-case example *"reaches -128 raw"* omits `reliability_modifier` from §9.4 (clamps `// 10` ±6, worst case -6). Actual worst-case raw composite = -20 + -18 + -90 + -6 = -134. The -60 floor still clamps correctly, so behavior is unaffected; the illustrative arithmetic is short one term.

**Fix:** Replace `-20 + -18 + -90 = -128` → `-20 + -18 + -90 + -6 = -134` and add parenthetical *"(reliability_modifier at floor; §9.4)"*.

---

### CR5 — scenario_schema_version cross-cite

[`docs/RELIABILITY_IMPLEMENTATION_PLAN.md`](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:94), line 94 B-Hegemony prerequisite block says `power_tier` is colocated with capital/color/starting AP in scenario config but does not cite `scenario_schema_version: 1` (the key SCALE_READINESS_PLAN introduced at DG-6).

**Fix:** Append to the bullet: *"— per `scenario_schema_version: 1` (see SCALE_READINESS_PLAN §DG-6)"*. This makes the plan self-contained for the B-Hegemony implementer.

---

### G1/G2/G4/G5 — expand C-lite ship-checklist (A12 expansion)

A12 catalogs notification_bar + dispatch + notifications.py drift. Third-pass audit found four more Godot surfaces with v2.4.3 drift. Append to the C-lite ship-checklist section above:

**In `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`:**
- `_render_nations()` lines ~181-322 must emit the Balance of Europe headline (per A8 payload schema) at the top of the Nations tab — currently jumps straight into the nation loop.
- `_render_talleyrand()` line ~672, ~688-689 treats `diplomatic_reliability` as a Talleyrand scalar. Per spec §6.1 it is a `Dict[str, int]` keyed by nation (nation-level global reputation). Move the render to per-nation rows in the Nations tab (one reliability value per nation row, per spec §11.1 commitment block).
- `_render_history()` lines ~692-722 renders event type names with `h_type.replace("_", " ").capitalize()` (produces "Diplomatic Treaty Broken"). The spec §9.2 canonical labels are "Word Broken", "The Chancery Shut", "The Wound Chosen". Add a label-map keyed on the routing join-table (A12 §2) rather than relying on string mangling.

**In `godot-client/project-sovereign/scripts/dispatch_view.gd`:**
- Lines ~249-265 render `diplomatic_events` with generic `text + priority` only. Per spec §9.2 CRITICAL commitments events need their specific icons and canonical labels. Wire through the same routing join-table (A12 §2) so dispatch surface matches notification_bar surface.

**In `godot-client/project-sovereign/scripts/incoming_proposal_popup.gd`:**
- Lines ~44, 46, 73-80 double-render `decision_reason` — "Court rationale" (line 74) + "Court motive" (line 80) display the same field via two different resolution paths. After U4's `hegemony_pressure` rename, both paths yield the same display string and the duplicate becomes visible to the player. Consolidate to one render site; remove the fallback-resolved duplicate.

**Verification notes (likely clean, confirm during C-lite):**
- `talleyrand_objection_popup.gd:36-46` hardcodes MILD/MODERATE/STRONG concern levels — orthogonal to v2.4.3's `hegemony_pressure` rename because `objection_text` is backend-preformatted prose. Confirm objection payloads remain pre-formatted during C-lite's backend pass.
- `diplomacy_wizard.gd:323-402` renders `acceptance_preview.positive/negative[]` generically. If backend preview emits `category: "hegemony"` warnings per spec §11.2, wizard may need a category-specific affordance. Verify backend preview shape during B-Hegemony.

**Clean Godot surfaces** (no v2.4.3 drift): `api_client.gd`, `war_status_panel.gd`, `war_detail_popup.gd`, `sabotage_discovery_popup.gd`, `vassal_rebellion_popup.gd`, `coalition_declaration_popup.gd`, `campaign_log.gd`, `mailbox_panel.gd`, `top_bar.gd`. No Godot-side `.gd` test files exist.
