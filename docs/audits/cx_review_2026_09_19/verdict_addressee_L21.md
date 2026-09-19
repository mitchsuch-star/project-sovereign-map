# VERDICT — L2-1 (lens "addressee")

> **CONFIRMED · P1 upheld · PRE-EXISTING (not shipped by row CX) ·
> player-reachable.** The defect reproduces on 27 of 27 verbs I drove myself.
> **But the finding is wrong in all three of its census figures, one of its
> listed verbs is not routed at all, and one of its sub-claims is false — and
> it MISSES its own mirror, which is the half a builder will trip over.**

Tree `master 727cf88a`, clean, read-only. Board: shipped 1805, **fresh world
per utterance**, driven at `POST /command` with the world/game_state/parser
triple swapped. Probes `.../cx_review/probes/rL21_*.py`. Nothing in the repo
was edited; every "fix" arm is a class-attribute monkeypatch in a probe or a
`-p` plugin.

---

## 1. Does it reproduce? YES — 27/27, exactly as filed

`rL21_a_headline.py`, one fresh board per line. Control first:

```
inert    | Zorglub attack Mack     | "There is no 'Zorglub' in the order of battle, Sire."
EXECUTED | Zorglub crush Mack      | ap 4->3  gold 800->512  battle_report  moved=[Davout,Lannes,Napoleon,Soult]
EXECUTED | Zorglub smash|destroy|annihilate|obliterate|rout|strike|defeat|fight|ambush Mack   — a real battle, all nine
EXECUTED | Zorglub occupy|capture|seize Swabia                                                — a real battle, all three
EXECUTED | Zorglub hunt|hound|intercept|harry|shadow Mack   | "Soult pursues Mack (at Swabia)…", 1 AP
EXECUTED | Zorglub pull back / Zorglub retire               | "General retreat ordered! Ney falling back! …" — eight corps, 0 AP
EXECUTED | Zorglub recon|reconnaissance|observe Swabia, Zorglub keep watch on Swabia | "Soult scouts Swabia…", 1 AP
inert    | Zorglub shell|barrage|cannonade Swabia           | masked at boot: "No artillery marshals available"
```

Rider (d) quotes the unbound name back as the order's own record:
*"Soult pursues Mack … **"Zorglub hunt Mack."** It will be done exactly, Sire."*

---

## 2. Shipped by row CX? NO — settled against the verbatim pre-row function

Two independent checks, not one:

* `_ADDRESSEE_IS_AN_ORDER_RE` is **byte-identical** at `b4a27a15^` and at
  HEAD. The row never touched it; it added a second *use* of it (the
  comma-less locator, `executor.py:1028`).
* `rL21_k_prerow.py` binds the **verbatim** pre-row `_unbound_addressee`
  (lifted from `git show b4a27a15^:backend/commands/executor.py`) onto the
  class and drives:

```
                                      PRE-ROW b4a27a15^     SHIPPED 727cf88a
  Zorglub crush Mack                  ok (executes)         ok (executes)     <- the hole, unchanged
  Zorglub attack Mack                 ok (executes)         REFUSED           <- the row's fix
```

The row's flip lever agrees (`rL21_b_lever.py`): every uncovered verb executes
at **both** lever positions. **Row CX narrowed this hole and created none of
it.**

## 3. Player-reachable? YES — 135 of 135

`rL21_j_client.py` is a port of `main.gd::_redirect_diplomatic_command` whose
tables are **read out of `main.gd` at run time**, so it cannot drift from the
file it claims to mirror (`NO_HOME=18, WAR_ROOM=2, FAMILY=115, NATION_ANY=13,
ADVISORY=7`), with a sensitivity arm (3/3 known-diplomatic sentences redirect).

> 27 missed verbs × 5 names (`Zorglub`, `Berthier`, `Grouchy`, `Wellington`,
> `Nay`) = **135 sentences, 0 intercepted, 135 sent verbatim to the backend.**

---

## 4. Severity P1 — UPHELD, with the mitigations on the record

**For P1.** It fires on names **the game itself prints** (`rL21_c_realistic.py`):

```
  Berthier crush Mack     -> a real battle   (the chief of staff, named in every dispatch)
  Grouchy  crush Mack     -> a real battle   (on the Commission bench)
  Suchet   crush Mack     -> a real battle
  Nay      crush Mack     -> a real battle   (one keystroke from Ney)
  Wellington / Blucher / Berthier / Grouchy / Suchet  pull back
                          -> GENERAL RETREAT, eight corps, 0 AP, no confirm
```

