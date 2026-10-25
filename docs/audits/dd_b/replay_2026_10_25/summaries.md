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
   controls: [Begin the 1805 Campaign]  [The School of War — a guided campaign]  [The School of War — The Table (a guided peace)]  [Continue  ·  Late June 1806]  [Load a Campaign…]  [Settings]  [Quit to Desktop]
```

```
#0001  click Looks right  ->  ok
  (clicked at (1960, 669))
view: <run>\frames\0001_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=[], region_panel=no, other=['main_menu']
── TitleBlock (layer 0): unchanged
── StatusLine (layer 0): unchanged
── PaintingCaption (layer 0) ──
   Jacques-Louis David — Bonaparte Crossing the Alps  ·  public domain
── VersionLine (layer 0): unchanged
── MenuColumn (layer 0): unchanged
```

```
#0002  click Begin the 1805 Campaign  ->  ok
  (clicked at (490, 439))
view: <run>\frames\0002_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=[], region_panel=no, other=['main_menu']
── TitleBlock (layer 0): unchanged
── MenuColumn (layer 0) ──
   Begin anew? The autosave of your running campaign is replaced.
   controls: [Begin the 1805 Campaign]  [Confirm — begin anew]  [Keep my campaign]  [The School of War — a guided campaign]  [The School of War — The Table (a guided peace)]  [Continue  ·  Late June 1806]  [Load a Campaign…]  [Settings]  [Quit to Desktop]
── StatusLine (layer 0): unchanged
── PaintingCaption (layer 0): unchanged
── VersionLine (layer 0): unchanged
```

```
#0003  click Confirm — begin anew  ->  ok
  (clicked at (378, 530))
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
#0004  type what if Ney attacks Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0004_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  What Swabia can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1543 of 1543 px] ──
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
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
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
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0005  type what if Massena attacks Archduke John  ->  ok
  (typed and Enter)
view: <run>\frames\0005_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
  The band weighs a force of his you have not scouted within reach of Tyrol — scout the provinces round it.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.

Nothing has been ordered, and nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1853 of 1853 px] ──
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
   The band weighs a force of his you have not scouted within reach of Tyrol — scout the provinces round it.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0006  type how do I get to Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Yes, Sire — Bernadotte can reach Vienna from Franconia in 2 turns: Franconia -> Bohemia -> Vienna. The order is 'Bernadotte, march to Vienna'.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2470 of 2470 px] ──
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
   ► how do I get to Vienna
   Yes, Sire — Bernadotte can reach Vienna from Franconia in 2 turns: Franconia -> Bohemia -> Vienna. The order is 'Bernadotte, march to Vienna'.
map: unchanged (53 labels)
```

```
#0007  type Murat, march to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['interrupt'], region_panel=no
reply: ok Murat: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' Berthier adds: Ney, Davout, Lannes and Napoleon would answer the guns — Murat 22,000, 80,665 with the muster committed, against Mack (large force) — weighed together, the balance of force looks favorable.
── InterruptPopup (layer 103) ──
   MURAT REPORTS
   "Murat: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' Berthier adds: Ney, Davout, Lannes and Napoleon would answer the guns — Murat 22,000, 80,665 with the muster committed, against Mack (large force) — weighed together, the balance of force looks favorable."
   controls: [Commit the Attack]  [Go Around]  [Hold Position]  [Cancel Order]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2536 of 2536 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Murat, march to Swabia
   Murat awaits your orders!
map: unchanged (53 labels)
```

```
#0008  click Go Around  ->  ok
  (clicked at (1768, 584))
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2625 of 2625 px] ──
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
   > Murat: go around
   Murat reroutes around Swabia. Murat: 'Enemy forces discovered at Swabia! Destination held by Mack. Odds unfavorable — awaiting orders.' Berthier adds: Ney, Davout, Lannes and Napoleon would answer the guns — Murat 22,000, 80,665 with the muster committed, against Mack (large force) — weighed together, the balance of force looks favorable.
map: unchanged (53 labels)
```

```
#0009  type Murat, march to Flanders  ->  ok
  (typed and Enter)
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat begins march to Flanders. Route: Orleanais → Flanders. Cavalry charges through Lorraine -> Orleanais. Murat: "We march. Pity whatever slows us."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2736 of 2736 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   1/4
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
   ► Murat, march to Flanders
   Murat begins march to Flanders. Route: Orleanais → Flanders. Cavalry charges through Lorraine -> Orleanais. Murat: "We march. Pity whatever slows us."
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1859,469)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1813,497)  Murat(1687,440)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1684,411)  10k(1910,645)
```

```
#0010  type Murat, cancel  ->  ok
  (typed and Enter)
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat halts his march and awaits new orders.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2846 of 2846 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   ► Murat, cancel
   Murat halts his march and awaits new orders.
   [0/4 actions remaining]
map: unchanged (54 labels)
```

```
#0011  type lay down two ships  ->  ok
  (typed and Enter)
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3001 of 3001 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   ► lay down two ships
   Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1859,469)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1813,497)  Murat(1687,440)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1684,411)  10k(1910,645)
```

```
#0012  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► lay down two ships
   Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the
   [0/4 actions remaining]
map: unchanged (54 labels)
```

```
#0013  click Britain  ->  ERROR: no visible control's text holds "Britain"
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► lay down two ships
   Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the
   [0/4 actions remaining]
map: unchanged (54 labels)
```

```
#0014  scroll 1830 600 down 10  ->  ok
  (scrolled down 10 at (1830, 600))
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 376 of 816 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   Neutral (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► lay down two ships
   Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the
   [0/4 actions remaining]
map: unchanged (54 labels)
```

```
#0015  scroll 1830 600 up 3  ->  ok
  (scrolled up 3 at (1830, 600))
view: <run>\frames\0015_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 231 of 814 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► lay down two ships
   Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the
   [0/4 actions remaining]
map: unchanged (54 labels)
```

```
#0016  click Britain  ->  ok
  (clicked at (1825, 444))
view: <run>\frames\0016_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 267 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War with the Third Coalition   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — the court sees no reason to sign at +0: Propose Peace stands at -7 of 50; it wants her loyalty to the league — she has no reason of he …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Hopeless]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3001 of 3001 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► lay down two ships
   Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the
   [0/4 actions remaining]
map: unchanged (54 labels)
```

```
#0017  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0017_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 596 px] ──
   ARMISTICE PREVIEW - Britain /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Britain /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 0 turns old and stays so; exhaustion holds. No territory or gold changes hands until it ends …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms](disabled: A truce settles nothing: no province or gold changes hands until it ends. Demands are pres)  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2517 of 2517 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
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
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
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
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
   ► what if Massena attacks Archduke John
   Were you to give the order, Sire:
   MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
   The band weighs a force of his you have not scouted within reach of Tyrol — scout the provinces round it.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► how do I get to Vienna
   Yes, Sire — Bernadotte can reach Vienna from Franconia in 2 turns: Franconia -> Bohemia -> Vienna. The order is 'Bernadotte, march to Vienna'.
   ► Murat, march to Swabia
   Murat awaits your orders!
   > Murat: go around
   Murat reroutes around Swabia. Murat: 'Enemy forces discovered at Swabia! Destination held by Mack. Odds unfavorable — awaiting orders.' Berthier adds: Ney, Davout, Lannes and Napoleon would answer the guns — Murat 22,000, 80,665 with the muster committed, against Mack (large force) — weighed together, the balance of force looks favorable.
   ► Murat, march to Flanders
   Murat begins march to Flanders. Route: Orleanais → Flanders. Cavalry charges through Lorraine -> Orleanais. Murat: "We march. Pity whatever slows us."
   [1/4 actions remaining]
   ► Murat, cancel
   Murat halts his march and awaits new orders.
   [0/4 actions remaining]
   ► lay down two ships
   Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
   [0/4 actions remaining]
   ► propose armistice with Britain
map: unchanged (54 labels)
```

```
#0018  click Not Now  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2583 of 2583 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0019  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0019_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2583 of 2583 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► propose armistice with Britain
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0020  scroll 1830 600 down 7  ->  ok
  (scrolled down 7 at (1830, 600))
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 231 of 814 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2583 of 2583 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► propose armistice with Britain
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0021  click Austria  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 356 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Sire, the field reads +0 and no road carries. Propose Peace comes nearest at -1 of 50; her loyalty to the league — she has no reason of her own to brea …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Hopeless]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2583 of 2583 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► propose armistice with Britain
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0022  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 596 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 0 turns old and stays so; exhaustion holds. No territory or gold changes hands until it ends …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms](disabled: A truce settles nothing: no province or gold changes hands until it ends. Demands are pres)  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2628 of 2628 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose armistice with Austria
map: unchanged (54 labels)
```

```
#0023  click Not Now  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2694 of 2694 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0024  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2694 of 2694 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Of course, Sire. Take your time.
   ► propose armistice with Austria
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0025  scroll 1830 600 down 7  ->  ok
  (scrolled down 7 at (1830, 600))
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 231 of 814 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2694 of 2694 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Of course, Sire. Take your time.
   ► propose armistice with Austria
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0026  click Austria  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 356 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Permit me to observe, Sire, that a level war is the dearest kind to end: Propose Peace reads -1 of 50; it wants her loyalty to the league — she has no  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Hopeless]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2694 of 2694 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Of course, Sire. Take your time.
   ► propose armistice with Austria
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0027  click Propose Peace  ->  ok
  (clicked at (1825, 588))
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 442 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms / Mutual: /   • Peace Treaty (end state of war) — France and Austria /  / Assessment: GENEROUS / The manner of this peace: none — it brings Austria to no terms the Emperor's designs read (two of her own provinces or her capital, her vassalage, or a compensated cession). /  / Acceptance Estimate / Score: 0 - REJECT / Key advantage: Base Disposition / Key  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2739 of 2739 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose peace with Austria
map: unchanged (54 labels)
```

```
#0028  click Adjust terms  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 420 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria -8/50. / Treasury 400 gold: committed 0 / reserve 400 / remaining 0 / Sire, this settlement of the War with the Third Coalition — the table w …
   The table /   * Austria ▸ - Holding out (-8/50) White peace /       Blocker: Settlement legitimacy /       Metternich regrets that Austria must remain… unconvinced — it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. /       + Add demand / Austria is the holdout. / ▸ Austria won't accept these terms yet. Use 'More generous' (or ease …
   Austria:
   Coverage:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, a white peace for the War with the Third Coalition — the table with Austria cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered  …
   controls: <Austria ▸>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Bring Britain to the table]  [Bring Russia to the table]  <Grant>  <Decline>  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2760 of 2760 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: adjust terms
map: unchanged (54 labels)
```

```
#0029  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 420 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2760 of 2760 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
map: unchanged (54 labels)
```

```
#0030  click Back Out  ->  ok
  (clicked at (2250, 969))
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2827 of 2827 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0031  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2827 of 2827 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0032  scroll 1830 600 down 10  ->  ok
  (scrolled down 10 at (1830, 600))
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 376 of 816 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   Neutral (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2827 of 2827 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0033  scroll 1830 600 down 10  ->  ok
  (scrolled down 10 at (1830, 600))
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 805 of 845 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Saxony  —  Peace  |  -10 (Wary)]  [Hanover  —  Peace  |  -50 (Hostile)]  [Hesse  —  Peace  |  0 (Neutral)]  [Papal States  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2827 of 2827 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0034  click Denmark  ->  ok
  (clicked at (1825, 459))
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 200 px, 0 of 478 px] ──
   THE CABINET — Denmark
   DP: 5
   TALLEYRAND'S ASSESSMENT — DENMARK / Status: Peace   Relation: +10 (Neutral) /  / "Denmark is neither friend nor foe. Opportunity exists for closer ties — open borders would be a natural first step." / Recommendation: Talleyrand recommends: Court Denmark — ≈1 turn and 2 DP to carry Open Borders Agreement; improving relations would take ≈2 turns and 2 DP. Courting risks blowback — a 20% chance a tur …
   A vassalage of Denmark needs a war (a dictated peace) or open borders and above — we stand at Peace.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback]  [Propose Open Borders (1 DP)  —  Uncertain]  [↳ Skip ahead: Non-Aggression (2 DP)]  [Propose Vassal (3 DP)](disabled: A vassalage of Denmark needs a war (a dictated peace) or open borders and above — we stand)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2827 of 2827 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0035  click Propose Open Borders  ->  ok
  (clicked at (1825, 512))
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 68 px] ──
   DIPLOMATIC PROPOSAL — Denmark /  / Mutual: /   • Mutual open borders between France and Denmark /  / Harshness: Low / Acceptance estimate: ~45% (REJECT likely — no workable counter) / Key obstacle: the weight of the bloc pressing against them / DP cost: 1 /  / Political Context: /   • Denmark's court sees the French-led alignment consolidating across Europe and will resist a cross-bloc agreement.  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2872 of 2872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose open borders with Denmark
map: unchanged (54 labels)
```

```
#0036  click Adjust terms  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Denmark /  /  / "I suggest offering 25 gold per turn."
   controls: [icon: Close (Esc) @(2151,292)]  [Offer 25 gold]  [Offer more]  [Offer less]  [Skip gold]  [Never mind]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2894 of 2894 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: adjust terms
map: unchanged (54 labels)
```

```
#0037  click Skip gold  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Denmark /  /  / "Offering an Action Point is extraordinary — an entire extra action each turn. Worth 18 acceptance points, more than ceding a province."
   controls: [icon: Close (Esc) @(2151,292)]  [Offer the AP]  [Too costly]  [Back]  [Never mind]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2916 of 2916 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: skip gold
map: unchanged (54 labels)
```

```
#0038  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2982 of 2982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0039  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0039_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0040  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0040_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 295 of 838 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0041  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0041_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 582 of 822 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0042  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0042_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 763 of 843 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Saxony  —  Peace  |  -10 (Wary)]  [Hanover  —  Peace  |  -50 (Hostile)]  [Hesse  —  Peace  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0043  click Sweden  ->  ok
  (clicked at (1825, 381))
view: <run>\frames\0043_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 46 px, 0 of 468 px] ──
   THE CABINET — Sweden
   DP: 5
   TALLEYRAND'S ASSESSMENT — SWEDEN / Status: Peace   Relation: -60 (Hostile) /  / "Relations with Sweden remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate.
   Their design is aimed at France herself.
   Their price is 1368g — the treasury holds 400g.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1368g) (1 DP + 1368g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. No other design wakes after it.](disabled: Their price is 1368g — the treasury holds 400g.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
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
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0044  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0044_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0045  scroll 1830 600 down 16  ->  ok
  (scrolled down 16 at (1830, 600))
view: <run>\frames\0045_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 622 of 822 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0046  click Prussia  ->  ok
  (clicked at (1825, 442))
view: <run>\frames\0046_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 310 px, 0 of 445 px] ──
   THE CABINET — Prussia
   DP: 5
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: -10 (Wary) /  / "Prussia maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. Courting Prussia would be quicker — ≈4 turns again …
   The treasury cannot sustain the subsidy (needs 800g in hand).
   Their price is 1128g — the treasury holds 400g.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3).](disabled: The treasury cannot sustain the subsidy (needs 800g in hand).)  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Armed Neutrality next (600g to buy off in turn).](disabled: Their price is 1128g — the treasury holds 400g.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0047  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0047_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0048  key T  ->  ok
  (pressed T)
view: <run>\frames\0048_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 618 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Late September 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0049  key 7  ->  ok
  (pressed 7)
view: <run>\frames\0049_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 970 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late September 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire: 40,000 men on the Channel coast, 2 turns at war with Britain, stage a descent — no order; a march out resets the count. Her blockade on you lifts; a won Diversion can open the Strait for up to 2 turns …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0050  key T  ->  ok
  (pressed T)
view: <run>\frames\0050_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0051  click Swabia  ->  ERROR: no visible control's text holds "Swabia"
view: <run>\frames\0051_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2982 of 2982 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0052  click_at 1814 397  ->  ok
  (clicked at (1814, 397) on MapArea '100' (Control, layer 0))
view: <run>\frames\0052_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 420 px] ──
   Rhineland
   France  City · Plains / ACTIONS /   Recruit:  59,000 over the ordinance — every levy costs ×1.45 /       Infantry    741g — the treasury holds 400g /       Cavalry    1,504g — the treasury holds 400g /       Artillery    No commander of guns serves us — commission Marmont (4500g) and he raises a corps of guns. /   Substitutes:   Buy Substitutes    4,012g — the treasury holds 400g /   ▸ Build — 6 w …
   controls: [icon @(535,73)]  <▸ Build — 6 works>  <Fall back>  <Fall back>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2982 of 2982 px]: unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0053  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0053_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2982 of 2982 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (54 labels)
```

```
#0054  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0054_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 136 px] ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 4,851 casualties, 49,149 remaining /     Massena: 5,933 casualties, 36,067 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Archduke Charles: "France pays …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2853 of 2854 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   999 (+920 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
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
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
   ► what if Massena attacks Archduke John
   Were you to give the order, Sire:
   MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
   The band weighs a force of his you have not scouted within reach of Tyrol — scout the provinces round it.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► how do I get to Vienna
   Yes, Sire — Bernadotte can reach Vienna from Franconia in 2 turns: Franconia -> Bohemia -> Vienna. The order is 'Bernadotte, march to Vienna'.
   ► Murat, march to Swabia
   Murat awaits your orders!
   > Murat: go around
   Murat reroutes around Swabia. Murat: 'Enemy forces discovered at Swabia! Destination held by Mack. Odds unfavorable — awaiting orders.' Berthier adds: Ney, Davout, Lannes and Napoleon would answer the guns — Murat 22,000, 80,665 with the muster committed, against Mack (large force) — weighed together, the balance of force looks favorable.
   ► Murat, march to Flanders
   Murat begins march to Flanders. Route: Orleanais → Flanders. Cavalry charges through Lorraine -> Orleanais. Murat: "We march. Pity whatever slows us."
   [1/4 actions remaining]
   ► Murat, cancel
   Murat halts his march and awaits new orders.
   [0/4 actions remaining]
   ► lay down two ships
   Only 1 of the 2 laid — the yards allow 1 this turn — the blockade slows the slips. A keel is laid at Bordelais (400g). The fleet stands at 46 sail — readiness 69 (down 1 — new crews come aboard green at 40; only sea-time makes a navy), and Britain's blockade rots her 5 a turn at anchor — staging the camp lifts the blockade and readiness recovers +5/turn to 75. 0 more keels possible this turn.
   [0/4 actions remaining]
   ► propose armistice with Britain
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► propose armistice with Austria
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► propose open borders with Denmark
   Directing Talleyrand: adjust terms
   Directing Talleyrand: skip gold
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► end turn
   Your unratified settlement draft with Austria (1 clause) was set aside at turn's end.
   Bavaria's petition over Tyrol lapses with the settlement it was filed against, set aside at turn's end.
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -92g | Blockade: -219g | Materiel: -296g | Other: +1270g | Upkeep: -2654g | Net: +599g | Spent: 400g
   Treasury: 999g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,453 troops
   Supply shortage at Tyrol: Archduke John loses 591 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1859,469)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1813,497)  Murat(1687,440)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1788,425)  12k(1684,411)  10k(1910,648)
