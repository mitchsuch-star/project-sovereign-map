# Vassal Playtest Memo — July 14, 2026

**Build:** europe_1805, anthropic LLM mode, DEBUG on · **Scope:** ~3 live turns + an engineered VS-R spiral · **Method:** live drive against the running backend (`:8005`), then a 14-agent adversarial code-verification (verify each finding, score pillars, completeness hunt, synthesize). Bug fixes landed the same session — see §5.

## 1. Verdict

The **vassal improvements landed and are correctly engineered.** VS-R's grip-spiral is a genuinely clever, correctly-firing beat: live, Napoleon's *authority* read a healthy **60–65 ("Respected"/"Normal")** while the derived `get_imperial_grip` crumbled to **~20** the moment Paris fell — exactly the crux the research memo targeted (raw authority does not spiral on military collapse; the derived grip does). The recent slices (Combat Overhaul, Economy, MC pass) are mechanically clean and GR5-symmetric.

The one real dent was in **VS-1's reason to exist** — its discoverable "teach it" recovery loop recommended a **dead lever** ("garrison their capital"), the typed form of another taught lever failed to parse, and the spiral hint named a VS-R-blunted lever plus a nonexistent "subsidy". None game-breaking (EC-6 sandbox: losing Paris didn't end the game), but the teaching surface pointed at partly-broken remedies. **All fixed this session.**

## 2. What works (confirmed live + in code)

- **VS-R crux fix** — grip spiraled to ~20 at authority 65 (65 − 40 capital-lost). Zero new serialized fields; boot-dormant/byte-identical at grip 100.
- **"No cheap recovery" blunting** — invest gave **+4** in the spiral (*"the Emperor's faltering grip blunts the gesture"*) vs a **+10** control; subsidy/release/autonomy-down never softened. One-way coupling (never writes authority back).
- **VS-1 event gate (≥2)** surfaced the −2 satellite bleed for all three satellites with W6-3 reason-naming (*"the lord's defeats, satellite drift"*).
- **Economy legibility** — boot ledger reconciles to the gold (base 1512 + over-limit 236 + Grande Armée 882 = 2630 upkeep; net +2107). **EC-U1 reversal proven:** Masséna's 8,819 losses cut upkeep 2630→2008.
- **Narration (W6)** — dynamic headline *"Flanders has fallen. Enemy colours fly over French homeland soil"* + Berthier *"France herself is under the enemy's boot."*
- **MC texture** — glory ladder, MC-2 skill/rally tiers (Davout "fast"), MC-2b admin tiers, MC-3 web (Davout–Bernadotte −2 Hostile); emergent muster line *"WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions."*
- **GR5 enemy AI** ran the identical resolver (Archduke John got cautious +10% + terrain +25% correctly; surcharges/decisiveness symmetric).

## 3. Pillar scorecard

| Pillar | Score | One-line |
|---|---|---|
| Vassal (VS-1 + VS-R) | **6** | Clever, correctly-firing VS-R crux; VS-1's "teach it" loop recommended a dead lever (now fixed). |
| Command Robustness | **7** | Playtest-hardened core, marred by a dead typed-autonomy lever + two minor leaks (all fixed). |
| Combat (+ legibility) | **6** | Strong symmetric mechanics; the odds preview overstates attacker prospects at the decision point. |
| Economy | **7** | Excellently legible & clean; the drama-bearing half (Cost-of-Success) stayed dormant this run. |
| Narration + Marshal-Drama | **7** | Genuinely telling its stories; jealousy/crown payoff stayed dormant in a losing 3-turn opening. |

**Overall ≈ 6.6.** Sound engineering; the beats that fired are strong. Held down by (a) VS-1 teaching broken levers (fixed) and (b) a short losing run leaving the marquee drama surfaces dormant — a **coverage gap, not a defect** (`_out_bled` correctly denied Masséna stalemate glory; the Cost-of-Success economy never triggered because no glory was earned). A winning/mixed run is needed to exercise crown-lighting, autonomous glory-attacks, petitions, and the estate/rente economy at strength.

## 4. Findings (adversarially verified)

Verdicts after the 14-agent pass corrected two of my live-read claims (honesty note): **F2 refuted as a bug** (terrain IS folded into the odds band; only a legibility residual remains) and **F8 split** (the "−50 shown as −1" delta is WAD; the desync is the real bug). The dispositions:

| ID | Verdict | Sev | One-line |
|----|---------|-----|----------|
| F1 | CONFIRMED | P2 | Spiral hint recommended a VS-R-blunted lever + a nonexistent "subsidy". |
| F1c | CONFIRMED | P2 | "garrison their capital" reads `garrison_troops` (never assigned) → a dead lever. |
| F3 | CONFIRMED | P2 | Danger/threat readings counted a co-located ALLY (Bavaria's Deroy) as an enemy force. |
| F6 | CONFIRMED | P2 | Typed autonomy changes dead-ended (executor read the wrong command key; mock too narrow). |
| F8b | CONFIRMED | P2 | A blocked rebellion orphaned the vassal at a stale `VASSAL` diplomatic state (live: KoI kept Milan+Piedmont). |
| C1 | CONFIRMED | P2 | Talleyrand's `<35` advisory wasn't grip-aware — contradicted the same dispatch's event line. |
| C2 | CONFIRMED | P3 | Autonomy-up blunt printed a bare "+4" with no cause. |
| F5 | CONFIRMED | P3 | Berthier recovery prompt fed the LLM raw action ids → echoed "Invest_vassal". |
| F7 | CONFIRMED | P3 | `/debug/vassal_loyalty` showed 4 of ~7 terms — never summed to the real delta. |
| F4 | OBSERVED | P3 | A messy MOVE target leaked raw ("No path from Milan to On Archduke John At Tyrol"). |
| F2 | REFUTED(bug)→design | — | "favorable" is a force-balance heuristic (omits defender baseline/stance/dice), not a bug. |
| F8a | WAD | — | "−50 shown as −1" — `delta_str` mirrors the bounded delta; the swing was multi-turn courting. |

## 5. Fixes landed (this session)

Backend-only (no `.gd` touched). Single-source, conservative. Tests: `tests/test_playtest_fixes_2026_07_14.py` (19) + 2 updated pins. Suite **13,238 passed / 3 skipped**, ruff clean.

- **F1/F1c/C1** — new single-source `vassal.recovery_hint_for_grip(grip)`; drops the blunted "grant autonomy", the nonexistent "subsidy", and the dead "garrison their capital"; spiral copy names only unblunted arrests (win a decisive battle → restores grip; release). Talleyrand's advisory now routes through the same helper.
- **F1c** (garrison) — the unwired formula block + its 4 tests were KEPT (intended-but-unwired), only removed from the hint copy. Wire-or-remove → `DESIGN_REFINEMENT.md` VP-D1.
- **F3** — new `dispatch._intel_marshal_is_enemy` (is_at_war) guards all 3 threat-framing sites; the truthful sightings list (`_build_intelligence`) intentionally still shows allies.
- **F6** — executor reads `raw_command` + more/grant/less directions; mock matches "autonomy" or make/set/turn + a level word. Restores the F1 diplomacy-wizard autonomy buttons too.
- **F8b** — a blocked war allocation now resolves as graceful independence (set the pair to PEACE, sidestepping the war-instance side-conflict) instead of orphaning at VASSAL.
- **C2** — autonomy-up appends the same grip-blunt note as invest when the gain is reduced.
- **F5** — Berthier recovery prompt maps verbs through `action_display_name` and drops meta/debug ids.
- **F7** — debug breakdown gains `lord_battle_modifier` + `imperial_grip_drift` + `imperial_grip`.
- **F4** — `strategic_executor._resolve_region_from_phrase` (region substring → marshal location) + a clean-fail message; never leaks the raw phrase.
- **F2** (polish) — the muster label reads "the balance of force looks {band}"; the deeper defender-baseline fold → `DESIGN_REFINEMENT.md` VP-D2.

**Routed to `DESIGN_REFINEMENT.md`:** VP-D1 (garrison wire-or-remove), VP-D2 (odds-band defender baseline), VP-D3 (defensive-reinforcer valuation — verify intent), VP-D4 (grip memoization nit).

## 6. Coverage note

Run a **winning/mixed playthrough** (or seed one marshal ahead on the glory ladder) to exercise the dormant marshal-drama surfaces — crown-lighting, autonomous glory-attacks, grievance petitions, and the Cost-of-Success estate/rente/expectation economy — before those pillars are signed off at strength. This run's losing opening is why they stayed dormant (correct behavior), not a defect.
