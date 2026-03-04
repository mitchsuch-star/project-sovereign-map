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

---

## Implementation Notes
- Top bar changes require Godot `top_bar.gd` modifications
- Debug commands wire through `executor.py` `_execute_debug()` routing
- Estimated: ~2 hours implementation, ~8 tests
