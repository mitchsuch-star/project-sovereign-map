# Bugfix Plan: Proposal Flow — 4 Bugs + 2 Hardening Passes

**Status:** AWAITING APPROVAL — do not code until confirmed.
**Risk:** LOW (all changes additive, safe fallbacks, no refactoring)

---

## Principles

1. **Additive only** — no refactoring, no deleting existing code
2. **Safe fallbacks everywhere** — every `.get()` chain has a human-readable default string
3. **Defensive comments at every fix site** — explain WHY the guard exists
4. **Tests for every fix** — parametrized where possible
5. **No behavioral changes to working paths** — only fix broken ones

---

## Bug 1: Incoming proposal terms blank

**Root cause:** `deliver_ai_proposal()` in `ai_diplomacy.py:793-798` builds clauses only from demands/sweeteners using raw type keys (`"gold_per_turn"`, `"territory_cede"`). For proposal types with no demands/sweeteners (peace, non-aggression, armistice), the clause list is **genuinely empty**. Additionally, the safety valve at `main.py:193` hardcodes `"clauses": []`.

**Fix:**
- File: `backend/game_logic/ai_diplomacy.py`
- Always include the base proposal type description as the first clause (e.g. "Propose Peace Treaty")
- Translate demand/sweetener type keys to human-readable text using a display map (similar to `_format_proposal_summary` which already exists at line 826)
- Add comment: `# BUGFIX: Always include base proposal type as first clause — empty clauses cause blank popup in Godot`

**Exact change (ai_diplomacy.py ~line 793):**
```python
# BUGFIX: Always include base proposal type as first clause.
# Without this, peace/non-aggression/armistice proposals show blank
# popup in Godot because they have no demands or sweeteners.
_CLAUSE_TYPE_DISPLAY = {
    "gold_lump": "Gold payment",
    "gold_per_turn": "Gold per turn",
    "territory_cede": "Territory cession",
    "territory_return": "Territory return",
    "action_point": "Action point concession",
    "unit_trade": "Military units",
}
from backend.display_names import PROPOSAL_TYPE_DISPLAY
base_label = PROPOSAL_TYPE_DISPLAY.get(proposal_type, proposal_type.replace("_", " ").title())
clauses = [f"Proposal: {base_label}"]
for d in terms.get("demands", []):
    label = _CLAUSE_TYPE_DISPLAY.get(d.get("type", ""), d.get("type", "unknown"))
    clauses.append(f"Demand: {label} — {d.get('value', '')}")
for s in terms.get("sweeteners", []):
    label = _CLAUSE_TYPE_DISPLAY.get(s.get("type", ""), s.get("type", "unknown"))
    clauses.append(f"Offer: {label} — {s.get('value', '')}")
```

---

## Bug 2 & 3: acceptance_hint / rejection_hint show raw component keys

**Root cause:** `ai_diplomacy.py:803` builds factors as `{"reason": k, "value": v}` where `k` is the raw component key. Lines 809-810 set `acceptance_hint = positive_factors[0].get("reason")` — returns raw key like `"base_disposition"` instead of natural language.

`FEEDBACK_STRINGS` already exists at `diplomacy.py:136-189` with positive/negative natural-language entries for 13 component keys. The `_generate_feedback()` function and `_enrich_proposal_summary()` both use it correctly. Only `deliver_ai_proposal()` skips the translation.

**AUDIT FINDING: 3 missing keys in FEEDBACK_STRINGS.** `calculate_acceptance()` returns 16 component keys but `FEEDBACK_STRINGS` only covers 13. Missing:
- `military_supremacy` (binary +25 bonus)
- `battlefield_diplomacy` (+10 for decisive battles)
- `military_pressure` (scales with war score)

If any of these 3 is the best/worst factor, the hint silently falls back to empty string.

**Fix (two files):**

### A. Add 3 missing keys to FEEDBACK_STRINGS (`diplomacy.py:189`)
```python
# BUGFIX: These 3 keys are in calculate_acceptance() components but were
# missing from FEEDBACK_STRINGS, causing empty hint fallback.
"military_supremacy": {
    "negative": "their overwhelming military advantage",
    "positive": "our decisive military superiority",
},
"battlefield_diplomacy": {
    "negative": "recent battlefield setbacks",
    "positive": "our recent victories on the battlefield",
},
"military_pressure": {
    "negative": "the military balance favors them",
    "positive": "our military pressure on their borders",
},
```

