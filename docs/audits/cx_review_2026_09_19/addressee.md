# LENS 2 — ATTACKING THE COMMA-LESS ADDRESSEE RULE

**Tree:** `master 727cf88a`, clean, read-only. **Board:** the shipped 1805
scenario, a **fresh world per utterance**, driven at `POST /command` through
`backend.main`'s TestClient with the world/game_state/parser triple swapped —
the same harness `tests/test_cx1_a_question_never_orders.py` uses.
**Probes:** `.../cx_review/probes/p1..p16*.py` (scratchpad only; nothing in the
repo was touched).

**Sanity first:** `pytest tests/test_cx1_a_question_never_orders.py -k
TestAnAddressNeedsNoComma` is **20 passed** on this tree. Every finding below is
invisible to those twenty pins.

---

## THE ONE-LINE VERDICT

> **The rule works for the two verbs its own tests use and for nothing else.**
> Measured over 14 unbindable addressees × 24 order forms on a fresh board each
> (336 drives, `p14_final.py`): **274 EXECUTED**, 18 were refused by the CX-1
> rule, 44 were inert for an unrelated reason. Every one of the 18 refusals is
> on `attack` or `retreat`.

And the mirror defect: the same predicate **refuses 23 measured real orders**
that marched before the row landed (`p4_lever.py`, `p16_fp_drive.py`).

The root is one design choice. `_unbound_addressee` asks *"does the leading run
contain grammar?"* when the question it needs answered is *"is the leading run a
**name**?"* Both failure directions fall out of that: a run with one filler word
in it is never a name (274 executions), and a run with no filler word is always
a name (23 refusals of `quickly`, `cavalry`, `ok`).

---

## FINDING L2-1 (P1) — THE RULE IS ONE VERB WIDE

`_ADDRESSEE_IS_AN_ORDER_RE` is how the comma-less arm locates the addressee: no
verb found → `return None` → the guard stands down entirely. A **drift census**
of every verb that routes to a marshal-LESS command type, measured against that
regex (`p6_census.py`):

> **28 of 36 routed verbs are missing. The regex covers 8:**
> attack · assault · bombard · charge · chase · engage · pursue · storm.
>
> **Missing:** ambush · annihilate · barrage · cannonade · capture · conscript ·
> crush · defeat · destroy · fight · harry · hound · hunt · keep watch ·
> obliterate · observe · occupy · pull back · recon · reconnaissance · retire ·
> rout · seize · shadow · shell · smash · strike.

They are not obscure. They are `backend/ai/attack_vocabulary.py`'s own
`BATTLE_VERBS` / `CAPTURE_VERBS` / `PURSUIT_VERBS` / `BOMBARD_VERBS` — a module
whose docstring exists **because three seams carried three silently-diverging
copies of "what counts as an attack word".** This is the fourth copy.

Driven end to end (`p7_drive_all.py`), on a fresh 1805 boot, by a player who has
named nobody:

| utterance | measured |
|---|---|
| `Zorglub attack Mack` *(the row's own control)* | refused free — AP 4, gold 800 |
| **`Zorglub crush Mack`** | **a real battle.** AP 4→3, gold 800→546, Davout/Lannes/Murat moved |
| `Zorglub smash / destroy / annihilate / obliterate / rout / strike / defeat / fight / ambush Mack` | a real battle, all nine |
| `Zorglub occupy / capture / seize Swabia` | a real battle, all three |
| `Zorglub hunt / hound / intercept / harry / shadow Mack` | a PURSUE order to Soult, 1 AP — **and rider (d) quotes the sentence back as the record:** *"Zorglub hunt Mack"* |
| **`Zorglub pull back`** · **`Zorglub retire`** | **GENERAL RETREAT — eight corps fall back**, 0 AP. This is the spec's own §3.1 headline (`Wellington retreat` "marched the entire army back") reachable one word over |
| `Zorglub recon / reconnaissance / observe Swabia`, `Zorglub keep watch on Swabia` | Soult scouts, 1 AP |
| `Zorglub shell / barrage / cannonade Swabia` | *masked at boot* — see below |

**The bombardment arm is masked, not safe.** At boot the executor answers *"No
artillery marshals available for bombardment"*, so the three verbs look inert.
Give one corps guns — which the player does by typing `recruit artillery` — and
`Zorglub shell Swabia` **fires Ney's guns and spends 1 AP**, while
`Zorglub bombard Swabia` refuses (`p13_artillery.py`).

**Player-reachable: yes.** `main.gd::_redirect_diplomatic_command` intercepts
only the diplomatic families (`DIPLO_NO_HOME_KEYWORDS`, `DIPLO_WAR_ROOM_KEYWORDS`,
`DIPLO_FAMILY_KEYWORDS`, the nation-gated prefixes); none of these verbs appears
in any of them and none of these sentences names a nation, so the terminal sends
them verbatim.

**Shipped by this row: no** — the *behaviour* is FA-22's, pre-existing. But
`COMMAND_EXPERIENCE_SPEC.md` §3.1 records it as closed (*"far wider than a typo:
`Grouchy attack Mack` … `Zorglub attack Mack` all sent Soult in"*), and what
actually closed is 8 verbs of 36. The record over-claims.

**Fix shape.** Do not extend the literal. Derive the alternation from the
existing single source — `attack_vocabulary`'s four sets plus the mock chain's
own retreat/scout branch words — and add a **drift census pin** in the CX-3
idiom: *every verb the mock parser routes to a marshal-less type must be
findable by the addressee regex*, mutation-tested. That pin is what this slice
needed and does not have.

---

## FINDING L2-2 (P1) — `general_defensive` IS A SIXTH MARSHAL-LESS TYPE AND THE TUPLE OMITS IT

`parser._classify_command` produces **six** marshal-less types (`p1_types.py`),
not five:

```
attack          -> general_attack            OK  in _MARSHAL_LESS_TYPES
attack <x>      -> auto_assign_attack        OK
retreat         -> general_retreat           OK
scout <x>       -> auto_assign_scout         OK
bombard <x>     -> auto_assign_bombardment   OK
defend          -> general_defensive         ** NOT IN THE TUPLE **
```

So `_unbound_addressee` returns `None` on its **first line** for every `defend`
sentence and the guard never runs — **comma or no comma**. Measured
(`p2_unbound_leak.py`, `p7_drive_all.py`):

| utterance | measured |
|---|---|
| `Zorglub defend` | *"All forces take defensive positions: Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena…"* — 1 AP |
| `Wellington defend` · `Berthier defend` · `Grouchy defend` | identical |
| **`the Iron Marshal, defend`** | identical — **FA-22's own named case, in FA-22's own punctuation** |
| **`Wellington, defend`** | identical |
| `Zorglub, defend` | refused — but by the *parser's* single-token `Marshal 'Zorglub'` path, not by this guard |

I checked all five tuple members as the lens asked: the five that are there are
each genuinely produced and each genuinely reaches the guard. The hole is the
sixth type, not one of the five.

**Player-reachable: yes** — `defend` is in the completer's own `_MARSHAL_VERBS`
table, so the game teaches the verb.
**Shipped by this row: no** — FA-22's omission, untouched by CX-1, which widened
the *punctuation* rule without re-reading the *type* list.

**Fix shape.** Add `"general_defensive"` to `_MARSHAL_LESS_TYPES`, and pin the
tuple against `_classify_command`'s own return values by census, so a seventh
type cannot be added without the guard learning it.

---

## FINDING L2-3 (P2) — THE ARTICLE HOLE: FA-22's THREE NAMED CASES, ONE KEYSTROKE OVER

`_NOT_AN_ADDRESS_RE` contains `the`, and the stand-down is tested **before** the
`phrase.lower().startswith("the ")` strip eleven lines below. So every articled
address disarms the comma-less arm (`p12_the.py`):

| utterance | measured |
|---|---|
| `the Iron Marshal, attack Mack` | refused free — *"There is no 'Iron Marshal'…"* |
| **`the Iron Marshal attack Mack`** | **a real battle.** AP 4→3, Davout/Lannes/Napoleon moved |
| **`the Prince of Moskowa attack Mack`** | **a real battle** |
| `the cavalry, attack Mack` | refused free |
| **`the cavalry attack Mack`** | **a real battle** |

`the Iron Marshal`, `the Prince of Moskowa` and `the cavalry` are precisely the
three examples the executor's own FA-22 comment block cites at line 1576. The
comma form refuses them; the comma-less form — the one CX-1 exists to close —
fights.

**Fix shape.** Strip the leading article **before** the stand-down test, and drop
`the` from the function-word set (it is a determiner on a name, not grammar that
proves the run is not a name). The collective words already cover `the army` /
`the cavalry` on their own.

---

## FINDING L2-4 (P2) — ONE FILLER ANYWHERE IN THE RUN DISARMS THE GUARD

`_NOT_AN_ADDRESS_RE` is applied with `.search()` over the **whole** leading run,
so a single function word anywhere in it stands the rule down however plainly the
run also names somebody (`p12_the.py`):

```
Zorglub just attack Mack      -> a real battle, AP 4->3
Zorglub now attack Mack       -> a real battle
Zorglub then attack Mack      -> a real battle
Zorglub first attack Mack     -> a real battle
Zorglub still attack Mack     -> a real battle
Zorglub you attack Mack       -> a real battle
Zorglub please attack Mack    -> a real battle
Zorglub's corps attack Mack   -> a real battle   ("corps" is in the set)
```

Same root as L2-3, and the reason a single-word fix there is not enough.

**Fix shape.** Test the **head** of the run, not the whole run: after stripping a
leading article, if the first token is a function word or a collective the run is
grammar; otherwise the run is an address and any remaining fillers are noise.
That one change closes L2-3 and L2-4 together and does not touch the polite
imperative (`can you attack Mack`, `do attack Mack`, `please attack Mack`), whose
function word **is** the head — verified in `p3_false_pos.py`, all three still
`guard=None`.

---

## FINDING L2-5 (P3, **SHIPPED BY THIS ROW**) — A RUN WITH NO FUNCTION WORD IS TREATED AS A NAME

The mirror of L2-4, and the only finding here the row genuinely introduced.
Measured at both lever positions, end to end (`p4_lever.py`, `p16_fp_drive.py`):
**23 of 28 probed shapes are NEW refusals** — they executed with
`AN_ADDRESS_NEEDS_NO_COMMA = False` and are refused with it `True`.

```
quickly attack Mack       lever OFF: a battle, AP 4->3   lever ON: "There is no 'quickly' in the order of battle"
immediately attack Mack   lever OFF: a battle            lever ON: "There is no 'immediately' ..."
cavalry attack Mack       lever OFF: a battle            lever ON: "There is no 'cavalry' ..."
infantry attack Mack      lever OFF: a battle            lever ON: "There is no 'infantry' ..."
ok attack Mack            lever OFF: a battle            lever ON: "There is no 'ok' ..."
okay retreat              lever OFF: a general retreat   lever ON: "There is no 'okay' ..."
tonight retreat           lever OFF: a general retreat   lever ON: "There is no 'tonight' ..."
Marshal attack Mack       lever OFF: a battle            lever ON: "There is no 'Marshal' ..."
```

plus `urgently`, `quick`, `hurry`, `today`, `finally`, `instantly`, `promptly`,
`yes`, `alright`, `right`, `well`, `General`, `guards`, `gentlemen`, `artillery`.

**Held at P3 deliberately, and here is the measurement that holds it there:**

* The refusal is **free** — it returns before any AP or gold is touched. Nothing
  is lost but the sentence.
* **0 of 794** recorded utterances trip it — every golden-corpus row (437) plus
  every string in `tools/playtest_scripts/*.json`, at both lever positions
  (`p5_corpus.py`). The only four hits are the row's own intended cases
  (`nay attack wellinton`, `Nay attack Mack`, `Zorglub attack Mack`,
  `Wellington retreat`).
* **0 of 101** command-shaped strings the game itself prints trip it — the
  COMMAND REFERENCE, the completer's `_MARSHAL_VERBS` table read out of
  `main.gd` (filled with real 1805 names, in both comma and comma-less form),
  and the chip templates (`p11_printed.py`). Every client chip builds
  `"<Name>, <verb>"` **with** the comma (`region_panel.gd:134`,
  `counsel.py:128-177`, `clarification.py:157/200/253/311/363`), so the CX-3
  rule — *the game must not offer a sentence it cannot read* — is not breached.

It is a legibility regression on natural English, not a mechanical one. The
head-token fix in L2-4 closes it in the same edit.

---

## FINDING L2-6 (P3) — THE COLLECTIVE GUARD IS IN THE WRONG BRANCH

`_NOT_AN_ADDRESS_RE` is tested **inside** `if not sep:`. The comma path never
sees it, so the same collective is read two ways (`p3_false_pos.py`,
`p4_lever.py`):

```
all marshals attack     -> executes (guard None)      <- the CX-1 comment's own case
all marshals, attack    -> REFUSED: "There is no 'all marshals' in the order of battle"
everyone retreat        -> executes
everyone, retreat       -> REFUSED: "There is no 'everyone' ..."
the army retreat        -> executes
the army, retreat       -> REFUSED: "There is no 'army' ..."
gentlemen, attack Mack  -> REFUSED
marshals, attack        -> REFUSED
```

Pre-existing (FA-22), and the comma form is the more natural way to write it. The
row's own pin `test_a_collective_address_is_not_an_unbound_name` tests **only**
the comma-less form — and two of its four cases (`the army attack`,
`every corps retreat`) would pass anyway on `the` / `corps` via L2-3/L2-4 rather
than on the collective rule, so the pin is weaker than it reads.

**Fix shape.** Hoist the collective / function-word test out of the `if not sep:`
branch so both punctuations answer alike. Note the design question it exposes:
`Marshal, attack Mack` (a bare honorific) arguably deserves the CR-2
*"Which marshal, Sire?"* clarification rather than a refusal naming "Marshal" as
an unknown officer.

---

## FINDING L2-7 (P2) — THE SEAM BETWEEN CX-1's TWO ARMS: A TWO-WORD SUBJECT IS NEITHER

The lens asked for a sentence that is **neither** refused as an unbound addressee
**nor** read as a question, and executes something unasked. There is one, and it
is the game's own printed name (`p8_interaction.py`, `p9_twoword.py`):

```
can Ney attack Mack                              -> a question (control)   inert
can Archduke Charles attack Mack                 -> A REAL BATTLE. AP 4->3, Soult musters against Mack
may / could / might Archduke Charles attack Mack -> a real battle, all three
can Archduke John attack Mack                    -> A REAL BATTLE. Massena vs ArchdukeJohn
can Archduke Charles retreat                     -> GENERAL RETREAT, eight corps
```

Both guards decline, for different reasons:

* **arm (d)** reads **one** word after the lead (`_SUBJECT_AFTER_LEAD_RE`,
  `(?P<subj>[A-Za-z][\w'-]*)`, with `HONORIFIC = marshal|general|gen\.|marechal`
  — no *archduke*, *prince*, *duke*). The subject token is `archduke`; the roster
  key is `ArchdukeCharles`; no match, so not a question.
* **the address arm** stands down because the leading run `can ` holds a function
  word (L2-4's root again).

**Measured at both positions of `A_QUESTION_NEVER_ORDERS`: identical.** So this is
**not** shipped by CX-1 — but arm (d) is the guard that owns the shape, and the
spec's §3.1 describes it as *"given the live roster"*. The roster it is given is
keys; the player reads display names.

**Size of the hole on the shipped board** (`p10_multiword.py`): **2 of 22
commanders** print as two words (`ArchdukeCharles` → *"Archduke Charles"*,
`ArchdukeJohn` → *"Archduke John"*) and **6 of 126 provinces** contain a space
(East Anglia, East Frisia, East Prussia, La Mancha, New Russia, White Russia).
This is CX3-X1 / IQ10-6 one layer out — *the game prints a name whose question
form its own guard cannot read.*

**Fix shape.** Match the subject **greedily against the live subject list**
(longest name first, on the humanised form) instead of taking one token, or add
the printed honorifics to `HONORIFIC`. The first is the real fix; the second is a
plaster that misses `La Mancha`.

---

## WHAT I CHECKED AND FOUND CLEAN (stated so it is not re-checked)

* **`_MARSHAL_LESS_TYPES`' five members** are each genuinely produced by
  `_classify_command` and each genuinely reaches the guard. The tuple is right as
  far as it goes; L2-2 is about the sixth type, not these five.
* **No live name collides with `_NOT_AN_ADDRESS_RE`** — 0 of 22 commanders and 0
  of 126 provinces contain any of its words (`p10_multiword.py`), so the
  stand-down cannot fire on a real marshal's or province's own name.
* **Every client chip and every backend clarification option carries the comma.**
  `region_panel.gd:134` emits `"<Name>, <verb>"`; all five `clarification.py`
  builders set `"command": f"{m.name}, …"`; `counsel.py`'s six suggestion lines
  all carry it.
* **The one comma-less string the client builds is not reachable with a dangerous
  name.** `main.gd::_on_clarification_choice_made` composes
  `marshal_name + " " + keyword + " " + chosen_target` with **no comma**, and
  `clarification_popup.gd:32` defaults `current_marshal` to the literal
  `"Marshal"` while `_clarification_response` titles its questions
  `"marshal": "Berthier"` — either of which would now be refused as an unknown
  officer (measured: `Marshal attack Mack`, `Berthier attack Mack`). It does
  **not** fire today: that route (`clarification_popup.gd:113`) is taken only
  when an option carries `target` and **no** `command`, and every Berthier-titled
  builder sets `command`. Recorded as a latent hazard for whoever next adds a
  command-less option, not filed as a defect.
* **`Davoust attack Mack`** still repairs to Davout rather than refusing (FA-80),
  exactly as the spec pins.
* **`Zorglub give them hell`** asks *"Which marshal shall lead the attack, Sire?"*
  — the right outcome, reached by the bare-`general_attack` clarify path rather
  than by the guard.
* **`do it` / `Ney, do it`** (CX-6's own case) are inert and shrug, in both
  directions.

---

## THE ONE EDIT THAT CLOSES FOUR OF THE SEVEN

L2-3, L2-4, L2-5 and L2-6 are one predicate, wrongly framed. Replacing

> *the run is not a name if it **contains** grammar*

with

> *strip a leading article; the run is not a name if its **first token** is a
> function word or a collective; otherwise it is an address*

closes all four in one edit, and leaves the polite imperative (`can you`, `do`,
`please`) untouched because there the function word **is** the head. L2-1 and
L2-2 are separate, and are the P1s: a derived verb alternation with a drift
census, and the sixth command type.

⛔ **The lesson this lens re-earns, in the row's own idiom:** *the pins were
written on the two verbs the finding happened to use.* `attack` and `retreat`
are 8 of the 36 doors into the same room, and the other 28 were never opened.
