# VERDICT:L2-5 — CONFIRMED, and understated on width; its own prescribed fix closes 0 of 23

**Default verdict was REFUTED. It survives.** Every figure below is from a probe
I ran myself, on the shipped 1805 board, at `master 727cf88a` (clean).
Probes: `probes/rf/rf01..rf11`.

| | |
|---|---|
| **Verdict** | **CONFIRMED** — reproduces exactly, 23 of 23 |
| **Severity** | **P3 HELD** — but the finding's own severity argument is incomplete (§4) |
| **Player-reachable** | **YES**, measured (§5) |
| **Shipped by row CX** | **YES**, proven against the pre-row tree, not the lever (§2) |
| **Prescribed fix** | **DOES NOT WORK** — closes **0 of 23**, and widens the defect (§6) |
| **Width** | filed as 23 across 2 doors; measured **256 of 261 cells across 9 doors** (§3) |

---

## 1. It reproduces, exactly as filed (rf01)

23 of 23 named shapes, driven end to end at `POST /command` on a fresh 1805
board per utterance, both lever positions:

```
quickly attack Mack       OFF: AP 4->3, 5 corps moved   ON: "There is no 'quickly' in the order of battle, Sire. Whom did you intend?"
immediately attack Mack   OFF: AP 4->3, 6 corps moved   ON: "There is no 'immediately' ..."
cavalry attack Mack       OFF: AP 4->3, 6 corps moved   ON: "There is no 'cavalry' ..."
okay retreat              OFF: whole-army retreat, 8 corps, free   ON: "There is no 'okay' ..."
tonight retreat           OFF: whole-army retreat, 8 corps, free   ON: "There is no 'tonight' ..."
Marshal attack Mack       OFF: AP 4->3, 6 corps moved   ON: "There is no 'Marshal' ..."
```

…and `urgently quick hurry today finally instantly promptly yes alright right
well General guards gentlemen artillery infantry ok`. The message is verbatim
what the lens filed.

**One correction to the filed wording.** The lens calls the lever-OFF outcome
"a battle". On the `attack` doors it is the **muster prompt** — `MUSTER —
Soult (30,000; 101,499 if all march…)` — costing 1 AP and relocating five to
six corps, not a resolved battle. On the `retreat` doors it *is* the full
general retreat, executed and free. The regression is real either way; the
label was loose.

**A second correction, minor but real for the client:** the executor sets
`"kind": "marshal_not_found"` and `main.py` does not propagate it — `kind` is
absent from the response. The player gets a bare sentence with no structured
handle, so there is no clarification road, no did-you-mean, no chip. (rf05 D/E)

## 2. Shipped by row CX — proven against the pre-row tree (rf02)

The lens measured this **with the lever only**. That is not sufficient proof of
"the row shipped it": the lever restores one branch of one function, while
CX-2, CX-3 and CX-5 all touched `backend/ai/llm_client.py` — the mock parser
that decides what these sentences parse to in the first place.

So I archived the true pre-row tree read-only (`git archive b4a27a15^ backend
godot-client/.../maps tests/data`) and drove the same 26 utterances through
**both** trees in separate interpreters:

```
                           PRE-ROW b4a27a15^   HEAD 727cf88a
quickly attack Mack        EXECUTED            REFUSED_UNBOUND   <== shipped by row CX
...  (23 of 23 identical)
attack Mack                EXECUTED            EXECUTED
retreat                    EXECUTED            EXECUTED
Ney, attack Mack           EXECUTED            EXECUTED
NEW unbound-refusals introduced between b4a27a15^ and HEAD: 23/26
```

The lens's attribution is right, and now it is proven rather than inferred.

## 3. Width: the lens opened 2 of 15 doors (rf03, rf04, rf10)

`_MARSHAL_LESS_TYPES` has five members and the mock parser routes **fifteen**
distinct bare phrasings into them:

```
attack / attack Mack / assault / engage / storm     -> general_attack, auto_assign_attack
bombard Mack / bombard Swabia                       -> auto_assign_bombardment
retreat / withdraw / fall back / pull back          -> general_retreat
scout Swabia / reconnoitre / recon                  -> auto_assign_scout
pursue Mack                                         -> auto_assign_attack
```

Crossing 9 sound doors with 29 natural leading runs, driven end to end at both
arms — **261 cells, 256 new refusals, 5 unchanged.**

**And the worst family is not adverbs.** These are all refused:

