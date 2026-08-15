# COMPREHENSIVE STATE-OF-THE-GAME PLAYTEST — August 15, 2026

> **The first playtest run on the standing harness** (`tools/playtest_driver.py`,
> doc of record `docs/PLAYTESTING.md`) — five driver campaigns plus a Mode-C
> client walk, ~120 played turns total across six arms, scored against the two
> most recent baselines (`CREATIVE_AUDIT_2026_08_08.md` §6 and
> `PLAYTEST_CA9_2026_08_09.md` §4b). Master at `1aa005a` + the one sanctioned
> harness fix (see §6). Report-only session: **defects are routed, not fixed**
> (`BUG_FIXES.md` §Comprehensive Playtest PC15 / `DESIGN_REFINEMENT.md`
> §Comprehensive Playtest).
>
> **Evidence lives in `tools/playtest_runs/<name>/digest.md`** (gitignored, on
> this machine): `variance_{historical,ulm,austerlitz,jena}` · `flagship-1805`
> (+ committed-quality saves `flagship-1805_t12/_t20` in its `saves/`; a copy
> of t12 is staged at `saves/flagship_visual_t12.json` for the user's own
> eyeball pass) · `naval-descent` · `diplomacy-latewar` · `tutorial-lesson` ·
> `vassal-probe`. Screenshots: `docs/audits/PLAYTEST_F_*_2026_08_15.jpg` (8).

## 1. Verdict

**The trend line turns up for the first time since July: directional ≈6.7**
(Aug 8 ≈6.3 · Aug 9 ≈6.4) — and unlike the last two audits, this one had the
LONGER evidence base, so the rise is not a short-campaign artifact. The PT and
HC rows visibly paid off: refusals name their remedies, the war ledger shows
its arithmetic, the calendar dates everything, the Gazette exists and is good,
and the muster/committed-strength math is finally shown where it is applied.

**Round 0 readiness: NOT YET — three P1s first, then GO.** All three were hit
by an unattended robot inside 25 turns, all three read as "the game stopped
listening to me," and all three are exactly the CA9 through-line one seam
further down (an honest computation whose DELIVERY lies):

1. **A destroyed marshal vanishes silently** — no event type exists for corps
   annihilation (`marshal_captured/recovered/released/commissioned` is the
   whole vocabulary). Ney and Murat died in the flagship and the player was
   never told; their names then misroute (P1-2/P1-3below).
2. **A pending order-bound interrupt swallows every typed command** —
   `[INTERRUPT ROUTE] Routing 'Murat, attack Buxhowden' -> Soult
   destination_blocked response: attack` · `Routing 'Ney, march to Vienna' ->
   Bernadotte cannon_fire response: investigate` · `Routing 'Davout, march to
   London' -> Davout cannon_fire response: investigate`. The router
   keyword-matches (with an any-text fallback) and never checks the addressed
   marshal. 3 hits across two runs.
3. **A stale settlement pair-substitute confirm wedges all later proposals** —
   `propose peace to Austria` looped EIGHT `proposal_confirm` popups with no
   send (diplomacy-latewar T22); every typed "confirm" was consumed by the
   stale active dialogue. BUG-CA-7's family, alive on the settlement channel.

With those three closed (all are known-seam fixes: the death event + a
fallen-marshal name guard; an addressed-marshal check in the interrupt route;
stale-dialogue retirement or stack-aware confirm), **Round 0 is GO** — the
build gaps position 10 owns are already fixed, the tutorial teaches, the menu
front door works, and everything a stranger meets in ten minutes behaved.

## 2. Pillar scores

| Pillar | Aug 8 | Aug 9 | **Aug 15** | Δ vs Aug 9 |
|---|---|---|---|---|
| Command & parsing | 6.0 | 6.5 | **6.5** | = |
| Marshal drama | 6.5 | 7.0 | **7.0** | = |
| Combat legibility | 5.5 | 6.0 | **6.5** | ▲ |
| Narration & briefing | 6.5 | 6.5 | **7.0** | ▲ |
| Economy | 6.0 | 6.0 | **6.5** | ▲ |
| Diplomacy & settlement | 6.5 | 6.0 | **6.0** | = |
| AI aliveness | 7.0 | 6.5 | **7.0** | ▲ |
| Vassals | 6.5 (Jul 25) | — | **6.5** | = |
| Naval | 7.0 (Aug 3) | — | **6.5** | ▼ |
| UI/UX | 6.5 (Jul 25) | — | **7.0** | ▲ |
| **Directional** | ≈6.3 | ≈6.4 | **≈6.7** | ▲ |

