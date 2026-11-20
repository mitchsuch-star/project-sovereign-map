# On His Own — the Emperor's desk, his marshals' judgement, and exact orders (row IC)

> **Status: DESIGN, version 5 — November 19, 2026 — and BOTH COMMITS the user approved are BUILT, the same day:
> THE DESK (§4, §5, §11's menu steer; pushed November 19 at his word, "Push both") and DIRECTIVES (one list for
> every order to several marshals, named armies, the war goal of §9 — slices IC-4 … IC-6).** What was built, how
> each differs from the design as written, and their blind readings are in §15's two landing records; the rules
> are `SYSTEMS_REFERENCE.md` §229 and §230, the ledger `BUG_FIXES.md` §IC and §IC directives. **Nothing else here
> is built** — not a marshal on his own, not exact orders, not "take the war goal", not the enemy's war plans.
>
> **The user's rulings in Plan Mode (November 19, 2026), which amend this document:** (1) any order to several
> marshals shows ONE list first — each man's order, its price, whether he may object — and is sent on one
> confirmation ("One list for all"); (2) named armies — form an army, name it, give it a directive by name
> ("Yes, named armies"); (3) the build order — "Desk, then directives": two commits, each with its own review
> and test run. Directives (the list, named armies, the war goal of §9) are therefore the NEXT build, ahead of
> Session 2 as §15 numbers it; `docs/NEXT_SESSION_PROMPT.md` carries the approved plan for them.
>
> Written at the user's word — *"design this and the four fun items make design incredible"* — and then, at his
> word — *"look at edge cases, how enemy will use it and make sure the interactions are extremly solide and
> verstile do a pitch of the concept to focus groups of agents and create an improvment loop these focus groups
> should be intelligent people"* — put three times to six panels of four experts each (72 people in all, fresh
> panels every round), and rewritten after each round.
>
> **The loop's bar was NOT met.** The middle score was 6 out of 10 in every round; "can a rule be broken?" never
> rose above 5. In the last round all 24 people gave the same verdict — *build it after these fixes* — and none
> said *do not build it*. Those fixes are written into this document. **They have not been put to a fourth
> panel.** The full record is in §19 and in `docs/audits/ic_focus_groups/`.
>
> A fact-check of this version's claims about the existing game (§0–§14) found six that were wrong or
> overstated. All six are corrected here.
>
> The routing lines (STATUS, CLAUDE.md) are NOT written yet — see §20.

**How to read this.** §0 is the design on one page. §2 is the order of a turn. §3 walks three mornings. §4–§11
are the parts. §12 is every ruling on an edge case. §13 is every number and how it gets settled. §14–§15 are for
the builder. §16 lists every decision, each one line to reverse. §17–§18 say what was cut, refused, or only
recommended. §19 is the record of the focus groups.

---

## §0 The design on one page

**The idea.** You are the Emperor. You cannot be everywhere. The corps near you, you command by hand, and they
fight better under your eye. Everywhere else you choose a man, tell him what you want, and then live with who he
is.

Five things, built to work as one:

1. **The desk says what you are doing.** Three lines always on screen: THE PEACE (how you win, how far along),
   THE WAR (each war's goal), TO DECIDE (up to three matters that need you, each a click away).
2. **One line as the turn ends.** Everything about to happen, said at once — including what each marshal on his
   own will do tonight, and which of your provinces an enemy you can see can reach.
3. **On his own.** A standing order that a bold or careful marshal carries out by his own judgement. He does one
   thing a turn, and the screen says what, before you end the turn.
4. **Exact orders.** A literal marshal takes no order "on his own". His standing order carries up to three
   if-thens, which he follows to the letter.
5. **Typing talks to them.** You ask, change, give today's order, or recall — in a sentence. They answer in
   their own voice.

**One new idea for the player.** There are two kinds of order: **today's order**, given by hand; and **a
standing order**, which is either *exact* (as today: it does the one thing it names and never chooses) or *on
his own* (new: he chooses).

**The enemy.** It keeps its hand exactly as today. What it gains is a **war plan** — drawn by the campaign's
seed from a few written ones — which writes its literal marshals' exact orders and names a province its corps
favour. You can learn it, and play against it.

### Words of the game used below (all of these exist today)

| Word | What it is |
|---|---|
| **Titled province** | A province that counts toward winning: your homeland, land ceded to you by treaty, a conquest held quietly for twelve turns, or a loyal client's land. |
| **The Peace** | How the reign is won: hold 45 titled provinces, summon the Congress of Paris, and have the great powers accept it. |
| **Actions** | What you spend to give orders by hand: 4 a turn, shared among all your corps. |
| **A standing order** | An order that carries itself out over several turns: take (march to) a place, pursue, hold, support. 2 actions to give; 1 for a literal man, for the Emperor's own corps, and for any support order. |
| **A law / the Staff** | Laws are bought in the laws book. The Staff is France's great one — the Grand Quartier Général, 9,000 gold and 300 a turn. |
| **Bold / careful / literal** | A marshal's nature. The code calls them aggressive, cautious and literal. |
| **The order of rank** | The marshals' seniority. The game keeps it; a higher man put under a lower one takes it ill. |
| **A day of battle** | A big undecided battle (50,000 men or more) fought over several rounds, in which you choose what your side does, or press "Leave it to him". |
| **The courts** | The other nations. |

---

## §1 Where this comes from

### 1.1 The user's words (November 19, 2026)

- "what if they set ai intent for marshals or macro intent how would this work"
- "you can have x autonomous marsahls and as you increas etech you get kmore up to x and typing talsk to them!"
- "perfect and yeah he does things on his own and this gives literal a purpose"
- "design this and the four fun items make design incredible"
- "look at edge cases, how enemy will use it and make sure the interactions are extremly solide and verstile do
  a pitch of the concept to focus groups of agents and create an improvment loop these focus groups should be
  intelligent people"

The second line is a ruling, and this design records it as one: **a cap on marshals who act on their own, raised
by the laws, with typing as the way to talk to them** (§6.4, §8).

### 1.2 The research behind it

`reports/Friendlier game and typed commands.md` found that the game's biggest remaining gap is direction, not
wording, and that typing earns its place for asking and for things a button does badly. Its four ways were: show
the aim and the next step; steer a first-timer into the lesson; show trouble before End Turn; give the marshals
more voice.

### 1.3 What the reads of the code found (the builder verifies each before relying on it)

**Corrections made along the way** — each was a claim of mine, or of the research, that turned out to be wrong:

- "Four bold marshals share one objection line" was **already fixed** on November 17. Seven French marshals
  already have their own battle lines (`backend/game_logic/marshal_voice.py`).
- **Attack odds are already on the attack card** (`order_confirm_card.gd`, `order_quotes.attack_quote`).
- **End Turn already stops for seven reasons**, sharing one confirmation window shown one reason at a time
  (`main.gd` `_execute_end_turn`).
- **"The enemy recalls its armies when its capital is threatened" does not exist.** The code reacts once a
  homeland province — above all the capital — is *lost* (`enemy_ai.py` homeland rungs). Nothing reacts to a
  threat.
- **The decision logic is not free of dice.** It rolls a daily mood and a score jitter from one random stream per
  nation per turn (`ai_rng`, `_get_mood_adjusted_threshold`). A design that reused it as it stands would let a
  question change the answer.
- **The enemy is not short of actions.** Its five great powers field 1 to 3 corps on 4 actions (plus up to 2
  free ones); lesser courts have 2 or 3 actions for one corps. Every corps acts every turn. France fields 8
  corps on 4 actions.
- **The enemy's "posture" cannot be set by a plan.** It is one value per coalition, recomputed every turn, and
  already shown on the war panel (`coalition.py`, `war_status.py`).
- **"Mission" and "a free hand" are taken** (diplomatic missions; "Licence — a free hand, no gold"). "A written
  order" already means a standing order you gave.

**What already exists and is built on here:**

| Already in the game | Where | What this design does with it |
|---|---|---|
| A marshal can act without orders for three turns after a crisis of trust, on the enemy's decision logic | `EnemyAI.decide_single_action`; `TurnManager._process_autonomous_marshals` | Left as it is; shown and counted. The game's name for it is "independent command". |
| …but the client never shows his report | no reader of `independent_command_report` in any `.gd` | Shown at last |
| A jealous, idle bold marshal strikes on his own "as the turn closes, before the enemy phase", after a warning | `jealousy.process_autonomous_attacks`; `turn_manager.py` about line 599 | The same seam carries the new pass. The strike itself is unchanged. |
| A marshal can petition for an independent command | `jealousy.check_shadow_petitions` | Granting it gives him a real one |
| Standing orders carry themselves out, free, after the enemy has moved — for France only | `strategic.process_strategic_orders` | Exact orders stay here |
| One if-then on a hold | `condition_grammar.py`; `StrategicOrder.contingency` | Two for a man on his own; three for a literal man |
| Friends next to a battle may join it on an arrival roll; Lannes has +15 ("marches to the sound of the guns"), Bernadotte −15 ("Eyes on a Crown") | `combat_executor.py` (reinforcements) | "March to the guns" is this roll. A marshal's shipped ability is his personal line. |
| "Leave it to him" in a day of battle | `battle_day.leave_it` | How a marshal on his own fights a day you do not take |
| Peace cancels pursuits and marches into the other side's land, and walks stranded corps home | `diplomacy._collect_peace_order_cancellations`; `withdrawal.py` | The same rule ends an order on his own |
| Standing orders are drawn on the map as dashed arrows | `scenes/map_order_layer.gd` | "Tonight" arrows use the same layer |
| A row of marshal name chips | `marshal_chip_row.gd` | The open lines by the command line |
| Win and lose are fully built, with progress figures | `congress.py`, `game_end.py`, `fall.py` | Shown on the desk |
| Per-nation live sight for the enemy | `WorldState.get_live_visible_enemies` | What an enemy literal marshal's if-thens read |
| Seeded choices inside authored bounds | `campaign_variance.py` | How a court's war plan is drawn |
| The pull a court's corps already feel toward its goals | `war_council.aim_pull_set` | Where a plan's favoured province goes |
| Laws are data, with a closed list of effects | `reforms.py`; `europe_1805.json` `reforms` | One new effect: the count |
| The order of rank, and "a higher man under a lower takes it ill" | `precedence.py` | The teeth of choosing a man |

---

## §2 The order of a turn

| Step | What happens |
|---|---|
| **1. Your turn** | You give today's orders. |
| **2. You end the turn** | **First of all, before anything else moves:** every marshal on his own does what the screen says under "Tonight" — an act, or *waits* — highest rank first. (Today's jealous strikes follow, unchanged.) |
| **3. The enemy's if-thens** | Each enemy literal marshal checks his if-thens once, on what you have just done. |
| **4. The enemy's turn** | Each enemy nation moves its corps, as today. If a battle is fought next to a marshal of yours who *waited* and has "march to the guns", he **tries to join it** — the game's existing arrival roll. |
| **5. Your if-thens** | Checked **once, on the board as the enemy left it**, for your marshals who waited and did nothing else, and for exact orders; carried out highest rank first. One that has become impossible does nothing and is not used up. No chains. Standing marches go on, as today. |
| **6. Morning** | What you lost and gained; one line from each of your marshals; then the rest. |

**One thing a turn.** Any marshal with a standing order does exactly one of these in a turn: today's order, if
you give him one; **or** the act shown under "Tonight"; **or**, if he *waited*, joining a battle next to him or
the first of his if-thens to come true. Never two. Defending when attacked is not an act. Digging in while he
waits is not an act.

**Each side's if-thens answer the other side's turn.** That is the one moment for every if-then, for every
marshal, of every nation. "March to the guns" is the single exception, because a battle cannot be joined after
it is over: it works at the moment the battle is fought.

---

## §3 What you will see — three mornings in 1805

*The men and places are the real 1805 opening: Masséna, a bold man, alone in Milan with 42,000; Ney and Davout
on the Rhine; Soult, a literal man, with you in Lorraine; Mack in Swabia with 52,000. The figures are for
illustration.*

**The first morning.** At the head of your desk:

> **THE PEACE** — 28 of 45 titled provinces
> **THE WAR** — Austria: no goal named · *name one*
> **TO DECIDE** — 1. Mack stands in Swabia with 52,000; Ney and Davout can reach him.
> 2. Masséna in Milan is five marches from you. He proposes to act on his own.
> 3. You can afford the Artillery Reserve.

You press the second. A card opens on one sentence:

> **Masséna proposes:** hold Milan and Venetia, and fight at our 8 to their 10 or better. *2 actions.*
> **[Give]** **[Change]**

You give it. The desk now reads *On their own: 1 of 1*.

You turn to Soult and type: *"Soult, hold Lorraine. If an enemy comes within reach, attack. If outnumbered, fall
back on Champagne."* The line reads it back before it costs anything:

> *Taken:* Soult · hold Lorraine · 1. if an enemy comes within reach, attack **if not outnumbered** (today: our
> 9 to their 10) · 2. if outnumbered, fall back on Champagne
> *Not taken:* nothing. *1 action. 1 if-then still free.*

You press End Turn. One line: *"Tonight: Masséna waits · Lannes has no orders."* You press again.

**The second morning.** The enemy's moves play on the map. The Archduke has marched into Venetia. Under "Your
marshals": *Masséna: "The Archduke is in Venetia with forty thousand." — He waited. Nothing of his came true.*

And at the turn's end the line now reads:

> *Tonight:* Masséna attacks the Archduke in Venetia — our 8.4 to their 10. May become a great battle.
> **[Order it yourself]**

You can let him, or give the order yourself and fight the day by hand. You let him. He fights it his own way.

**A later morning.** You have bought the Staff, so the desk reads *On their own: 1 of 2*. Ney, with no such
order, has watched Masséna's name in the bulletins; TO DECIDE says *"Ney may strike without orders tonight. Give
him something to do."* You want Bavaria kept, not risked, so you choose Davout — and the card says first: *"Ney
ranks above Davout, is within three marches, and has no order of his own. He will take this ill. Nobody would
mind if you chose Ney."*

That is the game this design is after: a clear aim, a few real choices each morning, and men who are themselves.

---

## §4 The desk: THE PEACE, THE WAR, TO DECIDE

| Line | What it says | Where the words come from | Click |
|---|---|---|---|
| **THE PEACE** | "N of 45 titled provinces". When a road of the Emperor's Designs is proclaimed, its progress. When a Fall clock runs, that warning takes the line. | The desk composes it from `congress.titled`, `fall.warning_state`, `imperial_designs.goal_clause`. | The Congress page. Hover lists each condition for summoning it, met or not, and what makes a province titled. |
| **THE WAR** | One part per war (two shown, "+N"): the enemy, the purpose, the war goal (§9), and whether it is yours. With none named: "no goal named · name one". **At peace:** the most pressing want of a court, which the game does not hide ("Prussia wants Hanover"). | `war_status.build_active_wars`; `intent.build_intent_payload` | Set War Purpose (it exists), or that court's page. |
| **TO DECIDE** | Up to three matters, each one plain sentence and one door. "+n more" behind them. | below | The right screen, the right corps, or a ready line on the command line. |

**TO DECIDE — one list, three doors.** One builder makes the list. The desk shows it, the turn-end line reads it,
and typing "what now?" answers from it.

The order of the list, written before any play:

1. **What bites when the turn ends.** A marshal who *asks* (always first). A last stand unanswered. A day of
   battle waiting. A letter that lapses tonight. A treasury about to go negative. A province an enemy you can see
   can reach next turn.
2. **What wastes the turn.** A corps on ground it could take. A corps with no orders, nearest the enemy first. A
   literal man with no if-then left. A bold man who may strike without orders tonight.
3. **What could grow the empire.** The Congress can be summoned. A law you can afford. A marshal you can hire. A
   place is free in the count and a corps stands three or more marches from you. A war with no goal named.

Rules: each row is one sentence of at most 90 characters and says why it matters; a row leaves when the matter is
done; a small × sets it aside for the turn; nothing in it reads a hidden enemy.

**Where it sits.** At the head of the command desk, in all three forms of the desk (one line in the narrow form).
It reflows with the window, needs no clearing of the map's names, and sits above where replies are read. At the
user's setup (scale 1.8 on a 5120-wide window) the desk is a full-height column 483 wide.

---

## §5 The line as the turn ends

Today End Turn can stop for seven reasons, one confirmation at a time. The design says them all at once, in
**one list above the End Turn button** — text first, an arrow second, one row a matter, and a key to step through:

> *Tonight:* Masséna attacks the Archduke in Venetia — our 8.4 to their 10. May become a great battle.
> **[Order it yourself]**
> *Tonight:* Davout waits. If Ney is attacked next to him, he tries to join.
> *Also:* Lannes has no orders · a letter from Vienna lapses tonight · Mack (about 50,000) can reach Bavaria.

- The list is always shown as you press. **A second press is asked only when it holds something you might want
  to stop**: an attack that may become a great battle, a step outside his area, a lapse, an idle corps (as your
  settings say today).
- A setting turns the second press off.
- The backend's one true stop stays: an open question that must be answered.

**What the enemy you can see can reach.** A small new reading: for each enemy at war with you *that you can
see*, which of your provinces lie within his next march. Those get a red edge in a new "tomorrow" view of the
map, with the text beside it. An enemy you cannot see is never drawn or counted. It is worked out once a turn
per visible enemy and thrown away when what you can see changes (golden rule 8).

**After the fact.** The report of the enemy's moves tags each loss: **"you were warned"** or **"he came out of
the fog"**.

---

## §6 On his own — the rules

### 6.1 The order

| Part | Choices |
|---|---|
| **Task**, with its area and its "so that" | **Take** a place — so that it is yours. The area is the place and the road to it, drawn on the card with the turns it will take. On the road he fights only what bars it, and only if his odds are met; otherwise he waits, and asks after two turns. · **Pursue** a named enemy army — so that it is destroyed. Never more than three marches from where he started (a ring on the map, fixed when the order is given). If it leaves the ring, or is unseen for three turns, he stops and asks. He heads for the last sighting, and the arrow says "last seen turn N". · **Hold** one or two provinces — so that the enemy does not have them. · **Support** a named friend, not the Emperor — so that he is covered. He stays within one march of him. (The corps beside you are yours to command by hand.) |
| **Risk** | **More · usual · less**: one man in ten either side of *his own* odds. Always shown as numbers, in the form "our 8 to their 10". |
| **If-thens** (up to two) | The same lists as exact orders (§7). Each is used once. They are checked only on a turn he waited. On a turn he acts they show greyed: "only on turns he waits". |

These four tasks are the four standing orders the game already has. Nothing else is added.

**His own odds are authored**, one figure per marshal in the scenario file, spaced further apart than the risk
step so that two men never read the same. Placeholders, to be authored with the user: Murat 5, Ney 6, Lannes 7,
Masséna 8 of ours to their 10; Davout 10, Bernadotte 14.

**How the odds are reckoned.** They are the game's own battle forecast — the figure the attack card already
shows you — so walls, rivers and ground count. He reckons from what France knows: exactly where the enemy is
fully seen; from the middle of the range where he is partly seen; and **he never attacks what France cannot
see**. No moods. No dice in the choice.

### 6.2 Who can be set on his own

- A **bold** or **careful** marshal whose trust in you is 30 or more.
- **Not a literal man** — he answers: *"Give me my orders to the letter, Sire."* (§7)
- Not the Emperor. Not an ally's or a client's commander. Not a marshal who is acting without orders.
- Artillery marshals: Hold or Support only. (Guns cannot march and fire in one turn.)

### 6.3 What it costs

- **2 actions** to give. A just-given order has its own **[Withdraw]** for a full refund until the turn ends.
- **Any change — task, area, risk, an if-then — 1 action, at once.**
- **Asking** is free.
- **Recalling** costs no actions. It costs trust 3 only if you chose it while he was in the middle of a task.
  The button says which.

### 6.4 How many — the count

The desk shows **"On their own: n of N"**. It counts marshals set on their own. A man acting without orders (the
three turns the game grants after a crisis of trust) is shown in it too: if that takes it over — "2 of 1" —
nobody is forced off, and no new man can be set until it is back under.

| Step | N | What it is in the game |
|---|---|---|
| The start | **1** | The Emperor writes to one distant man himself |
| The Staff in force | **2** | A third power for a law whose fifth action the project's own measures show going mostly unused |
| A new law, **the Emperor's Aides-de-Camp** (needs the Staff) | **3** | The officers who carried his intentions to far commands |

- **The count limits judgement, not movement.** Exact orders are not counted and never were: an exact order does
  the one thing it names and never chooses.
- "On their own" is a **new kind of law effect**. The laws spec calls that structural and asks for the user's
  ruling; the ruling is the second quote in §1.1.
- **If the Staff lapses** for want of gold, N falls at the turn's refill. The laws' forecast warns a turn ahead,
  so you may recall whom you prefer first; otherwise the lowest-ranked order ends. No trust is lost.
- The courts are not capped: they set no man on his own (§10).

### 6.5 "Tonight" is true

His pass runs first of all when the turn ends, so nothing moves between your last order and his act. The line
says exactly what he will do.

- If his act **shares a target or a road with a higher-ranked marshal's**, the line says so beforehand:
  *"Tonight: Lannes attacks Mack — after Ney; stays put if Ney's fight changes things."*
- **He never improvises.** If the higher man's act has made his own impossible, or worse than his odds, or left
  a fight undecided, **he stays put** — which is the same as waiting, so his if-thens are then checked.
- If "Tonight" is an attack that **may become a great battle**, the line says "may". Order it yourself to fight
  the day by hand. If you leave it, he fights it his own way — the game's existing "leave it to him" — never in
  silence.
- The one thing he does without it being shown: a shattered corps withdraws, as any corps does.

### 6.6 What comes first

1. **Where he may go** — wherever you could march that corps by hand. The game's own test.
2. **Survival** — a shattered corps withdraws by the game's retreat rule. A last stand stays yours to decide.
3. **Peace** — it ends his order (§6.9).
4. **Today's order.**
5. **His task**, at his risk, in his nature — or, on a turn he waits, his if-thens.
6. **Waiting.** On a Hold he digs in, up to the usual limit. He never drills on his own.

And for the man himself: **a feud beats his personal line; his personal line beats his nature.**

### 6.7 His way — shown before you give the order

His nature; **his personal line**; his feuds; his place in the order of rank.

| | A bold man | A careful man |
|---|---|---|
| Walls | Storms a garrison if his odds are met | Never storms; besieges (1–2 turns) |
| A beaten enemy leaves his area | Follows one province out, **once per order** — if set to more risk, or if his trust is under 50. You see it first under "Tonight". Out there he fights in the field only: he storms nothing, captures nothing, raises no question, and comes back by the safest road as his next turn's act. | Never |
| A friend he hates | Will not try to join his battle. The card warns. | The same |
| Objects to being given | Hold, with an enemy near | Tasks against bad odds or walls |

A careful man also counter-attacks an enemy he has just beaten off on his area — the decision logic already has
this.

**His personal line is the ability the game already ships for him**, said in plain words as it bears on a man
acting on his own: Lannes "marches to the sound of the guns" (+15 on the arrival roll); Bernadotte "Eyes on a
Crown" (−15); Davout "Iron Resolve". A new line is authored only where a marshal's ability does not bear on
this, and **never one that contradicts it**. Candidates, to be authored with the user, each a tested rule:
Murat — horse: follows a beaten enemy two provinces, not one, and never storms walls. Ney — on reaching an enemy
he attacks at once, at one step more risk than you set. Masséna — never gives up a walled place, short of being
shattered. Davout — attacked while holding, he does not fall back.

### 6.8 The life of the order

| State | What he does | Leaves it when |
|---|---|---|
| **Given** | Nothing yet. [Withdraw] refunds it in full. | The turn ends |
| **On the road** | Marches to his area | He arrives · the road is barred two turns (→ asks) |
| **At work** | His task, or waits | Task done · target lost · the area cannot feed him · nowhere he may go · an if-then takes him out of his area · his trust falls under 30 (→ asks) |
| **Asks** | Waits. One row in TO DECIDE, shown first. | You answer ("carry on" is free) · three turns unanswered (→ ended, no trust lost) |
| **Suspended** | Recovers (wounded, broken) | He is fit (→ back where he was). "For N turns" counts from then. |
| **Ended** | — | Recalled · killed or captured · N falls · peace in the land he stands in, or with the nation a Take or Pursue was against (the game's road-home rule walks him out) |

A Take that is done becomes a Hold of that place at once: the same place in the count, no new reward, no
objection.

### 6.9 The card, the morning, and what he earns

**The card** opens on **his own proposal** and one sentence — *"Masséna proposes: hold Milan and Venetia, and
fight at our 8 to their 10 or better. 2 actions."* — with [Give] and [Change]. Everything else is behind Change.
It names who would take the choice ill, and who could be chosen with nobody minding.

**The morning.** One block, "Your marshals": a line a man, in his own voice, with the plain cause beside it. The
full letter on a click. Only men who acted or ask are shown; the rest fold into "5 quiet". His move is replayed
on the map with a mark that shows he acted on his own.

**Trust.** +5 when he wins a battle under the order or takes a defended place; at most once per man in ten
turns. Changing his task does not earn a second +5.

**Glory.** Alone he earns it in full; beside the Emperor, half — as today. So marshals want this, and the
others grow jealous by rules that exist.

**The slight.** Choosing a man slights a bold marshal who outranks him only if that marshal is within three
marches and has no order of his own. It is forgotten when he is himself set on his own, or next wins a battle.

**The petition.** A marshal who has spent four turns beside the Emperor, is skilled, and has less glory than
most already petitions for an independent command, once a campaign. Granting it opens this card. With no place
free you may promise it for two turns.

### 6.10 What he never does

Take land the task did not name. Recruit, build or spend. Plunder — what he takes, he secures. Answer a letter
or a treaty. Make the jealous strike without orders: he has work.

---

## §7 Exact orders — the literal man (the same for every nation)

**Bold and careful men act on their own. A literal man gets it to the letter.**

- A literal marshal cannot be set on his own. Any standing order of his carries **up to three if-thens**,
  numbered. Other marshals keep today's rule: one if-then, on a hold.
- **If:** an enemy comes within reach · he is attacked · he is outnumbered · he is being surrounded · a named
  friend is attacked next to him · a named place falls · a named friend arrives · a named enemy comes within reach.
- **Then:** attack · fall back on X · march to X · try to join that friend's battle · dig in.
- **"Attack" means attack if not outnumbered.** "Attack whatever the odds" is its own choice, and carries its
  warning: *may fight far worse odds than shown.* **At most one of the three lines may be an attack**, and a line
  that repeats or contradicts an earlier one is refused.
- **Words, defined.** *Within reach*: next to him (two provinces for horse). *Outnumbered*: fewer men than the
  enemy within reach. *Being surrounded*: enemy corps, each at least a fifth of his strength, in two or more
  provinces next to him, and no friend next to him. *A friend arrives*: comes within one march of him.
- **What trips a line.** Only what his own nation can see. A force under a fifth of his own strength trips
  nothing (forces in one province are added together) — **but a line that names a marshal fires on that marshal
  whatever his strength.** A line arms one turn after it is written.
- **Which, when there is a choice.** He attacks the enemy that tripped the line; failing that, the weakest he
  can see. He falls back by the shortest way he may go. He joins the nearer battle.
- **Each line is used once.** His piece shows "2 of 3 left". A "march to X" that fires carries on until he
  arrives. When none fits he stands, and a TO DECIDE row offers **[Renew his orders]** for 1 action.
- **One thing a turn** binds him too: on a turn you give him today's order, his if-thens sleep.
- **The card** opens on two or three written presets ("hold, and fall back if outnumbered"), like the other card.
- 1 action to give. Not counted. He never objects and is never interrupted mid-order — both as today.
- A hold that carries two or more if-thens counts as real work: he does not grow restless on it.

**Why this gives him a purpose.** A marshal on his own *acts* on your turn, and you see it coming. A literal man
*answers* the enemy the same turn, exactly as written, and never otherwise. He is the one man who will never
surprise you — and the man for whom what you type is exactly what you get. Grouchy on the day of Waterloo heard
the guns and kept to his orders; the blame, as it should, falls on the man who wrote them.

---

## §8 Talking — the job of the typed line

The names of marshals on their own, or under exact orders, sit by the command line. Click one: the line begins
"Masséna, " with ready things to say.

| You want to | You say, for example | What you pay |
|---|---|---|
| **Ask** | "what will you do?" · "what do you see?" · "why did you fall back?" · "can you take Verona?" | Nothing. It is the same reading his act will use, and asking changes nothing in the game. |
| **Change** | "Masséna, more risk" · "take Venice" · "if outnumbered, fall back on Milan" | 1 action, at once |
| **Today's order** | Any ordinary order. The read-back offers "make it his new task" beside "send". | Its usual price. It is his one thing this turn. |
| **Recall** | "Masséna, stand down" | No actions (§6.3) |
| **Give** | "Davout, hold Bavaria and Swabia on your own, less risk" | 2 actions |
| **Exact orders** | "Soult, hold Lorraine. If an enemy comes within reach, attack. If outnumbered, fall back on Champagne." | 1 action |

**The read-back rule.** Before anything is spent, the line shows every part it took and names every part it did
not. A long sentence that is half understood is never half carried out in silence. (This is also the cure for
the four open defects in which a long typed order quietly drops a part.)

**With and without a language model.** The parts are fixed lists, so the built-in parser reads them with no key.
With a key, the model only maps freer wording onto the same parts. It writes no reply and decides nothing.

**What typing is honestly for.** Three rounds of panels marked typing between 4 and 7, most often 5, and said
the same thing each time: **asking a marshal a question is a real job for the typed line; writing a literal
man's three lines in one sentence is a natural one; nearly everything else is a quicker way to do what a card
already does.** Every act has a card. Diplomacy is never typed. That is all the evidence supports, and this
design does not claim more.

---

## §9 The war goal

- **One place a war aims at** ("Vienna"). Free to name. It shows on THE WAR line and as a gilt ring on the map.
- A task **"take the war goal"** follows it. Changing the goal costs 1 action for each man serving it.
- **Two marshals as one force** need no new rule: one leads, and the other is set to Support him. A higher man
  supporting a lower one takes it ill, as today, and the card says so before you give the order.

---

## §10 The other side of the hill — the enemy

**The enemy keeps its hand.** Its bold and careful marshals are moved by their court exactly as today, moods and
all. Courts are not short of actions, so they set no man on his own. Two rounds of panels showed that forcing
"roles" on enemy corps made the enemy slower or easier to solve, broke its existing reactions, and needed fog
machinery the game does not have (§17).

### 10.1 The war plan

Every court at war — **or the coalition, when courts fight together** — follows a war plan, drawn by the
campaign's seed from two or three written ones. The historical seed draws the historical plan.

- **A plan is a short list of steps** (two or three). Each step gives:
  - **exact orders for each of the court's literal marshals** — the same three if-thens and the same rules as
    yours (§7);
  - **one province the court's corps favour** — a new saved field that joins the pull its logic already feels.
    This is how a plan reaches the Archduke and Kutuzov without giving them orders.
- **A step ends on its written condition** — a line used, an "until" met, or a number of turns — and the next
  step applies. Steps only go forward.
- **All of a court's plans open with the same first step**, so the opening does not give the plan away.
- **When the steps run out**, its literal marshals are today's literal marshals again.
- **When a court's capital is lost**, the plan is torn up: every corps goes back to today's logic until it is
  retaken.
- Plans are written content, read and checked in the scenario file like the game's other seeded choices.

**A literal marshal under a plan is moved by his written orders and by nothing else** — except to save his
corps, as any corps does, and to fight a battle he is already in. His court's decision logic skips him. His acts
cost his court nothing.

Plans the historians' panels asked for, as a start: **the Third Coalition** — "the Danube junction" (Mack: hold
the Iller until the Russians arrive; Buxhowden: march to Moravia, and if Kutuzov is attacked next to him, try to
join) · "the long retreat" (if Napoleon comes within reach, fall back) · "Weyrother's disposition" (march and
attack). **Prussia** — "the Thuringian concentration" · "the Saale line" · "wait behind the Elbe". **Britain** —
"hold the lines, never risk the army" · "the descent on a coast".

### 10.2 What you can learn

Position and strength stay fogged. A report of a task names its place: that is what a spy is for.

| How | What it gives |
|---|---|
| **Free** | Every marshal's **nature**, on his piece. Reputations were public. |
| **The spy mission** (it exists: one diplomatic point, three turns) | Each literal marshal's current **task**, wherever he stands, and the province the court's corps **favour**. |
| **Captured orders** — when you rout any corps of that court | The **if-thens of the literal marshal nearest the routed corps**, in his court's own words. If the court has none, the favoured province. Good until the court's next step — two turns at most. |

- Knowledge ages by time only: "learned 4 turns ago". You are never told that orders changed.
- A literal man can be read as "will". A bold or careful enemy only as "may": his court's logic has moods.
- The enemy's "Tonight" is never shown.
- **A surprise is never a lie.** No court plants false orders.

### 10.3 What the enemy learns of you

Nothing new, with one exception: when one of your marshals on his own is routed, the court learns his task, and
if he was to take a place, that place joins what its corps favour for five turns.

The enemy's logic reads the board as it does today. This design adds no new all-seeing read. An enemy literal
marshal's if-thens read the live sight the code already keeps for each nation — never France's.

### 10.4 Playing against it

- Learn a literal man's lines, and do the thing they do not cover. That is Ulm — on the seed that draws it.
- Read the favoured province, and be elsewhere, or be there first.
- Read each man's nature for his odds.

### 10.5 The hunt — a measured option, not a promise

An earlier version said "the enemy prefers your men on their own". The panel that read the code showed that was
true only by accident: the enemy marks down — by up to a quarter, while his grip holds — any stack that holds
a fit Emperor, so a lone corps can look up to a third better to it. But it cannot tell a man on his own from any
other lone corps, and nothing makes it go looking.

The option: **one new term in the enemy's movement that draws it toward a French corps it can see with no
friend within one march, weighted by the odds.** It is adopted only by the rule in §13 (R-HUNT), and reported
per seed either way.

---

## §11 The voice, and the first turn

**The voice.** Named lines for seven French marshals in battle, acknowledgement and completion lines by nature,
and petition and jealousy lines all exist (`marshal_voice.py`). None is replaced. What is written new:

| Moment | Who gets lines |
|---|---|
| His proposal on the card; accepting | each of the seven by name; by nature for the rest |
| His morning line: he struck · he waited · he stayed put · he asks · the task is done | each of the seven by name; by nature for the rest |
| Being given today's order over his own · being recalled · being passed over | by nature |
| Answering a question | by nature, with named lines for the seven |
| A literal man repeating his orders, and standing when they do not cover the case | Soult and Grouchy by name |
| An enemy court's words in captured orders | by court |

Rules of a line: at most two sentences; the cause and the consequence ride beside it in plain words; lines are
keyed to the situation, and each man remembers one thing (a rival's absence, an order you overruled, a slight);
no line twice within his last three; on the historical seed the first line of each set is said; every line is
written by hand. A marshal's line is shown with his portrait and name. A full guide,
`docs/MARSHAL_VOICE_BIBLE.md`, is written in the voice slice.

**Golden rule 11, read for marshals.** The rule allows the period voice only in Berthier's and Talleyrand's
quoted lines. The marshals' written lines are already in that voice. The design reads the rule as covering any
named character's quoted line, with the plain words beside it; the rule's text is amended when the slice lands.

**The first turn.**

- **The menu.** On a machine with no saved campaign and no finished lesson, "The School of War — a guided
  campaign" is the highlighted, focused choice, with a line saying how long it takes and that you can leave.
  "Begin the 1805 Campaign" stays one press away.
- **The lesson is not cut.** Two cards are added near its end: setting a man on his own, and asking a question.
- **Two first-open lines** join the eleven: the first time TO DECIDE is shown, and the first time the card opens.
- **The real campaign teaches itself**: TO DECIDE is worked out from the board, so on turn one it already says
  "Mack stands in Swabia…".

---

## §12 Rulings on edge cases

*Every one of these came from a panel's finding, or from the reads of the code. The full ledgers are in
`docs/audits/ic_focus_groups/`.*

**Giving the order**

| Case | Ruling |
|---|---|
| The count is full | The card says so and offers to recall another man. A place freed is usable next turn. |
| A task against his nature | He objects, with today's answers. "Trust his judgement" takes his counter-proposal. |
| At peace | Only Hold and Support can be given. Take and Pursue belong to a named war. |
| He is broken, wounded or besieging | He can be given an order; it starts when he is fit. |
| Bernadotte set to Support a man | His ability makes him slow to the guns; the card says so, so you know what the order will and will not deliver. |
| A man is set to Support one he hates | Refused at the card, with the reason. |
| The Emperor | Cannot be supported by a man on his own, and cannot be set on his own. |
| A man acting without orders | Cannot be given an order on his own until that ends. |

**Each turn**

| Case | Ruling |
|---|---|
| Two men after the same enemy | The higher acts first. The lower's line says "after Ney; stays put if Ney's fight changes things". |
| He acted, and the enemy then attacks him | He defends. Defending is not an act. |
| He waited, and was drawn into a neighbour's battle by the arrival roll | That was his one thing. His if-thens are not checked that turn. |
| He tried to join and the roll failed | He did not arrive. His line says so. It was still his one thing. |
| His if-then takes him out of his area | The order goes to "asks". His task does not march him back. |
| He stays put because a higher man's act changed things | Staying put is waiting: his if-thens are checked. |
| Today's order, then a recall, then another order the same turn | Each at its price; the last is his one thing. |
| A marshal on his own in the Emperor's province | The Emperor's +10% and half glory apply, as today. His order carries on. |
| The area cannot feed him | He shifts within it; failing that he asks. Near the point of being shattered, he withdraws. |
| Supply or stacking | Today's rules. A supporting corps beside its friend does not count toward crowding, as today. |
| He is wounded | The order is suspended for the three turns. |
| His trust falls under 30 | He asks. Recalling him then costs no trust. |
| A last stand | Still your question, as today. It is rare and grave. |

**Battles**

| Case | Ruling |
|---|---|
| His attack may become a great battle | The line says "may". [Order it yourself] to fight the day by hand. |
| A day of battle he opened, which you leave | At nightfall it is fought his way ("leave it to him"), never in silence. |
| You take his day yourself | It costs him nothing: full glory if the Emperor's corps is absent. |
| The Emperor's corps is in the battle's province | It is the Emperor's battle (+10%, half glory); his morning line says what he thinks. |
| Two of your men in one battle | The higher-ranked leads the day. |
| Following a beaten enemy one province out | A field fight only: nothing stormed, nothing captured, no question raised. "Tonight" says "fights at X; will not keep it." |
| A siege interrupted by a try to join | The siege keeps its progress. |
| A capture inside his task | He secures it. No window opens at the turn's end. |

**Areas, roads and politics**

| Case | Ruling |
|---|---|
| The road to a Take is barred | He fights what bars it if his odds are met; otherwise he waits, and asks after two turns. |
| A pursued army leaves the ring, or flees where he may not go | He stops at the edge and asks; the row offers [Extend, 1 action] and [Recall]. |
| A pursued army is destroyed by another, or a place is taken by a friend | Done. |
| The friend he supports is killed or captured | He holds where he stands and asks. |
| The friend he supports goes where he may not | He stops at the border and asks. |
| His area is lost to the enemy | He retakes it if his odds are met; otherwise his if-thens, or survival, decide. |
| Peace | Every order in the land that made peace ends, and a Take or Pursue against that nation ends, wherever he stands. The road-home rule walks him out. |
| An ally makes peace, or an alliance ends | "Where he may go" is tested each turn; if he may no longer stand there he leaves by the nearest way and asks. |
| "Until Ney arrives", and Ney is killed or captured | The condition lapses and he asks. |
| "Until X falls", when X has already fallen | Refused at the read-back. |

**The count**

| Case | Ruling |
|---|---|
| The Staff lapses | N falls at the turn's refill, never mid-battle. The forecast warns first. Otherwise the lowest rank goes. No trust lost. |
| A man goes out of hand while the count is full | "2 of 1". Nobody is forced off. No new man until it is back under. |
| An ask is ignored | The row stays first in TO DECIDE. After three turns the order ends; no trust lost. |
| An exchanged prisoner | Comes back with no order. |

**If-thens and exact orders**

| Case | Ruling |
|---|---|
| Two lines come true the same turn | Only the first in the list fires. |
| Two literal men's lines fire together | Carried out by rank. |
| A line names a place lost, or a friend dead | It is struck; his line says "his orders are broken", and TO DECIDE flags it at once. |
| A used line's condition comes true again | Used is used. The card shows it. |
| A line fires and he is then forced back by the retreat rule | The line counts as used. |
| Three attack lines | Refused: at most one attack line an order. |
| A non-literal man is given two if-thens on an exact order | The second is not taken, and the read-back says why. |
| Buxhowden ordered to a friend he hates | A literal man obeys. His line grumbles. |

**The enemy**

| Case | Ruling |
|---|---|
| A court with one corps, or no literal marshal | Nothing changes for it but the favoured province. |
| A court at peace | No plan. Its plan takes effect the day it goes to war. |
| A court hires a literal marshal mid-war | The plan's current step carries one general set of lines for such a man. |
| A plan step aims at a province the court already holds | Skipped. |
| An allied court's literal marshal (Bavaria's Deroy) | He follows his own court's plan. France is not shown it. |
| Napoleon starts next to Mack | A line arms one turn after it is written; nothing fires on turn one. |
| Your routed man was after a place the enemy already favours | The five turns start again. |
| Captured orders name a fogged friend | The name and the intent are shown; where he is, is not. |
| A great battle the enemy's literal man opens | Offered to you only if a French corps fights in it, as today. |

**Display and saves**

| Case | Ruling |
|---|---|
| A "Tonight" arrow that points into fog | It stops at the edge of what France can see. |
| A busy turn | The turn-end list shows only acts; if-thens open on demand. The morning shows only men who acted or ask. |
| Colour | Never alone: a shape or a badge marks a man on his own; numerals at 16 px or more. |
| Keys | Every card action has one; Give is Enter; the turn-end list can be stepped through. |
| Saves | The order, its if-thens, used lines, the ring's centre, siege progress, the unseen-turns count, the stepped-out mark, a promised petition; for the enemy, the plan, its step and the favoured province; for France, what was learned and when. |
| Old saves | They have none of this. A war already running draws its plan on load. |

---

## §13 The numbers, and how each one is settled

Every number below is a placeholder. None is picked by feel. Each is settled by a rule written here, before any
measure is run.

| Number | Placeholder | Settled by |
|---|---|---|
| N at the start / with the Staff / with the Aides-de-Camp | 1 / 2 / 3 | R-BAND and R-FUN. **"2 at the start" is an arm of the measure**: every panel split on it. |
| The new law's price | 15 authority, 150 gold a turn | Reachable by a commanded France around turn 15 to 20 |
| Each marshal's own odds | Murat 5, Ney 6, Lannes 7, Masséna 8, Davout 10, Bernadotte 14 | Authored with the user; R-READ (two men must never read the same) |
| The risk step | 1 man in 10 | Smaller than the gap between two men |
| Trust needed | 30 | The game's own line between Wary and Hostile |
| The step outside his area | one province, once per order | R-TRUE: it is on the card and under "Tonight" |
| If-thens: on his own / literal / other exact orders | 2 / 3 / 1 | R-READ |
| The floor that trips nothing | a fifth of his strength | The measure's probes |
| The Pursue ring | three marches | R-FUN |
| Captured orders stay good | until the next step, two turns at most | R-HILL |
| TO DECIDE rows | 3 | R-READ |

**The rules:**

- **R-INERT.** Two switches guard the old game. With the player's side unused and the enemy's side off, every
  committed measure reproduces byte for byte. **A purity test**: run every question and every preview, then
  check that no key outside the game's existing inert list was written and no draw was taken from the global
  random stream. The promise "a reload changes nothing" is made for seeded campaigns; the historical campaign's
  battle dice are not reload-stable today, and this design does not change that.
- **R-TRUE.** Every act a marshal on his own made in the measure was exactly what "Tonight" said — or he stayed
  put, and the line had said he might.
- **R-BAND.** With men on their own in use on the three commanded seeds, France's provinces at turn 40 stay
  inside the gate band the project keeps (23 to 28). Reported per seed.
- **R-FUN.** Over twenty turns with men on their own in use: (1) the orders given by hand each turn fall by at
  least a third from turn 10 on; (2) at least four in ten of all orders are still given by hand; (3) each man on
  his own gives a moment worth a line (he asks, he stays put, he steps out, or he wins) at least once in eight
  turns and no more than once in three.
- **R-READ.** The blind reading the project uses: frames from the real client at the user's setup, the questions
  and the answer key written first, three fresh readers, every reader right on every question.
  - *The desk:* "What are you trying to do?" · "What would you do first?" · "What happens if you end the turn?"
  - *On his own:* "What will Masséna do tonight?" · "What might he do that you did not ask?" · "How many more
    men can you set on their own?" · "What will Soult do if Mack attacks him?"
  - *The enemy:* shown a literal marshal's captured orders — "What will he do if you do X?"
- **R-HILL.** With the enemy's side on: the story classes and the France band hold on the standing seeds; a
  literal enemy marshal acts no less often than today, **averaged over the plans and reported per plan** (the
  historical plan makes Mack more passive than today on purpose); and the enemy's reading of R-READ is met.
- **R-HUNT.** The hunt (§10.5) is adopted only if, on the standing seeds, the enemy's attacks on lone French
  corps rise, the France band holds, and no seed loses a story class. Otherwise it stays off. The table is
  reported either way.

---

## §14 What it stands on in the code (for the builder — verify each line first)

| Part | Stands on | New |
|---|---|---|
| The desk | `congress.titled` / `gate_terms`; `fall.warning_state`; `imperial_designs.goal_clause`; `war_status.build_active_wars`; `intent.build_intent_payload`; `strategic.pending_marshal_decisions`; `battle_day.awaiting`; the lapsing counts and `action_summary` on the response; `reforms.deck` / `law_refusal`; `recruitment.first_affordable_commission`; the jealousy warning | `backend/game_logic/today.py`: `aim_lines`, `to_decide`. Rides `build_base_response` and the `/test` boot payload. The typed "what now?" reads it. |
| The turn-end list | `main.gd` `_execute_end_turn` (seven conditions, one `_show_lapse_confirmation`) | One list above the input row; a "tomorrow" view on `scenes/map_order_layer.gd` |
| Reach | `question_desk._answer_safe` (the same idea, per province); `world.get_visible_enemies`; `get_nation_regions`; `order_quotes.march_reach`. **Not** `marshal.movement_range` alone — the code calls that an attack range. | `backend/game_logic/threats.py`, kept per turn |
| The pass | The seam where jealous strikes fire today (`turn_manager.py` about 592–603). Before it run a game-over early return, the Congress signatures (about 429) and the offer lapse (about 469). None moves a corps — but the lapse is not inert: an unanswered call to arms is refused, an unanswered petition lowers a client's loyalty, and an unanswered letter applies its decline, which can move gold, relations, loyalty, laws and ships. | The new pass sits **above** all of them, guarded by `_resuming`, so that nothing at all changes between your last order and his act. `process_autonomous_attacks` is unchanged but skips a man on his own. |
| The order | `StrategicOrder` and its serialization; the game's own test of where a corps may go | A new mode with `task`, `area`, `risk`, `if_thens`, `state`, the ring's centre, the stepped-out mark. `backend/commands/own_order.py`: give, read back, his way, the count, withdraw. |
| His choice | **A new, pure reading** — one function used by a question, by "Tonight" and by the act. It takes its candidates from the decision ladder's rules but draws nothing, writes nothing, and reads France's intel only. | It must **not** call `_get_mood_adjusted_threshold` or `ai_rng` |
| The odds | `combat_executor.muster_odds`; `order_quotes.attack_quote` | Fed with France's known strengths (the middle of a band where partly seen) |
| Trying to join | The arrival roll in `combat_executor` (reinforcements), with the support bonus | A marshal on his own is in the joiners' list only if he waited and has the if-then; joining marks his turn used |
| Your if-thens | `strategic.process_strategic_orders`; `contingency_trigger`; `_fire_contingency` | `contingency` becomes a list (2 or 3); the new "ifs"; one frozen board; by rank behind the switch (today it is alphabetical); men on their own who acted are left out |
| A day he opens | `battle_day._after_the_battle`, `night_falls`, `leave_it` | At nightfall a day led by a man on his own goes through `leave_it` |
| Peace | `diplomacy._collect_peace_order_cancellations`; `withdrawal.py` | The new mode joins the cancellations |
| The count | `reforms.EFFECT_TYPES` / `WIRED_EFFECT_TYPES` / `CLAUSE_SHAPES`; the validator; the `reforms` block of `europe_1805.json` | Effect `on_their_own`; one law in France's deck; the Staff carries +1 |
| The enemy's plan | `campaign_variance.seeded_int` / `seeded_permutation`; `war_council.aim_pull_set`; `WorldState.get_live_visible_enemies` | Plans in the scenario file, validator-checked (same first step; at most one "fall back from a named enemy" per list). A saved plan id, step, and favoured province per court. A pass for enemy literal marshals' if-thens that takes a nation and refreshes the live-sight cache first. `_evaluate_marshal` skips a planned literal marshal except for survival, retreat recovery and a battle he is in; the stagnation breaker yields to the plan. |
| What you learn | `diplomacy` GATHER_INTEL; the rout result in `combat_executor`; `enemy_voice.py` | A saved store of what France has learned of each enemy marshal, and when. Kept apart from the enemy's live state (`tactical_state` is player-only). |
| The voice | `marshal_voice.py`, `pick_marshal_voice`; `portrait_locket.gd`; each marshal's shipped ability | New line sets; a "said lately" record (saved); the portrait beside a line |
| The first turn | `main_menu.gd` (the status block); `tutorial_overlay.gd` `STEPS`; `first_open.py` `LINES` | The steer; two cards; two lines |

**The three riskiest pieces, in the engineers' order:**

1. **Re-sequencing End Turn** — the new pass above the signatures and the lapse; your if-thens by rank. *Needs
   first:* a frozen trace of today's End Turn with both switches off.
2. **Exact orders for every nation** — the list of if-thens; the trigger moved from France's intel store to
   per-nation live sight; the court's logic skipping a planned literal marshal. *Needs first:* the plan's steps
   written for one court.
3. **One pure reading for a question, "Tonight" and the act** — and the new law effect. *Needs first:* the
   purity test, written before the reading.

**Other warnings from the panels that read the code:**

- The undo stack empties when any later order cannot be taken back; that is why a just-given order has its own
  [Withdraw].
- A new saved key outside the take-back's `ORDER_KEYS` blocks the take-back.
- The decision ladder's "already attacked this target" brake is keyed by marshal and target: it stops one corps
  striking the same target twice. A second corps is stopped only against a stub, or on a target closed by a day
  of battle. The builder checks both when two men on their own go for one enemy.
- Today's standing-order class asks the player after a stalemate; those arms are stripped for a man on his own.
- The lesson's cards are counted and byte-sliced by pins. Two new cards mean re-seating them.
- A new order mode runs CLAUDE.md's twelve-step "adding a new action" list, the serialization tests and the
  save-format doc.
- **Not verified:** what each marshal's shipped ability does beyond Lannes's, Bernadotte's and Davout's. §6.7
  depends on it. The builder reads them all before any personal line is written.

---

## §15 The build — four sessions, eleven slices

The user's cadence: fewer, larger sessions; the low-risk one first, then a pause for his review; one measure with
arms; one review before each commit. Every panel that spoke of scope said to stage it.

### Session 1 — The desk and the turn-end list (display only; the board cannot move)

| Slice | What | Done when | Tests |
|---|---|---|---|
| **IC-1** | THE PEACE, THE WAR, TO DECIDE | The three lines show on turn one of 1805; every row's door works; "what now?" answers from the same list | `tests/test_ic1_the_desk.py`; driven `TestRowIC1TheDeskAtHisSetup` |
| **IC-2** | The turn-end list; reach; the "tomorrow" view; the report's tags | One list says every reason at once; a seen enemy edges what he can reach; an unseen one never does | `tests/test_ic2_the_turn_ends.py`; driven `TestRowIC2OnePressOrTwo` |
| **IC-3** | The menu's steer; what is hidden today, shown (the report of a man acting without orders; the jealous warning as a row) | A first-time machine lands on the lesson; a man acting without orders is seen on the map and in the report | `tests/test_ic3_what_was_hidden.py` |

Measure: R-INERT on every arm; R-READ for the desk. STATUS line: *"ROW IC, SESSION 1 — THE DESK AND THE TURN'S END"*.
**Pause for the user's review.**

#### Session 1's landing record — the desk (November 19, 2026; the first of two commits)

**Built** (`SYSTEMS_REFERENCE.md` §229 is the rule; `BUG_FIXES.md` §IC the ledger, 31 rows, none open):

- **IC-1** — THE PEACE, THE WAR, TO DECIDE from ONE key, `desk` (`backend/game_logic/today.py`), on every reply
  and at boot; the typed "what now?" answers from the same rows. Tests `tests/test_ic1_the_desk.py`.
- **IC-2** — the list when End Turn stops (`scripts/turn_end_list.gd`); what a seen enemy can reach
  (`backend/game_logic/threats.py`); the map's danger mark; the report's "You were warned" / "out of your
  sight". Tests `tests/test_ic2_the_turns_end.py`.
- **IC-3** — the menu's steer; a marshal who acted without orders named in the report; the jealous strike and
  the restless literal man as rows. Tests `tests/test_ic3_what_was_hidden.py`.
- Driven in the real client at the first player's setup: `tests/test_dd_b_the_client_hands.py::TestRowICTheDesk`
  (the names §15's table gave its driven classes were not used — one class holds the walk).

**Where it differs from §4 and §5 as written, and why:**

| The design said | What was built | Why |
|---|---|---|
| The three lines stand at the head of the command desk. | They stand on a card at the top-left corner of the map's room, beside the desk; one line on the slim bar. | At the first player's setup (scale 1.8 on 5120 x 1377) the desk's column is already full: three more lines pushed its header under the top bar. |
| One LINE as the turn ends, saying everything at once. | A LIST where the log is, one row a matter, each a door; the log's one-sentence warning is printed as before. | The warning was already one joined sentence, easy to miss and with nothing to press. |
| The line also says what each marshal on his own will do tonight, and a "tomorrow" view. | Not built. | They belong to "on his own" (§6), which is not built; nothing is promised on the screen. |
| A seen enemy "edges" what he can reach. | A mark on each province of ours he can walk into with nothing in his way, wearing the province's name; one march, for every corps. | One march is the game's own "in danger" verdict and claims nothing about an arm the player has not seen. |
| A first-time machine "lands on the lesson". | The School of War is the one lit row and holds the keyboard, with a line beside it; "Begin" is one press away. | Styling and focus only: no row renamed, moved or shut. |
| Going through a row's door ends End Turn's wait. | It does not: the list stays up while the wait stands. | The review: a wait ended there let the next End Turn straight through, the other matters never seen again. |

**One rule narrowed** (lever L4, from a blind reader): with no action left, corps with no orders no longer
stop End Turn (and are no row). R-INERT otherwise: `BASELINE_SERIES` byte-identical.

**The blind readings** (`docs/audits/ic_client/README.md`): the bar written first each time; reading 1 MET
21/21, reading 2 MET 27/27, reading 3 MET 6/6 — nine fresh readers. Ten levers were built from what the
readers said confused them (L1–L10); the last three were pressed in the real client and pinned by the driven
tests, not put to a fourth reading. What the readers still could not tell is listed there.

**The review before the commit:** three reviewers (the backend, the client, the words and the tests); no
serious fault; sixteen rows — thirteen fixed, three closed with their evidence.

**The pause** this section asks for stands: the second commit (directives) was NOT started in this session.
**Pushed** November 19, 2026, at the user's word ("Push both" — this commit and row PW part 3's).

#### Session 1's second commit — DIRECTIVES — landing record (November 19, 2026)

The user's rulings in Plan Mode: "One list for all", "Yes, named armies", "Desk, then directives". Built
(`SYSTEMS_REFERENCE.md` §230 is the rule; `BUG_FIXES.md` §IC directives the ledger, none open), as three
slices the approved plan numbered **IC-4 … IC-6** — the later sessions' slices below keep their content and
take the next numbers (IC-7 … IC-14):

- **IC-4 — the directive** (`backend/commands/directive.py`): any order to several marshals — the collective
  words, a list of names, a named army, a Ctrl-clicked group sent to a province — is ONE list before anything
  is spent (each man's order, its price, whether he may object, who will not go and why, the total against the
  actions in hand), given on one confirmation as ONE request and taken back as one. Tests
  `tests/test_ic4_the_directive.py` (with a fuzz).
- **IC-5 — named armies** (`backend/game_logic/armies.py`): form · add · remove · disband, free; the chip;
  "Army of Italy, hold". Tests `tests/test_ic5_named_armies.py`.
- **IC-6 — the war goal** (`backend/game_logic/war_goals.py`; §9's naming and showing half): set and clear,
  free; THE WAR line, the gold ring, the war's window, and a TO DECIDE row that opens the march on it as one
  list. Tests `tests/test_ic6_the_war_goal.py`.
- Driven in the real client at the first player's setup: `tests/test_dd_b_the_client_hands.py::TestRowICDirectives`.

**Where it differs from the design as written, and why:**

| The design said | What was built | Why |
|---|---|---|
| A directive is "high-level" — an order the marshals carry out in their own way. | Each man's OWN order, as the game would carry it out for him alone, shown row by row; nobody improvises. | The user's ruling "One list for all": what is shown is what is done. A marshal's own judgement belongs to "on his own" (§6), not built. |
| §9: "take the war goal" — changing the goal turns every man who serves it. | The goal is named, shown and offered as one list; nobody serves it by standing order. | Serving a goal is a standing order of "on his own"; it stays with IC-10 (§15, Session 3). |
| A group sent by a click marches. | Each man takes his own click order — a move next door at one action, a march beyond — and the head says "go to". | Row PW's click rule for a single corps; a group charged the two-action march to all. |
| (not in the design) | The war's purpose and the player's goal are told apart in words ("— your war goal: Vienna"). | Blind reading 2: "to hold the homeland — goal: Vienna" read as one aim. |

**The blind readings** (`docs/audits/ic_client/directives/README.md`; questions and key written before each
reading's frames): reading 1 MET 21/21, reading 2 NOT MET 28/30, reading 3 MET 15/15, reading 4 MET 12/12 —
twelve fresh readers, 76 of 78; sixteen levers built from what they said confused them.

**The review before the commit:** three readers by lane and a skeptic for each; sixteen rows (IC-R17 …
IC-R32), every one fixed — among them "Army of Italy, disband" read as an order to its first man, the desk
plotting every idle corps' road on every reply, and a fog leak of an unseen commander's fall.

**Inert where unused:** the byte-identity series and the France band (26 / 27 / 28, `tools/_ic_band_2026_11_19.json`).

### Session 2 — On his own

| Slice | What | Done when | Tests |
|---|---|---|---|
| **IC-7** | The order, the pure reading, the pass, "Tonight", the card, the count and its law, the morning block (lines by nature) | An order can be given by card; "Tonight" equals the act on every path of the life table; the count holds; the Staff raises it | `tests/test_ic7_on_his_own.py` (each task; each state and its way out; one thing a turn; the purity test; the count; serialization); driven `TestRowIC7InTheClient` |
| **IC-8** | Talking: open lines, ask, change, today's order, recall, withdraw; the read-back rule | Every line of §8 works with no key; nothing is spent before the read-back is confirmed | `tests/test_ic8_talking.py`; rows in the golden corpus |

Measure: one sweep with arms — as today; N 1; N 2 at the start; N by the ladder — on the three commanded seeds.
R-INERT, R-TRUE, R-BAND, R-FUN; R-READ for "on his own". STATUS line: *"ROW IC, SESSION 2 — ON HIS OWN"*.

### Session 3 — Exact orders, the war goal, the voice

| Slice | What | Done when | Tests |
|---|---|---|---|
| **IC-9** | Exact orders for France's literal men | Three if-thens; one attack line at most; each used once; one thing a turn; an uncovered case is a row, not a stop | `tests/test_ic9_exact_orders.py` |
| **IC-10** | The war goal; "take the war goal" | Changing the goal turns every man who serves it, at its price | `tests/test_ic10_the_war_goal.py` |
| **IC-11** | The voice: each marshal's shipped ability as his personal line; authored odds; the new lines; "said lately"; the portrait; `docs/MARSHAL_VOICE_BIBLE.md`; rule 11's wording; the lesson's two cards | No line twice in a man's last three; three readers tell two marshals apart from their lines alone | `tests/test_ic11_every_man_his_own_line.py` |

STATUS line: *"ROW IC, SESSION 3 — EXACT ORDERS, THE WAR GOAL AND THE VOICE"*.

### Session 4 — The other side of the hill

| Slice | What | Done when | Tests |
|---|---|---|---|
| **IC-12** | War plans; enemy literal marshals under exact orders | Each court at war draws a plan; a planned literal marshal has one master; his if-thens read his own nation's sight | `tests/test_ic12_the_war_plan.py`; a fog census pin for every enemy if-then |
| **IC-13** | Natures public; the spy's report; captured orders | Nothing is shown that was not learned; knowledge ages by time only | `tests/test_ic13_what_you_learn.py` |
| **IC-14** | The hunt, as an arm; the closing measure and readings; the records | Every rule of §13 is met on the final tree, or the report says which was not | `tests/test_ic14_the_hunt.py` |

STATUS line: *"ROW IC, SESSION 4 — THE OTHER SIDE OF THE HILL — ROW IC COMPLETE"*.

**Where the row sits against the deploy.** By default all four sessions run before the deploy session — the
pattern of rows BA, OC and PW, and the user's standing rule that content is not cut or pushed back to protect a
date. This is sizing, not pressure. One line to reverse.

---

## §16 Decisions taken (each is one line to reverse; strike any)

| # | Decision | Why |
|---|---|---|
| D1 | The feature is called **on his own**; the game's "independent command" stays the name of the three turns without orders | "Mission" and "a free hand" mean something else in diplomacy; the panels asked for one plain phrase |
| D2 | A literal man **cannot** be set on his own; he gets **exact orders** | The user's "this gives literal a purpose" |
| D3 | The count limits **judgement only**; exact orders are not counted | An exact order never chooses; counting them would cap the ordinary marches the game has today |
| D4 | The courts set no man on his own | They are not short of actions; forcing it made them worse (§17) |
| D5 | N is 1, 2 (the Staff), 3 (a new law) | Placeholders; "2 at the start" is measured |
| D6 | **He acts first when you end the turn**, before the enemy moves | So that "Tonight" is true; no side gets the last word |
| D7 | **One thing a turn**, for every marshal with a standing order | It is the price of handing off, and it closes every double act the panels found |
| D8 | He never improvises: what the screen said, or he stays put | "Show before, never surprise" |
| D9 | No moods and no dice in his choice; each marshal's own odds are authored | So the card's sentence is true, and the men differ |
| D10 | He reckons from what France knows, and never attacks what France cannot see | So a free question cannot probe the fog |
| D11 | Four tasks — the four standing orders the game has | One new idea, not five |
| D12 | He secures what he takes; no plunder switch | Fewer rules; plunder stays the player's own choice by hand |
| D13 | Any change costs 1 action, at once | One price; no hidden pending state |
| D14 | Each if-then is used once; a literal man has three, of which one may be an attack | A bound that needs no count |
| D15 | A marshal's personal line is his shipped ability | The game already made the men different; nothing is contradicted |
| D16 | The enemy keeps its hand and gains a war plan with steps | Readable, varied, and inert when switched off |
| D17 | Natures are public | Reputations were; it gives the player a read from turn one |
| D18 | No false orders, ever | The project's standing principle: a surprise is never a lie |
| D19 | The hunt is a measured option | A claim the code did not support becomes a rule tested before it is kept |
| D20 | The desk's three lines sit at the head of the command desk | It reflows in every form and keeps the map clear |
| D21 | Marshals' quoted lines may keep the period voice; plain words ride beside | It is what the existing lines already do |
| D22 | The lesson is not cut; two cards are added | Nothing is cut without the user's word |
| D23 | Four sessions, all before the deploy | The same standing rule; every panel said to stage it |

---

## §17 What was cut, and why

Each was in an earlier version of this design. Each was cut because panels showed it did not work.

| Cut | Why |
|---|---|
| **Enemy "roles"** — a main army in hand, the rest in standing roles | The enemy is not short of actions. Roles made it slower or easier to solve, broke its existing reactions (recapture, threat response), needed rules for a destroyed main army and for assigning roles, and needed per-nation fog the game does not have. Two rounds scored the enemy's side lowest because of them. |
| **A "capital in danger" recall** | It rested on a rule that does not exist, was gamed by a single feint, and was false history for Russia and Britain. |
| **The enemy's posture as a plan's dial** | The code recomputes it every turn and already shows it. |
| **Berthier's reading** of an enemy marshal | It contradicted "each line used once": what France saw him do is exactly what he will not do again. |
| **A marshal who acts after the enemy has moved** (version 2) | A plan he might not keep was "a lie on the map", and France's men got the last word every turn. |
| **A one-night lag on adjustments** | A hidden pending state. One price replaced it. |
| **Attached corps (the Wing)** | Never worth their place in the count. A second man set to Support the first does the same job. |
| **Counting literal men** as "on their own" | They are not. The one-attack-line bound does the work. |
| **The plunder switch** | Dead weight. |
| **The Watch task** | It overlapped scouts and towers, and broke the match with the four standing orders. |
| **"How boldly: Press / Steady / Safe"**, then "high / normal / low" | Each clashed with another word or read backwards. Now: more / usual / less, always with the odds. |
| **Ground in hand by command skill** | Masséna's command skill is 3 in the 1805 file. |

---

## §18 Refused, and recommended but not built

**Refused, with reasons** (none is a promise for later):

- **A purpose picker, a "contain" or "fix" task.** Three panels of historians asked. The card states a "so
  that"; and the game has no rule by which fighting pins an army — that would be a combat design of its own.
- **Couriers, or any delay on orders.** Three panels of historians asked; every other panel approved its absence.
- **A second axis of character, or recasting Davout and Soult.** The natures are earlier rulings that run
  through the whole game. Authored odds and shipped abilities do the work here.
- **Counting every standing order.** It would cap the ordinary marches the game has today.
- **Upkeep on a man on his own.** Bookkeeping; the choice is who and what.
- **An if-then that fires every time.** It is a man on his own outside the count.
- **A false order the enemy can plant.** A surprise is never a lie.
- **A personal line that breaks a "never"** (Murat taking an unnamed capital). Conquest stays the player's act.
- **A favoured province per enemy corps; coalition armies of mixed nations.** New behaviour in the enemy's hand,
  or a change to how nations own corps.

**Recommended, not in this design** — offered because the user has said expansions are welcome; each would need
his word and its own gate:

- **A price for distance.** An order changed more than three marches from the Emperor costs 2 actions, not 1,
  and the button says so. It gives "you cannot be everywhere" teeth with no waiting. Raised by historians in all
  three rounds.
- **A pinning rule in combat**, so that "pin him" could be a real task.
- **A second line of character** for the marshals (discipline beside daring).

---

## §19 The record of the focus groups

**How it ran.** Six panels a round, four experts each, told to disagree and that a panel which only praises is
useless: players; designers; historians; newcomers and UX; engineers and QA; the enemy's side. The last two read
the game's code. Fresh people every round — 72 in all. Round two was told what round one found and how it was
ruled, and asked to break the rulings; round three likewise. The rules of the loop — what each panel returns,
how every finding is ruled, and when the loop stops — were written before any panel saw anything
(`docs/audits/ic_focus_groups/00_the_bar.md`).

**The bar:** no accepted fault of the first rank left open; no more than three of the second; the middle of all
scores at 8 or more; no panel under 7 on Solidity or Want. At most three rounds.

**The scores** (the mean of six panels, out of 10):

| | Round 1 (version 2) | Round 2 (version 3) | Round 3 (version 4) |
|---|---|---|---|
| A Clarity | 5.8 | 5.8 | 6.2 |
| B Agency — is it you playing? | 6.7 | 7.0 | 7.0 |
| C Character — are the marshals different men? | 7.2 | 5.3 | 6.2 |
| D Solidity — can a rule be broken? | 4.0 | 4.5 | 4.5 |
| E The enemy — a better and fair opponent? | 5.5 | 5.3 | 5.5 |
| F Typing — does the typed line have a real job? | 5.8 | 5.7 | 5.2 |
| G Want — would you play it, or fight to build it? | 6.8 | 6.3 | 6.8 |
| **Middle of all 42 scores** | **6** | **6** | **6** |
| Faults of the first rank raised (counting each panel's separately) | 25 | 19 | 17 — 11 distinct |
| Verdict asked for | — | — | **24 of 24: build it after these fixes** |

**THE BAR WAS NOT MET, in any round.** Three things should be said about that:

1. **The scores did not rise.** Each round's panels were sent to hunt for faults, and found real ones in
   whatever had just been changed. Agency rose and held. Character fell when the dice were removed and partly
   recovered. Solidity stayed low throughout: a design of this size has many joints, and a pitch cannot close
   them all.
2. **The findings did converge, modestly.** First-rank faults fell from 25 to 19 to 17, and the last round's 17
   were only 11 distinct faults: three panels independently named the same top one. Every one of them is ruled
   in §12 and written into this version.
3. **This version is untested.** Nobody has read version 5. The honest reading is that the design is much
   sounder than it was, and is **not proven**. The first session is display only for that reason, and the
   user's own play outranks every panel.

**What each round changed.**

- *Round 1* found that tasks which follow a moving target broke "he keeps to his ground"; that the cap leaked;
  that fog was not stated for the enemy; that trust could be farmed; that a default harmed the player unasked;
  and — from the panels that read the code — that two of the design's claims about the existing game were
  false (the capital recall; "nothing is random"). Version 3 moved the marshal's act to the turn's end, before
  the enemy, so that what the screen says is what he does.
- *Round 2* found that acting before the enemy had cost him the power to react; that removing the dice had made
  four bold men one man; that the new capital rule was gamed and false; and that the enemy's "roles" made it
  worse. Version 4 answered mostly by cutting.
- *Round 3* found the remaining joints: when "march to the guns" fires; a lower man's dependence on a higher
  man's battle; personal lines against other rules and against the abilities the game already ships; the
  literal man as a free attack loop; and an enemy literal marshal with two masters. Version 5 is the answer.

**Dissent that stood through all three rounds.**

- **Historians:** the order has no stated purpose; nothing costs more for being far away; one axis of character
  cannot hold Davout or Soult. (§18)
- **Typing:** a real job for asking; a shortcut for almost everything else. (§8)
- **The enemy's side:** readable and fairer, not stronger; in 1805 it changes two or three marshals. (§10)
- **N of 1 at the start:** split in every panel. It is an arm of the measure. (§13)

**The files:** `docs/audits/ic_focus_groups/` — the bar; the three pitches as the panels read them; the three
ledgers with every finding and its ruling.

---

## §20 Records, and the next session's prompt

**WRITTEN at the close of Session 1's first commit (November 19, 2026)** — STATUS's entry and NEXT UP line, CLAUDE.md's live state, `SYSTEMS_REFERENCE.md` §229, `BUG_FIXES.md` §IC; and at the close of its second (directives, the same day) — §230, `BUG_FIXES.md` §IC directives, STATUS, CLAUDE.md, `SAVE_FORMAT_REFERENCE.md` (`armies`, `war_goals`), `docs/NEXT_SESSION_PROMPT.md`. The paragraph below is the record of why they waited. **Not written in the design session, on purpose.** `docs/STATUS.md` holds exactly seven session entries and its pin
allows seven. `CLAUDE.md` is one byte under its size cap. Both carry pins that cost a full run of the suite, and
the working tree holds the user's uncommitted work. The routing lines for row IC are written at the close of
Session 1, with the trims they need. Until then this file, the folder `docs/audits/ic_focus_groups/` and the
memory note `feedback_autonomous_marshals_typing.md` are the record.

**The next session's prompt, decided now:**

> Build row IC, Session 1 — the desk and the turn-end list — from `docs/INDEPENDENT_COMMAND_SPEC.md` (§4, §5,
> §11's menu steer, §15). Plan Mode first. Display only: the board must not move (R-INERT on every arm). Verify
> each line of §14 against the code before relying on it. Press everything in the real client at Interface Scale
> 1.8 on a 5120-wide window. Write the blind reading's questions and answer key before any frame is shot. One
> review before the commit. Write the row's routing lines into STATUS and CLAUDE.md with the trims they need.
> Then stop for my review before Session 2.
