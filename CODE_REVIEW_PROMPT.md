========================================================================
  CODE REVIEW PROMPT — Memory and Pressure v2.4.3 spec fixes
========================================================================

You are reviewing a documentation/spec commit for the Napoleonic strategy
game "project-sovereign-map". No production code changed — these are
design-spec edits that will drive a future implementation session.
Evaluate them AS IF they are the contract that code will be written against.

------------------------------------------------------------------------
  WHAT YOU ARE REVIEWING
------------------------------------------------------------------------
  Commit:   7646ea1 on origin/master
  Branch:   master
  Parent:   aef84ec (v2.4.2 audit report)
  Scope:    5 files, +315 / -188 lines
              - CLAUDE.md
              - docs/COALITION_SPEC.md
              - docs/COMMITMENTS_PRESENTATION_SPEC.md (v0.5 -> v0.5.1)
              - docs/RELIABILITY_COMMITMENTS_SPEC.md  (v2.4.2 -> v2.4.3)
              - docs/RELIABILITY_IMPLEMENTATION_PLAN.md

  Source of truth for what the commit was trying to do:
    docs/MEMORY_AND_PRESSURE_V2_4_2_DEEP_AUDIT.md
  (14 findings + 7 writing items + 7 consistency items = 21 action items)

  Start reading: open the audit file and the v2.4.3 changelog entry at
  the top of section 17 in RELIABILITY_COMMITMENTS_SPEC.md side by side.

------------------------------------------------------------------------
  REVIEW DIMENSIONS
------------------------------------------------------------------------

  1) CORRECTNESS — did each fix actually address the finding?
     For each audit ID (A1-A14, B1-B7, C1-C7):
       - Locate the target text in the edited file.
       - Compare against the audit prescription.
       - Classify:
           OK    — fix is correct and complete.
           PART  — fix addresses some but not all of the finding.
           MISS  — fix claimed in changelog but not in body.
           WRONG — fix is present but introduces a new problem.
       - Quote the exact line(s) or code block(s) you relied on.

  2) CODE SNIPPETS — any Python/pseudocode in the spec is a contract.
     For each new or changed snippet:
       - Does it run as written? (_top_overlord walker in section 7.1 is
         new; sorted(...) key in section 7.3 is new; grievance floor in
         section 9.3 is new.)
       - Are all variables / helpers defined before use?
       - Any off-by-one, bad default, or missed edge case?

  3) INTERNAL CONSISTENCY — the five files must agree.
     Specifically check:
       - CLAUDE.md v2.4.3 references match the spec header version.
       - RELIABILITY_COMMITMENTS_SPEC v2.4.3 references match the plan
         header's "Spec: v2.4.3" line.
       - COMMITMENTS_PRESENTATION_SPEC v0.5.1 references v2.4.3 of the
         commitments spec, not v2.4.2.
       - COALITION_SPEC section 2a new hegemony_passive row matches the
         section 7.3 ladder values (1/3/5/8).
       - Section 9.3 composite-floor claim matches the plan's Merge
         ordering section (both must describe the same B-B1-lite / B-B4
         ordering).
       - Section 8.6.1a grievance-variant cost (400g + 2 DP) matches
         section 8.8.4's cost claim.
       - Section 11.1 four-case Balance-of-Europe state machine names
         the same states (BREWING / DECLARED / etc.) that COALITION_SPEC
         sections 3 and 4 use.

  4) NEW SURFACE AREA — what did v2.4.3 add that implementers must build?
     Two new sub-sections and three new risks mean new code/tests:
       - 8.6.1a Make Amends (grievance variant): distinct action verb,
         distinct cost, parser disambiguation.
       - 8.8.7a Alliance termination on defensive refusal: new
         diplomatic_treaty_broken end_reason_family value
         (defensive_refusal_termination), bloc-cache invalidation,
         anti_renewal_cooldown interaction.
       - R9 / R10 / R11: three new playtest gates.
     Question: does the plan (RELIABILITY_IMPLEMENTATION_PLAN.md) call
     out work for these? If not, file-level gap — the spec changed but
     implementers will not see the ask.

  5) DANGLING / STALE REFERENCES — the C7 trim removed content.
     grep the trimmed file for any section still citing the cut content
     as live:
       - attributed_lines[] references outside section 9.1's stub
       - "spotlight tier" / "dispatch spotlight" references outside the
         section 7.2 stub and the section 10/12 worked examples
       - "N+1 aftermath" references outside section 9.4's stub
     Any live reference is a broken pointer.

  6) CHANGELOG FIDELITY — the v2.4.3 bullet in section 17 claims specific
     edits in specific sections. For each claimed edit:
       - Does the body actually contain it?
       - Does the body contain edits the changelog does not mention?
     Flag divergence in both directions.

  7) NEW RISKS vs. SCOPE — section 14 added R9/R10/R11.
     Are these risks legitimately audit-sourced (A13, A14, A11 → R9, R10,
     R11)? Or did the author slide in unflagged design changes as "risks"?
     (Expected: all three trace back to A-series audit findings.)

