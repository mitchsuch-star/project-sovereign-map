# Parser & Autofill — assurance pass

> **Status: INVESTIGATION + RECOMMENDATION. Nothing here is built, gated or
> approved.** Produced September 20, 2026 by a 53-agent read-only fleet
> (18 recon -> 18 adversarial refuters -> 7 competing plans -> 6 judges ->
> 4 syntheses), driving the real `POST /command` and the real
> `CommandParser.parse` against an unmodified `europe_1805.json` boot world at
> HEAD `15c498cb`, `LLM_MODE=mock`, seed `historical`. No repo file was modified
> during the investigation.
>
> **User ask: "assure the parser and autofill are in good form and sensical."**
>
> Every claim below carries a confidence marker. **measured** = the agent ran it
> and is reporting output. **read** = the code path was read end to end.
> **inferred** = judgement. Claims that could not be reproduced are recorded as
> such rather than deleted. Line numbers were current at measurement time; this
> repo's own records say ~80% of filed line numbers go stale, so **navigate by
> symbol**.

---

## Verdict in one paragraph

The parser is in good form for the sentences it was built for — 688/688 corpus, 1,850 tests, and refusals that are genuinely excellent — but it has one live, silent, unguarded seam: a compound order whose first clause is not stand-still vocabulary discards that clause and fights instead, at 0.95 confidence, with no warning. The autofill is correctly built and correctly pinned, but the pin stops at the parser: 280/280 of the lines it draws parse, and 59.3% of them are refused by the executor.


## Key numbers (all measured unless noted)

- Golden corpus: 688/688 passed (mock), 6/6 passed (keyless replay, 0 drift)
- Parser-family test suite: 1,850 passed across 20 files; predictor pins 32 passed
- Completer lines at the PARSER: 280/280, zero action mismatches — the founding rule holds
- Completer lines at the EXECUTOR: 80 execute cleanly (28.6%), 34 stage a question (12.1%), 166 refused (59.3%)
- Per-verb legality of the first five offers: garrison 0/40 · unfortify 0/8 · scout 6/40 · move to 7/40 · march to 8/40 · attack 12/32 · support 22/40 · hold 8/8
- Compound-order swallow: 10 of 10 non-stand-still first clauses discarded and a real battle fought, 0 warned; control 4 of 4 correct
- Every swallowed sentence parses at confidence 0.95 against a 0.7 escalation gate — no LLM is ever consulted
- Unknown addressee: 4 of 8 forms take irreversible action (gold 800->400 keel, gold 800->59 recruit, fleet posture, Austria subjugated)
- Multi-marshal control: 4 sentences, byte-identical muster heads — naming a second marshal is inert; parse_multiple has 0 production callers
- Completer coverage: 14 of 56 VALID_ACTIONS; 17 of 26 first letters produce nothing
- Open defect rows routed to 'CR-6 proper': 47 — a label with no spec section, no gate and no build contract
- parser_eval.ALLOWED_EXPECTED_KEYS: 11 keys, none able to express a compound outcome


## Open questions that need your ruling

- Compound/conditional orders are owned by CR-7 in the spec, not CR-6 — but 47 rows are routed to 'CR-6 proper', which has no gate or build contract. Do you want CR-6 proper scoped as a real row, or should the two P1 families be pulled out and built ahead of it?
- The completer target-pool fix (item 4) is client-only and cheap — every input it needs is already on the wire. Do you want it taken as a standalone slice ahead of the parser work, since it is the surface a new player meets first?
- Item 8 (a two-command corpus harness) is a prerequisite for pinning items 1, 2 and 7 honestly. Are you willing to spend a slice on the instrument before the fixes, given this repo's record of fixes shipping unpinned?


---

# Assurance: the parser and the autofill

Everything below was **measured by me at HEAD `15c498cb`**, driving `POST /command` in-process with a fresh 1805 world per sentence, or running the committed gates. Where I could not reproduce a relayed claim I say so. Confidence is marked per finding.

---

## 1. Verdict

