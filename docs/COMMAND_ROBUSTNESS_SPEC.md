# Command Robustness Phase ("Talk to Your Marshals")

> **Status:** v0.2 — July 3, 2026. **Phase ACTIVE — user blessed scope July 3, 2026 (CR-0..CR-5; CR-6 still holds its own gate).** **CR-0 LANDED July 3, 2026** (see §2 row + BUG_FIXES.md). CR-6 (Conversational Objection Negotiation) and anything coupling `strategic_score` to outcomes REQUIRE their own design gates per the ROADMAP LLM Mechanical Expansion rules.
> **Origin:** July 2, 2026 re-staging. Promotes ROADMAP.md's "Post-Diplomacy Command Layer Queue" (9 NEEDS-SPEC items, explicitly gated on "diplomacy refinement stable" — that condition is now met) into a numbered phase, grounded in a same-day code audit + live probe of the parse pipeline on the shipped 1805 boot.
> **Vision anchor:** This IS the game's core pillar — "you talk to your generals" — and design philosophy #4 ("Every input gets a response. No silent failures."). Golden Rule 6 boundary holds throughout: **LLM parses, executor stays deterministic.** `validate_parse_result` (`backend/ai/validation.py:141`) remains the enforcement seam.

---

## 1. Ground truth (audited July 2, 2026)

The pipeline is a 4-stage chain: fast keyword parser → optional LLM fallback (only when fast confidence < 0.7) → fuzzy-match pass → strategic-order detection. Structurally sound, but **roster-pinned to the retired legacy Waterloo world**:

- **P0 DEFECT (probe-verified, all LLM modes):** `parser.py:56` hardcodes 4 legacy player marshals; the mock parser's marshal extraction matches (`llm_client.py:610-615`). On the shipped 1805 boot, **"Soult, attack Mack" / "Lannes, move to Swabia" / "Massena, hold Milan" all fail** — 5 of the player's 7 French marshals (Soult, Lannes, Murat, Bernadotte, Massena) cannot be commanded by typed text. Worse, the failure chain hides it from the LLM: the fast parser awards 0.8 confidence for any recognized action verb (≥ the 0.7 fallback threshold), so the LLM is never consulted before the fuzzy pass hard-errors with suggestions naming marshals that don't exist in this world. Tracked in BUG_FIXES.md (upgraded from the older "dev-mode only" framing, which the probe disproved for marshal-name commands).
- `known_regions` for fuzzy/typo correction derives from legacy `REGIONS_DATA` — 19 names on a 126-province map (`parser.py:139-140`). The mock target-extraction ladder is likewise legacy-hardcoded (`llm_client.py:857-911`).
- The prompt's "Geographic layout" block describes the retired 19-region map — actively misleading the live LLM (`prompt_builder.py:393-396`).
- Only 2 tactical + 2 strategic of the 12 defined few-shot examples are actually sent; zero few-shots exist for recruit/garrison/form_square/vassal/settlement/request_terms verbs.
- Dead/unwired affordances: `parse_multiple` (multi-marshal splitting, `parser.py:612` — never called from the live path), `build_clarification_prompt` (`prompt_builder.py:638` — designed, never wired), the player-facing "Multi-marshal commands coming in a future update!" string (`validation.py:195` — an unowned deferral this spec now owns), fuzzy-matcher Phase 3/6 TODOs incl. the autocomplete dropdown idea.
- Silent-marshal-drop class: meta-actions (`parser.py:209`) skip marshal fuzzy-matching — "Murat, charge" succeeds with `marshal=None`, silently discarding the addressee.
- Provider: `claude-3-haiku-20240307` pin (2024-generation) with brittle 3-way JSON brace-extraction; Groq is a stub returning `matched=False`.
- Context substrate already half-exists: `world.command_history` persists the last 50 structured `{raw_input, marshal, action, target, turn}` entries — currently only fed back as raw strings for repetition scoring, and only recorded in LLM mode.
- E-1 (July 2) already dynamized **nation** extraction from both live rosters — the pattern to copy for marshals/regions.

## 2. Slice plan

