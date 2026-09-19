# REFUTING THE EXECUTOR CENSUS

Adversarial re-derivation of `cx_recon/executor_road.md`. Default verdict was
REFUTED; each finding had to survive being attacked. Every claim below is a
`file:line` I read or the output of a probe under
`…/scratchpad/cx_recon/probes/refute2/`.

**Measurement tree.** The working tree is dirty (a sibling's uncommitted
"CX slice 1 — A QUESTION NEVER ORDERS" touching `backend/ai/clause_guards.py`
and `backend/ai/llm_client.py`). I measured on a **pristine HEAD copy**
(`…/cx_recon/pristine`), verified byte-identical to `f7008582` for every file
I touched:

```
backend/ai/clause_guards.py        HEAD=43b1867b… PRIST=43b1867b… SAME
backend/ai/llm_client.py           HEAD=80100afb… PRIST=80100afb… SAME
backend/commands/vassal_executor.py HEAD=95ffc501… PRIST=95ffc501… SAME
backend/commands/executor.py       HEAD=f956f154… PRIST=f956f154… SAME
backend/game_logic/vassal.py       HEAD=17a33bf8… PRIST=17a33bf8… SAME
```

`tests/` and `godot-client/` are `CLEAN_AT_HEAD` per `git status --porcelain`,
so I read those from the repo.

## Scoreboard

| id | verdict | the short version |
|---|---|---|
| EXR-1 | **SURVIVES (P1) — but both its evidence and its magnitude are wrong** | reproduced independently; its headline effect unwinds in 2 turns; the effect that *doesn't* unwind is one it never looked for |
| EXR-2 | **SURVIVES, NARROWED** | counts exact, but it describes one of two client behaviours; the other sends the sentence |
| EXR-3 | **SURVIVES on the shadow half, REFUTED on its arithmetic** | shadow table reproduced exactly; "8 of its 13 entries" is **6 of 13**, mutation-proven |
| EXR-4 | **SURVIVES** | exact, and two more phrasings measured |
| EXR-5 | **SURVIVES** | exact |
| EXR-6 | **SURVIVES, NARROWED on severity** | exact under the gate's own rule; 2 of the 4 are aliases of a covered action |
| EXR-7 | **SURVIVES** | every citation exact; correctly says nothing is broken today |
| EXR-8 | **SURVIVES, but contradicts its own body** | headline says 24, its own list is 26, measured 26 |
| EXR-9 | **SURVIVES** | one off-by-one (`:5776` → `:5777`) |
| EXR-10 | **NARROWED** | conclusion holds; its dispatch census missed a third copy |
| EXR-11 | **SURVIVES** | independently confirmed, and the sibling's slice matters more than it says |

Stale-line rate is **1 in ~40 citations** — far better than this repo's
documented ~80%. The failure mode here is not stale lines, it is **filing the
transient half of a defect and missing the durable half**.

---

# REFUTE:EXR-1 — SURVIVES as P1; the reasoning is wrong in both directions

## The core is real, and I closed the report's own UNVERIFIED

Reproduced independently through `POST /command` on the pristine tree
(`probes/refute2/x02_p1_repro.py`), shipped 1805 board, turn 1:

```
BEFORE: turn=1 AP=4 DP=5 gold=800 vassals=[Holland,KingdomOfItaly,Switzerland] FR_marshals=8
  'vassalize Austria' -> HTTP 200 success=True   truthy blocking keys: []
  'vassalize Britain' -> HTTP 200 success=True   truthy blocking keys: []
  'vassalize Russia'  -> HTTP 200 success=True   truthy blocking keys: []
AFTER : turn=1 AP=4 DP=5 gold=800 vassals=[Austria,Britain,Holland,KingdomOfItaly,Russia,Switzerland] FR_marshals=14
```

No objection, no dialogue, no confirm — I checked every blocking key on the
response and all were falsy. And there is **no backend guard at all**: a string
census over `backend/main.py` finds `DIPLO_FAMILY` 0, `vassalize` 0,
`subjugate` 0, `_redirect_diplomatic` 0, `make_vassal` 0, `Take your seat` 0.