```

```
#0055  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0055_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   42,000 → 36,067
   54,000 → 49,149
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3487,62)]  [icon: Envoy from Prussia @(3529,62)]  [icon: Envoy from Ottoman Empire @(3571,62)]  [icon: Envoy from Portugal @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   0 →
   T:1
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   999 (+920 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Your unratified settlement draft with Austria (1 clause) was set aside at turn's end.
   Bavaria's petition over Tyrol lapses with the settlement it was filed against, set aside at turn's end.
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -92g | Blockade: -219g | Materiel: -296g | Other: +1270g | Upkeep: -2654g | Net: +599g | Spent: 400g
   Treasury: 999g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,453 troops
   Supply shortage at Tyrol: Archduke John loses 591 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 999g (+895 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 70% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 36,067 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Orleanais — 22,000 — Awaiting orders.
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
#0056  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0056_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1962 of 1962 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   999 (+920 next turn)
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
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0057  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0057_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: ok MUSTER — Ney (24,000; expect about 89,821 with the corps likely to arrive, up to 92,811 if all march; certain 24,000; a bad day (1 in 10) 76,464) vs Mack (large force) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  What Swabia can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 78,000 we muster) would cost ~585g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fort
── IncomingProposalPopup (layer 112) [scrolled 0 of 46 px] ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade /  / Hardenberg, stiffly: "Prussia's  …
   controls: [Accept]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2136 of 2136 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   734 (+1,153 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
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
   ► Ney, attack Mack
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (24,000; expect about 89,821 with the corps likely to arrive, up to 92,811 if all march; certain 24,000; a bad day (1 in 10) 76,464) vs Mack (large force) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 78,000 we muster) would cost ~585g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney launches a decisive assault. Ney gains the advantage over Mack. Casualties: Ney's army 5,311, Mack 18,568. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -265g, Austria -928g. Our treasury stands at 734 gold. Ney advances into Swabia. (298 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
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
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 68,811 committed (Davout, Lannes, Napoleon) = 92,811.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,153 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 2,158 | Mack 18,568
   Strength: Ney 24,000 → 21,842 → 21,544 after the advance | Mack 52,000 → 33,432
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1871,375)  Ney +3(1847,444)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Soult(1753,436)  Murat(1695,440)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1684,411)  10k(1910,648)
```

```
#0058  click Not Now  ->  ok
  (clicked at (1979, 687))
view: <run>\frames\0058_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2158 of 2158 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   734 (+1,153 next turn)
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
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0059  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0059_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   An unanswered envoy awaits your reply — the Cabinet stays shut until it is answered or the turn ends. Reopen Envoys to answer it.
   controls: [icon: Close (Esc) @(2075,284)]  [Open Envoys (3)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2158 of 2158 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Casualties: Ney's own corps 2,158 | Mack 18,568
   Strength: Ney 24,000 → 21,842 → 21,544 after the advance | Mack 52,000 → 33,432
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0060  click Open Envoys  ->  ok
  (clicked at (1829, 427))
view: <run>\frames\0060_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2158 of 2158 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   734 (+1,153 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Casualties: Ney's own corps 2,158 | Mack 18,568
   Strength: Ney 24,000 → 21,842 → 21,544 after the advance | Mack 52,000 → 33,432
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0061  scroll 1830 640 down 5  ->  ok
  (scrolled down 5 at (1830, 640))
view: <run>\frames\0061_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 91 of 91 px] ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
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
   or click the letter to reply in full
   controls: {ACTIVE}  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2158 of 2158 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Casualties: Ney's own corps 2,158 | Mack 18,568
   Strength: Ney 24,000 → 21,842 → 21,544 after the advance | Mack 52,000 → 33,432
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0062  click#2 Accept  ->  ok
  (clicked at (1433, 763))
view: <run>\frames\0062_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
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
   A COURT WRITES (1)
   Ottoman Empire writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Ottoman Empire
   Proposal
   Turn 1
   Incoming proposal: Open Borders Agreement
   Reis Efendi, serene and unhurried: "The Porte has outlasted a hundred ascendancies by keeping its counsel with each at its noon; France's noon has come, and the Sublime Porte observes it without haste. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2181 of 2181 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   794 (+1,172 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (53 labels)
```

```
#0063  click Accept  ->  ok
  (clicked at (1433, 613))
view: <run>\frames\0063_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
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
   Threat 76 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1632 of 1632 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   794 (+1,181 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
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
   ► Ney, attack Mack
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (24,000; expect about 89,821 with the corps likely to arrive, up to 92,811 if all march; certain 24,000; a bad day (1 in 10) 76,464) vs Mack (large force) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   What Swabia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 78,000 we muster) would cost ~585g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney launches a decisive assault. Ney gains the advantage over Mack. Casualties: Ney's army 5,311, Mack 18,568. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -265g, Austria -928g. Our treasury stands at 734 gold. Ney advances into Swabia. (298 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
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
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 68,811 committed (Davout, Lannes, Napoleon) = 92,811.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,153 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 2,158 | Mack 18,568
   Strength: Ney 24,000 → 21,842 → 21,544 after the advance | Mack 52,000 → 33,432
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
map: unchanged (53 labels)
```

```
#0064  click Open ▸  ->  ok
  (clicked at (2191, 294))
view: <run>\frames\0064_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 46 px] ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade /  / Hardenberg, stiffly: "Prussia's  …
   controls: [Accept]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2172 of 2172 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   794 (+1,181 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
map: unchanged (53 labels)
```

```
#0065  click Accept  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0065_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Napoleon
   10,000 → 9,461
   Lannes
   18,000 → 16,787
   Davout
   26,000 → 24,599
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 21,842 → 21,544 after the advance
   52,000 → 33,432
   marched to the guns
   marched to the guns
   +1 corps in reserve
   Soult — awaits explicit orders
   THE GREAT BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Treaty with Portugal @(3487,62)]  [icon: Treaty with Ottoman @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Open Borders Agreement Accepted @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   +17 →
   T:1
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2238 of 2238 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   794 (+1,191 next turn)
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
map: unchanged (53 labels)
```

```
#0066  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0066_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2260 of 2260 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   794 (+1,191 next turn)
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
   No pending envoys at this time.
map: unchanged (53 labels)
```

```
#0067  look  ->  ok
  (a fresh frame)
view: <run>\frames\0067_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2260 of 2260 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
map: unchanged (53 labels)
```

```
#0068  click_at 1753 436  ->  ok
  (clicked at (1753, 436) on MapArea '100' (Control, layer 0))
view: <run>\frames\0068_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) ──
   Brabant
   Holland  Rural · Plains / ACTIONS /     Negotiate with Holland   /  / One province — who holds it, what it pays, what defends it. Click the map to choose another. / Intel: Partial (reports only) / Income: Unknown   Stability: Unknown   Supply: Unknown /  / MARCH HERE  a standing order — he marches on each turn /     Soult · 1 AP · this turn   /     Dumonceau · 2 AP · this turn   /     Murat · 2 AP …
   controls: [icon @(535,73)]  <Negotiate with Holland>  <Soult · 1 AP · this turn>  <Dumonceau · 2 AP · this turn>  <Murat · 2 AP · this turn>  <Napoleon · 1 AP · 2 turns>  <Davout · 2 AP · 2 turns>  <+5 more…>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2260 of 2260 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   794 (+1,191 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
map: unchanged (53 labels)
```

```
#0069  click_at 1871 380  ->  ok
  (clicked at (1871, 380) on MapArea '100' (Control, layer 0))
view: <run>\frames\0069_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) ──
   Frankfurt
   Hesse  Capital · Plains / ACTIONS /     Negotiate with Hesse   /  / One province — who holds it, what it pays, what defends it. Click the map to choose another. / Intel: Partial (reports only) / Income: Unknown   Stability: Unknown   Supply: Unknown / Stripped? unknown — scout it / Garrison: Present (unknown strength) /  / MARCH HERE  a standing order — he marches on each turn /     Bernadotte     …
   controls: [icon @(535,73)]  <Negotiate with Hesse>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2260 of 2260 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
map: unchanged (53 labels)
```

```
#0070  click_at 1940 540  ->  ok
  (clicked at (1940, 540) on MapArea '100' (Control, layer 0))
view: <run>\frames\0070_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 793 px] ──
   Franconia
   Bavaria  Major City · Plains / ACTIONS /   Recruit:   Infantry     Cavalry     Artillery    not our soil — our levies are raised on our own ground /   Substitutes:   Buy Substitutes    3,308g — the treasury holds 794g /     Negotiate with Bavaria   /  / One province — who holds it, what it pays, what defends it. Click the map to choose another. / Income: 200g   Stability: 100%   Supply: 60,000 /   …
   controls: [icon @(535,73)]  <Negotiate with Bavaria>  <Fortify>  <Scout>  <Hold (2 AP)>  <Fall back>  <Napoleon · 1 AP · this turn>  <Davout · 2 AP · this turn>  <Lannes · 2 AP · this turn>  <Ney · 2 AP · this turn>  <Massena · 1 AP · 2 turns>  <+4 more…>  <Davout · 1 AP · this turn>  <Lannes · 1 AP · this turn>  <Napoleon · 1 AP · this turn>  <Ney · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <+4 more…>  <Davout · 1 AP · this turn>  <Lannes · 1 AP · this turn>  <Napoleon · 1 AP · this turn>  <Ney · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <+4 more…>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2260 of 2260 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
map: unchanged (53 labels)
```

```
#0071  click_at 1847 452  ->  ok
  (clicked at (1847, 452) on MapArea '100' (Control, layer 0))
view: <run>\frames\0071_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) ──
   Rhineland
   France  City · Plains / ACTIONS /   Recruit:  47,458 over the ordinance — every levy costs ×1.37 /       Infantry    819g — the treasury holds 794g /       Cavalry    1,412g — the treasury holds 794g /       Artillery    No commander of guns serves us — commission Marmont (4500g) and he raises a corps of guns. /   ▸ Build — 6 works (each finished work keeps 20g a turn) /  / One province — who hold …
   controls: [icon @(535,73)]  <▸ Build — 6 works>  <Napoleon · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Davout · 2 AP · this turn>  <Lannes · 2 AP · this turn>  <Murat · 2 AP · this turn>  <+5 more…>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2260 of 2260 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
map: unchanged (53 labels)
```

```
#0072  click_at 1850 560  ->  ok
  (clicked at (1850, 560) on MapArea '100' (Control, layer 0))
view: <run>\frames\0072_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2260 of 2260 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
map: unchanged (53 labels)
```

```
#0073  click_at 1850 520  ->  ok
  (clicked at (1850, 520) on MapArea '100' (Control, layer 0))
view: <run>\frames\0073_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 2223 px] ──
   Swabia
   Austria  City · Plains / ACTIONS /     Negotiate with Austria   /  / One province — who holds it, what it pays, what defends it. Click the map to choose another. / Income: 0g   Stability: 25%   Supply: 40,000 / War damage: 20%  suppressing this province's income /  / FORCES PRESENT /   Ney (21,544 foot)    Scout      Attack Mack      Hold (2 AP)      Fall back      Fortify   Mack stands here — att …
   controls: [icon @(535,73)]  <Negotiate with Austria>  <Scout>  <Attack Mack>  <Hold (2 AP)>  <Fall back>  <Scout>  <Attack Mack>  <Hold (2 AP)>  <Fall back>  <Scout>  <Attack Mack>  <Hold (2 AP)>  <Fall back>  <Scout>  <Attack Mack>  <Hold (1 AP)>  <Fall back>  <Bernadotte · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Murat · 2 AP · this turn>  <Massena · 2 AP · 2 turns>  <Teulie · 2 AP · 2 turns>  <+1 more…>  <Bernadotte · 1 AP · this turn>  <Murat · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <Teulie · 1 AP · 2 turns>  <+1 more…>  <Bernadotte · 1 AP · this turn>  <Murat · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <Teulie · 1 AP · 2 turns>  <+1 more…>  <Bernadotte · 1 AP · this turn>  <Murat · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <Teulie · 1 AP · 2 turns>  <+1 more…>  <Bernadotte · 1 AP · this turn>  <Murat · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <Teulie · 1 AP · 2 turns>  <+1 more…>  <Bernadotte · 1 AP · this turn>  <Murat · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <Teulie · 1 AP · 2 turns>  <+1 more…>  <Bernadotte · 1 AP · this turn>  <Murat · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <Teulie · 1 AP · 2 turns>  <+1 more…>  <Bernadotte · 1 AP · this turn>  <Murat · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <Teulie · 1 AP · 2 turns>  <+1 more…>  <Bernadotte · 1 AP · this turn>  <Murat · 1 AP · this turn>  <Soult · 1 AP · this turn>  <Massena · 1 AP · 2 turns>  <Teulie · 1 AP · 2 turns>  <+1 more…>  <Bernadotte · attack · 1 AP>  <Murat · attack · 1 AP>  <Soult · attack · 1 AP>  <Massena · march & attack · 2 AP · 2 turns>  <Teulie · march & a …
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2260 of 2260 px]: unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
map: unchanged (53 labels)
```

```
#0074  click Attack Mack  ->  ERROR: 4 controls match "Attack Mack" — pick one with click#N
  candidates: #1 <Attack Mack> on RegionPanel @(282,366) | #2 <Attack Mack> on RegionPanel @(282,366) | #3 <Attack Mack> on RegionPanel @(282,366) | #4 <Attack Mack> on RegionPanel @(282,366)
view: <run>\frames\0074_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 2223 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2260 of 2260 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
map: unchanged (53 labels)
```

```
#0075  click#1 Attack Mack  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0075_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Ney has taken Swabia
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+600 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2929 of 2929 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   682 (+1,151 next turn)
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
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 68,811 committed (Davout, Lannes, Napoleon) = 92,811.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,153 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 2,158 | Mack 18,568
   Strength: Ney 24,000 → 21,842 → 21,544 after the advance | Mack 52,000 → 33,432
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
   ► Ney, attack Mack
   ⚔ Second Battle of Swabia ⚔
   MUSTER — Ney (21,544; expect about 84,235 with the corps likely to arrive) vs Mack (33,432 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Swabia feeds 32,000 — the whole muster standing there would lose ~3,540 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 72,391 we muster) would cost ~543g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   Ney holds them at Swabia while allies attack from Rhineland! (+1 coordination)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Alert] Ney's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney engages in solid combat. Ney gains the advantage over Mack. Casualties: Ney's army 2,256, Mack 22,815. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -112g, Austria -1140g. Our treasury stands at 682 gold. Swabia has been captured by France!
   [Alarm] Europe's alarm rises +10 — Conquered territory +2, Won a battle +3, Won a decisive battle +5.
   [!] Mack's broken army flees to Munich! (106 lost to march) (recovering for 3 turns)
   Your forces have taken Swabia. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ⚑ Swabia captured! ⚑
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Ney fought with Davout, Lannes and Napoleon beside him — massed effective strength: 21,544 (lead) + 62,691 committed (Davout, Lannes, Napoleon) = 84,235.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Ney's supporting allies lost 1,364 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%, Exhaustion -10%, Flanking +1%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 892 | Mack 22,815
   Strength: Ney 21,544 → 20,652 | Mack 33,432 → 10,617
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1613,523)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney +3(1847,454)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,579)  Archduke John(2039,511)  Soult(1753,436)  ?(1880,562)  Mack(1868,501)  Murat(1695,440)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,492)  12k(1551,454)  ?(1769,580)  12k(1684,411)  10k(1910,648)
```

```
#0076  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0076_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Napoleon
   9,461 → 9,227
   Lannes
   16,787 → 16,267
   Davout
   24,599 → 23,989
   ⚔
   Ney ◆
   Mack ◆
   21,544 → 20,652
   33,432 → 10,617
   +1 corps in reserve
   Soult — awaits explicit orders
   SECOND BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Treaty with Portugal @(3487,62)]  [icon: Treaty with Ottoman @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Open Borders Agreement Accepted @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +36 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3018 of 3018 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   682 (+1,151 next turn)
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
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (55 labels)
```

```
#0077  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0077_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3018 of 3018 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   682 (+1,151 next turn)
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
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (55 labels)
```

```
#0078  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0078_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 796 px] ──
   ENEMY PHASE - Turn 2
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Second Battle of Milan /     Archduke Charles: 4,182 casualties, 43,514 remaining /     Massena's army: 5,008 casualties — Massena's own corps: 31,614 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%)  …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2552 of 2553 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   885 (+698 next turn)
   Inf:
   84,575
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 2,158 | Mack 18,568
   Strength: Ney 24,000 → 21,842 → 21,544 after the advance | Mack 52,000 → 33,432
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   No pending envoys at this time.
   ► Ney, attack Mack
   ⚔ Second Battle of Swabia ⚔
   MUSTER — Ney (21,544; expect about 84,235 with the corps likely to arrive) vs Mack (33,432 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Swabia feeds 32,000 — the whole muster standing there would lose ~3,540 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 72,391 we muster) would cost ~543g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   Ney holds them at Swabia while allies attack from Rhineland! (+1 coordination)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Alert] Ney's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney engages in solid combat. Ney gains the advantage over Mack. Casualties: Ney's army 2,256, Mack 22,815. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -112g, Austria -1140g. Our treasury stands at 682 gold. Swabia has been captured by France!
   [Alarm] Europe's alarm rises +10 — Conquered territory +2, Won a battle +3, Won a decisive battle +5.
   [!] Mack's broken army flees to Munich! (106 lost to march) (recovering for 3 turns)
   Your forces have taken Swabia. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ⚑ Swabia captured! ⚑
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Ney fought with Davout, Lannes and Napoleon beside him — massed effective strength: 21,544 (lead) + 62,691 committed (Davout, Lannes, Napoleon) = 84,235.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Ney's supporting allies lost 1,364 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%, Exhaustion -10%, Flanking +1%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 892 | Mack 22,815
   Strength: Ney 21,544 → 20,652 | Mack 33,432 → 10,617
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
   ► end turn
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -92g | Blockade: -281g | Materiel: -495g | Other: +1329g | Upkeep: -2848g | Net: +203g
   Treasury: 885g
   Actions refreshed: 4/4
   Bavaria completes a market at Franconia.
   Bavaria completes a market at Munich.
   Supply shortage at Swabia: Ney loses 762 troops — 91 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Davout loses 885 troops — 105 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Lannes loses 600 troops — 71 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Napoleon loses 340 troops — 40 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Tyrol: Mack loses 190 troops
   Supply shortage at Tyrol: Archduke Charles loses 1,531 troops
   Supply shortage at Tyrol: Archduke John loses 729 troops
   Switzerland loyalty 96 (-2): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1942,451)  ?(1959,325)  Brunswick(1958,287)  Ney +3(1859,454)  ?(1951,590)  Mack(1954,537)  ?(1965,564)  Archduke Charles(2028,511)  ?(1979,590)  Archduke John(2015,485)  Soult(1753,436)  Deroy(1901,535)  Murat(1695,440)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  10k(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1684,411)  10k(1910,648)
