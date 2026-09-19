# THE QUESTION DESK, DRIVEN

Recon report — read-only. Every claim below is a `file:line` or the output of a
probe committed under `scratchpad/cx_recon/probes/`. Nothing under `backend/`,
`godot-client/`, `tests/`, `docs/` or `tools/` was touched.

**Headline: a question can start a battle.** Ten of thirty-two execution probes
moved the board on pristine HEAD; **five still do** after a sibling agent's
in-flight fix (§0a). `can Ney attack Mack` fights. `retreat?` retreats the entire
army of eight corps, free. `end turn?` advances the turn irreversibly. And 82%
of the twelve questions the user named return a **12,717-character COMMAND
REFERENCE** — which, measured, does not contain the word `status`, `where is`,
`who holds` or `how many men` even once, so the desk that could have answered
them is unreachable from the only surface the game hands a lost player.

---

## ⚠ 0a. THE TREE MOVED UNDER THIS REPORT — read this first

At session start `git status` was **clean**. It is not now:

```
 M backend/ai/clause_guards.py      (+48 −2)
```

A **sibling agent in this same workflow is building a fix while I measured**.
The edit is titled *"CX slice 1 — A QUESTION NEVER ORDERS"*, adds a flip lever
`A_QUESTION_NEVER_ORDERS`, a `_SUBJECT_WH_WORDS = {who, whom, whose, why}` set
that makes those four leads a question on their own, and a `_CONTRACTED_AUX_RE`
for `where's`. It landed at **09:26:46**.

**Provenance of everything in this report.** All headline probes finished
**09:18–09:23**, three-plus minutes before that edit, so §1–§4 measured
**pristine HEAD**. The one exception is `probes/v_out.txt` (09:26:53, seven
seconds after) — it tests `Davot, attack Mack`, `Ny, attack Mack` and
`Masena, move to Piedmont`, none of which carries a WH lead, so the edit cannot
reach them; but the timing is disclosed rather than assumed away.

**I then re-drove every executing row against the current tree**
(`probes/redrive.py`, which hashes `clause_guards.py` before and after and
confirms it did not move mid-measurement — `f576750cb2244306` both ends):

| Row | pristine HEAD | current tree (sibling's fix in place) |
|---|---|---|
| `why not attack Mack` | **battle fought** | ✅ **closed** — `is_question` now True |
| `who holds Swabia` (no `?`) | *"Which marshal shall hold Swabia"* | ✅ **closed** — *"Swabia is held by Bavaria."* |
| `who holds Vienna` (no `?`) | hold-order clarification | ✅ **closed** |
| `where's Ney?` | already worked | ✅ still works (contraction now explicit) |
| `can Ney attack Mack` | battle fought | ❌ **still fights** — 4 corps, 1 AP |
| `may Ney attack Mack` | battle fought | ❌ **still fights** |
| `does Ney attack Mack` | battle fought | ❌ **still fights** |
| `is Ney attacking Mack` | battle fought | ❌ **still fights** |
| `how about Ney attacks Mack` | battle fought | ❌ **still fights** |
| `what about attacking Mack` | battle fought | ❌ **still fights** |
| `retreat?` | general retreat | ❌ **still retreats the army** |
| `end turn?` | turn advanced | ❌ **still ends the turn** |
| `attack?` → `Ney` (two-step) | battle fought | ❌ **still fights** |

Controls held on the current tree: the corpus pins `when ready then retreat` →
retreat and `would you have Ney attack Mack` → attack both still behave, and
`should I attack?` still routes to help.

**⚠ The target kept moving while I measured.** That table was taken at
`clause_guards.py` = `f576750cb2244306`. Minutes later the file was
`6436267c01d67550` — the sibling had added a *deliberative openers* rule
(`what about …`, `how about …`), which closes two more. Final snapshot
(`probes/redrive2_out.txt`, hash stamped identical before and after the run):

| Still EXECUTES at `6436267c01d67550` | |
|---|---|
| `can Ney attack Mack` · `may` · `does` · `is Ney attacking` | battle, 1 AP, 4 corps |
| `retreat?` | general retreat of eight corps, 0 AP |
| `end turn?` | turn 1→2 |
| `attack?` → `Ney` (two-step) | battle, 1 AP |
| `Ney, attack Mack?` | battle (intended — an order with a `?`) |

| Closed since pristine HEAD | |
|---|---|
| `why not attack Mack` · `who holds Swabia` · `who holds Vienna` | WH-subject rule |
| `how about Ney attacks Mack` · `what about attacking Mack` | deliberative-openers rule |

**So 5 of the 10 are closed and 5 survive, and the survivors are exactly the two
families a lead-word rule cannot reach: modal leads with a third-person subject,
and bare verbs with no lead at all.** Controls held throughout — `when ready
then retreat` still retreats, `would you have Ney attack Mack` still attacks,
`should I attack?` still routes to help, and every desk answer in §3 still
answers.

**Do not trust this table as a row list — re-measure.** `probes/redrive.py`
re-runs it in about thirty seconds and stamps the source hash it measured.
Everything in §3 (the wall) and §4 (the refusal) is untouched by the edits and
was re-confirmed by the control rows above.

---

## 0. Method, and how to reproduce

| Probe | What it does |
|---|---|
| `probes/drive_desk.py` | 152 utterances, **one freshly booted 1805 world each**, driven through the real `POST /command` (fastapi `TestClient`) with `M.world` / `M.parser` / `M.game_state["world"]` swapped per the project's TestClient trap. Records parsed action, full player text, and a **world fingerprint diff** (turn, AP, gold, every marshal's location/strength/morale/stance/order, every region controller, diplomatic states, dialogue queue). Output `desk_rows.json`. |
| `probes/drive2.py` | typo asymmetry, nation-vs-region, fallback reachability, punctuation flip, `is_question` isolated. |
| `probes/drive3.py` | the **two-step** (question → clarification → executed order), `_resolve` behaviour, the wall's own content, golden-corpus coverage. |
| `probes/drive4.py` | whether the answer exists in state for each of the twelve; corpus expectations; the "the Emperor" string census. |
| `probes/drive5.py` | the Emperor's honorific, the dropped `question_answered` flag, fog honesty, `_plausible_name_typo` verdicts. |
| `probes/stats.py` | the counts quoted in this report. |

