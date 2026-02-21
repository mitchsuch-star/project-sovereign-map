# Top Bar & Information Screens Spec

> **Authored:** February 21, 2026
> **Status:** APPROVED — audited, amendments applied, ready for implementation
> **Sessions:** 2 (A: Top Bar Framework + Dispatch, B: Strategic Ledger)
> **Audit:** Data layer verified against marshal.py, region.py, world_state.py, intel.py, dispatch.py. All field names, types, and derivation logic confirmed against source.

---

## Overview

Unified top bar UI framework replacing scattered hotkeys and overlays. The top bar is the main UI shell for all information screens going forward. Architecture decisions are final — reviewed by Opus, data layer audited.

```
[Event Log] [Ledger] [Generals] [Dispatch]          [!][*][!]  Turn 5
 ^^^ bar buttons ^^^                                 ^^^ notifications ^^^
```

---

## Architecture (FINAL -- do not deviate)

### Top bar is a CONTROLLER, not a container

`top_bar.gd` is its own CanvasLayer (layer 75) with a row of buttons + notification icons + turn counter. Screens are INDEPENDENT CanvasLayers (layer 50) that top_bar tracks and tells to show/hide. This minimizes refactoring -- each screen owns its own scene tree, rendering, and data fetching.

### Layer ordering (VERIFIED against all .tscn files)

| Layer | Contents |
|-------|----------|
| Base  | Map (Control node, no CanvasLayer) |
| 50    | All information screens (Event Log, Ledger, Generals, Dispatch) |
| 75    | Top bar + notification expanded detail panel |
| 100   | Modal dialogs -- ALL 9 existing dialogs stay at 100 (objection, redemption, enemy_phase, glorious_charge, capture_choice, load, strategic_report, interrupt, clarification). Do NOT change these. |
| 101   | Pause menu (unchanged) |

**AUDIT NOTE:** The original spec said modals at layer 90. Verified: every dialog .tscn file uses `layer = 100`. Campaign log currently at 102, drops to 50.

Top bar is always visible -- dimmed by pause menu overlay, NOT hidden (matches EU4/CK3 pattern where the top bar persists behind the pause overlay).

### Hotkeys

| Key | Action | Notes |
|-----|--------|-------|
| L   | Event Log | Existing, rewired through top_bar |
| T   | Ledger | New -- NOT Tab (Tab already toggles terminal minimize at main.gd:463-466) |
| G   | Generals | Placeholder -- screen built in future session |
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
  +-- BarContainer (HBoxContainer, anchored top, full width)
      +-- ScreenButtons (HBoxContainer, left-aligned)
      |   +-- EventLogBtn (Button: "Event Log")
      |   +-- LedgerBtn (Button: "Ledger")
      |   +-- GeneralsBtn (Button: "Generals") [disabled until future session]
      |   +-- DispatchBtn (Button: "Dispatch")
      +-- Spacer (Control, h_size_flags EXPAND)
      +-- RightSection (HBoxContainer, right-aligned)
          +-- NotificationArea (Container -- notification_bar repositioned here)
          +-- TurnLabel (Label: "Turn 5")
```

**State tracking:**

```gdscript
var active_screen: String = ""  # "" = none, "event_log", "ledger", "generals", "dispatch"
var screens: Dictionary = {}    # maps screen name to node reference

