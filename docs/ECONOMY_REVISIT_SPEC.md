# Economy Revisit Phase (1805-Scale Economy & Campaign Feel)

> **Status:** DRAFT v0.1 — July 2, 2026. **Needs user scope blessing; EC-2 (gold sinks) and EC-6 (victory conditions) carry explicit design gates.** EC-0 is a defect fix.
> **Origin:** July 2, 2026 re-staging. Consolidates the scattered economy rows into ONE owner (each source row now points here): **DEF-3 Economy Pass** (`MAP_IMPLEMENTATION_PLAN.md:293` + the nation_config.py:414/:445 balance-ownership notes), **B4 Gold Sink Options** (`DESIGN_REFINEMENT.md:287-307`), **R161 One-Time Trade / Economic Diplomacy queue item 7** (`DESIGN_REFINEMENT.md:249, :57-58`), **R26 Continental System Buff** (`DESIGN_REFINEMENT.md:242`), **Enemy AP Rebalancing** (`DESIGN_REFINEMENT.md:311-315` — its "after full map" trigger fired July 2), **DW-3 economic-diplomacy note** (`SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md:155`), the **DG-3 supply/overextension re-evaluation** (trigger fired — `SCALE_READINESS_PLAN.md:152-171`), the **DG-5 victory-condition contradiction**, and the previously-unowned scale imbalances (garrison cap, manpower regen density).
> **Vision constraint:** "Territory as Command Dilemma" — territory problems have faces, not numbers. Depth here means meaningful *choices* (what to build, whom to pay, what a truce is worth), never spreadsheet management.

---

## 1. Ground truth (audited July 2, 2026 — code wins over older docs)

**The money loop is complete but thin, and sinks did not scale with the map.** Income: typed region income (300/200/150/100/50 by region_type, modified by stability/war damage/buildings) + trade + tribute + treaty clauses + settlement streams + British subsidy. Sinks: upkeep 5g/1000 troops, recruit 150–600g, five buildings 250–400g (slot-capped), watchtower 250g, repair 150g, vassal invest 200g.

- **Scale data point:** France ~3.4k gold/turn on 28 provinces (Slice 8 smoke) vs ~950g upkeep at ~190k fielded — the documented "~700g vs ~250g" gap is ~5× understated. The ENTIRE building stock (~1.85k) costs half a turn of French income; 200–500g one-shot sinks designed against the legacy economy are decorative now.
- **CONFIRMED DEFECT (fix first — EC-0):** `world_state.py:5925-5928` resets `nation_actions` from the LEGACY builder every `advance_turn` regardless of `sovereign_map` — Austria's approved 4 AP (1805 pre-slice item 8) is squashed back to 3 after turn 1, and `ap_per_turn` treaty penalties compound forever for Europe-only nations. **Every AI-pressure measurement since the cutover ran Austria at the un-tuned value** — Slice-8 balance verdicts touching Austrian tempo need re-baselining after the fix. (Also spawned as a background task chip.)
- Manpower: `EUROPE_MANPOWER_POOLS` covers all 20 nations, but per-region regen bonuses (cavalry +500/plains, artillery +200/urban) were tuned for 19 regions and now scale with province count; infantry regen is a flat 2500/turn for every nation regardless of size.
- `GARRISON_MAX_PER_NATION = 3` (including the capital) — effectively 2 player detachment slots on a 126-province map; a 19-region-era constant.
- Continental System: mechanically real but minimal — player-lord hardcoded, ~200g/turn total cap, no player join/leave command (R26).
- DEF-3 has a working hook already: scenario `region_overrides` can author per-province `income_value` today; alternatively `create_europe_regions` is a one-line change to consume an optional registry income field (preferred — income is map data, not scenario data).
- The war-economy transfer layer (indemnities, recurring settlement gold, treaty clauses, subsidy, tribute, plunder) is complete — this phase's job is **sinks and per-province depth, not new transfer channels**.

## 2. Slice plan

