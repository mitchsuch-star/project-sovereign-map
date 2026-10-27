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
   controls: [Begin the 1805 Campaign]  [The School of War — a guided campaign]  [The School of War — The Table (a guided peace)]  [Continue  ·  Early February 1806]  [Load a Campaign…]  [Settings]  [Quit to Desktop]
```

```
#0001  click Looks right  ->  ok
  (clicked at (1960, 669))
view: <run>\frames\0001_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=[], region_panel=no, other=['main_menu']
── TitleBlock (layer 0): unchanged
── StatusLine (layer 0): unchanged
── PaintingCaption (layer 0): unchanged
── VersionLine (layer 0): unchanged
── MenuColumn (layer 0): unchanged
```

```
#0002  click Load a Campaign…  ->  ok
  (clicked at (490, 690))
view: <run>\frames\0002_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 480 px] ──
   LOAD GAME
   controls: [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [Cancel]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 552 of 552 px] ──
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
── MapControls (layer 0) [under a modal] ──
   controls: [icon: Zoomed out as far as the map goes — the whole theatre is in  @(1794,992)](disabled: Zoomed out as far as the map goes — the whole theatre is in view)  [icon: The whole theatre is already in view @(1828,992)](disabled: The whole theatre is already in view)  [icon: Zoom in  (+) @(1862,992)]
── command window, new lines ──
   ═══════════════════════════════════════
   IMPERIAL HEADQUARTERS
   ═══════════════════════════════════════
   September 1805 — The War of the Third Coalition
   You are Napoleon Bonaparte.
   Establishing connection to headquarters...
   ✓ Communications established!
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
   • "what if Ney attacks Mack" — free: it names who marches with him before you commit
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Berthier: "Sire, the staff will read your orders as written. Should you wish the clerks to puzzle out unusual phrasings, see Settings — Smarter Parsing (optional)."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1838,471)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,645)
```

```
#0003  click replay_opening  ->  ok
  (clicked at (1825, 510))
view: <run>\frames\0003_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
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
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_opening
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
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0004  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0004_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0005  scroll 1280 400 down 5  ->  ok
  (scrolled down 5 at (1280, 400))
view: <run>\frames\0005_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0006  click Satisfy their design  ->  ERROR: no visible control's text holds "Satisfy their design"
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0007  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0008  scroll 2560 800 down 5  ->  ok
  (scrolled down 5 at (2560, 800))
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0009  look  ->  ok
  (a fresh frame)
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0010  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0011  scroll 2500 700 down 3  ->  ok
  (scrolled down 3 at (2500, 700))
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0012  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0013  scroll 1828 550 down 3  ->  ok
  (scrolled down 3 at (1828, 550))
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 150 of 733 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0014  click Britain  —  At War  ->  ok
  (clicked at (1825, 477))
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 282 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War with the Third Coalition   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — the court sees no reason to sign at +0: Propose Peace stands at -7 of 50; it wants her loyalty to the league — she has no reason of he …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Propose Armistice (1 DP)  —  Hopeless]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px] ──
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0015  scroll 1828 550 down 4  ->  ok
  (scrolled down 4 at (1828, 550))
view: <run>\frames\0015_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 398 px, 130 of 240 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War with the Third Coalition   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — the court sees no reason to sign at +0: Propose Peace stands at -7 of 50; it wants her loyalty to the league — she has no reason of he …
   France is at war with this court.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn]  [Buy Off Their Design (1308g) (1 DP + 1308g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. It buys the design's sleep, not her goodwill: +5 relations (−90 → −85); she still counts toward a league until relations reach −10. No other design wakes after it.](disabled: France is at war with this court.)  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured. Honouring it means declaring on the aggressor: France's relations fall 30 with that court and 15 with every other (15 and 7 after a rejected ultimatum).](disabled: France is at war with this court.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0016  click Satisfy  ->  ERROR: no visible control's text holds "Satisfy"
view: <run>\frames\0016_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 398 px, 130 of 240 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0017  click Back  ->  ok
  (clicked at (1774, 788))
view: <run>\frames\0017_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0018  scroll 1828 550 down 10  ->  ok
  (scrolled down 10 at (1828, 550))
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 479 of 719 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0019  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0019_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0020  click Talleyrand: Idle  ->  ok
  (clicked at (3264, 18))
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 24 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 5/5
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 5/5 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Idle — no active diplomatic mission. /  / PROPOSAL IN TRANSIT /   None /  / PENDING ENVOYS /   0 envoys awaiting response /  / SABOTAGE WARNINGS /   None detected. /  / DIPLOMAT …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0021  click Assess the Situation  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 222 px] ──
   TALLEYRAND'S ASSESSMENT /  / "Sire — the state of Europe, plainly told. /  /   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1) /  /   Against Britain + Austria + Russia: the war hangs in the balance (+0) — 0 battles across 0 turns. /     Britain's design: The Low Countries — They will not suffer France's bloc in Flanders. /     Their price: prepared to go as far as war — Fra …
   ▼ more below
   controls: [icon: Close (Esc) @(2151,292)]  [Satisfy their design (Britain)]  [Thank you]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1544 of 1544 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Talleyrand, assess our situation
map: unchanged (53 labels)
```

```
#0022  click Satisfy their design  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 508 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / France concedes: /   • France cedes Flanders to Britain / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS / Revanche lapses: France's cession of Flanders reconciles her Revanche while the treaty holds. /  / Acceptance Estimate / Score: 21 - REJECT / Key advantage: Base Disposition / Key obstacle: Coalition L …
   ▼ more below
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: expand options
map: unchanged (53 labels)
```

```
#0023  scroll 1828 550 down 10  ->  ok
  (scrolled down 10 at (1828, 550))
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 440 of 508 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / France concedes: /   • France cedes Flanders to Britain / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS / Revanche lapses: France's cession of Flanders reconciles her Revanche while the treaty holds. /  / Acceptance Estimate / Score: 21 - REJECT / Key advantage: Base Disposition / Key obstacle: Coalition L …
   ▼ more below
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► Talleyrand, assess our situation
   Directing Talleyrand: expand options
map: unchanged (53 labels)
```

```
#0024  scroll 1828 550 down 10  ->  ok
  (scrolled down 10 at (1828, 550))
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 504 of 504 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / France concedes: /   • France cedes Flanders to Britain / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS / Revanche lapses: France's cession of Flanders reconciles her Revanche while the treaty holds. /  / Acceptance Estimate / Score: 21 - REJECT / Key advantage: Base Disposition / Key obstacle: Coalition L …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► Talleyrand, assess our situation
   Directing Talleyrand: expand options
map: unchanged (53 labels)
```

```
#0025  scroll 1828 550 up 3  ->  ok
  (scrolled up 3 at (1828, 550))
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 374 of 508 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / France concedes: /   • France cedes Flanders to Britain / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS / Revanche lapses: France's cession of Flanders reconciles her Revanche while the treaty holds. /  / Acceptance Estimate / Score: 21 - REJECT / Key advantage: Base Disposition / Key obstacle: Coalition L …
   ▼ more below
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► Talleyrand, assess our situation
   Directing Talleyrand: expand options
map: unchanged (53 labels)
```

```
#0026  click Not Now  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1631 of 1631 px] ──
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (53 labels)
```

```
#0027  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1631 of 1631 px] ──
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Talleyrand, assess our situation
   Directing Talleyrand: expand options
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (53 labels)
```

```
#0028  type who am I fighting  ->  ok
  (typed and Enter)
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +0 (evenly matched), declared this turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the ACTIVE WARS banner in the lower right (click the war); every court's design in the Diplomatic Ledger (press D, or Alt+D while you type).
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1787 of 1787 px] ──
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
   ► who am I fighting
   We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +0 (evenly matched), declared this turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the ACTIVE WARS banner in the lower right (click the war); every court's design in the Diplomatic Ledger (press D, or Alt+D while you type).
map: unchanged (53 labels)
```

```
#0029  type what if Massena attacks Archduke John  ->  ok
  (typed and Enter)
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
  The band weighs a force of his you have not scouted — scout Carniola.
  On the men in view alone the odds read 'favorable' (42,000 against a substantial force).
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
  (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)

Nothing has been ordered, and nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1632 of 1632 px] ──
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
   ► what if Massena attacks Archduke John
   Were you to give the order, Sire:
   MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
   The band weighs a force of his you have not scouted — scout Carniola.
   On the men in view alone the odds read 'favorable' (42,000 against a substantial force).
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0030  click Vienna  ->  ERROR: no visible control's text holds "Vienna"
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1632 of 1632 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0031  click_at 2078 600  ->  ok
  (clicked at (2078, 600) on MapArea '100' (Control, layer 0))
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 111 px] ──
   Hungary
   Austria  City · Plains / Stripped? unknown — scout it / ACTIONS /     No landing here    only Napoleon's Guard is under the 15,000 lift, and the Emperor does not sail on an expedition — a new marshal's 5,000-man corps is under it from the day he is raised /  / One province — who holds it, what it pays, what defends it. Click the map to choose another. / No intelligence — scout or advance to learn  …
   controls: [icon @(535,73)]  <Murat · 1 AP · 2 turns>  <Bernadotte · 2 AP · 2 turns>  <Massena · 1 AP · 3 turns>  <Lannes · 1 AP · 4 turns>  <Napoleon · 1 AP · 4 turns>  <+3 more…>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2163 of 2163 px] ──
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0032  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2163 of 2163 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0033  key G  ->  ok
  (pressed G)
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 5265 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Esc closes it (Alt+G while you type). /  /   OUR DOCTRINE — The Corps System  ▸ the doctrine /  /   THE EMPEROR /   / [8] Napoleon  [Infantry]  France / In the field at Lorraine — The Presence goes where he stands. /   ★ The Presence  +10% here at Lorraine  Every French corps fighting in the Emperor's pro …
   controls: [Pin]  [icon @(2213,236)]  <▸ the doctrine>  <Fortify (2 AP)>  <Hold (1 AP)>  <Fall back>  <Commission a Marshal…>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (1 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0034  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0035  look  ->  ok
  (a fresh frame)
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0036  key q  ->  ok
  (pressed q)
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0037  key G  ->  ok
  (pressed G)
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 5265 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Esc closes it (Alt+G while you type). /  /   OUR DOCTRINE — The Corps System  ▸ the doctrine /  /   THE EMPEROR /   / [8] Napoleon  [Infantry]  France / In the field at Lorraine — The Presence goes where he stands. /   ★ The Presence  +10% here at Lorraine  Every French corps fighting in the Emperor's pro …
   controls: [Pin]  [icon @(2213,236)]  <▸ the doctrine>  <Fortify (2 AP)>  <Hold (1 AP)>  <Fall back>  <Commission a Marshal…>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (1 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0038  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0039  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0039_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0040  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0040_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0041  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0041_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  What Swabia can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses an
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   18,000 → 17,006
   Murat
   22,000 → 21,514
   Davout
   26,000 → 24,852
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 22,230 → 21,909 after the advance
   52,000 → 28,838
   marched to the guns
   marched to the guns
   +2 corps in reserve — 441 lost
   Soult — awaits explicit orders
   THE GREAT BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 78 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +20 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2326 of 2326 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   559 (−80 next turn)
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► who am I fighting
   We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +0 (evenly matched), declared this turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the ACTIVE WARS banner in the lower right (click the war); every court's design in the Diplomatic Ledger (press D, or Alt+D while you type).
   ► what if Massena attacks Archduke John
   Were you to give the order, Sire:
   MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
   The band weighs a force of his you have not scouted — scout Carniola.
   On the men in view alone the odds read 'favorable' (42,000 against a substantial force).
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
   ► Ney, attack Mack
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 100,000 we muster) would cost ~750g.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −1,200g more a turn.
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney engages in solid combat. Ney gains the advantage over Mack. Casualties: Ney's army 4,839, Mack 23,162. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -241g, Austria -1158g. Our treasury stands at 559 gold. Ney advances into Swabia. (321 lost to march) Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. Swabia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   [!] MARSHAL CAPTURED — Mack is taken by France at Swabia! 14,419 of his men escape home to the depots.
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
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
   Napoleon's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 90,642 committed (Davout, Lannes, Murat, Napoleon) = 114,642.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,069 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 1,770 | Mack 23,162
   Strength: Ney 24,000 → 22,230 → 21,909 after the advance | Mack 52,000 → 28,838
   Berthier: "Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire. And Mack was taken on that field — France holds him."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney +4(1847,444)  ?(1965,579)  Archduke John(1948,540)  Soult(1753,436)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0042  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0042_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2326 of 2326 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   559 (−80 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (48 labels)
```

```
#0043  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0043_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2326 of 2326 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (48 labels)
```

```
#0044  look  ->  ok
  (a fresh frame)
view: <run>\frames\0044_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2326 of 2326 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (48 labels)
```

```
#0045  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0045_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2326 of 2326 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (48 labels)
```

```
#0046  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0046_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 136 px] ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 4,575 casualties, 49,425 remaining /     Massena: 5,242 casualties, 36,758 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Archduke Charles: "France pays …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 77 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2817 of 2819 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   479 (+182 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 100,000 we muster) would cost ~750g.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −1,200g more a turn.
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney engages in solid combat. Ney gains the advantage over Mack. Casualties: Ney's army 4,839, Mack 23,162. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -241g, Austria -1158g. Our treasury stands at 559 gold. Ney advances into Swabia. (321 lost to march) Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. Swabia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   [!] MARSHAL CAPTURED — Mack is taken by France at Swabia! 14,419 of his men escape home to the depots.
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
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
   Napoleon's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 90,642 committed (Davout, Lannes, Murat, Napoleon) = 114,642.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,069 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 1,770 | Mack 23,162
   Strength: Ney 24,000 → 22,230 → 21,909 after the advance | Mack 52,000 → 28,838
   Berthier: "Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire. And Mack was taken on that field — France holds him."
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
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -262g | Other: +1295g | Upkeep: -3394g | Net: -80g
   Treasury: 479g
   Actions refreshed: 4/4
   Supply shortage at Swabia: Ney loses 1,067 troops
   Supply shortage at Swabia: Davout loses 1,210 troops
   Supply shortage at Swabia: Lannes loses 828 troops
   Supply shortage at Swabia: Murat loses 1,047 troops
   Supply shortage at Swabia: Napoleon loses 465 troops
   Supply shortage at Tyrol: Archduke Charles loses 1,468 troops
   Supply shortage at Tyrol: Archduke John loses 594 troops
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Soult at Lorraine. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney +4(1847,444)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,579)  Archduke John(2015,511)  Soult(1753,436)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0047  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0047_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   42,000 → 36,758
   54,000 → 49,425
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 77 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Envoy from Prussia @(3487,62)]  [icon: Envoy from Ottoman Empire @(3529,62)]  [icon: Envoy from Portugal @(3571,62)]  [icon: Marshal Murat seeks an audience @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +20 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   479 (+182 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — General Mack of Austria is taken at Swabia — he is our prisoner, and their order of battle is one commander shorter.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 479g (+182 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 44% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 36,758 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 23,642 — Awaiting orders.
   - Ney — Swabia — 20,842 — Awaiting orders.
   - Murat — Swabia — 20,467 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Lannes — Swabia — 16,178 — Awaiting orders.
   - Napoleon — Swabia — 9,094 — Awaiting orders.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 4,617 men, at Swabia.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   DIPLOMATIC EVENTS
   War exhaustion grows — Austria nears breaking point (exhaustion: 20).
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Soult at Lorraine. Holland pays them; their dead will be its grief.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+20)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0048  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0048_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1784 of 1784 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   479 (+182 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0049  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0049_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1784 of 1784 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   479 (+182 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0050  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0050_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0051  look  ->  ok
  (a fresh frame)
view: <run>\frames\0051_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0052  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0052_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 528 px] ──
   LOAD GAME
   controls: [Autosave - Turn 2 (Turn 2)]  [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0053  click replay_liberation  ->  ERROR: no visible control's text holds "replay_liberation"
view: <run>\frames\0053_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0054  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0054_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 290 of 528 px] ──
   LOAD GAME
   controls: [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0055  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0055_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0056  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0056_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 77/100 [Formed] — up 7 since yesterday (Won a decisive battle +5, Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, 1 smaller cause +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0057  click replay_liberation  ->  ok
  (clicked at (1825, 558))
view: <run>\frames\0057_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 84 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munich
   0 →
   T:2
   controls: [THIRD COALITION  ▸]  [War for Munich]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+540 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_liberation
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+540 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 16% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Swabia — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   > Napoleon — Lorraine — 10,000 — Moving to Flanders — 2 turns out.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Munich — screening force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Mack
   • Davout, march to Swabia
   • recruit infantry in Rhineland — 741g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2109,531)  France(1596,525)  Bavaria(1910,487)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney(1859,459)  Davout(1830,397)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1825,433)  Mack(1901,514)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,645)
```

```
#0058  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0058_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (24,000; expect about 109,247 with the corps likely to arrive, up to 118,036 if all march; certain 24,000; a bad day (1 in 10) 97,607) vs Mack (screening force) at Munich — the balance of force looks favorable.
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Munich
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Munich can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 106,000 we muster) would cost ~795g.
  A win here adds +3 to 
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   18,000 → 17,905
   Murat
   22,000 → 21,954
   ⚔
   Ney ◆
   Mack ◆
   24,000 → 23,829 → 22,988 after the advance
   2,500 → 0
   marched to the guns
   marched to the guns
   +1 corps in reserve
   Bernadotte — weighed his own ambitions
   BATTLE OF MUNICH
   click anywhere to skip ▸
   MUNICH · TURN 3
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 87 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +6 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1852 of 2123 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   785 (+184 next turn)
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
   • build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► Ney, attack Mack
   ⚔ Battle of Munich ⚔
   MUSTER — Ney (24,000; expect about 109,247 with the corps likely to arrive, up to 118,036 if all march; certain 24,000; a bad day (1 in 10) 97,607) vs Mack (screening force) at Munich — the balance of force looks favorable.
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 106,000 we muster) would cost ~795g.
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 84/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Terrain] Mack benefits from Mountains terrain (+25% defense)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney delivers an effective strike. Ney decisively defeats Mack! Mack's army is destroyed. Ney's army suffered 312 casualties.
   [Materiel] Guns, horses and stores lost with the fallen: France -15g, Austria -142g. Our treasury stands at 785 gold. Mack's army is destroyed! Ney advances into Munich. (841 lost to march) Munich, Bavaria's capital, retaken — handed back to Bavaria.
   [Alarm] Europe's alarm rises +3 — Won a battle +3.
   ★ Enemy army destroyed! ★
   ⚑ Munich — handed back to Bavaria ⚑
   ⚔ View the field
   [3/4 actions remaining]
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
   Massena was nearly in position, but fate intervened at the crucial moment.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 41,090 committed (Lannes, Murat) = 65,090.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 141 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Attack: Ney (Personality (aggressive) +15%)
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 171 | Mack 2,500
   Strength: Ney 24,000 → 23,829 → 22,988 after the advance | Mack 2,500 → 0
   Berthier: "Reinforcements from Lannes and Murat bolstered Ney's position — though Bernadotte and Massena never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Davout(1830,397)  ?(1948,562)  Archduke John(2032,540)  Soult(1741,436)  Napoleon(1764,462)  Ney(1888,535)  Lannes(1901,561)  Murat(1938,528)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,645)
```

```
#0059  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0059_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1852 of 2123 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   785 (+184 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (51 labels)
```

```
#0060  scroll 500 700 up 4  ->  ok
  (scrolled up 4 at (500, 700))