func register_screen(name: String, node: Node)  # called during setup
func toggle_screen(name: String)                 # close if open, open if closed (closing current first)
func close_all_screens()                         # called on turn transition
func is_screen_open() -> bool                    # for main.gd dialog guard
func get_active_screen() -> String               # for button highlighting and sub-tab key guards
func update_turn(turn_number: int)               # updates TurnLabel
```

**Button highlighting:** Active screen's button gets a distinct style (pressed/toggled look via StyleBoxFlat override). All other buttons use normal style.

**Turn counter:** Updated via `update_turn()` from `_update_status()` in main.gd. Add `if top_bar: top_bar.update_turn(current_turn)` at the end of `_update_status()` (main.gd:1219). This covers all backend response paths since every response handler calls `_update_status()`.

**Signal:** `screen_changed(screen_name: String)` -- emitted on open/close. main.gd listens to update map blocking.

### Task 2: Campaign Log Refactor

Minimal changes to integrate into top bar:

1. Change CanvasLayer layer from 102 to 50 in `campaign_log.tscn`. **No z-fighting risk:** all information screens share layer 50, but the one-screen-at-a-time rule (top_bar enforces this) means only one is ever visible.
2. Remove standalone `$LogButton` from `main.tscn` (it's a Button node at top-right: anchor_left=1.0, anchor_right=1.0, offset_left=-80, offset_top=10, offset_right=-10, offset_bottom=42) and its `_on_log_button_pressed()` handler (main.gd:2248) and the log_button @onready var (main.gd:30) and pressed.connect (main.gd:278)
3. L key in `main.gd _unhandled_input` now calls `top_bar.toggle_screen("event_log")` instead of directly opening campaign_log
4. Campaign log registers with top_bar during setup in main.gd `_ready()`: `top_bar.register_screen("event_log", campaign_log)` -- registration happens AFTER both top_bar and campaign_log are loaded, so no timing issue
5. The log's `open_log(api_client)` method still calls `api_client.get_campaign_log()` as today -- no change to data fetching
6. Remove the wholesale `_unhandled_input` consumption from campaign_log path in main.gd (lines 444-449: the `if campaign_log and campaign_log.visible:` block that consumes ALL input and only allows L to close). Input blocking is now handled by main.gd checking `top_bar.is_screen_open()` with the new blocking pattern
7. **CRITICAL:** Remove campaign_log from `_is_any_dialog_open()` (main.gd:2227-2228). Campaign log is now an information screen, NOT a modal dialog. It moves to `_is_screen_open()` via top_bar.
8. Campaign log's `close_log()` still emits `closed` signal -- top_bar listens to know when screen was closed via X button or overlay click (in addition to bar button toggle)

### Task 3: Dispatch Re-read Screen

**Backend changes:**

1. Add `last_morning_dispatch` field to WorldState `__init__`: `self.last_morning_dispatch: dict = {}`
2. In `build_morning_dispatch()` (dispatch.py), store result on world: `world.last_morning_dispatch = dispatch_dict` -- the dict contains only primitives (ints, strings, bools, lists of dicts), JSON-serializable as-is, no circular refs
3. Serialize `last_morning_dispatch` in WorldState `to_dict()` / `from_dict()` (with `.get('last_morning_dispatch', {})` default)
4. New endpoint: `GET /dispatch` -- returns `world.last_morning_dispatch` or `{"success": true, "dispatch": {}}` if not yet built (turn 0)
5. **Add `get_dispatch()` method to `api_client.gd`** -- same pattern as `get_campaign_log()`
6. Update `docs/SAVE_FORMAT_REFERENCE.md` with new field

**Godot scene:** `dispatch_view.gd` + `dispatch_view.tscn`

- CanvasLayer at layer 50
- BackgroundOverlay (click-to-close, same pattern as campaign_log)
- PanelContainer centered, scrollable, styled to match campaign_log (dark panel bg `Color(0.08, 0.1, 0.15, 1)`, gold border `Color(0.85, 0.75, 0.55, 1)`, corner_radius 8, content_margin 20/16) -- the style is defined inline in campaign_log.tscn as a sub_resource, NOT a shared theme resource, so copy the StyleBoxFlat definition
- Renders dispatch with the same BBCode formatting as `_display_morning_dispatch()` in main.gd (167 lines, uses 8 COLOR constants: COLOR_BERTHIER, COLOR_INFO, COLOR_ERROR, COLOR_SUCCESS, COLOR_BATTLE, COLOR_OBSERVATION, COLOR_DISPATCH, and `_format_number()` helper). Duplicate the formatting into dispatch_view.gd using RichTextLabel directly instead of `add_output()`. Document as tech debt for future extraction. Format is stable -- duplication is acceptable.
- Shows "No dispatch available yet." on turn 0 / empty dispatch
- D key or Dispatch button -> top_bar.toggle_screen("dispatch") -> dispatch_view.open(api_client) -> fetches GET /dispatch -> renders
- Read-only, no interaction besides scrolling
- Registers with top_bar as "dispatch"

### Task 4: Notification Bar Repositioning

Move notification icons into the top bar's right section. Two approaches -- choose whichever is less disruptive:

**(a) Reparent:** notification_bar becomes a child of TopBar's RightSection/NotificationArea. Adjust positioning code. Expanded detail panel still drops down from notification_bar, now rendering at layer 75 (top bar's layer) -- above screens at layer 50.

**(b) Relative positioning:** Keep notification_bar as its own node but set its position relative to the top bar's RightSection. Less refactoring but more fragile if bar layout changes.

Either way:
- notification_bar is a `Control` (extends Control, NOT CanvasLayer), so if reparented as a child of TopBar's CanvasLayer at 75, it inherits layer 75 automatically
- Expanded detail panel is currently positioned at `Vector2(0, 36)` relative to notification_bar (notification_bar.gd:208). If reparented, this relative positioning still works, but the parent position changes -- verify the panel drops down correctly
- Remove `offset_top = 48.0` from notification_bar.tscn (was below the old LOG button which is being removed)
- Verify expanded panel doesn't get clipped behind screen content at layer 50 (it won't -- layer 75 > layer 50)
- Notification functionality unchanged -- same dismiss API, same priority colors, same icon buttons

### Task 5: Generals Placeholder

- Add "Generals" button to top bar ScreenButtons HBoxContainer
- Button is disabled (greyed out, `disabled = true`)
- G hotkey wired but does nothing while button is disabled (guard: `if screens.has("generals") and screens["generals"] != null`)
- This gets built in a future session -- just wire the button and hotkey so the framework is ready

### Task 6: Input Refactor in main.gd

**Split dialog detection:**

Replace `_is_any_dialog_open()` (main.gd:2207-2229) with three functions:

```gdscript
func _is_modal_dialog_open() -> bool:
    """True when a modal dialog requiring player choice is visible."""
    # objection, redemption, enemy_phase, glorious_charge,
    # capture_choice, load_dialog, strategic_report, interrupt, clarification
    # These block EVERYTHING
    # NOTE: campaign_log is REMOVED from this check -- it's now a screen, not a modal

