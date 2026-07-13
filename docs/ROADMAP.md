# Ink & Iron: Master Roadmap

> **THE source of truth for all phases and timeline.**
> **Other docs reference this — phase numbers only exist here.**
> **Last Updated:** July 3, 2026 — **Gate 4 PASSED in full + Slice H LANDED** (gate approved and implemented the same day). Queue re-staged July 2 (post-map / post-diplo). The real-map cutover is COMPLETE (the running game is the 126-province 1805 campaign) and **the Phase 8 Peace Deals arc is FULLY complete** (Slice G1 at `1a9da53`; Slice H July 3 — no live settlement successors). The forward queue is re-staged below as **§Current Phase Queue** — new phases CR (Command Robustness), EC (Economy Revisit), and MC (Marshal Content Pass) join the surviving 8.EVAL → 8.5 → Steam → 9/10/11 → Pre-EA → EA spine. See `docs/STATUS.md` for live state.

---

## Current Phase Queue (re-staged July 2, 2026)

Ordering below is the recommended sequence; A-items are small and interleave freely. User priorities anchored this staging: (1) command-by-text robustness, (2) economy revisit, (3) docs that cover the bases for a great game. **Re-sequenced July 9, 2026:** the **Comprehensive Codebase Audit (AUD) correctness sweep now runs before the EC *build***, feeding a Fable-led **econ eval** (`ECONOMY_REVISIT_SPEC.md §0.7`) of the economy recs before any of that code is written; the audit's **§8 creative/fun-factor capstone is split off to run *after* EC** so it judges the improved economy — CR (done) → **~~AUD sweep~~ ✅ → ~~econ eval~~ ✅ → ~~EC-2 gate~~ ✅ BLESSED → ~~EC build~~ ✅ COMPLETE (all July 9; EC pass 1 CLOSED at `fd97b6f`) → ~~§8 fun-factor capstone~~ ✅ COMPLETE July 10 (`docs/audits/CREATIVE_AUDIT_2026_07_10.md`) → ~~W6 Fun-Factor Build~~ ✅ COMPLETE July 10 (all 12 slices landed same day as approval, two sessions; the §0 re-score MEASURED all four target pillars MET — memo §9) → ~~MC gate + build~~ ✅ July 10–11 → ~~JV (Jealousy v3.2 + Marshalate)~~ ✅ July 11 → ~~UI U1–U5~~ ✅ + ~~DEF-1 voices~~ ✅ + ~~Artillery arm~~ ✅ July 12–13 → **▶ Combat Overhaul & Score-Raising Program — NEXT** (`COMBAT_OVERHAUL_SPEC.md`, born from the July 13 ⚔️ Field Review; Phase 0 = baseline sweep + the deterministic metric harness, no balance change).

