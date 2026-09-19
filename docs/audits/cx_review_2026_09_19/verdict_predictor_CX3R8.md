# VERDICT: CX3-R8 — **NARROWED**

**The row IS the largest text in the terminal, exactly as titled and by exactly
the ratio claimed — and the clause the lens used to give that fact weight is
false by measurement.**

* Tree: `f52df77f` (HEAD; row CX = `b4a27a15` … `727cf88a`). `git status` clean
  before and after — verified; Godot was run against the real project and wrote
  only to the already-present, ignored `.godot/` cache.
* Every number below is from a probe I ran, in
  `…/scratchpad/cx_review/probes/v_r8/`, against the **shipped 1805 board**
  (my own payload, `r8_payload.py` → `r8_payload.json`: 8 marshals / 4 enemies
  / 126 provinces off `world.get_filtered_game_state_summary()`; it matches the
  lens's own fixture byte-for-byte on all three rosters).
* Nothing under `backend/`, `godot-client/`, `tests/`, `docs/`, `tools/` was
  written.

---

## 1. THE TITLE CLAIM — **CONFIRMED, in the live scene**

`probes/v_r8/r8_fontsize.gd`, real `main.tscn` in Godot 4.4.1, real project
theme, real fonts:

```
CompletionRow exists          : true
CompletionRow has own override: false
CompletionRow normal_font_size: 16
OutputDisplay normal_font_size: 11  (override=true)
CommandInput  font_size       : 12  (override=true)
same font face row vs output  : true
theme resource on root        : res://ui/main_theme.tres
```

The 16 is not a guess about inheritance — it is `get_theme_font_size()` read off
the live node after `_ready()`, so it accounts for every cascade. The chain is
`project.godot [gui] theme/custom="res://ui/main_theme.tres"` →
`main_theme.tres:125 RichTextLabel/font_sizes/normal_font_size = 16`. No
`.gd` in the project calls `add_theme_font_size_override` on it; nothing at
runtime moves it.

Same font, three sizes, one panel:

```
   OutputDisplay  size 11  ascent 12.0px  line box 16.0px   'September 1805 …' width 209px
   CommandInput   size 12  ascent 13.0px  line box 17.0px   'September 1805 …' width 228px
   CompletionRow  size 16  ascent 17.0px  line box 22.0px   'September 1805 …' width 304px
```

## 2. THE EVIDENCE CLAIM — **CONFIRMED, and measured rather than eyeballed**

R8 says it is visible in `docs/audits/CX3_VERBS_X2_2026_09_19.png`. It is. I did
not take that on sight — whole-line ink bands are inflated by brackets and
descenders, so I compared **capitals only**, same frame, same glyph class
(`probes/v_r8/r8_png3.py`):

| glyph | node | size | ink height |
|---|---|---|---|
| `S` of *September 1805* | OutputDisplay | 11 | **14 px** |
| `N` of *Ney,* in the box | CommandInput | 12 | **16 px** |
| `N` of *Ney, attack* | **CompletionRow** | 16 | **21 px** |

21/14 = **1.50×** against the predicted 16/11 = 1.4545, and 21/16 = **1.31×**
against 16/12 = 1.333 — both inside one pixel of antialiasing. The suggestion
row's capitals are half again as tall as the game's own prose, and a third
taller than the line they complete.

## 3. PLAYER-REACHABLE — **YES**

`main.gd:660` connects `command_input.text_changed` → `_on_command_text_changed`
(`:917`), which calls `_refresh_suggestions()` whenever `history_index == -1` —
and `history_index` is `-1` by default (`:349`). `COMPLETIONS_ACTIVE := true`
(`:6870`). One keystroke in the command box and the row draws.

The client's 114-form diplomatic redirect is irrelevant here: this surface is
not a typed command, it is the client drawing itself. I confirmed it with my
own **windowed** (not headless) run — `probes/v_r8/r8_widest.gd` →
`R8_widest_shipped16.png`, the row rendered at 16 above a `Bernadotte, march to
c` command line — and the row's own committed frames show the same.

*Honest limitation recorded:* my keystroke arm (`r8_keystrokes.gd`) could not
prove this by synthetic input — under `--headless` an `InputEventKey` pushed at
the viewport does not reach a focused `Control`, and `insert_text_at_caret()`
does not emit `text_changed`. The reachability above rests on the signal wiring
plus the rendered frame, not on that arm.

## 4. SHIPPED BY ROW CX — **YES**

```
git show b4a27a15^:…/scripts/main.gd | grep -c _install_suggestion_row  ->  0
```

The node is new in `2c3535b5` (CX-3). Pre-existing is not available as a
defence. What *is* pre-existing is the terminal's own typography: both
overrides date to `92efe16c` (2026-01-09), seven months before the theme, and
survived the U2 sweep untouched — so the panel's 11/12 is the deliberate old
decision and the row simply never joined it.

---

## 5. THE SECOND CLAUSE — **REFUTED, on both halves**

> *"It is also what makes the widest real row wrap to two lines and trip
> CX3-R4."*

### (a) The row R4 names wraps at every size

`probes/v_r8/r8_fontsize.gd`, the 132-char row at the shipped 400×270 terminal
(box 494px):

```
   at size 16: text width 814px vs box 494px -> WRAPS
   at size 12: text width 611px vs box 494px -> WRAPS
   at size 11: text width 560px vs box 494px -> WRAPS
```

Not an estimate — `probes/v_r8/r8_counterfactual.gd` sets the override for real
and gives each arm its own settled frames (the naive `queue_sort()` read is the
never-laid-out 1px-wrap artefact and is worthless):

```
prefix 'Ney, march to A'  size 16 -> lines=2 …
prefix 'Ney, march to A'  size 12 -> lines=2 …
prefix 'Ney, march to A'  size 11 -> lines=2 …
```

**Two lines at 11.** The font size is not what wraps that row.

### (b) R4 trips at every size too

Same probe, panel growth against the hidden baseline (`vbox_min_h=305`):

```
prefix 'Ney, '            size 16 -> +30px   size 12 -> +25px   size 11 -> +24px
prefix 'Ney, march to A'  size 16 -> +52px   size 12 -> +42px   size 11 -> +40px
```

The panel grows — and the resize grip strands, and the map-label avoid rects go
stale — in **every** arm. Shrinking the row shrinks the jump by 6px. ⛔ **The
fix for R8 must not be recorded as closing R4.**

---

## 6. WHAT IS ACTUALLY TRUE INSTEAD (the narrowing, and it is worth more)

The clause the lens *could* have written is one it did not. Census of **every
realistic prefix** through the real `_build_completions` against the real board
— 8 marshals × 11 verbs × 26 letters, plus bare one- and two-letter prefixes —
composed exactly as `_render_suggestions` composes them, measured against the
row's real laid-out box (`probes/v_r8/r8_wrap_census.gd`):

```
BOX WIDTH (shipped 400x270 terminal, scale 1.0) = 494px
distinct rows censused            : 821
rows that WRAP at size 16 (shipped): 548  (66.7%)
rows that WRAP at size 12         : 456  (55.5%)
rows that WRAP at size 11         : 427  (52.0%)
rows the SIZE alone wraps (16 wraps, 11 would fit): 121
rows the SIZE alone wraps (16 wraps, 12 would fit):  92
```

So the size costs **121 of 821 rows (14.7%)** an extra line they would not
otherwise take — and the cheapest of them is the commonest thing a player will
ever type:

```
Bernadotte,   w16=684  w12=513  w11=470   (box 494)
     [Bernadotte, attack]   Bernadotte, march to   Bernadotte, move to   Bernadotte, scout   Bernadotte, fortify  (Tab)
```

A bare `<marshal>,` for the long names wraps at 16 and fits at 11. That is the
real charge, and 427 rows wrapping regardless is the reason the filed one is
wrong.

### 6a. And a correction to the sibling row R8 leans on

CX3-R4 publishes *"the widest real row is 132 chars → 2 lines / 44px."* It is
not the widest — that census read `Ney` and the board also holds `Bernadotte`.
The true widest is **177 chars**, and I rendered it rather than computing it
(`r8_widest.gd`, windowed):

```
SHIPPED (inherits 16): lines=3  row_h=66  panel=517x427  top=932
   [Bernadotte, march to Cagliari]   Bernadotte, march to Carniola   Bernadotte, march to Champagne   Bernadotte, march to Constantinople   Bernadotte, march to Copenhagen  (Tab)
WITH 11px OVERRIDE  : lines=2  row_h=32  panel=517x393  top=966
SHIPPED 16 @ scale 2.0: lines=3  row_h=66      (scale is inherited — the spec's claim holds)
```

**Three lines, 66px, the terminal 34px taller and its top edge 34px higher.**
R4's own worst case is one line worse than it published — evidence *for* R4,
found while refuting R8's use of it. Frames:
`probes/v_r8/R8_widest_shipped16_crop.png` vs `R8_widest_override11_crop.png`.

---

## 7. SEVERITY — **P4 is right, and the false clause is what would have raised it**

No mechanic, no data, no refusal, nothing unreadable or unreachable; the
completer works exactly as designed. The consequential harm the lens attached
to it belongs to R4 and fires at every size. What survives is a typography
inversion — a transient hint set half again larger than the prose it sits on
top of and than the line it completes — plus 14.7% of rows taking a line they
need not. P4.

## 8. WOULD THE FIX SHIP A REGRESSION? — **No pin reds; one caution**

* `grep -rn "add_theme_font_size_override\|theme_override_font" tests/` →
  **zero hits in the whole suite.** Nothing pins the row's size, in either
  direction.
* `test_cx3_the_predictor.py::test_it_draws_inside_the_terminal_not_on_a_canvas_layer`
  asserts `"CanvasLayer" not in install` plus two `in` assertions
  (`layout.add_child(...)`, `layout.move_child`). An added
  `_suggestion_row.add_theme_font_size_override("normal_font_size", …)` line
  satisfies all three.
* `test_ui2_part2_color_and_map.py:130` and `test_ui_visual_foundation.py:106`
  pin **the theme's** `RichTextLabel/normal_font_size = 16` and
  `default_font_size = 16`. An instance override does not touch the theme
  resource, so both hold. (Worth stating explicitly: the theme's 16 is a
  *pinned deliberate decision* from U2 Part 2 — the terminal's 11/12 is the
  local exception, and the row should join the panel it lives in, not the house
  default.)
* No `content_scale_factor` regression: the scale arm above shows 3 lines at
  1.0 and at 2.0 alike, because the override is logical and the scale is
  applied on top. The spec's §3.3 claim survives the fix untouched.

**Caution for whoever builds it: use 12, not 11.** The row's content *is*
command text and it sits directly above the line it completes, so 12 is the
neighbour that matters — and it buys 92 of the 121 rows anyway. And write on
the row, in the landing record, that **427 rows still wrap and R4 still fires**,
or the next reader will believe the two were closed together.

---

## 9. WHAT I COULD NOT BREAK

Said plainly, because my default verdict was REFUTED and these survived it:

* the 16 — read off the live node, not inferred from the `.tres`
* the 11 and the 12 — both real overrides, both in `main.tscn`, both live
* the PNG claim — 21px vs 14px vs 16px of measured ink, ratios matching to
  within antialiasing
* row CX's authorship — 0 occurrences of the installer pre-row
* reachability — one keystroke, and I rendered the frame myself
* the spec's `content_scale_factor` claim, which R8 does not dispute and which
  holds at 1.0 and 2.0 with and without the override