func _is_screen_open() -> bool:
    """True when a top bar screen is open. Blocks map, allows terminal."""
    return top_bar != null and top_bar.is_screen_open()

func _is_hotkey_blocked() -> bool:
    """True when hotkeys should not fire."""
    return command_input.has_focus() or _is_modal_dialog_open()
```

**Input blocking while a screen is open (NOT a modal dialog):**

- Set `map_area.mouse_filter = Control.MOUSE_FILTER_IGNORE` when screen opens (block map clicks/hover). MapArea is a Control node (confirmed in main.tscn), so mouse_filter is valid. Current default is MOUSE_FILTER_STOP (Godot default for Control -- not explicitly set in tscn).
- Restore `map_area.mouse_filter = Control.MOUSE_FILTER_STOP` when screen closes
- Block map hotkeys: arrow keys (panning in map.gd _process), E (end turn) -- guard with `_is_screen_open()`
- Allow terminal input: player can type commands and submit while reading any screen
- Screen hotkeys (L, T, G, D) still work for switching between screens -- guard with `_is_hotkey_blocked()` only (not `_is_screen_open()`)
- Connect to top_bar's `screen_changed` signal to toggle map mouse filter AND `map_area.panning_enabled` (see Edge Case 10)

**All hotkey guards use `_is_hotkey_blocked()`:**

```gdscript
# In _unhandled_input:
if event.keycode == KEY_L:
    if not _is_hotkey_blocked():
        top_bar.toggle_screen("event_log")
        get_viewport().set_input_as_handled()
