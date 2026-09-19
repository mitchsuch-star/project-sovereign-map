# VERDICT — CX5-L5-F8 (lens "retreat")

> **NARROWED · P3 → P4 · PRE-EXISTING (row CX shipped nothing here — proven
> three ways) · player-reachable.** The sentence reproduces exactly as filed.
> **But its title's causal claim is REFUTED by the control the lens did not
> run: `Lannes, attack Mack` — the plainest named order in the game, no noun
> phrase, no retreat word — produces a BYTE-IDENTICAL muster block and commits
> *five* corps instead of four.** The noun phrase buys nothing but a warning
> the named order does not get. The behaviour is the documented `auto_resolved`
> contract, it is disclosed, it *halts and asks* when the odds are bad, and the
> parse sits at **confidence 0.55 — below the 0.7 gate**, so unlike the defect
> CX-5 actually closed (0.90, uncorrectable) live mode escalates it. **The
> remedy the finding asks for reds 7 pins that exist specifically to stop it.**
> One genuine P4 residue survives, and it is a different defect from the one
> filed.

Tree `master 727cf88a`, clean, read-only. Board: shipped 1805, **fresh world
per utterance**, driven at `POST /command` with the world/game_state/parser
triple swapped. Probes `.../cx_review/probes/refute_L5F8/{h,a_headline,
b_controls,c_prerow,d_reach_and_escalate,e_comma_arm,f_fixcost,g_corpus_fixA,
i_sidebyside,j_gate}.py`. Nothing in the repo was edited; both "fix" arms are
monkeypatch plugins.

---

## 1. Does it reproduce? YES — exactly, to the corps

`a_headline.py`, fresh board:

```
UTTERANCE : Lannes, smash the retreating column
EXECUTED  : True   ap (4, 3)  battle=True
MOVED     : ['Davout', 'Lannes', 'Napoleon', 'Ney']
OUR LOSS  : Davout 26000->24012, Lannes 18000->16459,
            Napoleon 10000->9236, Ney 24000->22167
THEIR LOSS: Mack 52000->36764
MSG       : Your words named no foe our maps know, Sire — Lannes marches on
            Mack at Swabia, the nearest in sight. Name another and he will
            turn. | MUSTER — Lannes (18,000; 82,340 if all march, up to
            101,556 if every corps arrives) vs Mack …
```

And the mechanism is as described: `_retreat_is_a_noun('lannes, smash the
retreating column') = True` **and** `mentions_attack(...) = True`, with the
attack branch sitting above the retreat branch, so the noun rule never gets a
vote. Figures match the lens to within combat RNG.

**Two of its three siblings are mis-described.** `harry Kutuzov's withdrawal`
is filed as "→ attack on target `Kutuzov'S Withdr…`", which reads as an
execution alongside siblings described by their outcomes. Its *parse* is
`attack/0.55`; its *outcome* is `"Cannot find 'Kutuzov'S Withdrawal' to
pursue."`, **AP 4→4, inert** — the same shelf as the other two.

---

## 2. Shipped by row CX? NO — three independent checks

| check | result |
|---|---|
| **`git diff b4a27a15^ 727cf88a -- backend/`** | row CX touches six files. `backend/ai/attack_vocabulary.py` = **0 diff lines**. `backend/commands/combat_executor.py` = **0 diff lines**. The entire causal chain — `mentions_attack` claiming the sentence, `guessed_target_refusal` disclosing and proceeding — is untouched. |
| **pre-row source** | at `b4a27a15^`, `elif mentions_attack(...)` is line 1860 and the retreat branch is line 1897. The attack branch sat above the retreat branch before the row too. |
| **verbatim pre-row parser, bound and driven** (`c_prerow.py`, `e_comma_arm.py`) | `PRE-ROW b4a27a15^: action=attack target=None confidence=0.55` · `SHIPPED 727cf88a: action=attack target=None confidence=0.55`. Byte-identical on **all seven** forms I tried, including the comma-free arm CX-1 actually shipped, the trailing-`?` arm, the negated arm and the compound arm. |

And the row's own levers agree: with **all four** of `A_RETREAT_CAN_BE_A_NOUN`,
`A_QUESTION_NEVER_ORDERS`, `COUNSEL_IS_DERIVED_FROM_THE_BOARD` and
`THE_DESK_ANSWERS_THE_BOARD` set False, the headline still fights at the same
AP with the same four corps. **`shipped_by_this_row: false` is correct.**

---

