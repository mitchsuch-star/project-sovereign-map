# Playtest Evaluation Prompt

> Copy this entire prompt into a new Claude conversation. The evaluator will play multiple games via curl commands against the running backend and provide a strategic/fun evaluation.

---

## PROMPT START

You are a game evaluator and strategist. Your job is to play the Napoleonic strategy game "Ink & Iron" by issuing curl commands to the backend API, try to WIN, and then write a detailed evaluation of the game's strategic depth, balance, and fun factor.

### How to Play

The backend runs at `http://127.0.0.1:8005`. You issue natural language commands via the `/command` endpoint. The game is turn-based — you get 4 military actions + 2 admin actions per turn, then end your turn. The enemy AI (Britain + Prussia) takes its turn automatically.

**Start a new game:**
```bash
curl -X POST http://127.0.0.1:8005/new_game
```

**Issue a command:**
```bash
curl -s -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Ney, attack Waterloo"}' | python -m json.tool
```

**Check status:**
```bash
curl -s http://127.0.0.1:8005/status | python -m json.tool
```

**End your turn:**
```bash
curl -s -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
```

**Handle popups (when response contains these flags):**
```bash
# Objection (marshal disagrees): choose trust/insist/compromise
curl -s -X POST http://127.0.0.1:8005/respond_to_objection \
  -H "Content-Type: application/json" \
  -d '{"choice": "insist"}' | python -m json.tool

# Capture choice (after taking a region): plunder or secure
curl -s -X POST http://127.0.0.1:8005/capture_choice \
  -H "Content-Type: application/json" \
  -d '{"choice": "secure"}' | python -m json.tool

# Glorious charge (Murat cavalry): charge or restrain
curl -s -X POST http://127.0.0.1:8005/respond_to_glorious_charge \
  -H "Content-Type: application/json" \
  -d '{"choice": "charge"}' | python -m json.tool
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
| **Ney** | Belgium | 72,000 | Aggressive | Cavalry, 2-tile attack range, shock master. Will object to defensive orders. |
| **Davout** | Paris | 48,000 | Cautious | Best tactician, defense genius. Will object to suicidal attacks. |
| **Grouchy** | Belgium | 33,000 | Literal | Follows orders exactly. Weakest stats but reliable. |

**Total French strength: 153,000**

### Enemy Forces

| Marshal | Location | Strength | Personality | Nation |
|---------|----------|----------|-------------|--------|
| **Wellington** | Waterloo | 68,000 | Cautious | Britain |
| **Uxbridge** | Waterloo | 18,000 | Aggressive | Britain (cavalry) |
| **Blucher** | Netherlands | 55,000 | Aggressive | Prussia |
| **Gneisenau** | Netherlands | 45,000 | Cautious | Prussia |

**Total Coalition strength: 186,000**

### Victory Conditions

- **Total Victory:** Control 12+ of 13 regions (any turn)
- **Timed Victory:** Control 10+ regions by turn 40
- **Defeat:** Lose Paris OR all marshals destroyed

### Key Mechanics to Exploit

1. **Terrain:** Hills +15% defense, Mountains +25%, Urban +20%, Forest +10%. Waterloo is hills — attacking there is costly.
2. **Fortification:** Marshals can fortify over multiple turns for stacking defense bonus. Davout is best at this.
3. **Stances:** Aggressive (+15% attack, -10% defense), Defensive (+15% defense, -10% attack), Neutral (no modifier).
4. **Supply attrition:** Regions have troop capacity. Overcrowding costs troops each turn. Home territory gets 1.5x capacity.
5. **Garrison:** Paris has 15,000 garrison troops. Must be reduced below 5,000 to capture. Regenerates +2,000/turn.
6. **Economy:** Gold from controlled regions. Recruit troops, build structures (fortifications, supply depots, markets, training grounds). Plundering gives immediate gold but damages the region.
7. **Drill:** Training troops gives +10-20% attack bonus for next battle (consumed on use).
8. **Fog of War:** You only see regions where you have marshals or recent scouts. Enemy movements in fogged regions are hidden.
9. **Strategic Orders:** Multi-turn orders (MOVE_TO, PURSUE, SUPPORT) cost 2 AP but execute automatically. Cancel costs 1 AP.
10. **Objections:** Marshals may refuse orders based on personality. Trust/Insist/Compromise affects trust score, which affects future cooperation.

### Available Commands

**Combat:** `Ney, attack Wellington` / `Ney, attack Waterloo` (region or marshal name)
**Move:** `Grouchy, move to Paris` / `Ney, march to Rhine`
**Defend:** `Davout, defend` / `Davout, hold position`
**Fortify:** `Davout, fortify` / `Davout, dig in`
**Drill:** `Ney, drill` / `Ney, train troops`
**Stance:** `Ney, aggressive stance` / `Davout, defensive stance`
**Scout:** `Grouchy, scout Rhine`
**Recruit:** `recruit for Ney` / `recruit in Paris`
**Retreat:** `Ney, retreat` / `Ney, fall back`
**Build:** `build fortification in Paris` / `build supply depot in Lyon`
**Repair:** `repair buildings in Belgium`
**Economy:** `economy` / `treasury`
**Strategic:** `Ney, pursue Wellington` / `Grouchy, march to Vienna`
**Cancel:** `cancel Ney's orders`
**End turn:** `end turn`

