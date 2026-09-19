# REFUTATION — `cx_recon/parser_road.md` (topic: parser)

Default verdict REFUTED; each row had to earn its survival. Every claim below
is a `file:line` I read myself or the output of a probe under `probes/rf*.py`
that I actually ran. Read-only throughout.

---

## 0. Tree provenance — read this first

**The census's line numbers are accurate at HEAD.** I re-derived nine anchors
against `git show HEAD:backend/ai/llm_client.py`: `_addressed_marshal` 1294 ✅,
`elif "hold" in command_lower` 1890 ✅, `_proposal_keywords` 1543 ✅,
`_diplomat_names` 1476 (census 1478, the branch head) ✅, `_war_keywords` 1503,
`"train"` 2055 ✅, `"scou"` 1950 (census 1948, the `elif` head) ✅. Given this
repo's own audit history ("~80% of rows carry a stale line number"), that is
worth stating in the census's favour. `probes/rf13_provenance.py`.

**But two files on the parser road were being edited by sibling agents while we
both worked.** `backend/ai/clause_guards.py` was already modified when the
census opened; **`backend/ai/llm_client.py` became modified (+31 lines) during
MY session** — it was clean at my start and `git status` now shows
`M backend/ai/llm_client.py` plus an untracked
`tests/test_cx1_a_question_never_orders.py`. Worktree line numbers are now
+26/+27 against HEAD.

I did **not** treat the census's citations as stale on that basis, and I
verified my own results are unaffected: all 37 utterances I measured are
`is_question() == False` under **both** the HEAD and worktree versions of
`clause_guards.py`, and all three changed hunks in `llm_client.py`
(`@@ -535`, `@@ -1353`, `@@ -1601`) sit outside the action chain
(HEAD 1782–2222). **My measurements are HEAD-valid by construction**
(`probes/rf13_provenance.py`). The census's own provenance note is nonetheless
wrong — see MISSED:4.

**The method difference that drives most of this report:** the census measured
**parse dictionaries**. I measured the **real `POST /command` endpoint** with
the world swapped to the 1805 board, a fresh world per utterance, recording
AP, marshal locations, stances and the player-visible message. A parse dict
says what the chain decided; the endpoint says what the player gets, and for
nine of the thirteen rows those are not the same thing.

---

## 1. Verdicts

| id | verdict | severity: filed → measured |
|---|---|---|
| CX-P1 white peace | **REFUTED** | P2 → P4 (design, pinned) |
| CX-P2 coverage gate | **NARROWED** | P2 → P3 |
| CX-P3 diplomatic pre-routes | **NARROWED** | P2 → P4 |
| CX-P4 contiguity | **SURVIVES** | P3 ✅ |
| CX-P5 bare `hold` | **SURVIVES — understated** | P3 → **P2** |
| CX-P6 grant independence | **SURVIVES — widened** | P3 ✅ |
| CX-P7 unbounded keywords | **REFUTED on consequence** | P3 → INFO |
| CX-P8 naval fuzzy seam | **NARROWED to latent** | P3 → P4 |
| CX-P9 LLM-only ids | **SURVIVES** | INFO ✅ |
| CX-P10 confidence ≠ meaning | **SURVIVES — fully verified** | INFO ✅ |
| CX-P11 escalation cost | **NARROWED (numbers) + interpretation REFUTED** | INFO |
| CX-P12 click road | **SURVIVES** | INFO ✅ |
| CX-P13 three small hazards | **SURVIVES — harm measured** | P4 ✅ |

---

## REFUTE:CX-P1 — REFUTED

> "`propose_white_peace` is unreachable from any typed phrasing, and the two
> natural phrasings silently become a generic `diplomatic_proposal` reporting
> success."

The mechanical half reproduces. Everything the census built on it does not.

**(a) The unreachability is the documented design, stated in three places the
census did not read.**

- `godot-client/project-sovereign/scripts/diplomacy_wizard.gd:703-705`:
  *"Spec line 352: `propose_white_peace` is structured-only on the wizard
  surface — the typed `propose white peace with X` echo is display copy, not a
  parser dependency."*
- `backend/commands/diplomatic_executor.py:3089-3097` — the executor docstring
  names the whole contract (`settlement_terms=[]`, `white_peace=True`,
  "bypasses the editor empty-Ratify gate"), citing
  SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1.