Run: `.venv/Scripts/python.exe <path>/probes/drive_desk.py` from the repo root.
`LLM_MODE=mock` is set in-script and `CommandParser(use_real_llm=False)` is
asserted before every call — **zero live API calls**, by construction.

Board: `europe_1805.json`, France, turn 1, seed `historical`. Own marshals
Ney/Davout (Rhineland), Soult/Napoleon (Lorraine), Lannes/Murat
(Franche-Comte), Bernadotte (Franconia), Massena (Milan). Mack 52,000 at
Swabia at PARTIAL visibility.

---

## 1. The pipeline as it actually is

```
POST /command  (backend/main.py:2659)
  └─ CommandParser.parse
       └─ llm_client fast parser
            ├─ diplomatic routing (mission/proposal keywords)   ← runs FIRST
            └─ if is_question(original_text):            llm_client.py:1601
                 ├─ classify_question(...)               question_desk.py:112
                 │     └─ resolved?  → action "status", carries `question`
                 └─ else            → action "help"   (COMMAND REFERENCE)
  └─ executor → MetaExecutor._execute_status        meta_executor.py:591
       └─ answer_question(world, question)          question_desk.py:330
            └─ None? → "I cannot say, Sire — our maps hold no entry for …"
```

Two independent gates decide whether you get a sentence:

1. **`is_question()`** (`clause_guards.py:579`) — needs an interrogative LEAD
   *plus* one more signal (a `?`, a first-person subject, or for a WH-lead an
   auxiliary). If it returns `False`, the sentence is parsed **as an order**.
2. **`classify_question()`** — five regexes (`where` / `who_holds` / `who_at` /
   `doing` / `how_many`, `question_desk.py:44-79`) and an **exact, non-fuzzy**
   name resolve against three rosters (`_resolve`, `question_desk.py:82`). Miss
   either and it returns `None`, and the caller falls to `help`.

Gate 1 is where the board gets moved. Gate 2 is where the wall comes from.

---

## 2. (a) DOES A QUESTION EVER EXECUTE AN ORDER? — **YES. Ten of them.**

Every row below was measured by state diff on a fresh board, not by reading the
prose. `probes/drive_desk.py`, group `A execution attempts`.

