# VERDICT — `CX3-R1` — **CONFIRMED, P2, narrowed in two places**

Baseline `f52df77f` (the row's last commit; `727cf88a` + a docs-only correction).
`git status` clean before and after. Nothing under `backend/`, `godot-client/`,
`tests/`, `docs/` or `tools/` was written. Probes in
`…/scratchpad/cx_review/probes/`.

Default verdict was REFUTED. It did not survive contact with the code.

---

## 1. WHAT I RAN — not the finder's probe

I did not trust the finder's port, and I did not trust their scene probe either.
I built a **third** instrument: `probes/v2_make_harness.py` slices the SHIPPED
function bodies out of `godot-client/project-sovereign/scripts/main.gd` **as
text** — `_build_completions`, `_add_addressee_or_bare`, `_add_verb_or_target`,
`_refresh_suggestions`, `_render_suggestions`, `_accept_suggestion`,
`_refresh_after_accept`, `_clear_suggestions`, `_on_command_text_changed`, the
four history functions, and the five constants (325 lines) — and pastes them
verbatim into a `SceneTree` script that **Godot 4.4.1 compiles and runs
headless** against a real `LineEdit` and a real `RichTextLabel`.

The only inputs the harness supplies are the two nodes the real scene supplies
and the payload the real backend supplies: `probes/v1_payload.py` boots
`europe_1805.json` in-process and dumps
`WorldState.get_filtered_game_state_summary()`, which is what `backend/main.py:517`
sends and what `_remember_game_state` stores.

```
player_nation : France
marshals (8)  : Bernadotte Davout Lannes Massena Murat Napoleon Ney Soult
enemies  (4)  : ArchdukeJohn Brunswick Deroy Mack
regions (126)
REGION PREFIX PAIRS: []   ENEMY PREFIX PAIRS: []   MARSHAL PREFIX PAIRS: []
ADDRESSEE PREFIX PAIRS: []   BARE PREFIX PAIRS: []
```

Run:
```
.venv/Scripts/python.exe probes/v1_payload.py
.venv/Scripts/python.exe probes/v2_make_harness.py
Godot_v4.4.1 --headless --path probes/gdproj --import
Godot_v4.4.1 --headless --path probes/gdproj --script res://harness.gd   # run1.txt
```

---

## 2. IT REPRODUCES — every row of the finder's table, exactly

Real Godot, shipped bytes (`run1.txt`):

```
typed "N"                offers ["Napoleon, ", "Ney, "]
  Tab x1 -> "Napoleon, "                offers ["Napoleon, attack ", …5]
  Tab x2 -> "Napoleon, attack "         offers [4 enemies]
  Tab x3 -> "Napoleon, attack Archduke John"   offers [1]
  Tab x4 -> "Napoleon, attack Archduke John"   (stuck)

typed "Ney, attack "     offers ["…Archduke John","…Brunswick","…Deroy","…Mack"]
  Tab x1..x4 -> "Ney, attack Archduke John"   every time

typed "Ney, march to "   offers [Albania, Alentejo, Algiers, Amsterdam, Anatolia]
  Tab x1..x4 -> "Ney, march to Albania"       every time

typed "Ney, m"           offers ["Ney, march to ", "Ney, move to "]
  Tab x1..x4 -> "Ney, march to "              ("move to" never reachable)

typed "e"                offers ["end turn", "economy"]
  Tab x1..x4 -> "end turn"                    ("economy" never reachable)
```

Census over the whole grammar (every 1- and 2-letter prefix, every
`<marshal>, `, every `<marshal>, <verb>`, `<marshal>, <verb> `, and
`<marshal>, <verb> <letter>`):

```
=== C. no history ===
  prefixes offering >=2 suggestions               : 760
  prefixes where Tab ever put offer #2 on the line: 0
=== C2. with a realistic 6-entry history ===
  prefixes offering >=2 suggestions               : 763
  prefixes where Tab ever put offer #2 on the line: 0
```

**760 / 0 — the finder's exact figure, arrived at independently.**

The mechanism is as read: `_accept_suggestion` advances `_suggestion_index` only
when `command_input.text` already equals the highlighted entry, and
`_refresh_after_accept` then rebuilds the list **from the text it just wrote**,
so every survivor begins with that text and the list collapses to one member.
Verified there is no second road: `_suggestion_row.mouse_filter =
Control.MOUSE_FILTER_IGNORE`, and `Utils.bbcode_color` emits `[color=#…]`, never
`[url=…]`, so the row carries no meta link and no `meta_clicked` handler exists.

---

## 3. NARROWING (a) — the cycle is NOT "dead by arithmetic". It fires, and it still delivers one line.

The finder wrote *"The cycle is dead by arithmetic on this map, not by
accident."* That is the one claim that does not survive. I went looking for the
input the finder's census could not contain — a line the player types that
**already equals** offer #1 — which needs history, and history is empty in a
port-and-prefix census.

`probes/v3_exception_census.py`, same harness (`run2.txt`):

```
seed "Ney, attack"   history ["Ney, attack"]
  shown 5: ["Ney, attack", "…Archduke John", "…Brunswick", "…Deroy", "…Mack"]
  offers REACHED by Tab: [2]      NEVER reachable: [1, 3, 4, 5]

seed "Ney, march to"  history ["Ney, march to"]
  offers REACHED by Tab: [2]      NEVER reachable: [1, 3, 4, 5]

bare-slotted-verb-in-history cases tried: 48   Tab reached offer #2 in: 48
                                               reached offer #3 in: 0
```

All 8 marshals × 6 slotted verbs = **48 of 48** reach offer #2. So the advance
branch is live code on the ordinary board, not dead arithmetic. It buys nothing:
the rebuild still collapses the list on the same press, so **offer #1 becomes the
unreachable one instead** and #3–#5 stay unreachable.

The invariant is therefore **simpler and stronger** than filed:

> Of the up-to-five offers the row draws, **exactly one can ever reach the
> command line. Never two. Which one depends on whether the typed line is
> already in history.** "Tab again walks the list" never happens on any input.

---

## 4. NARROWING (b) — "Up/Down are the history walk" is wrong about Down, and that matters

`_history_next` opens `if history_index == -1: return`. `_on_command_text_changed`
refreshes the list **only** when `history_index == -1`; the only writer that sets
it non-`-1` is `_history_previous`, whose last statement is `_clear_suggestions()`.
So **suggestions live ⟹ `history_index == -1` ⟹ Down is a measured no-op.**

Down is not "the history walk" in the state that matters — it is a free key. That
is the fix the finder did not name, and it is the conventional one.

---

## 5. THE FIXES — two of the three filed would ship a regression or achieve nothing

I implemented the finder's (a) and (c) against the same shipped body and measured
them over the whole grammar (`probes/v4_fix_regressions.py`, `run3.txt`).
"offers reachable overall" counts, across the 760 prefixes that show ≥2, how many
of the 3,224 drawn offers any number of Tab presses can put on the line.

```
variant=shipped  prefixes>=2=760  offer#2 reachable in 0    ALL reachable in 0    760/3224
variant=a        prefixes>=2=760  offer#2 reachable in 760  ALL reachable in 760  3224/3224
variant=c        prefixes>=2=760  offer#2 reachable in 0    ALL reachable in 0    760/3224
```

**Shipped: 760 of 3,224 drawn offers are reachable — 23.6%.**

**Fix (a), "do not re-narrow after an accept": it works (3,224/3,224) and it
destroys the behaviour the row documents.**

```
seed "N"
  [shipped] N -> "Napoleon, " -> "Napoleon, attack " -> "Napoleon, attack Archduke John"
  [a]       N -> "Napoleon, " -> "Ney, " -> "Napoleon, " -> "Ney, "      <-- forever
seed "Ney, "
  [shipped] -> "Ney, attack " -> "Ney, attack Archduke John"
  [a]       -> "Ney, attack " -> "Ney, march to " -> "Ney, move to " -> "Ney, scout "
```

`_refresh_after_accept`'s docstring states its whole purpose: *"Re-derive from
the newly filled line so the NEXT slot is offered immediately — type `ne`, Tab,
and the verbs are already there."* Under (a) the addressee slot oscillates
between `Napoleon, ` and `Ney, ` and **a verb is never offered** until the player
types a character. (a) buys the walk by selling the chain; it is a trade, not a
fix, and the record must say so.

**Fix (c), "cycle before rebuilding": measured IDENTICAL coverage to the shipped
code — it fixes nothing — and it makes every Tab after the first skip the
highlighted entry.**

```
seed "Ney, "  [c] -> "Ney, attack " -> "Ney, attack Brunswick"   (skips Archduke John, the gold-bracketed one)
seed "Ney, m" [c] -> "Ney, march to " -> "Ney, march to Alentejo" (skips Albania, the gold-bracketed one)
```

**Fix (b) is the survivable shape**, with a correction: take **Down** (proved
free in §4), not Shift+Tab — Shift+Tab is Godot's `ui_focus_prev`, so taking it
is a second taking, which is exactly what
`test_tab_is_the_accept_key_and_was_free`'s docstring ("nothing was taken from
the player") is about. And write the new arm as a **separate `elif` above** the
existing one: any shape that edits the existing line into
`elif event.keycode == KEY_TAB and not event.shift_pressed and _accept_suggestion():`
**reds that pin**, which asserts the literal string
`"elif event.keycode == KEY_TAB and _accept_suggestion():" in source`.

---

## 6. SHIPPED BY ROW CX — yes, and invisible to the suite by construction

`git show b4a27a15^:…/main.gd | grep -c "_accept_suggestion\|_suggestions"` → **0**.
The whole predictor is CX-3 (`2c3535b5`). Plain Tab was previously unhandled in
`_on_command_input_gui_input` and fell through to `ui_focus_next`, so the row took
nothing — it added a feature whose advertised second half does not exist.

Nothing in the suite can see it. The only two references to `_accept_suggestion`
in `tests/` are **source-text censuses**
(`test_accepting_a_completion_never_sends_it` asserts `"send_command" not in
accept`; `test_tab_is_the_accept_key_and_was_free` asserts a literal line), and
the one mutation in `tools/_sweep_cx.json` that touches the pair
(`CX3-7 "the completer sends instead of filling"`) only proves the never-sends
census binds. **No test anywhere drives the accept state machine**, which is why
23,618 green tests say nothing.

---

## 7. PLAYER-REACHABLE — yes

`_install_suggestion_row()` is called at `main.gd:659` in `_ready`;
`COMPLETIONS_ACTIVE` is `const true`; `command_input.text_changed` and
`command_input.gui_input` are both connected there. Plain Tab carries
`alt_pressed == false`, so it passes the `_SCREEN_HOTKEYS` and `_alt_game_key`
arms above it and lands on the `KEY_TAB` arm whenever the command line has focus
— the client's dominant state. This is a keypress, not a command, so `main.gd`'s
114-form diplomatic redirect is not in the path.

---

## 8. SEVERITY — P2 stands, and here is the argument against it

For P3: nothing is destroyed, no AP is spent, no state is corrupted, nothing is
mis-parsed, and Tab still does something defensible (it walks the slot chain).
The player can always keep typing.

For P2, which is where I land: the game **draws** up to five entries, brackets
one in gold, dims the other four, and prints the hint `(Tab)` beside them — an
affordance for a selection that no input the client accepts can make. Three
documents and the function's own docstring state behaviour the code does not
have (`COMMAND_EXPERIENCE_SPEC.md:366`, commit `2c3535b5`, `_accept_suggestion`'s
docstring, and the rendered row). The project graded the July-25 "command
terminal swallowed the mouse wheel" at P2 — the same family: an input affordance
the game advertises and does not honour. And the concrete cases are ordinary:
`N` + Tab addresses **Napoleon** with `Ney, ` sitting visibly in the dimmed list
and no key that reaches it; `Ney, march to ` + Tab fills **Albania**, the
alphabetically first of 126 provinces.

It is CX-3's own headline rule one layer out. The row's census proves *the game
must not offer a sentence it cannot read*; what it did not check is that **the
game must not offer a sentence the player cannot select.**

---

## 9. WHAT THE PIN MUST BE

Not another source census — the row already has two on this function and both
are green about the defect. The pin has to **drive the state machine**: from a
list of N drawn offers, assert every entry can be placed on the line by some
sequence of accepted keys. The suite is Python and this is GDScript, so it needs
the Godot-side harness idiom the project already owns (IQ-10's
`tools/iq10_surface_screenshot.gd` / the parse harness), or the slice-and-compile
shape in `probes/v2_make_harness.py`. A 20-line GDScript check run by the parse
harness would have caught this before it shipped, and would have caught fix (c)
too.
