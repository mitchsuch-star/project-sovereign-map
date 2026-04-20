# Memory and Pressure v2.4.2 — Deep Audit

> **Auditor:** Claude (Opus 4.7)
> **Date:** April 20, 2026
> **Scope:** Design + prose audit of the v2.4.2 Hegemony refactor. Deliberately goes beyond `MEMORY_AND_PRESSURE_V2_4_1_AUDIT_REPORT.md`; the prior audit's findings are not repeated unless new evidence warrants it.
> **Sources:** `RELIABILITY_COMMITMENTS_SPEC.md` v2.4.2, `RELIABILITY_IMPLEMENTATION_PLAN.md` v2.4.2, `COMMITMENTS_PRESENTATION_SPEC.md` v0.5, `COALITION_SPEC.md`, `SCALE_READINESS_PLAN.md` §Phase 0, prior audit.

---

## 1. Executive Summary

v2.4.2 applies the prior audit's cleanup faithfully — the concern→hegemony rename is complete, §9.5 reconciles the 33% row, R7/R8 are named, "Quadrangle" is gone. But new issues remain. **Two CRITICAL blockers:** (a) §7.1 code walks one vassal hop while prose says "walk the `lord` chain until it terminates," and (b) §9.3's "no composite floor needed" claim silently breaks once §8.8.9's stackable `grievance_modifier` lands. **Five MAJOR:** §8.6's still-active "wire this in this phase" order for a cancelled reliability tick; §8.6.1 preconditions blocking the grievance-removal path §8.8.4 promises; `world.nation_power_tiers` contradicting `SCALE_READINESS_PLAN.md` §Phase 0's "no separate tier map"; `COALITION_SPEC.md` §2a's "alliance formation does NOT generate threat" directly disagreeing with hegemony_passive; R5 and R8 risks that don't actually close the gaps they name. Overall design is strong — the engine is elegant, historically apt, proportionate — but several definitional contracts still disagree with themselves. **Overall score: 7.0 / 10.**

---

## 2. Part A — Edge Case Findings

### CRITICAL

**A1. §7.1 vassal chain: code does one hop; prose says walk to top overlord.** The §7.1 rule reads *"vassal-of-vassal cascades up to the top overlord (walk the `lord` chain until it terminates)."* The accompanying code only includes entries where `record.get("lord") == leader`. A sub-vassal (X's lord is Intermediate, Intermediate's lord is Leader) is missed. Invisible at v0.1's 5-nation scale but directly contradicts §7.7's "same engine generalizes to 13-20 nations without rewrite" — historical sub-vassals (Confederation of the Rhine, 1807-13) are the canonical case. Also: the "highest-power overlord wins (alphabetical tie-break)" rule for a two-lord collision is not in the code. Resolve: recursive walk + alphabetical fallback, OR soften prose to one-hop only. Confidence 95%.

**A2. §9.3 "no composite floor needed" is broken by §8.8.9's `grievance_modifier`.** §9.3 rationalizes the no-floor decision by saying "only two terms cannot stack into runaway values" (hegemony max -20 + betrayal max ~-18 from strikes, before hard-reject gates). But §8.8.9 introduces `grievance_modifier = -30 per active grievance`, stackable across multiple defensive-call refusals against the same victim. Three grievances + full hegemony + 2 strikes = -30×3 + -20 + -12 = -122. Even a single grievance + hegemony + one strike exceeds -55. The plan's parallel-slice structure does not catch this because B-B1-lite ships the formula collapse *before* B-B4 adds the grievance term. Fix: reintroduce a floor, cap grievance stacking, or scope §9.3's claim to "pre-DG-4." Confidence 85%.

### MAJOR

**A3. §8.6 still orders a cancelled reliability tick.** §8.6 says *"every 5 honored treaty turns: `+3` to `diplomatic_reliability[actor]`... — **wire this in this phase** (currently absent)."* But §13 cancels B-B6 (the redemption tick), §12.2 removes `actor_honored_turns`, and §14 R7 treats the tick as cut and discusses re-opening it. The prose in §8.6 is the most load-bearing contradiction in the spec because it instructs implementers to ship a slice that has been explicitly cancelled. Prior audit did not surface this. Confidence 95%.

