# Balance Patch Playtest Evaluation Prompt

> Copy this entire prompt into a new Claude conversation. Start the backend first: `".venv\Scripts\python.exe" backend/main.py` from the project root.

---

## PROMPT START

You are a game evaluator and strategist. Your job is to play the Napoleonic strategy game "Ink & Iron" by issuing curl commands to the backend API, try to WIN using **multiple different strategies across 3 games**, and then write a detailed evaluation focusing on whether the balance patch fixed the known issues.

### How to Play

The backend runs at `http://127.0.0.1:8005`. You issue natural language commands via the `/command` endpoint. You get 4 military actions + 2 admin actions per turn, then end your turn. The enemy AI (Britain + Prussia) takes its turn automatically.

```bash
# Start a new game
curl -s -X POST http://127.0.0.1:8005/new_game | python -m json.tool

# Issue a command
curl -s -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Ney, attack Waterloo"}' | python -m json.tool

# Check status
curl -s http://127.0.0.1:8005/status | python -m json.tool

# End your turn
curl -s -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool

# Handle popups (check response for these flags):
# Objection: choose trust/insist/compromise
curl -s -X POST http://127.0.0.1:8005/respond_to_objection \
  -H "Content-Type: application/json" \
  -d '{"choice": "insist"}' | python -m json.tool

# Capture choice: plunder or secure
curl -s -X POST http://127.0.0.1:8005/capture_choice \
  -H "Content-Type: application/json" \
  -d '{"choice": "secure"}' | python -m json.tool
```

### The Map (13 regions)

```
                 Netherlands (Britain, rural, plains)
                      |
Paris ---- Belgium ---- Rhine ---- Bavaria ---- Vienna
(FR,cap)   (FR,town)   (PR,town)  (PR,town)    (PR,major)
  |    \      |
  |   Waterloo (BR,rural,hills)
  |
Brittany ---- Bordeaux ---- Geneva ---- Milan (BR,city,urban)
(FR,rural)    (FR,rural)   (BR,town)     |
                              |         Vienna
                           Marseille
                           (FR,city)

Lyon (FR,major) connects to: Paris, Rhine, Bavaria, Marseille, Milan
```

**Starting control:** France 6 regions (Paris, Belgium, Lyon, Brittany, Bordeaux, Marseille), Britain 4 (Waterloo, Netherlands, Milan, Geneva), Prussia 3 (Rhine, Bavaria, Vienna).

### Your Forces (France)

| Marshal | Location | Strength | Personality | Notes |
|---------|----------|----------|-------------|-------|
| **Ney** | Belgium | 72,000 | Aggressive | Cavalry, 2-tile attack range, shock master |
| **Davout** | Paris | 48,000 | Cautious | Best tactician, counter-punch defense master |
| **Grouchy** | Belgium | 28,000 | Literal | Follows orders exactly. Reliable but weak |
| **Drouot** | Paris | 25,000 | Cautious | Artillery. Cannot attack after moving. 2x fort degradation |

**Total French: 173,000 | Starting gold: 800 | Net income: ~-15g/turn (break-even with admin bonus)**

### Enemy Forces

| Marshal | Location | Strength | Personality | Nation |
|---------|----------|----------|-------------|--------|
| **Wellington** | Waterloo | 52,000 | Cautious | Britain (hills defense + reverse slope) |
| **Uxbridge** | Waterloo | 18,000 | Aggressive | Britain (cavalry, pursuit master) |
| **Blucher** | Netherlands | 55,000 | Aggressive | Prussia |
| **Gneisenau** | Netherlands | 45,000 | Cautious | Prussia |
| **PrinceAugust** | Netherlands | 20,000 | Cautious | Prussia (artillery) |

**Total Coalition: 190,000**

### Key Mechanics

1. **Terrain:** Hills +15% def, Mountains +25%, Urban +20%, Forest +10%.
2. **Supply attrition:** Regions have troop capacity. Overcrowding costs troops each turn (continuous formula, max 3%). Home territory gets 1.5x capacity. Belgium (town) = 25k base, 37.5k home.
3. **Economy:** 5g upkeep per 1000 troops. Gold from controlled regions (modified by stability). Captured regions start at 25 stability (0% income), grow +5/turn (+5 if marshal present).
4. **Stances:** Aggressive (+15% atk, -10% def), Defensive (+15% def, -10% atk), Neutral.
5. **Fortification:** Stacking defense bonus over turns. Only works in Defensive stance.
6. **Drill:** +10-20% attack bonus for next battle (consumed on use).
7. **Garrison:** Paris has 15k garrison. Must reduce below 5k to capture. Regens +2k/turn.
8. **Strategic Orders:** MOVE_TO, PURSUE, SUPPORT cost 2 AP but auto-execute. Cancel costs 1 AP.
9. **Objections:** Marshals may refuse orders. Trust/Insist/Compromise affects trust score.
10. **AI homeland defense:** The AI now tracks lost territory and redirects marshals to recapture it.

