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
#0003  click Begin the 1805 Campaign  ->  ok
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
── BottomLeftUI (layer 0) [scrolled 1455 of 1455 px] ──
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
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (G) shows its strength and its flaw.
   The Emperor's Designs — I The Protector of the Rhine, II The Crowns of Italy, III The Continental System: one proclamation decides what the Empire is for, and it cannot be undone. In the Cabinet: F1 → The Emperor's Designs.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
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
── StrategicLedger (layer 50) [scrolled 0 of 816 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late September 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire: 40,000 men on the Channel coast, 2 turns at war with Britain, stage a descent — no order. Britain recalls her fleet and her blockade on you lifts; a won Diversion can open the Strait for up to 2 turns …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1455 of 1455 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0005  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0005_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1455 of 1455 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0006  type what can I do  ->  ok
  (typed and Enter)
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok These orders would be carried out today, Sire:
  Ney, attack Mack
  Davout, march to Lorraine
  Soult, fortify
  recruit infantry in Rhineland — 741g for 3,000 men under Davout
  build supply depot in Rhineland — 300g
For any matter of state, press F1 for the Cabinet.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1146 of 1146 px] ──
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
   For any matter of state, press F1 for the Cabinet.
map: unchanged (53 labels)
```

```
#0007  type Soult, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. "Soult, march to Flanders." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1809 of 1809 px] ──
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
#0008  type Napoleon, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. (1 AP — the Emperor commands in his own name.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1920 of 1920 px] ──
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
#0009  type lay down a ship of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2074 of 2074 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   400 (+801 next turn)
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
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Lannes(1800,497)  Murat(1825,471)  Soult(1683,440)  Napoleon(1706,466)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1730,420)  10k(1910,645)
```

```
#0010  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (24,000; expect about 88,050 with the corps likely to arrive, up to 93,229 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  What Swabia can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 90,000 we muster) would cost ~675g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
  (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   18,000 → 16,790
   Murat
   22,000 → 21,409
   Davout
   26,000 → 24,601
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 21,846 → 21,547 after the advance
   52,000 → 33,701
   marched to the guns
   marched to the guns
   Bernadotte — weighed his own ambitions
   THE GREAT BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 78 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +18 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1927 of 1927 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   1/4
   Admin:
   1/2
   Gold:
   133 (+13 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   • "Ney, attack Mack"
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► what can I do
   These orders would be carried out today, Sire:
   Ney, attack Mack
   Davout, march to Lorraine
   Soult, fortify
   recruit infantry in Rhineland — 741g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
   ► Soult, march to Flanders
   Soult begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. "Soult, march to Flanders." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
   ► Napoleon, march to Flanders
   Napoleon begins march to Flanders. Route: Orleanais → Flanders. Moves to Orleanais. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
   [2/4 actions remaining]
   ► Ney, attack Mack
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (24,000; expect about 88,050 with the corps likely to arrive, up to 93,229 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 90,000 we muster) would cost ~675g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+2%)
   Ney's forces press forward aggressively. Ney gains the advantage over Mack. Casualties: Ney's army 5,354, Mack 18,299. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -267g, Austria -914g. Our treasury stands at 133 gold. Ney advances into Swabia. (299 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   ⚔ View the field
   [1/4 actions remaining]
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
   Massed effective strength: 24,000 (lead) + 69,229 committed (Davout, Lannes, Murat) = 93,229.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,200 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%)
   Casualties: Ney's own corps 2,154 | Mack 18,299
   Strength: Ney 24,000 → 21,846 → 21,547 after the advance | Mack 52,000 → 33,701
   Berthier: "Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Bernadotte never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1871,375)  Ney +3(1847,444)  ?(1965,579)  Archduke John(1948,540)  Soult(1683,440)  Napoleon(1706,466)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1730,420)  10k(1910,645)
```

```
#0011  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   5,354
   18,299
   Lannes
   18,000 → 16,790
   Murat
   22,000 → 21,409
   Davout
   26,000 → 24,601
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 21,846 → 21,547 after the advance
   52,000 → 33,701
   marched to the guns
   marched to the guns
   Bernadotte — weighed his own ambitions
   Berthier: “Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Bernadotte never arrived, Sire.” / Mack: "A temporary derangement of the arithmetic. Vienna will understand."
   THE GREAT BATTLE OF SWABIA
   SWABIA · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1927 of 1927 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (49 labels)
```

```
#0012  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1927 of 1927 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (49 labels)
```

```
#0013  click Ledger (T)  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 684 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Late September 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Moving To  Loc …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1927 of 1927 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (49 labels)
```

```
#0014  click ECONOMY  ->  ok
  (clicked at (1667, 283))
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 750 px] ──
   STRATEGIC LEDGER
   ═══ ECONOMY ═══ / Late September 1805 / The treasury's books — income against upkeep, and every charge with its name on it. /  /   Treasury: 133g /   Ceiling:  2,335g  (where the charges level the chest off at this rate) /   Income:   +2590g /   Trade:    +350g /   Admin:    +25g /   Tribute:  +937g /   Blockade: -175g  (trade halved under enemy sail) /   Admiralty: -92g /   Materiel: -267g  (guns …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY](disabled: You are reading this book)  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1927 of 1927 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (49 labels)
```

```
#0015  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0015_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +18 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1927 of 1927 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (49 labels)
```

```
#0016  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0016_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 1 ended. (Warning: 1 action unused) Turn 2 begins!

Income: 2590g | Admiralty: -92g | Blockade: -219g | Materiel: -231g | Upkeep: -3346g (incl. 180g over-limit, 630g Grande Armée, 1152g campaign pay) | Other: +1270g | Net: -28g | Spent: 400g | Treasury: 105g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 136 px] ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 5,318 casualties, 48,682 remaining /     Massena: 4,622 casualties, 37,378 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Archduke Charles: "France pays …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2351 of 2353 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   105 (+228 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [2/4 actions remaining]
   ► lay down a ship of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
   [2/4 actions remaining]
   ► Ney, attack Mack
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (24,000; expect about 88,050 with the corps likely to arrive, up to 93,229 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 90,000 we muster) would cost ~675g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+2%)
   Ney's forces press forward aggressively. Ney gains the advantage over Mack. Casualties: Ney's army 5,354, Mack 18,299. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -267g, Austria -914g. Our treasury stands at 133 gold. Ney advances into Swabia. (299 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   ⚔ View the field
   [1/4 actions remaining]
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
   Massed effective strength: 24,000 (lead) + 69,229 committed (Davout, Lannes, Murat) = 93,229.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,200 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%)
   Casualties: Ney's own corps 2,154 | Mack 18,299
   Strength: Ney 24,000 → 21,846 → 21,547 after the advance | Mack 52,000 → 33,701
   Berthier: "Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Bernadotte never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
   ► end turn
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -92g | Blockade: -219g | Materiel: -231g | Other: +1270g | Upkeep: -3346g | Net: -28g | Spent: 400g
   Treasury: 105g
   Actions refreshed: 4/4
   Supply shortage at Swabia: Ney loses 777 troops
   Supply shortage at Swabia: Davout loses 887 troops
   Supply shortage at Swabia: Lannes loses 605 troops
   Supply shortage at Swabia: Murat loses 772 troops
   Supply shortage at Tyrol: Archduke Charles loses 1,428 troops
   Supply shortage at Tyrol: Archduke John loses 586 troops
   Supply shortage at Munich: Mack loses 134 troops
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Orleanais. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat is eyeing Mack's position at Munich. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney +3(1847,454)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,579)  Archduke John(2015,511)  ?(1880,562)  Soult(1683,440)  Napoleon(1706,466)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1755,420)  12k(1684,411)  10k(1910,648)
```

```
#0017  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0017_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   42,000 → 37,378
   54,000 → 48,682
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Envoy from Prussia @(3487,62)]  [icon: Envoy from Ottoman Empire @(3529,62)]  [icon: Envoy from Portugal @(3571,62)]  [icon: Marshal Murat seeks an audience @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +18 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1938 of 1938 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   105 (+228 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Naples and Russia have signed an Open Borders Agreement.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat is eyeing Mack's position at Munich. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   --- Strategic Order Updates ---
   Napoleon: Napoleon is marching to Flanders (1 turn remaining).
   Soult: Soult is marching to Flanders (1 turn remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 105g (+203 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 58% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 37,378 — Awaiting orders.
   > Soult — Orleanais — 30,000 — Moving to Flanders — arrives next turn. (to the letter)
   - Davout — Swabia — 23,714 — Awaiting orders.
   - Ney — Swabia — 20,770 — Awaiting orders.
   - Murat — Swabia — 20,637 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Lannes — Swabia — 16,185 — Awaiting orders.
   > Napoleon — Orleanais — 10,000 — Moving to Flanders — arrives next turn.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Munich — substantial force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 3,041 men, at Swabia.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Murat is eyeing Mack's position at Munich. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Orleanais. Holland pays them; their dead will be its grief.
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
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+18)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 76/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0018  click_at 1829 700  ->  ok
  (clicked at (1829, 700) on Verdict 'Berthier: “Stalemate. Massena and Archdu' (RichTextLabel, layer 121))
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   AUSTRIA LOSSES
   4,622
   5,318
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 37,378
   54,000 → 48,682
   Berthier: “Stalemate. Massena and Archduke Charles glare at each other across the field.” / Archduke Charles: "France pays full price for every Austrian mile now."
   THE GREAT BATTLE OF MILAN
   MILAN · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1938 of 1938 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 76/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0019  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0019_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1938 of 1938 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   105 (+228 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 76/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0020  type what if Murat attacks Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Murat (20,637; expect about 110,191 with the corps likely to arrive, up to 112,995 if all march) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — but Murat resents him, and will make no use of him: NOTHING of his weight reaches the fighting — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL NOT — Bernadotte: will not lift a finger for Marshal Murat
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Munich can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in g
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders /  / Hardenberg, stiffly: "Prussia's interest is the Rhine at peace and the army at home; Berlin signs where those two meet. Open the borders." /  / An unexpected overture. There may be hidden motives worth examining. /  / This offer will  …
   controls: [Accept]  [Let Talleyrand haggle (1 DP)]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   105 (+228 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► what if Murat attacks Mack
   Were you to give the order, Sire:
   MUSTER — Murat (20,637; expect about 110,191 with the corps likely to arrive, up to 112,995 if all march) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — but Murat resents him, and will make no use of him: NOTHING of his weight reaches the fighting — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Bernadotte: will not lift a finger for Marshal Murat
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 126,184 we muster) would cost ~946g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (55 labels)
```

```
#0021  click Accept  ->  ok
  (clicked at (1574, 687))
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   THE COURTS WRITE (2)
   Ottoman Empire and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Ottoman Empire
   Proposal
   Open ▸
   Turn 1
   Incoming proposal: Open Borders Agreement
   Reis Efendi, serene and unhurried: "The Porte has outlasted a hundred ascendancies by keeping its counsel with each at its noon; France's noon has come, and the Sublime Porte observes it without haste. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders
   or click the letter to reply in full
   WAITING
   Portugal
   Proposal
   Open ▸
   Turn 1
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "Portugal has watched France grow so vast that a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet harbor within it. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders · Offer: Gold payment - 60
   or click the letter to reply in full
   controls: {ACTIVE}  [Accept]  [Decline]  {WAITING}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3487,62)]  [icon: Marshal Murat seeks an audience @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Open Borders Agreement Accepted @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +18 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2556 of 2556 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   105 (+247 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
map: unchanged (55 labels)
```

```
#0022  click#1 Accept  ->  ok
  (clicked at (1433, 465))
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   A SMALL COURT WRITES (1)
   Portugal writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Portugal
   Proposal
   Open ▸
   Turn 1
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "Portugal has watched France grow so vast that a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet harbor within it. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders · Offer: Gold payment - 60
   or click the letter to reply in full
   controls: {ACTIVE}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3487,62)]  [icon: Marshal Murat seeks an audience @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Open Borders Agreement Accepted @(3613,62)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2578 of 2578 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   105 (+247 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
map: unchanged (55 labels)
```

```
#0023  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3487,62)]  [icon: Marshal Murat seeks an audience @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Open Borders Agreement Accepted @(3613,62)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2600 of 2600 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   105 (+247 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
map: unchanged (55 labels)
```

```
#0024  type Murat, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Murat (20,637; expect about 110,191 with the corps likely to arrive, up to 112,995 if all march) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — but Murat resents him, and will make no use of him: NOTHING of his weight reaches the fighting — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL NOT — Bernadotte: will not lift a finger for Marshal Murat
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Munich can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Ney
   20,770 → 20,770
   Davout
   23,714 → 23,317
   Massena
   37,378 → 36,748
   ⚔
   Murat ◆
   Mack ◆
   marched to the guns
   20,637 → 20,060 → 19,654 after the advance
   31,882 → 0
   marched to the guns
   marched to the guns
   +2 corps in reserve — 260 lost
   THE GREAT BATTLE OF MUNICH
   click anywhere to skip ▸
   MUNICH · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 84 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Treaty with Prussia @(3487,62)]  [icon: Open Borders Agreement Accepted @(3529,62)]  [icon: Treaty with Ottoman @(3571,62)]  [icon: Treaty with Portugal @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +36 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2405 of 2405 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   72 (−94 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 76/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   ► what if Murat attacks Mack
   Were you to give the order, Sire:
   MUSTER — Murat (20,637; expect about 110,191 with the corps likely to arrive, up to 112,995 if all march) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — but Murat resents him, and will make no use of him: NOTHING of his weight reaches the fighting — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Bernadotte: will not lift a finger for Marshal Murat
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 126,184 we muster) would cost ~946g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
   ► Murat, attack Mack
   ⚔ The Great Battle of Munich ⚔
   MUSTER — Murat (20,637; expect about 110,191 with the corps likely to arrive, up to 112,995 if all march) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — but Murat resents him, and will make no use of him: NOTHING of his weight reaches the fighting — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Bernadotte: will not lift a finger for Marshal Murat
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Munich
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 126,184 we muster) would cost ~946g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Murat attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Terrain] Mack benefits from Mountains terrain (+25% defense)
   [Combat] Murat's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Murat's attack! (+2%)
   Murat's forces advance steadily. Murat decisively defeats Mack! Mack's army is destroyed. Murat's army suffered 1,864 casualties.
   [Materiel] Guns, horses and stores lost with the fallen: France -93g, Austria -1660g. Our treasury stands at 72 gold. Mack's army is destroyed! Murat advances into Munich. (406 lost to march) Munich remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   ★ Enemy army destroyed! ★
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Teulie's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 20,637 (lead) + 92,358 committed (Ney, Davout, Lannes, Massena, Teulie) = 112,995.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,287 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Murat: "Their squares were a suggestion. My cavalry declined it."
   Murat fought like a man with something to prove — and proved it. His grievance is settled.
   The corps system brought Ney in.
   The corps system brought Davout in.
   Berthier: the corps marched apart and arrived together.
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1943,581)  Archduke Charles(1940,554)  ?(1970,581)  Archduke John(1999,528)  Ney +5(1901,528)  Soult(1683,440)  Napoleon(1706,466)  Dumonceau(1755,322)  ?(2068,435)  ?(1959,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1755,420)  12k(1684,411)  10k(1910,645)
```

```
#0025  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   1,864
   31,882
   Ney
   20,770 → 20,770
   Davout
   23,714 → 23,317
   Massena
   37,378 → 36,748
   ⚔
   Murat ◆
   Mack ◆
   marched to the guns
   20,637 → 20,060 → 19,654 after the advance
   31,882 → 0
   marched to the guns
   marched to the guns
   +2 corps in reserve — 260 lost
   DESTROYED
   Berthier: “Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away.”
   THE GREAT BATTLE OF MUNICH
   MUNICH · TURN 2
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0026  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0027  click Diplomacy (D)  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 3150 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 7/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 40% of the continent's weight. /   The courts believe he will go as far as war (alarm 84). /   They think he is coming for Austria — his corps stand against their soil. /  / The Emperor …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0028  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +36 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0029  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0030  scroll 1700 600 down 5  ->  ok
  (scrolled down 5 at (1700, 600))
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 190 of 836 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (5)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0031  click Britain  —  At War  ->  ok
  (clicked at (1825, 485))
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 442 px, 0 of 267 px] ──
   THE CABINET — Britain
   DP: 7
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War with the Third Coalition   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — the court sees no reason to sign at +0: Open Settlement with Britain alone stands at -2 of 50; it wants Britain's consent (settlement  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Hopeless]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0032  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0033  click BLOCKADED  ->  ok
  (clicked at (2982, 18))
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 772 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early October 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 46 sail of the line — readiness 64  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — staging the camp lifts the …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Teulie, march to Provence>  <Dumonceau, march to Normandy>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0034  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +36 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2405 of 2405 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (52 labels)
```

```
#0035  type Dumonceau, march to Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Dumonceau begins march to Normandy. Route: Flanders → Picardy → Artois → Normandy. Moves to Flanders. Dumonceau: "We move deliberately — arrival is worth little if the army arrives broken."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3076 of 3076 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   72 (−94 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Dumonceau, march to Normandy
   Dumonceau begins march to Normandy. Route: Flanders → Picardy → Artois → Normandy. Moves to Flanders. Dumonceau: "We move deliberately — arrival is worth little if the army arrives broken."
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1943,581)  Archduke Charles(1940,554)  ?(1970,581)  Archduke John(1999,528)  Ney +5(1901,528)  Soult(1683,440)  Napoleon(1706,466)  Dumonceau(1716,322)  ?(2068,435)  ?(1959,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1684,411)  10k(1910,645)
```

```
#0036  type Massena, march to Milan  ->  ok
  (typed and Enter)
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Not enough actions! Need 2, have 1 — Massena cannot march to Milan today.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3165 of 3165 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   72 (−94 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, march to Milan
   Not enough actions! Need 2, have 1 — Massena cannot march to Milan today.
map: unchanged (52 labels)
```

```
#0037  type Davout, march to Lorraine  ->  ok
  (typed and Enter)
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Not enough actions! Need 2, have 1 — Davout cannot march to Lorraine today.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3253 of 3253 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   72 (−94 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, march to Lorraine
   Not enough actions! Need 2, have 1 — Davout cannot march to Lorraine today.
map: unchanged (52 labels)
```

```
#0038  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3320 of 3320 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   72 (−94 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   [end turn]  (Tab)
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ The treasury will stand at -22 gold when the turn ends (72 now, −94 next turn) — the Ledger's Economy tab shows what drains it.
   Press End Turn again, Enter, or type end turn again to end the turn in deficit.
map: unchanged (52 labels)
```

```
#0039  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0039_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!

Income: 2590g | Admiralty: -92g | Blockade: -281g | Materiel: -286g | Upkeep: -3160g (incl. 120g over-limit, 360g Grande Armée, 1416g campaign pay) | Other: +1401g | Net: +172g | Treasury: 244g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 378 px] ──
   ENEMY PHASE - Turn 2
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Bernadotte /     Battle of Franconia /     Archduke Charles: 2,050 casualties, 45,204 remaining /     Bernadotte: 5,735 casualties, 11,265 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) — and advances into Franconia /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Bernadotte (O …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 83 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1757 of 1758 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   244 (+458 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Teulie's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 20,637 (lead) + 92,358 committed (Ney, Davout, Lannes, Massena, Teulie) = 112,995.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,287 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Murat: "Their squares were a suggestion. My cavalry declined it."
   Murat fought like a man with something to prove — and proved it. His grievance is settled.
   The corps system brought Ney in.
   The corps system brought Davout in.
   Berthier: the corps marched apart and arrived together.
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 577 | Mack 31,882
   Strength: Murat 20,637 → 20,060 → 19,654 after the advance | Mack 31,882 → 0
   Berthier: "Reinforcements! Ney, Davout, Lannes, Massena and Teulie marched onto the field beside Murat. The enemy's advantage melted away."
   ► Dumonceau, march to Normandy
   Dumonceau begins march to Normandy. Route: Flanders → Picardy → Artois → Normandy. Moves to Flanders. Dumonceau: "We move deliberately — arrival is worth little if the army arrives broken."
   [1/4 actions remaining]
   ► Massena, march to Milan
   Not enough actions! Need 2, have 1 — Massena cannot march to Milan today.
   ► Davout, march to Lorraine
   Not enough actions! Need 2, have 1 — Davout cannot march to Lorraine today.
   ⚠ The treasury will stand at -22 gold when the turn ends (72 now, −94 next turn) — the Ledger's Economy tab shows what drains it.
   Press End Turn again, Enter, or type end turn again to end the turn in deficit.
   ► end turn
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -92g | Blockade: -281g | Materiel: -286g | Other: +1401g | Upkeep: -3160g | Net: +172g
   Treasury: 244g
   Actions refreshed: 4/4
   Bavaria completes a market at Franconia.
   Bavaria completes a market at Munich.
   Supply shortage at Franconia: Archduke Charles loses 618 troops
   Supply shortage at Munich: Ney loses 1,246 troops
   Supply shortage at Munich: Davout loses 1,399 troops
   Supply shortage at Munich: Lannes loses 963 troops
   Supply shortage at Munich: Murat loses 1,179 troops
   Supply shortage at Munich: Massena loses 2,204 troops
   Supply shortage at Munich: Deroy loses 944 troops
   Supply shortage at Munich: Teulie loses 442 troops
   Kingdom of Italy loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-3): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Britain subsidizes Austria with 200 gold.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Lannes has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  ?(1948,584)  Archduke John(1948,554)  Deroy(1948,425)  Ney +5(1901,528)  Soult(1704,322)  Napoleon(1715,296)  Dumonceau(1728,270)  ?(2068,435)  ?(1923,347)  10k(1901,591)  ?(1857,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  10k(1910,645)
```

```
#0040  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0040_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 83 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Envoy from Denmark @(3400,64)]  [icon: Envoy from Saxony @(3442,64)]  [icon: Napoleon arrived @(3484,64)]  [icon: Soult arrived @(3526,64)]  [icon: Marshal Davout seeks an audience @(3568,64)]  [+4]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +32 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1873 of 1873 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   244 (+458 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Lannes has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
   --- Strategic Order Updates ---
   Dumonceau: Dumonceau is marching to Normandy (3 turns remaining).
   Napoleon: Napoleon arrives at Flanders.
   Soult: As ordered: "Soult, march to Flanders". Soult arrives at Flanders. Soult stands ready for instruction.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — General Mack of Austria is destroyed at Munich — his corps annihilated, his name struck from their order of battle.
   • Sire — Bernadotte was mauled at Franconia: a third of his corps — 5,735 men — lost in a single action.
   • Sire — Marshal Murat has destroyed Mack's corps at Munich. No enemy formation remains in that field.
   • Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 244g (+458 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 39% of French forces (an estimate — 1 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Munich — 34,544 — Awaiting orders.
   - Soult — Flanders — 30,000 — Awaiting orders.
   - Davout — Munich — 21,918 — Awaiting orders.
   - Ney — Munich — 19,524 — Awaiting orders.
   - Murat — Munich — 18,475 — Awaiting orders.
   - Lannes — Munich — 15,087 — Awaiting orders.
   - Bernadotte — Franconia — 11,265 — Awaiting orders. Trust:40 Morale:55%
   ⚠ IN PERIL — an enemy force of ~41,031 shares the field (Franconia).
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   - Teulie — Munich — 6,933 — Awaiting orders.
   > Dumonceau — Flanders — 6,500 — Moving to Normandy — 3 turns out.
   INTELLIGENCE
   Deroy — Munich — 14,795 [confirmed]
   Archduke Charles — Franconia — 41,031 [confirmed]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 7,433 men, at Munich.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Lannes has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 48).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
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
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+33)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 83/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0041  click Envoys  ->  ok
  (clicked at (3391, 18))
view: <run>\frames\0041_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   THE SMALL COURTS WRITE (2)
   Denmark and Saxony write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Denmark
   Proposal
   Open ▸
   Turn 2
   Incoming proposal: Non-Aggression Pact
   Bernstorff, watchful and correct: "As his sovereign has long willed, Denmark moves toward what the Crown desires. Sign the pact of non-aggression."
   Terms: Proposal: Non-Aggression Pact
   or click the letter to reply in full
   WAITING
   Saxony
   Proposal
   Open ▸
   Turn 2
   Incoming proposal: Open Borders Agreement
   Einsiedel, anxiously: "Saxony has kept her house through many great reigns by keeping her treaties in good repair; His Majesty would merely continue the practice. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders · Offer: Gold payment - 82
   or click the letter to reply in full
   controls: {ACTIVE}  [Accept]  [Decline]  {WAITING}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1873 of 1873 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 83/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0042  click#1 Accept  ->  ok
  (clicked at (1433, 421))
view: <run>\frames\0042_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   A SMALL COURT WRITES (1)
   Saxony writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Saxony
   Proposal
   Open ▸
   Turn 2
   Incoming proposal: Open Borders Agreement
   Einsiedel, anxiously: "Saxony has kept her house through many great reigns by keeping her treaties in good repair; His Majesty would merely continue the practice. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders · Offer: Gold payment - 82
   or click the letter to reply in full
   controls: {ACTIVE}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 83 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Envoy from Denmark @(3400,64)]  [icon: Envoy from Saxony @(3442,64)]  [icon: Napoleon arrived @(3484,64)]  [icon: Soult arrived @(3526,64)]  [icon: Marshal Davout seeks an audience @(3568,64)]  [+4]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1894 of 1894 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   244 (+458 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
map: unchanged (51 labels)
```

```
#0043  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0043_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 83 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Envoy from Denmark @(3400,64)]  [icon: Envoy from Saxony @(3442,64)]  [icon: Napoleon arrived @(3484,64)]  [icon: Soult arrived @(3526,64)]  [icon: Marshal Davout seeks an audience @(3568,64)]  [+4]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1916 of 1916 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   244 (+458 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (51 labels)
```

```
#0044  click BLOCKADED  ->  ok
  (clicked at (2986, 18))
view: <run>\frames\0044_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 772 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late October 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 46 sail of the line — readiness 59  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — staging the camp lifts the  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Bernadotte, march to Provence>  <Teulie, march to Provence>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1916 of 1916 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (51 labels)
```

```
#0045  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0045_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +32 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1916 of 1916 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (51 labels)
```

```
#0046  type what if Ney attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0046_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Ney (19,524; expect about 118,448 with the corps likely to arrive, up to 137,870 if all march) vs Archduke Charles (41,031 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 76%); order 'Davout, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — he will NOT make it from the mountains at Munich in time; order 'Murat, support Ney' and it rises to about 47% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Bernadotte: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 76%); order 'Teulie, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  Standing modifiers, already in the
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1960 of 1960 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   326 (+485 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Ney attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Ney (19,524; expect about 118,448 with the corps likely to arrive, up to 137,870 if all march) vs Archduke Charles (41,031 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 76%); order 'Davout, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — he will NOT make it from the mountains at Munich in time; order 'Murat, support Ney' and it rises to about 47% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Bernadotte: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 76%); order 'Teulie, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~7,661 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 127,746 we muster) would cost ~958g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   Nothing has been ordered, and nothing spent.
map: unchanged (51 labels)
```

```
#0047  type Ney, attack Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0047_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (19,524; expect about 118,448 with the corps likely to arrive, up to 137,870 if all march) vs Archduke Charles (41,031 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 76%); order 'Davout, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — he will NOT make it from the mountains at Munich in time; order 'Murat, support Ney' and it rises to about 47% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Bernadotte: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 76%); order 'Teulie, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  Standing modifiers, already in the band: Archduke Charles stands +3%
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Teulie
   6,933 → 6,393
   Bernadotte
   11,265 → 10,826
   Lannes
   15,087 → 13,617
   ⚔
   Ney ◆
   Archduke Charles ◆
   marched to the guns
   19,524 → 16,986
   41,031 → 34,965
   marched to the guns
   +2 corps in reserve
   Davout — could not reach the field
   He resents Murat's glory.
   THE GREAT THIRD BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 3
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2788 of 2788 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   77 (+693 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+33)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 83/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
   ► what if Ney attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Ney (19,524; expect about 118,448 with the corps likely to arrive, up to 137,870 if all march) vs Archduke Charles (41,031 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 76%); order 'Davout, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — he will NOT make it from the mountains at Munich in time; order 'Murat, support Ney' and it rises to about 47% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Bernadotte: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 76%); order 'Teulie, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~7,661 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 127,746 we muster) would cost ~958g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   Nothing has been ordered, and nothing spent.
   ► Ney, attack Archduke Charles
   ⚔ The Great Third Battle of Franconia ⚔
   MUSTER — Ney (19,524; expect about 118,448 with the corps likely to arrive, up to 137,870 if all march) vs Archduke Charles (41,031 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 76%); order 'Davout, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — he will NOT make it from the mountains at Munich in time; order 'Murat, support Ney' and it rises to about 47% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Bernadotte: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 76%); order 'Teulie, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~7,661 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 127,746 we muster) would cost ~958g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   Ask 'what if Ney attacks Archduke Charles' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+6%)
   Ney engages in solid combat. Brutal stalemate between Ney and Archduke Charles. Heavy casualties on both sides: Ney's army 4,987, Archduke Charles 6,066.
   [Materiel] Guns, horses and stores lost with the fallen: France -249g, Austria -303g. Our treasury stands at 77 gold.
   Lannes withdraws to Munich after the battle.
   Teulie withdraws to Munich after the battle.
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout could not reach the battlefield in time.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat could not reach the battlefield in time.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena was nearly in position, but fate intervened at the crucial moment.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Teulie's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 19,524 (lead) + 33,073 committed (Lannes, Teulie, Bernadotte) = 52,597.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,449 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "Neither side yielded. Unfinished business sits badly with me."
   Attack: Ney (Personality (aggressive) +15%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Ney's own corps 2,538 | Archduke Charles 6,066
   Strength: Ney 19,524 → 16,986 | Archduke Charles 41,031 → 34,965
   Berthier: "Lannes and Teulie's timely arrival aided Ney. Davout, Murat and Massena, however, were conspicuously absent."
map: unchanged (51 labels)
```

```
#0048  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0048_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2788 of 2788 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Ney's own corps 2,538 | Archduke Charles 6,066
   Strength: Ney 19,524 → 16,986 | Archduke Charles 41,031 → 34,965
   Berthier: "Lannes and Teulie's timely arrival aided Ney. Davout, Murat and Massena, however, were conspicuously absent."
map: unchanged (51 labels)
```

```
#0049  type what if Massena attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0049_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Massena (34,544; expect about 97,764 with the corps likely to arrive, up to 109,574 if all march) vs Archduke Charles (34,965 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 76%); order 'Davout, support Massena' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL NOT — Lannes: has already marched this turn
  WILL JOIN — Murat: will march to the sound of the guns — likely to make it in time (about 76%); order 'Murat, support Massena' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Bernadotte: stands on the field and will fight beside him
  WILL NOT — Teulie: has already marched this turn
  Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster standing there would lose ~5,204 men a turn to short supply.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 102,749 we muster) would cost ~771g.
  Every corps in the province shares the field — that is the design. Only a corps st
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2789 of 2789 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   77 (+693 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what if Massena attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Massena (34,544; expect about 97,764 with the corps likely to arrive, up to 109,574 if all march) vs Archduke Charles (34,965 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 76%); order 'Davout, support Massena' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL NOT — Lannes: has already marched this turn
   WILL JOIN — Murat: will march to the sound of the guns — likely to make it in time (about 76%); order 'Murat, support Massena' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Bernadotte: stands on the field and will fight beside him
   WILL NOT — Teulie: has already marched this turn
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~5,204 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 102,749 we muster) would cost ~771g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   Nothing has been ordered, and nothing spent.
map: unchanged (51 labels)
```

```
#0050  type Davout, support Massena  ->  ok
  (typed and Enter)