```

```
#0079  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0079_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Teulie
   7,500 → 6,945
   ⚔
   Massena ◆
   Archduke Charles ◆
   36,067 → 31,614
   47,696 → 43,514
   THE GREAT SECOND BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Envoy from Denmark @(3400,64)]  [icon: Envoy from Saxony @(3442,64)]  [icon: Marshal Murat seeks an audience @(3484,64)]  [icon: Treaty with Portugal @(3526,64)]  [icon: Treaty with Ottoman @(3568,64)]  [+2]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +30 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2004 of 2004 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   885 (+698 next turn)
   Inf:
   84,575
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Bavaria completes a market at Franconia.
   Bavaria completes a market at Munich.
   Supply shortage at Swabia: Ney loses 762 troops — 91 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Davout loses 885 troops — 105 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Lannes loses 600 troops — 71 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Napoleon loses 340 troops — 40 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Tyrol: Mack loses 190 troops
   Supply shortage at Tyrol: Archduke Charles loses 1,531 troops
   Supply shortage at Tyrol: Archduke John loses 729 troops
   Switzerland loyalty 96 (-2): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Marshal Ney holds the field at Swabia — Mack's corps breaks a second time on this ground and flees.
   • Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 885g (+698 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 33% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Massena — Milan — 28,020 — Hunted by Archduke Charles on consecutive turns — holds Milan with 28,020 men.
   - Davout — Swabia — 23,104 — Awaiting orders.
   - Murat — Orleanais — 22,000 — Awaiting orders.
   - Ney — Swabia — 19,890 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Lannes — Swabia — 15,667 — Awaiting orders.
   - Napoleon — Swabia — 8,887 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   - Teulie — Milan — 5,630 — Awaiting orders.
   INTELLIGENCE
   Deroy — Munich — 31,707 [confirmed]
   Mack — Tyrol — screening force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 2,587 men, at Swabia.
   Switzerland loyalty 96 (-2): satellite drift, the lord's defeats
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   War exhaustion grows — Austria nears breaking point (exhaustion: 28).
   Sire — Portugal and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Prussia and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 48).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   France hands Swabia back to Bavaria — the liberated soil comes home.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Denmark — Non-Aggression Pact
   - Saxony — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+31)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0080  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0080_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2004 of 2004 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   885 (+698 next turn)
   Inf:
   84,575
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0081  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0081_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2004 of 2004 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   885 (+698 next turn)
   Inf:
   84,575
   Cav:
   18,500
   Art:
   11,200
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0082  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0082_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2004 of 2004 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0083  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0083_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2004 of 2004 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0084  click Envoys  ->  ok
  (clicked at (3391, 18))
view: <run>\frames\0084_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2004 of 2004 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0085  click#2 Accept  ->  ok
  (clicked at (1433, 675))
view: <run>\frames\0085_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   A SMALL COURT WRITES (1)
   Denmark writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Denmark
   Proposal
   Turn 2
   Incoming proposal: Non-Aggression Pact
   Bernstorff, watchful and correct: "As his sovereign has long willed, Denmark moves toward what the Crown desires. Sign the pact of non-aggression."
   Terms: Proposal: Non-Aggression Pact
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Saxony @(3442,64)]  [icon: Treaty with Portugal @(3484,64)]  [icon: Treaty with Ottoman @(3526,64)]  [icon: Treaty with Prussia @(3568,64)]  [+1]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   967 (+706 next turn)
   Inf:
   84,575
   Cav:
   18,500
   Art:
   11,200
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (55 labels)
```

```
#0086  click Accept  ->  ok
  (clicked at (1433, 456))
view: <run>\frames\0086_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Saxony @(3442,64)]  [icon: Treaty with Denmark @(3484,64)]  [icon: Treaty with Portugal @(3526,64)]  [icon: Treaty with Ottoman @(3568,64)]  [+2]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2048 of 2048 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   967 (+725 next turn)
   Inf:
   84,575
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
map: unchanged (55 labels)
```

```
#0087  click Close  ->  ok
  (clicked at (3358, 64))
view: <run>\frames\0087_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   Imperial Box
   Blockade — Britain closes our ports
   T2
   Britain's fleet now outmatches ours 1.25 to 1 off our coast: our trade is cut by 62% (the Orders in Council), our crews rot 5 a turn at anchor and the yards lay one keel a turn. THE ADMIRALTY (press T, then 7) — the Blockade Board.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Saxony @(3442,64)]  [icon: Treaty with Denmark @(3484,64)]  [icon: Treaty with Portugal @(3526,64)]  [icon: Treaty with Ottoman @(3568,64)]  [+2]  [Keep]  [Acknowledge]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2048 of 2048 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
map: unchanged (55 labels)
```

```
#0088  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0088_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 1016 px] ──
   ENEMY PHASE - Turn 3
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     Fourth Battle of Milan /     Archduke Charles: 3,282 casualties, 35,926 remaining /     Massena's army: 4,155 casualties — Massena's own corps: 24,312 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Casu …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2028 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,458 (+1,125 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   France holds 28 regions. Treasury: 885g (+698 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 33% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Massena — Milan — 28,020 — Hunted by Archduke Charles on consecutive turns — holds Milan with 28,020 men.
   - Davout — Swabia — 23,104 — Awaiting orders.
   - Murat — Orleanais — 22,000 — Awaiting orders.
   - Ney — Swabia — 19,890 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Lannes — Swabia — 15,667 — Awaiting orders.
   - Napoleon — Swabia — 8,887 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   - Teulie — Milan — 5,630 — Awaiting orders.
   INTELLIGENCE
   Deroy — Munich — 31,707 [confirmed]
   Mack — Tyrol — screening force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 2,587 men, at Swabia.
   Switzerland loyalty 96 (-2): satellite drift, the lord's defeats
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   War exhaustion grows — Austria nears breaking point (exhaustion: 28).
   Sire — Portugal and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Prussia and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 48).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   France hands Swabia back to Bavaria — the liberated soil comes home.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Denmark — Non-Aggression Pact
   - Saxony — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+31)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -92g | Blockade: -329g | Materiel: -634g | Other: +1374g | Upkeep: -2418g | Net: +491g
   Treasury: 1,458g
   Actions refreshed: 4/4
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Supply shortage at Swabia: Ney loses 628 troops
   Supply shortage at Swabia: Davout loses 730 troops
   Supply shortage at Swabia: Lannes loses 460 troops
   Supply shortage at Swabia: Napoleon loses 280 troops
   Supply shortage at Tyrol: Archduke Charles loses 631 troops
   Supply shortage at Tyrol: Archduke John loses 374 troops
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 94 (-5): the contingent's dead, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 92 (-4): satellite drift, the lord's defeats
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier notes that Davout has grown restless — he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,481)  Mack(2024,443)  Bernadotte(1942,451)  Massena(1764,616)  ?(1959,325)  Brunswick(1958,287)  Ney +3(1859,454)  ?(1501,602)  Castanos(1501,564)  ?(1953,588)  Archduke Charles(1940,561)  ?(1980,588)  Archduke John(1995,528)  Soult(1753,436)  Deroy(1901,535)  Murat(1695,440)  Dumonceau(1755,322)  Teulie(1909,589)  ?(2072,435)  ?(1959,376)  ?(1869,762)  10k(1859,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1684,411)  10k(1910,645)
```

```
#0089  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0089_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   TEULIE REPORTS
   "Teulie is cornered at Milan with 3,751 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Teulie is cornered @(3358,64)]  [icon: Bernadotte — free attack! @(3400,64)]  [icon: Envoy from Hesse @(3442,64)]  [icon: Envoy from Papal States @(3484,64)]  [icon: Marshal Murat seeks an audience @(3526,64)]  [icon: Treaty with Saxony @(3568,64)]  [+5]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +25 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2269 of 2269 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,458 (+1,125 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Supply shortage at Swabia: Ney loses 628 troops
   Supply shortage at Swabia: Davout loses 730 troops
   Supply shortage at Swabia: Lannes loses 460 troops
   Supply shortage at Swabia: Napoleon loses 280 troops
   Supply shortage at Tyrol: Archduke Charles loses 631 troops
   Supply shortage at Tyrol: Archduke John loses 374 troops
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 94 (-5): the contingent's dead, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 92 (-4): satellite drift, the lord's defeats
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier notes that Davout has grown restless — he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Teulie: Teulie is cornered at Milan with 3,751 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
   • Sire — Teulie was mauled at Milan: a quarter of his corps — 1,432 men — lost in a single action.
   • Sire — Ney, Davout, Lannes and Napoleon stand 64,348 men at Swabia, which feeds 60,000. 4,348 too many. 4,685 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the province. Rhineland can feed 60,000 more and Franche-Comte can feed 52,500 more — a corps marched there ends it.
   • Sire — London now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1,368 gold and shortens the road to 5 turns.
   SITUATION
   France holds 28 regions. Treasury: 1,458g (+1,125 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 36% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 90 (Strong)
   MARSHAL STATUS
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 22,374 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Murat — Orleanais — 22,000 — Awaiting orders.
   < Massena — Piedmont — 20,056 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 20,056 men. Morale:19%
   ⚠ Morale failing (19) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Ney — Swabia — 19,262 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   » Bernadotte — Franconia — 15,005 — Threw back the enemy — may strike once, free, this turn only. Archduke Charles stands within reach at Tyrol. Trust:40
   - Lannes — Swabia — 14,105 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Napoleon — Swabia — 8,607 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   ? Teulie — Milan — 3,751 — Hunted by Archduke Charles on consecutive turns — holds Milan with 3,751 men. Morale:24%
   ⚠ Morale failing (24) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Deroy — Munich — 31,707 [confirmed]
   Mack — Bohemia — screening force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Supply cost you 2,098 men, at Swabia.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier notes that Davout has grown restless — he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Saxony and France have signed the Open Borders Agreement.
   Sire — Denmark and France have signed the Non-Aggression Pact.
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
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+26)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   Teulie awaits your orders!
map: unchanged (58 labels)
```

```
#0090  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0090_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2269 of 2269 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   Teulie awaits your orders!
map: unchanged (58 labels)
```

```
#0091  click Envoys  ->  ERROR: no visible control's text holds "Envoys"
view: <run>\frames\0091_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2269 of 2269 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   Teulie awaits your orders!
map: unchanged (58 labels)
```

```
#0092  click Attempt a Breakout  ->  ok
  (clicked at (1971, 584))
