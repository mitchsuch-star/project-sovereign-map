# Top Bar & Information Screens Spec

> **Authored:** February 21, 2026
> **Status:** APPROVED — ready for implementation
> **Sessions:** 2 (A: Top Bar Framework + Dispatch, B: Strategic Ledger)

---

## Overview

Unified top bar UI framework replacing scattered hotkeys and overlays. The top bar is the main UI shell for all information screens going forward. Architecture decisions are final — reviewed by Opus, all edge cases addressed.

```
[Event Log] [Ledger] [Generals] [Dispatch]          [!][★][!]  Turn 5
 ^^^ bar buttons ^^^                                 ^^^ notifications ^^^
```

---

## Architecture (FINAL — do not deviate)

### Top bar is a CONTROLLER, not a container

`top_bar.gd` is its own CanvasLayer (layer 75) with a row of buttons + notification icons + turn counter. Screens are INDEPENDENT CanvasLayers (layer 50) that top_bar tracks and tells to show/hide. This minimizes refactoring — each screen owns its own scene tree, rendering, and data fetching.

### Layer ordering

| Layer | Contents |
|-------|----------|
| Base  | Map (Control node, no CanvasLayer) |
| 50    | All information screens (Event Log, Ledger, Generals, Dispatch) |
| 75    | Top bar + notification expanded detail panel |
| 90    | Modal dialogs (objections, glorious charge, enemy phase, capture choice, etc.) |
| 101   | Pause menu (unchanged) |

Campaign log drops from layer 102 to layer 50. Top bar is always visible — dimmed by pause menu overlay, NOT hidden (matches EU4/CK3 pattern where the top bar persists behind the pause overlay).

### Hotkeys

| Key | Action | Notes |
|-----|--------|-------|
| L   | Event Log | Existing, rewired through top_bar |
| T   | Ledger | New — NOT Tab (Tab already toggles terminal minimize) |
| G   | Generals | Placeholder — screen built in future session |
| D   | Dispatch re-read | New |
| Esc | Close any open screen first, THEN pause menu on second press | Existing Smart Esc pattern extended |

### Screen behavior

- **ONE screen at a time.** Opening a new screen closes the current one.
- **Click active button = toggle off** (close screen).
- **All screens close on turn transition** (avoid stale data).
- **Each screen owns its own data fetching.** Top bar calls `screen.open(api_client)`, screen calls API.
- **Terminal input STAYS ACTIVE** while screens are open. Map interaction is blocked.

---

## Session A: Top Bar Framework + Dispatch Re-read

### Task 1: top_bar.gd + top_bar.tscn

**Scene structure:**

```
TopBar (CanvasLayer, layer 75)
  └── BarContainer (HBoxContainer, anchored top, full width)
      ├── ScreenButtons (HBoxContainer, left-aligned)
      │   ├── EventLogBtn (Button: "Event Log")
      │   ├── LedgerBtn (Button: "Ledger")
      │   ├── GeneralsBtn (Button: "Generals") [disabled until future session]
      │   └── DispatchBtn (Button: "Dispatch")
      ├── Spacer (Control, h_size_flags EXPAND)
      └── RightSection (HBoxContainer, right-aligned)
          ├── NotificationArea (Container — notification_bar repositioned here)
          └── TurnLabel (Label: "Turn 5")
```

**State tracking:**

```gdscript
var active_screen: String = ""  # "" = none, "event_log", "ledger", "generals", "dispatch"
var screens: Dictionary = {}    # maps screen name to node reference

func register_screen(name: String, node: Node)  # called during setup
func toggle_screen(name: String)                 # close if open, open if closed (closing current first)
func close_all_screens()                         # called on turn transition
func is_screen_open() -> bool                    # for main.gd dialog guard
func get_active_screen() -> String               # for button highlighting
func update_turn(turn_number: int)               # updates TurnLabel
```

**Button highlighting:** Active screen's button gets a distinct style (pressed/toggled look via StyleBoxFlat override). All other buttons use normal style.

