# LENS 3 — ATTACKING THE QUESTION DESK AND THE COUNSEL (CX-2)

Review of `backend/ai/question_desk.py` (CX-2 half), `backend/ai/counsel.py`
and `meta_executor._route_unanswered_question`, at master `727cf88a`, clean.

**Method.** Every claim below was reproduced by a probe I ran, on the shipped
1805 board (`parser_eval.build_world("1805")`) or on the committed played
fixture `tests/fixtures/playtest_saves/fixture_t20_ambient.json`, driven
through `POST /command` (the production surface) unless stated. Probes are in
`…/scratchpad/cx_review/lens3/` (`dh.py` + `p02`…`p23`). Client reachability
was decided by re-implementing `main.gd::_redirect_diplomatic_command` from
the `.gd` source (`p18_client_gate.py`), not assumed.

**Headline.** The slice's central promise — *"Every answer reads the seam the
MECHANIC reads … so a quoted figure is the applied figure and the two cannot
drift"* — holds for the **build** arm and for the **muster renderer**, and
fails for **five of the nine board kinds**. Two of those failures are the
row's own sibling guards not being carried across: `counsel._is_free_to_order`
and `counsel`'s at-war check exist, with comments explaining exactly why, and
the desk arms written in the same slice have neither.

---

## WHAT I TRIED TO BREAK AND COULD NOT (report these as holding)

Stated first because they are the things that would have been worst.

* **No crash arm found.** 14 utterances × 5 hostile boards (legacy 19-region
  fixture · 1805 with every war set to PEACE · a captured player marshal ·
  every French marshal captured · France at zero provinces · France with no
  army · an eliminated court) produced **zero** `[QUESTION DESK] could not
  answer` prints and zero raised exceptions (`p09_crashes.py`,
  `p10_edge_answers.py`). The silent-except arms are not currently masking
  anything on these boards.
* **Asking does not stamp the combat transients** (`p20_transients.py`). This
  was the CA8-19 class and I pushed hard on it: the only write is
  `sovereign_presence: <absent> → 0.0`, which is the identity value at every
  reader (`float(getattr(...) or 0.0)`), does **not** compound over ten
  repeats, and does not reach `total_coordination_*`, the `_display_*` fields
  or `_jealousy_solo_attack` — including the adversarial arm with the Emperor
  standing among the joiners. `_build_muster_preview`'s `_saved`/`finally`
  block does its job.
* **Asking costs no AP and starts no battle** on every kind, on both boards.
* **The build prices are exactly applied**: desk quotes depot 300g /
  fortification 400g / market 350g at Rhineland; typed builds charge
  300 / 400 / 350 (`p21_final.py`).
* **The muster really is the attack's own string.** The header the desk prints
  for `what happens if I attack ArchdukeJohn` is byte-identical to the header
  the real `Bernadotte, attack ArchdukeJohn` prints (`p15_neutral_and_tag.py`).
  That claim in §3.2 is true.

---

## FINDINGS

### DESK-1 (P2, fog) — `_answer_what_if` names a fogged enemy's exact province

`question_desk._answer_what_if` (≈line 690) resolves the foe from the
deliberately omniscient `_askable_enemy_names` roster, then reads
`enemy.location` and prints it, **with no visibility check anywhere in the
arm**.

Measured strictly by cell visibility (`p23_strict.py`):

| board | enemy corps | province named although the cell is **UNKNOWN** |
|---|---|---|
| shipped 1805 boot, turn 1 | 14 | **10** |
| committed fixture `t20` | 17 | **9** (+1 at STALE) |

Boot leak list: ArchdukeCharles→Carniola, Kutuzov→Podolia, Buxhowden→Volhynia,
Moore→London, Hohenlohe→Silesia, Armfelt→Scania, Damas→Naples,
Frederick→Jutland, Castanos→La Mancha, Abdurrahman→Karaman.

**Reproduction** (`p22_leak_census.py`, through `POST /command` on a fresh
boot board):

```
> why not attack Kutuzov
No corps of ours stands within reach of Kutuzov at Podolia, Sire —
there is no battle to weigh.                                   [AP 4 -> 4]

> where is Kutuzov
We have no word of Kutuzov's whereabouts, Sire.
```

