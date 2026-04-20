# Memory and Pressure v2.4.1 — Audit Report

> **Auditor:** Claude (Opus 4.7)
> **Date:** April 19, 2026
> **Scope:** Pre-implementation audit of the v2.4 Hegemony refactor + v2.4.1 §7.8 / §9.5 clarifications.
> **Sources reviewed:** `RELIABILITY_COMMITMENTS_SPEC.md` v2.4.1, `RELIABILITY_IMPLEMENTATION_PLAN.md` v2.4, `COALITION_SPEC.md`, `COMMITMENTS_PRESENTATION_SPEC.md` v0.4-labelled file, `CLAUDE.md`, and code in `backend/models/world_state.py`, `backend/game_logic/coalition.py`, `backend/game_logic/diplomacy.py`, `backend/game_logic/vassal.py`.

---

## A. Cross-doc consistency

### CRITICAL — `COMMITMENTS_PRESENTATION_SPEC.md` is labelled v0.4 but does not reflect the v2.4 trim

The plan (`RELIABILITY_IMPLEMENTATION_PLAN.md` line 172) directs the reader to "`COMMITMENTS_PRESENTATION_SPEC.md` (v0.4 forthcoming — will trim cut items)". The file on disk is already labelled v0.4 (header line 3), but its v0.4 pass was an April 16 audit-fix pass, *before* the April 19 hegemony rescope. The v0.3 Rescope Note (lines 25-35) still lists *"Preserved from v0.2: Spotlight tier on the notification rail (elevated card, 2-turn persist, action buttons) / Split-voice render (`attributed_lines[]`) / One N+1 Talleyrand aside keyed by `episode_id`"* — all three are cancelled in v2.4. §2 "Phase Placement" (lines 62-69) still shows the old execution flow including `A1-fill (concern seed)`, `A2 fill (ledger concern display)`, `B2a-fill (ratification anger)`, `B6 (redemption tick)`. §9.1 "Dispatch spotlight card" (lines 255-302) is normative for the split-voice `attributed_lines[]` contract that v2.4 cancels. An implementer reading the plan and then opening this file will be instructed to ship items the hegemony refactor explicitly cuts. This is the highest-severity cross-doc drift found.

### MAJOR — `CLAUDE.md` "Before Modifying" row (line 164) is stale

Row reads *"Memory and Pressure substrate (rivalries / betrayal memory / paradox / reliability) | `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v2.3 — ...) ... `world_state.py` (`betrayal_history`, `next_episode_id`, `nation_rivalries` when seeded)"*. Three issues: (1) version tag is **v2.3**, spec is v2.4.1; (2) the row header uses "rivalries" as the defining concept, but v2.4 has deleted authored rivalry data from v0.1; (3) `nation_rivalries` is flagged as a field that will seed — v2.4 explicitly cancels that slice. The sister row on line 345 ("Memory and Pressure (substrate + presentation)") also reads v2.0.

### MINOR — orphaned "concern" language left inside the v2.4 spec

After the renames, several prose references still read in the old vocabulary. Locations:

- §8.4 line 431: *"switches to `nation_concerns` data once seeded — see §7.1"* — `nation_concerns` was deleted; the war-state proxy is now permanent.
- §8.8.1 line 549 + §11.2 line 925: stable category tie-break order still lists `concern` between `betrayal` and `peace_conflict`. §11.2 line 914 already renames the category to `hegemony`. Tie-break order needs the rename applied in the two canonical lists.
- §10.2 line 840, §10.3 line 848, §10.5 line 861, §11.2 line 903, §11.2 line 933: prose uses "concern" / "View all concerns" / "cached concern lookups" / "high-concern nations".
- §11.4 line 943: dispatch events list still calls out *"concern escalation (Prussia-Saxony triggers)"*. §13 line 1024 explicitly cancels Prussia-Saxony triggers — the event will never fire.
- §8.8.4 line 590: *"When rivalry data seeds in a later slice (v0.2+), unremoved grievance flags upgrade to rivalry entries; this is the intended graduation path"* — the graduation target no longer exists.
- §15 Gate 1 line 1113: *"Implemented via composite `political_commitment_mod` + hard-reject posture"* — `political_commitment_mod` was deleted in v2.4.

Test budgets and slice names are internally consistent between `RELIABILITY_COMMITMENTS_SPEC.md` §13 and `RELIABILITY_IMPLEMENTATION_PLAN.md` §Test Budget Comparison (both land at 35-42, 1 session, same slice list).

---

## B. Substrate compatibility

