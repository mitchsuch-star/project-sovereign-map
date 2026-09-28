# SR-5b â€” the A2 strangulation arc and the SHUT OUT arm, played (September 28, 2026)

Score Mandate Chunk 5, slice SR-5b "The second road at sea". The standing DEF-5 evidence the naval spec
has owed since August 2 (`NAVAL_SPEC.md` Â§15.12: the NV-10 drive was *scripted* against the executor and
"does not falsify the 80%-closure acceptance arm"). This memo is that arc **played** â€” every order through
`POST /command` with the mock parser, the ambient world live underneath â€” on the committed instrument.

## Method

- **Script** `tools/playtest_scripts/sr5b_shut_out.json`. France declares war on **Portugal** (2 ports â€” Junot,
  1807) and the **Papal States** (1 port â€” 1808); **Soult** marches on Lisbon; **Massena** marches on Rome (his
  march is re-issued, because cannon fire at Munich pulls him to the guns); Ney, Davout, Lannes, Murat and the
  Emperor keep the war with Austria in the field; Soult then turns on the British corps that land in Portugal.
- **Two policies.** `--diplomacy accept` is the A2 sue-path: the driver takes Britain's suit when it comes, which
  is the arc's end. `--diplomacy decline` is the SHUT OUT arm: France keeps the war with Britain â€” at peace the
  System closes nothing, because `naval.closure_against` counts the ports of courts AT WAR with Britain (plus
  vassals, members and conquered capitals).