**(a) The parser — GOOD FORM, with one unguarded seam.**
Every gate it owns is green, its name resolution is strong, and its refusals are the best-engineered part of the command layer. It has exactly one defect family that is both live and silent: **compound and conditional clause handling**. Inside that family it does not refuse and does not warn — it discards what the player said, executes something else, and charges for it.

**(b) The autofill (command-line completer) — SENSICAL IN CONSTRUCTION, NOT YET IN PLAY.**
It is built on a real rule (*"the game must not offer a sentence it cannot read"*) and that rule is enforced by a Python pin over the `.gd` table — unusually good discipline. But the rule was drawn one layer too shallow. Every line it draws **parses**; a majority are **refused by the game**. It is not wrong, it is *unaware of the board*.

---

## 2. The measured evidence

### The committed gates — all green, all reproduced

| Gate | Result | Method |
|---|---|---|
| Golden corpus, mock | **688/688 passed** (4 `live_only` skipped) | `LLM_MODE=mock python -m backend.ai.parser_eval` |
| Golden corpus, keyless replay | **6/6 passed**, 6 live calls replayed from 6 cassettes, **drifted: none** | `parser_eval --replay` |
| Parser-family test suite | **1,850 passed** in 59.9s, across 20 files | `pytest` over the CR-0..CR-5b, CX-1/2/3/7, parse-negation, strategic-parser, fuzzy, IQ-9 and sweep-5 files |
| Predictor pins | **32 passed** in 15.8s | `test_cx3_the_predictor.py` + `test_cx7_predictor_driven.py` |
| Completer lines at the **parser** | **280/280, zero action mismatches** | my census: 8 marshals × 12 verbs × the first `MAX_SUGGESTIONS` targets, `parser.parse(..., world=world)` |

That last row is the important one and it is to the completer's credit: **the founding rule genuinely holds at the parser.** Nothing it offers is unreadable.

### My own adversarial battery — where it breaks

**Compound orders (16 sentences, fresh world each, state delta not message text):**

```
sentence                                  fought  1st-clause-done  warned  AP     deltas
Ney, fortify then attack Mack             True    False            False   4->3   Rhineland->Swabia  24000->21935
Ney, scout Swabia then attack Mack        True    -                False   4->3   Rhineland->Swabia  24000->22340
Ney, drill your men then attack Mack      True    -                False   4->3   Rhineland->Swabia  24000->21361
Ney, retreat then attack Mack             True    -                False   4->3   Rhineland->Swabia  24000->21939
Ney, form square then attack Mack         True    -                False   4->3   Rhineland->Swabia  24000->21951
Ney, unfortify then attack Mack           True    -                False   4->3   Rhineland->Swabia  24000->21573
Ney, defend then attack Mack              True    -                False   4->3   Rhineland->Swabia  24000->21906
Ney, scout Swabia, then attack Mack       True    -                False   4->3   Rhineland->Swabia  24000->20805
Ney, scout Swabia and then attack Mack    True    -                False   4->3   Rhineland->Swabia  24000->21349
Ney, fortify; attack Mack                 True    False            False   4->3   Rhineland->Swabia  24000->22362
--- CONTROL: stand-still vocabulary (what FA-7 fixed) ---
Ney, wait then attack Mack                False   -                TRUE    4->4   (no move, no battle)
Ney, hold your position then attack Mack  False   -                TRUE    4->2   (no move, no battle)
Ney, stay put then attack Mack            False   -                TRUE    4->4   (no move, no battle)
Ney, rest your men then attack Mack       False   -                TRUE    4->4   (no move, no battle)
```

**10 of 10 swallowed; 4 of 4 control correct.** For `fortify` I asserted the real flag: `marshal.fortified` is `False` after the command. A real battle is fought, ~2,000 men die, 1 AP is spent, and `"One order at a time"` appears nowhere. *(measured)*

Also measured in the same run: **`march` and `move` diverge on the identical sentence.** `Ney, march to Swabia then attack Mack` correctly defers the attack to arrival (no battle). `Ney, move to Swabia then attack Mack` **fights immediately.** *(measured)*

**Conditional orders (12 sentences):**

