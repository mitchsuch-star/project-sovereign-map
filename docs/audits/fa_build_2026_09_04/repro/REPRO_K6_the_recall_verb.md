Repo is clean; all 11 probes live in scratch.

---

# REPRO C — FA-S9-D1 + FA-71 ("the recall verb")

Read-only, master `9ef38da8`, mock parser, sandboxed saves. Probes under
`C:\Users\User\AppData\Local\Temp\claude\C--Users-User-PycharmProjects-project-sovereign-map\d3a697cd-1535-475d-bd1b-457545b1c421\scratchpad\s14\C_recall\`.

## Headline

**The serialization blocker re-verifies exactly — and it is WORSE than the prior repro measured.** It is not only "the frozen men are deleted": one save/load also **defeats the slice-9 attrition exemption and the sweep destroys the marshal outright**. Measured, verbatim event: `Murat has been eliminated by supply attrition at None`. So both rows understate their own player consequence: the man is not "frozen forever", he is **dead one turn after the first save**.

Three of the eleven measurements contradict the prior repro's build guidance, and two of those change the slice's shape.

---

## FA-S9-D1 — the recall verb (gate, `DESIGN_REFINEMENT.md:83`)

**VERDICT: REPRODUCED, AND WIDER.** The gate's body is accurate. Its stated consequence ("he now sits frozen forever, an extra action his only legacy") holds only for a session that never saves.

### What reproduces (numbers)

`probe_1_serial.py` — the static census:

```
'administrative' in Marshal class source          : False
'administrative_strength' in Marshal class source : False
'administrative_location' in Marshal class source : False
fresh Marshal vars() count : 105
to_dict key count          : 105
  to_dict has 'administrative'          : False   vars() has: False
  to_dict has 'administrative_strength' : False   vars() has: False
  to_dict has 'administrative_location' : False   vars() has: False
from_dict mentions 'administrative': False
```

Zero occurrences of the string `administrative` anywhere in `backend/models/marshal.py`. The three attributes are created by assignment in exactly two places and read in exactly those same two files (probe 8/9).

`probe_2_arm.py` — the arm end to end on the shipped 1805 boot:

```
BEFORE  Murat: strength=22000 loc=Franche-Comte  bonus_actions=0 max_actions=4
handler: "Murat has been transferred to administrative duties. Their 22,000 troops
          await future assignment. You now have 5 actions per turn."
AFTER   administrative=True strength=0 location=None
        admin_strength=22000 admin_location=Franche-Comte
        bonus_actions=1 max_actions=5   field=7 admin=1

marshal.to_dict keys containing 'admin': []
AFTER LOAD:
    administrative      : <ABSENT>
    administrative_stren: <ABSENT>
    administrative_locat: <ABSENT>
    strength / location : 0 / None
    bonus_actions       : 1  max_actions: 5
    field / admin       : 8 / 0
 => a recall on the LOADED world would give: strength=0 at 'Paris'
```

### What is NEW — three consequences neither row states

**(1) The slice-9 attrition exemption is defeated by one load.** `probe_4_attrition.py`, both arms on the same board:

```
--- NO LOAD (slice-9 exemption) ---
    in marshals before sweep: True   after sweep: True
--- AFTER A LOAD ---
    in marshals before sweep: True   after sweep: False
    fallen_marshals: [None]
    event: Murat has been eliminated by supply attrition at None
```

`world_state.py:6584` reads `getattr(m, "administrative", False)`; the flag is gone after a load, so `ADMINISTRATIVE_EXEMPT_FROM_ATTRITION` (`world_state.py:50`) no longer covers him. This is the *exact* P1 the slice-9 review round landed a fix for, resurrected by the save. `tests/test_fa26_the_question_is_asked_2026_09_05.py::test_an_administrative_man_survives_the_attrition_sweep` (`:582`) cannot see it — it never saves.

**(2) The max-1-admin rule is reset by a load, and the +1 action compounds.** `probe_3_consequences.py`:

```
PRE-LOAD   : field=7 admin=1 bonus=1 max=5
POST-LOAD  : field=8 admin=0 bonus=1 max=5
  second transfer accepted: "Lannes ... You now have 6 actions per turn."