| Utterance | Action | Cost | What actually happened |
|---|---|---|---|
| `can Ney attack Mack` | attack | 1 AP | **Battle fought.** Ney Rhineland→Swabia, 24,000→21,774. Davout and Lannes dragged in. France 800→490g, Austria 700→**−77g**. |
| `may Ney attack Mack` | attack | 1 AP | Battle fought. Ney 24,000→20,168; Murat's trust 75→**72**. |
| `does Ney attack Mack` | attack | 1 AP | Battle fought. Ney→Swabia, 24,000→22,006. |
| `is Ney attacking Mack` | attack | 1 AP | Battle fought. Ney→Swabia, 24,000→21,597. |
| `why not attack Mack` | attack | 1 AP | Battle fought — **led by Soult**, whom the sentence never names. |
| `how about Ney attacks Mack` | attack | 1 AP | Battle fought. |
| `what about attacking Mack` | attack | 1 AP | Battle fought — led by Soult. |
| `Ney, attack Mack?` | attack | 1 AP | Battle fought. (Documented as intended — an order with a `?` stays an order.) |
| `retreat?` | retreat | **0 AP** | **General retreat of all eight corps.** Ney/Davout/Lannes/Murat→Lorraine, Soult/Napoleon→Franche-Comte, Bernadotte Franconia→Munich (−170 men), Massena Milan→Munich (−2,100 men). Free, silent, irreversible. |
| `end turn?` | end_turn | 0 AP | **Turn 1→2** with 4 AP unspent, +42 log events, and two `incoming_proposal` modals stacked. |

### 2.1 The law underneath: **the question mark is load-bearing, and it flips the outcome**

`is_question` requires a `?` (or a first-person subject) for every modal lead
that is not will/would/shall (`clause_guards.py:589-609`). Measured
(`drive2.py` §7):

```
is_question('can Ney attack Mack' )  = False   → ATTACK, battle fought
is_question('can Ney attack Mack?')  = True    → 12,717-char COMMAND REFERENCE
is_question('why not attack Mack' )  = False   → ATTACK, battle fought
is_question('why not attack Mack?')  = True    → 12,717-char COMMAND REFERENCE
```

Eight pairs behave this way. **The same English sentence, one character apart,
either burns an AP and 2,200 men or prints a manual.** A player who does not
type terminal punctuation — which is most players typing into a game — is on
the executing side of that line for every one of them.

The `?`-requirement is documented and deliberate: the comment at
`clause_guards.py:568-571` says the modal leads "DO begin imperative-ish orders
in practice ('can you attack Mack')". That reasoning is sound for *`can you`* —
second person, the person addressed. It does not hold for **`can Ney`**,
**`does Ney`**, **`is Ney`**, **`may Ney`**: a third-person subject after a
modal cannot be an imperative in English. The rule already knows this
distinction — `_SECOND_PERSON_AFTER_LEAD_RE` (`clause_guards.py:562`) is
exactly that test, and it is applied **only** to will/would/shall
(`clause_guards.py:595-605`).

⚠ **I tested that recommendation before publishing it, and it is wrong in
both halves** (`probes/subject_test.py`, which reimplements the proposed
predicate in the probe and runs it over all 447 corpus rows; production was not
edited):

* it closes **4** of the executing rows, not eight — `can` / `may` / `does` /
  `is`. `how about` and `what about` are WH leads, not modal leads, and
  `retreat?` / `end turn?` / `attack?` have no lead at all, so the subject test
  cannot see any of them.
* **it moves three golden-corpus rows**, all PARSE-NEG refusals, because after
  the clause guard blanks the negated clause the lead word is `do`:
  `Ney, do not attack` (`parseneg-do-not-attack-refuses`),
  `Talleyrand, do not propose peace with Austria`, and
  `Ney, do not attak Mack` (`fa80-a-negated-typo-is-still-a-refusal`). All three
  expect `success: false`; routing them to `help` returns `success: true` and
  **reds them**.

The polite second-person imperatives it exists to protect are safe
(`can you attack Mack`, `would you have Ney attack Mack`, `could you scout
Swabia` — all unchanged). So the shape is right and the siting is not: the
subject test would have to run *after* the negation guard has had its say, or
exclude the `do/does/did` leads. **Treat this as a direction, not a patch.**

### 2.2 The two-step: a question that executes on the NEXT line

Worse than the direct hits, because the player believes they are *answering*,
not *ordering*. `probes/drive3.py` §1:

