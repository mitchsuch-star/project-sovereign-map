# ON HIS OWN — a design pitch (version 4)

*You are being asked to attack this design before anyone builds it. It is for a single-player, turn-based
Napoleonic strategy game on PC. Nothing below is built unless it says "exists today". Two earlier rounds of
panels tore apart versions 2 and 3. Version 4 answers them mostly by CUTTING. Section 9 lists what round two
found, the rulings, and what was cut. Try to break the rulings, and say whether the cuts were right.*

---

## 1. The game, in short (all of this exists today)

- You are Napoleon in 1805. Europe in 126 provinces. One turn is a few days.
- You have **7 marshals with corps, plus your own corps** (8 in all) and **4 actions a turn** shared by all of
  them. A move or an attack costs an action. On an average turn most of your corps do nothing.
- The other powers have **1 to 3 corps each and also 4 actions**; every enemy corps acts every turn. The gap is
  the game's oldest complaint.
- Marshals have a **nature**: bold (Ney, Lannes, Murat, Masséna), careful (Davout, Bernadotte) or literal (Soult;
  Grouchy if you hire him). They have **trust** in you (0–100), **object** to orders against their nature, grow
  **jealous** of each other's glory, and stand in an **order of rank**: a higher man put under a lower one takes
  it ill. An idle, jealous bold marshal sometimes **attacks on his own** as the turn ends, after a warning.
- **Standing orders** exist: take (march to) a place, pursue an army, hold, support a friend. They cost 2 actions
  to give (1 for a literal man) and then carry themselves out, free, after the enemy has moved. A hold can carry
  **one if-then** ("if Mack advances, fall back to Bohemia"). There is no limit on how many you give.
- **Fog of war**: you see enemy corps only near your own corps, scouts and towers. A spy mission (3 turns) lifts
  the fog over one nation's land for 5 turns. Today nothing shows you an enemy marshal's nature or orders.
- The Emperor's own corps gives **+10% attack and defence to every friendly corps in his province**; a marshal
  who fights beside him earns **half the glory**.
- A big undecided battle (50,000+ men) becomes a **"day of battle"** fought over rounds, in which you choose
  what your side does, or press "Leave it to him".
- **Laws** are bought with gold or with the Emperor's authority. France's great one is "the Staff" (9,000 gold,
  300 a turn); today it gives one more action a turn.
- You **win** by holding 45 "titled" provinces and having the great powers accept the peace at a Congress.
- You can play by clicking or by **typing** ("Ney, attack Mack"; "can Ney reach Vienna?"). Typing is optional.
- The developer's first full playtest ended: "everything feels convoluted and opaque and disconnected".

## 2. The idea

You are the Emperor. You cannot be everywhere. The corps near you, you command by hand, and they fight better
under your eye. Everywhere else you choose a man, tell him what you want, and then live with who he is.

1. **The desk** — three lines always on screen: THE PEACE (how you win, how far along), THE WAR (each war's
   goal), TODAY (up to three matters that need a decision, "+n more" behind them).
2. **One line as the day ends** — everything about to happen, said at once.
3. **On his own** — a standing order a bold or careful marshal carries out by his own judgement.
4. **Exact orders** — a literal marshal's standing order, with up to three if-thens he follows to the letter.
5. **Typing talks to them** — ask, change, order for today, recall; they answer in their own voice.

There are two kinds of order: **today's order** (by hand) and **a standing order**, which is either *exact* (as
today: it does the one thing it names and never chooses) or *on his own* (new: he chooses).

## 3. The order of a turn

