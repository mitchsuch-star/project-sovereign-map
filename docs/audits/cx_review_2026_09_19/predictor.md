# LENS 4 — ATTACK THE PREDICTOR AND ITS CENSUS (CX-3)

Baseline `727cf88a`, clean. (HEAD moved to `f52df77f` while I worked — docs +
`test_cx1_*` only; it touches nothing in this lens, so every finding below
stands at HEAD. An untracked `harm.json` appeared in the repo root during the
run; it is not mine and I did not touch it.)

Probes: `…/scratchpad/cx_review/probes/`. Nothing under `backend/`,
`godot-client/`, `tests/`, `docs/` or `tools/` was written; `git status`
verified clean at the end except for the file above.

---

## THE SHORT VERSION

**The census the row is proudest of came back green, and I could not break it.**
4,229 completer lines through the real parser: **0** action mismatches, **0**
wrong addressees. 213 through the real `/command` executor: **0**
cannot-read refusals. The fog claim holds by measurement — 14 enemy marshals
alive on the 1805 boot, **4** in the payload, **10 fogged names the completer
can never say**.

**The defect is not in what it offers. It is in what it does when you press the
key it tells you to press.**

> **The row shows five suggestions and exactly one of them can be put on the
> command line — by Tab, by mouse, by anything.** Measured in the real scene in
> Godot, not in a port. And the second-ranked verb it offers, submitted,
> **spends an action point and marches the marshal at Mack.**

---

## 1. THE CANDIDATES — the census holds (and this is the honest headline)

I ported `_build_completions`, `_add_addressee_or_bare`, `_add_verb_or_target`,
`_starts_with_ci`, `Utils.humanize_entity_name` and the Tab state machine to
Python (`probes/completer_port.py`), enumerated the **whole candidate universe**
— not the five shown for one prefix, the union over every prefix — and drove it.

Ground truth first (`probes/p1_payload.py`). The completer's source is
`world.get_filtered_game_state_summary()` (`backend/main.py:517`), **not**
`get_llm_game_state()` as `_visible_enemy_names`'s docstring claims:

| | |
|---|---|
| `marshals` | 8 — Bernadotte, Davout, Lannes, Massena, Murat, Napoleon, Ney, Soult |
| `enemies` | 4 — ArchdukeJohn, Brunswick, Deroy, Mack |
| `map_data` | 126 province names, all display-ready, 0 camelCase, 0 non-alpha |

**`probes/p2_parse_census.py` — 4,229 candidates through the real parser:**

```
ACTION MISMATCH (0):
WRONG ADDRESSEE (0):
TARGET DRIFT / MISSING (8):
   verb='attack' resolved-target='ArchdukeJohn'  x8
   'Ney, attack Archduke John' offered='Archduke John' -> target='ArchdukeJohn'
        action='attack' success=True
```

The only "drift" is the NPC-1 key normalisation, which is correct.

**`probes/p3_exec_census.py` — 213 through the real `/command`** (two marshals ×
every verb × own location / two adjacent / three far / every enemy / every other
marshal, **plus all 126 provinces for `march to`**):

```
*** CANNOT-READ REFUSALS (0) ***
```

**The fog claim is real, not asserted** (`probes/p12_fog_and_history.py`):

```
enemy marshals ALIVE in the world : 14
enemy marshals in client payload  : ['ArchdukeJohn','Brunswick','Deroy','Mack']
FOGGED (never offered) : Abdurrahman, ArchdukeCharles, Armfelt, Buxhowden,
                         Castanos, Damas, Frederick, Hohenlohe, Kutuzov, Moore
```

`ArchdukeCharles` — the name the commit message says would leak through a
persisted history — is measurably absent from the live roster. That decision
was right.

**Port-dependence:** this section's breadth rests on the port. I verified it by
reading `main.gd:6981-7078` line by line, and the two findings below that matter
most were then reproduced **in Godot against the shipped `.gd`**, not the port.

---

## 2. `CX3-R1` — **P2. The row offers five. One is reachable. By anything.**

### Reproduced in the real scene

`probes/cx3_tab_probe2.gd`, real `main.tscn` in Godot 4.4.1 headless, real
`_accept_suggestion`, Tab pushed as a real `InputEventKey` through the viewport:

```
[D] offers = ["Ney, attack Brunswick", "Ney, attack Deroy", "Ney, attack Mack"]
[D] Tab x1 -> Ney, attack Brunswick   offers now ["Ney, attack Brunswick"]
[D] Tab x2 -> Ney, attack Brunswick   offers now ["Ney, attack Brunswick"]
[D] Tab x3 -> Ney, attack Brunswick
```

### And censused over the whole board

`probes/p4_tab_walk.py`, every one- and two-letter prefix plus every
`<marshal>, <verb> <letter>`:

```
prefixes offering >=2 suggestions : 760
prefixes where Tab ever reached #2: 0
```

### Why

`_accept_suggestion` advances the highlight only when the line **already equals**
the highlighted entry:

```gdscript
if command_input.text == str(_suggestions[_suggestion_index]):
    _suggestion_index = (_suggestion_index + 1) % _suggestions.size()
command_input.text = str(_suggestions[_suggestion_index])
_refresh_after_accept()
```

…and `_refresh_after_accept` then **rebuilds the list from the text it just
wrote**. Every surviving entry must begin with that text, so the rebuilt list
has exactly one member — unless one candidate's name is a strict prefix of
another's. Measured on the shipped board:

```
REGION PREFIX PAIRS: []      ENEMY PREFIX PAIRS: []      MARSHAL PREFIX PAIRS: []
```

Zero. The cycle is dead by arithmetic on this map, not by accident.

Nor is there another road: `_suggestion_row.mouse_filter =
Control.MOUSE_FILTER_IGNORE` (not clickable), and Up/Down are the history walk.
**Suggestions 2–5 are unreachable by any input the client accepts.**

### What the player gets

| they type | Tab gives them | they wanted |
|---|---|---|
| `N` | `Napoleon, ` | often `Ney, ` — and there is no way back but editing |
| `Ney, ` | `Ney, attack ` | the other four verbs are decoration |
| `Ney, m` | `Ney, march to ` | `move to` is in the list and unreachable |
| `Ney, attack ` | `Ney, attack Archduke John` (alphabetically first) | whoever they meant |
| `Ney, march to ` | **`Ney, march to Albania`** | anywhere on the correct continent |

### The claims it falsifies

* commit `2c3535b5`: *"Tab accepts, Tab again walks the list."*
* `COMMAND_EXPERIENCE_SPEC.md` §3.3: *"**Tab** accepts; Tab again walks the list."*
* `_accept_suggestion`'s own docstring: *"Tab takes the highlighted line; Tab again walks the list."*
* the rendered row itself, which prints five entries and the hint `(Tab)`.

### Suggested fix

Three shapes, cheapest first. (a) Do not re-narrow after an accept: keep the
list the player is choosing from until they type. (b) Give the walk its own key
— Down while the list is up, or Shift+Tab — and leave Tab as accept-only.
(c) Cycle **before** rebuilding: `_suggestion_index` advance on every Tab press,
not only when the line already matches. Whichever is chosen, the pin must be
*"from a list of N, every entry can be placed on the line"*, driven by the
executor-level state machine — a test that only asks what `_build_completions`
returns cannot see this.

---

## 3. `CX3-R2` — **P2. The second offer costs an AP and marches him at Mack.**

`Ney, march to ` — the exact string with the trailing space that
`_add_verb_or_target` writes, one Tab away from typing `Ney, ma` — submitted at
the real `/command` (`probes/p11_verbslot_cost.py`):

```
the completer's offer    AP      ok     modal raised       standing order left
'Ney, attack '           4->3    True   -                  -
'Ney, march to '         4->3    True   pending_interrupt  ? -> Swabia (path=['Swabia'])
'Ney, move to '          4->4    True   -                  -
'Ney, scout '            4->3    True   -                  -
'Ney, hold'              4->2    True   -                  ? -> Rhineland (path=[])
'Ney, garrison '         4->4    False  -                  -
```

```
 'Ney, march to '  AP 4->3  modal=pending_interrupt
   order: ? -> Swabia (path=['Swabia'])
   msg  : Ney: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?'
   pending_interrupt: {'marshal':'Ney','interrupt_type':'contact_bad_odds',
     'enemy':'Mack','location':'Swabia','is_first_step':True,
     'options':['attack_anyway','go_around','hold_position','cancel_order']}
```