view: <run>\frames\0050_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves to support Massena (at Munich). Davout holds your written order: when Massena leads a battle within reach, he will march to the guns. The order lapses of itself once Massena is out of danger — name a duration to hold him to it. Davout: "He will not stand alone while I am in range."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3450 of 3450 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   77 (+693 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, support Massena
   Davout moves to support Massena (at Munich). Davout holds your written order: when Massena leads a battle within reach, he will march to the guns. The order lapses of itself once Massena is out of danger — name a duration to hold him to it. Davout: "He will not stand alone while I am in range."
   [2/4 actions remaining]
map: unchanged (51 labels)
```

```
#0051  type Murat, support Massena  ->  ok
  (typed and Enter)
view: <run>\frames\0051_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves to support Massena (at Munich). Murat holds your written order: when Massena leads a battle within reach, he will march to the guns. The order lapses of itself once Massena is out of danger — name a duration to hold him to it. Murat: "He shall have my sabers the moment he needs them — and I shall have a share of the credit."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3605 of 3605 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   77 (+693 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, support Massena
   Murat moves to support Massena (at Munich). Murat holds your written order: when Massena leads a battle within reach, he will march to the guns. The order lapses of itself once Massena is out of danger — name a duration to hold him to it. Murat: "He shall have my sabers the moment he needs them — and I shall have a share of the credit."
   [1/4 actions remaining]
map: unchanged (51 labels)
```

```
#0052  type Massena, attack Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0052_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Massena (34,544; expect about 109,574 with the corps likely to arrive) vs Archduke Charles (34,965 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Davout: marches under your written support order — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL NOT — Lannes: has already marched this turn
  WILL JOIN — Murat: marches under your written support order — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Bernadotte: stands on the field and will fight beside him
  WILL NOT — Teulie: has already marched this turn
  Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster standing there would lose ~5,204 men a turn to short supply.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 102,749 we muster) would cost ~771g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
  Bernadotte shares the
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Ney
   16,986 → 16,475
   Murat
   18,475 → 17,920
   Davout
   21,918 → 21,094
   ⚔
   Massena ◆
   Archduke Charles ◆
   marched to the guns
   34,544 → 32,809 → 31,825 after the advance
   34,965 → 23,875
   marched to the guns
   marched to the guns
   +1 corps in reserve — 325 lost
   THE GREAT FOURTH BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 3
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 91 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Napoleon arrived @(3400,64)]  [icon: Soult arrived @(3442,64)]  [icon: Treaty with Denmark @(3484,64)]  [icon: Treaty with Saxony @(3526,64)]  [icon: Treaty with Prussia @(3568,64)]  [+3]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +35 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3893 of 3893 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   -120 (+883 next turn)
   Inf:
   84,562
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   His supporting allies lost 2,449 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "Neither side yielded. Unfinished business sits badly with me."
   Attack: Ney (Personality (aggressive) +15%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Ney's own corps 2,538 | Archduke Charles 6,066
   Strength: Ney 19,524 → 16,986 | Archduke Charles 41,031 → 34,965
   Berthier: "Lannes and Teulie's timely arrival aided Ney. Davout, Murat and Massena, however, were conspicuously absent."
   ► what if Massena attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Massena (34,544; expect about 97,764 with the corps likely to arrive, up to 109,574 if all march) vs Archduke Charles (34,965 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 76%); order 'Davout, support Massena' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL NOT — Lannes: has already marched this turn
   WILL JOIN — Murat: will march to the sound of the guns — likely to make it in time (about 76%); order 'Murat, support Massena' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Bernadotte: stands on the field and will fight beside him
   WILL NOT — Teulie: has already marched this turn
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~5,204 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 102,749 we muster) would cost ~771g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   Nothing has been ordered, and nothing spent.
   ► Davout, support Massena
   Davout moves to support Massena (at Munich). Davout holds your written order: when Massena leads a battle within reach, he will march to the guns. The order lapses of itself once Massena is out of danger — name a duration to hold him to it. Davout: "He will not stand alone while I am in range."
   [2/4 actions remaining]
   ► Murat, support Massena
   Murat moves to support Massena (at Munich). Murat holds your written order: when Massena leads a battle within reach, he will march to the guns. The order lapses of itself once Massena is out of danger — name a duration to hold him to it. Murat: "He shall have my sabers the moment he needs them — and I shall have a share of the credit."
   [1/4 actions remaining]
   ► Massena, attack Archduke Charles
   ⚔ The Great Fourth Battle of Franconia ⚔
   MUSTER — Massena (34,544; expect about 109,574 with the corps likely to arrive) vs Archduke Charles (34,965 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Davout: marches under your written support order — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL NOT — Lannes: has already marched this turn
   WILL JOIN — Murat: marches under your written support order — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Bernadotte: stands on the field and will fight beside him
   WILL NOT — Teulie: has already marched this turn
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~5,204 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 102,749 we muster) would cost ~771g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   Ask 'what if Massena attacks Archduke Charles' to read the muster before you commit — it costs nothing.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Combat] Massena's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Massena's attack! (+4%)
   Massena's forces advance steadily. Massena gains the advantage over Archduke Charles. Casualties: Massena's army 3,950, Archduke Charles 11,090. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -197g, Austria -554g. Our treasury stands at -120 gold. Massena advances into Franconia. (984 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   Davout answered the guns and stands at Franconia; his support order stands and resumes next turn.
   Murat answered the guns and stands at Franconia; his support order stands and resumes next turn.
   ⚔ View the field
   [0/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 34,544 (lead) + 75,354 committed (Ney, Davout, Murat, Bernadotte) = 109,898.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,215 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "The field is ours! Give me leave and I will take the next one before dusk."
   Davout fought like a man with something to prove — and proved it. His grievance is settled.
   The corps system brought Ney in.
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Massena's own corps 1,735 | Archduke Charles 11,090
   Strength: Massena 34,544 → 32,809 → 31,825 after the advance | Archduke Charles 34,965 → 23,875
   Berthier: "Reinforcements! Ney, Davout and Murat marched onto the field beside Massena. The enemy's advantage melted away."
   The war's cost now stands at 26,512 of our men.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1955,347)  Ney +4(1952,419)  ?(1959,320)  Brunswick(1958,287)  ?(1948,588)  Archduke John(1948,561)  Lannes(1888,535)  Deroy(1901,471)  Teulie(1913,445)  Soult(1704,322)  Napoleon(1715,296)  Dumonceau(1728,270)  ?(2068,435)  ?(1959,376)  10k(1901,591)  ?(1863,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  10k(1910,645)
```

```
#0053  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0053_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3893 of 3893 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Casualties: Massena's own corps 1,735 | Archduke Charles 11,090
   Strength: Massena 34,544 → 32,809 → 31,825 after the advance | Archduke Charles 34,965 → 23,875
   Berthier: "Reinforcements! Ney, Davout and Murat marched onto the field beside Massena. The enemy's advantage melted away."
   The war's cost now stands at 26,512 of our men.
map: unchanged (52 labels)
```

```
#0054  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0054_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 3 ended. Turn 4 begins!

Income: 2590g | Admiralty: -92g | Blockade: -329g | Upkeep: -2614g (incl. 68g over-limit, 126g Grande Armée, 1260g campaign pay) | Other: +1480g | Net: +1035g | Treasury: 915g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 3
   BAVARIA / ──────────────────────────── / - Deroy moves to Franconia / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 89 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3196 of 3197 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   915 (+1,035 next turn)
   Inf:
   86,624
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   WILL NOT — Teulie: has already marched this turn
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~5,204 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 102,749 we muster) would cost ~771g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   Nothing has been ordered, and nothing spent.
   ► Davout, support Massena
   Davout moves to support Massena (at Munich). Davout holds your written order: when Massena leads a battle within reach, he will march to the guns. The order lapses of itself once Massena is out of danger — name a duration to hold him to it. Davout: "He will not stand alone while I am in range."
   [2/4 actions remaining]
   ► Murat, support Massena
   Murat moves to support Massena (at Munich). Murat holds your written order: when Massena leads a battle within reach, he will march to the guns. The order lapses of itself once Massena is out of danger — name a duration to hold him to it. Murat: "He shall have my sabers the moment he needs them — and I shall have a share of the credit."
   [1/4 actions remaining]
   ► Massena, attack Archduke Charles
   ⚔ The Great Fourth Battle of Franconia ⚔
   MUSTER — Massena (34,544; expect about 109,574 with the corps likely to arrive) vs Archduke Charles (34,965 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Davout: marches under your written support order — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL NOT — Lannes: has already marched this turn
   WILL JOIN — Murat: marches under your written support order — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Bernadotte: stands on the field and will fight beside him
   WILL NOT — Teulie: has already marched this turn
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~5,204 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 102,749 we muster) would cost ~771g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   Ask 'what if Massena attacks Archduke Charles' to read the muster before you commit — it costs nothing.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Combat] Massena's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Massena's attack! (+4%)
   Massena's forces advance steadily. Massena gains the advantage over Archduke Charles. Casualties: Massena's army 3,950, Archduke Charles 11,090. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -197g, Austria -554g. Our treasury stands at -120 gold. Massena advances into Franconia. (984 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   Davout answered the guns and stands at Franconia; his support order stands and resumes next turn.
   Murat answered the guns and stands at Franconia; his support order stands and resumes next turn.
   ⚔ View the field
   [0/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 34,544 (lead) + 75,354 committed (Ney, Davout, Murat, Bernadotte) = 109,898.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,215 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "The field is ours! Give me leave and I will take the next one before dusk."
   Davout fought like a man with something to prove — and proved it. His grievance is settled.
   The corps system brought Ney in.
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Massena's own corps 1,735 | Archduke Charles 11,090
   Strength: Massena 34,544 → 32,809 → 31,825 after the advance | Archduke Charles 34,965 → 23,875
   Berthier: "Reinforcements! Ney, Davout and Murat marched onto the field beside Massena. The enemy's advantage melted away."
   The war's cost now stands at 26,512 of our men.
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -92g | Blockade: -329g | Other: +1480g | Upkeep: -2614g | Net: +1035g
   Treasury: 915g
   Actions refreshed: 4/4
   Supply shortage at Franconia: Ney loses 710 troops
   Supply shortage at Franconia: Davout loses 909 troops
   Supply shortage at Franconia: Murat loses 772 troops
   Supply shortage at Franconia: Bernadotte loses 452 troops
   Supply shortage at Franconia: Massena loses 1,372 troops
   Supply shortage at Franconia: Deroy loses 631 troops
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier notes that Davout no longer presses the matter — his quarrel with Murat has cooled.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,484)  Archduke Charles(2024,457)  Deroy(1955,347)  Ney +4(1943,431)  ?(1959,320)  Brunswick(1958,287)  ?(1501,602)  Castanos(1501,564)  ?(1948,588)  Archduke John(1948,561)  Lannes(1888,535)  Teulie(1913,471)  Soult(1704,322)  Napoleon(1728,296)  Dumonceau(1691,418)  ?(1959,376)  10k(1901,591)  ?(1889,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1768,420)  12k(1716,446)  10k(1910,645)
```

```
#0055  look  ->  ok
  (a fresh frame)
view: <run>\frames\0055_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3196 of 3197 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier notes that Davout no longer presses the matter — his quarrel with Murat has cooled.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
map: unchanged (54 labels)
```

```
#0056  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0056_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 89 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Hesse @(3358,64)]  [icon: Envoy from Papal States @(3400,64)]  [icon: Napoleon arrived @(3442,64)]  [icon: Soult arrived @(3484,64)]  [icon: Treaty with Denmark @(3526,64)]  [icon: Treaty with Saxony @(3568,64)]  [+4]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +35 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2051 of 2051 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   915 (+1,035 next turn)
   Inf:
   86,624
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -92g | Blockade: -329g | Other: +1480g | Upkeep: -2614g | Net: +1035g
   Treasury: 915g
   Actions refreshed: 4/4
   Supply shortage at Franconia: Ney loses 710 troops
   Supply shortage at Franconia: Davout loses 909 troops
   Supply shortage at Franconia: Murat loses 772 troops
   Supply shortage at Franconia: Bernadotte loses 452 troops
   Supply shortage at Franconia: Massena loses 1,372 troops
   Supply shortage at Franconia: Deroy loses 631 troops
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier notes that Davout no longer presses the matter — his quarrel with Murat has cooled.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Davout: Davout is moving to support Massena.
   Dumonceau: Dumonceau marches to Picardy. 2 regions to Normandy.
   Murat: Murat is moving to support Massena.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — London now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1,404 gold and shortens the road to 5 turns (not today: the treasury holds 915 gold).
   SITUATION
   France holds 28 regions. Treasury: 915g (+1,035 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 34% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Franconia — 30,453 — Awaiting orders.
   - Soult — Flanders — 30,000 — Awaiting orders.
   > Davout — Franconia — 20,185 — Supporting Massena.
   > Murat — Franconia — 17,148 — Supporting Massena.
   - Ney — Franconia — 15,765 — Awaiting orders.
   - Lannes — Munich — 13,617 — Awaiting orders.
   - Bernadotte — Franconia — 10,049 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   > Dumonceau — Picardy — 6,500 — Moving to Normandy — 2 turns out.
   - Teulie — Munich — 6,393 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 14,017 [confirmed]
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Supply cost you 4,215 men, at Franconia.
   Berthier notes that Davout no longer presses the matter — his quarrel with Murat has cooled.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 67).
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   THE CAMP: France has massed 40,000 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non-Aggression Pact
   - Papal States — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+36)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0057  click BLOCKADED  ->  ok
  (clicked at (2970, 18))
view: <run>\frames\0057_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 772 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early November 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 46 sail of the line — readiness 54  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — the blockade lifts as the …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Lannes, march to Provence>  <Bernadotte, march to Provence>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2051 of 2051 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0058  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0058_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +35 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2051 of 2051 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0059  click Envoys  ->  ok
  (clicked at (3375, 18))
view: <run>\frames\0059_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   THE SMALL COURTS WRITE (2)
   Hesse and Papal States write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Hesse
   Proposal
   Open ▸
   Turn 3
   Incoming proposal: Non-Aggression Pact
   Hesse, wishing to go unnoticed: "Hesse counts what a quarrel with France would cost and what an understanding would return, and finds his councillors of one mind. Sign the pact of non-aggression."
   Terms: Proposal: Non-Aggression Pact
   or click the letter to reply in full
   WAITING
   Papal States
   Proposal
   Open ▸
   Turn 3
   Incoming proposal: Open Borders Agreement
   Cardinal Consalvi, serenely: "Rome measures powers in centuries and finds it profitable to be patient with all of them; an understanding with France costs the Church nothing that time will not repay. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders · Offer: Gold payment - 105
   or click the letter to reply in full
   controls: {ACTIVE}  [Accept]  [Decline]  {WAITING}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2051 of 2051 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0060  click#1 Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0060_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   A SMALL COURT WRITES (1)
   Papal States writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Papal States
   Proposal
   Open ▸
   Turn 3
   Incoming proposal: Open Borders Agreement
   Cardinal Consalvi, serenely: "Rome measures powers in centuries and finds it profitable to be patient with all of them; an understanding with France costs the Church nothing that time will not repay. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders · Offer: Gold payment - 105
   or click the letter to reply in full
   controls: {ACTIVE}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 89 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Hesse @(3358,64)]  [icon: Envoy from Papal States @(3400,64)]  [icon: Napoleon arrived @(3442,64)]  [icon: Soult arrived @(3484,64)]  [icon: Treaty with Denmark @(3526,64)]  [icon: Treaty with Saxony @(3568,64)]  [+4]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   915 (+1,035 next turn)
   Inf:
   86,624
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
map: unchanged (54 labels)
```

```
#0061  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0061_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 89 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Hesse @(3358,64)]  [icon: Envoy from Papal States @(3400,64)]  [icon: Napoleon arrived @(3442,64)]  [icon: Soult arrived @(3484,64)]  [icon: Treaty with Denmark @(3526,64)]  [icon: Treaty with Saxony @(3568,64)]  [+4]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2095 of 2095 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   915 (+1,035 next turn)
   Inf:
   86,624
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (54 labels)
```

```
#0062  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0062_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2095 of 2095 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (54 labels)
```

```
#0063  click Austria  —  At War  ->  ERROR: no visible control's text holds "Austria  —  At War"
view: <run>\frames\0063_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2095 of 2095 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (54 labels)
```

```
#0064  scroll 1700 600 down 5  ->  ok
  (scrolled down 5 at (1700, 600))
view: <run>\frames\0064_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 767 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -10 (Wary)]  [Spain  —  Alliance  |  +37 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2095 of 2095 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (54 labels)
```

```
#0065  click Austria  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0065_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 356 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." / Recommendation: If I may, Sire — Propose Armistice would be signed this morning (51 of 50). It costs 1 DP. A truce keeps the ledg …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Favorable]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Uncertain — a counter is likely]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2095 of 2095 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (54 labels)
```

```
#0066  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0066_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 684 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads +36 for France (4 battles, 2 decisives kept); the war is 3 turns old and stays so; exhaustion holds. No territory or gold changes hands until it en …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 89 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2140 of 2140 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,020 (+1,058 next turn)
   Inf:
   86,624
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose armistice with Austria
map: unchanged (54 labels)
```

```
#0067  click Send as suggested  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0067_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 89 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3358,64)]  [icon: Soult arrived @(3400,64)]  [icon: Treaty with Hesse @(3442,64)]  [icon: Treaty with Papal States @(3484,64)]  [icon: Armistice Dispatched @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+5]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +35 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2206 of 2206 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,020 (+1,058 next turn)
   Inf:
   86,624
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (54 labels)
```

```
#0068  type Soult, march to Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0068_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
Picardy feeds 22,500; the 36,500 men standing there would lose ~705 a turn to short supply. "Soult, march to Normandy." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1785 of 1786 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,020 (+1,058 next turn)
   Inf:
   86,624
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — London now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1,404 gold and shortens the road to 5 turns (not today: the treasury holds 915 gold).
   SITUATION
   France holds 28 regions. Treasury: 915g (+1,035 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 34% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Franconia — 30,453 — Awaiting orders.
   - Soult — Flanders — 30,000 — Awaiting orders.
   > Davout — Franconia — 20,185 — Supporting Massena.
   > Murat — Franconia — 17,148 — Supporting Massena.
   - Ney — Franconia — 15,765 — Awaiting orders.
   - Lannes — Munich — 13,617 — Awaiting orders.
   - Bernadotte — Franconia — 10,049 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Flanders — 10,000 — Awaiting orders.
   > Dumonceau — Picardy — 6,500 — Moving to Normandy — 2 turns out.
   - Teulie — Munich — 6,393 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 14,017 [confirmed]
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Supply cost you 4,215 men, at Franconia.
   Berthier notes that Davout no longer presses the matter — his quarrel with Murat has cooled.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 67).
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   THE CAMP: France has massed 40,000 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non-Aggression Pact
   - Papal States — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+36)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   ► propose armistice with Austria
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
   ► Soult, march to Normandy
   Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 36,500 men standing there would lose ~705 a turn to short supply. "Soult, march to Normandy." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,484)  Archduke Charles(2024,457)  Deroy(1955,347)  Ney +4(1943,431)  ?(1959,320)  Brunswick(1958,287)  ?(1501,602)  Castanos(1501,564)  ?(1948,588)  Archduke John(1948,561)  Lannes(1888,535)  Teulie(1913,471)  Napoleon(1715,322)  Soult(1679,379)  Dumonceau(1703,296)  ?(1959,376)  10k(1901,591)  ?(1889,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,425)  10k(1910,645)
```

```
#0069  type Napoleon, march to Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0069_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
Picardy feeds 22,500; the 46,500 men standing there would lose ~1,674 a turn to short supply. (1 AP — the Emperor commands in his own name.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1919 of 1919 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,020 (+1,058 next turn)
   Inf:
   86,624
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, march to Normandy
   Napoleon begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 46,500 men standing there would lose ~1,674 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,484)  Archduke Charles(2024,457)  Deroy(1955,347)  Ney +4(1943,431)  ?(1959,320)  Brunswick(1958,287)  ?(1501,602)  Castanos(1501,564)  ?(1948,588)  Archduke John(1948,561)  Lannes(1888,535)  Teulie(1913,471)  Soult(1679,379)  Napoleon(1690,322)  Dumonceau(1703,296)  ?(1959,376)  10k(1901,591)  ?(1889,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,425)  10k(1910,645)
```

```
#0070  click BLOCKADED  ->  ok
  (clicked at (2970, 18))
view: <run>\frames\0070_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 794 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early November 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 46 sail of the line — readiness 54  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — the blockade lifts as the …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Lannes, march to Provence>  <Bernadotte, march to Provence>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Normandy
   Napoleon begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 46,500 men standing there would lose ~1,674 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
map: unchanged (54 labels)
```

```
#0071  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0071_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +35 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Napoleon, march to Normandy
   Napoleon begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 46,500 men standing there would lose ~1,674 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
map: unchanged (54 labels)
```

```
#0072  type Massena, march to Milan  ->  ok
  (typed and Enter)
view: <run>\frames\0072_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok Massena: 'Archduke John bars the way!' Engaging!


[Combat] Massena leads the charge! (Aggressive: +15% attack)
[Shield] Archduke John's DEFENSIVE stance strengthens the line! (+15% defense)
[Shield] Archduke John's methodical defense is exemplary! (Cautious: +20% total) Outnumbered bonus: +10%
[Fort] Archduke John's fortified position provides +12% defense!
[Terrain] Archduke John benefits from Mountains terrain (+25% defense)
[Combat] Massena's combined arms coordination! (+10% attack)
[Combat] Adjacent allies bolster Massena's attack! (+2%)
Massena launches a decisive assault. Massena gains the advantage over Archduke John. Casualties: Massena's army 2,783, Archduke John 9,567. Both armies remain in the field.
[Materiel] Guns, horses and stores lost with the fallen: France -139g, Austria -478g. Our treasury stands at 881 gold. Massena advances into Tyrol. (1,691 lost to march)
[Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
Davout answered the guns and stands at Tyrol; his support order stands and resumes next turn.
Murat answered the guns and stands at Tyrol; his support order stands and resumes next turn.
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Ney
   15,765 → 15,436
   Murat
   17,148 → 16,701
   Davout
   20,185 → 19,658
   ⚔
   Massena ◆
   Archduke John ◆
   marched to the guns
   30,453 → 29,390 → 27,699 after the advance
   19,414 → 9,847
   marched to the guns
   marched to the guns
   +2 corps in reserve — 417 lost
   Bernadotte — weighed his own ambitions
   THE GREAT BATTLE OF TYROL
   click anywhere to skip ▸
   TYROL · TURN 4
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 97 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3358,64)]  [icon: Soult arrived @(3400,64)]  [icon: Treaty with Hesse @(3442,64)]  [icon: Treaty with Papal States @(3484,64)]  [icon: Armistice Dispatched @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+5]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +38 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2100 of 2100 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   881 (+2,385 next turn)
   Inf:
   86,624
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non-Aggression Pact
   - Papal States — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+36)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   ► propose armistice with Austria
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
   ► Soult, march to Normandy
   Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 36,500 men standing there would lose ~705 a turn to short supply. "Soult, march to Normandy." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
   ► Napoleon, march to Normandy
   Napoleon begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 46,500 men standing there would lose ~1,674 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
   ► Massena, march to Milan
   ⚔ The Great Battle of Tyrol ⚔
   Massena: 'Archduke John bars the way!' Engaging!
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Archduke John's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Archduke John's methodical defense is exemplary! (Cautious: +20% total) Outnumbered bonus: +10%
   [Fort] Archduke John's fortified position provides +12% defense!
   [Terrain] Archduke John benefits from Mountains terrain (+25% defense)
   [Combat] Massena's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Massena's attack! (+2%)
   Massena launches a decisive assault. Massena gains the advantage over Archduke John. Casualties: Massena's army 2,783, Archduke John 9,567. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -139g, Austria -478g. Our treasury stands at 881 gold. Massena advances into Tyrol. (1,691 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   Davout answered the guns and stands at Tyrol; his support order stands and resumes next turn.
   Murat answered the guns and stands at Tyrol; his support order stands and resumes next turn.
   ⚔ View the field
   [1/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Teulie's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 30,453 (lead) + 89,544 committed (Ney, Davout, Lannes, Murat, Teulie) = 119,997.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,720 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "They broke like green wood, Sire. I want the pursuit."
   The corps system brought Teulie in.
   Berthier: the corps marched apart and arrived together.
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Archduke John (Defensive stance +15%, Fortified position +12%, Personality (cautious) +5%, Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena's own corps 1,063 | Archduke John 9,567
   Strength: Massena 30,453 → 29,390 → 27,699 after the advance | Archduke John 19,414 → 9,847
   Berthier: "Ney, Davout, Lannes, Murat and Teulie arrived to reinforce Massena, but Bernadotte failed to reach the field in time."
   The war's cost now stands at 29,295 of our men.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2040,504)  Archduke Charles(2028,477)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1501,602)  Castanos(1501,564)  Archduke John(1960,528)  Ney +5(1948,554)  Soult(1679,379)  Napoleon(1690,322)  Dumonceau(1703,296)  ?(2068,435)  ?(1959,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,425)  10k(1910,645)
```

```
#0073  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0073_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2100 of 2100 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Casualties: Massena's own corps 1,063 | Archduke John 9,567
   Strength: Massena 30,453 → 29,390 → 27,699 after the advance | Archduke John 19,414 → 9,847
   Berthier: "Ney, Davout, Lannes, Murat and Teulie arrived to reinforce Massena, but Bernadotte failed to reach the field in time."
   The war's cost now stands at 29,295 of our men.
map: unchanged (53 labels)
```

```
#0074  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0074_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!

Income: 2590g | Admiralty: -92g | Upkeep: -2228g (incl. 24g over-limit, 1140g campaign pay) | Other: +1547g | Net: +1817g | Treasury: 2,698g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 4
   BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 95 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2641 of 2641 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,698 (+1,769 next turn)
   Inf:
   88,561
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 36,500 men standing there would lose ~705 a turn to short supply. "Soult, march to Normandy." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
   ► Napoleon, march to Normandy
   Napoleon begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 46,500 men standing there would lose ~1,674 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
   ► Massena, march to Milan
   ⚔ The Great Battle of Tyrol ⚔
   Massena: 'Archduke John bars the way!' Engaging!
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Archduke John's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Archduke John's methodical defense is exemplary! (Cautious: +20% total) Outnumbered bonus: +10%
   [Fort] Archduke John's fortified position provides +12% defense!
   [Terrain] Archduke John benefits from Mountains terrain (+25% defense)
   [Combat] Massena's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Massena's attack! (+2%)
   Massena launches a decisive assault. Massena gains the advantage over Archduke John. Casualties: Massena's army 2,783, Archduke John 9,567. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -139g, Austria -478g. Our treasury stands at 881 gold. Massena advances into Tyrol. (1,691 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   Davout answered the guns and stands at Tyrol; his support order stands and resumes next turn.
   Murat answered the guns and stands at Tyrol; his support order stands and resumes next turn.
   ⚔ View the field
   [1/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Teulie's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 30,453 (lead) + 89,544 committed (Ney, Davout, Lannes, Murat, Teulie) = 119,997.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,720 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "They broke like green wood, Sire. I want the pursuit."
   The corps system brought Teulie in.
   Berthier: the corps marched apart and arrived together.
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Archduke John (Defensive stance +15%, Fortified position +12%, Personality (cautious) +5%, Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena's own corps 1,063 | Archduke John 9,567
   Strength: Massena 30,453 → 29,390 → 27,699 after the advance | Archduke John 19,414 → 9,847
   Berthier: "Ney, Davout, Lannes, Murat and Teulie arrived to reinforce Massena, but Bernadotte failed to reach the field in time."
   The war's cost now stands at 29,295 of our men.
   ► end turn
   ═══════════════════════════════════════
   TURN 5 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -92g | Other: +1547g | Upkeep: -2228g | Net: +1817g
   Treasury: 2,698g
   Actions refreshed: 4/4
   Bavaria completes a supply depot at Munich.
   Supply shortage at Tyrol: Ney loses 926 troops
   Supply shortage at Tyrol: Davout loses 1,179 troops
   Supply shortage at Tyrol: Lannes loses 799 troops
   Supply shortage at Tyrol: Murat loses 1,002 troops
   Supply shortage at Tyrol: Massena loses 1,661 troops
   Supply shortage at Tyrol: Teulie loses 375 troops
   Supply shortage at Picardy: Soult loses 650 troops
   Supply shortage at Picardy: Napoleon loses 216 troops
   Talleyrand returns from Austria with excellent news: they have accepted our proposal! The decisive factor was our military dominance.
   Treaty signed: At War → Armistice with Austria.
   Britain subsidizes Austria with 200 gold.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Soult seeks an audience, Sire — he asks for a command of his own.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,504)  Archduke John(2025,477)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Dumonceau(1616,379)  Ney +5(1948,554)  ?(1551,406)  Castanos(1551,353)  Soult(1679,405)  Napoleon(1703,322)  ?(2068,435)  ?(1959,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,433)  ?(1910,645)
```

```
#0075  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0075_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 95 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3358,64)]  [icon: Marshal Soult asks for a command @(3400,64)]  [icon: Napoleon arrived @(3442,64)]  [icon: Soult arrived @(3484,64)]  [icon: Treaty with Austria @(3526,64)]  [icon: The Moniteur is out @(3568,64)]  [+9]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:4
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1982 of 1982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,698 (+1,769 next turn)
   Inf:
   88,561
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Soult seeks an audience, Sire — he asks for a command of his own.
   --- Strategic Order Updates ---
   Davout: Davout answered the guns this turn and stands at Tyrol; his support order resumes next turn.
   Dumonceau: Dumonceau marches to Artois. 1 region to Normandy.
   Massena: Massena is marching to Milan (2 turns remaining).
   Murat: Murat answered the guns this turn and stands at Tyrol; his support order resumes next turn.
   Napoleon: Napoleon is marching to Normandy (2 turns remaining).
   Soult: Soult is marching to Normandy (2 turns remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 5
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — a truce with Austria holds the guns silent — the war is paused, not over. 5 corps stand on the wrong side of the new frontier. Berthier has given them the road home — Ney to Franche-Comte and Lannes to Franche-Comte. They have safe passage for 5 turns while they march. Davout, Massena and Murat hold under your own orders and were not moved — the treaty offers a road, it does not overrule the Emperor. Their passage lapses with the corridor. Davout, Lannes, Massena, Murat and Ney hold under your own orders and were not moved — the treaty offers a road, it does not overrule the Emperor. Th
   • Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
   • Sire — St Petersburg now pays London 300 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 2,698g (+1,817 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   > Soult — Picardy — 29,350 — Moving to Normandy — 2 turns out. (to the letter)
   > Massena — Tyrol — 26,038 — Moving to Milan — arrives next turn.
   > Davout — Tyrol — 18,479 — Supporting Massena.
   > Murat — Tyrol — 15,699 — Supporting Massena.
   > Ney — Tyrol — 14,510 — Moving to Franche-Comte — 2 turns out.
   > Lannes — Tyrol — 12,534 — Moving to Franche-Comte — 2 turns out.
   - Bernadotte — Franconia — 10,049 — Awaiting orders. Trust:40 Morale:45%
   > Napoleon — Picardy — 9,784 — Moving to Normandy — 2 turns out.
   > Dumonceau — Artois — 6,500 — Moving to Normandy — arrives next turn.
   - Teulie — Tyrol — 5,885 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 14,017 [confirmed]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 6,808 men, at Tyrol and Picardy.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Soult seeks an audience, Sire — he asks for a command of his own.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   Talleyrand has departed for the court of Austria.
   War exhaustion grows — Austria nears breaking point (exhaustion: 86).
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Austria have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 4 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -80 and will thaw to -65, short of -60; the ledger and the war's age come back with it. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 1 French corps stands on Bavarian soil under the truce.
   Talleyrand returns from Austria with a response.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war come, having been asked.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0076  click 46 sail  ->  ok
  (clicked at (3021, 18))
view: <run>\frames\0076_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 596 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late November 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 46 sail of the line — readiness 59  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: No army is staged: 6,500 of the  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Ney, march to Provence>  <Lannes, march to Provence>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1982 of 1982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0077  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0077_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:4
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1982 of 1982 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0078  type what can I do  ->  ok
  (typed and Enter)
view: <run>\frames\0078_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok These orders would be carried out today, Sire:
  Ney, march to Bohemia
  Davout, fortify
  Soult, drill
  recruit infantry in Picardy — 629g for 3,000 men under Soult
  build supply depot in Paris — 300g
For any matter of state, press F1 for the Cabinet.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1674 of 1674 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,698 (+1,769 next turn)
   Inf:
   88,561
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what can I do
   These orders would be carried out today, Sire:
   Ney, march to Bohemia
   Davout, fortify
   Soult, drill
   recruit infantry in Picardy — 629g for 3,000 men under Soult
   build supply depot in Paris — 300g
   For any matter of state, press F1 for the Cabinet.
map: unchanged (52 labels)
```

```
#0079  type what can the fleet do  ->  ok
  (typed and Enter)
view: <run>\frames\0079_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok The fleet musters 46 sail at readiness 59, guarding home waters, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 1 crossing shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing that touches our own coast; Blockade the enemy closes an at-war court's ports where our sail outmatches hers 1.25 to 1 — her trade halved — and leaves our own coast unguarded.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2358 of 2358 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,698 (+1,769 next turn)
   Inf:
   88,561
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what can the fleet do
   The fleet musters 46 sail at readiness 59, guarding home waters, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 1 crossing shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing that touches our own coast; Blockade the enemy closes an at-war court's ports where our sail outmatches hers 1.25 to 1 — her trade halved — and leaves our own coast unguarded.
map: unchanged (52 labels)
```

```
#0080  type Dumonceau, land in Ireland  ->  ok
  (typed and Enter)
view: <run>\frames\0080_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2447 of 2447 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,698 (+1,769 next turn)
   Inf:
   88,561
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
map: unchanged (52 labels)
```

```
#0081  click_at 1320 350  ->  ok
  (clicked at (1320, 350) on MapArea '100' (Control, layer 0))
view: <run>\frames\0081_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2447 of 2447 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► what can the fleet do
   The fleet musters 46 sail at readiness 59, guarding home waters, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 1 crossing shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
map: unchanged (52 labels)
```

```
#0082  click_at 1300 301  ->  ok
  (clicked at (1300, 301) on MapArea '100' (Control, layer 0))
view: <run>\frames\0082_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 221 px] ──
   Munster
   Britain  City · Plains / ACTIONS /     No landing here    no corps of 15,000 or fewer stands at a yard (Bordelais, Brittany, Normandy, Provence) or on a shore abroad or of ours across the water — march one there /  / One province — who holds it, what it pays, what defends it. Click the map to choose another. / No intelligence — scout or advance to learn more. / Income: Unknown   Stability: Unknown …
   controls: [icon @(535,73)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2447 of 2447 px]: unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► what can the fleet do
   The fleet musters 46 sail at readiness 59, guarding home waters, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 1 crossing shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
map: unchanged (52 labels)
```

```
#0083  key G  ->  ok
  (pressed G)
view: <run>\frames\0083_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 6808 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  / SEEKS AN AUDIENCE — Soult /   / [3] Soult  [Infantry]  France / IV Corps - marching for the Speyer crossing from its Lorraine camps, 10,000 of its best carved away to form the Emperor's Guard. A superb tactician who executes the Emperor's plan to the letter, exactly on the appointed …
   controls: [Pin]  [icon @(2213,236)]  <Hear him — he seeks an audience>  <Fortify>  <Drill>  <Hold (1 AP)>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2447 of 2447 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► what can the fleet do
   The fleet musters 46 sail at readiness 59, guarding home waters, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 1 crossing shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
map: unchanged (52 labels)
```

```
#0084  click Commission a Marshal  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0084_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 2169 px] ──
   GENERALS
   ← Back to the Marshalate   /  /   COMMISSION A MARSHAL / Treasury: 2,698g | Pools: 88,561 foot · 22,000 horse · 12,400 guns | A commission raises his corps at the capital from his own arm's pool (1 admin AP + the candidate's price). /  /   / Mortier  [Cautious]  [Infantry] a corps of 5,000 foot  4,000g / Edouard Mortier - steady, imperturbable, and universally liked - one of the few marshals who h …
   controls: [Pin]  [icon @(2213,236)]  <← Back to the Marshalate>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2447 of 2447 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► what can the fleet do
   The fleet musters 46 sail at readiness 59, guarding home waters, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 1 crossing shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
map: unchanged (52 labels)
```

```
#0085  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0085_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:4
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2447 of 2447 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► what can the fleet do
   The fleet musters 46 sail at readiness 59, guarding home waters, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 1 crossing shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
map: unchanged (52 labels)
```

```
#0086  type Davout, march to Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0086_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout begins march to Franche-Comte. Route: Munich → Franche-Comte. Moves to Munich. Davout: "The roads will be scouted before each march, Sire."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2579 of 2579 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   2,698 (+1,769 next turn)
   Inf:
   88,561
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, march to Franche-Comte
   Davout begins march to Franche-Comte. Route: Munich → Franche-Comte. Moves to Munich. Davout: "The roads will be scouted before each march, Sire."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,504)  Archduke John(2025,477)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Dumonceau(1616,379)  Ney +4(1948,561)  Davout(1901,535)  ?(1551,406)  Castanos(1551,353)  Soult(1679,405)  Napoleon(1703,322)  ?(2068,435)  ?(1959,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,433)  ?(1910,645)
```

```
#0087  type Murat, march to Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0087_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat begins march to Franche-Comte. Cavalry charges through Munich -> Franche-Comte. Murat: "We march. Pity whatever slows us."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2051 of 2051 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   2,698 (+1,953 next turn)
   Inf:
   88,561
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   > Soult — Picardy — 29,350 — Moving to Normandy — 2 turns out. (to the letter)
   > Massena — Tyrol — 26,038 — Moving to Milan — arrives next turn.
   > Davout — Tyrol — 18,479 — Supporting Massena.
   > Murat — Tyrol — 15,699 — Supporting Massena.
   > Ney — Tyrol — 14,510 — Moving to Franche-Comte — 2 turns out.
   > Lannes — Tyrol — 12,534 — Moving to Franche-Comte — 2 turns out.
   - Bernadotte — Franconia — 10,049 — Awaiting orders. Trust:40 Morale:45%
   > Napoleon — Picardy — 9,784 — Moving to Normandy — 2 turns out.
   > Dumonceau — Artois — 6,500 — Moving to Normandy — arrives next turn.
   - Teulie — Tyrol — 5,885 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 14,017 [confirmed]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 6,808 men, at Tyrol and Picardy.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Soult seeks an audience, Sire — he asks for a command of his own.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   Talleyrand has departed for the court of Austria.
   War exhaustion grows — Austria nears breaking point (exhaustion: 86).
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Austria have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 4 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -80 and will thaw to -65, short of -60; the ledger and the war's age come back with it. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 1 French corps stands on Bavarian soil under the truce.
   Talleyrand returns from Austria with a response.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war come, having been asked.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   ► what can I do
   These orders would be carried out today, Sire:
   Ney, march to Bohemia
   Davout, fortify
   Soult, drill
   recruit infantry in Picardy — 629g for 3,000 men under Soult
   build supply depot in Paris — 300g
   For any matter of state, press F1 for the Cabinet.
   ► what can the fleet do
   The fleet musters 46 sail at readiness 59, guarding home waters, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 1 crossing shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing that touches our own coast; Blockade the enemy closes an at-war court's ports where our sail outmatches hers 1.25 to 1 — her trade halved — and leaves our own coast unguarded.
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
   ► Davout, march to Franche-Comte
   Davout begins march to Franche-Comte. Route: Munich → Franche-Comte. Moves to Munich. Davout: "The roads will be scouted before each march, Sire."
   [2/4 actions remaining]
   ► Murat, march to Franche-Comte
   Murat begins march to Franche-Comte. Cavalry charges through Munich -> Franche-Comte. Murat: "We march. Pity whatever slows us."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,504)  Archduke John(2025,477)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Dumonceau(1616,379)  Ney +3(1948,564)  Murat(1813,497)  Davout(1901,535)  ?(1551,406)  Castanos(1551,353)  Soult(1679,405)  Napoleon(1703,322)  ?(2068,435)  ?(1959,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,433)  ?(1910,645)
```

```
#0088  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0088_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 5 ended. Turn 6 begins!

Income: 2590g | Charges of Empire: -48g | Admiralty: -92g | Blockade: -368g | Upkeep: -1956g (incl. 12g over-limit, 912g campaign pay) | Other: +1551g | Net: +1677g | Treasury: 4,375g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 269 px] ──
   ENEMY PHASE - Turn 5
   AUSTRIA / ──────────────────────────── / - Archduke Charles moves to Bohemia / - Archduke Charles attacks Deroy /     Fifth Battle of Franconia /     Archduke Charles: 1,510 casualties, 22,365 remaining /     Deroy: 2,509 casualties, 11,508 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) — and advances into Franconia /     ⚔ View the field /     --- Berthier's Repor …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1987 of 1989 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,375 (+1,554 next turn)
   Inf:
   90,398
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Sire — the Papal States and France have signed the Open Borders Agreement.
   Talleyrand has departed for the court of Austria.
   War exhaustion grows — Austria nears breaking point (exhaustion: 86).
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Austria have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 4 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -80 and will thaw to -65, short of -60; the ledger and the war's age come back with it. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 1 French corps stands on Bavarian soil under the truce.
   Talleyrand returns from Austria with a response.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war come, having been asked.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   ► what can I do
   These orders would be carried out today, Sire:
   Ney, march to Bohemia
   Davout, fortify
   Soult, drill
   recruit infantry in Picardy — 629g for 3,000 men under Soult
   build supply depot in Paris — 300g
   For any matter of state, press F1 for the Cabinet.
   ► what can the fleet do
   The fleet musters 46 sail at readiness 59, guarding home waters, under Villeneuve, Sire. Her yards: Bordelais, Brittany, Normandy, Provence. 1 crossing shut to us. She keeps one of two postures, each an order of 1 action on THE ADMIRALTY (press T, then 7): Recall to home waters covers every crossing that touches our own coast; Blockade the enemy closes an at-war court's ports where our sail outmatches hers 1.25 to 1 — her trade halved — and leaves our own coast unguarded.
   ► Dumonceau, land in Ireland
   Name the landing, Sire — click a coastal province on the map for Dumonceau's landing chip; THE ADMIRALTY (press T, then 7) lists the best landings.
   ► Davout, march to Franche-Comte
   Davout begins march to Franche-Comte. Route: Munich → Franche-Comte. Moves to Munich. Davout: "The roads will be scouted before each march, Sire."
   [2/4 actions remaining]
   ► Murat, march to Franche-Comte
   Murat begins march to Franche-Comte. Cavalry charges through Munich -> Franche-Comte. Murat: "We march. Pity whatever slows us."
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -48g | Admiralty: -92g | Blockade: -368g | Other: +1551g | Upkeep: -1956g | Net: +1677g
   Treasury: 4,375g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Massena loses 493 troops
   Supply shortage at Tyrol: Teulie loses 111 troops
   Supply shortage at Munich: Ney loses 479 troops
   Supply shortage at Munich: Davout loses 610 troops
   Supply shortage at Munich: Lannes loses 414 troops
   Supply shortage at Munich: Deroy loses 387 troops
   Kingdom of Italy loyalty 96 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 92 (-2): satellite drift
   Britain subsidizes Austria with 300 gold.
   Territorial rivalry between Russia and Austria grows.
   Berthier reports that Bernadotte appears envious of Lannes's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Soult(1604,379)  Napoleon(1627,353)  Massena(1936,575)  Teulie(1960,549)  Murat(1813,497)  Ney(1888,535)  Davout(1845,471)  Deroy(1948,425)  Castanos(1539,399)  Dumonceau(1563,425)  ?(1490,371)  Moore(1490,344)  ?(2068,435)  ?(1923,347)  10k(1898,603)  ?(1857,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1486,427)  ?(1910,645)
