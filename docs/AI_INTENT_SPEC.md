# AI Intent — Phase Spec (v1.2, gate record + aliveness contract + gameflow pass)

> **Status:** **DESIGN GATE HELD July 20, 2026.** The six open questions of v0.1 are decided and
> recorded in **§6, which is authoritative**. Nothing is built yet; the build may begin against this
> document without a further gate, except where §6 names a re-check.
> **v1.1 (July 20, 2026):** adds §3.4, the **great-power aliveness contract** — the assurance that
> Austria, Prussia, Russia and Britain feel like distinct political actors pursuing their own designs
> and conducting real politics *with each other*, not just posturing toward France. Additive to the
> gate; it hardens the DoD and AI-V acceptance, it does not reopen §6.
> **v1.2 (July 20, 2026) — the gameflow pass.** A creative review asking one question the first two
> revisions did not: *what does the player actually do, turn to turn, once this ships, and what can
> still astonish them?* v1.1 is a correct simulation spec and an incomplete game spec. Five additions,
> all additive, none reopening §6: **§3.5** the mirror (Europe's reading of France, shown to France) ·
> **§3.6** where the surprises live — the fog boundary sharpened from "no fog" to *no fog on
> dispositions, fog on agreements and timing*, plus emergent designs and the volte-face · **§3.7**
> Britain as a contested auction rather than a wall · **§4.2b** the participation surface, which turns
> pin 3 ("the player is never a spectator") from a limit into a mechanic · **§4.6a** the named beats
> and the tempo rule. **§7a** adds the seven historical scenes as a falsifiable acceptance list, and
> **§9** records the review's own dispositions and the honest scope cost. Where v1.2 amends v1.1 it
> says so in place.
> **v1.2 also carries a correction to its own first draft (§9 rows 12–13).** That draft answered
> *"can this surprise me?"* and mistook it for *"will this differ next time?"* — the AI layer has
> **zero** randomness (`agendas.py`, `ai_diplomacy.py` and `coalition.py` contain no `random` call
> between them) and the project has **no campaign seed**, so every campaign would open identically
> and diverge only as the player forked it. **§3.8** adds the serialized campaign seed and scopes what
> it may perturb (the bars, never the choices); **§5 pin 14** fences it; and the AI-V acceptance run
> becomes an **N-seed sweep**, because every §7 number had been specified against a single
> deterministic trace.
> **§3.8 left one question open and the user decided it the same day: ✅ D7 — the *opening* is seeded
> too, within authored historical bounds.** **§6 D7** is the gate record and **§3.8.1** is the
> envelope that makes "within bounds of history" falsifiable: the bounds are **authored content, not a
> formula** (a value with no authored band never varies), the map/roster/`starting_wars`/deck-content/
> marshals/statecraft are **fixed on every seed** while **dispositions** vary, the **historian test**
> is a hard pin on all seeds, and `SOVEREIGN_SEED=historical` reproduces today's boot byte-for-byte so
> the existing suite needs no edit. Pins 1 and 14 are narrowed, not deleted.
> **Motivating evidence:** `docs/audits/CREATIVE_AUDIT_2026_07_19.md` §2.1, §3, §7 + the AI
> decision-architecture map taken at `b4b6326`, **re-verified against master at `12636a6`** for this
> revision (§0.1 records four corrections the re-verification forced).
> **Relationship to the NA arc:** this does not replace Nation Agendas. NA-0..NA-6d built the
> *content* of what nations want and the machinery that consumes it once a war exists. This phase
> builds the **will** — the missing first link — and de-centres the world from France.

---

## 0. The finding this phase exists to fix

The July 19 audit asked two questions and got one good answer and one bad one.

**Good:** nations that are *already at war* now visibly pursue their designs. Britain took Flanders,
Amsterdam, Gelderland and Brabant on the `low_countries` deny agenda and then sent a status-quo
settlement to bank it. Austria massed both archdukes on Milan for `redeem_italy`. That is the NA arc
paying off exactly as intended.

**Bad:** nothing else in Europe ever does anything. Over 40 turns of real AI play (through
`TurnManager.end_turn`, not `advance_turn`): zero formations, zero agenda shifts, and no border
movement except by nations already at war. Tracing it produced a finding larger than the one I went
looking for:

> **No AI nation can decide to go to war. About anything. Ever.**

The evidence is unambiguous and, in places, deliberate:

- Every `PEACE → WAR` edge in the codebase is a cascade (call-to-arms), a vassal auto-join, a
  negotiated entry, an armistice expiry, a rebellion — or `coalition.form_coalition()`.
- `enemy_ai.py` never imports `declare_war` or `set_diplomatic_state`. Every targeting path is
  pre-filtered to nations already at war (`is_at_war` gates at `enemy_ai.py:595, 1406, 1434, 3029,
  3114, 3194, 3862, 4292, 4583, 4656`), so the auto-declare seam in `combat_executor.py` is
  unreachable from an AI-issued attack.
- Agendas influence *target choice only*, downstream of the ratio/threshold gates — the code says so
  at `enemy_ai.py:2669` ("the ratio/threshold gates already ran").
- `ai_diplomacy.py:1067-1073` states the absence as a decision: *"no unilateral AI declare-war path
  in NA-5 — the coalition system remains the war-maker."*

And the war-maker that *does* exist is not a decision at all — it is a **global anti-France threat
scalar**. `form_coalition()` does not take a target: it binds `france = world.player_nation` at
`coalition.py:1323` and every member declares on that value at `:1339`. The France-centricity is
explicit elsewhere too: the war-declaration threat bump fires only when `aggressor ==
world.player_nation` (`diplomacy.py:7658`), and `hegemony_passive` computes a non-player hegemon's
pressure correctly and then **discards it because there is nowhere to put it**
(`coalition.py:1739-1745`, comment: *"v0.1 France-targeted scalar, D2 will generalize"*).

**The consequence, stated plainly:** Europe is not a continent of powers with interests. It is one
player and nineteen nations whose entire foreign policy is a posture toward that player. Five of ten
nations with authored decks boot at war with nobody, two of them holding *acquisitive* designs
(Prussia wants Hanover — adjacent, undefended; Sardinia wants Savoy restored) that they will hold,
unpursued, until the sun burns out.

That is why no formable ever fires. It is also why the world feels like a diorama.

### 0.1 Four corrections from re-verification (v1.0)

v0.1 made four claims that did not survive a second pass. All are recorded rather than quietly
edited, and **each one changes the build**. *(The heading read "Two corrections" through v1.1 while
listing A–D; corrected in v1.2.)*

**Correction A — `war_objective = "conquest"` is not a dead branch with no caller.** It is at
`diplomacy.py:7577-7580` as described, and it fires when *neither* party is the player. But there are
two reachable callers: `meta_executor.py:2108` (the `trigger_commitment_paradox` debug cheat, which
asserts `player not in (attacker, defender)` and hits the branch deterministically) and
`combat_executor.py:3482` / `:3532` (the auto-declare-on-attack seam, live for any non-player
attacker). The accurate statement is: **no *production AI* caller exists**, because
`enemy_ai.py`'s targeting is `is_at_war`-gated end to end.

*Why this changes the build:* the shortest correct path to an AI war is **not** a new declare-war
call in `ai_diplomacy.py`. It is to let the intent layer decide, then let the AI attack a nation it
is not yet at war with and have `combat_executor.py:3482` do what it already does. AI-3 should
**reuse that seam** rather than open a second one. GR5 is satisfied for free, the objective is
already pre-provisioned, and there is exactly one PEACE→WAR path to test. AI-3's job shrinks to
*deciding* and *announcing*; the declaration plumbing exists.

**Correction B — generalising threat is not a "small wire". It is the largest engineering item in
the phase.** `add_threat(world, amount, source_key)` has **no target parameter**
(`coalition.py:667-690`). It mutates one clamped int, `world.threat_level`, plus a flat
`threat_sources_this_turn` list whose entries carry no target field
(`world_state.py:748-749`). Both are serialized (`world_state.py:5188-5189`, `:5759`, `:5768`).
`threat_level` is read in **16 backend modules (73 references) and 10 more in `.gd`**. "Threat
accrues against whoever is behaving threateningly" means converting a serialized world scalar into a
per-target map across the diplomatic, settlement, ledger, dispatch and advisory layers.

*Why this changes the build:* AI-4 gets a **migration contract** (§4.4a) and is the phase's
highest-risk slice, not a footnote inside it.

**Correction C — two things v0.1 proposed to build already exist, in partial form.** Both must be
*generalised*, not invented, and describing them as new would have produced duplicate systems:

- **A bandwagon rung is live.** `ai_diplomacy.py:1094` ("P-Bandwagon") already fires when the player
  is hegemon at ≥50% bloc share against a non-hostile minor/secondary outside a rival bloc. §3.1's
  `bandwagon` is that rung, widened to any hegemon and driven by intent instead of bloc share alone.
- **An AI-vs-AI diplomatic path is live but nearly untested.** `process_ai_ai_diplomatic_phase`
  (`ai_diplomacy.py:1954`, called from `world_state.py:7061`) runs adjacency rivalry drift and a
  pairwise treaty loop capped at 2/turn. But its ladder is **upgrade-or-downgrade only —
  `_evaluate_ai_ai_proposal` can never return a war** — and `_ai_ai_acceptance:2087` carries a July
  2026 fix comment recording that the initiator-side check had been scoring a self-pair, so **zero
  AI-AI treaties had ever ratified** before it. AI-2 extends a real but effectively unexercised path;
  it should expect to find bugs there and budget for them.

**Correction D — a live cache defect the intent layer would otherwise inherit.** `agendas.py:288`
documents `_agenda_cache` as "cleared by `invalidate_active_nations_cache()`". It is not:
`WorldState.invalidate_bloc_members_cache` (`world_state.py:1682`) clears only the bloc caches, and
the sole direct clear of `_agenda_cache` is `formations.py:488`. In practice the agenda cache
self-heals on the turn key alone, so a mid-turn conquest or diplomatic flip does not refresh it.

*Why this changes the build:* principle 3 says to cache intent "on the `get_active_agenda` idiom."
Doing that literally would inherit the defect, and intent is read at more mid-turn moments than
agendas are. **Fixing the agenda-cache invalidation is a prerequisite of AI-1**, not a drive-by — and
it must be landed and pinned *before* intent caches anything, or every later slice debugs through it.

---

## 1. Thesis

**Give every nation a will of its own, legible to the player, expressed in peace as well as war.**

A nation should want something, weigh what it is willing to pay for it, try the cheap instruments
first, and — when the design matters enough and the moment is right — go to war for it, against
whoever is in the way, including nations that are not France.

The player should be able to *see* this happening and *trade* on it: play the courts against each
other, buy off a design, arm someone else's grievance, or watch two rivals exhaust themselves while
France rearms. Today none of that is possible because there is nothing to play against.

**The historical claim underneath it.** In 1805–15, powers rarely declared war out of nothing. They
were **bought** (Prussia takes Hanover at Schönbrunn, December 1805, in exchange for Ansbach, Cleves
and Neuchâtel), **aimed** (Napoleon points Russia at Sweden at Tilsit; Britain subsidises whoever
will march), **bandwagoned** (Bavaria, Württemberg, Baden in 1805; the Confederation of the Rhine in
1806), or went to war because a bargain was **reneged on** (Prussia mobilises in 1806 when Napoleon
offers Hanover back to Britain — the road to Jena runs through a broken compensation, not through
ambition). A model that only knows "escalate alone until you fight" would be both less fun and less
true. §3 encodes the other modes.

---

## 2. Design principles

1. **GR5 — one executor, both sides.** Intent produces the *same* actions the player can take,
   through the *same* seams. An AI war declaration goes through the existing `declare_war` seam at
   `combat_executor.py:3482` (§0.1 Correction A), not a private path. If a behaviour cannot be
   expressed as an existing action, that is a signal the action is missing, not that intent needs a
   back door.
2. **GR6 — no LLM in the decision.** Intent is derived, deterministic, and testable. The LLM may
   *voice* an intent that was already decided; it may never choose one.
3. **Derived over serialized.** Intent is a *reading* of the world (agenda + situation + relations +
   force), recomputed and per-turn cached on the `get_active_agenda` idiom
   (`agendas.py:294-299`: turn-keyed `_agenda_cache`, cleared by `invalidate_active_nations_cache`).
   Serialize only what genuinely cannot be re-derived — and note that **the ladder's own history is
   in that category** (§5.8).
4. **Legibility is the feature, not the reporting of it.** An intent the player cannot perceive is
   indistinguishable from randomness. Every intent strong enough to move armies must be readable
   *before* it moves them (§4.6).
5. **Symmetry de-centres France; it does not dethrone her.** Threat, coalitions, grudges and
   settlements must work between any two powers. But 1805 *is* a France-centred decade, and the
   campaign's central pressure is the anti-France coalition. Generalise the machinery; keep the
   gravity (§6 D3).
6. **Nothing new becomes mandatory.** Every mechanic boots dormant or neutral on the authored 1805
   opening; the historically-correct opening must not shift because the engine grew a new appetite.
7. **Counter-play before consequence.** No intent mechanic lands without the instrument that answers
   it landing in the same slice. A war the player could not have prevented is a cutscene.
8. **Great powers have character, not just targets.** A living Europe is not five nations running the
   same ladder at different provinces. Each major power must climb the ladder *its own way* — the
   instrument it reaches for first, how it answers coercion, whether it fights alone or builds a bloc.
   This is the difference between "the AI wants Hanover" and "*that is exactly what Prussia would
   do.*" It is the aliveness contract of §3.4, and it is derived, not LLM-voiced (principle 2 holds).

---

## 3. The model — what "intent" is

An **Intent** is a derived record answering four questions about one nation:

| Field | Meaning |
|---|---|
| **want** | the objective — an agenda design, a survival need, an opportunity |
| **against** | who stands in the way (may be nobody; may not be France) |
| **weight** | how much this nation cares, 0–100, derived from agenda type, proximity, history |
| **price** | what it is currently willing to pay: nothing / diplomacy / gold / a war |

`price` is the spine. It is a **ladder, climbed in order**, and this is what makes intent read as
statecraft rather than aggression:

```
  indifferent → ask → buy → align → bandwagon → coerce → fight
                (proposal) (subsidy, (alliance, (serve the  (ultimatum) (declare war)
                            gift)     guarantee) strong for
                                                 payment)
                                  └── sponsor ──┘  (branch, not a rung:
                                                    pay someone else to fight)
```

A nation only reaches `fight` after the cheaper rungs have been tried and failed, or are structurally
unavailable. This is the single most important behavioural claim in the spec: **war is the bottom of
a ladder, not a dice roll.** It also gives the player counter-play at every rung — a design you buy
off never becomes a war.

`weight` gates how far up the ladder a nation is willing to climb. A `guard_neutrality` design never
reaches `coerce`; a `survival` intent starts near the top.

### 3.1 The two rungs v0.1 was missing

v0.1's ladder modelled one nation escalating alone against a holder. That is the *rarest* mode in the
period. Two additions, both cheap, both historical, both counter-play surfaces:

- **`bandwagon`** (between `align` and `coerce`). A nation whose design is blocked by a power it
  cannot beat may instead **serve that power for payment** — accept a subsidy, join its bloc, or take
  compensation elsewhere. This is Prussia in December 1805 and the Confederation of the Rhine in
  1806. It gives the hegemon — usually the player — a way to *buy peace* rather than only deter war;
  without it, every strong France produces a uniformly hostile Europe, which is neither the history
  nor the better game. **Per §0.1 Correction C this rung already exists** as P-Bandwagon
  (`ai_diplomacy.py:1094`), gated on player-hegemon + ≥50% bloc share. The work is to widen it to any
  hegemon and drive it from intent rather than from bloc share alone.
- **`sponsor`** (a branch, not a rung). A nation with high `weight` but insufficient force does not
  climb to `fight`; it looks for a **proxy** — subsidising a third party's existing design against
  the same target. This is Britain's entire foreign policy and Napoleon aiming Russia at Sweden. It
  is the mechanism by which the player can *arm someone else's grievance*, and it routes through the
  already-generalised `get_paymaster_nation` (NA-3 §5.7).

### 3.2 Opportunism — the gate that makes wars land at dramatic moments

v0.1's restraint gates all asked *"can I afford it?"*. History mostly asked **"is he busy?"**.
`weight` receives an **opportunism term**: a coveter's willingness rises sharply when the holder (or
the holder's protector) is already at war, committed elsewhere, in a spiral, or bankrupt.

This is not a balance knob — it is the difference between AI wars arriving at random and arriving
*while France is deep in Austria*. It is also self-limiting: it decays the moment the victim's
situation improves, so it produces vulture wars rather than permanent aggression.

### 3.3 Compensation creates an obligation, and breaking it is the strongest casus belli

The counter-instruments in §6 D5 are not one-way purchases. When a design is **bought off** — the
coveted province ceded, an equivalent granted elsewhere, or an indemnity paid — the bargain becomes a
**standing expectation**, in the same idiom ES-7 already uses for marshals. Satisfying it keeps the
peace. **Reneging on it, or handing the coveted object to the coveter's enemy, is the highest-weight
casus belli in the game** and may skip ladder rungs.

That is precisely the road from Schönbrunn to Jena, and it means the buy-off instrument has teeth in
both directions: it is a real solution *and* a hostage the player has given.

### 3.4 The great-power aliveness contract

Everything above describes the *machinery*. This section is the **assurance that the machinery
produces recognisable political actors** — that Austria, Prussia, Russia and Britain feel alive,
goal-oriented, and engaged in real statecraft *with each other*, not merely nineteen postures aimed
at France. It is the answer to the audit's core wound (a diorama of one player and inert nations) and
it is the thing most likely to fail silently: the intent layer could ship, every court could climb
the same ladder correctly, and Europe could still feel like a spreadsheet because every power plays
identically. This contract exists to make that outcome a **failing test**.

**Each major power gets a `statecraft` profile** — a small, per-nation, *derived* weighting over the
same ladder and instrument-selection every nation uses. It is not a new personality system and it
carries no LLM (principle 2, principle 8). It generalises what the codebase already gestures at —
`NATION_DESIRE_PROFILES` and `TALLEYRAND_COMMENTARY` in `diplomatic_templates.py`, and Russia's
existing 1.1 honour bias — into a full statecraft weighting. It biases four things only: **which rung
the power prefers**, **which instrument it reaches for first**, **how it answers being coerced**, and
**a `weight` modifier on its design**. Nothing else.

| Power | Its design | Statecraft — *how* it pursues it | Reaches first for | Under coercion | Historical anchor |
|---|---|---|---|---|---|
| **Austria** | `redeem_italy` / German primacy | The **aggrieved patient revanchist.** Twice-beaten (1797, 1800); will wait years for the right partner and is very hard to make quit. Fights inside a coalition, rarely alone. | `align` / build a bloc | **Hardens** — coercion confirms the grievance | The Third Coalition; Metternich's patience |
| **Prussia** | `hanoverian_prize` / north-German primacy | The **hesitant opportunist.** Terrified of choosing the wrong side; sells its neutrality, takes compensation, joins the strong — and defects when the wind turns. The archetypal `bandwagon`er. | `buy` / `bandwagon` | **Folds, then resents** — the reneged bargain (§3.3) is its one true casus belli | Neutrality 1795–1806 → Schönbrunn → Jena |
| **Russia** | `arbiter_of_europe` | The **distant arbiter.** Chases prestige and the balance of Europe, not land next to home; intervenes far from its own borders on principle, and leads or `sponsor`s coalitions. Withdraws sharply once prestige is served or catastrophe strikes. | `sponsor` / lead a coalition | **Escalates on honour**, then reverses hard | Austerlitz → Tilsit reversal (the 1.1 honour bias, already live) |
| **Britain** | `low_countries` deny | The **paymaster behind the Channel.** Never wants a land war of its own; funds everyone who will march and denies the Scheldt. Its field armies and continental gains are as beatable as anyone's — its *core* (the treasury, the will to keep paying) is what sits behind the moat. | `sponsor` (the branch, not the rung) | **Reached by the lever, not the ultimatum** — a land threat cannot touch the core, so it answers with more gold; but the Continental System strangles its trade *now*, and Ireland/invasion reach it once naval (DEF-5) lands | Pitt's subsidy system; the Berlin & Milan Decrees answering it |

**Britain is reachable — through the right lever, not the front door.** This matters enough to state
plainly, because a Britain that *cannot* be coerced is an unbeatable paymaster with no counter-play,
which breaks principle 7. Britain is hard, not impossible: you beat its expeditionary corps and strip
its continental holdings on land like any power, and you reach the *core* it hides behind the Channel
by **cutting its trade** (the Continental System the game already models) — and, once the DEF-5 naval
layer lands, by **Ireland and the invasion threat**. Its `statecraft` answers a land ultimatum with
gold precisely so the player learns the front door is the wrong door; the reward for finding the
economic lever is that the gold finally stops. Until then Britain keeps paying, which is the correct
and historical frustration, not a dead end.

The secondary powers (Sardinia, Ottoman, Sweden, Denmark) get *lighter* profiles — a preferred rung
and a coercion reaction, no more — because they are texture, not protagonists; over-characterising
them is how the narration budget (§4.6) blows.

**Politics with each other, witnessed.** Aliveness is not only *toward* the player. The contract
requires the majors to conduct the AI-vs-AI game legibly: Austria courting Russia into a bloc,
Britain's gold appearing in a war it never joined, Prussia bandwagoning to the strong and later
defecting, two powers exhausting each other while France rearms. AI-4's third-party settlements and
the converged AI-vs-AI diplomacy path (AI-2) are what make this real; §3.4 is the assurance that when
they run, they run *in character* and the player can *read* the character from the ledger and from
Talleyrand — not just infer a target.

**Where it must not go.** No LLM in the choice (principle 2). No new serialized personality object —
`statecraft` is a per-nation constant table read by the ladder, derived. It must not perturb the 1805
boot (§5 pin 1). And it must not collapse under stress into "every power defends its capital
identically" — the homogeneity guard below is the pin that forbids exactly that.

**The minors are alive through *timing*, not character.** Bavaria, Saxony, Denmark, Sweden and the
rest get light profiles on purpose, and that is not a compromise — a minor power's drama in this
period was never its statecraft, it was **the moment it chose a side**. Bavaria in 1805, Saxony in
1806, Bernadotte's Sweden in 1812: the little states decided campaigns not by having designs of their
own but by flipping at the hinge. So the assurance for a minor is not "does it have a style" but
**"can it flip, late, and does the flip matter?"** — which is `bandwagon` plus the vassalage on-ramp
(§4.5), and it costs no narration budget because a flip is a beat (§4.6a), not a line.

### 3.5 The mirror — France has an intent too, and the player should see the version Europe reads

Everything above describes what the player can learn about *other* courts. The cheapest and most
transformative surface in the phase is the inverse: **the player's own row, filled in with Europe's
reading of France.** What do the courts believe Napoleon wants? Who do they think he is coming for?
Where do they place him on the price ladder?

It costs almost nothing — once `threat_by_target` exists (§4.4a) and intent derives from observable
facts, France's perceived intent derives from the *same* function reading the *same* observables:
conquests taken, armies standing near whose border, asks refused, bargains kept or broken, coalitions
provoked. No new machinery, one more call.

What it buys is out of all proportion:

- It converts the ledger from a spreadsheet about foreigners into a **mirror**. "Why is Prussia
  arming?" acquires an answer, and the answer is something the player did.
- It makes the counter-instruments legible as *reputation management*, not just as purchases.
- **The player can be wrong about how they are seen.** Perception is derived from deeds, not
  intentions — a defensive massing on the Rhine reads as a threat to Hanover whether or not it was
  meant as one. That gap between what France means and what Europe reads is a surprise engine that
  costs a single derived row, and it is the most historically honest thing in the phase: the road to
  the Third Coalition ran through exactly that misreading.

*Pin:* France's perceived intent is derived from observable French actions only. It never reads the
player's plans — there are none to read (GR6) — and a player who does nothing must drift *down* the
perceived ladder over time, so that restraint is a legible strategy and not merely an absence.

### 3.6 Where the surprises live

D4 makes the ladder fully open, and that is right: this project has a standing rule that diplomacy
has no fog, and hiding a court's disposition would be the one place a hidden number could make the
ledger lie. But a world with no fog and no uncertainty is a train timetable, and a phase whose entire
output is *legible* runs a real risk of being *predictable* — which is a worse failure than the
diorama it replaces, because at least a diorama does not pretend. Surprise has to come from
somewhere legitimate. There are four sources, and none of them requires the ledger to lie.

**1. Timing.** Already decided in D4, and it carries more weight than it looks: you know Prussia will
coerce, you never know that this is the turn. §3.2's opportunism is what makes the answer *dramatic*
rather than random — the moment arrives when France is committed elsewhere.

**2. The sealed article — the fog boundary, sharpened.** "Diplomacy has no fog" is a rule about
**dispositions**: what a court wants, who it wants it from, what it will pay. It has never meant that
France is a party to every bilateral treaty in Europe, and it should not. When two AI courts strike a
bargain — a sponsorship, a compensation, an understanding about a third party's provinces — the
**fact of the meeting is public and the article may be sealed.** The player sees that Russia's envoy
was in Berlin; they do not automatically see what was agreed.

This is not a fog exception smuggled in; it is the fog boundary drawn in the historically correct
place. The secret article is *the* characteristic diplomatic instrument of this period — Tilsit's
secret articles, the Reichenbach conventions, the partition understandings — and modelling its
absence is a bigger distortion than modelling it. It also finally gives intelligence and Talleyrand a
job in the diplomatic layer: a sealed bargain is **discoverable** (rumour, a diplomat's read, a
defection, the payment showing up in someone's ledger), and §5 pin 12 requires that every sealed
article have at least one route to being learned *before* it bites. A surprise the player could not
possibly have seen coming is not a surprise, it is a cheat.

**3. Emergent designs — the world writes content the author did not.** Every design in the game today
is authored in a deck. The most interesting designs in history were not: they were *acquired*, by
being humiliated. Prussia's design after Jena was not Prussia's design before it. So a nation that is
partitioned, stripped of a capital, forced into a punitive settlement, or has a standing compensation
bargain broken (§3.3) may **promote a grievance into a design** — entering the deck like any other,
so every downstream system already built (NA-1 legibility, NA-2 acceptance mod, NA-3 resolve and
target bias, NA-6 formation) consumes it for free.

Bounded deliberately: promotion only from the serialized grievance record (never from a vibe), at
most one emergent design per nation, and it is announced as a beat. This is also what makes the DoD's
"≥1 agenda shift" an actual *system* rather than a deck-order tick — and it is the single mechanic
most likely to produce a campaign the player wants to tell someone about.

**4. The volte-face.** §3.4 gives Russia "reverses hard" as an adjective. Make it a mechanic: a great
power that is **beaten and then courted** — rather than beaten and humiliated — can reverse in one
settlement, from enemy to partner, and be aimed at a third party. That is Tilsit, and it is the
single most dramatic diplomatic event of the period. It is also a *player-caused* surprise, which is
the best kind: it rewards the choice to be generous to a broken enemy, an option the game currently
gives the player no reason to consider. It routes through the existing settlement layer plus the
`sponsor` branch, and it gets its own beat (§4.6a).

*What is never hidden:* a nation's want, its target, its current rung (D4), its stated war reason
(§5 pin 4), or the fact that a war is coming (§4.6 fore-warning). Fog lives in **agreements and
timing** — never in dispositions.

### 3.7 Britain is an auction, not a wall

§3.4 (v1.1) established that Britain is reachable by the economic lever rather than the front door,
and that until the player finds the lever "Britain keeps paying, which is the correct and historical
frustration, not a dead end." That is true and insufficient: a frustration the player cannot *play
against* in the meantime is still a wall, just an explained one.

The fix is already three-quarters built. `get_british_subsidy_recipient` (`coalition.py:1084`) picks
who gets paid; `_process_british_subsidy` (`:1119`) pays them; `get_paymaster_nation` /
`get_paymaster_subsidy_amount` (`agendas.py:778, 822`) already generalise the paymaster posture beyond
Britain. Three additions turn a standing drain into a game:

- **The subsidy is visible.** The player can see who Britain is paying and how much. Today the most
  consequential fact about why Austria will not settle is invisible.
- **The subsidy is contestable.** France may **outbid** — through the D5 compensation instrument, or
  by paying directly — for a recipient's alignment. Britain's purse is finite and its own; an
  outbidding war over Austria is the paymaster duel the period actually ran on, and mechanically it
  is a comparison inside a function that already exists.
- **The recipient can be made not worth funding.** Peace, compensation, vassalage or defeat each
  remove a recipient from the list. The player learns that the way to beat a paymaster is to buy or
  break its clients, not to march at it — which is the lesson §3.4 wants taught, delivered as a
  strategy rather than as a wall.

The Continental System remains the way to stop the gold at its source (§3.4). This section is what
the player gets to *do* about Britain in the fifty turns before that lands.

### 3.8 Variance — will the second campaign differ from the first?

§3.6 answers *"can this surprise me?"* — within one playthrough. It does **not** answer *"will this
be different next time?"*, and those are separate properties that the v1.2 pass conflated. Asked
directly, the answer against the code as it stands is **no**, and the measurement is stark:

| Layer | `random` uses |
|---|---|
| `agendas.py` | **0** — `get_active_agenda` is "first predicate that holds wins" over an authored deck |
| `ai_diplomacy.py` | **0** |
| `coalition.py` | **0** |
| `enemy_ai.py` | 3, in ~4,600 lines |
| **A campaign seed anywhere in the project** | **none exists** |

Intent as specified is a pure function of world state, so it inherits this exactly. Combined with §5
pin 1 (the 1805 opening is byte-identical), the consequence is unavoidable: **the opening moves of
every campaign are identical, and stay identical until the player's own choices have moved the world
state far enough to fork it.** Prussia reaches for Hanover on the same turn, Britain pays the same
client, the same crisis brews at the same moment. The second campaign teaches you the timings; the
third is a script you already know. That is a fair description of a failure this phase would ship
with, and it is not one §3.6 addresses.

**Determinism here is load-bearing, so the fix cannot be `random()` at the decision.** M1–M7
byte-identical, the boot pin, the §4.4a threat-series pin and §5 pin 8's save/load determinism all
depend on reproducibility. The answer is a **serialized campaign seed**: fixed at world creation,
written through `to_dict`/`from_dict`, deterministic *within* a campaign (a save reloads to the same
Europe, and any pin may fix the seed to a constant and keep its exact numbers), varied *across* them.

**Where the seed is allowed to bite — the bars, not the choices:**

1. **Threshold jitter.** It perturbs `weight`, the opportunism trigger, ladder dwell time and
   cooldown lengths within a small band. Prussia still wants Hanover — **character is fixed** (§3.4);
   what moves is *when* she reaches for it. This is the cheap, high-yield lever, because the system
   compounds: a few turns' difference in one court's timing changes which war France is busy with,
   which changes who is opportune, which forks the mid-game entirely.
2. **Tie-breaks.** Where two designs or two targets score equal, the seed chooses. Today "first
   predicate wins" quietly makes authored deck order into destiny, and this costs nothing to fix.
3. **Weighted late, not early.** The band widens with turn number. Turn 1 of 1805 *should* look like
   1805 every time — that is a feature, not sameness — and the divergence should arrive as the
   campaign earns it.

**What the seed must never do: make intent unreadable.** D4 is untouched. The jitter moves a number;
the ledger shows the number it actually moved to. The player always reads the truth about Prussia's
weight — they simply cannot carry last campaign's *timings* into this one. The seed invalidates
**memorisation**, never **understanding**, and that distinction is the whole design.

**Sequencing consequence: the seed lands with AI-0/AI-1 or not at all.** Introduced late, every pin
written against "the" deterministic trace has to be revisited, and the phase would pay for it twice.
It is a small slice with an outsized ordering constraint.

> **✅ DECIDED July 20, 2026 — the opening varies too, within authored historical bounds** (user:
> *"yes this should be seeded but within bounds of history"*). The gate decision is **§6 D7**,
> authoritative; the envelope that makes "within bounds of history" a *test* rather than an intention
> is **§3.8.1**. §5 pin 1 is narrowed accordingly, not deleted.

### 3.8.1 The historical envelope — what "within bounds of history" means, concretely

D7 raises the obvious risk: "seeded opening" is one bad afternoon away from Prussia booting at war
with Spain over Sicily. The envelope is what forbids that, and its governing principle is a single
structural choice:

> **The bounds are authored content, not a formula.** Every seeded value is an authored range sitting
> beside the value it varies, in `europe_1805.json` — the same file that already carries
> `nation_relations` (29 pairs), `diplomatic_states`, `starting_wars`, `agendas` and `threat_level`.
> **No authored band → no variance.** A designer opts each dimension in by writing its range.

That makes historical fidelity **reviewable by reading the scenario file**, enforceable by
`modding/validator.py` like every other scenario block, and free for modders. It also makes
ahistorical drift *structurally impossible* rather than merely unlikely: the engine cannot invent a
range it was not given, so no future slice can widen the opening by accident.

**Tier 1 — fixed. The identity of the scenario; never varies on any seed.**

Province ownership and the nation roster · capitals · `starting_wars` (the Third Coalition *is* the
scenario) · **deck *content*** — which designs a nation holds, because those designs are the history ·
the marshal roster with its MC-2/MC-3/MC-4 skills, personalities and relationships · treasury,
manpower and force levels (the E1 band is blessed and calibrated; §5 pin 1 keeps them) · the §3.4
`statecraft` profiles, because Austria is Austria.

**Tier 2 — banded. What was genuinely contingent in 1805, and only where authored.**

| Dimension | Why it is historically fair game |
|---|---|
| `nation_relations`, per pair, ±band | **Prussia's disposition is the definitional contingency of the period** — Haugwitz was sent to Vienna with something close to an ultimatum and arrived to congratulate Napoleon after Austerlitz. A 1805 in which Berlin is a little warmer or a little colder is 1805. |
| **Deck *order*** among equally-live designs | Which of a court's authored designs is live *first*. Never which designs it holds. |
| **Initial ladder readiness** (`weight`, starting rung) | How close a court begins to acting on a design it demonstrably held. This is §3.8's jitter applied at turn 0. |
| **Starting grudges**, small and drawn from real ones | Austria–Prussia over Germany, Russia–Ottoman over the straits, Prussia–Hanover. Never invented ones. |
| **The minors' lean** — bandwagon readiness | Bavaria, Baden and Württemberg genuinely were up for grabs, and §3.4 says a minor's aliveness *is* its timing. This is the band that matters most. |
| **Britain's first subsidy client** | Pitt was shopping. |
| `threat_level` (85), narrow band | Blessed balance number and the campaign's central pressure (D3) — a small band only; **widening it escalates**. |

**Tier 3 — derived.** Everything downstream follows and is never separately seeded: intent, coalition
posture, advisories, the §3.5 mirror.

**The historian test — the pin that makes this falsifiable.** Across the N-seed sweep, *every* seed
must satisfy: the Third Coalition exists and France is at war with Austria, Britain and Russia ·
**France is at peace with Prussia** (Prussia's entry is a thing that *happens*, never a boot state) ·
every nation's turn-0 active design is drawn from its own authored deck · no nation boots eliminated,
or holding a province it did not hold in 1805 · no minor boots at war. A seed that fails any of these
is a build failure, not a colourful opening.

**The `historical` seed — the migration contract, and why this costs no test churn.** `SOVEREIGN_SEED`
joins the documented boot-precedence chain in `main.py` alongside `SOVEREIGN_SCENARIO` /
`SOVEREIGN_MAP`. **Unset, or `SOVEREIGN_SEED=historical`, reproduces today's boot byte-for-byte** —
every band collapses to its authored centre. `conftest` pins it suite-wide exactly as it already pins
`SOVEREIGN_SCENARIO=none`, so all 14,409 existing tests, the E1 economic band, M1–M7 and the §4.4a
threat series keep their exact numbers with no edit. §5 pin 1 is **narrowed** to "the historical seed
is byte-identical," which is the same additive pattern §4.4a uses and which this project has already
run successfully once.

**The seed is shown and shareable** — rendered in the ledger and written into the save, so a good
opening can be replayed or reported against. One string, real value.

*Reconciliation with §3.8's "weighted late":* that guidance stands with a nuance D7 forces. Turn 1
still *looks* like 1805 on every seed — Tier 1 guarantees the tableau — and what varies at boot is
**dispositions, not the map**. The two levers are complementary: Tier 2 supplies the spread in initial
conditions, the §3.8 jitter supplies the compounding that turns it into a different mid-game.

---

## 4. Slices

Ordered so each lands standing on the previous one, and so the first two are playable and
falsifiable before anything can declare a war.

### AI-1 — The Intent Layer (read-only)

**Prerequisite (§0.1 Correction D):** fix `_agenda_cache` invalidation first — wire it into
`invalidate_active_nations_cache` as its docstring already claims, with a pin that a mid-turn
region-control change refreshes the active agenda. Land and pin this *before* intent caches anything.

Build `backend/game_logic/intent.py`: one derivation chokepoint, `get_nation_intent(nation, world)`,
per-turn cached on the `get_active_agenda` pattern (`agendas.py:294-299` — per-nation dict under a
turn key), invalidated through the now-correct chokepoint. It reads the existing agenda view, region
control, relations, relative force, war state and grudges — and writes nothing.

Deliverable is a **pure reading of the world plus its legibility surfaces**: `build_intent_payload`
mirroring `agendas.build_agenda_payload:1214`, hung on the Diplomatic Ledger's nations-tab row as an
`"intent"` sibling to the existing `"agenda"` key (`diplomatic_ledger.py:415`) — un-fogged by the same
DPF-1 precedent — and read by Talleyrand at the two sites that already consume the agenda payload
(`diplomatic_advisory.py:216,366`). Zero behaviour change; the player can now see what every nation
wants and what it is currently prepared to pay.

*Why first:* it is falsifiable on its own (boot intents are pinnable against the authored 1805
opening), and it makes every later slice debuggable.

### AI-2 — Peacetime pursuit (the cheap rungs)

Wire `ask` / `buy` / `align` / `bandwagon` into `ai_diplomacy.process_diplomatic_phase:898` as
intent-driven proposal selection. Today rungs P3/P4/P7 fire on relation and threat scalars; they
should fire on *what the nation is trying to achieve*. Prussia wanting Hanover should be courting
Hanover, subsidising a claim, or seeking a guarantee against Austria — visibly, every turn, in the
mailbox.

This alone converts five idle courts into active ones without a single new war, and gives the player
a peacetime diplomatic game to play.

*Includes:* **the third-party generalisation, which is the slice's real bulk.**
`process_diplomatic_phase` returns `None` when `nation == player` and reads every state, relation and
war score against `player` (`:934-941`) — it is structurally a France-facing function. The AI-vs-AI
path is a *separate*, much narrower function (`process_ai_ai_diplomatic_phase:1954`) whose ladder
cannot express a demand, let alone a war, and which per §0.1 Correction C had never successfully
ratified a treaty until a July 2026 fix. Converging these two paths so an intent-driven proposal
resolves the same way regardless of who is on each end is the prerequisite for AI-3 and AI-4, and it
should be scoped as such rather than as a parameter change.

**Ships with the D5 counter-instruments** (§6 D5) — per principle 7, the player must be able to
answer AI-2 in AI-2.

#### 4.2b — The participation surface (pin 3, made a mechanic)

§5 pin 3 says "the player is never a spectator" and then guards it with the D1 cap, the D2
elimination floor and the fore-warning surface. Those are **limits** — they bound how much of the
campaign happens without France. None of them is *participation*. If AI-3 ships with only those
guards, the honest description of the feature is "sometimes a war you are not in appears in your
ledger," and the player's verb for it is *reading*.

The gap closes cheaply, because a war between two other powers is the richest decision the game can
hand a player who is not in it. **When an AI-vs-AI war brews or begins, both sides court France**,
and the player chooses among five answers — every one of which routes through a seam that already
exists:

| Answer | Seam it uses | What it feels like |
|---|---|---|
| **Join A / join B** | the existing call-to-arms and negotiated-entry paths | picking a winner, and being owed for it |
| **Sell neutrality** | D5 compensation, in reverse — the AI pays *you* to stay out | Prussia's entire 1795–1806, played from the other side |
| **Sponsor without joining** | the `sponsor` branch through `get_paymaster_nation` | being Britain for once |
| **Broker** | the existing settlement package, third-party-capable per AI-4 | ending someone else's war on your terms, for a price |
| **Refuse everyone** | — | and watch, having been *asked*, which is the whole difference |

The last row is the point. A war the player was courted about and declined to touch is a decision;
the identical war with no courting is scenery. This is the single highest fun-per-line item in the
phase.

**One legibility dependency:** the ledger must show third-party **war exhaustion** — `world.
war_exhaustion` is already a per-nation dict (`coalition.py:1248, 1265`) and is already accrued from
battles, so this is a display wire, not a system. Without it, "let them bleed each other while France
rearms" — stated as a core fantasy in §1 — is a guess. With it, it is a strategy the player can time.

*Landing split:* the **sell-neutrality** and **sponsor** arms ship with AI-2 (they need only the
diplomacy path). **Join**, **broker** and the exhaustion display ship with AI-3/AI-4, because they
need a third-party war to exist and to be endable. The row is tracked as one item so neither half is
orphaned.

### AI-3 — The Decision for War (the missing first link)

The heart of the phase. A new rung — sited with the NA-5 ultimatum rung, which already computes most
of the preconditions and whose comment names this absence — that lets a nation with sufficient
`weight`, an exhausted ladder, favourable force, and a justification **enter a war for itself**.

**Mechanism (per §0.1 Correction A):** intent sets a war-intent marker; the AI's existing targeting
gates widen to admit the intended target; the attack flows through
`combat_executor.py:3482`, which already declares the war and already assigns
`war_objective = "conquest"` for AI-vs-AI. **No new PEACE→WAR edge is created.** The declaration is
announced (§4.6) before the army moves, so the seam's implicit "war begins when steel meets steel"
never surprises the player.

Requirements that make it feel like history rather than chaos:
- **A stated reason.** The war carries its design as `war_objective` — the pre-provisioned
  `"conquest"` default at `diplomacy.py:7577` is replaced by the actual design where one exists, and
  the reason is what the player reads and what the settlement layer scores. A war nobody can explain
  is a bug.
- **The ladder must have been climbed.** Declaration requires prior refused asks/coercion **on the
  serialized record** (§5.8); no cold-open wars. The single exception is §3.3 reneged compensation,
  which is itself a record of a prior bargain.
- **Restraint gates:** force ratio, treasury, existing war load, alliance webs, armistice cooldowns,
  and the D1 world-wide cap on simultaneous AI-initiated wars.
- **Opportunism** (§3.2) as the timing term.
- **Fore-warning.** The player learns a war is brewing before it lands (§4.6) — this is the
  difference between drama and a surprise diff. It surfaces as **The Brewing Crisis** beat (§4.6a),
  with the instruments that would defuse it listed and honestly gated, and it is subject to the tempo
  rule: one foregrounded crisis world-wide.
- **The player is courted, not merely warned** (§4.2b). Both sides seek France's alignment, purchase
  her neutrality, or ask her to broker. A war France was never approached about fails AI-V.

A note on §3.6: the sealed article hides *how a war was arranged*, never *that it was declared* or
*what for*. A war's reason is always rendered (§5 pin 4); what may have been sealed is the bargain
between two other courts that produced it — which is exactly the shape of a historical surprise and
not a suspension of the fore-warning contract.

### AI-4 — A continent, not a hub (de-France-centering)

Make the consequences of AI-vs-AI war real, by generalising three France-literal systems:

- **Threat** — per §4.4a below. This is the slice's bulk.
- **Coalitions** — `form_coalition` takes a target instead of binding `world.player_nation`
  (`coalition.py:1323`). Subject to D3: a coalition forms against a non-player hegemon **only when
  that power's hegemony share exceeds France's**, so the anti-France coalition cannot be diluted by
  the generalisation.
- **Settlements** — third-party wars must be able to end without the player, through the existing
  settlement package, and appear in the ledger as news. **Without this AI-3 is a one-way ratchet**:
  wars that start and never end. This is a hard dependency of AI-3, not a nice-to-have, and if AI-4
  slips then AI-3 ships with a blunt AI-vs-AI armistice as a stopgap.

#### 4.4a — Threat migration contract (the phase's highest-risk item)

`world.threat_level: int` and `world.threat_sources_this_turn: list` are serialized and read across
16 backend modules (73 refs) and 10 `.gd` refs (§0.1 Correction B). The migration is **additive, not
a rewrite**:

1. Introduce `world.threat_by_target: dict[str, int]` and give `add_threat` / `reduce_threat` an
   **optional** `target` parameter defaulting to `world.player_nation`. Every existing call site keeps
   its exact behaviour, unchanged, untouched.
2. Make `threat_level` a **property** returning `threat_by_target.get(player_nation, 0)`, with a
   setter writing the same slot. All 73 backend reads and all 10 `.gd` reads keep working byte-for-byte.
3. `threat_sources_this_turn` entries gain a `target` key, defaulted to the player on read of a legacy
   save. `from_dict` seeds `threat_by_target` from a legacy scalar; `to_dict` writes both for one
   release.
4. **Pin:** a boot world and a 40-turn run produce a byte-identical `threat_level` series before and
   after the migration. This pin is written and green *before* any non-player target is ever passed.

Only once that is green does any producer start passing a real target.

### AI-5 — Intent into the existing systems

Intent is only worth building if it feeds what is already there. Each of these is a small wire, not
a new system:

| System | What intent unlocks |
|---|---|
| **NA formations** | A nation that *pursues* an acquisitive design can finish one. Poland, Italy and the Roman Republic become reachable without the player brokering them. |
| **Vassals** | Intent explains courting and defection pressure — a lord with a strong design is a lord worth following or worth leaving. `bandwagon` is the vassalage on-ramp. |
| **Economy** | War Effort and subsidy flow with intent; the paymaster already generalises (`get_paymaster_nation`) and can now pay someone else's war — this is the `sponsor` branch's executor. |
| **Jealousy (enemy proxy)** | The EC-M faction proxy gets a real faction to be proxy *for*. |
| **Ultimatums (NA-5)** | Becomes the `coerce` rung of the ladder rather than a terminal gesture. |
| **Marshal recruitment** | A nation preparing a design should be commissioning marshals — the P1.75 rung already exists and would gain a reason. |

### AI-6 — Legibility (why any of this is fun)

Intent that the player cannot read is noise. This slice is not polish; it is the deliverable.

- **The ledger** shows each court's want, its target, and where it sits on the price ladder.
- **The dispatch** reports movement on the ladder as news — a court hardening, an ask refused, a
  guarantee sought. This is the raw material of a diplomatic game.
- **Talleyrand** reads intent aloud and advises against it: who to buy off, who to arm, who is about
  to move.
- **Fore-warning before war**, always. The player should be able to say afterwards *"I saw that
  coming and chose not to stop it."*
- **A war's reason is carried and shown** wherever the war appears — panel, ledger, settlement.

*Narration budget, as a number:* the audit found jealousy alone emitting 6–9 near-duplicate lines a
turn. Intent touches every nation, so the cap ships from day one: **at most 2 intent lines per
dispatch**, chosen by `weight`, with the rest collapsed into a single "and three other courts stir"
tail. **Fore-warnings and declarations are exempt** — those are never suppressed. A pin asserts the
cap; a second pin asserts the exemption.

**v1.2 amendment — the cap governs *routine ladder movement only*.** As written above the cap is a
line budget over everything intent emits, which would let it suppress the phase's best content: the
cap is measured in *lines*, and the §4.6a beats are **events**, not lines. Stated precisely: routine
movement on the ladder (a court hardening, an ask refused, a guarantee sought) is capped at 2 per
dispatch and collapses into the tail; the six named beats are exempt in the same way fore-warnings
and declarations already are. A third pin asserts a beat is never collapsed into the tail. Getting
this wrong is not hypothetical — it is precisely how the jealousy system buried its own best moment
(the audit's own words: *"the system is working beautifully underneath… but the volume buries it"*).

*Relevance, not just weight:* the 2 chosen lines are picked by `weight` **× proximity to French
interest**. A Russo-Ottoman quarrel at the Danube and a Prussian design on Hanover are not equally
worth the player's two lines, and `weight` alone cannot tell them apart. The far war still happens
and still appears in the ledger; it just does not spend the dispatch budget.

#### 4.6a — The beats

Every system in this project that landed well named its **moment**: Wave 6's battle names, NA-6b's
Proclamation, the Jealousy petition channel, the muster preview the July-19 audit called the best
surface in the game. Every system that landed flat emitted lines. Intent is the largest system the
game has added since diplomacy and it currently specifies *reporting* (§4.6) without specifying a
single moment. These are its moments, each one an existing transport:

1. **The Courier.** An ask, an offer or a sale of neutrality arrives as a **named envoy in the Voice
   Bible register**, through the existing `incoming_proposal` dtype and popup idiom
   (`ai_diplomacy.py:1300, 1403`). Not a dispatch line. The whole point of AI-2 is that Europe starts
   talking to France; it should arrive as somebody talking.
2. **The Brewing Crisis.** The fore-warning of §4.3, as a *named* crisis with the instruments that
   would defuse it listed and **honestly gated** — the `/formables` honest-availability contract
   (which the audit singled out as "a model for how gated content should be surfaced") applied to
   diplomacy. "Prussia will move on Hanover. You may compensate, guarantee, or aim her elsewhere —
   two of those three you can afford."
3. **The Ultimatum.** Already built (NA-5), now re-homed as the `coerce` rung rather than a terminal
   gesture. No new surface; a new position in a ladder.
4. **The Broken Bargain (§3.3).** The compensation the player took and did not honour, arriving as a
   cold envoy and the strongest casus belli in the game. This beat must land harder than any other
   because it is the only one that is entirely the player's own doing — Schönbrunn to Jena, played.
5. **The Volte-Face (§3.6).** A beaten great power, courted rather than humiliated, reversing into a
   partner in one settlement. The reward for generosity, and a genuine astonishment.
6. **The Congress.** A third-party war ending without France, reported as news **with the
   consequences named** — who gained, who now borders France, who is now free to look elsewhere. A
   settlement the player reads as a diff is a patch note; one that names what it means for France is
   a plot development.

**Tempo — one foregrounded crisis at a time, world-wide.** Other intents continue to climb silently
and surface when the foreground clears. The phase's failure mode is not too few wars — D1 already
bounds that — it is **four simultaneous crises reading as noise**, which is exactly how jealousy
failed in both the July-10 and July-19 audits. The lesson is available in advance this time; the rule
is the standing brewing-crisis limit, and it is a blessed number tunable in-band.

### AI-V — Assurance and evaluation

- A both-sides pin set (the MC-V pattern): every intent kit exercised for an AI nation *and*
  reachable by the player's own systems.
- **The falsifying run:** the 40-turn AI-only simulation that produced `formations: NONE` and no
  agenda shift is the phase's acceptance test. Acceptance numbers in §7.
- **v1.2 amendment — the acceptance run is N runs, not one.** As written, every acceptance number in
  §7 is measured on a single 40-turn trace. Against a fully deterministic AI layer (§3.8) that trace
  is not a *sample* of the system's behaviour, it **is** the system's behaviour for exactly one
  opening — so "≥1 and ≤4 AI-initiated wars" would be a claim about one point of a function nobody
  had sampled, and tuning D1's cap against it would be tuning against an anecdote. Once the campaign
  seed exists the fix is nearly free: **run the acceptance sweep over N seeds (start at 10) and
  report the distribution.** The band becomes a claim about that distribution — *no run exceeds the
  ceiling, the median sits in band, and no seed produces zero* — which is both a stronger guarantee
  and the only honest way to state one. The same sweep is what proves §3.8 works at all: **if every
  seed produces the same war count on the same turns, the variance slice failed**, and that is a
  cheap, falsifiable pin rather than a matter of opinion.
- **The §3.4 aliveness assertions**, run against that same simulation:
  - **In-character, once each.** Over the run, each major exhibits its signature move at least once —
    Austria builds or joins a bloc rather than fighting alone; Prussia bandwagons *and* later reneges
    or defects; Russia intervenes in a war not on its own border; Britain funds a war it never joins.
  - **The homogeneity guard.** No two majors reduce to the same instrument distribution. Concretely:
    the per-power histogram of first-instrument choices (`ask`/`buy`/`align`/`bandwagon`/`sponsor`/
    `coerce`/`fight`) must differ between every pair of majors by a fixed floor. Identical AIs fail.
  - **Legible from the ledger.** For each major, the Intent row + Talleyrand read together name its
    *style*, not only its target — a scripted assertion, not a vibe.
- **The v1.2 gameflow assertions**, run against the same simulation:
  - **The player was asked.** Every AI-initiated war produced at least one courting offer to France
    before or during it (§4.2b). A war France was never approached about fails.
  - **The seven scenes** (§7a): at least 5 of 7 demonstrably reachable, each unreachable one carrying
    a written blocking predicate — the same honest-absence discipline the DoD already applies to
    formations.
  - **The beats fired and were not collapsed** (§4.6a): each of the six beats reachable, and a pin
    that a beat is never swallowed by the §4.6 line cap.
  - **The soap-opera measurement** (§5 pin 13): the share of dispatch column-inches spent on events
    France was not party to, reported as a number rather than asserted as a feel.
- A live scored creative pass in the `docs/audits/` idiom, which must speak to whether the majors felt
  like distinct statesmen — the pillar this contract exists to raise — **and to whether the player had
  something to do about them**, which is the pillar §4.2b exists to raise.

---

## 5. What must not break

Pins to write before the first behaviour change:

1. **The 1805 opening is byte-identical at boot** on the `historical` seed. No nation acquires an
   appetite on turn 0. *(Narrowed by D7, not weakened: `SOVEREIGN_SEED` unset or `=historical`
   reproduces today's boot byte-for-byte and is pinned suite-wide in `conftest`, so this pin and every
   number resting on it — the E1 band, M1–M7, §4.4a's threat series — hold unedited. On any other seed
   the guarantee is the §3.8.1 **historian test**: Tier-1 values identical, Tier-2 values inside their
   authored bands, and the five hard conditions true on every seed. The original intent of this pin —
   "the engine must not grow an appetite the scenario did not author" — is strengthened by D7, because
   the appetite now has to be written down in the scenario file to exist at all.)*
2. **M1–M7 byte-identical** (`tests/test_combat_sweep_metrics.py`).
3. **The player is never a spectator.** AI-vs-AI war must not resolve the campaign around France; the
   D1 cap, the D2 elimination floor and the fore-warning surface are the guards.
4. **No unexplained war.** A declaration without a reason the player can read is a failing test, not
   a rough edge.
5. **The coalition remains a real threat.** Generalising threat must not defang the anti-France
   coalition, which is the campaign's central pressure. Guarded structurally by the §4.4a migration
   contract and by D3's hegemony-share condition, and measured before/after.
6. **GR8** — intent is per-turn cached; no per-region scans in a hot path.
7. **Serialization discipline** — every new persisted field through `to_dict`/`from_dict` +
   `SAVE_FORMAT_REFERENCE.md`.
8. **Derived intent survives a save/load round-trip identically** — and *because* it is derived, the
   ladder's history must **not** be. Refused asks, coercion on record, compensation bargains and
   their expectations are **serialized**; if they are re-derived, "no cold-open wars" becomes a lie
   the moment a player loads a save. Pin: save mid-ladder, load, assert the same rung and the same
   war eligibility.
9. **The AI must not solve the player's problems.** A third party taking a province France covets, or
   destroying an enemy France was about to beat, is a feel-bad even when it is "alive". The
   opportunism term (§3.2) must not aim AI wars at the player's own active war targets without the
   player having a say — the `sponsor` branch is how that is *supposed* to happen, with France paying
   for it.
10. **The majors stay in character under stress** (§3.4). The `statecraft` profile must not collapse
    to a uniform "defend the capital" the moment a power is threatened — a Prussia that bandwagons in
    peace but plays identically to Austria in a crisis is not alive, it is a facade. Pin: a major's
    behaviour under threat still reflects its profile (Britain still reaches for gold not a levy;
    Austria still seeks a partner before fighting alone), and the homogeneity guard (§4.7) holds in
    wartime, not only at peace.
11. **Surprise is never a lie** (§3.6). Nothing hidden may be a *disposition*. A court's want, its
    target, its rung, its stated war reason and the fact that a war is coming are always readable.
    Only **agreements** (the sealed article) and **timing** are uncertain. Pin: an assertion that no
    intent field consumed by the ledger is ever suppressed or falsified for any nation.
12. **Every sealed article is discoverable before it bites** (§3.6). A bargain the player had no
    possible route to learning is a cheat, not a surprise. Each sealed article carries at least one
    discovery route — rumour, a diplomat's read, a defection, or the money appearing in a ledger —
    and the D5 counter-instruments must remain usable once it *is* discovered. Pin: a sealed article
    with zero discovery routes fails the test, and a discovered one still has an answer.
13. **A living Europe must not become a soap opera.** The inverse of the diorama is a campaign where
    so much happens elsewhere that France's own war reads as incidental. Guarded by D1's cap, D3's
    gravity condition, the §4.6a tempo rule and the §4.6 relevance weighting — and measured, not
    assumed: the acceptance run reports what share of dispatch column-inches were spent on events
    France was not party to.
14. **The seed varies dispositions, never the map, the roster, or the save** (§3.8, D7). *(Amended by
    D7 — the first draft of this pin asserted turn-0 intent byte-identical across every seed, which
    D7 overturns.)* Pin, in three parts: **(a)** the `historical` seed reproduces today's boot
    byte-for-byte and every existing byte-identical pin is green with it fixed; **(b)** the §3.8.1
    **historian test** passes on every seed of the N-seed sweep — Tier-1 values identical, Tier-2
    inside their authored bands, and a value with no authored band never varies; **(c)** a
    mid-campaign save/load round-trip reproduces the same subsequent 5 turns, because the seed is
    serialized rather than re-rolled.

---

## 6. Gate record — decisions (authoritative)

Held July 20, 2026. The six questions of v0.1 §6 are answered in **D1–D6**; **D7** was raised by the
v1.2 gameflow pass (§3.8) and decided the same day. Where a decision names a re-check, that re-check
is the only remaining gate in the phase.

### D1 — World motion: **calibrated, not maximal.**

**Cap: 2 simultaneous AI-initiated wars world-wide**, plus a per-nation cooldown after any war it
started. Rationale: 1805–15 opened roughly one new non-French war every 18–24 months (Russo-Turkish
1806, Anglo-Russian 1807, the Gunboat War 1807, the Finnish War 1808, Dano-Swedish 1808) against a
continuous French war. Three parallel AI wars is not a livelier version of that decade; it is a
different century. **Acceptance target: the 40-turn AI-only run produces ≥1 and ≤4 AI-initiated
wars.** Below 1 the phase failed; above 4 the map is dissolving. The cap is a blessed number, tunable
in-band; changing its *shape* escalates.

### D2 — Elimination without France: **minors yes, great powers no.**

An AI-initiated war may take provinces, impose vassalage, extract indemnities, and **eliminate a
minor** (no authored deck, not a great power). A **great power's last capital cannot fall to an
AI-initiated war** — that war routes to a forced settlement instead. This is the historically true
answer, not merely the playable one: Venice, Genoa and the HRE were extinguished in this period,
while Prussia and Austria survived catastrophic defeat *because the hegemon chose to keep them*.
Annihilating a great power is a hegemon's prerogative, and in this game the hegemon is the player.

### D3 — France stays the gravitational centre — **and that is a design choice, not an omission.**

Generalise the *machinery* (threat is per-target, coalitions take a target, settlements are
third-party-capable). Keep the *gravity*: a coalition forms against a non-player hegemon **only when
that power's hegemony share exceeds France's own**. Below that line, the anti-France coalition is the
only coalition, exactly as today.

This means the player can genuinely be eclipsed — lose enough and Europe turns on Austria instead,
which is a real and earned game state — but the campaign's central pressure cannot be diluted by
ambient AI-vs-AI noise. A Napoleonic game in which Europe stops caring about France has lost its
subject. §5.5's before/after measurement is the guard.

### D4 — Ladder visibility: **fully open, with uncertain timing.**

Want, target and current rung are **all shown** in the ledger. Rationale: this project has a standing
rule that **diplomacy has no fog of war**, and v0.1's own recommendation (soften the rung by
relations) would have introduced exactly that, in the one layer that has deliberately never had it.

What is *not* shown is **when**. Imminence is conveyed by Talleyrand's voice and by the fore-warning
events, never by a hidden number the player could have read. So the player always knows Prussia wants
Hanover and is prepared to coerce for it; they never know that this is the turn. That is the honest
place to put uncertainty, and it keeps intelligence valuable without making the ledger lie.

> **v1.2 note — §3.6 does not amend this decision, it draws its boundary.** The sealed article hides
> an **agreement between two other courts**, never a **disposition**: want, target, rung and stated
> war reason stay open exactly as D4 requires, and §5 pin 11 makes that a test. D4's "uncertain
> timing" and §3.6's "uncertain agreements" are the same principle applied twice — uncertainty lives
> outside the ledger's claims, never inside them.

### D5 — The player gets counter-instruments. **Three, and they ship with AI-2, not after it.**

Per principle 7, an intent mechanic and its answer land together.

1. **Compensation — buy off a design.** Cede the coveted province, grant an equivalent elsewhere, or
   pay an indemnity, to satisfy or suspend a design. *Schönbrunn, December 1805.* Creates a standing
   expectation per §3.3.
2. **Sponsorship — aim a power at a target.** Subsidise or licence another nation's design against a
   third party, through the existing paymaster seam. *Tilsit, 1807; Britain's entire foreign policy.*
3. **Guarantee — protect a border.** Pledge to defend a province, raising the coveter's `weight` bar
   for war and putting France's credibility at stake if it is tested.

All three route through the existing wizard/settlement seams and work in **both directions** — the AI
can offer them to the player and to each other. Together with §3.3 they turn AI-3 from something done
*to* the player into something played *against*: every war the AI starts is one the player could have
bought, aimed elsewhere, or deterred — and chose not to.

### D6 — Sequencing: **BD → AI-0/0b/0c → AI-1 → AI-2 → re-check → AI-3 → AI-4 → AI-5/6 → AI-V.**

*(Header updated by D7. The three AI-0 rows are the front block: **AI-0** the agenda-cache
invalidation fix (§0.1 Correction D), **AI-0b** the campaign seed and **AI-0c** the historical bands
(§3.8, D7). All three are prerequisites rather than features — each one, landed late, invalidates
pins written before it.)*

Battle Diorama (ROADMAP row BD) keeps its place first: it is contained, visual, already scoped, and
a deliberate palate cleanser between two large systems arcs.

Then **AI-1 + AI-2 + D5 ship as one playable increment** — a Europe that visibly wants things and can
be bargained with, with zero new wars. **Then a short re-check with the user before AI-3**, because
AI-3 is the only slice that can change the shape of the campaign, and because AI-1/AI-2 will have
produced the first real evidence about how much motion the world actually wants (D1's cap is the
thing most likely to need adjusting, and it will be adjustable from data instead of from argument).

AI-4's §4.4a migration may begin in parallel with AI-2 — it is a no-behaviour-change refactor with
its own byte-identical pin, and it is the phase's long pole.

### D7 — Variance: **seeded, and the opening is seeded too — within authored historical bounds.**

Decided July 20, 2026, on the question §3.8 raised and declined to answer itself (user: *"yes this
should be seeded but within bounds of history"*).

The phase ships a **serialized campaign seed** (§3.8), and its reach extends to the **1805 opening**,
not merely to in-campaign thresholds. Without this the phase would have shipped a very good script:
the AI layer contains no randomness at all — `agendas.py`, `ai_diplomacy.py` and `coalition.py` have
zero `random` calls between them — so every campaign would have opened identically and diverged only
as the player forked it.

**The bound is authored, not computed** (§3.8.1). Every varying value carries an authored range in
`europe_1805.json`; no band means no variance. Province ownership, the roster, `starting_wars`, deck
*content*, the marshals and the §3.4 statecraft profiles are **fixed on every seed** — what varies is
**dispositions**: relations within a per-pair band, deck *order* among equally-live designs, initial
ladder readiness, small grudges drawn from real ones, the minors' lean, Britain's first client. The
historian test in §3.8.1 is a hard pin: on every seed the Third Coalition exists, France is at war
with Austria/Britain/Russia and **at peace with Prussia**, and no nation holds a province it did not
hold in 1805.

**`SOVEREIGN_SEED` unset or `=historical` reproduces today's boot byte-for-byte**, pinned suite-wide
in `conftest` like `SOVEREIGN_SCENARIO=none`. So §5 pin 1 is **narrowed rather than deleted**, and the
existing suite, the E1 economic band, M1–M7 and the §4.4a threat series keep their numbers unedited.

*Consequence for the build:* **AI-0b (seed) and AI-0c (historical bands) land at the front**, with
AI-0/AI-1. A seed retrofitted after the pins are written is paid for twice. `threat_level`'s band is a
blessed number tunable in-band; **widening the envelope — adding a new Tier-2 dimension — escalates.**

---

## 7. Definition of done

- Every nation has a readable intent; the player can name what any court wants and what it will pay.
- Idle courts are visibly active in peacetime through existing diplomatic verbs.
- A nation can go to war for a stated reason, having first tried cheaper instruments, with the player
  fore-warned — through the existing `combat_executor.py:3482` declaration seam, with **no new
  PEACE→WAR edge in the codebase**.
- The player can buy off, aim, or deter a design (D5), and can be offered the same.
- Wars can happen, **and end**, between powers that are not France.
- **The majors feel like distinct statesmen (§3.4).** The player can name each major power's *style*
  from the ledger and Talleyrand — not just its target — and over a run each behaves in character:
  Austria the patient coalition-builder, Prussia the bandwagoner who reneges, Russia the distant
  arbiter, Britain the paymaster who never marches. The §4.7 homogeneity guard and in-character
  assertions are green.
- **The great powers conduct politics with each other, witnessed.** At least one bloc formed, one
  betrayal or defection, and one third-party war fought and settled among non-France powers appear in
  the campaign log across the run — the player sees a living balance of power, not a hub.
- **The 40-turn AI-only acceptance run** produces: ≥1 and ≤4 AI-initiated wars (D1), every one of
  them carrying a reason the ledger renders; ≥1 third-party settlement; ≥1 agenda shift; and **≥1
  formation, or a written explanation of the specific predicate that blocked it** (formation is the
  longest chain in the game and 40 turns may honestly be too short — an unexplained absence fails,
  an explained one does not).
- **The player was courted, not merely warned** (§4.2b). Every AI-initiated war produced at least one
  offer to France — join, sell neutrality, sponsor, or broker — so that standing aside was a choice
  the player made rather than a thing that happened around them.
- **France can read itself** (§3.5). The player's own ledger row shows Europe's reading of France, and
  a player who does nothing drifts down the perceived ladder.
- **At least one genuine surprise is structurally possible and none of them is a lie** (§3.6, §5 pins
  11–12): a sealed article that was discoverable, an emergent design, or a volte-face.
- **Two campaigns are not the same campaign** (§3.8, D7). Across the N-seed acceptance sweep, the
  opening dispositions, war counts, the turns wars begin and which courts reach `fight` all vary —
  while the **§3.8.1 historian test passes on every seed**, the `historical` seed reproduces today's
  boot byte-for-byte, and a save/load reproduces its own campaign exactly.
- **Every seed is a 1805 a historian would recognise** (§3.8.1). Tier-1 fixed on all seeds, Tier-2
  inside authored bands, and no dimension varies that a designer did not write a band for.
- The 1805 opening is byte-identical, M1–M7 unmoved, and the pre/post anti-France threat series
  measured and reported (§5.5).
- Scored creative pass recorded in `docs/audits/`.

### 7a — The seven scenes (historical acceptance)

The DoD above is measured in counts. This is measured in *recognition*: can the engine **produce**
the decade's characteristic political events — not script them, not fake them, but reach them from
authored 1805 by the machinery in §3? A phase that hits every number and cannot produce any of these
has built a simulation of statecraft without its texture.

| # | Scene | The mechanic that reaches it |
|---|---|---|
| 1 | **The Confederation of the Rhine** — a cluster of minors bandwagons to the hegemon | `bandwagon` (§3.1) + the vassalage on-ramp (§4.5), timing per §3.4's minors paragraph |
| 2 | **Schönbrunn** — a design bought off with compensation elsewhere | D5 instrument 1, creating a standing expectation (§3.3) |
| 3 | **Jena** — that bargain broken, and the war that follows says so | §3.3 reneged compensation as the highest-weight casus belli, carried as the war's stated reason |
| 4 | **Tilsit** — a beaten enemy reverses and is aimed at a third party | the volte-face (§3.6) + the `sponsor` branch |
| 5 | **Pitt's subsidy** — a war funded by a power that never marches, and France bidding for the recipient | `get_paymaster_nation` + the subsidy contest (§3.7) |
| 6 | **The Continental System bites** — the gold stops because the trade was cut | the existing Continental System reaching Britain's core (§3.4) |
| 7 | **A partition** — two powers agree to carve a third, possibly in a sealed article, and it lands as a fait accompli | the sealed article (§3.6) + third-party settlement (§4.4) |

**Acceptance:** ≥5 of 7 demonstrably reachable in the AI-V run, each miss carrying a written blocking
predicate. Scene 6 may legitimately be blocked on economic scale and scene 7 on the sealed-article
slice slipping — those are explanations; "it didn't come up" is not.

---

## 8. Owner rows (GR9)

| Row | Owner | Landing | Tracking |
|---|---|---|---|
| AI-0 Agenda-cache invalidation fix | §0.1 Correction D, §4.1 prerequisite | `_agenda_cache` wired into `invalidate_active_nations_cache` | `test_ai_intent_layer.py` (mid-turn refresh pin) |
| AI-1 Intent layer | §4.1 | `intent.py` + `build_intent_payload` + ledger row | STATUS + `test_ai_intent_layer.py` |
| AI-2 Peacetime pursuit | §4.2 | `ai_diplomacy` rung rework | `test_ai_intent_peacetime.py` |
| AI-2b Counter-instruments (D5) | §6 D5, §3.3 | compensation / sponsorship / guarantee through the wizard + settlement seams | `test_ai_intent_counterplay.py` |
| AI-2c Great-power statecraft (§3.4) | §3.4 aliveness contract | per-nation `statecraft` weighting over the ladder/instrument choice (generalises `NATION_DESIRE_PROFILES`); authored the majors, light for secondaries | `test_ai_intent_aliveness.py` (in-character + homogeneity guard) |
| AI-3 Decision for war | §4.3 | war-intent marker + widened targeting into the existing declare seam | `test_ai_intent_war_decision.py` |
| AI-4a Threat migration | §4.4a | `threat_by_target` + `threat_level` property, byte-identical | `test_ai_intent_threat_migration.py` |
| AI-4b De-France-centering | §4.4 | targeted coalitions + third-party settlement | `test_ai_intent_third_party.py` |
| AI-5 System wiring | §4.5 | per-system wires (formations, vassals, econ/sponsor, jealousy proxy, NA-5, recruitment) | `test_ai_intent_system_wiring.py` |
| AI-6 Legibility | §4.6 | ledger/dispatch/Talleyrand + the 2-line narration cap | `test_ai_intent_legibility.py` |
| AI-V Assurance | §4.7 | both-sides pins + the 40-turn acceptance run | `test_ai_intent_assurance.py` |
| Economy re-measure | audit §5 | re-measure from an actively-spending run before tuning | carried here so it is not lost |

### v1.2 rows (the gameflow pass)

| Row | Owner | Landing | Tracking |
|---|---|---|---|
| **AI-0b Campaign seed** | §3.8 | serialized world seed + `SOVEREIGN_SEED` on the boot chain + threshold jitter + tie-breaks; **must land with AI-0/AI-1** or every pin written against the deterministic trace is revisited | `test_ai_intent_variance.py` |
| **AI-0c Historical bands (D7)** | §6 D7, §3.8.1 | authored per-dimension ranges in `europe_1805.json` + validator schema + `MODDING_FORMAT.md` row; the `historical` seed collapses every band to its centre; the seed shown in ledger + save | `test_ai_intent_historical_envelope.py` (the historian test) |
| **AI-1b The mirror** | §3.5 | France's own ledger row = Europe's derived reading of France; restraint drifts it down | folded into `test_ai_intent_layer.py` |
| **AI-2d Participation surface** | §4.2b | sell-neutrality + sponsor arms with AI-2; join / broker / third-party war-exhaustion display with AI-3/AI-4 — **one row so neither half orphans** | `test_ai_intent_participation.py` |
| **AI-2e Subsidy contest** | §3.7 | subsidy recipient + amount made visible; France may outbid or remove a client, through `get_paymaster_nation` / `get_british_subsidy_recipient` | folded into `test_ai_intent_counterplay.py` |
| **AI-3b Sealed articles** | §3.6, §5 pin 12 | AI↔AI bargains whose *fact* is public and *article* may be sealed, each with ≥1 discovery route | `test_ai_intent_sealed_articles.py` |
| **AI-5b Emergent designs + volte-face** | §3.6 | grievance→design promotion (max 1/nation, from the serialized record) and the courted-loser reversal through the settlement layer | `test_ai_intent_emergent_designs.py` |
| **AI-6b The beats + tempo** | §4.6a | six named beats on existing transports; one foregrounded crisis world-wide; cap governs routine lines only; relevance-weighted line selection | folded into `test_ai_intent_legibility.py` |

**Scope honesty (GR9).** These six rows are real additions to an already-large phase, and pretending
otherwise would be the failure mode this project has a rule against. Their disposition:

- **Core — must ship with the phase**, because without them AI-3 is something done *to* the player:
  **AI-2d** (participation) and **AI-6b** (beats + tempo). AI-2d is the single item most likely to
  decide whether the phase is fun.
- **Core *and* order-constrained: AI-0b + AI-0c** (§3.8, D7). Small, but they must land at the front.
  A phase whose every campaign opens identically has built a very good script, and retrofitting a seed
  after the pins are written costs more than writing it first. AI-0c is mostly *authoring* — ranges
  beside values in a JSON the scenario system already loads — plus a validator block and the historian
  test.
- **Cheap and high-yield — take them where they sit:** **AI-1b** (one derived row) and **AI-2e**
  (a comparison in an existing function plus a display).
- **May slip past the phase with a named landing, and say so if they do:** **AI-3b** sealed articles
  (a genuinely new mechanic — nothing in `settlement_*.py` or `diplomacy.py` models a hidden clause
  today) and **AI-5b** emergent designs + volte-face. If either slips, it lands in the phase's own
  exit review rather than becoming a vague "later" — and §7a scenes 4 and 7 fail with that as their
  written blocking predicate, which is the honest outcome, not a hidden one.

**Not in this phase, deliberately:** narrative/LLM-voiced diplomacy beyond existing register banks
(GR6); a new war-goal system beyond reusing `war_objective`; any rebalance of the anti-France
coalition beyond keeping it intact (§5.5); naval-dependent designs and the preventive-seizure war
(Copenhagen 1807) — that is a `deny_regions` fast-path that needs the DEF-5 naval layer to mean
anything, and it is homed there, not here.

---

## 9. v1.2 review record — what the gameflow pass changed, and why

The review asked one question of v1.1: **what does the player do, turn to turn, once this ships?**

v1.1 answers it honestly for the peacetime half — AI-2 gives Europe verbs and D5 gives France three
answers — and then thins out precisely where the phase gets loud. Once AI-3 lands, the spec's
player-facing verbs for an AI-vs-AI war are *read the ledger* and *have been warned*. Pin 3 names the
right worry ("the player is never a spectator") and then guards it with three limits, none of which
is participation. That is the gap §4.2b closes, and it is the single change in this revision most
likely to decide whether the phase reads as a living Europe or as weather.

The second finding is quieter and more dangerous. v1.1's commitment to legibility is so thorough —
fully open ladder, fore-warning always, no unexplained war, every reason rendered — that **the phase
had no remaining capacity to surprise anyone.** Four correct wins in a row (NA, the sweeps, the
audits) have trained this project's specs toward legibility as an unalloyed good, and it mostly is;
but a strategy game whose entire diplomatic layer is knowable in advance has traded one failure
(the diorama) for another (the timetable). §3.6 puts surprise back in the three places it can live
without the ledger ever lying — **agreements, timing, and the world writing designs the author did
not** — and §5 pins 11–12 fence it so it can never become the fog D4 correctly refused.

| # | Finding | Disposition |
|---|---|---|
| 1 | Pin 3 is a limit, not a mechanic — the player's verb for an AI war is *reading* | **§4.2b** participation surface; **AI-2d** |
| 2 | Total legibility left no room for surprise; "no fog" was being read as "no uncertainty" | **§3.6** — fog boundary drawn at dispositions-vs-agreements; pins 11–12 |
| 3 | ≥1 agenda shift was a DoD number with no system behind it | **§3.6** emergent designs; **AI-5b** |
| 4 | Intent specified reporting, never a *moment* — the failure pattern of every flat system this project has shipped | **§4.6a** the six beats |
| 5 | The narration cap, as written, could suppress the phase's best content | §4.6 v1.2 amendment: cap governs routine lines; beats are events |
| 6 | `weight` alone can't tell a Danube quarrel from a Prussian design on Hanover | §4.6 relevance weighting |
| 7 | Britain explained is still Britain unplayable for fifty turns | **§3.7** the subsidy contest; **AI-2e** |
| 8 | Intent was entirely outward-facing; France could not read itself | **§3.5** the mirror; **AI-1b** |
| 9 | "Reverses hard" and "minors are texture" were adjectives doing a mechanic's job | §3.6 volte-face; §3.4 minors-are-timing paragraph |
| 10 | The inverse failure of the diorama — a soap opera — was unguarded and unmeasured | §5 pin 13, measured in the acceptance run |
| 11 | Historical fidelity was asserted in prose but never made falsifiable | **§7a** the seven scenes |
| 12 | *(added on review)* Surprise-within-a-playthrough was mistaken for variance-across-playthroughs. The AI layer has **zero** randomness and the project has **no campaign seed** — every campaign opens identically and diverges only as the player forks it | **§3.8** + **AI-0b**, order-constrained to the front; pin 14 |
| 13 | *(added on review)* Every §7 acceptance number was measured on a **single** 40-turn trace — against a deterministic layer that is one point of an unsampled function, and D1's cap would have been tuned against an anecdote | AI-V amendment: N-seed sweep, band stated as a distribution; the same sweep falsifies §3.8 |
| 14 | *(decided by the user, July 20)* §3.8 scoped the seed to in-campaign thresholds and left the **opening** as an open gate question. Left there, the first ~10 turns of every campaign are still a script | **§6 D7** + **§3.8.1** the historical envelope: the opening is seeded too, bounded by **authored** ranges (no band → no variance), with the historian test as the pin and the `historical` seed as the zero-churn migration. Row **AI-0c**; pins 1 and 14 narrowed |

**What the review did *not* touch.** §6 is untouched — every decision D1–D6 survives the read intact,
and the pass produced no argument against any of them. §0.1's four corrections and the §4.4a
migration contract are untouched. §3.4's statecraft table is extended only by the minors paragraph.
The sequencing in D6 stands, with the v1.2 rows slotted into the slices they belong to rather than
appended as a tail — the phase does not grow a new stage, it grows in place.
