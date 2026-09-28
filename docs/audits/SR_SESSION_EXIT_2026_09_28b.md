# Score Mandate — Session Exit, September 28, 2026 (the second that day)

**Row SR, `docs/SCORE_MANDATE_PLAN.md` §5.**
- One exit per session, covering every slice that no earlier exit covered.
- One residue slice after it.
- **No §1 re-score** — the one full re-score happens at the end of the
  mandate.

## 1. What this exit covers

Three landed commits, none of which had been through an exit. The previous
exit, `SR_SESSION_EXIT_2026_09_28.md`, landed with its residue as `716b09a7`.

| Slice | Commit | What it changed |
|---|---|---|
| SR-5a "The chest" | `00a9b4d7` | The ruled balance (Britain up, France trimmed); the ledger says why the bills moved; AAR-6 (an admin order asks the admin pool) and IQ1-5-1 (the forecast prices tomorrow's war tick); SR5A-1/-2; ES-4 and ES-7b struck; the series re-recorded once. |
| SR-5b "The second road at sea" | `01b7aaed` | The expedition names its levers (AAR-D7); the naval yard built (NV-D9); privateers struck (NV-D3); SR5B-1 — a refused order keeps the standing order; the A2 and SHUT OUT arms played. |
| SR-5c "The Descent's second throw" + the Chunk 5 reserve | `21699f55` | The Grand Diversion repeatable 4 turns after its last throw at readiness − 25; SR5B-2 (an override names the order it sets aside); FA-66 (a fleet action can lead the dispatch). |

## 2. Method

**Eight played arms.** Each ran on both trees, in process, through
`tools/playtest_driver.py`: saves sandboxed, mock parser, no key.
- **The four standing exit arms:** `sr_exit_first_contact.json` (`--turns 2`),
  `sr_exit_aar_typed.json` (`--turns 18 --objection insist --diplomacy accept`),
  `sr_exit_chunk4_field.json` (`--turns 10 --objection insist --diplomacy
  decline`), `sr_exit_chunk5_laws.json` (`--turns 10 --diplomacy accept`).
- **Chunk 5's sea evidence arm**, committed with this memo as
  `tools/playtest_scripts/sr_exit_chunk5_sea.json` (`--turns 12 --diplomacy
  decline`). Over twelve turns it prices and tries to raise a naval yard,
  sets a hold aside with a fought attack and keeps a march through a refused
  one, throws the Grand Diversion, is refused inside the wait and throws it
  again four turns later, commissions a 5,000-man corps and sends it across
  to Munster, and lays keels. (The driver answers the diversion's confirm
  itself, so the script's own "confirmed" line lands inside the wait.)
- **The IQ-1 economy arms, re-run** (Chunk 5's evidence line names a
  commanded France, a passive France and a beaten France):
  `commanded_full40.json` and `commanded_spender40.json` (both `--turns 40
  --diplomacy accept`) and the unscripted 40-turn ambient run (the passive
  France). The beaten France was not re-driven: its Net ratchet is SR-5a's
  question (c), measured and pinned in that slice (the rewritten IQ1-5
  pins), and the suite ran it at this exit.
- **The rest of Chunk 5's evidence line** was played inside SR-5b: the A2
  strangulation arc and the Continental System shut-out arc on six 40-turn
  arms (`docs/audits/SR5B_SHUT_OUT_ARM_2026_09_28.md`). The Descent is played
  here, on the sea arm.

**The two trees.** Before: `716b09a7`, extracted with `git archive` into the
scratchpad. After: the staged tree of the SR-5c + reserve commit, extracted
the same way while its pre-commit hook ran; it landed unchanged.

**The reads.** Every typed line's reply paired across the two trees; every
after-tree digest scanned for a roster key or a raw nation where a printed
name belongs; the economy arms' ledger rows compared at turns 5–40.

## 3. What the exit read

### 3.1 The sea arm (37 lines, 12 turns) — the session's new road

- **The naval yard:** "how much is a naval yard" is answered ("1,200 gold and
  4 turns"; before: "I cannot answer that from the dispatches"); the order is
  refused honestly for its price on turn 1 (France holds 800 gold after the
  SR-5a balance); before, "Unknown building type".
- **The Grand Diversion:** the quote reads the readiness odds ("40 times in
  100 at her readiness (65)" — the blockade had already rotted the boot's 70);
  the first throw WON on turn 2 (the strait open for two turns, the
  London–Normandy crossing among it). Inside the wait the refusal names it
  ("sailed the feint 1 turn ago — she may try it again in 3 turns"). The
  second throw went on turn 6 as ruled, at readiness 64 (39 in 100). It
  failed, and turn 7's morning dispatch **led** with "The fleet is shattered
  … France loses 26 sail; Spain 17 and Holland 7 beside her" (FA-66 in the
  wild).
- **The expedition:** Oudinot's 5,000, sent to Munster from Bordelais on
  turn 8, were intercepted at sea (1,478 men lost, 12 sail of the escort).
  Asked on turn 7, before he reached the yard, the order named the yards he
  could sail from.
- **SR5B-1 held:** "Soult, attack Lisbon" refused "cannot reach" and the
  march to Bordelais stood.
- **Found:** the headline named the battle "at the France–Britain action"
  (the naval layer has no sea zones — every name is "the X–Y action"): SRX-19.
  The strait line read "draws **the Britain fleet** off station" and the
  landing line (before tree) "slips past **the Britain patrols**": SRX-20.

### 3.2 First contact, the AAR arm, the Chunk 4 field arm, the laws arm

- **First contact: 27 of 28 identical.** The one change is a regression of
  SR-5b's: "what can I build" at Rhineland now ends "Not naval yard —
  Rhineland has no anchorage — a yard needs open water to moor at.." — a
  work the province can never take, named at every inland answer, with a
  doubled period: **SRX-18.** The same line appears in the AAR and Chunk 4
  arms at Paris.
- **AAR-6 visible in play:** on the AAR arm, `recruit for Marmont` with the
  military actions spent was refused on the before tree ("0 actions left")
  and recruits on the after tree.
- **SR5B-2 in play** (the AAR arm, turn 10): "Soult, drill" over his pursuit
  closes "Soult's pursuit of Kutuzov is set aside." (The digest's markdown
  cuts a long reply short; the clause is in its jsonl record.)
- **Found — a grey case made visible** (the AAR arm, turn 7): "Lannes, attack
  Tyrol" at peace with Austria answered "Choose your war purpose against
  Austria. Issue the attack again after the declaration is settled.
  **Lannes's march to Bohemia is set aside.**" The attack never happened, yet
  the march was destroyed — and destroyed for nothing if the declaration is
  then cancelled. SR5B-1 read only a refusal: **SRX-23.**
- **The laws arm:** the laws road reads true, and each refusal of the Staff
  states its price. The before tree bought it on turn 6. The after tree was
  refused at every scripted attempt — the last on turn 6, holding 6,817 of
  9,000 — its chest holding 8,191 on turn 7 and "ready to enact" by turn 10,
  after the script had stopped asking. That is SR-5a's leaner France paying
  for the two laws this script enacts first; SR-5a's own saving arm buys the
  Staff on turn 7.
- The remaining differences are drift: the rival courts' purses (SR-5a) move
  the AI from turn 1, and the after-tree AAR board makes its peaces
  differently.

### 3.3 Raw names in the backend's prose (both trees — older than this session)

- "**KingdomOfItaly** has been eliminated from the war." — the rail
  notification, the campaign-log line, the dispatch template and the
  diplomatic preview's refusal all printed the tag. The client's name net
  (`Utils.humanize_nation_keys_in_text`) rewrites a multi-token tag on the
  rail, in the log and in the dispatch view, so a player saw "Kingdom of
  Italy" there. The tag reached the payload, the driver's digest and the
  preview refusal, which the diplomacy wizard prints as given — **SRX-21.**
- "We rejected **PapalStates**'s open borders agreement proposal" — through
  the client's net, "Papal States's": the possessive is still wrong, and a
  single-word tag ("Ottoman's") is not rewritten in prose at all — **SRX-22.**
  The same formatter prints `source` raw on nine non-possessive lines ("…
  rejected our counter-offer", the ultimatum answers). The client's net
  already rewrites their multi-token tags, and they belong to NPC-12's
  standing display-name census, whose next slice is SR-6b (Chunk 6's copy
  pass).

### 3.4 The economy arms — Britain up, France trimmed, over forty turns

The chests and France's own ledger row come from the digests; both courts'
Net at the end is the ledger's own figure (`ledger._build_economy`), read off
each arm's final save with that tree's code.

| arm | tree | France chest t41 | Britain chest t41 | France Net t41 | Britain Net t41 | France provinces |
|---|---|---|---|---|---|---|
| commanded (control) | before | 57,434 | 11,817 | +2,900 | +1,316 | 26 |
| commanded (control) | after | 91,878 | 33,999 | +2,545 | **+2,413** | 30 |
| commanded (spender) | before | 26,445 | 9,368 | +1,972 | +1,345 | 27 |
| commanded (spender) | after | 43,778 | 33,999 | +2,028 | **+2,413** | 30 |
| passive (ambient) | before | −897 | 12,885 | +262 | — | 4 |
| passive (ambient) | after | 503 | 15,397 | +53 | — | 4 |

- **SR-5a nearly doubled Britain's income at peace** (+1,316 → +2,413 a turn)
  and its chest is three times what it was (11.8k → 34.0k), as intended.
- **At a long peace the two incomes converge.** The commanded France ratifies
  the common peace on turn 10 — every French and British war pair resolved —
  and no court is at war at the end of either arm. By then France earns
  about what Britain does (+2,545 on the control arm, +2,028 on the spender
  arm, against +2,413): it pays no blockade and no Admiralty, its Charges of
  Empire fall to the peace rate, it pays for a smaller army, and it rules 30
  provinces. The chest gap is SPENDING, not income: Britain's AI spends what
  it earns (the same 33,999 on both arms), and the scripted France keeps what
  it does not order. **Britain is richer at the boot (Net 2,851 against 1,032,
  SR-5a's record), where France pays for its war; across a long French peace
  they are level.** (The Nets were read at the boot and at turn 41 only, not
  through the war between.) SR-5a measured Britain's turn-40 chest, never the pair's Nets,
  so this is new. It is consistent with the EC-P3 gate's ruling that "a golden
  peace may grow rich", and it goes to the user as **SRX-D1**
  (`DESIGN_REFINEMENT.md`) with the recommendation to keep it.
- The passive France collapses as before (4 provinces at turn 40 on both
  trees — the passive harness, not a balance claim).
- **Corrected before commit:** the exit's first reading said "a France at
  peace out-banks Britain … while Britain stays at war and pays war charges".
  That compared hoards, not incomes, and the final saves show no court at war.

## 4. The residue (landed with this memo)

SRX-18 … SRX-23, all FIXED — `BUG_FIXES.md` §Score Mandate Session Exit
(September 28, second); rules `SYSTEMS_REFERENCE.md` §79.3; pins
`tests/test_sr_exit_residue_2026_09_28b.py`. SRX-D1 is the user's.

Found while running the residue's neighbourhood: SR-2e's support-objection
pin answered "insist" without pinning the defiance roll (6% on that board,
from the global `random` stream), so it passed or failed with the tests
before it. The fixture now pins the roll; defiance keeps its own pins.

## 5. Verdict

The session's three slices read true on the played road: the naval yard,
the expedition's levers, the second throw, the fleet-action headline and the
refused order's kept march all do what their records say. The exit found one
regression of the session's own (SRX-18), one wording defect in a new
surface (SRX-19), one gap in SR5B-1's reading of "not carried out" (SRX-23)
and three older copy leaks (SRX-20/21/22) — all fixed in the residue. The
economy's "Britain richer than France" is met at the boot, where France pays
for its war; across a long French peace the two incomes are level (§3.4), and
that question goes to the user as SRX-D1.
