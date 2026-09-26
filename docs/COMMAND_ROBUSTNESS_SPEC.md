# Command Robustness Phase ("Talk to Your Marshals")

> **Status:** v0.6 — July 5, 2026 (CR-5 scope review-hardened — see §6.7: discoverability, audience, live-only exposure). **Phase ACTIVE — user blessed scope July 3, 2026 (CR-0..CR-5; CR-6 still holds its own gate).** **CR-0 + CR-1 LANDED July 3; CR-2 + CR-3 + CR-4 LANDED July 4, 2026** (see §2 rows). **CR-5 scope BLESSED July 5, 2026 (full blessed scope in §6).** **CR-5 ✅ COMPLETE — all 4 phases LANDED July 6-7, 2026; a whole-slice adversarial + live-backend audit landed 8 more fixes July 7 (§6.10, incl. a HIGH live bug: the aggressive bad-odds interrupt was unanswerable via the popup)** (safe half → Phase 3 lethal attack-on-arrival gate → Phase 4 aggressive→engage arm). Phase 4 (July 7): the aggressive delegation re-issues a **delegation-INFERRED strategic PURSUE** (`pursue <enemy>` — a bare `attack` is not a strategic keyword and would never become tagged/gated), threading `delegation_inferred=True`; two first-step PURSUE seams Phase 3 did not cover (co-located-at-creation + move-failed) closed via `_inferred_first_step_gate`; guardrail (e) hardened to a MODE gate (mock always degrades to ASK — the bias is live-only); rider (d) "words become the record" LIVE (quarry-scoped); first-use hint latch-on-surface; failsafe flipped + tripwire rewritten; the cannon-fire redirect (autonomous Grouchy Moment) scope-boundary documented (§6.4) — it abandons the order so the gate no-ops. Two adversarial audit rounds, 5 findings fixed; 86 CR-5 tests + 3 live_only corpus rows. **CR-5b (Flavor Echoing) ✅ LANDED July 7, 2026 — entry gate CLEARED (§6.11); no user design gate needed.** CR-6 (Conversational Objection Negotiation) and anything coupling `strategic_score` to outcomes REQUIRE their own design gates per the ROADMAP LLM Mechanical Expansion rules. **The "CR-6 gate" slot was first used for the S5-D1 bare-attack mini-gate — ✅ BLESSED + LANDED July 16, 2026 (§7); the Conversational Objection Negotiation feature above remains unbuilt behind its own gate.**
> **Origin:** July 2, 2026 re-staging. Promotes ROADMAP.md's "Post-Diplomacy Command Layer Queue" (9 NEEDS-SPEC items, explicitly gated on "diplomacy refinement stable" — that condition is now met) into a numbered phase, grounded in a same-day code audit + live probe of the parse pipeline on the shipped 1805 boot.
> **Vision anchor:** This IS the game's core pillar — "you talk to your generals" — and design philosophy #4 ("Every input gets a response. No silent failures."). Golden Rule 6 boundary holds throughout: **LLM parses, executor stays deterministic.** `validate_parse_result` (`backend/ai/validation.py:141`) remains the enforcement seam.

---

## 1. Ground truth (audited July 2, 2026)

The pipeline is a 4-stage chain: fast keyword parser → optional LLM fallback (only when fast confidence < 0.7) → fuzzy-match pass → strategic-order detection. Structurally sound, but **roster-pinned to the retired legacy Waterloo world**:

- **P0 DEFECT (probe-verified, all LLM modes):** `parser.py:56` hardcodes 4 legacy player marshals; the mock parser's marshal extraction matches (`llm_client.py:610-615`). On the shipped 1805 boot, **"Soult, attack Mack" / "Lannes, move to Swabia" / "Massena, hold Milan" all fail** — 5 of the player's 7 French marshals (Soult, Lannes, Murat, Bernadotte, Massena) cannot be commanded by typed text. Worse, the failure chain hides it from the LLM: the fast parser awards 0.8 confidence for any recognized action verb (≥ the 0.7 fallback threshold), so the LLM is never consulted before the fuzzy pass hard-errors with suggestions naming marshals that don't exist in this world. Tracked in BUG_FIXES.md (upgraded from the older "dev-mode only" framing, which the probe disproved for marshal-name commands).
- `known_regions` for fuzzy/typo correction derives from legacy `REGIONS_DATA` — 19 names on a 126-province map (`parser.py:139-140`). The mock target-extraction ladder is likewise legacy-hardcoded (`llm_client.py:857-911`).
- The prompt's "Geographic layout" block describes the retired 19-region map — actively misleading the live LLM (`prompt_builder.py:393-396`).
- Only 2 tactical + 2 strategic of the 12 defined few-shot examples are actually sent; zero few-shots exist for recruit/garrison/form_square/vassal/settlement/request_terms verbs.
- Dead/unwired affordances: `parse_multiple` (multi-marshal splitting, `parser.py:612` — never called from the live path), `build_clarification_prompt` (`prompt_builder.py:638` — designed, never wired), the player-facing "Multi-marshal commands coming in a future update!" string (in `validation.py`'s `validate_parse_result`, the `len(result.marshals) > 1` block — navigate by the string; the `:195` this line once cited is `NEVER_STRATEGIC_ACTIONS` commentary, corrected September 22, 2026 — an unowned deferral this spec now owns), fuzzy-matcher Phase 3/6 TODOs incl. the autocomplete dropdown idea.
- Silent-marshal-drop class: meta-actions (`parser.py:209`) skip marshal fuzzy-matching — "Murat, charge" succeeds with `marshal=None`, silently discarding the addressee.
- Provider: `claude-3-haiku-20240307` pin (2024-generation) with brittle 3-way JSON brace-extraction; Groq is a stub returning `matched=False`.
- Context substrate already half-exists: `world.command_history` persists the last 50 structured `{raw_input, marshal, action, target, turn}` entries — currently only fed back as raw strings for repetition scoring, and only recorded in LLM mode.
- E-1 (July 2) already dynamized **nation** extraction from both live rosters — the pattern to copy for marshals/regions.

## 2. Slice plan

| Slice | Scope | Gate |
|-------|-------|------|
| **CR-0 (P0 defect fix)** — ✅ **LANDED July 3, 2026** | Dynamize parser rosters from the live world: `valid_marshals` from `world.marshals` (mirror the `_get_known_enemies(world)` pattern), `known_regions` from `world.regions`, mock target ladder from game_state. Closes the 5/7-marshal gap + the BUG_FIXES bare-command entry in one pass. Behavior tests over BOTH worlds (legacy fixture + `europe_1805.json`): `tests/test_command_robustness_cr0_parser_rosters.py` (66 tests, incl. the 4-lens adversarial-review regressions — enemy-honorific guard, punctuated targets, position-aware matching, vassal nation targets, edit-distance enemy typos, word-boundary demonyms). **Landed extras (same defect family, probe-verified):** case-tolerant `Marshal [Name]` regex ("Marshal Soult" never matched); exact-enemy-wins-before-region-fuzzy ("Mack" was rewritten to "La Mancha"); punctuation-stripped word scans ("Bernadotte," drifted to region "Bern"); nation-keyed vassal keywords from live game_state + word-scan skip fix (typed "invest in saxony" was dead in EVERY world); live-nation demonyms in strategic generic classification ("pursue the austrians" no longer becomes fake region "The Austrians"). | None (defect) |
| **CR-1** — ✅ **LANDED July 3, 2026** | Parser eval harness: golden corpus of (utterance → expected `{marshal, action, target, type, strategic}`) parameterized over both scenario worlds; runs in mock mode in CI, optionally against the live provider on demand. Seed from the ~320 existing parser tests. This is the phase's regression gate — land before behavior changes. **Shipped:** `tests/data/parser_golden_corpus.json` (233 entries — workflow-mined from the existing parser test files + authored action-coverage closers, every entry traceable via `source`; 88 entries carry `diplo` family assertions; `live_phrasing_backlog` section owns the mock-unparseable strategic phrasings as CR-3 input) + engine/CLI `backend/ai/parser_eval.py` (`-m backend.ai.parser_eval [--live]`; implicit success=True so negative expectations can never pass vacuously; `--live` refuses to run when the provider resolves to mock) + `tests/test_command_robustness_cr1_eval_harness.py` (per-entry × world matrix, corpus hygiene incl. no-dead-keys-on-failure-entries, the **action-coverage gate** — new-action checklist step 12 — and the production-payload sync pin vs `backend.main.get_llm_game_state`). **Defects fixed by first corpus run (same family):** typed `status` was dead (only `parser.valid_actions` lacked it); a live-path Unicode print CRASHED every enemy-marshal MOVE_TO parse on cp1252 consoles; 'journey' fuzzy-bound marshal=Ney at the parser word-scan (V2-55 covered only the mock layer); fogged-honorific "Attack Marshal <fogged enemy>" hard-failed (enemy-guard union + parser-side demotion); lowercase sentence words ("costs") hard-failed whole commands (capitalization-gated errors + strategic-verb skip words). **+ the IQ-9 replay tier (September 18, 2026):** the `live_only` rows run KEYLESSLY on committed cassettes — `python -m backend.ai.parser_eval --replay` (the same `evaluate_entry` loop on a parser whose Anthropic client is bound to `tests/_parser_replay.py`'s ReplayClient; exit 2 on a cassette miss) and `tests/test_iq9_keyless_parser_gate.py::TestLiveOnlyCorpusRows` in the suite; `run_corpus(..., parser=None)` keeps the default loop byte-identical. See §9. | None |
| **CR-2** — ✅ **LANDED July 4, 2026** | Confidence-gate rework + clarification dialogue. **Shipped:** (a) **marshal-aware confidence** — a leading comma-addressed name resolving to nothing drops the fast parse to 0.55 (`UNRESOLVED_ADDRESS_CONFIDENCE` < the 0.7 gate), so live mode consults the LLM BEFORE the fuzzy pass hard-errors; (b) **one forced LLM retry** (`LLMClient.reparse_with_llm`) when a confident fast parse fuzzy-errors — the "confidently wrong" class finally reaches the LLM; mock returns None (mock stays fully playable); (c) **executor-binding demotions** in BOTH extraction layers (mock scan + parser word-scan): a name in support-object position ("support ney") or inside an `until` condition clause ("hold until Ney arrives") is the supportee/condition marshal, never the executor — plus a live-parse safety net unbinding `marshal == target` on SUPPORT/PURSUE; (d) **one-question disambiguation** — new `backend/commands/clarification.py` builds "Which marshal shall …, Sire?" (marshal-less valid orders; candidates exclude the target, the condition marshal, admin/dead marshals, and — for moves — anyone already at the destination) and did-you-mean questions (addressed unknown names, from the parser's new structured `kind`/`unknown_name`/`candidates` failure fields), riding the EXISTING `awaiting_clarification` popup with per-option full **reissue `command` strings** (the Grouchy/literal + combat auto-assign emitters now carry them too — same round-trip for all surfaces); registered on the DialogueManager as LOCAL_PLANNING **`command_clarification`** (soft, never blocks, consumed by the next input, stale-cleared at turn boundary) ONLY from main.py's player path (AI commands can never create one); typed answers ("Davout" / "2" / "yes" / "cancel", edit-distance-1 tolerant) resolve deterministically pre-parse (Golden Rule 6); (e) **Berthier interception extended** — parse failures with candidates and executor `Marshal 'None'` failures now route to clarifications (before CR-2, EVERY fuzzy error fell through the executor into the generic Berthier shrug and the computed suggestions were dropped — probe-verified); Berthier prose remains the no-candidate fallback; (f) **silent-marshal-drop fixed** — meta actions (charge/recruit/build/…) with an explicitly-addressed unknown name error with candidates instead of silently discarding the addressee (interjections like "No, charge!" guarded via `ADDRESS_NON_NAME_WORDS`); (g) **sequential compound orders** — "attack Bern, then hold your positions" (previously: phantom region "Your Positions" + a stray HOLD upgrade) parses the first clause and reports the dropped tail via a Berthier warning (parser `warning`s are now actually surfaced in the response message); guards keep "march to X then attack" (attack-on-arrival) and unparseable first clauses unsplit — true conditionals stay CR-7; (h) Godot: `clarification_popup.gd` reissues option `command`s verbatim (new `clarification_command` signal; the pre-CR-2 popup leaked the backend cancel option as target "cancel"), and popup-cancel clears the backend dialogue via a guarded "never mind" round-trip (`clarification_registered` response flag). Adversarially reviewed pre-commit (5 lenses, 3-skeptic per-finding verification): 7 distinct confirmed defects ALL fixed — incl. a CRITICAL Godot null-`strategic_type` popup crash, the named-tail attack-on-arrival regression, the pursue-chooser wrong-enemy confirm, 0-AP question ordering, and interrupt-vs-answer precedence (full record: STATUS.md July 4 entry). Tests: `tests/test_command_robustness_cr2_clarification.py` (63) + 13 cr2-* corpus entries (3 pinned candidates deliberately re-pinned with behavior-change notes). | None |
| **CR-3** — ✅ **LANDED July 4, 2026** | LLM modernization. **Shipped:** (1) **model pin** `claude-3-haiku-20240307` (deprecated, retires Apr 2026) → `claude-haiku-4-5`; (2) **forced tool-use structured output** — the parse request forces a `submit_parsed_command` tool call (`PARSE_TOOL` + `tool_choice`, providers.py), so the parse arrives as already-parsed JSON and malformed-JSON failures are structurally impossible on the primary path; the 3-way brace extraction survives only as a text-block fallback; `max_tokens` 500→1000 (measured outputs ~300 — truncating the forced call surfaced as an undetectable no-parse); (3) **audit item (a)** — LLM strategic verbs (`pursue`→attack, `march`/`support`/`reinforce`→move) remap at the provider seam (`LLM_STRATEGIC_ACTION_REMAP`); the deterministic `detect_strategic_command` still owns the multi-turn upgrade (Golden Rule 6); (4) **audit item (b)** — dead `dialogue` field CUT from OUTPUT_SCHEMA + the tool schema (Flavor Echoing stays parked at the CR-5 gate, §4); (5) **audit item (c)** — new `ParseResult.llm_error` set on API-layer failure, propagated to parser.py top-level + both main.py Berthier call sites (`skip_llm`) + a `reparse_with_llm` guard: at most ONE blocking LLM call per request (was ~10s worst case stacked); token-budget comments corrected to the measured ~5K input (live usage on the 1805 boot; cost ~$0.0065/parse); (6) **audit item (d)** — `diplomatic_data["action"]` validated against `DIPLOMATIC_ACTION_ALLOWLIST` at the validate_parse_result seam AND unknown diplomatic_data fields stripped (`DIPLOMATIC_DATA_ALLOWED_FIELDS` — confirmation-gate flags like `_treaty_warning_resolved` are dialogue-response-minted, never parse-minted); cheat gate keys off the command's `key_source` ("none" = no live key armed; env fallback for hand-built dicts) closing the latent BYOK hole, and live parse results now carry the client's true key_source; (7) **prompt modernization** — retired-world geographic block replaced by per-marshal compass lines derived from live `grid_position` (`_format_geography`, same data `resolve_direction` uses); few-shots are live-roster templates (`FEW_SHOT_TEMPLATES`, 12 examples incl. previously-uncovered recruit/garrison/form_square/vassal/diplomacy/request_terms) with thin-roster guards (single-marshal worlds skip the pair example; fully-fogged worlds teach `generic` instead of retired names); the `live_phrasing_backlog` verbs documented in the strategic keyword lists (live probe: "hunt down Mack" → PURSUE ✓). **Dispositions:** `build_clarification_prompt` CUT (never wired; shipped clarification is deterministic — closes the §3 CR-2 deferral). **Verified:** `tests/test_command_robustness_cr3_llm_modernization.py` (72) + live API probe (4 calls incl. tool-use extraction, remap, request_terms diplomatic_data through the allowlist). Adversarially reviewed pre-commit (5 lenses / 15 findings; skeptic-verification stage lost to credit exhaustion, findings adjudicated manually): 5 real defects ALL fixed (live key_source provenance, empty-dict diplomatic_data kill, diplomatic_data field smuggling, tool-call truncation at 500 tokens, thin-roster retired-name grafts). | None |
| **CR-4** — ✅ **LANDED July 4, 2026 (third slice that day)** | Context carryover on the existing `command_history` substrate. **Shipped:** new `backend/commands/context_carryover.py` — (1) **Semantic reference resolution**, a deterministic PRE-parse rewrite (Golden Rule 6; the LLM is never consulted): "again"/"repeat"/"once more" repeat the last field order; "same target"/"the same place" reuse the last objective; "him"/"her"/"them" resolve to the last enemy named; "there" to the last province named (fallback: where the last-named enemy stands); "not you, Davout" re-issues the last order's action+target to another marshal (roster-matched exact/edit-1; **re-issues, does NOT auto-undo** the prior order — deterministic undo of a resolved order is unsafe, `cancel` stays the standing-order escape). A reference with nothing to resolve against gets a helpful Berthier reply, never a confusing parse failure. (2) **Persistent Command Focus** — `get_focus_marshal` + `try_focus_reissue`: a bare specific order ("hold", "move to Vienna") defaults to the last EXPLICITLY-addressed player marshal (still alive/in-field) instead of re-asking. Fires ONLY at the executor's "Marshal 'None'" seam (before the CR-2 clarification), so it never overrides an explicit marshal or a general/auto-assign order; falls through to the CR-2 "Which marshal, Sire?" when no eligible focus exists; surfaces a visible "Continuing with <marshal>" note on a clean success (an objection dominates its own surface). **Decisions of record:** history now records in BOTH mock and live modes (carryover must resolve mock-side — the live-only repetition prompt is unaffected) and each entry carries the parsed `target` (SAVE_FORMAT row updated). Focus is DERIVED from history, not a new serialized field. Carryover is skipped while a diplomatic dialogue awaits an answer (a terse "no"/"again" there is a dialogue response, not a reference; objection answers use the separate `/respond_to_objection` channel). Tests: `tests/test_command_robustness_cr4_context_carryover.py`. | None |
| **CR-5** — ✅ **SCOPE BLESSED July 5, 2026 (full scope §6)** | Personality-Biased Disambiguation — a vague **delegation verb** ("Ney, deal with Wellington") resolves to a concrete `action` through the marshal's personality. Prompt-copy on the single existing parse call (expands the generic `## Personality Rules` block, `prompt_builder.py:365-368`, into the authored verb table §6.2); zero extra LLM cost/latency; Golden Rule 6 holds (LLM sets only `action`/`strategic_type`, executor untouched). **Player-visible behavior is the full three-way split: aggressive→attack, cautious→scout, literal→ask** — Soult was reassigned cautious→literal at the July 5 gate (§6.1) so the literal "ask" arm is player-reachable (the "Grouchy asks" headline is reframed to "Soult asks"; the *dramatic* literal continue-into-disaster beat stays gated behind the autonomous Grouchy Moment, §4). Guardrails §6.3, riders §6.4, acceptance §6.5. | ✅ Scope BLESSED July 5, 2026 |
| **CR-5b** — ✅ **LANDED July 7, 2026** | **Flavor Echoing** — the marshal's IMMEDIATE spoken reply at the **response seam** echoes the player's tone ("the game heard me"), distinct from CR-5's parse seam. **Entry gate CLEARED** (§6.11): the non-parroting fallback is specifiable as a deterministic FLOOR keyed to (personality, RESOLVED action, target) — never the raw verb — so CR-5b landed as a fast-follow, no user gate. A `flavor` field rides the EXISTING CR-3 parse call (zero extra LLM call — re-adds the field CR-3 cut "parked at the CR-5 gate"); the live LLM composes an action-agnostic attitude line, and `flavor_passes_register` drops any parroting/action-naming/register-violating line to the floor. Cosmetic only (§5 non-goal holds — Golden Rule 6). `test_command_robustness_cr5b_flavor_echoing.py` (60). | ✅ Entry gate CLEARED July 7, 2026 (§6.11) |
| **CR-6 mini-gate (bare-attack gating)** — ✅ **BLESSED + LANDED July 16, 2026** | S5-D1: a bare `attack` with no marshal named auto-picked a marshal into a real battle, skipping CR-2 clarification, the W6-4 muster gate, and objections. Resolve-and-rewrite at the dispatch seam so the pick flows through the ordinary named-attack pipeline. Full record: **§7**. | ✅ Gate held + built (record §7) |
| **CR-6** (feature) | Conversational Objection Negotiation — player argues back in natural language; LLM classifies into the existing deterministic Insist/Trust/Compromise buckets with a trust modifier. Distinct from the bare-attack mini-gate above (which reused the "CR-6 gate" slot the 8.EVAL named). | **USER DESIGN GATE** (LLM picks the bucket) — still unbuilt |
| **CR-7 — "The Second Clause"** — ✅ **BUILT COMPLETE September 22, 2026 (CR-7-1..CR-7-8; landing records = the memo's §CR-7-1 and §CR-7-2..8 LANDING RECORD blocks; the queue ruling = §11.1 below)** | Conditional/compound orders. **Build contract = `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`** (8 slices, 5.0 sessions, four honest stopping points, per-slice `done_when` + kill gates); routing = `docs/STATUS.md` ▶ NEXT UP. **CR-7-1 is a P1 and is slice 1 of the queue:** a compound order whose first clause is not stand-still vocabulary **discards that clause and executes the tail** — measured **40 of 40** non-movement shapes (`Ney, fortify then attack Mack` marches Rhineland→Swabia, fights, 24,000→22,050, `fortified` still False, 1 AP, no warning), at confidence 0.95 against a 0.70 gate, so no model is ever consulted. FA-7's fix enumerated the verbs that were *reported* instead of asking whether clause 1 carries an order, so every verb outside `STAND_STILL_ALTERNATION` is still eaten. The conditional substrate is **NOT dead code** (`StrategicCondition`: 6 serialized fields, 5 typed-reachable, `_check_condition` evaluated per turn) — what is broken is what a player can SAY: **4 of 15** natural phrasings work, 2 mint phantom provinces (`till Ney arrives` → target `"Lorraine Till Ney Arrives"`), 2 mint unmeetable orders (`until relief arrives`), 4 drop silently — **all charged 2 AP**. Also owns `parse_multiple` (zero production callers) and the multi-marshal string — **which is at `validation.py:410-413`, NOT the `:195` cited twice in §2/§3 of this spec; `:195` is `NEVER_STRATEGIC_ACTIONS` commentary.** ~~Command-surface shortcuts, map-driven command context, fuzzy autocomplete dropdown UI and R158 parse-confidence display stay backlog under this row.~~ **Disposed by the CR-6 triage, September 23, 2026 (§12.5) — CR-7 closed with them still under its "backlog":** `parse_multiple` + the multi-marshal string + CQ-8 → **CRT-11**; the fuzzy autocomplete dropdown → **closed**, absorbed by row CX and built as CX-3's predictor (`COMMAND_EXPERIENCE_SPEC.md` §5, §3.3; made reachable by CX-R2); command-surface shortcuts and map-driven command context → **closed**, built as UI-6's Region Action Panel (a map click opens the province's order chips) and made honest by row CN; R158 parse-confidence display → **struck** (§12.5). | ✅ Scoped Sept 20, 2026 (memo) — per-item at phase review |
| **The CR-6 triage** — ✅ **HELD September 23, 2026 (record + build contract = §12)** | D3's dated session. It disposed every row that named "CR-6 proper", the seven intake rows and CR-7's orphans:<br>• rows are homed to slices **CRT-1 … CRT-11**, closed, or struck with a reason;<br>• it filed CQ-30 … CQ-36;<br>• **it found four P1s on one seam** — an order to retreat, a prohibition, a negative question and a refusal each carry out the OPPOSITE — and routed them as **CRT-1, AHEAD of the shippable build**. | ✅ Held (delegated grant) — CRT-1 next |

> **⛔ "CR-6 proper" IS RETIRED AS A ROUTING DESTINATION — September 20, 2026.**
> It had accumulated **47 routed rows** (`grep -c "CR-6 proper" docs/BUG_FIXES.md`)
> with no spec section, no gate and no build contract — an unowned dumping
> ground, which is exactly what Golden Rule 9 forbids. From today:
> compound/conditional members → **CR-7** (which the table above already names
> as their owner); the state-mutating members — the unbound-addressee family,
> where without a comma `Zorglub build ships` spends **400 gold** and
> `Zorglub vassalize Austria` **subjugates a great power** — → **CX-R1**, built
> at slice 2 of the queue; the remainder is triaged into a real row in the
> session **immediately after CR-7-8** (dated, not deferred).
> **Nothing new routes to "CR-6 proper"** — a new row names CR-7, CX-R, or
> files its own. **`CR-6` the FEATURE** (Conversational Objection Negotiation)
> keeps its standing USER DESIGN GATE and is untouched by this. Record +
> argument = `docs/STATUS.md` ▶ NEXT UP ruling **D3**; assurance measurements
> = `docs/audits/PARSER_AUTOFILL_ASSURANCE_2026_09_20.md`.
> **✅ THE TRIAGE WAS HELD September 23, 2026 — §12.** Every row that still named
> "CR-6 proper", the seven rows the Command-Road Queue filed to the triage and
> the two orphans CR-7 left behind now name a real slice (CRT-1 … CRT-11, or
> HC-L's L-1 session) or are closed or struck with their reason.

Deferred out (unchanged owners): anti-memorization/creative-phrasing bundle (gated behind CR-4/CR-5 per ROADMAP), Voice-to-Text (Pre-EA; rides this pipeline unchanged), Groq implementation (Pre-EA BYOK).

## 3. Absorbed owner rows (Golden Rule 9 — each source row now points here)

- BUG_FIXES.md mock-parser bare-command entry (+ its upgraded marshal-roster dimension) → CR-0
- `validation.py` multi-marshal "coming soon" string (the `len(result.marshals) > 1` block inside `validate_parse_result` — `"Multi-marshal commands coming in a future update!"`; it was at `:410-413` on September 22, 2026, NOT the `:195` this row cited twice, which is `NEVER_STRATEGIC_ACTIONS` commentary — navigate by the string) → CR-7 (still open: CQ-8) → **CRT-11** (the CR-6 triage, §12 — the string is a player-facing promise on the live road and is replaced by the relay)
- Dead `parse_multiple` / `build_clarification_prompt` / fuzzy TODOs → CR-2/CR-7 dispositions. **CR-2 disposition (July 4, 2026):** the shipped clarification dialogue is fully deterministic — `build_clarification_prompt` (prompt_builder.py:638) stays unwired; its cut-or-wire decision moves to CR-3's prompt-surface cleanup. **CR-3 disposition (July 4, 2026): CUT** — the function is deleted from prompt_builder.py (an LLM-phrased clarification question would add a blocking API call for zero mechanical gain over the deterministic builder). `parse_multiple` + the fuzzy autocomplete TODOs remain CR-7. **CR-6 triage disposition (September 23, 2026, §12.5):** `parse_multiple` → **CRT-11** (deleted by that slice unless its relay reads it); the fuzzy autocomplete → **closed** (row CX's predictor, CX-3 + CX-R2).
- DESIGN_REFINEMENT R158 (parser confidence feedback) → CR-7 → **struck by the CR-6 triage, September 23, 2026 (§12.5)**, with its re-open condition
- ROADMAP Post-Diplomacy Command Layer Queue (all 9 rows) → CR-2..CR-7
- SYSTEMS_REFERENCE §5 stays the single pipeline-behavior doc; this spec links, never duplicates.

## 4. Candidates parked for the CR-5/CR-6 gate review — DECISIONS RECORDED July 5, 2026

User direction (July 3): the text system is the pillar, not a gimmick — surface these at the same design table as the CR-5 scope blessing / CR-6 gate rather than losing them. Each row's completion definition is an accept/drop/re-home decision recorded at that review (Golden Rule 9: this section is the owner row; the gate review is the landing). **The CR-5 half of that review happened July 5, 2026 — dispositions below. The CR-6 half remains open.**

| Candidate | Sketch | Decision (July 5, 2026 CR-5 gate) |
|-----------|--------|-----------------------------------|
| **Flavor Echoing pull-forward** | ROADMAP anti-memorization bundle marks it HIGHEST PRIORITY ("the game heard me" — marshal reply echoes the player's own words). | **ACCEPTED → promoted to owned slice CR-5b** (§2 row + §6.4). NOT a CR-5 rider — it lives at the response seam, not the parse seam, and its mock-parroting failure mode needs its own design. All five Golden-Rule-9 elements recorded in §6.4; the non-parroting mock design is CR-5b's entry gate. |
| **Player's words become the record** | Persist raw phrasing on the order; quote it in campaign log / battle reports / future Gazette. `command_history` already stores raw input. | **ACCEPTED into CR-5 as rider (d)** (§6.4) — but as an explicitly-scoped, **separately-tested** sub-item (own STATUS row + own test), scoped to the inferred/delegation class only. Justified as record/legibility payoff ONLY — it does **not** discharge the anti-memorization tension (see the named gap below). |
| **Two-way channel (questions, not just orders)** | "Ney, what do you see?" / "Berthier, can we take Vienna before winter?" — military-side advisory mirroring `diplomatic_advisory.py`; deterministic fog-respecting data, LLM phrases only (Golden Rule 6 safe). | **HELD for CR-8** (unchanged) — not part of the CR-5 blessing; re-confirm at its own review. |
| **Commander-intent orders** | "Take Vienna" with no marshal named → Berthier proposes the assignment ("Lannes is closest, Sire — shall he march?"), one confirm. | **HELD as a CR-2 extension** (unchanged) — not part of the CR-5 blessing. |
| **Tone parsing** | Brusque vs. flattering vs. precise phrasing → small trust/objection modifier, personality-dependent. Same LLM-classifies-into-deterministic-buckets shape as CR-6 — shares that gate. | **HELD for the CR-6 gate** (unchanged) — mechanical (trust) effect, stays gated. |
| **Pre-battle councils** | Before a big coordinated attack, an opt-in typed exchange where marshals voice concerns — objections as a conversation you choose, not an interruption. | **HELD for its own mini-gate after CR-6** (unchanged). |
| **Autonomous "Grouchy Moment"** *(newly identified at the CR-5 gate)* | A marshal reacts to a nearby battle **without a typed order** (hears the guns → aggressive marches, cautious asks, literal continues original orders — the historical failure). Surfaced because the draft CR-5 verb table wrongly imported it as a parse row. | **RE-HOMED OUT of CR-5 — needs its own design gate outside Command Robustness.** It is an event/AI-autonomy feature, not a command-parse feature: the parser has no read access to a marshal's active `StrategicOrder` and `VALID_ACTIONS` has no continue/noop verb. "March to the sound of the guns" *as a typed order* is just an explicit move+engage and needs no personality inference. Owner: this row; landing: a dedicated marshal-autonomy gate (candidate for MC-4 / a future autonomy phase). |
| **Mechanical delegation incentive** *(newly identified at the CR-5 gate)* | Make a delegation verb ("deal with X") *mechanically* competitive with the explicit verb, not just a feel carrot (e.g. a personality-fit bonus for delegating to the right marshal, or a trust cost on explicit micro-management). | **PARKED for the CR-6/CR-7 gate.** This phase **declares delegation feel-first / mechanically-optional** (see the named gap in §6.4). Neither rider (d) nor CR-5b changes the fact that explicit verbs are mechanically dominant; that is this row's problem to own, not CR-5's. |

## 5. Non-goals

- No LLM influence on combat/mechanics outcomes (Golden Rule 6). The three ROADMAP "LLM Mechanical Expansion Path" ideas stay design-gated outside this phase.
- No phrasing **bonuses/penalties** in this phase (anti-memorization *mechanical* bundle stays gated — see the "Mechanical delegation incentive" row in §4). CR-5b Flavor Echoing is exempt: it is a **cosmetic/feel** echo with no mechanical effect, so it does not breach this non-goal.
- Mock mode remains fully playable: every slice ships mock-safe fallbacks.

---

## 6. CR-5 Blessed Scope (recorded July 5, 2026)

> **Implementation methodology (the *how*):** `docs/CR5_IMPLEMENTATION_BRIEF.md` (July 6, 2026) — a 6-phase plan, a code-verified seam map, the marshal-voice register baseline (a DEF-1 down payment), a risk register, and a Definition-of-Done checklist. This §6 remains the normative *what*; the brief refines the framing on one point (the change is **not** prompt-copy-only — the fast/mock parser short-circuits above the 0.7 confidence gate, so the mock degrade is real work). Reconcile the brief's acceptance-criteria numbering against §6.5 in the brief's Phase 0.

**Decision:** CR-5 is **BLESSED to implement now, ahead of the Marshal Content Pass.** It is a prompt-copy slice on the single existing LLM parse call: expand the generic `## Personality Rules` block (`prompt_builder.py:365-368` — currently three vague lines, no verb specificity) into the authored verb-resolution table (§6.2), wire the literal/neutral "ask" arm to the shipped CR-2 clarification, and add the guardrails (§6.3). **Golden Rule 6 holds throughout:** the LLM picks only which concrete `action` (and `strategic_type` where the verb is inherently strategic) a vague delegation verb becomes; the deterministic executor and objection layer are untouched. `validate_parse_result` (`validation.py:290`) is the enforcement seam.

**Why CR-5 before the Marshal Content Pass (sequencing rationale).** CR-5 keys off personality **type** (aggressive/cautious/literal), which is authored for all 21 marshals, piped into the parse `game_state` (`main.py:191`), rendered per-marshal into the live prompt (`prompt_builder.py:541`), and **already** load-bearing for interpretation (`executor.py:599` literal action-cost; enemy-AI attack thresholds). It does **not** depend on abilities (MC-1), skills (MC-2), or relationships (MC-3) — the thin, gated part of the roster. CR-5-first also makes MC-4's roster-skew decision **empirical** (playtested) rather than abstract. The one MC-adjacent prerequisite is the one-field personality-type audit in §6.3(d), not the content pass.

### 6.1 Player-facing truth — the "Grouchy asks" framing is corrected, and the literal arm is made player-reachable

**As originally audited:** the shipped 1805 campaign let the player command **7 French marshals: 4 aggressive (Ney, Lannes, Massena, Murat) + 3 cautious (Davout, Soult, Bernadotte), and ZERO literal/balanced/loyal** — all three literal marshals (Buxhowden, Deroy, Mack) are enemy. That would have made CR-5's signature *third* arm (literal → "ask", the most legible arm — the marshal visibly declines to guess) invisible to the player, and no French 1805 marshal is a natural literal (Grouchy himself is not in the roster).

**Decision at this gate (July 5, 2026 — user):** **Soult was reassigned `cautious → literal`** (`europe_1805.json`; his Austerlitz Pratzen assault reads as precise on-the-hour execution of the Emperor's plan — bio nudged to match). This is an MC-4 personality-coverage assignment **pulled forward** so CR-5's three-way split is player-reachable on day one, chosen over the alternatives (Davout is the best pure fit but is VISION's canonical *cautious* exemplar; Bernadotte is historically the *worst* fit). Pinned by `tests/test_europe_1805_scenario.py::test_cr5_literal_arm_player_reachable`. Therefore:

- CR-5's **player-visible** behavior is now the full **three-way split: aggressive → attack, cautious → scout, literal → ask** (aggressive: Ney/Lannes/Murat/Massena; cautious: Davout/Bernadotte; literal: **Soult**). One deliberate reassignment stands — Soult cautious→literal (above) — the **one disclosed exception** to the §6.8 character rule, made because no French marshal is a natural literal (the archetype, Grouchy/Mack, is enemy-only); MC-4 owns resolving it properly. (A brief Massena aggressive→cautious was **reverted** per that same rule — see §6.8.) Commandable split **4 aggressive / 2 cautious / 1 literal**; full-roster distribution **13 cautious / 4 aggressive / 4 literal**.
- **The headline demo is reframed** away from "Grouchy asks" (Grouchy is not in the roster) to **"Soult asks"** — a marshal the player commands.
- **Ceiling caveat (honest):** CR-5 lights up only literal's *"asks for clarification"* behavior. The *dramatic* literal payoff — the marshal who continues his original orders into disaster (the true Grouchy Moment) — is the **autonomous** feature re-homed out of CR-5 (§4) and remains gated. A literal-Soult also objects *less* than as cautious (literal "follows exactly"; per `personality.py` its trigger set is thinner), so he will execute a risky order you insist on where cautious-Davout would push back — an intended differentiation, flagged for the MC-1/MC-2 objection-content pass.

### 6.2 The verb-resolution table (authored)

**Scope:** method-free **delegation verbs** where the player hands the marshal a problem and cedes the method. **Delegation verbs:** `deal with`, `handle`, `see to`, `take care of`, `sort out`, `attend to`, `do something about` (+ obvious inflections).

**EXCLUDED** (the fast parser + CR-3 remaps already own these → base `action` + strategic upgrade; CR-5 must not claim them, or it double-owns): `march`, `advance to`, `head to`, `proceed to`, `pursue`, `chase`, `hunt`, `support`, `reinforce`, `link up`. (`llm_client.py:1008-1022` pre-empts them to `move`/`attack`; strategic upgrade happens downstream.)

**Target = enemy marshal/army** ("Ney, deal with Wellington"):

| Personality | Reads the order as | `action` (+ strategic) | Legibility tier (§6.3c) |
|-------------|--------------------|------------------------|-------------------------|
| **Aggressive** | Engage and destroy | `attack` if adjacent; else move-to-engage with attack-on-arrival (`parser.py:33-34` tail regex), or `attack`+`PURSUE` if the enemy is mobile | **Battle-starting** → evaluate_situation; objection-or-confirm if bad odds, else soft note |
| **Cautious** | Observe first, stay poised | `scout` if not adjacent; else `hold`/`defend` facing them | Soft note (+ one-tap "No, attack") |
| **Literal** | "Deal with" has no literal military reading → refuse to infer | **ASK** (CR-2 clarification: "Deal with Wellington how, Sire — attack or observe?") | Clarification |

**Target = objective/region** ("see to Vienna"):

| Personality | Reads as | `action` (+ strategic) | Tier |
|-------------|----------|------------------------|------|
| **Aggressive** | Take it | move-to + assault garrison (attack-on-arrival), `MOVE_TO` | Battle-starting if garrisoned → gate; else soft note |
| **Cautious** | Secure it carefully | move-to + `fortify`/`hold` on arrival, `MOVE_TO`/`HOLD` | Soft note |
| **Literal** | Refuse to infer | **ASK** ("Take Vienna, or garrison it, Sire?") | Clarification |

**Neutral / unknown personality** (balanced, loyal, unset, **or mock mode**) → **ALWAYS ASK.** Never guess a default action. This is the honest mock-safe fallback and the balanced/loyal-placeholder-safe behavior in one rule. (Verified mock detail: delegation verbs are wired only as *diplomatic* keywords in mock — `llm_client.py:1375` — so a marshal-addressed delegation verb drops to `unknown` → CR-2 clarification, and does **not** mis-route to the diplomatic router, which requires "talleyrand" present.)

**Target absent** ("deal with it", "handle them") → resolve "it/them/there" via **CR-4 context carryover** first, then apply the table. Nothing to resolve → clarification.

**Adjacency/distance is the executor's job, not the LLM's (Golden Rule 6).** The table's "if adjacent … else move-to-engage / scout vs hold" splits are *intent-level*: personality sets only the intent action (engage vs observe). Whether that becomes an immediate `attack` or a `MOVE_TO` + attack-on-arrival (aggressive), or a `scout` vs a `hold`/`defend` (cautious), is decided by the existing executor/strategic layer from real world geography — the LLM never needs to know adjacency and must not guess it. A biased parse emits the intent verb; the deterministic layer resolves the rest exactly as it does for explicit orders today.

**Two rows CUT from the original pitch:**

1. **The "march to the sound of the guns → literal continues standing order" row is CUT.** (a) *Unimplementable at the parse seam:* the parser has no read access to a marshal's active `StrategicOrder`, and `VALID_ACTIONS` has no continue/noop verb — the nearest, `hold`, means **stop**, the opposite of continuing. (b) *Category error:* the autonomous Grouchy Moment is an event/AI feature (§4 re-homed row), not a parse feature. The literal arm is **ASK**, full stop.
2. **"cover / watch / keep an eye on [X]" — CUT for CR-5** (fork resolved). Left out to keep the blessed scope crisp; re-add post-playtest ONLY as a named row with its own table entry + test (aggressive → scout-and-ready, cautious → scout+fortify, literal → ask). Do not half-implement.

### 6.2a Playtest evidence — the gap is real and measured (July 5, 2026)

A live feel-test playthrough (`LLM_MODE=anthropic`, 1805 opening, before any CR-5 work) empirically confirmed the gap this table closes. Same delegation verb + same target (`deal with Mack`), the three arms **all collapse to `attack`** today — personality has zero influence on the resolution:

| Command | Marshal (personality) | Observed today (pre-CR-5) | §6.2 target |
|---------|-----------------------|---------------------------|-------------|
| `Ney, deal with Mack` | Ney (Aggressive) | `attack` (+15%) | attack ✓ — *but by LLM luck, not personality logic* |
| `Davout, deal with Mack` | Davout (Cautious) | `attack` at **−10%** ("notes the risks but prepares the attack") — a frontal assault at bad odds | **scout** ✗ |
| `Soult, deal with Mack` | Soult (Literal) | `attack` (AP-blocked, but parsed to attack, **no ask**) | **ASK** ✗ |
| `Soult, deal with the situation as you see fit` | Soult (Literal) | live-LLM **drifted to `restrain`** → nonsense reply *"No pending Glorious Charge to restrain."* | **ASK** ✗ |

**Verification (CONFIRMED_IN_CODE):** mock has no personality-biased resolution — `deal with` is wired only as a *diplomatic* keyword (`llm_client.py:1375`, dead code for marshal-addressed commands, unreachable without "talleyrand" present) so mock → `unknown` → CR-2 clarification; live → the LLM guesses with no delegation-verb table, producing the drift above. This is exactly what §6.3's **temp-0 pin + action-only output + the §6.2 verb table** exist to eliminate. These four rows are the natural **before-state assertions** for the §6.5 acceptance tests. (Playtest write-up + the four *separate*, now-fixed, out-of-scope bugs it also surfaced: session of July 5, 2026; the fixes landed with `test_playtest_fixes_2026_07_05.py`.)

### 6.3 Guardrails (all blocking)

- **(a) Action-only output.** Personality may set only `action` (+ inherent `strategic_type`); never `strategic_score`, `ambiguity`, trust, or any outcome. **Enforcement is ROUTER-SIDE (deterministic), not a validation strip** (July 7 audit F4 clarified this): `route_arm`/`classify_arm` take ONLY `(personality, resolved_bool)` — they structurally cannot read an LLM `strategic_score`/`ambiguity`/`trust`, and `delegation.py` never writes any outcome field. `validate_parse_result` (`validation.py`) only range-clamps `strategic_score`/`ambiguity`; it does not personality-strip, and does not need to, because the deterministic router ignores those fields entirely. Test: `TestGuardrailAActionOnly` (router signatures cannot read outcome fields + a source-scan that the delegation module writes none).
- **(b) Temperature 0.** Pin the parse-provider temperature `0.3 → 0` (`providers.py:424`). Free post-CR-3 (forced `tool_choice` removed the JSON-robustness reason for temp > 0); global to all parses (determinism is good everywhere). Assert `temperature == 0` in the CR-1 harness. (Removes run-to-run flip on identical input; does not remove cross-prompt/model drift.)
- **(c) One-modal, objection-first legibility** (replaces the original single-tier confirm, which double-prompted against the objection layer and missed the danger case):
  - **Inferred battle-starting action** (aggressive → attack/charge/bombard): run the existing `evaluate_situation` (`executor.py:1013`). If the marshal **objects** → the objection is the gate (it already carries Trust/Insist/Compromise and states the read). Else if **odds are bad** → a lightweight CR-2 confirm ("Ney reads this as an assault on Wellington — the odds are against us. [Confirm] [No, hold]"). Else → **execute + soft note.** This catches the aggressive-suicidal-auto-attack case (aggressive marshals do **not** self-object to bad attacks) and never stacks two modals.
  - **⚠ TWO SEAMS, not one — the gate must cover attack-ON-ARRIVAL (sign-off defect, §6.8).** The bullet above gates only the *immediate/adjacent* attack. When the inferred target is **not adjacent**, an aggressive delegation resolves to `MOVE_TO`/`PURSUE` + **attack-on-arrival**, and the later-turn auto-engage runs through the strategic executor with `_strategic_execution: True`, which **bypasses the objection/`evaluate_situation` gate AND the AP cost** (CLAUDE.md: strategic execution skips both) and judges odds with a looser, **fortification-blind** strength-ratio rule (~0.7 "favorable" on raw strength). So the parse-seam confirm fires for an *adjacent* Ney but is **silent** for a delegated Massena/Murat marching two hops into a fortified superior force — the exact case (d) worries about. **Required for CR-5 to ship the attack arm:** (i) **tag the order as delegation-inferred** (an explicitly-typed strategic order stays gate-free — the player said it); (ii) when such a tagged order reaches its **attack-on-arrival**, route it through the **same** bad-odds legibility gate before it commits; (iii) make that odds read **fortification/terrain-aware**, so 42k vs a fortified 54k reads as *bad odds*, not "favorable." Without this, guardrail (c)'s headline claim holds only for adjacent targets. **Test:** a delegated aggressive marshal whose attack-on-arrival lands on a fortified superior force shows the one-modal confirm (not a silent commit).
  - **Inferred non-battle action** (cautious → scout/hold/fortify/move-to-observe): **execute + a non-blocking LOCAL_PLANNING note** carrying a one-tap reissue ("Davout will scout Wellington's approach — [No, attack instead]"), reusing CR-2's per-option `command` strings.
  - **Explicitly-typed action:** no confirm, ever.
  - **Honest naming:** the tiers are **battle-starting vs not**, NOT "reversible vs irreversible." A mis-biased scout still burns AP + a turn with no undo; the soft note makes it *legible and same-turn-correctable*, not costless — say so in the copy.
  - **Legibility IS the feature — every inferred-resolution surface NAMES the personality (required, not polish).** The confirm and the soft note must attribute the read to the marshal's *character*, not state a bare action: "Ney needs no second invitation — he **attacks**." / "Davout, cautious as ever, will **scout** first — [No, attack instead]." / "Soult won't guess your intent, Sire — **attack or observe?**". This is deterministic template copy (built from the known personality + resolved action; **not** the LLM echoing raw words — that is CR-5b), so it is mock-safe and Golden-Rule-6-safe. It is load-bearing because the personality bias is **imperceptible from a single command** — a player perceives it only via this attribution or via the cross-marshal contrast — so without the named attribution CR-5 ships *invisible* (the review blocker, §6.7). It also gives CR-5 an in-band feel payoff, making the slice independently demonstrable without waiting for CR-5b's word-echo.
  - Test: an inferred forced-unfavorable attack shows **exactly one** modal; and a test asserts the resolution surface names the acting marshal's personality.
- **(d) Personality-type pre-flight (blocking prerequisite).** Audit and freeze the 7 commandable marshals' `personality_type` assignments **before the aggressive → attack arm ships** — because that arm makes type drive an inferred, AP-committing, undo-less battle-start; a mistyped marshal silently throws an army at the enemy from a vague order. One-field review, **not** the MC content pass. (Note: this is *not* "first-time load-bearing" — personality already drives interpretation; the new risk is the *battle-starting, no-undo* dimension.) **(d) is a human sign-off checkpoint, not automated coverage** — `test_cr5_literal_arm_player_reachable` pins Soult=literal but does not certify the other 6 assignments; the freeze is a reviewer decision recorded before the attack arm merges. **✅ DONE July 5, 2026 — see §6.8** (4-lens panel: 6 keeps + the guardrail (c) attack-on-arrival fix + the "character, not situation" design rule; a brief Massena recast was reverted).
- **(e) Mock degrade — explicit + tested.** Mock cannot produce the bias; it degrades to the CR-2 clarification. Test asserts graceful degrade (never a silent wrong bias) and no mis-route to the diplomatic router.
- **Corpus regression gate (acceptance-level).** Extend the CR-1 golden corpus at the **LIVE tier**: same utterance × personality → distinct `action` — aggressive/cautious/**literal** all via the 1805 roster now that Soult is literal (Ney→attack, Davout→scout, **Soult→ask**); the legacy-Grouchy fixture stays as a secondary cross-check.

### 6.4 Rider dispositions

- **Rider (d) "Player's words become the record" — IN, as a separately-owned sub-item.** Persist raw phrasing on inferred/delegation orders and quote it verbatim in the campaign-log one-liner + battle-report attribution. Read-only over CR-4's stored `raw_input` (`world_state.py` `add_to_command_history`); pure string ops in `campaign_log.format_event_oneliner`; no LLM; mock-safe. **Own STATUS row + own behavior test** (raw phrasing appears verbatim in both surfaces, asserted in mock) — NOT under CR-5's test umbrella. Scoped to the inferred/delegation class only (do not parrot back explicit "attack Wellington"). **(d) is justified as record/legibility payoff ONLY — it does not address the anti-memorization tension; that claim is struck.**
- **Rider (a) Flavor Echoing — DEFERRED as owned slice CR-5b** (all five Golden-Rule-9 elements):
  - **Slice id / owner row:** CR-5b, §2 row (promoted from §4).
  - **Landing (seam-explicit):** marshal reply generation echoes a token/phrase from the player's raw order at the **response seam** (distinct from CR-5's parse seam); triggered on delegation/vague-verb orders; wired result → `main.py` → `main.gd`.
  - **Completion:** live mode composes a reply referencing the player's phrasing; **mock mode produces a designed non-parroting fallback** — personality-appropriate acknowledgment keyed to the *resolved action*, explicitly NOT naive insertion of the raw verb into a canned frame. The mock design is part of completion, not a TODO.
  - **STATUS line:** one line in `STATUS.md` Next Steps sequencing CR-5b immediately after CR-5.
  - **Behavior test:** live — reply contains a player-phrasing token; mock — reply is the designed fallback and **does not** contain the raw verb naively inserted (a *negative* assertion guarding the gimmick).
  - **Entry gate:** if the non-parroting mock design cannot be specified at implementation time, CR-5b routes through its own design gate — stated explicitly, never "fast-follow."
- **Named open gap (recorded, not implied).** Neither rider (d) nor CR-5b makes delegation *mechanically* competitive with explicit verbs — both are **feel** carrots. **This phase declares delegation feel-first / mechanically-optional.** A "mechanical delegation incentive" is a parked row owned by the CR-6/CR-7 gate (§4).
- **Grouchy-Moment scope boundary (Phase 4 audit, recorded + pinned).** The guardrail-(c) safety invariant ("TWO SEAMS") covers the delegation order's OWN auto-attack seams. It does **not** cover the cannon-fire redirect: an aggressive marshal who hears the guns *abandons* his current order (`_handle_interrupt` nulls `strategic_order`) to rush a different nearby battle — the **autonomous Grouchy Moment**, re-homed to its own AI-event gate (§6.3 march-to-guns cut). Because the order is nulled before the attack, the inferred gate correctly no-ops; this is identical for explicit and inferred PURSUE and is **not** a Phase-4 seam. Pinned by `TestGrouchyMomentScopeBoundary` so a future change to that behavior is deliberate. (Optional hardening — gating the redirect too — belongs to the Grouchy Moment gate, not here.)

### 6.9 Phase 4 landing record (July 7, 2026)

CR-5 Phase 4 (the aggressive→engage arm) landed with two corrections to the turnkey brief, both found by a code-verified pre-implementation seam audit and confirmed by two adversarial audit rounds:

1. **Route as `pursue <enemy>`, not `attack <target>`.** `attack` is not a strategic keyword (`strategic_parser.STRATEGIC_KEYWORDS`), so a re-issued bare `attack` stays a one-shot tactical action — never a `StrategicOrder`, so never tagged and never gated. The mock parser maps `pursue`→base action `attack` and `detect_strategic_command` upgrades `pursue <enemy marshal>`→PURSUE; the arm threads `delegation_inferred=True` onto the resulting order (via `parsed["delegation_inferred"]` → both `StrategicOrder` constructors).
2. **Two first-step PURSUE seams needed closing.** Phase 3 gated the per-turn processor (`_inferred_attack_gate` ×5) + `_handle_first_step_blocked`, but NOT the two order-*creation*-turn PURSUE seams (`_execute_strategic_command`: enemy co-located at creation, and move-failed-at-target). PURSUE routing makes them reachable, so Phase 4 closed both with `strategic_executor._inferred_first_step_gate` (single-sourcing the odds/copy from `inferred_attack_favorable` / `describe_inferred_bad_odds`).

**Live-API probe (July 7, 2026) — a key correction.** Running the four §6.2a delegation commands against the live model (`claude-haiku-4-5`) confirmed the plumbing end-to-end (mode=`anthropic`, `parse_resolved_to_action`=True, and the aggressive arm produces a tagged PURSUE) — BUT the model resolved **all three** ("Ney / Davout / Soult, deal with Mack") to `action=scout`, NOT the personality-differentiated actions AC-2 assumed. This is not a defect: CR-5 routing is **deterministic** (route_arm keys on the *marshal's* personality, not the LLM action — Ney still becomes an aggressive PURSUE despite the LLM saying `scout`), and the probe simply re-demonstrates *why* it must be (the LLM does not reliably apply the §6.2 table). Consequence: **AC-2's "distinct action in the corpus at the LIVE tier" is superseded** — the distinctness lives at the router, not the parser. The `live_only` corpus rows were corrected to assert only that the live delegation *resolves* (the precondition), with the personality split pinned deterministically at the router/endpoint tier. AC-1 (the §6.2 table IS in the prompt) still holds as authored copy; its effect is advisory.

Also hardened at this gate: **guardrail (e) is a MODE gate** — `parse_resolved_to_action` returns False for `mode=="mock"`, so a mock/fast-parser resolution (even one that incidentally resolves a keyword-bearing delegation to a real action) always degrades to ASK; the personality bias is a genuine-live-LLM feature only (§6.7 live-only exposure). **Pinned keylessly since September 18, 2026 (IQ-9, §9):** the three executed arms — aggressive → a `delegation_inferred` PURSUE with the flavor WITHHELD on the bad-odds modal, cautious → the scout clamp with the register-gated prefix, literal → ASK even when the model resolved — and the mock-mode ASK all run on authored cassettes through `POST /command` in `tests/test_iq9_keyless_parser_gate.py::TestCR5Arms`, each asserting exactly one live call. **Rider (d)** quotes the verbatim phrase only for a battle against the delegation's own quarry (`order.target==defender.name`), never an explicit charge/attack at a different enemy. Both surfaces are wired to the player: the campaign-log one-liner (baked into the backend-formatted event string Godot renders) AND the after-action battle report — the latter's `delegation_attribution` field was orphaned backend-side and is now rendered by `main.gd._display_berthier_report` (a July 7 frontend-contract audit found + closed the Golden-Rule-9 gap; the interrupt modal and delegation clarification ride the already-shipped `pending_interrupt` / `awaiting_clarification` wiring). The **first-use hint** latches on-surface (shown even when the reissued order is rejected). Audit tally: 5 confirmed findings (1 high = the mock-mode guardrail-e hole; 4 low), all fixed; completeness critic confirmed lethal-seam completeness sound. Tests: `test_command_robustness_cr5_personality_disambiguation.py` (86) + 3 `live_only` corpus rows + `parser_eval.py` `live_only` skip support.

### 6.10 Whole-slice audit landing record (July 7, 2026 — post-completion)

After CR-5 was declared complete, a whole-slice adversarial audit (9-dimension find→verify workflow + a live-backend behavioral probe against `claude-haiku-4-5`) surfaced **8 confirmed defects**, all fixed the same day with regression tests (`test_command_robustness_cr5_personality_disambiguation.py` grows 86 → 103). Full suite green (11710) + ruff clean; the three player-facing fixes re-verified live.

- **L1 (HIGH, live-only — the audit's own dimensions did not probe the interrupt-answer frontend contract).** The CR-5 aggressive-delegation bad-odds gate is the signature Phase-4 surface, but its interrupt was **unanswerable via the real UI**: the stored `pending_interrupt` dict omitted a `marshal` key, so on the SYNCHRONOUS `response.pending_interrupt` path the Godot popup (`interrupt_popup.gd` / `main.gd:3090` read `interrupt_data.get("marshal", "Marshal")`) sent the literal `"Marshal"` to `/strategic_response`, which 404'd with *"Marshal 'Marshal' not found"* — Confirm/Hold/Cancel dead. Systemic (all 5 strategic-interrupt builders omitted it; the enemy-phase report-list path masked it because those dicts carry `marshal` at top level). **Fix:** stamp `"marshal": marshal.name` on every stored `pending_interrupt` (`strategic.py`, `strategic_executor.py`, serialized so it survives save/load). Re-verified live: the interrupt now carries `Ney` and `/strategic_response` resolves. Tests: `TestInterruptCarriesMarshalName` (incl. the handle_response round-trip).
- **F1 (MED).** Comma-less address `"Marshal Soult deal with Mack"` (the most natural phrasing of the exact affordance) silently dropped the delegation — `_ADDRESS_RE` required a trailing comma. **Fix:** comma optional (`\s*,?`); the `get_marshal` validation still prevents a false delegation. `TestDelegationAddressCommaOptional`.
- **F3 (MED).** camelCase enemy KEY (`ArchdukeCharles`) leaked verbatim into ASK/cautious/bad-odds copy (R7 violation, reachable in the default mock build). **Fix:** new `display_names.humanize_entity_name` chokepoint; `_resolve_target` now matches the raw key OR its spaced form and returns a humanized display (the raw name still keys the executor), so the natural spaced form also resolves. `TestDelegationCopyHumanizesEnemyKeys`.
- **F2 (LOW).** In live mode the delegation was recorded to `command_history` with the LLM's DISTRUSTED target, poisoning later `"same target"`/`"him"`/`"again"` carryover. **Fix:** the router overwrites that entry's marshal/target with the authoritative deterministic values (no-op in mock). `TestDelegationCarryoverCorrection`.
- **F4 (LOW).** Guardrail (a) was advertised-as-tested but had no test and no personality-scoped strip. **Fix:** documented as router-side deterministic enforcement (§6.3a above) + `TestGuardrailAActionOnly`.
- **F5 (LOW).** `test_exactly_one_modal_no_stacked_objection` was vacuous (asserted an `objection` key the helper never sets). **Fix:** rewritten to assert across the real objection channels (`world.pending_objection` / `pending_strategic_objection`).
- **F6 (LOW).** The §6.2 region/objective delegation table had zero tests. **Fix:** `TestRegionObjectiveDelegation`.
- **F7 (LOW).** AC-2 corpus wording unmet by the inert `live_only` rows — corrected above (distinctness lives at the router tier).

Two audit findings were REFUTED and left as-is (correct behavior): `inferred_attack_favorable` folding only fort/terrain (not stochastic reinforcements) is spec-conformant per §6.3c(iii); the unused `BATTLE_ACTIONS` reference is a harmless clamp constant. **Verdict: CR-5 sound as shipped after these 8 fixes; no open must-fix defects.**

### 6.11 CR-5b Flavor Echoing — entry gate + landing record (July 7, 2026)

**Entry gate (§6.4 rider (a)) — CLEARED, no user design gate.** A 3-lens adversarial design panel (Napoleonic voice/craft · systems/consistency · test-design; the skeptic lens hit a tooling cap and its concerns were carried into the post-build review) adjudicated the non-parroting mock fallback **specifiable**: CR-5 already shipped its structural proof (`describe_cautious_delegation` / `describe_inferred_bad_odds` are deterministic helpers keyed to (personality, RESOLVED action, target) that never splice the raw verb), and the fallback is a bounded sibling of the same shape with a falsifiable NEGATIVE assertion (contains none of `DELEGATION_VERBS`, no action/strategic-enum token). Because the gate is specifiable, CR-5b landed as a fast-follow — **not** routed to a dedicated user gate (the §6.4 escalation condition was not met).

**Corrected framing (adopted at the gate):** guardrail (e) routes EVERY mock/fast-parser delegation — and every literal/neutral delegation — to the ASK arm, whose `_ask_question` already quotes the clause verbatim ("deal with Mack" — give battle, or observe?). So the executed aggressive/cautious arms are **LIVE-only**, and the deterministic floor is a **live-mode fallback** (fires when the live `flavor` line is empty / errored / register-dropped), not a mock surface. The ASK arm's clause-quote **is** "the game heard me" for the only path a default (mock) player reaches — so CR-5b is scoped OUT of the ASK arm (Golden-Rule-9 boundary, pinned byte-identical).

**Architecture (zero extra LLM call).** A `flavor` field is re-added to `PARSE_TOOL` (the successor to the `dialogue` field CR-3 cut "parked at the CR-5 gate"), plumbed `schemas.py ParseResult.flavor` → `to_dict`/`from_dict` → `providers.py json_to_parse_result` → the **load-bearing** `parser.py` command-dict lift → captured in `main.py` **before** the arm re-parses (which clobbers `parsed`) → attached at the response seam. Prompt-gated to delegation-only (null otherwise — preserves CR-3's token posture). The live line is **action-agnostic ATTITUDE** (it names the target + echoes tone but never a game action) so it cannot contradict the deterministic router (which the July-7 probe showed the LLM cannot be trusted to match); the deterministic CR-5 note / order-confirmation carries the authoritative deed. `delegation.flavor_passes_register` is a hard drop-to-floor gate (parroting verb / action word / personality label / internal-key leak / length / first-person-outside-quotes). Cosmetic ONLY — `flavor` is a display string, never read by routing or serialized (§5 non-goal + Golden Rule 6 hold, code-verified).

**Scope decisions of record.** (1) ASK arm untouched (above). (2) Cautious arm: the live line PREFIXES the shipped `describe_cautious_delegation` note (which keeps sole ownership of the deed) — no deterministic cautious floor, so no double-narration; the prefix is dropped if register-violating or exclamatory (cautious = measured). (3) Aggressive arm: the register-passed live line, else the deterministic floor, attached ONLY on the non-modal success path — it SKIPS the bad-odds confirm AND the objection modal (`requires_input`/`pending_interrupt`/`pending_objection`/`awaiting_response`) to preserve §6.3 one-modal legibility. (4) Rider (d) is the RECORD seam (log/report); CR-5b is the RESPONSE seam — the gate forbids the response line from repeating the verbatim clause, so no double-parrot.

**Pinned keylessly since September 18, 2026 (IQ-9, §9):** the `flavor` lift from a REAL live result, the register gate dropping a parroting line to the deterministic floor, the cautious prefix dropped on an exclamatory line, and the modal-withholding rule — `tests/test_iq9_keyless_parser_gate.py::TestCR5Arms` on authored cassettes.

**Adversarial review (3-lens find→verify).** 12 findings → **4 confirmed, all cosmetic (Golden Rule 6 held throughout the plumbing + mechanics)**, all fixed with regression tests: (1) a contraction-safe quote-span tokenizer (the naive `'[^']*'` treated every apostrophe as a delimiter, false-dropping eager in-quote lines like "'They'll…'" AND false-passing first-person narration); (2) word-boundary parroting guard (was substring — dropped "mis**handle**d"); (3) the aggressive attach now skips the objection modal shapes too; (4) a personality-label guard (a live "cautious…" line double-narrated the note's "cautious as ever"). Plus modest **floor variety** (a small template set keyed deterministically on the names) to blunt the memorization edge on the fallback path. Tests: `test_command_robustness_cr5b_flavor_echoing.py` (60). Full suite green (11770); ruff clean.

**Next: Economy Revisit (EC-0).**

### 6.5 Acceptance criteria (CR-5)

1. The §6.2 verb table is encoded as prompt copy in `## Personality Rules`; delegation verbs resolve to `action` per personality on the live parse call.
2. Same utterance × personality → distinct **behavior** (Ney→aggressive PURSUE / Davout→cautious scout / Soult→literal ask). **Distinctness is asserted at the DETERMINISTIC router tier** (`test_command_robustness_cr5_personality_disambiguation.py::TestRouteArmPhaseGate` + the arm-endpoint tests) — NOT in the corpus. Per §6.9 (Phase-4 live probe), the live model does **not** reliably apply the §6.2 table, so CR-5 routing keys on the marshal's *personality*, not the LLM's action; the 3 `live_only` corpus rows therefore assert only that a live delegation *resolves* (the precondition), never a distinct action. (July 7 audit F7 corrected this wording — the original "distinct action in the CR-1 corpus at the LIVE tier" was unmet by the corpus and is superseded by the router tier.)
3. Mock never produces a silent wrong bias: marshal-addressed delegation verb degrades to CR-2 clarification (tested); no mis-route to the diplomatic router.
4. Excluded verbs (`march`/`pursue`/`support`/`reinforce`/`head to`/…) remain owned by the fast parser + CR-3 remap (regression-asserted).
5. Guardrails (a)-(e) each have a passing test; guardrail (d) pre-flight is signed off before the aggressive→attack arm merges.
6. Rider (d) has its own STATUS row + passing mock test.
7. **Every inferred-resolution surface (confirm + soft note) names the acting marshal's personality** (§6.3c) — asserted in a test; the bias is perceptible from a single command's attribution.
8. **The delegation first-use hint** (§6.7) fires once per campaign on a delegation verb and never on an explicit verb — asserted in a test — OR its drop is explicitly recorded in §6.7.

### 6.6 Sequencing

CR-5 → CR-5b (Flavor Echoing) → then the Marshal Content Pass gate (MC-1), whose MC-4 roster-skew decision is now informed by CR-5 playtest. Codex audit targets master at the CR-5 commit SHA. **CR-5 is independently demonstrable** (the §6.3c personality-named attribution carries the in-band feel payoff), so CR-5b deepens the "the game heard me" beat but is not a prerequisite for CR-5 being playtestable.

### 6.7 Discoverability, audience & exposure (review-hardening — July 5, 2026)

A cold-eyes player review flagged that CR-5 as first blessed would ship *invisible* — a player who types explicit verbs never learns delegation exists, and the personality bias is imperceptible from one command. Three additions close that (the §6.3c personality-named attribution is the first and primary one):

- **Discoverability hint (owner + landing + test).** Beyond the §6.3c attribution, a **first-use hint** teaches that delegation exists: the first time a player issues any delegation verb in a campaign, Berthier notes it once — *"You may hand a marshal a task and let him solve it his own way, Sire — each acts to his character."* **Owner:** this row. **Landing:** CR-5 (rides the existing Berthier/response path). **Completion:** shown once per campaign, dismissible, mock-safe (static copy, no LLM). **Test:** `test_cr5_delegation_first_use_hint` (fires once, not on explicit verbs). If you choose NOT to ship the hint, that is an explicit **drop recorded here** — not silence (Golden Rule 9).
- **Audience (stated, not implied).** Delegation verbs are a **feel-first affordance for the roleplay/immersion player** — the VISION target ("anyone who's ever yelled 'why won't my general just DO what I said'"), **not** the optimizer. Explicit verbs remain mechanically dominant (the §6.4 named gap), so success is *not* universal adoption — success is that a player who talks naturally to marshals is delighted by the character-colored result. Measured on feel and legibility, not on being the optimal input.
- **Live-only exposure (honest denominator).** CR-5's personality bias is a **live-LLM feature.** The shipped default is `LLM_MODE=mock` (`.env.example`), where a delegation verb degrades to the CR-2 clarification (guardrail e) with **no bias** — default-config players are guaranteed *correct*, not *biased*, and do not see the signature behavior until they arm a key. CR-5's felt value is scoped to live/BYOK players (a legitimate Pre-EA target). This is a framing note, not a defect (the degrade is correct) — recorded so the feature's value is measured against the right player set, not "all players."

### 6.8 Guardrail (d) sign-off — personality assignments (July 5, 2026)

The `personality_type` freeze required by §6.3(d) was performed by a **4-lens panel** (Napoleonic historian, game/UX designer, systems/mechanics reviewer, skeptic) over the 7 commandable French marshals. **Outcome: 6 keeps + 1 spec fix + a design rule of record.**

> **DESIGN RULE (of record): `personality_type` = the marshal's CHARACTER / temperament — never his scenario situation, his current orders, or a patch for a mechanic.** Situation is expressed through starting position, strength, and relations; **danger is handled by guardrails (§6.3c), not by falsifying character.** (This rule was earned the hard way: the panel briefly recast an aggressive marshal to cautious to defuse a dangerous arm — falsifying the man to patch the mechanic — and it was reverted. The mechanic is the guardrail's job.)

- **Ney, Lannes, Murat (aggressive) and Davout, Bernadotte (cautious) — KEEP** (all four lenses). Ney/Lannes/Murat are textbook aggressive (impetuous infantry / bold vanguard / reckless cavalry); Davout/Bernadotte are safe cautious (methodical / hesitant). Two footnotes logged, **neither worth changing** (both fail safe under CR-5): the skeptic is right that **Davout** is the roster's *best* literal fit ("exacting, incorruptible"), and cautious is the residue of Soult owning the one literal slot; and **Bernadotte's** defining trait (political unreliability) has **no** personality type — it lives in the objection/defiance + MC-3 trust/relationship systems, not the delegation router.
- **Soult (literal) — KEEP** — the disclosed, tested reassignment (§6.1); the bio earns it and it is the *safest* CR-5 arm (asks, commits nothing). *(Superseded framing — see the MC-4 addendum at the end of this section: no longer an "exception" at all.)*
- **Massena (aggressive) — KEEP.** The panel's soft lenses first recommended recast→cautious because his bio holds the second front against a fortified, stronger Charles (54k vs 42k) and `aggressive` makes "Massena, deal with Charles" resolve to an irreversible assault. **That recommendation was rejected (and a brief recast reverted) per the design rule above:** Massena was one of Napoleon's most aggressive marshals ("dear child of victory"; he *attacked* Charles at Caldiero in 1805) — his holding role is his *situation*, not his temperament. The danger is real but it is the **guardrail's** job, not the personality's: the §6.3c attack-on-arrival fix makes an aggressive Massena safe without lying about who he was. The systems reviewer had this right from the start ("do not recast — his aggressive type is defensible; fix the guardrail"). Pinned by `test_cr5_signoff_massena_aggressive_is_his_character`. Commandable split stays **4 aggressive / 2 cautious / 1 literal**.
- **SPEC FIX — the sign-off's most important output: guardrail (c) had a hole** (§6.3c "Two seams"). (c) as first written gated only the *immediate/adjacent* inferred attack; the *non-adjacent* attack-on-arrival path — the one Massena and Murat-via-PURSUE actually travel — slips past it through `_strategic_execution: True` (bypasses the objection gate + AP cost) and a fortification-blind odds rule. Fixed in-spec: the bad-odds legibility gate must cover the attack-on-arrival seam and be fortification-aware. **This is mandatory regardless of the Massena recast** — it still exposes Murat and any future aggressive marshal delegated at a non-adjacent fortified target.

> **MC-4 ADDENDUM (July 10, 2026 — the Soult "exception" is RETIRED; the design rule holds with ZERO exceptions).** The Marshal Content Pass gate **canonized Soult-literal as his CHARACTER** (`MARSHAL_CONTENT_PASS_SPEC.md` §9): the 1805 frame is the one campaign where Soult operates under Napoleon's direct hand, and there he was the army's supreme executor — he drilled the Boulogne camps to clockwork and delivered the Pratzen assault at the exact appointed hour; his independent-command flaws and "King Nicolas" ambition belong to Spain 1809+, outside this scenario. The Marshal Content Pass gave the canonization mechanical and textual legs (the Drillmaster of Boulogne ability, the executes-to-the-letter bio line, trust 70 + the Soult–Ney −1 edge for the ambition). Accordingly, the July-5 reassignment recorded above is **no longer a disclosed exception to the design rule — it is a correct reading of the man in this scenario**, and the personality=character rule is unconditional. `test_cr5_literal_arm_player_reachable` remains the pin.

---

## §7 CR-6 mini-gate — bare-attack gating (S5-D1) ✅ BLESSED + LANDED July 16, 2026

> **This is the CR-6 gate slot's first use** (the 8.EVAL, `docs/audits/EVAL_8_2026_07_16.md` §3 item 2, pre-staged the questions here). Distinct from the *Conversational Objection Negotiation* CR-6 feature (§2 row), which stays unbuilt behind its own gate. **This section is the authoritative gate + landing record.**

### §7.1 The finding (S5-D1)

A bare `attack` with no marshal named auto-picked a marshal into a **real battle**, skipping every gate a specified attack passes through — the most ambiguous lethal order had the fewest safeguards (a post-CR-2/W6-4 inconsistency; long-standing WAD). Verified live: `_execute_general_attack` auto-commits `combat_ready[0]`; both auto paths called `_execute_attack` **without** the `command` kwarg, so the W6-4 muster gate (`command is not None`) structurally could not arm; objections key on `command["marshal"]`, which is `None`; and `build_marshal_choice_clarification` was never reached because the auto-pick "succeeded."

### §7.2 Blessed decisions (user, July 16, 2026 — over two rounds)

- **(a) Marshal pick — "Ask when >1 in contact."** A bare `attack` with more than one *commandable* marshal in enemy contact raises the "Which marshal shall lead the attack, Sire?" clarification; a single eligible marshal keeps the instant auto-pick. (Applies to the bare `general_attack` only — `auto_assign_attack` / "attack \<target\>" has a single natural pick and keeps it.)
- **(b) Muster gate — ARM it.** The bare-attack paths now carry `command`, so the W6-4 muster preview + bad-odds interrupt arm: **silent on favorable odds** (the muster rides the after-action report), **Berthier warning on non-favorable odds**. Consistency (the lazy verb behaves like the explicit one) + it surfaces the who-musters personality drama (jealousy/rivalry withholding) on lazy commands too.
- **(c) Objections — ROUTE them.** The auto-picked (or clarification-chosen) marshal passes the same objection/defiance gate a named marshal gets.
- **(d) E-CA-4 — CLOSED as subsumed by (b).** No always-on odds line. The only "pause" is the Berthier muster briefing, which is odds-gated — realistic (a chief of staff only speaks up when the odds are questionable; there is no pause before a clearly-winning attack).

### §7.3 Implementation — resolve-and-rewrite at the dispatch seam

`CommandExecutor.execute` calls the new `CombatExecutor.resolve_auto_attack(command, world, raw_input)` **after** the AP pre-check (AP-first ordering preserved) and **before** the objection block, for a PLAYER `general_attack` / `auto_assign_attack` only. It returns one of:

- **`clarify`** → `build_contact_attack_clarification` (`clarification.py`) for >1 commandable marshal in enemy contact; each option reissues a fully-formed `"<marshal>, attack <enemy>"` and registers on the existing `main.py:1738` clarification seam (typed-answer channel + popup, zero new Godot).
- **`named`** → **rewrites the command in place** to a specific `attack` (`type="specific"`, `marshal`, `target`). From there the order is indistinguishable from a typed `"<marshal>, attack <enemy>"` — so the **entire** named-attack pipeline applies: the objection block evaluates the picked marshal (c), `_execute_attack` receives `command` and arms the muster gate (b), and the AP / autonomous / fortified checks all run. **Zero lines changed in the ~170-line objection block.**
- **`passthrough`** → leaves the command for `_execute_general_attack` / `_execute_auto_assign_attack` (move-toward / no-enemies / error cases, byte-unchanged).

**GR5 carve-out:** guarded to `not is_ai_command and not is_strategic_execution and not _autonomous_execution`. AI / strategic-execution / autonomous callers never issue these command types and are excluded regardless. The resolver prefers a *commandable* marshal over an autonomous one when both are in contact (a bare "attack" reaches for whoever CAN be ordered).

**Single-sourcing (no new S5-D3 mirror):** extracted `_scan_general_attack_candidates` (shared by `_execute_general_attack` + the resolver) and `_resolve_auto_assign_attacker` (shared by `_execute_auto_assign_attack` + the resolver).

### §7.4 Test posture — no pins flipped

The gating lives at the **dispatch seam**, so the direct-call unit tests in `test_auto_assign_attack.py` (24) call the executor methods directly, bypass the resolver, and **stay green** — the "conscious pin flip" the finding anticipated turned out to be unnecessary. New behavior is pinned by `tests/test_cr6_bare_attack_gating.py` (13: resolver verdicts + full-pipeline muster (b) / objection routing (c) / clarification (a) / passthrough / GR5 guard + the Finding-1 regression below). Full suite **13,627/3**, ruff clean, no `.gd` touched.

**Pre-ship adversarial review (find→verify, 6 agents) — one real regression caught + fixed before commit:** threading `command` (which carries the raw typed text) into the rewritten named attack armed the **ESP-EV-4 guessed-target guard** (`_execute_attack`, ~`:3211`), so `attack them all` / `attack <typo-region>` were **falsely refused** ("names no foe or province our maps know") — the raw words never grounded the resolver's own pick. **Fix:** the guessed-target guard stands down for a `_auto_assigned` command — the target was resolved *deterministically* (the game chose it, the player did not type it), which is a delegation, matching the guard's own "delegated → let it fly" rule. The guard still fires for a player-typed `specific` attack (its real purpose — catching an LLM target substitution). One cosmetic fix folded (the auto-pick note no longer prepends onto a pre-battle glorious-charge prompt). Findings 3a/3b (a clarification could list a retreating marshal → honest block message; provenance drops on the objection-confirm round-trip) accepted as minor/pre-existing.

---

## §8 PARSE-NEG — sentence-shape guards ✅ LANDED August 3, 2026

**Not a CR slice and not gated** — a correctness bug found by the EA-scope
refund panel and fixed on the ROADMAP's position 0. Recorded here because this
spec owns the parse pipeline and because §8 constrains what CR-6 may assume.

**Full landing record: `docs/BUG_FIXES.md` §PARSE-NEG landing.** In one line:
the fast parser selected an action by keyword and scored its confidence by how
many identifiers it matched, never by whether the sentence meant the keyword —
so a negated order carried the *same* keywords as its affirmative, scored
HIGHER, cleared the 0.7 escalation gate and executed. `Ney, never attack Mack`
attacked; `don't declare war on Austria` declared war.

**What CR-6 inherits, and must not undo:**

1. **`backend/ai/clause_guards.py` is the single source** for the four
   sentence-shape predicates (negation, condition, stand-down, question). Any
   new consumer reads it rather than re-deriving; `parser.py` already shares
   `strip_negated_clauses` for the strategic detector.
2. **Clauses are blanked with SPACES, never spliced.** Every position-aware
   rule in the pipeline — the CR-2 executor-eligibility scan, the
   "Marshal &lt;Name&gt;" capture, the CR-2 unresolved-address demotion — indexes
   into the command text. A length-changing edit moves all of them silently.
3. **The guards are subtractive, not decisive.** They only change what text the
   existing keyword chain reads. They never pick an action. A refusal happens
   when the chain finds nothing in what survives — never because a marker was
   present.
4. **A refusal does not escalate to the LLM** (`_should_fallback_to_llm`). This
   is the one recorded deviation from the filed prescription; the reasoning is
   in the landing record and at the call site. If CR-6's gate returns *yes* on
   free-text classification, this is the boundary that gets re-opened — with
   the constraint that a model must never be able to re-derive an action the
   player explicitly forbade.
5. **Conditional orders are refused, not executed now.** `if`/`unless`/`when`/
   `once`/`after` with a real (two-word) clause issue nothing. `until` is the
   sole exception because `StrategicCondition` implements it. **The
   conditional-order system is CR-7's, and as much of it as the engine can
   hold is BUILT (September 22, 2026):** CR-7-4 made every `until` form the
   engine reads honest (`condition_grammar.py` — one vocabulary, validated
   referents, the echo), and CR-7-5 added the guard's THIRD VERDICT — a
   `when|if|once|as soon as <friendly marshal> arrives` clause behind a HOLD
   is handed off as the engine's own `until_marshal_arrives`, fails closed,
   and widens none of the nine REFUSING words. Everything else stays refused
   by this rule, and `Ney, retreat if outnumbered` stays pinned as
   accepted-not-ideal (`parseneg-retreat-if-outnumbered-executes`) — the
   two-word floor is untouched. See §11.
6. **A question routes to `help`, after diplomatic routing.** Talleyrand's
   advisory desk answers a question better than the command reference does and
   keeps precedence. A question-answering Berthier is CR-6's to build; when it
   exists, it replaces the `help` route, not the guard.

---

## §9 IQ-9 — the keyless parser gate ✅ LANDED September 18, 2026

**Owner record:** `docs/IMPROVEMENT_QUEUE_SPEC.md` §1.8 (the lead's landing
record) and `docs/SYSTEMS_REFERENCE.md` §48 (the rules). This section is the
TECHNICAL record for the parse pipeline: what the gate is, what it pins, and
the below-gate phrasing set it owns.

**The finding it answers.** The live-LLM escalation path — the 0.7 gate's
live arms, `AnthropicProvider._make_parse_request` (the `stop_reason`
truncation discard) and `_post_messages` (the typed-exception ladder the
July-18 SDK migration added) — was referenced by ZERO test files; every
"live" test stubbed ABOVE them. And the suite was keyless by per-test
discipline, not by construction: three test ids in two files built
ENV-DERIVED clients that escalated to the real API on any checkout whose
`.env` said `LLM_MODE=anthropic` (measured before the fix: 3 of 3 with
`provider_name: anthropic`; after: 0).

**The seam.** `AnthropicProvider.bind_sdk_client(client)` — the ONE
production addition (`_client()` is unchanged; it only reads the attribute
the seam sets, so live behaviour cannot change). A fake SDK client's
`messages.create(**body)` is the last line of our code before the SDK, and
exactly what the recorder wraps, so replay and record share one shape.
Replay support = `tests/_parser_replay.py`; cassettes =
`tests/data/parser_cassettes/`; recorder = `tools/record_parser_cassettes.py`
(opt-in `--record`, refuses without a key; see PLAYTESTING.md "Recording
parser cassettes").

**Rules (each measured):** a cassette miss is a `BaseException` — an
`Exception` miss is swallowed by both catch-alls into a green
`llm_error=True` fallback; the key is `(kind, utterance, world)`, never the
prompt hash (+355 chars the moment one order is in history); the suite never
records; the network guard allows loopback (asyncio's Windows self-pipe,
TestClient, the IQ-8 driver's server) and refuses everything else, including
the SDK's own transport — and the guard surfaces through the SDK as
`APIConnectionError` with the `RuntimeError` as `__cause__`, not as a bare
`RuntimeError` (recon §4.5 corrected by measurement).

**The T0 floor** (`tests/conftest.py`): `LLM_MODE=mock` as a MODULE-LEVEL
assignment (backend.main builds its parser singleton at import, before any
fixture) plus an autouse per-test pin, and the guard installed at conftest
import. The census instrument `tests/_escalation_census.py` (`-p`, never
auto-registered) re-runs the three ids under `LLM_MODE=anthropic` inside
the gate file and asserts every env-derived client is mock.

**Tiers and counts** (`tests/test_iq9_keyless_parser_gate.py`, 111 tests):
T0 suite floor (9) · seam (5) · request invariants (3) · the gate itself (2)
· A the four `live_only` corpus rows × worlds through `evaluate_entry`
unchanged (6 + the `--replay` and default-loop pins) · B the below-gate
phrasing set, parse fields AND `POST /command` dispatch (8 + 13) · CR-5 arms
+ CR-5b register gate (8) · C sixteen response shapes S1–S16 (16) · D the
nine typed API errors × {llm_error + exactly one live call, the ladder names
its cause} (18 + 1) · CR-2 retry (4) · Berthier's second call (2) · E
transport over `httpx.MockTransport` through the REAL SDK (3: 1 hit / 1 hit
/ 2 hits on a 429) · hygiene (12). **Every pin that involves the model
asserts the NUMBER of live calls.** Mutation sweep `tools/_sweep_iq9.json`,
24 rows (the recon's list), 24 killed, 0 INERT at close on a private copy —
with ONE row re-targeted: the recon's row 22 (delete the attach guard's
`pending_interrupt` clause) measured INERT BY CONSTRUCTION, because the
bad-odds modal sets `requires_input` AND `pending_interrupt` and the other
clause still guards it; the row now deletes the pair, and the R1 modal pin
kills it.

**The below-gate phrasing set (this section is its owner record;
`tests/data/parser_cassettes/phrasings.json` is the machine copy):**

| id | utterance | world | pins (measured through the real pipeline) |
|---|---|---|---|
| `below-gate-get-after` | Ney, get after Mack | 1805 | plain below-gate → attack Mack (MUSTER preview, AP 4→3); the S/E-tier phrase |
| `below-gate-keep-an-eye` | Davout, keep an eye on Mack | 1805 | scout Swabia WITHOUT the cautious clamp note |
| `backlog-make-your-way` | Lannes, make your way to Swabia | 1805 | `march` remapped to move + the deterministic MOVE_TO upgrade; a MOVE_TO order issues |
| `diplomatic-ask-austria` | ask Austria what they want | 1805 | the only diplomatic phrasing that escalates → allowlist path → the desk answers, no AP |
| `cr2-unresolved-address` | Zorglub, attack Mack | 1805 | 0.55 demotion → model `marshals: []` → **the CR-2 `unknown_name` clarification** (the addressed-token guard outranks the model; recon said "Which marshal?", corrected by measurement) |
| `demonym-harass` | Murat, harass the Austrians | 1805 | the demonym target cleared + `target_nation_hint` Austria → MUSTER vs Mack |
| `gibberish-berthier` | flurble the wibble | 1805 | `matched:false` → fast result → **Berthier's own text-mode call, the second cassette** (`.recovery`) |
| `aggressive-plain` | Ney, hit the Prussians hard | 1805 | attack + demonym Prussia → refused honestly out of reach, no AP |

Plus the corpus `live_only` rows (R1–R5: `cr5-deleg-aggressive-ney-resolves-live`,
`cr5-deleg-cautious-davout-resolves-live`, `cr5-deleg-literal-soult-asks`, the
two `fa73-live-*` twins on both worlds) and `cr2-retry-hunt-down-mack`.

**Covers / does not cover** — verbatim in `SYSTEMS_REFERENCE.md` §48.

**Routed, not fixed here (GR9, `BUG_FIXES.md` §Improvement Queue):**
**IQ9-X1** the CR-2 forced retry cannot rescue the word-scan family (the
retried marshal-less live parse is re-run through the fuzzy pass, whose
marshal word-scan re-reads 'down' → Davout; one live call, discarded; pinned
as CURRENT behaviour by `TestCR2Retry::test_retry_cannot_rescue_the_word_scan_family_today`,
owner CR-6 proper) · **IQ9-X2** the fuzzy suggestion can name a FOGGED enemy
(`_extract_enemy_marshal_names` is omniscient; R5; owner CR-6 proper) ·
**IQ9-X3** (found by this build) a failure dict carries no `mode`, so the
`parse_mode` provenance stamp reads "mock" on a request that DID make a live
call (`main.py` `_PARSE_PROVENANCE`; pinned as current behaviour by
`TestBelowGatePhrasings::test_a_live_road_failure_still_stamps_mock_provenance`).
`_StubResolvingParser`'s mode omission (recon F4) is left in place — the CR-5
file stays green on the replay tier and the stub still exercises the
deterministic clamp offline.


---

## §10 ROW CX — the typed road measured, and the question made safe ✅ LANDED September 19, 2026

**Owner record:** `docs/COMMAND_EXPERIENCE_SPEC.md` (the gate ruling, the model
ruling, the predictor's measurements and the per-slice landing records) and
`docs/SYSTEMS_REFERENCE.md` §50 (the rules). This section is the TECHNICAL
record for the parse pipeline.

**What CX adds to §8's inheritance, and must not be undone:**

1. **`is_question` is no longer lead-plus-one-signal.** Five arms, one lever
   `A_QUESTION_NEVER_ORDERS`, each grounded in a sentence that EXECUTED:
   the four subject-WH leads (`who/whom/whose/why`), the deliberative openers
   (`what about` / `how about` / `is it time to`), the leads with **no
   imperative form in English** (`is are was were am does did has had` —
   `have` deliberately excluded, the causative imperative), **the subject**
   for the leads that do have one (FA slice 7's own will/would/shall rule,
   extended and given the live roster), and an **unaddressed** line ending in
   `?`. §8's rule 3 still holds: the guards remain subtractive and never pick
   an action.
2. **`is_question` takes an optional roster** (`subjects`). Omitted — every
   caller outside the parse chain — the arm is dormant and the function is
   byte-identical to before. It is fed by `llm_client._question_subjects`:
   the player's marshals, `_askable_enemy_names` (deliberately omniscient
   about NAMES; positions are the fogged half) and the province names.
3. **`_unbound_addressee` no longer keys on the comma.** With none, the
   addressee is the leading run before the first order verb — and that run
   must contain no function word and no collective, or the polite and
   emphatic imperatives (`can you attack Mack`, `do attack Mack`) are refused
   as unknown marshals.
4. **§8 rule 6 is DISCHARGED, on its own terms.** It read: *"A question routes
   to `help`, after diplomatic routing … A question-answering Berthier is
   CR-6's to build; when it exists, it replaces the `help` route, not the
   guard."* It exists. `question_desk` answers the BOARD as well as the facts;
   a question the desk cannot take gets a ROUTER (a sentence, the surface that
   holds the answer, and the orders that would be carried out) instead of the
   12,717-character reference; and a **syntax** question keeps the reference,
   because there it is the answer (`_SYNTAX_QUESTION_RE`). The guard is
   untouched, exactly as the rule required. Five pins flipped consciously,
   each with its reason on its own row.
5. **`halt Ney` parses.** The help documented it as the twin of `cancel Ney`
   and the keyword list held every form of the word except that one.
6. **THE GAME MUST NOT OFFER A SENTENCE IT CANNOT READ**, and it is a census
   now (`tests/test_cx3_the_predictor.py`) over the completer's verb table AND
   every phrasing quoted in the COMMAND REFERENCE, run through the real parser
   **and the real executor** — because `"Davout, hold Ulm"` parses perfectly
   and the executor refuses it.

**Measured on the escalation gate, keyless:** it fires on **3.39%** of real
play, **0.00%** on a commanded campaign and **0.00%** on the chip road; **86%**
of what it catches is a sentence the corpus says must be REFUSED; **4
`live_only` corpus rows against 49 `mock_only`**; and every confident-and-wrong
defect that reproduces sits at 0.90–0.95, above the gate. **Ruling: keep
escalation and re-aim it at open-ended questions — the one road with no
deterministic answer — with the desk deterministic first because the shipped
default is `LLM_MODE=mock`.** The re-open condition is on the spec's §4.

### §10.1 The review round (CX-7) — the pipeline half

**Landing record: `COMMAND_EXPERIENCE_SPEC.md` §8.** Two pipeline facts worth
keeping here, because both are about where a rule LIVES rather than what it
says.

1. **`clause_guards` now owns "who was addressed".** `address_of` and
   `looks_like_an_address` join the four sentence-shape predicates, and
   `_ORDER_VERB_RE` — a hand-maintained list that had lived in `executor.py`
   — moves in beside them. Both the question guard and the executor read the
   one source. Row CX had shipped two rules about the same sentence in one
   commit, disagreeing about whether a comma is required; a shared predicate
   is the only thing that stops that recurring.
2. **The roster a guard matches typing against must hold the PRINTED form.**
   `_question_subjects` carried the scenario key alone, so
   `can Archduke Charles attack Mack` fought while `can Mack attack Ney`
   asked. It composes `display_names.humanize_entity_name` now. Any future
   guard that matches the player's words against a roster inherits the same
   obligation — see `SYSTEMS_REFERENCE.md` §50.12.

**Still CR-6 proper's, unchanged** *(⚠ "CR-6 proper" was RETIRED as a routing destination on September 20, 2026 — D3 in `docs/STATUS.md` ▶ NEXT UP — and conditional orders went to CR-7 and are BUILT, §11; the rest is triaged the session after CR-7-8)*: ~~conditional orders (§8 rule 5)~~, IQ9-X1,
IQ9-X2, IQ9-X3, the six real deferrals of IQ7-X7, and the three rows CX routed
(CX3-X1, CX-X1 the wh-word Cabinet backdoor, CX-X2 the corpus's blind spot) —
**plus two from the review round: L2-1** (the verb list is 27 of 40 short and
must be DERIVED from the parser's routing table, not widened a third time —
**✅ CLOSED by CX-R1, September 22, 2026, `SYSTEMS_REFERENCE.md` §51**) and
**CX7-X1** (the fuzzy near-miss guard offering `sure` → *"Did you mean
Soult?"*).

## §11 CR-7 — The Second Clause ✅ BUILT COMPLETE September 22, 2026

**Build contract and landing records = `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`** (§CR-7-1 LANDING RECORD; §CR-7-2..8 LANDING RECORD). Rules = `SYSTEMS_REFERENCE.md` §4 Stages 2a–2e. The eight slices, in one line each:

| Slice | What landed | Tests |
|---|---|---|
| CR-7-1 | a tail fuses only onto a head that can carry an arrival (40 → 0) | `test_cr7_1_the_tail_stops_eating_the_head.py` |
| CR-7-2 | the corpus harness evaluates `dropped_sequel` / `warning_contains` / `strategic_condition` / `attack_on_arrival` and REFUSES an unknown key; 15 marker rows amended + 18 `cr7-*` rows (corpus 706/706) | `test_cr7_2_the_harness_can_see_it.py` |
| CR-7-3 | **the relay** (`backend/commands/relay.py`): the tail rides EVERY arm as `dropped_sequel` + `relay_kind` + `relay_note`; handed back for the seal (`relay_command`, the client fills the line and never sends) only when coherent (`ready`); named-not-filled on `contradiction` (a fortified / squared / drilling / defensive corps told to move, a standing hold an override verb would end) and `moment` (a live march — ETA and destination named); a refused head cancels the tail (`refused_head`); behind a question it waits (`question`, a transient `world._pending_relay`, one command's life, never serialized) and is re-judged when the answer lands. The bare comma is the fifth boundary (CQ-10) with the address comma, a diplomatic head, a unit named like a verb, a refused whole sentence and emphasis all controlled; the third clause behind an arrival tail is reported. `CommandRequest.relayed` → `command_history[].relayed` (the CR-7-8 instrument) | `test_cr7_3_the_tail_comes_back.py` |
| CR-7-4 | **one condition vocabulary** (`backend/ai/condition_grammar.py`): the strip and the read are one list; `till` / `'til` / word-numbers / the honorific; referents validated (unknown / enemy / self / fallen refused at 0 AP by cause); `for 0 turns` refused; `until turn N` read as turns-from-now; `until relief arrives` = relieved; the echo names every accepted condition from the same sentence the Ledger renders (`describe_condition`) and names an unread clause ("is not a clause I can hold — the order stands without it"); the refusal split by cause (a friendly arrival never blames the enemy); `until the battle is won` reads THIS order's battle (order-scoped result first, marshal-scoped gated on `last_combat_turn >= started_turn`, stamped at both combat seams, cleared at issuance) | `test_cr7_4_the_engine_says_what_it_heard.py` |
| CR-7-5 | **the third verdict** (`clause_guards.strip_condition_clauses_with_handoff`): `when|if|once|as soon as <friendly marshal> arrives` (and a LEADING `until … ,`) behind a HOLD is handed off as `until_marshal_arrives`, fails closed (HOLD residue, friendly roster, sole condition), nine REFUSING words untouched, two-word floor untouched, refusal terminal; the pre-negation verdict (CQ-7), the trailing `should`, the comma leak. 0 of the 7 pinned refusals flip | `test_cr7_5_the_third_verdict.py` |
| CR-7-6 | **the arrival order carries its object**: `StrategicOrder.arrival_target` (declared, nested, legacy-safe) set from the parse, kept through the objection-resume rebuild, read by ONE helper `strategic.pick_contact_enemy` at the first-step, mid-path and arrival seams. Kill gate run FIRST: the first-step seam fires deterministically and engaged `enemies[0]` (Mack) when Charles was named | `test_cr7_6_the_arrival_order_carries_its_object.py` |
| CR-7-7 | the completer's `_CONTINUATIONS` (`then attack <E>` after a complete march; `until <M> arrives` / `for 3 turns` / `until relieved` after a hold), the help block "TWO ORDERS IN ONE LINE", the School's step II sentence; the repaired verb-table pin (every offered line executes on a province the marshal is NOT in — `garrison` exempted BY NAME to CX-R2/CN and proved red) | `test_cr7_7_the_completer_teaches_both_forms.py` |
| CR-7-8 | the queue retired by contract — §11.1 | `test_cr7_8_the_queue_is_retired.py` |

**Costs, decided (the user's "make sure costs … are smoothed out"):** a standing order pays ONCE at issuance (`marshal.strategic_order_ap`: 2, 1 for a literal or the sovereign) and its steps are free — `_strategic_execution` — unchanged; the one two-step order the engine holds (`march to X then attack Y`) is that one price. A relayed tail is an ordinary new command and pays its own AP when the player sends it; a tail that is NOT relayed (contradiction, moment, refused head) costs nothing because nothing is sent. A REFUSED condition costs 0 AP (before: `for 0 turns` charged 2 for a no-op). An unread clause still costs the order's price, because the order the player asked for is issued — and the echo says the clause is not held.

**Contradictions, decided (the user's note "fortify and attack is a contradiction"):** the relay never invites a contradictory tail. Contradiction is judged from the marshal's LIVE state after the head ran — fortified / in square / drilling / defensive stance told to move, or a standing HOLD / SUPPORT that an executor override verb (`attack move defend fortify drill retreat`) would end — and the note says what the tail would undo. The player may still type it; the game will not pre-fill it.

### §11.1 CR-7-8 — the cross-turn order queue is RETIRED BY CONTRACT (Golden Rule 9)

The N-step order queue held across turns is **not built, and the promise is removed, not deferred.** No player-facing surface — backend or client — offers to hold, queue, save or defer an order for a later turn (`tests/test_cr7_8_the_queue_is_retired.py`, an AST census with a sensitivity arm). The answer to "multi-step" is CR-7-3's relay plus CR-7-6's depth-1 arrival action, and no surface claims otherwise.

**The reasons are measured, not aesthetic** (memo §CR-7-8): the hook every queue design advances on, `_complete_order`, fired **once in fourteen driven turns** across three standing marches; `_break_order` fired **zero** times while two of the three orders died at one of the other **42 `strategic_order = None` sites** across 11 files — so a lapse notice hooked there would have been silent on the only real lapse; Davout stood **eleven turns** holding a live MOVE_TO and never moved; six ordinary player verbs wipe the order even on a command refused at 0 AP; `_complete_order` pays a literal marshal +5 trust, so a per-step advance through it is a trust farm; and `clause_guards.strip_deferred_clauses` already rules against it in production source (*"the engine holds no order until a later turn and inventing one would hand out free actions"*). **Re-measured September 22, 2026 on the COMMANDED 40-turn arm** (`tools/cr7_8_order_completions.py`, `commanded_full40.json`, seed `historical`): **0 completions, 0 breaks** for player marshals.

**Two re-open conditions, both instrumented:**

1. **The relay is re-sent verbatim too often.** `CommandRequest.relayed` is stamped by the client when the line it sends is the relay fill UNCHANGED, and recorded as `command_history[].relayed`. If a played campaign shows a relayed tail re-sent as-is on **more than one compound in ten** (count `relayed` entries against entries carrying a `dropped_sequel` in the same session), the relay is not answering the need and the queue is re-opened at a design gate.
2. **The churn that made it furniture has been fixed.** If `python -m tools.cr7_8_order_completions` reports player `_complete_order` fires **above 5 per 40-turn commanded arm** on the committed script, standing marches are completing often enough that a queue behind them would be reachable — re-open.

**Recorded dissent (memo §5, carried):** the relay solves silence, not memory — a five-hop march outlives the player's memory of its tail. The mitigation that binds is the `moment` kind: the tail is handed back with its moment NAMED (destination and ETA), never pre-filled. **The PARSE-NEG §8 rule 5 scope ambiguity resolves to CR-7** (above).

---

## §12 THE CR-6 TRIAGE — the retired backlog, homed ✅ HELD September 23, 2026

> **A triage, not a build — zero production code and zero tests changed.** Ruling
> D3 (`docs/STATUS.md` ▶ NEXT UP, September 20, 2026) retired "CR-6 proper" as a
> routing destination — 47 routed rows with no spec section, no gate and no build
> contract — and dated this session. Its intake: every row that still named
> "CR-6 proper"; the seven rows the Command-Road Queue filed here (CQ-17, CQ-20,
> CQ-21, CQ-24, CQ-28, CQ-29, CX-X3); and the orphans CR-7 left under its
> "backlog" when it closed (CQ-8, the multi-marshal string, `parse_multiple`, the
> autocomplete dropdown, command-surface shortcuts, map-driven command context,
> R158). **Every row now names a real slice with a done-when and a behaviour test
> (Golden Rule 9), or is closed or struck with its reason.** The slices are **CRT-1
> … CRT-11** ("Command-Road Triage"), numbered in build order. The prefix is new
> on purpose: `docs/audits/cx_recon_2026_09_19/refute_keystrokes.md` already uses
> `CX-R3`…`CX-R13` as recon ids. `CR-6` the FEATURE (Conversational Objection
> Negotiation, ROADMAP position 15) is untouched and keeps its USER DESIGN GATE.
> **The disposition of record for every row is `docs/BUG_FIXES.md`**: the
> Command-Road Queue table, and the ALL-57-VERDICTS table and routed rows of
> §Row CX. Each row carries its re-measure, its owner slice and its done-when.
> This section is the index and the build contract.

### §12.1 Method — re-measured, not re-read

Everything was re-measured at HEAD `5fec6a9c` (the docs commit after CX-R2) on a
fresh shipped 1805 board per sentence, `LLM_MODE=mock`, driven at the real
`POST /command` with the world / game_state / parser triple swapped (a probe
harness in the session's scratch directory; nothing in the repo was touched but
these documents). The intake rows and the routed CX / IQ rows were driven by hand.
The September 19 review verdicts (`docs/audits/cx_review_2026_09_19/`) were
re-driven by four read-only agents, one per family, each reproducing its rows' OWN
sentences and, where it measured a fix shape, simulating it in-process on a
patched copy. **Every P1 and every P2 that spends or leaks was re-confirmed by
hand** before it was filed. The three rows pinned as CURRENT behaviour (IQ9-X1,
IQ9-X3, IQ7-X7) were confirmed by running their pins (10 passed). The golden
corpus stands at 711/711 and moves under none of the simulated fix shapes — for
this family it is not evidence, which is why every done-when is stated at
`POST /command`.

### §12.2 What the re-measure found

1. **FOUR P1s, ONE SEAM — each makes the game carry out the OPPOSITE of what the
   player said, silently, at confidence 0.8–0.9, above the 0.70 gate, so no key
   corrects it.**
   - **CQ-32:** `Ney, retreat as they attack` fights a battle with four French
     corps. The reason clause is read as the order.
   - **CQ-34:** `Nobody retreat` orders a general retreat (−2,270 men), and `No one
     attack Mack` fights (−6,010). CX-7's collective list (`3ccf6b69`) RE-OPENED the
     plain forms.
   - **CXR1-3:** `couldn't we attack Mack` fights (−6,010). It was filed at P1 on
     September 19 and has sat under "CR-6 proper" since, with no owner and no date.
   - **CQ-35:** with a letter current, `I would not accept` SIGNS the treaty. This is
     FA-N2's class, one vocabulary gap wider.

   All four close in `clause_guards`: the negation vocabulary, the negative
   indefinites, and a subtractive reason-clause guard.
2. **Almost nothing had closed itself.** Only four rows closed since filing: L2-6
   and L2-7 (by CX7-2 and CX7-4), CX-X4 (by CN-3 + CN-4), and CQ-20 (in the shipped
   client only — the Cabinet door claims it). Everything else reproduced, most rows
   with the same figures. The desk's two modules (`question_desk.py`, `counsel.py`)
   have not changed since the review round filed them.
3. **Wider than filed:**
   - **CQ-17:** the estate arm endows the ADDRESSEE for 200 gold and an admin action,
     and no verb takes an estate back.
   - **CX-X1:** a question DOWNGRADES a real alliance for 1 DP (`why not downgrade
     relations with Spain`). The seam is the backend's `_parse_diplomatic_command`,
     which never reads the shared question verdict.
   - **CX7-X1:** 568 of 2,408 closed-class cells are claimed as a marshal's name.
   - **DESK-2:** the price quote misstates every arm; artillery is quoted too.
4. **New P2s that spend or leak:**
   - **CQ-30:** `Ney, attack Archduke Charls` fights MACK. A one-letter slip on a
     FOGGED foe's name is read as a description, while the exact name refuses
     honestly.
   - **CQ-31:** `Ney, move to London` takes 2 actions across the crossing that
     `march to London` refuses for free. FA slice 5's one issuance reader has a
     second door.
   - **CQ-33:** `with the Guard` turns a march into a 2-action hold.
   - **L2-7b:** `can Bavaria attack Mack` fights.
   - **DESK-1:** `why not attack Kutuzov` names Kutuzov's FOGGED province (a fog
     leak).
5. **Three labels have the shape "CR-6 proper" had.** None is in this intake, and
   all are recorded in §12.5 so they are not lost: "CR-8" (the advice owner), "the
   next UI slice" (predictor polish and IQ10-X1/X2), and NPC-12's wider census.

### §12.3 The slices — owned, ordered, each with its contract

**Build order:**
1. CRT-1.
2. ROADMAP position 10 (the shippable build).
3. CRT-2 … CRT-11, in order.

> **⚑ AMENDED September 23, 2026 by the pre-build review and the release plan** (the user: *"lets just release a playable game"*; routing = `STATUS.md` ▶ NEXT UP). All of these were reproduced at HEAD `289697ef`. Row GE (game end) lands first, then the release; these become the first fix updates after it.
>
> **Update 2:**
> - all of **CRT-3** ("a question never orders"): `what happens if we downgrade relations with Spain` downgrades the alliance; `could Austria retreat` orders a general French retreat; `maybe build ships` spends 400g;
> - **WO-32** (P1): the vassal-rebellion popup is lost when its order is refused.
>
> **Update 3:**
> - **CX5-L5-F2** from CRT-6: `Davout, block Mack's retreat` makes Davout retreat;
> - **CQ-30** from CRT-2: a misspelt, fogged name (`Archduke Charls`) fights Mack instead. The fix refuses free, per CRT-2's own contract.
>
> CRT-2's other rows (CQ-17, CQ-29) and CRT-4 … CRT-11 follow, in this order. Player reports may re-order them.

HC-L's L-1 may ride any session.

**Why CRT-1 goes first:** ruling D2's own rule is that a P1 which fires on ordinary
typing precedes the build (the recorded dissent: *"slices 1 and 2 alone … must
still precede the build"*). Four P1s on one seam are exactly that case.

**After the build, Round 0 evidence may re-order CRT-2 … CRT-11:** a row a tester
actually hits jumps the queue.

**Build contracts:** the per-row done-whens in `docs/BUG_FIXES.md` are the build
contracts. Each slice's commit carries the four-file gate STATUS names: the STATUS
block, the landing record (appended here as `§12.x CRT-n LANDING RECORD`),
CLAUDE.md LIVE STATE and the BUG_FIXES rows.

| # | Slice | P | Rows | Effort | Done when (headline — the rows carry the full done-when) | Pins |
|---|---|---|---|---|---|---|
| ~~**1**~~ | ~~**CRT-1 "What the sentence forbids is never the order"**~~ ✅ **LANDED September 23, 2026 — landing record §12.7** | **P1 ×4** | CQ-32, CQ-34, CQ-35, CXR1-3; CX5-L5-F1 (P2, the same guard) | 1.0–1.25 | All changes are in `clause_guards`:<br>• the modal and perfect negative contractions and `ought` / `have we` join the negation vocabulary;<br>• the negative indefinites (`nobody`, `no one`, `none`, `not a man`…) become markers and leave `_COLLECTIVE`;<br>• a SUBTRACTIVE third-party reason-clause guard (the PARSE-NEG shape: blank with spaces, never pick an action), sited after the question and condition guards and excluding wh-words and condition words.<br>Every measured sentence spends nothing and moves nothing. The controls behave exactly as today: `someone attack Mack`, `everyone retreat`, `Ney, attack Mack as he retreats`, `accept`, `I would accept`, `Davout, don't advance on our left, fortify`. **Do NOT widen `is_question`'s lead.** | `tests/test_crt1_what_the_sentence_forbids.py` + additions to `test_parse_negation.py` and `test_fa_n_p1_cluster_2026_09_02.py` |
| → | **ROADMAP position 10 — THE SHIPPABLE BUILD** | — | — | — | — | — |
| ~~**2**~~ | ~~**CRT-2 "The name is never replaced"**~~ ✅ **LANDED September 26, 2026 — CQ-30 §12.8, CQ-17 + CQ-29 §12.10** | P2 ×3 | CQ-17, CQ-29, CQ-30 | 0.75–1.0 | A name the sentence gives is the one acted on, or the order is refused free:<br>• a reward goes to its OBJECT;<br>• an unresolved province is refused with the region matcher's answer, never raised at the capital;<br>• a near miss of any roster enemy takes the ASK arm, fog-honest, while descriptions keep ESP-EV-4's disclose-and-proceed. | `tests/test_crt2_the_name_is_never_replaced.py` |
| ~~**3**~~ | ~~**CRT-3 "A question never orders"**~~ ✅ **LANDED September 26, 2026 — landing record §12.8** | P2 | CX-X1 (+ the downgrade), L2-7b, CXR1-2, CXR1-4, CXR1-5, CXR1-N2, CXR1-N3 | 1.0 | The diplomatic parser reads the shared question verdict, so a question reaches the advisory and never the chooser or a downgrade. The question arms' residue closes:<br>• the comma tail stands down only on an order verb;<br>• a hedge arm;<br>• a leading run of up to three non-order words;<br>• the comma-free address;<br>• nation subjects in `_question_subjects`. | `tests/test_crt3_a_question_never_orders.py` + `test_cx1_a_question_never_orders.py` additions |
| **4** | **CRT-4 "The road law is read where it is quoted and where it is taken"** | P2 | CQ-31, DESK-3, DESK-10 | 0.5 | `move to X` refuses exactly where `march to X` refuses. The desk's reach answer is Yes iff the march is accepted (33 → 0), and its turn count equals the driven arrival. Measure `BASELINE_SERIES` first: the move road is shared with the AI. | `tests/test_crt4_the_road_law_everywhere.py` |
| **5** | **CRT-5 "An answer is read closed"** | P2 | IQ7-X7 | 0.75 | Every dialogue family's typed answer is read by a closed per-family grammar that fails closed, so IQ7-X7's seven deferrals execute nothing and its pinned-as-current class flips. **Ruled here:** a hedged answer (`maybe accept`, `perhaps accept`) is not a plain answer and fails closed. It is one of IQ7-X7's own seven lines, and it is IQ-7's closed-grammar lesson. | `tests/test_iq7_review_round.py::TestIQ7X7TheDeferralLimitOnOtherFamilies` (flipped) + `tests/test_crt5_an_answer_is_read_closed.py` |
| **6** | **CRT-6 "The retreat is a word, not always an order"** | P2 + P3/P4 | CQ-33, CX5-L5-F2…F7, CX5-L5-N2, N4, N5 | 1.25 | • The noun rule covers the demonstratives, the possessives, `line of retreat` and the carry-out/continuative forms.<br>• `with the Guard` and `guard the retreat` are not a HOLD.<br>• `fall back now` is not a destination.<br>• `pursue Mack's retreat` pursues Mack.<br>• The "he will turn" promise appears only while nothing is committed.<br>**The F6 pins land FIRST:** the corpus is blind to this family, at 711/711 with CX-5's lever on AND off. | `tests/test_crt6_the_retreat_is_a_word.py` |
| ~~**7**~~ | ~~**CRT-7 "The desk answers what the order would do"**~~ ✅ **LANDED September 26, 2026 — landing record §12.9** | P2 ×3 + P3/P4 | DESK-1, 2, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16 (+ DESK-6's dead clause) | 1.25–1.5 | Each desk answer asks the seam that would refuse or charge the order:<br>• the what-if answer reads fog and the executor's refusals;<br>• the price reads `recruit_quote`;<br>• `who is winning` reads the war banner's rows;<br>• the counsel reads the action pools and CN-4's refusals;<br>• the router points at the right screen;<br>• our own captured or fallen marshal can be asked about;<br>• the muster prints display names (keep the diorama's keys). | `tests/test_crt7_the_desk_reads_the_order.py` |
| **8** | **CRT-8 "The Cabinet's rules hold on every road"** | P2 (keyed / API) + P3/P4 | CX-X3, CQ-36, CX-X2, CQ-20's witness | 0.5 | • A typed `make_vassal` is refused unless one of §8a's two paths is met, at `vassal_executor._execute_make_vassal`. Never in `create_vassal_conquest`: the settlement's clause and the AI rung call it legitimately.<br>• The Cabinet's break row either breaks a boot alliance through its preview or is dimmed with the executor's reason.<br>• `client_blocked` is derived from the committed redirect mirror, and the four `known_unwitnessed` family actions get witnesses. | `tests/test_crt8_the_cabinets_rules.py` + the eval-harness pin |
| **9** | **CRT-9 "The state speaks first"** | P3 | CQ-21, CQ-24, CQ-28 | 1.0 | ONE pure per-verb state probe (fortified, drill-locked, recovering, broken, zero actions), read by the battery, the payload, the completer and both chip surfaces. **CQ-28's rule, decided:** refuse the standing order at issuance, free. Measure `BASELINE_SERIES` first. A `.gd` slice, so the boot smoke is owed. | CX-R2's census with `_state_gated` deleted + CN-4's census at 0 actions + `tests/test_crt9_the_state_speaks_first.py` |
| **10** | **CRT-10 "The suggestion is honest"** | P3/P4 | CX7-X1, L2-6's residue, IQ9-X2, CX3-X1, CX3-X2, CX3-X3, CX-BEHAV-1 | 1.0 | • The word scan skips `never_an_address` words (568 → 0).<br>• A suggestion never names a fogged enemy.<br>• Ulm and Austerlitz refuse by naming Swabia and Moravia.<br>• No marshal question is staged for a destination the map lacks.<br>• A guess keeps the typed first letter.<br>• `help` and the refusals' `Example:` strings name 1805 provinces.<br>⛔ **Lands WITH or AFTER CRT-1:** without it, the word-scan fix turns `Nobody, retreat` into a general retreat. | `tests/test_crt10_the_suggestion_is_honest.py` + the `test_cx3_the_predictor` re-key |
| **11** | **CRT-11 "The second name is heard"** | P3 | CQ-8 (+ the "coming in a future update" promise, `parse_multiple`) | 0.5 | The second marshal's order is RELAYED, never spent. The muster no longer asks the player to type what he typed, and the promise string is gone from every road. | `tests/test_crt11_the_second_name_is_heard.py` |
| **HC-L** | **L-1 riders** (row 7 of the queue, unconditional) | P3/P4 | IQ9-X1, IQ9-X3 | +0.25 on L-1 | Both are live-LLM-road rows, and L-1 already opens that road and replays the IQ-9 cassettes. The retried live parse is ADOPTED when it resolves the mis-bound marshal, and a failure dict carries `mode`. Both pinned-as-current tests flip. | the two IQ-9 pins (flipped) + `tests/test_cr6_retry_rescues_the_word_scan.py` |

**Totals:** CRT-1 is 1.0–1.25 sessions before the build, and CRT-2 … CRT-11 are
≈ 8.5–9 sessions after it.

**None of these slices can move `BASELINE_SERIES` or M1–M7 by design.** Every seam
is on the typed road:
- the AI never parses text, never answers a dialogue by typing, and never reaches
  the desk;
- `guessed_target_refusal` returns early without `_raw_input`, which AI commands
  never carry.

**CRT-4 and CRT-9 touch roads the AI shares** (the move executor, the state gates).
They measure the series FIRST, and any gate the AI's road does not already carry
is filed, not flipped (CQ-22's precedent).

### §12.4 Every row, disposed (index — the full disposition is on each row in `docs/BUG_FIXES.md`)

| Row | P | HEAD re-measure (Sept 23) | Disposition |
|---|---|---|---|
| CQ-17 | P2 | LIVE, wider (estate arm irreversible) | CRT-2 |
| CQ-20 | P3 | API only; the Cabinet door claims it in the client | **CLOSED in the shipped client**; pin owed → CRT-8 |
| CQ-21 · CQ-24 · CQ-28 | P3 | LIVE (measured on CX-R2's landing HEAD) | CRT-9; CQ-28's rule decided (§12.5) |
| CQ-29 | P2 | LIVE, to the digit | CRT-2 |
| CX-X3 | P2 | LIVE over the API; keyed exposure through paraphrase | CRT-8 |
| CQ-8 (+ multi-marshal string, `parse_multiple`) | P3 | LIVE — the muster asks the player to type what he typed | CRT-11 |
| autocomplete dropdown | — | built as row CX's predictor (CX-3, CX-R2) | **CLOSED** |
| command-surface shortcuts · map-driven command context | — | built as UI-6's Region Action Panel, made honest by row CN | **CLOSED** |
| R158 parse-confidence display | — | — | **STRUCK** (§12.5) |
| IQ9-X1 · IQ9-X3 | P3/P4 | LIVE (pins pass) | HC-L L-1 riders |
| IQ9-X2 | P3 | re-homed | CRT-10 (its spending sibling is CQ-30 → CRT-2) |
| IQ7-X7 | P2 | LIVE (pins pass) | CRT-5 |
| CX7-3 | P3 | fixed for the two measured; its L2-1 remainder closed by CX-R1 | **CLOSED** |
| CX7-X1 | P4 → P3 | LIVE, far wider (568 cells) | CRT-10 |
| CX3-X1 | P3 (Ulm) / P4 | LIVE | CRT-10 |
| CX-X1 | P2 | LIVE on the backend, wider (a downgrade) | CRT-3 |
| CX-X2 | P3 → P4 | first half LIVE; chip half largely moot since CN-4 | CRT-8 |
| CX-X4 | P3 | closed by CN-3 + CN-4 | **CLOSED** |
| CX-BEHAV-1 | P3 | LIVE, wider (two refusals teach Lyon — a loop) | CRT-10 |
| CX5-L5-F1 | P2 | LIVE 8/8 | CRT-1 |
| CX5-L5-F2 … F7 | P2 … P4 | LIVE | CRT-6 |
| CX5-L5-F8 | — | working as designed | **CLOSED**; residue N5 → CRT-6 |
| CXR1-1 · L2-5 | — | closed by CX-7 | **CLOSED** |
| CXR1-2 · CXR1-4 · CXR1-5 | P2 | LIVE | CRT-3 |
| CXR1-3 | **P1** | LIVE 15/15 | **CRT-1** |
| CXR1-6 | — | refutation holds | **STRUCK** |
| DESK-1 · DESK-2 · DESK-7 | P2 | LIVE (DESK-1 a fog leak) | CRT-7 |
| DESK-3 · DESK-10 | P2 / P3 | LIVE | CRT-4 |
| DESK-4 · 5 · 8 · 9 · 11 · 12 | P3/P4 | LIVE | CRT-7 |
| DESK-6 | — | refutation holds | **CLOSED**; its dead `is_drilling` clause → CRT-7 |
| L2-1 … L2-4 | — | closed by CX-R1 | **CLOSED** (recorded September 22) |
| L2-6 · L2-7 | — | closed since CX7-2 / CX7-4 | **CLOSED**; residues → CRT-10 (L2-6) and L2-7b → CRT-3 |
| **NEW** CQ-30 · CQ-31 · CQ-33 | P2 | found here | CRT-2 · CRT-4 · CRT-6 |
| **NEW** CQ-32 · CQ-34 · CQ-35 | **P1** | found here, confirmed by hand | **CRT-1** |
| **NEW** CQ-36 | P3 | found here (the boot alliance cannot be broken) | CRT-8 |
| **NEW** DESK-13 … 16 · CXR1-N2 · N3 · CX5-L5-N2 · N4 · N5 · CX3-X2 · CX3-X3 · L2-7b | P2 … P4 | found here | per the slice table |

### §12.5 Decisions taken here (under the standing delegated grant — recorded, not gated)

1. **CRT-1 precedes the shippable build.** D2's order put position 10 next because
   *"the three P1s are dead"*. Four new ones are live on ordinary typing, all on one
   seam. Nothing else from this triage moves ahead of the build.
2. **CQ-28: refuse at issuance, free, in the lock's own words.** Three reasons:
   - a one-turn lock is the commitment the player chose;
   - a queued order is the promise §11.1 retired by contract;
   - the refusal costs one re-typed line, where the queued arm costs 2 actions for a
     turn of nothing.

   Re-open with §11.1's conditions.
3. **CQ-8: RELAY the second name, never spend it.** This follows CR-7's cost rule: a
   relayed order pays its own actions when the player seals it.
4. **CQ-20: closed in the shipped client** by the Cabinet door (G1). The API road is a
   parser fallback by standing ruling; its pin is owed to CRT-8.
5. **CX-X3 is KEPT, not closed by that same standing ruling.** The door claims only
   the sentences it can SPELL, and a keyed player's paraphrase reaches an executor
   with no rule. The rule is §8a exactly. The ledger's minor-court filter is a display
   choice and must not be imported.
6. **A hedged dialogue answer fails closed** (CRT-5's ruling, above). This is the
   ruling CXR1-4's measured shape needed.
7. **Place names.** Ulm → Swabia and Austerlitz → Moravia are AUTHORED aliases that
   REFUSE AND NAME THE PROVINCE. An alias that resolves would be discarded by the
   march/hold path's typo re-check. **Jena gets no alias:** there is no Thuringia
   province, the map's projection is ambiguous, and the game prints Jena only as a
   title-screen caption. It falls through to the honest "no such province" answer,
   without the across-Europe guess (CX3-X3).
8. **R158 is STRUCK.** The fast parser's confidence is 0.90–1.00 on every measured
   cell where the game acted on an order the player did not give (D6). Showing it
   would say the game is sure exactly when it is wrong, and the relay, the named
   refusals and the completer already carry the feedback R158 asked for. **Re-open**
   only if a CALIBRATED confidence exists (an HC-L model, with a measured
   calibration).
9. **"CR-8" is recorded, not re-owned.** It is the §4 "Two-way channel" candidate:
   its owner is §4, and its landing is the CR-6 FEATURE's gate review, where §4's own
   completion definition (accept, drop or re-home) is taken. The FACT desk is CRT-7's;
   ADVICE waits on that gate. The label names no row by itself, so anything citing
   "CR-8" means that §4 candidate and that gate.
10. **Two labels outside this intake keep "CR-6 proper"'s shape.** They are flagged,
    not re-homed, because this triage's scope was D3's label:
    - **"the next UI slice"** owns CX3-R2/R4/R5/R6/R9/R10/R11/R12, IQ10-X1 and IQ10-X2;
    - **NPC-12's wider census** has ~426 interpolations and an AST pin named as its
      completion, but no slice.

    **Dated trigger:** the next session that touches a `.gd` file names a concrete row
    for the first, and CRT-7's builder names a concrete owner for the second. Both
    are tracked in the STATUS block.

### §12.6 Re-open conditions and standing rules

- **Nothing new routes to "CR-6 proper"** (D3 stands). A new command-road row names
  a CRT slice, CR-7, CX-R, or files its own.
- **A new phrasing in a CRT slice's class is a pin in that slice's file, not a new
  row.** This applies especially to CRT-1: the negation and reason vocabulary is a
  CLASS, and the next member will be found.
- **The four-file gate applies to every CRT slice.** STATUS, this section's landing
  record, CLAUDE.md LIVE STATE and the BUG_FIXES rows all go in the same commit.

### §12.7 CRT-1 LANDING RECORD — "What the sentence forbids is never the order" ✅ LANDED September 23, 2026

**Re-measured first, on HEAD `d9745e22`,** at the real `POST /command` on a fresh
1805 boot per sentence (`LLM_MODE=mock`, the three seams swapped, a state snapshot
diffed around every line): every filed figure reproduced, and every control
behaved.

| Family | Measured before | After |
|---|---|---|
| **CQ-32** `Ney, retreat as they attack` and five siblings (`, Mack is attacking` · `because they are attacking` · `, they will attack us` · `, the Austrians are storming the bridge` · `since the enemy attacks`) | FOUGHT at Swabia — Ney, Davout, Lannes and the Emperor marched, a battle report, the Butcher's Bill; 6 of 6 | the retreat road: Ney to Lorraine at 0 AP (or an aggressive Ney objecting to the retreat), no battle, no destination bound |
| **CX5-L5-F1** `Ney, cover the retreat as they fall back` and seven siblings | RETREATED Ney at 0.9; `hold the line as they fall back` staged a MARCH onto Mack ("Mack blocks the path at Swabia") | Ney stands at Rhineland: `hold the line` holds, `fortify` reaches the fortify road, `cover the retreat` is the honest shrug; `fall back, the enemy is retreating` / `withdraw as they fall back` still retreat |
| **CQ-34** `Nobody retreat` · `Let no one retreat` · `Nobody is to retreat` · `No one attack Mack` · `None attack Mack` · `Nobody, retreat` (+8) | a GENERAL RETREAT of eight corps (−2,270); a battle (−6,010); NEY sent (`none` → Ney) | refused free, "no order goes out", nothing moved; `someone attack Mack` / `everyone retreat` / `all marshals attack` exactly as before |
| **CXR1-3** `couldn't we attack Mack` (+18 forms incl. `have we attacked Mack`, `ought we to attack Mack`, `wasn't Ney to attack Mack`, `haven't we retreated enough`) | 15 of 15 acted — a battle or a general retreat | refused free; `can you attack Mack`, `would you have Ney attack Mack`, `Ney, you should attack Mack` and **`Davout, don't advance on our left, fortify`** unchanged |
| **CQ-35** `I would not accept` (+10, incl. `I'd not accept`) with Prussia's letter current; `I would not send it` on the proposal confirm | "Treaty signed" 11 of 11; Talleyrand dispatched, 1 DP spent | the letter stays current, France–Prussia stays PEACE, 0 DP; `accept` / `I would accept` / `we could accept that` still sign, `send it` still sends |

**What was built** — the contract's three items in `backend/ai/clause_guards.py`, and
the readers the class turned out to have:

1. **The vocabulary** (`_CRT1_NEGATION_ARMS`, lever
   `WHAT_THE_SENTENCE_FORBIDS_IS_NEVER_THE_ORDER`): the modal negatives
   (`would/could/might/may/ought/need/dare + not`, contracted or not), the perfect
   (`have/has/had + not`), the past copula (`was/were + not`), the idioms of
   reluctance (`'d rather not`, `had better not`, `would sooner not`), the contracted
   auxiliaries (`'d/'ll/'re/'ve/'s + not`), the deliberative openers `ought we|i` /
   `have we|i`, and the negative indefinites (`nobody`, `no one`, `no-one`, `none`,
   `not one`, `not a man/soul/corps/…`, `no man/men/marshal/corps/…`). ONE regex
   (`_negation_re()`), read by `negation_marker_spans` and `strip_negated_clauses`
   and therefore by `dialogue_routing.text_the_player_still_means` for every
   dialogue family — which is why one list closes CQ-35 and CXR1-3 together. The
   legacy regex is kept byte-for-byte for the lever's False arm (pinned).
2. **The negative indefinites left `_COLLECTIVE`** and joined `_NEVER_AN_ADDRESS`
   (nobody is called Nobody). **The vocative comma:** a subject marker consumes a
   comma typed straight after it — `Nobody, retreat` is `Nobody retreat`. Measured
   on the first cut without that rule: the comma ended the clause at the marker and
   `retreat` stood as a general retreat.
3. **The reason-clause guard** (`strip_reason_clauses` / `reason_clause_spans`,
   lever `THE_REASON_IS_NOT_THE_ORDER`): subtractive, same-length blank, never picks
   an action. A clause is a subordinator (`as`, `because`, `since`, `now that`,
   `seeing that`) or a bare comma, then a third party (`they` / `he` / `she`, `the
   enemy` / `the Austrians` / any `the <demonym>` by morphology, or a foe on the
   roster handed in — BOTH registers, key and printed form), then a predicate (an
   auxiliary and a verb, or a hostile third-person verb). Sited AFTER the question
   and condition guards in the mock chain, so `if they attack, retreat` keeps the
   condition guard's refusal and `when Davout arrives` keeps CR-7's hand-off. `it`
   is deliberately not a subject (`Ney, it is time to attack Mack` is an order) and
   a friendly name never is (`as Davout arrives` is timing, CR-7's).

**Three readers, not one.** The blank had to reach every reader of the raw text (the
FA slice-1 lesson, again): (a) the mock chain (`llm_client`); (b) the strategic
layer's read in `parser.py` — measured, `Ney, hold the line as they fall back` read
HOLD in the chain and a MARCH onto Mack in the strategic layer; (c) the parser's
fuzzy target scan, **found while driving**: `Ney, retreat, Mack is attacking`
retreated correctly and then bound Mack as the retreat's DESTINATION ("Mack cannot
be reached, Sire — no such province is known to the staff"). `foe_names_for_guards`
(`llm_client`) supplies the roster in both registers: with the KEYS alone, `Ney,
retreat, Archduke Charles is attacking` ATTACKED him — the CX-7 through-line one
guard over.

**A sentence that is only the enemy's movements** (`as they attack`; `Ney, they are
storming the bridge`) leaves nothing to execute and is refused by NAME: a new
`refusal == "reason"` arm in `main.py` quotes the clause and asks for the order
(*"You have told me what the enemy is about, Sire — 'as they attack' — but not what
the marshal is to do about it. Nothing has been relayed"*), never the generic shrug.

**Deviations from the contract, recorded:**
- **`'d not` is CLOSED.** The row wrote it off as FA-N2's bare-`not` limit; it is a
  contraction, not a bare `not`. 11 of 11, not 10 of 11. A bare `not` stays the
  documented limit and CRT-5's closed grammar remains its backstop.
- **`ought` / `have we` are MARKERS**, as asked, so `ought we to attack Mack` wears
  the negation refusal ("no order goes out"). `is_question`'s lead is untouched. A
  bare `ought` is NOT a marker — `Ney, you ought to attack Mack` fights (pinned).
- **The comma arm requires an auxiliary or a hostile verb**, so a second marshal's
  order after a comma (`, Davout hold Swabia`) is never read as a reason clause.

**Residue, recorded not fixed:** the negation and deferral blanks are still not
applied to the parser's fuzzy target scan (pre-existing, outside this row —
`Ney, hold your position, do not attack Mack` binds a target string the hold
ignores); CRT-10's word-scan work owns that reader.

**Tests:** `tests/test_crt1_what_the_sentence_forbids.py` (103 — every family at
`POST /command` reading the WORLD, the controls, the narrowness pins, a sensitivity
class that flips each lever and shows the defect reproduce, the corpus) +
`test_parse_negation.py::TestParserBehaviour::test_a_negative_indefinite_is_a_prohibition`
(+13) + `test_fa_n_p1_cluster_2026_09_02.py::TestFAN2NegatedAnswers::test_a_modal_negated_accept_answers_nothing`
and the `send` twin (+18). **Sweep `tools/_sweep_crt1.json`: 14 mutations, 14 killed,
0 INERT, 0 BROKEN.** Corpus 711 → 723 rows (12 `crt1-*` rows), 723/723 — it was
711/711 in BOTH arms before the rows were added, so the corpus is not evidence here;
the sensitivity class is. `BASELINE_SERIES` + M1–M7 byte-identical without re-record
(63 passed), for the stated reason: the AI never parses text. Zero `.gd`. Adjacent
suites green (CR-7, CX-R1/R2, CX-1/7, FA slices 1/7, IQ-7 review, WO slice 11,
CR-2/CR-4: 2,062 passed).


### §12.8 CRT-3 LANDING RECORD — "A question never orders" ✅ LANDED September 26, 2026 (Score Mandate Chunk 3, SR-3a part (i) — with CRT-2's first pin CQ-30 and CRT-6's first pin CX5-L5-F2)

**Re-measured first, on HEAD `dc297b50`,** at the real `POST /command` on a fresh
shipped 1805 boot per sentence (`LLM_MODE=mock`, the three seams swapped, the
board read before and after): every filed figure reproduced.

| Family | Measured before | After |
|---|---|---|
| **CX-X1** `why not declare war on Prussia` · `what if we …` · `how about we …` · `why not downgrade relations with Spain` · `how about we downgrade relations with Bavaria` · `why not cool relations with Spain` · `should we court Bavaria?` | the `war_purpose_selection` chooser staged against a court at PEACE; Alliance → Defensive Alliance for 1 DP with no confirm; a courting mission staged, question mark and all | Talleyrand's ADVISORY conversation (`diplomatic_dialogue.type == "advisory"`), states and points unchanged; `Talleyrand, declare war on Prussia` still stages the chooser and `Talleyrand, court Prussia` still reaches the mission road |
| **CXR1-2** `can Ney attack Mack, Berthier` · `could Davout recruit, Berthier` · `are they going to retreat, Berthier` · `does Ney hold Rhineland, Berthier` (+2) | a muster and a battle (AP 4→3); 741 gold; a general retreat; a 2-action HOLD | the desk's answer, nothing moved; `Ney, should Mack advance, fortify` still stands the arm down (the inverted conditional keeps its refusal) |
| **CXR1-4** `perhaps build ships` · `maybe build a depot in Paris` · `worth attacking Mack` · `maybe defend` · `possibly attack Mack` · `perhaps we should release Holland` · `Ney, perhaps attack Mack` | 400 gold, a keel; 300 gold; a battle; the whole army defends | a question (the router or the desk), nothing spent; `time to march on Vienna` is NOT a hedge (the triage's ruling) |
| **CXR1-5 / CXR1-N2 / CXR1-N3** `hmm why not defend` · `just wondering why not retreat` · `I wonder why not retreat` · `tell me why not retreat` · `actually what about build ships` · `Ney why not attack Mack` · `Davout why not retreat` · `Davout how about fortify` · `hmm, why not defend` · `uh, why not retreat` | the whole army defends (1 action); a GENERAL RETREAT; 400 gold; a battle; "There is no Marshal 'hmm' in the order of battle" | a question; nothing moves; the interjection is never an officer |
| **L2-7b** `can Bavaria attack Mack` · `can Prussia retreat` · `could Russia defend` · `can the Prussians attack` · `could the Austrian army retreat` | a muster and a battle (6,010 French lost); a general retreat of eight corps; the whole army defends | a question about the court; `can you attack Mack` (the polite imperative) still marches |
| **CX5-L5-F2** `Lannes, cut off Mack's line of retreat` · `Davout, cover Ney's retreat` · `Ney, block that retreat` (+3) | the ADDRESSED marshal retreated (480 of 480 third-party cells) | he stands where he was — the shrug, or (`cover Ney's retreat`) a SUPPORT of Ney, the honest reading; his OWN retreat (`Ney, retreat`, `begin the retreat`, `sound the retreat`) still retreats |
| **CQ-30** `Ney, attack Archduke Charls` · `Ney, attack Kutusof` | "… Ney marches on Mack at Swabia, the nearest in sight" and a BATTLE AGAINST MACK | the ASK arm, fog-honest: "No foe of that name is in sight, Sire — whom shall Ney engage?" with the visible foes offered; `the weakest enemy` still discloses and proceeds; the exact `Kutuzov` still says "no intelligence" |

**Built, each behind its own lever whose down arm reproduces the row** (rules `docs/SYSTEMS_REFERENCE.md` §72.1):

- **CX-X1 — the Cabinet reads the shared verdict** (`llm_client.THE_CABINET_READS_THE_SHARED_QUESTION`). `_parse_with_mock_chain` computes `clause_guards.is_question(original_text, _question_subjects(game_state))` ONCE and hands it to every one of the twelve `_parse_diplomatic_command` call sites (`question=`); inside, the shared verdict makes the line a question and OUTRANKS the mission words (`should we court Bavaria?` is asked, not sent), so a question reaches `diplomatic_advisory` / `diplomatic_feasibility` and never the chooser, a downgrade or a mission. The client's own door had to move with it: `main.gd`'s `_is_advisory_question` gains the parser's SUBJECT RULE — a modal lead followed by a first-person subject asks (`should we …`, `can we …`) and is SENT; `will you declare war on Prussia` is the polite imperative and stays a Cabinet order; the copular and perfect leads ask whatever follows; `do` is in neither list (`do declare war` is the emphatic order). The door's Python mirror (`tests/test_wo_slice7_cabinet_door.py`) re-runs the two new lists verbatim — its "counsel is never claimed" pin is what found the door, because the backend now answers what the door used to swallow.
- **CXR1-2 — the tail stands the arms down only on an order** (`clause_guards.THE_TAIL_STANDS_DOWN_ONLY_ON_AN_ORDER`). `_trailing_clause_stands_the_arm_down(rest)`: the subject arms stand down before a trailing clause only when it OPENS with an order verb (`order_verb_re()`) — the inverted conditional's second half — never before a vocative or an aside. The filed "tail contains a verb" shape (7/10) is NOT built.
- **CXR1-4 — a hedge is a question** (`A_HEDGE_IS_NOT_AN_ORDER`, `_HEDGE_LEAD_RE`: perhaps / maybe / possibly / worth …ing / it might be worth / might as well / I suppose / I guess / I wonder if), read before the lead. `time to …` deliberately absent.
- **CXR1-5 / CXR1-N2 — a leading run hides no question** (`A_LEADING_RUN_HIDES_NO_QUESTION`, `_leading_run_hides_a_question`): when no lead matches, up to SIX leading words that are not order verbs and carry no negation marker may precede a deliberative opener (`why not`, `what about`, `how about`, `is it time to`); the run may be a name without its comma. The ceiling is six, not the row's three, because `I was just wondering why not retreat` (four) ordered a GENERAL RETREAT at the wire during the build. The bare subject-WH leads are deliberately NOT read behind a run (`Davout who is at Paris attack Mack` stays an order — the comma-free relative clause the row warned about).
- **CXR1-N3 — the interjections are never an address**: `hmm hm hmmm um umm er erm uh ah oh eh huh` join `_NEVER_AN_ADDRESS` (not `hey`, which the Ney-slip repair owns), and the parser's meta-addressee arm (`_apply_fuzzy_matching`, the `_leading_addressed_token` read for `status` / `help`) now consults `never_an_address` like every other addressee seam — it had read the hesitation as an officer because a question routes to a meta action.
- **L2-7b — a court is a subject** (`clause_guards.A_COURT_IS_A_SUBJECT`): `_question_subjects` adds the courts the parser knows plus the adjective and its plural (`Prussian`, `Prussians`); `_names_a_subject` strips a leading `the`.
- **CX5-L5-F2 — the retreat noun takes a possessive** (`llm_client.THE_RETREAT_NOUN_TAKES_A_POSSESSIVE`, `_RETREAT_NOUN_WIDE_RE`): a demonstrative, a proper possessive (`Mack's`), up to two modifiers and the "line / route / path / road / avenue of" bridge; the ORDER verbs (`sound / begin / continue the retreat`) still carry it out.
- **CQ-30 — a near miss asks** (`combat_executor.A_NEAR_MISS_ASKS`, `_near_miss_of_a_roster_name`): in `guessed_target_refusal`'s `auto_resolved` arm, a target word one typed mistake from a foreign commander's SURNAME (`parser._plausible_name_typo`, omniscient match; a token two commanders share is skipped) takes the ASK arm with a fog-honest question (`build_attack_target_clarification(..., question=)`), naming no hidden man and no hidden province; every ESP-EV-4 description still discloses and proceeds. `Kutuzof` and `Buxhowdn` were already asking through the parser's substitution arm; the row's two that FOUGHT take the new arm.

**Two pins flipped consciously, found by the families, not by the slice's own pins:** (1) `tests/test_iq7_review_round.py::TestIQ7X7TheDeferralLimitOnOtherFamilies` — `maybe accept` no longer signs Portugal's letter: a hedge is a question, and pass 3's `A_QUESTION_NEVER_ANSWERS` closes it — CRT-5's own ruling (§12.5-6) landing one line early; the class's docstring asked for exactly this flip; the five real deferrals stay pinned as current and stay CRT-5's. (2) `tests/test_wo_slice7_cabinet_door.py::TestTheMirrorAgreesWithTheParser::test_counsel_and_homeless_verbs_are_never_claimed` — red the moment the backend answered `should we declare war on Prussia` as counsel while the door still claimed it; the door and its mirror moved together (above).

**Not built here, with reasons:** the client's non-question half of CX-X1 (`what the hell, declare war on Prussia` is sent) stays the recorded P4; the door's rule is a mirror of the parser's subject rule, not a classifier. **L-D "the boolean road"** (the plan's SR-3a rider) was SKIPPED: it sits behind a user gate (`LOCAL_PARSER_FEASIBILITY_2026_09_20.md` §6.3) that this session's prompt left unfilled.

**Tests:** `tests/test_crt3_a_question_never_orders.py` (72 — every family at `POST /command` reading the WORLD, the controls, a lever-down pin per rule) + `tests/test_crt6_the_retreat_is_a_word.py` (21 — CX5-L5-F2, the file the rest of CRT-6 lands in) + `tests/test_crt2_the_name_is_never_replaced.py` (13 — CQ-30, the file CQ-17 / CQ-29 land in) + the two flipped pins. **Sweep `tools/_sweep_sr3a_i.json`: 18 mutations, 18 killed, 0 INERT** (one first reported INERT — the article strip — because the sweep spec named only the wire pins, where the article cases are refused for other reasons too; direct guard pins added, the spec re-scoped to the class, re-checked killed). Corpus 791/791 (the CR-1 harness); the parse / question / Cabinet families 6,394 green after the two flips; `BASELINE_SERIES` + M1–M7 byte-identical without re-record, for the stated reason: the AI never parses text and never carries `_raw_input`. **One `.gd` touched** (`main.gd`, the door): parse harness EXIT=0 (`tools/godot_parse_report.json` regenerated), headless boot smoke 0 `SCRIPT ERROR`.

### §12.9 CRT-7 LANDING RECORD — "The desk answers what the order would do" ✅ LANDED September 26, 2026 (Score Mandate Chunk 3, SR-3a part (ii) — with the Creative AAR's desk rows AAR-17 / AAR-19 / AAR-23 / AAR-29 / AAR-31)

**Re-measured first, at the real `POST /command` on a fresh shipped 1805 boot.** Every row reproduced: `who am I fighting and why` / `who are we at war with` / `who is at war with us` / `who are our enemies` / `is Vienna safe?` / `is Rhineland safe?` / `What does Kutuzov have with him?` / `What does Mack have with him?` / `How long until the armistice with Austria expires?` (in a truce too) / `who are my allies` → "I cannot answer that from the dispatches"; `how is the war effort` → pointed at the ECONOMY tab ("effort" contains "fort"); `what happened last turn` → "I cannot interpret that order"; `why not attack Kutuzov` → "…within reach of Kutuzov at PODOLIA" (a cell the player had never seen — DESK-1, P2); `what if I attack Deroy` → a MUSTER against our Bavarian ally, and against Mack under a truce → a MUSTER the order refuses; `how much is a gun` → "654 gold for 10,000 artillery" with no commander of guns serving, `how much is a battalion` → 654 for 10,000 where the order raises 3,000 for 741 under Davout (DESK-2, P2); `what is my income` → 3,400 + 350 − 2,630 = 1,120 against a printed Net of +1,842; `who is winning` → three even scores for ONE coalition war (DESK-7, P2); `what can I do` at 0 military actions → four orders the game refuses and no `end turn`; the boot's own counsel offering `Ney, drill`, which the game refuses ("enemy forces nearby"); `where is Ney` after his corps was destroyed → the shrug.

**The rule, built sixteen ways (each behind its own lever whose down arm reproduces the row — `SYSTEMS_REFERENCE.md` §72.2 is the rules):** the war question and its six kin (`THE_DESK_ANSWERS_THE_WAR_QUESTION`: `wars`, `allies`, `safe`, `truce_clock`, `war_effort`, `news`, and "what does X have" on the strength arm), the past-tense WH lead (`A_PAST_TENSE_WH_IS_A_QUESTION`), the fog-honest what-if (`THE_WHAT_IF_IS_FOG_HONEST`), the what-if that refuses like the order (`THE_WHAT_IF_REFUSES_LIKE_THE_ORDER` — `friendly_fire_refusal`, the executor's armistice block, the declaration warning for a court at peace), the price that is the quote (`THE_PRICE_IS_THE_QUOTE` + `counsel.THE_LEVY_LINE_IS_THE_QUOTE`), the income sentence that sums (`THE_INCOME_SENTENCE_SUMS`), who is winning off the banner (`WHO_IS_WINNING_READS_THE_BANNER`), the router's whole words (`THE_ROUTER_READS_WHOLE_WORDS`), the counsel's action points / refusals / spread / crossing (`THE_COUNSEL_READS_THE_ACTION_POINTS`, `THE_COUNSEL_READS_THE_REFUSALS`, `THE_COUNSEL_SPREADS_THE_ORDERS`, `THE_COUNSEL_READS_THE_CROSSING`), the insist arm's price (`THE_INSIST_ARM_NAMES_ITS_PRICE`), Berthier's sanitised suggestions (`BERTHIER_SUGGESTS_ONLY_ORDERS_THE_GAME_TAKES`), the objection that names its concern (`THE_OBJECTION_NAMES_ITS_CONCERN`), our own fallen (`OUR_OWN_FALLEN_ARE_ANSWERED`).

**Found while building, fixed as riders:** `CommandExecutor._make_diplomatic_error` printed `armistice_cooldowns` as "turns remaining" — the engine writes that key ONCE at the truce's start (5, or the pair-exit floor of 8) and never decrements it, so the refusal said "5 turns remaining" on every turn of the truce; it reads the truce's clock (`ARMISTICE_DURATION − armistice_turns`, the rule the truce expires by), pluralised, and the desk's truce clock and the refusal now agree at the wire.

**Decisions taken here (under the standing grant):** (1) **the odds do NOT rank the counsel's attack** — a first cut sorted the attack candidates by the muster's band and promoted `Soult, attack Mack` over `Ney, attack Mack`; twenty-four first-contact pins that quote the boot's first line went red, and the row asked for none of it. The counsel offers what the executor TAKES, in roster order; the odds are the what-if's to answer. (2) **DESK-11 is CLOSED as already landed** by row EP F2's display-name pass and pinned here rather than re-built. (3) **DESK-12's dead `peace` half is deleted**, its reason at the pattern (the peace-intent route claims the sentence first). (4) **AAR-29's IQ9-X3 half** (a live-road failure stamped `parse_mode: mock`) stays SR-3c's, where the row homed it. (5) **DESK-6's residue** (the `is_drilling` flag no Marshal has) is cleaned in the counsel's free-to-order clause.

**Two pins re-seated consciously, both found by the slice's own build and not by the families:** `tests/test_cx2_berthier_answers_the_board.py::TestTheGuardsWhereTheyBite::test_the_levy_line_is_PRICED_where_the_levy_is_open` had pinned the LEDGER's headline levy (450g for 10,000) beside an order the executor charged 518 for — DESK-2's finding, exactly; it pins the quote now. `tests/test_bugfix_session3.py::TestPT4ArmisticeAttack._setup_armistice` staged only the cooldown; it stages the truce's clock too, and its "4 turns remaining" assertion holds unchanged.

**One more found by the hook, not by the slice:** the authored IQ-9 recovery cassette `gibberish-berthier.recovery` (and its MANIFEST row) RE-STAMPED — the hook's `TestCassetteHygiene::test_drift_is_acknowledged_or_fails` caught the new recovery-prompt section; attributed exactly: the lever `prompt_builder.THE_RECOVERY_PROMPT_NAMES_THE_COUNSEL` down reproduces the recorded fingerprint `582b90ff…` (1,854 chars) byte for byte, up gives `13183675…` (2,276 chars); system prompt unchanged; the attribution is pinned both ways.

**Tests:** `tests/test_crt7_the_desk_reads_the_order.py` (110 — every row at `POST /command` on the shipped boot, the action points read before and after each question, a lever-down pin per rule, the boot's every counsel line sent through `/command` on a fresh boot and none refused, the client's button rendering pinned in the `.gd` source). **Sweep:** `tools/_sweep_sr3a_ii.json` 39/39 killed, 0 INERT at close — two first reported INERT, both real weaknesses in the slice's own pins: the cheapest-levy comparison (on the boot ONE province levies, so the first quote was the cheapest by accident — re-staged with Ney alone at Provence, the dearer first quote, and the chest raised so the price decides) and the fortify refusal (the engaged Ney was consumed by the attack line and the fortify loop stopped at Davout before it reached him — re-staged with the rest of the roster drill-locked so the refusal is the one thing between him and a fortify line); both re-checked KILLED. **Balance:** `BASELINE_SERIES` + M1–M7 byte-identical without re-record — display and parser only by construction (the desk, the counsel, the router, the objection copy and the recovery reply are player surfaces; the AI never parses text and never reads them; the armistice refusal's TEXT changed, not its verdict). **Client:** ONE `.gd` (`objection_dialog.gd`), parse harness EXIT=0 (`tools/godot_parse_report.json` regenerated), headless boot smoke 0 `SCRIPT ERROR`. Rows: `docs/BUG_FIXES.md` AAR-17 / AAR-19 / AAR-23 / AAR-29 / AAR-31 FIXED; DESK-1 / 2 / 4 / 5 / 7 / 8 / 9 / 13 / 14 / 15 / 16 FIXED, DESK-11 CLOSED (F2, pinned), DESK-12 FIXED (the dead half), DESK-6's residue cleaned.

### §12.10 CRT-2 LANDING RECORD — "The name is never replaced" ✅ LANDED September 26, 2026 (Score Mandate Chunk 3, SR-3b — CQ-17 and CQ-29; CQ-30 landed first, §12.8)

**Re-measured first, at the real `POST /command` on a fresh shipped 1805 boot.** Both rows reproduced to the digit. **CQ-17:** `Davout, grant Ney a rente` pensioned DAVOUT (120g/turn); `Davout, revoke Ney's rente` withdrew Davout's own 60g/turn; with Swabia staged French, `Davout, endow Ney with Swabia` endowed DAVOUT for 200 gold and an administrative action — irreversible, since no verb takes an estate back. The unaddressed controls rewarded Ney. **CQ-29:** with Soult at Paris and 20,000 gold, `recruit infantry in Swabbia` / `in Atlantis` / `in Franche-Comté` / `in Swabbia, Sire` / `in Austria` / `raise troops at Ulm` each raised 10,000 infantry AT PARIS for 654 gold; `build supply depot in Atlantis` / `in Franche-Comté` / `in Brittanny`, `repair the fort in Atlantis` and `repair Lorrain` answered *"Specify a region"* — though the player had specified one.

**The rule — a name the sentence gives is the one acted on, or the order is refused free, saying which name it read — built four ways, each behind a lever whose down arm reproduces the row (`SYSTEMS_REFERENCE.md` §72.3 is the rules):**

1. **A reward goes to its OBJECT** (`parser.A_REWARD_GOES_TO_ITS_OBJECT`, at the parser's shared fuzzy pass so the mock and the live road agree): an ADDRESSED `grant_pension` / `revoke_pension` / `grant_dotation` goes to the first of our marshals named after the address; the addressee is decoration. A fallen man named there — addressed or not — is answered with the desk's own DESK-15 sentence (`fallen_reward_object_refusal`, kind `fallen_recipient`, rendered verbatim through `main.VERBATIM_PARSE_REFUSAL_KINDS` beside WO-1's enemy addressee): *"Marshal Lannes fell at Franche-Comte on turn 1, Sire — his corps was destroyed and no order can reach him"*, never *"Did you mean Ney?"* (what the recipient rule alone produced) and never *"Whose household…?"* (the pre-slice answer).
2. **Accents never hide a name** (`llm_client.ACCENTS_NEVER_HIDE_A_NAME`): the fast parser's name matcher reads both sides with accents folded, one character for one (`fold_accents`), so its position scoring is untouched; `Franche-Comté` is `Franche-Comte` and `Masséna` is Massena.
3. **The named ground is kept** (`llm_client.A_NAMED_GROUND_IS_KEPT`): a recruit / build / repair line's spoken province is kept when no known name matched it (`named_ground_phrase` — the last "in"/"at" that yields a place, the Sweep-5 rule; and `repair`'s direct object, the verb's own example form "repair Paris"). A manner ("at once", "in haste", "in person"), a generic ("the capital"), a formation ("Ney's corps") or the thing mended ("the damage", "war damage") is never a place, and a further clause word — including another "in"/"at" — ends the place.
4. **The executor resolves or refuses** (`economy_executor.A_NAMED_PROVINCE_IS_NEVER_REPLACED`): a named province that does not resolve exactly is read through `CommandExecutor._fuzzy_match_region` — the march road's own: a typed mistake is read as the province it meant, a nation is answered with its provinces (IGR-A3), a place the map does not hold is refused free. The verb RE-RUNS on the read province and FA-54's grounding note is appended to WHATEVER comes back (`_reread_named_province`), so no exit of the verb acts on a province the player did not type without saying which one it read; the typed line rides through (`raw_text`, the `grant_dotation` idiom). Exact names — every AI order — never reach the matcher. A recruit is never raised at the capital in a named province's stead.

**Measured after, at the wire (same staging):**

| Line | Before | After |
|---|---|---|
| `Davout, grant Ney a rente` | Davout pensioned | **Ney** pensioned |
| `Davout, endow Ney with Swabia` | **Davout** endowed, 200g | **Ney** endowed, 200g |
| `Davout, grant Lannes a rente` (Lannes fallen) | Davout pensioned | refused free: *"Marshal Lannes fell at…"* |
| `recruit infantry in Swabbia` | 10,000 at Paris, 654g | refused free: *"We do not control Swabia … (Our maps read Swabia as the province nearest your order, Sire.)"* |
| `recruit infantry in Atlantis` | 10,000 at Paris, 654g | refused free: *"Region 'Atlantis' not found. Did you mean 'Albania'?"* — the typed march's own answer |
| `recruit infantry in Austria` | 10,000 at Paris, 654g | refused free: *"Austria is a nation, not a province…"* |
| `recruit infantry in Lorrain in haste` | — | 3,000 at Lorraine, 741g, the reading disclosed |
| `recruit infantry in Franche-Comté` | 10,000 at Paris, 654g | 3,000 at Franche-Comte, 872g — identical to the unaccented line |
| `build supply depot in Brittanny` | *"Specify a region"* | *"Cannot build in Brittany — town regions…"* + the reading |
| `repair Lorrain` | *"Specify a region"* | Lorraine repaired, 150g, the reading disclosed |
| `recruit infantry at once` / `in haste` / `in the capital` | capital levy | capital levy (unchanged) |

**Rider found while building, fixed here:** **a hold the game placed reads no name** (`strategic_executor.THE_DEFAULT_HOLD_READS_NO_NAME`). Every bare `Ney, hold` — and `hold here`, `hold position`, `hold our lines` — answered *"Ney will hold Rhineland. (Our maps read Rhineland as the province nearest your order, Sire.)"*: FA-54's note claiming a reading of a name nobody typed, measured on the pre-slice tree. A note that fires on every hold teaches the player to skip the one CQ-29 now depends on. The strategic parser marks its own default (`target_placed_by_the_game`, carried beside the other strategic keys; transient, never saved), the executor treats a generic hold it resolved as placed too, and a typed name still discloses (`hold Rhinelnd` → Rhineland, `Soult, hold Mainz` → Maine).

**Decisions taken here (under the standing grant):** (1) **the recipient rule is the one sentence the sweep could observe** — its first cut read only an address that named one of ours and excluded the addressee from the object scan; both narrower forms came back INERT (on every road the parse already binds the first name after a non-marshal address), so they were REMOVED rather than pinned. (2) **A named marshal keeps his own road** — `Ney, recruit infantry in Swabbia` still levies where Ney stands (PF-7's surfaced correction, CN-1 + CN-2's recorded ruling); the province re-read runs only where the game chooses the man. Pinned as the boundary. (3) **The accent fold stays although the executor's matcher rescues the accented province at the wire** — the fold makes the fast parse read the right name (the corpus pins it), rather than leaning on the executor to repair a wrong one.

**Found, filed, not fixed — different invariants:** **CQ-37** (an idiom is read as a place or a condition: `recruit infantry at once in Lorrain` is refused as a contingency — the condition guard exempts "once more/again" but not a PRECEDING "at"; `Ney, hold fast` is refused as a destination; both free, both pre-existing) → the Chunk 3 reserve; **CQ-38** (`grant Ney and Murat a rente` pays Ney and says nothing of Murat — the second name is DROPPED, not replaced; pre-existing on the unaddressed form) → CRT-11 "the second name is heard".

**Drive-by (test hygiene):** `tests/test_estate_second_pass.py::TestBattleReportExpectationNote._decisive_win` — "dies whatever the rolls" was false once in 300 (replaying its staging under `random.seed(0..299)`, seed 261 leaves Mack standing at Swabia with 69 men: no decisive victory, no note), identically on the pre-slice tree; it failed one regression run in five during this slice. The dice are pinned (seed 1805, a winning roll) with the measurement in the comment.

**Tests:** `tests/test_crt2_the_name_is_never_replaced.py` (49 new, 62 in the file with CQ-30's 13) — every row at `POST /command` on the shipped boot with the gold, admin, pensions, estates and strengths read before and after; a lever-down pin per rule. **Golden corpus:** eleven `crt2-*` rows, 780 → 791, mock 791/791 — the eight defect rows FAIL on the pre-slice tree and the three controls pass (falsifiability run on a clean worktree). **Sweep:** `tools/_sweep_sr3b.json` 20/20 killed, 0 INERT at close — four first INERT, all resolved on the evidence: two by REMOVING code the sweep proved unobservable (the recipient helper's narrower forms, decision 1), two by re-staging pins on phrasings where the rule decides (the condition guard strips "once" before the ground is read, so "at once" could see neither the manner nor the tail rule; "in haste", "in the capital" and "in Lorrain in haste" do), and the accent mutation paired with the corpus harness. **Gates:** the parser / command / FA / NPC / PC15 families (5,528, 97 files), the strategic / hold / economy / estate / baseline families (3,200, 77 files), the IQ-9 keyless gate green (no cassette drift — no prompt changed); `BASELINE_SERIES` + M1–M7 byte-identical without re-record (structural: every AI order names an exact province and no AI parses a reward); ruff clean; zero `.gd`.
