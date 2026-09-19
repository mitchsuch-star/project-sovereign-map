# VERDICT: CX3-R2 — **NARROWED** (P2 → **P3**), **PRE-EXISTING**, and one half
# of it is worse than filed

Refuter pass. Tree `f52df77f` (docs-only on top of `727cf88a`), clean before and
after — `git status` empty, nothing written under `backend/`, `godot-client/`,
`tests/`, `docs/` or `tools/`. Probes: `probes/ref_CX3R2/`.

**Default verdict was REFUTED. It did not survive contact — the core reproduces.
But three of the row's own load-bearing claims do not, and the control it never
ran cuts the severity in half.**

---

## THE ONE-LINE VERDICT

The hazard line is real and I reproduced it from the real Godot engine through
to the real executor. But it does **not** stage "an attack order": it stages
`MOVE_TO Swabia` with `attack_on_arrival: False` — **byte-identical in AP,
order, path, modal and message to `Ney, march to Swabia` typed in full.** The
only thing the player did not give is the **destination**. It is 100%
pre-existing (reproduced at `f7008582`), and the game's own corpus-pinned
generic family is strictly harsher than it. What row CX did ship is the
**reachability**, and there the finding *understates* itself.

---

## 1. WHAT I REPRODUCED — and on the string the CLIENT actually sends

The finding posts `'Ney, march to '` **with the trailing space**. The client
does not send that string. `main.gd:1616` is

```gdscript
var command = command_input.text.strip_edges()
```

so what leaves the box is `'Ney, march to'`. That is the string a refuter has to
drive, and the finding never did. I drove both (`probes/ref_CX3R2/r1_repro.py`,
real `POST /command`, fresh 1805 world per row):

```
CMD 'Ney, march to '     AP 4 -> 3  ok=True  loc Rhineland -> Rhineland
     order  : MOVE_TO -> Swabia  path=['Swabia']
     modals : ['pending_interrupt']
     msg    : Ney: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?'

CMD 'Ney, march to'      AP 4 -> 3  ok=True   ... IDENTICAL ...
CMD 'ney, march to'      AP 4 -> 3  ok=True   ... IDENTICAL ...
CMD 'Ney, march'         AP 4 -> 3  ok=True   ... IDENTICAL ...
```

**It survives the strip.** Board facts the row asserts also check out: Swabia is
`controller='Bavaria'`, Mack stands there with **52,000**, Ney is at Rhineland
(adjacent), 4 AP a turn.

### The reachability, on the SHIPPED `.gd`, in real Godot 4.4.1

I did not use the finder's port. `probes/ref_CX3R2/tab_probe.gd` loads
`res://scripts/main.gd`, hands it a real `LineEdit` and the measured payload
rosters, and drives the real `_build_completions` / `_accept_suggestion`:

```
typed "Ney, "          -> ["Ney, attack ","Ney, march to ","Ney, move to ","Ney, scout ","Ney, fortify"]
typed "Ney, m"         -> ["Ney, march to ","Ney, move to "]
typed "Ney, ma"        -> ["Ney, march to "]

typed "Ney, m"      Tab1 ok=true line="Ney, march to "  ENTER would send "Ney, march to"
typed "Ney, ma"     Tab1 ok=true line="Ney, march to "  ENTER would send "Ney, march to"

keystrokes=8 (incl. Tab) from empty via "Ney, ma";  7 via "Ney, m"
```

`probes/ref_CX3R2/tab_probe2.gd`, every marshal × every slotted verb:
**`<Name>, m` + Tab lands the bare `march to` for all 8 French marshals —
48 of 48 slotted-verb roads reach the bare verb in exactly one Tab.**

**CONFIRMED: reachable, by a player, through the shipped client.** No redirect
touches it — `_redirect_diplomatic_command`'s families contain no military verb
(grepped: no `march`/`move`/`attack`/`scout`/`hold`/`support` in
`DIPLO_WAR_ROOM_KEYWORDS`, `DIPLO_NO_HOME_KEYWORDS` or `_matches_cabinet_family`).

---

## 2. THE CONTROL THE FINDING DID NOT RUN — and it halves the claim

The title says the offer *"stages an attack order the player never gave."*
`probes/ref_CX3R2/r6_control.py` runs the bare form beside the **same order with
the province named**, fresh world each, four marshals:

```
command                            AP    order          batt   dead   modal
--------------------------------------------------------------------------------
'Ney, march to'                    1     MOVE_TO Swabia False  0      pending_interrupt
'Ney, march to Swabia'             1     MOVE_TO Swabia False  0      pending_interrupt

'Massena, march to'                1     MOVE_TO Tyrol  True   6055   -
'Massena, march to Tyrol'          1     MOVE_TO Tyrol  True   7202   -      (delta = combat RNG)

'Murat, march to'                  1     MOVE_TO Swabia False  0      pending_interrupt
'Murat, march to Swabia'           1     MOVE_TO Swabia False  0      pending_interrupt

'Napoleon, march to'               1     MOVE_TO Swabia False  0      pending_interrupt
'Napoleon, march to Swabia'        1     MOVE_TO Swabia False  0      pending_interrupt
```

