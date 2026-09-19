# VERDICT — CX3-R11

**NARROWED.** The observable reproduces exactly. The **diagnosis is refuted by
measurement**, and the fix it points at is **inert**.

> The finding says the census's gap is **scope** — that `recruit` is offered by
> a producer outside the census. Measured: **`recruit` is INSIDE the census's
> own quoted set.** It is printed in the backend help body at
> `meta_executor.py:745` as `"recruit" / "recruit for Davout" / "recruit at
> Paris"`, and the census's own regex takes all three. The row's headline
> example is not a scope miss; it is a **refusal-predicate** miss.
>
> And the real hole hides two strings that are **worse than `recruit` and of
> the census's OWN stated class** — one of which is the manual's only example
> for `move`, and the other an exact sibling of the `"Davout, hold Ulm"` case
> CX-3 wrote into its own docstring and fixed by hand.

Probes I ran: `probes/r11_a_scope.py`, `probes/r11_b_execute.py`,
`probes/r11_c_success_sweep.py`. Tree at `f52df77f` (HEAD moved past the task's
`727cf88a`; the extra commit is docs + `test_cx1_*` and touches nothing here).
Nothing outside the scratchpad was written; no git mutation.

---

## 1. What reproduces, exactly as filed

`probes/r11_b_execute.py` — real `/command` endpoint, fresh shipped 1805 board:

```
=== 'recruit'
   success      : False
   message      : Berthier scans the dispatches. 'No marshal is available to receive
                  reinforcements, Sire.' Recruits join a marshal who can reach the depot:
                  Ney (out of range - 5 regions away, range 1); Davout (out of range - 5
                  regions away, range 1); Soult (out of range - 4 regions away, range 1)
                  (and 5 others). March a corps within range, or name one directly
                  ("recruit 10000 infantry with Ney").
```

The client's boot help does print it (`main.gd:762` — `"recruit" or "end
turn"`), it is printed at campaign start, and **it is player-reachable**: I
walked `_redirect_diplomatic_command`'s three keyword arrays
(`DIPLO_NO_HOME_KEYWORDS`, `DIPLO_WAR_ROOM_KEYWORDS`, `DIPLO_FAMILY_KEYWORDS`)
and none of the 114 forms is a substring of `recruit`, so the sentence reaches
the backend unchanged. All eight French marshals boot at least 4 provinces from
Paris with `movement_range` 1, and Tier 1 of the D7 seed envelope fixes marshal
placement — so **this refuses on turn 1, on every seed, for every player.**

So the *behaviour* half is real, and P4 is defensible on impact: the refusal is
CA8-11's, and it names the cause, the distance, the range, and a command that
works.

---

## 2. What does not reproduce — the diagnosis

`probes/r11_a_scope.py` runs the census's own extraction
(`MetaExecutor._execute_help({}, world)["message"]`, regex `"([^"\n]{3,70})"`):

```
help body chars: 11636
quoted strings censused: 50

--- quoted strings containing 'recruit' (IN CENSUS SCOPE) ---
    'recruit'
    'recruit at Paris'
    'recruit for Davout'
bare 'recruit' in censused set: True

--- client boot-help strings vs the census's quoted set ---
   'Ney, attack Mack'       in census scope: True
   'recruit'                in census scope: True
   'scout Swabia'           in census scope: False
   'move to Flanders'       in census scope: False
   'end turn'               in census scope: False
```

**The row's one filed example is in scope.** Two of the five boot-help strings
are already censused. The census passes `recruit` not because it cannot see it,
but because it looks at the wrong thing.

The finding also never drove `"recruit at Paris"` — same help line, same
census, and it **also refuses** (`success=False`, same block reason). It
under-counts its own family by one.

### The scope fix is measured inert

Widening the census to the client's boot help catches **nothing**. All five
strings pass the census's own predicate: `Ney, attack Mack` (already in scope),
`scout Swabia` ok, `move to Flanders` ok (a clarification, not a refusal),
`recruit` (already in scope), `end turn` ok. Zero new failures.

The third producer is not a gap either. **The tutorial chips already have their
own census** — `tests/test_tutorial_position7.py:414`
`test_b1_every_suggest_mock_parses_to_its_action` reads every
`(suggest, suggest_action)` pair out of `tutorial_overlay.gd` and mock-parses
it. The finding says they are "out of this census by construction" without
checking whether another one covers them. One does, and it predates row CX.

