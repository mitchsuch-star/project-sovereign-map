# FA-D27 — the balance measurement (September 11, 2026)

> Measured at master `9f0681be` (FA slice 17 parts 0–h all landed) with the
> committed driver `tools/playtest_driver.py` (Mode A, in-process, mock parser,
> `PYTHONHASHSEED=0`, the turn-boundary reseed), **touching no constant**. Every
> run is 40 driven turns from the 1805 boot. Runs live in the session scratch
> directory (`d27_runs/<arm>-<seed>/digest.md`); the table below is the whole
> evidence. The instrument is slice 17 part f's — it answers the paradox /
> rebellion / sabotage decisions, presses nothing greyed, and reads the WHOLE
> mailbox, which is what makes the `accept` arm meaningful (slice 15's driver
> could not activate a major court's settlement offer at all).

## 0. The question

The slice-4 review round measured an unattended France overrun on 8/8 seeds
(Fr@40 mean 2.2) and a scripted France on 5/5 arms, and filed FA-D27 as a gate:
*does the AI now beat an unattended France, and is that wrong?* The round's own
eight fixes then moved the passive board back to France 5. Slices 5–17 have
landed since. This memo re-measures the same three shapes plus the two the
driver could not run before: a France that ANSWERS the coalition's peace offer,
and a France that PROPOSES peace.

## 1. The arms

| arm | policy | seeds |
|---|---|---|
| `ambient` | no orders; every incoming proposal declined (the slice-4 shape) | historical, ulm, austerlitz, jena, marengo |
| `accept` | no orders; `--diplomacy accept` (the coalition's settlement offer is answered) | historical, ulm, austerlitz |
| `propose` | no orders; `--diplomacy propose` (one bilateral peace overture per turn, round-robin over the at-war courts) | historical, ulm, austerlitz |
| `tyrant` | `weird_tyrant.json` — 30 loops of all-out attack, plunder, insist; decline everything | historical, ulm, austerlitz |
| `emperor` | `np_campaign_emperor.json` — 22 loops of the Emperor at the front, fortify, trust; decline everything | historical, ulm, austerlitz |

## 2. The board (`Fr@N` = French provinces after N end-turns; boot = 28)

| run | Fr@10 | Fr@20 | Fr@30 | Fr@40 | threat (last 6) | Paris | Napoleon | battles |
|---|---|---|---|---|---|---|---|---|
| ambient-historical | 21 | 6 | 6 | **5** | 55 52 51 50 51 52 | held | free | 34 |
| ambient-ulm | 28 | 19 | 14 | **12** | 16 15 16 17 16 15 | held | free | 44 |
| ambient-austerlitz | 28 | 13 | 5 | **8** | 27 26 27 31 33 35 | held | free | 37 |
| ambient-jena | 17 | 11 | 11 | **10** | 8 5 4 3 2 1 | held | free | 35 |
| ambient-marengo | 28 | 29 | 29 | **29** | 40 38 40 42 44 46 | held | free | 24 |
| accept-historical | 28 | 27 | 27 | **27** | 34 32 30 28 26 24 | held | free | 17 |
| accept-ulm | 28 | 28 | 28 | **28** | 30 28 26 24 22 10 | held | free | 7 |
| accept-austerlitz | 28 | 28 | 28 | **28** | 33 31 29 27 25 23 | held | free | 5 |
| propose-historical | 28 | 27 | 29 | **29** | 70 68 68 68 68 68 | held | free | 23 |
| propose-ulm | 28 | 28 | 28 | **28** | 30 28 26 24 22 20 | held | free | 12 |
| propose-austerlitz | 28 | 27 | 27 | **27** | 26 24 22 20 18 16 | held | free | 10 |
| tyrant-historical | 28 | 28 | 18 | **10** | 60 57 46 45 44 43 | held | free | 34 |
| tyrant-ulm | 32 | 29 | 28 | **11** | 54 53 52 51 50 47 | held | free | 49 |
| tyrant-austerlitz | 27 | 15 | 4 | **2** | 4 3 4 3 2 1 | held | free | 49 |
| emperor-historical | 29 | 31 | 33 | **24** | 95 92 91 90 79 78 | held | **captured t35** | 55 |
| emperor-ulm | 28 | 17 | 11 | **13** | 2 3 2 1 0 0 | held | free | 27 |
| emperor-austerlitz | 28 | 28 | 29 | **28** | 79 77 75 73 71 69 | held | **captured** | 42 |

Seed means: ambient Fr@30 **13.0** / Fr@40 **12.8** (the slice-4 review's "after"
tree: 3.9 / 2.2; its own fixes then measured 5); accept 27.7 / 27.7; propose
28.0 / 28.0; tyrant 16.7 / 7.7; emperor 24.3 / 21.7. Paris held on 17 of 17
runs; no French corps count is tabulated here (the digest's ledger row carries
provinces, not the roster).

## 3. What the arms say

1. **The passive, diplomacy-refusing France is still overrun — on 4 of 5 seeds
   (5, 12, 8, 10 provinces at turn 40), not 8 of 8, and one seed (`marengo`)
   holds all 29.** The board moved 2.2 → 12.8 at turn 40 since the slice-4
   measurement without any constant changing; the movers are the slice-4
   review's eight AI-side fixes, slices 5–16, and slice 17 part 0 (a
   recovering corps annexes nothing) — none of them a balance number.
2. **The war is decidable by DIPLOMACY, and the instrument can now show it.**
   With `--diplomacy accept` Britain's settlement offer arrives by turn 5
   (`MAILBOX #8 Britain incoming_settlement_offer → activated` →
   `accept_settlement_offer` → `confirm_settlement` → *Settlement of France +
   Spain + Holland + Bavaria + KingdomOfItaly vs Britain + Austria + Russia:
   settlement ratified*) and France keeps 27–28 provinces on 3 of 3 seeds;
   Britain re-declares later and offers terms again. With `--diplomacy
   propose` the same three seeds end 27–29. **The slice-15 review's struck
   claim ("with `--diplomacy accept` the same seed goes 6 → 27") was struck
   because it did not reproduce on THAT driver — on this one it reproduces:
   ambient-historical 5 vs accept-historical 27.** The instrument, not the
   engine, was the confound.
3. **A fighting France that refuses peace pays for it.** The tyrant script
   (all-out attack, plunder, insist) ends 2–11; the Emperor script holds
   13–28 but **Napoleon is captured on 2 of 3 seeds** (historical turn 35 by
   Kutuzov at Vienna; austerlitz) — and the run continues, because captivity
   is peace LEVERAGE (NP-4's Brétigny rule puts his return as the first clause
   of any draft), not an ending.
4. **Nothing in the table shows the AI "too strong" rather than "finally not
   wasting its actions".** A France that does nothing and refuses every offer
   loses the Third Coalition war on most seeds; a France that answers the
   offer, or asks for peace, keeps its map; a France that fights without
   diplomacy holds most of its provinces and loses its Emperor. Those are the
   three outcomes a strategy game about 1805 should have.

## 4. The ruling recorded on the row (FA-D27)

**RULED — option (a), leave the military balance.** The measurement that the
gate asked for exists now and says the balance is decided by whether France
answers the table, which is the design. Re-open condition: if the Phase-3
played campaign (a scripted France that fights AND answers diplomacy on the
part-f driver) ends below 20 provinces on 3 or more of 5 seeds at turn 40, or
if the PLAYED (human) campaign loses Paris before turn 20 without a refused
peace offer on the record, re-open at option (b) — a France-side lever
(starting AP or treasury), never an AI-side nerf. Dissent: the ambient arm's 4
of 5 collapses are a heavy tax on a player who ignores the mailbox; the answer
is the letter-book's legibility (already landed) and FA-D7/FA-D17's
peace-route honesty (ruled below), not a constant.

FA-D29 (a 500-man stub shields a garrison from P4) is measured and ruled in the
same session — see its row.
