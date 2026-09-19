# VERDICT:CX5-L5-F4 — **NARROWED** (P3 → P4)

Tree `master 727cf88a`, clean, nothing under the repo modified. Everything
below was measured by my own probes, on the shipped 1805 board
(`parser_eval.build_world("1805")`), `LLM_MODE=mock`, one fresh board per
utterance, driven at `POST /command` through `TestClient`. Attribution is
always by flipping `llm_client.A_RETREAT_CAN_BE_A_NOUN` and re-measuring the
SAME utterance, never by reading the diff.

My probes: `probes/verdict_retreat_f4.py`, `verdict_f4_escalation.py`,
`verdict_f4_mid_retreat.py`, `verdict_f4_fixtest.py`, `verdict_f4_confirm.py`,
`verdict_f4_family.py`, `fixa_plugin.py`.

---

## THE CORE MECHANISM REPRODUCES, AND ROW CX SHIPPED IT

`_RETREAT_NOUN_RE` carries `|\bretreating\b` as an unconditional alternative
(`llm_client.py:761`) under a comment asserting the participle *"is always
adjectival"*. It is also the progressive verb, and `_ORDER_THE_RETREAT_RE`
requires a determiner a bare participle never has. So the continuative
`-ing` order falls out of the retreat branch and lands in the shrug.

Driven end to end, both arms:

```
Ney, keep retreating       PRE retreat/0.9 -> HEAD REFUSED
Ney, continue retreating   PRE retreat/0.9 -> HEAD REFUSED
Ney, go on retreating      PRE retreat/0.9 -> HEAD REFUSED
Ney, resume retreating     PRE retreat/0.9 -> HEAD REFUSED
```

`Ney, keep retreating` at HEAD: AP 4→4, nothing moves, *"Berthier frowns at
the dispatch. 'I see Marshal Ney's name, Sire, but the instruction is
unclear…'"* With the lever down, the same sentence on the same board:
*"Ney bristles at the retreat order but obeys. Ney retreats from Rhineland to
Lorraine. Army begins recovery (currently at −45% effectiveness)."*

**Player-reachable: YES.** I checked all six client redirect lists in
`main.gd`. None of these phrasings hits `DIPLO_NO_HOME_KEYWORDS`,
`DIPLO_WAR_ROOM_KEYWORDS`, `DIPLO_FAMILY_KEYWORDS`,
`DIPLO_NATION_ANYWHERE_KEYWORDS` or `DIPLO_ADVISORY_STARTS`; the only hit is
in `DIPLO_ADDRESS_EXEMPT_WORDS`, which is an *exemption*. The sentence
reaches the backend unchanged.

So: **real, shipped by row CX, reachable.** Everything else about the row is
over-stated, and the prescribed fix is half-regressive.

---

## 1. "EVERY CONTINUATIVE RETREAT ORDER IS REFUSED" IS FALSE — MEASURED

The engine has four retreat spellings. **One regressed** (`probes/verdict_f4_family.py`):

```
keep / continue / go on RETREATING     PRE retreat/0.9 -> HEAD REFUSED   <- regressed
keep / continue / go on WITHDRAWING    PRE retreat/0.9 -> HEAD retreat/0.9  (untouched)
keep FALLING BACK / PULLING BACK / RETIRING   REFUSED in BOTH arms (pre-existing)
continue|resume THE RETREAT / THE WITHDRAWAL  retreat/0.9 in BOTH arms
```

`keep withdrawing` — the same continuative, the same meaning, one verb over —
**works at HEAD**, because `_RETREAT_NOUN_RE` names `withdrawal|withdrawals`
and never `withdrawing`. `keep falling back` and `keep pulling back` are
refused with the lever in *either* position: pre-existing, nothing to do with
row CX.

And the army-wide road is fully intact at HEAD: `retreat`, `general retreat`,
`all marshals retreat`, `everyone retreat`, `order a general retreat` all
still parse `retreat/0.8/general_retreat`, identically in both arms.

**One member the finding missed**, same lever, same board: `Ney, keep up the
retreat` → `retreat/0.9` → REFUSED. That is an F3 member (a carry-out verb
absent from the allowlist), not an F4 one.

## 2. THE CONFIDENCE FIGURES ARE WRONG

The row states *"All eight were `retreat / 0.9` pre-CX-5."* Measured pre-CX-5
on the shipped board: **0.9 with Ney addressed, 0.55 with Lannes addressed,
0.8 for the seven bare unaddressed ones.** The direction holds; the figure
does not.

Related, and it changes the harm story: **seven of the eight filed utterances
are unaddressed**, and pre-CX-5 each one fired a **general retreat of the
entire army** — Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena and
Napoleon all falling back at −45% for three turns, free, at 0.8, above the
escalation gate. For those seven, what CX-5 removed is a two-word bare phrase
that routed the Grande Armée; the addressed single-marshal case
(`Ney, keep retreating`) is the one that reads as a clean loss.

## 3. THE SEVERITY QUALIFIER THE ROW APPLIED TO F3 AND NOT TO F4

Measured on the raw `ParseResult` with a simulated live client
(`probes/verdict_f4_escalation.py`, threshold 0.7):

```
HEAD  Ney, keep retreating    action=unknown  conf=0.5  refusal=None  escalates=True
PRE   Ney, keep retreating    action=retreat  conf=0.9  refusal=None  escalates=False
```

Every one of these refusals lands at **0.5 with `refusal=None`**, so
`_should_fallback_to_llm` returns **True** — with a key the sentence
escalates and a live player very likely gets the retreat. **The regression is
mock-only**, which is the launcher default for a keyless tester, and is
exactly the qualifier F3 states about itself. F4 omits it.

