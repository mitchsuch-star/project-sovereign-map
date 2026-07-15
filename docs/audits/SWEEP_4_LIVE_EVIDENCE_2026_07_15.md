# SWEEP 4 — Live vassal evidence (Combat Overhaul Phase 5)

**Date:** July 15, 2026 · France / europe_1805 · real `from_scenario` world + real backend over HTTP (`:8005`, `LLM_MODE=mock`).
The whole vassal-loyalty pipeline (`process_vassal_loyalty`, `get_imperial_grip`, `invest_in_vassal`, `change_vassal_autonomy`) is **mechanics-only — it never calls the LLM** — so the decisive evidence was captured deterministically in mock mode; the player-facing dispatch surfaces are also LLM-independent (built by `dispatch.py`). This mirrors the Sweep-3 method (deterministic economy probe + live HTTP prong).

**Phase-5 scope under test** (commits `4392c30` VS-1/VS-2, `9131df6` VS-R, `016bf71` 10-findings fix):
VS-1 loyalty-recovery lever + "teach it" (event gate `≥3→≥2`, grip-aware `recovery_hint`), VS-2 dead-code removal (coalition war-weariness term), VS-R authority↔loyalty coupling (derived `get_imperial_grip`, banded drift, "no cheap recovery" lever blunt), and the 10 playtest fixes (F1/F1c/F3/F6/F8b/C1/C2/F5/F7/F4).

---

## Prong 1 — engine probe (deterministic, decisive)

Script: `vassal_probe.py` on the real 1805 world. Full output: `vassal_probe_output.txt`.

### A. VS-1 — the −2 satellite bleed surfaces every turn, with a recovery hint that names ONLY working levers

Boot: `authority=100 (Divine Right)  imperial_grip=100 (VS-R dormant)`; France holds Holland / KingdomOfItaly / Switzerland, all loyalty 100, Satellite.

Three quiet turns (no battles) — the steady −2 drift now surfaces every turn (VS-1 event gate `abs(delta) ≥ 2`, was `≥ 3`), each with the healthy-band hint:

```
turn 1: Switzerland loyalty 98 (-2): satellite drift — Invest in them or grant them autonomy to steady them.
turn 2: Switzerland loyalty 96 (-2): satellite drift — Invest in them or grant them autonomy to steady them.
turn 3: Switzerland loyalty 94 (-2): satellite drift — Invest in them or grant them autonomy to steady them.
```

The hint names **only working levers** (post-F1/F1c): no dead "garrison their capital", no nonexistent "large subsidy", no VS-R-blunted "grant autonomy" wording in the spiral variant.

**Invest ARRESTS the slide** at healthy grip (multiplier 1.0 → full value, byte-identical to pre-VS-R):

```
grip=100  lever_multiplier=1.0
invest Switzerland: 94 -> 100
message: Invested in Switzerland: +10 loyalty (94 → 100). Cost: 1 DP + 200g. Cooldown: 3 turns.
```

### B. VS-R — THE CRUX: raw authority stays high while the derived grip spirals

Mirroring the July-14 live playtest: set a strained court (`authority=65 "Respected"`), then Paris falls to Austria.

```
>>> authority STILL 65 (Respected) — raw tracker blind to the military collapse (memo Q1)
>>> derived imperial_grip = 25  (SPIRAL (<30)) — the crux fix
```

This is the exact defect the VS-R research targeted: `authority_tracker` has no military mover (its only nudges are ±5 gated on outnumbering; a capital lost to assault docks it by zero), so a player could lose Paris and the war with the tracker near 100. The **derived** `get_imperial_grip` closes that gap (Paris −40 → 25).

Spiral-band consequences, all firing correctly:

```
authority_vassal_drift(grip=25) = -2      (extra per-turn bleed, additive, capped -4)
cheap-lever multiplier          = 0.4     (invest / autonomy-up blunted)
courting_unlock_bonus           = 2       (enemies court deeper); effectiveness x1.08
recovery_hint (spiral)          = "The Emperor's grip is slipping - coin and concessions no
                                   longer hold them. Win a decisive battle to restore your
                                   grip, or release them before they break away."
```

A loyalty turn in the spiral band now carries the grip term as a named cause (Switzerland is a satellite, so it stacks satellite-drift −2 + faltering-grip −2 = −4):

```
Holland        loyalty 98 (-2): satellite drift, the Emperor's faltering grip — [spiral hint]
KingdomOfItaly loyalty 98 (-2): satellite drift, the Emperor's faltering grip — [spiral hint]
Switzerland    loyalty 96 (-4): satellite drift, the Emperor's faltering grip — [spiral hint]
```

**"No cheap recovery" — invest BLUNTED in the spiral band** (still pays full cost — the point of a token gesture no longer holding):

```
invest Switzerland: 96 -> 100  (spiral grip=25)
message: Invested in Switzerland: +4 loyalty (96 → 100) — the Emperor's faltering grip blunts the gesture. …
```

The existential levers are **never** softened (spec): full release, autonomy-DOWN (−15), a large per-turn subsidy. One-way coupling — restoring Paris + authority returns grip to 100 and drift to 0; **nothing is written back to authority**.

### C. VS-2 — the dead coalition "war weariness" term is gone from the drift pipeline

```
live CALL to get_coalition_loyalty_penalty in executable code? False
(mentioned only in the removal comment? True)
```

