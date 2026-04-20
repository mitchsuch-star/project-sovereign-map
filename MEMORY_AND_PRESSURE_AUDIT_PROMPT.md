========================================================================
  COMPREHENSIVE AUDIT PROMPT — Memory and Pressure v2.4.3 spec ensemble
========================================================================

You are auditing the full Memory and Pressure v2.4.3 design-spec ensemble
for the Napoleonic strategy game "project-sovereign-map". No production
code has been written yet against v2.4.3 — these documents will be the
contract implementers read. Treat every sentence as if a contributor will
code directly from it without the author present to answer questions.

Your job: confirm the spec ensemble is ready to be implemented, that
every engine behavior has a matching UI surface (and vice versa), and
that there are no fuzzy edges where a builder would have to guess.

------------------------------------------------------------------------
  OUTPUT FILE (IMPORTANT — branch on your identity)
------------------------------------------------------------------------
  If you are Claude (any Claude model, running in Claude Code or any
  Anthropic harness):
      write your audit report to  docs/audits/MP_V243_AUDIT_CLAUDE.md

  If you are Codex (OpenAI Codex CLI or any GPT-series coding agent):
      write your audit report to  docs/audits/MP_V243_AUDIT_CODEX.md

  Create the `docs/audits/` directory if it does not exist. Write a
  SINGLE file with the full report — do not split across files. Use the
  exact filename shown above so the two audits can be diffed.

  Start the report with a one-line self-identification:
      `# Memory and Pressure v2.4.3 Audit — <your-model-id>, <date>`
  so readers can tell the two reports apart without opening filesystems.

------------------------------------------------------------------------
  DOCUMENTS IN SCOPE
------------------------------------------------------------------------
  Primary specs (read in full):
    - docs/RELIABILITY_COMMITMENTS_SPEC.md          (v2.4.3, ~1412 lines)
    - docs/RELIABILITY_IMPLEMENTATION_PLAN.md       (v2.4.3, ~344 lines)
    - docs/COMMITMENTS_PRESENTATION_SPEC.md         (v0.5.1, ~809 lines)
    - docs/DIPLOMAT_VOICE_BIBLE.md                  (~246 lines)

  Cross-ref specs (read sections you cite):
    - docs/COALITION_SPEC.md          — threat ladder / passive row, BREWING/DECLARED state names
    - docs/SCALE_READINESS_PLAN.md    — §DG-4 amendment, §Phase 0 taxonomy (`power_tier`)
    - docs/WAR_BARGAIN_SPEC.md        — confirm what the ensemble defers
    - docs/DIPLOMACY_SPEC.md          — acceptance formula, state machine
    - docs/FOG_OF_WAR_SPEC.md         — confirm diplomacy-no-fog assumption still holds
    - docs/TOP_BAR_SPEC.md            — Diplomatic Ledger tab ownership
    - docs/SAVE_FORMAT_REFERENCE.md   — serialization contract
    - CLAUDE.md                        — phase-row claims must match

  Live code surfaces to reality-check against:
    - backend/game_logic/coalition.py         — threat ladder, process_coalition_turn
    - backend/game_logic/diplomacy.py         — acceptance formula, state machine
    - backend/game_logic/diplomatic_templates.py  — commitments_* templates, diplomat copy
    - backend/game_logic/diplomatic_ledger.py — Balance of Europe headline renders here
    - backend/models/world_state.py           — betrayal_history, next_episode_id, vassals, diplomatic_reliability
    - backend/notifications.py                — priority tiers, icon registry
    - backend/campaign_log.py                 — event taxonomy + format_event_oneliner
    - godot-client/.../notification_bar.gd    — TYPE_ICONS, tier rendering
    - godot-client/.../diplomatic_ledger.gd   — Treaties / Threat tab rendering
    - godot-client/.../commitment_paradox_popup.{tscn,gd}  — referenced by name in presentation spec

  (If a filename I listed does not exist in the repo, call it out under
  "Missing artifacts" — that itself is a fuzzy edge.)

------------------------------------------------------------------------
  AUDIT DIMENSIONS