### CRITICAL — Four helpers the spec and plan call on `world` do not exist in the backend

The plan and spec §7.1-§7.3 use these six helpers as if they exist:

| Helper | Status | Closest existing code |
|--------|--------|-----------------------|
| `world.get_vassals_of(leader)` | **not implemented** | `world.vassals` dict must be iterated, filtering entries where `entry["lord"] == leader` |
| `world.get_treaty_state(a, b)` | **not implemented** | `world.get_diplomatic_state(a, b)` returns a string, not a `TreatyState` enum — the spec uses `TreatyState.ALLIANCE` as an enum that does not exist |
| `world.get_power_tier(nation)` | **not implemented** | `power_tier` is specced as authored scenario data per `SCALE_READINESS_PLAN.md` §Phase 0, but no scenario-loading code exists yet; a grep for `power_tier` inside `backend/` returns nothing |
| `world.get_major_powers()` | **not implemented** | No helper exists. Closest analogues are `get_active_nations()` and `get_known_nations()` |
| `world.get_active_strike_count(target, asker)` | **present under different name + reversed args** | `backend/game_logic/diplomacy.py:297` has module-level `_get_active_betrayal_strike_count(world, actor, victim)` — note `(actor, victim)` ordering versus the spec's `(victim, perpetrator)` |
| `world.get_nation_regions(nation)` | present + cached | `backend/models/world_state.py:1196` |
| `world.get_active_nations()` | present + cached | `backend/models/world_state.py:728` |

The plan's B-Hegemony item advertises *"3 helpers + engine + coalition wire-up + leader score update + 12 tests"*. In reality, four of the foundation helpers the engine reads through do not exist yet. Depending on scope decisions, this also implies scenario-data wiring for `power_tier` (authoring path from scenario config onto world state) and possibly a new `TreatyState` enum or a spec rewrite to consume the current string return. None of this is called out as new work.

### MAJOR — `coalition_leadership_score` is hardcoded to France

`backend/game_logic/coalition.py:207`: *"france = world.player_nation"*, then *"hostility = abs(_get_relation(world, france, nation))"*. The v2.4 plan adds a `bloc_share_against` term to this function but does not address that the function is still France-hostility-anchored. Test line 114 of the plan (*"`coalition_leadership_score` favors highest-bloc-share-against among non-bloc members"*) reads cleanly, but the function will still select leaders by France-hostility when a future non-French hegemon emerges. This is correctly scoped as D2 follow-up in `RELIABILITY_COMMITMENTS_SPEC.md` §R5 — no action needed for this ship — but the test should explicitly assert the French-hegemon precondition.

`process_coalition_turn` (coalition.py:881) and `add_threat` (coalition.py:95) both exist as expected; the wire-up target is real.

---

## C. Completeness

See §A MINOR list above for the enumerated orphans. Severity triage:

- **MAJOR**: §8.4 line 431 (witness scoping relies on deleted field), §8.8.4 line 590 (graduation path points at deleted store), §15 Gate 1 line 1113 (resolution cites deleted modifier) — these are load-bearing references that readers will follow to the wrong place.
- **MINOR**: everything else in the concern-prose list (§10.2, §10.3, §10.5, §11.2, §11.4).

Auto-downgrade rule (v2.3 §7.1) is correctly superseded in §7.6 line 302. `actor_honored_turns` is correctly removed from the v0.1 ship list in §12.2. Composite `political_commitment_mod` floor is correctly removed from §9.3 (the Gate 1 reference at §15 is the only stale one). Prussia-Saxony authored triggers are correctly removed from the cancellation list (§13 line 1024) but the §11.4 dispatch-events row still names them.

`§7.4.B third-party ratification anger` does not appear by that exact name in the v2.4 spec — the B2a-fill cancellation (§13 line 1022) is documented. No orphan found.

---

## D. Design coherence

### MINOR — v2.4.1 §9.5 table's -2 entry disagrees with the §9.1 formula

§9.1 computes `raw = int((share - 0.30) * 60); return max(-20, -raw)`. At share = 0.33 the formula returns `-int(0.03 * 60) = -1`. The §9.5 table shows *"France + 2 minors / ~33% / -2"*. Every other row matches the formula at its stated share (40% → -6, 45% → -9, 55% → -15, 65%+ → -20). The table prose says values are illustrative and depend on region allocation, but an auditor walking the table with the formula will spot the -2 mismatch. Either rephrase the row as *"~34-35%"* or note the floor clamps to -2 for the "some pressure but not none" threshold.

