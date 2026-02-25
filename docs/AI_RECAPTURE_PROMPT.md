# AI Territory Recapture — Implementation Prompt

> Paste this entire prompt into a new Claude Code session in the project root.

---

## PROMPT START

You are implementing a fix for the Enemy AI's failure to recapture lost territory. This is the single highest-impact change needed for game balance. Read CLAUDE.md first for project conventions.

### The Problem

The AI has a P3.7 "Homeland Defense" system (`_find_homeland_defense()` in `backend/ai/enemy_ai.py`) that is supposed to redirect marshals to recapture lost territory. **It doesn't work.** In playtesting:

- Player captured 5 enemy regions (Rhine, Bavaria, Vienna, Geneva, Milan) completely unopposed
- The AI never sent a single marshal to recapture any of them, even after 3+ turns
- The Prussian 3-marshal deathball (Blucher/Gneisenau/PrinceAugust) sat in Belgium the entire game
- The Prussian capital (Vienna) was captured and never contested

### Root Cause Analysis

Read `backend/ai/enemy_ai.py` lines 1350-1394 (P3 through P3.7) and lines 2178-2330 (`_find_homeland_defense`). There are 5 interconnected bugs:

#### Bug 1: P3 Threat Response Blocks P3.7 for Cautious Marshals
P3 (`_check_threats`) fires BEFORE P3.7. When a cautious marshal (Gneisenau, PrinceAugust) sees ANY adjacent enemy — even a small one — P3 returns a fortify/stance action, and P3.7 (homeland defense) is never reached. This means 2 of 3 Prussian marshals can never do homeland defense if there's any enemy within 1 tile.

**Fix:** When the nation has lost its capital or 2+ regions, P3.7 should fire BEFORE P3 for at least one marshal. The capital being lost should be the highest non-survival priority in the entire tree.

#### Bug 2: 3-Hop Range Limit Is Too Short
`_find_homeland_defense` filters targets to `dist <= 3`. The map is 13 regions — from Netherlands to Vienna is 4-5 hops (Netherlands→Belgium→Rhine→Bavaria→Vienna). The AI literally cannot "see" that its capital needs recapturing.

**Fix:** Increase range to 6 (covers entire map). For capital recapture specifically, range should be unlimited.

#### Bug 3: Deathball Never Splits Because of "Someone Closer" Check
Lines 2246-2256: If another marshal from the same nation is at equal or closer distance, the current marshal returns None. When all 3 Prussians are co-located, marshal #1 gets assigned Rhine, marshal #2 checks — sees #1 is same distance to Bavaria (both at Netherlands, dist 3) — returns None because it's not STRICTLY closer. Marshal #3 same. Only 1 of 3 marshals gets a homeland defense assignment.

**Fix:** The "someone closer" check should only skip if another marshal is STRICTLY closer AND that marshal is neither fortified nor drilling. Multiple marshals should be assigned to different lost regions.

#### Bug 4: Won't Move Through Enemy-Occupied Regions
Lines 2308-2311: The pathfinding skips adjacent regions that have enemy marshals. If the player has ANY marshal between the AI and its lost territory, the AI gives up. For homeland defense of your CAPITAL, you should be willing to fight through.

**Fix:** For capital recapture, allow movement toward regions with enemies (the AI will fight via P0 engagement when they arrive). For non-capital recapture, allow movement if the marshal's strength exceeds the enemies in the transit region.

#### Bug 5: Low Priority Score Doesn't Reflect Urgency
P3.7 returns priority 3 — same as generic threat response. The priority system picks the LOWEST score across all marshals. So if marshal A wants to homeland-defend (score 3) and marshal B wants to threat-respond (also score 3), it's a coin flip. Capital recapture should be higher priority.

**Fix:** Return priority 2 for capital recapture (same as survival), priority 3 for non-capital homeland defense.

### Implementation Plan

**Files to modify:** `backend/ai/enemy_ai.py` only.

#### Step 1: Increase Range and Fix Capital Priority