**Turn counter:** Updated via `update_turn()` on every backend response. Shows "Turn {N}".

**Signal:** `screen_changed(screen_name: String)` — emitted on open/close. main.gd listens to update map blocking.

### Task 2: Campaign Log Refactor

Minimal changes to integrate into top bar:

1. Change CanvasLayer layer from 102 to 50 in `campaign_log.tscn`
2. Remove standalone `$LogButton` from `main.tscn` and its `_on_log_button_pressed()` handler in `main.gd`
3. L key in `main.gd _unhandled_input` now calls `top_bar.toggle_screen("event_log")` instead of directly opening campaign_log
4. Campaign log registers itself with top_bar during setup: `top_bar.register_screen("event_log", campaign_log_node)`
5. The log's `open_log(api_client)` method still calls `api_client.get_campaign_log()` as today — no change to data fetching
6. Remove the wholesale `_unhandled_input` consumption from campaign_log path in main.gd (lines 444-449) — input blocking is now handled by main.gd checking `top_bar.is_screen_open()` with the new blocking pattern
7. Campaign log's `close_log()` still emits `closed` signal — top_bar listens to know when screen was closed via X button or overlay click (in addition to bar button toggle)

### Task 3: Dispatch Re-read Screen

**Backend changes:**

1. Store last built dispatch on WorldState: `world.last_morning_dispatch = dispatch_dict` in `build_morning_dispatch()` (dispatch.py)
2. Serialize `last_morning_dispatch` in WorldState `to_dict()` / `from_dict()` (with `.get('last_morning_dispatch', {})` default)
3. New endpoint: `GET /dispatch` — returns `world.last_morning_dispatch` or `{"success": true, "dispatch": {}}` if not yet built (turn 0)
4. Update `docs/SAVE_FORMAT_REFERENCE.md` with new field

**Godot scene:** `dispatch_view.gd` + `dispatch_view.tscn`

- CanvasLayer at layer 50
- BackgroundOverlay (click-to-close, same pattern as campaign_log)
- PanelContainer centered, scrollable
- Renders dispatch with the same BBCode formatting as `_display_morning_dispatch()` in main.gd
- Formatting approach: extract shared dispatch rendering into a helper function, OR duplicate the formatting (dispatch format is stable — duplication is acceptable)
- Shows "No dispatch available yet." on turn 0 / empty dispatch
- D key or Dispatch button → top_bar.toggle_screen("dispatch") → dispatch_view.open(api_client) → fetches GET /dispatch → renders
- Read-only, no interaction besides scrolling
- Registers with top_bar as "dispatch"

### Task 4: Notification Bar Repositioning

Move notification icons into the top bar's right section. Two approaches — choose whichever is less disruptive:

**(a) Reparent:** notification_bar becomes a child of TopBar's RightSection/NotificationArea. Adjust positioning code. Expanded detail panel still drops down from notification_bar, now rendering at layer 75 (top bar's layer) — above screens at layer 50.

**(b) Relative positioning:** Keep notification_bar as its own node but set its position relative to the top bar's RightSection. Less refactoring but more fragile if bar layout changes.

Either way:
- Expanded detail panel must render ABOVE screens (layer 75, same as top bar)
- Remove `offset_top = 48.0` from notification_bar.tscn (was below the old LOG button which is being removed)
- Verify expanded panel doesn't get clipped behind screen content at layer 50
- Notification functionality unchanged — same dismiss API, same priority colors, same icon buttons

### Task 5: Generals Placeholder

- Add "Generals" button to top bar ScreenButtons HBoxContainer
- Button is disabled (greyed out, `disabled = true`)
- G hotkey wired but does nothing while button is disabled (guard: `if screens.has("generals") and screens["generals"] != null`)
- This gets built in a future session — just wire the button and hotkey so the framework is ready

### Task 6: Input Refactor in main.gd

**Split dialog detection:**