- **Three seeds** (`historical`, `ulm`, `austerlitz`), 40 turns, `--declare-war proceed` (the declarations are the
  arm's point), saves every 2 turns, read by `tools/sr5b_shut_out_probe.py` (read-only).
- **Archives** `docs/audits/playtest_digests/sr5b-{accept,decline}-{historical,ulm,austerlitz}/`.
- **The SHUT OUT reading** (`congress._shut_out_reading`): closure â‰¥ `cs_shutout_pct` (50%, i.e. 13 of 26 ports)
  **and** no British corps standing on the Continent.

## Findings

1. **The A2 sue-path is played.** Britain proposes an armistice while losing on **turn 8 on six arms of six**, at war
   exhaustion 74â€“77, and again on turns 14â€“24 when refused or when the war resumes (in peace terms on turn 39 of
   `decline-ulm`). No soldier crosses to Britain. The Continental System contributes little: the closure reached
   tier 1 (â‰¥ 40%, +1 exhaustion a turn) and never tier 2; the war's own tick (+8 a turn) carries Britain to the
   table. Anchor A2's "â‰¥ 80% closure" is not reachable in play â€” the peak was 50%.

2. **The SHUT OUT reading never held in 240 played turns.** Its closure term was met exactly â€” 13 of 26 â€” on three
   arms (`decline-ulm` turns 10â€“14 with Lisbon and Rome French; `accept-ulm` turns 20â€“22 and `accept-austerlitz`
   turn 22 with Lisbon in Spain's hands), and at every one of those moments a British corps stood on the Continent:
   Wellesley, Moore, Paget or Shrapnel. Britain's descents (NV-5: a shore that will receive it) land where the System
   bites, in Portugal; Britain commissions new marshals (P1.75) and ships them again after Soult destroys one
   (Wellesley at Cartagena, `decline-historical` turn 15). Routed as a design question â€” `DESIGN_REFINEMENT.md`
   **SR5B-D1** â€” rather than changed: the Peninsular War was Britain's answer to the System, and whether a beachhead
   corps should keep Britain "in" is the user's call.

3. **At peace the System closes nothing.** Every accepted British armistice drops the closure from 10â€“13 of 26 to
   0â€“5 (the ports of a court at peace with Britain are open). Working as designed â€” the System was a war measure â€”
   and recorded so a reader of the tables is not surprised.

4. **Declining every offer ruins France.** The decline policy refuses Austria's and Prussia's tables too:
   `decline-historical` ends in THE FALL on turn 15 (the Emperor, captured by Austria in December 1805, a prisoner
   for 10 turns â€” the GE-1 clock), `decline-austerlitz` falls to 8 provinces and ends, `decline-ulm` holds 5. The
   arm measures the System, not a sound strategy.

5. **Found playing the arm: SR5B-1 (fixed in the slice).** The first trial stalled Soult at Bearn for thirty turns:
   `Soult, attack Lisbon`, refused "cannot reach", had cancelled his standing march before the order ran
   (`BUG_FIXES.md` Â§SR-5b The Second Road at Sea).

## Britain's offers (from the digests)

| arm | Britain's armistice / peace offers (turn â†’ the driver's answer) |
|---|---|
| accept-historical | 8 â†’ accept Â· 14 â†’ accept |
| accept-ulm | 8 â†’ accept (peace follows) |
| accept-austerlitz | 8 â†’ accept Â· 24 â†’ accept |
| decline-historical | 8 â†’ reject Â· 14 â†’ reject (THE FALL, turn 15) |
| decline-ulm | 8 â†’ reject Â· 18 â†’ reject Â· 39 (peace) â†’ reject |
| decline-austerlitz | 8 â†’ reject Â· 15 â†’ reject Â· 22 â†’ reject |

## The arms

### `sr5b-accept-historical`

| turn | closed / needed | British corps ashore | Britain WE | France–Britain | Lisbon | Rome | French provinces |
|---|---|---|---|---|---|---|---|
| 2 | 10 / 13 | — | 13 | WAR | Por | Pap | 28 |
| 4 | 10 / 13 | — | 39 | WAR | Por | Pap | 30 |
| 6 | 10 / 13 | Paget | 55 | WAR | Por | Pap | 29 |
| 8 | 3 / 13 | — | 74 | ARMISTICE | Por | Pap | 27 |
| 10 | 3 / 13 | — | 90 | ARMISTICE | Por | Pap | 27 |
| 12 | 3 / 13 | — | 106 | ARMISTICE | Por | Pap | 27 |
| 14 | 10 / 13 | Wellesley | 123 | WAR | Por | Pap | 27 |
| 16 | 0 / 13 | Wellesley | 0 | ARMISTICE | Por | Pap | 27 |
| 18 | 0 / 13 | — | 0 | ARMISTICE | Por | **Fr** | 28 |
| 20 | 8 / 13 | — | 8 | WAR | Por | **Fr** | 28 |
| 22 | 8 / 13 | Shrapnel | 24 | WAR | Por | **Fr** | 26 |
| 24 | 8 / 13 | Shrapnel | 40 | WAR | Por | **Fr** | 23 |
| 26 | 8 / 13 | Shrapnel | 56 | WAR | Por | **Fr** | 23 |
| 28 | 8 / 13 | Shrapnel | 72 | WAR | Por | **Fr** | 23 |
| 30 | 8 / 13 | Shrapnel | 88 | WAR | Por | **Fr** | 22 |
| 32 | 0 / 13 | Shrapnel | 0 | PEACE | Por | **Fr** | 22 |
| 34 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 22 |
| 36 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 22 |
| 38 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 22 |
| 40 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 22 |

### `sr5b-accept-ulm`

| turn | closed / needed | British corps ashore | Britain WE | France–Britain | Lisbon | Rome | French provinces |
|---|---|---|---|---|---|---|---|
| 2 | 10 / 13 | — | 13 | WAR | Por | Pap | 28 |
| 4 | 10 / 13 | — | 39 | WAR | Por | Pap | 29 |
| 6 | 11 / 13 | Paget | 56 | WAR | Por | **Fr** | 30 |
| 8 | 3 / 13 | Paget | 77 | ARMISTICE | Por | **Fr** | 30 |
| 10 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 25 |
| 12 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 25 |
| 14 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 25 |
| 16 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 25 |
| 18 | 11 / 13 | — | 1 | WAR | Por | **Fr** | 25 |
| 20 | 13 / 13 **(met)** | Wellesley | 19 | WAR | Spa | **Fr** | 22 |
| 22 | 13 / 13 **(met)** | Wellesley | 37 | WAR | Spa | **Fr** | 15 |
| 24 | 12 / 13 | — | 55 | WAR | Spa | **Fr** | 14 |
| 26 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 15 |
| 28 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 15 |
| 30 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 15 |
| 32 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 15 |
| 34 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 15 |
| 36 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 15 |
| 38 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 15 |
| 40 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 15 |

### `sr5b-accept-austerlitz`

| turn | closed / needed | British corps ashore | Britain WE | France–Britain | Lisbon | Rome | French provinces |
|---|---|---|---|---|---|---|---|
| 2 | 10 / 13 | — | 13 | WAR | Por | Pap | 28 |
| 4 | 10 / 13 | — | 39 | WAR | Por | Pap | 31 |
| 6 | 11 / 13 | Paget | 56 | WAR | Por | **Fr** | 31 |
| 8 | 3 / 13 | — | 77 | ARMISTICE | Por | **Fr** | 29 |
| 10 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 29 |
| 12 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 29 |
| 14 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 28 |
| 16 | 0 / 13 | — | 0 | PEACE | Por | **Fr** | 28 |
| 18 | 11 / 13 | — | 1 | WAR | Por | **Fr** | 28 |
| 20 | 11 / 13 | Paget, Wellesley | 19 | WAR | Por | **Fr** | 28 |
| 22 | 13 / 13 **(met)** | Paget, Wellesley | 37 | WAR | Spa | **Fr** | 27 |
| 24 | 5 / 13 | Paget, Wellesley | 55 | ARMISTICE | Spa | **Fr** | 27 |
| 26 | 5 / 13 | Paget, Wellesley | 71 | ARMISTICE | Spa | **Fr** | 27 |
| 28 | 5 / 13 | — | 87 | ARMISTICE | Spa | **Fr** | 27 |
| 30 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 27 |
| 32 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 27 |
| 34 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 27 |
| 36 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 27 |
| 38 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 27 |
| 40 | 0 / 13 | — | 0 | PEACE | Spa | **Fr** | 27 |

### `sr5b-decline-historical`

| turn | closed / needed | British corps ashore | Britain WE | France–Britain | Lisbon | Rome | French provinces |
|---|---|---|---|---|---|---|---|
| 2 | 10 / 13 | — | 13 | WAR | Por | Pap | 28 |
| 4 | 10 / 13 | — | 39 | WAR | Por | Pap | 30 |
| 6 | 10 / 13 | Paget | 55 | WAR | Por | Pap | 30 |
| 8 | 10 / 13 | — | 74 | WAR | Por | Pap | 28 |
| 10 | 10 / 13 | — | 90 | WAR | Por | Pap | 25 |
| 12 | 10 / 13 | Wellesley | 106 | WAR | Por | Pap | 25 |
| 14 | 11 / 13 | Wellesley | 123 | WAR | Por | **Fr** | 26 |

### `sr5b-decline-ulm`

| turn | closed / needed | British corps ashore | Britain WE | France–Britain | Lisbon | Rome | French provinces |
|---|---|---|---|---|---|---|---|
| 2 | 10 / 13 | — | 13 | WAR | Por | Pap | 28 |
| 4 | 10 / 13 | — | 39 | WAR | Por | Pap | 29 |
| 6 | 11 / 13 | Paget | 56 | WAR | Por | **Fr** | 30 |
| 8 | 11 / 13 | — | 77 | WAR | Por | **Fr** | 31 |
| 10 | 13 / 13 **(met)** | Wellesley | 97 | WAR | **Fr** | **Fr** | 27 |
| 12 | 13 / 13 **(met)** | Moore | 115 | WAR | **Fr** | **Fr** | 23 |
| 14 | 13 / 13 **(met)** | Moore | 133 | WAR | **Fr** | **Fr** | 20 |
| 16 | 10 / 13 | Moore, Shrapnel | 151 | WAR | **Fr** | **Fr** | 17 |
| 18 | 10 / 13 | Moore, Shrapnel | 167 | WAR | **Fr** | **Fr** | 16 |
| 20 | 9 / 13 | Moore, Shrapnel | 183 | WAR | **Fr** | **Fr** | 14 |
| 22 | 9 / 13 | Moore, Shrapnel | 199 | WAR | **Fr** | **Fr** | 13 |
| 24 | 9 / 13 | Moore, Shrapnel | 200 | WAR | **Fr** | **Fr** | 9 |
| 26 | 9 / 13 | Moore, Shrapnel | 200 | WAR | **Fr** | **Fr** | 8 |
| 28 | 9 / 13 | Moore, Shrapnel | 200 | WAR | **Fr** | **Fr** | 7 |
| 30 | 9 / 13 | Moore, Shrapnel | 200 | WAR | **Fr** | **Fr** | 7 |
| 32 | 9 / 13 | Moore, Shrapnel | 200 | WAR | **Fr** | **Fr** | 6 |
| 34 | 9 / 13 | Moore, Shrapnel | 200 | WAR | **Fr** | **Fr** | 6 |
| 36 | 7 / 13 | Moore, Shrapnel | 200 | WAR | **Fr** | **Fr** | 5 |
| 38 | 7 / 13 | Moore, Shrapnel | 200 | WAR | **Fr** | **Fr** | 5 |
| 40 | 7 / 13 | Moore, Shrapnel | 200 | WAR | **Fr** | **Fr** | 5 |

### `sr5b-decline-austerlitz`

| turn | closed / needed | British corps ashore | Britain WE | France–Britain | Lisbon | Rome | French provinces |
|---|---|---|---|---|---|---|---|
| 2 | 10 / 13 | — | 13 | WAR | Por | Pap | 28 |
| 4 | 10 / 13 | — | 39 | WAR | Por | Pap | 31 |
| 6 | 11 / 13 | Paget | 56 | WAR | Por | **Fr** | 32 |
| 8 | 11 / 13 | — | 77 | WAR | Por | **Fr** | 30 |
| 10 | 11 / 13 | — | 95 | WAR | Por | **Fr** | 30 |
| 12 | 10 / 13 | Wellesley | 112 | WAR | Por | **Fr** | 29 |
| 14 | 10 / 13 | Wellesley | 128 | WAR | Por | **Fr** | 28 |
| 16 | 7 / 13 | Shrapnel, Wellesley | 146 | WAR | Por | **Fr** | 29 |
| 18 | 7 / 13 | Shrapnel, Wellesley | 162 | WAR | Por | **Fr** | 26 |
| 20 | 7 / 13 | Shrapnel, Wellesley | 178 | WAR | Por | **Fr** | 26 |
| 22 | 7 / 13 | Shrapnel | 194 | WAR | Por | **Fr** | 26 |
| 24 | 7 / 13 | Shrapnel, Wellesley | 200 | WAR | Por | **Fr** | 22 |
| 26 | 7 / 13 | Shrapnel, Wellesley | 200 | WAR | Por | **Fr** | 18 |
| 28 | 7 / 13 | Shrapnel, Wellesley | 200 | WAR | Por | **Fr** | 16 |
| 30 | 7 / 13 | Shrapnel, Wellesley | 200 | WAR | Por | **Fr** | 15 |
| 32 | 7 / 13 | Shrapnel, Wellesley | 200 | WAR | Por | **Fr** | 15 |
| 34 | 7 / 13 | Shrapnel, Wellesley | 200 | WAR | Por | **Fr** | 12 |
| 36 | 7 / 13 | Shrapnel, Wellesley | 200 | WAR | Por | **Fr** | 9 |
| 38 | 7 / 13 | Shrapnel, Wellesley | 200 | WAR | Por | **Fr** | 8 |