| Step | What happens |
|---|---|
| 1. Your day | You give today's orders. |
| 2. You end the day | **First of all, before anything else moves:** every marshal on his own does what the screen says under "Tonight" — an act, or "waits" — highest rank first. (Today's jealous solo attacks join this same pass and are shown the same way.) |
| 3. The enemy's if-thens | Letters lapse. Then each enemy literal marshal checks his if-thens once, on what you have just done. |
| 4. The enemy's day | Each enemy nation moves its corps, as today. |
| 5. Your if-thens | Checked **once, on the board as the enemy left it**, for your marshals who *waited* and for exact orders; carried out highest rank first. One that has become impossible does nothing and is not used up. No chains. Standing marches go on, as today. |
| 6. Morning | What you lost and gained; one line from each of your marshals; then the rest. |

**One thing a night.** A marshal on his own does exactly one of these: the act shown under "Tonight"; **or**, if
"Tonight" says *waits*, the first of his if-thens to come true at step 5 — or joining a battle fought next to
him, if "march to the guns" is among them. Never two. A day of battle is his one thing each night until it ends.
Today's order, if you give him one, is his one thing.

## 4. On his own — the rules

**The order**

| Part | Choices |
|---|---|
| **Task**, with its area and its "so that" | **Take** a place — so that it is yours. Area: the place and the road to it, drawn on the card with the turns it will take. On the road he fights only what bars it, if his odds are met; otherwise he waits, and asks after two turns. · **Pursue** a named enemy army — so that it is destroyed (at less risk: so that it is pinned). Never more than three marches from where he started (a ring on the map); if it leaves the ring or is unseen three turns he stops and asks. · **Hold** one or two provinces — so that the enemy does not have them. · **Support** a named friend, not the Emperor (the corps beside you are yours to command by hand) — so that he is covered. He stays within one march of him. · **Watch** one or two provinces — so that you are warned. He scouts each night and avoids battle. |
| **Risk** | **More · usual · less**, always shown as numbers: 1.5 men in 10 either side of *his own* odds. Each marshal's own odds are authored — for example Murat 6, Ney 6.5, Lannes 7, Masséna 7.5 men to the enemy's 10; Davout 12, Bernadotte 14. No moods, no dice. He reckons from what France knows: exactly, where the enemy is fully seen; from the middle of the range where he is partly seen ("about 8 to 10"); and he never attacks what France cannot see. Watch has no risk setting. |
| **If-thens** (up to two) | The same lists as exact orders (section 5). Each is used once. They are checked only on a night he waited. |
| **Switch: he may plunder** | Off unless you turn it on. The card shows what it gains and what it costs you. |

**Who.** A bold or careful marshal with trust 30 or more. Not a literal man, the Emperor, an ally's commander, or
a man who is "out of hand" (the three turns of acting without orders the game already grants after a crisis of
trust). Artillery marshals: Hold or Support only.

**How many.** The desk shows **"On their own: n of N"**: marshals on their own, plus any man out of hand. **N is 1
at the start, 2 with the Staff, 3 with a new law, the Emperor's Aides-de-Camp.** The count limits *judgement*.
Exact orders are not counted, and never were: an exact order does the one thing it names and never chooses.

**What it costs.** 2 actions to give. **Any change — task, area, risk, an if-then — 1 action, at once.** Asking
is free. Recalling costs no actions; it costs trust 3 only if you chose it while he was in the middle of a task,
and the button says so.

**"Tonight" is true.** The pass runs first, so nothing moves between your last order and his act. The line on the
map and in the day's-end line says exactly what he will do — *"Tonight: attacks the Archduke at Caldiero, about 8
to 10. [Order it yourself]"* or *"Tonight: waits. If Soult is attacked, marches to his guns."* One exception,
shown on the line: if a higher-ranked marshal's act has made his own impossible, or worse than his odds, **he
holds. He never improvises.** If "Tonight" would be a great battle the line says so; order it yourself to fight
the day by hand, or leave it and he fights it his way.

**What comes first:** (1) where he may go — wherever you could march that corps by hand; (2) survival — a
shattered corps withdraws by the game's retreat rule; a last stand stays yours to decide; (3) today's order;
(4) his task, at his risk, in his nature — or, on a night he waits, his if-thens; (5) idle: he waits (on a Hold
he digs in up to the usual limit; he never drills on his own).

**His way** (shown before you give the order): his nature, **one personal line**, his feuds, his rank.

| | A bold man | A careful man |
|---|---|---|
| Walls | Storms a garrison if his odds are met | Never storms; besieges (1–2 turns) |
| A beaten enemy leaves his area | Follows one province out, once per order — if set to more risk or his trust is under 50 (under 30: every time). You see it first as "Tonight". He storms and takes nothing there and comes back by the safest road. | Never |
| A friend he hates | Will not march to his guns; the card warns | The same |
| Objects to being given | Hold or Watch with an enemy near | Tasks against bad odds or walls |

Personal lines (authored, one each, each a tested rule): **Murat** — horse: follows two provinces, not one.
**Ney** — marches to the guns whether told to or not. **Lannes** — storms walls at one step more risk.
**Masséna** — never gives up a walled place; asks for the plunder switch. **Davout** — keeps three provinces in
hand. **Bernadotte** — marches only to the guns of a man who outranks him.

**The life of the order**

| State | What he does | Leaves it when |
|---|---|---|
| Given | Nothing yet; you can undo it until the day ends | The day ends |
| On the road | Marches to his area | He arrives; or the road is barred two turns (→ asks) |
| At work | His task, or waits | Task done; target lost; area cannot feed him; no way he may go (→ asks) |
| Asks | Keeps his idle behaviour; one standing row in TODAY | You answer |
| Suspended | Recovers (wounded, broken) | He is fit (→ back where he was) |
| Ended | — | Recalled; killed or captured; N falls (you choose whom, else the lowest rank; no trust lost); peace in the land he stands in or with the nation he was sent against (the game's road-home rule walks him out) |

A Take that is done becomes a Hold of that place: same place in the count, no new reward.

**The card** opens on a suggested order and one sentence — *"Lannes holds Ulm and attacks at 7 to 10. 2 actions."*
— with [Give] and [Change]. Everything else is behind Change.

**The morning.** One block, "Your marshals": a line a man, in his own voice, the plain cause beside it; the full
letter on a click; quiet lines folded into a count. Each man remembers one thing (a rival's absence, an order you
overruled, a slight).

**Trust and glory.** Trust +5 when he wins a battle under the order or takes a defended place; at most once per
man in ten turns. Changing his task does not earn a second +5. Alone he earns full glory (beside the Emperor,
half). Choosing a man slights a bold marshal who outranks him only if that marshal is within three marches and
has no order of his own; it is forgotten when he gets one. The card names who would mind and who could be chosen
with nobody minding.

**What he never does.** Take land the task did not name. Recruit, build or spend. Answer a letter or a treaty.

## 5. Exact orders — the literal man (the same for every nation)

- A literal marshal cannot be set on his own. Any standing order of his carries **up to three if-thens**, numbered.
- **If:** an enemy comes within reach · he is attacked · he is outnumbered · he is being surrounded · a named
  friend is attacked next to him · a named place falls · a named friend arrives · a named enemy comes within reach.
  **Then:** attack · attack if not outnumbered · fall back on X · march to X · march to that friend's guns · dig in.
- *Within reach*: next to him (two provinces for horse). *Outnumbered*: fewer men than the enemy within reach.
  *Being surrounded*: enemy corps in two or more provinces next to him and no friend next to him.
- A line fires only on what his own nation can see. A force under a fifth of his own strength trips nothing
  (forces in one province are added together).
- Checked at the if-then step (section 3). **Each line is used once**; his piece shows "2 of 3 left". When none
  fits he stands, and a TODAY row offers **[Renew his orders]** for 1 action.
- Bare "attack" means whatever the odds. The read-back shows today's odds beside each attack line, marks a fatal
  one, and warns of a gap.
- 1 action. Not counted. Other marshals keep today's rule: one if-then, on a hold.

## 6. Talking — the typed line's job

Names of marshals on their own or under exact orders sit by the command line. **Ask** (free; the same reading
his act will use, and asking changes nothing in the game). **Change** (1 action). **Today's order** (usual price;
the read-back offers "make it his new task" beside "send"). **Recall**. **The read-back rule:** before anything is
spent, the line shows every part it took and names every part it did not. No language model is needed. Every act
also has a card.

## 7. The war goal

One place a war aims at ("Vienna"). A task "take the war goal" follows it. Changing the goal costs 1 action for
each man serving it. Two marshals work as one force with no new rule: one leads, and the other is set to Support
him (and a higher man supporting a lower one takes it ill, as today).

## 8. The other side of the hill — the enemy

**The enemy keeps its hand.** Its bold and careful marshals are moved by their court exactly as today, moods and
all. Courts are not short of actions, so they set no man on his own. Two rounds of panels showed that forcing
"roles" on them made the enemy slower or easier to solve.

**What every court gets is a plan of campaign**, drawn by the campaign's seed from two or three authored plans
per court (the historical seed draws the historical one, and the menu says so). A plan does two things:

- It **writes exact orders for the court's literal marshals** — the same three if-thens and the same rules as
  yours. Austria: "hold the Iller until the Russians arrive" (Ulm) · "the Inn line, falling back on Vienna" ·
  "march to join the Russians". Russia's Buxhowden: "march to Moravia; if Kutuzov is attacked, to his guns".
  A plan may include "if Napoleon comes within reach, fall back on X".
- It **sets two dials the court's logic already reads**: its posture (how good the odds must be), and one
  province its corps favour.

A court rewrites a literal man's orders the morning after a line is used or made impossible, or after he has
stood two turns; two nights after losing a dispatch. Rewrites cost it nothing but that night.

**What you can learn** (position, strength and orders stay fogged):

| How | What it gives |
|---|---|
| Free | Every marshal's **nature**, on his piece. Reputations were public. |
| The spy mission | The **plan's name and posture**, and each literal marshal's task, wherever he stands. |
| A captured dispatch — when you rout any corps of that court | The **written lines of that court's nearest literal marshal**, in his own court's words. Good for two nights: the court then rewrites. |
| Berthier's reading — after watching a man three turns | "Will / may / will not" about four named things (attack you here · leave his ground · fall back if pressed · march to a friend's guns), worked out only from what France has seen him do. |

