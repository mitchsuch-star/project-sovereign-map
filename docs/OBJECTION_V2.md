# V2 Objection System

> **V2a is COMPLETE.** See `docs/SYSTEMS_REFERENCE.md` Section 2 and `docs/archive/OBJECTION_V2A_DESIGN.md`.
> This document covers **V2b plans** (Phase 7b) only.

---

## V2b Preview: Defiance / Vindication / Authority

V2b adds the defiance/vindication/authority feedback loop. **Design gate required — see CLAUDE.md.**

### Fog-of-War Objection Triggers

| Situation | Cautious | Aggressive | Literal |
|-----------|----------|------------|---------|
| Attack into UNKNOWN | MODERATE→STRONG | No concern | Follows orders |
| Attack on STALE intel (3+) | MODERATE | MILD at most | Follows orders |
| Refuse attack when scout shows weakness | No concern | MODERATE→STRONG | No concern |
| PURSUE with no intel | STRONG | MILD | Depends on clarity |

### Defiance Mechanic (STRONG/EXTREME Only)

- Base chance: STRONG 15%, EXTREME 35%
- Modifiers: vindication (+10% per stack), authority (high: -10%, low: +10%), trust tier (HOSTILE: +15%, DEVOTED: -10%)
- **Hard cap: 40%**
- Defiance action = personality-preferred (Ney charges, Davout fortifies)
- Grouchy NEVER defies
- 3-turn cooldown after any defiance
- Variance band +/-5-8% prevents memorized thresholds

### Defiance Outcomes

| Result | Vindication | Authority | Trust | Extra |
|--------|-------------|-----------|-------|-------|
| Success | +1 | -5 | +2 | — |
| Failure | Reset to 0 | +3 | -5 | 3-turn cooldown, increased compliance |

### Authority (Global Stat)

Starts at 100. High (>=80): -10% defiance. Medium (50-79): neutral. Low (<50): +10% defiance. Changed by: defiance outcomes, vindication events, major victories (+5), defeats (-5), excessive trust choices (-2).

### Open Design Questions (MUST RESOLVE BEFORE CODING)

1. Failed defiance = full obedience (order executes) or marshal does preferred action?
2. Vindication decay: automatic (-1 per 3 idle turns) or event-triggered?
3. Aggressive trigger escalation: scale with beatable odds?

### Implementation Notes

`objection_v2.py` has 8+ helpers accessing enemy data without fog awareness. V2b switches these to fog-filtered data via `get_visible_enemies_near()`.
