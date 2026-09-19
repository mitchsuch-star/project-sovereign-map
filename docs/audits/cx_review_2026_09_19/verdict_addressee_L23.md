# VERDICT on L2-3 — the article hole

**CONFIRMED, narrowed on two claims, and UNDER-stated on one axis. Severity
P2 HOLDS. PRE-EXISTING, measured at both lever arms. The prescribed fix reds
nothing — 3041/3041 green and 0 of 460 recorded utterances move.**

Tree `master 727cf88a`, clean, read-only. Every number below is from a probe I
ran myself under `.../probes/ref_L23/`, on the shipped 1805 board through
`POST /command`, re-verified under an explicit `LLM_MODE=mock` +
`ANTHROPIC_API_KEY=` pin (my standalone probes do not load `tests/conftest.py`,
so the first run booted `mode=ANTHROPIC`; the re-run under mock is
character-identical, so nothing here depended on a live call).

---

## 1. It reproduces — exactly as filed

`r1_repro.py`, fresh board per utterance, mock-pinned:

| utterance | measured |
|---|---|
| `the Iron Marshal, attack Mack` | refused free — AP 4→4, gold 800→800 |
| **`the Iron Marshal attack Mack`** | **battle. AP 4→3, gold 800→494, 5 corps moved** |
| **`the Prince of Moskowa attack Mack`** | **battle. AP 4→3, gold 800→503** |
| `the cavalry, attack Mack` | refused free |
| **`the cavalry attack Mack`** | **battle. AP 4→3, gold 800→559** |

Mechanism as stated: `_NOT_AN_ADDRESS_RE.search(head)` (`executor.py:1039`)
runs inside the no-comma branch, **seven lines above** the
`startswith("the ")` strip at `:1046`, and `the` is in the set.

**The control the finding did not run, which proves the article is the whole
mechanism:** `Iron Marshal attack Mack` — same phrase, article deleted —
is **REFUSED** free. One keystroke.

---

## 2. PRE-EXISTING — measured, not reasoned

`r2_width_and_lever.py` at both positions of the row's own lever:

```
                                    AN_ADDRESS_NEEDS_NO_COMMA=True   =False
the Iron Marshal attack Mack        BATTLE ap4->3                    BATTLE ap4->3
the Prince of Moskowa attack Mack   BATTLE ap4->3                    BATTLE ap4->3
the cavalry attack Mack             BATTLE ap4->3                    BATTLE ap4->3
the Iron Marshal retreat            8 corps, ap4->4                  8 corps, ap4->4
  -- the un-articled twins, for contrast --
Emperor attack Mack                 REFUSED                          BATTLE ap4->3
reserve attack Mack                 REFUSED                          BATTLE ap4->3
Zorglub attack Mack                 REFUSED                          BATTLE ap4->3
```

Every articled form is byte-identical at both arms. The lever moves only the
un-articled twins. `git show b4a27a15^:backend/commands/executor.py` has a bare
`if not sep: return None` and **no `_NOT_AN_ADDRESS_RE` at all** — so pre-row,
articled and un-articled alike fought. The finding's `shipped_by_this_row:
false` is **correct**.

⚠ One honest qualifier the finding does not draw: the guard whose article
handling is inconsistent **is new code**. The row wrote its new stand-down test
on the wrong side of a strip that had been sitting seven lines below it since
FA-22. The *behaviour* is inherited; the *inconsistency* is the row's.

---

## 3. Two claims NARROWED

**(a) "three of FA-22's four named cases" is TWO of four.** FA-22's comment
block (`executor.py:1577-1580`) names exactly four, and *Prince of Moskowa
carries no article in FA-22's own wording*. Driven in FA-22's wording, comma
dropped (`r6_fa22_exact.py`):

```
HOLE      the Iron Marshal attack Mack      ap4->3
closed    Berthier attack Mack              ap4->4  refused free
closed    Prince of Moskowa attack Mack     ap4->4  refused free   <-- FA-22's wording
HOLE      the cavalry attack Mack           ap4->3
HOLE      the Prince of Moskowa attack Mack ap4->3  <-- article ADDED by the finding
```

The third case was manufactured by adding an article FA-22 never wrote.

**(b) The fix shape's own rationale is half false.** It says *"The collective
words already cover `the army` / `the cavalry` on their own."* Measured against
`_NOT_AN_ADDRESS_RE`: `army` **True**, `cavalry` **False** (nor `infantry`,
`artillery`, `guards`). Under the prescribed fix `the cavalry attack Mack`
becomes a refusal naming "cavalry" as an unknown marshal — which is exactly the
L2-5 legibility class the same lens holds at P3. The fix is still the right
fix; its stated reason is not, and a builder following the rationale would be
surprised by the `the cavalry` outcome.

**(c) And one claim the finding does NOT make, which should be said out loud
because its sibling L2-1 does:** the row's record does **not** over-claim here.
`COMMAND_EXPERIENCE_SPEC.md` §3.1 names `Grouchy` / `Berthier` / `Wellington` /
`Blucher` / `Zorglub` / `Wellington retreat` — all un-articled — and all six are
**genuinely closed** (`r7_spec.py`, 6 of 6 refused free). The spec never claimed
an articled form.

---

## 4. Severity UNDER-stated on harm, narrow on reachability → P2 HOLDS

The finding probed only `attack` (1 AP, ~300 gold). The retreat arm is worse and
was never measured:

```
the Iron Marshal retreat  ->  "General retreat ordered! Ney falling back!
                               Davout... Soult... Lannes... Murat...
                               Bernadotte... Massena... Napoleon falling back!"
                               EIGHT corps, ZERO AP, no confirm.