| sentence | outcome | verdict |
|---|---|---|
| `attack Mack if he is fortified` | refused, 0 AP | correct |
| `attack Mack **if he is not** fortified` | **muster + battle, 1 AP** | negation defeats the guard |
| `attack Mack when Davout arrives` | refused, 0 AP | correct |
| `attack Mack **should** the enemy advance` (trailing) | **battle, 1 AP** | `should` only guarded clause-initially |
| `Ney, should the enemy advance, attack Mack` (leading) | refused | correct |
| `attack Mack unless he is fortified` | refused | correct |
| `hold Rhineland until Davout arrives` | condition bound `{until_marshal_arrives: Davout}` | correct |
| `hold Rhineland for 3 turns` | condition bound `{max_turns: 3}` | correct |
| `hold Rhineland **until turn 5**` | **condition `None`, 2 AP charged**, message still says "holding position" | silently dropped |
| `hold Rhineland until **godot** arrives` | condition `{until_marshal_arrives: 'Godot'}` | **unmeetable order, 2 AP** |
| `hold Rhineland **for 0 turns**` | condition `{max_turns: 0}`, 2 AP | paid no-op |

*(measured)* The substrate is sound — five condition families bind and evaluate. The **parser surface** over it is where the holes are.

**The decisive fact for "why didn't the LLM catch it":** every one of those sentences parses at **confidence 0.95** against `llm_client.LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`. **No model is ever consulted for any of them.** *(measured)*

### The completer, scored against the executor

I reproduced `main.gd`'s own offer generation from the payload the client actually receives (`world.get_filtered_game_state_summary()`, not `parser_eval.build_llm_game_state`) and drove every line:

```
TOTAL drawn lines scored : 280
  executed cleanly       : 80   (28.6%)
  staged a question      : 34   (12.1%)
  refused                : 166  (59.3%)

verb         n     executed   staged   refused
attack       32    12         5        15
march to     40    8          0        32
move to      40    7          1        32
scout        40    6          0        34
fortify       8    5          3        0
unfortify     8    0          0        8
drill         8    0          3        5
defend        8    5          3        0
hold          8    8          0        0
retreat       8    7          1        0
support      40    22         18       0
garrison     40    0          0        40
```

*(measured. My denominator is 280 — 8 marshals × 12 verbs × up to 5 targets. A relayed figure of 153/232 = 65.9% circulates; the denominators differ, the shape does not.)*

**The mechanism, confirmed at the symbol:** `main.gd:_region_names` (7060) and `_visible_enemy_names` (7047) each take *every* key in the payload and end in `out.sort()`. So the first five provinces offered to a marshal standing at Rhineland are:

```
['Albania', 'Alentejo', 'Algiers', 'Amsterdam', 'Anatolia']
```

Alphabetical order, not proximity. `hold`, `retreat`, `support`, `fortify` and `defend` — the verbs with **no target slot or a friendly slot** — are near-perfect. Every bad number is a target pool sorted by the alphabet. *(measured + read)*

---

## 3. Where they are not sensical — ranked

### P1 — A compound order silently executes something the player did not say
`backend/commands/parser.py:_ATTACK_ON_ARRIVAL_TAIL_RE` (:72) suppresses the sequel split for any tail beginning `attack`/`engage`/`assault`; the exemption at :88 only readmits `llm_client.py:186 STAND_STILL_ALTERNATION` — `wait|hold|halt|stand fast|stand ground|stay put|stay here|stay where you are|remain|rest your men`. **`scout`, `fortify`, `drill`, `defend`, `retreat`, `form square`, `unfortify` are absent.** This is FA-7's own defect, one verb family over: FA-7 was fixed by *enumerating a vocabulary* rather than by asking whether the first clause carries an order, so every verb outside the list is still live. Cost per firing: 1 AP, a marched corps, ~2,000 casualties, no disclosure. *(measured)*

### P1 — A negated or trailing condition executes unconditionally
`clause_guards.strip_condition_clauses` applies a two-word floor (:473) to text that `strip_negated_clauses` has **already blanked** (`llm_client.py:1539-1540`), so `if he is not fortified` falls under the floor and executes while `if he is fortified` correctly refuses. Separately, `_SHOULD_INVERSION_RE` (:427) anchors to clause-initial `should`, so a **trailing** `should …` is unguarded with or without a negation. *(measured)*