view: <run>\frames\0060_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1588 of 2123 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   785 (+184 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (51 labels)
```

```
#0061  key L  ->  ok
  (pressed L)
view: <run>\frames\0061_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=['event_log'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── CampaignLog (layer 50) ──
   CAMPAIGN LOG
   Battle of Munich: Ney (France) attacked Mack (Austria) — Ney decisive victory (312 / 2,500 casualties)
   Ney → Murat: +1 (Professional)
   Murat → Ney: +1 (Professional)
   General Mack's corps DESTROYED at Munich by France
   Munich, Bavaria's capital, retaken by France — handed back to Bavaria.
   controls: [Pin]  [icon: Esc closes it (Alt+L while you type) @(2143,296)]  [▾ Turn 3  -  5 events]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1588 of 2123 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (51 labels)
```

```
#0062  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0062_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +6 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1588 of 2123 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (51 labels)
```

```
#0063  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0063_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 444 px] ──
   ENEMY PHASE - Turn 3
   AUSTRIA / ──────────────────────────── / - Archduke Charles moves to Tyrol / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 4,303 casualties, 49,697 remaining /     Massena: 5,713 casualties, 36,287 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%)  …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 86 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2727 of 2727 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   823 (+572 next turn)
   Inf:
   82,262
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ⚔ Battle of Munich ⚔
   MUSTER — Ney (24,000; expect about 109,247 with the corps likely to arrive, up to 118,036 if all march; certain 24,000; a bad day (1 in 10) 97,607) vs Mack (screening force) at Munich — the balance of force looks favorable.
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 106,000 we muster) would cost ~795g.
   A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 84/100.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Terrain] Mack benefits from Mountains terrain (+25% defense)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney delivers an effective strike. Ney decisively defeats Mack! Mack's army is destroyed. Ney's army suffered 312 casualties.
   [Materiel] Guns, horses and stores lost with the fallen: France -15g, Austria -142g. Our treasury stands at 785 gold. Mack's army is destroyed! Ney advances into Munich. (841 lost to march) Munich, Bavaria's capital, retaken — handed back to Bavaria.
   [Alarm] Europe's alarm rises +3 — Won a battle +3.
   ★ Enemy army destroyed! ★
   ⚑ Munich — handed back to Bavaria ⚑
   ⚔ View the field
   [3/4 actions remaining]
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
   Massena was nearly in position, but fate intervened at the crucial moment.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 41,090 committed (Lannes, Murat) = 65,090.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 141 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Attack: Ney (Personality (aggressive) +15%)
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 171 | Mack 2,500
   Strength: Ney 24,000 → 23,829 → 22,988 after the advance | Mack 2,500 → 0
   Berthier: "Reinforcements from Lannes and Murat bolstered Ney's position — though Bernadotte and Massena never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -534g | Other: +1295g | Upkeep: -3004g | Net: +38g
   Treasury: 823g
   Actions refreshed: 4/4
   Supply shortage at Franconia: Archduke Charles loses 779 troops
   Supply shortage at Munich: Ney loses 1,121 troops
   Supply shortage at Munich: Lannes loses 873 troops
   Supply shortage at Munich: Murat loses 1,070 troops
   Supply shortage at Munich: Deroy loses 1,053 troops
   Garrison at Munich reinforced: 0 -> 2,000
   Switzerland loyalty 97 (-3): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Murat has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Davout(1830,397)  ?(1951,579)  Archduke John(2032,540)  Soult(1741,436)  Napoleon(1764,462)  Ney(1888,535)  Lannes(1888,561)  Murat(1938,528)  Deroy(1948,425)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,615)  ?(2068,435)  ?(1923,347)  ?(1857,446)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1788,423)  12k(1693,420)  10k(1910,645)
```

```
#0064  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0064_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   NAPOLEON REPORTS
   "Berthier: 'Cannon fire at Munich, Sire. Investigate?'"
   controls: [March to the Guns]  [Continue as Ordered]  [Hold Position]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 86 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Envoy from Prussia @(3487,62)]  [icon: Envoy from Ottoman Empire @(3529,62)]  [icon: Envoy from Portugal @(3571,62)]  [icon: Marshal Davout seeks an audience @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +2 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2334 of 2334 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   823 (+572 next turn)
   Inf:
   82,262
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Supply shortage at Munich: Deroy loses 1,053 troops
   Garrison at Munich reinforced: 0 -> 2,000
   Switzerland loyalty 97 (-3): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Murat has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   --- Strategic Order Updates ---
   Napoleon: Berthier: 'Cannon fire at Munich, Sire. Investigate?'
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — General Mack of Austria is destroyed at Munich — his corps annihilated, his name struck from their order of battle.
   • Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,983 men — lost in a single action.
   • Sire — Marshal Ney has destroyed Mack's corps at Munich. No enemy formation remains in that field.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 823g (+572 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 39% of French forces (an estimate — 1 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 36,287 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Munich — 21,867 — Awaiting orders.
   - Murat — Munich — 20,884 — Awaiting orders.
   - Lannes — Munich — 17,032 — Awaiting orders.
   - Bernadotte — Franconia — 12,017 — Awaiting orders. Trust:40
   ⚠ IN PERIL — an enemy force of ~45,487 shares the field (Franconia).
   ? Napoleon — Lorraine — 10,000 — HALTED at Lorraine — awaiting your word.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Munich — 20,551 [confirmed]
   Archduke Charles — Franconia — 45,487 [confirmed]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 3,064 men, at Munich.
   Switzerland loyalty 97 (-3): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Murat has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   Munich passes from Bavaria to Austria.
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
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
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+2)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 86/100 [Formed] — up 2 since yesterday (Natural threat decay -3, Won a battle +3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   Napoleon awaits your orders!
map: unchanged (55 labels)
```

```
#0065  click Continue as Ordered  ->  ok
  (clicked at (1829, 551))
view: <run>\frames\0065_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 36,287
   54,000 → 49,697
   Ney — could not reach the field
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 3
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2378 of 2378 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   823 (+572 next turn)
   Inf:
   82,262
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Davout(1830,397)  ?(1951,579)  Archduke John(2032,540)  Soult(1753,436)  Ney(1888,535)  Lannes(1888,561)  Murat(1938,528)  Deroy(1948,425)  Napoleon(1683,440)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,615)  ?(2068,435)  ?(1923,347)  ?(1857,446)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1684,411)  10k(1910,645)
```

```
#0066  key R  ->  ok
  (pressed R)
view: <run>\frames\0066_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   4,514
   3,400
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 36,287
   54,000 → 49,697
   Ney — could not reach the field
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 3
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2378 of 2378 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0067  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0067_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 135 px] ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Shuts the Cabinet
   Turn 3
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces — but not a province she has declared guarded (Armed Neutrality): a column there still offends her (−25); up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   THE COURTS WRITE (2)
   Ottoman Empire and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Ottoman Empire
   Proposal
   Turn 3
   Incoming proposal: Open Borders Agreement
   Reis Efendi, serene and unhurried: "The Sublime Porte has learned across many centuries that it is the wiser house which comes to terms with the rising tide rather than argue with it, and it finds in France's greatness every reason for accommodation and none for dispute. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces — but not a province she has declared guarded (Armed Neutrality): a column there still offends her (−25); up to +100 gold a turn in trade
   or click the letter to reply in full
   WAITING
   Portugal
   Proposal
   Turn 3
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "Lisbon's fortune has always sailed with whoever commands the roads of Europe, and Portugal would sooner carry France's trade than test France's patience. Open the borders."
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2378 of 2378 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0068  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0068_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2378 of 2378 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   823 (+572 next turn)
   Inf:
   82,262
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0069  look  ->  ok
  (a fresh frame)
view: <run>\frames\0069_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2378 of 2378 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0070  key R  ->  ok
  (pressed R)
view: <run>\frames\0070_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: 'r' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2378 of 2378 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   823 (+572 next turn)
   Inf:
   82,262
   Cav:
   16,750
   Art:
   10,600
   r
   controls: [+]  [−]  [—]  [Execute]  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0071  key Backspace  ->  ok
  (pressed Backspace)
view: <run>\frames\0071_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2378 of 2378 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   823 (+572 next turn)
   Inf:
   82,262
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0072  click Dispatch (R)  ->  ok
  (clicked at (425, 18))
view: <run>\frames\0072_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1895 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 4 — Early November 1805 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Esc closes it; Alt+R (or Alt+B) while you type reopens it. /  / Sire — General Mack of Austria is destroyed at Munich — his corps annihilated, his name struck from their order …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (3)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2378 of 2378 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   823 (+572 next turn)
   Inf:
   82,262
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0073  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0073_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +2 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2378 of 2378 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0074  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0074_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2378 of 2378 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0075  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0075_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2378 of 2378 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0076  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0076_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2378 of 2378 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Napoleon awaits your orders!
   > Napoleon: continue order
   Napoleon reluctantly continues his march, ignoring cannon fire at Munich. Napoleon marches to Orleanais. 1 region to Flanders.
map: unchanged (54 labels)
```

```
#0077  click replay_aggressive  ->  ok
  (clicked at (1825, 510))
view: <run>\frames\0077_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1587 of 1587 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,478 next turn)
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
   Game loaded successfully.
   Loaded: replay_aggressive
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+1,478 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 34% of French forces (an estimate — 4 of 4 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Bohemia — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Bohemia — 24,000 — Awaiting orders.
   - Murat — Bohemia — 22,000 — Awaiting orders.
   - Massena — Bohemia — 22,000 — Awaiting orders. Morale:36%
   ⚠ Morale failing (36) — the men waver. Drill is closed: Archduke Charles is at Carniola, one region away.
   > Lannes — Bohemia — 18,000 — Supporting Napoleon.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Bohemia — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — small force [partial]
   Archduke Charles — Carniola — small force [partial]
   Archduke John — Tyrol — small force [partial]
   Kutuzov — Hungary — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Vienna garrison — Vienna — garrison — substantial force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Archduke Charles
   • Davout, march to Lorraine
   • recruit infantry in Rhineland — 663g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Archduke Charles' first — it names who marches with Ney, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Ney +5(2024,456)  Bernadotte(1930,451)  Deroy(1955,425)  ?(2016,632)  Archduke Charles(2016,605)  ?(1959,325)  Brunswick(1958,287)  ?(2131,579)  Kutuzov(2130,540)  ?(1859,469)  Mack(1853,430)  Davout(1830,397)  ?(1948,579)  Archduke John(1948,540)  ?(2079,435)  ?(2071,545)  ?(1959,376)  ?(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1716,420)  ?(1910,645)
```

```
#0078  type Massena, support Napoleon  ->  ok
  (typed and Enter)
view: <run>\frames\0078_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena moves to support Napoleon (at Bohemia). Massena holds your written order: when Napoleon leads a battle within reach, he will march to the guns. He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Massena, follow Napoleon' keeps him at Napoleon's side. Name a duration to hold him to it. He will drop this order for any battle within two provinces in a war of ours. Massena: "He shall have my sabers the moment he needs them — and I shall have a share of the credit."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1763 of 1763 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+1,478 next turn)
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
   ► Massena, support Napoleon
   Massena moves to support Napoleon (at Bohemia). Massena holds your written order: when Napoleon leads a battle within reach, he will march to the guns. He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Massena, follow Napoleon' keeps him at Napoleon's side. Name a duration to hold him to it. He will drop this order for any battle within two provinces in a war of ours. Massena: "He shall have my sabers the moment he needs them — and I shall have a share of the credit."
   [3/4 actions remaining]
map: unchanged (54 labels)
```

```
#0079  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0079_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1345 of 1345 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+1,478 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Lannes (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle within two provinces in a war of ours. Massena (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle within two provinces in a war of ours. Massena's corps stands below 40% morale beside Kutuzov (~27,500, Hungary) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0080  click_at 2024 456  ->  ok
  (clicked at (2024, 456) on MapArea '100' (Control, layer 0))
view: <run>\frames\0080_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1345 of 1345 px]: unchanged
── OrderStrip (layer 0) ──
   Ney selected — click a province: march · an enemy: attack · a marshal: support · Esc cancels / ■ this turn   ■ 1 turn   ■ 2–3 turns   ■ 4+ turns   59 provinces on his roads · a march costs 2 actions
── MapControls (layer 0): unchanged
── command window, last lines ──
   Massena moves to support Napoleon (at Bohemia). Massena holds your written order: when Napoleon leads a battle within reach, he will march to the guns. He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Massena, follow Nap
   [3/4 actions remaining]
   ⚠ Lannes (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle within two provinces in a war of ours. Massena (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle with
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0081  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0081_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1345 of 1345 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Massena moves to support Napoleon (at Bohemia). Massena holds your written order: when Napoleon leads a battle within reach, he will march to the guns. He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Massena, follow Nap
   [3/4 actions remaining]
   ⚠ Lannes (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle within two provinces in a war of ours. Massena (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle with
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0082  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0082_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1345 of 1345 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Massena moves to support Napoleon (at Bohemia). Massena holds your written order: when Napoleon leads a battle within reach, he will march to the guns. He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Massena, follow Nap
   [3/4 actions remaining]
   ⚠ Lannes (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle within two provinces in a war of ours. Massena (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle with
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0083  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0083_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1345 of 1345 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Massena moves to support Napoleon (at Bohemia). Massena holds your written order: when Napoleon leads a battle within reach, he will march to the guns. He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Massena, follow Nap
   [3/4 actions remaining]
   ⚠ Lannes (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle within two provinces in a war of ours. Massena (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle with
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0084  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0084_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1345 of 1345 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Massena moves to support Napoleon (at Bohemia). Massena holds your written order: when Napoleon leads a battle within reach, he will march to the guns. He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Massena, follow Nap
   [3/4 actions remaining]
   ⚠ Lannes (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle within two provinces in a war of ours. Massena (aggressive) holds a standing order at Bohemia with Kutuzov's ~27,500 one province off — he will drop it for any battle with
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (54 labels)
```

```
#0085  click replay_support  ->  ok
  (clicked at (1825, 462))
view: <run>\frames\0085_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/6
   Threat 70 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:8
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
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
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_support
   ════════════════════════════════════
   MORNING DISPATCH — Turn 9
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+828 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 44% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Paris — 30,000 — Awaiting orders.
   > Davout — Paris — 26,000 — Supporting Napoleon.
   > Ney — Paris — 24,000 — Supporting Napoleon.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   > Lannes — Paris — 18,000 — Supporting Napoleon.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   > Napoleon — Paris — 10,000 — Moving to Lyonnais — 2 turns out.
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
   • Murat, attack Mack
   • Soult, march to Artois
   • recruit infantry in Paris — 654g for 10,000 men under Soult
   • build supply depot in Paris — 300g
   Ask 'what if Murat attacks Mack' first — it names who marches with Murat, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1859,469)  Mack(1853,430)  ?(1965,579)  Archduke John(1948,540)  Murat(1813,497)  Ney +4(1595,421)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1716,420)  10k(1910,645)
```

```
#0086  type Soult, support Napoleon  ->  ok
  (typed and Enter)
view: <run>\frames\0086_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult moves to support Napoleon (at Paris). Soult holds your written order: when Napoleon leads a battle within reach, he will march to the guns. He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Soult, follow Napoleon' keeps him at Napoleon's side. Name a duration to hold him to it. "Soult, support Napoleon." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1675 of 1675 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
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
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, support Napoleon
   Soult moves to support Napoleon (at Paris). Soult holds your written order: when Napoleon leads a battle within reach, he will march to the guns. He goes to Napoleon now and stays only while Napoleon is in danger — the order lapses of itself once Napoleon is out of danger; 'Soult, follow Napoleon' keeps him at Napoleon's side. Name a duration to hold him to it. "Soult, support Napoleon." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map: unchanged (50 labels)
```

```
#0087  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0087_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 136 px] ──
   ENEMY PHASE - Turn 9
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 3,804 casualties, 50,196 remaining /     Massena: 7,094 casualties, 34,906 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10 …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (5)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2185 of 2185 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,428 (+982 next turn)
   Inf:
   82,287
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -354g | Other: +1295g | Upkeep: -2594g | Net: +628g
   Treasury: 1,428g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,510 troops
   Supply shortage at Tyrol: Archduke John loses 601 troops
   Soult's quarry has shifted to Limousin, Sire — he follows the letter of your order, not his instincts.
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-4): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Murat at Franche-Comte. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1859,469)  Mack(1853,430)  Ney(1587,497)  Napoleon(1611,471)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Murat(1813,497)  Davout(1583,442)  Soult(1596,416)  Lannes(1607,390)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  12k(1545,468)  ?(1769,580)  10k(1755,420)  12k(1710,420)  10k(1910,648)
```

```
#0088  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0088_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 34,906
   54,000 → 50,196
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 9
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (5)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: A Moment of History: The Bavarian Match @(3442,64)]  [icon: Envoy from Prussia @(3484,64)]  [icon: Envoy from Ottoman Empire @(3526,64)]  [icon: Envoy from Portugal @(3568,64)]  [+4]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   -4 →
   T:9
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2249 of 2249 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,428 (+982 next turn)
   Inf:
   82,287
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -354g | Other: +1295g | Upkeep: -2594g | Net: +628g
   Treasury: 1,428g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,510 troops
   Supply shortage at Tyrol: Archduke John loses 601 troops
   Soult's quarry has shifted to Limousin, Sire — he follows the letter of your order, not his instincts.
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-4): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Murat at Franche-Comte. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   --- Strategic Order Updates ---
   Davout: Napoleon is secure Davout: "Done, and done properly — no stragglers, no surprises."
   Lannes: Napoleon is secure Lannes: "Done — and I trust the next order has more fire in it."
   Napoleon: Napoleon marches to Limousin. 1 region to Lyonnais.
   Ney: Ney moves to support Napoleon. Napoleon is secure Ney: "Done — and I trust the next order has more fire in it."
   Soult: Soult is moving to support Napoleon.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,428g (+982 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 70% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 34,906 — Awaiting orders.
   > Soult — Paris — 30,000 — Supporting Napoleon. (to the letter)
   - Davout — Paris — 26,000 — Awaiting orders.
   - Ney — Limousin — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Paris — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   > Napoleon — Limousin — 10,000 — Moving to Lyonnais — arrives next turn.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Soult's quarry has shifted to Limousin, Sire — he follows the letter of your order, not his instincts.
   2 satellites drifted — Holland and Switzerland.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   Swabia passes from Bavaria to Austria.
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   An envoy from Switzerland has arrived with a petition.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Murat at Franche-Comte. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 5 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - The Cabinet — A Moment of History
   - Ottoman Empire — Open Borders Agreement
   - ...and 2 more
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-4)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0089  click End Turn  ->  ERROR: no visible control's text holds "End Turn"
view: <run>\frames\0089_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS LOST
   FRANCE LOSSES
   AUSTRIA LOSSES
   7,094
   3,804
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 34,906
   54,000 → 50,196
   Berthier: “The margin was slim. Training and preparation would serve Massena well.” / Archduke Charles: "Your marshals are bold. Boldness is not a plan."
   THE GREAT BATTLE OF MILAN
   MILAN · TURN 9
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2249 of 2249 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0090  click Continue  ->  ERROR: no visible control's text holds "Continue"
view: <run>\frames\0090_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2249 of 2249 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0091  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0091_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2249 of 2249 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,428 (+982 next turn)
   Inf:
   82,287
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0092  look  ->  ok
  (a fresh frame)
view: <run>\frames\0092_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2249 of 2249 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0093  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0093_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1696 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,428 (+982 next turn)
   Inf:
   82,287
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]  [Open Envoys (5)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,428g (+982 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 70% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 34,906 — Awaiting orders.
   > Soult — Paris — 30,000 — Supporting Napoleon. (to the letter)
   - Davout — Paris — 26,000 — Awaiting orders.
   - Ney — Limousin — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Paris — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   > Napoleon — Limousin — 10,000 — Moving to Lyonnais — arrives next turn.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Soult's quarry has shifted to Limousin, Sire — he follows the letter of your order, not his instincts.
   2 satellites drifted — Holland and Switzerland.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   Swabia passes from Bavaria to Austria.
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   An envoy from Switzerland has arrived with a petition.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Murat at Franche-Comte. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 5 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - The Cabinet — A Moment of History
   - Ottoman Empire — Open Borders Agreement
   - ...and 2 more
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-4)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   ⚠ You have 4 unanswered envoys that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: Switzerland — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
map: unchanged (58 labels)
```

```
#0094  click Continue  ->  ERROR: no visible control's text holds "Continue"
view: <run>\frames\0094_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   ⚠ You have 4 unanswered envoys that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: Switzerland — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
map: unchanged (58 labels)
```

```
#0095  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0095_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   ⚠ You have 4 unanswered envoys that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: Switzerland — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
map: unchanged (58 labels)
```

```
#0096  click End Turn  ->  ERROR: no visible control's text holds "End Turn"
view: <run>\frames\0096_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   ⚠ You have 4 unanswered envoys that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: Switzerland — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
map: unchanged (58 labels)
```

```
#0097  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0097_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   ⚠ You have 4 unanswered envoys that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: Switzerland — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
map: unchanged (58 labels)
```

```
#0098  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0098_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   ⚠ You have 4 unanswered envoys that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: Switzerland — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
map: unchanged (58 labels)
```

```
#0099  click replay_petition  ->  ok
  (clicked at (1825, 414))
view: <run>\frames\0099_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Murat seeks an audience @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+948 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_petition
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+948 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 35% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 18,920 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Tyrol — small force [partial]
   Archduke Charles — Munich — substantial force [partial]
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
   • Lannes, attack Archduke Charles
   • Ney, march to Swabia
   • recruit infantry in Rhineland — 729g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Lannes attacks Archduke Charles' first — it names who marches with Lannes, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
   The Emperor's Designs — I The Protector of the Rhine, II The Crowns of Italy, III The Continental System: one proclamation decides what the Empire is for, and it cannot be undone. In the Cabinet: F1 → The Emperor's Designs.
   Berthier: "Murat nurses a grievance against Ney, Sire. The rivalry wants settling before it is tested."
   ════════════════════════════════════
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
   • "what if Ney attacks Mack" — free: it names who marches with him before you commit
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Mack(1940,540)  Archduke John(2015,514)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1838,471)  ?(1901,540)  Archduke Charles(1791,521)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1865,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,645)
```

```
#0100  key G  ->  ok
  (pressed G)
view: <run>\frames\0100_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: 'g' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+948 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   g
   controls: [+]  [−]  [—]  [Execute]  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0101  click_at 3613 62  ->  ok
  (clicked at (3613, 62) on @Button@1945  (Button, layer 75))
view: <run>\frames\0101_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: 'g' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 4 — Early November 1805
   Imperial Box
   Marshal Murat seeks an audience
   T4
   Murat asks to be heard — at your leisure, Sire; nothing waits on it. His card is on the Generals screen.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Murat seeks an audience @(3613,62)]  [Hear him]  [Keep]  [Acknowledge]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0102  key Backspace  ->  ok
  (pressed Backspace)
