# CA9 — the three design answers, August 9, 2026

> **Status: DECISIONS RECORDED, NOTHING BUILT.** The user's instruction was
> *"just document my answers, next session can code those then playtest
> everything including what you did."* No production code was written for any
> of the three rows below. The CA9 tiers-1+2 fixes that were already landed
> (21 commits, `4ab1cc6`..`16302e6`) are untouched.
>
> **This file is authoritative for these three decisions.** Build order and
> tracking rows live in `docs/STATUS.md` and `docs/DESIGN_REFINEMENT.md`.

---

## 1. Peace terms — "a short war should be hard to end"

**The user's answer, verbatim:** *"look at euiv, if war is short its way harder
to end avoids cheesing 1 battle for free cash. think deeply about this"*

### First, a reframing: F14 did not create the cheese, it exposed it

CA9-F14 changed the *recommendation* so its sign matches the war — a winning
France demands, a losing France offers. That is not the problem the user is
naming. The problem is that **the war score itself is cheap**, and F14 made
that visible by wiring the recommendation to it.

Before F14, at war score +3 Talleyrand said "pay them 80 g/turn". After F14 he
says "demand 50 g/turn". The second is *honest* and the first was not — but if
war score +3 is reachable by winning one skirmish two turns into a war, then
the honest recommendation is an invitation to farm.

**So F14 stays. The work is one layer down.**

### What this codebase does today (measured, `diplomacy.calculate_war_score`)

| Component | Cap | How it is earned |
|---|---|---|
| Territory | ±40 | +5 per enemy *starting* province held (8 provinces maxes it) |
| Battles | ±30 | **+3 per battle won**, with quiet-turn decay (−2/turn after 2 quiet turns) |
| Decisive | ±20 | decisive battles, capped at 2 per side |
| Capital | ±30 | +20 holding their capital, +10 contesting it |
| Ticking | — | war-objective accumulation |
| **Total** | **±100** | |

**The number that matters: battles + decisive = ±50 of a ±100 scale, earned
with ZERO territory taken.** Ten battle wins alone reach +30. Add two decisive
results and you are at +50 without besieging a single town.

Acceptance (`settlement_scoring`) reads war score plus relations, war
exhaustion (`min(20, exhaustion // 3)`), objective alignment, agenda mod and
side pressure. **There is no term anywhere for how OLD the war is.** Exhaustion
is the only time-like input, and it is slow and symmetric.

### What EU4 actually does, and why it is the right reference

Three mechanisms, and it is worth being precise about which one does the work:

1. **Battle warscore is hard-capped at 25% of total.** You cannot win a war on
   field victories. This is the direct analogue of the row above — and this
   game sits at roughly **50%**.
2. **Occupation is the bulk of warscore, and occupation takes TIME** — you must
   march, siege, and hold. This is what makes a short war unwinnable *on
   points*: not a rule that says "wars must last N months", but the simple fact
   that you have not earned anything yet.
3. **Peace cost scales with what you demand**, so a small warscore buys a small
   thing. EU4 never says "no peace yet"; it says "this is all you have earned".

The user's phrasing — *"if war is short its way harder to end"* — is EU4's
**emergent** result, produced by (1) and (2). That is the shape to copy: not a
timer, but a scoreboard where the cheap things are worth little.

### The three options, and my recommendation

**Option A — re-weight the scoreboard (EU4 mechanism 1).**
Lower the battle cap so field wins alone cannot reach the demand thresholds,
and let territory dominate. Illustrative: battles ±30 → ±15, decisive ±20 →
±10, territory ±40 → ±50. A brilliant unbeaten campaign that takes nothing is
worth ~+25; taking five provinces is worth +25 on its own.
*Cost:* pure retune of one function. Moves `BASELINE_SERIES` (acceptance feeds
AI decisions) and needs a flip-experiment attribution.
*Risk:* makes the game more siege-y. It also devalues the one thing this
game's combat is genuinely good at, which is worth weighing.