------------------------------------------------------------------------

  Score each dimension with a one-word verdict (READY / RISKY / BLOCKER)
  plus evidence. Do not summarize without citing a line number or a
  code path.

  ── 1. INTERNAL CONSISTENCY ─────────────────────────────────────────

  Every cross-reference between the four specs must agree in both
  direction and detail. Check at minimum:

    a) Version headers
       - RELIABILITY_COMMITMENTS_SPEC says v2.4.3
       - RELIABILITY_IMPLEMENTATION_PLAN "Spec:" line points at v2.4.3
       - COMMITMENTS_PRESENTATION_SPEC "Depends on:" line cites v2.4.3
       - CLAUDE.md "Up Next" / phase row cites v2.4.3
       - No lingering "v2.4.2" / "v2.4.1" / "v2.4" in live-contract prose

    b) Shared values
       - Pressure ladder (1/3/5/8) in spec §7.3 vs. COALITION_SPEC §2a
         passive row vs. plan B-Hegemony test list
       - Hegemony share threshold (30% / 40% / 50% / 60%) — single
         source of truth, no divergence
       - `bilateral_betrayal_mod = -6 per strike` — spec §9.x vs. plan
         B-B1-lite test list
       - Composite floor value in §9.3 matches plan's merge-ordering
         section (B-B1-lite / B-B4 gate)
       - Make Amends cost (400g + 2 DP) — §8.6.1 vs §8.6.1a vs §8.8.4

    c) State / type names
       - BREWING / DECLARED / etc. in §11.1 four-case Balance-of-Europe
         machine vs. COALITION_SPEC §3-§4 state names
       - `end_reason_family` enum values (`french_breach`,
         `defensive_refusal_termination`, cascade families) are the same
         strings in spec, plan, presentation, and campaign_log.py
       - `speaker` enum (`envoy`, `foreign_office`, `talleyrand`) same
         between presentation spec §10.3 and Voice Bible

    d) Cancelled / deferred content
       - Every item crossed out in plan §"Cancelled in v2.4" is not
         silently re-referenced as live anywhere
       - `attributed_lines[]`, spotlight tier, N+1 callback, A1-fill,
         B2a-fill, B6, static `nation_concerns` field — all confirmed
         absent from live contract prose
       - Every WB-D deferred item in presentation §2 is actually pushed
         to WAR_BARGAIN_SPEC.md (don't just trust the label)

  ── 2. UI FIDELITY ──────────────────────────────────────────────────

  For each engine-emitted event, trace a complete render path:

    | Engine event (spec)  →  backend payload  →  notification tier
    |  →  icon key  →  label  →  template / copy  →  voice resolution
    |  →  popup/surface layer  →  review-action route

  Events to trace end-to-end:
    1. `commitment_paradox` (blocking)
    2. `hard_reject_posture_triggered` (CRITICAL notice)
    3. `hard_reject_posture_cleared` (NORMAL notice)
    4. `diplomatic_treaty_broken` (french_breach — CRITICAL)
    5. `diplomatic_treaty_broken` (other families — NORMAL)
    6. `commitment_paradox_resolved` (NORMAL)
    7. `witness_strike_recorded` (NORMAL)
    8. `diplomatic_treaty_broken` (defensive_refusal_termination —
       new in v2.4.3 §8.8.7a — where does this render?)
    9. Make Amends (§8.6.1) and Make Amends grievance variant
       (§8.6.1a) — what does the player see after paying 400g + 2 DP?
   10. Balance of Europe headline — four cases per §11.1, rendered
       in diplomatic_ledger.gd per presentation spec §15

  For each row, mark MISSING if any step is unspecified. In particular:
    - Does every CRITICAL notice have a named-diplomat attribution?
      (spec says yes; confirm each template exists)
    - Does every event with a popup have a `review_target` routing rule?
    - Is the `commitment_paradox_popup.{tscn,gd}` surface's field schema
      actually defined (beats 1-3, speaker slots, button labels)?
    - Does Balance of Europe headline have defined copy for the "no
      hegemon" case? (easy to forget the negative case)
    - Does the Morning Dispatch pull any of these events into its
      fog-filtered briefing? If so, which ones and with what priority?

  Also check the inverse direction (UI referenced but engine silent):
    - Every icon key in presentation §9.2 table — is the engine
      guaranteed to emit that event type with the matching payload?
    - Every voice register in Voice Bible — does a template actually
      call it with an event payload that exists?

  ── 3. FUZZY EDGES ──────────────────────────────────────────────────

  Flag anywhere an implementer would have to guess. Specifically hunt:

    a) Tie-breaks / edge cases
       - Hegemony tie-break beyond sorted(-share, -power, name) — what
         if two blocs tie on all three (theoretically possible at
         exactly equal territory + tier + name collision)?
       - Vassal `lord` cycle — `_top_overlord` has a guard; does any
         OTHER helper walk the chain without one?
       - What happens if `world.get_active_nations()` returns empty
         (all nations eliminated)? Does `_calculate_hegemony_pressure`
         crash, early-return, or silently mis-behave?
       - What if `european_power == 0` at turn 1 before regions are
         assigned? (spec returns `{}` — good — but plan tests this?)

    b) Ordering / race conditions
       - B-B1-lite and B-B4 merge-ordering gate is stated. What about
         B-Hegemony vs. B-B1-lite? Which must land first for the
         acceptance formula to read hegemon bloc correctly?
       - Does `invalidate_active_nations_cache()` pattern also cover
         `get_bloc_members()` cache invalidation? The spec says "per-
         turn cache" — is the invalidation trigger defined?

    c) Missing failure modes
       - Scenario data missing `power_tier` — spec says fallback is
         "secondary." Is this the same default the SCALE_READINESS
         taxonomy uses? What logs / warns when fallback fires?
       - Named-diplomat lookup for a non-cast nation (Ottomans,
         Sweden at 13-nation scale) — presentation §10.3 covers the
         5 authored ones; what's the fallback register?
       - `commitment_paradox` where both spurned nations happen to
         have the same named diplomat — does §12.3 beat 3 degrade
         cleanly?

    d) Silent assumptions
       - "Per-turn cached helper" — where does the cache live? If
         `world.turn_cache`, is that field defined on WorldState?
       - "Legacy alias on read" for `alliance_paradox → commitment_
         paradox` — what code paths still emit the legacy name? What
         is the removal criterion?
       - Non-France-hegemon guard in §7.3 says "emit a debug log for
         telemetry." Defined logging channel? Log level? Rate limit?

    e) Test-authoring ambiguity
       - B-Hegemony plan lists 18-22 tests — are the test names
         specific enough to write, or would two authors write
         different tests for the same bullet?
       - Does any dimension rely on LLM-mode behavior for its
         correctness test? (Mock mode must stay authoritative.)

  ── 4. CODE SNIPPET CORRECTNESS ─────────────────────────────────────

  Every Python block in the spec is a contract. For each:

    - Can it be pasted into a file and run with only the imports it
      cites? (Type hints from `typing` are fine; bespoke types must
      be defined upstream in the spec.)
    - Do all helpers it calls exist in current `master` or get added
      explicitly in the plan? Cross-check:
        - `world.get_active_nations()` — exists (CLAUDE.md §8)
        - `world.get_nation_regions()` — exists (CLAUDE.md §8)
        - `world.get_diplomatic_state(a, b)` — exists in diplomacy.py
        - `world.get_power_tier(nation)` — NEW in B-Hegemony, spec says
          reads from scenario data without a runtime map. Is the read
          path defined?
        - `world.vassals` dict shape — matches models/world_state.py?
        - `add_threat()` API on coalition — signature matches call?
        - `has_hard_reject_posture(world, France, nation)` — exists?
      For any NEW helper, confirm the plan has a slice that defines it.
    - Any off-by-one (e.g. `if share < 0.30 return 0` vs exactly-30 case)
    - Any mutable-default or shared-dict trap
    - Any integer/float mixing that would crash Godot-bound ints

  Specific snippets to check hard:
    - §7.1 `_top_overlord` and `get_bloc_members` — cycle safety,
      cache key, sort determinism
    - §7.2 `power_score` — default fallback, region-count source
    - §7.3 `_calculate_hegemony_pressure` — majors fallback, tie-break,
      `add_threat` call-site guard
    - §7.3 `_hegemony_pressure_for_share` — ladder edges
    - §9.x composite floor (if the numeric expression landed) — does
      it compose correctly with grievance_modifier stacking?
    - §11.1 four-case state machine — is the decision tree exhaustive?

  ── 5. IMPLEMENTATION PLAN COVERAGE ─────────────────────────────────

  Every normative contract in the specs should trace to a plan slice
  + a test. For each new v2.4.3 contract, confirm:

    - B-Hegemony covers: bloc helpers, power_score, hegemony engine,
      coalition leader selection, Balance of Europe headline,
      non-France-hegemon guard, vassal-chain recursion, cycle safety
    - B-B1-lite covers: collapsed acceptance formula,
      hegemony_target_mod, bilateral_betrayal_mod rewrite,
      composite-floor reintroduction (if §9.3 landed)
    - B-B3 covers: alliance_paradox → commitment_paradox rename,
      legacy-alias read path, save migration
    - B-B7 covers: Make Amends (standard) — cost, effect, cooldown
    - B-B4 covers: DG-4 call-to-arms, grievance-variant Make Amends,
      defensive-refusal termination (§8.8.7a), R9/R10/R11 playtest gates
    - C-lite covers: named-diplomat resolution helper, commitment_
      paradox_popup wiring, three-event committed prose, Balance of
      Europe headline render, period-vocabulary icons + priority tiers

  Flag any §-level contract in the specs that does NOT land in a slice.

  ── 6. VOICE / COPY FIDELITY ────────────────────────────────────────

  For each of the three live events + paradox beats:

    - Is there committed mock-mode prose in COMMITMENTS_PRESENTATION
      §12 worked examples?
    - Does each line trace to a Voice Bible register for the named
      diplomat? (Talleyrand / Castlereagh / Hardenberg / Metternich /
      Einsiedel)
    - Can a template author read the Voice Bible and reproduce the
      register without ambiguity?
    - Mock mode (LLM_MODE=mock) must produce fully valid output
      without LLM — is this confirmed for every template?
    - Is there a template for `speaker="foreign_office"` resolving to
      "The Chancery of {nation}" for each of the 5 nations?

  ── 7. DANGLING REFERENCES ──────────────────────────────────────────

  Run `grep` in each primary spec for content the v2.4 / v2.4.3 rescope
  CUT. Any live reference to:
    - `attributed_lines[]` (outside the §9.1 stub explaining the cut)
    - `spotlight` / `dispatch spotlight` / `Spotlight Carryover`
      (outside §7.2 + §8.2 stubs)
    - `N+1 aftermath` / `N+1 Talleyrand aside` (outside §9.4 stub)
    - `nation_concerns` as a stored field (outside §6.3 / §7 stubs)
    - `actor_honored_turns` / redemption tick (cancelled in v2.4)
    - `opposition_graph` / `war_bloc.target_nation` (seams stubbed)
    - `join_opportunity` / `war_entry_score` / `counter_bargain` /
      `pending_declaration` (all moved to WAR_BARGAIN_SPEC)
  is a broken pointer. Report file + line + what the reader would
  assume the reference is still active.

  ── 8. SCOPE DRIFT ──────────────────────────────────────────────────

  Compare what the v2.4.3 changelog in RELIABILITY_COMMITMENTS_SPEC
  §17 claims against what actually changed:
    - Does the body contain edits the changelog does not mention?
    - Does the changelog claim edits the body does not contain?
    - Does any "deep-audit fix" slide in a design change that was not
      in the audit? (Expected: A1-A14, B1-B7, C1-C7 only.)
    - Does v2.4.3 respect the "no new infra" principle of v2.4, or
      does it quietly re-add anything?

  ── 9. PHASE-ROW TRUTH ──────────────────────────────────────────────

  CLAUDE.md "Up Next" → Memory and Pressure line must say:
    - current spec version (v2.4.3)
    - remaining slices (B-Hegemony + B-B1-lite + B-B3 + B-B7 + C-lite)
    - test budget matching the plan (~45-54)
    - merge-ordering gate (B-B4 at/after B-B1-lite)
    - DG-4 parallel status
  Any drift is a blocker for a fresh session.