view: <run>\frames\0102_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+948 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0103  click_at 3613 62  ->  ok
  (clicked at (3613, 62) on @Button@1945  (Button, layer 75))
view: <run>\frames\0103_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Murat seeks an audience @(3613,62)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0104  click Generals (G)  ->  ok
  (clicked at (228, 18))
view: <run>\frames\0104_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 5333 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Esc closes it (Alt+G while you type). /  / SEEKS AN AUDIENCE — Murat /   / [5] Murat    [Cavalry]  France / The Cavalry Reserve - screening the Black Forest feint while the army wheels north of the Danube. / Aggressive: +15% attack, +5% more in aggressive stance. Fortify capped at 10%. Grows restless if i …
   controls: [Pin]  [icon @(2213,236)]  <Hear him — he seeks an audience>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <▸ the doctrine>  <Fortify (2 AP)>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify (2 AP)>  <Drill>  <Hold (2 AP)>  <Fortify (2 AP)>  <Drill>  <Hold (2 AP)>  <Fortify (2 AP)>  <Drill>  <Hold (1 AP)>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+948 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0105  click Hear him  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0105_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) [scrolled 0 of 24 px] ──
   MURAT — Marshal Murat seeks an audience
   "Sire — I have earned better than to watch Ney take the field while I hold a road." /  / Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a command worthy of his talents. /  / What each answer does / • Let it stand (Free) — Free, and it fixes nothing. For 3 more turns he brings NONE of his 18,920 men to any battle Ney leads, and the quarrel may harden further. / …
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Give him a command   [2 AP]]  [Later (he will return)]
── TopBar (layer 75) [under a modal]: unchanged
── MarshalManagement (layer 50) [under a modal] [scrolled 0 of 5333 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+948 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0106  click Give him a command  ->  ok
  (clicked at (2029, 702))
view: <run>\frames\0106_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   MURAT — Marshal Murat seeks an audience
   "Sire — I have earned better than to watch Ney take the field while I hold a road." /  / Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a command worthy of his talents. /  / What each answer does / • Let it stand (Free) — Free, and it fixes nothing. For 3 more turns he brings NONE of his 18,920 men to any battle Ney leads, and the quarrel may harden further. / …
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Give him a command   [2 AP]]  [Later (he will return)]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── MarshalManagement (layer 50) [under a modal] [scrolled 0 of 5333 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1587 of 1587 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+948 next turn)
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
   Mack has left Swabia; Archduke Charles at Munich (substantial force against his 18,920) is what stands in his reach now. Berthier reads the odds favorable. Send him?
map: unchanged (55 labels)
```

```
#0107  click Give him a command  ->  ok
  (clicked at (2029, 702))
view: <run>\frames\0107_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── MarshalManagement (layer 50) [scrolled 0 of 5309 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Esc closes it (Alt+G while you type). /  /   OUR DOCTRINE — The Corps System  ▸ the doctrine /  /   THE EMPEROR /   / [8] Napoleon  [Infantry]  France / In the field at Lorraine — The Presence goes where he stands. /   ★ The Presence  +10% here at Lorraine  Every French corps fighting in the Emperor's pro …
   controls: [Pin]  [icon @(2213,236)]  <▸ the doctrine>  <Fortify (2 AP)>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify (2 AP)>  <Drill>  <Hold (2 AP)>  <Fortify (2 AP)>  <Drill>  <Hold (2 AP)>  <Fortify (2 AP)>  <Drill>  <Hold (1 AP)>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>  <Fortify (2 AP)>  <Hold (2 AP)>  <Fall back>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   511 (+1,106 next turn)
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
   "Archduke Charles, then." Murat takes the command and goes. Murat pursues Archduke Charles (at Munich). Archduke Charles spotted at Munich! Engaging!
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Terrain] Archduke Charles benefits from Mountains terrain (+25% defense)
   [Combat] Murat's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Murat's attack! (+2%)
   Murat engages in solid combat. Brutal stalemate between Murat and Archduke Charles. Heavy casualties on both sides: Murat's army 5,799, Archduke Charles 6,820.
   [Materiel] Guns, horses and stores lost with the fallen: France -289g, Austria -341g. Our treasury stands at 511 gold.
   Lannes withdraws to Franche-Comte after the battle.
   Massena withdraws to Milan after the battle. He will drop this order for any battle within two provinces in a war of ours. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [2/4 actions remaining]
   --- Berthier's Report ---
   Murat: "A day of circling. Tomorrow the charge."
   Murat fought with particular ferocity — though one wonders if it was for France or for himself.
   Berthier: the corps marched apart and arrived together.
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Archduke Charles (Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,215 | Archduke Charles 6,820
   Strength: Murat 18,920 → 16,705 | Archduke Charles 31,690 → 24,870
   Berthier: "Lannes and Massena arrived in time to steady Murat's position. The field was held, nothing further."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  ?(1965,588)  Mack(1940,561)  ?(1980,562)  Archduke John(2015,509)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1838,471)  Archduke Charles(1910,535)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  10k(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,648)
```

```
#0108  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0108_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   511 (+1,106 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke Charles (Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,215 | Archduke Charles 6,820
   Strength: Murat 18,920 → 16,705 | Archduke Charles 31,690 → 24,870
   Berthier: "Lannes and Massena arrived in time to steady Murat's position. The field was held, nothing further."
map: unchanged (55 labels)
```

```
#0109  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0109_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,215 | Archduke Charles 6,820
   Strength: Murat 18,920 → 16,705 | Archduke Charles 31,690 → 24,870
   Berthier: "Lannes and Massena arrived in time to steady Murat's position. The field was held, nothing further."
map: unchanged (55 labels)
```

```
#0110  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0110_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,215 | Archduke Charles 6,820
   Strength: Murat 18,920 → 16,705 | Archduke Charles 31,690 → 24,870
   Berthier: "Lannes and Massena arrived in time to steady Murat's position. The field was held, nothing further."
map: unchanged (55 labels)
```

```
#0111  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0111_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,215 | Archduke Charles 6,820
   Strength: Murat 18,920 → 16,705 | Archduke Charles 31,690 → 24,870
   Berthier: "Lannes and Massena arrived in time to steady Murat's position. The field was held, nothing further."
map: unchanged (55 labels)
```

```
#0112  click replay_envoys  ->  ERROR: no visible control's text holds "replay_envoys"
view: <run>\frames\0112_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,215 | Archduke Charles 6,820
   Strength: Murat 18,920 → 16,705 | Archduke Charles 31,690 → 24,870
   Berthier: "Lannes and Massena arrived in time to steady Murat's position. The field was held, nothing further."
map: unchanged (55 labels)
```

```
#0113  scroll 1828 500 up 30  ->  ok
  (scrolled up 30 at (1828, 500))
view: <run>\frames\0113_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 528 px] ──
   LOAD GAME
   controls: [Autosave - Turn 10 (Turn 10)]  [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,215 | Archduke Charles 6,820
   Strength: Murat 18,920 → 16,705 | Archduke Charles 31,690 → 24,870
   Berthier: "Lannes and Massena arrived in time to steady Murat's position. The field was held, nothing further."
map: unchanged (55 labels)
```

```
#0114  scroll 1828 500 down 4  ->  ok
  (scrolled down 4 at (1828, 500))
view: <run>\frames\0114_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 116 of 528 px] ──
   LOAD GAME
   controls: [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,215 | Archduke Charles 6,820
   Strength: Murat 18,920 → 16,705 | Archduke Charles 31,690 → 24,870
   Berthier: "Lannes and Massena arrived in time to steady Murat's position. The field was held, nothing further."
map: unchanged (55 labels)
```

```
#0115  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0115_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 261 of 528 px] ──
   LOAD GAME
   controls: [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,215 | Archduke Charles 6,820
   Strength: Murat 18,920 → 16,705 | Archduke Charles 31,690 → 24,870
   Berthier: "Lannes and Massena arrived in time to steady Murat's position. The field was held, nothing further."
map: unchanged (55 labels)
```

```
#0116  click replay_envoys  ->  ok
  (clicked at (1825, 619))
view: <run>\frames\0116_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 113 px] ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Austria
   Proposal
   Shuts the Cabinet
   Turn 5
   Incoming proposal: Armistice
   Terms: Proposal: Armistice · Austria pays you 105 gold a turn for as long as the treaty stands
   A great court's letter is answered in full — open to accept, haggle or refuse.
   THE COURTS WRITE (2)
   Ottoman Empire and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Ottoman Empire
   Proposal
   Turn 5
   Incoming proposal: Open Borders Agreement
   Reis Efendi, serene and unhurried: "The Porte watches the star of France climb ever higher and, being an old admirer of whatever endures, would sooner arrange itself gracefully beneath so great a light than stand across its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces — but not a province she has declared guarded (Armed Neutrality): a column there still offends her (−25); up to +100 gold a turn in trade
   or click the letter to reply in full
   WAITING
   Portugal
   Proposal
   Turn 5
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "A kingdom as modest as ours does not measure itself against the Empire's shadow, and Lisbon would far rather reach an understanding than be caught standing in its path. Open the borders."
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Austria @(3529,62)]  [icon: Envoy from Ottoman Empire @(3571,62)]  [icon: Envoy from Portugal @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:4
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Austria's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_envoys
   ════════════════════════════════════
   MORNING DISPATCH — Turn 5
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
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Austria — Armistice
   - Ottoman Empire — Open Borders Agreement
   - Portugal — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+20)
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
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1838,471)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,645)
```

```
#0117  look  ->  ok
  (a fresh frame)
view: <run>\frames\0117_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 113 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0118  click Open ▸  ->  ERROR: 3 controls match "Open ▸" — pick one with click#N
  candidates: #1 [Open ▸] on MailboxPanel @(2183,294) | #2 [Open ▸] on MailboxPanel @(2183,499) | #3 [Open ▸] on MailboxPanel @(2183,718)
view: <run>\frames\0118_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 113 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0119  click#1 Open ▸  ->  ok
  (clicked at (2183, 294))
view: <run>\frames\0119_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 264 px] ──
   DIPLOMATIC ENVOY / Metternich (Schemer) of Austria /  / Proposes: Armistice / Terms: / France demands: /   - Austria pays 105 gold per turn to France for as long as the treaty stands / Mutual: /   - Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France …
   Set aside — the Cabinet stays shut until it is answered or the turn ends.
   controls: [Accept]  [Reject]  [Not Now (Cabinet stays shut)]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0120  click Not Now  ->  ok
  (clicked at (1978, 851))
view: <run>\frames\0120_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
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
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0121  look  ->  ok
  (a fresh frame)
view: <run>\frames\0121_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0122  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0122_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   An unanswered envoy awaits your reply (Austria's letter) — the Cabinet stays shut until it is answered or the turn ends. Reopen Envoys to answer it.
   controls: [icon: Close (Esc) @(2075,236)]  [Open Envoys (3)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0123  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0123_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0124  click Envoys (3)  ->  ok
  (clicked at (3379, 18))
view: <run>\frames\0124_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 113 px] ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Austria
   Proposal
   Shuts the Cabinet
   Turn 5
   Incoming proposal: Armistice
   Terms: Proposal: Armistice · Austria pays you 105 gold a turn for as long as the treaty stands
   A great court's letter is answered in full — open to accept, haggle or refuse.
   THE COURTS WRITE (2)
   Ottoman Empire and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Ottoman Empire
   Proposal
   Turn 5
   Incoming proposal: Open Borders Agreement
   Reis Efendi, serene and unhurried: "The Porte watches the star of France climb ever higher and, being an old admirer of whatever endures, would sooner arrange itself gracefully beneath so great a light than stand across its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces — but not a province she has declared guarded (Armed Neutrality): a column there still offends her (−25); up to +100 gold a turn in trade
   or click the letter to reply in full
   WAITING
   Portugal
   Proposal
   Turn 5
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "A kingdom as modest as ours does not measure itself against the Empire's shadow, and Lisbon would far rather reach an understanding than be caught standing in its path. Open the borders."
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0125  click#1 Open ▸  ->  ok
  (clicked at (2183, 294))
view: <run>\frames\0125_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 264 px] ──
   DIPLOMATIC ENVOY / Metternich (Schemer) of Austria /  / Proposes: Armistice / Terms: / France demands: /   - Austria pays 105 gold per turn to France for as long as the treaty stands / Mutual: /   - Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France …
   Set aside — the Cabinet stays shut until it is answered or the turn ends.
   controls: [Accept]  [Reject]  [Not Now (Cabinet stays shut)]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Austria's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0126  click Reject  ->  ok
  (clicked at (1794, 851))
view: <run>\frames\0126_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Rejected @(3613,62)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1763 of 1763 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
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
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Austria's proposal: declined
   You have rejected Austria's proposal. Talleyrand will convey your decision.
map: unchanged (53 labels)
```

```
#0127  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0127_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Your courts (2)
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Ottoman Empire  —  Peace · letter awaiting your answer  |  -20 (Wary)]  [Portugal  —  Peace · letter awaiting your answer  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1763 of 1763 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   Responding to Austria's proposal: declined
   You have rejected Austria's proposal. Talleyrand will convey your decision.
map: unchanged (53 labels)
```

```
#0128  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0128_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1763 of 1763 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   Responding to Austria's proposal: declined
   You have rejected Austria's proposal. Talleyrand will convey your decision.
map: unchanged (53 labels)
```

```
#0129  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0129_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1763 of 1763 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   Responding to Austria's proposal: declined
   You have rejected Austria's proposal. Talleyrand will convey your decision.
map: unchanged (53 labels)
```

```
#0130  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0130_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 261 of 528 px] ──
   LOAD GAME
   controls: [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1763 of 1763 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   Responding to Austria's proposal: declined
   You have rejected Austria's proposal. Talleyrand will convey your decision.
map: unchanged (53 labels)
```

```
#0131  scroll 1828 500 down 9  ->  ok
  (scrolled down 9 at (1828, 500))
view: <run>\frames\0131_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 522 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1763 of 1763 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   Responding to Austria's proposal: declined
   You have rejected Austria's proposal. Talleyrand will convey your decision.
map: unchanged (53 labels)
```

```
#0132  scroll 1828 500 up 5  ->  ok
  (scrolled up 5 at (1828, 500))
view: <run>\frames\0132_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 377 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1763 of 1763 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Setting aside Austria's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   Responding to Austria's proposal: declined
   You have rejected Austria's proposal. Talleyrand will convey your decision.
map: unchanged (53 labels)
```

```
#0133  click replay_truce_offer  ->  ok
  (clicked at (1825, 469))
view: <run>\frames\0133_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_truce_offer
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+228 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 44% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 26,000 — Awaiting orders.
   - Ney — Swabia — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Bernadotte, attack Mack
   • Ney, march to Franconia
   • build supply depot in Lorraine — 300g
   • build fortification in Lorraine — 400g
   Ask 'what if Bernadotte attacks Mack' first — it names who marches with Bernadotte, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1845,438)  ?(1965,579)  Mack(1940,540)  Archduke John(2015,514)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1825,521)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1893,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,645)
```

```
#0134  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0134_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0135  click Austria  —  ->  ERROR: no visible control's text holds "Austria  —"
view: <run>\frames\0135_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0136  scroll 1828 550 down 3  ->  ok
  (scrolled down 3 at (1828, 550))
view: <run>\frames\0136_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 150 of 733 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0137  click Austria  ->  ok
  (clicked at (1825, 557))
view: <run>\frames\0137_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 435 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — a level ledger still signs: Propose Armistice at 51 of 50. It costs 1 DP. A truce keeps the ledger (+0 stands, the war 2 turns old) an …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Propose Armistice (1 DP)  —  Favorable]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Open Settlement with Austria alone  —  opens with 575 gold to Austria staged — the sum that carries her]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Doubtful]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0138  click Propose Armistice  ->  ok
  (clicked at (1825, 427))
view: <run>\frames\0138_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 374 of 662 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 2 turns old and stays so; exhaustion holds. No territory or gold changes hands until it ends …
   ▼ more below
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms](disabled: A truce settles nothing: no province or gold changes hands until it ends. Demands are pres)  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1566 of 1566 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
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
   ► propose armistice with Austria
map: unchanged (53 labels)
```

```
#0139  scroll 1828 550 down 4  ->  ok
  (scrolled down 4 at (1828, 550))
view: <run>\frames\0139_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 550 of 662 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 2 turns old and stays so; exhaustion holds. No territory or gold changes hands until it ends …
   ▼ more below
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms](disabled: A truce settles nothing: no province or gold changes hands until it ends. Demands are pres)  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1566 of 1566 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► propose armistice with Austria
map: unchanged (53 labels)
```

```
#0140  click Send as suggested  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0140_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/5
   Threat 70 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Dispatched @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (53 labels)
```

```
#0141  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0141_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 400 px] ──
   ENEMY PHASE - Turn 3
   AUSTRIA / ──────────────────────────── / - Mack attacks Massena /     The Great Battle of Milan /     Mack: 6,998 casualties, 45,002 remaining /     Massena: 4,032 casualties, 37,968 remaining /     Result: Defender tactical victory (Massena victorious) /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Mack: "A temporary deran …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
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
   719 (+428 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -509g | Other: +1251g | Upkeep: -3104g | Net: -81g
   Treasury: 719g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Mack loses 2,250 troops
   Supply shortage at Tyrol: Archduke Charles loses 2,507 troops
   Supply shortage at Tyrol: Archduke John loses 1,000 troops
   Switzerland loyalty 97 (-3): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Lorraine. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was deep-seated hostility.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Berthier notes that Ney has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1845,438)  ?(1951,590)  Mack(1932,537)  ?(1965,564)  Archduke Charles(2028,511)  ?(1979,590)  Archduke John(2015,485)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1825,521)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1872,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1788,420)  12k(1693,420)  10k(1910,645)
