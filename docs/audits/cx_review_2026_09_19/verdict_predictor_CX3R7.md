# VERDICT — `CX3-R7` · **CONFIRMED at P3**, and the mechanism is worse than filed

Refuter pass on lens `predictor`'s row. Default verdict was REFUTED; it did not
survive contact. Baseline `727cf88a` (HEAD `f52df77f`, docs-only above it —
nothing in this lens's reach). Read-only throughout: `git status` clean, nothing
written under `backend/`, `godot-client/`, `tests/`, `docs/` or `tools/`.

**Probes (mine, all in real headless Godot 4.4.1 against the real `main.tscn`):**
`probes/rf/rf1_history.gd`, `rf2_history.gd`, `rf3_fixb.gd`, `rf4_narrow.gd`;
outputs `rf1_out.txt` … `rf4_out.txt`.

| | |
|---|---|
| verdict | **CONFIRMED** |
| severity | **P3 — as filed.** Not P2: nothing is misexecuted, nothing lies, no state is lost that was not already lost pre-row. |
| player-reachable | **YES**, on the row's own measured ~47.5% of lines |
| shipped by row CX | **YES — CX-3, commit `2c3535b5`**, by construction |
| filed fix | **would ship a measured regression.** A narrower one would not. |

---

## 1. THE REPORT'S OWN STATED LIMITATION IS FALSE — I PRESSED UP

The row says *"there is no headless way to press Up"* and files the reproduction
as **simulated from a Python port**. The shipped test class repeats the claim as
its justification:

> `tests/test_cx3_the_predictor.py:309` — *"The client half, pinned by reading
> the source — there is no headless way to press Up in this project, and the
> alternative is no pin at all."*

There is. The same `root.push_input(InputEventKey)` the lens already used for
**Tab** reaches `_on_command_input_gui_input`, and `KEY_UP` is handled four
lines below `KEY_TAB` in that one function. Thirty lines of GDScript. Everything
below is measured on the real scene with real key events, never a port.

---

## 2. THE REPRODUCTION I RAN — the ORDINARY sequence, not "retype all"

The filed repro retypes the whole line. The ordinary thing a player does with a
shell history is *recall the last order and change its target*. `rf4_narrow.gd`,
shipped code, real keys:

```
=== SHIPPED — recall `Ney, attack Mack`, retarget to Brunswick ===
  [typed "ney, a"]      offers=["Ney, attack Mack", "Ney, attack "]   visible=true
  [Up]                  text="Ney, attack Mack"   idx=0   offers=[]   visible=false
  [4 x Backspace]       text="Ney, attack "       idx=0   offers=[]   visible=false
  [typed "Bru"]         text="Ney, attack Bru"    idx=0   offers=[]   visible=false
```

`rf2_history.gd` measured what a live completer *would* have offered at those two
moments — `["Ney, attack Mack", "Ney, attack Brunswick", "Ney, attack Deroy"]`
and then **`["Ney, attack Brunswick"]`, a single unambiguous completion**. The
row is dead at exactly the keystroke it exists for.

And it does not recover. `rf1_history.gd` clears the line to empty with 40
backspaces and retypes a full fresh prefix:

```
[C after clearing the line]   text=""              hist_idx=2  suggestions=0
[C retyped a FULL prefix]     text="ney, attack "  hist_idx=2  suggestions=0
    _build_completions would offer: ["Ney, attack Mack", "Ney, attack Brunswick", "Ney, attack Deroy"]
```

**Backspace reaches the handler** (`text_changed` emissions from one backspace:
**1**), so the handler is entered and the guard is what refuses. "Dead for the
rest of the line" is exact. The escapes are: submit the line (`_add_to_history`,
measured to restore it), or press Down — which **discards what you typed** and
restores the pre-Up prefix.

---

## 3. WHY IT IS WORSE THAN FILED — the guard cannot do what its docstring says

```gdscript
func _on_command_text_changed(_text: String) -> void:
    """CX-3: … Reaching into history leaves `history_index` set, and a walk
    must not re-open the list under the line it just filled."""
    if history_index == -1:
        _refresh_suggestions()
```