------------------------------------------------------------------------
  OUT OF SCOPE (do not flag these)
------------------------------------------------------------------------
  - Stylistic / prose preferences (word choice, bullet vs prose).
  - Reopening v2.4 design decisions — the hegemony refactor is final.
    Your job is to confirm the spec ensemble implements it cleanly,
    not to second-guess the direction.
  - WAR_BARGAIN_SPEC internals — only confirm the deferral handoff
    is clean from this ensemble's side.
  - Scale Readiness Phase 2+ work beyond §DG-4 amendment cross-refs.
  - Non-Memory-and-Pressure sections of COALITION_SPEC.
  - Documentation tone of CLAUDE.md beyond the phase-row truth check.

------------------------------------------------------------------------
  WHEN TO PUSH BACK HARD
------------------------------------------------------------------------
  - A code snippet would raise or silently mis-behave on a legal input.
  - A UI surface references an event the engine cannot emit, or vice
    versa.
  - A "fix" in the v2.4.3 changelog is absent from the body.
  - Two specs disagree on a numeric threshold, enum value, or state
    name (single source of truth violation).
  - Make Amends grievance variant (§8.6.1a) has no defined disambiguator
    for the parser / wizard.
  - Defensive-refusal termination (§8.8.7a) breaks existing cascade
    metadata assumptions without a migration path.
  - CLAUDE.md still points at v2.4 / v2.4.2 anywhere it should say
    v2.4.3.
  - Presentation spec promises named-diplomat copy for an event the
    backend does not emit with enough payload to resolve the speaker.