In `_find_homeland_defense()`:
- Change max range from 3 to 6
- Add separate capital detection: if the lost region is the nation's capital (`region.is_capital`), set priority to 2 and range to unlimited
- Return the priority as part of the result so `_evaluate_marshal` can use it

```python
# Example: Return tuple with priority
def _find_homeland_defense(self, marshal, nation, world):
    # ... existing checks ...

    # Increase range: 6 for normal regions, unlimited for capital
    max_range = 6
    for lost_name in unclaimed_lost:
        lost_region = world.get_region(lost_name)
        is_capital = lost_region and lost_region.is_capital
        effective_range = 999 if is_capital else max_range
        dist = world.get_distance(marshal.location, lost_name)
        if dist > effective_range:
            continue
        # ... rest of evaluation ...

    # Return (action, is_capital_recapture) so caller can set priority
```

#### Step 2: Fix the "Someone Closer" Check to Allow Deathball Splitting

Replace the "someone else is closer" check with a smarter system:

```python
# OLD (broken): Skip if ANY other marshal is closer
for other in nation_marshals:
    if other_dist < my_dist:
        return None  # Someone else handles it

# NEW: Skip only if another AVAILABLE marshal is strictly closer
# and assign different targets to different marshals
for other in nation_marshals:
    if other.name == marshal.name:
        continue
    if other.strength <= 0:
        continue
    # Skip unavailable marshals (fortified, drilling, broken, retreating)
    if getattr(other, 'fortified', False):
        continue
    if getattr(other, 'drilling', False) or getattr(other, 'drilling_locked', False):
        continue
    if getattr(other, 'broken', False) or getattr(other, 'retreat_recovery', 0) > 0:
        continue
    other_dist = world.get_distance(other.location, best_target)
    if other_dist < my_dist:
        # Check if that closer marshal already claimed a DIFFERENT target
        if other.name not in [... marshals who already got assignments ...]:
            return None  # Let the closer available marshal handle it
```

#### Step 3: Allow Movement Through Contested Regions for Capital Recapture

In the "2-3 hops away" pathfinding section, relax the enemy-blocking filter for capital targets:

```python
# For capital recapture, allow moving through contested regions
# if our marshal is strong enough to fight through
if enemies_there and not is_capital_target:
    continue  # Normal: skip enemy-occupied
if enemies_there and is_capital_target:
    total_enemy = sum(e.strength for e in enemies_there)
    if marshal.strength < total_enemy * 0.5:
        continue  # Too weak even for desperate march
    # Otherwise allow — P0 will handle the fight when we arrive
```

#### Step 4: Elevate Priority When Homeland Is Threatened

In `_evaluate_marshal()`, modify the P3/P3.7 ordering so homeland defense can override threat response when critical:

```python
# Check if nation has lost capital BEFORE P3 threat response
capital_lost = self._is_capital_lost(nation, world)
regions_lost_count = self._count_lost_regions(nation, world)

# If capital is lost, P3.7 fires BEFORE P3 (priority 2)
if capital_lost:
    homeland_action = self._find_homeland_defense(marshal, nation, world)
    if homeland_action:
        return (homeland_action, 2)  # Same as survival — capital IS survival

# Normal P3 threat response
threat_action = self._check_threats(marshal, nation, world)
if threat_action:
    # If 2+ regions lost, only let P3 block P3.7 for ONE marshal per nation
    if regions_lost_count >= 2 and self._homeland_defenders_needed(nation, world):
        pass  # Skip P3, fall through to P3.7
    else:
        return (threat_action, 3)

# P3.7 homeland defense (normal priority)
homeland_action = self._find_homeland_defense(marshal, nation, world)
if homeland_action:
    return (homeland_action, 3)
```

#### Step 5: Add Helper Methods

```python
def _is_capital_lost(self, nation: str, world: WorldState) -> bool:
    """Check if this nation's capital is controlled by an enemy."""
    for region in world.regions.values():
        if region.is_capital and region.name in world.nation_starting_regions.get(nation, []):
            return region.controller != nation
    return False

def _count_lost_regions(self, nation: str, world: WorldState) -> int:
    """Count how many starting regions this nation has lost."""
    starting = world.nation_starting_regions.get(nation, [])
    return sum(1 for r in starting if world.get_region(r) and world.get_region(r).controller != nation)
```