**Option B — a war-age term on acceptance (EU4 mechanism 2, stated directly).**
Add an explicit penalty to peace acceptance scaled by how young the war is —
e.g. −30 at turn 1 of the war, decaying to 0 by turn 8. Nobody signs a peace in
the first fortnight, so the "declare → win one battle → collect → peace out"
loop has no exit to run to.
*Cost:* one new component in the acceptance formula, reading `war_start_turns`
which is already serialized. No new state.
*Risk:* it is a rule rather than an emergent consequence, so it can feel
arbitrary if the copy does not explain it. It must be VISIBLE — the per-court
acceptance breakdown already names its components, so it would read as *"The
war is barely begun: −30"*, which is honest and teaches the rule in one line.

**Option C — both.**

**My recommendation: B first, then A as a tuning question at the same gate.**

B is the cheaper change, it answers the user's sentence directly, and it is
self-documenting through a surface that already exists. A is the deeper and
more EU4-faithful fix, but it is a balance retune that wants a played campaign
to judge — and the user has said they want to playtest next session anyway, so
A is better decided *after* that playtest than before it.

**One caution to carry into the build.** Both options make wars harder to end,
and CA9's own campaign already ended with *"a war with no way out"* at 26
turns. The complaint that produced this row and the complaint that a war
cannot be closed are two ends of the same dial. Whatever lands, the exit has
to stay reachable for a player who has genuinely won — which in practice means
watching the TERRITORY arm, since that is what a real victory looks like.

### Also on the record

The armistice half of F14 (the `gold_lump 1600` at war score +19) was a
declared scope extension and is included in "F14 stays". It was never before
the CA8-D2 gate, whose language covered only the peace arm's ≤200g sweetener.

### ✅ LANDED August 9, 2026 — landing record (authoritative for row 1)

**Option B built, option A not built** — the battle-vs-territory re-weight
stays deferred to a judgement after the playtest, exactly as this memo
prescribes. Single source `diplomacy.war_age_acceptance_mod`
(`WAR_AGE_PENALTY_MAX = 30`, `WAR_AGE_PENALTY_WINDOW = 8`, linear decay),
consumed in `diplomacy.calculate_acceptance` beside the R142 war-weariness
term it mirrors. Tests: `tests/test_ca9_row1_war_age_penalty.py` (28), 4-of-4
mutation sweep. Suite 16,874 → **16,904 / 3 skipped**, ruff clean, no `.gd`.

**Three deliberate design decisions beyond the letter of the ruling.**

1. **A white peace is exempt at any age** (`proposal_extracts_value` reads the
   DEMAND side only; sweeteners are what the proposer pays and are ignored).
   This is the answer to this memo's own caution that "both options make wars
   harder to END, and CA9's campaign already closed with *a war with no way
   out*". Mutual withdrawal is always signable; only extraction is gated. It
   also means buying your way out of a war you started badly stays available,
   which is a good move a player should keep.