**Command & parsing 6.5** — The refusal floor is now excellent: `recruit`
names the reachable marshals, `endow Davout with an estate` answers "Which
province, Sire? Eligible estates: Tyrol, Bohemia" with a worked example, the
expedition names the exact yards Soult must stand at, `build` names its gate.
PARSE-NEG held (zero negation incidents in 68 anthropic commands, 9 honest
failures). What caps it: P1-2 (interrupt hijack ate three explicit orders),
P1-3's typed-confirm wedge, a dead marshal's name silently auto-selecting a
DIFFERENT marshal (`Ney, attack Archduke Charles` → "MUSTER — Soult…" via
LLM-validation fallback to bare `attack`), and `request terms from Austria`
answered by BRITAIN's chancery (coalition-leader substitution, unexplained).

**Marshal drama 7.0** — The engine ran hot in the flagship: 19 petitions
(13 jealousy, 4 rivalry, 2 Fontainebleau), crown churn narrated ("Murat,
crowned three turns ago, has been beaten — and the laurels have passed to
another"), grievances resolving IN battle prose ("Lannes fought like a man
with something to prove — and proved it. His grievance is settled."), the
marshal-voice trio on every battle (Kutuzov's line, Murat's reply, Berthier's
attribution), rentes granted/folded/eroding, autonomous glory-attacks that
chased Mack across Germany. Two caps: the petition FIREHOSE (19 modals in 24
turns — the CA9 §9 Q8 revisit now has a number) and the silent death of the
drama's own protagonists (P1-1).

**Combat legibility 6.5** — The muster preview's "24,000; 48,858 if all
march," the committed arithmetic shown in-line ("12,814 (lead) + 9,588
committed (Davout) = 22,402"), no-show attribution everywhere, and **the PT
row-2 attack-confirm gate ARMED in the wild** (flagship T2: cautious Davout at
unfavorable odds → "Commit the Attack … or Cancel"). The diorama carries
reserves, the refused-marshal shelf ("Soult — awaits explicit orders") and
odometers. Residue: `[Shield]`/`[Alert]`/`====` banner idioms still ride
enemy-phase `message` prose on the wire (the client rebuilds from structured
fields, so mostly invisible — but the strings are player-shaped and leak in
the gazette-adjacent surfaces).

**Narration & briefing 7.0** — Le Moniteur is a real newspaper: dated
masthead, VICTOIRE lead, battle rows with enemy commanders quoted in print
("You gained nothing. I call that a victory of arithmetic."). Dispatch
headlines stayed varied and honest across ~120 turns; the per-court fog tail
line renders ("Britain, Prussia, the Ottoman Empire and 3 other courts
stirred as well, but their formations remain beyond our sight"). Caps: the
grievance sentence repeats verbatim with only the number changing (3× per
campaign), the famine nag led 4–6 consecutive turns in three runs,
"Massena stand 21,858 men"/"Massena have been 4 turns over" (singular verb),
a "recovering: 0% (recovered)" non-event headline — and the biggest fact of
the flagship (two marshals annihilated) was never narrated at all.

**Economy 6.5** — EB-1 convergence CONFIRMED everywhere: all four variance
seeds cross net-zero mid-campaign and plateau (historical 20.4k · ulm 26.7k ·
austerlitz 18.6k · jena 22.7k; flagship net −692…+539 late), war grinds the
purse, nothing runs away. Prices are quoted at the point of decision (keels
400g, rente "face 240g/turn, fees and arrears" quoted at grant, invest 200g +
1 DP + cooldown, recruit 450g capital discount). Cap: the ally-soil depot gap
— four corps starved 14,610 men at MUNICH (Bavaria's own capital province,
France's ally) while the only counsel was "move a corps, or continue to pay"
(design row routed).

**Diplomacy & settlement 6.0** — The instruments are live and in character
(`guarantee Bavaria`: "their willingness falls by 8"; sponsor/buy-off refuse
at war with named reasons: "one does not bankroll the court one is
fighting"). The letter-book renders with per-court voice and an envoy-lapse
guard on End Turn. Offers keep arriving; Russia sues when losing. Caps: P1-3
(the confirm wedge), the request-terms court substitution, the Hesse
ghost-war chain (three modals of Conquest→objection→confirm producing NO
war and no receipt — fired in three separate runs), and "Requesting enemy
terms is not available for this pair" naming no reason.

**AI aliveness 7.0** — Europe punished overextension beautifully: Russia's
three marshals + Austria's two swarmed Murat then Ney with FIVE defensive
battles in single enemy phases — the deep push died on its own logistics,
which is the right lesson. Britain raids the coasts (Bordelais, Corsica,
Flanders fell in different runs), Moore grinds Normandy turn 1, **AI
commissions fired** (2 `marshal_commissioned` events — CA9 §9 Q10's answer is
"not blocked"), AI rentes continue, pair peaces + re-declarations happen.
Caps: Mack's routed corps toured three NEUTRAL capitals (Frankfurt → Berlin →
Dresden — the retreat scan treats neutral soil as free), and the exhausted
pair peace has no weight (austerlitz: Austria↔Bavaria peace AND Austria's
re-declaration on the SAME turn 17; jena peace T15 → re-declare T16).

**Vassals 6.5 (evidence thinner)** — Verbs work with honest disclosed terms
(invest +10 loyalty priced with cooldown; autonomy up says "a permanent
income cut"; autonomy down says "-15 loyalty … you collect more"). Drift
beats + recovery hints fire every run. But the t20 fixture world has
Switzerland — France's only vassal — already gone, with a stale
`vassal_rebellion_imminent` popup firing at load for a vassal that no longer
exists, and no rebellion narrative was observed anywhere. No deep-verb arc
(VS-3/4/5/6) was reachable this session.

**Naval 6.5** — Honest and voiced at every gate: keels quote price/readiness/
green-crew fold, `blockade Britain` names the watched courts, the Diversion
has a once-per-war latch, the expedition names its yards, and the Descent arc
produced a real Trafalgar ("caught coming home — the fleet is brought to
battle at bad readiness and loses 46 sail. A decisive defeat: the enemy's
line held the weather gage."). Caps: the typed `order the diversion` resolves
IRREVERSIBLY with no odds quote or confirm (the sibling expedition verb
quote-confirms; 46 sail died to one line), a march order to London is
accepted with no SHUT warning at order time, and the two open evidence items
(played A2 strangulation WIN, an actual London landing) remain open — this
session reached the Trafalgar branch, not the window.

**UI/UX 7.0** — Everything walked at 5120×1440 rendered correctly: the menu's
Continue row is calendar-labeled, the war-detail popup carries the new rows,
Moniteur/letter-book/region-panel/tooltip/enemy-phase/diorama all correct,
and the envoy-lapse guard on End Turn is exemplary protective UX. Warts: the
N hotkey didn't open the Moniteur under terminal focus (the top-bar button
works), the enemy-phase dialog ignored the wheel (thumb-drag scrolls — the
NV-P1 family, unconfirmed), and PARTIAL-intel regions show "Income: 0g /
Stability: 0%" as if they were facts while Supply correctly says Unknown.

## 3. The run matrix

| Arm | Runs | Result |
|---|---|---|
| A — variance | 4 seeds × 20 ambient turns, mock | **All completed, 0 unknown blockers.** Openings genuinely differ (historical: Charles storms Milan T1, Bernadotte captured T4; ulm: Mack comes WEST, beaten at Lorraine; austerlitz: Massena broken at Milan T2; jena: Swabia famine arc + the Frankfurt/Berlin pursuit) while Tier-1 history holds on every seed. Wars END (`third_party_peace` Britain↔Spain ~T16 on ALL FOUR; Austria↔Bavaria on three) and START (re-declarations on two). Economy converges everywhere. Calendar correct everywhere. |
| B — flagship | 24 turns, anthropic, scripted France | **Completed; 68 commands, 8 player battles, 19 petitions, both save snapshots kept.** The PT row-2 gate armed (T2); Ulm-ish arc played out; Tyrol+Bohemia taken; deep push annihilated by AI concentration; peace attempted (sent, 3 DP) with Austria's reply left standing (driver limit); the P1 cluster surfaced T19–23. |
| C — naval | 14 turns, anthropic | Descent arc to the Trafalgar branch; every naval gate honest; Hesse ghost chain ×2; London never reached (window never opened — diversion burned early at readiness 53, which the game allowed silently). |
| D — diplomacy | 10 turns from fixture_t20, anthropic, accept | First run BLOCKED by the driver's own answer table (fixed, §6); re-run completed. Instruments exercised; settlement chain exercised to the pair-substitute layer; the confirm wedge found; no ultimatum or carve was reachable (none staged in 10 turns). |
| E — tutorial | 12 turns, mock, `--scenario tutorial` | Completed, world isolated ("Your campaign autosave is untouched"). Beats I–III, V–IX teach; **beat IV broke its anchor** (`Senarmont, bombard Jellacic` → "Target out of range" — Jellacic wasn't adjacent; the S5 anchor-drift class again); the dotation-expectation nag fires INSIDE the school (TUT-F5 gated jealousy, not expectations); the school's own beats park two corps in 6-turn famine. |
| F — visual | Mode C, full pair on SOVEREIGN_PORT=8006 | **All owed surfaces PASS** (see §4). No 8005 session existed; pair shut down after. |

## 4. The owed visual sign-offs — what I saw (the user's own eyes still rule)

Per the standing convention these are REPORTS, not sign-offs — the staged save
`saves/flagship_visual_t12.json` reproduces every surface below via the
menu's Load.

| Surface | Screenshot | Seen |
|---|---|---|
| HC-0 calendar labels | `PLAYTEST_F_T12_BOARD…` | **PASS** — top bar "Turn 12 — Early March 1806", menu Continue row dated, dialog headers dated |
| PT-J2 Campaign/Blood rows | `PLAYTEST_F_WARDETAIL_CAMPAIGN_BLOOD_BLOCKADE…` | **PASS** — Score Breakdown: Territory +5 · Battles +15 · Decisive +15 · Capital 0 · **Campaign +2 · Blood +15 · Blockade −5** · Ticking 0 |
| HC-1 Blockade war-score row | same | **PASS** (−5 rendered in the breakdown) |
| HC-G Gazette screen | `PLAYTEST_F_GAZETTE…` | **PASS** — via the top-bar Moniteur button; issue pager works; content excellent. ⚠ the N HOTKEY did nothing under terminal focus — check whether that is the hotkey-block rule or a gap |
| IGR-F letter-book | `PLAYTEST_F_LETTERBOOK…` | **PASS** — per-court voices, terms, per-row Accept/Decline, lapse warning; PLUS an End-Turn envoy-lapse guard ("3 unanswered envoy(s) will lapse…") |
| CA9 F5 Supply: Unknown (panel + tooltip) | `PLAYTEST_F_FOG_TOOLTIP_REGIONPANEL…`, `PLAYTEST_F_SUPPLY_UNKNOWN_PARTIAL…` | **PASS** — no-intel arm says "No intelligence — scout or advance"; PARTIAL arm shows "Supply: Unknown" on both surfaces. ⚠ wart: PARTIAL "Income: 0g / Stability: 0%" read as facts on the panel |
| CA9 F7 per-court fog line | `PLAYTEST_F_FOGLINE_PERCOURT…` | **PASS** — "Britain, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight." after the nation blocks |
| BD diorama raise | `PLAYTEST_F_DIORAMA_RAISE…` | **PASS** — auto-raised on control return after the enemy-phase + strategic dialogs; reserves, the Soult awaits-orders shelf, ROUTED locket, Berthier + enemy verdict lines, Replay/Close |
| Marshal voice trio (bonus) | `PLAYTEST_F_ENEMYPHASE_VOICES…` | **PASS** — Kutuzov speaks, Murat answers, Berthier attributes; committed-strength arithmetic in-line |

## 5. Defects found (routed; digest named per row in BUG_FIXES/DESIGN_REFINEMENT)

**P1** — PC15-1 silent marshal destruction (flagship) · PC15-2 the interrupt
route swallows addressed commands (flagship T19/T21, naval T8) · PC15-3 the
settlement confirm wedge (diplomacy-latewar T22) · PC15-4 dead-marshal name →
bare-verb fallback → silent substitution (flagship T23).

**P2** — PC15-5 the neutral-soil family: forced retreats route through
neutral capitals, autonomous pursuit follows, and the resulting
war-purpose→Conquest→objection→confirm chain produces NO war and no receipt,
repeatedly (jena T18/19, flagship T5, naval T6/T10) · PC15-6 `request terms`
silently redirects to the coalition leader (diplomacy-latewar T21) · PC15-7
the typed Grand Diversion resolves with no quote/confirm (naval T5) · PC15-8
CR-5 literal delegation executed an attack instead of ASK on live parse
("Soult, deal with the Austrians", flagship T4) · PC15-9 tutorial beat IV
anchor broken (tutorial T4) · PC15-10 the petition firehose measured (19 in
24 turns — the CA9 Q8 revisit's number).

**P3** — PC15-11 "not available for this pair" names no reason · PC15-12
supply-headline singular grammar ("Massena stand/have been") · PC15-13
'Alsace' did-you-mean offers Wales/Balearics/Ulster · PC15-14 "recovering:
0% (recovered)" headline · PC15-15 same-turn peace-and-redeclare churn
(austerlitz T17) + congress beat repeated verbatim two turns running ·
PC15-16 PARTIAL-intel Income/Stability render as 0 · PC15-17 stale
`vassal_rebellion_imminent` popup at t20 load for an already-lost vassal ·
PC15-18 N-hotkey/wheel checks from §4.

**Harness (tools, not game)** — the driver's enemy-phase "0 attacks" counter
reads a key that doesn't exist (`action_type` vs `ai_action.action`); script
turn keys are 1-based loop indices, not world turns (documented nowhere);
`settlement_pair_substitute_confirm` still unanswerable (left standing by
design this session). Routed as a harness follow-up row.

## 6. The one fix this session made (sanctioned exception)

The mission allowed minimal fixes for blockers of the playtest itself. Arm
D's charter (accept settlements) was structurally unreachable: the driver's
`DIALOGUE_TYPE_ANSWERS` lacked `settlement_confirm`, which ships without an
options list, so the run blocked on its own acceptance. One dict entry in
`tools/playtest_driver.py` + a pin
(`test_playtest_harness_2026_08_15.py::TestAnswerTableCoversSettlementConfirm`).
Game code untouched.

## 7. What this playtest discharges

- **PT row-2 acceptance clause — DISCHARGED.** The attack-confirm gate armed
  in the wild (flagship T2, cautious Davout, unfavorable muster, the modal's
  own words in the digest).
- **The naval pillar is SCORED (6.5)** on played evidence (Descent to the
  Trafalgar branch + every gate exercised). The two NAVAL_SPEC §14/§15 open
  items (played A2 WIN, an actual landing) remain open — this session proved
  the failure branch, not the success branch.
- **The owed visual surfaces are all WALKED with screenshots** (§4). The
  user's own sign-off pass can run off `saves/flagship_visual_t12.json`.
- **CA9 §9 Q10 (AI commissions) — answered**: they fire (2 events, flagship).
- **The D7 variance contract — re-confirmed on 4 seeds** with wars starting
  AND ending.

## 8. What still needs a human or another session

- The three P1s (§1), then Round 0.
- The tutorial beat-IV anchor (Round 0 leads with the School).
- The played A2 naval WIN and a landed Descent (needs a played campaign that
  husbands readiness before the Diversion).
- An ultimatum and a carve/formable observed end-to-end (none staged in Arm
  D's 10 turns; needs a longer diplomacy campaign or a staged fixture).
- The user's own eyes on §4 (the standing sign-off convention).
