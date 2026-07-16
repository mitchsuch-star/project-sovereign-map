# SWEEP 5 — Live-Play Evidence (July 16, 2026)

**Owner:** `docs/COMBAT_OVERHAUL_SPEC.md` §2.2 (Half B evidence) — Sweep 5 measures the
**Parsing / UX** pillar after Phase 6 (PF-1..PF-9 + AI-1, commit `3c0246a`) and the two
Sweep-4 vassal parse fixes (`7908227`).
**Method:** fresh 6-turn `LLM_MODE=anthropic` playthroughs over HTTP against the real
1805 boot (`-m backend.main`, port 8005), driven by a scripted evidence harness
(scratchpad `sweep5_drive.py`) that answers the game's own questions in the game's own
idiom ("press on", "insist", "secure", "respect"). Every request/response pair captured
to JSONL for the Half-B reviewers.

The sweep ran **three capture rounds**, because the first two rounds live-found real
defects that were then fixed and re-verified — that loop IS the sweep working:

## Round 1 findings (both FIXED same-session)

1. **Typed-answer channel dead behind a soft-stop (HIGH).** With a mailbox proposal
   occupying the DialogueManager, the delegation ASK's registration silently no-oped, so
   answering Soult's own question ("give battle") fell to a fresh LLM parse →
   `Region 'generic' not found`. Root cause: `register_pending_clarification` skipped on
   ANY active dialogue. **Fix:** preempt non-hard-stop dialogues (the displaced dialogue
   returns via queue promotion on pop); hard-stops still refuse. The old CR-2 pin was
   consciously flipped. Tests: `test_sweep5_clarification_preempt.py` (6).
2. **"press on" bewildered Berthier at a blocked-path interrupt (MED).** The
   `contact_bad_odds` gate offers `attack_anyway` but no `continue_order`, so the natural
   continue-family answer fell through the interrupt keyword map to the LLM. **Fix:**
   continue-family falls back to `attack_anyway` when `continue_order` is absent
   (`main.py`). Tests: `test_sweep5_interrupt_press_on.py` (4).

## Round 2 findings (both FIXED same-session)

3. **Live LLM invented a marshal for a bare order (HIGH).** Typed `attack` (no marshal)
   → the live parse returned `marshals=['Bernadotte']` — a never-mentioned marshal — and
   broke his standing HOLD. **Fix:** validation-seam guard strips a single parsed marshal
   the utterance never named (typo-tolerant, same fuzzy budget as the parser), so live
   mode rejoins the designed CR-4-focus → CR-2-clarification flow.
   Tests: `test_sweep5_parse_validation.py` (guard arm).
4. **Unknown place name silently eaten (MED).** `Massena, move to Venetia` (no such
   region on the 126-map) → target nulled at both the LLM-validation seam and the fast
   parser → the executor's misleading `Move order requires a destination`. **Fix:**
   movement-family targets pass through unknown so the executor's fuzzy matcher owns the
   verdict (`Region 'Venetia' not found. Nearby: ...`), on BOTH parse paths.
   Tests: `test_sweep5_parse_validation.py` (passthrough + endpoint arms).

Plus corpus hygiene: `mock_only` entry support in `parser_eval.py` (mirror of
`live_only`) — the two V2-55 word-boundary rows pin the FAST parser's "Unknown action"
shape that the live LLM legitimately resolves differently. Live corpus now **432/432**
(2 mock_only skips); mock corpus **433/433** unchanged.

## Final round — what the definitive capture shows working

(JSONL: scratchpad `sweep5_evidence_final.jsonl`; the two earlier consoles are preserved
as the pre-fix failure record.)

- **PF-1 + the new "press on" mapping:** "Marshal Ney, march on Munich" → Mack blocks at
  Swabia (bad-odds interrupt) → typed "press on" → "Ney attacks Mack and wins!
  Continuing his march." — and by turn 3 Ney stands **in Munich**. Target was Munich,
  not "On Munich"; the interrupt resolved in the question's own idiom.
- **PF-2 + the preempt fix:** Soult's literal ASK → typed "give battle" → "Soult pursues
  Mack... 'Soult attack Mack.' No more and no less. (1 AP — Soult executes precise
  orders with fewer couriers.)" — rebound through the preempted slot with a mailbox
  proposal displaced-and-restored beneath it.
- **PF-4:** out-of-range attacks either became a narrated PURSUE ("Ney pursues
  ArchdukeJohn (at Bohemia). Moves to Franconia.") or a clean engagement-lock rejection
  ("Cannot attack elsewhere while engaged — ArchdukeCharles must be dealt with first.")
  — zero objections wasted on unreachable orders.
- **PF-6:** "Bernadotte, hold your ground" → "(2 AP — a standing strategic order...
  For a single-turn tactical hold, order 'defend' at 1 AP.)" — the upgrade priced and
  announced.
- **PF-7 (full chain):** "recruit 5000 artillery for Murat" → arm soft-correction
  ("Murat commands cavalry, Sire"), fixed-corps honesty ("drafted in fixed corps of
  3,000 — your 5,000 is noted"), Intendance pricing shown ("+15%"). "Murat, bombard
  Mack" → "Murat commands no guns... Order a direct assault, or bring an artillery corps
  within range." — rejected, never degraded.
- **Sweep-4 P2 fix:** "grant Holland more autonomy" → executes with the VP-D5 tribute
  legibility ("Tribute rate: 75% → 50% (a permanent income cut)").
- **W6-9 / vassal verbs / scout:** Talleyrand assessment (war score, coalition posture,
  threat movers), "invest in Switzerland" (+10 loyalty, cost + cooldown shown), "Murat,
  scout Swabia" (+ the courteous stand-down of his intended attack).
- **W6-8 estate beat (emergent):** Austria's one-turn occupation of Rhineland saw the
  Austrian AI endow Archduke Charles with "the Duchy of Rhineland"; the recapture
  offered confiscate/respect. The capture pipeline held every gate honestly.
- **PF-3 seam:** "Bernadotte, move to Bohemia" → honest block while defended ("enemy
  forces present! Use ATTACK..."); after Soult's win the capture choice fired and
  "Soult secures Bohemia" flipped control.
- **PF-5:** across 6 turns the ledger income lines re-rendered with changing numbers and
  no duplicate treaty/proposal note spam.

## Open observations routed to Half B

- **(a) Bare "attack" auto-pick:** with no marshal named, the executor attacked with a
  never-addressed marshal (Massena turn 4, Soult turn 6) rather than routing through
  CR-4 focus / CR-2 clarification — adjudicated by the Parsing/UX reviewers.
- **(b) PF-8 route honesty:** "Lannes, march to Copenhagen" printed a route through
  NEUTRAL Prussia/Sweden (Franconia → Berlin → Pomerania → Scania → Copenhagen) —
  passability-honesty question for the reviewers (the closed-border stall fires at the
  border hop, but the printed plan does not disclose the neutral crossings).

**Suite state at capture:** 13,547 passed / 3 skipped; ruff clean; M1–M7 byte-identical
to Sweep 4; corpus mock 433/433, live 432/432.