Citations verified: `_execute_make_vassal` at `vassal_executor.py:122`;
dispatch `executor.py:2538`; `free_actions` at `executor.py:1273` (33 entries,
`make_vassal` present); `ADMIN_ACTIONS` at `meta_executor.py:30`
(`make_vassal` absent); `create_vassal_conquest` at `vassal.py:540` with
exactly the four gates named.

**The report's §7 UNVERIFIED about the WPS-B power cap is now VERIFIED, and it
does not bind** (`x01_powercap.py`, `POWER_CAP_RATIO = 2` at
`diplomacy.py:3516`):

```
France power = 4025   cap (lord//ratio) = 2012
  Austria  WAR  1250  capOK=True 31%
  Britain  WAR  1800  capOK=True 44%
  Russia   WAR  1700  capOK=True 42%
eligible by state+cap: ['Austria','Bavaria','Britain','Russia','Spain']
```

The eligible set matches the report exactly.

## ⛔ Where the report is WRONG: its headline effect unwinds in two turns

*"Three sentences, on turn one, end the Third Coalition and take France's
marshal roster from 8 to 14."* I drove it forward (`x04`, `x05`):

```
turn  2 FRmarshals=14 vassal=[Austria,Britain,Russia] loyalty={12,13,12} state=VASSAL/VASSAL/VASSAL
turn  3 FRmarshals= 8 vassal=[]                      state=WAR/WAR/WAR
LOST BY TURN: {'Austria': 3, 'Russia': 3, 'Britain': 4}
assimilated roster at end: Mack->Austria, ArchdukeCharles->Austria, ArchdukeJohn->Austria,
                           Moore->Britain, Kutuzov->Russia, Buxhowden->Russia
```

A conquest vassal boots at **loyalty 20**, below the disaffected line, bleeds
~8/turn, and `vassal_broke_free` fires on turn 3. The roster goes **14 → 8**.
Every marshal walks home. The Third Coalition is back at WAR by turn 4.

**So the one measurement the report leads with — FR_marshals 8→14 — is the
transient half.** Filed as written, a builder would fix a two-turn blip.

## ⛔ Where the report is wrong the OTHER way: the durable prize it never looked for

`create_vassal_conquest` calls `_reconcile_vassal_diplomacy`
(`vassal.py:616` → `:630`), which downgrades the new vassal's alliances. Those
downgrades are **permanent** — nothing restores them when the vassal breaks
free. Measured against a control arm on **three seeds** (`x06`, `x07`):

| seed | arm | Austria\|Britain | Austria\|Russia | Britain\|Russia |
|---|---|---|---|---|
| refute-exr1 | control, turn 6 | ALLIANCE | ALLIANCE | ALLIANCE |
| refute-exr1 | annexed, turn 6 | **PEACE** | **OPEN_BORDERS** | **OPEN_BORDERS** |
| refute-seed2 | control, turn 9 | ALLIANCE | ALLIANCE | ALLIANCE |
| refute-seed2 | annexed, turn 9 | **PEACE** | **NON_AGGRESSION** | **DEFENSIVE_ALLIANCE** |
| austerlitz | control, turn 9 | ALLIANCE | ALLIANCE | ALLIANCE |
| austerlitz | annexed, turn 9 | **DEFENSIVE_ALLIANCE** | **DEFENSIVE_ALLIANCE** | **OPEN_BORDERS** |

**Three free sentences permanently dismantle the Third Coalition's alliance
web.** That is the defect. The vassalage was never the prize; it was the
delivery mechanism.

**And it is an unbounded loop.** `vassal_release_cooldowns` is written by
`release_vassal`, not by a break-free, so after the vassals walk out the
cooldown dict is **empty** and the same three sentences work again — measured
at turn 5 on two seeds, all three re-subjugated, AP/DP/gold unmoved:

```
release cooldowns: {}
re-vassalize Austria  -> ok=True   re-vassalize Britain -> ok=True   re-vassalize Russia -> ok=True
AP/DP/gold: 4 5 7672
```

Every two turns, for free, forever. Each cycle also re-rolls
`_reconcile_vassal_diplomacy` on whatever the courts have rebuilt, and each
one hands the player direct command of the enemy's officer corps for two turns
(`Kutuzov, march to Paris -> ok=True`).