### P1 — An unknown addressee spends gold and subjugates a great power
Driven by state delta, not `success`:

```
Zorglub blockade                  -> fleet posture CHANGED
Zorglub build ships               -> gold 800 -> 400, a keel laid
Zorglub recruit in Rhineland      -> gold 800 -> 59, Davout recruits 3,000
Zorglub vassalize Austria         -> Austria SUBJUGATED, marshals assimilated
--- correct ---
Zorglub fortify                   -> "Which marshal shall carry out this order, Sire?"
Zorglub attack Mack               -> refused
Zorglub, build ships  (COMMA)     -> refused
```

**The comma is the discriminator**: `Zorglub, build ships` refuses, `Zorglub build ships` spends 400 gold. This is row **L2-1** (filed as *"27 of 40 routed verbs still missing"*) plus **CX-X3** — but the filed rows describe it as a naval posture toggle, and the gold-spending members are the reason it outranks the rest of the backlog. *(measured)*

### P2 — The completer's `garrison` slot can never succeed, and its `unfortify` slot can never succeed
`garrison` is **0/40** on the boot board and `unfortify` **0/8**. Two separate causes:
- `garrison`: `economy_executor.garrison_refusal_probe` counts `garrison_strength > 0` over the nation's regions, and France boots holding **`['Paris', 'Normandy', 'Flanders']` = exactly the cap of 3**. Every French marshal is refused regardless of province. *(measured)*
- `unfortify`: nobody is fortified at boot.

⚠ **Correction to a relayed claim.** The report that `Ney, garrison Bohemia` returns `success: True`, garrisons Rhineland and spends 3,000 men **does not reproduce** — the cap refuses first, at 0 AP, with strength unchanged. The *underlying* substitution is real (`_execute_garrison` at :1567 reads `marshal.location` and never `command["region"]`), but it is **latent, not live**. Fix the cap without fixing the slot and you ship the substitution. *(measured)*

### P2 — The `attack` slot offers courts France is not at war with, including its ally

```
ArchdukeJohn   Austria    WAR        at_war=True
Brunswick      Prussia    PEACE      at_war=False
Deroy          Bavaria    ALLIANCE   at_war=False   <-- France's own ally
Mack           Austria    WAR        at_war=True
```

`_visible_enemy_names` filters on nationality, never on war. Half the offered targets are non-belligerents. And the response *already carries* what the filter needs — `active_wars.wars[].opponent` is on every response. *(measured)*

### P2 — Naming a second marshal is causally inert, and the game tells you to type what you just typed
Control experiment, four sentences, fresh world each:

```
Ney, attack Mack               MUSTER - Ney (24,000; 78,676 if all march, up to 96,789 ...)
Ney and Davout, attack Mack    MUSTER - Ney (24,000; 78,676 if all march, up to 96,789 ...)
Ney and Soult, attack Mack     MUSTER - Ney (24,000; 78,676 if all march, up to 96,789 ...)
Ney and Bernadotte, attack ... MUSTER - Ney (24,000; 78,676 if all march, up to 96,789 ...)
```

**Byte-identical.** The second name changes nothing. `parse_multiple` (`parser.py:2204`) — which handles this correctly — has **zero production callers**. And `Ney attack Mack, Davout scout Swabia` drops the second clause with `warned=False`, while the `;` form of the same sentence warns. *(measured)*

⚠ Relayed as *"silently drops Davout"*; that framing is wrong — Davout musters anyway as part of the pool. The real defect is that naming him is **inert**.

### P3 — The pins cannot see any of this, by construction
- `test_cx3_the_predictor.py:test_every_marshal_verb_parses_to_the_action_it_claims` samples **one marshal**, and `region = world.get_marshal(marshal).location` — so the `garrison` sample is `Ney, garrison Rhineland`, the exact input under which the substitution is invisible. It runs at the **parser**. *(read)*
- The sibling executor census asserts on a six-string refusal list (`"not found"`, `"cannot parse"`, …), **never on `success`** — so *"We already maintain 3 garrisons"* and *"We do not control X"* pass it green. It also calls `_execute(phrase)` twice per phrase (:288-289), each building a fresh world and TestClient. *(read)*
- `parser_eval.ALLOWED_EXPECTED_KEYS` holds 11 keys and **none can express a compound outcome** — no `dropped_sequel`, no `warning`, no `strategic_condition`. The corpus is structurally blind to both P1 families and will stay green through the fix. *(read)*