view: <run>\frames\0092_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Teulie
   5,630 → 5,183
   ⚔
   Massena ◆
   Archduke Charles ◆
   28,020 → 24,312
   39,208 → 35,926
   FOURTH BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 3
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3358,64)]  [icon: Envoy from Hesse @(3400,64)]  [icon: Envoy from Papal States @(3442,64)]  [icon: Marshal Murat seeks an audience @(3484,64)]  [icon: Treaty with Saxony @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+4]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2312 of 2312 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,458 (+1,125 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  46(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,481)  Mack(2024,443)  Bernadotte(1942,451)  Massena(1752,616)  Teulie(1776,590)  ?(1959,325)  Brunswick(1958,287)  Ney +3(1859,454)  ?(1501,602)  Castanos(1501,564)  ?(1940,588)  Archduke Charles(1940,561)  ?(1968,588)  Archduke John(1995,528)  Soult(1753,436)  Deroy(1901,535)  Murat(1695,440)  Dumonceau(1755,322)  ?(2072,435)  ?(1959,376)  ?(1869,762)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  12k(1684,411)  10k(1910,645)
```

```
#0093  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0093_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2312 of 2312 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map: unchanged (57 labels)
```

```
#0094  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0094_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2312 of 2312 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,458 (+1,125 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map: unchanged (57 labels)
```

```
#0095  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0095_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   An unanswered envoy awaits your reply — the Cabinet stays shut until it is answered or the turn ends. Reopen Envoys to answer it.
   controls: [icon: Close (Esc) @(2075,284)]  [Open Envoys (2)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2312 of 2312 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map: unchanged (57 labels)
```

```
#0096  click Open Envoys  ->  ok
  (clicked at (1829, 427))
view: <run>\frames\0096_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2312 of 2312 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,458 (+1,125 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map: unchanged (57 labels)
```

```
#0097  click Accept  ->  ERROR: 2 controls match "Accept" — pick one with click#N
  candidates: #1 [Accept] on MailboxPanel @(1433,478) | #2 [Accept] on MailboxPanel @(1433,697)
view: <run>\frames\0097_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2312 of 2312 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map: unchanged (57 labels)
```

```
#0098  click Accept  ->  ERROR: 2 controls match "Accept" — pick one with click#N
  candidates: #1 [Accept] on MailboxPanel @(1433,478) | #2 [Accept] on MailboxPanel @(1433,697)
view: <run>\frames\0098_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2312 of 2312 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map: unchanged (57 labels)
```

```
#0099  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0099_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2312 of 2312 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,458 (+1,125 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map: unchanged (57 labels)
```

```
#0100  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0100_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   An unanswered envoy awaits your reply — the Cabinet stays shut until it is answered or the turn ends. Reopen Envoys to answer it.
   controls: [icon: Close (Esc) @(2075,284)]  [Open Envoys (2)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2312 of 2312 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map: unchanged (57 labels)
```

```
#0101  click Open Envoys  ->  ok
  (clicked at (1829, 427))
view: <run>\frames\0101_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2312 of 2312 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,458 (+1,125 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
map: unchanged (57 labels)
```

```
#0102  click#1 Accept  ->  ok
  (clicked at (1433, 478))
view: <run>\frames\0102_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
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
   Threat 82 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Hesse @(3442,64)]  [icon: Treaty with Saxony @(3484,64)]  [icon: Treaty with Denmark @(3526,64)]  [icon: Treaty with Portugal @(3568,64)]  [+3]
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
   1,458 (+1,140 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
map: unchanged (57 labels)
```

```
#0103  click#1 Accept  ->  ok
  (clicked at (1433, 500))
view: <run>\frames\0103_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Hesse @(3442,64)]  [icon: Treaty with Papal States @(3484,64)]  [icon: Treaty with Saxony @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+4]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2356 of 2356 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,563 (+1,148 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (57 labels)
```

```
#0104  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0104_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2356 of 2356 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,563 (+1,148 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (57 labels)
```

```
#0105  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0105_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2356 of 2356 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (57 labels)
```

```
#0106  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0106_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 306 of 752 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -10 (Wary)]  [Spain  —  Alliance  |  +37 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -17 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Bavaria  —  Alliance  |  +57 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2356 of 2356 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (57 labels)
```

```
#0107  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0107_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 609 of 769 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (4)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Hesse  —  Non-Aggression  |  0 (Neutral)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2356 of 2356 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (57 labels)
```

```
#0108  scroll 1830 600 up 4  ->  ok
  (scrolled up 4 at (1830, 600))
view: <run>\frames\0108_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 448 of 751 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Ottoman Empire  —  Open Borders  |  -17 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Bavaria  —  Alliance  |  +57 (Friendly)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Hesse  —  Non-Aggression  |  0 (Neutral)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2356 of 2356 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (57 labels)
```

```
#0109  scroll 1830 600 up 2  ->  ok
  (scrolled up 2 at (1830, 600))
view: <run>\frames\0109_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 368 of 774 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Prussia  —  Open Borders  |  -10 (Wary)]  [Spain  —  Alliance  |  +37 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -17 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Bavaria  —  Alliance  |  +57 (Friendly)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2356 of 2356 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (57 labels)
```

```
#0110  click Prussia  ->  ok
  (clicked at (1825, 380))
view: <run>\frames\0110_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 266 px, 0 of 517 px] ──
   THE CABINET — Prussia
   DP: 7
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Open Borders   Relation: -10 (Wary) /  / "Our borders with Prussia are open, but trust remains shallow. A non-aggression pact would formalize the thaw." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Prussia stands on the Emperor's roads, Sire — The Pr …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3).]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Armed Neutrality next (600g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2356 of 2356 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (57 labels)
```

```
#0111  click Buy Off Their Design  ->  ok
  (clicked at (1825, 642))
view: <run>\frames\0111_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE CABINET ASKS:
   "Buy off Prussia's design — The Hanoverian Prize: 1,200 gold and 1 diplomatic point. The treasury holds 1,563 gold and would hold 363 after. The want sleeps 15 turns; it does not die — marching on Prussia inside the term is reneging, and it returns the heavier: their will against us +15, relations -25 and the strongest casus belli in Europe. Buying it wakes Armed Neutrality next (600g to buy off i …
   controls: [Buy it off]  [Not now]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1783 of 1783 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,563 (+1,148 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
   • Sire — Teulie was mauled at Milan: a quarter of his corps — 1,432 men — lost in a single action.
   • Sire — Ney, Davout, Lannes and Napoleon stand 64,348 men at Swabia, which feeds 60,000. 4,348 too many. 4,685 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the province. Rhineland can feed 60,000 more and Franche-Comte can feed 52,500 more — a corps marched there ends it.
   • Sire — London now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1,368 gold and shortens the road to 5 turns.
   SITUATION
   France holds 28 regions. Treasury: 1,458g (+1,125 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 36% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 90 (Strong)
   MARSHAL STATUS
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 22,374 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Murat — Orleanais — 22,000 — Awaiting orders.
   < Massena — Piedmont — 20,056 — Hunted by Archduke Charles across 1 frontier — stands at Piedmont with 20,056 men. Morale:19%
   ⚠ Morale failing (19) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Ney — Swabia — 19,262 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   » Bernadotte — Franconia — 15,005 — Threw back the enemy — may strike once, free, this turn only. Archduke Charles stands within reach at Tyrol. Trust:40
   - Lannes — Swabia — 14,105 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Napoleon — Swabia — 8,607 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   ? Teulie — Milan — 3,751 — Hunted by Archduke Charles on consecutive turns — holds Milan with 3,751 men. Morale:24%
   ⚠ Morale failing (24) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Deroy — Munich — 31,707 [confirmed]
   Mack — Bohemia — screening force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Supply cost you 2,098 men, at Swabia.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier notes that Davout has grown restless — he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Saxony and France have signed the Open Borders Agreement.
   Sire — Denmark and France have signed the Non-Aggression Pact.
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
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+26)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   Teulie awaits your orders!
   > Teulie: attempt breakout
   Teulie cuts his way out! Teulie falls back on Piedmont, his corps disordered but in the field. (37 lost to the march)
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
   ► buy off Prussia
   The Cabinet requests clarification...
map: unchanged (57 labels)
```

```
#0112  click Not now  ->  ok
  (clicked at (1829, 597))
view: <run>\frames\0112_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 46 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Hesse @(3442,64)]  [icon: Treaty with Papal States @(3484,64)]  [icon: Treaty with Saxony @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+4]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +25 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1849 of 1849 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,563 (+1,148 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (57 labels)
```

```
#0113  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0113_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1849 of 1849 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,563 (+1,148 next turn)
   Inf:
   86,587
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► buy off Prussia
   The Cabinet requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (57 labels)
```

```
#0114  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0114_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Prussia
   The Cabinet requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (57 labels)
```

```
#0115  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0115_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 384 px] ──
   LOAD GAME
   controls: [Autosave - Turn 4 (Turn 4)]  [replay_clock (Turn 19)]  [replay_firststep (Turn 4)]  [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1849 of 1849 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Prussia
   The Cabinet requests clarification...
   > cancel
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (57 labels)
```

```
#0116  click replay_firststep  ->  ok
  (clicked at (1825, 510))
view: <run>\frames\0116_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1543 of 1543 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+560 next turn)
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
   Loaded: replay_firststep
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+560 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 73% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Bohemia — 42,000 — Awaiting orders.
   > Soult — Franconia — 29,100 — Moving to Milan — 3 turns out. (to the letter)
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Munich — large force [partial]
   Archduke Charles — Carniola — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
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
   • Soult, attack Archduke John
   • Ney, march to Swabia
   • recruit infantry in Rhineland — 738g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Soult attacks Archduke John' first — it names who marches with Soult, and costs nothing.
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
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(2025,477)  Soult(1931,451)  Bernadotte(1971,425)  Deroy(1955,399)  ?(2016,632)  Archduke Charles(2016,605)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  ?(1948,579)  Archduke John(1948,540)  Napoleon(1752,436)  Lannes(1800,497)  Murat(1825,471)  Mack(1880,471)  ?(2068,435)  ?(2109,545)  ?(1959,372)  ?(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1685,416)  ?(1910,645)
```

```
#0117  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0117_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 1104 px] ──
   ENEMY PHASE - Turn 4
   AUSTRIA / ──────────────────────────── / - Mack attacks Lannes /     The Great Battle of Franche-Comte /     Mack: 5,021 casualties, 46,979 remaining /     Lannes's army: 4,052 casualties — Lannes's own corps: 15,727 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Lannes (The Emperor commands in person +10%) /     Casualties: Mack 5,02 …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2183 of 2183 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,117 (+1,043 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 5 BEGINS
   ═══════════════════════════════════════
   Income: 2559g | Requisitions: +50g | Admiralty: -90g | Blockade: -219g | Materiel: -726g | Other: +1337g | Upkeep: -2594g | Net: +317g
   Treasury: 1,117g
   Actions refreshed: 4/4
   Supply shortage at Bohemia: Massena loses 973 troops
   Supply shortage at Bohemia: Archduke Charles loses 826 troops
   Supply shortage at Franconia: Soult loses 620 troops
   Supply shortage at Franconia: Bernadotte loses 362 troops
   Supply shortage at Franconia: Deroy loses 409 troops
   Supply shortage at Munich: Mack loses 449 troops
   Soult holds at Franconia, per your orders — the guns at Bohemia did not move him.
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-4): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Bernadotte at Franconia. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(2012,477)  Archduke Charles(2037,451)  Soult(1931,451)  Bernadotte(1971,425)  Deroy(1955,399)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  Archduke John(1948,575)  Napoleon(1752,436)  Lannes(1800,497)  Murat(1825,471)  Mack(1901,528)  Dumonceau(1755,322)  Teulie(1909,601)  ?(2109,545)  ?(1959,372)  ?(1860,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1685,416)  10k(1910,645)
```

```
#0118  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0118_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 35,756
   54,000 → 50,159
   Soult — awaits explicit orders
   Bernadotte — weighed his own ambitions
   THE GREAT BATTLE OF BOHEMIA
   click anywhere to skip ▸
   BOHEMIA · TURN 4
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Envoy from Prussia @(3487,62)]  [icon: Envoy from Ottoman Empire @(3529,62)]  [icon: Envoy from Portugal @(3571,62)]  [icon: The Moniteur is out @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   -3 →
   T:4
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2181 of 2181 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,117 (+1,043 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ═══════════════════════════════════════
   Income: 2559g | Requisitions: +50g | Admiralty: -90g | Blockade: -219g | Materiel: -726g | Other: +1337g | Upkeep: -2594g | Net: +317g
   Treasury: 1,117g
   Actions refreshed: 4/4
   Supply shortage at Bohemia: Massena loses 973 troops
   Supply shortage at Bohemia: Archduke Charles loses 826 troops
   Supply shortage at Franconia: Soult loses 620 troops
   Supply shortage at Franconia: Bernadotte loses 362 troops
   Supply shortage at Franconia: Deroy loses 409 troops
   Supply shortage at Munich: Mack loses 449 troops
   Soult holds at Franconia, per your orders — the guns at Bohemia did not move him.
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-4): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Bernadotte at Franconia. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   --- Strategic Order Updates ---
   Soult: Soult is marching to Milan (2 turns remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 5
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,117g (+1,043 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 66% of French forces (an estimate — 1 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Bohemia — 34,783 — Awaiting orders.
   > Soult — Franconia — 28,480 — Moving to Milan — 2 turns out. (to the letter)
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 17,686 — Awaiting orders.
   - Bernadotte — Franconia — 16,638 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 14,952 — Awaiting orders.
   - Napoleon — Lorraine — 9,054 — Awaiting orders.
   - Teulie — Milan — 7,000 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 18,793 [confirmed]
   Archduke Charles — Bohemia — 49,333 [confirmed]
   Archduke John — Tyrol — 18,084 [confirmed]
   Mack — Munich — large force [partial]
   Brunswick — Berlin — large force [partial]
   Vienna garrison — Vienna — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 1,955 men, at Bohemia and Franconia.
   Soult holds at Franconia, per your orders — the guns at Bohemia did not move him.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Bernadotte at Franconia. The Kingdom of Italy pays them; their dead will be its grief.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0119  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0119_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2181 of 2181 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,117 (+1,043 next turn)
   Inf:
   82,300
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
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0120  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0120_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2181 of 2181 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,117 (+1,043 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0121  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0121_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2181 of 2181 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0122  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0122_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2181 of 2181 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0123  type Massena, march to Milan  ->  ok
  (typed and Enter)
view: <run>\frames\0123_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: Massena is engaged with Archduke Charles and cannot begin a strategic march. Deal with the engagement first.
Try: 'Massena, attack Archduke Charles' or 'Massena, retreat'. Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
── IncomingProposalPopup (layer 112) [scrolled 0 of 46 px] ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade /  / Hardenberg, stiffly: "Prussia's  …
   controls: [Accept]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2313 of 2313 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,117 (+1,043 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Massena, march to Milan
   Massena is engaged with Archduke Charles and cannot begin a strategic march. Deal with the engagement first.
   Try: 'Massena, attack Archduke Charles' or 'Massena, retreat'. Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
map: unchanged (55 labels)
```

```
#0124  click Not Now  ->  ok
  (clicked at (1979, 687))
view: <run>\frames\0124_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2336 of 2336 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,117 (+1,043 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (55 labels)
```

```
#0125  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0125_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1740 of 1741 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,117 (+1,043 next turn)
   Inf:
   82,300
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]  [Open Envoys (3)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,117g (+1,043 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 66% of French forces (an estimate — 1 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Bohemia — 34,783 — Awaiting orders.
   > Soult — Franconia — 28,480 — Moving to Milan — 2 turns out. (to the letter)
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 17,686 — Awaiting orders.
   - Bernadotte — Franconia — 16,638 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 14,952 — Awaiting orders.
   - Napoleon — Lorraine — 9,054 — Awaiting orders.
   - Teulie — Milan — 7,000 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 18,793 [confirmed]
   Archduke Charles — Bohemia — 49,333 [confirmed]
   Archduke John — Tyrol — 18,084 [confirmed]
   Mack — Munich — large force [partial]
   Brunswick — Berlin — large force [partial]
   Vienna garrison — Vienna — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 1,955 men, at Bohemia and Franconia.
   Soult holds at Franconia, per your orders — the guns at Bohemia did not move him.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Bernadotte at Franconia. The Kingdom of Italy pays them; their dead will be its grief.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   ► Massena, march to Milan
   Massena is engaged with Archduke Charles and cannot begin a strategic march. Deal with the engagement first.
   Try: 'Massena, attack Archduke Charles' or 'Massena, retreat'. Ask 'what if Massena attacks Archduke Charles' first — it names who marches with Massena, and costs nothing.
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   ⚠ You have 3 unanswered envoys that will lapse if you end the turn now.
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
map: unchanged (55 labels)
```

```
#0126  click End Turn  ->  ok
  (clicked at (817, 978))
view: <run>\frames\0126_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 840 px] ──
   ENEMY PHASE - Turn 5
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Second Battle of Bohemia /     Archduke Charles: 4,692 casualties, 44,641 remaining /     Massena's army: 5,451 casualties — Massena's own corps: 30,547 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10% …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2161 of 2161 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,829 (+1,333 next turn)
   Inf:
   84,437
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
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2551g | Requisitions: +50g | Admiralty: -90g | Blockade: -219g | Materiel: -621g | Other: +1319g | Upkeep: -2278g | Net: +712g
   Treasury: 1,829g
   Actions refreshed: 4/4
   Bavaria completes a supply depot at Franconia.
   Supply shortage at Bohemia: Massena loses 923 troops — 215 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Bohemia: Archduke Charles loses 615 troops
   Supply shortage at Munich: Mack loses 282 troops
   Soult holds at Swabia, per your orders — the guns at Franche-Comte did not move him.
   Holland loyalty 96 (-2): satellite drift, the lord's defeats
   Kingdom of Italy loyalty 89 (-9): the contingent's dead, satellite drift
   Switzerland loyalty 92 (-4): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(2012,477)  Archduke Charles(2037,451)  Bernadotte(1905,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Soult(1845,477)  Ney(1814,397)  Davout(1839,371)  Archduke John(1948,575)  Napoleon(1752,436)  Lannes(1800,503)  Murat(1825,451)  Mack(1901,528)  Dumonceau(1755,322)  Teulie(1909,601)  ?(2109,545)  ?(1959,376)  ?(1860,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1685,416)  10k(1910,645)
```

```
#0127  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0127_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Bernadotte
   16,638 → 15,423
   ⚔
   Massena ◆
   Archduke Charles ◆
   34,783 → 30,547
   49,333 → 44,641
   marched to the guns
   Soult — awaits explicit orders
   Archduke John — could not reach the field
   THE GREAT SECOND BATTLE OF BOHEMIA
   click anywhere to skip ▸
   BOHEMIA · TURN 5
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3445,62)]  [icon: Blockade — Britain closes our ports @(3487,62)]  [icon: Envoy from Denmark @(3529,62)]  [icon: Envoy from Saxony @(3571,62)]  [icon: The Moniteur is out @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   -8 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2161 of 2161 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2551g | Requisitions: +50g | Admiralty: -90g | Blockade: -219g | Materiel: -621g | Other: +1319g | Upkeep: -2278g | Net: +712g
   Treasury: 1,829g
   Actions refreshed: 4/4
   Bavaria completes a supply depot at Franconia.
   Supply shortage at Bohemia: Massena loses 923 troops — 215 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Bohemia: Archduke Charles loses 615 troops
   Supply shortage at Munich: Mack loses 282 troops
   Soult holds at Swabia, per your orders — the guns at Franche-Comte did not move him.
   Holland loyalty 96 (-2): satellite drift, the lord's defeats
   Kingdom of Italy loyalty 89 (-9): the contingent's dead, satellite drift
   Switzerland loyalty 92 (-4): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   --- Strategic Order Updates ---
   Soult: Soult adjusts route to avoid enemy at Tyrol. Moves to Swabia.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Teulie was mauled at Milan: half of his corps — 3,694 men — lost in a single action.
   • Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,829g (+1,333 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 52% of French forces (an estimate — 1 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Massena — Bohemia — 29,624 — Hunted by Archduke Charles on consecutive turns — holds Bohemia with 29,624 men.
   ⚠ Starving — supply has failed at Bohemia two turns running.
   > Soult — Swabia — 27,713 — Moving to Milan — 6 turns out. (to the letter)
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 17,038 — Awaiting orders.
   - Bernadotte — Franconia — 15,423 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 13,123 — Hunted by Mack on consecutive turns — holds Franche-Comte with 13,123 men.
   - Napoleon — Lorraine — 8,224 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   - Teulie — Milan — 3,306 — Awaiting orders. Morale:34%
   ⚠ Morale failing (34) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   INTELLIGENCE
   Deroy — Franconia — 18,793 [confirmed]
   Archduke Charles — Bohemia — 44,026 [confirmed]
   Archduke John — Tyrol — 18,084 [confirmed]
   Mack — Munich — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Vienna garrison — Vienna — garrison — substantial force [partial]
   TURN EVENTS
   Supply shortage at Bohemia: Massena loses 923 troops — 215 of them to living off the land (this stripped country feeds a French army 80%)
   Soult holds at Swabia, per your orders — the guns at Franche-Comte did not move him.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   LAPSED ENVOYS
   Prussia's Open Borders Agreement offer lapsed unanswered
   Ottoman Empire's Gift of Friendship offer lapsed unanswered
   Portugal's Gift of Friendship offer lapsed unanswered
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Denmark — Non-Aggression Pact
   - Saxony — Open Borders Agreement
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-7)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0128  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0128_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 91 px] ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   THE SMALL COURTS WRITE (2)
   Denmark and Saxony write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Denmark
   Proposal
   Turn 5
   Incoming proposal: Non-Aggression Pact
   Bernstorff, watchful and correct: "My master's design is known to all Europe; Denmark sends this offer in its pursuit. Sign the pact of non-aggression."
   Terms: Proposal: Non-Aggression Pact
   or click the letter to reply in full
   WAITING
   Saxony
   Proposal
   Turn 5
   Incoming proposal: Open Borders Agreement
   Einsiedel, anxiously: "Saxony has kept her house through many great reigns by keeping her treaties in good repair; His Majesty would merely continue the practice. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Saxony pays you 82 gold at the signing
   or click the letter to reply in full
   WAITING
   Switzerland
   Proposal
   Turn 6
   Incoming proposal: Client's Petition
   Terms: Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +8 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. · Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now +0); nothing is charged. · Left unanswered at the turn's end, the  …
   controls: {ACTIVE}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2161 of 2161 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0129  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0129_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2161 of 2161 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,829 (+1,333 next turn)
   Inf:
   84,437
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0130  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0130_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2161 of 2161 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,829 (+1,333 next turn)
   Inf:
   84,437
   Cav:
   18,500
   Art:
   11,200
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0131  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0131_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2161 of 2161 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0132  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0132_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2161 of 2161 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0133  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0133_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2161 of 2161 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0134  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0134_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 384 px] ──
   LOAD GAME
   controls: [Autosave - Turn 6 (Turn 6)]  [replay_clock (Turn 19)]  [replay_firststep (Turn 4)]  [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2161 of 2161 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 66/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0135  click replay_firststep  ->  ok
  (clicked at (1825, 510))
view: <run>\frames\0135_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1543 of 1543 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+560 next turn)
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
   Loaded: replay_firststep
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+560 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 73% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Bohemia — 42,000 — Awaiting orders.
   > Soult — Franconia — 29,100 — Moving to Milan — 3 turns out. (to the letter)
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Munich — large force [partial]
   Archduke Charles — Carniola — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
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
   • Soult, attack Archduke John
   • Ney, march to Swabia
   • recruit infantry in Rhineland — 738g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Soult attacks Archduke John' first — it names who marches with Soult, and costs nothing.
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
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(2025,477)  Soult(1931,451)  Bernadotte(1971,425)  Deroy(1955,399)  ?(2016,632)  Archduke Charles(2016,605)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  ?(1948,579)  Archduke John(1948,540)  Napoleon(1752,436)  Lannes(1800,497)  Murat(1825,471)  Mack(1880,471)  ?(2068,435)  ?(2109,545)  ?(1959,372)  ?(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1685,416)  ?(1910,645)
```

```
#0136  type Massena, march to Milan  ->  ok
  (typed and Enter)
view: <run>\frames\0136_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok Massena: 'Archduke John bars the way at Tyrol, Sire — I can take him.' Massena engages him on the road, on his own judgment.

MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Massena' and he will march
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
  Archduke John does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
  (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
Ask 'what if Massena attacks Archduke John' to read the muster before you commit — it costs nothing.


[Combat] Massena leads the charge! (Aggressive: +15% attack)
[Shi
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Archduke Charles
   54,000 → 49,970
   ⚔
   Massena ◆
   Archduke John ◆
   42,000 → 34,327
   20,000 → 18,010
   marched to the guns
   Soult — awaits explicit orders
   Bernadotte — weighed his own ambitions
   THE GREAT BATTLE OF TYROL
   click anywhere to skip ▸
   TYROL · TURN 4
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1743 of 2161 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   417 (+800 next turn)
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
   ► Massena, march to Milan
   ⚔ The Great Battle of Tyrol ⚔
   Massena: 'Archduke John bars the way at Tyrol, Sire — I can take him.' Massena engages him on the road, on his own judgment.
   MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Massena' and he will march
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
   Archduke John does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Ask 'what if Massena attacks Archduke John' to read the muster before you commit — it costs nothing.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Archduke John stands firm against superior numbers! (Cautious: +10% outnumbered)
   [Terrain] Archduke John benefits from Mountains terrain (+25% defense)
   [Combat] Adjacent allies bolster Massena's attack! (+4%)
   Massena delivers an effective strike. Brutal stalemate between Massena and Archduke John. Heavy casualties on both sides: Massena 7,673, Archduke John 6,020.
   [Materiel] Guns, horses and stores lost with the fallen: France -383g, Austria -301g. Our treasury stands at 417 gold.
   ArchdukeCharles withdraws to Carniola after the battle.
   Berthier: an inconclusive affair of his own making — nothing gained, nothing charged.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Archduke John was reinforced — massed effective strength: 20,000 (lead) + 64,243 committed (Archduke Charles) = 84,243.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Archduke John's supporting ally lost 4,030 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "Nothing settled. I do not leave accounts open for long."
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena 7,673 | Archduke John's own corps 1,990
   Strength: Massena 42,000 → 34,327 | Archduke John 20,000 → 18,010
   Berthier: "Where was Bernadotte? Massena held the field alone — reinforcement never came."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(2025,477)  Soult(1931,451)  Bernadotte(1971,425)  Deroy(1955,399)  ?(2016,632)  Archduke Charles(2016,605)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  Archduke John(1948,575)  Napoleon(1752,436)  Lannes(1800,497)  Murat(1825,471)  Mack(1901,528)  ?(2068,435)  ?(2109,545)  ?(1959,372)  ?(1901,603)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1685,416)  ?(1910,645)
```

```
#0137  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0137_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1743 of 2161 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena 7,673 | Archduke John's own corps 1,990
   Strength: Massena 42,000 → 34,327 | Archduke John 20,000 → 18,010
   Berthier: "Where was Bernadotte? Massena held the field alone — reinforcement never came."
map: unchanged (55 labels)
```

```
#0138  key L  ->  ok
  (pressed L)
view: <run>\frames\0138_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: 'l' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1743 of 2191 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   417 (+800 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   [Lannes,]  (Tab)
   l
   controls: [+]  [−]  [—]  [Execute]  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena 7,673 | Archduke John's own corps 1,990
   Strength: Massena 42,000 → 34,327 | Archduke John 20,000 → 18,010
   Berthier: "Where was Bernadotte? Massena held the field alone — reinforcement never came."
map: unchanged (55 labels)
```

```
#0139  look  ->  ok
  (a fresh frame)
view: <run>\frames\0139_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: 'l' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1743 of 2191 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena 7,673 | Archduke John's own corps 1,990
   Strength: Massena 42,000 → 34,327 | Archduke John 20,000 → 18,010
   Berthier: "Where was Bernadotte? Massena held the field alone — reinforcement never came."
map: unchanged (55 labels)
```

```
#0140  click Event Log  ->  ok
  (clicked at (53, 18))
view: <run>\frames\0140_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: 'l'
open: screens=['event_log'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── CampaignLog (layer 50) ──
   CAMPAIGN LOG
   Soult ordered to move to Milan
   Massena ordered to move to Milan
   The Great Battle of Tyrol: Massena (France) attacked Archduke John (Austria) — stalemate (7,673 / 6,020 casualties) — on his own judgment, on the road — Archduke John: "Neither yields. The Alps are patient, and so am I."
   controls: [Pin]  [icon: Close (L) @(2143,296)]  [▾ Turn 4  -  3 events]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1743 of 2191 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena 7,673 | Archduke John's own corps 1,990
   Strength: Massena 42,000 → 34,327 | Archduke John 20,000 → 18,010
   Berthier: "Where was Bernadotte? Massena held the field alone — reinforcement never came."
map: unchanged (55 labels)
```

```
#0141  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0141_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: 'l'
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1743 of 2191 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena 7,673 | Archduke John's own corps 1,990
   Strength: Massena 42,000 → 34,327 | Archduke John 20,000 → 18,010
   Berthier: "Where was Bernadotte? Massena held the field alone — reinforcement never came."
map: unchanged (55 labels)
```

```
#0142  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0142_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: 'l' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 1104 px] ──
   ENEMY PHASE - Turn 4
   AUSTRIA / ──────────────────────────── / - Mack attacks Lannes /     The Great Battle of Franche-Comte /     Mack: 5,347 casualties, 46,653 remaining /     Lannes's army: 3,908 casualties — Lannes's own corps: 15,808 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Lannes (The Emperor commands in person +10%) /     Casualties: Mack 5,34 …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2873 of 2873 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   917 (+1,256 next turn)
   Inf:
   82,250
   Cav:
   16,750
   Art:
   10,600
   l
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
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
   ► Massena, march to Milan
   ⚔ The Great Battle of Tyrol ⚔
   Massena: 'Archduke John bars the way at Tyrol, Sire — I can take him.' Massena engages him on the road, on his own judgment.
   MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Massena' and he will march
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
   Archduke John does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Ask 'what if Massena attacks Archduke John' to read the muster before you commit — it costs nothing.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Archduke John stands firm against superior numbers! (Cautious: +10% outnumbered)
   [Terrain] Archduke John benefits from Mountains terrain (+25% defense)
   [Combat] Adjacent allies bolster Massena's attack! (+4%)
   Massena delivers an effective strike. Brutal stalemate between Massena and Archduke John. Heavy casualties on both sides: Massena 7,673, Archduke John 6,020.
   [Materiel] Guns, horses and stores lost with the fallen: France -383g, Austria -301g. Our treasury stands at 417 gold.
   ArchdukeCharles withdraws to Carniola after the battle.
   Berthier: an inconclusive affair of his own making — nothing gained, nothing charged.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Archduke John was reinforced — massed effective strength: 20,000 (lead) + 64,243 committed (Archduke Charles) = 84,243.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Archduke John's supporting ally lost 4,030 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "Nothing settled. I do not leave accounts open for long."
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena 7,673 | Archduke John's own corps 1,990
   Strength: Massena 42,000 → 34,327 | Archduke John 20,000 → 18,010
   Berthier: "Where was Bernadotte? Massena held the field alone — reinforcement never came."
   ► end turn
   ═══════════════════════════════════════
   TURN 5 BEGINS
   ═══════════════════════════════════════
   Income: 2559g | Requisitions: +50g | Contributions: -49g | Admiralty: -90g | Blockade: -219g | Materiel: -756g | Other: +1337g | Upkeep: -2332g | Net: +500g
   Treasury: 917g
   Actions refreshed: 4/4
   Supply shortage at Bohemia: Massena loses 678 troops
   Supply shortage at Bohemia: Archduke Charles loses 646 troops
   Supply shortage at Franconia: Soult loses 620 troops
   Supply shortage at Franconia: Bernadotte loses 362 troops
   Supply shortage at Franconia: Deroy loses 410 troops
   Supply shortage at Franche-Comte: Lannes loses 378 troops
   Supply shortage at Franche-Comte: Murat loses 420 troops
   Supply shortage at Franche-Comte: Mack loses 1,502 troops
   Soult holds at Franconia, per your orders — the guns at Tyrol did not move him.
   Holland loyalty 96 (-4): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 96 (-4): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 94 (-6): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,000 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Bernadotte at Franconia. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(2012,477)  Archduke Charles(2037,451)  Soult(1931,451)  Bernadotte(1971,425)  Deroy(1955,399)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  Archduke John(1948,575)  Napoleon(1752,436)  Lannes(1800,497)  Murat(1813,471)  Mack(1825,445)  Dumonceau(1755,322)  Teulie(1909,601)  ?(2109,545)  ?(1959,372)  ?(1860,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1685,416)  10k(1910,645)
```

```
#0143  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0143_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: 'l' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   15,808 → 14,716
   ⚔
   Murat ◆
   Mack ◆
   21,197 → 16,312
   46,653 → 42,880 → 41,594 after the advance
   SECOND BATTLE OF FRANCHE-COMTE
   click anywhere to skip ▸
   FRANCHE-COMTE · TURN 4
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Envoy from Prussia @(3487,62)]  [icon: Envoy from Ottoman Empire @(3529,62)]  [icon: Envoy from Portugal @(3571,62)]  [icon: The Moniteur is out @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   -7 →
   T:4
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   917 (+1,256 next turn)
   Inf:
   82,250
   Cav:
   16,750
   Art:
   10,600
   l
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Massena: Massena is marching to Milan (2 turns remaining).
   Soult: Soult is marching to Milan (2 turns remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 5
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Mack has crossed into Franche-Comte. Lannes and Murat stand in his path.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 917g (+1,256 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 58% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   > Soult — Franconia — 28,480 — Moving to Milan — 2 turns out. (to the letter)
   > Massena — Bohemia — 28,375 — Moving to Milan — 2 turns out.
   ⚠ IN PERIL — an enemy force of ~45,885 shares the field (Bohemia).
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Bernadotte — Franconia — 16,638 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 15,892 — Awaiting orders.
   ⚠ IN PERIL — an enemy force of ~40,092 shares the field (Franche-Comte).
   - Lannes — Franche-Comte — 14,338 — Awaiting orders.
   ⚠ IN PERIL — an enemy force of ~40,092 shares the field (Franche-Comte).
   - Napoleon — Lorraine — 9,087 — Awaiting orders.
   - Teulie — Milan — 7,000 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 18,837 [confirmed]
   Mack — Franche-Comte — 40,092 [confirmed]
   Archduke Charles — Bohemia — 45,885 [confirmed]
   Archduke John — Tyrol — 16,124 [confirmed]
   Brunswick — Berlin — large force [partial]
   Vienna garrison — Vienna — garrison — substantial force [partial]
   TURN EVENTS
   Supply cost you 2,458 men, at Bohemia, Franconia and Franche-Comte.
   Soult holds at Franconia, per your orders — the guns at Tyrol did not move him.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,000 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Bernadotte at Franconia. The Kingdom of Italy pays them; their dead will be its grief.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-7)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0144  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0144_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: 'l' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1696 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   917 (+1,256 next turn)
   Inf:
   82,250
   Cav:
   16,750
   Art:
   10,600
   l
   controls: [+]  [−]  [—]  [Execute]  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0145  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0145_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: 'l'
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1653 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 5 — Late November 1805 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Mack has crossed into Franche-Comte. Lannes and Murat stand in his path. /   • Sire — London now pays St Petersburg 200 gold a turn a …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (3)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0146  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0146_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: 'l'
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -7 →
   T:4
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0147  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0147_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: 'l'
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
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0148  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0148_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: 'l'
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 384 px] ──
   LOAD GAME
   controls: [Autosave - Turn 5 (Turn 5)]  [replay_clock (Turn 19)]  [replay_firststep (Turn 4)]  [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0149  click replay_clock  ->  ok
  (clicked at (1825, 462))
view: <run>\frames\0149_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 60 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:18
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
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
   Loaded: replay_clock
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
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
   Threat: 60/100 [Formed]
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
#0150  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0150_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 136 px] ──
   ENEMY PHASE - Turn 19
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 4,577 casualties, 49,423 remaining /     Massena: 5,240 casualties, 36,760 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Archduke Charles: "France pays …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 58 / 100
   Turn 20 — Early July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (4)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,460 (+922 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -262g | Other: +1295g | Upkeep: -2654g | Net: +660g
   Treasury: 1,460g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,468 troops
   Supply shortage at Tyrol: Archduke John loses 594 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1880,478)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1838,471)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1788,425)  12k(1693,420)  10k(1910,648)
```

```
#0151  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0151_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 36,760
   54,000 → 49,423
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 19
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 58 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (4)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3403,62)]  [icon: Blockade — Britain closes our ports @(3445,62)]  [icon: Envoy from Prussia @(3487,62)]  [icon: Envoy from Denmark @(3529,62)]  [icon: Envoy from Hesse @(3571,62)]  [icon: The Moniteur is out @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   0 →
   T:19
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1850 of 1850 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,460 (+922 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Treasury: 1,460g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,468 troops
   Supply shortage at Tyrol: Archduke John loses 594 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 20
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,460g (+922 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 70% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 36,760 — Awaiting orders.
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
   An envoy from Denmark has arrived with a proposal.
   An envoy from Hesse has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   An envoy from Switzerland has arrived with a petition.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 4 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - Denmark — Non-Aggression Pact
   - Hesse — Non-Aggression Pact
   - ...and 1 more
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 58/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0152  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0152_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1850 of 1850 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,460 (+922 next turn)
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
   Threat: 58/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0153  click THIRD COALITION  ->  ok
  (clicked at (3429, 965))
view: <run>\frames\0153_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) ──
   THIRD COALITION
   Britain
   BR
   0
   FR
   Austria
   AU
   0
   FR
   Russia
   RU
   0
   FR
   Leader: Britain   Posture: Defensive /  /   Britain  WE:8  Unknown  — leads the coalition /   Austria  WE:10  ~120,000 men /   Russia  WE:8  Unknown /  / Coordination /   Britain-Austria: Good /   Britain-Russia: Good /   Austria-Russia: Good /  / Weak link: Austria (highest WE)
   controls: [icon @(3139,276)]  [Open Whole-War Settlement]  [Target Austria]  [Target Russia]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1850 of 1850 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,460 (+922 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 58/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0154  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0154_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1850 of 1850 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 58/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0155  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0155_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1850 of 1850 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 58/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0156  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0156_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 384 px] ──
   LOAD GAME
   controls: [Autosave - Turn 20 (Turn 20)]  [replay_clock (Turn 19)]  [replay_firststep (Turn 4)]  [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1850 of 1850 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 58/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0157  click replay_sea  ->  ok
  (clicked at (1825, 558))
view: <run>\frames\0157_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   +5 ↑
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
   Loaded: replay_sea
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 29 regions. Treasury: 800g (+471 by the accounts)
   The courts at war hold 27 regions. Estimated enemy strength: 40% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Flanders — 46,500 — Awaiting orders.
   - Massena — Milan — 42,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Picardy — 10,000 — Awaiting orders.
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
   • recruit infantry in Rhineland — 790g for 3,000 men under Davout
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
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1584,516)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Lannes(1800,497)  Murat(1825,471)  Soult(1716,322)  Napoleon(1690,418)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,486)  12k(1551,454)  ?(1769,580)  ?(1758,420)  12k(1713,446)  10k(1910,645)
```

```
#0158  look  ->  ok
  (a fresh frame)
view: <run>\frames\0158_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0159  click_at 1609 402  ->  ok
  (clicked at (1609, 402) on MapArea '100' (Control, layer 0))
view: <run>\frames\0159_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 46 px] ──
   Artois
   France  City · Plains / ACTIONS /   Recruit:  73,000 over the ordinance — every levy costs ×1.55 /       Infantry    Napoleon · 3,000 foot · 790g · field levy (pool 80,000) /       Cavalry    Murat commands our horse at Franche-Comte — march him within reach, or give him the order yourself: 'Murat, recruit cavalry'. /       Artillery    No commander of guns serves us — commission Marmont (4500g) a …
   controls: [icon @(535,73)]  <Infantry>  <▸ Build — 7 works>  <Napoleon · 1 AP · this turn>  <Soult · 1 AP · 2 turns>  <Murat · 2 AP · 2 turns>  <Davout · 2 AP · 4 turns>  <Lannes · 2 AP · 4 turns>  <+3 more…>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (54 labels)
```

```
#0160  key alt+m  ->  ok
  (pressed alt+m)
view: <run>\frames\0160_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
── command window, new lines ──
   Map view: political
map: unchanged (54 labels)
```

```
#0161  type what can I do  ->  ok
  (typed and Enter)
view: <run>\frames\0161_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
reply: ok These orders would be carried out today, Sire:
  Ney, attack Mack
  Davout, march to Lorraine
  Soult, fortify
  Napoleon, drill
  recruit infantry in Rhineland — 790g for 3,000 men under Davout
  build supply depot in Rhineland — 300g
Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
For any matter of state, press F1 for the Cabinet.
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 475 px] ──
   Artois
   France  City · Plains / ACTIONS /   Recruit:  73,000 over the ordinance — every levy costs ×1.55 /       Infantry    Napoleon · 3,000 foot · 790g · field levy (pool 80,000) /       Cavalry    Murat commands our horse at Franche-Comte — march him within reach, or give him the order yourself: 'Murat, recruit cavalry'. /       Artillery    No commander of guns serves us — commission Marmont (4500g) a …
   controls: [icon @(535,73)]  <Infantry>  <▸ Build — 7 works>  <Napoleon · 1 AP · this turn>  <Soult · 1 AP · 2 turns>  <Murat · 2 AP · 2 turns>  <Davout · 2 AP · 4 turns>  <Lannes · 2 AP · 4 turns>  <+3 more…>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1257 of 1257 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
   ► what can I do
   These orders would be carried out today, Sire:
   Ney, attack Mack
   Davout, march to Lorraine
   Soult, fortify
   Napoleon, drill
   recruit infantry in Rhineland — 790g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
map: unchanged (54 labels)
```

```
#0162  type Soult, march to Normandy  ->  ok
  (typed and Enter)
view: <run>\frames\0162_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
reply: ok Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
Picardy feeds 22,500; the 56,500 men standing there would lose ~1,844 a turn to short supply.
Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end. "Soult, march to Normandy." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 46 px] ──
   Artois
   France  City · Plains / ACTIONS /   Recruit:  73,000 over the ordinance — every levy costs ×1.55 /       Infantry    Napoleon · 3,000 foot · 790g · field levy (pool 80,000) /       Cavalry    Murat commands our horse at Franche-Comte — march him within reach, or give him the order yourself: 'Murat, recruit cavalry'. /       Artillery    No commander of guns serves us — commission Marmont (4500g) a …
   controls: [icon @(535,73)]  <Infantry>  <▸ Build — 7 works>  <Napoleon · 1 AP · this turn>  <Soult · 1 AP · 2 turns>  <Murat · 2 AP · 2 turns>  <Davout · 2 AP · 4 turns>  <Lannes · 2 AP · 4 turns>  <+3 more…>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1963 of 1963 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
   ► Soult, march to Normandy
   Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 56,500 men standing there would lose ~1,844 a turn to short supply.
   Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end. "Soult, march to Normandy." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map: unchanged (54 labels)
```

```
#0163  click War with the Third Coalition  ->  ok
  (clicked at (3429, 996))
view: <run>\frames\0163_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)', 'war_detail'], region_panel=yes
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) [scrolled 0 of 530 px] ──
   WAR WITH THE THIRD COALITION
   BR
   +5
   FR
   The ledger of one war — its score, its fronts, and the price of peace. Negotiate opens the table, where every court signs for itself. /  / The War with the Third Coalition: France holds Munster of Britain's. / With: Britain + Austria + Russia /  / Score Breakdown   trend ^ rising /   Territory:  +5/40 /   Battles:    0/15 /   Decisive:   0/15 /   Capital:    0/30 /   Campaign:   0/10 /   Blood:    …
   controls: [icon @(3139,276)]  [Negotiate with Britain]  [Negotiate with Austria]  [Negotiate with Russia]  [Open Settlement]  [Request Terms](disabled: Britain leads a league that is not yet spent, Sire — it names no terms while it can still )
── RegionPanel (layer 26) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1963 of 1963 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
   Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 56,500 men standing there would lose ~1,844 a turn to short supply.
   Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end. "Soult, march to Normandy." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map: unchanged (54 labels)
```

```
#0164  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0164_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1963 of 1963 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 56,500 men standing there would lose ~1,844 a turn to short supply.
   Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end. "Soult, march to Normandy." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map: unchanged (54 labels)
```

```
#0165  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0165_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── RegionPanel (layer 26) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1963 of 1963 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 56,500 men standing there would lose ~1,844 a turn to short supply.
   Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end. "Soult, march to Normandy." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map: unchanged (54 labels)
```

```
#0166  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0166_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── DiplomacyWizard (layer 110) [scrolled 295 of 838 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── RegionPanel (layer 26) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1963 of 1963 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 56,500 men standing there would lose ~1,844 a turn to short supply.
   Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end. "Soult, march to Normandy." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map: unchanged (54 labels)
```

```
#0167  click Britain  ->  ok
  (clicked at (1825, 380))
view: <run>\frames\0167_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── DiplomacyWizard (layer 110) [scrolled 0 of 442 px, 0 of 267 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War with the Third Coalition   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Sire, the field reads +5 and no road carries. Propose Peace comes nearest at 2 of 50; her loyalty to the league — she has no reason of her own to break …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Unlikely]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── RegionPanel (layer 26) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1963 of 1963 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Soult begins march to Normandy. Route: Picardy → Artois → Normandy. Moves to Picardy.
   Picardy feeds 22,500; the 56,500 men standing there would lose ~1,844 a turn to short supply.
   Picardy lies outside the camp — this takes 46,500 men out of it; the 2-turn count resets at the turn's end. "Soult, march to Normandy." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map: unchanged (54 labels)
```

```
#0168  click Propose Peace  ->  ok
  (clicked at (1825, 588))
view: <run>\frames\0168_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 420 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 2 - REJECT / Key advantage: Base Disposition / Key obstacle: Coalition Loyalty /  / War Summary / The War with the Third Coalition: France holds Munster of Britain's. / War score: 5 -> (Territory +5) / Settlement: White Peace / …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2009 of 2009 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
map: unchanged (54 labels)
```

```
#0169  click Adjust terms  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0169_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 398 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Britain - Separate settlement / Covered enemies: Britain / Still at war: Austria, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Britain -8/50. / Treasury 800 gold: committed 0 / reserve 500 / remaining 300 / Sire, this settlement of the War with the Third Coalition — the table …
   The table /   * Britain ▸ - Holding out (-8/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh declines for Britain: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents, and arithmetic does not sign papers it cannot balance. /       + Add demand / Britain is the holdout. / ▸ Britain won't accept these terms yet …
   Britain:
   Coverage:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, a white peace for the War with the Third Coalition — the table with Britain cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered  …
   controls: <Britain ▸>  <+ Add demand>  [Demand more of Britain]  [Ease Britain]  [Bring Austria to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2030 of 2030 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
   Directing Talleyrand: adjust terms
map: unchanged (54 labels)
```

```
#0170  click Back Out  ->  ok
  (clicked at (2250, 969))
view: <run>\frames\0170_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +5 ↑
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0171  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0171_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 640 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early December 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+471 next turn)
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
   ► propose peace with Britain
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0172  click ADMIRALTY  ->  ok
  (clicked at (2049, 283))
view: <run>\frames\0172_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 970 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Early December 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire: 40,000 men on the Channel coast, 2 turns at war with Britain, stage a descent — no order; a march out resets the count. Her blockade on you lifts; a won Diversion can open the Strait for up to 2 turns …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Britain
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0173  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0173_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +5 ↑
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► propose peace with Britain
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0174  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0174_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Britain
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0175  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0175_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 384 px] ──
   LOAD GAME
   controls: [Autosave - Turn 20 (Turn 20)]  [replay_clock (Turn 19)]  [replay_firststep (Turn 4)]  [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Britain
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (54 labels)
```

```
#0176  click replay_mission  ->  ok
  (clicked at (1825, 606))
view: <run>\frames\0176_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/6
   Threat 70 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:13
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1455 of 1455 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
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
   Loaded: replay_mission
   ════════════════════════════════════
   MORNING DISPATCH — Turn 14
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+828 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
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
   • Ney, march to Swabia
   • Davout, fortify
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
#0177  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0177_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1455 of 1455 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
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
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0178  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0178_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 295 of 838 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0179  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0179_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 582 of 822 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (12)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Austria  —  Peace  |  -40 (Hostile)  [MISSION]]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0180  click Austria  ->  ok
  (clicked at (1825, 442))
view: <run>\frames\0180_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 0 of 583 px] ──
   THE CABINET — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -40 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. Talleyrand is already at their court, Sire — net +9 a turn. / Talleyrand: "Austria stands on the Emperor's …
   Their design is aimed at France herself.
   Their price is 1320g — the treasury holds 800g.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile (+20 over 4 turns) — +32 earned, -15 from Prussia's declaration, drift +3]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1392g to buy off in turn).](disabled: Their price is 1320g — the treasury holds 800g.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0181  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0181_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0182  scroll 1830 600 down 16  ->  ok
  (scrolled down 16 at (1830, 600))
view: <run>\frames\0182_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 580 of 820 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (12)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Austria  —  Peace  |  -40 (Hostile)  [MISSION]]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0183  click Prussia  ->  ok
  (clicked at (1825, 484))
view: <run>\frames\0183_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 288 px, 0 of 558 px] ──
   THE CABINET — Prussia
   DP: 6
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: -10 (Wary) /  / "Prussia maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: Relations must improve before proposals will find purchase. Improve Relations is shut while Talleyrand is at Austria's court — recall Talleyrand from Austria first (the …
   Their price is 1128g — the treasury holds 800g.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3).]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Armed Neutrality next (600g to buy off in turn).](disabled: Their price is 1128g — the treasury holds 800g.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0184  scroll 1830 640 down 10  ->  ok
  (scrolled down 10 at (1830, 640))
view: <run>\frames\0184_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 288 px, 326 of 566 px] ──
   THE CABINET — Prussia
   DP: 6
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: -10 (Wary) /  / "Prussia maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: Relations must improve before proposals will find purchase. Improve Relations is shut while Talleyrand is at Austria's court — recall Talleyrand from Austria first (the …
   A vassalage of Prussia needs a war (a dictated peace) or open borders and above — we stand at Peace.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)](disabled: A vassalage of Prussia needs a war (a dictated peace) or open borders and above — we stand)  [Declare War (1 DP)]  [Send Ultimatum (2 DP)]  [Improve Relations (1 DP)  —  +8 relation/turn](disabled: Talleyrand is at Austria's court — F1 → Austria → Cancel)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0185  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0185_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
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
#0186  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0186_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 14
   AUSTRIA / ──────────────────────────── / - Archduke Charles moves to Tyrol / - Archduke Charles attacks Deroy /     Battle of Franconia /     Archduke Charles: 2,290 casualties, 51,710 remaining /     Deroy: 7,985 casualties, 14,015 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) — and advances into Franconia /     ⚔ View the field /     --- Berthier's Report --- /  …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (4)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,626 (+826 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Other: +1337g | Upkeep: -2792g | Net: +826g
   Treasury: 1,626g
   Actions refreshed: 4/4
   Supply shortage at Franconia: Bernadotte loses 200 troops
   Supply shortage at Franconia: Archduke Charles loses 1,012 troops
   Austria and France are at peace — Talleyrand is home.
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1838,471)  Deroy(1865,501)  Dumonceau(1755,322)  Massena(1910,589)  ?(2068,435)  ?(1959,404)  ?(1860,560)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1788,425)  12k(1693,420)  10k(1910,645)
```

```
#0187  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0187_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 68 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (4)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3220,64)]  [icon: Blockade — Britain closes our ports @(3262,64)]  [icon: Envoy from Prussia @(3304,64)]  [icon: Envoy from Ottoman Empire @(3346,64)]  [icon: Envoy from Portugal @(3388,64)]  [Talleyrand at Austria — Improving Relations]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:14
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1762 of 1762 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,626 (+826 next turn)
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
   [...earlier messages trimmed...]
   Actions refreshed: 4/4
   Supply shortage at Franconia: Bernadotte loses 200 troops
   Supply shortage at Franconia: Archduke Charles loses 1,012 troops
   Austria and France are at peace — Talleyrand is home.
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 15
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,626g (+826 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 16,800 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Franconia — 49,147 [confirmed]
   Deroy — Munich — small force [partial]
   Mack — Swabia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply shortage at Franconia: Bernadotte loses 200 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   Swabia passes from Bavaria to Austria.
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Austria and France are at peace — Talleyrand is home.
   An envoy from Switzerland has arrived with a petition.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 4 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - Ottoman Empire — Open Borders Agreement
   - Portugal — Open Borders Agreement
   - ...and 1 more
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0188  click Envoys  ->  ok
  (clicked at (3401, 18))
view: <run>\frames\0188_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 270 px] ──
   PENDING ENVOYS (4)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 14
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   THE COURTS WRITE (2)
   Ottoman Empire and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Ottoman Empire
   Proposal
   Turn 14
   Incoming proposal: Open Borders Agreement
   Reis Efendi, serene and unhurried: "The Porte watches the star of France climb ever higher and, being an old admirer of whatever endures, would sooner arrange itself gracefully beneath so great a light than stand across its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   or click the letter to reply in full
   WAITING
   Portugal
   Proposal
   Turn 14
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "A kingdom as modest as ours does not measure itself against the Empire's shadow, and Lisbon would far rather reach an understanding than be caught standing in its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Portugal pays you 60 gold at the signing
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1762 of 1762 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0189  click#1 Accept  ->  ok
  (clicked at (1433, 635))
