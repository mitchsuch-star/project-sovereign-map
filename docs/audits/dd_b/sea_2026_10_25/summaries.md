```
#0000  boot  ->  ok
  (the title screen, a first launch)
view: <run>\frames\0000_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=['scale_card'], region_panel=no, other=['main_menu']
── TitleBlock (layer 0) ──
   ANNO 1805 · EUROPE IN THE BALANCE
   INK & IRON
   The Campaigns of Napoleon
── StatusLine (layer 0) ──
   ✓ The war office answers.  ·  127.0.0.1:8006
── PaintingCaption (layer 0) ──
   François Gérard — The Battle of Austerlitz, 1805  ·  public domain
── VersionLine (layer 0) ──
   Ink & Iron — 0.1.0 early build
── ScaleCard (layer 0) ──
   CAN YOU READ THIS COMFORTABLY?
   Ink & Iron sized its interface for this screen. Drag the slider until the lines below read easily from where you sit — every window, ledger and pop-up follows. Settings → Interface changes it later.
   THE SCHOOL OF WAR   1 of 20   ·   Turn 1 — Late September 1805
   Sire — Austria has pushed two corps over the Iller while her main army musters at Vienna. Before orders, knowledge.
   Turn: 1    Actions: 4/4    Admin: 2/2    Gold: 900    Inf: 80,000
   140%
   For this screen the derived size is 140%. A chosen size is kept; 'Size for this screen' returns to the derived one.
   controls: [slider 1.4 of [0.75, 3.0], track x 1571..2017 at y 573]  [Size for this screen]  [Looks right]
── MenuColumn (layer 0) ──
   controls: [Begin the 1805 Campaign]  [The School of War — a guided campaign]  [The School of War — The Table (a guided peace)]  [Continue](disabled: No saved campaign yet)  [Load a Campaign…](disabled: No saved campaign yet)  [Settings]  [Quit to Desktop]
```

```
#0001  look  ->  ok
  (a fresh frame)
view: <run>\frames\0001_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=['scale_card'], region_panel=no, other=['main_menu']
── TitleBlock (layer 0): unchanged
── StatusLine (layer 0): unchanged
── PaintingCaption (layer 0) ──
   Jacques-Louis David — Bonaparte Crossing the Alps  ·  public domain
── VersionLine (layer 0): unchanged
── ScaleCard (layer 0): unchanged
── MenuColumn (layer 0): unchanged
```

```
#0002  click Looks right  ->  ok
  (clicked at (1960, 669))
view: <run>\frames\0002_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=[], region_panel=no, other=['main_menu']
── TitleBlock (layer 0): unchanged
── StatusLine (layer 0): unchanged
── PaintingCaption (layer 0) ──
   Ernest Meissonier — 1807, Friedland  ·  public domain
── VersionLine (layer 0): unchanged
── MenuColumn (layer 0): unchanged
```

```
#0003  click Begin the 1805  ->  ok
  (clicked at (490, 439))
view: <run>\frames\0003_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+828 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) ──
   controls: [icon: Zoomed out as far as the map goes — the whole theatre is in  @(1794,992)](disabled: Zoomed out as far as the map goes — the whole theatre is in view)  [icon: The whole theatre is already in view @(1828,992)](disabled: The whole theatre is already in view)  [icon: Zoom in  (+) @(1862,992)]
── command window, new lines ──
   New campaign ready.
   New campaign started. Autosave refreshed.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 1
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+828 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 44% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Mack
   • Davout, march to Lorraine
   • recruit infantry in Rhineland — 741g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (G) shows its strength and its flaw.
   The Emperor's Designs — I The Protector of the Rhine, II The Crowns of Italy, III The Continental System: one proclamation decides what the Empire is for, and it cannot be undone. In the Cabinet: F1 → The Emperor's Designs.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
   • "what if Ney attacks Mack" — free: it names who marches with him before you commit
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1838,471)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,645)
```

```
#0004  click BLOCKADED  ->  ok
  (clicked at (2974, 18))
view: <run>\frames\0004_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 948 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late September 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire: 40,000 men on the Channel coast, 2 turns at war with Britain, stage a descent — no order; a march out resets the count. Her blockade on you lifts; a won Diversion can open the Strait for up to 2 turns …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0005  scroll 1800 600 down 8  ->  ok
  (scrolled down 8 at (1800, 600))
view: <run>\frames\0005_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 461 of 947 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late September 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire: 40,000 men on the Channel coast, 2 turns at war with Britain, stage a descent — no order; a march out resets the count. Her blockade on you lifts; a won Diversion can open the Strait for up to 2 turns …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0006  scroll 1800 600 down 10  ->  ok
  (scrolled down 10 at (1800, 600))
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 925 of 949 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late September 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire: 40,000 men on the Channel coast, 2 turns at war with Britain, stage a descent — no order; a march out resets the count. Her blockade on you lifts; a won Diversion can open the Strait for up to 2 turns …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0007  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0008  type what can I do about the navy  ->  ok
  (typed and Enter)
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok The fleet musters 45 sail at readiness 70, guarding home waters — pinned in port by Britain, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 3 crossings shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing that touches our own coast; Blockade the enemy closes an at-war court's ports where our sail outmatches hers 1.25 to 1 — her trade halved — and leaves our own coast unguarded.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1653 of 1653 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+828 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what can I do about the navy
   The fleet musters 45 sail at readiness 70, guarding home waters — pinned in port by Britain, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 3 crossings shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing that touches our own coast; Blockade the enemy closes an at-war court's ports where our sail outmatches hers 1.25 to 1 — her trade halved — and leaves our own coast unguarded.
map: unchanged (53 labels)
```

```
#0009  type what can I do  ->  ok
  (typed and Enter)
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok These orders would be carried out today, Sire:
  Ney, attack Mack
  Davout, march to Lorraine
  Soult, fortify
  recruit infantry in Rhineland — 741g for 3,000 men under Davout
  build supply depot in Rhineland — 300g
Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
For any matter of state, press F1 for the Cabinet.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1367 of 1367 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+828 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what can I do
   These orders would be carried out today, Sire:
   Ney, attack Mack
   Davout, march to Lorraine
   Soult, fortify
   recruit infantry in Rhineland — 741g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
map: unchanged (53 labels)
```

```
#0010  type Soult, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. "Soult, march to Flanders." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2030 of 2030 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+828 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, march to Flanders
   Soult begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. "Soult, march to Flanders." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Napoleon(1752,436)  Lannes(1800,497)  Murat(1825,471)  Soult(1683,440)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1685,411)  10k(1910,645)
```

```
#0011  type Napoleon, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. (1 AP — the Emperor commands in his own name.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2141 of 2141 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   800 (+828 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, march to Flanders
   Napoleon begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Lannes(1800,497)  Murat(1825,471)  Soult(1683,440)  Napoleon(1706,466)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1730,420)  10k(1910,645)
```

```
#0012  type Ney, fortify  ->  ok
  (typed and Enter)
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['objection'], region_panel=no
reply: ok Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Mack at Swabia instead.)
── ObjectionDialog (layer 108) ──
   NEY'S CONCERN
   "Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Mack at Swabia instead.)"
   Personality: Aggressive
   Trust: 75 (Reliable)
   Track record: Neutral
   Authority: 100
   controls: [Trust Ney: attack Mack at Swabia (+3 trust)]  [Proceed as Ordered (2 AP — he must first go defensive, -10 trust)]  [Compromise: adopt AGGRESSIVE stance (+3 trust)]  [Cancel the Order (no cost)]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2251 of 2251 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   800 (+828 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Ney, fortify
   ⚠ Marshal Ney raises concerns...
map: unchanged (53 labels)
```

```
#0013  click Cancel the Order  ->  ok
  (clicked at (2015, 640))
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2340 of 2340 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   800 (+828 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► You withdraw the order.
   The order to Ney is withdrawn, Sire — nothing is spent.
map: unchanged (53 labels)
```

```
#0014  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!

Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -274g | Upkeep: -2654g (incl. 212g over-limit, 774g Grande Armée, 204g campaign pay) | Other: +1295g | Net: +648g | Treasury: 1,448g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 136 px] ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 4,696 casualties, 49,304 remaining /     Massena: 5,491 casualties, 36,509 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Archduke Charles: "France pays …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2231 of 2233 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,448 (+922 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Mack — Swabia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Mack
   • Davout, march to Lorraine
   • recruit infantry in Rhineland — 741g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (G) shows its strength and its flaw.
   The Emperor's Designs — I The Protector of the Rhine, II The Crowns of Italy, III The Continental System: one proclamation decides what the Empire is for, and it cannot be undone. In the Cabinet: F1 → The Emperor's Designs.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
   • "what if Ney attacks Mack" — free: it names who marches with him before you commit
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► what can I do about the navy
   The fleet musters 45 sail at readiness 70, guarding home waters — pinned in port by Britain, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 3 crossings shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing that touches our own coast; Blockade the enemy closes an at-war court's ports where our sail outmatches hers 1.25 to 1 — her trade halved — and leaves our own coast unguarded.
   ► what can I do
   These orders would be carried out today, Sire:
   Ney, attack Mack
   Davout, march to Lorraine
   Soult, fortify
   recruit infantry in Rhineland — 741g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
   ► Soult, march to Flanders
   Soult begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. "Soult, march to Flanders." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
   ► Napoleon, march to Flanders
   Napoleon begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
   ► Ney, fortify
   ⚠ Marshal Ney raises concerns...
   ► You withdraw the order.
   The order to Ney is withdrawn, Sire — nothing is spent.
   ► end turn
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -274g | Other: +1295g | Upkeep: -2654g | Net: +648g
   Treasury: 1,448g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,461 troops
   Supply shortage at Tyrol: Archduke John loses 593 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1868,478)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Lannes(1800,497)  Murat(1825,471)  Soult(1683,440)  Napoleon(1706,466)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1755,420)  12k(1684,411)  10k(1910,648)
```

```
#0015  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0015_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 36,509
   54,000 → 49,304
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3487,62)]  [icon: Envoy from Prussia @(3529,62)]  [icon: Envoy from Ottoman Empire @(3571,62)]  [icon: Envoy from Portugal @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   0 →
   T:1
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1961 of 1961 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,448 (+922 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -274g | Other: +1295g | Upkeep: -2654g | Net: +648g
   Treasury: 1,448g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,461 troops
   Supply shortage at Tyrol: Archduke John loses 593 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   --- Strategic Order Updates ---
   Napoleon: Napoleon is marching to Flanders (1 turn remaining).
   Soult: Soult is marching to Flanders (1 turn remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,448g (+922 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 70% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 36,509 — Awaiting orders.
   > Soult — Orleanais — 30,000 — Moving to Flanders — arrives next turn. (to the letter)
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   > Napoleon — Orleanais — 10,000 — Moving to Flanders — arrives next turn.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   Swabia passes from Bavaria to Austria.
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - Ottoman Empire — Open Borders Agreement
   - Portugal — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0016  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Massena ◆' (PanelContainer, layer 121))
view: <run>\frames\0016_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   AUSTRIA LOSSES
   5,491
   4,696
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 36,509
   54,000 → 49,304
   Berthier: “Stalemate. Massena and Archduke Charles glare at each other across the field.” / Archduke Charles: "France pays full price for every Austrian mile now."
   THE GREAT BATTLE OF MILAN
   MILAN · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1961 of 1961 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0017  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0017_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1961 of 1961 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,448 (+922 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0018  click Envoys  ->  ok
  (clicked at (3387, 18))
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 91 px] ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 1
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   THE COURTS WRITE (2)
   Ottoman Empire and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Ottoman Empire
   Proposal
   Turn 1
   Incoming proposal: Open Borders Agreement
   Reis Efendi, serene and unhurried: "The Porte has outlasted a hundred ascendancies by keeping its counsel with each at its noon; France's noon has come, and the Sublime Porte observes it without haste. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   or click the letter to reply in full
   WAITING
   Portugal
   Proposal
   Turn 1
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "Portugal has watched France grow so vast that a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet harbor within it. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Portugal pays you 60 gold at the signing
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1961 of 1961 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0019  click Accept  ->  ok
  (clicked at (1433, 635))
view: <run>\frames\0019_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 1
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   A SMALL COURT WRITES (1)
   Portugal writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Portugal
   Proposal
   Turn 1
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "Portugal has watched France grow so vast that a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet harbor within it. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Portugal pays you 60 gold at the signing
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3571,62)]  [icon: Treaty with Ottoman @(3613,62)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1983 of 1983 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,448 (+941 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
map: unchanged (59 labels)
```

```
#0020  click Accept  ->  ok
  (clicked at (1433, 635))
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 1
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   controls: {ACTIVE}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3529,62)]  [icon: Treaty with Ottoman @(3571,62)]  [icon: Treaty with Portugal @(3613,62)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,508 (+950 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (59 labels)
```

```
#0021  click Open  ->  ok
  (clicked at (2191, 294))
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade /  / Hardenberg, stiffly: "Prussia's  …
   controls: [Accept]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,508 (+950 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (59 labels)
```

```
#0022  click Accept  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Treaty with Ottoman @(3487,62)]  [icon: Treaty with Portugal @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Open Borders Agreement Accepted @(3613,62)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2071 of 2071 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,508 (+960 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
map: unchanged (59 labels)
```

```
#0023  type land an expedition in Ireland  ->  ok
  (typed and Enter)
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Choose who embarks, Sire — click a coastal province on the map for its landing chip. A corps of 15,000 or fewer sails; THE ADMIRALTY (press T, then 7) names who can, and where.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2182 of 2182 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,508 (+960 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► land an expedition in Ireland
   Choose who embarks, Sire — click a coastal province on the map for its landing chip. A corps of 15,000 or fewer sails; THE ADMIRALTY (press T, then 7) names who can, and where.
map: unchanged (59 labels)
```

```
#0024  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 882 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early October 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Moving To  Loca …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2182 of 2182 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,508 (+960 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   ► land an expedition in Ireland
   Choose who embarks, Sire — click a coastal province on the map for its landing chip. A corps of 15,000 or fewer sails; THE ADMIRALTY (press T, then 7) names who can, and where.
map: unchanged (59 labels)
```

```
#0025  click ADMIRALTY  ->  ok
  (clicked at (2049, 283))
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 904 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early October 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 45 sail of the line — readiness 65  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — staging the camp lifts the …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Teulie, march to Provence>  <Dumonceau, march to Normandy>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2182 of 2182 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   ► land an expedition in Ireland
   Choose who embarks, Sire — click a coastal province on the map for its landing chip. A corps of 15,000 or fewer sails; THE ADMIRALTY (press T, then 7) names who can, and where.
map: unchanged (59 labels)
```

```
#0026  scroll 1800 600 down 8  ->  ok
  (scrolled down 8 at (1800, 600))
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 461 of 903 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early October 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 45 sail of the line — readiness 65  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — staging the camp lifts the …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Teulie, march to Provence>  <Dumonceau, march to Normandy>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2182 of 2182 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   ► land an expedition in Ireland
   Choose who embarks, Sire — click a coastal province on the map for its landing chip. A corps of 15,000 or fewer sails; THE ADMIRALTY (press T, then 7) names who can, and where.
map: unchanged (59 labels)
```

```
#0027  click Dumonceau, march to Normandy  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 461 of 903 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early October 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 45 sail of the line — readiness 65  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — staging the camp lifts the …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Teulie, march to Provence>  <Dumonceau, march to Normandy>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1717 of 1718 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,508 (+960 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   SITUATION
   France holds 28 regions. Treasury: 1,448g (+922 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 70% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 36,509 — Awaiting orders.
   > Soult — Orleanais — 30,000 — Moving to Flanders — arrives next turn. (to the letter)
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   > Napoleon — Orleanais — 10,000 — Moving to Flanders — arrives next turn.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   Swabia passes from Bavaria to Austria.
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - Ottoman Empire — Open Borders Agreement
   - Portugal — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   ► land an expedition in Ireland
   Choose who embarks, Sire — click a coastal province on the map for its landing chip. A corps of 15,000 or fewer sails; THE ADMIRALTY (press T, then 7) names who can, and where.
   ► Dumonceau, march to Normandy
   Dumonceau begins march to Normandy. Route: Flanders → Picardy → Artois → Normandy. Moves to Flanders. Dumonceau: "We move deliberately — arrival is worth little if the army arrives broken."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1868,478)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Lannes(1800,497)  Murat(1825,471)  Soult(1683,440)  Napoleon(1706,466)  Dumonceau(1716,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1684,411)  10k(1910,648)
```

```
#0028  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   0 →
   T:1
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [scrolled 1717 of 1718 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Choose who embarks, Sire — click a coastal province on the map for its landing chip. A corps of 15,000 or fewer sails; THE ADMIRALTY (press T, then 7) names who can, and where.
   ► Dumonceau, march to Normandy
   Dumonceau begins march to Normandy. Route: Flanders → Picardy → Artois → Normandy. Moves to Flanders. Dumonceau: "We move deliberately — arrival is worth little if the army arrives broken."
   [2/4 actions remaining]
map: unchanged (59 labels)
```

```
#0029  look  ->  ok
  (a fresh frame)
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1717 of 1718 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Choose who embarks, Sire — click a coastal province on the map for its landing chip. A corps of 15,000 or fewer sails; THE ADMIRALTY (press T, then 7) names who can, and where.
   ► Dumonceau, march to Normandy
   Dumonceau begins march to Normandy. Route: Flanders → Picardy → Artois → Normandy. Moves to Flanders. Dumonceau: "We move deliberately — arrival is worth little if the army arrives broken."
   [2/4 actions remaining]
map: unchanged (59 labels)
```

```
#0030  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!

Income: 2575g | Admiralty: -90g | Blockade: -281g | Materiel: -748g | Upkeep: -2256g (incl. 160g over-limit, 540g Grande Armée, 204g campaign pay) | Other: +1329g | Net: +529g | Treasury: 2,037g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 862 px] ──
   ENEMY PHASE - Turn 2
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Second Battle of Milan /     Archduke Charles: 3,998 casualties, 43,845 remaining /     Massena's army: 5,313 casualties — Massena's own corps: 31,779 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%)  …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2139 of 2139 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,037 (+1,275 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 2575g | Admiralty: -90g | Blockade: -281g | Materiel: -748g | Other: +1329g | Upkeep: -2256g | Net: +529g
   Treasury: 2,037g
   Actions refreshed: 4/4
   Bavaria completes a market at Franconia.
   Supply shortage at Tyrol: Archduke Charles loses 1,039 troops
   Supply shortage at Tyrol: Archduke John loses 490 troops
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 97 (-3): the contingent's dead, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 94 (-4): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1868,478)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Lannes(1800,497)  Murat(1825,471)  Napoleon(1694,440)  Soult(1704,322)  Dumonceau(1728,296)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1762,420)  12k(1684,411)  10k(1910,648)
```

```
#0031  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   NAPOLEON REPORTS
   "Berthier: 'Cannon fire at Franche-Comte, Sire. Investigate?'"
   controls: [March to the Guns]  [Continue as Ordered]  [Hold Position]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Envoy from Denmark @(3400,64)]  [icon: Envoy from Saxony @(3442,64)]  [icon: Soult arrived @(3484,64)]  [icon: Treaty with Ottoman @(3526,64)]  [icon: Treaty with Portugal @(3568,64)]  [+2]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   -6 →
   T:2
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2029 of 2029 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,037 (+1,275 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 2575g | Admiralty: -90g | Blockade: -281g | Materiel: -748g | Other: +1329g | Upkeep: -2256g | Net: +529g
   Treasury: 2,037g
   Actions refreshed: 4/4
   Bavaria completes a market at Franconia.
   Supply shortage at Tyrol: Archduke Charles loses 1,039 troops
   Supply shortage at Tyrol: Archduke John loses 490 troops
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 97 (-3): the contingent's dead, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 94 (-4): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   --- Strategic Order Updates ---
   Dumonceau: Dumonceau is marching to Normandy (3 turns remaining).
   Soult: As ordered: "Soult, march to Flanders". Soult arrives at Flanders. Soult stands ready for instruction.
   Napoleon: Berthier: 'Cannon fire at Franche-Comte, Sire. Investigate?'
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 2,037g (+1,277 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 75% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 30,000 — Awaiting orders.
   - Massena — Milan — 28,148 — Hunted by Archduke Charles on consecutive turns — holds Milan with 28,148 men.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 20,732 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 14,539 — Awaiting orders.
   ? Napoleon — Orleanais — 10,000 — HALTED at Orleanais — awaiting your word.
   > Dumonceau — Flanders — 6,500 — Moving to Normandy — 3 turns out.
   - Teulie — Milan — 5,601 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   Sire — Prussia and France have signed the Open Borders Agreement.
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   War exhaustion grows — France nears breaking point (exhaustion: 20).
   War exhaustion grows — Austria nears breaking point (exhaustion: 20).
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Denmark — Non-Aggression Pact
   - Saxony — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-5)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Napoleon awaits your orders!
map: unchanged (59 labels)
```

```
#0032  look  ->  ok
  (a fresh frame)
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2029 of 2029 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Napoleon awaits your orders!
map: unchanged (59 labels)
```

```
#0033  click Continue as Ordered  ->  ok
  (clicked at (1829, 551))
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Teulie
   7,500 → 6,917
   ⚔
   Massena ◆
   Archduke Charles ◆
   36,509 → 31,779
   47,843 → 43,845
   THE GREAT SECOND BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: Envoy from Denmark @(3442,64)]  [icon: Envoy from Saxony @(3484,64)]  [icon: Soult arrived @(3526,64)]  [icon: Treaty with Ottoman @(3568,64)]  [+3]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,037 (+1,275 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Franche-Comte. Napoleon arrives at Flanders.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1868,478)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Lannes(1800,497)  Murat(1825,471)  Soult(1704,322)  Napoleon(1715,296)  Dumonceau(1728,270)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  10k(1910,648)
```

```
#0034  look  ->  ok
  (a fresh frame)
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   3,582
   2,695
   Teulie
   7,500 → 6,917
   ⚔
   Massena ◆
   Archduke Charles ◆
   36,509 → 31,779
   47,843 → 43,845
   THE GREAT SECOND BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 2
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Franche-Comte. Napoleon arrives at Flanders.
map: unchanged (59 labels)
```

```
#0035  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   THE SMALL COURTS WRITE (2)
   Denmark and Saxony write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Denmark
   Proposal
   Turn 2
   Incoming proposal: Non-Aggression Pact
   Bernstorff, watchful and correct: "As his sovereign has long willed, Denmark moves toward what the Crown desires. Sign the pact of non-aggression."
   Terms: Proposal: Non-Aggression Pact
   or click the letter to reply in full
   WAITING
   Saxony
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Einsiedel, anxiously: "Saxony has kept her house through many great reigns by keeping her treaties in good repair; His Majesty would merely continue the practice. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Saxony pays you 82 gold at the signing
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Franche-Comte. Napoleon arrives at Flanders.
map: unchanged (59 labels)
```

```
#0036  click#1 Accept  ->  ok
  (clicked at (1433, 456))
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   A SMALL COURT WRITES (1)
   Saxony writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Saxony
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Einsiedel, anxiously: "Saxony has kept her house through many great reigns by keeping her treaties in good repair; His Majesty would merely continue the practice. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Saxony pays you 82 gold at the signing
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: Treaty with Denmark @(3484,64)]  [icon: Treaty with Ottoman @(3526,64)]  [icon: Treaty with Portugal @(3568,64)]  [+2]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2095 of 2095 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,037 (+1,294 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
map: unchanged (59 labels)
```

```
#0037  click Accept  ->  ok
  (clicked at (1433, 500))
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 66 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: Treaty with Denmark @(3484,64)]  [icon: Treaty with Saxony @(3526,64)]  [icon: Treaty with Ottoman @(3568,64)]  [+3]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2117 of 2117 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,119 (+1,297 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (59 labels)
```

```
#0038  type Napoleon, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon begins march to Flanders. (1 AP — the Emperor commands in his own name.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   2,119 (+1,297 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 2,037g (+1,277 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 75% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 30,000 — Awaiting orders.
   - Massena — Milan — 28,148 — Hunted by Archduke Charles on consecutive turns — holds Milan with 28,148 men.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 20,732 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 14,539 — Awaiting orders.
   ? Napoleon — Orleanais — 10,000 — HALTED at Orleanais — awaiting your word.
   > Dumonceau — Flanders — 6,500 — Moving to Normandy — 3 turns out.
   - Teulie — Milan — 5,601 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   Sire — Prussia and France have signed the Open Borders Agreement.
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   War exhaustion grows — France nears breaking point (exhaustion: 20).
   War exhaustion grows — Austria nears breaking point (exhaustion: 20).
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Denmark — Non-Aggression Pact
   - Saxony — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-5)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Franche-Comte. Napoleon arrives at Flanders.
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
   ► Napoleon, march to Flanders
   Napoleon begins march to Flanders. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0039  type what if Ney attacks Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0039_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Ney (24,000; expect about 82,342 with the corps likely to arrive, up to 88,218 if all march; certain 24,000; a bad day (1 in 10) 70,908) vs Mack (large force) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  What Swabia can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 85,271 we muster) would cost ~640g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
  (Standing orders
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1543 of 1543 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   2,119 (+1,297 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
   MUSTER — Ney (24,000; expect about 82,342 with the corps likely to arrive, up to 88,218 if all march; certain 24,000; a bad day (1 in 10) 70,908) vs Mack (large force) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 85,271 we muster) would cost ~640g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (59 labels)
```

```
#0040  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0040_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (24,000; expect about 82,342 with the corps likely to arrive, up to 88,218 if all march; certain 24,000; a bad day (1 in 10) 70,908) vs Mack (large force) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  What Swabia can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 85,271 we muster) would cost ~640g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
Ask 'what if Ney attacks Mack' to read the muster be
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   14,539 → 13,478
   Murat
   20,732 → 20,127
   Davout
   26,000 → 24,482
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 21,664 → 21,376 after the advance
   48,163 → 31,928
   marched to the guns
   marched to the guns
   Bernadotte — weighed his own ambitions
   THE GREAT BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 3
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 74 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: Treaty with Denmark @(3484,64)]  [icon: Treaty with Saxony @(3526,64)]  [icon: Treaty with Ottoman @(3568,64)]  [+3]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   +11 →
   T:2
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1925 of 1925 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,843 (+1,521 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-5)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Franche-Comte. Napoleon arrives at Flanders.
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
   ► Napoleon, march to Flanders
   Napoleon begins march to Flanders. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
   MUSTER — Ney (24,000; expect about 82,342 with the corps likely to arrive, up to 88,218 if all march; certain 24,000; a bad day (1 in 10) 70,908) vs Mack (large force) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 85,271 we muster) would cost ~640g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
   ► Ney, attack Mack
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (24,000; expect about 82,342 with the corps likely to arrive, up to 88,218 if all march; certain 24,000; a bad day (1 in 10) 70,908) vs Mack (large force) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 85,271 we muster) would cost ~640g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+2%)
   Ney attacks with overwhelming force. Ney gains the advantage over Mack. Casualties: Ney's army 5,520, Mack 16,235. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -276g, Austria -811g. Our treasury stands at 1,843 gold. Ney advances into Swabia. (288 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 64,218 committed (Davout, Lannes, Murat) = 88,218.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,184 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%)
   Casualties: Ney's own corps 2,336 | Mack 16,235
   Strength: Ney 24,000 → 21,664 → 21,376 after the advance | Mack 48,163 → 31,928
   Berthier: "Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Bernadotte never arrived, Sire."
   The war's cost now stands at 26,000 of our men.
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1871,375)  Ney +3(1847,444)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Soult(1704,322)  Napoleon(1715,296)  Dumonceau(1728,270)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  10k(1910,648)
```

```
#0041  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0041_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1925 of 1925 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (54 labels)
```

```
#0042  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0042_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 904 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Late October 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Moving To  Locat …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1925 of 1925 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,843 (+1,521 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (54 labels)
```

```
#0043  click ADMIRALTY  ->  ok
  (clicked at (2049, 283))
view: <run>\frames\0043_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 882 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late October 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 45 sail of the line — readiness 60  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — staging the camp lifts the  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Lannes, march to Normandy>  <Dumonceau, march to Normandy>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1925 of 1925 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (54 labels)
```

```
#0044  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0044_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   +11 →
   T:2
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [scrolled 1925 of 1925 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (54 labels)
```

```
#0045  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0045_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2021 of 2021 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,843 (+1,521 next turn)
   Inf:
   84,337
   Cav:
   18,500
   Art:
   11,200
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ 2 corps stand in peril — an enemy force of ~31,928 shares the field (Swabia).
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0046  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0046_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!

Income: 2577g | Requisitions: +37g | Admiralty: -90g | Blockade: -329g | Materiel: -550g | Upkeep: -1656g (incl. 80g over-limit, 180g Grande Armée, 204g campaign pay) | Other: +1374g | Net: +1363g | Treasury: 3,206g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 862 px] ──
   ENEMY PHASE - Turn 3
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     Fourth Battle of Milan /     Archduke Charles: 3,010 casualties, 37,080 remaining /     Massena's army: 4,991 casualties — Massena's own corps: 23,689 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) /     ⚔ View the field /     --- Berthier's Report --- /     Attack: Archduke Charles ( …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 72 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2637 of 2637 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,206 (+1,819 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (24,000; expect about 82,342 with the corps likely to arrive, up to 88,218 if all march; certain 24,000; a bad day (1 in 10) 70,908) vs Mack (large force) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 85,271 we muster) would cost ~640g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+2%)
   Ney attacks with overwhelming force. Ney gains the advantage over Mack. Casualties: Ney's army 5,520, Mack 16,235. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -276g, Austria -811g. Our treasury stands at 1,843 gold. Ney advances into Swabia. (288 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 64,218 committed (Davout, Lannes, Murat) = 88,218.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,184 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%)
   Casualties: Ney's own corps 2,336 | Mack 16,235
   Strength: Ney 24,000 → 21,664 → 21,376 after the advance | Mack 48,163 → 31,928
   Berthier: "Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Bernadotte never arrived, Sire."
   The war's cost now stands at 26,000 of our men.
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
   ⚠ 2 corps stand in peril — an enemy force of ~31,928 shares the field (Swabia).
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2577g | Requisitions: +37g | Admiralty: -90g | Blockade: -329g | Materiel: -550g | Other: +1374g | Upkeep: -1656g | Net: +1363g
   Treasury: 3,206g
   Actions refreshed: 4/4
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Supply shortage at Franconia: Archduke Charles loses 431 troops
   Supply shortage at Swabia: Ney loses 1,282 troops
   Supply shortage at Swabia: Davout loses 1,468 troops
   Supply shortage at Swabia: Lannes loses 808 troops
   Supply shortage at Swabia: Murat loses 1,207 troops
   Supply shortage at Swabia: Deroy loses 1,086 troops
   Supply shortage at Munich: Mack loses 97 troops
   Holland loyalty 95 (-3): the lord's defeats, satellite drift
   Kingdom of Italy loyalty 90 (-7): the lord's defeats, the contingent's dead
   Switzerland loyalty 89 (-5): the lord's defeats, satellite drift
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Murat is eyeing Mack's position at Munich. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Berthier reports that Bernadotte appears envious of Davout's laurels — he has grown cold and withholding.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Deroy(1871,350)  Ney +3(1847,444)  ?(1501,602)  Castanos(1501,564)  ?(1953,579)  Archduke John(1948,540)  Mack(1868,501)  Soult(1704,322)  Napoleon(1728,296)  Dumonceau(1691,418)  Teulie(1909,589)  ?(2068,435)  ?(1959,404)  ?(1869,762)  ?(1860,591)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1768,420)  12k(1716,446)  10k(1910,645)
```

```
#0047  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0047_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   TEULIE REPORTS
   "Teulie is cornered at Milan with 3,483 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 72 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Teulie is cornered @(3358,64)]  [icon: Napoleon arrived (x2) @(3400,64)]  [icon: Envoy from Hesse @(3442,64)]  [icon: Envoy from Papal States @(3484,64)]  [icon: Marshal Murat seeks an audience @(3526,64)]  [icon: Soult arrived @(3568,64)]  [+6]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   +3 →
   T:3
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2136 of 2136 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,206 (+1,819 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Murat is eyeing Mack's position at Munich. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Berthier reports that Bernadotte appears envious of Davout's laurels — he has grown cold and withholding.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   --- Strategic Order Updates ---
   Dumonceau: Dumonceau marches to Picardy. 2 regions to Normandy.
   Napoleon: Napoleon arrives at Flanders.
   Teulie: Teulie is cornered at Milan with 3,483 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
   • Sire — Teulie was mauled at Milan: a quarter of his corps — 1,586 men — lost in a single action.
   • Sire — London now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1,368 gold and shortens the road to 5 turns.
   SITUATION
   France holds 28 regions. Treasury: 3,206g (+1,913 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 54% of French forces (an estimate — 2 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 90 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 30,000 — Awaiting orders.
   - Davout — Swabia — 23,014 — Awaiting orders.
   - Ney — Swabia — 20,094 — Awaiting orders.
   < Massena — Piedmont — 19,047 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 19,047 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Murat — Swabia — 18,920 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   ⚠ IN PERIL — an enemy force of ~31,690 shares the field (Franconia).
   - Lannes — Swabia — 12,670 — Awaiting orders.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   > Dumonceau — Picardy — 6,500 — Moving to Normandy — 2 turns out.
   ? Teulie — Milan — 3,483 — Hunted by Archduke Charles on consecutive turns — holds Milan with 3,483 men. Morale:4%
   ⚠ Morale failing (4) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Deroy — Swabia — 17,019 [confirmed]
   Archduke Charles — Franconia — 31,690 [confirmed]
   Mack — Munich — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Supply cost you 4,765 men, at Swabia.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Murat is eyeing Mack's position at Munich. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Berthier reports that Bernadotte appears envious of Davout's laurels — he has grown cold and withholding.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 44).
   War exhaustion grows — France nears breaking point (exhaustion: 42).
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non-Aggression Pact
   - Papal States — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+4)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 72/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   Teulie awaits your orders!
map: unchanged (56 labels)
```

```
#0048  click Attempt a Breakout  ->  ok
  (clicked at (1971, 584))
view: <run>\frames\0048_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Teulie
   5,601 → 5,069
   ⚔
   Massena ◆
   Archduke Charles ◆
   28,148 → 23,689
   40,090 → 37,080
   FOURTH BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 3
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 72 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived (x2) @(3358,64)]  [icon: Envoy from Hesse @(3400,64)]  [icon: Envoy from Papal States @(3442,64)]  [icon: Marshal Murat seeks an audience @(3484,64)]  [icon: Soult arrived @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+5]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2180 of 2180 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,206 (+1,819 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (34 lost to the march)
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Deroy(1871,350)  Ney +3(1847,444)  ?(1501,602)  Castanos(1501,564)  ?(1948,579)  Archduke John(1948,540)  Mack(1868,501)  Soult(1704,322)  Napoleon(1728,296)  Dumonceau(1691,418)  ?(2068,435)  ?(1959,404)  ?(1869,762)  ?(1901,591)  25k(1595,494)  12k(1551,454)  ?(1768,420)  12k(1716,446)  10k(1910,645)
```

```
#0049  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0049_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   THE SMALL COURTS WRITE (2)
   Hesse and Papal States write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Hesse
   Proposal
   Turn 3
   Incoming proposal: Non-Aggression Pact
   Hesse, wishing to go unnoticed: "Hesse counts what a quarrel with France would cost and what an understanding would return, and finds his councillors of one mind. Sign the pact of non-aggression."
   Terms: Proposal: Non-Aggression Pact
   or click the letter to reply in full
   WAITING
   Papal States
   Proposal
   Turn 3
   Incoming proposal: Open Borders Agreement
   Cardinal Consalvi, serenely: "Rome measures powers in centuries and finds it profitable to be patient with all of them; an understanding with France costs the Church nothing that time will not repay. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · The Papal States pays you 105 gold at the signing
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2180 of 2180 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (34 lost to the march)
map: unchanged (55 labels)
```

```
#0050  click#1 Accept  ->  ok
  (clicked at (1433, 478))
view: <run>\frames\0050_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   A SMALL COURT WRITES (1)
   Papal States writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Papal States
   Proposal
   Turn 3
   Incoming proposal: Open Borders Agreement
   Cardinal Consalvi, serenely: "Rome measures powers in centuries and finds it profitable to be patient with all of them; an understanding with France costs the Church nothing that time will not repay. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · The Papal States pays you 105 gold at the signing
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 72 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived (x2) @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: Treaty with Hesse @(3484,64)]  [icon: Treaty with Denmark @(3526,64)]  [icon: Treaty with Saxony @(3568,64)]  [+4]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2202 of 2202 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,206 (+1,834 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
map: unchanged (55 labels)
```

```
#0051  click Accept  ->  ok
  (clicked at (1433, 500))
view: <run>\frames\0051_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 72 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived (x2) @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: Treaty with Hesse @(3484,64)]  [icon: Treaty with Papal States @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+5]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2224 of 2224 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,311 (+1,834 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (55 labels)
```

```
#0052  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0052_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 860 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early November 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 90 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location: …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2224 of 2224 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,311 (+1,834 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (34 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (55 labels)
```

```
#0053  click ADMIRALTY  ->  ok
  (clicked at (2049, 283))
view: <run>\frames\0053_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 1058 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early November 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 45 sail of the line — readiness 55  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — staging the camp lifts th …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Teulie in Carniola>  <Land Teulie in Croatia>  <Land Teulie in Hungary>  <Land Teulie in Moravia>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2224 of 2224 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (34 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (55 labels)
```

```
#0054  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0054_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   +3 →
   T:3
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [scrolled 2224 of 2224 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (34 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (55 labels)
```

```
#0055  type who am I fighting  ->  ok
  (typed and Enter)
view: <run>\frames\0055_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +3 (evenly matched), in its 4th turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the war banner on the left (click the war); every court's design in the Diplomatic Ledger (press D).
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1717 of 1717 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,311 (+1,834 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   France holds 28 regions. Treasury: 3,206g (+1,913 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 54% of French forces (an estimate — 2 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 90 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 30,000 — Awaiting orders.
   - Davout — Swabia — 23,014 — Awaiting orders.
   - Ney — Swabia — 20,094 — Awaiting orders.
   < Massena — Piedmont — 19,047 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 19,047 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Murat — Swabia — 18,920 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   ⚠ IN PERIL — an enemy force of ~31,690 shares the field (Franconia).
   - Lannes — Swabia — 12,670 — Awaiting orders.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   > Dumonceau — Picardy — 6,500 — Moving to Normandy — 2 turns out.
   ? Teulie — Milan — 3,483 — Hunted by Archduke Charles on consecutive turns — holds Milan with 3,483 men. Morale:4%
   ⚠ Morale failing (4) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Deroy — Swabia — 17,019 [confirmed]
   Archduke Charles — Franconia — 31,690 [confirmed]
   Mack — Munich — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Supply cost you 4,765 men, at Swabia.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Murat is eyeing Mack's position at Munich. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Berthier reports that Bernadotte appears envious of Davout's laurels — he has grown cold and withholding.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 44).
   War exhaustion grows — France nears breaking point (exhaustion: 42).
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non-Aggression Pact
   - Papal States — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+4)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 72/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (34 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
   ► who am I fighting
   We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +3 (evenly matched), in its 4th turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the war banner on the left (click the war); every court's design in the Diplomatic Ledger (press D).
map: unchanged (55 labels)
```

```
#0056  type what if Ney attacks Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0056_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Ney (20,094; expect about 58,211 with the corps likely to arrive, up to 60,242 if all march; certain 20,094) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL NOT — Murat: will not lift a finger for Marshal Ney
  WILL NOT — Bernadotte: is pinned by enemies before his own front
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Munich can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 55,778 we muster) would cost ~418g.
  Munich is Bavaria's soil — the corps standing there are fed by contract, about −660g more a turn.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.

Nothing has been ordered, and nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1629 of 1629 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,311 (+1,834 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
   MUSTER — Ney (20,094; expect about 58,211 with the corps likely to arrive, up to 60,242 if all march; certain 20,094) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Murat: will not lift a finger for Marshal Ney
   WILL NOT — Bernadotte: is pinned by enemies before his own front
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 55,778 we muster) would cost ~418g.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −660g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (55 labels)
```

```
#0057  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0057_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (20,094; expect about 58,211 with the corps likely to arrive, up to 60,242 if all march; certain 20,094) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL NOT — Murat: will not lift a finger for Marshal Ney
  WILL NOT — Bernadotte: is pinned by enemies before his own front
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Munich can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 55,778 we muster) would cost ~418g.
  Munich is Bavaria's soil — the corps standing there are fed by contract, about −660g more a turn.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.


[Combat] Ney leads the charge! (Aggressive: +15% attack)
[Shield] Mack's DEFENSIVE sta
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   12,670 → 12,288
   Davout
   23,014 → 22,459
   ⚔
   Ney ◆
   Mack ◆
   20,094 → 19,285 → 18,900 after the advance
   30,235 → 12,075
   marched to the guns
   marched to the guns
   THE GREAT BATTLE OF MUNICH
   click anywhere to skip ▸
   MUNICH · TURN 4
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 80 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived (x2) @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: Treaty with Hesse @(3484,64)]  [icon: Treaty with Papal States @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+5]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   +17 →
   T:3
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2248 of 2248 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,224 (+1,284 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non-Aggression Pact
   - Papal States — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+4)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 72/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (34 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
   ► who am I fighting
   We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +3 (evenly matched), in its 4th turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the war banner on the left (click the war); every court's design in the Diplomatic Ledger (press D).
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
   MUSTER — Ney (20,094; expect about 58,211 with the corps likely to arrive, up to 60,242 if all march; certain 20,094) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Murat: will not lift a finger for Marshal Ney
   WILL NOT — Bernadotte: is pinned by enemies before his own front
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 55,778 we muster) would cost ~418g.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −660g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► Ney, attack Mack
   ⚔ The Great Battle of Munich ⚔
   MUSTER — Ney (20,094; expect about 58,211 with the corps likely to arrive, up to 60,242 if all march; certain 20,094) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Murat: will not lift a finger for Marshal Ney
   WILL NOT — Bernadotte: is pinned by enemies before his own front
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 55,778 we muster) would cost ~418g.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −660g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Shield] Mack's DEFENSIVE stance strengthens the line! (+15% defense)
   [Terrain] Mack benefits from Mountains terrain (+25% defense)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney delivers an effective strike. Ney gains the advantage over Mack. Casualties: Ney's army 1,746, Mack 18,160. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -87g, Austria -908g. Our treasury stands at 3,224 gold. Ney advances into Munich. (385 lost to march) Munich is Bavaria's soil — the corps standing there are fed by contract, about −216g more a turn. Munich remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   [!] Mack's broken army flees to Tyrol! (recovering for 3 turns)
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 20,094 (lead) + 40,148 committed (Davout, Lannes) = 60,242.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 937 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%)
   Defense: Mack (Defensive stance +15%, Terrain (Mountains) +25%)
   Casualties: Ney's own corps 809 | Mack 18,160
   Strength: Ney 20,094 → 19,285 → 18,900 after the advance | Mack 30,235 → 12,075
   Berthier: "Davout and Lannes arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire."
   The war's cost now stands at 38,773 of our men.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Murat(1847,464)  Deroy(1850,438)  ?(1501,602)  Castanos(1501,564)  ?(1940,588)  Mack(1960,556)  ?(1968,583)  Archduke John(2051,535)  Ney(1888,535)  Davout(1901,561)  Lannes(1942,530)  Soult(1704,322)  Napoleon(1728,296)  Dumonceau(1691,418)  ?(2068,435)  ?(1959,404)  ?(1869,762)  10k(1901,591)  ?(1854,373)  25k(1595,494)  12k(1551,454)  ?(1768,420)  12k(1716,446)  10k(1910,645)
```

```
#0058  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0058_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2248 of 2248 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Casualties: Ney's own corps 809 | Mack 18,160
   Strength: Ney 20,094 → 19,285 → 18,900 after the advance | Mack 30,235 → 12,075
   Berthier: "Davout and Lannes arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire."
   The war's cost now stands at 38,773 of our men.
map: unchanged (60 labels)
```

```
#0059  type Bernadotte, retreat to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0059_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte retreats from Franconia to Munich. Swabia cannot be reached, Sire — it is Austria-held soil and we are at war; Bernadotte falls back to Munich instead.  (170 lost to march) Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2894 of 2894 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,224 (+1,304 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Bernadotte, retreat to Swabia
   Bernadotte retreats from Franconia to Munich. Swabia cannot be reached, Sire — it is Austria-held soil and we are at war; Bernadotte falls back to Munich instead.  (170 lost to march) Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1943,451)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Murat(1847,477)  Deroy(1835,443)  ?(1501,602)  Castanos(1501,564)  ?(1940,583)  Mack(1940,556)  ?(1968,583)  Archduke John(2032,537)  Ney +3(1901,530)  Soult(1704,322)  Napoleon(1728,296)  Dumonceau(1691,417)  ?(2068,435)  ?(1959,376)  ?(1869,762)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1768,420)  12k(1716,445)  10k(1910,645)
```

```
#0060  type Massena, drill  ->  ok
  (typed and Enter)
view: <run>\frames\0060_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Massena is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2982 of 2982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,224 (+1,304 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, drill
   Massena is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
map: unchanged (57 labels)
```

```
#0061  click Generals  ->  ok
  (clicked at (228, 18))
view: <run>\frames\0061_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 6526 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  / SEEKS AN AUDIENCE — Murat /   / [5] Murat    [Cavalry]  France / The Cavalry Reserve - screening the Black Forest feint while the army wheels north of the Danube. / Aggressive: +15% attack, +5% more in aggressive stance. Fortify capped at 10%. Grows restless if idle too long. / Cava …
   controls: [Pin]  [icon @(2213,236)]  <Hear him — he seeks an audience>  <Fortify>  <Hold (2 AP)>  <Fall back>  <▸ the doctrine>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fortify>  <Drill>  <Hold (1 AP)>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fortify>  <Drill>  <Hold (2 AP)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,224 (+1,304 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Bernadotte, retreat to Swabia
   Bernadotte retreats from Franconia to Munich. Swabia cannot be reached, Sire — it is Austria-held soil and we are at war; Bernadotte falls back to Munich instead.  (170 lost to march) Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
   ► Massena, drill
   Massena is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
map: unchanged (57 labels)
```

```
#0062  click Hear him  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0062_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   MURAT — Marshal Murat seeks an audience
   "Sire — I have earned better than to watch Ney take the field while I hold a road." /  / Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a command worthy of his talents. /  / What each answer does / • Let it stand (Free) — Free, and it fixes nothing. For 3 more turns he brings NONE of his 20,127 men to any battle Ney leads, and the quarrel may harden further. / …
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Give him a command   [2 AP]]  [Later (he will return)]
── TopBar (layer 75) [under a modal]: unchanged
── MarshalManagement (layer 50) [under a modal] [scrolled 0 of 6526 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,224 (+1,304 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Bernadotte, retreat to Swabia
   Bernadotte retreats from Franconia to Munich. Swabia cannot be reached, Sire — it is Austria-held soil and we are at war; Bernadotte falls back to Munich instead.  (170 lost to march) Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
   ► Massena, drill
   Massena is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
map: unchanged (57 labels)
```

```
#0063  click Give him a command  ->  ok
  (clicked at (2029, 702))
view: <run>\frames\0063_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived (x2) @(3358,64)]  [icon: Soult arrived @(3400,64)]  [icon: Treaty with Hesse @(3442,64)]  [icon: Treaty with Papal States @(3484,64)]  [icon: Treaty with Denmark @(3526,64)]  [icon: Treaty with Saxony @(3568,64)]  [+4]
── MarshalManagement (layer 50) [scrolled 0 of 6480 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  /   OUR DOCTRINE — The Corps System  ▸ the doctrine /  /   THE EMPEROR /   / [8] Napoleon  [Infantry]  France / In the field at Flanders — The Presence goes where he stands. /   ★ The Presence  +10% here at Flanders  Every French corps fighting in the Emperor's province gains +10% att …
   controls: [Pin]  [icon @(2213,236)]  <▸ the doctrine>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Fall back>  <Fortify>  <Fall back>  <Fortify>  <Drill>  <Hold (1 AP)>  <Fortify>  <Fall back>  <Fortify>  <Fall back>  <Fortify>  <Drill>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2895 of 2896 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   2,956 (+1,434 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
   ► who am I fighting
   We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +3 (evenly matched), in its 4th turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the war banner on the left (click the war); every court's design in the Diplomatic Ledger (press D).
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
   MUSTER — Ney (20,094; expect about 58,211 with the corps likely to arrive, up to 60,242 if all march; certain 20,094) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Murat: will not lift a finger for Marshal Ney
   WILL NOT — Bernadotte: is pinned by enemies before his own front
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 55,778 we muster) would cost ~418g.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −660g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► Ney, attack Mack
   ⚔ The Great Battle of Munich ⚔
   MUSTER — Ney (20,094; expect about 58,211 with the corps likely to arrive, up to 60,242 if all march; certain 20,094) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Murat: will not lift a finger for Marshal Ney
   WILL NOT — Bernadotte: is pinned by enemies before his own front
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 55,778 we muster) would cost ~418g.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −660g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Shield] Mack's DEFENSIVE stance strengthens the line! (+15% defense)
   [Terrain] Mack benefits from Mountains terrain (+25% defense)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney delivers an effective strike. Ney gains the advantage over Mack. Casualties: Ney's army 1,746, Mack 18,160. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -87g, Austria -908g. Our treasury stands at 3,224 gold. Ney advances into Munich. (385 lost to march) Munich is Bavaria's soil — the corps standing there are fed by contract, about −216g more a turn. Munich remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   [!] Mack's broken army flees to Tyrol! (recovering for 3 turns)
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 20,094 (lead) + 40,148 committed (Davout, Lannes) = 60,242.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 937 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%)
   Defense: Mack (Defensive stance +15%, Terrain (Mountains) +25%)
   Casualties: Ney's own corps 809 | Mack 18,160
   Strength: Ney 20,094 → 19,285 → 18,900 after the advance | Mack 30,235 → 12,075
   Berthier: "Davout and Lannes arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire."
   The war's cost now stands at 38,773 of our men.
   ► Bernadotte, retreat to Swabia
   Bernadotte retreats from Franconia to Munich. Swabia cannot be reached, Sire — it is Austria-held soil and we are at war; Bernadotte falls back to Munich instead.  (170 lost to march) Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
   ► Massena, drill
   Massena is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
   "Archduke Charles, then." Murat takes the command and goes. Murat pursues Archduke Charles (at Franconia). Archduke Charles spotted at Franconia! Engaging!
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Combat] Adjacent allies bolster Murat's attack! (+6%)
   Murat faces a difficult fight. Archduke Charles holds the line. Casualties: Murat 5,379, Archduke Charles 2,632. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -268g, Austria -131g. Our treasury stands at 2,956 gold.
   (Murat stands down from his intended attack — your orders reached him in time.) Murat: "He is already beaten — he merely has not been told. I will tell him."
   [1/4 actions remaining]
   --- Berthier's Report ---
   Murat: "A horseman loses a field as he loses a race — by a length, not for good."
   Murat fought with particular ferocity — though one wonders if it was for France or for himself.
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Murat 5,379 | Archduke Charles 2,632
   Strength: Murat 18,920 → 13,541 | Archduke Charles 31,690 → 29,058
   Berthier: "Murat stood alone, Sire. Ney never came."
   The war's cost now stands at 44,152 of our men.
map: unchanged (57 labels)
```

```
#0064  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0064_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   +13 →
   T:3
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [scrolled 2895 of 2896 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Casualties: Murat 5,379 | Archduke Charles 2,632
   Strength: Murat 18,920 → 13,541 | Archduke Charles 31,690 → 29,058
   Berthier: "Murat stood alone, Sire. Ney never came."
   The war's cost now stands at 44,152 of our men.
map: unchanged (57 labels)
```

```
#0065  click Event Log  ->  ok
  (clicked at (53, 18))
view: <run>\frames\0065_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['event_log'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── CampaignLog (layer 50) [scrolled 0 of 72 px] ──
   CAMPAIGN LOG
   6 approaches from Austria and Prussia are rebuffed (open borders agreement)
   Teulie (France) retreated from Milan to Piedmont
   We accepted Hesse's non-aggression pact proposal (hegemony pressure)
   We accepted the Papal States' open borders agreement proposal (hegemony pressure)
   The Great Battle of Munich: Ney (France) attacked Mack (Austria) — Ney tactical victory (1,746 / 18,160 casualties) — Mack: "The army retires; the system remains intact. You will see."
   Building damaged: Market in Munich
   Mack (Austria) retreated from Munich to Tyrol
   Murat ordered to pursue Archduke Charles
   Second Battle of Franconia: Murat (France) attacked Archduke Charles (Austria) — Archduke Charles holds the field (5,379 / 2,632 casualties) — Archduke Charles: "My line was drawn a week ago. You found it this morning."
   Building damaged: Market in Franconia
   Murat (France) aired his grievance and was given a command
   controls: [Pin]  [icon: Close (L) @(2143,296)]  [▾ Turn 4  -  11 events]  [▸ Turn 3  -  24 events]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2895 of 2896 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   2,956 (+1,434 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Casualties: Murat 5,379 | Archduke Charles 2,632
   Strength: Murat 18,920 → 13,541 | Archduke Charles 31,690 → 29,058
   Berthier: "Murat stood alone, Sire. Ney never came."
   The war's cost now stands at 44,152 of our men.
map: unchanged (57 labels)
```

```
#0066  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0066_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   +13 →
   T:3
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [scrolled 2895 of 2896 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Casualties: Murat 5,379 | Archduke Charles 2,632
   Strength: Murat 18,920 → 13,541 | Archduke Charles 31,690 → 29,058
   Berthier: "Murat stood alone, Sire. Ney never came."
   The war's cost now stands at 44,152 of our men.
map: unchanged (57 labels)
```

```
#0067  type Murat, retreat  ->  ok
  (typed and Enter)
view: <run>\frames\0067_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat bristles at the retreat order but obeys. 
========================================
  [!] FIGHTING RETREAT! (+10% bonus) [!]  
========================================
Murat's cavalry refuses to flee quietly!
  -> Cavalry charges ArchdukeCharles! 1,597 casualties inflicted.
[FIGHTING RETREAT] Total enemy casualties: 1,597 (+10% cavalry bonus)
Murat retreats from Swabia to Munich.  (135 lost to march) Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
Murat withdraws to Munich, bloodied but defiant.
Munich is Bavaria's soil — the corps standing there are fed by contract, about −156g more a turn. Murat's pursuit of Archduke Charles is set aside.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2654 of 2654 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   2,956 (+1,300 next turn)
   Inf:
   86,112
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, retreat
   Murat bristles at the retreat order but obeys.
   ========================================
   [!] FIGHTING RETREAT! (+10% bonus) [!]
   ========================================
   Murat's cavalry refuses to flee quietly!
   -> Cavalry charges ArchdukeCharles! 1,597 casualties inflicted.
   [FIGHTING RETREAT] Total enemy casualties: 1,597 (+10% cavalry bonus)
   Murat retreats from Swabia to Munich.  (135 lost to march) Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
   Murat withdraws to Munich, bloodied but defiant.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −156g more a turn. Murat's pursuit of Archduke Charles is set aside.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1943,451)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Deroy(1859,477)  ?(1501,602)  Castanos(1501,564)  ?(1940,583)  Mack(1940,556)  ?(1968,583)  Archduke John(2032,537)  Ney +4(1901,530)  Soult(1704,322)  Napoleon(1728,296)  Dumonceau(1691,418)  ?(2068,435)  ?(1959,376)  ?(1869,762)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1768,420)  12k(1716,446)  10k(1910,645)
```

```
#0068  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0068_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!

Income: 2468g | Charges of Empire: -80g | Admiralty: -90g | Blockade: -368g | Upkeep: -2032g (incl. 40g over-limit, 912g campaign pay) | Other: +1439g | Net: +1337g | Treasury: 4,293g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 4
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Rhineland /     Region captured: Rhineland (was France) (secured) /  / BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 78 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3272 of 3272 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,293 (+1,217 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   [!] Mack's broken army flees to Tyrol! (recovering for 3 turns)
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 20,094 (lead) + 40,148 committed (Davout, Lannes) = 60,242.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 937 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%)
   Defense: Mack (Defensive stance +15%, Terrain (Mountains) +25%)
   Casualties: Ney's own corps 809 | Mack 18,160
   Strength: Ney 20,094 → 19,285 → 18,900 after the advance | Mack 30,235 → 12,075
   Berthier: "Davout and Lannes arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire."
   The war's cost now stands at 38,773 of our men.
   ► Bernadotte, retreat to Swabia
   Bernadotte retreats from Franconia to Munich. Swabia cannot be reached, Sire — it is Austria-held soil and we are at war; Bernadotte falls back to Munich instead.  (170 lost to march) Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
   ► Massena, drill
   Massena is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
   "Archduke Charles, then." Murat takes the command and goes. Murat pursues Archduke Charles (at Franconia). Archduke Charles spotted at Franconia! Engaging!
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Combat] Adjacent allies bolster Murat's attack! (+6%)
   Murat faces a difficult fight. Archduke Charles holds the line. Casualties: Murat 5,379, Archduke Charles 2,632. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -268g, Austria -131g. Our treasury stands at 2,956 gold.
   (Murat stands down from his intended attack — your orders reached him in time.) Murat: "He is already beaten — he merely has not been told. I will tell him."
   [1/4 actions remaining]
   --- Berthier's Report ---
   Murat: "A horseman loses a field as he loses a race — by a length, not for good."
   Murat fought with particular ferocity — though one wonders if it was for France or for himself.
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Murat 5,379 | Archduke Charles 2,632
   Strength: Murat 18,920 → 13,541 | Archduke Charles 31,690 → 29,058
   Berthier: "Murat stood alone, Sire. Ney never came."
   The war's cost now stands at 44,152 of our men.
   ► Murat, retreat
   Murat bristles at the retreat order but obeys.
   ========================================
   [!] FIGHTING RETREAT! (+10% bonus) [!]
   ========================================
   Murat's cavalry refuses to flee quietly!
   -> Cavalry charges ArchdukeCharles! 1,597 casualties inflicted.
   [FIGHTING RETREAT] Total enemy casualties: 1,597 (+10% cavalry bonus)
   Murat retreats from Swabia to Munich.  (135 lost to march) Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
   Murat withdraws to Munich, bloodied but defiant.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −156g more a turn. Murat's pursuit of Archduke Charles is set aside.
   ► end turn
   ═══════════════════════════════════════
   TURN 5 BEGINS
   ═══════════════════════════════════════
   Income: 2468g | Charges of Empire: -80g | Admiralty: -90g | Blockade: -368g | Other: +1439g | Upkeep: -2032g | Net: +1337g
   Treasury: 4,293g
   Actions refreshed: 4/4
   Murat's army is recovering. Effectiveness penalty: -30%.
   Bernadotte's army is recovering. Effectiveness penalty: -30%.
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Teulie's army is recovering. Effectiveness penalty: -30%.
   Bavaria completes a supply depot at Munich.
   Supply shortage at Tyrol: Mack loses 126 troops
   Supply shortage at Tyrol: Archduke John loses 198 troops
   Supply shortage at Munich: Ney loses 1,134 troops
   Supply shortage at Munich: Davout loses 1,347 troops
   Supply shortage at Munich: Lannes loses 737 troops
   Supply shortage at Munich: Murat loses 804 troops
   Supply shortage at Munich: Bernadotte loses 1,009 troops
   Supply shortage at Munich: Deroy loses 697 troops
   Switzerland loyalty 86 (-3): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   Berthier reports that Soult appears envious of Davout's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2025,547)  France(1580,531)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Dumonceau(1616,379)  ?(1827,401)  Archduke Charles(1827,322)  ?(1955,579)  Mack(1958,538)  Archduke John(1956,489)  Deroy(1913,431)  Ney +4(1901,515)  ?(1551,406)  Castanos(1551,353)  Soult(1704,322)  Napoleon(1728,296)  ?(2068,435)  ?(1959,376)  ?(1869,762)  10k(1901,597)  ?(1893,372)  25k(1595,497)  12k(1551,454)  10k(1755,420)  12k(1710,420)  10k(1910,645)
```

```
#0069  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0069_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 78 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Soult seeks an audience @(3358,64)]  [icon: Napoleon arrived (x2) @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: The Marshalate awaits @(3484,64)]  [icon: The Moniteur is out @(3526,64)]  [icon: Treaty with Hesse @(3568,64)]  [+7]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franconia
   +6 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Franconia]
── BottomLeftUI (layer 0) [scrolled 1760 of 1760 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,293 (+1,217 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Sire — Rhineland has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Teulie's corps has been broken at Milan. He must reform before he fights again.
   • Sire — Murat was mauled at Franconia: a quarter of his corps — 5,379 men — lost in a single action.
   • Sire — St Petersburg now pays London 300 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 27 regions. Treasury: 4,293g (+1,337 by the accounts)
   The courts at war hold 31 regions. Estimated enemy strength: 45% of French forces (an estimate — 2 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 30,000 — Awaiting orders.
   - Davout — Munich — 21,112 — Awaiting orders.
   < Massena — Piedmont — 19,047 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 19,047 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Ney — Munich — 17,766 — Awaiting orders.
   < Bernadotte — Munich — 15,821 — Recovers T7. Trust:40
   ⚠ Fell back under fire — the corps is recovering.
   < Murat — Munich — 12,602 — Recovers T7.
   ⚠ Fell back under fire — the corps is recovering.
   - Lannes — Munich — 11,551 — Awaiting orders.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   > Dumonceau — Artois — 6,500 — Moving to Normandy — arrives next turn.
   < Teulie — Piedmont — 3,449 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 3,449 men. Morale:4%
   ⚠ Morale failing (4) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Deroy — Munich — 10,922 [confirmed]
   Mack — Tyrol — small force [partial]
   Archduke Charles — Rhineland — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Murat's army is recovering. Effectiveness penalty: -30%.
   Bernadotte's army is recovering. Effectiveness penalty: -30%.
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Teulie's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 5,031 men, at Munich.
   Switzerland loyalty 86 (-3): satellite drift, the lord's defeats
   Berthier reports that Soult appears envious of Davout's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 72).
   War exhaustion grows — France nears breaking point (exhaustion: 63).
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Franconia passes from Bavaria to Austria.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war come, having been asked.
   THE CAMP: France has massed 46,500 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
   The court of Bavaria takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 34 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franconia) — the homeland — 27 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Franconia) — the homeland — 27 of 28 provinces held (ticking: +1, +1/turn)  |  Settlement (this pair): White Peace (+8)
   War Purpose: Defense vs Russia (War for Franconia) — the homeland — 27 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0070  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0070_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 860 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Late November 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 95 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location:  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1760 of 1760 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,293 (+1,217 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0071  click ADMIRALTY  ->  ok
  (clicked at (2049, 283))
view: <run>\frames\0071_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 1080 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late November 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 45 sail of the line — readiness 50  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — the blockade lifts as the  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Teulie in Carniola>  <Land Teulie in Croatia>  <Land Teulie in Hungary>  <Land Teulie in Moravia>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1760 of 1760 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0072  scroll 1800 600 down 6  ->  ok
  (scrolled down 6 at (1800, 600))
view: <run>\frames\0072_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 354 of 1082 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late November 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 45 sail of the line — readiness 50  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — the blockade lifts as the  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Teulie in Carniola>  <Land Teulie in Croatia>  <Land Teulie in Hungary>  <Land Teulie in Moravia>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1760 of 1760 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0073  click Land Teulie in Croatia  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0073_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['ledger'], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   TEULIE ASKS:
   "The expedition is drawn up, Sire: Teulie with 3,449 men, Piedmont to Croatia. The transports slip past unseen 78 times in 100 (Britain watches at 100 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. If she is intercepted she meets Britain's 112 effective against our 40 — a decisive defeat is  …
   controls: [Sail for Croatia]  [Stand down]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 78 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── StrategicLedger (layer 50) [under a modal] [scrolled 354 of 1082 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1826 of 1826 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,293 (+1,217 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► land Teulie in Croatia
   Teulie requests clarification...
map: unchanged (56 labels)
```

```
#0074  click Stand down  ->  ok
  (clicked at (1829, 646))
view: <run>\frames\0074_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 78 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Soult seeks an audience @(3358,64)]  [icon: Napoleon arrived (x2) @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: The Marshalate awaits @(3484,64)]  [icon: The Moniteur is out @(3526,64)]  [icon: Treaty with Hesse @(3568,64)]  [+7]
── StrategicLedger (layer 50) [scrolled 354 of 1082 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1892 of 1892 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,293 (+1,217 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (56 labels)
```

```
#0075  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0075_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franconia
   +6 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Franconia]
── BottomLeftUI (layer 0) [scrolled 1892 of 1892 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► land Teulie in Croatia
   Teulie requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (56 labels)
```

```
#0076  type what if Davout attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0076_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout stands at Munich, beyond reach of Archduke Charles at Rhineland this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2004 of 2004 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,293 (+1,217 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Davout attacks Archduke Charles
   Davout stands at Munich, beyond reach of Archduke Charles at Rhineland this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
map: unchanged (56 labels)
```

```
#0077  type what if Soult attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0077_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult stands at Flanders, beyond reach of Archduke Charles at Rhineland this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2114 of 2114 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,293 (+1,217 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Soult attacks Archduke Charles
   Soult stands at Flanders, beyond reach of Archduke Charles at Rhineland this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
map: unchanged (56 labels)
```

```
#0078  type is Paris safe  ->  ok
  (typed and Enter)
view: <run>\frames\0078_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Paris is ours, Sire, held by a garrison of 25,000. No enemy corps stands within two marches of it, so far as our intelligence reaches — it looks safe today.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2203 of 2203 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,293 (+1,217 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► is Paris safe
   Paris is ours, Sire, held by a garrison of 25,000. No enemy corps stands within two marches of it, so far as our intelligence reaches — it looks safe today.
map: unchanged (56 labels)
```

```
#0079  type Davout, pursue Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0079_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout pursues Archduke Charles (at Rhineland). Moves to Swabia. The province is secured. Davout: "I will follow — at a distance that leaves him no chance to turn on us."
── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Soult seeks an audience @(3358,64)]  [icon: Napoleon arrived (x2) @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: The Marshalate awaits @(3484,64)]  [icon: The Moniteur is out @(3526,64)]  [icon: Treaty with Hesse @(3568,64)]  [+7]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franconia
   +8 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Franconia]
── BottomLeftUI (layer 0) [scrolled 2336 of 2336 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,293 (+1,345 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, pursue Archduke Charles
   Davout pursues Archduke Charles (at Rhineland). Moves to Swabia. The province is secured. Davout: "I will follow — at a distance that leaves him no chance to turn on us."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,551)  France(1600,529)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Dumonceau(1616,379)  Davout(1860,464)  ?(1827,401)  Archduke Charles(1827,322)  ?(1955,579)  Mack(1958,538)  Archduke John(1956,490)  Deroy(1921,452)  Ney +3(1901,515)  ?(1551,406)  Castanos(1551,353)  Soult(1704,322)  Napoleon(1728,296)  ?(2068,435)  ?(1959,376)  ?(1869,762)  10k(1901,597)  ?(1893,372)  25k(1595,497)  12k(1551,454)  10k(1755,420)  12k(1710,420)  10k(1910,645)
```

```
#0080  type Ney, support Davout  ->  ok
  (typed and Enter)
view: <run>\frames\0080_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['objection'], region_panel=no
reply: ok Ney firmly objects: 'March to another man's guns, Sire? Give me a battle of my own.' (Trust him and he will attack Archduke John at Tyrol instead.)
── ObjectionDialog (layer 108) ──
   NEY'S CONCERN
   "Ney firmly objects: 'March to another man's guns, Sire? Give me a battle of my own.' (Trust him and he will attack Archduke John at Tyrol instead.)"
   Personality: Aggressive
   Trust: 72 (Reliable)
   Track record: Neutral
   Authority: 95
   controls: [Trust: Ney attacks Archduke John (1 AP, +3 trust)]  [Proceed with Support (1 AP, -10 trust)]  [Accept: Timed Support (3 turns) (1 AP, +3 trust)]  [Cancel the Order (no cost)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1854 of 1854 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,293 (+1,345 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ⚠ Morale failing (4) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Deroy — Munich — 10,922 [confirmed]
   Mack — Tyrol — small force [partial]
   Archduke Charles — Rhineland — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Murat's army is recovering. Effectiveness penalty: -30%.
   Bernadotte's army is recovering. Effectiveness penalty: -30%.
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Teulie's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 5,031 men, at Munich.
   Switzerland loyalty 86 (-3): satellite drift, the lord's defeats
   Berthier reports that Soult appears envious of Davout's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 72).
   War exhaustion grows — France nears breaking point (exhaustion: 63).
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Franconia passes from Bavaria to Austria.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war come, having been asked.
   THE CAMP: France has massed 46,500 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
   The court of Bavaria takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 34 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franconia) — the homeland — 27 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Franconia) — the homeland — 27 of 28 provinces held (ticking: +1, +1/turn)  |  Settlement (this pair): White Peace (+8)
   War Purpose: Defense vs Russia (War for Franconia) — the homeland — 27 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   ► land Teulie in Croatia
   Teulie requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
   ► what if Davout attacks Archduke Charles
   Davout stands at Munich, beyond reach of Archduke Charles at Rhineland this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   ► what if Soult attacks Archduke Charles
   Soult stands at Flanders, beyond reach of Archduke Charles at Rhineland this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   ► is Paris safe
   Paris is ours, Sire, held by a garrison of 25,000. No enemy corps stands within two marches of it, so far as our intelligence reaches — it looks safe today.
   ► Davout, pursue Archduke Charles
   Davout pursues Archduke Charles (at Rhineland). Moves to Swabia. The province is secured. Davout: "I will follow — at a distance that leaves him no chance to turn on us."
   [2/4 actions remaining]
   ► Ney, support Davout
   ⚠ Marshal Ney raises concerns...
map: unchanged (57 labels)
```

```
#0081  type Lannes, support Davout  ->  ERROR: the command line is not taking orders now (it is disabled)
view: <run>\frames\0081_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['objection'], region_panel=no
── ObjectionDialog (layer 108): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1854 of 1854 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Davout pursues Archduke Charles (at Rhineland). Moves to Swabia. The province is secured. Davout: "I will follow — at a distance that leaves him no chance to turn on us."
   [2/4 actions remaining]
   ► Ney, support Davout
   ⚠ Marshal Ney raises concerns...
map: unchanged (57 labels)
```

```
#0082  click Cancel the Order  ->  ok
  (clicked at (2015, 669))
view: <run>\frames\0082_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Soult seeks an audience @(3358,64)]  [icon: Napoleon arrived (x2) @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: The Marshalate awaits @(3484,64)]  [icon: The Moniteur is out @(3526,64)]  [icon: Treaty with Hesse @(3568,64)]  [+7]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franconia
   +8 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Franconia]
── BottomLeftUI (layer 0) [scrolled 1942 of 1942 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,293 (+1,345 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► You withdraw the order.
   The order to Ney is withdrawn, Sire — nothing is spent.
map: unchanged (57 labels)
```

```
#0083  type Lannes, support Davout  ->  ok
  (typed and Enter)
view: <run>\frames\0083_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['objection'], region_panel=no
reply: ok Lannes respectfully raises concerns: 'March to another man's guns, Sire? Give me a battle of my own.' (Trust him and he will attack Archduke John at Tyrol instead.)
── ObjectionDialog (layer 108) ──
   LANNES'S ADVICE
   "Lannes respectfully raises concerns: 'March to another man's guns, Sire? Give me a battle of my own.' (Trust him and he will attack Archduke John at Tyrol instead.)"
   Personality: Aggressive
   Trust: 85 (Loyal)
   Track record: Neutral
   Authority: 95
   controls: [Trust: Lannes attacks Archduke John (1 AP, +2 trust)]  [Proceed with Support (1 AP, -5 trust)]  [Accept: Timed Support (3 turns) (1 AP, +3 trust)]  [Cancel the Order (no cost)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2053 of 2053 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,293 (+1,345 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Lannes, support Davout
   ⚠ Marshal Lannes raises concerns...
map: unchanged (57 labels)
```

```
#0084  click Cancel the Order  ->  ok
  (clicked at (2015, 669))
view: <run>\frames\0084_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Soult seeks an audience @(3358,64)]  [icon: Napoleon arrived (x2) @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: The Marshalate awaits @(3484,64)]  [icon: The Moniteur is out @(3526,64)]  [icon: Treaty with Hesse @(3568,64)]  [+7]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franconia
   +8 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Franconia]
── BottomLeftUI (layer 0) [scrolled 2142 of 2142 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,293 (+1,345 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► You withdraw the order.
   The order to Lannes is withdrawn, Sire — nothing is spent.
map: unchanged (57 labels)
```

```
#0085  click Generals  ->  ok
  (clicked at (228, 18))
view: <run>\frames\0085_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 6570 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  / SEEKS AN AUDIENCE — Soult /   / [3] Soult  [Infantry]  France / IV Corps - marching for the Speyer crossing from its Lorraine camps, 10,000 of its best carved away to form the Emperor's Guard. A superb tactician who executes the Emperor's plan to the letter, exactly on the appointed …
   controls: [Pin]  [icon @(2213,236)]  <Hear him — he seeks an audience>  <Fortify>  <Drill>  <Hold (1 AP)>  <▸ the doctrine>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fall back>  <Fall back>  <Fortify>  <Drill>  <Hold (2 AP)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2142 of 2142 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,293 (+1,345 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Lannes, support Davout
   ⚠ Marshal Lannes raises concerns...
   ► You withdraw the order.
   The order to Lannes is withdrawn, Sire — nothing is spent.
map: unchanged (57 labels)
```

```
#0086  click Hear him  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0086_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   SOULT — Marshal Soult seeks an audience
   Give him a command is closed — There is no enemy within his reach to send him against.
   "My orders have been carried out exactly, Sire. I note that Davout was given orders worth carrying out." /  / Sire, Soult's dispatches have become unusually detailed — obsessively so. Staff report he feels his current assignment is... beneath his abilities. /  / What each answer does / • Let it stand (Free) — Free, and it fixes nothing. For 2 more turns he brings about half the weight of his 30,00 …
   controls: [Let it stand   [Free]]  [Reassign   [1 AP]]  [Rebuke]  [Give him a command   [1 AP]](disabled: There is no enemy within his reach to send him against.)  [Later (he will return)]
── TopBar (layer 75) [under a modal]: unchanged
── MarshalManagement (layer 50) [under a modal] [scrolled 0 of 6570 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2142 of 2142 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,293 (+1,345 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Lannes, support Davout
   ⚠ Marshal Lannes raises concerns...
   ► You withdraw the order.
   The order to Lannes is withdrawn, Sire — nothing is spent.
map: unchanged (57 labels)
```

```
#0087  look  ->  ok
  (a fresh frame)
view: <run>\frames\0087_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── MarshalManagement (layer 50) [under a modal] [scrolled 0 of 6570 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2142 of 2142 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Lannes, support Davout
   ⚠ Marshal Lannes raises concerns...
   ► You withdraw the order.
   The order to Lannes is withdrawn, Sire — nothing is spent.
map: unchanged (57 labels)
```

```
#0088  click Let it stand  ->  ok
  (clicked at (1613, 702))
view: <run>\frames\0088_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived (x2) @(3358,64)]  [icon: Soult arrived @(3400,64)]  [icon: The Marshalate awaits @(3442,64)]  [icon: The Moniteur is out @(3484,64)]  [icon: Treaty with Hesse @(3526,64)]  [icon: Treaty with Papal States @(3568,64)]  [+6]
── MarshalManagement (layer 50) [scrolled 0 of 6524 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  /   OUR DOCTRINE — The Corps System  ▸ the doctrine /  /   THE EMPEROR /   / [8] Napoleon  [Infantry]  France / In the field at Flanders — The Presence goes where he stands. /   ★ The Presence  +10% here at Flanders  Every French corps fighting in the Emperor's province gains +10% att …
   controls: [Pin]  [icon @(2213,236)]  <▸ the doctrine>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fortify>  <Drill>  <Hold (1 AP)>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fall back>  <Fall back>  <Fortify>  <Drill>  <Hold (2 AP)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2187 of 2187 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,293 (+1,345 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Soult's grievance runs its course.
map: unchanged (57 labels)
```

```
#0089  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0089_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franconia
   +8 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Franconia]
── BottomLeftUI (layer 0) [scrolled 2187 of 2187 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ⚠ Marshal Lannes raises concerns...
   ► You withdraw the order.
   The order to Lannes is withdrawn, Sire — nothing is spent.
   Soult's grievance runs its course.
map: unchanged (57 labels)
```

```
#0090  click Diplomacy  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0090_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 3330 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 7/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  /   Britain [Coalition Member] — WAR  Relation: -90 (Hostile) /   Laws: the Orders in Council and the Militia Transfer (300 gold a turn) /   Doctrine: The Line Holds; flaw: Irreplaceable (uncured — the Militia Transfer would end it once the Horse G …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2187 of 2187 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,293 (+1,345 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ⚠ Marshal Lannes raises concerns...
   ► You withdraw the order.
   The order to Lannes is withdrawn, Sire — nothing is spent.
   Soult's grievance runs its course.
map: unchanged (57 labels)
```

```
#0091  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0091_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franconia
   +8 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Franconia]
── BottomLeftUI (layer 0) [scrolled 2187 of 2187 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ⚠ Marshal Lannes raises concerns...
   ► You withdraw the order.
   The order to Lannes is withdrawn, Sire — nothing is spent.
   Soult's grievance runs its course.
map: unchanged (57 labels)
```

```
#0092  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0092_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 46 sail — readiness 50 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing), and Britain's blockade rots her 5 a turn at anchor — the blockade lifts as the enemy squadrons come home to the camp; readiness then recovers +5/turn to 75. 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived (x2) @(3358,64)]  [icon: Soult arrived @(3400,64)]  [icon: The Marshalate awaits @(3442,64)]  [icon: The Moniteur is out @(3484,64)]  [icon: Treaty with Hesse @(3526,64)]  [icon: Treaty with Papal States @(3568,64)]  [+6]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2342 of 2342 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   3,893 (+1,365 next turn)
   Inf:
   87,712
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 46 sail — readiness 50 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing), and Britain's blockade rots her 5 a turn at anchor — the blockade lifts as the enemy squadrons come home to the camp; readiness then recovers +5/turn to 75. 0 more keels possible this turn.
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,551)  France(1600,529)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Dumonceau(1616,379)  Davout(1860,464)  ?(1827,401)  Archduke Charles(1827,322)  ?(1955,579)  Mack(1958,538)  Archduke John(1956,490)  Deroy(1921,452)  Ney +3(1901,515)  ?(1551,406)  Castanos(1551,353)  Soult(1704,322)  Napoleon(1728,296)  ?(2068,435)  ?(1959,376)  ?(1869,762)  10k(1901,597)  ?(1893,372)  25k(1595,497)  12k(1551,454)  10k(1755,420)  12k(1710,420)  10k(1910,645)
```

```
#0093  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0093_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!

Income: 2290g | Charges of Empire: -167g | Admiralty: -92g | Upkeep: -2024g (incl. 52g over-limit, 900g campaign pay) | Other: +1411g | Net: +1418g | Spent: 400g | Treasury: 5,311g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 69 px] ──
   ENEMY PHASE - Turn 5
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Lorraine /     Region captured: Lorraine (was France) (secured) / - Archduke Charles moves to Franche-Comte — Franche-Comte falls (was France) and is secured /  / SPAIN / ──────────────────────────── / - Castanos breaks from square / - Castanos fortifies position /  / BAVARIA / ──────────────────────────── / - Deroy moves to Swabi …
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 78 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2301 of 2301 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,303 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   War exhaustion grows — France nears breaking point (exhaustion: 63).
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Franconia passes from Bavaria to Austria.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war come, having been asked.
   THE CAMP: France has massed 46,500 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
   The court of Bavaria takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 34 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franconia) — the homeland — 27 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Franconia) — the homeland — 27 of 28 provinces held (ticking: +1, +1/turn)  |  Settlement (this pair): White Peace (+8)
   War Purpose: Defense vs Russia (War for Franconia) — the homeland — 27 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   ► land Teulie in Croatia
   Teulie requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
   ► what if Davout attacks Archduke Charles
   Davout stands at Munich, beyond reach of Archduke Charles at Rhineland this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   ► what if Soult attacks Archduke Charles
   Soult stands at Flanders, beyond reach of Archduke Charles at Rhineland this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   ► is Paris safe
   Paris is ours, Sire, held by a garrison of 25,000. No enemy corps stands within two marches of it, so far as our intelligence reaches — it looks safe today.
   ► Davout, pursue Archduke Charles
   Davout pursues Archduke Charles (at Rhineland). Moves to Swabia. The province is secured. Davout: "I will follow — at a distance that leaves him no chance to turn on us."
   [2/4 actions remaining]
   ► Ney, support Davout
   ⚠ Marshal Ney raises concerns...
   ► You withdraw the order.
   The order to Ney is withdrawn, Sire — nothing is spent.
   ► Lannes, support Davout
   ⚠ Marshal Lannes raises concerns...
   ► You withdraw the order.
   The order to Lannes is withdrawn, Sire — nothing is spent.
   Soult's grievance runs its course.
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 46 sail — readiness 50 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing), and Britain's blockade rots her 5 a turn at anchor — the blockade lifts as the enemy squadrons come home to the camp; readiness then recovers +5/turn to 75. 0 more keels possible this turn.
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2290g | Charges of Empire: -167g | Admiralty: -92g | Other: +1411g | Upkeep: -2024g | Net: +1418g | Spent: 400g
   Treasury: 5,311g
   Actions refreshed: 4/4
   Murat's army is recovering. Effectiveness penalty: -15%.
   Bernadotte's army is recovering. Effectiveness penalty: -15%.
   Massena's army has fully recovered and is combat ready.
   Teulie's army is recovering. Effectiveness penalty: -15%.
   Supply shortage at Munich: Ney loses 608 troops
   Supply shortage at Munich: Lannes loses 395 troops
   Supply shortage at Munich: Murat loses 431 troops
   Supply shortage at Munich: Bernadotte loses 541 troops
   Garrison at Milan reinforced: 5,000 -> 7,000
   Switzerland loyalty 84 (-2): satellite drift
   Britain subsidizes Austria with 300 gold.
   Bernadotte's resentment of Davout has cooled with time.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2017,546)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Bavaria(1872,518)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,481)  Mack(2024,443)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Davout(1847,464)  Deroy(1871,438)  ?(1948,602)  Archduke John(1948,575)  ?(1813,517)  Archduke Charles(1813,490)  Ney +3(1901,547)  Castanos(1539,399)  Dumonceau(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1490,371)  Moore(1490,344)  ?(2072,435)  ?(1959,376)  ?(1869,762)  10k(1901,603)  ?(1893,372)  25k(1595,497)  12k(1551,454)  10k(1755,420)  12k(1710,420)  ?(1490,427)  7k(1910,645)
```

```
#0094  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0094_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 78 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3351,64)]  [icon: Britain binds Austria to the war @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Envoy from Austria @(3477,64)]  [icon: Dumonceau arrived @(3519,64)]  [icon: Napoleon arrived (x2) @(3561,64)]  [+11]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   -3 →
   T:5
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]
── BottomLeftUI (layer 0) [scrolled 2114 of 2114 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,303 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   --- Strategic Order Updates ---
   Davout: Davout is pursuing Archduke Charles.
   Dumonceau: Dumonceau arrives at Normandy. Dumonceau: "It is done. I took the liberty of posting pickets."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Lorraine has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Ney, Lannes, Murat and Bernadotte stand 55,765 men at Munich, which feeds 45,000. 10,765 too many. 7,006 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the province. Milan can feed 75,000 more and Swabia can feed 28,278 more — a corps marched there ends it.
   SITUATION
   France holds 25 regions. Treasury: 5,311g (+1,418 by the accounts)
   The courts at war hold 32 regions. Estimated enemy strength: 58% of French forces (an estimate — 2 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 30,000 — Awaiting orders.
   > Davout — Swabia — 20,854 — Pursuing Archduke Charles.
   - Massena — Piedmont — 19,047 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 19,047 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Ney — Munich — 17,158 — Awaiting orders.
   ⚠ Starving — supply has failed at Munich two turns running.
   < Bernadotte — Munich — 15,280 — Recovers T7. Trust:40
   ⚠ Fell back under fire — the corps is recovering.
   < Murat — Munich — 12,171 — Recovers T7.
   ⚠ Fell back under fire — the corps is recovering.
   - Lannes — Munich — 11,156 — Awaiting orders.
   ⚠ Starving — supply has failed at Munich two turns running.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Dumonceau — Normandy — 6,500 — Awaiting orders.
   < Teulie — Piedmont — 3,449 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 3,449 men. Morale:4%
   ⚠ Morale failing (4) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Deroy — Swabia — 10,868 [confirmed]
   Castanos — Normandy — 14,120 [confirmed]
   Mack — Bohemia — substantial force [partial]
   Archduke Charles — Franche-Comte — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Moore — London — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Murat's army is recovering. Effectiveness penalty: -15%.
   Bernadotte's army is recovering. Effectiveness penalty: -15%.
   Massena's army has fully recovered and is combat ready.
   Teulie's army is recovering. Effectiveness penalty: -15%.
   Supply cost you 1,975 men, at Munich.
   Switzerland loyalty 84 (-2): satellite drift
   Bernadotte's resentment of Davout has cooled with time.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   An envoy from Austria has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   France hands Swabia back to Bavaria — the liberated soil comes home.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   The court of Bavaria takes up a new design: Revanche.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Austria — Armistice
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0095  look  ->  ok
  (a fresh frame)
view: <run>\frames\0095_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2114 of 2114 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0096  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0096_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 2071 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 6 — Early December 1805 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Lorraine has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province agai …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (2)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2114 of 2114 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,303 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0097  click Open Envoys  ->  ok
  (clicked at (2084, 731))
view: <run>\frames\0097_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Austria
   Proposal
   Turn 5
   Incoming proposal: Armistice
   Terms: Proposal: Armistice
   A great court's letter is answered in full — open to accept, haggle or refuse.
   WAITING
   Switzerland
   Proposal
   Turn 6
   Incoming proposal: Client's Petition
   Terms: Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. · Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now +0); nothing is charged. · Left unanswered at the turn's end, the petition lapses — an …
   A client's petition is granted or refused in full — open to decide.
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Franche-Comte
   -3 →
   T:5
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2114 of 2114 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0098  click#1 Open  ->  ok
  (clicked at (2191, 294))
view: <run>\frames\0098_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 222 px] ──
   DIPLOMATIC ENVOY / Metternich (Schemer) of Austria /  / Proposes: Armistice / Terms: / Mutual: /   - Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads -1 for France (9 battles, 3 drawn, 2 decisives kept); the war is 5 turns old and stays so; exhaustion holds. N …
   controls: [Accept]  [Let Talleyrand haggle (1 DP)]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2114 of 2114 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,303 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0099  look  ->  ok
  (a fresh frame)
view: <run>\frames\0099_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 222 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2114 of 2114 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0100  click Accept  ->  ok
  (clicked at (1574, 878))
view: <run>\frames\0100_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 78 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2180 of 2180 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,307 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria.
map: unchanged (60 labels)
```

```
#0101  click Grant  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0101_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 78 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3351,64)]  [icon: Dumonceau arrived @(3393,64)]  [icon: Napoleon arrived (x2) @(3435,64)]  [icon: Soult arrived @(3477,64)]  [icon: Treaty with Austria @(3519,64)]  [icon: Armistice Accepted @(3561,64)]  [+11]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2246 of 2246 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,082 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0102  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0102_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 838 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early December 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 95 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location: …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2246 of 2246 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,082 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0103  click ADMIRALTY  ->  ok
  (clicked at (2049, 283))
view: <run>\frames\0103_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 904 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early December 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 46 sail of the line — readiness 55  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: Staged: 46,500 men have stood 3 …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Teulie in East Anglia>  <Land Teulie in Cornwall>  <Land Teulie in Midlands>  <Land Teulie in Wales>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2246 of 2246 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0104  scroll 1800 600 down 5  ->  ok
  (scrolled down 5 at (1800, 600))
view: <run>\frames\0104_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 288 of 906 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early December 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 46 sail of the line — readiness 55  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: Staged: 46,500 men have stood 3 …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Teulie in East Anglia>  <Land Teulie in Cornwall>  <Land Teulie in Midlands>  <Land Teulie in Wales>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2246 of 2246 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0105  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0105_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2246 of 2246 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0106  type Dumonceau, land in Ireland  ->  ok
  (typed and Enter)
view: <run>\frames\0106_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1673 of 1673 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,082 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   < Bernadotte — Munich — 15,280 — Recovers T7. Trust:40
   ⚠ Fell back under fire — the corps is recovering.
   < Murat — Munich — 12,171 — Recovers T7.
   ⚠ Fell back under fire — the corps is recovering.
   - Lannes — Munich — 11,156 — Awaiting orders.
   ⚠ Starving — supply has failed at Munich two turns running.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Dumonceau — Normandy — 6,500 — Awaiting orders.
   < Teulie — Piedmont — 3,449 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 3,449 men. Morale:4%
   ⚠ Morale failing (4) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Deroy — Swabia — 10,868 [confirmed]
   Castanos — Normandy — 14,120 [confirmed]
   Mack — Bohemia — substantial force [partial]
   Archduke Charles — Franche-Comte — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Moore — London — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Murat's army is recovering. Effectiveness penalty: -15%.
   Bernadotte's army is recovering. Effectiveness penalty: -15%.
   Massena's army has fully recovered and is combat ready.
   Teulie's army is recovering. Effectiveness penalty: -15%.
   Supply cost you 1,975 men, at Munich.
   Switzerland loyalty 84 (-2): satellite drift
   Bernadotte's resentment of Davout has cooled with time.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   An envoy from Austria has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   France hands Swabia back to Bavaria — the liberated soil comes home.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   The court of Bavaria takes up a new design: Revanche.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Austria — Armistice
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
map: unchanged (60 labels)
```

```
#0107  click_at 1335 245  ->  ok
  (clicked at (1335, 245) on MapArea '100' (Control, layer 0))
view: <run>\frames\0107_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 287 px] ──
   Ulster
   Britain  City · Plains / Stripped? unknown — scout it / ACTIONS /     Land Dumonceau here    6,500 men from Normandy · 72 in 100 slip past /       What moves the odds: a won diversion first (30 in 100) → 95 · a 5,000-man corps → 75 · the fleet at readiness 75 (4 turns in port) → 74 /     Land Teulie here    3,449 men from Piedmont · 78 in 100 slip past /       What moves the odds: a won diversion  …
   controls: [icon @(535,73)]  <Land Dumonceau here>  <Land Teulie here>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1673 of 1673 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,082 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
map: unchanged (60 labels)
```

```
#0108  click Land Dumonceau here  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0108_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   DUMONCEAU ASKS:
   "The expedition is drawn up, Sire: Dumonceau with 6,500 men, Normandy to Ulster. The transports slip past unseen 72 times in 100 (Britain watches at 112 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. If she is intercepted she meets Britain's 112 effective against our 45 — a decisive defeat i …
   controls: [Sail for Ulster]  [Stand down]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 78 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1739 of 1739 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,311 (+1,082 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► land Dumonceau in Ulster
   Dumonceau requests clarification...
map: unchanged (60 labels)
```

```
#0109  look  ->  ok
  (a fresh frame)
view: <run>\frames\0109_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1739 of 1739 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
   ► land Dumonceau in Ulster
   Dumonceau requests clarification...
map: unchanged (60 labels)
```

```
#0110  click Sail for Ulster  ->  ok
  (clicked at (1829, 614))
view: <run>\frames\0110_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE SAIL LOST
   BRITAIN SAIL LOST
   0
   0
   Gravina
   33 → 15 sail
   Verhuell
   Senyavin
   12 → 5 sail
   20 → 19 sail
   ⚔
   Villeneuve ◆
   Nelson ◆
   46 → 20 sail
   100 → 97 sail
   THE GREAT FLEET ACTION
   click anywhere to skip ▸
   THE FRANCE–BRITAIN ACTION · TURN 6
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 78 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 20 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3351,64)]  [icon: Dumonceau arrived @(3393,64)]  [icon: Napoleon arrived (x2) @(3435,64)]  [icon: Soult arrived @(3477,64)]  [icon: Treaty with Austria @(3519,64)]  [icon: Armistice Accepted @(3561,64)]  [+11]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 5t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   5,311 (+1,124 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > land Dumonceau in Ulster confirmed
   INTERCEPTED AT SEA: the British squadrons catch the transports off Ulster. Dumonceau loses 1,950 men to the guns and the water before the convoy scatters home. The escorting fleet is brought to action and beaten decisively — France loses 26 sail; Spain 18 and Holland 7 beside her.
   [2/4 actions remaining]
   ⚓ View the action
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2017,546)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Bavaria(1872,518)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  20(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,481)  Mack(2024,443)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Davout(1847,464)  Deroy(1871,438)  ?(1948,602)  Archduke John(1948,575)  ?(1813,517)  Archduke Charles(1813,490)  Ney +3(1901,547)  Castanos(1539,399)  Dumonceau(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1490,371)  Moore(1490,344)  ?(2072,435)  ?(1959,376)  ?(1869,762)  10k(1901,603)  ?(1893,372)  25k(1595,497)  12k(1551,454)  10k(1755,420)  12k(1710,420)  ?(1490,427)  7k(1910,645)
```

```
#0111  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0111_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   > land Dumonceau in Ulster confirmed
   INTERCEPTED AT SEA: the British squadrons catch the transports off Ulster. Dumonceau loses 1,950 men to the guns and the water before the convoy scatters home. The escorting fleet is brought to action and beaten decisively — France loses 26 sail; Spain 18 and Holland 7 beside her.
   [2/4 actions remaining]
   ⚓ View the action
map: unchanged (60 labels)
```

```
#0112  type Ney, march to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0112_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins march to Swabia. Moves to Swabia.
Swabia feeds 60,000; the 48,709 men standing there would lose ~756 a turn to crowding — too many corps on one province. Ney: "Good. An army rots standing still."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2027 of 2027 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   5,311 (+1,148 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, march to Swabia
   Ney begins march to Swabia. Moves to Swabia.
   Swabia feeds 60,000; the 48,709 men standing there would lose ~756 a turn to crowding — too many corps on one province. Ney: "Good. An army rots standing still."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2017,546)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Bavaria(1872,518)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  20(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,481)  Mack(2024,443)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1860,438)  Deroy(1871,375)  ?(1948,602)  Archduke John(1948,575)  ?(1813,517)  Archduke Charles(1793,490)  Lannes(1888,547)  Murat(1901,490)  Bernadotte(1918,464)  Castanos(1539,399)  Dumonceau(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1490,371)  Moore(1490,344)  ?(2072,435)  ?(1959,376)  ?(1869,762)  10k(1901,603)  ?(1915,434)  25k(1595,497)  12k(1551,454)  10k(1755,420)  12k(1710,420)  ?(1490,427)  7k(1910,645)
```

```
#0113  type Lannes, march to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0113_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Not enough actions! Need 2, have 0 — Lannes cannot march to Swabia today.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2116 of 2116 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   5,311 (+1,148 next turn)
   Inf:
   89,174
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, march to Swabia
   Not enough actions! Need 2, have 0 — Lannes cannot march to Swabia today.
map: unchanged (63 labels)
```

```
#0114  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0114_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 6 ended. Turn 7 begins!

Income: 2290g | Contributions: -110g | Charges of Empire: -413g | Admiralty: -40g | Upkeep: -1928g (incl. 36g over-limit, 852g campaign pay) | Other: +1139g | Net: +938g | Treasury: 6,249g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 531 px] ──
   ENEMY PHASE - Turn 6
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Deroy /     Third Battle of Swabia /     Archduke Charles: 572 casualties, 23,622 remaining /     Deroy: 4,968 casualties, 5,900 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) — and advances into Swabia /     Swabia CAPTURED! (was Bavaria) (secured) /     Deroy forced to retreat! /     ⚔ View the f …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 75 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 20 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2030 of 2032 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,249 (+808 next turn)
   Inf:
   90,436
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
   ► land Dumonceau in Ulster
   Dumonceau requests clarification...
   > land Dumonceau in Ulster confirmed
   INTERCEPTED AT SEA: the British squadrons catch the transports off Ulster. Dumonceau loses 1,950 men to the guns and the water before the convoy scatters home. The escorting fleet is brought to action and beaten decisively — France loses 26 sail; Spain 18 and Holland 7 beside her.
   [2/4 actions remaining]
   ⚓ View the action
   ► Ney, march to Swabia
   Ney begins march to Swabia. Moves to Swabia.
   Swabia feeds 60,000; the 48,709 men standing there would lose ~756 a turn to crowding — too many corps on one province. Ney: "Good. An army rots standing still."
   [0/4 actions remaining]
   ► Lannes, march to Swabia
   Not enough actions! Need 2, have 0 — Lannes cannot march to Swabia today.
   ► end turn
   ═══════════════════════════════════════
   TURN 7 BEGINS
   ═══════════════════════════════════════
   Income: 2290g | Contributions: -110g | Charges of Empire: -413g | Admiralty: -40g | Other: +1139g | Upkeep: -1928g | Net: +938g
   Treasury: 6,249g
   Actions refreshed: 4/4
   Murat's army has fully recovered and is combat ready.
   Bernadotte's army has fully recovered and is combat ready.
   Teulie's army has fully recovered and is combat ready.
   Supply shortage at Swabia: Ney loses 570 troops — 97 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Davout loses 699 troops — 119 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Archduke Charles loses 467 troops
   Supply shortage at Munich: Lannes loses 567 troops — 80 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Munich: Murat loses 619 troops — 87 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Munich: Bernadotte loses 777 troops — 109 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Munich: Archduke John loses 316 troops
   Garrison at Munich reinforced: 0 -> 2,000
   Garrison at Milan reinforced: 7,000 -> 9,000
   Holland loyalty 91 (-3): the contingent's dead, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 87 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Teulie's contingent comes home decimated — 3,449 of 7,500 men. The Kingdom of Italy counts its widows (-5 loyalty).
   Britain subsidizes Russia with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: Open Borders → Peace.
   Prussia declares war on Hanover — The Hanoverian Prize; declaring Hanover.
   Soult seeks an audience, Sire — he asks for a command of his own.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat's resentment of Ney has cooled with time.
   Soult's resentment of Davout has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   Ney is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Nivernais; he has 5 turns of safe passage.
   Davout is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Nivernais; he has 5 turns of safe passage.
   Lannes is on the wrong side of the frontier at Munich, Sire — the ground changed hands under him. Berthier has put him on the road home to Nivernais; he has 5 turns of safe passage.
   Murat is on the wrong side of the frontier at Munich, Sire — the ground changed hands under him. Berthier has put him on the road home to Nivernais; he has 5 turns of safe passage.
   Bernadotte is on the wrong side of the frontier at Munich, Sire — the ground changed hands under him. Berthier has put him on the road home to Nivernais; he has 5 turns of safe passage.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  20(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1860,438)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Lannes(1888,535)  Murat(1889,509)  Bernadotte(1918,483)  Archduke John(1959,457)  Castanos(1539,399)  Dumonceau(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1482,366)  Moore(1482,328)  Wellesley(1498,302)  ?(2068,435)  ?(1976,376)  ?(1869,762)  2k(1901,591)  25k(1595,497)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1490,427)  9k(1910,645)
```

```
#0115  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0115_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   AUSTRIA LOSSES
   BAVARIA LOSSES
   0
   0
   ⚔
   Archduke Charles ◆
   Deroy ◆
   24,194 → 23,622 → 23,215 after the advance
   10,868 → 5,900
   THIRD BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 6
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 75 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 20 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from the Kingdom of Italy @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Bavaria Eliminated! @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Marshal Soult asks for a command @(3561,64)]  [+17]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 4t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1936 of 1936 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,249 (+808 next turn)
   Inf:
   90,436
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   SITUATION
   France holds 25 regions. Treasury: 6,249g (+938 by the accounts)
   The courts at war hold 22 regions. Estimated enemy strength: 29% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 30,000 — Awaiting orders.
   > Davout — Swabia — 20,155 — Moving to Nivernais — 2 turns out.
   - Massena — Piedmont — 19,047 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 19,047 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   > Ney — Swabia — 16,417 — Moving to Nivernais — 2 turns out.
   > Bernadotte — Munich — 14,503 — Moving to Nivernais — 2 turns out. Trust:40
   ⚠ Starving — supply has failed at Munich three turns running.
   > Murat — Munich — 11,552 — Moving to Nivernais — arrives next turn.
   ⚠ Starving — supply has failed at Munich three turns running.
   > Lannes — Munich — 10,589 — Moving to Nivernais — 2 turns out.
   ⚠ Starving — supply has failed at Munich three turns running.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 22,625 [confirmed]
   Archduke John — Munich — 8,947 [confirmed]
   Castanos — Normandy — 14,120 [confirmed]
   Moore — London — substantial force [partial]
   Paget — Gascony — screening force [partial]
   Wellesley — London — small force [partial]
   Brunswick — Berlin — large force [stale - T4]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Murat's army has fully recovered and is combat ready.
   Bernadotte's army has fully recovered and is combat ready.
   Teulie's army has fully recovered and is combat ready.
   Supply cost you 3,232 men, at Swabia and Munich.
   2 satellites drifted — Holland and Kingdom of Italy.
   Soult seeks an audience, Sire — he asks for a command of his own.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat's resentment of Ney has cooled with time.
   Soult's resentment of Davout has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Austria and France have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads -1 for France (9 battles, 3 drawn, 2 decisives kept); the war is 5 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — Austria is bound by Britain's bond not to sign alone; a peace with her runs through the table, where the bond is priced. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 5 French corps stand on Bavarian soil under the truce.
   TRAFALGAR: Nelson's line has shattered the French fleet — 26 sail lost in a decisive action. Britain commands the sea.
   INTERCEPTED AT SEA: Britain's patrols caught Dumonceau's transports off Ulster — 1,950 men lost to the guns and the water.
   Leon passes from Spain to Britain.
   Intelligence reports Britain has raised Wellesley to high command.
   Swabia passes from Bavaria to Austria.
   Ney and Davout stand on Swabia, now Austria's soil — an armistice stands between us: they may march out, but no corps of ours may enter it again.
   War exhaustion grows — Bavaria nears breaking point (exhaustion: 60).
   Munich passes from Bavaria to Austria.
   Lannes, Murat and Bernadotte stand on Munich, now Austria's soil — an armistice stands between us: they may march out, but no corps of ours may enter it again.
   Austrian-led alignment leads the current largest alignment at 36% of active European bloc power.
   Sire — Bavaria has been eliminated from the war.
   Intelligence reports Spain has raised Cuesta to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from the Kingdom of Italy has arrived with a petition.
   Teulie's contingent comes home decimated — 3,449 of 7,500 men. The Kingdom of Italy counts its widows (-5 loyalty).
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Prussia have worsened significantly (-15 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 75/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The water is theirs until the yards replace what we lost, Sire — and new keels sail green."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0116  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0116_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1936 of 1936 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,249 (+808 next turn)
   Inf:
   90,436
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 75/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The water is theirs until the yards replace what we lost, Sire — and new keels sail green."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0117  click Event Log  ->  ok
  (clicked at (53, 18))
view: <run>\frames\0117_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=['event_log'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── CampaignLog (layer 50) [scrolled 0 of 144 px] ──
   CAMPAIGN LOG
   Spain holds Morocco — ticking war score (+1/turn)
   An envoy from the Kingdom of Italy has arrived with a petition
   Teulie's contingent comes home decimated — 3,449 of 7,500 men. The Kingdom of Italy counts its widows (-5 loyalty).
   Britain's gold: 200g reaches Russia
   Russia sponsors Austria against France (200g/turn)
   9 courts rebuff Austria (defensive alliance)
   Ney put on the road home from Swabia to Nivernais under the truce with Austria — 5 turns
   Davout put on the road home from Swabia to Nivernais under the truce with Austria — 5 turns
   Lannes put on the road home from Munich to Nivernais under the truce with Austria — 5 turns
   Murat put on the road home from Munich to Nivernais under the truce with Austria — 5 turns
   Bernadotte put on the road home from Munich to Nivernais under the truce with Austria — 5 turns
   controls: [Pin]  [icon: Close (L) @(2143,296)]  [▾ Turn 7  -  11 events]  [▸ Turn 6  -  30 events]  [▸ Turn 5  -  19 events]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1936 of 1936 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,249 (+808 next turn)
   Inf:
   90,436
   Cav:
   25,500
   Art:
   13,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 75/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The water is theirs until the yards replace what we lost, Sire — and new keels sail green."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0118  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0118_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 4t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1936 of 1936 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 75/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The water is theirs until the yards replace what we lost, Sire — and new keels sail green."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0119  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0119_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 21 sail — readiness 59 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Marescalchi (Loyalist) of Kingdom of Italy /  / The petition: /   - Grant it, and the Kingdom of Italy's tribute of 240g a turn is remitted for 8 collections (1920g forgone): loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and the Kingdom of Italy loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a tu …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 75 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 21 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2068 of 2068 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   5,849 (+832 next turn)
   Inf:
   90,436
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 21 sail — readiness 59 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  21(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1860,438)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Lannes(1888,535)  Murat(1889,509)  Bernadotte(1918,483)  Archduke John(1959,457)  Castanos(1539,399)  Dumonceau(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1482,366)  Moore(1482,328)  Wellesley(1498,302)  ?(2068,435)  ?(1976,376)  ?(1869,762)  2k(1901,591)  25k(1595,497)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1490,427)  9k(1910,645)
```

```
#0120  type lay down a ship of the line at Brittany  ->  ERROR: the command line is not taking orders now (it is disabled)
view: <run>\frames\0120_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2068 of 2068 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 21 sail — readiness 59 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
map: unchanged (59 labels)
```

```
#0121  look  ->  ok
  (a fresh frame)
view: <run>\frames\0121_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2068 of 2068 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 21 sail — readiness 59 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
map: unchanged (59 labels)
```

```
#0122  click Grant  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0122_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 75 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 21 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Bavaria Eliminated! @(3435,64)]  [icon: Ney arrived @(3477,64)]  [icon: Marshal Soult asks for a command @(3519,64)]  [icon: Dumonceau arrived @(3561,64)]  [+17]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 4t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2135 of 2135 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   5,849 (+592 next turn)
   Inf:
   90,436
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (1920g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (59 labels)
```

```
#0123  type lay down a ship of the line at Brittany  ->  ok
  (typed and Enter)
view: <run>\frames\0123_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Brittany — one fleet, whichever yard lays her keel (400g). The fleet stands at 22 sail — readiness 58 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 6/7
   Threat 75 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 22 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Bavaria Eliminated! @(3435,64)]  [icon: Ney arrived @(3477,64)]  [icon: Marshal Soult asks for a command @(3519,64)]  [icon: Dumonceau arrived @(3561,64)]  [+17]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2268 of 2268 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   5,449 (+616 next turn)
   Inf:
   90,436
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Brittany
   A keel is laid at Brittany — one fleet, whichever yard lays her keel (400g). The fleet stands at 22 sail — readiness 58 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  22(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1860,438)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Lannes(1888,535)  Murat(1889,509)  Bernadotte(1918,483)  Archduke John(1959,457)  Castanos(1539,399)  Dumonceau(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1482,366)  Moore(1482,328)  Wellesley(1498,302)  ?(2068,435)  ?(1976,376)  ?(1869,762)  2k(1901,591)  25k(1595,497)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1490,427)  9k(1910,645)
```

```
#0124  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0124_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!

Income: 2290g | Contributions: -150g | Charges of Empire: -441g | Admiralty: -44g | Upkeep: -1068g (incl. 36g over-limit) | Other: +849g | Net: +1436g | Spent: 800g | Treasury: 6,885g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 7
   AUSTRIA / ──────────────────────────── / - Archduke Charles detaches a garrison /  / ──────────────────────────── / Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 72 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 22 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2095 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,885 (+1,287 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Moore — London — substantial force [partial]
   Paget — Gascony — screening force [partial]
   Wellesley — London — small force [partial]
   Brunswick — Berlin — large force [stale - T4]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Murat's army has fully recovered and is combat ready.
   Bernadotte's army has fully recovered and is combat ready.
   Teulie's army has fully recovered and is combat ready.
   Supply cost you 3,232 men, at Swabia and Munich.
   2 satellites drifted — Holland and Kingdom of Italy.
   Soult seeks an audience, Sire — he asks for a command of his own.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat's resentment of Ney has cooled with time.
   Soult's resentment of Davout has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Austria and France have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads -1 for France (9 battles, 3 drawn, 2 decisives kept); the war is 5 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — Austria is bound by Britain's bond not to sign alone; a peace with her runs through the table, where the bond is priced. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 5 French corps stand on Bavarian soil under the truce.
   TRAFALGAR: Nelson's line has shattered the French fleet — 26 sail lost in a decisive action. Britain commands the sea.
   INTERCEPTED AT SEA: Britain's patrols caught Dumonceau's transports off Ulster — 1,950 men lost to the guns and the water.
   Leon passes from Spain to Britain.
   Intelligence reports Britain has raised Wellesley to high command.
   Swabia passes from Bavaria to Austria.
   Ney and Davout stand on Swabia, now Austria's soil — an armistice stands between us: they may march out, but no corps of ours may enter it again.
   War exhaustion grows — Bavaria nears breaking point (exhaustion: 60).
   Munich passes from Bavaria to Austria.
   Lannes, Murat and Bernadotte stand on Munich, now Austria's soil — an armistice stands between us: they may march out, but no corps of ours may enter it again.
   Austrian-led alignment leads the current largest alignment at 36% of active European bloc power.
   Sire — Bavaria has been eliminated from the war.
   Intelligence reports Spain has raised Cuesta to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from the Kingdom of Italy has arrived with a petition.
   Teulie's contingent comes home decimated — 3,449 of 7,500 men. The Kingdom of Italy counts its widows (-5 loyalty).
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Prussia have worsened significantly (-15 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 75/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The water is theirs until the yards replace what we lost, Sire — and new keels sail green."
   ════════════════════════════════════
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 21 sail — readiness 59 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (1920g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► lay down a ship of the line at Brittany
   A keel is laid at Brittany — one fleet, whichever yard lays her keel (400g). The fleet stands at 22 sail — readiness 58 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [4/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 8 BEGINS
   ═══════════════════════════════════════
   Income: 2290g | Contributions: -150g | Charges of Empire: -441g | Admiralty: -44g | Other: +849g | Upkeep: -1068g | Net: +1436g | Spent: 800g
   Treasury: 6,885g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 2,000 -> 4,000
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Garrison at Milan reinforced: 9,000 -> 10,000
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Berthier: Enemy forces spotted near Paris! Paget (4,613 troops) at Berry.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  22(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Ney(1740,436)  Davout(1794,418)  Lannes(1800,497)  Bernadotte(1825,521)  Archduke John(1897,547)  Murat(1739,486)  Castanos(1539,399)  Dumonceau(1563,373)  Soult(1682,367)  Napoleon(1728,310)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  ?(2068,435)  ?(1959,376)  ?(1869,762)  3k(1899,519)  4k(1901,591)  ?(1893,434)  25k(1595,497)  12k(1575,454)  ?(1769,580)  7k(1777,338)  12k(1698,420)  ?(1490,427)  ?(1910,645)
```

```
#0125  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0125_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 72 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 22 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Murat arrived @(3393,64)]  [icon: Bavaria Eliminated! @(3435,64)]  [icon: Ney arrived @(3477,64)]  [icon: Marshal Soult asks for a command @(3519,64)]  [icon: Dumonceau arrived @(3561,64)]  [+16]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 3t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1874 of 1874 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,885 (+1,287 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ═══════════════════════════════════════
   TURN 8 BEGINS
   ═══════════════════════════════════════
   Income: 2290g | Contributions: -150g | Charges of Empire: -441g | Admiralty: -44g | Other: +849g | Upkeep: -1068g | Net: +1436g | Spent: 800g
   Treasury: 6,885g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 2,000 -> 4,000
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Garrison at Milan reinforced: 9,000 -> 10,000
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Berthier: Enemy forces spotted near Paris! Paget (4,613 troops) at Berry.
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte marches to Franche-Comte. 1 region to Nivernais.
   Davout: Davout marches to Lorraine. 1 region to Nivernais.
   Lannes: Lannes marches to Franche-Comte. 1 region to Nivernais.
   Murat: Murat arrives at Nivernais. Murat: "It is done. Point me at something that shoots back, Sire."
   Ney: Ney marches to Lorraine. 1 region to Nivernais.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 8
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Franche-Comte, Lorraine and Rhineland lie in enemy hands. Austria holds them.
   • Sire — Paget has crossed into Berry. No French corps stands in his path.
   • Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   SITUATION
   France holds 25 regions. Treasury: 6,885g (+1,436 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 29% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 30,000 — Awaiting orders.
   > Davout — Lorraine — 19,948 — Moving to Nivernais — arrives next turn.
   - Massena — Piedmont — 19,047 — 5 turns idle. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   > Ney — Lorraine — 16,253 — Moving to Nivernais — arrives next turn.
   > Bernadotte — Franche-Comte — 14,358 — Moving to Nivernais — arrives next turn. Trust:40
   - Murat — Nivernais — 11,437 — Awaiting orders.
   > Lannes — Franche-Comte — 10,484 — Moving to Nivernais — arrives next turn.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 19,625 [confirmed]
   Archduke John — Munich — 8,947 [confirmed]
   Castanos — Normandy — 14,120 [confirmed]
   Moore — London — substantial force [partial]
   Paget — Berry — screening force [partial]
   Wellesley — London — small force [partial]
   Brunswick — Berlin — large force [stale - T4]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Brunswick passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 72/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A province held is a province the enemy taxes, Sire. March on it, or treat for it — the country will not forget which."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0126  type what if Murat attacks Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0126_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat stands at Nivernais, beyond reach of Paget at Berry this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Dumonceau stands within reach.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1984 of 1984 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,885 (+1,287 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Murat attacks Paget
   Murat stands at Nivernais, beyond reach of Paget at Berry this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Dumonceau stands within reach.
map: unchanged (61 labels)
```

```
#0127  type what if Dumonceau attacks Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0127_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Dumonceau (4,550) vs Paget (screening force) at Berry — the balance of force looks even — a hard fight that may go against us.
  Standing modifiers, already in the band: all told, Dumonceau's own modifiers weigh 10% against the attack.
  Berry feeds 60,000 — the whole muster can stand there fed.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 4,550 we muster) would cost ~34g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.

Nothing has been ordered, and nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1720 of 1720 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,885 (+1,287 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Dumonceau attacks Paget
   Were you to give the order, Sire:
   MUSTER — Dumonceau (4,550) vs Paget (screening force) at Berry — the balance of force looks even — a hard fight that may go against us.
   Standing modifiers, already in the band: all told, Dumonceau's own modifiers weigh 10% against the attack.
   Berry feeds 60,000 — the whole muster can stand there fed.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 4,550 we muster) would cost ~34g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (61 labels)
```

```
#0128  type Murat, pursue Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0128_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat pursues Paget (at Berry). Cavalry charges through Burgundy -> Limousin. Murat: "He is already beaten — he merely has not been told. I will tell him."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2383 of 2383 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,885 (+1,287 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, pursue Paget
   Murat pursues Paget (at Berry). Cavalry charges through Burgundy -> Limousin. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  22(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Murat(1600,507)  Ney(1740,436)  Davout(1794,418)  Lannes(1800,497)  Bernadotte(1825,521)  Archduke John(1897,547)  Castanos(1539,399)  Dumonceau(1563,373)  Soult(1682,367)  Napoleon(1728,310)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  ?(2068,435)  ?(1959,376)  ?(1869,762)  3k(1899,519)  4k(1901,591)  ?(1893,434)  25k(1595,478)  12k(1575,448)  ?(1769,580)  7k(1777,338)  12k(1698,420)  ?(1490,427)  ?(1910,645)
```

```
#0129  click Generals  ->  ok
  (clicked at (228, 18))
view: <run>\frames\0129_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 6106 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  / SEEKS AN AUDIENCE — Soult /   / [3] Soult  [Infantry]  France / IV Corps - marching for the Speyer crossing from its Lorraine camps, 10,000 of its best carved away to form the Emperor's Guard. A superb tactician who executes the Emperor's plan to the letter, exactly on the appointed …
   controls: [Pin]  [icon @(2213,236)]  <Hear him — he seeks an audience>  <Fortify>  <Drill>  <Hold (1 AP)>  <▸ the doctrine>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Hold (2 AP)>  <Fall back>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2383 of 2383 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,885 (+1,287 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Nothing has been ordered, and nothing spent.
   ► Murat, pursue Paget
   Murat pursues Paget (at Berry). Cavalry charges through Burgundy -> Limousin. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [2/4 actions remaining]
map: unchanged (61 labels)
```

```
#0130  click Hear him  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0130_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   SOULT — Marshal Soult asks for a command
   "Sire — give me a command of my own." /  / Soult has stood 4 turns at your side, Sire, while other men win their laurels in the field. Under the Emperor's eye every victory is the Emperor's. /  / What each answer does / • Give him a front — Free — counsel, not an order: give him a front of his own (Normandy watches an enemy border). March him there and the laurels he wins are HIS. / • He stays wit …
   controls: [Give him a front]  [He stays with me]  [Promise him the next campaign   [1 AP]]  [Later (he will return)]
── TopBar (layer 75) [under a modal]: unchanged
── MarshalManagement (layer 50) [under a modal] [scrolled 0 of 6106 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2383 of 2383 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,885 (+1,287 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Nothing has been ordered, and nothing spent.
   ► Murat, pursue Paget
   Murat pursues Paget (at Berry). Cavalry charges through Burgundy -> Limousin. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [2/4 actions remaining]
map: unchanged (61 labels)
```

```
#0131  look  ->  ok
  (a fresh frame)
view: <run>\frames\0131_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── MarshalManagement (layer 50) [under a modal] [scrolled 0 of 6106 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2383 of 2383 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Nothing has been ordered, and nothing spent.
   ► Murat, pursue Paget
   Murat pursues Paget (at Berry). Cavalry charges through Burgundy -> Limousin. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [2/4 actions remaining]
map: unchanged (61 labels)
```

```
#0132  click Give him a front  ->  ok
  (clicked at (1622, 702))
view: <run>\frames\0132_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 72 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 22 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Murat arrived @(3393,64)]  [icon: Bavaria Eliminated! @(3435,64)]  [icon: Ney arrived @(3477,64)]  [icon: Dumonceau arrived @(3519,64)]  [icon: Napoleon arrived (x2) @(3561,64)]  [+15]
── MarshalManagement (layer 50) [scrolled 0 of 6060 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  /   OUR DOCTRINE — The Corps System  ▸ the doctrine /  /   THE EMPEROR /   / [8] Napoleon  [Infantry]  France / In the field at Flanders — The Presence goes where he stands. /   ★ The Presence  +10% here at Flanders  Every French corps fighting in the Emperor's province gains +10% att …
   controls: [Pin]  [icon @(2213,236)]  <▸ the doctrine>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (1 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Hold (2 AP)>  <Fall back>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Hold (2 AP)>  <Fall back>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2427 of 2427 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,885 (+1,287 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Soult straightens. "You will not regret it, Sire." March him to Normandy and the front is his — the order is yours to give.
map: unchanged (61 labels)
```

```
#0133  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0133_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 3t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2427 of 2427 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Murat, pursue Paget
   Murat pursues Paget (at Berry). Cavalry charges through Burgundy -> Limousin. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [2/4 actions remaining]
   Soult straightens. "You will not regret it, Sire." March him to Normandy and the front is his — the order is yours to give.
map: unchanged (61 labels)
```

```
#0134  type Soult, pursue Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0134_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult pursues Paget (at Berry). Moves to Orleanais.
Orleanais lies outside the camp — this takes 30,000 men out of it; the 5-turn count resets at the turn's end. "Soult, pursue Paget." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2007 of 2007 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,885 (+1,287 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Franche-Comte, Lorraine and Rhineland lie in enemy hands. Austria holds them.
   • Sire — Paget has crossed into Berry. No French corps stands in his path.
   • Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   SITUATION
   France holds 25 regions. Treasury: 6,885g (+1,436 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 29% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 30,000 — Awaiting orders.
   > Davout — Lorraine — 19,948 — Moving to Nivernais — arrives next turn.
   - Massena — Piedmont — 19,047 — 5 turns idle. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   > Ney — Lorraine — 16,253 — Moving to Nivernais — arrives next turn.
   > Bernadotte — Franche-Comte — 14,358 — Moving to Nivernais — arrives next turn. Trust:40
   - Murat — Nivernais — 11,437 — Awaiting orders.
   > Lannes — Franche-Comte — 10,484 — Moving to Nivernais — arrives next turn.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 19,625 [confirmed]
   Archduke John — Munich — 8,947 [confirmed]
   Castanos — Normandy — 14,120 [confirmed]
   Moore — London — substantial force [partial]
   Paget — Berry — screening force [partial]
   Wellesley — London — small force [partial]
   Brunswick — Berlin — large force [stale - T4]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Brunswick passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 72/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A province held is a province the enemy taxes, Sire. March on it, or treat for it — the country will not forget which."
   ════════════════════════════════════
   ► what if Murat attacks Paget
   Murat stands at Nivernais, beyond reach of Paget at Berry this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Dumonceau stands within reach.
   ► what if Dumonceau attacks Paget
   Were you to give the order, Sire:
   MUSTER — Dumonceau (4,550) vs Paget (screening force) at Berry — the balance of force looks even — a hard fight that may go against us.
   Standing modifiers, already in the band: all told, Dumonceau's own modifiers weigh 10% against the attack.
   Berry feeds 60,000 — the whole muster can stand there fed.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 4,550 we muster) would cost ~34g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► Murat, pursue Paget
   Murat pursues Paget (at Berry). Cavalry charges through Burgundy -> Limousin. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [2/4 actions remaining]
   Soult straightens. "You will not regret it, Sire." March him to Normandy and the front is his — the order is yours to give.
   ► Soult, pursue Paget
   Soult pursues Paget (at Berry). Moves to Orleanais.
   Orleanais lies outside the camp — this takes 30,000 men out of it; the 5-turn count resets at the turn's end. "Soult, pursue Paget." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  22(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Murat(1600,507)  Ney(1740,436)  Davout(1794,418)  Lannes(1800,497)  Bernadotte(1825,521)  Archduke John(1897,547)  Soult(1695,440)  Castanos(1539,399)  Dumonceau(1563,373)  Napoleon(1715,310)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  ?(2068,435)  ?(1959,376)  ?(1869,762)  3k(1899,519)  4k(1901,591)  ?(1893,434)  25k(1595,478)  12k(1575,448)  ?(1769,580)  7k(1777,338)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0135  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0135_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 23 sail — readiness 62 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 72 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 23 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Murat arrived @(3393,64)]  [icon: Bavaria Eliminated! @(3435,64)]  [icon: Ney arrived @(3477,64)]  [icon: Dumonceau arrived @(3519,64)]  [icon: Napoleon arrived (x2) @(3561,64)]  [+15]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2140 of 2140 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   1/4
   Admin:
   1/2
   Gold:
   6,485 (+1,312 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 23 sail — readiness 62 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  23(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Murat(1600,507)  Ney(1740,436)  Davout(1794,418)  Lannes(1800,497)  Bernadotte(1825,521)  Archduke John(1897,547)  Soult(1695,440)  Castanos(1539,399)  Dumonceau(1563,373)  Napoleon(1715,310)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  ?(2068,435)  ?(1959,376)  ?(1869,762)  3k(1899,519)  4k(1901,591)  ?(1893,434)  25k(1595,478)  12k(1575,448)  ?(1769,580)  7k(1777,338)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0136  type lay down a ship of the line at Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0136_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 24 sail — readiness 61 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 72 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 24 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Murat arrived @(3393,64)]  [icon: Bavaria Eliminated! @(3435,64)]  [icon: Ney arrived @(3477,64)]  [icon: Dumonceau arrived @(3519,64)]  [icon: Napoleon arrived (x2) @(3561,64)]  [+15]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2273 of 2273 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   1/4
   Admin:
   0/2
   Gold:
   6,085 (+1,338 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 24 sail — readiness 61 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 97(1396,395)  24(1374,592)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Murat(1600,507)  Ney(1740,436)  Davout(1794,418)  Lannes(1800,497)  Bernadotte(1825,521)  Archduke John(1897,547)  Soult(1695,440)  Castanos(1539,399)  Dumonceau(1563,373)  Napoleon(1715,310)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  ?(2068,435)  ?(1959,376)  ?(1869,762)  3k(1899,519)  4k(1901,591)  ?(1893,434)  25k(1595,478)  12k(1575,448)  ?(1769,580)  7k(1777,338)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0137  type lay down a ship of the line at Brittany  ->  ok
  (typed and Enter)
view: <run>\frames\0137_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: No administrative actions remaining this turn. (Military commands: 1 remaining)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2362 of 2362 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   1/4
   Admin:
   0/2
   Gold:
   6,085 (+1,338 next turn)
   Inf:
   91,598
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Brittany
   No administrative actions remaining this turn. (Military commands: 1 remaining)
map: unchanged (61 labels)
```

```
#0138  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0138_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!

Income: 2290g | Contributions: -110g | Charges of Empire: -535g | Admiralty: -48g | Upkeep: -1020g (incl. 20g over-limit) | Other: +849g | Net: +1426g | Spent: 800g | Treasury: 7,511g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 8
   AUSTRIA / ──────────────────────────── / - Archduke Charles holds position / - Archduke John holds position /  / ──────────────────────────── / Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 69 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 24 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2297 of 2299 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,511 (+1,271 next turn)
   Inf:
   92,660
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Archduke Charles — Swabia — 19,625 [confirmed]
   Archduke John — Munich — 8,947 [confirmed]
   Castanos — Normandy — 14,120 [confirmed]
   Moore — London — substantial force [partial]
   Paget — Berry — screening force [partial]
   Wellesley — London — small force [partial]
   Brunswick — Berlin — large force [stale - T4]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Brunswick passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 72/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A province held is a province the enemy taxes, Sire. March on it, or treat for it — the country will not forget which."
   ════════════════════════════════════
   ► what if Murat attacks Paget
   Murat stands at Nivernais, beyond reach of Paget at Berry this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Dumonceau stands within reach.
   ► what if Dumonceau attacks Paget
   Were you to give the order, Sire:
   MUSTER — Dumonceau (4,550) vs Paget (screening force) at Berry — the balance of force looks even — a hard fight that may go against us.
   Standing modifiers, already in the band: all told, Dumonceau's own modifiers weigh 10% against the attack.
   Berry feeds 60,000 — the whole muster can stand there fed.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 4,550 we muster) would cost ~34g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► Murat, pursue Paget
   Murat pursues Paget (at Berry). Cavalry charges through Burgundy -> Limousin. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [2/4 actions remaining]
   Soult straightens. "You will not regret it, Sire." March him to Normandy and the front is his — the order is yours to give.
   ► Soult, pursue Paget
   Soult pursues Paget (at Berry). Moves to Orleanais.
   Orleanais lies outside the camp — this takes 30,000 men out of it; the 5-turn count resets at the turn's end. "Soult, pursue Paget." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [1/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 23 sail — readiness 62 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [1/4 actions remaining]
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 24 sail — readiness 61 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [1/4 actions remaining]
   ► lay down a ship of the line at Brittany
   No administrative actions remaining this turn. (Military commands: 1 remaining)
   ► end turn
   ═══════════════════════════════════════
   TURN 9 BEGINS
   ═══════════════════════════════════════
   Income: 2290g | Contributions: -110g | Charges of Empire: -535g | Admiralty: -48g | Other: +849g | Upkeep: -1020g | Net: +1426g | Spent: 800g
   Treasury: 7,511g
   Actions refreshed: 4/4
   Supply shortage at Nivernais: Ney loses 905 troops
   Supply shortage at Nivernais: Davout loses 1,111 troops
   Supply shortage at Nivernais: Lannes loses 583 troops
   Supply shortage at Nivernais: Bernadotte loses 799 troops
   Garrison at Munich reinforced: 4,000 -> 6,000
   Garrison at Hanover reinforced: 0 -> 2,000
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Sweden grows.
   Berthier reports that Murat resents Ney's laurels again, 5 turns after the last — he has grown restless for glory. He asked for an audience on turn 3, and will not ask again before turn 9.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat is eyeing Paget's position at Gascony. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 97(1396,395)  24(1354,613)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Castanos(1525,465)  Massena(1764,616)  Archduke Charles(1859,464)  ?(1501,602)  Paget(1501,564)  Murat(1600,507)  Archduke John(1897,535)  ?(1384,625)  Cuesta(1384,587)  Soult(1695,440)  ?(1701,299)  Brunswick(1700,266)  Ney +3(1748,476)  Dumonceau(1551,399)  Napoleon(1715,326)  ?(1490,371)  Moore(1490,344)  ?(1869,762)  3k(1822,506)  6k(1901,591)  25k(1595,478)  12k(1589,448)  ?(1769,580)  2k(1783,335)  ?(1755,420)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0139  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0139_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 69 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 24 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x2) @(3351,64)]  [icon: Bernadotte arrived @(3393,64)]  [icon: Davout arrived @(3435,64)]  [icon: Lannes arrived @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Murat arrived @(3561,64)]  [+18]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:8
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 2t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2158 of 2158 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,511 (+1,271 next turn)
   Inf:
   92,660
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Income: 2290g | Contributions: -110g | Charges of Empire: -535g | Admiralty: -48g | Other: +849g | Upkeep: -1020g | Net: +1426g | Spent: 800g
   Treasury: 7,511g
   Actions refreshed: 4/4
   Supply shortage at Nivernais: Ney loses 905 troops
   Supply shortage at Nivernais: Davout loses 1,111 troops
   Supply shortage at Nivernais: Lannes loses 583 troops
   Supply shortage at Nivernais: Bernadotte loses 799 troops
   Garrison at Munich reinforced: 4,000 -> 6,000
   Garrison at Hanover reinforced: 0 -> 2,000
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Sweden grows.
   Berthier reports that Murat resents Ney's laurels again, 5 turns after the last — he has grown restless for glory. He asked for an audience on turn 3, and will not ask again before turn 9.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat is eyeing Paget's position at Gascony. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte arrives at Nivernais. Bernadotte: "Accomplished as ordered. The army is intact."
   Davout: Davout arrives at Nivernais.
   Nivernais feeds 22,500; the 34,306 men standing there would lose ~612 a turn to short supply. Davout: "Accomplished as ordered. The army is intact."
   Lannes: Lannes arrives at Nivernais.
   Nivernais feeds 22,500; the 44,790 men standing there would lose ~1,560 a turn to short supply. Lannes: "Done — and I trust the next order has more fire in it."
   Murat: Murat is pursuing Paget.
   Ney: Ney arrives at Nivernais.
   Nivernais feeds 22,500; the 61,043 men standing there would lose ~3,398 a turn to short supply. Ney: "Done — and I trust the next order has more fire in it."
   Soult: Soult is pursuing Paget.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 9
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
   • Sire — 3 turns now with Franche-Comte, Lorraine and Rhineland in enemy hands. The country counts every one of them.
   • Sire — Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   SITUATION
   France holds 25 regions. Treasury: 7,511g (+1,426 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 23% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   > Soult — Orleanais — 30,000 — Pursuing Paget. (to the letter)
   - Massena — Piedmont — 19,047 — 6 turns idle. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Davout — Nivernais — 18,837 — Awaiting orders.
   - Ney — Nivernais — 15,348 — Awaiting orders.
   - Bernadotte — Nivernais — 13,559 — Awaiting orders. Trust:40
   > Murat — Limousin — 11,437 — Pursuing Paget.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Nivernais — 9,901 — Awaiting orders.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 19,625 [confirmed]
   Archduke John — Munich — 8,947 [confirmed]
   Moore — London — substantial force [partial]
   Brunswick — Oldenburg — large force [partial]
   Castanos — Berry — small force [partial]
   Paget — Gascony — screening force [partial]
   Cuesta — Bordelais — small force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 3,398 men, at Nivernais.
   Berthier reports that Murat resents Ney's laurels again, 5 turns after the last — he has grown restless for glory. He asked for an audience on turn 3, and will not ask again before turn 9.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat is eyeing Paget's position at Gascony. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   DIPLOMATIC EVENTS
   THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 69/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0140  type Ney, march to Burgundy  ->  ok
  (typed and Enter)
view: <run>\frames\0140_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins march to Burgundy. Moves to Burgundy. Ney: "At the double, Sire — the men will smell powder soon enough."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2268 of 2268 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   7,511 (+1,271 next turn)
   Inf:
   92,660
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, march to Burgundy
   Ney begins march to Burgundy. Moves to Burgundy. Ney: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 97(1396,395)  24(1354,613)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Castanos(1525,465)  Massena(1764,616)  Archduke Charles(1859,464)  ?(1501,602)  Paget(1501,564)  Murat(1600,507)  Archduke John(1897,535)  ?(1384,625)  Cuesta(1384,587)  Soult(1695,440)  ?(1701,299)  Brunswick(1700,266)  Davout(1736,486)  Lannes(1753,438)  Bernadotte(1821,490)  Ney(1684,495)  Dumonceau(1551,399)  Napoleon(1715,326)  ?(1490,371)  Moore(1490,344)  ?(1869,762)  3k(1895,506)  6k(1901,591)  25k(1595,478)  12k(1589,448)  ?(1769,580)  2k(1783,335)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0141  type Davout, march to Champagne  ->  ok
  (typed and Enter)
view: <run>\frames\0141_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout begins march to Champagne. Route: Burgundy → Champagne. Moves to Burgundy.
Burgundy feeds 22,500; the 34,185 men standing there would lose ~608 a turn to short supply. Davout: "The roads will be scouted before each march, Sire."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2401 of 2401 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   7,511 (+1,271 next turn)
   Inf:
   92,660
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, march to Champagne
   Davout begins march to Champagne. Route: Burgundy → Champagne. Moves to Burgundy.
   Burgundy feeds 22,500; the 34,185 men standing there would lose ~608 a turn to short supply. Davout: "The roads will be scouted before each march, Sire."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 97(1396,395)  24(1354,613)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Castanos(1525,465)  Massena(1764,616)  Archduke Charles(1859,464)  ?(1501,602)  Paget(1501,564)  Murat(1600,507)  Archduke John(1897,535)  ?(1384,625)  Cuesta(1384,587)  Soult(1695,440)  ?(1701,299)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1771,438)  Ney(1672,495)  Davout(1697,521)  Dumonceau(1551,399)  Napoleon(1715,326)  ?(1490,371)  Moore(1490,344)  ?(1869,762)  3k(1822,506)  6k(1901,591)  25k(1595,478)  12k(1589,448)  ?(1769,580)  2k(1783,335)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0142  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0142_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 25 sail — readiness 65 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 69 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x2) @(3351,64)]  [icon: Bernadotte arrived @(3393,64)]  [icon: Davout arrived @(3435,64)]  [icon: Lannes arrived @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Murat arrived @(3561,64)]  [+18]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1830 of 1830 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   7,111 (+1,298 next turn)
   Inf:
   92,660
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   MORNING DISPATCH — Turn 9
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
   • Sire — 3 turns now with Franche-Comte, Lorraine and Rhineland in enemy hands. The country counts every one of them.
   • Sire — Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   SITUATION
   France holds 25 regions. Treasury: 7,511g (+1,426 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 23% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   > Soult — Orleanais — 30,000 — Pursuing Paget. (to the letter)
   - Massena — Piedmont — 19,047 — 6 turns idle. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Davout — Nivernais — 18,837 — Awaiting orders.
   - Ney — Nivernais — 15,348 — Awaiting orders.
   - Bernadotte — Nivernais — 13,559 — Awaiting orders. Trust:40
   > Murat — Limousin — 11,437 — Pursuing Paget.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Nivernais — 9,901 — Awaiting orders.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 19,625 [confirmed]
   Archduke John — Munich — 8,947 [confirmed]
   Moore — London — substantial force [partial]
   Brunswick — Oldenburg — large force [partial]
   Castanos — Berry — small force [partial]
   Paget — Gascony — screening force [partial]
   Cuesta — Bordelais — small force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 3,398 men, at Nivernais.
   Berthier reports that Murat resents Ney's laurels again, 5 turns after the last — he has grown restless for glory. He asked for an audience on turn 3, and will not ask again before turn 9.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat is eyeing Paget's position at Gascony. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   DIPLOMATIC EVENTS
   THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 69/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► Ney, march to Burgundy
   Ney begins march to Burgundy. Moves to Burgundy. Ney: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   ► Davout, march to Champagne
   Davout begins march to Champagne. Route: Burgundy → Champagne. Moves to Burgundy.
   Burgundy feeds 22,500; the 34,185 men standing there would lose ~608 a turn to short supply. Davout: "The roads will be scouted before each march, Sire."
   [0/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 25 sail — readiness 65 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 97(1396,395)  25(1354,613)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Castanos(1525,465)  Massena(1764,616)  Archduke Charles(1859,464)  ?(1501,602)  Paget(1501,564)  Murat(1600,507)  Archduke John(1897,535)  ?(1384,625)  Cuesta(1384,587)  Soult(1695,440)  ?(1701,299)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1771,438)  Ney(1672,495)  Davout(1697,521)  Dumonceau(1551,399)  Napoleon(1715,326)  ?(1490,371)  Moore(1490,344)  ?(1869,762)  3k(1822,506)  6k(1901,591)  25k(1595,478)  12k(1589,448)  ?(1769,580)  2k(1783,335)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0143  type lay down a ship of the line at Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0143_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 26 sail — readiness 64 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you say so.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 69 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 26 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x2) @(3351,64)]  [icon: Bernadotte arrived @(3393,64)]  [icon: Davout arrived @(3435,64)]  [icon: Lannes arrived @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Murat arrived @(3561,64)]  [+18]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1963 of 1963 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   0/2
   Gold:
   6,711 (+1,324 next turn)
   Inf:
   92,660
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 26 sail — readiness 64 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you say so.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 97(1396,395)  26(1354,613)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Castanos(1525,465)  Massena(1764,616)  Archduke Charles(1859,464)  ?(1501,602)  Paget(1501,564)  Murat(1600,507)  Archduke John(1897,535)  ?(1384,625)  Cuesta(1384,587)  Soult(1695,440)  ?(1701,299)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1771,438)  Ney(1672,495)  Davout(1697,521)  Dumonceau(1551,399)  Napoleon(1715,326)  ?(1490,371)  Moore(1490,344)  ?(1869,762)  3k(1822,506)  6k(1901,591)  25k(1595,478)  12k(1589,448)  ?(1769,580)  2k(1783,335)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0144  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0144_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 9 ended. Turn 10 begins!

Income: 2272g | Contributions: -101g | Charges of Empire: -631g | Admiralty: -52g | Blockade: -320g | Materiel: -57g | Upkeep: -964g (incl. 4g over-limit) | Other: +849g | Net: +996g | Spent: 800g | Treasury: 7,707g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 91 px] ──
   ENEMY PHASE - Turn 9
   BRITAIN / ──────────────────────────── / - Paget moves to Guyenne /  / SPAIN / ──────────────────────────── / - Castanos attacks Paget /     Battle of Guyenne /     Castanos: 433 casualties, 13,546 remaining /     Paget: 1,439 casualties, 1,630 remaining /     Result: Attacker tactical victory (Castanos victorious) — and advances into Guyenne /     ⚔ View the field /     --- Berthier's Report ---  …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 26 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2339 of 2339 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,707 (+942 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Archduke John — Munich — 8,947 [confirmed]
   Moore — London — substantial force [partial]
   Brunswick — Oldenburg — large force [partial]
   Castanos — Berry — small force [partial]
   Paget — Gascony — screening force [partial]
   Cuesta — Bordelais — small force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 3,398 men, at Nivernais.
   Berthier reports that Murat resents Ney's laurels again, 5 turns after the last — he has grown restless for glory. He asked for an audience on turn 3, and will not ask again before turn 9.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat is eyeing Paget's position at Gascony. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   DIPLOMATIC EVENTS
   THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 69/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► Ney, march to Burgundy
   Ney begins march to Burgundy. Moves to Burgundy. Ney: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   ► Davout, march to Champagne
   Davout begins march to Champagne. Route: Burgundy → Champagne. Moves to Burgundy.
   Burgundy feeds 22,500; the 34,185 men standing there would lose ~608 a turn to short supply. Davout: "The roads will be scouted before each march, Sire."
   [0/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 25 sail — readiness 65 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [0/4 actions remaining]
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 26 sail — readiness 64 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you say so.
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2272g | Contributions: -101g | Charges of Empire: -631g | Admiralty: -52g | Blockade: -320g | Materiel: -57g | Other: +849g | Upkeep: -964g | Net: +996g | Spent: 800g
   Treasury: 7,707g
   Actions refreshed: 4/4
   Supply shortage at Nivernais: Lannes loses 105 troops
   Supply shortage at Nivernais: Bernadotte loses 144 troops
   Supply shortage at Burgundy: Ney loses 733 troops
   Supply shortage at Burgundy: Davout loses 900 troops
   Supply shortage at Burgundy: Soult loses 1,433 troops
   Garrison at Hanover reinforced: 2,000 -> 4,000
   Britain subsidizes Austria with 300 gold.
   Peace concluded between Hanover and Prussia without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   Murat went at Paget on his own initiative — his standing order to pursue Paget is void. He awaits fresh orders.
   Murat, hungry for glory, has attacked Paget on his own initiative.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   ⚔ Murat went in without orders:
   ⚔ Battle of Gascony ⚔
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
   [Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
   [Terrain] Paget benefits from Mountains terrain (+25% defense)
   Murat's forces advance steadily. Brutal stalemate between Murat and Paget. Heavy casualties on both sides: Murat 1,156, Paget 1,421.
   [Materiel] Guns, horses and stores lost with the fallen: France -57g, Britain -71g. Our treasury stands at 6,654 gold.
   ⚔ View the field
   --- Berthier's Report ---
   Murat: "Neither side yielded. Unfinished business sits badly with me."
   Murat fought with particular ferocity — though one wonders if it was for France or for himself.
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 1,156 | Paget 1,421
   Strength: Murat 11,437 → 10,281 | Paget 4,521 → 3,100
   Berthier: "An inconclusive affair. Both sides bloodied but unbroken."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  26(1374,600)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1859,469)  Archduke Charles(1859,430)  Castanos(1422,574)  Paget(1446,548)  Murat(1600,507)  ?(1901,540)  Archduke John(1901,501)  Lannes(1736,486)  Bernadotte(1760,460)  Ney(1672,495)  Davout(1675,460)  Soult(1697,434)  Dumonceau(1551,399)  Napoleon(1715,322)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1595,478)  12k(1551,454)  ?(1769,580)  4k(1783,319)  ?(1755,420)  12k(1680,405)  ?(1490,427)  ?(1910,645)
```

```
#0145  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0145_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   BRITAIN LOSSES
   0
   0
   ⚔
   Murat ◆
   Paget ◆
   11,437 → 10,281
   4,521 → 3,100
   BATTLE OF GASCONY
   click anywhere to skip ▸
   GASCONY · TURN 9
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 26 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3351,64)]  [icon: Ney arrived (x3) @(3393,64)]  [icon: Envoy from Britain @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Davout arrived @(3519,64)]  [icon: Lannes arrived @(3561,64)]  [+20]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:9
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 1t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,707 (+942 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Soult: Soult pursues Paget. 3 regions away.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
   • Sire — Leon has been taken by Britain.
   • Sire — Lannes and Bernadotte stand 23,211 men at Nivernais, which feeds 22,500. 711 too many. 3,647 men lost in 2 turns. No depot may be laid at Nivernais — rural regions don't support buildings (need city or larger). Orleanais can feed 52,500 more and Bern can feed 37,500 more — a corps marched there ends it.
   • Sire — the enemy has held Franche-Comte, Lorraine and Rhineland 4 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
   SITUATION
   France holds 25 regions. Treasury: 7,707g (+1,053 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 2% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   > Soult — Burgundy — 28,567 — Pursuing Paget — 3 turns behind him. (to the letter)
   - Massena — Piedmont — 19,047 — 7 turns idle. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   > Davout — Burgundy — 17,937 — Moving to Champagne — arrives next turn.
   - Ney — Burgundy — 14,615 — Awaiting orders.
   - Bernadotte — Nivernais — 13,415 — Awaiting orders. Trust:40
   ⚠ Starving — supply has failed at Nivernais two turns running.
   - Murat — Limousin — 10,281 — Awaiting orders.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Nivernais — 9,796 — Awaiting orders.
   ⚠ Starving — supply has failed at Nivernais two turns running.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 13,411 [confirmed]
   Paget — Guyenne — 1,630 [confirmed]
   Archduke Charles — Swabia — substantial force [stale - T9]
   Archduke John — Munich — small force [stale - T9]
   Brunswick — Berlin — large force [last known - T4]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 3,315 men, at Nivernais and Burgundy.
   Murat went at Paget on his own initiative — his standing order to pursue Paget is void. He awaits fresh orders.
   Murat, hungry for glory, has attacked Paget on his own initiative.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Leon passes from Spain to Britain.
   Westphalia passes from Hanover to Prussia.
   East Frisia passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Intelligence reports Spain has raised Blake to high command.
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   The court of Prussia takes up a new design: Armed Neutrality.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0146  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0146_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,707 (+942 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0147  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0147_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1807 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 10 — Early February 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants. /   • Sire — Leon ha …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,707 (+942 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0148  scroll 1800 600 down 3  ->  ok
  (scrolled down 3 at (1800, 600))
view: <run>\frames\0148_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 132 of 1807 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 10 — Early February 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants. /   • Sire — Leon ha …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0149  click Open Envoys  ->  ok
  (clicked at (2084, 731))
view: <run>\frames\0149_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 200 px] ──
   DIPLOMATIC ENVOY / Castlereagh (Hawk) of Britain /  / Proposes: Armistice / Terms: / Mutual: /   - Armistice (cease hostilities temporarily) — France and Britain /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads -2 for France (1 battle, a stalemate, 0 decisives kept); the war is 9 turns old and stays so; exhaustion holds.  …
   controls: [Accept]  [Let Talleyrand haggle (1 DP)]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Franche-Comte
   -2 →
   T:9
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War for Franche-Comte — Austria, truce 1t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,707 (+942 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0150  look  ->  ok
  (a fresh frame)
view: <run>\frames\0150_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 200 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0151  click Accept  ->  ok
  (clicked at (1574, 878))
view: <run>\frames\0151_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 66 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 26 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3351,64)]  [icon: Ney arrived (x3) @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Davout arrived @(3477,64)]  [icon: Lannes arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+21]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Russia
   0 →
   T:9
   controls: [THIRD COALITION  ▸]  [War with Russia]  [War with Britain — Britain, truce 5t]  [War for Franche-Comte — Austria, truce 1t]
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,707 (+1,535 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (55 labels)
```

```
#0152  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0152_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 750 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early February 1806 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 95 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location: …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,707 (+1,535 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (55 labels)
```

```
#0153  click FORCES  ->  ok
  (the control is disabled; the click did nothing (its reason: You are reading this book))
view: <run>\frames\0153_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 750 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (55 labels)
```

```
#0154  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0154_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Russia
   0 →
   T:9
   controls: [THIRD COALITION  ▸]  [War with Russia]  [War with Britain — Britain, truce 5t]  [War for Franche-Comte — Austria, truce 1t]
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (55 labels)
```

```
#0155  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0155_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 27 sail — readiness 58 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 66 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3351,64)]  [icon: Ney arrived (x3) @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Davout arrived @(3477,64)]  [icon: Lannes arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+21]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   7,307 (+1,551 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 27 sail — readiness 58 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  27(1374,600)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1859,469)  Archduke Charles(1859,430)  Castanos(1422,574)  Paget(1446,548)  Murat(1600,507)  ?(1901,540)  Archduke John(1901,501)  Lannes(1736,486)  Bernadotte(1760,460)  Ney(1672,495)  Davout(1675,460)  Soult(1697,434)  Dumonceau(1551,399)  Napoleon(1715,322)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1595,478)  12k(1551,454)  ?(1769,580)  4k(1783,319)  ?(1755,420)  12k(1680,405)  ?(1490,427)  ?(1910,645)
```

```
#0156  type lay down a ship of the line at Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0156_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 28 sail — readiness 57 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 66 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3351,64)]  [icon: Ney arrived (x3) @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Davout arrived @(3477,64)]  [icon: Lannes arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+21]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2138 of 2138 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   6,907 (+1,568 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 28 sail — readiness 57 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  28(1374,600)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1859,469)  Archduke Charles(1859,430)  Castanos(1422,574)  Paget(1446,548)  Murat(1600,507)  ?(1901,540)  Archduke John(1901,501)  Lannes(1736,486)  Bernadotte(1760,460)  Ney(1672,495)  Davout(1675,460)  Soult(1697,434)  Dumonceau(1551,399)  Napoleon(1715,322)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1595,478)  12k(1551,454)  ?(1769,580)  4k(1783,319)  ?(1755,420)  12k(1680,405)  ?(1490,427)  ?(1910,645)
```

```
#0157  type Soult, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0157_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. "Soult, march to Flanders." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2271 of 2271 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   3/4
   Admin:
   0/2
   Gold:
   6,907 (+1,568 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, march to Flanders
   Soult begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. "Soult, march to Flanders." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  28(1374,600)  15(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1859,469)  Archduke Charles(1859,430)  Castanos(1422,574)  Paget(1446,548)  Murat(1600,507)  ?(1901,540)  Archduke John(1901,501)  Soult(1695,440)  Lannes(1736,486)  Bernadotte(1771,460)  Ney(1672,495)  Davout(1697,521)  Dumonceau(1551,399)  Napoleon(1715,322)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1595,478)  12k(1551,454)  ?(1769,580)  4k(1783,319)  ?(1755,420)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0158  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0158_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!

Income: 2254g | Charges of Empire: -539g | Admiralty: -56g | Upkeep: -960g | Other: +849g | Net: +1548g | Spent: 800g | Treasury: 8,455g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 421 px] ──
   ENEMY PHASE - Turn 10
   BRITAIN / ──────────────────────────── / - Wellesley moves to Bearn / - Wellesley moves to Gascony /  / SPAIN / ──────────────────────────── / - Castanos attacks Paget /     Second Battle of Guyenne /     Castanos: 150 casualties, 13,261 remaining /     Paget: 810 casualties, 820 remaining /     Result: Attacker tactical victory (Castanos victorious) /     Paget forced to retreat! /     ⚔ View the …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 63 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,455 (+1,399 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Murat — Limousin — 10,281 — Awaiting orders.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Nivernais — 9,796 — Awaiting orders.
   ⚠ Starving — supply has failed at Nivernais two turns running.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 13,411 [confirmed]
   Paget — Guyenne — 1,630 [confirmed]
   Archduke Charles — Swabia — substantial force [stale - T9]
   Archduke John — Munich — small force [stale - T9]
   Brunswick — Berlin — large force [last known - T4]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 3,315 men, at Nivernais and Burgundy.
   Murat went at Paget on his own initiative — his standing order to pursue Paget is void. He awaits fresh orders.
   Murat, hungry for glory, has attacked Paget on his own initiative.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Leon passes from Spain to Britain.
   Westphalia passes from Hanover to Prussia.
   East Frisia passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Intelligence reports Spain has raised Blake to high command.
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   The court of Prussia takes up a new design: Armed Neutrality.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 27 sail — readiness 58 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 28 sail — readiness 57 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [4/4 actions remaining]
   ► Soult, march to Flanders
   Soult begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. "Soult, march to Flanders." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2254g | Charges of Empire: -539g | Admiralty: -56g | Other: +849g | Upkeep: -960g | Net: +1548g | Spent: 800g
   Treasury: 8,455g
   Actions refreshed: 4/4
   Supply shortage at Nivernais: Lannes loses 102 troops
   Supply shortage at Nivernais: Bernadotte loses 140 troops
   Supply shortage at Burgundy: Ney loses 244 troops
   Supply shortage at Burgundy: Davout loses 299 troops
   Holland loyalty 89 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   The armistice between Austria and France has collapsed. War resumes.
   Britain subsidizes Russia with 300 gold.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  28(1374,592)  16(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1859,469)  Archduke Charles(1859,430)  Wellesley(1501,598)  Castanos(1434,572)  Murat(1600,507)  ?(1901,540)  Archduke John(1901,501)  Soult(1695,440)  ?(1701,295)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1771,460)  Ney(1672,495)  Davout(1697,521)  Dumonceau(1551,399)  Napoleon(1715,322)  ?(1490,371)  Moore(1490,344)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1595,478)  12k(1551,454)  ?(1769,580)  ?(1783,319)  ?(1755,420)  12k(1684,411)  ?(1490,427)  ?(1910,645)
```

```
#0159  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0159_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   DAVOUT REPORTS
   "Davout: 'Cannon fire at Gascony, Sire. Spain and Britain are at war; France is not in it. Investigate?'"
   controls: [March to the Guns]  [Continue as Ordered]  [Hold Position]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 63 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Holland @(3351,64)]  [icon: Armistice Collapsed @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Blockade — Britain closes our ports @(3477,64)]  [icon: Settlement offer from Britain @(3519,64)]  [icon: Ney arrived (x3) @(3561,64)]  [+25]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Franche-Comte
   +5 ↑
   T:10
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War with Britain — Britain, truce 4t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1893 of 1893 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,455 (+1,399 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Lannes and Bernadotte stand 22,969 men at Nivernais, which feeds 22,500. 469 too many. 3,889 men lost in 3 turns. No depot may be laid at Nivernais — rural regions don't support buildings (need city or larger). Bern can feed 37,500 more and Orleanais can feed 23,933 more — a corps marched there ends it.
   • Sire — the truce with Austria has collapsed — the war resumes where it stood, at its age, with its ledger.
   • Sire — a truce with Britain holds the guns silent — the war is paused, not over. The truce grants safe passage home.
   • Sire — the enemy has held Franche-Comte, Lorraine and Rhineland 5 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
   SITUATION
   France holds 25 regions. Treasury: 8,455g (+1,548 by the accounts)
   The courts at war hold 23 regions. Estimated enemy strength: 29% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   > Soult — Orleanais — 28,567 — Moving to Flanders — arrives next turn. (to the letter)
   - Massena — Piedmont — 19,047 — 8 turns idle. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   ? Davout — Burgundy — 17,638 — HALTED at Burgundy — awaiting your word.
   ⚠ Starving — supply has failed at Burgundy two turns running.
   - Ney — Burgundy — 14,371 — Awaiting orders.
   ⚠ Starving — supply has failed at Burgundy two turns running.
   - Bernadotte — Nivernais — 13,275 — Awaiting orders. Trust:40
   ⚠ Starving — supply has failed at Nivernais three turns running.
   - Murat — Limousin — 10,281 — Awaiting orders.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Nivernais — 9,694 — Awaiting orders.
   ⚠ Starving — supply has failed at Nivernais three turns running.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 12,393 [confirmed]
   Wellesley — Gascony — 4,187 [confirmed]
   Moore — London — large force [partial]
   Brunswick — Oldenburg — substantial force [partial]
   Archduke Charles — Swabia — substantial force [stale - T9]
   Archduke John — Munich — small force [stale - T9]
   Swabia garrison — Swabia — garrison — screening force [stale - T7]
   Munich garrison — Munich — garrison — small force [stale - T7]
   TURN EVENTS
   Supply cost you 785 men, at Nivernais and Burgundy.
   Holland loyalty 89 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Britain and France have signed the Armistice.
   A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -2 for France (1 battle, a stalemate, 0 decisives kept); the war is 9 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -90 and will thaw to -75, short of -60; the ledger and the war's age come back with it. Spain stays at war with Britain — an ally, not a client: her war runs on, and no corps of ours stands on Spanish soil.
   Britain, for Britain and Russia, has offered terms to settle the War for Franche-Comte — Britain + Austria + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Holland has arrived with a petition.
   The armistice between Austria and France has collapsed. War resumes!
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 63/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (59 labels)
```

```
#0160  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0160_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1893 of 1893 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (59 labels)
```

```
#0161  click Continue as Ordered  ->  ok
  (clicked at (1829, 562))
view: <run>\frames\0161_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   SPAIN LOSSES
   BRITAIN LOSSES
   0
   0
   ⚔
   Castanos ◆
   Paget ◆
   13,411 → 13,261
   1,630 → 820
   Wellesley — could not reach the field
   SECOND BATTLE OF GUYENNE
   click anywhere to skip ▸
   GUYENNE · TURN 10
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1959 of 1959 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,455 (+1,399 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Gascony. Davout arrives at Champagne. Davout: "Done, and done properly — no stragglers, no surprises."
map: unchanged (59 labels)
```

```
#0162  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0162_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1959 of 1959 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,455 (+1,399 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Gascony. Davout arrives at Champagne. Davout: "Done, and done properly — no stragglers, no surprises."
map: unchanged (59 labels)
```

```
#0163  type commission Oudinot  ->  ok
  (typed and Enter)
view: <run>\frames\0163_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
reply: ok Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
── ProposalConfirmPopup (layer 110) ──
   SETTLEMENT OFFER FROM BRITAIN /  / the War for Franche-Comte — Britain + Austria + Russia /  / "His Majesty's Government offers terms for the War for Franche-Comte — Britain + Austria + Russia. No indemnity is asked and none is offered; London proposes only that the guns fall silent." /  / Their proposed terms: /   • Peace /  / Covered enemies: Britain, Russia /  / "Sire, Britain has dispatched a  …
   controls: [Review Settlement Offer]  [Request Revision]  [Reject Offer]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 63 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2070 of 2070 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   4,955 (+1,714 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► commission Oudinot
   Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  28(1374,592)  16(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1859,469)  Archduke Charles(1859,430)  Wellesley(1501,598)  Castanos(1434,572)  Murat(1600,507)  ?(1901,540)  Archduke John(1901,501)  Soult(1695,440)  ?(1701,295)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1771,460)  Ney(1684,495)  Davout(1649,414)  Oudinot(1595,442)  Dumonceau(1551,399)  Napoleon(1715,322)  ?(1490,371)  Moore(1490,344)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1634,479)  12k(1551,470)  ?(1769,580)  ?(1783,319)  ?(1755,420)  12k(1680,385)  ?(1490,427)  ?(1910,645)
```

```
#0164  click Review Settlement Offer  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0164_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 376 px] ──
   Settlement of the War for Franche-Comte — the table with Britain + Russia — ready for ratification / the War for Franche-Comte — the table with Britain + Russia - Separate settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Britain, Russia / Still at war: Austria / Will carry — these are the terms they offered. / Sire, this settlement of  …
   The table /   * Britain - Their own terms White peace /       Blocker: Settlement legitimacy /       Castlereagh for Britain: these are the terms Britain laid before France; Britain does not haggle with its own dispatch. /   * Russia - Their own terms White peace /       Blocker: Settlement legitimacy /       Czartoryski for Russia: these are the terms Russia laid before France; Russia does not ha …
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry; the verdict beside each row is that court's own, and the terms before you stand as offered. / Sire, the white peace for the War for Franche-Comte — the table with Britain + Russia is ready: no further land changes hands — each side keeps what it holds, now by treaty. Ratify and the f …
   controls: [Ratify White Peace]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 63 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2092 of 2092 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   4,955 (+1,714 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: accept settlement offer
map: unchanged (60 labels)
```

```
#0165  click Back Out  ->  ok
  (clicked at (1834, 969))
view: <run>\frames\0165_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Schimmelpenninck (Loyalist) of Holland /  / The petition: /   - Grant it, and Holland's tribute of 337g a turn is remitted for 8 collections (2696g forgone): loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Holland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now +0); nothin …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2158 of 2158 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   4,955 (+1,714 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: back out settlement
   Settlement review cancelled.
map: unchanged (60 labels)
```

```
#0166  click Grant  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0166_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 63 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Davout arrived (x2) @(3351,64)]  [icon: Armistice Collapsed @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Blockade — Britain closes our ports @(3477,64)]  [icon: Ney arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   +5 ↑
   T:10
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War with Britain — Britain, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2225 of 2225 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   4,955 (+1,377 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0167  type lay down a ship of the line at Brittany  ->  ok
  (typed and Enter)
view: <run>\frames\0167_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Brittany — one fleet, whichever yard lays her keel (400g). The fleet stands at 29 sail — readiness 61 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 6/7
   Threat 63 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 29 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Davout arrived (x2) @(3351,64)]  [icon: Armistice Collapsed @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Blockade — Britain closes our ports @(3477,64)]  [icon: Ney arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1740 of 1740 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   4,555 (+1,396 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Lannes — Nivernais — 9,694 — Awaiting orders.
   ⚠ Starving — supply has failed at Nivernais three turns running.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 12,393 [confirmed]
   Wellesley — Gascony — 4,187 [confirmed]
   Moore — London — large force [partial]
   Brunswick — Oldenburg — substantial force [partial]
   Archduke Charles — Swabia — substantial force [stale - T9]
   Archduke John — Munich — small force [stale - T9]
   Swabia garrison — Swabia — garrison — screening force [stale - T7]
   Munich garrison — Munich — garrison — small force [stale - T7]
   TURN EVENTS
   Supply cost you 785 men, at Nivernais and Burgundy.
   Holland loyalty 89 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Britain and France have signed the Armistice.
   A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -2 for France (1 battle, a stalemate, 0 decisives kept); the war is 9 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -90 and will thaw to -75, short of -60; the ledger and the war's age come back with it. Spain stays at war with Britain — an ally, not a client: her war runs on, and no corps of ours stands on Spanish soil.
   Britain, for Britain and Russia, has offered terms to settle the War for Franche-Comte — Britain + Austria + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Holland has arrived with a petition.
   The armistice between Austria and France has collapsed. War resumes!
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 63/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Gascony. Davout arrives at Champagne. Davout: "Done, and done properly — no stragglers, no surprises."
   ► commission Oudinot
   Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
   [4/4 actions remaining]
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: back out settlement
   Settlement review cancelled.
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► lay down a ship of the line at Brittany
   A keel is laid at Brittany — one fleet, whichever yard lays her keel (400g). The fleet stands at 29 sail — readiness 61 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  29(1374,592)  16(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1859,469)  Archduke Charles(1859,430)  Wellesley(1501,598)  Castanos(1434,572)  Murat(1600,507)  ?(1901,540)  Archduke John(1901,501)  Soult(1695,440)  ?(1701,295)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1771,460)  Ney(1684,495)  Davout(1649,414)  Oudinot(1595,442)  Dumonceau(1551,399)  Napoleon(1715,322)  ?(1490,371)  Moore(1490,344)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1634,479)  12k(1551,470)  ?(1769,580)  ?(1783,319)  ?(1755,420)  12k(1680,385)  ?(1490,427)  ?(1910,645)
```

```
#0168  type what if Ney attacks Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0168_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney stands at Burgundy, beyond reach of Franche-Comte this turn, Sire — the order would be refused, and nothing spent. Of ours, Bernadotte and Lannes stand within reach.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1851 of 1851 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   4,555 (+1,396 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Ney attacks Franche-Comte
   Ney stands at Burgundy, beyond reach of Franche-Comte this turn, Sire — the order would be refused, and nothing spent. Of ours, Bernadotte and Lannes stand within reach.
map: unchanged (60 labels)
```

```
#0169  type what if Lannes attacks Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0169_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Franche-Comte stands open, Sire — Lannes would take it by marching in.

Nothing has been ordered, and nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1983 of 1983 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   4,555 (+1,396 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Lannes attacks Franche-Comte
   Franche-Comte stands open, Sire — Lannes would take it by marching in.
   Nothing has been ordered, and nothing spent.
map: unchanged (60 labels)
```

```
#0170  type Lannes, attack Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0170_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes marches from Nivernais into Franche-Comte unopposed! (96 lost to march) Captured: Austria → France
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Lorraine
   +12 ↑
   T:10
   controls: [THIRD COALITION  ▸]  [War for Lorraine]  [War with Britain — Britain, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   3/4
   Admin:
   0/2
   Gold:
   4,555 (+1,333 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, attack Franche-Comte
   ⚑ Lannes marches from Nivernais into Franche-Comte unopposed! (96 lost to march) Captured: Austria → France
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2009,544)  France(1572,534)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  29(1374,592)  16(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  ?(1859,469)  Archduke Charles(1859,430)  Wellesley(1501,598)  Castanos(1434,572)  Murat(1600,506)  Lannes(1813,497)  ?(1901,540)  Archduke John(1913,501)  Soult(1695,440)  ?(1701,295)  Brunswick(1700,266)  Bernadotte(1747,471)  Ney(1684,495)  Davout(1649,414)  Oudinot(1595,442)  Dumonceau(1551,399)  Napoleon(1715,322)  ?(1490,371)  Moore(1490,344)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1634,479)  12k(1551,470)  ?(1769,580)  ?(1783,319)  ?(1755,420)  12k(1679,385)  ?(1490,427)  ?(1910,645)
```

```
#0171  type Davout, attack Lorraine  ->  ok
  (typed and Enter)
view: <run>\frames\0171_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Davout cannot reach Lorraine from Champagne! Range: 1, Distance: 3
No enemies within range. Try 'move to Lorraine' to get closer first
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2205 of 2205 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   3/4
   Admin:
   0/2
   Gold:
   4,555 (+1,333 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, attack Lorraine
   Davout cannot reach Lorraine from Champagne! Range: 1, Distance: 3
   No enemies within range. Try 'move to Lorraine' to get closer first
map: unchanged (60 labels)
```

```
#0172  type Bernadotte, attack Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0172_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Bernadotte cannot reach Rhineland from Nivernais! Range: 1, Distance: 2
No enemies within range. Try 'move to Rhineland' to get closer first
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2317 of 2317 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   3/4
   Admin:
   0/2
   Gold:
   4,555 (+1,333 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Bernadotte, attack Rhineland
   Bernadotte cannot reach Rhineland from Nivernais! Range: 1, Distance: 2
   No enemies within range. Try 'move to Rhineland' to get closer first
map: unchanged (60 labels)
```

```
#0173  type Davout, march to Lorraine  ->  ok
  (typed and Enter)
view: <run>\frames\0173_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout begins march to Lorraine. Route: Burgundy → Orleanais → Lorraine. Moves to Burgundy.
Burgundy feeds 22,500; the 32,009 men standing there would lose ~522 a turn to short supply. Davout: "As ordered. I keep my flanks as I go."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1834 of 1835 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   1/4
   Admin:
   0/2
   Gold:
   4,555 (+1,333 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   The armistice between Austria and France has collapsed. War resumes!
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +4, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 63/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Gascony. Davout arrives at Champagne. Davout: "Done, and done properly — no stragglers, no surprises."
   ► commission Oudinot
   Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
   [4/4 actions remaining]
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: back out settlement
   Settlement review cancelled.
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► lay down a ship of the line at Brittany
   A keel is laid at Brittany — one fleet, whichever yard lays her keel (400g). The fleet stands at 29 sail — readiness 61 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
   ► what if Ney attacks Franche-Comte
   Ney stands at Burgundy, beyond reach of Franche-Comte this turn, Sire — the order would be refused, and nothing spent. Of ours, Bernadotte and Lannes stand within reach.
   ► what if Lannes attacks Franche-Comte
   Franche-Comte stands open, Sire — Lannes would take it by marching in.
   Nothing has been ordered, and nothing spent.
   ► Lannes, attack Franche-Comte
   ⚑ Lannes marches from Nivernais into Franche-Comte unopposed! (96 lost to march) Captured: Austria → France
   [3/4 actions remaining]
   ► Davout, attack Lorraine
   Davout cannot reach Lorraine from Champagne! Range: 1, Distance: 3
   No enemies within range. Try 'move to Lorraine' to get closer first
   ► Bernadotte, attack Rhineland
   Bernadotte cannot reach Rhineland from Nivernais! Range: 1, Distance: 2
   No enemies within range. Try 'move to Rhineland' to get closer first
   ► Davout, march to Lorraine
   Davout begins march to Lorraine. Route: Burgundy → Orleanais → Lorraine. Moves to Burgundy.
   Burgundy feeds 22,500; the 32,009 men standing there would lose ~522 a turn to short supply. Davout: "As ordered. I keep my flanks as I go."
   [1/4 actions remaining]
map: unchanged (60 labels)
```

```
#0174  type Bernadotte, march to Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0174_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Not enough actions! Need 2, have 1 — Bernadotte cannot march to Franche-Comte today.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1924 of 1924 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   1/4
   Admin:
   0/2
   Gold:
   4,555 (+1,333 next turn)
   Inf:
   89,660
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Bernadotte, march to Franche-Comte
   Not enough actions! Need 2, have 1 — Bernadotte cannot march to Franche-Comte today.
map: unchanged (60 labels)
```

```
#0175  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0175_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!

Income: 2258g | Charges of Empire: -279g | Admiralty: -58g | Materiel: -180g | Upkeep: -972g (incl. 4g over-limit) | Other: +512g | Net: +1281g | Spent: 3900g | Treasury: 5,836g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 246 px] ──
   ENEMY PHASE - Turn 11
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Lannes /     Second Battle of Franche-Comte /     Archduke Charles: 862 casualties, 24,763 remaining /     Lannes: 3,606 casualties, 5,992 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) — and advances into Franche-Comte /     Franche-Comte CAPTURED! (was France) (secured) /     Lannes forced to ret …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 60 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 29 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1904 of 1906 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,836 (+1,323 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   COALITION THREAT
   Threat: 63/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Gascony. Davout arrives at Champagne. Davout: "Done, and done properly — no stragglers, no surprises."
   ► commission Oudinot
   Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
   [4/4 actions remaining]
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: back out settlement
   Settlement review cancelled.
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► lay down a ship of the line at Brittany
   A keel is laid at Brittany — one fleet, whichever yard lays her keel (400g). The fleet stands at 29 sail — readiness 61 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
   ► what if Ney attacks Franche-Comte
   Ney stands at Burgundy, beyond reach of Franche-Comte this turn, Sire — the order would be refused, and nothing spent. Of ours, Bernadotte and Lannes stand within reach.
   ► what if Lannes attacks Franche-Comte
   Franche-Comte stands open, Sire — Lannes would take it by marching in.
   Nothing has been ordered, and nothing spent.
   ► Lannes, attack Franche-Comte
   ⚑ Lannes marches from Nivernais into Franche-Comte unopposed! (96 lost to march) Captured: Austria → France
   [3/4 actions remaining]
   ► Davout, attack Lorraine
   Davout cannot reach Lorraine from Champagne! Range: 1, Distance: 3
   No enemies within range. Try 'move to Lorraine' to get closer first
   ► Bernadotte, attack Rhineland
   Bernadotte cannot reach Rhineland from Nivernais! Range: 1, Distance: 2
   No enemies within range. Try 'move to Rhineland' to get closer first
   ► Davout, march to Lorraine
   Davout begins march to Lorraine. Route: Burgundy → Orleanais → Lorraine. Moves to Burgundy.
   Burgundy feeds 22,500; the 32,009 men standing there would lose ~522 a turn to short supply. Davout: "As ordered. I keep my flanks as I go."
   [1/4 actions remaining]
   ► Bernadotte, march to Franche-Comte
   Not enough actions! Need 2, have 1 — Bernadotte cannot march to Franche-Comte today.
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2258g | Charges of Empire: -279g | Admiralty: -58g | Materiel: -180g | Other: +512g | Upkeep: -972g | Net: +1281g | Spent: 3900g
   Treasury: 5,836g
   Actions refreshed: 4/4
   Lannes's army is recovering. Effectiveness penalty: -30%.
   Supply shortage at Munich: Archduke Charles loses 495 troops
   Supply shortage at Munich: Archduke John loses 240 troops
   Supply shortage at Burgundy: Ney loses 234 troops
   Supply shortage at Burgundy: Davout loses 288 troops
   Garrison at Munich reinforced: 10,000 -> 12,000
   Garrison at Milan reinforced: 5,000 -> 7,000
   Holland loyalty 96 (-3): satellite drift, the lord's defeats
   Switzerland loyalty 86 (-3): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Sweden grows.
   Marshal Oudinot accepts his commission — he raises a corps of 5,000 at Paris.
   Berthier reports that Bernadotte resents Davout's laurels again, 8 turns after the last — he has grown quiet in the way the staff have learned to read.
   The rivalry between Bernadotte and Davout has become entrenched. The wound will not close on its own.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  29(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  Cuesta(1501,598)  Castanos(1434,572)  Murat(1600,507)  ?(1894,540)  Archduke Charles(1893,501)  ?(1921,540)  Archduke John(1909,475)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1760,460)  Ney(1672,495)  Davout(1697,434)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1704,322)  Napoleon(1728,296)  ?(1475,371)  Moore(1475,344)  ?(1502,371)  Wellesley(1490,287)  ?(1530,366)  Shrapnel(1505,261)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1557,478)  12k(1535,448)  ?(1769,580)  ?(1808,335)  ?(1755,420)  12k(1686,405)  ?(1490,427)  7k(1910,645)
```

```
#0176  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0176_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Lannes ◆
   Archduke Charles ◆
   9,598 → 5,992
   25,625 → 24,763 → 24,280 after the advance
   Bernadotte — weighed his own ambitions
   SECOND BATTLE OF FRANCHE-COMTE
   click anywhere to skip ▸
   FRANCHE-COMTE · TURN 11
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 60 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 29 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Soult arrived (x2) @(3351,64)]  [icon: Davout arrived (x2) @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: Envoy from Naples @(3519,64)]  [icon: Ney arrived (x3) @(3561,64)]  [+25]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Franche-Comte
   -1 →
   T:11
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War with Britain — Britain, truce 3t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2049 of 2049 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,836 (+1,323 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Switzerland loyalty 86 (-3): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Sweden grows.
   Marshal Oudinot accepts his commission — he raises a corps of 5,000 at Paris.
   Berthier reports that Bernadotte resents Davout's laurels again, 8 turns after the last — he has grown quiet in the way the staff have learned to read.
   The rivalry between Bernadotte and Davout has become entrenched. The wound will not close on its own.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Davout: Davout is marching to Lorraine (2 turns remaining).
   Soult: As ordered: "Soult, march to Flanders". Soult arrives at Flanders. Soult stands ready for instruction.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Lannes's corps has been broken at Franche-Comte. He must reform before he fights again.
   • Sire — Lannes was mauled at Franche-Comte: a third of his corps — 3,606 men — lost in a single action.
   • Sire — Ney and Davout stand 31,487 men at Burgundy, which feeds 22,500. 8,987 too many. 4,131 men lost in 3 turns. No depot may be laid at Burgundy — rural regions don't support buildings (need city or larger). Orleanais can feed 52,500 more and Lyonnais can feed 52,500 more — a corps marched there ends it.
   SITUATION
   France holds 25 regions. Treasury: 5,836g (+1,461 by the accounts)
   The courts at war hold 23 regions. Estimated enemy strength: 43% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 28,567 — Awaiting orders.
   - Massena — Piedmont — 19,047 — 9 turns idle. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   > Davout — Burgundy — 17,350 — Moving to Lorraine — 2 turns out.
   ⚠ Starving — supply has failed at Burgundy three turns running.
   - Ney — Burgundy — 14,137 — Awaiting orders.
   ⚠ Starving — supply has failed at Burgundy three turns running.
   - Bernadotte — Nivernais — 13,275 — Awaiting orders. Trust:40
   ⚠ Starving — supply has failed at Nivernais three turns running.
   - Murat — Limousin — 10,281 — Awaiting orders.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   < Lannes — Nivernais — 5,992 — Recovers T14. Morale:6%
   ⚠ Morale failing (6) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Paris — 5,000 — Awaiting orders.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 12,393 [confirmed]
   Cuesta — Gascony — 7,409 [confirmed]
   Archduke Charles — Munich — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Moore — London — large force [partial]
   Brunswick — Oldenburg — substantial force [partial]
   Wellesley — London — small force [partial]
   Shrapnel — London — screening force [partial]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — small force [partial]
   TURN EVENTS
   Lannes's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 522 men, at Burgundy.
   Munich's garrison regrows — small force.
   2 satellites drifted — Holland and Switzerland.
   Marshal Oudinot accepts his commission — he raises a corps of 5,000 at Paris.
   Berthier reports that Bernadotte resents Davout's laurels again, 8 turns after the last — he has grown quiet in the way the staff have learned to read.
   The rivalry between Bernadotte and Davout has become entrenched. The wound will not close on its own.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Intelligence reports Britain has raised Shrapnel to high command.
   An envoy from Naples has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Naples — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +7, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 60/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (63 labels)
```

```
#0177  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0177_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['marshal_petition', 'war_status_panel (not modal)'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   BERNADOTTE — Marshal Bernadotte demands to be heard
   Give him a command is closed — There is no enemy within his reach to send him against.
   "My corps is in good order, Sire. It has been in good order for some time now." /  / Sire, Bernadotte submitted a summary of his corps' service this season. It is accurate, and it is longer than it needed to be. The breach between them has become entrenched; he presses the point with unusual heat. /  / What each answer does / • Let it stand (Free) — Free, and it fixes nothing. For 2 more turns he  …
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Give him a command   [2 AP]](disabled: There is no enemy within his reach to send him against.)  [Later (he will return)]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2049 of 2049 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 60/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (63 labels)
```

```
#0178  type what if Ney attacks Archduke Charles  ->  ERROR: the command line is not taking orders now (it is disabled)
view: <run>\frames\0178_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['marshal_petition', 'war_status_panel (not modal)'], region_panel=no
── MarshalPetitionDialog (layer 114): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2049 of 2049 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 60/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (63 labels)
```

```
#0179  look  ->  ok
  (a fresh frame)
view: <run>\frames\0179_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['marshal_petition', 'war_status_panel (not modal)'], region_panel=no
── MarshalPetitionDialog (layer 114): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2049 of 2049 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 60/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (63 labels)
```

```
#0180  click Let it stand  ->  ok
  (clicked at (1595, 702))
view: <run>\frames\0180_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   A COURT WRITES (1)
   Naples writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Naples
   Proposal
   Turn 11
   Incoming proposal: Open Borders Agreement
   Medici, smoothly evasive: "Naples has always counted better than she has fought, and the count favors friendship with France. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Naples pays you 150 gold at the signing
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2092 of 2092 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,836 (+1,323 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Bernadotte's grievance runs its course.
map: unchanged (63 labels)
```

```
#0181  type what if Ney attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0181_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
reply: ok Ney stands at Burgundy, beyond reach of Archduke Charles at Munich this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 60 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 29 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2202 of 2202 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,836 (+1,323 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► what if Ney attacks Archduke Charles
   Ney stands at Burgundy, beyond reach of Archduke Charles at Munich this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
map: unchanged (63 labels)
```

```
#0182  look  ->  ok
  (a fresh frame)
view: <run>\frames\0182_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2202 of 2202 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   ► what if Ney attacks Archduke Charles
   Ney stands at Burgundy, beyond reach of Archduke Charles at Munich this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
map: unchanged (63 labels)
```

```
#0183  click Accept  ->  ok
  (clicked at (1433, 478))
view: <run>\frames\0183_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 60 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 29 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [scrolled 2225 of 2225 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,986 (+1,329 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted Naples's proposal. Treaty signed: Peace → Open Borders with Naples. Naples paid 150 gold into the treasury.
map: unchanged (63 labels)
```

```
#0184  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0184_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 60 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 29 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Soult arrived (x2) @(3351,64)]  [icon: Davout arrived (x2) @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: Ney arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+25]
── DispatchView (layer 50) [scrolled 0 of 1785 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 12 — Early March 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province a …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2225 of 2225 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,986 (+1,329 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Bernadotte's grievance runs its course.
   ► what if Ney attacks Archduke Charles
   Ney stands at Burgundy, beyond reach of Archduke Charles at Munich this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   You have accepted Naples's proposal. Treaty signed: Peace → Open Borders with Naples. Naples paid 150 gold into the treasury.
map: unchanged (63 labels)
```

```
#0185  scroll 1800 600 down 5  ->  ok
  (scrolled down 5 at (1800, 600))
view: <run>\frames\0185_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 220 of 1785 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 12 — Early March 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province a …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2225 of 2225 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Bernadotte's grievance runs its course.
   ► what if Ney attacks Archduke Charles
   Ney stands at Burgundy, beyond reach of Archduke Charles at Munich this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   You have accepted Naples's proposal. Treaty signed: Peace → Open Borders with Naples. Naples paid 150 gold into the treasury.
map: unchanged (63 labels)
```

```
#0186  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0186_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franche-Comte
   -1 →
   T:11
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War with Britain — Britain, truce 3t]
── BottomLeftUI (layer 0) [scrolled 2225 of 2225 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Bernadotte's grievance runs its course.
   ► what if Ney attacks Archduke Charles
   Ney stands at Burgundy, beyond reach of Archduke Charles at Munich this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   You have accepted Naples's proposal. Treaty signed: Peace → Open Borders with Naples. Naples paid 150 gold into the treasury.
map: unchanged (63 labels)
```

```
#0187  type Davout, march to Lorraine  ->  ok
  (typed and Enter)
view: <run>\frames\0187_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout is already carrying out that order. No change.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1674 of 1674 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,986 (+1,329 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 28,567 — Awaiting orders.
   - Massena — Piedmont — 19,047 — 9 turns idle. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   > Davout — Burgundy — 17,350 — Moving to Lorraine — 2 turns out.
   ⚠ Starving — supply has failed at Burgundy three turns running.
   - Ney — Burgundy — 14,137 — Awaiting orders.
   ⚠ Starving — supply has failed at Burgundy three turns running.
   - Bernadotte — Nivernais — 13,275 — Awaiting orders. Trust:40
   ⚠ Starving — supply has failed at Nivernais three turns running.
   - Murat — Limousin — 10,281 — Awaiting orders.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   < Lannes — Nivernais — 5,992 — Recovers T14. Morale:6%
   ⚠ Morale failing (6) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Paris — 5,000 — Awaiting orders.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 12,393 [confirmed]
   Cuesta — Gascony — 7,409 [confirmed]
   Archduke Charles — Munich — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Moore — London — large force [partial]
   Brunswick — Oldenburg — substantial force [partial]
   Wellesley — London — small force [partial]
   Shrapnel — London — screening force [partial]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — small force [partial]
   TURN EVENTS
   Lannes's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 522 men, at Burgundy.
   Munich's garrison regrows — small force.
   2 satellites drifted — Holland and Switzerland.
   Marshal Oudinot accepts his commission — he raises a corps of 5,000 at Paris.
   Berthier reports that Bernadotte resents Davout's laurels again, 8 turns after the last — he has grown quiet in the way the staff have learned to read.
   The rivalry between Bernadotte and Davout has become entrenched. The wound will not close on its own.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Intelligence reports Britain has raised Shrapnel to high command.
   An envoy from Naples has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Naples — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +7, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 60/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   ► what if Ney attacks Archduke Charles
   Ney stands at Burgundy, beyond reach of Archduke Charles at Munich this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   You have accepted Naples's proposal. Treaty signed: Peace → Open Borders with Naples. Naples paid 150 gold into the treasury.
   ► Davout, march to Lorraine
   Davout is already carrying out that order. No change.
map: unchanged (63 labels)
```

```
#0188  type Ney, march to Lorraine  ->  ok
  (typed and Enter)
view: <run>\frames\0188_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins march to Lorraine. Route: Orleanais → Lorraine. Moves to Orleanais. Ney: "At the double, Sire — the men will smell powder soon enough."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1784 of 1784 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   5,986 (+1,329 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, march to Lorraine
   Ney begins march to Lorraine. Route: Orleanais → Lorraine. Moves to Orleanais. Ney: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  29(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  Cuesta(1501,598)  Castanos(1434,572)  Murat(1600,507)  ?(1894,540)  Archduke Charles(1893,501)  ?(1921,540)  Archduke John(1909,475)  Ney(1694,440)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1766,460)  Davout(1685,512)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1704,322)  Napoleon(1728,296)  ?(1475,371)  Moore(1475,344)  ?(1502,371)  Wellesley(1490,287)  ?(1530,366)  Shrapnel(1505,261)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1634,478)  12k(1551,470)  ?(1769,580)  ?(1808,335)  ?(1755,420)  12k(1684,411)  ?(1490,427)  7k(1910,645)
```

```
#0189  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0189_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 30 sail — readiness 65 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 60 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 30 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Soult arrived (x2) @(3351,64)]  [icon: Davout arrived (x2) @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: Ney arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1917 of 1917 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   5,586 (+1,351 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 30 sail — readiness 65 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  30(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  Cuesta(1501,598)  Castanos(1434,572)  Murat(1600,507)  ?(1894,540)  Archduke Charles(1893,501)  ?(1921,540)  Archduke John(1909,475)  Ney(1694,440)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1766,460)  Davout(1685,512)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1704,322)  Napoleon(1728,296)  ?(1475,371)  Moore(1475,344)  ?(1502,371)  Wellesley(1490,287)  ?(1530,366)  Shrapnel(1505,261)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1634,478)  12k(1551,470)  ?(1769,580)  ?(1808,335)  ?(1755,420)  12k(1684,411)  ?(1490,427)  7k(1910,645)
```

```
#0190  type lay down a ship of the line at Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0190_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 31 sail — readiness 64 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 60 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 31 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Soult arrived (x2) @(3351,64)]  [icon: Davout arrived (x2) @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: Ney arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2051 of 2051 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   2/4
   Admin:
   0/2
   Gold:
   5,186 (+1,373 next turn)
   Inf:
   90,660
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 31 sail — readiness 64 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2002,543)  France(1563,535)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  31(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1764,616)  Cuesta(1501,598)  Castanos(1434,572)  Murat(1600,507)  ?(1894,540)  Archduke Charles(1893,501)  ?(1921,540)  Archduke John(1909,475)  Ney(1694,440)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1766,460)  Davout(1685,512)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1704,322)  Napoleon(1728,296)  ?(1475,371)  Moore(1475,344)  ?(1502,371)  Wellesley(1490,287)  ?(1530,366)  Shrapnel(1505,261)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1634,478)  12k(1551,470)  ?(1769,580)  ?(1808,335)  ?(1755,420)  12k(1684,411)  ?(1490,427)  7k(1910,645)
```

```
#0191  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0191_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!

Income: 2262g | Charges of Empire: -367g | Admiralty: -62g | Materiel: -293g | Upkeep: -920g | Other: +537g | Net: +1157g | Spent: 800g | Treasury: 6,343g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 312 px] ──
   ENEMY PHASE - Turn 12
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Milan /     The garrison of Milan is destroyed. /     Region captured: Milan (was Kingdom of Italy) (secured) / - Archduke Charles attacks Massena /     Battle of Piedmont /     Archduke Charles: 917 casualties, 29,163 remaining /     Massena: 5,862 casualties, 13,185 remaining /     Result: Attacker tactical victory (Archduke Cha …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 47 / 100
   Turn 13 — Late March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 31 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1922 of 1923 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,343 (+1,296 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Brunswick — Oldenburg — substantial force [partial]
   Wellesley — London — small force [partial]
   Shrapnel — London — screening force [partial]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — small force [partial]
   TURN EVENTS
   Lannes's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 522 men, at Burgundy.
   Munich's garrison regrows — small force.
   2 satellites drifted — Holland and Switzerland.
   Marshal Oudinot accepts his commission — he raises a corps of 5,000 at Paris.
   Berthier reports that Bernadotte resents Davout's laurels again, 8 turns after the last — he has grown quiet in the way the staff have learned to read.
   The rivalry between Bernadotte and Davout has become entrenched. The wound will not close on its own.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Intelligence reports Britain has raised Shrapnel to high command.
   An envoy from Naples has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Naples — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 32 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +7, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 60/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   ► what if Ney attacks Archduke Charles
   Ney stands at Burgundy, beyond reach of Archduke Charles at Munich this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   You have accepted Naples's proposal. Treaty signed: Peace → Open Borders with Naples. Naples paid 150 gold into the treasury.
   ► Davout, march to Lorraine
   Davout is already carrying out that order. No change.
   ► Ney, march to Lorraine
   Ney begins march to Lorraine. Route: Orleanais → Lorraine. Moves to Orleanais. Ney: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 30 sail — readiness 65 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [2/4 actions remaining]
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 31 sail — readiness 64 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 13 BEGINS
   ═══════════════════════════════════════
   Income: 2262g | Charges of Empire: -367g | Admiralty: -62g | Materiel: -293g | Other: +537g | Upkeep: -920g | Net: +1157g | Spent: 800g
   Treasury: 6,343g
   Actions refreshed: 4/4
   Lannes's army is recovering. Effectiveness penalty: -15%.
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Garrison at Munich reinforced: 12,000 -> 14,000
   Garrison at Milan reinforced: 0 -> 2,000
   Holland loyalty 93 (-3): satellite drift, the lord's defeats
   Switzerland loyalty 83 (-3): satellite drift, the lord's defeats
   Britain subsidizes Russia with 300 gold.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1979,553)  France(1563,535)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  31(1374,592)  18(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1764,616)  ?(1434,578)  Castanos(1434,540)  Murat(1600,507)  Massena(1644,541)  ?(1901,540)  Archduke John(1901,501)  Ney(1682,440)  Davout(1736,419)  Brunswick(1700,266)  Lannes(1736,486)  Bernadotte(1760,460)  Oudinot(1595,442)  Dumonceau(1539,399)  Cuesta(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1482,371)  Moore(1482,344)  ?(1510,371)  Shrapnel(1498,287)  ?(1869,762)  ?(1859,529)  ?(1901,591)  25k(1634,478)  12k(1551,470)  ?(1769,580)  ?(1792,420)  12k(1680,411)  ?(1490,427)  2k(1910,645)
```

```
#0192  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0192_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   19,047 → 13,185
   30,080 → 29,163 → 27,511 after the advance
   BATTLE OF PIEDMONT
   click anywhere to skip ▸
   PIEDMONT · TURN 12
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 47 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 31 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Sardinia's allegiance is in play @(3351,64)]  [icon: Kingdom of Italy Eliminated! @(3393,64)]  [icon: Soult arrived (x2) @(3435,64)]  [icon: Davout arrived (x2) @(3477,64)]  [icon: Ney arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Franche-Comte
   0 →
   T:12
   controls: [THIRD COALITION  ▸]  [War for Franche-Comte]  [War with Britain — Britain, truce 2t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2071 of 2071 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,343 (+1,296 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Actions refreshed: 4/4
   Lannes's army is recovering. Effectiveness penalty: -15%.
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Garrison at Munich reinforced: 12,000 -> 14,000
   Garrison at Milan reinforced: 0 -> 2,000
   Holland loyalty 93 (-3): satellite drift, the lord's defeats
   Switzerland loyalty 83 (-3): satellite drift, the lord's defeats
   Britain subsidizes Russia with 300 gold.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   --- Strategic Order Updates ---
   Davout: Davout marches to Orleanais. 1 region to Lorraine.
   Ney: Ney is marching to Lorraine (1 turn remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 13
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Massena's corps has been broken at Piedmont. He must reform before he fights again.
   • Sire — the Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
   • Sire — Massena was mauled at Piedmont: a quarter of his corps — 5,862 men — lost in a single action.
   • Sire — Franche-Comte, Lorraine and Rhineland lie in enemy hands. Austria holds them.
   SITUATION
   France holds 25 regions. Treasury: 6,343g (+1,450 by the accounts)
   The courts at war hold 25 regions. Estimated enemy strength: 45% of French forces (an estimate — 1 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 28,567 — Awaiting orders.
   > Davout — Orleanais — 17,350 — Moving to Lorraine — arrives next turn.
   > Ney — Orleanais — 14,137 — Moving to Lorraine — arrives next turn.
   - Bernadotte — Nivernais — 13,275 — Awaiting orders. Trust:40
   < Massena — Lyonnais — 13,185 — Recovers T15. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Murat — Limousin — 10,281 — 3 turns idle.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   < Lannes — Nivernais — 5,992 — Recovers T14. Morale:6%
   ⚠ Morale failing (6) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Paris — 5,000 — Awaiting orders.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Piedmont — 27,511 [confirmed]
   Cuesta — Normandy — 7,262 [confirmed]
   Archduke John — Munich — substantial force [partial]
   Moore — London — large force [partial]
   Brunswick — Oldenburg — large force [partial]
   Castanos — Guyenne — small force [partial]
   Shrapnel — London — screening force [partial]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — small force [partial]
   Milan garrison — Milan — garrison of 2,000 [confirmed]
   TURN EVENTS
   Lannes's army is recovering. Effectiveness penalty: -15%.
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Munich's garrison regrows — small force.
   Milan's garrison regains 2,000: 0 -> 2,000.
   2 satellites drifted — Holland and Switzerland.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   Sire — Naples and France have signed the Open Borders Agreement.
   THE LANDING: Wellesley has put 14,126 men ashore at Lisbon.
   Milan passes from Kingdom of Italy to Austria.
   Piedmont passes from Kingdom of Italy to Austria.
   Sire — the Kingdom of Italy has been eliminated from the war.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Allegiance.
   The court of Britain takes up a new design: The Paymaster of Coalitions.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 30 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +10, +1/turn)  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 47/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0193  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0193_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2071 of 2071 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,343 (+1,296 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 47/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0194  type status  ->  ok
  (typed and Enter)
view: <run>\frames\0194_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok === BERTHIER'S INTELLIGENCE REPORT ===

YOUR FORCES:
  Ney (Orleanais): 14,137 troops, morale 90, neutral stance, [MOVE_TO]
  Davout (Orleanais): 17,350 troops, morale 90, neutral stance, [MOVE_TO]
  Soult (Flanders): 28,567 troops, morale 100, neutral stance
  Lannes (Nivernais): 5,992 troops, morale 6, neutral stance, retreating
  Murat (Limousin): 10,281 troops, morale 60, neutral stance
  Bernadotte (Nivernais): 13,275 troops, morale 100, neutral stance
  Massena (Lyonnais): 13,185 troops, morale 0, neutral stance, retreating
  Napoleon (Flanders): 10,000 troops, morale 85, neutral stance
  Dumonceau (Normandy): 4,550 troops, morale 100, neutral stance
  Oudinot (Paris): 5,000 troops, morale 100, neutral stance

CONFIRMED INTELLIGENCE:
  Archduke Charles (Austria): 27,511 troops at Piedmont, defensive stance, morale 88 — famed for 'Habsburg Resolve'
  Cuesta (Spain): 7,262 troops at Normandy, aggressive stance, morale 100
  Milan (Austria): garrison of 2,000 holds the works

RECENT REPORTS:
  Swabia (Austria): garrison — screening force holds the works
  Castanos: small force near Guyenne
  Archduke John: substantial force near Munich
  Munich (Austria): garrison — small force holds the works
  Brunswick: large force near Oldenburg
  Moore, Shrapnel: large force near London

NO INTELLIGENCE: No word from 74 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.

── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2248 of 2248 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,343 (+1,296 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Orleanais): 14,137 troops, morale 90, neutral stance, [MOVE_TO]
   Davout (Orleanais): 17,350 troops, morale 90, neutral stance, [MOVE_TO]
   Soult (Flanders): 28,567 troops, morale 100, neutral stance
   Lannes (Nivernais): 5,992 troops, morale 6, neutral stance, retreating
   Murat (Limousin): 10,281 troops, morale 60, neutral stance
   Bernadotte (Nivernais): 13,275 troops, morale 100, neutral stance
   Massena (Lyonnais): 13,185 troops, morale 0, neutral stance, retreating
   Napoleon (Flanders): 10,000 troops, morale 85, neutral stance
   Dumonceau (Normandy): 4,550 troops, morale 100, neutral stance
   Oudinot (Paris): 5,000 troops, morale 100, neutral stance
   CONFIRMED INTELLIGENCE:
   Archduke Charles (Austria): 27,511 troops at Piedmont, defensive stance, morale 88 — famed for 'Habsburg Resolve'
   Cuesta (Spain): 7,262 troops at Normandy, aggressive stance, morale 100
   Milan (Austria): garrison of 2,000 holds the works
   RECENT REPORTS:
   Swabia (Austria): garrison — screening force holds the works
   Castanos: small force near Guyenne
   Archduke John: substantial force near Munich
   Munich (Austria): garrison — small force holds the works
   Brunswick: large force near Oldenburg
   Moore, Shrapnel: large force near London
   NO INTELLIGENCE: No word from 74 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
map: unchanged (59 labels)
```

```
#0195  type Bernadotte, march to Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0195_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte begins march to Franche-Comte. Moves to Franche-Comte. Bernadotte: "As ordered. I keep my flanks as I go."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Lorraine
   +5 ↑
   T:12
   controls: [THIRD COALITION  ▸]  [War for Lorraine]  [War with Britain — Britain, truce 2t]
── BottomLeftUI (layer 0) [scrolled 2334 of 2334 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,343 (+1,167 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   > Ney — Orleanais — 14,137 — Moving to Lorraine — arrives next turn.
   - Bernadotte — Nivernais — 13,275 — Awaiting orders. Trust:40
   < Massena — Lyonnais — 13,185 — Recovers T15. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Murat — Limousin — 10,281 — 3 turns idle.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   < Lannes — Nivernais — 5,992 — Recovers T14. Morale:6%
   ⚠ Morale failing (6) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Paris — 5,000 — Awaiting orders.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Piedmont — 27,511 [confirmed]
   Cuesta — Normandy — 7,262 [confirmed]
   Archduke John — Munich — substantial force [partial]
   Moore — London — large force [partial]
   Brunswick — Oldenburg — large force [partial]
   Castanos — Guyenne — small force [partial]
   Shrapnel — London — screening force [partial]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — small force [partial]
   Milan garrison — Milan — garrison of 2,000 [confirmed]
   TURN EVENTS
   Lannes's army is recovering. Effectiveness penalty: -15%.
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Munich's garrison regrows — small force.
   Milan's garrison regains 2,000: 0 -> 2,000.
   2 satellites drifted — Holland and Switzerland.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   Sire — Naples and France have signed the Open Borders Agreement.
   THE LANDING: Wellesley has put 14,126 men ashore at Lisbon.
   Milan passes from Kingdom of Italy to Austria.
   Piedmont passes from Kingdom of Italy to Austria.
   Sire — the Kingdom of Italy has been eliminated from the war.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Allegiance.
   The court of Britain takes up a new design: The Paymaster of Coalitions.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 30 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +10, +1/turn)  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 47/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Orleanais): 14,137 troops, morale 90, neutral stance, [MOVE_TO]
   Davout (Orleanais): 17,350 troops, morale 90, neutral stance, [MOVE_TO]
   Soult (Flanders): 28,567 troops, morale 100, neutral stance
   Lannes (Nivernais): 5,992 troops, morale 6, neutral stance, retreating
   Murat (Limousin): 10,281 troops, morale 60, neutral stance
   Bernadotte (Nivernais): 13,275 troops, morale 100, neutral stance
   Massena (Lyonnais): 13,185 troops, morale 0, neutral stance, retreating
   Napoleon (Flanders): 10,000 troops, morale 85, neutral stance
   Dumonceau (Normandy): 4,550 troops, morale 100, neutral stance
   Oudinot (Paris): 5,000 troops, morale 100, neutral stance
   CONFIRMED INTELLIGENCE:
   Archduke Charles (Austria): 27,511 troops at Piedmont, defensive stance, morale 88 — famed for 'Habsburg Resolve'
   Cuesta (Spain): 7,262 troops at Normandy, aggressive stance, morale 100
   Milan (Austria): garrison of 2,000 holds the works
   RECENT REPORTS:
   Swabia (Austria): garrison — screening force holds the works
   Castanos: small force near Guyenne
   Archduke John: substantial force near Munich
   Munich (Austria): garrison — small force holds the works
   Brunswick: large force near Oldenburg
   Moore, Shrapnel: large force near London
   NO INTELLIGENCE: No word from 74 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   ► Bernadotte, march to Franche-Comte
   Bernadotte begins march to Franche-Comte. Moves to Franche-Comte. Bernadotte: "As ordered. I keep my flanks as I go."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1985,554)  France(1572,534)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  31(1374,592)  18(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1764,616)  ?(1434,578)  Castanos(1434,540)  Murat(1600,506)  Massena(1648,541)  Bernadotte(1812,497)  ?(1901,548)  Archduke John(1901,521)  Ney(1682,440)  Davout(1736,419)  Brunswick(1700,266)  Lannes(1748,471)  Oudinot(1595,442)  Dumonceau(1539,399)  Cuesta(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1482,371)  Moore(1482,344)  ?(1510,371)  Shrapnel(1498,287)  ?(1869,762)  ?(1859,549)  ?(1901,591)  25k(1634,478)  12k(1551,470)  ?(1769,580)  ?(1792,420)  12k(1680,411)  ?(1490,427)  2k(1910,645)
```

```
#0196  type Murat, march to Lyonnais  ->  ok
  (typed and Enter)
view: <run>\frames\0196_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat begins march to Lyonnais. Moves to Lyonnais. Murat: "We march. Pity whatever slows us."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2444 of 2444 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   6,343 (+1,167 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, march to Lyonnais
   Murat begins march to Lyonnais. Moves to Lyonnais. Murat: "We march. Pity whatever slows us."
   [0/4 actions remaining]
map: unchanged (59 labels)
```

```
#0197  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0197_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 32 sail — readiness 68 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 47 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 32 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Sardinia's allegiance is in play @(3351,64)]  [icon: Kingdom of Italy Eliminated! @(3393,64)]  [icon: Soult arrived (x2) @(3435,64)]  [icon: Davout arrived (x2) @(3477,64)]  [icon: Ney arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2577 of 2577 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   5,943 (+1,205 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 32 sail — readiness 68 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1985,554)  France(1572,534)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  32(1374,592)  18(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1764,616)  ?(1434,578)  Castanos(1434,540)  Murat(1636,541)  Massena(1656,515)  Bernadotte(1812,497)  ?(1901,548)  Archduke John(1901,521)  Ney(1682,440)  Davout(1736,419)  Brunswick(1700,266)  Lannes(1748,471)  Oudinot(1595,442)  Dumonceau(1539,399)  Cuesta(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1482,371)  Moore(1482,344)  ?(1510,371)  Shrapnel(1498,287)  ?(1869,762)  ?(1859,549)  ?(1901,591)  25k(1593,497)  12k(1535,454)  ?(1769,580)  ?(1792,420)  12k(1680,411)  ?(1490,427)  2k(1910,645)
```

```
#0198  type lay down a ship of the line at Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0198_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 33 sail — readiness 67 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you say so.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 47 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 33 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Sardinia's allegiance is in play @(3351,64)]  [icon: Kingdom of Italy Eliminated! @(3393,64)]  [icon: Soult arrived (x2) @(3435,64)]  [icon: Davout arrived (x2) @(3477,64)]  [icon: Ney arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2711 of 2711 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   0/4
   Admin:
   0/2
   Gold:
   5,543 (+1,242 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 33 sail — readiness 67 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you say so.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1985,554)  France(1572,534)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  33(1374,592)  18(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1764,616)  ?(1434,578)  Castanos(1434,540)  Murat(1636,541)  Massena(1656,515)  Bernadotte(1812,497)  ?(1901,548)  Archduke John(1901,521)  Ney(1682,440)  Davout(1736,419)  Brunswick(1700,266)  Lannes(1748,471)  Oudinot(1595,442)  Dumonceau(1539,399)  Cuesta(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1482,371)  Moore(1482,344)  ?(1510,371)  Shrapnel(1498,287)  ?(1869,762)  ?(1859,549)  ?(1901,591)  25k(1593,497)  12k(1535,454)  ?(1769,580)  ?(1792,420)  12k(1680,411)  ?(1490,427)  2k(1910,645)
```

```
#0199  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0199_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2777 of 2777 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   0/4
   Admin:
   0/2
   Gold:
   5,543 (+1,242 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (27,511, Piedmont) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (59 labels)
```

```
#0200  look  ->  ok
  (a fresh frame)
view: <run>\frames\0200_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2777 of 2777 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 33 sail — readiness 67 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you
   [0/4 actions remaining]
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (27,511, Piedmont) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (59 labels)
```

```
#0201  type Massena, retreat  ->  ok
  (typed and Enter)
view: <run>\frames\0201_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena retreats from Lyonnais to Limousin.  Army begins recovery (currently at -55% effectiveness). Will recover over 3 turns.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2866 of 2866 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   0/4
   Admin:
   0/2
   Gold:
   5,543 (+1,242 next turn)
   Inf:
   91,660
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, retreat
   Massena retreats from Lyonnais to Limousin.  Army begins recovery (currently at -55% effectiveness). Will recover over 3 turns.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1985,554)  France(1572,534)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  33(1374,592)  18(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1764,616)  ?(1434,578)  Castanos(1434,540)  Massena(1600,506)  Murat(1644,541)  Bernadotte(1812,497)  ?(1901,548)  Archduke John(1901,521)  Ney(1682,440)  Davout(1736,419)  Brunswick(1700,266)  Lannes(1748,471)  Oudinot(1595,442)  Dumonceau(1539,399)  Cuesta(1563,373)  Soult(1704,322)  Napoleon(1728,296)  ?(1482,371)  Moore(1482,344)  ?(1510,371)  Shrapnel(1498,287)  ?(1869,762)  ?(1859,549)  ?(1901,591)  25k(1634,478)  12k(1536,454)  ?(1769,580)  ?(1792,420)  12k(1680,411)  ?(1490,427)  2k(1910,645)
```

```
#0202  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0202_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 13 ended. Turn 14 begins!

Income: 2271g | Contributions: -73g | Charges of Empire: -540g | Admiralty: -66g | Materiel: -289g | Upkeep: -872g | Other: +537g | Net: +968g | Spent: 800g | Treasury: 6,511g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 202 px] ──
   ENEMY PHASE - Turn 13
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Murat /     Battle of Lyonnais /     Archduke Charles: 832 casualties, 26,679 remaining /     Murat: 5,790 casualties, 4,491 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) — and advances into Lyonnais /     Murat forced to retreat! /     ⚔ View the field /     --- Berthier's Report --- /     Attack …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 44 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 33 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2780 of 2780 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,511 (+1,306 next turn)
   Inf:
   92,660
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   THE LANDING: Wellesley has put 14,126 men ashore at Lisbon.
   Milan passes from Kingdom of Italy to Austria.
   Piedmont passes from Kingdom of Italy to Austria.
   Sire — the Kingdom of Italy has been eliminated from the war.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Allegiance.
   The court of Britain takes up a new design: The Paymaster of Coalitions.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 30 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Franche-Comte) — the homeland — 25 of 28 provinces held (ticking: +10, +1/turn)  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Franche-Comte) — the homeland — 25 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 47/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Orleanais): 14,137 troops, morale 90, neutral stance, [MOVE_TO]
   Davout (Orleanais): 17,350 troops, morale 90, neutral stance, [MOVE_TO]
   Soult (Flanders): 28,567 troops, morale 100, neutral stance
   Lannes (Nivernais): 5,992 troops, morale 6, neutral stance, retreating
   Murat (Limousin): 10,281 troops, morale 60, neutral stance
   Bernadotte (Nivernais): 13,275 troops, morale 100, neutral stance
   Massena (Lyonnais): 13,185 troops, morale 0, neutral stance, retreating
   Napoleon (Flanders): 10,000 troops, morale 85, neutral stance
   Dumonceau (Normandy): 4,550 troops, morale 100, neutral stance
   Oudinot (Paris): 5,000 troops, morale 100, neutral stance
   CONFIRMED INTELLIGENCE:
   Archduke Charles (Austria): 27,511 troops at Piedmont, defensive stance, morale 88 — famed for 'Habsburg Resolve'
   Cuesta (Spain): 7,262 troops at Normandy, aggressive stance, morale 100
   Milan (Austria): garrison of 2,000 holds the works
   RECENT REPORTS:
   Swabia (Austria): garrison — screening force holds the works
   Castanos: small force near Guyenne
   Archduke John: substantial force near Munich
   Munich (Austria): garrison — small force holds the works
   Brunswick: large force near Oldenburg
   Moore, Shrapnel: large force near London
   NO INTELLIGENCE: No word from 74 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   ► Bernadotte, march to Franche-Comte
   Bernadotte begins march to Franche-Comte. Moves to Franche-Comte. Bernadotte: "As ordered. I keep my flanks as I go."
   [2/4 actions remaining]
   ► Murat, march to Lyonnais
   Murat begins march to Lyonnais. Moves to Lyonnais. Murat: "We march. Pity whatever slows us."
   [0/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 32 sail — readiness 68 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [0/4 actions remaining]
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 33 sail — readiness 67 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you say so.
   [0/4 actions remaining]
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (27,511, Piedmont) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► Massena, retreat
   Massena retreats from Lyonnais to Limousin.  Army begins recovery (currently at -55% effectiveness). Will recover over 3 turns.
   ► end turn
   ═══════════════════════════════════════
   TURN 14 BEGINS
   ═══════════════════════════════════════
   Income: 2271g | Contributions: -73g | Charges of Empire: -540g | Admiralty: -66g | Materiel: -289g | Other: +537g | Upkeep: -872g | Net: +968g | Spent: 800g
   Treasury: 6,511g
   Actions refreshed: 4/4
   Lannes's army has fully recovered and is combat ready.
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Garrison at Munich reinforced: 14,000 -> 16,000
   Garrison at Milan reinforced: 2,000 -> 4,000
   Holland loyalty 90 (-3): satellite drift, the lord's defeats
   Switzerland loyalty 80 (-3): satellite drift, the lord's defeats
   Britain subsidizes Austria with 300 gold.
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(1985,554)  France(1572,534)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  33(1354,613)  19(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1434,578)  Castanos(1434,540)  Massena(1600,506)  Murat(1636,541)  Archduke Charles(1656,480)  Bernadotte(1812,497)  ?(1901,548)  Archduke John(1901,521)  ?(1384,625)  Blake(1384,587)  Davout(1695,440)  Brunswick(1700,300)  Lannes(1748,521)  Ney(1684,506)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1859,549)  ?(1901,591)  12k(1513,436)  ?(1769,580)  10k(1755,420)  12k(1684,411)  ?(1468,417)  4k(1910,645)
```

```
#0203  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0203_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   DAVOUT REPORTS
   "Davout: 'Cannon fire at Lyonnais, Sire. Investigate?'"
   controls: [March to the Guns]  [Continue as Ordered]  [Hold Position]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 44 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 33 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Murat is cornered @(3351,64)]  [icon: Murat arrived (x2) @(3393,64)]  [icon: Bernadotte arrived (x2) @(3435,64)]  [icon: Marshal Soult seeks an audience @(3477,64)]  [icon: Kingdom of Italy Eliminated! @(3519,64)]  [icon: Soult arrived (x2) @(3561,64)]  [+26]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Lorraine
   +6 →
   T:13
   controls: [THIRD COALITION  ▸]  [War for Lorraine]  [War with Britain — Britain, truce 1t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1916 of 1916 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,511 (+1,306 next turn)
   Inf:
   92,660
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Murat: Murat arrives at Lyonnais. Murat: "Done — and I trust the next order has more fire in it."
   Davout: Davout: 'Cannon fire at Lyonnais, Sire. Investigate?'
   Ney: Ney hears cannon fire! Abandoning orders — rushing to Lyonnais! Ney moves from Orleanais to Burgundy
   Murat: Murat is cornered at Lyonnais with 4,491 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 14
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Murat was mauled at Lyonnais: half of his corps — 5,790 men — lost in a single action.
   • Sire — Lorraine and Rhineland lie in enemy hands. Austria holds them.
   • Sire — Archduke Charles has crossed into Lyonnais. Murat stands in his path.
   • Sire — the establishment stands 13,135 men under the ordinance, and the depots hold 92,660. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.
   • Sire — London now pays Vienna 300 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 26 regions. Treasury: 6,511g (+1,257 by the accounts)
   The courts at war hold 24 regions. Estimated enemy strength: 47% of French forces (an estimate — 1 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 28,567 — Awaiting orders.
   ? Davout — Orleanais — 17,350 — HALTED at Orleanais — awaiting your word.
   - Ney — Burgundy — 14,137 — Awaiting orders.
   < Massena — Limousin — 13,185 — Recovers T16. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Bernadotte — Franche-Comte — 13,143 — Awaiting orders. Trust:40
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Nivernais — 5,992 — Awaiting orders. Morale:6%
   ⚠ Morale failing (6) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Paris — 5,000 — 3 turns idle.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   ? Murat — Lyonnais — 4,491 — ENCIRCLED at Lyonnais by Archduke Charles — awaiting your word. Morale:0%
   ⚠ IN PERIL — an enemy force of ~26,056 shares the field (Lyonnais).
   INTELLIGENCE
   Archduke Charles — Lyonnais — 26,056 [confirmed]
   Brunswick — Oldenburg — 47,164 [confirmed]
   Archduke John — Munich — substantial force [partial]
   Moore — London — large force [partial]
   Castanos — Guyenne — small force [partial]
   Cuesta — Berry — screening force [partial]
   Blake — Bordelais — screening force [partial]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   Milan garrison — Milan — garrison of 4,000 [confirmed]
   TURN EVENTS
   Lannes's army has fully recovered and is combat ready.
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Munich's garrison regrows — substantial force.
   Milan's garrison regains 2,000: 2,000 -> 4,000.
   2 satellites drifted — Holland and Switzerland.
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Leon passes from Spain to Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
   The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 31 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Hesse may be ready to discuss improved relations. The diplomatic winds favor us.
   Sire, I believe Portugal may be ready to discuss improved relations. The diplomatic winds favor us.
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Lorraine) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Lorraine) — the homeland — 26 of 28 provinces held (ticking: +12, +1/turn)  |  Settlement (this pair): White Peace (+6)
   War Purpose: Defense vs Russia (War for Lorraine) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 44/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (59 labels)
```

```
#0204  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0204_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1916 of 1916 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (59 labels)
```

```
#0205  type what if Davout attacks Archduke Charles  ->  ERROR: the command line is not taking orders now (it is disabled)
view: <run>\frames\0205_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1916 of 1916 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (59 labels)
```

```
#0206  click Continue as Ordered  ->  ok
  (clicked at (1829, 551))
view: <run>\frames\0206_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Murat ◆
   Archduke Charles ◆
   10,281 → 4,491
   27,511 → 26,679 → 26,056 after the advance
   BATTLE OF LYONNAIS
   click anywhere to skip ▸
   LYONNAIS · TURN 13
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1982 of 1982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,511 (+1,307 next turn)
   Inf:
   92,660
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Lyonnais. Davout arrives at Lorraine. Davout: "It is done. I took the liberty of posting pickets."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(1994,558)  France(1580,531)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  33(1354,613)  19(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1434,578)  Castanos(1434,540)  Massena(1600,503)  Davout(1753,436)  Murat(1631,560)  Archduke Charles(1656,477)  Bernadotte(1812,497)  ?(1901,548)  Archduke John(1901,521)  ?(1384,625)  Blake(1384,587)  Brunswick(1700,300)  Lannes(1748,521)  Ney(1684,503)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1859,549)  ?(1901,591)  25k(1638,531)  12k(1513,436)  ?(1769,580)  12k(1696,420)  ?(1468,417)  4k(1910,645)
```

```
#0207  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0207_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   MURAT REPORTS
   "Murat is cornered at Lyonnais with 4,491 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2004 of 2004 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,511 (+1,307 next turn)
   Inf:
   92,660
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Murat awaits your orders!
map: unchanged (59 labels)
```

```
#0208  type what if Davout attacks Archduke Charles  ->  ERROR: the command line is not taking orders now (it is disabled)
view: <run>\frames\0208_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2004 of 2004 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Lyonnais. Davout arrives at Lorraine. Davout: "It is done. I took the liberty of posting pickets."
   Murat awaits your orders!
map: unchanged (59 labels)
```

```
#0209  look  ->  ok
  (a fresh frame)
view: <run>\frames\0209_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2004 of 2004 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Lyonnais. Davout arrives at Lorraine. Davout: "It is done. I took the liberty of posting pickets."
   Murat awaits your orders!
map: unchanged (59 labels)
```

```
#0210  look  ->  ok
  (a fresh frame)
view: <run>\frames\0210_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2004 of 2004 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Lyonnais. Davout arrives at Lorraine. Davout: "It is done. I took the liberty of posting pickets."
   Murat awaits your orders!
map: unchanged (59 labels)
```

```
#0211  click Attempt a Breakout  ->  ok
  (clicked at (1971, 584))
view: <run>\frames\0211_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 44 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 33 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Davout arrived (x3) @(3351,64)]  [icon: Murat arrived (x2) @(3393,64)]  [icon: Bernadotte arrived (x2) @(3435,64)]  [icon: Marshal Soult seeks an audience @(3477,64)]  [icon: Kingdom of Italy Eliminated! @(3519,64)]  [icon: Soult arrived (x2) @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2049 of 2049 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,511 (+1,339 next turn)
   Inf:
   92,660
   Cav:
   32,245
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Lyonnais! 2,245 of his men escape home to the depots.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(1994,558)  France(1580,531)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  33(1354,613)  19(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1434,578)  Castanos(1434,540)  Massena(1600,503)  Davout(1753,436)  Archduke Charles(1643,578)  Bernadotte(1812,497)  ?(1901,548)  Archduke John(1901,521)  ?(1384,625)  Blake(1384,587)  Brunswick(1700,300)  Lannes(1748,471)  Ney(1684,495)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1859,549)  ?(1901,591)  25k(1634,474)  12k(1513,436)  ?(1769,580)  12k(1696,420)  ?(1468,417)  4k(1910,645)
```

```
#0212  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0212_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2049 of 2049 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,511 (+1,339 next turn)
   Inf:
   92,660
   Cav:
   32,245
   Art:
   17,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Davout reluctantly continues his march, ignoring cannon fire at Lyonnais. Davout arrives at Lorraine. Davout: "It is done. I took the liberty of posting pickets."
   Murat awaits your orders!
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Lyonnais! 2,245 of his men escape home to the depots.
map: unchanged (58 labels)
```

```
#0213  type what if Bernadotte attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0213_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte stands at Franche-Comte, beyond reach of Archduke Charles at Lyonnais this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Ney and Massena stand within reach.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +13 ↑
   T:13
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Britain — Britain, truce 1t]
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,511 (+1,339 next turn)
   Inf:
   92,660
   Cav:
   32,245
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Bernadotte attacks Archduke Charles
   Bernadotte stands at Franche-Comte, beyond reach of Archduke Charles at Lyonnais this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Ney and Massena stand within reach.
map: unchanged (58 labels)
```

```
#0214  type what if Ney attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0214_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Ney (14,137) vs Archduke Charles (26,056 men) at Lyonnais — the balance of force looks unfavorable.
  WILL NOT — Massena: is in no condition to fight
  Standing modifiers, already in the band: Archduke Charles stands +24% on the defense (his stance, his character and his works).
  Lyonnais feeds 52,500 — the whole muster can stand there fed.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 14,137 we muster) would cost ~106g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.

Nothing has been ordered, and nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1916 of 1916 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,511 (+1,339 next turn)
   Inf:
   92,660
   Cav:
   32,245
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Ney attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Ney (14,137) vs Archduke Charles (26,056 men) at Lyonnais — the balance of force looks unfavorable.
   WILL NOT — Massena: is in no condition to fight
   Standing modifiers, already in the band: Archduke Charles stands +24% on the defense (his stance, his character and his works).
   Lyonnais feeds 52,500 — the whole muster can stand there fed.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 14,137 we muster) would cost ~106g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (58 labels)
```

```
#0215  type Davout, march to Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0215_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout begins march to Franche-Comte. Moves to Franche-Comte. Davout: "The roads will be scouted before each march, Sire."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1917 of 1917 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,511 (+1,339 next turn)
   Inf:
   92,660
   Cav:
   32,245
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   < Massena — Limousin — 13,185 — Recovers T16. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Bernadotte — Franche-Comte — 13,143 — Awaiting orders. Trust:40
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Nivernais — 5,992 — Awaiting orders. Morale:6%
   ⚠ Morale failing (6) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Paris — 5,000 — 3 turns idle.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   ? Murat — Lyonnais — 4,491 — ENCIRCLED at Lyonnais by Archduke Charles — awaiting your word. Morale:0%
   ⚠ IN PERIL — an enemy force of ~26,056 shares the field (Lyonnais).
   INTELLIGENCE
   Archduke Charles — Lyonnais — 26,056 [confirmed]
   Brunswick — Oldenburg — 47,164 [confirmed]
   Archduke John — Munich — substantial force [partial]
   Moore — London — large force [partial]
   Castanos — Guyenne — small force [partial]
   Cuesta — Berry — screening force [partial]
   Blake — Bordelais — screening force [partial]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   Milan garrison — Milan — garrison of 4,000 [confirmed]
   TURN EVENTS
   Lannes's army has fully recovered and is combat ready.
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Munich's garrison regrows — substantial force.
   Milan's garrison regains 2,000: 2,000 -> 4,000.
   2 satellites drifted — Holland and Switzerland.
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Leon passes from Spain to Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
   The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 31 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Hesse may be ready to discuss improved relations. The diplomatic winds favor us.
   Sire, I believe Portugal may be ready to discuss improved relations. The diplomatic winds favor us.
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Lorraine) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Lorraine) — the homeland — 26 of 28 provinces held (ticking: +12, +1/turn)  |  Settlement (this pair): White Peace (+6)
   War Purpose: Defense vs Russia (War for Lorraine) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 44/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Lyonnais. Davout arrives at Lorraine. Davout: "It is done. I took the liberty of posting pickets."
   Murat awaits your orders!
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Lyonnais! 2,245 of his men escape home to the depots.
   ► what if Bernadotte attacks Archduke Charles
   Bernadotte stands at Franche-Comte, beyond reach of Archduke Charles at Lyonnais this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Ney and Massena stand within reach.
   ► what if Ney attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Ney (14,137) vs Archduke Charles (26,056 men) at Lyonnais — the balance of force looks unfavorable.
   WILL NOT — Massena: is in no condition to fight
   Standing modifiers, already in the band: Archduke Charles stands +24% on the defense (his stance, his character and his works).
   Lyonnais feeds 52,500 — the whole muster can stand there fed.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 14,137 we muster) would cost ~106g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► Davout, march to Franche-Comte
   Davout begins march to Franche-Comte. Moves to Franche-Comte. Davout: "The roads will be scouted before each march, Sire."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(1994,558)  France(1580,531)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  33(1354,613)  19(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1434,578)  Castanos(1434,540)  Massena(1600,503)  Archduke Charles(1643,578)  Davout(1801,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  ?(1384,625)  Blake(1384,587)  Brunswick(1700,300)  Lannes(1733,486)  Ney(1680,495)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1862,529)  ?(1901,591)  25k(1634,474)  12k(1513,436)  ?(1769,580)  10k(1755,420)  12k(1710,420)  ?(1468,417)  4k(1910,645)
```

```
#0216  type Ney, march to Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0216_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins march to Franche-Comte. Route: Nivernais → Franche-Comte. Moves to Nivernais. Ney: "Good. An army rots standing still."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2027 of 2027 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   6,511 (+1,339 next turn)
   Inf:
   92,660
   Cav:
   32,245
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, march to Franche-Comte
   Ney begins march to Franche-Comte. Route: Nivernais → Franche-Comte. Moves to Nivernais. Ney: "Good. An army rots standing still."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(1994,558)  France(1580,531)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  33(1354,613)  19(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1434,578)  Castanos(1434,540)  Massena(1600,503)  Archduke Charles(1643,578)  Davout(1801,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  ?(1384,625)  Blake(1384,587)  Brunswick(1700,300)  Ney(1735,486)  Lannes(1760,445)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1862,529)  ?(1901,591)  25k(1634,474)  12k(1513,436)  ?(1769,580)  12k(1704,420)  ?(1468,417)  4k(1910,645)
```

```
#0217  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0217_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 34 sail — readiness 71 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 44 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 34 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Davout arrived (x3) @(3351,64)]  [icon: Murat arrived (x2) @(3393,64)]  [icon: Bernadotte arrived (x2) @(3435,64)]  [icon: Marshal Soult seeks an audience @(3477,64)]  [icon: Kingdom of Italy Eliminated! @(3519,64)]  [icon: Soult arrived (x2) @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2160 of 2160 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   6,111 (+1,380 next turn)
   Inf:
   92,660
   Cav:
   32,245
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 34 sail — readiness 71 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(1994,558)  France(1580,531)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  34(1354,613)  19(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1434,578)  Castanos(1434,540)  Massena(1600,503)  Archduke Charles(1643,578)  Davout(1801,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  ?(1384,625)  Blake(1384,587)  Brunswick(1700,300)  Ney(1735,486)  Lannes(1760,445)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1862,529)  ?(1901,591)  25k(1634,474)  12k(1513,436)  ?(1769,580)  12k(1704,420)  ?(1468,417)  4k(1910,645)
```

```
#0218  type lay down a ship of the line at Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0218_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 35 sail — readiness 70 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you say so.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 44 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 35 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Davout arrived (x3) @(3351,64)]  [icon: Murat arrived (x2) @(3393,64)]  [icon: Bernadotte arrived (x2) @(3435,64)]  [icon: Marshal Soult seeks an audience @(3477,64)]  [icon: Kingdom of Italy Eliminated! @(3519,64)]  [icon: Soult arrived (x2) @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2294 of 2294 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   0/4
   Admin:
   0/2
   Gold:
   5,711 (+1,421 next turn)
   Inf:
   92,660
   Cav:
   32,245
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 35 sail — readiness 70 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you say so.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(1994,558)  France(1580,531)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  35(1354,613)  19(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1434,578)  Castanos(1434,540)  Massena(1600,503)  Archduke Charles(1643,578)  Davout(1801,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  ?(1384,625)  Blake(1384,587)  Brunswick(1700,300)  Ney(1735,486)  Lannes(1760,445)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1862,529)  ?(1901,591)  25k(1634,474)  12k(1513,436)  ?(1769,580)  12k(1704,420)  ?(1468,417)  4k(1910,645)
```

```
#0219  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0219_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2360 of 2360 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   0/4
   Admin:
   0/2
   Gold:
   5,711 (+1,421 next turn)
   Inf:
   92,660
   Cav:
   32,245
   Art:
   17,800
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (26,056, Lyonnais) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (58 labels)
```

```
#0220  look  ->  ok
  (a fresh frame)
view: <run>\frames\0220_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2360 of 2360 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 35 sail — readiness 70 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you
   [0/4 actions remaining]
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (26,056, Lyonnais) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (58 labels)
```

```
#0221  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0221_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 14 ended. Turn 15 begins!

Income: 2229g | Charges of Empire: -620g | Admiralty: -70g | Blockade: -336g | Materiel: -84g | Upkeep: -808g | Other: +762g | Net: +1073g | Spent: 800g | Treasury: 6,784g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 245 px] ──
   ENEMY PHASE - Turn 14
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Lyonnais /     Region captured: Lyonnais (was France) (secured) / - Mack attacks Bernadotte /     Third Battle of Franche-Comte /     Mack: 5,425 casualties, 21,524 remaining /     Bernadotte's army: 1,687 casualties — Bernadotte's own corps: 12,086 remaining /     Result: Defender tactical victory (Bernadotte victorious) /     Ma …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 41 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 35 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2319 of 2320 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,784 (+989 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Munich's garrison regrows — substantial force.
   Milan's garrison regains 2,000: 2,000 -> 4,000.
   2 satellites drifted — Holland and Switzerland.
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Leon passes from Spain to Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
   The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 31 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Hesse may be ready to discuss improved relations. The diplomatic winds favor us.
   Sire, I believe Portugal may be ready to discuss improved relations. The diplomatic winds favor us.
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Lorraine) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Lorraine) — the homeland — 26 of 28 provinces held (ticking: +12, +1/turn)  |  Settlement (this pair): White Peace (+6)
   War Purpose: Defense vs Russia (War for Lorraine) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 44/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Lyonnais. Davout arrives at Lorraine. Davout: "It is done. I took the liberty of posting pickets."
   Murat awaits your orders!
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Lyonnais! 2,245 of his men escape home to the depots.
   ► what if Bernadotte attacks Archduke Charles
   Bernadotte stands at Franche-Comte, beyond reach of Archduke Charles at Lyonnais this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Ney and Massena stand within reach.
   ► what if Ney attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Ney (14,137) vs Archduke Charles (26,056 men) at Lyonnais — the balance of force looks unfavorable.
   WILL NOT — Massena: is in no condition to fight
   Standing modifiers, already in the band: Archduke Charles stands +24% on the defense (his stance, his character and his works).
   Lyonnais feeds 52,500 — the whole muster can stand there fed.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 14,137 we muster) would cost ~106g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► Davout, march to Franche-Comte
   Davout begins march to Franche-Comte. Moves to Franche-Comte. Davout: "The roads will be scouted before each march, Sire."
   [2/4 actions remaining]
   ► Ney, march to Franche-Comte
   Ney begins march to Franche-Comte. Route: Nivernais → Franche-Comte. Moves to Nivernais. Ney: "Good. An army rots standing still."
   [0/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 34 sail — readiness 71 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [0/4 actions remaining]
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 35 sail — readiness 70 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn. That was the last order the day could take, Sire — the turn ends when you say so.
   [0/4 actions remaining]
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (26,056, Lyonnais) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► end turn
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2229g | Charges of Empire: -620g | Admiralty: -70g | Blockade: -336g | Materiel: -84g | Other: +762g | Upkeep: -808g | Net: +1073g | Spent: 800g
   Treasury: 6,784g
   Actions refreshed: 4/4
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Crowded at Franche-Comte: Ney loses 413 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Davout loses 510 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 171 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Bernadotte loses 362 troops to the press of 4 corps on one province's roads
   Garrison at Munich reinforced: 16,000 -> 18,000
   The armistice between Britain and France has collapsed. War resumes.
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Britain and Portugal grows.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Bernadotte's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1269,811)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1578,529)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1407,384)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,413)  35(1354,613)  20(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  Massena(1600,502)  Archduke Charles(1643,578)  Ney +3(1813,487)  ?(1384,625)  Castanos(1384,587)  Brunswick(1700,300)  Oudinot(1595,442)  Dumonceau(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1859,519)  ?(1901,591)  25k(1634,474)  12k(1513,436)  ?(1769,580)  10k(1755,420)  12k(1710,420)  ?(1468,417)  ?(1910,645)
```

```
#0222  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0222_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   5,992 → 5,703
   Ney
   14,137 → 13,796
   ⚔
   Bernadotte ◆
   Mack ◆
   13,143 → 12,086
   26,949 → 21,524
   marched to the guns
   marched to the guns
   THIRD BATTLE OF FRANCHE-COMTE
   click anywhere to skip ▸
   FRANCHE-COMTE · TURN 14
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 41 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 35 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3351,64)]  [icon: Petition from Switzerland @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Britain binds Russia to the war @(3477,64)]  [icon: Blockade — Britain closes our ports @(3519,64)]  [icon: Ney arrived (x4) @(3561,64)]  [+32]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Asturias
   +9 →
   T:14
   controls: [THIRD COALITION  ▸]  [War for Asturias]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1915 of 1915 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,784 (+989 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of 26,056 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Marshal Murat has been taken. Austria holds him prisoner.
   • Sire — Aragon has been taken by Britain.
   • Sire — the establishment stands 21,113 men under the ordinance, and the depots hold 93,660. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.
   SITUATION
   France holds 26 regions. Treasury: 6,784g (+1,157 by the accounts)
   The courts at war hold 37 regions. Estimated enemy strength: 76% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 28,567 — Awaiting orders.
   - Davout — Franche-Comte — 16,496 — Awaiting orders.
   - Ney — Franche-Comte — 13,383 — Awaiting orders.
   < Massena — Limousin — 13,185 — Recovers T16. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   » Bernadotte — Franche-Comte — 11,724 — Threw back the enemy — may strike once, free, this turn only. Trust:40
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Franche-Comte — 5,532 — Awaiting orders. Morale:1%
   ⚠ Morale failing (1) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Paris — 5,000 — 4 turns idle.
   - Dumonceau — Normandy — 4,550 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Lyonnais — 26,056 [confirmed]
   Brunswick — Oldenburg — 47,164 [confirmed]
   Moore — London — large force [partial]
   Castanos — Bordelais — small force [partial]
   Cuesta — Berry — screening force [partial]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [partial]
   Milan garrison — Milan — garrison — small force [stale - T12]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Supply cost you 1,456 men, at Franche-Comte.
   Munich's garrison regrows — substantial force.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Bernadotte's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   DIPLOMATIC EVENTS
   Aragon passes from Spain to Britain.
   Galicia passes from Spain to Britain.
   Asturias passes from Spain to Britain.
   Aragon passes from Britain to Spain.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   The armistice between Britain and France has collapsed. War resumes!
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
   REVANCHE: Spain will not forgive Britain the loss of Galicia and 1 more province. A new design hardens in their court.
   The court of Spain takes up a new design: Revanche.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 31 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Asturias) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Asturias) — the homeland — 26 of 28 provinces held (ticking: +14, +1/turn)  |  Settlement (this pair): White Peace (+12)
   War Purpose: Defense vs Russia (War for Asturias) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 41/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0223  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0223_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1915 of 1915 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,784 (+989 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 41/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0224  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0224_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 860 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Late April 1806 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location: Fl …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1915 of 1915 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,784 (+989 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 41/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0225  click ADMIRALTY  ->  ok
  (clicked at (2049, 283))
view: <run>\frames\0225_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 1036 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late April 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 35 sail of the line — readiness 65  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — staging the camp lifts the bl …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in East Anglia>  <Land Dumonceau in Cornwall>  <Land Dumonceau in Midlands>  <Land Dumonceau in Wales>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1915 of 1915 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 41/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0226  scroll 1800 600 down 5  ->  ok
  (scrolled down 5 at (1800, 600))
view: <run>\frames\0226_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 288 of 1038 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late April 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 35 sail of the line — readiness 65  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — staging the camp lifts the bl …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in East Anglia>  <Land Dumonceau in Cornwall>  <Land Dumonceau in Midlands>  <Land Dumonceau in Wales>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1915 of 1915 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 41/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0227  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0227_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Asturias
   +9 →
   T:14
   controls: [THIRD COALITION  ▸]  [War for Asturias]
── BottomLeftUI (layer 0) [scrolled 1915 of 1915 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 41/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0228  click_at 1335 245  ->  ok
  (clicked at (1335, 245) on MapArea '97' (Control, layer 0))
view: <run>\frames\0228_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 67 px] ──
   Ulster
   Britain  City · Plains / Stripped? unknown — scout it / ACTIONS /     Land Dumonceau here    4,550 men from Normandy · 75 in 100 slip past /       What moves the odds: a won diversion first (40 in 100) → 95 /  / One province — who holds it, what it pays, what defends it. Click the map to choose another. / No intelligence — scout or advance to learn more. / Income: Unknown   Stability: Unknown   Su …
   controls: [icon @(535,73)]  <Land Dumonceau here>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1915 of 1915 px]: unchanged
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 41/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0229  click Land Dumonceau here  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0229_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   DUMONCEAU ASKS:
   "The expedition is drawn up, Sire: Dumonceau with 4,550 men, Normandy to Ulster. The transports slip past unseen 75 times in 100 (Britain watches at 97 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. If she is intercepted she meets Britain's 112 effective against our 34 — a decisive defeat is …
   controls: [Sail for Ulster]  [Stand down]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 41 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 35 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1981 of 1981 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,784 (+989 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► land Dumonceau in Ulster
   Dumonceau requests clarification...
map: unchanged (52 labels)
```

```
#0230  click Sail for Ulster  ->  ok
  (clicked at (1829, 598))
view: <run>\frames\0230_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond with us rises 20 → 40 (worth +2 a turn in loyalty, now +1), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (20 → 0: worth +0 a turn in loyalty, now …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2091 of 2091 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,784 (+1,026 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > land Dumonceau in Ulster confirmed
   THE LANDING: Dumonceau slips past the British patrols and puts 4,550 men ashore at Ulster (odds were 75 in 100). Ulster lies open, but Dumonceau's 4,550 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto.
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1269,811)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1578,529)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1407,384)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,413)  35(1354,613)  20(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  Dumonceau(1322,223)  Massena(1600,502)  Archduke Charles(1643,578)  Ney +3(1813,487)  ?(1384,625)  Castanos(1384,587)  Brunswick(1700,300)  Oudinot(1595,442)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1859,519)  ?(1901,591)  25k(1634,474)  12k(1536,436)  ?(1769,580)  10k(1755,420)  12k(1710,420)  ?(1490,417)  ?(1910,645)
```

```
#0231  click Grant  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0231_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 41 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 35 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3351,64)]  [icon: Armistice Collapsed @(3393,64)]  [icon: Blockade — Britain closes our ports @(3435,64)]  [icon: Ney arrived (x4) @(3477,64)]  [icon: Davout arrived (x4) @(3519,64)]  [icon: Murat arrived (x2) @(3561,64)]  [+30]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Asturias
   +9 →
   T:14
   controls: [THIRD COALITION  ▸]  [War for Asturias]
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,784 (+801 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (52 labels)
```

```
#0232  look  ->  ok
  (a fresh frame)
view: <run>\frames\0232_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   THE LANDING: Dumonceau slips past the British patrols and puts 4,550 men ashore at Ulster (odds were 75 in 100). Ulster lies open, but Dumonceau's 4,550 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto.
   [2/4 actions remaining]
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (52 labels)
```

```
#0233  type Oudinot, march to Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0233_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Oudinot begins march to Normandy. Moves to Normandy. Oudinot: "At the double, Sire — the men will smell powder soon enough."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2269 of 2269 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   6,784 (+801 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Oudinot, march to Normandy
   Oudinot begins march to Normandy. Moves to Normandy. Oudinot: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
map: unchanged (52 labels)
```

```
#0234  type what can I do  ->  ok
  (typed and Enter)
view: <run>\frames\0234_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok These orders would be carried out today, Sire:
  end turn — no military actions remain today
  recruit infantry in Flanders — 600g for 3,000 men under Soult
  build supply depot in Paris — 300g
For any matter of state, press F1 for the Cabinet.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1828 of 1828 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   6,784 (+801 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   INTELLIGENCE
   Archduke Charles — Lyonnais — 26,056 [confirmed]
   Brunswick — Oldenburg — 47,164 [confirmed]
   Moore — London — large force [partial]
   Castanos — Bordelais — small force [partial]
   Cuesta — Berry — screening force [partial]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [partial]
   Milan garrison — Milan — garrison — small force [stale - T12]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Supply cost you 1,456 men, at Franche-Comte.
   Munich's garrison regrows — substantial force.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Bernadotte's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   DIPLOMATIC EVENTS
   Aragon passes from Spain to Britain.
   Galicia passes from Spain to Britain.
   Asturias passes from Spain to Britain.
   Aragon passes from Britain to Spain.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   The armistice between Britain and France has collapsed. War resumes!
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
   REVANCHE: Spain will not forgive Britain the loss of Galicia and 1 more province. A new design hardens in their court.
   The court of Spain takes up a new design: Revanche.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 31 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Asturias) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Asturias) — the homeland — 26 of 28 provinces held (ticking: +14, +1/turn)  |  Settlement (this pair): White Peace (+12)
   War Purpose: Defense vs Russia (War for Asturias) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 41/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   ► land Dumonceau in Ulster
   Dumonceau requests clarification...
   > land Dumonceau in Ulster confirmed
   THE LANDING: Dumonceau slips past the British patrols and puts 4,550 men ashore at Ulster (odds were 75 in 100). Ulster lies open, but Dumonceau's 4,550 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto.
   [2/4 actions remaining]
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP.
   ► Oudinot, march to Normandy
   Oudinot begins march to Normandy. Moves to Normandy. Oudinot: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
   ► what can I do
   These orders would be carried out today, Sire:
   end turn — no military actions remain today
   recruit infantry in Flanders — 600g for 3,000 men under Soult
   build supply depot in Paris — 300g
   For any matter of state, press F1 for the Cabinet.
map: unchanged (52 labels)
```

```
#0235  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0235_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 36 sail — readiness 64 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 6/7
   Threat 41 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3351,64)]  [icon: Armistice Collapsed @(3393,64)]  [icon: Blockade — Britain closes our ports @(3435,64)]  [icon: Ney arrived (x4) @(3477,64)]  [icon: Davout arrived (x4) @(3519,64)]  [icon: Murat arrived (x2) @(3561,64)]  [+30]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1984 of 1984 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   6,384 (+844 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 36 sail — readiness 64 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1269,811)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1578,529)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1407,384)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,413)  36(1354,613)  20(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  Dumonceau(1322,223)  Massena(1600,502)  Archduke Charles(1643,578)  Ney +3(1813,487)  ?(1384,625)  Castanos(1384,587)  Brunswick(1700,300)  Oudinot(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Moore(1490,328)  ?(1869,762)  ?(1859,519)  ?(1901,591)  25k(1595,474)  12k(1589,443)  ?(1769,580)  10k(1755,420)  12k(1710,420)  ?(1490,417)  ?(1910,645)
```

```
#0236  type lay down a ship of the line at Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0236_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: The yards are at capacity this season (1 keel per turn — the blockade slows the slips). Time, not gold, builds a navy.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2073 of 2073 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   6,384 (+844 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Normandy
   The yards are at capacity this season (1 keel per turn — the blockade slows the slips). Time, not gold, builds a navy.
map: unchanged (52 labels)
```

```
#0237  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0237_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2138 of 2138 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   6,384 (+844 next turn)
   Inf:
   93,660
   Cav:
   30,000
   Art:
   18,400
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (26,056, Lyonnais) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (52 labels)
```

```
#0238  look  ->  ok
  (a fresh frame)
view: <run>\frames\0238_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2138 of 2138 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► lay down a ship of the line at Normandy
   The yards are at capacity this season (1 keel per turn — the blockade slows the slips). Time, not gold, builds a navy.
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (26,056, Lyonnais) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (52 labels)
```

```
#0239  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0239_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 15 ended. Turn 16 begins!

Income: 1974g | Requisitions: +37g | Charges of Empire: -722g | Admiralty: -72g | Blockade: -336g | Materiel: -342g | Upkeep: -744g | Other: +562g | Net: +357g | Spent: 400g | Treasury: 6,741g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 532 px] ──
   ENEMY PHASE - Turn 15
   BRITAIN / ──────────────────────────── / - Wellesley attacks Blake /     Battle of Leon /     Wellesley: 532 casualties, 12,902 remaining /     Blake: 1,257 casualties, 3,546 remaining /     Result: Attacker tactical victory (Wellesley victorious) — and advances into Leon /     ⚔ View the field /     --- Berthier's Report --- /     Attack: Wellesley (Defensive stance -10%) /     Berthier: "A stand …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 38 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2164 of 2165 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,741 (+599 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Asturias passes from Spain to Britain.
   Aragon passes from Britain to Spain.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   The armistice between Britain and France has collapsed. War resumes!
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
   REVANCHE: Spain will not forgive Britain the loss of Galicia and 1 more province. A new design hardens in their court.
   The court of Spain takes up a new design: Revanche.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 31 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Asturias) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Asturias) — the homeland — 26 of 28 provinces held (ticking: +14, +1/turn)  |  Settlement (this pair): White Peace (+12)
   War Purpose: Defense vs Russia (War for Asturias) — the homeland — 26 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 41/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   ► land Dumonceau in Ulster
   Dumonceau requests clarification...
   > land Dumonceau in Ulster confirmed
   THE LANDING: Dumonceau slips past the British patrols and puts 4,550 men ashore at Ulster (odds were 75 in 100). Ulster lies open, but Dumonceau's 4,550 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto.
   [2/4 actions remaining]
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP.
   ► Oudinot, march to Normandy
   Oudinot begins march to Normandy. Moves to Normandy. Oudinot: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
   ► what can I do
   These orders would be carried out today, Sire:
   end turn — no military actions remain today
   recruit infantry in Flanders — 600g for 3,000 men under Soult
   build supply depot in Paris — 300g
   For any matter of state, press F1 for the Cabinet.
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 36 sail — readiness 64 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
   [0/4 actions remaining]
   ► lay down a ship of the line at Normandy
   The yards are at capacity this season (1 keel per turn — the blockade slows the slips). Time, not gold, builds a navy.
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (26,056, Lyonnais) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 1974g | Requisitions: +37g | Charges of Empire: -722g | Admiralty: -72g | Blockade: -336g | Materiel: -342g | Other: +562g | Upkeep: -744g | Net: +357g | Spent: 400g
   Treasury: 6,741g
   Actions refreshed: 4/4
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   [!] Bernadotte's Counter-Punch opportunity has expired! (Must use immediately after defending)
   Crowded at Franche-Comte: Ney loses 401 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Davout loses 494 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 165 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Bernadotte loses 351 troops to the press of 4 corps on one province's roads
   Garrison at Munich reinforced: 18,000 -> 20,000
   Switzerland loyalty 88 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Britain subsidizes Austria with 300 gold.
   Peace concluded between Britain and Spain without France. Both courts are spent; their side of the war ends while the greater war goes on. Unheld homeland returns to its crown: Asturias.
   Berthier notes that Soult no longer presses the matter — his quarrel with Ney has cooled.
   Soult's resentment of Ney has cooled with time.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   Berthier: Enemy forces spotted near Paris! Archduke Charles (24,660 troops) at Berry.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1917,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  36(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,528)  Archduke Charles(1517,501)  ?(1545,528)  Cuesta(1522,443)  Wellesley(1273,648)  Dumonceau(1322,223)  Ney +3(1813,487)  Brunswick(1700,300)  Massena(1595,442)  Oudinot(1551,399)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,371)  Paget(1490,344)  ?(1869,762)  ?(1859,519)  ?(1901,591)  25k(1619,503)  12k(1538,470)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1490,414)  ?(1910,645)
```

```
#0240  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0240_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   13,185 → 6,327
   26,056 → 25,723 → 25,172 after the advance
   BATTLE OF LIMOUSIN
   click anywhere to skip ▸
   LIMOUSIN · TURN 15
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 38 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Blockade — Britain closes our ports @(3393,64)]  [icon: Settlement offer from Austria @(3435,64)]  [icon: Oudinot arrived @(3477,64)]  [icon: Ney arrived (x4) @(3519,64)]  [icon: Davout arrived (x4) @(3561,64)]  [+30]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Berry
   -6 →
   T:15
   controls: [THIRD COALITION  ▸]  [War for Berry]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1936 of 1936 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,741 (+599 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   • Sire — Berry has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Massena's corps has been broken at Limousin. He must reform before he fights again.
   • Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 24,382 men at Paris, and nobody has gone to collect them.
   SITUATION
   France holds 24 regions. Treasury: 6,741g (+699 by the accounts)
   The courts at war hold 37 regions. Estimated enemy strength: 50% of French forces (an estimate — 2 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 28,567 — Awaiting orders.
   - Davout — Franche-Comte — 16,002 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Ney — Franche-Comte — 12,982 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franche-Comte — 11,373 — Awaiting orders. Trust:40
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   < Massena — Paris — 6,327 — Has fallen back 2 times in five turns — now at Paris with 6,327 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Lannes — Franche-Comte — 5,367 — Awaiting orders. Morale:1%
   ⚠ Morale failing (1) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Normandy — 5,000 — Awaiting orders.
   - Dumonceau — Ulster — 4,550 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Oldenburg — 50,164 [confirmed]
   Wellesley — Leon — 12,773 [confirmed]
   Archduke Charles — Berry — substantial force [partial]
   Paget — London — small force [partial]
   Cuesta — Berry — screening force [partial]
   Blake — Leon — screening force [last known - T15]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [partial]
   Milan garrison — Milan — garrison — small force [stale - T12]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   [!] Bernadotte's Counter-Punch opportunity has expired! (Must use immediately after defending)
   Supply cost you 1,411 men, at Franche-Comte.
   Munich's garrison regrows — substantial force.
   Switzerland loyalty 88 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier notes that Soult no longer presses the matter — his quarrel with Ney has cooled.
   Soult's resentment of Ney has cooled with time.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   DIPLOMATIC EVENTS
   THE LANDING: Dumonceau has put 4,550 men ashore at Ulster.
   Galicia passes from Britain to Spain.
   Austria, for Austria and Russia, has offered terms to settle the War for Berry — Britain + Austria + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on. Unheld homeland returns to its crown: Asturias.
   THE CAMP: France has massed 43,567 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   The court of Austria hardens over Redeem Italy — prepared now to go as far as war.
   The court of Britain hardens over The Paymaster of Coalitions — prepared now to go as far as war.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Austria — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 29 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Saxony may be ready to discuss improved relations. The diplomatic winds favor us.
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Berry) — the homeland — 24 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Austria (War for Berry) — the homeland — 24 of 28 provinces held (ticking: +18, +1/turn)  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War for Berry) — the homeland — 24 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 38/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0241  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0241_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1936 of 1936 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,741 (+599 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 38/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0242  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0242_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 2093 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 16 — Early May 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Limousin has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against  …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1936 of 1936 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,741 (+599 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 38/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0243  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0243_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Berry
   -6 →
   T:15
   controls: [THIRD COALITION  ▸]  [War for Berry]
── BottomLeftUI (layer 0) [scrolled 1936 of 1936 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 38/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0244  type status  ->  ok
  (typed and Enter)
view: <run>\frames\0244_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
reply: ok === BERTHIER'S INTELLIGENCE REPORT ===

YOUR FORCES:
  Ney (Franche-Comte): 12,982 troops, morale 85, neutral stance
  Davout (Franche-Comte): 16,002 troops, morale 90, neutral stance
  Soult (Flanders): 28,567 troops, morale 100, neutral stance
  Lannes (Franche-Comte): 5,367 troops, morale 1, neutral stance
  Bernadotte (Franche-Comte): 11,373 troops, morale 95, neutral stance
  Massena (Paris): 6,327 troops, morale 0, neutral stance, retreating
  Napoleon (Flanders): 10,000 troops, morale 85, neutral stance
  Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
  Oudinot (Normandy): 5,000 troops, morale 100, neutral stance

PRISONERS:
  Murat: held by Austria at Vienna since T14.

CONFIRMED INTELLIGENCE:
  Wellesley (Britain): 12,773 troops at Leon, defensive stance, morale 82
  Brunswick (Prussia): 50,164 troops at Oldenburg, defensive stance, morale 86

RECENT REPORTS:
  Archduke Charles, Cuesta: substantial force near Berry
  Swabia (Austria): garrison — screening force holds the works
  Munich (Austria): garrison — substantial force holds the works
  Paget: small force near London
  London (Britain): garrison — substantial force holds the works
  Milan (Austria): garrison — small force holds the works [4 turns ago]

NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.

── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px] ──
   SETTLEMENT OFFER FROM AUSTRIA /  / the War for Berry — Britain + Austria + Russia /  / "Vienna submits terms for the War for Berry — Britain + Austria + Russia with no gold either way. Metternich prefers a settlement that leaves no ledger to argue over afterwards." /  / Their proposed terms: /   • Peace /   • Berry, Limousin, Lyonnais and Rhineland stay with Austria by this peace — French soil beh …
   controls: [Review Settlement Offer]  [Request Revision]  [Reject Offer]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 38 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2662 of 2662 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,741 (+599 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Franche-Comte): 12,982 troops, morale 85, neutral stance
   Davout (Franche-Comte): 16,002 troops, morale 90, neutral stance
   Soult (Flanders): 28,567 troops, morale 100, neutral stance
   Lannes (Franche-Comte): 5,367 troops, morale 1, neutral stance
   Bernadotte (Franche-Comte): 11,373 troops, morale 95, neutral stance
   Massena (Paris): 6,327 troops, morale 0, neutral stance, retreating
   Napoleon (Flanders): 10,000 troops, morale 85, neutral stance
   Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
   Oudinot (Normandy): 5,000 troops, morale 100, neutral stance
   PRISONERS:
   Murat: held by Austria at Vienna since T14.
   CONFIRMED INTELLIGENCE:
   Wellesley (Britain): 12,773 troops at Leon, defensive stance, morale 82
   Brunswick (Prussia): 50,164 troops at Oldenburg, defensive stance, morale 86
   RECENT REPORTS:
   Archduke Charles, Cuesta: substantial force near Berry
   Swabia (Austria): garrison — screening force holds the works
   Munich (Austria): garrison — substantial force holds the works
   Paget: small force near London
   London (Britain): garrison — substantial force holds the works
   Milan (Austria): garrison — small force holds the works [4 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
map: unchanged (52 labels)
```

```
#0245  look  ->  ok
  (a fresh frame)
view: <run>\frames\0245_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2662 of 2662 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Paget: small force near London
   London (Britain): garrison — substantial force holds the works
   Milan (Austria): garrison — small force holds the works [4 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
map: unchanged (52 labels)
```

```
#0246  click Reject Offer  ->  ok
  (clicked at (2056, 727))
view: <run>\frames\0246_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 38 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Blockade — Britain closes our ports @(3393,64)]  [icon: Oudinot arrived @(3435,64)]  [icon: Ney arrived (x4) @(3477,64)]  [icon: Davout arrived (x4) @(3519,64)]  [icon: Murat arrived (x2) @(3561,64)]  [+29]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Berry
   -6 →
   T:15
   controls: [THIRD COALITION  ▸]  [War for Berry]
── BottomLeftUI (layer 0) [scrolled 2730 of 2730 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,741 (+599 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: reject settlement offer
   Settlement offer rejected.
map: unchanged (52 labels)
```

```
#0247  type what if Davout attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0247_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout stands at Franche-Comte, beyond reach of Archduke Charles at Berry this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Massena and Oudinot stand within reach.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2840 of 2840 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,741 (+599 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Davout attacks Archduke Charles
   Davout stands at Franche-Comte, beyond reach of Archduke Charles at Berry this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Massena and Oudinot stand within reach.
map: unchanged (52 labels)
```

```
#0248  type land Oudinot in Ulster  ->  ok
  (typed and Enter)
view: <run>\frames\0248_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
reply: ok The expedition is drawn up, Sire: Oudinot with 5,000 men, Normandy to Ulster. The transports slip past unseen 69 times in 100 (Britain watches at 97 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. If she is intercepted she meets Britain's 112 effective against our 24 — a decisive defeat is the likely result: about half of every pooled fleet (France 36→~16, Holland 5→~2) is lost; Britain's side loses ~2%. What moves the odds: a won diversion first (34 in 100) → 95 · 10 more sail (4,000g) → 72. Sail? (yes / no)
── ClarificationPopup (layer 102) ──
   OUDINOT ASKS:
   "The expedition is drawn up, Sire: Oudinot with 5,000 men, Normandy to Ulster. The transports slip past unseen 69 times in 100 (Britain watches at 97 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. If she is intercepted she meets Britain's 112 effective against our 24 — a decisive defeat is t …
   controls: [Sail for Ulster]  [Stand down]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 38 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2906 of 2906 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,741 (+599 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► land Oudinot in Ulster
   Oudinot requests clarification...
map: unchanged (52 labels)
```

```
#0249  click Sail for Ulster  ->  ok
  (clicked at (1829, 598))
view: <run>\frames\0249_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Oudinot has taken Ulster
   Ireland needs Munster too — it lies a march from Ulster; carve at a table while the war with Britain runs. / How shall your forces treat the conquered territory?
   controls: [PLUNDER (+600 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 40 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2511 of 2512 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,741 (+487 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [partial]
   Milan garrison — Milan — garrison — small force [stale - T12]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   [!] Bernadotte's Counter-Punch opportunity has expired! (Must use immediately after defending)
   Supply cost you 1,411 men, at Franche-Comte.
   Munich's garrison regrows — substantial force.
   Switzerland loyalty 88 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier notes that Soult no longer presses the matter — his quarrel with Ney has cooled.
   Soult's resentment of Ney has cooled with time.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   DIPLOMATIC EVENTS
   THE LANDING: Dumonceau has put 4,550 men ashore at Ulster.
   Galicia passes from Britain to Spain.
   Austria, for Austria and Russia, has offered terms to settle the War for Berry — Britain + Austria + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on. Unheld homeland returns to its crown: Asturias.
   THE CAMP: France has massed 43,567 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   The court of Austria hardens over Redeem Italy — prepared now to go as far as war.
   The court of Britain hardens over The Paymaster of Coalitions — prepared now to go as far as war.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Austria — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 29 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Saxony may be ready to discuss improved relations. The diplomatic winds favor us.
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Berry) — the homeland — 24 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Austria (War for Berry) — the homeland — 24 of 28 provinces held (ticking: +18, +1/turn)  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War for Berry) — the homeland — 24 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 38/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Franche-Comte): 12,982 troops, morale 85, neutral stance
   Davout (Franche-Comte): 16,002 troops, morale 90, neutral stance
   Soult (Flanders): 28,567 troops, morale 100, neutral stance
   Lannes (Franche-Comte): 5,367 troops, morale 1, neutral stance
   Bernadotte (Franche-Comte): 11,373 troops, morale 95, neutral stance
   Massena (Paris): 6,327 troops, morale 0, neutral stance, retreating
   Napoleon (Flanders): 10,000 troops, morale 85, neutral stance
   Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
   Oudinot (Normandy): 5,000 troops, morale 100, neutral stance
   PRISONERS:
   Murat: held by Austria at Vienna since T14.
   CONFIRMED INTELLIGENCE:
   Wellesley (Britain): 12,773 troops at Leon, defensive stance, morale 82
   Brunswick (Prussia): 50,164 troops at Oldenburg, defensive stance, morale 86
   RECENT REPORTS:
   Archduke Charles, Cuesta: substantial force near Berry
   Swabia (Austria): garrison — screening force holds the works
   Munich (Austria): garrison — substantial force holds the works
   Paget: small force near London
   London (Britain): garrison — substantial force holds the works
   Milan (Austria): garrison — small force holds the works [4 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   Directing Talleyrand: reject settlement offer
   Settlement offer rejected.
   ► what if Davout attacks Archduke Charles
   Davout stands at Franche-Comte, beyond reach of Archduke Charles at Berry this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Massena and Oudinot stand within reach.
   ► land Oudinot in Ulster
   Oudinot requests clarification...
   > land Oudinot in Ulster confirmed
   THE LANDING: Oudinot slips past the British patrols and puts 5,000 men ashore at Ulster (odds were 69 in 100).
   Your forces have taken Ulster. Ireland needs Munster too — it lies a march from Ulster; carve at a table while the war with Britain runs. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [2/4 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1917,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1423,292)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  36(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,528)  Archduke Charles(1517,501)  ?(1545,528)  Cuesta(1522,443)  Wellesley(1273,648)  Dumonceau(1310,223)  Oudinot(1335,197)  Ney +3(1813,487)  Brunswick(1700,300)  Massena(1595,442)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Paget(1490,328)  ?(1869,762)  ?(1859,519)  ?(1901,591)  25k(1619,503)  12k(1538,470)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1490,414)  ?(1910,645)
```

```
#0250  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0250_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
── CaptureChoiceDialog (layer 105): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2511 of 2512 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   THE LANDING: Oudinot slips past the British patrols and puts 5,000 men ashore at Ulster (odds were 69 in 100).
   Your forces have taken Ulster. Ireland needs Munster too — it lies a march from Ulster; carve at a table while the war with Britain runs. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [2/4 actions remaining]
   Your forces await orders: Plunder or Secure?
map: unchanged (52 labels)
```

```
#0251  click SECURE  ->  ok
  (clicked at (1995, 601))
view: <run>\frames\0251_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 40 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Blockade — Britain closes our ports @(3393,64)]  [icon: Oudinot arrived @(3435,64)]  [icon: Ney arrived (x4) @(3477,64)]  [icon: Davout arrived (x4) @(3519,64)]  [icon: Murat arrived (x2) @(3561,64)]  [+29]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Berry
   +1 ↑
   T:15
   controls: [THIRD COALITION  ▸]  [War for Berry]
── BottomLeftUI (layer 0) [scrolled 2622 of 2622 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,741 (+487 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Oudinot secures Ulster. Stability set to 25. Order is maintained. 1 building damaged. Ireland needs Munster too — it lies a march from Ulster; carve at a table while the war with Britain runs.
map: unchanged (52 labels)
```

```
#0252  type Dumonceau, attack Munster  ->  ok
  (typed and Enter)
view: <run>\frames\0252_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Munster lies open, but Dumonceau's 4,550 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto. March him in with 'move to Munster' to stand there, or bring 5,000.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2732 of 2732 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,741 (+487 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Dumonceau, attack Munster
   Munster lies open, but Dumonceau's 4,550 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto. March him in with 'move to Munster' to stand there, or bring 5,000.
map: unchanged (52 labels)
```

```
#0253  type Oudinot, attack Munster  ->  ok
  (typed and Enter)
view: <run>\frames\0253_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok Oudinot marches from Ulster into Munster unopposed! (50 lost to march) Captured: Britain → France
Your forces have taken Munster. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Oudinot has taken Munster
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+600 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 42 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2424 of 2424 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Oudinot, attack Munster
   ⚑ Oudinot marches from Ulster into Munster unopposed! (50 lost to march) Captured: Britain → France
   Your forces have taken Munster. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/4 actions remaining]
   Your forces await orders: Plunder or Secure?
map: unchanged (52 labels)
```

```
#0254  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0254_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 42 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Blockade — Britain closes our ports @(3393,64)]  [icon: Oudinot arrived @(3435,64)]  [icon: Ney arrived (x4) @(3477,64)]  [icon: Davout arrived (x4) @(3519,64)]  [icon: Murat arrived (x2) @(3561,64)]  [+29]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +8 ↑
   T:15
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 2449 of 2449 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   DIPLOMATIC EVENTS
   THE LANDING: Dumonceau has put 4,550 men ashore at Ulster.
   Galicia passes from Britain to Spain.
   Austria, for Austria and Russia, has offered terms to settle the War for Berry — Britain + Austria + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on. Unheld homeland returns to its crown: Asturias.
   THE CAMP: France has massed 43,567 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   The court of Austria hardens over Redeem Italy — prepared now to go as far as war.
   The court of Britain hardens over The Paymaster of Coalitions — prepared now to go as far as war.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Austria — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 29 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Saxony may be ready to discuss improved relations. The diplomatic winds favor us.
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Berry) — the homeland — 24 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Austria (War for Berry) — the homeland — 24 of 28 provinces held (ticking: +18, +1/turn)  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War for Berry) — the homeland — 24 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 38/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Franche-Comte): 12,982 troops, morale 85, neutral stance
   Davout (Franche-Comte): 16,002 troops, morale 90, neutral stance
   Soult (Flanders): 28,567 troops, morale 100, neutral stance
   Lannes (Franche-Comte): 5,367 troops, morale 1, neutral stance
   Bernadotte (Franche-Comte): 11,373 troops, morale 95, neutral stance
   Massena (Paris): 6,327 troops, morale 0, neutral stance, retreating
   Napoleon (Flanders): 10,000 troops, morale 85, neutral stance
   Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
   Oudinot (Normandy): 5,000 troops, morale 100, neutral stance
   PRISONERS:
   Murat: held by Austria at Vienna since T14.
   CONFIRMED INTELLIGENCE:
   Wellesley (Britain): 12,773 troops at Leon, defensive stance, morale 82
   Brunswick (Prussia): 50,164 troops at Oldenburg, defensive stance, morale 86
   RECENT REPORTS:
   Archduke Charles, Cuesta: substantial force near Berry
   Swabia (Austria): garrison — screening force holds the works
   Munich (Austria): garrison — substantial force holds the works
   Paget: small force near London
   London (Britain): garrison — substantial force holds the works
   Milan (Austria): garrison — small force holds the works [4 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   Directing Talleyrand: reject settlement offer
   Settlement offer rejected.
   ► what if Davout attacks Archduke Charles
   Davout stands at Franche-Comte, beyond reach of Archduke Charles at Berry this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Massena and Oudinot stand within reach.
   ► land Oudinot in Ulster
   Oudinot requests clarification...
   > land Oudinot in Ulster confirmed
   THE LANDING: Oudinot slips past the British patrols and puts 5,000 men ashore at Ulster (odds were 69 in 100).
   Your forces have taken Ulster. Ireland needs Munster too — it lies a march from Ulster; carve at a table while the war with Britain runs. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [2/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Oudinot secures Ulster. Stability set to 25. Order is maintained. 1 building damaged. Ireland needs Munster too — it lies a march from Ulster; carve at a table while the war with Britain runs.
   ► Dumonceau, attack Munster
   Munster lies open, but Dumonceau's 4,550 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto. March him in with 'move to Munster' to stand there, or bring 5,000.
   ► Oudinot, attack Munster
   ⚑ Oudinot marches from Ulster into Munster unopposed! (50 lost to march) Captured: Britain → France
   Your forces have taken Munster. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Oudinot secures Munster. Stability set to 25. Order is maintained. 1 building damaged.
map: unchanged (52 labels)
```

```
#0255  type what can I do about Ireland  ->  ok
  (typed and Enter)
view: <run>\frames\0255_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."

What I CAN do today:
  Massena, attack Archduke Charles
  Ney, march to Nivernais
  recruit infantry in Paris — 518g for 10,000 men under Massena
  build supply depot in Paris — 300g
Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.

For any matter of state, press F1 for the Cabinet.
Type 'help' for the full command reference.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2227 of 2227 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what can I do about Ireland
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Massena, attack Archduke Charles
   Ney, march to Nivernais
   recruit infantry in Paris — 518g for 10,000 men under Massena
   build supply depot in Paris — 300g
   Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (52 labels)
```

```
#0256  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0256_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 29 titled provinces — 45 are needed (16 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2227 of 2227 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   build supply depot in Paris — 300g
   Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (52 labels)
```

```
#0257  click Formable Nations  ->  ok
  (clicked at (1825, 612))
view: <run>\frames\0257_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 222 px] ──
   THE CABINET — FORMABLE NATIONS
   DP: 7
   "The map of Europe is not finished, Sire. These states could yet exist — each names what its existence would require."
   States not yet on the map, Sire; each row names what its birth requires. One carved at the table is born your client — it pays tribute and marches when you call; one that forms by conquest rises free.
   Duchy of Warsaw — client state at the settlement table /     • at war with Prussia /     • Posen held at the settlement table (currently Prussia-held)
   Duchy of Normandy — client state at the settlement table /     • carved from France's own provinces — a clause only a victorious enemy may put before you
   Roman Republic — client state at the settlement table /     • at war with Papal States /     • Rome held at the settlement table (currently Papal States-held) /     • a decisive victory over Papal States — erasing a state entirely needs war score 90 (currently 0)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2227 of 2227 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   build supply depot in Paris — 300g
   Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (52 labels)
```

```
#0258  scroll 1850 500 down 6  ->  ok
  (scrolled down 6 at (1850, 500))
view: <run>\frames\0258_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 184 of 230 px] ──
   THE CABINET — FORMABLE NATIONS
   DP: 7
   "The map of Europe is not finished, Sire. These states could yet exist — each names what its existence would require."
   Duchy of Normandy — client state at the settlement table /     • carved from France's own provinces — a clause only a victorious enemy may put before you
   Roman Republic — client state at the settlement table /     • at war with Papal States /     • Rome held at the settlement table (currently Papal States-held) /     • a decisive victory over Papal States — erasing a state entirely needs war score 90 (currently 0)
   Ireland — client state at the settlement table /     ✓ at war with Britain /     ✓ Ulster held at the settlement table /     ✓ Munster held at the settlement table
   United Netherlands — forms by conquest (0 of 1 province held) /     • forms when a free Holland holds its claimed province /     • currently a vassal of France
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [↳ Open negotiations — Britain]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2227 of 2227 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   build supply depot in Paris — 300g
   Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (52 labels)
```

```
#0259  click Open negotiations  ->  ok
  (clicked at (1825, 624))
view: <run>\frames\0259_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 442 px, 0 of 312 px] ──
   THE CABINET — Britain
   DP: 7
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War for Munster   Relation: -75 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Sire, the field reads +11 and no road carries. Propose Peace comes nearest at 42 of 50; deep-seated hostility is the weight (-10). A payment of 775 gold to Britain  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Uncertain — a counter is likely]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Open Settlement with Britain alone  —  opens with 775 gold to Britain staged — the sum that carries her]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Uncertain — a counter is likely]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2227 of 2227 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   build supply depot in Paris — 300g
   Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (52 labels)
```

```
#0260  click Open Settlement with Britain alone  ->  ok
  (clicked at (1825, 550))
view: <run>\frames\0260_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 200 px] ──
   Settlement of the War for Munster — the table with Britain — every court consents; submit it for review / the War for Munster — the table with Britain - Separate settlement / Covered enemies: Britain / Still at war: Austria, Russia / Will carry as drafted — every court at or above 50. / Treasury 6,741 gold: committed 775 / reserve 500 / remaining 5,466 / Sire, this settlement of the War for Munste …
   The table /   * Britain ▸ - Will sign (50/50) Conceded: 775g /       Castlereagh signals that Britain will sign the settlement of the War for Munster — the table with Britain. /       Conceded · France pays 775 gold (yours)  [-][+]  Remove /       + Add demand / This peace carries.
   Britain:
   Coverage:
   Sire, the settlement of the War for Munster — the table with Britain stands ready for ratification. Acceptance reads as Will sign; what weighs heaviest: no single dominant pressure. /  / What the treaty titles /   * Status quo: Munster and Ulster stay ours by the treaty — titled. /  / This peace ends the war and closes the Ireland carve — erect it at the table first. /  / Allies and Standing /   * …
   controls: <Britain ▸>  <Remove>  <+ Add demand>  [Demand more of Britain]  [Ease Britain]  [Separate peace with Britain — alone: 53 (Favorable)]  [Bring Austria to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 42 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2795 of 2795 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose common peace with Britain  (sent from the diplomacy screen — typed, this line would open the whole table without the sum staged)
map: unchanged (52 labels)
```

```
#0261  click + Add demand  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0261_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 113 px, 0 of 200 px] ──
   Settlement of the War for Munster — the table with Britain — every court consents; submit it for review / the War for Munster — the table with Britain - Separate settlement / Covered enemies: Britain / Still at war: Austria, Russia / Will carry as drafted — every court at or above 50. / Treasury 6,741 gold: committed 775 / reserve 500 / remaining 5,466 / Sire, this settlement of the War for Munste …
   The table /   * Britain ▸ - Will sign (50/50) Conceded: 775g /       Castlereagh signals that Britain will sign the settlement of the War for Munster — the table with Britain. /       Conceded · France pays 775 gold (yours)  [-][+]  Remove /       − Add demand /         Demands of Britain /           Take Highlands from Britain /             — Highlands sits beside what we already hold; Britain wo …
   Britain:
   Coverage:
   Sire, the settlement of the War for Munster — the table with Britain stands ready for ratification. Acceptance reads as Will sign; what weighs heaviest: no single dominant pressure. /  / What the treaty titles /   * Status quo: Munster and Ulster stay ours by the treaty — titled. /  / This peace ends the war and closes the Ireland carve — erect it at the table first. /  / Allies and Standing /   * …
   controls: <Britain ▸>  <Remove>  <− Add demand>  <Take Highlands from Britain>  <Demand 300 gold from Britain>  <Demand 100 gold a turn from Britain for 3 turns>  <Force Britain into alliance>  <Erect Ireland from Britain's lands>  <▸ Offers to Britain (3)>  [Demand more of Britain]  [Ease Britain]  [Separate peace with Britain — alone: 53 (Favorable)]  [Bring Austria to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2795 of 2795 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
   ► propose common peace with Britain  (sent from the diplomacy screen — typed, this line would open the whole table without the sum staged)
map: unchanged (52 labels)
```

```
#0262  click Erect Ireland  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0262_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px] ──
   This draft will not carry as it stands. / the War for Munster — the table with Britain - Separate settlement / Covered enemies: Britain / Still at war: Austria, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Britain 17/50. / Treasury 6,741 gold: committed 775 / reserve 500 / remaining 5,466 / Sire, this settlement of the War for Munster — the table with Britain seats  …
   The table /   * Britain ▸ - Holding out (17/50) Demanded: Ireland carved out; Conceded: 775g /       Blocker: Term harshness /       Britain Will sign → Holding out /       Castlereagh declines for Britain: the terms weigh heavier than their defeat, and arithmetic does not sign papers it cannot balance. He adds that London has read the bulletins from Franche-Comte — Marshal Bernadotte's laurels do …
   Britain:
   Coverage:
   Sire, the settlement of the War for Munster — the table with Britain cannot be ratified now: the terms weigh heavier than their defeat. Revise terms or stand down before pressing further. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Britain 17/50). With Britain alone the table reads 17 of 50 and does not carry. It costs 3 diplomatic points; y …
   controls: <Britain ▸>  <Remove>  <Remove>  <+ Add demand>  [Demand more of Britain]  [Ease Britain]  [Bring Austria to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2824 of 2824 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement demand add
map: unchanged (52 labels)
```

```
#0263  look  ->  ok
  (a fresh frame)
view: <run>\frames\0263_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2824 of 2824 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
   ► propose common peace with Britain  (sent from the diplomacy screen — typed, this line would open the whole table without the sum staged)
   Directing Talleyrand: settlement demand add
map: unchanged (52 labels)
```

```
#0264  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0264_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 332 px] ──
   This draft will not carry as it stands. / the War for Munster — the table with Britain - Separate settlement / Covered enemies: Britain / Still at war: Austria, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Britain 21/50. / Treasury 6,741 gold: committed 875 / reserve 500 / remaining 5,366 / Sire, this settlement of the War for Munster — the table with Britain seats  …
   The table /   * Britain ▸ - Holding out (21/50) Demanded: Ireland carved out; Conceded: 875g /       Blocker: Term harshness /       Castlereagh declines for Britain: the terms weigh heavier than their defeat, and arithmetic does not sign papers it cannot balance. He adds that London has read the bulletins from Franche-Comte — Marshal Bernadotte's laurels do not alter the arithmetic. /       Conce …
   Britain:
   Coverage:
   Sire, the settlement of the War for Munster — the table with Britain cannot be ratified now: the terms weigh heavier than their defeat. Revise terms or stand down before pressing further. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Britain 21/50). With Britain alone the table reads 21 of 50 and does not carry. It costs 3 diplomatic points; y …
   controls: <Britain ▸>  <Remove>  <Remove>  <+ Add demand>  [Demand more of Britain]  [Ease Britain]  [Bring Austria to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2846 of 2846 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0265  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0265_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 332 px] ──
   This draft will not carry as it stands. / the War for Munster — the table with Britain - Separate settlement / Covered enemies: Britain / Still at war: Austria, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Britain 25/50. / Treasury 6,741 gold: committed 975 / reserve 500 / remaining 5,266 / Sire, this settlement of the War for Munster — the table with Britain seats  …
   The table /   * Britain ▸ - Holding out (25/50) Demanded: Ireland carved out; Conceded: 975g /       Blocker: Term harshness /       Castlereagh declines for Britain: the terms weigh heavier than their defeat, and arithmetic does not sign papers it cannot balance. He adds that London has read the bulletins from Franche-Comte — Marshal Bernadotte's laurels do not alter the arithmetic. /       Conce …
   Britain:
   Coverage:
   Sire, the settlement of the War for Munster — the table with Britain cannot be ratified now: the terms weigh heavier than their defeat. Revise terms or stand down before pressing further. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Britain 25/50). With Britain alone the table reads 25 of 50 and does not carry. It costs 3 diplomatic points; y …
   controls: <Britain ▸>  <Remove>  <Remove>  <+ Add demand>  [Demand more of Britain]  [Ease Britain]  [Bring Austria to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2868 of 2868 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0266  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0266_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px] ──
   This draft will not carry as it stands. / the War for Munster — the table with Britain - Separate settlement / Covered enemies: Britain / Still at war: Austria, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Britain 26/50. / Treasury 6,741 gold: committed 1,000 / reserve 500 / remaining 5,241 / Sire, this settlement of the War for Munster — the table with Britain seat …
   The table /   * Britain ▸ - Holding out (26/50) Demanded: Ireland carved out; Conceded: 1000g /       Blocker: Term harshness /       Castlereagh declines for Britain: the terms weigh heavier than their defeat, and arithmetic does not sign papers it cannot balance. He adds that London has read the bulletins from Franche-Comte — Marshal Bernadotte's laurels do not alter the arithmetic. /       Conc …
   Britain:
   Coverage:
   Sire, the settlement of the War for Munster — the table with Britain cannot be ratified now: the terms weigh heavier than their defeat. Revise terms or stand down before pressing further. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Britain 26/50). With Britain alone the table reads 26 of 50 and does not carry. It costs 3 diplomatic points; y …
   controls: <Britain ▸>  <Remove>  <Remove>  <+ Add demand>  [Demand more of Britain]  [Ease Britain]  [Bring Austria to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2890 of 2890 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0267  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0267_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2912 of 2912 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0268  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0268_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2934 of 2934 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0269  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0269_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2957 of 2957 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0270  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0270_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2979 of 2979 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0271  click Ease Britain  ->  ok
  (clicked at (1630, 639))
view: <run>\frames\0271_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0272  look  ->  ok
  (a fresh frame)
view: <run>\frames\0272_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0273  click_at 1758 530  ->  ok
  (clicked at (1758, 530) on PerCourtTable 'The table
  * Britain ▸ - Holding out (2' (RichTextLabel, layer 110))
view: <run>\frames\0273_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0274  click_at 1758 530  ->  ok
  (clicked at (1758, 530) on PerCourtTable 'The table
  * Britain ▸ - Holding out (2' (RichTextLabel, layer 110))
view: <run>\frames\0274_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0275  click_at 1758 530  ->  ok
  (clicked at (1758, 530) on PerCourtTable 'The table
  * Britain ▸ - Holding out (2' (RichTextLabel, layer 110))
view: <run>\frames\0275_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0276  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0276_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3023 of 3023 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0277  click Ease Britain  ->  ok
  (clicked at (1630, 639))
view: <run>\frames\0277_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3045 of 3045 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0278  look  ->  ok
  (a fresh frame)
view: <run>\frames\0278_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3045 of 3045 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0279  click_at 1772 531  ->  ok
  (clicked at (1772, 531) on PerCourtTable 'The table
  * Britain ▸ - Holding out (2' (RichTextLabel, layer 110))
view: <run>\frames\0279_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 332 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3045 of 3045 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0280  click Back Out  ->  ok
  (clicked at (2250, 969))
view: <run>\frames\0280_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 42 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 36 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Blockade — Britain closes our ports @(3393,64)]  [icon: Oudinot arrived @(3435,64)]  [icon: Ney arrived (x4) @(3477,64)]  [icon: Davout arrived (x4) @(3519,64)]  [icon: Murat arrived (x2) @(3561,64)]  [+29]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +8 ↑
   T:15
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 3111 of 3111 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,741 (+420 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (52 labels)
```

```
#0281  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0281_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 37 sail — readiness 58 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — the blockade lifts as the enemy squadrons come home to the camp; readiness then recovers +5/turn to 75. 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 42 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 37 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Blockade — Britain closes our ports @(3393,64)]  [icon: Oudinot arrived @(3435,64)]  [icon: Ney arrived (x4) @(3477,64)]  [icon: Davout arrived (x4) @(3519,64)]  [icon: Murat arrived (x2) @(3561,64)]  [+29]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2693 of 2693 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   1/2
   Gold:
   6,341 (+464 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   War Purpose: Defense vs Russia (War for Berry) — the homeland — 24 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 38/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Franche-Comte): 12,982 troops, morale 85, neutral stance
   Davout (Franche-Comte): 16,002 troops, morale 90, neutral stance
   Soult (Flanders): 28,567 troops, morale 100, neutral stance
   Lannes (Franche-Comte): 5,367 troops, morale 1, neutral stance
   Bernadotte (Franche-Comte): 11,373 troops, morale 95, neutral stance
   Massena (Paris): 6,327 troops, morale 0, neutral stance, retreating
   Napoleon (Flanders): 10,000 troops, morale 85, neutral stance
   Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
   Oudinot (Normandy): 5,000 troops, morale 100, neutral stance
   PRISONERS:
   Murat: held by Austria at Vienna since T14.
   CONFIRMED INTELLIGENCE:
   Wellesley (Britain): 12,773 troops at Leon, defensive stance, morale 82
   Brunswick (Prussia): 50,164 troops at Oldenburg, defensive stance, morale 86
   RECENT REPORTS:
   Archduke Charles, Cuesta: substantial force near Berry
   Swabia (Austria): garrison — screening force holds the works
   Munich (Austria): garrison — substantial force holds the works
   Paget: small force near London
   London (Britain): garrison — substantial force holds the works
   Milan (Austria): garrison — small force holds the works [4 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   Directing Talleyrand: reject settlement offer
   Settlement offer rejected.
   ► what if Davout attacks Archduke Charles
   Davout stands at Franche-Comte, beyond reach of Archduke Charles at Berry this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet. Of ours, Massena and Oudinot stand within reach.
   ► land Oudinot in Ulster
   Oudinot requests clarification...
   > land Oudinot in Ulster confirmed
   THE LANDING: Oudinot slips past the British patrols and puts 5,000 men ashore at Ulster (odds were 69 in 100).
   Your forces have taken Ulster. Ireland needs Munster too — it lies a march from Ulster; carve at a table while the war with Britain runs. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [2/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Oudinot secures Ulster. Stability set to 25. Order is maintained. 1 building damaged. Ireland needs Munster too — it lies a march from Ulster; carve at a table while the war with Britain runs.
   ► Dumonceau, attack Munster
   Munster lies open, but Dumonceau's 4,550 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto. March him in with 'move to Munster' to stand there, or bring 5,000.
   ► Oudinot, attack Munster
   ⚑ Oudinot marches from Ulster into Munster unopposed! (50 lost to march) Captured: Britain → France
   Your forces have taken Munster. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Oudinot secures Munster. Stability set to 25. Order is maintained. 1 building damaged.
   ► what can I do about Ireland
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Massena, attack Archduke Charles
   Ney, march to Nivernais
   recruit infantry in Paris — 518g for 10,000 men under Massena
   build supply depot in Paris — 300g
   Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
   ► propose common peace with Britain  (sent from the diplomacy screen — typed, this line would open the whole table without the sum staged)
   Directing Talleyrand: settlement demand add
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 37 sail — readiness 58 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — the blockade lifts as the enemy squadrons come home to the camp; readiness then recovers +5/turn to 75. 0 more keels possible this turn.
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1917,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1441,290)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  37(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,528)  Archduke Charles(1517,501)  ?(1545,528)  Cuesta(1522,443)  Wellesley(1273,648)  Dumonceau(1322,223)  Oudinot(1303,280)  Ney +3(1813,487)  Brunswick(1700,300)  Massena(1595,442)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Paget(1490,328)  ?(1869,762)  ?(1859,519)  ?(1901,591)  25k(1619,503)  12k(1538,470)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1490,414)  ?(1910,645)
```

```
#0282  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0282_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2759 of 2759 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/4
   Admin:
   1/2
   Gold:
   6,341 (+464 next turn)
   Inf:
   94,660
   Cav:
   30,000
   Art:
   19,000
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Massena's corps stands below 40% morale beside Archduke Charles (~27,500, Berry) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (52 labels)
```

```
#0283  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0283_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!

Income: 1917g | Occupation: -104g | Charges of Empire: -712g | Admiralty: -74g | Materiel: -460g | Upkeep: -704g | Other: +562g | Net: +425g | Spent: 400g | Treasury: 6,766g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 223 px] ──
   ENEMY PHASE - Turn 16
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     Battle of Paris /     Archduke Charles: 108 casualties, 24,552 remaining /     Massena: 3,202 casualties, 3,125 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) /     Massena forced to retreat! /     ⚔ View the field /     --- Berthier's Report --- /     Attack: Archduke Charles (Defens …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 39 / 100
   Turn 17 — Late May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 37 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3246 of 3246 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,766 (+747 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   Your unratified settlement draft with Britain (3 clauses) was set aside at turn's end.
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 1917g | Occupation: -104g | Charges of Empire: -712g | Admiralty: -74g | Materiel: -460g | Other: +562g | Upkeep: -704g | Net: +425g | Spent: 400g
   Treasury: 6,766g
   Actions refreshed: 4/4
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Crowded at Franche-Comte: Ney loses 389 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Davout loses 480 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 161 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Bernadotte loses 341 troops to the press of 4 corps on one province's roads
   Garrison at Munich reinforced: 20,000 -> 22,000
   Switzerland loyalty 86 (-2): satellite drift, the lord's defeats
   Britain subsidizes Russia with 300 gold.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1913,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1441,290)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  37(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,528)  Archduke Charles(1525,501)  ?(1859,469)  Bennigsen(1859,430)  Dumonceau(1322,223)  Oudinot(1303,280)  Ney +3(1813,487)  Brunswick(1700,300)  Massena(1595,442)  ?(1658,578)  Archduke John(1641,539)  Soult(1672,361)  Napoleon(1792,322)  ?(1490,366)  Paget(1490,328)  ?(1859,519)  ?(1901,591)  25k(1627,503)  6k(1533,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1490,417)
```

```
#0284  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0284_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   MASSENA REPORTS
   "Massena is cornered at Paris with 3,125 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 39 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 37 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Massena is cornered @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Oudinot arrived @(3435,64)]  [icon: Ney arrived (x4) @(3477,64)]  [icon: Davout arrived (x4) @(3519,64)]  [icon: Murat arrived (x2) @(3561,64)]  [+29]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Munster
   +2 →
   T:16
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,766 (+747 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   --- Strategic Order Updates ---
   Massena: Massena is cornered at Paris with 3,125 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 17
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. Archduke John's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Massena was mauled at Paris: half of his corps — 3,202 men — lost in a single action.
   • Sire — Normandy holds. Archduke Charles left 3,703 men before the works; 6,000 of ours are still under arms.
   • Sire — the levy has stood open 4 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
   SITUATION
   France holds 25 regions. Treasury: 6,766g (+885 by the accounts)
   The courts at war hold 36 regions. Estimated enemy strength: 84% of French forces (an estimate — 4 of 5 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 28,567 — Awaiting orders.
   - Davout — Franche-Comte — 15,522 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Ney — Franche-Comte — 12,593 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Bernadotte — Franche-Comte — 11,032 — Awaiting orders. Trust:40
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Franche-Comte — 5,206 — 3 turns idle. Morale:1%
   ⚠ Morale failing (1) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Munster — 4,950 — Awaiting orders.
   - Dumonceau — Ulster — 4,550 — Awaiting orders.
   ? Massena — Paris — 3,125 — Hunted by Archduke Charles across 2 frontiers — stands at Paris with 3,125 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Brunswick — Oldenburg — 50,164 [confirmed]
   Archduke Charles — Berry — substantial force [partial]
   Archduke John — Provence — substantial force [partial]
   Paget — London — small force [partial]
   Bennigsen — Swabia — screening force [partial]
   Blake — Leon — screening force [last known - T15]
   Wellesley — Leon — small force [last known - T16]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Supply cost you 1,371 men, at Franche-Comte.
   Munich's garrison regrows — substantial force.
   Switzerland loyalty 86 (-2): satellite drift, the lord's defeats
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   DIPLOMATIC EVENTS
   THE LANDING: Oudinot has put 5,000 men ashore at Ulster.
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the Highlands–Ulster crossing is shut — Britain commands the water.
   REVANCHE: Britain will not forgive France the loss of Ulster and 1 more province. A new design hardens in their court.
   The court of Britain takes up a new design: Revanche.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 28 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 23 of 28 provinces held  |  Settlement (this pair): White Peace (+9)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 23 of 28 provinces held (ticking: +23, +1/turn)  |  Settlement (this pair): White Peace (-7)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 23 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 39/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Massena awaits your orders!
map: unchanged (51 labels)
```

```
#0285  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0285_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Massena awaits your orders!
map: unchanged (51 labels)
```

```
#0286  type is Paris safe  ->  ERROR: the command line is not taking orders now (it is disabled)
view: <run>\frames\0286_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Massena awaits your orders!
map: unchanged (51 labels)
```

```
#0287  click Attempt a Breakout  ->  ok
  (clicked at (1971, 584))
view: <run>\frames\0287_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   6,327 → 3,125
   24,660 → 24,552
   BATTLE OF PARIS
   click anywhere to skip ▸
   PARIS · TURN 16
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 39 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 37 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3351,64)]  [icon: Oudinot arrived @(3393,64)]  [icon: Ney arrived (x4) @(3435,64)]  [icon: Davout arrived (x4) @(3477,64)]  [icon: Murat arrived (x2) @(3519,64)]  [icon: Bernadotte arrived (x2) @(3561,64)]  [+28]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2070 of 2070 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,766 (+747 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Massena: attempt breakout
   Massena cuts his way out! Massena falls back on Artois, his corps disordered but in the field.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1913,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1441,290)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  37(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Archduke Charles(1525,444)  Massena(1616,379)  ?(1859,469)  Bennigsen(1859,430)  Dumonceau(1322,223)  Oudinot(1303,280)  Ney +3(1813,487)  Brunswick(1700,300)  ?(1658,578)  Archduke John(1658,521)  Soult(1682,379)  Napoleon(1792,322)  ?(1490,366)  Paget(1490,328)  ?(1859,519)  ?(1901,591)  25k(1569,503)  6k(1539,472)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1490,417)
```

```
#0288  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0288_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2070 of 2070 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,766 (+747 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Massena awaits your orders!
   > Massena: attempt breakout
   Massena cuts his way out! Massena falls back on Artois, his corps disordered but in the field.
map: unchanged (51 labels)
```

```
#0289  type is Paris safe  ->  ok
  (typed and Enter)
view: <run>\frames\0289_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Paris is ours, Sire, held by a garrison of 25,000. Threats we can see: Archduke Charles of Austria is at Berry, one march away (substantial force); Paget of Britain is at London, two marches off (small force). It is held, but threatened.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2181 of 2181 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,766 (+747 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► is Paris safe
   Paris is ours, Sire, held by a garrison of 25,000. Threats we can see: Archduke Charles of Austria is at Berry, one march away (substantial force); Paget of Britain is at London, two marches off (small force). It is held, but threatened.
map: unchanged (51 labels)
```

```
#0290  type Soult, march to Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0290_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult begins march to Paris. Route: Westphalia → Artois → Paris. Moves to Westphalia.
Westphalia feeds 15,000; the 27,792 men standing there would lose ~355 a turn to short supply.
Westphalia lies outside the camp — this takes 27,792 men out of it; no turn counts toward staging while they stand there.
Westphalia is Prussia's soil — the corps standing there are fed by contract, about −324g more a turn. "Soult, march to Paris." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2379 of 2379 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   6,766 (+431 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, march to Paris
   Soult begins march to Paris. Route: Westphalia → Artois → Paris. Moves to Westphalia.
   Westphalia feeds 15,000; the 27,792 men standing there would lose ~355 a turn to short supply.
   Westphalia lies outside the camp — this takes 27,792 men out of it; no turn counts toward staging while they stand there.
   Westphalia is Prussia's soil — the corps standing there are fed by contract, about −324g more a turn. "Soult, march to Paris." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map: unchanged (51 labels)
```

```
#0291  type Napoleon, march to Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0291_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon begins march to Paris. Route: Westphalia → Artois → Paris. Moves to Westphalia.
Westphalia feeds 15,000; the 37,692 men standing there would lose ~1,231 a turn to short supply.
Westphalia is Prussia's soil — the corps standing there are fed by contract, about −108g more a turn. (1 AP — the Emperor commands in his own name.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1873 of 1873 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,766 (+331 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Bernadotte — Franche-Comte — 11,032 — Awaiting orders. Trust:40
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Lannes — Franche-Comte — 5,206 — 3 turns idle. Morale:1%
   ⚠ Morale failing (1) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Munster — 4,950 — Awaiting orders.
   - Dumonceau — Ulster — 4,550 — Awaiting orders.
   ? Massena — Paris — 3,125 — Hunted by Archduke Charles across 2 frontiers — stands at Paris with 3,125 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Brunswick — Oldenburg — 50,164 [confirmed]
   Archduke Charles — Berry — substantial force [partial]
   Archduke John — Provence — substantial force [partial]
   Paget — London — small force [partial]
   Bennigsen — Swabia — screening force [partial]
   Blake — Leon — screening force [last known - T15]
   Wellesley — Leon — small force [last known - T16]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Supply cost you 1,371 men, at Franche-Comte.
   Munich's garrison regrows — substantial force.
   Switzerland loyalty 86 (-2): satellite drift, the lord's defeats
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   DIPLOMATIC EVENTS
   THE LANDING: Oudinot has put 5,000 men ashore at Ulster.
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the Highlands–Ulster crossing is shut — Britain commands the water.
   REVANCHE: Britain will not forgive France the loss of Ulster and 1 more province. A new design hardens in their court.
   The court of Britain takes up a new design: Revanche.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 28 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 23 of 28 provinces held  |  Settlement (this pair): White Peace (+9)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 23 of 28 provinces held (ticking: +23, +1/turn)  |  Settlement (this pair): White Peace (-7)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 23 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 39/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Massena awaits your orders!
   > Massena: attempt breakout
   Massena cuts his way out! Massena falls back on Artois, his corps disordered but in the field.
   ► is Paris safe
   Paris is ours, Sire, held by a garrison of 25,000. Threats we can see: Archduke Charles of Austria is at Berry, one march away (substantial force); Paget of Britain is at London, two marches off (small force). It is held, but threatened.
   ► Soult, march to Paris
   Soult begins march to Paris. Route: Westphalia → Artois → Paris. Moves to Westphalia.
   Westphalia feeds 15,000; the 27,792 men standing there would lose ~355 a turn to short supply.
   Westphalia lies outside the camp — this takes 27,792 men out of it; no turn counts toward staging while they stand there.
   Westphalia is Prussia's soil — the corps standing there are fed by contract, about −324g more a turn. "Soult, march to Paris." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Westphalia → Artois → Paris. Moves to Westphalia.
   Westphalia feeds 15,000; the 37,692 men standing there would lose ~1,231 a turn to short supply.
   Westphalia is Prussia's soil — the corps standing there are fed by contract, about −108g more a turn. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
map: unchanged (51 labels)
```

```
#0292  type Davout, march to Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0292_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout begins march to Paris. Route: Nivernais → Burgundy → Limousin → Paris. Moves to Nivernais. Davout: "As ordered. I keep my flanks as I go."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1984 of 1984 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   6,766 (+331 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, march to Paris
   Davout begins march to Paris. Route: Nivernais → Burgundy → Limousin → Paris. Moves to Nivernais. Davout: "As ordered. I keep my flanks as I go."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1913,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1441,290)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  37(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Archduke Charles(1525,444)  Massena(1616,379)  ?(1859,472)  Bennigsen(1859,375)  Dumonceau(1322,223)  Oudinot(1303,280)  Ney(1800,497)  Lannes(1813,471)  Bernadotte(1825,445)  Brunswick(1700,300)  Davout(1748,486)  ?(1658,578)  Archduke John(1658,523)  Soult(1671,335)  Napoleon(1694,274)  ?(1490,366)  Paget(1490,328)  ?(1859,519)  ?(1901,591)  25k(1569,503)  6k(1539,472)  ?(1769,580)  ?(1752,420)  12k(1709,420)  ?(1490,417)
```

```
#0293  type lay down a ship of the line at Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0293_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 38 sail — readiness 62 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 39 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 38 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3351,64)]  [icon: Oudinot arrived @(3393,64)]  [icon: Ney arrived (x4) @(3435,64)]  [icon: Davout arrived (x4) @(3477,64)]  [icon: Murat arrived (x2) @(3519,64)]  [icon: Bernadotte arrived (x2) @(3561,64)]  [+28]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2116 of 2116 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   6,366 (+378 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 38 sail — readiness 62 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1913,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1441,290)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  38(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Archduke Charles(1525,444)  Massena(1616,379)  ?(1859,472)  Bennigsen(1859,375)  Dumonceau(1322,223)  Oudinot(1303,280)  Ney(1800,497)  Lannes(1813,471)  Bernadotte(1825,445)  Brunswick(1700,300)  Davout(1748,486)  ?(1658,578)  Archduke John(1658,523)  Soult(1671,335)  Napoleon(1694,274)  ?(1490,366)  Paget(1490,328)  ?(1859,519)  ?(1901,591)  25k(1569,503)  6k(1539,472)  ?(1769,580)  ?(1752,420)  12k(1709,420)  ?(1490,417)
```

```
#0294  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0294_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2183 of 2183 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   6,366 (+378 next turn)
   Inf:
   95,660
   Cav:
   30,000
   Art:
   19,600
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Lannes's corps stands below 40% morale beside Bennigsen (~2,500, Swabia) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0295  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0295_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 17 ended. Turn 18 begins!

Income: 1727g | Occupation: -104g | Contributions: -101g | Charges of Empire: -885g | Admiralty: -76g | Blockade: -336g | Materiel: -273g | Upkeep: -988g (incl. 324g campaign pay) | Other: +562g | Net: -474g | Spent: 400g | Treasury: 5,892g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 377 px] ──
   ENEMY PHASE - Turn 17
   BRITAIN / ──────────────────────────── / - Wellesley moves to Bearn — Bearn falls (was France) and is secured /  / AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Normandy /     The garrison of Normandy is destroyed. /     Region captured: Normandy (was France) (secured) / - Archduke Charles attacks Massena /     Battle of Artois /     Archduke Charles: 546 casualties, 18,446 r …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 36 / 100
   Turn 18 — Early June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 38 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2164 of 2165 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,892 (−133 next turn)
   Inf:
   96,660
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Munich's garrison regrows — substantial force.
   Switzerland loyalty 86 (-2): satellite drift, the lord's defeats
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   DIPLOMATIC EVENTS
   THE LANDING: Oudinot has put 5,000 men ashore at Ulster.
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the Highlands–Ulster crossing is shut — Britain commands the water.
   REVANCHE: Britain will not forgive France the loss of Ulster and 1 more province. A new design hardens in their court.
   The court of Britain takes up a new design: Revanche.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 28 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 23 of 28 provinces held  |  Settlement (this pair): White Peace (+9)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 23 of 28 provinces held (ticking: +23, +1/turn)  |  Settlement (this pair): White Peace (-7)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 23 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 39/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Massena awaits your orders!
   > Massena: attempt breakout
   Massena cuts his way out! Massena falls back on Artois, his corps disordered but in the field.
   ► is Paris safe
   Paris is ours, Sire, held by a garrison of 25,000. Threats we can see: Archduke Charles of Austria is at Berry, one march away (substantial force); Paget of Britain is at London, two marches off (small force). It is held, but threatened.
   ► Soult, march to Paris
   Soult begins march to Paris. Route: Westphalia → Artois → Paris. Moves to Westphalia.
   Westphalia feeds 15,000; the 27,792 men standing there would lose ~355 a turn to short supply.
   Westphalia lies outside the camp — this takes 27,792 men out of it; no turn counts toward staging while they stand there.
   Westphalia is Prussia's soil — the corps standing there are fed by contract, about −324g more a turn. "Soult, march to Paris." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Westphalia → Artois → Paris. Moves to Westphalia.
   Westphalia feeds 15,000; the 37,692 men standing there would lose ~1,231 a turn to short supply.
   Westphalia is Prussia's soil — the corps standing there are fed by contract, about −108g more a turn. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
   ► Davout, march to Paris
   Davout begins march to Paris. Route: Nivernais → Burgundy → Limousin → Paris. Moves to Nivernais. Davout: "As ordered. I keep my flanks as I go."
   [0/4 actions remaining]
   ► lay down a ship of the line at Normandy
   A keel is laid at Normandy — one fleet, whichever yard lays her keel (400g). The fleet stands at 38 sail — readiness 62 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [0/4 actions remaining]
   ⚠ Lannes's corps stands below 40% morale beside Bennigsen (~2,500, Swabia) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► end turn
   ═══════════════════════════════════════
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 1727g | Occupation: -104g | Contributions: -101g | Charges of Empire: -885g | Admiralty: -76g | Blockade: -336g | Materiel: -273g | Other: +562g | Upkeep: -988g | Net: -474g | Spent: 400g
   Treasury: 5,892g
   Actions refreshed: 4/4
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Crowded at Franche-Comte: Ney loses 251 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 104 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Bernadotte loses 220 troops to the press of 3 corps on one province's roads
   Supply shortage at Westphalia: Soult loses 355 troops
   Soult holds at Westphalia, per your orders — the guns at Artois did not move him.
   Garrison at Munich reinforced: 22,000 -> 24,000
   Switzerland loyalty 84 (-2): satellite drift, the lord's defeats
   Relations between Austria and Russia are deteriorating. Alliance may collapse in 2 turns.
   Britain subsidizes Austria with 300 gold.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1899,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  38(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(1604,379)  Archduke Charles(1618,353)  ?(1273,652)  Blake(1272,614)  ?(1861,470)  Kutuzov(1829,419)  ?(1891,469)  Bennigsen(1867,375)  Dumonceau(1322,223)  Oudinot(1303,280)  ?(1449,664)  Wellesley(1449,625)  Ney(1800,497)  Lannes(1813,471)  Bernadotte(1825,445)  ?(1589,598)  Archduke John(1589,560)  ?(1701,295)  Brunswick(1700,266)  Davout(1748,486)  Napoleon(1595,442)  Soult(1683,322)  ?(1490,366)  Paget(1490,309)  ?(1859,519)  ?(1901,591)  25k(1595,503)  ?(1769,580)  ?(1752,420)  12k(1707,420)  ?(1490,417)
```

```
#0296  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0296_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   MASSENA REPORTS
   "Massena is cornered at Artois with 2,277 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 36 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 38 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Massena is cornered @(3351,64)]  [icon: Blockade — Britain closes our ports @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Napoleon orders lost @(3477,64)]  [icon: Oudinot arrived @(3519,64)]  [icon: Ney arrived (x4) @(3561,64)]  [+31]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Munster
   -24 →
   T:17
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1782 of 1782 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,892 (−133 next turn)
   Inf:
   96,660
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Sire — Bearn has fallen to Britain. Enemy colours fly over French homeland soil. Wellesley's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Normandy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Massena's corps has been broken at Artois. He must reform before he fights again.
   • Sire — Archduke Charles has crossed into Artois. Massena stands in his path.
   • Sire — the levy has stood open 5 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
   SITUATION
   France holds 22 regions. Treasury: 5,892g (-201 by the accounts)
   The courts at war hold 39 regions. Estimated enemy strength: 96% of French forces (an estimate — 6 of 6 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   > Soult — Westphalia — 27,437 — Moving to Paris — 2 turns out. (to the letter)
   > Davout — Nivernais — 15,522 — Moving to Paris — 3 turns out.
   - Ney — Franche-Comte — 12,342 — 3 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, four turns running.
   - Bernadotte — Franche-Comte — 10,812 — Awaiting orders. Trust:40
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, four turns running.
   < Napoleon — Paris — 8,287 — Recovers T19. Morale:12%
   ⚠ Morale failing (12) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Lannes — Franche-Comte — 5,102 — 4 turns idle. Morale:1%
   ⚠ Morale failing (1) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Munster — 4,950 — Awaiting orders.
   - Dumonceau — Ulster — 4,550 — Awaiting orders.
   ? Massena — Artois — 2,277 — Hunted by Archduke Charles across 2 frontiers — stands at Artois with 2,277 men. Morale:0%
   ⚠ IN PERIL — an enemy force of ~18,262 shares the field (Artois).
   INTELLIGENCE
   Archduke Charles — Artois — 18,262 [confirmed]
   Archduke John — Languedoc — small force [partial]
   Kutuzov — Swabia — substantial force [partial]
   Brunswick — Oldenburg — large force [partial]
   Paget — London — substantial force [partial]
   Bennigsen — Swabia — screening force [partial]
   Wellesley — Bearn — small force [partial]
   Blake — Leon — screening force [stale - T15]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Supply cost you 930 men, at Franche-Comte and Westphalia.
   Soult holds at Westphalia, per your orders — the guns at Artois did not move him.
   Munich's garrison regrows — substantial force.
   Switzerland loyalty 84 (-2): satellite drift, the lord's defeats
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +1 the Emperor holds court in the capital, +1 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   Prussia seethes: France's columns cross Westphalia in defiance of its declared neutrality.
   Relations with Prussia have worsened significantly (-24 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 25 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 20 of 28 provinces held (ticking: +1, +1/turn)  |  Settlement (this pair): White Peace (+1)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 20 of 28 provinces held (ticking: +25, +1/turn)  |  Settlement (this pair): Favorable Terms — theirs to impose (-24)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 20 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 36/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Massena awaits your orders!
map: unchanged (59 labels)
```

```
#0297  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0297_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1782 of 1782 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Massena awaits your orders!
map: unchanged (59 labels)
```

```
#0298  type status  ->  ERROR: the command line is not taking orders now (it is disabled)
view: <run>\frames\0298_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1782 of 1782 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Massena awaits your orders!
map: unchanged (59 labels)
```

```
#0299  click Attempt a Breakout  ->  ok
  (clicked at (1971, 584))
view: <run>\frames\0299_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Napoleon
   9,900 → 8,287
   ⚔
   Massena ◆
   Archduke Charles ◆
   3,125 → 2,277
   18,992 → 18,446 → 18,262 after the advance
   marched to the guns
   Soult — awaits explicit orders
   BATTLE OF ARTOIS
   click anywhere to skip ▸
   ARTOIS · TURN 17
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 36 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 38 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Napoleon orders lost @(3435,64)]  [icon: Oudinot arrived @(3477,64)]  [icon: Ney arrived (x4) @(3519,64)]  [icon: Davout arrived (x4) @(3561,64)]  [+30]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1826 of 1826 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,892 (−117 next turn)
   Inf:
   97,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Massena: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Massena is taken by Austria at Artois! 1,138 of his men escape home to the depots.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1899,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  38(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1616,379)  ?(1273,652)  Blake(1272,614)  ?(1861,470)  Kutuzov(1829,419)  ?(1891,469)  Bennigsen(1867,375)  Dumonceau(1322,223)  Oudinot(1303,280)  ?(1449,664)  Wellesley(1449,625)  Ney(1800,497)  Lannes(1813,471)  Bernadotte(1825,445)  ?(1589,598)  Archduke John(1589,560)  ?(1701,295)  Brunswick(1700,266)  Davout(1748,486)  Napoleon(1595,442)  Soult(1683,322)  ?(1490,366)  Paget(1490,309)  ?(1859,519)  ?(1901,591)  25k(1595,503)  ?(1769,580)  ?(1752,420)  12k(1707,420)  ?(1490,417)
```

```
#0300  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0300_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1826 of 1826 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,892 (−117 next turn)
   Inf:
   97,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Massena awaits your orders!
   > Massena: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Massena is taken by Austria at Artois! 1,138 of his men escape home to the depots.
map: unchanged (58 labels)
```

```
#0301  type status  ->  ok
  (typed and Enter)
view: <run>\frames\0301_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok === BERTHIER'S INTELLIGENCE REPORT ===

YOUR FORCES:
  Ney (Franche-Comte): 12,342 troops, morale 85, neutral stance
  Davout (Nivernais): 15,522 troops, morale 90, neutral stance, [MOVE_TO]
  Soult (Westphalia): 27,437 troops, morale 100, neutral stance, [MOVE_TO]
  Lannes (Franche-Comte): 5,102 troops, morale 1, neutral stance
  Bernadotte (Franche-Comte): 10,812 troops, morale 95, neutral stance
  Napoleon (Paris): 8,287 troops, morale 12, neutral stance, retreating
  Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
  Oudinot (Munster): 4,950 troops, morale 100, neutral stance

PRISONERS:
  Murat: held by Austria at Vienna since T14.
  Massena: held by Austria at Vienna since T18.

CONFIRMED INTELLIGENCE:
  Archduke Charles (Austria): 18,262 troops at Artois, defensive stance, morale 100 — famed for 'Habsburg Resolve'

RECENT REPORTS:
  Blake: screening force near Leon [3 turns ago]
  Kutuzov, Bennigsen: substantial force near Swabia
  Swabia (Austria): garrison — screening force holds the works
  Wellesley: small force near Bearn
  Munich (Austria): garrison — substantial force holds the works
  Archduke John: small force near Languedoc
  Brunswick: large force near Oldenburg
  Paget: substantial force near London
  London (Britain): garrison — substantial force holds the works

NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.

── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2026 of 2070 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,892 (−117 next turn)
   Inf:
   97,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Franche-Comte): 12,342 troops, morale 85, neutral stance
   Davout (Nivernais): 15,522 troops, morale 90, neutral stance, [MOVE_TO]
   Soult (Westphalia): 27,437 troops, morale 100, neutral stance, [MOVE_TO]
   Lannes (Franche-Comte): 5,102 troops, morale 1, neutral stance
   Bernadotte (Franche-Comte): 10,812 troops, morale 95, neutral stance
   Napoleon (Paris): 8,287 troops, morale 12, neutral stance, retreating
   Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
   Oudinot (Munster): 4,950 troops, morale 100, neutral stance
   PRISONERS:
   Murat: held by Austria at Vienna since T14.
   Massena: held by Austria at Vienna since T18.
   CONFIRMED INTELLIGENCE:
   Archduke Charles (Austria): 18,262 troops at Artois, defensive stance, morale 100 — famed for 'Habsburg Resolve'
   RECENT REPORTS:
   Blake: screening force near Leon [3 turns ago]
   Kutuzov, Bennigsen: substantial force near Swabia
   Swabia (Austria): garrison — screening force holds the works
   Wellesley: small force near Bearn
   Munich (Austria): garrison — substantial force holds the works
   Archduke John: small force near Languedoc
   Brunswick: large force near Oldenburg
   Paget: substantial force near London
   London (Britain): garrison — substantial force holds the works
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
map: unchanged (58 labels)
```

```
#0302  type what if Soult attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0302_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Soult (27,437) vs Archduke Charles (18,262 men) at Artois — the balance of force looks even — a hard fight that may well decide nothing.
  WILL NOT — Napoleon: is in no condition to fight
  The band weighs more than the men: Archduke Charles stands +37% on the defense (his stance, his character and his works).
  Artois feeds 60,000 — the whole muster can stand there fed.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 27,437 we muster) would cost ~206g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.

Nothing has been ordered, and nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2356 of 2356 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,892 (−117 next turn)
   Inf:
   97,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Soult attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Soult (27,437) vs Archduke Charles (18,262 men) at Artois — the balance of force looks even — a hard fight that may well decide nothing.
   WILL NOT — Napoleon: is in no condition to fight
   The band weighs more than the men: Archduke Charles stands +37% on the defense (his stance, his character and his works).
   Artois feeds 60,000 — the whole muster can stand there fed.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 27,437 we muster) would cost ~206g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (58 labels)
```

```
#0303  type Ney, march to Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0303_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins march to Paris. Route: Nivernais → Burgundy → Limousin → Paris. Moves to Nivernais.
Nivernais feeds 22,500; the 27,864 men standing there would lose ~377 a turn to short supply. Ney: "At the double, Sire — the men will smell powder soon enough."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3039 of 3039 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   5,892 (−117 next turn)
   Inf:
   97,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, march to Paris
   Ney begins march to Paris. Route: Nivernais → Burgundy → Limousin → Paris. Moves to Nivernais.
   Nivernais feeds 22,500; the 27,864 men standing there would lose ~377 a turn to short supply. Ney: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1899,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  38(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1616,379)  ?(1273,652)  Blake(1272,614)  Kutuzov(1851,430)  ?(1891,469)  Bennigsen(1867,375)  Dumonceau(1322,223)  Oudinot(1303,280)  ?(1449,664)  Wellesley(1449,625)  Lannes(1800,497)  Bernadotte(1825,471)  ?(1589,598)  Archduke John(1589,560)  ?(1701,295)  Brunswick(1700,266)  Ney(1735,486)  Davout(1761,445)  Napoleon(1595,442)  Soult(1683,322)  ?(1490,366)  Paget(1490,309)  ?(1859,519)  ?(1901,591)  25k(1595,503)  ?(1769,580)  12k(1704,420)  ?(1490,417)
```

```
#0304  type Bernadotte, march to Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0304_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte begins march to Paris. Route: Nivernais → Burgundy → Limousin → Paris. Moves to Nivernais.
Nivernais feeds 22,500; the 38,676 men standing there would lose ~1,188 a turn to short supply. Bernadotte: "As ordered. I keep my flanks as I go."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3172 of 3172 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   5,892 (−117 next turn)
   Inf:
   97,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Bernadotte, march to Paris
   Bernadotte begins march to Paris. Route: Nivernais → Burgundy → Limousin → Paris. Moves to Nivernais.
   Nivernais feeds 22,500; the 38,676 men standing there would lose ~1,188 a turn to short supply. Bernadotte: "As ordered. I keep my flanks as I go."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1899,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  38(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1616,379)  ?(1273,652)  Blake(1272,614)  ?(1852,469)  Kutuzov(1851,430)  ?(1879,469)  Bennigsen(1867,375)  Dumonceau(1322,223)  Oudinot(1303,280)  ?(1449,664)  Wellesley(1449,625)  Lannes(1813,497)  ?(1589,598)  Archduke John(1589,560)  ?(1701,295)  Brunswick(1700,266)  Ney(1735,486)  Davout(1748,460)  Bernadotte(1760,434)  Napoleon(1595,442)  Soult(1683,322)  ?(1490,366)  Paget(1490,309)  ?(1859,524)  ?(1901,591)  25k(1595,503)  ?(1769,580)  12k(1686,416)  ?(1490,417)
```

```
#0305  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0305_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 39 sail — readiness 57 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 36 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 39 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Napoleon orders lost @(3435,64)]  [icon: Oudinot arrived @(3477,64)]  [icon: Ney arrived (x4) @(3519,64)]  [icon: Davout arrived (x4) @(3561,64)]  [+30]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2689 of 2689 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   5,492 (−57 next turn)
   Inf:
   97,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Supply cost you 930 men, at Franche-Comte and Westphalia.
   Soult holds at Westphalia, per your orders — the guns at Artois did not move him.
   Munich's garrison regrows — substantial force.
   Switzerland loyalty 84 (-2): satellite drift, the lord's defeats
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +1 the Emperor holds court in the capital, +1 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   Prussia seethes: France's columns cross Westphalia in defiance of its declared neutrality.
   Relations with Prussia have worsened significantly (-24 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 25 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 20 of 28 provinces held (ticking: +1, +1/turn)  |  Settlement (this pair): White Peace (+1)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 20 of 28 provinces held (ticking: +25, +1/turn)  |  Settlement (this pair): Favorable Terms — theirs to impose (-24)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 20 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 36/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Massena awaits your orders!
   > Massena: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Massena is taken by Austria at Artois! 1,138 of his men escape home to the depots.
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Franche-Comte): 12,342 troops, morale 85, neutral stance
   Davout (Nivernais): 15,522 troops, morale 90, neutral stance, [MOVE_TO]
   Soult (Westphalia): 27,437 troops, morale 100, neutral stance, [MOVE_TO]
   Lannes (Franche-Comte): 5,102 troops, morale 1, neutral stance
   Bernadotte (Franche-Comte): 10,812 troops, morale 95, neutral stance
   Napoleon (Paris): 8,287 troops, morale 12, neutral stance, retreating
   Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
   Oudinot (Munster): 4,950 troops, morale 100, neutral stance
   PRISONERS:
   Murat: held by Austria at Vienna since T14.
   Massena: held by Austria at Vienna since T18.
   CONFIRMED INTELLIGENCE:
   Archduke Charles (Austria): 18,262 troops at Artois, defensive stance, morale 100 — famed for 'Habsburg Resolve'
   RECENT REPORTS:
   Blake: screening force near Leon [3 turns ago]
   Kutuzov, Bennigsen: substantial force near Swabia
   Swabia (Austria): garrison — screening force holds the works
   Wellesley: small force near Bearn
   Munich (Austria): garrison — substantial force holds the works
   Archduke John: small force near Languedoc
   Brunswick: large force near Oldenburg
   Paget: substantial force near London
   London (Britain): garrison — substantial force holds the works
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   ► what if Soult attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Soult (27,437) vs Archduke Charles (18,262 men) at Artois — the balance of force looks even — a hard fight that may well decide nothing.
   WILL NOT — Napoleon: is in no condition to fight
   The band weighs more than the men: Archduke Charles stands +37% on the defense (his stance, his character and his works).
   Artois feeds 60,000 — the whole muster can stand there fed.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 27,437 we muster) would cost ~206g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► Ney, march to Paris
   Ney begins march to Paris. Route: Nivernais → Burgundy → Limousin → Paris. Moves to Nivernais.
   Nivernais feeds 22,500; the 27,864 men standing there would lose ~377 a turn to short supply. Ney: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   ► Bernadotte, march to Paris
   Bernadotte begins march to Paris. Route: Nivernais → Burgundy → Limousin → Paris. Moves to Nivernais.
   Nivernais feeds 22,500; the 38,676 men standing there would lose ~1,188 a turn to short supply. Bernadotte: "As ordered. I keep my flanks as I go."
   [0/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 39 sail — readiness 57 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1899,555)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  39(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1616,379)  ?(1273,652)  Blake(1272,614)  ?(1852,469)  Kutuzov(1851,430)  ?(1879,469)  Bennigsen(1867,375)  Dumonceau(1322,223)  Oudinot(1303,280)  ?(1449,664)  Wellesley(1449,625)  Lannes(1813,497)  ?(1589,598)  Archduke John(1589,560)  ?(1701,295)  Brunswick(1700,266)  Ney(1735,486)  Davout(1748,460)  Bernadotte(1760,434)  Napoleon(1595,442)  Soult(1683,322)  ?(1490,366)  Paget(1490,309)  ?(1859,524)  ?(1901,591)  25k(1595,503)  ?(1769,580)  12k(1686,416)  ?(1490,417)
```

```
#0306  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0306_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2755 of 2755 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   5,492 (−57 next turn)
   Inf:
   97,798
   Cav:
   30,000
   Art:
   20,000
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Lannes's corps stands below 40% morale beside Kutuzov (~27,500, Swabia) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (57 labels)
```

```
#0307  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0307_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 18 ended. Turn 19 begins!

Income: 1641g | Requisitions: +37g | Occupation: -60g | Charges of Empire: -721g | Admiralty: -78g | Blockade: -336g | Materiel: -187g | Upkeep: -600g | Other: +562g | Net: +258g | Spent: 400g | Treasury: 5,750g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 201 px] ──
   ENEMY PHASE - Turn 18
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Artois /     Region captured: Artois (was France) (secured) / - Archduke John attacks Gascony /     Region captured: Gascony (was France) (secured) / - Archduke Charles attacks Champagne /     Region captured: Champagne (was France) (secured) / - Archduke Charles attacks Napoleon /     Second Battle of Paris /     Archduke Charles …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 33 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 39 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3264 of 3264 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,750 (+709 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 1641g | Requisitions: +37g | Occupation: -60g | Charges of Empire: -721g | Admiralty: -78g | Blockade: -336g | Materiel: -187g | Other: +562g | Upkeep: -600g | Net: +258g | Spent: 400g
   Treasury: 5,750g
   Actions refreshed: 4/4
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Supply shortage at Nivernais: Ney loses 128 troops
   Supply shortage at Nivernais: Bernadotte loses 112 troops
   Soult holds at Artois, per your orders — the guns at Paris did not move him.
   Garrison at Munich reinforced: 24,000 -> 25,000
   Switzerland loyalty 82 (-2): satellite drift, the lord's defeats
   Britain subsidizes Russia with 300 gold.
   [!] Bernadotte's trust is faltering (39). Trust his judgment when he objects, and then let him win the battle he asked for — a vindicated objection is the only thing that pays (endow him with an estate or grant him a rente to stop the erosion) — at 20 he will ask to be released.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   Berthier: Enemy forces spotted near Paris! Archduke Charles (17,793 troops) at Champagne.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1880,556)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  39(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Napoleon(1524,499)  Soult(1616,379)  ?(1273,652)  Blake(1272,614)  ?(1852,469)  Kutuzov(1851,430)  ?(1879,469)  Bennigsen(1867,375)  ?(1501,598)  Archduke John(1501,564)  Dumonceau(1322,223)  Oudinot(1303,280)  ?(1449,664)  Wellesley(1449,625)  Lannes(1813,497)  ?(1701,305)  Brunswick(1700,266)  Ney(1735,486)  Bernadotte(1760,460)  Davout(1685,495)  ?(1649,444)  Archduke Charles(1649,418)  ?(1490,366)  Paget(1490,309)  ?(1859,525)  ?(1901,591)  25k(1595,503)  ?(1769,580)  ?(1755,420)  12k(1686,389)  ?(1490,417)
```

```
#0308  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0308_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Napoleon ◆
   Archduke Charles ◆
   8,287 → 4,539
   18,080 → 17,793
   SECOND BATTLE OF PARIS
   click anywhere to skip ▸
   PARIS · TURN 18
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 33 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 39 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Lannes grows bitter @(3351,64)]  [icon: Marshal Bernadotte grows bitter @(3393,64)]  [icon: Blockade — Britain closes our ports @(3435,64)]  [icon: Envoy from Britain @(3477,64)]  [icon: Oudinot arrived @(3519,64)]  [icon: Ney arrived (x4) @(3561,64)]  [+29]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Munster
   -31 →
   T:18
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,750 (+709 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier: Enemy forces spotted near Paris! Archduke Charles (17,793 troops) at Champagne.
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte is marching to Paris (3 turns remaining).
   Davout: Davout marches to Burgundy. 2 regions to Paris.
   Ney: Ney is marching to Paris (3 turns remaining).
   Soult: Soult marches to Artois. 1 region to Paris.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Artois has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Gascony has fallen to Austria. Enemy colours fly over French homeland soil. Archduke John's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Marshal Massena has been taken. Austria holds him prisoner.
   • Sire — Marshal Lannes's household goes unpaid. His patience erodes with his purse.
   • Sire — the levy has stood open 6 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
   SITUATION
   France holds 20 regions. Treasury: 5,750g (+445 by the accounts)
   The courts at war hold 41 regions. Estimated enemy strength: 105% of French forces (an estimate — 6 of 6 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   > Soult — Artois — 26,755 — Moving to Paris — arrives next turn. (to the letter)
   > Davout — Burgundy — 15,522 — Moving to Paris — 2 turns out.
   > Ney — Nivernais — 12,214 — Moving to Paris — 3 turns out.
   > Bernadotte — Nivernais — 10,700 — Moving to Paris — 3 turns out. Trust:39
   - Lannes — Franche-Comte — 5,102 — 5 turns idle. Morale:1%
   ⚠ Morale failing (1) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Munster — 4,950 — Awaiting orders.
   - Dumonceau — Ulster — 4,550 — Awaiting orders.
   < Napoleon — Berry — 3,163 — Has fallen back 2 times in five turns — now at Berry with 3,163 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Archduke Charles — Champagne — substantial force [partial]
   Archduke John — Gascony — small force [partial]
   Kutuzov — Swabia — substantial force [partial]
   Brunswick — Oldenburg — large force [partial]
   Bennigsen — Swabia — screening force [partial]
   Wellesley — Bearn — small force [partial]
   Blake — Leon — screening force [stale - T15]
   Paget — London — small force [stale - T16]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [stale - T16]
   TURN EVENTS
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Supply cost you 240 men, at Nivernais.
   Soult holds at Artois, per your orders — the guns at Paris did not move him.
   Munich's garrison regrows — substantial force.
   Switzerland loyalty 82 (-2): satellite drift, the lord's defeats
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   Massena — held by Austria since turn 18.
   DIPLOMATIC EVENTS
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 23 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 18 of 28 provinces held (ticking: +2, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 18 of 28 provinces held (ticking: +25, +1/turn)  |  Settlement (this pair): Favorable Terms — theirs to impose (-30)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 18 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 33/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0309  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0309_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1960 of 1960 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,750 (+709 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 33/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0310  type status  ->  ok
  (typed and Enter)
view: <run>\frames\0310_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: ok === BERTHIER'S INTELLIGENCE REPORT ===

YOUR FORCES:
  Ney (Nivernais): 12,214 troops, morale 85, neutral stance, [MOVE_TO]
  Davout (Burgundy): 15,522 troops, morale 90, neutral stance, [MOVE_TO]
  Soult (Artois): 26,755 troops, morale 100, neutral stance, [MOVE_TO]
  Lannes (Franche-Comte): 5,102 troops, morale 1, neutral stance
  Bernadotte (Nivernais): 10,700 troops, morale 95, neutral stance, [MOVE_TO]
  Napoleon (Berry): 3,163 troops, morale 0, neutral stance, retreating
  Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
  Oudinot (Munster): 4,950 troops, morale 100, neutral stance

PRISONERS:
  Murat: held by Austria at Vienna since T14.
  Massena: held by Austria at Vienna since T18.

RECENT REPORTS:
  Blake: screening force near Leon [4 turns ago]
  Kutuzov, Bennigsen: substantial force near Swabia
  Swabia (Austria): garrison — screening force holds the works
  Archduke John: small force near Gascony
  Wellesley: small force near Bearn
  Munich (Austria): garrison — substantial force holds the works
  Brunswick: large force near Oldenburg
  Archduke Charles: substantial force near Champagne
  Paget: small force near London [3 turns ago]
  London (Britain): garrison — substantial force holds the works [3 turns ago]

NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.

── IncomingProposalPopup (layer 112) [scrolled 0 of 178 px] ──
   DIPLOMATIC ENVOY / Castlereagh (Hawk) of Britain /  / Proposes: Armistice / Terms: / Mutual: /   - Armistice (cease hostilities temporarily) — France and Britain /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads -1 for France (1 battle, a stalemate, 0 decisives kept); the war is 18 turns old and stays so; exhaustion holds. …
   controls: [Accept]  [Let Talleyrand haggle (1 DP)]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 33 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 39 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2160 of 2160 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,750 (+709 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Nivernais): 12,214 troops, morale 85, neutral stance, [MOVE_TO]
   Davout (Burgundy): 15,522 troops, morale 90, neutral stance, [MOVE_TO]
   Soult (Artois): 26,755 troops, morale 100, neutral stance, [MOVE_TO]
   Lannes (Franche-Comte): 5,102 troops, morale 1, neutral stance
   Bernadotte (Nivernais): 10,700 troops, morale 95, neutral stance, [MOVE_TO]
   Napoleon (Berry): 3,163 troops, morale 0, neutral stance, retreating
   Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
   Oudinot (Munster): 4,950 troops, morale 100, neutral stance
   PRISONERS:
   Murat: held by Austria at Vienna since T14.
   Massena: held by Austria at Vienna since T18.
   RECENT REPORTS:
   Blake: screening force near Leon [4 turns ago]
   Kutuzov, Bennigsen: substantial force near Swabia
   Swabia (Austria): garrison — screening force holds the works
   Archduke John: small force near Gascony
   Wellesley: small force near Bearn
   Munich (Austria): garrison — substantial force holds the works
   Brunswick: large force near Oldenburg
   Archduke Charles: substantial force near Champagne
   Paget: small force near London [3 turns ago]
   London (Britain): garrison — substantial force holds the works [3 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
map: unchanged (59 labels)
```

```
#0311  type is Paris safe  ->  ERROR: the command line is not taking orders now (it is disabled)
view: <run>\frames\0311_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 178 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2160 of 2160 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Archduke Charles: substantial force near Champagne
   Paget: small force near London [3 turns ago]
   London (Britain): garrison — substantial force holds the works [3 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
map: unchanged (59 labels)
```

```
#0312  look  ->  ok
  (a fresh frame)
view: <run>\frames\0312_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 178 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2160 of 2160 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Archduke Charles: substantial force near Champagne
   Paget: small force near London [3 turns ago]
   London (Britain): garrison — substantial force holds the works [3 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
map: unchanged (59 labels)
```

```
#0313  click Accept  ->  ok
  (clicked at (1574, 878))
view: <run>\frames\0313_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 33 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 39 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Lannes grows bitter @(3351,64)]  [icon: Marshal Bernadotte grows bitter @(3393,64)]  [icon: Blockade — Britain closes our ports @(3435,64)]  [icon: Oudinot arrived @(3477,64)]  [icon: Ney arrived (x4) @(3519,64)]  [icon: Davout arrived (x4) @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   -30 →
   T:18
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Britain, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2754 of 2754 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,750 (+1,045 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (59 labels)
```

```
#0314  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0314_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 670 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 23 titled provinces — 45 are needed (22 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -65 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2754 of 2754 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,750 (+1,045 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   London (Britain): garrison — substantial force holds the works [3 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (59 labels)
```

```
#0315  scroll 1850 500 down 6  ->  ok
  (scrolled down 6 at (1850, 500))
view: <run>\frames\0315_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 227 of 672 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (10)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -65 (Hostile)]  [Britain  —  Armistice  |  -75 (Hostile)]  [Prussia  —  Open Borders  |  -38 (Hostile)]  [Spain  —  Alliance  |  +22 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Naples  —  Open Borders  |  -12 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2754 of 2754 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   London (Britain): garrison — substantial force holds the works [3 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (59 labels)
```

```
#0316  click Austria  —  At War  ->  ok
  (clicked at (1825, 419))
view: <run>\frames\0316_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 267 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War for Munster   Relation: -65 (Hostile) /  / "The campaign goes poorly against Austria. An armistice may be wise — though they will sense our weakness and demand terms." / Recommendation: Sire, no road carries while the field reads -30. Open Settlement with Austria alone comes nearest at 2 of 50; Austria's consent (base side pressure) is w …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Unlikely]  [Open Settlement — the whole table: Austria and Russia]  [Propose White Peace — the whole table: Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2754 of 2754 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   London (Britain): garrison — substantial force holds the works [3 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (59 labels)
```

```
#0317  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0317_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 750 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / France demands: /   • Austria releases Massena and Murat to France / France concedes: /   • France pays 1346 gold to Austria /   • France cedes Savoy to Austria / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 33 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 39 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2799 of 2799 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,750 (+1,045 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose armistice with Austria
map: unchanged (59 labels)
```

```
#0318  click Send as suggested  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0318_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 33 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 39 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Lannes grows bitter @(3351,64)]  [icon: Marshal Bernadotte grows bitter @(3393,64)]  [icon: Blockade — Britain closes our ports @(3435,64)]  [icon: Oudinot arrived @(3477,64)]  [icon: Ney arrived (x4) @(3519,64)]  [icon: Davout arrived (x4) @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   -30 →
   T:18
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Britain, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2864 of 2864 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,750 (+1,045 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {97}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (59 labels)
```

```
#0319  type Soult, fortify  ->  ok
  (typed and Enter)
view: <run>\frames\0319_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Artois. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile. Soult's march to Paris is set aside.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2356 of 2357 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   5,750 (+1,045 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Morale failing (1) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Oudinot — Munster — 4,950 — Awaiting orders.
   - Dumonceau — Ulster — 4,550 — Awaiting orders.
   < Napoleon — Berry — 3,163 — Has fallen back 2 times in five turns — now at Berry with 3,163 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Archduke Charles — Champagne — substantial force [partial]
   Archduke John — Gascony — small force [partial]
   Kutuzov — Swabia — substantial force [partial]
   Brunswick — Oldenburg — large force [partial]
   Bennigsen — Swabia — screening force [partial]
   Wellesley — Bearn — small force [partial]
   Blake — Leon — screening force [stale - T15]
   Paget — London — small force [stale - T16]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [stale - T16]
   TURN EVENTS
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Supply cost you 240 men, at Nivernais.
   Soult holds at Artois, per your orders — the guns at Paris did not move him.
   Munich's garrison regrows — substantial force.
   Switzerland loyalty 82 (-2): satellite drift, the lord's defeats
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   Massena — held by Austria since turn 18.
   DIPLOMATIC EVENTS
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 23 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 18 of 28 provinces held (ticking: +2, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 18 of 28 provinces held (ticking: +25, +1/turn)  |  Settlement (this pair): Favorable Terms — theirs to impose (-30)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 18 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 33/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Nivernais): 12,214 troops, morale 85, neutral stance, [MOVE_TO]
   Davout (Burgundy): 15,522 troops, morale 90, neutral stance, [MOVE_TO]
   Soult (Artois): 26,755 troops, morale 100, neutral stance, [MOVE_TO]
   Lannes (Franche-Comte): 5,102 troops, morale 1, neutral stance
   Bernadotte (Nivernais): 10,700 troops, morale 95, neutral stance, [MOVE_TO]
   Napoleon (Berry): 3,163 troops, morale 0, neutral stance, retreating
   Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
   Oudinot (Munster): 4,950 troops, morale 100, neutral stance
   PRISONERS:
   Murat: held by Austria at Vienna since T14.
   Massena: held by Austria at Vienna since T18.
   RECENT REPORTS:
   Blake: screening force near Leon [4 turns ago]
   Kutuzov, Bennigsen: substantial force near Swabia
   Swabia (Austria): garrison — screening force holds the works
   Archduke John: small force near Gascony
   Wellesley: small force near Bearn
   Munich (Austria): garrison — substantial force holds the works
   Brunswick: large force near Oldenburg
   Archduke Charles: substantial force near Champagne
   Paget: small force near London [3 turns ago]
   London (Britain): garrison — substantial force holds the works [3 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   ► propose armistice with Austria
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
   ► Soult, fortify
   [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Artois. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile. Soult's march to Paris is set aside.
   [2/4 actions remaining]
map: unchanged (59 labels)
```

```
#0320  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0320_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 40 sail — readiness 52 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 6/7
   Threat 33 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 40 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Lannes grows bitter @(3351,64)]  [icon: Marshal Bernadotte grows bitter @(3393,64)]  [icon: Blockade — Britain closes our ports @(3435,64)]  [icon: Oudinot arrived @(3477,64)]  [icon: Ney arrived (x4) @(3519,64)]  [icon: Davout arrived (x4) @(3561,64)]  [+28]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2490 of 2490 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   5,350 (+1,106 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 40 sail — readiness 52 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1880,556)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  40(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Napoleon(1524,499)  Soult(1616,379)  ?(1273,652)  Blake(1272,614)  ?(1852,469)  Kutuzov(1851,430)  ?(1879,469)  Bennigsen(1867,375)  ?(1501,598)  Archduke John(1501,564)  Dumonceau(1322,223)  Oudinot(1303,280)  ?(1449,664)  Wellesley(1449,625)  Lannes(1813,497)  ?(1701,305)  Brunswick(1700,266)  Ney(1735,486)  Bernadotte(1760,460)  Davout(1685,495)  ?(1649,444)  Archduke Charles(1649,418)  ?(1490,366)  Paget(1490,309)  ?(1859,525)  ?(1901,591)  25k(1595,503)  ?(1769,580)  ?(1755,420)  12k(1686,389)  ?(1490,417)
```

```
#0321  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0321_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2556 of 2556 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   5,350 (+1,106 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Lannes's corps stands below 40% morale beside Kutuzov (~27,500, Swabia) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (59 labels)
```

```
#0322  look  ->  ok
  (a fresh frame)
view: <run>\frames\0322_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2556 of 2556 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 40 sail — readiness 52 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
   [2/4 actions remaining]
   ⚠ Lannes's corps stands below 40% morale beside Kutuzov (~27,500, Swabia) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (59 labels)
```

```
#0323  type Lannes, retreat  ->  ok
  (typed and Enter)
view: <run>\frames\0323_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes retreats from Franche-Comte to Nivernais.  Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2645 of 2645 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   5,350 (+1,106 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, retreat
   Lannes retreats from Franche-Comte to Nivernais.  Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1880,556)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  40(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Napoleon(1524,499)  Soult(1616,379)  ?(1273,652)  Blake(1272,614)  ?(1852,469)  Kutuzov(1851,430)  ?(1879,469)  Bennigsen(1867,375)  ?(1501,598)  Archduke John(1501,564)  Dumonceau(1322,223)  Oudinot(1303,280)  ?(1449,664)  Wellesley(1449,625)  ?(1701,305)  Brunswick(1700,266)  Ney(1735,486)  Lannes(1748,460)  Bernadotte(1760,434)  Davout(1685,495)  ?(1649,434)  Archduke Charles(1630,404)  ?(1490,366)  Paget(1490,309)  ?(1859,519)  ?(1901,591)  25k(1595,503)  ?(1769,580)  12k(1686,431)  ?(1490,417)
```

```
#0324  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0324_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2711 of 2711 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   5,350 (+1,106 next turn)
   Inf:
   98,798
   Cav:
   30,000
   Art:
   20,000
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Napoleon's corps stands below 40% morale beside Archduke John (~10,000, Gascony) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (58 labels)
```

```
#0325  look  ->  ok
  (a fresh frame)
view: <run>\frames\0325_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2711 of 2711 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Lannes, retreat
   Lannes retreats from Franche-Comte to Nivernais.  Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
   ⚠ Napoleon's corps stands below 40% morale beside Archduke John (~10,000, Gascony) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (58 labels)
```

```
#0326  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0326_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!

Income: 1463g | Occupation: -60g | Charges of Empire: -689g | Admiralty: -80g | Materiel: -235g | Upkeep: -552g | Other: +899g | Net: +746g | Spent: 400g | Treasury: 6,096g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 906 px] ──
   ENEMY PHASE - Turn 19
   RUSSIA / ──────────────────────────── / - Kutuzov attacks Lorraine /     Region captured: Lorraine (was France) (secured) / - Kutuzov attacks Bernadotte /     Battle of Nivernais /     Kutuzov: 1,843 casualties, 31,969 remaining /     Bernadotte's army: 2,714 casualties — Bernadotte's own corps: 8,678 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- / …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 30 / 100
   Turn 20 — Early July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 40 sail]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2692 of 2693 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,096 (+789 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   DIPLOMATIC EVENTS
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 23 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 18 of 28 provinces held (ticking: +2, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 18 of 28 provinces held (ticking: +25, +1/turn)  |  Settlement (this pair): Favorable Terms — theirs to impose (-30)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 18 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 33/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Nivernais): 12,214 troops, morale 85, neutral stance, [MOVE_TO]
   Davout (Burgundy): 15,522 troops, morale 90, neutral stance, [MOVE_TO]
   Soult (Artois): 26,755 troops, morale 100, neutral stance, [MOVE_TO]
   Lannes (Franche-Comte): 5,102 troops, morale 1, neutral stance
   Bernadotte (Nivernais): 10,700 troops, morale 95, neutral stance, [MOVE_TO]
   Napoleon (Berry): 3,163 troops, morale 0, neutral stance, retreating
   Dumonceau (Ulster): 4,550 troops, morale 100, neutral stance
   Oudinot (Munster): 4,950 troops, morale 100, neutral stance
   PRISONERS:
   Murat: held by Austria at Vienna since T14.
   Massena: held by Austria at Vienna since T18.
   RECENT REPORTS:
   Blake: screening force near Leon [4 turns ago]
   Kutuzov, Bennigsen: substantial force near Swabia
   Swabia (Austria): garrison — screening force holds the works
   Archduke John: small force near Gascony
   Wellesley: small force near Bearn
   Munich (Austria): garrison — substantial force holds the works
   Brunswick: large force near Oldenburg
   Archduke Charles: substantial force near Champagne
   Paget: small force near London [3 turns ago]
   London (Britain): garrison — substantial force holds the works [3 turns ago]
   NO INTELLIGENCE: No word from 70 provinces beyond the frontiers of Silesia, Carniola, Vienna, Podolia, Moravia, Hungary, Aragon, Posen.
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   ► propose armistice with Austria
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
   ► Soult, fortify
   [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Artois. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile. Soult's march to Paris is set aside.
   [2/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 40 sail — readiness 52 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
   [2/4 actions remaining]
   ⚠ Lannes's corps stands below 40% morale beside Kutuzov (~27,500, Swabia) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► Lannes, retreat
   Lannes retreats from Franche-Comte to Nivernais.  Army begins recovery (currently at -45% effectiveness). Will recover over 3 turns.
   ⚠ Napoleon's corps stands below 40% morale beside Archduke John (~10,000, Gascony) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 1463g | Occupation: -60g | Charges of Empire: -689g | Admiralty: -80g | Materiel: -235g | Other: +899g | Upkeep: -552g | Net: +746g | Spent: 400g
   Treasury: 6,096g
   Actions refreshed: 4/4
   Soult's fortifications strengthen: +7% defense (max 12%)
   Lannes's army is recovering. Effectiveness penalty: -30%.
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Supply shortage at Burgundy: Davout loses 172 troops
   Supply shortage at Burgundy: Bernadotte loses 96 troops
   Holland loyalty 81 (-5): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 78 (-4): the lord's defeats, satellite drift
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Talleyrand returns from Austria empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was insufficient concessions.
   Britain subsidizes Austria with 300 gold.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1901,566)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  40(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Soult(1616,379)  Dumonceau(1310,223)  Oudinot(1335,197)  ?(1434,578)  Archduke John(1434,540)  Kutuzov(1786,418)  ?(1449,664)  Wellesley(1449,625)  ?(1901,537)  Bennigsen(1901,501)  ?(1701,305)  Brunswick(1700,266)  Ney(1735,486)  Lannes(1760,460)  Davout(1673,495)  Bernadotte(1696,434)  Napoleon(1595,442)  ?(1663,461)  Archduke Charles(1628,407)  ?(1490,366)  Paget(1490,309)  ?(1859,529)  ?(1901,597)  25k(1595,503)  ?(1769,580)  12k(1674,379)  ?(1490,417)
```

```
#0327  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0327_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   DAVOUT REPORTS
   "Davout: 'Cannon fire at Nivernais, Sire. Investigate?'"
   controls: [March to the Guns]  [Continue as Ordered]  [Hold Position]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 30 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 40 sail]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Lannes grows bitter @(3351,64)]  [icon: Marshal Bernadotte grows bitter @(3393,64)]  [icon: Bernadotte — free attack! @(3435,64)]  [icon: Petition from Holland @(3477,64)]  [icon: The blockade on our ports lifts @(3519,64)]  [icon: A Moment of History: The Throne of Holland @(3561,64)]  [+32]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Munster
   -31 →
   T:19
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Britain, truce 4t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2025 of 2025 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,096 (+789 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   Sire — Lorraine has fallen to Russia. Enemy colours fly over French homeland soil. Kutuzov's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Ile-de-France has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces a battle.
   • Sire — Napoleon's corps has been broken at Paris. He must reform before he fights again.
   • Sire — Marshal Lannes's household goes unpaid. His patience erodes with his purse.
   SITUATION
   France holds 17 regions. Treasury: 6,096g (+981 by the accounts)
   The courts at war hold 34 regions. Estimated enemy strength: 87% of French forces (an estimate — 4 of 4 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 85 (Strong at court; the Empire's grip 77 (shaken); the Presence at +9%)
   MARSHAL STATUS
   # Soult — Artois — 26,755 — Fortified at Artois.
   ? Davout — Burgundy — 15,350 — HALTED at Burgundy — awaiting your word.
   > Ney — Nivernais — 11,522 — Moving to Paris — 3 turns out.
   » Bernadotte — Burgundy — 8,582 — Threw back the enemy — may strike once, free, this turn only. Archduke Charles stands within reach at Ile-de-France. Trust:38
   < Lannes — Nivernais — 5,102 — Recovers T22. Morale:1%
   ⚠ Morale failing (1) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   > Oudinot — Ulster — 4,901 — Moving to Artois — 8 turns out.
   - Dumonceau — Ulster — 4,550 — Awaiting orders.
   < Napoleon — Paris — 599 — Hunted by Archduke Charles across 3 frontiers — stands at Paris with 599 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Archduke Charles — Ile-de-France — substantial force [partial]
   Archduke John — Guyenne — small force [partial]
   Kutuzov — Lorraine — substantial force [partial]
   Brunswick — Oldenburg — large force [partial]
   Bennigsen — Munich — screening force [partial]
   Wellesley — Bearn — small force [stale - T18]
   Paget — London — small force [stale - T16]
   Blake — Leon — screening force [last known - T15]
   Swabia garrison — Swabia — garrison — screening force [partial]
   Munich garrison — Munich — garrison — substantial force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +7% defense (max 12%)
   Lannes's army is recovering. Effectiveness penalty: -30%.
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Supply cost you 268 men, at Burgundy.
   2 satellites drifted — Holland and Switzerland.
   Berthier notes that Ney has grown restless — he sees his own laurels counted smaller while Bernadotte wins them. I recommend giving him meaningful orders soon.
   PRISONERS OF WAR
   Murat — held by Austria since turn 14.
   Massena — held by Austria since turn 18.
   DIPLOMATIC EVENTS
   Sire — Britain and France have signed the Armistice.
   A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -1 for France (1 battle, a stalemate, 0 decisives kept); the war is 18 turns old and stays so; exhaustion holds. At expiry: peace — relations stand at -75 and will thaw to -60, at or past -60; what each side holds is titled by the signature.
   Talleyrand has departed for the court of Austria.
   THE LAWS: Austria enacts the Jäger Battalions — infantry drafts muster at +10 morale.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +1 the Emperor holds court in the capital, +1 carried from last turn).
   An envoy from Holland has arrived with a petition.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Talleyrand returns from Austria with a response.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the Highlands–Ulster crossing stands open to our armies.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Holland — Client's Petition
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 20 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 15 of 28 provinces held (ticking: +2, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 15 of 28 provinces held (ticking: +25, +1/turn)  |  Settlement (this pair): Favorable Terms — theirs to impose (-31)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 15 of 28 provinces held (ticking: +1, +1/turn)  |  Settlement (this pair): White Peace (-6)
   COALITION THREAT
   Threat: 30/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (55 labels)
```

```
#0328  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0328_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2025 of 2025 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (55 labels)
```

```
#0329  click Dispatch  ->  ERROR: no visible control's text holds "Dispatch"
view: <run>\frames\0329_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2025 of 2025 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (55 labels)
```

```
#0330  look  ->  ok
  (a fresh frame)
view: <run>\frames\0330_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2025 of 2025 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (55 labels)
```

```
#0331  look  ->  ok
  (a fresh frame)
view: <run>\frames\0331_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2025 of 2025 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Davout awaits your orders!
map: unchanged (55 labels)
```

```
#0332  click March to the Guns  ->  ok
  (clicked at (1639, 551))
view: <run>\frames\0332_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   RUSSIA LOSSES
   0
   0
   Ney
   12,214 → 11,522
   ⚔
   Bernadotte ◆
   Kutuzov ◆
   10,700 → 8,678
   33,812 → 31,969
   BATTLE OF NIVERNAIS
   click anywhere to skip ▸
   NIVERNAIS · TURN 19
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2069 of 2069 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,096 (+789 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Davout: investigate
   Davout abandons his march and rushes toward the guns at Nivernais! Moved to Nivernais.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1901,566)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  40(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Soult(1616,379)  Dumonceau(1310,223)  Oudinot(1335,197)  ?(1434,578)  Archduke John(1434,540)  ?(1449,664)  Wellesley(1449,625)  ?(1901,537)  Bennigsen(1901,501)  ?(1701,305)  Brunswick(1700,266)  Ney(1735,486)  Davout(1748,460)  Lannes(1760,434)  Bernadotte(1684,512)  Napoleon(1595,442)  ?(1663,446)  Archduke Charles(1628,407)  ?(1490,366)  Paget(1490,309)  ?(1859,529)  ?(1901,597)  25k(1595,503)  ?(1769,580)  12k(1674,379)  ?(1490,417)
```

```
#0333  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0333_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2069 of 2069 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,096 (+789 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: investigate
   Davout abandons his march and rushes toward the guns at Nivernais! Moved to Nivernais.
map: unchanged (54 labels)
```

```
#0334  click Event Log  ->  ok
  (clicked at (53, 18))
view: <run>\frames\0334_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=['event_log'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── CampaignLog (layer 50) [scrolled 0 of 324 px] ──
   CAMPAIGN LOG
   France holds Berry — ticking war score (+1/turn)
   An envoy from Holland has arrived with a petition
   Relations auto-downgraded: Austria–Russia (Alliance → Defensive Alliance)
   Britain's gold: 300g reaches Austria
   Prussia rebuffs Russia (defensive alliance)
   The blockade of France is broken — her ports breathe again
   The Throne of Holland — a letter of the record is laid before the Emperor
   controls: [Pin]  [icon: Close (L) @(2143,296)]  [▾ Turn 20  -  7 events]  [▸ Turn 19  -  17 events]  [▸ Turn 18  -  16 events]  [▸ Turn 17  -  17 events]  [▸ Turn 16  -  12 events]  [▸ Turn 15  -  18 events]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2069 of 2069 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,096 (+789 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: investigate
   Davout abandons his march and rushes toward the guns at Nivernais! Moved to Nivernais.
map: unchanged (54 labels)
```

```
#0335  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0335_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   -31 →
   T:19
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Britain, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2069 of 2069 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: investigate
   Davout abandons his march and rushes toward the guns at Nivernais! Moved to Nivernais.
map: unchanged (54 labels)
```

```
#0336  click Envoys  ->  ok
  (clicked at (3404, 18))
view: <run>\frames\0336_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Holland
   Proposal
   Turn 20
   Incoming proposal: Client's Petition
   Terms: Grant it, and Holland's tribute of 337g a turn is remitted for 8 collections (2696g forgone): loyalty +10, its bond with us rises 20 → 40 (worth +2 a turn in loyalty, now +1), for 1 DP. · Refuse it, and Holland loses 10 loyalty and its bond with us falls 20 (20 → 0: worth +0 a turn in loyalty, now +1); nothing is charged. · Left unanswered at the turn's end, the petition lapses — and a laps …
   A client's petition is granted or refused in full — open to decide.
   WAITING
   The Cabinet
   Moment
   Turn 20
   A Moment of History: The Throne of Holland
   A moment of history is answered in full — open the letter to choose.
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2069 of 2069 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: investigate
   Davout abandons his march and rushes toward the guns at Nivernais! Moved to Nivernais.
map: unchanged (54 labels)
```

```
#0337  click#1 Open  ->  ok
  (clicked at (2184, 294))
view: <run>\frames\0337_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Schimmelpenninck (Loyalist) of Holland /  / The petition: /   - Grant it, and Holland's tribute of 337g a turn is remitted for 8 collections (2696g forgone): loyalty +10, its bond with us rises 20 → 40 (worth +2 a turn in loyalty, now +1), for 1 DP. /   - Refuse it, and Holland loses 10 loyalty and its bond with us falls 20 (20 → 0: worth +0 a turn in loyalty, now +1); nothin …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2069 of 2069 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,096 (+789 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: investigate
   Davout abandons his march and rushes toward the guns at Nivernais! Moved to Nivernais.
map: unchanged (54 labels)
```

```
#0338  click Grant  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0338_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 30 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 40 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Lannes grows bitter @(3351,64)]  [icon: Marshal Bernadotte grows bitter @(3393,64)]  [icon: Bernadotte — free attack! @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: A Moment of History: The Throne of Holland @(3519,64)]  [icon: Oudinot arrived @(3561,64)]  [+31]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2135 of 2135 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,096 (+452 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (81 → 91); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0339  click A Moment of History  ->  ok
  (clicked at (3519, 64))
view: <run>\frames\0339_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 30 / 100
   Turn 20 — Early July 1806
   Imperial Box
   A Moment of History: The Throne of Holland
   T20
   Admiral Ver Huell, for the deputation of the States General lays a letter before the Emperor — answer by Late July 1806. /  / The diplomatic packet waits in Envoys for review.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 40 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Lannes grows bitter @(3351,64)]  [icon: Marshal Bernadotte grows bitter @(3393,64)]  [icon: Bernadotte — free attack! @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: A Moment of History: The Throne of Holland @(3519,64)]  [icon: Oudinot arrived @(3561,64)]  [+31]  [Read the letter]  [Keep]  [Acknowledge]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2135 of 2135 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   > Davout: investigate
   Davout abandons his march and rushes toward the guns at Nivernais! Moved to Nivernais.
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (81 → 91); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0340  click Read the letter  ->  ok
  (clicked at (3406, 265))
view: <run>\frames\0340_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A MOMENT OF HISTORY — Early July 1806 / The Throne of Holland — Admiral Ver Huell, for the deputation of the States General lays a letter before the Emperor. / A moment of history, Sire: a decision the record sets before you — two answers, each priced below, or Not Now to set it aside. It waits this turn and the next; left unanswered, it takes the second answer for you. / Historically the Dutch de …
   controls: [Crown Louis]  [Keep the Republic]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 30 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 40 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Lannes grows bitter @(3351,64)]  [icon: Marshal Bernadotte grows bitter @(3393,64)]  [icon: Bernadotte — free attack! @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: A Moment of History: The Throne of Holland @(3519,64)]  [icon: Oudinot arrived @(3561,64)]  [+31]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2135 of 2135 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,096 (+452 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > Davout: investigate
   Davout abandons his march and rushes toward the guns at Nivernais! Moved to Nivernais.
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (81 → 91); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0341  click Not Now  ->  ok
  (clicked at (1979, 878))
view: <run>\frames\0341_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2158 of 2158 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,096 (+452 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Setting aside The Throne of Holland. Click the envoy badge to revisit.
map: unchanged (54 labels)
```

```
#0342  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0342_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 41 sail — readiness 57 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 6/7
   Threat 30 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 41 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Lannes grows bitter @(3351,64)]  [icon: Marshal Bernadotte grows bitter @(3393,64)]  [icon: Bernadotte — free attack! @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: A Moment of History: The Throne of Holland @(3519,64)]  [icon: Oudinot arrived @(3561,64)]  [+31]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2290 of 2290 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   5,696 (+514 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 41 sail — readiness 57 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1901,566)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  41(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Soult(1616,379)  Dumonceau(1310,223)  Oudinot(1335,197)  ?(1434,578)  Archduke John(1434,540)  ?(1449,664)  Wellesley(1449,625)  ?(1901,537)  Bennigsen(1901,501)  ?(1701,305)  Brunswick(1700,266)  Ney(1735,486)  Davout(1748,460)  Lannes(1760,434)  Bernadotte(1684,512)  Napoleon(1595,442)  ?(1663,446)  Archduke Charles(1628,407)  ?(1490,366)  Paget(1490,309)  ?(1859,529)  ?(1901,597)  25k(1595,503)  ?(1769,580)  12k(1674,379)  ?(1490,417)
```

```
#0343  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0343_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2356 of 2356 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   5,696 (+514 next turn)
   Inf:
   99,798
   Cav:
   30,000
   Art:
   20,000
   [end turn]  (Tab)
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Lannes's corps stands below 40% morale beside Kutuzov (~27,500, Lorraine) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0344  look  ->  ok
  (a fresh frame)
view: <run>\frames\0344_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2356 of 2356 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 41 sail — readiness 57 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
   [4/4 actions remaining]
   ⚠ Lannes's corps stands below 40% morale beside Kutuzov (~27,500, Lorraine) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0345  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0345_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!

Income: 1326g | Occupation: -60g | Contributions: -36g | Charges of Empire: -819g | Admiralty: -82g | Materiel: -349g | Upkeep: -544g (incl. 48g campaign pay) | Other: +562g | Net: -2g | Spent: 400g | Treasury: 5,694g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 642 px] ──
   ENEMY PHASE - Turn 20
   RUSSIA / ──────────────────────────── / - Kutuzov attacks Lannes /     Second Battle of Nivernais /     Kutuzov: 2,172 casualties, 29,797 remaining /     Lannes's army: 4,693 casualties — Lannes's own corps: 4,250 remaining /     Result: Attacker tactical victory (Kutuzov victorious) — and advances into Nivernais /     Lannes forced to retreat! /     ⚔ View the field /     --- Berthier's Report -- …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Turn 21 — Late July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 41 sail]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1764 of 1764 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   21
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,694 (+287 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -1 for France (1 battle, a stalemate, 0 decisives kept); the war is 18 turns old and stays so; exhaustion holds. At expiry: peace — relations stand at -75 and will thaw to -60, at or past -60; what each side holds is titled by the signature.
   Talleyrand has departed for the court of Austria.
   THE LAWS: Austria enacts the Jäger Battalions — infantry drafts muster at +10 morale.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +1 the Emperor holds court in the capital, +1 carried from last turn).
   An envoy from Holland has arrived with a petition.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Talleyrand returns from Austria with a response.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the Highlands–Ulster crossing stands open to our armies.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Holland — Client's Petition
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 20 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 15 of 28 provinces held (ticking: +2, +1/turn)  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 15 of 28 provinces held (ticking: +25, +1/turn)  |  Settlement (this pair): Favorable Terms — theirs to impose (-31)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 15 of 28 provinces held (ticking: +1, +1/turn)  |  Settlement (this pair): White Peace (-6)
   COALITION THREAT
   Threat: 30/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "France herself is under the enemy's boot, Sire. Every other matter is secondary."
   ════════════════════════════════════
   Davout awaits your orders!
   > Davout: investigate
   Davout abandons his march and rushes toward the guns at Nivernais! Moved to Nivernais.
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (81 → 91); bond 20 → 40 (+2 a turn). Cost: 1 DP.
   Setting aside The Throne of Holland. Click the envoy badge to revisit.
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 41 sail — readiness 57 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
   [4/4 actions remaining]
   ⚠ Lannes's corps stands below 40% morale beside Kutuzov (~27,500, Lorraine) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► end turn
   ═══════════════════════════════════════
   TURN 21 BEGINS
   ═══════════════════════════════════════
   Income: 1326g | Occupation: -60g | Contributions: -36g | Charges of Empire: -819g | Admiralty: -82g | Materiel: -349g | Other: +562g | Upkeep: -544g | Net: -2g | Spent: 400g
   Treasury: 5,694g
   Actions refreshed: 4/4
   Ney's army is recovering. Effectiveness penalty: -30%.
   Soult's fortifications strengthen: +9% defense (max 12%)
   Lannes's army is recovering. Effectiveness penalty: -15%.
   Napoleon's army has fully recovered and is combat ready.
   [!] Bernadotte's Counter-Punch opportunity has expired! (Must use immediately after defending)
   Supply shortage at Scotland: Moore loses 976 troops
   Supply shortage at Scotland: Shrapnel loses 128 troops
   Supply shortage at Nivernais: Ney loses 220 troops
   Supply shortage at Nivernais: Davout loses 322 troops
   Supply shortage at Nivernais: Lannes loses 99 troops
   Supply shortage at Burgundy: Bernadotte loses 61 troops
   Supply shortage at Burgundy: Archduke Charles loses 296 troops
   Holland loyalty 87 (-4): the lord's defeats, satellite drift
   Switzerland loyalty 74 (-4): the lord's defeats, satellite drift
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Britain and Austria grows.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(1859,495)  Denmark(1751,128)  France(1595,472)  Papal States(1869,731)  Portugal(1216,764)  Britain(1442,337)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 97(1396,395)  41(1374,592)  21(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  5(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Soult(1616,379)  Dumonceau(1322,223)  Bennigsen(1761,322)  ?(1431,184)  Moore(1431,157)  ?(1459,184)  Shrapnel(1446,105)  ?(1449,664)  Wellesley(1449,625)  ?(1480,433)  Archduke John(1480,395)  Oudinot(1419,131)  ?(1701,305)  Brunswick(1700,266)  Ney(1735,486)  Davout(1748,460)  Lannes(1760,434)  Bernadotte(1672,512)  Archduke Charles(1648,434)  Napoleon(1595,408)  ?(1859,526)  ?(1901,591)  25k(1595,503)  ?(1769,580)  12k(1684,405)
```

```
#0346  quit  ->  ok
  (the engine quits)
view: <run>\frames\0346_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 642 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1764 of 1764 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Switzerland loyalty 74 (-4): the lord's defeats, satellite drift
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Britain and Austria grows.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
map: unchanged (53 labels)
```