POST-2nd   : field=7 admin=1 bonus=2 max=6
POST-LOAD-2: field=8 admin=0 bonus=2 max=6   (two ghosts, two permanent AP)
```

Both copies of the one-admin gate (`disobedience.py:1600` `if admin_count == 0`, `meta_executor.py:1580` `if len(admin_marshals) >= 1`) read `get_admin_marshals()`, which reads the lost flag. Save-load-freeze is an **unbounded military-AP farm**, one AP per marshal, permanently.

**(3) The ghost is counted as a FIELD marshal after a load** (`field: 7 → 8`), which is the FA-N77 family one layer over: `get_field_marshals` filters on the flag that no longer exists.

### The real seam (symbols, current lines)

| what | symbol | file:line TODAY | row says |
|---|---|---|---|
| the freeze | `DisobedienceSystem.handle_redemption_response`, `elif choice == 'administrative_role'` | `disobedience.py:1798-1826` | — |
| the promise (option) | `_create_redemption_event` option builder | `disobedience.py:1604` | FA-71: 1512 |
| the promise (handler msg) | same handler | `disobedience.py:1822` | FA-71: 1698 |
| the `Phase 4` comment | same | `disobedience.py:1799` | FA-71: 1698 |
| zeroing | same | `disobedience.py:1804-1805` | FA-71: 1701-1704 |
| the ONLY restore | `MetaExecutor._execute_debug`, `elif ability == "admin"` | `meta_executor.py:1551-1601`; the `administrative = False` write is **`:1559`** | FA-71: 1541 |
| `_execute_debug` head | | **`:760`** | FA-71: 742 |
| `_execute_cheat` head | | **`:2282`** | FA-71: 2256 |

**Every FA-71 line citation is stale by +18 to +103.** Navigate by symbol.

### The debug restore, step by step (the mirror the verb must implement)

`meta_executor.py:1558-1566`, verbatim:

```python
if getattr(marshal, 'administrative', False):
    marshal.administrative = False
    strength = getattr(marshal, 'administrative_strength', 0)
    location = (getattr(marshal, 'administrative_location', None)
                or world.get_nation_capital(marshal.nation) or 'Paris')
    marshal.strength = strength
    marshal.location = location
    marshal.clear_iron_resolve()            # MC-1c: back on the map, no coil
    world.bonus_actions = max(0, getattr(world, 'bonus_actions', 0) - 1)
    # message quotes world.calculate_max_actions()
```

Five writes, one derived read. **It is a bad mirror in five measured ways** (`probe_10_hazards.py`):

| # | hazard | measured |
|---|---|---|
| 1 | restore location never re-validated | froze at Franche-Comte; province falls to Austria; restore puts **22,000 men into an Austrian-held province** with no battle, no crossing check, no supply check. `get_nation_capital` also **ignores the controller** — after Paris falls it still returns `'Paris'` |
| 2 | marshal index left stale | `index[None]` still `['Murat']` after the restore; `index['Franche-Comte']` still `['Lannes']` only. The non-indexed `get_marshals_in_region` finds him; every `*_indexed` hot-path reader does not, until the next `_advance_turn_internal` / `refresh_marshal_indexes` |
| 3 | a pre-fix save | restore gives **`0 men at 'Paris'`** and still refunds the AP (`bonus_actions 1 → 0`) |
| 4 | stale fields survive | after the restore: `administrative=False` but `admin_strength=22000`, `admin_location='Franche-Comte'` — never cleared |
| 5 | no liveness guard | a captured man (`captured_by`, strength 0 by W6-7 design) and a non-administrative man both reach the branch |

The gate's own blessed wording — *"at the capital or richest home province"* — is `recruitment.find_spawn_region(world, nation)` (`recruitment.py:95`) **verbatim**, and it already handles the fallen capital correctly (measured: `Paris` → after Paris falls, `Berry` → after total loss, `None`).

### The admin-AP mechanism (asked for explicitly)

Two pools, and they are **not the same pool**:

- **Military:** `world.calculate_max_actions()` = `4 + world.bonus_actions` (`world_state.py:9124-9131`). The Staff transfer buys **+1 MILITARY action**, permanently. `bonus_actions` is uncapped, serialized (`:907`, `:6954`, `:7547`).
- **Admin:** `world.admin_actions_remaining` / `max_admin_actions`, a flat **2 per turn** (`world_state.py:913-914`, refilled `:9752`).

The declaration mechanism is a single frozen set:
```
backend/commands/meta_executor.py:30
ADMIN_ACTIONS = {"recruit", "build", "repair", "grant_dotation",
                 "grant_pension", "revoke_pension", "recruit_marshal", "build_fleet"}
