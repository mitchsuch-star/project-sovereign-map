# MP v2.4.3 — Block 2: Substrate Alignment

> **Source:** 4 audit passes landed across [`MP_V243_AUDIT_COMBINED.md`](docs/audits/MP_V243_AUDIT_COMBINED.md) + [`MP_V243_AUDIT_PASS4.md`](docs/audits/MP_V243_AUDIT_PASS4.md) + two follow-up passes (commits c88b013, 5fcc93c). This work order integrates all code/test findings as first-class items — no addendum sectioning.
>
> **Ships as:** 3-4 focused commits organized by severity boundary. Order: BLOCKER/HIGH (P1, P3, P2, T4) → MAJOR substrate (U4, U3, U2+extensions, P6) → MINOR cleanup (B4, P5) → test sweep (T1, T10).
>
> **Pre-merge gate for:** B-B4 (needs U3, P6). Unblocks B-Hegemony tests (needs U4 + B1). C-lite pre-work (needs U2 + P1 + P3 + P2 if B-B3 pulled forward).
>
> **Depends on:** Block 1 should land first so spec contracts these code changes match are current.
>
> **Total effort:** ~4-6 hours depending on whether U2 (B-B3 rename) is pulled forward into this block.

---

## Scope summary

| Severity | Count | Dimension |
|----------|-------|-----------|
| BLOCKER | 1 | P1 — PopupQueue registry hardcode blocks post-rename delivery |
| HIGH | 3 | P3 half-migration, P2 dialogue_manager state, T4 round-trip tests |
| HIGH (out-of-scope) | 1 | T8 composite floor untested — hand off to B-B1-lite + B-B4 |
| MAJOR | 6 | U4+B1, U3+T3, U2+B3+P4, P6 |
| MINOR | 7 | B2, B4, B5, P5, P7, T6+T7, T10 |

All items here are **code or test** changes, except T8's hand-off note (which goes into B-B1-lite and B-B4 plan entries via Block 1 item 21).

---

## BLOCKER

### 1. P1 — `cooldown_manager.py:144, 155` PopupQueue hardcoded `alliance_paradox_popup`

[`backend/models/cooldown_manager.py:144, 155`](backend/models/cooldown_manager.py:144) — `PopupQueue.PRIORITY_ORDER` and `RESPONSE_KEYS` both list `"alliance_paradox_popup"` as the popup key.

**This is the actual delivery gate.** `main.py`'s `_include_popup_passthroughs` (via `build_base_response`) reads this registry to decide which popups to emit. Prior audits tracked `world.alliance_paradox_popup` attribute and the Godot scene only — the cooldown_manager registry was never sampled.

**Post-rename impact without fix:** Popup silently stops being delivered. `world.commitment_paradox_popup` is set, but PopupQueue doesn't know to look for it.

**Fix (fold into U2 commit):**
1. `PRIORITY_ORDER` line 144: rename key to `"commitment_paradox_popup"`; keep `"alliance_paradox_popup"` as a parallel entry for save-compat (read-only alias — if both are set on load, canonical wins).
2. `RESPONSE_KEYS` line 155: same dual-entry pattern.
3. Add a test asserting both keys resolve to the same popup slot (legacy alias contract).

**Verification:** `grep -n "alliance_paradox_popup" backend/` post-fix returns only alias-declaration sites.

---

## HIGH

### 2. P3 — `diplomatic_executor.py:2782, 2870` half-migration in live code

[`backend/commands/diplomatic_executor.py:2782, 2870`](backend/commands/diplomatic_executor.py:2782) — emits `"type": "commitment_paradox_resolved"` (new name) but clears `world.alliance_paradox_popup = None` (old attribute).

`campaign_log.py` already routes the new event-type at multiple sites (74/143/264/520/689). **Live code today is shipping a half-migration** — not just docs drift. Block 2's U2 rename must reconcile both sides.

**Fix (fold into U2 commit):** after U2 step 2 renames `world.alliance_paradox_popup` → `world.commitment_paradox_popup`, the clear-state writes at lines 2795, 2883 automatically update to the new attribute name via the rename. Add a unit test asserting `commitment_paradox_resolved` emission properly clears `commitment_paradox_popup`.

### 3. P2 — `dialogue_manager.py:49, 87` state inconsistent