```

That is FA-22's own headline harm (*"'Berthier, retreat' ran a WHOLE-ARMY
retreat — eight marshals, ZERO AP, no confirm"*) reachable one article over.

Against that, reachability is narrow in the way that matters to CX-3: the game
**prints** "The Iron Marshal" (Davout's biography, `marshal.py:2181`; and
`(Iron Marshal: …)` in `tactical_executor.py:451` / `movement_executor.py:989`)
but it prints **no command-shaped articled sentence anywhere** — every chip
builds `"<Name>, <verb>"` with the comma. So CX-3's *"the game must not offer a
sentence it cannot read"* is **not breached**. Free harm on an unprompted
phrasing: **P2 is right.** Not P1 (nothing irreversible, no gold, no AP on the
worst arm), not P3 (a live battle and an army-wide retreat are not cosmetic).

---

## 5. Width measured — and one of my OWN claims killed

`r5_endtoend.py`, 20 forms × both fix positions. **The hole reaches 10 of 20:**
`the Iron Marshal` · `the Prince of Moskowa` · `the cavalry` · `the Grande
Armee` · `the reserve` · `the vanguard` · `the garrison` · `the nearest
marshal` · **`the Marshal of the Empire`** (which shows the hole is *not* only a
LEADING article — any `the` anywhere in the head stands the guard down) · plus
the retreat arm.

⛔ **`the Emperor attack Mack` is NOT in the hole, and I filed it as width on my
first pass.** Driven end to end it musters **Napoleon**, not Soult — "the
Emperor" binds the Emperor, which is correct behaviour, and the fix does not
change it. Retracted.

Untouched by the fix, as they must be: `the army attack Mack`, `the men
retreat`, `the whole army retreat` (collectives still stand down on `army` /
`men`), and the controls `attack Mack`, `Ney, attack Mack`, `retreat`.

---

## 6. Player-reachable: **TRUE**, verified at the client

`main.gd::_redirect_diplomatic_command` is fail-open and matches only the
diplomatic families (`DIPLO_NO_HOME_KEYWORDS` / `DIPLO_WAR_ROOM_KEYWORDS` /
`DIPLO_FAMILY_KEYWORDS` / the nation-gated prefixes / the court + autonomy
rules). None of these sentences names a nation or a family keyword, and
`_is_advisory_question` keys on first word ∈ {what,how,where,who,whom,why,which}
— `the` is not among them. The memo's own §1a table agrees: movement and retreat
are **open** on the typed path. The terminal sends these verbatim.

---

## 7. The prescribed fix ships NO regression — with the negative control

Built at runtime as a pytest plugin (`fixplugin.py`: strip the article before
the stand-down test; drop `the` from the set). Nothing written to the repo.

* `tests/test_cx1_...py` + `tests/test_fa_slice1_...py` — **289 / 289 green**
* the whole parser / command / corpus selection — **3041 / 3041 green**
  (identical to the unpatched baseline, 3041 / 3041)
* reach over **460** recorded utterances (golden corpus + every string in
  `tools/playtest_scripts/*.json`): **0 move** — with a **sensitivity arm**
  proving the census is live (3 of 4 injected cases detected)
* independent textual superset (comma-less **and** `the` in the pre-verb head):
  only **3** recorded candidates exist — `check the status of Davout`, `send an
  expedition to Ireland to break the blockade`, `a diversion against the
  blockade` — all naval/status types, all driven end to end, all **SAME**

---

## 8. ⚠ Found while attacking the fix, and worth more than the finding:
## row CX shipped a FLAKY PIN

On my first `-x` run the selection redded at
`test_cx1_a_question_never_orders.py::TestTheRetreatIsSometimesANoun::test_the_lever`
and I nearly filed it as a regression of the fix. It is not. Re-run **without
`-x` and with the fix still installed it is green**, and on the **shipped tree
with nothing patched at all** it fails in fresh processes:

```
8 fresh processes, no plugin, no fix:   7 passed, 1 FAILED
  AssertionError: ('lever off = the defect reproduces',
                   "Lannes respectfully raises concerns: 'Retreat? We can still fight!'")
```

The pin drives `Lannes, cut down the retreat` and asserts the defect
reproduces, but the objection is an **unmocked `random.random()`**
(`objection_v2.py:269` — whose own docstring reads *"Tests should mock
random.random() for deterministic results"*), and `pytest-randomly` is not
installed, so `random` is OS-seeded per process. When Lannes objects, the pin
reds. Roughly **1 run in 8**.

Shipped by row CX (CX-5, `c73749c3`). This is the row's own lever pin, so it is
the pin most likely to be re-run by the next slice. Fix: seed or mock
`random.random()` for that drive, or assert on a board state the objection
cannot mask.

---

## Suggested disposition

Build L2-4's head-token rule, which closes L2-3 in the same edit and is the
version that survives `the Marshal of the Empire`: after stripping a leading
article, test only the **head token** of the run. Drop `the` from the set —
it is a determiner on a name, not a collective, and its presence there is what
made `the Iron Marshal` read as *"all marshals"*. Correct the fix shape's
rationale (`cavalry` is not in the collective set), correct the title to **two**
of FA-22's four, and pin the retreat arm, which is the expensive one. Fix the
CX-5 flake in the same session.