### Available Commands

`Ney, attack Wellington` | `Grouchy, move to Paris` | `Davout, fortify` | `Ney, drill` | `Ney, aggressive stance` | `Davout, stance defensive` | `Grouchy, scout Rhine` | `recruit for Ney` | `build fortification in Paris` | `economy` | `Ney, pursue Wellington` | `cancel Ney's orders` | `end turn`

---

## YOUR MISSION: 3 Games, 3 Strategies

Play 3 games with deliberately different strategies to test the balance patch:

### Game 1: Aggressive Opening
Attack Waterloo early with Ney+Grouchy. Try to break Wellington. Test if Wellington at 52k is beatable.

### Game 2: Southern Bypass
Abandon Belgium, rush south through Lyon→Rhine→Bavaria→Vienna capturing undefended territory. This was the ONLY viable strategy before the patch. **Test if the AI now defends its rear territory.**

### Game 3: Defensive/Economic
Fortify Paris with Davout, build economy, recruit, then counter-attack when strong. Test if France's economy can sustain a longer game.

For each game, after each turn note:
- Commands issued and why
- What the enemy did (especially: did it defend rear territory? Did it split forces?)
- Supply attrition amounts (are they reasonable?)
- Economy status (is France surviving?)

---

## BALANCE PATCH EVALUATION (write this after all 3 games)

The previous playtest found these issues. **For each one, rate whether the patch fixed it:**

### Issue 1: AI Never Defends Rear Territory
**Before:** Player captures 5 enemy regions completely unopposed. AI deathball sits in Belgium forever.
**Test:** In Game 2 (Southern Bypass), does the AI send marshals to recapture lost regions?
**Rating:** Fixed / Partially Fixed / Not Fixed
**Details:** [What happened]

### Issue 2: Supply Attrition Too Punishing
**Before:** 5% attrition killed 5,250 troops/turn at Belgium. Both sides lost more to attrition than combat.
**Test:** What attrition numbers do you see? Is it still punishing enough to encourage dispersal without being dominant?
**Rating:** Fixed / Partially Fixed / Not Fixed / Over-Corrected
**Details:** [Actual numbers observed]

### Issue 3: Wellington Unkillable
**Before:** 68k Wellington with hills+cautious+reverse slope survived three consecutive combined-arms attacks.
**Test:** In Game 1, can Ney + allies break Wellington with a focused assault?
**Rating:** Fixed / Partially Fixed / Not Fixed / Over-Corrected
**Details:** [Combat results]

### Issue 4: French Economy Death Spiral
**Before:** France starts at -40g/turn. Paris stability crashes from enemy attacks. Bankruptcy by turn 5-7.
**Test:** In Game 3, can France sustain itself economically for 15+ turns?
**Rating:** Fixed / Partially Fixed / Not Fixed / Over-Corrected
**Details:** [Economy numbers each turn]

### Issue 5: Only One Viable Strategy
**Before:** Southern Bypass was the only strategy that worked. All others led to death spirals.
**Test:** Did all 3 strategies feel viable? Or did you converge on one?
**Rating:** Fixed / Partially Fixed / Not Fixed
**Details:** [Which strategies worked]

### Issue 6: AI Deathball Never Splits
**Before:** Prussian 3-marshal stack (120k) captured Belgium turn 1 and sat there for the entire game.
**Test:** Does the AI ever split its forces? Send marshals to different objectives?
**Rating:** Fixed / Partially Fixed / Not Fixed
**Details:** [Observed AI behavior]

### Overall Balance Rating (1-10):
### Strategy Diversity Rating (1-10):
### AI Intelligence Rating (1-10):
### Fun Factor Rating (1-10):

### New Issues Found:
[List anything broken or unbalanced that the patch introduced]

### Remaining Issues:
[List anything from the old patch that's still not fixed]

### Top Recommendation:
[Single most impactful change still needed]

---

### Important Notes

- Commands use keyword matching (not AI). Be clear and direct.
- Check response JSON for `pending_objection`, `pending_capture_choice` flags — respond before issuing new commands.
- The `action_summary` in responses shows actions remaining, gold, regions, marshal status.
- The `enemy_phase` in end_turn responses shows AI actions (fog-filtered).
- Run `curl http://127.0.0.1:8005/status` between turns for full state.
- If a command fails, read the error — it tells you what's wrong.
- The AI gets 4 military actions + 2 admin actions per turn (same as you).

Good luck, Marshal. France expects every man to do his duty.

## PROMPT END
