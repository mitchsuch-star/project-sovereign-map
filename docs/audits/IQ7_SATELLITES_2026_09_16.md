# IQ-7 "The Satellites Have a Position" — the completion measurement (September 16, 2026)

**Memo of record for row IQ-7's §3 completion.** Landing record = `IMPROVEMENT_QUEUE_SPEC.md`
§1.6; rules = `SYSTEMS_REFERENCE.md` §46; the build contract's §3 (the four arms and the four
things that must hold) is what this memo grades. Every run below is archived under
`docs/audits/playtest_digests/iq7-*` (`digest.md`, `digest.jsonl`, `meta.json`).

**Platform (PR-D4 discipline):** Windows 11, CPython 3.13 (`.venv`), `PYTHONHASHSEED=0`,
mock parser, the tree that lands this row (master `e1cb33a5` + the IQ-7 build, committed as the
next commit — `meta.json` carries the driver revision), `tools/playtest_driver.py` Mode A with a
sandboxed `INK_IRON_SAVE_DIR`, `tools/playtest_scripts/commanded_full40.json`.

## 1. The arms

| # | arm | seeds | settings |
|---|---|---|---|
| 1 | **COMMANDED-GRANT** | historical · austerlitz · marengo | `commanded_full40 --diplomacy accept` (the `--client-petition` dial absent → mirrors `accept` = **grant**) |
| 2 | **COMMANDED-REFUSE** | the same three | as arm 1 + `--client-petition refuse` |
| 3 | **AMBIENT** | historical | unattended (the default `decline` policy → a petition is refused) |
| 4 | **LEVER-DOWN CONTROL** | historical | as arm 1 with the four `vassal` levers AND the driver's `THE_DIGEST_SEES_THE_WEB` set False in-process (`scratchpad/iq7/measure.py`, hash-pinned) |

