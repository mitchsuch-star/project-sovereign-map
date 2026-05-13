# Bilateral Peace Hardening Spec

> **Status:** Historical landed implementation reference v1.0
> **Date:** April 16, 2026
> **Phase placement:** Landed Peace Deals slice. After `Memory and Pressure`; parallel-safe with the landed `War Purpose + Score Semantics` slice; before the landed `War Bargains` slice.
> **Origin:** Identified in the April 10, 2026 focused audit as the second legitimacy-stack item: "make separate peace and bilateral settlement review legible before multilateral settlement exists."
> **Companion docs:** `DIPLOMACY_SPEC.md` (§5–§7 treaty/peace), `RELIABILITY_COMMITMENTS_SPEC.md` (substrate), `WAR_BARGAIN_SPEC.md` (depends on this spec — §2, §8.9.A, R4), `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` (active follow-up), `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` (landed, parallel)

---

## 1. Purpose

This spec hardens the bilateral peace flow so that every peace deal the player signs is **legible, previewable, and politically consequential** before any multilateral settlement or war-bargain mechanic exists.

Today, making peace is a treaty package like any other: the player offers terms, the acceptance formula decides, and the state transitions. What the player cannot see:

- which specific terms in the package change territory, alignment, or obligation
- what a separate peace costs politically with existing allies
- whether making peace contradicts a live commitment (bargain, paradox, bloc-opposition pressure)
- what the practical map-state outcome of the deal looks like before sending

This spec does not add new diplomatic verbs. It makes the existing bilateral peace flow show the player what they are actually doing — and what it will cost.

---

## 2. Problems To Solve

### P1. Peace terms lack explicit ownership

The current treaty package is a flat list of clauses. Territory cessions, gold transfers, and state changes all sit together with no clear "from whom → to whom" attribution. In a bilateral deal this is usually inferable, but it becomes ambiguous when vassal territory, allied commitments, or third-party consequences are involved.

### P2. Separate peace has no fallout preview

France can sign a bilateral peace with one war enemy while allies continue fighting. The current system processes this mechanically — no warning about ally reactions, no preview of strategic-order cancellations, no visibility into whether this peace undercuts an ally's war effort.

### P3. Peace proposals look identical to other proposals

The acceptance formula, the wizard flow, and the response format for a peace proposal are the same as for a trade upgrade or vassalage offer. Peace is the most politically charged decision in a war, and it should feel like one — the player should see the war context (war score, casualties, territory, objectives) at the moment of decision.

### P4. No promise-breach preview at the peace table

Once war bargains exist (WAR_BARGAIN_SPEC), France making peace with a named enemy may breach a live bargain. The current peace flow has no mechanism to surface that warning before the player sends. This spec must create the preview plumbing that war bargains plug into.

### P5. Armistice → Peace transition is mechanically invisible

The ARMISTICE → PEACE upgrade is a standard state transition, but it represents a political decision to end a war permanently. The player gets no summary of what they achieved in the war, what the war cost, and what the peace terms mean in context.

---

## 3. Goals

- Make every bilateral peace proposal show **explicit term ownership**: who gives, who receives, what changes on the map.
- Add a **peace preview panel** to the proposal flow that surfaces war context (war score, territory, battle record, objectives) alongside the terms being offered.
- Add a **separate-peace fallout preview** that warns when bilateral peace will anger allies, cancel strategic orders, or affect commitment-layer obligations.
- Create the **promise-breach warning plumbing** that WAR_BARGAIN_SPEC §8.9.A and §10.2 depend on — surfacing warnings when peace with a named enemy contradicts a live commitment.
- Add a **war outcome summary** on peace ratification: what France gained, lost, and what the political aftermath looks like.
- Keep the existing acceptance formula, wizard routing, and bilateral treaty mechanics intact — this is a legibility pass, not a mechanics rewrite.

---

## 4. Non-Goals

- No common peace, allied settlement, or conference-style spoils. Those belong to `Ally Participation + Common Peace` (queue item 4).
- No war objectives or ticking war score. Those belong to `War Purpose + Score Semantics` (queue item 3).
- No new acceptance formula components. The existing formula, including the v2.4.3 political subtotal (`hegemony_target_mod` + `bilateral_betrayal_mod` + `grievance_modifier`, clamped by the `-60` composite floor), is sufficient for bilateral peace.
- No ally beneficiaries on peace terms. Territory transfers in bilateral peace go to/from the two negotiating nations only.
- No new diplomatic actions or verbs. This spec makes the existing peace flow legible, not broader.
- No war-bargain lifecycle rules — this spec creates the warning surface; WAR_BARGAIN_SPEC owns the bargain state machine.