## The client defence is weaker than the report says — see MISSED-1

The report's framing ("a player typing into the terminal is stopped") is only
true for sentences that do not end in `?`. See **MISSED-1**.

## Fix hazards

- Do **not** fix this by adding `make_vassal` to `ADMIN_ACTIONS` or charging
  AP. The comment at `executor.py:1272` states the design — vassal verbs are
  free of *military* AP by intent. The missing price is DP/gold (MISSED-3).
- A fix **reds the golden corpus**: `parser_golden_corpus.json` id
  `vassalize-saxony` asserts `expected: {success: true, action: make_vassal}`,
  and `make_vassal` is on `MOCK_REACHABLE_ACTIONS`
  (`test_command_robustness_cr1_eval_harness.py:40`), so it cannot simply be
  deleted from the corpus without redding `TestActionCoverage`.
- Gating on war score / capital-held would also need the
  `settlement_ratify.py:678` road re-checked — that one is already priced
  (MISSED-3) and must not be broken.

---

# REFUTE:EXR-2 — SURVIVES, but NARROWED to a sub-claim of EXR-1

Counts re-derived (`x11`): `DIPLO_FAMILY_KEYWORDS` = **115** entries, declared
at `main.gd:1665` — both exact. Parsing `"<keyword> Austria"` through the real
mock parser, the only keywords landing on an action the Cabinet cannot produce
are the three named: `make vassal`, `vassalize`, `subjugate` → `make_vassal`.
The wizard's `_build_command` offers `propose_vassal` →
`"propose vassalization to " + nation` (`diplomacy_wizard.gd:776-777`), i.e. a
proposal that must be accepted. Confirmed.

**Narrowing:** this is EXR-1 seen from the client side, not an independent
defect, and it describes only *one* of the two things the shipped client does
with such a sentence. `_redirect_diplomatic_command` (`main.gd:1921`) fails
open on `_is_advisory_question` before it ever reaches the family match, so a
trailing `?` skips the Cabinet message entirely and the command is sent. EXR-2
is true of the polite phrasing and false of the interrogative one.

---

# REFUTE:EXR-3 — SURVIVES on the shadow half; its arithmetic is REFUTED

## The shadow table reproduces exactly

My first attempt used Ney (aggressive) and measured only 4 branches reaching
`_execute_specific` — **that was my instrument, not the finding**: objections
intercepted defend/hold/wait. Re-run with a literal marshal and hand-built
`type: "specific"` dicts, isolating the dispatch from the parser
(`x09_exr3_clean.py`, roster confirms `Soult: literal`):

```
attack YES   defend YES   hold YES   wait YES   move YES   scout YES   retreat YES
drill NO   fortify NO   unfortify NO   form_square NO   break_square NO
stance_change NO   cheat NO   debug NO
```

7 reachable, **8 shadowed** — the report's table, exactly. Every cited line is
exact (`:2465 drill`, `:2467 fortify`, `:2469 unfortify`, `:2471 form_square`,
`:2473 break_square`, `:2478 stance_change`, `:2483 cheat`, `:2488 debug`,
`:2565 command_type == "specific"`, `_execute_specific` at `:3021`). A full
census of callers confirms only three exist
(`executor.py:2571`, `combat_executor.py:10190`, `movement_executor.py:1157`).

## ⛔ REFUTED: "false for eight of its thirteen entries"

Mutation-tested the pin's own helper `_get_executor_dispatch_actions`
(`test_enforcement_suite.py:92`, regex-scoped to `_execute_specific`'s body
only) by deleting each shadowed branch from a copy of the source:

```
delete drill          pin REDS=True    delete break_square   pin REDS=True
delete fortify        pin REDS=True    delete stance_change  pin REDS=True
delete unfortify      pin REDS=True    delete cheat          pin REDS=False
delete form_square    pin REDS=True    delete debug          pin REDS=False
```

`tactical_actions` (`test_enforcement_suite.py:465`, the def is at **:465** —
exact) has **13** entries and `cheat`/`debug` are not among them. So the pin is
green-about-dead-code for **6 of its 13**, not 8. The finding's own body names
the right six; only its headline sentence is wrong.

## One piece of its supporting evidence I could not reproduce