[`backend/models/dialogue_manager.py:49, 87`](backend/models/dialogue_manager.py:49):
- Line 49 `HARD_STOP_TYPES` lists BOTH `"alliance_paradox"` and `"commitment_paradox"` (comment says transitional).
- Line 87 `DIALOGUE_PRIORITY` only maps `"alliance_paradox": 0`.

The rename is half-staged: hard-stop check passes for either name, but priority lookup for the new name returns the 99 default. Comment at lines 39-45 flags the transition plan; code never landed.

**Fix (fold into U2 commit):**
1. `DIALOGUE_PRIORITY` line 87: add `"commitment_paradox": 0` alongside the existing legacy entry.
2. Decision: keep or drop `"alliance_paradox"` in `HARD_STOP_TYPES`? Keep for legacy-save replay; add a comment: *"`alliance_paradox` kept as legacy alias; production emitters use `commitment_paradox`."*
3. Add tests: `DIALOGUE_PRIORITY["commitment_paradox"] == 0` AND `"commitment_paradox" in HARD_STOP_TYPES`.

### 4. T4 — `betrayal_history` / `next_episode_id` round-trip untested

[`tests/test_serialization_enforcement.py`](tests/test_serialization_enforcement.py) has zero matches for either field. Both are shipped v2.4.3 substrate; both serialize through `world_state.to_dict/from_dict` today ([world_state.py:3253-3272, 3578](backend/models/world_state.py:3253)); no round-trip test.

**Golden rule violated:** CLAUDE.md "Serialization Enforcement (MANDATORY)" — *"If it exists on the object, it must serialize."*

**Fix (fold into U2 commit or standalone "substrate test" commit):**
- Round-trip `betrayal_history` with a representative entry (actor, victim, turn, episode_id, type).
- Round-trip `next_episode_id` with a non-default value (e.g., 7) — verify monotonic counter survives.
- Round-trip legacy saves (missing keys) — confirm `.get()` defaults work.

**This is a pre-merge gate for U2**, because B-B3's alias-on-load extends the `from_dict` path. Without round-trip tests, the alias contract itself is untested.

### 5. T8 — Composite floor untested (out of Block 2 scope — handoff)

Full-suite grep for `composite_floor`, `grievance_modifier`, `grievance_floor`, `acceptance_floor`, `acceptance.*<=.*-` returns **zero matches** across `tests/`. Spec §9.3 authors a `-60` composite floor when DG-4's `grievance_modifier` is live. B-B1-lite flips the formula; B-B4 reintroduces the conditional floor. **Neither slice has a regression net today.**

**This is out of Block 2** (substrate-alignment only). Block 1 item 21 adds the following to B-B1-lite and B-B4 test budgets in the plan:
- **B-B1-lite:** 1-2 tests asserting composite score can go below -60 in the 3-term case when DG-4 is not live.
- **B-B4:** 2-3 tests asserting floor clamps at -60 for the 4-term case when `grievance_modifier` is live.

---

## MAJOR — substrate code

### 6. U4 + B1 — `rival_pressure` → `hegemony_pressure` + `unknown_baseline`

Spec [§964](docs/RELIABILITY_COMMITMENTS_SPEC.md:964): v2.4.3 enum is `hegemony_pressure` + `unknown_baseline`; `concern_pressure` kept as read-alias.

**Fix (single commit):**

1. **[`backend/game_logic/diplomacy.py:1828-1829, 1858`](backend/game_logic/diplomacy.py:1828)** — all three emit sites currently return `"rival_pressure"`.
   - Line 1828-1829 have **both branches returning the same value** (P6 dead-conditional bug exposed). Pick one: threshold branch returns `"hegemony_pressure"`; else-branch returns `"unknown_baseline"`. The if-threshold becomes meaningful instead of decorative.
   - Line 1858: return `"hegemony_pressure"`.

2. **[`backend/display_names.py:344`](backend/display_names.py:344)** — update the enum family:
   ```python
   "hegemony_pressure": "hegemony pressure",
   "unknown_baseline": "unknown baseline",
   "rival_pressure": "hegemony pressure",  # legacy alias
   ```

3. **Tests:**
   - Threshold-branch test: high threat / multiple wars → `"hegemony_pressure"`.
   - Else-branch test: low threat / zero wars → `"unknown_baseline"`.
   - Display mapping test: all three enum values resolve to non-empty display.
   - Legacy-save deserialization test: `decision_reason == "rival_pressure"` still renders.