```

```
#0142  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0142_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Mack ◆
   42,000 → 37,968
   52,000 → 45,002
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 3
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Envoy from Prussia @(3487,62)]  [icon: Envoy from Ottoman Empire @(3529,62)]  [icon: Envoy from Portugal @(3571,62)]  [icon: Armistice Rejected @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2050 of 2050 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   719 (+428 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -509g | Other: +1251g | Upkeep: -3104g | Net: -81g
   Treasury: 719g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Mack loses 2,250 troops
   Supply shortage at Tyrol: Archduke Charles loses 2,507 troops
   Supply shortage at Tyrol: Archduke John loses 1,000 troops
   Switzerland loyalty 97 (-3): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Lorraine. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was deep-seated hostility.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Berthier notes that Ney has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 719g (+428 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 71% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 31,794 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 26,000 — Awaiting orders.
   - Ney — Swabia — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Tyrol — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Switzerland loyalty 97 (-3): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier notes that Ney has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Austria.
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Lorraine. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria with a response.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0143  type Murat, march to Swabia  ->  ERROR: the command line is not taking orders now (it is disabled)
view: <run>\frames\0143_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   4,032
   6,998
   ⚔
   Massena ◆
   Mack ◆
   42,000 → 37,968
   52,000 → 45,002
   Berthier: “The engagement proceeded as one might expect, Sire.” / Mack: "A temporary derangement of the arithmetic. Vienna will understand."
   THE GREAT BATTLE OF MILAN
   MILAN · TURN 3
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2050 of 2050 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0144  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0144_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2050 of 2050 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   719 (+428 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0145  type Murat, march to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0145_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: ok Murat begins march to Swabia. Moves to Swabia.
Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders - each side's armies may cross the other's provinces — but not a province she has declared guarded (Armed Neutrality): a co …
   Set aside — the Cabinet stays shut until it is answered or the turn ends.
   controls: [Accept]  [Reject]  [Not Now (Cabinet stays shut)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   719 (+184 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Murat, march to Swabia
   Murat begins march to Swabia. Moves to Swabia.
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1845,438)  Murat(1872,375)  ?(1951,590)  Mack(1932,537)  ?(1965,564)  Archduke Charles(2028,511)  ?(1979,590)  Archduke John(2015,485)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1813,497)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1872,560)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1788,420)  12k(1693,420)  10k(1910,645)
```

```
#0146  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0146_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Murat begins march to Swabia. Moves to Swabia.
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
map: unchanged (58 labels)
```

```
#0147  look  ->  ok
  (a fresh frame)
view: <run>\frames\0147_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Murat begins march to Swabia. Moves to Swabia.
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
map: unchanged (58 labels)
```

```
#0148  click Not Now  ->  ok
  (clicked at (1978, 851))
view: <run>\frames\0148_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2250 of 2250 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   719 (+184 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (58 labels)
```

```
#0149  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0149_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2250 of 2250 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   719 (+184 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (58 labels)
```

```
#0150  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0150_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2250 of 2250 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (58 labels)
```

```
#0151  scroll 1828 500 down 9  ->  ok
  (scrolled down 9 at (1828, 500))
view: <run>\frames\0151_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2250 of 2250 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (58 labels)
```

```
#0152  scroll 1828 500 up 5  ->  ok
  (scrolled up 5 at (1828, 500))
view: <run>\frames\0152_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2250 of 2250 px]: unchanged
── MapControls (layer 0) ──
   controls: [icon: Zoom out  (−) @(1794,992)]  [icon: Fit Europe — the whole theatre  (Home re-centres) @(1828,992)]  [icon: Zoom in  (+) @(1862,992)]
── command window, last lines ──
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map names: Russia(2627,167)  Ottoman Empire(2396,798)  Prussia(2169,264)  Spain(1144,896)  Sweden(1910,-6)  Saxony(2125,381)  Austria(2138,594)  France(1539,531)  Bavaria(1929,499)  Kingdom of Italy(1762,679)  Denmark(1732,38)  Papal States(1878,787)  Britain(1370,270)  Hanover(1720,314)  Naples(1801,921)  Sardinia(1630,811)  Hesse(1908,379)  Holland(1733,362)  Switzerland(1754,561)
map pieces: 100(1292,373)  45(1264,618)  30(1316,798)  20(2005,82)  18(1973,29)  15(2332,672)  12(1536,248)  10(937,818)  10(1950,179)  5(1798,856)  Bernadotte(1955,441)  Deroy(1985,413)  ?(1990,282)  Brunswick(1991,243)  Ney(1852,457)  Davout(1864,429)  Murat(1845,402)  ?(1977,613)  Mack(1957,559)  ?(1999,584)  Archduke Charles(1977,532)  ?(2006,613)  Archduke John(2045,504)  Soult(1719,422)  Napoleon(1749,395)  Lannes(1809,498)  Dumonceau(1738,281)  Massena(1914,612)  Teulie(1944,585)  ?(2126,416)  ?(1990,346)  ?(1893,582)  ?(1908,344)  25k(1538,496)  12k(1483,442)  ?(1754,596)  10k(1770,424)  12k(1667,395)  10k(1929,679)
```

```
#0153  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0153_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2250 of 2250 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (58 labels)
```

```
#0154  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0154_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 377 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2250 of 2250 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (58 labels)
```

```
#0155  scroll 1828 500 down 9  ->  ok
  (scrolled down 9 at (1828, 500))
view: <run>\frames\0155_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2250 of 2250 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (58 labels)
```

```
#0156  scroll 1828 500 up 5  ->  ok
  (scrolled up 5 at (1828, 500))
view: <run>\frames\0156_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 383 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2250 of 2250 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Swabia feeds 60,000; the 71,692 men standing there would lose ~1,642 a turn to short supply.
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. He will drop this order for any battle within two provinces in a war of ours. Murat: "At the double, Sire — the men will smell powder soon enough."
   [2/4 actions remaining]
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (58 labels)
```

```
#0157  click replay_counter  ->  ok
  (clicked at (1825, 415))
view: <run>\frames\0157_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treaty with Austria @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munich
   0 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Munich]  [War for Munich — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1565 of 1565 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (−36 next turn)
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
   Game loaded successfully.
   Loaded: replay_counter
   ════════════════════════════════════
   MORNING DISPATCH — Turn 5
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (-36 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   > Davout — Swabia — 26,000 — Moving to Franche-Comte — arrives next turn.
   > Ney — Swabia — 24,000 — Moving to Franche-Comte — arrives next turn.
   > Murat — Swabia — 22,000 — Moving to Franche-Comte — arrives next turn.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   > Bernadotte — Franconia — 17,000 — Moving to Franche-Comte — 2 turns out. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Bavaria — Vassalage
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Soult, march to Rhineland
   • Lannes, fortify (2 AP)
   • build supply depot in Lorraine — 300g
   • build fortification in Lorraine — 400g
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
   The Emperor's Designs — I The Protector of the Rhine, II The Crowns of Italy, III The Continental System: one proclamation decides what the Empire is for, and it cannot be undone. In the Cabinet: F1 → The Emperor's Designs.
   Berthier: "Our finances strain, Sire. The treasury bleeds 36g this turn."
   ════════════════════════════════════
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
   • "what if Ney attacks Mack" — free: it names who marches with him before you commit
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2627,167)  Ottoman Empire(2396,798)  Prussia(2169,264)  Spain(1144,896)  Sweden(1910,-6)  Saxony(2125,381)  Austria(2071,509)  France(1539,531)  Bavaria(1970,477)  Kingdom of Italy(1762,679)  Denmark(1732,38)  Papal States(1878,787)  Britain(1370,270)  Hanover(1720,314)  Naples(1801,921)  Sardinia(1630,811)  Hesse(1908,379)  Holland(1733,362)  Switzerland(1754,561)
map pieces: 100(1292,371)  45(1264,616)  30(1316,796)  20(2005,80)  18(1973,27)  15(2332,670)  12(1536,246)  10(937,816)  10(1950,177)  5(1798,854)  Bernadotte(1955,441)  Deroy(1985,413)  ?(1990,282)  Brunswick(1991,243)  Ney(1852,457)  Davout(1864,429)  Murat(1845,402)  ?(1987,613)  Mack(1967,559)  Archduke John(1986,585)  Soult(1719,422)  Napoleon(1749,395)  Lannes(1809,498)  Massena(1929,612)  ?(2126,416)  ?(1990,346)  ?(1893,582)  ?(1908,344)  25k(1538,496)  12k(1483,442)  ?(1754,596)  12k(1667,395)  10k(1929,679)
```

```
#0158  click Envoys (1)  ->  ok
  (clicked at (3379, 18))
view: <run>\frames\0158_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   COUNTER-OFFER / Montgelas (Schemer) of Bavaria /  / In response to your Vassalage proposal, Bavaria offers modified terms: /  / Revised Terms: /   - Proposal: Vassalage /   - Added by Bavaria: you pay 300 gold more (442 at the signing) /  / Montgelas, coolly reckoning the gains: "Bavaria has marked where the weight of Europe now settles, and a prudent state places itself beside the rising power, n …
   Set aside — it waits in the mailbox until the turn ends; the Cabinet stays open.
   controls: [Accept Terms]  [Reject Terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (−36 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (52 labels)
```

```
#0159  click#1 Open ▸  ->  ERROR: no visible control's text holds "Open ▸"
view: <run>\frames\0159_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (52 labels)
```

```
#0160  click Accept counter-offer  ->  ERROR: no visible control's text holds "Accept counter-offer"
view: <run>\frames\0160_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (52 labels)
```

```
#0161  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0161_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (52 labels)
```

```
#0162  click Accept Terms  ->  ok
  (clicked at (1679, 851))
view: <run>\frames\0162_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 75 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treaty with Bavaria @(3529,62)]  [icon: Diplomatic Action Accepted @(3571,62)]  [icon: Treaty with Austria @(3613,62)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   358 (−481 next turn)
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
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 442 gold from the treasury.
map: unchanged (52 labels)
```

```
#0163  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0163_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   Treaties (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 36 titled provinces — 45 are needed (9 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1631 of 1631 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 442 gold from the treasury.
map: unchanged (52 labels)
```

```
#0164  click Prussia  ->  ERROR: no visible control's text holds "Prussia"
view: <run>\frames\0164_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1631 of 1631 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 442 gold from the treasury.
map: unchanged (52 labels)
```

```
#0165  scroll 1828 550 down 12  ->  ok
  (scrolled down 12 at (1828, 550))
view: <run>\frames\0165_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 622 of 742 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Prussia  —  Peace  |  +45 (Friendly)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Saxony  —  Peace  |  -10 (Wary)]  [Hanover  —  Peace  |  -50 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1631 of 1631 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 442 gold from the treasury.
map: unchanged (52 labels)
```

```
#0166  click Prussia  ->  ok
  (clicked at (1825, 394))
view: <run>\frames\0166_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 222 px, 0 of 552 px] ──
   THE CABINET — Prussia
   DP: 5
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: +45 (Friendly) /  / "Prussia is well-disposed toward us. The time is ripe for open borders, perhaps more." / Recommendation: Talleyrand recommends: Propose Open Borders / Talleyrand: "Prussia stands on the Emperor's roads, Sire — The Protector of the Rhine (A German Crown Brought to Terms). Proclaim one in the Cabinet (F1 → The Emperor' …
   The treasury cannot sustain the subsidy (needs 800g in hand).
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Propose Open Borders (1 DP)  —  Favorable]  [↳ Skip ahead: Non-Aggression (2 DP)]  [↳ Skip ahead: Defensive Alliance (4 DP)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3). If Prussia then declares on Hanover, her relations with every court, France's included, fall 15 (France–Prussia now +45, +50 once this compact is struck, +35 after her declaration).](disabled: The treasury cannot sustain the subsidy (needs 800g in hand).)  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. It buys the design's sleep, not her goodwill: +5 relations (+45 → +50); she already stands past the −10 line a league counts her below. Buying it wakes Armed Neutrality next (600g to buy off in turn).](disabled: Their price is 1128g — the treasury holds 358g.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   358 (−481 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 442 gold from the treasury.
map: unchanged (52 labels)
```

```
#0167  click Skip ahead: Non-Aggression  ->  ok
  (clicked at (1825, 482))
view: <run>\frames\0167_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 108 of 108 px] ──
   DIPLOMATIC PROPOSAL — Prussia /  / Terms Talleyrand proposes: /   • Non-Aggression Pact (agree not to attack) - up to +150 gold a turn in trade; breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court /   • No additional terms /  / Harshness: Low / Acceptance estimate: ~52% (ACCEPT) / Key obstacle: personal opposition from their diplomat / DP cost: 2 /  / Politica …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 75 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1676 of 1676 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   358 (−481 next turn)
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
   ► propose non aggression with Prussia
map: unchanged (52 labels)
```

```
#0168  click Send as suggested  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0168_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 3/5
   Threat 75 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treaty with Bavaria @(3487,62)]  [icon: Diplomatic Action Accepted @(3529,62)]  [icon: Non-Aggression Pact Dispatched @(3571,62)]  [icon: Treaty with Austria @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munich
   0 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Munich]  [War for Munich — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1742 of 1742 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   358 (−481 next turn)
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
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussian court with your Non-Aggression Pact proposal. Expect a response by next turn. (2 DP spent)
map: unchanged (52 labels)
```

```
#0169  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0169_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1808 of 1808 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   358 (−481 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ The treasury will stand at -123 gold when the turn ends (358 now, −481 next turn) — the Ledger's Economy tab shows what drains it.
   Press End Turn again, Enter, or type end turn again to end the turn in deficit.
map: unchanged (52 labels)
```

```
#0170  click Continue  ->  ERROR: no visible control's text holds "Continue"
view: <run>\frames\0170_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1808 of 1808 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussian court with your Non-Aggression Pact proposal. Expect a response by next turn. (2 DP spent)
   ⚠ The treasury will stand at -123 gold when the turn ends (358 now, −481 next turn) — the Ledger's Economy tab shows what drains it.
   Press End Turn again, Enter, or type end turn again to end the turn in deficit.
map: unchanged (52 labels)
```

```
#0171  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0171_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 5
   Britain, Russia, Austria and 1 other court stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 74 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   718 (+360 next turn)
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
   Mack — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Bavaria — Vassalage
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Soult, march to Rhineland
   • Lannes, fortify (2 AP)
   • build supply depot in Lorraine — 300g
   • build fortification in Lorraine — 400g
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
   The Emperor's Designs — I The Protector of the Rhine, II The Crowns of Italy, III The Continental System: one proclamation decides what the Empire is for, and it cannot be undone. In the Cabinet: F1 → The Emperor's Designs.
   Berthier: "Our finances strain, Sire. The treasury bleeds 36g this turn."
   ════════════════════════════════════
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
   • "what if Ney attacks Mack" — free: it names who marches with him before you commit
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 442 gold from the treasury.
   ► propose non aggression with Prussia
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussian court with your Non-Aggression Pact proposal. Expect a response by next turn. (2 DP spent)
   ⚠ The treasury will stand at -123 gold when the turn ends (358 now, −481 next turn) — the Ledger's Economy tab shows what drains it.
   Press End Turn again, Enter, or type end turn again to end the turn in deficit.
   ► end turn
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -195g | Other: +1449g | Upkeep: -3394g | Net: +360g
   Treasury: 718g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Mack loses 1,612 troops
   Supply shortage at Tyrol: Archduke John loses 620 troops
   Supply shortage at Franche-Comte: Ney loses 977 troops
   Supply shortage at Franche-Comte: Davout loses 1,058 troops
   Supply shortage at Franche-Comte: Lannes loses 732 troops
   Supply shortage at Franche-Comte: Murat loses 895 troops
   Garrison at Munich reinforced: 10,000 -> 12,000
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Lorraine. Holland pays them; their dead will be its grief.
   Talleyrand returns from Prussia with excellent news: they have accepted our proposal! The decisive factor was natural willingness to negotiate.
   Treaty signed: Peace → Non-Aggression with Prussia.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Deroy is on the wrong side of the frontier at Franconia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 3 turns of safe passage.
   Bernadotte is no nearer home — 1 march still to go from Swabia, and 2 turns to spare on the safe passage before his corps is interned.
   Deroy is no nearer home — 2 marches still to go from Franconia, and 1 turn to spare on the safe passage before his corps is interned.
map names: Russia(2627,167)  Ottoman Empire(2396,798)  Prussia(2169,264)  Spain(1144,896)  Sweden(1910,-6)  Saxony(2125,381)  Austria(2071,509)  France(1539,531)  Bavaria(1970,477)  Kingdom of Italy(1762,679)  Denmark(1732,38)  Papal States(1878,787)  Britain(1370,270)  Hanover(1720,314)  Naples(1801,921)  Sardinia(1630,811)  Hesse(1908,379)  Holland(1733,362)  Switzerland(1754,561)
map pieces: 100(1292,371)  45(1264,616)  30(1316,796)  20(2005,80)  18(1973,27)  15(2332,670)  12(1536,246)  10(937,816)  10(1950,177)  5(1798,854)  Deroy(1970,441)  ?(1990,282)  Brunswick(1991,243)  Bernadotte(1867,457)  ?(1987,613)  Mack(1967,559)  Archduke John(1986,585)  Soult(1719,422)  Napoleon(1749,395)  Ney +3(1809,485)  Dumonceau(1738,281)  Massena(1929,612)  ?(2126,416)  ?(1990,346)  ?(1893,582)  ?(1908,414)  25k(1538,496)  12k(1483,442)  ?(1754,596)  10k(1770,424)  12k(1667,395)  10k(1929,679)
```

```
#0172  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0172_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 74 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: Envoy from Ottoman Empire @(3442,64)]  [icon: Envoy from Portugal @(3484,64)]  [icon: Davout arrived @(3526,64)]  [icon: Murat arrived @(3568,64)]  [+8]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munich
   0 →
   T:5
   controls: [THIRD COALITION  ▸]  [War for Munich]  [War for Munich — Austria, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   718 (+360 next turn)
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
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Lorraine. Holland pays them; their dead will be its grief.
   Talleyrand returns from Prussia with excellent news: they have accepted our proposal! The decisive factor was natural willingness to negotiate.
   Treaty signed: Peace → Non-Aggression with Prussia.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Deroy is on the wrong side of the frontier at Franconia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 3 turns of safe passage.
   Bernadotte is no nearer home — 1 march still to go from Swabia, and 2 turns to spare on the safe passage before his corps is interned.
   Deroy is no nearer home — 2 marches still to go from Franconia, and 1 turn to spare on the safe passage before his corps is interned.
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte marches to Swabia. 1 region to Franche-Comte.
   Swabia feeds 40,000; the 88,830 men standing there would lose ~4,290 a turn to short supply.
   Swabia is Austria's soil — the corps standing there are fed by contract, about −192g more a turn.
   Davout: Davout arrives at Franche-Comte. Davout: "Accomplished as ordered. The army is intact."
   Murat: Murat arrives at Franche-Comte.
   Franche-Comte feeds 52,500; the 66,000 men standing there would lose ~1,573 a turn to short supply. Murat: "It is done. Point me at something that shoots back, Sire."
   Ney: Ney arrives at Franche-Comte.
   Franche-Comte feeds 52,500; the 90,000 men standing there would lose ~3,662 a turn to short supply. Ney: "Accomplished. The men want a battle, not another road."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Deroy and Bernadotte are no nearer home, and the safe passage leaves one turn to spare. After that their corps will be interned where they stand.
   • Sire — under the truce with Austria. Deroy is on the wrong side of the frontier at Franconia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 3 turns of safe passage.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 718g (+360 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Franche-Comte — 24,942 — Awaiting orders.
   - Ney — Franche-Comte — 23,023 — Awaiting orders.
   > Deroy — Franconia — 22,000 — Moving to Franche-Comte — 2 turns out. (to the letter) Trust:40
   - Murat — Franche-Comte — 21,105 — Awaiting orders.
   - Lannes — Franche-Comte — 17,268 — Awaiting orders.
   > Bernadotte — Swabia — 16,830 — Moving to Franche-Comte — arrives next turn. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Mack — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 3,662 men, at Franche-Comte.
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   DIPLOMATIC EVENTS
   Talleyrand returns from Bavaria with a response.
   Bavaria has been established under the protection of France.
   Sire — France and Bavaria have signed the Vassalage.
   Talleyrand has departed for the court of Prussia.
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   An envoy from Switzerland has arrived with a petition.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Lorraine. Holland pays them; their dead will be its grief.
   Sire — France and Prussia have signed the Non-Aggression Pact.
   Talleyrand returns from Prussia with a response.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Ottoman Empire — Open Borders Agreement
   - Portugal — Open Borders Agreement
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War for Munich) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0173  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0173_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   718 (+360 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0174  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0174_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0175  scroll 1828 500 down 9  ->  ok
  (scrolled down 9 at (1828, 500))
view: <run>\frames\0175_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) ──
   controls: [icon: Zoomed out as far as the map goes — the whole theatre is in  @(1794,992)](disabled: Zoomed out as far as the map goes — the whole theatre is in view)  [icon: The whole theatre is already in view @(1828,992)](disabled: The whole theatre is already in view)  [icon: Zoom in  (+) @(1862,992)]
── command window, last lines ──
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1942,482)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Deroy(1943,451)  ?(1959,325)  Brunswick(1958,287)  Bernadotte(1859,454)  ?(1965,579)  Mack(1940,540)  Archduke John(1920,514)  Soult(1741,436)  Napoleon(1764,462)  Ney +3(1813,487)  Dumonceau(1755,322)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1893,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1788,420)  12k(1693,420)  10k(1910,645)
```

```
#0176  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0176_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) ──
   controls: [icon: Zoom out  (−) @(1794,992)]  [icon: Fit Europe — the whole theatre  (Home re-centres) @(1828,992)]  [icon: Zoom in  (+) @(1862,992)]
── command window, last lines ──
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0177  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0177_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0178  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0178_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 383 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0179  scroll 1828 500 down 9  ->  ok
  (scrolled down 9 at (1828, 500))
view: <run>\frames\0179_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0180  scroll 1828 500 up 3  ->  ok
  (scrolled up 3 at (1828, 500))
view: <run>\frames\0180_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 441 of 528 px] ──
   LOAD GAME
   controls: [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0181  scroll 1828 500 up 3  ->  ok
  (scrolled up 3 at (1828, 500))
view: <run>\frames\0181_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 354 of 528 px] ──
   LOAD GAME
   controls: [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 74/100 [Formed] — up 4 since yesterday (Vassalized via treaty +5, Natural threat decay -3, Keeps Europe's largest army +1, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A treaty's patience is short, Sire. Order him home, or explain the loss to the Senate."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0182  click replay_truce_mission  ->  ok
  (clicked at (1825, 405))
view: <run>\frames\0182_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain binds Austria to the war @(3571,62)]  [icon: Treaty with Austria @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 1477 of 1477 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
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
   Game loaded successfully.
   Loaded: replay_truce_mission
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+228 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 26,000 — Awaiting orders.
   - Ney — Swabia — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, march to Franconia
   • Davout, fortify (2 AP)
   • build supply depot in Lorraine — 300g
   • build fortification in Lorraine — 400g
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2603,177)  Ottoman Empire(2378,789)  Prussia(2159,271)  Spain(1166,884)  Sweden(1908,9)  Saxony(2117,385)  Austria(2129,591)  France(1548,530)  Bavaria(1926,499)  Kingdom of Italy(1764,674)  Denmark(1735,52)  Papal States(1877,778)  Portugal(1090,817)  Britain(1384,277)  Hanover(1723,320)  Naples(1802,908)  Sardinia(1636,801)  Hesse(1907,383)  Holland(1735,366)  Switzerland(1757,559)
map pieces: 100(1308,375)  45(1282,612)  30(1332,786)  20(2000,92)  18(1970,40)  15(2318,664)  12(1545,253)  10(965,805)  10(1947,187)  5(1799,843)  Bernadotte(1951,442)  Deroy(1980,415)  ?(1985,289)  Brunswick(1985,251)  Ney(1851,458)  Davout(1880,415)  ?(1983,594)  Mack(1963,556)  Archduke John(1981,530)  Soult(1722,424)  Napoleon(1752,397)  Lannes(1795,497)  Murat(1800,470)  Massena(1926,608)  ?(2117,419)  ?(1985,351)  ?(1916,580)  ?(1905,349)  25k(1548,496)  12k(1494,444)  ?(1756,593)  12k(1673,399)  10k(1927,674)
```

```
#0183  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0183_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 789 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Your courts (1)
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -57 (Hostile)  [MISSION]]  [Britain  —  At War  |  -90 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0184  click Austria  ->  ok
  (clicked at (1825, 627))
view: <run>\frames\0184_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 464 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War with the Third Coalition   Relation: -57 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Sire, the truce with Austria has 2 turns to run; the ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 5 tu …
   Their design is aimed at France herself.
   Their price is 1320g — the treasury holds 800g.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Cancel: Improve Relations  —  Hostile (+20 over 3 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. It buys the design's sleep, not her goodwill: +5 relations (−57 → −52); she still counts toward a league until relations reach −10. Buying it wakes Primacy in Germany next (1392g to buy off in turn).](disabled: Their price is 1320g — the treasury holds 800g.)  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured. Honouring it means declaring on the aggressor: France's relations fall 30 with that court and 15 with every other (15 and 7 after a rejected ultimatum).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0185  click Back  ->  ok
  (clicked at (1774, 788))
view: <run>\frames\0185_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 789 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Your courts (1)
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -57 (Hostile)  [MISSION]]  [Britain  —  At War  |  -90 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0186  click Britain  ->  ok
  (clicked at (1825, 690))
view: <run>\frames\0186_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 372 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War with the Third Coalition   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Sire, the field reads +0 and no road carries. Propose Peace comes nearest at 3 of 50; her loyalty to the league — she has no reason of her own to break …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Propose Armistice (1 DP)  —  Unlikely]  [Open Settlement — the whole table: Britain and Russia]  [Propose White Peace — the whole table: Britain and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5](disabled: Talleyrand is at Austria's court — F1 → Austria → Cancel. Recalling forfeits Austria's rem)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0187  click Propose Peace  ->  ok
  (clicked at (1825, 554))
view: <run>\frames\0187_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 108 of 372 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 3 - REJECT / Key advantage: Base Disposition / Key obstacle: Coalition Loyalty /  / War Summary / The War with the Third Coalition: nothing taken yet on either side. / War score: 0 -> / Settlement: White Peace / Objective: Defe …
   ▼ more below
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1522 of 1522 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
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
   ► propose peace with Britain
map: unchanged (53 labels)
```

```
#0188  click Send as suggested  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0188_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 2/5
   Threat 70 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving... (paused)]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain binds Austria to the war @(3209,62)]  [Talleyrand at Austria — Improving Relations (paused — carrying a letter)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 1609 of 1609 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
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
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0189  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0189_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 789 px] ──
   THE CABINET
   DP: 2
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Your courts (1)
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -57 (Hostile)  [MISSION]]  [Britain  —  At War  |  -90 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0190  scroll 1828 550 down 6  ->  ok
  (scrolled down 6 at (1828, 550))
view: <run>\frames\0190_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 294 of 797 px] ──
   THE CABINET
   DP: 2
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (2)
   Treaties (3)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Austria  —  Armistice  |  -57 (Hostile)  [MISSION]]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -57 (Hostile)  [MISSION]]  [Spain  —  Alliance  |  +36 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0191  click Spain  ->  ok
  (clicked at (1825, 539))
view: <run>\frames\0191_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 44 px, 0 of 634 px] ──
   THE CABINET — Spain
   DP: 2
   TALLEYRAND'S ASSESSMENT — SPAIN / Status: Alliance   Relation: +36 (Friendly) /  / "Our alliance with Spain holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Our alliance with Spain frays, Sire — relations stand at 36, short of the 40 it holds on. Reassure Ally is shut while Talleyrand carries a proposal abroad — it opens when he is home.
   Talleyrand is in transit with the peace treaty to Britain — home in 1 turn
   Talleyrand is in transit with the peace treaty to Britain — home in 1 turn
   Talleyrand is in transit with the peace treaty to Britain — home in 1 turn
   Talleyrand is in transit with the peace treaty to Britain — home in 1 turn
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Propose Vassal (3 DP)  —  Doubtful](disabled: Talleyrand is in transit with the peace treaty to Britain — home in 1 turn)  [Declare War (1 DP)](disabled: Talleyrand is in transit with the peace treaty to Britain — home in 1 turn)  [Break Treaty (1 DP)](disabled: Talleyrand is in transit with the peace treaty to Britain — home in 1 turn)  [Downgrade (1 DP)](disabled: Talleyrand is in transit with the peace treaty to Britain — home in 1 turn)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0192  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0192_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0193  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0193_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0194  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0194_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 354 of 528 px] ──
   LOAD GAME
   controls: [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0195  scroll 1828 500 down 9  ->  ok
  (scrolled down 9 at (1828, 500))
view: <run>\frames\0195_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0196  scroll 1828 500 up 5  ->  ok
  (scrolled up 5 at (1828, 500))
view: <run>\frames\0196_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 383 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0197  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0197_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 267 of 528 px] ──
   LOAD GAME
   controls: [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) Talleyrand carries this letter; his Improve Relations at Austria pauses until he is home (about 1 turn).