The second producer is the finding's own withdrawn case applied inconsistently.
`llm_client.py:1341-1344` builds `actions_sample` from the literal list
`["attack","move","scout","defend","fortify","recruit"]` — a bare **vocabulary
list**, exactly the shape of `ALLOWED: move, recruit, defend, wait, change
stance` that the finding examined and correctly withdrew. The shrug's actual
*offer* (`_offer`, `_second`) comes from `counsel.what_can_i_do`, the same
source the executor reads. There is no second producer here.

---

## 3. The real hole, and it is worse than the one filed

`test_every_quoted_phrasing_survives_the_EXECUTOR` decides "refused" by
matching six needles — `not found`, `cannot parse`, `Unknown target`,
`I cannot interpret`, `no such`, `eludes me` — and **never reads
`result["success"]`**.

`probes/r11_c_success_sweep.py` — all 43 censused strings (exemptions removed)
through the real endpoint, a fresh board each time:

```
caught by TODAY's needle list : 0   []
success is False              : 18
```

Sixteen of the eighteen are legitimate gates the game is right to refuse (800g
against a 4,012g substitute; an enemy one province away blocking drill; an
expectation already met; a fleet already at guard). **Two are the census's own
class — the game teaching a place name the 126-province map does not have:**

| censused string | the executor answers | on the map? |
|---|---|---|
| `"repair Lyon"` (`meta_executor.py:800`) | **`Unknown region: Lyon`** | `'Lyon' in world.regions` is `False` |
| `"Soult, move to Bavaria"` (`meta_executor.py:739`) | `Bavaria is a nation, not a province. Name a province, Sire — theirs are Franconia, Munich, Swabia.` | `'Bavaria' in world.regions` is `False` |

`"repair Lyon"` is a flat dead end with no remedy named. `"Soult, move to
Bavaria"` is **the manual's only example for the `move` verb**.

Both are invisible to the census for a one-word reason: the needle list holds
`not found`, and `_execute_repair` says `Unknown region:`.

The sharpest part: the census's own docstring names `"Davout, hold Ulm"` ->
*"Region 'Ulm' not found"* as the case a parser-level census would call green.
That string stood at `b4a27a15^:meta_executor.py:704` and **is gone at HEAD** —
CX-3 fixed the one it wrote down, by hand, and left two siblings of the same
class standing inside its own scope, because the predicate meant to find them
generalises through a needle list rather than through the executor's own
answer.

---

## 4. Severity, attribution, reachability

* **Severity** — P4 holds for `recruit` on impact. The row **redirected at its
  real target is P3**: `repair Lyon` is a dead end, and the `move` example in
  the COMMAND REFERENCE does not work.
* **Player-reachable** — `recruit` **yes** (boot help, every session, not
  redirected). `repair Lyon` and `Soult, move to Bavaria` **yes**, by typing
  `help`, which is the surface both live on.
* **Shipped by row CX — NO, for every behaviour.** `"recruit" / "recruit for
  Davout" / "recruit at Paris"` stood at `b4a27a15^:meta_executor.py:657`;
  `"Soult, move to Bavaria"` at `:651`; `"repair Lyon"` at `:712`; and the
  client boot-help block is byte-identical at `b4a27a15^:main.gd:742-746`. The
  *census* is CX-3's, so "the census does not catch them" is the row's, and the
  finding's `shipped_by_this_row: false` is correct as stated.

---

## 5. Would the fix ship a regression?

* **The filed direction (widen the scope)** — no regression, and **no value**:
  measured 0 new failures. It would add a `.gd`-reading pin with no defect
  behind it and duplicate `test_b1_every_suggest_mock_parses_to_its_action`.
* **The obvious stronger fix (`assert result["success"]`)** — **ships a
  false-red census**: 18 of 43 red, 16 of them the game correctly saying no.
  It would red the treasury gate, the adjacent-enemy drill gate, the
  already-met expectation and the already-at-guard fleet, and the builder would
  then exempt them one by one until the pin meant nothing.
* **What actually works** — add the two naming refusals the executor really
  emits to the needle list (`Unknown region`, `is a nation, not a province`).
  That reds exactly 2, both real, and both close with a one-word edit to the
  help body naming a province that exists. No production behaviour moves, and
  no existing pin reds.

---

## 6. One thing the finding got right and should be kept

Its section 12's measurement of the **quoting form** — 0 single-quoted, 0
backticked, 0 curly-quoted, 0 strings over 70 characters, 0 under 3 — is
correct and worth keeping on the record. The regex is not the weakness. The
predicate is.