**A4. §8.6.1 preconditions block the grievance-removal path §8.8.4 promises.** §8.8.4 says defensive-refusal grievance flags persist after their `+2` strikes have decayed, and that *"Make Amends (§8.6.1)"* is the only removal path. But §8.6.1's preconditions require *"at least 1 active victim-side strike against the target."* Once the strikes decay but the grievance persists, Make Amends cannot be invoked — the mechanic has no legal entry point. Spec needs explicit grievance-target preconditions + selection rule (is the strike precondition relaxed? Is cost 400g + 2 DP instead of 200g + 1 DP? §8.8.4 hints but does not commit). Confidence 90%.

**A5. `world.nation_power_tiers` contradicts `SCALE_READINESS_PLAN.md` §Phase 0.** Phase 0 §"Phase 0 Cross-Cutting Taxonomy" is explicit: *"Storage shape: `power_tier` is a field on the authored nation record... **There is no separate tier map**. The authored scenario config is the single source of truth; runtime code reads from it and does not mutate it."* But §7.2's helper-compat note and the implementation plan's prerequisite-helpers block both introduce `world.nation_power_tiers: Dict[str, str]` as a runtime map hydrated from scenario config. The spec cites SCALE_READINESS_PLAN as canonical; then defines a data shape it forbids. Fix: drop the tier map and read from the scenario record directly, or revise SCALE_READINESS_PLAN. Confidence 90%.

**A6. `COALITION_SPEC.md` §2a's threat-source table contradicts hegemony_passive.** COALITION_SPEC §2a says: *"Alliance formation does NOT generate threat. Only aggressive actions (war, conquest, vassalization, battles, annexation) raise threat. Defensive alliances formed by other nations are their response to threat, not a source of it."* v2.4's §7.8.4 playtest implication — *"If France plays peacefully but builds a 50%+ bloc, the v2.4 engine will eventually trigger coalition formation through accumulated passive threat alone — no French aggression needed"* — flatly disagrees. The two specs now describe different threat engines. COALITION_SPEC §2a needs a new row (`hegemony_passive | +1/3/5/8/turn | during advance_turn when bloc share ≥ 30%`), and the note must be softened.

**A7. R5 mitigation does not prevent non-France hegemon from firing wrong-target threat.** The engine is hegemon-agnostic; `_calculate_hegemony_pressure` may return `{non-France: pressure}` in a losing campaign. The plan's wire-up (line 109) unconditionally calls `add_threat(world, increment, source_key="hegemony_passive")` on the France-targeted scalar. Result: Russia becomes hegemon → passive threat accrues *against France* on *Russia's* dominance. R5 acknowledges the architectural limit but does not guard the call site. Fix: explicit `if hegemon == world.player_nation:` guard, or a §7.3 clause forcing the v0.1 assumption at the call site. Confidence 80%.

**A8. R8 conflates threat_level lag with `hegemony_target_mod` lag.** R8 claims *"Austria's `hegemony_target_mod` penalty jumps on turn N+1, not turn N."* §10.5 states `_calculate_hegemony_pressure` is per-turn cached and invalidated on treaty ratification. A cache-invalidate → fresh-compute path means the acceptance-formula read on a same-turn proposal DOES see updated share. The actual lag is on `threat_level` (end-of-turn `add_threat`), not on the formula penalty. R8's three-option mitigation needs to separate the two; the formula side is already correct under §10.5. Confidence 85%.

**A9. Defensive-refusal's effect on the refuser's own treaties is unspecified.** §8.8 adds grievance flags, oathbreaker posture, and anti-renewal cooldown, but never answers: after `call_to_arms_refused_defensive`, does the refuser's existing `DEFENSIVE_ALLIANCE` with the abandoned nation persist, downgrade, or terminate? This matters because bloc membership is alliance-driven — the same refusal can shrink the hegemon bloc or leave it unchanged depending on the answer. Confidence 75%.

### MINOR

**A10. Hegemon-pick tie-break is order-dependent.** §7.3 line 261 uses `max(bloc_shares.items(), ...)`; Python's `max` keeps first occurrence on tie. Iteration order derives from the `majors` list-comprehension over `get_active_nations()`. §7.1 has an explicit alphabetical rule for the vassal-lord collision case but nothing for the main hegemon pick. Commit to `power_score` then alphabetical.

**A11. Share = 0.30 exactly is a dead zone.** Ladder returns 1 at 0.30; §9.1 formula `int((0.30 - 0.30) * 60) = 0` so `hegemony_target_mod = 0`. Likely intent-consistent but worth a note.