map: unchanged (53 labels)
```

```
#0198  click replay_truce_mission  ->  ok
  (clicked at (1825, 483))
view: <run>\frames\0198_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain binds Austria to the war @(3571,62)]  [icon: Treaty with Austria @(3613,62)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1477 of 1477 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
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
   Game loaded successfully.
   Loaded: replay_truce_mission
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+228 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 26,000 — Awaiting orders.
   - Ney — Swabia — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, march to Franconia
   • Davout, fortify (2 AP)
   • build supply depot in Lorraine — 300g
   • build fortification in Lorraine — 400g
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0199  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0199_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 789 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Your courts (1)
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -57 (Hostile)  [MISSION]]  [Britain  —  At War  |  -90 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0200  scroll 1828 550 down 6  ->  ok
  (scrolled down 6 at (1828, 550))
view: <run>\frames\0200_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 294 of 797 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (2)
   Treaties (3)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Austria  —  Armistice  |  -57 (Hostile)  [MISSION]]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -57 (Hostile)  [MISSION]]  [Spain  —  Alliance  |  +36 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0201  click Spain  ->  ok
  (clicked at (1825, 539))
view: <run>\frames\0201_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 200 px, 0 of 592 px] ──
   THE CABINET — Spain
   DP: 5
   TALLEYRAND'S ASSESSMENT — SPAIN / Status: Alliance   Relation: +36 (Friendly) /  / "Our alliance with Spain holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Our alliance with Spain frays, Sire — relations stand at 36, short of the 40 it holds on. Reassure Ally is shut while Talleyrand is at Austria's court — recall Talleyrand from Austria first (the …
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   Talleyrand is at Austria's court — F1 → Austria → Cancel. Recalling forfeits Austria's remaining courtship (+8 a turn, until the peace is signed); Spain, at 36, is under the 40 line and slides 1 a turn — the alliance lapses in about 30 turns.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Propose Vassal (3 DP)  —  Doubtful]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Reassure Ally (1 DP)  —  +4 relation/turn](disabled: Talleyrand is at Austria's court — F1 → Austria → Cancel. Recalling forfeits Austria's rem)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0202  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0202_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0203  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0203_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0204  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0204_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0205  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0205_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0206  scroll 1828 500 down 9  ->  ok
  (scrolled down 9 at (1828, 500))
view: <run>\frames\0206_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) ──
   controls: [icon: Zoomed out as far as the map goes — the whole theatre is in  @(1794,992)](disabled: Zoomed out as far as the map goes — the whole theatre is in view)  [icon: The whole theatre is already in view @(1828,992)](disabled: The whole theatre is already in view)  [icon: Zoom in  (+) @(1862,992)]
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0207  scroll 1828 500 up 6  ->  ok
  (scrolled up 6 at (1828, 500))
view: <run>\frames\0207_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1477 of 1477 px]: unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0) ──
   controls: [icon: Zoom out  (−) @(1794,992)]  [icon: Fit Europe — the whole theatre  (Home re-centres) @(1828,992)]  [icon: Zoom in  (+) @(1862,992)]
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1531,531)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,370)  45(1247,623)  30(1301,807)  20(2010,71)  18(1977,15)  15(2347,678)  12(1526,241)  10(910,828)  10(1954,171)  5(1797,867)  Bernadotte(1959,439)  Deroy(1990,413)  ?(1995,275)  Brunswick(1995,238)  Ney(1852,456)  Davout(1883,413)  ?(1971,590)  Mack(1971,563)  ?(2000,600)  Archduke John(1990,537)  Soult(1716,419)  Napoleon(1747,393)  Lannes(1793,497)  Murat(1803,471)  Massena(1933,616)  ?(2135,412)  ?(1995,341)  ?(1921,587)  ?(1910,341)  25k(1530,496)  12k(1473,441)  ?(1752,598)  12k(1678,392)  10k(1932,685)
```

```
#0208  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0208_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1477 of 1477 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0209  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0209_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0210  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0210_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 267 of 528 px] ──
   LOAD GAME
   controls: [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0211  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0211_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0212  click replay_design_peace  ->  ERROR: no visible control's text holds "replay_design_peace"
view: <run>\frames\0212_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0213  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0213_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0214  click replay_design_peace  ->  ERROR: no visible control's text holds "replay_design_peace"
view: <run>\frames\0214_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0215  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0215_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px] ──
   LOAD GAME
   controls: [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0216  click replay_design_peace  ->  ok
  (clicked at (1825, 410))
view: <run>\frames\0216_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 3/5
   Threat 45 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain Left Coalition @(3529,62)]  [icon: Austria Left Coalition @(3571,62)]  [icon: Coalition Dissolved @(3613,62)]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,900 (+1,275 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_design_peace
   ════════════════════════════════════
   MORNING DISPATCH — Turn 7
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 3,900g (+1,275 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Rhineland — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — substantial force [partial]
   Mack — Swabia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, march to Swabia
   • Davout, fortify (2 AP)
   • enact the Train des Équipages — 3,500g, then 200g a turn (cures Living off the land — the court's doctrine flaw — while its Staff stands)
   • recruit infantry in Rhineland — 246g for 3,000 men under Davout
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1531,531)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  ?(1975,442)  Deroy(1975,405)  ?(1995,275)  Brunswick(1995,238)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1826,343)  Bernadotte(1841,317)  ?(1988,600)  Archduke John(1981,563)  Soult(1716,419)  Napoleon(1747,393)  Lannes(1793,497)  Murat(1825,471)  Massena(1933,616)  ?(2135,412)  ?(1995,341)  ?(1894,587)  ?(1916,410)  25k(1530,496)  12k(1473,441)  ?(1752,598)  12k(1678,392)  10k(1932,685)
```

```
#0217  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0217_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Your courts (1)
   Treaties (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Peace  |  +10 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +40 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0218  scroll 1828 550 down 4  ->  ok
  (scrolled down 4 at (1828, 550))
view: <run>\frames\0218_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 233 of 750 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Your courts (1)
   Treaties (2)
   Vassals (3)
   Neutral (14)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Formable Nations — states that could yet exist]  [Prussia  —  Peace  |  +10 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Britain  —  Peace  |  -45 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0219  click Britain  ->  ok
  (clicked at (1825, 703))
view: <run>\frames\0219_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 578 px] ──
   THE CABINET — Britain
   DP: 3
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: Peace   Relation: -45 (Hostile) /  / "Relations with Britain remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. Improve Relations is shut while Talleyrand is at Prussia's court — recall Talleyrand from Prussia first (t …
   Relations with Britain stand at -45; an Open Borders needs -20.
   A vassalage of Britain needs a war (a dictated peace) or open borders and above — we stand at Peace.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Propose Open Borders (1 DP)  —  Hopeless](disabled: Relations with Britain stand at -45; an Open Borders needs -20.)  [Propose Vassal (3 DP)](disabled: A vassalage of Britain needs a war (a dictated peace) or open borders and above — we stand)  [Declare War (1 DP)]  [Send Ultimatum (2 DP)]  [Improve Relations (1 DP)  —  +8 relation/turn](disabled: Talleyrand is at Prussia's court — F1 → Prussia → Cancel. Recalling forfeits Prussia's rem)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,900 (+1,275 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0220  click Back  ->  ok
  (clicked at (1774, 788))
view: <run>\frames\0220_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Your courts (1)
   Treaties (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Peace  |  +10 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +40 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0221  scroll 1828 550 up 10  ->  ok
  (scrolled up 10 at (1828, 550))
view: <run>\frames\0221_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0222  scroll 1828 550 down 6  ->  ok
  (scrolled down 6 at (1828, 550))
view: <run>\frames\0222_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 294 of 774 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   Neutral (14)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Prussia  —  Peace  |  +10 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Britain  —  Peace  |  -45 (Hostile)]  [Russia  —  Peace  |  -45 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0223  click Austria  ->  ERROR: no visible control's text holds "Austria"
view: <run>\frames\0223_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 294 of 774 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0224  scroll 1828 550 down 10  ->  ok
  (scrolled down 10 at (1828, 550))
view: <run>\frames\0224_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 723 of 763 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Prussia  —  Peace  |  +10 (Neutral)  [MISSION]]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Saxony  —  Peace  |  -10 (Wary)]  [Hanover  —  Peace  |  -50 (Hostile)]  [Hesse  —  Peace  |  0 (Neutral)]  [Papal States  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0225  click Austria  ->  ERROR: no visible control's text holds "Austria"
view: <run>\frames\0225_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 723 of 763 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0226  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0226_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0227  click Diplomacy (D)  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0227_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 2797 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Prussia
   DP: 3/5
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  /   Britain [Neutral] — PEACE  Relation: -45 (Hostile) /   Doctrine: The Line Holds; flaw: Irreplaceable (uncured — the Militia Transfer would end it once the Horse Guards Reforms stands) /   Diplomat: Castlereagh (Hawk) — Skill 7 /   Regions: 11   …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0228  click BALANCE OF EUROPE  ->  ok
  (clicked at (1665, 273))
view: <run>\frames\0228_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 728 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Prussia
   DP: 3/5
   BALANCE OF EUROPE / ──────────────── / The courts are recovering from the last coalition. Cooldown: 5 turns. Europe's alarm stands at 45; no new coalition gathers below 60. /  / THE EMPEROR'S DESIGNS / No road is proclaimed. Three roads — one proclamation, and it cannot be undone. /   Road I — The Protector of the Rhine /     • The Confederation of the Rhine — 0 of 3 courts under the Emperor's pro …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [BALANCE OF EUROPE](disabled: You are reading this book)  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0229  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0229_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0230  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0230_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Your courts (1)
   Treaties (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Peace  |  +10 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +40 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0231  scroll 1828 550 down 8  ->  ok
  (scrolled down 8 at (1828, 550))
view: <run>\frames\0231_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 399 of 759 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (14)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Britain  —  Peace  |  -45 (Hostile)]  [Russia  —  Peace  |  -45 (Hostile)]  [Austria  —  Peace  |  -50 (Hostile)]  [Prussia  —  Peace  |  +10 (Neutral)  [MISSION]]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0232  click Austria  ->  ok
  (clicked at (1825, 617))
view: <run>\frames\0232_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 613 px] ──
   THE CABINET — Austria
   DP: 3
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -50 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. Improve Relations is shut while Talleyrand is at Prussia's court — recall Talleyrand from Prussia first (t …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. It buys the design's sleep, not her goodwill: +5 relations (−50 → −45); she still counts toward a league until relations reach −10. Buying it wakes Primacy in Germany next (1248g to buy off in turn).]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured. Honouring it means declaring on the aggressor: France's relations fall 30 with that court and 15 with every other (15 and 7 after a rejected ultimatum).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0233  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0233_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0234  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0234_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0235  type license Prussia against Hanover  ->  ok
  (typed and Enter; focus by grab_focus (the click did not focus the line))
view: <run>\frames\0235_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1610 of 1610 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,900 (+1,275 next turn)
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
   ► license Prussia against Hanover
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → Prussia → Sponsor Their Design — Licence.
   ⚜ Take your seat at the table (F1)
map: unchanged (54 labels)
```

```
#0236  look  ->  ok
  (a fresh frame)
view: <run>\frames\0236_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1610 of 1610 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► license Prussia against Hanover
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → Prussia → Sponsor Their Design — Licence.
   ⚜ Take your seat at the table (F1)
map: unchanged (54 labels)
```

```
#0237  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0237_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Your courts (1)
   Treaties (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Peace  |  +10 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +40 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1610 of 1610 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► license Prussia against Hanover
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → Prussia → Sponsor Their Design — Licence.
   ⚜ Take your seat at the table (F1)
map: unchanged (54 labels)
```

```
#0238  scroll 1828 550 down 4  ->  ok
  (scrolled down 4 at (1828, 550))
view: <run>\frames\0238_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 233 of 750 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Your courts (1)
   Treaties (2)
   Vassals (3)
   Neutral (14)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Formable Nations — states that could yet exist]  [Prussia  —  Peace  |  +10 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Britain  —  Peace  |  -45 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1610 of 1610 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► license Prussia against Hanover
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → Prussia → Sponsor Their Design — Licence.
   ⚜ Take your seat at the table (F1)
map: unchanged (54 labels)
```

```
#0239  click Prussia  ->  ok
  (clicked at (1825, 394))
view: <run>\frames\0239_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 244 px, 0 of 799 px] ──
   THE CABINET — Prussia
   DP: 3
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: +10 (Neutral) /  / "Prussia is neither friend nor foe. Opportunity exists for closer ties — open borders would be a natural first step." / Recommendation: Relations must improve before proposals will find purchase. Talleyrand is already at their court, Sire — net +7 a turn. / Talleyrand: "Prussia stands on the Emperor's roads, Sire — Th …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Cancel: Improve Relations  —  Wary → Neutral (+20, 2 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3). If Prussia then declares on Hanover, her relations with every court, France's included, fall 15 (France–Prussia now +10, +15 once this compact is struck, 0 after her declaration); the Improve Relations mission running with Prussia is set back the same 15.]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [↳ 400g a turn]  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. It buys the design's sleep, not her goodwill: +5 relations (+10 → +15); she already stands past the −10 line a league counts her below. Buying it wakes Armed Neutrality next (600g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1610 of 1610 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,900 (+1,275 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► license Prussia against Hanover
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   In the Cabinet: F1 → Prussia → Sponsor Their Design — Licence.
   ⚜ Take your seat at the table (F1)
