# VERDICT: CX-CLAIM-1 — **REFUTED**

**The two measurements are not the wrong way round. The memo's `45 / 692` IS the
real predicate, reached the way the shipped game reaches it; the claim's `50` is
the same predicate fed a truncated input.** The claim reproduces its own number
and misdiagnoses what it is.

Read-only, at master `727cf88a` (clean) plus a `git archive f7008582` control.
`LLM_MODE=mock`, no key, no network, provider stubbed at the call. Nothing under
`backend/`, `godot-client/`, `tests/`, `docs/` or `tools/` touched; no
git-mutating command run.

Probes I ran (mine, not the ones I was handed), under
`…/scratchpad/cx_review/probes/`:

| probe | what it does |
|---|---|
| `v1_escalation_two_arms.py` | both arms over the whole corpus at HEAD, diffed by row id |
| `v2_mechanism.py` | *why* they differ — flips `VERB_TYPO_PASS_ACTIVE`, walks the provider-call stacks |
| `v3_precx_control.py` | the same two arms on the pre-CX tree, at the corpus the memo names |
| `v4_rescue_and_trap.py` | do the five "dropped" rows actually parse correctly? + the claim's own recorded trap |
| `v5_fix_consequence.py` | would the suggested fix make the §4 table incommensurable? |

---

## 1. WHAT I MEASURED

Both arms run the **same** production function `LLMClient._should_fallback_to_llm`,
armed (`provider_name="anthropic"`, fake key) so its two mode/key guards pass and
its real conditions evaluate. Proof they passed: the reason histogram contains no
`mock` and no `nokey` bucket — only `confident` / `refusal` / `ESCALATED`.

* **ARM P** — the memo's stated method and the recon's: the production seam
  `CommandParser.parse(utterance, game_state, world=world)`.
* **ARM D** — the claim's method: the real predicate called **directly** on a
  `_parse_with_mock(...)` result.

```
HEAD 727cf88a (449 entries -> 694 evaluations)
  ARM P  45 / 694 = 6.48%    confident 615 · refusal 34
  ARM D  50 / 694 = 7.20%    confident 610 · refusal 34

pre-CX f7008582 (447 entries -> 692 evaluations)   <- the memo's own corpus
  ARM P  45 / 692 = 6.50%   <-- the published figure, to the digit
  ARM D  50 / 692 = 7.23%
```

**The memo's `45 / 692 = 6.5%` reproduces exactly, on the tree and the corpus it
names.** The claim's `50` reproduces too — as a different instrument's answer.

---

## 2. WHY THEY DIFFER — and it is not what the claim says

The difference is the **input**, not the predicate. `CommandParser.parse`
(`parser.py:1594`) applies `repair_leading_verb_typo` (FA-80) **before** anything
sees the sentence; ARM D skips that stage by construction.

Proven by experiment (`v2`), not by argument — flip the shipped lever:

```
ARM P, VERB_TYPO_PASS_ACTIVE = True    45 / 694
ARM P, VERB_TYPO_PASS_ACTIVE = False   49 / 694
newly escalating, exactly:  fa80-attak · fa80-mvoe · fa80-scuot · r7-hodl
still rescued with the lever down:     emperor-address
```

### The claim's causal theory is false, and its list is wrong in both directions

> *"45 = 50 − 5, and the five are exactly the escalating corpus rows that declare
> no `expected.success`"*

Measured, the two sets are **different sets that happen to be the same size** and
share four members:

| row | escalates ARM D | escalates ARM P | has `expected.success` |
|---|---|---|---|
| `fa80-attak-reads-as-attack` | ✅ | ❌ | no |
| `fa80-mvoe-reads-as-move` | ✅ | ❌ | no |
| `fa80-scuot-reads-as-scout` | ✅ | ❌ | no |
| `r7-hodl-lorraine-is-a-standing-hold` | ✅ | ❌ | no |
| **`emperor-address`** | ✅ | ❌ | **YES — `success: True`** |
| **`soutl-attack-mack`** | ✅ | **✅** | no |

`soutl-attack-mack` — which the claim names as one of its five — **escalates in
BOTH arms** (conf 0.55, action `attack`) and is not in the difference at all. The
fifth member of the real difference is `emperor-address`, which carries
`expected.success: True` and so falsifies the stated rule.

The claim's own CX-CLAIM-2, two sections later, lists `emperor-address` as an
escalating row *inside the memo's 29* — i.e. the report contradicts itself about
which five these are.

### Nothing is "silently dropped"

Both arms evaluate the full 692 / 694. The denominators are identical. ARM P
counts those five as **not escalating** because production resolves them before
the gate, not because they were excluded from a run.

---

## 3. THE CLAIM'S STRONGEST SENTENCE IS BACKWARDS

> *"four of which are the rescue class … The exclusion is not neutral: it removes
> precisely the evidence that argues **for** escalation."*

Driven through the production seam on the 1805 board (`v4`), all four parse to the
**correct order at confidence 0.95**, each carrying an explicit receipt:

```
'Ney, attak Mack'       -> Ney / attack / Mack     conf 0.95  "(Berthier read 'attak' as 'attack'.)"
'Ney, mvoe to Lorraine' -> Ney / move / Lorraine   conf 0.95  "(Berthier read 'mvoe' as 'move'.)"
'Ney, scuot Swabia'     -> Ney / scout / Swabia    conf 0.95  "(Berthier read 'scuot' as 'scout'.)"
'Davout, hodl Lorraine' -> Davout / hold / HOLD    conf 0.95  "(Berthier read 'hodl' as 'hold'.)"
'Emperor, attack Mack'  -> Napoleon / attack / Mack conf 0.95
```

Every one meets its corpus contract **without a model**. They are evidence that the
**deterministic** chain rescues that class — which is the memo's ruling ("the
deterministic chain carries twelve times more measured value than the model"), not
evidence against it. Folding them into the escalation numerator would credit the
model with four sentences it never sees and never needed to see.

---

## 4. SEVERITY, REACHABILITY, ATTRIBUTION

* **Severity: the filed P2 does not survive.** The central assertion is wrong.
  What is left is **P4 wording**: the memo's ⚠ note calls the 50 *"a hand-written
  re-implementation of the same predicate"*; the exact diagnosis is *the same
  predicate on a truncated input*. The note's operative clause — *"the
  real-predicate figure is the one cited"* — is **correct**, and its disclosure
  discipline (record, don't average) is what let me find the real cause in twenty
  minutes.
* **Player-reachable: NO.** A documentation figure, published in exactly two
  files (`COMMAND_EXPERIENCE_SPEC.md:512`, the memo `:249`), pinned by no test
  (`grep` over `tests/*.py` for `692` / `45 / 692` / `6.5%`: zero hits) and read
  by no code. Nothing about it reaches the client.
* **Shipped by row CX: not as a defect, because there is no defect.** The figure
  is a row-CX artifact (`704df816`), but the pre-CX control reproduces `45 / 692`
  exactly and the number moves with none of the row's levers.

---

## 5. WOULD THE SUGGESTED FIX SHIP A REGRESSION?

> *"cite 50 / 692 = 7.2%, state the row filter if one is wanted, and retract the
> ⚠ note — the re-implementation and the real predicate agreed."*

Docs-only, so **no pin would red**. It would nonetheless ship a worse document:

1. **It publishes a rate the shipped game does not have** — inflated by four
   sentences production repairs at confidence 0.95 before escalation is
   considered.
2. **"State the row filter" describes a filter that does not exist.** There is no
   filter; the denominator is whole in both arms. A reader told to look for one
   would find nothing.
3. **It retracts a true disclosure** and replaces it with a false one ("the
   re-implementation and the real predicate agreed" — they disagree, for a
   *reason*, and the reason is a shipped production stage worth naming).
4. The claim's proposed sentence is the exact opposite of what the row should
   say. The honest amendment is one clause: *the higher figure bypasses the FA-80
   verb-typo repair, which fixes four corpus rows deterministically before the
   gate — so 45 is the shipped behaviour.*

**Checked, because it would have been the stronger objection:** on the real
playtest population the two arms **agree exactly** — `51 / 1,456 = 3.50%` either
way (`v5`). So the corpus row is the *only* place the instruments diverge, and
they diverge solely on rows the corpus authored to pin a typo repair. The §4
table is not incommensurable; the claim's fix would be the one thing in it
measured differently from everything around it.

---

## 6. WHAT SURVIVES — credit, and one residue the claim did not file

* **Credit:** the claim's recorded `game_state`-shape trap is **real in
  direction**. Measured: `{"world": w}` in place of `get_llm_game_state()` drives
  cases at `UNRESOLVED_ADDRESS_CONFIDENCE = 0.55` from 6 → 24 and escalation from
  `45 / 694 = 6.48%` to `68 / 694 = 9.80%` (1805-only: 6.1% → 12.0%). **The
  stated 35% did not reproduce on either construction.** Direction right,
  magnitude ~3.5× over.
* **Residue, different from what was filed (P4, INFO):** `p1_escalation_rate.py`
  — the instrument behind `45 / 692` — **is not committed** (`git ls-files`: no
  hit). The figure is reproducible, as I have just shown, but a reader cannot
  re-run it from the tree. That is the IQ-8 table rule the memo cites in its own
  header, and it is the class CX-CLAIM-11 filed about the predictor. Cheapest
  discharge: the two-arm probe is ~80 lines and its ARM P output *is* the cited
  number.
* **Out of scope but true:** at HEAD the corpus is 449 entries → 694 evaluations,
  so `692` / `447` are stale by CX-2's own two rows. The published **rate** is
  unaffected (6.50% vs 6.48%, both "6.5%"). That is CX-CLAIM-8's subject.

---

## 7. THE ONE-LINE RECOMMENDATION

Leave `45 / 692 = 6.5%` standing. Replace the ⚠ note's *"a hand-written
re-implementation of the same predicate"* with *"the same predicate on a bare
`_parse_with_mock` result, which bypasses the FA-80 verb-typo repair and so counts
four typo rows the shipped seam fixes at confidence 0.95"*, and fix the denominator
to `449 entries × both worlds = 694` under CX-CLAIM-8.