```
imported at `executor.py:47`, consumed at **`executor.py:1224`** `is_admin_action = action in ADMIN_ACTIONS and is_player_action_check`, which gates on `admin_actions_remaining < 1` at `:1298-1304` and charges via `world_state.py:6817-6819`. `recruitment.py:33 RECRUIT_MARSHAL_AP = 1` is the documented precedent constant.

**Record this on the row:** the ruling prices the recall in a pool the transfer never touched. Freeze buys a military AP; recall spends an admin AP. That is not wrong — but it means the round trip is net-positive in military actions and near-free, so the brake is the cooldown, not the price.

### The 12-step checklist, measured

| # | site | current contents / shape | what `recall_marshal` needs |
|---|---|---|---|
| 1 | `validation.VALID_ACTIONS` | 54 entries; `recruit_marshal` present | add one |
| 1b | `validation.ADMINISTRATIVE_ACTIONS` (`:196-199`) | frozenset of 8: `grant_pension, revoke_pension, grant_dotation, recruit_marshal, recruit, build, repair, garrison`; feeds `NEVER_STRATEGIC_ACTIONS` (44) | add one — **defence in depth only**: `recall` is *not* in the strategic march-verb table (`strategic_parser.py:274/283/297` has `march`/`withdraw`/`fall back`, no `recall`), so the FA slice-7 `withdraw Ney's rente` pathology is not live for this verb. The slice-7 pin at `test_fa_slice7…:454` iterates a hard-coded list and does not break on an addition |
| 2 | executor body | `economy_executor.py:787 def _execute_recruit_marshal` | new `_execute_recall_marshal` beside it |
| 2b | dispatch | `executor.py:2315-2316 elif action == "recruit_marshal": result = self._economy._execute_recruit_marshal(...)` | one `elif` |
| 2c | admin-AP | `meta_executor.py:30 ADMIN_ACTIONS` | add one — this is what makes it 1 admin AP |
| 3 | `parser.py` `valid_actions` | list at `parser.py:756`, 51 entries; `recruit_marshal` ×4 refs; **`recall` ×0 refs** | add the row |
| 4 | `world_state._action_costs` | dict at `:937`; `"recruit_marshal": 1` at `:976`; `.get(action, 1)` defaults to 1 anyway | `"recall_marshal": 1` |
| 5 | `llm_client` mock | `recall` appears **exactly once**: `:1969` `re.search(r'\b(guard\|recall\|port\|station)\b', …)` inside the `set_fleet_posture` arm, which **also requires `\bfleet\b`** | new arm; ordering matters but the collision is narrow (see below) |
| 6 | `prompt_builder` few-shot | zero `recruit_marshal` hits — the precedent shipped with none | optional |
| 7 | `executor.py:1480 objection_actions` | literal list of 12; no admin verb is in it | **leave out and pin the absence** |
| 8 | serialization | **the blocker** — three fields into `Marshal.__init__` + `to_dict` + `from_dict` | copy the `redemption_cooldown_until` idiom verbatim: `marshal.py:323` / `:1630` / `:1817` |
| 9 | `display_names` | `ACTION_DISPLAY` (41) `'commissions'`; `DEFIANCE_DISPLAY` (41) `'commissioned a marshal'`; `OBJECTION_DISPLAY` (41) `'commissioning a marshal'` | three rows |
| 10 | `campaign_log._DEFIANCE_DISPLAY` / `_OBJECTION_DISPLAY` | both len 41, both carry `recruit_marshal` (re-exported from `display_names`) | mirror |
| 11 | `campaign_log.CAMPAIGN_LOG_TYPES` | **len 160**, `marshal_commissioned` present | a new type flips **10 test pins** (see below) — or reuse an existing type and flip none |
| 12 | `tests/data/parser_golden_corpus.json` | 436 entries; **675 params** (4 `live_only` + 243 both-world + 189 single-world); 3 `recruit_marshal` rows, all `world: "1805"` → 1 param each; 3 `set_fleet_posture` rows; **0 rows mention `recall`** | 2 positives + 2 negative guards → 675 + N |