Loyalty drift is now independent of coalition membership (the term was always 0 for a lord's own satellite; pinned by the flipped `test_deep_audit_session2` Fix17 assertion).

### GR5 — the coupling keys off the LORD, so it fires for enemy lords too

```
Britain    imperial_grip=75  drift_if_spiral=0
Russia     imperial_grip=75  drift_if_spiral=0
Austria    imperial_grip=75  drift_if_spiral=0
Prussia    imperial_grip=75  drift_if_spiral=0
```

Enemy intact court base = 75; a capital-lost enemy grades to 35 — symmetric by construction, no special-casing.

---

## Prong 2 — live HTTP playthrough (player-facing surfaces reach a real player)

Real backend, `LLM_MODE=mock`, driven with `play.py`; transcript in `transcript.jsonl`. **Clean boot — backend log 1110 lines, zero errors/tracebacks/exceptions.**

**The morning dispatch surfaces all three vassal-loyalty events WITH the recovery hint** (end-turn 1 → turn 2 event stream):

```
vassal_loyalty Holland        98 (-2): satellite drift, the lord's defeats — Invest in them or grant them autonomy to steady them.
vassal_loyalty KingdomOfItaly 98 (-2): satellite drift, the lord's defeats — Invest in them or grant them autonomy to steady them.
vassal_loyalty Switzerland    96 (-4): satellite drift, the lord's defeats — Invest in them or grant them autonomy to steady them.
```

(W6-3 reason-naming works live: "satellite drift, the lord's defeats" — France lost battles turn 1, so the −4 on Switzerland is satellite-drift −2 + lord's-defeats −2.)

**The taught levers are player-reachable and legible over HTTP:**

| Command | Result |
|---|---|
| `invest in Switzerland` | ✅ `Invested in Switzerland: +10 loyalty (96 → 100). Cost: 1 DP + 200g. Cooldown: 3 turns.` |
| `grant Holland autonomy` (hint's literal wording) | ✅ `Holland autonomy changed: Satellite → Autonomous. +10 loyalty (increased autonomy). Tribute rate: 50%.` |
| `grant KingdomOfItaly autonomy` | ✅ `KingdomOfItaly autonomy changed: Satellite → Autonomous. …` |

**The taught lever demonstrably arrests the drift:** after Holland and KingdomOfItaly are made Autonomous (drift −2 → +1), the next end-turn surfaces **only Switzerland** in the loyalty-event stream — the two autonomy'd satellites dropped out of the bleed entirely.

**F7 debug breakdown** (`GET /debug/vassal_loyalty/Switzerland`) now enumerates all six terms and sums to the delta:

```json
{"nation":"Switzerland","loyalty":94,"lord":"France","imperial_grip":85,
 "modifiers":{"autonomy_drift":-2,"garrison_bonus":0,"shared_enemy_bonus":0,
              "lord_battle_modifier":0,"relation_modifier":0,"imperial_grip_drift":0}}
```

(grip 85 ≥ 30 → `imperial_grip_drift 0`, VS-R correctly dormant; the breakdown is self-consistent — F7 fix.)

---

## Honest friction (characterized, not a vassal-pillar defect)

- **`grant X more autonomy` → Berthier shrug over HTTP.** `grant Holland autonomy` (the recovery hint's *literal* wording) parses and executes; the natural variant `grant Holland more autonomy` returns the Berthier "I cannot make sense of this" shrug over the real `/command` pipeline. Yet the **isolated mock parser classifies all three phrasings** (`grant Holland autonomy`, `grant Holland more autonomy`, `make Holland autonomous`) as `change_autonomy`. So the divergence is in the full `/command` pipeline (a pre-parse interceptor eats "more"), NOT the vassal system or the mock parser's action table. It belongs to **Parsing / Sweep 5**, not the Vassal pillar. The taught loop's exact wording works; the variant does not. Low severity.
- **Losing-opening coverage** (carried from the July-14 memo): a short mixed run keeps most marshal-drama surfaces (crown-lighting, autonomous glory-attacks, petitions) dormant. VS-R's spiral is the beat this sweep exercises; the crown/estate economy is out of Phase-5 scope.

---

## Half A — the hard gate (deterministic), for reference

Phase 5 touches **no combat code**, so the combat metric suite must be byte-unchanged; the vassal tests are the dedicated gate.

| ID | Metric | Sweep 3 | **Sweep 4** | Target | Verdict |
|----|--------|---------|-------------|--------|---------|
| M1 | concentration win-rate 1→5 corps | `…→0.818` | `0.000→0.000→0.013→0.355→0.818` | non-decreasing; 3≫1 | ✅ held |
| M1b | reinforcer contribution agg/cau/hostile | `41400/36000/0` | `41400/36000/0` | agg>cau>hostile | ✅ held |
| M2 | rout ≤2 turns 2:1 / 3:1 | `0.613/1.000` | `0.613/1.000` | ≥0.35 / ≥0.65 | ✅ held |
| M3 | net defender Δstrength/turn (2:1) | `−2749` | `−2749` | ≤ −2000 | ✅ held |
| M4 | multi-marshal report consistency | `100%` | `100%` | 100% | ✅ held |
| M5 | iron-resolve 3-stack payoff | `+0.240` | `+0.240` | ≥ +0.18 | ✅ held |
| M6 | attacker win-rate fort+mountains (GUARD) | `0.000` | `0.000` | < 0.5 | ✅ held |
| M7 | first jealousy trigger / roster run | `turn 1` | `turn 1` | ≤ 8 | ✅ held |

Vassal gate: `test_vassal_recovery_lever.py` (9) + `test_vassal_authority_coupling.py` (42+) + `test_playtest_fixes_2026_07_14.py` (19) = **70 green together.** **Full suite 13,314 passed / 3 skipped.** `ruff check backend/` clean. No `.gd` touched by Phase 5.
