# Bugfix Plan: Proposal Flow — 4 Bugs

**Status:** AWAITING APPROVAL — do not code until confirmed.

---

## Bug 1: Incoming proposal terms blank

**Root cause:** `deliver_ai_proposal()` in `ai_diplomacy.py:793-798` builds clauses only from demands/sweeteners using raw type keys (`"gold_per_turn"`, `"territory_cede"`). For proposal types with no demands/sweeteners (peace, non-aggression, armistice), the clause list is **genuinely empty**. Additionally, the safety valve at `main.py:193` hardcodes `"clauses": []`.

**Fix:**
- File: `backend/game_logic/ai_diplomacy.py`
- Always include the base proposal type description as the first clause
- Translate demand/sweetener type keys to human-readable text using a display map (similar to `_format_proposal_summary` which already exists at line 826)
- File: `backend/main.py:193` — derive clauses from dialogue context terms instead of hardcoding empty list

---

## Bug 2 & 3: acceptance_hint / rejection_hint show raw component keys

**Root cause:** `ai_diplomacy.py:803` builds factors as `{"reason": k, "value": v}` where `k` is the raw component key. Lines 809-810 set `acceptance_hint = positive_factors[0].get("reason")` — returns raw key like `"base_disposition"` instead of natural language.

`FEEDBACK_STRINGS` already exists at `diplomacy.py:136-189` with positive/negative natural-language entries for all 14 component keys. The `_generate_feedback()` function and `_enrich_proposal_summary()` both use it correctly. Only `deliver_ai_proposal()` skips the translation.

**Fix:**
- File: `backend/game_logic/ai_diplomacy.py`
- Import `FEEDBACK_STRINGS` from `diplomacy.py`
- Translate: `FEEDBACK_STRINGS.get(key, {}).get("positive", "complex diplomatic factors")` for acceptance hint
- `.get("negative", "complex diplomatic factors")` for rejection hint
- Safe fallback for unknown keys — never raise, never return raw key

---

## Bug 4: "Harsher terms" / "More generous" / "Adjust terms" dead end

**Root cause — TWO issues:**

### Issue A: `terms_guidance` dtype not handled in Godot
- `main.gd:776` dtype list: `["proposal_confirm", "proposal_execute", "proposal_options", "mission", "feasibility", "advisory", "force_declare_war_confirmation", "conflict_alert"]`
- The `adjust_terms` flow in `executor.py` generates dialogues with `type: "terms_guidance"` (8 instances: lines 12251, 12287, 12334, 12370, 12395, 12929, 12957, 13017)
- Godot doesn't recognize `terms_guidance` → popup never shown → input stays disabled → player stuck

### Issue B: PEACE template missing modify options
- PEACE template (T6b) at `diplomatic_templates.py:214` only has: `execute_proposal`, `adjust_terms`, `reconsider`
- WAR template (T6) at line 176 has full set: `execute_proposal`, `modify_harsh`, `modify_generous`, `adjust_terms`, `reconsider`
- Most first proposals happen at PEACE → players only get "Adjust terms" → hits Issue A dead end

### Issue C: No iteration cap
- `modify_harsh`/`modify_generous` handlers at `executor.py:12072-12169` don't track iteration count
- Per `CONVERSATIONAL_DIPLOMACY_DESIGN.md` §9b: max 2 modifications, then remove option + Talleyrand cap message

**Fix:**
- `godot-client/.../main.gd:776` — add `"terms_guidance"` to dtype list
- `diplomatic_templates.py:214` — add `modify_harsh`/`modify_generous` options to PEACE template (T6b)
- `executor.py` — add `modify_count` to dialogue context dict, increment on each modify, remove harsh/generous options at cap with Talleyrand message

---

## Additional Leak Audit

### defiance_type raw key in notifications
- `dispatch.py:724` — notification text: `f"Talleyrand altered your proposal to {target} ({defiance_type})."` — raw strings like `"stalled"`, `"ap_downgrade"`
- `dispatch.py:733` — popup data includes raw `defiance_type`
- **Fix:** Add `DEFIANCE_TYPE_DISPLAY` map, translate before use