### Your Mission

**Play 1 full game trying to WIN.** Make strategic decisions, react to enemy moves, manage your marshals' personalities. Track what works and what doesn't.

After each turn, briefly note:
- What commands you issued and why
- What the enemy did
- Any surprises (objections, unexpected combat results, etc.)
- Your evolving strategy

**After the game ends (win or lose), write this evaluation:**

### Evaluation Template

**1. Game Result:** Win/Loss, turn count, final region control

**2. Dominant Strategy (Meta):**
- What strategy did you converge on? Was it the only viable approach?
- Did you find any broken/exploitable mechanics?
- Was turtling (defensive camping) optimal, or did aggression pay off?
- Rate strategy diversity: Could you win multiple different ways? (1-10)

**3. Balance Assessment:**
- Starting position fairness (France vs Coalition): Fair / Slight advantage / Major advantage
- Marshal balance: Are all 3 French marshals useful, or is one clearly best?
- Economy balance: Is gold meaningful? Too much? Too little?
- Was the AI a credible threat? Did it make smart moves?
- Any broken combos or degenerate strategies?

**4. Strategic Depth (1-10):**
- How many meaningful decisions per turn?
- Did terrain/stances/fortification matter?
- Did the personality system create interesting dilemmas?
- Was there room for creative play or was optimal play obvious?

**5. Fun Factor (1-10):**
- Was it engaging? Did you want to keep playing?
- Best moment (what was the most satisfying or dramatic moment)?
- Worst moment (what was frustrating or felt unfair)?
- Would you play again with a different strategy?

**6. Personality System Rating (1-10):**
- Did marshals feel like distinct characters?
- Were objections dramatic and interesting, or annoying?
- Did trust management feel meaningful?
- Did you ever WANT to trust a marshal's judgment?

**7. Pacing (1-10):**
- How did the game flow feel? Too slow? Too fast? Just right?
- Were there dead turns with nothing to do?
- Did the endgame feel climactic or anticlimactic?

**8. Top 3 Issues (most impactful problems):**
1. ...
2. ...
3. ...

**9. Top 3 Strengths (best things about the game):**
1. ...
2. ...
3. ...

**10. Specific Recommendations:**
- What one change would most improve the game?
- Any mechanics that should be cut or simplified?
- What's missing that would add the most value?

### Important Notes

- The game uses `LLM_MODE=mock` by default — the command parser is keyword-based, not AI-powered. Commands should be clear and direct.
- Check the response JSON carefully. Look for `pending_objection`, `pending_capture_choice`, `pending_glorious_charge` flags — you must respond to these before issuing new commands.
- The `action_summary` in each response tells you actions remaining, gold, controlled regions, and marshal status.
- The `enemy_phase` field in end_turn responses shows what the AI did (filtered by fog of war).
- If a command fails, read the error message — it usually tells you exactly what's wrong.
- Run `curl http://127.0.0.1:8005/status` periodically to get a full picture of the game state.

Good luck, Marshal. France expects every man to do his duty.

## PROMPT END
