# VERDICT:DESK-11 — CONFIRMED (wider than filed), NOT NEW, and the filed fix shape is incomplete

**Filed by:** lens "desk" · **Severity filed:** P3 · **Claims:** player-reachable
`true`, shipped by row CX `false`
**Verdict:** **CONFIRMED** on all three claims, **WIDENED** on scope and
reachability, **NARROWED** on novelty and on the rhetorical framing, and the
filed **fix shape is measured incomplete** — while the obvious alternative
(fix it at the builder) is measured to **ship a regression**.

Tree: `master f52df77f`, clean. Every number below is from a probe I wrote and
ran myself, under `.venv/Scripts/python.exe`, `LLM_MODE=mock`, on the shipped
1805 board. Probes:
`scratchpad/cx_review/probes/refute_desk11/{h,r1_reproduce,r2_ordinary_case,r3_size_the_leak,r4_census,r5_ledger_leak,r6_assimilated,r7_fix_shape,r8_note_survives,r9_bounds}.py`
plus the pytest plugin `cxfixsim.py`.

---

## 1. Does it reproduce AT ALL, exactly as stated? — YES

`r1_reproduce.py`, fresh 1805 boot, driven through the **real `POST /command`**
endpoint (not the desk function in isolation):

```
>>> what happens if I attack ArchdukeJohn
Were you to give the order, Sire:
MUSTER — Bernadotte (17,000; 58,296 if all march, up to 60,470 if every corps
arrives) vs ArchdukeJohn (substantial force) at Tyrol — the balance of force
looks unfavorable.
  WILL JOIN — Massena: will march to the sound of the guns
  ...
Nothing has been ordered, and nothing spent.

>>> what happens if I attack ArchdukeCharles
No corps of ours stands within reach of Archduke Charles at Carniola, Sire —
there is no battle to weigh.
```

Both halves of the filing are exact: the muster branch prints the raw tag, the
no-candidates branch of **the same function** prints `Archduke Charles`.
`humanize_entity_name("ArchdukeJohn") == "Archduke John"` (`r1b`).

---

## 2. It is WIDER than filed, in three ways the filing did not measure

### (a) The player never has to type the tag — the ordinary spelling is enough

The filed repro types `ArchdukeJohn`, a string no player has ever seen. That
makes the defect look self-inflicted. It is not. `r2_ordinary_case.py`:

```
what happens if I attack Archduke John        -> raw tag in the answer: True
what happens if i attack archduke john        -> raw tag in the answer: True
what happens if I attack the Archduke John    -> raw tag in the answer: True
```

The player types the spelling **the game itself printed him**: on the same
boot, `r4_census.py` measures the morning dispatch rendering `Archduke John`
and the Generals screen rendering `Archduke Charles`, both humanised, with no
raw tag in either. He types back what he read, and the game answers with the
tag. That is the ordinary case, and it reproduces.

### (b) The muster leaks in FIVE places, not one

The filing names the header. `r6_assimilated.py` / `r3_size_the_leak.py`
measured all of these on real preview objects:

| # | site | producer | measured string |
|---|------|----------|-----------------|
| 1 | header, target | `_format_muster_lines` `preview['target']['name']` | `vs ArchdukeJohn (substantial force) at Tyrol` |
| 2 | header, attacker | `_format_muster_lines` `preview['attacker']['name']` | `MUSTER — ArchdukeJohn (20,000; …)` |
| 3 | WILL JOIN row | `_format_muster_lines` `row['marshal']` | `WILL JOIN — ArchdukeJohn: stands on the field and will fight beside him` |
| 4 | `shared_casualty_note` | **`_build_muster_preview`** | `ArchdukeJohn shares the field at Silesia — his men will absorb part of any losses.` |
| 5 | `reinforcement_note` | **`_build_muster_preview`** | `ArchdukeJohn does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him.` |

Sites 2–4 need `ArchdukeJohn` on the **player's** side, which is reachable:
`vassal.assimilate_vassal_marshals` flips `marshal.nation` and **keeps the
key** (`vassal.py:3917`, body `:3940-3952`), so a vassalised Austria puts him in the French
roster under the same camelCase name. Measured, `r6`:

```
assimilated (key unchanged): ['Mack', 'ArchdukeCharles', 'ArchdukeJohn']
ArchdukeJohn.nation now: France | .name: 'ArchdukeJohn'
MUSTER — ArchdukeJohn (20,000; 157,295 if all march, …) vs Mack …
  WILL JOIN — ArchdukeJohn: stands on the field and will fight beside him
  ArchdukeJohn shares the field at Swabia — his men will absorb part of any losses.
```

Site 5 was produced **organically** in `r3_size_the_leak.py` (a second Austrian
corps moved to Tyrol).

### (c) It is hit on turn 1, on half the board's legal targets

`r9_bounds.py`, boot 1805, no setup at all:

```
enemies a turn-1 France can muster against:
  [RAW-TAG] ArchdukeJohn (Austria, WAR)     at Tyrol   -- in reach: Bernadotte, Massena
  [clean  ] Mack         (Austria, WAR)     at Swabia  -- in reach: Ney, Davout, Soult, Lannes, Murat, Bernadotte, Napoleon
  [clean  ] Brunswick    (Prussia, PEACE)   at Berlin
  [clean  ] Deroy        (Bavaria, ALLIANCE) at Franconia
```

**One of the two at-war enemies France can weigh an attack against on turn 1 is
the defective one.** Exactly 2 of 22 marshals on the board trip it, both
Austrian, and the commission bench adds none.

---

## 3. Is it reachable by a PLAYER through the shipped client? — YES, by two roads

Checked in `main.gd` as instructed.

* **The redirect does not claim it.** `_redirect_diplomatic_command`
  (`main.gd:2007`) calls `_is_advisory_question(lower)` **first** and returns
  `false` for a wh-lead (`DIPLO_ADVISORY_STARTS` = what/how/where/who/whom/
  why/which, `main.gd:1997`; the call is `main.gd:2031`). `what happens if I attack …` starts with `what`,
  so it fails open to the backend. And `attack` is in
  `DIPLO_ADDRESS_EXEMPT_WORDS` anyway. Nothing in `DIPLO_FAMILY_KEYWORDS`
  substring-matches the sentence.
* **The client does not repair it.** `_display_result` (`main.gd:2994`) ends at
  the default arm `add_output("[color=…]" + message + "[/color]")`
  (`main.gd:3047`) — **verbatim**. `Utils.humanize_nation_keys_in_text`
  substitutes **nation** tags only (`utils.gd:296`, and only prose-safe
  multi-token ones); the client's own `Utils.humanize_entity_name` exists
  (`utils.gd:284`) and is called by `enemy_phase_dialog.gd`, not here.
* **No `.gd` consumes `muster_preview`** at all (grep over
  `scripts/` + `scenes/`), so the text is the only carrier and there is no
  second render that could repair it.
* **The second road is the ordinary attack order**, which lands the same string
  in `message` and in `interrupt_popup.gd:53` (`message_label.text = '"%s"'`,
  no humanisation). `r2c`, through the real endpoint:

```
>>> Bernadotte, attack Archduke John
Bernadotte halts before the order is carried out. …
MUSTER — Bernadotte (…) vs ArchdukeJohn (substantial force) at Tyrol — …
```

---

## 4. Did row CX introduce it? — NO. PRE-EXISTING, and the filing is right

* `git diff --stat b4a27a15^ HEAD -- backend/` lists six files;
  **`backend/commands/combat_executor.py` is not among them**, and
  `git log b4a27a15^..HEAD -- backend/commands/combat_executor.py` is empty.
* `git log -S "preview['target']['name']" -- backend/commands/combat_executor.py`
  gives **one** commit: **`e4dc29b4`, 2026-07-10, `feat(W6-4): muster preview
  + standing orders surfaced`** — ten weeks before row CX.
* `git show b4a27a15^:backend/ai/question_desk.py` has five `_KINDS` (where /
  who_holds / who_at / doing / how_many) and **no `what_if`**, so CX-2 did add
  the question road. But the *string* was already player-reachable by the
  attack order since July 10, and still is.

**So the filing's `shipped_by_this_row: false` is correct.** CX-2 added a
second door to a room that was already open.

### A narrowing of the filing's own framing

