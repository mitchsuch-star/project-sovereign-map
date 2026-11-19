# Round 3 ledger — findings and rulings (pitch v4, a third set of fresh panels) — THE LAST ROUND

Every one of the 24 panelists gave the same verdict: **BUILD IT AFTER THESE FIXES.** None said "do not build it".
The fixes below are written into `docs/INDEPENDENT_COMMAND_SPEC.md`. **They have not been tested by a further round.**

## Scores

| Panel | A Clarity | B Agency | C Character | D Solidity | E Enemy | F Typing | G Want |
|---|---|---|---|---|---|---|---|
| Players (Mendes, Whitman, Al-Sayed, Nyberg) | 6 | 7 | 6 | 5 | 6 | 4 | 7 |
| Designers (Roth, Ferreira, Iyer, Sorensen) | 6 | 7 | 7 | 4 | 6 | 4 | 7 |
| Historians (Ellis, Le Goff, Bergström, Alvarez) | 6 | 7 | 6 | 5 | 5 | 5 | 7 |
| Newcomers and UX (Choi, Hammond, Ortiz, Petrenko) | 6 | 7 | 7 | 5 | 6 | 5 | 7 |
| Engineers and QA (Ek, Diallo, Mori, O'Hara) — read the code | 7 | 8 | 6 | 4 | 6 | 7 | 7 |
| The enemy's side (Hoffmann, Chen, Katz, Kowalski) — read the code | 6 | 6 | 5 | 4 | 4 | 6 | 6 |

Median of all 42: **6**. THE BAR (median 8; Solidity and Want at 7 or more) IS NOT MET.

## Findings of the first rank, and the rulings

Raised: 17, counting each panel's separately (newcomers 3, designers 4, players 2, historians 2, the enemy's side 3,
engineers 3). They are 11 distinct faults, listed here.

| # | Raised by | Finding | Ruling |
|---|---|---|---|
| R3-1 | players, designers, historians (three panels) | "March to the guns" has no moment: battles are fought in the enemy's turn, if-thens are checked after it. | ACCEPT — it is the one if-then that works at the moment a battle is fought next to him, through the game's existing arrival roll for a supporting corps. He TRIES to join; the roll may fail. Joining is his one thing that turn. |
| R3-2 | newcomers, designers, players | A lower man's "Tonight" depends on a higher man's battle, which nobody can know in advance. | ACCEPT — the line says so beforehand: "attacks Mack — after Ney; stays put if Ney's fight changes things". A man waiting on an undecided fight stays put. |
| R3-3 | newcomers, players, designers | Personal lines contradict other rules (Ney and the feud rule; Masséna and survival; trust under 30). | ACCEPT — one precedence sentence: where he may go, survival and peace beat everything; a feud beats a personal line; a personal line beats his nature. Under 30 trust he ASKS. |
| R3-4 | engineers | Two of the six personal lines clash with abilities the game already ships (Lannes "marches to the sound of the guns", +15 on the arrival roll; Bernadotte "Eyes on a Crown", −15). | ACCEPT — a marshal's personal line IS his shipped ability, said in plain words. A new line is authored only where the ability does not bear on a man acting on his own, and never against it. |
| R3-5 | newcomers | A literal man's bare "attack": the read-back's odds are true when written and wrong when the line fires. | ACCEPT — plain "attack" means "attack if not outnumbered". "Attack whatever the odds" is its own choice, with its warning. |
| R3-6 | engineers, designers, players | The literal man is a free attack loop (three attack lines for one action, outside the count) and has a hand order plus a line the same turn. | ACCEPT — at most ONE of the three lines may be an attack; duplicates refused; "one thing a turn" binds every marshal with a standing order (today's order puts his if-thens to sleep). |
| R3-7 | designers | An if-then's result is undone by the task (he falls back, then his task marches him straight back). | ACCEPT — an if-then that takes him out of his area sends the order to "asks". |
| R3-8 | enemy, engineers, designers | An enemy literal marshal has two masters (his plan and his court's logic); "rewrites after he has stood two turns" contradicts every hold; nothing says where rewritten lines come from. | ACCEPT — a plan is a short written list of STEPS. A literal marshal under a plan is moved by his written orders and nothing else, except to save his corps and to fight a battle he is in. A used line or a met "until" moves to the next step. When the steps run out he is today's literal marshal again. |
| R3-9 | enemy, historians | "If Napoleon comes within reach" never fires: his corps is under a fifth of Mack's. | ACCEPT — a line that names a marshal fires on that marshal whatever his strength. |
| R3-10 | engineers | A jealous bold marshal who is also on his own: the existing jealous-attack code wipes his order, re-picks a target and reads true strength. | ACCEPT — a marshal on his own never makes the jealous solo attack. That attack stays exactly as it is today for the others. |
| R3-11 | historians | Berthier's "will", read from what France saw, contradicts "each line used once". | ACCEPT — Berthier's reading is CUT as a way of learning orders. |

## Findings of the second rank

Accepted: odds are the game's own battle forecast (the figure the attack card already shows), so walls and rivers count · authored odds spaced further apart than the risk step · a slight is forgotten only when the slighted man is himself set on his own, or next wins a battle · the card's suggestion is framed as the marshal's own proposal · if-thens show greyed on a turn he acts ("only on turns he waits") · the exact-order card opens on two or three authored presets · the turn-end line is a list you can tab through, text before arrows; every card action has a key · "turn" for time and "march" for distance, everywhere · a just-given order has its own [Withdraw] with a full refund, separate from Take back · "may become a great battle", never "will" · following a beaten enemy never captures and raises no question · "asks" rows show first, and an ask unanswered for three turns ends the order with no trust lost · a man acting without orders while the count is full shows "2 of 1"; nobody is forced off · all of a court's plans open with the same first step · courts fighting together draw one plan · a plan step names one province the court's corps favour (a new saved field joining the pull its logic already has) · tie-breaks for exact orders (the enemy that tripped the line; else the weakest seen; the nearer battle) · a line arms one turn after it is written · the purity test is "no non-inert key written, no global random draw", and the reload promise is made for seeded campaigns.

Cut on the panels' advice: the plunder switch (a marshal on his own always secures) · the Watch task (four tasks = the four standing orders the game has) · the posture "dial" (the code recomputes it every turn and already shows it) · Berthier's reading · bringing men "out of hand" into the new pass (their behaviour stays as today; they are shown and counted).

Accepted as a measured option, not a promise — "the hunt": one new term that draws the enemy toward a French corps it can see with no friend within one march. (The panel that read the code showed the pitch's claim "the enemy prefers your men on their own" was true only by accident.)

Rejected, with reasons: a false dispatch the enemy can plant (the project's standing principle: a surprise is never a lie) · a "fix"/pin task (the game has no rule by which fighting pins an army; that is a combat design of its own) · a personal line that breaks a "never" such as Murat taking an unnamed capital (conquest stays the player's act) · a favoured province per enemy corps (new behaviour in the enemy's hand) · counting exact orders with attack lines (the one-attack-line bound does the work).

## Dissent that stood through all three rounds

- **Historians, three panels running:** the order has no stated purpose beyond "so that"; nothing costs more for being far away; one axis of character cannot hold Davout or Soult.
- **Typing, every round (4 to 7, most often 5):** asking a marshal a question is a real job for the typed line; nearly everything else is a shortcut for a card.
- **The enemy's side, every round (4 to 6):** readable and fairer, not stronger; in 1805 it changes two or three marshals.
- **N of 1 at the start:** split in every panel between "scarcity is the point" and "the feature barely exists until the Staff is bought".