### P3 — Coverage and discoverability
- **14 of 56 `VALID_ACTIONS` are reachable from the completer.** Categorically absent: every economy, diplomacy, naval, vassal, recruitment and reward verb, plus `cancel`. *(measured)*
- **17 of 26 first letters produce nothing.** Offers exist only for the 6 distinct marshal initials `{B,D,L,M,N,S}` and the 4 bare-command initials `{s,e,h,w}`; empty input returns `[]`. Its only hint is drawn *inside the suggestion row*, so it is visible only once already triggered, and the help body mentions it zero times. *(measured by construction from `_build_completions` at 7077)*
- Addressing is exact-equality after `find(",")`, so `Marshal Ney, …` completes nothing.
- **Sibling surface, same rule, worse:** `region_panel.gd` has **0** `humanize_entity_name` calls and line 557 puts the raw roster key in the visible label — `"Attack ArchdukeCharles"`. R7 forbids that. *(measured)*

### The open backlog
**47 routings to "CR-6 proper"** in `docs/BUG_FIXES.md` *(measured: `grep -o "CR-6 proper" | wc -l`)*. CR-6 proper has **no spec section, no gate and no build contract** — `COMMAND_ROBUSTNESS_SPEC.md` §2 row 35 shows the *feature* (Conversational Objection Negotiation) is still behind a **USER DESIGN GATE**, while §2 row 36 shows **CR-7**, not CR-6, owns conditional/compound orders. The two P1 families above therefore have no owner who is scheduled. Also: the spec's own pointer `validation.py:195` is stale twice (:36 and :43) — the multi-marshal string is at **`validation.py:413`**. *(measured)*

---

## 4. What is genuinely good — do not disturb it

- **Refusals.** Specific, self-correcting, fog-honest, in Berthier's voice. When the parser says no, it says no well.
- **The parser-level contract.** 280/280 of the completer's lines resolve to the action the table claims. That is real.
- **The guard architecture.** Index-preserving blanking, subtractive guards that never *pick* an action, and a terminal refusal rule — this is why PARSE-NEG stayed fixed.
- **Fog.** Completer history is session-only and cleared on world swap; the board source is the already-filtered payload. No leak found.
- **The conditional substrate.** `StrategicCondition` is not dead code — five families bind, serialize and evaluate per turn.
- **The keyless gate.** IQ-9's replay arm works: 6 cassettes, no drift, no API key needed.

---

## 5. Remediation — prioritised

