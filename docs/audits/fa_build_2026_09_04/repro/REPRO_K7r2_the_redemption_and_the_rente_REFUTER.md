All measurements done. The repo is untouched by me (all probes under scratch).

---

# REFUTATION REPORT — FA-S12-1 / FA-S12-2

I re-ran **seven** of the reporter's measurements with my own probes. My arm 0 emits `BASELINE_SERIES` byte-for-byte, so my divergences are attributable.

**Headline: the report's numbers are almost all exact — but its single most load-bearing *mechanism* claim, the one that picks the fix seam, is false on its own flagship case.**

---

## FA-S12-1

### CLAIM 1 (the report's headline correction) — "bypassing `if not grants:` is a no-op; `_nearest_home_region` returns `None`; **the rollback is the seam, the early return is a symptom**"

**MY MEASUREMENT** (`r2_offer.py`, real ambient board, no grant standing):

| turn | `is_stranded` | `_nearest_home_region` | `offer_road_home('Spain')` |
|---|---|---|---|
| **t17** | True | **`Aragon`** | **`[{Castanos, Guyenne → Aragon}]`**, path `['Guyenne','Bordelais','Aragon']` |
| t18 | True | `None` | `[]` |
| t25 | True | `None` | `[]` |

The reason is structural: `is_stranded_at` has **two** arms —

```python
if not _passable(world, nation, location, with_grant=False): return True   # arm 1
return distance_home_from(...) is None                                      # arm 2
```

The reporter measured a **synthetic arm-2** stranding (no road). The **organic Castanos case is arm 1** — *no right to stand here* — which is fully compatible with a road existing. At t17 he had one (`dist=2`).

And it is not inert: an arm that offers the road with no grant (`r5_arms.py` arm E) **moves `BASELINE_SERIES` at index 24: 3 → 13** — *the identical index and values the report attributes to fix (a)* — and moves the board (**Austria 26 → 25**).

**VERDICT: REFUTED as stated; the conclusion NARROWED.** He still doesn't get home, so "you need the corridor" survives — but for a reason the report never found (Claim 6 below), and the guard is a **live lever**, not a symptom.

### CLAIM 2 — "a minimum window ALONE is also a no-op; the retire rule pops it in the same `advance_turn`"
**MY MEASUREMENT** (`r5_arms.py` arm A, window only, `MIN_WINDOW=3`): grants `{}` by t17, Castanos ends at Guyenne, **series byte-identical**. The pop is `withdrawal.py:1067`.
**VERDICT: CONFIRMED.**

### CLAIM 3 — fix (a) = window + retire floor → "road at t17, home at Aragon t18"; index 24: 3 → 13; board identical
**MY MEASUREMENT** (`r6_armA2.py`): `t16 grants={'Britain|Spain': 19}` → `t17 ord=Aragon` → **`t18 Aragon (Spain)`**; first divergence **index 24: 3 → 13**; France 5 / Austria 26 / Britain 21 = control.
**VERDICT: CONFIRMED exactly.**

### CLAIM 4 — the organic case and the corridor census
**MY MEASUREMENT** (`r1_ambient.py`): Castanos **25 stranded turns t17–t41**, all with `order=None`, `offered=False`, `dist=None` from t18. `open_evacuation_corridor` fires **6 times, 0 grants stand**; 5 nobody-stranded + 1 all-cut-off. Eliminations 2; `complete_vassal_break` 1 (Switzerland t25).
**VERDICT: CONFIRMED** — one stale number: the all-cut-off peace (`Spain|Switzerland`) is at **turn 39**, not "t40".

### CLAIM 5 — `test_a_cut_off_corps_is_never_interned` is inert
**MY MEASUREMENT** (spy plugin): **15 calls, 15 return at `if not grants:`, 0 reach the body.**
**VERDICT: CONFIRMED.**

