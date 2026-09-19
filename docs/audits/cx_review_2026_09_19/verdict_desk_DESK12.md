# VERDICT: DESK-12 — **NARROWED (and PRE-EXISTING in the half that harms); the filed fix would ship a regression**

Refutation pass at master `f52df77f` (row CX tip `727cf88a` + its docs commit), tree clean.
Probes: `…/scratchpad/cx_review/probes/` — `dk.py` (harness), `d01`…`d04`, `d03_client_mirror.py`,
`plug_nopeace.py`. Every figure below is from a probe I ran on the shipped 1805 boot board
(`parser_eval.build_world("1805")`), driven through `POST /command`, `LLM_MODE=mock`.

**Filed:** *"Half of the at_war kind's own authored vocabulary is blocked by the client … the player
asking the peace form gets the Cabinet redirect, never the answer."* P4, player-reachable **false**,
shipped by row CX **true**. Fix shape: *"add the interrogative leads to the client's advisory
exemption, or drop `peace` from the regex."*

---

## 1. The observable reproduces. The diagnosis does not.

I rebuilt `main.gd::_redirect_diplomatic_command` independently of lens 3's `p18` — and rather than
retyping the const arrays I **parse them out of the `.gd` source** (`d03_client_mirror.py`), so a
transcription slip cannot manufacture or hide a result. It agrees with the filed claim:

```
parsed 115 family keywords, 30 nation forms
'peace with' in family list: True      'war with' in family list: False

  passes   'am I at war with Prussia'        [fail-open]
  BLOCKED  'are we at peace with Prussia'    [CABINET:family:peace with]
```

So far, so filed. **But the client is the second door, not the first.** The backend's own
`_proposal_keywords` (`llm_client.py:1715`) contains `"peace with"` and returns at line 1727 —
**38 lines above** the `is_question(...)` block at 1765 that is the desk's only call site. I drove
the whole authored vocabulary through both doors (`d04_matrix.py`, 28 utterances):

| utterance | client | backend parse | desk answered? |
|---|---|---|---|
| `am I / are we / is France at **war** with X` | passes | `status` | **YES** (6/6) |
| `… at **war** with X?` | passes | `status` | **YES** (6/6) |
| `… at **peace** with X` | **BLOCKED** | *(would be)* `diplomatic_proposal` | no (0/6) |
| `… at **peace** with X?` | **passes** | `diplomatic_advisory` | **no** (0/6) |

```
desk answered: 13/28   client-blocked: 9/28
```

**The decisive row is the fourth.** The client *already* exempts a `?`-terminated sentence
(`_is_advisory_question` tests `ends_with("?")` first). `are we at peace with Austria?` therefore
**reaches the backend today** — and still never reaches the desk, because the proposal keyword eats
it one layer earlier. So:

* the filed cause ("blocked by the client") accounts for **6 of the 12** dead peace forms, not all;
* and **the filed fix cannot work.** Widening the client's advisory exemption to `are`/`am`/`is`
  only reproduces what the `?` form already does — `diplomatic_advisory`, never the desk.

## 2. "Never the answer" is measurably false — both roads answer the player

```
> are we at peace with Prussia          (client blocks)
  Berthier: Matters of state are conducted at the table, Sire … Take your seat in the Cabinet
     ⚜ Take your seat at the table (F1)
```
…and the Cabinet's own step-1 nation list prints exactly what was asked —
`diplomacy_wizard.gd:304-312` renders `display_name + "  —  " + state_display + "  |  " + relation`,
i.e. **`Prussia — Peace | -10`**. The redirect points at the surface that holds the answer.

```
> are we at peace with Austria?         (client passes)
  "We are at war with Austria, Sire. War score stands at 0 from our perspective. Their military
   strength is overmatched relative to ours. Metternich is calculating — skill 9…"
```
Talleyrand's advisory answers the question **more fully than the desk's one-liner would**
(`am I at war with Austria` → *"Yes, Sire — we are at war with Austria. The war score stands at +0."*).

A player asking this question is not left unanswered on either road. That is the narrowing.

## 3. ⛔ The filed fix would ship a regression — measured, not argued

Widen the client exemption as filed, and the **non-`?`** peace form reaches the backend. On the
shipped boot, against a court France is actually at war with (`d02_full_response.py`):

