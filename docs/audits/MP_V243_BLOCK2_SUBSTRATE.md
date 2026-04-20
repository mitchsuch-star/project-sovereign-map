# MP v2.4.3 — Block 2: Substrate Alignment

> **Source:** [MP_V243_AUDIT_COMBINED.md](docs/audits/MP_V243_AUDIT_COMBINED.md) — Block 2 (~1.5-3 hours, one session, doc + code). **Addendum (2026-04-20):** follow-up meta-audit added items B1-B5 (see [Addendum](#addendum--follow-up-findings-2026-04-20)) — fold each into its partner U-item's commit.
>
> **Ships as:** 2-3 small focused commits (U4, U3, optional U2). Don't split U3 and U4 across sessions — coupling them makes the "v2.4.3 enum + speaker discipline" boundary legible in `git log`.
>
> **Pre-merge gate for:** B-B4 (needs U3). Unblocks B-Hegemony tests that assert on `hegemony_pressure` (U4).
>
> **Depends on:** Block 1 ([`MP_V243_BLOCK1_DOC_CLEANUP.md`](docs/audits/MP_V243_BLOCK1_DOC_CLEANUP.md)) should land first so the spec contracts these code changes match are already current.

---

## Scope

2-3 unified findings + 5 addendum items, live-code changes with doc echoes. Each is a narrow diff.

| # | Finding | Work | Est. | Gating? |
|---|---------|------|------|---------|
| 1 | U4 — `rival_pressure` → `hegemony_pressure` | 3 line changes + display_names alias + 2-3 unit tests | 45 min | Blocks B-Hegemony tests |
| 2 | U3 — `french_breach` speaker_attribution | 1 conditional + payload addition + 2 unit tests | 45 min | Blocks B-B4 |
| 3 | U2 — `commitment_paradox` rename (optional — B-B3's slot) | Rename attribute + emitter type; alias-on-load; new Godot popup scene + script; update routing | 90-120 min | Unblocks C-lite §14 artifacts |

**Subtotal without U2: ~1.5 hours. With U2: ~3 hours.**

**Recommendation:** run U3 + U4 now; defer U2 to B-B3's scheduled slot unless B-B3 is imminent.

---

## Execution checklist

### U4 — `decision_reason` enum drift

**Spec requires** `hegemony_pressure` + `unknown_baseline`; `concern_pressure` kept as read-alias only (per [RELIABILITY_COMMITMENTS_SPEC.md:964-967](docs/RELIABILITY_COMMITMENTS_SPEC.md:964)).
**Live code returns** `rival_pressure` from three sites.

#### 1. Backend emit sites

[`backend/game_logic/diplomacy.py`](backend/game_logic/diplomacy.py:1828):
- Line 1828: `return "rival_pressure"` → `return "hegemony_pressure"`
- Line 1829: `return "rival_pressure"` → `return "hegemony_pressure"`
- Line 1858: `return "rival_pressure"` → `return "hegemony_pressure"`

Before flipping these, read the surrounding function context to confirm no branch is the "unknown/default baseline" case — if there is, that one should return `"unknown_baseline"` instead of `"hegemony_pressure"`.

#### 2. Display mapping

[`backend/display_names.py`](backend/display_names.py:344):
- Rename the existing key: `"rival_pressure": "rival pressure"` → `"hegemony_pressure": "hegemony pressure"`.
- Keep a read-alias entry: `"rival_pressure": "hegemony pressure"` (same display, so legacy saves render correctly).
- If there's a `concern_pressure` key elsewhere in the file, keep it and point it at the same display string.

#### 3. Tests

Add to the existing `tests/` module that covers decision-reason strings (search for `rival_pressure` in tests first — any references there are pointing at the old enum).

- **Unit test 1:** calling the emitter path returns `"hegemony_pressure"` (not `"rival_pressure"`).
- **Unit test 2:** `display_names` maps both `"hegemony_pressure"` and `"rival_pressure"` to a non-empty display string.
- **Unit test 3 (optional):** if saves are deserialized with `decision_reason: "rival_pressure"`, they still render.

#### 4. Verification

```bash
grep -rn rival_pressure backend/ tests/
```

Expected: only test fixtures asserting the alias behavior remain. Production code should be clean.

#### 5. Commit

Single commit, message approximately:
```
MP v2.4.3 U4: rival_pressure → hegemony_pressure enum

3 emit sites in diplomacy.py flipped; display_names renames key and
retains rival_pressure as read-alias for save compatibility.
Unblocks B-Hegemony tests that assert on the v2.4.3 enum.
```

---

### U3 — `french_breach` speaker_attribution

**Spec requires** family=`french_breach` → `speaker="envoy"` → victim's named diplomat (Hardenberg / Metternich / Einsiedel per Voice Bible).
**Live code** writes `speaker_attribution: "foreign_office"` unconditionally at [`backend/game_logic/diplomacy.py:783`](backend/game_logic/diplomacy.py:783).

#### 1. Backend emit

[`backend/game_logic/diplomacy.py`](backend/game_logic/diplomacy.py:775) — the `_record_treaty_broken()` (or equivalent) function around lines 775-809.

Change the literal `"speaker_attribution": "foreign_office"` at line 783 to a conditional:

```python
speaker = "envoy" if end_reason_family == END_REASON_FAMILY_FRENCH_BREACH else "foreign_office"
...
"speaker_attribution": speaker,
```

**Also add** `victim_nation` to the payload (if not already present) so the downstream resolver has enough context to pick the named diplomat without re-deriving it. The victim is the counterparty — `fault_nation` is the breaker (usually France), the other participant in the treaty is the victim.

**Do not touch** `hard_reject_posture_triggered` at lines 844-850 or `hard_reject_posture_cleared` at lines 403-416 — those correctly use `foreign_office`. Only the breach family is mis-attributed.

**Don't touch** the `obsolescence_or_external` / `counterparty_reversal` / `defensive_refusal_termination` families either — they all keep `foreign_office` under the spec.

#### 2. Central resolver signature (sketch only, do not wire)

Leave a named but stubbed helper at the natural home (likely `backend/game_logic/diplomatic_templates.py` or a new `speaker_resolver.py`) with a docstring saying C-lite §13 wires this:

```python
def resolve_named_diplomat(speaker: str, nation: str) -> str:
    """Resolve a speaker role + nation pair to an attribution label.

    Scheduled for C-lite §13 full implementation. Stub for now so
    notices, logs, and popups can import-and-call without crashing.
    """
    raise NotImplementedError("Wired in C-lite §13; see COMMITMENTS_PRESENTATION_SPEC §10.3")
```

This is strictly a signature so Block 2's code-review pass does not reintroduce per-caller resolver logic.

#### 3. Tests

- **Unit test 1:** `french_breach` emit path sets `speaker_attribution == "envoy"`.
- **Unit test 2:** `obsolescence_or_external` and `counterparty_reversal` still set `speaker_attribution == "foreign_office"`.
- **Unit test 3:** the payload includes `victim_nation` when emit is `french_breach`.

#### 4. Verification

```bash
grep -n 'speaker_attribution' backend/game_logic/diplomacy.py
```

Expected: line 783 now conditional on family; lines 409, 416, 850, 859 still literal `"foreign_office"`.

#### 5. Commit

Single commit, message approximately:
```
MP v2.4.3 U3: french_breach emits speaker_attribution=envoy

Per COMMITMENTS_PRESENTATION_SPEC §10.3 the injured-party envoy
voices the breach notice. Live emitter previously wrote
"foreign_office" unconditionally, which would render as an
anonymous chancery bulletin rather than Hardenberg's accusation.
Other end_reason_family values unchanged. Adds victim_nation to
payload so downstream resolver can pick the named diplomat.
Unblocks B-B4.
```

---

### U2 — `commitment_paradox` rename (optional — B-B3's scheduled work)

**Only do this now if B-B3 is the next coding slice.** Otherwise leave it in its plan slot.

**Spec canonical** is `commitment_paradox` on `commitment_paradox_popup.{tscn,gd}` (per [COMMITMENTS_PRESENTATION_SPEC.md:19, 214, 709, 746](docs/COMMITMENTS_PRESENTATION_SPEC.md:214)).
**Live code** uses `alliance_paradox` everywhere.

#### Scope summary

6 surfaces touch this:

| Surface | Files | Change type |
|---------|-------|-------------|
| Emitter type string | [diplomacy.py:2123-2135](backend/game_logic/diplomacy.py:2123) | Rename |
| WorldState attribute + serialization | [world_state.py:497, 668-673, 3271, 3578](backend/models/world_state.py:497) | Rename + alias-on-load |
| Godot main.gd registration + routing | [main.gd:100, 226-228, 726, 776-782, 2997](godot-client/project-sovereign/scripts/main.gd:226) | Rename |
| Godot popup scene | `scenes/alliance_paradox_popup.tscn` | New file (`commitment_paradox_popup.tscn`) |
| Godot popup script | `scripts/alliance_paradox_popup.gd` | New file (`commitment_paradox_popup.gd`) |
| Save format doc | `SAVE_FORMAT_REFERENCE.md` | Document alias-on-load |

#### 1. Lock the payload schema first

Before renaming, fix the popup payload schema. Per presentation §12.3:

```python
{
    "episode_id": int,
    "primary_nation": str,
    "secondary_nation": str,
    "attacker": str,
    "defender": str,
    "ally": str,
    # preview snapshots for the three-beat scene
    "attacker_preview": {...},
    "defender_preview": {...},
    "ally_preview": {...},
}
```

Confirm today's payload at [`diplomacy.py:2123-2131`](backend/game_logic/diplomacy.py:2123) matches (fields may be named slightly differently; reconcile with the spec before renaming).

#### 2. Backend rename

- [`backend/game_logic/diplomacy.py:2135`](backend/game_logic/diplomacy.py:2135): `"type": "alliance_paradox"` → `"type": "commitment_paradox"`.
- [`backend/models/world_state.py:497`](backend/models/world_state.py:497): `self.alliance_paradox_popup: Optional[Dict] = None` → `self.commitment_paradox_popup: Optional[Dict] = None`.
- [`backend/models/world_state.py:668-673`](backend/models/world_state.py:668): property + setter rename.
- [`backend/models/world_state.py:3271`](backend/models/world_state.py:3271): `to_dict` key `"alliance_paradox_popup"` → `"commitment_paradox_popup"`.
- [`backend/models/world_state.py:3578`](backend/models/world_state.py:3578): `from_dict` — **keep as alias-on-load**:
  ```python
  world.commitment_paradox_popup = (
      data.get("commitment_paradox_popup")
      or data.get("alliance_paradox_popup")  # legacy v1.0 alias
  )
  ```

#### 3. Godot rename + new scene/script

- Create `godot-client/project-sovereign/scenes/commitment_paradox_popup.tscn` (copy from `alliance_paradox_popup.tscn`; adjust any label changes needed for the three-beat scene per §12.3).
- Create `godot-client/project-sovereign/scripts/commitment_paradox_popup.gd` (copy from `alliance_paradox_popup.gd`; rename class if applicable).
- [`godot-client/project-sovereign/scripts/main.gd:100`](godot-client/project-sovereign/scripts/main.gd:100): `var alliance_paradox_popup = null` → `var commitment_paradox_popup = null`.
- [`godot-client/project-sovereign/scripts/main.gd:226-228`](godot-client/project-sovereign/scripts/main.gd:226): rename dialog key + scene path.
- [`godot-client/project-sovereign/scripts/main.gd:726`](godot-client/project-sovereign/scripts/main.gd:726): rename dialog routing entry (id, matches, show).
- [`godot-client/project-sovereign/scripts/main.gd:776-782`](godot-client/project-sovereign/scripts/main.gd:776): rename response-detection helper + route-handler function.
- [`godot-client/project-sovereign/scripts/main.gd:2997`](godot-client/project-sovereign/scripts/main.gd:2997): rename `_on_alliance_paradox_choice` → `_on_commitment_paradox_choice`.
- Delete or keep `alliance_paradox_popup.{tscn,gd}` — if deleting, grep the codebase one more time to confirm no stragglers reference the old path.

#### 4. Doc echo

[`docs/SAVE_FORMAT_REFERENCE.md`](docs/SAVE_FORMAT_REFERENCE.md) — confirm Block 1's U7 edit already documents the `alliance_paradox_popup` → `commitment_paradox_popup` alias. If not, add it.

#### 5. Tests

- **Unit test 1:** `world.commitment_paradox_popup = X; d = world.to_dict()` round-trips with key `"commitment_paradox_popup"`.
- **Unit test 2:** `world.from_dict({"alliance_paradox_popup": X})` loads X into `world.commitment_paradox_popup` (alias-on-load).
- **Unit test 3:** `world.from_dict({"commitment_paradox_popup": X})` loads X into `world.commitment_paradox_popup` (canonical).
- **Unit test 4:** emitter `type` string is `"commitment_paradox"`.

#### 6. Verification

```bash
grep -rn alliance_paradox backend/ tests/ godot-client/project-sovereign/scripts/
```

Expected: only alias-on-load references and test fixtures asserting alias behavior remain.

#### 7. Commit

Single commit, message approximately:
```
MP v2.4.3 U2 (B-B3): alliance_paradox → commitment_paradox rename

Canonical type is commitment_paradox per COMMITMENTS_PRESENTATION_SPEC.
Renames emitter type string, WorldState attribute + serialization,
Godot routing, and popup scene + script. Old alliance_paradox_popup
key is preserved as alias-on-load in from_dict for save compatibility.
SAVE_FORMAT_REFERENCE.md documents the alias policy.
```

---

## Definition of done

### Minimum (U3 + U4)

- [ ] `grep -rn rival_pressure backend/` returns no production-code hits (only test fixtures).
- [ ] `french_breach` emit path sets `speaker_attribution == "envoy"`; other families unchanged.
- [ ] Full test suite green (`".venv\Scripts\python.exe" -m pytest tests/ -v --tb=no -q`).
- [ ] Two commits landed: U4 enum flip + U3 speaker attribution.

### Full (U3 + U4 + U2)

- [ ] All above, plus:
- [ ] `grep -rn alliance_paradox backend/ godot-client/` returns only alias-on-load references and test fixtures.
- [ ] `commitment_paradox_popup.tscn` + `.gd` exist on disk.
- [ ] Round-trip save/load tests cover both legacy and canonical paradox popup keys.
- [ ] Three commits landed: U4, U3, U2.

## Out of scope

- Full commitments notice template family authoring (C-lite §13).
- Named-diplomat resolver implementation (C-lite §13 — this block leaves a stubbed signature only).
- Balance of Europe payload block + renderer (B-Hegemony + C-lite §14).
- Make Amends emitters + `reparations_cooldown` field (B-B7).
- DG-4 call-to-arms event emitters (B-B4).
- `END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION` constant (B-B4).

All of the above are already scheduled in [`RELIABILITY_IMPLEMENTATION_PLAN.md`](docs/RELIABILITY_IMPLEMENTATION_PLAN.md); Block 2 only closes the substrate-alignment gaps that would block those slices from running against today's master.

---

## Addendum — follow-up findings (2026-04-20)

Second-pass meta-audit surfaced five additional substrate gaps. Each folds into its partner U-item's commit rather than shipping standalone — keeps the commit count unchanged.

| # | Finding | Folds into | Severity | Est. |
|---|---------|-----------|----------|------|
| B1 | U4 extension — add `unknown_baseline` enum value per spec §964 catch-all | U4 | MAJOR | 15 min |
| B2 | U3 extension — name and import the `END_REASON_FAMILY_FRENCH_BREACH` constant (defined at `diplomacy.py:198-200`) | U3 | MINOR | 5 min |
| B3 | U2 extension — rename `dialogue_manager.push({"type": "alliance_paradox", ...})` and add `commitment_paradox` entry to `DIALOGUE_PRIORITY` | U2 | MAJOR | 15 min |
| B4 | Campaign-log dead-code cleanup — remove duplicate event-type branches at `backend/campaign_log.py:673-687` and `689-692` | standalone (new commit, ~10 min) | MINOR | 10 min |
| B5 | Block 2 DoD — add post-suite test-count expectation (combined audit §373) | DoD | MINOR | 2 min |

**Addendum subtotal: ~45 min on top of U3+U4 (~1.5h base), ~1h on top of U3+U4+U2 (~3h base).**

---

### B1 — U4 extension: add `unknown_baseline` enum

Spec [§964](docs/RELIABILITY_COMMITMENTS_SPEC.md:964) v2.4.3 enum is `hegemony_pressure` **+ `unknown_baseline`** (not just the rename). The catch-all value fires when pressure cannot be attributed to a specific hegemon (e.g., pre-engine state, ambiguous bloc share, calculation skipped). Currently `diplomacy.py:1828, 1829, 1858` all return the same non-default string.

**In U4 step 1** (after flipping the three sites to `"hegemony_pressure"`), audit the surrounding function in [`backend/game_logic/diplomacy.py`](backend/game_logic/diplomacy.py:1828): which of the three return paths is the genuine *default / fallback* path (not the specific-pressure path)? That path returns `"unknown_baseline"` instead. If none of the three is a true default, introduce one — the function must have a default path because consumers rely on the enum being exhaustive.

**In U4 step 2** (display_names): after the rename, add `"unknown_baseline": "unknown baseline"` as a third key. Three keys total in the family:
```python
"hegemony_pressure": "hegemony pressure",
"unknown_baseline": "unknown baseline",
"rival_pressure": "hegemony pressure",  # legacy alias
```

**In U4 step 3** (tests): add a fourth unit test — default/fallback path returns `"unknown_baseline"`.

**In U4 step 4** (verification): expected `grep` output is unchanged (`rival_pressure` only in test fixtures).

---

### B2 — U3 extension: name `END_REASON_FAMILY_FRENCH_BREACH`

U3 step 1 sketches `speaker = "envoy" if end_reason_family == END_REASON_FAMILY_FRENCH_BREACH else "foreign_office"`. The constant is already defined at [`backend/game_logic/diplomacy.py:198-200`](backend/game_logic/diplomacy.py:198) — ensure the U3 implementer uses the existing constant by name (not a string literal). Verify import ordering if the constant is defined in the same module.

If the conditional is written outside `diplomacy.py` (it should not be — `_record_treaty_broken` is in `diplomacy.py` so this is self-referential), import the constant explicitly.

No extra tests; this is a code-hygiene rider on U3's existing tests.

---

### B3 — U2 extension: dialogue_manager push + DIALOGUE_PRIORITY

If U2 lands in Block 2 (B-B3 pulled forward per audit §354), the rename touches one more surface the combined audit under-sampled:

1. **[`backend/game_logic/diplomacy.py:2134-2135`](backend/game_logic/diplomacy.py:2134)** — this is the `dialogue_manager.push({"type": "alliance_paradox", ...})` call. Rename the type string to `"commitment_paradox"` in the same pass as the popup-field rename. (Separate from U2 step 2.1, which handles the popup-field emitter at the same line range.)

2. **[`backend/models/dialogue_manager.py:87`](backend/models/dialogue_manager.py:87)** — `DIALOGUE_PRIORITY` map currently has `"alliance_paradox": 0` only. After the rename, the new type `"commitment_paradox"` would default to 99 (lowest priority) — the paradox would silently stop outranking other dialogues. Add `"commitment_paradox": 0` alongside `"alliance_paradox": 0` (keep both during transition).

3. **[`backend/models/dialogue_manager.py`](backend/models/dialogue_manager.py) HARD_STOP_TYPES** — verify `"commitment_paradox"` is in the hard-stop list (it must block commands per R12 / PL-27). If `"alliance_paradox"` is there today, add the new name alongside it.

Fold into U2's existing commit — the commit message should add one line: *"Also renames dialogue push + DIALOGUE_PRIORITY; both legacy and canonical keys listed for transition."*

**Verification** (augments U2 step 6):
```bash
grep -n "alliance_paradox\|commitment_paradox" backend/models/dialogue_manager.py backend/game_logic/diplomacy.py
```
Both names should appear in DIALOGUE_PRIORITY and HARD_STOP_TYPES; production emit sites should use only `commitment_paradox`.

---

### B4 — Campaign-log dead-code cleanup

[`backend/campaign_log.py:504-518`](backend/campaign_log.py:504) vs lines 673-687, and lines 520-530 vs 689-692: each pair is a duplicate branch for the same event type. Because `format_event_oneliner()` returns on the first match, the second occurrence is dead code.

**Fix:**
1. Read both branches to confirm they produce identical output (they should — grep the two ranges to diff).
2. Delete the second occurrence (lines 673-687 and 689-692).
3. Run the full test suite to confirm no campaign-log test was implicitly relying on the shadowed code.

This is a **separate commit** (not folded into U3 or U4) — unrelated diff, keeps git blame clean.

Commit message approximately:
```
MP v2.4.3 Block 2 cleanup: remove duplicate campaign_log branches

Two event types had mirrored handlers at two different line ranges
in campaign_log.py. The first return wins; the second was dead
code. Deleting removes ~30 lines without behavior change.
```

---

### B5 — Block 2 DoD — test count expectation

Combined audit [§373](docs/audits/MP_V243_AUDIT_COMBINED.md:373) specifies the post-merge suite should show *"pre-existing count + 4-6 new from U3/U4, +4-6 more if U2 is in"*. Add to this work order's DoD (both Minimum and Full sections):

**Minimum (U3 + U4 + B1):**
- [ ] Full test suite: **pre-existing count + 5-7 new** (U3 adds 2-3, U4 adds 3-4 incl. `unknown_baseline`).

**Full (U3 + U4 + U2 + B1 + B3):**
- [ ] Full test suite: **pre-existing count + 9-13 new** (U3: 2-3, U4: 3-4, U2: 4-6 incl. DIALOGUE_PRIORITY round-trip).

The count expectation gives the reviewer a quick sanity check without running `pytest -q` count-by-count.

---

## Addendum v2 — test-suite gaps (2026-04-20)

Third-pass audit found substantial test coverage gaps. Fold these into the U-item commits rather than shipping standalone tests.

| # | Finding | Folds into | Severity | Est. |
|---|---------|-----------|----------|------|
| **T4** | **NO serialization round-trip test for `betrayal_history` / `next_episode_id`** — golden-rule violation ("If it exists on the object, it must serialize") currently unenforced | U2 commit (or new substrate commit if U2 deferred) | **HIGH** | 15 min |
| **T8** | **Composite floor completely untested** — full grep for `composite_floor` / `grievance_modifier` in `tests/` returns 0 matches | B-B1-lite + B-B4 (out of Block 2 — flag in work order) | **HIGH** | tracked separately |
| T1 | ~40 test sites hardcode `"alliance_paradox"` across 15+ files; U2 alias-on-load would silently pass them (no `commitment_paradox` positive counterparts) | U2 commit | MAJOR | 30 min |
| T3 | No test asserts `speaker_attribution == "foreign_office"` in french_breach contexts — U3's flip lands without regression coverage | U3 commit | MEDIUM | 10 min |
| T6 | No test asserts `DIALOGUE_PRIORITY["commitment_paradox"]` or membership in `HARD_STOP_TYPES` | U2 commit (B3 extension) | MEDIUM | 10 min |
| T7 | No unit test exercises §7.5 opposition-graph `commitment_paradox` emission trigger directly | U2 commit | MEDIUM | 10 min |
| T10 | 5 audit-test files hardcode `{"type": "alliance_paradox", ...}` dialogue-manager push payloads (test_audit_part1, test_audit_playtest, test_audit_session4, test_audit_2_3, test_systems_audit_v2_session4) | U2 commit | MEDIUM | 20 min |

**Addendum v2 subtotal: ~1.5 hours on top of U2+U3+U4 (~5 hours with full U2 + B1 + B3 + addendum v2).**

---

### T4 — betrayal substrate round-trip (HIGH)

**[`tests/test_serialization_enforcement.py`](tests/test_serialization_enforcement.py)** has zero matches for `betrayal_history` or `next_episode_id`. Both are shipped v2.4.3 substrate fields on `WorldState`; both serialize through `to_dict` / `from_dict` today ([world_state.py:3253-3272, 3578](backend/models/world_state.py:3253)); neither has a round-trip test.

**Golden rule violated:** CLAUDE.md "Serialization Enforcement (MANDATORY)" — *"If it exists on the object, it must serialize."*

**Fix:** add to `tests/test_serialization_enforcement.py` (or a new `tests/test_memory_substrate_serialization.py`):

- Round-trip `betrayal_history` with a representative entry (actor, victim, turn, episode_id, type).
- Round-trip `next_episode_id` with a non-default value (e.g., 7) — verify monotonic counter survives load.
- Round-trip legacy saves (missing these keys) — confirm `.get()` defaults work.

This is a **pre-merge gate for U2**, because B-B3's alias-on-load (U2 step 2.5) extends the `from_dict` path and without a round-trip test, the alias contract is itself untested.

Commit folds into U2 commit with the addition: *"Adds round-trip coverage for betrayal_history + next_episode_id (previously untested v2.4.3 substrate)."*

---

### T8 — Composite floor (HIGH, out of Block 2 scope)

Full-suite grep for `composite_floor`, `grievance_modifier`, `grievance_floor`, `acceptance_floor`, `acceptance.*<=.*-` returns **zero matches** across all `tests/`.

Spec §9.3 authors a `-60` composite floor when DG-4's `grievance_modifier` is live. Spec §905 requires B-B4 to land with-or-after B-B1-lite's no-floor collapse. **Neither slice has a regression net today because no test pins the floor value.**

B-B1-lite will flip the formula (remove old floor) and B-B4 will reintroduce the conditional floor. Without coverage, either slice can silently introduce drift.

**This is OUT of Block 2's scope** (Block 2 is substrate-alignment only). Flag for B-B1-lite and B-B4 work orders:

- **B-B1-lite test budget:** add 1-2 tests asserting *"after no-floor collapse, composite score can go below -60 in the specific 3-term case when DG-4 is not live"*.
- **B-B4 test budget:** add 2-3 tests asserting *"when `grievance_modifier` is live, composite floor clamps at -60 for the 4-term case (hegemony + betrayal + grievance + reliability)"*.

Add an explicit note to [`RELIABILITY_IMPLEMENTATION_PLAN.md`](docs/RELIABILITY_IMPLEMENTATION_PLAN.md) B-B1-lite and B-B4 sections. **This note lives in Block 1** (doc-only, already in Addendum v2 of Block 1 per A11 DoD expansion) — here, just ensure Block 2 acknowledges the hand-off.

---

### T1 — alliance_paradox test-string sweep (MAJOR, folds into U2)

When U2 renames to `commitment_paradox` with alias-on-load, the ~40 existing test sites hardcoding `"alliance_paradox"` silently continue passing via the alias. That's the alias-on-load's *purpose* for save compatibility, but it masks test coverage of the new code path.

**Fix (fold into U2 commit):** for each hardcoded-string site, add a parallel positive test using the new name. Representative sites from audit:

- `tests/test_dialogue_manager.py:76, 90, 298, 301, 315, 318, 442, 446, 518` (HARD_STOP + priority)
- `tests/test_offer_lifetime.py:75, 125, 222, 247, 258, 459, 582`
- `tests/test_cooldown_popup_characterization.py:188, 191, 193` (priority comment bakes old string)
- `tests/test_session_3_commands.py:365` (docstring)
- `tests/test_audit_major_2026_03.py:471-478` (already-skipped with `commitment_paradox sibling flow` reason — resurrect as B3's first test)

For each: don't delete the old-name assertion (it validates the alias). Add a `commitment_paradox` assertion alongside it. Typical shape:
```python
# Existing (alias path — keep)
dialogue_manager.push({"type": "alliance_paradox", ...})
assert "alliance_paradox" in active_dialogue_types

# New (canonical path)
dialogue_manager.push({"type": "commitment_paradox", ...})
assert "commitment_paradox" in active_dialogue_types
```

Also: `test_cooldown_popup_characterization.py:191` has a priority comment citing `"alliance_paradox (0)"`. Update the comment inline — documentation rot otherwise.

---

### T3 — french_breach speaker assertion (MEDIUM, folds into U3)

`tests/test_playtest_bugfixes.py:306` is the only `speaker_attribution` assertion in the suite — and it checks `"talleyrand"`. [`test_phase2b_diplomacy.py:109, 299`](tests/test_phase2b_diplomacy.py:109) assert `end_reason_family == "french_breach"` but never assert the resulting speaker. U3's flip (foreign_office → envoy) lands without regression coverage.

**Fix (fold into U3 commit):** add one test — set up a french_breach scenario, trigger the emit, assert `speaker_attribution == "envoy"`. Add the symmetric negative for `obsolescence_or_external` — assert it still emits `"foreign_office"`.

Natural home: `tests/test_phase2b_diplomacy.py` alongside the existing `french_breach` end-reason coverage.

---

### T6 + T7 — DIALOGUE_PRIORITY + paradox emission (MEDIUM, fold into U2 / B3)

**T6:** add two assertions alongside B3 extension:
1. `DIALOGUE_PRIORITY["commitment_paradox"] == 0` (same priority as the legacy alias).
2. `"commitment_paradox" in HARD_STOP_TYPES`.

**T7:** add one unit test for the §7.5 opposition-graph trigger path — wire up a scenario where an ally-of-enemy relationship forces a paradox without going through the executor (which is covered by `test_phase4_batch4_ledger.py:251, 300`). The emitter at [`diplomacy.py:2123-2135`](backend/game_logic/diplomacy.py:2123) is the unit under test.

---

### T10 — audit-test alliance_paradox sweep (MEDIUM)

Five audit-test files hardcode `{"type": "alliance_paradox", ...}` as the dialogue-manager push payload:
- `tests/test_audit_part1.py:51, 140`
- `tests/test_audit_playtest.py:179`
- `tests/test_audit_session4.py:135`
- `tests/test_audit_2_3.py:1348, 1394`
- `tests/test_systems_audit_v2_session4.py:358, 365`

These were written during the Mar 2026 Diplomacy Deep Audit (memory note, not a current spec). They exercise the dialogue-manager push contract; under U2's alias-on-load they'll keep passing but won't exercise the new path.

**Fix (fold into U2 commit):** for each, add a parallel test with `"type": "commitment_paradox"`. Don't remove the old string — those tests anchor the alias contract. Aim to double the paradox-push coverage (~8 new tests across 5 files).

---

### Summary — updated test-count expectations

| Scenario | Pre-existing | U3 | U4 + B1 | U2 + T1 + T6 + T7 + T10 | T4 | Total new |
|---|---|---|---|---|---|---|
| Minimum (U3 + U4 + B1) | (suite) | 2-3 | 4-5 | — | — | 6-8 |
| Full (U3 + U4 + U2 + B1 + B3) | (suite) | 2-3 | 4-5 | 15-20 | 2-3 | 23-31 |

Replaces the Block 2 DoD count (B5). Updated DoD line:

- [ ] Minimum: Full test suite **pre-existing + 6-8 new**.
- [ ] Full: Full test suite **pre-existing + 23-31 new**.