### CHECK PASSED — passive threat ladder scales sensibly against `coalition.py` thresholds

Coalition thresholds (coalition.py:34-37): TENSION 30, MURMURS 40, BREWING 60, INSTANT 80. Decay is 2-3/turn depending on peace/war state. Feeding the hegemony ladder against those:

| Share | +/turn | Net of decay (~2) | Turns to BREWING (60) |
|-------|--------|-------------------|------------------------|
| 30-40% | 1 | ~0/turn | effectively never passively |
| 40-50% | 3 | ~1/turn | 40-50 turns |
| 50-60% | 5 | ~3/turn | 15-20 turns |
| 60%+ | 8 | ~6/turn | 8-10 turns |

This matches the spec's design intent (60%+ = "coalition formation inevitable"; 40% = "harder but possible"). The §7.8.4 playtest implication that peaceful hegemons eventually get coalitioned is mechanically consistent with these numbers. §9.5 playtest gates are internally coherent with §7.3.

---

## E. Feasibility

### MAJOR — ~35-42 tests / 1 session claim is underestimated for B-Hegemony

Walking slice by slice:

- **B-Hegemony (12 tests)**: the plan ships *"3 helpers + engine + coalition wire-up + leader score update"*. Actual new helpers:
  1. `get_bloc_members` (new)
  2. `power_score` (new)
  3. `bloc_power` (new, mentioned but not enumerated in the "3 helpers" count)
  4. `_calculate_hegemony_pressure` (new)
  5. `_hegemony_pressure_for_share` (new)
  6. `get_vassals_of` (new prerequisite)
  7. `get_treaty_state` (new prerequisite; may also need enum decision)
  8. `get_power_tier` (new prerequisite + scenario-data wiring)
  9. `get_major_powers` (new prerequisite)
  
  Plus cache invalidation hooks for bloc_members on treaty ratification / vassal change / war declaration / peace (four call sites minimum), plus the `coalition_leadership_score` update, plus the `add_threat` wire-up with the new `"hegemony_passive"` source key, plus scenario-data authoring for `power_tier` per `SCALE_READINESS_PLAN.md` §Phase 0 (which is decided but not implemented yet). Realistic tests to cover all of this likely sit at 18-22, not 12. A 1.5-session estimate is more honest.

- **B-B1-lite (6 tests)**: the work itself is small — two functions plus the reliability narrowing. But the test list in the plan line 131-135 excludes coverage of (a) warning category rename (`concern` → `hegemony`) + alias, (b) save-load alias for `decision_reason`, (c) debug breakdown output verification. 8-10 tests is more realistic.

- **B-B3 (3 tests) / B-B7 (8 tests) / Slice C-lite (10-12 tests)**: scopes unchanged from v2.3; plausible as stated.

- **Total:** ~40-50 tests is closer than 35-42. One session is tight but possible for a focused day; the risk is scenario-data wiring for `power_tier` spilling into a second session.

Test numbers are not the bottleneck — the unestimated helper work is.

---

## F. Risk assessment

### MAJOR — R7 missing: cancelling B-B6 leaves no passive reliability recovery path

Before v2.4: Make Amends (+2 per use, 10-turn per-pair cooldown) *plus* honored-turn tick (+3 per 5 honored turns, global) *plus* future bargain fulfillment (deferred). After v2.4: only Make Amends and deferred bargain fulfillment. A long campaign with no breaches accrues zero passive reputation recovery, even though France demonstrably *is* keeping its word. §14 does not list this as a risk. The v2.4 claim that B6 was "invisible to players" is debatable — the tick feeds `reliability_modifier` on every AI acceptance check. Recommend adding R7 explicitly: *"with B6 cancelled, reliability can only decrease or repair via Make Amends; consider tuning Make Amends to +3 or adding a minimal passive tick if playtest shows long-term reliability stagnation."*

### MAJOR — R8 missing: B-B2a-fill cancellation introduces one-turn delay on third-party reaction

The v2.4 rationale line 1022 says third-party ratification anger is *"captured by hegemony pressure naturally rising when France allies with someone"*. True, but the share recomputes *next* turn — not at ratification moment. When France ratifies an alliance with Britain, Austria's proposal-preview penalty from `hegemony_target_mod` jumps on turn N+1, not turn N. This is a meaningful UX gap if the player expects immediate feedback on a high-salience political move (France ratifies Britain alliance → "Metternich is alarmed" should fire that turn, not next turn's hegemony recalc). Spec should either (a) acknowledge and accept this one-turn lag as a documented design call, (b) trigger a hegemony recomputation on treaty ratification events inline, or (c) emit a deterministic dispatch spotlight at ratification time that narrates the political move even before the share math updates.

