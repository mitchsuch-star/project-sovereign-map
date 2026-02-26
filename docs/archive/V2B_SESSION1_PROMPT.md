# V2b Session 1: Core Mechanics — Implementation Prompt

**Date:** February 25, 2026
**Archived after:** Successful implementation (4076 tests, 0 failures)

---

## Original Prompt

Implement V2b Session 1: Core Mechanics (Defiance + Vindication + Authority). The spec is at `docs/V2B_DEFIANCE_SPEC.md` — read the full file. Session 0 (prerequisite fix) is complete. You are implementing Session 1 (§9, "Session 1: Core Mechanics"). Follow Parts A through D exactly as specified.

### Key Deliverables

**Part A: Infrastructure**
- New marshal fields: `last_objection_turn`, `defiance_cooldown_until` + serialization
- `recent_responses` format migration: `List[str]` → `List[Dict]` with `{"choice": str, "turn": int}`
- `check_excessive_trust()` in authority.py (replaces old trust-ratio branch)
- Rename `MAX_MAJOR_OBJECTIONS_PER_TURN` → `MAX_OBJECTION_POPUPS_PER_TURN`
- Add `MARSHAL_DEFIED_ORDER` notification type
- Add `"defiance"` campaign log event type

**Part B: Defiance Core**
- `calculate_defiance_chance()` in new `defiance.py`
- `get_defiant_action()` fallback table
- `defiance_succeeded()` three-way return
- Defiance roll wiring in executor.py
- 4-row outcome table application

**Part C: Vindication + Authority**
- Vindication escalation/de-escalation in objection flow
- Vindication decay in advance_turn
- Defensive vindication creation + resolution
- Authority major victory/defeat hooks

**Part D: Relationship SUPPORT Objection**
- Relationship-based trigger in `evaluate_strategic_situation()`
- Timed SUPPORT compromise (`condition.max_turns = 3`)
- `main.py` passthrough for defiance fields

### Edge Cases Required

EC-1 through EC-9 (see V2B_DEFIANCE_SPEC.md §9 confidence gate).

### Constraints

- Do NOT implement Session 2 (fog migration) or Session 3 (frontend)
- Run full test suite — zero regressions
- End with confidence report per §9 protocol
