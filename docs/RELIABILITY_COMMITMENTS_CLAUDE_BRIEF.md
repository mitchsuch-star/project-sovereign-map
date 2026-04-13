# Claude Review Brief: Reliability + Commitments

> Use this as the opening packet for a mediated design review.
> Context: Session 8 renderer work is still waiting on art. Bug-fix diplomacy work is complete. This is the first post-fix diplomacy spec track.

---

## Ask

Please critique the current `v0.3` direction in `docs/RELIABILITY_COMMITMENTS_SPEC.md`.

I want pressure on structure and failure modes, not a re-opening of the old bug-transport work.

---

## Proposed Direction

The draft combines three items into one system:

1. Rivalries create political branching.
2. Betrayal creates durable memory.
3. Territorial promises become tracked obligations.

Current working choices:

- keep `diplomatic_reliability` as nation-level global reputation
- add bilateral betrayal memory for specific victim pairs
- use a 2-level rivalry model for v0.1: `cold` / `active`
- allow lower treaty coexistence across rivals, but force a ratification-time paradox check for `DEFENSIVE_ALLIANCE` / `ALLIANCE`
- make `territorial_promise` a tracked clause with deadline and failure consequences
- v0.1 promises are AI-requested and player-confirmed, not player-authored from scratch
- promise deadlines are AI-set, visible before acceptance, and suspend during direct war with the beneficiary

---

## Where I Want Pushback

### 1. Rivalry pressure

Is "forced choice for deep military alignment, soft pressure below that" the right line?

### 2. Memory model

Is global reliability + bilateral betrayal the right split, or is that overcomplicated / underpowered?

### 3. Territorial promises

Is the current limited-scope promise package right for the 19-region map, or should v0.1 be narrowed further to exact single-region obligations only?

### 4. Failure handling

Is the current renegotiation model humane enough, or does it still need a stronger grace path before hard betrayal?

### 5. Remaining friction

What still looks most likely to create implementation drag or player confusion in the current v0.3 scope?

---

## Constraints

- Do not turn this into the war-goals spec. That is item 2.
- Do not add a whole new diplomacy UI stack.
- Keep the first implementation readable on the 19-region map.
- Reuse current ledger / dispatch / proposal-preview surfaces.

---

## Preferred Response Format

1. Strongest part of the draft
2. Weakest part of the draft
3. Most likely player-facing failure mode
4. Most likely implementation hazard
5. Changes you would make before coding
