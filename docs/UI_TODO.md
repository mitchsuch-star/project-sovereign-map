# UI TODO - Enemy Phase Popup

## Status: IMPLEMENTED (January 2025)

Files created:
- `godot-client/project-sovereign/scenes/enemy_phase_dialog.tscn`
- `godot-client/project-sovereign/scripts/enemy_phase_dialog.gd`
- Updated `main.gd` to show popup after end_turn

Backend fix: `main.py` now passes `enemy_phase` data to frontend.

---

## Problem (RESOLVED)

Currently the enemy phase is displayed as a cramped summary in the command log:
```
"Britain (4 actions): stance_change, fortify, defend, defend"
"Prussia (4 actions): stance_change, attack, attack, attack"
```

Issues:
1. **Missing Details** - Attacks show no battle info (who attacked, casualties, who won)
2. **Wrong Location** - Cramming into command log is bad UX, easy to miss

## Solution: Enemy Turn Popup

Modal/popup that appears at start of player's turn showing what happened during enemy phase.
Player dismisses to continue.

### Content Format

```
═══════════════════════════════════════════════
              ENEMY PHASE - Turn 2
═══════════════════════════════════════════════

BRITAIN
───────
- Wellington changes to DEFENSIVE stance
- Wellington fortifies at Waterloo (+2% defense)
- Wellington defends
- Wellington defends

PRUSSIA
───────
- Blucher changes to AGGRESSIVE stance
- Blucher attacks Ney at Belgium!
  - Battle of Belgium (1st Engagement)
  - Blucher: 45,000 vs Ney: 72,000
  - Result: Ney victory
  - Casualties: Blucher 5,200, Ney 3,100
  - Blucher retreats to Netherlands

- Blucher is in retreat recovery (2 turns remaining)

═══════════════════════════════════════════════
           [Click or press SPACE to continue]
═══════════════════════════════════════════════
```

## Implementation

### Backend Status: VERIFIED ✓
The backend returns full battle details in `response.enemy_phase.nations[nation].actions[]`:

**Fixed January 2025:** `main.py` was not passing `enemy_phase` to frontend - now fixed.
- Each action has `ai_action` (marshal, action, target)
- Battle results include full `events` array with:
  - `attacker.name`, `attacker.casualties`, `attacker.remaining`, `attacker.morale`
  - `defender.name`, `defender.casualties`, `defender.remaining`, `defender.morale`
  - `outcome`, `victor`, `enemy_destroyed`, `region_conquered`

### Godot Tasks

1. **Create popup scene** (`enemy_phase_popup.tscn`)
   - Modal panel with RichTextLabel for formatted content
   - Close button + keyboard dismiss (SPACE/ENTER/ESCAPE)
   - Semi-transparent background overlay

2. **Parse enemy_phase data** in `main.gd`
   - Check if `response.enemy_phase` exists after end_turn
   - Format each nation's actions with full details
   - Extract battle events and format casualties/results

3. **Show popup** before player can act
   - Block input until dismissed
   - Trigger after end_turn response received

4. **Dismiss handling**
   - Click anywhere / press SPACE/ENTER/ESCAPE to close
   - Re-enable player input after close

## Future Enhancements

```gdscript
# TODO: Option to auto-skip enemy popup (for experienced players)
#       Settings toggle: "Show enemy phase details" [ON/OFF]
#       If OFF, just show brief summary in log as now

# TODO: Animation/dramatic reveal (future polish)
#       - Typewriter effect for text
#       - Battle results flash/highlight
#       - Sound effects for attacks/victories

# TODO: Espionage system controls what player sees in popup
#       - Without spies: "Prussia took 4 actions" (no details)
#       - With spies in region: Full battle details for that region
#       - Spy network: See all enemy actions
#       - Could show "???" for unknown info
```

## Data Flow

```
Player: "end turn"
    │
    ▼
Backend: turn_manager.end_turn()
    │
    ├─► _process_enemy_turns()
    │       └─► Returns enemy_phase dict with full details
    │
    ▼
Response to Godot includes:
{
    "enemy_phase": {
        "nations": {
            "Prussia": {
                "actions": [
                    {
                        "success": true,
                        "message": "Blucher attacks Ney...",
                        "events": [{
                            "type": "battle",
                            "attacker": {
                                "name": "Blucher",
                                "casualties": 9021,
                                "remaining": 35979,
                                "morale": 85,
                                "forced_retreat": false
                            },
                            "defender": {
                                "name": "Ney",
                                "casualties": 13535,
                                "remaining": 58465,
                                "morale": 75,
                                "forced_retreat": false
                            },
                            "outcome": "attacker_tactical_victory",
                            "victor": "Blucher",
                            "region_conquered": false
                        }],
                        "ai_action": {"marshal": "Blucher", "action": "attack", "target": "Ney"}
                    },
                    ...
                ],
                "action_count": 4
            }
        },
        "total_actions": 8,
        "summary": ["Britain (4 actions): ...", "Prussia (4 actions): ..."]
    }
}
    │
    ▼
Godot: main.gd receives response
    │
    ├─► Check if enemy_phase exists
    ├─► Format popup content from enemy_phase.nations
    ├─► Show enemy_phase_popup
    ├─► Block input
    │
    ▼
Player dismisses popup
    │
    ▼
Enable input, continue playing
```

---

*Last updated: January 2025*
