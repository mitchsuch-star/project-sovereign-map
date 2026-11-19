# HIS OWN COMMAND — a design pitch (version 2)

*You are being asked to attack this design before anyone builds it. It is for a single-player, turn-based
Napoleonic strategy game on PC. Nothing below is built yet unless it says "exists today".*

---

## 1. The game, in short (all of this exists today)

- You are Napoleon in 1805. The map is Europe in 126 provinces. One turn is a few days.
- You have **7 marshals with corps, plus your own corps** (8 in all). You get **4 actions a turn**, shared by all
  of them. A move or an attack costs an action. So on an average turn most of your corps do nothing.
- The other powers have **1 to 3 corps each and also 4 actions**. Every enemy corps acts every turn, sometimes
  twice. This gap is the game's oldest complaint.
- Marshals have a **nature**: bold (Ney, Lannes, Murat, Masséna), careful (Davout, Bernadotte) or literal (Soult;
  Grouchy if you hire him). A bold man attacks when he has 7 men to the enemy's 10. A careful man wants 13 to 10.
  A literal man does exactly what he is told and never takes initiative.
- Marshals have **trust** in you (0–100). They **object** to orders against their nature, and you answer: trust
  his judgement, insist, compromise, or cancel. They grow **jealous** of each other's glory. There is an **order of
  rank** among them, and a higher man placed under a lower one takes it ill.
- **Standing orders** exist: march to a place, pursue an army, hold, support a friend. They cost 2 actions to give
  (1 for a literal man) and then run by themselves each turn, after the enemy has moved. A hold can carry **one
  if-then** ("if Mack advances, fall back to Bohemia").
- There is **fog of war**: you see enemy corps only near your own corps, scouts and watchtowers. A spy mission
  (3 turns) lifts the fog over one nation's land for 5 turns.
- The Emperor's own corps gives **+10% attack and defence to every friendly corps in his province** — and a marshal
  who fights beside him earns only **half the glory**.
- **Laws** are bought with gold or with the Emperor's authority. France's great one is "the Staff" (9,000 gold,
  300 a turn). Today it gives one more action a turn. Each great power has its own version.
- You **win** by holding 45 "titled" provinces and having the great powers accept the peace at a Congress.
- You can play by clicking or by **typing** ("Ney, attack Mack"; "can Ney reach Vienna?"). Typing is optional.
  The developer has asked three times whether typing is worth keeping.
- The developer's first full playtest ended: "everything feels convoluted and opaque and disconnected".

## 2. The idea

You are the Emperor. You cannot be everywhere. The corps near you, you command by hand — and they fight better
under your eye. Everywhere else you choose a man, tell him what you want, and then live with who he is.

Five parts, meant to work as one:

1. **The desk** — three lines always on screen: THE PEACE (how you win, how far along), THE WAR (what each war is
   for), TODAY (up to three matters that need you now, each a click away).
2. **One line before the day ends** — everything about to go wrong, said at once, including which of your
   provinces an enemy you can see can reach tomorrow. Press End Turn again to go.
3. **His own command** — a bold or careful marshal is given a task, a ground, how boldly, and limits. He then acts
   by his own judgement, once every night, and writes to you each morning.
4. **Orders to the letter** — a literal marshal takes no command of his own. His standing order carries up to
   three if-thens, which he follows exactly.
5. **Typing talks to them** — their names sit by the command line. You ask, adjust, overrule or recall them in a
   sentence, and they answer in their own voice.

## 3. His own command — the rules

**The four parts** (each a short fixed list, so it can be clicked or said):

| Part | Choices |
|---|---|
| Task | **Take** a place · **Hold** ground · **Hunt** a named enemy army · **Guard** a named friend · **Watch** a frontier (scout, report, avoid battle) |
| Ground | One or two provinces (three for a marshal of outstanding command skill — Davout). He keeps to it. |
| How boldly | **Press** · **Steady** · **Safe** — shifts the odds he needs by 1.5 men in 10 either way. A bold man needs 5.5 / 7 / 8.5 men per 10 of the enemy; a careful man 11.5 / 13 / 14.5. |
| Limits (up to two) | "If outnumbered, fall back on X" · "March to the guns" (join any battle in reach) · "Until relieved / for N turns / until X falls / until Ney arrives" · "Spare the country" (no plunder) |

**Who.** A bold or careful marshal whose trust in you is 30 or more. Not a literal man. Not the Emperor. Not an
ally's or a client's commander. Gun commanders may be given Hold or Guard only.

**How many.** One at the start. Two when the Staff is in force. Three with a new law, "the Emperor's
Aides-de-Camp". (If the Staff lapses for want of gold, the cap falls and the lowest-ranked command is withdrawn.)

**What it costs.** 2 actions once, when you give it. After that his one act each night is free. He acts every
single night — more than most of your corps get from your 4 actions — but never more than once. A corps you
favour by hand can do two or three things in a day; his cannot.

