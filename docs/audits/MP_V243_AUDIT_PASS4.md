# MP v2.4.3 Pass-4 Audit — 2026-04-20

> **Purpose:** Final audit pass hitting surfaces the combined audit + two follow-up passes under-sampled. 38 new findings (1 BLOCKER, 2 HIGH, 14 MAJOR, 21 MINOR) across three dimensions.
>
> **Ships as:** findings integrated directly into [`MP_V243_BLOCK1_DOC_CLEANUP.md`](docs/audits/MP_V243_BLOCK1_DOC_CLEANUP.md) and [`MP_V243_BLOCK2_SUBSTRATE.md`](docs/audits/MP_V243_BLOCK2_SUBSTRATE.md) — no separate execution path. This file is the **audit record** only.

---

## Cumulative finding count across all 4 passes

| Pass | Source | Findings | Blockers/Critical | High/Major | Minor |
|------|--------|----------|-------------------|------------|-------|
| 1 | Combined (Claude + Codex) | 17 | 3 | 7 | 7 |
| 2 | Meta-audit (spec + code + work orders) | 17 | 1 | 8 | 8 |
| 3 | Third pass (tests + Godot + cross-refs) | 17 | 1 | 5 | 11 |
| 4 | This pass (AI/endpoints + docs + plan) | 38 | 1 | 16 | 21 |
| **Total** | | **89** | **6** | **36** | **47** |

Saturation curve: passes 1-3 each yielded ~17 findings in their dedicated surfaces; pass 4 hit three large untouched surfaces simultaneously (AI code + docs ecosystem + plan slice prerequisites) and so yielded proportionally more. Pass 5 on these same surfaces would likely yield 3-5 minors.

---

## Dimension 1 — AI / endpoints / non-diplomacy code (7 findings)

### BLOCKER

