# MP v2.4.3 — Block 2: Substrate Alignment

> **Source:** [MP_V243_AUDIT_COMBINED.md](docs/audits/MP_V243_AUDIT_COMBINED.md) — Block 2 (~1.5-3 hours, one session, doc + code).
>
> **Ships as:** 2-3 small focused commits (U4, U3, optional U2). Don't split U3 and U4 across sessions — coupling them makes the "v2.4.3 enum + speaker discipline" boundary legible in `git log`.
>
> **Pre-merge gate for:** B-B4 (needs U3). Unblocks B-Hegemony tests that assert on `hegemony_pressure` (U4).
>
> **Depends on:** Block 1 ([`MP_V243_BLOCK1_DOC_CLEANUP.md`](docs/audits/MP_V243_BLOCK1_DOC_CLEANUP.md)) should land first so the spec contracts these code changes match are already current.

---

## Scope

2-3 unified findings, live-code changes with doc echoes. Each is a narrow diff.

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