Replace `_is_any_dialog_open()` with three functions:

```gdscript
func _is_modal_dialog_open() -> bool:
    """True when a modal dialog requiring player choice is visible."""
    # objection, redemption, enemy_phase, glorious_charge,
    # capture_choice, load_dialog, strategic_report, interrupt, clarification
    # These block EVERYTHING

func _is_screen_open() -> bool:
    """True when a top bar screen is open. Blocks map, allows terminal."""
    return top_bar != null and top_bar.is_screen_open()

func _is_hotkey_blocked() -> bool:
    """True when hotkeys should not fire."""
    return command_input.has_focus() or _is_modal_dialog_open()
```

**Input blocking while a screen is open (NOT a modal dialog):**

- Set `map_area.mouse_filter = Control.MOUSE_FILTER_IGNORE` when screen opens (block map clicks/hover)
- Restore `map_area.mouse_filter = Control.MOUSE_FILTER_STOP` when screen closes
- Block map hotkeys: arrow keys (panning), E (end turn) — guard with `_is_screen_open()`
- Allow terminal input: player can type commands and submit while reading any screen
- Screen hotkeys (L, T, G, D) still work for switching between screens — guard with `_is_hotkey_blocked()` only (not `_is_screen_open()`)
- Connect to top_bar's `screen_changed` signal to toggle map mouse filter

**All hotkey guards use `_is_hotkey_blocked()`:**

```gdscript
# In _unhandled_input:
if event.keycode == KEY_L:
    if not _is_hotkey_blocked():
        top_bar.toggle_screen("event_log")
        get_viewport().set_input_as_handled()
```

**Close all screens on turn transition:**

In `_display_turn_change()` or wherever turn advancement is processed in main.gd, call `top_bar.close_all_screens()`.

**Esc key updated Smart Esc:**

```
Priority order:
1. If command_input focused → release_focus (existing, unchanged)
2. If any screen open → close_all_screens via top_bar
3. If pause menu open → close pause menu
4. If modal dialog open → do nothing (modals handle their own Esc)
5. If nothing open → open pause menu
```

### Session A Tests

Backend only (~5 tests in `tests/test_dispatch_view.py`):

- `last_morning_dispatch` stored on WorldState after `build_morning_dispatch()`
- `last_morning_dispatch` serialization roundtrip (to_dict → from_dict)
- `GET /dispatch` returns stored dispatch
- `GET /dispatch` returns empty dict when no dispatch built yet
- No-float enforcement on dispatch endpoint response

No Godot unit tests — UI is smoke tested manually per `docs/MANUAL_TEST_PLAN.md`.

---

## Session B: Strategic Ledger

### Backend: ledger.py

`build_strategic_ledger(world) -> dict` with 5 sections:

#### "forces" — per player marshal

```python
{
    "name": str,
    "type": str,           # "infantry" / "cavalry" / "artillery"
    "personality": str,     # e.g. "aggressive"
    "location": str,
    "strength": int,
    "morale": int,
    "trust": int,
    "stance": str,          # "aggressive" / "neutral" / "defensive"
    "status": str,          # derived, priority: broken > retreating > drilling > fortified
                            #   > holding > pursuing > moving_to > supporting > idle
    "strategic_order": str, # "MOVE_TO Brussels (2 turns left)" or "None"
    "battles_won": int,
    "battles_lost": int,
    "special_flags": {
        "shock_ready": bool,
        "counter_punch": bool,
        "reckless": int,        # recklessness level (0 if not reckless)
        "exhausted": bool,
    }
}
```

Status derivation priority (highest wins):
1. `broken` → "broken"
2. `retreating` → "retreating"
3. `drilling or drilling_locked` → "drilling"
4. `fortified` → "fortified"
5. `in_strategic_mode and command_type == "HOLD"` → "holding"
6. `in_strategic_mode and command_type == "PURSUE"` → "pursuing"
7. `in_strategic_mode and command_type == "MOVE_TO"` → "moving_to"
8. `in_strategic_mode and command_type == "SUPPORT"` → "supporting"
9. default → "idle"

