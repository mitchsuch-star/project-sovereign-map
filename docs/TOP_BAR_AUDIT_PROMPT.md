# Top Bar Spec Audit Prompt

> Copy everything below the line into a new Opus session.

---

## Task

You are auditing `docs/TOP_BAR_SPEC.md` before implementation. This spec defines a unified top bar UI framework (Session A) and a Strategic Ledger backend+frontend (Session B). Do NOT write any code. Your job is to find problems.

## What to Read (in this order)

Read ALL of these files before writing any findings:

**The spec:**
- `docs/TOP_BAR_SPEC.md` — the full spec being audited

**Existing Godot code (you are checking the spec's assumptions against reality):**
- `godot-client/project-sovereign/scripts/main.gd` — input handling, dialog guards, terminal UI, morning dispatch rendering, all `_on_*` handlers. THIS IS THE MOST IMPORTANT FILE. The spec rewires large parts of it.
- `godot-client/project-sovereign/scripts/campaign_log.gd` — current overlay being refactored
- `godot-client/project-sovereign/scripts/pause_menu.gd` — CanvasLayer 101, Smart Esc pattern
- `godot-client/project-sovereign/scripts/notification_bar.gd` — alert icons being repositioned
- `godot-client/project-sovereign/scenes/main.tscn` — scene tree structure, node names, what $LogButton actually is
- `godot-client/project-sovereign/scenes/campaign_log.tscn` — current layer, structure
- `godot-client/project-sovereign/scenes/notification_bar.tscn` — current positioning, anchors
- `godot-client/project-sovereign/scenes/map.gd` — map rendering, mouse_filter, _gui_input, tooltip handling, arrow key panning

**Backend code (you are checking ledger data availability):**
- `backend/models/world_state.py` — WorldState fields, advance_turn, serialization, manpower, supply
- `backend/models/marshal.py` — Marshal fields, states, to_dict/from_dict
- `backend/models/region.py` — Region fields, buildings, garrison, supply_capacity
- `backend/game_logic/dispatch.py` — Morning Dispatch builder (ledger reuses similar patterns)
- `backend/game_logic/combat.py` — where battles_won/lost live
- `backend/intel_report.py` — existing fog-filtered intel (ledger reuses)
- `backend/models/intel.py` — RegionIntel, visibility tiers, known_marshals
- `backend/campaign_log.py` — existing fog filter patterns to reuse
- `backend/main.py` — existing endpoints, response formatting patterns
- `backend/commands/executor.py` — marshal state fields referenced by ledger (drilling, fortified, strategic mode, etc.)
- `backend/commands/strategic.py` — strategic order fields (command_type, target, path length)

**Project rules:**
- `CLAUDE.md` — golden rules, serialization enforcement, patterns, troubleshooting

## What to Audit

### Category 1: Data Availability (CRITICAL)

For every field the spec says `build_strategic_ledger()` will return, verify the source data actually exists on the model objects. Specifically:

- **Forces section:** Every field listed — does Marshal actually have `battles_won`, `battles_lost`, `shock_bonus` (for shock_ready flag), `counter_punch_available`, `recklessness`, etc.? Check `marshal.py __init__` and `to_dict`.
- **Status derivation:** The spec lists a priority chain (broken > retreating > drilling > fortified > holding > pursuing > moving_to > supporting > idle). Verify the actual field names on Marshal — is it `broken`, `is_broken`, `broken_state`? Is it `drilling`, `is_drilling`? Is strategic mode checked via `in_strategic_mode` or some other field? Is `command_type` the right field name on strategic orders?
- **Territories section:** Does Region have `stability`, `war_damage`, `income` (or is income calculated, not stored)? What about `fort_level` — is it a percentage already or a raw value? Is `supply_capacity` a method or property? How is `occupant_count` derived — do you iterate world.marshals filtering by location?
- **Economy section:** Where does `treasury`, `income`, `upkeep`, `bankruptcy_turns` live? On WorldState? Are they properties, methods, or stored values? Is there a `construction_queue` field or do you derive it from region building states?
- **Intel section:** Can `get_region_intel()` be reused directly? What does it return — does it have `known_marshals` with the fields the spec expects?
- **Manpower section:** Where are `regen_rate` values? Are they constants or calculated per-turn? The spec says `turns_until_full` — verify the math is possible from available data.

### Category 2: Godot Assumptions (CRITICAL)

- **main.gd _unhandled_input:** Read the ENTIRE function. The spec says to rewire L, add T/G/D, change Esc priority. Are there other hotkeys in _unhandled_input that the spec doesn't mention but that need updating? (E key? Tab? Others?)
- **Campaign log input consumption:** The spec says to remove "wholesale _unhandled_input consumption from campaign_log path in main.gd (lines 444-449)." Find the actual lines. Is the spec's line reference correct? What exactly happens there — is it just an early return, or does it set_input_as_handled, or something else?
- **$LogButton:** The spec says remove it from main.tscn. What is $LogButton actually — a Button node? Where in the scene tree? Is it referenced anywhere else besides _on_log_button_pressed?
- **map_area.mouse_filter:** The spec says set to MOUSE_FILTER_IGNORE when screens open. What is the current mouse_filter? Is `map_area` actually a Control (which has mouse_filter) or a Node2D (which doesn't)? Check the scene tree.
- **notification_bar positioning:** The spec says to reposition. The current tscn has specific anchor/offset values. Will reparenting break the expanded_panel positioning logic in notification_bar.gd? Check how `expanded_panel` is positioned (absolute vs relative).
- **Screen close on turn transition:** Where exactly in main.gd does turn transition happen? Is it `_display_turn_change()`? Is there ONE place or multiple paths (manual end turn vs auto-advance when AP exhausted)?
- **Esc priority order:** The spec lists 5 priority levels. Compare against the current Smart Esc implementation in pause_menu.gd and main.gd. Are there any cases the spec misses?

### Category 3: Spec Completeness

- **api_client.gd:** The spec mentions dispatch_view and strategic_ledger fetch data via API. Does api_client.gd need new methods (`get_dispatch()`, `get_ledger()`)? The spec doesn't list api_client.gd in modified files for Session B.
- **Screen registration timing:** The spec says screens register with top_bar during `_ready`. What's the node initialization order? If top_bar is loaded dynamically (like pause_menu is via `load()`), it might not exist when campaign_log tries to register. Check how existing overlays are loaded in main.gd `_ready()`.
- **Turn counter update:** The spec says "Updated from game state on every backend response." Where does this happen? Which function in main.gd processes backend responses? Is there ONE function or do multiple response handlers need to call `top_bar.update_turn()`?
- **Screen styling:** Campaign log has a specific StyleBoxFlat (dark panel, gold border). The spec says new screens match this style. Is the style defined inline in the tscn or as a theme resource? Will the ledger and dispatch need to copy-paste the style or can they reference a shared resource?
- **Close-all-screens on turn transition:** The spec says call `top_bar.close_all_screens()`. But screens fetch data on open. If a screen was open and data was mid-flight when close_all fires, does the callback need to guard against populating a closed screen?
- **Ledger sub-tab number keys (1-5):** These need to ONLY work when the ledger is open. Where in the input chain do they get handled? If they're in `_unhandled_input`, they'll conflict with other uses of number keys (currently none, but verify). The spec says guard with `top_bar.get_active_screen() == "ledger"` — but _unhandled_input is on main.gd while ledger is its own script. Who handles the 1-5 keys?
- **Dispatch formatting duplication:** The spec says extract shared dispatch rendering OR duplicate. Is `_display_morning_dispatch()` in main.gd complex enough that duplication is risky? How many lines is it? Does it reference main.gd-specific variables (COLOR constants, add_output, etc.)?

### Category 4: Serialization & Backend

- **`last_morning_dispatch` serialization:** The spec says store as dict on WorldState. Dispatch contains nested dicts with lists. Verify the dict returned by `build_morning_dispatch()` is JSON-serializable as-is (no datetime objects, no custom classes, no circular refs).
- **Endpoint patterns:** Check existing GET endpoints in main.py. Do they follow a consistent pattern? Does the spec's proposed response format match?
- **Ledger no-float enforcement:** The spec says "All values int() wrapped." The dispatch builder already does this. But are there values in the ledger that could be floats — morale as float, trust as float, income calculations with division?
- **Fog filtering for intel section:** The spec says "reuse existing get_region_intel()." Where is this function? What does it return? Does it give you everything you need (marshal name, nation, strength, visibility tier) or do you need to combine it with other data?

### Category 5: Edge Cases & Conflicts

- **Dialog layer conflicts:** The spec puts modal dialogs at layer 90. Currently, objection_dialog, enemy_phase_dialog, etc. — what layers are they at? If they're at different layers than 90, the spec's layer scheme won't work without changing all existing dialog tscn files. CHECK THIS.
- **Pause menu at layer 101 + campaign log dropping to 50:** Currently campaign log is at 102 (above pause menu). If a player has campaign log open and presses Esc, the spec says Esc closes the screen first. But if campaign log is at 50 and pause menu overlay is at 101, does the pause menu's BackgroundOverlay intercept clicks intended for the campaign log's close button? The overlay has `mouse_filter` — check what it's set to.
- **Notification bar is a Control, not CanvasLayer:** The spec says it renders at "layer 75, same as top bar." But if it's reparented as a child of the top bar CanvasLayer, it inherits layer 75 automatically. The expanded_panel drops down from the notification bar — at layer 75 it's above screens (50) but below dialogs (90). Verify this is correct and the expanded panel doesn't need its own CanvasLayer.
- **Supply status calculation:** The spec says "Strained" between 1x and 1.5x capacity. Where is this threshold defined? Is 1.5x the existing attrition threshold in world_state.py, or is the spec inventing a new threshold? If it's new, it could diverge from actual game behavior.

## Output Format

Organize findings as:

### Critical (will cause crashes, data errors, or broken UI)
- **C1: [title]** — description, affected spec section, fix

### Design Gaps (spec is incomplete or ambiguous)
- **D1: [title]** — description, what needs deciding

### Minor (cosmetic, naming, or optimization)
- **M1: [title]** — description

End with a **Session Readiness** assessment: can each session be implemented as-written, or does the spec need amendments first?