Two answers, one desk, one board, one turn, disagreeing about whether France
knows where Kutuzov is. **All eight phrasings reach it** — `what happens if I
attack` / `should I attack` / `why not attack` / `what about attacking` / `is
it time to attack` / `what if we attack` / `could I attack` / `how about we
attack` — and CX-1 is what routed the musing forms here.

The contract this breaks is written in this row's own source, in
`llm_client._askable_enemy_names`: *"Naming him is not a fog secret … his
POSITION is the fogged half, and the desk answers it honestly ('no word of
Kutuzov's whereabouts')."* The sibling arm `_answer_enemy` carries the exact
guard needed (`world.get_region_intel(marshal.location).visibility_at_least(PARTIAL)`).

**Player-reachable:** yes. `_is_advisory_question` exempts every `what`/`why`
lead, and `should I attack X` / `could I attack X` are "not claimed" by the
redirect — all reach the backend (`p18_client_gate.py`).

**Shipped by this row:** yes (CX-2).

**Fix shape:** gate the arm on the same `visibility_at_least(PARTIAL)`
predicate `_answer_enemy` uses; when the cell is not in view, answer with
`_answer_enemy`'s own "we have no word of his whereabouts" rather than a
muster. Do **not** fix it by narrowing the roster — the roster is deliberately
omniscient about names and `_question_subjects` depends on that.

---

### DESK-2 (P2, shown ≠ applied) — the levy answer is wrong in all three figures

`_answer_price` and `counsel._levy_terms` both read
`get_levy_status(...)["infantry_price"]`, which is priced **at the capital**
(`economy_executor.py:2454-2459`: `capital = world.get_nation_capital(nation)`),
with **no recruiting marshal** — and then name a *different* province, taken
from `_first_own_region_with_a_corps`. `get_levy_status` has no `region` key at
all (verified: key list is `army_strength, capital_held, closed_reason,
force_limit, headroom, infantry_amount, infantry_pool, infantry_price, open,
over_by, recipient_in_range, substitutes`), so `_levy_terms`'s
`levy.get("region")` is always `None` and the fallback always fires.

**Reproduction — shipped 1805 boot** (`p02_levy.py`, `p12_1805_levy_drive.py`):

```
> how much is a battalion
654 gold for 10,000 infantry, Sire, at Rhineland. The price rises at war
and above the force limit.

> recruit infantry in Rhineland
Davout recruits 3,000 infantry for Rhineland … Cost: 741 gold
                                        (Davout's intendance: -15%)
> recruit for Ney
Ney recruits 3,000 infantry at Rhineland … Cost: 1003 gold
                                        (Ney's intendance: +15%)
> recruit infantry in Paris          # the province 654 IS the price of
FAILED — "No marshal is available to receive reinforcements at Paris, Sire."
```

So: price understated by **+13% to +53%**, amount overstated **3.3×**
(10,000 vs the 3,000 field-levy cap), and the one province where 654 is the
true figure is the one the executor refuses.

The same root, measured end to end on the legacy board — the only board where
the counsel's priced line renders at all (`p11_drive_counsel_levy.py`):

```
counsel prints : recruit infantry in Belgium — 150g for 10,000 men
player types   : recruit infantry in Belgium
game answers   : Berthier notes: 'Marshal Ney commands cavalry, Sire.'
                 Ney recruits 3,000 cavalry … Cost: 300 gold
QUOTED 150g / CHARGED 300g  (+100%) — and cavalry, not infantry; 3,000, not 10,000
```

`get_levy_status` already *knows* about the arm — `LEVY_NAMES_ITS_RECIPIENT_ARM`
sets `open=False` and writes a `closed_reason` naming the cavalry recipient —
and neither consumer reads `open` or `closed_reason`.

Note also that this makes the desk **less** honest than the ledger it is
reaching parity with: `ledger.py`'s own `cost_note` says *"Live price at the
capital — war, stability, force limit **and the recruiting marshal** all move
it"*, while the desk attaches the capital figure to a named non-capital and
discloses only two of the four terms.

**Rider (P3):** on the shipped campaign `_levy_terms` returns `None` on both
the boot board and `t20` (`recipient_in_range` is False — every French corps
is 4–6 provinces from Paris), so the one priced economy line the module
docstring is built around never renders in ordinary 1805 play.

**Player-reachable:** yes (`how much is a battalion` → advisory lead `how`).
**Shipped by this row:** yes (CX-2).