The contrast figure (§1.0 re-baseline, run September 16 on the post-IQ-6 tree, identical to the
recon's `e38be000` figures): a commanded France at peace from turn 5 loses **2 / 3 / 3** of its
three satellites by turns 30–33 — Switzerland and Holland rebel on every seed, the Kingdom of
Italy is lost on two (once to Switzerland's VS-6 bribe), and the only vassal decision the player
ever sees is the rebellion modal 0–2 turns before the break.

## 2. What counts as done — all four hold

### 2.1 The consequential non-rebellion decision (arm 1 vs arm 2, same seeds)

| seed | arm 1 GRANT — petitions granted (turn: court) | satellites held at t40 | rebellion modals | Fr@40 / gold | arm 2 REFUSE — refusals | lost by | modals | Fr@40 / gold |
|---|---|---|---|---|---|---|---|---|
| historical | **5** — t6 Holland (relief), t6 Kingdom of Italy, t7 Switzerland, t15 Holland, t17 Switzerland | **3 / 3** | **0** | 28 / 109,509 | 4 — t6 Holland, t6 KoI, t7 Switzerland, t15 KoI | **0 / 3 by t22** (Switzerland rebels; Holland defects to Switzerland t21; KoI defects to Holland t22) | 3 | 29 / 94,387 |
| austerlitz | **6** — t6 Holland, t6 KoI, t7 Switzerland, t15 Holland, t16 KoI, + one | **3 / 3** | **0** | 28 / 108,831 | 3 — t6 Holland, t6 KoI, t7 Switzerland | **0 / 3 by t21** (Switzerland rebels t20; Holland defects t21; KoI rebels t21) | 2 | 29 / 95,886 |
| marengo | **6** — t5 Holland, t6 KoI, t8 Switzerland, t15 Holland, t16 KoI, + one | **3 / 3** | **0** | 29 / 114,693 | 3 — t5 Holland, t6 KoI, t8 Switzerland | **0 / 3 by t23** (Holland defects t23; KoI rebels t23; Switzerland rebels) | 5 | 29 / 104,255 |

- Every seed of arm 1 shows the digest line `POPUP diplomatic_dialogue: <court>, client_petition #N → grant the petition` at a loyalty ≥ 60 (the first at turn 5–6, the satellite at 88–100), and the grant's effect is in the same run: the ledger's `vassals` bit reads the +10 the turn after, tribute reads 0 for the next eight collections (the `proposal_result` quotes *"remitted for 8 collections (2696g forgone) … standing 0 → 20 (+1 loyalty a turn). Cost: 1 DP."*), and on two of three seeds a province (Tyrol) is ceded through the VS-3 path — which is why France ends on 28 rather than 29 there.
- **Consequential, proven by the contrast:** the two answers produce different webs at turn 40 on every seed — grant holds **3 / 3 / 3**, refuse holds **0 / 0 / 0** by turns 21–23, HEAD held 1 / 0 / 0 by turns 30–33. (The prototype's expectation was 5 / 6 / 6 petitions and exactly this contrast; it reproduced.)
- The honest limit the contract recorded holds: **granting dominates economically** on the scripted board (arm 1 ends 7–12k gold richer than the control's 102,218 despite the remitted tribute — a held web out-earns a lost one), so the trade-off a player feels is the PROVINCE ask and the refusal's cost, not the gold.

### 2.2 Not a rebellion

The counted decisions are all `client_petition`. Rebellion-modal counts per arm: GRANT **0 / 0 / 0**, REFUSE 3 / 2 / 5, AMBIENT 0, CONTROL 2.

### 2.3 The stated expectation

The §0.4 sentence — *"A loyal satellite is the Empire's settled frontier …"* — is verbatim at the head of `SYSTEMS_REFERENCE.md` §46 and in `IMPROVEMENT_QUEUE_SPEC.md` §1.6.

### 2.4 Legibility

The `vassals` LEDGER bit is on **40 of 40** LEDGER rows of every arm (`… · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100`). One petition popup, as the player reads it (the shipped boot, turn 6, Switzerland's relief — every court name through `display_nation`, no raw tag):

> Sire, Chancery of Helvetia brings a petition from Switzerland. Switzerland petitions the Emperor for relief from its tribute.
>
> Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its standing at our court would steady its loyalty by +1 a turn (now +0), for 1 DP.
> Refuse it, and Switzerland loses 10 loyalty and 20 standing — its drift worsens to -1 a turn from +0; nothing is charged.
> Left unanswered at the turn's end, the petition lapses — and a lapse is a refusal.
>
> Talleyrand: "A client that asks for relief is naming its own drift, Sire, while it still has the standing to ask. Grant it and the bond deepens; refuse it and that standing is spent."

Options: **Grant the petition** / **Refuse the petition** (no Counter). One Vassals ledger card row (Holland, parked at loyalty 50 for the probe): `standing "no standing to petition" · next_petition_in 0 · bond "no bond yet — each petition honoured is worth +1/turn" · remission_left 0 · relation 0 · relation_modifier 0`, beside the pre-existing loyalty/forecast/tribute/contribution keys.

## 3. The other arms

- **AMBIENT (historical):** Switzerland's turn-6 relief petition is refused by the unattended policy and Switzerland **defects to Britain at turn 15** (VS-6) instead of rebelling at turn 22 as on HEAD; Holland stays; France ends on **5** provinces — the same 5 as HEAD's ambient arm, so the passive-France guard (±1) holds.
- **CONTROL (all five levers down, in-process, hash-pinned):** `digest.md` and `digest.jsonl` are **byte-identical to the §1.0 re-baseline except the four rail lines that gained "Sire — "** — Builder A's R7 fix (IQ7-X6), which the driver renders verbatim. No petition, no `vassals` bit, the same two rebellions at turns 29 and 31.
- **Popup load:** 5–6 petitions per 40 turns on the grant arm. Each is echoed once more on the digest as `(stale passthrough — #N already answered this chain)` — the pre-existing mailbox cache echo, routed as IQ7-X5.

## 4. `BASELINE_SERIES` (the harness board, `_emit_series`)

Four hash-pinned subprocess arms with the four levers set in the child: **arm 0 (all False) byte-identical to the recorded series; R (R1+R2 only) identical; P (petitions up, lapse lever down) identical; PL (shipped) diverges at index [20]** — 41 → 31, the tail 8 / 5 / 2 / 0 instead of 18 / 15 / 12 / 0 — with France on 9 provinces at turn 40 in every arm. The lapse lever is the sole mover: the harness never answers, so Switzerland's turn-6 relief petition lapses and counts as a refusal. **The causal chain on the series board** (verified by an independent `reduce_threat` wrap and a counterfactual that suppresses only the one source): the series board is NOT the driver's ambient arm — France issues nothing and nobody answers. Switzerland (86) petitions for relief at turn 6 and the lapse costs 86 → 76 and relation 0 → −20; it petitions again at exactly 60 at turn 14 and that lapse costs 60 → 50, relation → −40; at 47 it is under the courting line, so Britain, Russia and Austria court it once a turn under the WO-8 cap, turns 15–20 (47 → 0); it rebels at turn 21 — index [20] — and the `vassal_rebellion` threat source is the step: 43 + 1 − 3 − 10 = 31. On the prior series the same satellite was lost at turn 29 to Britain's VS-6 bribe (the `vassal_defection` −10 at [28] → [29] — which the Phase-3 comment had mislabelled a rebellion). The offset over [20]–[28] is that one −10 arriving nine readings earlier; the Kingdom of Italy's elimination (−13 at [25] → [26]) is identical in both arms. **Pins that read this board, flipped consciously:** the WO slice-9 courting cap now delays Switzerland's break from 16 to 21 (was 28 → 30; both exits are real rebellions now, both were Britain's bribe before); the WO slice-10 ungated arm collapses 35 times (was 21 — the seven new hits are Bavaria's Deroy ordering `attack Bern` after Switzerland's earlier break, collapsed onto Bernadotte by the broad diplomatic check) and writes 28 failed actions against the gated arm's unchanged 5; the AI-V Arm-B variance pin's three-fact signature is EQUAL for historical and ulm (both war turns [21]), so the comparison was widened to the turn each court first reaches `fight` and the eliminations, and the narrowing it hides is routed (`DESIGN_REFINEMENT.md` IQ7-D4). The series is re-recorded ONCE with this attribution (`tests/test_ai_intent_threat_migration.py`); M1–M7 are byte-identical by construction (the combat harness never ends a turn).

## 5. Pillar re-score — ⚠ FOR USER CONFIRMATION

**Vassals 6.5 → 7.0.** Up because the web now produces a decision that is not a rebellion, on every seed, while the client is still loyal, and the two answers lead to different empires at turn 40 — a competent Emperor sees the system, and what a loyal vassal is FOR is stated. Held below 7.5 because the decision is one modal five or six times in forty turns, granting is economically dominant on the scripted board, and the satellite still fields no men (VD-C, the Contingent, is the row that would raise it further). Not above what the digests show.
