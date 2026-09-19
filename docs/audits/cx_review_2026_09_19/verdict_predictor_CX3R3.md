# VERDICT: CX3-R3 — **CONFIRMED** (title narrowed in two words)

Default verdict was REFUTED. It did not survive. I reproduced it myself, in
the **real `main.tscn` under Godot 4.4.1 headless, against a real backend on
the shipped 1805 board**, with **no stub board installed** — and a contrast
arm proves the fault is the route, not the feature.

Baseline: `f52df77f` (HEAD; `727cf88a` plus a docs/test-only commit that
touches no `.gd`). Repo `git status` clean before and after. Probes:
`…/scratchpad/cx_review/probes/verdict_r3/`.

---

## 1. MY REPRODUCTION

Backend: `SOVEREIGN_PORT=8011 LLM_MODE=mock INK_IRON_SAVE_DIR=<scratch>` —
default 1805 world. Client: `godot --headless --path godot-client/project-sovereign
--script …/r3_boot.gd`, which instantiates the **real** `res://scenes/main.tscn`
and sets `MenuBoot` to exactly what `main_menu.gd::_launch("")` leaves behind.

### Arm A — the Return-to-the-War-Room state (`pending_action = ""`)

```
[r3] f3    _initial_map_bootstrapped=false  _last_game_state.size=0  history=0
[r3] f60   _initial_map_bootstrapped=false  _last_game_state.size=0  history=0
[r3] f120  _initial_map_bootstrapped=true   _last_game_state.size=0  history=0
[r3] f900  _initial_map_bootstrapped=true   _last_game_state.size=0  history=0

======== SETTLED STATE (frame 900) ========
_initial_map_bootstrapped : true
map_area.visible          : true          <-- the MAP is fine; only the board is lost
_last_game_state.size()   : 0
  marshals  : []      enemies : []      regions : 0

  typed 'N'                -> []
  typed 'Ney'              -> []
  typed 'Ney, '            -> []
  typed 'Ney, attack '     -> []
  typed 'Ney, march to S'  -> []
  typed 'Dav'              -> []
  typed 'st'               -> ["status"]
  typed 'end'              -> ["end turn"]
  typed 'e'                -> ["end turn", "economy"]

  _suggestions : []     row visible : false
```

### Arm B — the Begin state (`pending_action = "new_game"`), same probe, same backend

```
[r3] f120  _initial_map_bootstrapped=true  _last_game_state.size=16
  marshals : ["Bernadotte","Davout","Lannes","Massena","Murat","Napoleon","Ney","Soult"]
  enemies  : ["Archduke John","Brunswick","Deroy","Mack"]     regions : 126

  typed 'Ney, '           -> ["Ney, attack ","Ney, march to ","Ney, move to ","Ney, scout ","Ney, fortify"]
  typed 'Ney, attack '    -> ["Ney, attack Archduke John", …, "Ney, attack Mack"]
  typed 'Ney, march to S' -> ["Ney, march to Samogitia", …, "Ney, march to Silesia"]
  row visible : true
```

**The mechanism is confirmed to the frame.** `_initial_map_bootstrapped` is
measurably `false` from f3 through f60 and only flips between f60 and f120 —
long after `_on_connection_test` ran, because the topology request that flips
it is issued *inside* `_on_connection_test` (`main.gd:741`). So the true arm
at `main.gd:747-748` is unreachable on a fresh scene, exactly as filed, and
the else-arm (`:749-752`) stores `map_data` and never remembers the state.

### The data was on the wire and was thrown away

`probes/p_test_payload.py`, live backend:

```
GET /test      game_state: marshals 8 · enemies 4 · map_data 126
POST /command  game_state: marshals 8 · enemies 4 · map_data 126
  marshals  /test == /command keys : True (8 vs 8)
  enemies   /test == /command keys : True (4 vs 4)
  map_data  /test == /command keys : True (126 vs 126)
```

`/test` (`backend/main.py:2601`) serves `world.get_filtered_game_state_summary()`
— **the same fog-filtered builder** `/command` serves. The boot handler already
reads that payload for five other consumers (`action_summary`, `gold`,
`manpower_pools`, `_process_active_wars`, `tutorial_overlay.on_world_swap`)
and for `game_state.map_data` itself. Only the completer's board is dropped.

### How long the defect lasts — measured, not assumed

`probes/r3_selfheal.gd` (Return arm, then one real `_execute_command()`):

```
[heal] BEFORE cmd  size=0   'Ney, '->[]   'N'->[]
[heal] f340        size=16  'Ney, '->["Ney, attack ", …]   'N'->["Napoleon, ","Ney, "]
[heal] AFTER  cmd  size=16  (unchanged)
```

One ordinary command restores it fully. The window is bounded: **from the
Return until the first command's response lands.**

---

## 2. WHERE THE FILED ROW OVER-REACHES (two words, both in the title)

