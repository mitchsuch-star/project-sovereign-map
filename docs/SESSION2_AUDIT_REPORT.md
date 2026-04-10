# Session 2 Audit Report: Diplomacy Interrupt Contract

**Date:** April 10, 2026
**Items:** PL-27 (FIXED), PL-34 (FIXED), PL-33 (CLOSED as duplicate)
**Tests:** 8110 -> 8151 (41 new, 0 regressions)

---

## Summary

Session 2 enforces the hard-stop vs soft-stop dialogue taxonomy so that incoming AI proposals no longer freeze all commands. Players can now issue orders while a proposal waits, respond to it later via the envoy badge, and see what proposals arrived, expired, or were dropped.

---

## Changes by File

### Backend

| File | Change | Lines |
|------|--------|-------|
| `backend/models/dialogue_manager.py` | Added type taxonomy constants (HARD_STOP_TYPES, SOFT_STOP_MAILBOX_TYPES, HYBRID_SOFT_STOP_TYPES, LOCAL_PLANNING_TYPES) and helper methods (is_hard_stop, is_soft_stop, is_local_planning, get_soft_stop_count) | +40 lines |
| `backend/commands/executor.py` | Changed dialogue guard from `pending_diplomatic_dialogue is not None` to `dialogue_manager.is_hard_stop()` | ~5 lines changed |
| `backend/main.py` | Split /command dialogue guard: hard-stop uses broad keyword matching, soft-stop matches only actual dialogue options and falls through to executor on no match. Fixed pending_envoy_count in 4 locations to include active soft-stop. Added GET /pending_envoy endpoint for envoy recovery | ~80 lines added/changed |
| `backend/game_logic/diplomatic_ledger.py` | Fixed pending_envoy_count to use authoritative formula | 3 lines |
| `backend/game_logic/ai_diplomacy.py` | Added campaign log events for proposal arrival, expiry, and overflow in _expire_queue, _enqueue_proposal, and deliver_ai_proposal | ~30 lines |
| `backend/campaign_log.py` | Added 3 event types (proposal_arrived, proposal_expired_unseen, proposal_dropped_overflow) with whitelist entries, category mappings, fog filter rules, and one-liner formatters | ~25 lines |

### Frontend (Godot)

| File | Change |
|------|--------|
| `godot-client/.../api_client.gd` | Added `get_pending_envoy()` GET endpoint caller |
| `godot-client/.../main.gd` | Replaced `_on_envoy_clicked()` text prefill with API call to `/pending_envoy` that reopens the proposal popup. Migrated `_on_incoming_proposal_choice()` from `send_command()` (synthesized English) to `send_dialogue_response()` (typed API) |

### Tests

| File | Change |
|------|--------|
| `tests/test_session2_bugfixes.py` | **NEW** — 32 tests covering taxonomy, guard split, envoy count, queue visibility events, PL-33 verification |
| `tests/test_audit_playtest.py` | Updated blocking test to use hard-stop type |
| `tests/test_audit_2_3.py` | Updated 3 blocking tests to use hard-stop types, added soft-stop pass-through test |
| `tests/test_audit_part1.py` | Updated blocking test to use hard-stop type |
| `tests/test_bugfix_popup_chain.py` | Updated 2 blocking tests to use hard-stop types, added soft-stop test |
| `tests/test_bugfix_session10.py` | Updated 2 blocking tests to use hard-stop types, added soft-stop test |
| `tests/test_campaign_log.py` | Updated type count assertion: 48 -> 51 |
| `tests/test_session_3_commands.py` | Updated blocking test to use hard-stop type, added soft-stop test |

### Docs

| File | Change |
|------|--------|
| `docs/STATUS.md` | Updated open count (7 -> 4), session status, test count |
| `docs/BUG_FIXES.md` | Marked PL-27/PL-34 FIXED, PL-33 CLOSED |
| `CLAUDE.md` | Updated bug count, dialogue state reference, troubleshooting entry |

---

## Dialogue Type Taxonomy

| Category | Types | Command Blocking |
|----------|-------|-----------------|
| **Hard-stop** | `force_declare_war_confirmation`, `alliance_paradox` | Blocks ALL commands |
| **Soft-stop mailbox** | `incoming_proposal`, `counter_offer`, `counter_offer_response`, `conflict_alert` | Allows pass-through |
| **Hybrid soft-stop** | `sabotage_confrontation`, `vassal_rebellion_imminent` | Allows pass-through (end_turn may warn) |
| **Local planning** | `proposal_confirm`, `advisory`, `mission`, `terms_guidance`, `ultimatum_demand_wizard`, etc. | Never blocks |

---

## Exit Criteria Verification

### PL-27 (FIXED)
- [x] Hard-stop vs soft-stop taxonomy enforced in both backend command paths
- [x] Incoming proposals, counter-offers, conflict alerts no longer freeze ordinary commands
- [x] Soft-stop has visible recovery surface via envoy badge + /pending_envoy endpoint
- [x] Pending envoy count includes active soft-stop + queued items
- [x] Envoy click opens recovery popup instead of prefilling terminal text
- [x] _on_incoming_proposal_choice uses typed dialogue response, not synthesized command
- [x] 32 regression tests covering all taxonomy paths

### PL-34 (FIXED)
- [x] Arrival events logged when proposals enqueue or deliver
- [x] Expiry events logged when proposals age out of queue
- [x] Overflow events logged when queue capacity exceeded
- [x] All 3 event types in campaign log whitelist with fog filter and one-liner format

### PL-33 (CLOSED as duplicate)
- [x] `status` works with no dialogue pending
- [x] `status` works with soft-stop dialogue pending
- [x] `status` blocked by hard-stop dialogue (intended)
- [x] `help` and `economy_report` verified under same matrix
- [x] No separate code shipped — PL-27 guard split resolved all symptoms

---

## Risk Areas for Auditor Review

1. **Soft-stop keyword matching in main.py**: For soft-stop dialogues, keyword routing now matches against actual dialogue option labels/actions instead of the global keyword list. This prevents "garrison" (a game command) from being misrouted to the dialogue handler when a proposal is pending. Auditor should verify edge cases with unusual command text.

2. **Envoy count formula**: All 4 locations (build_base_response, /command main path, /test endpoint, diplomatic_ledger) now use the same formula: `len(diplomatic_queue) + (1 if is_soft_stop() else 0)`. Auditor should verify these stay in sync after future changes.

3. **Campaign log event spam**: Proposal arrival events fire on both direct delivery AND enqueue. If a proposal is enqueued then delivered from queue, it gets one arrival event (at enqueue time) plus the existing dispatch/notification at delivery time. This is intended — the arrival event makes queued proposals visible immediately.

4. **Godot typed response migration**: Only `_on_incoming_proposal_choice` was migrated to typed responses. Other popup handlers (`_on_talleyrand_objection_choice`, etc.) still use `send_command()` fallbacks. These are lower-priority since they involve hard-stop dialogues where the old routing still works.

5. **end_turn with hybrid soft-stop**: The existing `_execute_end_turn` dialogue guard in meta_executor.py still checks `pending_diplomatic_dialogue is not None`, which blocks end_turn for ALL dialogue types including soft-stop. This is conservative behavior — the player is warned before losing a pending proposal to turn advance. Auditor should decide if hybrid soft-stop should auto-default on end_turn instead.
