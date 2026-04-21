# MP v2.4.3 — Block 1: Doc-Only Cleanup

> **Source:** 4 audit passes landed across [`MP_V243_AUDIT_COMBINED.md`](docs/audits/MP_V243_AUDIT_COMBINED.md) + [`MP_V243_AUDIT_PASS4.md`](docs/audits/MP_V243_AUDIT_PASS4.md) + two follow-up passes (commits c88b013, 5fcc93c). This work order integrates all doc-only findings as first-class items — no addendum sectioning.
>
> **Ships as:** single atomic commit. All edits anchor on the v2.4.3 contract; splitting creates windows where sections disagree.
>
> **Pre-merge gate for:** B-Hegemony (needs CR1, A1, A4, A8, P4C1-P4C5, U5, U15). B-B1-lite (needs U1, U5, A1, P4C6). B-B3 (needs P4C8-P4C10, U7). B-B4 (needs P4C11-P4C13, A1). B-B7 (needs P4C14). C-lite (needs U1, U5, U8, P4C15-P4C16, A12).
>
> **Total effort:** ~8 hours one focused session. 50 items across 5 severity tiers.

---

## Scope summary

| Severity | Count | Block 1 dimension |
|----------|-------|-------------------|
| CRITICAL | 1 | Structural spec defect |
| BLOCKER | 2 | Contract contradictions |
| MAJOR (spec edits) | 9 | Spec-internal drift |
| MAJOR (project-nav docs) | 5 | CLAUDE.md / STATUS.md / ROADMAP.md / SYSTEMS_REFERENCE.md |
| MAJOR (plan edits) | 14 | Slice prerequisite precision |
| MAJOR (work-order self-fixes) | 2 | Block 1 internal consistency |
| MINOR (spec edits) | 12 | Comment / arithmetic / prose hygiene |
| MINOR (project-nav docs) | 7 | Secondary doc drift |
| MINOR (plan edits) | 5 | Plan wording / session-count hygiene |
| MINOR (work-order self-fixes) | 1 | Block 1 internal consistency |
| Reference (C-lite ship-checklist) | 1 | Out-of-scope but catalogued |

---

## CRITICAL

### 1. CR1 — `§8.7` has no section header

