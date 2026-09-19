# VERDICT: L2-2 — NARROWED

**Finding as filed:** `general_defensive` is a sixth marshal-less command type
and `_MARSHAL_LESS_TYPES` omits it, so the guard never runs for `defend` —
comma or no comma. **P1**, player-reachable, not shipped by row CX.

**Verdict: NARROWED.** The mechanism is real and reproduces verbatim; the
census is correct; the proposed fix is correct and is clean against everything
I can measure. **The severity is wrong** — filed P1, measured P3 — because the
row never measured the leak's PAYLOAD, and the payload is 1 action point and a
sentence. And the fix, landed alone, imports L2-5 onto the defend family.

Tree: HEAD is **`f52df77f`**, clean — the task names `727cf88a`, and
`f52df77f` sits one commit above it. Checked: it touches only `docs/`,
`tests/test_cx1_…`, and a new `tools/_cx_sweep_both_arms.py`; **no
`backend/` or `godot-client/` source**, so every measurement below is
`727cf88a`'s behaviour. Probes: `probes/r1_reproduce.py`,
`r3_fix_regression_v2.py`, `r4_preexisting_and_payload.py`,
`r5_fix_end_to_end.py`, `patch_plugin.py`. Board: shipped 1805, **a fresh world
per utterance**, driven at `POST /command` with the world/game_state/parser
triple swapped.

---

## 1. Does it reproduce? YES — exactly as filed.

`probes/r1_reproduce.py`, one fresh 1805 board per row:

```
Zorglub defend            ok=True  AP 4->3  "All forces take defensive positions: Ney, Davout, Soult, …"
Wellington defend         ok=True  AP 4->3  identical
Berthier defend           ok=True  AP 4->3  identical
Grouchy defend            ok=True  AP 4->3  identical
Wellington, defend        ok=True  AP 4->3  identical   (WITH the comma)
the Iron Marshal, defend  ok=True  AP 4->3  identical   (WITH the comma)
Zorglub, defend           ok=True  AP 4->4  "There is no Marshal 'Zorglub'…"  — inert, parser path
CONTROL: Zorglub attack Mack   ok=False AP 4->4  refused free by the CX-1 guard
```

All six rows of the filed table reproduce, in both punctuations, including the
two FA-22 named cases.

*Observation in passing, not filed and not mine:* the parser's own refusal for
`Zorglub, defend` returns **`success: true`** while the guard's refusal for
`Zorglub attack Mack` returns `success: false` — two refusals of the same class
of error with opposite success flags. Pre-existing, adjacent, harmless here
(AP is unchanged either way).

**The census is right too**, and I re-derived it independently rather than
trusting it — an AST walk over `_classify_command`'s own `return` constants
(`r4`, part C):

```
returns      : auto_assign_attack, auto_assign_bombardment, auto_assign_scout,
               general_attack, general_defensive, general_retreat, specific
marshal-less : six
in tuple     : five
MISSING      : ['general_defensive']
```

`_MARSHAL_LESS_TYPES` has exactly one consumer (`executor.py:1018`), so there
is no second guard with the same hole. And I closed the census on the producer
side, which the finding does not: across `backend/` there are **15** literal
`["type"] = "<non-specific>"` assignments and **14** non-literal `["type"] =`
lines, and every one of them writes a diplomatic / settlement / event payload
dict, never a command dict. The only command-dict writes are three literal
`= "specific"` (`combat_executor.py:10189`, `executor.py:1613`,
`movement_executor.py:1156`). **`_classify_command` is the SOLE producer of a
marshal-less command type**, so the census is closed: six types, one hole, no
seventh arriving by another road.

**The whole finding in one table** — one utterance per marshal-less type, each
addressed by the same unbindable name, parsed on the shipped 1805 board and
handed straight to the guard:

```
type                       produced?  _unbound_addressee returns
general_attack             True       'Zorglub'
auto_assign_attack         True       'Zorglub'
general_retreat            True       'Zorglub'
auto_assign_scout          True       'Zorglub'
auto_assign_bombardment    True       'Zorglub'
general_defensive          True       None        <- the hole
```

---

## 2. Severity: P1 is WRONG. Measured P3.

**The finding tabulates the MESSAGE and never measures the STATE.** I did
(`r4`, full footprint: AP, admin AP, gold, turn, and per-marshal location,
strength, fortified, tactical_state, stance, morale, plus region stability and
controller):

