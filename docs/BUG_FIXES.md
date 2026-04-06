# Bug Fixes

> **Consolidated bug tracker.** All open bugs from playtest reviews, audits, and design fixes live here.
> Iterate sessions until clean, then move to `DESIGN_REFINEMENT.md`.
>
> **Last Updated:** April 6, 2026

---

## Summary

| Priority | Count | Status |
|----------|-------|--------|
| P1 — MAJOR | 2 | PL-5, PL-6 OPEN |
| P2 — MINOR | 1 | PL-7 OPEN |
| **Total** | **3** | **3 open** |

**Prior bugs:** 28 bugs fixed across Sessions 1-6 (~163 tests). All P0/P1/P2/P3 resolved before these new findings.

---

## P1 — MAJOR

### PL-5: Player Proposal Resolves Next Turn — No Feedback, Race Condition
- **Source:** Playtest (Apr 6)
- **Summary:** Player sends a diplomatic proposal (e.g., non-aggression to Saxony). Gets "Expect a response by next turn." No indication of accept/reject until morning dispatch (easily missed). Meanwhile, the AI generates its OWN proposal of the same type on the same end-turn, creating a confusing race condition where Saxony rejects the player's harsh terms then immediately proposes a clean non-aggression pact.
- **Root cause:** `execute_proposal` (diplomatic_executor.py:895-994) sets `proposal_in_transit` and `talleyrand_state = "IN_TRANSIT"`. Resolution deferred to `_process_proposal_in_transit()` (world_state.py:4300-4493) which runs inside `advance_turn`. AI proposal generation (`ai_diplomacy.py` P4 check) also runs during `advance_turn` with no awareness that the player just proposed the same thing.
- **Sub-bugs:**
  - (a) No same-turn feedback: player can't tell if proposal was accepted or rejected until next turn's dispatch
  - (b) AI cooldown gap: when player's proposal is rejected, `player_proposal_cooldowns` blocks the *player* from re-proposing, but the AI's separate cooldown system (`_is_on_cooldown` in ai_diplomacy.py) is untouched — AI immediately re-proposes same type
  - (c) `accept_counter_offer` path (diplomatic_executor.py:1773) doesn't call `apply_acceptance_cooldown` — no cooldown after accepting counter-offers
- **Proposed fix:** Resolve player proposals instantly in `execute_proposal` instead of deferring to `advance_turn`. Extract resolution logic from `_process_proposal_in_transit` into a reusable `resolve_proposal_immediately()` method on WorldState. Exception: "stalled" sabotage (Talleyrand deliberately delayed delivery) still defers. Also apply AI cooldowns on player-proposal rejection. Also add `apply_acceptance_cooldown` to counter-offer acceptance.
- **Files:** `diplomatic_executor.py` (execute_proposal + send_override paths), `world_state.py` (new resolve method + _process_proposal_in_transit refactor)
- **Scope:** Large — changes core diplomacy flow. Needs design gate.
- **Est. Tests:** ~8 new + ~6 existing tests updated

### PL-6: "Harsher" Terms on Friendship Pacts Demand Territory — Nonsensical
- **Source:** Playtest (Apr 6)
- **Summary:** Player proposes non-aggression pact to friendly Saxony (OPEN_BORDERS state, positive relations). Clicks "harsher" twice. System demands 150g/turn gold AND 1 territory cession from Saxony — for a *non-aggression pact*. This is extortion, not diplomacy. Saxony reasonably rejects. Player perceives acceptance odds barely changing because demand impact is tiny relative to base disposition.
- **Root cause:** `modify_harsh` handler (diplomatic_executor.py:996-1060) is proposal-type-blind. It blindly adds `gold_per_turn` (100g) and `territory_cede` (1 region) regardless of whether the proposal is a war reparation or a friendship pact. The demand value rates in `DEMAND_VALUES` (diplomacy.py:158) are also weak: gold_per_turn = -0.02/gold (100g = -2 acceptance points), territory_cede = -5/region. Two rounds of escalation only subtract ~7 points from a base of ~40-50, which is barely perceptible.
- **Sub-bugs:**
  - (a) Type-blind escalation: territory demands make no thematic sense for non_aggression, open_borders, defensive_alliance, or alliance proposals
  - (b) Weak demand impact: 100g gold demand = -2 acceptance points. Player clicks "harsher" and sees acceptance barely move.
- **Proposed fix:** Split `modify_harsh` by proposal type category. War resolution (peace, armistice): keep current behavior — gold + territory demands are war reparations. Friendship types (non_aggression, open_borders, defensive_alliance, alliance): cap at modest gold demand (~100g), NO territory demands ever, cap at 1 round of escalation with message "A non-aggression pact cannot bear heavier demands, Sire." For war types, increase gold demand to 300g and territory to 2 so the impact is actually visible.
- **Files:** `diplomatic_executor.py` (modify_harsh handler ~line 996)
- **Est. Tests:** ~5

---

## P2 — MINOR

### PL-7: Counter-Offer Acceptance Missing AI Cooldown
- **Source:** Playtest (Apr 6)
- **Summary:** When player accepts an AI counter-offer via `accept_counter_offer` (diplomatic_executor.py:1773), no `apply_acceptance_cooldown` is called. The AI has no cooldown preventing it from immediately proposing the next upgrade type.
- **Root cause:** The `accept_ai_proposal` path (line 2163) correctly calls `apply_acceptance_cooldown(source_nation, world)`, but the `accept_counter_offer` path (line 1785) only calls `_ratify_treaty` without setting any AI cooldown.
- **Fix:** Add `apply_acceptance_cooldown(source_nation, world)` call in the `accept_counter_offer` handler after ratification.
- **Files:** `diplomatic_executor.py` (line ~1790)
- **Est. Tests:** ~2