---

## 5. Design Principle

Peace hardening follows one rule:

**The player must be able to read the political cost of a peace deal before sending it.**

That means:

- every term in a peace package identifies who gives and who receives
- every peace proposal surfaces its war context (score, battles, territory)
- every separate peace warns about ally fallout
- every peace that contradicts a commitment warns before send
- the peace ratification moment shows a clear outcome summary

This is an information-architecture spec, not a new-mechanic spec. It makes the existing peace system honest.

---

## 6. System Overview

### 6.1 Peace proposal enrichment

The existing proposal flow (`diplomatic_executor.py` → `diplomatic_dialogue.py` → `diplomatic_templates.py`) constructs a treaty package from parsed clauses and evaluates it through the acceptance formula. This spec adds three enrichment layers to that flow for peace-class proposals:

1. **Term ownership annotation** — every clause in the package gets explicit `from_nation`, `to_nation`, `affected_regions`, and `term_type` fields
2. **War context snapshot** — a frozen snapshot of war state at proposal time, embedded in the proposal payload
3. **Fallout preview** — computed warnings about ally impact, commitment conflicts, and strategic-order cancellations

These enrichments attach to the proposal before the player sees the confirmation/review screen. They do not change the acceptance formula or the treaty ratification machinery.

### 6.2 Scope: which proposals get enrichment

Peace enrichment applies to proposals that **change a WAR or ARMISTICE state to a less hostile state**. Specifically:

- WAR → ARMISTICE (ceasefire)
- ARMISTICE → PEACE (formal peace)
- WAR → PEACE (fast-tracked peace, rare but legal through high war score)

Upgrade proposals between non-war states (PEACE → OPEN_BORDERS, etc.) do **not** get peace enrichment. Downgrade proposals (ALLIANCE → DEF_ALLIANCE, etc.) do **not** get peace enrichment — they already have commitment-layer warnings from Memory and Pressure.

### 6.3 Reused substrate

This spec builds on shipped infrastructure:

- `structured warnings[]` payload contract from Memory and Pressure — peace warnings use the same shape
- `commitment_paradox` machinery — peace proposals that create paradox conditions trigger the existing hard-stop
- `betrayal_history` / `bilateral_betrayal_mod` — visible in peace preview as context for why terms are harsh
- hegemony pressure / bloc geometry (`RELIABILITY_COMMITMENTS_SPEC.md` §7) — derived opposition signals visible in peace preview as context for third-party political cost
- `calculate_acceptance()` — unchanged; peace preview shows the formula breakdown per DIPLOMACY_SPEC §6f
- `build_base_response()` — peace ratification summary rides the existing popup/passthrough architecture

---

## 7. Term Ownership

### 7.1 Annotated clause model

Every clause in a peace proposal gets ownership fields:

```python
{
    "clause_type": "territory",
    "from_nation": "Prussia",
    "to_nation": "France",
    "regions": ["Rhineland"],
    "term_direction": "demand",      # "demand" | "concession" | "mutual"
    "sweetener_value": -12,
    "harshness_contribution": 0.4,
    "display_label": "Prussia cedes Rhineland to France"
}
```

Required ownership fields:

- `from_nation` — the nation giving something up
- `to_nation` — the nation receiving
- `regions` — affected regions (empty list for non-territorial clauses)
- `term_direction` — whether this clause is a demand on the target, a concession by the proposer, or mutual
- `display_label` — backend-generated human-readable sentence describing the term

### 7.2 Display label generation

Backend generates `display_label` for every clause. No raw clause types shown to the player.

Territory: "{from_nation} cedes {region_name} to {to_nation}"
Gold lump: "{from_nation} pays {amount} gold to {to_nation}"
Gold/turn: "{from_nation} pays {amount} gold per turn to {to_nation}"
Manpower: "{from_nation} transfers {amount} {unit_type} to {to_nation}"
Open borders: "Mutual open borders between {nation_a} and {nation_b}"
Military access: "{granting_nation} grants military access to {receiving_nation}"
Continental System: "{target_nation} closes ports to Britain"
AP/turn: "{from_nation} cedes {amount} AP per turn to {to_nation}"
Protection guarantee: "{guarantor} guarantees {target}'s sovereignty"

