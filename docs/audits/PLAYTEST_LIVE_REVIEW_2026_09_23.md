# Live Review — September 23, 2026: seven turns in the client, a Steam review, and how the game should end

> **What this is.** The user asked for four things in one session: *play the game for real using commands, look at the game, see if any remaining bugs or anything missing, do a Steam review, and determine how the end can work* (their suggestion: "holding X for X", with a "stabilization of the new status quo", plus defeat and what happens when nations are eliminated globally). This memo is the record. The design answer is **`docs/GAME_END_SPEC.md` §7**, a PROPOSAL awaiting the user's ruling; the defects are **`BUG_FIXES.md` §Live Review (LV-1 … LV-21)**; the design items are **`DESIGN_REFINEMENT.md` §Live Review (LV-D1 … LV-D5)**.
>
> **How it was played.** France, the 1805 campaign, on the real Godot client (window 2560×1340) against a fresh backend on port 8006, with the **live Anthropic parser** (`LLM_MODE=anthropic`), every order typed into the command box by hand. Turns 1–7 were played (the session crashed twice for reasons outside the game; the campaign was resumed through the menu's Continue, which is itself one of the checks). Every surface was read from native-resolution captures; four evidence frames are committed beside this memo as `LIVE_REVIEW_2026_09_23_*.png`. Beside the play, three probes ran headless: the 60-turn commanded-accept arm of the driver, a cheat probe that hands France 90 provinces while the enemy armies live, and a real global-elimination probe that runs the engine's own teardown on every rival court and plays twelve more turns.
>
> **Verification.** Every defect was traced to its producer by a read-only code pass after the play; the producer, the verdict and any prior row are on the BUG_FIXES rows. Two observations turned out to be working as designed (Bavaria's turn-1 walk-ins, the 318 men) and are filed as design or legibility items rather than bugs.

---

## §1 The campaign, as played

| Turn | What happened | What the game said |
|---|---|---|
| 1 | `Ney, attack Mack` → the Great Battle of Swabia (Ney + Davout + Lannes + the Guard vs Mack 52,000): won. `Soult, attack Mack` → Second Battle of Swabia: **Mack captured**. `Murat, scout Tyrol`. `Davout, move to Munich`. | Two dioramas, Berthier's report, Mack's quips ("A temporary derangement of the arithmetic. Vienna will understand."). The terminal opened EMPTY; the Dispatch screen said "No dispatch available yet". |
| 2 | Murat petitions (envy of Ney) → Promise Glory. Prussia, the Ottoman Empire, Portugal offer open borders → all accepted. `Ney, march to Vienna`. | The dispatch leads with Mack's capture; four marshals already "expect" 40–80g/turn; "Enemy nations hold 98 regions" (wrong: it counts neutrals and vassals). |
| 3 | Denmark (non-aggression) + Saxony (open borders) accepted. `Soult, march to Vienna`, `Davout, march to Vienna`. | The war-purpose line lists all 28 French provinces every turn. Austria's Charles is recapturing what Bavaria's AI took on turn 1. |
| 4 | Ney breaks off his march to hit Charles ("hears cannon fire") → Third Battle of Bohemia, Charles routed. Austria offers an ARMISTICE, Britain a paying PEACE (1,358g, the PR-D1b offer) → both refused. `Murat, pursue Archduke Charles`. | The battle report never printed (the envoy dialogs raised on the same tail swallowed it). |
| 5 | `Ney, attack Archduke John` and `Davout, attack Archduke John` at Vienna: both won; John retreats to Moravia. `Lannes, march to Vienna`. Bernadotte petitions → Rebuked. | Ney now "looks for 200g/turn", Davout 240g. Nine identical "beyond our sight" lines in the enemy phase. |
| 6 | Soult arrives at Vienna; Murat abandons the pursuit to join. `Soult, attack Vienna`, `Murat, attack Vienna`, `Ney, attack Vienna` → **Vienna falls**, secured. Davout petitions (a grievance the previous turn's report had called settled). Switzerland's client petition → granted. The Diplomacy wizard's settlement table refuses a WHITE peace: "the terms claim a victory the field has not delivered." | Threat 97/100. Berthier: "Their capital in our hands is worth ten field victories, Sire." |
| 7 | The marshals' collective petition (Fontainebleau) fires: Ney, Davout, Soult, Lannes, 600g/turn unmet → "I will find the means" (rentes, ~900g/turn). Le Moniteur special edition: *a capital stormed*. | Treasury 13,992g, income ~3,400g/turn. |

Zero server errors in either backend log. Zero parser misreads on 19 typed orders: every refusal was honest and named a remedy ("Bavaria is a nation, not a province — theirs are Franconia, Munich, Swabia"; "Cannot move into Bohemia — enemy forces present! Try: 'Bernadotte, attack Archduke John'"; "Bohemia is too far to scout (distance: 3)").

## §2 The Steam review

> *Written the way a reviewer with an afternoon on the build would write it. It grades the product, not the roadmap.*

**Ink & Iron — Early Access impressions. 7/10. Recommended once it has an ending.**

I have played a lot of Napoleonic strategy and none of it feels like this. You do not click a unit and a province; you type "Ney, attack Mack" and Marshal Ney — hot-headed, "the bravest of the brave", a man who resents watching anyone else take the field — goes and does it, and then tells you what he thinks of it. On turn one I typed that exact sentence and got a hundred-thousand-man battle rendered on a carved-wood tableau with tin soldiers toppling, odometers ticking off the dead, Berthier's verdict typed in a copperplate hand, and General Mack, freshly captured, sniffing that Vienna would understand. Six turns later I was in Vienna. That whole arc — Ulm to the Austrian capital — played out with about twenty typed sentences and the game narrating every step in a voice that never once broke character. When the fog closes in, it says so; when your cavalry general hears guns he abandons his orders and rides to them; when you win too much, your marshals gang up and petition you for estates. The diplomacy is not a menu: a Prussian envoy arrives stiff and wary, the Ottoman one "serene and unhurried", Portugal's minister "measuring the room". The economy ledger names every charge, with the reason, in prose. There is a newspaper.

The rough edges are real, and most of them are first-impression edges. The game opens on a blank terminal — no briefing, no "here is the situation, Sire", and the Dispatch screen says there is no dispatch yet. You will learn the game by typing `help`. Every turn stacks five or six modal windows on top of each other (a petition, an envoy, a mailbox of letters, a "strategic orders" recap, the enemy phase, a battle tableau) before you can give an order, and a few of them leak the engine: `(MOVE_TO)`, `PEACE → OPEN_BORDERS`, `ArchdukeJohn` with no space, "2.0 turns remaining". One petition's text runs off the edge of its box. The peace table told me, standing in Vienna with the Austrian commander in chains, that a white peace "claims a victory the field has not delivered" — which may be true of Britain and Russia, but it is not what the sentence says. And your marshals start asking for pay by turn two and hold a joint demonstration by turn seven of a *winning* campaign; that curve needs a longer fuse.

The bigger thing is that it does not end. Ask it how to win and Berthier tells you the campaign is "played open-ended — there is no laurel to be handed out; the war is the game." That is honest, and for a sandbox it is a defensible answer, but this is a game about Napoleon and the thing about Napoleon is that it ended. I also found the cheap way through: Britain offered me a paying peace on turn four, and if you take it the coalition dissolves, Europe's alarm falls to zero, and nothing whatsoever attacks you for the next fifty turns. The systems to make an ending out of this — coalitions that form against a hegemon, courts that hold grudges, a peace table that prices your conquests, satellites that drift — are all there and all working. What is missing is the game deciding, out loud, that you have won or lost.

Buy it if you want the best command-line general's-tent fantasy anyone has made, and you are happy to write your own ending for now. Wait a patch if you need the game to keep score.

*Strengths:* the command line and the marshals; the battle tableau; Berthier's narration; the depth of the diplomacy; the ledger. *Weaknesses:* the empty first turn; modal stacking; internal names leaking into prose; text overflow in three dialogs; the reward curve; no ending; the turn-four peace.

## §3 What the play found

Twenty-one rows, filed in `BUG_FIXES.md` §Live Review with the verified producer on each. In order of what a player hits first:

| Row | Sev | The observation (verified) |
|---|---|---|
| LV-1 | P2 | A fresh campaign (and every Continue/Load) opens on an EMPTY terminal: the boot help is printed and then wiped by the world-swap clear; there is no turn-1 dispatch anywhere (`build_morning_dispatch` runs only in `end_turn`). |
| LV-12 | P2 | The battle report did not print when an envoy/settlement dialog was raised on the attack's control-return tail (turn 4). The diorama played; Berthier's report was lost. |
| LV-14 | P2 | The settlement table's legitimacy blocker tells a player holding the enemy capital, with the enemy commander captive and the war score at +58, that a WHITE peace "claims a victory the field has not delivered". The real reason (per-court: Austria 32/50, Britain and Russia 24/50) is on the rows but not in the sentence; the panel's chip rows also overlap the "Allies and Standing" heading and clip Russia's row. |
| LV-2 | P3 | Raw marshal keys in prose: `ArchdukeJohn (Austria)` in the scout report, `[!] ArchdukeCharles is EXPOSED!` in the cannon-fire redirect, and `ArchdukeCharles` on the diorama nameplate and the map piece label. (An unlisted instance of the open NPC-12 census.) |
| LV-3 | P3 | `Treaty signed: PEACE → OPEN_BORDERS with Prussia`; `Responding to Ottoman's proposal: accept`; `You have accepted Ottoman's proposal` — raw state keys and the raw tag for the Ottoman Empire. |
| LV-4 | P3 | The STRATEGIC ORDERS dialog: `[ ] Ney (MOVE_TO)`, `2 turn(s) remaining`, `Destination: Vienna (2.0 turns remaining)`; and `[HINT] Hungary is undefended`. |
| LV-5 | P3 | The marshal-petition body is cut off ("He requests a command worthy" / "It is accurate, and it is longer") — the body is a bounded 120–170 px box and the second line falls below the fold; intermittent (Davout's wrapped). The disabled "Give him a command [2 AP]" arm's reason renders last, below the fold. |
| LV-6 | P3 | The incoming-envoy dialog prints acceptance-formula fragments written from France-as-proposer's viewpoint, so an INCOMING offer says "Key obstacle: their diplomat outmaneuvered us" when Talleyrand outclasses the envoy. |
| LV-7 | P3 | "Enemy nations hold 98 regions" counts every non-French controller (126 − 28), vassals and neutrals included. The courts at war hold 28. |
| LV-8 | P3 | The FA-D4 defensive war purpose renders as a 28-name list on the dispatch, the terminal block, the war panel and the envoy dialog, every turn. |
| LV-10 | P3 | "Region captured: Carniola (secured)" never says whom it was taken from; `captured_from` is rendered only in the movement branch. |
| LV-11 | P3 | The battle report and the diorama show the lead's post-battle strength before the advance attrition: Ney 22,181 shown, 21,863 applied (318 lost to the advance march, mentioned only inline). |
| LV-13 | P3 | With no visible enemy action, the enemy-phase dialog prints one "Our scouts report activity within the borders of X…" line per court — nine identical lines on turns 4 and 5. |
| LV-15 | P3 | The Diplomacy wizard's action chips overflow horizontally at 2560×1340 ("Propose Armistice (1 DP) — Uncertain — a counte…") with a horizontal scrollbar; the gate reasons are unreadable. |
| LV-17 | P3 | Davout's vindication ("his grievance is settled — he fights with renewed vigor") and a fresh Davout confrontation ("the quarrel may harden further") arrived one turn apart, in that order. |
| LV-21 | P3→design | The collective petition fires on turn 7 of a winning campaign: 600g/turn unmet after ~6 victories (expectations 40 → 80 → 120 → 200 → 240 per marshal). Design row LV-D1. |
| LV-9 | P4 | "1 unanswered envoy(s)", "1 turns left", "1 more port(s)" — a dozen `(s)` sites, no shared plural helper. |
| LV-16 | P4 | Campaign-log rows are prefixed with letters (`D`, `!`, `X`, `$`) where glyphs are meant. |
| LV-18 | P4 | "Personality (cautious) +16%" on a defence line bundles more than the personality term (+5% elsewhere). |
| LV-19 | P4 | `Captured: Austria -> France` (ASCII arrow) inside the materiel line. |
| LV-20 | P4 | The wizard's step 1 has a large blank gap above the list; "Sponsor Their Design — Aim their court at France" is confusing copy for a court already at war with France. |

Two observations that are NOT bugs, recorded as design questions: Bavaria's single 22,000-man corps walking into three empty Austrian provinces on turn 1 (the P4.5 undefended-capture rung has no per-turn cap; FA-D13 asked exactly this and was closed as a duplicate of a display fix — LV-D2), and the "strategic orders" recap modal that blocks every turn start for every standing order (LV-D3).

## §4 What the probes found about the end

**A. The commanded-accept arm (60 turns, `tools/playtest_driver.py`, script `commanded_full40`, `--diplomacy accept`).** France accepts Britain's paying peace on turn 4 at war score 0 (1,358g FROM Britain). The coalition dissolves ("the league is spent; Europe's alarm falls from 90 to 45"). Then nothing: alarm 45 → 0 by turn 40; 0 enemy attacks in 56 turns; provinces 28 throughout; treasury 2,454 → 152,941. The digest's last twenty turns read "Massena's fortifications strengthen / have crumbled completely". This is PB-D1 ("the long peace") measured end to end, and it is the strongest argument that the game needs to decide it is over.

**B. The fiat conquest (cheat probe: France is handed one court's provinces per turn while every enemy army stays in the field).** Provinces 32 → 91 by turn 6; alarm 68 → 97 and pinned there for 25 turns; six REVANCHE designs promoted against France in six turns; the Charges of Empire climb to ~9,900g/turn and Net turns negative from turn 17; the map bleeds back 91 → 66 by turn 30 (Russian corps walking into Provence and Savoy unopposed; Holland breaks free; Prussia eliminated by the AI); Britain offers a settlement every five turns. Raw occupation without a settlement is unsustainable on the current board, which is exactly the property a "stabilization" victory should key off.

**C. The real global elimination (`probe_global_elimination.py`, in-process; arm A every rival court torn down by `WorldState._eliminate_nation`, arm B vassals included; 12 turns played after).** No crash, no server error, `game_over` never set. The first dispatch headlines every knockout correctly ("Sire — Britain is knocked out of the war. No army remains beneath their colours."). Then the machinery runs with no subject: Europe's alarm climbs to 99 and reads "Brewing" (+8 hegemony passive, +3 for 50% of the map, +2 for the largest army, every turn) while Talleyrand says in the same breath "No coalition stands against us" and "France wages no war — a rare and precious quiet"; the enemy phase shows nothing; the treasury grows ~14,000g/turn; the satellites drift down (Holland 100 → 59 in twelve turns); `enemy_nations` is never pruned; "how do I win" still answers "there is no laurel to be handed out". Nothing in the game recognises that the war is over.

**D. What the code has today** (from the research pass; details in `GAME_END_SPEC.md` §1 and §7.0): elimination is "holds zero provinces"; great powers can be eliminated on the battlefield, never by the AI-vs-AI term generator (D2); `Region` has no ownership-history field, so "ceded by treaty" and "seized by force" are indistinguishable after the turn of the capture; Britain's and Austria's designs target French homeland (Flanders, Savoy) and can never read satisfied; a partitioned power's Revanche is permanent; the only "hold for N turns" idiom is `armistice_turns`.

## §5 Scores (directional, this build, from seven played turns plus the probes)

| Pillar | Sept 12 | Now | Why |
|---|---|---|---|
| Command & parsing | 7.5 | **7.5** | 19 of 19 typed orders parsed as meant; every refusal honest and remedied. |
| Combat legibility | 7.0 | **7.5** | The tableau and Berthier's report are the best surfaces in the game; LV-12 and LV-11 are the deductions. |
| Marshal drama | 7.5 | **7.0** | Petitions, vindication, the no-shows all fire and are legible; the curve is too steep (LV-21) and the vindication/confrontation contradiction (LV-17). |
| Narration | 7.0 | **7.0** | The dispatch, the Moniteur and the enemy-phase voice hold; the nine-line fog and the raw keys cost it. |
| Diplomacy | 6.5 | **6.5** | Envoys, the letter-book, client petitions, the wizard all work; the settlement blocker's sentence (LV-14) and the inverted hints (LV-6) are the cost. |
| Economy | 6.5 | **6.5** | The ledger names everything; the reward curve and the turn-4 paying peace remain. |
| UI/UX | 7.5 | **7.0** | Empty first turn, three overflow defects, five modal stacks per turn. |
| AI aliveness | 7.5 | **7.0** | Austria fought coherently and sued after Vienna; Bavaria's walk-ins and the nine-court silence read as noise. |
| **First contact** (new) | — | **5.5** | The single worst first impression is turn 1: no briefing, no dispatch, no hint. |
| **The ending** (new) | — | **3.0** | Measured: the game cannot end, the cheap peace is available on turn 4, and a world with no rivals still reads "Brewing". |
| Directional | ≈7.0 | **≈6.9** | Held, with two new pillars scored honestly. Both are owned: LV-1 and row GE. |

## §6 Routing

- **Row GE:** `GAME_END_SPEC.md` §7 proposes the victory arm the user asked for ("The Imperial Peace" — hold X titled provinces for X quiet turns), the global-elimination rulings, and the defeat arm as it should stand. **Awaiting the user's ruling on §7.8 Q1–Q5 before GE-1 starts.**
- **Defects:** `BUG_FIXES.md` §Live Review, LV-1 … LV-21, each with its producer and fix shape. Recommended landing: LV-1 and LV-12 ride the release build (first-contact and lost-report defects); the copy family LV-2/3/4/9/19 lands together as one display-name pass (NPC-12's census has a first slice); LV-5/15/14's panel overlap are `.gd` layout fixes for the next client session; LV-13 is a one-line producer change.
- **Design:** `DESIGN_REFINEMENT.md` §Live Review, LV-D1 (the reward curve, re-opening UX23-D1..D4 with the measured turn-7 collective petition), LV-D2 (Bavaria's walk-ins, re-opening FA-D13), LV-D3 (the strategic-orders recap modal), LV-D4 (the settlement legitimacy predicate for a victor, to be ruled with GE §7), LV-D5 (PB-D1 evidence).
- **Not changed:** no production code was touched in this session; the plan's order (GE → the release build → Updates 1–5) stands, with GE now opening on the §7 ruling.