### B. Translate hints in deliver_ai_proposal (`ai_diplomacy.py:809-810`)
```python
# BUGFIX: Translate component keys to human-readable strings.
# Raw keys like "base_disposition" must never reach the Godot popup.
# Pattern: match _enrich_proposal_summary() in diplomatic_dialogue.py:447.
from backend.display_names import FEEDBACK_STRINGS

if positive_factors:
    best_key = positive_factors[0].get("reason", "")
    acceptance_hint = FEEDBACK_STRINGS.get(best_key, {}).get(
        "positive", "complex diplomatic factors"
    )
else:
    acceptance_hint = "No strong positives identified"

if negative_factors:
    worst_key = negative_factors[0].get("reason", "")
    rejection_hint = FEEDBACK_STRINGS.get(worst_key, {}).get(
        "negative", "complex diplomatic factors"
    )
else:
    rejection_hint = "No major obstacles identified"
```

**Fallback guarantee:** Unknown keys → `"complex diplomatic factors"` (never raw key, never crash).

---

## Bug 4: "Harsher terms" / "More generous" / "Adjust terms" dead end

**Root cause — THREE issues that combine into dead-end trap:**

### Issue A: `terms_guidance` dtype not handled in Godot
- `main.gd:776` dtype list: `["proposal_confirm", "proposal_execute", "proposal_options", "mission", "feasibility", "advisory", "force_declare_war_confirmation", "conflict_alert"]`
- The `adjust_terms` flow in `executor.py` generates dialogues with `type: "terms_guidance"` (8 instances: lines 12251, 12287, 12334, 12370, 12395, 12929, 12957, 13017)
- Godot doesn't recognize `terms_guidance` → popup never shown → input stays disabled → player stuck

**Fix:** `main.gd:776` — add `"terms_guidance"` to dtype list. Add comment:
```gdscript
# BUGFIX: "terms_guidance" is generated by the adjust_terms flow in executor.py
# (8 instances). Without this, selecting "Adjust terms" causes a dead-end
# where the popup never shows and input stays disabled.
```

### Issue B: PEACE template + Fallback template missing modify options
- PEACE template (T6b) at `diplomatic_templates.py:214` only has: `execute_proposal`, `adjust_terms`, `reconsider`
- WAR template (T6) at line 176 has full set: `execute_proposal`, `modify_harsh`, `modify_generous`, `adjust_terms`, `reconsider`
- Fallback template at line 983 only has: `execute_proposal`, `reconsider`
- Most first proposals happen at PEACE → players only get "Adjust terms" → hits Issue A dead end

**Fix:** Add `modify_harsh` and `modify_generous` options to both PEACE template AND fallback template (matching WAR template format). Add comment:
```python
# BUGFIX: These options were missing from PEACE/fallback templates.
# Without them, peacetime proposals only offered "Adjust terms" which
# hit the terms_guidance dead-end in Godot. Must match WAR template (T6).
```

### Issue C: No iteration cap
- `modify_harsh`/`modify_generous` handlers at `executor.py:12072-12169` don't track iteration count
- Per `CONVERSATIONAL_DIPLOMACY_DESIGN.md` §9b: max 2 modifications, then remove option + Talleyrand cap message

**Fix:** `executor.py` — add `modify_count` to dialogue context dict, increment on each modify, remove harsh/generous options at cap with Talleyrand message.
```python
# BUGFIX: §9b iteration cap — max 2 modifications to prevent infinite loop.
# modify_count is carried in the dialogue context dict across round-trips.
context = dict(dialogue.get("context", {}))
modify_count = context.get("modify_count", 0) + 1
context["modify_count"] = modify_count

# At cap: remove self-referential option, add Talleyrand cap message
if modify_count >= 2:
    # Remove "Even harsher" / "Even more generous" from options
    # Add cap message to talleyrand_text per §9b
```

**Cap messages (from spec §9b):**
- Harsh cap: `"Sire, I cannot propose terms more severe than total subjugation. These are the harshest terms possible."`
- Generous cap: `"Sire, we are offering everything short of the crown itself. Any more and we negotiate from our knees."`

---

## Bug 5 (NEW): Popup passthrough gaps in response handlers

**Root cause:** 4 POST endpoints and 2 code paths in `/command` build response dicts but **never call `_include_popup_passthroughs()`**. Any diplomatic popup set on `world` during these handlers is silently lost and never reaches Godot.

**This is the RECURRING BUG PATTERN** — "conversational diplomacy not causing popups" keeps happening because new response paths get added without the passthrough call.

### Gaps found:

| # | Endpoint / Path | Line | Impact |
|---|----------------|------|--------|
| 1 | `/capture_choice` success | 1157 | Diplomatic popups lost after region capture |
| 2 | `/capture_choice` exception | 1162 | Same, on error path |
| 3 | `/respond_to_redemption` success | 1215 | Follow-up popups lost during redemption |
| 4 | `/respond_to_redemption` exception | 1233 | Same, on error path |
| 5 | `/respond_to_glorious_charge` success | 1307 | Combat consequence popups lost |
| 6 | `/respond_to_glorious_charge` exception | 1312 | Same, on error path |
| 7 | `/strategic_response` success | 1361 | Multi-popup scenarios broken |
| 8 | `/strategic_response` exception | 1366 | Same, on error path |
| 9 | `/command` interrupt route | 525 | Interrupt response popups lost |
| 10 | `/command` exception handler | 953 | Diagnostic popups lost on crash |

**Fix:** Add `_include_popup_passthroughs(response, world)` call before every `return` in these handlers. Add defensive comment block at the top of the function:

```python
# ════════════════════════════════════════════════════════════
# DEFENSIVE: Always call _include_popup_passthroughs() before returning.
# Diplomatic popups (coalition, sabotage, proposals, objections) can be
# set on world by ANY executor call. If we return without passing them
# through, the popup is silently lost and never reaches Godot.
# See BUGFIX_PLAN_PROPOSAL_FLOW.md Bug 5 for the recurring pattern.
# ════════════════════════════════════════════════════════════
```

**RISK: VERY LOW** — `_include_popup_passthroughs()` is already called in 12 places. It only ADDS keys to the response dict (never modifies existing keys). Godot already handles `None` values for all popup keys.

---

## Leak Fix: defiance_type raw key in notifications

- `dispatch.py:724` — notification text: `f"Talleyrand altered your proposal to {target} ({defiance_type})."` — raw strings like `"stalled"`, `"ap_downgrade"`
- `dispatch.py:733` — popup data includes raw `defiance_type`
- `dispatch.py:743` — dispatch event includes raw `defiance_type`

**Sabotage popup itself is CLEAN** — `sabotage_discovery_popup.gd` shows `ordered_summary` vs `delivered_summary`, not `defiance_type`. Verified.

**Fix:** Add display map in `dispatch.py`, translate before use:
```python
# BUGFIX: Translate raw defiance_type keys to human-readable strings.
# Raw keys like "ap_downgrade" and "stalled" must not reach the player.
DEFIANCE_TYPE_DISPLAY = {
    "stalled": "Delayed Delivery",
    "ap_downgrade": "Reduced Concessions",
    "unit_overpay": "Inflated Demands",
    "softened": "Softened Terms",
    "hardened": "Hardened Terms",
    "unknown": "Modified Terms",
}
display_type = DEFIANCE_TYPE_DISPLAY.get(defiance_type, "Modified Terms")
```

