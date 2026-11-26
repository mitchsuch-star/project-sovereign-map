# Gameplay and Architecture Review — November 25, 2026

> **Asked for:** "It's still not fun and the UX isn't great — do a deep review of the
> gameplay loop and architecture … make the overarching game better like EU4 or Civ,
> though just do research here." Plus four reports from your play: the line goes crazy
> when you click a general; clicks aren't accurate on your ultrawide; you erased Austria,
> kept all of it, then every country joined one coalition; how do you cross into Turkey,
> and the navy is confusing.
>
> **Research only — nothing in the game was changed.** This is the review and a proposed
> plan (§5). The plan waits for your word; until then the plan of record is unchanged.

---

## The short version

**Why it isn't fun yet** — most important first:

1. **The hands don't do what the eye is told.** The box under the cursor names one thing
   and the click does another; the line from a selected general vanishes, jumps and swaps
   its tag between points a few pixels apart. Every other improvement goes through the
   mouse, so this comes first. (§1.1, §1.2)
2. **Conquest is free, then the punishment is a cliff.** You can erase a country and keep
   every province with no peace price, no revolt and almost no cost. Then one France-wide
   number crosses a line and every court with poor relations joins one league at once —
   and every war you declare costs relations with *every* court, so after two wars that
   is all of Europe. (§1.3)
3. **One far goal, no steps toward it.** The desk's only goal is "hold 45 titled provinces,
   then summon the Congress of Paris"; the grading at turn 44 is told only if you type a
   question. There is no ladder of nearer goals with rewards — and the one goal pushes you
   to conquer, which feeds the cliff in point 2. (§2, P1)
4. **A turn is mostly reading.** Four actions for eight marshals, under a stream of reports,
   envoys and other courts' decrees. The parts only this game has — marshals who argue,
   Bold against Careful — drown in routine lines. (§2, P3)
5. **Rules hide until they refuse you** — the sea crossings, closed borders, the 15,000-man
   landing limit, who joins a league — and the refusal often names the wrong way through.
   (§1.4, §2 P4)
6. **Everything is switched on from turn 1.** About 25 systems are live at the start. Civ
   hands you systems by era; EU4 points you at them with missions. (§2, P6)

**Why the last weeks didn't fix it:** the project measures what is easy to measure —
computer-only campaigns on fixed seeds, blind readers looking at screenshots, pinned
wording. Those catch breakage and confusing words, and none of them measures fun. Your own
play is the only fun measure, and it has happened twice (November 18 and now). Meanwhile
each new system has added reading and rules on top of a turn that was never proven fun. (§4)

**What I recommend, in order** — row FUN, before the deploy (needs your word):

1. **FUN-1 the hands** — what the cursor shows is what the click does; a steady line; the
   worst crossing confusion fixed.
2. **FUN-2 conquest with a cost** — a grudge per court, join rules with a stake, an
   "erase this country?" card, land that settles slowly.
3. **FUN-3 goals** — a goal ladder for France, 1805–1807 (Ulm to Tilsit), and the turn-44
   scoreboard on screen.
4. **FUN-4 the turn diet** — the map tells the turn, the report shrinks to a few lines,
   systems wake up when they matter.
5. **FUN-5 the sea made plain** — straits that work like EU4's.

After each one you play for 20–30 minutes with one question to answer. Hold the deploy
until you call it fun. (§5)

---

## 1. Your four reports

### 1.1 "When I click on generals the line goes crazy if I move the mouse around"

**What the line is.** Once a general is selected the map is in order mode. Each time the
cursor reaches a new province or piece, the map draws a dashed road from his feet to it,
with a tag at its head (place, price, turns, what happens there):
`map_renderer_base.gd:3696` (`_order_hover_tick`) → `main.gd:12088`
(`_on_map_order_hover`) → `main.gd:12105` (`_show_ghost_for`).

