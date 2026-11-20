# On His Own — the Emperor's desk, his marshals' judgement, and exact orders (row IC)

> **Status: DESIGN, version 6 — November 20, 2026 — the review of "on his own".** The user's words that day,
> verbatim: *"review the new autonomous generla conmcept assure low authority autonomy isnt in conflict even
> removing it if needed and make sure buttons exist for simpler things but typing is used for missions and
> excepts a wide array if things and also if army has differner personalities they arent all doing same thing
> every turn etc full reveiw and u[pdates"*. Four code readers, three design panels run twice each (two
> independent samples per question) and two adversaries reviewed version 5 (§19.4; every finding and its ruling
> in `docs/audits/ic_focus_groups/round4_review_ledger.md`). **What version 6 changes:** the trust crisis's
> "Grant Autonomy" — three turns run by the enemy's AI, with its moods and dice — is REMOVED by the user's
> consent and replaced by **a task to prove himself** under exact orders (§6.11); **every simple order is a
> button and a task is a typed sentence** that opens already filled with the marshal's own proposal (§8); **men
> of different natures do different things, night after night**, with no dice in their choice (§6.7); an
> army's task (§9.1); the build re-cut into three sessions, all before the deploy (§15). Version 6 was read by
> two fresh readers before its commit; **it has not been put to a scored panel**, and the user's own play
> outranks every panel. Nothing version 6 adds is built yet; the desk and directives below are.
>
> **Version 5's status, as it stood (November 19, 2026) — BOTH COMMITS the user approved are BUILT, the same day:
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
> The routing lines (STATUS, CLAUDE.md) are NOT written yet — see §20. *(Written at the close of Session 1's
> two commits, November 19; version 6's on November 20 — §20.)*

**How to read this.** §0 is the design on one page. §2 is the order of a turn. §3 walks three mornings. §4–§11
are the parts — §6.7 is how the men differ, §6.11 is autonomy you grant and acts you did not order, §8 is the
buttons and the typed tasks. §12 is every ruling on an edge case. §13 is every number and how it gets settled.
§14–§15 are for the builder. §16 lists every decision, each one line to reverse. §17–§18 say what was cut,
refused, or only recommended. §19 is the record of the focus groups and of the November 20 review (§19.4).

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
   thing a turn, and the screen says what, before you end the turn. **Who he is decides what he does** — his own
   proposal, his own odds, his own way of waiting, his own recent battles — so Ney, Murat and Davout on one
   board do three different things, and none of them does the same idle thing night after night (§6.7). No
   dice in his choice.
4. **Exact orders.** A literal marshal takes no order "on his own". His standing order carries up to three
   if-thens, which he follows to the letter.
5. **Buttons for simple orders; typing for tasks.** Every simple order — one man, one act — is a button. A
   **task** — a standing order with a condition, a time limit, a risk, two places or an if-then (what the user
   called "missions") — is a sentence you type; the line opens already filled with the marshal's own proposal,
   and word-chips under it write into the sentence. The line takes a wide array of wordings, reads back what it
   took and what it did not before anything is spent, and the marshal answers in his own voice (§8). Asking is
   free.

**One new idea for the player.** There are two kinds of order: **today's order**, given by hand; and **a
standing order**, which is either *exact* (as today: it does the one thing it names and never chooses) or *on
his own* (new: he chooses).

**Autonomy is only ever given.** A man is on his own because you set him so — never because his trust broke or
your authority fell. Low authority makes men restless and disobedient (they attack without waiting for orders,
or refuse an order you press); it never sets anyone on his own (§6.11).

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

**Words this design reserves** (version 6; each phrase means one thing on every screen, and no two overlap — §6.11):

| On screen | Means | Never used for |
|---|---|---|
| **on his own** | a man *you* set to act by his own judgement | anything the game does to a man unasked |
| **a task** | a standing order with its parts, given by typing (§8); the user's "missions" | — ("mission" stays the diplomats' word: the spy mission) |
| **a task to prove himself** | the trust crisis's answer: one task, under exact orders, three turns (§6.11) | — |
| **attacks without waiting for orders** | the jealous strike, warned the night before | a man on his own |
| **refused your order** | V2b: he declined an order you pressed | a man's own task as given |

"Autonomy" and "independent command" leave the marshals' screens (the vassals' autonomy scale is another
screen and keeps its word).

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

**November 20, 2026** (the review; quoted whole in the status block). Version 6 reads it as three rulings and
one delegation:

- **"assure low authority autonomy isnt in conflict even removing it if needed"** — the game never grants
  autonomy for low authority (the code was read: §1.3); the autonomy that does conflict is the trust crisis's
  three turns on the enemy's AI, which the user's "even removing it" consents to remove. It is removed and
  replaced (§6.11). Low authority's real effects — men who attack without waiting for orders, men who refuse
  an order you press — are kept and named apart.
- **"make sure buttons exist for simpler things but typing is used for missions and excepts a wide array if
  things"** — every simple order gets a button, and the typed line becomes the road for tasks, reading a wide
  word table (§8). This amends version 5's §8, which had given tasks a card.
- **"if army has differner personalities they arent all doing same thing every turn"** — the men differ by who
  they are and by what has happened to them, not by dice (§6.7); an army's men take different parts of one
  task (§9.1).
- **"full reveiw and u[pdates"** — the delegation: the review's rulings are taken here, each one line to
  reverse (§16), and the next session's prompt is pre-decided.

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
  (`main.gd` `_execute_end_turn`). *(Version 6: at least nine since row IC's desk — say "several".)*
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

**What the November 20 review found in the code** (four readers, each claim at file and line; every one is in
the ledger, `docs/audits/ic_focus_groups/round4_review_ledger.md`):

- **Authority never grants autonomy.** The only standing "acts on his own" state is the trust crisis's "Grant
  Autonomy" (`disobedience.py`, offered at trust 20 or less, always — the only arm besides paying him when he is
  the last field marshal). It hands the man to `EnemyAI.decide_single_action` — the enemy's moods and score
  jitter from the shared `ai_rng` stream — for three turns in which he takes no orders, and it runs **after**
  the enemy has moved (`turn_manager.py`, the call near line 777). Nothing shows what he will do before the turn
  ends. It breaks five of this design's rules (D9, §6.5, §2, §6.4, D1). *Version 5 had said "left as it is;
  shown and counted"; round 2 of the panels had already ruled the opposite (G2-10: "they act in the same pass,
  by the same fixed odds"). Version 6 removes it (§6.11).*
- **Low authority's real effects are indiscipline, not autonomy:** below 30 every jealousy threshold falls to 1
  but a devoted man's, who stays immune (`jealousy._threshold_for`, the breakpoints in
  `backend/models/authority.py`), so a bold man turns jealous — and so warned and striking — sooner; below 50 a pressed order is refused more often (V2b, `defiance.py`, +10 points);
  below 50 the Staff's order to several is not heard and between 50 and 69 a doubting man answers in person
  (`group_orders.py`, `ARMY_AUTHORITY_HEARD` / `ARMY_AUTHORITY_CARRIES`); a purchase priced in authority is
  refused when paying it would leave your authority under 60 (`standing.refusal`, the purchase floor).
- **Nothing stops a man acting independently from striking too** (`jealousy.py`'s warning pass and
  `process_autonomous_attacks` never read `autonomous`): an aggressive, jealous man in the trust crisis's three
  turns can strike before the enemy moves and act again on the enemy's AI after it — two acts in one turn.
  Filed as **IC-V3**.
