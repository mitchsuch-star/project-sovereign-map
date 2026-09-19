# VERDICT:CX3-R6 — **NARROWED.** The focus loss is real, universal and
# **PRE-EXISTING**; what row CX shipped is a different, smaller case the
# finding never constructed — and "silently" is false.

Refuter pass at `727cf88a` (tree clean). Default verdict was REFUTED; the
finding survives, but not as filed. Every line below is from a probe I ran,
not from the one I was handed.

Probes (mine, all committed to the scratchpad):

| file | what it does |
|---|---|
| `probes/refute4/r4_tab_consequence.gd` | first pass, HEAD, frame-spaced |
| `probes/refute4/r4b_sharp.gd` | HEAD with `set_input_enabled(true)` — the real playing state |
| `probes/refute4/r4c_sync.gd` | **SYNCHRONOUS** (focus read inside the same `push_input` call) |
| `probes/refute4/r4d_prerow.gd` | **the pre-row control arm**, run against the tree at `f7008582` = `b4a27a15^` |
| `probes/refute4/r4e_recovery.gd` | recovery, and what the player can actually see |
| `probes/refute4/plug_fixedgd.py` + `fixed_main.gd` | the filed fix applied to a copy, run against the suite |

⚠ Probe 1 produced an anomaly (a Tab on an empty list *keeping* focus) that
probes 2–3 killed: it was my own frame-spacing, not the game. `push_input()`
is synchronous, so probe 3 reads focus inside the same call. Everything
below is probe 3/4/5.

---

## 1. Does it reproduce AT ALL, exactly as stated? — **The behaviour yes, the story no.**

`r4c_sync.gd`, HEAD, input enabled (`set_input_enabled(true)`, which every
response path calls):

```
[S1 empty line]        text=''             n=0 | tap1: CommandInput -> SendButton | tap2: SendButton -> DiplomacyButton
[S2 text, no offers]   text='Ney, fortify' n=0 | tap1: CommandInput -> SendButton | tap2: SendButton -> DiplomacyButton
[S5 offers, walk]      text='Ney, '        n=5 | tap1: CommandInput -> CommandInput text='Ney, attack '
[S6 shift+tab, offers] text='Ney, '        n=5 | tap1: CommandInput -> CommandInput text='Ney, attack '
[S7 shift+tab, none]   text=''             n=0 | tap1: CommandInput -> MinimizeButton
```

So the mechanism is exactly as described, and it is **wider than filed**: the
finding reproduced it on `Ney, attack Mack at once`, a sentence nobody types.
It reproduces on the **empty line** — the state the client leaves after every
single command, because `set_input_enabled(true)` clears nothing but grabs
focus. One keystroke, not twenty-four characters.

But two of the finding's own sentences do not survive.

---

## 2. **"Silently" is FALSE, and I measured the opposite.**

The filed consequence is *"after which typed characters go nowhere."* They do
not go nowhere. `_is_hotkey_blocked()` is `command_input.has_focus() or
_is_modal_dialog_open()` (`main.gd:5881`), and the focus is now on a **Button**,
so it returns false and `_unhandled_input`'s letter hotkeys fire:

```
[S11 post-command state] CommandInput -> SendButton   hotkey_blocked_now=false
[S12 bare 'n' from stray focus] screen_before=false screen_after=true  focus=SendButton
```

`n` — the first letter of `Ney`, the likeliest next thing a player types —
**opens Le Moniteur over the map.** `l`, `t`, `g`, `d`, `r` open the other five
screens. And from the stray focus, ESC does not come home:

```
[E2b] stray focus=SendButton  then ESC: SendButton -> SendButton  pause_menu_visible=true
```

ESC opens the **pause menu**. Getting home by Tab costs six more presses:

```
[E2] Tabs needed to get home = 6  focus=CommandInput
```

This makes the symptom louder and uglier than filed — and, as §3 shows, it is
not row CX's.

---

## 3. **PRE-EXISTING. The control arm reproduces it identically.**

`r4d_prerow.gd` against the pre-row tree (`f7008582` = `b4a27a15^`), whose
`_on_command_input_gui_input` has **no bare-Tab arm at all** (2 `KEY_TAB` sites
total: the `_alt_game_key` match and `_unhandled_input`'s terminal toggle; no
`COMPLETIONS_ACTIVE`):

