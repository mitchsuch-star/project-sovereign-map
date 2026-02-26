# V2 Objection System

> **V2a is COMPLETE.** See `docs/SYSTEMS_REFERENCE.md` Section 2 and `docs/archive/OBJECTION_V2A_DESIGN.md`.
> **V2b DESIGN LOCKED.** See `docs/V2B_DEFIANCE_SPEC.md` for full implementation spec.

---

## V2b: Defiance / Vindication / Authority

Full spec: **`docs/V2B_DEFIANCE_SPEC.md`**

### Quick Summary

- **Defiance:** STRONG/EXTREME concerns can trigger marshal defiance after player insists. 15-35% base, 40% hard cap. Personality-preferred fallback action.
- **Vindication:** Per-marshal score (-5 to +5). +10% defiance per stack. Decays -1 per 3 idle turns.
- **Authority:** Global 0-100. High (≥80) suppresses defiance -10%. Low (<50) emboldens +10%. Changed by defiance outcomes, major battles, excessive trusting.
- **Fog migration:** 8+ objection helpers switch from omniscient to fog-filtered data.
- **Relationship SUPPORT:** Hostile target → STRONG objection (aggressive) / MODERATE (cautious). New trigger.
- **Literal bypass:** Grouchy never defies, never objects to hostile SUPPORT.

### Implementation: 2 Sonnet Sessions

- Session 1: Core mechanics (defiance, vindication, authority, serialization)
- Session 2: Fog migration + relationship triggers + polish
- Code review checkpoint between sessions
- ~140 estimated tests