Knowledge ages by time only ("learned 4 turns ago"). A literal man can be read as "will"; a bold or careful
enemy only as "may", because his court's logic has moods.

**What the enemy learns of you.** Nothing new — with one exception: when one of your men on his own is routed,
the court learns his task, and if he was to take a place its corps favour that place for five turns (the dial
that exists). The enemy's logic reads the board as it does today; this design adds no new all-seeing read, and
its if-thens use the live sight the code already has for each nation.

**Playing against it.** Learn a literal man's lines and do what they do not cover. Learn the plan. Read each
man's nature for his odds. And expect the enemy to prefer your men on their own to the Emperor's stack: they
fight without his +10%.

**Two switches** guard the old game: with the player's side unused and the enemy's side off, every committed test
run reproduces today exactly. A purity test checks that every question and preview leaves the saved world and
the random state untouched.

## 9. What round two found, the rulings, and the cuts

| Found in version 3 | Ruling in version 4 |
|---|---|
| Acting before the enemy cost him the power to react: a man who had acted could not fall back or march to the guns that night; the same if-then fired at different moments for different men | One thing a night: the act you saw, or — if he waited — his if-thens after the enemy has moved. One word, one moment, for every marshal. |
| A lower man "thought again" after a higher man's battle and did something never shown | He does what the screen said, or holds. He never improvises. |
| Letters lapsing and jealous attacks ran between your last order and his act | His pass runs first of all; jealous attacks join it |
| The count mislabelled literal men as "on their own" and still missed ordinary standing orders | The count limits judgement only. An exact order never chooses. |
| Four bold men were one man | Each marshal's own odds, and one personal line each |
| "Capital in danger": gamed by a feint, false for most courts | Cut, with enemy roles |
| Enemy roles: slower, easier to solve, broke the court's existing reactions, needed fog the game does not have | **Cut.** The enemy keeps its hand; it gains plans. |
| A fixed-number enemy was a solved machine | The enemy's bold and careful men keep their moods |
| A captured dispatch showed the orders you had just beaten | It shows the nearest literal marshal's lines |
| The one-night lag was a hidden pending state | **Cut.** Any change: 1 action, at once. |
| Attached corps were never worth their place | **Cut.** Set a second man to Support the first. |
| A 5,001-man probe used up a line | A force under a fifth of his strength trips nothing |
| Trust for any battle fought, even lost | Only for a battle won or a defended place taken |
| A free question could probe the fog through his odds | He reckons from what France knows |
| Twelve ideas on the first card | The card opens on a suggestion and one sentence |
| "Risk: high" read backwards; "conditions/lines/if-thens"; "the law"; "free rein" | More/usual/less with numbers; "if-thens"; "where he may go"; "out of hand" |

**Ruled against, with reasons:** counting every standing order (it would cap the ordinary marches the game has
today) · upkeep on a man on his own (bookkeeping; the choice is who and what) · an if-then that fires every time
(it is a man on his own outside the count) · a purpose picker and a "contain" task (the card states a "so that";
Pursue at less risk *is* contain) · couriers and a second axis of character (as before).

## 10. What we are least sure of now

- Was cutting the enemy's roles right, or did the enemy's half shrink to too little?
- Exact orders stay outside the count, bounded only by "each line used once". Is that bound enough?
- One thing a night with act-or-wait: clear, or one idea too many?
- Authored odds and one personal line each: are the men men again?
- N of 1 / 2 / 3.
- Is the typed line's job real, or still a shortcut for cards?