```

```
#0089  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0089_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   MASSENA REPORTS
   "Massena: 'Cannon fire at Franconia, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'"
   controls: [March to the Guns]  [Continue as Ordered]  [Hold Position]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from the Kingdom of Italy @(3351,64)]  [icon: Blockade — Britain closes our ports @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Dumonceau arrived @(3477,64)]  [icon: Murat arrived @(3519,64)]  [icon: Marshal Soult asks for a command @(3561,64)]  [+14]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 4t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2275 of 2275 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,375 (+1,554 next turn)
   Inf:
   90,398
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   --- Strategic Order Updates ---
   Davout: Davout is marching to Franche-Comte (1 turn remaining).
   Dumonceau: Dumonceau arrives at Normandy. Dumonceau: "It is done. I took the liberty of posting pickets."
   Lannes: Lannes marches to Munich. 1 region to Franche-Comte.
   Murat: Murat arrives at Franche-Comte. Murat: "Done — and I trust the next order has more fire in it."
   Napoleon: Napoleon marches to Artois. 1 region to Normandy.
   Ney: Ney marches to Munich. 1 region to Franche-Comte.
   Munich feeds 45,000; the 56,122 men standing there would lose ~1,503 a turn to short supply.
   Soult: Soult marches to Artois. 1 region to Normandy.
   Massena: Massena: 'Cannon fire at Franconia, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'
   Massena awaits your orders!
map: unchanged (57 labels)
```

```
#0090  click Continue as Ordered  ->  ok
  (clicked at (1829, 562))
view: <run>\frames\0090_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2180 of 2180 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,375 (+1,554 next turn)
   Inf:
   90,398
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Territorial rivalry between Russia and Austria grows.
   Berthier reports that Bernadotte appears envious of Lannes's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Davout: Davout is marching to Franche-Comte (1 turn remaining).
   Dumonceau: Dumonceau arrives at Normandy. Dumonceau: "It is done. I took the liberty of posting pickets."
   Lannes: Lannes marches to Munich. 1 region to Franche-Comte.
   Murat: Murat arrives at Franche-Comte. Murat: "Done — and I trust the next order has more fire in it."
   Napoleon: Napoleon marches to Artois. 1 region to Normandy.
   Ney: Ney marches to Munich. 1 region to Franche-Comte.
   Munich feeds 45,000; the 56,122 men standing there would lose ~1,503 a turn to short supply.
   Soult: Soult marches to Artois. 1 region to Normandy.
   Massena: Massena: 'Cannon fire at Franconia, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'
   Massena awaits your orders!
   > Massena: continue order
   Massena reluctantly continues his march, ignoring cannon fire at Franconia. Massena arrives at Milan. Massena: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Massena and Teulie stand 31,319 men at Tyrol, which feeds 20,000. 11,319 too many. 6,546 men lost in 2 turns. No depot may be laid at Tyrol — not controlled by France. Milan can feed 75,000 more and Bohemia can feed 40,000 more — a corps marched there ends it.
   • Sire — a truce with Austria holds the guns silent — the war is paused, not over. 5 corps stand on the wrong side of the new frontier. Berthier has given them the road home — Ney to Franche-Comte and Lannes to Franche-Comte. They have safe passage for 5 turns while they march. Davout, Massena and Murat hold under your own orders and were not moved — the treaty offers a road, it does not overrule the Emperor. Their passage lapses with the corridor. Davout, Lannes, Massena, Murat and Ney hold under your own orders and were not moved — the treaty offers a road, it does not overrule the Emperor. 
   • Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
   SITUATION
   France holds 28 regions. Treasury: 4,375g (+1,677 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 19% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   > Soult — Artois — 29,350 — Moving to Normandy — arrives next turn. (to the letter)
   ? Massena — Tyrol — 25,545 — HALTED at Tyrol — awaiting your word.
   ⚠ Starving — supply has failed at Tyrol two turns running.
   > Davout — Munich — 17,500 — Moving to Franche-Comte — arrives next turn.
   - Murat — Franche-Comte — 15,386 — Awaiting orders.
   > Ney — Munich — 13,741 — Moving to Franche-Comte — arrives next turn.
   > Lannes — Munich — 11,870 — Moving to Franche-Comte — arrives next turn.
   - Bernadotte — Franconia — 10,049 — Awaiting orders. Trust:40 Morale:45%
   > Napoleon — Artois — 9,784 — Moving to Normandy — arrives next turn.
   - Dumonceau — Normandy — 6,500 — Awaiting orders.
   - Teulie — Tyrol — 5,774 — Awaiting orders.
   ⚠ Starving — supply has failed at Tyrol two turns running.
   INTELLIGENCE
   Deroy — Munich — 11,121 [confirmed]
   Archduke Charles — Franconia — 22,036 [confirmed]
   Castanos — Normandy — 14,120 [confirmed]
   Moore — London — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 2,107 men, at Tyrol and Munich.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Berthier reports that Bernadotte appears envious of Lannes's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from the Kingdom of Italy has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Soult(1604,379)  Napoleon(1627,353)  Teulie(1947,575)  Murat(1813,497)  Ney(1888,535)  Davout(1886,561)  Lannes(1942,528)  Deroy(1948,425)  Castanos(1539,399)  Dumonceau(1563,425)  ?(1490,371)  Moore(1490,344)  Massena(1910,601)  ?(2068,435)  ?(1923,347)  10k(1901,629)  ?(1857,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1486,427)  10k(1910,659)
```

```
#0091  click_at 1300 301  ->  ok
  (clicked at (1300, 301) on MapArea '100' (Control, layer 0))
view: <run>\frames\0091_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 221 px] ──
   Munster
   Britain  City · Plains / ACTIONS /     Land Dumonceau here    6,500 men from Normandy · 73 in 100 slip past /       What moves the odds: a won diversion first (29 in 100) → 95 · a 5,000-man corps → 76 /  / One province — who holds it, what it pays, what defends it. Click the map to choose another. / No intelligence — scout or advance to learn more. / Income: Unknown   Stability: Unknown   Supply:  …
   controls: [icon @(535,73)]  <Land Dumonceau here>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2180 of 2180 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0092  click Land Dumonceau here  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0092_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   DUMONCEAU ASKS:
   "The expedition is drawn up, Sire: Dumonceau with 6,500 men, Normandy to Munster. The transports slip past unseen 73 times in 100 (Britain watches at 100 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. What moves the odds: a won diversion first (29 in 100) → 95 · a 5,000-man corps → 76. Sail? …
   controls: [Sail for Munster]  [Stand down]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
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
   4,375 (+1,858 next turn)
   Inf:
   90,398
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► land Dumonceau in Munster
   Dumonceau requests clarification...
map: unchanged (58 labels)
```

```
#0093  click Sail for Munster  ->  ok
  (clicked at (1829, 549))
view: <run>\frames\0093_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Dumonceau has taken Munster
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+600 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1716 of 1718 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,375 (+1,720 next turn)
   Inf:
   90,398
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   SITUATION
   France holds 28 regions. Treasury: 4,375g (+1,677 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 19% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   > Soult — Artois — 29,350 — Moving to Normandy — arrives next turn. (to the letter)
   ? Massena — Tyrol — 25,545 — HALTED at Tyrol — awaiting your word.
   ⚠ Starving — supply has failed at Tyrol two turns running.
   > Davout — Munich — 17,500 — Moving to Franche-Comte — arrives next turn.
   - Murat — Franche-Comte — 15,386 — Awaiting orders.
   > Ney — Munich — 13,741 — Moving to Franche-Comte — arrives next turn.
   > Lannes — Munich — 11,870 — Moving to Franche-Comte — arrives next turn.
   - Bernadotte — Franconia — 10,049 — Awaiting orders. Trust:40 Morale:45%
   > Napoleon — Artois — 9,784 — Moving to Normandy — arrives next turn.
   - Dumonceau — Normandy — 6,500 — Awaiting orders.
   - Teulie — Tyrol — 5,774 — Awaiting orders.
   ⚠ Starving — supply has failed at Tyrol two turns running.
   INTELLIGENCE
   Deroy — Munich — 11,121 [confirmed]
   Archduke Charles — Franconia — 22,036 [confirmed]
   Castanos — Normandy — 14,120 [confirmed]
   Moore — London — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 2,107 men, at Tyrol and Munich.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Berthier reports that Bernadotte appears envious of Lannes's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from the Kingdom of Italy has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   ► land Dumonceau in Munster
   Dumonceau requests clarification...
   > land Dumonceau in Munster confirmed
   THE LANDING: Dumonceau slips past the British patrols and puts 6,500 men ashore at Munster (odds were 73 in 100).
   Your forces have taken Munster. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [2/4 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Soult(1604,379)  Napoleon(1627,353)  Teulie(1947,575)  Dumonceau(1303,280)  Murat(1813,497)  Ney(1888,535)  Davout(1886,561)  Lannes(1942,528)  Deroy(1948,425)  Castanos(1551,405)  ?(1490,371)  Moore(1490,344)  Massena(1910,601)  ?(2068,435)  ?(1923,347)  10k(1901,629)  ?(1857,434)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  ?(1487,417)  10k(1910,659)
```

```
#0094  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0094_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from the Kingdom of Italy @(3351,64)]  [icon: Blockade — Britain closes our ports @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: Dumonceau arrived @(3519,64)]  [icon: Murat arrived @(3561,64)]  [+15]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +5 ↑
   T:5
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 4t]
── BottomLeftUI (layer 0) [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,375 (+1,720 next turn)
   Inf:
   90,398
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Dumonceau secures Munster. Stability set to 25. Order is maintained. 1 building damaged.
map: unchanged (58 labels)
```

```
#0095  type recruit infantry in Artois  ->  ok
  (typed and Enter)
view: <run>\frames\0095_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: ok Soult recruits 3,000 infantry for Artois (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war) (×1.00 over the ordinance). Morale: 100% -> 94%
Infantry pool: 90,398 -> 87,398
── IncomingProposalPopup (layer 112) [scrolled 0 of 24 px] ──
   A CLIENT'S PETITION / Marescalchi (Loyalist) of Kingdom of Italy /  / The petition: /   - Grant it, and the Kingdom of Italy's tribute of 352g a turn is remitted for 8 collections (2816g forgone): loyalty +4 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and the Kingdom of Italy loses 10 loyalty and its bond with us falls 20 (0  …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   3,775 (+1,720 next turn)
   Inf:
   87,398
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► recruit infantry in Artois
   + Soult recruits 3,000 infantry for Artois (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war) (×1.00 over the ordinance). Morale: 100% -> 94%
   Infantry pool: 90,398 -> 87,398
   [2/4 actions remaining]
map: unchanged (58 labels)
```

```
#0096  click Refuse  ->  ok
  (clicked at (1829, 687))
view: <run>\frames\0096_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3351,64)]  [icon: Massena arrived @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Dumonceau arrived @(3477,64)]  [icon: Murat arrived @(3519,64)]  [icon: Marshal Soult asks for a command @(3561,64)]  [+15]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +5 ↑
   T:5
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2027 of 2027 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   3,775 (+1,720 next turn)
   Inf:
   87,398
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to the Kingdom of Italy's proposal: declined
   The Kingdom of Italy's petition for relief is refused: loyalty −10 (96 → 86); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (58 labels)
```

```
#0097  type Murat, march to Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0097_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat begins march to Normandy. Route: Orleanais → Picardy → Artois → Normandy. Cavalry charges through Lorraine -> Orleanais. Murat: "Good. An army rots standing still."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   3,775 (+1,720 next turn)
   Inf:
   87,398
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, march to Normandy
   Murat begins march to Normandy. Route: Orleanais → Picardy → Artois → Normandy. Cavalry charges through Lorraine -> Orleanais. Murat: "Good. An army rots standing still."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Soult(1604,379)  Napoleon(1627,353)  Teulie(1947,575)  Dumonceau(1303,280)  Ney(1888,535)  Davout(1886,561)  Lannes(1942,528)  Deroy(1948,425)  Murat(1695,440)  ?(1551,403)  Castanos(1538,364)  ?(1483,366)  Moore(1490,287)  Massena(1910,601)  ?(2068,435)  ?(1923,347)  10k(1901,629)  ?(1857,434)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1684,411)  ?(1490,417)  10k(1910,659)
```

```
#0098  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0098_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 6 ended. Turn 7 begins!

Income: 2627g | Occupation: -52g | Contributions: -110g | Charges of Empire: -181g | Admiralty: -92g | Blockade: -368g | Upkeep: -1364g (incl. 324g campaign pay) | Other: +1531g | Net: +1991g | Spent: 600g | Treasury: 5,766g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 6
   BAVARIA / ──────────────────────────── / - Deroy moves to Franche-Comte / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2184 of 2185 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,766 (+1,801 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 2,107 men, at Tyrol and Munich.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Berthier reports that Bernadotte appears envious of Lannes's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from the Kingdom of Italy has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   ► land Dumonceau in Munster
   Dumonceau requests clarification...
   > land Dumonceau in Munster confirmed
   THE LANDING: Dumonceau slips past the British patrols and puts 6,500 men ashore at Munster (odds were 73 in 100).
   Your forces have taken Munster. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [2/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Dumonceau secures Munster. Stability set to 25. Order is maintained. 1 building damaged.
   ► recruit infantry in Artois
   + Soult recruits 3,000 infantry for Artois (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war) (×1.00 over the ordinance). Morale: 100% -> 94%
   Infantry pool: 90,398 -> 87,398
   [2/4 actions remaining]
   Responding to the Kingdom of Italy's proposal: declined
   The Kingdom of Italy's petition for relief is refused: loyalty −10 (96 → 86); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► Murat, march to Normandy
   Murat begins march to Normandy. Route: Orleanais → Picardy → Artois → Normandy. Cavalry charges through Lorraine -> Orleanais. Murat: "Good. An army rots standing still."
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 7 BEGINS
   ═══════════════════════════════════════
   Income: 2627g | Occupation: -52g | Contributions: -110g | Charges of Empire: -181g | Admiralty: -92g | Blockade: -368g | Other: +1531g | Upkeep: -1364g | Net: +1991g | Spent: 600g
   Treasury: 5,766g
   Actions refreshed: 4/4
   Crowded at Franche-Comte: Ney loses 274 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 237 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Deroy loses 168 troops to the press of 3 corps on one province's roads
   Supply shortage at Normandy: Soult loses 1,374 troops
   Supply shortage at Normandy: Napoleon loses 415 troops
   Supply shortage at Normandy: Castanos loses 600 troops
   Switzerland loyalty 90 (-2): satellite drift
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: OPEN_BORDERS → PEACE.
   Prussia declares war on Hanover — The Hanoverian Prize; declaring Hanover.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Bernadotte is on the wrong side of the frontier at Franconia, Sire — the ground changed hands under him. Berthier has put him on the road home to Rhineland; he has 3 turns of safe passage.
   Bernadotte is no nearer home — 2 marches still to go from Franconia, and 1 turn to spare on the safe passage before his corps is interned.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1394,357)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1942,451)  ?(1959,325)  Brunswick(1958,287)  ?(1859,472)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Teulie(1947,595)  Dumonceau(1303,280)  Ney(1800,497)  Lannes(1813,471)  Deroy(1825,445)  Davout(1901,535)  Murat(1695,440)  Soult(1539,399)  Napoleon(1550,373)  Castanos(1563,347)  ?(1482,366)  Moore(1482,328)  Wellesley(1498,302)  Massena(1910,621)  ?(2068,435)  ?(1976,376)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1684,411)  ?(1490,417)  10k(1910,649)
```

```
#0099  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0099_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   DAVOUT REPORTS
   "Davout: 'Cannon fire at Munich, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'"
   controls: [March to the Guns]  [Continue as Ordered]  [Hold Position]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Napoleon arrived (x2) @(3435,64)]  [icon: Soult arrived (x2) @(3477,64)]  [icon: Blockade — Britain closes our ports @(3519,64)]  [icon: Massena arrived @(3561,64)]  [+18]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Munster
   +4 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 3t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1921 of 1921 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,766 (+1,801 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   ► land Dumonceau in Munster
   Dumonceau requests clarification...
   > land Dumonceau in Munster confirmed
   THE LANDING: Dumonceau slips past the British patrols and puts 6,500 men ashore at Munster (odds were 73 in 100).
   Your forces have taken Munster. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [2/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Dumonceau secures Munster. Stability set to 25. Order is maintained. 1 building damaged.
   ► recruit infantry in Artois
   + Soult recruits 3,000 infantry for Artois (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war) (×1.00 over the ordinance). Morale: 100% -> 94%
   Infantry pool: 90,398 -> 87,398
   [2/4 actions remaining]
   Responding to the Kingdom of Italy's proposal: declined
   The Kingdom of Italy's petition for relief is refused: loyalty −10 (96 → 86); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► Murat, march to Normandy
   Murat begins march to Normandy. Route: Orleanais → Picardy → Artois → Normandy. Cavalry charges through Lorraine -> Orleanais. Murat: "Good. An army rots standing still."
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 7 BEGINS
   ═══════════════════════════════════════
   Income: 2627g | Occupation: -52g | Contributions: -110g | Charges of Empire: -181g | Admiralty: -92g | Blockade: -368g | Other: +1531g | Upkeep: -1364g | Net: +1991g | Spent: 600g
   Treasury: 5,766g
   Actions refreshed: 4/4
   Crowded at Franche-Comte: Ney loses 274 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 237 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Deroy loses 168 troops to the press of 3 corps on one province's roads
   Supply shortage at Normandy: Soult loses 1,374 troops
   Supply shortage at Normandy: Napoleon loses 415 troops
   Supply shortage at Normandy: Castanos loses 600 troops
   Switzerland loyalty 90 (-2): satellite drift
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: OPEN_BORDERS → PEACE.
   Prussia declares war on Hanover — The Hanoverian Prize; declaring Hanover.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Bernadotte is on the wrong side of the frontier at Franconia, Sire — the ground changed hands under him. Berthier has put him on the road home to Rhineland; he has 3 turns of safe passage.
   Bernadotte is no nearer home — 2 marches still to go from Franconia, and 1 turn to spare on the safe passage before his corps is interned.
   --- Strategic Order Updates ---
   Lannes: Lannes arrives at Franche-Comte. Lannes: "Accomplished. The men want a battle, not another road."
   Murat: Murat is marching to Normandy (2 turns remaining).
   Napoleon: Napoleon arrives at Normandy.
   Normandy feeds 22,500; the 23,904 men standing there would lose ~106 a turn to short supply.
   Ney: Ney arrives at Franche-Comte.
   Franche-Comte feeds 52,500; the 34,052 men standing there would lose ~511 a turn to crowding — too many corps on one province. Ney: "Done — and I trust the next order has more fire in it."
   Soult: The order was "Soult, march to Normandy". Soult arrives at Normandy.
   Normandy feeds 22,500; the 56,254 men standing there would lose ~1,789 a turn to short supply. I await further instruction.
   Davout: Davout: 'Cannon fire at Munich, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'
   Davout awaits your orders!
map: unchanged (60 labels)
```

```
#0100  click Continue as Ordered  ->  ok
  (clicked at (1829, 562))
view: <run>\frames\0100_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1961 of 1961 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,766 (+1,801 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Davout: Davout: 'Cannon fire at Munich, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'
   Davout awaits your orders!
   > Davout: continue order
   Davout reluctantly continues his march, ignoring cannon fire at Munich. Davout arrives at Franche-Comte.
   Franche-Comte feeds 52,500; the 50,873 men standing there would lose ~1,277 a turn to crowding — too many corps on one province. Davout: "Done, and done properly — no stragglers, no surprises."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 7
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Paget has crossed into Gascony. No French corps stands in his path.
   • Sire — Leon has been taken by Britain.
   • Sire — Bernadotte is no nearer home, and the safe passage leaves one turn to spare. After that his corps will be interned where it stands.
   • Sire — Prussia would now join a league against us — relations −25. A league stands declared without her; she would march in the next — the price to keep her out: Talleyrand brings her to −10 in 2 turns (2 DP); buying off her design costs 1,272 gold.
   • Sire — St Petersburg now pays Vienna 200 gold a turn against us. The coalition has its paymaster; it lacks only its armies.
   SITUATION
   France holds 29 regions. Treasury: 5,766g (+1,991 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 27% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 30,976 — Awaiting orders.
   - Massena — Milan — 25,007 — Awaiting orders.
   ? Davout — Munich — 17,500 — HALTED at Munich — awaiting your word.
   > Murat — Orleanais — 15,386 — Moving to Normandy — 2 turns out.
   - Ney — Franche-Comte — 13,467 — Awaiting orders.
   - Lannes — Franche-Comte — 11,633 — Awaiting orders.
   > Bernadotte — Franconia — 10,049 — Moving to Rhineland — 2 turns out. Trust:40 Morale:45%
   - Napoleon — Normandy — 9,369 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   - Teulie — Tyrol — 5,774 — 3 turns idle.
   ⚠ Starving — supply has failed at Tyrol two turns running.
   INTELLIGENCE
   Deroy — Franche-Comte — 8,273 [confirmed]
   Castanos — Normandy — 13,520 [confirmed]
   Archduke Charles — Swabia — substantial force [partial]
   Moore — London — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Wellesley — London — small force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 2,300 men, at Franche-Comte and Normandy.
   Switzerland loyalty 90 (-2): satellite drift
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LANDING: Dumonceau has put 6,500 men ashore at Munster.
   Leon passes from Spain to Britain.
   Intelligence reports Britain has raised Wellesley to high command.
   Franconia passes from Bavaria to Austria.
   Bernadotte stands on Franconia, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   Swabia passes from Bavaria to Austria.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Intelligence reports Spain has raised Cuesta to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   Prussia has declared war on Hanover.
   THE CAMP: France has massed 40,345 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
   The court of Bavaria takes up a new design: its own survival.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Prussia have worsened significantly (-15 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+4)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1394,357)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1942,451)  ?(1959,325)  Brunswick(1958,287)  ?(1859,472)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Teulie(1947,595)  Dumonceau(1303,280)  Ney(1800,497)  Davout(1801,471)  Lannes(1825,445)  Deroy(1825,419)  Murat(1695,440)  Soult(1539,399)  Napoleon(1550,373)  Castanos(1563,347)  ?(1482,366)  Moore(1482,328)  Wellesley(1498,302)  Massena(1910,621)  ?(2068,435)  ?(1976,376)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1684,411)  ?(1490,417)  10k(1910,649)
```

```
#0101  type what if Ney attacks Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0101_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: ok Ney stands at Franche-Comte, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2048 of 2048 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,766 (+2,005 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► what if Ney attacks Paget
   Ney stands at Franche-Comte, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
map: unchanged (60 labels)
```

```
#0102  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0102_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Davout arrived @(3393,64)]  [icon: Napoleon arrived (x2) @(3435,64)]  [icon: Soult arrived (x2) @(3477,64)]  [icon: Blockade — Britain closes our ports @(3519,64)]  [icon: Massena arrived @(3561,64)]  [+19]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +4 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 3t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2115 of 2115 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,766 (+1,780 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0103  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0103_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2115 of 2115 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► what if Ney attacks Paget
   Ney stands at Franche-Comte, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0104  scroll 1700 600 down 5  ->  ok
  (scrolled down 5 at (1700, 600))
view: <run>\frames\0104_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 225 of 751 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (10)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -74 (Hostile)]  [Prussia  —  Open Borders  |  -25 (Wary)]  [Spain  —  Alliance  |  +34 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -14 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2115 of 2115 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► what if Ney attacks Paget
   Ney stands at Franche-Comte, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0105  click Prussia  ->  ok
  (clicked at (1825, 523))
view: <run>\frames\0105_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 266 px, 0 of 553 px] ──
   THE CABINET — Prussia
   DP: 6
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Open Borders   Relation: -25 (Wary) /  / "Our borders with Prussia are open, but trust remains shallow. A non-aggression pact would formalize the thaw." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Prussia stands on the Emperor's roads, Sire — The Pr …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [↳ 400g a turn]  [Buy Off Their Design (1272g) (1 DP + 1272g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2115 of 2115 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► what if Ney attacks Paget
   Ney stands at Franche-Comte, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (60 labels)
```

```
#0106  click Licence  ->  ok
  (clicked at (1825, 554))
