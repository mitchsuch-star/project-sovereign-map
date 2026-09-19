# VERDICT: CX5-L5-F7 — **NARROWED**

**Row:** `guard` / `protect` eat the screening idiom before it is asked
**Filed by:** lens "retreat", P4, `player_reachable: true`, `shipped_by_this_row: false`
**Verdict:** **NARROWED.** It reproduces exactly, it is pre-existing as filed, and
P4 is right for the half it is actually about — but **the mechanism in its title
is wrong for both of its own examples**, the 2-AP half belongs to a wider defect
the codebase has already recorded, and the obvious fix ships a regression that
**no pin and no corpus row can see**.

Tree: `master f52df77f` (one docs-only commit above `727cf88a`; `git show --stat`
confirms it touches no file under `backend/` or `godot-client/scripts/`, so the
code is the row's code). Repo clean before and after; nothing under the repo was
modified. All measurements at `POST /command` through `TestClient` on a **fresh
shipped-1805 board per utterance**, `LLM_MODE=mock`, no key, zero live calls.
Probes: `probes/rf7/{h,p1_repro,p2_prerow,p3_battery,p4_apply_fix,p5_fix_effect,p6_minimal_pairs,p7_seeds}.py`.

---

## 1. Does it reproduce AT ALL, exactly as stated? — **YES, verbatim.**

My own run, not the one I was given:

```
U : Lannes, guard the retreat
AP: (4, 4)  admin: (2, 2)  gold: (800, 800)  success: False
CHANGED: []
MSG: Region 'Retreat' not found. Did you mean 'Crete'?
PRED: screening=False  retreat_is_noun=True

U : Lannes, cover the withdrawal of the guard
AP: (4, 2)  admin: (2, 2)  gold: (800, 800)  success: True
CHANGED: ['Lannes']
   Lannes ('Franche-Comte', 18000, …, strategic_order=False)
        -> ('Franche-Comte', 18000, …, strategic_order=True)
MSG: Lannes will hold Franche-Comte. Holding position. (Our maps read
     Franche-Comte as the province nearest your order, Sire.) Lannes:
     "Standing guard while others win laurels. As you command."
     (2 AP — a standing strategic order to hold this ground turn after turn.
     For a single-turn tactical hold, order 'defend' at 1 AP.)
```

Both figures the row quotes (AP 4→4 inert; AP 4→2) are exact, and the structural
claim holds: the HOLD family's keyword list (`…, "anchor at", "guard", "protect"`,
`llm_client.py:2083-2091`) sits **above** the retreat branch (`:2098`), so neither
`_mentions_screening_idiom` nor `_retreat_is_a_noun` is consulted.

**Robust, not a one-seed artefact.** Six seeds (`historical`, `1`, `7`, `31`,
`99`, `austerlitz`), same result on every one: case 1 inert, case 2 `HOLD/2AP`.

---

## 2. Did row CX introduce it? — **NO. PRE-EXISTING, measured, not read off a diff.**

I extracted the whole pre-row tree read-only (`git archive b4a27a15^ backend tests
tools godot-client/…/assets`) and drove the identical utterances against it
(`p2_prerow.py`, with `_retreat_is_a_noun` confirmed absent from that module):

```
PREROW  Lannes, guard the retreat
        AP (4,4) changed []  MSG: Region 'Retreat' not found. Did you mean 'Crete'?
PREROW  Lannes, cover the withdrawal of the guard
        AP (4,2) changed ['Lannes']  MSG: Lannes will hold Franche-Comte. …(2 AP…)
```

**Byte-identical to HEAD on both.** The HOLD keyword list and its position
relative to the retreat branch are unchanged between `b4a27a15^` and HEAD.
`shipped_by_this_row: false` is correct.

---

## 3. Is the stated MECHANISM right? — **NO, and it is wrong for BOTH examples.**

The title says *the hold family's bare `guard`/`protect` **keywords** eat the
screening idiom*. The minimal pairs (`p6_minimal_pairs.py`) say otherwise.

### 3a. Example 1 has no screening idiom to eat.

`_mentions_screening_idiom`'s verb alternation is `\b(?:cover|screen|protect|shield)`
— **`guard` is not in it.** Measured:

```
_mentions_screening_idiom('lannes, guard the retreat')  = False
_retreat_is_a_noun('lannes, guard the retreat')         = True
```