view: <run>\frames\0189_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 51 px] ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 14
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   A SMALL COURT WRITES (1)
   Portugal writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Portugal
   Proposal
   Turn 14
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "A kingdom as modest as ours does not measure itself against the Empire's shadow, and Lisbon would far rather reach an understanding than be caught standing in its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Portugal pays you 60 gold at the signing
   or click the letter to reply in full
   WAITING
   Switzerland
   Proposal
   Turn 15
   Incoming proposal: Client's Petition
   Terms: Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +2 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. · Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now +0); nothing is charged. · Left unanswered at the turn's end, the  …
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3284,62)]  [Talleyrand at Austria — Improving Relations]  [icon: The Moniteur is out @(3602,62)]  [icon: Treaty with Ottoman @(3641,62)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,626 (+845 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
map: unchanged (55 labels)
```

```
#0190  click Accept  ->  ok
  (clicked at (1433, 635))
view: <run>\frames\0190_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 14
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   WAITING
   Switzerland
   Proposal
   Turn 15
   Incoming proposal: Client's Petition
   Terms: Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +2 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. · Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now +0); nothing is charged. · Left unanswered at the turn's end, the  …
   A client's petition is granted or refused in full — open to decide.
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3263,62)]  [Talleyrand at Austria — Improving Relations]  [icon: The Moniteur is out @(3581,62)]  [icon: Treaty with Ottoman @(3623,62)]  [icon: Treaty with Portugal @(3651,62)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,686 (+854 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (55 labels)
```

```
#0191  click Open ▸  ->  ERROR: 2 controls match "Open ▸" — pick one with click#N
  candidates: #1 [Open ▸] on MailboxPanel @(2184,294) | #2 [Open ▸] on MailboxPanel @(2184,429)
view: <run>\frames\0191_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (55 labels)
```

```
#0192  click Accept  ->  ERROR: no visible control's text holds "Accept"
view: <run>\frames\0192_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (55 labels)
```

```
#0193  click#1 Open ▸  ->  ok
  (clicked at (2184, 294))
view: <run>\frames\0193_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 46 px] ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade /  / Hardenberg, stiffly: "Berlin wil …
   controls: [Accept]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,686 (+854 next turn)
   Inf:
   82,375
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
map: unchanged (55 labels)
```

```
#0194  click Accept  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0194_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +2 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a  …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,686 (+864 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
map: unchanged (55 labels)
```

```
#0195  click Refuse  ->  ok
  (clicked at (1829, 687))
view: <run>\frames\0195_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 68 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3220,64)]  [Talleyrand at Austria — Improving Relations]  [icon: The Moniteur is out @(3538,64)]  [icon: Treaty with Ottoman @(3580,64)]  [icon: Treaty with Portugal @(3622,64)]  [icon: Treaty with Prussia @(3651,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:14
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,686 (+864 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0196  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0196_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,686 (+864 next turn)
   Inf:
   82,375
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
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0197  scroll 1830 600 down 24  ->  ok
  (scrolled down 24 at (1830, 600))
view: <run>\frames\0197_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 733 of 773 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sweden  —  Peace  |  -59 (Hostile)]  [Naples  —  Peace  |  -29 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Saxony  —  Peace  |  -10 (Wary)]  [Hanover  —  Peace  |  -49 (Hostile)]  [Hesse  —  Peace  |  0 (Neutral)]  [Papal States  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0198  scroll 1830 600 up 6  ->  ok
  (scrolled up 6 at (1830, 600))
view: <run>\frames\0198_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 488 of 768 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Bavaria  —  Alliance  |  +59 (Friendly)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Austria  —  Peace  |  -39 (Hostile)]  [Sweden  —  Peace  |  -59 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0199  click Austria  ->  ok
  (clicked at (1825, 586))
view: <run>\frames\0199_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 0 of 445 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -39 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Austria stands on the Emperor's r …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1320g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0200  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0200_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0201  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0201_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0202  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0202_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 384 px] ──
   LOAD GAME
   controls: [Autosave - Turn 15 (Turn 15)]  [replay_clock (Turn 19)]  [replay_firststep (Turn 4)]  [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0203  scroll 1830 500 down 6  ->  ok
  (scrolled down 6 at (1830, 500))
view: <run>\frames\0203_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 174 of 384 px] ──
   LOAD GAME
   controls: [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [replay_spain (Turn 11)]  [replay_detour (Turn 19)]  [replay_peril (Turn 8)]  [replay_beira (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0204  click replay_spain  ->  ok
  (clicked at (1825, 480))
view: <run>\frames\0204_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:10
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
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
   Loaded: replay_spain
   ════════════════════════════════════
   MORNING DISPATCH — Turn 11
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
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+10)
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
#0205  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0205_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
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
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0206  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0206_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 295 of 838 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +2 (Neutral)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0207  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0207_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 582 of 822 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0208  scroll 1830 600 up 8  ->  ok
  (scrolled up 8 at (1830, 600))
view: <run>\frames\0208_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 231 of 814 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +2 (Neutral)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0209  click Spain  ->  ok
  (clicked at (1825, 587))
view: <run>\frames\0209_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 178 px, 0 of 503 px] ──
   THE CABINET — Spain
   DP: 5
   TALLEYRAND'S ASSESSMENT — SPAIN / Status: Alliance   Relation: +2 (Neutral) /  / "Our alliance with Spain holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Our alliance with Spain frays, Sire — relations stand at 2, short of the 40 it holds on. Talleyrand recommends: Reassure Ally — +4 a turn on relations, 1 DP a turn. /  / KEY FACTORS /   + Base wil …
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Reassure Ally (1 DP)  —  +4 relation/turn]  [Propose Vassal (3 DP)  —  Unlikely]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0210  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0210_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0211  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0211_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 295 of 838 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +2 (Neutral)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0212  click Britain  ->  ok
  (clicked at (1825, 380))
view: <run>\frames\0212_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 442 px, 0 of 267 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War with the Third Coalition   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — the court sees no reason to sign at +0: Propose Peace stands at 21 of 50; it wants her loyalty to the league — she has no reason of he …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Doubtful]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Unlikely]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
#0213  click Propose Peace  ->  ok
  (clicked at (1825, 588))
view: <run>\frames\0213_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 442 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 21 - REJECT / Key advantage: Base Disposition / Key obstacle: Coalition Loyalty /  / War Summary / The War with the Third Coalition: nothing taken yet on either side. / War score: 0 -> / Settlement: White Peace / Objective: Def …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1544 of 1544 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
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
   ► propose peace with Britain
map: unchanged (53 labels)
```

```
#0214  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0214_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:10
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1609 of 1609 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (53 labels)
```

```
#0215  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0215_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1609 of 1609 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
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
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (53 labels)
```

```
#0216  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0216_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (53 labels)
```

```
#0217  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0217_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 174 of 384 px] ──
   LOAD GAME
   controls: [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [replay_spain (Turn 11)]  [replay_detour (Turn 19)]  [replay_peril (Turn 8)]  [replay_beira (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose peace with Britain
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (53 labels)
```

```
#0218  click replay_detour  ->  ok
  (clicked at (1825, 528))
view: <run>\frames\0218_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Vienna
   0 →
   T:18
   controls: [THIRD COALITION  ▸]  [War for Vienna]  [War for Vienna — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1455 of 1455 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+775 next turn)
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
   Loaded: replay_detour
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 29 regions. Treasury: 800g (+775 by the accounts)
   The courts at war hold 22 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Franconia — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Vienna — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Bohemia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, march to Swabia
   • Davout, fortify
   • recruit infantry in Rhineland — 727g for 3,000 men under Davout
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
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Austria(2055,548)  France(1600,542)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,481)  Mack(2024,451)  Soult(1931,451)  Bernadotte(1971,425)  Deroy(1955,399)  Napoleon(2109,501)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Lannes(1800,497)  Murat(1825,471)  Massena(1910,589)  ?(2072,429)  25k(2117,556)  ?(1959,372)  ?(1860,560)  ?(1893,372)  25k(1595,497)  12k(1551,454)  ?(1769,580)  12k(1716,420)  10k(1910,645)
```

```
#0219  type Soult, march to Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0219_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
reply: ok The direct road to Vienna via Bohemia is closed by the truce with Austria; the lawful road is 7 provinces, 7 turns, through Prussia and Russia — march, or cancel?
── ClarificationPopup (layer 102) ──
   BERTHIER ASKS:
   "The direct road to Vienna via Bohemia is closed by the truce with Austria; the lawful road is 7 provinces, 7 turns, through Prussia and Russia — march, or cancel?"
   controls: [March (1 AP)]  [Cancel Order]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+775 next turn)
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
   ► Soult, march to Vienna
   Berthier requests clarification...
map: unchanged (54 labels)
```

```
#0220  click Cancel Order  ->  ok
  (clicked at (1829, 524))
view: <run>\frames\0220_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Vienna
   0 →
   T:18
   controls: [THIRD COALITION  ▸]  [War for Vienna]  [War for Vienna — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1587 of 1587 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+775 next turn)
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
map: unchanged (54 labels)
```

```
#0221  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0221_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1587 of 1587 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+775 next turn)
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
   ► Soult, march to Vienna
   Berthier requests clarification...
   Order cancelled.
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (54 labels)
```

```
#0222  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0222_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1587 of 1587 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Soult, march to Vienna
   Berthier requests clarification...
   Order cancelled.
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (54 labels)
```

```
#0223  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0223_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 174 of 384 px] ──
   LOAD GAME
   controls: [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [replay_spain (Turn 11)]  [replay_detour (Turn 19)]  [replay_peril (Turn 8)]  [replay_beira (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1587 of 1587 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Soult, march to Vienna
   Berthier requests clarification...
   Order cancelled.
   Berthier nods. "Very well, Sire — the order is withdrawn."
map: unchanged (54 labels)
```

```
#0224  click replay_peril  ->  ok
  (clicked at (1825, 576))
view: <run>\frames\0224_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Hungary
   +30 →
   T:7
   controls: [THIRD COALITION  ▸]  [War for Hungary]
── BottomLeftUI (layer 0) [scrolled 1653 of 1653 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,703 next turn)
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
   Loaded: replay_peril
   ════════════════════════════════════
   MORNING DISPATCH — Turn 8
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 30 regions. Treasury: 800g (+1,703 by the accounts)
   The courts at war hold 26 regions. Estimated enemy strength: 117% of French forces (an estimate — 4 of 5 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Vienna — 24,000 — Awaiting orders. Morale:20%
   ⚠ Morale failing (20) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Murat — Vienna — 22,000 — Awaiting orders. Morale:20%
   ⚠ Morale failing (20) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Lannes — Vienna — 18,000 — Awaiting orders. Morale:20%
   ⚠ Morale failing (20) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Soult — Hungary — 10,000 — Awaiting orders.
   ⚠ IN PERIL — an enemy force of ~32,000 shares the field (Hungary).
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Buxhowden — Hungary — 32,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke Charles — Carniola — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Kutuzov — Moravia — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Hungary) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Hungary) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Hungary) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Soult, attack Buxhowden
   • Ney, march to Bohemia
   • recruit infantry in Rhineland — 638g for 3,000 men under Davout
   • build supply depot in Vienna — 300g
   Ask 'what if Soult attacks Buxhowden' first — it names who marches with Soult, and costs nothing.
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
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1676,531)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(2016,642)  Archduke Charles(2016,615)  Ney(2096,501)  Lannes(2109,475)  Murat(2121,449)  ?(1959,325)  Brunswick(1958,287)  ?(2195,487)  Kutuzov(2194,448)  Soult(2118,575)  Buxhowden(2143,549)  ?(1859,469)  Mack(1853,430)  Davout(1830,397)  ?(1965,579)  Archduke John(1948,540)  Napoleon(1752,436)  Massena(1910,589)  ?(2068,435)  25k(2066,556)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,497)  12k(1551,454)  ?(1769,574)  12k(1685,416)  10k(1910,645)
```

```
#0225  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0225_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1741 of 1741 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,703 next turn)
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
   ⚠ Soult's corps (10,000) stands in peril — an enemy force of ~32,000 shares the field (Hungary). 3 corps stand below 40% morale beside Buxhowden (32,000, Hungary) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (59 labels)
```

```
#0226  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0226_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1741 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ⚠ Soult's corps (10,000) stands in peril — an enemy force of ~32,000 shares the field (Hungary). 3 corps stand below 40% morale beside Buxhowden (32,000, Hungary) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (59 labels)
```

```
#0227  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0227_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 174 of 384 px] ──
   LOAD GAME
   controls: [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [replay_spain (Turn 11)]  [replay_detour (Turn 19)]  [replay_peril (Turn 8)]  [replay_beira (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1741 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ⚠ Soult's corps (10,000) stands in peril — an enemy force of ~32,000 shares the field (Hungary). 3 corps stand below 40% morale beside Buxhowden (32,000, Hungary) — end the turn anyway?
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (59 labels)
```

```
#0228  click replay_beira  ->  ok
  (clicked at (1825, 615))
view: <run>\frames\0228_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   T:6
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1565 of 1565 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Loaded: replay_beira
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+828 by the accounts)
   The courts at war hold 32 regions. Estimated enemy strength: 44% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Dictated Terms (+40)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+20)
   War Purpose: Defense vs Portugal (War) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
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
#0229  click War with  ->  ok
  (clicked at (3429, 996))
view: <run>\frames\0229_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) [scrolled 0 of 508 px] ──
   WAR WITH THE THIRD COALITION
   BR
   0
   FR
   The ledger of one war — its score, its fronts, and the price of peace. Negotiate opens the table, where every court signs for itself. /  / The War with the Third Coalition: nothing taken yet on either side. / With: Britain + Austria + Russia + Portugal /  / Score Breakdown   trend = stable /   Territory:  0/40 /   Battles:    0/15 /   Decisive:   0/15 /   Capital:    0/30 /   Campaign:   0/10 /    …
   controls: [icon @(3139,276)]  [Negotiate with Britain]  [Negotiate with Austria]  [Negotiate with Portugal]  [Negotiate with Russia]  [Open Settlement]  [Request Terms](disabled: Britain leads a league that is not yet spent, Sire — it names no terms while it can still )
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0230  click Open Settlement  ->  ok
  (clicked at (2875, 784))
view: <run>\frames\0230_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 91 px, 0 of 552 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 33/50, Russia 15/50. / Treasury 800 gold: committed 0 / reserve 500 / remaining 300 / Sire, this settlement of t …
   The table /   * Austria ▸ - Holding out (33/50) White peace /       Blocker: National design /       Metternich regrets that Austria must remain… unconvinced — it would seal their national design out of reach. /       + Add demand /   * Britain ▸ - Holding out (-8/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh declines for Britain: it claims no victory, but a whole-war  …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, a white peace for the War with the Third Coalition — the table with Austria + Britain + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still n …
   controls: <Austria ▸>  <+ Add demand>  <Britain ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  <Grant>  <Decline>  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1587 of 1587 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Opening settlement review for Britain
map: unchanged (53 labels)
```

```
#0231  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0231_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 157 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 41/50, Russia 23/50. / Treasury 800 gold: committed 300 / reserve 500 / remaining 0 / Sire, this settlement of t …
   The table /   * Austria ▸ - Holding out (close) (41/50) Conceded: 100g /       Blocker: National design /       Austria Holding out → Holding out (close) /       Metternich allows that Austria is… persuadable — though the terms cut against their national design. /       Conceded · France pays 100 gold  [-][+]  Remove /       + Add demand /   * Britain ▸ - Holding out (0/50) Conceded: 100g /        …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <Remove>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
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
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0232  click Ease Britain  ->  ok
  (clicked at (1630, 656))
view: <run>\frames\0232_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 135 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 43/50, Russia 25/50. / Treasury 800 gold: committed 400 / reserve 400 / remaining 0 / Sire, this settlement of t …
   The table /   * Austria ▸ - Holding out (close) (43/50) Conceded: 100g /       Blocker: National design /       Metternich allows that Austria is… persuadable — though the terms cut against their national design. /       Conceded · France pays 100 gold  [-][+]  Remove /       + Add demand /   * Britain ▸ - Holding out (4/50) Conceded: 200g /       Blocker: Settlement legitimacy /       Castlereagh …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <Remove>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1631 of 1631 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0233  click#1 + Add demand  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0233_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 490 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 43/50, Russia 25/50. / Treasury 800 gold: committed 400 / reserve 400 / remaining 0 / Sire, this settlement of t …
   The table /   * Austria ▸ - Holding out (close) (43/50) Conceded: 100g /       Blocker: National design /       Metternich allows that Austria is… persuadable — though the terms cut against their national design. /       Conceded · France pays 100 gold  [-][+]  Remove /       − Add demand /         Demands of Austria /           Take Tyrol from Austria ▾ /             — Tyrol sits beside what we a …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <− Add demand>  <Take Tyrol from Austria>  <▾>  <Demand 200 gold from Austria>  <Demand 100 gold a turn from Austria for 3 turns>  <Vassalize Austria>  <Subjugate Austria>  <Force Austria into alliance>  <Austria joins the Continental System>  <▸ Offers to Austria (2)>  <Britain ▸>  <Remove>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1631 of 1631 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Opening settlement review for Britain
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0234  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0234_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 135 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Russia 33/50. / Treasury 800 gold: committed 700 / reserve 100 / remaining 0 / Sire, this settlement of the War with the …
   The table /   * Austria ▸ - Will sign (51/50) Conceded: 200g /       Austria Holding out (close) → Will sign /       Metternich signals that Austria will sign the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia. /       Conceded · France pays 200 gold  [-][+]  Remove /       + Add demand /   * Britain ▸ - Holding out (12/50) Conceded: 300g /       Blocker …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <Remove>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Separate peace with Austria — alone: 47 (Uncertain — a counter is likely)]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1653 of 1653 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0235  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0235_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 135 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Russia 35/50. / Treasury 800 gold: committed 800 / reserve 0 / remaining 0 / Sire, this settlement of the War with the T …
   The table /   * Austria ▸ - Will sign (55/50) Conceded: 300g /       Metternich signals that Austria will sign the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia. /       Conceded · France pays 300 gold  [-][+]  Remove /       + Add demand /   * Britain ▸ - Holding out (14/50) Conceded: 300g /       Blocker: Settlement legitimacy /       Castlereagh decl …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <Remove>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Separate peace with Austria — alone: 48 (Uncertain — a counter is likely)]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0236  click More generous  ->  ok
  (clicked at (1689, 969))
