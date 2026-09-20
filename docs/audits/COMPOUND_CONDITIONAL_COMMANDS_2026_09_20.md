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