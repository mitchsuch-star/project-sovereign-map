# The Score Mandate — Chunk 2 EXIT: "The table tells one truth" (September 26, 2026)

**Routing:** `docs/SCORE_MANDATE_PLAN.md` §2 Chunk 2 (exit) + §5 (measurement).
**What this memo is:** the played-arm re-score of the DIPLOMACY pillar after
SR-2a (one verdict per screen), SR-2b (the Talleyrand verbs), SR-2c (WO-32 +
PR-D1c + PR-D1d) and the quick-win reserve all landed. The exit's four moments
— **the settlement table as victor and as loser, a mediation answered, a court
courted to a treaty** — were each driven at the wire on the shipped tree (mock
parser, seed `historical`, `tools/playtest_driver.py` arms archived under
`docs/audits/playtest_digests/sr2-exit-*`, then the saves hand-driven through
`POST /command`, `/mailbox/activate` and `/respond_to_diplomatic_dialogue` —
the client's own routes). Nothing was built for this memo; the residues it
found are filed below, not fixed.

**Verdict, FOR USER CONFIRMATION:** diplomacy **6.25 → 6.75** (target 7.0 NOT
met; residue = four legibility rows, SR-2d). Directional ≈7.0 (98.25 / 14).

---

## 1. The four arms

| Arm | Script / dials | Archive | What happened |
|---|---|---|---|
| **victor** | the AAR road `sr1e_aar_road.json` (18 loops; saves at 8/9/10) | `sr2-exit-victor` | Ulm turn 1, Vienna stormed; Austria sues for a truce on turn 7 (At War → Armistice), Russia on turn 10, Britain on turn 15; Britain's league offers at 9/13/16 (declined by the script's dial). At turn 9 France holds 29 provinces. |
| **loser** | the passive ambient France, 40 turns, `--diplomacy decline --settlement decline` (saves at 20/30) | `sr2-exit-loser` | Britain asks 5,177 / 5,693 / 5,508 / 5,840 / 4,946 / 2,384 gold on turns 11–37; Paris falls to Austria; France is reduced to Rhineland; the Emperor a prisoner ten turns → **THE FALL OF THE EMPIRE, the eclipse** (battles 44: 8 won, 21 lost; provinces lost 27). A genuine loser's chair. |
| **courted** | `volte_court_austria.json` + `--diplomacy accept` (40 loops) | `sr2-exit-courted` | Austria: truce turn 7 → peace; courted every loop; **Austria herself proposes Open Borders (22) → Non-Aggression (25) → Defensive Alliance (28) → ALLIANCE (31)**. The `volte_face` beat did not print on this arm (see §3). |
| **mediation** | `sr2_exit_tilsit.json` — the commanded arm with `propose peace to Russia` at every loop until she signs; `--diplomacy first --settlement decline --decline-from Austria,Britain` (40 loops; re-driven to 24 with saves at 19/20/21 as `sr2-exit-mediation-saves`) | `sr2-exit-mediation` | Russia rejects once, then **signs a bilateral PEACE on turn 8** (her counter accepted). France, fighting on against Austria and Britain with no settlement, loses Paris and the Emperor; **THE FALL on turn 24**. The end save carries `Russia|mediation: 6` — the Arbiter's Offer was ISSUED on turn 21 (10-turn cooldown set at issue), riding the turn-21 "Britain settlement offer" the driver declined. |

## 2. The four moments at the wire

### 2.1 The victor's table (turn 10, from `sr2-exit-victor_t9.json`)

- `Talleyrand, request terms from Britain` at turn 9 is refused with the
  gate line SR-1c/SR-1d built: *"Britain leads a league that is not yet
  spent, Sire — it names no terms while it can still fight (exhaustion 79 of
  80; at most 1 turn, sooner if the war turns against it)."*