```

**Close all screens on BOTH turn transition paths:**

1. In `_display_turn_change()` (main.gd:914) -- manual end turn
2. In `_display_turn_advance()` (main.gd:1127) -- auto-advance when AP exhausted
3. Before enemy phase dialog appears (main.gd ~line 645, before `_show_enemy_phase_dialog()` is called) -- close screens so they don't sit behind the modal

All three paths must call `if top_bar: top_bar.close_all_screens()`.

**Esc key updated Smart Esc:**

```
Priority order:
1. If command_input focused -> release_focus (handled in gui_input at main.gd:365-367, fires BEFORE _unhandled_input)
2. If any screen open -> close_all_screens via top_bar
3. If pause menu open -> close pause menu
4. If modal dialog open -> do nothing (modals handle their own Esc)
5. If nothing open -> open pause menu
```

**NOTE:** Step 1 happens in `_on_command_input_gui_input` (a gui_input handler on LineEdit), which fires before `_unhandled_input`. The existing code at main.gd:365-367 already handles this. Steps 2-5 go in `_unhandled_input`.

### Session A Tests

Backend only (~5 tests in `tests/test_dispatch_view.py`):

- `last_morning_dispatch` stored on WorldState after `build_morning_dispatch()`
- `last_morning_dispatch` serialization roundtrip (to_dict -> from_dict)
- `GET /dispatch` returns stored dispatch
- `GET /dispatch` returns empty dict when no dispatch built yet
- No-float enforcement on dispatch endpoint response

No Godot unit tests -- UI is smoke tested manually per `docs/MANUAL_TEST_PLAN.md`.

---

## Session B: Strategic Ledger

### Backend: ledger.py

`build_strategic_ledger(world) -> dict` with 5 sections:

#### "forces" -- per player marshal

```python
{
    "name": str,
    "type": str,           # "infantry" / "cavalry" / "artillery"
                            # Derived: "cavalry" if marshal.is_cavalry,
                            #          "artillery" if marshal.is_artillery,
                            #          else "infantry"
    "personality": str,     # e.g. "aggressive" — from marshal.personality.value
    "location": str,
    "strength": int,
    "morale": int,
    "trust": int,           # marshal.trust.value (Trust class, .value is int)
    "stance": str,          # "aggressive" / "neutral" / "defensive"
    "status": str,          # derived — see priority chain below
    "strategic_order": str, # see formatting rules below
    "battles_won": int,     # marshal.battles_won (confirmed: field exists)
    "battles_lost": int,    # marshal.battles_lost (confirmed: field exists)
    "special_flags": {
        "shock_ready": bool,    # marshal.shock_bonus > 0
        "counter_punch": bool,  # marshal.counter_punch_available
        "reckless": int,        # marshal.recklessness (0 if not cavalry)
        "exhausted": bool,      # marshal._get_exhaustion_penalty() > 0
                                # NOTE: No "exhausted" boolean exists on Marshal.
                                # Must derive from _get_exhaustion_penalty() method.
                                # Artillery is exempt (method returns 0.0 internally).
                                # Penalty triggers on 2nd+ attack in a turn.
    }
}
```

**Status derivation priority (highest wins):**
1. `marshal.broken` -> "broken"
2. `marshal.retreating` -> "retreating"
3. `marshal.drilling or marshal.drilling_locked` -> "drilling"
4. `marshal.fortified` -> "fortified"
5. `marshal.in_strategic_mode and marshal.strategic_order.command_type == "HOLD"` -> "holding"
6. `marshal.in_strategic_mode and marshal.strategic_order.command_type == "PURSUE"` -> "pursuing"
7. `marshal.in_strategic_mode and marshal.strategic_order.command_type == "MOVE_TO"` -> "moving_to"
8. `marshal.in_strategic_mode and marshal.strategic_order.command_type == "SUPPORT"` -> "supporting"
9. default -> "idle"

Note: `in_strategic_mode` is a property (`self.strategic_order is not None`), not a stored field.

**Strategic order summary string formatting:**
- `marshal.strategic_order is None` -> `"None"`
- `command_type == "MOVE_TO"` -> `"MOVE_TO {target} ({len(order.path)} turns left)"`
- `command_type == "PURSUE"` -> `"PURSUE {target} (tracking)"` (target is a marshal name)
- `command_type == "SUPPORT"` -> `"SUPPORT {target} (active)"` (target is a marshal name)
- `command_type == "HOLD"` -> `"HOLD at {target}"` (target is a region name or "generic")

#### "territories" -- per player-controlled region

```python
{
    "name": str,
    "terrain": str,
    "region_type": str,         # "capital" / "major_city" / "city" / "town" / "rural"
    "buildings": [              # list of dicts
        {"name": str, "status": str}
        # status: "built" / "constructing (Xt)" / "damaged"
        # For built: iterate region.buildings list, each is {"type": str, "damaged": bool}
        # For constructing: from region.building_under_construction (singular dict, not a queue)
    ],
    "garrison": int,            # region.garrison_strength, 0 if none
    "supply_capacity": int,     # region.supply_capacity (property, computed from type + buildings + terrain)
    "occupant_count": int,      # count of marshals where marshal.location == region.name
    "supply_status": str,       # "OK" / "Over capacity" — see derivation below
    "stability": int,           # region.stability (int, 0-100)
    "war_damage": int,          # int(region.war_damage * 100) — stored as float 0.0-0.5,
                                # display as percentage 0-50. int(0.3) = 0 which is WRONG.
                                # Must multiply by 100 first.
    "income": int,              # region.get_effective_income() — NOT region.income_value
                                # Applies stability and war_damage modifiers, supply_depot +50,
                                # market +25%
}
```

**NO `fortification_level` field.** Fortification bonuses live on Marshal (`defense_bonus` from fortify actions), not on Region. Regions have `buildings` list which already shows if a "fortification" building exists. Don't invent a field that doesn't exist on the model.

**Supply status derivation:**
- Sum strength of all marshals in region = total_occupant_strength
- Compare against `region.supply_capacity`
- `total_occupant_strength <= capacity` -> "OK"
- `total_occupant_strength > capacity` -> "Over capacity"
- **No "Strained" tier.** Attrition triggers as soon as total exceeds capacity (with a 1.5x bonus for home territory defenders, but that's a per-marshal calculation in `process_supply_attrition()`, not a display threshold). Showing a fake "Strained" band would mislead players about when attrition actually kicks in.

**FUTURE INTERPLAY NOTE:** When diplomacy is added, region ownership changes will affect this section. Supply status depends on which nation controls a region (home territory 1.5x bonus). If regions can change hands mid-session or have contested states, the supply_status derivation may need updating.

#### "economy" -- single dict

```python
{
    "treasury": int,            # world.gold (property for world.nation_gold[player_nation])
    "income": int,              # world.calculate_turn_income(player_nation)["income"]
    "upkeep": int,              # world.calculate_turn_upkeep(player_nation)["total"]
    "net": int,                 # income - upkeep
    "bankruptcy_turns": int,    # world.bankruptcy_turns (property for nation_bankruptcy_turns)
    "construction_queue": [     # DERIVED — iterate all player regions, collect active builds
        {"region": str, "building": str, "turns_remaining": int}
        # Each region has at most ONE building_under_construction (dict or None).
        # Not a queue — one active build per region max.
        # Iterate: for r in regions if r.controller == player_nation
        #            and r.building_under_construction is not None
    ],
    "income_breakdown": [       # per-region income detail
        {"region": str, "income": int, "type": str}
        # income = region.get_effective_income()
        # type = region.region_type
        # world.calculate_turn_income() already returns region_details with this data
    ]
}
```

**FUTURE INTERPLAY NOTE:** When trade routes or diplomacy modifiers are added, income_breakdown should include those sources. The current income calculation in world_state.py only considers region base + buildings + stability + war_damage. Any new income sources (trade, tribute, subsidies) would need to flow through calculate_turn_income() and then automatically appear here.

#### "intel" -- dict

```python
{
    "known_enemies": [          # fog-filtered enemy sightings
        {
            "name": str,
            "nation": str,
            "location": str,
            "strength_display": str,
            # Derivation by visibility tier (from RegionIntel):
            #   FULL:       exact strength formatted with commas, e.g. "45,000"
            #   PARTIAL:    band string from get_strength_band(), e.g. "large force"
            #   STALE:      "last seen: {frozen_strength}" using intel.known_marshals snapshot
            #   LAST_KNOWN: "unknown" (location only, no strength data)
            #   UNKNOWN:    not included in this list
            "visibility": str,  # "full" / "partial" / "stale" / "last_known"
        }
    ],
    "nation_summaries": [       # per-enemy-nation aggregated intel
        {
            "nation": str,
            "known_marshals": int,
            "estimated_strength": int,
            # For exact strengths, use actual value.
            # For bands, use BAND_MIDPOINTS from dispatch.py:
            #   {"no forces": 0, "screening force": 2500, "small force": 10000,
            #    "substantial force": 27500, "large force": 55000, "massive force": 85000}
            "regions_controlled": int,
            # Count regions where region.controller == nation
        }
    ],
    "unknown_region_count": int,  # count of regions at UNKNOWN visibility
}
```

**Data source:** `world.get_region_intel(region_name)` returns a `RegionIntel` object with:
- `.visibility` (str: "full"/"partial"/"stale"/"last_known"/"unknown")
- `.known_marshals` (list of dicts: `{"name", "nation", "strength"?, "band"?, "morale"?, "stance"?}`)
- `.exact_strength` (int or None, only at FULL)
- `.strength_band` (str)
- `.last_updated_turn` (int)

Iterate all regions, skip UNKNOWN, collect enemy marshals from intel.known_marshals.

**FUTURE INTERPLAY NOTE:** The intel section is designed to be extensible. When multi-marshal coordination (Phase 7) is complete, intel could show coordination group sightings. When diplomacy is added, nation_summaries could include diplomatic status (allied/hostile/neutral). The structure supports adding fields to nation_summaries without breaking the UI -- new fields would just need color coding in the Godot renderer.

#### "manpower" -- dict

```python
{
    "infantry": {
        "current": int,         # world.manpower_pools[player_nation]["infantry"]
        "max": int,             # MAX_INFANTRY_POOL = 100000
        "regen_rate": int,      # DYNAMIC — see calculation below
        "recruit_amount": int,  # INFANTRY_RECRUIT_AMOUNT = 10000
        "recruit_base_cost": int,  # 200 (base cost — actual cost varies by region stability)
        "cost_note": str,       # "Modified by region stability (+/-25%)"
        "turns_until_full": int,
        # = 0 if current >= max
        # = int(math.ceil((max - current) / regen_rate)) if regen_rate > 0
        # = -1 if regen_rate == 0 (meaning "never")
        # IMPORTANT: math.ceil returns int in Python 3, but wrap with int() anyway for safety
    },
    "cavalry": {
        # same fields, different constants:
        # max = MAX_CAVALRY_POOL = 30000
        # recruit_amount = CAVALRY_RECRUIT_AMOUNT = 5000
        # recruit_base_cost = 300
    },
    "artillery": {
        # same fields, different constants:
        # max = MAX_ARTILLERY_POOL = 20000
        # recruit_amount = ARTILLERY_RECRUIT_AMOUNT = 3000
        # recruit_base_cost = 400
    },
}
```

**Regen rate calculation (DYNAMIC -- not a static constant):**

Infantry regen is always `INFANTRY_BASE_REGEN = 5000` (flat, no territory dependency).

Cavalry regen: `CAVALRY_BASE_REGEN (500) + PLAINS_CAVALRY_REGEN (500) * plains_count + STABLES_CAVALRY_REGEN (750) * stables_count` where:
- `plains_count` = number of player-controlled regions with `terrain == "plains"`
- `stables_count` = number of player-controlled regions with `has_building("stables")`

Artillery regen: `ARTILLERY_BASE_REGEN (300) + URBAN_ARTILLERY_REGEN (200) * urban_count` where:
- `urban_count` = number of player-controlled regions with `terrain == "urban"`

**MUST extract into reusable method:** Create `WorldState.get_manpower_regen_rates(nation) -> dict` that returns `{"infantry": int, "cavalry": int, "artillery": int}`. Both `_process_manpower_regen()` and `ledger.py` call this method. Do NOT duplicate the calculation logic.

**All values `int()` wrapped. No floats to Godot.**

### Backend: endpoint

`GET /ledger` in main.py:
- Calls `build_strategic_ledger(world)`
- Returns `{"success": true, "ledger": <dict>}`
- Guards: `if not game_state.get("world")` -> 400

### Godot: strategic_ledger.gd + strategic_ledger.tscn

CanvasLayer at layer 50.

**Scene structure:**

```
StrategicLedger (CanvasLayer, layer 50)
  +-- BackgroundOverlay (ColorRect, click-to-close)
  +-- PanelContainer (centered, styled same as campaign_log)
      +-- VBoxContainer
          +-- HeaderRow (HBoxContainer)
          |   +-- TitleLabel ("STRATEGIC LEDGER")
          |   +-- CloseButton ("X")
          +-- SubTabRow (HBoxContainer)
          |   +-- ForcesTab (Button: "FORCES")
          |   +-- TerritoriesTab (Button: "TERRITORIES")
          |   +-- EconomyTab (Button: "ECONOMY")
          |   +-- IntelTab (Button: "INTELLIGENCE")
          |   +-- ManpowerTab (Button: "MANPOWER")
          +-- HSeparator
          +-- ScrollContainer
              +-- ContentArea (VBoxContainer -- populated per sub-tab)