## 3. The headline's causal claim: REFUTED

The finding blames the **noun phrase** for "a four-corps battle with the
Emperor committed". Nobody ran the control. I did (`b_controls.py`,
`i_sidebyside.py`, same board, same seed):

```
class        | utterance                              | ap   | moved
-------------|----------------------------------------|------|----------------------------------
FILED        | Lannes, smash the retreating column    | 4->3 | Davout,Lannes,Napoleon,Ney
named foe    | Lannes, smash Mack                     | 4->3 | Davout,Lannes,Napoleon,Ney
named foe    | Lannes, attack Mack                    | 4->3 | Davout,Lannes,Murat,Napoleon,Ney
named foe    | Lannes, attack Mack at Swabia          | 4->3 | Davout,Lannes,Murat,Napoleon,Ney
bare deleg.  | Lannes, attack                         | 4->3 | Davout,Lannes,Napoleon,Ney
no retreat   | Lannes, smash the column               | 4->3 | Davout,Lannes,Napoleon,Ney
docstring    | Lannes, attack the enemy vanguard      | 4->3 | Davout,Lannes,Napoleon,Ney
nation named | Lannes, smash the retreating Austrians | 4->3 | Davout,Lannes,Napoleon,Ney   (silent)
```

Side by side, the muster blocks are **identical line for line** — same
`82,340 if all march`, same six WILL JOIN / WILL NOT rows, same *"The Emperor
commands in person"*, same *"Every corps in the province shares the field —
that is the design."* The **only** difference is that the noun phrase gets an
**extra** line the named order does not:

> *Your words named no foe our maps know, Sire — Lannes marches on Mack at
> Swabia, the nearest in sight.*

Three consequences the finding did not draw:

1. **The four corps and the Emperor are the ordinary multi-marshal
   reinforcement system**, not a price of the noun phrase. `Lannes, attack
   Mack` commits **more**.
2. **The retreat word is not load-bearing at all.** `Lannes, smash the column`
   — no retreat vocabulary anywhere — behaves identically. Filed under lens
   "retreat", the case has nothing to do with retreat; it is a plain
   ungrounded-target case.
3. **It is the documented contract, exercised exactly as documented.**
   `combat_executor.guessed_target_refusal`'s docstring names
   *"attack the enemy vanguard"* and *"attack the weakest enemy"* as the
   legitimate delegations this branch exists to let through. I drove both: same
   AP, same corps, same disclosure. The engine cannot tell the lens's sentence
   from them, **and the July 18, 2026 review ruled in writing that it must
   not try** — *"the set of words a player may use to describe a foe is not
   enumerable."*

---

## 4. Severity: P3 is over-stated. Three mitigations, all measured

