# PROJECT SOVEREIGN - DEVELOPMENT PLAN
## For Claude Code Reference

> **Last Updated:** 2025-01-16 - Week 1 Day 2 Complete
> **Current Phase:** Phase 2 - Combat, Skills, and Disobedience (Week 1 of 4)

---

## 🎯 CURRENT STATUS

### ✅ Completed (Week 1 Days 1-2)

**MVP Complete (Jan 15, 2025):**
- Basic combat, movement, conquest
- Action economy (4 actions/turn)
- Command parsing (NL → structured)
- Victory/defeat conditions
- 13-region Waterloo scenario
- 5 marshals (Ney, Davout, Grouchy, Wellington, Blücher)

**Phase 2 Day 1-2 (Jan 16, 2025):**
- [x] Combat dice system (2d6 + skill modifiers)
  - Variance works, skilled marshals still advantaged
  - Narrative descriptions (no raw roll numbers)
  - Critical success/failure on natural 12/2
  - File: `backend/game_logic/combat.py`
  - Tests: `tests/test_combat_dice.py`

- [x] Bug fixes:
  - Paris-Waterloo adjacency corrected
  - Action consumption moved after validation
  - No more wasted actions on failed commands

- [x] Fuzzy matching for typo tolerance
  - Auto-corrects: "waterlo" → "Waterloo", "davot" → "Davout"
  - Rejects bad input: "xyz" → error
  - File: `backend/utils/fuzzy_matcher.py`
  - Tests: `tests/test_fuzzy_matching.py`

---

## 🚧 CURRENT TASK: 6-Skill System (Days 3-4)

**Goal:** Make marshals feel different through skills

**Implementation:**
1. Add 6 skills to Marshal model:
   - Tactical, Shock, Defense, Logistics, Administration, Command
   - Values: 1-10 (10 = best)

2. Assign historical values to all 5 marshals (from CLAUDE.md Phase 2.2):
   - Ney: High Shock (9), low Defense (4)
   - Davout: Balanced excellence (8-9 across board)
   - Grouchy: Average (5 across board)
   - Wellington: High Defense (10), low Shock (4)
   - Blücher: High Shock (8), low Defense (5)

3. Integrate into combat:
   - Tactical → already used in dice rolls (keep working)
   - Shock → attacker damage bonus
   - Defense → defender damage reduction
   - Others → Phase 5 (add TODO comments)

**Files to modify:**
- `backend/models/marshal.py` - add skills dict
- `backend/data/marshals.py` - assign values to all marshals
- `backend/game_logic/combat.py` - integrate Shock and Defense
- `tests/test_marshal_skills.py` - new test file

**Success criteria:**
- All marshals have 6 skills
- Ney hits harder (high Shock)
- Wellington defends better (high Defense)
- Combat feels different for each marshal

---

## 📋 UPCOMING TASKS (Week 1)

**Day 5 (Jan 18):**
- [ ] Marshal abilities (1 signature ability per marshal)
  - Ney: "Bravest of the Brave" (+2 Shock when attacking)
  - Davout: "Iron Marshal" (ignores first morale penalty)
  - Wellington: "Reverse Slope" (+2 Defense in Hills/Forest)
  - Grouchy: "Literal Obedience" (never takes initiative)
  - Blücher: "Vorwärts!" (+1 pursuit damage)

**Days 6-7 (Jan 19-20):**
- [ ] Flanking mechanics (2+ marshals attacking = bonus)
- [ ] Morale system foundation (track 0-100 per marshal)

---

## 🎯 WEEK 2-4 PREVIEW

**Week 2:** Disobedience negotiation (THE core innovation)
**Week 3:** Order queue & delay (Grouchy moments)
**Week 4:** Rivalries & causality reports

---

## 📐 CRITICAL PATTERNS (ALWAYS FOLLOW)

### 1. Port 8005 (not 8000!)
```python
uvicorn.run(app, host="127.0.0.1", port=8005)
```

### 2. INT Wrapping for Godot
```python
# Godot expects integers, crashes on floats
return {
    "turn": int(self.current_turn),
    "gold": int(self.gold),
    "strength": int(marshal.strength),
    "skills": {k: int(v) for k, v in skills.items()}  # Skills too!
}
```

### 3. Unified Marshal Storage
```python
# Single dict for ALL marshals (player + enemy)
self.marshals = {}
self.marshals.update(create_starting_marshals())  # French
self.marshals.update(create_enemy_marshals())     # Coalition
```

### 4. Executor Pattern
```python
# ALL actions go through executor (player AND AI)
result = executor.execute(parsed_command, game_state)
# Never modify world_state directly from parser or routes
```

### 5. LLM Constraint (Phase 3+)
```python
# LLM selects from valid options, NEVER generates freely
valid_actions = rules.get_valid_actions(nation, game_state)
llm_choice = llm.select_action(valid_actions, personality)
result = executor.execute(llm_choice, game_state)
```