- **"Every order has a button" (row PW part 3's record) is false** for eight simple orders — chase (pursue), the
  one-action stand (defend), posture (stance), square, bombard, scout a named province, a charge the player
  starts, stay put — and the group face lacks attack, support, fall back and garrison; the Help's Orders page
  says the map's clicks "give the same orders" as the typed line (`codex_view.gd`). Filed as **IC-V4**.
- **The typed line has no road for a task.** It reads four standing verbs, five kinds of "until", one if-then
  shape and a "then" after a march (`strategic_parser.STRATEGIC_KEYWORDS`, `condition_grammar`); risk words are
  not read at all (only "carefully" is set aside, as an aside — `reading.py`); a target is one place or one man.
  **The read-back** (`parse_preview`) shows neither a condition it took nor a clause it dropped — both appear only
  after the order is sent (**IC-V2**) — and a one-word condition slips under the clause guard's two-word floor
  (`clause_guards.py`, counted after the "if") and is blanked, not named: "Ney, retreat if outnumbered" retreats
  now and the "if" is said nowhere before he goes (**IC-V1**).
- **Today's enemy differs by type, not by man.** Its thresholds are per nature (`enemy_ai.ATTACK_THRESHOLDS`);
  skills and shipped abilities play no part in its decisions; its daily mood is one stream per nation, drawn in
  call order, so it is noise rather than character. Version 5 as written would have made the bold men
  near-copies and set the careful men digging in every night (§6.7 answers it).
- **A bold man's standing order already yields to cannon fire** within two provinces, in a war France may
  lawfully join (`strategic.py` `_check_interrupts`, the "cannon_fire" redirect; a careful man asks instead) — which would make "Tonight" false for a bold man on his own;
  version 6 exempts him (§6.5).
- **Directives are uniform by design** (`group_orders._run_members` sends each man the same line): right for an
  order you give; the men's differences belong to what they do on their own.
- **A pure per-man, per-turn draw is buildable** (`campaign_variance._unit`, a hash with no stream: reload-proof
  and question-proof) — version 6 keeps it only as R-VARIETY's written fallback (§6.7, §13).

**What already exists and is built on here:**

| Already in the game | Where | What this design does with it |
|---|---|---|
| A marshal can act without orders for three turns after a crisis of trust, on the enemy's decision logic | `EnemyAI.decide_single_action`; `TurnManager._process_autonomous_marshals`, `_end_autonomy`; the audience's arms in `disobedience.py` | ~~Left as it is; shown and counted.~~ **Version 6: removed** — replaced by a task to prove himself under exact orders, with the same rewards (§6.11). "Independent command" is retired as a name. |
| …but the client never shows his report | no reader of `independent_command_report` in any `.gd` (row IC's desk names him in the report) | Goes with the old engine |
| A jealous, idle bold marshal strikes on his own "as the turn closes, before the enemy phase", after a warning | `jealousy.process_autonomous_attacks`; `turn_manager.py` about line 599 | The same seam carries the new pass. The strike is unchanged but for two things: it skips a man on his own (a guard the code lacks — IC-V3's sibling), and its words become "attacks without waiting for orders" |
| A marshal can petition for an independent command | `jealousy.check_shadow_petitions` | "Give him a front" opens the line with his own proposal (§6.9) |
| A bold man's standing order yields to a battle within two provinces | `strategic._check_interrupts` ("cannon_fire") | A man on his own is exempt (§6.5) |
| The Staff's orders to several are not heard below authority 50 | `group_orders.py` (`ARMY_AUTHORITY_*`) | An army's task (§9.1) obeys the same rule |
| A read-back of every typed order before it is sent, one reader for preview, card and executor | `parse_preview.read_one`; `directive.quote` | The four rows of §8.4 |
| The grammar of conditions and the one if-then | `condition_grammar._READ_CLAUSES`, `_CONTINGENCY_RE`, `describe_condition`, `describe_contingency` | The word table of §8.3 |
| A word list generated from the code, checked by a census | `tools/gen_routed_order_words` (CX-R1) | How §8.3's table generates the parser's words |
| The general's card: seven fixed slots with prices; the province chips; the group face | `marshal_state.gd` (`SLOTS`), `selection_card.gd`, `region_panel.gd`, `order_confirm_card.gd` | Where the missing buttons go (§8.1) |
| Davout's Iron Resolve (a stack each fortified turn, three at most) | `marshal.py` | His way of waiting has a point (§6.7) |
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
| **2. You end the turn** | **First of all, before anything else moves:** every marshal on his own does what the screen says under "Tonight" — an act, or *waits* — highest rank first. **Then the jealous strikes** ("attacks without waiting for orders"), only for men with no order and no act this turn, re-read on the board his acts left; a strike that no longer holds says so (its warning said "may"). Where a strike and his act aim at one enemy, rank settles it across both passes. *(Version 6: nothing else acts for a French marshal at the turn's end — the trust crisis's three turns on the enemy's AI, which ran after the enemy had moved, are removed: §6.11.)* |
| **3. The enemy's if-thens** | Each enemy literal marshal checks his if-thens once, on what you have just done. |
| **4. The enemy's turn** | Each enemy nation moves its corps, as today. If a battle is fought next to a marshal of yours who *waited* and has "march to the guns", he **tries to join it** — the game's existing arrival roll. |
| **5. Your if-thens** | Checked **once, on the board as the enemy left it**, for your marshals who waited and did nothing else, and for exact orders — a task to prove himself (§6.11) among them; carried out highest rank first. One that has become impossible does nothing and is not used up. No chains. Standing marches go on, as today. |
| **6. Morning** | What you lost and gained; one line from each of your marshals; then the rest. |

**One thing a turn.** Any marshal with a standing order does exactly one of these in a turn: today's order, if
you give him one; **or** the act shown under "Tonight"; **or**, if he *waited*, joining a battle next to him or
the first of his if-thens to come true. Never two. Defending when attacked is not an act. Digging in while he
waits is not an act. *(Version 6: of his ways of waiting (§6.7), digging in and looking are waiting — his
if-thens are still checked and he may still answer a battle next to him; a probe, a fall-back, a siege or a
strike is his one thing that night. All of them are shown under "Tonight".)*

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

You press the second. *(Version 6: the line, not a card.)* The command line opens already written, with the
read-back under it:

> *Masséna, hold Milan, and fight at our 8 to their 10 or better.*
> chips: **[more risk]** **[less risk]** **[until…]** **[if…]**
> *Taken:* hold Milan · his odds, our 8 to their 10 (he attacks only with at least 8 men for every 10 of
> theirs) · *Masséna: "Milan will not fall while I hold it, Sire."* · *2 actions*

You press Enter. The desk now reads *On their own: 1 of 1*.

You turn to Soult and type: *"Soult, hold Lorraine. If an enemy comes within reach, attack. If outnumbered, fall
back on Champagne."* The line reads it back before it costs anything:

> *Taken:* Soult · hold Lorraine · 1. if an enemy comes within reach, attack **if not outnumbered** (today: our
> 9 to their 10) · 2. if outnumbered, fall back on Champagne
> *Not taken:* nothing. *1 action. 1 if-then still free.*

You press End Turn. One line: *"Tonight: Masséna waits · Lannes has no orders."* You press again.

**The second morning.** The enemy's moves play on the map. The Archduke has marched into Tyrol, beside Milan.
Under "Your marshals": *Masséna: "The Archduke is in Tyrol with forty thousand." — He waited. Nothing of his
came true.*

And at the turn's end the line now reads:

> *Tonight:* Masséna strikes the Archduke in Tyrol, beside his area — our 8.4 to their 10; he comes back after.
> May become a great battle. **[Order it yourself]**

*(Version 6: names corrected — "Venetia" and "Ulm" are not provinces of the 1805 map; Milan's neighbours are
Piedmont, Tyrol and Munich. The strike beside his area is a bold Hold's one step out, §6.7.)*

You can let him, or give the order yourself and fight the day by hand. You let him. He fights it his own way.

**A later morning.** You have bought the Staff, so the desk reads *On their own: 1 of 2*. Ney, with no such
order, has watched Masséna's name in the bulletins; TO DECIDE says *"Ney may attack without waiting for orders
tonight."* **[Give him an order]** **[Set him on his own]**. You want Bavaria kept, not risked, so you choose
Davout — and the read-back says first: *"Ney ranks above Davout, is within three marches, and has no order of
his own. He will take this ill. Nobody would mind if you chose Ney."*

**Weeks on** — the Staff and the Aides-de-Camp bought, three men on their own on the Danube *(version 6)*:

> *Tonight:* Murat chases Kienmayer's horse into Munich — two provinces at most, in the field only; he will
> not storm the walls.
> *Tonight:* Ney attacks Mack in Swabia — the odds are our 6 to their 10, and since his last win he goes in at
> 5 or better (his own 6, one step bolder).
> *Tonight:* Davout digs in in Franconia — Iron Resolve 2 of 3; he strikes when it is full.

Three men, one front, three different nights — and tomorrow Davout's line will not say "digs in" a third time
while there is a siege to begin.

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
   literal man with no if-then left. A bold man who may attack without waiting for orders tonight (built today
   as "may attack on his own when the turn ends" — version 6's words, with two buttons: [Give him an order]
   [Set him on his own], the second only while a place in the count is free).
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

> *Tonight:* Masséna strikes the Archduke in Tyrol — our 8.4 to their 10. May become a great battle.
> **[Order it yourself]**
> *Tonight:* Davout waits. If Ney is attacked next to him, he tries to join.
> *Then:* Lannes may attack Mack without waiting for orders (warned last night).
> *Also:* Murat has no orders · a letter from Vienna lapses tonight · Mack (about 50,000) can reach Munich.

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
| **Risk** | **More · usual · less**: one man in ten either side of *his own* odds. Always shown as numbers, in the form "our 8 to their 10" (more risk: he goes in at our 7 to their 10; less: at our 9). *Version 6:* **his figure moves two steps at most, in all** — one from you (a word such as "boldly" or "carefully", §8.3, or a chip; saying it twice changes nothing) and one from him (his recent record or his impatience, §6.7, or Ney's line on reaching an enemy — when more than one applies, still one step). A word can never make Bernadotte fight at Murat's odds. The read-back shows all three numbers. |
| **If-thens** (up to two) | The same lists as exact orders (§7). Each is used once. They are checked only on a turn he waited. On a turn he acts they show greyed: "only on turns he waits". |

These four tasks are the four standing orders the game already has. Nothing else is added. *(Version 6: a task
typed in a sentence — §8 — is one of these four with its parts; it is never a fifth task. A Hold of two
provinces is one area: he does one thing a turn inside it.)*

**His own odds are authored**, one figure per marshal in the scenario file, spaced further apart than the risk
step so that two men never read the same. Placeholders, to be authored with the user: Murat 5, Ney 6, Lannes 7,
Masséna 8 of ours to their 10; Davout 10, Bernadotte 14. ("Masséna 8" means he attacks only with at least 8 men
for every 10 of theirs; a lower figure is a bolder man.)

**How the odds are reckoned.** They are the game's own battle forecast — the figure the attack card already
shows you — so walls, rivers and ground count. He reckons from what France knows: exactly where the enemy is
fully seen; from the middle of the range where he is partly seen; and **he never attacks what France cannot
see**. No moods. No dice in the choice. The forecast is the game's own and is never recomputed beside it
(golden rule 1): where a second man would join a first (§6.7), his reading is the same forecast with the first
man's force added.

### 6.2 Who can be set on his own

- A **bold** or **careful** marshal whose trust in you is 30 or more.
- **Not a literal man** — he answers: *"Give me my orders to the letter, Sire."* (§7)
- Not the Emperor. Not an ally's or a client's commander. Not a marshal on a task to prove himself (§6.11 — he
  is under exact orders for its three turns). *(Version 5 said "not a marshal who is acting without orders";
  version 6 removes that state.)*
- Artillery marshals: Hold or Support only. (Guns cannot march and fire in one turn.)
- Horse (cavalry) marshals: any task, but a horseman never digs in on his own; his Hold is a screen (§6.7).

### 6.3 What it costs

- **2 actions** to give *(version 6: 1 for a Support task — the game prices every support order at 1)*. A
  just-given order has its own **[Withdraw]** for a full refund until the turn ends.
- **Any change — task, area, risk, an if-then — 1 action, at once.**
- **Asking** is free.
- **Recalling** costs no actions. It costs trust 3 only if you chose it while he was in the middle of a task —
  none when he has asked to be relieved (§6.8: his trust fell under 30, his road was barred, his task ran out).
  The button says which.
- **Today's order to a man on his own** *(version 6)* is an ordinary order — its usual price, his one thing that
  turn, and it may draw an objection or a refusal like any order you give. His task stands and resumes the next
  night, unless today's order took him out of his area (then he asks).
- **His objection is read once, at Give** *(version 6)*: giving or changing his task reads the plain concern of
  the order — the same reading as today's objection, without its mood variance — and the read-back shows it
  before you press. "Give it anyway" costs the objection's usual trust and nothing else: **no refusal is ever
  rolled on his own task** (V2b needs an order you pressed; his task is his own proposal or your change of it).
  **A man never objects to his own proposal** — Masséna proposing a walled Hold with the Archduke near does not
  then object to holding.
- **A man set on his own does nothing the night he is given** (the life table's "Given"); so moving the one
  place in the count from man to man costs 2 actions and a lost night each time — the count cannot be cycled
  for free.

### 6.4 How many — the count

The desk shows **"On their own: n of N"**. It counts marshals **you** set on their own, and nothing else
*(version 6)*. A man on a task to prove himself (§6.11) is under exact orders and is not counted; the jealous
strike is an act, not a state, and is not counted. *(Version 5 counted the trust crisis's three turns without
orders here — "2 of 1" — a state version 6 removes, and the "2 of 1" rule with it.)*

| Step | N | What it is in the game |
|---|---|---|
| The start | **1** | The Emperor writes to one distant man himself |
| The Staff in force | **2** | A third power for a law whose fifth action the project's own measures show going mostly unused |
| A new law, **the Emperor's Aides-de-Camp** (needs the Staff) | **3** | The officers who carried his intentions to far commands |

- **The count limits judgement, not movement.** Exact orders are not counted and never were: an exact order does
  the one thing it names and never chooses.
- "On their own" is a **new kind of law effect**. The laws spec calls that structural and asks for the user's
  ruling; the ruling is the second quote in §1.1.
- **If the Staff lapses** for want of gold, N falls at the turn's refill (the number allowed drops when the
  Staff's gold runs out). The laws' forecast warns a turn ahead,
  so you may recall whom you prefer first; otherwise the lowest-ranked order ends. No trust is lost.
- **Authority never moves N** *(version 6)*. N falls only when the law itself lapses — never with a dip in your
  authority. Low authority bites elsewhere: the Aides-de-Camp, priced in authority, cannot be bought when paying
  would leave you under the purchase floor of 60 (the law's card says so before it refuses), and men grow
  restless sooner (§6.11).
- The courts are not capped: they set no man on his own (§10).

### 6.5 "Tonight" is true

His pass runs first of all when the turn ends, so nothing moves between your last order and his act. The line
says exactly what he will do.

- If his act **shares a target or a road with a higher-ranked marshal's**, the line says so beforehand:
  *"Tonight: Lannes attacks Mack — after Ney; stays put if Ney's fight changes things."*
- **He never improvises.** If the higher man's act has made his own impossible, or worse than his odds, or left
  a fight undecided, **he stays put** — which is the same as waiting, so his if-thens are then checked (at step 5
  of §2, on the board the enemy left).
- If "Tonight" is an attack that **may become a great battle**, the line says "may". Order it yourself to fight
  the day by hand. If you leave it, he fights it his own way — the game's existing "leave it to him" — never in
  silence.
- The one thing he does without it being shown: a shattered corps withdraws, as any corps does.
- **He does not leave his task for distant cannon fire** *(version 6)*. Today a bold man's standing order yields
  to a battle within two provinces (the "cannon_fire" redirect); a man on his own is exempt, and his card says
  so ("he will not leave his task for a battle elsewhere"). His only march to the guns is Lannes's line (§6.7) or
  the arrival roll of §2, step 4 — shown, as "may", never promised.
- **He makes no jealous strike.** The strike skips a man on his own (he has work; §6.10). The code needs a guard
  for it — today nothing in the strike's path reads such a state (IC-V3 is the same hole for the old one).

### 6.6 What comes first

1. **Where he may go** — wherever you could march that corps by hand. The game's own test.
2. **Survival** — a shattered corps withdraws by the game's retreat rule. A last stand stays yours to decide.
3. **Peace** — it ends his order (§6.8).
4. **Today's order.**
5. **His task**, at his risk, in his nature — or, on a turn he waits, his if-thens (checked later, at step 5 of
   §2, on the board the enemy left).
6. **Waiting.** His own way of waiting, by nature and by man (§6.7) — never the same idle act a third night
   running while another sensible one exists. He never drills on his own. *(Version 5: "on a Hold he digs in, up
   to the usual limit" — which set every careful man, and a bold Masséna, digging in night after night.)*

And for the man himself: **a feud beats his personal line; his personal line beats his nature.**

### 6.7 His way — who he is decides what he does

His nature; his own proposal; his way of waiting; his personal line; his recent record; his feuds; his place in
the order of rank — all shown before you give the order.

*Version 6.* The user's word: *"if army has differner personalities they arent all doing same thing every
turn"*. Version 5 made the men differ by one authored number: on one board the bold men came out near-copies,
and every careful man — and a bold Masséna told to hold — dug in night after night (§1.3). Version 6 makes them
differ in seven ways, **none of them dice** (D9 stands).

**1. The bold and the careful.**

| | A bold man | A careful man |
|---|---|---|
| Walls | Storms a garrison if his odds are met | Never storms; besieges (1–2 turns) |
| A beaten enemy leaves his area | Follows one province out — if set to more risk, or if his trust is under 50. You see it first under "Tonight". Out there he fights in the field only: he storms nothing, captures nothing, raises no question, and comes back by the safest road as his next turn's act. | Never |
| An enemy beside his area | Strikes it at his odds, in the field, and comes back as his next turn's act — shown under "Tonight" | Counter-attacks only an enemy he has just beaten off on his area (the decision logic already has this) — but Davout's strike when Iron Resolve is full is his personal line, which beats his nature (point 7) |
| A friend he hates | Will not try to join his battle. The card warns. | The same |
| Objects to being given | A Hold with an enemy near — never his own proposal (§6.3) | Tasks against bad odds or walls |

**His one step outside his area is once per order, in all** — following a beaten enemy out *or* striking a
neighbour, not both — one province (two for Murat, his personal line). A new task is a new order.

**2. His own proposal.** "Give him a task…" opens the line on the task *he* would choose — a pure reading of his
nature, his line and what France sees, never random — with the reason in one sentence:

| Man | He proposes |
|---|---|
| Ney (bold) | Take the nearest enemy-held place in reach, at his odds |
| Murat (bold, horse) | Pursue the weakest enemy army France can see; failing one, take an unwalled place |
| Lannes (bold) | Support the friend nearest a fight (his "to the guns" bears on it); failing one, take beside him |
| Masséna (bold) | Hold his front with its walled place, and strike out from it |
| Davout (careful) | Hold and dig in, and strike when Iron Resolve is full — or besiege the place he can reduce |
| Bernadotte (careful) | Hold in the rear; the line warns he is slow to a fight |
| Any other | By nature: a bold man takes; a careful man holds; artillery holds or supports |
| A literal man — only for a task to prove himself (§6.11) | Hold where he stands, and fall back on his nearest held province if outnumbered |

His nature is shown on the line beside his proposal (IC-10 builds it, with his card's nature where the card
does not yet show it).

**3. His way of waiting.** On a night he does not strike, he does one act from his own short list — each a real
act of the game, shown under "Tonight":
- **A bold man:** probe one province inside his area toward the nearest enemy France can see (never into a
  province where a seen enemy stands; coming back is part of the same act); look — scout the next province,
  revealing what a scout order would and no more; strike an enemy beside his area (above).
- **A careful man:** dig in (up to the usual limit; Davout's stacks); besiege a walled place in his area (1–2
  turns); fall back one province to better ground inside his area; counter-attack a force he has just beaten off.
- **A horseman never digs in:** his Hold is a screen — look, and probe.
- **Nobody drills on his own:** a drilling corps is locked out of the fight, so "Tonight" would promise a man who
  cannot answer.
- **Which of these is still "waiting"** (§2's one thing a turn): digging in and looking are — his if-thens are
  still checked and he may still answer a battle next to him; a probe, a fall-back, a siege or a strike is his
  one thing that night.

**4. The third night.** He does not take the same waiting act a third night running while another sensible act
on his list exists — he will not, say, dig in three nights in a row while there is something else useful to do;
when it is the only sensible one, the line says so ("digs in again — nothing has changed").
A dig-in stops being sensible at the usual limit; Davout's at three stacks. His last nights are a saved record,
read, never drawn.

**5. One man per target.** The pass runs in rank order, and each man's reading leaves out what a higher man has
already taken.
- A second man may share a target only when his own odds are met only with the first beside him: he **joins**,
  and the line says "with Ney" (the forecast with Ney's force added — golden rule 1).
- Otherwise he takes his next target, or his way of waiting; a careful man near a bold lead covers the road or
  the flank.
- A Pursue has one man per enemy army.
- A man who cannot be placed without piling on stays put, and the line says why.

So three bold men in reach of one enemy read as a lead, a join and a third task — not three copies of one
attack.

**6. His recent record — one step, shown.** One step bolder for his next fight after a victory; one step more
careful after a defeat; a bold man three nights without a fight grows impatient — one step bolder until he
fights. However many of these apply — or Ney's own line on reaching an enemy — it is **one step from him**,
added to your one step: never beyond two from his own figure (§6.1). The line names it ("Ney, one step bolder
since his last win, goes in at our 5 to their 10"). It is read from battles and nights already past, so a
question cannot move it.

**7. His personal line.** Where his shipped ability bears on a task on his own, it is his line — Davout's Iron
Resolve (a stack each night dug in, three at most, spent on his next blow). Where it does not, one line is
authored with the user's review, each a tested rule that **never contradicts the ability the game ships**:
- **Murat** follows a beaten enemy two provinces, not one, and never storms walls.
- **Ney**, on reaching an enemy, attacks at once at one step more risk.
- **Lannes**: an enemy fighting a friend within two marches outranks any other target for him (his +15 to the
  guns, made a choice).
- **Masséna** never chooses to give up a walled place short of being shattered.
- **Davout** never chooses to fall back from a Hold he was attacked on (a beaten corps still retreats by the
  battle's rule).
- **Bernadotte** starts a new task one night late, once per order, and the line says so.

A feud beats his personal line; his personal line beats his nature.

**The measure, written now** (R-VARIETY, §13): if the men still read alike — all the men in reach doing the same
act on 40% of turns or more — the written fallback below is built. Otherwise there is no draw of any kind.

**The fallback, only if R-VARIETY is missed: the day's nerve** — the one seeded value this design would ever
allow, fixed before you act and always shown, never a hidden roll. One step, leaning with his nature (a bold man is
steady or bolder; a careful man steady or more careful; it counts inside his one step, §6.1), drawn once at the
start of your turn from the campaign
seed, the turn and his name by the pure hash `campaign_variance._unit` (no stream: a question, an undo or a
reload cannot move it); shown on his line; zero on the historical seed; computed only for men on their own, so
an unused feature changes nothing (R-INERT). Only today's is shown; someone who knows the seed can compute it
ahead, as with the game's other seeded draws. A man set on his own does nothing the night he is given (§6.3), so
no one can shop for a bold day by swapping men.

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

### 6.9 Giving it, the morning, and what he earns

**Giving it — the line, not a form** *(version 6; version 5 had a card with [Give] and [Change])*. "Give him a
task…" on his card opens the command line **already written with his own proposal** — *"Masséna, hold Milan,
and fight at our 8 to their 10 or better."* — with word-chips under it that write into the sentence
(more risk · less risk · until… · if… · and a second province), and the read-back of §8.4 below it: what was
taken, what was not, his answer, the price (2 actions). Enter, or [Give], gives it. Change a word by typing or by
a chip. The read-back names who would take the choice ill, and who could be chosen with nobody minding. Nobody
faces a blank line, and the chips teach the words.

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
most already petitions for a command of his own, once a campaign. "Give him a front" opens the line with his
own proposal. If he cannot be set on his own (his trust, a literal man, the count full), the petition says why
in plain words and offers "He stays with me" — never a dead button. With no place free you may promise it for
two turns.

### 6.10 What he never does

Take land the task did not name. Recruit, build or spend. Plunder — what he takes, he secures. Answer a letter
or a treaty. Make the jealous strike without orders: he has work.

### 6.11 Autonomy you grant, and acts you did not order *(version 6)*

**The rule.** A man is on his own only because you set him so (§6.2: bold or careful, trust 30 or more).
Nothing the game does to a man — at any trust, at any authority — sets him on his own.

**What is removed, with the user's consent** ("even removing it if needed"): the trust crisis's **"Grant
Autonomy"** — three turns in which the man takes no orders and is moved by the enemy's decision logic, with its
moods and dice, after the enemy has moved, never shown beforehand (§1.3). It broke five of this design's rules:
no dice in his choice (D9), "Tonight" is true (§6.5), the order of the turn (§2), the count (§6.4) and the name
(D1); and it had the opposite sign to the user's idea — autonomy forced on a broken man at trust 20, where the
design earns it at 30 and the laws raise it. Its code goes (`TurnManager._process_autonomous_marshals`,
`_end_autonomy`, the debug arm), and with it the player-facing names "Autonomy" and "independent command".

**What takes its place in the audience: a task to prove himself.** When his trust falls to 20 or less the
audience offers, as today, to pay what he is owed (when a debt stands), a quiet post on the staff, or dismissal
— and, where "Grant Autonomy" stood, **"Give him a task to prove himself"**:
- **His** task, proposed by him (§6.7's proposal — he names where he will prove himself), given as an **exact
  order** (§7): the task and one if-then (three for a literal man), shown in full before you give it.
- **Three turns.** He takes no other order meanwhile. "Call him back" ends it at any time; his trust then stays
  where it is. **It costs no action** — it is the audience's answer, as "Grant Autonomy" was.
- **Trust returns by what he achieves** — today's rewards, kept: +40 trust and +10 authority for a spectacular
  result (now *two battles won or a defended place taken*: an empty province proves nothing; a battle he wins
  defending counts — so a careful man holding a threatened province can earn it), +25 for a good one, +15 for
  none, +5 for a poor one.
- **When the three turns end** he comes back to your hand with his new trust and no standing order, and the
  morning says how he did.
- **Always offered**, so the last field marshal is never left with no answer. Not counted (exact orders never
  are). Given only through the audience, so it cannot be bought at will; the audience's five-turn cooldown stands.
- **An old save** with a man in the middle of the three old turns settles his score on loading — the same bands,
  on what he achieved so far — and the first morning says so in one line.

**Acts you did not order — kept, and named apart.** Low authority's real effects stay, because they are the
felt cost of a weak grip ("authority bites", the user's rule):
- **The jealous strike** — a bold, jealous, idle man may attack *without waiting for orders* when the turn ends.
  Low authority (under 30) makes it come sooner. It is warned the night before (TO DECIDE: [Give him an order]
  [Set him on his own]); any order to him clears it; it runs after the on-his-own pass, for men with no order and
  no act this turn.
- **A refused order** — V2b: an order you pressed after he objected may be refused, more often under authority
  50. Never on a man's own task as given (§6.3); today's order to a man on his own is an ordinary order and can be
  refused like any other.
- **The Staff's orders to several** go unheard under authority 50 (§9.1 obeys it).

| On screen | Who chose | Never used for |
|---|---|---|
| on his own · his task · Tonight | you | anything else |
| a task to prove himself | you, at his audience | — |
| attacks without waiting for orders | he did, warned the night before | a man on his own |
| refused your order | he did, when you pressed | a man's own task as given |

The words "autonomy" and "independent command" leave the marshals' screens; "on his own" appears only for a man
you set (today's "may attack on his own when the turn ends" and the report's "He acts on his own for N more
turns" change with it). A census test holds it (§13).

**What a man on his own never does:** the jealous strike; drop his task for distant cannon fire (§6.5); face a
refusal roll on his own task (§6.3).

**The owner of the removal** (golden rule 9): row IC, slice **IC-9** (Session 2) — the audience's new arm built
first, the old arm and its engine deleted in the same commit, old saves settled. Done when the audience offers
no autonomy arm, no French marshal is ever moved by the enemy's decision logic, the words census passes, and an
old save loads settled. STATUS line: *"ROW IC, SESSION 2 — the trust crisis's autonomy replaced by a task to
prove himself"*. Tests: `tests/test_ic9_exact_orders.py` (the trial's arm, the bands, the last marshal, the
old-save settle) and the rewritten `tests/test_autonomy.py`, `test_redemption_v2b.py`,
`test_administrative_role.py`, `test_wo41_redemption_survives_the_save.py` — rewritten, never deleted, so the
audience keeps its cover. **Until IC-9 lands, the game is unchanged** — and there is no conflict to meet in
it: "on his own" is not built before Session 3.

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
- **The line** opens on two or three written presets ("hold, and fall back if outnumbered") as ready sentences
  to take or edit *(version 6: the line, not a card — §8.2)*.
- 1 action to give (a literal man's standing order costs 1 today). *(Version 6: another man's exact order costs
  his standing order's usual price — 2, or 1 for a support order; a task to prove himself costs none.)* Not
  counted. He never objects and is never interrupted mid-order — both as today.
- A hold that carries two or more if-thens counts as real work: he does not grow restless on it. *(Version 6:
  any live exact order will count as work for his restlessness — new: today
  `jealousy.update_literal_hold_counters` counts a Hold with an if-then as sidelined.)*
- **A task to prove himself** (§6.11) is an exact order of this kind for a man of any nature: the task and one
  if-then — three for a literal man.
- **The eight "ifs" and five "thens" are the word table's** (§8.3): one list, generated into the parser.
  Today two of the ifs exist (an enemy, or a named one, comes within reach — `condition_grammar._CONTINGENCY_RE`)
  and two of the answers (fall back on X, attack); the other six ifs and three answers are new, deterministic,
  and read only what his own nation can see.

**Why this gives him a purpose.** A marshal on his own *acts* on your turn, and you see it coming. A literal man
*answers* the enemy the same turn, exactly as written, and never otherwise. He is the one man who will never
surprise you — and the man for whom what you type is exactly what you get. Grouchy on the day of Waterloo heard
the guns and kept to his orders; the blame, as it should, falls on the man who wrote them.

---

## §8 Buttons for simple orders; the typed line for tasks *(rewritten in version 6)*

*The user's word, November 20: "make sure buttons exist for simpler things but typing is used for missions and
excepts a wide array if things". Version 5's text — typing's job was asking and a literal man's lines, and every
act had a card — stands in §8.8 as the record.*

### 8.1 Simple orders are buttons

**Simple** = one marshal (or one group), one verb, at most one place or one enemy, no condition, no time limit,
no risk word — today's one-turn orders, and a bare standing order too (march to a place, hold, chase a seen
enemy, support a friend), carried out as today, exactly. Every simple order is one click, with its price and what
it will do on its face before the press (row PW's rule).

**Built today** (the November 20 inventory): move and march (a click on the map), attack (a click on an enemy,
the province's chip), support (right-click or drag onto a friend), hold, fortify and unfortify, drill, scout
where he stands, fall back, garrison and cancel (the general's seven slots), take, storm or besiege where he
stands, recruit, name and disband an army, the war goal, take back, and the group face's Hold…, Fortify…,
Drill… and a march to a province.

**Missing — built in IC-7, the first slice of Session 2** (filed as **IC-V4**):

| Order | The button | Where |
|---|---|---|
| Chase (pursue) an enemy France can see | "Chase him", beside Attack | the order card for an enemy |
| The one-action stand (defend) | "Stand here · 1 action", beside the Hold slot (2 actions), whose face becomes "Hold the ground · 2 actions" | the general's card — today Hold hides the cheaper stand |
| Scout a named province | "Look at Swabia" | a click on a province he can look into |
| Posture (stance) | a small "Posture" menu | the general's card |
| Form or break square | in the Posture menu, where the game allows it | the general's card |
| Bombard | "Bombard", beside Attack | a gun corps with an enemy France can see in range |
| A glorious charge, or restraint, that you start | "Charge" / "Restrain" | a reckless horseman's card (today only the popup as he is about to charge) |
| Stay put this turn | "Stay put" — free | the general's card: it quiets his "no orders" row for this turn; it is not work for a literal man's restlessness and clears no warning |
| A march's "then …" | a small pick: then hold · then fortify · then drill · then defend (today's four arrival verbs) | the order card (it can already read one) |
| The group's attack, support, fall back, garrison | beside Hold… Fortify… Drill… | the group face — each shows the list first |

The client carries them in **one table, `SIMPLE_ORDER_BUTTONS`** (the pin in `tests/test_ic_review_pins.py`
asks for it), and the Help's Orders page (`codex_view.gd`, which today says the map's clicks "give the same
orders") and the boot help (which presents the card's seven slots as the orders) say what is true. For a man on his own (Session 3): "Ask him", "Change" and "Stand him down" on his card,
each the click twin of a typed verb (§8.6).

### 8.2 A task is typed — and the line is never blank

**A task** = what a man is to carry on with over several turns, when it carries a part no button holds — a
condition, a time limit, a risk word, two places, an if-then — or when he is set to do it on his own (the user's
"missions"; the screen says *task*, because "mission" is the diplomats' word). **The typed line is its road.**

**On his own, or an exact order — the read-back says which.** A typed task to a bold or careful man is *on his
own* when it was opened from "Give him a task…", or the sentence says so ("on your own", "as you see fit", "use
your judgement"), or it carries a risk word (risk exists only for a man on his own). Anything else typed is an
**exact** standing order, carried out as today. The TAKEN row names which ("on his own — 1 of 2" or "exact
order"); with the count full it offers the exact order instead and says why.
- "Give him a task…" on his card, or a TO DECIDE row, opens the line **already written** with his own proposal
  (§6.7) — for a literal man, two or three ready sentences to take or edit.
- **Word-chips** under the line write into the sentence: *more risk · less risk · until… · for N turns · if… ·
  and a second province*. A chip puts its words where they belong; nothing is sent that you cannot read.
- **Tab** and the predictor offer the next word the table allows: a task, a place, how bold, until, if.
- The first task opens with a first-open line and one example (`first_open.py`); the Help gains a page, "What you
  can tell a marshal", with six sentences from §8.3.
- **No separate form.** The chips are the form, and what they build is the sentence: a player who never types
  can still give any task, and one who types learns the words by watching the chips write them.

### 8.3 The word table — what the line takes

**One table, here.** The parser's word lists are generated from it — as the addressee rule's verbs already are
(`tools/gen_routed_order_words`, CX-R1) — so no word is promised that is not read.

| Part | Words it takes | Becomes |
|---|---|---|
| **Who** | a marshal's name (with the typo-forgiveness row PW built) · several names · "everyone" · a named army | one man · a directive (§230) · an army's task (§9.1) |
| **Task** | take · seize · capture · besiege · storm · invest\* — chase · pursue · hunt down · harry · go after · shadow — hold · guard · protect · stand fast · stand firm · keep\* — support · join · back up · follow (a friend) · cover (a friend) · stay with\* | one of the four standing orders — never a fifth task (D11). *\* new words; the rest are read today (`strategic_parser.STRATEGIC_KEYWORDS`; take, seize, capture, besiege and storm as today's take order where he stands — as a standing task, Take is new). "Defend" stays the one-action stand, never a hold word.* |
| **Where** | one province · two provinces for a hold ("Munich and Franconia") · "the war goal" | the place; a two-province Hold is one area |
| **Whom** | an enemy marshal France can see · a friend by name | the target. An unseen enemy and a name that does not exist get the **same** answer — no free look through the fog |
| **How bold** | boldly · aggressively · press hard — carefully · cautiously · only at good odds · don't risk the army — "at any cost" | one step either way of *his own* odds, shown as numbers; "at any cost" is one step bolder, and a careful man states his objection |
| **How long** | for N turns · until turn N · until X arrives · until relieved · until the battle is won · until X is destroyed | today's six condition clauses — five "until" forms and "for N turns" (`condition_grammar._READ_CLAUSES`) |
| **If … then** | if (an enemy / a named enemy) comes within reach · he is attacked · he is outnumbered · he is being surrounded · (a friend) is attacked next to him · (a place) falls · (a friend) arrives — then attack · fall back on X · march to X · join his battle · dig in. "When", "should" and "in case" read as "if" | the if-thens of §6.1 and §7: two for a man on his own (checked only on a night he waits), three for a literal man's exact orders, one for anyone else's exact order (today's rule); one attack line at most |
| **Then** | after a march: then hold · then fortify · then drill · then defend; "then dig in" reads as fortify (new) | today's arrival verbs (`strategic_parser.ARRIVAL_VERBS`) |
| **Ask** | what will you do · what do you see · why did you … · can you take X · how strong is X | free; the same reading as "Tonight"; it reads only what France can see |
| **Change** | more risk · less risk · take X instead · add or drop an if-then · stand down | §6.3's prices |

**What the line refuses — free, with the nearest real sentence already written in:**
- a second task in one sentence ("first take Swabia, then support Soult") → *"One task at a time. 'Murat, take
  Swabia' — he will ask for the next when it is done."*
- a river line or a stretch ("the line of the Inn", "between Munich and Vienna") → *"Name one or two provinces:
  'Davout, hold Munich and Franconia'."*
- "their main army" → *"Name its commander."*
- seasons, weeks, "as long as it takes" → *"Say 'for N turns' or 'until turn N'."*
- "unless …" → offered back as the if-then it means: *"Did you mean: if Mack advances, fall back on Lorraine?"*
- anything §6.10 forbids (recruit, build, spend, a treaty) — and diplomacy, which is never typed.
- a name that could mean two things (two men, a man or a place) → one question with a button for each reading,
  nothing spent — the road row PW built for "did you mean Ney?".

**Examples** — each is built today, or the slice that builds it is named:

| Sentence | Becomes | Lands |
|---|---|---|
| "Davout, hold Franconia." | Hold | today |
| "Davout, hold Franconia for three turns." | Hold, for 3 turns | today |
| "Davout, hold Franconia until Ney arrives." | Hold, until he arrives | today (the read-back shows the condition: IC-8) |
| "Davout, when Ney arrives, hold Lorraine." | Hold now, ending when he arrives | today |
| "Murat, chase Mack until he is destroyed." | Pursue, until destroyed | today |
| "Soult, follow Ney." | Support | today |
| "Ney, march to Lorraine, then fortify." | March, then fortify | today |
| "Ney, if Mack advances, fall back to Lorraine." | Hold with one if-then | today |
| "Ney, retreat if outnumbered." | *Taken:* fall back now · *Not taken:* "if outnumbered" — *"give it as a hold with an if-then?"* | IC-8 (today he retreats and the "if" is dropped without a word: IC-V1) |
| "Soult, hold Lorraine. If attacked, dig in. If outnumbered, fall back on Champagne." | three if-thens | IC-9 |
| "Soult, hold. If Ney is attacked next to you, join his battle." | the arrival roll, as an if-then | IC-9 |
| "Davout, hold Franconia. If Munich falls, march to Munich." | a named place falls | IC-9 |
| "Masséna, hold Milan and Piedmont, carefully." | a two-province area, one step less risk | IC-10 |
| "Ney, take Swabia boldly." | on his own, one step more risk | IC-10 |
| "Davout, take the war goal." | on his own, toward the goal | IC-12 |
| "Army of Italy, hold Milan." | an army's task (§9.1) | IC-12 |
| "Masséna, what will you do?" | free | IC-10 |
| "Masséna, stand down." | recall, free | IC-10 |

### 8.4 The read-back — four rows, before anything is spent

1. **Taken** — the task, the place, how bold (as numbers: his own odds, your step, his recent record), how long,
   each if-then.
2. **Not taken** — every part that would change what he does (a condition, an if-then, a second task, a risk
   word), quoted, with the plain reason. While one stands, Give reads **"Send what I understood"** and sends the
   line restated without it, at that order's own price — shown, so you see exactly what goes (a refusal itself
   costs nothing). Filler ("and report", "please") is a quiet note and blocks nothing.
3. **His answer** — one line in his own voice, from the same reading as "Tonight" (a man on his own) or as his
   exact order.
4. **Price** — actions; his objection, if he has one (§6.3); what it replaces; who would take it ill.

**One reader** serves the read-back, the line and the executor (`parse_preview.read_one`, as directives already
do), so what you read is what is done. Built today: the price and some riders. New: the condition, the if-then
and the "not taken" row (IC-V2).

### 8.5 With and without a language model

The parts are fixed lists, so the built-in parser reads the whole table with no key. With a key, the model only
maps freer wording onto the same parts — the task, the place, how bold. It never writes a condition, an if-then
or a number, writes no reply and decides nothing (golden rule 6); the parser re-reads conditions from the text
every time. **WS-12** — today a live parse's own score moves morale, trust and attack — is fixed first, as ruled
November 17: the model's number moves nothing.

### 8.6 Talking to a man on his own

The names of marshals on their own, or under exact orders, sit by the command line. Click one: the line begins
"Masséna, " with ready things to say.

| You want to | You say, for example | What you pay |
|---|---|---|
| **Ask** | "what will you do?" · "what do you see?" · "why did you fall back?" · "can you take Tyrol?" | Nothing. It is the same reading his act will use, and asking changes nothing in the game. |
| **Change** | "Masséna, more risk" · "take Tyrol instead" · "if outnumbered, fall back on Milan" | 1 action, at once |
| **Today's order** | Any ordinary order. The read-back offers "make it his new task" beside "send". | Its usual price. It is his one thing this turn. |
| **Recall** | "Masséna, stand down" | No actions (§6.3) |
| **Give** | "Davout, hold Munich and Franconia on your own, carefully" | 2 actions (1 for a Support task) |
| **Exact orders** | "Soult, hold Lorraine. If an enemy comes within reach, attack. If outnumbered, fall back on Champagne." | 1 action (a literal man; another man's exact order costs his standing order's price) |

### 8.7 What lands on the way — Session 2's head

The read-back's promise depends on the typed road's open defects, so they move from Session H's head to IC-8:
**UI6-X70, X73, X74, X75** (a long typed order quietly drops a part), **WS-14** (the read-back's standing
question), **WS-12** with **GRD-33**, and the two this review found — **IC-V1** (a one-word condition slips
under the two-word floor) and **IC-V2** (the read-back shows no condition).

### 8.8 What typing is for — the record

Version 5, after three rounds of panels that marked typing between 4 and 7: *"asking a marshal a question is a
real job for the typed line; writing a literal man's three lines in one sentence is a natural one; nearly
everything else is a quicker way to do what a card already does. Every act has a card. Diplomacy is never
typed."* Version 6: the user's ruling gives the line its second real job — **tasks** — and asks that it take a
wide array of things; every simple order keeps its button; asking stays free; diplomacy is still never typed.

---

## §9 The war goal

- **One place a war aims at** ("Vienna"). Free to name. It shows on THE WAR line and as a gilt ring on the map.
  *(Built: directives, §230.)*
- A task **"take the war goal"** follows it. Changing the goal costs 1 action for each man serving it.
- **Two marshals as one force** need no new rule: one leads, and the other is set to Support him. A higher man
  supporting a lower one takes it ill, as today, and the card says so before you give the order.

### 9.1 An army's task — the men of one army take different parts *(version 6)*

The user's word: *"if army has differner personalities they arent all doing same thing every turn"*. A named
army (built: §230) given a **task** — "Army of Italy, hold Milan", "Army of the Rhine, take Swabia" — is read
as two marshals as one force, writ large; no new rule:
- **Its commander** — the army's named commander, else its senior man who may be set on his own (bold or
  careful, trust 30 or more; artillery only for a Hold or a Support) — is set **on his own** with the task. If no
  man of the army qualifies, the list says so and offers the task as exact orders, uncounted. A supporter who is
  already on his own keeps his own task and his place in the count ("on his own — not included").
  He takes the one place in the count; if the count is full, the list says so and offers to recall someone,
  and nothing is given.
- **Every other man is set to Support him** — today's standing support, not counted, 1 action each. Each man's
  row shows his own part as the game already decides it: his odds of joining a fight (Lannes +15 "to the guns",
  Bernadotte −15, a bold man +5, a careful man −5), and a literal man's exact line ("if Masséna is attacked next
  to you, join his battle").
- **One list before anything is spent** — the user's ruling "One list for all": each man's row, its price, who
  is over the count, who will take it ill; Give sends it as one; Take back undoes it as one.
- The commander then acts by §6.7 (his proposal, his way, his record); the supporters keep their own natures in
  every battle near him. So the army's men do different things — one leads, a bold man hurries to his fights, a
  careful man keeps his distance, a literal man answers to the letter — and nobody improvises.
- **Directives stay what they are** (§230) — a directive is today's order sent to several men at once, the same
  order for each — today's order to several is one order, the same for each man, as
  built. A directive never silently overrides a man on his own — his row says "on his own — not included", with
  a press to include him.
- The Staff's orders to several go unheard below authority 50 (`group_orders.py`); an army's task obeys the same
  rule and says so before Give.

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

- Learn a literal man's lines, and do the thing they do not cover. That is Ulm (the 1805 manoeuvre, not a
  province) — on the seed that draws it.
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

### 10.6 Different men on the other side too *(version 6 — the sibling the review filed)*

The user's "different personalities … not all doing the same thing" holds for the enemy as well, and today it
does not: an enemy marshal's thresholds are per nature, his skills and ability play no part in his court's
choices, and his daily mood is **one stream per nation**, drawn in call order — so it is noise, not character,
and it shifts with how many corps were weighed before him (§1.3). The fix — each enemy man's mood keyed by the
campaign seed, the turn and his name (`campaign_variance._unit`, no stream), leaning with his nature — **changes
the old game**, so it is not folded in quietly: it is an **arm of Session 4's measure** (IC-14), behind its own
switch, with its own before-and-after sweep (the band, the story classes, the AI-France harness), and it is
adopted only on that session's gate with the user's word. The byte-identity series runs with it down.

---

## §11 The voice, and the first turn

**The voice.** Named lines for seven French marshals in battle, acknowledgement and completion lines by nature,
and petition and jealousy lines all exist (`marshal_voice.py`). None is replaced. What is written new:

| Moment | Who gets lines |
|---|---|
| His proposal on the line (the read-back's "his answer"); accepting | each of the seven by name; by nature for the rest |
| His morning line: he struck · he waited · he stayed put · he asks · the task is done | each of the seven by name; by nature for the rest |
| His way of waiting, the third night's change, his recent record ("bolder since his last win") *(version 6)* | by nature, with named lines for the seven |
| Asking for a task to prove himself; its end, by result *(version 6)* | by nature, with named lines for the seven |
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
- **The lesson is not cut.** Two cards are added near its end: setting a man on his own (by the line, with its
  chips), and asking a question.
- **Two first-open lines** join the eleven: the first time TO DECIDE is shown, and the first time the line opens
  for a task *(version 6: the line, not a card)*.
- **The real campaign teaches itself**: TO DECIDE is worked out from the board, so on turn one it already says
  "Mack stands in Swabia…".

---

## §12 Rulings on edge cases

*Every one of these came from a panel's finding, or from the reads of the code. The full ledgers are in
`docs/audits/ic_focus_groups/`.*

**Giving the order**

| Case | Ruling |
|---|---|
| The count is full | The read-back says so and offers to recall another man. A place freed is usable next turn. |
| A task against his nature | He objects, with today's answers. "Trust his judgement" takes his counter-proposal. *(Version 6: read once at Give, no dice; "give it anyway" costs the objection's trust — §6.3.)* |
| At peace | Only Hold and Support can be given. Take and Pursue belong to a named war. |
| He is broken, wounded or besieging | He can be given an order; it starts when he is fit. |
| Bernadotte set to Support a man | His ability makes him slow to the guns; the card says so, so you know what the order will and will not deliver. |
| A man is set to Support one he hates | Refused at the card, with the reason. |
| The Emperor | Cannot be supported by a man on his own, and cannot be set on his own. |
| ~~A man acting without orders~~ | ~~Cannot be given an order on his own until that ends.~~ *Version 6: that state is removed (§6.11).* |
| A man on a task to prove himself | Cannot be set on his own until it ends; "Call him back" ends it, and his trust stays where it is. |
| A typed task with a part the line cannot read | The read-back's "not taken" row quotes it; Give becomes "Send what I understood" and sends the restated line (§8.4). |
| A typed task naming an enemy France cannot see | The same answer as a name that does not exist — no free look through the fog. |
| Two tasks in one sentence | Refused free: "one task at a time", the first already written in. |
| "Boldly" to a careful man; "at any cost" | One step bolder at most; the careful man states his objection (§6.3). Never two steps from his own odds with his record added. |
| The petition from a man who cannot be set on his own | The petition says why in plain words and offers "He stays with me" — never a dead button. |
| Swapping the one place from man to man | 2 actions and a lost night each time: a man set on his own does nothing the night he is given. |

**Each turn**

| Case | Ruling |
|---|---|
| Two men after the same enemy | The higher acts first. The lower joins only if he needs the higher man to meet his own odds ("with Ney"); otherwise he takes his next target or his way of waiting (§6.7). If he joins, his line says "with Ney; stays put if Ney's fight changes things". |
| The same idle act a third night | Not while another sensible act on his list exists; when none does, the line says "again — nothing has changed" (§6.7). |
| Cannon fire within two provinces of a bold man on his own | He does not leave his task (§6.5); his card said so. |
| A jealous strike and his act aim at one enemy | His pass runs first; the strike is re-read on the board he left, and rank settles a shared target. |
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
| A bold man strikes an enemy beside his area | The same rules as the follow-out, and it is the same once-per-order step outside his area (§6.7). The battle runs through the game's whole post-battle road — glory, the jealousy it stirs, trust, the report — as any attack does. |
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
| ~~A man goes out of hand while the count is full~~ | ~~"2 of 1"…~~ *Version 6: no such state; the count counts only men you set (§6.4).* |
| A man on a task to prove himself while the count is full | Not counted: exact orders never are. The count is unchanged. |
| An army's task when the count is full | The list says so and offers to recall someone; nothing is given until a place is free (§9.1). |
| A directive to an army that holds a man on his own | His row reads "on his own — not included", with a press to include him; a directive never overrides him silently. |
| Your authority dips | N does not move. Only the law's own lapse moves N (§6.4). |
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
| Saves | The order, its if-thens, used lines, the ring's centre, siege progress, the unseen-turns count, the stepped-out mark, a promised petition; for the enemy, the plan, its step and the favoured province; for France, what was learned and when. *Version 6 adds:* the risk step; his recent record (last battle's result, quiet nights); the record of his last waiting acts; a task to prove himself (its task, turns left, its score). The day's nerve, if R-VARIETY ever builds it, is **never saved** — it is worked out from saved fields. Every new field: `to_dict`/`from_dict` with `.get` defaults, `SAVE_FORMAT_REFERENCE.md`, the enforcement test, and the take-back's `ORDER_KEYS` decided field by field (an undo of a give restores the count and the actions; it never gives back a night already spent). |
| Old saves | They have none of this. A war already running draws its plan on load. *Version 6:* a man saved in the middle of the old three turns loads settled (§6.11). |

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
| The step outside his area | one province (two for Murat, his personal line), once per order — following out or striking a neighbour, not both | R-TRUE: it is on the card and under "Tonight" |
| If-thens: on his own / literal / other exact orders | 2 / 3 / 1 | R-READ |
| The floor that trips nothing | a fifth of his strength | The measure's probes |
| The Pursue ring | three marches | R-FUN |
| Captured orders stay good | until the next step, two turns at most | R-HILL |
| TO DECIDE rows | 3 | R-READ |
| *Version 6:* his recent record — after a win / after a defeat / a bold man's quiet nights | one step bolder / one step more careful / impatient after 3 | R-VARIETY and R-BAND |
| The most steps from his own odds — one from you (word or chip) + one from him (record, impatience, Ney's line, or the nerve if built; never more than one together) | 2 | R-READ (the read-back shows all three numbers) |
| The same idle act, nights running, before he must change it | 3 (never a third while another sensible act exists) | R-VARIETY |
| A task to prove himself: turns; the bands | 3; +40 trust and +10 authority / +25 / +15 / +5 (today's) | kept from today; "spectacular" = two battles won or a defended place taken |
| The day's nerve (only if R-VARIETY is missed) | one step; a bold man bolder three days in ten, a careful man more careful three in ten | R-VARIETY's own arm |

**The rules:**

- **R-INERT.** Two switches guard the old game. With the player's side unused and the enemy's side off, every
  committed measure reproduces byte for byte. **A purity test**: run every question and every preview, then
  check that no key outside the game's existing inert list was written and no draw was taken from the global
  random stream. The promise "a reload changes nothing" is made for seeded campaigns; the historical campaign's
  battle dice are not reload-stable today, and this design does not change that. *Version 6:* the one
  deliberate exception is the trust crisis's audience (IC-9): a commanded run whose playtest driver answers an
  audience with today's default, "Grant Autonomy", will answer it with the task to prove himself, so those runs
  move — Session 2 re-reads the France band and says per seed which moved and why. Everything else reproduces.
- **R-VARIETY** *(version 6, written before any data)*. On 30 seeds × 20 turns, with three bold men and two
  careful men on their own on the 1805 board: (1) all the men in reach of an enemy do the same act on **fewer than
  40%** of the turns they are all in reach; (2) **no man** takes the same waiting act a third night running while
  another sensible act existed (zero cases — a test, not a rate); (3) over 20 turns every man shows **at least two
  kinds** of act. If (1) or (3) is missed with §6.7's seven ways, the day's nerve (§6.7) is built as the arm, and
  kept only if the bar is then met with it and R-BAND still holds; the user is told which happened.
- **The words census** *(version 6)*. A test reads every player-facing string of the marshals' screens: "autonomy"
  and "independent command" appear on none; "on his own" appears only for a man you set; the jealous strike says
  "without waiting for orders"; V2b says "refused your order" (the vassals' autonomy scale is exempt by name).
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
  - *Version 6 — the buttons and the line:* "How would you make Murat chase Mack without typing?" · "You typed
    'Ney, retreat if outnumbered' — what will happen?" · "Why does Davout do something different tonight from
    Ney?"
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
| *v6:* The buttons | `marshal_state.gd` (`SLOTS`, `order_specs`), `selection_card.gd` (the group face), `region_panel.gd` (chips), `order_confirm_card.gd`, `order_quotes.py` (each kind's price and words), the verbs in `validation.VALID_ACTIONS` | One table `SIMPLE_ORDER_BUTTONS`; the backend quotes the new kinds (pursue, defend, stance, square, bombard, scout-a-place, charge, wait) through the same quote road; the Help's Orders page (`codex_view.gd`) and the boot help made true |
| *v6:* The line and the read-back | `parse_preview.read_one` and `_order_reading`; `condition_grammar.describe_condition` / `describe_contingency` (pure); `unread_condition_clauses`; the clause guard's two-word floor (`clause_guards.py`, counted after the marker — IC-V1); `strip_condition_clauses`; `directive.quote` | The four rows; "Send what I understood" sends the restated line; one reader for read-back, line and executor |
| *v6:* The word table | `strategic_parser.STRATEGIC_KEYWORDS`; `condition_grammar._READ_CLAUSES`, `_CONTINGENCY_RE`; `reading.py` (filler words); the predictor | One table in `backend/ai/`, its word lists generated into the parser like `tools/gen_routed_order_words` (CX-R1) with a census test; the golden corpus gains a row per part |
| *v6:* The chips and the filled line | `main.gd` (the command line, Tab ideas), `marshal_chip_row.gd` | "Give him a task…" fills the line with his proposal; the chips write into it |
| *v6:* The men | the forecast (`combat_executor.muster_odds`); Iron Resolve (`marshal.py`); the battle record (the campaign log / the jealousy book); `campaign_variance._unit` (only for the fallback) | His proposal, his way of waiting, the third-night record, one man per target, his recent record — all inside the one pure reading |
| *v6:* The audience | `disobedience._get_available_redemption_options`, `handle_redemption_response`; `TurnManager._process_autonomous_marshals`, `_end_autonomy`; the executor's "acting independently" block; `marshal.autonomous`, `autonomy_turns`, `autonomy_reason` and the `autonomous_*` counters; `redemption_dialog.gd`; `main.gd`'s "AUTONOMY GRANTED"; `while_you_waited._own_way`; the playtest driver's default answer | The trial's arm (an exact order, his proposal, three turns, the bands); the old arm, its engine and its words deleted in the same commit; the fields kept only to settle an old save on load |
| *v6:* The exemptions | `strategic._check_interrupts` ("cannon_fire"); `jealousy`'s warning pass and `process_autonomous_attacks`; `jealousy.update_literal_hold_counters` | A man on his own skips the redirect and the strike; a live exact order counts as engaged |

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
  depends on it. The builder reads them all before any personal line is written. *(Version 6: read November 20
  — Ney +2 shock when attacking; Murat +5,000 pursuit losses; Masséna +10% defence when outnumbered; Soult a
  one-turn drill that never locks him out; Napoleon +10% attack and defence to every French corps fighting in his
  province, and enemies decline odds against him they would take against a marshal. Of the six men
  who can be on their own, only Davout's bears on a task as it stands; the other lines of §6.7 are authored.)*
- *Version 6:* renaming the jealous strike's words moves pinned text (`test_jealousy_v32.py`,
  `test_pt_f_jealousy_channel.py`, `test_wo_slice17_frontier_halts_the_charge.py`) — budget the re-pins with the
  census test, never bypass them.
- *Version 6:* the trial's arm replaces the playtest driver's default audience answer; the France band is re-read
  in the same session (R-INERT's one exception).
- *Version 6 — golden rule 8:* "Tonight", the proposals, the ways of waiting and the one-man-per-target pass read
  cached helpers (`get_nation_regions`, adjacency, the forecast's own caches) — never a scan of every region per
  man per turn; each is worked out once per state and kept, as the desk's reach is (`threats.py`, keyed to the
  world by a weak reference — the directives' trap).

---

## §15 The build — Session 1 built; Sessions 2–4 re-cut by version 6

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

### The rest of the row — re-cut by version 6 (November 20, 2026)

*Version 5's tables for Sessions 2–4 (IC-7 … IC-14: on his own and talking; exact orders, the war goal and the
voice; the other side of the hill) are re-cut so that what everything else stands on lands first: the buttons
and the line before judgement, exact orders before the audience's trial can replace "Grant Autonomy", and that
replacement before "on his own" exists — so the shipped game never holds both. Nothing is dropped; the slices
are renumbered IC-7 … IC-15.*

### Session 2 — Buttons for orders, the line for tasks, exact orders (nothing yet chooses for itself)

| Slice | What | Done when | Tests |
|---|---|---|---|
| **IC-7** | The buttons (§8.1): chase, the one-action stand, scout a named province, posture, square, bombard, a charge or restraint you start, stay put, a march's "then", the group's attack, support, fall back and garrison; `SIMPLE_ORDER_BUTTONS`; the Help's Orders page and the boot help made true | Every order of §8.1 is one click with its price on its face, pressed in the real client at the user's setup; IC-V4 closed | `tests/test_ic7_the_buttons.py`; driven `TestRowIC7TheButtons`; the pin `TestICV4…` promoted |
| **IC-8** | The line for tasks (§8.2–§8.5): the word table and its generated lists, the chips, the filled line, the read-back's four rows, the refusals with the nearest sentence; first, the typed road's open defects — UI6-X70, X73, X74, X75, WS-14, WS-12 with GRD-33, IC-V1, IC-V2 | Every "today" and "IC-8" line of §8.3's examples reads back as written, with no key; nothing is spent before Give; a part that changes what he does is never dropped in silence | `tests/test_ic8_the_line.py`; the golden corpus (a row per part); the pins of the rows it closes promoted |
| **IC-9** | Exact orders (§7): three if-thens for a literal man, one for the others, the six new ifs and three new answers, each used once, the renew row; **the audience's task to prove himself** replacing "Grant Autonomy" — the old arm, its engine and its words deleted in the same commit, old saves settled; IC-V3 closed with the engine | §7's rules hold on every if-then; the audience offers no autonomy arm; no French marshal is ever moved by the enemy's decision logic; the words census passes | `tests/test_ic9_exact_orders.py`; the rewritten `test_autonomy.py`, `test_redemption_v2b.py`, `test_administrative_role.py`, `test_wo41_redemption_survives_the_save.py` |

Measure: R-INERT on every arm but the audience's (the France band re-read with the driver's new answer, per seed);
R-READ for the buttons and the line (§13's version-6 questions). STATUS line: *"ROW IC, SESSION 2 — BUTTONS FOR
ORDERS, THE LINE FOR TASKS, EXACT ORDERS"*.

### Session 3 — On his own

| Slice | What | Done when | Tests |
|---|---|---|---|
| **IC-10** | The order, the pure reading, the pass, "Tonight", the count and its law, giving it by the line (his proposal, the risk step), the morning block; the exemptions (cannon fire, the jealous strike); the petition's button; the desk row's two buttons | "Tonight" equals the act on every path of the life table; the count holds; the Staff raises it; a man on his own never strikes or redirects | `tests/test_ic10_on_his_own.py` (each task; each state and its way out; one thing a turn; the purity test; the count; serialization); driven `TestRowIC10InTheClient` |
| **IC-11** | The men (§6.7): proposals, ways of waiting, the third night, one man per target, the recent record, the personal lines; R-VARIETY and, only if it is missed, the day's nerve | R-VARIETY met (per seed, said either way) | `tests/test_ic11_different_men.py` |
| **IC-12** | An army's task (§9.1); "take the war goal" | An army's task is one list, its commander on his own and the rest supporting; changing the goal turns every man who serves it, at its price | `tests/test_ic12_an_armys_task.py` |

Measure: one sweep with arms — as today; N 1; N 2 at the start; N by the ladder — on the three commanded seeds.
R-INERT, R-TRUE, R-BAND, R-FUN, R-VARIETY; R-READ for "on his own". STATUS line: *"ROW IC, SESSION 3 — ON HIS
OWN"*.

### Session 4 — The voice, and the other side of the hill

| Slice | What | Done when | Tests |
|---|---|---|---|
| **IC-13** | The voice: the new lines (§11), "said lately", the portrait, `docs/MARSHAL_VOICE_BIBLE.md`, rule 11's wording, the lesson's two cards, the two first-open lines | No line twice in a man's last three; three readers tell two marshals apart from their lines alone | `tests/test_ic13_every_man_his_own_line.py` |
| **IC-14** | War plans; enemy literal marshals under exact orders; the enemy's per-man mood as an arm (§10.6) | Each court at war draws a plan; a planned literal marshal has one master; his if-thens read his own nation's sight; the mood arm adopted only on its gate | `tests/test_ic14_the_war_plan.py`; a fog census pin for every enemy if-then |
| **IC-15** | Natures public; the spy's report; captured orders; the hunt, as an arm; the closing measure and readings; the records | Nothing is shown that was not learned; every rule of §13 is met on the final tree, or the report says which was not | `tests/test_ic15_what_you_learn.py` |

STATUS line: *"ROW IC, SESSION 4 — THE VOICE AND THE OTHER SIDE OF THE HILL — ROW IC COMPLETE"*.

**Where the row sits against the deploy.** All three sessions run before the deploy session (Session H) — the
pattern of rows BA, OC and PW, and the user's standing rule that content is not cut or pushed back to protect a
date. *Version 6: until November 20 no record had homed them (the STATUS line said only "later sessions of the
row"); they are now a row of `PRE_DEPLOY_PLAN.md` §2, and `docs/NEXT_SESSION_PROMPT.md` opens Session 2.* This
is sizing, not pressure: about three sessions. One line to reverse.

---

## §16 Decisions taken (each is one line to reverse; strike any)

| # | Decision | Why |
|---|---|---|
| D1 | The feature is called **on his own**; ~~the game's "independent command" stays the name of the three turns without orders~~ *v6: the three turns are removed, and "autonomy" and "independent command" leave the marshals' screens; the words table of §0 keeps every phrase to one meaning* | "Mission" and "a free hand" mean something else in diplomacy; the panels asked for one plain phrase |
| D2 | A literal man **cannot** be set on his own; he gets **exact orders** | The user's "this gives literal a purpose" |
| D3 | The count limits **judgement only**; exact orders are not counted | An exact order never chooses; counting them would cap the ordinary marches the game has today |
| D4 | The courts set no man on his own | They are not short of actions; forcing it made them worse (§17) |
| D5 | N is 1, 2 (the Staff), 3 (a new law) | Placeholders; "2 at the start" is measured |
| D6 | **He acts first when you end the turn**, before the enemy moves | So that "Tonight" is true; no side gets the last word |
| D7 | **One thing a turn**, for every marshal with a standing order | It is the price of handing off, and it closes every double act the panels found |
| D8 | He never improvises: what the screen said, or he stays put | "Show before, never surprise" |
| D9 | No moods and no dice in his choice; each marshal's own odds are authored. *v6: what varies is drawn from who he is and what has happened — his proposal, his way of waiting, the third night, one man per target, his recent record — all shown before you end the turn. The one possible exception, only if R-VARIETY is missed, is the day's nerve: a seeded value fixed before you act and always shown — never a hidden roll* | So the card's sentence is true, and the men differ |
| D10 | He reckons from what France knows, and never attacks what France cannot see | So a free question cannot probe the fog |
| D11 | Four tasks — the four standing orders the game has. *v6: a typed task is one of the four with its parts — never a fifth* | One new idea, not five |
| D12 | He secures what he takes; no plunder switch | Fewer rules; plunder stays the player's own choice by hand |
| D13 | Any change costs 1 action, at once | One price; no hidden pending state |
| D14 | Each if-then is used once; a literal man has three, of which one may be an attack | A bound that needs no count |
| D15 | A marshal's personal line is his shipped ability. *v6: where it does not bear on a task (all but Davout's), one line is authored, never contradicting it (§6.7)* | The game already made the men different; nothing is contradicted |
| D16 | The enemy keeps its hand and gains a war plan with steps | Readable, varied, and inert when switched off |
| D17 | Natures are public | Reputations were; it gives the player a read from turn one |
| D18 | No false orders, ever | The project's standing principle: a surprise is never a lie |
| D19 | The hunt is a measured option | A claim the code did not support becomes a rule tested before it is kept |
| D20 | The desk's three lines sit at the head of the command desk *(built on their own card at the map's corner — §15's landing record)* | It reflows in every form and keeps the map clear |
| D21 | Marshals' quoted lines may keep the period voice; plain words ride beside | It is what the existing lines already do |
| D22 | The lesson is not cut; two cards are added | Nothing is cut without the user's word |
| D23 | Four sessions, all before the deploy. *v6: the three left, re-cut, homed in `PRE_DEPLOY_PLAN.md` §2 before Session H* | The same standing rule; every panel said to stage it |
| **D24** *(v6)* | **"Grant Autonomy" is removed**; the audience's arm becomes a task to prove himself — his proposal, under exact orders, three turns, today's rewards | The user's consent ("even removing it if needed"); it broke five rules and had the opposite sign to an autonomy that is earned (§6.11) |
| **D25** *(v6)* | Every simple order is a button; a task is a typed sentence, the line opening filled with his proposal, word-chips writing into it — no separate form | The user's ruling (§1.1); nobody faces a blank line, and the chips teach the words |
| **D26** *(v6)* | One word table generates the parser's words for tasks; outside it, refused free with the nearest real sentence | "A wide array" kept honest: no word is promised that is not read |
| **D27** *(v6)* | The read-back's four rows; a part that would change what he does blocks Give until you choose "Send what I understood" | "Show before, never surprise"; filler never blocks |
| **D28** *(v6)* | Men differ in seven ways, none of them dice (§6.7) | The user's "not all doing the same thing every turn"; the adversaries' "earned, not seeded" |
| **D29** *(v6)* | An army's task: its commander on his own, the rest supporting by today's rules; directives stay uniform | No new decision system; the men keep their natures in every fight |
| **D30** *(v6)* | A man on his own is exempt from the cannon-fire redirect and the jealous strike, and faces no refusal roll | Otherwise "Tonight" is false or dice decide his obedience |
| **D31** *(v6)* | Authority never moves the count; low authority bites as restlessness, refusal and the purchase floor | Autonomy is only ever given (§0) |

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
| *v6:* **"Grant Autonomy"** — the trust crisis's three turns on the enemy's AI (shipped content, removed by the user's consent) | §6.11: hidden dice, after the enemy moved, never shown, counted against the earned count, the opposite sign of the feature. Its rewards are kept in the task to prove himself. |
| *v6:* **The card with [Give] and [Change]** for a task | The user's ruling: tasks are typed. The chips under the filled line do the card's job and teach the words. |
| *v6 (panels' proposals, not adopted):* **"Stand him down"** as the audience's new arm (P1) | A free trust farm with nothing to do; the task to prove himself keeps the deed and the reward. |
| *v6 (panels' proposals):* **A daily seeded temper as the default** (P3) | Both adversaries: count-shopping and "personality is character, not situation". Kept only as R-VARIETY's fallback. |
| *v6 (panels' proposals):* **Fixed risk floors (12 / 8 / 6 to 10) and "at any cost" as no floor** (P2) | They overrode a man's own odds by a word; a word moves one step, no more. |
| *v6 (panels' proposals):* **Two-step tasks, named river lines, "their main army"** (P2) | A second act, new scenario data, or a fog hazard; refused free with the nearest sentence. |
| *v6 (panels' proposals):* **A skill term added to his odds** (R4) | Counts skills twice (the forecast has them) and hides a calculation; the authored figure is his boldness. |

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
- *v6:* **A separate form for tasks.** The chips write the sentence; a second road would make typing a shortcut
  for a card again, which the user's ruling undoes.
- *v6:* **Two tasks in one sentence, river lines, "between X and Y", "their main army", seasons.** Each is
  refused free, with the nearest real sentence written in (§8.3); none is promised.

**Recommended, not in this design** — offered because the user has said expansions are welcome; each would need
his word and its own gate:

- **A price for distance.** An order changed more than three marches from the Emperor costs 2 actions, not 1,
  and the button says so. It gives "you cannot be everywhere" teeth with no waiting. Raised by historians in all
  three rounds.
- **A pinning rule in combat**, so that "pin him" could be a real task.
- **A second line of character** for the marshals (discipline beside daring). *v6: CLOSED — §6.7 makes the men
  differ without a new axis.*

*v6:* the first two stay offered, not promised — no slice, no screen and no help text mentions them.

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

### 19.4 The review of November 20, 2026 (version 6)

**Why.** The user's words (the status block); and the plain fact that version 5 had never been put to anyone.

**Who read what** — all read-only, on Sonnet (the user's standing rule for swarms):
- **Four code readers:** R1 every way a French marshal acts without your order, and its tie to trust or
  authority; R2 every order's click road; R3 how far the typed line reaches for standing orders and conditions;
  R4 how nature shapes decisions, today and under version 5. Each claim at file and line.
- **Three design panels of three experts:** P1 "does autonomy as a punishment contradict autonomy as a
  reward?" (a systems designer, a historian of the marshalate, a UX lead); P2 "buttons for simple things, typing
  for tasks, a wide array" (a strategy-UX designer, a parser engineer, a newcomer's advocate); P3 "different
  natures, different nights" (a designer of character-driven AI, a historian of 1805–1809 command, a hardcore
  player).
- **An adversary panel** (an engineer who knows this code's traps, a QA lead, an enemy-side designer), given all
  three panels and all four maps and told to break them.
- **Each panel and the adversary ran twice** — a fault in the run's last line made it re-run them — so every
  question has two independent samples.

**Not a scored round.** No marks out of 10 were asked: this was a review against the code and the user's three
new rulings, not a fourth round of the focus groups' loop, whose bar (above) stands and was never met.

**Where both samples agreed** (taken as settled): the trust crisis's "Grant Autonomy" is the one real clash and
should go; low authority's effects are indiscipline, kept and named apart; a man on his own is exempt from the
cannon-fire redirect and the jealous strike; the petition opens his card; about eight simple orders lack a
button; the read-back must show what it took and what it dropped; version 5 makes the bold men copies and the
careful men dig in nightly; nature-specific waiting, a third-night rule and one man per target.

**Where they split, and how it was settled:**

| Split | Settled | Why |
|---|---|---|
| What replaces "Grant Autonomy"? Both P1 samples: "stand him down" — three idle turns, a small trust gain | **A task to prove himself**, under exact orders, with today's rewards | Both adversaries: a stand-down is a free trust farm and drops the deed-and-reward content; P1's first sample had itself named "a task to the letter" as the later answer — version 6 lands it with the removal |
| Is the removal inside the user's consent? One adversary: "low authority" is not trust | Yes, read plainly | The game ties no autonomy to authority; the only autonomy granted at low standing is this one, and version 5 itself counted it as "a man acting without orders"; D24 is one line to strike |
| A daily seeded temper (both P3 samples) or none (both adversaries) | **No dice**; seven earned ways; the temper only as R-VARIETY's written fallback | Count-shopping and "personality is character, not situation"; the bar, written now, decides |
| A card as a second road (both P2 samples) or the user's "typing is used for missions" | **The line**, filled with his proposal, with chips that write into it | Typing stays the road, and every player can still give any task |
| Fixed risk floors and "at any cost" as no floor (P2) or one step (P3, adversaries) | **One step** | A word must not override a man's own odds |
| Two-step tasks, river lines, "their main army" (P2) or only what the design owns (adversaries) | **Refused free**, the nearest sentence written in | A second act, new scenario data, or a fog hazard |
| A mixed army's roles by nature with derived exact lines (P3) or "a second decision system and a count dodge" (adversaries) | **Its commander on his own, the rest supporting** by today's rules | No new system; the men's natures already decide how they join a fight |
| Re-key the enemy's mood per man (R4, P3) | **An arm of Session 4**, adopted only with the user's word | It changes the old game |

**The adversaries' first-rank list, and where each went:** the stand-down's price and farm — not adopted (D24);
a smuggled second act — refused, and a two-province hold is one area (§6.1, §8.3); risk words overriding a man's
odds — one step (§6.1); one rule for setting, recalling and swapping — a lost night (§6.3); R-INERT stated
precisely — the audience the one exception, the nerve worked out only for men on their own (§13); D9 decided in
the open — it stands, with a written fallback (§6.7); every new field listed and the nerve never saved (§12,
"Saves"); WS-12 — not a fresh ruling: ruled November 17 (`docs/audits/OPEN_CALLS_RULED_2026_11_17.md` §3), moved
unchanged to IC-8; an unseen enemy and a name that does not exist read the same (§8.3); Give the only change of
state, every quote pure (§8.4).

**Defects the review found in the shipped game** (§1.3): four, filed with strict-xfail pins in
`tests/test_ic_review_pins.py` — IC-V1 (a one-word condition dropped in silence), IC-V2 (the read-back shows no
condition), IC-V3 (a man acting independently can strike and act again in one turn), IC-V4 (eight simple orders
and four group orders with no button, and two help texts that say otherwise). Ledger: `BUG_FIXES.md` §IC review.

**The fresh readers' check, before the commit.** Two fresh Sonnet readers read the written version 6 — one for
plain words and contradictions, one for every claim about the code. The code reader found fourteen claims wrong
or overstated, all corrected here: two names in the examples that are not provinces ("Venetia"; "Ulm" as a
place), the two-word floor's real home (the clause guard, not `unread_condition_clauses`), risk words "not read
at all", the purchase floor's exact rule, a devoted man's immunity below 30, today's four arrival verbs ("then dig
in" is new), three task words that are new and "defend" kept as the stand, six condition clauses, the Help's words
quoted exactly, the cannon-fire redirect's two conditions, the literal man's restlessness rule as new, Napoleon's
ability in full. The plain-words reader found fifteen contradictions — some inherited from version 5 — and they
are settled in the text: the risk cap (one step from you, one from him, never more than two), Murat's two
provinces inside the once-per-order step, a man never objecting to his own proposal, today's order to a man on his
own as an ordinary order, the rule that decides between "on his own" and an exact order (§8.2), which ways of
waiting still count as waiting (§2, §6.7), the costs of a Support task, of another man's exact order and of the
trial, the trial's end, an army whose commander cannot be set on his own (§9.1), and when if-thens are checked.
The ledger's three unanswered findings (an ambiguous name; golden rule 8 for "Tonight") were written in too.

**Honest state.** Version 6 has been read by those two fresh readers; it has not been scored by a panel; nothing
it adds is built; the user's own play outranks all of it.

**Every finding and its ruling:** `docs/audits/ic_focus_groups/round4_review_ledger.md`.

---

## §20 Records, and the next session's prompt

**Version 6's records — written November 20, 2026:** this file; the review's ledger
(`docs/audits/ic_focus_groups/round4_review_ledger.md`); `BUG_FIXES.md` §IC review (IC-V1 … IC-V4) and the seven
rows moved from Session H's head to IC-8 (UI6-X70, X73, X74, X75, WS-12, WS-14; GRD-33 in `DESIGN_REFINEMENT.md`);
`PRE_DEPLOY_PLAN.md` §2's row IC; the pins `tests/test_ic_review_pins.py` and the plan-homes pin taught the IC
slices; STATUS (an entry and the NEXT UP lines), CLAUDE.md's live state, `docs/NEXT_SESSION_PROMPT.md` (Session 2,
its forks decided). **The next session's prompt is that file**; the one below is Session 1's, kept as the record.

**WRITTEN at the close of Session 1's first commit (November 19, 2026)** — STATUS's entry and NEXT UP line, CLAUDE.md's live state, `SYSTEMS_REFERENCE.md` §229, `BUG_FIXES.md` §IC; and at the close of its second (directives, the same day) — §230, `BUG_FIXES.md` §IC directives, STATUS, CLAUDE.md, `SAVE_FORMAT_REFERENCE.md` (`armies`, `war_goals`), `docs/NEXT_SESSION_PROMPT.md`. The paragraph below is the record of why they waited. **Not written in the design session, on purpose.** `docs/STATUS.md` holds exactly seven session entries and its pin
allows seven. `CLAUDE.md` is one byte under its size cap. Both carry pins that cost a full run of the suite, and
the working tree holds the user's uncommitted work. The routing lines for row IC are written at the close of
Session 1, with the trims they need. Until then this file, the folder `docs/audits/ic_focus_groups/` and the
memory note `feedback_autonomous_marshals_typing.md` are the record.

**Session 1's prompt, as it was decided (November 19):**

> Build row IC, Session 1 — the desk and the turn-end list — from `docs/INDEPENDENT_COMMAND_SPEC.md` (§4, §5,
> §11's menu steer, §15). Plan Mode first. Display only: the board must not move (R-INERT on every arm). Verify
> each line of §14 against the code before relying on it. Press everything in the real client at Interface Scale
> 1.8 on a 5120-wide window. Write the blind reading's questions and answer key before any frame is shot. One
> review before the commit. Write the row's routing lines into STATUS and CLAUDE.md with the trims they need.
> Then stop for my review before Session 2.