`rf1_history.gd` arm (A) connects a counter to `text_changed` and assigns the
text programmatically, the way every walk and `_accept_suggestion` does:

```
=== (A) programmatic `text =` ===
    text_changed emissions from assignment: 0
```

**Godot's `LineEdit` does not emit `text_changed` on a programmatic
`set_text`.** So a walk filling the line *cannot* re-open the list, with or
without the guard. The stated danger is structurally unreachable; the guard's
only reachable effect is the defect. This is not a trade-off that was made and
went wrong — it is a guard against nothing.

Two more facts make it a single point of failure:

* **`_refresh_suggestions()` has exactly ONE caller in the entire client** —
  `main.gd:922`, inside this guard. (`_refresh_after_accept` rebuilds inline.)
  Everything the completer is rests on that one guarded line.
* **No Python test names `_on_command_text_changed`.** Grep over `tests/`:
  zero hits. Nothing pins it in either direction.

### Why it shipped invisible

`tools/cx3_completer_screenshot.gd`, the row's own committed evidence harness,
does this:

```gdscript
_main.command_input.text = str(entry[1])
_main.command_input.caret_column = ...
_main._refresh_suggestions()          # called BY HAND
```

Given arm (A)'s measured **0** emissions, the harness never once entered
`_on_command_text_changed`. The five committed `CX3_*_2026_09_19.png` would be
byte-identical with the guard present, absent, or the whole function deleted.
The evidence proves the row renders; it is blind by construction to the path a
player takes. That is the finding's real lesson, and it is this project's own
recorded one — *construct the ordinary case, not the convenient one.*

---

## 4. SEVERITY — P3 is right, and I tried to move it both ways

**Not P2.** No wrong order is issued, no figure is misreported, the CX-3 census
guarantee ("the game must not offer a sentence it cannot read") is untouched —
a silent completer offers nothing, so it cannot offer something unreadable. The
harm ceiling is *the player types the rest of the line unaided*, which is what
they did before CX-3 existed. Down's discard of typed text looks like data loss
but is **pre-existing in kind and strictly milder than pre-row**: `b4a27a15^`'s
`_history_next` set `command_input.text = ""` — it blanked the line outright.

**Not P4.** The feature is not degraded, it is *entirely off*, with no
indication why, on the path the row itself costed as the most common one.

## 5. PLAYER-REACHABLE — yes, in the row's own currency

Nothing here touches the backend; it is pure client, on the focused command
line the client re-grabs at every control-return tail. `main.gd`'s 114-form
diplomatic redirect is irrelevant — no command is submitted.

The spec §5 table prices the prefix-filtered history at a **47.5% hit rate**
over the 1,416 archived commands and raised `MAX_HISTORY` 10 → 50 *because* of
it. By the row's own model roughly half of all typed lines begin with an Up
press, and the completer is dead on every one of them from that press until
submission. Two of CX-3's three headline features are mutually exclusive within
a line.

## 6. SHIPPED BY ROW CX — yes, by construction

`git show b4a27a15^:…/main.gd` has **no** `_on_command_text_changed`, **no**
`_history_anchor`, **no** `_refresh_suggestions`, **no** `text_changed`
connection. Bisected across the row:

```
b4a27a15  _on_command_text_changed=0  _history_anchor=0
5fc3d5c8  _on_command_text_changed=0  _history_anchor=0
2c3535b5  _on_command_text_changed=3  _history_anchor=6   <-- CX-3
```

There was no completer to kill before CX-3. The interaction is wholly this row's.

---

## 7. ⛔ THE FILED FIX SHIPS A REGRESSION — measured

The row prescribes: *"in `_on_command_text_changed`, treat a keystroke as leaving
history — set `history_index = -1`, clear `_history_anchor`, refresh."*

`rf3_fixb.gd` runs the identical keys under three arms. Same board, same
history, the only difference is the fix:

```
=== ARM 0 — SHIPPED ===
  [typed "ney"]   idx=-1  offers=4
  [Up x1]         text="Ney, march to Swabia"   idx=2
  [edited "!"]    text="Ney, march to Swabia!"  idx=2
  [Up x2]         text="Ney, attack Mack"       idx=1     <-- the walk climbs

=== ARM 1 — THE FILED FIX ===
  [Up x1]         text="Ney, march to Swabia"   idx=2
  [edited "!"]    text="Ney, march to Swabia!"  idx=-1
  [Up x2]         text="Ney, march to Swabia!"  idx=-1    <-- nothing
  [Up x3]         text="Ney, march to Swabia!"  idx=-1    <-- nothing
```

**The filed fix trades a dead completer for a dead history walk.** Once
`history_index` is -1, `_history_previous` re-derives the pool from the *visible*
line; an edited line prefix-matches nothing, `pool.is_empty()` returns, and Up
is inert for the rest of the line. It does not close the hole, it moves it —
and it moves it onto the very feature the row measured at 47.5%.

It also quietly settles the sibling `CX3-R7b` in the wrong direction: R7b wants
the walk to re-read the current line, and ARM 1 *is* that behaviour. The two
siblings are in tension and the report does not notice.

**No shipped pin reds either way** — `TestTheHistoryWalk` pins the bodies of
`_history_pool`/`_history_previous`/`_history_next`, which neither fix touches,
and nothing names `_on_command_text_changed`. So "reds no pin" is not evidence of
safety here; the regression is invisible to the suite, exactly as the defect was.

### The fix that measures clean

Drop the guard — refresh unconditionally — and **do not touch `history_index`**.
Given arm (A), the guard protects nothing, and `_accept_suggestion`'s hand-picked
`_suggestion_index` is safe because its assignment emits nothing either.

```
=== ARM 2 — NARROW FIX (rf3) ===
  [Up x2 after the edit]  text="Ney, attack Mack"  idx=1   <-- byte-identical to ARM 0

=== NARROW FIX on the ordinary sequence (rf4) ===
  [deleted "Mack"]  offers=["Ney, attack Mack","Ney, attack Brunswick","Ney, attack Deroy"]  visible=true
  [typed "Bru"]     offers=["Ney, attack Brunswick"]                                         visible=true
```

The walk is unchanged; the completer comes back with the one offer that
finishes the line. Whoever builds it should pin it **behaviourally**, with the
`push_input` harness above — the source-text pins are what let this through.

---

## 8. THE SIBLINGS

**`CX3-R7b` (the frozen anchor) — NARROWED, P4 stands.** The behaviour is real
and I reproduced it (ARM 0 above: edit the line, Up walks the frozen `"ney"`
pool and discards the edit). But the report's criticism of the record misreads
it. The docstring reads *"the walk is PREFIX-FILTERED … **the standard shell
idiom**, and the thing that makes a longer window pay"* — the phrase modifies
**prefix filtering**, which is standard, not the anchor freeze. The record is
not claiming what R7b says it claims. The report already concedes the behaviour
is "defensible as written"; with the misquote removed, there is nothing left to
fix. **Do not build it** — ARM 1 shows where it leads.

**Third sibling (Down-off-the-end leaves no completion row) — CONFIRMED, P4.**
`rf1` arm (D): `text="ne"  hist_idx=-1  suggestions=0  row_visible=false`, where
`"ne"` offers 4. `_history_previous` calls `_clear_suggestions()` and
`_history_next` does not re-render. Cosmetic, one keystroke wide, and the narrow
fix in §7 does not close it — a `_refresh_suggestions()` at the end of
`_history_next`'s off-the-end branch would.

**"No index-out-of-range, no wrong-pool crash" — CONFIRMED.** I could not
produce one either; the pool is stable for the duration of a walk.

---

## 9. HONEST LIMITS

* `_last_game_state` is a stub dict, not a live backend — which is what the
  completer reads in play (spec §4: *"handing it that dict is handing it exactly
  what it reads in play"*), and what the committed harness does.
* `command_history` was seeded directly rather than accumulated by 40 turns of
  play; `_add_to_history` is its only writer and I exercised it once (`rf2`,
  arm F) with the expected result.
* Arm (A)'s conclusion is engine behaviour, measured on 4.4.1 — the version the
  project pins. A future engine that starts emitting `text_changed` on
  `set_text` would make the guard load-bearing and the narrow fix wrong.