**`len(CAMPAIGN_LOG_TYPES) == 160` is pinned in TEN test files** (the two in-code comments at `campaign_log.py:136` and `withdrawal.py:1113` both say *"nine"* — stale by one):
`test_bph_a_term_ownership.py:303`, `test_ca9_row3_a7_jealousy_note.py:456`, `test_ca9_row3_phase_a.py:154`, `test_ca9_row3_q2_council_command.py:433`, `test_campaign_log.py:138`, `test_fa_slice11_the_briefing_tells_the_truth_2026_09_05.py:235`, `test_igr_a_honest_copy.py:197`, `test_igr_b_campaign_log_readable.py:546`, `test_igr_f_envoy_digest.py:824`, `test_wo_slice4_the_capital_speaks.py:794`.

---

## FA-71 — the one-way door (`BUG_FIXES.md:3342`, P3, VERIFIED Sept 2)

**VERDICT: REPRODUCED, but under-severed and stale-lined.**

- Its census claim is **exact**: `grep -rn 'administrative = False' backend/` → **one hit**, `meta_executor.py:1559`, inside `_execute_debug` behind `if not debug_mode: return {"success": False, …}`. Writes of `True`: two (`disobedience.py:1800`, `meta_executor.py:1588`).
- Its **player_consequence is understated**. "loses that corps for the rest of the campaign" is the no-save case. With a save/load the corps *and the marshal* are destroyed (§above). On that evidence the row is at least P2.
- Its `fix_shape` (a) — *"restore `administrative_strength` at `administrative_location`/capital"* — **prescribes the enemy-held-province hazard**. The gate's own wording ("the capital or richest home province") is the safer one.
- Its `fix_shape` phrase *"recompute max actions"* is a **no-op**: `calculate_max_actions` is derived, not stored.
- Its `behaviour_test` (*"`world.calculate_max_actions()` drops by exactly 1; refusal when AP is short; the debug branch stays byte-identical"*) is sound and directly measurable.
- Its `already_filed` (WO-36 fixed the client echo) is **correct** — confirmed at `main.gd:4453` and `:4504-4511`.

---

## Corrections to the PRIOR repro (`REPRO_J4_the_diversion_and_the_recall.md`)

Three of its build instructions are wrong; two change the slice.

**1. Step 12 is NOT enforced by CI.** The prior repro says *"`test_command_robustness_cr1_eval_harness.py`'s action-coverage gate FAILS CI for any mock-reachable action with zero corpus coverage, so this step is mandatory, not optional."* Measured: the gate iterates `MOCK_REACHABLE_ACTIONS`, a **hand-maintained list of 52** at `tests/test_command_robustness_cr1_eval_harness.py:40` — and **`recruit_marshal`, the precedent it cites, is not in it**, despite being demonstrably mock-reachable (`commission Grouchy` → `recruit_marshal`, target `'Grouchy'`). The gate would pass with zero corpus rows. Write the rows *and* add the id to the hand list, or the gate stays blind.