### Test Plan

Write tests in `tests/test_ai_recapture.py`. Key scenarios:

```python
# Test 1: Basic recapture — marshal moves toward lost region
def test_homeland_defense_moves_toward_lost_region():
    """When Prussia loses Rhine, nearest Prussian marshal moves toward it."""
    world = WorldState(player_nation="France")
    world.get_region("Rhine").controller = "France"  # Player captured Rhine
    blucher = world.get_marshal("Blucher")
    blucher.location = "Netherlands"  # 2 hops from Rhine

    ai = EnemyAI(CommandExecutor())
    action, priority = ai._evaluate_marshal(blucher, "Prussia", world)

    assert action is not None
    assert action["action"] == "move"
    assert action["target"] == "Belgium"  # Moves toward Rhine

# Test 2: Capital recapture is highest non-survival priority
def test_capital_recapture_priority():
    """Recapturing the capital should have priority 2 (survival-level)."""
    world = WorldState(player_nation="France")
    world.get_region("Vienna").controller = "France"  # Player took capital
    gneisenau = world.get_marshal("Gneisenau")
    gneisenau.location = "Bavaria"  # Adjacent to Vienna

    ai = EnemyAI(CommandExecutor())
    action, priority = ai._evaluate_marshal(gneisenau, "Prussia", world)

    assert action is not None
    assert priority == 2  # Capital = survival priority
    assert action["action"] == "attack"
    assert action["target"] == "Vienna"

# Test 3: Deathball splits when multiple regions lost
def test_deathball_splits_for_recapture():
    """When 2+ regions lost, marshals split to recapture different targets."""
    world = WorldState(player_nation="France")
    world.get_region("Rhine").controller = "France"
    world.get_region("Bavaria").controller = "France"
    # All 3 Prussians co-located
    for name in ["Blucher", "Gneisenau", "PrinceAugust"]:
        world.get_marshal(name).location = "Belgium"

    ai = EnemyAI(CommandExecutor())
    game_state = {"world": world}
    results = ai.process_nation_turn("Prussia", world, game_state)

    # At least 2 marshals should be moving toward different targets
    move_targets = [r["ai_action"]["target"] for r in results
                    if r.get("ai_action", {}).get("action") == "move"]
    assert len(set(move_targets)) >= 2, f"Expected split, got targets: {move_targets}"

# Test 4: P3 threat response doesn't block capital recapture
def test_threat_response_doesnt_block_capital_recapture():
    """Even with adjacent enemies, capital recapture should fire."""
    world = WorldState(player_nation="France")
    world.get_region("Vienna").controller = "France"
    gneisenau = world.get_marshal("Gneisenau")
    gneisenau.location = "Bavaria"  # Adjacent to Vienna
    # Place a French marshal adjacent to create a "threat"
    ney = world.get_marshal("Ney")
    ney.location = "Rhine"  # Adjacent to Bavaria
    ney.strength = 70000  # Stronger than Gneisenau

    ai = EnemyAI(CommandExecutor())
    action, priority = ai._evaluate_marshal(gneisenau, "Prussia", world)

    # Should STILL try to recapture Vienna despite adjacent threat
    assert action is not None
    assert action["target"] == "Vienna" or action["action"] == "attack"

# Test 5: Won't recapture if broken/retreating
def test_broken_marshal_doesnt_recapture():
    """Broken marshals should recover, not try to recapture."""
    world = WorldState(player_nation="France")
    world.get_region("Rhine").controller = "France"
    blucher = world.get_marshal("Blucher")
    blucher.location = "Netherlands"
    blucher.broken = True
    blucher.retreat_recovery = 2

    ai = EnemyAI(CommandExecutor())
    action, priority = ai._evaluate_marshal(blucher, "Prussia", world)

    # Should be recovery action, NOT homeland defense
    assert priority == 1  # Recovery priority

# Test 6: Extended range reaches distant regions
def test_extended_range_reaches_capital():
    """Marshals at Netherlands can target Vienna (4-5 hops)."""
    world = WorldState(player_nation="France")
    world.get_region("Vienna").controller = "France"
    blucher = world.get_marshal("Blucher")
    blucher.location = "Netherlands"

    ai = EnemyAI(CommandExecutor())
    action, _ = ai._evaluate_marshal(blucher, "Prussia", world)

    assert action is not None
    assert action["action"] == "move"  # Should start moving

# Test 7: Cautious marshal still recaptures when P3 would normally fire
def test_cautious_marshal_recaptures_over_fortifying():
    """Gneisenau (cautious) should recapture instead of fortifying when 2+ regions lost."""
    world = WorldState(player_nation="France")
    world.get_region("Rhine").controller = "France"
    world.get_region("Bavaria").controller = "France"
    gneisenau = world.get_marshal("Gneisenau")
    gneisenau.location = "Belgium"  # Adjacent to Rhine
    gneisenau.stance = Stance.DEFENSIVE
    # Place enemy adjacent to trigger P3
    ney = world.get_marshal("Ney")
    ney.location = "Paris"
    ney.strength = 70000

    ai = EnemyAI(CommandExecutor())
    action, _ = ai._evaluate_marshal(gneisenau, "Prussia", world)

    # Should recapture Rhine, not fortify
    assert action["action"] in ("attack", "move")
    assert action["target"] == "Rhine"

# Test 8: Full integration — Southern Bypass scenario
def test_southern_bypass_ai_response():
    """Simulate the Southern Bypass strategy and verify AI responds."""
    world = WorldState(player_nation="France")
    executor = CommandExecutor()
    ai = EnemyAI(executor)
    game_state = {"world": world}

    # Player captures Rhine, Bavaria, Vienna (like Game 2 playtest)
    for region_name in ["Rhine", "Bavaria", "Vienna"]:
        world.get_region(region_name).controller = "France"

    # All Prussians at Belgium (like the playtest)
    for name in ["Blucher", "Gneisenau", "PrinceAugust"]:
        m = world.get_marshal(name)
        m.location = "Belgium"

    results = ai.process_nation_turn("Prussia", world, game_state)

    # At least 2 marshals should be heading toward lost territory
    actions = [r.get("ai_action", {}) for r in results if r.get("success")]
    move_actions = [a for a in actions if a.get("action") == "move"]

    assert len(move_actions) >= 2, (
        f"Expected at least 2 marshals moving to recapture, got {len(move_actions)}. "
        f"Actions: {actions}"
    )
```

