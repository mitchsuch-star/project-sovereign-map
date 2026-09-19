# VERDICT — DESK-3 · CONFIRMED (understated twice; one harm re-attributed)

**Row under review:** CX, at master `f52df77f` (production HEAD for the row is
`727cf88a`), clean tree.
**Finding:** DESK-3 — *`_answer_reach` answers YES across a sea crossing the
Royal Navy bars — `find_path` instead of `plot_route`*, filed P2,
player-reachable, shipped by row CX.

**Default verdict was REFUTED. It did not survive.** Every line below is from a
probe I wrote and ran myself, in
`…/scratchpad/cx_review/probes/ref_desk3/` (`rh.py` + `r01`…`r12`), against
`POST /command` on the shipped 1805 board unless stated.

---

## 1. Does it reproduce AT ALL, exactly as stated? — YES, and wider

`r01_reproduce.py`, staged arm (the finding's own recipe — Davout moved to
the Normandy shore, fresh boot):

```
>>> can Davout reach London                          success=True   AP 4 -> 4
    | Yes, Sire — Davout can reach London from Normandy in 1 turn: Normandy -> London.

>>> Davout, move to London                           success=False  AP 4 -> 4
    | The crossing from Normandy to London is barred — the Royal Navy commands the
      water with 100 sail (100 effective) against our 54. …

>>> Davout, march to London                          success=False  AP 4 -> 4
    | (identical)

plot_route(w, Davout, "London", use_weighted=False, want_verdict=True)
  road   : ['London']
  verdict: legal=True  closed_destination=False  naval_leg=('Normandy','London')
  naval_check.allowed: False
```

Byte-for-byte the filed reproduction, including the `naval_check` already in
hand at the seam the desk does not call.

**But the staging is unnecessary — and that is the finding's first
understatement.** On an UNSTAGED fresh 1805 boot, at their boot provinces, **all
eight French marshals** are told yes:

```
  [Ney @ Rhineland]        Yes … in 6 turns: Rhineland -> Lorraine -> Orleanais -> Picardy -> Artois -> Normandy -> London.
  [Davout @ Rhineland]     Yes … in 6 turns: (same road)
  [Soult @ Lorraine]       Yes … in 5 turns: Lorraine -> Orleanais -> Picardy -> Artois -> Normandy -> London.
  [Lannes @ Franche-Comte] Yes … in 6 turns
  [Murat @ Franche-Comte]  Yes … in 6 turns
  [Bernadotte @ Franconia] Yes … in 7 turns
  [Massena @ Milan]        Yes … in 6 turns: Milan -> Piedmont -> Lyonnais -> Limousin -> Berry -> Normandy -> London.
  [Napoleon @ Lorraine]    Yes … in 5 turns
```

The Ulster claim reproduces verbatim too — a twelve-province road
`… -> Normandy -> London -> Cornwall -> Midlands -> Northumbria -> Scotland ->
Highlands -> Ulster`.

It reproduces unchanged on the committed played fixture
`tests/fixtures/playtest_saves/fixture_t20_ambient.json` (`r10_final.py`), so it
is not an artefact of turn 1.

The crossing is **unconditionally shut**, not strength-dependent
(`r11_last.py`: `crossing_check(Normandy→London)` returns
`allowed=False verdict='shut'` at 1,000 / 5,000 / 14,000 / 15,000 / 26,000 /
40,000 men). There is no corps size for which the desk's YES is right.

---

## 2. Is the SEVERITY right? — P2 holds, and the finding UNDERSTATES the harm

The finding measured only the one-step case, where the order is refused at
0 AP. That is the mildest arm. `r07_dies_at_water.py`, Davout staged at Artois
(French home soil, nothing ambient in the way), the desk's own two-step road:

```
>>> can Davout reach London          AP 4 -> 4
    | Yes, Sire — Davout can reach London from Artois in 2 turns: Artois -> Normandy -> London.

>>> Davout, move to London           AP 4 -> 2      success=True     ← ACCEPTED
    | Davout begins marching to London (distance: 2). Moved to Normandy. Route: Normandy -> London.

  turn ->  2 | Davout @ Normandy | order=MOVE_TO London
  turn ->  3 | Davout @ Normandy | order=NONE
      >> strategic_reports: {'marshal':'Davout','command':'MOVE_TO','order_status':'breaks',
         'reason': "Davout's his march halts at the water's edge — The crossing from
         Normandy to London is barred — the Royal Navy commands the water with 100 sail …"}
```

So the sentence the desk volunteers costs **2 action points and a turn of
marching**, and the standing order is **destroyed** (`breaks`), not stalled. The
same shape at range: `Ney, move to London` from Rhineland is accepted, charges
2 AP and marches him to Lorraine (`r04_severity.py`).

**P2 is the right severity** — nothing is corrupted, nothing is unrecoverable,
and the game does eventually say why — but it is a priced defect, not a cosmetic
one, and the finding's "shown ≠ applied" label is if anything generous.

### ⚠ One half of that harm is NOT row CX's, and must not be charged to it

The reason the distant order is not refused at 0 AP is a **pre-existing** hole I
found while attacking the severity. `plot_route` returns the refusal perfectly
well on that board (`r05_why_no_refusal.py`):

```
plot_route(use_weighted=False) road=['Lorraine','Orleanais','Picardy','Artois','Normandy','London']
   legal=True closed_dest=False naval_leg=('Normandy','London')  naval_check allowed=False
   issuance_road_refusal -> REFUSE: "The crossing from Normandy to London is barred …"
```