```

**Sub-tab switching:**
- Number keys 1-5 switch sub-tabs. **Handled by strategic_ledger.gd in its own `_input()` method**, guarded by `visible` check (only processes when the ledger is actually shown). NOT in main.gd -- don't couple main to ledger internals.
- Clicking sub-tab buttons also switches
- Default sub-tab: FORCES
- Active sub-tab button gets highlight style (same pattern as top bar active button)

**Content rendering per sub-tab:**

Each sub-tab clears ContentArea and populates with RichTextLabel or Label nodes.

**Color coding rules:**
- broken / retreating -> red text
- drilling -> blue text
- idle -> grey text
- Supply "Over capacity" -> red
- Bankruptcy turns > 0 -> red
- Pool depleted (current = 0) -> red
- Pool low (current < recruit_amount) -> orange
- Trust < 30 -> red text
- Morale < 40 -> red text
- Trust < 55 or Morale < 60 -> orange text

**Style:** Match campaign_log panel (dark panel bg `Color(0.08, 0.1, 0.15, 1)`, gold border `Color(0.85, 0.75, 0.55, 1)`, corner_radius 8, content_margin 20/16). Copy the inline StyleBoxFlat from campaign_log.tscn -- it's not a shared theme resource.

**Data fetching:** `open(api_client)` fetches `GET /ledger`, caches while open. Registers with top_bar as "ledger".

### Session B Tests

~45 tests in `tests/test_ledger.py`:

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
- Special flags: exhausted from _get_exhaustion_penalty() > 0
- Strategic order summary string: MOVE_TO with turns remaining
- Strategic order summary string: PURSUE with "tracking"
- Strategic order summary string: SUPPORT with "active"
- Strategic order summary string: HOLD with region
- Strategic order summary string: None when no order
- Type detection: cavalry, artillery, infantry

**Territories section:**
- Supply status: OK when occupant strength <= capacity
- Supply status: Over capacity when occupant strength > capacity
- NO "Strained" tier (verify it doesn't exist)
- war_damage as percentage: int(region.war_damage * 100), not int(region.war_damage)
- income uses get_effective_income(), not income_value
- Building display: built buildings from region.buildings list
- Building display: constructing from region.building_under_construction
- Building damaged status
- Garrison strength included
- NO fortification_level field present (verify it doesn't exist)
- Occupant count matches marshals in region

**Economy section:**
- Net = income - upkeep
- Bankruptcy turns included when > 0
- Construction queue derived from regions with active builds
- Construction queue is empty when no regions are building
- Income breakdown per region uses get_effective_income()

**Intel section:**
- UNKNOWN regions excluded from known_enemies
- FULL visibility shows exact strength (formatted with commas)
- PARTIAL visibility shows band string
- STALE visibility shows "last seen: N"
- LAST_KNOWN shows "unknown" strength
- Nation summary: marshal count aggregation
- Nation summary: estimated strength from BAND_MIDPOINTS
- Unknown region count

**Manpower section:**
- Dynamic regen rates: test with/without plains regions, stables, urban regions
- Regen rate extraction: get_manpower_regen_rates() matches _process_manpower_regen() logic
- turns_until_full: 0 when at max
- turns_until_full: correct ceiling division
- turns_until_full: -1 when regen_rate is 0
- recruit_base_cost shows base cost (200/300/400)
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
- No cross-screen navigation (Ledger marshal click -> Generals, defer to 1805)
- No "Issue Order" button in Generals (not built yet)
- No screen animations/transitions
- No notification sound
- No real-time screen refresh (close all on turn change is sufficient)
- No Generals screen content (placeholder only)
- No "Strained" supply tier (attrition doesn't work that way)
- No fortification_level on territories (fortification is a marshal state, not a region state)

---

## Edge Cases Addressed

1. **Rapid toggle during async fetch:** If player toggles screen off while data is loading, callback guard checks visibility before populating. Campaign log already has this pattern (shows "Loading..." then populates) -- dispatch_view and strategic_ledger follow same approach.

2. **Screen open + end turn:** All screens close on turn transition via `top_bar.close_all_screens()`. Called from BOTH `_display_turn_change()` and `_display_turn_advance()`. Morning Dispatch renders in terminal as usual.

3. **Screen open + modal dialog:** Modal dialogs are at layer 100, screens at layer 50. Dialog appears on top. Screen stays open underneath. When dialog is dismissed, screen is still there. `_is_modal_dialog_open()` is checked separately from `_is_screen_open()`.

4. **Notification panel + screen overlap:** Notification expanded panel renders at layer 75 (top bar layer), above screens at layer 50. No visual overlap issues. notification_bar is a Control (extends Control, not CanvasLayer), so it inherits its parent's layer.

5. **D/G/T hotkeys while typing:** All guarded by `_is_hotkey_blocked()` which checks `command_input.has_focus()`.

6. **Pause menu + top bar:** Top bar stays visible but dimmed by pause overlay (75% opacity ColorRect at layer 101). Turn counter and notifications remain visible-but-dimmed. Matches EU4/CK3 pattern.

7. **Tab key unchanged:** Tab still toggles terminal minimize/restore (main.gd:463-466). NOT reassigned to Ledger. T is Ledger.

8. **Screens close before enemy phase dialog:** When end turn triggers enemy phase, screens are closed before the enemy phase dialog (layer 100) appears -- avoids stale screen content sitting behind the modal.

9. **Ledger 1-5 keys don't leak:** Handled in strategic_ledger.gd's own `_input()`, guarded by `visible`, so they only fire when ledger is actually shown. If another system later uses number keys, there's no conflict because the guard prevents processing when ledger is hidden.

10. **map.gd arrow key panning vs screen open:** map.gd `_process()` (line 109) checks `Input.is_action_pressed()` for arrow keys, which fires regardless of `_unhandled_input` handling. When a screen is open, `map_area.mouse_filter` is set to IGNORE, but `_process` still runs. The text-focus guard (map.gd:121) doesn't know about screens. **Implementation: add `var panning_enabled: bool = true` to map.gd. In `_process`, add `if not panning_enabled:` before the arrow key block (after the zoom block). main.gd toggles `map_area.panning_enabled = false` when a screen opens and `= true` when it closes, inside the `screen_changed` signal handler that already manages `mouse_filter`.** This avoids reference cycles — map.gd never references main, main already holds `map_area`.

---

## Future Interplay Notes

These systems have known interaction points with planned features:

| Feature | Affected Ledger Section | What Changes |
|---------|------------------------|--------------|
| **Multi-Marshal Coordination (Phase 7)** | Forces | Add coordination group display, combined arms bonuses. `status` might need "coordinating" state. |
| **Diplomacy (1805)** | Intel, Economy | Nation summaries need diplomatic status. Economy needs trade/tribute income sources. |
| **Sieges (1805)** | Territories | Siege status per region, garrison under siege display. |
| **Coalition Trigger** | Intel | Coalition formation status, threat level indicator. |
| **Generals Screen** | Forces | Cross-nav from Forces to Generals for detailed marshal view. |
| **Jealousy (Phase 7b)** | Forces | Jealousy indicators between marshals, affects coordination willingness. |

The ledger structure is designed to be additive -- new fields can be added to any section without breaking existing UI. The Godot renderer ignores unknown keys.

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
- `godot-client/project-sovereign/scenes/campaign_log.tscn` (layer 102 -> 50)
- `godot-client/project-sovereign/scripts/campaign_log.gd` (minimal -- close signal routing)
- `godot-client/project-sovereign/scenes/notification_bar.tscn` (positioning, remove offset_top 48)
- `godot-client/project-sovereign/scripts/notification_bar.gd` (positioning if needed)
- `godot-client/project-sovereign/scripts/main.gd` (input refactor, top_bar wiring, remove LOG button refs, remove campaign_log from _is_any_dialog_open)
- `godot-client/project-sovereign/scenes/main.tscn` (remove $LogButton, add top_bar)
- `godot-client/project-sovereign/scripts/api_client.gd` (add get_dispatch() method)
- `backend/game_logic/dispatch.py` (store last_morning_dispatch on world)
- `backend/models/world_state.py` (last_morning_dispatch field + serialization)
- `backend/main.py` (GET /dispatch endpoint)
- `godot-client/project-sovereign/scenes/map.gd` (add `panning_enabled` flag, guard in `_process`)

### Session B (new)
- `backend/game_logic/ledger.py`
- `godot-client/project-sovereign/scripts/strategic_ledger.gd`
- `godot-client/project-sovereign/scenes/strategic_ledger.tscn`
- `tests/test_ledger.py`

### Session B (modified)
- `backend/main.py` (GET /ledger endpoint)
- `backend/models/world_state.py` (add get_manpower_regen_rates() method)
- `godot-client/project-sovereign/scripts/main.gd` (register ledger screen with top_bar)
- `godot-client/project-sovereign/scripts/top_bar.gd` (ledger screen registration in setup)
- `godot-client/project-sovereign/scripts/api_client.gd` (add get_ledger() method)