map: unchanged (54 labels)
```

```
#0240  click Licence  ->  ok
  (clicked at (1825, 598))
view: <run>\frames\0240_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE CABINET ASKS:
   "License Prussia's design against Hanover: no gold, 1 diplomatic point. France blesses it and pledges non-interference for 10 turns. The compact binds France: marching on Prussia before it lapses, or guaranteeing Hanover, is reneging — relations -25 and the strongest casus belli in Europe. If Prussia then declares on Hanover, her relations with every court, France's included, fall 15 (France–Pruss …
   controls: [Grant the licence]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 3/5
   Threat 45 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1676 of 1676 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,900 (+1,275 next turn)
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
   ► sponsor Prussia against Hanover, 0 gold
   The Cabinet requests clarification...
map: unchanged (54 labels)
```

```
#0241  click No  ->  ok
  (clicked at (1829, 646))
view: <run>\frames\0241_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 3/5
   Threat 45 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain Left Coalition @(3529,62)]  [icon: Austria Left Coalition @(3571,62)]  [icon: Coalition Dissolved @(3613,62)]
── BottomLeftUI (layer 0) [scrolled 1743 of 1743 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,900 (+1,275 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (54 labels)
```

```
#0242  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0242_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Holland @(3189,64)]  [icon: European Courts Concerned @(3231,64)]  [icon: A Moment of History: The Bavarian Match @(3273,64)]  [icon: Envoy from Prussia @(3315,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]
── BottomLeftUI (layer 0) [scrolled 1853 of 1853 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,243 (+1,327 next turn)
   Inf:
   82,500
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
   ► end turn
   ═══════════════════════════════════════
   TURN 8 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -22g | Other: +1337g | Upkeep: -2562g | Net: +1343g | Spent: 2100g
   Treasury: 5,243g
   Actions refreshed: 4/4
   Supply shortage at Rhineland: Ney loses 522 troops
   Supply shortage at Rhineland: Davout loses 565 troops
   Supply shortage at Rhineland: Bernadotte loses 369 troops
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Britain, Spain and Bavaria stirred, but their formations remain beyond our sight.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 8
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   • Sire — an envoy from Prussia has arrived with a proposal.
   • Sire — Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The cheapest court to keep out of it is Ottoman Empire: Talleyrand brings her to −10 in 1 turn (1 DP); buying off her design costs 600 gold (+5 relations; she still counts toward a league until relations reach −10).
   SITUATION
   France holds 28 regions. Treasury: 5,243g (+1,343 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 25,435 — Awaiting orders.
   - Ney — Rhineland — 23,478 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Rhineland — 16,631 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Archduke John — Tyrol — substantial force [partial]
   Deroy — Franconia — substantial force [last known - T1]
   Brunswick — Berlin — large force [last known - T1]
   TURN EVENTS
   Supply cost you 1,456 men, at Rhineland.
   2 satellites drifted — Holland and Switzerland.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 17. 1 DP a turn, 3 so far.
   An envoy from Holland has arrived with a petition.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - The Cabinet — A Moment of History
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1531,531)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  Ney(1811,369)  Davout(1826,343)  Bernadotte(1841,317)  ?(1988,600)  Archduke John(1981,563)  Soult(1716,419)  Napoleon(1747,393)  Lannes(1793,497)  Murat(1825,471)  Massena(1933,616)  ?(1894,587)  ?(1910,410)  25k(1530,496)  12k(1473,441)  ?(1752,598)  12k(1678,392)  10k(1932,685)
```

```
#0243  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0243_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1853 of 1853 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0244  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0244_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1853 of 1853 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,243 (+1,327 next turn)
   Inf:
   82,500
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0245  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0245_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1853 of 1853 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0246  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0246_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0247  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0247_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px] ──
   LOAD GAME
   controls: [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0248  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0248_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0249  click replay_guarded  ->  ERROR: no visible control's text holds "replay_guarded"
view: <run>\frames\0249_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0250  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0250_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0251  click replay_guarded  ->  ERROR: no visible control's text holds "replay_guarded"
view: <run>\frames\0251_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0252  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0252_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px] ──
   LOAD GAME
   controls: [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0253  click replay_guarded  ->  ERROR: no visible control's text holds "replay_guarded"
view: <run>\frames\0253_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0254  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0254_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['load'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px] ──
   LOAD GAME
   controls: [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs] — unchanged since yesterday (Natural threat decay -2, Denied national designs +1, The weight of the hegemon +1)
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: 5 lesser courts would march. Bound for now by a fresh peace: Austria, Britain and Russia. The Balance of Europe (D, or Alt+D while you type) names the price to keep each court out.
   Berthier: "Your armies stand ready, Sire. The initiative is ours."
   ════════════════════════════════════
map: unchanged (46 labels)
```

```
#0255  click replay_guarded  ->  ok
  (clicked at (1825, 474))
view: <run>\frames\0255_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:11
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1565 of 1565 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (−401 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_guarded
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (-401 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 51% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Napoleon — Flanders — 37,692 — Awaiting orders.
   - Soult — Dresden — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Kutuzov — Podolia — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Hohenlohe — Silesia — substantial force [partial]
   Vienna garrison — Vienna — garrison — substantial force [partial]
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
   • build supply depot in Rhineland — 300g
   • build fortification in Rhineland — 400g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
   The Emperor's Designs — I The Protector of the Rhine, II The Crowns of Italy, III The Continental System: one proclamation decides what the Empire is for, and it cannot be undone. In the Cabinet: F1 → The Emperor's Designs.
   Berthier: "Our finances strain, Sire. The treasury bleeds 401g this turn."
   ════════════════════════════════════
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
   • "what if Ney attacks Mack" — free: it names who marches with him before you commit
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2119,262)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1531,531)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Naples(1801,933)  Hanover(1657,294)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  ?(2301,288)  Hohenlohe(2300,250)  Soult(2135,340)  Bernadotte(1959,439)  Deroy(1990,413)  ?(2371,372)  Kutuzov(2370,335)  ?(1995,275)  Brunswick(1995,238)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1841,343)  ?(1988,600)  Archduke John(1981,563)  Lannes(1793,497)  Murat(1825,471)  Napoleon(1684,326)  Massena(1933,616)  10k(2134,412)  ?(2187,562)  ?(1995,341)  ?(1894,587)  ?(1916,410)  25k(1530,496)  12k(1473,441)  ?(1752,598)  ?(1734,393)  12k(1684,392)  10k(1932,685)
```

```
#0256  type Soult, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0256_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
reply: ok Berlin and Brunswick are Prussia's guarded ground (Armed Neutrality) — standing in them costs −25 with Prussia — march, go round or cancel?
── ClarificationPopup (layer 102) ──
   BERTHIER ASKS:
   "Berlin and Brunswick are Prussia's guarded ground (Armed Neutrality) — standing in them costs −25 with Prussia — march, go round or cancel?"
   controls: [March (1 AP)]  [Go round (1 AP, 5 provinces)]  [Cancel Order]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (−401 next turn)
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
   ► Soult, march to Flanders
   Berthier requests clarification...
map: unchanged (59 labels)
```

```
#0257  click Cancel Order  ->  ok
  (clicked at (1829, 572))
view: <run>\frames\0257_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:11
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (−401 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Order cancelled.
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (59 labels)
```

```
#0258  type Napoleon, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0258_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Napoleon already stands at Flanders — nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1787 of 1787 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (−401 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, march to Flanders
   Napoleon already stands at Flanders — nothing spent.
map: unchanged (59 labels)
```

```
#0259  type Napoleon, march to Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0259_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1919 of 1919 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (−401 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0260  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0260_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1919 of 1919 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0261  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0261_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1919 of 1919 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (−401 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0262  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0262_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1919 of 1919 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0263  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0263_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0264  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0264_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px] ──
   LOAD GAME
   controls: [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0265  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0265_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0266  click replay_table  ->  ERROR: no visible control's text holds "replay_table"
view: <run>\frames\0266_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0267  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0267_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0268  click replay_table  ->  ERROR: no visible control's text holds "replay_table"
view: <run>\frames\0268_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0269  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0269_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px] ──
   LOAD GAME
   controls: [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0270  click replay_table  ->  ERROR: no visible control's text holds "replay_table"
view: <run>\frames\0270_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0271  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0271_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px] ──
   LOAD GAME
   controls: [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, march to Paris
   Napoleon begins march to Paris. Route: Picardy → Artois → Paris. Arrives in 3 turns. Moves to Picardy.
   Picardy feeds 22,500; the 37,692 men standing there would lose ~381 a turn to short supply. (1 AP — the Emperor commands in his own name.)
   [3/4 actions remaining]
map: unchanged (59 labels)
```

```
#0272  click replay_table  ->  ok
  (clicked at (1825, 426))
view: <run>\frames\0272_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +10 ↑
   T:15
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_table
   ════════════════════════════════════
   MORNING DISPATCH — Turn 16
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 30 regions. Treasury: 6,241g (+969 by the accounts)
   The courts at war hold 26 regions. Estimated enemy strength: 44% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
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
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+26)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Mack
   • Davout, march to Lorraine
   • recruit infantry in Rhineland — 714g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1500,504)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1333,231)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  Bernadotte(1959,439)  Deroy(1990,413)  ?(1995,275)  Brunswick(1995,238)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1841,343)  ?(1988,600)  Archduke John(1981,563)  Soult(1716,419)  Napoleon(1747,393)  Lannes(1793,497)  Murat(1825,471)  Massena(1933,616)  ?(2135,412)  ?(1995,341)  ?(1894,587)  ?(1916,410)  25k(1530,470)  12k(1473,441)  ?(1752,598)  12k(1678,392)  10k(1932,685)
```

```
#0273  click War with  ->  ERROR: no visible control's text holds "War with"
view: <run>\frames\0273_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0274  click War for Munster  ->  ok
  (clicked at (3429, 996))
view: <run>\frames\0274_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) [scrolled 0 of 398 px] ──
   WAR FOR MUNSTER
   BR
   +10
   FR
   The ledger of one war — its score, its fronts, and the price of peace. Negotiate opens the table, where every court signs for itself. /  / The War for Munster: France holds Munster and Ulster of Britain's. / With: Britain + Austria + Russia /  / Settlement Tier: White Peace / A peace signed now is on the held line: Munster and Ulster stay ours by the treaty — and closes the Ireland carve — erect i …
   controls: [icon @(3139,189)]  [Negotiate with Britain]  [Negotiate with Austria]  [Negotiate with Russia]  [Open Settlement]  [Request Terms](disabled: Britain leads a league that is not yet spent, Sire — it names no terms while it can still )
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0275  click Open Settlement  ->  ok
  (clicked at (2771, 872))
view: <run>\frames\0275_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 135 px, 0 of 574 px] ──
   This draft will not carry as it stands. / the War for Munster — the table with Austria + Britain + Russia - Whole-war settlement / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria -18/50, Britain 26/50, Russia -18/50. / Treasury 6,241 gold: committed 1,000 / reserve 500 / remaining 4,741 / Sire, this settlement of the War for M …
   The table /   * Austria ▸ - Holding out (-18/50) White peace /       Blocker: War objective alignment /       Metternich regrets that Austria must remain… unconvinced — the terms would end the war without the object it was fought for. /       + Add demand /   * Britain ▸ - Holding out (26/50) Demanded: Ireland carved out; Conceded: 1000g /       Blocker: Term harshness /       Castlereagh declines …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War for Munster — the table with Austria + Britain + Russia cannot be ratified now: the terms weigh heavier than their defeat. Revise terms or stand down b …
   controls: <Austria ▸>  <+ Add demand>  <Britain ▸>  [icon: - Britain · Conceded · France pays 1000 gold (yours) up to 1,0 @(1559,460)]  [icon: + Britain · Conceded · France pays 1000 gold (yours) up to 1,0 @(1577,460)]  <Remove>  <Remove>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Drop Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  <Grant>  <Decline>  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
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
   Opening settlement review for Britain
map: unchanged (53 labels)
```

```
#0276  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0276_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 179 px, 0 of 508 px] ──
   This draft will not carry as it stands. / the War for Munster — the table with Austria + Britain + Russia - Whole-war settlement / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria -12/50, Britain 30/50, Russia -12/50. / "Gold past 1,000 buys nothing more from Britain at this table, Sire." / Treasury 6,241 gold: committed 1,200  …
   ▼ more below
   The table /   * Austria ▸ - Holding out (-12/50) Conceded: 100g /       Blocker: War objective alignment /       Metternich regrets that Austria must remain… unconvinced — the terms would end the war without the object it was fought for. /       Conceded · France pays 100 gold  [-][+] up to 1,000  Remove /       + Add demand /   * Britain ▸ - Holding out (30/50) Demanded: Ireland carved out; Conce …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War for Munster — the table with Austria + Britain + Russia cannot be ratified now: the terms weigh heavier than their defeat. Revise terms or stand down b …
   controls: <Austria ▸>  [icon: - Austria · Conceded · France pays 100 gold up to 1,000 Remove @(1504,371)]  [icon: + Austria · Conceded · France pays 100 gold up to 1,000 Remove @(1522,371)]  <Remove>  <+ Add demand>  <Britain ▸>  [icon: - Britain · Conceded · France pays 1000 gold (yours) up to 1,0 @(1559,482)]  [icon: + Britain · Conceded · France pays 1000 gold (yours) up to 1,0 @(1577,482)]  <Remove>  <Remove>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Drop Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1543 of 1543 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
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
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0277  click +  ->  ERROR: 2 controls match "+" — pick one with click#N
  candidates: #1 [icon: + Austria · Conceded · France pays 100 gold up to 1,000 Remove @(1522,371)] on ProposalConfirmPopup @(1522,371) | #2 [icon: + Britain · Conceded · France pays 1000 gold (yours) up to 1,0 @(1577,482)] on ProposalConfirmPopup @(1577,482)
view: <run>\frames\0277_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 179 px, 0 of 508 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1543 of 1543 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Opening settlement review for Britain
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0278  click#2 +  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0278_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 179 px, 0 of 508 px] ──
   This draft will not carry as it stands. / the War for Munster — the table with Austria + Britain + Russia - Whole-war settlement / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria -12/50, Britain 30/50, Russia -12/50. / "Gold past 1,000 buys nothing more from Britain at this table, Sire — set to 1,000." / Treasury 6,241 gold: c …
   ▼ more below
   The table /   * Austria ▸ - Holding out (-12/50) Conceded: 100g /       Blocker: War objective alignment /       Metternich regrets that Austria must remain… unconvinced — the terms would end the war without the object it was fought for. /       Conceded · France pays 100 gold  [-][+] up to 1,000  Remove /       + Add demand /   * Britain ▸ - Holding out (30/50) Demanded: Ireland carved out; Conce …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War for Munster — the table with Austria + Britain + Russia cannot be ratified now: the terms weigh heavier than their defeat. Revise terms or stand down b …
   controls: <Austria ▸>  [icon: - Austria · Conceded · France pays 100 gold up to 1,000 Remove @(1504,371)]  [icon: + Austria · Conceded · France pays 100 gold up to 1,000 Remove @(1522,371)]  <Remove>  <+ Add demand>  <Britain ▸>  [icon: - Britain · Conceded · France pays 1000 gold (yours) up to 1,0 @(1559,482)]  [icon: + Britain · Conceded · France pays 1000 gold (yours) up to 1,0 @(1577,482)]  <Remove>  <Remove>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Drop Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
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
   Directing Talleyrand: settlement demand set magnitude
map: unchanged (53 labels)
```

```
#0279  click Back Out  ->  ok
  (clicked at (2250, 969))
view: <run>\frames\0279_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +10 ↑
   T:15
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept until the turn ends — reopen Settlement this turn to continue.
map: unchanged (53 labels)
```

```
#0280  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0280_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 136 px] ──
   ENEMY PHASE - Turn 16
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 5,044 casualties, 48,956 remaining /     Massena: 4,635 casualties, 37,365 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Archduke Charles: "France pays …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 17 — Late May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (4)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2118 of 2118 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,035 (+969 next turn)
   Inf:
   82,350
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   Your unratified settlement draft with Britain (5 clauses) was set aside at turn's end (a draft lasts one turn).
   Bavaria's petition over Tyrol lapses with the settlement it was filed against, set aside at turn's end.
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2890g | Occupation: -30g | Charges of Empire: -157g | Admiralty: -90g | Blockade: -219g | Materiel: -231g | Other: +1295g | Upkeep: -2664g | Net: +794g
   Treasury: 7,035g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,443 troops
   Supply shortage at Tyrol: Archduke John loses 589 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2079,510)  France(1500,504)  Bavaria(1962,501)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1333,231)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  Bernadotte(1959,439)  Deroy(1990,413)  ?(1995,275)  Brunswick(1995,238)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1841,343)  ?(1992,600)  Archduke Charles(1972,563)  Archduke John(1962,537)  Soult(1716,419)  Napoleon(1747,393)  Lannes(1793,497)  Murat(1825,471)  Dumonceau(1734,276)  Massena(1917,616)  Teulie(1948,590)  ?(2135,412)  ?(1995,341)  ?(1921,645)  ?(1916,410)  25k(1530,470)  12k(1473,441)  ?(1752,598)  10k(1764,422)  12k(1678,392)  10k(1932,685)
```

```
#0281  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0281_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   42,000 → 37,365
   54,000 → 48,956
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 16
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (4)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: Envoy from Prussia @(3442,64)]  [icon: Envoy from Ottoman Empire @(3484,64)]  [icon: Envoy from Portugal @(3526,64)]  [icon: The Marshalate awaits @(3568,64)]  [+1]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Munster
   +8 →
   T:16
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,035 (+969 next turn)
   Inf:
   82,350
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   Your unratified settlement draft with Britain (5 clauses) was set aside at turn's end (a draft lasts one turn).
   Bavaria's petition over Tyrol lapses with the settlement it was filed against, set aside at turn's end.
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2890g | Occupation: -30g | Charges of Empire: -157g | Admiralty: -90g | Blockade: -219g | Materiel: -231g | Other: +1295g | Upkeep: -2664g | Net: +794g
   Treasury: 7,035g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,443 troops
   Supply shortage at Tyrol: Archduke John loses 589 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 17
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 30 regions. Treasury: 7,035g (+1,025 by the accounts)
   The courts at war hold 27 regions. Estimated enemy strength: 69% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 37,365 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
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
   An envoy from Switzerland has arrived with a petition.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   REVANCHE: Britain will not forgive France the loss of Ulster and 1 more province. A new design hardens in their court.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 4 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - Ottoman Empire — Open Borders Agreement
   - Portugal — Open Borders Agreement
   - ...and 1 more
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (2 held, unsettled: Munster, Ulster) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+8)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0282  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0282_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2073 of 2073 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,035 (+969 next turn)
   Inf:
   82,350
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0283  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0283_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0284  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0284_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2073 of 2073 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,035 (+969 next turn)
   Inf:
   82,350
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0285  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0285_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0286  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0286_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0287  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0287_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px] ──
   LOAD GAME
   controls: [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0288  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0288_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0289  click replay_sea_camp  ->  ERROR: no visible control's text holds "replay_sea_camp"
view: <run>\frames\0289_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0290  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0290_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0291  click replay_sea_camp  ->  ERROR: no visible control's text holds "replay_sea_camp"
view: <run>\frames\0291_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0292  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0292_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px] ──
   LOAD GAME
   controls: [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0293  click replay_sea_camp  ->  ERROR: no visible control's text holds "replay_sea_camp"
view: <run>\frames\0293_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0294  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0294_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px] ──
   LOAD GAME
   controls: [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0295  click replay_sea_camp  ->  ERROR: no visible control's text holds "replay_sea_camp"
view: <run>\frames\0295_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0296  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0296_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px] ──
   LOAD GAME
   controls: [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0297  look  ->  ok
  (a fresh frame)
view: <run>\frames\0297_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0298  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0298_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0299  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0299_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0300  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0300_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0301  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0301_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0302  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0302_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0303  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0303_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0304  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0304_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0305  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0305_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0306  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0306_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0307  click replay_sea_camp  ->  ERROR: no visible control's text holds "replay_sea_camp"
view: <run>\frames\0307_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0308  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0308_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0309  click replay_sea_camp  ->  ERROR: no visible control's text holds "replay_sea_camp"
view: <run>\frames\0309_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0310  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0310_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px] ──
   LOAD GAME
   controls: [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0311  click replay_sea_camp  ->  ERROR: no visible control's text holds "replay_sea_camp"
view: <run>\frames\0311_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0312  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0312_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px] ──
   LOAD GAME
   controls: [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0313  click replay_sea_camp  ->  ERROR: no visible control's text holds "replay_sea_camp"
view: <run>\frames\0313_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0314  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0314_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px] ──
   LOAD GAME
   controls: [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0315  scroll 1828 500 up 30  ->  ok
  (scrolled up 30 at (1828, 500))
view: <run>\frames\0315_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 528 px] ──
   LOAD GAME
   controls: [Autosave - Turn 17 (Turn 17)]  [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0316  look  ->  ok
  (a fresh frame)
view: <run>\frames\0316_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2073 of 2073 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0317  click replay_sea_camp  ->  ok
  (clicked at (1825, 510))
view: <run>\frames\0317_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:7
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1543 of 1543 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,207 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_sea_camp
   ════════════════════════════════════
   MORNING DISPATCH — Turn 8
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+1,207 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 42% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   < Massena — Milan — 42,000 — Recovers T11. Morale:0%
   ⚠ Morale failing (0) — the men waver. Fell back under fire. Recovering from the rout, 3 turns — drill once he has reformed.
   - Soult — Flanders — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Flanders — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — substantial force [partial]
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
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
   The Emperor's Designs — I The Protector of the Rhine, II The Crowns of Italy, III The Continental System: one proclamation decides what the Empire is for, and it cannot be undone. In the Cabinet: F1 → The Emperor's Designs.
   Berthier: "Your orders, Sire."
   ════════════════════════════════════
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
   • "what if Ney attacks Mack" — free: it names who marches with him before you commit
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1531,531)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  ?(1975,442)  Deroy(1975,405)  ?(1995,275)  Brunswick(1995,238)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1841,343)  ?(1988,600)  Archduke John(1981,563)  Napoleon(1731,419)  Lannes(1793,497)  Murat(1825,471)  Dumonceau(1734,276)  Soult(1648,340)  Bernadotte(1700,250)  Massena(1933,616)  ?(2135,412)  ?(1995,341)  ?(1894,587)  ?(1916,410)  25k(1530,496)  12k(1473,441)  ?(1752,598)  10k(1734,391)  12k(1684,392)  10k(1932,685)
```

```
#0318  click Ledger (T)  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0318_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early January 1806 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); Esc closes it (Alt+T while you type). /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1543 of 1543 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,207 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (56 labels)
```

```
#0319  key 7  ->  ok
  (pressed 7)