------------------------------------------------------------------------
  OUTPUT REPORT STRUCTURE
------------------------------------------------------------------------
  Write to the branch-specific file named at the top. Structure:

    # Memory and Pressure v2.4.3 Audit — <model-id>, <date>

    ## Executive summary
    One paragraph. Overall verdict: READY / READY-WITH-FIXES /
    REQUEST-CHANGES / BLOCKED. Name the top 3 findings.

    ## Dimension scorecard
    | Dimension | Verdict | Blocker count | Major | Minor |
    |-----------|---------|----|-------|-------|
    | 1. Internal consistency            | ... | ... | ... | ... |
    | 2. UI fidelity                     | ... | ... | ... | ... |
    | 3. Fuzzy edges                     | ... | ... | ... | ... |
    | 4. Code snippet correctness        | ... | ... | ... | ... |
    | 5. Implementation plan coverage    | ... | ... | ... | ... |
    | 6. Voice / copy fidelity           | ... | ... | ... | ... |
    | 7. Dangling references             | ... | ... | ... | ... |
    | 8. Scope drift                     | ... | ... | ... | ... |
    | 9. Phase-row truth                 | ... | ... | ... | ... |

    ## Event trace matrix (UI fidelity §2)
    One row per engine event. Columns: payload → tier → icon → label
    → template → voice → surface → review-route. Empty cell = MISSING.

    ## Findings
    Numbered list. For each:
      - ID (e.g. F1, F2, ...)
      - Severity: BLOCKER / MAJOR / MINOR / NIT
      - Location: file:line or §ref
      - Observation: what you saw (quote the line)
      - Impact: what breaks if an implementer writes code from this
      - Suggested fix: concrete diff-level prescription
    Sort by severity; blockers first.

    ## Missing artifacts
    Files / helpers / templates the specs name but which do not exist
    and are not scheduled by the plan.

    ## Cross-spec value table
    Single table of every shared numeric threshold / enum string /
    state name, with the value in each spec that names it. Highlight
    mismatches.

    ## Recommendation
    One of: APPROVE / APPROVE-WITH-FIXES / REQUEST-CHANGES / BLOCKED.
    One paragraph: what must happen before the next session codes.