**A12. Balance of Europe headline has no no-hegemon / brewing-only copy.** §11.1 shows three composed lines, each gated on "share ≥ 30%" or coalition status. Spec commits no default when no hegemon exists. Also: the example headline reads `Brewing (62/100) — Britain leads`, but `COALITION_SPEC.md` §3-§4 selects a leader only at *declaration*, not during brewing. Brewing has `qualifying_nations` but no designated leader.

**A13. Same-turn Make Amends flood.** §8.6.1 cooldown is per-pair. Five wronged nations → five Make Amends in one turn (1000g + 5 DP) for +10 reliability. Probably fine economically; no global per-turn cap documented.

**A14. Bandwagoning escape valve assumes AI proposal behavior.** §9.5 calls bandwagoning one of two escape valves, but nothing in the spec describes AI triggers that actually push minors to propose TO the hegemon. If `ai_diplomacy.py` does not fire minor→hegemon alliance proposals, the valve is decorative. Confidence 70%.

---

## 3. Part B — Internal Consistency

- **B1. §5 layer 1 still named "Rivalry pressure"** — should be "Hegemony pressure" post-v2.4. Prior audit swept §10/§11 prose but missed the principles block at §5, the first section a cold reader meets. Confidence 95%.
- **B2. §13 Slice C points to `COMMITMENTS_PRESENTATION_SPEC.md` v0.3**; actual presentation spec is v0.5.
- **B3. §13 advertises "~12 tests" for B-Hegemony**; plan raises to 18-22 after the prerequisite-helper audit. Spec/plan drift.
- **B4. §9.1 code comment "Linear scaling from -2 at 30% to -20 at 60%+"** is wrong at the boundaries: formula returns `0` at exactly 0.30 and `-18` at exactly 0.60. The -2 start and -20 clamp only appear elsewhere in the share range. Comment should say "-20 clamped at 63.33%+."
- **B5. §9.2 "natural cap at -18 because 3 strikes triggers hard-reject"** is misleading: hard-reject blocks proposal evaluation; it does not cap strike accumulation. With §8.7 exception paths, a 4-strike nation could compute -24 if a proposal reaches §9.2.
- **B6. Gate 9 resolution** ("distinct textures with explicit overlap rules") is vague; §8.8 DG-4 adds a new treaty-based obligation layer but Gate 9 does not cite it. Confidence 70%.
- **B7. Plan's Execution Order omits B-B4 (DG-4)** from the critical path even though §8.8.9's `grievance_modifier` collides with B-B1-lite's composite-floor claim (A2). A "merge ordering" paragraph is warranted.
- **B8. Changelog accuracy** spot-checks clean — every v2.4.2 edit cited in §17 is present in the body. Density is high (see C4).

---

## 4. Part C — Writing Quality

- **C1. §5 primes cold readers with deprecated vocabulary** ("Rivalry pressure"). Also captured as B1.
- **C2. §8.8 is deeply nested** (§8.8.1 through §8.8.14). Past §8.8.9 it reads as an adjunct spec inside a subsection. Graduate to its own top-level §9 once DG-4 ships.
- **C3. "Extraordinary play" at §7.4** is a handwave for the non-France-hegemon case that A7 flags — the writing invites the bug.
- **C4. §17 v2.4.2 changelog bullet is ≈900 words single-blob.** Skimming readers lose the critical delta amid housekeeping. Break into sub-bullets.
- **C5. §7.1 code snippet is load-bearing but lacks a worked-example tie-back.** Readers reverse-engineer bloc semantics from code; prose gives rules but no walkthrough.
- **C6. Under-specification on three implementation-defining behaviors:** bloc definition (A1), treaty consequence of defensive refusal (A9), grievance-removal preconditions (A4). These are not polish — they block code.
- **C7. `COMMITMENTS_PRESENTATION_SPEC.md` v0.5 top-note disclaims roughly half the file as non-normative** but leaves the disclaimed sections intact. Cold readers still have to mentally ignore most of the spec.

---

## 5. Part D — Scorecard