The report asserts `combat_executor.py:10190` "re-enters with
`action == 'attack'`". `routed_command = dict(command)` at
`combat_executor.py:10152` copies the caller's action verbatim and never
rewrites it — and driving `bombard Swabia` on the boot board,
`_execute_specific` was **never reached** (the function returns its
no-artillery-in-range refusal first). The claim may be true on a board with
artillery in range; on the shipped boot board it is **UNVERIFIED**, and it is
asserted in the report without a measurement.

---

# REFUTE:EXR-4 — SURVIVES, exactly as filed

Spied on `DiplomaticExecutor._execute_propose_white_peace` through the real
`POST /command` (`x10`):

```
typed  'propose white peace with Austria'  white_peace_executor=False ok=True
       -> "regarding the Peace Treaty proposal to Austria…"  (a plain diplomatic_proposal)
typed  'white peace with Austria'          white_peace_executor=False ok=True   (same)
typed  'propose white peace Austria'       white_peace_executor=False ok=False  (parse failure)
wizard {action: propose_white_peace, target_nation: Austria}
                                           white_peace_executor=True  ok=True
```

Confirmed, and worse than filed in one respect: a third phrasing (`propose
white peace Austria`, no "with") is not a silent substitution but a hard parse
failure, so the verb has **no** working typed form at all — not one that
misroutes plus one that works.

---

# REFUTE:EXR-5 — SURVIVES, exactly as filed

`CAMPAIGN_LOG_TYPES` = **165** entries. Vassal-named types, all six:
`vassal_auto_join_war`, `vassal_broke_free`, `vassal_defected`,
`vassal_liberated`, `vassal_refuses_call`, `vassal_transferred`. A keyword
scan for any creation / autonomy / release type returns **NONE**. The log
records only loss.

This is corroborated from the other side by my own EXR-1 probe: the only
log-visible types the free annexation of Austria wrote were
`coalition_member_left` and `evacuation_granted`, and the unwind wrote
`vassal_defected` and `vassal_broke_free` — the chronicle records the empire
falling apart and never records it being built.

---

# REFUTE:EXR-6 — SURVIVES; NARROWED on severity

`MOCK_REACHABLE_ACTIONS` imported directly: a **`list` of 53**, declared at
`test_command_robustness_cr1_eval_harness.py:40` — exact. The gate
(`test_every_mock_reachable_action_has_a_corpus_entry`) computes
`missing = [a for a in MOCK_REACHABLE_ACTIONS if a not in covered]`, so it
genuinely only checks what is on the list. All eight claimed actions are
absent from it (verified by import, not regex).

I attacked the "four genuinely uncovered" half with the **gate's own coverage
rule**, which the report did not use — it also unions `expected.diplo.action`,
and I expected that to rescue the diplomatic one. It does not:

```
diplomatic_downgrade   covered_by_gate_rule=False
propose_common_peace   covered_by_gate_rule=False
finances               covered_by_gate_rule=False
treasury               covered_by_gate_rule=False
diplomatic_feasibility covered_by_gate_rule=True   grant_region_to_vassal True
purchase_levy          covered_by_gate_rule=True   recruit_marshal        True
```

