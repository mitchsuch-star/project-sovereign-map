# V2b Session 2: Fog-of-War Migration — Implementation Prompt

**Date:** February 25, 2026
**Archived after:** Successful implementation (4164 tests, 0 failures)

---

## Original Prompt

Implement V2b Session 2: Fog-of-War Migration. The spec is at `docs/V2B_DEFIANCE_SPEC.md` — read the full file. Session 0 and Session 1 are complete (4076 tests passing). You are implementing Session 2 (§9, "Session 2: Fog-of-War Migration"). Follow Steps 1 through 4 exactly as specified.

**Steps:**
1. Infrastructure (2 helpers): Update `get_visible_enemies_near()` + add `get_target_intel_level()`
2. Type A scan queries (3 leaf → 3 auto-propagate): `_check_enemy_adjacent`, `_get_friendly_to_enemy_ratio`, `_path_crosses_enemy`/`_path_has_enemies`
3. Type B target info queries (2 functions): `_get_attack_odds_ratio`, `_check_attack_target_fortified`
4. New fog-specific triggers (4 situations): attack UNKNOWN, attack STALE, scout-shows-weakness, PURSUE no intel

**Edge cases to verify:**
- EC-3: Multi-battle defensive vindication (Session 1 implemented, verify still works)
- Marshal's own region always FULL (Step 0 rule)
- STALE threshold: current_turn - last_updated_turn >= 3
- Cautious attacks fortified target at PARTIAL → no fort bump
- Fog-filtered ratios: 0 visible enemies → 999.0
- Path with mix of PARTIAL/UNKNOWN regions
- `_check_enemy_in_region()` unchanged
- Aggressive marshal attacking UNKNOWN → no objection

**Deliverables:** 88 new tests, confidence report, archived prompt.