view: <run>\frames\0319_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 882 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early January 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire, is staged — no order; a march out resets the count, and Britain's squadrons, held home by the camp, go back to the blockade (trade −50%, crews rot 5 a turn, about −175g a turn) from the turn after next …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Dumonceau, march to Normandy>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1543 of 1543 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (56 labels)
```

```
#0320  click Dumonceau, march to Normandy  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0320_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 860 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early January 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire, is staged — no order; a march out resets the count, and Britain's squadrons, held home by the camp, go back to the blockade (trade −50%, crews rot 5 a turn, about −175g a turn) from the turn after next …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   800 (+1,207 next turn)
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
   ► Dumonceau, march to Normandy
   Dumonceau begins march to Normandy. Route: Flanders → Picardy → Artois → Normandy. Arrives in 4 turns. Moves to Flanders. Dumonceau: "We move deliberately — arrival is worth little if the army arrives broken."
   [2/4 actions remaining]
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1531,531)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  ?(1975,442)  Deroy(1975,405)  ?(1995,275)  Brunswick(1995,238)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1841,343)  ?(1988,600)  Archduke John(1981,563)  Napoleon(1731,419)  Lannes(1793,497)  Murat(1825,471)  Soult(1669,276)  Bernadotte(1684,250)  Dumonceau(1700,224)  Massena(1933,616)  ?(2135,412)  ?(1995,341)  ?(1894,587)  ?(1916,410)  25k(1530,496)  12k(1473,441)  ?(1752,598)  ?(1734,391)  12k(1684,392)  10k(1932,685)
```

```
#0321  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0321_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:7
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1675 of 1675 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   800 (+1,207 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► Dumonceau, march to Normandy
   Dumonceau begins march to Normandy. Route: Flanders → Picardy → Artois → Normandy. Arrives in 4 turns. Moves to Flanders. Dumonceau: "We move deliberately — arrival is worth little if the army arrives broken."
   [2/4 actions remaining]
map: unchanged (56 labels)
```

```
#0322  type Soult, march to Orleanais  ->  ok
  (typed and Enter)
view: <run>\frames\0322_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult begins march to Orleanais. Moves to Orleanais.
Orleanais lies outside the camp — this takes 30,000 men out of it; the 2-turn count resets at the turn's end — Britain's squadrons, held home by the camp, go back to the blockade (trade −50%, crews rot 5 a turn, about −175g a turn) from the turn after next. "Soult, march to Orleanais." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1853 of 1853 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   800 (+1,207 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, march to Orleanais
   Soult begins march to Orleanais. Moves to Orleanais.
   Orleanais lies outside the camp — this takes 30,000 men out of it; the 2-turn count resets at the turn's end — Britain's squadrons, held home by the camp, go back to the blockade (trade −50%, crews rot 5 a turn, about −175g a turn) from the turn after next. "Soult, march to Orleanais." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [1/4 actions remaining]
map: unchanged (56 labels)
```

```
#0323  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0323_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1389 of 1389 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   800 (+1,207 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Massena's corps stands below 40% morale beside Archduke John (~27,500, Tyrol) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (56 labels)
```

```
#0324  click Continue  ->  ERROR: no visible control's text holds "Continue"
view: <run>\frames\0324_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1389 of 1389 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Orleanais lies outside the camp — this takes 30,000 men out of it; the 2-turn count resets at the turn's end — Britain's squadrons, held home by the camp, go back to the blockade (trade −50%, crews rot 5 a turn, about −175g a turn) from the turn after next. "Soult, march to Orleanais." It will be do
   [1/4 actions remaining]
   ⚠ Massena's corps stands below 40% morale beside Archduke John (~27,500, Tyrol) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (56 labels)
```

```
#0325  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0325_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 69 px] ──
   ENEMY PHASE - Turn 8
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 700 casualties, 53,300 remaining /     Massena: 21,226 casualties, 20,774 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) /     Massena forced to retreat! /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Ch …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys (5)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1898 of 1899 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,564 (+1,825 next turn)
   Inf:
   82,125
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   INTELLIGENCE
   Deroy — Franconia — substantial force [partial]
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
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
   The Emperor's Designs — I The Protector of the Rhine, II The Crowns of Italy, III The Continental System: one proclamation decides what the Empire is for, and it cannot be undone. In the Cabinet: F1 → The Emperor's Designs.
   Berthier: "Your orders, Sire."
   ════════════════════════════════════
   Your marshals await your orders, Sire.
   Commands:
   • "Ney, attack Mack"
   • "what if Ney attacks Mack" — free: it names who marches with him before you commit
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► Dumonceau, march to Normandy
   Dumonceau begins march to Normandy. Route: Flanders → Picardy → Artois → Normandy. Arrives in 4 turns. Moves to Flanders. Dumonceau: "We move deliberately — arrival is worth little if the army arrives broken."
   [2/4 actions remaining]
   ► Soult, march to Orleanais
   Soult begins march to Orleanais. Moves to Orleanais.
   Orleanais lies outside the camp — this takes 30,000 men out of it; the 2-turn count resets at the turn's end — Britain's squadrons, held home by the camp, go back to the blockade (trade −50%, crews rot 5 a turn, about −175g a turn) from the turn after next. "Soult, march to Orleanais." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [1/4 actions remaining]
   ⚠ Massena's corps stands below 40% morale beside Archduke John (~27,500, Tyrol) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► end turn
   ═══════════════════════════════════════
   TURN 9 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Materiel: -1061g | Other: +1295g | Upkeep: -1970g | Net: +764g
   Treasury: 1,564g
   Actions refreshed: 4/4
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Supply shortage at Tyrol: Archduke Charles loses 1,686 troops
   Supply shortage at Tyrol: Archduke John loses 633 troops
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-4): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Piedmont. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2079,510)  France(1531,531)  Bavaria(1962,501)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  Massena(1746,649)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1841,343)  ?(1976,600)  Archduke Charles(1972,563)  ?(2004,600)  Archduke John(1962,537)  Napoleon(1731,419)  Lannes(1793,497)  Murat(1825,471)  Soult(1657,425)  Bernadotte(1669,276)  Dumonceau(1700,250)  Teulie(1932,616)  ?(1880,831)  ?(1881,616)  ?(1916,410)  25k(1530,496)  12k(1473,441)  ?(1752,598)  ?(1734,391)  12k(1684,392)  10k(1932,685)
```

```
#0326  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0326_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 20,774
   54,000 → 53,300
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 8
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys (5)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3358,64)]  [icon: A Moment of History: The Bavarian Match @(3400,64)]  [icon: Envoy from Prussia @(3442,64)]  [icon: Envoy from Ottoman Empire @(3484,64)]  [icon: Envoy from Portugal @(3526,64)]  [icon: Soult arrived @(3568,64)]  [+1]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   -21 →
   T:8
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,564 (+1,825 next turn)
   Inf:
   82,125
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   --- Strategic Order Updates ---
   Dumonceau: Dumonceau is marching to Normandy (3 turns remaining).
   Soult: The order was "Soult, march to Orleanais". Soult arrives at Orleanais. I await further instruction.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 9
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
   • Sire — Massena was mauled at Milan: half of his corps — 21,226 men — lost in a single action.
   • Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,564g (+1,825 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 76% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Orleanais — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   < Massena — Piedmont — 20,502 — Recovers T11. Morale:0%
   ⚠ Morale failing (0) — the men waver. Fell back under fire. Recovering from the rout, 2 turns — drill once he has reformed.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Flanders — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   - Teulie — Milan — 7,000 — Awaiting orders.
   > Dumonceau — Flanders — 6,500 — Moving to Normandy — 3 turns out.
   INTELLIGENCE
   Mack — Swabia — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Deroy — Franconia — substantial force [last known - T1]
   Brunswick — Berlin — large force [last known - T1]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Flanders. Holland pays them; their dead will be its grief.
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   Swabia passes from Bavaria to Austria.
   War exhaustion grows — France nears breaking point (exhaustion: 20).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   An envoy from Switzerland has arrived with a petition.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Piedmont. The Kingdom of Italy pays them; their dead will be its grief.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 5 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - The Cabinet — A Moment of History
   - Ottoman Empire — Open Borders Agreement
   - ...and 2 more
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms — theirs to impose (-21)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0327  click End Turn  ->  ERROR: no visible control's text holds "End Turn"
view: <run>\frames\0327_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   16,666
   549
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 20,774
   54,000 → 53,300
   ROUTED
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 8
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0328  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0328_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,564 (+1,825 next turn)
   Inf:
   82,125
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0329  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0329_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1894 of 1894 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,564 (+1,825 next turn)
   Inf:
   82,125
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]  [Open Envoys (5)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ You have 4 unanswered envoys that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: Switzerland — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
map: unchanged (54 labels)
```

```
#0330  click End Turn  ->  ok
  (clicked at (817, 978))
view: <run>\frames\0330_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 685 px] ──
   ENEMY PHASE - Turn 9
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Teulie /     Second Battle of Milan /     Archduke Charles: 789 casualties, 50,825 remaining /     Teulie: 5,043 casualties, 1,957 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) /     Teulie forced to retreat! /     ⚔ View the field /     --- Berthier's Report --- /     Attack: Archduke Charles (Fo …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1742 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,794 (+1,601 next turn)
   Inf:
   84,025
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   < Massena — Piedmont — 20,502 — Recovers T11. Morale:0%
   ⚠ Morale failing (0) — the men waver. Fell back under fire. Recovering from the rout, 2 turns — drill once he has reformed.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Flanders — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   - Teulie — Milan — 7,000 — Awaiting orders.
   > Dumonceau — Flanders — 6,500 — Moving to Normandy — 3 turns out.
   INTELLIGENCE
   Mack — Swabia — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Deroy — Franconia — substantial force [last known - T1]
   Brunswick — Berlin — large force [last known - T1]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Flanders. Holland pays them; their dead will be its grief.
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   Swabia passes from Bavaria to Austria.
   War exhaustion grows — France nears breaking point (exhaustion: 20).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   An envoy from Switzerland has arrived with a petition.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Piedmont. The Kingdom of Italy pays them; their dead will be its grief.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 5 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - The Cabinet — A Moment of History
   - Ottoman Empire — Open Borders Agreement
   - ...and 2 more
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms — theirs to impose (-21)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   ⚠ You have 4 unanswered envoys that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: Switzerland — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2575g | Admiralty: -90g | Blockade: -219g | Materiel: -450g | Other: +1256g | Upkeep: -1842g | Net: +1230g
   Treasury: 2,794g
   Actions refreshed: 4/4
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Bavaria completes a market at Franconia.
   Supply shortage at Franconia: Archduke Charles loses 120 troops
   Holland loyalty 96 (-2): satellite drift, the lord's defeats
   Kingdom of Italy loyalty 86 (-12): the contingent's dead, satellite drift
   Switzerland's petition for relief went unanswered and lapses as a refusal: loyalty −10 (96 → 86); bond 0 → -20 (-1 a turn). Nothing is charged.
   Switzerland loyalty 81 (-15): refused petition, satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2079,510)  France(1531,531)  Bavaria(1962,501)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  Archduke Charles(1975,439)  Massena(1746,649)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1841,343)  ?(1981,600)  Archduke John(1981,563)  Napoleon(1731,419)  Lannes(1793,497)  Murat(1825,471)  ?(1900,560)  Deroy(1921,533)  Soult(1657,425)  Bernadotte(1684,276)  Dumonceau(1652,390)  Teulie(1932,616)  ?(1880,831)  ?(1881,616)  ?(1916,410)  25k(1530,496)  12k(1473,441)  ?(1752,598)  ?(1734,391)  12k(1650,361)  10k(1932,685)
```

```
#0331  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0331_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   TEULIE REPORTS
   "Teulie is cornered at Milan with 1,957 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Teulie is cornered @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: A Moment of History: The Bavarian Match @(3442,64)]  [icon: Envoy from Denmark @(3484,64)]  [icon: Envoy from Saxony @(3526,64)]  [icon: Soult arrived @(3568,64)]  [+1]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   -25 →
   T:9
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1983 of 1983 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,794 (+1,601 next turn)
   Inf:
   84,025
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Switzerland's petition for relief went unanswered and lapses as a refusal: loyalty −10 (96 → 86); bond 0 → -20 (-1 a turn). Nothing is charged.
   Switzerland loyalty 81 (-15): refused petition, satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   --- Strategic Order Updates ---
   Dumonceau: Dumonceau marches to Picardy. 2 regions to Normandy.
   Teulie: Teulie is cornered at Milan with 1,957 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Teulie was mauled at Milan: half of his corps — 5,043 men — lost in a single action.
   • Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 2,794g (+1,680 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 75% of French forces (an estimate — 2 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 90 (Strong)
   MARSHAL STATUS
   - Soult — Orleanais — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 21,184 — Awaiting orders.
   < Massena — Piedmont — 20,502 — Recovers T11. Morale:0%
   ⚠ Morale failing (0) — the men waver. Fell back under fire. Recovering from the rout, 1 turn — drill once he has reformed.
   - Bernadotte — Flanders — 17,000 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 15,771 — Awaiting orders.
   - Napoleon — Lorraine — 9,072 — Awaiting orders.
   > Dumonceau — Picardy — 6,500 — Moving to Normandy — 2 turns out.
   ? Teulie — Milan — 1,957 — ENCIRCLED at Milan by Archduke John — awaiting your word. Morale:20%
   ⚠ Morale failing (20) — the men waver. Drill is closed: Archduke John is at Tyrol, one region away.
   INTELLIGENCE
   Archduke Charles — Franconia — 46,738 [confirmed]
   Deroy — Munich — substantial force [partial]
   Mack — Swabia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [last known - T1]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   DIPLOMATIC EVENTS
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot. The Descent camp (Flanders, Artois, Normandy, Brittany) was broken, and Britain's squadrons, no longer held home to guard against it, are back on the blockade.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   LAPSED ENVOYS
   Prussia's Open Borders Agreement offer lapsed unanswered
   Ottoman Empire's Gift of Friendship offer lapsed unanswered
   Portugal's Gift of Friendship offer lapsed unanswered
   Switzerland's petition for relief went unanswered and lapses as a refusal: loyalty −10 (96 → 86); bond 0 → -20 (-1 a turn). Nothing is charged.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - The Cabinet — A Moment of History
   - Denmark — Non-Aggression Pact
   - Saxony — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms — theirs to impose (-25)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 66/100 [Formed] — down 2 since yesterday (Natural threat decay -6, The weight of the hegemon +2)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
   Teulie awaits your orders!
map: unchanged (55 labels)
```

```
#0332  key R  ->  ok
  (pressed R)
view: <run>\frames\0332_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1983 of 1983 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
   Teulie awaits your orders!
map: unchanged (55 labels)
```

```
#0333  click Attempt a breakout  ->  ok
  (clicked at (1971, 584))
view: <run>\frames\0333_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Napoleon
   10,000 → 9,072
   Murat
   22,000 → 21,184
   ⚔
   Lannes ◆
   Mack ◆
   18,000 → 15,771
   52,000 → 46,741
   marched to the guns
   THE GREAT BATTLE OF FRANCHE-COMTE
   click anywhere to skip ▸
   FRANCHE-COMTE · TURN 9
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3403,62)]  [icon: A Moment of History: The Bavarian Match @(3445,62)]  [icon: Envoy from Denmark @(3487,62)]  [icon: Envoy from Saxony @(3529,62)]  [icon: Soult arrived @(3571,62)]  [icon: The Moniteur is out @(3613,62)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,794 (+1,601 next turn)
   Inf:
   84,025
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2079,510)  France(1531,531)  Bavaria(1962,501)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  Archduke Charles(1975,439)  Massena(1730,649)  Teulie(1762,623)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1841,343)  ?(1981,600)  Archduke John(1981,563)  Napoleon(1731,419)  Lannes(1793,497)  Murat(1825,471)  ?(1900,560)  Deroy(1921,533)  Soult(1657,425)  Bernadotte(1684,276)  Dumonceau(1652,390)  ?(1880,831)  ?(1921,616)  ?(1916,410)  25k(1530,496)  12k(1473,441)  ?(1710,598)  ?(1734,391)  12k(1650,361)  10k(1932,685)
```

```
#0334  click Dispatch (R)  ->  ERROR: no visible control's text holds "Dispatch (R)"
view: <run>\frames\0334_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   2,798
   3,704
   Napoleon
   10,000 → 9,072
   Murat
   22,000 → 21,184
   ⚔
   Lannes ◆
   Mack ◆
   18,000 → 15,771
   52,000 → 46,741
   marched to the guns
   THE GREAT BATTLE OF FRANCHE-COMTE
   click anywhere to skip ▸
   FRANCHE-COMTE · TURN 9
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0335  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0335_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   The Cabinet
   Moment
   Turn 9
   A Moment of History: The Bavarian Match
   A moment of history is answered in full — open the letter to choose.
   THE SMALL COURTS WRITE (2)
   Denmark and Saxony write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Denmark
   Proposal
   Turn 9
   Incoming proposal: Non-Aggression Pact
   Bernstorff, watchful and correct: "My master's design is known to all Europe; Denmark sends this offer in its pursuit. Sign the pact of non-aggression."
   Terms: Proposal: Non-Aggression Pact
   or click the letter to reply in full
   WAITING
   Saxony
   Proposal
   Turn 9
   Incoming proposal: Open Borders Agreement
   Einsiedel, anxiously: "His Majesty asks most respectfully for assurance — Europe has grown loud, and Saxony is small. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces — but not a province she has declared guarded (Armed Neutrality): a column there still offends her (−25); up to +100 gold a turn in trade · Saxony pays you 82 gold at the signing
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0336  click Dispatch (R)  ->  ERROR: no visible control's text holds "Dispatch (R)"
view: <run>\frames\0336_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0337  click Close  ->  ok
  (clicked at (1829, 830))
view: <run>\frames\0337_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,794 (+1,601 next turn)
   Inf:
   84,025
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0338  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0338_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,794 (+1,601 next turn)
   Inf:
   84,025
   Cav:
   18,500
   Art:
   11,200
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0339  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0339_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0340  look  ->  ok
  (a fresh frame)
