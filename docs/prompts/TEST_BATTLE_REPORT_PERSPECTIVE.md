# Prompt: Battle Report Perspective Tests

## Goal

Add tests to `tests/test_battle_report.py` that verify Berthier's observation perspective logic works correctly for:
1. Enemy attacking a French marshal (the original bug — defender is the player)
2. French marshal attacking an enemy (the normal case — attacker is the player)
3. Non-France player nations (future-proofing for playable Britain, Prussia, etc.)
4. Edge cases: missing nation fields, third-party battles, symmetric matchups

## Context

`backend/game_logic/battle_report.py` has a function `_pick_observation(battle_result, player_nation="France")` that selects Berthier's one-liner observation after combat. It was recently rewritten to be perspective-aware: "we won" means the player's side won, regardless of whether the player was attacking or defending.

The perspective logic (lines 262-287 of `battle_report.py`):
```python
attacker_nation = battle_result.get("attacker_nation", "")
defender_nation = battle_result.get("defender_nation", "")
we_are_attacker = (attacker_nation == player_nation)

if we_are_attacker:
    we_won = attacker_won
    we_lost = defender_won
    our_mods = atk_mods
    their_mods = def_mods
    our_name = attacker_data.get("name", "Attacker")
    enemy_name = defender_data.get("name", "Defender")
else:
    we_won = defender_won
    we_lost = attacker_won
    our_mods = def_mods
    their_mods = atk_mods
    our_name = defender_data.get("name", "Defender")
    enemy_name = attacker_data.get("name", "Attacker")
```

Templates use `{marshal}` (our side) and `{enemy}` (their side) placeholders.

`generate_battle_report(battle_result, player_nation="France")` passes `player_nation` to `_pick_observation`.

## Known Gaps

1. **Every existing observation test uses `atk_nation="France"` (the default).** Zero tests verify the flipped case where the enemy is the attacker.

2. **`combat.py` line 620 calls `generate_battle_report(result_dict)` without passing `player_nation`**, relying on the default `"France"`. This means the report is always generated assuming France is the player. For future multi-nation support, `player_nation` would need to be threaded from `world.player_nation` through `resolve_battle()` into `generate_battle_report()`. Tests should flag this gap.

3. **No test verifies `{marshal}` and `{enemy}` are filled correctly when perspective flips.** The templates should never contain literal `{marshal}` or `{enemy}` in the output.

## What to Test

### Class: TestPerspectiveFlip (new class in test_battle_report.py)

Use the existing `_pick_observation` import (already imported at line 19). Use the existing `_make_result` helper pattern from `TestObservationPriority` class or create a similar helper.

#### Core flip tests:

1. **`test_french_attacker_wins_is_victory`** — France attacks Britain, attacker wins. Observation should reference the French marshal positively (victory/decisive/dominated).

2. **`test_french_defender_wins_is_victory`** — Britain attacks France, defender wins. Observation should reference the French marshal positively, NOT celebrate Britain's attack.

3. **`test_french_attacker_loses_is_defeat`** — France attacks Britain, defender wins. Observation should reflect French loss (cost/terrain/fortification).

4. **`test_french_defender_loses_is_defeat`** — Britain attacks France, attacker wins. Observation should reflect French loss, not celebrate Britain's victory.

5. **`test_names_correct_when_france_attacks`** — France (Ney) attacks Britain (Wellington). Check observation contains "Ney" (as {marshal}) not "Wellington" for the "our side" references.

6. **`test_names_correct_when_france_defends`** — Britain (Wellington) attacks France (Grouchy). Check observation contains "Grouchy" (as {marshal}) for our side. Wellington should only appear as the enemy.

7. **`test_no_unfilled_placeholders`** — For both attacker and defender perspectives, verify the observation string does NOT contain literal `{marshal}` or `{enemy}`.

#### Modifier perspective tests:

8. **`test_fortification_loss_when_defending`** — French defender has fortification modifier, enemy attacker wins. Should NOT trigger "lost_into_fortification" (that's for when WE attack into THEIR fortification). Should trigger something else.

9. **`test_fortification_loss_when_attacking`** — French attacker loses, enemy defender has fortification. Should trigger "lost_into_fortification" (we attacked their fort and lost).

10. **`test_terrain_advantage_is_enemies_terrain`** — French attacker loses, enemy defender has terrain bonus. "lost_terrain_disadvantage" should fire. Then flip: French defender loses, enemy attacker does NOT have terrain (defender has it). Terrain advantage check should look at THEIR mods, not ours.

11. **`test_drill_victory_uses_our_drill`** — French defender wins with drill bonus in def_mods. "won_drilled" should trigger (our mods are def_mods when we're defender).

12. **`test_bad_stance_uses_our_aggressive`** — French defender is in aggressive stance and loses. Enemy attacker is in defensive stance. "lost_bad_stance" should trigger because OUR mods (def_mods) have aggressive and THEIR mods (atk_mods) have defensive.

#### Multi-nation / future-proof tests:

13. **`test_non_france_player_nation`** — Set `player_nation="Britain"`, attacker is Britain, defender is France. Observation should treat Britain as "us". Verifies the system isn't hardcoded to France.

14. **`test_prussia_as_player_defends`** — `player_nation="Prussia"`, attacker is France, defender is Prussia, defender wins. Should be a victory observation from Prussia's perspective.

15. **`test_third_party_battle`** — `player_nation="France"`, attacker is Britain, defender is Prussia. Neither side is the player. `we_are_attacker` is False (Britain != France), so it defaults to defender perspective (Prussia). This is a known behavior — document it but don't necessarily "fix" it. Just verify it doesn't crash and returns a valid observation string.

16. **`test_player_nation_default_is_france`** — Call `_pick_observation(result)` without explicit `player_nation`. Verify it behaves identically to `_pick_observation(result, "France")`.

#### Edge case tests:

17. **`test_missing_nation_fields`** — Battle result without `attacker_nation`/`defender_nation` keys. Should not crash. `we_are_attacker` will be `"" == "France"` = False, defaulting to defender perspective.

18. **`test_empty_nation_strings`** — Both nations are `""`. Should not crash and should return a valid observation.

19. **`test_same_nation_battle`** — Both attacker and defender are France (civil war edge case). `we_are_attacker` = True. Should work without crashing.

20. **`test_generate_battle_report_accepts_player_nation`** — Call `generate_battle_report(result, player_nation="Britain")` and verify the observation reflects Britain's perspective, not France's.

### Wiring gap test (integration):

21. **`test_combat_resolver_uses_default_france`** — Call `CombatResolver().resolve_battle()` with a French attacker and British defender. Verify `battle_report` is present and observation is from France's perspective. Then call with British attacker and French defender. Verify observation is STILL from France's perspective (because combat.py hardcodes the default).

22. **`test_combat_result_includes_nation_fields`** — Verify `resolve_battle()` return dict contains `attacker_nation` and `defender_nation` matching the marshals' `.nation` attributes.

## Helper Pattern

Use this helper (similar to existing `_make_result` in `TestObservationPriority`):

```python
def _make_result(self, outcome, atk_cas=5000, def_cas=8000,
                 atk_orig=50000, def_orig=68000, atk_mods=None, def_mods=None,
                 atk_nation="France", def_nation="Britain",
                 atk_name="Ney", def_name="Wellington"):
    return {
        "outcome": outcome,
        "attacker": {"name": atk_name, "casualties": atk_cas, "remaining": atk_orig - atk_cas},
        "defender": {"name": def_name, "casualties": def_cas, "remaining": def_orig - def_cas},
        "attacker_nation": atk_nation,
        "defender_nation": def_nation,
        "attacker_original_strength": atk_orig,
        "defender_original_strength": def_orig,
        "modifier_snapshot": {
            "attacker": atk_mods or [],
            "defender": def_mods or [],
        },
    }
```

## Files to Modify

- `tests/test_battle_report.py` — Add `TestPerspectiveFlip` class with ~22 tests

## Files to Read First

- `backend/game_logic/battle_report.py` — The full file, especially `_pick_observation` and `_OBSERVATIONS` templates
- `tests/test_battle_report.py` — Existing tests and helpers to follow the same patterns

## Constraints

- Do NOT modify `battle_report.py` or `combat.py` — this is a test-only task
- All tests should pass with the current code
- Follow existing test patterns (pytest classes, assert-based, no unittest.mock needed for these)
- If any test FAILS, that reveals a real bug. Document it in the test with a comment but make the test assert the ACTUAL behavior (so it passes), and add a `# BUG:` comment explaining what the correct behavior should be
- Run `pytest tests/test_battle_report.py -v` to verify all pass
- Run `pytest tests/ -v --tb=short` to verify no regressions