(corpus: 447 entries, 57 distinct actions under the gate's rule.)

**Narrowing:** `treasury` and `finances` are folded into `economy` at
`executor.py:2444` — same handler, so two of the four "uncovered" actions
share a covered executor. `economy` itself has only **1** corpus row, which is
thin, but the uncovered *behaviour* is 2 actions, not 4. P3 → **P4** on
severity; the structural point (a hand-maintained list gating a coverage
check) is untouched and correct.

---

# REFUTE:EXR-7 — SURVIVES; every citation exact

`LLM_STRATEGIC_ACTION_REMAP` at `providers.py:248` mapping exactly
`pursue→attack, march→move, support→move, reinforce→move`, applied at
`providers.py:347` inside `build_parse_result_from_json`. All four are in
`VALID_ACTIONS` (`validation.py:46-49`, verified by import). The mock-chain
claim holds: a regex over `llm_client.py` for `action = "<alias>"` returns
**0**. The `repudiate_bargain` precedent comment is verbatim at
`executor.py:2508-2517`.

The finding is honest that nothing is broken today and says so. No attack lands.

---

# REFUTE:EXR-8 — SURVIVES, but the finding contradicts its own body

`ACTION_DISPLAY` has **43** rows — exact. All 26 ids the report lists in §5 are
genuinely absent (measured: `of those actually PRESENT: none`), and
`action_display_name('make_vassal')` → `'make vassal'`, confirming the
fallback.

**But the headline says "24 executable ids" while its own §5 list is 26, and
26 is the measured number.** An internal arithmetic error.

The blast-radius reasoning **holds up to attack**, which surprised me.
`recovery_action_vocabulary` (`prompt_builder.py:875`) has two arms: the
`narrated` arm goes through `action_display_name` and feeds the **LLM prompt**;
the `typed` arm is the **player-facing** one and builds
`a.replace("_", " ")` directly, never touching `ACTION_DISPLAY`. So a missing
row cannot reach player copy through this helper, exactly as filed.

**Further narrowing the report did not make:** `_RECOVERY_HIDDEN_ACTIONS`
(`prompt_builder.py:870-872`) already excludes `cheat`, `debug`, `unknown`,
`status`, `help`, `diplomatic_error`, `diplomatic_downgrade`,
`diplomatic_break` — 8 of the 26 — so the real prompt-side blast radius is
~18 ids. P4 is right; the magnitude is smaller than the number in the title.

---

# REFUTE:EXR-9 — SURVIVES; one off-by-one

`@app.post("/cancel_order")` at `main.py:5737` ✓, hard-stop guard re-derived at
`:5767` ✓, `executor._execute_cancel(...)` at `:5773` ✓. A grep for
`executor._execute_*` across `backend/main.py` returns **exactly one hit**
(`:5773`), so "the only endpoint that calls an `_execute_*` directly" is
confirmed by census, not assertion.

**Stale:** the AP charge is `world.use_action("cancel")` at **`:5777`**, not
`:5776` (`:5776` is the `if` guarding it).

---

# REFUTE:EXR-10 — NARROWED; conclusion holds, census incomplete

I did not re-drive all six `command_type` branches. What I did attack is the
"no orphan executors / one dispatch" framing, and it is **incomplete**: there
is a **third** copy of the action dispatch the report never names —
`meta_executor._execute_post_objection` — carrying its own 18-branch
if/elif chain at `meta_executor.py:2271+`, including one key
(`action == "bombardment"`, `:2334`) that appears in **neither** of the two
the report censused. That key is live, not dead: it is the defiance
substitution (`defiance.py:173`). Details in **MISSED-4**.

The finding's actual claim — that no `_execute_*` method is an orphan — I did
not falsify.

---

# REFUTE:EXR-11 — SURVIVES, and matters more than it says

Independently confirmed: `git status --short` shows
` M backend/ai/clause_guards.py`, ` M backend/ai/llm_client.py` and
`?? tests/test_cx1_a_question_never_orders.py` at `f7008582`.

The report treats the sibling edit as hygiene. It is substantive: the slice
changes the answer to the question in **MISSED-1**. Measured on both trees
(`x03_question_bypass.py`) — see below.

---

# WHAT THE CENSUS MISSED

## MISSED-1 — ⛔ P1: one character defeats the client guard, for the whole diplomatic family

The report calls `main.gd`'s keyword list "what actually protects the shipped
client". It does not read the guard's own control flow.
`_redirect_diplomatic_command` (`main.gd:1921`) runs, in order: empty check →
bare-underscore token → **`_is_advisory_question(lower)` → `return false`** →
no-home keywords → war-room keywords → `_matches_cabinet_family`. And
`_is_advisory_question` (`main.gd:1969`) begins:

```gdscript
func _is_advisory_question(lower: String) -> bool:
    """Questions and counsel stay spoken — Talleyrand answers them."""
    if lower.ends_with("?"):
        return true
```

`return false` from the redirect is documented as fail-open ("the backend sees
the sentence exactly as it always did"), and the call site
(`main.gd:1602`) is `if _redirect_diplomatic_command(command): return` followed
by `api_client.send_command(command, …)`. **So a trailing `?` sends the
sentence.** Measured through the real mock parser on both trees:

| utterance | PRISTINE HEAD | working tree (sibling's slice) |
|---|---|---|
| `vassalize Austria?` | **`make_vassal` / Austria** | `help` |
| `subjugate Austria?` | **`make_vassal` / Austria** | `help` |
| `make vassal Austria?` | **`make_vassal` / Austria** | `help` |
| `vassalize Austria ?` | **`make_vassal` / Austria** | `help` |
| `release Holland?` | **`release_vassal` / Holland** | `help` |
| `cede Tyrol to Bavaria?` | **`grant_region_to_vassal` / Bavaria** | `help` |
| `vassalize Austria` (no `?`) | `make_vassal` | `make_vassal` |

At HEAD the shipped client does **not** protect against EXR-1 — and the hole
is not specific to `make_vassal`: `release_vassal` and
`grant_region_to_vassal` ride through it too, both irreversible. The
uncommitted sibling slice closes the `?` half; it does not close EXR-1 itself
(the bare phrasing still executes on both trees, and is still stopped only by
client copy).

**Why the census missed it:** it treated the keyword list as the guard and
never read the three predicates that run before the list.

## MISSED-2 — the durable half of EXR-1

Folded into REFUTE:EXR-1 above rather than repeated: the permanent alliance-web
demolition (3 seeds, control-armed) and the empty-cooldown infinite repeat.
The census measured the roster count, which unwinds; it never ran the board
forward and never ran a control arm, so it could not see either.

## MISSED-3 — the price asymmetry, and the priced road sitting right beside the free one

Two things the census had in scope (it censused AP, admin AP, DP and gold per
action) and did not compare.

**(a) Every vassal verb charges a diplomatic point except the one that annexes
a great power.** Measured through `POST /command` (`x12`):

```
'vassalize Austria'            ok=True  AP 4->4  DP 5->5  gold 800->800
'release Holland'              ok=True  AP 4->4  DP 5->4  gold 800->800
'grant Holland more autonomy'  ok=True  AP 4->4  DP 5->4  gold 800->800
```

The DP charge is at `vassal_executor.py:263-269`, inside
`_execute_release_vassal` (`:246`): *"Releasing a vassal costs 1 DP."*
`_execute_make_vassal` (`:122`) has no such block. The comment at
`executor.py:1272` — *"Vassal commands … are free — they cost DP/gold, not
military AP"* — is true of three of the four and false of the one that matters.
**The game charges you to let a puppet go and charges you nothing to make
one.** That is the sentence the fix should be written against.

**(b) The game already has a priced road to conquest-vassalization.** A full
census of `create_vassal_conquest` callers finds exactly two:

```
backend/commands/vassal_executor.py:144   <- the free typed verb
backend/game_logic/settlement_ratify.py:678 <- the peace table
```

The settlement road (`settlement_ratify.py:660-690`) requires `current_state ==
"WAR"` **and** a ratified `subjugation` term that has been through the
settlement scorer and the accepting court's consent, and it passes
`garrison_size` so loyalty reflects the force that took the place. The typed
verb reaches the same function with `garrison_size=0` and none of that.

**This also makes it a GR5 asymmetry the census asserted away.** It wrote
"The AI never mints `make_vassal` … those run through `ai_diplomacy`", implying
parity. The AI's only road is `create_vassal_treaty` (`ai_diplomacy.py:1833`),
which needs acceptance — **no AI code path calls `create_vassal_conquest` at
all** (`enemy_ai.py` 0, `ai_diplomacy.py` 0, `turn_manager.py` 0). The free
conquest door is player-only.

## MISSED-4 — the dispatch has three copies, not two, and a 33-entry list has two

The report's §1 table names two dispatch seams (`_execute_one`,
`_execute_specific`). There is a third: `_execute_post_objection`
(`meta_executor.py:2186`, chain from `:2271`), with its own 18 action
literals. Measured set algebra over the three bodies (`x12`):

```
_execute_one            : 46 action literals
_execute_specific       : 15
_execute_post_objection : 18
in _execute_one but reachable through NEITHER of the other two after an objection: 29
  (make_vassal, cancel, charge, restrain, end_turn, status, help, meta_command,
   all four naval verbs, all reward verbs, every diplomatic_* verb, …)
in post_objection but in neither dispatch: ['bombardment']
```

**Honest narrowing of my own finding:** the 29 are a *latent* gap, not a live
one — `objection_actions` (`executor.py:1599`) is 12 entries
(`attack, defend, move, scout, recruit, fortify, stance_change, retreat,
drill, wait, hold, form_square`) and none of the 29 is among them, so nothing
reaches the post-objection chain today. And `bombardment` is not dead — it is
the defiance substitution (`defiance.py:173`,
`meta_executor.py:1879`). P4, structural.

Alongside it, `free_actions` is a **33-entry list literal duplicated
byte-identically in two files** — `executor.py:1273` and
`meta_executor.py:2208` — maintained by hand, with the AP decision in one and
the post-objection AP decision in the other. Any fix that prices `make_vassal`
must edit both or the objection path will disagree with the direct path. The
census printed the executor copy and did not name the second.

---

# What I could not verify

- **The live (`LLM_MODE=anthropic`) road** — same limit the report declares. I
  add one static fact it did not: `make_vassal`, `propose_white_peace` and all
  four strategic aliases are in `VALID_ACTIONS` (56 entries, verified by
  import), so the live model is explicitly told `make_vassal` is a legal
  action. Whether it emits it for a phrasing the mock refuses is **UNVERIFIED**
  and needs an IQ-9 cassette.
- **`combat_executor.py:10190`'s action value** — see EXR-3; not reproducible
  on the boot board.
- **The six `command_type` branches (EXR-10)** — not re-driven.
- Ambient AI combat confounds any per-marshal strength comparison across arms,
  so I make no claim about whether harm done to an assimilated enemy marshal
  persists after he goes home. The strength deltas I measured moved in both
  directions and are noise.

# Measurement hygiene (the same hazard EXR-11 reports, one round later)

The sibling kept working while I measured. `git status --short` at the start of
this pass showed two dirty backend files; by the end it showed **four**, with
`backend/commands/executor.py` and
`tests/test_fa_slice7_the_mock_speaks_plainly_2026_09_04.py` newly modified
(an in-flight slice self-named *"CX slice 1 — AN ADDRESS NEEDS NO COMMA"*).

**No measurement in this report is affected.** Every backend import ran against
the hash-verified pristine HEAD copy with an `assert PRIST in L.__file__` guard
at the top of each probe, and every repo file I read directly
(`tests/test_command_robustness_cr1_eval_harness.py`,
`tests/data/parser_golden_corpus.json`, `tests/test_enforcement_suite.py`,
`main.gd`, `diplomacy_wizard.gd`) was re-checked as `CLEAN` at the end of the
run. I wrote nothing outside the scratchpad.

Worth noting for whoever sequences the fixes: that sibling slice is working the
same seam as **MISSED-1** — addressing and answer-shape ahead of the executor —
so the two should land in one order, not concurrently.

# Probe index (`…/cx_recon/probes/refute2/`)

| file | what it measures |
|---|---|
| `x01_powercap.py` | WPS-B power cap per nation at boot; closes the report's own UNVERIFIED |
| `x02_p1_repro.py` | EXR-1 independently through `POST /command`; phrasing census; backend-guard census over `main.py` |
| `x03_question_bypass.py` | MISSED-1, on both the pristine and dirty trees |
| `x04_durability.py` | does the annexation survive? (20 end-turns) |
| `x05_what_persists.py` | per-turn unwind + assimilated-roster nationality |
| `x06_durable_prize.py` | control-armed alliance-web / threat / order-the-enemy measurement |
| `x07_seed2_and_repeat.py` | two more seeds + the empty-cooldown repeat |
| `x08_exr3_shadow.py` | first (worse) shadow probe + the pin mutation test |
| `x09_exr3_clean.py` | shadow claim isolated from parser noise with a literal marshal |
| `x10_exr456.py` | EXR-4 white-peace spy, EXR-5 log types, EXR-6 corpus, EXR-8 ACTION_DISPLAY |
| `x11_gate_rule_and_115.py` | EXR-6 under the gate's own rule; the 115 keywords |
| `x12_missed.py` | MISSED-3 prices, MISSED-4 three dispatches + duplicated `free_actions`, AI road census |