4. **Verification:** `grep -rn rival_pressure backend/ tests/` returns only test fixtures asserting alias behavior.

### 7. U3 + T3 — `french_breach` speaker_attribution + regression coverage

Spec [COMMITMENTS_PRESENTATION_SPEC.md:216, 403-413](docs/COMMITMENTS_PRESENTATION_SPEC.md:216): family=`french_breach` → `speaker="envoy"` → victim's named diplomat.

**Live code** ([`diplomacy.py:775-783`](backend/game_logic/diplomacy.py:775)) writes `"speaker_attribution": "foreign_office"` unconditionally. U3 rename + add payload + regression test.

**Fix (single commit):**

1. **[`diplomacy.py:775-783`](backend/game_logic/diplomacy.py:775)** — change literal to conditional:
   ```python
   speaker = "envoy" if end_reason_family == END_REASON_FAMILY_FRENCH_BREACH else "foreign_office"
   ...
   "speaker_attribution": speaker,
   ```
   Import `END_REASON_FAMILY_FRENCH_BREACH` from [`diplomacy.py:198-200`](backend/game_logic/diplomacy.py:198) if not already in scope (it's self-referential).

2. **Add `victim_nation` to payload** so the downstream resolver can pick the named diplomat.

3. **Do NOT touch** `hard_reject_posture_triggered` at 844-850, `hard_reject_posture_cleared` at 403-416 — those correctly use `foreign_office`.

4. **Stub central resolver** at `backend/game_logic/diplomatic_templates.py` or `speaker_resolver.py`:
   ```python
   def resolve_named_diplomat(speaker: str, nation: str) -> str:
       raise NotImplementedError("Wired in C-lite §13; see COMMITMENTS_PRESENTATION_SPEC §10.3")
   ```
   Stub only — full wire-up is C-lite.

5. **Tests (T3 coverage):**
   - `french_breach` emit path: `speaker_attribution == "envoy"`.
   - `obsolescence_or_external` / `counterparty_reversal`: `speaker_attribution == "foreign_office"`.
   - Payload includes `victim_nation` when family is `french_breach`.

6. **Verification:** `grep -n 'speaker_attribution' backend/game_logic/diplomacy.py` — line 783 conditional; lines 409, 416, 850, 859 literal `"foreign_office"`.

### 8. U2 + B3 + P4 — `commitment_paradox` rename

**Only land in Block 2 if B-B3 is the next coding slice.** Otherwise leave in B-B3 plan slot.

**Spec canonical** is `commitment_paradox` on `commitment_paradox_popup.{tscn,gd}` per [COMMITMENTS_PRESENTATION_SPEC.md:19, 45, 214](docs/COMMITMENTS_PRESENTATION_SPEC.md:19) (after Block 1 CR2 fix).

**Rename surfaces** (consolidated from U2 + B3 + P4):

| Surface | Files / sites | Action |
|---------|---------------|--------|
| Emitter type string | [diplomacy.py:2134-2135](backend/game_logic/diplomacy.py:2134) | Rename |
| WorldState attribute + serialization | [world_state.py:497, 668-673, 3271, 3578](backend/models/world_state.py:497) | Rename + alias-on-load |
| Dialogue manager push | [diplomacy.py:2134](backend/game_logic/diplomacy.py:2134) dict type | Rename (B3 extension) |
| Dialogue manager priority | [dialogue_manager.py:87](backend/models/dialogue_manager.py:87) | Add canonical entry, keep alias (P2 + B3) |
| Dialogue manager hard-stop | [dialogue_manager.py:49](backend/models/dialogue_manager.py:49) | Keep both (P2) |
| PopupQueue registry | [cooldown_manager.py:144, 155](backend/models/cooldown_manager.py:144) | Dual-entry (P1 — **BLOCKER**) |
| diplomatic_executor clear-state | [diplomatic_executor.py:2795, 2883](backend/commands/diplomatic_executor.py:2795) | Auto via attribute rename (P3) |
| Turn manager priority comment | [turn_manager.py:248](backend/game_logic/turn_manager.py:248) | Update comment |
| Turn manager clear-state | [turn_manager.py:358](backend/game_logic/turn_manager.py:358) | Auto via attribute rename (P4) |
| executor comment | [executor.py:450](backend/commands/executor.py:450) | Update comment (P5) |
| meta_executor comment | [meta_executor.py:115](backend/commands/meta_executor.py:115) | Update comment (P5) |
| Godot main.gd routing | [main.gd:100, 226-228, 726, 776-782, 2997](godot-client/project-sovereign/scripts/main.gd:100) | Rename |
| Godot popup scene | New `scenes/commitment_paradox_popup.tscn` | Create (copy from legacy) |
| Godot popup script | New `scripts/commitment_paradox_popup.gd` | Create (copy from legacy) |
| Save format doc | `SAVE_FORMAT_REFERENCE.md` | Block 1 item 5 covers alias policy |

**Step 1 — lock payload schema first:**

```python
{
    "episode_id": int,
    "primary_nation": str,
    "secondary_nation": str,
    "attacker": str,
    "defender": str,
    "ally": str,
    "attacker_preview": {...},
    "defender_preview": {...},
    "ally_preview": {...},
}
```

Reconcile today's payload at [`diplomacy.py:2123-2131`](backend/game_logic/diplomacy.py:2123) with this shape before renaming.

**Step 2 — backend rename:** rename emitter type string, WorldState attribute + serialization. `from_dict` keeps alias-on-load:
```python
world.commitment_paradox_popup = (
    data.get("commitment_paradox_popup")
    or data.get("alliance_paradox_popup")  # legacy v1.0 alias
)
```

**Step 3 — PopupQueue + dialogue_manager:** dual-entry for PopupQueue (P1); add canonical entry to DIALOGUE_PRIORITY (P2); keep HARD_STOP_TYPES as-is with dual entries.

**Step 4 — Godot:** create new scene + script; update main.gd routing; keep or delete legacy scene (grep first).

**Step 5 — comment rot:** update turn_manager:248, executor:450, meta_executor:115 comments (P5).

**Step 6 — tests (T1 + T6 + T7 + T10 sweep):**
- Round-trip both key names through to_dict/from_dict.
- `DIALOGUE_PRIORITY["commitment_paradox"] == 0`.
- `"commitment_paradox" in HARD_STOP_TYPES`.
- PopupQueue `PRIORITY_ORDER` + `RESPONSE_KEYS` both reference new name.
- Emitter `type` string is `"commitment_paradox"`.
- **T1 sweep:** for each of ~40 existing `"alliance_paradox"` test sites across `test_dialogue_manager.py:76,90,298,301,315,318,442,446,518`, `test_offer_lifetime.py:75,125,222,247,258,459,582`, `test_cooldown_popup_characterization.py:188,191,193`, `test_session_3_commands.py:365`, `test_audit_major_2026_03.py:471-478`, add a parallel `"commitment_paradox"` assertion.
- **T10 sweep:** for each of 5 audit-test files (`test_audit_part1.py:51,140`, `test_audit_playtest.py:179`, `test_audit_session4.py:135`, `test_audit_2_3.py:1348,1394`, `test_systems_audit_v2_session4.py:358,365`) add parallel canonical-name tests.
- **T7:** unit test exercising §7.5 opposition-graph paradox trigger path (the emitter at diplomacy.py:2123-2135 directly).

**Step 7 — verification:**
```bash
grep -rn alliance_paradox backend/ tests/ godot-client/
```
Expected: alias-on-load sites, PopupQueue dual-entries, test fixtures asserting alias, comment rot cleaned up. Production emit sites should all use `commitment_paradox`.

### 9. P6 — `diplomacy.py:1828-1829` dead conditional

See item 6 above — folded into U4 commit. The fix makes the if-threshold meaningful by returning different values in the two branches (`"hegemony_pressure"` vs `"unknown_baseline"`).

---

## MINOR — hygiene + tests

### 10. B2 — `END_REASON_FAMILY_FRENCH_BREACH` constant naming

Covered in item 7 step 1. Import by name, not string literal.

### 11. B4 — Campaign log dead-code cleanup

[`backend/campaign_log.py:504-518`](backend/campaign_log.py:504) vs `673-687`; `520-530` vs `689-692`. Each pair is a duplicate event-type branch. First return wins; second is dead code.

**Fix (standalone commit, not folded):**
1. Diff the two ranges of each pair to confirm identical output.
2. Delete the second occurrences (lines 673-687 and 689-692).
3. Run full test suite to confirm no test relies on the shadowed code.

Commit message: *"MP v2.4.3 Block 2 cleanup: remove duplicate campaign_log branches."*

### 12. B5 — Test count DoD

Updated in Definition of done below.

### 13. P5 — Comment rot cleanup

[`backend/commands/executor.py:450`](backend/commands/executor.py:450) + [`backend/commands/meta_executor.py:115`](backend/commands/meta_executor.py:115) — both hard-stop blocking comments name `alliance_paradox`. Code indirects through `HARD_STOP_TYPES`, so behavior is fine; comments rot after rename.

**Fix (fold into U2 commit):** update both comments to reference `commitment_paradox` with parenthetical `(alias: alliance_paradox)`.

### 14. P7 — AI proposal migration note

[`backend/game_logic/ai_diplomacy.py:746, 754, 768, 782, 814, 841`](backend/game_logic/ai_diplomacy.py:746) — threads `decision_reason` end-to-end. Values come from `determine_ai_offer_decision_reason` (fixed in item 6). After U4, in-flight proposals in saves carry legacy enum until turn flush.

**Fix (documentation only):** add a one-line comment at [ai_diplomacy.py:841](backend/game_logic/ai_diplomacy.py:841) where `decision_reason` is emitted into `log_event`: *"# decision_reason: v2.4.3 emits 'hegemony_pressure' / 'unknown_baseline'; legacy saves carry 'rival_pressure' until next turn flush."*

### 15. T6 + T7 — DIALOGUE_PRIORITY + paradox emission tests

T6 folded into item 3 (P2) tests. T7 folded into item 8 step 6 (U2 test sweep).

---

## Definition of done

### Minimum path (no U2 pull-forward)

- [ ] Items 6 (U4 + B1), 7 (U3 + T3), 11 (B4), 14 (P7 comment) landed.
- [ ] Test suite: **pre-existing count + 6-8 new** (U4+B1: 3-4, U3+T3: 2-3, B4: 0-1).
- [ ] `grep -rn rival_pressure backend/` returns no production-code hits (only test fixtures asserting alias).
- [ ] `grep -n "speaker_attribution" backend/game_logic/diplomacy.py` shows conditional at 783; `foreign_office` literal at 409/416/850/859.
- [ ] 2-3 commits landed: U4+B1 (+ P6 fix), U3+T3+B2, B4.

### Full path (U2 pulled forward for B-B3)

- [ ] All minimum-path items, plus:
- [ ] Items 1 (P1), 2 (P3), 3 (P2), 4 (T4), 8 (U2+B3+P4+P5+T1+T6+T7+T10) landed.
- [ ] Test suite: **pre-existing count + 23-31 new** (minimum: 6-8, plus U2 sweep: 15-20, T4: 2-3).
- [ ] `grep -rn alliance_paradox backend/ godot-client/` returns only alias-on-load sites, PopupQueue dual-entries, test fixtures, legacy Godot scene (if kept), and comment aliases.
- [ ] `commitment_paradox_popup.tscn` + `.gd` exist on disk.
- [ ] Round-trip save/load tests cover both canonical and legacy paradox popup keys.
- [ ] Round-trip save/load tests cover `betrayal_history` + `next_episode_id`.
- [ ] `DIALOGUE_PRIORITY["commitment_paradox"] == 0` asserted.
- [ ] PopupQueue `PRIORITY_ORDER` + `RESPONSE_KEYS` both reference `"commitment_paradox_popup"`.
- [ ] 4-5 commits landed: U4+B1, U3+T3+B2, U2+extensions, B4, (optional) substrate-tests.

## Out of scope

- Balance of Europe payload block in `build_diplomatic_ledger` (B-Hegemony + C-lite).
- `commitments_notice_*` template family (C-lite §13).
- `notification_bar.gd` icon map extension (C-lite §14).
- `resolve_named_diplomat` full wire-up (C-lite §13 — stubbed here only).
- Make Amends emitters + `reparations_cooldown` (B-B7).
- DG-4 call-to-arms emitters + `END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION` (B-B4).
- Composite floor tests (T8 — handed off to B-B1-lite + B-B4 via Block 1).
- Non-diplomacy-adjacent tests (`test_enemy_ai.py`, `test_turn_manager.py`, etc.) — confirmed clean by pass-4.
