# Compound & Conditional Commands — the CR-7 build plan

> **Status: INVESTIGATION + RECOMMENDATION. Nothing here is built, gated or
> approved.** Produced September 20, 2026 by a 53-agent read-only fleet
> (18 recon -> 18 adversarial refuters -> 7 competing plans -> 6 judges ->
> 4 syntheses), driving the real `POST /command` and the real
> `CommandParser.parse` against an unmodified `europe_1805.json` boot world at
> HEAD `15c498cb`, `LLM_MODE=mock`, seed `historical`. No repo file was modified
> during the investigation.
>
> **User ask: "lay out plan for multi step or conditional commands."**
>
> Every claim below carries a confidence marker. **measured** = the agent ran it
> and is reporting output. **read** = the code path was read end to end.
> **inferred** = judgement. Claims that could not be reproduced are recorded as
> such rather than deleted. Line numbers were current at measurement time; this
> repo's own records say ~80% of filed line numbers go stale, so **navigate by
> symbol**.

---

## Verdict in one paragraph

Multi-step and conditional commands are not a missing feature — they are one live P1 (40 of 40 compound shapes discard the player's first clause and fight a battle nobody ordered) plus a built, paid-for conditional substrate the parser throws the sentence away before reaching. Build it as CR-7 "The Second Clause": 8 slices, 5.0 sessions, four honest stopping points, and the cross-turn order queue retired by written contract rather than deferred — because I measured its one hook firing once in fourteen turns and its lapse hook firing never.


## Key numbers (all measured unless noted)

- 40 of 40 non-movement compound shapes SWALLOWED (action=attack, dropped_sequel=None, warning=None) — measured at CommandParser.parse on the 1805 board
- `Ney, fortify, then attack Mack` at POST /command: 1 AP, Rhineland->Swabia, 24,000->22,050 men, fortified still False, no warning
- _complete_order fired 1 time in 14 driven turns across 3 standing marches; _break_order fired 0 times while 2 of 3 orders died
- Davout's MOVE_TO Bordelais stood 11 turns without moving one province, then vanished without going through _break_order
- 4 of 15 natural condition phrasings produce the condition asked for; 2 mint phantom provinces, 2 mint unmeetable marshals, 4 drop silently at 2 AP
- 42 `strategic_order = None` sites across 11 files
- 0 of 449 corpus rows assert strategic_condition, dropped_sequel or attack_on_arrival; ALLOWED_EXPECTED_KEYS is 11 keys and evaluate_entry silently ignores unknown ones
- dropped_sequel: 8 occurrences, all in parser.py, all producers, zero consumers in backend/ or godot-client/
- _check_condition: exactly ONE call site (strategic.py:2126); 6 StrategicCondition fields, 5 typed-reachable
- Conditional/compound sentences parse at 0.90-0.95 against LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7 — no model, local or cloud, is ever consulted


## Open questions that need your ruling

- CR-7-6 (the arrival order carrying its object) is pre-gated on a reachability probe I did NOT run: I measured _complete_order reachable, but not attack_on_arrival firing, and two prior agents drove ~8 marches and saw zero. Run that probe FIRST — it decides whether the deferred-arrival case exists at all, and therefore how much of 'multi-step' this row can honestly deliver.
- CR-7-2's relay answers the same-turn case completely and the multi-turn case not at all: handing `fortify` back for `Soult, march to Bordelais, then fortify` fortifies him at the ORIGIN. Do you want the relay to refuse a tail behind a multi-turn strategic head rather than offer a keypress that produces the wrong order?
- CR-7-5 flips 0-3 of the 7 pinned corpus refusals and consciously flips FA-50's `test_the_address_form_is_not_split`. Both are pins landed by named past slices — confirm you want them flipped with measurement on the record rather than worked around.
- `move to Swabia` produces NO strategic order while `march to Swabia` does, and the completer offers both (main.gd:6970-6971). Unifying them is a one-line behaviour change outside this row's stated scope — fold it into CR-7-1 or file it separately?


---

# Multi-step and conditional commands — the build plan

**Row CR-7 "The Second Clause".** Everything below is measured on the shipped 1805 board this session unless marked *read*. Navigate by symbol; the line numbers here were current at measurement time and this repo's own records say ~80% of filed line numbers go stale.

---

## 1. Where it stands today

### A two-clause order executes the *wrong* clause, and says nothing

This is the headline and it is worse than "the tail is dropped". The tail does not get dropped — **it replaces the head, spends the AP, marches the corps and fights.**

Measured at `POST /command`, fresh 1805 world:

```
>>> Ney, fortify, then attack Mack
    success=True   ap 4->3   loc Rhineland->Swabia   str 24,000->22,050
    fortified False->False   battle_report=YES   warning=None
    'One order at a time' in message: False
```

Ney was told to fortify. He marched into Swabia, fought Mack, lost **1,950 men**, and is not fortified. Nothing in the reply mentions the word "fortify".

I drove 16 first clauses × 4 tail forms (` then attack Mack`, `, then attack Mack`, ` and then attack Mack`, `; attack Mack`) through `CommandParser.parse(text, gs, world=world)`:

| First clause | Verdict | Count |
|---|---|---|
| `fortify`, `scout <R>`, `drill your men`, `defend`, `retreat`, `unfortify`, `form square`, `garrison <R>`, `bombard <E>`, `recruit infantry` | **SWALLOWED** — `action=attack`, `strategic_type=None`, `dropped_sequel=None`, `warning=None` | **40 / 40** |
| `wait`, `hold your position`, `stay here` | split + told | 12 / 12 |
| `march to <R>`, `advance to <R>` | fused (`MOVE_TO`, `attack_on_arrival=True`) — the intended idiom | 4 / 8 |
| `march to <R> and then attack` | fused onto the phantom target **`Swabia And`** (`in world.regions` → False) | 2 |
| `march to <R>; attack <E>` | fused with **`attack_on_arrival=False`** — the attack silently gone | 2 |
| `move to <R>` (any tail) | swallowed; `move to` gets **no strategic upgrade at all**, even bare | 4 |

The seam is one predicate in `parser.py:_split_sequential_orders` (:136):

```python
if _ATTACK_ON_ARRIVAL_TAIL_RE.match(tail) and not (
        _STAND_FAST_FIRST_CLAUSE_RE.search(first)
        and not _ENGINE_CONDITION_RE.search(first)):
    return None
```

`_ATTACK_ON_ARRIVAL_TAIL_RE` (:72) declines the split for any tail starting `attack|engage|assault`. `_STAND_FAST_FIRST_CLAUSE_RE` (:88) re-permits it only for `STAND_STILL_ALTERNATION` (`llm_client.py:186` — `wait|hold|halt|stand fast|stand ground|stay put|stay here|stay where you are|remain|rest your men`). That list is FA-7's fix: it enumerates the verbs that were *reported*, not the question "does clause 1 carry an order". Every verb outside the list is still eaten — which is exactly the shape of the four consecutive slices this repo has recorded fixing at this regex.

### When the split *does* fire, the player is told — on one arm only

`parser.py:2056-2062` composes the note; `main.py:3584` surfaces it:

> *Berthier: "One order at a time, Sire — I have relayed the first. "attack Mack" must follow as its own command."*

Gated on `if result.get("success")`. Measured:

```
>>> Ney, march to Karaman, then Davout, fortify
    success=False  ap 4->4  message: "Cannot enter Karaman, Sire — it is
    controlled by Ottoman (diplomatic state: PEACE)..."
    'One order at a time': absent      Davout.fortified = False
```

A refused head loses its tail in total silence. And `dropped_sequel` is a **census of 8 occurrences, all in `parser.py`, all producers** — zero consumers in `backend/` or `godot-client/`. The value is computed to build one string and thrown away.

### The conditional substrate is built, paid for, and unreachable from most English

`StrategicCondition` (`marshal.py:39`) has six fields, all serialized. `_check_condition` has **exactly one** call site (`strategic.py:2126`) and one def (`:3846`). Five of six are typed-reachable. Nothing here is dead code.

What is broken is what a player can *say*. Fifteen phrasings, driven at `POST /command` on **Davout** (cautious — an aggressive marshal pre-objects to a HOLD and the defect looks fixed; that confound will cost you an afternoon if you sample Ney):

| Utterance | Outcome | AP |
|---|---|---|
| `hold Lorraine until Ney arrives` | ✅ `{until_marshal_arrives: 'Ney'}` | 2 |
| `hold Lorraine until relieved` | ✅ `{until_relieved: True}` | 2 |
| `hold Lorraine for 3 turns` | ✅ `{max_turns: 3}` | 2 |
| `hold Lorraine until victory` | ✅ `{until_battle_won: True}` | 2 |
| `hold Lorraine until **Marshal** Ney arrives` | condition **silently dropped**, unconditional standing order | 2 |
| `hold Lorraine **till** Ney arrives` | target = **`Lorraine Till Ney Arrives`** (not a region) | 2 |
| `hold Lorraine for **three** turns` | target = **`Lorraine For Three Turns`** (not a region) | 2 |
| `hold Lorraine until **relief** arrives` | `{until_marshal_arrives: 'Relief'}` — **unmeetable forever** | 2 |
| `hold Lorraine until **Godot** arrives` | accepted; Godot is not on the board — **unmeetable forever** | 2 |
| `hold Lorraine for **0** turns` | accepted, `max_turns=0`, self-completes next tick | 2 |
| `hold Lorraine until turn 5` | silently dropped | 2 |
| `hold Lorraine **unless** attacked` | silently unconditional | 2 |
| `hold Lorraine **while** Ney marches` | silently unconditional | 2 |
| `**until Ney arrives,** hold Lorraine` | refused entirely — *"I cannot determine…"* | 0 |

**4 of 15.** Two phantom provinces, two unmeetable orders, four silent drops — every one of them charged.

Root cause is a two-regex split that must move together:

- `strategic_parser._strip_conditions` (:579) decides what is **removed** from the target text: `until\s+.*$` (no `till`), `for\s+\d+\s+turns?` (digits only).
- `strategic_parser._parse_condition` (:804) decides what is **read**: same vocabulary mismatch.

A prior flip experiment (in the recon, *read*) widened `_parse_condition` alone and the phantom stood on 5 of 6 — worse, because the Ledger then renders "3 turn(s) remaining" for an order already doomed.

### The refusal blames the wrong party, and advertises the fix it won't accept

`main.py:3455-3463` — **one hardcoded string for every refusing marker**:

> *Berthier sets down his pen. "Sire, that is a contingency, not an order — I have no way to hold a dispatch **until the enemy moves**. Nothing has been relayed. … a standing order I can hold is **'hold until Davout arrives'**."*

Measured: `hold Rhineland when Davout arrives`, `…if…`, `…once…`, `…as soon as…` all return this. The sentence is about a *friendly marshal arriving*; the refusal blames the enemy; and the paraphrase it offers is a sentence the engine honours. This is the cheapest high-value fix in the row.

### No model — local or cloud — is ever consulted for any of it

Two independent blockers, both *read* and consistent with every prior measurement:

1. `llm_client.py:1066-1067` — `if fast_result.confidence >= LLM_FALLBACK_CONFIDENCE_THRESHOLD: return False`, threshold `0.7` at `:63`. These sentences parse at 0.90–0.95.
2. `llm_client.py:1081` — `if fast_result.refusal: return False`. A guard refusal is terminal by design.

And structurally: `result["strategic_condition"]` is written at **exactly one site**, `parser.py:1991`, inside `if strategic:` where `strategic = detect_strategic_command(...)` — a deterministic regex layer. The LLM's own `is_strategic` / `strategic_type` / `strategic_condition` are discarded even though `prompt_builder.py:501-506` and the `PARSE_TOOL` schema ask for them.

**Write this in the spec so it is not re-litigated mid-row:** making a model useful here needs a merge site *and* a confidence demotion for condition-bearing utterances *and* a widened tool schema. The second is the larger and riskier half. It is a separate row and this one must not block behind it.

---

## 2. The obstacle — `clause_guards`, and why it exists

`backend/ai/clause_guards.py` is subtractive by design: it **blanks** subordinate clauses with spaces, same-length, never splicing, and never picks an action. The index-preserving blank is load-bearing and the file says so at `:20-25`.

The verdict is binary today — `strip_condition_clauses` (:436) returns `(text, refuse: bool)` over **9 REFUSING** markers (`as soon as, in case, provided that, provided, if, unless, when, once, after`) and **3 BLANK-ONLY** (`until, while, before`). Refusal is gated on a two-word floor at `:473`.

It exists because of five named defects, each of which a careless widening re-opens:

| # | Defect | Why the guard shape prevents it |
|---|---|---|
| 1 | **PARSE-NEG headline** — `Ney, if Mack advances fall back to Alsace` *marched immediately at 0.95*: a subordinate clause's keyword outranked the main verb | `if` stays in REFUSING; pinned `parseneg-conditional-refuses` |
| 2 | **Phantom-province family** — un-blank a clause and the free-text target scan reads its nouns as provinces (pinned 8 ways; live today as `fortify before Mack arrives` → `target='Mack'`) | the blank stays |
| 3 | **until/then** — terminating `until` at `then` leaves `attack` standing | `_UNTIL_CLAUSE_END_RE` (:68) runs to sentence end |
| 4 | **CR-2 index shift** — the executor-eligibility scan and the `Marshal <Name>` capture index into the text | same-length blanking, never splicing |
| 5 | **FA-7 two-marshal P1** — a clause left standing under a leading address is re-addressed to the wrong marshal | `address_governs_only_deferred_text` (:353) |

`strip_deferred_clauses` (:288-290) additionally carries a **written production ruling** against the thing a queue would build: *"the engine holds no order until a later turn and inventing one would hand out free actions."*

**The guards are not the main obstacle.** They are one of three, and the smallest. The other two are the swallow regex in `parser.py` (which destroys the clause before any guard sees it) and the fact that nothing consumes `dropped_sequel`. That ordering is why the guards are touched fourth, not first.

---

## 3. THE PLAN

Eight slices, **5.0 sessions**, in build order. Four stopping points; at each the game is better and nothing is half-built.

| # | Slice | Effort | Stop? |
|---|---|---|---|
| 1 | The tail stops eating the head | 0.5 | ✅ **Stop-1** — P1 dead |
| 2 | The harness can see it | 0.25 | |
| 3 | Nothing is dropped in silence — and the tail comes back | 1.0 | ✅ **Stop-2** — multi-step works |
| 4 | The engine says what it heard | 1.0 | ✅ **Stop-3** — conditions honest |
| 5 | The third verdict — a narrow conditional grammar | 1.0 | kill-gated |
| 6 | The arrival order carries its object | 0.5 | kill-gated **first** |
| 7 | The completer and the School teach both forms | 0.5 | |
| 8 | The queue is retired by contract (GR9) | 0.25 | ✅ **Stop-4** |

---

### CR-7-1 — The tail stops eating the head · 0.5 session

**Grafted from B1's MS-0, and pulled ahead of the harness.** The P1 is live in 40 of 40 shapes and its pins cannot live in the corpus anyway (the corpus can't express `dropped_sequel`), so the instrument is not a prerequisite.

