# REFUTATION OF `near_miss.md`

Read-only, September 19 2026. Default verdict REFUTED; every row re-derived
from source and re-driven through the real `POST /command` endpoint on the
real 1805 boot board with an **independent** harness
(`probes/rfn_harness.py` — fresh boot world per utterance, `LLM_MODE=mock`,
`SOVEREIGN_SEED=historical`, no network). Probes:
`rfn_01_comma.py`, `rfn_02_parse.py`, `rfn_03_head_vs_tree.py`,
`rfn_04_rest.py`, `rfn_05_missed.py`, `rfn_06_warpurpose.py`,
`rfn_07_warpurpose2.py`, `rfn_08_rest2.py`, `rfn_09_client.py`.

**Scoreboard: 5 SURVIVE · 8 NARROWED · 1 REFUTED-as-evidenced.**
The census is substantially honest and its central behaviour reproduces.
But **five of its seven proposed fixes would ship a regression or fail to fix
the case they name**, its P1 ranking is inverted, and it missed a bigger,
more reachable instance of its own headline defect.

---

## THE ONE-PARAGRAPH ANSWER TO THE ANSWER

The report's headline is true and mis-aimed. `Nay attack Mack` really does
send Soult into a real battle — I reproduced it, and the hole is **wider than
filed** (it runs a whole-army *retreat* too, and it swallows the seven French
names the game's own Commission bench prints). But the comma is not the root,
the proposed comma fix would refuse four working collective delegations while
still not fixing `the Guard`, and the far more reachable version of the same
harm is one the report never tested: **`Ney, attack Ulm` — the campaign's own
subject, printed in the game's own manual — fights a real battle against Mack
at Swabia, 1 AP, ~6,600 French and ~15,600 Austrian dead, while `hold Ulm`,
`move to Ulm`, `march to Ulm` and `pursue Ulm` all refuse for free.** No typo
is required and no comma is involved; the player need only name a place the
map does not have. Meanwhile the report's NM-10 evidence is taken on a
**hand-staged world** (`nm40_followups.py:60` teleports Hohenlohe to Swabia)
and does not reproduce on the boot board at all — though the finding
underneath it is real and worse than filed.

---

## ⚠ THE MEASUREMENT SUBSTRATE WAS DIRTY — AND NEITHER REPORT SAID SO

`git status` at both our sessions:

```
 M backend/ai/clause_guards.py      (mtime 2026-09-19 09:34:43)
 M backend/ai/llm_client.py         (mtime 2026-09-19 09:31:27)
```

The working tree carries an **uncommitted "CX slice 1 — A QUESTION NEVER
ORDERS"** change: `has`/`had` added to the interrogative leads, a new
`A_QUESTION_NEVER_ORDERS` lever, `_SUBJECT_WH_WORDS`,
`_DELIBERATIVE_OPENER_RE`, an `is_question(text, subjects)` roster arm, and an
unaddressed-line-ending-in-`?` rule. Its own comments cite measurements that
overlap this census directly (*"why not attack Mack → a REAL BATTLE"*).

Consequences, measured (`rfn_03_head_vs_tree.py`, HEAD extracted with
`git show HEAD:backend/ai/clause_guards.py`):

- **9 of 22 `is_question` cases differ between HEAD and the working tree.**
- The report's **own NM-5 table row `Would you have Ney attack Mack please?`
  → "attacks, 1 AP"** is the HEAD answer. On the tree I measured it returns the
  **12,717-char manual**. That row no longer reproduces.
- The report cites `clause_guards.py:561`, `llm_client.py:1164`,
  `llm_client.py:1240`, `llm_client.py:1120`. Those are all **HEAD** line
  numbers; the working tree has 564 / 1181 / 1257 / 1137. **It cited HEAD and
  measured the worktree**, and disclosed neither.

`executor.py` (Sept 14) and `combat_executor.py` (Sept 16) are **clean**, so
NM-1/2/3/11/12/13/14 are unaffected by this. NM-4/5/8 are not.

---

## ROW-BY-ROW

### REFUTE:NM-1 — SURVIVES (behaviour) / NARROWED (mechanism, magnitude, scope, fix)

**Reproduced exactly.** `rfn_01_comma.py` §B, fresh board per row:
`Nay, attack Mack` → refused 0 AP; `Nay attack Mack` → Soult attacks, battle
fought, 1 AP. Same split for `Grouchy`/`Berthier`/`Wellington`/`Blucher`.
The guard is real: `executor.py:972-974` inside `_unbound_addressee`
(`:958`), gated to `_MARSHAL_LESS_TYPES` (`:923`), called at `:1521`.

Five corrections, four of which matter:

**(a) The comma is not the root — it is the second of two misses.** The
parser fails to *bind* `Nay` because of the 4-char fuzzy floor (NM-7), and
`_unbound_addressee` is only the safety net. Measured
(`rfn_02_parse.py`): the parser binds a leading bare name perfectly well
without a comma — `Neyy attack Mack`→Ney, `Sult attack Mack`→Soult,
`Muart attack Mack`→Murat. So the sentence shape is fine; it is *this name*
that fails. NM-1 and NM-2 are the same defect seen twice, and **fixing NM-2
alone removes NM-1's harm even with the comma guard untouched** — the report
ranks them as independent P1s and never states the dependency.

**(b) The report's stated limit is wrong, in a way that makes the finding
stronger.** It says *"P1-1 through P1-3 all arise below the parser … so the
escalation cannot reach them."* Measured confidence:

| utterance | confidence | vs the 0.7 gate |
|---|---|---|
| `Nay, attack Mack` | **0.55** | escalates in live mode |
| `Nay attack Mack` | **0.80** | **never escalates** |

Escalation *can* reach it (a bound marshal or a refusal from the LLM means the
executor never sees `auto_assign_attack`). The truth is the opposite of the
report's reasoning and worse: the comma'd form gets **both** the executor
guard and the LLM rescue; the bare form gets **neither**.

**(c) The casualty figures are one stochastic draw and are not
reproducible.** Three runs of the identical utterance in one process
(`rfn_08` tail): French lost 6,775 / 6,617 / 6,557; Mack lost
15,648 / 16,589 / 14,749; gold 301 / 291 / 290; **Ney joins the muster in two
runs of three**. The report's "5,922 / 17,087 / 296 gold, six corps
relocated" is a single sample presented as a measurement, and it falls outside
the band I measured. The finding is unaffected; the precision is not earned.

**(d) The scope is WIDER than filed — it is not only `attack`.** The guard
covers five `_MARSHAL_LESS_TYPES`, and the retreat family has the same hole:

```
'Berthier, retreat'  refused 0 AP
'Berthier retreat'   GENERAL RETREAT, 9 marshals moved, 0 AP
'Nay retreat'        GENERAL RETREAT, 9 marshals moved, 0 AP
'Grouchy retreat'    GENERAL RETREAT, 9 marshals moved, 0 AP
```

**(e) Two table rows are mis-described.** `Grouchy, attack Mack` is not
"refused with did-you-mean, 0 AP" — it returns **`success: True`** with
*"There is no Marshal 'Grouchy'…"* and no candidates, from a **different code
path** than `Nay` (see MISSED-4). `Wellington attack Mack` has no did-you-mean
either.

**(f) The proposed fix #1 would ship a regression and would not do what it
claims.** *"A leading token that is neither a roster name nor an order verb,
followed by an order verb, is an addressee."* Measured today
(`rfn_09_client.py` §C), these all fight and would all start being refused:

```
'all forces attack Mack'    fought, 1 AP, 6 corps
'everyone attack Mack'      fought, 1 AP, 6 corps
'the army attack Mack'      fought, 1 AP, 6 corps
'the cavalry attack Mack'   fought, 1 AP, 6 corps
```

And it would **not** fix `the Guard attack Mack`, because
`_ADDRESSEE_IS_AN_ORDER_RE` (`executor.py:930`) already contains `guard`, so
that phrase reads as an order and returns None either way. Finally, the claim
*"Closes P1-1 and P1-3 together"* is **false**: a bare `retreat` has no
leading token at all, so `_unbound_addressee` never sees it.

---

### REFUTE:NM-2 — NARROWED: this is a GATE RE-OPEN, not an unbuilt half

**The claim *"the auto-assign half of that row is unbuilt"* is FALSE.** The
CR-6 mini-gate record, `docs/COMMAND_ROBUSTNESS_SPEC.md` §7.2(a), blessed the
exclusion in writing:

> "(Applies to the bare `general_attack` only — `auto_assign_attack` /
> "attack \<target\>" has a single natural pick and keeps it.)"

