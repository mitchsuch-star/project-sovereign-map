# FINAL AUDIT — VERIFICATION PASS, September 2, 2026

> **What this is.** The Final Whole-Game Audit
> (`FINAL_AUDIT_2026_09_01.md`, held at master `ccf5f111`) was published with
> **46 of its 128 filed rows UNVERIFIED** — three session usage limits killed
> the refuter pass and the ten pillar scorers. It was also named, in
> `STATUS.md` and `CLAUDE.md`, as the next build contract. This pass is
> inserted in front of that build to make the contract trustworthy: every
> filed row re-checked adversarially, the neighbourhoods swept for what the
> audit missed, and the prose read against the evidence.
>
> **Method.** Three fleets at master `15d128b3` (no code has changed since the
> audit SHA — verified: `git diff --name-only ccf5f111..HEAD` touches only
> `docs/`, `CLAUDE.md` and one stray file). Every row went to an adversarial
> verifier told to default to REFUTED; every Tier-A row then to an independent
> agent told to attack that verdict whichever way it went; every surviving row
> to a neighbourhood sweep. Six further agents reviewed the memo's own prose.
> The session lead verified the headline rows and all counts by hand,
> independently, and had the fleet check the lead's findings in turn.
>
> **Report-only for the game.** No production behaviour was changed. What
> changed is documentation: amendments in place, new rows filed, and the
> routing in `STATUS.md` / `CLAUDE.md` corrected to point here first.

## 0. The short answer

**The audit is safe to build from. It is not safe to build from verbatim.**

Of the 128 filed rows, **exactly one was refuted** — and a second refutation, on
FA-67, was itself over-broad and is adjudicated back to NARROWED here. A real
defect survives in **108 of 128 rows (84%)**. **All nine P1s are real.** The
audit's finders were accurate about *mechanism* to an unusual degree: where a row
says the code does X, it does X. Both headline parsing defects reproduce by hand
on the shipped mock-default build in under a minute, the §0 evidence table
reconciles exactly against the archived digests, and the machine record agrees
with the memo on all 128 rows with zero severity, kind or verdict mismatches.

What the pass found, in order of consequence:

1. **Half the rows need correction before a builder touches them** — 65 of 128
   came back NARROWED: the right defect, but a stale line number, an over-stated
   magnitude, a wrong seam, or a universality claim the body itself contradicts.
   This is the dominant failure mode and it is why *reproduce before fixing* has
   to be a hard rule, not advice.
2. **In six rows the `fix_shape` field prescribes the fix the row's own corrected
   summary rejects** (FA-54, FA-D13, FA-D18, FA-D24, FA-D25, FA-100). The memo
   warns about this for the *title*; the danger is in the field a builder
   actually executes.
3. **`already_filed` is the audit's least reliable field** (~44% wrong). It was
   written per-row by finders who could not see each other's work and was never
   reconciled after dedupe, so rows assert "NEW" while duplicating a sibling *in
   the same audit* — five such pairs, both members born in the same commit.
4. **The memo's own §7 headline claim is false**, in a way that makes its
   recommended first build wider than "one call at one seam" (FA-N1, §5).
5. **UNVERIFIED did not mean lower quality.** Of the 46 rows nobody had tried to
   kill, **zero were refuted.** The status was a budget artefact, not a signal —
   exactly as the memo said it was.

Two boundaries worth stating plainly, because both cut against a tidier story:
the memo's **§0 evidence table is exact** but its **§1/§2 narrative is materially
looser** (four claims corrected here, including one that reports an allied
capital's loss as a French conquest); and **this pass hit the same usage limit
that crippled the audit**, losing 155 of 280 agents. Every row has a verdict, but
only 21 were cross-checked (§10).

## 1. What the verification found, row by row

**Every one of the 128 filed rows now carries a verdict.** 21 were cross-checked by a second, independent agent.

| | VERIFIED | NARROWED | DUPLICATE | REFUTED | n |
|---|---|---|---|---|---|
| **all filed rows** | 43 | 65 | 19 | 1 | **128** |

*A defect survives in **108 of 128 rows (84%)** — VERIFIED or NARROWED.*

**by original severity**

| | VERIFIED | NARROWED | DUPLICATE | REFUTED | n |
|---|---|---|---|---|---|
| P1 | 3 | 6 | 0 | 0 | 9 |
| P2 | 14 | 22 | 5 | 0 | 41 |
| P3 | 19 | 32 | 12 | 0 | 63 |
| P4 | 7 | 5 | 2 | 1 | 15 |

**by kind**

| | VERIFIED | NARROWED | DUPLICATE | REFUTED | n |
|---|---|---|---|---|---|
| defect | 28 | 31 | 10 | 1 | 70 |
| tie_in | 9 | 13 | 4 | 0 | 26 |
| harness | 4 | 16 | 5 | 0 | 25 |
| missing | 2 | 5 | 0 | 0 | 7 |

**by the status the audit published**

| | VERIFIED | NARROWED | DUPLICATE | REFUTED | n |
|---|---|---|---|---|---|
| UNVERIFIED | 12 | 27 | 7 | 0 | 46 |
| AUTHOR_VERIFIED | 14 | 8 | 2 | 1 | 25 |
| HARNESS (author-checked) | 4 | 14 | 5 | 0 | 23 |
| PLAUSIBLE | 9 | 8 | 2 | 0 | 19 |
| NARROWED | 4 | 8 | 3 | 0 | 15 |

**The three readings that matter:**

1. **Every one of the nine P1s is a real defect** — 3 VERIFIED, 6 NARROWED, none refuted and none a duplicate. The audit's top tier is trustworthy.
2. **UNVERIFIED was not a quality signal.** Of the 46 rows nobody had tried to kill, **zero were refuted** (12 VERIFIED, 27 NARROWED, 7 DUPLICATE). "Nobody tested it" turned out to say nothing about whether it would survive — exactly as the memo warned.
3. **Both refutations landed on AUTHOR-VERIFIED rows**, not on the fleet's. The session author's own hand-checks produced the audit's only two false positives — and one of those (FA-67) this pass re-adjudicated to NARROWED, because the refutation answered only half the row.

Harness rows fared worst as filed (4 of 25 VERIFIED), which is consistent with §3(a): they are claims about the instrument and its backlog rather than about game code.

### The one-line reading

**Nothing was refuted outright except one row, and that row is one of the three the
memo's own §7 recommendation rests on.** The audit's finders were accurate about
*mechanism* to a degree that is genuinely unusual: where a row says the code does X, it
does X. What they were not reliable about is everything *around* the mechanism — the line
number, the magnitude, the universality, and above all whether anybody had already filed it.

### The error modes, measured

Classified from what each verifier reported the row got wrong (a row can carry more than one):

| error mode | share of examined rows | what it means for a builder |
|---|---|---|
| **stale line number** | ~80% | The most common defect by far. Cited seams have drifted, sometimes by exactly the offset an earlier slice inserted. **Never navigate by the row's line number; navigate by the symbol it names.** |
| **over-stated magnitude** | ~50% | The mechanism is real; the number attached is bigger than the code can produce, or is measured on an unrepresentative arm. |
| **`already_filed` wrong** | ~44% | See §2 — the audit's least reliable field, by a distance. |
| **title over-reaches its body** | ~25% | FA-6 was the published example; it is a family, not a one-off. The body is usually right where the title is not. |
| **false universal** | ~12% | "every", "never", "only", "all" — the body often contradicts the title's quantifier. This is what caught the memo's own §7 headline (FA-N1). |
| **wrong seam in `fix_shape`** | ~8% | The mode that most deserves care: a builder following `fix_shape` verbatim edits the wrong function. |
| **`repro` does not run as written** | ~5% | Usually a missing setup line, not a fabricated repro. |

### The finding a builder should read first

**In six rows the `fix_shape` field still prescribes the fix that the row's own
refuter-corrected `summary` explicitly rejects** — FA-54, FA-D13, FA-D18, FA-D24, FA-D25,
FA-100. The memo's §6 standing rule anticipates the shape of this ("where a refuter left a
NARROWED note, the note is the truth and the title is not") but it **undercounts (six, not
two) and scopes the warning to the *title*** — the field a builder skims — rather than to
`fix_shape` and `behaviour_test`, which are the fields a builder actually executes.