**When he acts.** After the enemy has moved, with your other standing orders, highest-ranked commander first.

**How he decides.** By the same decision logic that moves the enemy's marshals today, held to his task and his
ground. He sees only what France can see. Nothing is random and no language model is involved.

**What beats what — the six rungs, top first:**

1. **The law**: treaties, lawful roads (never across neutral land or the sea), a question the game must have answered.
2. **The corps' survival**: a shattered or doomed corps retreats, even off his ground.
3. **Your order of the day**: if you order him by hand, he does that today and not his own choice.
4. **His limits**, in the order you gave them.
5. **His task**, on his ground, at his boldness, in his nature.
6. **His quiet act** when nothing else applies: holding → dig in or drill; taking → close up; hunting → follow;
   guarding → close up; watching → scout.

**"Means to."** Each night after acting he works out what he would do next as things stand. You see it all next
day: a faint arrow on the map, a line on his card, and a part of the day's-end line. It is honest, not binding —
the enemy moves before he does. Whether he keeps to it is his nature (table below), and his letter says why.

**His letter.** Each morning, first in the report: one line in his own voice with his portrait, then a plain line
saying what he did and the cause. His move is replayed on the map with the enemy's.

**His way** (shown on the card before you give the command):

| | A bold man | A careful man |
|---|---|---|
| The enemy's move worsens the odds overnight | Goes in if his odds are still met | Holds, and says why |
| The enemy's move opens a better chance on his ground | Takes it | Keeps to what he meant |
| Past his ground | May follow a beaten enemy **one province out, once per task** — if set to Press, or if his trust is low (30–49). Only into land at war with you. He takes nothing there and is back the next night. | Never |
| Walls | Storms a garrison if his odds are met | Never storms; besieges (1–2 turns) |
| Land he takes | Plunders it (never land that was yours) | Secures it |
| Objects to being given | Hold or Watch with an enemy near | Tasks against bad odds or walls |

**What he never does.** Take ground the task did not name. Cross neutral or allied land, or the sea. Recruit,
build, or spend gold. Answer a letter or a treaty for you.

**How it ends.** Task done: he holds what he took and asks what next (a TODAY row; the command stays his). You
stand him down: the place is free next turn (trust −3 if he was mid-task). He is killed, captured or broken. The
cap falls. Peace with the nation he was sent against.