Each is the *same harm* the row itself rated **P1** as CX-1b, one word over,
and the retreat arm is irreversible and army-wide at zero cost.
`Davoust`/`Soolt` are correctly repaired by FA-80; `Mack` is correctly caught
by the enemy-marshal gate — so the guard is the only thing standing here.

**Against P1, recorded honestly.** It is **pre-existing**, not a regression;
and **the game teaches none of the 27 verbs** — I grepped every surface that
teaches a command (`counsel.py`, `clarification.py`, `meta_executor.py`'s
COMMAND REFERENCE, `question_desk.py`, and all of `scripts/*.gd`): every hit is
a code comment or prose (`attack - Engage enemy forces or capture region`).
**CX-3's rule — the game must not offer a sentence it cannot read — is NOT
breached.** The player must supply the synonym unprompted, and the comma form
(`Berthier, crush Mack`) is refused correctly.

Net: P1 stands on harm and on the project's own precedent, but it is a
**pre-existing P1 the player walks into, not one the game leads them into.**

---

## 5. ⛔ THE CENSUS IS WRONG IN ALL THREE FIGURES

The finding says *"of the 36 verbs routing to a marshal-less type, the regex
covers 8 and misses 28."* I did my own census **at the real call site** — a spy
on `_unbound_addressee` recording the `command["type"]` the **executor**
actually sees, while driving `Zorglub <verb> <obj>` through `POST /command`
(`rL21_i_spy.py`). My first attempt read the type from a standalone
`parser.parse()` and got `type=None` for eleven verbs the end-to-end drive had
already shown executing — **a harness artifact, and I discarded it.**

| | finding | measured |
|---|---|---|
| routed to a marshal-less type | 36 | **40** |
| covered by the regex | 8 | **13** |
| missed | 28 | **27** |

* **The "covered 8" omits six real members** — `retreat`, `withdraw`,
  `fall back`, `scout`, `reconnoitre`, `reconnoiter` are all in the regex AND
  routed, and all four I drove are refused (`Zorglub withdraw`,
  `Zorglub fall back`, `Zorglub scout Swabia` → *"There is no 'Zorglub'…"*).
* **`charge` is in the finding's "covered" list but is not routed** —
  `type=specific` ("Charge requires a marshal"), so it is not part of this hole
  in either direction.
* **`conscript` is in the finding's "missing" list but is not routed** either
  (`type=specific`).
* **The finding's own missing list has 27 entries while its prose says 28**, and
  it omits `intercept` — which its own drive table uses.
* **The sub-claim "all 18 refusals are on `attack` or `retreat`" is FALSE.**
  `withdraw`, `fall back`, `scout`, `reconnoitre` and `reconnoiter` are refused
  too. It is an artefact of the 24 order forms that sweep happened to pick.

Three of the 27 (`shell`, `barrage`, `cannonade`) are artillery-masked at boot,
so the live-at-boot count is **24 executing**.

---

## 6. ⛔ THE FINDING MISSES ITS OWN MIRROR — the same gap is a FALSE REFUSAL

`_ADDRESSEE_IS_AN_ORDER_RE` is read at **two** sites. The lens only looked at
the new one.

```
site (1) executor.py:1028  the comma-less LOCATOR              <- NEW in CX-1
site (2) executor.py:1046  "is the phrase itself an order?"    <- FA-22, runs in BOTH arms
```

Site (2) is what keeps `attack Bern, then hold your positions` working. With the
verb list one-verb-wide there too, the **same 27 verbs** produce the opposite
defect — a legitimate compound order refused as an unknown officer
(`rL21_d_site2.py`, **25 of 31 probed**):

```
  crush Mack, then hold your positions -> "There is no 'crush Mack' in the order of battle, Sire."
  occupy Swabia, then hold             -> "There is no 'occupy Swabia' in the order of battle, Sire."
  pull back, then fortify              -> "There is no 'pull back' in the order of battle, Sire."
  retire, then fortify                 -> "There is no 'retire' in the order of battle, Sire."
  recon Swabia, then fortify           -> "There is no 'recon Swabia' in the order of battle, Sire."
  (controls: attack / bombard / scout / retreat / pursue + ", then …"  all ok)
```