A builder who reads the title, skips the corrected summary and implements `fix_shape` will,
in those six cases, build the thing the audit already knew was wrong.

## 2. `already_filed` is the audit's least reliable field

Roughly **44% of examined rows carry an inaccurate `already_filed` claim**, and the errors
run both ways: rows cite a row that is closed, miss the row that duplicates them, or assert
"NEW" while a sibling in *the same audit* covers the same seam.

**Fifteen rows came back DUPLICATE.** One cross-checker drew a distinction that changes how
they should be handled:

- Some duplicate a **pre-existing OPEN row** (FA-24 ≡ NPC-7, among others). Those are true
  duplicates — strike or merge.
- Others duplicate **a sibling filed in the same commit**: FA-62 ≡ FA-29, FA-66 ≡ FA-D21,
  FA-D14 ≡ FA-D13, FA-10 ≡ FA-74, FA-24 ≡ FA-48. `git blame` puts both members of these
  pairs in `adebd639`, the audit's own filing commit, so **neither has priority and
  "DUPLICATE" is the wrong word.** They are *merge candidates* — one defect the dedupe pass
  split into two rows.

**The mechanism is structural, not careless.** `already_filed` was written per-row by
sixteen finders who could not see each other's output, and the dedupe pass that followed
compared seams and titles but never rewrote the field. It records what one lens knew at the
moment it wrote, and was never reconciled against what survived.

**What to do with it:** treat `already_filed` as a hint, never a clearance. Before building
any row, grep `BUG_FIXES.md` and `DESIGN_REFINEMENT.md` for its seam — including the other
FA rows.

## 3. What the audit got wrong as a body of work

Four systematic biases, argued from content. The `lens` field is empty on all 130 rows, so
per-agent attribution is not recoverable and none of this is computed per-lens.

**(a) The finders read code better than they read the repository.** Mechanism claims are
near-flawless; claims about what is *already known* are wrong ~44% of the time. The audit
was built to find defects in the game and was not equipped to find defects in its own backlog.

**(b) Quantifiers were not verified.** "Only", "every", "never" appear as rhetorical
emphasis and survive into headline prose. The memo's single highest-leverage recommendation
rested on one — §7's "the only trust-writing seam" — and it was false. It was found not by
reading the row, which is careful and claims no such thing, but by reading the memo's
editorial framing of it.

**(c) Magnitude was measured on whichever arm was open.** Numbers are typically real but
drawn from the most extreme campaign, then stated generally. The narrative sections (§1, §2)
are materially looser than the evidence table (§0), which is exact.

**(d) The published verification status is not a quality signal — and the memo said so.**
UNVERIFIED rows verified at essentially the same rate as rows that had already survived a
refuter. "Nobody tried to kill it" turned out to say nothing about whether it would survive.
The memo was right to publish the status and right to warn against reading it as a grade.

**One bias in the audit's favour, worth stating because it is unusual:** the memo declines
to print a pillar score it did not measure, marks every unverified row, corrects its own
mid-session claim in §0.1 rather than deleting it, and keeps two killed hand-verified claims
on the record. Where it is wrong, it is wrong in the open.

## 4. What this pass got wrong

Published for the same reason. Two of the three hardest calls here were initially decided
wrong, both by measuring the wrong quantity instead of reading the stated one.

1. **FA-8's "48".** I measured the wrong metric, concluded the audit's most-quoted AI figure
   was unreproducible, and edited `STATUS.md` to say so. An independent prose reviewer
   reached the same conclusion by a different wrong route, offering five variants
   (105 / 69 / 85 / 59 / 58) and proposing 59 as a replacement. Applying **the row's own
   stated rule** — AI attacker lost ≥1,000 *and the French defender <1,000* — across all 231
   archived battles gives **exactly 48**. My edit is reverted; the reviewer's correction is
   not applied.
2. **FA-67.** A verifier returned REFUTED at high confidence and was right about half the
   row; I verified that half independently. But the refutation never addressed the row's
   second clause, which is correct. Adjudicated **NARROWED**.

