# The Fifth Blind Author Set — DD-0 S4's done-when, read a second time, October 10, 2026

**Routing:** `PRE_DEPLOY_PLAN.md` §3.0 (DD-0's done-when: *the blind set reads ≥ 85 % of orders as meant keyless, on a FRESH set*; "S4 landing record, part 3"); rules `SYSTEMS_REFERENCE.md` §104 (the Reading, the exit predicate, the spine split and the slot reader) and §102 (how a blind set is read); the blind file `tools/playtest_scripts/unrehearsed_2026_10_10_fifth.json` (300 orders, never edited after the run); runner `tools/unrehearsed_census.py --trace`; records `docs/audits/unrehearsed/2026_10_10_fifth_{keyless,keyed}.json`; the fourth set's memo `docs/audits/UNREHEARSED_CENSUS_2026_10_10_FOURTH.md`.

## Why a fifth author
S4 part 3 fixed the fourth set's worklist (DD0-11 … DD0-17) — fifteen of its thirty-three shrugs by name — so the fourth file is **rehearsed by its own fixes** and reads 145 of 300 on this tree where it read 119. The done-when is read on a FRESH set only, so a fifth author wrote one.

## The method
The same method as the fourth: an agent given only what a player sees on the 1805 boot screen (the roster and where each corps stands, the two enemy commanders in sight and the two known to exist, our provinces, the provinces next to our corps, the courts, who we are at war with, the vassals, the treasury, the turn) and the ONE judge's family names for `intended.action`, told to use no tool, wrote **300 orders**, no questions, in deliberately varied registers, **30 meant to be refused**. The transcript shows **zero tool uses**. The JSON was saved as written. Each line ran on a FRESH 1805 boot board through the real `POST /command`, keyless (`LLM_MODE=mock`) and keyed (`anthropic`), read by the ONE judge (`tools/_score_probes.py`), every row carrying its parse trace.

## The reading
| arm | as meant | asked | board refusal | refused as meant | honest refusal | shrug | misread (judge) | executed when refusal meant (judge) |
|---|---|---|---|---|---|---|---|---|
| keyless | **125 (41.7 %)** | 35 | 57 | 24 | 22 | **29** | 2 | 6 |
| keyed (38 live parses) | **137 (45.7 %)** | 42 | 62 | 24 | 27 | 0 | 2 | 6 |

**Keyless 125 of 300 as meant (41.7 %), keyed 137 (45.7 %), against the done-when of ≥ 85 %. NOT met** — the second fresh author reads where the first did (119 / 39.7 % on the tree before part 3), and the rehearsed fourth set reads 145 on the same tree. **Read RIGHT by hand** (as meant + asked + the board's own refusal + refused as meant): **241 of 300 (80.3 %)** keyless.

## The eight the judge files as dangerous, read by hand against their traces
**Executed something other than what was meant (1):**
- `Ney, strike camp, abandon the works.` → *"Your words named no foe our maps know, Sire — Ney engaged Mack at Swabia, the nearest in sight"*. The chain read `strike` as the battle verb (CRT-11's destroy clause) before the unfortify idiom could read `abandon the works`; the bare attack's guessed-target road then fought the nearest foe behind a disclosure. **The one real execution of the set** → DD0-18.

**Staged, not yet done (1):** `Declare war on Holland.` (meant: refuse — Holland is our own vassal) → *"Choose your war purpose against Holland."* The war-purpose chooser opens against our own satellite; the declaration itself waits on the chooser. The Cabinet should refuse a war on a vassal before the chooser → DD0-18.

**Disclosed, not silent (1):** `Ney, retreat forward into Swabia.` (meant: refuse — a contradiction) → *"Ney retreats from Rhineland to Lorraine. Swabia cannot be reached, Sire — enemy forces under Mack hold it; Ney falls back to Lorraine instead."* The retreat road picks a safe province and SAYS so (the exit predicate's contract); the author would have had it refused. Recorded, not filed (the fourth set's `Davout, retreat to Swabia.` is the same class).

**Asked (1):** `Davout, attack Atlantis.` → *"No foe called Atlantis is in sight, Sire. The nearest in sight is Mack at Swabia — shall Davout …?"* — the proper-name ask (SF-V4), read right; the judge's `ASKED_RX` does not know "shall Davout".

**Honest refusals in shapes the judge does not know (4):** `Recruit 50,000 infantry in Paris.` / `Recruit minus ten thousand cavalry.` → *"No marshal of infantry/cavalry can reach Paris"*; `Repeal the Levee en Masse.` → *"There is no law called 'Levee en Masse'"*. Both shapes were grepped against the committed records in part 3 and NOT added to the judge: each moves rows in the third set and the October 3 records (a judge edit never rewrites a committed reading).

**The second misread** is the Cabinet's: `Open negotiations with Britain, Talleyrand, see what they want.` → the war-score advisory (*"the war with Britain is at a standstill"*) — the same desk the fourth set's `open talks with Russia` reached (DD0-18's Cabinet half).

**So by hand: executed-other-than-meant 1, staged-when-refusal-meant 1, disclosed 1, asked 1, honest refusals 4.**

## The worklist (keyless) — DD0-18
**The shrugs (29):** a new march register — `Lannes, get yourself to Swabia.`, `Marshal Ney, kindly take your corps down to Nassau.`, `Soult, bring the corps up to Rhineland alongside Davout.`, `Murat rides to Nivernais.`, `Shift Murat's horse to Lorraine so he can screen the Emperor.`, `Davout, I want you in Brabant covering the Dutch coast.`, `Bernadotte, shift your corps to Bohemia, and keep an eye out for Charles on the way.`, `Ney, on to Swabia and the enemy.`; the retreat register — `Soult, retire on Franche-Comte.`, `Pull Ney back behind the Rhine.`, `Lannes, break off, rejoin Soult at Lorraine.`; the fortify register — `Massena digs in at Milan.`; the desks — `Fort at Milan, Massena will need it.`, `An estate for Marshal Soult, with the Emperor's thanks.`, `Bernadotte, an estate, grudgingly.`, `Make Suchet a marshal.`, `Mission to the Porte — Talleyrand, court the Ottomans.`, `Lannes forms square against the Austrian horse.`, `That is all for today, Berthier. Close the turn.`, `Done. Advance the clock.`; the statement-then-order — `Mack must be destroyed. Davout, see to it.`, `Massena, John sits at Tyrol — go and get him.` (a dash, not a sentence, between the statement and the order); and the rest of the file's 29 (the record names each).

**The honest refusals (22), the parser's share:** `Lannes, break off, rejoin Soult at Lorraine.` → *"Region 'Soult' not found"* (the man read as the place); `lannes dont move` → the negation's refusal where a HOLD was meant; the rest are the board's own (Frankfurt, Nassau and Dresden are a neutral's — *"Cannot enter … (diplomatic state: PEACE)"* — which the judge reads as honest refusals and a player reads as the board).

## What the measurement says
Two fresh authors, two trees, the same figure: **~40 % as meant keyless, ~80 % read right by hand.** The gap between the two numbers is not the parser's — on this boot board the provinces beside our corps belong to neutrals (Hesse, Saxony, Switzerland, Bavaria), so a quarter of every author's marches are refused by the border law, and the marshals object to a quarter of the rest; both are the game reading RIGHT and neither is `as_meant`. The gap between 80 % and the parser's ceiling IS the parser's: each fresh author brings a register the vocabulary has not met (this one: `get yourself to`, `kindly take your corps down to`, `rides to`, `retire on`, `break off, rejoin`, `digs in at`, `Close the turn`, `Advance the clock`), and the slot reader fills the verb only when every other word is a march word. The ≥ 85 % done-when, read as `as_meant`, is structurally out of reach on the boot board; read as *read right by hand* it stands at 80 %. **Put to the user** (S4 part 4's head): keep the done-when as written and widen the vocabulary author by author, or re-base its instrument to "read right by hand ≥ 85 % and 0 executed-other-than-meant" — the figure the pillar is actually asking for.
