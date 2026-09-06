All measurements are complete and the repo is untouched by me (the `combat_executor.py` diff and the `REPRO_K1` file belong to a sibling agent, not to this probe).

---

# FA-S12-1 & FA-S12-2 — reproduction report

Probes (all read-only, all under `C:\Users\User\AppData\Local\Temp\claude\C--Users-User-PycharmProjects-project-sovereign-map\d3a697cd-1535-475d-bd1b-457545b1c421\scratchpad\s14\J_strays\`):

| file | what it measures |
|---|---|
| `p1b_no_corridor.py` | the two-arm synthetic geometry (stranding-free peace vs corridor-open peace) |
| `p2_what_he_is_told.py` | whether bypassing `if not grants:` helps; the WO-17 direction term |
| `p4_told2.py` | the honest refusals the player actually gets; dispatch silence |
| `p5_ambient.py` | instrumented 40-turn `BASELINE_SERIES` replica — corridor + elimination + threat census |
| `p6_castanos.py` | the ORGANIC FA-S12-1 case on the shipped seeded board |
| `p7_fixa_arms.py` / `p8_fixa_full.py` / `pC_fixa_final.py` | fix-(a) flip arms |
| `p9_attrib.py` | attribution of the fix-(a) series divergence |
| `pA_elim_arms.py` | FA-S12-2 six-arm flip experiment |
| `pB_neighbourhood.py` / `pD_extras.py` / `pE_lord_exit.py` | residue and the fifth exit |
| `fixa_plugin.py` / `fixb_plugin.py` | pytest plugins that simulate each fix to enumerate flipping pins |

My replica emits `BASELINE_SERIES` byte-for-byte on arm 0 in every experiment, so every divergence below is attributable.

---

## FA-S12-1 — no corridor when nobody was stranded

**VERDICT: REPRODUCED, and WIDER in mechanism. The row's diagnosis names the wrong seam for the fix, its own done-when names the wrong pin, and there is an organic case on the shipped seeded board that the row does not know about.**

### What reproduces

**Synthetic (`p1b`).** Volhynia French, whole French army at Paris, Russians home; France↔Russia WAR → PEACE strands nobody. Measured: `grants = {}`, **0 `evacuation_granted` events**, `can_enter_territory(France→Russia) = False`. Davout then marches into Volhynia. Fifteen real ticks of `process_evacuation_grants`:

```
stranded=True  dist_home=None  road_order=False  road_home_offered=False
events: 0        warnings: 0     internment: none    grants: {}  (all 15 turns)
```

Arm B — same corps, same province, same turn, but Massena was standing in Volhynia when the ink dried (`grants = {'France|Russia': 11}`, beat: *"1 corps stands on the wrong side of the new frontier… safe passage for 10 turns"*): Davout is handed the road at t2 with the mid-treaty beat, warned 2/1/0 on t2/t3/t4, interned t5. **The outcome for two identically stranded corps turns entirely on whether a third corps was caught out.**

**Organic, on the seeded ambient board (`p6`) — this is the strong evidence.** Spain's **Castanos**:

| turn | location | controller | stranded | dist_home |
|---|---|---|---|---|
| 16 | Guyenne | France | False | 2 |
| **17** | Guyenne | **Britain** | **True** | 2 |
| 18–41 | Guyenne | Britain | True | **None** |

The **Britain|Spain peace is signed at turn 16** — `marching=[] cut_off=[]` → the provisional grant is rolled back. Britain takes Guyenne under him at turn 17. He then stands there for **25 consecutive turns (t17–t41)** with `strategic_order = None`, `road_home_offered = False`, ringed by Britain (PEACE) and Austria (PEACE). The only thing the game ever says about him is one line **23 turns late**, attached to an unrelated Spain↔Switzerland treaty: *"Castanos can find no land route home at all — cut off, and that passage must be negotiated."*

**Corridor census, 40 turns:** `open_evacuation_corridor` fires **6 times and all six roll back** — five "nobody stranded", one "everyone cut off". **Zero corridors ever stand on the ambient board.** Stranded-with-no-standing-grant sightings: **26** (Castanos 25, Britain/Paget 1).

### What is false, or narrower than the row claims

1. **The seam the row names for the fix is not the seam.** The row says "slice 12's top-up — keyed on a standing grant — never reaches him". Measured (`p2`): **bypassing `if not grants:` is a no-op.** With no grant, `_nearest_home_region` returns `None` and `offer_road_home(world, "France")` returns `[]` — because `distance_home` routes `with_grant=True`, so the road *only exists because the grant does*. The corps is classified **cut off**, and the tick would refuse him honestly. **The rollback in `open_evacuation_corridor` is the seam; the early return is a symptom.**

2. **A minimum window ALONE is also a no-op.** Measured (`p7`, `MIN_WINDOW=3`): five min-window grants written, **`grants standing per turn` is empty on every one of the 40 turns**, Castanos unrescued. The `if not any(stranded_by_nation.get(n) for n in parts): grants.pop(key)` retire rule pops the grant **inside the same `advance_turn` that wrote it.** Fix (a) needs *both* halves: don't roll back, **and** floor the retire.

3. **The done-when names a pin that is already fixed.** `tests/test_fa_slice12_the_road_home_2026_09_05.py::test_a_cut_off_corps_is_still_refused_honestly` already stages a second reachable corps and asserts `world.evacuation_grants` is truthy — its docstring's third paragraph *is* the note the row asks for. The pin still green about a line it never executes is the older one:
   `tests/test_win_d3_road_home.py::TestCutOffCorps::test_a_cut_off_corps_is_never_interned` — measured **15 of 15 tick calls return at `if not grants:`; the `dist is None` guard runs zero times.** (Its two siblings on the same `_strand_beyond_rescue` fixture are fine: `test_the_dispatch_says_so_plainly` reads an event logged before the rollback, and `test_no_order_is_invented_for_a_corps_with_no_road` genuinely reaches `offer_road_home`'s `if not destination` guard.)

### The real seam

`backend/game_logic/withdrawal.py::open_evacuation_corridor` — the `if not marching and not cut_off:` block that restores/pops the provisional grant — **jointly with** `::process_evacuation_grants`'s `if not any(stranded_by_nation.get(n) for n in parts): grants.pop(key, None)` retire rule. Neither alone is sufficient.

### Evaluating both resolutions

**(a) minimum corridor window.** Built as a real fix would be sited — *inside* `WITHDRAWAL_ACTIVE`, *skipping any transition whose new state already opens the border*, *plus a retire floor* (`pC_fixa_final.py`):

| | control | fix (a), MIN_WINDOW=3 |
|---|---|---|
| Castanos | Guyenne t17–t41, no road, no word | road at t17, **home at Aragon t18** |
| corridors opened | 0 standing | 4 (`Austria\|Bavaria`, `Austria\|KoI`, `Britain\|Spain`, `Spain\|Switzerland`) |
| corridor-turns across 40 turns | 0 | **12** |
| final provinces | Austria 26 / Britain 21 / France 5 / Spain 9 … | **identical in every nation** |
| Trojan sightings | 0 | **0** |
| `BASELINE_SERIES` | matches | **index 24: 3 → 13**, converges at 25 |

*The "already opens the border" skip is load-bearing*: it removes two of the five naive corridors (the t2 Russia transitions to states that already permit entry) **and** it is the difference between 0 and 1 flipped pins.

**Is (a) safe from the Trojan-corridor exploit? Yes, and by construction, not by luck.** WO-17's direction term is `has_evacuation_grant(mover_nation, host, mover_location)` → `_corridor_is_for` → a memoised `is_stranded_at`. Direct measurement with a grant standing: Ney at **Paris** → **False**; Davout at **Volhynia** → **True**. And the source-side guarantee is stronger than the behavioural one: `tests/test_wo_slice13_corridor_direction.py::TestTheCensusPin::test_every_relocation_seam_names_its_mover` allows exactly **one** bare `can_enter_territory` call in the whole backend (`war_council.py`, which relocates nobody). So a corps standing anywhere it could already walk home from has no claim, no matter which seam moves it.

**(b) document it as deliberately uncovered.** Measured what the player gets today. If he **asks**, he is answered honestly:

- `issuance_road_refusal`: *"There is no open road to Paris, Sire — every route crosses Russia's closed frontier at Lithuania. Secure passage (open borders, or war) or name a province we can reach."*
- `move_refusal_probe`: *"Cannot enter Ukraine — it is controlled by Russia (diplomatic state: PEACE). Open borders or higher required."*

Both are true — and both give advice that is **wrong for this case**: the instrument that exists for exactly this situation is the corridor, and the game declined to issue one. Unprompted, the game says **nothing**: five ticks of `build_morning_dispatch` never name Davout or Volhynia, and no notification is raised. So (b) is not "add a sentence to the spec" — to be *honest* it needs a new producer that runs with `grants` empty, i.e. removing the same early return and adding a "stranded, no corridor" arm. **That is comparable work to (a) and its deliverable is a corps who is told he is stuck, rather than a corps who gets home.**

### What the filed fix would break

The naive siting flipped exactly two of 113 pins, and both are the design constraints, not accidents:

| pin | why it flipped | constraint it teaches |
|---|---|---|
| `test_win_d3_road_home.py::TestTheMeasuredDefect::test_control_arm_reproduces_the_stranding` | the min-window write ran outside the `WITHDRAWAL_ACTIVE` guard | the write must sit **inside** the guard, or the whole slice's control arm is destroyed |
| `test_win_d3_road_home.py::TestGrantChokepoint::test_vassalization_needs_no_corridor_because_it_opens_the_border` | a corridor was written for a WAR → VASSAL transition | **skip any transition whose new state already permits entry** — VASSAL/ALLIANCE need no corridor, and writing one there re-opens the §3.4 "must not become open borders" question for no benefit |

With both constraints honoured: **113 / 113 pass** across `test_win_d3_road_home.py`, `test_fa_slice12_the_road_home_2026_09_05.py`, `test_wo_slice13_corridor_direction.py`.

Not tested by anything, and worth a pin either way: including or excluding the **all-cut-off** case in the min window is measurably indistinguishable on this board (identical series, identical corridors) — because by the time the one all-cut-off peace fires (Spain|Switzerland, t40) Castanos is already home under the fix.

### Series / harness risk

- **`BASELINE_SERIES`: YES, one index.** `index 24: 3 → 13`, converging at 25. Attributed by instrumenting `reduce_threat` in both arms: the **Switzerland `vassal_rebellion` fires one loop-turn later (23 → 24)**. It is a timing shift, not a design change to France's threat, and the final province distribution is identical in all eighteen nations. One flip lever + one re-record.
- **M1–M7: structurally impossible.** `tests/test_combat_sweep_metrics.py` contains **0** occurrences of `end_turn`, `advance_turn`, `withdrawal`, `evacuation`.

### Recommended build shape

Take **(a)**, with the three constraints the measurement produced:
1. Write the window **inside** the `WITHDRAWAL_ACTIVE` guard (or the control arm dies).
2. **Skip** when the new diplomatic state already opens the border (`can_enter_territory(..., ignore_evacuation=True)`).
3. Add a **retire floor**, not just a window — the "everybody is home" pop otherwise kills it in the same `advance_turn`.

Flip lever, one re-record attributed to the Switzerland-rebellion timing shift, and re-point the *older* inert pin (`test_win_d3_road_home.py::TestCutOffCorps::test_a_cut_off_corps_is_never_interned`) at whatever the ruling is — it will begin executing the `dist is None` guard for the first time if the all-cut-off case is included in the window.

---

## FA-S12-2 — elimination is a fourth vassal exit

**VERDICT: REPRODUCED exactly — every figure in the row is right. But it is WIDER (a fifth silent exit in the same handler is strictly worse), and the row's own completion definition is WRONG.**

### What reproduces

- `_eliminate_nation` fires **exactly twice in 40 turns**: **Bavaria** at `current_turn=9` (`was_vassal_of=None`) and **KingdomOfItaly** at `current_turn=10`, `was_vassal_of=France`, `loyalty=93`, `own_vassals=[]`, `marshals=[]`, `assimilated_corps=[]`.
  *Sampling note*: the call fires while `world.current_turn == 10`; the vassal dict first reads without KoI at turn 11. The row's "turn 11" is right as the player reads it; the code's clock says 10. Both are defensible — say which you mean in the pin.
- **Holland 92 on t10 and 92 on t11** — exact. **Switzerland 74 → 72**, its normal −2 drift — exact.
- `complete_vassal_break` is called **once** in 40 turns: Switzerland, t25, the WAR exit. **Never** on the elimination path. `reduce_threat(10, "vassal_rebellion", target=France)` fires once, at t25.
- Residue after KoI's elimination: no CS membership leak, no cooldown, no popup residue; a ghost `Austria|KingdomOfItaly: -80` relation row already survives elimination by design.

### The six-arm flip experiment (`pA_elim_arms.py`)

Each effect applied alone, after the row is popped — the ordering `check_vassal_rebellion` uses:

| arm | effect | `BASELINE_SERIES` | first divergence | board at t41 |
|---|---|---|---|---|
| **0** | control | **matches** | — | France 5, Austria 26 |
| **1** | full `complete_vassal_break` | moves | **index 10: 55 → 45** | **France 4, Austria 27** |
| **2** | `reduce_threat(10)` only | moves | **index 10: 55 → 45** | identical to control |
| **3** | sibling loyalty −10 only | moves | **index 18: 31 → 21** | identical to control |
| **4** | relation −50 only | **matches** | — | identical; writes `France\|KingdomOfItaly: -50` |
| **5** | marshal hand-back only | **matches** | — | identical (no subject) |

**Two independent findings the row does not have:**

1. **TWO arms move the series, at DIFFERENT indices.** The row's done-when — *"a re-recorded series attributed to the `reduce_threat` lever alone"* — would be a **false attribution**. `reduce_threat` moves index 10; the sibling shock moves index 18 on its own. Two levers, or decline one.
2. **Arm 1 has a balance consequence.** France ends with **4 provinces instead of 5** and Austria with **27 instead of 26**, because the sibling shock drops Switzerland 74 → 62 at t10 and it rebels earlier. Against the standing **FA-D27** gate (an unattended France overrun on 8/8 seeds), this makes France strictly worse. That belongs on the ruling, not in a build note.

Arms 4 and 5 are measurably inert on this board — arm 5 for a *stated* reason (KoI's `assimilated_corps = []`), so it is inert by fixture, not by design.

### Which of the four is owed when the satellite is conquered by a THIRD party

The strongest evidence is the engine's own precedent for a non-hostile departure, `vassal.release_vassal` (voluntary release). It applies:

| effect | `check_vassal_rebellion` (all 3 exits) | `release_vassal` (voluntary) | elimination (today) |
|---|---|---|---|
| corps handed back | ✅ | ✅ | ❌ |
| sibling shock −10 | ✅ | **❌** | ❌ |
| lord's threat | −10 | **−8**, `voluntary_vassal_release` | ❌ |
| relation −50 | ✅ | **❌** | ❌ |

So the engine already draws exactly the line the ruling needs: *a departure that is not a betrayal gets the hand-back and the threat relief, not the shock and not the rupture.*

- **Threat reduction — OWED.** France's coalition threat is accumulated fear of a *growing* France, and France is one satellite smaller. `release_vassal` grants 8 for giving one up voluntarily; losing one to a rival is at least as much. This is the arm that should ship, and the one that carries the re-record.
- **Relation −50 — DECLINE, and say so.** It is a rupture term and there is no court left to be angry with. Measured inert on the series; it adds a ghost row beside one that already survives elimination. Declining it costs nothing.
- **Sibling shock — CONTESTED, and the row's reading is not the mechanic's meaning.** In `check_vassal_rebellion` this is a *defiance-is-contagious* signal — another satellite got away with it. A satellite eaten by Austria demonstrates the opposite. There is a second reading (the lord could not protect her), but that is a different mechanic at a different magnitude, and `release_vassal` declines the shock outright. It is also the only arm that costs France a province and it moves the series at a **second** index. **Recommend: decline it in code with the reason, or put it to the user as its own term with its own lever.**
- **Hand-back — see below; on the satellite path it is arguably WRONG.**

### WIDER — the fifth silent exit, in the same handler, and it is worse

The same handler also deletes every satellite of an **eliminated lord**:

```python
for vname in list(self.vassals.keys()):
    if self.vassals[vname].get("lord") == nation:
        del self.vassals[vname]
```

Measured (`pE_lord_exit.py`) with Bavaria hand-built as Austria's satellite carrying its own assimilated corps, then Austria stripped to zero regions:

- `world.vassals["Bavaria"]` deleted with **no event, no notification, no dispatch line** — new `event_log` rows are `['coalition_member_left', 'nation_eliminated']`, and **rows naming Bavaria: `[]`**.
- **Bavaria's own corps `Deroy` is DESTROYED**, tombstoned `{'nation': 'Austria', 'cause': 'nation_eliminated'}` — because the marshal sweep keys on `m.nation`, and an assimilated corps flies the **lord's** flag. Bavaria survives with **3 provinces** and an active-nation row; its army has been annihilated with its lord's and recorded as Austrian dead.
- No threat moves for anyone.

**This is what makes "just call `complete_vassal_break`" the wrong shape**, because the two sub-cases have *opposite* ordering requirements:

- **Lord eliminated** → the hand-back must run **BEFORE** the marshal sweep, or the freed satellite's army dies with its lord.
- **Satellite eliminated** → running the hand-back **before** the sweep **kills** the corps (he acquires `nation = <the dead satellite>` and the sweep destroys him); running it **after** leaves a corps of a nation with no territory, no diplomatic states and no capital. Neither is right. The honest answer is that a conquered satellite's assimilated contingent **stays with the lord** — decline the arm on this path, and state it.

### What the filed fix would break

- **No double-apply.** A grep of every `reduce_threat` call site in `backend/` shows none on the elimination path: `remove_coalition_member` does not touch threat, and the PEACE-teardown `set_diplomatic_state` loop does not either. No sibling-loyalty write, no relation write and no marshal hand-back exists on that path today.
- **No dict-mutation-during-iteration.** `complete_vassal_break` iterates `world.vassals.items()` but mutates only *values*; the handler's own vassal loops use `list(...)`.
- **One real ordering hazard.** `complete_vassal_break` must be called **after** `self.vassals.pop(nation, None)` — otherwise the departing satellite's own row satisfies `other_state["lord"] == lord` and it **docks itself −10**. Every existing caller deletes first; the elimination handler must too.
- A dangling `original_nation` pointing at a dead nation is **mechanically inert**: both VS-4 consumers (`combat_executor.py:782`, `:971`) gate on `origin in vassals`, so a deleted row disarms them. It is cosmetic only in `battle_diorama.py` (its own comment says "display flourish").

### Pins that flip

**Zero, other than the series.** Simulated the full fix via `fixb_plugin.py` and ran **994 tests** across every elimination-touching file — `test_dlf11_eliminated_nations`, `test_phase2bplus_elimination`, all nine `test_vassal_*`, both slice-11 files, `test_settlement_vassalage`, `test_session7_coalition`, `test_igr_d_carve_completable`, `test_na6d_audit`, `test_nation_agendas_formables`, `test_hegemony_engine`, `test_pt_j_rulings`, `test_ca8_gate_closeout`, `test_econ_war_coupling`, `test_hc_g_gazette`, `test_napoleon_np4_peril`, `test_pc15_fix_slice`, `test_phase2b_ai_diplomacy`, `test_phase4_batch6_qol`, `test_pt_e_turn_report`, `test_settlement_recurring_gold`, `test_systems_v3_session6/8`, `test_war_settlement_foundation`, `test_wo_slice12_copy_sweep`, both slice-10 files, `test_fa_slice8`.
Baseline **994 passed** → with the fix **994 passed**.

### Series / harness risk

- **`BASELINE_SERIES`: YES, and the key number is one.** The elimination path fires **twice in 40 turns** and only **once for a satellite** (KingdomOfItaly, lord France, `current_turn = 10`). That single firing is the entire lever. `reduce_threat` alone → **index 10: 55 → 45**. The sibling shock alone → **index 18: 31 → 21**. Both together (arm 1) → index 10 **and** a changed board.
- **M1–M7: structurally impossible.** `tests/test_combat_sweep_metrics.py` contains **0** occurrences of `_eliminate_nation`, `capture_region`, `vassal`, `complete_vassal_break`, `set_diplomatic_state`, `reduce_threat`, `advance_turn`, `end_turn`.

### Recommended build shape

1. **Do not call `complete_vassal_break` from the elimination handler.** Add a sited tail with **per-arm levers** and a comment naming which of the four it declines and why — that is what the row's own done-when allows and what the ordering trap requires.
2. **Ship the threat arm** (`reduce_threat(world, 10, "vassal_lost_to_conquest", target=lord)`), sited **after** `self.vassals.pop(nation, None)`. One lever, one re-record, `index 10: 55 → 45`.
3. **Decline the relation arm in code**, with the reason (no court left; measured inert).
4. **Decline the hand-back on the satellite path**, with the reason (an assimilated contingent has no homeland to return to; and either siting is wrong — before the sweep it dies, after it is an orphan).
5. **Put the sibling shock to the user.** It is the only arm that costs France a province, it moves the series at a *second* index, and `release_vassal` — the engine's own non-betrayal precedent — declines it.
6. **File / fold the fifth exit.** When a **lord** is eliminated its satellites are freed in total silence and their assimilated corps are annihilated and tombstoned under the lord's flag while the satellite survives with territory. That is a bigger defect than the row's own, it needs the hand-back **before** the marshal sweep, and it needs a `record_vassal_break`-style brief.