**Fix shape:** price through `_calculate_recruit_cost` at the province the
answer names, passing the marshal who would receive them, and quote the
delivered amount (the field-levy cap) rather than `INFANTRY_RECRUIT_AMOUNT`;
or, at minimum, say "at the capital" and name the terms the ledger names.

---

### DESK-3 (P2, shown ≠ applied) — `_answer_reach` says YES across a sea the crossing gate bars

`_answer_reach` calls `world.find_path(..., passable_for=player)` directly.
`strategic.plot_route`, the seam FA slice 5 built to be the single source,
says in its own docstring that **"the pathfinders are edge-blind to sail"** and
returns `naval_leg` / `naval_check` for exactly this case.

**Reproduction** (`p06_reach_naval.py`, fresh boot board, Davout moved to the
Normandy shore):

```
> can Davout reach London
Yes, Sire — Davout can reach London from Normandy in 1 turn: Normandy -> London.

> Davout, move to London
FAILED — "The crossing from Normandy to London is barred — the Royal Navy
commands the water with 100 sail (100 effective) against our 54…"
```

`plot_route(w, Davout, "London", use_weighted=False, want_verdict=True)` on
the same board returns `naval_leg: ('Normandy','London')` with that refusal
message already in hand. From Rhineland the desk prints a six-province road to
London, and `can Ney reach Ulster` prints a **twelve**-province road across the
Channel and up through Britain — contradicting NAVAL_SPEC's headline anchor A5
in writing.

`_answer_reach`'s docstring — *"asked of `find_path` with the MOVEMENT LAW
applied (`passable_for`), so the answer is the road he would actually be
allowed to walk"* — is therefore false as written.

**Player-reachable:** yes (`can …` is "not claimed" by the client redirect).
**Shipped by this row:** yes (CX-2).

**Fix shape:** call `plot_route(..., want_verdict=True)` and render the
verdict: `legal` → yes; `naval_leg` → the crossing message; `blocker_region` /
`closed_destination` → the existing "not lawfully" arm (which already works —
`can Ney reach Constantinople` is answered correctly today).

---

### DESK-4 (P2, shown ≠ applied) — the desk weighs an attack on an ALLY, and on a court at peace

`_answer_what_if` has no diplomatic-state check.

**Reproduction** (`p15_neutral_and_tag.py`, `p16_attack_ally.py`, boot board;
`world.get_diplomatic_state("France","Bavaria") == "ALLIANCE"`):

```
> what happens if I attack Deroy
Were you to give the order, Sire:
MUSTER — Bernadotte (17,000) vs Deroy (22,000 men) at Franconia —
the balance of force looks even.
   … (no mention of war, alliance or betrayal anywhere in the answer)

> Bernadotte, attack Deroy
FAILED — "Bernadotte cannot attack Bavaria — they are our ally, Sire,
and we are not at war with them."
```

`what happens if I attack Brunswick` likewise musters against **Prussia, at
PEACE** — the very court CX-2 removed from the Berthier shrug *because*
proposing action against it was "an act of war against a neutral". The
docstring's promise — *"the player is told exactly what he would be told a
moment later"* — is measurably untrue here: the order cannot be given at all.

`counsel.military_counsel` carries the guard and a nine-line comment
(`counsel.py:113-124`) explaining that it is kept deliberately even though
redundant today, because *"the cost of an upstream widening is the game
proposing a war on a neutral."* The desk arm written in the same slice has no
such guard.

**Player-reachable:** yes. **Shipped by this row:** yes (CX-2).

**Fix shape:** ask the same question the executor asks before mustering; when
not at war, answer with the refusal the order gives (and, for a court at
peace, name the Cabinet).

---

### DESK-5 (P2, legibility / a false account) — the treasury answer's own arithmetic contradicts its Net, and inverts the sign on a played board

`_answer_treasury` names four of the ~15 signed Net components and presents
them as an account.

**Reproduction** (`p03_applied.py`):

| board | the sentence | its own sum | stated Net | gap |
|---|---|---|---|---|
| 1805 boot | "provinces yield 3,400 and trade 350; the army costs 2,630. Net +1,842" | +1,120 | +1,842 | **+722** |
| fixture `t20` | "provinces yield 2,350 and trade 350; the army costs 980. **Net −876**" | **+1,720** | −876 | **−2,596** |