view: <run>\frames\0106_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Davout arrived @(3393,64)]  [icon: Napoleon arrived (x2) @(3435,64)]  [icon: Soult arrived (x2) @(3477,64)]  [icon: Blockade — Britain closes our ports @(3519,64)]  [icon: Massena arrived @(3561,64)]  [+19]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2226 of 2226 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,766 (+1,780 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► sponsor Prussia against Hanover, 0 gold
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (60 labels)
```

```
#0107  click 46 sail  ->  ok
  (clicked at (2976, 18))
view: <run>\frames\0107_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 948 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late December 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 46 sail of the line — readiness 50  (Adm. Villeneuve) /   Posture: guarding home waters — pinned in port by Britain /   Britain's blockade rots her crews 5 a turn at anchor, to 50 — the blockade lifts as the  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in Wales>  <Land Dumonceau in Midlands>  <Land Dumonceau in Northumbria>  <Land Dumonceau in Cornwall>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► sponsor Prussia against Hanover, 0 gold
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (60 labels)
```

```
#0108  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0108_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +4 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 3t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2226 of 2226 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► sponsor Prussia against Hanover, 0 gold
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (60 labels)
```

```
#0109  type lay down another ship of the line  ->  ok
  (typed and Enter)
view: <run>\frames\0109_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais (400g). The fleet stands at 47 sail — readiness 50 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing), and Britain's blockade rots her 5 a turn at anchor — the blockade lifts as the enemy squadrons come home to the camp; readiness then recovers +5/turn to 75. 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 5/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 47 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Davout arrived @(3393,64)]  [icon: Napoleon arrived (x2) @(3435,64)]  [icon: Soult arrived (x2) @(3477,64)]  [icon: Blockade — Britain closes our ports @(3519,64)]  [icon: Massena arrived @(3561,64)]  [+19]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1740 of 1741 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   5,366 (+1,795 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   > Murat — Orleanais — 15,386 — Moving to Normandy — 2 turns out.
   - Ney — Franche-Comte — 13,467 — Awaiting orders.
   - Lannes — Franche-Comte — 11,633 — Awaiting orders.
   > Bernadotte — Franconia — 10,049 — Moving to Rhineland — 2 turns out. Trust:40 Morale:45%
   - Napoleon — Normandy — 9,369 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   - Teulie — Tyrol — 5,774 — 3 turns idle.
   ⚠ Starving — supply has failed at Tyrol two turns running.
   INTELLIGENCE
   Deroy — Franche-Comte — 8,273 [confirmed]
   Castanos — Normandy — 13,520 [confirmed]
   Archduke Charles — Swabia — substantial force [partial]
   Moore — London — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Wellesley — London — small force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 2,300 men, at Franche-Comte and Normandy.
   Switzerland loyalty 90 (-2): satellite drift
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LANDING: Dumonceau has put 6,500 men ashore at Munster.
   Leon passes from Spain to Britain.
   Intelligence reports Britain has raised Wellesley to high command.
   Franconia passes from Bavaria to Austria.
   Bernadotte stands on Franconia, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   Swabia passes from Bavaria to Austria.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Intelligence reports Spain has raised Cuesta to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   Prussia has declared war on Hanover.
   THE CAMP: France has massed 40,345 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
   The court of Bavaria takes up a new design: its own survival.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Prussia have worsened significantly (-15 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+4)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► what if Ney attacks Paget
   Ney stands at Franche-Comte, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► sponsor Prussia against Hanover, 0 gold
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► lay down another ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 47 sail — readiness 50 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing), and Britain's blockade rots her 5 a turn at anchor — the blockade lifts as the enemy squadrons come home to the camp; readiness then recovers +5/turn to 75. 0 more keels possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1394,357)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  47(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1942,451)  ?(1959,325)  Brunswick(1958,287)  ?(1859,472)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Teulie(1947,595)  Dumonceau(1303,280)  Ney(1800,497)  Davout(1801,471)  Lannes(1825,445)  Deroy(1825,419)  Murat(1695,440)  Soult(1539,399)  Napoleon(1550,373)  Castanos(1563,347)  ?(1482,366)  Moore(1482,328)  Wellesley(1498,302)  Massena(1910,621)  ?(2068,435)  ?(1976,376)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1684,411)  ?(1490,417)  10k(1910,649)
```

```
#0110  type Ney, attack Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0110_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
reply: ok Paget stands at Gascony, four marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Nivernais), or cancel?
── ClarificationPopup (layer 102) ──
   NEY ASKS:
   "Paget stands at Gascony, four marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Nivernais), or cancel?"
   controls: [Pursue Paget (2 AP)]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 47 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1808 of 1808 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   5,366 (+1,795 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Ney, attack Paget
   Ney requests clarification...
map: unchanged (60 labels)
```

```
#0111  click Pursue Paget  ->  ok
  (clicked at (1829, 476))
view: <run>\frames\0111_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 47 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Davout arrived @(3393,64)]  [icon: Napoleon arrived (x2) @(3435,64)]  [icon: Soult arrived (x2) @(3477,64)]  [icon: Blockade — Britain closes our ports @(3519,64)]  [icon: Massena arrived @(3561,64)]  [+19]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +4 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 3t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1917 of 1917 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   5,366 (+1,795 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   > Ney, attack Paget
   Ney pursues Paget (at Gascony). Moves to Nivernais. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interrupt, and stands down if intelligence on him lapses. 'Ney, cancel' recalls him. Ney: "Run him to ground, then. My sabers are hungry."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1394,357)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  47(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1942,451)  ?(1959,325)  Brunswick(1958,287)  ?(1859,470)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Teulie(1947,595)  Dumonceau(1303,280)  Davout(1801,497)  Lannes(1813,471)  Deroy(1825,445)  Murat(1695,440)  Ney(1748,486)  Soult(1539,399)  Napoleon(1550,373)  Castanos(1563,347)  ?(1482,366)  Moore(1482,328)  Wellesley(1498,302)  Massena(1910,621)  ?(2068,435)  ?(1976,376)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1684,411)  ?(1490,417)  10k(1910,649)
```

```
#0112  type Teulie, march to Milan  ->  ok
  (typed and Enter)
view: <run>\frames\0112_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Teulie begins march to Milan. Moves to Milan. Teulie: "At the double, Sire — the men will smell powder soon enough."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2029 of 2029 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   5,366 (+1,795 next turn)
   Inf:
   89,135
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Teulie, march to Milan
   Teulie begins march to Milan. Moves to Milan. Teulie: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1394,357)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  47(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1942,451)  ?(1959,325)  Brunswick(1958,287)  ?(1859,470)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Dumonceau(1303,280)  Davout(1801,497)  Lannes(1813,471)  Deroy(1825,445)  Murat(1695,440)  Ney(1748,486)  Soult(1539,399)  Napoleon(1550,373)  Castanos(1563,347)  ?(1482,366)  Moore(1482,328)  Wellesley(1498,302)  Massena(1898,595)  Teulie(1922,538)  ?(2068,435)  ?(1976,376)  10k(1901,623)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1684,411)  ?(1490,417)  10k(1910,654)
```

```
#0113  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0113_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 7 ended. Turn 8 begins!

