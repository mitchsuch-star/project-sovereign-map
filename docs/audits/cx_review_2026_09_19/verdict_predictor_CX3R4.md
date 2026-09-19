# VERDICT — CX3-R4 · **NARROWED**

**Lens:** predictor · **Filed severity:** P3 · **My verdict:** the mechanism is
real and reproduces, the magnitude is **understated by up to 73%**, the
landing spot is **wrong**, the "re-creating the stranding the docstring was
written to prevent" framing is **wrong in the direction that matters** (that
stranding is already live, permanent, and larger, on pre-CX code), and the
defect is **conditional and self-cancelling** in two ways the finding does not
state.

Tree at `727cf88a` (probes also valid at `f52df77f`, which touches no `.gd`).
`git status` clean before and after. Nothing under `backend/`,
`godot-client/`, `tests/`, `docs/` or `tools/` was written.

My probes (mine, not the ones I was handed), all real `main.tscn` in Godot
4.4.1 headless:
`probes/ref_r4_layout.gd` · `ref_r4_layout2.gd` · `ref_r4_layout3.gd` ·
`ref_r4_layout5.gd` · `ref_r4_fixshape.gd`

---

## 1. WHAT REPRODUCES — exactly as filed

`ref_r4_layout2.gd`, shipped default terminal 400×270, Interface Scale 1.0,
viewport 1920×1080, the real signal path (`_on_command_text_changed`, the
handler `LineEdit.text_changed` calls):

```
=== A. SHIPPED DEFAULT 400x270, scale 1.0 ===
  row HIDDEN, grip glued     panel 517x353 top=717 | row_h=0  | grip y=707 want=707 DRIFT=(0,0)  | avoid_top=718 (off by -1)
  row SHOWN  (5 suggestions) panel 517x383 top=687 | row_h=22 | grip y=707 want=677 DRIFT=(0,30) | avoid_top=718 (off by -31)
```

Confirmed, all of it:

* `BottomLeftUI` is clamped **up** to its combined minimum (517×353 against a
  400×270 request), so the row does not clip — it grows the panel and, being
  bottom-anchored, the growth goes **upward**.
* `_position_resize_grip` is not re-run. The grip stays at y 707 while the
  corner it must straddle moves to 687.
* `_push_map_label_avoid_rects` is not re-run. The map is still told the panel
  begins at 718 while it begins at 687.
* Nothing watches the panel: the only `resized` connection in the file is on
  the root window (`main.gd:678-679`). Verified by grep — four hits, all the
  root-window pair and `_on_root_resized` itself.
* Reachable by an ordinary player through the shipped client with no backend,
  no parser and no driver: type one character that yields a suggestion. This
  is not a typed-road defect, so `main.gd`'s 114 diplomatic redirects are not
  in the path. A fresh install has no `user://ui_settings.cfg`, so
  `get_terminal_*` return `DEFAULT_TERMINAL_WIDTH/HEIGHT = 400/270` and the
  defect is present out of the box.

---

## 2. WHERE THE FINDING IS WRONG

### (a) The magnitude is understated. 30px is the FLOOR; the real figure is 52.

The finding measured one prefix (`Ney, `, the verb slot). The row is
autowrapped, and on the real 126-province board **every prefix with a target
slot wraps to two lines**. `ref_r4_layout5.gd`, provinces read from the
committed `assets/maps/europe.json` (126 loaded):

```
prefix               sugg  lines  row_h   panel_top  GRIP DRIFT y
"N"                  2     1      22      687        30
"Ney, "              5     1      22      687        30
"Ney, attack "       4     2      44      665        52
"Ney, m"             2     1      22      687        30
"Ney, march to "     5     2      44      665        52
"Ney, march to A"    5     2      44      665        52
"Ney, march to S"    5     2      44      665        52
"Ney, support "      5     2      44      665        52
"Ney, garrison "     5     2      44      665        52
```

Four of the twelve verbs in `_MARSHAL_VERBS` take a target slot, and **all four
cost 52px**, not 30. The finding's own §5 measured the 132-char two-line row
and then reported the one-line number.

### (b) "entirely off the corner and onto the header" is not where it lands.

Measured at the worst case (`ref_r4_layout5.gd`, drift 52):

```
WORST CASE 'Ney, march to ': panel top=665 right=527  grip=(517,707 20x20)  drift=52
   MinimizeButton   rect=(445,707 38x60)
   ScaleUpButton    rect=(409,707 32x29)
   Header           rect=(34,689 469x117)
```

