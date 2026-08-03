# The Quiet-France Played Campaign — ROADMAP position 1

**Held August 3, 2026.** 42 turns driven live over HTTP against a fresh backend on the
shipped 1805 board (`LLM_MODE=anthropic`, `SOVEREIGN_SEED=historical`), France played
actively through the Ulm concentration to turn 5, then **passive** — no French initiative,
only routine answers — to turn 42. Every order was typed as a player types it.

**This memo is the evidence pack.** The disposition of each defect is
`BUG_FIXES.md` §Quiet-France Played Campaign (authoritative); the two P1s were fixed in
session, eight rows are routed OPEN. Ten of the twelve findings were confirmed against the
code by a 12-agent find→refute fleet; **two of my own readings were corrected by the
refuters** and both corrections are recorded below rather than quietly dropped.

**Headline results**
1. **The enemy phase as theater re-scores 6.0 — below the 6.5 target.** Under
   `ROAD_TO_EA_REPLAN_2026_08_03.md` §5 that upholds the plan's own dissent and moves the
   composition slice to position 3, ahead of the shippable build.
2. **The D1 band is MET and measured for the first time in a played world** — 2
   AI-initiated wars in 42 turns against a band of 1–4 per 40.
3. **Two P1s found by playing, both invisible to 16,042 green tests** — and one of them
   re-opened, on a different code path, the exact defect class that shipped the day before.

---

shipped 1805 board. Every order typed as a player would type it.

## Confirmed defects (evidence in transcript.jsonl)

