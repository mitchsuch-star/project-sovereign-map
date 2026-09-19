# VERDICT: L2-7 — CONFIRMED, PRE-EXISTING, and WIDER THAN FILED

**Refuter:** default verdict REFUTED; reproduced independently before any
claim below was accepted. **Tree:** `master 727cf88a` (+ `f52df77f` docs),
clean, read-only. **Board:** shipped 1805 scenario, a **fresh world per
utterance**, driven at `POST /command` through `backend.main`'s TestClient
with the world/game_state/parser triple swapped. **Probes:** my own,
`.../cx_review/probes/r1..r9*.py` + `fixsim_plugin.py` (scratchpad only;
nothing in the repo was touched, no git mutation).

---

## VERDICT IN ONE LINE

The finding is **real, correctly attributed, and under-states its own reach by
a factor of three**. The filer drove `attack` and `retreat` and filed the
province half as a **name census with no drive** — so the sentence that
actually matters, `can East Prussia be defended`, is not in the report. It
spends an action point and puts the whole French army on the defensive.

Measured at the guard, all six imperative-capable leads × 8 two-token subjects
× 6 order tails:

> **two-token subjects: read as a question 0 of 288.**
> **one-token twins:    read as a question 252 of 288.**

The subject arm is not *weak* on multi-token names. It is **100% blind** to
every one of them on the shipped board.

---

## 1. DOES IT REPRODUCE, EXACTLY AS STATED? — YES

`r1_repro.py`, fresh board per line, footprint = AP · gold · turn · every
player marshal's location and strength.