On the played board the three named figures say the empire is making
**+1,720 a turn** and the fourth says it is **losing 876**. The gap reconciles
exactly against the omitted components — boot: `vassal_tribute +937,
admin_bonus +50, admiralty −90, blockade −175`; t20: `+487 +50 −90 −175
−2,868`. The dominant missing term on the played board is **`state_charges`
2,868 — the Charges of Empire, nearly three times the army upkeep the sentence
does name** — so the answer to "what's my income" cannot tell the player why he
is losing money, which is the only reason to ask it.

This is also the one place the desk departs from the SC-33 contract the ledger
holds to ("the visible lines still sum to Net").

**Player-reachable:** yes. **Shipped by this row:** yes (CX-2).

**Fix shape:** either drop the derivation and give treasury + Net + a pointer,
or name the top signed component by magnitude ("…and the Charges of Empire
2,868") so the sentence reconciles or says it does not.

---

### DESK-6 (P3) — `_answer_reach` promises a march by a prisoner; `_answer_what_if` musters prisoners

`_answer_own_marshal` has the guard (*"Marshal Ney is a prisoner of X, Sire —
no order can reach him until his release"*) and `counsel._is_free_to_order`
checks `captured_by`, `is_drilling` and `administrative`. Neither
`_answer_reach` nor `_answer_what_if`'s candidate loop (which filters on
`strength > 0` only) checks anything.

**Reproduction** (`p10_edge_answers.py`, boot board, `Ney.captured_by =
"Austria"` — an ordinary NP-4 / W6-7 outcome):

```
> can Ney reach Vienna
Yes, Sire — Ney can reach Vienna from Rhineland in 4 turns: …
```

With every French marshal captured, `what happens if I attack Mack` still
musters Ney leading and Davout/Lannes/Murat joining, while `what can I do`
correctly returns only the two build lines — one slice, two answers, one guard.

**Player-reachable:** yes. **Shipped by this row:** yes.
**Fix shape:** reuse `counsel._is_free_to_order` in both arms.

---

### DESK-7 (P3) — `_answer_winning` drops a belligerent, and disagrees with the banner it points at

Two defects in one arm (`p17_winning.py`).

**(a) A court at war with no marshal on the board is omitted.** The foe list is
built from `world.marshals.values()`, not from `get_nations_at_war_with`.
On the committed `t20` fixture France is at war with **Austria, Britain,
Russia and Switzerland**, and the answer names three:

```
War score, Sire — Austria -26 (losing); Britain -54 (losing); Russia +0 …
   actually at war with : ['Austria', 'Britain', 'Russia', 'Switzerland']
   the desk's own scan  : ['Austria', 'Britain', 'Russia']
```

Control: removing Britain's marshals from a boot board drops Britain from the
answer while she is still at war.

**(b) The desk quotes PAIR scores; the banner it points at shows the WAR
score.** Same board: desk "−26; −54; +0", `build_active_wars` row
`war_score: -78`. The docstring claims *"the canonical helper every other
consumer reads, so the desk cannot disagree with the war banner"*; it does, by
construction, and CA8-D2's ruling (§10.1) is that leverage keys to the WAR.

**Player-reachable:** yes. **Shipped by this row:** yes.
**Fix shape:** iterate `get_nations_at_war_with(player)`; and either quote the
war-level aggregate or say the figures are per-court so the banner's number is
not read as a contradiction.

---

### DESK-8 (P3) — the router's topic table matches substrings, so it points at the wrong screen

`_QUESTION_TOPICS` is scanned with `any(word in lowered for word in words)` —
substring, not word. All driven through `POST /command` (`p13_router.py`,
`p14_router_collisions.py`):

| typed | pointer given | why | what a player wants |
|---|---|---|---|
| `how is the war effort` | the **Economy** tab | `"fort"` ⊂ "ef**fort**" | the war banner |
| `is our war effort sustainable` | the **Economy** tab | same | the war banner |
| `why won't Ney fortify` | the **Economy** tab | `"fort"` ⊂ "**fort**ify" | Generals / Orders |
| `why did the charge fail` | the **Economy** tab | `"charge"`, and the economy row is scanned before `"fail"`→log | the campaign log |
| `why did Murat's charge fail` | the **Economy** tab | same | the campaign log |
| `what are our borders` | the **Orders** tab | `"order"` ⊂ "b**order**s" | the Cabinet |
| `why is there disorder in Swabia` | the **Orders** tab | `"order"` ⊂ "dis**order**" | the region |
| `why did the attack really fail` | the **Cabinet** | `"ally"` ⊂ "re**ally**" | the campaign log |
| `why did the assault finally fail` | the **Cabinet** | `"ally"` ⊂ "fin**ally**" | the campaign log |
| `who are my allies` | **no pointer at all** | "allies" does not contain "ally" | the Diplomatic Ledger |

The last two rows are the crisp statement of it: **`really` routes to
diplomacy and `allies` does not.** The code's own comment says *"a wrong
pointer is worse than none"*, and these are wrong pointers.

**Player-reachable:** yes, all ten. **Shipped by this row:** yes (CX-2).
**Fix shape:** match on word boundaries (`\bfort\b`), add the plurals the
table means (`allies`, `orders`), and move the `"why"`/`"fail"` log row above
the economy row so a failure question is not captured by "charge".

---

### DESK-9 (P3, shown ≠ applied) — the counsel is blind to action points

`_answer_options` prints *"These orders **would be carried out today**, Sire"*
and its docstring says *"What can be ordered, right now, that would not be
refused."* `_is_free_to_order` never looks at AP.

**Reproduction** (`p21_final.py`, boot board with `actions_remaining = 0` —
the exact state in which a player asks this question):

```
> what can I do
These orders would be carried out today, Sire:
  Ney, attack Mack
  Ney, march to Lorraine
  …
> Ney, attack Mack
Not enough actions! Need 1, have 0.
```

**Player-reachable:** yes. **Shipped by this row:** yes.
**Fix shape:** drop the AP-priced lines at 0 AP (the free verbs and the
Cabinet line remain), or soften the sentence to name the cost.

---

### DESK-10 (P3, shown ≠ applied) — the reach answer's turn count double-counts for cavalry

`steps = max(0, len(lawful) - 1)` is the road length in provinces, printed as
"turns". `strategic.py`'s own docstring (lines 11-12) is *"Cavalry
(movement_range=2) moves 2 regions per turn"*.

**Reproduction** (`p08b_cavalry_turns.py`, clear road, no interrupt):

```
> can Murat reach Orleanais
Yes, Sire — Murat can reach Orleanais from Rhineland in 2 turns: …
> Murat, march to Orleanais
Murat begins march to Orleanais. Cavalry charges through Lorraine -> Orleanais.
  ARRIVED after 1 end-turn
```

**Player-reachable:** yes. **Shipped by this row:** yes.
**Fix shape:** `ceil(steps / marshal.movement_range)`.

---

### DESK-11 (P3, R7) — the muster prints the raw camelCase tag, in the row's flagship answer

```
> what happens if I attack ArchdukeJohn
MUSTER — Bernadotte (17,000; …) vs ArchdukeJohn (substantial force) at Tyrol …
```

while the arm's own other branch humanises correctly (*"…within reach of
Archduke Charles at Carniola"*).

**Shipped by this row: NO — pre-existing.** I checked: the real
`Bernadotte, attack ArchdukeJohn` prints the same raw tag
(`p15_neutral_and_tag.py`), so the defect is in the shared
`_format_muster_lines`, and CX-2 inherits it honestly. It is reported here
because CX-2 made it reachable from a question and §3.2 advertises this exact
string as the proof that the desk reads the mechanic's own seam.

**Fix shape:** `humanize_entity_name` at the muster renderer (fixes both
surfaces at once); owner is the combat/R7 seam, not CX.

---

### DESK-12 (P4) — half of the `at_war` kind's own vocabulary is blocked by the client

The CX-2 regex accepts *war* **or** *peace* (`at\s+(?:war|peace)\s+with`).
Measured against `main.gd` (`p18_client_gate.py`):

```
am I at war with Prussia        reaches backend   (not claimed)
are we at peace with Prussia    BLOCKED BY CLIENT (family keyword 'peace with')
```

The player asking the peace form gets the Cabinet redirect, never the answer.
This is the CX-X2 class routed to CR-6, but this instance was authored by CX-2
itself.

**Fix shape:** either add the interrogative leads to the client's advisory
exemption, or drop `peace` from the regex and record why. Owner could
reasonably be CR-6 with the rest of CX-X2.

---

### DESK-13 (P4) — the counsel names one marshal out of eight, with four orders he cannot all take

`military_counsel`'s `seen_verbs` breaks after the first marshal for attack and
move, and the stance loops add one line each — so all four military lines
belong to one man (`p21_final.py`):

```
BOOT : 8 corps on the board, counsel names 1: {'Ney'}
t20  : 7 corps on the board, counsel names 2: {'Ney', 'Massena'}
```

With 4 AP and four Ney lines, the counsel spends the player's whole turn on one
corps and never mentions the other seven. (Related: after `Ney, march to
Lorraine` the counsel proposes `Ney, march to Rhineland` — back the way he
came.)

**Fix shape:** one line per marshal rather than one per verb.

---

### DESK-14 (P4) — `what happened last turn` is not treated as a question at all

It gets Berthier's generic shrug, not the router, so the gazette pointer never
fires for the most natural phrasing (`p14_router_collisions.py`). The `what`
lead carries no `is_question` signal (arm (a) is who/whom/whose/why; arm (c) is
the copular leads), and "happened" is a plain past tense. The gazette row *is*
reachable by other phrasings (`why has nothing happened` → Le Moniteur), so
this is a classification gap, not a dead table row. It also means §3.2's "41 of
41 driven questions answered, 0 walls" does not cover this sentence.

**Fix shape:** CX-1's arm, not CX-2's — a `what`/`when` lead followed by a past
participle with no imperative reading. Owner: CR-6 proper.

---

## ON THE USER'S OWN QUESTION (routing to the LLM), from what this lens saw

§4's ruling is *"the model follows the question desk, not the order chain"* and
CX-D2 asks whether the model may answer a question the desk cannot classify.
Two things this review measured bear on that gate, and both argue for keeping
the model strictly *below* the desk:

1. **The desk's failures are not classification failures.** Every finding above
   is an answer the desk gave confidently and wrongly (a fogged province, a
   capital price, a barred crossing, an ally). A model layered on top would not
   have caught one of them, because the desk never declined.
2. **The cheap win is not escalation, it is the verdict objects the codebase
   already returns.** `plot_route(want_verdict=True)`, `move_refusal_probe`,
   `get_levy_status["closed_reason"]` and the executor's own refusal strings
   each already contain the correct answer to a question the desk currently
   answers from a weaker source. Wiring those is deterministic, free, works in
   the shipped `LLM_MODE=mock` default, and closes five of the findings above.

---

## SUMMARY

| id | severity | what | shipped by CX-2 | player-reachable |
|---|---|---|---|---|
| DESK-1 | P2 | fogged enemy's exact province named by `what_if` (10/14 at boot) | yes | yes |
| DESK-2 | P2 | levy price/arm/amount all wrong; capital price at a named non-capital | yes | yes |
| DESK-3 | P2 | `reach` says yes across a barred Channel crossing | yes | yes |
| DESK-4 | P2 | `what_if` musters an attack on an ALLY / a court at peace | yes | yes |
| DESK-5 | P2 | treasury sentence does not reconcile; sign inverts on a played board | yes | yes |
| DESK-6 | P3 | `reach`/`what_if` ignore captivity | yes | yes |
| DESK-7 | P3 | war-score answer drops a belligerent; disagrees with its own pointer | yes | yes |
| DESK-8 | P3 | router topic table matches substrings → wrong screens | yes | yes |
| DESK-9 | P3 | counsel promises orders at 0 AP | yes | yes |
| DESK-10 | P3 | reach turn count double-counts for cavalry | yes | yes |
| DESK-11 | P3 | raw `ArchdukeJohn` in the muster | **no (pre-existing)** | yes |
| DESK-12 | P4 | `are we at peace with X` blocked by the client | yes | no (blocked) |
| DESK-13 | P4 | counsel names 1 of 8 marshals | yes | yes |
| DESK-14 | P4 | `what happened last turn` gets the shrug, no pointer | no (CX-1 gap) | yes |

**The through-line.** CX-2 built two correct guards in `counsel.py` — the
at-war check and `_is_free_to_order` — and wrote long comments explaining why
each had to exist. The desk arms in the same file, in the same slice, have
neither, plus no fog check and no crossing check. Everything above except
DESK-11 and DESK-14 is one rule applied unevenly across one commit: **the
answer must be asked of the seam that would refuse the order, not of the seam
that describes the map.**
