# Claude Review Brief: Reliability + Commitments

> Use this as the opening packet for a mediated design review.
> Context: Session 8 renderer work is still waiting on art. Bug-fix diplomacy work is complete. This is the first post-fix diplomacy spec track.

---

## Ask

Please critique the current `v0.4` direction in `docs/RELIABILITY_COMMITMENTS_SPEC.md`.

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
- use a 2-level rivalry model for v0.1: `cold` / `active`, with two hardcoded Prussia-Saxony escalation triggers
- allow lower treaty coexistence across rivals, but force a ratification-time paradox check for `DEFENSIVE_ALLIANCE` / `ALLIANCE` (sibling to existing `alliance_paradox`, not an extension)
- make `territorial_promise` a tracked clause with `deadline_turn` + `suspended_turns` storage
- v0.1 promises are AI-requested and player-confirmed, not player-authored from scratch
- promise deadlines are AI-set, visible before acceptance, and suspend during direct war with the beneficiary
- fulfillment check: beneficiary controls region + France held alliance during promise window (passive control sufficient)
- renegotiation via typed command, available any time while promise is active, cheaper early
- Slice C includes a minimal AI promise stub in `generate_suggested_terms` so promises can exist before full Slice D AI

---

## Resolved Gates (v0.4)

The following questions were resolved during the v0.3 → v0.4 review. See §16 in the spec for full reasoning.

1. **Forced choice vs soft penalty** — forced choice for deep military alignment, soft penalty below
2. **Memory model split** — global reliability + bilateral betrayal confirmed as the right structure
3. **Renegotiation cost** — both relation (-5) and reliability (-3), no betrayal strike
4. **Deadline storage** — `deadline_turn` + `suspended_turns`, not `remaining_turns`
5. **Renegotiation entry point** — typed command, not ledger action
6. **Slice C AI stub** — yes, required for testability
7. **Passive allied control** — sufficient for v0.1 fulfillment
8. **Prussia-Saxony escalation** — two hardcoded triggers (war, vassalization), not full dynamic system

---

## Remaining Open Question

Should option 3 in the commitment paradox ("proceed at severe political cost") be available in v0.1, or should the paradox strictly force a choice between reject and downgrade?

---

## Where I Want Pushback

### 1. Promise lifecycle edge cases

The spec now covers treaty-break → promise-failure, suspension semantics, and renegotiation cost model. Are there remaining lifecycle gaps?

### 2. Acceptance formula growth

Four new modifiers grouped under a "political commitment" composite. Is the grouping right, or should some of these be folded into existing components?

### 3. Territorial promises scope

Still allowing 1-2 regions per promise package. Should v0.1 be narrowed to single-region only?

### 4. Commitment paradox — 2 options or 3?

Is a strict forced choice cleaner for v0.1, or does the "proceed at cost" option add meaningful player agency?

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
