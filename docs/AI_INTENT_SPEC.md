# AI Intent — Phase Spec (v1.4 — gate record · phased build plan · the four review passes)

> **Status: DESIGN GATE HELD July 20, 2026 — §6 (D1–D7) is authoritative and has survived every
> subsequent pass untouched. Stages A–D are BUILT** (§14 A+B · §15 C · §17 D, each authoritative);
> the D6 re-check between Stage C and Stage D was **held July 24, 2026 — gate record §16**.
> Remaining: Stage E (consequence & character) → F (the stage) → G (AI-V), per §11.
>
> **How to read this document.**
> - **Building?** Start at **§11 — the phased build plan** (Stages A–G, per-stage scope, entry/exit
>   criteria, the living cut list). §8 is the owner ledger (GR9); §5 the pins; §7 + §7a the
>   acceptance. **§10 is the correction table — read it before trusting any prose claim about the
>   codebase**, including this document's own earlier passes.
> - **Understanding the design?** §0 the finding → §1 thesis → §2 principles → §3 the model (the
>   ladder · §3.1a the descent · §3.4 statecraft · §3.5 the mirror · §3.6 surprises · §3.8 variance ·
>   §3.9 attractors) → §6 the decisions.
> - **Checking provenance?** §9 (v1.2 gameflow record) · §9a (v1.3 verification record) · §10 (the
>   19 corrections) · §12 (v1.4 creative record). Passes append records; they never silently edit
>   the gate.
>
> **Version history** — each pass additive, none reopening §6:
>
> | v | Date | What it did | Record |
> |---|---|---|---|
> | v1.0 | July 20, 2026 | gate held, D1–D6 decided; §0.1 re-verification corrected three v0.1 claims (A–C), each changing the build | §6, §0.1 |
> | v1.1 | July 20, 2026 | §3.4 the great-power aliveness contract — majors as distinct statesmen, with AI-V teeth | §3.4 |
> | v1.2 | July 20, 2026 | the gameflow pass — §3.5 mirror · §3.6 surprises · §3.7 the auction · §4.2b participation · §4.6a beats · §7a scenes · §3.8 variance (its own correction: the AI layer has zero randomness and no campaign seed existed); **D7 decided same day** — the opening is seeded too, within authored bounds (§3.8.1) | §9 |
> | v1.3 | July 21, 2026 | the verification pass — ten ground-truth readers, ten lenses, two refuters per finding; **19 factual corrections** (row AI-0 deleted; the historian test's false clause; third-party war exhaustion *decays*); §3.1a the descent · §3.9 attractors · §2 principle 9; contracts §4.2c / §4.3a / §4.4a steps 5–6 / §4.4b / §4.6b; pins 15–20; AI-V three arms | §9a, §10 |
> | **v1.4** | **July 24, 2026** | **the structure & creative pass — §11 the phased build plan (the builder's front door); §12 six gameplay additions: the deterrence receipt · Russia's second design · the licence · the purchased dispatch + the player's seal · armed mediation · the allegiance auction; pins 21–24; beat 7** | **§11, §12** |
| v1.4.1 | July 24, 2026 | §13 the standing review questions (user-directed): border massing (new row AI-3c, Stage D) · multi-front conduct (AI-V assertions) · recruit/commission budgeting (the §8 economy re-measure) · AI-vs-AI wars (=Stage D) · the non-France hegemon (=D3 + pin 16d). **Same day: Stage A (AI-0b/0c/0d) and Stage B (AI-1/AI-1b/AI-2a) BUILT — landing record §14.** | §13, §14 |
| v1.4.2 | July 24, 2026 | **Stage C BUILT** (landing record §15; evidence pack `docs/audits/STAGE_C_EVIDENCE_2026_07_24.md`) · **⛩ THE RE-CHECK HELD** (gate record §16: D1 cap confirmed 2; AI-3b slipped out of Stage D; AI-5c keeps Stage E; pin 17b re-sited to §17; the §4.4b exclusive ruling) · **Stage D BUILT** — war and peace, indivisible (landing record §17: AI-3 + §4.3a + AI-3c · AI-4a steps 5–6 · §4.4b · AI-4c · AI-4b + broker/join · beats 2/3/6/7; pins 15/16/17/19/21 green) | §15, §16, §17 |
>
> **Motivating evidence:** `docs/audits/CREATIVE_AUDIT_2026_07_19.md` §2.1, §3, §7 + the AI
> decision-architecture map taken at `b4b6326`, re-verified against master at `12636a6` (v1.0) and
> again at `e7f92dd` (v1.3 — §0.1 records the corrections re-verification forced, three standing and
> one withdrawn; §10 records v1.3's nineteen).
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
(Prussia wants Hanover — one province from Berlin's own corps, held by a minor that fields no
marshal; Sardinia wants Savoy restored) that they will hold, unpursued, until the sun burns out.

That is why no formable ever fires. It is also why the world feels like a diorama.

### 0.1 Three corrections from re-verification (v1.0), and one withdrawn (v1.3)

v0.1 made four claims that did not survive a second pass. All are recorded rather than quietly
edited, and **each one changes the build**. *(The heading read "Two corrections" through v1.1 while
listing A–D; corrected to "Four" in v1.2; corrected to "Three" in v1.3 when D was itself refuted —
the correction needed a correction, which is the argument for §10's discipline, not against it.)*

**Correction A — `war_objective = "conquest"` is not a dead branch with no caller.** It is at
`diplomacy.py:7577-7580` as described, and it fires when *neither* party is the player. But there are
two reachable callers: `meta_executor.py:2108` (the `trigger_commitment_paradox` debug cheat, which
asserts `player not in (attacker, defender)` and hits the branch deterministically) and
`combat_executor.py:3482` / `:3532` (the auto-declare-on-attack seam, live for any non-player
attacker). The accurate statement is: **no *production AI* caller exists**, because
`enemy_ai.py`'s targeting is `is_at_war`-gated end to end.

*v1.3 narrows the seam claim.* `:3482` declares unconditionally, but **`:3532` declares only when
`can_enter_territory(...)` is False** — and `OPEN_MOVEMENT_STATES` includes OPEN_BORDERS and
NON_AGGRESSION (`diplomacy.py:61`), treaties `_evaluate_ai_ai_proposal` actually mints
(`ai_diplomacy.py:2012-2064`). Under one of those an AI marches in, captures, and **no war is
declared, no `war_objective` exists, and no reason renders**. Separately, `:3483` / `:3533` *ignore*
a failed declaration for a non-player attacker and fight anyway.

*Why this changes the build:* the shortest correct path to an AI war is **not** a new declare-war
call in `ai_diplomacy.py`. It is to let the intent layer decide, then let the AI attack a nation it
is not yet at war with and have `combat_executor.py:3482` do what it already does. AI-3 should
**reuse that seam** rather than open a second one. GR5 is satisfied for free, the objective is
already pre-provisioned, and there is exactly one PEACE→WAR path to test. AI-3's job shrinks to
*deciding* and *announcing*; **the declaration plumbing exists for a coveter at PEACE or ARMISTICE
with its target, and every other pre-war state needs an explicit step — written as §4.3a.**

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

**Correction D — WITHDRAWN on verification (v1.3). The defect does not exist.** v0.1 claimed
`_agenda_cache` was documented as cleared by `invalidate_active_nations_cache()` and was not, and
made fixing it prerequisite slice **AI-0**. Nine of this review's twenty readers checked it
independently and it is false on every sub-claim. The chain is live and was landed in the NA-0 commit
itself: `invalidate_active_nations_cache` (`world_state.py:1611`) ends at `:1619` by calling
`invalidate_bloc_members_cache`, whose **last statement** (`:1695`) is `self._agenda_cache = None`,
under the comment *"NA-0: agenda activation reads region control, vassalage, AND war/alliance
geometry — this seam is the one all three mutation families reach."* `capture_region` (`:2897`) and
`set_diplomatic_state` (`diplomacy.py:2634`) both reach it. There are **two** direct clears, not one —
`world_state.py:1695` and `formations.py:488`, the latter belt-and-braces for the deck-swap case; do
not "clean it up." Both behaviours are already pinned:
`test_nation_agendas.py::TestCacheAndSerialization::test_cache_invalidation_recomputes_same_turn` and
`::test_production_diplomatic_seam_flushes_cache`.

*Why the withdrawal changes the build:* **row AI-0 is deleted** and D6's front block loses a slice.
More importantly, **following the original instruction would have re-opened the P1 NA-0 closed** —
`set_diplomatic_state` reaches the bloc seam *directly* and never touches
`invalidate_active_nations_cache`, so "move the flush up" breaks same-turn agenda refresh on a war
declaration. The idiom is safe for intent to copy as-is. One real residual survives, and it belongs
*inside* AI-1 rather than in front of it: agenda activation reads only region control, vassalage and
war/alliance geometry — the three families that seam reaches — while **intent additionally reads
relations, relative force and treasury, and none of those has an invalidation seam**
(`WorldState.modify_nation_relation`, `world_state.py:1760-1778`, invalidates nothing; a battle that
changes relative strength invalidates nothing). AI-1 decides explicitly whether to accept turn-key
staleness on those terms — the choice `agendas.py:17-20` already makes for treasury — or to wire
`modify_nation_relation` into the same chokepoint, and pins the decision either way.

*The one true thing in the original claim* is that `agendas.py:288`'s docstring is loose where the
module header at `:17-20` is precise. Tightening that one line is a P3 drive-by, not a slice.

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
   (`agendas.py:294-299`: turn-keyed `_agenda_cache`, cleared through the bloc-cache chokepoint —
   `invalidate_bloc_members_cache`, `world_state.py:1695`, reached both by
   `invalidate_active_nations_cache` and directly by `set_diplomatic_state`).
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
9. **Reactivity — a change in the world must change what somebody wants, what somebody will pay, or
   what somebody can do.** *(v1.3.)* A phase that adds wants without adding reactions builds a set of
   standing intentions, not a living continent. Every intent input needs a seam that notices when it
   moves; where no seam exists this phase either builds one or writes down that the input is
   turn-granular by design. This principle is stated because the v1.3 review kept finding *instances*
   of one class — the world does not notice that X happened — and a principle catches the next one
   before it ships:

   | Something happens | What notices it today | Owner |
   |---|---|---|
   | A **non-player** wins battles / takes a capital | nothing — every threat producer is player-keyed | AI-4a step 5 (§4.4a) |
   | Two third parties **bleed each other** | nothing — war exhaustion never accrues and decays −5/turn | AI-4c (§4.2b, §3.1a) |
   | A power is **humiliated** — partitioned, capital lost, punitively settled | nothing durable — no serialized record survives the grudge window | AI-5b(i) (§3.6) |
   | A hostile army stands on a great power's **home soil** | nothing in `statecraft` — §3.4's Britain row answered with gold regardless | AI-2c (§3.4) |

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
  is the mechanism by which the player can *arm someone else's grievance*.
  **v1.3 correction:** it does **not** route through `get_paymaster_nation` (NA-3 §5.7).
  `get_paymaster_nation` is the **coalition special case** of this branch — one payer, resolved from
  an authored deck entry, inside the single `active_coalition`, and structurally never the hegemon
  (`_paymaster_active`, `agendas.py:198`), so France can be neither payer nor recipient and the
  function cannot express "Napoleon aims Russia at Sweden" at all. The general branch needs a
  **directed** sponsorship — a named payer aiming a named recipient at a named target — carried on an
  existing directed-payment seam and owned by AI-2b (§6 D5-2).

### 3.1a Descent — how a want cools, and how a war ends *(v1.3)*

The ladder above is specified only as **climbed**. That is the largest omission in v1.2 and it is not
a matter of taste: §4.4 already names the risk in its own words — *"without this AI-3 is a one-way
ratchet"* — and then assigns the job to machinery that this review found **dead for exactly the
AI-vs-AI case AI-3 exists to create.** A continent whose courts can only escalate is not a living
Europe; it is a fuse.

State the principle first, because it is cheap: **`price` is a per-turn *reading*, not a latch.** A
design that satisfies, or a `weight` that collapses, lowers the rung for free and no builder should
ever store the marker. But the four descent seams the phase leans on are in very different states,
and the spec must say which owns which.

**(a) The want cools — works today, nothing to build.** An `acquire_regions` entry goes inactive the
instant it satisfies (`agendas._entry_satisfied`), and §3.2's opportunism term decays the moment the
victim's situation improves. Stated here only so that no one latches the war-intent marker.

**(b) The design is bought off — specified, cross-reference only.** D5 instrument 1 plus §3.3's
standing expectation. Note the asymmetry §3.3 already builds in: buying a design off does not delete
it, it converts it into a hostage.

**(c) The nation tires — the machinery exists and silently no-ops.** Three separate live terms read
war exhaustion: `effective_p1_threshold = -40 + peace_threshold_delta + we // 20` and
`effective_stalemate_turns = max(2, 5 + patience - we // 30)` (`ai_diplomacy.py:944, :958`), plus the
settlement-acceptance component `min(20, we // 3)` (`settlement_scoring.py:1459-1486`). NA-3's
`get_agenda_resolve_delta` layers on top (satisfied +10 sues sooner, advancing −8 fights longer).
**This is the seam that is dead:** third-party `we` is permanently 0 *and decaying*, so all three
terms no-op for any war France is not in. Owner row **AI-4c**; the defect is stated in full at §4.2b.

**(d) The war ends — half reusable, half must be built.** The settlement scorer is already
nation-agnostic (`settlement_scoring.calculate_common_peace_acceptance`, zero `player_nation`
references) and so is the mutation core. But there is no AI term generator
(`ai_diplomacy.py:2419` returns `player_not_participant`), no AI acceptor, and
`settlement_validation.py:1121` returns `unauthorized_actor` for **any** non-player author. Owner row
**AI-4b**; the seam inventory is at §4.4.

**And the answer to a question §3 never asked:** *what does a court want on turn 3 of its war?* Its
`want` is intact and its `price` is `fight`. What moves turn to turn is its **resolve**, and resolve
is (c). No new field, no new rung — but if (c) and (d) are not built, a nation that reaches `fight`
never comes back down, and the ledger displays a *falling* exhaustion number for two powers grinding
each other, which is worse than displaying nothing.

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
| **Britain** | `low_countries` deny | The **paymaster.** Never wants a land war of its own; funds everyone who will march and denies the Scheldt. Its field armies and continental gains are as beatable as anyone's; what it defends is the *will to keep paying*. | `sponsor` (the branch, not the rung) | **Answers coercion with gold while no hostile army stands on British home soil** — an ultimatum from the continent buys another subsidy, not a concession; the Continental System strangles the trade that funds it, and an army in the home provinces is answered on the ordinary war-score path like any power | Pitt's subsidy system; the Berlin & Milan Decrees answering it |

**Britain is reachable — and v1.3 corrects *how*.** v1.1 wrote Britain as sitting behind a moat: "a
land threat cannot touch the core." **That is false in this codebase and the correction matters,
because a hard-coded never-folds is exactly the unbeatable-paymaster failure principle 7 forbids.**
`europe.json`'s `sea_links` contains `[116, 109]` — **London ↔ Flanders** — the registry folds sea
links into `adjacent`, and `adjacent` *is* the movement graph (`region.py:150` →
`movement_executor.py`, with no naval gate). Flanders' `starting_controller` is **France**. A French
corps can march on London from turn 1; DEF-6 (LANDED, Slice 8) kept the crossing walkable
*deliberately* and gated it with the 25k capital garrison — roughly three assaults, pinned by
`tests/test_map_slice8_balance.py`. §0 of this very spec records Britain taking Flanders by land.
**The Channel is a toll, not a moat**, and what DEF-5 adds is Ireland and the naval expedition, not
the first land route.

So Britain's coercion answer is **derived, never hard-coded**: *Britain answers coercion with subsidy
while no hostile army stands on British home soil.* An ultimatum from the continent buys another
subsidy — that is the correct and historical frustration, and it teaches the player that the front
door is the wrong door. But once a hostile army holds British home provinces, Britain's `statecraft`
permits conceding on the ordinary war-score path like any power; §5 pin 10 asserts only that it never
spontaneously adopts Austria's coalition-building profile. The cheap levers remain the interesting
ones: cut the trade (the Continental System, already modelled), or take its clients away (§3.7).

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

Bounded deliberately: promotion only from a durable record (never from a vibe), at most one emergent
design per nation, and it is announced as a beat. This is also what makes the DoD's "≥1 agenda shift"
an actual *system* rather than a deck-order tick — and it is the single mechanic most likely to
produce a campaign the player wants to tell someone about.

**v1.3 — where the record actually lives, because "the serialized grievance record" does not exist.**
The four triggers do not need the same machinery and must not be given the same store:

- **Partition and capital loss need no new store.** Derive them from serialized
  `nation_starting_regions` versus live control — the same comparison `agendas.survival_override_active:144-159`
  already runs — and derive the promoted design's `regions` (the lost homeland provinces) and
  `against` (their current controller) the same way.
- **A punitive settlement needs a durable record, and its home is `world.settlement_memories`** —
  serialized whole (`world_state.py:5339-5342`), pair-keyed, already written at the settlement-reaction
  seams, and already supporting `expires_in=None` durable mode (`settlement_reactions.py:196-221`).
  Add a `memory_type="punitive_settlement"` record at the ratify seam carrying author, provinces
  ceded and turn.
- **A broken compensation bargain** already has an owner: §3.3 plus §5 pin 8. Cross-reference only.
- **Do NOT extend `betrayal_history["grievance_flags"]`.** Its `to_dict`
  (`world_state.py:5231-5241`) projects exactly four scalar keys, so a `provinces` field silently
  vanishes on save/load; and its documented clearing route is Make Amends, which would let a player
  erase a partition with a gesture.

**Three code-forced constraints, each of which kills the mechanic in its named case if missed.**
**(a)** The promoted entry must be one of the five `AGENDA_TYPES` (`agendas.py:47-53`) —
`validator.py:461` errors on anything else and `_entry_active` silently returns False for an unknown
type, so an invented `"revanche"` type is a dead design. In practice it is an `acquire_regions` entry
over the lost provinces. **(b)** State **where in the deck it inserts**: `get_active_agenda:315-319`
is first-predicate-wins and §3.8.1 Tier 2 treats deck order as meaningful, so an appended entry
sitting behind a still-active design never activates — front-insert, with a pin. **(c)** The
**survival override outranks the deck** (`:306-313`) and fires on exactly the states §3.6 promotes
from, so the design must be *recorded at the humiliation* and *activate when the override clears*.
Pin both halves — a Prussia that is promoted to revanche while still fighting for its life, and whose
new design only becomes live once it is not, is the mechanic; anything else is dead code in precisely
the case it was written for.

*(Phrasing correction while we are here: the agenda grudge does not "expire at 10 turns" in the sense
of being destroyed — `archive_terminal_war_instances` deepcopies into serialized
`archived_war_instances`. What expires is `get_agenda_grudge_nations`' read window, because it never
consults the archive.)*

**4. The volte-face.** §3.4 gives Russia "reverses hard" as an adjective. Make it a mechanic: a great
power that is **beaten and then courted** — rather than beaten and humiliated — can reverse in one
settlement, from enemy to partner, and be aimed at a third party. That is Tilsit, and it is the
single most dramatic diplomatic event of the period. It is also a *player-caused* surprise, which is
the best kind: it rewards the choice to be generous to a broken enemy, an option the game currently
gives the player no reason to consider. It routes through the existing settlement layer plus the
`sponsor` branch, and it gets its own beat (§4.6a). *(v1.4: the reversal also retires or suspends
the reversed power's `contain_hegemon` design so its deck advances — "aimed at a third party" needs
an object to aim at, and §12.2 authors the design Russia advances to.)*

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
  outbidding war over Austria is the paymaster duel the period actually ran on. **v1.3 corrects the
  price:** this is *not* "a comparison inside a function that already exists."
  `get_british_subsidy_recipient` (`coalition.py:1084-1116`) compares relations *among coalition
  members* and cannot see a French offer at all. The outbid is a comparison between Britain's
  `get_paymaster_subsidy_amount` and **France's standing directed sponsorship obligation (AI-2b)**,
  evaluated where the recipient's alignment is decided — so this arm lands with AI-2b's directed
  record, not before it.
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

*v1.3 footnote — the table is scoped to the **political** layer, and should say so.* The decision
layer is deterministic; the **simulation is not.** Nineteen further backend modules use `random` at
84 sites — `combat.py:160-161` (the 2d6), `enemy_ai.py:428` (a per-decision mood roll on every attack
decision), `vassal.py:960/2091`, `jealousy.py:1135`. What is genuinely absent is *production
seeding*: `grep -rn "random.seed\|random.Random(" backend/` returns nothing, and no RNG state is
serialized. That distinction is load-bearing twice below — it is why the seed can be introduced
cheaply, and why §5 pin 14(c) cannot promise campaign replay.

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
Europe, and any pin may fix the campaign seed **and the ambient module RNG** to constants — the
`tests/test_combat_sweep_metrics.py:36-39` idiom, already used by 21 test files — and keep its exact
numbers), varied *across* them.

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

**Sequencing consequence: the seed lands with AI-1 or not at all.** Introduced late, every pin
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
| `nation_relations`, per pair, ±band | **Prussia's disposition is the definitional contingency of the period** — Haugwitz was sent to Vienna with something close to an ultimatum and arrived to congratulate Napoleon after Austerlitz. A 1805 in which Berlin is a little warmer or a little colder is 1805. **This row also carries the starting grudges** (Austria–Prussia over Germany, Russia–Ottoman over the straits, Prussia–Hanover): they are per-pair dispositions and the file already carries 29 such pairs. *Do not author a separate `starting_grudges` key* — both grudge readers (`agendas.get_agenda_grudge_nations`, `formations.get_formation_grudge_contributions`) are fully derived and emit THREAT under the shared `AGENDA_GRUDGE_CAP`, so an authored turn-0 grudge would add boot threat and fight pins 1 and 5. **Two clamps:** a band on any pair appearing in `starting_wars` or `diplomatic_states` may not change that pair's authored boot state, and no band may carry a pair across a documented behavioural threshold (the −80/−90 armistice-first band, the coalition threat inputs). `modding/validator.py` clamps the authored band; `from_scenario` does not re-clamp at runtime. |
| **Deck *order*** among equally-live designs | Which of a court's authored designs is live *first*. Never which designs it holds. |
| **Initial ladder readiness** (`weight`, starting rung) | How close a court begins to acting on a design it demonstrably held. This is §3.8's jitter applied at turn 0. |
| **The minors' lean** — bandwagon readiness | The genuinely uncommitted courts were up for grabs and §3.4 says a minor's aliveness *is* its timing, so this is the band that matters most. **v1.3 re-points it:** the eligible set is Saxony, Denmark, Portugal, Hanover, Hesse, the Papal States and Sardinia, plus the secondaries Naples, Sweden and the Ottomans. *Bavaria, Baden and Württemberg were the v1.1 examples and all three are wrong* — Baden and Württemberg are not nations in `EUROPE_ROSTER` at all, and Bavaria is Tier-1 committed by both `starting_wars` and a France ALLIANCE in `diplomatic_states`. **A minor already committed by `starting_wars` or `diplomatic_states` is Tier 1 for this band**, and the band governs bandwagon timing from turn 1 onward, never the turn-0 belligerent set. |
| **Britain's first subsidy client** | Pitt was shopping. **Derived, not separately authored** — `get_british_subsidy_recipient` selects on relation, so this falls out of the relations band for free. |
| `threat_level` (85), narrow band | Blessed balance number and the campaign's central pressure (D3) — a small band only; **widening it escalates**. |

**Tier 3 — derived.** Everything downstream follows and is never separately seeded: intent, coalition
posture, advisories, the §3.5 mirror.

**The historian test — the pin that makes this falsifiable. Six clauses (v1.3 corrected the fifth,
which was false, and split it in two).** Across the N-seed sweep, *every* seed must satisfy:

1. The **Third Coalition exists** and France is at war with Austria, Britain and Russia.
2. **France is at peace with Prussia** — Prussia's entry is a thing that *happens*, never a boot
   state.
3. Every nation **that has an authored deck** has a turn-0 active design drawn from that deck. *(Only
   10 of the 20 roster nations carry decks, and France carries none; the v1.1 phrasing "every
   nation's" was unsatisfiable as written.)*
4. **No nation boots eliminated**, and province ownership is **byte-identical to the authored map on
   every seed** — Tier 1; the seed never touches the map. *(The elimination half is a live check, not
   a tautology: elimination is derived from region holdings, and NA-6c shipped carve logic that
   mis-announced eliminations.)*
5. **The boot war set and alliance map are authored, never seeded.** The `starting_wars` rows and the
   `diplomatic_states` map are byte-identical on every seed; the seed may not add, remove or re-point
   a war or an alliance.
6. **The 1805 alignment holds on every seed:** Bavaria and the Kingdom of Italy stand with France
   against Austria; Spain and Holland with France against Britain; Prussia neutral.

A seed that fails any of these is a build failure, not a colourful opening.

> **v1.3 correction — the fifth clause used to read "· no minor boots at war," and it is false on the
> shipped scenario.** `europe_1805.json`'s `starting_wars` are France→Britain, France→Austria,
> France→Russia, **Spain→Britain, Holland→Britain, Bavaria→Austria and KingdomOfItaly→Austria**;
> `NATION_POWER_TIERS` rates Bavaria, Holland and the Kingdom of Italy `minor`. So the phase's one
> falsifiable historical pin contradicted Tier 1 four paragraphs above it and would have redded on
> turn 0 of the `historical` seed — the seed whose entire promise is that it reproduces today's boot
> byte-for-byte. It was also *historically* wrong: Spain, Holland, Bavaria and the Kingdom of Italy
> were belligerents in 1805, and clauses 5 and 6 now pin that fact instead of forbidding it.

**The `historical` seed — the migration contract, and why this costs no test churn.** **Unset, or
`SOVEREIGN_SEED=historical`, reproduces today's boot byte-for-byte** — every band collapses to its
authored centre — so the existing suite, the E1 economic band, M1–M7 and the §4.4a threat series keep
their exact numbers with no edit. §5 pin 1 is **narrowed** to "the historical seed is byte-identical,"
the same additive pattern §4.4a uses and which this project has already run successfully once.

*v1.3 corrects where the default lives, and it is not a footnote.* v1.2 said `SOVEREIGN_SEED` "joins
the documented boot-precedence chain in `main.py`." It cannot: `main.py`'s `_resolve_scenario_path()`
is a mutually-exclusive selector that returns one *path*, and a seed is orthogonal to it — worse,
under the suite's own `SOVEREIGN_SCENARIO="none"` pin `main.py` never loads `europe_1805.json` at
all, and **75 direct `WorldState.from_scenario(...)` calls across 42 test files bypass `main.py`
entirely**, including `test_combat_sweep_metrics.py:531-532`, which builds the M7 world as
`from_dict(from_scenario(...).to_dict())`. So **the default must live in the model**: the seed is
fixed in `WorldState.__init__` from the environment — the in-model `SMOKE_START_ENV` idiom already at
`world_state.py:68` — with an explicit `seed=` override on `from_scenario`. `main.py` *reports* the
seed in its boot banner and documents it *alongside* the precedence chain rather than as a rung in
it, and `conftest` pins it suite-wide as defence in depth rather than as the mechanism. Get this
backwards and §5 pin 2 (M1–M7) is red on day one.

**The seed is shown and shareable** — rendered in the ledger and written into the save, so a good
opening can be replayed or reported against. One string, real value.

*Reconciliation with §3.8's "weighted late":* that guidance stands with a nuance D7 forces. Turn 1
still *looks* like 1805 on every seed — Tier 1 guarantees the tableau — and what varies at boot is
**dispositions, not the map**. The two levers are complementary: Tier 2 supplies the spread in initial
conditions, the §3.8 jitter supplies the compounding that turns it into a different mid-game.

### 3.9 Historical attractors — why turn 40 still rhymes *(v1.3)*

The historian test is a **boot** test. §3.8 promises that the mid-game "forks entirely." §7a demands
that seven historical scenes be reachable. Nothing in v1.2's 1,185 lines explained why a campaign
that has genuinely forked should, at turn 40, still look like 1805–15 — and the phase's brief asks
for *assured historic outcomes* and *variability* in the same sentence, a tension the spec never
named. This section names it and resolves it.

**The resolution: assure the shapes, vary the casting.** Assured outcomes and variability are in
tension only if "outcome" means an *event*. This phase assures **shapes** — a coalition forms against
the strongest power; a bought-off design becomes a hostage; a paymaster funds a war it never joins; a
beaten power is either humiliated into revanche or courted into partnership — and varies **which
nations, which provinces, and which turn**. *A seed that produces the Fourth Coalition against
Austria in 1809 over Silesia is a better outcome than one that reproduces 1806, not a worse one.*

**The campaign rhymes because the *forces* are constrained, not because the outcomes are.** Four
attractors do that work, and all four are already in this spec — they were simply never collected:

1. **D3's gravity condition.** A coalition forms against a non-player hegemon only when that power's
   hegemony share exceeds France's. Whoever is strongest accumulates Europe's enmity, and in a
   Napoleonic campaign that is usually France. This is the single strongest attractor in the phase.
2. **Tier-1 authored content (§3.8.1).** The map, the roster, the decks, the marshals and the
   `statecraft` profiles are fixed on every seed. The *cast* is constant even when the plot is not,
   and a constant cast with constant motives produces recognisable drama from any starting hand.
3. **§3.4's statecraft.** Each major's response to a given pressure is recognisable regardless of
   seed: Austria builds a bloc, Prussia sells its position, Russia intervenes far from home, Britain
   pays. Same pressures, same characters, different order of events.
4. **§3.3's compensation-and-renege loop.** This is a historical *shape*, not a historical *event*.
   Schönbrunn → Jena can run between different parties, over different provinces, on different turns,
   and still be the same story — which is exactly what "historic outcomes with variability" means.

**And it is measurable, which is the point.** §7a's seven scenes are the falsifiable form of this
section, and their acceptance verb is **shape reachability**: *a scene counts when its mechanic
produced its shape, regardless of which nations played the parts.* Scene 3 does not require Prussia
specifically; it requires that a bargain was broken and that the war which followed said so. §7's DoD
carries the same claim as a testable line ("Turn 40 still rhymes"), asserted across the sweep.

*Where this bounds the seed:* an attractor the seed can switch off is not an attractor. Nothing in
AI-0b/AI-0c may band D3's gravity condition, the `statecraft` profiles, or the existence of the
compensation loop. Those are Tier 1 by this section as well as by §3.8.1.

---

## 4. Slices

Ordered so each lands standing on the previous one, and so the first two are playable and
falsifiable before anything can declare a war.

*(Reference convention, stated once because v1.2 used it without ever defining it: the slice headings
below are numbered subsections of §4 in order — **AI-1 = §4.1, AI-2 = §4.2, AI-3 = §4.3, AI-4 = §4.4,
AI-5 = §4.5, AI-6 = §4.6, AI-V = §4.7** — so a cross-reference to "§4.5" means the AI-5 slice.
Lettered subsections (§4.2b, §4.2c, §4.3a, §4.4a, §4.4b, §4.6a, §4.6b) sit inside their parent
slice.)*

### AI-1 — The Intent Layer (read-only)

**Cache siting (v1.3 — replaces the deleted AI-0 prerequisite, §0.1 Correction D withdrawn):** intent
hangs its per-turn cache on the **same** chokepoint the agenda cache already uses — add
`self._intent_cache = None` beside `self._agenda_cache = None` in
`WorldState.invalidate_bloc_members_cache` (`world_state.py:1695`), **not** in
`invalidate_active_nations_cache` — and mirrors the two existing agenda pins
(`test_nation_agendas.py:251, :265`) for intent. One real gap comes with the slice rather than before
it: intent additionally reads **relations, relative force and treasury**, none of which reaches that
seam. AI-1 decides and pins whether those terms are turn-granular by design — the choice
`agendas.py:17-20` already makes for treasury — or whether `modify_nation_relation`
(`world_state.py:1760-1778`) is wired to the chokepoint.

Build `backend/game_logic/intent.py`: one derivation chokepoint, `get_nation_intent(nation, world)`,
per-turn cached on the `get_active_agenda` pattern (`agendas.py:294-299` — per-nation dict under a
turn key), invalidated through the existing chokepoint (`world_state.py:1682-1695`, which 28
production call sites reach). It reads the existing agenda view, region control, relations, relative
force, war state and grudges — and writes nothing.

Deliverable is a **pure reading of the world plus its legibility surfaces**: `build_intent_payload`
mirroring `agendas.build_agenda_payload:1214`, hung on the Diplomatic Ledger's nations-tab row as an
`"intent"` sibling to the existing `"agenda"` key (`diplomatic_ledger.py:415`) — un-fogged by the same
DPF-1 precedent — and read by Talleyrand at the two sites that already consume the agenda payload
(`diplomatic_advisory.py:216,366`). Zero behaviour change; the player can now see what every nation
wants and what it is currently prepared to pay.

**And it renders (v1.3): the payload is not the deliverable, the render is.**
`diplomatic_ledger.gd:380-397` draws the `agenda` key with hand-written key-by-key GDScript and has
**no generic key iteration**, so a new sibling payload key renders *nothing*. The `.gd` work for the
intent row, the §3.5 mirror row and the §3.7 subsidy row lands **inside its own slice, not deferred
to AI-6** — because D6 schedules the user re-check after AI-1+AI-2, and a re-check that judges "a
Europe that visibly wants things" against an invisible build is worthless. Standing XR-1 rule
applies: boot the engine and grep `SCRIPT ERROR` before landing. Contract at §4.6b.

*Why first:* it is falsifiable on its own (boot intents are pinnable against the authored 1805
opening), and it makes every later slice debuggable.

### AI-2 — Peacetime pursuit (the cheap rungs)

Wire `ask` / `buy` / `align` / `bandwagon` into `ai_diplomacy.process_diplomatic_phase:898` as
intent-driven proposal selection. Today rungs P3/P4/P7 fire on relation and threat scalars; they
should fire on *what the nation is trying to achieve*. Prussia wanting Hanover should be courting
Hanover, subsidising a claim, or seeking a guarantee against Austria — visibly, in the mailbox,
within the delivery budget of §4.2c.

This alone converts five idle courts into active ones without a single new war, and gives the player
a peacetime diplomatic game to play.

*Includes:* **the third-party generalisation, which is the slice's real bulk — split out in v1.3 as
its own row, AI-2a, because it is not one parameter change but six seams.**
`process_diplomatic_phase` returns `None` when `nation == player` and reads every state, relation and
war score against `player` (`:934-941`) — it is structurally a France-facing function. The AI-vs-AI
path is a *separate*, much narrower function (`process_ai_ai_diplomatic_phase:1954`) whose ladder
cannot express a demand, let alone a war, and which per §0.1 Correction C had never successfully
ratified a treaty until a July 2026 fix. Converging these two paths so an intent-driven proposal
resolves the same way regardless of who is on each end is the prerequisite for AI-3 and AI-4.

The six seams, named so the row is buildable:

1. **The envelope.** `_build_proposal_terms` (`ai_diplomacy.py:491`) hard-codes
   `"target_nation": player` at `:513`; `_make_proposal` (`:1175-1199`) has **no target field at
   all** and stamps `get_game_bucket` + `_get_talleyrand_assessment` — France's perspective — onto
   every proposal.
2. **The transport.** `deliver_ai_proposal` (`:1343-1405`) is player-only end to end; the AI-AI path
   has no transit at all.
3. **Resolution is asymmetric.** The player gets Accept / Reject / **Counter**; the AI-AI path gets
   ratify-or-nothing. **Decide the counter-offer arm explicitly** — either scope it in, or record the
   asymmetry and amend this slice's own acceptance sentence, because as written a no-counter AI-AI
   path silently fails the only criterion §4.2 states.
4. **Cooldowns are keyed differently on each path** — per-NATION on the player path
   (`_is_on_cooldown:245`), per-PAIR on the AI-AI path. Re-key to an **ordered** `(proposer,
   recipient)` pair — *not* `_make_diplo_key`, which sorts and would collapse "Prussia asks Austria"
   with "Austria asks Prussia" — as a save migration in the §4.4a additive idiom: `ai_proposal_cooldowns`
   is serialized (`world_state.py:5159` / `:5698`) and legacy `"{nation}|nation"` keys read as
   `(proposer=nation, recipient=player)`. Fold `ai_stalemate_counters` (nation-keyed,
   `world_state.py:708`, read `diplomacy.py:4409` / `:6592`) into the same migration.
5. **The refusal producer, which does not exist and is not optional.** `_evaluate_ai_ai_proposal`
   either returns `None` or ratifies; `ai_ai|{diplo_key}` is written only inside `_ratify_treaty`
   (`world_state.py:8405`). **There is no refusal moment on that path at all.** §5 pin 8 requires
   refused asks on the serialized record and §4.3 makes that record the war gate — so **AI-2a must
   build the refusal record and its public event on both paths, or AI-3's central gate is
   unsatisfiable for exactly the wars AI-3 exists to create.**
6. **The good news, so the row is not over-priced:** `calculate_acceptance`
   (`diplomacy.py:6508-7016`) has **zero** functional `player` references and `_ai_ai_acceptance:2087`
   already calls it. The scorer needs no work.

*Pin:* the whole player-facing proposal flow — generation, delivery, dialogue, accept/reject/counter,
cooldowns applied — is byte-identical before and after AI-2a, green before any non-player recipient
is ever passed. That makes AI-2a a no-behaviour-change refactor which may run in parallel with AI-1,
exactly like §4.4a.

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
| **Sell neutrality** | D5 compensation, in reverse — the AI pays *you* to stay out | Prussia's entire 1795–1806, played from the other side. **And the payment creates a §3.3 standing expectation against the payer:** entering the war later is *reneging*, the highest-weight casus belli in the game. Selling neutrality is a hostage France has given, not free money — without that, "refuse everyone" is strictly dominated |
| **Sponsor without joining** | the `sponsor` branch through `get_paymaster_nation` | being Britain for once |
| **Broker** | the existing settlement package, third-party-capable per AI-4 | ending someone else's war on your terms, for a price |
| **Refuse everyone** | — | and watch, having been *asked*, which is the whole difference |

The last row is the point. A war the player was courted about and declined to touch is a decision;
the identical war with no courting is scenery. This is the single highest fun-per-line item in the
phase.

**One legibility dependency, and v1.3 corrects its price from zero to a slice.** The ledger must show
third-party **war exhaustion**. v1.2 called this "a display wire, not a system" because
`world.war_exhaustion` is already a per-nation dict (`coalition.py:1248, 1265`) "already accrued from
battles." **Both halves are false, and the truth is worse than nothing being there:**

- Every battle accrual arm (`combat_executor.py:1710-1754` and its auto-combat mirror
  `world_state.py:9702-9730`) is France-conditioned except the garrison-stalemate arm.
- The per-turn tick (`coalition.py:1825-1833`) keys AI rows on `_get_diplo_state(world, france,
  nation)` and **decays −5/turn** for any nation not at war with France.

So two AI powers fighting for twenty turns converge on exhaustion **0** — and four such wars exist at
boot (Spain and Holland against Britain, Bavaria and the Kingdom of Italy against Austria). The
ledger would show a *falling* number for two powers grinding each other, which is worse than showing
nothing. This makes war exhaustion the **fourth** France-literal system to generalise, it moves out
of AI-2d's display half into its own owner row **AI-4c**, and per §3.1a it is the load-bearing seam of
the *descent*: three live peace-seeking terms read `we` and all three silently no-op at 0.

*What AI-4c must do:* key the per-turn tick on `world.get_nations_at_war_with(nation)` — the exact
predicate France's own arm already uses at `:1817` — which fixes accrual and the −5/turn drain in one
edit; add an explicit `if france not in (attacker.nation, defender_nation):` arm to **both** combat
copies (a trailing `else` does not work, because `elif defender_won:` swallows the defender-won
third-party case); and carry the Europe scoping (`sovereign_map == "europe"`), because the legacy
fixture world boots at war and an ungated tick drifts its pinned economy.

*And the display must be **per war**, not per nation.* When both third-party belligerents are also at
war with France — the 1805 boot case, Austria and Russia — the France-pair tick gives each +8/turn, so
a bare per-nation scalar would report *French*-war exhaustion as "they are bleeding each other."
Either the row is per-war, or it is explicitly labelled as national exhaustion across all wars.
Otherwise "let them bleed each other while France rearms" — a core fantasy stated in §1 — is
unplayable in exactly the configuration the campaign opens in.

*Landing split:* the **sell-neutrality** and **sponsor** arms ship with AI-2 (they need only the
diplomacy path). **Join** and **broker** ship with AI-3/AI-4, because they need a third-party war to
exist and to be endable. The row is tracked as one item so neither half is orphaned. *(v1.3: the
exhaustion display leaves this row for AI-4c — it is a system, not a display.)*

#### 4.2c — The delivery contract (what actually reaches the mailbox) *(v1.3)*

§4.2 promises intent asks arrive "visibly, every turn, in the mailbox." Taken literally that is both
unachievable and undesirable, and the spec should say which it means.

**Unachievable, because a throttle already eats them.**
`turn_manager._process_ai_diplomatic_phase:440-459` buckets every proposal whose `decision_reason` is
`hegemony_pressure` or `agenda_pursuit` — the reason NA-1 introduced for exactly this class of ask —
into `MAX_BANDWAGON_PER_TURN = 2` world-wide, with a **silent `continue`**. And `decision_reason` is
*derived* at `_build_proposal:1189` via `determine_ai_offer_decision_reason` (`diplomacy.py:7223`),
so intent asks inherit the throttled labels automatically and cannot be exempted by passing a new
reason at the call site. Stacked on top: `_has_pending_proposal_from` (one live proposal per nation),
`TYPE_LAPSE_COOLDOWN = 6` and `NATION_REJECTION_COOLDOWN = 3`.

**Undesirable, because §4.6's cap and §5 pin 13 exist.** "Every turn" collides with both, and with
the W6-10 anti-monotony lesson this spec endorses elsewhere.

So: **intent asks carry their own world-wide per-turn budget** — a blessed number, tunable in-band —
sized so §4.2b's marquee case, *both* belligerents courting France in the same turn, cannot be
starved by an unrelated bandwagon proposal. Use the exemption precedent already in that block:
`turn_manager.py:449-455` carves ultimatums out with a comment naming this exact bug class. Carve
`_has_pending_proposal_from` explicitly. And resolve the opportunism collision with the existing
`URGENT_REPROPO_DELTA` bypass — §3.2's marquee promise is that willingness rises precisely when the
holder is committed elsewhere, and a 6-turn lapse cooldown would silently eat that moment.

*Replace §4.2's "visibly, every turn, in the mailbox" with the stated budget.* Do **not** solve this
by removing the throttle: removing a throttle without a replacement is exactly the jealousy volume
failure this spec cites against itself, reintroduced at a higher event rate.

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
- **A stated reason — and v1.3 splits it in two, because as written it was impossible.** v1.2 said
  the war "carries its design as `war_objective`." It cannot:
  `OFFENSIVE_OBJECTIVE_TYPES = {"conquest", "subjugation", "forced_alliance"}` (`diplomacy.py:2944`),
  and `declare_war:7562-7567` returns `{"success": False, "message": "Invalid offensive war
  objective: …"}` for anything else, while `OBJECTIVE_TYPE_DISPLAY` has no entry for a design id and
  `.get(k, k)`-leaks the raw key at four render sites — an R7 violation. So: the **objective type**
  is an enum member (`subjugation` where the design is vassalage, `conquest` otherwise, falling back
  to `conquest` when `_get_objective_availability` refuses), and the **stated reason** is the agenda
  `title` (`agendas.py:68`, already exposed by `build_agenda_payload:1214`). The war surfaces render
  `OBJECTIVE_TYPE_DISPLAY[type]` for the mechanic and the title for the reason; no design string ever
  enters the display map. Setting `target_regions` to the design's coveted provinces instead of
  `[capital]` applies to AI-initiated wars carrying a design **only**, leaving the player's War
  Purpose numbers byte-identical. Adding a `design` / `grievance` key to the existing
  `create_war_objective` record (`diplomacy.py:3199-3220`) is **reuse**, and §8's "no new war-goal
  system" scope line should say so explicitly.
- **The ladder must have been climbed.** Declaration requires prior refused asks/coercion **on the
  serialized record** (§5.8); no cold-open wars. The exceptions are §3.3 reneged compensation, which
  is itself a record of a prior bargain — **or a rung that is structurally unavailable** (§3): a court
  whose asks are legally impossible reaches `coerce` through the NA-5 ultimatum rung, which already
  force-sends past the acceptance filter (`ai_diplomacy.py:862`). Stated so this is not read as an
  absolute the ladder itself never claimed. *(Note the dependency: the serialized refusal record does
  not exist on the AI-AI path today — AI-2a builds it, §4.2 seam 5.)*
- **Restraint gates:** force ratio, treasury, existing war load, alliance webs, armistice cooldowns,
  **war-objective availability, war-instance side conflict**, and the D1 world-wide cap on
  simultaneous AI-initiated wars.
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

#### 4.3a — The declaration contract (what "reuse the seam" actually requires) *(v1.3)*

§0.1 Correction A's insight is right and must survive: **AI-3 adds no new PEACE→WAR edge.** But "the
declaration plumbing exists" is true for exactly one pre-war state, and the gap between one and all
of them is where undeclared conquests live. Four requirements.

**1. The declaration is a step AI-3 owns, not a side effect it hopes for.** At the §4.6 fore-warning
seam, AI-3 calls `diplomacy.declare_war(world, coveter, target)` **itself** — the same function
`combat_executor.py:3482` calls, so the DoD's "no new PEACE→WAR edge" is untouched, and the announced
war is backed by a state change rather than by a promise the seam may not keep. This also resolves an
apparent contradiction in v1.2: fore-warning says the war is announced *before* the army moves, while
the seam declares war *at* the attack. AI-3 declares at the announcement; the seam's own declaration
then finds the war already live and is a no-op.

**2. Treaty states gate the `fight` rung.** A coveter holding any `OPEN_MOVEMENT_STATES` treaty with
its target must **break it or let it lapse first** — a visible ladder step between `coerce` and
`fight`. Without it, `:3529`'s guard skips the declaration entirely and the AI marches in and
captures with no war, no objective and no reason to render; and `friendly_fire_refusal` would make a
fore-warned war a silent no-op against an ally.

**3. The declaration is the gate, not a side effect.** `:3483` and `:3533` currently *discard* a
refused `declare_war` for a non-player attacker and proceed to battle, garrison combat and
`_attempt_region_capture`. AI-3 adds an explicit abort at both.

**4. The intent layer pre-checks the same refusals** through one shared `can_declare_war` preview —
armistice cooldown, objective validity and availability, war-instance side conflict — so the abort is
a fail-safe rather than the normal path, and a fore-warned crisis never dies silently.

**The mainline blocked case, named so it is not discovered late.** Two co-belligerents against France
cannot declare on each other (`settlement_helpers.py:644-645`: a nation that would land on both sides
of a merge cannot reconcile incompatible sides). So **Prussia defecting from a coalition** needs the
VS-6 side-exit pattern (`vassal.py:1947-1975`) lifted into a shared helper: peace out the defector's
WAR pairs, then declare. Without it, §7's DoD line "one betrayal or defection" is unreachable for the
boot Third Coalition — which is the only coalition the campaign opens with.

### AI-4 — A continent, not a hub (de-France-centering)

Make the consequences of AI-vs-AI war real, by generalising **four** France-literal systems *(v1.2
said three; war exhaustion is the fourth and was priced at zero)*:

- **Threat** — per §4.4a below, including its v1.3 steps 5–6. This is the slice's bulk.
- **Coalitions** — the coalition subsystem is **de-France-anchored**, per the migration contract at
  §4.4b. *(v1.2 priced this as "`form_coalition` takes a target instead of binding
  `world.player_nation` (`coalition.py:1323`)". It binds the player at **nine** sites — `:850, :878,
  :911, :927, :960, :1011, :1323, :1518, :1708` — plus two singleton-keyed readers, and
  `world.active_coalition` is a single `Optional[dict]` with 55 backend and 8 `.gd` references.)*
  Subject to D3: a coalition forms against a non-player hegemon **only when that power's hegemony
  share exceeds France's**, so the anti-France coalition cannot be diluted by the generalisation.
- **War exhaustion** — per §4.2b's v1.3 correction and §3.1a(c). It never accrues to a third party
  and decays −5/turn, so the three live peace-seeking terms that read it — the settlement-acceptance
  component `min(20, we // 3)` (`settlement_scoring.py:1459-1486`), the peace threshold
  (`ai_diplomacy.py:944`) and the patience term (`:958`) — all silently no-op for any war France is
  not in. Owner row **AI-4c**.
- **Settlements** — third-party wars must be able to end without the player, through the existing
  settlement package, and appear in the ledger as news. **Without this AI-3 is a one-way ratchet**:
  wars that start and never end. This is a hard dependency of AI-3, not a nice-to-have.
  *v1.3 replaces "generalising" with the seam inventory, because the halves are in very different
  states:* **Reusable as-is** — the scorer (`settlement_scoring.calculate_common_peace_acceptance`,
  zero `player_nation` refs) and the mutation core (`_apply_settlement_terms` /
  `_resolve_pair_state_transitions` / `_record_common_peace_treaties`, `settlement_ratify.py:226/618/838`).
  **Already a wire** — the news half (`is_settlement_event_visible`, `settlement_presentation.py:317`).
  **Must be built** — drop `player_not_participant` (`ai_diplomacy.py:2419`) for the AI-AI arm and
  rename `_settlement_offer_build_terms`'s `player` parameter to `accepter`; **open the
  `unauthorized_actor` gate** (`settlement_validation.py:1121`) and say what replaces it (an
  actor-is-a-belligerent-on-the-proposer-side check); an AI acceptor scoring through the existing
  scorer with no dialogue; a **headless ratify wrapper** that assembles the pair plan and calls
  `_apply_settlement_terms` directly and **never touches `world.dialogue_manager`** — `ratify_settlement_confirm`
  pops the mount at `settlement_ratify.py:1473` and `stage_settlement_confirm` refuses a second
  concurrent settlement at `settlement_staging.py:3178`, so the mount is a single global slot; and a
  **nation-pair-general territorial term generator**, which does not exist today
  (`_settlement_offer_build_terms` emits only `peace` + `gold_indemnity`, plus a carve clause gated
  `payer == player`) and which §7a scene 7 requires.

**The stopgap, and the decision v1.3 forces.** v1.2 said that if AI-4 slips, AI-3 ships with "a blunt
AI-vs-AI armistice as a stopgap." That stopgap is narrower than it sounds: an armistice terminates
through the existing `armistice_expired_peace` arm (`diplomacy.py:9119`) only at relation ≥
`ARMISTICE_AUTO_PEACE_RELATION` = −60, so it does **not** cover a pair already below that line — which
is precisely the pair that fought a war. So **pick one and say so in §8**: either AI-4b is Core and
un-slippable and the stopgap is deleted, or the stopgap is the shipped v1 and the DoD lines it
carries (wars that "end", ≥1 third-party settlement), §7a scene 7, §4.2b's Broker row and §4.6a
beat 6 are each re-marked with a written blocking predicate. As drafted, Core rows depended on a
slippable one, which is the failure GR9 exists to prevent. **This spec picks the first: AI-4b is
Core.**

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
   after the migration, **at a fixed ambient RNG seed K and `SOVEREIGN_SEED=historical`** (v1.3 — the
   run passes through `enemy_ai.py:428`'s per-decision mood roll and `combat.py`'s 2d6; without the
   RNG clause this pin is unachievable and reds on every run, and it gates the phase's highest-risk
   slice). This pin is written and green *before* any non-player target is ever passed.

Only once that is green does any producer start passing a real target — which is **steps 5 and 6**,
added in v1.3 because v1.2 carried them as a single closing sentence. They are the larger half.

**5. The producer migration.** State the rule once, because it makes the conversion nearly
mechanical: **`target` is the ACTOR, never the victim.** Today's scalar rises from France's *own*
deeds, and `_calculate_hegemony_pressure` returns `{hegemon: increment}` — so keying by victim would
credit Austria for France's conquests and break the byte-identical pin. Every site already binds the
actor in its guard expression, so the conversion is "delete the `== world.player_nation` guard, pass
the guarded variable as `target`": `attacker.nation` (`combat_executor.py:1712/1721/1727/1742/1750`
plus the mirror `world_state.py:9702-9729`), `capturing_nation` (`world_state.py:2901`), `to_nation`
(`settlement_ratify.py:314`), `proposer_member` (`:801`), `lord` (`vassal.py:188/271`),
`breaker_nation` (`diplomacy.py:9506`), `nation_a` (`:8589`), `aggressor` (`:7659`), and the
ultimatum family (`diplomatic_executor.py:3700-3715`). Handle the `process_coalition_turn` standing
block separately (`coalition.py:1721-1791`): `region_control_*` and `hegemony_passive` need per-nation
loops — `:1738-1745` **already computes `{hegemon: increment}` correctly and discards it**, and it is
the fuel D3's eclipse clause needs — while the four other contributors (`defensive_refusal_memory`,
`schemer_peace_rejection`, `agenda_grudge` / `formation_grudge:<tag>`, `ultimatum_defied`) each need
either a per-nation generalisation or an explicit written "stays France-only" decision. Silence there
is how this gap recurs. **Without step 5, `threat_by_target[X]` is permanently 0 for every non-player
X and D3's "the player can genuinely be eclipsed" is structurally unreachable.**

**6. Decay, and the threshold reader.** Decay is the *only* mechanism that lowers threat, and it
bypasses `add_threat` / `reduce_threat` entirely: `coalition.py:1793-1802` writes `world.threat_level`
directly and appends its own untargeted `{"source": "decay"}` entry, and `_calculate_threat_decay` is
France-shaped throughout (two further direct writers exist at `meta_executor.py:2018` and
`world_state.py:5759`). So: `_calculate_threat_decay(world, target)` re-keys its self-exclusion and
its `_get_diplo_state(world, france, n)` loop to `target`; the Continental-System `+1` (`:894-897`) is
a France-only instrument and applies to the player slot only, stated explicitly; the direct write at
`:1793-1802` routes through `reduce_threat(..., target=...)` so the log entry carries a target like
every other; and the brewing / instant / threshold block (`:1863, :1877, :1916`) runs per target with
non-zero threat, subject to D3's gate. **Without step 6 any non-player slot is a one-way ratchet to
the clamp** — a permanent coalition trigger against Austria, which is neither D3, nor pin 5, nor 1805.

#### 4.4b — Coalition migration contract *(v1.3, the second long pole)*

Same size and rigour as §4.4a, and it was priced as one parameter change.

**Open with the D3 arbitration ruling, because it determines the data structure.** State explicitly
whether an anti-France coalition and an anti-hegemon coalition may be **simultaneously active**, and
if not, which wins and what happens to the loser. D3 today says Europe turns on Austria *"instead"* —
which reads as exclusive but is never stated as a rule.

- *If exclusive*, the singleton suffices and the migration is mostly anchor work:
  `world.active_coalition` **already carries a `target_nation` key** (`coalition.py:1387`).
- *If concurrent*, use the §4.4a pattern — `active_coalition` becomes a property over
  `coalitions.get(player_nation)` **with a setter**, because `from_dict:5770`, `form_coalition:1384`,
  `set_coalition_posture:1410` and the dissolve path `:1546` all assign to it — and state whether
  `coalition_count` and the `_ORDINALS` naming ("The Third Austrian Coalition") are per-target or
  world-wide.

**Then the anchors.** Enumerate the nine France-literal bindings (`:850, :878, :911, :927, :960,
:1011, :1323, :1518, :1708`) plus the two singleton-keyed readers (`get_coalition_loyalty_penalty:1241`,
`add_coalition_shock:1297`), giving each an optional `target` defaulting to `world.player_nation`.
Flag `coalition_leadership_score:963` as the one that must change **semantics** rather than gain a
default — it carries its own docstring admission at `:950-951`: *"the `france` hostility anchor stays
France-coupled in v0.1 … D2 Coalition Generalization will generalize."*

**Assign the two threat producers that fall between the two contracts** —
`_calculate_defensive_refusal_memory_threat:844-850` and `_calculate_threat_decay:873-899` —
explicitly to AI-4a or AI-4b, so neither is orphaned in the seam between them.

**Close with the §4.4a-idiom pin:** a boot world plus a 40-turn run produces a byte-identical
coalition formation / brewing / dissolution series — name, leader, members, formed turn, posture —
before and after, green *before* any non-player target is passed.

### AI-5 — Intent into the existing systems

Intent is only worth building if it feeds what is already there. Each of these is a small wire, not
a new system:

| System | What intent unlocks |
|---|---|
| **NA formations** | A nation that *pursues* an acquisitive design can finish one. Poland, Italy and the Roman Republic become reachable without the player brokering them. |
| **Vassals** | Intent explains courting and defection pressure — a lord with a strong design is a lord worth following or worth leaving. `bandwagon` is the vassalage on-ramp. |
| **Economy** | War Effort and subsidy flow with intent. *(v1.3: the coalition subsidy stays as-is — `get_paymaster_nation` is its special case, not the general branch. The `sponsor` branch's executor is the **directed payment record** in AI-2b.)* |
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
dispatch and collapses into the tail; the named beats *(seven since v1.4)* are exempt in the same way fore-warnings
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
7. **The Crisis Passes.** *(v1.4)* The other ending. A foregrounded crisis that de-escalates — the
   design bought off, the coveter deterred by a guarantee, the moment starved as §3.2's opportunism
   decayed — is **announced with its cause named and the instrument credited**, on beat 2's own
   transports. *"Berlin stands down, Sire. The King will not test your guarantee of Hanover."*
   Without this beat deterrence is invisible: the player who successfully prevents a war sees
   nothing, and the D5 instruments teach nothing at the exact moment they work. Ochakov 1791; the
   Prussian mobilisation dissolving after Austerlitz. Conservation of narrative, not added noise: a
   crisis that was foregrounded already owed the player an ending — this beat is the second of
   exactly two. Pin 21; full argument §12.1.

**Tempo — one foregrounded crisis at a time, world-wide.** Other intents continue to climb silently
and surface when the foreground clears. The phase's failure mode is not too few wars — D1 already
bounds that — it is **four simultaneous crises reading as noise**, which is exactly how jealousy
failed in both the July-10 and July-19 audits. The lesson is available in advance this time; the rule
is the standing brewing-crisis limit, and it is a blessed number tunable in-band.

**v1.3 — name the transport for all beats, not one** *(v1.4: seven beats; beat 7 rides beat 2's
transports by construction)*. "Each one an existing transport" is asserted but
only beat 1 and beat 3 are traced to one. The default is **reuse**: branch
`incoming_proposal_popup.gd` on a new dtype in the NA-5 `is_ultimatum` pattern. Only if a beat mints a
new `.tscn` does the CanvasLayer band need resolving — and it does need resolving then, because
101–119 is fully occupied with 110 and 115 already double-booked. Any new dtype also needs the
`main.gd` whitelist (the `:12` const plus **both** `dtype in [...]` lists at `:3996` and `:4039`),
without which it falls through to terminal text — a recurring bug CLAUDE.md lists by name.

#### 4.6b — The client surfaces *(v1.3)*

**A payload key is not a surface.** This phase contained no Godot work at all — the word "Godot"
appeared zero times in v1.2's 1,185 lines and `.gd` appeared three times, all inside a reference
count — in a spec whose principle 4 says legibility is the feature and not the reporting of it. The
proof that this matters: `diplomatic_ledger.gd:380-397` renders the `agenda` key with hand-written,
key-by-key GDScript (`title`, `stance_line`, `forms.display_name`, `forms.progress`) and has **no
generic key iteration**, so §4.1's `"intent"` sibling key renders nothing at all.

The files and the specific edit each needs:

| File | What it must gain |
|---|---|
| `diplomatic_ledger.gd` | the Intent row, the §3.5 mirror row, the §3.7 subsidy row, and third-party war exhaustion — it already reads `war_exhaustion` at `:810` |
| `war_status_panel.gd` / `war_detail_popup.gd` | third-party wars — note `war_status.py:41-42` **drops every war France is not in**, so the neutral third-party row is backend *and* `.gd` work |
| `mailbox_panel.gd` | AI-2 ask rows |
| `dispatch_view.gd` | ladder-movement lines |
| `main.gd` | the dtype whitelist for any new dialogue type (see §4.6a); `cooldown_manager.py PRIORITY_ORDER` + `dialog_manager.register()` for any new popup |
| a courting surface | §4.2b's five answers need somewhere to be answered |

**Ownership rule, so this does not become a dumping ground:** every row that names a ledger row, a
display or a beat **lands its own render in its own slice**. AI-6c owns only what no earlier row
claimed. And the standing XR-1 rule rides every `.gd`-touching row: boot the engine, grep
`SCRIPT ERROR`, before landing.

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
- **v1.3 amendment — the sweep is three arms, because the run is already nondeterministic.** The
  variance pin immediately above cannot be evaluated as written: a 40-turn AI-only run varies
  run-to-run *today*, with no campaign seed at all, because `enemy_ai.py:428` rolls a mood on every
  attack decision and `combat.py:160-161` rolls 2d6 (§3.8's v1.3 footnote). Two seeds differing
  proves nothing unless the ambient noise is held constant. So:
  - **Arm A — control.** Two runs at the same `SOVEREIGN_SEED` *and* the same ambient constant K
    produce a byte-identical trace. **If Arm A is red, nothing else in the sweep means anything.**
  - **Arm B — the variance pin.** Different `SOVEREIGN_SEED`, same K. Must differ in turn-0
    dispositions and in at least one of {AI-initiated war count, the turns wars begin, which courts
    reach `fight`}. Holding K is what makes the difference *attributable to the seed* rather than to
    combat noise.
  - **Arm C — acceptance.** N runs (start at 10) with **both** the seed and the ambient RNG varying,
    because that is the distribution production actually produces. Freezing K here would reproduce §9
    row 13's own error on a different axis.
  - **Arm (b) — a scripted France**, one run per seed on a fixed subset (precedent: Sweep 5's "exit
    scenarios scripted"). Exercise each D5 instrument once, renege on one compensation, outbid
    Britain for one subsidy client, close the ports under the Continental System, and offer a courted
    settlement to a beaten great power. Several §7a scenes and §4.6a beats are unreachable by a
    passive France *by construction*, and "the harness had no player" is not a blocking predicate.
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
  - **The beats fired and were not collapsed** (§4.6a): each of the seven beats reachable, and a pin
    that a beat is never swallowed by the §4.6 line cap. *(v1.3 arm map: beats 1, 3 and 6 → arm (a);
    beat 4, "entirely the player's own doing", and beat 2's honest-gated defuse list → arm (b); beat
    5 → either. v1.4: beat 7 → either — arm (b) scripts an instrument-caused defusal, arm (a) may
    produce an opportunism-decay one.)*
  - **The throttle did not eat the phase** (§4.2c): no AI-initiated war may begin while either
    belligerent's courting offer to France was throttle-deferred, and the boot 1805 world can deliver
    a full turn's intent-ask budget in one turn.
  - **The mirror moves upward too** (§3.5): arm (b) asserts that a France which conquers, refuses
    asks or breaks a bargain **rises** on the perceived ladder. The downward-drift assertion is arm
    (a)'s, where a passive France is the ideal test case — but only the upward half makes the mirror
    a surprise engine rather than a decay counter.
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
   authored bands, and the **six** hard conditions true on every seed. The original intent of this pin —
   "the engine must not grow an appetite the scenario did not author" — is strengthened by D7, because
   the appetite now has to be written down in the scenario file to exist at all.)*
2. **M1–M7 byte-identical** (`tests/test_combat_sweep_metrics.py`).
3. **The player is never a spectator.** AI-vs-AI war must not resolve the campaign around France; the
   D1 cap, the D2 elimination floor and the fore-warning surface are the guards.
4. **No unexplained war, and no unannounced conquest.** A declaration without a reason the player can
   read is a failing test, not a rough edge — and *(v1.3)* every province that changes hands between
   two nations does so inside a war the ledger can name. The second clause exists because the
   `OPEN_MOVEMENT_STATES` path (§0.1 Correction A, §4.3a) lets an AI march in and capture with no
   declaration at all.
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
    behaviour under threat still reflects its profile (Austria still seeks a partner before fighting
    alone), and the homogeneity guard (AI-V) holds in wartime, not only at peace. *(v1.3 narrows the
    Britain clause: with no hostile army on British home soil, Britain answers coercion with subsidy
    rather than a levy; **with** one, it is permitted to concede on the ordinary settlement path, and
    this pin asserts only that it never spontaneously adopts Austria's coalition-building profile.
    London is land-reachable — §3.4 — so a pin that forbade Britain ever to fold would forbid a
    reachable and correct game state.)*
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
    inside their authored bands, a value with no authored band never varies, and the **six** hard
    conditions hold, including that the boot war set and alliance map are byte-identical on every
    seed; **(c)** *(v1.3 — narrowed, because the v1.2 wording promised something no campaign seed can
    deliver)* **the campaign seed round-trips**: `from_dict` restores the exact seed value `to_dict`
    wrote, never a freshly generated one, and every seeded quantity — the Tier-2 opening values, the
    §3.8 jitter on `weight` / opportunism / dwell / cooldowns, and every seeded tie-break —
    recomputes identically after a load, asserted with the module RNG pinned in the
    `tests/test_combat_sweep_metrics.py:36-39` idiom. **Campaign-level replay determinism is
    explicitly NOT claimed:** combat dice (`combat.py:160-161, :1088`), enemy-marshal mood
    (`enemy_ai.py:428`), vassal defection (`vassal.py:960/2091`) and jealousy (`jealousy.py:1135`)
    draw from the unseeded global `random`, whose state is not serialized and will not be — threading
    a campaign RNG into those 84 call sites would be a 19-module refactor, would rewrite the module
    seeds in 21 test files, and would break pin 2.
15. **No undeclared conquest** *(v1.3, §4.3a).* An AI capture of a province belonging to a nation it
    is not at war with, without a preceding successful `declare_war`, is a failing test — asserted
    directly against the `can_enter_territory` branch at `combat_executor.py:3523-3535`, which today
    skips the declaration under every `OPEN_MOVEMENT_STATES` treaty. And a **refused** declaration —
    armistice cooldown, unavailable objective, or co-belligerent side conflict — leaves
    `region.controller`, marshal locations and strengths byte-identical, creates no `war_instance`,
    and emits no conquest event. The intent layer never fore-warns a crisis whose declaration
    predicate is already refused.
16. **Threat is not a one-way ratchet, in either direction** *(v1.3, §4.4a steps 5–6).* **(a)**
    France's `threat_level` and decay series over a boot world + 40-turn run are byte-identical before
    and after **both** the store migration and the producer migration. **(b)** A non-player
    `threat_by_target` slot whose sources stop returns to 0 on the same schedule France's does.
    **(c)** No target's slot reaches `THREAT_INSTANT_MIN` (80) without at least one turn in the
    brewing tier, so §4.6's "fore-warning before war, always" holds for non-player targets too.
    **(d)** A scripted fixture in which a non-player power's hegemony share exceeds France's and it
    wins battles and takes a capital drives `threat_by_target[that power]` through the brewing
    threshold and forms a coalition against it, while France's own slot is unmoved — D3's "the player
    can genuinely be eclipsed" made into a test rather than a sentence.
17. **War exhaustion is belligerent-relative** *(v1.3, §4.2b, AI-4c).* **(a)** A 20-turn AI-vs-AI war
    with no French participation produces a monotonically non-decreasing exhaustion series for both
    belligerents. *(This is the pin that fails against master today.)* **(b)** France's own series is
    byte-identical after the generalisation, and every nation's exhaustion and treasury series at the
    authored boot is measured and reported in the §5.5 shape — the four boot third-party belligerents
    begin accruing at turn 1, which moves `calculate_war_effort_cost` (`world_state.py:3916`), and
    those deltas are blessed explicitly at the D6 re-check. **(c)** The legacy / bare fixture world is
    untouched: the Europe scoping is carried verbatim.
18. **Intent is deckless-neutral** *(v1.3).* `get_nation_intent` returns the ladder's bottom rung
    `indifferent` for any nation with no live agenda — which in the bare `SOVEREIGN_SCENARIO=none`
    world (where the whole suite runs, `conftest.py:73-85`) and under `SOVEREIGN_MAP=legacy` is
    **every** nation, since `world.agendas` defaults to `{}` (`world_state.py:316`). At `indifferent`
    the §4.2 rung rework falls through to today's behaviour **byte-identically**: P3's
    `threat_level > 60` shelter ask (`ai_diplomacy.py:1028`), P4's `relation > 30` upgrade (`:1045`)
    and P7's opportunism (`:1057`) all still fire on a deckless court exactly as they do now. Pinned
    on the bare world, in the `test_nation_agendas.py::test_deckless_world_is_byte_identical` idiom.
    This is the N1 rule applied to intent.
19. **Descent is reachable** *(v1.3, §3.1a).* **(a)** A design that satisfies drops its holder's rung
    within one turn, with no latch anywhere in intent. **(b)** A nation whose war exhaustion crosses
    the `effective_p1_threshold` seam sues for peace on the AI-vs-AI path, not only against France.
    **(c)** An AI-vs-AI war can be ratified to PEACE with the player's mounted dialogue untouched. If
    (b) or (c) is red, AI-3 is a one-way ratchet regardless of what the war counts say.
20. **The phase is visible in the running game** *(v1.3, §4.6b).* After any `.gd`-touching row the
    engine boots with 0 `SCRIPT ERROR` and the parse harness exits 0 — the standing XR-1 rule — and a
    live in-game verification confirms that the AI-1 intent row, the §3.5 mirror row, the §3.7
    subsidy row and each §4.6a beat render through their named transports. **A beat that exists only
    in a JSON response is exactly the failure §4.6a exists to prevent.**
21. **Every foregrounded crisis ends on screen** *(v1.4, §12.1)*. A crisis that was foregrounded
    (beat 2) resolves as exactly one of two beats: the fore-warned war, or **The Crisis Passes**
    (beat 7) naming its cause — the D5 instrument that bought it off or deterred it, the §3.2
    opportunism that decayed, the design that satisfied. A foregrounded crisis that silently stops
    being mentioned is a failing test. Non-foregrounded ladder coolings stay quiet — this pin adds
    no lines to the §4.6 budget and does not touch pin 13.
22. **Deck depth never moves the boot** *(v1.4, §12.2)*. `gulf_and_straits` — and any later authored
    second design — is **inactive at boot on every seed**: Russia's deck carries no order band, so
    `arbiter_of_europe` leads it on all seeds, and no nation's turn-0 active design differs from
    today's on the `historical` seed. Asserted beside pin 1's boot bytes. (Austria's pair is the one
    deck the order band may reorder, deliberately — §12.2.)
23. **A licence is a bond** *(v1.4, §12.3)*. A directed sponsorship at `amount_per_turn: 0` creates
    the same §3.3 standing expectation as a paid one. The licensor entering the licensed war against
    its recipient — or guaranteeing its target — is *reneging*, with the same highest-weight casus
    belli, in both directions: either side of the board may hold either end of a licence.
24. **The seal is symmetric and never deletes a consequence** *(v1.4, §12.4)*. Any party's sealed
    article — including France's — is discoverable by the same routes at the same price; discovery
    fires the deferred third-party reaction **in full** (masking defers reads at the intent/threat
    derivation chokepoint; it never reduces them); and no *disposition* is sealable by anyone —
    pin 11's boundary holds against the player too.

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
minor**. A **great power's last capital cannot fall to an AI-initiated war** — that war routes to a
forced settlement instead.

*(v1.3 keys the terms to one source, a clarification of D2's vocabulary and not a reopening of its
decision: **great power = `NATION_POWER_TIERS[nation] == "major"`** — France, Britain, Russia, Austria,
Prussia. The v1.0 gloss "no authored deck, not a great power" does not survive contact with the
roster: Spain is a `secondary` court that boots at war holding Madrid and has no deck, while Sweden,
Holland, the Kingdom of Italy, Sardinia and Denmark all hold decks and are `minor`/`secondary`. Deck
possession is not the tier.)* This is the historically true
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

### D6 — Sequencing: **BD → AI-0b/0c → AI-1 → AI-2 → re-check → AI-3 → AI-4 → AI-5/6 → AI-V.**

*(Header updated by D7, then by v1.3, then by v1.4. The AI-0 front block: **AI-0b** the
campaign seed and **AI-0c** the historical bands (§3.8, D7), joined in v1.4 by **AI-0d** the second
design (§12.2, pure authoring beside AI-0c). The first two are prerequisites rather than
features — each one, landed late, invalidates pins written before it. **AI-0 (the agenda-cache fix) is
deleted:** §0.1 Correction D is withdrawn, the defect does not exist, and its one real residual is a
sentence inside AI-1. Stage names per §11: BD → A → B → C → re-check → D → E/F → G.)*

Battle Diorama (ROADMAP row BD) keeps its place first: it is contained, visual, already scoped, and
a deliberate palate cleanser between two large systems arcs.

Then **AI-1 + AI-2 + D5 ship as one playable increment** — a Europe that visibly wants things and can
be bargained with, with zero new wars. **Then a short re-check with the user before AI-3**, because
AI-3 is the only slice that can change the shape of the campaign, and because AI-1/AI-2 will have
produced the first real evidence about how much motion the world actually wants (D1's cap is the
thing most likely to need adjusting, and it will be adjustable from data instead of from argument).
*(v1.3: **the re-check carries a written cut list** — see §9a. A cut made at the re-check with its
consequence written down is a decision; a cut discovered at AI-V is a failure.)*

AI-4's §4.4a migration may begin in parallel with AI-2 — it is a no-behaviour-change refactor with
its own byte-identical pin, and it is the phase's long pole. *(v1.3: **AI-2a**, the diplomacy-path
convergence, is the same shape — a no-behaviour-change refactor with its own byte-identical pin — and
may begin in parallel with AI-1.)*

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
ladder readiness, small grudges drawn from real ones, the minors' lean, Britain's first client.
**The historian test in §3.8.1 is the hard pin and is the single normative statement of it** —
*(v1.3: this paragraph previously restated the test in three clauses and silently dropped two, so the
gate record and the falsifiable pin disagreed. §3.8.1 now carries all six clauses, corrected; D7
points at it rather than paraphrasing it.)*

**`SOVEREIGN_SEED` unset or `=historical` reproduces today's boot byte-for-byte**, pinned suite-wide
in `conftest` like `SOVEREIGN_SCENARIO=none`. So §5 pin 1 is **narrowed rather than deleted**, and the
existing suite, the E1 economic band, M1–M7 and the §4.4a threat series keep their numbers unedited.
*(v1.3: the seed's default lives in `WorldState.__init__`, not in `main.py`'s scenario-path selector —
75 test call sites bypass `main.py` entirely, including the M7 world. See §3.8.1's migration
paragraph; getting this backwards reds pin 2 on day one.)*

*Consequence for the build:* **AI-0b (seed) and AI-0c (historical bands) land at the front**, with
AI-1. A seed retrofitted after the pins are written is paid for twice. `threat_level`'s band is a
blessed number tunable in-band; **widening the envelope — adding a new Tier-2 dimension — escalates.**

---

## 7. Definition of done

- Every nation has a readable intent; the player can name what any court wants and what it will pay.
- Idle courts are visibly active in peacetime through existing diplomatic verbs.
- A nation can go to war for a stated reason, having first tried cheaper instruments, with the player
  fore-warned — through the existing `combat_executor.py:3482` declaration seam, with **no new
  PEACE→WAR edge in the codebase**.
- The player can buy off, aim, or deter a design (D5), and can be offered the same.
- Wars can happen, **and end**, between powers that are not France — *(v1.3)* and the ending is
  reachable by the intended route: in the sweep, at least one AI-vs-AI war ends by **settlement or by
  exhaustion-driven peace**, not only by armistice expiry.
- **Somebody bleeds and Europe notices** *(v1.3)*. At least one AI-vs-AI war runs ≥5 turns with
  France neutral, and **both** belligerents' exhaustion rises monotonically over it — the falsifiable
  form of §1's "watch two rivals exhaust themselves while France rearms," which today is a number
  that falls.
- **The majors feel like distinct statesmen (§3.4).** The player can name each major power's *style*
  from the ledger and Talleyrand — not just its target — and over a run each behaves in character:
  Austria the patient coalition-builder, Prussia the bandwagoner who reneges, Russia the distant
  arbiter, Britain the paymaster who never marches. The AI-V homogeneity guard and in-character
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
  11–12): a sealed article that was discoverable, an emergent design, or a volte-face. *(v1.3 makes
  this measurable rather than asserted:* **an emergent design is promoted at least once on every
  sweep seed where a promoting event occurred** — partition, capital loss, punitive settlement, or a
  broken §3.3 bargain — *and the promoting event is named in the campaign log; on seeds where no
  promoting event occurred, a scripted reachability test asserts promotion fires from a constructed
  record. Deliberately not an unconditional "≥6 of 10": three of the four triggers are player-driven
  or D2-blocked, so a flat threshold would fail for reasons unrelated to the mechanic. If AI-3b or
  AI-5b(ii) slip, they fail here carrying the same written blocking predicate they carry in §7a.)*
- **Deterrence is visible** *(v1.4, pin 21)*. Across the sweep, at least one foregrounded crisis
  ends in **The Crisis Passes** with its cause named — arm (b) scripts one via a D5 instrument — and
  no foregrounded crisis evaporates silently on any seed. The instruments must be seen to *work*,
  not only to exist.
- **Two campaigns are not the same campaign** (§3.8, D7). Across the N-seed acceptance sweep, the
  opening dispositions, war counts, the turns wars begin and which courts reach `fight` all vary —
  measured on **Arm B, with the ambient RNG held constant**, so the difference is attributable to the
  seed rather than to combat noise *(v1.3)* — while the **§3.8.1 historian test passes on every
  seed**, the `historical` seed reproduces today's boot byte-for-byte, and a save/load **restores the
  campaign's own seed, so its seeded dispositions and timings continue unchanged.**
- **Every seed is a 1805 a historian would recognise** (§3.8.1). Tier-1 fixed on all seeds, Tier-2
  inside authored bands, and no dimension varies that a designer did not write a band for.
- **Turn 40 still rhymes** (§3.9) *(v1.3)*. Across the sweep the four historical shapes are each
  reachable: a coalition forms against the strongest power; a bought-off design becomes a hostage; a
  paymaster funds a war it never joins; a beaten power is either humiliated into revanche or courted
  into partnership. **Which nations play the parts may differ by seed — that is the variability, not
  a failure.**
- **The phase is visible in the running game** (§4.6b, pin 20) *(v1.3)*. No AI-* slice is "landed" on
  green backend tests alone if its Landing column names a ledger row, a display or a beat; the engine
  boots with 0 `SCRIPT ERROR` and the parse harness exits 0 after every `.gd`-touching row.
- The 1805 opening is byte-identical, M1–M7 unmoved, and the pre/post anti-France threat series
  measured and reported (§5.5).
- Scored creative pass recorded in `docs/audits/`.

### 7a — The seven scenes (historical acceptance)

The DoD above is measured in counts. This is measured in *recognition*: can the engine **produce**
the decade's characteristic political events — not script them, not fake them, but reach them from
authored 1805 by the machinery in §3? A phase that hits every number and cannot produce any of these
has built a simulation of statecraft without its texture.

| # | Scene | The mechanic that reaches it | Arm |
|---|---|---|---|
| 1 | **The Confederation of the Rhine** — a cluster of minors bandwagons to the hegemon | `bandwagon` (§3.1) + the vassalage on-ramp (§4.5), timing per §3.4's minors paragraph | either — but note that with a passive France the hegemony share may never reach the P-Bandwagon gate (`ai_diplomacy.py:1094`) |
| 2 | **Schönbrunn** — a design bought off with compensation elsewhere | D5 instrument 1, creating a standing expectation (§3.3) | either (D5 works AI↔AI) |
| 3 | **Jena** — that bargain broken, and the war that follows says so | §3.3 reneged compensation as the highest-weight casus belli, carried as the war's stated reason | either |
| 4 | **Tilsit** — a beaten enemy reverses and is aimed at a third party | the volte-face (§3.6) + the `sponsor` branch (AI-2b's directed record) + **the §12.2 second design as the aim's object** — a reversed Russia advances to *The Gulf and the Straits* | either — §3.6 calls it "a *player-caused* surprise" |
| 5 | **Pitt's subsidy** — a war funded by a power that never marches, and France bidding for the recipient | the subsidy contest (§3.7) + AI-2b's directed record | **(b)** |
| 6 | **The Continental System bites** — the gold stops because the trade was cut | the existing Continental System reaching Britain's purse (§3.4) | **(b)** |
| 7 | **A partition** — two powers agree to carve a third, possibly in a sealed article, and it lands as a fait accompli | the sealed article (§3.6) + third-party settlement (§4.4) | (a) |

**Acceptance:** ≥5 of 7 demonstrably reachable, each miss carrying a written blocking predicate.
Scene 6 may legitimately be blocked on economic scale and scene 7 on the sealed-article slice
slipping — those are explanations; "it didn't come up" is not.

**v1.3 adds three things this list needed to be usable.**
**(1) The arm map above,** because §7a as written demanded scenes a passive France cannot produce —
scene 5 needs France to bid, scene 6 needs France to close the ports — and the AI-V harness has no
player. The ≥5-of-7 threshold is evaluated over the **union of both arms**; otherwise §7a's own
pre-excusing of 6 and 7, plus §8's pre-authorised failure of 4 and 7, leaves the threshold
unreachable before a line is written.
**(2) The verb, defined:** *reachable = observed at least once across the sweep, in the arm it is
mapped to. A scene not observed fails unless a named predicate blocked it, and "the harness had no
player" is not a predicate.*
**(3) The §3.9 casting rule:** *a scene counts when its mechanic produced its shape, regardless of
which nations played the parts.* Scene 3 does not require Prussia specifically — it requires that a
bargain was broken and that the war which followed said so.

---

## 8. Owner rows (GR9)

*(v1.3: **row AI-0 is DELETED** — §0.1 Correction D is withdrawn, the defect does not exist, and both
of its proposed pins already exist in `test_nation_agendas.py`. Rows amended by v1.3 are marked.)*

| Row | Owner | Landing | Tracking |
|---|---|---|---|
| AI-1 Intent layer *(amended)* | §4.1 | `intent.py` + `build_intent_payload` + **the `diplomatic_ledger.gd:380-397` render**; intent cache hung on `invalidate_bloc_members_cache`; the relation/force/treasury staleness question decided and pinned. **Touches `.gd` → boot the engine, grep `SCRIPT ERROR`** | STATUS + `test_ai_intent_layer.py` |
| AI-2 Peacetime pursuit | §4.2 | `ai_diplomacy` rung rework, within the §4.2c delivery budget | `test_ai_intent_peacetime.py` |
| AI-2b Counter-instruments (D5) *(amended)* | §6 D5, §3.3 | compensation / **directed sponsorship record** `{payer, recipient, aim, amount_per_turn, started_turn, expiry}` on the existing `gold_per_turn` treaty or `recurring_settlement_payments` seam — the only genuinely new field is `aim` / guarantee **with its abandonment grievance** (`_add_grievance_flag`, `diplomacy.py:450`, `grievance_type="guarantee_abandoned"` — today `protection_promised` is a pure +5 acceptance sweetener with **zero** enforcement); wizard + settlement seams; both directions | `test_ai_intent_counterplay.py` |
| AI-2c Great-power statecraft (§3.4) *(amended)* | §3.4 aliveness contract | per-nation `statecraft` weighting over the ladder/instrument choice (generalises `NATION_DESIRE_PROFILES`); authored for the majors, light for secondaries; **Britain's coercion answer derived from hostile-army-on-home-soil, never hard-coded** | `test_ai_intent_aliveness.py` (in-character + homogeneity guard) |
| AI-3 Decision for war *(amended)* | §4.3, §4.3a | war-intent marker + widened targeting + **explicit `declare_war` at the announcement seam** + the treaty-break ladder step + the co-belligerent side-exit (shared VS-6 helper) + the refused-declaration abort at both seams + `war_objective` enum mapping with `conquest` fallback | `test_ai_intent_war_decision.py` |
| AI-4a Threat migration *(amended)* | §4.4a | `threat_by_target` + `threat_level` property, byte-identical — **including steps 5 (producer migration) and 6 (decay + threshold reader)** | `test_ai_intent_threat_migration.py` |
| AI-4b De-France-centering *(amended)* | §4.4, §4.4b | **coalition de-anchoring (§4.4b — the second long pole)** + third-party settlement: AI term generator, AI acceptor, headless ratify wrapper, `unauthorized_actor` gate replaced. **Core, not slippable** — the armistice stopgap does not cover a pair below −60 relation | `test_ai_intent_third_party.py` |
| AI-5 System wiring | §4.5 | per-system wires (formations, vassals, econ/sponsor, jealousy proxy, NA-5, recruitment) | `test_ai_intent_system_wiring.py` |
| AI-6 Legibility | §4.6 | ledger/dispatch/Talleyrand + the 2-line narration cap | `test_ai_intent_legibility.py` |
| AI-V Assurance *(amended)* | AI-V §4 | both-sides pins + the three-arm N-seed acceptance sweep + the scripted-France arm | `test_ai_intent_assurance.py` |
| Economy re-measure | audit §5 | re-measure from an actively-spending run before tuning | carried here so it is not lost |

### v1.2 rows (the gameflow pass)

| Row | Owner | Landing | Tracking |
|---|---|---|---|
| **AI-0b Campaign seed** *(amended)* | §3.8 | serialized world seed set in **`WorldState.__init__` from `SOVEREIGN_SEED`** (the in-model `SMOKE_START_ENV` idiom) + a `from_scenario(seed=…)` override + threshold jitter + tie-breaks; `main.py` reports it in the boot banner and documents it *alongside* the precedence chain, not as a rung in it; **must land with AI-1** or every pin written against the deterministic trace is revisited | `test_ai_intent_variance.py` |
| **AI-0c Historical bands (D7)** *(amended)* | §6 D7, §3.8.1 | authored per-dimension ranges in `europe_1805.json` + validator schema + `MODDING_FORMAT.md` row; the `historical` seed collapses every band to its centre; the seed shown in ledger + save; **every band pin constructs its world through `WorldState.from_scenario(path, seed=…)` directly, per the 75-caller idiom** | `test_ai_intent_historical_envelope.py` (the **six-clause** historian test) |
| **AI-1b The mirror** | §3.5 | France's own ledger row = Europe's derived reading of France; restraint drifts it down | folded into `test_ai_intent_layer.py` |
| **AI-2d Participation surface** *(amended)* | §4.2b | sell-neutrality (**creating a §3.3 expectation against the payer**) + sponsor arms with AI-2; join / broker with AI-3/AI-4 — **one row so neither half orphans**. *(The exhaustion display leaves this row for AI-4c — it is a system, not a display.)* | `test_ai_intent_participation.py` |
| **AI-2e Subsidy contest** *(amended)* | §3.7 | subsidy recipient + amount made visible; remove-a-client; **the outbid arm depends on AI-2b's directed record and lands with it** — `get_british_subsidy_recipient` compares relations among coalition members and cannot see a French offer | folded into `test_ai_intent_counterplay.py` |
| **AI-3b Sealed articles** | §3.6, §5 pin 12 | AI↔AI bargains whose *fact* is public and *article* may be sealed, each with ≥1 discovery route | `test_ai_intent_sealed_articles.py` |
| **AI-5b(i) Emergent designs** *(split, Core)* | §3.6 | grievance→design promotion (max 1/nation) from **derived homeland loss** + a durable `settlement_memories` `punitive_settlement` record + §3.3 broken bargains; an `acquire_regions` entry, **front-inserted**, **activating when the survival override clears**; `get_agenda_grudge_nations` generalised off `world.player_nation` to a `(victim, author)` query | `test_ai_intent_emergent_designs.py` |
| **AI-5b(ii) The volte-face** *(split, may slip; amended v1.4)* | §3.6 | the courted-loser reversal through the settlement layer + the `sponsor` branch; **the reversal retires/suspends the reversed power's `contain_hegemon` design so its deck advances to the next design** (§12.2 authors Russia's). **If it slips, §4.6a beat 5 and §7a scene 4 carry the written blocking predicate** and the AI-V beats assertion amends seven → six | folded into `test_ai_intent_emergent_designs.py` |
| **AI-6b The beats + tempo** *(amended v1.4)* | §4.6a | **seven** named beats on existing transports (v1.4 adds beat 7, The Crisis Passes — pin 21); one foregrounded crisis world-wide; cap governs routine lines only; relevance-weighted line selection | folded into `test_ai_intent_legibility.py` |

### v1.3 rows (the verification pass)

| Row | Owner | Landing | Tracking |
|---|---|---|---|
| **AI-2a Diplomacy-path convergence** | §4.2 (the six seams) | recipient-explicit proposal envelope (`_build_proposal_terms`, `_make_proposal`, `deliver_ai_proposal`); **the AI-AI refusal record + its public event**, without which AI-3's ladder gate is unsatisfiable; cooldown re-key to an ordered `(proposer, recipient)` with `from_dict` migration; `ai_stalemate_counters` recipient-scoped; the counter-offer arm decided in writing. **No behaviour change — the byte-identical player-flow pin is green first.** May run parallel with AI-1 | `test_ai_intent_peacetime_convergence.py` |
| **AI-4c War-exhaustion generalisation** | §4.2b, §4.4, §3.1a | per-turn tick re-keyed to `get_nations_at_war_with(nation)`; an explicit third-party battle arm in **both** combat copies; Europe scoping carried; per-war ledger display. **Balance-touching** — every AI nation gains a non-zero `calculate_war_effort_cost`, blessed at the D6 re-check; the §8 economy re-measure covers it. **Must not be cut** (§9a) | `test_ai_intent_third_party.py` |
| **AI-6c Client surfaces** | §4.6b | `diplomatic_ledger.gd` (intent + mirror + subsidy + third-party exhaustion), `war_status_panel.gd` / `war_detail_popup.gd`, `mailbox_panel.gd`, `dispatch_view.gd`, `main.gd` dtype whitelist, `cooldown_manager.py PRIORITY_ORDER` + `dialog_manager.register()` for any new popup, and the §4.2b courting surface. **Owns only what no earlier row claimed** — every row naming a display lands its own render. Boot the engine, grep `SCRIPT ERROR` | `test_ai_intent_legibility.py` + boot smoke |
| **§4.4b Coalition de-anchoring** | §4.4b | folded into AI-4b as its second long pole; listed here so the price is not lost again | `test_ai_intent_third_party.py` |

### v1.4 rows (the creative pass)

| Row | Owner | Landing | Tracking |
|---|---|---|---|
| **AI-0d The second design** *(Core, authoring — lands with AI-0c)* | §12.2 | Russia's `gulf_and_straits` (`acquire_regions`, `["Finland", "Rumelia"]`) authored **behind** `arbiter_of_europe` in `europe_1805.json`; no order band for Russia (pin 22); AI-0c authors its deck-order band over **Austria's** existing pair instead — the band's first real subject; validator already validates decks | pin 22, folded into `test_ai_intent_historical_envelope.py` |
| **AI-5c The Arbiter's Offer** *(may slip — §11 cut list #2)* | §12.5 | armed mediation: a non-belligerent major with a live contain/arbiter design offers to mediate a French war above an exhaustion floor — suggested terms through the existing incoming-settlement machinery, mediator credited on accept; refusal consequence **derived only** (mediator weight + relations; no new threat namespace, no auto-join); AI-vs-AI mediation deferred to the exit review | `test_ai_intent_mediation.py` |
| *Folds (no new rows):* | | 12.1 the deterrence receipt → **AI-6b** (beat 7, pin 21) · 12.3 the licence → **AI-2b** (amount-0 arm, pin 23) · 12.4 the purchased dispatch + player seal → **AI-3b** (its principle-7 half, pin 24) · 12.6 the allegiance auction → **AI-2d** (Stage C half) | |

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
- **Cheap and high-yield — take them where they sit:** **AI-1b** (one derived row) and the visibility
  and remove-a-client halves of **AI-2e**. *(v1.3 strikes "a comparison in an existing function plus a
  display": the **outbid** half is not cheap and depends on AI-2b's directed record.)*
- **At most ONE of AI-3b / AI-5b(ii) may slip, with a named landing. Both cannot** *(v1.3)*. §7's DoD
  surprise line has exactly three satisfiers — a discoverable sealed article, an emergent design, a
  volte-face — which are precisely these rows' payloads, so both slipping makes a mandatory DoD line
  unsatisfiable while §7a still passes at its ≥5-of-7 floor. **AI-5b therefore splits: (i) emergent
  designs is Core; (ii) the volte-face may slip.** Emergent designs is kept because it writes into
  `world.agendas` — an already-serialized per-nation deck store consumed unchanged by NA-1/2/3/6 —
  and because per §3.6 it is what makes the separate DoD number "≥1 agenda shift" a system rather
  than a deck-order tick. **AI-3b** sealed articles remains the first cut: it is the only item in the
  phase with genuinely new machinery and no existing seam. Whichever slips lands in the phase's own
  exit review rather than becoming a vague "later", and its §7a scene fails carrying that as its
  written blocking predicate — the honest outcome, not a hidden one. *(v1.4's additions keep the
  same discipline: AI-0d is Core-and-cheap authoring beside AI-0c; the three folds ride their host
  rows' dispositions — 12.4 goes wherever AI-3b goes; AI-5c may slip, §11 cut list #2.)*

**Not in this phase, deliberately:** narrative/LLM-voiced diplomacy beyond existing register banks
(GR6); a new war-goal system beyond reusing `war_objective` — *(v1.3: adding a `design` /
`grievance` key to the existing `create_war_objective` record, `diplomacy.py:3199-3220`, counts as
reuse; minting a new objective enum member would not)*; any rebalance of the anti-France
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
and the pass produced no argument against any of them. §0.1's four corrections *(three after v1.3
withdrew Correction D — see §10)* and the §4.4a migration contract are untouched. §3.4's statecraft table is extended only by the minors paragraph.
The sequencing in D6 stands, with the v1.2 rows slotted into the slices they belong to rather than
appended as a tail — the phase does not grow a new stage, it grows in place.

---

## 9a. v1.3 verification-pass record — what the fresh read changed, and what it cost

The pass asked the three questions of the brief — **does this assure historic outcomes, produce
variability and surprise, and run on dynamic conditions depending on what happens?** — with ten
ground-truth readers checking every `file:line` claim against master, ten design lenses, and two
adversarial refuters on every finding.

**The headline is uncomfortable and worth stating plainly: the spec's design spine is the best in this
project's history and its factual layer was unreliable.** The price ladder, GR5 reuse of the existing
declare seam, the additive threat migration and D7's "bounds are authored content, not a formula" all
survived every lens. But a **prerequisite slice fixed a bug that does not exist**; the phase's **one
falsifiable historical pin contained a clause false on the shipped scenario**; and a surface priced at
"a display wire, not a system" turned out to be a system that *decays* for exactly the wars this phase
exists to create. Nineteen corrections are tabled in §10. The lesson for the next spec: a claim of the
form *"X already exists, so this is cheap"* is the highest-risk sentence a design document can
contain, and every one of them should be read as a checkable assertion rather than as context.

**Against the brief, three structural gaps, each now closed:**

| # | Finding | Disposition |
|---|---|---|
| 1 | **The ladder only ever climbed.** A want could rise and never cool; a war could start and never end. Worse than an omission — the three seams that lower it are *dead in code* for the AI-vs-AI case, so §4.4's own named worst outcome ("AI-3 is a one-way ratchet") was live rather than hypothetical | **§3.1a** the descent; **AI-4c**; §5 pin 19; the DoD's "somebody bleeds and Europe notices" |
| 2 | **Turn 0 was falsifiable and turn 40 was not.** The historian test pins the opening; §3.8 promises the mid-game forks entirely; §7a asks for seven historical scenes — and nothing explained why a forked campaign should still rhyme. The tension between *assured outcomes* and *variability* is the brief's actual question and the spec never named it | **§3.9** the historical attractors — *assure the shapes, vary the casting*; the §7a casting rule; the DoD's "turn 40 still rhymes" |
| 3 | **Reactivity was a list of special cases, not a principle.** Four separate findings were instances of one shape: the world does not notice that something happened | **§2 principle 9** with its four-row obligation table, each row already owned |
| 4 | **The phase had no Godot work at all** — zero mentions in 1,185 lines — in a spec whose principle 4 says legibility is the feature. `diplomatic_ledger.gd` reads the agenda payload key by hand, so §4.1's new sibling key would have rendered nothing | **§4.6b** the client surfaces; **AI-6c**; §5 pin 20; the per-row ownership rule |
| 5 | Four contracts were asserted in a sentence each and priced accordingly | **§4.3a** declaration, **§4.4a steps 5–6** producers, **§4.4b** coalition, **§4.2c** delivery |
| 6 | The variance pin could not be evaluated: a 40-turn run is already nondeterministic without any seed | AI-V's **three arms** (control / variance / acceptance) + the scripted-France arm |
| 7 | §7a demanded scenes a passive France cannot produce, with a harness that has no player | §7a's **arm map** and the defined verb |

**Scope honesty (GR9).** These edits **remove** one phantom slice (AI-0) and **add** roughly 2.5
slices of genuinely new work — AI-4c (~0.75), AI-6c (~1.5), §4.3a's declaration contract (~0.5 inside
AI-3). They also make visible about **3.5 slices of work the phase always contained but had priced at
zero**: AI-2a's convergence (~1.5, which §4.2 already called "the slice's real bulk" in prose),
§4.4b's coalition de-anchoring (~1, priced as one parameter change against nine bindings), AI-5b(i)'s
grievance substrate (~0.5, assumed to exist), and AI-2b's directed sponsorship record (~0.5, priced
on a function that cannot express it). **Six of those seven rows are corrections to the price, not
additions to the scope — the phase was always this big.**

**The cut list, written before the pressure exists.** *(v1.4: the **living** cut list now sits in
§11's re-check block, with AI-5c slotted in; this copy stays as the v1.3 record.)* D6's pre-AI-3
re-check carries it, in priority order; each entry names what it takes with it:

1. **AI-3b sealed articles** — the only item with genuinely new machinery and no existing seam. Takes
   §7a scene 7 and part of the DoD surprise line; §3.6's surprise budget is then carried by AI-5b(i),
   which is Core and cheap.
2. **AI-5b(ii) the volte-face** — takes §4.6a beat 5 and §7a scene 4, and amends AI-V's "six beats"
   to five.
3. **AI-2e's outbid arm** — takes §7a scene 5's France-bidding half; the visibility and
   remove-a-client halves stay.
4. **§3.5's upward mirror assertion** — takes an AI-V arm-(b) row, not a DoD line.

**And one thing that must not be cut to pay for anything: AI-4c.** It is small, it is the descent
half of the ladder, and without it AI-3 ships the one-way ratchet §4.4 already names as its own worst
outcome — with the additional cruelty that the ledger would display a *falling* number for two powers
grinding each other, which is worse than displaying nothing at all.

---

## 10. v1.3 correction table — factual claims that did not survive re-verification

Recorded rather than quietly edited, in the discipline §0.1 set. All ground truth re-verified against
master at `e7f92dd`. Every row changes the build, the price, or a pin.

| # | Section | What it said | Ground truth | Where it is fixed |
|---|---|---|---|---|
| 1 | §0.1 Correction D | `_agenda_cache` is never cleared; fixing it is prerequisite **AI-0** | False on all four sub-claims. `invalidate_bloc_members_cache`'s **last statement** (`world_state.py:1695`) is `self._agenda_cache = None`; `invalidate_active_nations_cache:1619` calls it; `capture_region` and `set_diplomatic_state` both reach it; there are **two** direct clears. Pinned twice in `test_nation_agendas.py` | §0.1 D **withdrawn**; row AI-0 **deleted**; D6 header |
| 2 | §4.1 prerequisite | "wire it into `invalidate_active_nations_cache`" | Doing so would **regress** the NA-0 fix — `set_diplomatic_state` reaches only the bloc seam | §4.1 cache-siting paragraph |
| 3 | §3.8.1 historian test | "· no minor boots at war" | False on the shipped scenario: Spain, Holland, Bavaria and KingdomOfItaly all boot at war, as they did in 1805. Contradicted Tier 1 four paragraphs above and would red on the `historical` seed | §3.8.1's **six** clauses; §5 pins 1, 14(b) |
| 4 | §6 D7 | restated the historian test, silently dropping two clauses | The authoritative gate record and the falsifiable pin disagreed | D7 points at §3.8.1 as the single normative statement |
| 5 | §3.8.1 Tier 2 | "Bavaria, Baden and Württemberg genuinely were up for grabs … the band that matters most" | Baden and Württemberg are **not nations** in `EUROPE_ROSTER`; Bavaria is Tier-1 committed by `starting_wars` *and* a France alliance. The band had no eligible subject | Tier-2 "minors' lean" row re-pointed |
| 6 | §4.2b | third-party war exhaustion is "a display wire, not a system" | Never accrues (every battle arm is France-conditioned) and **decays −5/turn** for any nation not at war with France. Four such wars exist at boot | §4.2b rewritten; **AI-4c**; §3.1a(c); §5 pin 17 |
| 7 | §4.4 | "generalising **three** France-literal systems" | Four — war exhaustion is the fourth | §4.4 |
| 8 | §4.4 | "`form_coalition` takes a target instead of binding `world.player_nation` (`coalition.py:1323`)" | Nine France-literal bindings, two singleton-keyed readers, and `active_coalition` is a singleton with 55 backend + 8 `.gd` refs. `coalition_leadership_score:950-951` carries its own docstring admission | **§4.4b** migration contract |
| 9 | §4.4a step 1 | migration scoped to an optional `target` on `add_threat` / `reduce_threat` | **Decay bypasses both** — `coalition.py:1793-1802` writes `threat_level` directly; two more direct writers exist. Decay is the only mechanism that lowers threat | §4.4a **step 6** |
| 10 | §4.4a closing | "Only once that is green does any producer start passing a real target" | One clause covering a second, larger migration. **Every** producer is player-keyed; without it `threat_by_target[X]` is permanently 0 and D3's eclipse clause is unreachable | §4.4a **step 5** + producer table |
| 11 | §4.3 | the war "carries its design as `war_objective`" | Impossible: `OFFENSIVE_OBJECTIVE_TYPES` is a three-member enum and `declare_war:7562` rejects anything else; `OBJECTIVE_TYPE_DISPLAY` would `.get(k,k)`-leak the raw key at four sites (R7) | §4.3 splits objective **type** from stated **reason** |
| 12 | §0.1 Correction A | "`combat_executor.py:3482` / `:3532` … live for any non-player attacker" | `:3532` declares **only** when `can_enter_territory` is False; under OPEN_BORDERS or NON_AGGRESSION an AI captures with **no war declared**. And `:3483`/`:3533` ignore a *failed* declaration and fight anyway | §0.1 A narrowed; **§4.3a**; §5 pins 4, 15 |
| 13 | §3.4 | Britain's core "sits behind the moat"; "a land threat cannot touch the core" | `europe.json` `sea_links` contains London ↔ Flanders, sea links fold into `adjacent`, and Flanders boots **French**. DEF-6 kept the crossing walkable deliberately, gated by the 25k garrison. §0 of this spec records Britain taking Flanders by land | §3.4 Britain row + paragraph, derived rule; §5 pin 10 |
| 14 | §3.8 / D7 | "the AI layer contains no randomness at all" | True of the three political modules, false of `enemy_ai.py` (3, incl. a mood roll on every attack decision) and 19 further backend modules (84 sites). No production seeding exists anywhere | §3.8 footnote; §5 pin 14(c); AI-V's three arms |
| 15 | §5 pin 14(c) | a save/load "reproduces the same subsequent 5 turns" | Unachievable — the ambient RNG is unseeded and unserialized. No campaign seed can deliver campaign replay | pin 14(c) narrowed to seed round-trip + seeded-quantity identity |
| 16 | §3.8.1 | `SOVEREIGN_SEED` "joins the boot-precedence chain in `main.py`" | `_resolve_scenario_path` returns a *path*; 75 `from_scenario` calls across 42 test files bypass `main.py`, including the M7 world | seed default lives in `WorldState.__init__`; AI-0b row |
| 17 | §3.7 / §3.1 / §4.5 / D5-2 | the `sponsor` branch "routes through the already-generalised `get_paymaster_nation`"; the outbid is "a comparison inside a function that already exists" | `get_paymaster_nation` is the coalition special case — one payer, from a deck entry, inside the single coalition, never the hegemon, so France can be neither payer nor recipient. `get_british_subsidy_recipient` cannot see a French offer | directed sponsorship record in **AI-2b**; §3.1, §3.7, §4.5, AI-2e all re-pointed |
| 18 | §3.6 | promotion "only from the serialized grievance record" | No such record exists for three of the four triggers; `betrayal_history["grievance_flags"]` projects four scalar keys and is clearable by Make Amends | §3.6's split substrate + three code-forced constraints; **AI-5b(i)** |
| 19 | §4.2 | intent asks arrive "visibly, **every turn**, in the mailbox" | `turn_manager.py:440-459` throttles the two relevant `decision_reason` labels to `MAX_BANDWAGON_PER_TURN = 2` world-wide with a silent `continue`, stacked on three more cooldowns | **§4.2c** the delivery contract |

**What the pass deliberately did *not* change**, so this review's own enthusiasm is on the record as
having been resisted: **§6 D1–D7 all stand** — findings that tried to reopen D1's cap, D3's gravity
condition, D4's no-fog, D2's routing and D7's Tier-1 fixing were all refuted, and D6's re-check
remains the sanctioned place to move D1's number *from data*. **The Hanover / Schönbrunn → Jena
worked example stands** (Hanover borders Berlin's own corps and fields zero marshals; `against` is
derived and retargets as control changes). **§3.8's core argument stands** — the seed is the right
fix, "the bars, not the choices" is the right scope, and the proposal to migrate 84 ambient `random.`
sites into a world-owned RNG was correctly rejected as a 19-module refactor that would break pin 2.
**§4.6's narration cap and §4.6a's tempo rule stand** — the answer to the throttle is a named budget,
never a removed throttle. **§2 principle 3 stands**; only its citation needed tightening.

---

## 11. The phased build plan *(v1.4 — the builder's front door)*

Everything in this section is **collated, not new**: D6 owns the order, §8 owns the rows, §5 the
pins, §7 + §7a the acceptance. It exists because a builder should not have to collate five sections
to answer *"what do I build next, and how do I know it landed?"* — which, after four review passes,
was the honest state of this document. On any conflict, **§6 and §8 win**.

**The shape of the phase in one paragraph.** Foundations first — the seed and the authored bounds,
because every pin written before them is written twice. Then the read-only layer *and its render*:
Europe shows its hand. Then the peacetime game: Europe talks, and France can answer. **Then the user
re-check — the phase's only remaining gate.** Only then the decision for war, packaged in one
indivisible stage with the machinery that lets other people's wars hurt and *end*. Then consequence
wiring, the presentation remainder, and a three-arm acceptance sweep against the seven scenes.

**What a turn feels like when this is done** — the vignette every stage below builds toward:

> Turn 14. The dispatch leads with the one foregrounded crisis: *"Berlin has moved to coercion —
> Prussia masses on Hanover's border."* Beneath it, one routine line: *Vienna seeks a Russian
> guarantee.* The ledger's designs tab shows Prussia at `coerce`, weight 74 and climbing — and, in
> France's own row, how Europe reads *you*: hegemon, 0.41 of the continent's weight, *keeps his
> bargains* (three seasons without a broken article). Talleyrand: *"Berlin can be bought, Sire — the
> Hanoverian design is exactly the kind gold satisfies. Austria cannot. If you mean to fight
> Prussia, do it before the British subsidy renews."* Four answers stand open: compensate Berlin
> (and hand her a hostage in the §3.3 sense — yours); guarantee Hanover (and stake your credibility
> on a test you may not want); aim Prussia at somebody else entirely; or let the war come, having
> been asked. The mailbox holds one more thing: St. Petersburg's envoy — beaten at Austerlitz,
> courted since — proposes partnership, *and asks what France would say to a Russian design on
> Finland.* You know what Tilsit cost the last man who signed one. You sign.

### 11.1 The stages

**Bold** rows are Core (§8's triage); *(slip N)* rows sit on the cut list below at that position.
BD (Battle Diorama, its own ROADMAP row) precedes Stage A per D6 — a deliberate palate cleanser.

| Stage | Rows | What the player has when it lands | Exit criteria |
|---|---|---|---|
| **A — The Dice and the Bounds** | **AI-0b** campaign seed · **AI-0c** historical bands · **AI-0d** the second design *(v1.4)* | Two campaigns stop being the same campaign; the seed shown in ledger + save, shareable | pins 14(a) + 22 green; the six-clause historian test harness exists; validator + `MODDING_FORMAT.md` rows; suite + M1–M7 byte-identical on `historical` |
| **B — Europe Shows Its Hand** | **AI-1** intent layer + its ledger render · **AI-1b** the mirror ∥ **AI-2a** diplomacy-path convergence (refactor) | The designs tab: every court's want, target and rung — and Europe's derived reading of France | boot intents pinned against authored 1805; renders live in-game (pin 20); AI-2a's byte-identical player-flow pin green |
| **C — The Bargaining Table** | **AI-2** intent-driven rungs · **AI-2b** D5 instruments + the licence *(v1.4)* · **AI-2c** statecraft · **AI-2d** sell-neutrality / sponsor arms + the allegiance auction *(v1.4)* · **AI-2e** subsidy visibility + remove-a-client · ∥ AI-4a steps 1–4 (refactor) | Europe talks: couriers with reasons, all three D5 instruments both directions, consent as a currency, Britain's purse visible, a minor's flip contested | pin 18 (deckless-neutral); the §4.2c delivery budget live; beats 1 + 4's envoy firing; pin 23; the re-check evidence pack assembled |
| ⛩ **THE RE-CHECK** — D6's only remaining gate | — | — | user decides from data: D1's cap number; the living cut list (§11.2); AI-4c's economy deltas blessed (pin 17b); AI-5c keep or slip |
| **D — War and Peace** *(indivisible — a war that can start must be able to end)* | **AI-3** the decision + §4.3a declaration contract · AI-4a steps 5–6 (producers + decay) · **AI-4b** third-party settlements + §4.4b coalition de-anchoring · **AI-4c** war-exhaustion generalisation · AI-2d join / broker arms · *AI-3b sealed articles + the purchased dispatch (slip 1)* | The first AI war: fore-warned, courted about, priced, endable — "let them bleed while France rearms" readable per war | pins 15 / 16 / 17 / 19 / 21 / 24; the DoD war lines (a war starts AND ends; exhaustion rises monotonically; France was courted); beats 2, 3, 6 and 7 firing. Internal order per D6 — AI-3 then AI-4 — but **nothing user-facing lands mid-stage**: harness-only until AI-4b/4c close the loop |
| **E — Consequence and Character** | **AI-5** system wires (formations · vassals · econ · jealousy proxy · NA-5 as the coerce rung · recruitment) · **AI-5b(i)** emergent designs · *AI-5b(ii) the volte-face (slip 3)* · *AI-5c the Arbiter's Offer (v1.4, slip 2)* | Grievances become designs; generosity has a payoff; the arbiter finally arbitrates | pin 19 + the emergent-design assertions; beat 5 fired or its written predicate |
| **F — The Stage** | **AI-6** cap + relevance weighting · **AI-6b** tempo + any beat no row claimed · **AI-6c** surface remainder | A dispatch that breathes: two routine lines, one foregrounded crisis, beats never buried | the narration pins (cap / exemption / never-collapsed); pin 20's live in-game pass |
| **G — The Reckoning** | **AI-V** three arms + the scripted-France arm | — | the full §7 DoD; §7a ≥5-of-7 across the arm union; the scored creative pass in `docs/audits/` |

### 11.2 Stage rules and the living cut list

**Rules, so the table cannot be gamed:**

- **Exactly two parallel tracks**, both v1.3-blessed no-behaviour-change refactors with their own
  byte-identical pins: AI-2a beside Stage B, AI-4a steps 1–4 beside Stage C. Nothing else runs ahead
  of its stage.
- **Stage D is indivisible.** AI-3 alone is the one-way ratchet §4.4 names. The stage exits only
  when, under the harness, an AI-initiated war has both started and ended.
- **Beats land with their owning rows** (§4.6b's ownership rule): beat 1 with AI-2 · beat 4's envoy
  with AI-2b, its war with AI-3 · beats 2 and 7 with AI-3 · beat 3 with AI-3's ladder gate (NA-5
  exists today; intent starts driving it in Stage D, §4.5 completes the wire in E) · beat 6 with
  AI-4b · beat 5 with AI-5b(ii). AI-6b owns the tempo rule and whatever no row claimed.
- **Every `.gd`-touching row**: boot the engine, grep `SCRIPT ERROR`, parse harness EXIT=0 (pin 20,
  the standing XR-1 rule).

**The living cut list** — supersedes §9a's copy (kept there as the v1.3 record). Cuts happen only at
the re-check or the exit review, and each entry names what it takes with it:

1. **AI-3b** sealed articles, *including* the §12.4 purchased dispatch and player seal — both halves
   go together. Takes §7a scene 7 and part of the DoD surprise line; §3.6's surprise budget then
   rides AI-5b(i), which is Core and cheap.
2. **AI-5c** the Arbiter's Offer *(v1.4)* — takes its beat variant; `arbiter_of_europe` stays a
   stance line until the exit review. Nothing else depends on it.
3. **AI-5b(ii)** the volte-face — takes beat 5 and §7a scene 4; the AI-V beats assertion amends
   seven → six.
4. **AI-2e's outbid arm** — takes §7a scene 5's France-bidding half; the visibility and
   remove-a-client halves stay.
5. **§3.5's upward-mirror assertion** — takes an AI-V arm-(b) row, never a DoD line.

**Never cut: AI-4c.** §9a's closing rule stands — without it AI-3 ships the ratchet, and the ledger
displays a *falling* exhaustion number for two powers grinding each other, which is worse than
displaying nothing.

---

## 12. v1.4 — the creative & structure pass *(July 24, 2026)*

A fresh-mind creative review with one constraint honoured throughout: **§6 is untouched.** Nothing
below reopens D1–D7; every addition routes through machinery the gate already blessed, and two of
them are definitions of words the gate record itself already used. The previous passes each asked
one question — v1.2 asked *"what does the player do?"*, v1.3 asked *"is it true?"* — and this pass
asks the one that remained: **"where are the missing reward loops, and what would the decade's own
statesmen recognise as absent?"**

**The gameplay verdict, first, because it was the brief.** The spine is right and this pass found no
reason to move any of it: the price ladder, the participation surface, the sealed article, the
seeded opening, the descent, the attractors. What was missing is narrow and characteristic of a spec
grown by review rather than by play: the game rewards *escalation* with drama at every rung and
rewards *successful prevention* with silence (§12.1); its marquee historical scene names an aim that
has no object (§12.2); its counter-instruments all cost gold, in a game whose France is often
gold-poor and permission-rich (§12.3); its one espionage surface has routes but no verb (§12.4); its
most alive neutral design has a stance line but no behaviour (§12.5); and the moment §3.4 itself
calls a minor's entire drama — the flip — happens *to* the player rather than being fought over
(§12.6). Each addition names the gap, the history, the mechanic, the price, and the owner.

### 12.1 The deterrence receipt — beat 7, "The Crisis Passes"

**The gap.** §3.1a builds the descent, and §4.6a — before this pass — named six beats, every one of
them an escalation or the resolution of somebody else's war. A player who *successfully deters* a war sees nothing: the
guarantee holds, the crisis quietly stops being foregrounded, and the D5 instruments teach nothing
at the exact moment they work. That is the worst reward loop a strategy game can ship — the payoff
for the phase's most sophisticated play is the *absence of an event* — and it quietly breaks D4's
promise too: if every foregrounded crisis always becomes a war, fore-warning is not warning, it is
scheduling.

**The history.** The period is full of wars that did not happen, and contemporaries experienced the
stand-downs as *events*: the Ochakov crisis of 1791, where Pitt mobilised the fleet against Russia
and then climbed down in public; Prussia's 1805 mobilisation — Haugwitz carried what was nearly an
ultimatum toward Napoleon and, after Austerlitz, delivered congratulations instead. A Europe where
crises only ever resolve one way is not the Europe this phase is modelling.

**The mechanic.** A foregrounded crisis (beat 2) must end **on screen**, as exactly one of two
beats: the fore-warned war, or **The Crisis Passes** — the stand-down, with its cause named and the
instrument credited. *"Berlin stands down, Sire. The King will not test your guarantee of Hanover."*
Cause taxonomy is the descent's own (§3.1a): bought off (b), deterred (the guarantee raised the
`weight` bar past reach), starved (§3.2 opportunism decayed), or satisfied (a). Conservation of
narrative, not added noise: a foregrounded crisis already owed the player an ending, so this beat
adds zero net lines to the §4.6 budget and pin 13 is untouched — non-foregrounded ladder coolings
stay quiet.

**Price and owner.** Nearly free — the intent layer computes every input already; the beat rides
beat 2's transports. Folds into **AI-6b**, lands in Stage D with beat 2. **Pin 21.** DoD gains the
"deterrence is visible" line, and AI-V arm (b) scripts one instrument-caused defusal.

### 12.2 The second design — Russia's "The Gulf and the Straits" (row AI-0d)

**The gap, and it is structural.** §1 names *"Napoleon points Russia at Sweden at Tilsit"* as one of
the four historical modes this phase exists to model. §3.6-4 defines the volte-face as a beaten
power "reversed... and **aimed at a third party**." §7a scene 4 makes that acceptance. But Russia's
authored deck holds exactly one design — `arbiter_of_europe`, a contain-the-hegemon posture — so a
volte-faced Russia has **nothing to advance to**: the deck ends, the aim has no object, and the
phase's marquee scene falls back to whichever nation happens to hold a design pointing somewhere
convenient. Meanwhile D7's Tier-2 "deck order among equally-live designs" band is nearly vacuous
where it matters most: among the majors, only Austria holds two live designs. Two gaps, one authored
entry.

**The history.** Finland boots Swedish on this map; Rumelia and Constantinople boot Ottoman. Russia
took Finland in 1808–09 — Alexander's stated casus was the security of Petersburg, and the licence
for it was agreed at Tilsit — and fought the Ottomans from 1806 to 1812 over the Danube and the
road to the Straits, a war that ran the entire width of the Napoleonic wars. France played **both
sides of the Eastern Question inside two years** — Sébastiani sent to stiffen the Porte in 1806,
the Tilsit understanding aiming Alexander south and north in 1807 — which is exactly the two-handed
game §3 wants on the player's desk. And the slow unwinding of those understandings — Oldenburg, the
principalities, Poland — is the road to 1812: the licence mechanism (§12.3) carries its own sequel.

**The authored entry** (behind `arbiter_of_europe`; the file's own blurb idiom):

```json
{
  "id": "gulf_and_straits",
  "type": "acquire_regions",
  "title": "The Gulf and the Straits",
  "regions": ["Finland", "Rumelia"],
  "blurb": "Petersburg is shielded on the Gulf and completed at the Straits - the Tsar's two shores. A design that waits behind the war with France, and wakes the day that war is no longer the Tsar's concern."
}
```

**Why it is safe, and what it unlocks.** Inactive at boot on every seed — `arbiter_of_europe` is
live at boot (France's share 0.396 ≥ its 0.33 floor) and first-predicate-wins; Russia's deck gets
**no order band** (no band → no variance, §3.8.1), so this cannot move the opening anywhere —
**pin 22**. It activates by exactly two routes, both wanted: arbiter goes inactive (France genuinely
contained — the late game gains an eastern storyline instead of a frozen board), or the volte-face
retires it (Tilsit — the AI-5b(ii) clause v1.4 adds). Its two victims collide with two authored
designs — Sweden's `scourge_of_the_usurper` and the Ottoman `guard_the_straits`, giving the guard
type its first real thing to guard against — and both targets are non-capital provinces, so the wars
it generates end in settlements, not eliminations (D2 untouched; the victims survive their loss
exactly as Sweden and the Porte did). It is AI-3's most natural far-from-France war, the relevance
weighting's first real subject, the licence's marquee use, and `against` is derived per §3's own
machinery — the intent layer, not the deck, decides which shore first, which is §3.2's opportunism
doing character work.

**And Austria gets the variance instead.** AI-0c authors its deck-order band over Austria's
*existing* pair — `redeem_italy` / `primacy_germany` — because that is the one place deck order was
genuinely contested in 1805: the Vienna war council's actual debate, Charles arguing Italy the main
theatre while Mack marched on the Iller. A seed where Austria opens Germany-first is not an
ahistorical seed; it is the other half of the real deployment.

**Price and owner.** Authoring + the validator that already validates decks + pin 22. Row
**AI-0d**, Core, lands with AI-0c in Stage A. The cheapest line in the phase per unit of payoff.

### 12.3 The licence — sponsorship at gold zero *(a definition, not a new instrument)*

D5-2's own gate text reads *"subsidise **or licence** another nation's design against a third
party."* The subsidy half got AI-2b's directed record; the licence half was never defined. Define
it: **a directed sponsorship with `amount_per_turn: 0`, whose consideration is the licensor's
committed non-interference.** Same record, same seams, one semantic: the licensor has sold not gold
but *permission*, and the §3.3 machinery holds the bond — the licensor entering the licensed war
against its recipient, or guaranteeing its target, is **reneging**, the highest-weight casus belli
in the game (**pin 23**, both directions — an AI hegemon may licence too, GR5).

It is also the exact inverse of §4.2b's sell-neutrality — one record shape, opposite flow — so the
build mints **one** record, not two. History: Tilsit's green-lights cost Napoleon nothing but
consent, and consent turned out to be the most expensive thing he ever sold. Gameplay: a gold-poor
France gains the currency it always has; *"drop your design on my provinces and I will bless your
design on his"* — the deflection trade — becomes playable without a treasury, and every licence
granted is a §3.3 hostage the player chose to hand over. Price: ~zero beyond AI-2b. Folds into
**AI-2b**, Stage C.

### 12.4 The purchased dispatch, and the player's own seal *(AI-3b's principle-7 half)*

**The gap.** Pin 12 makes every sealed article discoverable and lists only *passive* routes —
rumour, a diplomat's read, a defection, money in a ledger. Principle 7 says no mechanic lands
without its answering instrument in the same slice. Applied to AI-3b itself, that demands **an
active discovery verb**: pay Talleyrand's network to buy the text of a known meeting. The fact of
the meeting is always public (§3.6), so the player always has a handle to pull; the purchase is
deterministic and priced, through the standard 12-step action checklist. History: the *cabinet
noir*; every court of the period bought dispatches, and Talleyrand himself sold France's secrets to
Austria and Russia from 1808 — the man will hardly object to running the trade in the other
direction.

**And the seal cuts both ways (GR5).** France's own licence- and sponsorship-class bargains may be
sealed for a premium — hidden from third-party *reaction* until discovered. Implementation stays
cheap because intent is derived: masking happens at the intent/threat derivation chokepoint — a
court's read simply excludes articles it is not party to and has not discovered — one site, not N
producer sites, with discovery state carried on the article record. On discovery, the deferred
reaction fires **in full** plus an "the article is out" beat: sealing defers consequence, never
deletes it, and no disposition is sealable by anyone (**pin 24** — pin 11's boundary holds against
the player too). That converts the sealed article from AI flavour into a player risk instrument —
seal the Tilsit licence and race Britain's spies — which is the period's actual texture: half of
Europe's chanceries spent the decade paying to read the other half's mail.

**Price and owner.** Honest: article record + input masking + discovery state + one action. It is
why this stays **inside AI-3b** and why cut-list entry 1 takes both halves together.

### 12.5 The Arbiter's Offer — armed mediation (row AI-5c, may slip)

**The gap.** `arbiter_of_europe` is the most alive design in the boot deck — and its only behaviour
is a stance line. The audit read it aloud (*"correctly reads France's hegemony share"*) and that is
all it does. §3.4 promises Russia "intervenes far from home on principle"; the peacetime half of
that character does not exist.

**The mechanic.** A non-belligerent major with a live contain/arbiter design **offers to mediate a
French war** above an exhaustion floor: suggested terms through the existing incoming-settlement
machinery, delivered as a Courier variant, the mediator's interest named. Accept → the settlement
review opens with the mediator credited (relations, design satisfaction). Refuse → **derived
consequence only** in v1: the mediator's weight against France rises and relations drop — no new
threat namespace, no auto-join. The elegance is what happens next without a single bespoke wire:
that weight rise feeds the mediator's own ladder, its statecraft does the rest (Austria builds a
bloc, Russia sponsors), and refusing mediation *becomes* the ramp toward the next coalition — which
is Prague 1813 reproduced by machinery rather than scripted. History: Russia's 1806 mediation
feelers; Metternich's armed mediation of 1813, the ladder rung between neutrality and the Sixth
Coalition.

**Price and owner.** Medium-small: an ask type on the existing transport + suggested-terms reuse +
one derived consequence. Row **AI-5c**, Stage E, **may slip at the re-check** (cut list #2).
AI-vs-AI mediation — a court brokering someone *else's* war — is explicitly deferred to the exit
review; the player-facing half is the fun half.

### 12.6 The allegiance auction — a minor's flip is contested *(inside AI-2d)*

§3.4's own words: a minor's aliveness *is* its timing — "the moment it chose a side." §4.2b makes
wars courtable. Combine them: when a minor's bandwagon readiness crests, the flip is announced as
**in play** — a Courier beat — and both the hegemon and its rival may bid through the same D5
instruments before it resolves by lean + light profile. History: Bavaria, September 1805 — courted
by both empires, invaded by one, signed with the other in secret at Bogenhausen (a sealed-article
natural, if AI-3b lands). Saxony, 1806. Gameplay: the bandwagon rung becomes a contest the player
can *narrowly lose* rather than a weather event, and the D5 instruments get a second theatre.
Price: an eligibility predicate + the beat + best-standing-offer resolution over records that
already exist. Folds into **AI-2d's Stage C half**.

### 12.7 What this pass deliberately did not add

Recorded so the restraint is auditable, in the §10 discipline: **no espionage system** (one verb,
§12.4, priced and deterministic — an agent network with placement and counter-intelligence is a
different game); **no mediation teeth beyond derived weight** (an auto-join on refusal would mint a
new PEACE→WAR edge and violate §4.3a); **no second designs beyond Russia's** (Prussia, Britain and
the minors' decks are correctly shaped — more authored appetite is exactly the drift pin 1 exists
to stop, and Austria's variance need is served by ordering, not content); **no beat for
non-foregrounded coolings** (the tail stays quiet or pin 13 dies by a thousand stand-down notices);
and **no reopening of the §9a scope arithmetic** — the two genuine additions here (AI-0d authoring,
AI-5c) are priced above and one of them may slip.

### 12.8 Review record

| # | Finding | Disposition |
|---|---|---|
| 1 | Deterrence succeeds invisibly — the D5 instruments have no success feedback, and a foregrounded crisis could evaporate silently | **§12.1** beat 7 · pin 21 · DoD line |
| 2 | §7a scene 4's aim has no object: a volte-faced Russia's deck ends at `arbiter_of_europe`; the Tier-2 deck-order band is vacuous for every major but Austria | **§12.2** row AI-0d · pin 22 · the AI-5b(ii) retire clause · Austria's order band |
| 3 | D5-2 says "or licence" and the licence was never defined; sell-neutrality had no proactive mirror | **§12.3** the amount-0 arm of AI-2b · pin 23 |
| 4 | Pin 12's discovery routes are all passive — principle 7 was never applied to AI-3b itself; and the seal was AI-only, which is a GR5 asymmetry | **§12.4** the purchased dispatch + player seal · pin 24 |
| 5 | `arbiter_of_europe` has a stance line and no behaviour; §3.4's "intervenes on principle" had no peacetime expression | **§12.5** row AI-5c (may slip) |
| 6 | The minors' one dramatic moment — the flip — is uncontested weather | **§12.6** inside AI-2d |
| 7 | The document itself: four passes of sediment, build scope collated from five sections, no stage structure | **§11** the phased build plan · the compact header · the living cut list |

**What the pass did *not* touch, so its restraint is on the record like its predecessors':** §6
D1–D7 stand untouched; no v1.3 correction is reopened and no §10 row is contradicted; the §9a scope
arithmetic and cut-priority stand (AI-5c slots at #2 without displacing the never-cut rule on
AI-4c); every §5 pin 1–20 stands unedited; and the beat count is the only number this pass moved
anywhere in the acceptance layer (six → seven, with the AI-V arm map extended to match).

---

## 13. Standing review questions *(v1.4.1 — user-directed, July 24, 2026)*

Six questions the user put to the phase at the Stage A/B build session, recorded here so the
re-check and AI-V review them against evidence rather than memory. Each row names where the spec
already answers, and what remains open with its owner. **Nothing here reopens §6.**

| # | Question | Where the spec answers it today | What remains open — owner |
|---|---|---|---|
| Q1 | **Do the AI nations position troops on their borders — does the army agree with the ledger?** | Partially, and only as *reading*: NA-3 §5.6 biases enemy target-choice toward covets, and AI-1b's mirror reads FRANCE'S positions as intent ("his corps stand against their soil"). Nothing yet makes an AI court at `coerce`+ MASS toward its target before acting — the fore-warning is ledger-only. | **Row AI-3c "The army agrees with the ledger"** (below) — Stage D, inside AI-3: the war-intent marker biases the existing enemy-AI movement rungs toward the design's frontier, so a brewing war is visible ON THE MAP as well as in the ledger (the §3.5 mirror's symmetric half). GR5: same movement rungs, new bias input; no new movement system. |
| Q2 | **Can the AI handle fighting multiple wars at once — and what other edge cases lurk?** | The 1805 boot already puts Britain in three wars and the engine copes because all wars share the France-pair machinery. The generalisation is exactly where the risk moves: per-pair resolve (`effective_p1_threshold`), AI-4c per-war exhaustion, AI-4b third-party settlements. D1's cap bounds SIMULTANEOUS AI-initiated wars, not a nation's total belligerency. | **AI-V arm (a) gains a multi-front assertion set** (tracked in `test_ai_intent_assurance.py`): a scripted two-front fixture where one nation fights two separate wars — each war's resolve, exhaustion and settlement track resolves independently; no cross-war state bleed (the named edge cases: simultaneous settlement tracks on both wars, force starvation of one front, armistice on one front while the other burns, and a peace on front A never mutating front B's `war_instance`). |
| Q3 | **How does the AI balance WHEN to recruit marshals vs troops vs saving gold?** | The admin-chain priorities exist and are documented (`ENEMY_AI_REFERENCE.md`): P1 recruit, P1.6 vassal shore-up, P1.75 marshal commission, GR5-priced with war-priced recruitment ×3 and the Intendance modifier. What no pass has measured is that ordering under the EC-W economy (war effort + butcher's bill + contributions), where treasuries drain in war. | Owned by the **§8 "Economy re-measure" row** (already carried so it is not lost) + one AI-V arm-(a) assertion: over the 40-turn run, no solvent at-war major sits at zero recruitment for the whole run, and no nation commissions itself into bankruptcy (the two failure shapes). Re-tuning, if the measure demands it, is blessed-number territory — escalates only on shape change. |
| Q4 | **Do nations actually fight each other?** | **Not today — that is the finding the phase exists to fix (§0): no AI nation can decide to go to war, ever.** AI-3 (Stage D) builds the decision; AI-4 makes third-party wars hurt and END; D1 caps the world at 2 simultaneous AI-initiated wars; the DoD demands ≥1 AI-vs-AI war fought AND settled in the sweep. | Nothing further — Stage D is the answer. The Stage A/B session landed the prerequisites (the refusal record without which AI-3's ladder gate was unsatisfiable). |
| Q5 | **Can someone other than France be hegemon?** | **Yes, by design (D3):** the hegemon is derived court-relatively (`agendas._hegemon`, the §18 whole-phase fix), so whoever's bloc leads IS the hegemon — but a coalition forms against a non-player hegemon only when its share exceeds France's own. §5 pin 16(d) makes the eclipse a test: a scripted fixture where another power's share exceeds France's drives threat and coalition-formation against IT. | The pin lands with AI-4a steps 5–6 (Stage D). Note for the re-check: on the shipped opening France leads at 0.396, so eclipse is a mid-game state, not a boot state — working as designed. |
| Q6 | **What about any other edge cases?** | §5's 24 pins are the standing edge-case ledger; §10's corrections are the record of the ones prose got wrong. | The Q2 multi-front set above is the one genuinely new family this review added. Anything further found at the re-check joins §11.2's living cut list or a pin, never a vague note. |

### 13.1 Row AI-3c — "The army agrees with the ledger" *(new, Stage D, inside AI-3)*

| Row | Owner | Landing | Tracking |
|---|---|---|---|
| **AI-3c Border massing** | §13 Q1, §4.3's fore-warning | a court whose intent stands at `coerce` or `fight` (and whose §3.2 opportunism window is open) biases its EXISTING enemy-AI movement rungs toward the design's frontier — corps drift to the border before the declaration, so the fore-warned war is visible on the map; a design bought off or cooled (§3.1a) releases the bias the same turn (no latch). D4 holds: the massing is the *timing* signal made physical, never a hidden number. GR5: the bias rides the same movement scoring every marshal uses; no teleporting, no new movement verbs. | folded into `test_ai_intent_war_decision.py`; AI-V arm (a) asserts ≥1 fore-warned war in the sweep showed pre-war massing on the target frontier |

*Scope honesty:* AI-3c is a bias term inside Stage D's existing work, not a new stage; if the D6
re-check finds Stage D over-budget, AI-3c may slip to Stage E carrying its Q1 row here as the
written record — it must not silently vanish, because Q1 is a user question with a name on it.

---

## 14. Landing record — Stage A + Stage B *(July 24, 2026, one session; authoritative)*

**Built and landed:** Stage A (AI-0b · AI-0c · AI-0d) and Stage B (AI-1 · AI-1b · AI-2a), per the
§11.1 table, under the user's "as many phases as comfortable" direction. BD (Battle Diorama) was
deliberately re-sequenced BEHIND the AI stages by that same direction — its ROADMAP row stands.
*(Superseded July 24, 2026 — Stage C landed the same day, §15. The phase now stands AT the
⛩ re-check: nothing past Stage C may build before the user decides from the §15 evidence pack.)*

### Stage A — the dice and the bounds

- **AI-0b.** `backend/game_logic/campaign_variance.py`: sha256-derived, module-RNG-free
  `seeded_int` / `seeded_jitter` (JITTER_RAMP_TURNS=12, 0 at turn 0, 0 forever on historical) /
  `seeded_tiebreak` / `seeded_permutation`; serialized `WorldState.campaign_seed` (env
  `SOVEREIGN_SEED` read in `__init__` per the in-model idiom; `from_dict` restores EXACTLY, missing
  key → `historical` — pin 14c); `from_scenario(path, seed=…)` override; boot banner in `main.py`;
  seed shown in the strategic ledger (Intel tab, bbcode-sanitised) + save metadata; conftest pins
  `SOVEREIGN_SEED=historical` suite-wide. *A jitter draw is a fixed per-(seed, namespace)
  disposition scaled by the ramp — a mid-range draw is 0 at every amplitude, by design.*
- **AI-0c.** Authored bands in `europe_1805.json`: TEN relation bands (France|Prussia [-25,5] the
  Haugwitz contingency; Prussia|Russia; the grudge pairs Austria|Prussia + Hanover|Prussia NEW at
  centre 0; Ottoman|Russia; the Britain-client pair Austria|Britain + Britain|Russia; the minors'
  France-lean Saxony/Denmark/Naples), `threat_level_band [80, 90]`, Austria's `order_group` pair
  (Italy-first vs Germany-first — seed `ulm` opens Germany-first, pinned). Resolution in
  `from_scenario` AFTER validation, BEFORE `from_dict` — the save path never sees a band.
  Validator: `_validate_nation_relations` (sorted-key, contains-value, war-pair band entirely below
  the −60 armistice-first line), `_validate_threat_level_band` (requires the authored centre),
  `order_group` schema + contiguity (rejected in formable-template decks — no resolver, no band).
  MODDING_FORMAT + SAVE_FORMAT rows. **Deliberately deferred with owners:** the minors'
  bandwagon-lean *dimension* beyond relations and the boot-readiness band land with their consumers
  (AI-2, Stage C); the "new campaigns default to a random seed" flip is a **re-check decision** —
  until then variance is opt-in via `SOVEREIGN_SEED`/`seed=`.
- **AI-0d.** Russia's `gulf_and_straits` authored behind `arbiter_of_europe` (§12.2 verbatim; no
  Russia order band). Pin 22 green on every sweep seed; the one existing pin it legitimately moved
  (`test_contain_inactive_inside_hegemon_bloc` — Russia allied into France's bloc now advances to
  the Gulf, the Tilsit route) flipped consciously with the record in the test.
- **Tests:** `test_ai_intent_variance.py` + `test_ai_intent_historical_envelope.py` — the
  **six-clause historian test** across a 7-seed sweep (historical + crimson-1805/ulm/austerlitz/
  jena-06/wagram/tilsit), Tier-1 identity, Tier-2 in-band, no-band-never-varies, variance-is-real
  (relations ≥3 values, threat ≥3 values, Austria order fires), pin 14(a) unset≡historical.

### Stage B — Europe shows its hand

- **AI-1.** `backend/game_logic/intent.py`: `get_nation_intent` chokepoint — the §3 record
  {want, against, weight, price} derived from the agenda view + war state + relations + §3.2
  opportunism + the §3.8 jitter (the seed's first consumer, landed together per D7's ordering
  constraint); per-turn `_intent_cache` cleared in `invalidate_bloc_members_cache` beside
  `_agenda_cache`; **staleness DECIDED: relations/force/treasury turn-granular by design** (the
  agendas treasury choice), pinned. A live design's price floors at `ask`; deckless/vassal/player
  read `indifferent` (pin 18) and every surface omits. Boot intents pinned (measured): Austria/
  Britain/Russia `fight`; **Prussia `align` at 59 over Hanover** (the Potsdam winter, straight off
  the authored opening); Sweden/Sardinia `coerce`; Ottoman/Denmark `ask`. Surfaces: the nations-tab
  `intent` sibling + `diplomatic_ledger.gd` render; Talleyrand's war room names each belligerent's
  price; the rung-1.5 counsel carries the price clause.
- **AI-1b.** `build_france_mirror_payload` — "How Europe Reads France" atop the nations tab (a NEW
  block: the player never had a row): hegemon share, perceived rung derived from `threat_level`
  (restraint drifts it DOWN — the decay does the work, pinned), perceived target from French corps
  positions (ally/vassal soil never reads as the threat — staging; the read falls on whoever
  borders it: boot pin = Hesse, §3.5's blessed misreading shape). Europe-world only; legacy None.
- **AI-2a.** The six seams, no behaviour change: recipient-explicit envelope
  (`_build_proposal_terms`/`_make_proposal` — Talleyrand annotates only player-addressed mail);
  recipient-aware transport (`deliver_ai_proposal` routes foreign recipients to
  `_resolve_ai_ai_proposal`, never the mailbox); **the refusal producer both paths** — serialized
  `world.diplomatic_refusals` (`{proposer}>{recipient}` ORDERED keys, dedupe 6 / memory 12 turns,
  `get_refused_asks` is AI-3's gate read) written on player-rejects-AI, AI-rejects-player
  (reject AND counter-fail arms), and the AI-AI moment that did not exist — with its public
  `ai_ai_proposal_refused` campaign-log event (registered + formatted + **visible through the fog
  filter**); cooldown re-key to ordered pairs with the migration built into the key semantics
  (legacy `{nation}|…` IS recipient=player — zero save/test churn; the R43 `ai_ai|` ratify cooldown
  stays pair-symmetric BY DECISION); `ai_stalemate_counters` key semantics documented (bare name =
  vs-player; the acceptance-term latent coupling noted for AI-2). **The counter-offer arm, decided
  in writing:** AI-AI resolves accept-or-refuse only; court-to-court counters need statecraft
  (who haggles) and land with AI-2c — recorded in `_resolve_ai_ai_proposal`'s docstring. **Only a
  recipient-side refusal is a refusal** — a proposer-side balk stays silent, as pre-refactor.
- **Tests:** `test_ai_intent_layer.py` (23) + `test_ai_intent_peacetime_convergence.py` (21).

### The review, and what it caught

A 60-agent find→2-refuter workflow (8 lenses) confirmed **11 distinct findings, ALL FIXED
pre-commit** — headline **P1: the court-to-court refusal event was invisible in-game**
(`filter_campaign_log` had no branch for it and the phase loop excludes refusal events from its
return — no surface showed it); plus the refusal misattribution ("{X} rebuffs {X}" when the
proposer's own acceptance balked — now recipient-refusals only), the counter-fail arm missing the
pin-8 record, two validator gaps (orphan threat band; formable-deck order_group as silent no-op),
the survival-threat capital-first that never applied, live-design price `indifferent` nonsense
copy, the seed's bbcode injection, and four test-falsifiability hardenings (the live-path AI-AI
ratify pin, nonzero-jitter pins, the tautological historical-jitter test, the fog-filter/log-half
assertions). Consciously flipped pins: campaign-log type count 122→123 (two files), the 1805
relations matrix +2 grudge pairs, the war-room row key set +`intents`, the Russia
contain-inactive-in-bloc pin (→ gulf_and_straits, the Tilsit route).

**Exit criteria check (§11.1):** Stage A — pins 14(a)+22 green ✓ · six-clause historian harness ✓ ·
validator + MODDING_FORMAT rows ✓ · suite + M1–M7 byte-identical on historical ✓. Stage B — boot
intents pinned against authored 1805 ✓ · renders live (parse harness EXIT=0, headless boot 0
`SCRIPT ERROR`; the **pin-20 live in-game visual pass remains open** for the user's next session —
backend payloads + renders verified headless only) ✓* · AI-2a byte-identical player-flow pin green
(suite) ✓.

## 15. Landing record — Stage C, "The Bargaining Table" *(July 24, 2026, same session as A+B; authoritative)*

**Built and landed** per the §11.1 table: **AI-2 · AI-2b · AI-2c · AI-2d (Stage C half) · AI-2e**,
plus the parallel-track **AI-4a steps 1-4**. Commits `2f2dc22` (the build) + the review-fix commit.
**The phase now stands AT the ⛩ re-check** — Stage D may not build before the user decides.

### What landed

- **AI-4a steps 1-4** — `world.threat_by_target` with `threat_level` as a property over the
  player's slot (the `gold` idiom); `add_threat`/`reduce_threat` optional ACTOR target; source
  entries carry `target`. **The step-4 pin held byte-identical against the `d1be956` baseline
  before any behaviour slice landed** (`test_ai_intent_threat_migration.py` — a
  PYTHONHASHSEED-pinned 40-turn subprocess harness; the ambient sim is hash-order-unstable across
  processes, pin 14(c) observed in the wild). The constant was then re-recorded CONSCIOUSLY at the
  rung rework. Steps 5-6 stay Stage D; every non-player slot is structurally 0 (pinned).
- **AI-2b** — `instruments.py`: the ONE directed record (§12.3) covering sponsorship, the licence
  (amount 0, pin 23) and sell-neutrality (`kind="neutrality"`); compensation bargains that SUSPEND
  a design at the `get_active_agenda` chokepoint; guarantees with the intent deterrent (−8, shown)
  and the `guarantee_abandoned` enforcement `protection_promised` never had. Three serialized
  stores + `allegiance_auctions` (§5 pin 8). Player verbs `sponsor_design` / `buy_off_design` /
  `guarantee_nation` (1 DP, honest-availability refusals, 12-step wiring, 4 corpus rows). Renege
  marks ride the EXISTING directed grievance store; intent reads them as the §3.3 weight surge
  (+15). Beat 4 fires on the PL-14 outcome popup in the Voice Bible register.
- **AI-2c** — `nation_config.NATION_STATECRAFT` (honor-bias idiom, `world.get_statecraft`): the
  four majors per the §3.4 table + six light secondaries; ask-order partition under the NA-2
  design-front rule; the coercion delta at the player-ultimatum seam (Britain's subsidy wall −40
  **derived** from `hostile_army_on_home_soil` — pin 10); the AI-AI haggle arm AI-2a's docstring
  promised (near-miss band [35,50), one rung down, dual consent, non-hagglers byte-identical);
  `weight_mod` authored 0 on every 1805 court (boot-neutral, pinned). *§3.4 amendment note: the
  `haggles` gate is a FIFTH biased thing beyond the section's "four things only" — mandated by
  AI-2a's own deferral language; recorded here rather than silently.*
- **AI-2** — the P-Intent rung **BEFORE P3** (the design outranks the threat-shelter ask — at boot
  threat 85, a P3-first ordering would have silenced every design ask): the design purchase
  (accept cedes + satisfies — §3.1a descent live; reject writes the pin-8 record), sell-neutrality
  (accept mints the §3.3 compact; the bond DISCLOSED at decision time as a rendered
  `neutrality_compact` clause + its own Talleyrand assessment), the alignment ask; AI-AI trigger 0
  (design asks → the refusal record AI-3 escalates from, dedupe-window-aware so legacy triggers
  are not shadowed; alignment pacts); P-Bandwagon widened to any ≥50% hegemon, intent-driven,
  boot-dormant; the sponsor branch (Russia funds Austria from turn 1); the §4.2c budget
  (`INTENT_ASK_BUDGET_PER_TURN = 2`, its own lane — court-to-court envelopes consume neither);
  the opportunism valve (design_purchase only, the URGENT_REPROPO idiom).
- **AI-2d (Stage C half)** — sell-neutrality + sponsor arms (above) + the §12.6 allegiance
  auction: serialized `allegiance_auctions`, the announced flip (always-visible, pin 11), 3-turn
  bidding window over standing D5 records + lean (10g/turn = 1 point), player wins arrive as
  refusable OFFERS, passed crests lapse, an AI flip is announced only when the pact actually
  ratified. Join/broker stay Stage D (§4.2b's split).
- **AI-2e** — the subsidy visible (campaign log + dispatch + THE PAYMASTER'S PURSE balance block +
  per-nation Compacts ledger lines, `.gd` renders landed); the outbid at recipient selection over
  AI-2b's directed record; a bought-off client not worth funding.

### The review, and what it caught

An 8-lens find→2-refuter workflow (56 agents; 27 verifiers were killed by the session usage cap —
those findings were adjudicated by hand, in context, against the code). **16 confirmed findings,
ALL FIXED in the follow-up commit** — headline **P1 (three lenses converged): renege attribution
was DIRECTION-BLIND** — the symmetric `is_at_war` plus a mint-time-fixed breaker branded the
ATTACKED party ("torn up — by your hand, not ours" shown to a player the AI had just declared war
on, with the aggressor collecting the +15 surge). Root fix: **renege is an ACT** — only a
POST-MINT war brands anyone, and the branded party is the war's AGGRESSOR read from the
war_instances attackers side; unattributable/pre-existing wars LAPSE the record on the log
(`instrument_lapsed`), branding nobody. Also fixed: guarantee grace now runs from
max(war start, pledge) with ward-aggression voiding unblamed; mint gates refuse at-war buy-offs /
sponsorships and guaranteed-aim sponsorships (the guarantee verb's own idiom); the sell-neutrality
compact mints ONLY on successful ratification and the offer maps to a ratifiable type at cold
relations; the licence dedupe (one live record per kind+payer+recipient+aim — the +5-relation pump
is dead); the player sustain bar (×4 cover, the AI's own gate); the term counter (a promised
10-turn sponsorship pays exactly 10 on both mint paths, and an expiry-turn war can no longer slip
the bond); compensation terms are FINITE (`COMPENSATION_TERM_TURNS` 15 — the design sleeps, it is
not deleted); the ultimatum confirm estimate now carries the coercion delta (shown = applied, was
lying by up to 40 for Britain); `hostile_army_on_home_soil` read a nonexistent `captured` attr (a
PRISONER at London dropped the subsidy wall) + gained the 1,000-man floor; the haggle arm and the
auction announce nothing a failed ratify did not sign; the Broken-Bargain popup never clobbers an
in-transit answer (the NA-6b §17.1 class); expiries/lapses reach the campaign log; dispatch
priorities authored (broken_bargain/allegiance HIGH).

### Deferred with owners (GR9)

- **AI producers for guarantees + compensation grants + region-granting compensation** (the D5
  "both directions" remainder): the records bind both directions today, but an AI court choosing
  to guarantee/buy off needs the war-decision context — owner **AI-3 (Stage D)**, where the
  choice has stakes. Sell-neutrality + sponsorship already produce AI-side.
- **The F1 wizard chips for the three instrument verbs** (typed-command + refusal surfaces landed;
  the guided chips belong to the courting surface): owner **AI-6c (Stage F)**, the client-surface
  remainder row that owns "the §4.2b courting surface".
- **A ledger Net line for standing sponsorship payments** (the per-turn transfer is visible in the
  Compacts row and the campaign log but not as a treasury Net component — the treaty
  `gold_per_turn` clauses share this pre-existing shape): owner — the §8 economy re-measure row,
  with EC pass 2.
- **Statecraft applies on legacy worlds** (Austria hardens under a legacy-fixture ultimatum too):
  CONSCIOUS — statecraft is character, world-agnostic like the honor bias; the legacy suite is
  green with it live.

**Exit criteria check (§11.1 Stage C):** pin 18 deckless-neutral green (bare-world pins in all
four new test files) ✓ · the §4.2c delivery budget live (its own lane + the marquee-case test) ✓ ·
beat 1 firing (the named-envoy pin on a live design purchase) + beat 4 firing (the cold-envoy
popup pin) ✓ · pin 23 green (licensor renege both directions, licence == paid bond) ✓ · the
re-check evidence pack = `docs/audits/STAGE_C_EVIDENCE_2026_07_24.md` ✓. Suite **14,772/3**
(+159 over Stage B's 14,613); parse harness EXIT=0; headless boot 0 `SCRIPT ERROR`; the pin-20
live in-game pass remains OPEN for the user's next session (now covering the Stage B ledger
surfaces + the Stage C compacts/purse rows and the courier/auction beats).

---

## 16. ⛩ The re-check — gate record *(held July 24, 2026; authoritative)*

**Authority.** D6's "user re-check between Stage C and Stage D," held from the evidence pack
(`docs/audits/STAGE_C_EVIDENCE_2026_07_24.md`) under the user's standing session direction — *"do
next phase of intent, commit and push"* — the same delegated-defaults idiom as the EC-W gate and
8.EVAL. Every decision below is the evidence pack's own recommendation or the spec's marked
default; **nothing reopens §6.** Stage D (War and Peace) is hereby OPEN to build.

### 16.1 The docket, decided

1. **D1's cap — CONFIRMED at 2** simultaneous AI-initiated wars, acceptance band 1–4 over the
   40-turn sweep. Evidence §2: no live AI wars exist yet to measure against; the refusal-record
   accumulation rate (≤1 per coveting pair per 6-turn dedupe window, one standing boot pair)
   puts no pressure on the default. **Re-measure at the Stage D landing record** from the first
   40-turn sweep with wars live, and again at AI-V.
2. **Cut list #1 — AI-3b (sealed articles + purchased dispatch + player seal) SLIPS out of
   Stage D.** The slip the stage table already marks *(slip 1)* is exercised: Stage D is the
   phase's largest stage and its indivisibility rule (a war must start AND end under the harness
   before anything user-facing lands) is the wrong place to carry the phase's one optional
   espionage surface. **Slipped, not cut** — final keep-or-cut at the exit review. While slipped:
   pin 24 rides the row; §7a scene 7's sealed-article half and the DoD surprise line carry this
   entry as their written blocking predicate (the partition itself stays reachable — AI-4b's
   third-party settlement is Stage D Core; only the *sealed* arrangement of it waits).
3. **Cut list #2 — AI-5c (the Arbiter's Offer) KEEPS its Stage E slot.** The refusal consequence
   is derived-only, the transport exists, and it is `arbiter_of_europe`'s only behaviour; cutting
   now would re-open §12.5's gap for no schedule gain (Stage E is not the long pole). It remains
   cut-list #2 if Stage E overruns — this record is its keep decision, not its immunity.
4. **Cut list #3/#5 unchanged** (AI-5b(ii) volte-face stays the Stage E slip candidate; the §3.5
   upward-mirror assertion stays an AI-V arm-(b) row). **Cut list #4 CLOSED** — the outbid arm
   landed in Stage C and did not slip (evidence §3).
5. **Pin 17(b) — the AI-4c economy deltas are NOT blessED here, by necessity** (evidence §4: the
   third-party exhaustion/treasury series cannot exist until AI-4c lands). The blessing is
   **re-sited to the Stage D landing record (§17)**, where the measured boot third-party series —
   the four boot belligerents' exhaustion and `calculate_war_effort_cost` deltas — is recorded
   and blessed with data, as pin 17(b) itself anticipates.
6. **Balance flags (evidence §5) stand as blessed in-band:** guarantees at 1 DP (the credibility
   stake is the real price), `COMPENSATION_TERM_TURNS = 15`, sponsorship term 10 / tiers
   200/300/400. Revisit with live-war data at the exit review; shape changes escalate.
7. **AI-3c (border massing) stays INSIDE Stage D.** §13 Q1 carries the user's name; the row is a
   bias term on existing movement rungs, not a stage risk. The §13.1 slip-to-E clause stays
   available if the stage overruns mid-build.
8. **The §4.4b D3 arbitration ruling — EXCLUSIVE.** One active coalition world-wide.
   Anti-France precedence, so D3's gravity is never diluted: a coalition against a non-player
   hegemon forms only when **no anti-France coalition is active** and that power's hegemony share
   exceeds France's; if France's own threat crosses the formation threshold while an anti-X
   coalition stands, the anti-X coalition **dissolves in its favour** (logged as its own event —
   Europe remembers who the real danger is). `coalition_count` and the `_ORDINALS` naming stay
   world-wide — one sequence of coalitions in Europe's history, whoever each was against.
   Consequence per §4.4b: the singleton `world.active_coalition` suffices; the migration is
   anchor work on the existing `target_nation` key, not a store rewrite.

### 16.2 What Stage D builds (the scope as gated)

Per §11.1 with the dispositions above: **AI-3** (+ §4.3a all four requirements + the
co-belligerent side-exit helper + **AI-3c**) · **AI-4a steps 5–6** · **AI-4b** third-party
settlements + §4.4b under the exclusive ruling (Core, the stopgap stays deleted) · **AI-4c**
(never cut) · **AI-2d join/broker arms** + the Stage C deferral "AI producers for guarantees +
compensation" (§15, owner AI-3) · **beats 2, 3, 6, 7** with pin 21's one-of-two-endings contract
and the one-foregrounded-crisis tempo rule. AI-3b is out (item 2). Exit = §11.1's Stage D row:
pins 15 / 16 / 17 / 19 / 21 green (24 slipped with its row), the DoD war lines, and an
AI-initiated war that has both started and ended under the harness.

---

## 17. Landing record — Stage D, "War and Peace" *(July 24, 2026; authoritative)*

**Built and landed in one session, immediately after the §16 re-check, under the same user
direction ("do next phase of intent, commit and push").** The stage's indivisibility rule held:
nothing user-facing landed before AI-4b/4c closed the loop, and the exit test is the §11.1
sentence itself — under the harness, an AI-initiated war both **starts** (Prussia declares on
Hanover for the Hanoverian Prize, fore-warned, coerced, ladder-climbed) **and ends** (the
exhausted loser sues through the P1 seam; the winner takes the surrender; the design province
changes hands; the war instance closes) — `test_ai_intent_war_decision.py` +
`test_ai_intent_third_party.py`.

### What landed

- **AI-4a steps 5–6** (the phase's highest-risk item): every threat producer now passes the
  ACTOR as `target` — battle wins/decisive victories/capital captures (both combat copies),
  region capture, treaty annex/return, liberation, forced alliance (both the treaty and
  settlement layers), war declaration, diplomatic downgrade, treaty breach, ultimatum annex,
  and all six vassal-family sites. The coalition standing block gained per-nation
  region-control loops and the previously computed-and-DISCARDED non-player
  `hegemony_passive` increment (D3's fuel, wired). The four standing contributors carry their
  written decisions in-code (defensive-refusal memory / schemer markers / the two grudge
  families / ultimatum defiance — all STAY FRANCE-ONLY, reasons stated at the block).
  Per-target decay runs on the player's own schedule through `reduce_threat` (entries carry
  targets); the eclipse pass (`_eclipse_candidate`) brews — never instant-forms (pin 16c
  structural) — against a non-player power only when its bloc share exceeds France's AND no
  coalition stands anywhere (the §16.1-8 exclusive ruling), and the player is never enrolled
  (neither as qualifying nor via the already-at-war arm).
- **Pin 16(a) VERIFIED in isolation**: with the AI-4c tick temporarily neutralised, the
  40-turn `historical` threat series was byte-identical to the recorded baseline; re-run with
  AI-4c live it was byte-identical AGAIN (the third-party exhaustion economics did not ripple
  into France's series on the pinned run) — **`BASELINE_SERIES` stands unedited.** The
  Stage-C-era `test_no_nonplayer_slot_ever_accrues` invariant was consciously INVERTED
  (non-player slots now live: Britain peaked 55, Austria 19, Holland/Spain/Prussia/Russia
  decayed back to 0 on the same run — pin 16(b) live organically); the new assertion also pins
  that no non-player slot reaches the brewing tier on the historical ambient run (D3's gravity,
  measured).
- **§4.4b under the exclusive ruling**: `qualifies_for_coalition` / `get_qualifying_nations` /
  `get_nations_at_war_with_target` / `coalition_leadership_score` (the one SEMANTIC change —
  hostility re-anchored to the coalition's target) / `select_coalition_leader` /
  `form_coalition` / `check_dissolution` / `calculate_coalition_war_score` all take or read the
  target, defaulting to the player byte-identically (`target_nation` key, legacy records
  default player). Anti-France precedence: an eclipse coalition dissolves
  (`the_greater_danger`, its own log event) the turn France's alarm crosses the brewing line,
  cooldown zeroed — Europe remembers who the real danger is. `coalition_count`/`_ORDINALS`
  stay world-wide.
- **AI-4c**: the per-turn tick keys on `get_nations_at_war_with(nation)` on Europe worlds (the
  France arm's own predicate); the legacy world keeps the France-relative read verbatim (pin
  17c green). Both combat copies gained the explicit third-party arm — the LOSER bears its own
  dead, the France arms verbatim above it. **The mirror copy's pre-existing divergence
  (France-defender-wins grants no decisive_victory/shock) is PRESERVED, not fixed** —
  byte-identity before symmetry; flagged for the exit review. Coalition shock kept its
  France-arm gating verbatim (members' WE feeds separate-peace acceptance — widening it is a
  behaviour change this migration must not smuggle in; exit-review item). Display: the nations
  tab gained the labelled `war_weariness` line ("National exhaustion across all wars: N
  (trend) — at war with …", §4.2b's labelled arm) with its own `diplomatic_ledger.gd` render.
- **Pin 17(b) BLESSED, with the data the re-check re-sited here** (3-turn boot measurement,
  historical seed): Spain we=24/28g·turn, Holland we=26/5g, Bavaria we=40/4g, KingdomOfItaly
  we=24/10g — the four boot third-party belligerents accrue from turn 1 as the pin demands,
  their `calculate_war_effort_cost` deltas are one order below their treasuries
  (257–2,938g standing), and no solvency shape moved. Blessed as-is; the §8 economy re-measure
  row still owns the long-run retune.
- **AI-3 — `war_council.py`**: the crisis lifecycle (open → beat 2 with honestly-gated
  instruments → beat 3's AI-AI coercive demand, REFUSED onto the serialized record → the
  declaration at `CRISIS_FOREWARN_TURNS=2` of foregrounded tenure), the ladder gate
  (`CRISIS_REFUSALS_REQUIRED=2` or a §3.3 renege grievance that may skip rungs), the restraint
  gates (no existing wars, treasury ≥500, force ratio 1.25× incl. the target's guarantors in
  the scale), `MAX_SIMULTANEOUS_AI_WARS=2` (D1 — a capped crisis WAITS, it does not die), the
  §4.3a-4 `can_declare_war` shared preview, the §4.3a-2 treaty-break-first step (an
  unbreakable predicate stalls the crisis and cools it as starved after 4 polls — pin 21's
  termination guarantee), the §4.3a-1 declaration at the announcement (`declare_war` direct;
  the combat seam later finds the war live), war instances stamped
  `ai_initiated`/`design_id`/`stated_reason`, the objective's `target_regions` re-pointed to
  the DESIGN's provinces (+`design` key — reuse, not a new war-goal system), and the logged
  `war_declaration` event carrying `stated_reason` for the headline (pin 4). **v1 scope
  pinned: AI-vs-AI acquire designs only** — a player-targeted design coerces through NA-5 and
  fights through the coalition (the NA-5 no-unilateral-war pin stands); deny/contain designs
  express through guarantees and coalitions, never a council war.
- **§4.3a-3 + pin 15**: both combat-seam refusal discards are now ABORTS (a refused
  declaration returns a refusal, the world byte-identical), and the `OPEN_MOVEMENT_STATES`
  capture hole is CLOSED — an attack on a peace-nation's region always requires a successful
  declaration (AI) or the WPS staging (player; the player's silent open-borders capture is
  gone with it — pin 4's second clause). Plain movement under those treaties is untouched.
- **The §4.3a blocked case**: `exit_shared_wars_for_defection` — the VS-6 side-exit idiom
  lifted into `war_council` — peaces out a co-belligerent's shared wars so the defection
  declaration can land; pinned executable against the boot Third Coalition (Austria exits its
  France war, then declares on Britain). Organic use stays with AI-5b(ii).
- **AI-3c**: `get_intent_frontier` (per-turn cached, GR8) anchors the P7 mover on the design's
  own unmet provinces — the massing EMERGES from the existing `_can_ai_move_to` gates
  stalling every corps at the last lawful region; the bias enters P7's
  empty-targets early-return so an at-peace coveter finally moves; released the turn the
  crisis cools (no latch); deckless worlds byte-identical (the store is empty).
- **AI-4b — `settlement_third_party.py`**: the loser sues through
  `effective_peace_threshold` — **P1's inline formula EXTRACTED to this one seam, verbatim
  (pin 19b)** — the winner scores through
  `settlement_scoring.calculate_common_peace_acceptance` (module attribute — the standing
  patch seam holds for the AI-AI arm, pinned), hard stops are an absolute veto, and the
  **victor's-consent arm** covers what the scorer honestly under-scores: SURRENDER-shaped
  terms (every material clause flowing to the accepter) need no enthusiasm, and a white peace
  lands on mutual exhaustion. Terms = `_settlement_offer_build_terms` (its `player` parameter
  RENAMED `accepter`, nation-pair-general per §4.4) + the territorial generator: up to two of
  the winner's DESIGN provinces still in the loser's hands cede — **the D2 capital ruling
  landed here**: a single-province minor's capital IS the design's object and may cede (its
  nation eliminating, D2's "minors yes"), a great power's (`_CANONICAL_MAJORS`) capital never
  rides a routine cession. The headless ratify wrapper drives the four internals + the three
  invalidations + `process_formations` and NEVER touches `dialogue_manager` (pin 19c pinned
  with a mounted sentinel). Beat 6 (The Congress) names its consequences — who took what, who
  pays, whether the new ground touches the French frontier.
- **AI-2d join/broker**: an AI guarantor of the target declares on the aggressor at the
  declaration (`guarantee_honored`, casus belli); FRANCE's own pledge produces the ward's
  plea (`guarantee_called` dispatch event) and the Stage C abandonment clock does the honest
  rest — the player is never auto-conscripted. The broker: a court within
  `BROKER_ASK_MARGIN=10` of its threshold asks France to convene (`broker_peace` on the
  existing incoming-proposal transport + display row); Accept runs the settlement attempt at
  the broker margin with the outcome as a result popup (the PL-14 rule — no new dtype), and a
  landed congress pays the broker's fee (+10 relations with both courts).
- **AI instrument producers** (the Stage C deferral, §15 → here): on a live foregrounded
  crisis, a folds-statecraft holder solvent for `compute_buyoff_price` buys the coveter off
  (gold moves, the bargain minted, the crisis passes bought_off — descent (b) has an AI
  producer at last), and one protector per turn world-wide (sponsor/align statecraft, warm to
  the ward, cold to the coveter, at peace) pledges the guarantee that makes beat 7's
  "deterred" reachable without the player.
- **Beats 2/3/6/7** on existing transports: campaign-log types `crisis_brewing` /
  `coercive_demand` / `crisis_passed` / `guarantee_honored` / `third_party_peace` (count pins
  flipped consciously 134 → 140, both test files) riding the town-crier visibility arm beside
  the auction (DPF-1 — a crisis, its demand, its ending and a congress are court knowledge);
  dispatch templates + priorities (beats HIGH — events, exempt from the routine cap; the
  demand MEDIUM under the crisis lead); and the dispatch HEADLINE finally has non-France arms
  — `europe_at_war` (with the stated reason) / `europe_crisis` / `europe_congress` /
  `europe_crisis_passed`, all weighted BELOW everything France-centric (pin 13) with their own
  Berthier closing notes.

### Conscious pin flips and preserved warts

1. `test_no_nonplayer_slot_ever_accrues` → `test_nonplayer_slots_live_and_bounded` (the
   Stage-C-era steps-5-6-have-not-landed invariant, inverted by landing them).
2. Campaign-log count 134 → 140 (both count pins; the five beats plus the
   §16.1-8 pivot event `coalition_dissolved_for_france`).
3. The auto-combat mirror's missing decisive_victory/shock on France-defender-wins is
   PRESERVED (pre-existing divergence; byte-identity first) — exit-review item.
4. Coalition shock stays France-gated in both copies (widening it moves members' WE, which
   moves separate-peace acceptance) — exit-review item.
5. `war_declaration` threat now credits EVERY aggressor's own slot — a coalition member
   declaring on France takes a transient +20 in its own slot (decays; D3-gated from ever
   mattering); noted at `form_coalition`.
6. The player attacking an open-borders partner's region now stages the War Purpose dialog
   instead of silently capturing (pin 4's second clause — behaviour change, correct).

### Serialization

ONE new world field: `war_intents` (crisis records — fore-warning tenure must survive a save;
`from_dict` reads pre-Stage-D saves as `{}`). War instances carry `ai_initiated` / `design_id`
/ `stated_reason` / `third_party_peace_attempt_turn` / `broker_ask_turn` inside the
already-serialized container; objectives carry `design`. `SAVE_FORMAT_REFERENCE.md` updated
(including the missing `diplomatic_refusals` row this session found).

### Exit criteria check (§11.1 Stage D as gated by §16)

Pin 15 (refused-declaration aborts + the capture hole) ✓ · pin 16(a-d) (byte-identical series
verified in isolation AND with AI-4c live; return-to-zero organic; never-instant structural;
the eclipse fixture forms against Austria with France's slot unmoved) ✓ · pin 17(a-c) (both
belligerents monotone over 20 turns; boot deltas measured + blessed above; legacy tick
verbatim) ✓ · pin 19(a-c) (satisfy-drops-rung via the crisis-passes causes; the AI-AI suing
seam IS P1's; ratify with the mounted dialogue untouched) ✓ · pin 21 (both endings on screen;
the stall guarantee) ✓ · pin 24 slipped with AI-3b (§16.1-2) · the war starts AND ends under
the harness ✓ · beats 2/3/6/7 firing (campaign log + dispatch + headline arms) ✓ · France
courted: the courting rides the existing Stage C arms the moment the war exists (sell-
neutrality's "a war France is not in" gate opens; the guarantee plea and broker ask are new
Stage D couriers) — the sweep-level "every AI war produced ≥1 offer" assertion stays with
AI-V, where the DoD sites it. `test_ai_intent_war_decision.py` (19) +
`test_ai_intent_third_party.py` (13) + the flipped migration pins; suite green (count in
STATUS); ruff clean; `diplomatic_ledger.gd` boot-smoked (XR-1).

### 17.1 The review round — 9 lenses, 2 HIGH + 12 confirmed findings, ALL FIXED

A nine-lens adversarial fleet (threat migration · war-council lifecycle · settlements · combat
seams · fog/GR/display · exhaustion/economy · coalition rulings · beats delivery · test
falsifiability) ran against the landed commit `3227024`. Everything the fleet confirmed was
fixed in the same session:

- **[r5 HIGH] The boot-minors exhaustion ratchet.** The seven `starting_wars` fold into ONE
  instance CONTAINING France, so the instance-scoped player-skip froze the four satellite
  sub-pairs (Spain|Britain, Holland|Britain, Bavaria|Austria, KingdomOfItaly|Austria) — under
  the AI-4c tick they would have ratcheted to exhaustion 200 with no exit until the player
  ended the whole Third Coalition war. Fixed as **the exhausted-pair exit**: a non-player,
  NON-VASSAL sub-pair inside a player-containing instance signs a white peace when both sides
  are spent (≥120), the pair is old (≥10 turns) and stagnant (|score| ≤ 15) — §3.1a's descent
  (c) for the co-belligerent minors, Spain's own 1795/1802 exits; ONE pair exit per turn
  world-wide; the player's pairs and every vassal's pairs untouchable (a vassal follows its
  lord's war — its weariness is the lord's pressure to read). The 40-turn threat baseline was
  re-recorded consciously ONCE for this (identical through turn 17, +3 after — the ripple of
  the minors' side-wars actually ending).
- **[r2 HIGH] The D1 cap jammed on elimination victories.** A design war won by eliminating
  the minor never receives `ended_turn` (elimination bypasses the settlement path), so the cap
  counted it forever — two successful conquests would have ended AI war-making for the
  campaign. Fixed: a war is LIVE for the cap only with two standing sides.
- **[r2 MED] Pin 21's stall guarantee extended to the SOFT gates** (cap/ladder/restraints, 8
  turns) — a fully fore-warned crisis that cannot fire no longer freezes the world-wide
  foreground slot forever.
- **[r1 MED ×4] The eclipse reader leaks**: the CRITICAL brewing-countdown notification, the
  top-bar `coalition_brewing` flag (`main.py` ×2), the Morning-Dispatch coalition section's
  sources/brewing/active-coalition blocks, and the war-room "What stirred Europe" list all now
  filter to PLAYER-targeted threat entries / player-targeted coalitions.
- **[r6 MED ×3] Presentation de-anchoring**: `coalition_declared`/`coalition_dissolved`/
  `coalition_brewing_started` oneliners, the formation notification (NORMAL priority + "on
  {target}" copy for eclipses), and the new `diplomatic_coalition_{formed,dissolved,brewing}_other`
  dispatch templates; the §5b convergence bias converges on the coalition's own
  `target_nation`; the 6a/brewing precedence now fires only when France can actually coalesce
  (≥1 qualifying court — kills the dissolve/re-brew oscillation); the eclipse brewing gained
  its turn-1 rail notice + dispatch line; the France coalition panel (`diplomatic_ledger`)
  excludes eclipse records until Stage F's own render.
- **[r3 MED] The broker ask names its war** (`proposer_nation`/`target_nation` on the terms —
  was "between Unknown and France") + the envoy chip dismissal on accept; the last-region
  cession is only generated at the total-annexation score (the announced peace always matches
  the applied one); the force arm STRUCTURALLY refuses any material package not flowing wholly
  toward the accepter (the winner-pays hole closed by shape, not by constant coupling).
- **[r8/r5-fog] R7 leaks**: `third_party_peace` and the eclipse brewing messages humanize
  their nation names; the guarantor-join war's logged declaration carries "honouring the
  guarantee of X" as its stated reason (pin 4).
- **[r4 LOW] The auto-combat mirror gained the symmetric falsy-nation guard.**
- **[r9] Test falsifiability**: pin 15's FULL second clause asserted (strengths, locations,
  instance count, no conquest event); the third-party battle arm exercised through the real
  executor; the deterred skip became a hard assert; the save/load test drives the CLOCK to the
  post-load declaration; the real declaration pins `count_ai_initiated_wars == 1`; the
  elimination-frees-the-cap pin added.
- **Accepted with reasons**: the three cause-copy variants (dispatch/headline/log — different
  registers per surface, flagged as drift-watch); the AI-AI coercive-demand dedupe return
  unused (the ladder gate re-verifies independently); the eliminated-coveter "satisfied" copy;
  the orphaned `proposal_result` route + the single-candidate headline repeat (pre-existing,
  out of scope); vassal-only wars settling headlessly (vassals fight their own wars —
  confirmed intended); the guarantee's 1-DP player price vs the AI's predicate throttle (DP is
  architecturally player-only; mechanic shared — not a GR5 break).

Post-fix gates: suite **14,831/3**, ruff clean, M1–M7 byte-identical, the 40-turn baseline
re-recorded consciously (§ above), no new `.gd` touches this round.
