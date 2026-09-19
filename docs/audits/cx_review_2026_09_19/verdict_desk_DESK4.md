# VERDICT:DESK-4 — NARROWED

**Filed:** `_answer_what_if` weighs an attack on France's own ALLY and on a court
at peace, with no war caveat. P2, player-reachable, shipped by row CX.

**Verdict: NARROWED.** The ALLY half reproduces exactly, is real, and is shipped
by CX-2. The PEACE half — half the filed body and the whole of its rhetorical
argument — is **REFUTED**: the order against a court at peace *succeeds*, so
there is no shown-not-applied gap there. The severity is **over-graded: P3, not
P2** — measured breadth is **1 contradiction of 14** on the shipped boot board
and **0 of 17** on the committed played fixture; no figure is wrong, no AP is
spent, no state moves. And the filed **fix shape would ship a regression** in
one direction while **missing a wider case (ARMISTICE)** in the other.

Everything below was reproduced by probes I wrote and ran myself, at HEAD
(`f52df77f`; row CX tip `727cf88a`, the extra commit is docs-only), on the
shipped 1805 board, driven through `POST /command`. Probes live in
`.../scratchpad/cx_review/probes/desk4/` (`h.py` plus `p1`...`p13`). Read-only;
no repo file touched.

---

## 1. The ally half — CONFIRMED, verbatim

`p1_board.py` establishes the board: France/Bavaria = **ALLIANCE**, Deroy of
Bavaria stands at **Franconia with 22,000**, and **Bernadotte is co-located**
there with 17,000 — so the desk's own "co-located first" rule picks him.

`p2_repro.py`, one fresh boot world per row, through `POST /command`:

```
> what happens if I attack Deroy                         success=True  AP 4->4
  Were you to give the order, Sire:
  MUSTER — Bernadotte (17,000) vs Deroy (22,000 men) at Franconia — the
  balance of force looks even.
    Franconia feeds 60,000 — the whole muster can stand there fed.
    Every corps in the province shares the field — that is the design. ...
  Nothing has been ordered, and nothing spent.

> Bernadotte, attack Deroy                               success=False AP 4->4
  Bernadotte cannot attack Bavaria — they are our ally, Sire, and we are not
  at war with them.
```

Alliance, war and betrayal appear nowhere in the answer. The docstring's promise
— *"the player is told exactly what he would be told a moment later"* — is false
here. **Confirmed.** `p7` shows the same shape for **VASSAL** (staged): *"...they
are our vassal, Sire..."*.

**Player-reachable: YES**, and I checked the client rather than assuming.
`main.gd:2031` runs `_is_advisory_question` **before** any redirect, and
`DIPLO_ADVISORY_STARTS` (`main.gd:1997`) contains `"what"`, so
`_redirect_diplomatic_command` returns false and the sentence reaches the
backend untouched.

**Shipped by row CX: YES**, verified against the pre-row tree, not the commit
stat. The scratchpad `pre_cx/` tree is byte-identical (LF-normalised) to
`b4a27a15^` for `question_desk.py`, `llm_client.py`, `parser.py`,
`meta_executor.py` and `main.py`. Driving it (`p5_prerow.py`):

```
pre-row:  what happens if I attack Deroy  -> 12,717 chars of COMMAND REFERENCE
pre-row:  Bernadotte, attack Deroy        -> the SAME ally refusal (pre-existing)
```

`_answer_what_if` and `classify_board_question` do not exist before CX-2. The
refusal is old; **the false muster in front of it is CX-2's.**

---

## 2. The peace half — REFUTED

The filed body says `what happens if I attack Brunswick` "likewise musters
against Prussia at PEACE", and leans on it for the FA-80(c) / "act of war
against a neutral" argument. **A court at PEACE is attackable by design, and the
order goes through.**

`world_state.py:2523 can_attack_nation` says so in its own docstring — *"A
NEUTRAL (PEACE) target stays attackable: attacking a neutral is the intended
auto-war-declaration path"* — as does `combat_executor.friendly_fire_refusal`
(*"else None ... declaring war on a neutral as before"*). Measured, `p2`/`p4`/`p6`:

```
> Bernadotte, attack Brunswick                           success=TRUE
  Bernadotte challenges the order: 'The odds are not in our favor...'
> insist                                                 success=TRUE  AP 4->3
  ... Choose your war purpose against Prussia. Issue the attack again after the
      declaration is settled.
  [war_purpose_popup] target_nation=Prussia  (Conquest / Forced Alliance / Subjugation)
```

and on a staged board where the odds are favourable so **no objection fires at
all** (`p6`, Bernadotte 90,000):

```
> what happens if I attack Brunswick   -> MUSTER ... "looks favorable"
> Bernadotte, attack Brunswick         -> success=TRUE, war_purpose_selection
                                          NAMING Prussia, before any battle
```

So for a court at peace the order is legal, the war is **named in a blocking
modal of its own**, and the desk's muster is the same account the order gives —
including the odds band that is the reason the marshal objects. **No
shown-not-applied.** The filed reproduction never issued the Brunswick order.

