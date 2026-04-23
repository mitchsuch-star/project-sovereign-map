# B-B1-lite Audit Prompt (for a fresh agent)

Copy the prompt below into a fresh Claude Code session. It is self-contained — the auditing agent has no memory of the implementing conversation. The goal is an independent, read-only audit.

---

## Prompt

You are auditing the **B-B1-lite slice** of the Memory and Pressure v2.4.3 refactor in a Python/FastAPI Napoleonic diplomacy game at `C:\Users\User\PycharmProjects\project-sovereign-map`. The slice was just implemented and is suite-green (`8613 passed, 2 skipped`, was `8572`). Your job is to **audit it independently** against the specs and report findings. You are a **code reviewer**, not an implementer — do not write or edit code.

### What the slice is supposed to do

Per `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` §§190-215 and `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3 §§9.1-9.2 + §11.2:

1. Add `hegemony_target_mod(asker, target, world) -> int` — per-pair cross-bloc acceptance friction. Reads `_identify_max_bloc_share(world)` from `backend/game_logic/coalition.py`. Formula `max(-20, -int((share - 0.30) * 60))`. Gates: 0 when no hegemon, `share < 0.30`, asker not in hegemon's bloc, target in hegemon's bloc, `asker == target`.
2. Add `bilateral_betrayal_mod(asker, target, world) -> int` — `-6 * _get_active_betrayal_strike_count(world, asker, target)`. Flat, no cap.
3. Tighten `reliability_modifier` from `// 5` capped ±10 to `// 10` capped ±6.
4. Wire both new terms into `calculate_acceptance` sum + `components` dict + `_generate_feedback` trackable set.
5. Add a `hegemony` warning category to `build_proposal_commitment_warnings` with band-aware text (label-free 30-33%, descriptive 33-49%, proper noun 50%+), gated identically to the modifier.
6. Add FEEDBACK_STRINGS entries for both new keys.
7. 41 new tests in `tests/test_hegemony_acceptance.py` (plan budget was ~7-8 — the implementer counted a 4-assertion gate test as one test but pytest sees 4).

### Anti-scope (must NOT be in this slice)