Vassal territory clauses include the vassal name: "France cedes Dresden (Saxon territory) to Prussia"

### 7.3 Existing clause wiring

The current `_ratify_treaty()` in `diplomacy.py` already processes clause types with implicit from/to based on the proposer/target pair. This spec makes that implicit ownership **explicit** by:

1. Annotating clauses at proposal-construction time (in `diplomatic_templates.py` or `diplomatic_executor.py`)
2. Carrying the annotations through the proposal payload to the confirmation screen
3. Using the annotations for display, warnings, and the ratification summary

The ratification machinery itself does not change — ownership annotation is a display/preview layer, not a new processing path.

---

## 8. Peace Preview Panel

### 8.1 War context snapshot

When the player opens a peace proposal (WAR/ARMISTICE → less hostile state), the proposal flow captures a war context snapshot:

```python
{
    "target_nation": "Prussia",
    "current_state": "WAR",
    "proposed_state": "PEACE",
    "war_score": 45,
    "war_score_components": {
        "territory": 20,
        "battle": 15,
        "decisive_battle": 10,
        "capital": 0,
        "ticking": 0
    },
    "war_duration_turns": 8,
    "battles_fought": 3,
    "battles_won": 2,
    "battles_lost": 1,
    "decisive_victories": 1,
    "decisive_defeats": 0,
    "french_casualties_total": 18000,
    "enemy_casualties_total": 31000,
    "regions_held_by_france": ["Rhineland"],          # enemy starting regions France holds
    "regions_held_by_enemy": [],                       # French starting regions enemy holds
    "france_relation": -45,
    "acceptance_preview": {
        "score": 52,
        "outcome": "ACCEPT",
        "largest_positive": "war_score_modifier",
        "largest_negative": "relation_modifier"
    }
}
```

The snapshot is frozen at proposal-construction time and does not update if game state changes before the player sends. This prevents the player from gaming the preview by modifying state mid-composition.

**WPS extension:** The landed `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` slice extends this snapshot with optional `war_objective`, `settlement_tier`, and ticking-score fields; see WPS §14.3 for the exact fields. Live war-score component readers should tolerate the fifth additive `ticking` component. Earlier BPH consumers must ignore unknown fields so WPS can extend the payload without a breaking migration.

### 8.2 Peace preview content

The preview shows three sections:

**Section 1 — War Summary:**
- War score and components (territory, battles, decisive, capital, ticking when WPS is live)
- Duration, battles won/lost, casualty totals
- Regions currently held by each side
- War score trend (rising/falling/stagnant based on last 3 turns)

**Section 2 — Terms Review:**
- Each clause with its `display_label` (from §7.2)
- Terms grouped by direction: "France demands" / "France concedes" / "Mutual"
- Acceptance preview: estimated outcome (ACCEPT / COUNTER / REJECT) and key formula drivers
- Harshness assessment: "generous" / "balanced" / "harsh" / "punitive" label

**Section 3 — Political Consequences:**
- Warnings from fallout preview (§9)
- Commitment conflicts (§10)
- Strategic order cancellations that will fire on ratification (per DIPLOMACY_SPEC §5b.4)

### 8.3 Preview routing

The peace preview panel is **not** a new screen or popup. It replaces the generic proposal confirmation step for peace-class proposals:

- Player opens diplomacy wizard → selects nation → selects peace/armistice
- Player constructs terms (existing clause-selection flow)
- **NEW:** Instead of generic "Send proposal?", the player sees the Peace Preview Panel with all three sections
- Player confirms send or backs out

Backend generates the preview payload as part of the `/diplomatic_preview` response. Godot renders it in the existing `diplomacy_wizard.gd` flow as an enriched confirmation step.

---

## 9. Separate-Peace Fallout Preview

### 9.1 When separate-peace warnings fire

Separate-peace warnings appear when France proposes peace with Nation X while:

- France has at least one ally (`DEFENSIVE_ALLIANCE` or `ALLIANCE`) that is also at war with Nation X
- France has a live commitment (bargain, once WAR_BARGAIN_SPEC ships) that involves Nation X as the named enemy
- France's strategic orders target Nation X's forces or territory

### 9.2 Ally fallout warnings

For each ally still fighting Nation X:

```python
{
    "warning_type": "separate_peace_ally",
    "ally": "Austria",
    "ally_state_vs_target": "WAR",
    "ally_war_score_vs_target": -15,
    "ally_relation_with_france": 32,
    "predicted_relation_change": -10,
    "severity": "MAJOR",
    "display": "Austria is still at war with Prussia (war score: -15). Making separate peace will anger Austria (-10 relation)."
}
```

Severity bands:

- `MINOR` — ally is also winning (war_score > 20) and has no commitment conflict → `-5` relation
- `MAJOR` — ally is neutral or losing (war_score ≤ 20) → `-10` relation
- `SEVERE` — ally has been fighting for 5+ turns and contributed materially (casualties > 5000 in this war) → `-15` relation and Talleyrand warning

### 9.3 Separate-peace relation penalty mechanics

On ratification of a separate peace:

- Each ally still fighting the target nation receives the predicted relation hit
- The penalty scales with the ally's investment in the war (duration and casualties)
- If the peace terms are generous to the enemy (harshness < 0.2), the penalty doubles for allies (France gave away what the alliance fought for)
- If the peace terms are harsh (harshness > 0.7), no additional ally penalty beyond the base (France extracted maximum value)

Penalty formula:

```python
base_penalty = -5
if ally_war_score_vs_target <= 20:
    base_penalty = -10
if ally_war_turns >= 5 and ally_casualties_in_war > 5000:
    base_penalty = -15
if harshness < 0.2:  # generous peace
    base_penalty *= 2
separate_peace_penalty = base_penalty
```

The penalty fires once on ratification. No per-turn decay needed — it's a one-time political cost applied to `nation_relations`.

### 9.4 Strategic order cancellation preview

Per DIPLOMACY_SPEC §5b.4, peace triggers auto-cancellation of military orders targeting the now-peaceful nation. The fallout preview lists which orders will be cancelled:

```python
{
    "warning_type": "order_cancellation",
    "orders": [
        {"marshal": "Ney", "order_type": "PURSUE", "target": "Blücher"},
        {"marshal": "Davout", "order_type": "MOVE_TO", "target": "Berlin"}
    ],
    "display": "Peace with Prussia will cancel Ney's pursuit of Blücher and Davout's march on Berlin."
}
```

This is informational only — the cancellations already happen mechanically. The spec makes them visible before the player commits.

---

## 10. Commitment Conflict Warnings

### 10.1 Warning plumbing contract

This section defines the interface that WAR_BARGAIN_SPEC §10.2 and future commitment systems plug into. The peace flow checks a `get_peace_commitment_conflicts(world, proposer, target, terms)` function and surfaces results as structured warnings.

v0.1 of this spec ships the plumbing with **two live conflict types** that exist today:

1. **Paradox conflict** — if making peace with Nation X while allied with a nation that has an active military or commitment conflict against Nation X would create a `commitment_paradox` condition
2. **Bloc-opposition conflict** — if making peace with Nation X while France and X sit on opposing sides of the hegemony/bloc geometry defined in `RELIABILITY_COMMITMENTS_SPEC.md` §7, and the bloc-share divergence exceeds the 30% threshold that activates `hegemony_target_mod`, surface the political context. This is derived from `_identify_max_bloc_share(world)` and bloc-membership checks, not from a stored rivalry table. It is an INFO warning, not a hard block.

### 10.2 Future conflict types (reserved interface)

When WAR_BARGAIN_SPEC ships, it plugs into the same interface with:

- **Bargain breach** — peace with the named enemy of a live bargain
- **Bargain void** — peace that destroys the claim basis of a live bargain
- **Peace-conflict warning** — normalization with named enemy after a surfaced warning (WAR_BARGAIN_SPEC §8.9.A)

The interface shape:

```python
def get_peace_commitment_conflicts(
    world, proposer: str, target: str, terms: List[Dict]
) -> List[Dict]:
    """Return structured warnings for commitment conflicts
    created by this peace proposal.

    Each warning:
    {
        "conflict_type": str,      # "paradox" | "bloc_opposition" | "bargain_breach" | ...
        "severity": str,           # "INFO" | "WARNING" | "HARD_STOP"
        "affected_entity": str,    # nation, bargain id, etc.
        "display": str,            # human-readable warning
        "detail": Dict,            # type-specific payload
    }
    """
```