**P1. `backend/models/cooldown_manager.py:144,155` — `PopupQueue.PRIORITY_ORDER` and `RESPONSE_KEYS` hardcode `"alliance_paradox_popup"`.** This is the actual delivery gate for the popup (main.py's `_include_popup_passthroughs` reads the registry). Prior passes tracked `world.alliance_paradox_popup` attribute and Godot scene only — the cooldown_manager registry was not sampled. Rename must update both entries and add a read-only alias for save compatibility. Without this fix, post-rename popup delivery silently breaks.

### HIGH

**P2. `backend/models/dialogue_manager.py:49,87` — state inconsistent.** `HARD_STOP_TYPES` lists BOTH `"alliance_paradox"` and `"commitment_paradox"` (comment says this is transitional), but `DIALOGUE_PRIORITY` only maps `"alliance_paradox": 0`. The rename path is half-set-up: the hard-stop check will pass for either name, but priority lookup for the new name returns the default (99). A comment at lines 39-45 already flags the transition plan; the code changes never landed.

**P3. `backend/commands/diplomatic_executor.py:2782,2870` — half-migration in live code.** Emits `"type": "commitment_paradox_resolved"` (new name) but subsequently clears `world.alliance_paradox_popup = None` (old attribute). `campaign_log.py` already routes the new event-type name at multiple sites (74/143/264/520/689). This is NOT just docs drift — live code is shipping a half-migration today. Block 2 rename must reconcile both sides.

### MAJOR

**P4. `backend/game_logic/turn_manager.py:248,358` — `alliance_paradox` references.** Priority comment at 248 (`# Priority: alliance_paradox > vassal_rebellion > sabotage > ai_proposal`) and clear-state write at 358. Missed by prior passes that focused on diplomacy.py and main.gd.

**P6. `backend/game_logic/diplomacy.py:1828-1829` — dead conditional.** `determine_ai_offer_decision_reason` has `if int(threat) > 60 or wars >= 2: return "rival_pressure"` followed by `return "rival_pressure"` — both branches return the same value. U4 renames the string but exposes the underlying logic bug. Post-rename, one branch should return `"hegemony_pressure"` and the other `"unknown_baseline"` (per B1 extension), otherwise the if-threshold is pointless.

### MINOR

**P5. `backend/commands/executor.py:450` + `backend/commands/meta_executor.py:115` — comment landmines.** Hard-stop blocking comments name `alliance_paradox`. Code indirection reads from `HARD_STOP_TYPES`, so behavior is fine; comments rot after rename.

**P7. `backend/game_logic/ai_diplomacy.py:746,754,768,782,814,841` — migration note.** AI proposal pipeline threads `decision_reason` end-to-end. Values come from `determine_ai_offer_decision_reason` (finding P6). Not a shape drift — a value-drift migration path. After U4, any in-flight proposals in saves carry legacy enum until turn flush.

### Clean confirmations (no drift)

- `backend/ai/validation.py`, `prompt_builder.py`, `enemy_ai.py`, `llm_client.py`, `strategic_parser.py` — LLM/parser layers fully insulated
- `backend/game_logic/diplomatic_advisory.py` — no stale enum strings
- `backend/main.py` — clean on popup passthroughs (abstraction works, provided P1 lands)
- `backend/save_manager.py` — delegates to world_state.to_dict/from_dict (inheritance captured by prior audits)
- `backend/commands/objection_v2.py`, `defiance.py` — operate on marshal-trust, no v2.4.3 contact
- `backend/game_logic/coalition.py`, `vassal.py` — no residual `nation_power_tiers` reads or legacy enums

---

## Dimension 2 — Documentation ecosystem (12 findings)

### HIGH

**D1. `docs/STATUS.md:195-196, 232-239` — describes cancelled v2.1/v2.0 slice list.** References `rivalry seed (Slice A1-fill)`, `direct_rivalry_mod / rival_conflict_mod / graduated bilateral_betrayal_mod cap -24`, `composite political_commitment_mod`, `redemption tick Slice B6 actor_honored_turns`, `C3-lite presentation pass: spotlight tier, split-voice attributed_lines[], one N+1 Talleyrand aside`. Every item is cancelled/replaced in v2.4.3.

**D2. `docs/STATUS.md:73, 127` — misroutes fresh sessions to cancelled work.** Tells a new session to "pick up Memory and Pressure — Slice A (rivalry seed)". Next slice is B-Hegemony.

**D3. `docs/ROADMAP.md:196` — Post-Phase-8 table still cites v2.1 + v2.0 plan.** Stale remaining work list, "~68-74 tests / ~3 sessions", "presentation v0.3". Should read v2.4.3 / ~70-83 tests / ~2 sessions / v0.5.1.

**D10. `docs/SYSTEMS_REFERENCE.md §21 + §22` — describes pre-v2.4.3 reliability + names alliance_paradox_popup.** §21 at line ~3534 says reliability is "+5 per treaty honored for 10+ turns, -10 per treaty break, capped ±10" and `reliability_modifier` component — v2.4.3 narrowed to `clamp(// 10, -6, +6)`. §22 priority list item 7 is `alliance_paradox_popup`. This is one of the three "essential for Chat" docs per MEMORY.md, so drift here is high-impact.

### MEDIUM

**D4. `docs/COMMITMENTS_PLAYTEST_SCRIPT.md:4` + Prerequisites** — references stale commit `cc7d83d`; doesn't exercise B-Hegemony Balance of Europe headline or named-diplomat helper.

**D5. `docs/DIPLOMAT_VOICE_BIBLE.md:199-224` §Minimum cast coverage** — missing Chancery-voice `hard_reject_clear` copy and `witness_strike` reactions (both are live §8.1 events requiring voice). Heading label "C3-lite (v0.3)" also stale.

**D6. `docs/ADDING_CONTENT.md:910-1045` §Adding New Nations** — 9-step checklist doesn't mention `power_tier` authored field. Adding a new nation without it defaults to `"secondary"` silently, hiding scenario errors.

**D7. `docs/MODDING_FORMAT.md:471` — declares "Current format version: 1.0".** Doesn't mention `scenario_schema_version: 1`, `power_tier`, or the `political_status` authored/runtime split.

**D8. `docs/DESIGN_REFINEMENT.md:121` — R17d DP Breakdown cites cancelled components** (`political_commitment_mod` / `direct_rivalry_mod` / `rival_conflict_mod`). Live is `hegemony_target_mod` + `bilateral_betrayal_mod` + `grievance_modifier`.

**D9. `docs/DESIGN_REFINEMENT.md:115-122` + R119/R160/R162** — cite "v2.1" throughout. R160 references `RELIABILITY_COMMITMENTS_SPEC.md v2.1 §7` — v2.4.3 dropped static rivalries entirely.

### LOW-MEDIUM

**D11. `docs/ARCHITECTURE_REFACTORING_PLAN.md:1077, 2092, 2138, 2195` — cites `alliance_paradox_popup` as canonical.** B-B3 renames, but architecture plan wasn't updated.

**D12. `docs/BUG_FIXES.md:644` — hard-stop list still names `alliance_paradox`.** Minor post-rename drift.

### Clean (no drift)

- `docs/VISION.md`, `TUTORIAL_SCRIPT.md`, `FUTURE_DESIGN.md` — no v2.4.3 surface contact
- `docs/archive/*` — not auditing archive unless current docs cite archived as live

---

## Dimension 3 — Implementation plan slice-by-slice (19 findings)

### B-Hegemony (lines ~83-133)

**P4C1 MAJOR.** Plan doesn't explicitly list `WorldState._bloc_members_cache` field contract (U15 required it be named).

**P4C2 MAJOR.** Plan says `world.get_bloc_members(leader)` as method; spec §7.1 shows module function `get_bloc_members(world, leader)`. Disagreement.

**P4C3 MAJOR.** `bloc_power` and `power_score` locations silent (likely `coalition.py`). Import contract for `hegemony_target_mod` in `diplomacy.py` missing.

**P4C4 MAJOR.** Cache invalidation lists four call sites but not §8.8.7a same-turn alliance termination as fifth site.

**P4C5 MAJOR.** `coalition_leadership_score` wire-up doesn't specify `european_power` denominator access pattern (arg vs module-level helper).

### B-B1-lite (lines ~134-155)

**P4C6 MAJOR.** Legacy variable removal vague. §9.1 replaces `direct_concern_mod` + `concern_conflict_mod`; §9.3 pre-DG-4 deletes `political_commitment_mod = max(-40, raw)`. Plan must list explicit removals.

**P4C7 MINOR.** Test bullet "scales linearly -1 to -20" misses §9.1 integer-truncation semantics (0 at 30% boundary, not -1).

### B-B3 (lines ~156-166)

**P4C8 MAJOR.** Rename scope missing `dialogue_manager.py:86 DIALOGUE_PRIORITY` entry. (This overlaps B3/P2 — the plan's silence is the finding, fix is already in Block 2.)

**P4C9 MAJOR.** Rename scope missing `WorldState.alliance_paradox_popup` attribute rename path. Silent on whether field renames (with alias) or retains legacy name.

**P4C10 MINOR.** Silent on `SAVE_FORMAT_REFERENCE.md` alias-on-load policy update.

### B-B4 (lines ~189-213)

**P4C11 MAJOR.** Plan doesn't list `END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION` constant as new `display_names.py` / emitter addition. Only mentioned in test bullet.

**P4C12 MAJOR.** `grievance_modifier = -30 per grievance` value not stated in plan. Saturation cap at 3 mentioned; value not.

**P4C13 MAJOR.** Composite floor `-60` reintroduction listed only in Merge-ordering paragraph, not in B-B4 Files/Work list.

### B-B7 (lines ~168-186)

**P4C14 MINOR.** `reparations_cooldown: Dict[str, int]` added but no serialization-enforcement test call-out (CLAUDE.md mandatory rule).

### C-lite (lines ~216-233)

**P4C15 MAJOR.** Plan doesn't list: `commitments_notice_*` family, `notification_bar.gd` TYPE_ICONS extension, priority-tier mapping in `notifications.py`, `review_target` routing, campaign-log dedup by `episode_id`, Balance of Europe payload in `build_diplomatic_ledger`, `incoming_proposal_popup` dedup. Seven missing prerequisites.

**P4C16 MAJOR.** `resolve_named_diplomat` helper location unspecified (`diplomat.py` vs `diplomatic_templates.py`).

### Cross-cutting (lines ~275-330)

**P4C17 MAJOR.** Test budget table: plan line ~327 says B-B4 "25-29"; spec §8.8.13 line 807 says "~25 new". Count mismatch.

**P4C18 MINOR.** Session count "~1.5 effective" inconsistent with test totals (45-54 base + 25-29 B-B4 = ~70-83 tests ≈ 2.5 sessions at historical pace).

**P4C19 MINOR.** Merge-ordering "remove only the *explanatory surface* of the old composite aggregation" is undefined (legacy `old_composite` variable, `components["political_commitment_mod"]` emit, etc.).

### Clean (no drift)

- Plan Execution Order + slice prerequisites scan: every helper in spec §7 **is** represented in B-Hegemony prerequisite list (`get_power_tier`, `get_bloc_members`, `power_score`, `bloc_power`, `_calculate_hegemony_pressure`, `_hegemony_pressure_for_share`, `coalition_leadership_score`, scenario config authoring) — findings P4C1-P4C5 are about precision, not omission.

---

## Where these findings live

All 38 findings are integrated into the block work orders:

- **Doc-only items** (CR-D-P4C series, 24 items) → [`MP_V243_BLOCK1_DOC_CLEANUP.md`](docs/audits/MP_V243_BLOCK1_DOC_CLEANUP.md)
- **Code items** (P1-P7, 7 items — minus P4C which is plan-doc) → [`MP_V243_BLOCK2_SUBSTRATE.md`](docs/audits/MP_V243_BLOCK2_SUBSTRATE.md)
- **Plan-edit items** (P4C1-P4C19, 19 items) → Block 1 (plan is a doc)

The combined audit's 17 findings + pass-2's 17 + pass-3's 17 are integrated into the same two files with addendum sections collapsed into severity-ordered main flow (see commits c88b013, 5fcc93c, this commit).
