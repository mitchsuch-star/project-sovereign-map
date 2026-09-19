# VERDICT — CX3-R9 — **NARROWED**

**Filed by:** lens `predictor`, P4, *"The committed evidence frames cannot show
the widest row the shipped board produces."*
**Verdict:** **NARROWED.** The core survives my own reproduction. One of its two
stated consequences is **REFUTED**. One of its two load-bearing figures is
**WRONG by a whole rendered line**. And it **understates itself in the other
direction** — it missed that the stub is not merely smaller than the shipped
board but *counterfactual*, and that the row's own evidence frame therefore
depicts the row's own headline rule being broken.
**Severity: P4 holds.** Evidence quality, not product. Not player-reachable.
Shipped by row CX.

Tree at `727cf88a`, clean before and after (`git status --porcelain` empty).
Nothing under `backend/`, `godot-client/`, `tests/`, `docs/` or `tools/` written.
The user's `user://ui_settings.cfg` was backed up and verified byte-identical
afterwards. Probes: `probes/refute_r9/`.

---

## 1. WHAT I RAN

Six probes, all mine — I deliberately did not reuse the lens's port, because the
decisive questions here are about rendered geometry and only the real scene can
answer them.

| probe | what it does |
|---|---|
| `r9_a_ground_truth.py` | boots the real 1805 scenario, reads `world.get_filtered_game_state_summary()` — the completer's only source (`backend/main.py:517`) |
| `r9_b_rows.py` | my own mirror of `_build_completions` + `_render_suggestions`, written from `scripts/main.gd:6981-7110` |
| `r9_c_frame_lines_at_executor.py` | drives **the committed frames' own suggestion lines** through the real `/command` |
| `r9_d_crop_frames.py` | crops the committed PNGs so I read them instead of trusting a description |
| `r9_f_row_in_godot.gd` | **Godot 4.4.1, real `main.tscn`**: 48 cells — {stub, real} × {default 400×270, saved 433.892×421.842} × {scale 1.0, 2.0} × the five committed shots + the true worst prefix — reading `CompletionRow.get_line_count()`/`get_content_height()` and the panel's rect |
| `r9_g_width_clamp.gd` | sweeps the requested terminal width across the config's whole legal range (300…1000) |
| `r9_h_exhaustive_widest.py` | **exhaustive** census over 25,160 target-slot prefixes for the true widest row |

Godot ran via `Start-Process` (the GUI exe swallows stdout), exit 0, **0
`SCRIPT ERROR`**, results written to an absolute scratchpad path.

---

## 2. CONFIRMED — the core, reproduced

**(a) The stub is what the row says it is.** `tools/cx3_completer_screenshot.gd`
`STATE` holds 5 `map_data` keys, 2 `enemies`, 4 `marshals`. The shipped board,
measured:

```
player_nation : France
marshals  n=8 : Bernadotte, Davout, Lannes, Massena, Murat, Napoleon, Ney, Soult
enemies   n=4 : ArchdukeJohn, Brunswick, Deroy, Mack
regions   n=126
```

**(b) The region shot is narrower than the board, exactly as filed** — and I
measured the *rendered* consequence the finding only asserted:

```
board terminal         scale typed             sug chars LINES panelW panelH
STUB  shipped-default  1.0   Ney, march to S     3    76     1  517.0  383.0
REAL  shipped-default  1.0   Ney, march to S     5   128     2  517.0  405.0
```

**(c) No committed frame contains a wrapped row.** All 20 stub cells in my table
come back `LINES=1`; max 81 chars (`Ney, `). I verified two frames against the
PNGs themselves and my Godot measurement reproduces them exactly:

* `CX3_REGION_*` → `[Ney, march to Savoy]   Ney, march to Saxony   Ney, march to Swabia  (Tab)` — one line, 76 chars ✔
* `CX3_ENEMY_X2` → `[Ney, attack Archduke John]   Ney, attack Mack  (Tab)` — one line, 55 chars ✔

**(d) The capture really is unpinned.** `main.gd:1287`
(`_setup_scalable_terminal`, reached from `_ready()` at :673) calls
`_apply_terminal_size(UiSettings.get_terminal_width(), …)`, which reads
`user://ui_settings.cfg`. On this machine that file is **dated 2026-08-08 —
six weeks before row CX existed** — and holds:

```
[terminal]  width=433.892  height=421.842
[display]   ui_scale=1.75
```

