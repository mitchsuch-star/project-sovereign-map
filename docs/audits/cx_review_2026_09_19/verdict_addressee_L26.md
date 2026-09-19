# VERDICT:L2-6 — NARROWED (pre-existing; ⛔ the suggested fix ships a P1 regression)

**Finding:** lens "addressee", L2-6 — *"The collective guard is inside the
`if not sep:` branch, so the comma form of the same collective is refused."*
**Tree:** `master 727cf88a`, clean, read-only. **Board:** the shipped 1805
scenario, a **fresh world per utterance**, driven at `POST /command` with the
world/game_state/parser triple swapped. `LLM_MODE=mock` forced in every probe.
**My probes** (not the lens's): `r26_harness.py`, `r26_repro.py`,
`r26_printed.py`, `r26_hoist.py`, `r26_hoist_plugin.py`, `r26_guard.py`,
`r26_pin_sensitivity.py`, `r26_lever.py`, `r26_split_plugin.py`,
`r26_split_check.py`, `r26_missing_controls.py` — all under
`…/scratchpad/cx_review/probes/`. Nothing in the repo was touched.

---

## THE ONE-LINE VERDICT

> **The asymmetry is real and pre-existing. The severity is right. But three of
> the finding's own twelve rows are wrong about their own measurement, and the
> fix it prescribes — applied verbatim — reds five pins in FA-22's own test
> class and puts `the Iron Marshal, attack Mack` back into a real battle.**

---

## 1. DOES IT REPRODUCE? — YES for the rule, NO for three of its rows

`r26_repro.py`, one fresh 1805 board per utterance:

| utterance | measured | filed as |
|---|---|---|
| `all marshals attack` | **INERT** — *"Which marshal shall lead the attack, Sire?"* | "executes" ❌ |
| `all marshals, attack` | REFUSED — *"There is no 'all marshals'…"* | ✔ |
| `everyone retreat` | EXECUTED — general retreat | ✔ |
| `everyone, retreat` | REFUSED | ✔ |
| `the army retreat` | **INERT** — Berthier: *"this order eludes me"* | "executes" ❌ |
| `the army, retreat` | REFUSED | ✔ |
| `marshals, attack` | REFUSED (comma-less clarifies) | ✔ |
| `gentlemen, attack Mack` | REFUSED — **and `gentlemen attack Mack` refuses identically** | ✔ but **not an L2-6 case** ❌ |
| `all corps, / all forces, / all units, / the whole army,` | REFUSED, all four; comma-less EXECUTES, all four | ✔ |
| `every corps, retreat` | REFUSED; `every corps retreat` EXECUTES | ✔ |
| `the army, attack` | REFUSED; `the army attack` clarifies | ✔ |
| `everyone, hold` | **REFUSED? no — INERT**, and `everyone hold` is **identical** | not probed; **symmetric** |

So the divergence holds on **9 of 12** shapes, but its shape is narrower than
filed. Only **6** are refuse-vs-**execute** (`everyone retreat`, `all corps`,
`all forces`, `all units`, `the whole army`, `every corps`). **3** are
refuse-vs-a-*different free question* (`all marshals`, `the army retreat`,
`the army attack`). **1 is symmetric** (`everyone hold` — one of the row's own
four pinned cases, which the finding did not probe in the comma form). **1 is
mis-filed** (`gentlemen` is not in `_NOT_AN_ADDRESS_RE` at all —
`r26_missing_controls.py` — so both punctuations refuse and it is evidence of
nothing).

---

## 2. IS IT PRE-EXISTING? — YES, and proven twice

**(a) By source.** `git show b4a27a15^:backend/commands/executor.py` — the
pre-row `_unbound_addressee` is:

```python
head, sep, _tail = raw.partition(",")
if not sep:
    return None
phrase = head.strip()...          # ← byte-identical to HEAD from here down
```

Row CX's entire diff to this function is confined to the `if not sep:` branch
(`git diff b4a27a15^ HEAD -- backend/commands/executor.py`). **The comma path
is byte-identical before and after the row.**

**(b) By lever.** `r26_lever.py`, both positions of
`AN_ADDRESS_NEEDS_NO_COMMA` on all 11 comma cases: **0 of 11 moved.**

The finding's `shipped_by_this_row: false` is **correct**. It is FA-22's.

---

## 3. IS THE SEVERITY RIGHT? — P3 is right, and arguably generous

Every divergent case is **free**: the refusal returns before AP, gold, turn or
any marshal state is touched (measured AP 4→4, gold 800→800, zero marshals
moved on every refused case), and it **names the miss and asks a question**.
There is no shape where the comma form silently does the *wrong* thing — the
divergence is only ever refusal-vs-action, never action-vs-wrong-action.

⚠ And the direction is worth recording, because the finding's framing inverts
it: on the six genuine cases **the comma form is the safer half**.
`everyone, retreat` refuses free where `everyone retreat` runs a **0-AP
whole-army retreat** — which is FA-22's own "wider than the row" harm
(*"eight marshals, 2,270 men, ZERO AP, no confirm"*). Design intent says the
collective should reach the marshal-less arm, so the fix direction is right;
but the thing being lost today is a keystroke's worth of consistency, not men.

---

## 4. IS IT PLAYER-REACHABLE? — yes by typing, but the game never offers one

* **Client redirect (`main.gd::_redirect_diplomatic_command`, :2007):** none of
  these sentences contains any entry of `DIPLO_NO_HOME_KEYWORDS`,
  `DIPLO_WAR_ROOM_KEYWORDS` or `DIPLO_FAMILY_KEYWORDS`, and none names a
  nation. The terminal sends them **verbatim**. Reachable.
* **But nothing teaches it** (`r26_printed.py`): the COMMAND REFERENCE holds
  **50** quoted phrasings, **15** with a comma, and **all 15 are
  `<real marshal name>, <verb>`** — `Ney, attack Mack`, `Davout, fortify`, …
  **Zero** comma'd collectives. `git grep` over `godot-client/` finds **0**
  producers of a comma'd collective command string. **This is not a CX-3
  breach** — the game does not offer a sentence it cannot read.

⚠ **Found in passing, not part of this finding:** CX-3's own census needles in
`test_every_quoted_phrasing_survives_the_EXECUTOR` are `not found`,
`cannot parse`, `Unknown target`, `I cannot interpret`, `no such`, `eludes me`
— **`order of battle` is not among them**. If the manual ever did teach an
unbindable addressee, that census would call it green. A census gap worth a
line of its own.

---

## 5. ⛔ WOULD THE SUGGESTED FIX SHIP A REGRESSION? — YES. FIVE PINS, MEASURED.

The fix shape, verbatim: *"Hoist the collective / function-word test out of the
`if not sep:` branch so both punctuations answer alike."*

I applied **exactly that hoist and nothing else** (`r26_hoist_plugin.py`) and
ran the existing pins:

```
BASELINE   (no hoist)  : 152 passed
WITH THE HOIST         :   5 failed, 147 passed
```

**Every failure is in `tests/test_fa_slice1_the_two_words_2026_09_02.py::
TestAnUnboundAddresseeRefuses` — FA-22's own class:**

| pin | what it becomes |
|---|---|
| `test_nobody_else_is_sent[the Iron Marshal, attack Mack]` | **Soult musters and fights a real battle** (757 lost to the march, materiel billed both sides) |
| `test_nobody_else_is_sent[the cavalry, attack Mack]` | same |
| `test_nobody_else_is_sent[the reserve, attack Mack]` | same |
| `test_the_refusal_names_what_the_player_typed` | the refusal is gone |
| `test_the_army_wide_retreat_is_covered_too[the Iron Marshal, retreat]` | **whole-army retreat: 189,000 → 186,730 — 2,270 men, zero AP** |

Those are the **exact three cases the executor's own FA-22 comment block names
at `executor.py:1576`**, and the exact harm FA-22 was landed to kill. Also
flipped to executing by the same edit (`r26_hoist.py`):
`you there, attack Mack`, `first Berthier, attack Mack`, and
**`the Wellington, retreat` → a general retreat** — the spec's §3.1 headline
case (*"`Wellington retreat` marched the ENTIRE ARMY back"*) reopened through
the comma road.

**Why:** `_NOT_AN_ADDRESS_RE` is **one regex doing two jobs**. `the` sits in it
beside `all` / `army` / `marshals`. Hoisting the collective test hoists the
article test with it, and `the <anything>, <order>` stops being an address.

---

## 6. THE COUNTER-PROPOSAL — verified, not prescribed

Split the regex. The **collective** alternation crosses into the comma path;
the **article/function-word** alternation stays comma-less-only, where
`the Iron Marshal` must keep refusing (`r26_split_plugin.py`):

```python
_COLLECTIVE_RE = re.compile(r"\b(?:all|every|everyone|everybody|each|both|any"
                            r"|army|armies|corps|marshals|generals|commanders"
                            r"|men|troops|soldiers|forces|everything)\b", re.I)
...
if not sep:
    ...
    if self._NOT_AN_ADDRESS_RE.search(head):   # article + grammar: comma-less only
        return None
if _COLLECTIVE_RE.search(head):                # collectives: BOTH punctuations
    return None
```

Measured (`r26_split_check.py`, `r26_split_plugin.py`):

* **all 10** goal cases stop being refused;
* **all 9** guard cases still refuse — `the Iron Marshal,` `the Prince of
  Moskowa,` `the cavalry,` `the reserve,` `the Iron Marshal, retreat`,
  `the Wellington, retreat`, `Berthier,` `Nay,` `gentlemen,`;
* all 4 probed pairs become **symmetric**;
* **169 passed / 0 failed** across `TestAnUnboundAddresseeRefuses` +
  `test_cx1_a_question_never_orders.py` + `test_cx3_the_predictor.py`
  (the hoist reds 5 of the same selection).

⚠ Honest limit: I ran the pins this change can plausibly reach, not the whole
23,618-test suite. A builder must run it.

---

## 7. THE FINDING'S SECOND CLAIM — CONFIRMED, AND WORSE THAN FILED

*"`test_a_collective_address_is_not_an_unbound_name` tests only the comma-LESS
form, and two of its four cases would pass on `the` / `corps` rather than on
the collective rule."*

Mutation-tested each case by deleting the collective word it names
(`r26_pin_sensitivity.py`):

| pinned case | drop | result |
|---|---|---|
| `all marshals attack` | `all`+`marshals` | **REDS** — isolates its word |
| `every corps retreat` | `every` | **stays green** (passes on `corps`) |
| `the army attack` | `army` | **stays green** (passes on `the`) |
| `everyone hold` | `everyone` | **stays green** — *not named by the finding* |

**It is 3 of 4, not 2 of 4** — and the third is worse than weak, it is
**vacuous**: a bare `hold` is not one of `_MARSHAL_LESS_TYPES`, so
`_unbound_addressee` returns `None` on its **first line** and that case can
never exercise the collective rule at all, under any mutation.

Coverage gap confirmed too: run the pin's own four cases in the comma form and
three would **fail** its assertion (`all marshals, attack`,
`every corps, retreat`, `the army, attack`); only the vacuous one passes.

---

## 8. FOUND WHILE REFUTING (not filed as L2-6)

`r26_guard.py` spied the real call site. `now Zorglub, attack Mack`,
`just Zorglub,…`, `so Wellington,…`, `and Blucher,…`, `then Grouchy,…`,
`my Wellington,…` all answer *"There is no 'now Zorglub' in the order of
battle, Sire. Whom did you intend?"* — **with `_unbound_addressee` never
called.** There is a **second producer of that same sentence**,
`backend/commands/clarification.py:369` (*"I do not find 'X' in the order of
battle"*) and a sibling path. Anyone reading a refusal's text as proof the
guard fired will be wrong about which seam they are in — the lens's own group-C
rows are tagged on that text. Worth a line in whatever row next touches this.

---

## DISPOSITION

**NARROWED.** Keep the finding, at **P3**, marked **pre-existing (FA-22)**, with
its own reproduction table corrected (two rows do not execute, one row is not a
case) — **and with its `fix_shape` struck and replaced by the split**, because
as written it reopens FA-22 on the three cases FA-22's own comment block names.
The second claim (the weak pin) should be raised from "two of four" to "three of
four, one of them structurally vacuous" and carried as its own line item.