## 4. THE REACHABILITY ARGUMENT, MEASURED ON THE ORDINARY CASE

The row's reachability argument is that the game prints `RETREATING
(stage: N)`. I staged that board — Ney with `retreating=True`,
`retreat_recovery=1`, the card reading RETREATING — and drove it in three
states, both arms (`probes/verdict_f4_mid_retreat.py`):

```
A  same turn he retreated       HEAD shrug   |  PRE "Ney has already retreated this turn."
B  next turn, still in danger   HEAD shrug   |  PRE retreats Rhineland -> Lorraine   <- the real loss
C  next turn, NOT in danger     HEAD shrug   |  PRE "Ney is not in danger. Use 'move'."
```

**In two of the three states the pre-CX-5 order was also refused**, and what
regressed there is the *quality of the refusal* — an honest, diagnostic
message replaced by a shrug — not the ability to retreat. Only arm B loses an
order. In all three, `Ney, continue the retreat` and `Ney, retreat` work at
HEAD.

And the CX-3 census is **not** breached. The predictor's `_MARSHAL_VERBS`
(`main.gd:6892`) teaches `retreat`, which works; `RETREATING` is a *status
label* (`marshal_management.gd:600`, `ledger.py:219`), not an order the game
offers. "The game must not offer a sentence it cannot read" does not bind
here.

## 5. ⛔ THE SUGGESTED FIX SHIPS A WORSE REGRESSION — AND NO PIN SEES IT

The finding prescribes two rules. I built both and measured them
(`probes/verdict_f4_fixtest.py`, `verdict_f4_confirm.py`):

| utterance | PRE-CX5 | **SHIPPED** | **FIX-A** (following noun / preceding determiner) | **FIX-B** (continuative auxiliary) |
|---|---|---|---|---|
| `Ney, march to Swabia, the enemy is retreating` | retreat/0.9 | **move/0.9** | **retreat/0.9** ⛔ | move/0.9 |
| `Ney, our men are retreating` | retreat/0.9 | **REFUSED** | **retreat/0.9** ⛔ | REFUSED |
| `Ney, the Austrians are retreating` | retreat/0.9 | **REFUSED** | **retreat/0.9** ⛔ | REFUSED |
| `Ney, Mack is retreating` | retreat/0.9 | **REFUSED** | **retreat/0.9** ⛔ | REFUSED |
| `Lannes, ride down the retreating Austrians` (pin) | retreat/0.55 | REFUSED | REFUSED | REFUSED |
| `Lannes, pursue the retreating enemy` (pin) | attack | attack+fights | attack+fights | attack+fights |
| `Ney, keep retreating` | retreat/0.9 | REFUSED | retreat/0.9 ✓ | retreat/0.9 ✓ |

**FIX-A — the finding's first clause — reverts four HEAD behaviours to the
pre-CX-5 defect at confidence 0.9, which is ABOVE the escalation gate, so no
key in any mode can correct them.** One of the four is *the row's own
recorded win* (`the enemy is retreating` stops turning a march into a rout);
driven, the march goes from AP 4→3 to AP 4→4 because the retreat branch
reclaims it. The other three are the bare report `X is retreating` routing
the addressed corps — a fresh instance of exactly the defect CX-5 exists to
close.

**And the standing instrument is blind to all of it:** under FIX-A the CX-5
pin class is **33/33 green** (`pytest -k "Retreat or retreat" -p fixa_plugin`)
and the golden corpus is **688/688**, byte-identical to shipped. So FIX-A
would land with everything green.

**FIX-B — the finding's second clause — is clean on every pin, on the
recorded win, on the corpus, and fixes exactly the filed family.** The
`Lannes, sound the retreat` difference I first saw between arms was objection
RNG, not the patch: the parse is identical, and I do not claim it.

**Recommendation to the owner: build clause two, never clause one.** Add a
continuative-auxiliary arm to `_ORDER_THE_RETREAT_RE`
(`\b(?:keep\s+on|go\s+on|keep|continue|start|begin|resume|stay)\s+retreating\b`)
and leave `_RETREAT_NOUN_RE` alone. Add `keep up` while there (§1). If it is
built, pin `Ney, our men are retreating` and `Ney, march to Swabia, the enemy
is retreating` — neither is pinned today, which is why FIX-A looks safe.

## 6. WHY P4 AND NOT P3

Real, shipped by this row, reachable — but: one of four spellings; a working
synonym one word away (`continue the retreat`, `keep withdrawing`); nothing
charged (AP 4→4 on every refusal); escalates with a key, so mock-only; the
army-wide road untouched; the game never offers the phrasing; and in two of
the three states where a player is actually looking at the word RETREATING,
the pre-CX-5 order was refused as well. Against F3 in the same report (15
verbs, the same mock-only qualifier) filed at P3, this is a step below.

## PRE-EXISTING, OUT OF SCOPE, RECORDED

⛔ **A cause I guessed and then measured wrong, recorded as wrong.** I first
wrote that `sound the general retreat` fails on a second adjective past the
`(?:\w+\s+)?` window. It does not: `_ORDER_THE_RETREAT_RE` matches it, and
`_retreat_is_a_noun` returns False. The real cause is one layer up and has
nothing to do with row CX — **bare `sound` fuzzy-matches to the marshal
Soult**:

```
sound the retreat              PRE and HEAD: REFUSED — "Did you mean 'Soult'? ('sound' not found)"
sound the general retreat      PRE and HEAD: REFUSED — same
Ney, sound the general retreat PRE and HEAD: retreat/0.9      (addressed, works)
```

Pre-existing, identical in both lever arms, WO-13's family. Worth one line on
the record because `sound the retreat` is the spec's own flagship carry-out
example and it only works when a marshal is addressed — but it is not F4's,
and it is not row CX's.