Both failures have the same shape as the game defect the audit calls its through-line: the
right answer exists, and something downstream reports a different one.

## 5. New findings

### FA-N1 — §7's uniqueness claim is false, and its recommended first build is wider than "one seam"

**P2 · confidence HIGH · amended in place at memo §7 and in the three files that copied it.**

Memo §7 read: *"`world_state.py:6207` … is **the only** trust-writing seam in the backend
that does not consult `check_redemption_threshold`. Every other one does."*

An AST census over the whole backend covering **both** trust-write APIs — `modify_trust()`
**and** `marshal.trust.modify()`; a `modify_trust`-only grep misses the cavalry seams the
sentence itself cites — finds **49 trust writes, 16 negative, and four unchecked families,
not one**:

| seam | enclosing function | caller / turn coverage | verdict |
|---|---|---|---|
| `world_state.py:6207` | `_process_dotation_state` | `advance_turn` does not check | **unchecked** — this is FA-26 |
| `combat_executor.py:7316` | `_execute_attack` (4112-7348) | — | **unchecked**; sibling `_execute_bombardment` (3639-4047) checks at :3839 |
| `strategic_executor.py:1691` | `_handle_strategic_objection_response` (1645-1969) | typed route's caller `_execute_strategic_command` (454-1643) does not check | **unchecked on the typed route**; the endpoint route checks at :2502/:2657 |
| `jealousy.py:2717, 2832-2875` | `_apply_confrontation_choice`, `_apply_rivalry_choice` | `/marshal_petition_response`; **`jealousy.py` has ZERO checker calls** | **unchecked** (8 negative writes) |

The five families the memo *names* as covered are covered — the list is right, the
quantifier is not. There is no global per-turn sweep: the only all-marshal loop containing
the checker is `_check_cavalry_limits`, and it is cavalry-only.

**Two of the three additional families are unmaintained siblings of copies the memo cites as
covered** — the audit's own through-line, inside the row it recommends building first.

**FA-26's own row is clean and claims no uniqueness.** The over-claim is editorial, and it
had propagated to `BUG_FIXES.md`, `STATUS.md` and `CLAUDE.md`. All four are corrected.

**Effect on the build:** §7's *"one call, at one seam"* understates the work. The fix should
be a shared helper across all four families, or FA-26 will close the dotation arc and leave
a marshal rebuked in a confrontation, docked for refusing to reinforce, or penalised for an
insisted-on strategic order still rotting silently past trust 20. **The recommendation gets
better, not worse:** more marshals are affected than the memo claims — and the ambient
autosave confirms it, with three of France's seven marshals at trust 0 by turn 41, not the
one the memo named.

*Behaviour test:* an AST census pin over `backend/` asserting that every negative
`modify_trust` / `trust.modify` site sits on a call path to `check_redemption_threshold`,
with the four known families enumerated so the pin fails when a fifth appears.

<!--ADJACENT-->

## 6. Prose and cross-document corrections applied

All of the following were verified and **fixed in place** in this pass.

| # | where | was | now |
|---|---|---|---|
| 1 | memo §0.1 | "the two P1 parsing defects below" | names FA-7 (P1) and FA-6 (P2) |
| 2 | memo §1 | "two P1 exceptions" | "two exceptions … one of them a P1" |
| 3 | memo §8 | "the fleet's two P1 parsing claims" | "…both filed P1 at the time" |
| 4 | STATUS.md | "two P1s a first-time player hits" | "two defects … one a P1, one a P2" |
| 5 | CLAUDE.md | "Headline P1s, both…" | "The two headline parsing defects — one P1, one P2" |
| 6 | memo §1 | Lisbon evidence pointed at "(§6)" | "(§5)" |
| 7 | memo §1 | "Six joins … are in §7" | §7 holds one recommendation; the rest are §6's slices |
| 8 | memo §2 | petition claim cited "(FA-4)" | "(FA-5)" — FA-4 is the settlement-offer defect |
| 9 | memo §2 | bare "remnant FA-9," | "(FA-9)" |
| 10 | memo §6 | "59 of 128 rows / 16 unslotted / 17 FA-D outside" | **57 / 17 / 19**, all three re-measured |
| 11 | memo §3a | heading "Defects — P1 (9)" while holding a P2 | "(8, plus FA-6, downgraded to P2 …)" |
| 12 | memo §0 | vocabulary lists CONFIRMED with no members | notes that no row reached that bar |
| 13 | **15 dangling "finding N" refs across 9 rows** | per-lens private numbering, mechanically unresolvable (`lens` is empty) | every one resolved to a named row, in **both** the memo and the machine record |
| 14 | memo §7 + 3 files | "the only trust-writing seam" | FA-N1 amendment (§5) |
| 15 | memo §7 | FA-67 "no combat seam anywhere raises trust" | corrected — vindication grants +3 on a battle victory |
| 16 | memo §1 | "Lannes, trust 0" | three of France's seven — Lannes, Bernadotte, Massena |
| 17 | memo §2 | "Munich taken" | removed — Munich is **Bavaria's capital, France's ally**, and passed to Austria |
| 18 | memo §2 | "wins every battle it fights" | "wins every battle it starts until t19", when Murat is repulsed 4,328 to 807 |
| 19 | memo §2 | "Massena ground … to 41 men" | 21,067 → 32; the digest's "41" is one battle's casualties |
| 20 | memo §6 | slice 1 "all hand-reproduced, corpus rows exist for every phrasing" | **both false** — measured **0 of 345** corpus entries contain any deferral phrasing |
| 21 | memo §6 | slice 8 (the harness) ordered last | flagged, with a four-point ordering note |
| 22 | memo §5 | a working-well note asserting as working what FA-D17 files as a defect | annotated against FA-D17 |