view: <run>\frames\0236_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 113 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Russia 35/50. / Treasury 800 gold: committed 800 / reserve 0 / remaining 0 / Sire, this settlement of the War with the T …
   The table /   * Austria ▸ - Will sign (55/50) Conceded: 300g /       Metternich signals that Austria will sign the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia. /       Conceded · France pays 300 gold  [-][+]  Remove /       + Add demand /   * Britain ▸ - Holding out (14/50) Conceded: 300g /       Blocker: Settlement legitimacy /       Castlereagh decl …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <Remove>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Separate peace with Austria — alone: 48 (Uncertain — a counter is likely)]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0237  click#2 Add demand  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0237_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 135 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Russia 35/50. / Treasury 800 gold: committed 800 / reserve 0 / remaining 0 / Sire, this settlement of the War with the T …
   The table /   * Austria ▸ - Will sign (55/50) Conceded: 300g /       Metternich signals that Austria will sign the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia. /       Conceded · France pays 300 gold  [-][+]  Remove /       + Add demand /   * Britain ▸ - Holding out (14/50) Conceded: 300g /       Blocker: Settlement legitimacy /       Castlereagh decl …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <Remove>  <− Add demand>  <▸ Demands of Britain (5)>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Separate peace with Austria — alone: 48 (Uncertain — a counter is likely)]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0238  click Demands of Britain  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0238_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 356 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Russia 35/50. / Treasury 800 gold: committed 800 / reserve 0 / remaining 0 / Sire, this settlement of the War with the T …
   The table /   * Austria ▸ - Will sign (55/50) Conceded: 300g /       Metternich signals that Austria will sign the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia. /       Conceded · France pays 300 gold  [-][+]  Remove /       + Add demand /   * Britain ▸ - Holding out (14/50) Conceded: 300g /       Blocker: Settlement legitimacy /       Castlereagh decl …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <Remove>  <− Add demand>  <Take Wessex from Britain>  <▾>  <Demand 300 gold from Britain>  <Demand 100 gold a turn from Britain for 3 turns>  <Force Britain into alliance>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Separate peace with Austria — alone: 48 (Uncertain — a counter is likely)]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (53 labels)
