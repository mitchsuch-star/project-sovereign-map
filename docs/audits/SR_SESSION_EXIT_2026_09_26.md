# Score Mandate — Session Exit, September 26, 2026

**Row SR, `docs/SCORE_MANDATE_PLAN.md` §5** (one exit per session, over every
slice no earlier exit covered; one residue slice after it; **no §1 re-score** —
the one full re-score happens at the end of the mandate).

## 1. What this exit covers

Ten landed slices, none through an exit before:

| Slice | Commit | What it changed |
|---|---|---|
| SR-2d "the letter tells the truth" (Chunk 2's exit residue) | `dc297b50` | the letter subtracts what it carves; a ratified settlement names itself; the mediator is named on every surface |
| SR-3a (i) CRT-3 "a question never orders" + CX5-L5-F2 + CQ-30 | `d322c3e6` | the Cabinet reads the shared question verdict; hedges and leading runs are questions |
| SR-3a (ii) CRT-7 "the desk answers what the order would do" + AAR-17/19/23/29/31 | `29bd4d31` | seven desk kinds; the what-if fog-honest and refusing like the order |
| SR-3b CRT-2 "the name is never replaced" | `225cb42d` | a reward goes to its object; the named ground is kept |
| SR-3c L-1 "the prompt turns around" + IQ9-X1/X3 | `525ec653` | the parse prompt static first |
| The Chunk 3 reserve (boot help, CQ-37, AAR-25) | `11043d2a` | the help teaches the desk; "at once" is no condition |
| SR-2e (i) standing orders reliable | `6e288d57` | SUPPORT one action; AAR-8/9/10/11; CRT-4 one road reader |
| SR-2e (ii) CRT-5 "an answer is read closed" | `755f7b0a` | one closed grammar for every dialogue's typed answer |
| L-D "the boolean road" | `374738a3` | a keyless delegation takes the marshal's own arm |
| SR-4a "the field's price" (AAR-4/24/32) | `f176c95d` | the scout names the garrison; the assault's muster; the band folds the standing modifiers |

**Chunk 3 is CLOSED by this exit** (§5: a chunk closes when its last slice has
been through a session exit). Chunk 2 stays closed (SR-2e is its re-ruled last
row). Chunk 4 is open: SR-4c and its reserve remain.

## 2. Method

- **Two committed played arms**, each run on BOTH trees in-process through
  `tools/playtest_driver.py` (saves sandboxed, mock parser, no key):
  `tools/playtest_scripts/sr_exit_first_contact.json` (`--turns 2`, the
  ten-minute test — 28 typed lines) and `sr_exit_aar_typed.json` (`--turns 18
  --objection insist --diplomacy accept` — every line the Creative AAR's player
  typed on turns 1–18, 145 sent).
- **The before tree is `dc297b50`**, checked out with `git worktree add
  --detach` in the scratchpad and removed afterwards. It CONTAINS SR-2d, so
  SR-2d is read through its own pins and the Chunk 2 memo's reads, not through
  the arms' delta; every other slice is in the delta.
- Every typed line's reply paired across the two trees and classified
  (answered now / reworded / new shrug / now refused), a "shrug" being the
  desk's or the parser's I-cannot-answer family.
- **The golden corpus** (mock) and **the keyless replay** (IQ-9's cassettes) on
  both trees, and the after-corpus run against the before engine.
- **The wire reads** each touched pillar's evidence line names, by a scratch
  harness over `POST /command` on both trees: Portugal's letter answered ten
  ways (CRT-5); the seven delegation rows under mock (L-D); the price of a
  SUPPORT order (SR-2e); the desk's reach answer against the march (CRT-4).
- `BASELINE_SERIES` + M1–M7: byte-identical at every one of the ten commits
  (each commit's pre-commit hook ran the full suite).

## 3. What the exit read

### 3.1 First contact — the ten-minute test (28 lines, 2 turns)

**Shrugs 11 → 2; refusals 3 → 1; 11 replies changed** — nine for the better, one a different shrug (F3), and one, "is Vienna safe", answered WRONG (F1).
Answered now: "who am I fighting and why" and "who are we at war with" (the
war banner's own row — the Third Coalition, our purpose, their designs);
"is Paris safe" ("held by a garrison of 25,000 … it looks safe today");
"what does Kutuzov have with him" (fog-honest: "We have no word of Kutuzov's
whereabouts"); "who are my allies"; "what happened last turn" on turn 1 ("The
campaign has just opened…") and turn 2 (the overnight dispatch); "how is the
war effort". Reworded: "who is winning" reads one coalition row, not three pair
scores for one war. **"is Vienna safe" is answered — and answered wrong (F1).**
Still shrugging: "what are Ney's odds against Vienna" (F2) and "how long until
the armistice with Russia expires" typed without its mark (F3).

### 3.2 The command arm — the AAR's own lines (145 sent, 18 turns)

**Shrugs 7 → 2; refusals 46 → 46 (the 46 byte-identical); 10 replies
changed.** Line by line against the AAR's complaints:

- AAR-17 — the war questions answered (turn 1, twice).
- AAR-23 — Massena's fortify objection names its price: "(Insisting costs 2
  actions — he must first go defensive.)"
- AAR-4 — `Ney, scout Vienna` (turn 4) names the works: "No field army stands
  there. Garrison: 25,000 — it must be assaulted — a march halts before it; a
  capital's garrison, it regrows 2,000 a turn up to 25,000." (It had read "No
  enemy forces detected.")
- AAR-24 — both Vienna assaults (turns 5 and 6) open with the assault's one-line
  muster: "Ney storms the works at Vienna alone: 18,808 men, 22,386 in the
  assault's reckoning (+4% from the corps at his side), against a garrison of
  25,000. Soult and Bernadotte do not join an assault on the works; the
  garrison breaks below 5,000."
- AAR-32 — `Ney, attack Hungary` (turn 7) against Archduke Charles: the band
  read "even" and now reads "unfavorable". The battle that followed — Ney lost
  2,616, Charles 2,213, both armies in the field — is the exchange the new
  band describes.
- Turn 11: "Is Vienna safe?" answered (F1), "What does Kutuzov have with him?"
  answered ("reported at Podolia — substantial force"), "How long until the
  armistice with Russia expires?" answered honestly ("There is no armistice
  with Russia, Sire — France and Russia stand at Peace").
- Still shrugging: "what are Ney's odds against Vienna" — **the AAR player's
  own turn-5 line** (F2) — and "Berthier, remind me what the Russians demanded
  at the table" (F5).

### 3.3 The corpus and the keyless replay

- Corpus: **780/780 before, 793/793 after.** The thirteen rows the session
  added, run against the before engine: ten FAIL — the eight CRT-2 rows (the
  object of a reward, the kept ground) and the two CQ-37 rows ("at once") —
  and three pass on both, the rows that pin what must NOT change (a reward to
  the addressee himself, and two phrases that are not places —
  `recruit at once`, `repair the damage`).
- The keyless replay: **6/6 on both trees**, drift none — L-1's prompt change
  moved no replayed parse.

### 3.4 The wire reads

- **CRT-5 (Portugal's letter current).** Before, all ten phrasings SIGNED the
  treaty — "accept the offer later", "accept it next turn", "yes, later", "if
  we accept", "accept the offer, but not now", "we will accept tomorrow",
  "accept once Austria agrees", "accept prussia", "maybe accept" and "accept".
  After, only "accept" signs; eight are answered "A deferral, a condition or a
  second matter is not an answer, Sire — nothing was relayed", and "maybe
  accept" is a question (CRT-3) and signs nothing.
- **L-D (keyless delegation, mock).** Before, 7 of 7 asked. After: Ney,
  Murat, Lannes and Massena take the aggressive arm (a delegation-inferred
  PURSUE under the bad-odds gate), Davout and Bernadotte scout Swabia, Soult
  asks; "Ney, deal with the attack on Mack" still asks.
- **SR-2e (the price of a SUPPORT order).** Ney and Davout paid 2 actions
  before (4 → 2) and pay 1 after (4 → 3). Soult, literal, paid one on both
  trees; Lannes's order met an objection on both and cost one either way.
- **CRT-4 (the desk against the march).** "can Soult reach London" said YES,
  five turns, before — a walk across the Channel the march refuses — and says
  no after, naming the Royal Navy, as the march does. "can Davout reach
  Vienna" read four turns through Mack's Swabia before and six by the lawful
  road after; "can Murat reach Orleanais" reads "this very turn", the march
  arriving on the order, where it had read two turns.

### 3.5 Balance and the drama baseline

- `BASELINE_SERIES` + M1–M7 byte-identical at all ten commits; no slice moved
  the series.
- **Petitions (SR-4c's baseline):** 13 in 18 turns on the AAR arm — 11
  jealousy confrontations, 2 rivalry — one on turn 1; identical on both trees
  (no slice this session touched them). The AAR counted nine.

## 4. What the exit found

| # | Severity | Finding | Disposition |
|---|---|---|---|
| **F1** | P2 | **"is X safe?" reads France's side on soil France does not hold.** First contact, turn 1: "Vienna is Austria's, Sire; we have no intelligence on what holds it. Threats we can see: Archduke John of Austria is at Tyrol, two marches off (substantial force). It is safe for a turn or two, no longer." — Austria's own army named as the threat to Austria's own capital. The AAR arm, turn 11: "No enemy corps stands within two marches of it … it looks safe today" — the only corps that threaten Vienna are ours, and the answer cannot see them. `_answer_safe` (SR-3a (ii), AAR-17) counts "enemies at war with France" whoever holds the province. | **Residue R1** |
| **F2** | P2 | **The odds question has no desk kind, and the what-if drops the name it was asked about.** "what are Ney's odds against Vienna" shrugs on both arms (the AAR player's own turn-5 line); "should Ney attack Vienna" and "can Ney take Vienna" shrug (the what-if reads only a foreign commander, never a province); and "should Davout attack Mack" answers with whichever corps stands nearest, not Davout — CRT-2's class, inside the desk. | **Residue R2** |
| **F3** | P3 | **A question typed without its mark never reaches the desk.** "how long until the armistice with Russia expires" (no "?") is not a question to `is_question` — a "how" lead needs an auxiliary — and the order parser shrugs; with the mark it is answered. "what if Ney attacks Vienna" is read as a condition and refused. | **Residue R3** |
| **F4** | instrument | **The digest now hides an assault's result.** The driver records a reply's first line (`first_line(message, 400)`); SR-4a made the assault's muster the first line, so the digest shows "ASSAULT — Ney storms the works…" and loses the outcome that follows it. | **Residue R4** |
| F5 | P3 | "Berthier, remind me what the Russians demanded at the table" — no desk kind reads the table's history. | Filed — BUG_FIXES SRX-5 |
| F6 | P3 | The typed `propose common peace with Austria` still opens with LV-14's retired copy ("the terms claim a victory the field has not delivered") on its first line. The typed settlement route is debug-only by the user's rule. | Filed — BUG_FIXES SRX-6 |
| F7 | instrument | `--diplomacy accept` answers a non-ratifiable settlement confirm by dialing harsher until the 16-answer chain cap (turn 7, both trees). Capped and pre-existing. | Filed — BUG_FIXES SRX-7 |
| F8 | test hygiene | Found by the residue's family run: a driven tutorial pin fails after its class sibling (pre-existing at `dc297b50`). | Filed — BUG_FIXES SRX-8 |

## 5. The residue slice

**One slice, four fixes, each behind its own lever whose down arm reproduces
the finding** (the landing record is `SCORE_MANDATE_PLAN.md` §5; rules
`SYSTEMS_REFERENCE.md` §73.3; pins `tests/test_sr_exit_residue_2026_09_26.py`;
sweep `tools/_sweep_sr_exit_residue.json`). Every finding was reproduced at
`POST /command` on the shipped boot before a line was written.

- **R1 (F1) — "is X safe?" reads the holder's side**
  (`question_desk._safe_for_the_holder`, lever
  `THE_SAFE_ANSWER_READS_THE_HOLDER`). On soil that is not ours the threats
  are the corps at war with its HOLDER that we can see, and on enemy soil the
  holder's own corps are named as its cover. Measured on the boot: "Vienna is
  Austria's, Sire; we have no intelligence on what holds it. Corps at war with
  Austria within two marches: Deroy of Bavaria is at Franconia, two marches
  off (22,000 men); Bernadotte is at Franconia, two marches off (17,000 men).
  Austria's own we can see: Archduke John of Austria is at Tyrol, two marches
  off (substantial force). Its nearest enemy is two marches off." Our own
  soil reads byte for byte as before; an ally's soil ("is Munich safe")
  still names Austria's corps as its threats.
- **R2 (F2) — the what-if names its marshal, reads the odds, and weighs a
  province** (levers `THE_WHAT_IF_NAMES_ITS_MARSHAL`,
  `THE_DESK_READS_THE_ODDS`, `THE_WHAT_IF_WEIGHS_A_PROVINCE`).
  - "should Davout attack Mack" weighs Davout; a named corps beyond reach is
    never replaced — "Massena stands at Milan, beyond reach of Mack at Swabia
    this turn, Sire — the order would set him in pursuit, and there is no
    battle to weigh yet. Of ours, … stand within reach."; a foreign subject is
    "not ours to order"; a name the desk cannot place ends the classification
    rather than let the older entry weigh the nearest corps in his stead.
  - The odds phrasings ("what are Ney's odds / chances against…", "how good
    are…", "what odds does Ney have against…") are the what-if.
  - A province is weighed in the ORDER's own sequence (`_execute_attack`):
    out of reach it is refused ("Ney stands at Rhineland, beyond reach of
    Vienna this turn, Sire — the order would be refused, and nothing spent",
    and the order agrees: "cannot reach Vienna"); a corps engaged where it
    stands attacks nothing elsewhere; the crossing gate; a corps at war with us
    standing there is fought whoever owns the ground (the build's first cut
    refused "what if Ney attacks Swabia" as Bavarian soil, while the order
    fights Mack there — corrected before landing); ours holds nothing to
    attack; an ally's soil is refused; a court at peace or under a truce would
    first be put a declaration; then the works — **the assault's own one-line
    muster and the resolver's exchange**, then open ground.
  - **The exchange is ONE method.** `_resolve_garrison_combat`'s loss
    arithmetic became `CombatExecutor.garrison_exchange` (and the stand and
    collapse rules `garrison_report.garrison_fights` / `garrison_breaks`,
    read by the order and the desk alike); the desk's forecast
    (`garrison_report.assault_forecast`) takes the resolver's reads PURELY —
    every transient coordination field restored, the modifier read with
    `consume=False` — and quotes the exchange the order then applies, **pinned
    to the digit against the order itself**. At PARTIAL the garrison is a band
    and no figure that would give its count away is printed.
- **R3 (F3) — a quantity "how" and a conjecture "what if" are questions**
  (`clause_guards`, lever `A_QUANTITY_OR_CONJECTURE_ASKS`): "how long / how
  many / how much / how far / how soon / how often" and "what if" open no
  imperative; measured against the whole golden corpus, no row changes its
  verdict.
- **R4 (F4) — the digest keeps an assault's result** (`tools/
  playtest_driver.py`, lever `THE_DIGEST_KEEPS_THE_ASSAULT_RESULT`): the line
  after the assault's muster is recorded beside it — a `↳` line in the
  markdown and a `result` field in the jsonl — and, found by the re-read
  below, the lines after a lead-in (`THE_DIGEST_READS_PAST_A_LEAD_IN`).

**Filed with owners (GR9), heading the next session:** SRX-5 (the desk reads
the table's history — "remind me what the Russians demanded") → Chunk 6;
SRX-6 (the white-peace blocker still speaks CA8-17's "the terms claim a
victory the field has not delivered" beside F5's corrected sentence) →
Chunk 9; SRX-7 (the driver dials a non-ratifiable settlement harsher to the
16-answer cap) → the Chunk 4 reserve; and SRX-8, found by the residue's own
family run and pre-existing — a driven tutorial pin
(`TestTheCabinetLesson::test_the_card_advances_on_the_confirm_response`) that
fails after its class sibling and passes alone, as its file and in the full
suite, measured identically at `dc297b50`, `11043d2a` and `f176c95d` → the
Chunk 4 reserve. Rows in `BUG_FIXES.md` §Score Mandate Session Exit.

### The residue re-read on the arms

Both arms were run again on the residue's tree (`sr-exit-first-contact-residue`,
`sr-exit-aar-typed-residue`) and paired against the exit's "after" run:

- **First contact: shrugs 2 → 0, refusals 1 → 0, three replies changed** —
  "is Vienna safe" now names Austria's own Archduke John as its cover, not its
  threat; "what are Ney's odds against Vienna" gives the order's own answer
  ("Ney stands at Rhineland, beyond reach of Vienna this turn, Sire — the
  order would be refused, and nothing spent"); "how long until the armistice
  with Russia expires" is answered ("There is no armistice with Russia, Sire —
  France and Russia are at war").
- **The AAR's lines: shrugs 2 → 1 (SRX-5 remains), refusals 46 → 46, two
  replies changed.** Turn 5, the AAR player's own question, one line before the
  order: "Were you to give the order, Sire: ASSAULT — Ney storms the works at
  Vienna alone: 18,808 men, 22,494 in the assault's reckoning (+4% from the
  corps at his side), against a garrison of 25,000. … The works would hold:
  about 7,872 of the garrison fall and Ney loses about 5,225 — 17,128 remain."
  The order, two lines later: 7,835 fell, Ney lost 5,251, 17,165 remained —
  **within half a percent, and the whole gap is the board changing between the
  two lines**: the script moved Soult from Franconia into Bohemia in between,
  and the reckoning the order printed is 22,386, not 22,494 (Soult now stands
  beside Ney instead of adjacent to him). On an unchanged board the pin
  `test_the_forecast_is_the_exchange_the_resolver_applies` holds it to the
  digit. Turn 11, under the Austrian truce, "Is Vienna safe?" reads "No corps
  at war with Austria stands within two marches of it … it looks safe today" —
  true from Vienna's side, since the truce stands.
- The re-read found F4's blindness one reply over: a desk answer opens with a
  lead-in ("Were you to give the order, Sire:") and the digest recorded only
  that line. R4 now reads past a lead-in (`continuation_line`, lever
  `THE_DIGEST_READS_PAST_A_LEAD_IN`), which is how the forecast above was read.

**Gates:** pins `tests/test_sr_exit_residue_2026_09_26.py` (68); golden corpus +6 `sre-*` rows (799/799 mock; five fail with the levers down, the sixth is a control — the first commit's hook found four of the six leaning on CX-1's lever, whose own pin requires every golden row to pass under both of its arms: R3 now stands on its own lever outside CX-1's block, and the two F2 rows carry the mark, their plain forms pinned at `/command`); the residue re-read on both arms (above); sweep `tools/_sweep_sr_exit_residue.json` 34/34 killed, 0 INERT; the 188-file desk, question-guard, garrison, driver and corpus family 11,356 passed and 1 failed — the pre-existing order-dependent tutorial pin SRX-8, failing identically at `dc297b50` (the full suite passes it); `BASELINE_SERIES` + M1–M7 + the AI-V assurance byte-identical (81 passed) (the extraction is arithmetic-identical, pinned against the pre-extraction formula on a grid, and the desk and the digest are display only); zero `.gd`.