**(e) Attribution.** `git log --diff-filter=A` puts the tool **and all ten
PNGs** in `2c3535b5` (CX-3). Nothing pre-existed. `shipped_by_this_row: true`
is correct, and `player_reachable: false` is correct — these are dev artefacts
under `docs/audits/`.

**(f) The claim the frames are cited for is TRUE, and I confirmed it on the
board the frames do not use.** `COMMAND_EXPERIENCE_SPEC.md:379` and the memo
(:338) cite the frames for one thing only — that the row inherits
`content_scale_factor` and cannot be IQ-10's third fixed-size casualty. In all
**24 real-board cells** the line count is identical at 1.0 and 2.0. The row
scales; it does not reflow. The citation is not false.

---

## 3. REFUTED — *"the panel width in the frames is whatever this machine happened to have"*

The mechanism is real. **The consequence did not occur.** Width sweep over the
config's entire legal range, real scene:

```
requested  panel_w   row_w   LINES(real board)
300.0      517.0     469.0   2
400.0      517.0     469.0   2     <- shipped default
433.892    517.0     469.0   2     <- this machine's saved value
500.0      517.0     469.0   2
517.0      517.0     469.0   2
600.0      600.0     552.0   2
700.0      700.0     652.0   2
1000.0    1000.0     952.0   1     <- the row stops wrapping entirely
```

`BottomLeftUI` is a PanelContainer that clamps up to its own combined minimum —
the Execute / Diplomacy / End Turn button row — at **517**. Every saved width
from the config MIN (300) through 517 renders **identically**. The developer's
433.892 is inside that band, so the committed frames' width is the button row's
minimum, not this machine's setting, and would be byte-identical on any machine
whose saved width is ≤ 517.

So the hazard is **latent, not realised**. It bites only above 517 — where, as
the sweep shows, it would erase the very wrap the finding wants captured. Worth
pinning as insurance. Not a description of what shipped.

⚠ **And pinning the width alone would change nothing in the frames**, since 400
and 433.892 land on the same 517. The finding's fix presents it as a correction;
it is insurance.

---

## 4. WRONG FIGURE — *"the widest row is 132 characters … 2 lines / 44px"*

Exhaustive census, **25,160** target-slot prefixes (every marshal × every
slotted verb × every tail that is a prefix of some pool member, all lengths):

```
WIDEST ROW THE SHIPPED BOARD CAN PRODUCE: 177 characters
  reached by typing: 'Bernadotte, march to C'
  [Bernadotte, march to Cagliari]   Bernadotte, march to Carniola   Bernadotte,
  march to Champagne   Bernadotte, march to Constantinople   Bernadotte, march
  to Copenhagen  (Tab)
```

and in the real scene it is **not 2 lines**:

```
REAL  shipped-default  1.0   Bernadotte, march to c   5   177   LINES=3  content_h=66.0  panelH=427.0
REAL  shipped-default  2.0   Bernadotte, march to c   5   177   LINES=3  content_h=66.0  panelH=425.0
```

The finding's **132 / 2 lines / 44px** is the width at `Ney, march to ` — one
prefix the lens happened to pick. It is neither a committed shot nor the
maximum. It understates the real worst case by **45 characters (34%) and by a
whole rendered line** — 66px of panel growth, not 44 — and the panel it
displaces grows **383 → 427** rather than 383 → 405.

This matters because 44px vs 66px is the magnitude fed to the sibling finding
CX3-R4 (the stranded grip / un-re-run label-avoid rects), and it is 50% larger
than filed.

Incidentally, **128 chars / 2 lines / 44px is the real board's answer at the
shot the committed tool already takes** — so the finding's own number describes
a prefix nobody shoots, while the shipped board's answer at the prefix that *is*
shot went unstated.

---

## 5. THE FINDING UNDERSTATES ITSELF — the stub is counterfactual, not just small

The finding treats the stub as a smaller version of the board. It is not. One
of its five `map_data` keys **is not a province on the shipped board at all**:

```
'Saxony' in map_data (the completer's ONLY region pool): False
'Saxony' in world.regions                              : False
'Saxony' is a NATION                                   : True
```

`Saxony` is a *nation*. So `CX3_REGION_2026_09_19.png` and its X2 twin — I read
both — show the predictor offering:

> `[Ney, march to Savoy]   Ney, march to Saxony   Ney, march to Swabia  (Tab)`

and the shipped game **refuses that exact middle line** at the real executor:

```
'Ney, march to Saxony'   http=200  success=False
  "Saxony is a nation, not a province. Name a province, Sire — theirs are Dresden."
```