* **"empty" is wrong; "boardless" is right.** My own run shows the five
  `_BARE_COMMANDS` still complete (`st`→`status`, `end`→`end turn`,
  `e`→`end turn`/`economy`). What is gone is everything derived from the
  board: **0 of 8 marshals, 0 of 4 visible enemies, 0 of 126 provinces** —
  and any prefix containing a comma returns `[]`, because `_build_completions`
  can match no addressee and falls through to `_add_addressee_or_bare`, which
  a `"Ney, "` prefix cannot satisfy. The lens's own body says this (`'st' ->
  ['status']`); only its title says "empty".
* **"the only route back into a live campaign" over-claims.** It is the only
  route back into the *running in-memory* world. A player can also press
  **Continue** and re-enter from the autosave — `/load` answers through
  `build_base_response` → `_apply_world_swap_response` → `_sync_response_hud`,
  which populates. The defect is scoped to the one route that deliberately
  avoids a load.

Everything else in the row — mechanism, line numbers, reachability,
attribution, severity and fix — reproduced as written. (Trivially: the row
cites `main.gd:838` for `MenuBoot.pending_action = ""`; at HEAD `:838` is
`came_from_game = true` and `:839` is the `pending_action` line. Navigate by
symbol, per the project's own standing rule.)

---

## 3. SEVERITY — **P3 stands.** Not P2, not P4.

Against P2: nothing mechanical breaks. `map_area.visible == true` in my own
Return-arm run; the HUD, the map, the tutor card and every typed command work.
No fog leak, no lost state, no soft-lock, and it self-heals after one command.

Against P4: this is the row's **headline feature**, silently dead on a route
a player reaches with two always-enabled buttons, and dead precisely for the
first command after returning — the moment a player who has been away in a
menu most needs the naming help. The surface gives no sign: the row simply
does not appear, which is indistinguishable from "I typed something with no
completions".

---

## 4. PLAYER-REACHABLE THROUGH THE SHIPPED CLIENT — **YES**

Not a typed-road defect, so `main.gd`'s diplomatic-keyword redirect is not in
play. The route is two buttons, both shipped and unconditionally enabled:

* `pause_menu.gd:122 _on_main_menu()` → `main_menu_requested.emit()` (`:124`),
  wired at `main.gd:547` to `_on_pause_main_menu_requested` (`main.gd:834`),
  which sets `came_from_game = true` (`:838`) and `pending_action = ""` (`:839`).
* `main_menu.gd:229` adds **"Return to the War Room"** whenever
  `came_from_game` — `_add_menu_button("return", …, true)`, always enabled —
  → `_on_return_pressed` (`:422`) → `_launch("")` (`:483`).
* Back in `main.tscn`, `_consume_menu_boot_action` matches `""` against
  `"new_game" / "tutorial" / "continue" / "load"` and falls to `_: pass`.

I verified the four *other* arms are unaffected: `new_game` measured
populating (arm B above); `tutorial` takes the same `_on_new_game_result`
path; `continue`/`load` take `_apply_world_swap_response` → `_sync_response_hud`.

---

## 5. SHIPPED BY ROW CX — **YES, by CX-3 `2c3535b5`**

```
git show b4a27a15^:…/main.gd | grep -c "_last_game_state"   ->  0
_remember_game_state occurrences:  b4a27a15 -> 0 · 5fc3d5c8 -> 0 · 2c3535b5 -> 2
```

`_last_game_state`, `_remember_game_state` and `_build_completions` did not
exist before row CX. The `_initial_map_bootstrapped` two-arm gate **is**
pre-existing (pre-row `main.gd:730`, post-row `:747`) — but it was inert,
because there was nothing to remember. CX-3 added the consumer and wired it to
one of the two arms. This is the row's own recurring shape one layer out:
*a new reader attached to the busy path and not to the quiet one.*

---

## 6. WOULD THE SUGGESTED FIX SHIP A REGRESSION? — **No. I looked for one.**

The fix is `_remember_game_state(response.game_state)` on the boot path.

* **Fog leak?** No — measured. `/test`'s `game_state` is key-identical to
  `/command`'s on all three rosters (8/4/126), from the same
  `get_filtered_game_state_summary()`. This was the sharpest attack available
  and it fails.
* **A pin it would red?** None. A grep over `tests/` finds exactly one file
  touching any of this machinery and one relevant assertion:
  `test_the_enemy_roster_comes_from_the_fog_filtered_payload` requires
  `_last_game_state.get("enemies"` inside `_visible_enemy_names` and forbids
  `get_enemies_of_nation` anywhere in the source. Adding a call site touches
  neither. No call-site census exists over `_remember_game_state`.
* **A stale board during a world swap?** Checked; closed by construction. Both
  swap arms call `set_input_enabled(false)` *first* (`main.gd:6792` new game,
  `:6804` tutorial), so the player cannot type in the window where `/test`'s
  board would briefly precede the tutorial's own roster, and
  `_sync_response_hud` overwrites it on the same round trip.
* **Crash risk?** `_remember_game_state` guards `if game_state is Dictionary`
  and never touches `map_area`, the only thing that can be null here.

**One improvement on the filed shape.** The row says "in the else-branch too".
Site it at the **head of the `main.gd:744` block instead**, covering both arms
— the true arm already remembers via `_update_map_from_game_state`, so a later
change that makes that arm reachable cannot re-open the gap.

**And the pin must drive the boot path.** The row's own capture scene,
`tools/cx3_completer_screenshot.gd`, hand-installs `_main._last_game_state =
STATE` at frame 60 — so the committed visual evidence
(`docs/audits/CX3_*_2026_09_19.png`) is **structurally incapable** of showing
this, and so is any pin that begins by assigning the board. The falsifiable
assertion is: *boot the scene the way the menu boots it, ask nothing else of
it, and `_own_marshal_names()` is non-empty.*