| Slice | Scope | Gate |
|-------|-------|------|
| **CR-0 (P0 defect fix)** — ✅ **LANDED July 3, 2026** | Dynamize parser rosters from the live world: `valid_marshals` from `world.marshals` (mirror the `_get_known_enemies(world)` pattern), `known_regions` from `world.regions`, mock target ladder from game_state. Closes the 5/7-marshal gap + the BUG_FIXES bare-command entry in one pass. Behavior tests over BOTH worlds (legacy fixture + `europe_1805.json`): `tests/test_command_robustness_cr0_parser_rosters.py` (66 tests, incl. the 4-lens adversarial-review regressions — enemy-honorific guard, punctuated targets, position-aware matching, vassal nation targets, edit-distance enemy typos, word-boundary demonyms). **Landed extras (same defect family, probe-verified):** case-tolerant `Marshal [Name]` regex ("Marshal Soult" never matched); exact-enemy-wins-before-region-fuzzy ("Mack" was rewritten to "La Mancha"); punctuation-stripped word scans ("Bernadotte," drifted to region "Bern"); nation-keyed vassal keywords from live game_state + word-scan skip fix (typed "invest in saxony" was dead in EVERY world); live-nation demonyms in strategic generic classification ("pursue the austrians" no longer becomes fake region "The Austrians"). | None (defect) |
| **CR-1** | Parser eval harness: golden corpus of (utterance → expected `{marshal, action, target, type, strategic}`) parameterized over both scenario worlds; runs in mock mode in CI, optionally against the live provider on demand. Seed from the ~320 existing parser tests. This is the phase's regression gate — land before behavior changes. | None |
| **CR-2** | Confidence-gate rework + clarification dialogue: retry via LLM when the fuzzy pass errors (today the LLM never sees "confidently wrong" parses); marshal-aware confidence scoring; one-question disambiguation ("Which marshal, Sire?") on the existing DialogueManager LOCAL_PLANNING taxonomy, unifying the four partial clarification surfaces (fuzzy suggest, Grouchy popup, strategic interpreted_target, Berthier recovery); extend Berthier interception beyond its two hardcoded error shapes; fix the silent-marshal-drop class. | None |
| **CR-3** | LLM modernization: refresh the model pin; evaluate structured tool-use output replacing JSON brace-extraction; fix the geographic-layout prompt block + token-budget comments; dynamic few-shots using live roster names; broaden verb coverage. | None |
| **CR-4** | Context carryover: Persistent Command Focus + Semantic Command History (ROADMAP rows) built on the existing `command_history` structure — "again", "same target", "him/there", "not you, Davout"; decide mock-mode recording. | None |
| **CR-5** | Personality-Biased Disambiguation — the signature feature: "Ney, deal with Wellington" → attack; "Davout, deal with Wellington" → hold/scout; "Grouchy…" → asks. Same parse call, personality-aware system prompt, zero extra LLM cost; mock-safe neutral fallback. ROADMAP marks it "can prototype early." | Scope blessing |
| **CR-6** | Conversational Objection Negotiation — player argues back in natural language; LLM classifies into the existing deterministic Insist/Trust/Compromise buckets with a trust modifier. | **USER DESIGN GATE** (LLM picks the bucket) |
| **CR-7 (backlog)** | Conditional/compound orders (wire or replace `parse_multiple`; owns the `validation.py:195` string), command surface shortcuts, map-driven command context, fuzzy autocomplete dropdown UI, R158 parse-confidence display. | Per-item at phase review |

Deferred out (unchanged owners): anti-memorization/creative-phrasing bundle (gated behind CR-4/CR-5 per ROADMAP), Voice-to-Text (Pre-EA; rides this pipeline unchanged), Groq implementation (Pre-EA BYOK).

## 3. Absorbed owner rows (Golden Rule 9 — each source row now points here)

- BUG_FIXES.md mock-parser bare-command entry (+ its upgraded marshal-roster dimension) → CR-0
- `validation.py:195` multi-marshal "coming soon" string → CR-7
- Dead `parse_multiple` / `build_clarification_prompt` / fuzzy TODOs → CR-2/CR-7 dispositions
- DESIGN_REFINEMENT R158 (parser confidence feedback) → CR-7
- ROADMAP Post-Diplomacy Command Layer Queue (all 9 rows) → CR-2..CR-7
- SYSTEMS_REFERENCE §5 stays the single pipeline-behavior doc; this spec links, never duplicates.

## 4. Candidates parked for the CR-5/CR-6 gate review (recorded July 3, 2026)

User direction (July 3): the text system is the pillar, not a gimmick — surface these at the same design table as the CR-5 scope blessing / CR-6 gate rather than losing them. Each row's completion definition is an accept/drop/re-home decision recorded at that review (Golden Rule 9: this section is the owner row; the gate review is the landing).

| Candidate | Sketch | Natural home if accepted |
|-----------|--------|--------------------------|
| **Flavor Echoing pull-forward** | ROADMAP anti-memorization bundle marks it HIGHEST PRIORITY ("the game heard me" — marshal reply echoes the player's own words). Decide whether it rides CR-5 instead of waiting out the full bundle gate. | CR-5 rider |
| **Two-way channel (questions, not just orders)** | "Ney, what do you see?" / "Berthier, can we take Vienna before winter?" — military-side advisory mirroring `diplomatic_advisory.py`; deterministic fog-respecting data, LLM phrases only (Golden Rule 6 safe). | New CR-8 slice |
| **Commander-intent orders** | "Take Vienna" with no marshal named → Berthier proposes the assignment ("Lannes is closest, Sire — shall he march?"), one confirm. | CR-2 extension |
| **Player's words become the record** | Persist raw phrasing on the order; quote it in campaign log / battle reports / future Gazette. `command_history` already stores raw input. | CR-4 rider |
| **Tone parsing** | Brusque vs. flattering vs. precise phrasing → small trust/objection modifier, personality-dependent. Same LLM-classifies-into-deterministic-buckets shape as CR-6 — shares that gate. | CR-6 gate item |
| **Pre-battle councils** | Before a big coordinated attack, an opt-in typed exchange where marshals voice concerns — objections as a conversation you choose, not an interruption. | Own mini-gate after CR-6 |

## 5. Non-goals

- No LLM influence on combat/mechanics outcomes (Golden Rule 6). The three ROADMAP "LLM Mechanical Expansion Path" ideas stay design-gated outside this phase.
- No phrasing bonuses/penalties in this phase (anti-memorization bundle stays gated).
- Mock mode remains fully playable: every slice ships mock-safe fallbacks.