### Sabotage popup (Godot)
- `sabotage_discovery_popup.gd` does NOT display `defiance_type` directly — it shows `ordered_summary` vs `delivered_summary`. So the popup itself is clean.
- The leak is only in the notification text at `dispatch.py:724`.

### main.py safety valve
- `main.py:193` hardcodes `"clauses": []` — always empty in the fallback path
- **Fix:** derive clauses from dialogue context `proposal` terms

---

## Files to Modify

| # | File | Changes |
|---|------|---------|
| 1 | `backend/game_logic/ai_diplomacy.py` | Bugs 1, 2, 3: clause display names + hint translation |
| 2 | `backend/game_logic/diplomatic_templates.py` | Bug 4B: add modify_harsh/generous to PEACE template |
| 3 | `backend/commands/executor.py` | Bug 4C: iteration cap tracking |
| 4 | `backend/game_logic/dispatch.py` | Leak: defiance_type display map |
| 5 | `backend/main.py` | Leak: safety valve clause derivation |
| 6 | `godot-client/.../main.gd` | Bug 4A: add "terms_guidance" to dtype list |
| 7 | `tests/test_bugfix_proposal_flow.py` | New test file |

---

## Implementation Order

1. **Hint translation** (`ai_diplomacy.py`) → fixes Bugs 2+3
2. **Clause population** (`ai_diplomacy.py`) → fixes Bug 1
3. **PEACE template** (`diplomatic_templates.py`) → fixes Bug 4B
4. **terms_guidance dtype** (`main.gd`) → fixes Bug 4A
5. **Iteration cap** (`executor.py`) → fixes Bug 4C
6. **Safety valve clauses** (`main.py`) → fixes leak
7. **defiance_type display** (`dispatch.py`) → fixes leak
8. **Tests** (`test_bugfix_proposal_flow.py`)
9. **Full suite** — zero regressions

---

## Tests to Write (`test_bugfix_proposal_flow.py`)

1. `test_acceptance_hint_no_raw_keys` — parametrized against all 14 component keys
2. `test_rejection_hint_no_raw_keys` — same
3. `test_feedback_unknown_key_fallback` — unknown key → fallback string, no exception
4. `test_incoming_proposal_clauses_nonempty` — clauses non-empty for any AI proposal
5. `test_modify_harsh_produces_new_dialogue` — returns diplomatic_dialogue with type proposal_confirm
6. `test_modify_harsh_increases_harshness` — new dialogue harshness > original
7. `test_modify_generous_decreases_harshness` — new dialogue harshness < original
8. `test_modify_iteration_cap` — after max modifications, options removed
9. `test_defiance_type_display` — notification uses human-readable string
10. `test_peace_template_has_modify_options` — T6b includes modify_harsh/modify_generous

---

## Key Code References

| What | Where |
|------|-------|
| `FEEDBACK_STRINGS` (14 keys, pos/neg) | `diplomacy.py:136-189` |
| `deliver_ai_proposal()` (bugs 1-3) | `ai_diplomacy.py:713-823` |
| `_format_proposal_summary()` (reference) | `ai_diplomacy.py:826` |
| `_enrich_proposal_summary()` (correct pattern) | `diplomatic_dialogue.py:384-475` |
| `modify_harsh` handler | `executor.py:12072-12119` |
| `modify_generous` handler | `executor.py:12121-12169` |
| `adjust_terms` handler | `executor.py:12204-12277` |
| WAR template T6 (has modify options) | `diplomatic_templates.py:176-209` |
| PEACE template T6b (missing modify) | `diplomatic_templates.py:214-237` |
| Fallback template (missing modify) | `diplomatic_templates.py:983-1001` |
| Godot dtype check | `main.gd:776` |
| Safety valve (empty clauses) | `main.py:188-197` |
| defiance_type in notification | `dispatch.py:724` |
| §9b iteration cap spec | `CONVERSATIONAL_DIPLOMACY_DESIGN.md:1470-1480` |

**Estimated risk:** MEDIUM