The filing says *"§3.2 advertises this exact string as proof the desk reads the
mechanic's own seam."* The spec does **not** print the defect: §3.2's worked
example is `"what happens if I attack Mack"` (`COMMAND_EXPERIENCE_SPEC.md:317`),
a one-word name the bug cannot touch, and the word `MUSTER` appears nowhere in
the spec or the memo. Worse for the filing's rhetoric: the row's actual
contract — *"prints the exact string the order itself would print"* — is
**kept** by the defect, because both roads print the same wrong name. Row CX
did not break its own promise here; an older R7 contract is broken underneath
it.

---

## 5. Novelty: this is NOT a new bug class. It is an unenumerated instance of an OPEN row

The project has filed this exact class repeatedly, and one row is **still open**:

| row | sev | status | scope |
|-----|-----|--------|-------|
| **NPC-12** | **P2** | **OPEN** (`BUG_FIXES.md:8421`) | *"Raw camelCase enemy keys reach the terminal … ~426 enemy-reachable interpolations … That remainder keeps this row OPEN at P2 with an AST pin named as its completion."* Names **`combat_executor.py`** as a seam. |
| N27 (CA9) | P3 | CONFIRMED (`:8923`) | *"135 occurrences to 44 spaced"* |
| IQ5-RV3 | P3 | fixed | the reinforcement block, **same class, same file, same example name** |
| FA-69 | P3 | fixed | filed as *"DUPLICATE of N27 (an unenumerated instance, not a new bug class)"* |
| CX-X4 | P3 | routed by **this row's own memo** (`memo:368`) | the region panel's `Attack ArchdukeCharles` |

The sharpest version of the finding is this: **`CombatExecutor` already has the
display function, and the muster does not call it.** `_reinf_name`
(`combat_executor.py:751`) was added by the IQ-5 review round five weeks ago as
*"the ONE display function for every marshal name interpolated into
`reinforcement_messages`"*, and its docstring's worked example is literally
`"ArchdukeJohn" -> "Archduke John"`. The file imports `humanize_entity_name`
**22 times**. `_format_muster_lines`, six hundred lines up in the same class,
was simply not swept. That is FA-69's framing — *an inconsistency within one
file* — not a new class.

**P3 is the right severity** by the project's own calibration: IQ5-RV3, the
directly analogous row, is P3. It should not be raised to P2 on its own; the
P2 already exists and is NPC-12.

### Found while sizing it — a sibling leak the filing did not look for