**Reproduced** on the real client at your setup (5120×1377 window, Interface Scale 1.8)
with Soult selected, eight resting points (frames:
`C:\Users\User\AppData\Local\Temp\claude\1bd395101ae53e89\6f3af8b9-d7d2-4cf7-ab8b-97648da555cd\scratchpad\repro\run1\frames\`,
0004–0012). The line always ended at the province under the cursor — it never pointed at
the wrong place — but:

- **It vanishes over pieces and over his own ground.** Over Mack, the line disappeared and a
  big hover box (about 220×80 px) covered the stacks; back near Soult, no line at all.
  In code: over a piece there is no row in the reach table, so the line is cleared
  (`main.gd:12135`) until the server's quote comes back.
- **Two points 21 px apart give two different pictures** — a "Move · arrives now" line to
  Rhineland, then no line and a red "Attack Mack" tag (frames 0011 → 0012).
- **The tag swaps sides.** It sits on the side the road's last leg points, so it jumps
  left, below, up-right between frames (`map_order_layer.gd:633-635`).
- **Roads detour without saying why on the road itself.** Soult's road to Vienna dips south
  through Switzerland and the Tyrol and back up through Bavaria, because Mack blocks
  Swabia (frame 0007). On a whole-Europe view it reads as a zigzag.
- **Two road sources.** The first road drawn comes from the reach table; 0.15 s after the
  cursor rests the client fetches an exact quote and redraws from it (`main.gd:11946`,
  `:12100`). Where the two differ, the line changes a moment after you stop.
- **The boxes take turns with it.** Inside reach the province's hover box hides and the tag
  shows; outside reach the line goes and the box returns (`map_renderer_base.gd:4407-4420`).

On your screen a province is a few dozen pixels wide at the whole-map view, so an ordinary
mouse movement crosses several provinces a second and each crossing redraws a whole
multi-leg road, moves the tag and swaps the boxes. In continuous motion that is "crazy".

**Fix (FUN-1):** one road source, drawn when the cursor rests; never blank the line while
the next loads (keep the last one, faded); over an enemy, the attack road at once; over
your own piece, a "Select Davout" tag; the tag on one fixed side of the cursor; the hover
box always off while a general is selected (the tag carries the province name); a detour
says so on the road ("goes round Mack in Swabia").

### 1.2 "Clicks aren't accurate on ultrawide"

**No constant offset found.** The arithmetic that turns your mouse position into a map
position, and map positions into drawn lines, agrees with itself at any Interface Scale
(`map_renderer_base.gd:4425`, `map_order_layer.gd:291`). On the real client at your setup,
clicks on provinces all landed (Bavaria, Austria, Hesse), and a click on Masséna's figure
selected him.

**What is wrong is that the cursor promises one thing and the click does another:**

- **Hover names a piece; the click opens the province under the cursor.** Pointing at Mack's
  name plate showed Mack's box, and the click opened Rhineland — the province the plate
  happened to sit over (frame 0018). Name plates sit 25–35 px off their figures, often
  over another province. For your own pieces the click selects the man; for anyone
  else's it falls through to the province under the cursor
  (`map_renderer_base.gd:3479-3506`).
- **In a mixed stack the front piece decides.** Clicking Bernadotte's figures, where
  Bavaria's Deroy stood in front, opened the Bavaria panel — the box had named Deroy, an
  ally's piece the click can't select (frame 0002).
- **Targets are small.** A stack of two or three figures is about 45×30 logical px on your
  screen; a figure about 25 px tall. A click within 30 px picks a piece — but only while
  no general is selected (`map_renderer_base.gd:2382-2392`, the PW-R19 note at
  `:4520-4532`). With one selected, a near miss on another general becomes an order for
  the province under him.
- **One link has never been tested.** Every test of clicking at your setup injects clicks
  already divided by your 1.8 scale (`tools/dd_b_client.gd:430, 754, 779` —
  `push_input(ev, true)`), skipping the step where Windows' real mouse position becomes the
  game's. That step is Godot's own and normally right, but nobody has checked it on your
  monitor.

**Fix (FUN-1):** one rule — *what the box under the cursor names is what the click does*
(a click on Mack's plate is Mack: his card, or with a general selected the attack card);
in a mixed stack your own piece is the one a click picks; bigger targets at the
whole-map view; the near-miss grab kept for selecting your own generals; one driven test
with real window-level input at 5120×1377 / 1.8 (`Input.parse_input_event` with window
coordinates, not `push_input` with logical ones).

### 1.3 "I beat Austria by eliminating them, kept all the land, then a coalition of every country formed"

**What the code does** (each read and checked):

- **Erasing a country is the cheapest way to win land.** Taking a court's last province
  erases it (`world_state.py:5913-5941`). A rule makes a falling court sign a peace and
  get its homeland back — but it skips the player: "erasing a court outright stays the
  hegemon's prerogative" (`settlement_third_party.py:1159-1187`). No treaty, no war-score
  price, no limit.
- **Conquered land costs almost nothing.** A province you take starts "Hostile" and pays
  nothing, then climbs to full pay in about 10 turns, about 5 with a garrison
  (`region.py:394-403`). No revolt, no upkeep, no limit on how much you hold.
- **The push-back is one France-wide number.** Each province you take adds 2, a capital 15,
  a won battle 3 or 5 (`world_state.py:5846-5853`). The extra alarm a computer-run
  conqueror raises doesn't apply to you (`alarm.py:112-127`). At 60 a league starts
  brewing; at 80 it forms on the spot (`coalition.py:40-46`). The 1805 start is already
  at 68–70.
- **Who joins: anyone below −10 relations with you** — no check for distance, stake, size or
  alliance (`coalition.py:1887-1928`).
- **Every war you declare costs −15 relations with every court in Europe** (−7 with a
  reason for war) and −30 with the target (`diplomacy.py`,
  `declaration_relation_penalties`). Two wars without a reason put every court below −10.
  That is why every country joined, including ones with no stake.
- **Even a quiet France gets a league.** Once France leads a third of Europe's power and has
  fought no battle for 16 turns, the alarm stops falling and then climbs +3 a turn to the
  brewing line ("the Armed Peace", `coalition.py:88-128`).
- **The warning exists, but not where you act.** A forecast names who would march and when
  (the Balance of Europe tab, the dispatch, the desk — `coalition.py:4695-4808`); nothing
  warns you on the order that erases Austria.

**What EU4 does instead** (research, §3): each conquest adds a grudge per country — larger
for neighbours and for the same culture or religion — that fades by about 2 a year; a
country joins a coalition only when its grudge passes a line *and* it dislikes you; your
allies, subjects and countries under truce can't join; the peace screen shows, before you
sign, which countries your demands would push over the line; land costs war score, so a
total conquest takes several wars; and overextension, unrest and coring make a big gain a
burden for years.

**Proposal (FUN-2)** — keep the drama, make it gradual and visible:

1. **A grudge per court** in place of the single number: each capture adds to every court's
   grudge, scaled by distance and stake (Prussia minds Saxony and Hanover, Russia minds
   Poland, everyone minds a capital); grudges fade; shown as a map mode ("Who fears you")
   and in each court's row.
2. **Join rules:** a court joins a league only when its grudge passes the line *and* it
   borders you or holds a stake; never your allies, vassals or courts under truce; at
   least three members; a member can be peeled off (truce, gifts, land handed back).
3. **A declaration angers the target and its friends**, not every court in Europe.
4. **"Erase this country?" card:** when an order would take a country's last province, or
   push a court over the line, the order card says so plainly — who would join and in
   about how many turns — and offers the alternative (offer peace now and keep X).
5. **Land has a price:** new provinces stay unsettled longer (pay less, give no recruits,
   need a garrison or risk revolt — history with teeth: the Tyrol in 1809, Spain in 1808);
   peace terms price provinces in war score, so taking everything is a choice, not the
   default.

### 1.4 "How do I cross into Turkey from the Balkans? Naval stuff is confusing"

**How to do it today** (checked by running the game's own code with Murat at 14,000 men):

1. Be at war with the Ottomans. At peace their border is closed: "Open borders or higher
   required."
2. Bring a corps of **15,000 men or fewer** to a coast he may sail from. Napoleon cannot
   sail. *(Corrected November 25, 2026, while building FUN-1: a corps may sail from an
   enemy or foreign coast he stands on — Rumelia while it is still the Porte's — or from
   one of our dockyards; once Rumelia is ours and joined to France by land it is "home
   soil", and from home soil a landing sails only at a dockyard. The nearest shore he can
   sail from is then a march or two away — Albania, for instance.)*
3. Do **not** order a march into Constantinople — it is refused. Order a **landing**: type
   "land Murat in Constantinople", or use the landing button on the province card (FUN-1
   puts it on the refused march's card too, dimmed with the reason when he cannot sail
   from where he stands).
4. Confirm the odds card ("slip past unseen 60 times in 100 …").
5. Once ashore, Anatolia is an ordinary march.

**Why it is confusing:**

- **The strait isn't where you look for it.** The map's sea crossing is Rumelia ↔
  Constantinople; Constantinople ↔ Anatolia is plain land (`europe.json` sea links:
  Region_083 – Region_105). You look for the crossing at the edge of Asia, and it sits
  before the city instead.
- **The border wall hides the sea wall.** At peace you only see "Open borders or higher
  required" — no button and no hint how to get it. The sea rules appear only after you
  have declared war.
- **The refusal names the wrong fix.** It says "break the fleet that covers the passage"
  even when your fleet already outnumbers the Ottoman one 3.5 to 1. Beating the fleet
  doesn't help: an enemy shore must be landed on, never marched onto (`naval.py`, the
  landing rule near lines 1960–1975).
- **Britain shuts a strait it has nothing to do with.** Once you hold Rumelia, Britain's
  blockade fleet (100 ships) counts as covering the Bosphorus, and the march is "shut"
  (`naval.py:1801`, `_fleet_covers_link`).
- **The advice is jargon with no button.** "Build or pool a fleet to contest the passage"
  — "pool" means allies' fleets counted with ours, and no button offers either
  (`naval.py:1991-2010`). *(Corrected while building FUN-1: it is not a dead end — every
  dockyard builds into France's ONE fleet, so a yard in Provence helps at the Bosphorus
  too; FUN-1 says so in plain words.)*
- **Five words for one thing** — barred, defended shore, landing, shut, contested — plus
  "effective", "pooled", "diversion", "window" unexplained; the odds card names Spain and
  Holland, which have nothing to do with the Bosphorus.
- **The help is wrong.** The Codex says an expedition sails "from a friendly dockyard
  province" (`codex_terms.gd:49-50`); it can embark from any coast you hold.
- **Green at peace, refused anyway.** The province window's sea line says the crossing is
  open (it is, at sea) while the march is refused at the border.

**Proposal:**
- *Quick, in FUN-1:* a refusal always names the one way that works, as a button ("Land a
  corps of 15,000 or fewer — Lannes (12,000) can go"); at peace, "Ask the Porte for open
  borders" as a button; the Codex corrected. *(Built in FUN-1. The blockade that covers
  a strait in another sea moved to FUN-5 by FUN-1's plan — open row FUN1-11, its strict
  pin `tests/test_fun5_the_sea_made_plain.py`.)*
- *The real fix, FUN-5:* **straits like EU4's** — a short strait (the Bosphorus, the
  Dardanelles, Messina, the Sound) is a land link with a strait icon, closed only while an
  enemy fleet commands that sea; armies cross it like a river. Long sea routes stay
  landings. The Bosphorus moves to Constantinople ↔ Anatolia. One sea map mode: who
  commands each sea, which crossings are open, and why.

---

## 2. The gameplay loop — what a turn is today

**A turn:** the morning report, the desk (THE PEACE / THE WAR / TO DECIDE), letters and
envoys; then **4 actions** (`nation_config.py:532`) shared among **8 marshals**, Napoleon
included — a move costs 1 or 2, a march order 2 — so two to four marshals get an order and
the rest wait, follow standing orders or act on their own; then End Turn, and the enemy's
moves play on the map. Turns are half a month: turn 44, the graded end, is about June 1807.

**What it feels like with nobody at the wheel** — six turns of the hands-off driver
(historical seed, `tools/playtest_driver.py --turns 6`): every turn one to three courts
send envoys asking for open borders or a pact (Prussia, the Ottomans, Portugal, Denmark,
Saxony, Hesse, the Papal States), each a letter to answer; the log fills with other
courts' decrees ("Russia decrees the Remounts for 8 turns"); Archduke Charles attacks
Masséna three times in one turn for three stalemates.

**At your setup** (frame 0007 of the reproduction): the left third of the screen is
panels — the command panel, the desk's paragraphs, a selected general's card with eleven
buttons and two lines of help — and the map is a strip 765 logical px tall showing Europe
from Cornwall to Anatolia, with name plates overlapping pieces and each other.

### The problems, most important first

**P1 — One far goal, no steps toward it.** The desk's goal is "Win the peace: hold 45 titled
provinces … then summon the Congress of Paris. You hold 35." The grading at turn 44 is
told only if you type a question about your goal (`first_contact.py:294-312`). Nothing in
between — no "take Vienna before Russia arrives", no reward for getting there. EU4 has
mission trees and Civ has victory types, eras and quests for exactly this: the player
always knows the next thing worth doing. Here the one goal says "more provinces" and the
league punishes provinces, with nothing to steer between them.

**P2 — Conquest is free; the push-back is a cliff.** §1.3.

**P3 — A turn is mostly reading.** Four actions against a flood of text. What only this game
has — marshals who argue, natures that clash — is buried among routine lines. In Civ a
turn is a handful of decisions, each with an instant visible result; in EU4 alerts sit as
icons and the map shows what happened.

**P4 — Rules you meet only when they refuse you.** The sea crossings, closed borders, the
15,000-man limit, the defended shore, who joins a league. EU4's answer is a tooltip on
every number and a preview before every costly act.

**P5 — The hands.** §1.1–1.2. First in the build order, because every other change reaches
you through the mouse.

**P6 — Everything at once.** The 1805 scenario switches on about 25 systems from turn 1:
statecraft, the Questions, the Awakening, crowns, agendas, formable nations, reforms,
doctrines, navies, imperial designs, moments, war plans, authority, affairs of state,
jealousy, the Order of the Marshalate and more. Civ unlocks systems by era; EU4's
missions point you at them one at a time. Nothing needs cutting — they can wake up when
they matter.

**And the hook is buried.** The pitch is "talk to your generals and they talk back". That is
now one system among dozens, and `docs/VISION.md` still says "Players don't click armies.
They type commands" — no longer true. The game needs one page that says what a turn is
for.

**What a turn could feel like after row FUN** (illustration, not a spec): *Turn 7, early
January 1806. Three icons on the map mark what happened — a battle at Ulm, Prussia
mobilising, an envoy waiting. The goal ladder reads "Next: take Vienna before the
Russians arrive — 2 of 3 steps; reward: Austria sues for peace." The "Who fears you" mode
shows Prussia at 41 of 50: one more capital and she joins. Ney wants to storm the bridge;
Davout wants to wait for Soult. You choose, and the map shows what came of it.*

---

## 3. What EU4 and Civ do that this game should borrow (research)

Ranked for a game about commanding marshals:

1. **A goal ladder.** Something that finishes this turn, something in five to ten turns,
   something for the campaign. EU4: country-specific mission trees with rewards — Paradox
   found country-specific missions more fun than generic ones. Civ: victory types, eras,
   quests; builds and research finish on different turns, so something always completes
   soon (the "one more turn" pull). → FUN-3.
2. **Push-back you can see coming, per country.** EU4's aggressive expansion: a grudge per
   country by distance, culture and religion, fading about 2 a year; a coalition only past
   a line and with a dislike, at least four members, never allies or truces; the peace
   screen previews who goes over the line. Civ VI shows the warmonger cost before you
   declare, smaller with a reason for war, and adds war weariness. → FUN-2.
3. **Land costs attention.** EU4: coring, overextension, unrest, separatism. Civ: loyalty and
   amenities. A big gain is a burden for a while. → FUN-2.
4. **Every number says why; every costly act shows its price first.** Paradox's nested
   tooltips let them "explain anything without writing a novel in each tooltip" (their
   Victoria 3 UX diary); EU4 previews the grudge on the peace screen; Civ previews the
   warmonger cost. → every refusal names the way through; every card previews.
5. **The map is the main report.** Map modes (political, diplomatic opinion, military, the
   sea), icons where things happened, an outliner listing your armies and their orders.
   → FUN-4 (the turn on the map; a "Who fears you" mode); FUN-5 (a sea mode).
6. **Unlock gradually.** Civ by era and technology; EU4's missions double as tutorials.
   → FUN-4.
7. **Simple, visible crossing rules.** EU4: a strait an enemy fleet can block. Civ:
   embarking, with the risk visible. → FUN-5.
8. **Characters make the drama.** Civ's leader agendas make each rival predictable enough
   to plan around. Here: Bold, Careful and To-the-letter should create clashes you see
   coming — the game's own hook, put at the centre of the turn.
9. **Sid Meier:** a game is "a series of interesting decisions"; "double it or halve it";
   "one good game beats two great ones" — sub-games competing for attention hurt each
   other. **Soren Johnson:** the player should have the fun, not the computer — so a
   marshal acting on his own must always say why and leave room to step in.

**Sources:** Sid Meier's lessons —
https://www.gamedeveloper.com/game-platforms/analysis-sid-meier-s-key-design-lessons ·
Soren Johnson's writings — https://www.designer-notes.com/writings · "Sid's Rules" —
https://forums.civfanatics.com/threads/sids-rules.319860 · EU4 mission diaries —
https://forum.paradoxplaza.com/forum/threads/eu4-development-diary-19th-of-march-2019.1161211/page-2
and https://admin-forum.paradoxplaza.com/forum/developer-diary/eu4-development-diary-14th-of-may-2019.1176867
· Victoria 3 UX diary (nested tooltips) —
https://forum.paradoxplaza.com/forum/developer-diary/victoria-3-dev-diary-29-user-experience.1506484/page-5
· EU4 aggressive expansion and coalitions (a guide; the official wiki would not load) —
https://www.fandomspot.com/eu4-handling-aggressive-expansion-coalitions/ · Civ VI
diplomacy and war weariness — https://civilization.fandom.com/wiki/Diplomacy_(Civ6),
https://civilization.fandom.com/wiki/War_weariness_(Civ6) · Civ V embarkation —
https://civilization.fandom.com/wiki/Embarked_(Civ5). Figures from guides and forums
(EU4's "about 2 a year", "at least four") should be checked against the game before they
are used as numbers here.

---

## 4. Architecture and process — why fun isn't improving

**The size, measured today:**

| | Files | Lines |
|---|---:|---:|
| Backend (Python) | 204 | 355,166 |
| Client (GDScript) | 86 | 87,777 — `main.gd` alone 17,490 |
| Tests | 1,020 | 617,414 — 43,793 tests; the commit gate 16–26 min |
| Docs (Markdown) | 1,304 | 897,115 |

Largest backend files: `world_state.py` 18,473 · `diplomacy.py` 17,791 ·
`combat_executor.py` 15,849 · `main.py` 9,981 (68 endpoints). 135 test files read the
client's source text. `CLAUDE.md` is 62 KB and at its cap. 95 commits this month.

**What that means:**

1. **The measures don't measure fun.** The band and the story classes are computer-only
   campaigns on fixed seeds; blind readings are strangers reading screenshots; pins check
   wording and code shape. They catch breakage and confusing words — keep them for that —
   but a game can pass every one and still be dull. Your play is the only fun measure.
2. **Every change carries a heavy tail** — spec, gate, pins, seed sweeps, records, the
   20-minute hook. Right for a release; wrong for finding fun, which takes fast, rough tries
   with a player in the loop.
3. **Systems keep landing on an unproven core.** Each new system was measured as "alive" in
   computer-only runs, and each added reading and rules for the player.
4. **`main.gd` is the drag on UX work.** One 17,490-line script runs the command line, every
   popup, the order flow, directives and screens; the order flow alone carries a nest of
   waiting flags (`_order_go_pending`, `_order_card_wait`, `_order_dwell`,
   `_order_quote_pending` …). Every UX fix touches it.
5. **More is written about the game than the game itself** — more lines of docs than code
   and client together — and session time goes into records.

**Recommendations:**

- **A fun loop.** Each session ends with a playable build and one question for you; you play
  20–30 minutes; the next session starts from your answer. Keep the measures only where
  they protect something you liked.
- **No new systems until a turn is fun** — a pause, not a cut (needs your word).
- **Wake systems up when they matter** — progressive unlock; nothing removed.
- **Split `main.gd` before the deploy.** The planned split (S16) sat after the deploy; it now
  follows row FUN (FUN-1's plan measured the order flow's share and kept it out of FUN-1).
- **A fast lane for tests inside a session** — the tests touching what changed, a few
  minutes — so one session can hand you several builds. Your full gate still runs at every
  commit ("the gate stays, the wait goes").
- **One page of design pillars** — what the game is, what a turn is for, how you win —
  replacing `VISION.md`'s outdated lines; every session reads it first.

---

## 5. The plan — proposed, waiting for your word

**Row FUN — "make it fun", before Session H (the deploy).** Each session ends with a build
you play for 20–30 minutes and one question you answer; the STATUS line, the owner row in
`PRE_DEPLOY_PLAN.md` §2 and each behaviour test are written the day you adopt the row.

| Session | What changes for you | Done when | Behaviour test |
|---|---|---|---|
| **FUN-1 the hands** | What the cursor shows is what the click does; the line steady (never blank, never lying, tag on one side); your own piece wins a mixed stack; bigger targets; crossing refusals name the way through, with a button; "ask for open borders" button; the Codex corrected; the fast test lane. *(By FUN-1's approved plan: the `main.gd` split moved to S16, right after row FUN; the blockade-over-a-strait rule moved to FUN-5.)* | A driven test with real window-level input at 5120×1377 / 1.8 clicks every piece and province it aims at and the action matches the hover box every time; the line never blanks between two resting points; your play: "the clicks work" | `tests/test_fun1_the_hands.py` |
| **FUN-2 conquest with a cost** | A grudge per court; join rules with a stake; declarations anger the target and its friends only; the "erase this country?" card; land settles slowly and can revolt; peace terms priced in war score | Erasing Austria shows its price before the click; on 10 seeds no league member lacks a border or a stake; your play: "I saw it coming" | `tests/test_fun2_conquest_with_a_cost.py` |
| **FUN-3 goals** | France's goal ladder — about 12–15 authored goals from Ulm to Tilsit, with rewards and branches (peace with Britain, partition Austria, the Rhine, Prussia, Poland); the turn-44 scoreboard on the desk | Fresh readers name the next goal on each of the first ten turns; your play: "I know what I'm aiming for" | `tests/test_fun3_goals.py` |
| **FUN-4 the turn diet** | The turn told on the map (icons where things happened); a report of at most five lines; envoys folded into one list; systems wake up when they matter; a "Who fears you" map mode | On the hands-off run a typical turn shows ≤ 5 report lines and ≤ 1 popup; your play: "the turn reads fast" | `tests/test_fun4_turn_diet.py` |
| **FUN-5 the sea made plain** | Straits as river crossings, closed only by an enemy fleet in that sea; strait icons; the Bosphorus at Constantinople ↔ Anatolia; a sea map mode; landings only for real voyages; a blockade covers only the straits of its own seas (FUN1-11, moved here from FUN-1) | A corps crosses the Bosphorus at war with no enemy fleet in that sea; Britain's blockade no longer shuts it once France holds Rumelia; every closed crossing says why on hover | `tests/test_fun5_the_sea_made_plain.py` (opened by FUN-1 with FUN1-11's strict pin) |

If you would rather have fewer sessions, FUN-3 and FUN-4 can merge.

**The deploy:** I recommend holding Session H until you have played a FUN build and called
it fun. Row TU (the tutorial rewrite) moves after row FUN, so the tutorial teaches the game
as it will be.

**Nothing is cut.** Every system stays in the game; FUN-4 decides when each wakes up, and
anything you want on from turn 1 stays on.

---

## Appendix — FUN-1's brief, pre-decided

For the session that builds FUN-1 once you adopt row FUN (Plan Mode first, as you prefer).

> **Superseded by FUN-1's approved plan (November 25, 2026)** where they differ: the
> order-mode grab is our own pieces only at 18 px (selection mode keeps 30 px for any
> piece); the line's road is the instant reach road for provinces and enemies, fading only
> while a road is coming; step 5's blockade change moved to FUN-5; step 6 (the split) moved
> to S16, right after row FUN — measured at ~925–1,400 lines, ~330 references and 14–20
> pinning test files, with nothing for you to see.

1. **Reproduce with a real mouse first.** A driven test at 5120×1377 / Interface Scale 1.8
   that feeds window-level input (`Input.parse_input_event` with window coordinates) —
   never `push_input(ev, true)` — and records, for each point, what the hover box named and
   what the click did. It fails today on Mack's plate (box: Mack; click: Rhineland) and on
   the Bernadotte/Deroy stack (box: Deroy; click: the Bavaria panel).
2. **One rule for the cursor:** what the box names is what the click does. A plate or a
   near-miss that names a piece makes the click that piece's (his card; with a general
   selected, the order on him). In a mixed stack your own piece is the one named and
   clicked. Forks decided: the near-miss grab (30 px) stays for selecting your own
   generals in order mode as well; on open ground in order mode the click is the order,
   as now.
3. **The line:** one road source — the server's quote, fetched at rest (the 0.15 s dwell
   stays); the last road stays drawn, faded, until the next arrives; over an enemy the
   attack road; over your own piece no road and a "Select <name>" tag; the tag always
   right of the cursor, flipped only within 200 px of the screen's right edge; the
   province hover box off while a general is selected; a detour named on the tag ("goes
   round Mack in Swabia").
4. **Targets:** at the whole-map view a piece's hit box is at least 32×32 logical px.
5. **The crossing, quick half:** the landing refusal offers the landing as a button and
   names a corps that fits; the "break the fleet" advice is said only where beating the
   fleet would open the crossing; at peace, "Ask the Porte for open borders" is a button
   (Talleyrand's existing proposal); the Codex's expedition line corrected (any coast you
   hold). *(The blockade's own seas moved to FUN-5 — open row FUN1-11.)*
6. **The split:** the map-order code (selection, ghost road, quotes, the order card's
   waiting flags) moves out of `main.gd` into its own script, behaviour unchanged, before
   steps 2–3 touch it.
7. **The fast lane:** a command that runs the tests touching the changed files in a few
   minutes, for builds inside the session; the full gate still runs at the commit.
8. **Done when:** the step-1 test passes at your setup and at 1920×1080 / 1.0; the line
   never blanks between two resting points on the eight-point sweep of this review; your
   own 20-minute play answers one question — "do the clicks and the line behave?".