- `grievance_modifier` — owned by B-B4
- Composite `-60` acceptance floor reintroduction — B-B4 (the plan's §9.3 merge gate)
- `alliance_paradox` → `commitment_paradox` rename — B-B3
- `make_amends` action — B-B7
- Balance-of-Europe ledger/headline payload or Nations tab per-row stamps — C-lite / D3
- Plumbing `commitment_event_metadata` into betrayal warning text — plan line 200 says cite referent "when available", implementer deferred citing because the strike schema doesn't carry named-nation/episode metadata. Verify this deferral is legitimate.

### Files changed

Run `git diff --stat` from the repo root to confirm scope. Expected:
- `backend/display_names.py` (+~8)
- `backend/game_logic/diplomacy.py` (+~180)
- `tests/test_da1_ai_intelligence.py` (+~17 — legacy test migration helper)
- `tests/test_phase4_batch3_features.py` (±24 — reliability tests updated to new `// 10` ±6 contract)
- `tests/test_session4_diplomacy.py` (+~15 — legacy test migration helper)
- `tests/test_hegemony_acceptance.py` (new file, 41 tests)

### What to check (in priority order)

**1. Spec compliance.** Read the key anchors and verify the implementation matches:
- `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` lines 190-215 (the B-B1-lite definition) + lines 387-398 (the merge gate with B-B4).
- `docs/RELIABILITY_COMMITMENTS_SPEC.md` §9.1 (`hegemony_target_mod` formula + gates) and §9.2 (`bilateral_betrayal_mod` + reliability narrowing).
- `docs/COMMITMENTS_PRESENTATION_SPEC.md` §8.1a (bloc-naming contract — label-free / descriptive / proper-noun bands) and §11.2 (warning payload).

Verify exactly:
- The 30% boundary returns 0 via integer truncation, NOT via an explicit guard. (Spec intent: 0.30→0 is the formula's floor; 0.29 also returns 0 but via the `share < 0.30` guard.)
- At 0.33 share, returns `-1` (because `-int(0.03 * 60) = -int(1.8) = -1`). At 0.3333…, returns `-2` (integer truncation at 2.0). The implementation must not round.
- Clamp kicks at `share >= ~0.6334` returning `-20`.
- `_get_active_betrayal_strike_count(world, actor, victim)` arg order is `(world, actor, victim)` — confirm `bilateral_betrayal_mod(asker, target, world)` calls it with `asker=actor, target=victim` (not swapped).
- `reliability_modifier` change is EXACTLY `max(-6, min(6, reliability // 10))` — not `// 6` or `± 10`.

**2. Merge gate compliance.** Per plan lines 387-398, B-B1-lite MUST NOT ship with unbounded negative composite scores. Since B-B4 is not yet landed, the no-composite-floor clause applies. Check that:
- No `-60` composite floor was introduced in this slice.
- An inline comment at the sum block (`calculate_acceptance` ~line 1693) cites B-B4 as the composite-floor owner so a future merge cannot forget it.
- The `grievance_modifier` term is NOT in `calculate_acceptance` (B-B4 owns it).

**3. Preview warning gate symmetry.** The plan warns that warning-without-modifier confuses players. Verify:
- `_build_hegemony_preview_warning` uses the same five gate conditions as `hegemony_target_mod` (asker/target same, no hegemon, share<0.30, asker not in bloc, target in bloc). Read both functions side-by-side.
- The warning reads `_hegemony_signal_band(share)` and `describe_hegemon_bloc(world, hegemon, share)` from `backend/game_logic/coalition.py`, NOT the sticky `world.hegemony_signal_high_water` field. High-water is asymmetrically sticky for passive-threat ratchet purposes and would cause preview lag after a bloc shrinks.
- The counter-play hint only attaches when `proposer_nation == hegemon` (because `_pick_counterplay_hint` is authored for player-is-hegemon cases; routing France-specific hints through non-hegemon bloc members would leak logic).

**4. Components dict + FEEDBACK_STRINGS contract.** Per `tests/test_bugfix_proposal_flow.py::TestBugfix_FeedbackStringsCompleteness`, every `FEEDBACK_STRINGS` entry must have non-empty `positive` AND `negative` strings. Both new modifiers are always ≤ 0 in practice, so the `positive` string will rarely surface — but the contract requires it. Check that the implementer's phrasing ("balance of power across Europe" / "a clean bilateral slate with them") is reasonable and distinct from existing entries.

**5. Legacy test migration.** Per plan line 308, pre-v2.4.3 tests must be updated to match the new substrate. Check:
- `tests/test_phase4_batch3_features.py::TestR34DiplomaticReliability` — 3 tests updated to `// 10` ±6 contract. The renamed `test_reliability_modifier_capped_at_plus_minus_6` (was `_plus_minus_10`) should assert the new cap correctly.
- `tests/test_da1_ai_intelligence.py` + `tests/test_session4_diplomacy.py` — 7 AI trigger tests got a `_clear_opening_bloc(world)` helper call. Verify the helper is correct (strips `ALLIANCE` / `DEFENSIVE_ALLIANCE` states to `PEACE`, invalidates bloc cache) and that its migration comment explains WHY (hegemony_target_mod tax on the opening Prussia-Austria-Britain bloc pushes expected acceptance below the `score < 20` AI filter in `process_diplomatic_phase`).
- The migration DID NOT touch `make_world` / `make_war_world` fixtures globally — only individual failing tests. Other tests that pass without the clear (e.g., `test_we_0_fires_at_threshold`) should stay untouched.

**6. Test quality.** Read `tests/test_hegemony_acceptance.py` end-to-end. Verify:
- The 5 share curve points (0.30, 0.33, 0.50, 0.60, 0.635) produce the documented expected values (0, -1, -12, -18, -20). Spot-check the math yourself.
- The `test_hegemony_cache_invalidation` test uses real WorldState geometry (not monkeypatch) so it actually exercises the live `_identify_max_bloc_share` + `invalidate_bloc_members_cache` seam. Monkeypatched curve tests are fine because they're isolating the formula, but the cache test must be real.
- The test fixture `_seed_betrayal_strikes` writes directly to `world.betrayal_history` with correct schema (`severity`, `turn`, `episode_id`, `decays_on_turn`). Check it matches what `_get_active_betrayal_strikes` at `diplomacy.py:281-296` reads.
- Parametrize coverage is adequate (seven curve points including extremes).

**7. Regression scan.** Run:
```
".venv\Scripts\python.exe" -m pytest tests/ --tb=no -q
```
Expected: `8613 passed, 2 skipped`. If anything fails, it's either a bug introduced by the slice OR a pre-existing flake. Investigate.

Then run:
```
".venv\Scripts\python.exe" -m ruff check backend/game_logic/diplomacy.py backend/display_names.py tests/test_hegemony_acceptance.py tests/test_da1_ai_intelligence.py tests/test_session4_diplomacy.py tests/test_phase4_batch3_features.py
```
Expected: 5 pre-existing errors (`E402` imports at lines 140+3822 in diplomacy.py, `F841` unused `player` at 3571 in diplomacy.py, `F841` unused `original_gold`/`original` in test_da1_ai_intelligence.py). Confirm NONE of the 5 are from code added by the slice (check line numbers against `git blame` for changed lines).

**8. Smoke verify.** Optional but valuable: start the backend and hit a proposal-preview path to see the warning render in the actual API response.

```
".venv\Scripts\python.exe" backend/main.py
```
Then in another shell:
```
curl -X POST http://127.0.0.1:8005/command -H "Content-Type: application/json" \
  -d '{"command": "propose alliance with saxony"}' | python -m json.tool
```
Inspect the `warnings` field. If France's bloc commands ≥30% share at game start (1805 opening typically has Prussia-Austria-Britain bloc above threshold, so France is NOT in the hegemon's bloc and the warning should NOT fire for `France → Saxony`). If you want to force the warning, set up a world where France is dominant.

### Specific invariants to spot-check

- `hegemony_target_mod` returns 0 when `world.get_bloc_members` raises `AttributeError` (fixture robustness). Look at the `try/except` — is it too broad (catching things it shouldn't) or too narrow (missing real exceptions)?
- `_build_hegemony_preview_warning` branching at `band == 0` (30-33% pre-noticed) vs `band >= 1` correctly falls through `bloc_label` (`None` at 33-49%) to `descriptive_label`. Verify by reading `describe_hegemon_bloc` at `backend/game_logic/coalition.py:560`.
- The counter-play hint suppression when `proposer_nation != hegemon` is correct — verify that `_pick_counterplay_hint` at `coalition.py:263` returns `""` for the non-hegemon case, so the implementer's defensive gate is actually defensive rather than redundant.
- At 3 strikes, `bilateral_betrayal_mod = -18` AND `hard_reject_posture` fires separately (not dead weight). Read the components dict output in `test_bilateral_betrayal_mod::test_three_strike_composition_with_hard_reject` and confirm both surface.

### What to report

Write a report under 1000 words with these sections:

1. **PASS/FAIL verdict** per checklist item above (spec compliance, merge gate, gate symmetry, FEEDBACK contract, legacy migration, test quality, regression, smoke).
2. **Findings** — anything that looks wrong, risky, or underspecified. Rank by severity (Critical / High / Medium / Low). Cite `file:line` for every finding.
3. **Spec gaps** — if the implementation deviates from spec, was it deviation with justification (e.g., the metadata referent deferral) or an oversight? Flag either way.
4. **Followup recommendations** — anything that should be fixed before the slice is considered closed.

**Do NOT** rewrite code, implement fixes, or propose broad refactors. This is a targeted audit of a single slice.

### Reference reading order if cold

1. `CLAUDE.md` — orient to the project, golden rules, file map
2. `docs/STATUS.md` top entry — what shipped previously (B-Hegemony)
3. `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` §§190-215 + 387-398
4. `docs/RELIABILITY_COMMITMENTS_SPEC.md` §§9.1, 9.2, 11.2
5. `docs/COMMITMENTS_PRESENTATION_SPEC.md` §§8.1a, 11, 16
6. `backend/game_logic/coalition.py` lines 160-260, 560-600, 263-310 (the B-Hegemony substrate you're auditing against)
7. `backend/game_logic/diplomacy.py` — the changes (grep for `hegemony_target_mod`, `bilateral_betrayal_mod`, `_build_hegemony_preview_warning`, the `calculate_acceptance` wiring)
8. `tests/test_hegemony_acceptance.py` — the new tests

Report back when done.