### Validation

After implementation:
```bash
# Run the new tests
".venv\Scripts\python.exe" -m pytest tests/test_ai_recapture.py -v

# Run the full test suite (ensure no regressions)
".venv\Scripts\python.exe" -m pytest tests/ -v --tb=short -q

# Manual validation with curl
# Start server, then simulate the Southern Bypass:
# 1. Move all French to Lyon, capture Rhine
# 2. End turn
# 3. Check /status — Prussians should be MOVING toward Rhine
```

### Key Constraints (from CLAUDE.md)

- **Enemy AI uses SAME executor as player** — don't create special recapture commands
- **All numbers to Godot: `int()`** — wrap any new numeric returns
- **Serialization enforcement** — if you add new fields to WorldState, add to `to_dict()`/`from_dict()` and run `test_serialization_enforcement.py`
- **Don't change P0 (engagement) or P1 (retreat recovery)** — those are survival-critical
- **Update docs:** After implementation, update `docs/ENEMY_AI_REFERENCE.md` (P3.7 section) and `docs/STATUS.md`

### What Success Looks Like

After this fix, playtesting the Southern Bypass strategy should show:
1. Player captures Rhine → at least 1 Prussian marshal starts moving toward Rhine within 1-2 turns
2. Player captures Vienna (capital) → nearest available Prussian marshal IMMEDIATELY redirects, even if it means abandoning fortification
3. The Prussian deathball SPLITS: different marshals head toward different lost regions
4. Cautious marshals (Gneisenau) participate in recapture even when enemies are nearby
5. The Southern Bypass is no longer a free win — the player must defend captured territory

## PROMPT END