So the guard that would have answered example 1 correctly is **CX-5's own
`_retreat_is_a_noun`**, not the screening idiom. The true statement is *"the HOLD
family outranks `_retreat_is_a_noun`"* — which is a different claim with a
different fix, and it is the one that matters, because a fix aimed at the
screening idiom (§3c, arm A) **leaves example 1 exactly as it is**.

(The row's own title would have been true of `Lannes, protect the retreat`, where
`screening=True` and HOLD eats it anyway. I measured it: same outcome as example
1 — inert, `Region 'Retreat' not found. Did you mean 'Crete'?`.)

### 3b. Example 2's claimant is the NOUN *the Guard*, not a hold verb.

Delete the word `guard` from the row's own second example and change nothing
else:

```
Lannes, cover the withdrawal                  AP (4,4) chg=[]  scr=True noun=True
   -> Berthier frowns at the dispatch. "…the instruction is unclear…"   [INERT]
Lannes, cover the withdrawal of the guard     AP (4,2) chg=['Lannes'] scr=True noun=True
   -> Lannes will hold Franche-Comte … (2 AP …)
```

**The screening idiom is not eaten by a hold verb. It is eaten by the Imperial
Guard appearing as a noun.** Same pair with the natural phrasing:
`Lannes, cover the retreat` → inert shrug; `Lannes, cover the retreat of the
Guard` → 2 AP HOLD.

### 3c. The 2-AP half has nothing to do with retreat, screening, or CX-5 — and is
already on the record.

Remove every retreat word and the 2-AP HOLD survives:

```
Ney, move to Paris          AP (4,2)  -> marches, route Lorraine→…→Paris
Ney, move to Paris with the Guard   AP (4,2) -> "Ney will hold Rhineland." [march cancelled]

Ney, scout Swabia           AP (4,3)  -> scouts, reports Mack ~52,000
Ney, scout Swabia with the guard    AP (4,2) -> "Ney will hold Rhineland."

Ney, fortify                AP (4,4)  -> objection
Ney, fortify with the guard         AP (4,2) -> "Ney will hold Rhineland."

Ney, recruit 5000 men for the guard AP (4,2) -> "Ney will hold Rhineland."
```

So the real rule is: **any sentence containing the substring `guard` that reaches
the HOLD branch becomes a 2-AP standing HOLD at the nearest province** — and
outside the screening family it is worse than F7's case, because a march to Paris
is silently converted into standing still.

The project already knows this class. `backend/commands/combat_executor.py:9905`
carries FA-22's note verbatim: *"Measured: `the Guard, attack Mack` — where the
hold keyword inside 'Guard' claims the sentence and leaves the attack with no
target."* And the phrase is the **game's own**: `europe_1805.json` prints the
Emperor as *"on the Rhine **with the Guard** — 10,000 men carved from Soult's own
IV Corps"*, and three authored agendas are titled *"Guard the Straits"*, *"Guard
the Peninsula"*, *"Guard the Vistula"*.

---

## 4. Is the SEVERITY right? — **P4 is right for the half the row is about; the
other half is mis-homed rather than under-rated.**

* The retreat half (`guard the retreat`, `protect the retreat`, `guard our
  retreat`, `guard the withdrawal`, `protect the withdrawal`, `protect the
  flank`, `protect the corps`) is **0 AP, nothing moves, on every seed** — a silly
  suggestion (`'Retreat'` → `Crete`, `'Flank'` → `Finland`, `'Corps'` → `Corsica`)
  and no state change. **P4, as filed.**
* The 2-AP half is worth more than P4 — 2 of 4 action points on an unrequested
  standing order, and `cancel` costs another — but it is the `Guard`-noun family
  of §3c, not this row. Filing it under "the screening idiom" understates it
  (it is not limited to screening) and mis-directs the fix.

---

## 5. Is it reachable by a PLAYER through the shipped client? — **YES, confirmed.**

* `main.gd` holds no `guard` / `protect` / `cover` / `screen` / `shield` /
  `withdraw` term in `DIPLO_FAMILY_KEYWORDS`, `DIPLO_NO_HOME_KEYWORDS`,
  `DIPLO_WAR_ROOM_KEYWORDS`, `DIPLO_NATION_ANYWHERE_KEYWORDS` or
  `DIPLO_ADDRESS_NAMES`, so `_matches_cabinet_family` is False and **nothing is
  redirected to the Cabinet**. (`protectorate` appears only in a comment, not in a
  keyword list.)