**Trust and glory.** Trust +5 once per command, if he served three nights or fought under it. A battle fought
alone earns full glory (under the Emperor's eye, half) — so marshals *want* their own command, and the others
grow jealous by rules that exist today. Give a command to a man while a bold marshal who outranks him has none,
and the higher man's view of him drops a step; the card warns first. A marshal who has spent four turns in the
Emperor's shadow already petitions for an independent command; granting it now gives him a real one.

## 4. Orders to the letter — the literal man

- Any standing order of his (hold, march, pursue, support) carries **up to three if-thens**, numbered.
- "If": an enemy comes within reach · he is attacked · he is outnumbered · a named friend is attacked · a named
  place falls · a named friend arrives. "Then": attack · fall back on X · march to X · march to that friend's
  guns · hold · fortify. Any "if" with any "then".
- Each night the lines are checked in order; the first true one fires. **Each line fires once and is then spent.**
- When no line fits, or all are spent, **he stands where he is** and a TODAY row says so. It never stops the game.
- He attacks when a line says attack, whatever the odds. That is the bargain.
- Costs 1 action. Does not count against the cap. Other marshals keep today's rule: one if-then, on a hold.
- The read-back refuses a line that repeats or contradicts an earlier one, and warns of a gap ("nothing here
  covers being outnumbered").

*Why:* until now "never takes initiative" set him apart from nobody, because no marshal took initiative. Now he
is the one man who will never surprise you — and the man for whom what you type is exactly what you get.

## 5. Talking — the typed line's job

- **Open lines.** Names of your commanders and men under orders to the letter sit by the command line. Click one:
  the line starts "Masséna, " with four ready things to say.
- **Ask** (free): "what will you do?" · "what do you see?" · "why did you fall back?" · "can you take Verona?"
- **Adjust** boldness or a limit (free, once per man per day): "press harder" · "until Venice falls".
- **Change** task or ground (1 action).
- **Overrule** for one day (the order's usual price): any ordinary order. The read-back offers "make it his new
  task" beside "send".
- **Stand down** (no actions).
- **The read-back rule.** Before anything is spent the line shows every part it took and names every part it did
  not. Nothing half-understood is half-carried-out.
- With no language model the fixed phrasings work. With one, it only maps freer wording onto the same parts.
- Everything can also be done by a card with pickers. Typing is never the only way.

## 6. The plan and the wing

- **The object of a war**: one place the whole war aims at ("Vienna"), free to set. A sixth task, "serve the
  plan", means "take that object, then hold it"; change the object and every man serving it turns.
- **The Wing**: one commander may be given up to two more corps that march with him and fight where he fights.
  One place of the cap, one Wing at a time, needs the Staff. A higher-ranked man placed under him takes it ill.

## 7. The other side of the hill — the enemy uses the same thing

**One rule for every nation.** Each nation has a hand (its actions) and own commands up to its cap (one at the
start, one more with its own Staff law). Its literal marshals take orders to the letter.

**What changes for an enemy nation.** Today every enemy corps re-decides from nothing every turn. With this:

- The court keeps its main army in hand, as today.
- It gives a command to its best independent man among the rest. The task comes from things the game already
  works out: a frontier facing an enemy in sight → Hold it; an ally's army beside him → Guard it; the war's stated
  object within two marches and the odds met → Take it; otherwise Watch. Boldness comes from the coalition's
  posture.
- He then acts once a night by the same six rungs and the same "way" as your men.
- Its literal marshals (Mack, Buxhowden) get orders to the letter written by their court. **A court without its
  Staff law writes one if-then; with it, three.** So Austria in 1805 writes Mack "Hold Swabia until Kutuzov
  arrives" and nothing about being outnumbered. That is Ulm.
- When its capital is threatened the court recalls its commanders (the recall rule exists today).

**What you can learn** (military orders are fogged; nothing is shown that you have not learned):

- **His nature** — once you have fought him or had full sight of him.
- **His orders** — three ways: your spy mission now also reports each marshal's orders for its 5 turns; beat a
  marshal in battle and you capture a dispatch with his orders; or watch him for three turns and Berthier offers
  a reading in guarded words ("will / may / will not").
- What you learned goes stale if his court changes his orders, and says how old it is.

**Playing against a command.** The same rungs that bind your men bind his:

- A bold man on Press follows a beaten corps one province out → bait him and cut him off.
- A careful man will not storm walls and gives ground before strength → move him by massing; stop him with a fort.
- A literal man does only what is written → learn his orders, then do the thing they do not cover.
- A man guarding a friend marches to that friend's guns → strike the friend to pull him off his post.
- A court recalls its commanders when its capital is threatened → threaten Vienna to empty Italy.

All of this can happen to your men too. The enemy's logic sees your corps, as today; it never reads your orders.

## 8. Rulings on edge cases

1. No command free → the card says so and offers to stand another man down. A place freed is usable next turn.
2. A task against his nature → he objects, with the answers that exist today. "Trust his judgement" takes his
   counter-proposal.
3. No lawful road to the ground → refused at the card. At peace only Hold, Guard and Watch can be given.
4. A marshal who is broken, recovering, wounded (3 turns) or besieging can be given a command; it starts when he
   is fit.
5. One real act a night. Changing posture (stance, leaving works or a square) rides free with it.
6. Two commanders after the same enemy: both may attack, senior first.
7. Friends beside a fight join by today's rules. A man on Hold leaves his post for another's battle only if his
   limits say "march to the guns". He is never asked the "do I march to the sound of the guns?" question that
   standing orders raise today.
8. If the Emperor's corps is in the battle's province it is the Emperor's battle (+10%, half glory).
9. A great undecided battle (50,000+ men) opens a "day of battle", offered to you next morning, as today. For a
   commander's battle, if you leave it, he fights it his own way. You may always take the day yourself.
10. Supply: he shifts within his ground to feed the corps. If his ground cannot feed him he says so and stays.
11. A hunted army unseen for three turns → he stops and asks. The place he was to take is taken by a friend →
    done. His ground is lost → he retakes it if his odds are met.
12. Peace with the nation he was sent against → the command ends that night and the game's existing road-home
    rule walks him out. Land that becomes unlawful to stand on → he leaves by the nearest lawful road and asks.
13. Trust falls under 30 while he holds a command → he keeps it but takes no adjustments ("I know my business,
    Sire"). You can still overrule him by order or stand him down.
14. A commander cannot launch the jealous solo attack that idle bold marshals sometimes make. "Everyone, march"
    and the Staff's army order skip commanders and say so.
15. The three-turn independence a marshal can win after a crisis of trust (exists today) does not count against
    the cap. Granting a petition needs a free place.
16. If a Wing's leader falls the Wing dissolves and its followers show as idle.
17. A letter is written only when something happened or he asks. "Held; nothing seen" is one grey line.
18. A saved game keeps each command, its "means to" and its spent if-thens. Old saves simply have none.
19. With no command given, nothing in the game behaves differently from today.

## 9. What we are least sure of — attack these first

- One act a night: too little, too much, or right?
- The cap of 1 / 2 / 3 for seven marshals.
- Shutting literal men out of commands entirely.
- Bold men plundering by default.
- "Means to" that the man may not keep.
- Whether enemy nations become better opponents with commands, or just slower ones.
- Whether learning an enemy's orders three ways is too easy, too hard, or dull.
- The Wing: three corps on one place of the cap.
- Whether typing now has a job nobody would rather click.
- We chose **no order delay** (no couriers taking turns to arrive). Was that right?