| # | Phase | Contents | Gate | Spec |
|---|-------|----------|------|------|
| **A** | **Loose-Ends Closeout** | ~~Gate 4 visual-half confirmation~~ (✅ **PASSED July 3, 2026**); ~~G2 closure bookkeeping~~ (DONE July 2); ~~Slice H design gate → H-1/H-2~~ (✅ **APPROVED + LANDED July 3, 2026** — the settlement arc has no live successors); R19 modding validator (~3h); Jealousy stays gated (sequenced after MC per its prerequisite note). | Jealousy needs its user gate | `SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md` (LANDED) |
| **CR** | **Command Robustness** ("Talk to Your Marshals") — **ACTIVE (scope blessed July 3, 2026)** | Promotes the Post-Diplomacy Command Layer Queue (below) to a numbered phase. ~~CR-0~~ + ~~CR-1~~ **✅ LANDED July 3, 2026** (the P0 parser roster gap is FIXED — rosters live-world derived; the eval harness — golden corpus over both worlds + action-coverage gate, 246 entries post-CR-2 — is the phase's standing regression gate; typed `status` wire connected); ~~CR-2~~ **✅ LANDED July 4, 2026** (marshal-aware confidence + LLM retry on fuzzy errors; the unified `command_clarification` question — "Which marshal, Sire?" — riding the existing popup with deterministic typed answers; silent-marshal-drop + self-support + condition-hijack + sequential-"then" fixes; parse failures with candidates surface as clarifications instead of the Berthier shrug); ~~CR-3~~ **✅ LANDED July 4, 2026** (live-LLM modernization — `claude-haiku-4-5` pin + forced tool-use structured output + Golden-Rule-6 seam hardening); ~~CR-4~~ **✅ LANDED July 4, 2026** (deterministic context carryover — reference resolution + Persistent Command Focus); **CR-5 (Personality-Biased Disambiguation) ✅ SCOPE BLESSED July 5, 2026** (spec §6 — prompt-copy delegation-verb table; player-visible = three-way aggressive→attack/cautious→scout/literal→ask (Soult reassigned cautious→literal at the gate so the literal arm is player-reachable); guardrails = objection-first one-modal legibility + temp-0 + a blocking personality-type pre-flight; rider (d) "words become the record" IN, **Flavor Echoing promoted to owned slice CR-5b**); **CR-5 ✅ COMPLETE — all 4 phases LANDED July 6-7, 2026** (safe half `a438614` → Phase 3 lethal gate `de6d740` → Phase 4 aggressive arm: delegation-inferred PURSUE, two first-step seams closed, guardrail-e MODE gate, rider (d) live, two adversarial audit rounds / 5 findings fixed; 86 CR-5 tests). **Next: CR-5b (Flavor Echoing)** — non-parroting mock design is its entry gate. CR-6 (conversational objection negotiation) + CR-7 backlog remain. | CR-6 needs its own design gate | `COMMAND_ROBUSTNESS_SPEC.md` v0.6 + `CR5_IMPLEMENTATION_BRIEF.md` |
| **AUD** | **Comprehensive Codebase Audit** (component-by-component, fix-as-you-find) — **✅ CORRECTNESS SWEEP + ECON EVAL BOTH COMPLETE July 9, 2026** (eval memo `docs/audits/ECONOMY_ECON_EVAL_2026_07_09.md` — 23 verdicts feeding the EC-2 gate; headline dissents: E5 full-income redirect + ES-3 promoted to pass 1; ES-2 simplified to stability-tier occupation cost) | The full §5–§7 sweep ran July 9 in six committed chunks: **7 fixes, 0 open escalations** (turn-1 DP shortfall, misattributed personality copy, wrong-side Berthier coordination, unpaired hold-clear, misattributed vassal dispatch, RNG-flaky test seeded, scorer-seam import hygiene); the three never-audited subsystems (`diplomatic_defiance` / `war_contribution` / `settlement_reactions`) verified sound; live-backend seam + topology verification clean; doc counts reconciled. Log: `docs/audits/AUDIT_2026_07_09.md`. **~~The §8 creative / fun-factor capstone~~ ✅ COMPLETE July 10, 2026** (post-EC as staged — memo `docs/audits/CREATIVE_AUDIT_2026_07_10.md`; 10 defects routed to `BUG_FIXES.md` §Creative-Audit Findings; Wave 6 filed in `DESIGN_REFINEMENT.md` and **approved in full July 10 → the W6 row below**). | none — the whole audit arc is closed | `AUDIT_GUIDELINE.md` (+ `ECONOMY_REVISIT_SPEC.md §0.7`) |
| **EC** | **Economy Revisit** (1805-scale economy + campaign feel) — **✅ PASS-1 BUILD COMPLETE July 9, 2026** (Track 1 S1–S4 + Track 2 S5 ES-3 / S6 ES-2 / S7 ES-7 ALL LANDED at `fd97b6f`; stacked E1 band test green; read the history below through the `§0.6.7` gate record; standing user tuning flags both CLOSED: the E1 turn-1 anchor was RESOLVED July 10, 2026 — measured anchors accepted, no retune, spec S7 note — and E-CA-3 war-priced recruitment landed as W6-11) | ~~EC-0 fixes the **AP-reset defect**~~ **✅ LANDED July 4, 2026** (world-scoped `base_nation_actions` snapshot — Austria holds 4 AP, Europe-only treaty AP penalties apply-then-release instead of compounding); **PRE-EC ledger floor ✅ landed July 7** (economy tab now reconciles to Net); **EC-6 victory DECIDED July 7 = sandbox** (remove hard win/lose; real win-conditions → the new Pre-Ship Victory & Objectives Pass); **EC-2 audit + gate decisions RECORDED July 8; the gate-ready pass-1 spec (ES-7 "Cost of Success" mechanic + ordered plan + item reconciliation + escalations) is `ECONOMY_REVISIT_SPEC.md` §0.6.** Pass-1 = **ES-2 Occupation Upkeep + ES-7 (REFRAMED — success makes a marshal more expensive; *paying stops the bleed, never buys trust*; player-facing surface = endow the marshal with an ESTATE + a province-derived TITLE, e.g. "Endow Ney with the Duchy of Swabia" — internal action id stays `grant_dotation`; ES-8 title *flavor* rides pass 1 free, ES-8 stat-bonus mechanic stays deferred) + ES-1 manpower-fix prereq**; ES-4 → pass 2; ES-10 CUT; band ~55–70% of the whole net incl. the diplomatic economy. **The build is UNBLOCKED (audit ✅ + econ eval ✅ + gate ✅, all July 9):** §0.6.3 as amended by §0.6.7 — Track 1 (S1 ES-1a art re-key+drop / S2 ES-1b cavalry+stables / S3 ledger-GR8 fix / S4 EC-6a sandbox toggle) → Track 2 = S5 ES-3 → S6 ES-2 (stability-tier shape) → S7 ES-7 (full-income redirect), ONE stacked band test as acceptance. Also EC-3 super-linear upkeep; EC-4 enemy AP; Continental System (EC-5); DG-3 supply/overextension (EC-7). | ~~Econ eval (§0.7)~~ ✅ July 9 → ~~EC-2 design gate~~ **✅ BLESSED July 9, 2026** (econ-eval memo §8 accepted in full; blessed numbers + 4 structural amendments recorded in **§0.6.7** — ES-7 full-income redirect, ES-2 stability-tier occupation shape, ES-3 promoted to pass 1, endow triangle) → **▶ BUILD NEXT (§0.6.3 as amended)**; EC-5/EC-7/soft-goal RESOLVED July 8 (cont.) — §0.6.6 | `ECONOMY_REVISIT_SPEC.md` |
| **W6** | **Wave 6 Fun-Factor Build — ✅ COMPLETE July 10, 2026** (all 12 slices landed the same day the user approved, across two build sessions; spec §15 DoD recorded) | All 12 slices landed in order: W6-0/1 BUG-CA correctness (dialogue identity P1, typed-answer routing, retreat doctrine, report/stat fixes) → W6-2 Dynamic Battle Naming → W6-3 the Dispatch Rewrite → W6-4 muster preview + standing orders → W6-5 the Literal Doctrine → W6-6 enemy marshals speak → W6-7 Marshal Fates → W6-8 estate confiscation (confiscate/respect + `respected_estates` acceptance term) → W6-9 the assessment verb (war room + executable counsel; R117 landed) → W6-10 incoming voice/variety/territorial honesty (diplomat_line register bank, 6-turn type cooldowns, P3 relation-band asks, settlement status-quo line) → W6-11 balance duo (symmetric casualty-scaled morale in both combat copies; war-priced recruitment ×3 + over-limit compose, GR5-priced AI). **Scores re-measured live per §0 (memo §9): narration 3.5→7.5 ✓, combat legibility 4.5→7 ✓, incoming diplomacy 4→7 ✓, marshal drama 6→7.5 ✓ — all four targets MET.** | ~~APPROVED July 10, 2026~~ COMPLETE (blessed numbers remain in-band tunable; structural changes escalate) | **`WAVE6_FUN_FACTOR_SPEC.md`** (§15 DoD) |
| **MC** | **Marshal Content Pass — ✅ CLOSED July 11, 2026 at the MC exit review** (gate ✅ BLESSED July 10, 2026; ~~MC-0~~ ~~Q3 "The Rally"~~ ~~MC-1a~~ ~~MC-1b~~ ~~MC-1c~~ ~~MC-2~~ ~~MC-3~~ ~~MC-4~~ ~~MC-V~~ landed July 10; **~~the exit review~~ HELD July 11 — record spec §11**: MC-2b landed as "The Intendance" (admin wired at the recruit-cost seam, Europe-scoped, memo-§3 values live, card row restored); MC-V-2 decided — enemy literals play LITERAL (alias narrowed to autonomous player marshals); MC-V-1/3/4/5 disposed; First Horseman watch closed; Soult-literal re-check passed live; bonus P1 fix — the W6 `headline` shadow that had killed the Godot client) | Previously UNOWNED gap: all 21 shipped marshals boot with ability "None", flat skills, zero relationships. **Gate record = spec §4; MC-1a+MC-1b landing record = spec §5, MC-1c = spec §6 (all July 10, 2026): ALL TEN blessed abilities are LIVE** — Ney, Davout (Iron Resolve: T2 serialized coil-uncoil-spring — fortified turns coil +1 stack cap 3, his next attack consumes all for +8% each max +24%; a 34-agent pre-commit 4-lens review confirmed 7 findings all fixed, headline: the accrual tick re-coiled routed/captured carriers via the stale pre-existing `fortified` flag — now guarded to standing marshals), Charles (+3% AND rout-threshold 15 at all three rout copies), Soult, Lannes, Murat, Massena, Bernadotte, Kutuzov, Moore; MC-1b's 22-agent review confirmed 15 findings, all fixed (headline: the [S62] third rout copy; coordinated pursuit accounting; the Eyes-on-a-Crown trust-dock exemption — ✅ ratified by the user July 10, 2026). **~~MC-2~~ ✅ LANDED July 10, 2026 (landing record = spec §7):** the blessed 21-row skills/trust table authored into `europe_1805.json` (admin flat 5 reserved for MC-2b; French trust mean exactly 70.0), The Rally texture activated (Davout 9/Charles 8 fast tier; Mack/Massena/Buxhowden/Hohenlohe 3 poor), the memo-§6.4 re-measures pinned (Ney +6.9% relative at shock 9; Lannes/Bernadotte arrival 90/60), and the marshal card upgraded to a `█░` bar character sheet with backend-derived skill hints + Rally notes (shown=applied; `test_marshal_content_mc2_skills_trust.py`, 113). **~~MC-3~~ ✅ LANDED July 10, 2026 (landing record = spec §8):** the blessed 13-pair relationship web authored as 26 symmetric directed edges — zero new mechanics, five pre-existing consuming seams pinned (coordination ×0.0/×0.5/×1.25, A-D4 hostile refusal = the Davout–Bernadotte Auerstedt no-show live, arrival ±10/step, muster preview, card rows; Charles–Mack −2 makes Mack's isolation emerge from the graph, GR5); the Jealousy v3.1 prerequisite is MET (`test_marshal_content_mc3_relationships.py`, 47). **~~MC-4~~ ✅ LANDED July 10, 2026 (landing record = spec §9):** balanced/loyal deferral closed as a GR9 contract (retired reserved values + a three-arm boot guard: validator hard-error = scenarios cannot boot them, `create_marshal_from_data` raises, omitted-key default logs; re-open owners = Jealousy gate / MC exit review; never name a revived type "loyal"); Soult-literal CANONIZED as character (the §6.8 exception language retired in both specs — the personality=character rule holds with zero exceptions; `test_marshal_content_mc4_personality_guard.py`, 23). **~~MC-V~~ ✅ LANDED July 10 (spec §10) and ~~the MC EXIT REVIEW~~ ✅ HELD July 11, 2026 (spec §11): MC-2b "The Intendance" landed (`test_marshal_content_mc2b_administration.py`, 49), MC-V-2 decided (enemy literals play literal — `enemy_ai.get_effective_ai_personality` single source), MC-V rows all disposed, the First Horseman watch CLOSED (3 checks, no over-harvest), the Soult-literal re-check PASSED live. THE PASS IS CLOSED.** Prerequisite for the Jealousy gate — MET. | ~~USER DESIGN GATE~~ BLESSED July 10; exit review held July 11 | `MARSHAL_CONTENT_PASS_SPEC.md` |
| **JV** | **Jealousy v3.2 + estate riders + Marshal Recruitment — ✅ LANDED July 11, 2026** (the gate blessed AND built in one session under the user's full-auth grant; backend `467c167` + the Godot/docs commit) | The glory ladder + relationship-scaled grievances on the MC-3 web, the three personality expressions (aggressive autonomous glory-attacks, cautious withholding via the derived −1, the literal Vindicated Garrison fog-lift), battle-time resolution + surges, Crowned with Glory (+1 shock/defense/administration), escalation to the mutual spiral, enemy jealousy on the EC-M proxy (**literal-AI follow-on decided: enemy literals participate fully**), the ONE marshal-petition channel (§6 confrontations, §6b rivalry + Separate Them, **ESP-1 Fontainebleau**, **ESP-2 war-weary**; **ESP-4 rente default** folded), and **Marshal Recruitment — "The Marshalate"** (authored 17-candidate bench, shared executor, AI P1.75 commission rung, Generals-screen Commission view + LAURELS ladder header). Record = `JEALOUSY_SPEC.md` §0 + `MARSHAL_RECRUITMENT_SPEC.md`; tests 107+22+34; suite 12,958/3. | ~~USER GATE~~ granted July 11 ("full auth") | `JEALOUSY_SPEC.md` §0 |
| **UI** | **UI Visual Foundation Sweep — ✅ U1–U5 LANDED July 12–13, 2026** (visual sign-offs pending) | The presentation layer: a custom font stack (Cinzel / EB Garamond / Source Sans 3) + ONE central `main_theme.tres` registered via `gui/theme/custom` + typed Button styleboxes — fixes the three structural gaps (no shipped font / 299 hardcoded `StyleBoxFlat`+`theme_override_*` across 51 files / buttons that only override `font_color`). Then UI-2 color-centralization + UI-scale (**absorbs DEF-13**, map SubViewport kept native) and UI-3 texture/border/icon/portrait polish. **All third-party assets already gathered + license-verified** (13 OFL fonts, CC0 textures/borders, curated Phosphor MIT + Game-icons CC-BY icon sets, 37 Wikimedia PD marshal portraits, CC0 audio/flags/ornaments/decor); tracked credits at repo-root `THIRD_PARTY_LICENSES.md`. Display-only, Golden-Rule-6 clean. **War-Table Pieces style gate CLOSED July 12, 2026 — tin flats on a round base (spec §7, references gathered); the whole sweep is now segmented into build sessions U1–U5 in spec §8.** | none — proposal + assets DONE; land session **U1** (UI-0+UI-1, low risk), then review | `UI_VISUAL_FOUNDATION_SPEC.md` |
| **B** | **DEF-1 Roster Voices + presentation polish** — **✅ voices + loyalist register LANDED July 13, 2026** | ~~Bespoke registers for the 15 chancery-fallback diplomats (incl. the new `loyalist` register class)~~ ✅ **DONE** (loyalist register class + 15 bespoke incoming-proposal voices, adversarially verified; `test_w6_incoming_voice.py`); ~~Voice Bible reconciliation (WB-D five lines, reactive_summon)~~ ✅ **DONE** (reactive_summon GR9-closed; WB-D = the live `commitments_notice_*` family). Remaining **homed** as owned follow-on "Roster Voices — Depth": per-court bespoke `commitments_notice_*` copy + `TALLEYRAND_COMMENTARY` coverage for the 15 (working fallbacks today — landing trigger + completion test in `DIPLOMAT_VOICE_BIBLE.md` §DEF-1 landing note); optional DEF-12 map-modes mini-gate. **(DEF-13 UI-Scale folded into the UI row above.)** | DEF-12 needs gate | DEF rows in `MAP_IMPLEMENTATION_PLAN.md` |
| **CO** | **Combat Overhaul & Score-Raising Program — ▶ NEXT** (scope blessed July 13, 2026) | Born from the ⚔️ Field Review (7-turn live 1805 playthrough + a 25-agent adversarial code audit; overall 6.4/10). Converts the problematic scores (Combat 5.0 / Economy 5.0 / Marshal Drama 6.0 / Vassals 6.0) into a **sweepable, phased build** measured by a deterministic combat-metric suite (M1–M7, the hard gate) + the 12-component LLM review (directional). **Phase 0** harness + baselines (no balance change) → **Phase 1** additive **personality- & relationship-scaled** reinforcement (CO-1/CO-1b — an aggressive reinforcer pushes harder, a resentful one ≈0; metric M1b) + odds-on-committed-force + the single-source survivor-count bug (CO-5) → **Phase 2** decisiveness→rout→capture (CO-3) + the enemy per-corps **regen cap** so attrition is winnable (CO-4) + reinforcement legibility (CO-6) + the Iron-Resolve stance-trap fix (CO-7) → **Phase 3** un-starve Marshal Drama — the verified **TRIPLE LOCK** (stalemate=0 glory `jealousy.py:154`; `GLORY_WINDOW=5` decay; `authority>70` +1-threshold dampening at boot-authority 100 `jealousy.py:381`) → **Phase 4** Economy (regressive upkeep + a conquest-free gold sink) → **Phase 5** Vassal loyalty recovery lever → **Phase 6** the parser + every live-found play-friction bug (PF-1…PF-9 + the AI-priority-order tech-debt). Balance numbers are **sweep-tuned, not separately gated**. | none — scope blessed; numbers are sweep-tuned. Land **Phase 0** (harness, low risk), then Phase 1 | **`COMBAT_OVERHAUL_SPEC.md`** |
| **8.EVAL** | **Pre-8.5 Evaluation Gate** (unchanged owner for its rows) | Triage: war-LLM improvement items, DWL-DIP-E7 + DWL-DIP-METTERNICH (triggers go live at Gate 4 passage), DW-2 dual-acceptance-model convergence + war-score credit calibration, DESIGN_REFINEMENT queue items 5-6 (Nation Agendas, Talleyrand Desk), Wave 4/5 items, AI P3-P6 opportunism, arch-plan findings #23. Output: keep/defer/drop list. | Evaluation session with user | ROADMAP §8.EVAL (below) |
| — | **Then the existing spine** | Phase 8.5 (Events/Gazette/Marshal Voice) → STEAM PAGE + LLC → 9 (Advisors) → 10 (Character & People) → 11 (Britain naval/subsidy + governance; vassal core already landed) → Pre-EA (incl. **Pre-Ship Victory & Objectives Pass** — design the real 1805 win/lose conditions the EC-6 sandbox decision deferred; own design gate) → EA. | per phase | below |

Standing deferred rows that survive this staging with owners: DEF-4 (behind the 15× tripwire), DEF-5 naval spec (needed before Phase 11 Britain), ~~Jealousy v3.1 (gate after MC)~~ **✅ LANDED July 11, 2026 as v3.2 (row JV above)**, Historical Precision P1 ministers (EA), Post-EA table.

**Open design decisions parked for the user:** ~~EC-2 sink set~~ (**DECIDED July 8** = ES-2 + ES-7-reframed + ES-1 prereq; **the EC-2 gate itself ✅ BLESSED July 9, 2026** — numbers E1–E6 + the econ-eval amendments recorded in `ECONOMY_REVISIT_SPEC.md` §0.6.7; **no EC decisions remain parked**) · ~~MC-1 ability set~~ + ~~MC-4 personality types~~ (**both DECIDED at the MC gate July 10, 2026** — ten abilities blessed + landed; balanced/loyal deferred by contract + Soult-literal canonized, spec §9) · CR-6 gate (CR-5 scope BLESSED July 5, 2026 — spec §6) · DEF-12 map modes · Jealousy v3.1 (after MC + v3.2 addendum). *(EC-5 Continental System self-cost scope §0.6.6 Q3, EC-7/ES-6 supply timing §0.6.6 Q4, and sandbox soft-goal §0.6.6 Q6 all RESOLVED July 8, 2026 (cont.) — Q3 = Option B symmetric self-cost + Britain income-bite behind the two-sided AI-solvency test (Option A fallback), Q4 = dated trigger opening once the EC-2 pair lands and its AI-solvency band test is green, Q6 = keep the sandbox pure open-ended and defer any soft goal to the Pre-Ship Victory & Objectives Pass; EC-6/DG-5 victory conditions DECIDED July 7, 2026 = sandbox; the Slice H gate was approved + landed July 3, 2026.)*

---

## Quick Status

| Phase | Name | Status |
|-------|------|--------|
| 1-5.3 | Foundation through AI Fixes | COMPLETE |
| **V2a** | **Objection System Refactor** | **COMPLETE** |
| **6** | **Core Campaign Systems** | **COMPLETE** |
| **6.5** | **Information & UI Systems** | **COMPLETE** (map renderer shipped with the July 2, 2026 real-map cutover — 126-province 1805 campaign is the running game) |
| **7 Core** | **Multi-Marshal Coordination** | **COMPLETE.** 7 sessions (57-61a, 61b, 64). ~246 tests. |
| **7b** | Casualty Dist, AI Coord, Reports/UI, Tactical Triangle, V2b | **COMPLETE.** Residuals re-homed July 2, 2026: Jealousy = standing design gate (after the Marshal Content Pass); Gneisenau Staff Work → 8.EVAL triage (its 1805 landing condition arrived with no owner slice); cross-nation coordination → 8.EVAL triage. |
| **8** | **Diplomacy & Peace** | **FUNCTIONALLY COMPLETE July 2, 2026.** Cleanup spec v0.32; all settlement slices + Guided Terms + Slice G1 landed (`1a9da53`); SC-32 formally closed; **Gate 4 PASSED in full + Slice H LANDED July 3, 2026 — the Phase 8 arc is FULLY complete with no live successors.** See `docs/STATUS.md`. |
| **8.EVAL** | **Pre-8.5 War LLM + Diplomacy Refinement Evaluation** | **Planned after Imperial Settlement final gate, before 8.5.** Audit buried war-LLM improvement items, battle/war narration toggle scope, creative-command war uses, `DESIGN_REFINEMENT.md` diplomacy queue items, AI ultimatums/trade/agenda/motive/Talleyrand Desk candidates, and decide what ships before 8.5 vs moves to Pre-EA/Post-EA. **+ July 3, 2026 AI-audit routed items (balance-sensitive; findings verified, fixes deliberately deferred to this triage):** (a) AI proposal anti-spam retune for 19-nation scale (turn-1 envoy flood, `ai_diplomacy.py` P-trigger cooldowns); (b) P2 "stalemate" armistice trigger counts battle-free turns from WAR START — the whole Third Coalition sues for armistice by turn ~5-7 with zero combat (`ai_diplomacy.py:426`; candidate fix: require ≥1 battle or count from last battle); (c) AI settlement offers always demand the PLAYER pay the gold indemnity regardless of who is losing (`ai_diplomacy.py:1867` — direction by war score); (d) re-adding the M3 territory sweetener needs real region selection + ratification wiring (the inert numeric version was REMOVED July 3); (e) enemy-AI selection sort ignores `action_priority` (divergence from ENEMY_AI_REFERENCE.md's contract — changing it reorders ALL AI behavior, needs a balance pass); (f) `_evaluate_marshal` side-effect-free refactor remainder (threat-responder claims + refortify-cooldown still commit during candidate evaluation; the own-claim lockout and the worst oscillation cases were fixed July 3); (g) `diplomatic_advisory.py` dead strength tier + off-by-one military-advantage bands. |
| **CR** | **Command Robustness** (NEW July 2, 2026) | Next major phase after A-items — `COMMAND_ROBUSTNESS_SPEC.md` (user priority) |
| **EC** | **Economy Revisit** (NEW July 2, 2026) | `ECONOMY_REVISIT_SPEC.md` (user priority) |
| **AUD** | **Comprehensive Codebase Audit** (Fable, fix-as-you-find) | **✅ Correctness sweep COMPLETE July 9, 2026** (7 fixes, 0 escalations — `docs/audits/AUDIT_2026_07_09.md`); **✅ econ eval (§0.7) COMPLETE same day** (`docs/audits/ECONOMY_ECON_EVAL_2026_07_09.md`); the §8 fun-factor capstone runs post-EC. `AUDIT_GUIDELINE.md` |
| **MC** | **Marshal Content Pass** (NEW July 2, 2026) | `MARSHAL_CONTENT_PASS_SPEC.md` — NEEDS DESIGN GATE |
| 8.EVAL | Pre-8.5 Evaluation Gate | **Trigger LIVE (Gate 4 passed July 3, 2026)**; sequenced after CR/EC/MC — see §Current Phase Queue |
| 8.5 | Events, Goals & National Identity | Planned, blocked on 8.EVAL |
| -- | **STEAM PAGE + LLC** | **After 8.5** |
| 9 | Advisors (Minimal) | Planned |
| 10 | Character & People (Minimal) | Planned |
| 11 | Britain (naval/subsidy) & Imperial Governance | Planned — vassal core LANDED in Phase 8; remaining rows are Britain naval/subsidy pressure (needs DEF-5) + governance promotion |
| Pre-EA | Polish & Infrastructure | Planned |
| EA | 1805 Campaign | TBD 2026 — the 126-province map shipped FULLY WIRED July 2, 2026 (Option C partial wiring is superseded) |

**Phase 8 settlement closure record (July 2, 2026):** cleanup spec v0.32 GO with all five slice families + SC-5R + SC-32/G2 + SC-31 landed; Guided Terms complete (June 10); CH-1..5 landed; the ONE end-of-queue Gate 4 smoke RAN July 2 (16 findings, 11 fixed at `7635229`; machine half green) and **the visual half was user-confirmed July 3, 2026 — GATE 4 PASSED**; Slice G1 landed July 2 at `1a9da53` (SC-30 closed; SC-32 formally closed); **Slice H (the two full-agency ally petitions) gate-approved + LANDED July 3, 2026 — the settlement arc is closed with no live successors.**

**Removed from EA scope:** Phase 12 (Communication cutoff), Naval abstraction, Full advisor action-gating. See [Post-EA Expansion](#post-ea-expansion).

---

## Completed Phases

| Phase | Name | Tests | Key Features |
|-------|------|-------|--------------|
| 1 | Foundation | ~80 | Core loop, actions, regions, marshals |
| 2 | Combat & AI | ~90 | Dice combat, enemy AI, stances, drill/fortify |
| 3 | Relationships | ~30 | Marshal relationships, historical values |
| 4 | LLM Integration | ~60 | Parsing, personality responses, BYOK |
| 5.1 | Tactical Feedback | 64 | Word-based scoring, strategic feedback |
| 5.2 | Strategic Commands | ~350 | MOVE_TO, PURSUE, HOLD, SUPPORT, interrupts, modding, Phase M (Strategic Objections) |
| 5.3 | Enemy AI Fixes | ~15 | Stagnation counter, oscillation fixes, consolidation |

**Total Tests:** 3799 (verified Feb 24, 2026 — historical; the suite was **10,781 passed, 1 skipped** at Slice G1, July 2, 2026)

---

## V2a: Objection System Refactor

**Status:** COMPLETE. All 7 units shipped (1216 tests). Deterministic situational triggers, trust affects consequences only, MILD concerns as flavor text. V2b (defiance/vindication) deferred to Phase 7b. See `OBJECTION_V2.md`.

---

## Phase 6: Core Campaign Systems

**Goal:** Complete playable campaign loop with resources and campaign pressure. Hard victory conditions are optional scenario content, not a core requirement.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Economy | Income per region, treasury, upkeep | Medium | **COMPLETE** (6.2.A-H). Economy balance revisit for 1805. |
| Reinforcements (Enemy) | AI can recruit troops | Low | **COMPLETE** |
| Manpower Pools | Separate: Infantry, Cavalry, Artillery | Medium | **COMPLETE** |
| Attrition | Movement/supply decay | Low | **COMPLETE** |
| Fog of War | Hidden enemies, scouting required, watchtower building | Medium | **COMPLETE** (Sessions 32-36, 38). 157 tests. See `FOG_OF_WAR_SPEC.md`. |
| Terrain | Region terrain affects combat/movement | Medium | **COMPLETE** (6.1.A+B). |
| Sieges | Fortified cities require siege mechanics | Medium | **Deferred to 1805** — fort + contested capture sufficient for 19-region map. |
| City Fortification | "Fortify this city" building action | Low | **COMPLETE** |
| Artillery Unit Type | Third marshal type with bombardment | Medium | **COMPLETE** (Sessions 42-44, 48-52). 127+ tests. |
| Turn Events Log | Track battles/captures/retreats per turn | Low | **COMPLETE** |
| Player Garrison | Detach 3k troops to garrison a region | Low | **COMPLETE** |
| Enemy AI Garrison | AI places garrisons via Building Blocks | Low | **COMPLETE** |
| Save/Load | Full game state persistence + autosave | Low | **COMPLETE** |
| Berthier Parse Recovery | Failed parses -> in-character clarification | Low | **COMPLETE** |
| Post-Battle Analysis | Modifier breakdown, casualties, Berthier observation | Low | **COMPLETE** |

### MAP COMMISSIONING REMINDER

**Commission the Europe map during Phase 6 development.** Art takes 2-4 weeks; should be ready for Phase 6.5 renderer integration.

**Map approach: EU4-style bitmap color map** (NOT SVG).

**Artist brief:**
- 1805 Europe, Portugal to Moscow, Scandinavia to Ottoman Balkans
- EU4 political map style
- ~120-150 province outlines (we wire ~80-100 for EA v1, rest greyed out)
- **Two deliverables:** (1) visual map (pretty, what players see), (2) province color map (each province = unique solid RGB color, same dimensions, pixel-aligned)
- Include coastlines for Britain and North Africa where visually useful; any greyed/unwired areas are map-art staging, not active settlement powers
- Each province must be a distinct closed region for hover detection and color fill
- Artist familiar with Paradox modding ideal — this is the standard EU4 approach

**Province count target: ~80-100 wired for EA v1:**

| Area | Regions | Notes |
|------|---------|-------|
| France | 10-12 | Core gameplay area |
| Low Countries | 3-4 | Belgium, Netherlands, Luxembourg |
| German States | 14-18 | Confederation of the Rhine heartland |
| Austria/Habsburg | 8-10 | Vienna to Transylvania |
| Italy | 8-10 | Piedmont to Sicily |
| Iberia | 6-8 | Peninsular War theater |
| Russia (to Moscow) | 8-10 | Warsaw, Lithuania, Smolensk, Moscow, St. Petersburg |
| Scandinavia | 3 | Denmark, Sweden, Norway |
| Ottoman Europe | 6-8 | Constantinople, Greece, Serbia, Balkans |
| Switzerland | 1-2 | |

**Hit detection:** Sample pixel from hidden color map at mouse position -> dictionary lookup -> province ID. O(1), no polygon math.

**Implementation plan:** See `docs/archive/PHASE6_IMPLEMENTATION_PLAN.md` for session-by-session breakdown.

**Dependencies:** None
**Exit Criteria:** Player manages economy, enemies reinforce, terrain matters, can save/load, failed parses feel in-character

---

## Phase 6.5: Information & UI Systems

**Goal:** Player can track 80-100 regions, 30 marshals, 8 nations without drowning.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Notification System | EU4-style persistent alerts (9 triggers, 3 priority tiers) | Medium | **COMPLETE** (70 tests) |
| Top Bar Framework | Unified top bar (CanvasLayer 75), screen controller, dispatch re-read | Medium | **COMPLETE** (8 tests). Spec: `TOP_BAR_SPEC.md`. |
| Strategic Ledger | 6-section overview: forces, territories, economy, intel, manpower, orders (with cancel buttons) | Medium | **COMPLETE** (54 tests). Spec: `TOP_BAR_SPEC.md`. |
| Marshal Management UI | View all marshals, relationships, abilities, biography, personality/unit type descriptions | Medium | **COMPLETE** (68 tests) |
| Campaign Log | Fog-filtered event log, Godot overlay (L key) | Low | **COMPLETE** (57 tests) |
| Tooltips | Hover info on regions, marshals, nations | Low | **Absorbed into Map Renderer** — existing 3 tooltip variants (marshal 20+ fields, fogged force, region 12+ fields) sufficient. Remaining gaps (region occupant summary, off-screen clamping, theming) handled by Map Renderer items 24/32/42 and Phase 7b Session 66. |
| Morning Dispatch | Berthier's turn-start briefing (SITUATION, MARSHAL STATUS, INTELLIGENCE) | Low | **COMPLETE** (57 tests) |
| Tutorial Infrastructure | `TutorialManager` for staged popups/highlights | Medium | **Deferred to Pre-EA** — element highlighting is throwaway before Map Renderer, content grows through Phase 8.5, existing popup infrastructure sufficient. Build against stable scene tree + final mechanics during Pre-EA polish. |
| Map Renderer | EU4-style bitmap map integration. See Map Renderer Notes below. Includes tech debt cleanup: extract shared `_format_number()` and color palette from 3 UI scripts into `utils.gd` autoload. | High | **IN PROGRESS** — Slices 1-3 COMPLETE (shared layers, province color-map, Camera2D+SubViewport). Remaining: commissioned art + Godot smoke validation. |
| Pause Menu | Smart Esc → Save/Load/Settings/Quit | Low | **COMPLETE** |
| Wire Marshal Abilities | Drouot/Wellington/Blucher/Uxbridge wired. Gneisenau deferred to Phase 7. | Medium | **COMPLETE** (54 tests) |

### Special Abilities Exploration (Post-Phase 6.5) — COMPLETE

**Evaluation complete.** See `docs/SPECIAL_ABILITIES_EVALUATION.md` for full analysis.

**Wired abilities (6):** Ney (+2 shock), Davout (+20% attack after defending), Drouot (15% fort degradation), Wellington (+5% defense), Blucher (+3k pursuit), Uxbridge (+5k pursuit). All reviewed and confirmed balanced for Phase 7 coordination mechanics.

**Davout's Counter-Punch Mastery — IMPLEMENTED.** +20% attack on next attack after being attacked (any outcome, any target). Combos with cautious personality's free counter-punch for the Auerstedt fantasy. 22 tests.

**Grouchy:** His literal personality IS his ability — no separate mechanic needed.

**1805 roster planning:** Principles documented. Only ~10-12 of ~30-40 total generals across all nations should have unique abilities. Candidates listed per nation. Enemy abilities deferred to 1805 roster build.

**Adding new abilities:** Full checklist added to `docs/ADDING_CONTENT.md` → "Wiring a Special Ability" section (16 steps, common mistakes, auto-detect vs manual wiring audit).

### Map Renderer Notes

The map transition replaces ALL procedural drawing in `map.gd` (circles, lines, draw_string) with commissioned art + sprite assets. Five workstreams: art integration, sprite assets, scene architecture, code refactor, validation & polish.

#### A. Art Integration (requires commissioned map)

1. **Visual map layer** — `Sprite2D` for the pretty map (what the player sees). Artist draws borders, terrain features, region labels, coastlines, cities. PNG format (lossless). Artist and dev must agree on exact pixel dimensions upfront.
2. **Province color map** — Hidden `Image` loaded in memory (NOT as texture — need pixel-level `get_pixel()` access). Each province is a unique flat RGB color, pixel-aligned to visual map. **CRITICAL: No anti-aliasing, no dithering, no JPEG compression on this file.** Anti-aliased border pixels blend two province colors and match NEITHER in the lookup table — hit detection breaks silently. PNG only. Must be same dimensions as visual map.
3. **Province definition mapping** — JSON data file mapping each RGB color `[r, g, b]` to a region name. Must be loadable by both Godot (for hit detection) and backend (for validation). Include a "no province" sentinel color for ocean/empty space (e.g., pure black `[0,0,0]`). Example: `{"128,0,0": "Paris", "0,128,0": "Belgium", ...}`.
4. **Region anchor points** — Per-province `Vector2` coordinates for placing unit icons, garrison indicators, building icons. Either artist marks anchor positions in a reference layer or derive center-of-mass programmatically from the color map. Replaces current `REGION_POSITIONS` dict. Include in the JSON definition file alongside RGB colors.
5. **Nation color shader** — Fragment shader reads province color map as a uniform texture, compares pixel to active province colors, swaps to nation color. Pass per-province controller data as a uniform (texture or array). Must handle: conquest mid-game (province changes color), neutral regions (light green), unplayable provinces (grey).
6. **Fog of war shader** — Per-province darkening/overlay based on visibility level (5 tiers: FULL → no overlay, PARTIAL → slight dim, STALE → medium grey, LAST_KNOWN → dark grey, UNKNOWN → near-black). Replaces current `FOG_OVERLAYS` color constants drawn over circles. Pass per-province visibility as uniform data alongside the nation color shader (can be combined into one shader pass).
7. **Province highlight shader** — When mouse hovers a province, pass the hovered province's RGB color as a uniform. Shader highlights all pixels matching that color on the visual map (glow, brightened border, pulse). Separate selected vs hovered states (different highlight colors).
8. **Greyed-out unplayable provinces** — Provinces in the art but not wired for gameplay. §4.4 landed as a CPU-side `Image.lerp` overlay: `map_renderer_base.gd::_apply_unwired_grey_overlay()` stamps `UNWIRED_GREY_COLOR` over every visual pixel whose lookup color belongs to an unwired province, blended by `UNWIRED_GREY_BLEND = 0.7` before `ImageTexture.create_from_image()`. No shader. Non-interactive: color map lookup returns province ID but game ignores input on unwired provinces.

#### B. Sprite Assets (commission alongside or after map)

All icons become proper textures instead of procedural `draw_rect`/`draw_arc`/`draw_string`. **Pack all sprites into a single spritesheet/atlas** for draw call batching (important at 80+ provinces with multiple icons each).

9. **Marshal unit sprites** — Per-nation variants (France/Britain/Prussia/Austria/Neutral). Small flag or officer icon. Plus fogged/silhouette versions with "?" overlay for PARTIAL/STALE enemies. Need enough visual distinction at small sizes (map may be zoomed out).
10. **Garrison shield sprite** — Small shield icon. Tint per nation at runtime via `modulate` (one base asset) or per-nation variants if tinting looks wrong.
11. **Unit type badges** — Infantry (crossed rifles), Cavalry (horseshoe/sabre), Artillery (cannon) — small overlay on or beside marshal sprite. Must read clearly at default zoom.
12. **Status indicator sprites** — Fortified (rampart), Retreating (arrows), Broken (skull), Drilling (crossed swords), Shock Ready (lightning), Strategic Order (scroll/banner), Holding (anchor). Small enough to stack beside marshal sprite without clutter.
13. **Building icons** — Supply Depot, Fortification, Training Ground, Market, Stables. Plus damaged variant (cracked/red tint) and under-construction variant (scaffold). Displayed on the province near anchor point.
14. **Watchtower sprite** — Active (tower with flag), Under Construction (scaffold), Damaged (crumbling). Positioned on province.
15. **Bombardment indicator** — Cannon flash or smoke puff for bombardment events (transient, shown during bombardment resolution).

#### C. Scene Architecture (design before coding)

16. **Scene tree hierarchy** — MapArea becomes a proper scene (`.tscn`) with structured children instead of a flat Control with `_draw()`. Hierarchy:
    ```
    MapArea (Node2D)
    ├── Camera2D (zoom/pan)
    ├── VisualMap (Sprite2D — the pretty map)
    ├── NationColorOverlay (Sprite2D + shader — province nation tinting)
    ├── FogOverlay (Sprite2D + shader — per-province fog darkening)
    ├── HighlightOverlay (Sprite2D + shader — hover/select glow)
    ├── BuildingLayer (Node2D — building icon sprites per province)
    ├── GarrisonLayer (Node2D — garrison shield sprites per province)
    ├── MarshalLayer (Node2D — marshal unit sprites, stacked per province)
    ├── StatusLayer (Node2D — fortified/retreating/broken indicators)
    └── TooltipPanel (CanvasLayer — PanelContainer + Labels, screen-space)
    ```
    Z-order: map → nation color → fog → highlight → buildings → garrisons → marshals → status → tooltips. Tooltips on a CanvasLayer so they render in screen space regardless of zoom/pan.

17. **Camera2D instead of manual transform** — Replace `draw_set_transform(pan_offset, 0.0, Vector2(zoom_level, zoom_level))` with a proper Camera2D node. Built-in zoom, pan, smoothing. Set `Camera2D.limit_left/right/top/bottom` to map pixel bounds — prevents panning into empty space. Zoom-to-cursor logic adapts from current `_zoom_at_point()`.

18. **Marshal sprite stacking** — Multiple marshals in one province (Phase 7 encourages co-location) need a spreading algorithm. Options: horizontal fan-out from anchor point, or grid layout. Cap visible icons (e.g., 6) with a "+N more" indicator if exceeded. Must not overlap garrison shield below or region label. Current code already handles this with offset math — port the layout logic to position child sprites.

19. **Sprite atlas** — All marshal/garrison/status/building icons in a single `AtlasTexture` spritesheet. Godot batches draw calls for sprites sharing a texture. At 80+ provinces × 3-4 icons each = 300+ sprites — batching matters.

20. **Preserve `update_all_regions()` contract** — `main.gd` calls `map_area.update_all_regions(map_data)` from 10+ places. The function signature and data format must NOT change. Internally, it switches from setting dict values + `queue_redraw()` to showing/hiding/repositioning child sprite nodes and updating shader uniforms. This is the primary integration point — getting this right prevents regressions across the entire frontend.

#### D. Code Refactor (after art + sprites delivered)

21. **Rip out procedural drawing** — Remove `_draw_regions()`, `_draw_connections()`, `_draw_marshal_icons()`, `_draw_fogged_force_icons()`, `_draw_garrison_indicator()`, `_draw_tooltip()`, `_draw_fogged_tooltip()`, `_draw_region_tooltip()`, and all `draw_circle`/`draw_arc`/`draw_rect`/`draw_line`/`draw_string` calls from `map.gd`. The entire `_draw()` override goes away. Remove `queue_redraw()` calls (no longer needed — Godot scene tree handles rendering).

22. **Input refactor** — Replace distance-to-circle hit detection with color map pixel lookup. `_gui_input()` reads pixel from hidden Image at mouse position (accounting for Camera2D transform), looks up province in definition dict. Return "no province" for ocean/empty pixels. Emit `region_hovered(region_name)` and `region_clicked(region_name)` signals.

23. **Sprite-based unit rendering** — Marshal icons, garrison shields, status indicators become `Sprite2D` child nodes positioned at region anchor points. `update_all_regions()` iterates game state and shows/hides/repositions sprites. Pool sprite nodes (pre-create a max count, show/hide as needed) rather than add/remove children every update.

24. **UI-based tooltips** — Replace manual `draw_string` tooltip rendering (~400 lines across 3 functions) with a `PanelContainer` + `VBoxContainer` + `Label` nodes on a CanvasLayer. Populate label text on hover. Clamp tooltip position to screen bounds (prevent off-screen overflow). Three tooltip variants preserved: marshal (full detail), fogged force (name/band/intel), region (controller/terrain/economy/buildings). Tooltip theming: dark panel, gold accents, consistent with BottomLeftUI aesthetic.

25. **Zoom/pan via Camera2D** — Remove manual `zoom_level`, `pan_offset`, `draw_set_transform()`, `_zoom_at_point()`. Use Camera2D with `zoom` property and `position` for pan. Keep: mouse wheel zoom toward cursor, middle-click drag pan, arrow key pan. Add: map edge clamping (can't pan past map bounds).

26. **Remove dead constants** — Delete `REGION_POSITIONS` (replaced by anchor points from definition file), `REGION_CONNECTIONS` (adjacency is visual on real map), `FOG_OVERLAYS` (replaced by shader uniforms). Keep `COLORS` dict — still needed to pass nation colors as shader uniforms.

27. **Clean up debug prints** — Remove all `FORTIFY_DEBUG`, `TOOLTIP DEBUG`, `print("Clicked region:")` statements from map.gd. Replace with conditional debug overlay (togglable in settings).

28. **`_on_region_clicked` signal emission** — Currently just `print()`. Must emit a signal that `main.gd` can connect to. Use case: clicking a province could pre-fill the command input with a region name, show a context panel, or select a marshal in that province.

#### E. Validation, Polish & Edge Cases

29. **Color map validation script** — Python script (runs at asset delivery) that: (a) loads the color map PNG, (b) extracts all unique RGB colors, (c) checks every color has an entry in the definition JSON, (d) checks every entry in the definition JSON exists in the color map, (e) flags any colors that appear fewer than N pixels (likely anti-aliasing artifacts that shouldn't be there). Run this BEFORE integration.

30. **Coordinate system alignment** — Godot Y-axis increases downward, same as image coordinates. Confirm artist delivers map with north at top. Anchor points are in image pixel coordinates. Camera2D position maps directly. No coordinate inversion needed (but verify).

31. **Memory budget** — 4K visual map: ~30MB uncompressed RGBA in memory. 4K color map: ~30MB as Image (pixel access, not GPU texture). Total ~60MB for maps alone. Acceptable on desktop. If targeting lower-spec machines, consider 2K with upscale shader, or compress visual map (color map must stay uncompressed for pixel-exact reads).

32. **Tooltip off-screen clamping** — Current tooltips can overflow past window edge (tooltip_pos = mouse + offset, no bounds check). New tooltip PanelContainer must clamp: if tooltip would extend past right edge, flip to left of cursor. Same for bottom edge.

33. **Multi-marshal overlap prevention** — With 5+ marshals in one province (Phase 7 co-location), sprite icons pile up. Need: max visible count with "+N" overflow badge, or dynamic icon scaling that shrinks icons when count exceeds threshold. Test with worst case: 6 marshals + garrison + 2 buildings + watchtower on one province.

34. **Fog transition smoothness** — When visibility level changes (e.g., scout reveals UNKNOWN → FULL), the shader should transition smoothly (0.3s fade) rather than snapping. Tween the fog uniform value per province. Low priority but high polish.

35. **Zoom-level-dependent detail** — At maximum zoom-out, marshal name labels become unreadable. Options: hide name labels below a zoom threshold (show only icon), or scale label font with zoom. Building/watchtower icons may also need to hide at extreme zoom-out. At maximum zoom-in, show more detail (exact troop count on marshal sprite?).

36. **Minimap** — At 80+ provinces with zoom, player needs spatial awareness. Small minimap in corner showing full map with a viewport rectangle indicating current view. Implementation: `SubViewport` rendering the map at small scale into a `TextureRect`, overlaid with a rectangle showing Camera2D's visible area. Low priority for 13 provinces, essential for 80+.

37. **Edge-of-screen pan** — Mouse at screen edge scrolls the map (standard in strategy games). Detectable in `_process()`: if mouse x < 20px, pan left. Optional toggle in settings (some players prefer drag-only). Low priority.

38. **Keyboard navigation** — Home key centers camera on capital. Number keys or hotkeys jump to specific marshals. Not a blocker but the Camera2D architecture should support `camera.position = anchor_points["Paris"]` for instant jumps.

39. **Incremental transition strategy** — Don't flip everything at once. Phases:
    - **Step 1:** Load visual map as Sprite2D background behind existing procedural drawing. Verify scaling/positioning.
    - **Step 2:** Implement color map pixel lookup alongside existing circle hit detection. Verify both agree.
    - **Step 3:** Replace procedural marshal icons with sprites. Keep old tooltips.
    - **Step 4:** Replace procedural tooltips with UI nodes.
    - **Step 5:** Switch to Camera2D, remove manual transform.
    - **Step 6:** Enable shaders (nation color, fog, highlight). Remove remaining procedural drawing.
    - **Step 7:** Remove all dead code, constants, debug prints.
    Each step is independently testable and the map is functional throughout.

40. **main.tscn scene update** — Current scene tree has `MapArea` as a plain `Control` node with `map.gd` script. Must be restructured: either convert to a packed scene (`map.tscn`) instanced in main, or rebuild the node tree in `main.tscn` directly. The `@onready var map_area = $MapArea` reference in `main.gd` must still resolve.

41. **Regression test: all 5 fog levels** — After refactor, manually verify each visibility state renders correctly: FULL (clear, all data), PARTIAL (slight dim, fogged enemy silhouettes with strength bands), STALE (medium fog, stale ghost icons), LAST_KNOWN (dark, minimal data), UNKNOWN (near-black, no military intel). Current code handles all 5 — the refactor must preserve every behavior.

42. **Regression test: all tooltip variants** — Marshal tooltip (20+ fields: name, nation, strength, morale, movement, skills, personality, trust, vindication, stance, unit type, drilling, fortified, retreating, broken, abilities, strategic order, artillery ammo). Fogged force tooltip (name, nation, strength band, intel quality). Region tooltip (name, controller, type, terrain, income, stability, supply, garrison, war damage, buildings, construction, watchtower). Every field must survive the refactor.

43. **Debug overlay toggle** — Development aid: key shortcut to show the color map instead of the visual map, display anchor points as dots, show province RGB values on hover. Strip from release build or gate behind debug setting.

### Option C: Partial Europe Wiring

> **SUPERSEDED BY SHIPPED REALITY (Map Slices 1–9, closed July 2, 2026):** the commissioned art arrived with **126 provinces and ALL of them landed wired and in play** — the running game is the full 1805 Europe campaign (see `docs/MAP_IMPLEMENTATION_PLAN.md` + `docs/STATUS.md`). No partial-wiring EA staging is planned; the `wired:false` grey-out machinery (§4.4) stays available for future maps/mods.

Wire ~80-100 provinces for EA v1. Remaining provinces from the 120-150 in the art are visible but greyed out. Expand playable area in EA updates. Players see this as a roadmap, not a limitation.

**Dependencies:** Phase 6 (needs data to display), commissioned map art
**Exit Criteria:** Player has clear visibility into game state, map looks professional

---

## Phase 7 Core: Multi-Marshal Coordination

**Goal:** "Position IS Coordination" — automatic positional bonuses make multi-marshal positioning the core strategic skill. Relationships have real mechanical impact and evolve through shared experience.

**Design Principle:** All coordination bonuses are automatic and positional. No new command syntax. Building Blocks principle — enemy AI benefits identically from the same passive bonuses. See `docs/MULTI_MARSHAL_SPEC.md` for full spec + `docs/PHASE7_SPEC_AMENDMENTS.md` for audit corrections.

**Architecture:** Coordination bonuses flow through transient fields on Marshal, read by `get_attack_modifier()` / `get_defense_modifier()` (Golden Rule #1). `combat.py` reads them, never recalculates. AI earns bonuses through co-location duration (not strategic commands it cannot issue).

**Scope Decision (Feb 20, 2026):** Full spec is 10 sessions (57-66, ~340 tests). Phase 7 Core ships 6 sessions. Sessions 62 (casualty distribution), 63 (AI coordination enhancements), 65 (full battle reports), 66 (Godot tooltips/tutorial/audit) deferred to Phase 7b. Rationale: Core delivers all player-facing coordination mechanics + the Grouchy Rule + dynamic relationships. Casualty distribution deferred because (a) it modifies `resolve_battle()` contract (highest-risk change in spec), (b) coordination works without it (allies provide bonuses, primary combatant absorbs casualties), and (c) playtest data should inform the proportional distribution design. AI enhancements deferred because AI already benefits from passive coordination when co-located. Each core session includes basic combat display messages — no separate presentation session needed.

### Phase 7 Core Sessions

| Session | Feature | Description | Complexity | Tests | Status |
|---------|---------|-------------|------------|-------|--------|
| **57** | **Combined arms** | 1/3=0%, 2/3=+10%/+5%, 3/3=+20%/+10%. Unit type diversity, NOT relationship-scaled. Includes basic combat message. | Medium | 43 | **COMPLETE** |
| **58** | **Coordination bonus + hard cap** | +3% atk/+5% def per ally, relationship-scaled (Hostile 0%→Devoted 150%). Hard cap: +25% atk/+20% def. Includes per-ally message. | Medium | 44 | **COMPLETE** |
| **59** | **Dedicated coordination + co-location** | +5%/+5% flat from 2-turn co-location (both sides) OR SUPPORT order (player, immediate). New serialized fields. Includes status message. | Medium | 31 | **COMPLETE** |
| **60** | **Adjacent support bonus** | +2% atk per adjacent friendly marshal. Not relationship-scaled. Includes adjacent count message. | Low | 23 | **COMPLETE** |
| **61a** | **Adjacent reinforcement (core)** | Arrival score formula, base reinforcement, near-miss, serialization, SUPPORT clearing, retreat timing. | High | 49 | **COMPLETE** |
| **61b** | **Adjacent reinforcement (edge cases)** | Grouchy Rule, Hostile exclusion, `moved_this_turn` eligibility, fortified SUPPORT advisory. | Medium | 22 | **COMPLETE** |
| **64** | **Win/loss relationships** | Shared battle → relationship check. Severity-scaled. 3-turn cooldown. Rivalry Resolved. Relationship change notification. | Medium | 34 | **COMPLETE** |

**Key formulas:** Combined arms (type count), Coordination (per-ally × relationship scaling), Arrival score (logistics ×5 + relationship ±20 + terrain ±10 + personality ±5 ± variance, threshold >60/65), Win/loss (severity-scaled, asymmetric: winning together builds faster than losing destroys).

**Note on casualty model:** Without Session 62, combat remains 1v1 between primary attacker/defender. Allied marshals provide coordination bonuses and share retreat fate (Session 61 reinforcement) but do not take proportional casualties. This is a simplification, not a bug. Supply attrition limits stacking. Session 62 in Phase 7b upgrades this to full proportional distribution.

### Phase 7b

Items deferred from Phase 7 Core + items that build on coordination data:

**Deferred from Phase 7 Core (ship first in 7b):**

| Session | Feature | Description | Complexity | Tests | Status |
|---------|---------|-------------|------------|-------|--------|
| **62** | **Casualty distribution** | `resolve_battle(apply_casualties=False)`. Proportional by strength. Hostile = 0%. See amendments C1/C2 for full contract. | High | 63 | **COMPLETE** |
| **63** | **AI enhancements** | P4.6 coordinated attack, P4.75 mod, P4.76 co-location persistence, P4.77 cross-nation, P4.78 defensive positioning. | High | 35 | **COMPLETE** |
| **65** | **Battle reports & Berthier** | 7 coordination observation categories. Berthier names all reinforcers (arrival/failure/mixed). Full observations. | Medium | 24 | **COMPLETE** |
| Gate 4 | **Combat path fixes** | general_attack delegation, reinforcer stalemate retreat, auto-assign delegation, artillery no-advance, Berthier narrative voice. | Medium | 23 | **COMPLETE** |
| **66** | **Godot UI + integration audit** | Tooltips, tutorial inline-dramatic, display formatting, cross-system audit, doc updates. | Medium | 32 | **COMPLETE** |

**Linked Group — Tactical Triangle Completion (2 sessions):**

Design approved. See `docs/TACTICAL_TRIANGLE_SPEC.md` for full spec.

| Session | Feature | Description | Complexity | Est. Tests | Status |
|---------|---------|-------------|------------|------------|--------|
| **67** | **Square Formation** | Infantry-only anti-cavalry stance (-40% cav dmg), vulnerable to artillery (+50%), +5% defense. Auto-break on move/attack. 1 AP. AI P2.5. 3 objection triggers. | Medium | ~40 | Planned — DESIGN APPROVED |
| **68** | **Auto-Bombardment + Overwatch** | Artillery on SUPPORT auto-bombards before combat. Passive -3% attack debuff per friendly artillery in region (cap -9%). | Medium | ~45 | Planned — DESIGN APPROVED |

**Other deferred items:**

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| **V2b: Defiance/Vindication** | MODERATE/STRONG/EXTREME concerns trigger defiance (5%/15%/35% base). 40% hard cap, vindication decay, authority feedback loop, fog migration, relationship SUPPORT objections. Full spec: `V2B_DEFIANCE_SPEC.md`. Sessions 0-3 + audit cleanup. | Medium | **COMPLETE** |
| **Jealousy system** | Marshal getting all glory → others resent. Needs multi-marshal battle data from Phase 7. Open: trigger threshold, consequence type, duration, objection interaction. | Medium | Deferred — NEEDS DESIGN |
| **Cross-nation coordination** | Coalition partners coordinate. The diplomacy layer now provides alliance/coalition state. See amendments C3. | Medium | **Re-homed July 2, 2026 → 8.EVAL triage** (was an unowned deferral) |
| **Gneisenau Staff Work** | +10% ally bonus — Coalition-specific advantage. | Low | **Re-homed July 2, 2026 → 8.EVAL triage** (its "1805 full campaign" landing condition arrived July 2 with no owner slice; note Gneisenau is not in the shipped 21-marshal roster — the triage decides implement-on-roster-add vs drop) |

**Moved to Phase 8:** Coalition Trigger — threat mechanics are inherently diplomatic and should ship alongside peace treaties and nation relations.

### V2b Audit Findings (from V2a audit) — RESOLVED

All items shipped in V2b Sessions 0-3 + audit cleanup:
- **Defensive vindication:** Wired in Session 1 (creation, resolution, stale clearing).
- **Vindication decay:** Implemented (-1 per 3 turns of no objection activity).
- **Idle marshal objection:** Moved to V2a Unit 6 (see V2a section above).
- **Aggressive trigger escalation:** Wired via vindication escalation (v_score > 0 → +1 ConcernLevel).
- **Objection audit cleanup:** Master Rules #1/#2 — validated fallback chains + exhaust→MILD demotion. 10 flagged issues fixed, 4 design notes documented.

### AI Enhancements for Scale (1805)

**AP Scaling:** With 15-20 enemy marshals, 4 AP per nation causes action starvation. AP should reflect national bureaucratic capacity:

| Nation | Base AP | Rationale |
|--------|---------|-----------|
| France | 5 | Corps system, Napoleon's genius |
| Prussia | 4 | Efficient, reformed military |
| Britain | 4 | Competent but parliamentary delays |
| Russia | 3 | Vast but slow |
| Austria | 3 | Bureaucratic, multi-ethnic complexity |
| Minor nations | 2 | Limited administration |

Additional: tiered actions (free basic actions for idle marshals, AP only for offensive), strategic order conflict detection.

### AI Enhancement: Combined Strength Evaluation (IMPLEMENTED)

AI evaluates attack decisions using combined strength of all friendly marshals in the same region. Affects DECISION-MAKING only. Phase 7 coordination system gives these decisions mechanical teeth.

### AI Enhancement: P0 Survival Instinct

If marshal strength < 20% of starting_strength AND enemy in same region -> ALWAYS retreat regardless of personality. Threshold personality-adjusted: Cautious 30%, Normal 20%, Aggressive 15%.

**Dependencies:** Phase 6 (economy, supply attrition, artillery unit type)
**Phase 7 Core Exit Criteria:** Coordination bonuses apply automatically in combat, relationships affect and evolve through coordination quality, Grouchy Rule fires with inline-dramatic narrative, ~190 new tests, basic coordination messages in combat output
**Phase 7b Exit Criteria:** Proportional casualty distribution, AI deliberately seeks coordination, full battle reports with Berthier coordination observations, Godot tooltips with reinforcement probabilities, tactical triangle complete, V2b defiance/vindication

---

## Phase 8: Diplomacy & Peace

**Goal:** Wars start and end through negotiation. Diplomacy feels like talking to PEOPLE.

**Full spec:** `docs/DIPLOMACY_SPEC.md` (v2.3, master-audited) + `docs/CONVERSATIONAL_DIPLOMACY_DESIGN.md` (v1.2, master-audited) + `docs/COALITION_SPEC.md` (v1.1, master-audited). 5 nations, 19 regions, acceptance formula, Talleyrand defiance, vassal system, war score, coalition formation/breaking. Master audit: 4 CRITICAL + 4 MAJOR findings fixed. Fun score 81/100.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Map Expansion + Nations | 19 regions, 5 nations (France/Britain/Prussia/Austria/Saxony), 4 new marshals | Medium | SPEC COMPLETE |
| Diplomatic States | WAR→ARMISTICE→PEACE→...→ALLIANCE + downgrade transitions | Medium | SPEC COMPLETE |
| Acceptance Formula | Deterministic: base + war_score + relation + threat + sweetener + skill + personality | Medium | SPEC COMPLETE |
| War Score | Territory ±40 + battles ±30 + decisive battle ±20 + capital ±30. Inline formula (§6e) | Medium | SPEC COMPLETE |
| Talleyrand Commands | Propose/demand via text. Parser routing (§2f). Missions (§2e) | Medium | SPEC COMPLETE |
| DP Economy | 4 DP/turn (France), use-or-lose. Per-nation formula (§4a) | Low | SPEC COMPLETE |
| AI Proposals | AI proposes when losing, stalemate, opportunistic. Anti-spam cooldowns | Medium | SPEC COMPLETE |
| Vassal System | Passive loyalty (garrison+autonomy+investment). Multi-vassal viable | Medium | SPEC COMPLETE |
| Talleyrand Defiance | 2% Schemer floor, 30% hard cap. Sabotage during transit | Medium | SPEC COMPLETE |
| Treaty System | 13 clause types including unit swaps, AP reparation tier | Medium | SPEC COMPLETE |
| Diplomatic Ledger UI | D key, 4 tabs: Nations, Treaties, Threat, Talleyrand Status | Medium | SPEC COMPLETE |
| **Diplomacy Chat** | LLM-powered conversations with nation leaders | High | Planned |
| **Leader Personalities** | Distinct voices (see table below) | Medium | Planned |
| **Coalition System** | Threat-from-success, 3-tier formation (murmurs/brewing/declaration), coalition structure (leader sets posture), coalition AI (convergence bias, friction), breaking (separate peace, decisive victory, diplomatic wedge), dissolution (cooldown) | Medium | **SPEC v1.1 APPROVED** — `COALITION_SPEC.md`. Master-audited. ~55 tests (Session 7). |

**Note:** Coalition moved here from Phase 7b — threat calculation, warning periods, and coalition formation only make sense alongside peace treaties and nation relations.

### Phase 8 Unified Session Plan

| Session | Name | Key Features | Estimated Tests | Complexity |
|---------|------|--------------|-----------------|------------|
| **1A** | Map Expansion | 13→19 regions, adjacency, region data migration | ~30 | HIGH |
| **1B** | Nations + Marshals + Economy | Austria, Saxony, 4 new marshals, starting economy | ~30 | HIGH |
| **2** | Diplomatic States + Acceptance Formula | State transitions, acceptance formula, war score, DP | ~60 | MEDIUM |
| **3** | Talleyrand Commands + Dialogue | Proposal flow, dialogue state machine, 10 templates | ~55 | HIGH |
| **4** | AI Proposals + Advisory | AI diplomatic phase, counter-offers, advisory conversations | ~40 | HIGH |
| **5** | Vassal System + Treaty Clauses | Loyalty, tribute, rebellion, carving, Continental System | ~45 | MEDIUM |
| **6** | Talleyrand Defiance + Objections | Sabotage, discovery, diplomatic confrontation | ~50 | MEDIUM |
| **7** | Coalition System (NEW) | Formation, structure, AI, breaking, dissolution, British subsidy | ~55 | HIGH |
| **8A** | Backend Ledger + Debug Arsenal | diplomatic_ledger.py, GET /diplomatic_ledger, 10 cheat commands, 8 debug endpoints, pass-throughs | **82** | **COMPLETE** |
| **8B** | Diplomatic Ledger UI + Top Bar | 4-tab Godot ledger (D key), top bar (DP/threat/Talleyrand/envoy), Dispatch→R key | **30** | **COMPLETE** |
| **8C** | Popups + Notifications | 11 notification constants, 18 fire points, 6 popup data contracts, 3 new world_state fields, 6 Godot popup scenes, priority queue | **31** | **COMPLETE** |
| **8D** | Dispatch + Polish + Deferred | ~20 dispatch event types, campaign log, fog filtering, AI-AI diplomacy, special acceptance bonuses | ~50 | MEDIUM |

**Total estimated tests: ~525.** Critical path: Sessions 1A/1B (HIGH RISK) → 2 → 3/4 → 5 → 6 → 7 → 8A → 8B/8C → 8D. Session 8 expanded to 4 sub-sessions per `docs/SESSION_8_PLAN.md`.

### Post-Phase 8 Refinement Order

**(July 2, 2026: items 1–4 below ALL LANDED** — Memory and Pressure v2.4.3 complete; BPH landed; WPS landed; War Bargains landed April 2026; Ally Participation + Common Peace landed as the Imperial Settlement system through Slice G1. Item 5's tracks route through 8.EVAL and the new EC/CR phases. Kept as the historical sequencing record.)

1. `Memory and Pressure`
   First diplomacy follow-up implementation target. Keep this bilateral and legible. Current canonical docs are `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3, `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` v2.4.3, `docs/COMMITMENTS_PRESENTATION_SPEC.md` v0.5.2, and `docs/DIPLOMAT_VOICE_BIBLE.md` v1.2. Audit-block sequence: Block 1 doc cleanup (complete), Block 2 substrate fixes (complete), Block 3 bloc naming (SUPERSEDED — folded back into §8.1a + voice bible + parent slices). Remaining implementation slices open directly.
2. `Bilateral Peace Hardening`
   Tighten separate peace, bilateral peace preview, term ownership, and promise-breach warnings before any multilateral settlement work.
3. `War Purpose + Score Semantics`
   Define war objectives, ticking score meaning, and settlement legitimacy at the bilateral/system layer.
3.5. `War Bargains` — `docs/WAR_BARGAIN_SPEC.md`
   The named-enemy bilateral promise mechanic split out of `Reliability + Commitments` v1.0 in the April 16 rescope. Depends on items 1-3; implementable as a Peace Deals phase precursor before item 4.
4. `Ally Participation + Common Peace` — `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
   Full-Europe wartime settlement flow: ally beneficiaries, contribution standing, common peace routing, and settlement fallout. Do not overload the normal nation -> proposal -> terms wizard with conference logic. Coding starts from `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.18 against spec v1.21, beginning with the A1 foundation gate before any A2/B/C/D behavior. Future nations enter this system one by one through `docs/ADDING_CONTENT.md` plus a settlement readiness fixture, not through settlement-specific hard-coding.
5. Remaining diplomacy follow-ups
   Agendas, Talleyrand explanation layers, and economic diplomacy all remain spec-gated behind the earlier items.

Reference planning docs:

- `docs/STATUS.md`
- `docs/DESIGN_REFINEMENT.md`
- `docs/RELIABILITY_COMMITMENTS_SPEC.md`
- `docs/WAR_BARGAIN_SPEC.md`
- `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`

### Post-Diplomacy Command Layer Queue

**PROMOTED July 2, 2026 → the Command Robustness phase (`docs/COMMAND_ROBUSTNESS_SPEC.md`).** The gating condition ("once the diplomacy refinement queue above is stable") was met; each row below maps to a CR slice in that spec (which is now the owner). The table is kept as the design-intent record.

| Item | Description | Status |
|------|-------------|--------|
| **Personality-Biased Disambiguation** | Same ambiguous order, different results based on who you're talking to. "Ney, deal with Wellington" → attack (Aggressive). "Davout, deal with Wellington" → hold/scout (Cautious). Literal marshals → ask for clarification. LLM parses THROUGH the marshal's personality lens instead of neutrally. Zero additional LLM calls — same parse call with personality-aware system prompt. **Within golden rule** (parsing determines action; executor stays deterministic). This is the game's signature LLM innovation: no other strategy game has personality-filtered command interpretation. Mock-safe: keyword parser falls back to neutral (ask) disambiguation. *(Player-visible = the three-way aggressive→attack / cautious→scout / literal→ask split; Soult was reassigned cautious→literal at the July 5 gate so the literal arm is player-reachable. The dramatic literal continue-into-disaster beat remains gated behind the autonomous Grouchy Moment.)* | ✅ **SCOPE BLESSED July 5, 2026 → CR-5** (`COMMAND_ROBUSTNESS_SPEC.md` §6; blessed scope incl. authored verb table + guardrails) |
| **Conversational Objection Negotiation** | Marshal objects → player argues back in natural language instead of clicking Insist/Trust/Compromise. LLM evaluates whether the player's argument addresses the marshal's stated concern using real game state. Cogent argument → resolves as Trust with +2 trust bonus. Poor argument → resolves as Insist. Mock mode: three buttons remain as fallback. **Pushes golden rule safely** — LLM classifies player response into one of three existing deterministic resolution buckets, not new outcomes. ~$0.0002/objection (Haiku). Cross-ref: Phase 8.5 Novel LLM Applications. | **NEEDS SPEC — design gate required (LLM affects trust outcome bucket)** |
| **Conditional and Compound Orders** | "If they retreat, pursue. Otherwise hold." / "Ney and Davout, pincer from Belgium and Holland." LLM extracts conditional logic and multi-marshal coordination that the keyword parser can't handle. Conditionals become reactive triggers in the strategic order system. Compound orders could grant a planning coherence bonus. Mock-safe: keyword parser handles simple orders; complex ones get Berthier clarification. Depends on Standing Tactical Intent + Semantic Command History. | **NEEDS SPEC — after Standing Tactical Intent** |
| **Persistent Command Focus** | Keep the current addressee/context active until the player changes it, so follow-ups like `attack`, `again`, `same target`, or `not you, Davout` become first-class commands instead of raw history recall. | **NEEDS SPEC** |
| **Standing Tactical Intent** | Let the player express ongoing battlefield intent (`keep pressure on Wellington`, `hold unless outnumbered`, `bombard until the fort breaks`) so repetitive re-entry of the same order is reduced without flattening marshal personality. | **NEEDS SPEC** |
| **Semantic Command History** | Track last marshal/action/target/interpretation, not just raw strings, so the parser and UI can understand follow-up intent rather than treating every line as a fresh utterance. | **NEEDS SPEC** |
| **Command Surface Shortcuts** | Add lightweight follow-up affordances after results (`Repeat`, `Pursue`, `Fortify`, `Scout`, `Ask Berthier`, `Switch Marshal`) while preserving typed commands as the power-user path. | **NEEDS SPEC** |
| **Map-Driven Command Context** | Clicking a marshal should set focus and clicking a region should prefill a target/context, turning the map into a command helper instead of leaving the text box as the only steering surface. | **NEEDS SPEC** |
| **Military Follow-Up Parsing Guardrails** | Keep deterministic mechanics and use LLM/context handling for echoing, disambiguation, and conversational follow-ups rather than making combat bonuses depend on ornate phrasing. | **NEEDS SPEC** |

### Diplomacy Chat Architecture

Player types natural language proposals. LLM generates leader response in-character. Rules engine resolves outcome deterministically. LLM narrates the result.

```
Player: "I offer Austria peace if they cede Tyrol"
  -> LLM generates Metternich's response (in-character)
  -> Rules engine: war score + relations + territory value -> accept/reject/counter
  -> LLM voices outcome: "Metternich smiles thinly..."
```

**Cost control:**
- 2 LLM calls per exchange (response + outcome narration)
- Last 3-4 exchanges as context only (prevents token creep)
- Max 3 diplomatic exchanges per turn (prevents cost abuse)
- Template fallback if LLM unavailable
- ~$0.0004-0.0008 per exchange (Haiku)

**Leader Personalities (per leader, not per nation):**

| Leader | Nation | Personality | Voice |
|--------|--------|-------------|-------|
| Metternich | Austria | Scheming | Calculating, poison-pill deals, never says what he means |
| Tsar Alexander | Russia | Idealistic | Grand gestures, emotional, unpredictable pivots |
| Frederick William | Prussia | Cautious | Deferential, follows strongest ally, hedges |
| Castlereagh | Britain | Pragmatic | Subsidy offers, cold cost-benefit, funds coalitions |

**Dependencies:** Phase 6 (economy for peace terms), Phase 7 (coordination for diplomatic context)
**Exit Criteria:** Can negotiate peace, AI diplomacy feels alive, leaders have distinct voices, coalition trigger functional

---

## Phase 8.5: Events, Goals & National Identity

**Goal:** Campaigns have narrative, nations feel distinct, player has objectives beyond "conquer."

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| **Events System** | Random + historical events with choices | High | Planned |
| **National Goals** | "Unite Germany", "Continental System" | Medium | Planned |
| **National Flavor** | France FEELS different from Austria | Medium | Planned |
| **Light Tech/Reforms** | Simple upgrades: conscription, tactics, administration | Medium | Planned |
| **Campaign Objectives** | Victory conditions beyond territory (prestige, survival) | Medium | Planned |
| **Battle History Screen** | Detailed past-battle viewer (ledger sub-tab or standalone). Full modifier breakdowns including coordination stats (combined arms %, per-ally %, dedicated %, adjacent %, total). Replaces coordination data removed from Berthier's Report modifier snapshots in Gate 4. | Low | Planned |
| Historical Moments | Coronation, Tilsit, Retreat from Moscow | Medium | Planned |
| **Imperial Governance Events** | Marshal-as-governor events, personality-driven regional outcomes. See `FUTURE_DESIGN.md`. | Medium | Planned |
| **Gazette System** | Period newspaper every 3-5 turns, LLM-generated | Medium | Planned |
| **Marshal Voice (Tier 1)** | Template personality responses for all events | Low | Planned |
| **Marshal Voice (Tier 2)** | LLM personality for high-drama moments | Medium | Planned |
| **Music & Sound (Core)** | Battle drums, march, tension, ambient | Medium | Planned |
| **Grouchy Moment LLM** | LLM narrates Grouchy's inner monologue when ignoring cannon fire | Low | Planned |
| **Intercepted Dispatches** | Scout results as captured enemy letters | Low | Planned |
| **Marshal Memory** | Similar situation recurs -> marshal references last time | Low | Planned |
| **Napoleon's Desk** | Turn-start LLM briefing from chief of staff | Low | Planned |
| **Command Echoing** | Combat reports reference player's original phrasing | Low | Planned |
| **Napoleon Comparison** | Post-game: compare your campaign to real Napoleon | Low | Planned |

### Gazette System ("Le Moniteur")

Every 3-5 turns, generate a period newspaper summarizing recent events via single LLM call.

**Content:** Battles, territory changes, marshal heroics, tension/foreshadowing.
**Bias:** Written from French perspective. Post-EA: multiple nation perspectives.
**Trigger:** Every 5 turns by default. Force on: major battle, territory loss, marshal death.
**Cost:** ~$0.0005 per gazette (~$0.005 per 40-turn game)

### Marshal Voice System (Tiered)

**Tier 1 -- Templates (free, always-on):**
- 3-5 personality-specific variants per event type
- File: `backend/ai/marshal_voice.py`

**Tier 2 -- LLM Drama (default for high-stakes moments):**
- Triggers: objections, combat results, cannon fire, forced retreat
- 200-token prompt budget, 1-2 sentences in-character
- Cache by (marshal, event_type, outcome)
- Fallback to Tier 1 if LLM fails
- Cost: ~$0.001-0.003/turn

**Tier 3 -- Full Flavor (opt-in toggle, see Pre-EA):**
- ALL commands get LLM personality response
- ~$0.0004/command extra, warned in UI

### Novel LLM Applications

| Feature | Description | Trigger |
|---------|-------------|---------|
| **Grouchy Moment LLM** | "The marshal frowns. The sound of battle echoes from the west. His orders are clear. He continues east." | Cannon fire interrupt + literal personality |
| **Intercepted Dispatches** | "My dear Castlereagh, I have positioned sixty-eight thousand at Waterloo..." | Scout action result |
| **Marshal Memory** | "The last time you ordered me to attack fortified positions, we lost 12,000 men." | Similar situation recurs |
| **Napoleon's Desk** | "Sire, Davout reports the enemy fortifying Belgium. Ney requests permission to attack." | Turn start |
| **Command Echoing** | Player typed "unleash hell" -> "Ney unleashed hell on Wellington's lines — 12,000 casualties." | Combat report |
| **Autonomy Inner Monologue** | "Ney sees the gap and cannot resist" | Autonomous marshal acts |
| **LLM Objection Arguments** | Objection references real game state | Objection popup (Tier 2) |
| **Conversational Objection Negotiation** | Marshal objects → player argues back in NL → LLM evaluates whether the argument addresses the marshal's concern using real game state → resolves into existing Insist/Trust/Compromise bucket with trust modifier. The game's "talk to your generals" fantasy fully realized. Cross-ref: Post-Diplomacy Command Layer Queue. **Needs design gate.** | Objection popup (replaces 3-button flow for LLM-on players) |
| **Personality-Biased Parsing** | Same ambiguous order → different action based on marshal personality. "Deal with Wellington" → attack (Aggressive), scout (Cautious), clarify (Literal). Zero extra LLM calls — system prompt change. Cross-ref: Post-Diplomacy Command Layer Queue. **Can prototype early.** | Every ambiguous command parse |
| **Napoleon Comparison** | "You lasted 47 turns. Napoleon lasted 120 months. Your coalition formed on turn 12; historically, the Third Coalition formed in 1805." | Post-game screen |

### Diplomatic LLM Features (Memory and Pressure era — added April 16 creative audit)

These hook into the Memory and Pressure substrate (betrayal memory, rivalries, named diplomats, `episode_id` lineage) and the Voice Bible cast. All Haiku, all mock-safe, ~$0.003/game total.

| Feature | Description | Trigger | Cost/game |
|---------|-------------|---------|-----------|
| **Betrayal Memory Voice** | When a nation rejects a proposal due to bilateral strikes, the named diplomat voices *why* in their register (Hawk accusation, Schemer calculation, Dove lament). Uses `bilateral_betrayal_mod` + Voice Bible register. | Proposal rejection where `bilateral_betrayal_mod < -8` | ~$0.0005 |
| **Rival Pressure Rationale** | When deepening with Nation A angers rival Nation B, B's named diplomat explains the rivalry concern in the `warnings[]` preview. Transforms "-12 rivalry mod" into Metternich's words. | Proposal preview where `rival_conflict_mod < -4` | ~$0.0004 |
| **Make Amends Response** | When France successfully executes Make Amends (§8.6.1), the target's named diplomat acknowledges the gesture in their register — grudging Hawk acceptance vs relieved Dove gratitude. | `_execute_make_amends()` success | ~$0.0009 |
| **Strategic Order Narration** | When a marshal executes a strategic order autonomously, narrate their inner first-person moment. Extends "talk to generals" to "hear them think." | Strategic order execution where `actor != player_commanded` | ~$0.0008 |
| **Inter-Turn Moment Snapshots** | Once per 3-5 turns, a named voice (diplomat or marshal) delivers one private evocative line in the Morning Dispatch. Threads personality through quiet turns. | Turn-end dispatch, personality-random trigger | ~$0.0008 |

### LLM Mechanical Expansion Path (design gate — not Phase 8.5 scope)

The golden rule is "LLM never affects mechanics — parsing only, executor is deterministic" (CLAUDE.md). Three expansions stay within the rule while giving LLM a mechanical-adjacent role:

1. **Diplomatic quality preview (advisory, not input).** LLM reads game state + betrayal memory + rivalry data and generates a natural-language "strategic situation briefing" richer than the raw ledger. Talleyrand says "I estimate Metternich will find this 60% acceptable" — that's player advisory, not formula input. The executor ignores it; the deterministic acceptance formula remains authoritative. Mock-safe: template fallback uses `warnings[]` text directly.

2. **Strategic_score → authority bonus (carrot path).** The existing `strategic_score` from creative-phrasing evaluation (see "Encouraging Creative Commands" below) is currently display-only. A future design could gate a small constant authority bonus (+1) on `strategic_score > threshold` per game. This makes LLM availability affect outcomes — **requires a dedicated design gate** before implementation. Mock mode must provide a default passing score so LLM-off players aren't penalized.

3. **AI proposal coherence filter.** LLM evaluates AI-generated proposals for historical plausibility before surfacing them. This IS mechanical (filtering bad proposals) but can be framed as "Talleyrand reviewing his own work before presenting it to the Emperor." Mock-safe: without LLM, proposals pass unfiltered (current behavior). With LLM, proposals that read as historically implausible get re-rolled. Low priority but high immersion upside.

These are **design-gated** — do not implement any as part of Phase 8.5 without a dedicated spec. The golden rule must be explicitly amended by a design gate, not silently stretched.

### Encouraging Creative Commands (Anti-Memorization)

These ideas are downstream of the post-diplomacy command-layer queue above. Do not ship phrasing bonuses/penalties before `Persistent Command Focus`, `Standing Tactical Intent`, and `Semantic Command History` are specified. **Exception:** `Personality-Biased Disambiguation` can prototype earlier — it is a system-prompt change to the existing parse call, not a new command-surface feature.

| Feature | Description |
|---------|-------------|
| **Flavor Echoing** | Marshal voice echoes player's words. HIGHEST PRIORITY — signals "the game heard me." |
| **Synonym Bonus** | LLM detects creative phrasing, boosts strategic_score |
| **Command Suggestions** | Occasionally offer alternatives: "Instead of 'attack,' try 'storm the heights'" |
| **Repetition Penalty** | Same phrasing 5+ times in a row lowers strategic_score. Subtle, not punishing. |
| **"Napoleon's Wit" Bonus** | LLM scores commands for historical flair |
| **Command Variety Tracker** | Milestone rewards: "Your marshals admire your eloquence" (+authority) |

**Key insight:** Carrot, not stick. "attack wellington" always works perfectly. Creative phrasing earns bonuses.

### Positive Events

| Event | Trigger | Effect |
|-------|---------|--------|
| **Victory celebration** | Decisive victory (>2:1 ratio) | +5 morale nearby |
| **Momentum** | Win 2+ battles same turn | +10 morale army-wide |
| **Rallying speech** | Morale recovers past 60 from below 40 | Trust +3 |
| **Captured supplies** | Conquer high-income region | Gold bonus |
| **Vindication narrative** | Marshal proven right | Trust +8, "Davout was right!" |
| **Rivalry resolved** | Rival marshals fight together | Trust boost for both |

**Dependencies:** Phase 8 (diplomacy for event outcomes)
**Exit Criteria:** Each campaign tells a story, nations play differently, marshals have voice, gazette provides rhythm

---

## STEAM PAGE + LLC

**After Phase 8.5.** Marshal voice, gazette, audio, and EU4-style map all working. This is when the game is trailerworthy.

- Commission trailer showing command typing + objection popup + map
- Set up LLC for business entity
- Steam page with screenshots using commissioned Europe map
- Begin wishlist accumulation — every month without a page is lost wishlists
- Work with Claude Chat on store page copy, descriptions, tags

---

## Phase 9: Advisors (Minimal)

**Goal:** Empire feels run by people. Advisors provide stats + flavor, not action gating.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Advisor Characters | Named characters per domain (Talleyrand, Berthier, Treasurer) | Low | Planned |
| Passive Stat Bonuses | Each advisor has 2-3 stats boosting their domain | Low | Planned |
| Named Voices | Advisors narrate their domain's screens in-character | Medium | Planned |
| Advisor Death/Replacement | Events can remove advisors, replacement has trade-offs | Low | Planned |
| **National Identity** | Austria starts with Metternich (diplomacy god), Prussia with Scharnhorst (military reform) | Low | Planned |

### Advisor Design (Minimal EA Version)

Advisors exist as **named voices on information screens** with **passive stat bonuses**. They don't gate actions, don't have trust, don't refuse orders.

Example: Metternich as Austria's advisor gives Diplomacy +2 (better peace terms, slower coalition formation). If he dies or is dismissed, Austria loses the bonus. Recruiting a replacement is a choice: "The new diplomat is cautious — +1 diplomacy but -1 military spending."

**Post-EA promotion:** Advisors gain action gating, trust relationships, dismissal consequences (the full VISION Layer 1). But for EA, they're personality lenses on information with stat bonuses.

**Dependencies:** Phase 8 (diplomacy for advisor context)
**Exit Criteria:** Advisors feel like people running an empire, stats affect outcomes

---

## Phase 10: Character & People (Minimal)

**Goal:** Marshals feel like people who live, die, and can be replaced. If all marshals die, you lose.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Marshal Death | Casualties in battle (% chance per major defeat) | Medium | Planned |
| Marshal Pool | Historical marshals waiting activation | Low | Planned |
| Recruit Marshals | Activate from pool (costs gold + manpower) | Low | ✅ **LANDED July 11, 2026** — `MARSHAL_RECRUITMENT_SPEC.md` (the Marshalate: authored `marshal_pool`, shared executor, AI commission rung) |
| All-Dead Loss | If all marshals die, game over | Low | Planned |

### ~~Evaluate Adding New Personality Type Before 1805~~ — ✅ DECIDED July 10, 2026 (MC-4)

The condition arrived at the Marshal Content Pass and the evaluation ran at its gate: **do NOT implement Loyal or Balanced** — the deferral closed as a Golden Rule 9 contract (`MARSHAL_CONTENT_PASS_SPEC.md` §9): both are retired reserved values, boot-guarded against authoring; the missing archetypes are expressed cheaper via trust + the MC-3 relationship web + abilities (Bernadotte's unreliability = trust 40 + negative edges + Eyes on a Crown). Re-open owners: the Jealousy v3.1 gate or the MC exit review; a revived fourth type must not be named "loyal" (diplomat `loyalist` namespace collision).

**Deferred from EA:** LLM-generated marshals (when pool empty), acquired traits system.

**Dependencies:** Phase 6 (economy for recruitment costs)
**Exit Criteria:** Marshals can die, player can recruit replacements, total death = loss

---

## Phase 11: Vassals & Britain

**Goal:** Client states work, France's empire makes geographic sense, and Britain threatens through subsidies/naval pressure once the relevant map and movement rules exist.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| **Simplified Vassals** | Conquered nations become vassals with loyalty number | Medium | Planned |
| Vassal Troops | Vassals contribute troops automatically | Low | Planned |
| Vassal Defection | If coalition threat > loyalty, vassal defects | Medium | Planned |
| **Authority -> Loyalty** | Napoleon's authority affects all vassal loyalty (1813 snowball) | Low | Planned |
| **Imperial Governance → Vassals** | Marshals installed as permanent rulers of conquered territory. Trust/personality determines loyalty. See `FUTURE_DESIGN.md`. | Medium | Planned |
| **Britain Naval/Subsidy Pressure** | Britain as funder: subsidy pool, expeditionary forces, Channel/naval access abstraction when the map supports it | Medium | Planned |
| Continental System | Player action to reduce British income/subsidies | Low | Planned |

### Simplified Vassal System

No autonomy slider, no vassal management UI. Just: "Bavaria is your vassal (loyalty 72). They provide 15,000 troops. If coalition threat exceeds their loyalty, they defect."

Authority drop -> vassals waver -> defect in next coalition -> lose their troops AND territory becomes hostile -> more enemies -> more authority loss. The 1813-1814 death spiral in game mechanics. Inverse: high authority -> loyal vassals -> coalition can't peel them away.

### Britain as Naval/Subsidy Power

Britain has a subsidy pool that grows from colonial income. When coalition forms, Britain funds it. If the map/naval abstraction supports it, Britain can project Wellington + troops through coastal or island-access rules.

To beat Britain: exhaust their willingness to fund coalitions (war score / diplomacy) or make Continental System work (reduce income). Historically accurate for most of the Napoleonic Wars.

**Naval abstraction is separate from Imperial Settlement A1** and should be designed when Britain/water reachability becomes a map problem.

**Dependencies:** Phase 8 (coalition trigger + diplomacy for vassal creation)
**Exit Criteria:** France has client states, vassals can defect, Britain funds enemies

---

## Pre-EA Polish

**Goal:** Game is shippable, onboardable, monetizable.

**Tutorial policy:** TUTORIAL_SCRIPT.md is updated every phase (3-5 rows per feature). `TutorialManager` infrastructure + Short Waterloo Scenario scripting happens here, built against stable Map Renderer scene tree + final mechanics. See TUTORIAL_SCRIPT.md "Update Policy" section.

| Feature | Description | Complexity | Status |
|---------|-------------|------------|--------|
| Tutorial System + Content | Build `TutorialManager` (deferred from Phase 6.5) + populate from TUTORIAL_SCRIPT.md. Build against stable Map Renderer scene tree. | Medium | Planned |
| **LLM Monetization** | BYOK + token tiers + payment | High | CRITICAL |
| **LLM Feature Toggles** | Per-feature model/on-off selection in settings | Low | Planned |
| At-will Autonomy | Grant autonomy anytime (gold-gated, one admin slot) | Low | Planned |
| At-will Administrator | Sideline marshal for +1 AP (gold-gated) | Low | Planned |
| Increase Salary | Gold -> Trust conversion | Low | Planned |
| Modding Polish | Finish tools, docs, examples | Low | Nearly done |
| LLM Efficiency | Caching, optimization | Medium | Planned |
| Settings Menu | Audio, display, controls, LLM settings | Low | Planned |
| Steam Integration | Achievements, cloud saves | Medium | Planned |
| **Music & Sound (Polish)** | Full period orchestral, per-nation themes | Medium | Planned |
| Difficulty Settings | AI bonuses, player handicaps | Low | Planned |
| **Full Flavor Toggle** | Tier 3 marshal voice (opt-in with cost warning) | Low | Planned |
| **LLM Cost Display** | Per-feature token usage in settings | Low | Planned |
| **Voice-to-Text** | Speak orders naturally — feeds into existing parser pipeline | Medium | Planned |
| **Short Waterloo Scenario** | 10-15 turn tutorial scenario, 3 marshals, reuse current 19-region data | Medium | Planned |

### LLM Settings UI

```
LLM Features          Model       Status
---------------------------------------------
Command Parsing       Haiku       [ON]
Marshal Voice         Haiku       [ON]
Gazette              Sonnet       [ON] (recommended)
Diplomacy Chat       Sonnet       [ON] (recommended)
Battle Narration     Haiku        [OFF]
Full Flavor Mode     Haiku        [OFF]

Estimated cost/game: ~$0.05
```

Power users tune per-feature, casual players use defaults.

### Voice-to-Text

Killer feature for the "talk to your marshals" fantasy. Player speaks commands, speech-to-text converts to text, text feeds into existing parser pipeline unchanged. The parser already handles natural language — voice is just a new input method.

**Architecture:** Godot `AudioStreamPlayer` captures mic -> send audio to Whisper API (or browser Speech-to-Text API) -> insert transcribed text into command input -> submit through normal parser. Backend is unaware of voice vs typed input.

**Cost:** Whisper API ~$0.006/minute. Average command ~3-5 seconds = ~$0.0003/command. 40 commands/game = ~$0.012/game. Negligible. Alternatively, browser-native `SpeechRecognition` API is free but less accurate.

**Fallback:** Always show text input. Voice is additive, never required. Toggle in settings.

**Dependencies:** All phases complete

**Exit Criteria:** New players learn, payments work, game feels alive

---

## 1805 Campaign Launch (Early Access)

**Goal:** Option C — commission full Europe map, wire partial regions, expand over EA updates.

**Scale-readiness scope lock:** The current France-led 1805 draft scenario uses the 13-nation DG-1 roster from `docs/SCALE_READINESS_PLAN.md`, but that is not an engine cap. EA geography may still wire regions in stages, and larger maps / later scenarios may author more nations as needed.

| Feature | Description | Complexity | Notes |
|---------|-------------|------------|-------|
| **~80-100 Wired Regions** | Western/Central Europe playable | Medium | Data entry + balance |
| **EU4-Style Bitmap Map** | Province color map, visual overlay | Integrated in 6.5 | Commissioned art |
| Map Interaction | Click provinces, zoom, pan | Integrated in 6.5 | |
| **Scenario-authored Nation Roster** | Current 1805 draft: France, Britain, Austria, Prussia, Russia, Spain, Ottoman Empire, Sweden, Naples/Two Sicilies, Bavaria, Saxony, Portugal, Denmark-Norway | HIGH | Scenario data + balance. The draft roster is 13 nations today, but the map / engine are not capped there. |
| 20+ Marshals | Historical personalities per nation | Medium | Data entry |
| **1805-accurate Diplomats** | Swap recognizable-but-post-1805 diplomats (Hardenberg / Metternich / Castlereagh / Einsiedel) for the historically-accurate 1805 ministers (Haugwitz / Stadion / Mulgrave / Bose). Voice Bible port of existing register notes. See `DESIGN_REFINEMENT.md` §P1. | Low | Period fidelity upgrade; deferred from Memory and Pressure v0.1 |
| Year-Based Turns | Monthly 1805-1815 | Low | |
| Optional 1805 Objectives | Scenario-authored goals if a later build wants them; no hard victory required for the base sandbox | Low | Deferred |
| **Greyed-Out Expansion** | Remaining 40-70 provinces visible but non-interactive | Low | Visual promise |
| **AI Fog of War** | AI gets fog (softer than player's) at 80+ regions | Medium | Omniscient AI unfair at scale. Toggle point: `get_visible_enemies_near()` |

### Economy Rebalance for 1805

**OWNED July 2, 2026 by `docs/ECONOMY_REVISIT_SPEC.md`** (this section is its historical design rationale; the 1805-scale numbers there supersede the legacy figures below — France measured ~3.4k gold/turn on 28 provinces at Slice 8).

The 19-region map has known balance tensions surfaced by Session 26 Opus audit:
- **Admin AP bonus (150g) is disproportionately important** — 9-43% of a nation's income. Creates strong disincentive for Coalition AI to recruit/build.
- **Coalition death spiral** — battle losses → recruitment needs → lost admin bonus → deficit → bankruptcy → desertion → more losses.
- **France cannot go bankrupt** under normal play (+85 to +235/turn). Bankruptcy is Coalition-only.
- **Buildings expensive for Coalition** — a 350g market is 44% of Prussia's starting gold.

These are acceptable for the tutorial scenario (France should feel dominant). For the France-led 1805 prototype at 80+ regions and a multi-nation Europe roster:
- Income sources will be more numerous and distributed
- Admin AP bonus should scale differently (flat 150g matters less with 2000g income)
- Building costs may need scaling by era or nation
- British subsidy / expeditionary pressure may still be needed
- Upkeep rate (5g/1000 troops) should be re-evaluated against 1805 army sizes

### AI Fog of War for 1805

**RESOLVED (April 19, 2026):** Scale Readiness Phase 2.3 landed the live nation-perspective fog seam (`enemy_ai.py` fog-aware queries); the shipped 126-province campaign runs with AI fog live. Residual open idea: AI difficulty tiers/compensation (needs its own spec — see ARCHITECTURE_REFACTORING_PLAN Phase F supersession note). Historical rationale below.

At 19 regions, AI omniscience is fine — too few regions for fog to matter strategically. At 80+ regions, omniscient AI feels unfair (it always knows where you are, you never know where it is). Options to evaluate:
- AI gets fog but with bonuses (wider adjacency range, faster intel updates)
- AI fog is "softer" — PARTIAL everywhere instead of UNKNOWN
- AI uses watchtowers and scouts like the player but with priority logic already built

The practical Phase 2 seam is a nation-perspective **live** visibility helper for AI decision-making, not a serialized per-nation intel store. The older `get_visible_enemies_near()` note was directionally right about the toggle point, but the current implementation target is narrower: switch scale-sensitive AI queries onto live fog-filtered contacts first, then revisit deeper AI-side intel/history later if Europe playtests need it. The 12 objection helper TODO markers (V2b) also apply here since AI nations' marshals would need fog-aware objection triggers.

### Executor Refactoring for 1805

**LANDED (R10A/B–R13A/B decomposition):** executor.py is ~1.5k lines with 8 sub-executors (see CLAUDE.md file table); this section is historical. Residual shared-helper items, if any, route through 8.EVAL. Historical scope below:
- **Executor decomposition:** Extract `_execute_debug` (~867 lines) and `_process_dialogue_choice` (~1,098 lines) out of executor.py. Resolves 125 inline imports / circular deps.
- **Shared helpers:** Extract duplicated recruit cost formula (3 locations), drill check helper (3 locations), auto-end-turn logic. Replace 43 hand-rolled AI enemy queries with helper methods.
- **Risk:** HIGH for executor decomposition (circular deps), MEDIUM for helpers (behavioral equivalence). Strong test suite (6,904+) makes verification practical.

See `docs/SYSTEMS_AUDIT_FIX_PLAN.md` Phase E for details.

### AP Scaling for 1805

Nation AP reflects bureaucratic capacity (see Phase 7 table). Additional: free basic actions for idle marshals (stance, wait), AP only for offensive actions. Strategic order conflict detection required.

### Option C Expansion Plan

EA v1: Western + Central Europe (~80 regions). EA updates add Eastern Europe, expand Russia, Ottoman interior. Each update = wire more provinces from existing art + add region data. No new art commissions needed.

**Dependencies:** All phases + Pre-EA complete, commissioned map art
**Exit Criteria:** Partial 1805 campaign playable, map looks professional

---

## Post-EA Expansion

| Feature | Priority | Notes |
|---------|----------|-------|
| **Full Europe (120+ regions)** | HIGH | Wire remaining provinces from existing art |
| Multi-Nation Play | HIGH | Play as Austria, Russia, etc. |
| Coalition Player | HIGH | Lead coalition against France |
| Additional Start Dates | HIGH | 1809, 1812, 1815 scenarios |
| **Naval Abstraction** | HIGH | Required when Britain becomes playable |
| **Britain Playable** | HIGH | Own provinces, naval mechanics, subsidy system |
| **Communication / Courier Delay** | MEDIUM | Distance-based turn lag, Napoleon's HQ location matters, player-only (Option A) |
| **Full Advisor System** | MEDIUM | Action gating, trust, dismissal (VISION Layer 1) |
| **North Africa / Egypt** | MEDIUM | Expansion map art, Egyptian campaign scenario |
| Weather System | MEDIUM | Russian winter, mud season |
| Campaign Editor | MEDIUM | Player-made scenarios |
| Steam Workshop | MEDIUM | Mod sharing |
| **Multi-Nation Battle Reports** | LOW | Thread player_nation from world state through combat resolver. Currently hardcoded to France. Tests document exact wiring point. |
| Accessibility | MEDIUM | Colorblind, fonts, keybinding |
| Mobile Port | LOW | Touch UI |
| Multiplayer | LOW | Co-op? Competitive? |

### Courier Delay (Post-EA Design)

Lighter version of communication cutoff: orders to distant marshals take effect 1 turn later. Within 3 regions of Napoleon: instant. 4-6 regions: 1 turn delay. 7+: 2 turns. Makes Napoleon's physical location matter. Player-only for EA; when other nations become playable, each gets own HQ anchor.

---

## Critical Path to EA

1. COMPLETE: Strategic Commands, Enemy AI, Serialization/Modding
2. COMPLETE: V2a Objection System Refactor (all 7 units)
3. Post-V2a: TUTORIAL_SCRIPT.md, doc updates
4. **Commission Europe map art** (2-4 week lead time, parallel with Phase 6)
5. Phase 6: Economy, Manpower, Terrain, Fog, **Save/Load**, **Berthier**, **Post-battle analysis**
6. Phase 6.5: Notifications, **Top Bar Framework + Dispatch** (Session A), **Strategic Ledger** (Session B), Marshal UI, ~~Campaign Briefing~~, ~~Marshal Report~~ (shipped as Morning Dispatch), ~~Tutorial infra~~ (deferred to Pre-EA), **Map Renderer**
7. Phase 7 Core: Multi-Marshal Coordination (Sessions 57-61a, 61b, 64 — 7 sessions, ~246 tests) — combined arms, coordination bonuses, Grouchy Rule, dynamic relationships
7b. Phase 7b: Casualty Distribution (S62), AI Coordination (S63), Battle Reports + Reinforcement Reporting (S65), Godot UI (S66), Tactical Triangle (S67-68), V2b, Jealousy
8. Phase 8: **Diplomacy** (11 sessions: Map Expansion, Nations, States+Formula, Talleyrand, AI Proposals, Vassals, Defiance, **Coalition**, Ledger Backend+Debug, Ledger UI+Top Bar, Popups+Notifications, Dispatch+Polish). ~525 tests. Session 8 expanded to 8A-8D per `SESSION_8_PLAN.md`.
8a. Peace Deals closure: Memory and Pressure, Bilateral Peace Hardening, War Purpose + Score Semantics, War Bargains, Ally Participation + Common Peace, Imperial Settlement Slice F UI/UX closure, Slice G AI/ally settlement agency, final smoke.
8b. **Pre-8.5 Evaluation Gate:** audit buried war-LLM improvement items and diplomacy-refinement items before starting 8.5. Inputs: `DESIGN_REFINEMENT.md`, LLM cost/toggle table, battle/war narration notes, creative-command war uses, AI ultimatums/trade/agenda/Talleyrand Desk candidates, and any future-design AI strategic depth notes. Output: keep/defer/drop list plus scoped handoff.
8c. **AI Strategic Depth:** Flanking coordination, capital defense, **AI-AI strategic intent** (opportunistic war declarations, vassalization of beaten AI opponents, cross-AI threat assessment). Infrastructure 95% nation-agnostic — needs decision-making layer only. See FUTURE_DESIGN.md "AI-AI Strategic Intent" section.
9. Phase 8.5: **Events, Gazette, Marshal Voice, Grouchy LLM, Intercepted Dispatches, Creative Commands, Napoleon Comparison**
10. **STEAM PAGE + LLC** (marshal voice, gazette, audio, EU4 map all working)
11. Phase 9: Advisors (minimal: stats + flavor + named voices)
12. Phase 10: Marshal death/recruitment (minimal)
13. Phase 11: Vassals (loyalty + authority), Britain (naval/subsidy pressure)
14. Pre-EA: Tutorial content, LLM monetization, **LLM feature toggles**, **Voice-to-Text**, **Waterloo scenario**, Steam integration
15. Wire ~80-100 regions from commissioned map, data entry, balance
16. **TBD 2026: Early Access**

---

## Phase Dependencies Graph

```
                    Commission Map Art (parallel)
                           |
Phase 6 (Economy/Terrain/Save) --+--> Phase 6.5 (UI/Info/Map Renderer)
                                 |          |
                                 |          +--> Phase 7 Core --> Phase 7b (Casualties + AI + Triangle + V2b)
                                 |                    |
                                 |                    +--> Phase 8 (Diplomacy/Peace)
                                 |                              |
                                 |                              +--> Phase 8.5 (Events/Voice/Gazette)
                                 |                                        |
                                 |                                  STEAM PAGE + LLC
                                 |                                        |
                                 +--> Phase 10 (Characters) ----+         |
                                                                |         v
Phase 8 (Diplomacy) --> Phase 11 (Vassals/Britain) ----+  Phase 9 (Advisors)
                                                       |         |
                                                       v         v
                                                  Pre-EA Polish
                                                       |
                                                  Wire Regions + Balance
                                                       |
                                                  EA Launch
```

---

## LLM Cost Budget (Per 40-Turn Game)

| System | Phase | Calls | Model | Cost | Toggleable |
|--------|-------|-------|-------|------|------------|
| Command parsing | 4 (existing) | ~40 LLM + ~360 free | Haiku | ~$0.016 | ON by default |
| Berthier parse recovery | 6 | ~5 failures | Haiku | ~$0.002 | ON by default |
| Marshal Voice Tier 2 | 8.5 | ~30-50 drama events | Haiku | ~$0.012-0.020 | ON by default |
| Gazette | 8.5 | ~8 gazettes | Sonnet (rec.) | ~$0.008 | ON by default |
| Diplomacy Chat | 8 | ~40-60 exchanges | Sonnet (rec.) | ~$0.016-0.024 | ON by default |
| Grouchy Moment / Dispatches | 8.5 | ~5-10 events | Haiku | ~$0.002-0.004 | ON by default |
| Napoleon's Desk briefing | 8.5 | ~40 turns | Haiku | ~$0.016 | OFF by default |
| **Total per game (defaults)** | | | | **~$0.07-0.09** | |
| Full Flavor Tier 3 (opt-in) | Pre-EA | +160 routine calls | Haiku | +$0.064 | OFF by default |

At 1000 games/month = ~$70-90. BYOK covers heavy users. All systems degrade gracefully to templates when LLM unavailable. Per-feature toggle in settings lets players control cost vs immersion.

---

## Document References

- **STATUS.md** -- Current test count, active work, blockers
- **SYSTEMS_REFERENCE.md** -- Game systems reference
- **ENEMY_AI_REFERENCE.md** -- Enemy AI decision tree
- **OBJECTION_V2.md** -- V2 objection system design
- **VISION.md** -- Core concept, north star
- **TUTORIAL_SCRIPT.md** -- Living tutorial content document (updated each phase)
- **FUTURE_DESIGN.md** -- Deferred concepts, post-EA designs

**Rule:** Phase numbers and timeline ONLY exist in this document. Other docs say "see ROADMAP.md".