### CLAIMS 7–8 — 113 pins; M1–M7 impossible; census pin
`--co` = **113 collected**. All ten greps over `test_combat_sweep_metrics.py` = **0**. `AUDITED_BARE = {"war_council.py": 1}`.
**VERDICT: ALL CONFIRMED.**

---

## FA-S12-2 — every number reproduces

`r7_elim_arms.py`, my own six arms:

| arm | report | **mine** |
|---|---|---|
| 1 full break | idx 10: 55→45, France 4 / Austria 27 | **identical** |
| 2 `reduce_threat` | idx 10: 55→45, board identical | **identical** |
| 3 sibling −10 | idx 18: 31→21, board identical | **identical** |
| 4 relation −50 | series identical | **identical** |
| 5 hand-back | series identical | **identical** |

Also confirmed: KoI eliminated at `current_turn=10`, `was_vassal_of=France`, `loyalty=93`; Holland **92 → 92**; Switzerland **74 → 72**; `release_vassal` = `reduce_threat(world, 8, "voluntary_vassal_release")` with no shock and no relation term; **no double-apply** (the second `vassal_rebellion` site at `vassal.py:1215` is inside the `not EVERY_BREAK_COMPLETES_ITSELF` legacy fallback); cited lines `combat_executor.py:782` / `:971` are **exact**; **665/665 pass** under both arm 1 and arm 2 on a 15-file elimination subset.

**The fifth exit** (`r8_fifth_exit.py`, Bavaria as Austria's satellite, Austria stripped): Bavaria row **deleted**, Bavaria keeps **3 provinces**, Deroy **destroyed** and tombstoned `{'nation': 'Austria', 'cause': 'nation_eliminated'}`, new events `['coalition_member_left','nation_eliminated']`, **events naming Bavaria: `[]`**.

**VERDICT: CONFIRMED throughout.** The "two levers at different indices" correction to the row's done-when is real and important.

---

## What the reporter MISSED — a builder must know

1. **Castanos is `fortified=True` at t17.** The P1.2 rung's `_fortified_corps_never_marches()` arm returns **`unfortify`**, spending the only turn the road exists. So a 1-turn window cannot work: **the window must outlive the unfortify turn.** `MIN_WINDOW=3` passes by covering t17–t19, not because 3 was reasoned. Pin the window against the *fortified* corps, not the distance.

2. **The road closes because Bordelais falls to Britain at t18** — a third party's conquest, not the treaty. The corridor's real value is that it makes **British** soil passable, creating a *different and more durable* road (via Gascony) that survives Bordelais falling. The report's "he had a road at t17" hides this, and a builder pinning "distance 2 at t17" pins the wrong thing.

3. **Removing the early return is a live lever.** It moves the series at **index 24** *and* the board (**Austria 26 → 25**). The report calls it a no-op. A builder who "cleans it up" alongside fix (a) ships two levers under one attribution — and both fork at the same index, so the arms will not separate them.

4. **The code already states the rule the FA-S12-2 ruling needs**, and the report argues from a hand-built table instead. `vassal.py:2711-2713`:
   > *"losing a satellite relieves the anti-player threat on every other loss path (rebellion −10, release −8, defection-free −10) — the transfer outcome is the same player loss and gets the same relief."*

   That enumerates **four** paths; elimination is the missing fifth. It is a stronger citation than `release_vassal` alone — and it argues for **−10**, the majority rate the other paths use, not the **−8** the report leans toward.

5. **The working tree is NOT clean.** `world_state.py` carries uncommitted FA-N77 + FA-N46, and `withdrawal.py` an uncommitted comment edit. Neither touches the elimination or corridor paths and arm 0 still equals `BASELINE_SERIES`, so no measurement is invalidated — but the report's "HEAD 9ef38da8, clean / the repo is untouched" framing is wrong, and anyone re-deriving these numbers after those land must re-check.

6. Unverified by me (budget): the report's claim that fix (a) opens exactly 4 corridors / 12 corridor-turns, and that the two flipping pins are the two it names.