HARD_STOP conflicts block the proposal until the player resolves the underlying contradiction (e.g., via the existing `commitment_paradox` popup). WARNING conflicts are surfaced but do not block. INFO conflicts provide political context.

### 10.3 Integration with existing warnings

Peace commitment conflicts merge with Memory and Pressure's `structured warnings[]` payload. The peace preview panel (§8) renders them in Section 3 alongside ally fallout and order cancellation warnings.

Warning priority order (highest first):

1. HARD_STOP — commitment paradox, impossible term combination
2. Bargain breach (WARNING, reserved for WAR_BARGAIN_SPEC)
3. Separate-peace ally fallout (WARNING)
4. Strategic order cancellation (INFO)
5. Bloc-opposition context (INFO)

Max 3 inline warnings in the preview; overflow behind "View all concerns" expander.

---

## 11. Peace Ratification Summary

### 11.1 War outcome summary

On successful peace ratification (acceptance score ≥ 50 or player accepts counter-offer), the response includes a war outcome summary:

```python
{
    "peace_ratification_summary": {
        "target_nation": "Prussia",
        "previous_state": "WAR",
        "new_state": "PEACE",
        "war_duration_turns": 8,
        "war_outcome": "french_victory",     # french_victory | enemy_victory | stalemate | white_peace
        "territory_gained": ["Rhineland"],
        "territory_lost": [],
        "gold_received": 500,
        "gold_paid": 0,
        "casualties_france": 18000,
        "casualties_enemy": 31000,
        "final_war_score": 45,
        "terms_ratified": [
            "Prussia cedes Rhineland to France",
            "Prussia pays 500 gold to France"
        ],
        "political_aftermath": [
            "Austria views this separate peace unfavorably (-10 relation)",
            "Ney's pursuit of Blücher has been cancelled"
        ]
    }
}
```

### 11.2 War outcome classification

```python
if war_score >= 30:
    war_outcome = "french_victory"
elif war_score <= -30:
    war_outcome = "enemy_victory"
elif any_territory_changed or any_gold_exchanged:
    war_outcome = "stalemate"     # compromised peace
else:
    war_outcome = "white_peace"   # status quo ante
```

### 11.3 Dispatch integration

The next turn's Morning Dispatch includes a peace settlement section when a peace was ratified the previous turn:

"The Treaty of [capital_of_target] — France and Prussia have concluded peace after [N] turns of war. France gained Rhineland. Final war score: +45."

This uses the existing `dispatch.py` builder and the `last_morning_dispatch` field on WorldState. No new dispatch infrastructure needed.

### 11.4 Campaign log event

New campaign log event type: `peace_ratified`

```python
{
    "type": "peace_ratified",
    "turn": 8,
    "target_nation": "Prussia",
    "war_outcome": "french_victory",
    "territory_gained": ["Rhineland"],
    "territory_lost": [],
    "final_war_score": 45,
    "war_duration_turns": 8,
    "terms_summary": ["Prussia cedes Rhineland", "Prussia pays 500 gold"]
}
```

Added to `CAMPAIGN_LOG_TYPES` in `campaign_log.py`. One-liner format: "Peace with Prussia (French victory) — gained Rhineland, +500 gold."

Fog rule: public to both nations in the peace and any allied witness of either party.

---

## 12. Armistice Hardening

### 12.1 Armistice as pre-peace

An armistice is not peace — it is a ceasefire with an expiration. The current system handles the mechanical differences (no trade, minimum duration, cooldown). This spec adds legibility:

**Armistice proposal preview** shows:
- Current war score and trend
- Minimum duration remaining before armistice can be broken
- Remaining active minimum-duration lock from `armistice_cooldowns`, if any; v0.1 has no separate post-break re-entry cooldown
- Predicted acceptance score for future PEACE proposal at current relation/war_score (informational projection, not a guarantee)

Implementation: compute the projection by calling `calculate_acceptance()` with `proposal_type='peace'` at the current bilateral state. Display it as an informational estimate, not a guaranteed future result.

**Armistice expiration warning** — 1 turn before armistice minimum expires, Morning Dispatch warns: "The armistice with [nation] expires next turn. Prepare for resumed hostilities or pursue peace."

### 12.2 DIPLOMACY_SPEC armistice duration resolution