#### "territories" — per player-controlled region

```python
{
    "name": str,
    "terrain": str,
    "region_type": str,         # "capital" / "major_city" / "city" / "town" / "rural"
    "buildings": [              # list of dicts
        {"name": str, "status": str}  # status: "built" / "constructing (2t)" / "damaged"
    ],
    "garrison": int,            # garrison_strength, 0 if none
    "supply_capacity": int,
    "occupant_count": int,      # number of marshals in this region
    "supply_status": str,       # "OK" / "Strained" / "Over capacity"
    "stability": int,
    "war_damage": int,
    "income": int,              # effective_income (after stability/damage)
    "fortification_level": int, # region fort_level as percentage (0-100)
}
```

Supply status derivation:
- Total strength of all marshals in region vs region supply_capacity
- `<= capacity` → "OK"
- `<= capacity * 1.5` → "Strained"
- `> capacity * 1.5` → "Over capacity"

#### "economy" — single dict

```python
{
    "treasury": int,
    "income": int,
    "upkeep": int,
    "net": int,                 # income - upkeep
    "bankruptcy_turns": int,
    "construction_queue": [     # list of active constructions
        {"region": str, "building": str, "turns_remaining": int}
    ],
    "income_breakdown": [       # per-region income detail
        {"region": str, "income": int, "type": str}  # type = region_type
    ]
}
```

#### "intel" — dict

```python
{
    "known_enemies": [          # fog-filtered enemy sightings
        {
            "name": str,
            "nation": str,
            "location": str,
            "strength_display": str,   # exact "45,000" or band "large force" or "last seen: 30,000"
            "visibility": str,         # "full" / "partial" / "stale" / "last_known"
        }
    ],
    "nation_summaries": [       # per-enemy-nation aggregated intel
        {
            "nation": str,
            "known_marshals": int,
            "estimated_strength": int,
            "regions_controlled": int,
        }
    ],
    "unknown_region_count": int,  # regions at UNKNOWN visibility
}
```

Fog filtering: reuse existing `get_region_intel()`. FULL = exact strength, PARTIAL = band string, STALE = "last seen: {frozen strength}", LAST_KNOWN = location only (strength_display = "unknown"), UNKNOWN = not included in known_enemies.

Nation summaries aggregate from known_enemies: count marshals per nation, sum estimated strength (using BAND_MIDPOINTS from dispatch.py for non-exact), count regions controlled by each enemy nation.

#### "manpower" — dict

```python
{
    "infantry": {
        "current": int,
        "max": int,
        "regen_rate": int,
        "recruit_cost": int,        # gold cost per batch
        "recruit_amount": int,      # troops per batch
        "turns_until_full": int,    # 0 if at max, else ceil((max - current) / regen_rate)
    },
    "cavalry": { ... same fields ... },
    "artillery": { ... same fields ... },
}
```

**All values `int()` wrapped. No floats to Godot.**

### Backend: endpoint

`GET /ledger` in main.py:
- Calls `build_strategic_ledger(world)`
- Returns `{"success": true, "ledger": <dict>}`
- Guards: `if not game_state.get("world")` → 400

### Godot: strategic_ledger.gd + strategic_ledger.tscn

CanvasLayer at layer 50.

**Scene structure:**

```
StrategicLedger (CanvasLayer, layer 50)
  └── BackgroundOverlay (ColorRect, click-to-close)
  └── PanelContainer (centered, styled same as campaign_log)
      └── VBoxContainer
          ├── HeaderRow (HBoxContainer)
          │   ├── TitleLabel ("STRATEGIC LEDGER")
          │   └── CloseButton ("X")
          ├── SubTabRow (HBoxContainer)
          │   ├── ForcesTab (Button: "FORCES")
          │   ├── TerritoriesTab (Button: "TERRITORIES")
          │   ├── EconomyTab (Button: "ECONOMY")
          │   ├── IntelTab (Button: "INTELLIGENCE")
          │   └── ManpowerTab (Button: "MANPOWER")
          ├── HSeparator
          └── ScrollContainer
              └── ContentArea (VBoxContainer — populated per sub-tab)
```

