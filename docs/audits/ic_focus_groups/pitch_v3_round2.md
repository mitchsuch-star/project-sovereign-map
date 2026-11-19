# ON HIS OWN — a design pitch (version 3)

*You are being asked to attack this design before anyone builds it. It is for a single-player, turn-based
Napoleonic strategy game on PC. Nothing below is built unless it says "exists today". Version 2 was torn apart
by six panels; section 10 lists what they found and how each fault was ruled. Try to break those rulings.*

---

## 1. The game, in short (all of this exists today)

- You are Napoleon in 1805. The map is Europe in 126 provinces. One turn is a few days.
- You have **7 marshals with corps, plus your own corps** (8 in all), and **4 actions a turn** shared by all of
  them. A move or an attack costs an action. On an average turn most of your corps do nothing.
- The other powers have **1 to 3 corps each and also 4 actions**. Every enemy corps acts every turn, sometimes
  twice. This gap is the game's oldest complaint.
- Marshals have a **nature**: bold (Ney, Lannes, Murat, Masséna), careful (Davout, Bernadotte) or literal (Soult;
  Grouchy if you hire him). By nature a bold man attacks with 7 men to the enemy's 10; a careful man wants 13.
  A literal man does exactly what he is told.
- Marshals have **trust** in you (0–100), **object** to orders against their nature, grow **jealous** of each
  other's glory, and have an **order of rank**: a higher man placed under a lower one takes it ill.
- **Standing orders** exist: take (march to) a place, pursue an army, hold, support a friend. They cost 2 actions
  to give (1 for a literal man) and then run by themselves, free, after the enemy has moved. A hold can carry
  **one if-then** ("if Mack advances, fall back to Bohemia").
- **Fog of war**: you see enemy corps only near your own corps, scouts and watchtowers. A spy mission (3 turns)
  lifts the fog over one nation's land for 5 turns. Today nothing shows you an enemy marshal's nature or orders.
- The Emperor's own corps gives **+10% attack and defence to every friendly corps in his province**, and a
  marshal who fights beside him earns **half the glory**.
- A big undecided battle (50,000+ men) becomes a **"day of battle"** fought over several rounds, in which you
  choose what your side does. You may also press "Leave it to him".
- **Laws** are bought with gold or with the Emperor's authority. France's great one is "the Staff" (9,000 gold,
  300 a turn); today it gives one more action a turn. Each great power has its own.
- You **win** by holding 45 "titled" provinces and having the great powers accept the peace at a Congress.
- You can play by clicking or by **typing** ("Ney, attack Mack"; "can Ney reach Vienna?"). Typing is optional.
- The developer's first full playtest ended: "everything feels convoluted and opaque and disconnected".

## 2. The idea

You are the Emperor. You cannot be everywhere. The corps near you, you command by hand — and they fight better
under your eye. Everywhere else you choose a man, tell him what you want, and then live with who he is.

1. **The desk** — three lines always on screen: THE PEACE (how you win, how far along), THE WAR (each war's
   goal), TODAY (up to three matters that need a decision, each a click away).
2. **One line before the day ends** — everything about to happen or go wrong, said at once. Press again to go.
3. **On his own** — a standing order given to a bold or careful marshal *to carry out by his own judgement*.
4. **Exact orders** — a literal marshal's standing order, with up to three if-thens he follows to the letter.
5. **Typing talks to them** — their names sit by the command line; you ask, adjust, overrule or recall in a
   sentence, and they answer in their own voice.

One new idea, then: every standing order is given either **exact** (as today) or **on his own** (new).

## 3. The order of a turn (the same for every nation)

1. **Your day.** You give orders by hand.
2. **You end the day.** Your marshals who are on their own act — once each, highest rank first — *exactly as the
   screen said they would*. Then the enemy answers.
3. **Each enemy nation's day**, in turn: its orders by hand, then its marshals who are on their own.
4. **Tripwires.** Standing marches go on, and exact orders are checked: an if-then fires on what the *other side*
   has just done. (This is where standing orders run today.)
5. **Morning.** What you lost and gained; one line from each of your marshals; then the rest.

So no side's men get the last word, and nothing moves between your last order and your marshals' acts.