- `tests/test_settlement_white_peace.py:18-19` — the file header:
  *"The typed `propose common peace with X` command path remains debug/parser-
  only and does not stage through the labeled CTA surface."*

**(b) There is a standing pin that asserts the census's finding as correct
behaviour.** `tests/test_settlement_white_peace.py`,
`TestTypedCommandPath::test_typed_propose_common_peace_does_not_route_through_player_facing_surfaces`:

```python
assert action_str != "propose_white_peace", (
    "typed `propose white peace with X` must not auto-parse to "
    "propose_white_peace; wizard CTA is the only player surface")
```

**Any fix that gives `propose_white_peace` a typed keyword branch reds this
pin.** That is the row's regression answer, named.

**(c) "Silently … reports success" is false on both counts.** Measured at the
endpoint (`probes/rf1_whitepeace.py`, `rf2_wp_payload.py`):

- `propose a white peace with Austria` stages a full dialogue with
  `proposal_terms_summary: ["Peace Treaty (end state of war)"]`,
  `annotated_terms: []`, and four options (*More demanding / More generous /
  Adjust terms / Reconsider*), plus Talleyrand commentary. The player is
  **shown** the terms and can edit or withdraw. Not silent.
- It is **byte-identical** to the control `propose peace with Austria`, and a
  peace treaty with zero clauses *is* a white peace in substance — peace, with
  nothing exchanged. Not wrong.

**Residue worth keeping (P4):** the typed road stages a **bilateral** proposal
while the wizard route stages a `settlement_confirm`. Those are different
mechanisms — but that is the general typed-vs-settlement boundary the project
already records, not a white-peace defect.

---

## REFUTE:CX-P2 — NARROWED

> "The CR-1 action-coverage gate walks a hand-written list that has drifted;
> two mock-reachable actions have ZERO corpus rows and are invisible to it."

**The arithmetic reproduces exactly** (`probes/rf3_coverage.py`): corpus 447
entries; `MOCK_REACHABLE_ACTIONS` 53 entries vs a 65-id union; gate-counted
`diplomatic_downgrade` = **0**, `propose_common_peace` = **0**; twelve ids in
the union are absent from the hand list. The gate at
`tests/test_command_robustness_cr1_eval_harness.py:180-197` does iterate only
that list. **The structural claim survives** — a hand-maintained allowlist
cannot fail for an id nobody added to it.

**The magnitude is over-stated in two ways.**

1. *"Invisible to it" ≠ unpinned.* Both ids have parse-level coverage outside
   the corpus: `tests/test_diplomacy_button.py:759` parses
   `"downgrade relations with Prussia"`; `propose_common_peace` appears in
   **17 test files**, including endpoint-level POSTs at
   `tests/test_fa_slice10_the_offer_on_the_desk_2026_09_05.py:277,292`.
2. *One of the two exemplars is deliberately not player-facing.*
   `tests/test_settlement_white_peace.py:421` — the typed
   `propose common peace with X` "remains in the parser keyword table as a
   **debug/parser-only** entry". Filing zero corpus coverage for a debug-only
   verb as a P2 over-reads it.

So: a real gate weakness, demonstrated with the two worst available examples.
P3. The census's own fix shape (derive the list, or assert
`hand ⊇ measured-reachable`) is right and would have surfaced better ones.

---

## REFUTE:CX-P3 — NARROWED (P2 → P4)

> "Diplomatic pre-routes outrank every marshal verb and only 3 of 14 carry the
> `_addressed_marshal` guard, so marshal orders are hijacked and the marshal is
> dropped."