```
> attack?
Which marshal shall lead the attack, Sire?
> Ney
MUSTER — Ney (24,000; 78,676 if all march …) vs Mack …
```
→ **Ney, Davout, Lannes AND Napoleon march on Swabia. Mack 52,000→38,469.
Ney −2,274. 1 AP spent.** The CR-6 bare-attack gate does not stop a question;
it only adds a step, and the step reads like a clarification of a *question*.

```
> who holds Swabia            (no question mark)
Which marshal shall hold Swabia, Sire?
> 1
Ney grumbles about defensive orders but complies. Ney shifts to DEFENSIVE
stance at Rhineland. Effect: -10% attack, +15% defense.
```
→ **1 AP spent and a marshal's stance changed, from a question about who owns a
province.** Reproduces identically for `who holds Vienna`. Answering `Ney`
instead of `1` produces *"Ney firmly objects: 'I would rather attack than sit
idle.'"* — an objection to an order the player never gave.

Cause: without the `?`, `is_question` is False, and the string `who **holds**
Swabia` reaches the `hold` verb.

### 2.3 What does NOT execute (verified, so nobody "fixes" it)

`will/shall/would Ney attack Mack` (with or without `?`) all print the manual —
the will/would/shall arm's subject test is doing its job. `should Ney attack
Mack`, `should Ney retreat`, `should Ney fortify` all reach Berthier's
contingency refusal at 0 AP. `can we retreat`, `what if I attack Mack`,
`why don't we attack Mack`, `shouldn't Ney attack Mack` are all clean.

---

## 3. (b) A SENTENCE, OR A WALL?

**The COMMAND REFERENCE measures 12,717 characters.** (`drive_desk.py`; the
docstring at `question_desk.py:23` says 9,630 — see §7.) For comparison: a desk
answer is 20–95 chars; the full intel report behind bare `status` is 936.

Across all 152 rows: **97 walls, 35 one-sentence answers, 12 Berthier shrugs,
8 battle reports.**

### The twelve, each with four-plus near-miss variants (98 rows)

| # | Question | answered | wall | verdict |
|---|---|---|---|---|
| U1 | where is Ney | **7/10** | 2/10 | works; loses to a typo and to inversion |
| U2 | can Ney reach Vienna | 0/8 | 7/8 | **wall** |
| U3 | who is winning | 0/8 | **8/8** | **wall** |
| U4 | what happens if I attack Mack | 0/8 | **8/8** | **wall** |
| U5 | should I attack | 0/8 | 6/8 | **wall** |
| U6 | why did that fail | 0/8 | **8/8** | **wall** |
| U7 | what can I build here | 0/8 | **8/8** | **wall** |
| U8 | how much is a battalion | 0/8 | **8/8** | **wall** |
| U9 | what does Austria want | 1/8 | 7/8 | wall unless you say "Talleyrand," |
| U10 | am I at war with Prussia | 0/8 | **8/8** | **wall** |
| U11 | how many men does Davout have | **5/8** | 2/8 | works; loses to a typo and the possessive |
| U12 | what's my income | 0/8 | **8/8** | **wall** |

**Two of twelve are answered. Ten are not. Eight of the ten are answered by
nothing at all, in any phrasing.**

### The desk's own five kinds are in good shape — 19/22

Driven with names spelled the way the game prints them (`drive_desk.py`,
group `D`):

```
where is Mack?                → Mack of Austria was reported at Swabia — large force.
where is Archduke Charles?    → We have no word of Archduke Charles's whereabouts, Sire.
where is ArchdukeCharles?     → (identical — the camelCase key works too)
who holds Swabia?             → Swabia is held by Bavaria.
who holds Brunswick?          → Brunswick is held by Hanover.        (region, not the marshal)
who is at Rhineland?          → Rhineland (France): Our own: Ney (24,000), Davout (26,000).
who is at Swabia?             → Swabia (Bavaria): Reported: Mack — large force, this turn.
who is at Vienna?             → No word from Vienna, Sire — it has not been scouted.
what is Davout doing?         → Marshal Davout awaits orders at Rhineland.
how many men does Mack have?  → Mack of Austria was reported at Swabia — large force.
how big is Soult's corps?     → Marshal Soult commands 30,000 men at Lorraine, morale 100.
where is Paris?               → Paris (our own soil) adjoins Berry, Artois, Limousin, Champagne, Normandy.
```

**The NPC-cluster hazard is genuinely closed**: `Archduke Charles` and
`ArchdukeCharles` both resolve, via `name_match_patterns` splitting camelCase
(`question_desk.py:_forms`, verified in `drive3.py` §2). The fog is honest —
Charles (Carniola), Kutuzov (Podolia), Moore (London), Castanos (La Mancha) are
all at `unknown` visibility, so *"we have no word"* is **true**, not a shrug
(`drive5.py` §3). All four synonym verbs work: `who owns/rules/governs/has
Swabia` → identical answer. Casing is free: `WHERE IS NEY`, `where is soult?`
both work.

**That is the shape the other ten questions need, and it already exists.**

---

## 4. (c) DOES THE REFUSAL NAME A SURFACE? — **No. It names 32 commands.**

For every one of the 97 wall rows, the entire player-facing response is
`MetaExecutor._execute_help` (`meta_executor.py:629`) — a static string that
does not vary by what was asked. Measured content of that string
(`drive3.py` §4):

| needle | occurrences in the 12,717-char reply |
|---|---|
| `status` | **0** |
| `where is` | **0** |
| `who holds` | **0** |
| `how many men` | **0** |
| `question` / `ask` | **0** |
| `war score` | **0** |
| `Ledger` / `ledger` | 3 / 4 |
| `F1` | 4 |
| `Talleyrand` | 4 |

It does carry one navigational block, at `meta_executor.py:807`:

```
SCREENS & HOTKEYS:
  F1 diplomacy wizard | T strategic ledger | G marshals
  D diplomatic ledger | L campaign log | R morning dispatch
  E end turn | Tab terminal