**2. Step 3b's hazard does not exist.** The prior repro warns the addressee resolution may not find an administrative marshal. Measured (`probe_6`, live `/command`):

```
world.get_marshal('Murat')            -> Marshal(Murat, 0 troops at None, …)
'Murat' in get_marshals_by_nation     -> False
'Murat' in get_field_marshals         -> False
'Murat' in get_admin_marshals         -> True
POST /command "Murat, hold"           -> success=True
   "Murat refuses outright: 'I would rather attack than sit idle.'"
```

He is fully addressable today; the exclusions live in the **roster helpers** (`get_marshals_by_nation` `strength > 0`, `find_nearest_marshal_within_range` `if getattr(marshal,'administrative',False)`, `clarification.py:139`), which the address path does not use. No explicit lookup is needed.

**3. The client sites are a shorter list than stated.** The prior repro names five `.gd` sites. Measured: `redemption_dialog.gd:77-79` renders `opt.get("text")` / `opt.get("description")` **verbatim from the backend option dict**, and `main.gd:4509-4511` renders the backend `msg` verbatim under the banner. **The copy fix is backend-only — zero `.gd` diff.** Only `main.gd:4426` is a hard-coded literal (`Type: 'grant_autonomy', 'administrative_role', or 'dismiss'`), and it carries no promise. A Generals-card chip would be the only real `.gd` work, and it is optional.

**4. One collision the prior repro missed.** Its `recall`-collision analysis is right but incomplete:

```
'recall Murat'                  -> action=None            (unparseable today)
'recall the fleet'              -> set_fleet_posture       <- the known one
'recall the fleet to port'      -> set_fleet_posture
'recall Villeneuve'             -> action=None             (no `fleet` word — safe)
'recall the squadron'           -> action=None             (safe)
'restore Murat to command'      -> repair                  <- MISSED
'reinstate Murat' / 'bring Murat back' / 'Murat, return to the field' -> None
```

`restore` is already claimed by the `repair` verb. It must not be a synonym for the new one.

**5. Its line citations are inherited from the row and are stale** (see the table above).

---

## Pins that flip

Baseline measured green today: `test_administrative_role.py` + `test_serialization_enforcement.py` + `test_redemption_v2b.py` + `test_fa26_…` + `test_recruitment_rework.py` + `test_command_robustness_cr1_eval_harness.py` + `test_fa_slice7_…` + `test_naval_channel_gate.py` = **1004 passed**.