DIPLOMACY_SPEC was internally inconsistent on armistice minimum duration: §5a/§5b.2/§7d said 5 turns, while the turn-order processing, EC-Z, and design decisions table still said 3 turns. `PEACE_DEALS_UMBRELLA_SPEC.md` §4.1 resolves this: **5 turns is canonical** and matches live code in `_process_armistice_expiration()`. This spec's armistice preview reads the canonical 5-turn value.

**Note:** WAR_BARGAIN_SPEC §R6 now uses the same resolved 5-turn value for its zombie-clock dependency. Both specs read the canonical armistice duration from the shared diplomacy model.

---

## 13. AI Behavior

### 13.1 AI peace proposal generation

AI peace proposals already use `calculate_acceptance()` and generate terms via `ai_diplomacy.py`. This spec adds:

- AI peace proposals include annotated terms (§7) — same ownership format as player proposals
- AI peace proposals include the war context snapshot (§8.1) in the response payload so the player sees war context when reviewing an AI offer
- AI counter-offers on peace proposals include updated term annotations

### 13.2 AI separate-peace awareness

AI nations already evaluate separate peace through war exhaustion and war score. This spec adds:

- When AI proposes separate peace to France, the proposal includes a fallout preview for France's allies (so the player can see consequences before accepting)
- AI nations that witness France making a separate peace with their war enemy apply the relation penalty from §9.3

### 13.3 AI does not change

No new AI decision logic. AI peace timing, war exhaustion thresholds, and acceptance formula are unchanged. This spec makes existing AI peace behavior more legible to the player, not smarter.

---

## 14. Data Model Additions

### 14.1 New fields

This slice adds one persistent WorldState field. All other peace preview data is computed on-the-fly from existing state and attached to proposal payloads as transient enrichment.

Persistent addition:

- `peace_ratification_log: List[Dict]` — stores the last 5 peace ratification summaries for dispatch/ledger reference. Capped to prevent unbounded growth. Each entry is the `peace_ratification_summary` shape from §11.1.

### 14.2 Serialization

- `peace_ratification_log` added to `WorldState.to_dict()` / `from_dict()` with `.get("peace_ratification_log", [])` default.
- Run `pytest tests/test_serialization_enforcement.py -v` after implementation.
- Update `docs/SAVE_FORMAT_REFERENCE.md`.

### 14.3 Endpoint changes

- `GET /diplomatic_preview` — extended response: when the previewed proposal is peace-class, include `war_context_snapshot`, `annotated_terms`, `fallout_warnings`, and `commitment_conflicts` in the response
- `POST /command` — peace ratification response includes `peace_ratification_summary` field
- No new endpoints

---

## 15. Player-Facing Surface Changes

### 15.1 Diplomacy wizard (peace proposals)

The existing `diplomacy_wizard.gd` confirmation step is replaced with the Peace Preview Panel (§8) for peace-class proposals. The panel has three sections (war summary, terms review, political consequences) rendered in the existing wizard area. Same Confirm/Back Out buttons.

### 15.2 Incoming AI peace proposals

When the player receives an AI peace proposal, the response popup includes the war context snapshot and annotated terms. The player sees the same legibility as their own proposals.

### 15.3 Diplomatic Ledger additions

The Diplomatic Ledger Treaties tab (Tab 2) shows recent peace ratifications:

- "Treaty of Berlin (Turn 8) — French victory, gained Rhineland, +500 gold"
- Clicking expands to full ratification summary

### 15.4 War Status Panel additions

The existing War Status Panel (`war_status_panel.gd`) and War Detail Popup (`war_detail_popup.gd`) are unchanged in structure. The peace preview references war status data but does not modify these panels.

---

## 16. Implementation Sequence

### Slice BPH-A: Term ownership + display labels (~15 tests)

- Add ownership fields to clause construction in `diplomatic_templates.py` / `diplomatic_executor.py`
- Generate `display_label` for every clause type (§7.2)
- Carry annotations through proposal payload to confirmation screen
- Godot: render annotated terms in wizard confirmation step
- Add `peace_ratified` campaign log event type
- Tests: clause annotation correctness, display label generation, all clause types covered

### Slice BPH-B: Peace preview panel + war context (~18 tests)

- Compute war context snapshot at proposal time (§8.1)
- Extend `GET /diplomatic_preview` with war context for peace-class proposals
- Godot: replace generic confirmation with Peace Preview Panel for peace proposals
- Three sections: war summary, terms review, political consequences (consequences empty until BPH-C)
- Acceptance preview in terms section
- Armistice preview additions (§12.1)
- Tests: snapshot correctness, preview routing (only peace-class), acceptance preview accuracy

