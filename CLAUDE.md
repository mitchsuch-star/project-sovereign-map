# CLAUDE.md

Napoleonic strategy game. Players type commands ("Marshal Ney, attack Wellington") and AI marshals respond based on personality. Godot 4 frontend, FastAPI backend on port 8005. For game vision see `docs/VISION.md`.

## Golden Rules

1. **Combat modifiers: SINGLE SOURCE in `marshal.py`** — `get_attack_modifier()` / `get_defense_modifier()` only. `combat.py` reads them, never recalculates.
2. **All numbers to Godot: `int()`** — Godot crashes on floats.
3. **All marshals in ONE dict:** `world.marshals` (not separate player/enemy).
4. **State clearing: AFTER reading** — get the value, use it, then clear.
5. **Enemy AI uses SAME executor as player** (Building Blocks principle — same systems, different input values. See `docs/SYSTEMS_REFERENCE.md` §23).
6. **LLM never affects mechanics** — parsing only, executor is deterministic.
7. **Port 8005** (not 8000!) — change in BOTH `backend/main.py` AND `godot-client/.../api_client.gd`.
8. **Scale-ready code: NO per-region scans in hot paths** — Map is scaling to full 1805 Europe. Never iterate `world.regions.values()` in loops called multiple times per turn. Use cached helpers (e.g. `get_active_nations()` is per-turn cached, `get_nation_regions()` for region lookups). If adding a new helper that scans regions, cache the result per-turn and invalidate via `invalidate_active_nations_cache()` pattern.
9. **No open-ended deferrals** — any hidden, cut, deferred, later, v2, or polish player-facing work must name a concrete owner row/spec, landing slice, completion definition, STATUS tracking line, and behavior test. If the work is not going to land, remove the player-facing promise explicitly. Do not leave "future work" labels, disabled placeholders, or vague backlog notes in active specs.

## Workflow: work directly on master

This is a single-developer project with pre-commit-hook test gating and Codex audits run by commit SHA. Branch-per-slice / worktree-per-slice creates state-drift bugs (the branch falls behind master between slices, the merge back is noisy, and the audit prompt still ends up referencing master after merge anyway). The workflow is intentionally single-threaded: one local master worktree, one active implementation path, and audit/fix follow-ups recorded by master commit SHA. The default is:

- **Commit directly to master.** No `claude/<slice-id>` feature branch, no worktree.
- **The pre-commit hook runs `ruff check backend/` + the full pytest suite.** If a commit is blocked, fix the underlying lint/test failures — do not bypass with `--no-verify`. The hook source is tracked at `scripts/git-hooks/pre-commit`; since `.git/hooks/` is not version-controlled, install it after a fresh clone with `cp scripts/git-hooks/pre-commit .git/hooks/pre-commit` (PowerShell: `Copy-Item scripts/git-hooks/pre-commit .git/hooks/pre-commit`).
- **Codex audits target master at the slice's commit SHA.** When emitting an audit prompt, write `Audit master at commit <SHA>...` rather than naming a feature branch. The audit prompt should also instruct Codex to verify any follow-up work continues on master.
- **If the harness spawns a worktree on a `claude/...` branch anyway:** finish the slice in the worktree (avoid mid-session churn), push branch-tip-to-master via `git push origin <branch>:master`, and add a note to the session summary recommending the user disable auto-worktree creation in their launcher.
- **Exception:** Use a feature branch only when the slice is genuinely throwaway/experimental and the user explicitly asks for one.

## Current Phase

**RE-STAGED July 2, 2026.** The real-map cutover is COMPLETE and Phase 8 (Diplomacy & Peace, incl. the full Imperial Settlement arc) is functionally complete. **Routing authority: `docs/ROADMAP.md` §Current Phase Queue + `docs/STATUS.md` Next Steps.** Phases 6, 6.5, 7 Core, 7b, 8 — COMPLETE (full session history in `docs/STATUS.md` + archives).

### The queue in one line

~~Gate 4 visual-half confirmation~~ (✅ PASSED July 3, 2026) → ~~Slice H gate + landing~~ (✅ LANDED July 3, 2026) → ~~**Command Robustness** CR-0..CR-5~~ (✅ COMPLETE July 3-7, 2026; `docs/COMMAND_ROBUSTNESS_SPEC.md`) → ~~**CR-5b (Flavor Echoing)**~~ (✅ LANDED July 7, 2026; entry gate CLEARED — non-parroting floor + register gate) → ~~**Comprehensive Codebase Audit correctness sweep**~~ (✅ COMPLETE July 9, 2026 — 7 fixes, 0 escalations, suite 11,789/1; `docs/audits/AUDIT_2026_07_09.md`) → ~~**Econ eval**~~ (✅ COMPLETE July 9, 2026 — memo `docs/audits/ECONOMY_ECON_EVAL_2026_07_09.md`; 23 verdicts feeding the EC-2 gate — headline dissents: ES-7 E5 constants scale-incoherent → full-income redirect; ES-3 promoted into pass 1 for the band's turn-1 anchor; ES-2 simplified to stability-tier occupation cost on non-homeland soil) → ~~**EC-2 USER DESIGN GATE**~~ (✅ BLESSED July 9, 2026 — memo §8 accepted in full; **gate record = `ECONOMY_REVISIT_SPEC.md` §0.6.7**, authoritative: ES-7 full-income redirect, ES-2 stability-tier occupation shape with zero new serialized fields, ES-3 promoted into pass 1, the endow triangle, blessed numbers E1–E6) → ~~**Economy Revisit BUILD**~~ (✅ **COMPLETE July 9, 2026 — EC pass 1 CLOSED**: Track 1 S1–S4 AND Track 2 S5 ES-3 → S6 ES-2 → S7 ES-7 ALL LANDED, stacked two-sided E1 band test green — landing notes `docs/ECONOMY_REVISIT_SPEC.md` §0.6.3 Track-2 block; **one user tuning flag: the E1 turn-1 anchor measured 36.9% vs the aspirational 55–70%, unreachable without breaking Austria's +18 boot solvency — spec S7 note**) → ~~**§8 creative/fun-factor capstone**~~ (✅ COMPLETE July 10, 2026 — memo `docs/audits/CREATIVE_AUDIT_2026_07_10.md`: live 5-turn anthropic-mode playtest + 2 evidence sweeps; pillar scores command 7.5 / marshal drama 6 / combat legibility 4.5 / **narration 3.5** / economy 6 / diplomacy 6.5 / aliveness 7.5; **10 routed defects → `BUG_FIXES.md` §Creative-Audit Findings — BUG-CA-7 dialogue-stack misroute = P1**; Wave 6 expansions EXP-N1..EXP-D1 + escalations E-CA-1..6 filed in `DESIGN_REFINEMENT.md`; 4 inline legibility fixes, `test_creative_audit_legibility_fixes_2026_07_10.py`) → ~~**Wave 6 Fun-Factor Build**~~ (✅ **COMPLETE July 10, 2026 — all 12 slices W6-0..W6-11 landed in order across two sessions** per `docs/WAVE6_FUN_FACTOR_SPEC.md` (§15 DoD recorded): every BUG-CA row FIXED; the score-raisers live-verified; **the §0 re-score addendum (memo §9) MEASURED all four target pillars MET — narration 3.5→7.5, combat legibility 4.5→7, incoming diplomacy 4→7, marshal drama 6→7.5**; second session landed W6-8 estate confiscation (`respected_estates`, confiscate/respect on the capture pipeline), W6-9 the assessment verb ("Talleyrand, assess our situation" → the war room + executable counsel; R117 landed), W6-10 incoming voice/variety/territorial honesty (diplomat_line register bank, 6-turn type cooldowns incl. lapse, P3 relation-band asks, settlement status-quo line), and W6-11 the balance duo (symmetric casualty-scaled morale both combat copies; war-priced recruitment ×3 + over-limit compose, Europe-scoped, GR5-priced AI) — blessed numbers remain in-band tunable, spec §14 ledger) → **▶ Marshal Content Pass gate — RUNS NEXT** (`docs/MARSHAL_CONTENT_PASS_SPEC.md`; needs USER design gate; the capstone AND the Wave-6 re-score both name roster content as the binding constraint — DO NOT CODE before approval, MC-0 exempt) → DEF-1 voices + DEF-13 UI scale → 8.EVAL → Phase 8.5.