### PC-1 — the forced-retreat capture is mute in the phase that performs it  [P2]
*(Downgraded from P1 after checking the next turn's dispatch — see correction below.)*

Turn 3. `ArchdukeCharles` is broken at Swabia and force-retreats into **Rhineland**, a French
home province with no garrison, **capturing it**. The enemy-phase message stream prints only:

> `[!] ArchdukeCharles's broken army flees to Rhineland! (209 lost to march) (recovering for 2 turns)`

which reads as unambiguously **good news** — his army broke. Nothing in that phase says France
just lost a home province and 150g/turn.

Contrast the same phase's Munich: captured via the *attack* path, which prints
`Munich has been captured by Austria!` inline. The capture announcement is attached to the
attack branch, not to the transfer itself, so the **forced-retreat capture branch is mute**.

**Correction to my first reading:** the loss is NOT silent overall. The turn-4 morning dispatch
leads with it, at the top weight:
> `home_captured (weight 100): "Sire — Rhineland has fallen. Enemy colours fly over French
> homeland soil."` · Berthier: *"France herself is under the enemy's boot, Sire."*

So the real defect is a one-turn lag plus an inverted affect **in the moment it happens**: the
line the player reads at the time reads as a victory. Fix is one inline sentence on the
retreat-capture branch, not a new reporting path.

### PC-2 — one enemy marshal fights three separately-named battles in one phase  [P2]
Turn 3, `ArchdukeCharles` attacks Lannes at Swabia three times in a single enemy phase. Each
attack emits its own banner, its own casualty line, and its own **named** diorama:
"Fifth Battle of Swabia", "Sixth Battle of Swabia". By turn 3 the board has held six numbered
battles of Swabia. This is the PT-F6 square-thrash pathology in the *attack* branch — PT-F6
fixed forming/breaking square, not repeat assaults.

Same phase, the exhaustion banner narrates the repetition instead of hiding it:
`(2nd attack: -10%)`, `(3rd attack: -20%)`.

### PC-3 — a no-op hold line is emitted twice, every phase  [P2]
```
[Bavaria]
   Deroy holds position at Franconia, awaiting further orders. (Current stance: defensive)
   Deroy holds position at Franconia, awaiting further orders. (Current stance: defensive)
```
Verbatim duplicate. Observed turn 2 (Swabia) and turn 3 (Franconia) — systematic, not a one-off.

### PC-4 — the flanking line names a province the attacker's side does not hold  [P2]
Turn 1: `Mack flanks from Swabia while allies attack from Rhineland!` — Rhineland was **French**.
Turn 3: `ArchdukeCharles flanks from Swabia while allies attack from Munich!` — Charles is
attacking *into* Swabia; "flanks from Swabia" names the defender's own province as his origin.

### PC-5 — the diorama observation contradicts its own contingent list  [P2]
Turn 1 enemy phase, defender side lists **Lannes engaged, Davout engaged, Ney engaged**, Soult
`refused`; `committed_total: 64,943`. The observation printed over that tableau reads:

> "Where was Soult, Murat and Bernadotte? Lannes held the field alone — reinforcement never came."

Lannes had two full corps beside him. The observation also names Murat and Bernadotte, who are
not in the tableau at all.

### PC-6 — the bad-odds interrupt prices a number that will not fight  [P2]
Turn 1: `Ney, march on Swabia` → *"Mack blocks the path at Swabia. Odds unfavorable. Your orders?"*
Ney 24k vs Mack 52k. On `press on`, Davout and Lannes auto-reinforced and the committed figure was
**68k vs 52k** — Ney lost 948 and inflicted 12,151. The decision the player is asked to make is
priced on solo strength while the reinforcement system commits neighbours.

### PC-7 — square tutorial copy addressed to the player, inside the enemy's report  [P3]
Turn 2, under `[Austria]`:
> `ArchdukeCharles forms square at Munich! ... Any order — even one that fails — will break the
> discipline required to hold square.`
The second sentence is instruction for *the player's* squares, printed inside an enemy action.

### PC-8 — `en_route` to the province he is standing in  [P3]
Turn 2 dispatch: `Ney — location: Swabia, status: en_route, status_note: "Moving to Swabia."`

### PC-0 — THE HEADLINE FIND: the `/command` interrupt router re-opens PARSE-NEG  [P1]
`backend/main.py:1523-1562`. When any options-bearing interrupt is pending, the router
matches **raw substrings** against the typed command, **above the parser** and therefore
outside the `clause_guards` PARSE-NEG landed yesterday. Measured against the live router
(branch order is the elif chain, gated on the option being offered):

| typed | routes to |
|---|---|
| `hold your position, do not attack` | **attack_anyway** |
| `do not attack` | **attack_anyway** |
| `ney, stop attacking` | **attack_anyway** |
| `ney, without attacking, move to lorraine` | **attack_anyway** |
| `raise a fleet` *(a golden-corpus utterance)* | **attempt_breakout** |
| `set the fleet to raid commerce` | **attempt_breakout** |

Two independent bugs in one seam:
1. **No negation guard.** `"attack" in cmd_lower` fires on every negated form. PARSE-NEG's
   own headline sentence — "hold your position, do not attack" — parses as HOLD at the
   parser and **as ATTACK here**, because this router returns before the parser is reached.
   The `attack` branch (line 1538) is also checked *before* the `hold` branch (1557), so
   the negation loses even on a sentence containing "hold".
2. **No word boundaries.** `"flee"` ⊂ `"fleet"`, so **every naval order in the game**
   answers a pending last-stand interrupt as "attempt breakout" — a −10% escape roll with
   a marshal's liberty on it.

**Observed live, not theorised.** Turn 42, with Massena cornered, I typed
`set the fleet to raid commerce`. Backend log:
`[INTERRUPT ROUTE] Routing 'set the fleet to raid commerce' -> Massena last_stand response: attempt_breakout`
Result: *"The breakout fails — [!] MARSHAL CAPTURED — Massena is taken by Austria at
Limousin!"* The fleet posture was never changed (still `guard`), and the reply glued a
naval sentence to a land capture with an em dash, so it reads as though the breakout
caused it.

Why nothing caught it: the golden-corpus eval calls `CommandParser.parse` directly, so it
never traverses this router; and the corpus has no last-stand fixture. `raise a fleet` is
row-covered and still hijackable.

## Working well (evidence for the record)
- **Letter-book (IGR-F)** — Ottoman/Portugal/Denmark/Saxony/Hesse/Papal all batched, one row each,
  real per-court voices, answered without a modal. Reis Efendi's and Araujo's lines are excellent.
- **Campaign-log collapse (IGR-B)** — `"28 approaches rebuffed, chiefly from Bavaria and Prussia
  (open borders)"` on turn 3. Working exactly as specified.
- **Emergent designs (Stage E)** — turn 3, unprompted:
  `REVANCHE: Bavaria swears to retake Munich — Austria is not forgiven`.
- **Jealousy** — organic confrontation turn 3 (Murat envies Davout's recognition), AP-priced arms
  enabled (the July-25 P1 stays fixed).
- **Rente copy** — "paper is dearer than land, Sire, and it buys no title."
- **War Purpose gate** — Ney halts at Hesse's frontier rather than dragging France into a new war.
- **Parser** — 12 typed orders, 0 misreads so far (incl. "press on", "insist", "4", "accept").

---

## Measured statistics (42 turns, 41 dispatches, 41 enemy phases)

| measure | value |
|---|---|
| dispatch headline class `estate_eroding` | **21 of 41 turns (51%)**, longest run **7 consecutive** |
| single most-repeated headline sentence | Davout's household ×**12**; Ney's ×**9** (Berthier note byte-identical each time) |
| verbatim duplicate message lines inside one phase | **30** (23 of them `Deroy holds position at Swabia…`) |
| one marshal taking >2 actions in one phase | **37 occurrences**, max **5** (`ArchdukeJohn: move, attack, fortify, unfortify, attack`) |
| same marshal attacking 2–3× in one phase | **22 occurrences** |
| fortify→unfortify / wait×2 thrash | **41 occurrences** (Brunswick fortify→unfortify on t14, t16, t18) |
| live notification tray at t42 | **50 alerts, 50 distinct ids**, incl. 7× "Ney is cornered", 7× "Massena is cornered", one from turn 3 |
| turns carrying a marshal petition | **25 of 42** |
| parser misreads on typed orders | **0** (~20 orders; the P1 above is the *router*, not the parser) |

The duplicate hold is **producer-side**: the two records carry distinct `action_number`,
`marshal_priority` and `strategic_score`, so the AI genuinely spends two of its actions on
`wait` — it is not a rendering artefact.

## Open evidence items — what this campaign closed

| item | result |
|---|---|
| **living balance / D1 band** | ✅ **MET.** 2 AI-initiated wars in 42 turns (t15 Austria→Bavaria, t17 Spain→Britain, both "stated cause: conquest") against an acceptance band of 1–4 per 40. First time measured in a played world. |
| **naval pillar score** | **7.0.** Blockade is a real mounting cost (−175 → −306/turn); Admiralty block complete and honest; crossings render SHUT with the live ratio (1.9× → 3.7×); Britain **plundered Bordelais** in an actual amphibious consequence; CS closure falling 38%→23% as France loses ports is coherent. Deductions: a passive France has almost no naval counterplay (1 keel/turn at 400g while holding 39,000g), and the fleet never fought. |
| **played A2 sue-path** | ❌ **Structurally unreachable defensively.** CS closure only rises by taking ports, so a France that stops conquering watches it *fall* (38%→23%, never reaching the 40% first notch). Britain never sued. This is a finding, not a failure to test. |
| **enemy phase as theater (was 5.5)** | **6.0 — target 6.5 NOT met.** See below. |
| **narration (was 6.0, stale)** | prose **holds ~6.0** and is often excellent; the **dispatch headline specifically scores 4.5** over a long campaign. |
| NV-P1 wheel check · NV-4..11 visual sign-off · NV-V anchors A1–A5 | still open — need the client, not a driver. |

## Pillar re-score

| pillar | was | now | note |
|---|---|---|---|
| **enemy phase as theater** | 5.5 | **6.0** | PT-D1 muster odds and PT-D2 diorama taxonomy are real wins; PT-F6 fixed square only. The composition still reads as farce whenever two mechanisms stack, which was the original complaint verbatim. |
| narration | 6.0 | **6.0** (headline 4.5) | The writing is good. The *selection* is stuck. |
| AI aliveness / living balance | 6.5 | **8.0** | 2 AI wars, 6 congresses, 3 emergent REVANCHE designs, a vassal rebellion, an elimination, Britain fighting its own Peninsular war. |
| marshal drama | 7.5–8.5 | **7.5** | Content excellent; 25 petitions in 42 turns is fatigue. |
| naval | — | **7.0** | first score |
| parsing | 7.5 | **7.0** | parser itself clean; the router (PC-0) is a parse-class P1 |

### The dissent is upheld
`ROAD_TO_EA_REPLAN_2026_08_03.md` §5: *"if that re-measure comes back below 6.5 the
composition slice moves to position 3, ahead of the shippable build."*
**Measured 6.0 → below 6.5 → the composition slice is owed position 3.**