```

— which is a **generic index buried ~6,000 characters into a manual**, and is
never joined to the question asked. Ask *"what's my income"* and nothing in the
reply says "press T". Ask *"who is winning"* and nothing says "press D" or
"open the war detail". **There is no case in which the refusal names the surface
that holds the answer.**

And note what the reply does *not* do: it does not even fall back to the 936-char
intelligence report. A question about the board is answered with a list of verbs.

### The three other shrugs, quoted exactly

The desk's own designed fallback (`meta_executor.py:613`) —
*"I cannot say, Sire — our maps hold no entry for …"* — is **structurally
unreachable on the shipped board**. It fires only when `classify_question`
resolves a subject that `answer_question` then cannot answer; every resolvable
subject comes from a roster that both halves read, and `drive2.py` §4 confirms
`[n for n in enemy_roster if n not in world.marshals] == []`. Likewise
`_answer_enemy`'s *"We have no record of {shown}, Sire"* (`question_desk.py:285`)
needs a name in a roster but absent from `world.marshals` — today, only a fallen
marshal, and `world.fallen_marshals == {}` at boot. **Two authored honest
refusals that essentially nobody will ever see.** What players get instead is the
12,717-char manual.

The two shrugs that *are* reachable:
```
Ney's location?   → Berthier frowns at the dispatch. "I see Marshal Ney's name,
                    Sire, but the instruction is unclear. Valid orders include:
                    attack, move, scout, defend, fortify, recruit."
Davout's men?     → Berthier adjusts his spectacles. "Sire, I understand this
                    concerns Marshal Davout, but I cannot determine the order.
                    Perhaps: 'Davout, attack Mack' or 'Davout, move to Paris'?"