------------------------------------------------------------------------
  USEFUL STARTING COMMANDS
------------------------------------------------------------------------
  # Confirm the branch state you are auditing
  git log --oneline -5

  # Version drift sweep
  grep -rn "v2\.4\.[0-9]\|v0\.[0-9]" docs/RELIABILITY_COMMITMENTS_SPEC.md \
      docs/RELIABILITY_IMPLEMENTATION_PLAN.md \
      docs/COMMITMENTS_PRESENTATION_SPEC.md CLAUDE.md

  # Cut-content dangling-reference sweep
  grep -n "attributed_lines\|spotlight\|N+1\|nation_concerns\|actor_honored_turns" \
      docs/RELIABILITY_COMMITMENTS_SPEC.md \
      docs/COMMITMENTS_PRESENTATION_SPEC.md \
      docs/RELIABILITY_IMPLEMENTATION_PLAN.md

  # Event name cross-check against live code
  grep -rn "commitment_paradox\|hard_reject_posture\|diplomatic_treaty_broken\|witness_strike_recorded" \
      backend/ docs/

  # Helper existence checks (expected NEW in B-Hegemony)
  grep -rn "get_power_tier\|get_bloc_members\|_top_overlord\|_calculate_hegemony_pressure" \
      backend/

  # Priority-tier registry and icon keys (UI fidelity)
  grep -n "CRITICAL\|NORMAL\|priority" backend/notifications.py
  grep -n "TYPE_ICONS\|icon_" godot-client/

  # Balance of Europe headline render site
  grep -n "Balance of Europe\|hegemon" \
      backend/game_logic/diplomatic_ledger.py \
      godot-client/.../diplomatic_ledger.gd

  # Defensive-refusal termination — new in §8.8.7a
  grep -rn "defensive_refusal_termination\|end_reason_family" backend/ docs/

  # Composite-floor claim consistency
  grep -n "composite floor\|grievance_modifier\|-60\|-90" docs/RELIABILITY_COMMITMENTS_SPEC.md

========================================================================
