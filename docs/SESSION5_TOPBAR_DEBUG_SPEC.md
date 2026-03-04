# Session 5: Top Bar & Debug Commands — Design Gate

> **Status:** AWAITING APPROVAL. Do not implement until approved.
> **Created:** March 4, 2026

---

## Top Bar Additions

### Vassal Count Indicator
- Position: After diplomacy DP indicator
- Format: `Vassals: 2` (or hidden if 0)
- Color: Normal=white, any loyalty<40=yellow, any loyalty<20=red

### Total Loyalty Average
- Position: Next to vassal count
- Format: `Avg Loyalty: 72`
- Color: >60=green, 40-60=yellow, <40=red

### Tribute Income Summary
- Position: In economy tooltip or ledger
- Format: `Tribute: +150g/turn`
- Shows sum of all vassal tribute contributions

### Continental System Status Icon
- Position: Next to trade income
- Format: Icon (ship with X) when active, hidden when inactive
- Tooltip: "Continental System active — N members, blocking Xg British trade"

### War Score Tracker
- Position: Top bar, grouped with diplomacy indicators
- Format: Per active war, e.g. `Prussia: +35` / `Austria: -12`
- Only shown for nations France is currently at WAR with
- Color: Positive (France winning)=green, 0=white, negative (France losing)=red
- Sign convention: positive = France advantage, negative = France losing
- Source: `world.war_scores` (sign-adjusted for France perspective via diplo_key ordering)
- Updates each turn automatically (war scores recalculated in advance_turn)
- Tooltip: "War score vs [Nation]. >50 enables harsh demands. <-30 risks vassal defection cascade."

---

## Debug Commands

### `debug vassal loyalty [nation] [value]`
- Sets vassal loyalty directly
- Example: `debug vassal loyalty Saxony 10`
- Validates: nation must be a current vassal

### `debug vassal create [nation]`
- Creates a SATELLITE vassal with loyalty=60
- Example: `debug vassal create Prussia`
- Sets diplomatic state to VASSAL, runs marshal assimilation

### `debug vassal rebellion [nation]`
- Forces immediate rebellion (sets loyalty=0, triggers check)
- Example: `debug vassal rebellion Saxony`

### `debug continental_system [add|remove] [nation]`
- Adds/removes a nation from Continental System
- Example: `debug continental_system add France`

### `debug war_score [nation] [value]`
- Sets war score for France vs nation directly
- Example: `debug war_score Prussia 85`
- Handles sign convention (stores raw in diplo_key order)

---

## Implementation Notes
- Top bar changes require Godot `top_bar.gd` modifications
- Debug commands wire through `executor.py` `_execute_debug()` routing
- Estimated: ~2 hours implementation, ~8 tests