* **It is disclosed, first line, before the muster.** (`i_sidebyside.py`)
* **It halts and asks when the odds are bad.** (`j_gate.py`) Staged into the
  dangerous shape — the cautious Davout at 4,000 against Mack at 90,000, given
  the *same* noun phrase — the engine **does not commit**:

  ```
  -> 'Davout, smash the retreating column'
     battle_report? False
     msg: Your words named no foe our maps know, Sire — Davout marches on Mack
          at Swabia … | Davout halts before the order is carried out. "Before I
          commit the corps: the odds are against us…" | The muster reads
          unfavorable. 'Commit the Attack' to send him in regardless — or
          Cancel to hold him back.
  ```
  The disclosure rides the `muster_confirm` interrupt (CA9-F1's carry), and
  **`battle_report` is False**. Nothing is committed.
* **It is LLM-correctable.** (`d_reach_and_escalate.py`) Parse confidence
  **0.55** against `LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`, so live mode
  escalates. This is the material difference from the defect CX-5 *did* close,
  which stamped **0.90** — above the gate, so, in the spec's own words, *"no
  key in any mode could ever have corrected it."* Quoting the two together, as
  the lens's framing invites, over-states the new case by the width of that
  gate.

**P4.** The behaviour the finding measured is working as designed.

---

## 5. Player-reachable? YES — but that is not the interesting half

`d_reach_and_escalate.py` ports `main.gd::_redirect_diplomatic_command` by
reading its tables out of the file at run time (sensitivity arm: 2/2
known-diplomatic sentences redirect). All nine phrasings are **sent verbatim to
the backend** — none carries a `DIPLO_*` keyword. Unaddressed
(`smash the retreating column`) the client still sends it and CR-2 asks
*"Which marshal shall lead the attack, Sire?"* at 0 AP.

---

## 6. Would the suggested fix ship a regression? YES — both ways to build it

The remedy is *"a noun phrase naming no foe should not commit four corps
including Napoleon."* Two mechanisms exist. I built and measured both.

### FIX A — hoist `_retreat_is_a_noun` above `mentions_attack`

The only lever in the row that recognises the lens's own sentence.
`f_fixcost.py`, ten ordinary pursuit orders, driven before and after:

**5 of 10 orders that fight today are refused after the fix**, including a
fully-specified one naming the nation *and* the province:

```
- Lannes, smash the retreating column
- Ney, crush the retreating enemy
- Ney, rout the retreating Austrians at Swabia     <- names nation AND province
- Ney, storm the enemy's retreat route
- Ney, engage the retreating rearguard             <- mis-routes: Ney now OBJECTS
                                                      "I would rather attack than sit idle"
```

The last is the worse failure — it does not fall through to Berthier, it falls
into a *different action*. And spec §3.4 records the row's measured, deliberate
intent in one line: **"`pursue the retreating enemy` still pursues and
fights."** Fix A revokes it.

⚠ **The golden corpus is green under Fix A — 688/688, unchanged.** The corpus
has **zero** coverage of the attack-verb-plus-retreating-noun class, so it
would not have caught a 5-of-10 regression. Anyone who builds here must pin the
class first.

### FIX B — make `guessed_target_refusal` ask on an `auto_resolved` pick

Sited where the corps are actually committed. Run against the three files that
reference the contract (baseline **397 passed**):

```
7 failed, 390 passed
FAILED …TestGuardRunsBeforeTheLethalBranches::
        test_unresolvable_name_is_disclosed_not_silently_substituted
FAILED …test_descriptive_delegations_are_never_blocked[Ney, attack the weakest enemy]
FAILED …test_descriptive_delegations_are_never_blocked[Ney, attack the enemy vanguard]
FAILED …test_descriptive_delegations_are_never_blocked[Ney, attack the British army]
FAILED …test_descriptive_delegations_are_never_blocked[Ney, attack the enemy in front of you]
FAILED …test_descriptive_delegations_are_never_blocked[Ney, attack the rest]
FAILED …test_descriptive_delegations_are_never_blocked[Ney, attack anyone nearby]
```

`tests/test_playtest_command_and_ui_2026_07_18.py:358` exists **verbatim for
this fix**, and says so in its own docstring: *"The regression the review
caught before it shipped… every one of them is an ordinary delegation and must
engage rather than bounce to a popup."* Fix B is that regression, re-shipped.

---

## 7. What actually survives — the P4 residue, and it is a different defect

Not what was filed, and worth a row of its own:

> **The disclosure's second sentence is a promise it cannot keep on the branch
> that needs it.**
>
> *"Name another and he will turn."* is **true** on the `muster_confirm`
> branch (J2 — nothing committed, the player may still redirect) and **false**
> on the resolved-battle branch (A1 — 7,106 French casualties already taken,
> Mack already down 12,467, nothing left to turn). Same string, both branches,
> `combat_executor.py:322`.
>
> Pre-existing: landed `90f062d4`, **2026-07-18**, two months before row CX,
> in a file row CX does not touch. Player-reachable on the ordinary typed road.
> Fix shape: make the clause conditional on the branch — *"Name another and he
> will turn"* when the order is still pending, *"Say the word and he will turn
> on another"* (or nothing) once the battle is reported. Copy only; no pin
> reds; no mechanic moves.

---

## 8. Disposition

| the finding says | verdict |
|---|---|
| it reproduces | **YES**, exactly |
| `shipped_by_this_row: false` | **CORRECT** — proven three ways |
| `player_reachable: true` | **CORRECT** |
| lever-independent | **CORRECT** — all four levers down, unchanged |
| *"a noun phrase **buys** a four-corps battle"* | **REFUTED** — `Lannes, attack Mack` buys the same, and one corps more |
| P3 | **over-stated → P4**; disclosed, gated at bad odds, escalates at 0.55 |
| *"a noun phrase naming no foe should not commit four corps"* | **DO NOT BUILD** — 7 pins written to stop it; 5 of 10 pursuit orders lost the other way |
| the siblings | one mis-described (`harry Kutuzov's withdrawal` is inert, not an attack) |

**Recommendation: close CX5-L5-F8 as working-as-designed; open the §7 copy
residue as its own P4 row.**
