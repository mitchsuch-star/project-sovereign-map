# Codex Audit: Diplomatic Ledger War Bargains Tab

## Context

The War Bargains system (WB-A through WB-D) is complete with ~160 backend tests. Gate 2 smoke test (`tools/gate2_smoke_test.py`) passes 59/59 checks. However, the diplomatic ledger's Godot UI was missing a 5th tab to display war bargain data that the backend already sends. This audit covers the wiring that closes that gap.

## What Changed

### Files Modified

1. **`godot-client/project-sovereign/scenes/diplomatic_ledger.tscn`**
   - Added `BargainsTab` Button node under `SubTabRow` (after `TalleyrandTab`)

2. **`godot-client/project-sovereign/scripts/diplomatic_ledger.gd`**
   - Added `@onready var bargains_tab` reference
   - Extended `tab_buttons` array to include 5th tab
   - Added `KEY_5` input handling for tab switching
   - Added `open_to_war_bargains(api_client)` method (opens tab index 4)
   - Added `_render_war_bargains()` renderer: splits bargains into live (active/triggered) and completed sections, renders each with status color, badge, enemy, claim region, cooldown
   - Added `_format_bargain_entry(b)` helper for per-bargain BBCode rendering
   - Updated render dispatch `match` to include case `4`

3. **`godot-client/project-sovereign/scripts/top_bar.gd`**
   - Added `ledger_war_bargains` case in `open_diplomatic_ledger_review()` routing to call `open_to_war_bargains()`

4. **`docs/STATUS.md`**
   - Added session entry documenting the change

## Audit Checklist

### Scene Tree Integrity
- [ ] `BargainsTab` node path matches `@onready` reference: `$PanelContainer/VBoxContainer/SubTabRow/BargainsTab`
- [ ] Node type is `Button` with `layout_mode = 2` and `theme_override_font_sizes/font_size = 12`, consistent with sibling tabs
- [ ] No `.uid` or resource ID conflicts with existing nodes

### Tab Wiring Completeness
- [ ] `tab_buttons` array has exactly 5 entries: `[nations_tab, treaties_tab, threat_tab, talleyrand_tab, bargains_tab]`
- [ ] All 5 buttons get `pressed.connect(_on_tab_pressed.bind(i))` in `_ready()` loop
- [ ] `_update_tab_highlights()` iterates all 5 tabs correctly (no hardcoded range)
- [ ] `KEY_5` is handled in `_input()` and calls `_switch_tab(4)`
- [ ] `_render_current_tab()` match statement includes case `4: _render_war_bargains()`

### Data Contract
- [ ] `_render_war_bargains()` reads `cached_data.get("war_bargains", [])` — matches the backend key from `build_diplomatic_ledger()` in `backend/game_logic/diplomatic_ledger.py`
- [ ] Backend `_build_war_bargains()` calls `get_all_bargains_for_ledger(world)` which returns dicts with keys: `bargain_id`, `promiser`, `beneficiary`, `named_enemy`, `claim_region`, `status`, `source_treaty`, `created_turn`, `ended_turn`, `badge`, `end_reason`, `cooldown_remaining`
- [ ] Renderer uses `b.get("key", default)` pattern (never raw indexing) for all fields
- [ ] All integer fields passed to display are wrapped in `int()` (Godot float safety)
- [ ] `status` values handled: `active`, `triggered`, `fulfilled`, `breached`, `void` — verify no unknown status causes a silent render gap

### Notification Review Routing
- [ ] `top_bar.gd::open_diplomatic_ledger_review()` handles `"ledger_war_bargains"` before the generic `open()` fallback
- [ ] It checks `node.has_method("open_to_war_bargains")` before calling
- [ ] Notification rail bargain events in `commitments_routing.py` use `review_target: "ledger_war_bargains"` — verify these are: `bargain_fulfilled`, `bargain_voided`, `bargain_ratified`, `bargain_triggered`
- [ ] `bargain_breached` uses `review_target: "diplomacy_wizard"` (NOT ledger) — confirm this is intentional (opens the Propose Redress wizard flow, not the ledger)

### Render Quality
- [ ] Live bargains (active/triggered) render in a separate section from completed bargains (fulfilled/breached/void)
- [ ] Status colors are visually distinct and match the game's existing palette conventions (blue=info, amber=warning, green=success, red=error, grey=neutral)
- [ ] Badge display (honoured/broken/lapsed) matches the `get_all_bargains_for_ledger()` badge contract
- [ ] Empty state ("No war bargains recorded") displays correctly when `war_bargains` array is empty
- [ ] `end_reason` underscores are replaced with spaces for display
- [ ] Cooldown display only shows when `cooldown_remaining > 0`

### Edge Cases
- [ ] Opening ledger when no bargains exist shows empty state, not a crash
- [ ] Tab switching from bargains tab to other tabs and back preserves scroll position reset (`scroll_container.scroll_vertical = 0` in `_switch_tab`)
- [ ] `close_view()` clears `cached_data` and `_open_review_target` — bargains tab state doesn't leak
- [ ] Pre-Peace-Deals saves (no `war_bargains` key in ledger response) fall back to empty array via `.get("war_bargains", [])`

### Omissions to Flag (Not Bugs)
- [ ] No bargain creation/interaction from the ledger tab — view-only, consistent with other ledger tabs
- [ ] No sort/filter controls — acceptable for v0.1
- [ ] Tab text "WAR BARGAINS" may need visual sizing check if 5 tabs crowd the SubTabRow on smaller resolutions

## Backend Reference

The backend data contract is in:
- `backend/game_logic/diplomatic_ledger.py` line 62: `"war_bargains": _build_war_bargains(world)`
- `backend/game_logic/diplomacy.py` function `get_all_bargains_for_ledger()` (line ~5915)
- `backend/game_logic/commitments_routing.py` lines ~115-160: event routing with `review_target` assignments

## How to Run

```bash
# Gate 2 smoke test (offline + live)
.venv\Scripts\python.exe tools/gate2_smoke_test.py

# Full test suite
.venv\Scripts\python.exe -m pytest tests/ -q --tb=no

# Godot — manual: open diplomatic ledger (D key), press 5 or click WAR BARGAINS tab
```