### PASSED — R1 / R3 / R5 / R6 coverage is adequate

Each covers the risk it names, with a named mitigation that is operable via playtest tuning. R5 (hegemon-agnostic engine but France-targeted threat scalar) is honest about the limitation — the threat scalar is clearly scoped as D2 follow-up.

---

## G. Substrate that should be removed

### CHECK PASSED — v2.4 claim that nothing shipped needs to come out is correct

The only candidate is `backend/game_logic/diplomacy.py:443`: `rivalries = getattr(world, 'nation_rivalries', {}) or {}` in `_classify_witness_scope`. Since no code ever sets `world.nation_rivalries`, the conditional is dormant — the branch always returns `{}` and falls through to the war-state proxy check. It does not crash, does not leak state, and does not affect behaviour. It could be cleaned up during B-B1-lite work but is not required. No campaign-log or dispatch event types in `backend/campaign_log.py` reference concerns, rivalries, or any v2.4-cancelled concept (spot-checked via grep). Coalition.py passive-threat comments use "hegemony" lowercase (line 60) as an English word, not as a code reference.

---

## Prioritized action list

### Must fix BEFORE implementation starts

1. **Rewrite or version-gate `COMMITMENTS_PRESENTATION_SPEC.md`** so it reflects the v2.4 trim. Either rev to v0.5 with the spotlight-tier / split-voice / N+1 / A1-fill / A2-fill / B2a-fill / B6 references cut, or add a v2.4 Rescope Note at the top pinning the cuts and mark the affected sections non-normative. **Without this, the implementer is directed to ship the cancelled work.** (Critical, §A)

2. **Decide the helper contract**: either implement `world.get_vassals_of` / `get_treaty_state` / `get_power_tier` / `get_major_powers` / `get_active_strike_count` as named in the spec, or rewrite §7 / §9 / plan B-Hegemony to consume the existing code (`world.vassals` dict iteration, `get_diplomatic_state` returning strings, `_get_active_betrayal_strike_count` module function). The spec's `TreatyState.ALLIANCE` enum does not exist — pick a direction. (Critical, §B)

3. **Author `power_tier` scenario data + loader**. The hegemony engine cannot run without this. `SCALE_READINESS_PLAN.md` §Phase 0 decided the taxonomy; Phase 0 has not wired it into Python. Budget a task for this before or inside B-Hegemony. (Critical, §B)

4. **Update `CLAUDE.md` line 164 + line 345** to v2.4.1, drop `nation_rivalries`, and retitle the row to reflect hegemony-based pressure. (Major, §A)

5. **Add risks R7 (no passive reliability recovery) and R8 (one-turn delay on third-party reaction) to §14.** Decide whether to mitigate or accept each. (Major, §F)

### Fix during the implementation session

6. **Spec prose cleanup pass** on `RELIABILITY_COMMITMENTS_SPEC.md`:
   - §8.4 line 431: drop `nation_concerns` reference; declare war-state proxy permanent.
   - §8.8.4 line 590: rewrite grievance-graduation target.
   - §15 Gate 1 line 1113: replace `political_commitment_mod` with `hegemony_target_mod`.
   - §8.8.1 line 549 + §11.2 line 925: replace `concern` with `hegemony` in the tie-break ordering.
   - §10.2 / §10.3 / §10.5 / §11.2 / §11.4 / §11.2-line-933: replace "concern" prose with "hegemony" or "pressure".
   - §11.4 line 943: drop the Prussia-Saxony dispatch event (cancelled in §13).
   (Minor to Major, §C)

7. **Revise the B-Hegemony test list in `RELIABILITY_IMPLEMENTATION_PLAN.md`** to cover the four prerequisite helpers, cache invalidation paths, and `coalition_leadership_score`'s France-anchoring. Expect ~18-22 tests, not 12. (Major, §E)

8. **Add one test to B-B1-lite** asserting the `concern` → `hegemony` warning-category alias round-trips through save/load. (Minor, §E)

9. **Optional housekeeping**: remove the dormant `nation_rivalries` branch at `backend/game_logic/diplomacy.py:443` during B-B1-lite to prevent future grep confusion. (Minor, §G)

10. **Reconcile §9.5 33%-row value** with the §9.1 formula — either change the table's -2 to -1, raise the stated share to ~35%, or add a note that the ladder floors to -2 at the first-bucket boundary. (Minor, §D)

---

*End of audit.*