```
Both name the right man and then offer to attack with him. Neither names a
surface. Both are shorter and better than the wall.

---

## 5. DEFECT ROWS

Numbered `QD-n`. Each gives an exact utterance that reproduces on the 1805 boot.

### QD-1 (P1) — A question fights a battle. Eight phrasings, no confirmation.
*(§0a: **still open on the current tree** — `why not attack Mack` is closed by the sibling's WH-lead rule; the six modal-lead phrasings are not.)*
`can Ney attack Mack` · `may Ney attack Mack` · `does Ney attack Mack` ·
`is Ney attacking Mack` · `why not attack Mack` · `how about Ney attacks Mack` ·
`what about attacking Mack`
Each spends 1 AP and fights. Measured: Ney 24,000 → 21,774; Austria's treasury
to −77g. No modal, no confirm, `battles_this_turn == 1`.
**Seam:** `clause_guards.py:589-609` — the `?`-or-first-person requirement is
applied to modal leads with a **third-person** subject, which cannot be
imperatives. `_SECOND_PERSON_AFTER_LEAD_RE` (`:562`) already encodes the correct
test and is scoped to will/would/shall only.
**Blast radius:** the golden corpus pins `would you have Ney attack Mack` →
attack (a genuine polite imperative, second person) and `can I attack Mack?` →
help. A subject test preserves both.

### QD-2 (P1) — `retreat?` retreats the whole army, free and silent.
*(§0a: **still open** — a bare verb has no lead, so the WH-lead rule cannot see it.)*
Eight corps relocate; Bernadotte and Massena take attrition (−170, −2,100 men);
0 AP; no confirmation. `is_question('retreat?') == False` — a bare verb has no
interrogative lead, so the trailing `?` is discarded and the general-retreat arm
fires. **The single most destructive thing in this report, and the cheapest to
type.**

### QD-3 (P1) — `end turn?` ends the turn.
*(§0a: **still open** — same reason as QD-2.)*
Turn 1→2 with 4 of 4 AP unspent, +42 log events, two `incoming_proposal` modals
stacked. Irreversible. FA-6 built the guard for `what happens next turn`
(verified working, §7) — the bare-verb-plus-`?` form was never covered.

### QD-4 (P1) — The two-step: a clarification converts a question into an order.
*(§0a: the `who holds Swabia` / `who holds Vienna` half is **closed**; the `attack?` → `Ney` half **still fights**.)*
`attack?` → *"Which marshal shall lead the attack, Sire?"* → `Ney` → four corps
march on Swabia, Mack 52,000→38,469, 1 AP.
`who holds Swabia` → *"Which marshal shall hold Swabia, Sire?"* → `1` → a
marshal's stance changes, 1 AP. Reproduces on `who holds Vienna`.
The player is answering what reads like a question about the map and is issuing
an order. **The gate that is supposed to make bare verbs safe is what makes this
reachable.**

### QD-5 (P2) — Eight of the twelve questions have no answer in any phrasing.
`who is winning` · `what happens if I attack Mack` · `why did that fail` ·
`what can I build here` · `how much is a battalion` · `am I at war with
Prussia` · `what's my income` · `can Ney reach Vienna` — **0 of 8 variants each**,
all 12,717 chars. **And the game knows every one of these answers**
(`drive4.py` §1):
* who is winning → `war_status.build_active_wars` returns `war_score` per war.
* am I at war with Prussia → `world.get_diplomatic_state("France","Prussia")` = `PEACE`. One lookup.
* what's my income → `ledger.build_strategic_ledger(w)["economy"]` has `treasury: 800, income: 3400, trade_income: 350, blockade: 175, admiralty: 90, vassal_tribute: 937` … 24 keys. The typed verb `economy` already prints a 1,572-char treasury report.
* what can I build here → `economy_executor` knows `depot, fort, market, stable, supply_depot, training_ground, watchtower`.
* how much is a battalion → `EconomyExecutor._calculate_recruit_cost` exists.
* can Ney reach Vienna → `strategic.plot_route(world, marshal, destination, …, want_verdict=True)` returns a verdict; `MovementExecutor.move_refusal_probe` is a pure pre-flight built for exactly this.
* what happens if I attack Mack → `CombatExecutor._build_muster_preview` / `_bad_odds_muster_note` produce *"the balance of force looks favorable"* — **the game already writes the answer, and only prints it once the attack is committed.**

### QD-6 (P2) — A typo is a named near-miss on the order road and a 12,717-char manual on the question road.
```
Ny, attack Mack        → "I do not find 'Ny' in the order of battle, Sire. Did you mean Ney?"   (66 chars)
where is Ny?           → COMMAND REFERENCE                                                      (12,717 chars)

Davot, attack Mack     → typo silently corrected; FOUR CORPS MARCH, battle fought, 1 AP
how many men does Davot have?  → COMMAND REFERENCE
```
The second pair is the sharp one, and it was verified separately
(`probes/v_out.txt`): `Davot, attack Mack` moves Ney, Davout, Lannes and
Napoleon and records a battle; `Masena, move to Piedmont` marches Massena and
costs him 2,520 men to the road. **The order road will accept a typo and act on
it irreversibly. The question road will not accept the same typo to tell you
where the man is standing.**
Also `where is Masena?`, `where is Nay?`, `what is Davout's strength?`.
`_resolve` (`question_desk.py:82`) does exact-form and whole-word containment
only — **no fuzzy arm at all**, while `parser._plausible_name_typo:635` and
`executor._correction_survives:225` exist and are measured to accept
`Davot→Davout`, `Masena→Massena`, `Viena→Vienna`, `Prusia→Prussia`.
The same asymmetry hits an unknown name: `Wellington, attack` → *"There is no
'Wellington' in the order of battle, Sire. Whom did you intend?"* (75 chars);
`where is Wellington?` → 12,717 chars. (Wellesley is on the `marshal_pool`
bench, so this is a name the game itself shows the player.)