Use `display_type` in notification text (line 724) and dispatch event (line 743). The popup data at line 733 can keep raw `defiance_type` for backend use (Godot doesn't display it).

---

## Leak Fix: main.py safety valve empty clauses

- `main.py:193` hardcodes `"clauses": []` — always empty in the fallback path

**Fix:** Derive clauses from dialogue context proposal terms:
```python
# BUGFIX: Derive clauses from dialogue context instead of hardcoding [].
# Empty clauses cause blank popup in Godot incoming_proposal_popup.
proposal = context.get("proposal", {})
clauses = []
proposal_type = proposal.get("type", "unknown")
if proposal_type != "unknown":
    from backend.display_names import PROPOSAL_TYPE_DISPLAY
    base_label = PROPOSAL_TYPE_DISPLAY.get(proposal_type, proposal_type.replace("_", " ").title())
    clauses.append(f"Proposal: {base_label}")
for d in proposal.get("demands", []):
    clauses.append(f"Demand: {d.get('type', 'unknown')} — {d.get('value', '')}")
for s in proposal.get("sweeteners", []):
    clauses.append(f"Offer: {s.get('type', 'unknown')} — {s.get('value', '')}")
if not clauses:
    clauses = ["Diplomatic proposal"]  # Ultimate fallback — never empty
```

---

## Files to Modify

| # | File | Changes | Risk |
|---|------|---------|------|
| 1 | `backend/game_logic/diplomacy.py` | Add 3 missing FEEDBACK_STRINGS keys | TRIVIAL |
| 2 | `backend/game_logic/ai_diplomacy.py` | Bugs 1, 2, 3: clause display + hint translation | LOW |
| 3 | `backend/game_logic/diplomatic_templates.py` | Bug 4B: add modify options to PEACE + fallback templates | TRIVIAL |
| 4 | `godot-client/.../main.gd` | Bug 4A: add "terms_guidance" to dtype list | TRIVIAL |
| 5 | `backend/commands/executor.py` | Bug 4C: iteration cap tracking | LOW |
| 6 | `backend/main.py` | Bug 5: popup passthroughs + safety valve clauses | LOW |
| 7 | `backend/game_logic/dispatch.py` | Leak: defiance_type display map | TRIVIAL |
| 8 | `tests/test_bugfix_proposal_flow.py` | New test file | N/A |

---

## Implementation Order

**Phase 1: Data display fixes (safest — no flow changes)**
1. Add 3 missing FEEDBACK_STRINGS keys (`diplomacy.py`) — Bugs 2/3 completeness
2. Hint translation (`ai_diplomacy.py`) → fixes Bugs 2+3
3. Clause population (`ai_diplomacy.py`) → fixes Bug 1
4. defiance_type display map (`dispatch.py`) → fixes leak
5. Safety valve clauses (`main.py`) → fixes leak

**Phase 2: Flow fixes (slightly higher risk — changes dialogue routing)**
6. PEACE + fallback template options (`diplomatic_templates.py`) → fixes Bug 4B
7. `terms_guidance` dtype (`main.gd`) → fixes Bug 4A
8. Iteration cap (`executor.py`) → fixes Bug 4C

**Phase 3: Popup passthrough hardening (lowest risk — additive only)**
9. Add `_include_popup_passthroughs()` to all 10 gaps (`main.py`) → fixes Bug 5

**Phase 4: Validation**
10. Tests (`test_bugfix_proposal_flow.py`)
11. Full suite — zero regressions

---

## Tests to Write (`test_bugfix_proposal_flow.py`)

### Bugs 1-3: Hint + Clause translation
1. `test_acceptance_hint_no_raw_keys` — parametrized against ALL 16 component keys (including 3 new)
2. `test_rejection_hint_no_raw_keys` — same
3. `test_feedback_unknown_key_fallback` — unknown key → `"complex diplomatic factors"`, no exception
4. `test_all_component_keys_in_feedback_strings` — every key from `calculate_acceptance()` components exists in `FEEDBACK_STRINGS`
5. `test_incoming_proposal_clauses_nonempty` — clauses non-empty for any AI proposal (peace, non-aggression, armistice, alliance, trade)

### Bug 4: Template + dtype + iteration cap
6. `test_peace_template_has_modify_options` — T6b includes `modify_harsh` AND `modify_generous`
7. `test_fallback_template_has_modify_options` — fallback includes `modify_harsh`, `modify_generous`, `adjust_terms`
8. `test_modify_harsh_produces_proposal_confirm` — returns `diplomatic_dialogue` with `type: "proposal_confirm"`
9. `test_modify_generous_produces_proposal_confirm` — same
10. `test_modify_iteration_cap_harsh` — after 2 modifications, "Even harsher" option removed, cap message shown
11. `test_modify_iteration_cap_generous` — same for generous
12. `test_modify_count_persists_in_context` — context dict carries `modify_count` across iterations

### Bug 5: Popup passthrough coverage
13. `test_capture_choice_includes_popup_keys` — response has all 7 popup keys (even if None)
14. `test_redemption_includes_popup_keys` — same
15. `test_glorious_charge_includes_popup_keys` — same
16. `test_strategic_response_includes_popup_keys` — same

### Leak fixes
17. `test_defiance_type_display_all_types` — parametrized against all 5 defiance types + "unknown"
18. `test_safety_valve_clauses_nonempty` — main.py fallback path produces non-empty clauses

---

## Key Code References

| What | Where |
|------|-------|
| `FEEDBACK_STRINGS` (13 keys, needs 16) | `diplomacy.py:136-189` |
| `calculate_acceptance()` components (16 keys) | `diplomacy.py:748-765` |
| `deliver_ai_proposal()` (bugs 1-3) | `ai_diplomacy.py:713-823` |
| `_format_proposal_summary()` (reference pattern) | `ai_diplomacy.py:826` |
| `_enrich_proposal_summary()` (correct pattern) | `diplomatic_dialogue.py:384-475` |
| `PROPOSAL_TYPE_DISPLAY` (type→label map) | `diplomatic_dialogue.py` (top-level constant) |
| `modify_harsh` handler | `executor.py:12072-12119` |
| `modify_generous` handler | `executor.py:12121-12169` |
| `adjust_terms` handler | `executor.py:12204-12277` |
| WAR template T6 (has modify options) | `diplomatic_templates.py:176-209` |
| PEACE template T6b (missing modify) | `diplomatic_templates.py:214-237` |
| Fallback template (missing modify) | `diplomatic_templates.py:983-1001` |
| Godot dtype check | `main.gd:776` |
| Safety valve (empty clauses) | `main.py:188-197` |
| `_include_popup_passthroughs()` | `main.py:127-200` |
| `/capture_choice` (missing passthrough) | `main.py:1136-1166` |
| `/respond_to_redemption` (missing passthrough) | `main.py:1169-1237` |
| `/respond_to_glorious_charge` (missing passthrough) | `main.py:1266-1316` |
| `/strategic_response` (missing passthrough) | `main.py:1319-1370` |
| `/command` interrupt route (missing passthrough) | `main.py:513-525` |
| `/command` exception handler (missing passthrough) | `main.py:948-960` |
| defiance_type in notification | `dispatch.py:724` |
| defiance_type in popup data | `dispatch.py:733` |
| defiance_type in dispatch event | `dispatch.py:743` |
| sabotage_discovery_popup.gd (CLEAN — no defiance_type) | `sabotage_discovery_popup.gd:24-47` |
| §9b iteration cap spec | `CONVERSATIONAL_DIPLOMACY_DESIGN.md:1470-1480` |
| Defiance types (5 values) | `diplomatic_defiance.py:180-236` |

---

## Defensive Documentation to Add

### 1. Comment in `_include_popup_passthroughs()` header:
```python
# ════════════════════════════════════════════════════════════
# CRITICAL: Every response handler that returns a dict to Godot MUST
# call this function before returning. Diplomatic popups can be set on
# world by ANY executor call. Skipping this call silently loses popups.
#
# Known gap pattern: new POST endpoints get added without this call.
# If you add a new endpoint, add _include_popup_passthroughs(response, world)
# before the return statement. See Bug 5 in BUGFIX_PLAN_PROPOSAL_FLOW.md.
# ════════════════════════════════════════════════════════════
```

### 2. Comment in CLAUDE.md troubleshooting table:
```
| Popup not showing after endpoint | Every POST handler MUST call `_include_popup_passthroughs(response, world)` before returning — see main.py:127 |
```

### 3. Comment in CLAUDE.md "Adding a new popup/dialog" pattern:
Add a step: `5. Verify ALL response handlers in main.py call _include_popup_passthroughs()`

---

## Bug 6: Terms guidance action routing — Belgium/AP mismatch (FIXED)

**Root cause:** Godot popup (`_on_proposal_confirm_choice` in `main.gd`) sent actions via natural language through `/command`. When user clicked "Offer Action Points" (action=`territory_no_ap`):

1. `_ACTION_KEYWORD_MAP` didn't have `territory_no_ap` → fell back to raw action string
2. Command sent: `"Talleyrand, territory_no_ap the Prussia proposal"`
3. Backend `action_map` keyword matching: `"territory"` is a substring of `"territory_no_ap"` → matched `territory_yes`
4. **Resolved to Belgium suggestion instead of AP step**

Same bug affected ALL terms_guidance actions not in keyword map: `territory_no_gold`, `territory_no_ap`, `offer_region`, `skip_region`, `enough_territory`, `offer_gold`, `more_gold`, `less_gold`, `skip_gold`, `offer_ap`, `skip_ap`.

**Fix:** Direct action routing via `/respond_to_diplomatic_dialogue`:

1. Added `send_dialogue_response()` to `api_client.gd` — POSTs to `/respond_to_diplomatic_dialogue`
2. Rewrote `_on_proposal_confirm_choice` in `main.gd` to find the action's 1-based index in the options array and send it directly, bypassing all keyword matching
3. Old keyword path preserved as fallback for actions not found in options

**Files modified:**
- `godot-client/.../api_client.gd` — added `send_dialogue_response()` method
- `godot-client/.../main.gd` — rewrote `_on_proposal_confirm_choice` for direct routing
- `tests/test_bugfix_proposal_flow.py` — added Section 12 with routing tests

---

## What This Plan Does NOT Change

- No changes to combat, trust, disobedience, or turn processing
- No changes to AI decision tree
- No changes to save/load serialization (no new fields on model classes)
- No changes to existing working popup flows
- No changes to fog of war
- No refactoring of any kind

---

**Estimated risk:** LOW (additive guards, safe fallbacks, well-tested pattern)
**Estimated scope:** ~150 lines of changes across 7 files + ~200 lines of tests