Income: 2627g | Occupation: -52g | Contributions: -150g | Charges of Empire: -354g | Admiralty: -94g | Upkeep: -1124g (incl. 108g campaign pay) | Other: +1310g | Net: +2163g | Spent: 400g | Treasury: 7,529g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 7
   BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 47 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2053 of 2055 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,529 (+1,943 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   THE LANDING: Dumonceau has put 6,500 men ashore at Munster.
   Leon passes from Spain to Britain.
   Intelligence reports Britain has raised Wellesley to high command.
   Franconia passes from Bavaria to Austria.
   Bernadotte stands on Franconia, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   Swabia passes from Bavaria to Austria.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Intelligence reports Spain has raised Cuesta to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   Prussia has declared war on Hanover.
   THE CAMP: France has massed 40,345 men on the invasion coast. Britain has seen it — expect the fleet home to guard the water.
   REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
   The court of Bavaria takes up a new design: its own survival.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Prussia have worsened significantly (-15 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+4)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► what if Ney attacks Paget
   Ney stands at Franche-Comte, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► sponsor Prussia against Hanover, 0 gold
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► lay down another ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 47 sail — readiness 50 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing), and Britain's blockade rots her 5 a turn at anchor — the blockade lifts as the enemy squadrons come home to the camp; readiness then recovers +5/turn to 75. 0 more keels possible this turn.
   [4/4 actions remaining]
   ► Ney, attack Paget
   Ney requests clarification...
   > Ney, attack Paget
   Ney pursues Paget (at Gascony). Moves to Nivernais. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interrupt, and stands down if intelligence on him lapses. 'Ney, cancel' recalls him. Ney: "Run him to ground, then. My sabers are hungry."
   [2/4 actions remaining]
   ► Teulie, march to Milan
   Teulie begins march to Milan. Moves to Milan. Teulie: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 8 BEGINS
   ═══════════════════════════════════════
   Income: 2627g | Occupation: -52g | Contributions: -150g | Charges of Empire: -354g | Admiralty: -94g | Other: +1310g | Upkeep: -1124g | Net: +2163g | Spent: 400g
   Treasury: 7,529g
   Actions refreshed: 4/4
   Crowded at Franche-Comte: Davout loses 350 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 232 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Deroy loses 165 troops to the press of 3 corps on one province's roads
   Supply shortage at Normandy: Soult loses 1,267 troops
   Supply shortage at Normandy: Napoleon loses 383 troops
   Supply shortage at Normandy: Castanos loses 553 troops
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Teulie's contingent comes home crowned with victory — 5,717 of 7,500 men. The Kingdom of Italy rejoices (+8 loyalty).
   Britain subsidizes Russia with 300 gold.
   Bernadotte's resentment of Lannes has cooled with time.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Bernadotte is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 2 turns of safe passage.
   Bernadotte is no nearer home — 1 march still to go from Swabia, and 1 turn to spare on the safe passage before his corps is interned.
   Berthier: Enemy forces spotted near Paris! Paget (4,613 troops) at Berry.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  47(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Murat(1616,379)  Bernadotte(1846,464)  Archduke Charles(1871,438)  Dumonceau(1303,280)  Davout(1801,497)  Lannes(1813,521)  Deroy(1825,412)  Ney(1748,486)  Soult(1539,399)  Napoleon(1542,373)  Castanos(1563,347)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  10k(1901,623)  ?(1893,372)  25k(1595,486)  12k(1575,454)  ?(1769,580)  7k(1777,335)  ?(1755,420)  12k(1711,420)  ?(1490,417)  10k(1910,654)
```

```
#0114  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0114_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 47 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3351,64)]  [icon: A Moment of History: The Bavarian Match @(3393,64)]  [icon: Prussia Declares War! @(3435,64)]  [icon: Davout arrived @(3477,64)]  [icon: Teulie arrived @(3519,64)]  [icon: Napoleon arrived (x2) @(3561,64)]  [+21]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +3 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 2t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2225 of 2225 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,529 (+1,943 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Supply shortage at Normandy: Soult loses 1,267 troops
   Supply shortage at Normandy: Napoleon loses 383 troops
   Supply shortage at Normandy: Castanos loses 553 troops
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Teulie's contingent comes home crowned with victory — 5,717 of 7,500 men. The Kingdom of Italy rejoices (+8 loyalty).
   Britain subsidizes Russia with 300 gold.
   Bernadotte's resentment of Lannes has cooled with time.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Bernadotte is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 2 turns of safe passage.
   Bernadotte is no nearer home — 1 march still to go from Swabia, and 1 turn to spare on the safe passage before his corps is interned.
   Berthier: Enemy forces spotted near Paris! Paget (4,613 troops) at Berry.
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte marches to Swabia. 1 region to Rhineland.
   Murat: Murat marches to Artois. 1 region to Normandy.
   Ney: Ney is pursuing Paget.
   Teulie: Teulie arrives at Milan. Teulie: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 8
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Paget has crossed into Berry. No French corps stands in his path.
   • Sire — Bernadotte is no nearer home, and the safe passage leaves one turn to spare. After that his corps will be interned where it stands.
   • Sire — Soult and Napoleon stand 38,695 men at Normandy, which feeds 22,500. 16,195 too many. 3,439 men lost in 2 turns. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 75,000 more and Maine can feed 52,500 more — a corps marched there ends it.
   • Sire — St Petersburg now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design costs 1,368 gold.
   SITUATION
   France holds 29 regions. Treasury: 7,529g (+2,163 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 29% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 29,709 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy two turns running.
   - Massena — Milan — 25,007 — Awaiting orders.
   - Davout — Franche-Comte — 17,150 — Awaiting orders.
   > Murat — Artois — 15,386 — Moving to Normandy — arrives next turn.
   > Ney — Nivernais — 13,467 — Pursuing Paget.
   - Lannes — Franche-Comte — 11,401 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   > Bernadotte — Swabia — 9,949 — Moving to Franche-Comte — arrives next turn. Trust:40 Morale:45%
   - Napoleon — Normandy — 8,986 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy two turns running.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franche-Comte — 8,108 [confirmed]
   Archduke Charles — Swabia — 20,712 [confirmed]
   Castanos — Normandy — 12,967 [confirmed]
   Moore — London — substantial force [partial]
   Paget — Berry — screening force [partial]
   Wellesley — London — small force [partial]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 2,232 men, at Franche-Comte and Normandy.
   Bernadotte's resentment of Lannes has cooled with time.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Brunswick passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Teulie's contingent comes home crowned with victory — 5,717 of 7,500 men. The Kingdom of Italy rejoices (+8 loyalty).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+3)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0115  click 47 sail  ->  ok
  (clicked at (3033, 18))
view: <run>\frames\0115_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 772 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early January 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 47 sail of the line — readiness 55  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: Staged: 54,081 men have stood 3  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in Wales>  <Land Dumonceau in Midlands>  <Land Dumonceau in Northumbria>  <Land Dumonceau in Cornwall>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2225 of 2225 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0116  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0116_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +3 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 2t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2225 of 2225 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0117  type lay down two ships of the line at Bordelais  ->  ok
  (typed and Enter)
view: <run>\frames\0117_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: ok A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 48 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
── IncomingProposalPopup (layer 112) ──
   A MOMENT OF HISTORY — Early January 1806 / The Bavarian Match — The Cabinet lays a letter before the Emperor. / A moment of history, Sire: a decision the record sets before you — two answers, each priced below, or Not Now to set it aside. It waits this turn and the next; left unanswered, it takes the second answer for you. / Eugène, adopted by Napoleon, wed Augusta of Bavaria at Munich (historical …
   controls: [Seal the match]  [Let Baden keep her]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 48 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1761 of 1762 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   7,129 (+1,960 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   Sire — Paget has crossed into Berry. No French corps stands in his path.
   • Sire — Bernadotte is no nearer home, and the safe passage leaves one turn to spare. After that his corps will be interned where it stands.
   • Sire — Soult and Napoleon stand 38,695 men at Normandy, which feeds 22,500. 16,195 too many. 3,439 men lost in 2 turns. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 75,000 more and Maine can feed 52,500 more — a corps marched there ends it.
   • Sire — St Petersburg now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design costs 1,368 gold.
   SITUATION
   France holds 29 regions. Treasury: 7,529g (+2,163 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 29% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 29,709 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy two turns running.
   - Massena — Milan — 25,007 — Awaiting orders.
   - Davout — Franche-Comte — 17,150 — Awaiting orders.
   > Murat — Artois — 15,386 — Moving to Normandy — arrives next turn.
   > Ney — Nivernais — 13,467 — Pursuing Paget.
   - Lannes — Franche-Comte — 11,401 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   > Bernadotte — Swabia — 9,949 — Moving to Franche-Comte — arrives next turn. Trust:40 Morale:45%
   - Napoleon — Normandy — 8,986 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy two turns running.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franche-Comte — 8,108 [confirmed]
   Archduke Charles — Swabia — 20,712 [confirmed]
   Castanos — Normandy — 12,967 [confirmed]
   Moore — London — substantial force [partial]
   Paget — Berry — screening force [partial]
   Wellesley — London — small force [partial]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 2,232 men, at Franche-Comte and Normandy.
   Bernadotte's resentment of Lannes has cooled with time.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Brunswick passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Teulie's contingent comes home crowned with victory — 5,717 of 7,500 men. The Kingdom of Italy rejoices (+8 loyalty).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+3)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► lay down two ships of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 48 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  48(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Murat(1616,379)  Bernadotte(1846,464)  Archduke Charles(1871,438)  Dumonceau(1303,280)  Davout(1801,497)  Lannes(1813,521)  Deroy(1825,412)  Ney(1748,486)  Soult(1539,399)  Napoleon(1542,373)  Castanos(1563,347)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  10k(1901,623)  ?(1893,372)  25k(1595,486)  12k(1575,454)  ?(1769,580)  7k(1777,335)  ?(1755,420)  12k(1711,420)  ?(1490,417)  10k(1910,654)
```

```
#0118  click Let Baden keep her  ->  ok
  (clicked at (1828, 687))
view: <run>\frames\0118_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 48 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Davout arrived @(3435,64)]  [icon: Teulie arrived @(3477,64)]  [icon: Napoleon arrived (x2) @(3519,64)]  [icon: Soult arrived (x2) @(3561,64)]  [+20]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +3 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 2t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1828 of 1828 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   7,129 (+1,960 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Answering The Bavarian Match: Let Baden keep her
   The Bavarian Match — Let Baden keep her: Bavaria's goodwill 53 → 48.
map: unchanged (59 labels)
```

```
#0119  type lay down a ship of the line  ->  ok
  (typed and Enter)
view: <run>\frames\0119_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais (400g). The fleet stands at 49 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Davout arrived @(3435,64)]  [icon: Teulie arrived @(3477,64)]  [icon: Napoleon arrived (x2) @(3519,64)]  [icon: Soult arrived (x2) @(3561,64)]  [+20]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1961 of 1961 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   6,729 (+1,976 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 49 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 0 more keels possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  49(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Murat(1616,379)  Bernadotte(1846,464)  Archduke Charles(1871,438)  Dumonceau(1303,280)  Davout(1801,497)  Lannes(1813,521)  Deroy(1825,412)  Ney(1748,486)  Soult(1539,399)  Napoleon(1542,373)  Castanos(1563,347)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  10k(1901,623)  ?(1893,372)  25k(1595,486)  12k(1575,454)  ?(1769,580)  7k(1777,335)  ?(1755,420)  12k(1711,420)  ?(1490,417)  10k(1910,654)
```

```
#0120  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0120_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 5 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: No administrative action remains this turn — the summons is an act of state.)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1961 of 1961 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   The Bavarian Match — Let Baden keep her: Bavaria's goodwill 53 → 48.
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 49 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 0 more keels possible this turn.
   [4/4 actions remaining]
map: unchanged (59 labels)
```

```
#0121  scroll 1700 600 down 5  ->  ok
  (scrolled down 5 at (1700, 600))
view: <run>\frames\0121_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 225 of 751 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (10)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -71 (Hostile)]  [Prussia  —  Open Borders  |  -19 (Wary)]  [Spain  —  Alliance  |  +33 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -13 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1961 of 1961 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   The Bavarian Match — Let Baden keep her: Bavaria's goodwill 53 → 48.
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 49 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 0 more keels possible this turn.
   [4/4 actions remaining]
map: unchanged (59 labels)
```

```
#0122  click Austria  ->  ok
  (clicked at (1825, 483))
view: <run>\frames\0122_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 233 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Munster   Relation: -71 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Sire, the truce with Austria has 2 turns to run and the ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 7 turns old  …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1961 of 1961 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   The Bavarian Match — Let Baden keep her: Bavaria's goodwill 53 → 48.
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 49 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 0 more keels possible this turn.
   [4/4 actions remaining]
map: unchanged (59 labels)
```

```
#0123  scroll 1700 560 down 4  ->  ok
  (scrolled down 4 at (1700, 560))
view: <run>\frames\0123_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 103 of 249 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Munster   Relation: -71 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Sire, the truce with Austria has 2 turns to run and the ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 7 turns old  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Peace (2 DP)  —  Unlikely]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1961 of 1961 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   The Bavarian Match — Let Baden keep her: Bavaria's goodwill 53 → 48.
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 49 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 0 more keels possible this turn.
   [4/4 actions remaining]
map: unchanged (59 labels)
```

```
#0124  click Improve Relations  ->  ok
  (clicked at (1825, 607))
view: <run>\frames\0124_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Austria /  / "Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2006 of 2006 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   6,729 (+1,976 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► improve relations with Austria
map: unchanged (59 labels)
```

```
#0125  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0125_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Davout arrived @(3435,64)]  [icon: Teulie arrived @(3477,64)]  [icon: Napoleon arrived (x2) @(3519,64)]  [icon: Soult arrived (x2) @(3561,64)]  [+21]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +3 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 2t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2072 of 2072 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   6,729 (+1,976 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (59 labels)
```

```
#0126  type Murat, cancel  ->  ok
  (typed and Enter)
view: <run>\frames\0126_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Berthier adjusts his spectacles. "Sire, I understand this concerns Marshal Murat, but I cannot determine the order. Perhaps: 'Murat, attack Moore' or 'Murat, move to Paris'?"
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2182 of 2182 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   6,729 (+1,976 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, cancel
   Berthier adjusts his spectacles. "Sire, I understand this concerns Marshal Murat, but I cannot determine the order. Perhaps: 'Murat, attack Moore' or 'Murat, move to Paris'?"
map: unchanged (59 labels)
```

```
#0127  type Murat, halt  ->  ok
  (typed and Enter)
view: <run>\frames\0127_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat halts his march and awaits new orders.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2293 of 2293 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   3/4
   Admin:
   0/2
   Gold:
   6,729 (+1,976 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, halt
   Murat halts his march and awaits new orders.
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0128  type Napoleon, march to Artois  ->  ok
  (typed and Enter)
view: <run>\frames\0128_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon begins march to Artois. Moves to Artois. (1 AP — the Emperor commands in his own name.)
── TopBar (layer 75) ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The blockade on our ports lifts @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Davout arrived @(3435,64)]  [icon: Teulie arrived @(3477,64)]  [icon: Napoleon arrived (x2) @(3519,64)]  [icon: Soult arrived (x2) @(3561,64)]  [+21]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1765 of 1765 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   2/4
   Admin:
   0/2
   Gold:
   6,729 (+1,976 next turn)
   Inf:
   90,772
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   INTELLIGENCE
   Deroy — Franche-Comte — 8,108 [confirmed]
   Archduke Charles — Swabia — 20,712 [confirmed]
   Castanos — Normandy — 12,967 [confirmed]
   Moore — London — substantial force [partial]
   Paget — Berry — screening force [partial]
   Wellesley — London — small force [partial]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 2,232 men, at Franche-Comte and Normandy.
   Bernadotte's resentment of Lannes has cooled with time.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Brunswick passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Teulie's contingent comes home crowned with victory — 5,717 of 7,500 men. The Kingdom of Italy rejoices (+8 loyalty).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+3)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► lay down two ships of the line at Bordelais
   A keel is laid at Bordelais — one fleet, whichever yard lays her keel (400g). The fleet stands at 48 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 1 more keel possible this turn.
   [4/4 actions remaining]
   Answering The Bavarian Match: Let Baden keep her
   The Bavarian Match — Let Baden keep her: Bavaria's goodwill 53 → 48.
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 49 sail — readiness 55 (new crews come aboard green at 40, but she is green enough already — this keel cost her nothing). 0 more keels possible this turn.
   [4/4 actions remaining]
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
   ► Murat, cancel
   Berthier adjusts his spectacles. "Sire, I understand this concerns Marshal Murat, but I cannot determine the order. Perhaps: 'Murat, attack Moore' or 'Murat, move to Paris'?"
   ► Murat, halt
   Murat halts his march and awaits new orders.
   [3/4 actions remaining]
   ► Napoleon, march to Artois
   Napoleon begins march to Artois. Moves to Artois. (1 AP — the Emperor commands in his own name.)
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  49(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Murat(1604,379)  Napoleon(1620,353)  Bernadotte(1846,464)  Archduke Charles(1871,438)  Dumonceau(1303,280)  Davout(1801,497)  Lannes(1813,521)  Deroy(1825,412)  Ney(1748,486)  Soult(1539,399)  Castanos(1563,425)  ?(1482,371)  Moore(1482,344)  ?(1510,371)  Wellesley(1498,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  10k(1901,623)  ?(1893,372)  25k(1595,486)  12k(1575,454)  ?(1769,580)  7k(1777,335)  ?(1755,420)  12k(1711,420)  ?(1490,417)  10k(1910,654)
```

```
#0129  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0129_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!

Income: 2702g | Occupation: -30g | Contributions: -110g | Charges of Empire: -512g | Admiralty: -98g | Upkeep: -1008g | Other: +1290g | Net: +2234g | Spent: 800g | Treasury: 8,963g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 69 px] ──
   ENEMY PHASE - Turn 8
   BRITAIN / ──────────────────────────── / - Moore abandons fortified position / - Moore holds position / - Wellesley recruits troops (Irreplaceable, ×1.25) / - Wellesley recruits troops (Irreplaceable, ×1.25) /  / SPAIN / ──────────────────────────── / - Castanos abandons fortified position / - Castanos moves to Berry /  / BAVARIA / ──────────────────────────── / - Deroy holds position /  / ─────── …
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 89 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2274 of 2274 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,963 (+2,019 next turn)
   Inf:
   92,309
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 9 BEGINS
   ═══════════════════════════════════════
   Income: 2702g | Occupation: -30g | Contributions: -110g | Charges of Empire: -512g | Admiralty: -98g | Other: +1290g | Upkeep: -1008g | Net: +2234g | Spent: 800g
   Treasury: 8,963g
   Actions refreshed: 4/4
   Crowded at Franche-Comte: Davout loses 514 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 342 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Bernadotte loses 298 troops to the press of 4 corps on one province's roads
   Crowded at Franche-Comte: Deroy loses 243 troops to the press of 4 corps on one province's roads
   Supply shortage at Normandy: Soult loses 142 troops
   Garrison at Hanover reinforced: 0 -> 2,000
   Britain subsidizes Austria with 300 gold.
   Berthier notes that Soult no longer asks for a command — he no longer stands in the Emperor's shadow.
   Berthier reports that Soult appears envious of Bernadotte's laurels — he has thrown himself into his post with obsessive diligence.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 100(1396,395)  49(1354,613)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Castanos(1525,489)  Murat(1604,379)  Napoleon(1627,326)  ?(1859,470)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Dumonceau(1303,280)  Davout(1801,497)  Lannes(1800,471)  Bernadotte(1825,445)  Deroy(1825,419)  ?(1384,625)  Cuesta(1384,587)  Ney(1684,495)  Soult(1551,399)  Moore(1478,362)  Wellesley(1502,287)  Massena(1910,595)  ?(2068,435)  ?(1976,376)  10k(1901,623)  ?(1899,434)  25k(1595,486)  12k(1551,454)  ?(1769,580)  2k(1777,335)  12k(1716,420)  25k(1490,417)  10k(1910,654)
```

```
#0130  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0130_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 89 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived (x3) @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Settlement offer from Austria @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Marshal Soult seeks an audience @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+23]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +2 →
   T:8
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 1t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1960 of 1960 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,963 (+2,019 next turn)
   Inf:
   92,309
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte arrives at Franche-Comte.
   Franche-Comte feeds 52,500; the 46,608 men standing there would lose ~1,154 a turn to crowding — too many corps on one province. Bernadotte: "It is done. I took the liberty of posting pickets."
   Napoleon: Napoleon arrives at Artois.
   Ney: Ney pursues Paget. 2 regions away.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 9
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Soult stands 29,567 men at Normandy, which feeds 22,500. 7,067 too many. 3,581 men lost in 3 turns. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 75,000 more and Maine can feed 52,500 more — a corps marched there ends it.
   • Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
   • Sire — Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   SITUATION
   France holds 29 regions. Treasury: 8,963g (+2,234 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 42% of French forces (an estimate — 1 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 29,567 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy three turns running.
   - Massena — Milan — 25,007 — Awaiting orders.
   - Davout — Franche-Comte — 16,636 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Murat — Artois — 15,386 — Awaiting orders.
   > Ney — Burgundy — 13,467 — Pursuing Paget — 2 turns behind him.
   - Lannes — Franche-Comte — 11,059 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,986 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franche-Comte — 7,865 [confirmed]
   Moore — London — 30,000 [confirmed]
   Castanos — Berry — 12,838 [confirmed]
   Wellesley — London — 25,000 [confirmed]
   Archduke Charles — Swabia — substantial force [partial]
   Paget — Gascony — screening force [partial]
   Cuesta — Bordelais — small force [partial]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Supply cost you 1,296 men, at Franche-Comte and Normandy.
   Berthier notes that Soult no longer asks for a command — he no longer stands in the Emperor's shadow.
   Berthier reports that Soult appears envious of Bernadotte's laurels — he has thrown himself into his post with obsessive diligence.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Intelligence reports Austria has raised Hiller to high command.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Austria, for Britain, Austria and Russia, has offered terms to settle the War for Munster — Britain + Austria + Russia. Offering 2410 gold. It also Austria's design pointed elsewhere: The Eastern Question (Albania, Ottoman Empire's), licensed by France.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -60.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Austria — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+2)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0131  click 49 sail  ->  ok
  (clicked at (2937, 18))
view: <run>\frames\0131_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late January 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 49 sail of the line — readiness 60  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: Staged: 53,939 men have stood 4 t …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in Wales>  <Land Dumonceau in Midlands>  <Land Dumonceau in Northumbria>  <Land Dumonceau in Cornwall>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0132  look  ->  ok
  (a fresh frame)
view: <run>\frames\0132_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0133  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0133_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +2 →
   T:8
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 1t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0134  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0134_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0135  click The Emperor's Designs  ->  ok
  (clicked at (1825, 502))
view: <run>\frames\0135_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 1920 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Your own aims, Sire, not the courts'. A road asks a construction, then a seal; hold both and the peace that seals it can be the Decisive Peace. Proclaiming costs 2 DP and 1 administrative action and cannot be undone.
   No road is proclaimed. Three roads — one proclamation, and it cannot be undone.
   Road I — The Protector of the Rhine (The Act of Confederation) /     ✓ Bavaria must stand with France /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Austria −10, Prussia −10. /     • The Confederation of the Rhine (the construction) — 0 of 3 courts under the Emperor's protection; to be held 4 end turns /         Three of Bavaria, Hesse, Saxon …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Proclaim Road I — The Act of Confederation]  [Proclaim Road II — The Schönbrunn Proclamation]  [Proclaim Road III — The Blockade of the British Isles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0136  scroll 1700 560 down 10  ->  ok
  (scrolled down 10 at (1700, 560))
view: <run>\frames\0136_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 379 of 1920 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Road I — The Protector of the Rhine (The Act of Confederation) /     ✓ Bavaria must stand with France /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Austria −10, Prussia −10. /     • The Confederation of the Rhine (the construction) — 0 of 3 courts under the Emperor's protection; to be held 4 end turns /         Three of Bavaria, Hesse, Saxon …
   Road II — The Crowns of Italy (The Schönbrunn Proclamation) /     ✓ the Kingdom of Italy must be France's /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Naples −10, Spain −10. /     • The Throne of Naples (the construction) — 0 of 1 province titled to the Empire /         Naples titled to the Empire — her court France's satellite at loyalty 4 …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [↳ Bavaria]  [↳ Hesse]  [↳ Saxony]  [↳ Hanover]  [↳ Austria]  [↳ Prussia]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0137  scroll 1700 560 down 15  ->  ok
  (scrolled down 15 at (1700, 560))
view: <run>\frames\0137_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 942 of 1920 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Road II — The Crowns of Italy (The Schönbrunn Proclamation) /     ✓ the Kingdom of Italy must be France's /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Naples −10, Spain −10. /     • The Throne of Naples (the construction) — 0 of 1 province titled to the Empire /         Naples titled to the Empire — her court France's satellite at loyalty 4 …
   Road III — The Continental System (The Blockade of the British Isles) /     ✓ France must be at war with the mistress of the seas /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Denmark −15, Portugal −15. /     • The Blockade of the British Isles (the construction) — 10 of 26 ports shut to Britain — 13 needed; to be held 6 end turns /          …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [↳ Naples]  [↳ Austria]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0138  scroll 1700 560 down 15  ->  ok
  (scrolled down 15 at (1700, 560))
view: <run>\frames\0138_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 1507 of 1955 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   The Temple of Glory (the decree of Posen, 2 December 1806) · any road /   The Madeleine rebuilt as a temple to the Grand Army — the names of the fallen on its walls, the Empire's glory made stone. /   8,000 gold and 1 administrative action, once — authority +15; the Charges of Empire fall by 777g a turn
   The Temple of Glory serves a road of the Empire, Sire — proclaim one first (F1 → The Emperor's Designs).
   The Princes' Dotations (1806) · Road I /   Domains and pensions for the German princes who sit in the Confederation — their crowns guaranteed, their loyalty bought. /   6,000 gold and 1 administrative action, once — relations: Hesse +20, Saxony +20; loyalty +15 for the Emperor's vassals among them (none yet); Europe's alarm +3; the Charges of Empire fall by 670g a turn
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Decree The Temple of Glory](disabled: The Temple of Glory serves a road of the Empire, Sire — proclaim one first (F1 → The Emper)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0139  scroll 1700 560 up 7  ->  ok
  (scrolled up 7 at (1700, 560))
view: <run>\frames\0139_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 1258 of 1932 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Road III — The Continental System (The Blockade of the British Isles) /     ✓ France must be at war with the mistress of the seas /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Denmark −15, Portugal −15. /     • The Blockade of the British Isles (the construction) — 10 of 26 ports shut to Britain — 13 needed; to be held 6 end turns /          …
   THE ACTS OF THE EMPIRE — gold for the road, each decreed once
   The Temple of Glory (the decree of Posen, 2 December 1806) · any road /   The Madeleine rebuilt as a temple to the Grand Army — the names of the fallen on its walls, the Empire's glory made stone. /   8,000 gold and 1 administrative action, once — authority +15; the Charges of Empire fall by 777g a turn
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [↳ Ottoman]  [↳ Denmark]  [↳ Portugal]  [↳ Russia]  [↳ Britain]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0140  click Proclaim Road III  ->  ERROR: no visible control's text holds "Proclaim Road III"
view: <run>\frames\0140_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 1258 of 1932 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0141  scroll 1700 560 up 30  ->  ok
  (scrolled up 30 at (1700, 560))
view: <run>\frames\0141_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 178 of 1920 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Road I — The Protector of the Rhine (The Act of Confederation) /     ✓ Bavaria must stand with France /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Austria −10, Prussia −10. /     • The Confederation of the Rhine (the construction) — 0 of 3 courts under the Emperor's protection; to be held 4 end turns /         Three of Bavaria, Hesse, Saxon …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Proclaim Road III — The Blockade of the British Isles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (60 labels)
```

```
#0142  click Proclaim Road III  ->  ok
  (clicked at (1723, 396))
view: <run>\frames\0142_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE CABINET ASKS:
   "The Blockade of the British Isles: The Continental System becomes the Empire's road — 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Denmark −15, Portugal −15. The Protector of the Rhine, The Crowns of Italy are forsworn, and this cannot be undone. Proclaim it? (yes / no)"
   controls: [Proclaim The Continental System]  [Not now]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 89 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,963 (+2,019 next turn)
   Inf:
   92,309
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► proclaim The Continental System
   The Cabinet requests clarification...
map: unchanged (60 labels)
```

```
#0143  click Proclaim The Continental System  ->  ok
  (clicked at (1829, 524))
view: <run>\frames\0143_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 112 px] ──
   SETTLEMENT OFFER FROM AUSTRIA /  / the War for Munster — Britain + Austria + Russia /  / "Vienna submits terms for the War for Munster — Britain + Austria + Russia with 2410 gold to close them. Metternich pays where another campaign would cost Austria more than coin." /  / Their proposed terms: /   • Peace /   • 2410 gold (Austria → France) /   • Compensation: Austria's design pointed elsewhere: T …
   controls: [Review Settlement Offer]  [Request Revision]  [Reject Offer]
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2202 of 2202 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   8,963 (+1,994 next turn)
   Inf:
   92,309
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > proclaim The Continental System confirmed
   The Blockade of the British Isles is proclaimed — The Continental System is the Empire's road, and the others are forsworn. Europe's alarm +8; relations: Denmark −15, Portugal −15. The Blockade of the British Isles: 13 of the Continent's 26 ports shut to Britain, held six end turns — a court at war with her, in the System by a peace's clause, France's satellite, or with her capital held by a power at war with her. Then The Peace of the Continent: After the Blockade, Britain signs a war-ending peace with France — a great power in the System by France's clause, no lifting clause, France's own pr
   [4/4 actions remaining]
map: unchanged (60 labels)
```

```
#0144  click Review Settlement Offer  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0144_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 376 px] ──
   Settlement of the War for Munster — the table with Austria + Britain + Russia — ready for ratification / the War for Munster — the table with Austria + Britain + Russia - Whole-war settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Austria, Britain, Russia / Will carry — these are the terms they offered. / Sire, this settlement of the Wa …
   The table /   * Austria - Their own terms Demanded: 2410g; Conceded: its design pointed at Albania /       Blocker: Term harshness /       Metternich for Austria: these are the terms Austria laid before France; Austria does not haggle with its own dispatch. /   * Britain - Their own terms White peace /       Blocker: Term harshness /       Castlereagh for Britain: these are the terms Britain laid  …
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry; the verdict beside each row is that court's own, and the terms before you stand as offered. / Sire, the settlement of the War for Munster — the table with Austria + Britain + Russia lies ready on the terms Britain themselves put on the table. Their consent is given; the signature is  …
   controls: [Ratify Settlement]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   8,963 (+1,994 next turn)
   Inf:
   92,309
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: accept settlement offer
map: unchanged (60 labels)
```

```
#0145  click Back Out  ->  ok
  (clicked at (1834, 969))
view: <run>\frames\0145_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived (x3) @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Marshal Soult seeks an audience @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Davout arrived @(3561,64)]  [+22]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +2 →
   T:8
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Austria, truce 1t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2291 of 2291 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   8,963 (+1,994 next turn)
   Inf:
   92,309
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: back out settlement
   Settlement review cancelled.
map: unchanged (60 labels)
```

```
#0146  type Davout, march to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0146_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout begins march to Rhineland. Route: Lorraine → Rhineland. Moves to Lorraine. Davout: "The roads will be scouted before each march, Sire."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1740 of 1740 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   8,963 (+1,994 next turn)
   Inf:
   92,309
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Davout — Franche-Comte — 16,636 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Murat — Artois — 15,386 — Awaiting orders.
   > Ney — Burgundy — 13,467 — Pursuing Paget — 2 turns behind him.
   - Lannes — Franche-Comte — 11,059 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,986 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franche-Comte — 7,865 [confirmed]
   Moore — London — 30,000 [confirmed]
   Castanos — Berry — 12,838 [confirmed]
   Wellesley — London — 25,000 [confirmed]
   Archduke Charles — Swabia — substantial force [partial]
   Paget — Gascony — screening force [partial]
   Cuesta — Bordelais — small force [partial]
   Brunswick — Berlin — large force [partial]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Supply cost you 1,296 men, at Franche-Comte and Normandy.
   Berthier notes that Soult no longer asks for a command — he no longer stands in the Emperor's shadow.
   Berthier reports that Soult appears envious of Bernadotte's laurels — he has thrown himself into his post with obsessive diligence.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Intelligence reports Austria has raised Hiller to high command.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Austria, for Britain, Austria and Russia, has offered terms to settle the War for Munster — Britain + Austria + Russia. Offering 2410 gold. It also Austria's design pointed elsewhere: The Eastern Question (Albania, Ottoman Empire's), licensed by France.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -60.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Austria — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+2)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   ► proclaim The Continental System
   The Cabinet requests clarification...
   > proclaim The Continental System confirmed
   The Blockade of the British Isles is proclaimed — The Continental System is the Empire's road, and the others are forsworn. Europe's alarm +8; relations: Denmark −15, Portugal −15. The Blockade of the British Isles: 13 of the Continent's 26 ports shut to Britain, held six end turns — a court at war with her, in the System by a peace's clause, France's satellite, or with her capital held by a power at war with her. Then The Peace of the Continent: After the Blockade, Britain signs a war-ending peace with France — a great power in the System by France's clause, no lifting clause, France's own pr
   [4/4 actions remaining]
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: back out settlement
   Settlement review cancelled.
   ► Davout, march to Rhineland
   Davout begins march to Rhineland. Route: Lorraine → Rhineland. Moves to Lorraine. Davout: "The roads will be scouted before each march, Sire."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 100(1396,395)  49(1354,613)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Castanos(1525,489)  Murat(1604,379)  Napoleon(1627,326)  ?(1879,469)  Archduke Charles(1875,376)  ?(1501,602)  Paget(1501,564)  Davout(1753,436)  Dumonceau(1303,280)  Lannes(1800,497)  Bernadotte(1812,471)  Deroy(1825,445)  ?(1384,625)  Cuesta(1384,587)  Ney(1684,495)  Soult(1551,399)  Moore(1478,362)  Wellesley(1502,287)  Massena(1910,595)  ?(2068,435)  ?(1976,376)  10k(1901,623)  ?(1893,434)  25k(1595,486)  12k(1551,454)  ?(1769,580)  2k(1777,335)  12k(1696,420)  25k(1490,417)  10k(1910,654)
```

```
#0147  type Lannes, march to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0147_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes begins march to Rhineland. Route: Lorraine → Rhineland. Moves to Lorraine. Lannes: "At the double, Sire — the men will smell powder soon enough."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   8,963 (+1,994 next turn)
   Inf:
   92,309
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, march to Rhineland
   Lannes begins march to Rhineland. Route: Lorraine → Rhineland. Moves to Lorraine. Lannes: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 100(1396,395)  49(1354,613)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Castanos(1525,489)  Murat(1604,379)  Napoleon(1627,326)  ?(1867,469)  Archduke Charles(1859,430)  ?(1501,602)  Paget(1501,564)  Davout(1741,436)  Lannes(1764,462)  Dumonceau(1303,280)  Bernadotte(1800,497)  Deroy(1825,471)  ?(1384,625)  Cuesta(1384,587)  Ney(1684,495)  Soult(1551,399)  Moore(1478,362)  Wellesley(1502,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  10k(1901,623)  ?(1893,372)  25k(1595,486)  12k(1551,454)  ?(1769,580)  2k(1777,335)  12k(1684,416)  25k(1490,417)  10k(1910,654)
```

```
#0148  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0148_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 9 ended. Turn 10 begins!

Income: 2675g | Occupation: -30g | Charges of Empire: -459g | Admiralty: -98g | Upkeep: -1008g | Other: +1319g | Net: +2399g | Treasury: 11,362g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 553 px] ──
   ENEMY PHASE - Turn 9
   BRITAIN / ──────────────────────────── / - Paget moves to Guyenne / - Moore holds position / - Wellesley recruits troops (Irreplaceable, ×1.25) / - Moore recruits troops (Irreplaceable, ×1.25) /  / SPAIN / ──────────────────────────── / - Castanos attacks Paget /     Battle of Guyenne /     Castanos: 619 casualties, 12,219 remaining /     Paget: 1,544 casualties, 2,932 remaining /     Result: Atta …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 95 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1810 of 1811 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,362 (+2,236 next turn)
   Inf:
   93,746
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Intelligence reports Austria has raised Hiller to high command.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Austria, for Britain, Austria and Russia, has offered terms to settle the War for Munster — Britain + Austria + Russia. Offering 2410 gold. It also Austria's design pointed elsewhere: The Eastern Question (Albania, Ottoman Empire's), licensed by France.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -60.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Austria — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+2)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   ► proclaim The Continental System
   The Cabinet requests clarification...
   > proclaim The Continental System confirmed
   The Blockade of the British Isles is proclaimed — The Continental System is the Empire's road, and the others are forsworn. Europe's alarm +8; relations: Denmark −15, Portugal −15. The Blockade of the British Isles: 13 of the Continent's 26 ports shut to Britain, held six end turns — a court at war with her, in the System by a peace's clause, France's satellite, or with her capital held by a power at war with her. Then The Peace of the Continent: After the Blockade, Britain signs a war-ending peace with France — a great power in the System by France's clause, no lifting clause, France's own pr
   [4/4 actions remaining]
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: back out settlement
   Settlement review cancelled.
   ► Davout, march to Rhineland
   Davout begins march to Rhineland. Route: Lorraine → Rhineland. Moves to Lorraine. Davout: "The roads will be scouted before each march, Sire."
   [2/4 actions remaining]
   ► Lannes, march to Rhineland
   Lannes begins march to Rhineland. Route: Lorraine → Rhineland. Moves to Lorraine. Lannes: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2675g | Occupation: -30g | Charges of Empire: -459g | Admiralty: -98g | Other: +1319g | Upkeep: -1008g | Net: +2399g
   Treasury: 11,362g
   Actions refreshed: 4/4
   Supply shortage at Normandy: Soult loses 139 troops
   Supply shortage at East Frisia: Brunswick loses 459 troops
   Garrison at Hanover reinforced: 2,000 -> 4,000
   The armistice between Austria and France has concluded. Peace declared — signed on the held line.
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Sweden grows.
   Peace concluded between Hanover and Prussia without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Massena's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  49(1374,600)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1583,294)  10(1111,753)  10(1927,239)  5(1804,784)  Paget(1522,499)  Murat(1604,379)  Napoleon(1627,353)  ?(1859,469)  Archduke Charles(1859,430)  Castanos(1422,574)  Cuesta(1446,548)  Davout(1741,436)  Lannes(1764,462)  Dumonceau(1303,280)  Bernadotte(1812,497)  ?(1901,537)  Deroy(1901,501)  Ney(1684,495)  Soult(1551,399)  ?(1647,318)  Brunswick(1646,279)  Moore(1478,362)  Wellesley(1502,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  ?(1901,623)  ?(1893,372)  25k(1595,486)  12k(1551,454)  ?(1769,580)  4k(1777,319)  12k(1684,416)  25k(1490,417)  10k(1910,654)
```

```
#0149  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0149_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   NEY REPORTS
   "Ney: 'Cannon fire at Franche-Comte, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'"
   controls: [March to the Guns]  [Continue as Ordered]  [Hold Position]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 95 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Britain binds Russia to the war @(3393,64)]  [icon: Napoleon arrived (x3) @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Marshal Soult seeks an audience @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+24]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Munster
   +1 →
   T:9
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1965 of 1965 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,362 (+2,236 next turn)
   Inf:
   93,746
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   --- Strategic Order Updates ---
   Davout: Davout is marching to Rhineland (1 turn remaining).
   Lannes: Lannes is marching to Rhineland (1 turn remaining).
   Ney: Ney: 'Cannon fire at Franche-Comte, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'
   Ney awaits your orders!
map: unchanged (61 labels)
```

```
#0150  click Envoys  ->  ERROR: no visible control's text holds "Envoys"
view: <run>\frames\0150_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1965 of 1965 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Davout: Davout is marching to Rhineland (1 turn remaining).
   Lannes: Lannes is marching to Rhineland (1 turn remaining).
   Ney: Ney: 'Cannon fire at Franche-Comte, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'
   Ney awaits your orders!
map: unchanged (61 labels)
```

```
#0151  click Continue as Ordered  ->  ok
  (clicked at (1829, 562))
view: <run>\frames\0151_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   SPAIN LOSSES
   BRITAIN LOSSES
   0
   0
   Castanos
   12,097 → 11,939
   ⚔
   Cuesta ◆
   Paget ◆
   7,791 → 7,620 → 7,544 after the advance
   2,932 → 182
   SECOND BATTLE OF GUYENNE
   click anywhere to skip ▸
   GUYENNE · TURN 9
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
   11,362 (+2,236 next turn)
   Inf:
   93,746
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Massena's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   --- Strategic Order Updates ---
   Davout: Davout is marching to Rhineland (1 turn remaining).
   Lannes: Lannes is marching to Rhineland (1 turn remaining).
   Ney: Ney: 'Cannon fire at Franche-Comte, Sire. Austria and Bavaria are at war; France is not in it. Investigate?'
   Ney awaits your orders!
   > Ney: continue order
   Ney reluctantly presses the pursuit, ignoring cannon fire at Franche-Comte. Ney pursues Paget. 1 region away.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — THE BLOCKADE OF THE BRITISH ISLES: the Emperor proclaims The Continental System the Empire's road — The Blockade of the British Isles, then The Peace of the Continent. The other roads are forsworn.
   • Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
   • Sire — 4 turns of famine at Normandy now. 3,720 men gone, and not one of them to the enemy. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 75,000 more and Maine can feed 52,500 more — a corps marched there ends it.
   SITUATION
   France holds 29 regions. Treasury: 11,362g (+2,399 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 55% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 29,428 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy four turns running.
   - Massena — Milan — 25,007 — 3 turns idle.
   > Davout — Lorraine — 16,636 — Moving to Rhineland — arrives next turn.
   - Murat — Artois — 15,386 — Awaiting orders.
   ? Ney — Burgundy — 13,467 — HALTED at Burgundy — awaiting your word.
   > Lannes — Lorraine — 11,059 — Moving to Rhineland — arrives next turn.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,986 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Moore — London — 40,000 [confirmed]
   Castanos — Guyenne — 11,939 [confirmed]
   Paget — Berry — 182 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Cuesta — Guyenne — 7,544 [confirmed]
   Deroy — Munich — substantial force [partial]
   Archduke Charles — Swabia — substantial force [partial]
   Brunswick — East Frisia — substantial force [partial]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Supply shortage at Normandy: Soult loses 139 troops
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Massena's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   Westphalia passes from Hanover to Prussia.
   East Frisia passes from Hanover to Prussia.
   Intelligence reports Spain has raised Blake to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -49.
   The armistice between Austria and France has concluded. Peace declared.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   The court of Prussia takes up a new design: Armed Neutrality.
   Relations with Austria have improved significantly (+11 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+1)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  49(1374,600)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1583,294)  10(1111,753)  10(1927,239)  5(1804,784)  Paget(1522,499)  Murat(1604,379)  Napoleon(1627,353)  ?(1859,469)  Archduke Charles(1859,430)  Castanos(1422,574)  Cuesta(1446,548)  Ney(1599,489)  Davout(1741,436)  Lannes(1764,462)  Dumonceau(1303,280)  Bernadotte(1812,497)  ?(1901,537)  Deroy(1901,501)  Soult(1551,399)  ?(1647,318)  Brunswick(1646,279)  Moore(1478,362)  Wellesley(1502,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  ?(1901,623)  ?(1893,372)  25k(1595,460)  12k(1551,454)  ?(1769,580)  4k(1777,319)  12k(1684,416)  25k(1490,417)  10k(1910,654)
```

```
#0152  look  ->  ok
  (a fresh frame)
view: <run>\frames\0152_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   SPAIN LOSSES
   BRITAIN LOSSES
   247
   2,065
   Castanos
   12,097 → 11,939
   ⚔
   Cuesta ◆
   Paget ◆
   7,791 → 7,620 → 7,544 after the advance
   2,932 → 182
   ROUTED
   SECOND BATTLE OF GUYENNE
   click anywhere to skip ▸
   GUYENNE · TURN 9
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0153  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0153_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
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
   11,362 (+2,236 next turn)
   Inf:
   93,746
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0154  click Close  ->  ERROR: no visible control's text holds "Close"
view: <run>\frames\0154_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0155  look  ->  ok
  (a fresh frame)
view: <run>\frames\0155_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0156  click 49 sail  ->  ok
  (clicked at (2920, 18))
view: <run>\frames\0156_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early February 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 49 sail of the line — readiness 65  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: Staged: 53,800 men have stood 5 …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in Wales>  <Land Dumonceau in Midlands>  <Land Dumonceau in Northumbria>  <Land Dumonceau in Cornwall>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0157  look  ->  ok
  (a fresh frame)
view: <run>\frames\0157_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0158  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0158_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +1 →
   T:9
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0159  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0159_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 789 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — Road III, The Continental System: The Blockade of the British Isles — 10 of 26 ports shut to Britain — 13 needed; The Peace of the Continent — Britain has not signed
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0160  click The Emperor's Designs  ->  ok
  (clicked at (1825, 522))
view: <run>\frames\0160_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 666 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "The Empire's road is proclaimed, Sire — The Continental System. It cannot be undone, and the other roads are forsworn."
   The Blockade of the British Isles was proclaimed on turn 9: The Continental System.
   Road III — The Continental System (The Blockade of the British Isles) /     ✓ Proclaimed — the Empire's road. /     • The Blockade of the British Isles (the construction) — 10 of 26 ports shut to Britain — 13 needed; to be held 6 end turns /         13 of the Continent's 26 ports shut to Britain, held six end turns — a court at war with her, in the System by a peace's clause, France's satellite, o …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0161  scroll 1700 560 down 30  ->  ok
  (scrolled down 30 at (1700, 560))
view: <run>\frames\0161_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 623 of 664 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "The Empire's road is proclaimed, Sire — The Continental System. It cannot be undone, and the other roads are forsworn."
   The Temple of Glory (the decree of Posen, 2 December 1806) · any road /   The Madeleine rebuilt as a temple to the Grand Army — the names of the fallen on its walls, the Empire's glory made stone. /   8,000 gold and 1 administrative action, once — authority +15; the Charges of Empire fall by 553g a turn
   The Princes' Dotations (1806) · Road I
   The Abolition of Feudalism (Naples, 2 August 1806) · Road II
   The Raft on the Niemen (25 June 1807) · Road III /   Two emperors on a raft midstream — the beaten court courted, not crushed, and asked to shut its ports against Britain. /   6,000 gold and 1 administrative action, once — relations +20 with the great power beaten; Europe's alarm +3; the Charges of Empire fall by 415g a turn
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Decree The Temple of Glory]  [Decree The Raft on the Niemen](disabled: The Raft on the Niemen needs a great power at war with the Empire beaten first (Russia, Pr)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0162  click Decree The Temple of Glory  ->  ok
  (clicked at (1825, 457))
view: <run>\frames\0162_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE CABINET ASKS:
   "The Temple of Glory (the decree of Posen, 2 December 1806): The Madeleine rebuilt as a temple to the Grand Army — the names of the fallen on its walls, the Empire's glory made stone. It costs 8,000 gold and 1 administrative action, once — authority +15. The treasury holds 11,362 gold; the Charges of Empire fall by 553g a turn. Decree it? (yes / no)"
   controls: [Decree The Temple of Glory]  [Not now]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 95 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1938 of 1938 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,362 (+2,236 next turn)
   Inf:
   93,746
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► decree The Temple of Glory
   The Cabinet requests clarification...
map: unchanged (61 labels)
```

```
#0163  click Decree The Temple of Glory  ->  ok
  (clicked at (1829, 524))
view: <run>\frames\0163_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 95 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Britain binds Russia to the war @(3393,64)]  [icon: Napoleon arrived (x3) @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Marshal Soult seeks an audience @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+24]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +1 →
   T:9
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   3,362 (+2,764 next turn)
   Inf:
   93,746
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   > decree The Temple of Glory confirmed
   The Temple of Glory is decreed — 8,000 gold paid, once and never again: authority +15. The road page: F1 → The Emperor's Designs.
   [4/4 actions remaining]
map: unchanged (61 labels)
```

```
#0164  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0164_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!

Income: 2670g | Occupation: -30g | Charges of Empire: -94g | Admiralty: -98g | Upkeep: -1008g | Other: +1324g | Net: +2764g | Spent: 8000g | Treasury: 6,126g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 10
   BRITAIN / ──────────────────────────── / - Moore fortifies position / - Wellesley abandons fortified position /  / SPAIN / ──────────────────────────── / - Castanos fortifies position /  / ──────────────────────────── / Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 93 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1698 of 1699 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,126 (+2,585 next turn)
   Inf:
   95,083
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   MARSHAL STATUS
   - Soult — Normandy — 29,428 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy four turns running.
   - Massena — Milan — 25,007 — 3 turns idle.
   > Davout — Lorraine — 16,636 — Moving to Rhineland — arrives next turn.
   - Murat — Artois — 15,386 — Awaiting orders.
   ? Ney — Burgundy — 13,467 — HALTED at Burgundy — awaiting your word.
   > Lannes — Lorraine — 11,059 — Moving to Rhineland — arrives next turn.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,986 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Moore — London — 40,000 [confirmed]
   Castanos — Guyenne — 11,939 [confirmed]
   Paget — Berry — 182 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Cuesta — Guyenne — 7,544 [confirmed]
   Deroy — Munich — substantial force [partial]
   Archduke Charles — Swabia — substantial force [partial]
   Brunswick — East Frisia — substantial force [partial]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Supply shortage at Normandy: Soult loses 139 troops
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Murat wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Massena's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   Westphalia passes from Hanover to Prussia.
   East Frisia passes from Hanover to Prussia.
   Intelligence reports Spain has raised Blake to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -49.
   The armistice between Austria and France has concluded. Peace declared.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   The court of Prussia takes up a new design: Armed Neutrality.
   Relations with Austria have improved significantly (+11 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+1)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
   ► decree The Temple of Glory
   The Cabinet requests clarification...
   > decree The Temple of Glory confirmed
   The Temple of Glory is decreed — 8,000 gold paid, once and never again: authority +15. The road page: F1 → The Emperor's Designs.
   [4/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2670g | Occupation: -30g | Charges of Empire: -94g | Admiralty: -98g | Other: +1324g | Upkeep: -1008g | Net: +2764g | Spent: 8000g
   Treasury: 6,126g
   Actions refreshed: 4/4
   Supply shortage at Normandy: Soult loses 135 troops
   Britain subsidizes Russia with 300 gold.
   Berthier notes that Soult no longer presses the matter — his quarrel with Bernadotte has cooled.
   Soult's resentment of Bernadotte has cooled with time.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  49(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1959,325)  Brunswick(1958,287)  Murat(1604,379)  Napoleon(1627,353)  Davout(1815,418)  Lannes(1838,376)  Castanos(1501,598)  Ney(1599,489)  Dumonceau(1303,280)  Bernadotte(1812,497)  ?(1901,537)  Deroy(1901,501)  Soult(1551,399)  Moore(1478,362)  Wellesley(1502,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  ?(1901,623)  ?(1893,434)  25k(1595,460)  12k(1513,436)  ?(1769,580)  ?(1777,319)  12k(1716,420)  25k(1467,417)  10k(1910,654)
```

```
#0165  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0165_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 93 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Lannes arrived (x2) @(3351,64)]  [icon: Ney arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Armistice Concluded @(3477,64)]  [icon: Britain binds Russia to the war @(3519,64)]  [icon: Napoleon arrived (x3) @(3561,64)]  [+23]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   0 →
   T:10
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 2120 of 2120 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,126 (+2,585 next turn)
   Inf:
   95,083
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The road is chosen, Sire, and every court has read it. The page in the Cabinet says what each design still asks."
   ════════════════════════════════════
   ► decree The Temple of Glory
   The Cabinet requests clarification...
   > decree The Temple of Glory confirmed
   The Temple of Glory is decreed — 8,000 gold paid, once and never again: authority +15. The road page: F1 → The Emperor's Designs.
   [4/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2670g | Occupation: -30g | Charges of Empire: -94g | Admiralty: -98g | Other: +1324g | Upkeep: -1008g | Net: +2764g | Spent: 8000g
   Treasury: 6,126g
   Actions refreshed: 4/4
   Supply shortage at Normandy: Soult loses 135 troops
   Britain subsidizes Russia with 300 gold.
   Berthier notes that Soult no longer presses the matter — his quarrel with Bernadotte has cooled.
   Soult's resentment of Bernadotte has cooled with time.
   --- Strategic Order Updates ---
   Davout: Davout arrives at Rhineland. Davout: "It is done. I took the liberty of posting pickets."
   Lannes: Lannes arrives at Rhineland. Lannes: "Accomplished. The men want a battle, not another road."
   Ney: Paget destroyed Ney: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 11
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   • Sire — Soult has been 5 turns over what Normandy can feed. 3,855 men dead. The country will ask where the army went. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 75,000 more and Berry can feed 52,685 more — a corps marched there ends it.
   • Sire — Britain's gold reaches Russia — the subsidy stands at 300 this season.
   SITUATION
   France holds 29 regions. Treasury: 6,126g (+2,764 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 55% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 29,293 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy five turns running.
   - Massena — Milan — 25,007 — 4 turns idle.
   - Davout — Rhineland — 16,636 — Awaiting orders.
   - Murat — Artois — 15,386 — 3 turns idle.
   - Ney — Limousin — 13,467 — Awaiting orders.
   - Lannes — Rhineland — 11,059 — Awaiting orders.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,986 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Moore — London — 40,000 [confirmed]
   Castanos — Gascony — 11,935 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Deroy — Munich — substantial force [partial]
   Cuesta — Berry — small force [partial]
   Brunswick — Berlin — large force [stale - T7]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Supply shortage at Normandy: Soult loses 135 troops
   Berthier notes that Soult no longer presses the matter — his quarrel with Bernadotte has cooled.
   Soult's resentment of Bernadotte has cooled with time.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -40.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0166  type Davout, march to Artois  ->  ok
  (typed and Enter)
view: <run>\frames\0166_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout begins march to Artois. Route: Lorraine → Orleanais → Picardy → Artois. Moves to Lorraine. Davout: "We move deliberately — arrival is worth little if the army arrives broken."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1696 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,126 (+2,585 next turn)
   Inf:
   95,083
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Britain subsidizes Russia with 300 gold.
   Berthier notes that Soult no longer presses the matter — his quarrel with Bernadotte has cooled.
   Soult's resentment of Bernadotte has cooled with time.
   --- Strategic Order Updates ---
   Davout: Davout arrives at Rhineland. Davout: "It is done. I took the liberty of posting pickets."
   Lannes: Lannes arrives at Rhineland. Lannes: "Accomplished. The men want a battle, not another road."
   Ney: Paget destroyed Ney: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 11
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   • Sire — Soult has been 5 turns over what Normandy can feed. 3,855 men dead. The country will ask where the army went. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 75,000 more and Berry can feed 52,685 more — a corps marched there ends it.
   • Sire — Britain's gold reaches Russia — the subsidy stands at 300 this season.
   SITUATION
   France holds 29 regions. Treasury: 6,126g (+2,764 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 55% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 29,293 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy five turns running.
   - Massena — Milan — 25,007 — 4 turns idle.
   - Davout — Rhineland — 16,636 — Awaiting orders.
   - Murat — Artois — 15,386 — 3 turns idle.
   - Ney — Limousin — 13,467 — Awaiting orders.
   - Lannes — Rhineland — 11,059 — Awaiting orders.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,986 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Moore — London — 40,000 [confirmed]
   Castanos — Gascony — 11,935 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Deroy — Munich — substantial force [partial]
   Cuesta — Berry — small force [partial]
   Brunswick — Berlin — large force [stale - T7]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Supply shortage at Normandy: Soult loses 135 troops
   Berthier notes that Soult no longer presses the matter — his quarrel with Bernadotte has cooled.
   Soult's resentment of Bernadotte has cooled with time.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -40.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► Davout, march to Artois
   Davout begins march to Artois. Route: Lorraine → Orleanais → Picardy → Artois. Moves to Lorraine. Davout: "We move deliberately — arrival is worth little if the army arrives broken."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  49(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1959,325)  Brunswick(1958,287)  Murat(1604,379)  Napoleon(1627,353)  Lannes(1829,397)  Castanos(1501,598)  Ney(1599,489)  Davout(1753,436)  Dumonceau(1303,280)  Bernadotte(1812,497)  ?(1901,537)  Deroy(1901,501)  Soult(1551,399)  Moore(1478,362)  Wellesley(1502,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  ?(1901,623)  ?(1893,434)  25k(1595,460)  12k(1513,436)  ?(1769,580)  ?(1777,319)  12k(1696,420)  25k(1467,417)  10k(1910,654)
```

```
#0167  type Ney, march to Artois  ->  ok
  (typed and Enter)
view: <run>\frames\0167_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins march to Artois. Route: Champagne → Artois. Moves to Champagne. Ney: "At the double, Sire — the men will smell powder soon enough."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1808 of 1808 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   6,126 (+2,585 next turn)
   Inf:
   95,083
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, march to Artois
   Ney begins march to Artois. Route: Champagne → Artois. Moves to Champagne. Ney: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  49(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Cuesta(1524,465)  ?(1959,325)  Brunswick(1958,287)  Murat(1604,379)  Napoleon(1627,353)  Lannes(1829,397)  Castanos(1501,598)  Davout(1753,436)  Dumonceau(1303,280)  Bernadotte(1812,497)  ?(1901,537)  Deroy(1901,501)  Ney(1648,430)  Soult(1551,399)  Moore(1478,362)  Wellesley(1502,287)  Massena(1910,595)  ?(2068,435)  ?(1959,376)  ?(1901,623)  ?(1893,434)  25k(1595,486)  12k(1580,454)  ?(1769,580)  ?(1777,319)  12k(1696,420)  25k(1490,417)  10k(1910,654)
```

```
#0168  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0168_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 11 ended. Turn 12 begins!

Income: 2713g | Occupation: -15g | Charges of Empire: -298g | Admiralty: -98g | Upkeep: -1008g | Other: +1349g | Net: +2643g | Treasury: 8,769g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 11
   BRITAIN / ──────────────────────────── / - Wellesley holds position /  / SPAIN / ──────────────────────────── / - Castanos abandons fortified position /  / ──────────────────────────── / Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 91 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2118 of 2118 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,769 (+2,430 next turn)
   Inf:
   96,320
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2713g | Occupation: -15g | Charges of Empire: -298g | Admiralty: -98g | Other: +1349g | Upkeep: -1008g | Net: +2643g
   Treasury: 8,769g
   Actions refreshed: 4/4
   Supply shortage at Normandy: Soult loses 132 troops
   Relations between Austria and Russia are deteriorating. Alliance may collapse in 2 turns.
   Britain subsidizes Russia with 200 gold.
   Massena's laurels have faded, Sire — for now no commander in the army stands above the rest.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  49(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Murat(1604,379)  Napoleon(1627,353)  Lannes(1829,397)  Castanos(1501,598)  Davout(1753,436)  Dumonceau(1303,280)  Bernadotte(1812,497)  ?(1901,537)  Deroy(1901,501)  Ney(1648,430)  ?(1595,452)  Cuesta(1595,425)  Soult(1551,399)  Moore(1478,362)  Wellesley(1490,287)  Shrapnel(1537,320)  Massena(1910,595)  ?(1901,623)  ?(1893,434)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1777,319)  12k(1696,420)  25k(1490,417)  10k(1910,654)
```

```
#0169  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0169_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 91 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Naples @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Ney arrived (x2) @(3435,64)]  [icon: Davout arrived (x2) @(3477,64)]  [icon: Britain binds Russia to the war @(3519,64)]  [icon: Napoleon arrived (x3) @(3561,64)]  [+23]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   -1 →
   T:11
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 2074 of 2074 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,769 (+2,430 next turn)
   Inf:
   96,320
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   [2/4 actions remaining]
   ► Ney, march to Artois
   Ney begins march to Artois. Route: Champagne → Artois. Moves to Champagne. Ney: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2713g | Occupation: -15g | Charges of Empire: -298g | Admiralty: -98g | Other: +1349g | Upkeep: -1008g | Net: +2643g
   Treasury: 8,769g
   Actions refreshed: 4/4
   Supply shortage at Normandy: Soult loses 132 troops
   Relations between Austria and Russia are deteriorating. Alliance may collapse in 2 turns.
   Britain subsidizes Russia with 200 gold.
   Massena's laurels have faded, Sire — for now no commander in the army stands above the rest.
   --- Strategic Order Updates ---
   Davout: Davout is marching to Artois (3 turns remaining).
   Ney: Ney is marching to Artois (1 turn remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain's gold reaches Russia — the subsidy stands at 200 this season.
   • Sire — Soult has been 6 turns over what Normandy can feed. 3,987 men dead. The country will ask where the army went. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 67,830 more and Berry can feed 60,000 more — a corps marched there ends it.
   • Sire — intelligence reports Britain has raised Shrapnel to high command.
   SITUATION
   France holds 29 regions. Treasury: 8,769g (+2,643 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 55% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 29,161 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy 6 turns running.
   - Massena — Milan — 25,007 — 5 turns idle.
   > Davout — Lorraine — 16,636 — Moving to Artois — 3 turns out.
   - Murat — Artois — 15,386 — 4 turns idle.
   > Ney — Champagne — 13,467 — Moving to Artois — arrives next turn.
   - Lannes — Rhineland — 11,059 — Awaiting orders.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,986 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Moore — London — 40,000 [confirmed]
   Castanos — Gascony — 11,935 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Shrapnel — London — 3,000 [confirmed]
   Deroy — Munich — substantial force [partial]
   Cuesta — Paris — small force [partial]
   Brunswick — Berlin — large force [last known - T7]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Supply shortage at Normandy: Soult loses 132 troops
   Massena's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   Intelligence reports Britain has raised Shrapnel to high command.
   An envoy from Naples has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -31.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Naples — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0170  click 49 sail  ->  ok
  (clicked at (2932, 18))
view: <run>\frames\0170_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early March 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 49 sail of the line — readiness 75  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: Staged: 53,533 men have stood 7 tu …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in Wales>  <Land Dumonceau in Midlands>  <Land Dumonceau in Northumbria>  <Land Dumonceau in Cornwall>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2074 of 2074 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0171  look  ->  ok
  (a fresh frame)
view: <run>\frames\0171_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2074 of 2074 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0172  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0172_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   -1 →
   T:11
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 2074 of 2074 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0173  click_at 1300 301  ->  ok
  (clicked at (1300, 301) on MapArea '100' (Control, layer 0))
view: <run>\frames\0173_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2074 of 2074 px]: unchanged
── OrderStrip (layer 0) ──
   Dumonceau selected — click a province: march · an enemy: attack · a marshal: support · Esc cancels / ■ this turn   ■ 1 turn   ■ 2–3 turns   ■ 4+ turns   1 province on his roads · a march costs 2 actions
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0174  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0174_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2074 of 2074 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0175  click 49 sail  ->  ok
  (clicked at (2932, 18))
view: <run>\frames\0175_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early March 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 49 sail of the line — readiness 75  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: Staged: 53,533 men have stood 7 tu …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in Wales>  <Land Dumonceau in Midlands>  <Land Dumonceau in Northumbria>  <Land Dumonceau in Cornwall>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2074 of 2074 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0176  click Land Dumonceau in Wales  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0176_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=['ledger'], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   DUMONCEAU ASKS:
   "The expedition is drawn up, Sire: Dumonceau with 6,500 men, Munster to Wales. The transports slip past unseen 75 times in 100 (Britain watches at 112 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. What moves the odds: a won diversion first (50 in 100) → 95 · a 5,000-man corps → 78. Sail? (y …
   controls: [Sail for Wales]  [Stand down]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 91 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2140 of 2140 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,769 (+2,430 next turn)
   Inf:
   96,320
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► land Dumonceau in Wales
   Dumonceau requests clarification...
map: unchanged (56 labels)
```

```
#0177  click Stand down  ->  ok
  (clicked at (1829, 597))
view: <run>\frames\0177_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   A COURT WRITES (1)
   Naples writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Naples
   Proposal
   Open ▸
   Turn 11
   Incoming proposal: Open Borders Agreement
   Medici, smoothly evasive: "Naples has always counted better than she has fought, and the count favors friendship with France. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders · Offer: Gold payment - 150
   or click the letter to reply in full
   controls: {ACTIVE}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 91 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Naples @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Ney arrived (x2) @(3435,64)]  [icon: Davout arrived (x2) @(3477,64)]  [icon: Britain binds Russia to the war @(3519,64)]  [icon: Napoleon arrived (x3) @(3561,64)]  [+23]
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,769 (+2,430 next turn)
   Inf:
   96,320
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (56 labels)
```

```
#0178  click The Grand Diversion  ->  ERROR: no visible control's text holds "The Grand Diversion"
view: <run>\frames\0178_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► land Dumonceau in Wales
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (56 labels)
```

```
#0179  look  ->  ok
  (a fresh frame)
view: <run>\frames\0179_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► land Dumonceau in Wales
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (56 labels)
```

```
#0180  click Accept  ->  ok
  (clicked at (1433, 421))
view: <run>\frames\0180_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 91 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Naples @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Ney arrived (x2) @(3435,64)]  [icon: Davout arrived (x2) @(3477,64)]  [icon: Britain binds Russia to the war @(3519,64)]  [icon: Napoleon arrived (x3) @(3561,64)]  [+23]
── StrategicLedger (layer 50) [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,769 (+2,430 next turn)
   Inf:
   96,320
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain's gold reaches Russia — the subsidy stands at 200 this season.
   • Sire — Soult has been 6 turns over what Normandy can feed. 3,987 men dead. The country will ask where the army went. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 67,830 more and Berry can feed 60,000 more — a corps marched there ends it.
   • Sire — intelligence reports Britain has raised Shrapnel to high command.
   SITUATION
   France holds 29 regions. Treasury: 8,769g (+2,643 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 55% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 29,161 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy 6 turns running.
   - Massena — Milan — 25,007 — 5 turns idle.
   > Davout — Lorraine — 16,636 — Moving to Artois — 3 turns out.
   - Murat — Artois — 15,386 — 4 turns idle.
   > Ney — Champagne — 13,467 — Moving to Artois — arrives next turn.
   - Lannes — Rhineland — 11,059 — Awaiting orders.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,986 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Moore — London — 40,000 [confirmed]
   Castanos — Gascony — 11,935 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Shrapnel — London — 3,000 [confirmed]
   Deroy — Munich — substantial force [partial]
   Cuesta — Paris — small force [partial]
   Brunswick — Berlin — large force [last known - T7]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Supply shortage at Normandy: Soult loses 132 troops
   Massena's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   Intelligence reports Britain has raised Shrapnel to high command.
   An envoy from Naples has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -31.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Naples — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► land Dumonceau in Wales
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
   You have accepted Naples's proposal. Treaty signed: Peace → Open Borders with Naples.
map: unchanged (56 labels)
```

```
#0181  look  ->  ok
  (a fresh frame)
view: <run>\frames\0181_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
   You have accepted Naples's proposal. Treaty signed: Peace → Open Borders with Naples.
map: unchanged (56 labels)
```

```
#0182  click The Grand Diversion  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0182_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=['ledger'], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE ADMIRALTY ASKS:
   "The Grand Diversion is drawn up, Sire. The fleet sails to draw the enemy squadrons off station: 50 times in 100 at her readiness (75) the strait opens for 2 turns; otherwise she is caught coming home and fights at readiness 65. Whatever the outcome, she may try it again 4 turns from now. And mark this, Sire: a success opens London-Normandy for both turns of the window. Sail? (yes / no)"
   controls: [Order the diversion]  [Stand down]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 91 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 49 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 728 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1742 of 1742 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,919 (+2,443 next turn)
   Inf:
   96,320
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► order the diversion
   The Admiralty requests clarification...
map: unchanged (56 labels)
```

```
#0183  click Order the diversion  ->  ok
  (clicked at (1829, 549))
view: <run>\frames\0183_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE SAIL LOST
   BRITAIN SAIL LOST
   0
   0
   Gravina
   33 → 17 sail
   Verhuell
   Senyavin
   12 → 6 sail
   20 → 19 sail
   ⚔
   Villeneuve ◆
   Nelson ◆
   49 → 25 sail
   100 → 96 sail
   THE GREAT FLEET ACTION
   click anywhere to skip ▸
   THE FRANCE–BRITAIN ACTION · TURN 12
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 91 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Lannes arrived (x2) @(3351,64)]  [icon: Ney arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Napoleon arrived (x3) @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+22]
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 684 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early March 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 25 sail of the line — readiness 65  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: Staged: 53,533 men have stood 7 tu …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in Wales>  <Land Dumonceau in Midlands>  <Land Dumonceau in Northumbria>  <Land Dumonceau in Cornwall>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1874 of 1874 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   8,919 (+2,469 next turn)
   Inf:
   96,320
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  25(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Murat(1604,379)  Napoleon(1627,353)  Lannes(1829,397)  Castanos(1501,598)  Davout(1753,436)  Dumonceau(1303,280)  Bernadotte(1812,497)  ?(1901,537)  Deroy(1901,501)  Ney(1648,430)  ?(1595,452)  Cuesta(1595,425)  Soult(1551,399)  Moore(1478,362)  Wellesley(1490,287)  Shrapnel(1537,320)  Massena(1910,595)  ?(1901,623)  ?(1893,434)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1777,319)  12k(1696,420)  25k(1490,417)  10k(1910,654)
```

```
#0184  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0184_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FLEET IS BROKEN
   FRANCE SAIL LOST
   BRITAIN SAIL LOST
   46
   5
   Gravina
   33 → 17 sail
   Verhuell
   Senyavin
   12 → 6 sail
   20 → 19 sail
   ⚔
   Villeneuve ◆
   Nelson ◆
   49 → 25 sail
   100 → 96 sail
   STRUCK
   STRUCK
   STRUCK
   The Admiralty: “Britain holds the sea. The French line is broken and scattered — 46 sail lost against 5. Until the fleet is rebuilt, our coasts and our crossings are at their pleasure.”
   THE GREAT FLEET ACTION
   THE FRANCE–BRITAIN ACTION · TURN 12
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 91 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1874 of 1874 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map: unchanged (56 labels)
```

```
#0185  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0185_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1874 of 1874 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map: unchanged (56 labels)
```

```
#0186  look  ->  ok
  (a fresh frame)
view: <run>\frames\0186_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1874 of 1874 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map: unchanged (56 labels)
```

```
#0187  click Ledger (T)  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0187_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 91 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Lannes arrived (x2) @(3351,64)]  [icon: Ney arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Napoleon arrived (x3) @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+22]
── StrategicLedger (layer 50) [scrolled 0 of 838 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early March 1806 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / ═══ THE CABINET ═══ /   Talleyrand → Austria │ IMPROVING RELATIONS  +8 a turn, drift +1, net +9 /     Relations -31 (Hostile) · ≈18 turns to +100 at the present rate · 1 DP a turn   [Recall] /  / Authority:  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1874 of 1874 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map: unchanged (56 labels)
```

```
#0188  click TERRITORIES  ->  ok
  (clicked at (1569, 283))
view: <run>\frames\0188_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 2268 px] ──
   STRATEGIC LEDGER
   ═══ TERRITORIES ═══ / Early March 1806 / The provinces of the Empire — who holds each, what it pays, how quietly it sits under you. /  / THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1) /   • Munster — a peace with Britain that leaves it ours titles it at the signature; otherwise 12 quiet turns from the peace /  / Berry [major city, plains] /   In …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES](disabled: You are reading this book)  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1874 of 1874 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map: unchanged (56 labels)
```

```
#0189  look  ->  ok
  (a fresh frame)
view: <run>\frames\0189_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 2268 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1874 of 1874 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map: unchanged (56 labels)
```

```
#0190  click ADMIRALTY  ->  ok
  (clicked at (2049, 283))
view: <run>\frames\0190_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 684 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early March 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 25 sail of the line — readiness 65  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: Staged: 53,533 men have stood 7 tu …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in Wales>  <Land Dumonceau in Midlands>  <Land Dumonceau in Northumbria>  <Land Dumonceau in Cornwall>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1874 of 1874 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map: unchanged (56 labels)
```

```
#0191  look  ->  ok
  (a fresh frame)
view: <run>\frames\0191_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 684 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1874 of 1874 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map: unchanged (56 labels)
```

```
#0192  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0192_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   -1 →
   T:11
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 1874 of 1874 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
map: unchanged (56 labels)
```

```
#0193  type where are my marshals  ->  ok
  (typed and Enter)
view: <run>\frames\0193_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Our army stands at 135,853 men under 9 marshals, Sire:
  Soult — 29,161 at Normandy (morale 94)
  Massena — 25,007 at Milan (morale 75)
  Davout — 16,636 at Lorraine (morale 75)
  Murat — 15,386 at Artois (morale 75)
  Ney — 13,467 at Champagne (morale 70)
  Lannes — 11,059 at Rhineland (morale 75)
  Bernadotte — 9,651 at Franche-Comte (morale 45)
  Napoleon — 8,986 at Artois (morale 85)
  … and 1 more
The Strategic Ledger's Forces tab (press T) has the full return; the Generals screen (press G) has each man's card.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1653 of 1653 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   8,919 (+2,469 next turn)
   Inf:
   96,320
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where are my marshals
   Our army stands at 135,853 men under 9 marshals, Sire:
   Soult — 29,161 at Normandy (morale 94)
   Massena — 25,007 at Milan (morale 75)
   Davout — 16,636 at Lorraine (morale 75)
   Murat — 15,386 at Artois (morale 75)
   Ney — 13,467 at Champagne (morale 70)
   Lannes — 11,059 at Rhineland (morale 75)
   Bernadotte — 9,651 at Franche-Comte (morale 45)
   Napoleon — 8,986 at Artois (morale 85)
   … and 1 more
   The Strategic Ledger's Forces tab (press T) has the full return; the Generals screen (press G) has each man's card.
map: unchanged (56 labels)
```

```
#0194  type Lannes, march to Artois  ->  ok
  (typed and Enter)
view: <run>\frames\0194_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes begins march to Artois. Route: Lorraine → Orleanais → Picardy → Artois. Moves to Lorraine. Lannes: "At the double, Sire — the men will smell powder soon enough."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2316 of 2316 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   8,919 (+2,469 next turn)
   Inf:
   96,320
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, march to Artois
   Lannes begins march to Artois. Route: Lorraine → Orleanais → Picardy → Artois. Moves to Lorraine. Lannes: "At the double, Sire — the men will smell powder soon enough."
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2040,556)  France(1584,516)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Bavaria(1901,566)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  25(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Murat(1604,379)  Napoleon(1627,353)  Castanos(1501,598)  Davout(1741,436)  Lannes(1764,462)  Dumonceau(1303,280)  Bernadotte(1812,497)  ?(1901,537)  Deroy(1901,501)  Ney(1648,430)  ?(1595,452)  Cuesta(1595,425)  Soult(1551,399)  Moore(1478,362)  Wellesley(1490,287)  Shrapnel(1537,320)  Massena(1910,595)  ?(1901,623)  ?(1893,434)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1777,319)  12k(1684,401)  25k(1490,417)  10k(1910,654)
```

```
#0195  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0195_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!

Income: 2719g | Occupation: -15g | Charges of Empire: -545g | Admiralty: -50g | Upkeep: -1000g | Other: +1374g | Net: +2483g | Treasury: 11,402g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 12
   SPAIN / ──────────────────────────── / - Cuesta moves to Normandy /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 89 / 100
   Turn 13 — Late March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2141 of 2142 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,402 (+2,258 next turn)
   Inf:
   97,357
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Moore — London — 40,000 [confirmed]
   Castanos — Gascony — 11,935 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Shrapnel — London — 3,000 [confirmed]
   Deroy — Munich — substantial force [partial]
   Cuesta — Paris — small force [partial]
   Brunswick — Berlin — large force [last known - T7]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Supply shortage at Normandy: Soult loses 132 troops
   Massena's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   Intelligence reports Britain has raised Shrapnel to high command.
   An envoy from Naples has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -31.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Naples — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► land Dumonceau in Wales
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
   You have accepted Naples's proposal. Treaty signed: Peace → Open Borders with Naples.
   ► order the diversion
   The Admiralty requests clarification...
   > order the diversion confirmed
   The diversion is caught coming home — the fleet is brought to battle at bad readiness. France loses 24 sail; Spain 16 and Holland 6 beside her. A decisive defeat: the enemy's line held the weather gage. She may try it again in 4 turns, at the odds her readiness then gives.
   [3/4 actions remaining]
   ⚓ View the action
   ► where are my marshals
   Our army stands at 135,853 men under 9 marshals, Sire:
   Soult — 29,161 at Normandy (morale 94)
   Massena — 25,007 at Milan (morale 75)
   Davout — 16,636 at Lorraine (morale 75)
   Murat — 15,386 at Artois (morale 75)
   Ney — 13,467 at Champagne (morale 70)
   Lannes — 11,059 at Rhineland (morale 75)
   Bernadotte — 9,651 at Franche-Comte (morale 45)
   Napoleon — 8,986 at Artois (morale 85)
   … and 1 more
   The Strategic Ledger's Forces tab (press T) has the full return; the Generals screen (press G) has each man's card.
   ► Lannes, march to Artois
   Lannes begins march to Artois. Route: Lorraine → Orleanais → Picardy → Artois. Moves to Lorraine. Lannes: "At the double, Sire — the men will smell powder soon enough."
   [1/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 13 BEGINS
   ═══════════════════════════════════════
   Income: 2719g | Occupation: -15g | Charges of Empire: -545g | Admiralty: -50g | Other: +1374g | Upkeep: -1000g | Net: +2483g
   Treasury: 11,402g
   Actions refreshed: 4/4
   Crowded at Artois: Ney loses 269 troops to the press of 3 corps on one province's roads
   Crowded at Artois: Murat loses 307 troops to the press of 3 corps on one province's roads
   Crowded at Artois: Napoleon loses 179 troops to the press of 3 corps on one province's roads
   Supply shortage at Normandy: Soult loses 559 troops
   Supply shortage at Normandy: Cuesta loses 136 troops
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Austria grows.
   Peace concluded between Austria and Bavaria without France. Both courts are spent; their side of the war ends while the greater war goes on.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  25(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Castanos(1525,465)  Ney(1603,379)  Murat(1616,353)  Napoleon(1627,327)  ?(1859,469)  Deroy(1859,430)  Lannes(1752,436)  Dumonceau(1303,280)  ?(1449,664)  Blake(1448,625)  Bernadotte(1812,497)  Davout(1686,440)  Soult(1539,399)  Cuesta(1552,373)  ?(1475,371)  Moore(1475,344)  ?(1502,371)  Wellesley(1490,287)  ?(1519,345)  Shrapnel(1505,261)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,486)  12k(1590,454)  ?(1769,580)  12k(1684,411)  ?(1490,417)  10k(1910,645)
```

```
#0196  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0196_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 89 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x3) @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Napoleon arrived (x3) @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+22]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   -2 →
   T:12
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 1982 of 1982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,402 (+2,258 next turn)
   Inf:
   97,357
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Income: 2719g | Occupation: -15g | Charges of Empire: -545g | Admiralty: -50g | Other: +1374g | Upkeep: -1000g | Net: +2483g
   Treasury: 11,402g
   Actions refreshed: 4/4
   Crowded at Artois: Ney loses 269 troops to the press of 3 corps on one province's roads
   Crowded at Artois: Murat loses 307 troops to the press of 3 corps on one province's roads
   Crowded at Artois: Napoleon loses 179 troops to the press of 3 corps on one province's roads
   Supply shortage at Normandy: Soult loses 559 troops
   Supply shortage at Normandy: Cuesta loses 136 troops
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Austria grows.
   Peace concluded between Austria and Bavaria without France. Both courts are spent; their side of the war ends while the greater war goes on.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   --- Strategic Order Updates ---
   Davout: Davout marches to Orleanais. 2 regions to Artois.
   Lannes: Lannes is marching to Artois (3 turns remaining).
   Ney: Ney arrives at Artois.
   Artois feeds 60,000; the 37,839 men standing there would lose ~755 a turn to crowding — too many corps on one province. Ney: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 13
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — The fleet is shattered in action with Britain — France loses 24 sail; Spain 16 and Holland 6 beside her.
   • Sire — Soult has been 6 turns over what Normandy can feed. 2,757 men dead. The country will ask where the army went. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 75,000 more and Maine can feed 52,500 more — a corps marched there ends it.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 29 regions. Treasury: 11,402g (+2,483 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 63% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 28,602 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy 6 turns running.
   - Massena — Milan — 25,007 — 6 turns idle.
   > Davout — Orleanais — 16,636 — Moving to Artois — 2 turns out.
   - Murat — Artois — 15,079 — 5 turns idle.
   - Ney — Artois — 13,198 — Awaiting orders.
   > Lannes — Lorraine — 11,059 — Moving to Artois — 3 turns out.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,807 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Cuesta — Normandy — 6,963 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Moore — London — large force [partial]
   Castanos — Berry — small force [partial]
   Wellesley — London — substantial force [partial]
   Blake — Bearn — small force [partial]
   Shrapnel — London — screening force [partial]
   Brunswick — Berlin — large force [last known - T7]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 1,314 men, at Artois and Normandy.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   DIPLOMATIC EVENTS
   Sire — Naples and France have signed the Open Borders Agreement.
   TRAFALGAR: Nelson's line has shattered the French fleet — 24 sail lost in a decisive action. Britain commands the sea.
   Franconia passes from Austria to Bavaria.
   Swabia passes from Austria to Bavaria.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -22.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The water is theirs until the yards replace what we lost, Sire — and new keels sail green."
   ════════════════════════════════════
map: unchanged (61 labels)
```

```
#0197  click Envoys  ->  ok
  (clicked at (3394, 18))
view: <run>\frames\0197_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2004 of 2004 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,402 (+2,258 next turn)
   Inf:
   97,357
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   No pending envoys at this time.
map: unchanged (61 labels)
```

```
#0198  look  ->  ok
  (a fresh frame)
view: <run>\frames\0198_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2004 of 2004 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The water is theirs until the yards replace what we lost, Sire — and new keels sail green."
   ════════════════════════════════════
   No pending envoys at this time.
map: unchanged (61 labels)
```

```
#0199  type Ney, march to Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0199_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins march to Normandy. Moves to Normandy.
Normandy feeds 22,500; the 48,763 men standing there would lose ~1,567 a turn to short supply. Ney: "Good. An army rots standing still."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2136 of 2136 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   11,402 (+2,258 next turn)
   Inf:
   97,357
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, march to Normandy
   Ney begins march to Normandy. Moves to Normandy.
   Normandy feeds 22,500; the 48,763 men standing there would lose ~1,567 a turn to short supply. Ney: "Good. An army rots standing still."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  25(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Castanos(1525,465)  Murat(1604,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  Lannes(1752,436)  Dumonceau(1303,280)  ?(1449,664)  Blake(1448,625)  Bernadotte(1812,497)  Davout(1686,440)  Ney(1538,399)  Soult(1551,373)  Cuesta(1551,347)  ?(1475,371)  Moore(1475,344)  ?(1502,371)  Wellesley(1490,287)  Shrapnel(1505,261)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,486)  12k(1589,454)  ?(1769,580)  12k(1684,411)  ?(1490,417)  10k(1910,645)
```

```
#0200  type land Dumonceau in Wales  ->  ok
  (typed and Enter)
view: <run>\frames\0200_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
reply: ok The expedition is drawn up, Sire: Dumonceau with 6,500 men, Munster to Wales. The transports slip past unseen 69 times in 100 (Britain watches at 107 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. What moves the odds: a 5,000-man corps → 72. Sail? (yes / no)
── ClarificationPopup (layer 102) ──
   DUMONCEAU ASKS:
   "The expedition is drawn up, Sire: Dumonceau with 6,500 men, Munster to Wales. The transports slip past unseen 69 times in 100 (Britain watches at 107 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. What moves the odds: a 5,000-man corps → 72. Sail? (yes / no)"
   controls: [Sail for Wales]  [Stand down]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 89 / 100
   Turn 13 — Late March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2204 of 2204 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   11,402 (+2,258 next turn)
   Inf:
   97,357
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► land Dumonceau in Wales
   Dumonceau requests clarification...
map: unchanged (60 labels)
```

```
#0201  click Sail for Wales  ->  ok
  (clicked at (1829, 549))
view: <run>\frames\0201_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Dumonceau has taken Wales
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+400 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 91 / 100
   Turn 13 — Late March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1807 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   11,402 (+1,925 next turn)
   Inf:
   97,357
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   • Sire — Soult has been 6 turns over what Normandy can feed. 2,757 men dead. The country will ask where the army went. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 75,000 more and Maine can feed 52,500 more — a corps marched there ends it.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 29 regions. Treasury: 11,402g (+2,483 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 63% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 28,602 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy 6 turns running.
   - Massena — Milan — 25,007 — 6 turns idle.
   > Davout — Orleanais — 16,636 — Moving to Artois — 2 turns out.
   - Murat — Artois — 15,079 — 5 turns idle.
   - Ney — Artois — 13,198 — Awaiting orders.
   > Lannes — Lorraine — 11,059 — Moving to Artois — 3 turns out.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,807 — Awaiting orders.
   - Dumonceau — Munster — 6,500 — Awaiting orders.
   INTELLIGENCE
   Cuesta — Normandy — 6,963 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Moore — London — large force [partial]
   Castanos — Berry — small force [partial]
   Wellesley — London — substantial force [partial]
   Blake — Bearn — small force [partial]
   Shrapnel — London — screening force [partial]
   Brunswick — Berlin — large force [last known - T7]
   London garrison — London — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 1,314 men, at Artois and Normandy.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   DIPLOMATIC EVENTS
   Sire — Naples and France have signed the Open Borders Agreement.
   TRAFALGAR: Nelson's line has shattered the French fleet — 24 sail lost in a decisive action. Britain commands the sea.
   Franconia passes from Austria to Bavaria.
   Swabia passes from Austria to Bavaria.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -22.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The water is theirs until the yards replace what we lost, Sire — and new keels sail green."
   ════════════════════════════════════
   No pending envoys at this time.
   ► Ney, march to Normandy
   Ney begins march to Normandy. Moves to Normandy.
   Normandy feeds 22,500; the 48,763 men standing there would lose ~1,567 a turn to short supply. Ney: "Good. An army rots standing still."
   [2/4 actions remaining]
   ► land Dumonceau in Wales
   Dumonceau requests clarification...
   > land Dumonceau in Wales confirmed
   THE LANDING: Dumonceau slips past the British patrols and puts 6,500 men ashore at Wales (odds were 69 in 100).
   Your forces have taken Wales. Plunder it for 400 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [0/4 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1579,511)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  25(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Castanos(1525,465)  Murat(1604,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  Lannes(1752,436)  ?(1449,664)  Blake(1448,625)  Bernadotte(1812,497)  Dumonceau(1395,287)  Davout(1686,440)  Ney(1538,399)  Soult(1551,373)  Cuesta(1551,347)  ?(1475,371)  Moore(1475,344)  ?(1502,371)  Wellesley(1493,287)  Shrapnel(1505,261)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,480)  12k(1589,450)  ?(1769,580)  12k(1684,411)  ?(1490,417)  10k(1910,645)
```

```
#0202  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0202_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 91 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x3) @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Napoleon arrived (x3) @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+22]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +5 ↑
   T:12
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 1895 of 1895 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   11,402 (+1,925 next turn)
   Inf:
   97,357
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {96}
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Dumonceau secures Wales. Stability set to 25. Order is maintained.
map: unchanged (60 labels)
```

```
#0203  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0203_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 13 ended. Turn 14 begins!

Income: 2725g | Requisitions: +75g | Occupation: -15g | Charges of Empire: -788g | Admiralty: -50g | Materiel: -230g | Upkeep: -984g | Other: +1374g | Net: +2107g | Treasury: 13,509g
── EnemyPhaseDialog (layer 118) [scrolled 0 of 510 px] ──
   ENEMY PHASE - Turn 13
   BRITAIN / ──────────────────────────── / - Moore attacks Wales /     Battle of Wales /     Moore attacks Dumonceau /     Moore: 813 casualties, 39,187 remaining /     Dumonceau: 3,280 casualties, 3,220 remaining /     Result: Attacker tactical victory (Moore victorious) — and advances into Wales /     Wales CAPTURED! (was France) (secured) /     Dumonceau forced to retreat! /     ⚔ View the field  …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 90 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2381 of 2381 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,509 (+2,099 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 14 BEGINS
   ═══════════════════════════════════════
   Income: 2725g | Requisitions: +75g | Occupation: -15g | Charges of Empire: -788g | Admiralty: -50g | Materiel: -230g | Other: +1374g | Upkeep: -984g | Net: +2107g
   Treasury: 13,509g
   Actions refreshed: 4/4
   Dumonceau's army is recovering. Effectiveness penalty: -30%.
   Supply shortage at Normandy: Ney loses 301 troops
   Supply shortage at Normandy: Soult loses 654 troops
   Holland loyalty 87 (-13): the contingent's dead, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 82 (-5): the lord's defeats, satellite drift
   Switzerland loyalty 89 (-5): the lord's defeats, satellite drift
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Britain subsidizes Russia with 300 gold.
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach. He asked for an audience on turn 8, and will not ask again before turn 14.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  25(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Castanos(1507,499)  Cuesta(1537,473)  Murat(1604,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  ?(1449,664)  Blake(1448,625)  Bernadotte(1812,497)  Lannes(1694,440)  Ney(1538,399)  Soult(1550,373)  Dumonceau(1507,344)  Davout(1673,379)  Wellesley(1478,370)  Shrapnel(1502,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,486)  12k(1590,454)  ?(1769,580)  12k(1751,420)  25k(1490,417)  10k(1910,645)
```

```
#0204  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0204_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   BRITAIN LOSSES
   0
   0
   ⚔
   Dumonceau ◆
   Moore ◆
   6,500 → 3,220
   40,000 → 39,187 → 38,012 after the advance
   BATTLE OF WALES
   click anywhere to skip ▸
   WALES · TURN 13
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 90 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from the Kingdom of Italy @(3351,64)]  [icon: Ney arrived (x4) @(3393,64)]  [icon: Envoy from Britain @(3435,64)]  [icon: Lannes arrived (x2) @(3477,64)]  [icon: Davout arrived (x2) @(3519,64)]  [icon: Napoleon arrived (x3) @(3561,64)]  [+25]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Munster
   -10 →
   T:13
   controls: [THIRD COALITION  ▸]  [War for Munster]
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
   13,509 (+2,099 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach. He asked for an audience on turn 8, and will not ask again before turn 14.
   --- Strategic Order Updates ---
   Davout: Davout marches to Picardy. 1 region to Artois.
   Lannes: Lannes marches to Orleanais. 2 regions to Artois.
   Ney: Ney arrives at Normandy.
   Normandy feeds 22,500; the 41,800 men standing there would lose ~955 a turn to short supply. Ney: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 14
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Dumonceau's corps has been broken at Midlands. He must reform before he fights again.
   • Sire — Dumonceau was mauled at Wales: half of his corps — 3,280 men — lost in a single action.
   • Sire — Wales has been taken by Britain.
   • Sire — Soult has been 6 turns over what Normandy can feed. 2,062 men dead. The country will ask where the army went. No depot may be laid at Normandy — rural regions don't support buildings (need city or larger). Paris can feed 75,000 more and Maine can feed 52,500 more — a corps marched there ends it.
   • Sire — London now pays Vienna 300 gold a turn against us. Her peace with us binds her 4 more turns.
   SITUATION
   France holds 29 regions. Treasury: 13,509g (+2,337 by the accounts)
   The courts at war hold 20 regions. Estimated enemy strength: 29% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Normandy — 27,948 — Awaiting orders.
   ⚠ Starving — supply has failed at Normandy 6 turns running.
   - Massena — Milan — 25,007 — 7 turns idle.
   > Davout — Picardy — 16,636 — Moving to Artois — arrives next turn.
   - Murat — Artois — 15,079 — 6 turns idle.
   - Ney — Normandy — 12,897 — Awaiting orders.
   > Lannes — Orleanais — 11,059 — Moving to Artois — 2 turns out.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,807 — Awaiting orders.
   < Dumonceau — East Anglia — 1,864 — Has fallen back 2 times in five turns — now at East Anglia with 1,864 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Castanos — Berry — 11,816 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Cuesta — Berry — 6,894 [confirmed]
   Shrapnel — London — 3,000 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Blake — Bearn — small force [partial]
   Brunswick — Berlin — large force [last known - T7]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Dumonceau's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 955 men, at Normandy.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach. He asked for an audience on turn 8, and will not ask again before turn 14.
   DIPLOMATIC EVENTS
   THE LANDING: Dumonceau has put 6,500 men ashore at Wales.
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -13.
   An envoy from the Kingdom of Italy has arrived with a petition.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-10)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 90/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0205  click Envoys  ->  ERROR: no visible control's text holds "Envoys"
view: <run>\frames\0205_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   BRITAIN LOSSES
   2,719
   674
   ⚔
   Dumonceau ◆
   Moore ◆
   6,500 → 3,220
   40,000 → 39,187 → 38,012 after the advance
   ROUTED
   BATTLE OF WALES
   click anywhere to skip ▸
   WALES · TURN 13
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1916 of 1916 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 90/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0206  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0206_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
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
   13,509 (+2,099 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 90/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0207  click Close  ->  ERROR: no visible control's text holds "Close"
view: <run>\frames\0207_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1916 of 1916 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 90/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0208  click Envoys  ->  ok
  (clicked at (3397, 18))
view: <run>\frames\0208_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Britain
   Proposal
   Open ▸
   Turn 13
   Incoming proposal: Armistice
   WAITING
   Kingdom of Italy
   Proposal
   Open ▸
   Turn 14
   Incoming proposal: Client's Petition
   controls: {ACTIVE}  {WAITING}  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1916 of 1916 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 90/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0209  click#1 Open  ->  ERROR: no visible control's text holds "Open"
view: <run>\frames\0209_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1916 of 1916 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 90/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0210  click_at 1646 274  ->  ok
  (clicked at (1646, 274) on @PanelContainer@6839 'ACTIVE' (PanelContainer, layer 119))
view: <run>\frames\0210_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 662 px] ──
   DIPLOMATIC ENVOY / Castlereagh (Hawk) of Britain /  / Proposes: Armistice / Terms: / Mutual: /   - Armistice (cease hostilities temporarily) — France and Britain /  / Assessment: GENEROUS /  / War Summary / The War for Munster: France holds Munster of Britain's. / War score: -10 v (Territory +5, Battle -6, Campaign +2, Blood -1, Blockade -2, Ticking -8) / Settlement (this pair): White Peace / Obje …
   controls: [Accept]  [Let Talleyrand haggle (1 DP)]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
   13,509 (+2,099 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 90/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0211  click Accept  ->  ok
  (clicked at (1574, 687))
view: <run>\frames\0211_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Marescalchi (Loyalist) of Kingdom of Italy /  / The petition: /   - Grant it, and the Kingdom of Italy's tribute of 375g a turn is remitted for 8 collections (3000g forgone): loyalty +10, its bond with us rises -20 → 0 (worth +0 a turn in loyalty, now -1), for 1 DP. /   - Refuse it, and the Kingdom of Italy loses 10 loyalty and its bond with us falls 20 (-20 → -40: worth -2 a …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 90 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
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
   13,509 (+2,024 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (56 labels)
```

```
#0212  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0212_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 90 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x4) @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Napoleon arrived (x3) @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+25]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   0 →
   T:13
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Britain, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2048 of 2048 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,509 (+1,649 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {96}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0213  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0213_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — Road III, The Continental System: The Blockade of the British Isles — 3 of 26 ports shut to Britain — 13 needed; The Peace of the Continent — Britain has not signed
   At War (1)
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2048 of 2048 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0214  scroll 1700 600 down 5  ->  ok
  (scrolled down 5 at (1700, 600))
view: <run>\frames\0214_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 181 of 787 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (1)
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Britain  —  Armistice  |  -90 (Hostile)]  [Prussia  —  Open Borders  |  -13 (Wary)]  [Spain  —  Alliance  |  +27 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2048 of 2048 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0215  click Britain  ->  ok
  (clicked at (1825, 507))
view: <run>\frames\0215_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 325 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: Armistice — the War for Munster   Relation: -90 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Britain, though they will demand terms." / Recommendation: If I may, Sire — a level war in truce: 5 turns, relations -90; the ledger stands: the war score reads -10 for France (2 battles, 0 decisives kept); the war is 1 …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2048 of 2048 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0216  scroll 1700 560 down 4  ->  ok
  (scrolled down 4 at (1700, 560))
view: <run>\frames\0216_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 103 of 316 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: Armistice — the War for Munster   Relation: -90 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Britain, though they will demand terms." / Recommendation: If I may, Sire — a level war in truce: 5 turns, relations -90; the ledger stands: the war score reads -10 for France (2 battles, 0 decisives kept); the war is 1 …
   Mission already active
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Peace (2 DP)  —  Hopeless]  [Improve Relations (1 DP)  —  +8 relation/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2048 of 2048 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0217  click Improve Relations  ->  ok
  (the control is disabled; the click did nothing (its reason: Mission already active))
view: <run>\frames\0217_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 103 of 316 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2048 of 2048 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0218  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0218_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2048 of 2048 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0219  click Talleyrand: Improving Relations  ->  ok
  (clicked at (3232, 18))
view: <run>\frames\0219_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 134 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Austria
   DP: 5/7
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 5/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Improving Relations → Austria /   Hostile → Wary (+58, 6 turns) /   Status: Active, Cost: 1 DP/turn /   Effect: +8 relation per turn /   Net +8 a turn · ≈16 turns to +100 at the …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2048 of 2048 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0220  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0220_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   0 →
   T:13
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Britain, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2048 of 2048 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0221  type recall Talleyrand from his mission  ->  ok
  (typed and Enter)
view: <run>\frames\0221_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2160 of 2160 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,509 (+1,649 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recall Talleyrand from his mission
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
map: unchanged (56 labels)
```

```
#0222  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0222_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — Road III, The Continental System: The Blockade of the British Isles — 3 of 26 ports shut to Britain — 13 needed; The Peace of the Continent — Britain has not signed
   At War (1)
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2160 of 2160 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► recall Talleyrand from his mission
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
map: unchanged (56 labels)
```

```
#0223  look  ->  ok
  (a fresh frame)
view: <run>\frames\0223_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2160 of 2160 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► recall Talleyrand from his mission
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
map: unchanged (56 labels)
```

```
#0224  scroll 1700 560 down 8  ->  ok
  (scrolled down 8 at (1700, 560))
view: <run>\frames\0224_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 308 of 794 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  Armistice  |  -90 (Hostile)]  [Prussia  —  Open Borders  |  -13 (Wary)]  [Spain  —  Alliance  |  +27 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Naples  —  Open Borders  |  -17 (Wary)]  [Portugal  —  Open Borders  |  -20 (Wary)]  [Denmark  —  Non-Aggression  |  -5 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2160 of 2160 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► recall Talleyrand from his mission
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
map: unchanged (56 labels)
```

```
#0225  click Austria  ->  ERROR: no visible control's text holds "Austria"
view: <run>\frames\0225_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 308 of 794 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2160 of 2160 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► recall Talleyrand from his mission
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
map: unchanged (56 labels)
```

```
#0226  scroll 1700 560 down 10  ->  ok
  (scrolled down 10 at (1700, 560))
view: <run>\frames\0226_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 709 of 789 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (4)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Austria  —  Peace  |  -13 (Wary)  [MISSION]]  [Sweden  —  Peace  |  -47 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2160 of 2160 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► recall Talleyrand from his mission
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
map: unchanged (56 labels)
```

```
#0227  click Austria  ->  ok
  (clicked at (1825, 585))
view: <run>\frames\0227_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 178 px, 0 of 558 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -13 (Wary) /  / "Austria maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: Relations must improve before proposals will find purchase. /  / KEY FACTORS /   + Base willingness (+35) /   + Diplomat personality (+5) /   + Our diplomatic reputatio …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile → Wary (+58, 6 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1212g) (1 DP + 1212g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2160 of 2160 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► recall Talleyrand from his mission
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
map: unchanged (56 labels)
```

```
#0228  click Cancel: Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0228_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 90 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x4) @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Napoleon arrived (x3) @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2247 of 2247 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,509 (+1,649 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {96}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (56 labels)
```

```
#0229  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0229_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — Road III, The Continental System: The Blockade of the British Isles — 3 of 26 ports shut to Britain — 13 needed; The Peace of the Continent — Britain has not signed
   At War (1)
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2247 of 2247 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (56 labels)
```

```
#0230  click Britain  ->  ERROR: no visible control's text holds "Britain"
view: <run>\frames\0230_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2247 of 2247 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (56 labels)
```

```
#0231  scroll 1700 560 down 4  ->  ok
  (scrolled down 4 at (1700, 560))
view: <run>\frames\0231_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 183 of 789 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (1)
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Britain  —  Armistice  |  -90 (Hostile)]  [Prussia  —  Open Borders  |  -13 (Wary)]  [Spain  —  Alliance  |  +27 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2247 of 2247 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (56 labels)
```

```
#0232  click Improve Relations  ->  ERROR: no visible control's text holds "Improve Relations"
view: <run>\frames\0232_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 183 of 789 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2247 of 2247 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (56 labels)
```

```
#0233  scroll 1700 560 up 30  ->  ok
  (scrolled up 30 at (1700, 560))
view: <run>\frames\0233_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — Road III, The Continental System: The Blockade of the British Isles — 3 of 26 ports shut to Britain — 13 needed; The Peace of the Continent — Britain has not signed
   At War (1)
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2247 of 2247 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (56 labels)
```

```
#0234  scroll 1700 560 down 5  ->  ok
  (scrolled down 5 at (1700, 560))
view: <run>\frames\0234_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 181 of 787 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (1)
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Britain  —  Armistice  |  -90 (Hostile)]  [Prussia  —  Open Borders  |  -13 (Wary)]  [Spain  —  Alliance  |  +27 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2247 of 2247 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (56 labels)
```

```
#0235  click Britain  —  Armistice  ->  ok
  (clicked at (1825, 507))
view: <run>\frames\0235_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 233 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: Armistice — the War for Munster   Relation: -90 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Britain, though they will demand terms." / Recommendation: Sire, the truce with Britain has 5 turns to run; the ledger stands: the war score reads -10 for France (2 battles, 0 decisives kept); the war is 13 turns old an …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2247 of 2247 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (56 labels)
```

```
#0236  scroll 1700 560 down 4  ->  ok
  (scrolled down 4 at (1700, 560))
view: <run>\frames\0236_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 103 of 249 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: Armistice — the War for Munster   Relation: -90 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Britain, though they will demand terms." / Recommendation: Sire, the truce with Britain has 5 turns to run; the ledger stands: the war score reads -10 for France (2 battles, 0 decisives kept); the war is 13 turns old an …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Peace (2 DP)  —  Hopeless]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2247 of 2247 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (56 labels)
```

```
#0237  click Improve Relations  ->  ok
  (clicked at (1825, 607))
view: <run>\frames\0237_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Britain /  / "Sire, I shall begin efforts to improve relations with Britain. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 90 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2293 of 2293 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,509 (+1,649 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► improve relations with Britain
map: unchanged (56 labels)
```

```
#0238  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0238_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 90 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 25 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x4) @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Napoleon arrived (x3) @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+25]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   0 →
   T:13
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Britain, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1696 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,509 (+1,649 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {96}
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ⚠ Starving — supply has failed at Normandy 6 turns running.
   - Massena — Milan — 25,007 — 7 turns idle.
   > Davout — Picardy — 16,636 — Moving to Artois — arrives next turn.
   - Murat — Artois — 15,079 — 6 turns idle.
   - Ney — Normandy — 12,897 — Awaiting orders.
   > Lannes — Orleanais — 11,059 — Moving to Artois — 2 turns out.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,807 — Awaiting orders.
   < Dumonceau — East Anglia — 1,864 — Has fallen back 2 times in five turns — now at East Anglia with 1,864 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Castanos — Berry — 11,816 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Cuesta — Berry — 6,894 [confirmed]
   Shrapnel — London — 3,000 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Blake — Bearn — small force [partial]
   Brunswick — Berlin — large force [last known - T7]
   London garrison — London — garrison of 25,000 [confirmed]
   TURN EVENTS
   Dumonceau's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 955 men, at Normandy.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach. He asked for an audience on turn 8, and will not ask again before turn 14.
   DIPLOMATIC EVENTS
   THE LANDING: Dumonceau has put 6,500 men ashore at Wales.
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -13.
   An envoy from the Kingdom of Italy has arrived with a petition.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-10)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 90/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
   ► recall Talleyrand from his mission
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
   ► improve relations with Britain
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Britain. (1 DP/turn)
map: unchanged (56 labels)
```

```
#0239  type lay down a ship of the line  ->  ok
  (typed and Enter)
view: <run>\frames\0239_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais (400g). The fleet stands at 26 sail — readiness 74 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 5/7
   Threat 90 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 26 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x4) @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Napoleon arrived (x3) @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1829 of 1829 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   13,109 (+1,658 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 26 sail — readiness 74 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  26(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Castanos(1507,499)  Cuesta(1537,473)  Murat(1604,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  ?(1449,664)  Blake(1448,625)  Bernadotte(1812,497)  Lannes(1694,440)  Ney(1538,399)  Soult(1550,373)  Dumonceau(1507,344)  Davout(1673,379)  Wellesley(1478,370)  Shrapnel(1502,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,486)  12k(1590,454)  ?(1769,580)  12k(1751,420)  25k(1490,417)  10k(1910,645)
```

```
#0240  type lay down a ship of the line  ->  ok
  (typed and Enter)
view: <run>\frames\0240_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok A keel is laid at Bordelais (400g). The fleet stands at 27 sail — readiness 73 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 5/7
   Threat 90 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney arrived (x4) @(3351,64)]  [icon: Lannes arrived (x2) @(3393,64)]  [icon: Davout arrived (x2) @(3435,64)]  [icon: Napoleon arrived (x3) @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+25]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1963 of 1963 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   12,709 (+1,666 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   [lay down a ship of the line]  (Tab)
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 27 sail — readiness 73 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Castanos(1507,499)  Cuesta(1537,473)  Murat(1604,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  ?(1449,664)  Blake(1448,625)  Bernadotte(1812,497)  Lannes(1694,440)  Ney(1538,399)  Soult(1550,373)  Dumonceau(1507,344)  Davout(1673,379)  Wellesley(1478,370)  Shrapnel(1502,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,486)  12k(1590,454)  ?(1769,580)  12k(1751,420)  25k(1490,417)  10k(1910,645)
```

```
#0241  type Soult, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0241_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult begins march to Flanders. Route: Artois → Westphalia → Flanders. Moves to Artois.
Artois feeds 60,000; the 51,834 men standing there would lose ~1,035 a turn to crowding — too many corps on one province. "Soult, march to Flanders." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2118 of 2118 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   3/4
   Admin:
   0/2
   Gold:
   12,709 (+1,666 next turn)
   Inf:
   98,357
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, march to Flanders
   Soult begins march to Flanders. Route: Artois → Westphalia → Flanders. Moves to Artois.
   Artois feeds 60,000; the 51,834 men standing there would lose ~1,035 a turn to crowding — too many corps on one province. "Soult, march to Flanders." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,465)  Cuesta(1532,439)  Soult(1604,379)  Murat(1616,353)  Napoleon(1627,327)  ?(1859,469)  Deroy(1859,430)  ?(1449,664)  Blake(1448,625)  Bernadotte(1812,497)  Lannes(1694,440)  Ney(1550,399)  Dumonceau(1507,344)  Davout(1673,379)  Wellesley(1478,370)  Shrapnel(1502,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,486)  12k(1588,454)  ?(1769,580)  12k(1751,420)  25k(1490,411)  10k(1910,645)
```

```
#0242  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0242_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!

Income: 2731g | Occupation: -15g | Charges of Empire: -955g | Admiralty: -54g | Upkeep: -976g | Other: +949g | Net: +1680g | Spent: 800g | Treasury: 14,389g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 14
   BRITAIN / ──────────────────────────── / - Moore moves to Midlands / - Moore moves to Cornwall / - Wellesley abandons fortified position / - Moore moves to London /  / SPAIN / ──────────────────────────── / - Cuesta moves to Normandy /  / ──────────────────────────── / Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 89 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1945 of 1946 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   14,389 (+1,766 next turn)
   Inf:
   99,357
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach. He asked for an audience on turn 8, and will not ask again before turn 14.
   DIPLOMATIC EVENTS
   THE LANDING: Dumonceau has put 6,500 men ashore at Wales.
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -13.
   An envoy from the Kingdom of Italy has arrived with a petition.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 10 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-10)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 90/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (82 → 92); bond -20 → 0 (+0 a turn). Cost: 1 DP.
   ► recall Talleyrand from his mission
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → the court → Cancel (the mission's row), or Recall on the rail.
   ⚜ Take your seat at the table (F1)
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
   ► improve relations with Britain
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Britain. (1 DP/turn)
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 26 sail — readiness 74 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 27 sail — readiness 73 (down 1 — new crews come aboard green at 40; only sea-time makes a navy). 0 more keels possible this turn.
   [4/4 actions remaining]
   ► Soult, march to Flanders
   Soult begins march to Flanders. Route: Artois → Westphalia → Flanders. Moves to Artois.
   Artois feeds 60,000; the 51,834 men standing there would lose ~1,035 a turn to crowding — too many corps on one province. "Soult, march to Flanders." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2731g | Occupation: -15g | Charges of Empire: -955g | Admiralty: -54g | Other: +949g | Upkeep: -976g | Net: +1680g | Spent: 800g
   Treasury: 14,389g
   Actions refreshed: 4/4
   Dumonceau's army is recovering. Effectiveness penalty: -15%.
   Supply shortage at Artois: Davout loses 534 troops
   Supply shortage at Artois: Soult loses 897 troops
   Supply shortage at Artois: Murat loses 484 troops
   Supply shortage at Artois: Napoleon loses 282 troops
   Holland loyalty 85 (-2): satellite drift
   Britain subsidizes Russia with 300 gold.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,465)  Blake(1532,439)  Davout +3(1616,347)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Ney(1538,399)  Cuesta(1563,373)  Dumonceau(1507,344)  Lannes(1673,379)  Moore(1478,370)  Wellesley(1502,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,486)  12k(1581,454)  ?(1769,580)  12k(1716,425)  25k(1490,411)  10k(1910,645)
```

```
#0243  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0243_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 89 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Holland @(3351,64)]  [icon: Davout arrived (x3) @(3393,64)]  [icon: Envoy from Austria @(3435,64)]  [icon: Settlement offer from Britain @(3477,64)]  [icon: Ney arrived (x4) @(3519,64)]  [icon: Lannes arrived (x2) @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   0 →
   T:14
   controls: [THIRD COALITION  ▸]  [War for Munster]  [War for Munster — Britain, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2181 of 2181 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   14,389 (+1,766 next turn)
   Inf:
   99,357
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Treasury: 14,389g
   Actions refreshed: 4/4
   Dumonceau's army is recovering. Effectiveness penalty: -15%.
   Supply shortage at Artois: Davout loses 534 troops
   Supply shortage at Artois: Soult loses 897 troops
   Supply shortage at Artois: Murat loses 484 troops
   Supply shortage at Artois: Napoleon loses 282 troops
   Holland loyalty 85 (-2): satellite drift
   Britain subsidizes Russia with 300 gold.
   --- Strategic Order Updates ---
   Davout: Davout arrives at Artois.
   Artois feeds 60,000; the 68,470 men standing there would lose ~2,197 a turn to short supply. Davout: "Done, and done properly — no stragglers, no surprises."
   Lannes: Lannes marches to Picardy. 1 region to Artois.
   Soult: Soult is marching to Flanders (2 turns remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 15
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Davout, Soult, Murat and Napoleon stand 66,273 men at Artois, which feeds 60,000. 6,273 too many. 2,952 men lost in 2 turns. A supply depot at Artois would ease it; Paris can feed 75,000 more and Friesland can feed 22,500 more — a corps marched there ends it.
   • Sire — a truce with Britain is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
   • Sire — London now pays Sweden 300 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 4 turns (4 DP); buying off her design costs 1,380 gold.
   SITUATION
   France holds 29 regions. Treasury: 14,389g (+1,680 by the accounts)
   The courts at war hold 10 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   > Soult — Artois — 27,051 — Moving to Flanders — 2 turns out. (to the letter)
   - Massena — Milan — 25,007 — 8 turns idle.
   - Davout — Artois — 16,102 — Awaiting orders.
   - Murat — Artois — 14,595 — 7 turns idle.
   - Ney — Normandy — 12,897 — Awaiting orders.
   > Lannes — Picardy — 11,059 — Moving to Artois — arrives next turn.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,525 — Awaiting orders.
   < Dumonceau — East Anglia — 1,864 — Has fallen back 2 times in five turns — now at East Anglia with 1,864 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Moore — London — 37,908 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Cuesta — Normandy — 6,826 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Castanos — Berry — small force [partial]
   Blake — Berry — small force [partial]
   Brunswick — Berlin — large force [last known - T7]
   Shrapnel — London — screening force [last known - T14]
   TURN EVENTS
   Dumonceau's army is recovering. Effectiveness penalty: -15%.
   Supply cost you 2,197 men, at Artois.
   Holland loyalty 85 (-2): satellite drift
   DIPLOMATIC EVENTS
   Sire — Britain and France have signed the Armistice.
   A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -10 for France (2 battles, 0 decisives kept); the war is 13 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -90 and will thaw to -75, short of -60; the ledger and the war's age come back with it. Spain stays at war with Britain — an ally, not a client: her war runs on, and no corps of ours stands on Spanish soil.
   An envoy from Austria has arrived with a proposal.
   Britain, for Britain and Russia, has offered terms to settle the War for Munster — Britain + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -79.
   An envoy from Holland has arrived with a petition.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
   Relations with Britain have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Austria — Open Borders Agreement
   - Britain — Settlement Offer
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 3 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-10)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0244  look  ->  ok
  (a fresh frame)
view: <run>\frames\0244_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2181 of 2181 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0245  click Envoys  ->  ok
  (clicked at (3401, 18))
view: <run>\frames\0245_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Austria
   Proposal
   Open ▸
   Turn 14
   Incoming proposal: Open Borders Agreement
   WAITING
   Britain
   Incoming Settlement Offer
   Open ▸
   Turn 14
   Settlement offer: the War for Munster — Britain + Russia
   WAITING
   Holland
   Proposal
   Open ▸
   Turn 15
   Incoming proposal: Client's Petition
   controls: {ACTIVE}  {WAITING}  {WAITING}  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2181 of 2181 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0246  click_at 1646 274  ->  ok
  (clicked at (1646, 274) on @PanelContainer@7558 'ACTIVE' (PanelContainer, layer 119))
view: <run>\frames\0246_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 24 px] ──
   DIPLOMATIC ENVOY / Metternich (Schemer) of Austria /  / Proposes: Open Borders Agreement / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders /   - Offer: Gold payment - 150 /  / Metternich, with perfect politeness: "Vienna has wanted the same things for a decade; one merely finds this the convenient season to put them in writing. Open the borders." /  / An interesting propos …
   controls: [Accept]  [Let Talleyrand haggle (1 DP)]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2181 of 2181 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   14,389 (+1,766 next turn)
   Inf:
   99,357
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0247  click Accept  ->  ok
  (clicked at (1574, 687))
view: <run>\frames\0247_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   SETTLEMENT OFFER FROM BRITAIN /  / the War for Munster — Britain + Russia /  / "His Majesty's Government offers terms for the War for Munster — Britain + Russia. No indemnity is asked and none is offered; London proposes only that the guns fall silent." /  / Their proposed terms: /   • Peace /   • Status quo: Munster stays ours by the treaty — titled. /  / Covered enemies: Britain, Russia /  / "Si …
   controls: [Review Settlement Offer]  [Request Revision]  [Reject Offer]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 89 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2246 of 2246 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   14,539 (+1,777 next turn)
   Inf:
   99,357
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria.
map: unchanged (53 labels)
```

```
#0248  click Review Settlement Offer  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0248_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 288 px] ──
   Settlement of the War for Munster — the table with Britain + Russia — ready for ratification / the War for Munster — the table with Britain + Russia - Whole-war settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Britain, Russia / Will carry — these are the terms they offered. / Sire, this settlement of the War for Munster — the table wit …
   The table /   * Britain - Their own terms White peace /       Blocker: Settlement legitimacy /       Castlereagh for Britain: these are the terms Britain laid before France; Britain does not haggle with its own dispatch. /   * Russia - Their own terms White peace /       Blocker: Settlement legitimacy /       Czartoryski for Russia: these are the terms Russia laid before France; Russia does not ha …
   Sire, the white peace for the War for Munster — the table with Britain + Russia is ready: no further land changes hands — each side keeps what it holds, now by treaty. Ratify and the field falls quiet. /  / White Peace — on the held line: each side keeps what it holds. / What the treaty titles /   * Status quo: Munster stays ours by the treaty — titled. /  / Allies and Standing /   * Britain - Sea …
   controls: [Ratify White Peace]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 89 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2268 of 2268 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   14,539 (+1,777 next turn)
   Inf:
   99,357
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: accept settlement offer
map: unchanged (53 labels)
```

```
#0249  click Ratify White Peace  ->  ok
  (clicked at (1457, 969))
view: <run>\frames\0249_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Schimmelpenninck (Loyalist) of Holland /  / The petition: /   - Grant it, and Holland's tribute of 337g a turn is remitted for 8 collections (2696g forgone): loyalty +10, its bond with us rises -18 → 2 (worth +0 a turn in loyalty, now -1), for 1 DP. /   - Refuse it, and Holland loses 10 loyalty and its bond with us falls 20 (-18 → -38: worth -2 a turn in loyalty, now -1); not …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 44 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 1828 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Britain
   DP: 6/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (13 turns ago) /  / Naples ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (13 turns ago) /  / Prussia ↔ France: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Sire, the settlement of the War for Munster — the table with Britain + Russia is not a curtain call; it is an accounti>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1783 of 1783 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   14,539 (+2,839 next turn)
   Inf:
   99,357
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   SITUATION
   France holds 29 regions. Treasury: 14,389g (+1,680 by the accounts)
   The courts at war hold 10 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   > Soult — Artois — 27,051 — Moving to Flanders — 2 turns out. (to the letter)
   - Massena — Milan — 25,007 — 8 turns idle.
   - Davout — Artois — 16,102 — Awaiting orders.
   - Murat — Artois — 14,595 — 7 turns idle.
   - Ney — Normandy — 12,897 — Awaiting orders.
   > Lannes — Picardy — 11,059 — Moving to Artois — arrives next turn.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,525 — Awaiting orders.
   < Dumonceau — East Anglia — 1,864 — Has fallen back 2 times in five turns — now at East Anglia with 1,864 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Moore — London — 37,908 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Cuesta — Normandy — 6,826 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Castanos — Berry — small force [partial]
   Blake — Berry — small force [partial]
   Brunswick — Berlin — large force [last known - T7]
   Shrapnel — London — screening force [last known - T14]
   TURN EVENTS
   Dumonceau's army is recovering. Effectiveness penalty: -15%.
   Supply cost you 2,197 men, at Artois.
   Holland loyalty 85 (-2): satellite drift
   DIPLOMATIC EVENTS
   Sire — Britain and France have signed the Armistice.
   A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -10 for France (2 battles, 0 decisives kept); the war is 13 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -90 and will thaw to -75, short of -60; the ledger and the war's age come back with it. Spain stays at war with Britain — an ally, not a client: her war runs on, and no corps of ours stands on Spanish soil.
   An envoy from Austria has arrived with a proposal.
   Britain, for Britain and Russia, has offered terms to settle the War for Munster — Britain + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -79.
   An envoy from Holland has arrived with a petition.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
   Relations with Britain have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Austria — Open Borders Agreement
   - Britain — Settlement Offer
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 3 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-10)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria.
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: confirm settlement
   Settlement Ratified: the War for Munster — the table with Britain + Russia (4 pairs resolved). Status quo: Munster stays ours by the treaty — titled.
   Settlement Ratified
   4 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
map: unchanged (53 labels)
```

```
#0250  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0250_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 44 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Davout arrived (x3) @(3393,64)]  [icon: Ney arrived (x4) @(3435,64)]  [icon: Lannes arrived (x2) @(3477,64)]  [icon: Napoleon arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+30]
── DiplomaticLedger (layer 50) [scrolled 0 of 1828 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   14,539 (+2,502 next turn)
   Inf:
   99,357
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0251  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0251_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0252  click 27 sail  ->  ok
  (clicked at (2943, 18))
view: <run>\frames\0252_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 684 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late April 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 27 sail of the line — readiness 78  (Adm. Villeneuve) /   Posture: guarding home waters /   Yards: Bordelais, Brittany, Normandy, Provence  (0/2 keels this turn) /   The Camp: No army is staged: the camp (Flande …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in Friesland>  <Land Ney in Friesland>  <Land Dumonceau in Normandy>  <Land Dumonceau in Artois>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0253  look  ->  ok
  (a fresh frame)
view: <run>\frames\0253_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 684 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0254  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0254_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0255  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0255_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — Road III, The Continental System: The Blockade of the British Isles — 0 of 26 ports shut to Britain — 13 needed; The Peace of the Continent — Britain has not signed
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 36 titled provinces — 45 are needed (9 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -12 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0256  click Formable Nations  ->  ok
  (clicked at (1825, 562))
view: <run>\frames\0256_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 256 px] ──
   THE CABINET — FORMABLE NATIONS
   DP: 5
   "The map of Europe is not finished, Sire. These states could yet exist — each names what its existence would require."
   States not yet on the map, Sire; each row names what its birth requires. One carved at the table is born your client — it pays tribute and marches when you call; one that forms by conquest rises free.
   Duchy of Warsaw — client state at the settlement table /     • at war with Prussia /     • Posen held at the settlement table (currently Prussia-held)
   Duchy of Normandy — client state at the settlement table /     • carved from France's own provinces — a clause only a victorious enemy may put before you
   Roman Republic — client state at the settlement table /     • at war with Papal States /     • Rome held at the settlement table (currently Papal States-held) /     • a decisive victory over Papal States — erasing a state entirely needs war score 90 (currently 0)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0257  scroll 1700 560 down 15  ->  ok
  (scrolled down 15 at (1700, 560))
view: <run>\frames\0257_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 210 of 256 px] ──
   THE CABINET — FORMABLE NATIONS
   DP: 5
   "The map of Europe is not finished, Sire. These states could yet exist — each names what its existence would require."
   Roman Republic — client state at the settlement table /     • at war with Papal States /     • Rome held at the settlement table (currently Papal States-held) /     • a decisive victory over Papal States — erasing a state entirely needs war score 90 (currently 0)
   Ireland — client state at the settlement table /     • at war with Britain /     • Ulster held at the settlement table (currently Britain-held) /     ✓ Munster held at the settlement table
   United Netherlands — forms by conquest (0 of 1 province held) /     • forms when a free Holland holds its claimed province /     • currently a vassal of France
   Italy — forms by conquest (2 of 5 provinces held) /     • forms when a free Kingdom of Italy holds all 5 of its claimed provinces /     • currently a vassal of France
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0258  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0258_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — Road III, The Continental System: The Blockade of the British Isles — 0 of 26 ports shut to Britain — 13 needed; The Peace of the Continent — Britain has not signed
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 36 titled provinces — 45 are needed (9 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -12 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0259  scroll 1700 560 down 5  ->  ok
  (scrolled down 5 at (1700, 560))
view: <run>\frames\0259_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 181 of 747 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -12 (Wary)]  [Prussia  —  Open Borders  |  -12 (Wary)]  [Spain  —  Alliance  |  +26 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Naples  —  Open Borders  |  -16 (Wary)]  [Portugal  —  Open Borders  |  -19 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0260  look  ->  ok
  (a fresh frame)
view: <run>\frames\0260_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 181 of 747 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0261  click Britain  —  ->  ERROR: no visible control's text holds "Britain  —"
view: <run>\frames\0261_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 181 of 747 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0262  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0262_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0263  type land Dumonceau in Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0263_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
reply: ok The expedition is drawn up, Sire: Dumonceau with 1,864 men, East Anglia to Normandy. No hostile fleet patrols these waters — the passage is unopposed. A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. Sail? (yes / no)
── ClarificationPopup (layer 102) ──
   DUMONCEAU ASKS:
   "The expedition is drawn up, Sire: Dumonceau with 1,864 men, East Anglia to Normandy. No hostile fleet patrols these waters — the passage is unopposed. A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. Sail? (yes / no)"
   controls: [Sail for Normandy]  [Stand down]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 44 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
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
   14,539 (+2,502 next turn)
   Inf:
   99,357
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► land Dumonceau in Normandy
   Dumonceau requests clarification...
map: unchanged (53 labels)
```

```
#0264  click Sail for Normandy  ->  ok
  (clicked at (1829, 524))
view: <run>\frames\0264_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 44 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Davout arrived (x3) @(3393,64)]  [icon: Ney arrived (x4) @(3435,64)]  [icon: Lannes arrived (x2) @(3477,64)]  [icon: Napoleon arrived (x3) @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+30]
── BottomLeftUI (layer 0) [scrolled 2003 of 2003 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   14,539 (+2,502 next turn)
   Inf:
   99,357
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {96}
── MapControls (layer 0): unchanged
── command window, new lines ──
   > land Dumonceau in Normandy confirmed
   THE LANDING: Dumonceau slips past the empty sea and puts 1,864 men ashore at Normandy (odds were 100 in 100).
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,465)  Blake(1532,439)  Davout +3(1616,405)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Ney(1538,399)  Dumonceau(1551,373)  Cuesta(1563,347)  Lannes(1673,379)  Moore(1478,347)  Wellesley(1502,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,486)  12k(1581,454)  ?(1769,580)  12k(1716,425)  25k(1490,411)  10k(1910,645)
```

```
#0265  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0265_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!

Income: 2733g | Occupation: -15g | Charges of Empire: -150g | Upkeep: -952g | Other: +912g | Net: +2528g | Treasury: 17,067g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 15
   PRUSSIA / ──────────────────────────── / - Brunswick recruits troops /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1918 of 1919 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   17,067 (+2,498 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Brunswick — Berlin — large force [last known - T7]
   Shrapnel — London — screening force [last known - T14]
   TURN EVENTS
   Dumonceau's army is recovering. Effectiveness penalty: -15%.
   Supply cost you 2,197 men, at Artois.
   Holland loyalty 85 (-2): satellite drift
   DIPLOMATIC EVENTS
   Sire — Britain and France have signed the Armistice.
   A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -10 for France (2 battles, 0 decisives kept); the war is 13 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -90 and will thaw to -75, short of -60; the ledger and the war's age come back with it. Spain stays at war with Britain — an ally, not a client: her war runs on, and no corps of ours stands on Spanish soil.
   An envoy from Austria has arrived with a proposal.
   Britain, for Britain and Russia, has offered terms to settle the War for Munster — Britain + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -79.
   An envoy from Holland has arrived with a petition.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
   Relations with Britain have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Austria — Open Borders Agreement
   - Britain — Settlement Offer
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Munster) · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 3 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-10)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria.
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: confirm settlement
   Settlement Ratified: the War for Munster — the table with Britain + Russia (4 pairs resolved). Status quo: Munster stays ours by the treaty — titled.
   Settlement Ratified
   4 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -18 → 2 (+0 a turn). Cost: 1 DP.
   ► land Dumonceau in Normandy
   Dumonceau requests clarification...
   > land Dumonceau in Normandy confirmed
   THE LANDING: Dumonceau slips past the empty sea and puts 1,864 men ashore at Normandy (odds were 100 in 100).
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 2733g | Occupation: -15g | Charges of Empire: -150g | Other: +912g | Upkeep: -952g | Net: +2528g
   Treasury: 17,067g
   Actions refreshed: 4/4
   Dumonceau's army has fully recovered and is combat ready.
   Crowded at Artois: Davout loses 483 troops to the press of 4 corps on one province's roads
   Crowded at Artois: Lannes loses 331 troops to the press of 4 corps on one province's roads
   Crowded at Artois: Murat loses 437 troops to the press of 4 corps on one province's roads
   Crowded at Artois: Napoleon loses 255 troops to the press of 4 corps on one province's roads
   Crowded at Normandy: Ney loses 257 troops to the press of 3 corps on one province's roads
   Crowded at Normandy: Dumonceau loses 37 troops to the press of 3 corps on one province's roads
   Crowded at Normandy: Cuesta loses 136 troops to the press of 3 corps on one province's roads
   Supply shortage at Westphalia: Soult loses 300 troops
   Holland loyalty 93 (-2): satellite drift
   Soult's resentment of Ney has cooled with time.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,465)  Blake(1532,439)  Davout +3(1616,399)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Brunswick(1700,300)  Ney(1538,399)  Dumonceau(1551,373)  Cuesta(1563,347)  Soult(1672,335)  Moore(1478,347)  Wellesley(1502,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  ?(1893,372)  25k(1595,486)  12k(1581,454)  ?(1769,580)  12k(1716,420)  25k(1490,411)  10k(1910,645)
```

```
#0266  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0266_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Petition from Switzerland @(3393,64)]  [icon: European Courts Concerned @(3435,64)]  [icon: Lannes arrived (x3) @(3477,64)]  [icon: Davout arrived (x3) @(3519,64)]  [icon: Ney arrived (x4) @(3561,64)]  [+32]
── BottomLeftUI (layer 0) [scrolled 2225 of 2225 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   17,067 (+2,498 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Crowded at Artois: Murat loses 437 troops to the press of 4 corps on one province's roads
   Crowded at Artois: Napoleon loses 255 troops to the press of 4 corps on one province's roads
   Crowded at Normandy: Ney loses 257 troops to the press of 3 corps on one province's roads
   Crowded at Normandy: Dumonceau loses 37 troops to the press of 3 corps on one province's roads
   Crowded at Normandy: Cuesta loses 136 troops to the press of 3 corps on one province's roads
   Supply shortage at Westphalia: Soult loses 300 troops
   Holland loyalty 93 (-2): satellite drift
   Soult's resentment of Ney has cooled with time.
   --- Strategic Order Updates ---
   Lannes: Lannes arrives at Artois.
   Artois feeds 60,000; the 77,332 men standing there would lose ~3,426 a turn to short supply. Lannes: "It is done. Point me at something that shoots back, Sire."
   Soult: Soult marches to Westphalia. 1 region to Flanders.
   Westphalia feeds 15,000; the 26,400 men standing there would lose ~300 a turn to short supply.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 16
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — peace with Britain and Russia is signed. A white peace — the map stands as it was. Dumonceau is marching home under Holland's colours.
   • Sire — our peace binds Britain for 4 more turns and Russia for 4 more turns; then each may join a league (relations −70 and −79).
   • Sire — the establishment stands 10,327 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
   SITUATION
   France holds 29 regions. Treasury: 17,067g (+2,528 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   > Soult — Westphalia — 26,100 — Moving to Flanders — arrives next turn. (to the letter)
   - Massena — Milan — 25,007 — 9 turns idle.
   - Davout — Artois — 15,619 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   - Murat — Artois — 14,158 — 8 turns idle.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   - Ney — Normandy — 12,640 — Awaiting orders.
   - Lannes — Artois — 10,728 — Awaiting orders.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,270 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   > Dumonceau — Normandy — 1,827 — Has fallen back 2 times in five turns — now at Normandy with 1,827 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Moore — London — 37,908 [confirmed]
   Brunswick — Oldenburg — 50,164 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Cuesta — Normandy — 6,690 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Castanos — Berry — small force [partial]
   Blake — Berry — small force [partial]
   Shrapnel — London — screening force [last known - T14]
   TURN EVENTS
   Dumonceau's army has fully recovered and is combat ready.
   Supply cost you 2,100 men, at Artois, Normandy and Westphalia.
   Holland loyalty 93 (-2): satellite drift
   Soult's resentment of Ney has cooled with time.
   DIPLOMATIC EVENTS
   Sire — Austria and France have signed the Open Borders Agreement.
   The coalition against France has dissolved.
   Munster — retained by the peace with Britain, titled by treaty.
   The war Holland shared with France is over — Dumonceau's contingent takes the road home to Amsterdam.
   Sire, the settlement of the War for Munster — the table with Britain + Russia is not a curtain call; it is an accounting. France, Spain must be read beside reactions from 2 courts, and the largest political cost remains settlement ratified.
   THE LANDING: Dumonceau has put 1,864 men ashore at Normandy.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -70.
   An envoy from Switzerland has arrived with a petition.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
   The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
   And Austria stirs at its own design.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: Prussia and 5 lesser courts would march. Bound for now by a fresh peace: Russia, Britain and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0267  click Envoys  ->  ok
  (clicked at (3402, 18))
view: <run>\frames\0267_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond with us rises 20 → 40 (worth +2 a turn in loyalty, now +1), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (20 → 0: worth +0 a turn in loyalty, now …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2225 of 2225 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   17,067 (+2,498 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: Prussia and 5 lesser courts would march. Bound for now by a fresh peace: Russia, Britain and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0268  look  ->  ok
  (a fresh frame)
view: <run>\frames\0268_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2225 of 2225 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: Prussia and 5 lesser courts would march. Bound for now by a fresh peace: Russia, Britain and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0269  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0269_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: Lannes arrived (x3) @(3435,64)]  [icon: Davout arrived (x3) @(3477,64)]  [icon: Ney arrived (x4) @(3519,64)]  [icon: Napoleon arrived (x3) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 2290 of 2290 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   17,067 (+2,273 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {96}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0270  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0270_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!

Income: 2735g | Occupation: -15g | Charges of Empire: -180g | Upkeep: -928g | Other: +687g | Net: +2299g | Treasury: 19,366g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 16
   Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 17 — Late May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2049 of 2049 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   19,366 (+2,271 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   [end turn]  (Tab)
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   • Sire — the establishment stands 10,327 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
   SITUATION
   France holds 29 regions. Treasury: 17,067g (+2,528 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   > Soult — Westphalia — 26,100 — Moving to Flanders — arrives next turn. (to the letter)
   - Massena — Milan — 25,007 — 9 turns idle.
   - Davout — Artois — 15,619 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   - Murat — Artois — 14,158 — 8 turns idle.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   - Ney — Normandy — 12,640 — Awaiting orders.
   - Lannes — Artois — 10,728 — Awaiting orders.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 8,270 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   > Dumonceau — Normandy — 1,827 — Has fallen back 2 times in five turns — now at Normandy with 1,827 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Moore — London — 37,908 [confirmed]
   Brunswick — Oldenburg — 50,164 [confirmed]
   Wellesley — London — 35,000 [confirmed]
   Cuesta — Normandy — 6,690 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Castanos — Berry — small force [partial]
   Blake — Berry — small force [partial]
   Shrapnel — London — screening force [last known - T14]
   TURN EVENTS
   Dumonceau's army has fully recovered and is combat ready.
   Supply cost you 2,100 men, at Artois, Normandy and Westphalia.
   Holland loyalty 93 (-2): satellite drift
   Soult's resentment of Ney has cooled with time.
   DIPLOMATIC EVENTS
   Sire — Austria and France have signed the Open Borders Agreement.
   The coalition against France has dissolved.
   Munster — retained by the peace with Britain, titled by treaty.
   The war Holland shared with France is over — Dumonceau's contingent takes the road home to Amsterdam.
   Sire, the settlement of the War for Munster — the table with Britain + Russia is not a curtain call; it is an accounting. France, Spain must be read beside reactions from 2 courts, and the largest political cost remains settlement ratified.
   THE LANDING: Dumonceau has put 1,864 men ashore at Normandy.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -70.
   An envoy from Switzerland has arrived with a petition.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
   The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
   And Austria stirs at its own design.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: Prussia and 5 lesser courts would march. Bound for now by a fresh peace: Russia, Britain and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 20 → 40 (+2 a turn). Cost: 1 DP.
   ► end turn
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2735g | Occupation: -15g | Charges of Empire: -180g | Other: +687g | Upkeep: -928g | Net: +2299g
   Treasury: 19,366g
   Actions refreshed: 4/4
   Crowded at Artois: Davout loses 624 troops to the press of 5 corps on one province's roads
   Crowded at Artois: Lannes loses 429 troops to the press of 5 corps on one province's roads
   Crowded at Artois: Murat loses 566 troops to the press of 5 corps on one province's roads
   Crowded at Artois: Napoleon loses 330 troops to the press of 5 corps on one province's roads
   Crowded at Artois: Dumonceau loses 73 troops to the press of 5 corps on one province's roads
   Holland loyalty 91 (-2): satellite drift
   Relations between Austria and Russia are deteriorating. Defensive Alliance may collapse in 2 turns.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,465)  Blake(1532,439)  Davout +4(1616,347)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Brunswick(1700,300)  Ney(1538,399)  Cuesta(1563,373)  Soult(1716,418)  ?(1482,371)  Moore(1482,344)  ?(1510,371)  Wellesley(1498,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  25k(1595,486)  12k(1581,454)  ?(1769,580)  ?(1763,420)  12k(1716,446)  ?(1484,417)  10k(1910,645)
```

```
#0271  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0271_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Soult arrived (x3) @(3393,64)]  [icon: European Courts Concerned @(3435,64)]  [icon: Lannes arrived (x3) @(3477,64)]  [icon: Davout arrived (x3) @(3519,64)]  [icon: Ney arrived (x4) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 1875 of 1875 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   19,366 (+2,271 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   [end turn]  (Tab)
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2735g | Occupation: -15g | Charges of Empire: -180g | Other: +687g | Upkeep: -928g | Net: +2299g
   Treasury: 19,366g
   Actions refreshed: 4/4
   Crowded at Artois: Davout loses 624 troops to the press of 5 corps on one province's roads
   Crowded at Artois: Lannes loses 429 troops to the press of 5 corps on one province's roads
   Crowded at Artois: Murat loses 566 troops to the press of 5 corps on one province's roads
   Crowded at Artois: Napoleon loses 330 troops to the press of 5 corps on one province's roads
   Crowded at Artois: Dumonceau loses 73 troops to the press of 5 corps on one province's roads
   Holland loyalty 91 (-2): satellite drift
   Relations between Austria and Russia are deteriorating. Defensive Alliance may collapse in 2 turns.
   --- Strategic Order Updates ---
   Dumonceau: Dumonceau marches to Artois. 3 regions to Amsterdam.
   Artois feeds 60,000; the 50,602 men standing there would lose ~2,022 a turn to crowding — too many corps on one province.
   Soult: "Soult, march to Flanders" — executed as written. Soult arrives at Flanders. Awaiting your next word.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 17
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — the establishment stands 12,276 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
   • Sire — the court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
   • Sire — Europe has watched us 4 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The cheapest court to keep out of it is Portugal: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 29 regions. Treasury: 19,366g (+2,299 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 26,100 — Awaiting orders.
   - Massena — Milan — 25,007 — 10 turns idle.
   - Davout — Artois — 14,995 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, three turns running.
   - Murat — Artois — 13,592 — 9 turns idle.
   ⚠ Crowded — Artois carries more corps than its roads can bear, three turns running.
   - Ney — Normandy — 12,640 — 3 turns idle.
   - Lannes — Artois — 10,299 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 7,940 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, three turns running.
   > Dumonceau — Artois — 1,754 — Has fallen back 2 times in five turns — now at Artois with 1,754 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Brunswick — Oldenburg — 50,164 [confirmed]
   Cuesta — Normandy — 6,690 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Moore — London — substantial force [partial]
   Castanos — Berry — small force [partial]
   Wellesley — London — substantial force [partial]
   Blake — Berry — small force [partial]
   TURN EVENTS
   Supply cost you 2,022 men, at Artois.
   Holland loyalty 91 (-2): satellite drift
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -61.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The depots are full and the ordinance allows it, Sire. Conscripts do not improve with keeping."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0272  type Davout, march to Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0272_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Davout begins march to Paris. Moves to Paris. Davout: "As ordered. I keep my flanks as I go."
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1985 of 1985 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   19,366 (+2,271 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {96}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, march to Paris
   Davout begins march to Paris. Moves to Paris. Davout: "As ordered. I keep my flanks as I go."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,465)  Blake(1532,439)  Lannes +3(1616,347)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Brunswick(1700,300)  Davout(1596,442)  Ney(1538,399)  Cuesta(1563,373)  Soult(1716,418)  ?(1482,371)  Moore(1482,344)  ?(1510,371)  Wellesley(1498,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  25k(1634,486)  12k(1581,470)  ?(1769,580)  ?(1763,420)  12k(1716,446)  ?(1484,417)  10k(1910,645)
```

```
#0273  type Murat, march to Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0273_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Murat begins march to Paris. Moves to Paris. Murat: "At the double, Sire — the men will smell powder soon enough."
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   19,366 (+2,271 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, march to Paris
   Murat begins march to Paris. Moves to Paris. Murat: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,468)  Blake(1523,443)  Lannes(1603,379)  Napoleon(1615,353)  Dumonceau(1628,327)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Brunswick(1700,300)  Davout(1583,442)  Murat(1608,416)  Ney(1538,399)  Cuesta(1539,373)  Soult(1716,418)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  25k(1595,486)  ?(1769,580)  ?(1763,420)  12k(1716,446)  ?(1490,414)  10k(1910,645)
```

```
#0274  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0274_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 17 ended. Turn 18 begins!

Income: 2737g | Occupation: -15g | Charges of Empire: -208g | Upkeep: -928g | Other: +687g | Net: +2273g | Treasury: 21,639g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 17
   SPAIN / ──────────────────────────── / - Cuesta holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1787 of 1789 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   21,639 (+2,246 next turn)
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
   ════════════════════════════════════
   Sire — the establishment stands 12,276 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
   • Sire — the court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
   • Sire — Europe has watched us 4 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The cheapest court to keep out of it is Portugal: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 29 regions. Treasury: 19,366g (+2,299 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 26,100 — Awaiting orders.
   - Massena — Milan — 25,007 — 10 turns idle.
   - Davout — Artois — 14,995 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, three turns running.
   - Murat — Artois — 13,592 — 9 turns idle.
   ⚠ Crowded — Artois carries more corps than its roads can bear, three turns running.
   - Ney — Normandy — 12,640 — 3 turns idle.
   - Lannes — Artois — 10,299 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 7,940 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, three turns running.
   > Dumonceau — Artois — 1,754 — Has fallen back 2 times in five turns — now at Artois with 1,754 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Brunswick — Oldenburg — 50,164 [confirmed]
   Cuesta — Normandy — 6,690 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Moore — London — substantial force [partial]
   Castanos — Berry — small force [partial]
   Wellesley — London — substantial force [partial]
   Blake — Berry — small force [partial]
   TURN EVENTS
   Supply cost you 2,022 men, at Artois.
   Holland loyalty 91 (-2): satellite drift
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -61.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The depots are full and the ordinance allows it, Sire. Conscripts do not improve with keeping."
   ════════════════════════════════════
   ► Davout, march to Paris
   Davout begins march to Paris. Moves to Paris. Davout: "As ordered. I keep my flanks as I go."
   [2/4 actions remaining]
   ► Murat, march to Paris
   Murat begins march to Paris. Moves to Paris. Murat: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 2737g | Occupation: -15g | Charges of Empire: -208g | Other: +687g | Upkeep: -928g | Net: +2273g
   Treasury: 21,639g
   Actions refreshed: 4/4
   Holland loyalty 89 (-2): satellite drift
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,468)  Blake(1523,443)  Lannes(1603,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  ?(1701,295)  Brunswick(1700,266)  Davout(1583,442)  Murat(1608,416)  Ney(1538,399)  Cuesta(1551,353)  Dumonceau(1683,322)  Soult(1716,418)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  25k(1595,486)  ?(1769,580)  ?(1763,420)  12k(1716,446)  ?(1490,414)  10k(1910,645)
```

```
#0275  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0275_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: A Moment of History: The Throne of Holland @(3393,64)]  [icon: Murat arrived (x2) @(3435,64)]  [icon: Davout arrived (x4) @(3477,64)]  [icon: Soult arrived (x3) @(3519,64)]  [icon: European Courts Concerned @(3561,64)]  [+32]
── BottomLeftUI (layer 0) [scrolled 2187 of 2187 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   21,639 (+2,246 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The depots are full and the ordinance allows it, Sire. Conscripts do not improve with keeping."
   ════════════════════════════════════
   ► Davout, march to Paris
   Davout begins march to Paris. Moves to Paris. Davout: "As ordered. I keep my flanks as I go."
   [2/4 actions remaining]
   ► Murat, march to Paris
   Murat begins march to Paris. Moves to Paris. Murat: "At the double, Sire — the men will smell powder soon enough."
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 2737g | Occupation: -15g | Charges of Empire: -208g | Other: +687g | Upkeep: -928g | Net: +2273g
   Treasury: 21,639g
   Actions refreshed: 4/4
   Holland loyalty 89 (-2): satellite drift
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   --- Strategic Order Updates ---
   Davout: Davout arrives at Paris. Davout: "It is done. I took the liberty of posting pickets."
   Dumonceau: Dumonceau marches to Westphalia. 2 regions to Amsterdam.
   Murat: Murat arrives at Paris. Murat: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 18
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Europe has watched us 5 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The cheapest court to keep out of it is Portugal: Talleyrand brings her to −10 in 1 turn (1 DP).
   • Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 12,276 men at Paris, and nobody has gone to collect them.
   SITUATION
   France holds 29 regions. Treasury: 21,639g (+2,273 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 26,100 — Awaiting orders.
   - Massena — Milan — 25,007 — 11 turns idle.
   - Davout — Paris — 14,995 — Awaiting orders.
   - Murat — Paris — 13,592 — Awaiting orders.
   - Ney — Normandy — 12,640 — 4 turns idle.
   - Lannes — Artois — 10,299 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 7,940 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, three turns running.
   > Dumonceau — Westphalia — 1,737 — Has fallen back 2 times in five turns — now at Westphalia with 1,737 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Cuesta — Normandy — 6,690 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Moore — London — substantial force [partial]
   Brunswick — Oldenburg — large force [partial]
   Castanos — Berry — small force [partial]
   Wellesley — London — substantial force [partial]
   Blake — Berry — small force [partial]
   TURN EVENTS
   Holland loyalty 89 (-2): satellite drift
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -52.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0276  click Envoys  ->  ok
  (clicked at (3401, 18))
view: <run>\frames\0276_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A MOMENT OF HISTORY — Early June 1806 / The Throne of Holland — Admiral Ver Huell, for the deputation of the States General lays a letter before the Emperor. / Historically the Dutch deputation under Admiral Ver Huell asked Napoleon for a king and was given his brother Louis (5 June 1806); Grand Pensionary Schimmelpenninck resigned rather than sign. The alternative was annexation, 1810. /   - Holl …
   controls: [Crown Louis]  [Keep the Republic]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2187 of 2187 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   21,639 (+2,246 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0277  click_at 1646 274  ->  ok
  (clicked at (1646, 274) on BackgroundOverlay  (ColorRect, layer 112))
view: <run>\frames\0277_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2187 of 2187 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0278  click Crown Louis  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0278_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Murat arrived (x2) @(3393,64)]  [icon: Davout arrived (x4) @(3435,64)]  [icon: Soult arrived (x3) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Lannes arrived (x3) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 2274 of 2274 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   21,639 (+2,246 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {96}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 89 → 99; its autonomy drift -2 → +1 a turn; tribute 75% → 50%; the ports shut against Britain stay 0 of 26; 1 diplomatic point (you hold 6).
map: unchanged (58 labels)
```

```
#0279  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0279_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — Road III, The Continental System: The Blockade of the British Isles — 0 of 26 ports shut to Britain — 13 needed; The Peace of the Continent — Britain has not signed
   Treaties (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 36 titled provinces — 45 are needed (9 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2274 of 2274 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 89 → 99; its autonomy drift -2 → +1 a turn; tribute 75% → 50%; the ports shut against Britain stay 0 of 26; 1 diplomatic point (you hold 6).
map: unchanged (58 labels)
```

```
#0280  click The Emperor's Designs  ->  ok
  (clicked at (1825, 522))
view: <run>\frames\0280_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 650 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 5
   "The Empire's road is proclaimed, Sire — The Continental System. It cannot be undone, and the other roads are forsworn."
   The Blockade of the British Isles was proclaimed on turn 9: The Continental System.
   Road III — The Continental System (The Blockade of the British Isles) /     ✓ Proclaimed — the Empire's road. /     • The Blockade of the British Isles (the construction) — 0 of 26 ports shut to Britain — 13 needed; to be held 6 end turns /         13 of the Continent's 26 ports shut to Britain, held six end turns — a court at war with her, in the System by a peace's clause, France's satellite, or …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2274 of 2274 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 89 → 99; its autonomy drift -2 → +1 a turn; tribute 75% → 50%; the ports shut against Britain stay 0 of 26; 1 diplomatic point (you hold 6).
map: unchanged (58 labels)
```

```
#0281  look  ->  ok
  (a fresh frame)
view: <run>\frames\0281_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 650 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2274 of 2274 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 89 → 99; its autonomy drift -2 → +1 a turn; tribute 75% → 50%; the ports shut against Britain stay 0 of 26; 1 diplomatic point (you hold 6).
map: unchanged (58 labels)
```

```
#0282  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0282_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2274 of 2274 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 89 → 99; its autonomy drift -2 → +1 a turn; tribute 75% → 50%; the ports shut against Britain stay 0 of 26; 1 diplomatic point (you hold 6).
map: unchanged (58 labels)
```

```
#0283  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0283_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!

Income: 2740g | Occupation: -15g | Charges of Empire: -235g | Upkeep: -928g | Other: +687g | Net: +2249g | Treasury: 23,888g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 18
   SPAIN / ──────────────────────────── / - Cuesta holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1985 of 1985 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   23,888 (+2,222 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   [end turn]  (Tab)
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Treasury: 21,639g
   Actions refreshed: 4/4
   Holland loyalty 89 (-2): satellite drift
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   --- Strategic Order Updates ---
   Davout: Davout arrives at Paris. Davout: "It is done. I took the liberty of posting pickets."
   Dumonceau: Dumonceau marches to Westphalia. 2 regions to Amsterdam.
   Murat: Murat arrives at Paris. Murat: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 18
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Europe has watched us 5 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The cheapest court to keep out of it is Portugal: Talleyrand brings her to −10 in 1 turn (1 DP).
   • Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 12,276 men at Paris, and nobody has gone to collect them.
   SITUATION
   France holds 29 regions. Treasury: 21,639g (+2,273 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 26,100 — Awaiting orders.
   - Massena — Milan — 25,007 — 11 turns idle.
   - Davout — Paris — 14,995 — Awaiting orders.
   - Murat — Paris — 13,592 — Awaiting orders.
   - Ney — Normandy — 12,640 — 4 turns idle.
   - Lannes — Artois — 10,299 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 7,940 — Awaiting orders.
   ⚠ Crowded — Artois carries more corps than its roads can bear, three turns running.
   > Dumonceau — Westphalia — 1,737 — Has fallen back 2 times in five turns — now at Westphalia with 1,737 men. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Cuesta — Normandy — 6,690 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Moore — London — substantial force [partial]
   Brunswick — Oldenburg — large force [partial]
   Castanos — Berry — small force [partial]
   Wellesley — London — substantial force [partial]
   Blake — Berry — small force [partial]
   TURN EVENTS
   Holland loyalty 89 (-2): satellite drift
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -52.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 89 → 99; its autonomy drift -2 → +1 a turn; tribute 75% → 50%; the ports shut against Britain stay 0 of 26; 1 diplomatic point (you hold 6).
   ► end turn
   ═══════════════════════════════════════
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 2740g | Occupation: -15g | Charges of Empire: -235g | Other: +687g | Upkeep: -928g | Net: +2249g
   Treasury: 23,888g
   Actions refreshed: 4/4
   Relations between Austria and Russia have collapsed: Defensive Alliance → Non-Aggression.
   Berthier reports that Soult resents Ney's laurels again, 5 turns after the last — he has thrown himself into his post with obsessive diligence.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  27(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,468)  Blake(1523,443)  Lannes(1603,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Brunswick(1700,300)  Davout(1583,442)  Murat(1608,416)  Ney(1538,399)  Cuesta(1551,353)  Soult(1682,379)  Dumonceau(1803,322)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  25k(1595,486)  ?(1769,580)  10k(1755,420)  12k(1710,420)  ?(1490,414)  10k(1910,645)
```

```
#0284  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0284_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 27 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Marshal Soult seeks an audience @(3393,64)]  [icon: Murat arrived (x2) @(3435,64)]  [icon: Davout arrived (x4) @(3477,64)]  [icon: Soult arrived (x3) @(3519,64)]  [icon: European Courts Concerned @(3561,64)]  [+32]
── BottomLeftUI (layer 0) [scrolled 1743 of 1743 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   23,888 (+2,222 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   [end turn]  (Tab)
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 2740g | Occupation: -15g | Charges of Empire: -235g | Other: +687g | Upkeep: -928g | Net: +2249g
   Treasury: 23,888g
   Actions refreshed: 4/4
   Relations between Austria and Russia have collapsed: Defensive Alliance → Non-Aggression.
   Berthier reports that Soult resents Ney's laurels again, 5 turns after the last — he has thrown himself into his post with obsessive diligence.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   --- Strategic Order Updates ---
   Dumonceau: Dumonceau marches to Flanders. 1 region to Amsterdam.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — relations between Austria and Russia have collapsed: Defensive Alliance → Non-Aggression.
   • Sire — Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
   • Sire — Europe has watched us 6 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The cheapest court to keep out of it is Portugal: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 29 regions. Treasury: 23,888g (+2,249 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 26,100 — Awaiting orders.
   - Massena — Milan — 25,007 — 12 turns idle.
   - Davout — Paris — 14,995 — Awaiting orders.
   - Murat — Paris — 13,592 — Awaiting orders.
   - Ney — Normandy — 12,640 — 5 turns idle.
   - Lannes — Artois — 10,299 — 3 turns idle.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 7,940 — Awaiting orders.
   > Dumonceau — Flanders — 1,737 — Moving to Amsterdam — arrives next turn. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Brunswick — Oldenburg — 50,164 [confirmed]
   Cuesta — Normandy — 6,690 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Moore — London — substantial force [partial]
   Castanos — Berry — small force [partial]
   Wellesley — London — substantial force [partial]
   Blake — Berry — small force [partial]
   TURN EVENTS
   Berthier reports that Soult resents Ney's laurels again, 5 turns after the last — he has thrown himself into his post with obsessive diligence.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   DIPLOMATIC EVENTS
   THE LAWS: Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Russia brings the Divisional System into force beside its Staff — Slow to concentrate is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -43.
   Relations between Austria and Russia have collapsed: Defensive Alliance → Non-Aggression.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Soult nurses a grievance against Ney, Sire. The rivalry wants settling before it is tested."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0285  type lay down a ship of the line  ->  ok
  (typed and Enter)
view: <run>\frames\0285_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok A keel is laid at Bordelais (400g). The fleet stands at 28 sail — readiness 96 (down 2 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Marshal Soult seeks an audience @(3393,64)]  [icon: Murat arrived (x2) @(3435,64)]  [icon: Davout arrived (x4) @(3477,64)]  [icon: Soult arrived (x3) @(3519,64)]  [icon: European Courts Concerned @(3561,64)]  [+32]
── BottomLeftUI (layer 0) [scrolled 1875 of 1875 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   23,488 (+2,202 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {96}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 28 sail — readiness 96 (down 2 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  28(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,468)  Blake(1523,443)  Lannes(1603,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Brunswick(1700,300)  Davout(1583,442)  Murat(1608,416)  Ney(1538,399)  Cuesta(1551,353)  Soult(1682,379)  Dumonceau(1803,322)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  25k(1595,486)  ?(1769,580)  10k(1755,420)  12k(1710,420)  ?(1490,414)  10k(1910,645)
```

```
#0286  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0286_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!

Income: 2740g | Occupation: -15g | Charges of Empire: -257g | Upkeep: -928g | Other: +662g | Net: +2202g | Spent: 400g | Treasury: 25,690g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 19
   SPAIN / ──────────────────────────── / - Cuesta holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 20 — Early July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2121 of 2121 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   25,690 (+2,200 next turn)
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
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2740g | Occupation: -15g | Charges of Empire: -257g | Other: +662g | Upkeep: -928g | Net: +2202g | Spent: 400g
   Treasury: 25,690g
   Actions refreshed: 4/4
   Dumonceau's contingent comes home decimated — 1,720 of 6,500 men. Holland counts its widows (-5 loyalty).
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  28(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,468)  Blake(1523,443)  Lannes(1603,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Brunswick(1700,300)  Davout(1583,442)  Murat(1608,416)  Ney(1538,399)  Cuesta(1551,353)  Soult(1716,418)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  25k(1595,486)  ?(1769,580)  10k(1764,420)  12k(1716,446)  ?(1490,414)  10k(1910,645)
```

```
#0287  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0287_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Dumonceau arrived (x2) @(3393,64)]  [icon: Marshal Soult seeks an audience @(3435,64)]  [icon: Murat arrived (x2) @(3477,64)]  [icon: Davout arrived (x4) @(3519,64)]  [icon: Soult arrived (x3) @(3561,64)]  [+33]
── BottomLeftUI (layer 0) [scrolled 2339 of 2339 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   25,690 (+2,200 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Wellesley — London — substantial force [partial]
   Blake — Berry — small force [partial]
   TURN EVENTS
   Berthier reports that Soult resents Ney's laurels again, 5 turns after the last — he has thrown himself into his post with obsessive diligence.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   DIPLOMATIC EVENTS
   THE LAWS: Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Russia brings the Divisional System into force beside its Staff — Slow to concentrate is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -43.
   Relations between Austria and Russia have collapsed: Defensive Alliance → Non-Aggression.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: 5 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Soult nurses a grievance against Ney, Sire. The rivalry wants settling before it is tested."
   ════════════════════════════════════
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 28 sail — readiness 96 (down 2 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2740g | Occupation: -15g | Charges of Empire: -257g | Other: +662g | Upkeep: -928g | Net: +2202g | Spent: 400g
   Treasury: 25,690g
   Actions refreshed: 4/4
   Dumonceau's contingent comes home decimated — 1,720 of 6,500 men. Holland counts its widows (-5 loyalty).
   --- Strategic Order Updates ---
   Dumonceau: Dumonceau arrives at Amsterdam. Dumonceau: "It is done. I took the liberty of posting pickets."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 20
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 26 and declare on turn 29: Russia, Britain and 5 lesser courts would march.
   • Sire — Britain and Russia would now join a league against us (relations −34 and −75). The Balance of Europe names the price to keep each out.
   SITUATION
   France holds 29 regions. Treasury: 25,690g (+2,202 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 26,100 — Awaiting orders.
   - Massena — Milan — 25,007 — 13 turns idle.
   - Davout — Paris — 14,995 — Awaiting orders.
   - Murat — Paris — 13,592 — Awaiting orders.
   - Ney — Normandy — 12,640 — 6 turns idle.
   - Lannes — Artois — 10,299 — 4 turns idle.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 7,940 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Oldenburg — 50,164 [confirmed]
   Cuesta — Normandy — 6,690 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Moore — London — substantial force [partial]
   Castanos — Berry — small force [partial]
   Wellesley — London — substantial force [partial]
   Blake — Berry — small force [partial]
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -34.
   Dumonceau's contingent comes home decimated — 1,720 of 6,500 men. Holland counts its widows (-5 loyalty).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 16 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Russia, Britain and 5 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0288  type end turn  ->  ok
  (typed and Enter)
view: <run>\frames\0288_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!

Income: 2740g | Occupation: -15g | Charges of Empire: -284g | Upkeep: -928g | Other: +687g | Net: +2200g | Treasury: 27,890g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 20
   SPAIN / ──────────────────────────── / - Cuesta holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 21 — Late July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 28 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1989 of 1989 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   21
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   27,890 (+2,174 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   [end turn]  (Tab)
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   ► lay down a ship of the line
   A keel is laid at Bordelais (400g). The fleet stands at 28 sail — readiness 96 (down 2 — new crews come aboard green at 40; only sea-time makes a navy). 1 more keel possible this turn.
   [4/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2740g | Occupation: -15g | Charges of Empire: -257g | Other: +662g | Upkeep: -928g | Net: +2202g | Spent: 400g
   Treasury: 25,690g
   Actions refreshed: 4/4
   Dumonceau's contingent comes home decimated — 1,720 of 6,500 men. Holland counts its widows (-5 loyalty).
   --- Strategic Order Updates ---
   Dumonceau: Dumonceau arrives at Amsterdam. Dumonceau: "It is done. I took the liberty of posting pickets."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 20
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 26 and declare on turn 29: Russia, Britain and 5 lesser courts would march.
   • Sire — Britain and Russia would now join a league against us (relations −34 and −75). The Balance of Europe names the price to keep each out.
   SITUATION
   France holds 29 regions. Treasury: 25,690g (+2,202 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 26,100 — Awaiting orders.
   - Massena — Milan — 25,007 — 13 turns idle.
   - Davout — Paris — 14,995 — Awaiting orders.
   - Murat — Paris — 13,592 — Awaiting orders.
   - Ney — Normandy — 12,640 — 6 turns idle.
   - Lannes — Artois — 10,299 — 4 turns idle.
   - Bernadotte — Franche-Comte — 9,651 — Awaiting orders. Trust:40 Morale:45%
   - Napoleon — Artois — 7,940 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Oldenburg — 50,164 [confirmed]
   Cuesta — Normandy — 6,690 [confirmed]
   Deroy — Swabia — substantial force [partial]
   Moore — London — substantial force [partial]
   Castanos — Berry — small force [partial]
   Wellesley — London — substantial force [partial]
   Blake — Berry — small force [partial]
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -34.
   Dumonceau's contingent comes home decimated — 1,720 of 6,500 men. Holland counts its widows (-5 loyalty).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   THE EMPEROR'S DESIGNS
   Road III, The Continental System — • The Blockade of the British Isles: 0 of 26 ports shut to Britain — 13 needed (to be held 6 end turns) · • The Peace of the Continent: Britain has not signed
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 16 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Russia, Britain and 5 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 21 BEGINS
   ═══════════════════════════════════════
   Income: 2740g | Occupation: -15g | Charges of Empire: -284g | Other: +687g | Upkeep: -928g | Net: +2200g
   Treasury: 27,890g
   Actions refreshed: 4/4
   Berthier notes that Soult no longer presses the matter — his quarrel with Ney has cooled.
   Soult's resentment of Ney has cooled with time.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 96(1396,395)  28(1374,592)  17(1416,737)  19(1971,161)  18(1948,118)  15(2234,635)  6(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1517,504)  Castanos(1517,468)  Blake(1523,443)  Lannes(1603,379)  Napoleon(1627,353)  ?(1859,469)  Deroy(1859,430)  Bernadotte(1812,497)  Brunswick(1700,300)  Davout(1583,442)  Murat(1608,416)  Ney(1538,399)  Cuesta(1551,353)  Soult(1716,418)  ?(1482,371)  Moore(1482,344)  Wellesley(1498,287)  Massena(1910,589)  ?(1859,530)  ?(1901,561)  25k(1595,486)  ?(1769,580)  ?(1763,420)  12k(1716,446)  ?(1490,414)  10k(1910,645)
```

```
#0289  quit  ->  ok
  (the engine quits)
view: <run>\frames\0289_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1989 of 1989 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Treasury: 27,890g
   Actions refreshed: 4/4
   Berthier notes that Soult no longer presses the matter — his quarrel with Ney has cooled.
   Soult's resentment of Ney has cooled with time.
map: unchanged (56 labels)
```