```
=== PRE-ROW TREE. has _refresh_suggestions? false   has _accept_suggestion? false
[P1 empty line]                 tap1: CommandInput -> SendButton | tap2: SendButton -> DiplomacyButton
[P2 text 'Ney, fortify']        tap1: CommandInput -> SendButton | tap2: SendButton -> DiplomacyButton
[P4 text 'Ney, ' (HEAD offers 5)] tap1: CommandInput -> SendButton | tap2: SendButton -> DiplomacyButton
[P5 shift+tab empty]            tap1: CommandInput -> MinimizeButton
[P7 post-command state]         CommandInput -> SendButton  hotkey_blocked_now=false
[P8 bare 'n' from stray focus]  screen_before=false screen_after=true  focus=SendButton
```

P1 ≡ S1. P2 ≡ S2. P5 ≡ S7. P7/P8 ≡ S11/S12. `_unhandled_input` is
**byte-identical** pre-row vs HEAD (`diff` of the whole function: no output).

And **P4 is the finding turned inside out**: at `Ney, ` the pre-row game threw
focus to Execute, and HEAD does not. Row CX did not create the focus loss — it
**removed it from the one state where an offer exists**. The filed headline
("with no suggestion it silently moves focus to Execute") is the game's
behaviour on *every* Tab for as long as the command line has existed.

What the row genuinely did is the finding's **first** clause: Tab's meaning is
now state-dependent, where before it had exactly one meaning.

---

## 4. **What the row DID ship, and the finding did not file: the slot-`""` dead end.**

The finding built its no-offer case by typing a whole extra phrase. The
ordinary case is six keystrokes, and it is the only one of this shape that row
CX is responsible for:

```
[S3 slot-'' accept then tab] text='Ney, h' n=1
   | tap1: CommandInput -> CommandInput  text='Ney, hold'   n=0
   | tap2: CommandInput -> SendButton    text='Ney, hold'   n=0
[S4 same, fortify]           text='Ney, f' n=1
   | tap1: CommandInput -> CommandInput  text='Ney, fortify' n=0
   | tap2: CommandInput -> SendButton    text='Ney, fortify' n=0
```

`_accept_suggestion()`'s own docstring says *"Tab takes the highlighted line;
Tab again walks the list."* For the **six** `_MARSHAL_VERBS` rows with slot
`""` — `fortify`, `unfortify`, `drill`, `defend`, `hold`, `retreat` — the accept
empties the list (`_add_verb_or_target` hits `if slot == "": continue`), so the
promised second Tab throws the caret to Execute instead of walking. The six
target-taking verbs and all three bare commands do not:

```
[S8 'st']     tap1 -> 'status'   n=1 | tap2 -> 'status'   n=1 | tap3 -> 'status'   n=1
[S9 'econom'] tap1 -> 'economy'  n=1 | tap2 -> 'economy'  n=1 | tap3 -> 'economy'  n=1
[S10 'end t'] tap1 -> 'end turn' n=1 | tap2 -> 'end turn' n=1 | tap3 -> 'end turn' n=1
```

**Mitigation, measured** (`r4e_recovery.gd`) — the game withdraws the
affordance one press before it becomes dangerous:

```
[E3] typed 'Ney, h'  hint_on_screen=true  hint_text=  [Ney, hold]  (Tab)
[E3] Tab#1: CommandInput -> CommandInput  text='Ney, hold'  hint_on_screen=false
[E3] Tab#2: CommandInput -> SendButton    text='Ney, hold'  hint_on_screen=false
```

So the *player-facing* teaching stays honest: `(Tab)` is on screen only while
Tab completes. The broken promise is in the docstring, not on the screen. That
is why this is P3 and not P2.

**Rider CONFIRMED and row-shipped:** Shift+Tab. S6 vs P6 — at HEAD, Shift+Tab
with offers standing **accepts** (`shift_pressed` is never checked); pre-row it
was `ui_focus_prev` to MinimizeButton. Real, new, and worth almost nothing:
focus-prev-to-MinimizeButton is not a capability anyone uses. P4 on its own.

**Rider with no verdict:** `_accept_suggestion()` called as an `elif` condition
with side effects is a style observation, not a defect. It is also the exact
shape a pin asserts (§6).

---

## 5. Player-reachable? — **Yes, and `main.gd`'s redirect is not in play.**