```

```
#0239  click Harsher terms  ->  ok
  (clicked at (1408, 969))
view: <run>\frames\0239_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 179 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 47/50, Russia 27/50. / Treasury 800 gold: committed 500 / reserve 300 / remaining 0 / Sire, this settlement of t …
   The table /   * Austria ▸ - Holding out (close) (47/50) Conceded: 200g /       Blocker: National design /       Austria Will sign → Holding out (close) /       Metternich allows that Austria is… persuadable — though the terms cut against their national design. /       Conceded · France pays 200 gold  [-][+]  Remove /       + Add demand /   * Britain ▸ - Holding out (6/50) Conceded: 200g /       Bl …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <Remove>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1720 of 1720 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Directing Talleyrand: settlement dial harsher
map: unchanged (53 labels)
```

```
#0240  click Harsher terms  ->  ok
  (clicked at (1408, 969))
view: <run>\frames\0240_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 113 px, 0 of 464 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 39/50, Russia 19/50. / Treasury 800 gold: committed 200 / reserve 500 / remaining 100 / Sire, this settlement of …
   The table /   * Austria ▸ - Holding out (close) (39/50) Conceded: 100g /       Blocker: National design /       Metternich allows that Austria is… persuadable — though the terms cut against their national design. /       Conceded · France pays 100 gold  [-][+]  Remove /       + Add demand /   * Britain ▸ - Holding out (-2/50) Conceded: 100g /       Blocker: Settlement legitimacy /       Castlereag …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <Remove>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1742 of 1742 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Directing Talleyrand: settlement dial harsher
map: unchanged (53 labels)
```

```
#0241  click Harsher terms  ->  ok
  (clicked at (1408, 969))
view: <run>\frames\0241_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 113 px, 0 of 442 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Separate settlement / Covered enemies: Austria, Britain, Russia / Still at war: Portugal / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 33/50, Russia 13/50. / Treasury 800 gold: committed 0 / reserve 500 / remaining 300 / Sire, this settlement of t …
   The table /   * Austria ▸ - Holding out (33/50) White peace /       Blocker: National design /       Austria Holding out (close) → Holding out /       Metternich regrets that Austria must remain… unconvinced — the terms cut against their national design. /       + Add demand /   * Britain ▸ - Holding out (-8/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh declines for Br …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War with the Third Coalition — the table with Austria + Britain + Russia cannot be ratified now: the fortunes of war do not yet compel them — at their scor …
   controls: <Austria ▸>  <+ Add demand>  <Britain ▸>  <+ Add demand>  <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1764 of 1764 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Directing Talleyrand: settlement dial harsher
map: unchanged (53 labels)
```

```
#0242  click Back Out  ->  ok
  (clicked at (2250, 969))
view: <run>\frames\0242_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:6
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1830 of 1830 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0243  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0243_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1830 of 1830 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
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
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0244  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0244_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1830 of 1830 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0245  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0245_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 174 of 384 px] ──
   LOAD GAME
   controls: [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [replay_spain (Turn 11)]  [replay_detour (Turn 19)]  [replay_peril (Turn 8)]  [replay_beira (Turn 6)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1830 of 1830 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0246  click replay_rump  ->  ERROR: no visible control's text holds "replay_rump"
view: <run>\frames\0246_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 174 of 384 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1830 of 1830 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0247  scroll 1830 500 down 10  ->  ok
  (scrolled down 10 at (1830, 500))
view: <run>\frames\0247_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 384 of 384 px] ──
   LOAD GAME
   controls: [replay_beira (Turn 6)]  [replay_rump (Turn 11)]  [replay_sanctuary (Turn 5)]  [replay_letters (Turn 2)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1830 of 1830 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0248  click replay_rump  ->  ok
  (clicked at (1825, 462))
view: <run>\frames\0248_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:10
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
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
   Loaded: replay_rump
   ════════════════════════════════════
   MORNING DISPATCH — Turn 11
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
   - Murat — Flanders — 22,000 — Awaiting orders.
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
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(1859,469)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1813,497)  Murat(1716,322)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1787,425)  12k(1693,420)  10k(1910,645)
```

```
#0249  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0249_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
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
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0250  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0250_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 295 of 838 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0251  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0251_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 582 of 822 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0252  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0252_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 763 of 843 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Saxony  —  Peace  |  -10 (Wary)]  [Hanover  —  Peace  |  -50 (Hostile)]  [Hesse  —  Peace  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0253  click Hanover  ->  ok
  (clicked at (1825, 581))
view: <run>\frames\0253_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 493 px] ──
   THE CABINET — Hanover
   DP: 5
   TALLEYRAND'S ASSESSMENT — HANOVER / Status: Peace   Relation: -50 (Hostile) / Hanover holds 1 province (Osnabruck); the rest are Prussia's. /  / "Relations with Hanover remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the dipl …
   Relations with Hanover stand at -50; an Open Borders needs -20.
   A vassalage of Hanover needs a war (a dictated peace) or open borders and above — we stand at Peace.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Propose Open Borders (1 DP)  —  Unlikely](disabled: Relations with Hanover stand at -50; an Open Borders needs -20.)  [Propose Vassal (3 DP)](disabled: A vassalage of Hanover needs a war (a dictated peace) or open borders and above — we stand)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0254  scroll 1830 640 down 10  ->  ok
  (scrolled down 10 at (1830, 640))
view: <run>\frames\0254_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 493 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0255  scroll 1830 560 down 10  ->  ok
  (scrolled down 10 at (1830, 560))
view: <run>\frames\0255_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 266 of 480 px] ──
   THE CABINET — Hanover
   DP: 5
   TALLEYRAND'S ASSESSMENT — HANOVER / Status: Peace   Relation: -50 (Hostile) / Hanover holds 1 province (Osnabruck); the rest are Prussia's. /  / "Relations with Hanover remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the dipl …
   No alliance to undermine
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Send Ultimatum (2 DP)]  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn](disabled: No alliance to undermine)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0256  scroll 1830 560 up 2  ->  ok
  (scrolled up 2 at (1830, 560))
view: <run>\frames\0256_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 197 of 478 px] ──
   THE CABINET — Hanover
   DP: 5
   TALLEYRAND'S ASSESSMENT — HANOVER / Status: Peace   Relation: -50 (Hostile) / Hanover holds 1 province (Osnabruck); the rest are Prussia's. /  / "Relations with Hanover remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the dipl …
   Prussia holds Hanover, Hanover's capital; this purpose scores only while we hold it.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Declare War (1 DP)](disabled: Prussia holds Hanover, Hanover's capital; this purpose scores only while we hold it.)  [Send Ultimatum (2 DP)]  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0257  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0257_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0258  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0258_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0259  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0259_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 384 of 384 px] ──
   LOAD GAME
   controls: [replay_beira (Turn 6)]  [replay_rump (Turn 11)]  [replay_sanctuary (Turn 5)]  [replay_letters (Turn 2)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0260  scroll 1830 500 down 20  ->  ok
  (scrolled down 20 at (1830, 500))
view: <run>\frames\0260_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 384 of 384 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1499 of 1499 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (55 labels)
```

```
#0261  click replay_sanctuary  ->  ok
  (clicked at (1825, 510))
view: <run>\frames\0261_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Vienna
   +25 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Vienna]
── BottomLeftUI (layer 0) [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,110 next turn)
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
   Loaded: replay_sanctuary
   ════════════════════════════════════
   MORNING DISPATCH — Turn 5
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 29 regions. Treasury: 800g (+1,110 by the accounts)
   The courts at war hold 27 regions. Estimated enemy strength: 58% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Vienna — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Kutuzov — Moravia — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Dictated Terms (+45)
   War Purpose: Defense vs Russia (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Mack
   • Davout, march to Lorraine
   • recruit infantry in Rhineland — 727g for 3,000 men under Davout
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
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2130,605)  France(1600,542)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  Murat(2109,501)  ?(1959,325)  Brunswick(1958,287)  ?(2195,487)  Kutuzov(2194,448)  ?(1859,469)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1813,497)  Massena(1910,589)  ?(2068,435)  25k(2109,556)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,497)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,645)
```

```
#0262  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0262_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,110 next turn)
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
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (57 labels)
```

```
#0263  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0263_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 295 of 838 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (57 labels)
```

```
#0264  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0264_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 582 of 822 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (11)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (57 labels)
```

```
#0265  scroll 1830 600 up 8  ->  ok
  (scrolled up 8 at (1830, 600))
view: <run>\frames\0265_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 231 of 814 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (57 labels)
```

```
#0266  click Austria  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0266_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 442 px, 0 of 336 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War for Vienna   Relation: -80 (Hostile) /  / "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." / Recommendation: Sire, Propose Armistice carries today — 58 of 50. It costs 1 DP. A truce keeps the ledger (+25 stands, the war 4 turns old) and …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Favorable]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Open Settlement with Austria alone  —  opens with 650 gold to Austria staged — the sum that carries her]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Doubtful — may counter]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1521 of 1521 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (57 labels)
```

```
#0267  click Propose Peace  ->  ok
  (clicked at (1825, 643))
view: <run>\frames\0267_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 574 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms / France demands: /   • Austria pays 133 gold per turn to France for as long as the treaty stands / Mutual: /   • Peace Treaty (end state of war) — France and Austria /   • Status quo: Vienna stays ours by the treaty — titled. /  / Assessment: BALANCED / The manner of this peace: none — it brings Austria to no terms the Emperor's designs read (two of her …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1566 of 1566 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,110 next turn)
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
   ► propose peace with Austria
map: unchanged (57 labels)
```

```
#0268  click Not Now  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0268_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Vienna
   +25 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Vienna]
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
   800 (+1,110 next turn)
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (57 labels)
```

```
#0269  type what if Murat attacks Kutuzov  ->  ok
  (typed and Enter)
view: <run>\frames\0269_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Murat (22,000) vs Kutuzov (substantial force) at Moravia — the balance of force looks unfavorable.
  What Moravia can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 22,000 we muster) would cost ~165g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
  (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)

Nothing has been ordered, and nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1367 of 1367 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,110 next turn)
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
   ► what if Murat attacks Kutuzov
   Were you to give the order, Sire:
   MUSTER — Murat (22,000) vs Kutuzov (substantial force) at Moravia — the balance of force looks unfavorable.
   What Moravia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 22,000 we muster) would cost ~165g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (57 labels)
```

```
#0270  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0270_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1367 of 1367 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,110 next turn)
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
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 22,000 we muster) would cost ~165g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (57 labels)
```

```
#0271  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0271_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 295 of 838 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1367 of 1367 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 22,000 we muster) would cost ~165g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (57 labels)
```

```
#0272  click Austria  ->  ok
  (clicked at (1825, 460))
view: <run>\frames\0272_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 336 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War for Vienna   Relation: -80 (Hostile) /  / "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." / Recommendation: Permit me to observe, Sire, that the arithmetic favours one road: Propose Armistice, at 58 of 50. It costs 1 DP. A truce keeps  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Favorable]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Open Settlement with Austria alone  —  opens with 650 gold to Austria staged — the sum that carries her]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Doubtful — may counter]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1367 of 1367 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 22,000 we muster) would cost ~165g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (57 labels)
```

```
#0273  click Propose Peace  ->  ok
  (clicked at (1825, 643))
view: <run>\frames\0273_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 574 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms / France demands: /   • Austria pays 133 gold per turn to France for as long as the treaty stands / Mutual: /   • Peace Treaty (end state of war) — France and Austria /   • Status quo: Vienna stays ours by the treaty — titled. /  / Assessment: BALANCED / The manner of this peace: none — it brings Austria to no terms the Emperor's designs read (two of her …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1935 of 1935 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,110 next turn)
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
   ► propose peace with Austria
map: unchanged (57 labels)
```

```
#0274  click Send as suggested  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0274_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 2/5
   Threat 70 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Peace Treaty Dispatched @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Vienna
   +25 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Vienna]
── BottomLeftUI (layer 0) [scrolled 2008 of 2008 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800 (+1,110 next turn)
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
   Talleyrand departs for the Austrian court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent)
map: unchanged (57 labels)
```

```
#0275  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0275_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 422 px] ──
   ENEMY PHASE - Turn 5
   RUSSIA / ──────────────────────────── / - Kutuzov attacks Murat /     Battle of Vienna /     Kutuzov: 2,314 casualties, 35,686 remaining /     Murat: 5,603 casualties, 16,397 remaining /     Result: Attacker tactical victory (Kutuzov victorious) /     ⚔ View the field /     --- Berthier's Report --- /     Kutuzov: "The old man strikes once, and only when the snow agrees." /     Murat: "The field i …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (4)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2053 of 2054 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,461 (+1,428 next turn)
   Inf:
   82,200
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
   Kutuzov — Moravia — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Dictated Terms (+45)
   War Purpose: Defense vs Russia (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Mack
   • Davout, march to Lorraine
   • recruit infantry in Rhineland — 727g for 3,000 men under Davout
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
   ► propose peace with Austria
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► what if Murat attacks Kutuzov
   Were you to give the order, Sire:
   MUSTER — Murat (22,000) vs Kutuzov (substantial force) at Moravia — the balance of force looks unfavorable.
   What Moravia can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 22,000 we muster) would cost ~165g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
   ► propose peace with Austria
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent)
   ► end turn
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2776g | Occupation: -30g | Admiralty: -90g | Blockade: -219g | Materiel: -767g | Other: +1337g | Upkeep: -2346g | Net: +661g
   Treasury: 1,461g
   Actions refreshed: 4/4
   Holland loyalty 96 (-4): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 98 (-2): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 94 (-6): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,000 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was the war is barely begun — no court signs away a province over one skirmish.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Berthier: Enemy forces spotted near Vienna! Archduke Charles (52,495 troops) at Bohemia.
   Berthier: Enemy forces spotted near Vienna! Kutuzov (35,686 troops) at Moravia.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1600,542)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,479)  Archduke Charles(2061,443)  Bernadotte(1930,451)  Deroy(1955,425)  Murat(2109,501)  ?(1959,325)  Brunswick(1958,287)  ?(2195,487)  Kutuzov(2194,448)  ?(1859,469)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1951,590)  Archduke John(1948,537)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1813,497)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  25k(2109,556)  ?(1959,376)  ?(1861,560)  ?(1893,372)  25k(1595,497)  12k(1551,454)  ?(1769,580)  10k(1788,425)  12k(1693,420)  10k(1910,645)