### Slice BPH-C: Fallout preview + commitment conflicts (~20 tests)

- Compute separate-peace ally fallout warnings (§9)
- Implement `get_peace_commitment_conflicts()` interface with paradox + `bloc_opposition` conflict types (§10)
- Compute strategic order cancellation preview (§9.4)
- Wire warnings into Peace Preview Panel Section 3
- Apply separate-peace relation penalty on ratification (§9.3)
- Render up to 3 inline warnings with "View all concerns" overflow
- Tests: ally fallout calculation, severity bands, harshness scaling, paradox detection, order cancellation listing, penalty application on ratification

### Slice BPH-D: Ratification summary + dispatch (~12 tests)

- Generate `peace_ratification_summary` on successful ratification (§11)
- Add `peace_ratification_log` to WorldState with serialization (§14)
- Include summary in `/command` response for Godot rendering
- Add peace settlement section to Morning Dispatch (§11.3)
- AI peace proposal enrichment (§13)
- Armistice expiration dispatch warning (§12.1)
- Tests: summary generation, war outcome classification, dispatch content, AI proposal enrichment, serialization round-trip

**Total: ~65 tests, ~3 sessions**

---

## 17. Risks

### R1. Preview staleness

The war context snapshot is frozen at proposal-construction time. If the player takes actions between opening the wizard and sending the proposal, the preview may be stale. **Mitigation:** snapshot is informational, not contractual. The acceptance formula still evaluates on current state at send time. Add a small "Preview may not reflect recent changes" note if more than 0 turns pass between construction and send (though in practice, proposals are composed and sent within one turn).

### R2. Separate-peace penalty creates degenerate AI farming

If the player can predict the exact relation hit, they might game it by timing separate peace to minimize fallout (e.g., signing when ally relation is high enough to absorb the hit). **Mitigation:** this is desirable player behavior — thinking about political timing IS the game. The penalty is transparent by design.

### R3. Warning overload

If too many warnings fire (ally fallout + order cancellations + bloc-opposition + paradox), the preview becomes unreadable. **Mitigation:** max 3 inline warnings, priority-sorted (§10.3), overflow behind expander.

### R4. Term ownership ambiguity for mutual clauses

Open borders and military access have no clear "from/to" — they are mutual or one-directional. **Mitigation:** use `term_direction: "mutual"` for bilateral clauses and `from_nation/to_nation` for one-directional ones. Display labels handle the distinction (§7.2).

### R5. Dependency inversion with War Purpose spec

If `War Purpose + Score Semantics` ships first, peace proposals should reference war objectives in the preview. If this spec ships first, war objectives are absent from the preview. **Mitigation:** the war context snapshot (§8.1) has extensible fields. War objectives can be added as optional fields without changing the preview architecture. Implementation order does not create a conflict — whichever lands second extends the other.

---

## 18. Resolved Design Calls

- **Peace preview vs. new popup:** Preview is an enriched confirmation step in the existing wizard, not a separate popup. Keeps the flow count low.
- **Separate-peace penalty: flat vs. scaled:** Scaled by ally investment (duration + casualties + harshness). Flat penalties either punish too much (early separate peace when ally barely fought) or too little (late separate peace after ally bled for years).
- **Commitment conflict blocking:** Only HARD_STOP conflicts block. Everything else warns. The player should be able to make politically costly decisions knowingly, not be locked out of them.
- **Persistent peace log vs. transient:** Small persistent log (5 entries). Dispatch needs to reference last-turn's peace; ledger needs recent treaties. Fully transient would lose this data on the next turn.
- **AI peace enrichment:** Yes — AI proposals get the same term ownership and war context treatment. The player should have symmetric information whether they propose peace or receive a proposal.

---

## 19. Changelog

- **April 16, 2026** — v1.0 drafted. Covers term ownership, peace preview panel, separate-peace fallout, commitment conflict plumbing, ratification summary, armistice hardening. ~65 tests across 4 slices. References WAR_BARGAIN_SPEC §2/§8.9.A/§10.2/R4 dependency. Originally noted the DIPLOMACY_SPEC armistice duration mismatch; this is now resolved to 5 turns by PEACE_DEALS_UMBRELLA_SPEC §4.1.