```
Zorglub defend  ->  scalar_diff {"ap": [4,3]}   marshal_diff {}   region_diff {}
```

Not one marshal field moves. `_execute_general_defensive`
(`combat_executor.py:10291`) builds a message and an event and **returns
`new_state: game_state` having mutated nothing at all.** Its event carries
`"effect": "All regions get +30% defensive bonus next turn"` — and that bonus
does not exist anywhere: `defensive_bonus` is not a field on `Marshal` or
anywhere else in `backend/` (grep over the whole backend: 0 hits).

⚠ Precision, because I first wrote this too strongly: the `effect` string is
never rendered either — `main.gd:3038` renders only `message`. So what the
player actually sees is *"⛨ All forces take defensive positions: Ney, Davout,
…"* in success green, with the action cost shown, and nothing behind it.

So the leak's entire payload is **1 AP of 4, and a sentence**. Compare the
row's own P1 in the same probe, with CX-1's lever off:

```
Zorglub attack Mack (lever OFF) -> a real battle: SIX corps relocated to Swabia,
                                   298 gold, ~5,000 men, AP 4->3
Zorglub defend      (either arm) -> AP 4->3.  Nothing else.
```

That is what a P1 looks like in this family, and this is not it. The project's
own nearest precedent is **FA-6, amended P1 → P2 on the reasoning that AP do
not carry over** — and FA-6 irreversibly ADVANCES THE TURN. A 1-AP no-op is
strictly less than that.

Three more measurements that hold it at P3:

* **The leak's outcome is byte-identical to the legitimate bare order.** A
  player who types `defend` gets the same 1-AP no-op and the same green
  all-forces-are-defending line. The addressee hole changes *who is blamed*,
  not *what happens*.
* **The family is the least-travelled command type in the game.** 0 of 456
  strings across every `tools/playtest_scripts/*.json`; 2 of 437 golden-corpus
  rows, both bare (`defend`, `defend my position`); and **zero tests anywhere
  in a 23,618-test suite mention `general_defensive` or its message.**
* Nothing irreversible, no gold, no men, no turn advance, no save state.

**The P2 boundary, stated so the owner can move it:** the guard is a safety
rule, and a safety rule with a hole is worth more than its current payload,
because the next verb routed into the family inherits it. That argues for
*fixing* it — and for the census pin, which is the durable half — not for
calling today's consequence severe. If the project's convention is that **any
unrequested AP charge is P2 regardless of payload**, then P2 and not lower; it
is not P1 under any reading, because nothing irreversible happens and the
row's own P1 comparator moves six corps.

---

## 3. Player-reachable: YES. Confirmed independently.

* `main.gd::_redirect_diplomatic_command` intercepts only
  `DIPLO_NO_HOME_KEYWORDS`, `DIPLO_WAR_ROOM_KEYWORDS` and
  `DIPLO_FAMILY_KEYWORDS` (read at `main.gd:1721-1775`). **None contains
  `defend` or any substring of these sentences, and none of them names a
  nation**, so the terminal sends them verbatim.
* `defend` is row 8 of the completer's own `_MARSHAL_VERBS`
  (`main.gd:6882-6893`), so the game teaches the verb.
* `Grouchy` and `Berthier` are names the game prints — Grouchy from the
  `marshal_pool` bench in `europe_1805.json:423`, Berthier in the fallback
  parser's own voice.

**But the game never OFFERS a leaking sentence.** The completer composes
`marshal + ", " + verb` (`main.gd:7048`) from the live roster, so every
suggestion binds and never reaches the guard. Verified in `r3`: all 40 printed
forms over the live roster, in both punctuations, are unaffected. **The CX-3
rule — the game must not offer a sentence it cannot read — is not breached.**
Reachable by a player who types an addressee the roster cannot bind: a typo, a
foreign marshal, a bench candidate, or the chief of staff.

---

## 4. Shipped by row CX: NO — and I proved it by experiment, not by reading.

The finding asserts this correctly but does not demonstrate it. Two independent
demonstrations:

**(a) Structural.** `git show b4a27a15^:backend/commands/executor.py` has
`_MARSHAL_LESS_TYPES` byte-identical at the same five members (lines 923-926).
The tuple gate is the FIRST line of `_unbound_addressee` and returns before any
punctuation logic, so no change CX-1 made to the comma rule could reach a
`general_defensive` command.

