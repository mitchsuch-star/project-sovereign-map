# AI Intent — Phase Spec (v1.0, gate record)

> **Status:** **DESIGN GATE HELD July 20, 2026.** The six open questions of v0.1 are decided and
> recorded in **§6, which is authoritative**. Nothing is built yet; the build may begin against this
> document without a further gate, except where §6 names a re-check.
> **Motivating evidence:** `docs/audits/CREATIVE_AUDIT_2026_07_19.md` §2.1, §3, §7 + the AI
> decision-architecture map taken at `b4b6326`, **re-verified against master at `12636a6`** for this
> revision (§0.1 records two corrections the re-verification forced).
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

### 0.1 Two corrections from re-verification (v1.0)

v0.1 made two claims that did not survive a second pass. Both are recorded rather than quietly
edited, and **both change the build**.

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
  difference between drama and a surprise diff.

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

### AI-V — Assurance and evaluation

- A both-sides pin set (the MC-V pattern): every intent kit exercised for an AI nation *and*
  reachable by the player's own systems.
- **The falsifying run:** the 40-turn AI-only simulation that produced `formations: NONE` and no
  agenda shift is the phase's acceptance test. Acceptance numbers in §7.
- A live scored creative pass in the `docs/audits/` idiom.

---

## 5. What must not break

Pins to write before the first behaviour change:

1. **The 1805 opening is byte-identical at boot.** No nation acquires an appetite on turn 0.
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

---

## 6. Gate record — decisions (authoritative)

Held July 20, 2026. The six questions of v0.1 §6 are answered below. Where a decision names a
re-check, that re-check is the only remaining gate in the phase.

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

### D6 — Sequencing: **BD → AI-1 → AI-2 → re-check → AI-3 → AI-4 → AI-5/6 → AI-V.**

Battle Diorama (ROADMAP row BD) keeps its place first: it is contained, visual, already scoped, and
a deliberate palate cleanser between two large systems arcs.

Then **AI-1 + AI-2 + D5 ship as one playable increment** — a Europe that visibly wants things and can
be bargained with, with zero new wars. **Then a short re-check with the user before AI-3**, because
AI-3 is the only slice that can change the shape of the campaign, and because AI-1/AI-2 will have
produced the first real evidence about how much motion the world actually wants (D1's cap is the
thing most likely to need adjusting, and it will be adjustable from data instead of from argument).

AI-4's §4.4a migration may begin in parallel with AI-2 — it is a no-behaviour-change refactor with
its own byte-identical pin, and it is the phase's long pole.

---

## 7. Definition of done

- Every nation has a readable intent; the player can name what any court wants and what it will pay.
- Idle courts are visibly active in peacetime through existing diplomatic verbs.
- A nation can go to war for a stated reason, having first tried cheaper instruments, with the player
  fore-warned — through the existing `combat_executor.py:3482` declaration seam, with **no new
  PEACE→WAR edge in the codebase**.
- The player can buy off, aim, or deter a design (D5), and can be offered the same.
- Wars can happen, **and end**, between powers that are not France.
- **The 40-turn AI-only acceptance run** produces: ≥1 and ≤4 AI-initiated wars (D1), every one of
  them carrying a reason the ledger renders; ≥1 third-party settlement; ≥1 agenda shift; and **≥1
  formation, or a written explanation of the specific predicate that blocked it** (formation is the
  longest chain in the game and 40 turns may honestly be too short — an unexplained absence fails,
  an explained one does not).
- The 1805 opening is byte-identical, M1–M7 unmoved, and the pre/post anti-France threat series
  measured and reported (§5.5).
- Scored creative pass recorded in `docs/audits/`.

---

## 8. Owner rows (GR9)

| Row | Owner | Landing | Tracking |
|---|---|---|---|
| AI-0 Agenda-cache invalidation fix | §0.1 Correction D, §4.1 prerequisite | `_agenda_cache` wired into `invalidate_active_nations_cache` | `test_ai_intent_layer.py` (mid-turn refresh pin) |
| AI-1 Intent layer | §4.1 | `intent.py` + `build_intent_payload` + ledger row | STATUS + `test_ai_intent_layer.py` |
| AI-2 Peacetime pursuit | §4.2 | `ai_diplomacy` rung rework | `test_ai_intent_peacetime.py` |
| AI-2b Counter-instruments (D5) | §6 D5, §3.3 | compensation / sponsorship / guarantee through the wizard + settlement seams | `test_ai_intent_counterplay.py` |
| AI-3 Decision for war | §4.3 | war-intent marker + widened targeting into the existing declare seam | `test_ai_intent_war_decision.py` |
| AI-4a Threat migration | §4.4a | `threat_by_target` + `threat_level` property, byte-identical | `test_ai_intent_threat_migration.py` |
| AI-4b De-France-centering | §4.4 | targeted coalitions + third-party settlement | `test_ai_intent_third_party.py` |
| AI-5 System wiring | §4.5 | per-system wires (formations, vassals, econ/sponsor, jealousy proxy, NA-5, recruitment) | `test_ai_intent_system_wiring.py` |
| AI-6 Legibility | §4.6 | ledger/dispatch/Talleyrand + the 2-line narration cap | `test_ai_intent_legibility.py` |
| AI-V Assurance | §4.7 | both-sides pins + the 40-turn acceptance run | `test_ai_intent_assurance.py` |
| Economy re-measure | audit §5 | re-measure from an actively-spending run before tuning | carried here so it is not lost |

**Not in this phase, deliberately:** narrative/LLM-voiced diplomacy beyond existing register banks
(GR6); a new war-goal system beyond reusing `war_objective`; any rebalance of the anti-France
coalition beyond keeping it intact (§5.5); naval-dependent designs and the preventive-seizure war
(Copenhagen 1807) — that is a `deny_regions` fast-path that needs the DEF-5 naval layer to mean
anything, and it is homed there, not here.