## 4. On his own — the rules

**The order has four parts and one switch** (each a short fixed list — clicked or said):

| Part | Choices |
|---|---|
| **Task** | **Take** a place · **Pursue** an army · **Hold** an area · **Support** a friend · **Watch** a frontier (scout, report, avoid battle). The first four are the standing orders you already know. |
| **Area** — set by the task | *Hold, Watch:* one or two provinces (three for a marshal of outstanding command — Davout); he stays in them. *Take:* the place, and the road to it, drawn on the card with the nights it will take; he stays on that road and in that place. *Pursue:* a named enemy army; he follows it, but never more than three marches from where he started (a ring on the map). *Support:* a named friend, not the Emperor; he stays within one march of him. |
| **Risk** | **High · normal · low** — the odds he needs to attack. A bold man: 5.5 / 7 / 8.5 men per 10 of the enemy. A careful man: 11.5 / 13 / 14.5. These numbers are fixed. A man on his own has no moods and rolls no dice to decide. |
| **Conditions** (up to two) | "If outnumbered, fall back on X" · "March to the guns" (join a battle within two provinces; that is then his act for the next night) · "Until recalled / for N turns / until X falls / until Ney arrives" |
| **Switch: he may plunder** | Off unless you turn it on. The card shows what plunder gains and what it costs you at the peace. |

**Who.** A bold or careful marshal whose trust in you is 30 or more. Not a literal man, the Emperor, an ally's
commander, or a man already on the three-turn "free rein" (below). Gun commanders: Hold or Support only.

**How many — one count.** The desk shows **"On their own: n of N"**. It counts every corps that acts without
your hand: each marshal on his own, each corps attached to one (section 7), each literal man under exact orders
(section 5), and any man on the "free rein" the game already grants for three turns after a crisis of trust.
**N is 2 at the start, 3 with the Staff, 4 with a new law, "the Emperor's Aides-de-Camp"** — at most half your
army. If the Staff lapses, N falls: the laws' forecast warns you first and you choose whom to recall; otherwise
the lowest-ranked goes. No trust is lost.

**What it costs.** 2 actions, once. After that his act each night is free: **one real act** — a move, a fight,
digging in, or a scout. Changing posture (stance, leaving works or a square) rides free with it. If you give him
an order by hand that day, *that* is his act ("acted today; nothing tonight"). If his fight turns into a day of
battle, the day is his act until it ends.

**"Tonight."** Because nothing moves between your last order and his act, the screen shows exactly what he will
do: *"Tonight: attacks the Archduke at Caldiero — 8 men to his 10. [Order it yourself]"*. It is on his card, in
the day's-end line, and as an arrow in the map's "tomorrow" view. One exception, said in advance: a lower-ranked
man acts after a higher one; if the higher man's battle changes the board, the lower man thinks again, and his
line next morning says so. If "tonight" would be a great battle, the line says so, and you may order it yourself
(1 action) to fight the day by hand. If you leave it, he fights it his own way — never in silence.

**What comes first** (top wins):

1. **The law** — he goes only where your corps may go today: your land, land at war with you, allied and client
   land. Never neutral or at-peace land. Never the sea.
2. **Survival** — any corps that is shattered withdraws, even out of his area. A last stand is still yours to
   decide, as today.
3. **Your order for today.**
4. **His conditions**, in the order you gave them.
5. **His task**, in his area, at his risk, in his nature.
6. **When idle** — Hold: dig in, up to the usual limit (he never drills on his own). Take: march. Pursue: head for
   the last sighting. Support: close up. Watch: scout.

**His way** (on the card before you give the order):

| | A bold man | A careful man |
|---|---|---|
| Walls | Storms a garrison if his odds are met | Never storms; besieges (1–2 turns) |
| An enemy he has just beaten off on his area | Attacks if his odds are met | Counter-attacks if his odds are met |
| A beaten enemy leaves his area | **Follows one province out, once per order** — if his risk is high or his trust is under 50 (under 30: every time). You see it first: *"Tonight: follows Mack into Bavaria — one step outside his area."* He storms nothing and takes nothing there, and returns by the safest lawful road. | Never |
| A friend he hates | Will not march to that man's guns. The card warns you. | The same |
| Objects to being given | Hold or Watch with an enemy near | Tasks against bad odds or walls |