| utterance | measured |
|---|---|
| `can Ney attack Mack` *(the filer's control)* | **INERT.** AP 4, gold 800, nothing moved. *"Were you to give the order, Sire: MUSTER…"* |
| `can Archduke Charles attack Mack` | **A REAL BATTLE.** AP 4→3, gold 800→511, **6 corps moved**, `battle_report` present, Ney −1,068 / Davout −1,157 / Soult −2,118 |
| `may / could / might Archduke Charles attack Mack` | a real battle, all three |
| `can Archduke John attack Mack` | **a real battle** — *"MUSTER — Massena (42,000) vs ArchdukeJohn"*, Massena −7,084 |
| `can Archduke Charles retreat` | **GENERAL RETREAT** — all eight corps fell back |

Every line the filer published reproduces. The mechanism they name is also
right, and I verified both halves at the source:

* `_SUBJECT_AFTER_LEAD_RE` (`clause_guards.py:654`) captures **exactly one
  token** — `(?P<subj>[A-Za-z][\w'’-]*)` — and its optional `HONORIFIC` is
  `marshal|general|gen\.|maréchal`. No *archduke*. The subject reads as
  `archduke`.
* `_question_subjects` (`llm_client.py:534`) hands the guard **raw keys** —
  `m.name` for enemies, `game_state["marshals"]` keys, `map_data` keys —
  so the list holds `ArchdukeCharles`, never `Archduke Charles`.

Control that isolates it: **`can ArchdukeCharles attack Mack` (one token, the
key spelling) is INERT.** The two-token split is the whole defect.

---

## 2. SHIPPED BY ROW CX? — NO. PRE-EXISTING, and the filer is right.

Two independent measurements, both mine.

**(a) The lever** (`r5_lever.py`; module global set in the CHILD — the
project's safe idiom, production source untouched):

| | `A_QUESTION_NEVER_ORDERS=True` (shipped) | `=False` (pre-CX) |
|---|---|---|
| 12 two-token cases | **all 12 EXECUTE** | **all 12 EXECUTE** |
| `can Ney attack Mack` | INERT | EXECUTES |
| `can Mack attack Ney` | INERT | EXECUTES |
| `can Swabia defend` | INERT | EXECUTES |
| `can Swabia attack Mack` | INERT | EXECUTES |

Identical on both arms for every two-token case; every one-token control
flips. **That is exactly what "the row closed the one-token case and left the
two-token case" looks like.**

**(b) The pre-row source.** `git show b4a27a15^:backend/ai/clause_guards.py`:

```python
def is_question(command_text: str) -> bool:      # no `subjects` parameter
```

`_SUBJECT_AFTER_LEAD_RE` does not exist pre-row (`grep -c` → 0);
`A_QUESTION_NEVER_ORDERS` does not exist pre-row (→ 0). The whole subject arm
is CX-1's.

**So the honest framing — which the filer got right and I could not break:**
the *behaviour* is pre-existing and unchanged, but the *guard that owns the
shape* is this row's own, and it is one-token wide. The row did not regress
anything; it left a hole in a wall it built, and the spec at
`COMMAND_EXPERIENCE_SPEC.md:204` records the wall as complete — *"extended and
given the live roster"*. The roster it is given is keys; the player reads
printed names.

---

## 3. WHERE THE FILING IS WRONG: IT UNDER-STATES ITSELF

The filer's size paragraph counts names and stops:

> *"6 of 126 provinces contain a space (East Anglia, East Frisia, East
> Prussia, La Mancha, New Russia, White Russia)."*

Their own three province probes (`can East Prussia be taken`, `can La Mancha
hold`, `can New Russia be taken`) are all inert — I re-ran them and confirm it
— which is presumably why the province half was filed as *size* rather than as
*behaviour*. **They picked the three tails that happen to need a marshal.**

I drove the rest (`r4_hunt.py`, `r6_reach.py`, `r9_grid.py`). Lead `can`,
8 two-token subjects × 6 tails, fresh board each:

> **31 of 48 EXECUTED.** The one-token twin grid: **5 of 48** — and all five
> are `Bavaria`, a *nation*, which is not in the subject list at all (a
> separate sibling gap, §7 below). **Every one-token subject that IS in the
> roster executes 0 of 6.**

What actually executes, that the report does not contain:

| utterance | measured |
|---|---|
| **`can East Prussia be defended`** | **whole-army DEFEND, 1 of 4 AP** — *"All forces take defensive positions: Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena, Napoleon"* |
| `can East Prussia defend` · `could East Prussia defend` | same |
| **`can White Russia / New Russia / La Mancha / East Anglia / East Frisia defend`** | same — **all six provinces** |
| `can East Prussia retreat` | **GENERAL RETREAT**, eight corps |
| `could East Prussia attack Mack` | **a real battle**, AP 4→3 |
| `can Archduke Charles defend` · `defend Tyrol` · `defend himself` | whole-army DEFEND, 1 AP |
| `can Archduke Charles scout Swabia` | Soult scouts, 1 AP |
| **`may / might Archduke Charles retreat`** | **GENERAL RETREAT**, eight corps |

The single-token twins of those exact sentences — `can Swabia be defended`,
`could Swabia defend`, `can Swabia hold`, `can Mack defend`, `can Mack be
attacked`, `may Mack retreat` — are **all INERT**, answered by Berthier's desk.

`can East Prussia be defended` is ordinary English about a province the map
paints, spelled exactly as the map paints it, and it is the row's own §3.1
whole-army class. That sentence is the finding, and it is not in the finding.

**This is also on-contract, not a stretch:** the spec's own arm (c) note cites
`is Swabia defended` — *"whose subject is a PROVINCE"* — so provinces are
explicitly inside the subject arm's intended scope.

---

## 4. PLAYER-REACHABLE? — YES, and by a sharper route than filed

* **`main.gd::_redirect_diplomatic_command` does not claim any of it.** None of
  these sentences contains a `DIPLO_NO_HOME_KEYWORDS`, `DIPLO_WAR_ROOM_KEYWORDS`
  or `DIPLO_FAMILY_KEYWORDS` entry, none names a nation for the gated
  prefixes, and `_is_advisory_question` returns **false** (= fail-open, the
  backend sees the sentence) — `can` is not in `DIPLO_ADVISORY_STARTS`
  (`what/how/where/who/whom/why/which`). Verbatim to the backend, either way.
* **The game prints the unreadable form.** Measured on the board:
  *"No intelligence on **Archduke Charles**'s position, Sire."*
* **The filer missed the decisive one: the completer HANDS the player the
  string.** `main.gd:6958 _visible_enemy_names()` returns
  `Utils.humanize_entity_name(name)` — so TAB offers **"Archduke John"** (I
  confirmed he is in the fog-filtered `enemies` payload at boot) — while
  `_question_subjects` hands the guard the raw key. **One seam humanises, the
  other does not.** That is the one-line statement of the defect, and it is a
  better fix anchor than anything in the report.

**But the CX-3 framing in the filing is a stretch and I narrow it.**
CX-3's census is `TestTheGameCanReadWhatItPrints` (quoted *command phrasings
the manual teaches*) and `TestTheCompleterOffersNothingItCannotRead` (*offered
command sentences*). The game never **offers** `can East Prussia be defended`.
This is not a CX-3 census miss; it is a print/read asymmetry one seam over.
Filing it as "CX3-X1 one layer out" over-claims a census hole that is not there.

---

## 5. SEVERITY — P2 IS RIGHT, for a bigger reason than filed

**Held at P2, agreeing with the filer.** Reasoning recorded so it is not
re-argued:

*Upward:* 31 of 48 driven cells execute; two shapes are the row's own
whole-army headline class (general retreat, whole-army defend); reachable
through the shipped client; the names are the game's own printed forms and one
of them is TAB-completable.

