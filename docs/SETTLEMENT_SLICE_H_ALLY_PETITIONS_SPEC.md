# Settlement Slice H: Full Ally Petition Substrate

> **Status:** ✅ **LANDED July 3, 2026** (approved v1.0 the same day — all five decisions D-H1..D-H5 as recommended in §9: D-H1 protected-set `{"player", "ally_petition"}`; D-H2 light refusal memory (−3 relation + decline record, no double penalty); D-H3 seat/consult floor with restoration exempt; D-H4 constants as stated; D-H5 honor = auto-adjust via restage, voiced). H-1 + H-2 shipped in one commit (the W1 three-place action-id sync forces backend dispatch, Godot whitelist, and harness ids to move together). Behavior suite: `tests/test_settlement_slice_h_ally_petitions.py` (22 tests); the two G2b absence pins INVERTED (`*_live_after_slice_h`); constants named in `SYSTEMS_REFERENCE.md` §25; voice families in `DIPLOMAT_VOICE_BIBLE.md` §16.1a. Landed deviation of record: candidate clauses carry NO `settlement_reason` key (the closed clause schema admits only `authored_by`; the petition's `basis` field carries the reason) and use the guided surface's `region`-singular shape.
> **Date:** July 2, 2026 (drafted) / July 3, 2026 (approved)
> **Owner rows:** SC-32 deferred sub-outcome (cleanup spec); the two absence pins `test_petition_request_reward_or_restoration_absent_until_slice_h_lands` + `test_petition_demand_bargain_honor_absent_until_slice_h_lands` (`tests/test_ally_settlement_petitions_g2b.py:426-431`) flip to positive when this lands; the DWL landing-ledger row (`tests/test_settlement_agency_landing_ledger.py:245-277`) updates in the same commit.
> **Companion docs:** `SETTLEMENT_UI_CLEANUP_SPEC.md` (v0.32), `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` (§13 term ownership, §14 reaction pass, §16.6 petition frame), `WAR_BARGAIN_SPEC.md` (landed v1.1), `RELIABILITY_COMMITMENTS_SPEC.md` (v2.4.3), `DIPLOMAT_VOICE_BIBLE.md` (§16.1a)
> **Design basis:** July 2, 2026 six-subsystem code recon (war bargains, commitments substrate, shipped G2b petitions, settlement authoring, contribution/restoration, voice/UI). Every reuse claim below was verified against live code at `1a9da53`.

---

## 1. Purpose

Give AI allies real skin in the player's peace settlements — the two full-agency petition types deliberately cut from G2-Slice-G2b:

- **`request_reward_or_restoration`** — an ally with standing or a restoration claim petitions for a concrete stake in the settlement being authored: return of its occupied home territory, or a coveted region / indemnity share earned by its war contribution.
- **`demand_bargain_honor`** — an ally holding a live war bargain with France petitions when the staged settlement would breach or silently ignore that promise, BEFORE ratification makes the breach real.

**Historical theme.** This is the compensation principle of Napoleonic diplomacy made playable: Bavaria expecting Tyrol at Pressburg for marching with France; Prussia demanding Hanover for its neutrality; every coalition court arriving at the peace table with a claims ledger. Allies who fought expect reward; allies who were promised expect delivery; and a France that pockets everything learns what Austria learned about unreliable patrons.

**Design center: the petitions are pressure, not co-authorship.** Per §16.6/§20.3 of the ally-participation spec, France (the side leader) owns the final settlement. A petition surfaces the ally's claim with a one-click way to honor it and a visible cost to refusing it. No veto, no hard stop, no conference.

## 2. What already exists (verified reuse map)

Slice H is unusual: **the enforcement layer is already landed.** What's missing is only the *petition surface* and the *grant affordance*.

| Need | Landed machinery (code-verified) |
|------|----------------------------------|
| Petition lifecycle (dialogue, dedupe, mailbox, notification, voice scaffold, ack dispatch) | `settlement_offers.py`: `queue_ally_settlement_petitions_for_player_action` (:617), `_queue_ally_settlement_petition` (:584), `build_ally_settlement_petition_dialogue` (:404), `handle_ally_settlement_petition_action` (:656), executor arm `diplomatic_executor.py:3095`, dtype `ally_settlement_petition` already whitelisted in Godot |
| "What does this ally want" | `_active_objective_claims_for_ally` (:212, from WPS `war_objectives`), `NATION_DESIRE_PROFILES.covets_regions`, lost-territory primitives (`world.nation_starting_regions` vs `get_nation_regions`) |
| "Is the ask already met" | `_settlement_terms_satisfy_ally_claim` (:264) |
| "Did this ally earn it" | `war_contribution.py` standing classifiers (`standing_for_participant` → seat/consult/beneficiary_only), `material_contribution_share` |
| Ally-directed reward clauses | Validator V2/V3 **already accept** `territory_cede from=<enemy> to=<ally>` (`settlement_validation.py:899`); ratify apply transfers to any `to` (`settlement_ratify.py:249-302`) and fires `allied_region_restored` +15 contribution for lawful restoration |
| Clause injection seam | `_restage_settlement_after_redraw` (`settlement_staging.py:1423`) — the same seam every guided demand verb rides; `settlement_demand_add` arm (`settlement_actions.py:1040-1360`) is the valid-by-construction clause factory (budget headroom, promised-region dedupe, cap check, voice beats) |
| Reward gratitude / shut-out teeth at ratify | `settlement_reactions.py`: `_is_named_beneficiary` → `ally_rewarded` gratitude memory; `settlement_shut_out` grievance for excluded contributors — **zero new enforcement code needed** |
| Bargain promise records + breach detection | `world.diplomatic_commitments` war-bargain lifecycle (`diplomacy.py:4841-5324`); settlement ratification **already auto-breaches** a live bargain whose claim region is awarded elsewhere (`settlement_reactions._evaluate_bargain_outcomes` :710) with −6 reliability / −10 relation / betrayal strike |
| Cooldown pattern | G1 `settlement_terms_requests` absolute `cooldown_until_turn` stamps + `ai_settlement_cooldowns` precedent |
| Voice | `settlement_ally_petition_{ptype}_{suffix}` template key scheme with named-diplomat suffix map + chancery fallback; `resolve_settlement_voice_line`; Talleyrand relay advisory |
| Terms preview inside a dialogue | `_term_display` bullet-list pattern (incoming-offer popup, `proposal_confirm_popup.gd:1434-1469`) |

**The genuinely new pieces are exactly four:** (1) two petition context finders, (2) a Grant affordance that routes the petition's pre-validated clause through the existing demand-add/restage machinery, (3) refusal memory + a petition cooldown store, (4) two voice families + a D5 copy check.

## 3. Petition type 1: `request_reward_or_restoration`

### 3.1 Trigger (extends the D7 solicited lock — no unsolicited firing)

Fires from the existing solicited trigger sites (`open_settlement`, `stage_settlement`) when ALL hold for a candidate ally:

1. Ally is an active same-side participant in the `war_instance` (never the player, never the covered enemies).
2. Ally has a basis, checked in priority order:
   - **Restoration basis** (strongest, always eligible regardless of standing): a region with `starting_controller == ally` currently controlled by a covered enemy court. *A court whose homeland is occupied may always ask.*
   - **Contribution basis**: standing `seat` or `consult` (`standing_for_participant`) AND an unsatisfied claim from `_active_objective_claims_for_ally` or a coveted region held by a covered enemy.
3. The staged terms do NOT already satisfy the claim (`_settlement_terms_satisfy_ally_claim`).
4. Not on petition cooldown for this (war, ally) pair (§6).
5. The candidate clause pre-validates (§3.2) — the petition NEVER asks for something the draft cannot legally hold (no-false-affordance, the G4F-16/G1 pattern).

### 3.2 Payload — a concrete, valid-by-construction candidate clause

The petition carries the exact clause Grant would inject, chosen at queue time:

- Restoration: `{"type": "territory_cede", "from": <covered enemy holding it>, "to": <ally>, "regions": [<ally's lost region>], "settlement_reason": "restoration"}`
- Reward: same shape with `settlement_reason: "contribution"`, region from claim/covet ranking; **gold fallback** (`gold_indemnity` to the ally within `compute_gold_payer_budgets` headroom) when no region candidate survives validation.

Pre-checks at queue time: V1 double-promise, `MAX_SETTLEMENT_CLAUSE_COUNT`, payer budget, V3 side partition (payer must be a covered enemy — France ceding its own soil to an ally is NOT expressible in the validator and stays out of scope, §8). The rendered dialogue shows the clause via `_term_display` plus the claim basis line (§13.4 rule: always name the basis — "Bavaria fought at Ulm" / "Hanover is Britain's occupation of their homeland").

### 3.3 Options

- **Grant** (`grant_ally_petition_clause`): injects the carried clause into the mounted PROPOSE draft through the `settlement_demand_add` machinery + `_restage_settlement_after_redraw` (re-validate, re-score all courts, persist scoped draft, voice beat). Because the PLAYER clicks Grant, the Slice-G player-only mutation boundary is preserved. If the draft changed since queue time and the clause no longer validates, Grant degrades to the refusal-free "no longer possible" re-check response (the G1 click-time affordance re-run pattern) — never a validator bounce.
- **Decline** (`decline_ally_petition`): records a `petition_declined` settlement memory (§5), starts the cooldown, removes the dialogue. Voiced acknowledgment by the ally's named diplomat (cool register).

No third option. Petitions stay advisory/non-blocking (never `HARD_STOP_TYPES`).

### 3.4 Consequences

- **Granted + ratified:** zero new code — the existing reactions pass fires `ally_rewarded` gratitude (+5 acceptance memory), restoration cessions accrue `allied_region_restored` +15 contribution to the ally, relation bonus per landed beneficiary rules.
- **Declined, then ally excluded at ratify:** the EXISTING `settlement_shut_out` grievance fires exactly as today. Slice H adds **no second penalty** — declining the ask is not the betrayal; concluding the peace without them is, and that teeth already exists. (Design choice D-H2.)
- **Declined:** immediate small relation dip only (−3, the advisory-tier consequence §16.6 authorizes), plus the decline memory feeding voice ("We asked once already, Sire").

## 4. Petition type 2: `demand_bargain_honor`

### 4.1 Trigger (solicited, `stage_settlement` only)

Fires when France stages settlement terms and `_get_live_bargains_by_promiser(world, "France")` holds a bargain (status `active`/`triggered`) whose beneficiary is a same-side participant in this war, AND the staged terms put the bargain at risk, detected by running the ALREADY-LANDED ratify-time predicates against the STAGED terms as a dry preview:

- **Imminent breach:** the claim region is awarded to a third party (`_evaluate_bargain_outcomes` breach predicate, `settlement_awarded_to_other`), or
- **Silent abandonment:** the settlement makes peace with the bargain's `target_enemy` while `_check_bargain_fulfillment` fails (France neither holds nor gains the claim region).

This is the settlement-table mirror of the landed E-2 mount-time `commitment_block_warning` honesty pattern: the game already punishes the breach at ratify — Slice H makes the ally SAY so while the player can still act.

### 4.2 Payload

Names the bargain verbatim (claim region, named enemy, `created_turn`, origin), the at-risk reason, and the exact consequence ladder the landed breach pipeline will apply (−6 reliability, −10 relation, +1 betrayal strike, 6-turn cooldown) — no invented numbers, read from the same constants `breach_bargain` uses.

### 4.3 Options

- **Honor the bargain** (`honor_bargain_in_settlement`): resolves the conflict in the draft via restage — removes/retargets the conflicting third-party award of the claim region (imminent-breach case) or injects `territory_cede from=<enemy> to=France, regions=[claim_region]` (abandonment case, subject to the same §3.2 pre-checks). Note the WB-v1 semantics: the bargain promises FRANCE's claim priority — honoring means France takes (or stops giving away) the claim region; it does not transfer land to the beneficiary.
- **Proceed regardless** (`decline_ally_petition`, shared handler): dialogue closes with the ally's named diplomat on the record; ratification then fires the EXISTING breach exactly as today. No double penalty — the petition is the warning, the breach is the teeth. (D-H2 again.)

### 4.4 Ratification interlock (the contract the DWL row demanded)

**The interlock is the landed `_evaluate_bargain_outcomes` call inside `route_settlement_reactions` at every ratification.** Slice H adds no second enforcement path; it adds visibility (the petition) and agency (one-click honor). The spec-level guarantee: a `demand_bargain_honor` petition MUST have fired (or been impossible per cooldown/dedupe) before any ratification that breaches a live bargain whose beneficiary is a same-side participant — pinned by a behavior test.

## 5. Memory & state (serialization-mandatory)

New serialized state, one field:

```python
world.ally_petition_state: Dict[str, Dict] = {}
# key: f"{war_id}|{ally}" → {"last_petition_turn": int, "cooldown_until_turn": int,
#                            "declined_types": [str], "granted_types": [str]}
```

- `to_dict`/`from_dict` (+ `.get()` default) + `SAVE_FORMAT_REFERENCE.md` row + serialization-enforcement test.
- Decline memories ride the EXISTING `_add_settlement_memory` typed store (`memory_type="petition_declined"`, expiring) — no parallel store (§17.1 rule).
- Petitions never write `betrayal_history` directly (D-H2): grievances remain owned by the ratify-time shut-out/breach pipelines.

## 6. Anti-spam / salience (per §16.6)

- Per-(war, ally) cooldown after ANY petition resolution: **5 turns** (matches `REQUEST_TERMS_COOLDOWN_TURNS`), absolute `cooldown_until_turn` stamps.
- At most **2** live ally-petition dialogues at once, salience-ordered: bargain-honor first (a promise at risk beats a new ask), then restoration, then reward; ties by `material_contribution_share`.
- The existing `petition_key` dedupe stays (covers re-staging the same unsatisfied claim while a petition is live).

## 7. Voice (Voice Bible §16.1a — extend before coding, per house rule)

- Two new families under the existing key scheme: `settlement_ally_petition_request_reward_or_restoration_{suffix}` and `settlement_ally_petition_demand_bargain_honor_{suffix}` — named diplomats (Castlereagh, Hardenberg, Metternich, Einsiedel) + chancery fallback, ally speaks, Talleyrand relays the advisory framing. Grant/decline acknowledgment lines per family.
- Registers: reward petition = formal claim with basis named; bargain-honor = wounded honor, the promise quoted ("At {created_turn_label}, Sire, France pledged its claim on {region} to secure our arms.").
- **D5 boundary:** no "conference"/"congress"/"veto" copy. The existing D5 auto-scan does NOT cover the `settlement_ally_petition_*` prefix — Slice H registers the prefix (or adds its own assertion) in the same commit.

## 8. Explicit non-goals (Golden Rule 9 dispositions)

- **France ceding its OWN territory to an ally** — not expressible under V3 side partitioning; stays out. If ever wanted, it is a validator rule change owned by a future spec, not this slice.
- **Ally-beneficiary war bargains ("Prussia gets Saxony")** — WB v1 is France-claim-scoped by design (`WAR_BARGAIN_SPEC.md` §5); Slice H honors that shape rather than extending it.
- **Unsolicited / turn-tick petitions** — D7 lock holds; any new trigger family is its own future spec (the D7 pins stay green).
- **`request_consultation` / `request_redress_after_settlement`** — remain CUT per SC-32 (terminal, no owner row needed).
- **AI-to-AI petitions** — AI leaders already run their own package construction (§16.5); no petition theater between AIs.

## 9. Open design decisions for the user gate

| ID | Question | Recommendation |
|----|----------|----------------|
| **D-H1** | Dial-sweep protection for granted clauses: the protection check is strict `authored_by == "player"` (`settlement_staging.py:950`), so a clause tagged `ally_petition` would be silently droppable by a More-Generous sweep — un-rewarding the ally with one click. | Tag granted clauses `authored_by="ally_petition"` AND extend the protection check to a protected-set `{"player", "ally_petition"}`. A granted promise should take a deliberate row-Remove to revoke (which then re-opens the petition surface after cooldown). |
| **D-H2** | Refusal teeth: immediate grievance flag vs light memory + existing ratify-time teeth. | Light memory (−3 relation, decline record). The landed shut-out grievance and bargain breach ALREADY punish the outcome at ratify; punishing the conversation would double-charge and discourage even opening the settlement table. |
| **D-H3** | Reward eligibility floor: standing `seat`/`consult` required for contribution-based asks? | Yes — but restoration basis is exempt (occupied-homeland courts may always petition). Mirrors §13.2's beneficiary rules exactly. |
| **D-H4** | Constants: 5-turn cooldown, max 2 live petitions, −3 decline relation dip. | As stated; all named in `SYSTEMS_REFERENCE.md` on landing. |
| **D-H5** | `honor_bargain_in_settlement` shape: auto-adjust the draft vs focus-only. | Auto-adjust via restage (remove/retarget the conflicting clause) with the change voiced — matches the one-click Ease/Drop holdout affordance pattern. Focus-only would re-create the G4F-5 dead-click class. |

## 10. Slice plan (post-gate)

- **H-1 (backend):** context finders + petition types registered + cooldown state + serialization + grant/decline/honor handlers through the demand-add/restage seam + the two absence tests inverted + ledger row updated. Behavior tests: petition fires on exact bases, never false-affordances, grant lands the clause and re-scores, decline records memory + cooldown, bargain petition precedes every would-breach ratification, D7 pins stay green, W1 three-place action-id sync.
- **H-2 (voice + Godot):** two template families + D5 prefix registration + petition popup content branch (terms preview via the incoming-offer bullet pattern) + campaign-log types (CAMPAIGN_LOG_TYPES count pins 90→+N) + parse-harness regeneration.
- Estimated size: comparable to G1 (the enforcement layer exists; this is surface + wiring).

## 11. Golden-rule compliance

- **Rule 5 (Building Blocks):** grant rides the same clause factory + restage seam as every player demand verb; no parallel authoring path.
- **Rule 6:** fully deterministic; LLM untouched.
- **Rule 8:** eligibility reads `war_instance` participants, live bargain indexes, and cached nation-region helpers — no `world.regions.values()` scans.
- **Rule 9:** every deferred/cut item above carries a disposition; the absence pins flip in the landing commit.
- **Serialization mandate:** §5 field ships with to_dict/from_dict + save-format row + enforcement test in H-1.
