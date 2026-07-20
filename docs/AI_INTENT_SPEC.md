# AI Intent — Phase Spec (v0.1, intent-focused)

> **Status:** DRAFT, awaiting a user design gate. Nothing here is built.
> **Motivating evidence:** `docs/audits/CREATIVE_AUDIT_2026_07_19.md` §2.1, §3, §7 + the AI
> decision-architecture map taken at `b4b6326` (cited inline throughout).
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
  pre-filtered to nations already at war, so the auto-declare seam in `combat_executor.py` is
  unreachable from an AI-issued attack.
- Agendas influence *target choice only*, downstream of the ratio/threshold gates — the code says so
  at `enemy_ai.py:2669` ("the ratio/threshold gates already ran").
- `ai_diplomacy.py:1070-1073` states the absence as a decision: *"no unilateral AI declare-war path
  in NA-5 — the coalition system remains the war-maker."*
- `declare_war` already pre-provisions `war_objective = "conquest"` for AI-vs-AI wars
  (`diplomacy.py:7577`), commented "WPS-A: future AI-AI/opportunistic wars". **Dead branch, no
  caller.** The seam was built and never connected.

And the war-maker that *does* exist is not a decision at all — it is a **global anti-France threat
scalar**. `form_coalition()` declares on behalf of a filtered list of nations, none of which
evaluated anything. The France-centricity is explicit in the code: the war-declaration threat bump
fires only when `aggressor == world.player_nation` (`diplomacy.py:7659`), and `hegemony_passive`
skips entirely when the hegemon is not the player (`coalition.py:1738`).

**The consequence, stated plainly:** Europe is not a continent of powers with interests. It is one
player and nineteen nations whose entire foreign policy is a posture toward that player. Five of ten
nations with authored decks boot at war with nobody, two of them holding *acquisitive* designs
(Prussia wants Hanover — adjacent, undefended; Sardinia wants Savoy restored) that they will hold,
unpursued, until the sun burns out.

That is why no formable ever fires. It is also why the world feels like a diorama.

---

## 1. Thesis

**Give every nation a will of its own, legible to the player, expressed in peace as well as war.**

A nation should want something, weigh what it is willing to pay for it, try the cheap instruments
first, and — when the design matters enough and the moment is right — go to war for it, against
whoever is in the way, including nations that are not France.

The player should be able to *see* this happening and *trade* on it: play the courts against each
other, buy off a design, arm someone else's grievance, or watch two rivals exhaust themselves while
France rearms. Today none of that is possible because there is nothing to play against.

---

## 2. Design principles

1. **GR5 — one executor, both sides.** Intent produces the *same* actions the player can take,
   through the *same* seams. An AI war declaration goes through `diplomacy.declare_war`, not a
   private path. If a behaviour cannot be expressed as an existing action, that is a signal the
   action is missing, not that intent needs a back door.
2. **GR6 — no LLM in the decision.** Intent is derived, deterministic, and testable. The LLM may
   *voice* an intent that was already decided; it may never choose one.
3. **Derived over serialized.** Intent is a *reading* of the world (agenda + situation + relations +
   force), recomputed and per-turn cached on the `get_active_nations()` idiom — like
   `get_active_agenda` and `get_imperial_grip` before it. Serialize only what genuinely cannot be
   re-derived (commitments made, cooldowns, grudges owed).
4. **Legibility is the feature, not the reporting of it.** An intent the player cannot perceive is
   indistinguishable from randomness. Every intent strong enough to move armies must be readable
   *before* it moves them (§4.6).
5. **Symmetry de-centres France.** Threat, coalitions, grudges and settlements must work between any
   two powers. Where a mechanic is currently France-literal, generalise it — the NA-3 paymaster
   generalisation (`get_paymaster_nation`) is the pattern to copy.
6. **Nothing new becomes mandatory.** Every mechanic boots dormant or neutral on the authored 1805
   opening; the historically-correct opening must not shift because the engine grew a new appetite.

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
  indifferent  →  ask       →  buy        →  align        →  coerce      →  fight
                (proposal)   (subsidy,    (alliance,     (ultimatum,   (declare war)
                             gift)         guarantee)     threat)