```
someone attack Mack            "There is no 'someone' in the order of battle, Sire."
somebody attack Mack           "There is no 'somebody' ..."
anyone attack Mack             "There is no 'anyone' ..."
whoever is closest attack Mack "There is no 'whoever is closest' ..."
```

`_NOT_AN_ADDRESS_RE` holds `all / every / everyone / everybody / each / both /
any` but **not the indefinite pronouns**. `someone attack Mack` is the plain
English for *"I do not care who — send whoever is nearest"*, which is the
entire purpose of `auto_assign_attack`, and the game's own clarification
literally asks *"Which marshal shall lead the attack, Sire?"*. That is a
sharper case than `quickly`, and the lens did not find it.

**The mirror hole, in the other direction, same list.** The guard computes the
head by searching `_ADDRESSEE_IS_AN_ORDER_RE`, which is a *different*
hand-written verb list from the parser's — and it is missing two the parser
knows:

```
Zorglub pull back      -> WHOLE-ARMY RETREAT executed  <== FA-22's original defect, still live
Zorglub recon Swabia   -> Soult scouts Swabia          <== ditto
```

So the same maintained-by-hand list over-refuses natural English on 256 cells
and under-refuses a genuinely unbound name on two doors. One root, both signs.

## 4. Severity: P3 HELD — but two of the finding's three supports are the wrong shape

**Support 1 holds, and I re-measured it.** The refusal is genuinely free.
Three refusals in sequence on one live board: `ap 4→4→4→4`, `gold 800→800`,
`turn 1→1`, and the next `attack Mack` works normally. (rf05 A/C)

**Support 2 holds, and I re-ran it independently.** Of 449 golden-corpus
utterances put through the predicate itself, **1** is claimed — `nay attack
wellinton`, the row's own intended case. All 233 order-shaped strings in
`tools/playtest_scripts/*.json` are comma-plus-real-name. (rf11)

**Support 3 does not cover the surface that matters, and this is the part the
lens missed.** Its third bullet is *"0 of 101 command-shaped strings the game
itself PRINTS"* — a census of **authored** text. The predictor's first source
is not authored:

```
F1  _add_to_history(command)              main.gd:1650
F2  api_client.send_command(command, ...) main.gd:1700
F3  history is written 50 lines BEFORE the command is sent -> REFUSED COMMANDS ARE RECORDED
F4  removal paths for a failed command: 0 -> never un-recorded
F5  _add_to_history takes a success flag? NO — it takes only the string
    MAX_SUGGESTIONS = 5; the history arm (main.gd:6993) runs FIRST, before the grammar
```

Measured, with the history arm ported verbatim (rf06):

```
typed 'quickly attack Mack'     -> REFUSED
  then typing 'qui'             -> predictor offers ['quickly attack Mack']
typed 'cavalry attack Mack'     -> REFUSED
  then typing 'cav'             -> predictor offers ['cavalry attack Mack']
offered sentences the parser/executor REFUSES: 5 of 5
```

That is **CX-3's own rule — "the game must not offer a sentence it cannot
read" — breached through CX-3's own history arm**, on precisely the sentences
CX-1's regression creates. CX-3's census is scoped to `_MARSHAL_VERBS`,
`_BARE_COMMANDS` and the COMMAND REFERENCE, so it is structurally incapable of
seeing this; the lens re-ran that census, found it clean, and drew the wrong
conclusion from a true result.

**Why P3 still, and not P2.** Nothing is spent, nothing is lost, no state
moves, the next sentence works, and no *authored* surface teaches the shape.
The player is inconvenienced and mildly insulted, then retypes. But the
predictor finding is the reason it must not be filed any lower: the row's
marquee feature **amplifies** the regression rather than being neutral to it,
and it does so on the one surface a frustrated player will lean on hardest.

## 5. Player-reachable: YES

`main.gd::_redirect_diplomatic_command` intercepts 114 keyword forms and fails
open otherwise. I read all three lists — `DIPLO_NO_HOME_KEYWORDS`,
`DIPLO_WAR_ROOM_KEYWORDS`, `DIPLO_FAMILY_KEYWORDS` — and **no order verb
appears in any of them** (`attack`, `retreat`, `scout`, `bombard`, `withdraw`,
`pursue`, `fall back`: zero hits). `quickly attack Mack` reaches
`POST /command` verbatim, exactly as I drove it.

## 6. The prescribed fix does not work — measured

The finding's remediation is one sentence: *"The head-token fix in L2-4 closes
it in the same edit."* L2-4's rule, verbatim: *"after stripping a leading
article, if the first token is a function word or a collective the run is
grammar; otherwise the run is an address."*

