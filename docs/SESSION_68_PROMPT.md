# Session 68: Auto-Bombardment + Overwatch (Tactical Triangle Part B)

> **Paste this entire prompt into a fresh Claude Code context.**
> **Prerequisite:** Session 67 (Square Formation) is complete and committed. 3926 tests passing.

---

## TASK

Implement Session 68 of the Tactical Triangle: **Artillery SUPPORT Auto-Bombardment** and **Artillery Overwatch**. These are Features 2 and 3 from `docs/TACTICAL_TRIANGLE_SPEC.md` (APPROVED design).

**Target: ~50 tests. WHEN DONE PROVIDE CONFIDENCE REPORT. MAKE IT 100% IF POSSIBLE. LOOK FOR EDGE CASES AS YOU WORK. DON'T BE SHY ABOUT BEING SMART.**

After the confidence report, **OUTPUT THE GATE 5 UI TEST CHECKLIST** from `docs/PHASE7_UI_TEST_GATE.md` so the user can run manual tests covering both Session 67 (Square Formation) and Session 68 (Auto-Bombardment + Overwatch) together.

---

## WHAT TO BUILD

### Feature A: Artillery SUPPORT Auto-Bombardment (~28 tests)

**Concept:** When an artillery marshal is on a SUPPORT order targeting Marshal X, and Marshal X attacks an enemy, the artillery auto-bombards the defender BEFORE combat resolves. Free preparatory bombardment that softens the target.

**Where it fires:** Inside `executor.py::_execute_attack()` (line ~3172), AFTER coordination context is calculated but BEFORE `resolve_battle()`. The bombardment result is prepended to the combat output.

**Implementation steps:**

1. **New block in `_execute_attack()`** — after coordination context calculation, before `resolve_battle()`:
   ```
   For each same-nation artillery marshal with SUPPORT order targeting the attacker:
       IF eligible (adjacent/co-located to battle region, not moved_this_turn,
                    bombardments_this_turn < 2, not broken/retreating/recovering,
                    strength > 0):
           Execute bombardment against defender using existing _execute_bombardment()
           Append result to pre_battle_messages list
           Defender takes damage BEFORE resolve_battle()

           IF defender.strength <= 0: break  # Early exit — dead target
   ```

2. **Dead-defender check after loop** — if `defender.strength <= 0`:
   - Skip `resolve_battle()` entirely
   - Declare attacker victory with 0 attacker casualties
   - Handle advance/capture normally
   - Message: "The preparatory bombardment destroyed {defender}. {attacker} advances unopposed."
   - Return early