- Turn 10: Britain's own offer arrives — a **white peace**, terms summary
  *"Peace · Status quo: France retains Bohemia; Bavaria retains Tyrol."*
  (SR-1a's cession line on the letter), voice *"No indemnity is asked and none
  is offered; London proposes only that the guns fall silent."*
- **Review** (`accept_settlement_offer`) opens the table: *"Sire, the white
  peace for France vs Austria + Britain + Russia is ready: no terms exchanged,
  no map redrawn — only the war ends. Ratify and the field falls quiet."*
  `staged_leaders {attackers: France, defenders: Britain}`, `can_ratify: true`,
  header **"Will carry — these are the terms they offered."**; every covered
  court's row reads `band_display: "Their own terms"`, `consents: true —
  "consents — these are their own terms"` while its scored column shows what a
  STRANGER'S white peace would earn (Austria 15 of 50: war exhaustion +20,
  settlement legitimacy −10, national design −8, …). **One verdict per screen
  — the AAR-2/AAR-3 contradiction ("Will sign" beside "cannot be ratified";
  the proposer's own offer priced at −32) is gone.**

### 2.2 The loser's table (turn 31, from `sr2-exit-loser_t30.json`)

- `Talleyrand, request terms from Britain` is taken (*"I shall ask Britain's
  chancery to name its terms for France + Holland vs Britain + Austria + Russia"*);
  the answer arrives with the next dispatches, beside Prussia's open-borders
  letter (the mailbox holds both; the settlement offer WAITING behind the
  ACTIVE letter, activated on its own).
- The package a beaten France is handed: **Peace · 5,406 gold France →
  Britain · a client state, the Duchy of Normandy, erected out of France ·
  status quo: Britain retains Berry, Corsica, Gascony; Austria retains
  Franche-Comte, Limousin, Lorraine, Lyonnais, Normandy, Paris, Provence.**
  Voice: *"London asks 5406 gold and a return to peace; the price is set, and
  London is not in the habit of revising figures lightly."*
- **Review**: *"the settlement … lies ready on the terms Britain themselves
  put on the table. Their consent is given; the signature is ours to give or
  withhold."* `can_ratify: true`, "Will carry — these are the terms they
  offered.", Austria's row `consented / Their own terms / 100 of 50 / accept`
  (concession credit +120, base side pressure −20, …). **Ratified at the
  wire**: *"Settlement Ratified: France vs Austria + Britain + Russia (4 pairs
  resolved). Status quo: Berry, Corsica and Gascony stay British by the
  treaty. Status quo: Franche-Comte, Limousin, Lorraine, Lyonnais, Paris and
  Provence stay Austrian by the treaty."* — France at war with nobody, 18
  provinces, treasury 12,462 → 7,094; **Normandy's controller is the new
  `Normandy`** (`nation_formations: Normandy {sponsor: Britain, turn 31}`) —
  the carve won and the ratified retention list correctly excluded it.

### 2.3 A mediation answered (turn 22, from `sr2-exit-mediation-saves_t21.json`)

- The Tilsit arm signs a bilateral PEACE with Russia on turn 8 (her counter to the
  second `propose peace to Russia`), so from turn 8 a non-belligerent contain-class
  major exists — the ONLY one the 1805 boot can produce (Russia boots at war with
  France; Sweden is `secondary`). France fights on against Austria and Britain
  without a settlement; by turn 21 both belligerents stand at war exhaustion 200
  and 177 against the floor of 60.
- From `sr2-exit-mediation-saves_t21.json` (turn 21, France 19 provinces): `end
  turn` → turn 22 opens with one envoy waiting — on the rail and in the mailbox it
  reads **"Britain — Settlement Offer"** (SR-2-X5). Activated, the letter is the
  Arbiter's Offer: `mediator: Russia`, `mediator_interest: Arbiter of Europe`,
  voice *"Under the good offices of Russia — whose court pursues Arbiter of
  Europe — the following terms are laid before you. His Majesty's Government
  offers terms for France vs Britain. London asks 5264 gold and a return to
  peace; the price is set …"* — terms: Peace · 5,264 gold France → Britain · the
  Duchy of Normandy carved out of France · status quo (Britain retains Artois,
  Burgundy, Champagne, Franche-Comte, Savoy; Austria retains Berry, Limousin,
  Lyonnais, Maine, Normandy, Provence — the SR-2-X2 overlap again).
- **Answered** (`accept_settlement_offer`): *"the settlement of France vs Austria +
  Britain lies ready on the terms Britain themselves put on the table. Their
  consent is given; the signature is ours to give or withhold."* — the review
  stages ONE verdict ("Will carry — these are the terms they offered", both
  courts `consents — these are their own terms`, 99 of 50, `can_ratify: true`);
  the review's own payload carries `mediator: null` — the arbiter's provenance is
  dropped between the letter and the table (folded into SR-2-X5).
- The driver's own 40-loop run declined this letter on turn 21 without knowing
  whose offices it carried; only the mediator's cooldown on the end save
  (`Russia|mediation: 6` at turn 25) showed that the Arbiter's Offer had fired at
  all — which is SR-2-X5's whole point.

### 2.4 A court courted to a treaty (the `courted` arm)

Austria — beaten, at truce from turn 7 and at peace after — is courted every
loop; SR-2b's honest refusals frame the road at both ends (*"we do not court a
belligerent — Austria is at war with us"* on turns 5–7, and once allied *"an
ally is reassured, not courted — the Reassure mission is the maintenance of
our alliance"*). Austria proposes each step herself: Open Borders (22),
Non-Aggression (25), Defensive Alliance (28), **Alliance (31)**. A court
courted to a treaty, on the shipped tree, with every step signed through the
ordinary letter.

## 3. What the arms did NOT show, said plainly

- **The `volte_face` beat did not print on the courted arm** — the alliance
  came by four ordinary proposals over nine turns rather than the beaten
  court's own volte-face at turn 21 (IQ-6's T2 arm). IQ-6's own T2 file drives that arm with SR-1d's lever DOWN (`THE_LEAGUE_TREATS_WHEN_SPENT=0`: the league's turn-4 offer, peace at 4, the courtship from 5, the volte-face at 21) and records that on the shipped tree Austria's ordinary ladder alliance lands about turn 29 — the exit's turn 31 is that shape. Since SR-1d the league treats only when spent (turn 9+ on this seed), so the beaten-then-courted window opens later; whether the volte-face is still reachable from the boot on the shipped tree is a standing question for the Chunk 7 aliveness re-score, not a defect of this chunk.
- **The mediated offer is indistinguishable from Britain's own on the rail
  and in the mailbox** (`Britain settlement offer`; the arbiter's provenance
  lives only inside the letter's voice). It fired — the cooldown proves it —
  but a player reading the rail would not know Russia had stepped in.
  Filed SR-2-X5.
- **The mediation needed a played Tilsit first**: on the 1805 boot the only
  contain-class major is Russia, who boots at war with France, so the
  Arbiter's Offer is reachable only after a Russia peace with no truce
  anywhere (`_find_mediator`). The commanded script signed one on turn 8.

## 4. Residues filed (not fixed here) — the SR-2d rows

| Row | What the wire showed | Where |
|---|---|---|
| **SR-2-X2** | The requested letter's status-quo summary names **Normandy** as retained by Austria while the same letter carves the Duchy of Normandy out of it; ratification resolves it right (the carve wins, the retained list drops Normandy), so only the LETTER lies. | the offer's `terms_summary` producer (`settlement_offers`) |
| **SR-2-X3** | A ratified settlement rides the rail as `proposal_result {proposal_type: "Diplomatic Action", outcome: "REJECT"}` with the ratification sentence as its message — IQ7-X4's mislabel one road over. | the PL-14 safety net (`main.py`) |
| **SR-2-X4** | The requested price moves between the letter and the review (5,406 → 5,398 gold) — re-priced at review time against a chest the end-turn ledger has since moved. | `settlement_staging` re-price at review |
| **SR-2-X5** | The Arbiter's Offer arrives as "Britain settlement offer" on the rail and in the mailbox, and the review it opens carries `mediator: null`; the mediator is named only inside the letter's voice. | `settlement_offer_arrival` rail row + mailbox summary + the review header |

## 5. The score

| Pillar | Before | After | Why |
|---|---|---|---|
| **Diplomacy** | 6.25 | **6.75** ⚑ FOR USER CONFIRMATION | The table now tells one truth on both chairs (AAR-2/3/7 gone at the wire, consent rows, ratify open when the courts consented); the Talleyrand verbs are honest at both ends of a courtship; WO-32's P1 is closed; the re-declared war no longer draws an offer at war-age 2; the Arbiter's Offer is reachable from play. Held below 7.0 by four legibility residues found by the exit itself (§4) and the invisible mediator. |
| **Directional** | ≈7.0 (97.75/14) | **≈7.0** (98.25/14 = 7.02) | |

**Next:** SR-2d (the four rows above, ≈0.4) is the plan's call — take it at
the head of Chunk 3, or bank it; then Chunk 3 FIRST CONTACT & COMMAND, or
SR-D3's AP/DP gate first — the user's call.