and `tests/test_cr6_bare_attack_gating.py::test_auto_assign_named_target_arms_muster_and_objection`
pins it with a docstring that says so: *"gets (b)+(c) but NOT the (a)
clarification."*

The code reading is right (`combat_executor.py:10063` has the
`if len(pool) > 1` clarify; `:10081` returns `named` with `explanation: ""`;
`_resolve_auto_assign_attacker` `:9893` contains no clarify branch). What the
report should have filed is that **the blessed premise is factually wrong on
the shipped board**: "a single natural pick" is only true when one marshal is
in range, and 7 player marshals are adjacent to Mack at boot —
`find_nearest_marshal_to_region` breaks a 7-way tie silently.

**Why the premise was never tested:** every CR-6 pin runs on
`build_world("legacy")` (the 19-region fixture) and `_isolate_single_contact`
parks every other player marshal at Brittany. The gate was held on a board
where there was, literally, a single natural pick.

**Regression check on fix #2:** it would *not* red the golden-corpus row
(`attack Mack` → `auto_assign_attack` is a **parse**-level pin, and the fix is
at the executor), and it would *not* red the CR-6 pin (one candidate ⇒
`len(pool) > 1` is false ⇒ still `named`). But it changes a blessed decision
and belongs at the gate, not in a bug slice.