**(b) Measured.** `r4` drives both arms of CX-1's own flip lever,
`AN_ADDRESS_NEEDS_NO_COMMA`, which the row documents as restoring the
comma-only rule byte-for-byte:

```
                          lever ON (shipped)        lever OFF (pre-CX-1)
Zorglub defend            AP 4->3, no-op            AP 4->3, no-op      IDENTICAL
Wellington, defend        AP 4->3, no-op            AP 4->3, no-op      IDENTICAL
defend                    AP 4->3, no-op            AP 4->3, no-op      IDENTICAL
Zorglub attack Mack       refused free              A REAL BATTLE        <- lever is live
```

The control flips and the defend family does not. **The lever bites, and it
does not touch this.** Pre-existing, FA-22's, in both punctuations.

One thing the finding does NOT over-claim, unlike its sibling L2-1: the row's
record does not assert the defend family. `COMMAND_EXPERIENCE_SPEC.md` §3.1 is
written entirely in `attack` and `retreat`, and never says otherwise.

---

## 5. Would the fix ship a regression? Not against anything recorded — but it does not stand alone.

The finding proposes the fix and never measures it. I did, four ways.

**(a) Every recorded utterance.** 437 unique golden-corpus rows + 456 strings
from every `tools/playtest_scripts/*.json` = **893 swept**. Two classify
`general_defensive` (`defend`, `defend my position`), both bare, both with an
empty leading run. **Newly refused under the fix: 0.** (`r3`, plus the script
arm.) The probe carries a sensitivity arm asserting it can see both states —
my first cut of this sweep read `type` off `parser.parse`'s WRAPPER instead of
`result["command"]` and reported a green 0 of everything while measuring
nothing. That correction is why the sweep is trustworthy.

**(b) The printed-sentence arm.** 40 completer/clarification-shaped forms over
the live roster, both punctuations: 0 refused.

**(c) End to end.** `r5` drives the six rows and eleven controls through
`POST /command` at both tuple positions. The fix closes **exactly** the six and
changes nothing else — `defend`, `defend my position`, `Ney, defend`,
`Ney defend`, `all forces defend`, `everyone defend`, `the army defend`,
`can you defend`, `please defend`, `we defend`, `Zorglub, defend` all identical.

**(d) The committed suite** under a pytest plugin that applies the fix at
`pytest_configure` (the six-member tuple is echoed at the head of the run, so
this arm is not measuring an unpatched tree — my earlier sweep already taught
me that lesson once):

```
[patch_plugin] _MARSHAL_LESS_TYPES = ('general_attack', 'auto_assign_attack',
  'general_retreat', 'auto_assign_scout', 'auto_assign_bombardment',
  'general_defensive')
...
23656 passed, 4 skipped in 737.54s (0:12:17)      exit 0
```

**Zero failures across the whole committed suite**, plus a separate targeted
run of the eight files that mention any of these symbols or a `defend` command
(`test_cx1_…`, `test_fa_slice1_the_two_words_…`,
`test_command_robustness_cr0_parser_rosters`, `test_llm_strategic`,
`test_strategic_parser`, `test_ui_disobedience`, `test_pf6_hold_ap_announce`,
`test_naval_diorama`): **505 passed.** The row's own 20
`TestAnAddressNeedsNoComma` pins are green under the fix.

⚠ **Stated limit of arm (d):** the patch is a class attribute, so tests that
SPAWN a child interpreter (the mutation sweeps, `spawn_run`, the driver arms)
re-import `backend` and run UNPATCHED. That is acceptable here and measured
rather than assumed: those harnesses drive the playtest scripts, and **0 of
their 456 strings classify `general_defensive`** (arm (a)), so there is nothing
in them for the fix to touch.

### ⚠ The fix extends L2-5 from five types to six. Land them together.

`r5`'s natural-English arm found collateral the finding did not look for:

```
quickly defend   SHIPPED AP 4->3 (no-op)  PATCHED AP 4->4 "There is no 'quickly' in the order of battle"
somebody defend  SHIPPED AP 4->3 (no-op)  PATCHED AP 4->4 "There is no 'somebody' …"
Vienna defend    SHIPPED AP 4->3 (no-op)  PATCHED AP 4->4 "There is no 'Vienna' in the order of battle"
Swabia defend    SHIPPED AP 4->3 (no-op)  PATCHED AP 4->4 "There is no 'Swabia' …"
```

