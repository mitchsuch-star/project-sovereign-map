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