*Downward, and why not P1:* 8 of 148 subjects (5.4%). Three of the four
executing shapes are cheap — retreat 0 AP, defend 1 of 4 AP, scout 1 AP; only
the attack arm spends gold and fights. And the row's own P1s (`why not
retreat`, `retreat?`) needed **no name at all** — any player, first turn, any
board. This one needs the player to type one of eight specific names as a
grammatical subject.

The **attack arm alone** (`could East Prussia attack Mack`, `can Archduke
Charles attack Mack` — 1 AP, ~290 gold, 6 corps committed, real casualties) is
the P1-shaped sliver inside a P2.

Also worth stating because the filer's examples obscure it: the *most natural*
questions about a commander are already safe for other reasons —
`can Archduke Charles attack Ney` (intel refusal), `can Archduke Charles be
attacked` / `be defeated` (no marshal in range), `can Archduke Charles take
Bavaria` / `hold Tyrol` (clarification). The executing set is
`defend` / `retreat` / `scout` / `attack <enemy>`. That narrows the *commander*
half and is the one place the filer's framing flatters the finding.

---

## 6. WOULD THE PROPOSED FIX SHIP A REGRESSION? — I could not make it.

The filer offers two shapes. I attacked both.

### Fix (1) — greedy longest-name match on the live subject list. **Measured safe.**

Simulated without touching production source (`fixsim_plugin.py` patches
`is_question` and every module that bound it by name at import —
`llm_client`, `parser`, `dialogue_routing`):

| check | result |
|---|---|
| **Closes the defect?** | **20 of 20** driven cases go INERT (`r8_fixdrive.py`). *Not inert — I checked, because a green suite under an inert fix is worthless.* |
| Polite imperatives still march | `can you attack Mack` · `do attack Mack` · `please attack Mack` · `would you have Ney attack Mack` · `when ready then retreat` · `Ney, attack Mack?` · `end turn?` — **all 7 still execute** |
| CX + negation pins | **296 passed** baseline, **296 passed** under the fix |
| Every other guard-touching test file, incl. the **CR-1 golden-corpus eval harness** | **2,395 passed / 1 skipped** baseline, **2,395 passed / 1 skipped** under the fix |
| Recorded strings whose verdict flips (449 corpus + `tools/playtest_scripts/*.json` = **2,134**) | **0** |
| Blast radius | `_SUBJECT_AFTER_LEAD_RE` has **one** call site, in `is_question`, and appears in **no other backend file** |

**I cannot name a pin it reds or a sentence it breaks.** Reported as measured
rather than manufactured.

### Fix (2) — add `archduke|prince|duke` to `HONORIFIC`. **A plaster, and the filer is right to say so.**

* `HONORIFIC` is **shared** by `_SUBJECT_AFTER_LEAD_RE` *and*
  `_ADDRESSED_LINE_RE` (which gates arm (e), the unaddressed-`?` rule), so it
  is not a local edit. Measured consequence: `Archduke Charles, attack Mack`
  becomes an **addressed** line (capture `'Archduke Charles, '`), so
  `Archduke Charles, attack Mack?` would keep its order instead of asking.
* **I hypothesised a worse regression and my own probe refuted it.** I expected
  `prince` to corrupt FA-22's own cited address *"the Prince of Moskowa"* into
  an addressee token `of`. It does not: the regex requires
  `[A-Za-z][\w'’-]*\s*[,:]` immediately after the honorific, and `of Moskowa,`
  does not match. Stated because I went looking for it and did not find it.
* **It cannot work anyway.** No honorific reaches `East Prussia`, `La Mancha`
  or the other four provinces — which are **6 of the 8** affected subjects and
  the half that carries the whole-army DEFEND. Fix (2) closes at most a
  quarter of the measured surface.

**Recommendation: fix (1), anchored on the asymmetry rather than on the regex
shape** — `_question_subjects` should hand the guard the *printed* form
(`humanize_entity_name`) alongside the key, exactly as `_visible_enemy_names`
already does for the completer, and the subject match should be greedy. Then
pin it as a drift census in the CX-3 idiom: *every subject the guard is given
must be readable in the form the client offers it.* That pin is what this
slice needed and does not have.

---

## 7. FOUND IN PASSING (not L2-7 — recorded so it is not lost)

1. **A NATION name is not a subject at all.** `can Bavaria attack Mack` /
   `retreat` / `defend` / `scout Swabia` / `be defended` — **5 of 5 EXECUTE**,
   and Bavaria is one token. Same shape as L2-7, different cause:
   `_question_subjects` reads marshals + enemy commanders + `map_data`, and
   never the nation roster. The filer's one-token control set happened to
   include it and the report does not mention it.
2. **A raw camelCase key reaches the player, in a sentence that teaches a
   nonsense order.** `can Archduke Charles take Bavaria` →
   *"Regarding **ArchdukeCharles**, Sire — I need a marshal and an action. For
   example: **'Ney, move to ArchdukeCharles'**."* That is an R7 violation
   *and* the game offering a sentence it cannot read (a marshal in a province
   slot) — the genuine CX-3-census article the filer was reaching for, at a
   different seam. Likely another lens's row; recorded either way.
3. `can Archduke Charles attack Mack?`, `will / would / shall / does / is
   Archduke Charles …` are **all INERT** — arms (a), (c) and (e) catch them
   without the subject. The subject arm is the *only* thing missing, which is
   why fix (1) is small.

---

## WHAT I CHECKED AND COULD NOT BREAK

* The filer's five published measurements — all five reproduce verbatim.
* "2 of 22 commanders" — correct (8 player + 14 enemy = 22; `ArchdukeCharles`,
  `ArchdukeJohn`).
* "6 of 126 provinces" — correct, and **all six execute**, which they did not
  show.
* "shipped by this row: false" — correct, proven twice (lever + pre-row source).
* "both guards decline, for different reasons" — correct; the address arm
  stands down on the function word `can` in the leading run, independently.