**The source claim is exactly right.** `_addressed_marshal` is computed at
HEAD `llm_client.py:1294` and consulted at 1491, 1499, 1561 only. The comment
at 1289-1292 states the original scope in writing ("the two new keyword routes
below (peace-intent, treaty-break) stand down for it") — so this was never a
general guard, and the census's "3 of 14" framing implies an intent the code
never claimed.

**The consequence claim does not survive the endpoint.** All six cases cost
**0 AP**, move **nothing**, and return an honest clarification naming the
missing identifier (`probes/rf4_hazards_endpoint.py`, `rf5_p3_and_determinism.py`):

```
Ney, invade Swabia          -> "Sire, which nation should I direct this proposal to?"
Ney, make war on Mack       -> "Sire, against which nation shall we declare war?
                               Specify: Austria, Bavaria, Britain, Denmark, ..."
Ney, escort the envoy...    -> "Sire, which nation shall I approach? ..."
Ney, hold the court of...   -> "Sire, where shall I direct my efforts?"
Ney, charm the locals       -> "Sire, where shall I direct my efforts?"
Ney, the minister has...    -> "Sire, which nation shall I approach? ..."
```

`Ney, make war on Mack` reads alarming as `diplomatic_declare_war target=None`.
**It does not declare war.** It asks which nation, and charges nothing.

**Residue (P4):** the copy is confusing — a military verb addressed to a
marshal is answered with a diplomatic question that never mentions why. Fixing
the *copy* is cheap and safe; adding `_addressed_marshal` to the other eleven
routes is the larger change and would need each route's own regression check.

---

## REFUTE:CX-P4 — SURVIVES

Reproduced at the endpoint **with controls**, which the census omitted
(`probes/rf9_tree_and_rest.py`):

```
offer an alliance to Prussia      -> Berthier shrug        0 AP
propose an alliance with Prussia  -> Berthier shrug        0 AP
propose alliance with Prussia     -> reaches the executor  ("Insufficient
                                     Diplomatic Points... costs 6 DP")   <- control
make Holland a vassal             -> Berthier shrug        0 AP
vassalize Holland                 -> reaches the executor  ("Cannot create
                                     vassal via treaty...")              <- control
```

The contiguous forms reach the executor and are refused on their merits; the
articled forms never arrive. Exactly as filed, and the diagnosis (contiguous
substrings at HEAD `llm_client.py:1543` / 2171, the class F6 already fixed once
for `change_autonomy`) is correct. Harm is a wasted keystroke — 0 AP. **P3 is
fair.**

---

## REFUTE:CX-P5 — SURVIVES, AND IS UNDERSTATED (P3 → P2)

> "'hold' as a bare substring sits above fortify/garrison/drill/recruit and
> eats stronghold/household/threshold."

True, and **worse than filed**. The census reported the parse and stopped. The
control it never ran is decisive (`probes/rf5_p3_and_determinism.py`):

```
Davout, garrison the stronghold  -> "Davout shifts to DEFENSIVE stance at
                                     Rhineland. Effect: -10% attack, +15% defense."
                                    ap 4->3, stance NEUTRAL->DEFENSIVE
Davout, recruit at the stronghold -> same
Soult,  garrison the stronghold   -> same
```

Three corrections to the row:

1. **It executes.** The census's five examples all happen to address **Ney**,
   who is aggressive and objects to a hold — so they *looked* harmless. For a
   marshal who does not object, the misparse spends **1 AP** and changes
   combat modifiers. On the shipped 1805 board, with the shipped roster.
2. **The outcome is not a "hold".** The executor turns it into a **stance
   change**. The player asked for a garrison and got −10% attack / +15%
   defense.
3. **It is not deterministic.** `Ney, drill the men at the stronghold` gave
   objection / objection / **executed** across three fresh-world runs. Any
   single-run executor probe on this board can mislead — a method note for
   whoever builds the fix.

**Fix hazard:** the in-flight `clause_guards.py` edit already re-routes
`does Ney hold Rhineland` (HEAD: not a question → falls to the `hold` branch;
worktree: question → help). A `\bhold\b` fix must be coordinated with that
work or the two will collide.

---

## REFUTE:CX-P6 — SURVIVES, WIDENED

Confirmed at the endpoint: `grant independence to Holland` → Berthier shrug,
0 AP, while the control `release Holland` works (and really does release
Holland: `DIPLO STATE: France-Holland: VASSAL -> PEACE (vassal_release)`).

**Widened:** `free Holland` is a **second** orphaned release phrasing — also a
shrug. The census found one; there are at least two.

---

## REFUTE:CX-P7 — REFUTED ON CONSEQUENCE (P3 → INFO)

> "Unbounded single keywords own whole sentences: blockade, recall, commission,
> autonomy, licence, ' halt'."

The parse observations are all correct. **Every one of the seven is caught one
layer down by an executor guard that names the real reason, costs 0 AP, and
moves nothing** (`probes/rf4_hazards_endpoint.py`):

```
Ney, break the blockade at Ulm    -> "The Admiralty takes its orders from the
   Emperor, Sire, not from a marshal in the field - and a fleet cannot invest a
   city. Say 'blockade the enemy' or 'guard home waters'; to invest a place,
   march on it."
Ney, recall the men to the colours-> "Ney is already in field command, Sire."
as I recall Ney is at Rhineland   -> "Ney is already in field command, Sire."
Ney, commission a bridge at Ulm   -> "No candidate named 'Ney' awaits a
                                      commission. Candidates: Mortier, Grouchy,
                                      Suchet, Oudinot, Augereau, Marmont, Senarmont."
give the men autonomy of movement -> "Specify which vassal."
Ney, licence the sutlers          -> "Sire, I am not aware of a court called 'Ney'."
Ney, the advance is halting       -> "Ney awaits further orders."
```

The blockade case is the sharpest refutation: that refusal is the FA-slice-7
naval guard ("the naval verbs anchor to the fleet and **refuse an addressed
marshal**") working exactly as landed. The census filed as a P3 defect a case
the repo has a shipped slice for, and quoted the parse instead of the message.

These are INFO-grade: a keyword reaches a branch it should not, and the branch
refuses well. The residue is that some refusals are non-obvious
(`"a court called 'Ney'"`), which is copy, not mechanics.

---

## REFUTE:CX-P8 — NARROWED TO LATENT-ONLY; 3 OF ITS 5 EXAMPLES REFUTED

> "`naval_executor.py:577` is the one ungated fuzzy seam of sixteen."

The seam is real: `_resolve_expedition_target` calls
`self._executor.fuzzy_matcher.match(target, list(world.regions.keys()))` bare.
The census then stopped reading. **The function continues for ~25 more lines**,
and the next gate is a shore check.

Measured on the live board (`probes/rf6_naval_seam.py`):

```
'Pass' -> Nassau    (75)  is_coastal=False  REFUSED by the shore gate
'Line' -> Berlin    (86)  is_coastal=False  REFUSED by the shore gate
'Guns' -> Brunswick (75)  is_coastal=False  REFUSED by the shore gate
'Rear' -> Bearn     (75)  is_coastal=True   passes
'Moon' -> Morocco   (75)  is_coastal=True   passes
```

**Three of the census's own five examples die inside the same function**, 6
lines below the line it cites. Beyond the shore gate sit an
already-there check, a land-adjacency check, and the NV-4 consent gate.

**Reachability, pushed harder than the census pushed it** (`probes/rf7_naval_reach.py`):
nine typed phrasings — `land` / `embark` / `expedition`, with and without the
article, and using **Napoleon**, the only marshal under the 15,000 transport
cap, so the lift gate could not mask the result. **All nine arrive with
`target=None`.** The parser nulls an unresolvable target, and the fuzzy
fall-through is guarded by `if not best and target`, so it is never entered.

What *does* reach it is a plausible typo — `land Soult in Munsterr` resolves
`Munsterr → Munster` — i.e. the seam is only ever entered with a string the
parser's own `_plausible_name_typo`-gated target arm already accepted.

Also: **no `.gd` emits `naval_expedition` as a command.** The only hit in the
client is `enemy_phase_dialog.gd:285`, a display label. The census's "a client
payload, an LLM parse, a future chip" is hypothetical on all three counts today.

**Verdict:** ungated by construction — worth closing as defence in depth,
which is what the census's own careful UNVERIFIED note said. But it is P4, not
P3, and its evidence table needs the three non-coastal rows struck.

---

## REFUTE:CX-P9 — SURVIVES

Confirmed as filed. Correctly INFO, and the census correctly reads it as
design rather than defect.

---

## REFUTE:CX-P10 — SURVIVES, FULLY VERIFIED

The census's best finding, and it holds under every check I made.

Confirmed at HEAD: the only confidence assignments in the chain are `0.95`
(action + marshal + target), `0.9` (action + one id), `0.8` (action alone),
`0.5` (unknown), clamped to `UNRESOLVED_ADDRESS_CONFIDENCE = 0.55`
(`llm_client.py:69`); `LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`
(`llm_client.py:63`). `_should_fallback_to_llm` (HEAD 874) has exactly the six
return-False arms the census lists — I read all of them. So the gate opens on
exactly two states, `0.5` and `0.55`.

The corollary is correct and load-bearing: **every hazard in CX-P3/P5/P7 ships
at 0.8–0.95 and is invisible to the model by construction, no matter how good
the model is.** My endpoint measurements are the empirical confirmation —
`Davout, garrison the stronghold` executes a stance change at confidence 0.9,
and no model in any mode is ever consulted.

---

## REFUTE:CX-P11 — NARROWED ON NUMBERS; INTERPRETATION REFUTED

**The numbers are close but did not reproduce to the digit**
(`probes/rf10_escalation_chips.py`). Independently:

```
1805-eligible rows            388      (census: 392)
escalate, bare mock chain      25  6.4% (census: 24 = 6.1%)
escalate, after typo repair    21  5.4%
confidence buckets  {1.0:8, 0.95:158, 0.9:123, 0.8:52, 0.75:1, 0.55:4, 0.5:42}
                     census    ... same, except 0.5:46
```

The denominator gap is explained: 447 total − 4 `live_only` = 443; 388 are
1805-eligible. **392 = 388 + the 4 `live_only` rows**, which the census
excludes everywhere else. The shape of the claim ("the model sees ~6% of
corpus utterances") is robust; the specific 24/392/6.1% triple is not
reproducible as stated.

**The interpretation is wrong, and this is the important part.** The census
writes: *"The 24 that reach the model are all genuine gaps."* Measured against
the corpus's own expectations (`probes/rf11_escalation_meaning.py`):

```
escalating rows: 21
  deliberate NEGATIVE CONTROLS (expected.success == False):  19  (90%)
  real phrasing gaps:                                         2  (10%)
```

The ids say it out loud: `fa80-a-hole-is-not-a-hold`,
`r7-the-line-held-is-not-an-order`, `r7-retire-ney-is-not-a-retreat`,
`fa-n8-pontoon-bridge-is-not-a-keel`,
`fa-n24-a-land-diversion-is-not-the-grand-diversion`,
`r7-send-the-wounded-forward-is-not-a-march`, `dance-with-the-moon`,
`xyzzy-foobar`. These rows exist to prove the parser **stays silent**.
Escalating them is the exact PARSE-NEG hazard documented at
`llm_client.py:911-925` — under forced tool-use every reply must name an action.

And the repo already says what the model should answer. The two cassettes the
census named as gaps —
`tests/data/parser_cassettes/fa73-live-cover-the-retreat-is-not-a-retreat.1805.json`
and `fa73-live-fix-bayonets-is-not-a-repair.1805.json` — both carry
`"action": "unknown"` with interpretations *"No listed action models screening
a withdrawal"* / *"No listed action models fixing bayonets"*. **The expected
model answer is that it adds nothing.**

**Honest limit, stated in both directions:** the golden corpus is a regression
corpus deliberately stuffed with negative controls, so 90% is a property of the
instrument, not of play. That is exactly why the same instrument cannot support
the census's "all genuine gaps" reading either.

---

## REFUTE:CX-P12 — SURVIVES

The negative result holds and is worth keeping. Minor re-derivation: I count
**12 distinct emit templates** in `region_panel.gd` source (`do:` / `order:`
string literals, several parameterised — `recruit` ×3 types, `build` ×6). 19
concrete strings after expansion is consistent with the census's hand list. No
correction needed.

---

## REFUTE:CX-P13 — SURVIVES, WITH THE HARM MEASURED

Confirmed, and the census under-reported two of the three:

```
Ney, scour the countryside     -> scout EXECUTES, ap 4->3   (real cost)
Ney, the scoundrels have fled  -> scout EXECUTES, ap 4->3   (real cost)
Ney, constrain the cavalry     -> drill -> objection, 0 AP
Ney, entrain the men           -> drill -> objection, 0 AP
build / Ney, repair / repairs in Paris -> honest Berthier refusals, 0 AP
```

The `scou` substring **spends an action point and runs a scout**. The bare-verb
shrugs are harmless. P4 is right for the family; the `scou` half is the live
one.

---

# 2. WHAT THE CENSUS MISSED

## MISSED:1 — the road diagram starts in the wrong place (P2, method)

§0 is titled "The shape of the road, **corrected**" and begins at
`CommandParser.parse`. The road does not begin there. `POST /command` is
`backend/main.py:2659-2660` (`execute_command`), and **307 lines run before
`parser.parse`**, containing at least four layers that can rewrite or refuse
the text first (`probes/rf8_missed.py`):

| layer | site | effect |
|---|---|---|
| pending-dialogue answer routing | `main.py` `_respond_to_dialogue_sync` (15 `_pending_answer_token` refs) | returns before the parser |
| **CR-4 context carryover** | `main.py:2923` `resolve_context_references` | **rewrites `command_text`** ("again", "him", "there", "not you, Davout") |
| CR-4 persistent command focus | `try_focus_reissue` | supplies a missing addressee |
| **PC15-4 fallen/captured-name guard** | `_addressed_lost_marshal_refusal` (`main.py:1150`) | refuses by name before any parse |

None appears in the census's diagram or its 24-row pre-chain table. For a
document whose stated purpose is to correct the model of the parser road, that
is a structural omission — and it is directly load-bearing for the design
question the census was asked: a text predictor belongs in this layer, and
"again"/"him"/"there" are **already resolved server-side**, so a predictor must
not re-implement them.

## MISSED:2 — 90% of escalations are negative controls, and no cassette is a live recording (P2)

Covered in REFUTE:CX-P11 above; filed separately because it is the answer to
"is routing to the LLM worth it" and it inverts the census's §7 conclusion.

Additional finding the census did not make: **all 17 cassettes are
`provenance: "authored"`** (`probes/rf12_final.py` — `{'authored': 17, '?': 1}`,
the `?` being `MANIFEST.json`). **Not one is a live recording.** So the repo
contains no measured evidence of what the model actually does on the escalation
set — only the maintainers' authored expectation, which is that it returns
`unknown`. Any claim that the LLM is or is not earning its keep is currently
unfalsifiable from in-repo data, and the honest next step is to record real
cassettes with `tools/record_parser_cassettes.py` (the opt-in recorder IQ-9
already ships) rather than to argue from the corpus.

## MISSED:3 — the prompt's static/volatile interleave, which is the number that decides caching (P3)

The census's §2e gives the cost (16,582 chars, ~4,905 approx tokens, "no prompt
caching anywhere") and stops. It never measured the one structural fact that
decides whether that cost is reducible (`probes/rf8_missed.py`):

```
prompt run1 = 16,579 chars   prompt run2 = 16,561 chars
longest common PREFIX =    84 chars  ( 0.5% of the prompt)
longest common SUFFIX = 3,987 chars  (24.0%)
```

**0.5%.** The volatile blocks are not merely "at the top" — they are
interleaved through the static body:

```
## Your Marshals        char     36   VOLATILE
## Enemy Forces         char    435   VOLATILE
## Valid Actions        char    637   static
## Valid Regions        char  1,885   VOLATILE
## Personality Rules    char  3,168   static
## Flavor Line          char  4,726   static
## Strategic Commands   char  6,419   static
## Cardinal Directions  char  7,960   VOLATILE
## Diplomatic Commands  char  9,528   static
## Cancel Command       char 11,408   static
## Ambiguity Scoring    char 11,815   static
## Output               char 12,595   static
## Examples             char 13,156   static
```

~12,000 chars of fully static content, cut four times by volatile blocks.

This also **corrects the project record**, which the census cited but did not
quote. `docs/STATUS.md:10464`: *"tools+system is ~700 tokens, below Haiku
4.5's 2048-token minimum cacheable prefix, and the volatile game state sits at
the TOP of the ~3.7K-token user prompt."* The measurement shows it is at the
top **and in the middle** — the record names half the obstacle.

**Honest conclusion, against my own interest in a dramatic finding:** this
measurement *supports* the recorded decision rather than overturning it. A
static-first reordering would create a ~2,850-token user-prompt prefix (plus
~760 for tools+system), clearing the 2,048 minimum — but it only pays on the
~6% of requests that escalate, against a prompt-restructure regression risk the
record already weighed. The census should have surfaced the reason and this
structure; it presented the cost as if nobody had considered it.

## MISSED:4 — the census's own provenance note is wrong, and the parser road is being edited live (P3, method)

The census wrote that for the uncommitted `clause_guards.py` edit, *"the line
numbers cited for `clause_guards.py` symbols are the only ones that could have
shifted."* That is false. The edit **rewrites `is_question()`**, which is:

- route **#21 in the census's own pre-chain table** (`llm_client.py:1597` →
  `status` via `question_desk.classify_question`, or `help`), and
- the producer of the census's own §4a `status` row.

Measured HEAD vs worktree over 22 utterances (`probes/rf9_tree_and_rest.py`):
**3 flip**, all False → True:

```
who commands at Ulm        HEAD=False  WORKTREE=True
what's the treasury        HEAD=False  WORKTREE=True
does Ney hold Rhineland    HEAD=False  WORKTREE=True
```

`does Ney hold Rhineland` is squarely the CX-P5 `hold`-substring family — at
HEAD it was not a question and fell through to the `hold` branch. So the census
measured its own headline hazard family on a tree where a sibling agent was
actively changing an adjacent case, and declared the edit irrelevant.

Worse for any future reader: **`backend/ai/llm_client.py` itself became
modified during my session** (+31 lines; clean at my start). Worktree line
numbers are now +26/+27 against HEAD. I re-established provenance for my own
results (§0); nobody reading either document later can assume it.

*(Observation, not a filed defect, since it is in-flight sibling work: in the
worktree all three flipped utterances now route to `help` — the COMMAND
REFERENCE dump — rather than to the fact desk. `what's the treasury` answering
with a command list is worth that agent's attention.)*

## MISSED:5 — an ordinary compound order mis-parses the destination (P3)

The census lists `_split_sequential_orders` (`parser.py:136`) in its own
pipeline diagram and **never probed a compound order**. Measured
(`probes/rf12_final.py`):

```
Ney, move to Alsace and then fortify
   -> "Region 'Alsace And' not found. From Rhineland the roads lead to:
       Swabia, Lorraine, Frankfurt, Gelderland."
```

The destination regex swallows the conjunction into the region name. Bare
`then` works (`Ney, attack Mack then move to Paris` executes and stages the
muster); `and then` does not. `Ney, fortify and Davout, scout Swabia` is
handled correctly and says so ("One order at a time, Sire — I have relayed the
first"), so the split machinery exists and this is specifically the
destination-extraction arm.

This is the same contiguity/boundary family as CX-P4 and CX-P13, on the
single most common compound phrasing a player would type.

---

# 3. Corrections to the census's own text

1. **"the two natural phrasings silently become a generic proposal"** — not
   silent (a full terms dialogue is staged and shown) and not generic (a
   zero-clause peace treaty is a white peace). REFUTED.
2. **"The 24 that reach the model are all genuine gaps"** — 19 of 21 are
   deliberate negative controls with `expected.success == False`. REFUTED.
3. **"392 1805-eligible golden-corpus rows"** — 388. The extra 4 are the
   `live_only` rows the census excludes elsewhere.
4. **"nothing in this census depends on that edit… line numbers… the only ones
   that could have shifted"** — the edit changes `is_question()` behaviour on
   3 of 22 probes, including a `hold`-family case. FALSE.
5. **CX-P8's evidence table** — 3 of its 5 rows (`Pass→Nassau`, `Line→Berlin`,
   `Guns→Brunswick`) are refused by the shore gate six lines below the seam.
6. **"`naval_executor.py:577` … anything that ever hands `naval_expedition` a
   target"** — no `.gd` emits `naval_expedition` as a command; the only client
   hit is a display label at `enemy_phase_dialog.gd:285`.
7. **Credit where due:** the census's line numbers were **accurate at HEAD**
   (nine anchors re-derived), which is unusual for this repo and should be said.

---

# 4. If only three things are built

1. **CX-P5** — the one row where an ordinary sentence spends an AP and changes
   combat modifiers without asking. Word-boundary `\bhold\b`, coordinated with
   the in-flight `is_question` work.
2. **MISSED:2 / CX-P11** — before tuning the LLM road, record real cassettes.
   The escalation set as measured is 90% sentences that should end in a refusal,
   and the repo's own authored expectation is that the model returns `unknown`.
   That is an argument for narrowing the gate, not widening it.
3. **CX-P10's corollary** — the reason a predictor is the right instrument:
   confidence counts identifiers, so the gate can never see a confidently-wrong
   parse. A keystroke-time predictor sits *upstream* of confidence and is the
   only mechanism in this architecture that can prevent one. (Note the
   census's `KEY_TAB` collision is real — verified at `main.gd:959` and
   `main.gd:1161`.)