The grip spans x 517–537. The Header's own rect ends at x 503; MinimizeButton
ends at 483; ScaleUpButton at 441. **The grip intersects no button and not the
header's rect** — it lands in the 12px `MainMargin` right strip plus the panel
border, i.e. glued to the panel's right EDGE, 30–52px below the corner. It is
visibly detached and it is the wrong place, but **nothing is covered, no click
is stolen, and dragging still works** (the grip takes input where it draws).
`ref_r4_layout2.gd` reports `sits on: nothing` at both 30 and 52px.

### (c) The framing is backwards: that stranding is ALREADY LIVE, PERMANENT, and LARGER.

This is the finding's real error. `ref_r4_layout3.gd` arm I — the completion
row **never shown**, pure pre-CX code path:

```
=== I. PRE-EXISTING header growth, with the CX row NEVER shown ===
  gold=1,200 inf=80,000 (glued)       panel top=717 right=527 | grip DRIFT=(0,0)   | avoid right=527  STALE=(dx 0)
  gold=88,556 inf=189,000 cav=42,500  panel top=717 right=547 | grip DRIFT=(-20,0) | avoid right=527  STALE=(dx 20)
```

The header's own status labels are the panel's binding minimum-**width**
constraint. `gold_value.text = _format_number(gold)` (`main.gd:4314`, and at
**pre-CX `main.gd:4228` verbatim** — `git show b4a27a15^`) grows them every
time the purse or a manpower pool crosses a digit, and re-glues nothing.
Realistic late-campaign values move the corner 20px; seven-digit values move it
42px (`ref_r4_layout.gd` Q5, `DRIFT=(-70,0)` on a wider starting panel).

`_position_resize_grip` has exactly the same two reachable call sites before
row CX as after (`git show b4a27a15^:…/main.gd` → 1256, 1287, and
`_reposition_after_layout`). **CX-3 did not re-create the stranding. It added a
second, transient, smaller trigger to a class that already had a permanent,
larger one.** Any record of this row must say so, or the fix will be scoped to
the wrong half.

*Honest note on a comparator I expected to fire and which did not:* the
`OpenEnvoysButton` visibility toggle (`main.gd:4290`, also pre-CX) moves
**nothing** — the `InputSection` is not the binding width constraint
(`ref_r4_layout2.gd` arm E: 559 → 559, drift 0,0). I report it because I filed
it as the obvious pre-existing comparator and it was wrong.

---

## 3. WHERE IT NARROWS

### (d) It vanishes above a dragged terminal height of 383px — including on the machine that shipped it.

`ref_r4_layout3.gd` arm B′ (the finding's own probe could not see this; the v2
attempt read `get_global_rect()` in the same frame as the visibility flip, and
a `Container` re-sorts on a **deferred** call, so it reported "MOVES 0px" for
every height including 270 — invalid, redone with a frame gap):

```
  requested h=180    panel top: hidden=717  shown=687   ROW MOVES IT 30px
  requested h=270    panel top: hidden=717  shown=687   ROW MOVES IT 30px
  requested h=340    panel top: hidden=717  shown=687   ROW MOVES IT 30px
  requested h=353    panel top: hidden=717  shown=687   ROW MOVES IT 30px
  requested h=365    panel top: hidden=705  shown=687   ROW MOVES IT 18px
  requested h=375    panel top: hidden=695  shown=687   ROW MOVES IT 8px
  requested h=383    panel top: hidden=687  shown=687   ROW MOVES IT 0px
  requested h=400    panel top: hidden=670  shown=670   ROW MOVES IT 0px
  requested h=500    panel top: hidden=570  shown=570   ROW MOVES IT 0px
```

The defect exists only while the requested height is under the row-shown
minimum. The shipped default (270) is inside the band. **This machine's saved
config is 434×422** (`ref_r4_layout2.gd` printed it) — outside the band, drift
exactly zero, which is why ten committed evidence frames and a live visual pass
never showed it.

### (e) It self-cancels on the ordinary cycle.

`ref_r4_layout3.gd` arm H, the real Enter path
(`_add_to_history` → `_clear_suggestions`):

```
  idle, glued                  grip DRIFT=(0,0)  STALE=(dx 0, dy 0)
  typing -> row UP             grip DRIFT=(0,30) STALE=(dx 0, dy 30)
  after Enter (row down again) grip DRIFT=(0,0)  STALE=(dx 0, dy 0)
```

The drift lasts exactly as long as a suggestion is on screen and is gone the
instant the player submits or clears the line. It does not accumulate. The
finding's "on the keystroke that opens the list and again on the one that
closes it" is right about the jump but does not say that the second jump is
the **repair**.

### (f) The 2.0 numbers hold, re-measured through the real path.

The finding's probe set `content_scale_factor` directly, bypassing
`_apply_ui_scale`. Through `_main._apply_ui_scale(2.0, false)`
(`ref_r4_layout2.gd` arm F): `panel 542x351 top=179` → `542x381 top=149`,
`DRIFT=(0,30)`, avoid off by 28. Same logical 30px. No correction needed.