Swabia is Bavaria-held with Mack's 52,000 in it. **The player named no
destination.** `march to` is a strategic keyword, a bare one parses
`target='generic'` (`backend/ai/generic_targets.py` — a designed sentinel), and
the strategic path resolves it to the nearest contact.

The sibling in the **same list** degrades correctly: `Ney, move to ` costs
**0 AP** and answers *"Where shall Ney march, Sire? He stands at Rhineland."*
Two adjacent offers, one free and honest, one that buys a fight.

`Ney, hold` costs **2 AP** and lands a standing order with a false disclosure
(see `CX3-R10`).

### Why the census cannot see it

`test_every_marshal_verb_parses_to_the_action_it_claims` builds
`f"{marshal}, {verb}" + (f" {target}" if target else "")` — for a slotted verb
it **always** appends a target. The string the completer actually puts on the
line, `"<Marshal>, <verb> "`, is never driven, at the parser or the executor.
That is the one shape of the row's own rule the row did not test.

**Honest attribution:** the parse is pre-existing. What CX-3 shipped is making
it a one-keystroke product and ranking it **second for every marshal on the
board**. Nobody typed `Ney, march to ` and stopped before; now Tab does.

### Suggested fix

Extend the pin to the verb-slot strings themselves, at the executor, asserting
0 AP and no standing order. Then either make the bare strategic verb free and
ask (`move to`'s behaviour is the model), or have the completer not leave a
slotted verb on the line as an accepted state — accept straight to
`<verb> <first target>`, or hold the accept until a target is chosen.

---

## 4. `CX3-R3` — **P3. The completer is empty on the route back into a campaign.**

`_last_game_state` is written **only** by `_remember_game_state`, called only
from `_update_map_from_game_state` (`main.gd:883`). The connection-test boot
path does not reach it:

```gdscript
# main.gd:745-752
if response.has("game_state") and response.game_state.has("map_data"):
    if _initial_map_bootstrapped:
        _update_map_from_game_state(response.game_state)   # false at boot
    else:
        _pending_initial_map_data = response.game_state.map_data.duplicate(true)
        _try_finalize_initial_map_bootstrap()              # never remembers
```

`_initial_map_bootstrapped` is false until `_try_finalize_initial_map_bootstrap`
sets it, and that runs *inside* this else-branch, so the true arm is
unreachable on a fresh scene.

With an empty board (`probes/p4_tab_walk.py` arm E):

```
typed 'N'              -> []
typed 'Ney'            -> []
typed 'Ney, '          -> []
typed 'Ney, attack '   -> []
typed 'st'             -> ['status']
```

**Reachable, and by the only route back:** `_on_pause_main_menu_requested`
(`main.gd:838`) sets `MenuBoot.pending_action = ""`, and
`_consume_menu_boot_action`'s `_:` arm is `pass`. So every time the player
visits the Main Menu mid-campaign and takes *Return to the War Room*, the
completer is dead until their next command returns. Begin / Continue / Load /
tutorial all populate it via `_apply_world_swap_response` → `_sync_response_hud`
(`main.gd:5119`), so those are fine. A first command that takes a
`_pre_hud_response_routes` early return (objection, glorious charge) also does
not populate it, because that route returns before `_sync_response_hud`.

**Fix:** call `_remember_game_state(response.game_state)` in the else-branch too
— one line, above the `duplicate`.

---

## 5. `CX3-R4` — **P3. The row resizes the terminal, and two consumers of that size are never told.**

`BottomLeftUI` is a **PanelContainer**, and `_position_resize_grip`'s own
docstring says why that matters:

> *"BottomLeftUI is a PanelContainer, so it **clamps up to its combined minimum
> size** (header + output + input row), and A+ text scale enlarges that min —
> the grip must follow the real top-right corner, not the requested footprint,
> **or it strands mid-panel**."*

CX-3 added a fourth contributor to that minimum and ran neither consumer.
Measured in the real scene (`probes/cx3_layout_probe2.gd`, Godot headless):

```
400x270 s1.0  row HIDDEN   panel=542x353 top=717  vbox_min_h=305  grip_y=708
400x270 s1.0  row SHOWN    panel=542x383 top=687  vbox_min_h=335  grip_y=708
400x270 s2.0  row HIDDEN   panel=542x351 top=179  vbox_min_h=303  grip_y=167
400x270 s2.0  row SHOWN    panel=542x381 top=149  vbox_min_h=333  grip_y=167
```

* The panel is **30px taller and its top edge 30px higher** whenever a
  suggestion exists, and back when the last one goes — so the header and the
  output text jump on the keystroke that opens the list and on the one that
  closes it. (The command line itself does **not** move: the panel is
  bottom-anchored. That is the saving grace.)
* **The grip is stranded exactly as its docstring warned** — it stays at
  `y=708` while the corner it should straddle moves to `687`. The grip is
  20×20 placed at `corner − 10`, so 21px adrift puts it entirely off the corner
  and onto the header. 18px adrift at Interface Scale 2.0.
* `_push_map_label_avoid_rects` — *"Pushed after every layout pass because the
  panel is resizable"* — is likewise not re-run, so a map label can draw over
  the 30px the terminal just grew into. That is the July-25 live-pass defect's
  own channel.

The only `resized` connection in `main.gd` is on the **root window**
(`main.gd:679`). Nothing watches the panel.

**Fix:** `_render_suggestions` (both arms) ends with `_reposition_after_layout()`
— or connect `bottom_left_ui.resized` to it once, which fixes the whole class.

### Answering the lens's question directly

**No, five long suggestions do not clip or push the input off screen**, and the
reason is not the row's design — it is that `BottomLeftUI` cannot shrink to the
400×270 default (let alone the 300×180 the grip allows) because its own button
row (`Execute` / `⚖ Diplomacy` / `End Turn (E)`) has a minimum width of ~517px.
At 469px of usable width the widest real row is **132 chars → 2 lines / 44px**:

```
row char length : 132
row text        :   [Ney, march to Albania]   Ney, march to Alentejo   Ney, march
                    to Algiers   Ney, march to Amsterdam   Ney, march to Anatolia  (Tab)
CompletionRow line count : 2   content_h 44
```

Interface Scale changes nothing here, because `content_scale_factor` scales
logical→physical and leaves the logical wrap identical. Measured at 1.0, 1.75
and 2.0: 2 lines each time. **The row genuinely does inherit the scale, as
claimed.** It overflows *height*, not width, and the PanelContainer absorbs it
by growing — which is `CX3-R4`.

One first-frame artefact I will **not** file as a defect because I could not
prove it reaches a drawn frame: in the frame the row goes hidden→visible it has
never been laid out, so autowrap wraps at 1px width and it claims
`81 lines / 1782px` (`vbox_min_h=2095` against a 373px box). Godot's deferred
container sort almost certainly lands before draw. Recorded as a hazard, not a
finding.

---

## 6. `CX3-R5` — **P3. The census exempts a string the parser reads as a command.**

`TestTheGameCanReadWhatItPrints.NOT_COMMANDS` holds seven strings. I drove all
seven anyway (`probes/p5_census_scope.py`, `probes/p6_exemption_and_nouns.py`):

```
'Bravest of the Brave'      success=False action=None
'Child of Victory'          success=False action=None
'Drillmaster of Boulogne'   success=True  action='drill'   <== READS AS A COMMAND
'Eyes on a Crown'           success=False action=None
'First Horseman of Europe'  success=False action=None
'Iron Resolve'              success=False action=None
'Roland of the Army'        success=False action=None
```

At the executor it stages a clarification: *"Which marshal shall carry out this
order, Sire?"* — the verb fires on the bare substring `drill` inside
`Drillmaster`, which is **CX-5's own shape** (*"the retreat is sometimes a
noun"*), one slice over and still live.

The list's only pin, `test_the_exemption_list_is_not_a_wildcard`, checks that
each exempt string **appears in the body**. It never checks the exemption is
*justified*. The docstring says the allowlist exists so *"a NEW non-command
string fails the census until somebody says what it is"* — but nobody checked
whether the seven already there were non-commands.

I scanned every name the game prints — 126 provinces + 8 marshals + 4 visible
enemies + the 7 ability names — for an embedded verb. **`Drillmaster of
Boulogne` is the only one.** So the list is one row wrong, not rotten.

**Fix:** one line in the existing test — every `NOT_COMMANDS` member must ALSO
fail to parse as an action. It turns the allowlist from an assertion into a
proof.

---

## 7. `CX3-R6` — **P3. Tab's meaning is state-dependent, and the empty case takes focus away silently.**

Measured in the real scene (`probes/cx3_tab_probe2.gd`):

```
[A] text='Ney, '   suggestions=5  focus BEFORE Tab=CommandInput
[A] after Tab: text=Ney, attack   focus=CommandInput
[B] text='Ney, attack Mack at once'  suggestions=0  focus BEFORE Tab=CommandInput
[B] after Tab: text=unchanged  focus=SendButton   <== focus left the command line
```

`elif event.keycode == KEY_TAB and _accept_suggestion()` consumes Tab **only
when a suggestion exists**. Otherwise it falls through to Godot's
`ui_focus_next`, which is live (`project.godot` overrides no input map, and
`main.tscn` sets no `focus_mode`). So a player who has learned *"Tab completes"*
will press it on a line with nothing to complete and silently lose the caret to
**Execute** — after which typed characters go nowhere.

Two riders: `Shift+Tab` is not checked either (`shift_pressed` is ignored), so
focus-*prev* is also gone whenever a suggestion exists; and
`_accept_suggestion()` is invoked **as an `elif` condition with side effects**,
which is legal but reads as a predicate.

`test_tab_is_the_accept_key_and_was_free`'s assertion is about `main.gd`'s own
handling and is true there. Its **conclusion** — *"nothing was taken from the
player to make room for it"* — is false, because the binding it displaces is the
engine's, not the file's.

**Fix:** consume `KEY_TAB` unconditionally in the command line (call
`accept_event()` whether or not a suggestion was accepted); decide Shift+Tab
deliberately.

---

## 8. `CX3-R7` — **P3. After one Up, the completer is dead for the rest of the line.**

```gdscript
func _on_command_text_changed(_text: String) -> void:
    if history_index == -1:
        _refresh_suggestions()
```

`history_index` returns to `-1` only from `_history_next`'s off-the-end branch
or `_add_to_history`. So one Up press disables the predictor until the player
walks all the way back down or submits something. Simulated from the ported
semantics (`probes/p12_fog_and_history.py`) — there is no headless way to press
Up, the same limit the shipped `TestTheHistoryWalk` states:

```
typed 'n'   completer_live = True
Up          completer_live = False   idx = 2
retype all  completer_live = False   <-- stays dead for the rest of the line
Down, then type -> completer_live = True
```

**Fix:** in `_on_command_text_changed`, treat a keystroke as leaving history —
set `history_index = -1`, clear `_history_anchor`, refresh. That is also what
makes `CX3-R7b` below go away.

### `CX3-R7b` — P4, the walk is not the idiom it names

`_history_pool` freezes the prefix in `_history_anchor` at the first Up. The
docstring calls this *"the standard shell idiom"*; readline's
`history-search-backward` re-reads the **current line** on every press. Measured
consequence: recall, edit the line to something else, press Up — the visible
prefix is ignored and the frozen one is walked.

```
1. typed 'ney'         -> pool ['Ney, fortify','Ney, attack Mack','Ney, march to Swabia']
4. select-all + type   -> line 'status now, please'  idx=1
   ...and the pool Up will walk is still ['Ney, fortify', …]
5. Up                  -> line 'Ney, fortify'   <-- the typed text is gone
6. Down, Down          -> line 'Ney, march to Swabia'
```

Defensible as written (the freeze is what makes Down's restore coherent), but
the record should not call it the shell idiom. I found **no index-out-of-range
and no wrong-pool crash**: the pool is constant for the duration of a walk
because `command_history` cannot change mid-walk and the anchor is assigned from
the same string the entry pool was built from.

Cosmetic sibling: `_history_previous` calls `_clear_suggestions()`,
`_history_next` does not — so Down-off-the-end restores the typed prefix with no
completion row until the next keystroke.

---

## 9. `CX3-R8` — **P4. The row is the largest text in the terminal.**

It sets no `theme_override_font_sizes`, so it inherits
`main_theme.tres:125 RichTextLabel/font_sizes/normal_font_size = 16` — against
`OutputDisplay`'s explicit **11** and `CommandInput`'s explicit **12**. Visible
in the committed evidence: in `CX3_VERBS_X2_2026_09_19.png` the suggestion line
is plainly larger than *"September 1805 — The War of the Third Coalition"*
above it and than `Ney,` in the box below it. It is also what makes the widest
row wrap to two lines and trip `CX3-R4`.

---

## 10. `CX3-R9` — **P4. The committed evidence cannot show the widest real row.**

`tools/cx3_completer_screenshot.gd` stubs the board:

```gdscript
"map_data": { "Swabia":…, "Saxony":…, "Savoy":…, "Lorraine":…, "Rhineland":… },
"enemies":  { "Mack":…, "ArchdukeJohn":… },
```

Five provinces against the shipped **126**, two enemies against four. So
`["region", "Ney, march to S"]` can offer at most three short lines where the
shipped board offers five long ones, and the widest row the game can produce —
the 132-character, two-line one I measured — was never on screen. The capture
also reads the developer's saved terminal size out of `user://ui_settings.cfg`
rather than pinning the shipped default, so the panel width in the frames is
whatever this machine had.

The claim the frames *do* support is the important one and it holds: the row
draws inside the terminal's VBox and inherits `content_scale_factor`.

**Fix:** have the capture scene take the roster from a committed payload fixture
(`probes/payload_1805.json` is one, 126 regions), and call
`_apply_terminal_size(UiSettings.DEFAULT_TERMINAL_WIDTH, …)` before shooting.

---

## 11. `CX3-R10` — **P4. `Ney, hold` prints a substitution that never happened.**

```
'Ney, hold'  -> "Ney will hold Rhineland. Holding position.
                 (Our maps read Rhineland as the province nearest your order, Sire.)"
```

`movement_executor.destination_grounding_note` returns the disclosure whenever
the resolved name's tokens are absent from the raw text — and has no branch for
*the player named no province at all*. Pre-existing; CX-3 makes it routine by
putting `hold` in the top-five verbs for every marshal (and it costs 2 AP).

---

## 12. WHERE THE CENSUS'S EDGE IS (scope, not a defect)

The regex `"([^"\n]{3,70})"` is adequate **on today's body** — measured: 0
single-quoted, 0 backticked, 0 curly-quoted, 0 strings over 70 chars, 0 under 3.
Nothing is being missed by the quoting form.

What the census does not read is anything outside `_execute_help`'s message.
Three other producers print command-shaped strings (`probes/p7_offered_elsewhere.py`):

| producer | measured |
|---|---|
| the client's own boot help, `main.gd` | `Ney, attack Mack` ✓ · `scout Swabia` ✓ · `move to Flanders` ✓ (clarifies) · `end turn` ✓ · **`recruit` → refused at boot**: *"No marshal is available to receive reinforcements, Sire."* |
| Berthier's shrug | `'Ney, attack Mack'` ✓ · `'Ney, march to Lorraine'` ✓ · *"Valid actions include: attack, move, scout, defend, fortify, **recruit**"* — same refusal |
| `tutorial_overlay.gd` suggest chips | 11 strings, tutorial-scenario names (Kienmayer, Senarmont, Jellacic); out of this census by construction |

`recruit` is a **gate** refusal, not a vocabulary one, and the spec's own §1 draws
that line (*"a chip removes naming risk, never gate risk"*) — so I file it P4, not
as an IQ10-6 instance. It is still worth knowing that the sentence a confused
player is handed names an action that will refuse them on turn 1.

I checked and **withdrew** one candidate: `change stance`, printed unquoted in
`ALLOWED: move, recruit, defend, wait, change stance`, does not parse — but that
row lists action *categories* (`attack`, `move`, `defend` sit beside it), and the
real phrasing is documented and quoted three lines up as `"Ney, go aggressive"`,
which parses and is censused. Not a defect.

---

## 13. ONE MORE, TINY

`_add_verb_or_target(marshal, rest, prefix, out, seen)` never reads `prefix`.
Harmless; noted because the signature implies the slot logic consults the whole
typed line, and it does not.

---

## 14. WHAT I COULD NOT BREAK

Said plainly, because the lens's default verdict is *wrong until reproduced* and
these survived the attempt:

* the verb table — 4,229 lines, real parser, **0** mismatches
* the same table at the real executor — **0** cannot-read refusals, including
  all 126 provinces for `march to`
* the fog boundary — 10 of 14 live enemy marshals are unreachable through the
  completer, by construction
* the decision not to persist history — `ArchdukeCharles` is measurably fogged
  at boot, so the stated leak was real
* `content_scale_factor` inheritance — 2 lines at 1.0, 1.75 and 2.0 alike
* the addressee comma, the dedupe, the `slot == "M"` self-exclusion, and the
  `_history_pool` index arithmetic (no out-of-range reachable)