2. **The armistice arms are included**, as a declared scope extension rather
   than something the gate said — the same shape F14's own armistice
   extension took. Reason: the stated goal is that the cash loop has "no exit
   to run to", and F14 measured the armistice sibling carrying `gold_lump
   1600` at war score +19, ~20× the peace arm. Penalising peace alone moves
   the cheese one door left. **Reversible in one line** (drop the two
   `armistice_*` entries from `WAR_AGE_PENALTY_TYPES`) if the user disagrees.
3. **The multilateral settlement scorer is deliberately NOT touched**, and
   the reasoning is recorded at the seam in `settlement_scoring.py`. It was
   built there first and removed: this memo prescribes reading
   `war_start_turns`, which is the *bilateral* map; the cheese is a bilateral
   loop; that scorer already carries `war_exhaustion` as its time-like input;
   and a congress settling a war inside that war's first eight turns is not a
   route real play reaches. Measured, the component fired **exclusively in
   fixtures** — it moved eight tuned contracts across five files and nothing
   else. Re-blessing eight blessed-number contracts for a term with no
   demonstrated live effect is how a real regression hides in the churn. If
   the playtest finds an early-cash route through the multilateral surface,
   the seam and its recipe are written down.

**What it actually does, measured.** The live effect is at the surface the
player uses — Talleyrand's own recommendation, which prices through
acceptance (NA-3 rider b). France winning on points (+30) against Prussia at
relation +20:

| war age | `generate_suggested_terms` demands |
|---|---|
| 1 turn | *(nothing)* |
| 9 turns | `gold_per_turn 174` |

That is the loop closing: ask your foreign minister what to demand for a
two-turn war and he now has nothing to suggest. Both arms carry a negative
control that re-runs them with the curve flattened and asserts the opposite,
so neither can pass against a constant 0.

**Two things found that this memo did not know.**

1. **An asymmetry I introduced and then fixed.** The bilateral read defaults
   `war_start_turns` to `current_turn` for R142's benefit — harmless for a
   *bonus*, wrong for a *penalty*, because it makes "start never recorded"
   indistinguishable from "declared this turn" and charges the full −30
   forever. The age term now reads key presence explicitly; unknown age →
   no penalty. Caught by a fixture, pinned, and mutation-tested.
2. **A pre-existing gap in IGR-D's carve contract, surfaced not caused.**
   `test_..._not_for_a_marginal_win` asserts a victor holding only Posen
   scores < 50. That is true at war age 0 (its blessed 34) and **false in a
   long war** (measured 54 at age 10) because `war_weariness` climbs to +20
   and nothing capped it for that clause. The age term is exactly 0 at that
   age, so the number is byte-identical to pre-row-1 master — the fixture had
   only ever been verified at an implicit age of 0. `_europe_world()` now
   models age 6 (a France that has broken Prussia's army and taken Posen
   manifestly is not one turn into the war), where both of IGR-D's bars hold
   at 58 vs 38, and the long-war case is pinned as its own named test so
   nobody files it later as a regression of this row. Whether an exhausted
   Prussia *should* concede a client after ten turns is a design question and
   a defensible yes; it is left alone and named.

**M1–M7 and `BASELINE_SERIES` byte-identical WITHOUT re-record — with a
reason, not a shrug.** A peace-acceptance change could plausibly move AI
behaviour, so it was measured: across all 14 directed pairs of the 7 boot
wars, the age term causes **zero outcome-band flips**. Every one of those
extractive peaces was already REJECT on hostile relations (France→Austria
−86 → −116; both reject), so no AI decision changes and the 40-turn series
cannot move. That also disposes of the concern that the 1805 boot — which
opens mid-war historically with all 7 wars stamped at turn 1 — would spend
eight turns unable to make peace: it could not make those peaces anyway.

---

## 2. The attack confirm popup — scope it to a real disaster, and to character

**The user's answer, verbatim:** *"only show popup if they are entering
potential disaster and general is cautious"*

### Today

`combat_executor._execute_attack` arms the muster-confirm interrupt when
`odds_band != "favorable"` — that is, on **"even" as well as "unfavorable"**,
for **every marshal regardless of personality**. Since CA9-F1 made the preview
count the enemy's reinforcements, "even" now happens far more often, so the
popup fires far more often. That is the texture the user is cutting back.

### The decision

Arm the confirm modal only when **both** hold:

1. the odds are genuinely bad — `odds_band == "unfavorable"` (below the 0.7
   floor), not merely "even"; **and**
2. the acting marshal's personality is `cautious`.

Everything else resolves without asking.

### Why the personality half is the interesting part

This is not just noise reduction — it is the game's own design language. An
aggressive marshal who charges bad odds without asking is *in character*, and
the consequence is his to own. A cautious marshal who stops to ask is Davout
being Davout. The popup stops being a UI gate and becomes a character beat,
which is what W6-5's literal doctrine did for objections.

**Consequences to hold in view when building:**

- The preview itself still prints, with honest numbers, on every attack. Only
  the *blocking* changes. The player does not lose information; they lose an
  interruption.
- A non-cautious marshal walking into an unfavorable fight now gets no warning
  at all. That is the intent, but it should be checked in play — it is exactly
  the shape CA9 filed as "the game let me commit". The distinction is that
  the numbers are now honest (F1), so it is an informed decision rather than a
  misled one.
- The CR-5 bad-odds gate is a **separate** surface with its own personality
  logic and is not in scope.
- Whatever the rule, the *same* predicate must decide the popup and the copy.

### ✅ LANDED August 9, 2026 — landing record (authoritative for row 2)

Built exactly as ruled. One predicate, `objection_v2.muster_gate_arms`
(`MUSTER_GATE_BAND = "unfavorable"` + `MUSTER_GATE_PERSONALITIES =
{"cautious"}`), consumed at the single gate site in
`combat_executor._execute_attack`. `even` no longer blocks anybody; only a
cautious marshal stops to ask. Tests: `tests/test_ca9_row2_muster_gate_scope.py`
(30). Suite 16,820 → **16,874 / 3 skipped**, ruff clean, no `.gd`.
**M1–M7 and `BASELINE_SERIES` byte-identical WITHOUT re-record** — correct by
construction, since the gate is guarded on `command is not None` and
`marshal.nation == world.player_nation`, so no AI behaviour can move.

The modal is now a character beat, so it speaks in the cautious register:
`marshal_voice.cautious_muster_halt` (3 rotated lines, deterministic, GR6),
spoken **only** behind a True from the predicate, with a falsifiable negative
that an aggressive marshal is never narrated as hesitating.

**Three things the build found that this record did not know.**

1. **The gate's surviving window is narrower than the ruling implies, and the
   severe case was already covered.** A cautious marshal at ≥2:1 raises a
   **V2a objection** — trust / insist / compromise, a richer decision with
   trust consequences — and it fires *before* the muster gate. Measured
   (enemy:own):

   | ratio | band | what the player meets |
   |---|---|---|
   | ≥ 2.00 | unfavorable | V2a objection |
   | 1.43–2.00 | unfavorable | **muster confirm** ← the gate's real window |
   | 1.00–1.43 | even | nothing (row 2 removed this) |
   | < 1.00 | favorable | nothing |

   So the ruling is coherent rather than redundant — whichever surface owns
   the severity band asks, and **the player is asked exactly once**. Insisting
   past an objection never yields a second modal (the post-objection path
   bypasses the gate). That is the CR-5 "objection-first ONE-modal legibility"
   guardrail, and it is now pinned in `TestTheTwoSurfacesDoNotStack` rather
   than assumed.

2. **The gate is not a guarantee even for the personality it is scoped to.**
   `objection_v2.apply_mood_variance` promotes a concern one level 10% of the
   time, so ~1 attack in 10 inside the gate's own window produces a blocking
   objection instead. This is intended (day-to-day mood) and is left alone,
   but it is the reason three test files needed the function neutralised —
   its own docstring prescribes exactly that — and it is pinned as real
   behaviour in `TestMoodVarianceCanPreEmptTheGate`. Anyone reading an "it
   gated yesterday and objected today" report should start there.

3. **A latent test-isolation defect, fixed in passing.** The
   `muster_endpoint` fixture never swapped `main_module.executor`, which
   carries per-marshal objection state (`major_objections_this_turn`) across
   tests — so that class's result depended on what ran before it. It now
   swaps the executor like the sweep-5 fixture always did. Found only because
   re-pointing the fixture at a cautious marshal made the objection layer
   relevant to it.

**Consciously flipped pins.** `test_w6_literal_doctrine.py::
test_literal_never_objects` asserted the muster confirm "is what catches"
a literal marshal ordered into terrible odds. Nothing catches him now, which
is a *stronger* statement of that file's own W6-5 doctrine — "generals who do
what they're ordered" — and the test says so. Gate fixtures in three files
moved from Ney to **Davout**, the roster's cautious French marshal: scoping a
gate by character means the fixture must have the character. One endpoint
assertion was also re-based from battle-outcome copy ("<name> leads the
charge", which never appears when the marshal *loses*) onto casualties, which
is the claim it was always trying to make.

**Not verified live over HTTP.** Port 8005 was held by a live session and I
did not disturb it. `TestMusterTypedAnswerEndpoint` drives the real FastAPI
app through `TestClient` (the same path minus the socket) and the change adds
no new response fields — only a message string — so there is no serialization
risk of the kind an HTTP pass exists to catch. The copy itself was read off a
real executor run. **The playtest still owns the feel question**, which is
the one thing none of this measures: a non-cautious marshal now walks into a
2.5:1 fight with no warning at all.

---

## 3. Grievances and popups — a revisit slice, not a patch

**The user's answer, verbatim:** *"we need to revisit grievences and popups in
general and check for issues, with everything here just mark answers mark it as
next dont code yet"*

So N4 is **not** getting a TTL bolted on. The whole channel gets looked at.

### What is already known to be wrong, as the starting list

- **N4 (P1, unfixed).** The pending marshal petition never expires, never
  re-validates, and is answered against LIVE state — so a turn-11 card served
  on turn 16 spends 1 AP on the wrong quarrel. It also blocks every other
  petition behind it: at least four petition-worthy events could not queue.
- **N21.** The drama channel has no dispatch budget — 13 marshal-drama lines in
  one briefing, flat and unranked. AI-6 landed a 2-per-dispatch cap on intent
  narration for exactly this failure mode; jealousy caps *fires* only.
- **N8.** "Separate Them" is a permanent, un-cancellable warning subscription —
  `separation_flagged` is never set False anywhere in `backend/`.
- **IGR-X7 family.** Capture routes fill popup keys without draining the queue.
- **The PopupQueue itself** now has 11 slots and a priority order that has
  accreted over many phases; nothing has audited whether the ordering still
  reflects what a player most needs to see.
- **The stash-and-raise discipline** (NA-6b, BD §14.1) is applied per-surface
  rather than centrally, and has already been got wrong twice.
- **NEW, added by row 2's build (Aug 9, 2026): the objection layer carries
  per-turn state on the module-global executor, and it leaks.**
  `DisobedienceSystem.major_objections_this_turn` gates a cap that *downgrades
  a major objection to a mild one* — so whether the player gets a blocking
  modal or a grumble depends on how many objections already fired, held on an
  object whose lifetime is the process, not the turn. A TestClient fixture
  that did not replace `main_module.executor` was order-dependent because of
  it. Worth auditing alongside the queue: this is the same class of defect as
  the popup slots — a blocking decision made from state nobody retires —
  and it sits on the surface the player meets most often.
- **Also for the audit's list, not a defect:** `apply_mood_variance` promotes
  a concern one level 10% of the time, which can turn a non-blocking advisory
  into a blocking modal. It is intended and should stay, but it means *no*
  popup-frequency measurement is reproducible without pinning it, and any
  before/after count for this slice must account for it.

### Shape of the slice

An audit first — enumerate every popup producer, its queue slot, its blocking
class, and whether anything ever retires it — then fix. The CA9 through-line
applies here too: several of these are surfaces asserting something the state
no longer supports.

---

## 4. Sequencing

The user's instruction: *"just document my answers, next session can code those
then playtest everything including what you did."*

1. Build these three (peace-terms model, popup scoping, grievance/popup
   revisit).
2. Then **one playtest covering everything** — the three new slices AND the 31
   CA9 rows already landed, which have not been played yet.

The playtest is also where the three items still owed from this session get
discharged: the visual sign-off on `Supply: Unknown` (region panel + map
tooltip) and the per-court fog line, and the open texture question of how the
muster popup feels once it is scoped.