```

```
#0276  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0276_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt', 'war_status_panel (not modal)'], region_panel=no
── InterruptPopup (layer 103) ──
   MURAT REPORTS
   "Murat is cornered at Vienna with 6,647 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (4)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Murat is cornered @(3358,64)]  [icon: Petition from Switzerland @(3400,64)]  [icon: Blockade — Britain closes our ports @(3442,64)]  [icon: Envoy from Prussia @(3484,64)]  [icon: Envoy from Ottoman Empire @(3526,64)]  [icon: Envoy from Portugal @(3568,64)]  [+2]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Vienna
   +5 →
   T:5
   controls: [THIRD COALITION  ▸]  [War for Vienna]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2048 of 2048 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,461 (+1,428 next turn)
   Inf:
   82,200
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Naples and Russia have signed an Open Borders Agreement.
   Berthier: Enemy forces spotted near Vienna! Archduke Charles (52,495 troops) at Bohemia.
   Berthier: Enemy forces spotted near Vienna! Kutuzov (35,686 troops) at Moravia.
   --- Strategic Order Updates ---
   Murat: Murat is cornered at Vienna with 6,647 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Murat was mauled at Vienna: a third of his corps — 5,603 men — lost in a single action.
   • Sire — Swabia has been taken by Austria.
   • THE SUN OF AUSTERLITZ — Talleyrand: "Austria has bent, Sire — now say what the Empire is for. The roads wait in the Cabinet (F1 → The Emperor's Designs)."
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 29 regions. Treasury: 1,461g (+1,428 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 88% of French forces (an estimate — 4 of 4 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 42,000 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   - Teulie — Milan — 7,000 — Awaiting orders.
   ? Murat — Vienna — 6,647 — ENCIRCLED at Vienna by Archduke Charles — awaiting your word. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Dumonceau — Amsterdam — 6,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — large force [partial]
   Archduke Charles — Bohemia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Kutuzov — Moravia — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Austria.
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   Swabia passes from Bavaria to Austria.
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   An envoy from Switzerland has arrived with a petition.
   Holland sends 6,000 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,000 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria with a response.
   Talleyrand reports: Sweden and Russia have signed the Open Borders Agreement.
   Talleyrand reports: Naples and Russia have signed the Open Borders Agreement.
   THE CONTINENTAL SYSTEM tightens: 11 of 26 (42%) of the Continent's ports are closed to Britain.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   REVANCHE: Austria will not forgive France the loss of Vienna. A new design hardens in their court.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 4 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders Agreement
   - Ottoman Empire — Open Borders Agreement
   - Portugal — Open Borders Agreement
   - ...and 1 more
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Vienna) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Austria (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+9)
   War Purpose: Defense vs Russia (War for Vienna) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-4)
   COALITION THREAT
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
   Murat awaits your orders!
map: unchanged (61 labels)
```

```
#0277  click Attempt a Breakout  ->  ok
  (clicked at (1971, 584))
view: <run>\frames\0277_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Murat ◆
   Archduke Charles ◆
   16,397 → 6,647
   54,000 → 52,495
   SECOND BATTLE OF VIENNA
   click anywhere to skip ▸
   VIENNA · TURN 5
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (4)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: Envoy from Prussia @(3442,64)]  [icon: Envoy from Ottoman Empire @(3484,64)]  [icon: Envoy from Portugal @(3526,64)]  [icon: The Moniteur is out @(3568,64)]  [+1]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2092 of 2092 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,461 (+1,612 next turn)
   Inf:
   82,200
   Cav:
   20,073
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Vienna! 3,323 of his men escape home to the depots.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1600,542)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,479)  Archduke Charles(2061,443)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  ?(2195,487)  Kutuzov(2194,448)  ?(1859,469)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1951,590)  Archduke John(1948,537)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1813,497)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  25k(2109,556)  ?(1959,376)  ?(1861,560)  ?(1893,372)  25k(1595,497)  12k(1551,454)  ?(1769,580)  10k(1788,425)  12k(1693,420)  10k(1910,645)
```

```
#0278  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0278_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 270 px] ──
   PENDING ENVOYS (4)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 5
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   THE COURTS WRITE (2)
   Ottoman Empire and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Ottoman Empire
   Proposal
   Turn 5
   Incoming proposal: Open Borders Agreement
   Reis Efendi, serene and unhurried: "The Porte watches the star of France climb ever higher and, being an old admirer of whatever endures, would sooner arrange itself gracefully beneath so great a light than stand across its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   or click the letter to reply in full
   WAITING
   Portugal
   Proposal
   Turn 5
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "A kingdom as modest as ours does not measure itself against the Empire's shadow, and Lisbon would far rather reach an understanding than be caught standing in its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Portugal pays you 60 gold at the signing
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2092 of 2092 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Murat awaits your orders!
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Vienna! 3,323 of his men escape home to the depots.
map: unchanged (60 labels)
```

```
#0279  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0279_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2092 of 2092 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,461 (+1,612 next turn)
   Inf:
   82,200
   Cav:
   20,073
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Murat awaits your orders!
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Vienna! 3,323 of his men escape home to the depots.
map: unchanged (60 labels)
```

```
#0280  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0280_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2092 of 2092 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,461 (+1,612 next turn)
   Inf:
   82,200
   Cav:
   20,073
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   ════════════════════════════════════
   Murat awaits your orders!
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Vienna! 3,323 of his men escape home to the depots.
map: unchanged (60 labels)
```

```
#0281  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0281_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2092 of 2092 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Murat awaits your orders!
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Vienna! 3,323 of his men escape home to the depots.
map: unchanged (60 labels)
```

```
#0282  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0282_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 384 of 384 px] ──
   LOAD GAME
   controls: [replay_beira (Turn 6)]  [replay_rump (Turn 11)]  [replay_sanctuary (Turn 5)]  [replay_letters (Turn 2)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2092 of 2092 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Murat awaits your orders!
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Vienna! 3,323 of his men escape home to the depots.
map: unchanged (60 labels)
```

```
#0283  scroll 1830 500 down 20  ->  ok
  (scrolled down 20 at (1830, 500))
view: <run>\frames\0283_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 384 of 384 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2092 of 2092 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Murat awaits your orders!
   > Murat: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Murat is taken by Austria at Vienna! 3,323 of his men escape home to the depots.
map: unchanged (60 labels)
```

```
#0284  click replay_letters  ->  ok
  (clicked at (1825, 558))
view: <run>\frames\0284_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 69 px] ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   THE SMALL COURTS WRITE (2)
   Saxony and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Saxony
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Einsiedel, anxiously: "Saxony has kept her house through many great reigns by keeping her treaties in good repair; His Majesty would merely continue the practice. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Saxony pays you 82 gold at the signing
   or click the letter to reply in full
   WAITING
   Portugal
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "A kingdom as modest as ours does not measure itself against the Empire's shadow, and Lisbon would far rather reach an understanding than be caught standing in its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Prussia @(3529,62)]  [icon: Envoy from Saxony @(3571,62)]  [icon: Envoy from Portugal @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1653 of 1653 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Game loaded successfully.
   Loaded: replay_letters
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
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
   - Prussia — Open Borders Agreement
   - Saxony — Open Borders Agreement
   - Portugal — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
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
#0285  click#1 Open ▸  ->  ok
  (clicked at (2183, 294))
view: <run>\frames\0285_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 46 px] ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade /  / Hardenberg, stiffly: "Berlin wil …
   controls: [Accept]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1653 of 1653 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0286  click Not Now  ->  ok
  (clicked at (1979, 687))
view: <run>\frames\0286_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1675 of 1675 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
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
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0287  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0287_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   An unanswered envoy awaits your reply — the Cabinet stays shut until it is answered or the turn ends. Reopen Envoys to answer it.
   controls: [icon: Close (Esc) @(2075,284)]  [Open Envoys (3)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
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
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0288  click Open Envoys  ->  ok
  (clicked at (1829, 427))
view: <run>\frames\0288_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) [scrolled 0 of 69 px] ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   THE SMALL COURTS WRITE (2)
   Saxony and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Saxony
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Einsiedel, anxiously: "Saxony has kept her house through many great reigns by keeping her treaties in good repair; His Majesty would merely continue the practice. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Saxony pays you 82 gold at the signing
   or click the letter to reply in full
   WAITING
   Portugal
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "A kingdom as modest as ours does not measure itself against the Empire's shadow, and Lisbon would far rather reach an understanding than be caught standing in its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1675 of 1675 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
map: unchanged (53 labels)
```

```
#0289  click#1 Accept  ->  ok
  (clicked at (1433, 635))
view: <run>\frames\0289_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   A great court's letter is answered in full — open to accept, haggle or refuse.
   A SMALL COURT WRITES (1)
   Portugal writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Portugal
   Proposal
   Turn 2
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "A kingdom as modest as ours does not measure itself against the Empire's shadow, and Lisbon would far rather reach an understanding than be caught standing in its path. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treaty with Saxony @(3613,62)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   882 (+853 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0290  click Close  ->  ok
  (clicked at (1829, 830))
view: <run>\frames\0290_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   882 (+853 next turn)
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
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0291  click_at 1814 424  ->  ok
  (clicked at (1814, 424) on MapArea '100' (Control, layer 0))
view: <run>\frames\0291_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   882 (+853 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── OrderStrip (layer 0) ──
   Ney selected — click a province: march · an enemy: attack · a marshal: support · Esc cancels / ■ this turn   ■ 1 turn   ■ 2–3 turns   ■ 4+ turns   60 provinces on his roads · a march costs 2 actions
── MapControls (layer 0): unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0292  click_at 1853 454  ->  ok
  (clicked at (1853, 454) on MapArea '100' (Control, layer 0))
view: <run>\frames\0292_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['order_card'], region_panel=no
── OrderConfirmCard (layer 123) ──
   ORDERS FOR NEY
   Ney, march to Rhineland
   Refused — No path from Rhineland to Rhineland.
   controls: [Send  (Enter)](disabled)  [Put in line]  [Cancel  (Esc)]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px]: unchanged
── OrderStrip (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0293  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0293_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treaty with Saxony @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px]: unchanged
── OrderStrip (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0294  click_at 1814 424  ->  ok
  (clicked at (1814, 424) on MapArea '100' (Control, layer 0))
view: <run>\frames\0294_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0295  click_at 1850 520  ->  ok
  (clicked at (1850, 520) on MapArea '100' (Control, layer 0))
view: <run>\frames\0295_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── RegionPanel (layer 26) [scrolled 0 of 375 px] ──
   Swabia
   Bavaria  City · Plains / ACTIONS /     Negotiate with Bavaria   /  / One province — who holds it, what it pays, what defends it. Click the map to choose another. / Intel: Partial (reports only) / Income: Unknown   Stability: Unknown   Supply: Unknown /  / MARCH HERE  a standing order — he marches on each turn /     Bernadotte · 1 AP · this turn    Mack holds Swabia — Bernadotte stops there and ask …
   controls: [icon @(535,73)]  <Negotiate with Bavaria>  <Bernadotte · 1 AP · this turn>  <Davout · 1 AP · this turn>  <Lannes · 1 AP · this turn>  <Murat · 1 AP · this turn>  <Napoleon · 1 AP · this turn>  <+3 more…>  <Bernadotte · attack · 1 AP>  <Davout · attack · 1 AP>  <Lannes · attack · 1 AP>  <Murat · attack · 1 AP>  <Napoleon · attack · 1 AP>  <+3 more…>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px]: unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0296  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0296_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0297  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0297_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0298  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0298_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 384 of 384 px] ──
   LOAD GAME
   controls: [replay_beira (Turn 6)]  [replay_rump (Turn 11)]  [replay_sanctuary (Turn 5)]  [replay_letters (Turn 2)]  [Unknown (Turn ?)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0299  click replay_firststep  ->  ERROR: no visible control's text holds "replay_firststep"
view: <run>\frames\0299_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 384 of 384 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0300  scroll 1830 500 up 20  ->  ok
  (scrolled up 20 at (1830, 500))
view: <run>\frames\0300_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) [scrolled 0 of 384 px] ──
   LOAD GAME
   controls: [Autosave - Turn 6 (Turn 6)]  [replay_clock (Turn 19)]  [replay_firststep (Turn 4)]  [replay_sea (Turn 6)]  [replay_mission (Turn 14)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Setting aside Prussia's proposal — the Cabinet stays shut until it is answered or the turn ends. Click the envoy badge to revisit.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (53 labels)
```

```
#0301  click replay_firststep  ->  ok
  (clicked at (1825, 510))
view: <run>\frames\0301_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1543 of 1543 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   800 (+560 next turn)
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
   Loaded: replay_firststep
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 28 regions. Treasury: 800g (+560 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 73% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Bohemia — 42,000 — Awaiting orders.
   > Soult — Franconia — 29,100 — Moving to Milan — 3 turns out. (to the letter)
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Munich — large force [partial]
   Archduke Charles — Carniola — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
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
   • Soult, attack Archduke John
   • Ney, march to Swabia
   • recruit infantry in Rhineland — 738g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Soult attacks Archduke John' first — it names who marches with Soult, and costs nothing.
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
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(2025,477)  Soult(1931,451)  Bernadotte(1971,425)  Deroy(1955,399)  ?(2016,632)  Archduke Charles(2016,605)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  ?(1948,579)  Archduke John(1948,540)  Napoleon(1752,436)  Lannes(1800,497)  Murat(1825,471)  Mack(1880,471)  ?(2068,435)  ?(2109,545)  ?(1959,372)  ?(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1685,416)  ?(1910,645)
```

```
#0302  type Massena, march to Milan  ->  ok
  (typed and Enter)
view: <run>\frames\0302_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok Massena: 'Archduke John bars the way at Tyrol, Sire — I can take him.' Massena engages him on the road, on his own judgment.

MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Massena' and he will march
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
  Archduke John does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
  (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
Ask 'what if Massena attacks Archduke John' to read the muster before you commit — it costs nothing.


[Combat] Massena leads the charge! (Aggressive: +15% attack)
[Shi
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Bernadotte
   Archduke Charles
   17,000 → 15,494
   54,000 → 49,301
   ⚔
   Massena ◆
   Archduke John ◆
   42,000 → 35,798
   20,000 → 17,680
   marched to the guns
   marched to the guns
   Soult — awaits explicit orders
   THE GREAT BATTLE OF TYROL
   click anywhere to skip ▸
   TYROL · TURN 4
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1785 of 1785 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   415 (+832 next turn)
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 70/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Soult, attack Archduke John
   • Ney, march to Swabia
   • recruit infantry in Rhineland — 738g for 3,000 men under Davout
   • build supply depot in Rhineland — 300g
   Ask 'what if Soult attacks Archduke John' first — it names who marches with Soult, and costs nothing.
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
   ► Massena, march to Milan
   ⚔ The Great Battle of Tyrol ⚔
   Massena: 'Archduke John bars the way at Tyrol, Sire — I can take him.' Massena engages him on the road, on his own judgment.
   MUSTER — Massena (42,000) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Massena' and he will march
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
   Archduke John does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 42,000 we muster) would cost ~315g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Ask 'what if Massena attacks Archduke John' to read the muster before you commit — it costs nothing.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Archduke John stands firm against superior numbers! (Cautious: +10% outnumbered)
   [Terrain] Archduke John benefits from Mountains terrain (+25% defense)
   [Combat] Adjacent allies bolster Massena's attack! (+2%)
   Massena's forces advance steadily. Brutal stalemate between Massena and Archduke John. Heavy casualties on both sides: Massena's army 7,708, Archduke John 7,019.
   [Materiel] Guns, horses and stores lost with the fallen: France -385g, Austria -350g. Our treasury stands at 415 gold.
   Bernadotte withdraws to Franconia after the battle.
   ArchdukeCharles withdraws to Carniola after the battle.
   Berthier: an inconclusive affair of his own making — nothing gained, nothing charged.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 42,000 (lead) + 16,065 committed (Bernadotte) = 58,065.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting ally lost 1,506 men.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Archduke John was reinforced — massed effective strength: 20,000 (lead) + 64,243 committed (Archduke Charles) = 84,243.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Archduke John's supporting ally lost 4,699 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "Nothing settled. I do not leave accounts open for long."
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena's own corps 6,202 | Archduke John's own corps 2,320
   Strength: Massena 42,000 → 35,798 | Archduke John 20,000 → 17,680
   Berthier: "Bernadotte reached the field beside Massena, Sire — it saved the line, no more."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Massena(2025,477)  Soult(1931,451)  Bernadotte(1971,425)  Deroy(1955,399)  ?(2016,632)  Archduke Charles(2016,605)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Davout(1839,371)  Archduke John(1948,575)  Napoleon(1752,436)  Lannes(1800,497)  Murat(1825,471)  Mack(1901,528)  ?(2068,435)  ?(2109,545)  ?(1959,372)  ?(1901,603)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1685,416)  ?(1910,645)
```

```
#0303  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0303_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1785 of 1785 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena's own corps 6,202 | Archduke John's own corps 2,320
   Strength: Massena 42,000 → 35,798 | Archduke John 20,000 → 17,680
   Berthier: "Bernadotte reached the field beside Massena, Sire — it saved the line, no more."
map: unchanged (55 labels)
```

```
#0304  click The Cabinet  ->  ok
  (clicked at (824, 978))
view: <run>\frames\0304_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1785 of 1785 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   415 (+832 next turn)
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
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena's own corps 6,202 | Archduke John's own corps 2,320
   Strength: Massena 42,000 → 35,798 | Archduke John 20,000 → 17,680
   Berthier: "Bernadotte reached the field beside Massena, Sire — it saved the line, no more."
map: unchanged (55 labels)
```

```
#0305  scroll 1830 600 down 8  ->  ok
  (scrolled down 8 at (1830, 600))
view: <run>\frames\0305_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 295 of 838 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1785 of 1785 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena's own corps 6,202 | Archduke John's own corps 2,320
   Strength: Massena 42,000 → 35,798 | Archduke John 20,000 → 17,680
   Berthier: "Bernadotte reached the field beside Massena, Sire — it saved the line, no more."
map: unchanged (55 labels)
```

```
#0306  click Austria  ->  ok
  (clicked at (1825, 460))
view: <run>\frames\0306_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 356 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Permit me to observe, Sire, that a level war is the dearest kind to end: Propose Peace reads 5 of 50; it wants her loyalty to the league — she has no r …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Unlikely]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1785 of 1785 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke John (Outnumbered (cautious) +10%, Terrain (Mountains) +25%)
   Casualties: Massena's own corps 6,202 | Archduke John's own corps 2,320
   Strength: Massena 42,000 → 35,798 | Archduke John 20,000 → 17,680
   Berthier: "Bernadotte reached the field beside Massena, Sire — it saved the line, no more."
map: unchanged (55 labels)
```

```
#0307  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0307_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 596 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 3 turns old and stays so; exhaustion holds. No territory or gold changes hands until it ends …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms](disabled: A truce settles nothing: no province or gold changes hands until it ends. Demands are pres)  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2362 of 2362 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   415 (+832 next turn)
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
map: unchanged (55 labels)
```

```
#0308  quit  ->  ok
  (the engine quits)
view: <run>\frames\0308_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 596 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2362 of 2362 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Casualties: Massena's own corps 6,202 | Archduke John's own corps 2,320
   Strength: Massena 42,000 → 35,798 | Archduke John 20,000 → 17,680
   Berthier: "Bernadotte reached the field beside Massena, Sire — it saved the line, no more."
   ► propose armistice with Austria
map: unchanged (55 labels)
```