**Sub-tab switching:**
- Number keys 1-5 switch sub-tabs (only while ledger is open — guard with `top_bar.get_active_screen() == "ledger"`)
- Clicking sub-tab buttons also switches
- Default sub-tab: FORCES
- Active sub-tab button gets highlight style (same pattern as top bar active button)

**Content rendering per sub-tab:**

Each sub-tab clears ContentArea and populates with RichTextLabel or Label nodes.

**Color coding rules:**
- broken / retreating → red text
- drilling → blue text
- idle → grey text
- Supply "Over capacity" → red
- Supply "Strained" → orange
- Bankruptcy turns > 0 → red
- Pool depleted (current = 0) → red
- Pool low (current < recruit_amount) → orange
- Trust < 30 → red text
- Morale < 40 → red text
- Trust < 55 or Morale < 60 → orange text

**Data fetching:** `open(api_client)` fetches `GET /ledger`, caches while open. Registers with top_bar as "ledger".

### Session B Tests

~40 tests in `tests/test_ledger.py`:

**build_strategic_ledger():**
- All 5 sections present and non-null
- Empty state (new game, no buildings, no intel)

**Forces section:**
- Status priority derivation: broken beats retreating
- Status priority derivation: retreating beats drilling
- Status priority derivation: drilling beats fortified
- Status priority derivation: strategic modes (hold/pursue/move_to/support)
- Status priority derivation: idle as default
- Special flags: shock_ready from shock_bonus > 0
- Special flags: counter_punch from counter_punch_available
- Special flags: reckless level from recklessness
- Strategic order summary string formatting
- Type detection: cavalry, artillery, infantry

**Territories section:**
- Supply status: OK when under capacity
- Supply status: Strained when between 1x and 1.5x
- Supply status: Over capacity when above 1.5x
- Building construction display: "constructing (Nt)" format
- Building damaged status
- Garrison strength included
- Fortification level as percentage
- Occupant count matches marshals in region

**Economy section:**
- Net = income - upkeep
- Bankruptcy turns included when > 0
- Construction queue lists active builds with turns remaining
- Income breakdown per region

**Intel section:**
- UNKNOWN regions excluded from known_enemies
- FULL visibility shows exact strength
- PARTIAL visibility shows band string
- STALE visibility shows "last seen: N"
- LAST_KNOWN shows "unknown" strength
- Nation summary: marshal count aggregation
- Nation summary: estimated strength from bands
- Unknown region count

**Manpower section:**
- turns_until_full calculation (0 when at max)
- turns_until_full calculation (correct ceiling division)
- All three pool types present

**Cross-cutting:**
- No-float enforcement on all values (recursive int check)
- GET /ledger endpoint returns valid response structure
- GET /ledger returns 400 when no world state

---

## Input Blocking Summary

Three blocking levels in main.gd:

| State | Map clicks | Map hotkeys (arrows, E) | Screen hotkeys (L,T,G,D) | Terminal input | Esc |
|-------|-----------|------------------------|--------------------------|---------------|-----|
| Nothing open | Yes | Yes | Yes | Yes | Opens pause |
| Screen open | **Blocked** | **Blocked** | Yes (switches) | **Yes** | Closes screen |
| Pause menu open | Blocked | Blocked | Blocked | Blocked | Closes pause |
| Modal dialog open | Blocked | Blocked | Blocked | Blocked | Dialog handles |

---

## What NOT to Build

- No column sorting in ledger (defer)
- No cross-screen navigation (Ledger marshal click → Generals, defer to 1805)
- No "Issue Order" button in Generals (not built yet)
- No screen animations/transitions
- No notification sound
- No real-time screen refresh (close all on turn change is sufficient)
- No Generals screen content (placeholder only)