3. **Constraints (all tested):**
   - Artillery must be adjacent to OR co-located with the battle region (bombardment range)
   - Artillery must NOT have `moved_this_turn`
   - Artillery must have `bombardments_this_turn < 2` (shared pool)
   - Artillery must NOT be broken/retreating/recovering
   - Consumes one of the artillery's `bombardments_this_turn`
   - Does NOT consume player AP
   - Collateral damage rules still apply (friendly fire possible!)
   - Fort degradation applies
   - Bombardment streak increments normally
   - Does NOT fire on defensive battles (only when supported marshal is ATTACKER)
   - Does NOT fire on auto-charge (reckless cavalry glorious charge)
   - Multiple SUPPORT artillery can fire (each spends their own slot)
   - Early exit inside loop if defender dies (don't waste remaining artillery slots)

4. **Fog of war:** When auto-bombardment fires from an adjacent region, the defender gains PARTIAL intel on the source region. Call the intel update method to record this.

5. **Battle report observations (2 new in `battle_report.py`):**
   - `support_bombardment_effective`: "Drouot's preparatory bombardment was devastating. {marshal}'s charge met a shaken enemy."
   - `support_bombardment_minimal`: "Drouot's guns fired in support, though the terrain blunted their effect."
   - Add to `_pick_observation()` priority chain — suggest Priority 0.6 (between reinforcement arrival P0.7 and full combined arms P0.5)

### Feature B: Artillery Overwatch (~22 tests)

**Concept:** Enemy artillery in the defender's region passively debuffs all attackers by -3% per gun. No action needed — the guns are simply *there*, suppressing the assault.

**Implementation steps:**

1. **New transient field on Marshal** in `marshal.py`:
   ```python
   # In get_attack_modifier(), AFTER coordination bonus line (~line 830):
   modifier *= (1.0 - getattr(self, 'overwatch_penalty', 0.0))
   ```
   This is a transient field — NOT in `__init__`, NOT serialized. Set dynamically, read via `getattr`, cleared after combat.

2. **New helper in `executor.py`:**
   ```python
   def _calculate_overwatch(self, attacker, attacking_allies, defender_region, world):
       """Count enemy artillery in defender's region, apply penalty to all attackers."""
       enemy_artillery_count = 0
       for m in world.marshals.values():
           if (m.location == defender_region
                   and m.nation != attacker.nation
                   and getattr(m, 'artillery', False)
                   and m.strength > 0
                   and not getattr(m, 'broken', False)
                   and not getattr(m, 'retreated_this_turn', False)
                   and getattr(m, 'retreat_recovery', 0) == 0
                   and not getattr(m, 'moved_this_turn', False)):
               enemy_artillery_count += 1

       capped = min(enemy_artillery_count, 3)  # -9% max
       penalty = capped * 0.03

       for combatant in [attacker] + (attacking_allies or []):
           combatant.overwatch_penalty = penalty
   ```

3. **Call site:** In `_execute_attack()`, call `_calculate_overwatch()` alongside coordination context, BEFORE `resolve_battle()`. Must also clear the field after combat (add `overwatch_penalty` to the `COORDINATION_FIELDS` cleanup list or clear separately).

4. **Constraints:**
   - Only non-broken, non-retreating, non-recovering, non-moved artillery counts
   - Cap at 3 artillery (-9% max overwatch)
   - Does NOT apply to bombardment (ranged fire isn't affected by local overwatch)
   - Does NOT apply to the artillery marshal itself when it's the defender in melee
   - Two-artillery mutual overwatch: artillery A provides overwatch when B is attacked
   - Applies to ALL attacking participants (primary + allies), not just primary
   - Overwatch is NOT coordination — does not count toward +25%/+20% hard cap
   - Applies to both player and AI attacks (Building Blocks)

5. **AI awareness** in `enemy_ai.py::_evaluate_target_ratio()` (~line 1847) or `_find_attack_opportunity()` (~line 2045):
   ```python
   # Factor overwatch into effective ratio
   overwatch_count = min(enemy_artillery_in_target_region, 3)
   effective_ratio *= (1.0 - overwatch_count * 0.03)
   ```
   This makes AI less eager to attack regions with artillery.

6. **Battle report:**
   - Attacker snapshot entry: "Artillery overwatch ({artillery_name}): -3% attack" (penalty type)
   - New Berthier observation: `overwatch_repelled` — "The enemy advance faltered under {artillery}'s watchful guns."
   - Add to `_pick_observation()` — suggest Priority 6f (after square observations at 6e)

---

## KEY CODE LOCATIONS

Read these files before implementing:

| File | Line | What's there |
|------|------|-------------|
| `executor.py` | ~3172 | `_execute_attack()` — insert auto-bombardment + overwatch here |
| `executor.py` | ~2818 | `_execute_bombardment()` — reuse this for auto-bombardment |
| `marshal.py` | ~830 | `get_attack_modifier()` — add overwatch penalty after coordination line |
| `battle_report.py` | | `snapshot_attacker_modifiers()` — add overwatch entry |
| `battle_report.py` | | `_OBSERVATIONS` + `_pick_observation()` — add 3 new categories |
| `enemy_ai.py` | ~1847 | `_evaluate_target_ratio()` — add overwatch factor |
| `combat.py` | | Square interaction messages (already implemented in S67, reference only) |

**Also read:** `docs/TACTICAL_TRIANGLE_SPEC.md` (the full approved spec, Features 2 and 3).

---

## CRITICAL PATTERNS TO FOLLOW

1. **Golden Rule #1:** Combat modifiers SINGLE SOURCE in `marshal.py`. The overwatch penalty goes in `get_attack_modifier()`. The `_calculate_overwatch()` helper only SETS the transient field — it does NOT calculate the modifier itself.

2. **Golden Rule #2:** All numbers to Godot: `int()`.

3. **Building Blocks:** AI uses SAME executor as player. Auto-bombardment fires for AI artillery on SUPPORT too. No separate AI code path.

4. **Transient field pattern:** `overwatch_penalty` follows the Phase 7 pattern — NOT in `__init__`, NOT serialized. Set via assignment, read via `getattr(self, 'overwatch_penalty', 0.0)`, cleared after combat. Add to `COORDINATION_FIELDS` cleanup list in executor.

5. **Deferred casualty path:** Session 62 introduced `resolve_battle(apply_casualties=False)`. Auto-bombardment fires BEFORE resolve_battle, so it doesn't interact with the deferred path directly — but the dead-defender check must handle the case where bombardment kills the defender before resolve_battle is even called.

6. **Bombardment reuse:** Auto-bombardment calls the existing `_execute_bombardment()`. Do NOT duplicate the bombardment formula. The same terrain modifiers, collateral rules, streak tracking, fort degradation, and square bonuses (+50% damage, -15 morale) all apply automatically.

7. **SUPPORT order detection:** Check `marshal.strategic_order` is not None, `marshal.strategic_order.command_type == "SUPPORT"`, and `marshal.strategic_order.target == attacker.name`.

8. **Auto-bombardment does NOT fire when:**
   - Supported marshal is the DEFENDER (only offensive attacks trigger it)
   - Attack is an auto-charge (reckless cavalry glorious charge — check `skip_reckless_popup` or the `_strategic_execution` flag)
   - Actually: the simplest check is whether we're inside a glorious charge path. Check for `command.get("_glorious_charge")` or similar flag.

---

## TEST CHECKLIST (from spec)

### Auto-Bombardment (~28 tests):
- [ ] Artillery on SUPPORT fires bombardment before supported marshal's attack
- [ ] Auto-bombardment uses existing bombardment formula (same damage, terrain mods)
- [ ] Auto-bombardment vs square: +50% damage AND -15 extra morale (inherits from S67)
- [ ] Auto-bombardment respects bombardments_this_turn limit (2 max shared pool)
- [ ] Auto-bombardment increments bombardments_this_turn
- [ ] Auto-bombardment does NOT fire if artillery moved_this_turn
- [ ] Auto-bombardment does NOT fire if artillery is broken/retreating/recovering
- [ ] Auto-bombardment does NOT fire on defensive battles (supported marshal is defender)
- [ ] Auto-bombardment does NOT fire if artillery not adjacent/co-located with battle region
- [ ] Auto-bombardment does NOT consume player AP
- [ ] Collateral damage rules apply (friendly fire possible)
- [ ] Fort degradation applies
- [ ] Bombardment streak increments
- [ ] Defender takes bombardment damage BEFORE resolve_battle
- [ ] Dead-defender check: if defender.strength <= 0 after bombardment, skip resolve_battle
- [ ] Auto-bombardment result appears in combat output as preamble
- [ ] Multiple SUPPORT artillery can fire (each spends their own bombardment slot)
- [ ] Auto-bombardment does NOT fire on auto-charge (reckless cavalry)
- [ ] Berthier observation: effective support bombardment
- [ ] AI artillery on SUPPORT also auto-bombards (Building Blocks)
- [ ] Bombardment result includes all standard fields (fort degradation, collateral, etc.)
- [ ] Fog: auto-bombardment from adjacent region gives defender PARTIAL intel on source region
- [ ] Auto-bombardment does NOT add combined arms type counting (already excluded per A-D6)
- [ ] SUPPORT order persists after auto-bombardment fires (order not consumed)
- [ ] Artillery with 0 bombardments remaining this turn skipped
- [ ] Early exit inside loop if defender dies mid-bombardment sequence

### Overwatch (~22 tests):
- [ ] Enemy artillery in defender's region applies -3% attack to attacker
- [ ] Overwatch applies to ALL attacking participants (primary + allies), not just primary
- [ ] Multiple enemy artillery stack (-6% for 2)
- [ ] Cap at 3 artillery (-9% max overwatch)
- [ ] Broken/retreating/recovering artillery does NOT provide overwatch
- [ ] Artillery that moved_this_turn does NOT provide overwatch
- [ ] Overwatch does NOT apply to bombardment (ranged attack)
- [ ] Overwatch penalty appears in attacker's modifier list in battle report
- [ ] Overwatch is NOT counted toward coordination hard cap (it's a debuff, not a bonus)
- [ ] Transient field `overwatch_penalty` resets after combat
- [ ] overwatch_penalty NOT serialized (transient — not in to_dict/from_dict)
- [ ] Two-artillery mutual overwatch: artillery A provides overwatch when B is attacked
- [ ] AI uses overwatch in target ratio assessment (-3% per gun)
- [ ] Berthier observation when overwatch contributed to defense
- [ ] Overwatch applies to both player and AI attacks (Building Blocks)
- [ ] Overwatch from fortified artillery still applies
- [ ] Overwatch does NOT apply from artillery that is itself the defender
- [ ] int() wrapping on overwatch penalty value
- [ ] No overwatch when 0 eligible artillery in region
- [ ] Overwatch field cleared after combat (in COORDINATION_FIELDS or separate cleanup)

---

## IMPLEMENTATION ORDER

1. **Feature A: Auto-Bombardment** — modify `executor.py` `_execute_attack()`, add auto-bombardment block. Add battle report observations. Test.
2. **Feature B: Overwatch** — add transient field to `marshal.py`, add `_calculate_overwatch()` to `executor.py`, wire into `_execute_attack()`. Add snapshot/observation to `battle_report.py`. Wire AI. Test.
3. **Run full test suite** — confirm 0 regressions.
4. **Update docs:** STATUS.md (session entry, test count), SYSTEMS_REFERENCE.md (auto-bombardment + overwatch sections), SAVE_FORMAT_REFERENCE.md (note overwatch_penalty is NOT serialized — transient field).
5. **Confidence report** — system-by-system coverage, edge cases handled.
6. **Output Gate 5 UI test checklist** — from `docs/PHASE7_UI_TEST_GATE.md`.

---

## GOTCHAS (from spec — review these)

| Issue | Solution |
|-------|----------|
| Auto-bombardment + collateral on own supported marshal | Supported marshal could take friendly fire if co-located with defender. Working as designed — flag in test. |
| HOLD artillery vs SUPPORT artillery priority | HOLD auto-bombards during strategic phase. SUPPORT auto-bombards during attack execution. Different timing, no conflict. |
| Multiple SUPPORT artillery overkill dead target | Early-exit inside for-each loop: `if defender.strength <= 0: break` |
| Overwatch penalty on attacker who also has coordination bonus | Independent. Both apply. Net example: +13% coordination and -3% overwatch = effective ~+10%. |
| Auto-bombardment fires, then battle resolves with weakened defender | Working as designed — that's the whole point. |
| Square + auto-break + coordination timing | Square breaks at START of _execute_attack, BEFORE coordination context. The auto-bombardment fires AFTER coordination is calculated but BEFORE resolve_battle. |
| Same-side artillery mutual overwatch | Artillery A provides overwatch when B is attacked. Each excluded from its OWN defense only. |
| Overwatch during bombardment | Does NOT apply — bombardment is ranged, overwatch is local suppression. |
| Auto-bombardment fog intel | Defender's nation gains PARTIAL intel on the source region when shelled from adjacent. |

---

## DOC UPDATES REQUIRED

| Doc | What to update |
|-----|---------------|
| `docs/STATUS.md` | Session 68 entry, test count, next steps (V2b or Jealousy, both need design approval) |
| `docs/SYSTEMS_REFERENCE.md` | Add auto-bombardment section (under Artillery or new subsection), add overwatch section |
| `docs/SAVE_FORMAT_REFERENCE.md` | Note that `overwatch_penalty` is NOT serialized (transient). No new serialized fields this session. |
| `CLAUDE.md` | Update "Completed in Phase 7b" with Session 68 summary. Update "Up Next" to remove Tactical Triangle. |

---

## COMMANDS

```bash
# Run tests
".venv\Scripts\python.exe" -m pytest tests/ -v --tb=no -q

# Run just Session 68 tests
".venv\Scripts\python.exe" -m pytest tests/test_auto_bombardment_overwatch.py -v

# Run serialization enforcement
".venv\Scripts\python.exe" -m pytest tests/test_serialization_enforcement.py -v

# Full suite with short failures
".venv\Scripts\python.exe" -m pytest tests/ -v --tb=short -q
```