`retire, then fortify` names **nobody at all** and is told an officer called
"retire" does not exist. Pre-existing too (identical against the verbatim
pre-row function, §2). This matters for the build: **the defect is
bidirectional, and one widened alternation closes both** — which makes the
finding's fix shape *more* valuable than it was filed, not less.

---

## 7. Would the suggested fix ship a regression? PARTLY — and not where you'd look

I built the finding's own fix shape (derive from `attack_vocabulary`'s four
sets + the mock chain's retreat/scout words), monkeypatched it, and measured.

**Where it does NOT regress — measured, with a sensitivity arm:**

* `rL21_f_corpus.py`: **0 predicate changes across 813 recorded utterances**
  (golden corpus + every `tools/playtest_scripts/*.json` string + every quoted
  command in the four row-CX / FA-slice-1 test files). ⚠ My first version of
  this scan returned 0 **vacuously** — it read `cmd["type"]` from the wrong
  dict, so all 813 were `type=None`; the sensitivity arm caught it
  (`rL21_f_selftest.py`, known positives must DIFF), I fixed the probe against
  `executor.py:1262` (`command = parsed_command.get("command", {})`), and the
  re-run is still 0 **with the arm live**. ⚠ Note the golden corpus is **not**
  a gate for this at all: it stops at `CommandParser.parse` and the predicate
  lives in the executor.
* Site (1) closes and site (2) opens, exactly as intended
  (`rL21_e_fix.py --fix`: 7/7 holes refuse, 6/6 mirrors execute).

**Where it DOES regress — the finding's own L2-5, multiplied by 27 verbs:**

`rL21_e_fix.py`, 26 natural sentences, **0 false refusals shipped → 8 with the
fix**:

```
  quickly crush Mack     -> "There is no 'quickly' in the order of battle"
  immediately pull back  -> "There is no 'immediately' …"
  cavalry crush Mack · artillery shell Swabia · ok crush Mack
  finally occupy Swabia  · tonight retire · urgently hunt Mack
```

⚠ **So the fix shape is sound but must NOT land alone.** L2-1's edit widens the
LOCATOR, and `_NOT_AN_ADDRESS_RE` asks *"does the run CONTAIN grammar?"* instead
of *"is its HEAD grammar?"* — so every verb added to L2-1 adds a new class of
false refusal. **L2-1 and L2-4 are one edit, and the finding files them as
two.** That dependency is not stated on L2-1 and should be.

**⚠ A pin I first blamed on the fix, and was wrong about.**
`tests/test_fa_slice1_the_two_words_2026_09_02.py` went 155→154 under the fix
and I nearly filed it. The control kills it: **baseline failed 1 of 4 runs with
no fix applied; the fix passed 4 of 4.**

```
  BASELINE x4 : 155 passed | 1 failed, 154 passed | 155 passed | 155 passed
  FIX      x4 : 155 passed | 155 passed | 155 passed | 155 passed
```

`TestTheSecondClauseNeverSuppliesTheAction::test_the_first_order_is_the_one_carried`
is **pre-existing flaky on unseeded combat RNG** (it failed on two *different*
parametrize cases across my runs). Driving all 116 quoted commands in that file
both ways, baseline-vs-baseline differs on **26** lines and baseline-vs-fix on
**22** — my own probe's noise is larger than the fix's effect — and there are
**zero** refusal-column differences. Worth its own row; not this one's.

---

## 8. What I checked and found clean

* The spec's §3.1 does not state a false fact — it says *"the leading run of
  words BEFORE the first order verb"* and never claims the verb list is
  complete. The finding's *"the record over-claims"* is fair but soft: the
  honest charge is that the limit is **unnamed**, which GR9 requires.
* `Davoust`/`Soolt` repair to Davout/Soult (FA-80) on both the covered and the
  uncovered verb; `Mack <any verb>` is caught by the enemy-marshal gate.
* `Berthier, crush Mack` (with the comma) is refused correctly — the hole is
  strictly comma-less + uncovered-verb.

---

## 9. Recommended disposition

**File it, at P1, as PRE-EXISTING, with the census corrected to 40/13/27 and
the mirror (§6) folded in as the same row.** Build it as one edit with L2-4's
head-token predicate — never alone — and gate it with the drift census the
lens asks for, which must be **mutation-tested** and must count the verb at the
**executor's** call site, not at `parser.parse` (that is the exact trap that made
my own first two probes vacuous).