I implemented it exactly and ran all four groups through it (rf07):

```
L2-5 shapes CLOSED by its own prescribed fix : 0
L2-5 shapes STILL REFUSED after the fix      : 23
```

**Zero.** Every one of these 23 heads — `quickly`, `cavalry`, `ok`, `tonight`,
`someone` — is a *content* word, so the head-token test claims it as an address
exactly as today's whole-run test does. The rule change is orthogonal to this
finding; it fixes L2-3 and L2-4 and leaves L2-5 untouched.

**Worse, it widens it.** A run whose head is a content word but which contains
grammar stands down today and would be refused after:

```
quickly and at once attack Mack    HEAD=pass   FIX=addr   (new refusal)
```

So a builder who follows the report closes two findings, believes he closed a
third, and ships one more refusal. **This is the correction that matters most
in this verdict.**

## 7. A shape that does work — measured against every pin (rf09)

The root is that the comma-less arm asks *"is this run NOT a name?"* against a
blocklist, and English has more adverbs than the list will ever have. Asked the
other way — *claim the run only when it looks like a name, and fail closed* —
it is bounded. Candidate: **1–3 tokens, and either a token is capitalised as
typed, or a token is within one keystroke (`osa_distance_at_most`, FA slice 7's
own helper) of a name on any roster.**

```
pins red by this shape          : 0
L2-5 shapes closed              : 28 of 30
L2-5 shapes still refused       : ['Marshal', 'General']
```

Checked against every case CX-1 pins: `Nay / Grouchy / Berthier / Wellington /
Blucher / Zorglub` all still refused; `all marshals / everyone / every corps /
the army / can you / do / please / (bare)` all still pass. The two residuals
are capitalised military titles, and the bounded list for them **already exists
as a single source** — `clause_guards.HONORIFIC`, landed by FA slice 7 and
composed into nine address regexes. Consuming it closes 30 of 30.

Honest residue: lowercase `zorglub attack mack` would pass. That is the
**pre-row** behaviour, not a new loss, and `nay` is still caught by the
edit-distance arm at any case.

## 8. Why the row's own instrument could not catch this

The memo (§6b) is admirably honest that `commanded_full40.json` is blind — *"0
of 166 strings omit the addressee comma"* — and says the row added the arm that
can: `typed_road.json`, which *"types the way a person does… it drops a
comma."* I read it. All 14 order-shaped lines:

```
Nay attack Mack · Zorglub attack Mack · Wellington retreat · Ney, attack Mack
retreat? · why not attack Mack · what about attack Mack · can Davout attack Mack ...
```

It drops the comma **only in front of a name** — never in front of an adverb,
an interjection, an arm noun or an indefinite pronoun. The instrument built to
catch this class was built on the geometry of the finding it was chasing, which
is this project's recorded lesson arriving on schedule: *the reviewers' first
move is to change the one parameter the builder held constant.*

⛔ **And the standing rule this row should now inherit, from IQ-7's own review
round, quoted in CLAUDE.md:** *"a rule built by stripping what you recognise is
only as safe as the list it strips."* IQ-7 applied it to an irreversible priced
answer and wrote the allowlist out. CX-1's refusal is free, which is why this
is P3 and not P1 — but it is the same anti-pattern, one row later, and the same
answer fixes it.

---

## Probe index (all under `probes/rf/`, all read-only, all keyless-mock)

| probe | what it measures |
|---|---|
| `rf_harness.py` | fresh shipped-1805 board per utterance, `POST /command`, asserts `use_real_api is False` before every run |
| `rf01_reproduce.py` | the 23 named shapes + 9 controls, both lever positions |
| `rf02_prerow.py` | the same shapes against the TRUE pre-row tree, two interpreters |
| `rf03_width.py` | which bare phrasings reach `_MARSHAL_LESS_TYPES` — 15 doors |
| `rf04_cross.py` | 13 doors × 12 runs + the `Zorglub` hole check |
| `rf05_cost.py` | AP/gold/turn cost, `command_history` residue, response keys |
| `rf06_predictor.py` | the `_add_to_history` → `_build_completions` breach, history arm ported verbatim |
| `rf07_fix.py` | L2-4's head-token rule implemented verbatim, scored against all four groups |
| `rf08_edges.py` | titled addresses, indefinite pronouns, `at once`, numbered corps |
| `rf09_shape.py` | the allowlist candidate against every CX-1 pin |
| `rf10_count.py` | 9 doors × 29 runs = 261 cells, both arms |
| `rf11_corpus.py` | the 449 corpus utterances through the predicate itself |