Left for the owner because they change a claim rather than a number: the propose arm's
paradox refusals ("twice" vs seven in the digest), "France lays a keel every turn" (five
`build ships` in twenty turns), and "Paget walked ten French provinces in eight turns".
Separately, **"Lisbon" appears in none of the nine committed digests** though §1 and §5 both
name it — the claim is TRUE (seven console logs carry *"THE LANDING: Paget … puts 5,000 men
ashore at Lisbon"*), but its evidence lives only in gitignored logs, which the memo's own §0
standard ("a memo may only cite an archived digest") does not admit.

## 7. The build order, revisited

§6's eight slices are **thematically sound** and all nine P1s are covered. Four problems,
now recorded as an ordering note in the memo itself:

1. **Slice 8 — the harness — is scheduled last, and it is the instrument every other slice
   depends on.** §6's own standing rule tells the builder to reproduce each UNVERIFIED row
   before building it, and slice 8 is exactly the set of harness defects that corrupt
   reproduction. **Do slice 8 first**, or accept that every reproduction before it runs on a
   known-faulty instrument.
2. **Slice 8 calls FA-92 "the worst".** FA-92 is P3. On the evidential ladder the memo uses
   for harness rows, **FA-10 is the only P1 harness row** and sits in the same slice. The
   slice also omits both P2 harness rows, FA-37 and FA-40.
3. **Slice 4 is labelled packaging, "do this before the export", but carries FA-9**, whose
   own fix shape is a scenario/design change.
4. **Slice 5 is sized at ~1 session with no gate step**, but FA-D13's fix shape opens
   "A design ruling…". Size it with the gate, or move the gated rows out.

**Where I would start, given the verification:**

1. **Slice 8 first**, reduced to what actually protects reproduction: FA-10, FA-37, FA-40,
   FA-74, FA-87, FA-92. Half a session, and everything after it is measured on an instrument
   that works.
2. **Slice 1 (the parser).** FA-7 is the strongest row in the audit and I reproduced it by
   hand in under a minute: `Ney, delay the attack` resolves a real battle — 1,099 casualties,
   1 AP spent, no confirmation, identical in shape to a plain attack order. **Write the
   corpus rows; they do not exist.**
3. **Slice 2 (the question reaches the player)**, with FA-1 re-scoped per its cross-check.
   The harm is not "never asked" — a CRITICAL rail alert *is* delivered and answering works
   end to end — it is that **the enemy phase does not pause**, so a measured 92% of the corps
   is destroyed in a single phase the player cannot interject into.
4. **Then FA-26, as a shared helper across all four families** (§5), not one call at one seam.

Slices 3, 5, 6 and 7 stand as written — slice 5 gated, and the six `fix_shape`-versus-
`summary` rows (§1) read carefully before anyone edits.

## 8. Corrections to the hand-off prompt

The prompt was itself red-teamed and is mostly accurate. Six of its claims did not hold:

| prompt claim | measured |
|---|---|
| "master `97c64eba` … the one uncommitted file is `docs/NEXT_SESSION_PROMPT.md`" | master is `15d128b3`; the tree is clean and the prompt is committed. (A stray scratch file `x` *was* committed at the repo root in that same commit — see §9.) |
| 6 rows carry "finding N" self-references (FA-4, FA-46, FA-67, FA-74, FA-90, FA-D2) | **9 rows, 15 phrases.** It missed FA-5, FA-40 and FA-79 entirely, and three plural/hyphenated forms (`findings 1 and 3`, `finding-1`, `findings 2 and 4`) that a `finding \d+` regex cannot see |
| "genuinely unbalanced brackets: FA-74, FA-93, FA-D24" | **none of the three.** FA-93 is balanced; FA-74 and FA-D24 are the *same* quoted-pattern false positive the prompt correctly diagnosed for FA-38/FA-D15 (`'(stale passthrough'`, `random.seed(`). FA-D10 was missed and is the same class. **There are zero genuine bracket defects** — the whole line item is dead |
| "a naive bracket check flags 12 rows" | 10 |
| "126 of 130 rows carry an `already_filed` claim" | all 130 do |
| "17 rows depend on gitignored artefacts … on a fresh clone they do not [run]" | **11** cite such a path, **8** in the repro line, and **6 of those 8 run the driver themselves**, generating their inputs from committed fixtures and scripts. Only FA-17 and FA-19 name a pre-existing local file, and both offer a re-derivable alternative in the same sentence. **Effectively no row is unreproducible on a clean clone** |

The prompt's most valuable warnings all held: `_corrected` over `summary`, the two severity
ladders, the empty `lens` field, the CRLF and cp1252 traps, and above all the requirement to
override `M.parser` so probes stay free — `.env` sets `LLM_MODE=anthropic`, and this session
ran hundreds of probes.

## 9. Housekeeping found in passing

A scratch file named **`x`** was committed at the repo root in `15d128b3` — fourteen lines of
probe output about `_build_proposal_terms`, evidently an accidental `git add`. It is removed
in this pass's commit.

## 10. What this pass did not do

**The same thing that crippled the audit, in the same way, and it is worth recording.**
Three usage limits killed the original audit's refuter pass and all ten pillar scorers. This
verification hit a usage limit mid-flight and lost **155 of 280 agents** — every adjacency
sweep in the first two fleets, and roughly two-thirds of the cross-checks. The work was
relaunched, but the shape of the gap should be read honestly:

- **Every filed row has a verdict**, and every one of the nine P1s was verified.
- **Cross-checking is partial.** Where a second agent did attack a verdict, it changed the
  answer often enough to matter — five of the first twenty-one cross-checks moved it, and one
  moved DUPLICATE to NARROWED on a point of definition. **A row with a single verdict in the
  table below is better evidenced than it was yesterday, and still not settled.**
- **No pillar re-score exists.** This pass did not attempt one. The Aug-16 priors still stand
  un-refreshed, and that remains the largest open question about *the game*, as opposed to
  the audit. If the owner wants a score before the build, it needs its own session — and it
  should run after slice 8, so it is measured on a harness that works.

## 11. The answer

**Is the audit safe to build from?** Yes — with one rule: **reproduce before fixing, and read
`_corrected` and the Sept-2 verdict before reading the title.** The mechanisms are sound.
Every one of the nine P1s is real. Both headline parsing defects reproduce by hand in under a
minute on the shipped build. The evidence table is exact, and the machine record is in
perfect agreement with the memo — 128 rows, zero severity, kind or verdict mismatches.

**Is it safe to build from verbatim?** No. Roughly half the rows need correction first, six
prescribe a fix their own summary rejects, about 80% carry a stale line number, and about 44%
assert a filing status that is wrong.

**Which rows would I build first?** Slice 8's reproduction-critical half; then FA-7; then
FA-1 re-scoped to the enemy phase not pausing; then FA-26 as a shared helper across four
seams rather than one.

---

## Appendix A — every filed row, with its verdict

Read this with §1. `prior status` is what the audit published; **verdict** is this pass's.
`x-checked` marks a row a second, independent agent attacked.

| row | sev | kind | prior status | **verdict** | x-checked | what it got wrong (short) |
|---|---|---|---|---|---|---|
| **FA-1** | P1 | defect | UNVERIFIED | **NARROWED** | yes | 1. "never asked" is FALSE, and it is the row's headline. A CRITICAL `marshal_last_stand` notification heads the same e… |
| **FA-2** | P1 | defect | UNVERIFIED | **NARROWED** | yes | 1. STALE LINE NUMBER: the rebellion queue is at vassal.py:1009 (call spanning 1009-1010), not the cited ":1005-1007". … |
| **FA-3** | P1 | defect | UNVERIFIED | **NARROWED** | yes | 1. UNIVERSALITY IS FALSE. "no offering court reaches the 50 threshold" and "winning or losing" are both wrong. At Fran… |
| **FA-4** | P1 | defect | UNVERIFIED | **VERIFIED** | yes | Materially, nothing. Four small things: 1. `already_filed: "none"` is right about pre-existing rows, but FA-4 now exis… |
| **FA-5** | P1 | defect | AUTHOR_VERIFIED | **NARROWED** | yes | Three things, none fatal. (1) Severity: P1 is one level high — see severity_verdict. (2) "`_fill_popup_keys_without_dr… |
| **FA-7** | P1 | defect | AUTHOR_VERIFIED | **VERIFIED** | yes | Five corrections, none of which touches the finding: 1. **Confidence is 0.9, not 0.95.** The `player_consequence` clos… |
| **FA-8** | P1 | defect | UNVERIFIED | **VERIFIED** | yes | Four corrections. None touches the seam, the mechanism, the fix shape, or the severity — they are all in the consequen… |
| **FA-9** | P1 | defect | UNVERIFIED | **NARROWED** | yes | 1. HEADLINE MAGNITUDE — the load-bearing error. "loses six French homeland provinces by turn 10 to a **1,218-man retre… |
| **FA-10** | P1 | harness | HARNESS-CHK | **NARROWED** | yes | 1. `already_filed` is wrong: "the over-correction is not filed anywhere" — it is FA-74 (P3, BUG_FIXES.md:218, same sea… |
| **FA-6** | P2 | defect | AUTHOR_VERIFIED | **NARROWED** |  | CALIBRATION OF THE EARLIER VERIFICATION: half sound. The Sept 2 amendment did the hard part right — it killed the fals… |
| **FA-11** | P2 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | — |
| **FA-12** | P2 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | Two things, both in the row's favour on the substance. (1) UNDERSTATED REACHABILITY — the material one. The row's stat… |
| **FA-13** | P2 | defect | UNVERIFIED | **VERIFIED** | yes | — |
| **FA-14** | P2 | defect | UNVERIFIED | **VERIFIED** | yes | 1. **`already_filed` is false.** "This seam is unfiled" — FA-19 files the identical seam at the identical line with an… |
| **FA-15** | P2 | defect | UNVERIFIED | **NARROWED** | yes | 1. **"NEW seam and NEW repro" is false.** Two OPEN rows in the same audit already carry ~two-thirds of it: FA-14 (BUG_… |
| **FA-16** | P2 | defect | UNVERIFIED | **NARROWED** |  | 1. `fix_shape` names the wrong seam. "ONE seam: `strategic.py:874`" would be a no-op — `_execute_strategic_turn` is ne… |
| **FA-17** | P2 | defect | UNVERIFIED | **NARROWED** |  | Five things, one of which invalidates the headline. 1. MECHANISM (invalidates the title). "A persistent settlement off… |
| **FA-18** | P2 | defect | UNVERIFIED | **DUPLICATE** |  | 1. **`already_filed` is wrong.** "NEW" is false — FA-28 (`docs/BUG_FIXES.md:172`, P2, OPEN) is the same defect with th… |
| **FA-19** | P2 | defect | UNVERIFIED | **DUPLICATE** | yes | 1. `already_filed: "none found"` is wrong. FA-14 (BUG_FIXES.md:158) and FA-15 (:159) are OPEN P2 rows in the same tabl… |
| **FA-20** | P2 | defect | UNVERIFIED | **NARROWED** | yes | Two corrections, neither large enough to narrow the verdict — the authoritative `_corrected`/`summary` text is accurat… |
| **FA-21** | P2 | defect | UNVERIFIED | **NARROWED** | yes | Five corrections; none weakens the finding, and the first two make it larger. 1. **The headline number is wrong for th… |
| **FA-22** | P2 | defect | UNVERIFIED | **VERIFIED** |  | Three corrections, none touching the seam, the repro or the severity: 1. **"a battle_report (Mack strength 0 afterward… |
| **FA-23** | P2 | defect | UNVERIFIED | **VERIFIED** |  | Three inaccuracies, none of which weakens the finding; two of them make it look milder than it is. 1. **The repro's sc… |
| **FA-24** | P2 | defect | AUTHOR_VERIFIED | **DUPLICATE** |  | The earlier AUTHOR_VERIFIED pass was **sound on mechanism and player consequence and unsound on novelty**. I set out t… |
| **FA-25** | P2 | defect | UNVERIFIED | **NARROWED** |  | 1. **`player_consequence` is false.** "no headline, no sub-beat, no turn-event line and no Gazette row; the player… be… |
| **FA-26** | P2 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | — |
| **FA-27** | P2 | defect | UNVERIFIED | **VERIFIED** |  | — |
| **FA-28** | P2 | defect | UNVERIFIED | **DUPLICATE** |  | 1. `already_filed` is false — FA-18 (OPEN, BUG_FIXES.md:162 / memo §3b:544) is the same defect with the same evidence;… |
| **FA-29** | P2 | defect | UNVERIFIED | **NARROWED** | yes | 1. **The already_filed claim missed the row's own twin.** "NEW: the exact shipped strings, the README contradiction, a… |
| **FA-30** | P2 | defect | UNVERIFIED | **NARROWED** |  | 1. THE FREQUENCY EVIDENCE IS FALSE. All four cited digest lines are non-instances. audit-flagship-mock:8 is turn 1's o… |
| **FA-31** | P2 | defect | UNVERIFIED | **NARROWED** |  | 1. THE HEADLINE IS INVERTED. "By the time the camp is staged, a WON roll leaves London-Normandy SHUT" — staging the ca… |
| **FA-32** | P2 | defect | UNVERIFIED | **NARROWED** |  | 1. **The title is false.** "a captured marshal vanishes from every daily surface" — he does not. `ledger._build_forces… |
| **FA-33** | P2 | defect | UNVERIFIED | **NARROWED** |  | Three things, one of them material to anyone fixing it. 1. MATERIAL — the scope claim in the title and in `_corrected`… |
| **FA-34** | P2 | defect | PLAUSIBLE | **NARROWED** |  | Three things, plus a calibration note on the earlier verification. 1. SCOPE UNDERSTATED. The row frames this as the af… |
| **FA-35** | P2 | defect | UNVERIFIED | **NARROWED** |  | 1. WRONG SEAM (the load-bearing error). The title and the first clause blame P4 (`enemy_ai.py:2739`). P4 is structural… |
| **FA-36** | P2 | harness | HARNESS-CHK | **VERIFIED** |  | CALIBRATION — the author's self-check was sound on the load-bearing parts (mechanism, seam, fix shape, the digest-357 … |
| **FA-37** | P2 | harness | HARNESS-CHK | **VERIFIED** |  | **Calibration on the prior HARNESS_AUTHOR_CHECK: sound.** Unusually so for a self-check — all three cited line numbers… |
| **FA-38** | P2 | missing | UNVERIFIED | **NARROWED** |  | 1. **Title over-counts.** "three vassals lost in one morning" — the deterministic re-run of the archived board shows t… |
| **FA-39** | P2 | harness | HARNESS-CHK | **NARROWED** |  | Six things, two of them load-bearing. (1) TITLE over-reaches: "no digest can tell" is false at the run level — every d… |
| **FA-40** | P2 | harness | HARNESS-CHK | **VERIFIED** |  | — |
| **FA-41** | P2 | harness | HARNESS-CHK | **DUPLICATE** |  | Not the mechanism — that is exactly right and reproduces on a hash-pinned run byte-identical to the archived digest. W… |
| **FA-42** | P2 | missing | UNVERIFIED | **NARROWED** |  | Five things, none fatal to the finding: 1. "captures Kienmayer on T2" is stated as certain; measured 2 of 6 trust runs… |
| **FA-43** | P2 | missing | UNVERIFIED | **NARROWED** |  | Three things, none fatal to the finding: 1. THE LEGAL FRAMING, which is the title's load-bearing half. "The zip ships … |
| **FA-D1** | P2 | tie_in | UNVERIFIED | **NARROWED** | yes | 1. "fires on every fresh conquest … every conquest opens 3-6 turns of +75 rate" — overstates. The scan `break`s at wor… |
| **FA-D2** | P2 | tie_in | UNVERIFIED | **NARROWED** | yes | 1. THE SEAM IS WRONG. `war_status.py:56` and `:157` do not "resolve through the coalition leader". `opponent` at :56 c… |
| **FA-D3** | P2 | tie_in | AUTHOR_VERIFIED | **NARROWED** |  | Three things, two of which change the fix. 1. "the acceptance formula already prices each one" — FALSE for the sweeten… |
| **FA-D4** | P2 | tie_in | UNVERIFIED | **VERIFIED** | yes | — |
| **FA-D5** | P2 | tie_in | UNVERIFIED | **VERIFIED** | yes | Four corrections, none touching the finding itself: 1. **The inline `repro` does not reproduce.** `m.trust.set(15)` + … |
| **FA-D6** | P2 | tie_in | AUTHOR_VERIFIED | **VERIFIED** |  | Four things, all secondary; the headline, the seam, the repro and the severity are all sound, and unusually for this a… |
| **FA-D7** | P2 | tie_in | UNVERIFIED | **NARROWED** | yes | 1. The worked example is unreproducible on the court it names. "with Britain's settlement offer covering Austria curre… |
| **FA-44** | P3 | defect | PLAUSIBLE | **NARROWED** |  | FOUR things, in descending importance. 1. **`player_consequence` overcounts by ~2x and borrows another row's defect.**… |
| **FA-45** | P3 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | — |
| **FA-46** | P3 | defect | PLAUSIBLE | **VERIFIED** |  | Small things, and one calibration finding against the single refuter. 1. The refuter's rewrite made the row LESS accur… |
| **FA-47** | P3 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | — |
| **FA-48** | P3 | defect | AUTHOR_VERIFIED | **DUPLICATE** |  | Five things. (1) DUPLICATE, undeclared: FA-24 [P2, OPEN] in the same audit is the same finding on the same evidence wi… |
| **FA-49** | P3 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | CALIBRATION: the earlier AUTHOR_VERIFIED hand-check was SOUND. Every load-bearing claim survived an adversarial re-che… |
| **FA-50** | P3 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | CALIBRATION: the author's hand-check was SOUND. All three probes they reported reproduce essentially verbatim, includi… |
| **FA-51** | P3 | defect | PLAUSIBLE | **VERIFIED** |  | Three things, one of them in the row's favour. 1. FALSE CLAUSE (also asserted by the refuter, so it survived one pass … |
| **FA-52** | P3 | defect | AUTHOR_VERIFIED | **NARROWED** |  | Three things, one material. 1. **MATERIAL — `already_filed: none.` is false.** FA-49 (BUG_FIXES.md:193, OPEN, same tab… |
| **FA-53** | P3 | defect | UNVERIFIED | **NARROWED** |  | Five things, in descending order of consequence. 1. **`already_filed` is false on the captor half.** It is NPC-15, OPE… |
| **FA-54** | P3 | defect | NARROWED | **VERIFIED** |  | **Calibration on the prior verification: the single refuter was SOUND, and its correction was load-bearing.** The orig… |
| **FA-55** | P3 | defect | UNVERIFIED | **DUPLICATE** |  | Four things, one fatal to the row's existence. 1. FATAL — the "NEW here" differentiator is false. The AI P-1 rung as t… |
| **FA-56** | P3 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | — |
| **FA-57** | P3 | defect | PLAUSIBLE | **VERIFIED** |  | — |
| **FA-58** | P3 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | The mechanism, seam, cited line, reachability and severity are all right — the earlier AUTHOR_VERIFIED call was sound,… |
| **FA-59** | P3 | defect | PLAUSIBLE | **VERIFIED** |  | — |
| **FA-60** | P3 | defect | PLAUSIBLE | **DUPLICATE** |  | **Calibration of the single refuter: mechanism work excellent, disposition wrong.** Right, and independently confirmed… |
| **FA-61** | P3 | defect | PLAUSIBLE | **NARROWED** |  | FIVE things, plus the calibration question on the prior refuter. 1. THE HEADLINE NUMBER IS MIS-ATTRIBUTED. The row's m… |
| **FA-62** | P3 | defect | UNVERIFIED | **DUPLICATE** |  | Three things, none of them factual — every string, line number and premise in FA-62 is correct. 1. **It is a duplicate… |
| **FA-63** | P3 | defect | UNVERIFIED | **NARROWED** |  | Five things, none fatal to the finding. 1. ATTACKER ATTRIBUTION. "Archduke Charles attacks Senarmont at Munich in the … |
| **FA-64** | P3 | defect | UNVERIFIED | **NARROWED** |  | Three things, one of them material. 1. MATERIAL — the player_consequence inverts causation. It reads: "the typed confi… |
| **FA-65** | P3 | defect | PLAUSIBLE | **NARROWED** |  | Four things, one of them the row's whole reason for existing. 1. THE DEAD ZONE DOES NOT EXIST. `_corrected` says "loya… |
| **FA-66** | P3 | defect | UNVERIFIED | **DUPLICATE** |  | `_corrected` is byte-identical to `summary`, so no refuter had moved this seam — consistent with its UNVERIFIED status… |
| **FA-67** | P3 | defect | AUTHOR_VERIFIED | **NARROWED** |  | (1) The headline is false: a won battle raises trust +3 through `vindication.resolve_battle`, called from combat_execu… |
| **FA-68** | P3 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | — |
| **FA-69** | P3 | defect | NARROWED | **NARROWED** |  | Four things, one of which would have caused the row to be silently dropped. 1. THE DUPLICATE ATTRIBUTION IS FALSE, AND… |
| **FA-70** | P3 | defect | PLAUSIBLE | **VERIFIED** |  | — |
| **FA-71** | P3 | missing | AUTHOR_VERIFIED | **VERIFIED** |  | Four things, none of them fatal to the claim: 1. **The repro names the wrong endpoint.** The row's repro calls `handle… |
| **FA-72** | P3 | harness | HARNESS-CHK | **VERIFIED** |  | Three things, all minor; none touches the verdict. 1. It attributes behaviour to POLICY KEYS that are dead. `"interrup… |
| **FA-73** | P3 | harness | AUTHOR_VERIFIED | **NARROWED** |  | Five things, and a calibration failure that explains them. 1. The load-bearing quote is truncated at the clause that r… |
| **FA-74** | P3 | harness | HARNESS-CHK | **DUPLICATE** |  | The author's hand-check ("Verified by opening") confirmed the code reading — which is accurate, line for line — but it… |
| **FA-75** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Three things, one of them load-bearing. 1. LOAD-BEARING — "`lapsed_offers` on the wire = [] every turn" is FALSE, and … |
| **FA-76** | P3 | harness | HARNESS-CHK | **DUPLICATE** |  | Four things, none of which touch the truth of the underlying defect: 1. **`already_filed: "none found"` is wrong.** FA… |
| **FA-77** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Three things, and a calibration note on the author check. 1. FABRICATED-BY-INFERENCE CITATION. "the route-through-Hano… |
| **FA-78** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Four things, all found by opening the code and re-deriving from the committed digests rather than trusting the row. 1.… |
| **FA-79** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Three substantive errors plus one calibration failure on the author's self-check. 1. **already_filed misses its own si… |
| **FA-80** | P3 | missing | PLAUSIBLE | **NARROWED** |  | **Calibration of the earlier verification: the single "mechanism" refuter was sound but over-confirmed.** All seven of… |
| **FA-81** | P3 | missing | PLAUSIBLE | **NARROWED** |  | **One substantive error, one trivial one — and a calibration finding about the single refuter.** 1. **`player_conseque… |
| **FA-82** | P3 | missing | UNVERIFIED | **VERIFIED** |  | One thing, and it matters for whoever fixes it: **the row's anchor line is wrong and always was.** The `file`/`line` f… |
| **FA-83** | P3 | harness | AUTHOR_VERIFIED | **NARROWED** |  | The author's hand-check was sound on quotation and weak on causation — it confirmed the strings appeared and did not a… |
| **FA-84** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Five things — one of them would misdirect a builder. 1. **Wrong seam for the banner half (material).** The row credits… |
| **FA-85** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Five things, in descending order of consequence. 1. THE FIX WOULD NOT HAVE WORKED, and the same audit already held the… |
| **FA-86** | P3 | harness | HARNESS-CHK | **DUPLICATE** |  | The author's hand-check was sound on the mechanism and careless on everything around it — which is the signature of ch… |
| **FA-87** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Four things, one of which is a calibration failure of the author check itself. 1. **`already_filed` is wrong on both c… |
| **FA-88** | P3 | harness | HARNESS-CHK | **DUPLICATE** |  | Calibration of the earlier HARNESS_AUTHOR_CHECK: the author verified the code correctly and reproduced nothing. Every … |
| **FA-89** | P3 | harness | HARNESS-CHK | **NARROWED** |  | CALIBRATION OF THE EARLIER PASS: the HARNESS_AUTHOR_CHECK verified the citations and did not test the inference. Every… |
| **FA-90** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Six things, three of them material. MATERIAL: 1. "no ... sub-gate LLM script" (repro) and the implication that no live… |
| **FA-91** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Four things, one of which matters. 1. THE EXEMPLAR (matters). The row's headline pairs blind spot (1) with "`_recovery… |
| **FA-92** | P3 | harness | HARNESS-CHK | **NARROWED** |  | Three things, one of them material. 1. MATERIAL — the record citation is backwards. "The record already knows the fail… |
| **FA-D8** | P3 | tie_in | NARROWED | **NARROWED** |  | 1. THE TITLE IS BACKWARDS. "only a >= 5,000 garrison detachment makes the AI stop" fuses two different mechanics and n… |
| **FA-D9** | P3 | tie_in | PLAUSIBLE | **NARROWED** |  | 1. THE ARITHMETIC, and it is load-bearing. `player_consequence` claims drill "would have fixed it in two turns"; the f… |
| **FA-D10** | P3 | tie_in | NARROWED | **NARROWED** |  | 1. `_corrected` asserts the spec "explicitly list[s] 'contribution shares' as required content for the war detail popu… |
| **FA-D11** | P3 | tie_in | PLAUSIBLE | **VERIFIED** |  | Four small things, none of which touch the defect (`_corrected` itself is accurate throughout): 1. `player_consequence… |
| **FA-D12** | P3 | tie_in | PLAUSIBLE | **VERIFIED** |  | Three things, none fatal. (1) THE DIGEST CITATION IS THE WRONG EPISODE AND THE LINE NUMBERS ARE OFF. The summary cites… |
| **FA-D13** | P3 | tie_in | NARROWED | **DUPLICATE** |  | 1. **`already_filed: "none"` is wrong, decisively.** FA-D14 (DESIGN_REFINEMENT.md:39, same audit, OPEN) is a strict su… |
| **FA-D14** | P3 | tie_in | UNVERIFIED | **DUPLICATE** |  | Four things, none of which kill the finding — they kill its right to be a separate row. (1) THE BIG ONE: `already_file… |
| **FA-D15** | P3 | tie_in | NARROWED | **VERIFIED** |  | `_corrected` is sound; the corrections below are against the rest of the row, which was NOT rewritten to match it and … |
| **FA-D16** | P3 | tie_in | UNVERIFIED | **NARROWED** |  | Three things, one of them load-bearing. 1. LOAD-BEARING — the remedy is boot-dead, and the behaviour_test as written w… |
| **FA-D17** | P3 | tie_in | NARROWED | **NARROWED** |  | 1. **The title is false as written.** "The Cabinet's 'Propose Peace' row stays green" — there is no such row at WAR. `… |
| **FA-D18** | P3 | tie_in | NARROWED | **NARROWED** |  | 1. THE TITLE IS INVERTED. "The armistice preview promises a peace the thaw arithmetic cannot deliver" - the shipped ch… |
| **FA-D19** | P3 | tie_in | AUTHOR_VERIFIED | **NARROWED** |  | Three things, one material. 1. MATERIAL — the player_consequence is wrong in its own cited scene. The row builds its c… |
| **FA-D20** | P3 | tie_in | PLAUSIBLE | **NARROWED** |  | Four things, none of which kill it. 1. `already_filed: none` is wrong. Six of the ten verbs are an explicitly owned Go… |
| **FA-D21** | P3 | tie_in | PLAUSIBLE | **DUPLICATE** |  | Three things, none of them the mechanism. (1) `already_filed: "none"` — it is a duplicate of FA-66 from the same audit… |
| **FA-93** | P4 | defect | AUTHOR_VERIFIED | **VERIFIED** |  | — |
| **FA-94** | P4 | defect | NARROWED | **NARROWED** |  | Three things, in descending order of consequence. 1. THE CENSUS IS INCOMPLETE IN THE ROW'S OWN DIRECTION — nobody, fin… |
| **FA-95** | P4 | defect | PLAUSIBLE | **VERIFIED** |  | — |
| **FA-96** | P4 | defect | NARROWED | **DUPLICATE** |  | 1. **`already_filed: none` is false — the row's one material error.** The defect is filed, gate-RULED (Aug 15, 2026), … |
| **FA-97** | P4 | defect | AUTHOR_VERIFIED | **REFUTED** |  | It verified the last link of the chain in isolation. Every static citation is right and every line number is current —… |
| **FA-98** | P4 | defect | PLAUSIBLE | **VERIFIED** |  | — |
| **FA-99** | P4 | defect | UNVERIFIED | **VERIFIED** |  | — |
| **FA-100** | P4 | defect | NARROWED | **NARROWED** |  | Four things, one of them serious. 1. SERIOUS — the authoritative `_corrected` block describes a different defect from … |
| **FA-101** | P4 | defect | UNVERIFIED | **NARROWED** |  | 1. UNDERCOUNTS THE CARRIERS — the material error. The row says "two documents" (main.py + WEIRD_OUTCOMES_SPEC.md). The… |
| **FA-102** | P4 | harness | HARNESS-CHK | **NARROWED** |  | Two factual clauses, both understating the gap: 1. "audit-latewar-t20 … a turn-boundary snapshot carrying no pending q… |
| **FA-D22** | P4 | tie_in | NARROWED | **VERIFIED** |  | Three things, none fatal; `_corrected` had already caught two of them. 1. The top-level `line: 233` field is OFF BY ON… |
| **FA-D23** | P4 | tie_in | UNVERIFIED | **VERIFIED** |  | Five errors, none fatal to the finding; the first is the one a builder would trip over. 1. WRONG SEAM for the objectio… |
| **FA-D24** | P4 | tie_in | NARROWED | **VERIFIED** |  | — |
| **FA-D25** | P4 | tie_in | NARROWED | **DUPLICATE** |  | Four things, in descending order of consequence. 1. `_corrected` states a FALSE fact and states it as verified: "'will… |
| **FA-D26** | P4 | tie_in | NARROWED | **NARROWED** |  | Six things, in descending order of consequence. 1. **The headline is measurably false of the shipped screen.** "The EC… |