# DESIGN_REFINEMENT.md — archive, 2026 Q2

> **Moved verbatim from `docs/DESIGN_REFINEMENT.md` by CODE-4 "the docs diet" (October 9, 2026).** Every
> section here was dated before the current quarter and held no OPEN or PARTIAL
> row when it moved. `tools/defect_census.py` and `tools/fa_row_tally.py` read
> this file beside the live ledger, so every count is unchanged by the move;
> the doc pins in `tests/` read it through `tests/_ledgers.py`. A row that
> re-opens is moved BACK to the live ledger, never edited here.

---

## Focused Audit Validation (Apr 10, 2026)

The focused attention / AI diplomacy audit tightened which diplomacy legitimacy items are already justified, which ones need bug-fix prerequisites, and which old notes are now stale.

### Already justified by current evidence

- **R160: Nation Rivalry System** — confirmed as the highest-leverage legitimacy upgrade. Current diplomacy still lets France drift toward broad friendship without enough forced political choice. *(Since SUPERSEDED by Memory and Pressure v2.4.3 — see the R160 row below.)*
- **R155: AI Proposal Personality Voice** — needs to expand from flavor text into motive legibility. The audit confirmed that AI personality currently changes a few constants, but not enough of proposal timing, persistence, target choice, or player-facing explanation.
- **R156: Diplomacy Strategic Optionality** — confirmed. Proposals happen, but they do not create enough meaningful branching until rivalry / exclusion pressure exists.

### Prerequisites now satisfied (Apr 12)

- **R160 / R155 / R156** are no longer blocked by the old diplomacy contract prerequisites. `PL-27`, `PL-34`, and `PL-32` are closed, and the Envoys inbox / current-turn offer lifetime / typed popup-response foundations are live.
- **R162: AI Ultimatums to Player** no longer waits on the mailbox/recovery transport fix, but it remains intentionally sequenced after the stronger commitment and agenda specs.
- Presentation-only diplomacy polish should still follow the grouped spec work above, not precede it.

### Current legitimacy stack

- Completed foundation: Envoys inbox / same-turn offer lifetime / backend-owned display labels / typed response routing.
- `Reliability + Commitments`: make alliances politically costly, promises meaningful, and betrayal cumulative.
- `Bilateral Peace Hardening`: make separate peace and bilateral settlement review legible before multilateral settlement exists.
- `War Purpose + Score Semantics`: make wars resolve toward recognizable political outcomes instead of generic pressure alone.
- `Ally Participation + Common Peace`: active wartime settlement layer; implementation starts from `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice A.
- `Nation Agendas + Motive Legibility`: make AI motives and strategic branching legible to the player.

---