And the order itself, dumped from the world:

```
{'command_type': 'MOVE_TO', 'target': 'Swabia', 'target_type': 'region',
 'path': ['Swabia'], 'attack_on_arrival': False, 'join_combat': True, ...}
```

**`attack_on_arrival` is False.** There is no attack order. The
`contact_bad_odds` modal is the ordinary first-step contact gate that *any*
march into a blocked province raises — it raises identically for the fully-typed
`Ney, march to Swabia`. The defect is exactly one thing: **the engine picks the
destination, and the destination it picks is the nearest enemy-held province.**

### And that is the game's DESIGNED answer to a targetless order

`backend/ai/generic_targets.py` is a 63-line module whose whole purpose is this
("`generic` is a DESIGNED sentinel, not an accident… the executor's existing
'no target → resolve the nearest sensible one' path takes over"). Measured on
the same board (`probes/ref_CX3R2/r5_family_and_fix.py`):

```
'Ney, pursue the enemy'   AP 4->2  order=PURSUE Mack  battle=True  dead=2254  modal=-
'Ney, chase the enemy'    AP 4->2  order=PURSUE Mack  battle=True  dead=2311  modal=-
'Ney, give them hell'     AP 4->3  (muster)           battle=True  dead=2098  modal=-
'Ney, march to'           AP 4->3  MOVE_TO Swabia     battle=False dead=0     modal=pending_interrupt
```

`Grouchy, pursue the enemy` is a **golden-corpus row** (`grouchy-pursue-the-enemy`,
source `test_strategic_parser.py::test_generic_target`), as are `chase-the-enemy`
and `harry-the-enemy`. So the shipped, pinned design costs **twice the AP** and
**fights without a modal**, where the row's finding costs one AP and raises a
cancellable one. The bare `march to` is the *mildest* member of a blessed family,
not an outlier.

---

## 3. ATTRIBUTION — PRE-EXISTING, measured, not inferred

`git archive f7008582` (= `b4a27a15^`) into the scratchpad, driven with the same
probe (`probes/ref_CX3R2/r4_prerow.py`):

```
PRE-ROW f7008582
'Ney, march to'      AP 4->3  order=MOVE_TO Swabia  battle=False modal=pending_interrupt
     msg: Ney: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?'
'Massena, march to'  AP 4->3  order=MOVE_TO Tyrol   battle=True  (str 42000->34184)
'Ney, march to '     AP 4->3  order=MOVE_TO Swabia  battle=False modal=pending_interrupt
'Ney, move to'       AP 4->4  order=None  "Where shall Ney march, Sire? He stands at Rhineland."
```

Identical, arm for arm. **`shipped_by_this_row: false` is correct.** Row CX's
backend diff (`clause_guards`, `counsel`, `llm_client`, `question_desk`,
`executor`, `meta_executor`) does not touch this path; its only `march`-adjacent
edit is the help text's `hold Ulm` → `hold Swabia`.

What row CX **did** ship is the road: `git show f7008582:…/main.gd | grep -c
"COMPLETIONS_ACTIVE\|_build_completions\|_accept_suggestion"` → **0**. There was
no completer. Before CX-3 the line had to be typed in full and stopped at; now
one Tab leaves it there.

---

## 4. WHAT THE FINDING MISSED, AND IT IS THE WORSE HALF

Two things I found that the row does not file, both on the shipped `.gd`
(`probes/ref_CX3R2/tab_probe2.gd`):

**(a) One mistake makes it the completer's TOP proposal for the rest of the
session.** `_add_to_history` stores the stripped line, and history is ranked
ahead of the grammar. With `command_history = ["Ney, march to"]`:

```
typed "Ney, "   -> ["Ney, march to","Ney, attack ","Ney, march to ","Ney, move to ","Ney, scout "]
typed "Ney, m"  -> ["Ney, march to","Ney, march to ","Ney, move to "]
Tab from 'Ney, m' now yields line="Ney, march to"   (already stripped — ENTER sends it verbatim)
```

It displaces `Ney, attack ` from first place. The hazard is self-reinforcing.

**(b) At the instant Enter would fire it, the gold-highlighted entry is a
DIFFERENT string from the line.**

```
line          : "Ney, march to "
highlighted   : "Ney, march to Albania"
full list     : ["Ney, march to Albania", ... 4 more provinces]
```

`_refresh_after_accept` resets `_suggestion_index` to 0 and `_render_suggestions`
brackets entry 0 in gold. So the player is shown `[Ney, march to Albania]` as
"selected" while the line holds `Ney, march to `. That is what makes the Enter
press plausible rather than exotic — and it is the same root as CX3-R1.

---

## 5. SEVERITY — P2 is over-stated. It is P3.

For: 1 AP of 4 is spent and **is not refunded** — measured
(`probes/ref_CX3R2/r3_recovery.py`, real `/strategic_response`):

```
choice=cancel_order    AP 4->3->3  order=None  loc=Rhineland ok=True  "Ney cancels his march."
choice=hold_position   AP 4->3->3  order=None  loc=Rhineland ok=True
choice=go_around       AP 4->3->3  order=MOVE_TO Swabia      ok=True
```

Against, all measured: the consequence **equals the named order's**; the modal
is a real blocking popup (`_show_interrupt_popup`) that names Mack and Swabia and
offers Cancel Order; the behaviour is pre-existing and unchanged by the row; and
the game's own pinned generic family is harsher. 7 of 8 French marshals get the
modal; the exception (Massena, aggressive with an adjacent foe) fights
immediately for ~6,000 men — and does so identically when the province **is**
named, so that is the first-step-contact design, not this row's.

Net: an irreversible 1-AP cost and a startling modal, on a line the UI makes
easy to send and then promotes. **P3**, and the part worth building is (4a)/(4b),
not the parse.

---

## 6. WOULD THE SUGGESTED FIX SHIP A REGRESSION? — YES, all three shapes

**Fix (a)** *"extend the pin to the verb-slot strings themselves, at the
executor, asserting 0 AP and no standing order."* I ran that assertion against
today's tree (`r5_family_and_fix.py` §b):

```
the pin 'every verb-slot string costs 0 AP and leaves no order'
would RED on 5 of 12 client verbs:
   'Ney, attack'     spends 1 AP, order=None        <- CR-6's BLESSED bare-attack gating
   'Ney, march to'   spends 1 AP, order=MOVE_TO Swabia
   'Ney, scout'      spends 1 AP, order=None        <- a legitimate scout-from-here
   'Ney, fortify'    spends 2 AP, order=None
   'Ney, hold'       spends 2 AP, order=MOVE_TO Rhineland   <- with its own designed
                                                               disclosure line
```

It would red `tests/test_cr6_bare_attack_gating.py`'s whole premise (the CR-6
mini-gate blessed a bare `attack` flowing through clarification/muster/objection
at cost), and the sentence it breaks is `Davout, hold` — which ships the
deliberate line *"(Our maps read Rhineland as the province nearest your order,
Sire.)"*. **The pin is also flaky**: objections are probabilistic, so `Ney,
fortify` measured `4->4` with `pending_objection` in one run and `4->2` in
another; `Ney, drill` and `Ney, defend` alternate the same way.

**Fix (b)** *"make the bare strategic verb free and ask (`move to`'s behaviour is
the model)."* A predicate of the form *a strategic order with no specific target
must ask and cost nothing* is exactly `is_generic_target()`. It would break the
family `backend/ai/generic_targets.py` exists to make work and the corpus pins
`grouchy-pursue-the-enemy` / `chase-the-enemy` / `harry-the-enemy`
(`test_strategic_parser.py::test_generic_target`, plus the executor-seam pin
`test_strategic_bugfixes.py::test_clarification_no_internal_terms`). The sentence
it breaks is the module docstring's own headline case, **`Ney, give them hell`**
— today a muster preview and a battle, tomorrow "where?".

**Fix (c)** *"accept straight to `<verb> <first target>`."* Measured: that puts
**`Ney, march to Albania`** on the line — alphabetically first, 2,000km away.
Strictly worse than the state it replaces.

**The shape that reds nothing** is at the client and at the census, not at the
executor's cost table: (i) do not let a slotted-verb accept be a *submittable*
resting state — when the line ends in a slotted verb with an empty slot **and the
completion list is open**, Enter re-prompts instead of sending; (ii) fix the gold
highlight so the bracketed entry is the one the line holds (this is CX3-R1's
root, and it is what makes the mis-send plausible); (iii) extend the census to
drive `"<Marshal>, <verb>"` at the **executor** as a *characterization* pin —
record each verb's measured cost and order rather than asserting zero — so the
next change to any of the twelve is caught without re-litigating five blessed
numbers.

---

## 7. CLAIM-BY-CLAIM

| the row's claim | verdict |
|---|---|
| `'Ney, march to '` → AP 4→3, `pending_interrupt`, order → Swabia | **CONFIRMED**, and survives the client's `strip_edges()` |
| `_build_completions("Ney, ma")` → `['Ney, march to ']` | **CONFIRMED** on the shipped `.gd` in real Godot |
| one Tab away | **CONFIRMED**, and wider — `<Name>, m` + Tab for all 8 marshals, 48/48 slotted roads |
| Swabia is Bavaria-held, Mack 52,000 | **CONFIRMED** |
| the census always appends a target, so `"<M>, <verb>"` is never driven | **CONFIRMED** (`test_cx3_the_predictor.py:194`); the executor census is scoped to the help body only |
| "stages an **attack** order" | **REFUTED** — `MOVE_TO`, `attack_on_arrival: False` |
| "the player never gave" | **NARROWED** — only the destination; bare ≡ named on AP/order/path/modal/message |
| "ranked **second** for every marshal" | **NARROWED** — second in the `<M>, ` display list, but that list's Tab yields `attack`; the real road is `<M>, m` |
| "the one shape of the row's own rule the row did not test" | **NARROWED** — the rule is *offer nothing it cannot read*, and `Ney, march to` **is** read; this is an untested state, not a breached rule |
| pre-existing | **CONFIRMED** at `f7008582`, arm for arm |
| P2 | **NARROWED to P3** |
| player-reachable | **CONFIRMED** |
