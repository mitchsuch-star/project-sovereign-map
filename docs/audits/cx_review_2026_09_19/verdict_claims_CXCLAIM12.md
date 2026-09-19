# VERDICT:CX-CLAIM-12 — **NARROWED**: the headline survives, the correction does not

> **NARROWED — the gate does intercept beyond the 114, but the claim's own
> correction adds 18 forms the gate is built to NOT intercept, omits 28 more
> exemptions, and its table does not sum to its own total.**

**Filed by** lens "claims", severity **P4**, `player_reachable: false`,
`shipped_by_this_row: true`.

**My verdict:** **NARROWED.** Severity **held at P4** (a true one-word prose
imprecision survives). `player_reachable: false` — **confirmed by measurement.**
`shipped_by_this_row: true` for the *prose* — **confirmed**; the *gate* is
**PRE-EXISTING and byte-stable across all six CX commits.**

⛔ **The filed correction must NOT be applied.** Publishing "152+" would put a
figure in the spec that a committed, passing test (`test_the_no_home_verbs_are_
never_intercepted`) asserts is impossible, and would contradict the cell
**directly beneath it in the same table**.

---

## 0. WHAT I RAN

Read-only, tree clean. ⚠ **Note on the stated SHA:** the task says the tree is at
`727cf88a`; `git log` reads **`f52df77f`** ("docs(cx): correct the row's own
headline figure"), a seventh CX commit on top. Every figure below is measured at
`f52df77f`, and probe 5 re-measures at all eight SHAs including `727cf88a` —
**nothing in this verdict moves between them.**

Instrument: **the project's own committed port of the client gate** —
`tests/test_wo_slice7_cabinet_door.py::_redirect_verdict` + `_extract_gd_list`,
the drift pin's own functions. I deliberately did not hand-roll a third
classifier; the whole point of the WO-D2 design is that the port IS the mirror.

| probe | question |
|---|---|
| `probes/refute_claim12/q1_counts.py` | every list the gate reads; the claim's own arithmetic |
| `probes/refute_claim12/q2_true_count.py` | is the family list 114 or 115? |
| `probes/refute_claim12/q3_sign.py` | **drive the gate**: which lists make it FIRE, which make it STAND DOWN |
| `probes/refute_claim12/q4_subtractive.py` | measure the sign of each list by flipping it off |
| `probes/refute_claim12/q5_provenance.py` | list sizes at all 8 SHAs, pre-row → HEAD |
| `probes/refute_claim12/q6_precedence.py` | is the no-home precedence load-bearing on the shipped corpus? |

---

## 1. THE ONE THING THAT DECIDES IT — **0 of 18**

The claim's table adds `DIPLO_NO_HOME_KEYWORDS` (18) into a total of
**intercepted** forms. I built one natural sentence per keyword and drove the
gate (`q3_sign.py` part A):

```
SENT (fail-open)     set war purpose against Austria
SENT (fail-open)     war purpose against Austria
SENT (fail-open)     set objective against Austria
SENT (fail-open)     declare purpose against Austria
SENT (fail-open)     set war goal against Austria
SENT (fail-open)     repudiate bargain with Austria
SENT (fail-open)     repudiate the bargain with Austria
SENT (fail-open)     break bargain with Austria
SENT (fail-open)     renounce bargain with Austria
SENT (fail-open)     cancel bargain with Austria
SENT (fail-open)     void bargain with Austria
SENT (fail-open)     make amends with Austria
SENT (fail-open)     offer amends to Austria
SENT (fail-open)     amends with Austria
SENT (fail-open)     amends to Austria
SENT (fail-open)     repair relations with Austria
SENT (fail-open)     offer reparations to Austria
SENT (fail-open)     send reparations to Austria

  -> intercepted 0 of 18
```

**The sign is backwards.** `_redirect_diplomatic_command` reads that list at
`main.gd:2036` and the body is `if keyword in lower: return false` — *"The
no-home verbs keep their typed route, checked FIRST exactly as the parser checks
them first."* These are **exemptions**. They are the forms the gate exists to let
through, and they are 18 of the 38 the claim says the row understates by.

And they are not merely neutral. With the guard removed (`q4_subtractive.py` part
b) the family list claims **7 of 7** compound probes that the guard rescues:

```
guard on: SENT   guard off: cabinet | set war purpose: war against Austria
guard on: SENT   guard off: cabinet | make amends and propose peace to Austria
guard on: SENT   guard off: cabinet | break bargain and break treaty with Austria
guard on: SENT   guard off: cabinet | declare purpose before we declare war on Austria
   … 7 of 7
```

So the list **SUBTRACTS**. The claim adds it.

---

## 2. AND IT OMITS 28 MORE EXEMPTIONS, BY ITS OWN LOGIC

The claim's stated method is "the function gates on six lists plus two extra
rules". Applied honestly, that method must also count the three exemption lists
it never mentions — all read by the same function, all making it stand down
(`q3_sign.py` part C, `q4_subtractive.py` part c):

```
SENT   Talleyrand, attack Prussia                (address_exempt: attack)
SENT   Talleyrand, assess our situation          (address_exempt: assess)
SENT   what would it take to make peace with Prussia  (advisory_starts: what)
SENT   why did Austria declare war on us         (advisory_starts: why)

exempt list removed -> 4 of 4 flip SENT -> INTERCEPTED
```

**Measured sign of every list the gate reads** (`q4_subtractive.py` part d):

| list | n | sign |
|---|---|---|
| `DIPLO_FAMILY_KEYWORDS` | 114 | ADDITIVE |
| `DIPLO_WAR_ROOM_KEYWORDS` | 2 | ADDITIVE (war table, not Cabinet) |
| `DIPLO_NATION_ANYWHERE_KEYWORDS` | 13 | ADDITIVE (gated on a court) |
| `DIPLO_NATION_GATED_PREFIXES` | 2 | ADDITIVE (gated on a court) |
| `DIPLO_AUTONOMY_VERBS × LEVELS` | 9 | ADDITIVE |
| `DIPLO_ADDRESS_NAMES` | 6 | ADDITIVE (a *route*, not a verb list) |
| `DIPLO_COURT_WORD` | 1 | ADDITIVE |
| cede/grant + `" to <court>"` | 1 | ADDITIVE |
| **`DIPLO_NO_HOME_KEYWORDS`** | **18** | **SUBTRACTIVE ← the claim adds it** |
| **`DIPLO_ADDRESS_EXEMPT_WORDS`** | **20** | **SUBTRACTIVE ← omitted** |
| **`DIPLO_ADVISORY_STARTS`** | **7** | **SUBTRACTIVE ← omitted** |
| **`DIPLO_COURT_EXCEPTION`** | **1** | **SUBTRACTIVE ← omitted** |

**additive 148 · subtractive 46.**

One witness per additive rule, all measured firing (`q3_sign.py` part D):
`declare war on Austria`→cabinet · `request terms`→war_room · `court Bavaria`→
cabinet · `make Holland a puppet`→cabinet · `invest in Bavaria`→cabinet ·
`guarantee Bavaria`→cabinet · `send the envoy to Bavaria`→cabinet ·
`cede Tyrol to Bavaria`→cabinet.

---

## 3. THE CLAIM'S TABLE DOES NOT SUM TO THE CLAIM'S OWN TOTAL

`q1_counts.py` part B. Every individual count the claim states is **correct**
(18 / 13 / 2 / 2 / 3×3) — but:

```
the claim's own six rows sum to : 158
the claim PUBLISHES the total as: 152+        (off by 6)
"understates by ~38 forms" (152-114=38); on its own rows it would be 44
```

`152` is reachable only by summing `114+18+13+2+2+3` — i.e. by counting
`DIPLO_AUTONOMY_VERBS` as 3 while the same line says the forms are `3 × 3 = 9`.
The claim's arithmetic is internally inconsistent on its own printed rows.

---

## 4. "114" IS CORRECT — AND THE COMMITTED PIN IS THE THING THAT SAYS 115

`q2_true_count.py`. The project's own extractor returns **115**:

```
naive quote scrape (the committed pin's method) : 115
real list ENTRIES (non-comment lines)           : 114
quoted strings living inside COMMENTS           : 1
   -> ['break the alliance with Austria']
```

`_extract_gd_list` regex-scrapes `"…"` from the whole block, and the WO-slice-11
comment inside `DIPLO_FAMILY_KEYWORDS` contains the sentence
`"break the alliance with Austria"` — violating the block's own stated
convention (*"One double-quoted string per line: the pin regex-extracts them"*).

**Behaviourally harmless**: the phantom entry is a strict superstring of the real
entry `break the alliance`, so it can never claim a sentence the real one does
not. It inflates the pin's *count* by exactly 1, nothing else.

**The row's "114" is the right number for the list it names.** The claim
conceded this ("correct"), and it is — but only because the lens counted entries
rather than trusting the committed extractor.

---

## 5. PROVENANCE — THE PROSE IS THE ROW'S, THE GATE IS NOT

`q5_provenance.py`, straight from `git show <sha>:<path>`, all eight SHAs:

```
commit               FAMILY  NO_HOME  NATION_ANYWHERE  ADDR_EXEMPT  ADVISORY
f7008582 PRE-ROW     114     18       13               20           7
b4a27a15 CX-1        114     18       13               20           7
5fc3d5c8 CX-2        114     18       13               20           7
2c3535b5 CX-3        114     18       13               20           7
704df816 records     114     18       13               20           7
c73749c3 CX-5        114     18       13               20           7
727cf88a CX-6        114     18       13               20           7
f52df77f HEAD        114     18       13               20           7
```

**The gate is byte-stable across the entire row.** Row CX did not build it; it
described it. The three prose sites are new in the row —
`COMMAND_EXPERIENCE_SPEC.md:66` in `b4a27a15`, and
`CX_THE_HAND_ON_THE_KEYBOARD…:70`/`:232` + `SYSTEMS_REFERENCE.md:5909` in
`704df816` — and `git grep` at `f7008582` finds the figure stated **nowhere**
before the row. So `shipped_by_this_row: true` stands, scoped to the prose.

---

## 6. PLAYER-REACHABLE: **NO** — confirmed

* no player-facing string anywhere states the figure (`grep` over `main.gd` and
  `backend/game_logic/` → empty);
* **no test pins it** (`grep -rn 'intercepts 114\|114 keyword' tests/` → empty);
* it appears in exactly three prose lines, all in `docs/`.

A player cannot reach this. It is a documentation-accuracy item and nothing else
— which is why P4 is the right ceiling and why I did not raise it.

---

## 7. WOULD THE SUGGESTED FIX SHIP A REGRESSION? **YES — a documentation one, and it contradicts the cell beneath it**

The claim says the row "**understates** the client's interception by ~38 forms",
i.e. publish ~152. Applying that:

1. **It contradicts a committed, passing test.**
   `tests/test_wo_slice7_cabinet_door.py:416`
   `test_the_no_home_verbs_are_never_intercepted` asserts
   `_redirect_verdict(utterance, …) == ""` for `make_amends`,
   `set_war_purpose`, `repudiate_bargain`. I ran it: **8 passed**. A doc that
   counts those 18 as intercepted asserts the opposite of a green pin.

2. **It contradicts the spec's own adjacent cell.** Same table, the row directly
   below the "114" cell (`COMMAND_EXPERIENCE_SPEC.md:67`):

   > **sole road** | move, march, retreat, hold, support, garrison,
   > **set war purpose**, cancel, and every question

   The spec already records the exemption correctly. The "fix" would make the
   table say, two lines apart, that `set war purpose` is both intercepted and a
   sole typed-road verb.

3. **It would still be the wrong number** — 152 by neither route (158 on the
   claim's own rows, 148 measured additive).

4. It would also read as a **design** claim the code contradicts: §2 G1-11
   records those three verbs as having no wizard home, so redirecting them
   *"would make them unreachable outright"*.

**What I would actually change** — the surviving kernel, one word:

> `_redirect_diplomatic_command` intercepts **the family's** 114 keyword forms …

or, if a total is wanted, **"148 additive forms across eight rules, of which the
114-entry family list is the bulk"** — never a sum that includes the exemptions.

---

## 8. TWO SIDE-FINDINGS, FOUND BY ATTACKING THE FIX (both INFO, neither is the verdict)

**(a) The committed drift pin carries a phantom 115th keyword** (§4). Harmless
behaviourally; it does mean any future count read off `_extract_gd_list` is one
high, and the block comment's own "one double-quoted string per line" rule is
broken by the line that says it.

**(b) `test_the_no_home_verbs_are_never_intercepted` is INERT with respect to the
list it exists to protect.** Its docstring says:

> Note `set war purpose against Austria` carries the war-declaration substring
> `war against ` — **precedence, not luck, is what saves it.**

Measured (`q4_subtractive.py` part a): `'set war purpose against austria'
contains 'war against '` → **False**. The phrasing carries `war purpose against`,
not `war against`. And on the shipped corpus (`q6_precedence.py`) all three rows
the test iterates are SENT with the **entire 18-entry no-home list deleted**:

```
[make_amends      ] 'make amends with Prussia'              family keywords: NONE
[set_war_purpose  ] 'set war purpose against Austria'       family keywords: NONE
[repudiate_bargain] 'repudiate the bargain with Austria'    family keywords: NONE
3 corpus rows; 0 would be claimed without the guard.
```

So the pin passes identically whether the guard exists or not — it proves the
verbs reach the backend, not that precedence saves them. The project's own
recorded lesson applies verbatim: *a sweep proves a pin binds, not that it is
about the right thing.* The compound sentences in §1 are where precedence is
genuinely load-bearing, and nothing pins those. **This is pre-existing (the pin
predates row CX) and belongs to WO slice 7, not here.**

---

## 9. SCOREBOARD

| the claim's assertion | verdict |
|---|---|
| `DIPLO_FAMILY_KEYWORDS` has exactly 114 members | ✅ **reproduces** (entries; the committed extractor says 115 — §4) |
| the gate reads six lists + two extra rules, not one | ✅ **reproduces** — eight additive rules in all |
| "114 is the size of one list, not the gate" | ✅ **the headline survives** |
| the six lists total **152+** | ❌ **wrong** — own rows sum to 158; measured additive 148 |
| the row **understates by ~38 forms** | ❌ **wrong** — 34 additive, and 18 of the claimed 38 are exemptions |
| `DIPLO_NO_HOME_KEYWORDS` (18) is part of the interception | ❌ **REFUTED — 0 of 18 intercepted; the sign is backwards** |
| (unstated) the gate's exemption lists are accounted for | ❌ 28 more omitted by its own method |
| `player_reachable: false` | ✅ **confirmed** |
| `shipped_by_this_row: true` | ✅ **confirmed for the prose**; the gate is pre-existing and byte-stable |
| severity P4 | ✅ **held** |

**NARROWED.** A real one-word prose imprecision survives. The correction offered
for it is wrong in composition, in magnitude and in its own arithmetic, and
applying it would contradict both a green test and the spec's own next line.