| # | Item | file:symbol | done_when |
|---|---|---|---|
| **1** | Compound order must never silently discard a clause | `parser.py:_split_sequential_orders` (:136) + `_ATTACK_ON_ARRIVAL_TAIL_RE` (:72); vocabulary at `llm_client.py:186 STAND_STILL_ALTERNATION` | The 10 sentences in §2 either split-and-warn or refuse. Pin asserts `marshal.fortified is True` / no `battle_report`, not message text. Note: `STAND_STILL_ALTERNATION` has exactly **one** consumer (`parser.py:89`) — its docstring claiming it is shared with the mock wait arm is stale, so extending it is lower-risk than it looks. |
| **2** | Negated + trailing conditions refuse like their twins | `clause_guards.strip_condition_clauses` word floor (:471-474); `_SHOULD_INVERSION_RE` (:427); `_REFUSING_CONDITION_WORDS` (:396); call order `llm_client.py:1539-1540` | `if he is not fortified` and `attack Mack should the enemy advance` refuse at 0 AP. Re-asking the floor against pre-negation text flips **0 of 449** corpus rows — measure that before building. |
| **3** | Unknown addressee never moves gold or state | `executor.py` addressee gate + `clause_guards._ORDER_VERB_RE` (:886) — **derive** from the routing table, don't widen a third time | All 8 `Zorglub` forms ask or refuse; state-delta snapshot (gold, fleets, vassals, marshals, region controllers) is empty for every one. |
| **4** | Order target pools by proximity, filter by war | `main.gd:_region_names` (7060) `out.sort()`; `_visible_enemy_names` (7047) | First five region offers are adjacent-or-reachable; `attack` offers no court at PEACE/ALLIANCE. `active_wars.wars[].opponent` and `/map_topology.regions[r].adjacent` are already on the wire — **client-only, no backend work.** Re-run the §2 scorer: executed% rises from 28.6%. |
| **5** | Make the table pin able to fail | `test_cx3_the_predictor.py:test_every_marshal_verb_parses_to_the_action_it_claims` and `..._survives_the_EXECUTOR` (:276) | Census runs at the executor, asserts `success`, uses a province the marshal is **not** standing in, and covers all 8 marshals. Mutation-check it: deleting the `garrison` region slot must red it. |
| **6** | `garrison` / `unfortify` stop being offered when they cannot succeed | `main.gd:_MARSHAL_VERBS` (6968); `economy_executor._execute_garrison` (:1567) — read `command["region"]` or drop the slot | `garrison` 0/40 and `unfortify` 0/8 become either legal or not offered. **Fix the slot at the same time as the cap**, or the latent substitution goes live. |
| **7** | Unhonourable conditions refuse instead of vanishing | `strategic_parser._parse_condition` (:804-837) **and** `_strip_conditions` (:579-587) — both, or the phantom province survives | `until turn 5`, `till X arrives`, `until <unknown> arrives`, `for 0 turns` each refuse with a reason. Widening `_parse_condition` alone was measured to leave the phantom standing on 5 of 6 cases. |
| **8** | Give the corpus a way to pin this | `parser_eval.ALLOWED_EXPECTED_KEYS` (:70) + a two-command harness | The corpus can assert `dropped_sequel`, `warning`, `strategic_condition`, and a prior command. **Prerequisite for 1, 2 and 7** — otherwise the fixes ship unpinned. Note the CLI silently ignores unknown expected keys, so CLI-green is not evidence. |
| **9** | Raw roster keys out of chip labels | `region_panel.gd:557` | `humanize_entity_name` count > 0; no chip reads `Attack ArchdukeCharles`. |
| **10** | Coverage + discoverability | `main.gd:_MARSHAL_VERBS` / `_BARE_COMMANDS` (6983); `meta_executor._execute_help` | A first-run hint exists outside the suggestion row; economy/diplomacy/naval/cancel verbs reachable. Lowest priority — this is a gap, not a defect. |

**Sequencing note:** items 1, 2 and 7 are the same repair philosophy — *stop enumerating vocabularies, start asking whether the clause carries an order*. The repo has already paid for this lesson twice (FA-7, and the IQ-7 review round's closed grammar). Item 8 should land first or the pins will go green about live defects, which is this codebase's single most-recorded failure mode.

---

## 6. Claims I could not reproduce

Recorded so they are not re-filed:

1. **`Ney, garrison Bohemia` succeeding and garrisoning Rhineland for 3,000 men** — does not reproduce. Refused at 0 AP by the garrison cap (Paris/Normandy/Flanders = 3 of 3). The substitution is real in code but unreachable at boot.
2. **`Zorglub buy substitutes for Ney` charging 4,012 gold** — does not reproduce. Refused on **price** (4,012g against a boot treasury of 800), not on the addressee. The addressee hole is real; this particular member is masked by affordability.
3. **`Ney and Davout, attack Mack` "silently dropping Davout"** — the observable is wrong. Davout musters regardless; the defect is that naming him is **causally inert** (four byte-identical muster heads).
4. **Completer refusal rate "153 of 232 = 65.9%"** — my measurement on the client's real payload is **166 of 280 = 59.3% refused, 28.6% executing cleanly, 12.1% staging a question.** Same conclusion, different denominator; `success: true` is not a refusal signal on this endpoint, so any figure read off that flag alone should be re-measured.