### Load-bearing operational facts (1805 boot — keep verbatim)

- **THE RUNNING GAME IS THE 126-PROVINCE 1805 CAMPAIGN, frontend + backend** (cutover closed July 2, 2026; plan + deferred rows in `docs/MAP_IMPLEMENTATION_PLAN.md`).
- **Boot precedence:** explicit `SOVEREIGN_SCENARIO` (+ smoke preset = RAISE, never combine) → `SOVEREIGN_SCENARIO=none` sentinel = bare flag world (conftest pins it suite-wide) → `SOVEREIGN_MAP=legacy` = the 19-region rollback (drilled live; no code change) → preset alone → **default = `godot-client/project-sovereign/assets/maps/europe_1805.json`**. Run the backend as `-m backend.main`.
- The **registry** `godot-client/project-sovereign/assets/maps/europe.json` is the single source for renderer AND `create_europe_regions()` (lru_cached — restart the server after edits; NEVER re-run `build_region_key_from_psd.py --adjacency-only`: it clobbers the hand-authored sea-link folds + DEF-7 cuts; `adjacent` = walkability incl. the 18 sea links, `sea_links` = the drawn dashed routes only).
- Europe config is scenario-scoped in `nation_config.py` (never touch the legacy globals — N1); scenario authoring contract in `docs/MODDING_FORMAT.md` (incl. the Slice-8 `region_overrides` key); capital garrisons tier-differentiated on Europe only (majors 25k / secondary 15k / minors 10k, `get_capital_garrison_target`); scenario boots compute fog via `calculate_visibility()` in `from_scenario` (own soil PARTIAL+, marshal locations FULL); Russia honor bias is 1.1 (DG-4 fixture pins re-derived at 1.1); G4 measured: bare-Europe turn 0.49× legacy, 1805 campaign 5.4× (roster workload), tripwires in `test_scale_readiness_phase2.py`.
- Manual settlement smoke shortcut: `SOVEREIGN_SMOKE_START=settlement_multilateral` (never combined with `SOVEREIGN_SCENARIO`); other presets: `settlement_losing`, `settlement_rejected`, `settlement_multiwar_ambiguity`, `settlement_surrender`, `settlement_recurring_gold`.

### Active work items