**What he never does.** Take land the task did not name. Recruit, build or spend gold. Answer a letter or a
treaty. Cross neutral land or the sea.

**The life of the order.** *Given* → *on the road* (to his area; he does not seek battle) → *at work* → *asks*
(task done; target destroyed or unseen three turns; no lawful road; the area cannot feed him — one standing row
in TODAY, never a window) → *suspended* (wounded, broken or recovering: it resumes when he is fit) → *ended*
(recalled; killed or captured; the count falls; peace with the nation a Take or Pursue was against — the game's
existing road-home rule then walks him out). A Take that is done becomes a Hold of that place at once.

**The morning.** One block, "Your marshals": one line a man, in his own voice, with the plain cause beside it.
Click for the full letter. "Held; nothing seen" lines fold into a count. Lines are keyed to the situation and
each man remembers one thing (a rival's absence, an order you overruled, a slight).

**The card** suggests a filled-in order you can accept with one click; states the purpose ("In the war against
Austria — war goal: Vienna"); shows his way, the cost, the count; names who would take the choice ill and who
could be chosen with nobody minding; and gives his answer in his own voice.

**Trust and glory.** Trust +5 only for a task done against an enemy (a battle fought, or a defended place
taken), at most once per man in ten turns; changing a task is never a new order. A battle fought alone earns full
glory (beside the Emperor, half), so marshals want to be on their own and the others grow jealous by today's
rules. Choosing a man while a bold marshal who outranks him has no such order costs that higher man's good
opinion of him; the card warns. Recalling a man mid-task costs trust 3, shown before you confirm.

## 5. Exact orders — the literal man

- A literal marshal cannot be set on his own. Instead, any standing order of his carries **up to three if-thens**,
  numbered. This is true for every nation.
- **If:** an enemy comes within reach · he is attacked · he is outnumbered · he is being surrounded · a named
  friend is attacked · a named place falls · a named friend arrives.
  **Then:** attack · attack if not outnumbered · fall back on X · march to X · march to that friend's guns · dig in.
- A line fires only on what he can know: what France sees in or beside his province, and guns within two
  provinces. Forces under 5,000 men trip nothing.
- Lines are checked in order after the enemy has moved; the first true one fires. **Each line is used once.** His
  piece shows "2 of 3 lines left". A "march to X" that fires carries on until he arrives.
- When no line fits, or all are used, **he stands** and a TODAY row says so. Writing him new orders costs 1 action.
- Bare "attack" means attack whatever the odds. The read-back shows today's odds beside every attack line, marks
  one that would be fatal, and warns of a gap ("nothing here covers being outnumbered").
- 1 action. He counts as one of "on their own". Other marshals keep today's rule: one if-then, on a hold.

*Why:* a man on his own is an **actor** — he moves on your turn and you see it coming. A literal man is a
**tripwire** — he answers the enemy the same night, exactly as written, and never otherwise.

## 6. Talking — the typed line's job

- **Open lines.** The names of marshals on their own or under exact orders sit by the command line. Click one: the
  line starts "Masséna, " with four ready things to say.
- **Ask** (free): "what will you do?" · "what do you see?" · "why did you fall back?" · "can you take Verona?" The
  answer is the same reading the night will use — asking changes nothing.
- **Adjust** risk or a condition: free, **reaches him tomorrow**, once in three turns per man.
- **Change** task or area: 1 action.
- **Order for today**: any ordinary order at its usual price; it is his act for the night. The read-back offers
  "make it his new task (1 action)" beside "send".
- **Recall**: no actions.
- **The read-back rule.** Before anything is spent the line shows every part it took and names every part it did
  not. With no language model the fixed phrasings work; with one, it only maps freer wording onto the same parts.
- Every act also has a card. Typing is never the only way.

## 7. The war goal and attached corps

- **The war goal**: one place a war aims at ("Vienna"). A task "take the war goal" follows it. Changing the goal
  costs 1 action while any man serves it.
- **Attached corps**: a marshal on his own may have up to two more corps attached; they move and fight with him.
  Each counts as one of "on their own". Needs the Staff; one such group at a time; the Emperor cannot be
  attached. A higher-ranked man attached under a lower one takes it ill, and it shows before you confirm. If the
  leader falls, they show as idle.

## 8. The other side of the hill — how the enemy uses it

**Honest framing.** The enemy has no shortage of actions, so this gives it no extra acts. What it gives the enemy
is *structure*, and gives you an opponent you can *read*.

- **A main army**, fixed when the war starts (the corps nearest the court's war goal). It is run by hand, with
  the full decision logic, exactly as today.
- **Every other corps holds a standing role** in the same four-part form, set relative to the main army and the
  war goal: support its flank · hold the home frontier · take a secondary goal · else watch — with "march to the
  guns" by default. Such a man acts once, at the end of his nation's day, under the same six lines and the same
  "way" as yours. A nation with one corps has none. Roles exist only for nations at war.
- **Literal marshals** (Mack, Buxhowden) get exact orders. What a court writes is **drawn by the campaign's seed
  from two or three authored sets per man**; the historical seed gives the historical one. For Mack: "hold Swabia
  until Kutuzov arrives" (Ulm) · "hold; if outnumbered fall back on Upper Austria" · "march to the Inn to meet
  Kutuzov". Ulm becomes something you find out, not something you memorise.
- **A court rewrites orders** only on stated triggers — a line used or made impossible; the task done or
  impossible for two turns; a dispatch lost; a recall — the morning after, for 1 of its actions.
- **A court gives "an order for today"** to such a man only when: its capital is in danger; the man's survival;
  or its main army is in battle within the sound of the guns.
- **"The capital is in danger"** is a new rule (today the game reacts only once a capital is *lost*): hostile
  strength within two marches exceeds its garrison plus the court's own corps within two marches. Then the
  *nearest* man on his own is recalled — one, not all — and is not sent out again for five turns. A court that
  has had a man baited out and beaten sets him one step safer for five turns.
- **No trust, no Wing.** Enemy marshals have no trust in their court, so the low-trust rules never touch them, and
  no court will in practice attach corps.
- **Tempo is measured.** If courts come out weaker or stronger than today on the standing test seeds, the lever
  is the court's action budget.

**What you can learn** (position, strength and orders stay fogged; nothing is shown that you have not learned):

- **Natures are public** — reputations were. Every marshal's nature shows on his piece.
- **Task and area** — your spy mission now also reports them, for marshals standing inside that nation's land.
- **The full text, if-thens included** — only from a captured dispatch, taken when you *rout* a corps. It is
  stamped at the moment of capture, and the beaten court rewrites two nights later. What you hold is good for a
  short time.
- **Berthier's reading** — after watching a man for three turns, "will / may / will not", worked out only from
  what France has seen him do, never from his real orders.
- Knowledge ages by time only: "learned 4 turns ago". You are never told that orders changed.
- The enemy's "tonight" is never shown.

**What the enemy learns of you.** Its decision logic sees your corps, as today. It never reads your orders or
your marshals' natures — with one exception: when one of your men on his own is routed, the court learns his
task, and if he was to take a place, it covers that place as if it were in danger.

**Playing against it** (and it against you): bait a bold man at high risk one province out and cut him off ·
mass against a careful man, or stop him with a fort · learn a literal man's lines and do the thing they do not
cover · strike a friend to pull his supporter off his post · put a capital in real danger to draw one man home.

## 9. Rulings on edge cases

1. Count full → the card says so and offers to recall another man. A place freed is usable next turn.
2. A task against his nature → he objects, with today's answers. "Trust his judgement" takes his counter-proposal.
3. At peace only Hold, Support and Watch can be given. Take and Pursue belong to a named war.
4. A broken, wounded or besieging marshal can be given an order; it starts when he is fit. "For N turns" counts
   from that day.
5. Two men after the same enemy: both may attack, senior first; if the enemy retreats the junior thinks again.
6. Friends beside a fight join by today's rules. A man on Hold leaves his post for another's battle only under
   "march to the guns". A man on his own is never asked the "shall I march to the guns?" question.
7. If the Emperor's corps is in the battle's province it is the Emperor's battle (+10%, half glory), and the
   marshal's line next morning says what he thinks of that.
8. Taking a marshal's day of battle yourself costs him nothing.
9. "March to the guns" takes him out of his area: he takes nothing there and returns the next night.
10. The friend he supports is killed or captured → he holds where he stands and asks.
11. "Until Ney arrives" and Ney dies → the condition lapses and he asks. "Until X falls" when X has already
    fallen → refused at the read-back.
12. Trust falls under 30 while he is on his own → he keeps the order but takes no adjustments. You can still give
    him an order for today, or recall him.
13. A man on his own cannot launch the jealous solo attack idle bold marshals sometimes make. "Everyone, march"
    and the Staff's army order skip him and say so.
14. A petition for a command of his own needs a free place; with none, you may promise it for two turns.
15. An exchanged prisoner comes back with no order.
16. Saves keep the order, its conditions, used lines, siege progress, the unseen-turns count and the adjustment
    stamp. Old saves have none.
17. A used line stays used even if its condition comes true again; the card says so.
18. Two switches guard the old game: with the player's side unused, and the enemy's side switched off, every
    committed test run reproduces today's results exactly.

## 10. What version 2's panels found, and the rulings (try to break these)

| Fault found in version 2 | Ruling in version 3 |
|---|---|
| Pursue and Support broke "he keeps to his ground"; how he reached his ground was never said | The area is defined per task; an "on the road" state |
| The cap leaked: a Wing, literal men and "free rein" men all sat outside it | One count of every corps that acts without the hand |
| A plan he might not keep was "a lie on the map"; France's men got the last word each night | He acts when you end your day, before the enemy; what the screen says is what he does |
| "Nothing is random" was false: the decision logic rolls a daily mood | No moods or dice for a man on his own; asking changes nothing |
| Fog not stated for the enemy; a pursuer could reveal a hidden army; enemy if-thens would have read France's sight | Every man decides on his own nation's sight; a pursuer heads for the last sighting |
| "The enemy recalls when its capital is threatened (exists today)" was false, and a feint would empty every front | A new, defined rule; only the nearest man; no re-sending for five turns |
| The enemy gained nothing, or got slower | Rewritten: a main army in hand, standing roles for the rest, measured tempo |
| Court orders were the same every game | Seeded from authored sets |
| A 5,000-man probe could use up a literal man's lines | Forces under 5,000 trip nothing; courts rewrite |
| Hand order by day, free act by night = two acts; marching to the guns and days of battle likewise | One act: each of these *is* the act |
| An unanswered day of battle left him silent | He fights it his own way |
| Trust could be farmed with trivial tasks | Only for a task done against an enemy, once in ten turns |
| Plunder by default harmed the player unasked | A switch, off by default, with the price shown |
| Free daily change of risk was puppetry | It reaches him tomorrow; once in three turns |
| Allied land was banned in one list and allowed in another | He goes wherever your corps may go today |
| Three lines for you, one for a court without its Staff | Three for every nation; courts differ in what they write |
| "Stale" intelligence told you orders had changed | Knowledge ages by time only |
| Too many words for one idea | Tasks use the standing orders' names; one new idea, "on his own" |
| About twenty items on a busy morning | One block, one line a man |

**Ruled against, with reasons:** a second axis of character (it would recast every marshal; the natures are
earlier decisions that run through the whole game) · a purpose picker (new players already carry too much; the
card states the purpose from the war goal) · couriers that take turns to arrive (three panels approved its
absence; the one-night lag on adjustments is the whole of it).

## 11. What we are least sure of now

- He acts before the enemy, so he no longer answers the enemy the same night. Only tripwires do. Right?
- Plans that are always true: are the men now too tame to be "who they are"?
- The count of 2 / 3 / 4 for eight corps.
- Exact orders: is "each line used once" a good game or a chore?
- Do standing roles make the enemy a better opponent, or only a different one?
- Is the new "capital in danger" rule sound, or the next thing to be gamed?
- Attached corps each counting one: is such a group ever worth it?
- The one-night lag on adjustments: sensible, or one rule too many?