This is a *keystroke in the client*, not a typed sentence, so the 114-form
diplomatic keyword redirect never sees it. The completer renders into the
terminal's own VBox (`_install_suggestion_row`), the `(Tab)` hint is on screen
in the qualifying state (E3), and both the pre-existing case (empty line) and
the row-shipped case (`Ney, h` + Tab + Tab) are reachable from a fresh line in
one and six keystrokes respectively, in the state the client puts itself in
after every response.

---

## 6. **Would the filed fix ship a regression? — Yes, and I ran it red.**

Filed fix: *"consume `KEY_TAB` unconditionally in the command line (call
`accept_event()` whether or not a suggestion was accepted)."* Written the
obvious way — `elif event.keycode == KEY_TAB:` / `_accept_suggestion()` — on a
copy of `main.gd`, with the pin repointed at the copy:

```
$ pytest tests/test_cx3_the_predictor.py -q -p plug_fixedgd
PLUGIN repointed MAIN_GD in: ['test_cx3_the_predictor']
................F
E   AssertionError: assert 'elif event.keycode == KEY_TAB and _accept_suggestion():' in '...'
tests/test_cx3_the_predictor.py:389
FAILED tests/test_cx3_the_predictor.py::TestTheCompletionSurface::test_tab_is_the_accept_key_and_was_free
1 failed, 16 passed
```

(baseline on the real file: `17 passed`.)

**The pin it reds:** `tests/test_cx3_the_predictor.py:389`,
`test_tab_is_the_accept_key_and_was_free` — a source-literal census on the
exact line the fix rewrites. Nothing else moves:
`tests/test_fa_slice13_shipping_2026_09_05.py` slices on `"KEY_TAB,"` (the
`_alt_game_key` match arm, which keeps its comma) and on `_unhandled_input`'s
body, both untouched.

**The sentence it breaks:** Tab would become the one key that can never leave
the command line. The road out survives — ESC, measured:

```
[E1] offers=5  ESC#1: CommandInput -> CommandInput  offers_now=0
[E1] ESC#2: CommandInput -> <none>
```

— but it costs two presses with a list up, and ESC *from* the stray focus opens
the pause menu (E2b), so the fix removes the cheap road while the expensive one
stays crooked.

**Better shapes, in order of what I would take:**

1. **Keep the pinned literal, add a sibling arm.** Preserves line 389 verbatim
   and decides Shift+Tab in writing:
   ```gdscript
   elif event.keycode == KEY_TAB and _accept_suggestion():
       command_input.accept_event()
   elif event.keycode == KEY_TAB and not event.shift_pressed:
       # Tab belongs to the line. ESC is the way out, and says so.
       command_input.accept_event()
   ```
   This closes the row-shipped case (§4) *and* the pre-existing one, and leaves
   `ui_focus_prev` alone.
2. **Cheaper, and closes only what the row broke:** make the docstring true —
   have `_refresh_after_accept` re-offer the sibling verbs after a slot-`""`
   accept, so `Ney, hold` + Tab walks to `Ney, retreat` instead of emptying.
   Does not touch the engine binding at all, reds nothing, and is the honest
   reading of *"Tab again walks the list."*
3. Do **not** fix the pre-existing half under row CX's name. If it is taken, it
   is its own row, and it must carry the §2 measurement — the symptom is a
   screen opening, not a dead keyboard.

**And the pin's docstring should be corrected in place:** *"nothing was taken
from the player"* is true of the file and false of the engine (Shift+Tab,
§4). The assertions are sound; the conclusion over-reaches. That half of the
finding I agree with without reservation.

---

## 7. One thing neither of us filed, found on the way

At `Ney, ` the row offers **five** verbs with `[attack]` highlighted, and there
is no key that moves the highlight — Up/Down are history (`_history_previous`),
and Tab *commits* to the highlighted one, at which point the other four vanish:

```
[S5] text='Ney, ' n=5 | tap1 -> text='Ney, attack ' n=1
```

A player who can see `hold` in the list cannot reach it with the keyboard; they
must keep typing. That is a legibility defect of the same surface, it is
row-shipped, and it is not CX3-R6. Filed here as context for the severity
call, not as this verdict's subject.

---

## Verdict

**NARROWED.** Severity **P3** (as filed), player-reachable **true**,
shipped-by-this-row **true — but only for the narrowed scope**: the
state-dependence of Tab, the slot-`""` dead end (§4), and the Shift+Tab rider.
The filed headline case, the filed reproduction and the filed consequence are
all **pre-existing**, reproduced byte-for-byte on `b4a27a15^`, and the word
*"silently"* is measurably wrong in the direction that makes it worse.