(Controls, same probe: `Ney, march to Savoy` → `success=True`, marches;
`Ney, attack Mack` → `success=True`, musters.)

**One of the three lines in the row's own region frame — 33% of it — is a
sentence the game cannot read**, inside the row whose centrepiece is stated in
its own spec heading as *THE GAME MUST NOT OFFER A SENTENCE IT CANNOT READ*, and
whose census exists to forbid exactly this.

⛔ **To be fair to the product: this is an evidence defect, not a game defect.**
`_region_names()` reads `map_data`, `map_data` has no `Saxony`, so the shipped
completer can never produce that line at any prefix. The census the row is
proudest of is not breached. But a reader of the committed frame sees the rule
broken, and that is a materially worse statement of CX3-R9 than "the frames are
narrow".

---

## 6. WHAT IS SOUND — 3 of the 5 shots are fine

Not all the frames are compromised, and the finding does not say which are:

| shot | stub | shipped | verdict |
|---|---|---|---|
| `ne` | 2 sug / 30 ch / 1 line | 2 / 30 / 1 | **identical** ✔ |
| `Ney, ` | 5 / 81 / 1 | 5 / 81 / 1 | **identical** ✔ (the verb table is a `const`) |
| `st` | 2 / 35 / 1 | 2 / 35 / 1 | **identical** ✔ |
| `Ney, attack ` | 2 / 55 / 1 | 4 / 99 / **2** | understated |
| `Ney, march to S` | 3 / 76 / 1 | 5 / 128 / **2** | understated **+ one counterfactual line** |

`Napoleon` does not collide with the `ne` prefix, and the verb table is
board-independent, which is why three of five hold.

---

## 7. WOULD THE SUGGESTED FIX SHIP A REGRESSION?

**No pin would red.** `grep` over `tests/ docs/ tools/` finds exactly two
references to the capture tool: its own usage header and the spec's prose line
at `COMMAND_EXPERIENCE_SPEC.md:380`. Nothing in the suite binds it. Both halves
are mechanically sound — `_apply_terminal_size` exists (`main.gd:1344`), does
**not** persist, and `UiSettings.DEFAULT_TERMINAL_WIDTH` = 400.0 exists.

**But the fix has three holes:**

1. **It names a fixture that is not in the repo.** `probes/payload_1805.json` is
   the lens's own scratchpad file. `find . -name payload_1805.json` returns
   nothing. Committing a 126-province snapshot also creates a drift surface —
   the scenario can change under it — with no pin to catch it. The tool's own
   docstring defends the stub (*"handing it that dict is handing it exactly what
   it reads in play"*), and that rationale is right about the **shape** and
   silent about the **content**, which is how `Saxony` got in.
2. **It does not reach the case it is about.** With the real payload and the
   `SHOTS` list unchanged, the widest committed frame becomes `Ney, march to S`
   at **2** lines. The board's worst is **3**. Reaching it needs a *sixth shot*
   at a wide prefix — `Bernadotte, march to C` — which the fix does not mention.
   The fix closes roughly two-thirds of the gap it names.
3. **It pins the size and leaves the scale unpinned.** `_ready` applies the
   saved `ui_scale` (1.75 here) *before* the tool overrides
   `root.content_scale_factor` directly at frame 60 — bypassing
   `_apply_ui_scale`, and so `refresh_viewport_scale()` and the deferred
   `_on_root_resized`. Measured, the line counts are scale-invariant either way,
   so this did not bite; but it is the same class of unpinned capture parameter
   the finding filed, one field over.

**The order I would build it in:** the counterfactual `Saxony` first (it is the
only part a reader can be misled by), then the sixth shot (it is the only part
that captures the state CX3-R4 is about), then the size/scale pins (insurance,
changes nothing today).

---

## 8. BOTTOM LINE

The finding is real and its title is accurate. Corrected on four counts:

* its stated maximum (**132 / 2 lines / 44px**) is not the maximum — the board
  makes **177 / 3 lines / 66px**, 34% wider and one whole line taller;
* its width consequence is **refuted** — the frames' 469px usable width is the
  button row's 517px floor, identical for every saved width ≤ 517, so the
  machine-dependence is latent and did not occur;
* it **missed the worse half** — the stub names a province the board does not
  have, and the committed frame shows the predictor offering a sentence the
  game refuses;
* **3 of the 5 shots are sound**, which the finding does not say.

P4 stands. Not player-reachable. Shipped by row CX-3, commit `2c3535b5`.
