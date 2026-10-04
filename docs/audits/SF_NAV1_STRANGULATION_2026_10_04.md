# SF-NAV-1 — the strangulation, played (Score Finish Step 6, October 4, 2026)

`docs/SCORE_FINISH_SPEC.md` §3 Step 6 asked for **one arm that closes 13 of 26 ports, drives out the corps
`continent_holders` names, holds SHUT OUT through a sitting, and records why Britain sues — and, if the
Continental System's tier 2 stays unreachable, the A2 anchor goes to the user.** This memo is that arm, played
through `POST /command` on the mock parser with the ambient world live underneath, and what it found.

## Method

- **Script** `tools/playtest_scripts/sf_nav1_strangulation.json`. France keeps its war with Britain **alone** —
  it signs with Austria and Russia when they ask, and refuses Britain, Portugal, the Papal States and Naples
  (`--diplomacy accept --decline-from Britain,Portugal,PapalStates,Naples`). It takes the capitals whose ports the
  System counts — **Lisbon** (Soult; Portugal's 2 ports — Junot, 1807), **Rome** (Massena; 1 port — 1808) and
  **Naples** (Massena; 1 port) — holds the **Normandy beach** against Moore's Channel crossing (Lannes,
  fortified), and drives every British corps that lands off the Continent (Soult hunts Paget, Wellesley and
  Shrapnel by name). The Emperor stays out of the fighting. `--objection insist` (marshals do what they are told);
  `--declare-war proceed` (the declarations are the arm's point).
- **Three seeds** (H A M — historical, austerlitz, marengo), 30 turns, a save every turn, read by the new
  read-only probe `tools/sf_nav1_strangulation_probe.py` (the closure, the SHUT OUT reading, the British corps on
  the Continent, Spain's state with Britain, Britain's war exhaustion and the System's tier per turn; Britain's
  envoys off the digest). The arm is the benchmark's `NAV1-H/A/M`.
- **Four drafts were played on the way** (v1 … v4; the drafts were not kept — the findings below were measured
  across them and re-read on the committed arm): each failure taught the arm something the game was right about — Massena answers cannon
  fire unasked (an aggressive marshal), an Emperor in the field is an Emperor captured (two drafts ended in THE
  FALL when Austria's peace was refused), Moore crosses the Channel on foot where the Royal Navy covers it unless
  Normandy is held, and a peace accepted before Lisbon falls keeps Lisbon Portuguese.

## Measured — the final arm

| seed | peak closure | SHUT OUT held | Spain's exit | last British corps on the Continent | Britain first sues |
|---|---|---|---|---|---|
| historical | **14 of 26** (tier 1) | **turn 11** (1 turn) | turn 16 | turn 16 | turn 8 (armistice, WE 79, tier 1) |
| austerlitz | 12 of 26 (tier 1) | never | turn 16 | turn 14 | turn 8 (armistice, WE 79, tier 1) |
| marengo | **13 of 26** (tier 1) | **turns 13–15** (3 turns) | turn 16 | turn 30 | turn 8 (armistice, WE 70, tier 0) |

(The v3 draft read the same shape: marengo held turns 13–15 at 14 of 26, historical turn 11.) **Re-read at Step 6's exit on
the committed benchmark arms `NAV1-H/A/M`** (archive `docs/audits/score_runs/2026_10_04_step6/arms/NAV1-*`, the probe read the
run’s saves, which are never archived): every figure in the table reproduces.

1. **SHUT OUT holds on a played board — for the first time.** The SR-5b arm never saw it in 240 played turns
   (SR5B-D1). Here the closure term (13 of 26) and the corps term (no British corps on the Continent) overlapped on
   two seeds of three: historical turn 11, marengo turns 13–15. The British corps were driven out by the sword —
   Soult took Britain's whole bench of three (`marshal_pool`): on historical Paget at Leon (turn 8), Wellesley at
   Lisbon (turn 9) and Shrapnel at Leon (turn 17); on marengo Paget (8), Shrapnel (11) and Wellesley (13) — which is
   what opened the turn-13 window. Moore's 30,000 are twice the transports' lift, and with Lannes on the Normandy
   beach he crossed only on marengo's turn 30. **A prisoner comes back with a peace:** on austerlitz Spain took
   Wellesley at Madrid on turn 14, made its peace with Britain on turn 16 — and Wellesley put 5,000 men ashore at
   Lisbon again that same turn.

2. **It never holds through a sitting (8 turns).** On **every seed Spain's war with Britain ends on turn 16** — the
   exhausted-pair exit (`settlement_third_party.PAIR_EXIT_*`: both courts at war exhaustion ≥ 120, ten turns at
   war, and their pair's war score within ±15, because Spain and Britain never fight each other) — and the
   closure falls by Spain's 3 ports, to 10–11. The window the System can hold is the turns between the last
   British corps leaving (turns 12–16) and Spain's exit (turn 16): 0–3 turns.

3. **Making up Spain's three ports takes the long campaign or a treaty the table cannot sign.** Without Spain
   the System needs Lisbon, Rome, Naples **and** Vienna **and** Hanover (France 4 + Holland 2 + Italy 1 + Portugal
   2 + the Papal States 1 + Naples 1 + Austria 1 + Hanover 1 = 13). The historical lever — the peace that enrols
   a beaten court in the System (Tilsit: Russia, 1807) — exists as the settlement's `forced_alliance` clause with
   `includes_continental_system`, but it is **settlement-tier**: the separate peace cannot carry it ("Your draft
   for Austria holds a forced alliance. Only a joint settlement can seal that"), and the joint table cannot be
   sealed while Britain fights on in the same war (the 1805 boot folds all seven starting wars into one instance,
   and Britain refuses). Measured on the v3 draft's turn 9.

4. **Tier 2 is unreachable on the played arm.** Peak 14 of 26 (54%); tier 2 wants 16 (60%), the A2 anchor 21
   (80%). **Under the spec's own rule, the A2 anchor goes to the user** — §6 row 17.

5. **Why Britain sues.** Britain asks for an armistice on **turn 8 on all three seeds**, at war exhaustion 70–79,
   with the System at tier 0–1: the war's own tick (+8 a turn) carries Britain to the table; the System adds at
   most +1 a turn (tier 1). Refused, she asks again on turns 10–29 (armistice or a settlement offer), her
   exhaustion pinned at 200 from turn 23. The System is a pinch, not the reason.

## Found on the way (fixed in Step 6)

- **SF6-X1** — a confirmed sea expedition left the marshal's standing order standing: Oudinot, landed at Munster,
  "marches to Ulster. 7 regions to Normandy" — his march to the yard walked him off his own beachhead. Played on
  the descent arm's re-stage (SF-V6).
- **SF6-X2** (found by the exit) — the SEA arm's landing had drifted out of a yard's reach since the baseline: Paget's
  Peninsula corps met Oudinot at Guyenne on his road to the Bordelais yard, so both landing lines were refused and
  naval F2 read SCRIPT PRECONDITION on Step 5's tree too. The arm now marches him to the Normandy yard.

## Routed

- **§6 row 17 (the user's): SF-NAV-1-D1 "The System outlives Spain's exit" — the A2 anchor.** Options and a
  recommendation are on the row (`SCORE_FINISH_SPEC.md` §6, `DESIGN_REFINEMENT.md` SF-NAV-1-D1).