…but a distant tactical `move` is auto-upgraded into a MOVE_TO inside
`backend/commands/movement_executor.py:540-596` ("begins marching to …" is that
function's string, `:592`), and **that seam never calls
`strategic.issuance_road_refusal`**. A project-wide grep finds exactly one
caller, `backend/commands/strategic_executor.py:958`. Row CX touched six
production files and `movement_executor.py` is not one of them
(`git diff --name-only b4a27a15^ f52df77f`: `clause_guards.py`, `counsel.py`,
`llm_client.py`, `question_desk.py`, `executor.py`, `meta_executor.py`).

→ **Routed separately, not folded into DESK-3:** *the auto-upgrade belt does not
read the road law* — FA slice 5's own refusal exists and one of its two issuance
seams is blind to it. Owner: the movement/strategic owner. Done when
`Ney, move to London` from Rhineland is refused at 0 AP in the same words the
Normandy order already uses.

---

## 3. Wider than filed — the arm is not only SAIL-blind

`world.find_path` never filters the **destination** (`world_state.py:5359`:
`if adjacent == end: return path + [end]`, before the `passable_for` check).
`r04_severity.py` censuses the boot board from Rhineland: **21 provinces France
may not enter are nonetheless called reachable** — Silesia, Berlin, East Prussia
(Prussia, PEACE), Dresden (Saxony), Rome (PapalStates), Brunswick (Hanover),
Beira (Portugal), Albania (Ottoman)…

Measured pair (`r10_final.py`), no staging beyond standing a marshal at
Franconia, and **no dependence on the pre-existing executor hole** — this one is
refused at 0 AP, so it is a strict shown ≠ applied at distance 4:

```
  DESK  (AP 4->4): Yes, Sire — Davout can reach Brunswick from Franconia in 4 turns:
                   Franconia -> Swabia -> Rhineland -> Gelderland -> Brunswick.
  ORDER (AP 4->4): Cannot enter Brunswick — it is controlled by Hanover
                   (diplomatic state: PEACE). Open borders or higher required.
```

The finding's title names one of **at least two** laws the arm is blind to. Its
fix shape happens to cover both — `plot_route`'s verdict returns
`closed_destination=True` for all four closed provinces I sampled and
`naval_leg` for London and Ulster (`r08_fix_regression.py` part b) — so the
prescription is right and its stated scope is too narrow. The row should be
re-titled *"…across a sea the Navy bars **and a frontier we may not cross**"*.

---

## 4. Player-reachable through the shipped client? — YES

Decided by re-running the **committed** drift mirror
`tests/test_wo_slice7_cabinet_door._redirect_verdict`, which extracts
`DIPLO_*` from the shipped `main.gd` and the court forms from `utils.gd` — the
client's own rule, not a third classifier (`r03_client_gate.py`):

```
  'can Davout reach London'    -> FAIL-OPEN (reaches backend)
  'can Davout reach London?'   -> FAIL-OPEN
  'Can Soult reach London'     -> FAIL-OPEN
  'can ney reach london'       -> FAIL-OPEN
  'declare war on Prussia'     -> cabinet          (control: claimed)
```

`can` is *deliberately* excluded from `DIPLO_ADVISORY_STARTS` (main.gd:1997, and
the comment above it explains that modals were removed because they open orders),
the sentence carries no family keyword and names no court, so it fails open and
reaches `/command` verbatim.

And the phrasing is not one I invented: **`can Ney reach Vienna` is item 2 of
"the twelve questions the user named"** in the row's own pin list
(`tests/test_cx2_berthier_answers_the_board.py:131`). This is a sentence the row
exists to answer.

*(The game does not otherwise teach the phrasing — `r09` finds 0 hits for a
`can <marshal> reach <place>` template in help, the predictor, the corpus or any
`.gd`. That bounds frequency; it does not bound reachability.)*

---

## 5. Did row CX introduce it? — YES, unambiguously

* `git log --oneline -S"_answer_reach" -- backend/ai/question_desk.py` → **`5fc3d5c8`** (CX-2) and nothing else.
* `git show b4a27a15^:backend/ai/question_desk.py` contains no `reach` kind; the
  classifier pattern (`question_desk.py:460`) and `_answer_reach`
  (`:665`) are both new in CX-2.
* I extracted `b4a27a15^` to a clean tree (`git archive`, read-only) and ran the
  same sentences through its own `backend.main` (`r02_prerow.py`):

```
>>> can Davout reach London   success=False  AP 4->4
    | "Sire, Marshal Davout awaits your command, but I cannot parse this order.
       Might you mean 'Davout, scout' or 'Davout, defend'?"
>>> can Ney reach Ulster      success=False  AP 4->4   (Berthier shrug)
>>> Davout, move to London    success=False  AP 4->4
    | The crossing from Normandy to London is barred — the Royal Navy commands … (IDENTICAL to HEAD)
```

The crossing gate is unchanged pre- and post-row. **Row CX did not break the
gate; it shipped a new surface that contradicts it.**

> **Method note for whoever reads this next.** The `pre_cx/` snapshot already in
> this scratchpad hashes differently from `git show b4a27a15^:…`
> (`ffa9370f…` vs `1530b78b…`) and my first read of that was "someone edited the
> tree — don't trust it." **Wrong: it is CRLF.** `git archive` applies the
> working-tree line-ending conversion; `tr -d '\r' | md5sum` reconciles the two
> exactly. The snapshot is faithful.

---

## 6. It falsifies the SPEC, not only the docstring

The finding says `_answer_reach`'s docstring is false as written. True — but the
spec says it too, and that is the sentence that should be corrected with the
fix. `docs/COMMAND_EXPERIENCE_SPEC.md:310-318`:

> **Every answer reads the seam the MECHANIC reads** — `_build_economy`,
> `get_war_score_for`, `get_active_agenda`, **`find_path(passable_for=…)`**,
> `_build_muster_preview` … So a quoted figure is the applied figure.

`find_path(passable_for=…)` is *not* the seam the mechanic reads. The mechanic
reads `plot_route` → `crossing_check`, and refuses a closed destination. The
spec names the blind oracle as the source of truth.

---

## 7. Would the fix ship a regression? — NO. And the pin that should have caught
this is VACUOUS

**No pin reds.** The only pins on the arm are in
`tests/test_cx2_berthier_answers_the_board.py` (51 pins, **all green at HEAD**,
re-run: `51 passed in 8.14s`). Two touch `reach`, both using **Vienna** — at-war
Austrian soil, `legal=True closed_destination=False naval_leg=None`, so the fix
answers it identically. `Rhineland→Vienna` is **the same road under BFS and
Dijkstra** (`r09`), so the fix is safe even if it switches pathfinders. No pin
asserts a YES for any of the 21 closed destinations or for London/Ulster.

**The pin meant to catch exactly this is green about it by construction.**
`test_the_reach_answer_obeys_the_movement_law` asserts

```python
lawful = board.find_path("Rhineland", "Vienna", passable_for="France")
assert " -> ".join(lawful) in message
```

— it asks the **same blind oracle** the production arm asks. I ran its own
assertion against the measurably-false London answer (`r09_pins_and_teaching.py`):

```
    message : Yes, Sire — Ney can reach London from Rhineland in 6 turns: Rhineland -> …
    lawful  : Rhineland -> Lorraine -> Orleanais -> Picardy -> Artois -> Normandy -> London
    PIN ASSERTION PASSES: True
```

A pin whose oracle is the expression under test cannot fail when that expression
is the wrong one. The replacement pin must assert against the **executor's**
answer (`issuance_road_refusal` / a driven `move to`), not against `find_path`.

**Legacy is untouched by construction** (`r10_final.py`): the 19-region world has
`fleets = False`, and `plot_route`'s naval loop is guarded by
`if getattr(world, "fleets", None)`. The fix is Europe-scoped without a lever.

### One real incompleteness in the filed fix shape

The finding writes `plot_route(…, use_weighted=False, …)`. **MOVE_TO and HOLD
march the *weighted* road** (`strategic_executor.py:911`:
`use_weighted = (strategic_type in ("MOVE_TO","HOLD"))`). On the shipped board
(`r08`, `r12`), over all 8 French marshals × 126 regions = 1,000 reachable pairs:

| | count |
|---|---|
| BFS road == weighted road | 858 |
| **roads DIFFER** | **142 (14.2%)** |
| …of which the **length** also differs | **28** |

e.g. Ney Rhineland→Copenhagen: `Frankfurt -> Berlin -> Pomerania -> Scania ->
Copenhagen` (BFS) vs `Frankfurt -> Brunswick -> Hanover -> Jutland -> Copenhagen`
(weighted); worst length gap Lannes Franche-Comte→Albania, 4 steps vs 5.

So `use_weighted=False` would close the naval and frontier lies and leave a
third, smaller one standing — the desk naming a road the order will not walk,
and on 28 pairs mis-quoting the turn count. **Build it with
`use_weighted=True`** to match the verb the question is about. (This is an
incompleteness in the prescription, not a regression: the arm already has this
divergence today.)

### Recommended fix, as measured

```
road, verdict = plot_route(world, marshal, place,
                           use_weighted=True, want_verdict=True)
  road is None                  -> "There is no road … not by land."   (unchanged)
  verdict["naval_check"]        -> render naval_check["message"]
  verdict["closed_destination"] -> the existing "not lawfully" arm  ← NEW, closes §3
  not verdict["legal"]          -> the existing "not lawfully" arm  (unchanged)
  otherwise                     -> "Yes, Sire — …" over marshal.location + road
```

and correct `COMMAND_EXPERIENCE_SPEC.md:313` to name `plot_route` rather than
`find_path(passable_for=…)`.

---

## VERDICT

**CONFIRMED — P2 stands, player-reachable, shipped by row CX (`5fc3d5c8`).**
Two corrections to the row as filed:

1. **Understated (reach):** no staging is needed — all eight French marshals at
   their boot provinces, and the played `t20` fixture, get the false YES; and the
   arm lies about **21 closed land provinces** as well as the sea, so the title's
   "sea crossing" is one of at least two blind laws.
2. **Understated (price), with half of it re-attributed:** at distance ≥2 the
   order is *accepted*, costs **2 AP**, marches, and **breaks at the water**
   a turn later — but that non-refusal is a **pre-existing** blindness in
   `movement_executor.py`'s auto-upgrade belt, which row CX never touched. That
   half is routed as its own row; DESK-3 owns the false sentence and the strict
   0-AP disagreements (the one-step sea case and the closed-frontier case at any
   distance).

Plus one thing the finding did not claim and should carry: **the row's own pin
for this arm passes on the defect**, because its oracle is the expression under
test.