view: <run>\frames\0340_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0341  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0341_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 528 px] ──
   LOAD GAME
   controls: [Autosave - Turn 10 (Turn 10)]  [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0342  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0342_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0343  click replay_sea_landing  ->  ERROR: no visible control's text holds "replay_sea_landing"
view: <run>\frames\0343_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0344  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0344_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0345  click replay_sea_landing  ->  ERROR: no visible control's text holds "replay_sea_landing"
view: <run>\frames\0345_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0346  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0346_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px] ──
   LOAD GAME
   controls: [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0347  click replay_sea_landing  ->  ERROR: no visible control's text holds "replay_sea_landing"
view: <run>\frames\0347_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0348  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0348_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px] ──
   LOAD GAME
   controls: [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0349  click replay_sea_landing  ->  ERROR: no visible control's text holds "replay_sea_landing"
view: <run>\frames\0349_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0350  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0350_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 64 of 528 px] ──
   LOAD GAME
   controls: [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0351  scroll 1828 500 up 30  ->  ok
  (scrolled up 30 at (1828, 500))
view: <run>\frames\0351_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 528 px] ──
   LOAD GAME
   controls: [Autosave - Turn 10 (Turn 10)]  [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (19 lost to the march)
map: unchanged (55 labels)
```

```
#0352  click replay_sea_landing  ->  ok
  (clicked at (1825, 462))
view: <run>\frames\0352_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:9
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,308 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_sea_landing
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+1,308 by the accounts)
   The courts at war hold 27 regions. Estimated enemy strength: 88% of French forces (an estimate — 4 of 4 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Davout — Moravia — 14,000 — Awaiting orders.
   - Ney — Moravia — 13,000 — Awaiting orders.
   - Lannes — Moravia — 12,500 — Awaiting orders.
   - Murat — Dresden — 11,000 — Awaiting orders.
   - Napoleon — Moravia — 10,000 — Awaiting orders.
   - Dumonceau — Normandy — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Kutuzov — Podolia — substantial force [partial]
   Moore — London — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Hohenlohe — Silesia — substantial force [partial]
   Vienna garrison — Vienna — garrison — substantial force [partial]
   London garrison — London — garrison — substantial force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Kutuzov
   • Davout, march to Ukraine
   • recruit infantry in Lorraine — 690g for 3,000 men under Soult
   • build supply depot in Lorraine — 300g
   Ask 'what if Ney attacks Kutuzov' first — it names who marches with Ney, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2187,540)  France(1531,531)  Bavaria(2032,503)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  ?(2301,288)  Hohenlohe(2300,250)  Murat(2135,340)  Bernadotte(1959,439)  Deroy(1990,413)  ?(2371,372)  Kutuzov(2370,335)  ?(1995,275)  Brunswick(1995,238)  Ney +3(2296,465)  ?(1868,459)  Mack(1868,421)  ?(1988,600)  Archduke John(1981,563)  Soult(1731,419)  Dumonceau(1473,372)  ?(1395,328)  Moore(1395,295)  Massena(1933,616)  10k(2134,412)  ?(2187,575)  ?(1995,341)  ?(1894,587)  ?(1916,410)  25k(1530,496)  12k(1473,441)  ?(1752,598)  12k(1684,392)  ?(1395,394)  10k(1932,685)
```

```
#0353  click Ledger (T)  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0353_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 728 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early February 1806 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); Esc closes it (Alt+T while you type). /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Statu …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,308 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (59 labels)
```

```
#0354  key 7  ->  ok
  (pressed 7)
view: <run>\frames\0354_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 1212 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early February 1806 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire: 40,000 men on the Channel coast, 2 turns at war with Britain, stage a descent — no order; a march out resets the count. Her blockade on you lifts; a won Diversion can open the Strait for up to 2 turns …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Land Dumonceau in East Anglia>  <Land Dumonceau in Cornwall>  <Land Dumonceau in Midlands>  <Land Dumonceau in Wales>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1631 of 1631 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (59 labels)
```

```
#0355  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0355_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:9
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1631 of 1631 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (59 labels)
```

```
#0356  type recruit infantry in Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0356_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Berthier checks the order of battle. 'No marshal of infantry can reach Normandy, Sire — none of our own corps stands within reach.' Dumonceau commands our foot here, but Holland pays its men — recruit into one of our own corps. Soult commands our foot at Lorraine — march him within reach, or give him the order yourself: 'Soult, recruit infantry'. Nothing was spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1763 of 1763 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,308 next turn)
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
   ► recruit infantry in Normandy
   Berthier checks the order of battle. 'No marshal of infantry can reach Normandy, Sire — none of our own corps stands within reach.' Dumonceau commands our foot here, but Holland pays its men — recruit into one of our own corps. Soult commands our foot at Lorraine — march him within reach, or give him the order yourself: 'Soult, recruit infantry'. Nothing was spent.
map: unchanged (59 labels)
```

```
#0357  type Dumonceau, recruit infantry  ->  ok
  (typed and Enter)
view: <run>\frames\0357_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Dumonceau's men belong to Holland, Sire — it raises and pays them. Recruit into one of our own corps.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1853 of 1853 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,308 next turn)
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
   ► Dumonceau, recruit infantry
   Dumonceau's men belong to Holland, Sire — it raises and pays them. Recruit into one of our own corps.
map: unchanged (59 labels)
```

```
#0358  type Dumonceau, land at Ulster  ->  ok
  (typed and Enter)
view: <run>\frames\0358_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
reply: ok The expedition is drawn up, Sire: Dumonceau with 6,500 men, Normandy to Ulster. The transports slip past unseen 75 times in 100 (Britain watches at 100 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. If she is intercepted she meets Britain's 110 effective against our 54 — a decisive defeat is the likely result: about half of every pooled fleet (France 45→~20, Spain 30→~14, Holland 12→~5) is lost; Britain's side loses ~4%. What moves the odds: a won diversion first (45 in 100) → 95 · a 5,000-man corps → 78. If it lands: Ulster is half of the Ireland carve (with Munster) — hold both while the war with Britain runs and Britain can be made to erect it at a table; what waits ashore is unscouted. Sailing costs 2 AP. Sail? (yes / no)
── ClarificationPopup (layer 102) ──
   DUMONCEAU ASKS:
   "The expedition is drawn up, Sire: Dumonceau with 6,500 men, Normandy to Ulster. The transports slip past unseen 75 times in 100 (Britain watches at 100 effective against our escort). A failed run costs ~30% of the corps if intercepted, ~5% turned back — and the fleet's readiness −10 if she is turned back. If she is intercepted she meets Britain's 110 effective against our 54 — a decisive defeat i …
   controls: [Sail for Ulster]  [Stand down]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,308 next turn)
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
   ► Dumonceau, land at Ulster
   Dumonceau requests clarification...
map: unchanged (59 labels)
```

```
#0359  click Stand down  ->  ok
  (clicked at (1829, 687))
view: <run>\frames\0359_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:9
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1986 of 1986 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,308 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (59 labels)
```

```
#0360  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0360_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1986 of 1986 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,308 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Dumonceau, land at Ulster
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (59 labels)
```

```
#0361  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0361_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1986 of 1986 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Dumonceau, land at Ulster
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (59 labels)
```

```
#0362  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0362_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1986 of 1986 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Dumonceau, land at Ulster
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (59 labels)
```

```
#0363  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0363_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 528 px] ──
   LOAD GAME
   controls: [Autosave - Turn 10 (Turn 10)]  [replay_sea_landing (Turn 10)]  [replay_sea_camp (Turn 8)]  [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1986 of 1986 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Dumonceau, land at Ulster
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (59 labels)
```

```
#0364  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0364_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1986 of 1986 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Dumonceau, land at Ulster
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (59 labels)
```

```
#0365  click replay_truce_offer  ->  ERROR: no visible control's text holds "replay_truce_offer"
view: <run>\frames\0365_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1986 of 1986 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Dumonceau, land at Ulster
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (59 labels)
```

```
#0366  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0366_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1986 of 1986 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Dumonceau, land at Ulster
   Dumonceau requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (59 labels)
```

```
#0367  click replay_truce_offer  ->  ok
  (clicked at (1825, 434))
view: <run>\frames\0367_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_truce_offer
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+228 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 44% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 26,000 — Awaiting orders.
   - Ney — Swabia — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Bernadotte, attack Mack
   • Ney, march to Franconia
   • build supply depot in Lorraine — 300g
   • build fortification in Lorraine — 400g
   Ask 'what if Bernadotte attacks Mack' first — it names who marches with Bernadotte, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1531,531)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  Bernadotte(1959,439)  Deroy(1990,413)  ?(1995,275)  Brunswick(1995,238)  Ney(1852,456)  Davout(1883,413)  ?(1971,590)  Mack(1971,563)  ?(2000,600)  Archduke John(1990,537)  Soult(1716,419)  Napoleon(1747,393)  Lannes(1793,497)  Murat(1803,471)  Massena(1933,616)  ?(2135,412)  ?(1995,341)  ?(1921,587)  ?(1910,341)  25k(1530,496)  12k(1473,441)  ?(1752,598)  12k(1678,392)  10k(1932,685)
```

```
#0368  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0368_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0369  scroll 1828 550 down 3  ->  ok
  (scrolled down 3 at (1828, 550))
view: <run>\frames\0369_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 150 of 733 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0370  click Austria  ->  ok
  (clicked at (1825, 557))
view: <run>\frames\0370_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 435 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — a level ledger still signs: Propose Armistice at 51 of 50. It costs 1 DP. A truce keeps the ledger (+0 stands, the war 2 turns old) an …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,236)]  [Propose Armistice (1 DP)  —  Favorable]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Open Settlement with Austria alone  —  opens with 575 gold to Austria staged — the sum that carries her]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Doubtful]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0371  click Propose Armistice  ->  ok
  (clicked at (1825, 427))
view: <run>\frames\0371_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 662 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 2 turns old and stays so; exhaustion holds. No territory or gold changes hands until it ends …
   ▼ more below
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms](disabled: A truce settles nothing: no province or gold changes hands until it ends. Demands are pres)  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1566 of 1566 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
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
   ► propose armistice with Austria
map: unchanged (53 labels)
```

```
#0372  click Send as suggested  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0372_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/5
   Threat 70 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Dispatched @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+228 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (53 labels)
```

```
#0373  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0373_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 400 px] ──
   ENEMY PHASE - Turn 3
   AUSTRIA / ──────────────────────────── / - Mack attacks Massena /     The Great Battle of Milan /     Mack: 6,017 casualties, 45,983 remaining /     Massena: 5,411 casualties, 36,589 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Mack: "You see? The position was sound. It is always s …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   702 (+458 next turn)
   Inf:
   82,250
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -556g | Other: +1251g | Upkeep: -3074g | Net: -98g
   Treasury: 702g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Mack loses 2,299 troops
   Supply shortage at Tyrol: Archduke Charles loses 2,495 troops
   Supply shortage at Tyrol: Archduke John loses 1,000 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Lorraine. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was deep-seated hostility.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1531,531)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1357,263)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  Bernadotte(1959,439)  Deroy(1990,413)  ?(1995,275)  Brunswick(1995,238)  Ney(1852,456)  Davout(1883,413)  ?(1981,617)  Mack(1962,563)  ?(1992,590)  Archduke Charles(1981,537)  ?(2020,600)  Archduke John(2000,467)  Soult(1716,419)  Napoleon(1747,393)  Lannes(1793,497)  Murat(1803,471)  Dumonceau(1734,276)  Massena(1917,616)  Teulie(1948,590)  ?(2135,412)  ?(1995,341)  ?(1896,587)  ?(1910,341)  25k(1530,496)  12k(1473,441)  ?(1752,598)  10k(1764,422)  12k(1678,392)  10k(1932,685)
```

```
#0374  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0374_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Mack ◆
   42,000 → 36,589
   52,000 → 45,983
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 3
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Envoy from Prussia @(3487,62)]  [icon: Envoy from Ottoman Empire @(3529,62)]  [icon: Envoy from Portugal @(3571,62)]  [icon: Armistice Rejected @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   702 (+458 next turn)
   Inf:
   82,250
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet — shut](disabled: The Cabinet (F1) — Prussia's letter stands unanswered — the Cabinet stays shut until it is)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -556g | Other: +1251g | Upkeep: -3074g | Net: -98g
   Treasury: 702g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Mack loses 2,299 troops
   Supply shortage at Tyrol: Archduke Charles loses 2,495 troops
   Supply shortage at Tyrol: Archduke John loses 1,000 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Lorraine. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was deep-seated hostility.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 702g (+458 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 72% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 30,854 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 26,000 — Awaiting orders.
   - Ney — Swabia — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Tyrol — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Austria.
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Napoleon at Lorraine. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria with a response.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0375  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0375_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1962 of 1962 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   702 (+458 next turn)
   Inf:
   82,250
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0376  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0376_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1962 of 1962 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   702 (+458 next turn)
   Inf:
   82,250
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet — shut]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0377  click Load Game  ->  ERROR: no visible control's text holds "Load Game"
view: <run>\frames\0377_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0378  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0378_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0379  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0379_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0380  scroll 1828 500 down 30  ->  ok
  (scrolled down 30 at (1828, 500))
view: <run>\frames\0380_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px] ──
   LOAD GAME
   controls: [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [replay_liberation (Turn 3)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0381  click replay_table  ->  ERROR: no visible control's text holds "replay_table"
view: <run>\frames\0381_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 528 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0382  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0382_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px] ──
   LOAD GAME
   controls: [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [replay_petition (Turn 4)]  [replay_support (Turn 9)]  [replay_aggressive (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0383  click replay_table  ->  ERROR: no visible control's text holds "replay_table"
view: <run>\frames\0383_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 412 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0384  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0384_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px] ──
   LOAD GAME
   controls: [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [replay_truce_offer (Turn 3)]  [replay_envoys (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0385  click replay_table  ->  ERROR: no visible control's text holds "replay_table"
view: <run>\frames\0385_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 296 of 528 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0386  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0386_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 180 of 528 px] ──
   LOAD GAME
   controls: [replay_opening (Turn 1)]  [replay_table (Turn 16)]  [replay_guarded (Turn 12)]  [replay_design_peace (Turn 7)]  [replay_truce_mission (Turn 6)]  [replay_counter (Turn 5)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed] — down 2 since yesterday (Natural threat decay -3, The weight of the hegemon +1)
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys a design's sleep, Sire, not a court's goodwill — a court bought off still counts toward the league while its relations stand under −10."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0387  click replay_table  ->  ok
  (clicked at (1825, 426))
view: <run>\frames\0387_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +10 ↑
   T:15
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_table
   ════════════════════════════════════
   MORNING DISPATCH — Turn 16
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 30 regions. Treasury: 6,241g (+969 by the accounts)
   The courts at war hold 26 regions. Estimated enemy strength: 44% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
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
   War Purpose: Defense vs Britain (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+26)
   War Purpose: Defense vs Austria (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Munster) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Mack
   • Davout, march to Lorraine
   • recruit infantry in Rhineland — 714g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Our doctrine: The Corps System — The corps march apart and fight together - and eat what the country gives them. The Generals screen (press G, or Alt+G while you type) shows its strength and its flaw.
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
   • Generals: press G (Alt+G while you type) to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map names: Russia(2650,157)  Ottoman Empire(2413,807)  Prussia(2179,257)  Spain(1124,908)  Sweden(1913,-21)  Saxony(2135,377)  Austria(2148,597)  France(1500,504)  Bavaria(1931,499)  Kingdom of Italy(1760,685)  Denmark(1730,24)  Papal States(1880,795)  Britain(1333,231)  Hanover(1716,308)  Naples(1801,933)  Sardinia(1625,820)  Hesse(1911,375)  Holland(1730,358)  Switzerland(1752,563)
map pieces: 100(1275,367)  45(1247,620)  30(1301,804)  20(2010,68)  18(1977,12)  15(2347,675)  12(1526,238)  10(910,825)  10(1954,168)  5(1797,864)  Bernadotte(1959,439)  Deroy(1990,413)  ?(1995,275)  Brunswick(1995,238)  ?(1868,459)  Mack(1868,421)  Ney(1811,369)  Davout(1841,343)  ?(1988,600)  Archduke John(1981,563)  Soult(1716,419)  Napoleon(1747,393)  Lannes(1793,497)  Murat(1825,471)  Massena(1933,616)  ?(2135,412)  ?(1995,341)  ?(1894,587)  ?(1916,410)  25k(1530,470)  12k(1473,441)  ?(1752,598)  12k(1678,392)  10k(1932,685)
```

```
#0388  click War for Munster  ->  ok
  (clicked at (3429, 996))
view: <run>\frames\0388_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) [scrolled 0 of 398 px] ──
   WAR FOR MUNSTER
   BR
   +10
   FR
   The ledger of one war — its score, its fronts, and the price of peace. Negotiate opens the table, where every court signs for itself. /  / The War for Munster: France holds Munster and Ulster of Britain's. / With: Britain + Austria + Russia /  / Settlement Tier: White Peace / A peace signed now is on the held line: Munster and Ulster stay ours by the treaty — and closes the Ireland carve — erect i …
   controls: [icon @(3139,189)]  [Negotiate with Britain]  [Negotiate with Austria]  [Negotiate with Russia]  [Open Settlement]  [Request Terms](disabled: Britain leads a league that is not yet spent, Sire — it names no terms while it can still )
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever the line is empty and you are not typing — Alt+key while you type
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0389  click Open Settlement  ->  ok
  (clicked at (2771, 872))
view: <run>\frames\0389_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 135 px, 0 of 574 px] ──
   This draft will not carry as it stands. / the War for Munster — the table with Austria + Britain + Russia - Whole-war settlement / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria -18/50, Britain 26/50, Russia -18/50. / Treasury 6,241 gold: committed 1,000 / reserve 500 / remaining 4,741 / Sire, this settlement of the War for M …
   The table /   * Austria ▸ - Holding out (-18/50) White peace /       Blocker: War objective alignment /       Metternich regrets that Austria must remain… unconvinced — the terms would end the war without the object it was fought for. /       + Add demand /   * Britain ▸ - Holding out (26/50) Demanded: Ireland carved out; Conceded: 1000g /       Blocker: Term harshness /       Castlereagh declines …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War for Munster — the table with Austria + Britain + Russia cannot be ratified now: the terms weigh heavier than their defeat. Revise terms or stand down b …
   controls: <Austria ▸>  <+ Add demand>  <Britain ▸>  [icon: - Britain · Conceded · France pays 1000 gold (yours) up to 1,0 @(1559,460)]  [icon: + Britain · Conceded · France pays 1000 gold (yours) up to 1,0 @(1577,460)]  <Remove>  <Remove>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Drop Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  <Grant>  <Decline>  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
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
   Opening settlement review for Britain
map: unchanged (53 labels)
```

```
#0390  click Back Out  ->  ok
  (clicked at (2250, 969))
view: <run>\frames\0390_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Munster
   +10 ↑
   T:15
   controls: [THIRD COALITION  ▸]  [War for Munster]
── BottomLeftUI (layer 0) [scrolled 1587 of 1587 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept until the turn ends — reopen Settlement this turn to continue.
map: unchanged (53 labels)
```

```
#0391  click War for Munster  ->  ok
  (clicked at (3429, 996))
view: <run>\frames\0391_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) [scrolled 0 of 398 px] ──
   WAR FOR MUNSTER
   BR
   +10
   FR
   The ledger of one war — its score, its fronts, and the price of peace. Negotiate opens the table, where every court signs for itself. /  / The War for Munster: France holds Munster and Ulster of Britain's. / With: Britain + Austria + Russia /  / Settlement Tier: White Peace / A peace signed now is on the held line: Munster and Ulster stay ours by the treaty — and closes the Ireland carve — erect i …
   controls: [icon @(3139,189)]  [Negotiate with Britain]  [Negotiate with Austria]  [Negotiate with Russia]  [Open Settlement]  [Request Terms](disabled: Britain leads a league that is not yet spent, Sire — it names no terms while it can still )
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1587 of 1587 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,241 (+969 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Opening settlement review for Britain
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept until the turn ends — reopen Settlement this turn to continue.
map: unchanged (53 labels)
```

```
#0392  quit  ->  ok
  (the engine quits)
view: <run>\frames\0392_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) [scrolled 0 of 398 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1587 of 1587 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Opening settlement review for Britain
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept until the turn ends — reopen Settlement this turn to continue.
map: unchanged (53 labels)
```

