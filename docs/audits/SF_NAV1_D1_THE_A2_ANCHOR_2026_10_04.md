# SF-NAV-1-D1 — the A2 anchor, researched and ruled (Score Finish Step 7, October 4, 2026)

`docs/SCORE_FINISH_SPEC.md` §6 row 17 asked one question: SHUT OUT held on a played board for the first time in
Step 6, but never for a sitting's 8 turns, because Spain's war with Britain ends on turn 16 on all three
benchmark seeds and takes 3 of the System's ports with it. Can a road outlast that exit, and what should anchor
A2 (`NAVAL_SPEC.md` §5.1 / §7) be? The user delegated the call (*"research and decide every open call … measure
first, decide, write a gate record … FOR USER CONFIRMATION, then build"*) and asked first for the road the Step 6
arm never tried: **conquest** — hold Lisbon, Rome, Naples, Vienna and Hanover with Britain's corps off the
Continent.

This memo is that research. The ruling is the gate record `SCORE_FINISH_SPEC.md` §6.6 (authoritative).

**A word on what a seed is.** Every figure below is one played campaign on one seed. The game is seeded so that
openings, cadences and dice differ from campaign to campaign; three seeds are a sample of the roads the board
offers, not a proof that a road is always open or always shut. Where all three seeds agree, the memo says "on all
three seeds", never "always".

## Method

- **Two conquest drafts, played on the three benchmark seeds** (historical, austerlitz, marengo), 30 turns, a
  save every turn, through `POST /command` on the mock parser with the ambient world live underneath, read by the
  Step 6 probe `tools/sf_nav1_strangulation_probe.py`:
  - **The Danube road** (`tools/playtest_scripts/sf_nav1_conquest_danube.json`): the Grande Armée goes down the
    Danube first — Ulm, then Archduke Charles, then Vienna — and France refuses Austria's peace until loop 9
    (the driver's new `policy_at` dial lifts the refusal); Bernadotte leaves for Hanover on turn 1; Soult marches
    on Lisbon from turn 1; Lannes holds the Normandy beach; Massena keeps Milan and then takes Rome and Naples.
  - **The Step 6 road plus Hanover** (`tools/playtest_scripts/sf_nav1_conquest_road.json`): the Step 6 arm
    unchanged (it takes Lisbon, Rome and Naples and hunts Britain's bench), plus war on Hanover on turn 1 and
    Bernadotte sent to take it on turn 2. Austria's peace is accepted as in Step 6, so Vienna is not attempted.
  - Two earlier drafts (a Vienna-first variant and a Hanover-on-turn-1 variant) were played on the way and not
    kept; their peaks (12 and 10–14) are inside the ranges below.
- **The record board**: the hand-played turn-24 save the CONG arm reads
  (`docs/audits/playtest_digests/rs0928-hand-played/retest_t24_summonable.json` — 47 titled provinces, the
  Congress of Paris summonable), read with the same reading the Congress uses (`congress._shut_out_reading`).
- **The arithmetic**, from the authored `navies` block (26 continental ports): France 4, Spain 3, Ottoman 3,
  Holland 2, Denmark 2, Russia 2, Portugal 2, Sweden 2, and one each for Naples, Austria, Prussia, Hanover, the
  Kingdom of Italy and the Papal States. SHUT OUT wants 13 (50%), tier 2 wants 16 (60%), A2's 80% wants 21.
- **Archived digests** (each with the probe's JSON beside it): `docs/audits/playtest_digests/sfnav1d1-danube-*/`
  and `sfnav1d1-road-*/`.

## Found first — an instrument defect (SF7-X1, fixed)

Playing the drafts, the driver **signed armistices with courts on its own `--decline-from` list**: Hanover,
Portugal and Naples, on 8 of the 12 draft runs. The cause: when several envoys arrive in one turn, a stale answer is
refused and the refusal re-carries the STORED dialogue, whose court lives in `context.source_nation` (and, on an
incoming proposal, `target_nation`) — fields the driver's court reader never read. With no court named, the
decline list did not fire and the accepting dial signed. **Step 6's own committed arm did this:** NAV1-H accepted
Portugal's armistice on turn 20 under `--decline-from Portugal`. Fixed in `tools/playtest_driver.py::_court_of`
behind the lever `THE_DECLINE_LIST_READS_THE_STORED_SHAPE`; `context.source_nation` is stamped only by the AI's
envoy producers, and `target_nation` is read only on an incoming proposal, so the player's own confirms are never
touched. **Step 6's table reproduces with the fix** (NAV1 re-read on all three seeds: peaks 14 / 12 / 13, SHUT OUT on
historical turn 11 and marengo turns 13–15, Spain's exit on turn 16, the last British corps on turns 16 / 14 / 30):
Portugal's armistice changed no port, because Lisbon in French hands counts Portugal's ports either way (NV-10).
All the figures below are with the fix.

## Measured

| Road | Seed | Peak closure | SHUT OUT held | Closure after Spain's exit (t17–30) | Last British corps on the Continent |
|---|---|---|---|---|---|
| Danube first | historical | 10 of 26 | never | 6–8 | turn 15 |
| Danube first | austerlitz | 11 | never | 6–7 | turn 26 |
| Danube first | marengo | 10 | never | 7–9 | turn 30 |
| Step 6 + Hanover | historical | 11 | never | 6–8 | turn 18 |
| Step 6 + Hanover | austerlitz | 11 | never | 6–7 | turn 30 |
| Step 6 + Hanover | marengo | 13 | turns 13–15 (3) | 10 | turn 12 |
| (Step 6's own arm, re-read) | historical / austerlitz / marengo | 14 / 12 / 13 | t11 / never / t13–15 | 10–11 / 8–9 / 10–12 | turns 16 / 14 / 30 |
| The record board (hand-played, turn 24) | — | 9 of 26 | no | (Spain already at peace) | none |

1. **Vienna was not taken on any seed.** The marches set out (Davout and Ney, from loop 5) and broke on Archduke
   Charles's army on the Bohemian road — 54,000 at the boot; in an unkept earlier draft he stood at Vienna itself
   with 47,000 on turn 4 of historical — and Vienna keeps a 25,000-man garrison behind him. While the Grande Armée
   was in Austria, Spain's war ran down, the Peninsula went unhunted and a British corps stayed ashore (austerlitz
   until turn 26, marengo until turn 30).
2. **Hanover is Prussia's before it is France's.** On austerlitz and marengo Bernadotte could not start his march
   (Archduke Charles had engaged him), and Prussia's crisis on Hanover (the Defenceless Prize, SF-LB-2; it opens on
   turn 5–13 depending on the seed) ended with Prussia eliminating Hanover. A Hanover held by Prussia closes
   nothing: Prussia is at peace with Britain. On historical he marched, was turned aside by cannon fire at Milan on
   turn 3 (the driver answers an interrupt with its first option) and never reached Hanover; France refused
   Hanover's armistices, and the port stayed with a Hanover at peace with Britain.
3. **The record board tops out below the line.** On the best hand-played campaign on record, France holds Vienna
   and Hanover at turn 24 — the road's two hard capitals — and reads **9 of 26**: Spain, France's ally, holds
   Lisbon, and an ally at peace with Britain counts for nothing. Rome and Naples would bring the road to **11**.
   Lisbon would need a war on France's own ally.
4. **The arithmetic has no margin.** After Spain's exit, 13 wants every one of eight capitals at once (France,
   Holland, the Kingdom of Italy, Lisbon, Rome, Naples, Vienna, Hanover) — exactly the 50% line, so a single lost
   province ends the reading. Tier 2 (16) wants Spain's 3 back, or three more ports from courts at peace with
   Britain (Denmark 2, Sweden 2, Russia 2, the Ottoman Empire 3, Prussia 1), each a new war. A2's 80% (21) leaves
   at most five of 26 ports open in all Europe.

## What this means

**The conquest road exists in arithmetic and was not found in play.** It needs the whole Continent's capitals at
once, two of them (Vienna, Hanover) in the hands of a great power's army and a rival's design, and it has no
margin when it gets there. The historical System was not held that way either: Prussia and Russia joined it at
Tilsit (1807) and Austria at Schönbrunn (1809) by treaty, beaten, not occupied. Today the game has no such
treaty on the road that exists — the separate peace — because the System clause is settlement-tier and the 1805
boot folds every war into one table Britain never signs.

## The ruling (gate record: `SCORE_FINISH_SPEC.md` §6.6)

**(a) as recommended: the Tilsit clause on a separate peace**, plus the exit the System lacks (a member that goes
to war with France leaves it, as a named beat), and A2 re-anchored to what play can measure. The conquest road is
kept as a road and named in the gate record; the done-when is read on whichever road holds.