| pin | today | after the fix |
|---|---|---|
| `test_serialization_enforcement.py::TestMarshalSerializationEnforcement::test_all_marshal_fields_serialized` (`:214`) | **structurally blind** — `get_instance_attributes` (`:30-40`) is `vars()` on `create_fully_populated_marshal()` (`:49`), which sets `autonomous`/`autonomy_turns`/`autonomy_reason` but **never `administrative`**. Measured missing-set today: `[]` | **BINDS**. Simulated: with the three fields present the missing-set is `['administrative', 'administrative_location', 'administrative_strength']` → RED until `to_dict` carries them, then green. This is the *desired* direction |
| `…::test_marshal_roundtrip_preserves_all_fields` (`:233`) | green, blind | binds the same way |
| `test_administrative_role.py` — `test_admin_role_stores_strength/location` (`:25`,`:44`), `test_admin_role_increments_bonus_actions` (`:64`), `test_admin_role_increases_max_actions` (`:80`), `test_admin_role_result_includes_new_max_actions` (`:95`), `test_admin_role_not_available_if_one_exists` (`:113`), `test_get_field_marshals_excludes_admin` (`:343`), `test_get_admin_marshals_includes_admin` (`:363`), `test_bonus_action_persists_after_advance_turn` (`:298`), `test_multiple_turns_maintain_bonus` (`:321`) | all green (70 in file) | **all unchanged** by the serialization fix; the recall verb adds new tests beside them. `test_multiple_turns_maintain_bonus` is the one to read carefully: the AP must survive turns and must *not* survive the recall |
| `test_fa26_…::test_an_administrative_man_survives_the_attrition_sweep` (`:582`) | green, no save/load arm | unchanged; **this is the natural home for the save/load arm** |
| `test_fa26_…::test_exemption_off_reproduces_the_destruction` (`:598`) | green (flips the module flag) | unchanged |
| `test_fa_slice7_…::test_an_administrative_verb_never_marches` (`:445`) | asserts 8 named verbs ARE in `NEVER_STRATEGIC_ACTIONS` | additive — no flip |
| any `len(CAMPAIGN_LOG_TYPES) == 160` | ten files | **only if a new log type is added**. A recall can reuse `marshal_commissioned` or emit no log type at all and flip none |
| `test_command_robustness_cr1_eval_harness.py` | 686 tests, 675 corpus params | 675 + N params; the coverage gate stays green either way unless the id is added to the hand list |
| copy pins | **none** — the only test occurrence of "restoration" is a docstring at `test_administrative_role.py:23`; `godot-client` has zero readers of `administrative_strength`/`administrative_location`/`troops_frozen` | the promise rewrite flips nothing |

`docs/SAVE_FORMAT_REFERENCE.md` documents `bonus_actions` (`:41`, `:184`) and has **no rows for the three marshal fields**; `docs/MODDING_FORMAT.md` has zero `administrative` hits. Both need a row.

---

## Series / harness risk: **ZERO, measured**

`probe_11_series.py` mirrors the `BASELINE_SERIES` driver (`test_ai_intent_threat_migration.py::_emit_series`, `PYTHONHASHSEED=0`, `SOVEREIGN_SEED=historical`, `LLM_MODE=mock`) for 20 turns:

```
turns with a standing redemption question : 5
administrative marshals seen              : 0
min French trust per turn: [40,40,40,40,40,40,38,36,34,32,30,28,26,24,22,20,18,16,14,12]
French trust at t20: Bernadotte 12, Massena 18, Lannes 43, Murat 61, Soult 70, Ney 75, Davout 85
```

The redemption **question** does fire on the ambient board (the FA-26 erosion tick bites from ~turn 16), but **`administrative` is never set**, because the only production caller of `handle_redemption_response` is `backend/main.py:4051` (`POST /respond_to_redemption`) and the series driver calls `tm.end_turn(game_state)` directly with no HTTP and answers nothing. So:

- Adding three `__init__` fields with defaults `False / 0 / None` changes no behaviour — every existing read is `getattr(m, 'administrative', False)` with the identical default.
- `to_dict` is never called inside the series (it records `threat_level` ints and province counts).
- The recall verb is player-typed and has no AI rung; `check_redemption_threshold` returns `None` for any non-player nation (`disobedience.py:1703`), so `administrative` is unreachable for AI marshals by construction.

**M1–M7 (`tests/test_combat_sweep_metrics.py`): zero occurrences of `administrative`, `redemption` or `trust` in the whole file.** No harness risk.

*(Caveat, stated rather than buried: byte-identity here is a fact about the harness — it never answers a modal — not evidence that the change is inert in a played campaign. A played campaign is exactly where the load-destroys-the-marshal defect lives.)*

---

## Recommended build shape

**Land it in two commits, serialization FIRST.** The serialization half is a standalone P2 fix that does not depend on the gate's ruling, and shipping the verb without it means `recall` restores 0 men at `Paris` on every loaded campaign.

### Commit 1 — "the frozen men survive the save" (no new verb)

1. Declare in `Marshal.__init__` beside `redemption_cooldown_until` (`marshal.py:322-323`):
   `self.administrative: bool = False`, `self.administrative_strength: int = 0`, `self.administrative_location: Optional[str] = None`.