---

## 4. ONE THING THAT IS WORSE THAN FILED

The **hide** direction can leave the grip off the panel entirely
(`ref_r4_layout2.gd` arm C):

```
  re-glued while row is up     panel top=687 | grip y=677 DRIFT=(0,0)
  row HIDDEN again             panel top=717 | grip y=677 DRIFT=(0,-30)
      grip rect=(517,677 20x20)  overlaps-panel=false
```

Grip 30px **above** the corner, floating on the map, `MOUSE_FILTER_STOP` — a
map click in that 20×20 square starts a terminal resize drag. It needs a
compound sequence (row up → A+ / window resize / minimize-restore → clear the
line), so it is rarer than the main case, but it is the only arm where
something is actually taken from the player.

---

## 5. SEVERITY

**Split, and P3 overall is defensible only because of the second half.**

* **The grip half is P4.** Cosmetic, self-cancelling, blocks nothing, steals no
  click, and no function is lost — the handle still drags where it is drawn.
* **The avoid-rect half stays P3.** `_nudge_clear_of_avoid_rects`
  (`map_label_layer.gd`) parks a label **flush against** the avoid rect's edge,
  so a label nudged clear of the old top is now 30–52px *inside* the new panel;
  the label layer carries `z_index = 50` against `BottomLeftUI`'s 0 and both
  are siblings on the same canvas, so it draws **over** the terminal. No
  redraw is needed for the symptom — the already-drawn label simply stops being
  above the panel. That is the July-25 live-pass defect's own channel, and
  because the nudge parks flush the overlap is likely rather than incidental.

---

## 6. WOULD THE SUGGESTED FIX SHIP A REGRESSION?

**No pin reds.** The only two pins that mention this machinery are presence-only
source censuses — `tests/test_ui_scale_expandable_terminal.py::test_main_wires_resize_grip_and_drag`
(asserts `func _create_resize_grip` / `_on_grip_gui_input` / `_resize_terminal_from_mouse`
/ `double_click` / `_reset_terminal_size` are present) and
`tests/test_map_slice8_balance.py:334` (a token list containing `"resize_grip"`).
Neither counts call sites; both survive either shape. I looked for a census pin
that would forbid a new caller and there is none.

**But the finding offers two shapes and they are not equivalent — build the
second, not the first.**

* *Shape 1, `_render_suggestions` ends with `_reposition_after_layout()`*:
  runs on **every keystroke**, and `_push_map_label_avoid_rects` →
  `set_ui_avoid_rects` → `queue_redraw()` on the label layer, whose `_draw`
  does a `font.get_string_size` and a greedy overlap test **per label** over
  126 provinces. A full label re-layout per character typed, to fix a size that
  changes on maybe two keystrokes in a sentence. It also fixes only the CX
  instance and leaves §2(c)'s permanent one standing.
* *Shape 2, connect `bottom_left_ui.resized` once*: measured
  (`ref_r4_fixshape.gd`) —

  ```
    keystroke 'N' (row appears, 1 line)                      fired 1 time(s)
    keystroke 'e' (row still 1 line, same height)            fired 0 time(s)
    'Ney, ' (row still 1 line)                               fired 0 time(s)
    'Ney, attack ' (row grows to 2 lines)                    fired 1 time(s)
    line cleared (row hides)                                 fired 1 time(s)
    PRE-EXISTING: gold/inf labels grow (no completion row)   fired 1 time(s)
  ```

  It fires only when the size really changes, costs nothing on the other
  keystrokes, and **closes the pre-CX header-growth instance for free**.
  `_reposition_after_layout` only `call_deferred`s, so there is no re-entrancy
  hazard connecting it to a signal emitted during layout.

**The pin to write is not "the row calls reposition".** It is *the grip's
position and the pushed avoid rect agree with `bottom_left_ui.get_global_rect()`
after the panel's size changes for ANY reason* — driven at 400×270 (inside the
band) and with the header labels grown, or it will pass on the developer's own
422px terminal and miss both halves exactly as the row's evidence did.

---

## 7. ONE CLAIM OF THE FINDING'S I COULD NOT REPRODUCE

The recorded hazard — "in the frame the row goes hidden→visible it has never
been laid out, so autowrap wraps at 1px width and it claims 81 lines /
1782px". `ref_r4_layout3.gd` arm J, reading in the same frame as the flip:

```
  SAME FRAME as the flip: panel h=353  row min_h=44  row lines=2
  ONE stage later        : panel h=405  row min_h=44  row lines=2
```

No balloon. The row's minimum is 44 in the flip frame and the panel has not yet
grown at all. The finding was right not to file it; it is not reproducible here
either.