`r4_census.py` / `r5_ledger_leak.py`: of six player-facing producers, the
morning dispatch and the Generals screen humanise ("Archduke John", "Archduke
Charles"); **the Strategic Ledger does not.**
`intel.known_enemies[].name` carries the raw key, and
`strategic_ledger.gd:883` renders it with
`bbcode += "  " + ename + " (" + Utils.display_nation_name(enation) + ") at "`
— the **nation** humanised beside the **marshal** left raw, in one
concatenation. Not DESK-11's, but the same sweep should take it.

And four of the desk's five enemy-facing arms are clean; `what_if` is the only
one that leaks (`r4b`).

---

## 6. Would the suggested fix ship a regression? — THE FILED ONE IS INCOMPLETE; THE OBVIOUS ONE IS WORSE

### 6a. The filed shape ("`humanize_entity_name` at the muster renderer") leaves two of the five sites raw

`r7_fix_shape.py` applies **exactly** the filed shape (humanise
`attacker.name`, `target.name`, `rows[].marshal` at the renderer) and measures
what survives:

```
BEFORE  RAW: WILL JOIN — ArchdukeJohn: stands on the field …
BEFORE  RAW: ArchdukeJohn shares the field at Silesia — his men will absorb …

AFTER   STILL RAW: ArchdukeJohn shares the field at Silesia — his men will absorb …
```

`r8_note_survives.py`, same for the enemy-side note:

```
AFTER   STILL RAW: ArchdukeJohn does not stand alone: at least 1 enemy corps
                   within reach of Tyrol would march to him.
```

Cause, by reading: `shared_casualty_note` and `reinforcement_note` are **prose
built in `_build_muster_preview`** (`combat_executor.py:1445`, `:1586`)
with `m.name` / `enemy_marshal.name` interpolated, and the renderer appends
them **verbatim** (`lines.append(f"  {preview['target']['reinforcement_note']}")`).
A renderer-level *name* swap cannot reach inside a pre-built sentence.

### 6b. Fixing it at the builder instead — the obvious "fix it at the source" move — SHIPS A REGRESSION

`rows[].marshal` and `target.name` are **machine keys**, not display strings.
`battle_diorama._inject_muster_promises` does `world.marshals.get(name)` on
`row["marshal"]` (`battle_diorama.py:249`) to honour the **PT-D2 muster-promise
parity** contract (*"every WILL JOIN name appears with SOME status"*).
Measured, `r6b`:

```
raw key    -> contingents injected: 1  (['ArchdukeJohn'])
humanised  -> contingents injected: 0  ([])
```

A builder-level humanise makes the lookup miss and the promised no-show
**vanishes silently from the Battle Diorama** — no exception, no red test on
the 1805 board today (French marshals are all one word), and **live the moment
an assimilated Archduke is a WILL JOIN**, which §2(b) shows is reachable. This
is the row's own recorded trap: `FA-69`'s ruling — *"`estate_holder` STAYS the
machine key … the display forms ride beside it"*.

### 6c. The shape that works, and what it costs

Humanise **at the renderer for the names** *and* **at the two note producers
for the prose**, leaving every machine key untouched — i.e. the FA-69 /
IQ5-RV3 idiom, with `_reinf_name`'s sibling (or `humanize_entity_name`
directly; note `_reinf_name` is gated on `BOTH_SIDES_NAME_THEIR_SCOPE`, which
is IQ-5's lever and should not silently govern the muster).

I simulated that shape as a pytest plugin (`cxfixsim.py`, patched
`CombatExecutor._format_muster_lines`, repo untouched) and ran it:

* the nine muster-touching families
  (`test_wo_slice8_panel_states_its_terms`, `test_ca9_row3_phase_a_legibility`,
  `test_creative_audit_ca9_2026_08_08`, `test_cx2_berthier_answers_the_board`,
  `test_enemy_phase_presentation`,
  `test_fa_slice16b_the_price_on_the_button_2026_09_06`,
  `test_iq5_both_sides_of_the_butchers_bill`, `test_napoleon_npv_review`,
  `test_battle_diorama`) — **678 passed, 0 failed**.
* the **FULL suite** under the same plugin —
  `pytest tests/ -p cxfixsim -q -p no:randomly` — **23,656 passed, 4 skipped
  in 676.99s, exit 0**. Not one pin red anywhere in the repo.
* No pin red. The candidate-red pin was
  `test_wo_slice8_panel_states_its_terms.py:337`
  (`assert "MUSTER — Ney (24,000) vs" in text`) — green, because every muster
  fixture in the suite uses one-word names (Ney / Mack / Napoleon), which is
  precisely why 23,618 tests never saw this.

**The sentence a naive fix would break:** none in the suite — the real risk is
the *un-pinned* one, the Battle Diorama's `out_of_reach` contingent, which
disappears without a word if the fix lands one layer too low.

---

## 7. Bottom line

| claim | verdict |
|---|---|
| reproduces as filed | **YES**, verbatim, through the real endpoint |
| severity P3 | **CORRECT** — matches IQ5-RV3, the project's own analogue |
| player-reachable | **YES**, and wider than filed: the humanised spelling works, two roads, turn 1, 1 of 2 at-war targets |
| shipped by row CX | **NO** — `e4dc29b4`, 2026-07-10; `combat_executor.py` untouched by the row |
| new bug class | **NO** — unenumerated instance of **OPEN NPC-12 (P2)**; a missed sweep site of IQ5-RV3's own fix |
| filed fix shape | **INCOMPLETE** — leaves `shared_casualty_note` and `reinforcement_note` raw |
| naive "fix at the source" | **SHIPS A REGRESSION** — breaks `_inject_muster_promises`' key lookup (1 → 0) |

**Recommended owner:** not row CX. It belongs to **NPC-12's census closure**
(whose stated completion is an AST pin), taken together with the Strategic
Ledger sibling in §5 and the memo's own **CX-X4**. Five sites, one file, one
idiom, and the display function already exists in the class.

**The filing's one real sin is under-selling itself**: it reported one leak
site, using a spelling no player types, and called the spec's boast broken when
it is not. Every one of those corrections makes the finding *stronger*.