2. `to_dict` (`:1629-1630` block) + `from_dict` (`:1816-1817` block), `.get()`-defaulted. This turns `test_all_marshal_fields_serialized` from blind to binding.
3. `SAVE_FORMAT_REFERENCE.md` rows.
4. Falsifiable pins, all of which are RED before this commit and green after: (a) the round trip preserves flag/strength/location; (b) **the attrition sweep spares him across a save/load** (the measured elimination); (c) `get_admin_marshals()` still returns 1 after a load, so the one-admin gate holds and a second transfer is refused; (d) `get_field_marshals()` still excludes him.

### Commit 2 — the verb

- **Action id `recall_marshal`**, executor `economy_executor._execute_recall_marshal` beside `_execute_recruit_marshal` (`:787`), dispatched by one `elif` at `executor.py:2315`.
- **Carry the name in `command["target"]`, not `command["marshal"]`** — the `recruit_marshal` precedent (measured: `commission Grouchy` → `target='Grouchy'`, `marshal=None`). It keeps the verb out of the objection battery and out of every marshal pre-gate that reads `strength`/`location`, both of which are degenerate for an administrative man.
- **Location:** `recruitment.find_spawn_region(world, nation)` — the gate's blessed wording verbatim, and the only helper that respects the controller. Optionally prefer `administrative_location` *only when `world.regions[loc].controller == marshal.nation`*; **never** the debug arm's `or 'Paris'`. If `find_spawn_region` returns `None`, refuse honestly ("there is no soil left to muster him on").
- **Do everything the debug arm forgets:** clear `administrative_strength`/`administrative_location` after the restore; call `world.refresh_marshal_indexes()`; guard on `administrative is True`, `not captured_by`, and `administrative_strength > 0` (the pre-fix-save case → refuse rather than silently restoring 0 and refunding the AP).
- **Price:** `ADMIN_ACTIONS` membership + `_action_costs["recall_marshal"] = 1` + `should_end_turn` parity with `recruit_marshal`. Note on the row that the reward is a *military* AP and the price an *admin* AP.
- **Cooldown:** **no new field.** `marshal.redemption_cooldown_until` already exists, is serialized (`marshal.py:323/1630/1817`) and is stamped `current_turn + 5` at `disobedience.py:1767` for every redemption answer. Measured: the arm does **not** reset trust, so a recalled man returns at the trust that broke him and the question re-fires after the cooldown — a fair loop, and AP-neutral (freeze +1 / recall −1).
- **Refactor the debug arm to call the new helper** so the two cannot drift, and pin that `/debug admin` is byte-identical for the *freeze* direction.
- **Corpus:** two positives (`recall Murat`, `recall Murat to the field`), `world: "1805"`, plus **three** negative guards — `recall the fleet` and `recall the fleet to home waters` → `set_fleet_posture`, and `restore Murat to command` → `repair` (the collision the prior repro missed). Add `recall_marshal` to `MOCK_REACHABLE_ACTIONS` or the gate stays blind.
- **Copy:** rewrite `disobedience.py:1604` and `:1822` to name the verb and its price; delete the `Phase 4` comment at `:1799`. **Backend-only — no `.gd` diff.**
- **No new campaign-log type** unless a beat is genuinely wanted; reusing `marshal_commissioned` or emitting none keeps all ten `== 160` pins untouched.

### One thing to decide at the gate, not in the build

The gate's wording is *"restores `administrative_strength` at the capital or richest home province"*; FA-71's `fix_shape` says *"at `administrative_location`/capital"*. **These are different rules and the second is the measured hazard** (22,000 men teleported into an Austrian-held province with no battle). Recommend the gate's own wording as the default, with the `administrative_location`-if-still-held preference as an explicit, tested option. Record whichever is chosen — this is a sixth member of the `fix_shape`-vs-`summary` family the build has hit before.