| Dimension | Score | Justification |
|---|---:|---|
| Elegance | 8 | Per-turn hegemon-share calc replaces four modifiers + static seed; bloc model underneath still fuzzy |
| Uniqueness | 8 | Period-specific; bloc-composition focus distinct from EU4-AE action-accumulation |
| Historical fidelity | 9 | Castlereagh/Pitt/Metternich references land; 1805 Third Coalition textbook |
| Scalability | 7 | §7.7 table is honest about 5→13; but A1 vassal-chain + A5 tier map surface at scale |
| Systemic coupling | 6 | Clean hook to `add_threat`; but A6 (COALITION_SPEC), A5 (tier map), A7 (non-France hegemon) leak |
| Fun (projected) | 7 | Bandwagoning + Make Amends preserve agency; grievance stacking may feel punitive without the §9.3 floor |
| Player legibility | 7 | Balance of Europe headline + ledger badges help; grievance + strike + hegemony stack is opaque |
| Mechanical depth | 7 | Recruit/release/amends/bandwagon decisions are real; grievance-removal gap (A4) undermines a core verb |
| Risk/tuning profile | 6 | 8 risks named honestly; R5 and R8 mitigations don't close the gaps they name |
| Implementation proportion | 9 | ~60 LOC engine + 18-22 tests for primary political texture is excellent |
| Writing quality | 6 | Rescope notes help; residual "Rivalry" at §5; §8.6 contradictory directive; §17 density |
| Internal consistency | 5 | §7.1, §8.6, §8.6.1/§8.8.4, §9.3, R5, R8, COALITION_SPEC §2a, SCALE_READINESS_PLAN §Phase 0 all disagree with one or more sibling specs |

**Overall arithmetic mean: 7.0 / 10.** The hegemony engine is the correct core abstraction and the implementation budget is proportionate. Execution risk concentrates in three areas: (1) the DG-4 / hegemony intersection where grievance stacking and grievance-removal both break the formula collapse's bounded-design claim, (2) cross-doc drift where three companion specs now describe incompatible contracts (COALITION_SPEC threat sources, SCALE_READINESS_PLAN tier storage, PRESENTATION_SPEC non-normative bulk), and (3) a handful of code/prose mismatches that surface only at scale or under unusual play.

---

## 6. Prioritized Action List

**Must fix BEFORE implementation:**

1. **A1** — resolve §7.1 vassal-chain recursion: transitive walk in code OR soften prose to one-hop.
2. **A2** — reconcile §9.3 with §8.8.9: reintroduce a composite floor, cap grievance stacking, or scope the §9.3 claim to "pre-DG-4."
3. **A3** — rewrite §8.6 so it no longer directs implementers to ship B-B6; restate the intended reliability-recovery contract in one place (R7 is the best home).
4. **A4** — write an explicit grievance-removal contract in §8.6.1 / §8.8.4: preconditions when no strikes are active, target selection, cost, interaction with ordinary strikes.
5. **A5** — align `power_tier` ownership with `SCALE_READINESS_PLAN.md` §Phase 0: drop `world.nation_power_tiers` and read from the authored scenario record, or revise Phase 0.
6. **A6** — update `COALITION_SPEC.md` §2a so passive hegemony threat is a first-class input rather than a contradiction.
7. **A7** — guard the `add_threat` wire-up against non-France hegemon (plan line 109) or commit to the v0.1 France-only assumption at the call site.
8. **A8** — rewrite R8 to distinguish threat_level lag from `hegemony_target_mod` (same-turn, cache-invalidated).
9. **A9** — specify what a `call_to_arms_refused_defensive` does to the refuser's existing alliance with the abandoned nation.

**Fix DURING the implementation session:**

10. **A10** — commit to a deterministic tie-break rule for the main hegemon pick (§7.3).
11. **B1 / C1** — rename §5 layer 1 from "Rivalry pressure" to "Hegemony pressure."
12. **B2** — bump §13's v0.3 reference to v0.5.
13. **B3** — align §13 Slice B test count (~12) with plan's 18-22.
14. **A12** — specify no-hegemon and brewing-state default Balance of Europe copy.
15. **B4 / B5** — correct the §9.1 comment boundary claim and the §9.2 "natural cap" framing.
16. **B7** — add a "merge ordering" paragraph in the plan: B-B4 must land AFTER or WITH B-B1-lite's composite-floor collapse.

**Deferrable:**

17. **A11, A13, A14** — playtest-gate items; document in §14 if not mitigated after first playtest.
18. **C2** — graduate §8.8 to its own top-level section once DG-4 ships.
19. **C4** — break §17 v2.4.2 changelog bullet into sub-bullets.
20. **C7** — trim the non-normative bulk of `COMMITMENTS_PRESENTATION_SPEC.md` v0.5 (rather than disclaiming it in place).

---

*End of audit.*