- ~~Gate 4 visual half~~ **✅ PASSED July 3, 2026** (user confirmed the 5-item eyes-only checklist; passage recorded in STATUS.md + the cleanup spec masthead; the DWL-DIP-E7 / DWL-DIP-METTERNICH 8.EVAL triggers are LIVE).
- ~~Slice H~~ **✅ LANDED July 3, 2026** (gate approved v1.0 + implemented same day): `request_reward_or_restoration` + `demand_bargain_honor` are LIVE (Grant/Decline/Honor through the restage seam; `ally_petition` dial-protected provenance; `ally_petition_state` serialized; tests in `test_settlement_slice_h_ally_petitions.py`). **The settlement arc is fully closed — no live successors.** SC-32 formally CLOSED; do NOT rebuild G2 sub-slices.
- **Command Robustness (`COMMAND_ROBUSTNESS_SPEC.md` v0.6, ACTIVE — scope blessed July 3, 2026):** ~~CR-0~~ + ~~CR-1~~ **✅ LANDED July 3, 2026** — parser rosters live-world derived (all 7 French 1805 marshals commandable; `test_command_robustness_cr0_parser_rosters.py`) and the eval harness is the phase's standing regression gate (`tests/data/parser_golden_corpus.json` 246 entries + `backend/ai/parser_eval.py` engine/CLI + `test_command_robustness_cr1_eval_harness.py`; typed `status` wire connected; new-action checklist step 12 = corpus entry). ~~CR-2~~ **✅ LANDED July 4, 2026** — marshal-aware confidence + one forced LLM retry on fuzzy errors; support-object/condition-clause executor demotions; the unified `command_clarification` LOCAL_PLANNING question ("Which marshal, Sire?" — `backend/commands/clarification.py`); silent-marshal-drop fixed; sequential "then" orders parse the first clause + report the tail (`test_command_robustness_cr2_clarification.py`, 63 tests). ~~CR-3~~ **✅ LANDED July 4, 2026 (second slice that day)** — live-LLM modernization: model pin `claude-haiku-4-5` (old 2024 Haiku pin deprecated); forced tool-use structured output (`PARSE_TOOL` + `tool_choice` in providers.py — brace extraction is a fallback only; `max_tokens` 1000); LLM strategic verbs remapped at the provider seam (`pursue`→attack, `march`/`support`/`reinforce`→move — `detect_strategic_command` still owns the upgrade); dead `dialogue` field CUT (Flavor Echoing stays parked at the CR-5 gate); `ParseResult.llm_error` guarantees at most ONE blocking LLM call per request (Berthier `skip_llm` + retry guard); `diplomatic_data` allowlist + field-stripping at the `validate_parse_result` seam; cheat gate keys off command `key_source` (BYOK-safe, env fallback for hand-built dicts); prompt geographic block now derives per-marshal compass lines from live `grid_position`; few-shots are live-roster templates incl. the corpus `live_phrasing_backlog` verbs; `build_clarification_prompt` deleted (`test_command_robustness_cr3_llm_modernization.py`, 72 tests; live-API probe verified; 5 adversarial-review fixes folded pre-commit). ~~CR-4~~ **✅ LANDED July 4, 2026 (third slice that day)** — context carryover on the existing `command_history` substrate (`backend/commands/context_carryover.py`): deterministic PRE-parse reference resolution ("again", "same target", "him"/"her"/"them", "there", "not you, Davout" — Golden Rule 6, no LLM) + Persistent Command Focus (a bare specific order defaults to the last explicitly-addressed marshal at the "Marshal 'None'" seam, before the CR-2 clarification). Decisions: history records in BOTH mock+live modes and now carries `target`; focus is derived from history (no new serialized field); "not you, X" re-issues without auto-undo; carryover skipped while a diplomatic dialogue awaits an answer (`test_command_robustness_cr4_context_carryover.py`, 73 tests; 8 pre-commit adversarial-review fixes + 5 post-landing audit fixes — pronoun/"there" anchoring, focus warning re-surface, soft-stop recording, broadened collective guard). **CR-5 (Personality-Biased Disambiguation) — scope BLESSED July 5, 2026** (full blessed scope in `COMMAND_ROBUSTNESS_SPEC.md` §6, grounded in a code-verified pipeline audit + adversarial design panel): prompt-copy delegation-verb table (§6.2) on the single existing parse call; **player-visible behavior is the three-way split aggressive→attack / cautious→scout / literal→ask** (Soult reassigned cautious→literal at the gate — `europe_1805.json`, pinned by `test_cr5_literal_arm_player_reachable` — so the "asks" arm is player-reachable; "Grouchy asks" reframed to "Soult asks"; the dramatic literal continue-into-disaster beat stays gated behind the autonomous Grouchy Moment); guardrails = action-only + temp-0 pin + objection-first ONE-modal legibility + a blocking personality-type pre-flight (§6.3); rider (d) "words become the record" IN as a separately-tested sub-item, **Flavor Echoing promoted from §4 to owned slice CR-5b** (non-parroting mock design is its entry gate). The march-to-guns "literal continues" row was CUT (unimplementable at the parse seam + a category error — the autonomous Grouchy Moment is re-homed to its own gate). Safe half (ASK/cautious arms, prompt table, first-use hint) landed July 6 (`a438614`); Phase 3 (the lethal attack-on-arrival gate) landed July 7 (`de6d740`). **CR-5 COMPLETE — Phase 4 LANDED July 7, 2026.** The aggressive→engage arm is LIVE: a genuine live-mode resolved aggressive delegation re-issues a delegation-INFERRED strategic **PURSUE** (`pursue <enemy>`, NOT a bare `attack` — that is not a strategic keyword, so it would never become a tagged/gated order) tagged `delegation_inferred=True`; every auto-attack seam is fortification/terrain-gated — the Phase-3 per-turn `_inferred_attack_gate` PLUS two NEW first-step PURSUE seams Phase 3 didn't cover (co-located-at-creation + move-failed-at-target) now closed via `strategic_executor._inferred_first_step_gate`. **Guardrail (e) hardened to a MODE gate** (`parse_resolved_to_action` returns False for `mode=="mock"`, so a mock / fast-parser resolution — even one carrying a stray action keyword — always degrades to ASK; the bias is live-only). **Rider (d) "words become the record" LIVE** — the verbatim delegation phrase rides the inferred order's `original_command`, quoted in the campaign-log battle one-liner + battle-report `delegation_attribution`, scoped to the quarry (`order.target==defender.name`, never an explicit charge/attack at a different enemy). First-use hint is now **latch-on-surface** (shown even when the reissue is rejected). Failsafe flipped `True` + tripwire rewritten; guardrail-(d) personality freeze re-confirmed. **Scope boundary (documented, pinned):** the cannon-fire redirect (autonomous Grouchy Moment) *abandons* the order (nulls `strategic_order`) before rushing a different battle, so the inferred gate correctly no-ops — re-homed per spec §6.3, not a Phase-4 seam. Two adversarial audit rounds (6-dimension find→verify, then fix-review + completeness critic — lethal-seam completeness confirmed sound): 5 confirmed findings, ALL fixed. `test_command_robustness_cr5_personality_disambiguation.py` (86) + 3 `live_only` corpus rows + harness `live_only` support. **A post-completion whole-slice adversarial + live-backend audit (July 7) landed 8 more fixes** — 1 HIGH (the aggressive bad-odds interrupt was unanswerable via the Godot popup: the stored `pending_interrupt` omitted the marshal name, so `/strategic_response` got the literal `"Marshal"` and 404'd — fixed by stamping `"marshal": marshal.name` on every strategic-interrupt builder in `strategic.py`/`strategic_executor.py`, serialized), 2 MED (comma-less address `"Marshal Soult deal with Mack"` dropped the delegation → `_ADDRESS_RE` comma made optional; camelCase enemy key leaked into copy → new `display_names.humanize_entity_name` chokepoint + spaced-name resolution in `_resolve_target`), 5 LOW (carryover target poisoning + 4 test/doc-coverage gaps); all fixed with regression tests (86→103; suite 11710 green; the 3 player-facing fixes re-verified live). Details: spec §6.10. **CR-5b (Flavor Echoing) ✅ LANDED July 7, 2026** — the marshal's IMMEDIATE spoken reply at the RESPONSE seam echoes the player's tone ("the game heard me"). **Entry gate CLEARED** (adversarial design panel): the non-parroting fallback is a bounded deterministic FLOOR keyed to (personality, RESOLVED action, target) — never the raw verb — with a falsifiable negative assertion. Architecture: a `flavor` field rides the EXISTING CR-3 parse call (zero extra LLM call — re-adds the field CR-3 cut "parked at the CR-5 gate"; plumbed schemas.py→providers.py→parser.py lift→main.py attach), gated to delegation-only in the prompt (null otherwise). Live LLM composes an action-AGNOSTIC attitude line (it can't name the deed — the deterministic router owns it, so no contradiction); `delegation.flavor_passes_register` DROPS a parroting/action-naming/register-violating line to the deterministic floor (the live-mode fallback; mock always ASKs via guardrail e, so the executed arms are live-only). Cosmetic ONLY (Golden Rule 6 — flavor is a display string, never read by routing/serialization). Scope boundaries (Golden Rule 9): does NOT touch the ASK arm (its clause-quote is already the echo) and does NOT duplicate rider (d)'s RECORD-seam quote; aggressive flavor skips every modal surface (bad-odds + objection). `test_command_robustness_cr5b_flavor_echoing.py` (60). Two adversarial workflows (3-lens design panel → clear the gate; 3-lens find→verify review → 4 confirmed cosmetic fixes: robust contraction-safe quote tokenizer, word-boundary parrot guard, objection-modal attach guard, personality-word double-narration guard, + floor variety). **Next: Comprehensive Codebase Audit → econ eval → Economy Revisit build (re-sequenced July 9, 2026).** CR-6 needs its own design gate.
- ~~**Comprehensive Codebase Audit (`AUDIT_GUIDELINE.md`, Fable-led)**~~ — **✅ CORRECTNESS SWEEP COMPLETE July 9, 2026** (full log `docs/audits/AUDIT_2026_07_09.md`): six committed chunks per §10, **7 fixes / 0 open escalations** — turn-1 DP fallback (1805 boots with 5 DP, was 4), combat personality-copy misattribution ("Bravest of the Brave"/"Iron Marshal" captioning other marshals), wrong-side Berthier coordination observations, unpaired hold-clear on order break, vassal dispatch naming the wrong protector, the RNG-flaky movement test seeded, scorer-seam bare-import removed. The three never-audited subsystems (`diplomatic_defiance.py`, `war_contribution.py`, `settlement_reactions.py`) verified sound; live-backend seam + topology verification clean; doc counts reconciled to **11,789/1**. **✅ Econ eval COMPLETE July 9, 2026 (same day)** — memo `docs/audits/ECONOMY_ECON_EVAL_2026_07_09.md` (23 verdicts, all claims re-verified against `c5e411e`; zero audit escalations to triage; headline dissents = E5 full-income redirect + ES-3→pass 1; simplifications = ES-2 stability-tier occupation cost + E2 cuts; owned expansion riders = EC-5a subsidy coupling + CS activation surface). **~~The §8 creative/fun-factor capstone~~ ✅ COMPLETE July 10, 2026** (post-EC as staged; memo `docs/audits/CREATIVE_AUDIT_2026_07_10.md`): verdict — the game generates great stories and doesn't tell them; narration (3.5) + battle legibility (4.5) now lag every system, economy up to 6 post-EC. 10 defects routed (`BUG_FIXES.md` §Creative-Audit Findings, BUG-CA-7 P1), Wave 6 filed (`DESIGN_REFINEMENT.md`), 4 inline legibility fixes. Sequence CLOSED: **~~audit sweep~~ → ~~econ eval~~ → ~~EC-2 gate~~ → ~~EC build~~ → ~~§8 capstone~~ → ▶ MC gate.**
- **Economy Revisit (`ECONOMY_REVISIT_SPEC.md` v0.4 — design DONE; ✅ EC-2 GATE BLESSED July 9, 2026 post-econ-eval — gate record §0.6.7 AMENDS the description below: ES-7 = FULL-income redirect not a 30% skim, ES-2 = stability-tier occupation cost not an integration ramp, ES-3 rides pass 1, grant scope = conquered-only + estate occupation-exempt; the BUILD RUNS NEXT per §0.6.3 as amended):** EC-0 (AP-reset) + PRE-EC ledger floor LANDED; EC-6 DECIDED = sandbox — **Track 1 (S1–S4 incl. the EC-6a toggle) ✅ ALL LANDED July 9, 2026; Track 2 ✅ CLOSED July 9: ~~S5 ES-3~~ (upkeep 8 + force limit + ladder, Europe-scoped) · ~~S6 ES-2~~ (stability-tier occupation cost on non-homeland provinces, 0.50/0.35/0.20/0.10-floor × base income, zero new serialized fields, Europe-scoped) · ~~S7 ES-7~~ (full-income redirect — `dotation.py`, `Marshal.dotation_regions` + `expectation_grace_turn` only, `grant_dotation` 12-step wiring, amendment-4 estate occupation-exemption, grace-turn-2 erosion via `modify_trust` only, AI grant rung, "Dotations" ledger line, 57 tests) + the stacked two-sided E1 band test GREEN (`test_economy_e1_band.py` — turn-1 France 36.9% absorption with the 55–70% aspirational anchor flagged as unreachable at blessed constants without breaking Austria's boot solvency; fresh doubled empire 84% absorbed; steady-state doubled empire 54.5% in-band). EC PASS 1 COMPLETE — NEXT = §8 capstone**. **EC-2 audit + gate decisions RECORDED July 8; the gate-ready pass-1 spec is §0.6** — ES-7 REFRAMED to "The Cost of Success" — mechanically unchanged (recurring income-skim + no-trust-bump + grace-turn erosion) but its **player-facing surface is now "endow the marshal with an ESTATE and a province-derived TITLE"** (e.g. "Endow Ney with the Duchy of Swabia" — the Domaine Extraordinaire framing; internal action id stays `grant_dotation`; ES-8 title *flavor* rides pass 1 for free, the ES-8 stat-bonus mechanic stays deferred): success raises a marshal's reward *expectation*; unmet/revoked expectation erodes loyalty via `modify_trust`; **paying stops the bleed, never buys trust**; explicitly OUT of the `modify_relationship` Jealousy graph; fires AI-side, GR5. Pass-1 = **ES-2 Occupation Upkeep + ES-7** matched pair, **ES-1** manpower fix as gate-free prereq; ES-4 → pass 2; **ES-10 CUT**. Build order = §0.6.3 (gate-free ES-1 re-key+retune / EC-6a toggle / ledger-GR8 fix, THEN the EC-2 pair). All balance numbers (band E1 + regen/upkeep/ES-7 constants E2–E6) ESCALATE to the EC-2 gate. **EC-5 self-cost = Option B / EC-7 (ES-6) timing = dated-trigger / sandbox soft-goal = open-ended all RESOLVED July 8 (cont.); the blessed numbers were SET at the July-9 gate (§0.6.7) — nothing about EC pass 1 remains open.**
- **Marshal Content Pass (`MARSHAL_CONTENT_PASS_SPEC.md`, drafted, NEEDS DESIGN GATE):** the 21-marshal 1805 roster ships with no abilities/skills/relationships; MC-0 (ability display bug) may land independently. Prerequisite for the Jealousy gate.
- **Settlement routing rules that still hold:** blocked ratification omits `confirm_settlement`; `Revise Terms` only when a real edit-capable route exists (the guided PROPOSE surface — the freeform editor is retired); failed review routes to `Open War Detail`; incoming AI settlement offers are LIVE and answerable, but enemy-offer WAITING affordances stay terminally removed (G2d cut); pair-substitute CTAs follow the SC-29 scoped-eligibility contract; surrender terms live per the landed SC-31 `author_surrender_terms` eligibility contract; `request_terms` is LIVE (Slice G1). Tests patch the settlement scorer at `settlement_scoring.calculate_common_peace_acceptance` (stable seam).

### Deferred / homed (Golden Rule 9)

DEF-1 Roster Voices (15 chancery-fallback diplomats; owns the loose voice/copy backlog), DEF-3 Economy Pass (→ `ECONOMY_REVISIT_SPEC.md` EC-1), DEF-4 Phase 5.2/5.3/5.6 (measured NOT forced; 15× tripwire), DEF-5 naval spec, DEF-12 full map modes (gate-owned), DEF-13 dated UI-Scale Mini-Pass (baseline pinned) — rows in `docs/MAP_IMPLEMENTATION_PLAN.md`. CH-6/CH-7 + DW-2/DW-4 remainders owned by `docs/SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md`'s ledger. 8.EVAL owns the war-LLM/diplomacy triage (DWL-DIP-E7, DWL-DIP-METTERNICH, DESIGN_REFINEMENT queue items 5-6).

### Design Gates

- **Wave 6 Fun-Factor Build** — **✅ APPROVED IN FULL July 10, 2026 AND ✅ BUILT COMPLETE the same day** (all 12 slices W6-0..W6-11 landed; spec §15 DoD recorded; the §0 re-score measured all four target pillars MET — memo `docs/audits/CREATIVE_AUDIT_2026_07_10.md` §9). Gate additions honored: Dynamic Battle Naming (W6-2) and the Literal Doctrine (W6-5 — user steer: literal marshals need not object, the fantasy is "generals who do what they're ordered"). Build spec `docs/WAVE6_FUN_FACTOR_SPEC.md` (authoritative; blessed defaults remain tunable in-band, structural changes escalate). Supersedes R59/R153 literal-objection triggers.
- **Slice H Ally Petitions** — ✅ APPROVED v1.0 + LANDED July 3, 2026 (D-H1..D-H5 as recommended). `docs/SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md`
- **Command Robustness** — v0.2 scope BLESSED July 3, 2026 (CR-0..CR-5); **CR-5 detailed scope BLESSED July 5, 2026 (spec §6); ~~CR-5b (Flavor Echoing)~~ ✅ LANDED July 7, 2026 (entry gate CLEARED — non-parroting mock floor specifiable, no user gate needed).** CR-6 needs a dedicated gate. `docs/COMMAND_ROBUSTNESS_SPEC.md`
- **Economy Revisit** — v0.4 (July 8, 2026); **EC-2 gate-ready pass-1 spec in §0.6** (ES-2 + ES-7-reframed pair — ES-7 surface = "endow marshal with estate + province-derived title"; band + constants E1–E6 escalate). **✅ EC-2 GATE BLESSED July 9, 2026** — the econ-eval memo (`docs/audits/ECONOMY_ECON_EVAL_2026_07_09.md`) was accepted in full at the gate; **the gate record is spec §0.6.7 (authoritative)**: ES-7 full-income redirect (0.30 skim deleted), ES-2 stability-tier occupation cost (no new serialized fields), ES-3 promoted into pass 1, conquered-only/occupation-exempt endow triangle, blessed numbers E1–E6. **The build session codes §0.6.3 as amended — no further gate before Track 2.** EC-5 self-cost (=Option B) / EC-7 timing (=dated-trigger) / sandbox soft-goal (=open-ended) RESOLVED July 8 (cont.) — only the blessed numbers (E1–E6) remain at the gate (§0.6.6). EC-6 = sandbox (decided). `docs/ECONOMY_REVISIT_SPEC.md`
- **Marshal Content Pass** — v0.1 DRAFTED July 2, 2026, NEEDS APPROVAL (MC-1 ability set). DO NOT CODE (MC-0 display fix exempt). `docs/MARSHAL_CONTENT_PASS_SPEC.md`
- **Jealousy System** — v3.1 spec drafted, NEEDS APPROVAL; sequenced AFTER the Marshal Content Pass (MC-3 relationships are its prerequisite) with a v3.2 roster addendum. DO NOT CODE. `docs/JEALOUSY_SPEC.md`
- **Coalition Spec v1.1** — Approved Mar 2, 2026. `docs/COALITION_SPEC.md`
- **Settlement Conversational Re-front v0.6 / Guided Terms v0.2 / Cleanup v0.32** — approved + fully implemented (historical; per-court gate contract remains normative in the re-front spec).

---

## File Reference

### Backend Core

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI endpoints, response formatting |
| `backend/commands/executor.py` | Action execution, dispatch, objection routing (~1.5k lines) |
| `backend/commands/combat_executor.py` | Combat execution + coordination: attack, bombardment, charge, garrison, form_square, post-combat pipeline, multi-marshal coordination, reinforcements, overwatch, auto-dispatch combat (~4.7k lines, R10A+R10B) |
| `backend/commands/strategic_executor.py` | Strategic order execution: MOVE_TO, PURSUE, HOLD, SUPPORT, cancel, objection messages, target resolution, first-step blocking (~1.8k lines, R11) |
| `backend/commands/diplomatic_executor.py` | Diplomatic execution: proposals, dialogue state machine, missions, trust reactions, AI proposal accept/reject/counter, terms guidance wizard (~2.3k lines, R11) |
| `backend/commands/economy_executor.py` | Economy execution: economy report, recruit, garrison, build, watchtower, repair (~800 lines, R13A) |
| `backend/commands/tactical_executor.py` | Tactical execution: defend, wait, drill, fortify, unfortify, stance_change, restrain, auto_break_square (~715 lines, R13A) |
| `backend/commands/movement_executor.py` | Movement execution: move, scout, auto_assign_scout, retreat, movement attrition (~680 lines, R13B) |
| `backend/commands/meta_executor.py` | Meta/debug/objection: end_turn, status, help, debug, cheat, handle_objection_response, post_objection (~1.9k lines, R13B) |
| `backend/commands/vassal_executor.py` | Vassal management: invest, change_autonomy, make_vassal, release_vassal (~147 lines, R13A) |
| `backend/commands/capture_executor.py` | Post-capture plunder/secure choice handling (~94 lines, R13A) |
| `backend/commands/parser.py` | Command parsing, fuzzy matching |
| `backend/commands/disobedience.py` | V1 objection system, trust values |
| `backend/commands/objection_v2.py` | V2a objection system (ConcernLevel triggers) |
| `backend/commands/defiance.py` | V2b defiance system (chance calc, fallback table, outcomes) |
| `backend/commands/strategic.py` | Strategic order per-turn executor |
| `backend/commands/vindication.py` | Vindication tracker |
| `backend/models/marshal.py` | Marshal class, combat modifiers, states, serialization |
| `backend/models/world_state.py` | Game state, turn processing, action economy |
| `backend/models/region.py` | `create_europe_regions()` builds the live 126-province world from `europe.json` (lru_cached); legacy REGIONS_DATA/NATION_CAPITALS survive as the test-fixture world; terrain/region type constants, starting_controller, grid_position |
| `backend/nation_config.py` | Scenario-scoped nation config: EUROPE_ROSTER, EUROPE_NATION_CAPITALS/GOLD/ACTIONS/AUTHORITY, EUROPE_MANPOWER_POOLS, EUROPE_VASSAL_WEB + builders; legacy DEFAULT_* globals (N1: never perturb them) |
| `backend/models/personality.py` | PersonalityType enum |
| `backend/models/personality_modifiers.py` | Combat bonuses by personality |
| `backend/models/cooldown_manager.py` | CooldownManager (5 auto-decrement cooldowns) + PopupQueue (7 priority-ordered popups) (R6) |
| `backend/models/dialogue_manager.py` | DialogueManager (push/pop/peek, priority queue, clear_stale timeout, promote_if_empty) (R12) |
| `backend/display_names.py` | Single source of truth for all internal→display name translations (R7) |
| `backend/campaign_log.py` | Campaign log fog filter + one-liner formatter |
| `backend/game_logic/combat.py` | Combat resolution, messages |
| `backend/game_logic/battle_report.py` | Post-battle modifier snapshots, report generation, Berthier observations |
| `backend/game_logic/relationship.py` | Win/Loss Relationship Formula (severity, ordered pairs, cooldown) |
| `backend/notifications.py` | Notification system (EU4-style persistent alerts, collector, dismiss) |
| `backend/game_logic/dispatch.py` | Morning Dispatch builder (fog-filtered turn-start briefing), stores last_morning_dispatch on WorldState |
| `backend/game_logic/ledger.py` | Strategic Ledger builder (6 sections: forces, territories, economy, intel, manpower, orders) |
| `backend/game_logic/marshal_overview.py` | Marshal Management builder (player marshal cards with identity, ability, stats, trust, status, relationships) |
| `backend/game_logic/turn_manager.py` | Turn flow, enemy phase |
| `backend/ai/enemy_ai.py` | Enemy AI decision tree (P1-P8) |
| `backend/ai/llm_client.py` | LLM integration (fast parser + Anthropic) |
| `backend/ai/strategic_parser.py` | Strategic command detection |
| `backend/ai/validation.py` | VALID_ACTIONS (single source of truth for LLM) |
| `backend/ai/prompt_builder.py` | Context-aware LLM prompts |
| `backend/intel_report.py` | Berthier Intelligence Report (fog-filtered status view) |
| `backend/models/diplomat.py` | DiplomaticRepresentative class, starting diplomats |
| `backend/game_logic/diplomacy.py` | Diplomacy engine: transitions, war score, acceptance formula, DP, war declaration, cascade, trade income |
| `backend/game_logic/ai_diplomacy.py` | AI proposal generation (P1-P7 triggers), M3 counter-offer, alliance conflict check, anti-spam |
| `backend/game_logic/diplomatic_advisory.py` | Advisory conversations: threat assessment, nation analysis, action recommendations |
| `backend/game_logic/coalition.py` | Coalition system: threat accumulation/decay, formation/brewing/instant, leader/posture, AI friction/convergence, war exhaustion, British subsidy, dissolution/cooldown |
| `backend/game_logic/diplomatic_ledger.py` | Diplomatic Ledger builder (4 tabs: nations, treaties, balance_of_europe, talleyrand) with fog-filtered army strength |
| `backend/game_logic/war_status.py` | War Status Panel data builder: `build_active_wars()` produces war/coalition/armistice data for HUD, embedded in every response via `_include_popup_passthroughs()` |
| `backend/game_logic/vassal.py` | Vassal system: creation, loyalty, rebellion, cascade, tribute, investment, autonomy, marshal assimilation, Continental System |
| `backend/commands/diplomatic_defiance.py` | Talleyrand sabotage: defiance chance, sabotage types, discovery, confrontation, pre-proposal objection, redemption |
| `backend/save_manager.py` | Save/load file I/O, autosave |
| `backend/game_logic/settlement_*.py` | Imperial Settlement package (CH-1 split, June 10, 2026): `settlement_routes` (L0 routing/reopen/recovery) → `settlement_validation` (L1 primitives/eligibility/validator) → `settlement_baseline` (L2 baseline/presets/per-court acceptance) → `settlement_staging` (L3 draft stores/confirm build/stage/guided payload) → `settlement_ratify` (L4 apply/ratify) → `settlement_actions` (L5 dialogue-action dispatch + arms) → `settlement_offers` (L6 offers/petitions/recurring). Each imports lower layers only. `settlement_preview.py` is the public re-export door (production imports true homes). Tests patch the scorer at `settlement_scoring.calculate_common_peace_acceptance` (stable seam). |

### Godot Core

| File | Purpose |
|------|---------|
| `utils.gd` | Shared color palette (COLOR_ consts + map-layer colors), NATION_COLORS (20-nation Europe set, Slice 7.5 re-authored), `display_nation_name()`/`humanize_nation_keys_in_text()` render-time key translation (July 2 UI Cleanup — R7 chokepoints), bbcode_color/format_number helpers (R15) |
| `popup_base.gd` | Base class for modal popups: close_popup, _disable_all_buttons, _apply_standard_theme (R15) |
| `dialog_manager.gd` | Centralized dialog registry: register, get_dialog, is_any_modal_open, hide_all (R16) |
| `api_client.gd` | Backend communication |
| `game_manager.gd` | Game state coordination |
| `map_renderer_base.gd` | Map renderer base: scene layers, Camera2D+SubViewport, province color-map, hover/click, zoom/pan |
| `map.gd` | The Europe GAME map (Slice 7 rewrite): game glue on the chain `map_renderer_base.gd` → `europe_map.gd` → `map.gd`; name-keyed `/map_topology` handoff, Utils colors |
| `europe_map.gd` / `europe_map_smoke.gd` | Shared Europe renderer (asset paths, Region_NNN→name re-key, registry anchors) / the smoke-scene subclass (seed + owner-cycle demo) |
| `map_label_layer.gd` | Screen-space zoom-LOD map labels (nation/province tiers, occupied-rect avoidance) |
| `main.gd` | Terminal UI, response handling |
| `pause_menu.gd` | Pause menu overlay (Phase 6.5) |
| `campaign_log.gd` | Campaign log overlay (Phase 6.5), CanvasLayer 50 |
| `notification_bar.gd` | Notification bar (Phase 6.5), reparented into top bar |
| `top_bar.gd` | Top bar controller (Session A): screen management, hotkeys, notifications, turn counter |
| `dispatch_view.gd` | Dispatch re-read screen (Session A): CanvasLayer 50, BBCode rendering |
| `strategic_ledger.gd` | Strategic Ledger screen (Session B): CanvasLayer 50, 6 sub-tabs, number key switching, Orders tab cancel buttons |
| `marshal_management.gd` | Marshal Management screen: CanvasLayer 50, card-based marshal view, G key toggle |
| `diplomatic_ledger.gd` | Diplomatic Ledger screen (Session 8B): CanvasLayer 50, 4 sub-tabs (Nations/Treaties/Balance of Europe/Talleyrand), D key toggle |
| `*_popup.gd` (7 files) | Modal popups: coalition_declaration, incoming_proposal, talleyrand_objection, sabotage_discovery, talleyrand_redemption, vassal_rebellion, alliance_paradox. CanvasLayer 100-119 |
| `mailbox_panel.gd` | Browsable mailbox inbox: CanvasLayer 119, click-to-activate rows |
| `war_status_panel.gd` | War Status HUD (CanvasLayer 25) + `war_detail_popup.gd` (CanvasLayer 30) |
| `diplomacy_wizard.gd` | Diplomacy Button wizard (Session B): F1 hotkey, 2-step nation→action flow, own HTTPRequest, command handoff, `open_for_nation()` for war panel handoff |

---

## Before Modifying: Required Reading

| If you're modifying... | Read these first |
|------------------------|------------------|
| Combat damage/modifiers | `marshal.py` (get_*_modifier), `combat.py` (resolve_combat), `combat_executor.py` (_execute_attack, _execute_bombardment), `docs/MULTI_MARSHAL_SPEC.md` (coordination bonuses) |
| Multi-marshal coordination | `docs/MULTI_MARSHAL_SPEC.md`, `combat_executor.py` (_calculate_coordination_context, _calculate_reinforcements, _calculate_overwatch), `marshal.py` (transient bonus fields) |
| Combat execution (attack/bombard/charge) | `combat_executor.py` (all _execute_* methods, post-combat pipeline, coordination, reinforcements, overwatch) |
| Marshal abilities | `personality_modifiers.py`, `marshal.py`, `combat.py`, `docs/ADDING_CONTENT.md` (wiring checklist), `marshal_overview.py` (_WIRED_ABILITY_MARSHALS) |
| Fortify/Drill mechanics | `tactical_executor.py` (_execute_fortify/drill), `marshal.py`, `world_state.py` (_process_tactical_states) |
| Disobedience/Trust | `disobedience.py`, `objection_v2.py`, `personality.py`, `docs/V2B_DEFIANCE_SPEC.md` |
| Cavalry limits | `world_state.py` (_check_cavalry_limits), `marshal.py` (cavalry counters) |
| Terrain system | `region.py` (constants, Region class), `combat.py` (_get_terrain_bonus), `combat_executor.py` (resolve_battle calls, charge blocking) |
| Turn processing | `world_state.py` (advance_turn), `meta_executor.py` (_execute_end_turn) |
| Adding new actions | See pattern below |
| Retreat/Broken state | `combat.py` (forced retreat), `marshal.py` (retreat_recovery), `combat_executor.py` (_handle_forced_retreat, _apply_forced_retreat_or_break) |
| Enemy AI behavior | `enemy_ai.py`, `turn_manager.py`, `executor.py` (is_player_action check) |
| Capital garrison | `combat_executor.py` (_resolve_garrison_combat), `world_state.py` (garrison init/regen), `enemy_ai.py` (P4.25) |
| Player garrison | `economy_executor.py` (_execute_garrison), `region.py` (garrison_detachment), `world_state.py` (regen exclusion) |
| Fort degradation | `combat.py` (resolve_combat degradation block), `battle_report.py` (P6c observations) |
| Supply attrition | `world_state.py` (process_supply_attrition), `region.py` (supply_capacity) |
| Strategic commands | `strategic.py`, `strategic_parser.py`, `strategic_executor.py` (_execute_strategic_command, _execute_cancel, objection handling) |
| Objection V2 system | `objection_v2.py`, `docs/OBJECTION_V2.md`, `docs/V2B_DEFIANCE_SPEC.md` |
| Fog of war | `docs/FOG_OF_WAR_SPEC.md`, `intel.py`, `intel_report.py`, `map.gd`. Use `get_visible_enemies()` for player-facing, `get_enemies_of_nation()` for omniscient only |
| Manpower / recruitment | `world_state.py` (manpower constants), `economy_executor.py` (_execute_recruit), `enemy_ai.py` (P1/P4.5/P7) |
| Artillery / bombardment | `marshal.py` (artillery flag), `combat.py` (cavalry counter, fort degradation), `combat_executor.py` (_execute_bombardment, _distribute_casualties), `enemy_ai.py` (_score_artillery_position) |
| Top bar / screen system | `top_bar.gd` (controller), `main.gd` (_on_screen_changed, _is_modal_dialog_open, _is_screen_open, _is_hotkey_blocked), `docs/TOP_BAR_SPEC.md` |
| Morning dispatch / re-read | `dispatch.py` (build + store), `dispatch_view.gd` (render), `main.gd` (_display_morning_dispatch), `world_state.py` (last_morning_dispatch field) |
| Strategic ledger | `ledger.py` (build_strategic_ledger), `strategic_ledger.gd` (render), `world_state.py` (get_manpower_regen_rates), `main.py` (GET /ledger, POST /cancel_order) |
| Marshal management UI | `marshal_overview.py` (build_marshal_overview), `marshal_management.gd` (render), `marshal.py` (biography field), `main.py` (GET /marshal_overview) |
| Win/Loss relationships | `relationship.py` (formulas, participants, process), `combat_executor.py` (_execute_attack wiring), `marshal.py` (modify_relationship, last_relationship_change_turn), `docs/MULTI_MARSHAL_SPEC.md` §9 |
| Square formation / Tactical Triangle | `docs/TACTICAL_TRIANGLE_SPEC.md`, `marshal.py`, `combat.py`, `combat_executor.py`, `tactical_executor.py`, `executor.py` |
| Vassal system | `vassal.py`, `world_state.py` (vassals dict, advance_turn), `diplomacy.py` (AP clause), `turn_manager.py`, `dispatch.py` |
| Diplomatic ledger | `diplomatic_ledger.py` (build_diplomatic_ledger, fog-filtered army strength), `main.py` (GET /diplomatic_ledger, debug endpoints), `world_state.py` (popup fields) |
| Diplomacy wizard / button | `diplomacy_wizard.gd` (wizard UI, `open_for_nation()`), `main.gd` (F1 hotkey, button wiring, command handoff), `main.py` (GET /diplomatic_preview nation list mode), `docs/DIPLOMACY_BUTTON_SPEC.md` |
| War status panel (N4) | `war_status.py` (build_active_wars), `war_status_panel.gd` (HUD), `war_detail_popup.gd` (detail), `main.gd` (_process_active_wars) |
| Suggested terms / smart suggestions | `diplomatic_templates.py` (generate_suggested_terms 5-stage pipeline), `diplomatic_dialogue.py`, `docs/TALLEYRAND_SMART_SUGGESTIONS_SPEC.md` |
| Diplomacy execution | `diplomatic_executor.py` (_execute_diplomatic*, handle_diplomatic_dialogue_response, trust reactions, AI proposal handlers) |
| Dialogue state (R12, PL-27) | `dialogue_manager.py` (push/pop/peek, PL-27 taxonomy: HARD_STOP/SOFT_STOP/HYBRID/LOCAL_PLANNING types), `world_state.py` (transparent properties). Only hard-stop dialogues block commands. Endpoints: `GET /mailbox`, `POST /mailbox/activate` |
| Diplomacy system (Phase 8) | `docs/DIPLOMACY_SPEC.md`, `docs/COALITION_SPEC.md`, `diplomacy.py`, `diplomat.py`, `diplomatic_dialogue.py`, `diplomatic_templates.py`, `ai_diplomacy.py`, `diplomatic_advisory.py`, `vassal.py`, `diplomatic_defiance.py`, `coalition.py` |
| Memory and Pressure substrate (hegemony / betrayal memory / paradox / reliability) | `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v2.4.3 — §8.8 holds the DG-4 call-to-arms episode contract, §8.6.1a authors the Make Amends grievance variant, §8.8.7a authors the existing-alliance termination on defensive refusal; `docs/SCALE_READINESS_PLAN.md` §DG-4 Amendment is the source of truth), `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`, `docs/COMMITMENTS_PRESENTATION_SPEC.md`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `docs/COALITION_SPEC.md`, `diplomacy.py`, `world_state.py` (`betrayal_history`, `next_episode_id`), `commitments` logic within `diplomatic_templates.py`, `campaign_log.py`, `coalition.py` (hegemony engine when landed) |
| Peace Deals / Imperial Settlement | **The settlement arc is COMPLETE (July 2, 2026)** — package: `settlement_routes/validation/baseline/staging/ratify/actions/offers.py` + the `settlement_preview.py` public door (CH-1 split); tests patch the scorer at `settlement_scoring.calculate_common_peace_acceptance`. **NO live successors** — Gate 4 passed in full and Slice H landed July 3, 2026 (`docs/SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md` v1.0). Normative contracts: `SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6 (per-court gate), `SETTLEMENT_GUIDED_TERMS_SPEC.md` v0.2 (guided authoring — the freeform editor is retired), `SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32 (SC rows; SC-32 CLOSED). `SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md` owns the surviving CH-6/CH-7 + DW ledger rows. Do not route active work to v0.19-v0.27, Slice F/E, or a fresh G2 start. |
| C3-lite presentation (Memory and Pressure final slice) | `docs/COMMITMENTS_PRESENTATION_SPEC.md` (v0.5.2 — v2.4.3 hegemony-aligned; §8.1a owns the bloc-naming contract folded from the retired Block 3 audit; non-normative bulk trimmed per v2.4.2 deep-audit C7; Slice C trims cut spotlight-tier card variant, split-voice `attributed_lines[]`, N+1 Talleyrand aside), `docs/COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` (historical), `docs/DIPLOMAT_VOICE_BIBLE.md`, `commitments_routing.py`, `diplomatic_templates.py`, `notifications.py`, `notification_bar.gd`, `dispatch.py`. Any `speaker="envoy"` / `speaker="foreign_office"` template MUST resolve through `resolve_named_diplomat()` or chancery fallback per Voice Bible. Live notice families include treaty breach, hard-reject posture, Make Amends, Balance of Europe, DG-4 call-to-arms, witness strike, and paradox popup/resolution metadata. |
| Diplomat voice (register rules per named diplomat) | `docs/DIPLOMAT_VOICE_BIBLE.md`, `backend/models/diplomat.py` (cast = Talleyrand, Castlereagh, Hardenberg, Metternich, Einsiedel). Read Voice Bible BEFORE authoring any new line for a named foreign diplomat. |

For detailed system docs: `docs/SYSTEMS_REFERENCE.md`
For Enemy AI details: `docs/ENEMY_AI_REFERENCE.md`

---

## Common Modification Patterns

### Adding a new action

1. Add to `VALID_ACTIONS` in `validation.py` (single source of truth for LLM)
2. Add `_execute_[action]()` in the appropriate sub-executor (see file reference table)
3. Add to `valid_actions` list in `parser.py`
4. Add cost to `_action_costs` in `world_state.py`
5. Add keywords to mock parser in `llm_client.py` (search "ADD NEW ACTION KEYWORDS HERE" — do not trust line numbers)
6. Add few-shot example in `prompt_builder.py` if complex
7. If triggerable by objection, add to `objection_actions` in `disobedience.py`
8. Add to_dict/from_dict if new state fields needed
9. Add to `ACTION_DISPLAY` in `display_names.py`
10. Add to `_DEFIANCE_DISPLAY` + `_OBJECTION_DISPLAY` in `campaign_log.py` (lines ~21, ~43)
11. Add event type to `CAMPAIGN_LOG_TYPES` in `campaign_log.py` (line ~83) + format in `format_event_oneliner()`
12. Add a golden-corpus entry in `tests/data/parser_golden_corpus.json` (CR-1) — the eval harness's action-coverage gate fails CI for any mock-reachable action with zero corpus coverage

### Adding a new marshal state

1. Add field to `marshal.py __init__`
2. Add to `to_dict()` and `from_dict()` (with `.get()` default)
3. Process in `world_state.py _process_tactical_states()` if per-turn
4. Add blocking logic in `executor.py` if it prevents actions
5. Run `pytest tests/test_serialization_enforcement.py -v`

### Adding a new popup/dialog

```
Backend → Frontend data flow:
  sub-executor → main.py → api_client.gd → main.gd
```

1. Sub-executor (e.g., `meta_executor.py`, `combat_executor.py`): Return field in result dict
2. `main.py`: Add early return to pass through the field (most common wiring gap!)
3. `main.gd`: Check for field in `_on_command_result()`
4. Create dialog scene (.tscn) and script (.gd) — assign unique layer in 101-118 range
5. **R16:** Register in `main.gd _ready()` via `dialog_manager.register()` — set `modal=true` (default) for blocking dialogs, `modal=false` for HUD elements
6. **R4:** All POST handlers use `build_base_response()` which structurally guarantees popup passthroughs. No manual `_include_popup_passthroughs()` calls needed.

**Test with curl BEFORE assuming Godot is broken:**
```bash
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
```

**SERIALIZATION WARNING:** Executor results contain `new_state` (WorldState with circular refs). Strip `new_state` before embedding in API responses.

### Adding a new combat modifier

1. Add state field to `marshal.py __init__`
2. Apply in `marshal.py get_attack_modifier()` or `get_defense_modifier()` ONLY
3. Add message in `combat.py` (DO NOT recalculate modifier)
4. Clear state in `combat.py` if consumable (AFTER get_*_modifier call)

---

## Serialization Enforcement (MANDATORY)

**"If it exists on the object, it must serialize."**

For ANY new field on ANY model class:
1. Add to `to_dict()` method
2. Add to `from_dict()` method (with `.get(key, default)`)
3. Run: `pytest tests/test_serialization_enforcement.py -v`
4. Update `docs/SAVE_FORMAT_REFERENCE.md`

Serializable classes: Marshal, StrategicOrder, StrategicCondition, WorldState, Region, Trust, AuthorityTracker, VindicationTracker, RegionIntel

---

## Strategic Commands

Strategic orders (MOVE_TO, PURSUE, HOLD, SUPPORT) cost 2 AP (1 for literal). Key patterns:

- **Tactical objection:** `world.pending_objection` — for per-action objections
- **Strategic objection:** `world.pending_strategic_objection` — for order-issuance objections (different field!)
- **Strategic execution flag:** `command["_strategic_execution"] = True` skips AP cost + objections
- **Cancel:** "cancel/halt/stop/abort" → `_execute_cancel()`, costs 1 AP

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| State cleared too early | Get value, use it, THEN clear (e.g. drill/shock bonus) |
| "No objection pending" | Strategic uses `pending_strategic_objection`, not `pending_objection` |
| Post-objection "Unknown action" | `_execute_post_objection` must handle all actions + strategic routing |
| Enemy AI crash | `game_state` must be dict `{"world": WorldState}`, not WorldState directly |
| Internal names in frontend | Use `display_names.py` maps (R7) — never raw action/state/personality strings. Import from `backend.display_names`, not original files |
| Response key mismatch | curl test the endpoint to verify key names match what Godot reads |
| None crash on parse field | Guard `.lower()`/`.strip()` — parser may return None for optional fields |
| `.get('key', '')` returns None | Use `(d.get('key') or '')` — `.get()` default only applies for MISSING keys, not `None` values |
| Objection on impossible action | Pre-validate BEFORE objection check — see bypass hierarchy in executor.py |
| AP error after objection proceed | AP must be checked in pre-validation BEFORE objection fires, not after |
| Data cleared before capture | Save per-turn lists (e.g. mild_concerns) BEFORE calling advance_turn |
| "build" parsed as drill | Mock parser keyword order matters — "build " must be checked BEFORE "train" (substring in "training") |
| Fog leaks enemy info | Filter to PARTIAL+ visibility for attack suggestions, move destinations, event reports |
| PURSUE/SUPPORT path error | `order.target` is marshal name — resolve to `target_marshal.location` before pathfinding |
| Godot null "pressed" on startup | `@onready` node paths must match FULL scene tree in .tscn — verify intermediate nodes |
| Vassal loyalty unexpected | Check `nation_relations` default — France/Saxony=40, adds +2/turn via relation//20 modifier |
| AP clause wrong nation | `from_nation` is the penalized nation (loses AP), not `to_nation` |
| "Talleyrand awaiting" stuck state | Only hard-stop dialogues block commands. Check `dialogue_manager.py` HARD_STOP_TYPES |
| New diplomatic state missing | Add to `post_break_map` in diplomacy.py AND `validate_transition()` |
| Popup not showing after early return | Use `build_base_response()` or `_build_result_response()` — they structurally guarantee popup passthroughs (R4) |
| Popup not showing after endpoint | Use `build_base_response()` for ALL POST handlers. Only `/command` main path (enemy_phase deferral) calls `_include_popup_passthroughs()` directly |
| New dialogue type shows in terminal | **TWO things:** (1) Add dtype to `main.gd:697` whitelist so Godot shows popup. (2) If dialogue concludes with a result, set `world.proposal_result_popup` so outcome shows as popup. See PL-14 fix |
| Raw internal keys in popup text | Use display maps (FEEDBACK_STRINGS, DEFIANCE_TYPE_DISPLAY, PROPOSAL_TYPE_DISPLAY) — never expose raw component/enum keys to players |
| Fog leak — player sees fogged enemies | Use `world.get_visible_enemies(nation)` for player-facing queries (R5). `get_enemies_of_nation()` is omniscient — only for combat/AI/mechanics |
| Region attribute returns default silently | Region uses `income_value` (not `income`) and `adjacent_regions` (not `connections`). Check `region.py` for exact names |

---

## Don't Do

- Add features outside current phase scope
- Change port without updating api_client.gd
- Make executor LLM-dependent (keep deterministic)
- Store API keys in code (use .env)
- Skip serialization for new fields
- Bypass executor for state changes
- Run objection evaluation before action validation (check bypass hierarchy in executor.py)
- Show raw internal action names to players (use `_ACTION_DISPLAY_NAMES` translation)
- Use `.get('key', default)` when value may be `None` — use `(d.get('key') or default)` instead
- Skip AP check before objection evaluation — player should never see objection then AP failure
- Use `get_enemies_of_nation()` for player-facing queries — use `get_visible_enemies()` instead (R5). `get_enemies_of_nation()` is omniscient and leaks fog
- Add a new nation without updating `NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY` in `diplomatic_templates.py`
- Iterate `world.regions.values()` in hot paths — use `get_active_nations()` (cached), `get_nation_regions()` instead
- Use `[world.player_nation] + list(world.enemy_nations)` — use `world.get_active_nations()` instead

---

## Commands

**IMPORTANT (Windows/WSL):** Use Windows-style paths with the venv Python. Unix-style `python -m pytest` silently fails on this WSL setup.

```bash
# Backend
".venv\Scripts\python.exe" -m backend.main    # Runs on port 8005 (MUST be -m module form post-cutover)

# Tests (MUST use Windows paths — see note above)
cd "C:\Users\User\PycharmProjects\project-sovereign-map"
".venv\Scripts\python.exe" -m pytest tests/ -v                          # Full suite
".venv\Scripts\python.exe" -m pytest tests/ -v --tb=no -q              # Quick count
".venv\Scripts\python.exe" -m pytest tests/test_objection_v2.py -v     # V2 tests only

# Coverage
".venv\Scripts\python.exe" -m pytest tests/ --cov=backend --cov-report=term-missing -v --tb=no -q

# Lint
ruff check backend/                     # Check for issues
ruff check backend/ --fix               # Auto-fix safe issues

# Validate mod
".venv\Scripts\python.exe" -m backend.modding.validator path/to/mod.json
```

---

## Document Map

| Need | Read |
|------|------|
| Session state / what's next | `docs/STATUS.md` |
| **Wave 6 fun-factor build (ACTIVE — take slices in order)** | **`docs/WAVE6_FUN_FACTOR_SPEC.md`** (approved July 10, 2026; audit evidence in `docs/audits/CREATIVE_AUDIT_2026_07_10.md`) |
| **Open bugs (consolidated)** | **`docs/BUG_FIXES.md`** |
| **Design refinement items** | **`docs/DESIGN_REFINEMENT.md`** |
| Phase timeline | `docs/ROADMAP.md` |
| Game systems (combat, trust, disobedience, LLM, cavalry, strategic) | `docs/SYSTEMS_REFERENCE.md` |
| Enemy AI decision tree | `docs/ENEMY_AI_REFERENCE.md` |
| Combat specs (V2b, Multi-Marshal, Tactical Triangle) | `docs/V2B_DEFIANCE_SPEC.md`, `MULTI_MARSHAL_SPEC.md`, `TACTICAL_TRIANGLE_SPEC.md` |
| Diplomacy specs (system, coalition, wizard, suggestions, jealousy) | `docs/DIPLOMACY_SPEC.md`, `COALITION_SPEC.md`, `DIPLOMACY_BUTTON_SPEC.md`, `TALLEYRAND_SMART_SUGGESTIONS_SPEC.md`, `JEALOUSY_SPEC.md` |
| Memory and Pressure (substrate + presentation) | `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v2.4.3), `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` (v0.5.2 C3-lite hegemony-aligned; §8.1a owns bloc-naming contract post-Block-3 fold), `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` (historical) |
| Peace Deals (umbrella + sub-specs) | **COMPLETE July 2, 2026** — routing: `docs/ROADMAP.md` §Current Phase Queue + `docs/STATUS.md`. Live: Slice H draft spec (`SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md`, user gate pending) + Gate 4 visual half. Normative: `SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6, `SETTLEMENT_GUIDED_TERMS_SPEC.md` v0.2, `SETTLEMENT_UI_CLEANUP_SPEC.md` v0.32; `SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md` owns the surviving ledger rows. Historical anchors: `PEACE_DEALS_UMBRELLA_SPEC.md`, `BILATERAL_PEACE_HARDENING_SPEC.md`, `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`, `WAR_BARGAIN_SPEC.md` (LANDED April 2026), `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` + its implementation plan. |
| Diplomat voice bible / playtest | `docs/DIPLOMAT_VOICE_BIBLE.md`, `COMMITMENTS_PLAYTEST_SCRIPT.md` |
| UI specs (top bar, fog) | `docs/TOP_BAR_SPEC.md`, `FOG_OF_WAR_SPEC.md` |
| Save format / serialization | `docs/SAVE_FORMAT_REFERENCE.md` |
| Adding content / modding | `docs/ADDING_CONTENT.md`, `MODDING_FORMAT.md` |
| Vision, future design, manual tests | `docs/VISION.md`, `FUTURE_DESIGN.md`, `MANUAL_TEST_PLAN.md`, `TUTORIAL_SCRIPT.md` |
| Architecture (audit + refactoring) | `docs/ARCHITECTURE_AUDIT_REPORT.md`, `ARCHITECTURE_AUDIT_SPEC.md`, `ARCHITECTURE_REFACTORING_PLAN.md` |
| **Component-by-component audit playbook (fix-as-you-find)** | **`docs/AUDIT_GUIDELINE.md`** |
| Archived specs & session history | `docs/archive/` |

## Documentation Rules

**If you changed behavior, update the doc that describes it.** Session ends → STATUS.md. Phase completed → ROADMAP.md + STATUS.md. System changed → SYSTEMS_REFERENCE.md. New fields → SAVE_FORMAT_REFERENCE.md.

**Deferred work must have a HOME and a LANDING.** Any item marked hidden, cut, deferred, later, v2, polish, or backlog must name its owner spec/row, landing slice, completion definition, STATUS tracking line, and behavior test in the same table or bullet. If no owner row or landing slice exists, create that contract before implementation continues. Never leave deferred work as vague "later polish," "future work," disabled placeholder copy, or an unowned player-facing promise.

CLAUDE.md "Current Phase" must always list remaining items. Completed items get brief summaries. Never mark a phase complete when items remain in ROADMAP.md.

---

## Environment

`.env`: `LLM_MODE=mock|anthropic|groq` (`groq` is an unimplemented stub — degrades to fast-parser-only; Pre-EA item), `ANTHROPIC_API_KEY` if anthropic. Server: `127.0.0.1:8005`, CORS enabled.