Invert the exemption from a negative enumeration to a positive rule: **a tail may fuse onto a head only if that head can CARRY an arrival.** `attack_on_arrival` is a movement idiom — the code's own comment at `parser.py:78` says so ("it means march there and hit whatever you find"). So the exemption survives when clause 1 names a march (`march|move|advance|proceed|head|go` to `<region>`) or carries `until` (`_ENGINE_CONDITION_RE`, :90 — the one condition the engine implements). A closed set of six verbs replaces an open set of everything-else.

Three riders in the same seam:

- **Unify `move to` with `march to`.** Measured: `Ney, move to Swabia` alone yields `strategic_type=None` while `march to` yields `MOVE_TO`. The completer offers both (`main.gd:6970-6971`). A synonym divergence on the game's most basic order.
- **Kill the `and then` phantom.** `_SEQUEL_SPLIT_RE` matches ` then `, the attack-tail rule then declines the split, and the orphan conjunction rides into the target: `Swabia And`, `in world.regions` → False.
- **The `;` degradation.** `march to Swabia; attack Mack` → `MOVE_TO` with `attack_on_arrival=False`. The semicolon silently downgrades the engine's one supported two-step order to a plain march.

No `clause_guards` change. No queue. The tail lands in the existing `dropped_sequel` warning path, which already works.

**done_when** — flip experiment, both arms, on the 1805 board:

- (a) The 40 non-movement shapes go **40 SWALLOWED → 0**, each producing its own action plus a `dropped_sequel`.
- (b) Must-keep, byte-identical: `march to Swabia then attack Mack` → `MOVE_TO` / `aoa=True`, no split. `advance to Swabia then attack Mack` likewise. `hold until Davout arrives then attack Mack` stays one parse. `wait for Davout then attack Mack` still splits (FA-7's own case).
- (c) `and then` yields a real province on 3 of 3 (`target in world.regions`); `;` preserves `aoa=True`.
- (d) Corpus rows `cr2-march-to-vienna-then-attack-not-split`, `cr2-march-then-attack-named-object-not-split`, `parseneg-until-then-attack-holds`, the three `fa7-*` rows, `secure-and-hold-vienna`, `defend-and-hold-belgium`, `fa50-attack-and-hold-keeps-the-attack` — green with assertions **unedited**.
- (e) **Sensitivity arm (graft, B1):** restore the old predicate and ≥30 of the 40 shapes must red. `python -m backend.ai.parser_eval` reports 688/688 in *both* arms, so **a green corpus is not evidence here** — say so in the test docstring.
- (f) `BASELINE_SERIES` and M1–M7 **byte-identical without re-record**. This is a parser slice; the AI does not type. A moved series means the change reached the engine — bisect and stop.

---

### CR-7-2 — The harness can see it · 0.25 session

Measured: `ALLOWED_EXPECTED_KEYS` (`parser_eval.py:71`) is **11 keys** — `success, marshal, action, not_action, target, type, strategic_type, target_stance, requested_type, error_contains, diplo`. Of 449 corpus rows, **0 assert `strategic_condition`, 0 assert `dropped_sequel`, 0 assert `attack_on_arrival`**, while 24 carry a compound/conditional marker.

Worse: `evaluate_entry` (:147) has **no unknown-key arm**. It checks only the keys it recognises, so a row asserting `dropped_sequel` with deliberately wrong values reports **PASS** on the CLI. The hygiene gate lives in `tests/test_command_robustness_cr1_eval_harness.py:128`, not in the CLI — a CLI-green run is not evidence.

Add `dropped_sequel`, `warning_contains`, `strategic_condition`, `attack_on_arrival`, each with an assertion arm; make the CLI **refuse** an unknown expected key rather than ignore it. Record in the docstring the one thing it still cannot do: the entry schema has no key for a *prior* command, so CR-4 carryover is structurally uncoverable by corpus and its pins live in pytest.

**done_when:** a row asserting `dropped_sequel: "attack Mack"` against a sentence that drops something else **FAILS** the CLI (today it passes). The 24 existing marker rows carry the value they actually produce. Unmodified corpus still 688/688 mock + 6/6 replay, keyless.

---

### CR-7-3 — Nothing is dropped in silence, and the tail comes back · 1.0 session

Where the multi-step *experience* lands, for the price of a payload key and a keypress.

**The mechanism already ships.** `main.gd:_on_tutorial_suggest_command` (:6893) is a chip-latch-respecting command-line fill whose own docstring states this slice's philosophy verbatim:

> *"the tutor chip FILLS the command line — the player presses Enter themselves (muscle memory for a typed-command game). It never sends."*

So: the tail rides the response as a live key on **every** arm (success, refusal, objection, clarification, interrupt), stashed on the world for exactly one command's life on the question arms and raised when control returns — the NA-6b stash-and-raise discipline already used for the Proclamation and the deferred petition. The client fills the command line behind one key.

Three measured holes to close:

- A **refused** head loses its tail in silence (`main.py:3584` gates on `success`). Deliver the note on a refusal too, in the refusal's own voice, stating the rule: *a refused head cancels the tail, and the tail is never promoted to a new head* — the player wrote it to follow something that did not happen.
- The comment at `main.py:3581-3583` claims objection popups skip the note because it "re-surfaces if the reissued/proceeded command re-parses". Measured **false** on all three arms — `insist`/`trust`/`compromise` is a different utterance and never re-parses the compound. Replace the claim with what happens. (This repo's recurring shape: a production comment asserting a recovery path that does not exist.)
- A third clause behind an attack-on-arrival tail is lost silently. Re-scan the tail for a second boundary and name what lies past it.

**Cancel semantics: there is nothing to cancel.** A relayed tail is an ordinary new command — editable, ignorable, and it pays its own AP when sent. `strategic_executor._execute_cancel` (:2495) is untouched and gains no step addressing.

**done_when:** a 14-shape battery reports the dropped tail on **14 of 14** — on success, on a refused head, and after each of `insist`/`trust`/`compromise`. The relay key round-trips and re-fills the line verbatim. **Zero new serialized fields**: the stash is transient, pinned *not* to survive save/load, with a pin that `load_game` does not resurrect it. FA-50's `tests/test_fa_slice1_the_two_words_2026_09_02.py:611-616` is flipped **consciously**, MESSAGE-only (the split itself must not change — the muster surface depends on it), with its falsified docstring rationale on the record.

> ⚠ **Integrity check, keep it:** if the tail must survive save/load for the relay to work, the design is wrong — a serialized relay is the queue wearing a disguise. Stop and re-gate.

---

### CR-7-4 — The engine says what it heard · 1.0 session

Conditions, **no grammar change** — pure defect work on a live substrate.

1. **One shared vocabulary module** read by both `_strip_conditions` (:579) and `_parse_condition` (:804). Widening either alone is measured worse than the defect. Cover `until|till|'til|until such time as`, the `Marshal <Name>` honorific the game itself prints, word-numbers (`for three turns`).
2. **Validate the referent.** `until\s+(\w+)\s+arrives` `.capitalize()`s with no roster check. Refuse `Godot`/`relief` by name instead of minting an order that can never complete.
3. **Floor `for N turns` at 1.** `for 0 turns` is accepted today and self-completes with *"grows restless"*.
4. **`until turn 5`** — refuse it or map it; it silently drops while the confirmation still promises a standing hold.
5. **Fix `until_battle_won`'s stale read** *(graft, B2 — and take its correction, not its framing)*: swap the read to the **order-scoped** `StrategicOrder.last_combat_result` (`marshal.py:129` — already exists, already serialized, already written by the same module at `strategic.py:4493`). Do **not** "clear the 16 marshal-scoped writes": that breaks the ally-victory arm (`strategic.py:3426`) and the SUPPORT arm of this very condition (`:3935`).
6. **The echo.** The confirmation is byte-identical across six different conditions today (`"Davout will hold Lorraine. Holding position."`). One sentence per accepted condition, from the single source `ledger._derive_condition_text` already reads. Shown == applied.
7. **The refusal stops lying.** Split `main.py:3457-3463` by cause: a sentence about a friendly arrival never blames the enemy.

**done_when:** the 15-phrasing battery yields **0 phantom provinces** (every issued order's target is in `world.regions`) and **0 unmeetable conditions** (every `until_marshal_arrives` names a marshal on the board). `for 0 turns` and `until turn 5` refused with their own reasons. Every accepted condition named in the confirmation AND the Ledger, drift-pinned against one source. M1–M7 + `BASELINE_SERIES` byte-identical.

---

### CR-7-5 — The third verdict · 1.0 session — *kill-gated*

The only slice in the PARSE-NEG minefield, and it lands **after** the echo exists to show what a widened grammar took.

`strip_condition_clauses` gains a **third verdict** — REFUSE / BLANK-ONLY / **HAND-OFF** — and returns the clause **span** alongside the index-preserving blanked text. The precedent is in the same file: `negation_marker_spans` (:177), landed by FA-N2 for exactly this reason.

HAND-OFF fires for **one** predicate family in v1: `<friendly marshal> arrives`. So `when|if|once|as soon as <marshal> arrives, hold <region>` lands on the existing `until_marshal_arrives`.

**Four non-negotiables** *(grafted from B2, which words them best)*:

- (a) The index-preserving blank **stays** and is never spliced.
- (b) `_REFUSING_CONDITION_WORDS` is **never widened** beyond its 9 members.
- (c) HAND-OFF fires only on a span matching the CR-7-4 closed grammar, and **fails closed** — this is IQ-7's lesson verbatim: *a rule built by stripping what you recognise is only as safe as the list it strips; for an irreversible priced answer, write the allowlist out and fail closed.*
- (d) The refusal stays **terminal** (`llm_client.py:1081`). A HAND-OFF is not an escalation; no model is consulted; GR6 holds and the shipped keyless mock default gets the whole feature.

Two ordering defects ride along: `strip_negated_clauses` runs before `strip_condition_clauses` (`llm_client.py:1539-1540`) so the blanked clause fails the two-word floor and `attack Mack if he is **not** fortified` **fights** while its un-negated twin is correctly refused; and `_SHOULD_INVERSION_RE` (:427) is clause-initial only, so a trailing `should` fights. Close the comma leak too (`attack if, Bavaria is threatened` → `target=Bavaria`).

> **The counterfactual that makes the ordering fix safe to attempt** *(graft, B2)*: re-asking the word-count floor against the PRE-negation text flips **0 of 449** corpus rows. Carry that number onto the slice.

**done_when:** `if|when|once|as soon as <friendly marshal> arrives` produces the same order and condition as `until` on 8 of 8. `if Mack advances fall back to Alsace` still **REFUSED**. `attack Mack if he is not fortified` refused exactly like its twin. Trailing `should` refused. No province conjured by the comma leak. At most 3 of the 7 pinned refusals flip, named in the commit; the 17 guard rows and the 3 "accepted-not-ideal" elliptical rows stay green.

---

### CR-7-6 — The arrival order carries its object · 0.5 session — *kill-gated FIRST*

⚠ **Run the reachability probe before writing a line.** `attack_on_arrival` is a bare boolean (`marshal.py:109`) and `strategic.py:2461` then picks `target = enemies[0]` — the named quarry survives nowhere. Replace it with a declared `arrival_action: Optional[Dict]` (verb + target), keeping the bool as a derived read for one release.

Three traps:

- **Serialization gate is blind here** *(graft, B2)*: `tests/test_serialization_enforcement.py:get_instance_attributes` short-circuits on `is_dataclass`, so it sees declared fields but not runtime attributes. It must be a **declared** dataclass field in `to_dict` and `from_dict`, with its own round-trip pin.
- **Four construction sites**, different kwarg sets — above all the **12-kwarg objection-resume rebuild** at `strategic_executor.py:~2046`, which would silently eat it on any objection.
- No new **top-level** serialized field: it nests in the marshal dict and `from_dict` reads every optional key with `.get()`, so legacy saves load by construction.

**done_when — kill gate checked first:** a probe makes the arrival attack fire deterministically on the player path. I measured `_complete_order` reachable (below) but did **not** measure `attack_on_arrival` firing, and two prior agents drove ~8 marches and saw zero: `_handle_move_to_arrival` (:2453) fires only when the destination is empty at issuance and an enemy arrives later, while the `destination_blocked` interrupt repeats `awaiting_response` forever (the NPC-16 family). **If it cannot be made to fire in one probe, this slice does not land**: the phrasing is refused honestly, the row closes with the measurement, and no payload is enriched that nothing consumes.

If it fires: `march to Swabia then attack ArchdukeCharles` engages Charles and not `enemies[0]` when both stand there; save/load round-trips; an objection answered `insist` preserves it; a legacy save with only `attack_on_arrival: true` still fights.

---

### CR-7-7 — The completer and the School teach both forms · 0.5 session

Measured: `_MARSHAL_VERBS` (`main.gd:6968`) is 12 rows with no `then` and no condition slot; `for 3 turns` and `until … arrives` appear nowhere in `main.gd`.

Offer three continuations, all derivable from payload the response already carries: after a completed movement destination, ` then attack <enemy at or adjacent to it>`; after `hold <region>`, ` until <friendly marshal> arrives` and ` for 3 turns`. Behind the token, the same verb table. Help block + tutorial order card gain the relay key.

**The founding rule — the game must not offer a sentence it cannot read — and the existing pin cannot enforce it.** `tests/test_cx3_the_predictor.py:190` samples `region = world.get_marshal(marshal).location`, i.e. the marshal's **own** province, which is precisely the input under which a silent substitution is invisible; and the file's executor census asserts on message substrings, never on `success`.

**done_when:** every phrasing the completer offers parses to the action it claims **and** returns `success: True` through the real executor, on a province the marshal is **not** standing in — the repaired pin shown RED against today's `garrison` row first. Every quoted phrasing in the new help block is driven through the executor in the same pin. A player who has never read a doc can produce one compound and one conditional order from completions alone, scripted as a keystroke sequence.

---

### CR-7-8 — The queue is retired by contract · 0.25 session

The N-step order queue held across turns is **not built**, and the promise is **removed**, not deferred. GR9 forbids the third option.

**The reasons are measured, not aesthetic.** I spied `_complete_order` and `_break_order` and drove 14 real end-turns with three standing player marches:

```
ISSUE Soult, march to Bordelais     ok=True  MOVE_TO -> Bordelais  from Orleanais
ISSUE Davout, march to Bordelais    ok=True  MOVE_TO -> Bordelais  from Lorraine
ISSUE Bernadotte, march to Anjou    ok=False (refused at issue)

turn  2  Soult=Orleanais/MOVE_TO   Davout=Lorraine/MOVE_TO   completes=0 breaks=0
turn  6  Soult=Bordelais/None      Davout=Lorraine/MOVE_TO   completes=1 breaks=0
turn 12  Soult=Bordelais/None      Davout=Lorraine/MOVE_TO   completes=1 breaks=0
turn 13  Soult=Bordelais/None      Davout=Lorraine/None      completes=1 breaks=0
turn 15  Soult=Bordelais/None      Davout=Swabia/None        completes=1 breaks=0

_complete_order fired 1 time  (Soult, France, turn 6)
_break_order    fired 0 times
```

Three findings, all decisive:

1. **The hook both losing plans build on fires once in fourteen turns.** Soult completed; that is the whole yield.
2. **`_break_order` fired zero times while Davout's order demonstrably died** between turns 12 and 13 — nulled at one of the other 41 sites, silently. B1's MS-3 hooks its lapse notice at `_break_order`; it would have been **silent on the only real lapse in the run**.
3. **Davout stood at Lorraine for eleven turns holding a live `MOVE_TO Bordelais` and never moved one province.** A queue behind that head waits forever.

Add the containment census: **42 `strategic_order = None` sites across 11 files** (`backend/commands/{executor,strategic,strategic_executor,combat_executor,tactical_executor}.py`, `backend/models/{marshal,world_state}.py`, `backend/game_logic/{diplomacy,jealousy,marshal_overview,withdrawal}.py`) — and six ordinary player verbs wipe the order **even when the command is refused at 0 AP**, so a queue would be destroyed by commands the player never got to make. Plus: `_complete_order` pays a literal marshal +5 trust (`strategic.py:3960`; Soult is the 1805 literal), so a per-step advance routed through it is a trust farm scaling with step count. Plus `clause_guards.strip_deferred_clauses` (:288-290) already rules against it in production source.

This slice **ratifies** that ruling rather than leaving an unowned "future work" label. The answer to multi-step is CR-7-3's relay plus CR-7-6's depth-1 arrival action, and no surface claims otherwise.

**done_when:** a census pin over every player-facing producer (backend + `.gd`) finds no string offering to hold, queue, save or defer an order for a later turn, with a sensitivity arm that reds when such a string is planted. `COMMAND_ROBUSTNESS_SPEC.md` carries the ruling, its measured reasons and **two** re-open conditions (below). `docs/STATUS.md` carries the tracking line. The "CR-6/CR-7 scope" ambiguity in PARSE-NEG §8 rule 5 resolves in writing to CR-7.

> ⚠ Also fix the spec's own stale pointer: `COMMAND_ROBUSTNESS_SPEC.md:36` and `:43` send CR-7 to `validation.py:195` for the multi-marshal string; the real site is `validation.py:410-413`. Line 195 is `NEVER_STRATEGIC_ACTIONS` commentary.

---

## 4. What it costs

**AP — pay once at issuance, steps free.** The engine's existing model: `marshal.strategic_order_ap` (`marshal.py:912`) is the single source (2; 1 for literal, sovereign, or auto-upgrade), and `executor.py:1427` makes `_strategic_execution` free. The same intent typed as two commands costs 3 AP *and* the second destroys the first's order. Per-step pricing would invent a second model. **But the overrule must be written at the seam**: `clause_guards.py:288-290` rules against holding an order for later; a *condition* is a trigger the engine already evaluates every turn, which a bare deferral is not. Say so in code and amend that comment to name the carve-out. A relayed tail (CR-7-3) pays its own AP — that is not a carve-out at all.

**`_strategic_execution` carries three rules, not one.** It makes the step free (`executor.py:1427`), **un-objectable** (`:1714` — *"marshal can't object to own decision"*), and exempt from the standing-decision refusal (`:1677`). Copying the pattern silently decides a marshal may never refuse step 2. That is a design ruling — *a marshal may refuse the order, not its second step* — and belongs in the record, not in a side effect.

**Serialization.** CR-7-3: zero new fields (transient stash, pinned not to survive save/load). CR-7-6: one **declared** dataclass field on `StrategicOrder`, nesting in the marshal dict, no new top-level `WorldState` field — with the `is_dataclass` blind spot and the four construction sites above.

**Objection / interrupt / rout / refused head.** Inherited unchanged. A refused first step ends the order it created (slice 3's `attack_was_refused`, consulted at `strategic.py:2478`). A rout or capture nulls the order and anything it carried dies with it — correct, the order is what carried it. Three of the 42 sites need a conscious ruling: `executor.py:1785` (six verbs wipe on a refused command at 0 AP), `main.py:3586` (refused head drops the tail), and the objection path whose comment claims a recovery measurement shows does not exist.

**GR5 — the AI does not get this, and that is the rule, not an omission.** `SYSTEMS_REFERENCE.md` §23 explicitly exempts the strategic command system from Building Blocks, and `process_strategic_orders` (:1105) filters on `player_nation`, so an order planted on an AI marshal is inert furniture that never clears. The pin is the inverse of the usual one: **nothing may plant a strategic order on an AI marshal.**

**Cancel.** Unchanged, whole-order, keyed on the marshal, 1 AP, −3 trust unless cancelled the turn it was issued (`strategic_executor.py:2495`). No step addressing, because nothing is held.

**Completer.** 12 rows today; +3 continuation tokens; the CX3 predictor pin repaired to drive the executor on a province the marshal is not standing in.

**Corpus.** 449 rows, 24 with a marker, **0 asserting any of the three new keys**. The harness must land (CR-7-2) before any row can bind — and **any pin written for CR-7-1 must live in pytest driving `POST /command`**, because the corpus reports 688/688 in both arms of the swallow fix.

---

## 5. Kill criteria and the recorded dissent

### Kill criteria

1. **CR-7-1 moves the board.** `BASELINE_SERIES` or M1–M7 diverge on a parser slice → the change reached the engine. Bisect and stop.
2. **CR-7-1 is partial.** Any SWALLOWED shape survives in the 40-shape battery. A partial fix is worse than none: it teaches the player that some compounds are safe.
3. **CR-7-5 cannot fail closed.** *(graft, B2's wording — it states the falsifiable trigger)* If permitting conditions requires widening `_REFUSING_CONDITION_WORDS` beyond its 9 members or loosening the two-word floor at `clause_guards.py:473`, **STOP and ship CR-7-1/2/3/4 alone**. Those are defect fixes and need no guard change. Conditional orders are a feature; PARSE-NEG was a P1 that executed orders the player had forbidden. The trade is not close. The corrected refusal copy ships either way.
4. **CR-7-5's negative controls.** If any of the five named defects reproduces under its own control, the slice closes as refused-with-measurement.
5. **CR-7-6's probe fails.** No deterministic arrival attack on the player path → the slice does not land, by design. Likely outcome; a planned stop, not a failure.
6. **Any new pin survives its own stated killer**, or comes back INERT in a mutation sweep. This repo has found real weaknesses in ~20 pins that way, including source censuses matching the comment explaining the guard. `git diff` after every sweep — a crashed sweep once left `if False:` in production source.
7. **CR-7-3's stash needs serialization** → the design is wrong; re-gate.

### Recorded dissent

**The relay does not answer the multi-turn case, and that is the case people type multi-step *for*.**

`Soult, march to Bordelais, then fortify` is a five-hop march. Handing `fortify` back and inviting a keypress produces the wrong order at the wrong province, at full AP. B1's closing sentence is the correct objection and CR-7-3 does not answer it: *a march that takes five turns will always outlive the player's memory of its tail.* The relay solves silence, not memory.

Three things keep this from overturning the plan, and all three are measured:

- The alternative does not work either. `_complete_order` fired **once in 14 turns**; `_break_order` fired **zero** times while two of three orders died. A queue built on that hook is furniture, and its lapse notice — hooked where B1 puts it — would have been silent on the only real lapse.
- The P1 dies in slice 1 regardless, and the gap is **owned** by CR-7-8 rather than hidden.
- Davout's eleven-turn stall says the churn is in the *board*, not only in the queue design.

**Two mitigations, both binding:**

1. **CR-7-3 must not ship copy implying the tail can simply be sent.** For a tail behind a multi-turn strategic head, hand it back **with its moment named** — *"Soult reaches Bordelais in ~5 turns; send this then, or order him to hold until he arrives"* — or refuse to relay it at all.
2. **CR-7-8's contract carries a SECOND re-open trigger.** The first (a player re-typing a relayed tail unchanged on >10% of compound commands) does not catch the real case. Add: **if `_complete_order` fires for player marshals above a floor — say 5 per 40-turn commanded arm on `tools/playtest_scripts/commanded_full40.json` — the queue is re-opened**, because the churn that makes it furniture has been fixed. Measure it off the committed driver archive, not off an impression. And run that measurement **during** CR-7-3, not after, so the row learns whether the queue is reachable before it finishes designing around its absence.

**Secondary dissent:** CR-7-3 flips FA-50's `test_the_address_form_is_not_split` on the strength of a measurement (that its "must still muster both" rationale is false) that I did **not** reproduce myself. Re-measure the muster control before flipping that pin, not after. This repo has shipped a regression of the exact class it was fixing in three consecutive slices, and every time the reviewers' first move was to change one fixture parameter the builder had held constant.

---

## Corrections to the source material, carried forward

| Claim as filed | Measured |
|---|---|
| `ALLOWED_EXPECTED_KEYS` has 12 keys | **11** (`parser_eval.py:71`) |
| The swallow is "8 of 11" / "36 of 40" | **40 of 40** non-movement shapes; 10 distinct heads, all four tail forms |
| `_complete_order` "fired once in six turns" / "zero in twelve" | **1 in 14 turns, 3 standing marches** — reachable but rare |
| A lapse notice at `_break_order` covers the lapse | `_break_order` fired **0** times while an order died |
| `move to` and `march to` differ only in compounds | `move to Swabia` **alone** yields `strategic_type=None` |
| 42 null sites / 9 files | 42 sites / **11 files** |
| `for 0 turns` yields no condition | yields `max_turns=0` — a paid order that self-completes |
| `Marshal` has `personality_type` | it is `personality`; `personality_type` raises `AttributeError` (the IGR-E family — worth an AST census if any new code reads it) |

All figures above are **measured** this session at `CommandParser.parse` or `POST /command` on `europe_1805.json`, seed `historical`, `LLM_MODE=mock`, except where marked *read*. No repo file was modified; probes live in the session scratchpad.

---

## CR-7-1 — LANDING RECORD (September 22, 2026)

**Landed on master; the HEAD the slice was measured and built against is
`a6661032`.** `tests/test_cr7_1_the_tail_stops_eating_the_head.py` (**106**) ·
`tools/_sweep_cr7_1.json` **14 mutations / 14 killed / 0 INERT** · `BASELINE_SERIES`
+ M1–M7 **byte-identical without re-record** (63 pins) · golden corpus **688/688 in
BOTH arms**, as this contract predicted — not evidence · ruff clean · zero `.gd`,
zero new serialized fields · files touched: `backend/commands/parser.py`,
`backend/ai/strategic_parser.py`.

### Re-measured first, on the landing HEAD

- **40 of 40 SWALLOWED** at `CommandParser.parse` (`action=attack`, no strategic
  order, no `dropped_sequel`, no warning) — the table in §1 reproduces exactly.
- `POST /command`: `Ney, fortify then attack Mack` → success, AP 4→3,
  Rhineland→Swabia, **24,000 → 21,720**, `fortified` False, a battle report,
  `warning=None`. (§1's 22,050 is the same defect at a different combat roll.)
- **Also measured, not in the contract:** `Ney, march to Swabia and attack Mack`
  → **SPLIT** (`action=move`, `dropped_sequel="attack Mack"`). FA-50's bare-`and`
  arm (`_and_clause_is_a_second_order`) had no arrival exemption, so the `and`
  form of the engine's one two-step order — `_detect_attack_on_arrival`'s own
  "and attack" hint — was degraded to a march plus a "One order at a time" note
  while the `then` form fused. `Ney, support Davout then attack Mack` → fused
  SUPPORT with `attack_on_arrival=True`, a flag SUPPORT's executor never reads
  (the tail lost one stage later). `Ney, march to Swabia, attack Mack` → MOVE_TO
  with `attack_on_arrival=False` (the comma sibling of the `;` degradation).

### What was built

1. **The positive rule** — `parser._head_can_carry_arrival`, behind the flip lever
   `TAIL_FUSES_ONLY_ONTO_A_MARCH` (False reproduces the pre-slice predicate
   byte-for-byte). A tail beginning `attack|engage|assault` fuses onto the head
   ONLY when `strategic_parser.clause_can_carry_an_arrival(head)` — the head's
   `_detect_strategic_type` is in `ARRIVAL_CARRYING_TYPES = {MOVE_TO, PURSUE}`
   AND `_extract_target_text` names a destination — or when the head is a
   standing order (`clause_is_a_standing_order`) carrying `until`. Measured
   while building: a bare `until` arm re-opened the swallow on `fortify until
   Davout arrives then attack Mack`, hence the standing-order guard.
   - **Why the set is DERIVED, not the contract's six verbs.** §CR-7-1 named
     `march|move|advance|proceed|head|go`. `advance on`, `fall back to`,
     `withdraw to`, `push to`, `make for`, `retire to`, `march north` are all
     MOVE_TO heads the six would have split, and `move`/`go` are the tactical
     forms (rider, below). The routing table is the one source — the CX-7 lesson
     the queue's own D-block states for CX-R1 applies here too.
   - **Why PURSUE is in and HOLD / SUPPORT are out.** The executor reads
     `order.attack_on_arrival` in `strategic._handle_move_to_arrival` and the
     PURSUE contact arms only. A tail fused onto SUPPORT is stamped and lost —
     the same defect in a different coat. It is reported now.
2. **The same rule at FA-50's `and` arm**, closing the `and attack` degradation
   found above; `fortify and attack Mack` still splits (control pinned).
3. **`and then` consumed whole.** `_SEQUEL_SPLIT_RE` takes the optional `and`;
   `_strip_conditions` cuts `and then|and|then` + `attack|engage|assault`;
   `_clean_target_text` drops a dangling conjunction (a region name never ends
   in one). The CR-2 pin `test_split_helper_attack_on_arrival_not_split` asserted
   the helper's verdict on "march to Vienna and then attack" and never read the
   destination it produced — **"Vienna And"**. The three unit seams are pinned
   separately so belt and braces cannot mask each other in the sweep.
4. **`;` keeps the arrival.** `_detect_attack_on_arrival` is a boundary regex
   (`then` / `and then` / `and` / `;` + the three tail verbs, word-bounded so
   "Holland" is not a conjunction; `then assault` joins the hint set the split
   gate already exempted).
5. **The rider, scoped** — `parser.promote_tactical_move_with_arrival_tail`,
   applied in `parse()` after the typo repair and under the same lever: a
   `move to` / `go to` head with an arrival tail becomes `march to` before any
   reader, so the fast parser, the split gate and `detect_strategic_command`
   agree by construction (the CR-4 / NP-1 raw-string precedent). The typed text
   stays `raw_input` / `raw_command` (R1-11) — their readers (save/load, the
   interrupt's `original_command`, the diplomatic verbs, the bombard-verb check)
   never re-derive the march. A head that is already a standing order (`move to
   reinforce Ney` = SUPPORT) is left alone. **Bare `move to` is NOT unified** —
   see the correction below.

### The sweep, and what it took

`tools/_sweep_cr7.json` — **33 mutations, 33 killed, 0 INERT at close.** The FIRST sweep (31 mutations) came back **8 INERT**, and every one was a real weakness, six in my own pins and two in the code:

- **Two guards deleted rather than kept as unpinnable belt.** The comma arm's separate bare-address guard and its whole-sentence-refusal guard were both INERT beside the verb-opening guard — a bare name, `the Guard`, and `should Mack advance` are all refused by "the head must OPEN with an order verb after its address", so the other two could be removed with nothing left to pin.
- **Six pins repaired:** the ledger drift pin compared a ONE-armed condition (a local copy naming "until X arrives" reads identically — now a two-armed condition, `for 3 turns until Ney arrives` → "3 turn(s) remaining, until Ney arrives"); the friendly-arrival refusal pin used Davout, whom the generic arm's own example happens to name (now Soult); the sole-condition guard was pinned with a second clause the chain refused anyway (now an elliptical `unless attacked`, which only the guard catches); the objection-resume rebuild was pinned through `insist`, which re-executes through the PRIMARY site (now `compromise`, the arm that builds through the rebuild); the completer's half-typed-target guard was a loose source census satisfied by the hold branch alone (now both branches' own lines); the combat-seam stamp was pinned through `_execute_attack`, which skips the pipeline's step (now a census over both blocks, stated as such).
- **The full suite found what the sweep could not:** the comma arm's first cut split `Ney, wait, march to Lorraine` into a free wait and a dropped march — FA-R3's own pin (`test_fa_slice14_…::test_the_order_is_charged`), one file the slice never named. WO-6's leading filler is now a span no comma inside may cut, and the FA-R3 sentence is re-pinned in `test_cr7_3_…` beside the other filler shapes.
- **A second probe found the clarification arm silent:** the CR-2 questions ("Which marshal, Sire?", the did-you-mean) are built as fresh dicts, so a relay stamped on `result` never reached them — `_relay_question` now attaches the tail at both builders, the did-you-mean's own parse failure carries `dropped_sequel`, and a marshal-less head ("scout Swabia, then fortify") re-addresses the relayed tail to the man who acted (read off the first event — the executor's result carries no `marshal` key).
- **A pre-existing flake widened CQ-11:** WO-6's `test_end_to_end_the_marshal_retreats_and_never_waits` went red in a long batch on the objection roll (aggressive Ney objected to the retreat); pinned at 0.5 like the rest.

### The hook's full run, and what it took

The pre-commit hook's first full run (24,162 passed) blocked the commit on **seven** failures in two families — neither visible to the slice's own files run alone, both recorded here rather than buried:

- **Four legacy `until_battle_won` pins hand-set a victory without its turn** (`test_strategic_executor`, `test_strategic_ui_comprehensive` ×2, `test_systems_v3_session5`). Item 5 reads a marshal-scoped result only when `last_combat_turn >= started_turn`, and *a result with no turn reads as stale* — the rule this slice's own pin states. Every production writer stamps both fields in the same block (the CR-7-4 census pin requires it), so the four fixtures now stamp `last_combat_turn = world.current_turn` beside the result they simulate; **their assertions are unchanged**. The alternative — reading a missing stamp as "unknown, accept" — would have kept the pre-slice behaviour for a pre-CR-7-4 save and was declined: it re-opens the defect for exactly the save that carries it.
- **Three CR-7-6 spy pins were BLIND in the full suite and green alone**, and the cause is a suite-wide hazard: `test_command_robustness_cr5b` monkeypatched `execute` on the executor **instance** (`monkeypatch.setattr(m.executor, "execute", …)`); pytest records `getattr(instance, name)` — the BOUND method — and its undo writes that bound method back as an **instance attribute**, which shadows the class for the rest of the session. Every later class-level patch of `CommandExecutor.execute` — the CR-7-6 spy — was silently bypassed for the singleton, so the spy reported an empty list under a battle that plainly happened. Bisected by halves over the 130 files that precede CR-7-6 alphabetically (the suite runs in file order; pytest-randomly is not installed). **Ten instance-level patches across five files converted to class-level** (`type(obj)`; a `__getattr__`-delegated name such as `_execute_cancel` is patched on the SUB-executor's class, since `vars(M.executor)` never holds it) — including a fourth FA-26 site patched through a local alias that no source census can see. Pinned twice: a static census in `test_cr7_6_*` (target resolved on `backend.main`; a genuine instance attribute such as `_combat` is exempt; its own example strings are split so the scan cannot read them) and a **session-end guard in `tests/conftest.py`** that flags any bound-method instance attribute on the 16 singleton objects (none exist at boot — measured) so an alias-form offender anywhere in the suite fails the run by name. Both proven with a deliberate probe (direct and delegated shapes) that was then deleted — and the guard earned its keep on the hook's SECOND full run, naming two more sites in `test_wo_slice11` under a module alias (`m_mod`) the census had not listed. The spy fixture itself now names the cause instead of reporting an empty list.

### `done_when`, disposed

- **(a)** 40 → **0** ✅ — each row's action and target equal the bare head's own
  parse (so the pin binds to the rule, not to a hand-typed action list), and
  `dropped_sequel == "attack Mack"` on all 40.
- **(b)** ✅ `march to` / `advance to Swabia then attack Mack` → MOVE_TO,
  `aoa=True`, no split; `hold until Davout arrives then attack Mack` one parse
  with `{until_marshal_arrives: Davout}`; `wait for Davout then attack Mack`
  splits; the CR-2 helper pins hold unedited.
- **(c)** ✅ `and then` → a real province on 3 of 3 and the CR-2 sentence now
  reads "Vienna"; `;` → `aoa=True`.
- **(d)** ✅ the nine named corpus rows green on every world they name, their
  `expected` blocks frozen inline in the test and compared — unedited by
  construction.
- **(e)** ✅ lever DOWN → **40 of 40** SWALLOWED again (≥30 required); the lever
  also governs the rider and the `and` arm, so the arm proves what it claims.
- **(f)** ✅ series + M1–M7 byte-identical; structurally,
  `detect_strategic_command` has one production caller (pinned by census).

### Corrections to this contract, carried forward

| Claim in §CR-7-1 | Measured |
|---|---|
| "Unify `move to` with `march to`" | **Compound half built. The bare half is design, not defect.** `strategic_parser`'s header documents the split, `test_strategic_parser::test_move_is_not_strategic` pins it, the executor auto-upgrades a DISTANT tactical move (`Ney, move to Bohemia` → a MOVE_TO order, measured), and on the 1805 boot an adjacent `Ney, move to Lorraine` costs **1 AP** while `Ney, march to Lorraine` costs **2 AP**. Unifying the bare forms at the parse layer would double the price of the game's most basic order — a balance ruling, not a UX row's; pinned as the reason (`test_the_adjacent_costs_that_keep_the_rider_compound_only`). Re-open at a scenario-balance gate. |
| the six-verb head set | derived from `STRATEGIC_KEYWORDS` instead (see 1). |
| "No `clause_guards` change. No queue." | Held. |
| the headline after the fix: Ney "fortifies" | For **Ney** (aggressive) the head now reaches the objection system and he objects to sitting idle — to the FORTIFY, the order he was given: no battle, no movement, AP unchanged, the tail still reported. For cautious **Davout** the fortify executes and he keeps his ground. Both pinned. CR-7-3's objection-arm finding (the note does not re-surface after insist/trust/compromise) is visible here and stays CR-7-3's. |

### Filed, not built

- **CQ-10** (`BUG_FIXES.md` §Command-Road Queue) — **the bare comma is not a
  boundary**: `march to Swabia, attack Mack` loses the arrival; `fortify, attack
  Mack` is a FIFTH tail form on which the swallow survives. Needs the FA-50 shape
  (a verb lookahead plus the caller's `fast_parse` head gate, which refuses a
  bare name) and its own negative controls — a comma split must never fire on
  the address comma. Owner: CR-7-3's boundary re-scan.
- **The user's note, September 22: "fortify and attack is a contradiction."**
  Carried to CR-7-3: for a contradictory pair the drop note must not invite the
  tail to be re-sent as-is (attacking abandons the works); the relay copy should
  say what the head did to the tail, and the multi-turn-head mitigation in §5
  already binds.

### The §Open questions row, answered

"`move to Swabia` produces NO strategic order while `march to Swabia` does…
fold it into CR-7-1 or file it separately?" — **folded, compound-only**, with
the bare form recorded as design and the AP price on the record (above).

---

## CR-7-2 … CR-7-8 — LANDING RECORD (September 22, 2026)

**Landed on master in one session, under the user's direction** — *"continue work on multi step commands make sure costs and contradictions are smoothes out make all decisions"* — which **re-sequenced the queue** (CR-7-2..8 pulled ahead of CX-R1 / CN / CX-R2; recorded in `docs/STATUS.md` ▶ NEXT UP and `CLAUDE.md`). The HEAD measured and built against is `a40114d4` (CR-7-1's landing). Tests `tests/test_cr7_2_the_harness_can_see_it.py` · `test_cr7_3_the_tail_comes_back.py` · `test_cr7_4_the_engine_says_what_it_heard.py` · `test_cr7_5_the_third_verdict.py` · `test_cr7_6_the_arrival_order_carries_its_object.py` · `test_cr7_7_the_completer_teaches_both_forms.py` · `test_cr7_8_the_queue_is_retired.py` · golden corpus **706/706** (449 → 467 rows, both worlds) · Godot parse harness **EXIT=0** (47 scripts) after an import pass · boot smoke **0 SCRIPT ERROR** · `BASELINE_SERIES` + M1–M7 **byte-identical without re-record** · ruff clean · **one new serialized field** (`StrategicOrder.arrival_target`, CR-7-6, declared, nested) · files: `backend/ai/condition_grammar.py` (new) · `backend/commands/relay.py` (new) · `backend/ai/clause_guards.py` · `backend/ai/strategic_parser.py` · `backend/ai/llm_client.py` · `backend/ai/schemas.py` · `backend/ai/parser_eval.py` · `backend/commands/parser.py` · `backend/commands/strategic.py` · `backend/commands/strategic_executor.py` · `backend/commands/combat_executor.py` · `backend/commands/meta_executor.py` · `backend/game_logic/ledger.py` · `backend/main.py` · `backend/models/marshal.py` · `backend/models/world_state.py` · `godot-client/.../main.gd` · `api_client.gd` · `tutorial_overlay.gd` · `tools/cr7_8_order_completions.py` (new) · `tests/data/parser_golden_corpus.json`.

### Re-measured first, on the landing HEAD (all reproduced; three sharpened)

- **CR-7-3**: `Ney, march to Karaman, then Davout, fortify` → "Cannot enter Karaman", no word about Davout, `dropped_sequel` absent from the wire; `Ney, fortify then attack Mack` → objection → after `insist` / `trust` / `compromise` the note re-surfaced on **0 of 3**; `march to Swabia then attack Mack then fortify` → the third clause gone; **CQ-10**: `Ney, fortify, attack Mack` → `action=attack` (swallowed on the fifth form), `march to Swabia, attack Mack` → `attack_on_arrival=False`. **Sharpened:** `dropped_sequel` never reached the wire on the ORDINARY success arm either — the main `/command` path builds through the `_COMMAND_RESULT_SIMPLE_FIELDS` whitelist (filed and closed as CQ-12).
- **CR-7-4**: the 15-row table reproduced exactly (4 of 15 honest; the two phantoms; Relief/Godot; `for 0 turns` → `max_turns=0`; four silent drops; every one 2 AP; the echo byte-identical; the refusal blaming the enemy for `hold Rhineland when Davout arrives`).
- **CR-7-5**: `attack Mack if he is not fortified` → MUSTER + battle, AP 4→3; `should the enemy advance` → fought; `attack if, Swabia is threatened` → the province conjured (the memo's `Bavaria` example was caught one guard later by the nation-not-province refusal — the leak is real with a province name).
- **CR-7-6 (the kill gate, run FIRST)**: with Mack AND Archduke Charles staged at Swabia — aggressive Ney at 250,000 (favourable odds), `march to Swabia then attack Archduke Charles` → the strategic attack issued was **against Mack**; at unfavourable odds the interrupt named Mack; cautious Davout asked and named the region. So the arrival attack DOES fire deterministically on the player path — at the first-step seam — and the object is lost there. **Sharpened:** `_handle_move_to_arrival`'s own branch was never observed firing in the ambient world (a cannon-fire redirect intervened on every multi-turn probe; the destination-is-empty-then-enemy-arrives case is a defensive seam) — it is threaded and pinned by a direct call, and named as the belt.
- **CR-7-8**: `tools/cr7_8_order_completions.py` on the COMMANDED 40-turn arm (`commanded_full40.json`, seed `historical`, 160 commands + 40 end turns): **0 `_complete_order` / 0 `_break_order`** for player marshals — the script issues only adjacent tactical moves, so no standing march ever forms. The memo's own 1-in-14 was on three scripted marches; the committed commanded arm is lower still.
- **CR-7-7**: `_MARSHAL_VERBS` 12 rows, no `then`, no condition slot; `for 3 turns` / `until … arrives` absent from `main.gd`; the help text had no compound or conditional row.

### What was built

1. **CR-7-2** — `ALLOWED_EXPECTED_KEYS` 11 → 15; `evaluate_entry` arms for the four keys (`dropped_sequel` and `attack_on_arrival` compare the parse result's own top-level values so a row may assert `null`); an unknown key is a MISMATCH the CLI reports (the pytest hygiene gate still forbids committing one). 15 marker rows amended to assert what they always produced; 18 `cr7-*` rows added. **Recorded limit:** the entry schema has no key for a PRIOR command — CR-4 carryover stays uncoverable by corpus.
2. **CR-7-3** — `backend/commands/relay.py` (rules `SYSTEMS_REFERENCE.md` §4 Stage 2c). Five kinds; the parser's `sequel_note` says the rule and names the tail, the relay's sentence says what became of it, spliced into ONE Berthier remark. The stash `world._pending_relay` is popped at the top of every `/command` (the typed `insist` hands it on), consumed by `_respond_to_objection_sync` and `/strategic_response`, re-stashed when the answer is itself a question, cleared by `advance_turn`, and never serialized (pinned: `to_dict`, `from_dict`, `save_game` → `load_game`). The client: `_stash_relay` on the three response roads, `_fill_pending_relay` at `set_input_enabled(true)` (fills only an empty line, never over a chip in flight, never sends), `relayed` on the send when the line is the fill unchanged → `CommandRequest.relayed` → `command_history[].relayed`. **CQ-10**: `parser._comma_clause_is_a_second_order` — the first comma (left to right) whose head opens with an order verb after its address and fast-parses on its own, the tail fast-parses, the tail is not bare emphasis in the head's verb family, the whole sentence is not a guard refusal; the arrival rule and the third-clause re-scan apply. The comma joined `_ATTACK_ON_ARRIVAL_HINT_RE`, `strip_condition_text` and the promote rider.
3. **CR-7-4** — `backend/ai/condition_grammar.py` (rules Stage 2b): `strip_condition_text` / `parse_condition` / `describe_condition` / `refusal_copy` / `unread_condition_clauses` + `clause_guards.condition_marker_spans` (the `negation_marker_spans` idiom). `strategic_parser._read_condition` is the ONE read for all three branches of `detect_strategic_command` (the two early-return branches used to call the legacy unvalidated read — that is how a self-referent slipped through the first cut). The parse carries `condition_refusal` (→ a `refusal="condition"` failure with `refusal_detail`, answered by `refusal_copy` at 0 AP) and `condition_notes` (the echo's second half, rendered by `_execute_strategic_command`). The ledger's `_derive_condition_text` reads `describe_condition`. Item 5: `_check_condition` reads the order-scoped result first and gates the marshal-scoped one on `last_combat_turn >= started_turn`; both `combat_executor` seams stamp `last_combat_turn` (it had NO reader anywhere); both `StrategicOrder` constructions clear the holder's `last_combat_result`. Item 7: the "conditional" refusal carries `refusal_detail={"clause", "friendly_arrival"}` and main.py's copy splits by cause.
4. **CR-7-5** — `ConditionGuardVerdict` + `strip_condition_clauses_with_handoff(text, friendly_names, roster_names)`; the two-tuple `strip_condition_clauses` is its no-roster face (no hand-off possible through it). `_parse_with_mock` became a wrapper that stamps the hand-off ONCE onto a matched, order-bearing result (the chain has a dozen `return ParseResult(...)` sites); the chain takes the verdict on the pre-negation text too, demands a HOLD residue (`clause_is_a_hold_order`) and fails closed. The parser blanks the handed-off span same-length for the strategic layer and passes `condition_override`; `_read_condition` re-validates the name on the board (self / fallen) so a hand-off can never mint what an `until` would refuse. `ParseResult` gained `refusal_detail` and `condition_handoff`.
5. **CR-7-6** — `StrategicOrder.arrival_target`; `_extract_arrival_target` (the words after the tail verb, resolved through the one name-form source, never one of ours); `strategic.pick_contact_enemy` at `_handle_first_step_blocked`, `_handle_blocked_path`, `_handle_move_to_arrival` (a census pin forbids a surviving `enemies[0]` pick at those seams); both construction sites carry it.
6. **CR-7-7** — `_CONTINUATIONS` + `_add_continuations` (offered only once the head's own target is a real province name); the help block; the School's step II sentence. The repaired verb-table pin executes every `_MARSHAL_VERBS` line on a province the marshal is NOT in, with the state a no-target verb needs met FIRST (fortify before `unfortify`; the enemy moved off before `drill` — an honest precondition refusal is not a substitution); `garrison` is exempted BY NAME with its reason and proved red.
7. **CR-7-8** — the census (AST string literals, docstrings excluded — the ruling lives in one and names the promise it forbids; `.gd` literals) with a sensitivity arm and innocent neighbours (FA-7's own refusal PHRASE "an order for a later turn" is not a promise); the spec's §11.1; the tool; the two instrumented re-open conditions.

### `done_when`, disposed

- **CR-7-2** ✅ a row asserting `dropped_sequel: "attack Mack"` against a sentence dropping something else FAILS the CLI; the marker rows carry their values; corpus green on both worlds (706/706).
- **CR-7-3** ✅ the 14-shape battery reports the tail on **14 of 14** — success, refused head, and after each of `insist` / `trust` / `compromise` (and the interrupt answer); the relay key round-trips (`relay_command` re-addressed, e.g. `Davout, fortify`); ZERO new serialized fields; the stash pinned NOT to survive `save_game` → `load_game`. **FA-50's `test_the_address_form_is_not_split` was NOT flipped** — the note's opening phrase "One order at a time" was kept, and the muster control re-measured green in the new file rather than trusted.
- **CR-7-4** ✅ the 15-phrasing battery: **0 phantom provinces, 0 unmeetable conditions**; `for 0 turns` and `until turn 1` refused with their own reasons (and `until turn 5` READ, per the contract's "refuse it or map it" — mapped, with the echo); every accepted condition named in the confirmation AND the Ledger, drift-pinned against `describe_condition`.
- **CR-7-5** ✅ `if|when|once|as soon as <friendly marshal> arrives` = `until` on **8 of 8**; `if Mack advances fall back to Alsace` still REFUSED; the negated twin refused exactly like its twin; trailing `should` refused; no province conjured by the comma leak; **0 of the 7 pinned refusals flip** (≤3 allowed); the `parseneg-*` corpus rows green on both worlds. Kill criterion 3 never fired: no REFUSING word widened, the floor untouched.
- **CR-7-6** ✅ the kill gate passed (above): `march to Swabia then attack ArchdukeCharles` engages Charles and not `enemies[0]` when both stand there; the order round-trips; an objection answered `insist` preserves it; a legacy save with only `attack_on_arrival: true` still fights.
- **CR-7-7** ✅ every offered continuation parses to its action AND executes `success: True` on a province the marshal is not standing in; every quoted help phrasing executes; the tutor names both forms; the keystroke script is the table's own contract (a complete march offers `then attack <E>`, a complete hold offers `until <M> arrives`).
- **CR-7-8** ✅ the census finds no promise, reds when one is planted; the spec carries the ruling + two re-open conditions; STATUS carries the tracking line; PARSE-NEG §8 rule 5 resolves to CR-7; the `validation.py:195` pointer corrected (the string is inside `validate_parse_result`'s multi-marshal block — navigate by `"Multi-marshal commands coming in a future update!"`).

### Corrections to this contract, carried forward

| Claim in the contract | Measured |
|---|---|
| CR-7-3: "FA-50's `test_the_address_form_is_not_split` is flipped consciously, MESSAGE-only" | **Not flipped.** The parser's sentence keeps its opening phrase; the muster control was re-measured green rather than trusted (the secondary dissent asked for exactly that). |
| CR-7-3: the objection arm | The V2a trigger's roll made `Ney, fortify then attack Mack` object on **2 of 3** fresh boards in one process — CR-7-1's own pin was order-dependent (CQ-11). Every objection-arm pin now pins the roll at 0.5. |
| CR-7-4 item 2: "Refuse `Godot` / `relief` by name" | `Godot` refused by name; **`until relief arrives` is READ as `until_relieved`** (the words mean it) and the echo says so — a refusal would have been the less honest answer. |
| CR-7-4 item 4: "`until turn 5` — refuse it or map it" | **Mapped** to `for (N − now) turns`, floored at 1, said so in the echo; a turn behind us is refused. |
| CR-7-4 item 5: "swap the read to the order-scoped `last_combat_result`" | Swapping ALONE would have broken `until victory` on a HOLD whose battle is DEFENSIVE — the order-scoped field is written only by the order-driven combat seam. Built as order-scoped FIRST plus the marshal-scoped read gated on a turn stamp (`last_combat_turn`, which had no reader anywhere) plus the clear at issuance. |
| CR-7-5: "HAND-OFF fires for one predicate family" | Two markers more than named: a **leading** `until <friendly> arrives,` — the one `until` shape the engine's own read could never reach, because its clause ran to the sentence end and took the order with it (the memo's 15th row, "refused entirely") — rides the same hand-off, under the same HOLD gate. |
| CR-7-6: "`_handle_move_to_arrival` picks `target = enemies[0]`" | True, but that branch is the BELT; the live loss is at `_handle_first_step_blocked` (the memo's own kill-gate probe found it there). All three seams read the one helper. |
| CR-7-7: "the repaired pin shown RED against today's `garrison` row first" | Shown red — and `move to` (enemy in the destination), `unfortify` (not fortified) and `drill` (enemy adjacent) went red too, on honest PRECONDITION refusals that are not substitutions; the pin now meets each verb's precondition first, and only `garrison` is exempted. |
| CR-7-8: "measure `_complete_order` off the committed driver archive" | The archives record no order completions (the digest has no such row), so the measurement is a committed TOOL with the spy, run on the committed script: **0 / 0**. |
| The memo's "'until the enemy moves' … `hold Rhineland when Davout arrives` … the paraphrase it offers is a sentence the engine honours" | The paraphrase is now what the engine DOES: `hold Rhineland when Davout arrives` holds now, until Davout arrives, and says so. |

### Filed, not built

- **CQ-8** (naming a second marshal is inert; `parse_multiple` has zero callers) stays CR-7 backlog — the multi-marshal string is where §3 now says it is.
- **The relay fill on screen** — the `.gd` half is parse-clean and boot-clean; the eyes-on half is the next play session's (the standing visual sign-off convention).
- **A `relayed` census over a played campaign** (re-open condition 1) — needs a human playing; instrument in place.

## CR-7-9 — "THE CONDITIONS SAY WHAT THEY MEAN" — LANDING RECORD (September 22, 2026)

**Opened by the user asking how several conditions behave** (*"what if multiple conditions
arise in x turns hows it look or work"*) and then *"make fixes continue with and finish work
assure ux is good for this process and it adds to dynamism and fun etc commit and push when
done"*. The answer was measured on the landed CR-7 before a line was written
(`tools`-free probes at the real `/command`, mock mode): a condition could carry several
arms and the engine read them as **whichever comes first** — but `and` was stored exactly
like `or`, the echo listed the arms with a comma that said nothing, a `hold for 1 turn` ran
one turn longer than the Ledger's "0 turn(s) remaining" admitted, and a tail stashed behind
a question was dropped mute by the next order or the turn's end after a note that said it
would wait. Three findings, all built, filed as **CQ-14 / CQ-15 / CQ-16** and closed.

### What shipped

- **`and` means both; `or` means whichever comes first; the sentence says so.**
  `condition_grammar.read_connector` reads the word between clauses (a clause may OPEN with
  it — `until Davout arrives or the battle is won` — the second `until` being what a player
  says, not types); `and` sets `StrategicCondition.require_all` (serialized); a dangling
  connector is cut before the target (`hold Lorraine for 2 turns and until Davout arrives`
  held `Lorraine and`); both words in one order read as any-of and the echo says so; a man
  already at the holder's side is noted (`Davout is already at Rhineland with him — that arm
  is met at the turn's end`). `describe_condition` — the one sentence the echo AND the Ledger
  read — renders `… or … — whichever comes first`, `… and … — both` / `— all 3`, `(met)`,
  and names the unmet arms for the beat. Single-arm strings are byte-identical.
- **The all-of latch and the progress beat (the dynamism).** ONE per-arm reader
  (`_condition_arms`; the voiced completion labels unchanged); an all-of arm that lands is
  latched on `StrategicOrder.condition_progress` (serialized) and reported on that tick's
  own report line — *"Davout has arrived. Ney holds on — until the battle is won as well."*
  — the Ledger ticks it off, and the order ends on the last arm: *"Victory achieved! With
  that, every condition of Ney's order is met."* A timer that lands early in an all-of says
  *the agreed turns have passed*, never *abandons*; the hold handler's own expiry never fires
  an all-of alone.
- **The timer counts the turn it was given.** ONE rule, `strategic.count_order_turns`,
  read by the checker, the hold handler's expiry, the skip branch (the issuing turn's tick
  now READS the condition; the first step stays un-repeated) and the Ledger. Measured before:
  `hold for 1 turn` given on turn 1 → Ledger "0 turn(s) remaining" for the whole of turn 2
  while he held on, completing at turn 2's end; after: it ends with turn 1, the Ledger says
  "1 turn(s) remaining" on the turn it stands and never 0 on a live order, `for 2 turns`
  reads "1 turn(s) remaining" after one end turn and completes on the second, `until turn 3`
  is over as turn 3 begins. **SUPPORT is the exception and the reason is measured:** in
  `end_turn` the enemy phase runs BEFORE the strategic tick, so the turn a supporter arrives
  gave the ally no enemy phase at his side — a SUPPORT counts from the turn after arrival
  (the two `TestTimedSupportArrivalTimer` pins were right and hold; the Ledger now agrees
  with them instead of reading 0 on turn 5).
- **The tail is let go with a word.** The question note now says how long it waits
  (*"Answer, and it returns to the line; another order, or the turn's end, lets it go."*);
  a command that neither answers nor re-types the tail, and the turn boundary, mark the
  stash `world._relay_let_go` (transient) and `build_base_response` speaks it once on the
  reply that dropped it — `relay_let_go` + *"The order that waited behind the question —
  "fortify" — is let go with it. Give it again when you mean it."*; re-typing the tail is
  not a drop; the consuming routes clear it only when the SAME stash is consumed (a
  boundary's word survives an unrelated answer). **Found in passing:** the typed interrupt
  answer (`press on`) never brought the tail back — the popup route did — and now does.
- **The help teaches it** (`or / and` line; `'for 2 turns' counts the turn you give it`).

### Decisions taken under the grant

- All-of is a LATCH, not a snapshot: an arm that was true and passed stays met (Davout
  arrived and marched on; a battle won and then another lost). The alternative — all arms
  true at one tick — makes "until Davout arrives and until the battle is won" unwinnable
  the moment he leaves, which no player means.
- The HOLD/SUPPORT asymmetry follows the engine's own turn order, not symmetry for its own
  sake; the rule is one function with the reason in its docstring.
- Mixed connectors (`and … or …`) read as any-of and SAY so rather than refuse — the
  order is still a coherent one, and a refusal would cost the player the whole line.

### Measured

- Probes at the real `/command` (mock): `or` → *(until Davout arrives or until the battle
  is won — whichever comes first)*; `for 2 turns and until Davout arrives` → *— both*,
  target `Rhineland`; `for 1 turn` completes on the first end turn, `for 2 turns` reads
  1 remaining then completes; the all-of latch beat then the completion line; the let-go
  line on another order, on `end turn`, and NOT on a re-type; the already-here note.
- Pins: `tests/test_cr7_9_the_conditions_say_what_they_mean.py` (37). Flipped
  consciously: the CR-7-4 two-armed Ledger literal (`, ` → ` or … — whichever comes first`)
  and its grammar import census (`strategic.py` now reads the one sentence for the beat).
  Mutation sweep `tools/_sweep_cr7_9.json`: **27 of 27 killed, 0 INERT, first pass** (the grammar, the latch, both timers, the Ledger, the pop, the builder, the boundary, the note, the executor hand-off and both serializations).
- Corpus: three `cr7-9-*` rows (`and` / bare-`or` / `for … and until`); `parser_eval`
  709/709. M1–M7 byte-identical; `BASELINE_SERIES` control arm green without re-record (no
  AI-issued order carries a condition). Zero `.gd` — the Ledger renders the same string
  field, the reports the same shape.

### Filed, not built

- **The typed interrupt route's relay consumption has no end-to-end pin** (a deterministic
  bad-odds interrupt is a two-marshal staging the popup tests already own); the clearing
  is pinned directly on `_attach_answered_relay`.
- **Three or more arms** render `— all 3` and evaluate correctly, but no golden row types
  one; the grammar's clause spans are what bound it.