------------------------------------------------------------------------
  WHAT TO IGNORE
------------------------------------------------------------------------
  - Stylistic preferences (word choice, Oxford commas, bullet vs prose).
  - The overall audit design recommendations themselves — trust that the
    audit was correct; your job is to confirm the commit delivers what
    the audit asked for.
  - CRLF / LF line-ending warnings from git.

------------------------------------------------------------------------
  WHEN TO PUSH BACK HARD
------------------------------------------------------------------------
  - A code snippet is syntactically invalid or would throw at runtime
    on a normal input (e.g., cycle-safety test passes a self-referencing
    vassal and the walker infinite-loops).
  - A new contract contradicts an existing one in the same spec (check
    especially 9.3 floor claims against 9.4 reliability narrowing).
  - Section 8.8.7a "alliance terminates" claim silently breaks existing
    tests — check whether diplomatic_treaty_broken cascade metadata
    currently has a defensive_refusal_termination family.
  - Changelog misrepresents the scope of change (claims doc-only when
    mechanics shifted, or claims a fix landed that did not).
  - CLAUDE.md phase row still pointing to v2.4 or v2.4.2 anywhere.

------------------------------------------------------------------------
  OUTPUT FORMAT
------------------------------------------------------------------------
  Structure your report as:

    ## Correctness scorecard
    [table: audit ID | verdict | one-sentence reason | line ref]

    ## New problems introduced
    [bulleted list — each item: what, where, severity (blocker / major /
     minor / nit)]

    ## Missing / weak fixes
    [bulleted list — audit items marked PART or MISS above, with
     explanation of what is still needed]

    ## Recommendation
    [one of: APPROVE / APPROVE-WITH-FIXES / REQUEST-CHANGES / REJECT]
    [one paragraph explaining the call]

------------------------------------------------------------------------
  USEFUL STARTING COMMANDS
------------------------------------------------------------------------
  # See the diff scoped to the two critical files
  git show 7646ea1 -- docs/RELIABILITY_COMMITMENTS_SPEC.md
  git show 7646ea1 -- docs/RELIABILITY_IMPLEMENTATION_PLAN.md

  # Or the whole commit
  git show 7646ea1

  # Check for remaining v2.4.2 references that should have been bumped
  grep -rn "v2\.4\.2" docs/ CLAUDE.md

  # Check for stale spotlight / attributed_lines refs after C7 trim
  grep -n "attributed_lines\|spotlight" docs/COMMITMENTS_PRESENTATION_SPEC.md

  # Check 9.3 consistency
  grep -n "composite floor\|grievance_modifier\|-60\|-90" docs/RELIABILITY_COMMITMENTS_SPEC.md

========================================================================