| Slice | Scope | Gate |
|-------|-------|------|
| **EC-0 (defect)** — ✅ **LANDED July 4, 2026** | The `advance_turn` AP reset is now world-scoped: the constructor snapshots the world's own base AP into `base_nation_actions` (serialized; from_dict defaults to the loaded `nation_actions` for fresh scenarios + pre-fix saves — mod-safe for custom-AP scenarios the legacy builder could never rebuild), and the reset restores from that snapshot instead of `build_default_nation_actions`. Europe Austria holds 4 across turns (was squashed to 3); every Europe-only nation's `ap_per_turn` penalty applies-then-releases each turn (was compounding forever); legacy Austria stays 3. No Slice-8 balance PIN moved in the suite; the prose verdicts touching Austrian tempo were measured at 3 AP and now run at the intended 4 (note for the balance pass). `tests/test_economy_ec0_ap_reset.py`. | None |
| **EC-1 (DEF-3)** | Authored per-province income where history diverges from region_type defaults (registry field preferred over scenario overrides); the DEF-3 row's promised registry sane-bounds test; starting-treasury/pool balance pass over `EUROPE_NATION_GOLD`/`EUROPE_MANPOWER_POOLS` (the nation_config ownership notes point here). | None |
| **EC-2** | Gold sinks at 1805 scale — **design gate**: Province Development as the anchor candidate (re-costed for a 3.4k/turn economy: recurring or scaling costs; per-region state on `Region` + `get_nation_regions` per Golden Rule 8 — copy the SC-33 recurring-payments and Slice-8 cached-index house patterns); building cost/effect scaling; the other B4 candidates (gifts, mercenary garrisons, bounties) evaluated after. Forced march stays REJECTED. | **USER DESIGN GATE** |
| **EC-3** | Scale retunes: manpower regen density (per-region bonuses at 126-province density; flat infantry regen vs nation size), `GARRISON_MAX_PER_NATION`, upkeep rate sanity vs 1805 army sizes. | None |
| **EC-4** | Enemy AP rebalance (the DESIGN_REFINEMENT row, trigger fired; meaningful only after EC-0). | None |
| **EC-5** | Continental System decision: upgrade to a real embargo economy (per-member trade severance, smuggling risk, Britain naval-income interplay, player join/leave command — R26) **or** close the row with the promise trimmed. Do not leave it half-owned. | User decision |
| **EC-6** | Victory/pacing reconciliation — **the DG-5 three-way contradiction**: SCALE_READINESS decided "no mandatory hard victory," but live code runs `VICTORY_REGION_FRACTION=0.75` + a 60-turn time-expired end, and CLAUDE.md glosses DG-5 as "raw-count hegemony victory." Options: (i) honor DG-5 as written, (ii) build the hegemony victory, (iii) re-decide DG-5 to bless the shipped behavior. Victory pacing determines whether long-horizon sinks (EC-2) can ever pay back — so it belongs in this phase. | **USER DECISION** |
| **EC-7** | Campaign-feel evaluation (DG-3): the "after first Europe playtest" supply/overextension trigger has fired — run the evaluation (likely Option A distance-from-capital penalty) and either open a Supply pass with an owner row or re-defer with a new dated trigger. | User decision |
| **EC-8 (optional)** | Economic diplomacy: R161 one-time trade (gold/manpower/territory exchange without state change) + diplomacy-facing sink candidates. May defer to the 8.EVAL/diplomacy track if this phase runs long — but the row's owner is HERE until explicitly re-homed. | Scope blessing |

## 3. Presentation invariant

Any new stream or sink MUST appear in the strategic ledger economy tab (`ledger.py:_build_economy`) in the same slice that lands it — the SC-33 "invisible tribute" bug class is the cautionary precedent.

## 4. Non-goals

- No new transfer channels (the war-economy layer is complete).
- No per-province micromanagement UI — depth lands as decisions and events, not spreadsheets (vision constraint).
- Naval/blockade economics belong to DEF-5's future naval spec, not here.