---

## Edge Cases Addressed

1. **Rapid toggle during async fetch:** If player toggles screen off while data is loading, callback guard checks visibility before populating. Campaign log already has this pattern (shows "Loading..." then populates) — dispatch_view follows same approach.

2. **Screen open + end turn:** All screens close on turn transition via `top_bar.close_all_screens()`. Morning Dispatch renders in terminal as usual.

3. **Screen open + modal dialog:** Modal dialogs are at layer 90, screens at layer 50. Dialog appears on top. Screen stays open underneath. When dialog is dismissed, screen is still there. `_is_modal_dialog_open()` is checked separately from `_is_screen_open()`.

4. **Notification panel + screen overlap:** Notification expanded panel renders at layer 75 (top bar layer), above screens at layer 50. No visual overlap issues.

5. **D/G/T hotkeys while typing:** All guarded by `_is_hotkey_blocked()` which checks `command_input.has_focus()`.

6. **Pause menu + top bar:** Top bar stays visible but dimmed by pause overlay (75% opacity ColorRect at layer 101). Turn counter and notifications remain visible-but-dimmed. Matches EU4/CK3 pattern.

7. **Tab key unchanged:** Tab still toggles terminal minimize/restore. NOT reassigned to Ledger. T is Ledger.

---

## Doc Updates After Implementation

| Doc | Update |
|-----|--------|
| `CLAUDE.md` | Add `top_bar.gd`, `dispatch_view.gd`, `strategic_ledger.gd`, `ledger.py` to file reference tables. Update Phase 6.5 completed list. Add top_bar to "Before Modifying" table. |
| `STATUS.md` | New session entries with test counts |
| `ROADMAP.md` | Mark Strategic Ledger as COMPLETE, mark Top Bar + Dispatch as COMPLETE, update Phase 6.5 status |
| `SAVE_FORMAT_REFERENCE.md` | Add `last_morning_dispatch` field to WorldState |
| `SYSTEMS_REFERENCE.md` | Add Top Bar / Screen Management section |
| `MANUAL_TEST_PLAN.md` | Add top bar smoke test checklist |

---

## Files Created/Modified

### Session A (new)
- `godot-client/project-sovereign/scripts/top_bar.gd`
- `godot-client/project-sovereign/scenes/top_bar.tscn`
- `godot-client/project-sovereign/scripts/dispatch_view.gd`
- `godot-client/project-sovereign/scenes/dispatch_view.tscn`
- `tests/test_dispatch_view.py`

### Session A (modified)
- `godot-client/project-sovereign/scenes/campaign_log.tscn` (layer 102 → 50)
- `godot-client/project-sovereign/scripts/campaign_log.gd` (minimal — close signal routing)
- `godot-client/project-sovereign/scenes/notification_bar.tscn` (positioning)
- `godot-client/project-sovereign/scripts/notification_bar.gd` (positioning if needed)
- `godot-client/project-sovereign/scripts/main.gd` (input refactor, top_bar wiring, remove LOG button refs)
- `godot-client/project-sovereign/scenes/main.tscn` (remove $LogButton, add top_bar)
- `backend/game_logic/dispatch.py` (store last_morning_dispatch)
- `backend/models/world_state.py` (last_morning_dispatch field + serialization)
- `backend/main.py` (GET /dispatch endpoint)

### Session B (new)
- `backend/game_logic/ledger.py`
- `godot-client/project-sovereign/scripts/strategic_ledger.gd`
- `godot-client/project-sovereign/scenes/strategic_ledger.tscn`
- `tests/test_ledger.py`

### Session B (modified)
- `backend/main.py` (GET /ledger endpoint)
- `godot-client/project-sovereign/scripts/main.gd` (register ledger screen with top_bar)
- `godot-client/project-sovereign/scripts/top_bar.gd` (ledger screen registration in setup)
