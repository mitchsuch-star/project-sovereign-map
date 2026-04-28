# War Settlement Ally Participation Implementation Plan

> **Status:** v1.0 READY FOR SLICE A
> **Last Updated:** April 28, 2026
> **Source spec:** `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.3

This plan is the coding handoff for Imperial Settlement / Ally Participation. It assumes BPH, WPS, and WB are landed and keeps the settlement system additive over pairwise `diplomatic_states`, `war_scores`, and WPS `war_objectives`.

## Scale Rules

- Target 13-20 active nations, 100+ regions, 78+ bilateral pairs, and 20 simultaneous pairwise wars.
- No settlement slice may add a per-turn scan of all regions for every war.
- Hot paths use active participants, direct term targets, direct beneficiaries, live bargain indexes, and affected regions only.
- Presentation emits one popup/rail beat per settlement family, not one per participant.

## Slice A - War Identity And Grouping

Files:
- `backend/models/world_state.py`
- `backend/game_logic/diplomacy.py`
- `backend/game_logic/war_status.py`
- `docs/SAVE_FORMAT_REFERENCE.md`
- `tests/test_war_settlement_instances.py`

Build:
- Add `world.war_instances: Dict[str, Dict] = {}` with save/load defaults.
- Create a `war_id` when a pair enters `WAR`; attach pairwise keys under `objective_keys`.
- Store side leaders, participants, `participant_meta`, active episode ids, and re-entry episode ids.
- Do not replace pairwise diplomacy. `war_instance` groups existing pairs.

Gate:
- 28-34 focused tests.
- Old saves load with `{}`.
- Pairwise war declarations and cleanup still pass existing WPS/WB tests.

## Slice B - Contribution Tracker

Files:
- `backend/models/world_state.py`
- `backend/game_logic/diplomacy.py`
- `backend/game_logic/dispatch.py`
- `docs/SAVE_FORMAT_REFERENCE.md`
- `tests/test_war_contribution_scores.py`

Build:
- Add `world.war_contribution_scores: Dict[str, Dict[str, Dict[str, int]]] = {}`.
- Add battle attribution adapter using `battle_region`, then `location`, then `region`.
- Accrue battle, occupation, support, and staying-power buckets from events.
- Add `war_support_delivered` event ingestion with dedupe by `episode_id`.
- Apply material-contribution gate: staying power alone cannot create seat-level grievance or threshold dispatch.

Gate:
- 40-46 focused tests.
- Contribution accrual does not scan all regions per turn.
- Old battle records with only attacker/defender/location remain valid.

## Slice C - Common Peace Scoring And Term Legitimacy

Files:
- `backend/game_logic/diplomacy.py`
- `backend/game_logic/diplomatic_templates.py`
- `tests/test_common_peace_acceptance.py`
- `tests/test_settlement_term_legitimacy.py`

Build:
- Implement `compute_side_pressure_score(war_instance)`.
- Implement common-peace acceptance with the v1.3 constants table.
- Normalize territory terms to canonical `from` / `to`; accept `from_nation` / `to_nation` only at input boundaries.
- Enforce direct-score gates for burdened non-leader enemies.
- Implement pressure-basis warnings for unoccupied or barely fought regions.

Gate:
- 36-44 focused tests.
- Rejection feedback names the top two objectionable components.
- Existing bilateral peace acceptance remains unchanged.

## Slice D - Settlement Reaction Pass

Files:
- `backend/game_logic/diplomacy.py`
- `backend/game_logic/campaign_log.py`
- `backend/game_logic/coalition.py`
- `tests/test_settlement_reactions.py`

Build:
- Apply `settlement_shut_out` grievance flags through existing `betrayal_history`.
- Add `settlement_memories` for `settlement_gratitude`, `sold_out_by_war_leader`, and `settlement_context`.
- Wire War Bargain fulfillment/breach through existing WB-B lifecycle helpers.
- Implement `compute_local_balance_warning()` from live relation/bloc/adjacency/desire-profile data only.
- Trigger cross-war reaction checks only for affected participants and affected active wars.

Gate:
- 42-50 focused tests.
- No duplicate BPH-C separate-peace relation penalty.
- Balance of Europe beats fire only through existing threshold/hegemon-swap seams.

## Slice E - Presentation, Ledger, And Logs

Files:
- `backend/game_logic/dispatch.py`
- `backend/game_logic/campaign_log.py`
- `backend/game_logic/diplomatic_ledger.py`
- Godot settlement / ledger surfaces as needed
- `tests/test_settlement_presentation.py`

Build:
- Add settlement route metadata separate from commitment routes.
- Dispatch top three settlement beats plus one digest overflow line.
- Notification rail spotlights only major settlement outcomes.
- Campaign log emits one `settlement_summary` entry per common peace with structured `participant_reactions`.
- War status panel shows contribution share and standing with top-five default rows plus overflow.

Gate:
- 28-36 focused tests.
- Large 6+ participant settlement emits one campaign-log one-liner, not per-participant spam.
- Godot surfaces remain usable on the current 19-region map.

## Final Gate

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_war_settlement_instances.py tests/test_war_contribution_scores.py tests/test_common_peace_acceptance.py tests/test_settlement_reactions.py tests/test_settlement_presentation.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_war_objectives.py tests/test_wb_a_bargain_model.py tests/test_wb_b_lifecycle.py tests/test_wpsb_power_cap.py -q
.\.venv\Scripts\python.exe -m ruff check backend tests
```

Full-suite run is required before merging Slice E because it touches shared diplomacy, campaign log, dispatch, ledger, serialization, and Godot contracts.