---

### REFUTE:NM-3 — SURVIVES, and is WIDER than filed

Reproduced (`rfn_04_rest.py` §NM-3): bare `retreat` → 9 marshals changed,
0 AP, no confirmation, while `attack`/`move`/`scout`/`hold`/`fortify`/`drill`/
`wait`/`unfortify`/`pursue`/`form square` all ask at 0 AP.

**Wider:** `withdraw` and `fall back` do the identical whole-army retreat
(9 changed, 0 AP). The report names only `retreat`. And `advance` → the
Berthier shrug, `charge` → an honest refusal, `bombard` → an honest refusal:
**five policies for bare verbs, not two.**

**Narrowed:** "free" is explicit design — the help text prints
`retreat - Fall back toward friendly territory (FREE)`, and FA-R3 is recorded
in CLAUDE.md as having *reverted* a rule that charged a general retreat. The
defect is the unasked **army-wide scope**, not the price. And as above,
fix #1 does not reach it.

---

### REFUTE:NM-4 — REFUTED as a new finding; NARROWED to one genuine sub-case

Two of the three "fails open" cases are a **documented, deliberately pinned
trade-off**, not a hole. `docs/COMMAND_ROBUSTNESS_SPEC.md` §8 item 5 states
the rule (*"`if`/`unless`/`when`/`once`/`after` with a real (**two-word**)
clause issue nothing"*), and the corpus pins it **in both directions**:

- `parseneg-retreat-if-outnumbered-executes` — `"Ney, retreat if outnumbered"`,
  `expected: {"success": true, "action": "retreat"}`, notes: *"The elliptical
  floor cuts both ways… Recorded deliberately so the trade-off is visible
  rather than discovered."*
- `parseneg-unless-elliptical-holds` — notes: *"the two-word floor is what
  keeps `cr2-when-r…` [green]."*

**Fix #4 would red `parseneg-retreat-if-outnumbered-executes` directly** and
threatens `parseneg-unless-elliptical-holds` and the `cr2-when-ready-…` row
the CX slice's own comment names.

**The genuine sub-case:** `should` is absent from
`_CONDITION_MARKER_RE` entirely (measured: the guarded text comes back
**unchanged** for `attack Mack should the odds favour us`), so the inverted
conditional is unhandled. Note the inconsistency: `Ney, should Mack advance,
fortify` **is** refused, but `Ney, attack Mack should Mack advance` fights.

**The report also under-counts its own family.** Twelve cases gave it three
open; five extra tries gave me three more — `if possible`, `when able`,
`should Mack advance` all fight at 1 AP. The open set is larger than filed.

---

### REFUTE:NM-5 — NARROWED; one of its own table rows no longer reproduces

The mechanism is correct **at HEAD**: `_MODAL_LEADS` short-circuits with
`return not _SECOND_PERSON_AFTER_LEAD_RE.match(...)` *before* the
`text.endswith("?")` test, so `would/will/shall` + `you` ignores the question
mark while `can/could/may/might` does not. Three narrowings:

1. **Without a `?`, there is no asymmetry** — `could you attack Mack`,
   `would you attack Mack`, `can you attack Mack` all march (measured). The
   split is driven entirely by the question mark, which the report's framing
   ("identical politeness, opposite outcomes") obscures.
2. **The unaddressed half is already closed in the working tree.** Measured on
   the tree: `Would you have Ney attack Mack please?` → **MANUAL**, not
   "attacks, 1 AP". The asymmetry survives only in the **addressed** form
   (`Ney, could you attack Mack?` → manual vs `Ney, would you attack Mack?` →
   fights, 1 AP; `Ney, will you attack Mack?` → fights).
3. **Fix #3 points the opposite way from the in-flight CX slice.** Adding
   `can|could|may|might` to the second-person exemption would make a
   `?`-terminated sentence *execute*, while CX slice 1 is busy making
   `?`-terminated unaddressed lines *questions*. It also sits against
   `parseneg-polite-order-still-marches`, whose notes exist specifically to
   pin the `would/will/shall` carve-out. Two agents pulling opposite ways on
   one predicate is the finding worth filing.

---

### REFUTE:NM-6 — SURVIVES (one item over-listed)

Confirmed at source: `meta_executor.py:651` `"Soult, move to Bavaria"`,
`:704` `"Davout, hold Ulm"`, `:712` `"repair Lyon"`. An automated census of
all 50 double-quoted help examples against the live 126-region key set
(`rfn_08_rest2.py` §B) returns exactly those three place tokens as unknown
(the nation tokens — Austria, Prussia, Saxony — are correct, they belong to
diplomatic verbs). `halt Ney` with no standing order → the generic shrug,
confirmed.

Over-listed: the report writes *"`repair Lyon` / `build … at Lyon`"*. The help
text's build example is `"build market at Paris"`, and Paris is a region. Three
bad place examples, not four.

---

### REFUTE:NM-7 — SURVIVES on behaviour; the PROPOSED FIX is REFUTED

Behaviour reproduces: `_MIN_FUZZY_TARGET_LEN = 4` at `parser.py:584`, consumed
at `:645-646` inside `_plausible_name_typo`; `Ney, move to Lyon` → *"Did you
mean 'Lyonnais'?"*, `Wien`→Vienna, `Munchen`→Munich, while `Ney, move to Ulm`
→ a bare *"Region 'Ulm' not found."*

**Fix #5 ("drop the floor to 3 for the suggestion only") would re-open
WO-45 verbatim and would not fix the case it names.** Measured with the
project's own scorer over the live 126-region list:

```
'Ulm'  ratio   -> Ulster 44, Stockholm 33, Oslo 28
'Ulm'  partial -> Stockholm 80, Ulster 80, Amsterdam 50
'Nay'  partial -> Naples 80, Nassau 80, Brittany 66
```

At a 3-char floor the suggest band would answer **"Did you mean
'Stockholm'?"** for Ulm — which is precisely the defect the floor was landed
to kill, stated at the seam itself (`executor.py:615-625`: *"`Ney, attack Nye`
answered 'Did you mean Ukraine?' … a name the game cannot justify is not
offered as a guess"*). And the **correct** answer for Ulm is *Swabia*, which
is not lexically reachable at any floor — Ulm is a town inside a province, not
a misspelling.

Minor: `_plausible_name_typo(word, candidate)` is **pairwise**
(`parser.py:635`), not a list scan; the report's probe called it with a list.

---

### REFUTE:NM-8 — SURVIVES; framing over-dramatized

`random.choice` confirmed (`llm_client.py:1240` at HEAD / `:1257` on the
tree). Call-site census confirmed: exactly two — `main.py:3543` and `:3691`.
Twelve drives of `Ney, forage` gave 3 distinct messages (x5/x4/x3).

**Narrowing:** the 8 templates are split into **three buckets by what was
recognised** (3 marshal-recognised, 2 target-recognised, 3 nothing-recognised)
and `random.choice` runs *inside* a bucket. So a player repeating one command
sees only that bucket's 2–3 variants, and **all three of the marshal bucket's
variants name valid orders for the same marshal**. "A different excuse every
time" overstates it; "the same advice in three costumes" is what happens. P3
is the right severity; the prose is not.

The real sub-finding in this row is the one it buries: **`Ney, cancel` with
nothing to cancel lands on the shrug** instead of *"Ney holds no order to
cancel"* — confirmed.

---

### REFUTE:NM-9 — SURVIVES

The census is sound and the report already carries its own caveat (that 83 is
a *charge* count, not a safety count, and that bare `retreat` is inside it).
Nothing to refute. Worth noting only that "46 templates" counts refusals
reached, not refusal *producers* — my own drive found six distinct Berthier
openings across three producers, so the producer count is smaller than the
template count implies.

---

### REFUTE:NM-10 — EVIDENCE REFUTED (staged world); FINDING CONFIRMED AND WORSE

**The cited evidence is taken on a hand-staged board and the report does not
say so.** `probes/nm40_followups.py:60`:

```python
w = fresh_world()
w.marshals["Hohenlohe"].location = "Swabia"     # <-- undisclosed
```

On the genuine boot board Hohenlohe stands at **Silesia**, so
`Ney, attack Hohenlohe` becomes a strategic PURSUE and hits
`strategic.hostile_verb_at_peace` (`:150`), giving a **free, honest refusal
naming the remedy**: *"We are not at war with Prussia, Sire — Hohenlohe may
not be attacked while the peace holds. Declare war on Prussia first, or leave
him be."* **0 AP.** The report's headline row does not reproduce. Its
concluding check is also read off the wrong key — `diplomatic_states` is
pair-keyed (`France|Prussia`), so `diplomatic_states.get('Prussia')` returning
`None` proves nothing.

**But the finding underneath is real and I reproduced it on the boot board**
with an *adjacent* peaceful court (`Ney, attack Frankfurt`, Hesse —
`rfn_06`/`rfn_07`), and it is worse than filed. See MISSED-3.

Also corrected: with **no** answer typed in between, a re-issue is **free**
and the hard stop holds (*"Our purpose in this war awaits your answer, Sire —
nothing was relayed."*, 0 AP, four attempts, 1 AP total). So "each typed
re-issue costs another AP" is false as a rule; the charge only recurs once the
player *obeys the prompt*.

---

### REFUTE:NM-11 — NARROWED; the example is mis-classified

The scout arm does silently discard an unresolvable target and charge 1 AP —
confirmed. But the report's own example is the wrong kind of near-miss:
**`Bavarai` is a misspelt NATION, not a province.** Measured:

```
'Ney, scout Swabya'   -> correctly scouts Swabia          (typo corrected)
'Ney, scout Bavarai'  -> generic scout-from-here, 1 AP     (Bavaria is a nation)
'Ney, scout xyzzy'    -> generic scout-from-here, 1 AP     (pure garbage, same)
```

So this is not "a misspelt scout target vanishes" — it is "the scout arm has
no unresolvable-target branch at all", and the contrast the report draws with
the move arm is really the contrast with `_fuzzy_match_region`'s **nation**
arm (IGR-A3), which the move verb reaches and scout does not.

---

### REFUTE:NM-12 — SURVIVES; "never asks" is not a rule

`Massena, attack Mack` (Milan→Swabia, not adjacent) → 2 AP, a standing PURSUE,
Massena Milan 42,000 → Munich 39,480 with the order set. Confirmed verbatim.

Narrowed: the row generalises to "an out-of-range attack … never asks". On the
same board `Bernadotte, attack Mack` raises an **objection at 0 AP**
(*"Sire, the enemy is too strong. We need reinforcements."*) and
`Massena, attack Brunswick` refuses free. The behaviour is per-marshal and
per-target, not a blanket policy.

---

### REFUTE:NM-13 — SURVIVES and is wider (three paths, not two)

Confirmed: `Nay, fortify` → the marshal picker; `Nay, attack Mack` → a
dead-end refusal with no candidates. But there is a **third** path the report
folded away — see MISSED-4. And the bench path returns
**`success: True` on a refusal**, which is FA-N4's class.

---

### REFUTE:NM-14 — NARROWED; the report missed the real defect underneath it

*"Region 'Attack Mack' not found. Nearby: La Mancha, Karaman, Stockholm"* is
real (`executor.py:651`). But it is filed as cosmetic P3, and it is the
visible end of a single-source divergence the game already fixed once. See
MISSED-1.

---

## WHAT THE CENSUS MISSED

### MISSED-1 — PC15-13's geographic fix reached ONE call site in ten

`_fuzzy_match_region(region_name, world, near=None)` (`executor.py:519`)
carries PC15-13's `near` parameter: when the caller says where the marshal
stands, a low-confidence miss answers with the **roads out of his province**
instead of the closest-spelled name on the map. An AST-free grep of all ten
call sites finds **exactly one that passes it** —
`movement_executor.py:457-458`. The other nine (both combat attack routes at
`combat_executor.py:5463`/`:9987`/`:10159`, `executor.py:865`/`:2015`,
`movement_executor.py:966`/`:1109`/`:1238`, `strategic_executor.py:167`) do
not.

Measured — and the row's **own worked example** reproduces one verb over:

```
'Ney, move to Alsace'  -> "From Rhineland the roads lead to: Swabia, Lorraine, Frankfurt, Gelderland."
'Ney, hold Alsace'     -> "Region 'Alsace' not found. Nearby: Wales, Balearics, Ulster"
```

`Wales, Balearics, Ulster` is the exact triple the source comment at
`executor.py:630-634` names as the defect PC15-13 was landed to kill. The fix
is written, tested and wired to one verb.

**Fix:** thread `near=marshal.location` at the nine sites. No new code.

---

### MISSED-2 — `attack <a place the map does not have>` FIGHTS. This is the real P1.

This is the report's own headline harm — *a battle the player did not order* —
reached without a typo, without a comma, and without an unbindable marshal.
The player need only name a place that is not one of the 126 regions.

Measured, fresh board per row (`rfn_08_rest2.py` §A, and the Ulm sweep):

| utterance | outcome |
|---|---|
| `Davout, hold Ulm` | refused, **0 AP** — *"Region 'Ulm' not found."* |
| `Ney, move to Ulm` | refused, **0 AP** |
| `Ney, march to Ulm` | refused, **0 AP** |
| `Ney, pursue Ulm` | refused, **0 AP** — *"Cannot find 'Ulm' to pursue."* |
| **`Ney, attack Ulm`** | **BATTLE FOUGHT, 1 AP, five corps engaged, ~20,200 men lost between the two sides** |

Same for `Ney, attack Alsace`, `Ney, attack Moscow`, `Ney, attack Zorgabad` —
all fight at 1 AP. The line printed is

> *"Your words named no foe our maps know, Sire — Ney marches on Mack at
> Swabia, the nearest in sight. Name another and he will turn."*

`combat_executor.py:323`, inside `guessed_target_refusal`'s `auto_resolved`
arm. **The disclose-and-proceed rule is deliberate** — its docstring
(`:196-234`) records a July 18 2026 adversarial review that reinstated it,
because *"the set of words a player might use to describe a foe is not
enumerable"* and refusing would have bounced `attack the weakest enemy`.

That rationale is sound **for descriptive delegation** and was never aimed at
this case. `Ulm`, `Alsace`, `Moscow` are not descriptions of a foe; they are
place names, the game knows they are place-shaped, and it already owns a
did-you-mean path for exactly them — which four other verbs consult and this
one does not. "Name another and he will turn" is false comfort: the battle has
already happened.

**Reachability beats NM-1 by a wide margin.** NM-1 needs a mistyped marshal
name *and* an omitted comma. This needs one wrong place name — and **the
game's own manual prints three of them** (`Bavaria`, `Ulm`, `Lyon`,
NM-6). `Ulm` is the province the 1805 campaign is *about*.

**Fix shape (not the report's):** in the `auto_resolved` arm, when the
player's ungrounded words resolve as a **place-shaped token** that
`_fuzzy_match_region` can answer (a did-you-mean, a nation, or the `near`
roads), return that answer instead of proceeding. Descriptive delegations
(`the weakest enemy`, `the British army`) are untouched because they produce
no region verdict.

---

### MISSED-3 — the war-purpose prompt's own printed answers destroy it, and re-charge AP

Reproduced on the boot board with an adjacent peaceful court
(`rfn_07_warpurpose2.py`):

```
'Ney, attack Frankfurt'  -> 1 AP charged. pending_diplomatic_dialogue = 'war_purpose_selection'
                            "Choose your war purpose against Hesse."
                            "...Answer with one of: 1=Conquest, 2=Forced Alliance,
                             3=Subjugation, 4=Back Out."
'conquest' / '1' / '2' / '3' / 'Conquest'
                         -> 0 AP. pending_diplomatic_dialogue = None.  NOT at war.
                            Falls through to Talleyrand's ADVISORY:
                            "I must strongly advise against declaring war on Hesse..."
're-issue'               -> 1 AP charged again, re-stages.
```

Four attempts with an answer typed between them = **3 AP burned, no war
declared**. Four attempts with nothing typed = **1 AP** and the hard stop
holds.

Root: `dialogue_routing._ANSWER_VOCABULARY` (`dialogue_routing.py:60-120`) has
**no entry** for `conquest`, `forced alliance`, `subjugation`, or the digits —
only `let the province stand` / `let it stand` → `reconsider`
(`:80-81`, added by PT-A3 for exactly this dialogue, for a *different*
sentence). So the prompt names four answers and **three of the four are
silently routed into an advisory that pops the dialogue**. Only `4` /
`back out` behaves (*"Of course, Sire. Take your time."*).

This is IQ-10's H-row class — *the game's own printed sentence is not
typable* — on a priced, blocking dialogue. It is also the true content of
NM-10, which the report had the evidence for and read as "re-issues cost AP".

---

### MISSED-4 — the Commission bench prints seven French names that fight with Soult

`world.marshal_pool["France"]` = `Mortier, Grouchy, Suchet, Oudinot,
Augereau, Marmont, Senarmont` — **rendered to the player on the Generals
screen's Commission bench** (CLAUDE.md, "The Marshalate"). They are the most
plausible wrong French names a player can type, and the report tested none of
them except `Grouchy`, which it mis-filed as a typo.

Measured (`rfn_05_missed.py` §MISSED-2) — **three different behaviours for one
bench**:

| | `<name>, attack Mack` | `<name> attack Mack` | `<name>, fortify` |
|---|---|---|---|
| Grouchy, Suchet, Oudinot, Augereau | `success: **True**`, *"There is no Marshal 'X'…"*, 0 AP | **Soult fights**, 1 AP | *"There is no Marshal 'X'…"* |
| Mortier, Marmont | `success: False`, *"There is no 'X'…"*, 0 AP | **Soult fights**, 1 AP | **the marshal picker** |

Two findings in one: the same bench splits across two refusal paths for no
player-visible reason, and **one of them returns `success: True` for a
refusal** (FA-N4's class — a refusal wearing the success flag). Every one of
the seven, typed without a comma, sends Soult into a battle.

---

### MISSED-5 — the client road is clean, and that is worth recording as measured

The report waves the click road off without driving it. I drove it. The
`region_panel.gd` chips emit `"<Marshal>, attack <enemy>"` (comma present),
`"recruit <arm> in <region>"`, `"repair <region>"`, `"build <x> in <region>"`
(`region_panel.gd:134/140/272/412/424/557`). I typed every one of those
templates back for all **eight** multi-word / punctuated region keys on the
1805 map (`East Anglia`, `East Frisia`, `East Prussia`, `Franche-Comte`,
`Ile-de-France`, `La Mancha`, `New Russia`, `White Russia`): **32 of 32 parse
correctly and refuse for board reasons, 0 AP, no misparse.** The report's
conclusion holds; it just was not measured. Treat this as the control that
confirms *the near-miss cost is a property of the typed road* — which is the
one sentence in the report that most needed evidence and had none.

---

## SUMMARY OF WHAT I WOULD BUILD, AND IN WHAT ORDER

1. **MISSED-2** — the unknown-place attack. Biggest harm, cheapest reach, and
   the manual prints the trigger.
2. **MISSED-1** — thread `near=` at the nine call sites. Zero new code.
3. **MISSED-3** — teach `_ANSWER_VOCABULARY` the four answers the war-purpose
   prompt prints.
4. **NM-1 + MISSED-4** — but **not** with the report's rule. Key the guard on
   *"the leading phrase names a marshal the game knows about but cannot command
   here"* (the bench, the staff, an enemy roster, a fallen tombstone) rather
   than on *"is not a verb"*, so `all forces` / `the cavalry` / `everyone`
   keep working.
5. **NM-6** — pin the help examples against the live region list. One test.
6. **NM-2** — take it to the CR-6 gate with the 7-adjacent-marshals
   measurement; do not build it as a bug fix.
7. **NM-4 / NM-5 / NM-7** — do **not** build the filed fixes. Each reds a
   named pin or re-opens a landed row.
