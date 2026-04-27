# Codex Audit: WB-D War Bargain Presentation Extension

Run this in your terminal after committing and pushing the WB-D branch:

```bash
claude -p "$(cat tools/codex_audit_wb_d.md)"
```

---

## Task

You are reviewing the WB-D (War Bargain Presentation Extension) implementation. This is a presentation-only pass that adds commitments routing, notifications, witness scope classification, voiced templates, and ledger badges for the existing war bargain mechanical system (WB-A/B/C).

## Files Changed

Check these files for correctness:

1. **`backend/game_logic/commitments_routing.py`** — 5 new route entries + 5 templates + `format_commitments_notice` bargain branches + counterparty breach override
2. **`backend/game_logic/diplomacy.py`** — `_get_bargain_witnesses()` now returns scope-classified list, `_emit_bargain_event()` emits notifications, `get_all_bargains_for_ledger()` includes completed bargains with badges
3. **`backend/notifications.py`** — 3 new constants (BARGAIN_FULFILLED, BARGAIN_BREACHED, BARGAIN_VOIDED)
4. **`backend/game_logic/diplomatic_ledger.py`** — Uses `get_all_bargains_for_ledger` instead of `get_live_bargains_for_ledger`
5. **`tests/test_wb_d_presentation.py`** — 29 tests covering all deliverables

## Audit Checklist

For each item, report PASS or FAIL with a one-line explanation:

### Routing Table
- [ ] All 5 bargain event types (`bargain_fulfilled`, `bargain_breached`, `bargain_voided`, `bargain_ratified`, `bargain_triggered`) have entries in `COMMITMENTS_ROUTES`
- [ ] Each route has: icon (starts with `icon_`), label, template (starts with `commitments_notice_`), speaker, review_target, review_label
- [ ] `bargain_breached` with `end_reason_family="counterparty_reversal"` uses the override route (NORMAL priority, talleyrand speaker)
- [ ] Priority assignments: fulfilled=HIGH, breached=CRITICAL (french_breach)/NORMAL (counterparty), voided=NORMAL, ratified=NORMAL, triggered=HIGH

### Templates
- [ ] `bargain_fulfilled` template includes Talleyrand-register language (urbane, aphoristic — "belief" coin)
- [ ] `bargain_breached` template uses `{injured_diplomat}` (resolved via Voice Bible) + scope-branched witness aside
- [ ] `bargain_voided` template includes a `void_reason_phrase` lookup for each void reason
- [ ] `bargain_ratified` and `bargain_triggered` use Talleyrand register ("Sire", "Permit me to observe")
- [ ] No modern jargon or game-mechanic language leaks into player-facing copy

### Witness Scope
- [ ] `_get_bargain_witnesses()` returns `List[Dict[str, str]]` with `nation` + `scope_reason` keys
- [ ] Uses existing `_classify_witness_scope()` (no duplicated logic)
- [ ] `_get_bargain_dominant_witness_scope()` follows the existing precedence: ally > rival > shared_enemy > region_observer
- [ ] `fulfillment_snapshot["witness_nations_at_fulfillment"]` now stores enriched witness format

### Notifications
- [ ] Terminal bargain states (fulfilled, breached, voided) emit notifications
- [ ] Notification priority matches routing table priority
- [ ] Notification uses `commitments_label`, `format_commitments_notice`, `commitments_notice_details`
- [ ] Non-terminal events (ratified, triggered) do NOT emit notifications (they're dispatch-only)

### Dispatch Integration
- [ ] Bargain events are now in `COMMITMENTS_ROUTES`, so `_format_dispatch_event_text()` routes them through `format_commitments_notice`
- [ ] Priority in `_build_diplomatic_events_section` uses `commitments_priority()` for bargain events
- [ ] `dispatch_vars` includes `dominant_witness_scope`, `injured_diplomat`, `review_nation`

### Response Routes
- [ ] `bargain_breached` (French fault) has `review_target = "diplomacy_wizard"` + `review_label = "Propose Redress"`
- [ ] `bargain_voided` and fulfilled have `review_target = "ledger_war_bargains"`
- [ ] `review_nation` is passed in dispatch vars so Godot can pre-fill the wizard

### Ledger Badges
- [ ] `get_all_bargains_for_ledger()` returns live + completed bargains
- [ ] Completed bargains have `badge` field: fulfilled="honoured", breached="broken", void="lapsed"
- [ ] Completed bargains include `ended_turn` and `end_reason` fields
- [ ] Live bargains do NOT have a `badge` field

### Golden Rules (CLAUDE.md)
- [ ] No per-region scans in hot paths (witness classification uses `get_active_nations()`)
- [ ] All numbers sent to Godot use `int()` wrapping
- [ ] No LLM dependency (templates are deterministic mock-mode safe)
- [ ] Single source of truth respected (modifiers in marshal.py only, routing in commitments_routing.py only)

### Tests
- [ ] Test file covers: routing completeness, template formatting, witness scope, notifications, dispatch, response routes, counterparty breach, ledger badges
- [ ] All tests pass: `".venv\Scripts\python.exe" -m pytest tests/test_wb_d_presentation.py -v`
- [ ] Full suite passes: `".venv\Scripts\python.exe" -m pytest tests/ --tb=no -q`

## How to Run

```bash
cd "C:\Users\User\PycharmProjects\project-sovereign-map"
".venv\Scripts\python.exe" -m pytest tests/test_wb_d_presentation.py -v
".venv\Scripts\python.exe" -m pytest tests/ --tb=no -q
```

## Expected Output

- 29 WB-D tests pass
- Full suite: 9272+ tests pass, 0 fail

## Report Format

After completing the audit, output a summary:

```
## WB-D Audit Results

PASS: X/Y checks
FAIL: Z checks (list each with one-line explanation)

### Issues Found (if any)
- [severity] file:line — description
```