---

## 📚 WHERE TO FIND SPECIFICATIONS

**Full specs:** `/mnt/project/CLAUDE_UPDATED.md`
- Phase 2.1: Combat dice (lines 522-560)
- Phase 2.2: Marshal skills (lines 562-590)
- Phase 2.3: Disobedience (lines 592-776)
- Phase 2.4: Order delay (lines 778-976)
- Phase 2.5: Causality (lines 978-1110)

**Quick reference:** `/mnt/project/PROJECT_BRIEF_UPDATED.md`
**Design philosophy:** `/mnt/project/VISION_UPDATED.md`
**Feature interactions:** `/mnt/project/FEATURE_AUDIT_UPDATED.md`
**Changelog:** `/mnt/project/CHANGELOG.md`

---

## 🗂️ FILE STRUCTURE

```
backend/
  main.py                    # FastAPI server (PORT 8005!)
  
  data/
    marshals.py              # Marshal definitions with skills ← MODIFY FOR SKILLS
    regions.py               # Region definitions
  
  models/
    marshal.py               # Marshal class ← MODIFY FOR SKILLS
    world_state.py           # Central game state
  
  commands/
    parser.py                # NL → structured (has fuzzy matching)
    executor.py              # ALL game actions
  
  game_logic/
    combat.py                # Battle resolution ← MODIFY FOR SKILLS
    turn_manager.py          # Turn progression
  
  utils/
    fuzzy_matcher.py         # Typo tolerance (just added)
  
  ai/
    llm_client.py            # Mock LLM (Phase 3 = real LLM)

tests/
  test_combat_dice.py        # Dice system tests
  test_fuzzy_matching.py     # Fuzzy matching tests
  test_marshal_skills.py     # ← CREATE THIS for skills
```

---

## 🧪 TESTING CHECKLIST

After each implementation:

```bash
# Run specific tests
pytest tests/test_marshal_skills.py -v

# Run all tests (ensure nothing broke)
pytest tests/ -v

# Start backend
cd backend && python main.py

# Manual playtest in Godot:
# - Attack with different marshals (Ney, Davout, Wellington)
# - Check casualties reflect skills (Ney = high damage, Wellington = good defense)
# - Verify existing features still work
```

---

## 🎯 DESIGN PRINCIPLES

### The Golden Rule
> "LLMs explain, react, and color events - they don't cause them."

### Core Vision
- You command **people**, not pieces
- Orders pass through **personalities** who negotiate
- Losses are **YOUR fault**, not RNG
- Waterloo (1815) is practice, **1805 is the real game**

### LLM Philosophy (Phase 3+)
```
CORRECT: Rules → Valid Options → LLM Selects → Executor Runs
WRONG:   LLM generates actions freely
```

---

## 💡 COMMON ISSUES & SOLUTIONS

### Issue: Godot crashes with type error
**Solution:** Wrap ALL numbers in `int()` - Godot 4.3 is strict about types

### Issue: Tests fail after change
**Solution:** Check if you broke executor pattern or int wrapping

### Issue: Command not parsing
**Solution:** Check fuzzy_matcher.py - might need threshold adjustment

### Issue: Wrong marshal executes command
**Solution:** Check parser applies fuzzy match to BOTH marshal and target

---

## 📊 PROJECT METRICS

**Target:** Early Access May 2026 (17 weeks from MVP)

**Phase Timeline:**
- Phase 1: ✅ Complete (Foundation)
- Phase 2: 🚧 Week 1 of 4 (Combat, Skills, Disobedience)
- Phase 3: ⏳ Weeks 5-7 (LLM Integration, Advisors)
- Phase 4: ⏳ Weeks 8-10 (AI Nations, Coalition)
- Phase 5: ⏳ Weeks 11-13 (Supply, Stability, Vassals)
- Phase 6: ⏳ Weeks 14-17 (Polish, 1805 Map)

**Current Progress:** ~6% to EA (1 of 17 weeks)

---

## 🚀 IMMEDIATE NEXT STEP

**Run this prompt with Sonnet:**

```bash
claude-code "Implement 6-skill system for marshals per CLAUDE.md Phase 2.2.
[Full prompt provided by user]"
```

**Expected time:** 10-15 minutes
**Expected result:** All marshals differentiated by skills, combat shows differences

---

## 📝 NOTES FOR FUTURE SESSIONS

- Fuzzy matching "nearby suggestions" show "none" - polish in Phase 3
- Standing orders system (Week 3) will enable "Davout, take Brussels" → auto-pathing
- Autocomplete dropdown (Phase 3) will make 200+ regions manageable
- Real LLM integration starts Phase 3 (currently using mock mode)

---

**Last command executed:** Fuzzy matching implementation (successful with minor polish needed)
**Next command:** 6-skill system implementation
**Model to use:** Sonnet (straightforward implementation following clear spec)