That is **L2-5's class** — *a run with no function word is treated as a name* —
plus **FA-54's class** on the last two (a province refused with the wrong
category's idiom, and WO slice 2's rule is that an ADDRESSEE which is a
province should resolve to the province).

⛔ **But I checked the fair comparison before filing this as a cost of the fix,
and it softens it substantially.** The shipped tree ALREADY does exactly this
on the five types in the tuple:

```
Swabia attack Mack    AP 4->4  "There is no 'Swabia' in the order of battle, Sire."
Vienna attack Mack    AP 4->4  "There is no 'Vienna' …"
quickly attack Mack   AP 4->4  "There is no 'quickly' …"
somebody attack Mack  AP 4->4  "There is no 'somebody' …"
Swabia retreat        AP 4->4  "There is no 'Swabia' …"
```

So the fix **does not create** this behaviour — it makes the sixth type
consistent with the five that already have it, which is arguably the point. It
widens L2-5's reach by one verb, silently, trip-ping no recorded utterance and
no pin.

**Recommendation, unchanged but for the right reason:** take L2-4/L2-5's
head-token predicate FIRST or in the same commit, so all six types get the
correct rule at once rather than the sixth inheriting the flawed one.

### The fix closes the guard hole and leaves the real trap standing

Worth saying on the row, because the fix will look complete and will not be:
after it lands, `Zorglub defend` is refused free and **`defend` still costs
1 AP, mutates nothing, and reports in success green that all eight marshals
took defensive positions.**

And it is not that the verb is unimplemented — its PER-MARSHAL sibling is a
real mechanic. `tactical_executor._execute_defend` is context-aware: NEUTRAL →
DEFENSIVE stance, DEFENSIVE → fortify. So:

```
Soult, defend    -> a real stance change / fortify
defend           -> 1 AP, and nothing, for the whole army
Zorglub defend   -> the same nothing, with the guard asleep
```

`general_defensive` is a paid no-op standing beside a working sibling, and the
help text at `meta_executor.py:735` sells it as *"Take defensive position (+30%
bonus)"*. That is the larger defect in this neighbourhood, it belongs to
nobody, the fix does not touch it — and the fix will make it *look* handled,
because the refusal it adds is correct and visible while the no-op underneath
stays silent. It deserves its own row.

---

## 6. What the finding got right, stated so it is not re-litigated

* The mechanism, the first-line early return, and all six table rows: correct.
* The six-vs-five census: correct, re-derived by AST.
* "All five tuple members are genuinely produced and reach the guard": correct.
* `player_reachable: true`: correct.
* `shipped_by_this_row: false`: correct.
* The `fix_shape`'s durable half — **pin the tuple against
  `_classify_command`'s own return values by census** — is the right shape and
  is the part worth keeping. A seventh type should not be addable without the
  guard learning it.

  ⚠ **Write it as an AST walk over the function's own `Return` constants, not
  as a source grep.** `r4` part C does exactly this and takes eight lines. The
  project's own repeated lesson (slice 13's licence census, slice 10's
  direction gate) is that a text census is killed by a text pin *by
  construction* and comes back INERT under the sweep; an AST census executes
  production source and dies the moment a member is deleted from the tuple.

## 7. What I changed about the finding

| field | filed | verdict |
|---|---|---|
| reproduces | — | **YES**, verbatim, all six rows |
| census (six types, one missing) | correct | **correct**, re-derived by AST; producer side closed too |
| severity | **P1** | **P3** (P2 at the outside) — measured null payload |
| player-reachable | true | **true**, confirmed against `main.gd`'s redirect and completer |
| shipped by row CX | false | **false**, now *proven* by flipping the row's own lever |
| fix shape | add the type + census pin | **correct** — but land it with L2-4/L2-5's head-token predicate, and write the pin as an AST census |

## 8. The one-line ruling

> Real, reproduced, pre-existing, correctly diagnosed, correctly fixed — and
> **P3, not P1**, because the room it leaks into is empty: the executor it
> reaches mutates nothing, and the sentence it prints — *"All forces take
> defensive positions"* — is a claim the engine never carries out for anybody,
> addressed or not.
>
> The finding measured the message and not the board. Attacking a fix means
> asking what it costs; attacking a *finding* means asking what it costs too.