[`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md) — the spec jumps from `### 8.6.1 Active redemption: Make Amends` (line 539) → `#### 8.6.1a` grievance variant → directly to `### 8.8 Call-to-arms refusal episodes` (line 629). No `### 8.7` header exists. Hard-reject posture content (3-strike threshold, survival-exception, `hard_reject_posture_triggered`) is orphaned after §8.6.1a and visually belongs to the grievance variant subsection.

**Six internal cites dangle:** lines 698, 878, 883, 886, 958, 1382.

**Fix:** Insert `### 8.7 Hard-reject posture` header immediately before the orphaned content (between §8.6.1a end and line 629). Section body is already written.

**Verify:** `grep -n "^### 8\." docs/RELIABILITY_COMMITMENTS_SPEC.md` should list `8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.6.1, 8.6.1a, 8.7, 8.8`.

---

## BLOCKERS

### 2. U1 — v0.5.1 trim leak (§12 + DG-4 + cross-refs)

Source: combined audit §U1.

**2a. Presentation spec §8.1 event routing table — add DG-4 rows.** [`docs/COMMITMENTS_PRESENTATION_SPEC.md:213-220`](docs/COMMITMENTS_PRESENTATION_SPEC.md:213). Append three rows via the §2 routing join-table (see item 4 below).

**2b. Presentation spec §9.2 icon/label table — add DG-4 icons + labels.** Reference the §2 routing join-table (do NOT restate strings — see A9 dedup fix in item 15).

**2c. Presentation spec §13 core tasks — add DG-4 template stubs.** Add a bullet naming `commitments_notice_call_refused_offensive/defensive/honored_costly`.

**2d. Presentation spec §12.1/§12.2/§12.3 — retrofit worked examples.**
- Relabel "spotlight" → "CRITICAL notice" throughout.
- Collapse "two-beat split-voice card" → "single-voice card with named-diplomat inline attribution".
- **Delete** the `Next-morning callback` and `Optional N+1 aside` blocks. Preserve verbatim in `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` under a new appendix "v0.3 deferred prose (moved by v0.5.1 trim — retained as design intent for WB-D)".
- **Keep** the §12.3 beat-3 **in-popup** aside (part of `commitment_paradox_popup.gd`'s beat-3 rendering — NOT a post-popup callback). This is A10's clarification.

**2e. §8.8.5 cross-ref.** [`RELIABILITY_COMMITMENTS_SPEC.md:692`](docs/RELIABILITY_COMMITMENTS_SPEC.md:692): replace *"Emits `call_to_arms_honored_costly` spotlight through C3-lite presentation (see §8.8.8)"* → *"Emits `call_to_arms_honored_costly` CRITICAL notice through C3-lite presentation (see §8.8.10)"*.

**2f. §8.8.10 language.** [lines 758-768](docs/RELIABILITY_COMMITMENTS_SPEC.md:758):
- "authored spotlight and notice copy" → "CRITICAL notice copy (no spotlight tier in C3-lite v0.5.1)"
- "Victim's diplomat leads the refusal spotlight" → "Victim's diplomat voices the CRITICAL notice"

**Verify:** `grep -n spotlight docs/RELIABILITY_COMMITMENTS_SPEC.md docs/COMMITMENTS_PRESENTATION_SPEC.md` → only historical/changelog/stub references remain.

### 3. A1 — Spec §905 internal contradiction

[`docs/RELIABILITY_COMMITMENTS_SPEC.md:905`](docs/RELIABILITY_COMMITMENTS_SPEC.md:905).

**Current:** *"must ship B-B4 (DG-4 grievance_modifier) together with or immediately **before** the floor is removed. Under no circumstance may B-B1-lite's no-floor collapse land in code while B-B4's `grievance_modifier` is already live"*

The first sentence says B-B4 lands **before** B-B1-lite. The second sentence prohibits exactly that. Plan Option A (preferred) + CLAUDE.md line 26 agree with the second sentence, not the first.

**Fix:** "together with or immediately **before** the floor is removed" → "together with or immediately **after** B-B1-lite's no-floor collapse lands".

**Verify:** `grep -n "immediately before the floor" docs/RELIABILITY_COMMITMENTS_SPEC.md` returns nothing.

---

## MAJOR — Spec edits

### 4. U5 — Commitments routing join-table (single source of truth)

[`docs/COMMITMENTS_PRESENTATION_SPEC.md §8.1`](docs/COMMITMENTS_PRESENTATION_SPEC.md:213). Add **one** join-table that notifications / dispatch / campaign log / popups / ledger all derive from:

| Event family | Priority | Icon key | Player label | Template key | Speaker resolver | Review target |
|--------------|----------|----------|--------------|--------------|------------------|---------------|
| `commitment_paradox` | HARD_STOP (popup) | `icon_paradox` | "Conflicting Oaths" | `commitments_notice_paradox` | `talleyrand` | `ledger_commitments` |
| `balance_of_europe_shifted` | NORMAL | `icon_balance_of_europe` | "Balance of Europe Shifts" | `commitments_notice_balance_of_europe_shifted` | `envoy` → resolved `speaker_nation`, else `foreign_office` → "The Chancery of {nation}" | Open Ledger |
| `amends_offered` | NORMAL | `icon_amends_offered` | "Amends Offered" | `commitments_notice_amends_offered` | `envoy` → target court's named diplomat | Open Ledger |
| `hard_reject_posture_triggered` | CRITICAL | `icon_hard_reject` | "The Chancery Shut" | `commitments_notice_hard_reject_triggered` | `foreign_office` → "The Chancery of {nation}" | Open Ledger |
| `hard_reject_posture_cleared` | NORMAL | `icon_chancery_reopened` | "The Chancery Reopens" | `commitments_notice_hard_reject_cleared` | `foreign_office` → "The Chancery of {nation}" | Open Ledger |
| `diplomatic_treaty_broken` (`french_breach`) | CRITICAL | `icon_treaty_broken` | "Word Broken" | `commitments_notice_breach_french` | `envoy` → victim's diplomat | "Review the broken treaty" |
| `diplomatic_treaty_broken` (other) | NORMAL | `icon_treaty_dragged` | "Treaty Dragged Apart" | `commitments_notice_breach_other` | `foreign_office` → context | Open Ledger |
| `commitment_paradox_resolved` | NORMAL | `icon_paradox_resolved` | "The Wound Chosen" | `commitments_notice_paradox_resolved` | `talleyrand` (notice) / `system` (log) | — |
| `witness_strike_recorded` | NORMAL | `icon_witness_strike` | "Europe Is Aware" | `commitments_notice_witness_strike` | `system` / `foreign_office` per scope | — |
| `call_to_arms_refused_offensive` | CRITICAL | `icon_call_refused_offensive` | "Pact Dishonoured" | `commitments_notice_call_refused_offensive` | `envoy` → victim's diplomat | Open Ledger |
| `call_to_arms_refused_defensive` | CRITICAL | `icon_call_refused_defensive` | "Ally Abandoned" | `commitments_notice_call_refused_defensive` | `envoy` → victim's diplomat | Open Ledger |
| `call_to_arms_honored_costly` | CRITICAL | `icon_call_honored_costly` | "Oath Kept" | `commitments_notice_call_honored_costly` | `foreign_office` → "The Chancery of France" | Open Ledger |

Flag as: *"Single source of truth. Notifications, dispatch formatter, campaign log, popups, and ledger MUST derive priority/icon/label/template/voice/review-target from this row — do not hardcode elsewhere."*

Add note under the row: *"`balance_of_europe_shifted` is the same-turn 33% / 50% / 60% hegemony preview beat from `RELIABILITY_COMMITMENTS_SPEC.md` §4.1 / §11.1 and `RELIABILITY_IMPLEMENTATION_PLAN.md` B-Hegemony. It exists so coalition declaration is never the player's first clue."*

Add note under `amends_offered`: *"Both standard and grievance-variant Make Amends use this row. The target court's named acknowledgment is mandatory so apology reads as public politics rather than a quiet stat purchase."*

### 5. U7 — `SAVE_FORMAT_REFERENCE.md` refresh

- Line 12: `Format version: 1.0` → `Format version: 1.1`.
- Line 14: Update compatibility statement to `Memory and Pressure v2.4.3 substrate (betrayal_history, next_episode_id, nation-level diplomatic_reliability) + Diplomacy Button Session A`.
- Lines 107-109: Show nation-level `diplomatic_reliability`; add `betrayal_history: []`; add `next_episode_id: 1`; note `alliance_paradox_popup` as **legacy alias**, canonical is `commitment_paradox_popup` (v2.4.3), `from_dict` accepts both.
- Line 190: Reference `commitment_paradox` in pending_dialogue_queue (with alias note).
- Lines 224-226: Rewrite `diplomatic_reliability` row to nation-level; footnote legacy per-pair as v1.0.
- Lines 874-875: Update sample `game_version` to current.
- Add row: `reparations_cooldown: {}` — status "Planned (B-B7)".

### 6. A8 — Balance of Europe payload schema lock

[`docs/COMMITMENTS_PRESENTATION_SPEC.md §11`](docs/COMMITMENTS_PRESENTATION_SPEC.md) — add subsection:

```
balance_of_europe: {
  hegemon: Optional[str],
  share: float,                      # 0.0-1.0
  threat_level: int,                 # 0-100
  coalition_state: Literal["NONE", "BREWING", "DECLARED", "COOLDOWN"],
  qualifying_nations: List[str],     # ≥ 15% share
  leader: Optional[str],             # coalition leader if DECLARED
}
```

Note: *"Populated by `build_diplomatic_ledger()` from B-Hegemony engine output; rendered by Nations-tab headline in C-lite §14. Five state cases per RELIABILITY_COMMITMENTS_SPEC §11.1 (incl. COOLDOWN per A5)."*

### 7. A4 — COALITION_SPEC §2a breakpoints named

[`docs/COALITION_SPEC.md:62`](docs/COALITION_SPEC.md:62). Hegemony_passive row currently: *"+1/+3/+5/+8/turn (share-scaled ladder)"* / cell says "bloc share ≥ 30%".

**Fix cell:** *"+1 (30% ≤ share < 40%) / +3 (40% ≤ share < 50%) / +5 (50% ≤ share < 60%) / +8 (share ≥ 60%) — per RELIABILITY_COMMITMENTS_SPEC §7.3 ladder; threat ramps with bloc share of continental power"*.

### 8. U8 — Voice Bible v0.3 → v0.5.1

[`docs/DIPLOMAT_VOICE_BIBLE.md`](docs/DIPLOMAT_VOICE_BIBLE.md):
- Line 4: `v0.3 scope note (Apr 16, 2026)` → `v0.5.1 scope note (2026-04-20)`.
- Line 6: `COMMITMENTS_PRESENTATION_SPEC.md v0.3 §10.3` → `v0.5.1 §10.3`.
- Status line 3: `v1 draft — Apr 15, 2026` → `v1.1 — v0.5.1 aligned — 2026-04-20`.
- Line 203 heading: `(v0.3 — must land...)` → `(v0.5.1 — must land...)`.
- Minimum cast coverage: add the four `balance_of_europe_shifted` warning families (`Castlereagh`, `Hardenberg`, `Metternich`, `Einsiedel`, each with noticed / alarming / crisis variants) and four `amends_offered` acknowledgment lines.
- Add changelog: *"v1.1 (2026-04-20): labels realigned to presentation v0.5.1; minimum live coverage expanded to hegemony beats + Make Amends acknowledgments."*

### 9. U10 — B-Hegemony test bullet (3 vs 4 Balance-of-Europe cases)

[`docs/RELIABILITY_IMPLEMENTATION_PLAN.md:132`](docs/RELIABILITY_IMPLEMENTATION_PLAN.md:132). Recommended: remove the Balance-of-Europe test bullet from B-Hegemony entirely; all 4 (now 5 per A5) state-case tests live in C-lite §14.

### 10. U15 — Runtime contracts (logger / ValueError / cache field)

Add to [`docs/RELIABILITY_COMMITMENTS_SPEC.md`](docs/RELIABILITY_COMMITMENTS_SPEC.md) near §996:

**Logger for non-France hegemon guard** (§319):
- Channel: `logging.getLogger("backend.game_logic.coalition")`, level `INFO`.
- Format: `[hegemony] non-France hegemon detected ({hegemon_nation} @ {share:.2f}); skipping add_threat (threat scalar France-targeted in v0.1)`.
- Rate: once per turn per actor.

**Fail-loud shape** (presentation §10.3 / §415):
- `raise ValueError(f"loyalist register unsupported: {nation}/{personality}")`.

**Per-turn bloc cache** (§996):
- `WorldState._bloc_members_cache: Dict[str, Set[str]]` (leader → members).
- `invalidate_bloc_members_cache()` called from same seams as `invalidate_active_nations_cache()` PLUS §8.8.7a same-turn alliance termination (P4C4).

Add to presentation §10.3: *"When `speaker='envoy'` cannot resolve, raise ValueError per above; do not silently fall back to `system`."*

### 11. U16 — Non-cast nation fallback scope

[`docs/COMMITMENTS_PRESENTATION_SPEC.md §10.3`](docs/COMMITMENTS_PRESENTATION_SPEC.md:413). Add: *"v0.1 scope assumes the 5-nation roster (France + Britain + Austria + Prussia + Saxony). If a future event targets a non-cast nation, the render falls back to `foreign_office` → 'The Chancery of {nation}' with no personality register until the cast expands. The fail-loud `ValueError` fires only for the named-diplomat resolver path (`speaker='envoy'` + cast nation); it does not fire on the non-cast fallback."*

### 12. CR2 — `§12.5` dangling refs

[`docs/COMMITMENTS_PRESENTATION_SPEC.md`](docs/COMMITMENTS_PRESENTATION_SPEC.md):
- Line 45: `§12.5` → `§12.3`.
- Line 214: `§12.5` → `§12.3`.
- Line 807 (changelog): leave as-is (historical).

---

## MAJOR — Project-navigation docs

### 13. A2 — CLAUDE.md Up Next corrections

[`CLAUDE.md:26`](CLAUDE.md:26):
1. Add B-B4 to Remaining list. Change *"Remaining: B-Hegemony ... + B-B1-lite ... + B-B3 ... + B-B7 ... + trimmed C-lite presentation (~45-54 tests, ~1.5 sessions ...)"* → *"Remaining: B-Hegemony ... + B-B1-lite ... + B-B3 ... + B-B4 (DG-4 call-to-arms + grievance_modifier + composite floor reintroduction) + B-B7 ... + trimmed C-lite presentation (v0.5.1) (~70-83 tests incl. B-B4's 25-29, ~2 sessions)"*.
2. Verify merge-gate sentence matches spec §905 after item 3's fix.

### 14. A3 — CLAUDE.md File Reference row

[`CLAUDE.md:164`](CLAUDE.md:164). Add to the "Memory and Pressure substrate" cell: `docs/COMMITMENTS_PRESENTATION_SPEC.md`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `docs/COALITION_SPEC.md`. B-Hegemony needs COALITION_SPEC; C-lite needs the other two directly.

### 15. D1+D2 — STATUS.md v2.1 slice list + cold-start misroute

[`docs/STATUS.md`](docs/STATUS.md):
- Lines 73, 127: delete "pick up Memory and Pressure — Slice A (rivalry seed)" routing. Replace with "pick up Memory and Pressure — B-Hegemony (engine + bloc helpers + Balance of Europe)".
- Lines 195-196, 232-239: rewrite v2.1 slice list (rivalry seed, direct_rivalry_mod, rival_conflict_mod, composite political_commitment_mod, redemption tick Slice B6, spotlight/attributed_lines/N+1) to v2.4.3 slice list (hegemony engine, hegemony_target_mod, flat -6 per strike, B6 cancelled, single-voice CRITICAL notices only).

### 16. D3 — ROADMAP.md v2.1 citation

[`docs/ROADMAP.md:196`](docs/ROADMAP.md:196). Update Post-Phase-8 Refinement Order table: v2.1 → v2.4.3; "68-74 tests / ~3 sessions" → "~70-83 tests / ~2 sessions"; presentation v0.3 → v0.5.1.

### 17. D10 — SYSTEMS_REFERENCE.md §21+§22 update

[`docs/SYSTEMS_REFERENCE.md`](docs/SYSTEMS_REFERENCE.md):
- §21 line ~3534 Diplomatic Reliability: rewrite to v2.4.3 narrowed shape (`clamp(// 10, -6, +6)` not `±10`).
- §22 line ~3564 popup priority list item 7: `alliance_paradox_popup` → `commitment_paradox_popup` (with alias note).

**Rationale:** SYSTEMS_REFERENCE is one of three "essential for Chat" docs per MEMORY.md; drift here misleads cross-conversation reasoning.

---

## MAJOR — Plan edits

### 18. P4C1-P4C5 — B-Hegemony prerequisites precision

[`docs/RELIABILITY_IMPLEMENTATION_PLAN.md`](docs/RELIABILITY_IMPLEMENTATION_PLAN.md) lines ~90-140.

- **P4C1:** Add `WorldState._bloc_members_cache: Dict[str, Set[str]]` explicitly to B-Hegemony prerequisite field list (per U15 contract).
- **P4C2:** Decide — `world.get_bloc_members(leader)` method OR `get_bloc_members(world, leader)` module function. Update both plan and spec §7.1 to match.
- **P4C3:** Name `bloc_power` and `power_score` locations (likely `backend/game_logic/coalition.py`) + their import path into `diplomacy.py` for `hegemony_target_mod`.
- **P4C4:** Cache invalidation list must include §8.8.7a same-turn alliance termination as fifth invalidation site.
- **P4C5:** `coalition_leadership_score` wire-up — specify `european_power` denominator as arg or helper call.

### 19. P4C6 — B-B1-lite legacy variable removal explicit

Plan line ~139. Replace vague *"Replace existing acceptance formula's `direct_concern_mod` / `concern_conflict_mod` slots"* with explicit removal list: `direct_concern_mod`, `concern_conflict_mod`, `political_commitment_mod` (old composite). Clarify what B-B1-lite must **delete** vs **narrow**.

### 20. P4C8-P4C10 — B-B3 rename scope

Plan lines ~156-166 — add to rename scope list:
- `backend/models/dialogue_manager.py:86` — `DIALOGUE_PRIORITY` must gain `"commitment_paradox": 0` entry.
- `backend/models/world_state.py:497` — `alliance_paradox_popup` attribute rename (with alias-on-load).
- `docs/SAVE_FORMAT_REFERENCE.md` — alias-on-load policy documentation (see item 5 above).

### 21. P4C11-P4C13 — B-B4 deliverables precision

Plan lines ~189-213:
- **P4C11:** Add `END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION` constant to Files/Work list (emitter constant + `display_names.py` label).
- **P4C12:** State `grievance_modifier = -30 per grievance, saturating at 3 active grievances per asker-target pair (max -90)` in Files/Work — currently only in test bullet.
- **P4C13:** Composite floor `-60` reintroduction listed only in Merge-ordering paragraph; add to B-B4 Files/Work list explicitly.

### 22. P4C15-P4C16 — C-lite prerequisites

Plan lines ~216-233 — add to C-lite Files/Work list:
- `commitments_notice_*` template family (10 templates per §2 join-table).
- `notification_bar.gd` TYPE_ICONS extension (10 icon keys).
- `notifications.py` priority-tier mapping (map commitments types → priority).
- `review_target` routing field + Godot click-handler.
- Campaign-log dedup by `episode_id` (§13 anti-spam).
- Balance of Europe payload additions in `build_diplomatic_ledger()`.
- `incoming_proposal_popup.gd` duplicate decision_reason render fix.
- `resolve_named_diplomat(speaker, nation)` helper location: `backend/game_logic/diplomatic_templates.py` (or new `speaker_resolver.py`).

### 23. P4C17 — Plan vs spec B-B4 test count

Plan line ~327: B-B4 "25-29". Spec §8.8.13 line 807: "~25 new". **Fix:** update spec §8.8.13 to "~25-29 new" (match plan), or narrow plan to "~25" (match spec). Pick one.

---

## MAJOR — Work-order self-fixes

### 24. A9 — Dedup §1b ↔ §2 icon/label strings

Both item 2b and item 4 above list DG-4 icon/label strings. Item 2b rewrites to: *"Add DG-4 rows to §9.2 using the icon keys + labels defined in §4's routing join-table (single source of truth — do not restate strings here)."*

### 25. A11 — Block 1 DoD acceptance items

See "Definition of done" below for the full DoD list including all U15 runtime-contract items, A1 grep verification, A2 B-B4-in-Remaining check, A3 File Reference additions, A8 payload schema presence, CR1 header grep.

---

## MINOR — Spec edits

### 26-37

**26. U9** — Presentation §9.2: *"Commitments events use CRITICAL or NORMAL only. HIGH tier (used by MARSHAL_DEFIED_ORDER) is intentionally not used."*

**27. U11** — RCS §11.1 Case 1 lines 1018-1021: replace self-contradiction with *"The equilibrium line is standalone. If a coalition is independently brewing from event-based threat (battles, captures), a BREWING line from Case 3 may still render below it; composable."*

**28. U12** — RCS §11.1 Case 2 line 1026: add *"When `threat_level < 30` with hegemon present, render only the hegemon line; flavor line suppressed."*

**29. U13** — RCS §843-848 hegemony_target_mod comment: *"clamped at -20 from 63.33%+ onward"* → *"clamped at -20 from ~63.34%+ onward (integer truncation of raw = 20 clamps to max ceiling)"*.

**30. U14** — Presentation §10.3 line 402: drop `per §10.3` self-ref qualifier OR move rule inline.

**31. U17** — Plan line 329 total row: correct to `~46-53` to match row sum, OR annotate `~45-54 (approx. — rows sum to 46-53)`.

**32. A5** — RCS §11.1 add Case 5 COOLDOWN: *"`coalition_state == COOLDOWN`. Line: 'The last coalition has disbanded. Europe takes breath — no new coalition can form for {turns_remaining} turns.' If `threat_level > 0`, append residual-pressure flavor."*

**33. A6** — Voice Bible §Minimum cast coverage: add *"(5) paradox after-choice aside — one per foreign diplomat, fires when their alliance is spurned. (6) reactive summon one-exchange — per foreign cast member."* Note: additive to the 4-line lead-line minimum.

**34. A7** — Cross-cite SCALE_READINESS §DG-4 Amendment and RCS §8.8.10 on `cascade_profile.*` scenario-config keys. Each doc should point at the other.

**35. CR3** — RCS §11.1 Case 2 threat_level [40, 60) Murmurs band: extend gate to `30 ≤ threat_level < 60` with shared copy, OR author distinct Murmurs line.

**36. CR4** — RCS §901 worst-case arithmetic: `-20 + -18 + -90 = -128` → `-20 + -18 + -90 + -6 = -134 (reliability_modifier at floor; §9.4)`.

**37. CR5** — Plan line 94 B-Hegemony prerequisite block: append *"— per `scenario_schema_version: 1` (see SCALE_READINESS_PLAN §DG-6)"* to power_tier bullet.

---

## MINOR — Project-navigation docs

### 38-44

**38. D4** — `docs/COMMITMENTS_PLAYTEST_SCRIPT.md:4` update stale commit reference; add B-Hegemony Balance-of-Europe headline probes and named-diplomat helper probes to Q3/Q4 debrief.

**39. D5** — Voice Bible §Minimum cast coverage add Chancery-voice `hard_reject_clear` copy + `witness_strike` reactions (beyond A6 paradox/summon).

**40. D6** — `docs/ADDING_CONTENT.md:910-1045` §Adding New Nations: add `power_tier` authored field (`major | secondary | minor`) to the 9-step checklist. Note: missing field silently defaults to `"secondary"`, hiding scenario errors.

**41. D7** — `docs/MODDING_FORMAT.md:471` bump format version to 1.1. Add `scenario_schema_version: 1` and `power_tier` / `political_status` split to Nations section.

**42. D8+D9** — `docs/DESIGN_REFINEMENT.md:115-122, 121` — R17d DP Breakdown + R119/R160/R162 — replace v2.1 citations with v2.4.3 (hegemony_target_mod, bilateral_betrayal_mod, grievance_modifier). R160 note: static rivalries dropped entirely in v2.4.3, not superseded by v2.1 §7.

**43. D11** — `docs/ARCHITECTURE_REFACTORING_PLAN.md:1077, 2092, 2138, 2195` — four sites cite `alliance_paradox_popup` as canonical. Add alias note or update to `commitment_paradox_popup`.

**44. D12** — `docs/BUG_FIXES.md:644` — hard-stop list names `alliance_paradox`. Add alias note.

---

## MINOR — Plan edits

### 45-49

**45. P4C7** — B-B1-lite test bullet line ~149: *"scales linearly -1 to -20"* — fix to match §9.1 integer-truncation (0 at 30% boundary, -18 at 60%, clamp at -20 from 63.34%).

**46. P4C10** — B-B3 silent on SAVE_FORMAT update; add explicit cross-ref to item 5 above.

**47. P4C14** — B-B7 line ~182 `reparations_cooldown` add requires `test_serialization_enforcement.py` round-trip (CLAUDE.md mandatory rule).

**48. P4C18** — Plan line ~6 session count "~1.5 effective" vs total ~70-83 tests: update to "~2 sessions (~30-40 tests per session at current pace)".

**49. P4C19** — Plan Merge-ordering Option B "remove only the *explanatory surface*" — define explicitly: *"remove `components['political_commitment_mod']` from the acceptance formula debug emit but retain the `political_commitment_mod` dict key as a computed view over the new terms"* OR whatever the intent is. Undefined as written.

---

## MINOR — Work-order self-fixes

### 50. A10 — §1d §12.3 in-popup aside clarification

Already folded into item 2d above. (Ensure the "Keep the §12.3 beat-3 in-popup aside" note lands during retrofit.)

---

## Reference — C-lite ship-checklist (A12 + G1/G2/G4/G5)

Not a Block 1 task — catalogued here so C-lite implementer hits them deterministically. All derive from item 4 (the §2 routing join-table, single source of truth).

**In `backend/notifications.py:24-61`:** Add `COMMITMENT_PARADOX_RESOLVED`, `HARD_REJECT_POSTURE_TRIGGERED`, `HARD_REJECT_POSTURE_CLEARED`, `WITNESS_STRIKE_RECORDED`, `CALL_TO_ARMS_REFUSED_OFFENSIVE`, `CALL_TO_ARMS_REFUSED_DEFENSIVE`, `CALL_TO_ARMS_HONORED_COSTLY` notification types. Wire emit sites in `diplomacy.py` to create rail notifications.

**In `godot-client/project-sovereign/scripts/notification_bar.gd:30-42`:** Add `TYPE_ICONS` entries for 10 commitments icon keys per join-table.

**In `backend/game_logic/diplomacy.py:789`:** Make `diplomatic_treaty_broken` priority conditional on family (CRITICAL for `french_breach`, NORMAL otherwise).

**In `backend/game_logic/dispatch.py:1082, 1111, 1112`:** Correct `_DIPLOMATIC_EVENT_PRIORITY` — `hard_reject_posture_triggered` CRITICAL (not HIGH); `hard_reject_posture_cleared` NORMAL (not MEDIUM); `diplomatic_treaty_broken` family-branched. Add entries for `witness_strike_recorded` (NORMAL) + `commitment_paradox_resolved` (NORMAL).

**In `backend/game_logic/diplomatic_templates.py` or `speaker_resolver.py`:** `resolve_named_diplomat(speaker, nation) -> str` — per A1/U3/U15 contracts.

**Rail notifications:** add `review_target: Optional[str]` field; commitments events set per join-table.

**Godot surfaces (G-series):**
- `diplomatic_ledger.gd` `_render_nations()` — add Balance of Europe headline render at top of Nations tab.
- `diplomatic_ledger.gd` `_render_talleyrand()` — `diplomatic_reliability` is nation-keyed `Dict[str, int]`, not a Talleyrand scalar. Move to per-nation rows in Nations tab.
- `diplomatic_ledger.gd` `_render_history()` — replace raw `h_type.replace("_", " ").capitalize()` with label-map per join-table.
- `dispatch_view.gd:249-265` — add icon + label map per join-table (CRITICAL commitments events need specific icons/labels).
- `incoming_proposal_popup.gd:44, 46, 73-80` — double-render of `decision_reason` as "Court rationale" + "Court motive"; consolidate to one site.

**Campaign log dedup** (not strictly C-lite but adjacent): `backend/campaign_log.py:504-518 vs 673-687`, `520-530 vs 689-692` — delete second pair (dead code, first return wins).

---

## Definition of done

- [ ] CR1 verified: `grep -n "^### 8\." docs/RELIABILITY_COMMITMENTS_SPEC.md` shows `8.7` in the output.
- [ ] A1 verified: `grep -n "immediately before the floor" docs/RELIABILITY_COMMITMENTS_SPEC.md` returns nothing.
- [ ] U1 verified: `grep -n spotlight docs/RELIABILITY_COMMITMENTS_SPEC.md docs/COMMITMENTS_PRESENTATION_SPEC.md` returns only historical/changelog/stub refs.
- [ ] U5 present: §8.1 routing join-table exists and is flagged as single source of truth.
- [ ] A8 present: §11 `balance_of_europe` payload schema block exists.
- [ ] U15 present: logger channel + ValueError + `_bloc_members_cache` named in RCS.
- [ ] A2 present: CLAUDE.md:26 Remaining list contains "B-B4" explicitly.
- [ ] A3 present: CLAUDE.md:164 includes presentation spec + Voice Bible + COALITION_SPEC.
- [ ] D1+D2 present: STATUS.md cold-start routing points to B-Hegemony.
- [ ] CR2 verified: `grep -n "§12.5" docs/COMMITMENTS_PRESENTATION_SPEC.md` returns only line 807 (changelog).
- [ ] U7: SAVE_FORMAT_REFERENCE documents v2.4.3 substrate + alias policy.
- [ ] U8: Voice Bible header reads "v1.1 — v0.5.1 aligned".
- [ ] Single atomic commit titled approximately: *"MP v2.4.3 Block 1: doc-only cleanup (50 items across 4 audit passes)"*.

## Out of scope

- No code changes (Block 2).
- C-lite ship-checklist items are reference-only here; execute in C-lite slice.
- Playtest prose updates to COMMITMENTS_PLAYTEST_SCRIPT.md beyond D4 header fix — playtest authoring is separate.