* The CX-3 predictor table `_MARSHAL_VERBS` offers `hold` / `retreat` / `support`
  and **never** `guard` / `cover` / `protect`, so the **CX-3 census is not
  violated** — the game does not offer a sentence it cannot read here. The player
  types it unprompted (helped along by the Emperor's own biography and the
  agenda titles above).

---

## 6. Would a fix ship a regression? — **YES, and no pin would catch it.**

F7 files **no fix** (unlike F1–F5 it has no `**Fix**:` line), so I built and
measured the two obvious ones on a scratch HEAD tree (`p4_apply_fix.py`,
`p5_fix_effect.py`; the repo itself untouched):

**Arm A — ask `_mentions_screening_idiom` before the HOLD family** (the fix the
title implies).
* Fixes example 2 (2-AP HOLD → shrug) ✔
* **Does not fix example 1** — `guard` is not a screening verb (§3a) ✘
* **Creates an asymmetry it did not have**: `Ney, protect the rear` becomes a
  shrug while `Ney, guard the rear` keeps **marching Ney to Lorraine for 2 AP**.
  Two spellings of one order, two answers — the exact shape F4 condemns
  elsewhere in the same report.
* Also loses an honest named refusal: `Ney, guard the bridge and cover our
  retreat` goes from *"Region 'Bridge' not found. Did you mean 'Bergen'?"* to a
  bare shrug.

**Arm B — `_mentions_screening_idiom` OR `_retreat_is_a_noun` before the HOLD
family** (F1's "hoist both guards", generalised to cover example 1).
* Fixes both F7 examples ✔
* **Ships a regression on an ordinary sentence**, because `_RETREAT_NOUN_RE`
  matches the bare participle `\bretreating\b` **unconditionally**:

```
Ney, protect Rhineland, the enemy is retreating
   BASE  AP (4,2)  Ney: "Ney will hold Rhineland. Holding position."   ← CORRECT
   ARM B AP (4,4)  "Sire, Marshal Ney awaits your command, but I cannot parse
                    this order. Might you mean 'Ney, scout' or 'Ney, defend'?"
```

  That is the pinned FA-D20 contract — corpus row
  `fa-d20-protect-rhineland-stays-hold`, *"a province keeps HOLD"* — **with one
  trailing battlefield observation added**. Also:

```
Davout, protect Bavaria, their retreat is disorderly
   BASE  "Bavaria is a nation, not a province. Name a province, Sire —
          theirs are Franconia, Munich, Swabia."           ← an honest refusal
   ARM B a bare shrug
Ney, guard Paris while the Austrians are retreating
   BASE  AP (4,4) objection staged   ->   ARM B AP (4,2) HOLD at Paris
```

**And the answer to "name the pin it would red" is: NONE.** Measured under arm B
on the scratch tree:

```
Parser eval: 688/688 passed (mock mode)
504 passed  (test_cx1, test_cx3, test_fa_slice7, test_fa_slice14,
             test_playtest_command_and_ui_2026_07_18, test_strategic_parser)
```

Identical under arm A and under pristine. **The regression arm B ships is
invisible to every standing instrument**, because `fa-d20-protect-rhineland-stays-hold`
carries only the bare sentence. That is this row's own recorded lesson, one layer
out: *the reviewers' first move is to add the ONE clause the builder held
constant.* Any fix here needs its pin written on the sentence **with** the
trailing clause, before the fix lands.

---

## 7. What the row should say instead

> **PRE-EXISTING (FA-22's class), P4 for the retreat half.** The HOLD family's
> keyword list outranks BOTH retreat guards, so `guard/protect the retreat` is
> answered with a nonsense province suggestion at 0 AP. Separately and more
> widely, the bare substring `guard` claims any sentence reaching the HOLD
> branch — including the noun *the Guard*, which the game itself prints — so
> `move to Paris with the Guard` buys a 2-AP HOLD instead of a march. The two are
> different defects with different fixes; neither is CX-5's.
>
> A fix must (a) reach `guard` as well as the four screening verbs, or it leaves
> the row's own first example standing and splits `guard the rear` from `protect
> the rear`; and (b) **not** hoist `_retreat_is_a_noun` unguarded, or
> `protect Rhineland, the enemy is retreating` — the FA-D20 pin plus one clause —
> becomes a shrug, silently, with the corpus at 688/688.