The counsel-parity argument is a **category error, and `counsel.py`'s own
comment forecloses it**: that guard exists because `military_counsel` produces
*"a target the player is TOLD to attack"*. The desk answers a target the player
named. Measured (`p10`): `military_counsel(boot, "France")` returns
`['Ney, attack Mack', 'Ney, march to Lorraine', 'Ney, fortify', 'Ney, drill']` —
the game **never proposes** the Bavarian. `test_cx2`'s own docstring at line 463
states the same distinction.

---

## 3. Severity — P2 is over-graded; P3

Full census (`p8_census.py`), every non-player marshal, one fresh world per row,
both sides driven through `POST /command`:

| board | desk musters | order refused for a diplomatic reason |
|---|---|---|
| shipped 1805 boot, turn 1 | 4 of 14 | **1** (Deroy) |
| committed fixture `t20` | 1 of 17 | **0** |

No figure is wrong, nothing is spent (AP 4->4 on every question), no state moves,
and the player loses one keystroke. Against its own siblings in the same report
— DESK-1 names 10 of 14 fogged provinces, DESK-2 misprices the levy by 13-53%
and overstates the amount 3.3x — this does not sit at the same grade.

**Ceiling, in fairness to the finding:** it is not a one-court curiosity. Staged
an armistice with Austria at boot (`p9`) and the count goes **1 of 4 mustered ->
3 of 4** (Mack, ArchdukeJohn, Deroy). That is the case the filing missed, and it
is the one that occurs in a played campaign.

---

## 4. The filed fix would ship a regression, and would miss the wider case

> *"ask the same question the executor asks before mustering; when not at war,
> answer with the refusal the order gives (and, for a court at peace, name the
> Cabinet)."*

**(a) There is no single question.** The executor refuses on **two** predicates:
`combat_executor.friendly_fire_refusal` -> `can_attack_nation` (OWN / ALLIANCE /
DEFENSIVE_ALLIANCE / VASSAL) and `executor._make_diplomatic_error:655`
(**ARMISTICE only**). `can_attack_nation("France","Austria")` returns **True**
under an armistice (`p7`), so gating on it alone leaves this standing:

```
[ARMISTICE with Austria]
> what happens if I attack Mack  -> MUSTER ... "the balance of force looks favorable"
> Ney, attack Mack               -> FAILED "Cannot attack Mack — armistice with
                                    Austria (5 turns remaining)."
```

**(b) The "when not at war" clause is the regression.** It would replace a
*correct* muster for Brunswick with a refusal the executor never gives —
manufacturing the same shown-not-applied defect in the opposite direction, on
the more common state. It reds no committed pin (every `what happens if I
attack` pin in `test_cx2_berthier_answers_the_board.py` — the TWELVE list at
:133 and `test_the_muster_is_the_attack_s_own_string` at :175 — uses **Mack**,
at war), which is exactly why it would ship silently. The sentence it breaks is
the Brunswick muster measured in section 2.

**(c) "name the Cabinet" is wrong for the case it is offered for.** The tactical
attack on a peace court *is* the declaration road, via `war_purpose_selection` —
no Cabinet visit is required or useful.

**What to build instead:** one shared predicate over the executor's **real**
refusal set (both sites), consulted by `_answer_what_if` before it musters, and
scoped to the road the desk itself chose — the desk only musters co-located or
adjacent, i.e. the TACTICAL road, so PEACE must stay musterable. A court at
peace deserves at most one added clause naming the war-purpose step: a P4
nicety, not this row.

---

## 5. Found while refuting — worse than what was filed, and not the desk's

The CX-3 completer's enemy pool is `game_state["enemies"]`, built by
`main.py:212 get_llm_game_state` from `get_enemy_marshals()` — **fog-filtered
but not at-war filtered**. Measured off the real `/command` payload (`p12`),
`Deroy` (our ALLY) is in the pool the client holds.

Re-implementing `main.gd::_build_completions` faithfully (verb table
`main.gd:6882`, `["attack","E"]`; `MAX_SUGGESTIONS = 5`;
`COMPLETIONS_ACTIVE = true`; rendered on `text_changed`, accepted with Tab) and
then driving every line it returns (`p13`):

```
typed 'Bernadotte, attack '  -> offers 4:  ...Archduke John / ...Brunswick / ...Deroy / ...Mack
   'Bernadotte, attack Deroy'     success=False  "cannot attack Bavaria — they are our ally"
typed 'Ney, attack '        -> offers 4:  ...Archduke John / ...Brunswick / ...Deroy / ...Mack
   'Ney, attack Brunswick'        success=False  "We are not at war with Prussia, Sire —
                                                  Brunswick may not be attacked while the
                                                  peace holds."   (out of range -> the
                                                  STRATEGIC road, strategic.py:181)
   'Ney, attack Deroy'            success=False  "cannot attack Bavaria — they are our ally"
```

So the game **offers**, on screen as the player types and one Tab away, a
sentence it will not carry out — 1 of 4 for Bernadotte, **2 of 4 for Ney**. That
is strictly worse than answering one the player named, and it is CX-3's own
stated rule (*"the game must not offer a sentence it cannot read"*) one step
out: the sentence **parses**, so that census is structurally blind to it. Filed
here as a neighbourhood finding for the CX-3 lens. It is not `_answer_what_if`'s
defect and does not change this verdict, but it does mean the ally hole is
reachable without a question being asked at all.