```
> are we at peace with Austria
  message: "Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms
            appropriate to the current military situation."
  diplomatic_dialogue.type = "proposal_confirm"     dp_cost = 3     dialogue_id = 1
  world.pending_diplomatic_dialogue = {… 'action': 'execute_proposal', terms: {'type': 'peace' …}}
  options: [Send as suggested | Harsher terms | More generous | Adjust terms | Reconsider]
```
`is France at peace with Austria` and `am I at peace with Austria` do the same. And the client
**mounts it**: `_response_has_proposal_confirm_route` fires on any non-null `diplomatic_dialogue`
(`main.gd:2704`), so `_route_proposal_confirm_response` puts a peace-proposal confirmation modal in
the player's face — **off a typed question.** That is the exact class row **CX-1 exists to prevent**
("a question never orders"), and the client block is currently the only thing preventing it.

*(On this seed the Send button is disabled by the Bavaria alliance paradox. That is board luck, not
a guard: the paradox is a HARD_STOP on this pair only.)*

## 4. Shipped by row CX? Only the dead arm. The harm is PRE-EXISTING.

* Backend: `git show b4a27a15^:backend/ai/llm_client.py` → `"peace with"` in `_proposal_keywords` at
  **line 1549**, `if is_question(original_text):` at **line 1601**. The proposal road claimed this
  sentence before row CX existed.
* Client: `git log -S'"peace with",' -- …/main.gd` → **`96a37fe3`, 2026-08-21, WO slice 7 (WO-D2 / G1)** —
  four weeks before CX-1.
* CX-2 added the `at_war` kind itself (absent from `b4a27a15^:backend/ai/question_desk.py`).

So what row CX shipped is a **dead regex arm** — the `(?:war|peace)` alternation — and a source
comment (`# "am I at war with Prussia" / "are we at peace with Austria"`) advertising as an example
a sentence the desk can never receive. **No player-visible behaviour changed in either direction.**

## 5. Severity: P4 stands, and the real weight is that it is unpinned

The `at_war` kind has **zero coverage anywhere**:
* `grep -c "at war with\|at peace with" tests/data/parser_golden_corpus.json` → **0**, over 449 rows.
* No test file references the kind; the one `classify_board_question` call in the CX-2 suite
  (`:565`) is the `treasury` kind.

I measured the safe fix rather than assuming it: `plug_nopeace.py` strips `peace` from the pattern
**in memory** (nothing under `backend/` touched) and re-runs the row's own files plus the keyless
parser gate:

```
BASELINE                          314 passed in 36.50s
peace stripped from at_war regex  314 passed in 36.03s
```

**Half the kind's authored vocabulary can be deleted and not one pin notices.**

## 6. One the lens missed: the WAR half is not clean either

```
  BLOCKED  'Talleyrand, am I at war with Prussia'   [CABINET:addressed]
```
`_is_diplomat_addressed` claims the whole address route and none of `DIPLO_ADDRESS_EXEMPT_WORDS`
appears, so the *war* form is blocked too whenever the player addresses the foreign minister — which
`_LEAD`'s own `_ADDR` prefix invites. (Conversely `Ney, are we at peace with Prussia` is the **one**
backend-reachable route to the peace arm — the `and not _addressed_marshal` guard on
`_proposal_keywords` skips it — and the client blocks that. Nobody types it.)

## 7. Corrected disposition

**Not** "add the interrogative leads to the client's advisory exemption" — that is the regression in §3.

Either:
* **(a)** drop `peace` from the at_war pattern and record on the row *why* (the backend owns the
  phrase for proposals). Measured cost: **zero pins** (§5). This is the honest, cheap close; or
* **(b)** if the peace form is wanted, it must be taken at the **backend** — the desk consult moved
  above `_proposal_keywords`, or the keyword narrowed. That is CR-6-sized and carries its own
  regression surface (`make peace`, `sue for peace`, `seek peace` are order keywords sharing that
  block), and it must land **together with** a fix for §3, because it opens the same door.

Either way the row should record that **`are we at peace with X` stages a peace proposal on the
typed road today** (pre-existing, currently masked by the client) — that is worth more than DESK-12
itself and belongs with CX-X2 at CR-6.

`player_reachable`: the **symptom** is fully reachable (most natural phrasing, first try); the desk
**answer** is not reachable by any phrasing a person would type. Filing it as `false` reads as "no
player ever sees this", which is the wrong half.