```

A nation only reaches `fight` after the cheaper rungs have been tried and failed, or are structurally
unavailable. This is the single most important behavioural claim in the spec: **war is the bottom of
a ladder, not a dice roll.** It also gives the player counter-play at every rung — a design you buy
off never becomes a war.

`weight` gates how far up the ladder a nation is willing to climb. A `guard_neutrality` design never
reaches `coerce`; a `survival` intent starts near the top.

---

## 4. Slices

Ordered so each lands standing on the previous one, and so the first two are playable and
falsifiable before anything can declare a war.

### AI-1 — The Intent Layer (read-only)

Build `backend/game_logic/intent.py`: one derivation chokepoint, `get_nation_intent(nation, world)`,
per-turn cached, invalidated on the same signals as the agenda cache. It reads the existing agenda
view, region control, relations, relative force, war state and grudges — and writes nothing.

Deliverable is a **pure reading of the world plus its legibility surfaces**: the Diplomatic Ledger
gains an Intent row per court, and Talleyrand can be asked about it. Zero behaviour change; the
player can now see what every nation wants and what it is currently prepared to pay.

*Why first:* it is falsifiable on its own (boot intents are pinnable against the authored 1805
opening), and it makes every later slice debuggable.

### AI-2 — Peacetime pursuit (the cheap rungs)

Wire `ask` / `buy` / `align` into `ai_diplomacy.process_diplomatic_phase` as intent-driven proposal
selection. Today rungs P3/P4/P7 fire on relation and threat scalars; they should fire on *what the
nation is trying to achieve*. Prussia wanting Hanover should be courting Hanover, subsidising a
claim, or seeking a guarantee against Austria — visibly, every turn, in the mailbox.

This alone converts five idle courts into active ones without a single new war, and gives the player
a peacetime diplomatic game to play.

*Includes:* generalising proposal targeting so an AI can propose to **another AI** and have it
resolve (today the interesting rungs are France-facing).

### AI-3 — The Decision for War (the missing first link)

The heart of the phase. A new rung — sited with the NA-5 ultimatum rung, which already computes most
of the preconditions and whose comment names this absence — that lets a nation with sufficient
`weight`, an exhausted ladder, favourable force, and a justification, call
`diplomacy.declare_war(...)` **for itself**.

Requirements that make it feel like history rather than chaos:
- **A stated reason.** The war carries its design as `war_objective` — the dead `"conquest"` default
  at `diplomacy.py:7577` finally gets a caller, and the reason is what the player reads and what the
  settlement layer scores. A war nobody can explain is a bug.
- **The ladder must have been climbed.** Declaration requires prior refused asks/coercion on record;
  no cold-open wars.
- **Restraint gates:** force ratio, treasury, existing war load, alliance webs, armistice cooldowns,
  and a world-wide cap on simultaneous AI-initiated wars so the map cannot dissolve.
- **Fore-warning.** The player learns a war is brewing before it lands (§4.6) — this is the
  difference between drama and a surprise diff.

### AI-4 — A continent, not a hub (de-France-centering)

Make the consequences of AI-vs-AI war real, by generalising three France-literal systems:

- **Threat** — `add_threat` and the `hegemony_passive` contributor are player-targeted
  (`coalition.py:1738`, `diplomacy.py:7659`). Threat should accrue *against whoever is behaving
  threateningly*, per the NA-3 court-relative hegemon resolution that already exists.
- **Coalitions** — `form_coalition` should be able to form against a non-player hegemon. A Europe
  that can coalesce against Austria is a Europe where France has options.
- **Settlements** — third-party wars must be able to end without the player, through the existing
  settlement package, and appear in the ledger as news.

This is where the world starts telling stories the player merely *witnesses* — the thing the audit
found completely absent.

### AI-5 — Intent into the existing systems

Intent is only worth building if it feeds what is already there. Each of these is a small wire, not
a new system:

| System | What intent unlocks |
|---|---|
| **NA formations** | A nation that *pursues* an acquisitive design can finish one. Poland, Italy and the Roman Republic become reachable without the player brokering them. |
| **Vassals** | Intent explains courting and defection pressure — a lord with a strong design is a lord worth following or worth leaving. |
| **Economy** | War Effort and subsidy flow with intent; the paymaster already generalises (`get_paymaster_nation`) and can now pay someone else's war. |
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

*Narration budget:* the audit found jealousy alone emitting 6–9 near-duplicate lines a turn. Intent
touches every nation, so it must ship with a per-turn cap per event family from day one, not after
the next audit says so.

### AI-V — Assurance and evaluation

- A both-sides pin set (the MC-V pattern): every intent kit exercised for an AI nation *and*
  reachable by the player's own systems.
- **The falsifying run:** the 40-turn AI-only simulation that produced `formations: NONE` and no
  agenda shift is the phase's acceptance test. It must produce AI-initiated wars with stated reasons,
  at least one completed design, and at least one third-party settlement — with the M1–M7 combat
  harness byte-identical and the authored 1805 opening unmoved.
- A live scored creative pass in the `docs/audits/` idiom.

---

## 5. What must not break

Pins to write before the first behaviour change:

1. **The 1805 opening is byte-identical at boot.** No nation acquires an appetite on turn 0.
2. **M1–M7 byte-identical** (`tests/test_combat_sweep_metrics.py`).
3. **The player is never a spectator.** AI-vs-AI war must not be able to resolve the campaign around
   France; the world-wide cap and the fore-warning surface are the guards.
4. **No unexplained war.** A declaration without a reason the player can read is a failing test, not
   a rough edge.
5. **The coalition remains a real threat.** Generalising threat must not defang the anti-France
   coalition, which is the campaign's central pressure. This is the highest-risk item in the phase
   and deserves its own before/after measurement.
6. **GR8** — intent is per-turn cached; no per-region scans in a hot path.
7. **Serialization discipline** — every new persisted field through `to_dict`/`from_dict` +
   `SAVE_FORMAT_REFERENCE.md`.

---

## 6. Open questions for the gate

These change what gets built and are **not** mine to decide:

1. **How much world-motion is wanted?** A Europe where three AI wars run in parallel is alive but
   noisy; one where a third-party war is a rare event is calmer but closer to today. This sets the
   simultaneous-war cap and most weight thresholds.
2. **Should AI wars be able to eliminate a nation, or change the map materially, without France?**
   The honest version says yes. The playable version may want a floor.
3. **Is France still the gravitational centre?** Generalising threat is the difference between "the
   coalition sometimes forms against someone else" and "France is one power among several." Both are
   defensible; they are different games.
4. **Ladder visibility — full or fogged?** Diplomacy currently has no fog
   ([[project_diplo_no_fog]]). Showing every court's exact price is legible; hiding some of it makes
   intelligence valuable. Recommend: want and target open, exact ladder rung softened by relations.
5. **Does the player get new counter-instruments** (buy off a design, guarantee a border, subsidise
   someone else's war), or only the existing verbs? Recommend: at least *buy off a design*, or AI-3
   is something done to the player rather than played against.
6. **Sequencing vs. Battle Diorama (ROADMAP row BD).** BD is queued next and is a contained visual
   slice; this phase is large. Recommend BD first as a palate cleanser, then AI-1/AI-2 as a
   playable increment before committing to AI-3.

---

## 7. Definition of done

- Every nation has a readable intent; the player can name what any court wants and what it will pay.
- Idle courts are visibly active in peacetime through existing diplomatic verbs.
- A nation can go to war for a stated reason, having first tried cheaper instruments, with the player
  fore-warned.
- Wars can happen, and end, between powers that are not France.
- At least one formable forms without the player brokering it.
- The 40-turn AI-only acceptance run is no longer static; the 1805 opening and M1–M7 are unmoved.
- Scored creative pass recorded in `docs/audits/`.

---

## 8. Owner rows (GR9)

| Row | Owner | Landing | Tracking |
|---|---|---|---|
| AI-1 Intent layer | this spec §4.1 | `intent.py` + ledger row | STATUS + `test_ai_intent_layer.py` |
| AI-2 Peacetime pursuit | §4.2 | `ai_diplomacy` rung rework | `test_ai_intent_peacetime.py` |
| AI-3 Decision for war | §4.3 | declare-war rung + objective | `test_ai_intent_war_decision.py` |
| AI-4 De-France-centering | §4.4 | threat/coalition/settlement generalisation | `test_ai_intent_third_party.py` |
| AI-5 System wiring | §4.5 | per-system wires | folded into the above |
| AI-6 Legibility | §4.6 | ledger/dispatch/Talleyrand + narration cap | `test_ai_intent_legibility.py` |
| AI-V Assurance | §4.7 | both-sides pins + 40-turn acceptance run | `test_ai_intent_assurance.py` |
| Economy re-measure | audit §5 | re-measure from an actively-spending run before tuning | carried here so it is not lost |

**Not in this phase, deliberately:** narrative/LLM-voiced diplomacy beyond existing register banks
(GR6); a new war-goal system beyond reusing `war_objective`; any rebalance of the anti-France
coalition beyond keeping it intact (§5.5).