### QD-7 (P2) — `shoud I attack?` is read as a marshal's name.
> `I do not find 'shoud' in the order of battle, Sire. Did you mean Soult?`

A typo in the *interrogative lead word* drops `is_question` entirely, and the
sentence falls to the marshal fuzzy scan. This is the exact defect named in the
PARSE-NEG record (`llm_client.py:1586-1588`: *"the marshal fuzzy scan turned
'should I attack?' into 'Did you mean Soult?'"*) — fixed for the correctly
spelled form, alive for the misspelled one. No side effect, but it is the
single least helpful possible reply to a lost player.

### QD-8 (P2) — The desk demotes the Emperor.
```
where is Napoleon?  → "Marshal Napoleon stands at Lorraine with 10,000 men (morale 85)."
```
`display_names.marshal_honorific` (`display_names.py:1358`) exists as the single
source for exactly this — `marshal_honorific(w, "Napoleon")` returns **"the
Emperor Napoleon"** — and its docstring records the row-NP live-drive finding
that a template calling him "Marshal Napoleon" *"demotes the one man the whole
court orbits."* `question_desk.py` does not import it (measured: `False`) and
hardcodes `Marshal {name}` at 12 sites. `Napoleon.is_sovereign is True`.

### QD-9 (P2) — The game's own printed noun is not typable: `the Emperor`.
```
where is the Emperor?  → COMMAND REFERENCE (12,717)
where is the emperor   → COMMAND REFERENCE
where is Emperor?      → COMMAND REFERENCE
where is Bonaparte?    → COMMAND REFERENCE
where is Napoleon Bonaparte?  → works
```
There are **80 `the Emperor` string literals in `backend/`** — including
`combat_executor.py:1722` *"The Emperor commands in person — +10% harder"*,
which appears in the very muster text this probe captured. The game says it,
80 times, and cannot hear it. (This is the IQ-10 H-class defect —
"`gather intelligence on Austria` shrugged while `gather intel on` worked" — one
row over.) Same family: `where is Blucher?`, `where is Archduke Ferdinand?`.

### QD-10 (P2) — A nation is a legitimate subject of "who holds", and walls.
```
who controls Bavaria?  → COMMAND REFERENCE
who holds Bavaria?     → COMMAND REFERENCE
who holds Austria?     → COMMAND REFERENCE
```
Bavaria is a nation, not a region (`'Bavaria' a region? False | a nation?
True`) — and the desk's *own answer to another question* is **"Swabia is held by
Bavaria."** The game teaches the name and then cannot take it back. The honest
answer ("Bavaria is a court, not a province — it holds Swabia, Munich, …") is
one `get_nation_regions` call away.

### QD-11 (P3) — "What does Austria want" is answered by a system that never speaks.
`Talleyrand, what does Austria want?` gives 285 chars of war score, strength and
Metternich's skill — and **never names the agenda**. Measured
(`drive4.py` §1): `get_active_agenda("Austria", w)` returns
`AgendaView(id='redeem_italy', title='Redeem Italy', blurb='The priority theater
of 1805 — Charles holds the main army in Italy; the losses of Campo Formio and
Luneville must be undone.', regions=('Milan','Piedmont','Savoy'))`. That blurb
*is* the answer to the question, it is authored, and the advisory does not read
it. Without the honorific it is a wall; and `Talleyrand, what does Austria want`
(no `?`) gives a third answer, *"Sire, I await your instructions regarding
Austria."*

### QD-12 (P3) — `question_answered` is produced and delivered to no one.
`_execute_status` returns `{"question_answered": True}` (`meta_executor.py:619`).
Measured on the wire: `question_answered` is **absent from all 34 response
keys**, and `main.py` mentions the string **zero times**. The client cannot tell
a one-line desk answer from a 936-char intel report, so it cannot render them
differently. Dead field.

### QD-13 (P3) — Two authored refusals are unreachable.
`meta_executor.py:613` *"I cannot say, Sire — our maps hold no entry for …"* and
`question_desk.py:285` *"We have no record of {shown}, Sire."* Both require a
name that resolves in a roster but fails downstream; measured, no such name
exists on the boot board. Harmless in itself — but it means the wall is the real
fallback, and that is what the design intended these lines to prevent.

### QD-14 (P3) — Inversion and possession are unsupported shapes.
`is Ney at Paris?` (a yes/no positional question — the most natural way to check
one fact) → 12,717 chars. `Ney's location?` and `Davout's men?` → Berthier
shrugs. `what is the Grande Armee doing?` → wall. `what turn is it?`,
`what year is it?`, `what is the date?`, `how many turns left?` → wall, though
`build_strategic_ledger` returns `calendar_label` and HC-0 exists to produce it.

---

## 6. What the desk gets RIGHT (verified — do not regress these)

* **Fog is honest.** `where is Moore?` / `Kutuzov` / `Castanos` / `Archduke
  Charles` → *"We have no word …"* and all four are at `unknown` visibility
  (`drive5.py` §3). `who is at Vienna?` → *"No word from Vienna, Sire — it has
  not been scouted."* PARTIAL gives a band (*"large force"*), FULL gives the
  number (*"Deroy of Bavaria is at Franconia — 22,000 men, confirmed"*).
* **camelCase keys and printed names both resolve** (`Archduke Charles` ==
  `ArchdukeCharles`), which is the NPC-cluster hazard closed at the root.
* **Region-first resolution works**: `who holds Brunswick?` answers about the
  province, not the Prussian marshal. The review-round fix holds.
* **Casing and the honorific address are free**: `WHERE IS NEY`,
  `Berthier, where is Ney?`, `where is Marshal Ney` all answer.
* **The answers are the right length** — 20 to 95 characters.

---

## 7. Corrections to the record (measured)

1. **`question_desk.py:23` says the COMMAND REFERENCE is 9,630 characters. It is
   12,717.** Measured on every one of 97 wall rows. The docstring's figure is
   from Sept 4, 2026; the help text has grown ~32% since.
2. **`tests/data/parser_golden_corpus.json` has 447 entries**, and only **16**
   are question-shaped. None of the eight QD-1 phrasings is among them: the
   corpus pins `will Ney attack Mack?`, `would Ney attack Mack`,
   `shall we attack Mack` — precisely the three modal leads that already have
   the subject test — and does **not** pin `can/may/does/is Ney attack(ing)
   Mack`. The corpus covers the arm that works.
3. **FA-6 is intact.** `what happens next turn` → *"Berthier holds the dispatch
   unsealed. 'For a later day, Sire — but I keep no…'"*, turn stays 1. But
   `what happens next turn?` (with `?`) → 12,717-char wall, and `end turn?` →
   turn advances. The guard is verb-specific, not shape-specific.
4. The desk's own five kinds mostly survive a dropped `?` — `where is Mack`,
   `who is at Swabia`, `what is Davout doing`, `how many men does Ney have` all
   answer without punctuation. The exception is the `who_holds` family, which
   collides with the `hold` verb (QD-4).

---

## 8. UNVERIFIED

* **Live-parser behaviour.** Everything here is `LLM_MODE=mock`. Under
  `LLM_MODE=anthropic` the fast parser escalates only below confidence 0.7; the
  QD-1 rows parse at high confidence and so would not escalate — but this was
  **not measured** (no live call was made, by rule). The IQ-9 cassettes
  (`tests/data/parser_cassettes/`) were not replayed.
* **The Godot client's rendering.** Whether a 12,717-char reply scrolls, clips
  or is clamped in the terminal was not observed. IQ-10's `>3000`-char findings
  suggest it is worth a frame.
* **Later-turn boards.** All 152 rows are turn 1. A question asked with a
  standing order, a captured marshal, or a fallen marshal on the board (which is
  what makes QD-13's refusals reachable) was not driven.
* **The region-panel click road.** `region_panel.gd` emits typed commands, so it
  converges on the same parser — but no chip emits a question, so it is
  presumed unaffected. Not checked.
* **QD-1's proposed fix was not built or tested**, only reasoned from
  `_SECOND_PERSON_AFTER_LEAD_RE`'s existing use. The claim that it preserves
  every corpus expectation is an inference from the 16 rows listed in §7.2, not
  a test run.
