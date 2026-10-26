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
#0004  click Diplomacy (D)  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0004_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 3017 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 5/5
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  /   Britain [Coalition Member] — WAR  Relation: -90 (Hostile) /   Doctrine: The Line Holds; flaw: Irreplaceable (uncured — the Militia Transfer would end it once the Horse Guards Reforms stands) /   Diplomat: Castlereagh (Hawk) — Skill 7 /   Region …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
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
turn: Turn 1 — Late September 1805   command line: ''
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
#0006  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
#0007  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 190 of 836 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Cancel]
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
#0008  click Austria  —  At War  ->  ok
  (clicked at (1825, 565))
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
#0009  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 308 of 355 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Sire, the field reads +0 and no road carries. Propose Peace comes nearest at -1 of 50; her loyalty to the league — she has no reason of her own to brea …
   France is at war with this court.
   France is at war with this court.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1392g to buy off in turn).](disabled: France is at war with this court.)  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured.](disabled: France is at war with this court.)  [Subjugate  —  make her France's vassal by conquest — she must be beaten first](disabled: Austria still stands — Vienna is its own and 3 of its corps are in the field (its war scor)  [Back]  [Cancel]
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
#0010  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
#0011  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
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
#0012  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 805 of 845 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Saxony  —  Peace  |  -10 (Wary)]  [Hanover  —  Peace  |  -50 (Hostile)]  [Hesse  —  Peace  |  0 (Neutral)]  [Papal States  —  Peace  |  -10 (Wary)]  [Cancel]
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
#0013  scroll 1828 500 up 3  ->  ok
  (scrolled up 3 at (1828, 500))
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 683 of 843 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Saxony  —  Peace  |  -10 (Wary)]  [Cancel]
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
#0014  click Prussia  —  Peace  ->  ok
  (clicked at (1825, 381))
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 310 px, 0 of 474 px] ──
   THE CABINET — Prussia
   DP: 5
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: -10 (Wary) /  / "Prussia maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. Courting Prussia would be quicker — ≈4 turns again …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3).]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Armed Neutrality next (600g to buy off in turn).](disabled: Their price is 1128g — the treasury holds 800g.)  [Back]  [Cancel]
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
#0015  click Improve Relations  ->  ok
  (clicked at (1825, 458))
view: <run>\frames\0015_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Prussia /  / "Sire, I shall begin efforts to improve relations with Prussia. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
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
   ► improve relations with Prussia
map: unchanged (53 labels)
```

```
#0016  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0016_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1609 of 1609 px] ──
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
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0017  click Diplomacy (D)  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0017_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 3017 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Prussia
   DP: 5/5
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  /   Britain [Coalition Member] — WAR  Relation: -90 (Hostile) /   Doctrine: The Line Holds; flaw: Irreplaceable (uncured — the Militia Transfer would end it once the Horse Guards Reforms stands) /   Diplomat: Castlereagh (Hawk) — Skill 7 /   Region …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px] ──
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
   ─────────────────────────────────────
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0018  click WAR BARGAINS  ->  ok
  (clicked at (1914, 273))
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Prussia
   DP: 5/5
   ═══ WAR BARGAINS ═══ /  / No war bargains recorded.
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS](disabled: You are reading this book)  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0019  click TALLEYRAND  ->  ok
  (clicked at (1799, 273))
view: <run>\frames\0019_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 112 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Prussia
   DP: 5/5
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 5/5 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Improving Relations → Prussia /   Wary (+0 over 0 turns) /   Status: Active, Cost: 1 DP/turn /   Effect: +8 relation per turn /   Net +8 a turn · ≈16 turns to +100 at the presen …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1609 of 1609 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0020  click Assess the Situation  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 200 px] ──
   TALLEYRAND'S ASSESSMENT /  / "Sire — the state of Europe, plainly told. /  /   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1) /  /   Against Britain + Austria + Russia: the war hangs in the balance (+0) — 0 battles across 0 turns. /     Britain's design: The Low Countries — They will not suffer France's bloc in Flanders. /     Their price: prepared to go as far as war — Fra …
   controls: [icon: Close (Esc) @(2151,292)]  [Satisfy their design (Britain)]  [Thank you]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1654 of 1654 px] ──
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
#0021  click Satisfy their design (Britain)  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Britain /  /  / "Sire, the war with Britain is at a standstill. Neither side has won a decisive advantage on the battlefield."
   controls: [icon: Close (Esc) @(2151,292)]  [Propose peace]  [Press advantage]  [Wait]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1676 of 1676 px] ──
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
#0022  click Propose peace  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 2/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Improving Relations]  [icon: Peace Treaty Dispatched @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1743 of 1743 px] ──
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
   Directing Talleyrand: execute proposal
   Talleyrand departs for the British court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent)
map: unchanged (53 labels)
```

```
#0023  type what can I do  ->  ok
  (typed and Enter)
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
#0024  type what if Ney attacks Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
── BottomLeftUI (layer 0) [scrolled 2031 of 2031 px] ──
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
#0025  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 829 px] ──
   THE CABINET
   DP: 2
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2031 of 2031 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −1,200g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0026  click The Emperor's Designs  ->  ok
  (clicked at (1825, 572))
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 1880 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 2
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Your own aims, Sire, not the courts'. A road asks a construction, then a seal; hold both and the peace that seals it can be the Decisive Peace. Proclaiming costs 2 DP and 1 administrative action and cannot be undone.
   No road is proclaimed. Three roads — one proclamation, and it cannot be undone.
   Road I — The Protector of the Rhine (The Act of Confederation) /     ✓ Bavaria must stand with France /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Austria −10, Prussia −10. /     • The Confederation of the Rhine (the construction) — 0 of 3 courts under the Emperor's protection; to be held 4 end turns /         Three of Bavaria, Hesse, Saxon …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Proclaim Road I — The Act of Confederation]  [Proclaim Road II — The Schönbrunn Proclamation]  [Proclaim Road III — The Blockade of the British Isles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2031 of 2031 px] ──
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
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −1,200g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0027  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 379 of 1880 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 2
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Road I — The Protector of the Rhine (The Act of Confederation) /     ✓ Bavaria must stand with France /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Austria −10, Prussia −10. /     • The Confederation of the Rhine (the construction) — 0 of 3 courts under the Emperor's protection; to be held 4 end turns /         Three of Bavaria, Hesse, Saxon …
   Road II — The Crowns of Italy (The Schönbrunn Proclamation) /     ✓ the Kingdom of Italy must be France's /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Naples −10, Spain −10. /     • The Throne of Naples (the construction) — 0 of 1 province titled to the Empire /         Naples titled to the Empire — her court France's satellite at loyalty 4 …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [↳ Bavaria]  [↳ Hesse]  [↳ Saxony]  [↳ Hanover]  [↳ Austria]  [↳ Prussia]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2031 of 2031 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −1,200g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0028  click ↳ Bavaria  ->  ok
  (clicked at (1606, 617))
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 662 px] ──
   THE CABINET — Bavaria
   DP: 2
   TALLEYRAND'S ASSESSMENT — BAVARIA / Status: Alliance   Relation: +60 (Loyal) /  / "Our alliance with Bavaria stands firm. There is little to gain from change, and much to lose." / Recommendation: Relations must improve before proposals will find purchase. Reassure Ally is shut while Talleyrand carries a proposal abroad — it opens when he is home. / Talleyrand: "Bavaria stands on the Emperor's road …
   Talleyrand is in transit with the peace treaty to Britain — home in 1 turn
   Talleyrand is in transit with the peace treaty to Britain — home in 1 turn
   Talleyrand is in transit with the peace treaty to Britain — home in 1 turn
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)  —  Uncertain — a counter is likely](disabled: Talleyrand is in transit with the peace treaty to Britain — home in 1 turn)  [Declare War (1 DP)](disabled: Talleyrand is in transit with the peace treaty to Britain — home in 1 turn)  [Break Treaty (1 DP)](disabled: Talleyrand is in transit with the peace treaty to Britain — home in 1 turn)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2031 of 2031 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −1,200g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0029  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2031 of 2031 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Swabia is Bavaria's soil — the corps standing there are fed by contract, about −1,200g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Nothing has been ordered, and nothing spent.
map: unchanged (53 labels)
```

```
#0030  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   18,000 → 16,969
   Murat
   22,000 → 21,496
   Davout
   26,000 → 24,808
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 22,163 → 21,846 after the advance
   52,000 → 29,126
   marched to the guns
   marched to the guns
   +2 corps in reserve — 458 lost
   Soult — awaits explicit orders
   THE GREAT BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 2/5
   Threat 78 / 100
   Turn 1 — Late September 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Improving Relations]  [icon: Peace Treaty Dispatched @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +20 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2678 of 2678 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   549 (−60 next turn)
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
   Ask 'what if Ney attacks Mack' first — it names who marches with Ney, and costs nothing.
   For any matter of state, press F1 for the Cabinet.
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
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney engages in solid combat. Ney gains the advantage over Mack. Casualties: Ney's army 5,022, Mack 22,874. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -251g, Austria -1143g. Our treasury stands at 549 gold. Ney advances into Swabia. (317 lost to march) Swabia is Bavaria's soil — the corps standing there are fed by contract, about −252g more a turn. Swabia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   [!] Mack's broken army flees to Munich! (1,354 lost to march) (recovering for 3 turns)
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
   His supporting allies lost 3,185 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 1,837 | Mack 22,874
   Strength: Ney 24,000 → 22,163 → 21,846 after the advance | Mack 52,000 → 29,126
   Berthier: "Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
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
#0031  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2678 of 2678 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (48 labels)
```

```
#0032  type what if Ney attacks Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Ney (21,846; expect about 68,511 with the corps likely to arrive, up to 70,967 if all march; certain 21,846) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  WILL NOT — Davout: has already marched this turn
  WILL NOT — Lannes: has already marched this turn
  WILL NOT — Murat: has already marched this turn
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL NOT — Napoleon: has already marched this turn
  Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Munich can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 63,846 we muster) would cost ~479g.
  Munich is Bavaria's soil — the corps standing there are fed by contract, about −504g more a turn.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3193 of 3193 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   549 (−60 next turn)
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
   MUSTER — Ney (21,846; expect about 68,511 with the corps likely to arrive, up to 70,967 if all march; certain 21,846) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL NOT — Davout: has already marched this turn
   WILL NOT — Lannes: has already marched this turn
   WILL NOT — Murat: has already marched this turn
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Napoleon: has already marched this turn
   Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 63,846 we muster) would cost ~479g.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −504g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (48 labels)
```

```
#0033  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (21,846; expect about 68,511 with the corps likely to arrive, up to 70,967 if all march; certain 21,846) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  WILL NOT — Davout: has already marched this turn
  WILL NOT — Lannes: has already marched this turn
  WILL NOT — Murat: has already marched this turn
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
  WILL NOT — Napoleon: has already marched this turn
  Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Munich can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 63,846 we muster) would cost ~479g.
  Munich is Bavaria's soil — the corps standing there are fed by contract, about −504g more a turn.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart u
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Massena
   42,000 → 41,600
   ⚔
   Ney ◆
   Mack ◆
   21,846 → 21,500 → 20,941 after the advance
   27,772 → 2,739
   marched to the guns
   Bernadotte — weighed his own ambitions
   THE GREAT BATTLE OF MUNICH
   click anywhere to skip ▸
   MUNICH · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 2/5
   Threat 86 / 100
   Turn 1 — Late September 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Improving Relations]  [icon: Peace Treaty Dispatched @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +36 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3830 of 3830 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   512 (−502 next turn)
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
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,185 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 1,837 | Mack 22,874
   Strength: Ney 24,000 → 22,163 → 21,846 after the advance | Mack 52,000 → 29,126
   Berthier: "Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
   MUSTER — Ney (21,846; expect about 68,511 with the corps likely to arrive, up to 70,967 if all march; certain 21,846) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL NOT — Davout: has already marched this turn
   WILL NOT — Lannes: has already marched this turn
   WILL NOT — Murat: has already marched this turn
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Napoleon: has already marched this turn
   Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 63,846 we muster) would cost ~479g.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −504g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ► Ney, attack Mack
   ⚔ The Great Battle of Munich ⚔
   MUSTER — Ney (21,846; expect about 68,511 with the corps likely to arrive, up to 70,967 if all march; certain 21,846) vs Mack (substantial force) at Munich — the balance of force looks favorable.
   WILL NOT — Davout: has already marched this turn
   WILL NOT — Lannes: has already marched this turn
   WILL NOT — Murat: has already marched this turn
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Napoleon: has already marched this turn
   Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 63,846 we muster) would cost ~479g.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −504g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [!] Mack is EXPOSED! (Just retreated, no ally to cover)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Alert] Ney's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Terrain] Mack benefits from Mountains terrain (+25% defense)
   [Combat] Adjacent allies bolster Ney's attack! (+10%)
   Ney's forces advance steadily. Ney gains the advantage over Mack. Casualties: Ney's army 746, Mack 25,033. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -37g, Austria -1251g. Our treasury stands at 512 gold. Ney advances into Munich. (559 lost to march) Munich remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   [!] MARSHAL CAPTURED — Mack is taken by France at Munich! 1,369 of his men escape home to the depots.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 21,846 (lead) + 49,121 committed (Massena) = 70,967.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting ally lost 400 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%, Exhaustion -10%)
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 346 | Mack 25,033
   Strength: Ney 21,846 → 21,500 → 20,941 after the advance | Mack 27,772 → 2,739
   Berthier: "Massena arrived to reinforce Ney, but Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Davout +3(1832,454)  ?(1948,588)  Archduke John(1974,535)  Soult(1753,436)  Ney(1888,535)  Massena(1913,561)  ?(2068,435)  ?(1959,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0034  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3830 of 3830 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 346 | Mack 25,033
   Strength: Ney 21,846 → 21,500 → 20,941 after the advance | Mack 27,772 → 2,739
   Berthier: "Massena arrived to reinforce Ney, but Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
map: unchanged (49 labels)
```

```
#0035  key T  ->  ok
  (pressed T)
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: 't' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3830 of 3860 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   512 (−502 next turn)
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   [Talleyrand, assess our situation]  (Tab)
   t
   controls: [+]  [−]  [—]  [Execute]  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 346 | Mack 25,033
   Strength: Ney 21,846 → 21,500 → 20,941 after the advance | Mack 27,772 → 2,739
   Berthier: "Massena arrived to reinforce Ney, but Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
map: unchanged (49 labels)
```

```
#0036  key BackSpace  ->  ok
  (pressed BackSpace)
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3830 of 3830 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   512 (−502 next turn)
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
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 346 | Mack 25,033
   Strength: Ney 21,846 → 21,500 → 20,941 after the advance | Mack 27,772 → 2,739
   Berthier: "Massena arrived to reinforce Ney, but Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
map: unchanged (49 labels)
```

```
#0037  key Alt+T  ->  ok
  (pressed Alt+T)
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 684 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Late September 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / ═══ THE CABINET ═══ /   Talleyrand → Prussia │ IMPROVING RELATIONS  +8 a turn, drift +0, net +8 /     Relations -10 (Wary) · paused: he is carrying your proposal — costs nothing, earns nothing until he re …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3830 of 3830 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 346 | Mack 25,033
   Strength: Ney 21,846 → 21,500 → 20,941 after the advance | Mack 27,772 → 2,739
   Berthier: "Massena arrived to reinforce Ney, but Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
map: unchanged (49 labels)
```

```
#0038  click ECONOMY  ->  ok
  (clicked at (1667, 283))
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 750 px] ──
   STRATEGIC LEDGER
   ═══ ECONOMY ═══ / Late September 1805 / The treasury's books — income against upkeep, and every charge with its name on it. /  /   Treasury: 512g /   Ceiling:  none — the chest is not growing at this rate /   Income:   +2590g /   Trade:    +350g /   Admin:    +50g /   Tribute:  +937g /   Blockade: -175g  (trade halved under enemy sail) /   Admiralty: -90g /   Materiel: -288g  (guns, horses and sto …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY](disabled: You are reading this book)  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3830 of 3830 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   512 (−502 next turn)
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
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 346 | Mack 25,033
   Strength: Ney 21,846 → 21,500 → 20,941 after the advance | Mack 27,772 → 2,739
   Berthier: "Massena arrived to reinforce Ney, but Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
map: unchanged (49 labels)
```

```
#0039  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0039_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +36 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 3830 of 3830 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 346 | Mack 25,033
   Strength: Ney 21,846 → 21,500 → 20,941 after the advance | Mack 27,772 → 2,739
   Berthier: "Massena arrived to reinforce Ney, but Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
map: unchanged (49 labels)
```

```
#0040  type what if Massena attacks Archduke John  ->  ok
  (typed and Enter)
view: <run>\frames\0040_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Massena (41,600; expect about 58,713 with the corps likely to arrive) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Tyrol
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
  The band weighs a force of his you have not scouted within reach of Tyrol — scout the provinces round it.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 62,541 we muster) would cost ~469g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.

Nothing has been ordered, and nothing spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 4209 of 4209 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   512 (−502 next turn)
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
   MUSTER — Massena (41,600; expect about 58,713 with the corps likely to arrive) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
   WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Tyrol
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
   The band weighs a force of his you have not scouted within reach of Tyrol — scout the provinces round it.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 62,541 we muster) would cost ~469g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (49 labels)
```

```
#0041  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0041_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 4275 of 4275 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   512 (−502 next turn)
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
   ⚠ 2 corps stand in peril — an enemy force of ~29,126 shares the field (Swabia).
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (49 labels)
```

```
#0042  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0042_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 202 px] ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Archduke Charles moves to Tyrol / - Archduke Charles attacks Bernadotte /     Battle of Franconia /     Archduke Charles: 1,912 casualties, 52,088 remaining /     Bernadotte: 5,711 casualties, 11,289 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) — and advances into Franconia /     ⚔ View the field /     --- Berthier's Rep …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 85 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3140 of 3140 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   123 (−104 next turn)
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
   WILL NOT — Murat: has already marched this turn
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Munich
   WILL NOT — Napoleon: has already marched this turn
   Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 63,846 we muster) would cost ~479g.
   Munich is Bavaria's soil — the corps standing there are fed by contract, about −504g more a turn.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [!] Mack is EXPOSED! (Just retreated, no ally to cover)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Alert] Ney's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Terrain] Mack benefits from Mountains terrain (+25% defense)
   [Combat] Adjacent allies bolster Ney's attack! (+10%)
   Ney's forces advance steadily. Ney gains the advantage over Mack. Casualties: Ney's army 746, Mack 25,033. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -37g, Austria -1251g. Our treasury stands at 512 gold. Ney advances into Munich. (559 lost to march) Munich remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   [!] MARSHAL CAPTURED — Mack is taken by France at Munich! 1,369 of his men escape home to the depots.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 21,846 (lead) + 49,121 committed (Massena) = 70,967.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting ally lost 400 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%, Exhaustion -10%)
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Ney's own corps 346 | Mack 25,033
   Strength: Ney 21,846 → 21,500 → 20,941 after the advance | Mack 27,772 → 2,739
   Berthier: "Massena arrived to reinforce Ney, but Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
   ► what if Massena attacks Archduke John
   Were you to give the order, Sire:
   MUSTER — Massena (41,600; expect about 58,713 with the corps likely to arrive) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
   WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Tyrol
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
   The band weighs a force of his you have not scouted within reach of Tyrol — scout the provinces round it.
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 62,541 we muster) would cost ~469g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   ⚠ 2 corps stand in peril — an enemy force of ~29,126 shares the field (Swabia).
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► end turn
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -285g | Other: +1337g | Upkeep: -3722g | Net: -389g
   Treasury: 123g
   Actions refreshed: 4/4
   Supply shortage at Franconia: Bernadotte loses 118 troops
   Supply shortage at Franconia: Archduke Charles loses 918 troops
   Supply shortage at Swabia: Davout loses 823 troops
   Supply shortage at Swabia: Lannes loses 563 troops
   Supply shortage at Swabia: Murat loses 713 troops
   Supply shortage at Swabia: Napoleon loses 316 troops
   Supply shortage at Munich: Ney loses 812 troops
   Supply shortage at Munich: Massena loses 1,614 troops
   Supply shortage at Munich: Deroy loses 853 troops
   Switzerland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Soult at Lorraine. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Britain empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was her loyalty to the league — she has no reason of her own to break ranks yet.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   Berthier reports that Massena appears envious of Ney's laurels — he has grown restless for glory.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Massena is eyeing Archduke John's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Davout +3(1832,454)  ?(1956,579)  Archduke John(2031,540)  Soult(1753,436)  Ney(1888,535)  Massena(1901,561)  Deroy(1937,528)  Dumonceau(1755,322)  Teulie(1909,589)  ?(2068,435)  ?(1959,404)  10k(1859,591)  ?(1854,373)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0043  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0043_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Bernadotte ◆
   Archduke Charles ◆
   17,000 → 11,289
   54,000 → 52,088 → 50,526 after the advance
   Ney — could not reach the field
   BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 85 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Envoy from Prussia @(3231,64)]  [icon: Envoy from Ottoman Empire @(3273,64)]  [icon: Envoy from Portugal @(3315,64)]  [icon: Marshal Massena seeks an audience @(3357,64)]  [Talleyrand at Prussia — Improving Relations]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +33 →
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
   123 (−104 next turn)
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
   Berthier reports that Massena appears envious of Ney's laurels — he has grown restless for glory.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Massena is eyeing Archduke John's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — General Mack of Austria is taken at Munich — he is our prisoner, and their order of battle is one commander shorter.
   • Sire — Bernadotte was mauled at Franconia: a third of his corps — 5,711 men — lost in a single action.
   • Sire — Marshal Ney holds the field at Swabia — Mack's corps is broken and flees.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 123g (-104 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 42% of French forces (an estimate — 1 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Munich — 39,986 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 23,985 — Awaiting orders.
   - Murat — Swabia — 20,783 — Awaiting orders.
   - Ney — Munich — 20,129 — Awaiting orders.
   - Lannes — Swabia — 16,406 — Awaiting orders.
   - Bernadotte — Franconia — 11,171 — Awaiting orders. Trust:40 Morale:51%
   ⚠ IN PERIL — an enemy force of ~49,608 shares the field (Franconia).
   - Napoleon — Swabia — 9,226 — Awaiting orders.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Munich — 21,147 [confirmed]
   Archduke Charles — Franconia — 49,608 [confirmed]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 4,959 men, at Franconia, Swabia and Munich.
   Switzerland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Massena appears envious of Ney's laurels — he has grown restless for glory.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Massena is eyeing Archduke John's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Britain.
   War exhaustion grows — Austria nears breaking point (exhaustion: 20).
   War exhaustion grows — Austria nears breaking point (exhaustion: 40).
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Soult at Lorraine. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Britain with a response.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+33)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 85/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0044  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0044_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   123 (−104 next turn)
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
   Threat: 85/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0045  type what if Davout attacks Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0045_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Davout (23,985; expect about 135,561 with the corps likely to arrive, up to 160,788 if all march; certain 23,985; a bad day (1 in 10) 107,442) vs Archduke Charles (49,608 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — may make it from the mountains at Munich in time (about 47%); order 'Ney, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Davout are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
  The Emperor commands in person — every corps on this fi
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement (free military passage) - breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade /  / Hardenberg, stiffly: "Prussia's  …
   controls: [Accept]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 85 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   123 (−104 next turn)
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
   ► what if Davout attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Davout (23,985; expect about 135,561 with the corps likely to arrive, up to 160,788 if all march; certain 23,985; a bad day (1 in 10) 107,442) vs Archduke Charles (49,608 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — may make it from the mountains at Munich in time (about 47%); order 'Ney, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Davout are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   Standing modifiers, already in the band: all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~8,498 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 141,686 we muster) would cost ~1,063g.
   Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (52 labels)
```

```
#0046  click Accept  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0046_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   THE COURTS WRITE (2)
   Ottoman Empire and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
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
   controls: {ACTIVE}  [Open ▸]  [Accept]  [Decline]  {WAITING}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 85 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3212,64)]  [icon: Marshal Massena seeks an audience @(3254,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Peace Treaty Rejected @(3633,64)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +33 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2622 of 2622 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   123 (−85 next turn)
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
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
map: unchanged (52 labels)
```

```
#0047  click#1 Accept  ->  ok
  (clicked at (1433, 500))
view: <run>\frames\0047_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   A SMALL COURT WRITES (1)
   Portugal writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   ACTIVE
   Portugal
   Proposal
   Turn 1
   Incoming proposal: Open Borders Agreement
   Araujo, measuring the room: "Portugal has watched France grow so vast that a careful minister in Lisbon thinks less of resisting such a tide than of finding a quiet harbor within it. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces; up to +100 gold a turn in trade · Portugal pays you 60 gold at the signing
   or click the letter to reply in full
   controls: {ACTIVE}  [Open ▸]  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 85 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Marshal Massena seeks an audience @(3231,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Peace Treaty Rejected @(3610,64)]  [icon: Treaty with Prussia @(3645,64)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2643 of 2643 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   123 (−76 next turn)
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
map: unchanged (52 labels)
```

```
#0048  click Accept  ->  ok
  (clicked at (1433, 500))
view: <run>\frames\0048_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 85 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Marshal Massena seeks an audience @(3231,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Peace Treaty Rejected @(3610,64)]  [icon: Treaty with Prussia @(3645,64)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2666 of 2666 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   183 (−66 next turn)
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
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (52 labels)
```

```
#0049  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0049_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2666 of 2666 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (52 labels)
```

```
#0050  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0050_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 767 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (5)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -10 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +39 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2666 of 2666 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (52 labels)
```

```
#0051  click Austria  —  At War  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0051_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 442 px, 0 of 447 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." / Recommendation: Sire, no road carries this morning. The nearest is Open Settlement with Austria alone at 39 of 50; the weight aga …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Uncertain]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Open Settlement with Austria alone  —  275 gold to Austria would carry her; the treasury can fund 183]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Doubtful]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2666 of 2666 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   183 (−66 next turn)
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
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
map: unchanged (52 labels)
```

```
#0052  click Open Settlement with Austria alone  ->  ok
  (clicked at (1825, 550))
view: <run>\frames\0052_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 508 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 39/50. / Treasury 183 gold: committed 0 / reserve 183 / remaining 0 / Sire, this settlement of the War with the Third Coalition — the table w …
   The table /   * Austria ▸ - Holding out (close) (39/50) White peace /       Blocker: National design /       Metternich allows that Austria is… persuadable — though it would seal their national design out of reach. /       + Add demand / Austria is the holdout. / ▸ Austria won't accept these terms yet. Use 'More generous' (or ease a court) until each accepts, then 'Submit for Review' to ratify. Su …
   Austria:
   Coverage:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, a white peace for the War with the Third Coalition — the table with Austria cannot be sealed as it stands: it would seal their national design out of reach. Author terms or hold …
   controls: <Austria ▸>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Bring Britain to the table]  [Bring Russia to the table]  <Grant>  <Decline>  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 85 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2711 of 2711 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   183 (−66 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose common peace with Austria  (sent from the diplomacy screen — typed, this line would open the whole table, not the court alone)
map: unchanged (52 labels)
```

```
#0053  click Back Out  ->  ok
  (clicked at (2250, 969))
view: <run>\frames\0053_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 85 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Bavaria petitions over settlement scope @(3231,64)]  [icon: Marshal Massena seeks an audience @(3273,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Peace Treaty Rejected @(3645,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +33 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2776 of 2776 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   183 (−66 next turn)
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
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (52 labels)
```

```
#0054  type Davout, attack Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0054_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Davout (23,985; expect about 135,561 with the corps likely to arrive, up to 160,788 if all march; certain 23,985; a bad day (1 in 10) 107,442) vs Archduke Charles (49,608 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — may make it from the mountains at Munich in time (about 47%); order 'Ney, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Davout are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
  The Emperor commands in person — every corps on this field fights +10% harder, if he marc
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   16,406 → 15,813
   Murat
   20,783 → 20,408
   Massena
   39,986 → 38,538
   ⚔
   Davout ◆
   Archduke Charles ◆
   marched to the guns
   23,985 → 22,539 → 22,200 after the advance
   49,608 → 39,860
   marched to the guns
   marched to the guns
   +1 corps in reserve — 417 lost
   Ney — could not reach the field
   THE GREAT SECOND BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Bavaria petitions over settlement scope @(3231,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Peace Treaty Rejected @(3610,64)]  [icon: Treaty with Prussia @(3645,64)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +36 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3162 of 3162 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   -30 (+102 next turn)
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
   Threat: 85/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
   ► what if Davout attacks Archduke Charles
   Were you to give the order, Sire:
   MUSTER — Davout (23,985; expect about 135,561 with the corps likely to arrive, up to 160,788 if all march; certain 23,985; a bad day (1 in 10) 107,442) vs Archduke Charles (49,608 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — may make it from the mountains at Munich in time (about 47%); order 'Ney, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Davout are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   Standing modifiers, already in the band: all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~8,498 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 141,686 we muster) would cost ~1,063g.
   Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal. Portugal paid 60 gold into the treasury.
   ► propose common peace with Austria  (sent from the diplomacy screen — typed, this line would open the whole table, not the court alone)
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► Davout, attack Archduke Charles
   ⚔ The Great Second Battle of Franconia ⚔
   MUSTER — Davout (23,985; expect about 135,561 with the corps likely to arrive, up to 160,788 if all march; certain 23,985; a bad day (1 in 10) 107,442) vs Archduke Charles (49,608 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — may make it from the mountains at Munich in time (about 47%); order 'Ney, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Davout are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Davout' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 99%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Franconia
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   Standing modifiers, already in the band: all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~8,498 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 141,686 we muster) would cost ~1,063g.
   Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Ask 'what if Davout attacks Archduke Charles' to read the muster before you commit — it costs nothing.
   [Combat] Davout attacks cautiously at unfavorable odds on his own numbers — his own 24k against 50k. (Cautious: -10% attack)
   [Combat] Davout's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Davout's attack! (+2%)
   Davout's forces advance steadily. Davout gains the advantage over Archduke Charles. Casualties: Davout's army 4,279, Archduke Charles 9,748. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -213g, Austria -487g. Our treasury stands at -30 gold. Davout advances into Franconia. (339 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney could not reach the battlefield in time.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 23,985 (lead) + 104,041 committed (Lannes, Murat, Massena, Napoleon) = 128,026.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,833 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "Precision carried it. It usually does."
   Massena fought like a man with something to prove — and proved it. His grievance is settled.
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Davout (Personality (cautious) -10%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Davout's own corps 1,446 | Archduke Charles 9,748
   Strength: Davout 23,985 → 22,539 → 22,200 after the advance | Archduke Charles 49,608 → 39,860
   Berthier: "Reinforcements from Lannes, Murat, Massena and Napoleon bolstered Davout's position — though Ney never arrived, Sire."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1967,326)  Davout +5(1943,431)  Brunswick(1958,287)  ?(1953,588)  Archduke John(1948,561)  Soult(1753,436)  Ney(1888,535)  Deroy(1913,471)  Dumonceau(1755,322)  Teulie(1909,589)  ?(2068,435)  ?(1959,376)  10k(1859,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0055  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0055_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3162 of 3162 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Davout's own corps 1,446 | Archduke Charles 9,748
   Strength: Davout 23,985 → 22,539 → 22,200 after the advance | Archduke Charles 49,608 → 39,860
   Berthier: "Reinforcements from Lannes, Murat, Massena and Napoleon bolstered Davout's position — though Ney never arrived, Sire."
map: unchanged (49 labels)
```

```
#0056  type Lannes, attack Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0056_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Lannes (15,813; expect about 162,031 with the corps likely to arrive) vs Archduke Charles (39,860 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL JOIN — Davout: stands on the field and will fight beside him
  WILL JOIN — Murat: stands on the field and will fight beside him — but he and Lannes are at odds; expect about half his weight
  WILL JOIN — Bernadotte: stands on the field and will fight beside him
  WILL JOIN — Massena: stands on the field and will fight beside him
  WILL JOIN — Napoleon: stands on the field and will fight beside him
  The Emperor commands in person — every corps on this field fights +10% harder.
  Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster standing there would lose ~8,221 men a turn to short supply.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 137,068 we muster) would cost ~1,028g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
  Napoleon shares the field at Franconia — his men wil
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Murat
   20,408 → 20,150
   Davout
   22,200 → 21,638
   Massena
   38,538 → 37,558
   ⚔
   Lannes ◆
   Archduke Charles ◆
   15,813 → 15,145
   39,860 → 16,772
   +3 corps in reserve — 1,199 lost
   THIRD BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 100 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Bavaria petitions over settlement scope @(3231,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Peace Treaty Rejected @(3610,64)]  [icon: Treaty with Prussia @(3645,64)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +39 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3209 of 3209 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   -213 (+270 next turn)
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
   [Combat] Davout attacks cautiously at unfavorable odds on his own numbers — his own 24k against 50k. (Cautious: -10% attack)
   [Combat] Davout's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Davout's attack! (+2%)
   Davout's forces advance steadily. Davout gains the advantage over Archduke Charles. Casualties: Davout's army 4,279, Archduke Charles 9,748. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -213g, Austria -487g. Our treasury stands at -30 gold. Davout advances into Franconia. (339 lost to march)
   [Alarm] Europe's alarm rises +8 — Won a battle +3, Won a decisive battle +5.
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney could not reach the battlefield in time.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 23,985 (lead) + 104,041 committed (Lannes, Murat, Massena, Napoleon) = 128,026.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,833 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "Precision carried it. It usually does."
   Massena fought like a man with something to prove — and proved it. His grievance is settled.
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Davout (Personality (cautious) -10%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Davout's own corps 1,446 | Archduke Charles 9,748
   Strength: Davout 23,985 → 22,539 → 22,200 after the advance | Archduke Charles 49,608 → 39,860
   Berthier: "Reinforcements from Lannes, Murat, Massena and Napoleon bolstered Davout's position — though Ney never arrived, Sire."
   ► Lannes, attack Archduke Charles
   ⚔ Third Battle of Franconia ⚔
   MUSTER — Lannes (15,813; expect about 162,031 with the corps likely to arrive) vs Archduke Charles (39,860 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him — but he and Lannes are at odds; expect about half his weight
   WILL JOIN — Bernadotte: stands on the field and will fight beside him
   WILL JOIN — Massena: stands on the field and will fight beside him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~8,221 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 137,068 we muster) would cost ~1,028g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Franconia — his men will absorb part of any losses.
   Ask 'what if Lannes attacks Archduke Charles' to read the muster before you commit — it costs nothing.
   Lannes holds them at Franconia while allies attack from Swabia! (+1 coordination)
   [Combat] Lannes leads the charge! (Aggressive: +15% attack)
   [Combat] Lannes's combined arms coordination! (+10% attack)
   Lannes launches a decisive assault. Lannes gains the advantage over Archduke Charles. Casualties: Lannes's army 3,667, Archduke Charles 23,088. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -183g, Austria -1154g. Our treasury stands at -213 gold. Franconia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +7 — Won a battle +3, Won a decisive battle +5.
   [!] Archduke Charles's broken army flees to Tyrol! (recovering for 2 turns)
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 15,813 (lead) + 146,218 committed (Ney, Davout, Murat, Bernadotte, Massena, Napoleon) = 162,031.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,999 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Lannes: "The field is ours! Give me leave and I will take the next one before dusk."
   Attack: Lannes (Personality (aggressive) +15%, Flanking +1%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 668 | Archduke Charles 23,088
   Strength: Lannes 15,813 → 15,145 | Archduke Charles 39,860 → 16,772
   Berthier: "Reinforcements! Ney marched onto the field beside Lannes. The enemy's advantage melted away."
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Ney +6(1943,431)  ?(1959,325)  Brunswick(1958,287)  ?(1953,588)  Archduke Charles(1940,561)  ?(1980,588)  Archduke John(1956,471)  Soult(1753,436)  Deroy(1901,535)  Dumonceau(1755,322)  Teulie(1909,589)  ?(2068,435)  ?(1959,376)  10k(1859,591)  ?(1889,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0057  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0057_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3209 of 3209 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 668 | Archduke Charles 23,088
   Strength: Lannes 15,813 → 15,145 | Archduke Charles 39,860 → 16,772
   Berthier: "Reinforcements! Ney marched onto the field beside Lannes. The enemy's advantage melted away."
map: unchanged (50 labels)
```

```
#0058  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0058_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 3209 of 3209 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 668 | Archduke Charles 23,088
   Strength: Lannes 15,813 → 15,145 | Archduke Charles 39,860 → 16,772
   Berthier: "Reinforcements! Ney marched onto the field beside Lannes. The enemy's advantage melted away."
map: unchanged (50 labels)
```

```
#0059  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0059_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 767 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (5)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -10 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +39 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3209 of 3209 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 668 | Archduke Charles 23,088
   Strength: Lannes 15,813 → 15,145 | Archduke Charles 39,860 → 16,772
   Berthier: "Reinforcements! Ney marched onto the field beside Lannes. The enemy's advantage melted away."
map: unchanged (50 labels)
```

```
#0060  click Austria  —  At War  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0060_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 447 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." / Recommendation: Permit me to observe, Sire, that every door is shut by arithmetic, not by malice: Open Settlement with Austria al …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Uncertain — a counter is likely]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Open Settlement with Austria alone  —  75 gold to Austria would carry her; the treasury can fund 0]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Uncertain]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3209 of 3209 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   -213 (+270 next turn)
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
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 668 | Archduke Charles 23,088
   Strength: Lannes 15,813 → 15,145 | Archduke Charles 39,860 → 16,772
   Berthier: "Reinforcements! Ney marched onto the field beside Lannes. The enemy's advantage melted away."
map: unchanged (50 labels)
```

```
#0061  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0061_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3209 of 3209 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 668 | Archduke Charles 23,088
   Strength: Lannes 15,813 → 15,145 | Archduke Charles 39,860 → 16,772
   Berthier: "Reinforcements! Ney marched onto the field beside Lannes. The enemy's advantage melted away."
map: unchanged (50 labels)
```

```
#0062  type what if Ney attacks Archduke John  ->  ok
  (typed and Enter)
view: <run>\frames\0062_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Ney (19,492; expect about 45,772 with the corps likely to arrive, up to 46,912 if all march; certain 19,492) vs Archduke John (substantial force) at Tyrol — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Tyrol
  WILL NOT — Lannes: has already marched this turn
  WILL NOT — Murat: has already marched this turn
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL NOT — Massena: has already marched this turn
  WILL NOT — Napoleon: has already marched this turn
  WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Tyrol
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 48,630 we muster) would cost ~365g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.

Nothing has been ordered, and nothi
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3699 of 3699 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   -213 (+270 next turn)
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
   ► what if Ney attacks Archduke John
   Were you to give the order, Sire:
   MUSTER — Ney (19,492; expect about 45,772 with the corps likely to arrive, up to 46,912 if all march; certain 19,492) vs Archduke John (substantial force) at Tyrol — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Tyrol
   WILL NOT — Lannes: has already marched this turn
   WILL NOT — Murat: has already marched this turn
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL NOT — Massena: has already marched this turn
   WILL NOT — Napoleon: has already marched this turn
   WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Tyrol
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 48,630 we muster) would cost ~365g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (50 labels)
```

```
#0063  click Envoys  ->  ok
  (clicked at (3387, 18))
view: <run>\frames\0063_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm', 'war_status_panel (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   ALLY SETTLEMENT PETITION - BAVARIA /  / the War with the Third Coalition — the table with Austria / Related claim: settlement /  / "The chancery of Bavaria petitions for Tyrol in the settlement of the War with the Third Coalition — the table with Austria. Bavaria fought beside France in this war and presses its claim." /  / Claim at issue: Tyrol against Austria /  / Basis: Bavaria fought beside Fr …
   controls: [Grant the Claim]  [Decline]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 4228 of 4228 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   -213 (+270 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 48,630 we muster) would cost ~365g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
map: unchanged (50 labels)
```

```
#0064  click Decline  ->  ok
  (clicked at (1834, 727))
view: <run>\frames\0064_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 100 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Bavaria petitions over settlement scope @(3231,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Peace Treaty Rejected @(3610,64)]  [icon: Treaty with Prussia @(3645,64)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 4294 of 4294 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   -213 (+270 next turn)
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
   Directing Talleyrand: decline ally petition
   The chancery of Bavaria records France's refusal in cool terms.
map: unchanged (50 labels)
```

```
#0065  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0065_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 4360 of 4360 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   -213 (+270 next turn)
   Inf:
   82,312
   Cav:
   16,750
   Art:
   10,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ 2 corps stand in peril — an enemy force of ~16,772 shares the field (Franconia).
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
map: unchanged (50 labels)
```

```
#0066  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0066_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 2
   BAVARIA / ──────────────────────────── / - Deroy moves to Franconia / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 97 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3897 of 3898 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   373 (+586 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   WILL JOIN — Bernadotte: stands on the field and will fight beside him
   WILL JOIN — Massena: stands on the field and will fight beside him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Standing modifiers, already in the band: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~8,221 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 137,068 we muster) would cost ~1,028g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Franconia — his men will absorb part of any losses.
   Ask 'what if Lannes attacks Archduke Charles' to read the muster before you commit — it costs nothing.
   Lannes holds them at Franconia while allies attack from Swabia! (+1 coordination)
   [Combat] Lannes leads the charge! (Aggressive: +15% attack)
   [Combat] Lannes's combined arms coordination! (+10% attack)
   Lannes launches a decisive assault. Lannes gains the advantage over Archduke Charles. Casualties: Lannes's army 3,667, Archduke Charles 23,088. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -183g, Austria -1154g. Our treasury stands at -213 gold. Franconia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Alarm] Europe's alarm rises +7 — Won a battle +3, Won a decisive battle +5.
   [!] Archduke Charles's broken army flees to Tyrol! (recovering for 2 turns)
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 15,813 (lead) + 146,218 committed (Ney, Davout, Murat, Bernadotte, Massena, Napoleon) = 162,031.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,999 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Lannes: "The field is ours! Give me leave and I will take the next one before dusk."
   Attack: Lannes (Personality (aggressive) +15%, Flanking +1%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 668 | Archduke Charles 23,088
   Strength: Lannes 15,813 → 15,145 | Archduke Charles 39,860 → 16,772
   Berthier: "Reinforcements! Ney marched onto the field beside Lannes. The enemy's advantage melted away."
   ► what if Ney attacks Archduke John
   Were you to give the order, Sire:
   MUSTER — Ney (19,492; expect about 45,772 with the corps likely to arrive, up to 46,912 if all march; certain 19,492) vs Archduke John (substantial force) at Tyrol — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Tyrol
   WILL NOT — Lannes: has already marched this turn
   WILL NOT — Murat: has already marched this turn
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL NOT — Massena: has already marched this turn
   WILL NOT — Napoleon: has already marched this turn
   WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Tyrol
   Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
   What Tyrol can feed is not known — the province is unscouted.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 48,630 we muster) would cost ~365g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Nothing has been ordered, and nothing spent.
   Directing Talleyrand: decline ally petition
   The chancery of Bavaria records France's refusal in cool terms.
   ⚠ 2 corps stand in peril — an enemy force of ~16,772 shares the field (Franconia).
   Press End Turn again, Enter, or type end turn again to end the turn anyway.
   ► end turn
   Your unratified settlement draft with Austria (1 clause) was set aside at turn's end.
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -281g | Other: +1437g | Upkeep: -3070g | Net: +586g
   Treasury: 373g
   Actions refreshed: 4/4
   Bavaria completes a market at Franconia.
   Bavaria completes a market at Munich.
   Supply shortage at Franconia: Ney loses 1,169 troops
   Supply shortage at Franconia: Davout loses 1,298 troops
   Supply shortage at Franconia: Lannes loses 908 troops
   Supply shortage at Franconia: Murat loses 1,209 troops
   Supply shortage at Franconia: Bernadotte loses 653 troops
   Supply shortage at Franconia: Massena loses 2,253 troops
   Supply shortage at Franconia: Napoleon loses 511 troops
   Supply shortage at Franconia: Deroy loses 1,253 troops
   Supply shortage at Tyrol: Archduke Charles loses 224 troops
   Supply shortage at Tyrol: Archduke John loses 267 troops
   Britain subsidizes Austria with 200 gold.
   Berthier notes that Massena no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Murat appears envious of Davout's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Murat is eyeing Archduke Charles's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Deroy(1967,305)  Ney +6(1943,431)  ?(1959,332)  Brunswick(1958,279)  ?(1953,579)  Archduke Charles(1940,540)  ?(1980,579)  Archduke John(1956,471)  Soult(1753,436)  Dumonceau(1755,322)  Teulie(1909,589)  ?(2068,435)  ?(1959,376)  10k(1859,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0067  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0067_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 97 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain binds Austria to the war @(3358,64)]  [icon: Blockade — Britain closes our ports @(3400,64)]  [icon: Bavaria petitions over settlement scope @(3442,64)]  [icon: Envoy from Denmark @(3484,64)]  [icon: Envoy from Saxony @(3526,64)]  [icon: Marshal Murat seeks an audience @(3568,64)]  [+6]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +38 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2204 of 2204 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   373 (+586 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Bavaria completes a market at Franconia.
   Bavaria completes a market at Munich.
   Supply shortage at Franconia: Ney loses 1,169 troops
   Supply shortage at Franconia: Davout loses 1,298 troops
   Supply shortage at Franconia: Lannes loses 908 troops
   Supply shortage at Franconia: Murat loses 1,209 troops
   Supply shortage at Franconia: Bernadotte loses 653 troops
   Supply shortage at Franconia: Massena loses 2,253 troops
   Supply shortage at Franconia: Napoleon loses 511 troops
   Supply shortage at Franconia: Deroy loses 1,253 troops
   Supply shortage at Tyrol: Archduke Charles loses 224 troops
   Supply shortage at Tyrol: Archduke John loses 267 troops
   Britain subsidizes Austria with 200 gold.
   Berthier notes that Massena no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Murat appears envious of Davout's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Murat is eyeing Archduke Charles's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Marshal Lannes holds the field at Franconia — Archduke Charles's corps is driven from Franconia yet again — broken, and fleeing.
   • Sire — Ney, Davout, Lannes, Murat, Bernadotte, Massena and Napoleon stand 125,400 men at Franconia, which feeds 60,000. 65,400 too many. 8,119 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the province. Swabia can feed 60,000 more and Munich can feed 37,500 more — a corps marched there ends it.
   • Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 373g (+586 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 32% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Franconia — 35,305 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Franconia — 20,340 — Awaiting orders.
   - Murat — Franconia — 18,941 — Awaiting orders.
   - Ney — Franconia — 18,323 — Awaiting orders.
   - Lannes — Franconia — 14,237 — Awaiting orders.
   - Bernadotte — Franconia — 10,235 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Starving — supply has failed at Franconia two turns running.
   - Napoleon — Franconia — 8,019 — Awaiting orders.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 19,635 [confirmed]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 8,001 men, at Franconia.
   Berthier notes that Massena no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Murat appears envious of Davout's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Murat is eyeing Archduke Charles's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 79).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at -2. 1 DP a turn, 1 so far.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0068  click Envoys (2)  ->  ok
  (clicked at (3391, 18))
view: <run>\frames\0068_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2204 of 2204 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0069  click#1 Accept  ->  ok
  (clicked at (1433, 456))
view: <run>\frames\0069_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
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
   DP: 6/7
   Threat 97 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Bavaria petitions over settlement scope @(3231,64)]  [icon: Marshal Murat seeks an audience @(3273,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Denmark @(3645,64)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   373 (+605 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
map: unchanged (50 labels)
```

```
#0070  click Accept  ->  ok
  (clicked at (1433, 500))
view: <run>\frames\0070_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 97 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Bavaria petitions over settlement scope @(3231,64)]  [icon: Marshal Murat seeks an audience @(3273,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Denmark @(3645,64)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1696 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   455 (+613 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Murat is eyeing Archduke Charles's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Marshal Lannes holds the field at Franconia — Archduke Charles's corps is driven from Franconia yet again — broken, and fleeing.
   • Sire — Ney, Davout, Lannes, Murat, Bernadotte, Massena and Napoleon stand 125,400 men at Franconia, which feeds 60,000. 65,400 too many. 8,119 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the province. Swabia can feed 60,000 more and Munich can feed 37,500 more — a corps marched there ends it.
   • Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 373g (+586 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 32% of French forces (an estimate — 2 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Franconia — 35,305 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Franconia — 20,340 — Awaiting orders.
   - Murat — Franconia — 18,941 — Awaiting orders.
   - Ney — Franconia — 18,323 — Awaiting orders.
   - Lannes — Franconia — 14,237 — Awaiting orders.
   - Bernadotte — Franconia — 10,235 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Starving — supply has failed at Franconia two turns running.
   - Napoleon — Franconia — 8,019 — Awaiting orders.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 19,635 [confirmed]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 8,001 men, at Franconia.
   Berthier notes that Massena no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Murat appears envious of Davout's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Murat is eyeing Archduke Charles's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 79).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at -2. 1 DP a turn, 1 so far.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (50 labels)
```

```
#0071  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0071_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (50 labels)
```

```
#0072  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0072_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 767 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +38 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (50 labels)
```

```
#0073  click Austria  —  At War  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0073_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 501 px] ──
   THE CABINET — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." / Recommendation: One could, of course, wait; one need not. Propose Armistice reads 51 of 50 today, Sire. It costs 1 DP. A truce ke …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Favorable]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Uncertain]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   455 (+613 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
map: unchanged (50 labels)
```

```
#0074  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0074_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 684 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / France concedes: /   • France releases a captured marshal to Austria / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 2 turns old and sta …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms](disabled: A truce settles nothing: no province or gold changes hands until it ends. Demands are pres)  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 97 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1741 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   455 (+613 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose armistice with Austria
map: unchanged (50 labels)
```

```
#0075  click Harsher terms  ->  ok
  (clicked at (1829, 674))
view: <run>\frames\0075_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 618 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / France demands: /   • Austria pays 300 gold per turn to France for as long as the treaty stands / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: HARSH /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the wa …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even harsher]  [Milder terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1762 of 1762 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   455 (+613 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify harsh
map: unchanged (50 labels)
```

```
#0076  click Milder terms  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0076_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 684 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / France concedes: /   • France releases a captured marshal to Austria / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 2 turns old and sta …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms](disabled: A truce settles nothing: no province or gold changes hands until it ends. Demands are pres)  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1785 of 1785 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   455 (+613 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: less generous
map: unchanged (50 labels)
```

```
#0077  click Send as suggested  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0077_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 97 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3220,64)]  [icon: Bavaria petitions over settlement scope @(3262,64)]  [icon: Marshal Murat seeks an audience @(3304,64)]  [icon: Treaty with Denmark @(3346,64)]  [icon: Treaty with Saxony @(3388,64)]  [Talleyrand at Prussia — Improving Relations]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +38 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1851 of 1851 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   455 (+613 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (50 labels)
```

```
#0078  type Massena, move to Munich  ->  ok
  (typed and Enter)
view: <run>\frames\0078_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena moves from Franconia to Munich (2,118 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1962 of 1962 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   455 (+697 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, move to Munich
   → Massena moves from Franconia to Munich (2,118 lost to march)
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Deroy(1967,326)  Ney +5(1943,431)  Brunswick(1958,287)  ?(1953,588)  Archduke Charles(1940,561)  ?(1980,588)  Archduke John(1956,471)  Soult(1753,436)  Massena(1901,535)  Dumonceau(1755,322)  Teulie(1909,589)  ?(2068,435)  ?(1959,376)  10k(1859,591)  ?(1889,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0079  type Davout, move to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0079_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Franconia to Swabia (217 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2072 of 2072 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   455 (+697 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Swabia
   → Davout moves from Franconia to Swabia (217 lost to march)
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Deroy(1955,347)  Ney +4(1943,431)  ?(1959,320)  Brunswick(1958,287)  Davout(1860,464)  ?(1953,588)  Archduke Charles(1940,561)  ?(1980,588)  Archduke John(1959,471)  Soult(1753,436)  Massena(1901,535)  Dumonceau(1755,322)  Teulie(1909,589)  ?(2068,435)  ?(1959,376)  10k(1859,591)  ?(1889,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0080  type Murat, move to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0080_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves from Franconia to Swabia (189 lost to march)
(Murat stands down from his intended attack — your orders reached him in time.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2205 of 2205 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   455 (+719 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, move to Swabia
   → Murat moves from Franconia to Swabia (189 lost to march)
   (Murat stands down from his intended attack — your orders reached him in time.)
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Deroy(1955,368)  Ney +3(1943,431)  ?(1959,325)  Brunswick(1958,287)  Davout(1847,464)  Murat(1872,438)  ?(1953,588)  Archduke Charles(1940,561)  ?(1980,588)  Archduke John(1956,471)  Soult(1753,436)  Massena(1901,535)  Dumonceau(1755,322)  Teulie(1909,589)  ?(2068,435)  ?(1959,396)  10k(1859,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0081  type Ney, move to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0081_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney moves from Franconia to Swabia (183 lost to march)
Swabia feeds 60,000; the 57,015 men standing there would lose ~1,139 a turn to crowding — too many corps on one province.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1721 of 1721 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   455 (+719 next turn)
   Inf:
   84,499
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 19,635 [confirmed]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 8,001 men, at Franconia.
   Berthier notes that Massena no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Murat appears envious of Davout's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Murat is eyeing Archduke Charles's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 79).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at -2. 1 DP a turn, 1 so far.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
   ► propose armistice with Austria
   Directing Talleyrand: modify harsh
   Directing Talleyrand: less generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
   ► Massena, move to Munich
   → Massena moves from Franconia to Munich (2,118 lost to march)
   [3/4 actions remaining]
   ► Davout, move to Swabia
   → Davout moves from Franconia to Swabia (217 lost to march)
   [2/4 actions remaining]
   ► Murat, move to Swabia
   → Murat moves from Franconia to Swabia (189 lost to march)
   (Murat stands down from his intended attack — your orders reached him in time.)
   [1/4 actions remaining]
   ► Ney, move to Swabia
   → Ney moves from Franconia to Swabia (183 lost to march)
   Swabia feeds 60,000; the 57,015 men standing there would lose ~1,139 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Lannes(1930,451)  Bernadotte(1930,376)  Napoleon(1964,409)  Deroy(1955,350)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1860,438)  Murat(1838,412)  ?(1953,588)  Archduke Charles(1940,561)  ?(1980,588)  Archduke John(2015,518)  Soult(1753,436)  Massena(1901,535)  Dumonceau(1755,322)  Teulie(1909,589)  ?(2068,435)  10k(1859,591)  ?(1857,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0082  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0082_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 3
   BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1768 of 1768 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,318 (+863 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at -2. 1 DP a turn, 1 so far.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony. Saxony paid 82 gold into the treasury.
   ► propose armistice with Austria
   Directing Talleyrand: modify harsh
   Directing Talleyrand: less generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
   ► Massena, move to Munich
   → Massena moves from Franconia to Munich (2,118 lost to march)
   [3/4 actions remaining]
   ► Davout, move to Swabia
   → Davout moves from Franconia to Swabia (217 lost to march)
   [2/4 actions remaining]
   ► Murat, move to Swabia
   → Murat moves from Franconia to Swabia (189 lost to march)
   (Murat stands down from his intended attack — your orders reached him in time.)
   [1/4 actions remaining]
   ► Ney, move to Swabia
   → Ney moves from Franconia to Swabia (183 lost to march)
   Swabia feeds 60,000; the 57,015 men standing there would lose ~1,139 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -329g | Other: +1512g | Upkeep: -2820g | Net: +863g
   Treasury: 1,318g
   Actions refreshed: 4/4
   Bavaria completes a market at Swabia.
   Crowded at Franconia: Lannes loses 427 troops to the press of 4 corps on one province's roads
   Crowded at Franconia: Bernadotte loses 307 troops to the press of 4 corps on one province's roads
   Crowded at Franconia: Napoleon loses 240 troops to the press of 4 corps on one province's roads
   Crowded at Franconia: Deroy loses 589 troops to the press of 4 corps on one province's roads
   Crowded at Swabia: Ney loses 362 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Davout loses 402 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Murat loses 375 troops to the press of 3 corps on one province's roads
   Switzerland loyalty 96 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Talleyrand returns from Austria with excellent news: they have accepted our proposal! The decisive factor was our military dominance.
   Treaty signed: At War → Armistice with Austria.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier reports that Bernadotte appears envious of Davout's laurels — he has grown cold and withholding.
   Berthier reports that Massena resents Ney's laurels again, 2 turns after the last — he has grown loud at the staff table about who is given the honours.
   Massena is eyeing Archduke John's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,481)  Archduke Charles(2043,443)  Lannes(1930,451)  Bernadotte(1930,376)  Napoleon(1964,409)  Deroy(1955,350)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1860,438)  Murat(1838,412)  ?(1501,602)  Castanos(1501,564)  ?(1953,588)  Archduke John(1948,561)  Soult(1753,436)  Massena(1901,535)  Dumonceau(1755,322)  Teulie(1909,589)  10k(1859,591)  ?(1857,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0083  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0083_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 93 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Hesse @(3189,64)]  [icon: Envoy from Papal States @(3231,64)]  [icon: Bavaria petitions over settlement scope @(3273,64)]  [icon: Marshal Murat seeks an audience @(3315,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1829 of 1829 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,318 (+863 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier reports that Bernadotte appears envious of Davout's laurels — he has grown cold and withholding.
   Berthier reports that Massena resents Ney's laurels again, 2 turns after the last — he has grown loud at the staff table about who is given the honours.
   Massena is eyeing Archduke John's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
   • Sire — London now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1,368 gold and shortens the road to 5 turns (not today: the treasury holds 1,318 gold).
   SITUATION
   France holds 28 regions. Treasury: 1,318g (+863 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Munich — 33,187 — Awaiting orders.
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Swabia — 19,721 — Awaiting orders.
   - Murat — Swabia — 18,377 — Awaiting orders.
   - Ney — Swabia — 17,778 — Awaiting orders.
   - Lannes — Franconia — 13,810 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franconia — 9,928 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Napoleon — Franconia — 7,779 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, two turns running.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 19,046 [confirmed]
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Supply cost you 2,113 men, at Franconia and Swabia.
   Switzerland loyalty 96 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Bernadotte appears envious of Davout's laurels — he has grown cold and withholding.
   Berthier reports that Massena resents Ney's laurels again, 2 turns after the last — he has grown loud at the staff table about who is given the honours.
   Massena is eyeing Archduke John's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Mack, our prisoner, is released for his ransom and returns to Vienna — an Austrian commander back in the field.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   Talleyrand has departed for the court of Austria.
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Austria have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 3 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — Austria is bound by Britain's bond not to sign alone; a peace with her runs through the table, where the bond is priced. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 7 French corps stand on Bavarian soil under the truce.
   Talleyrand returns from Austria with a response.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0084  click Envoys (2)  ->  ok
  (clicked at (3375, 18))
view: <run>\frames\0084_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 1829 of 1829 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0085  click#1 Accept  ->  ok
  (clicked at (1433, 478))
view: <run>\frames\0085_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   Threat 93 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3189,64)]  [icon: Marshal Murat seeks an audience @(3231,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Austria @(3610,64)]  [icon: Armistice Accepted @(3645,64)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1850 of 1850 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,318 (+878 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
map: unchanged (56 labels)
```

```
#0086  click Accept  ->  ok
  (clicked at (1433, 500))
view: <run>\frames\0086_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 93 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3189,64)]  [icon: Marshal Murat seeks an audience @(3231,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Austria @(3610,64)]  [icon: Armistice Accepted @(3645,64)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (56 labels)
```

```
#0087  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0087_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (56 labels)
```

```
#0088  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0088_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 225 of 751 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (10)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +37 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -17 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (56 labels)
```

```
#0089  click Prussia  ->  ok
  (clicked at (1825, 523))
view: <run>\frames\0089_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 266 px, 0 of 642 px] ──
   THE CABINET — Prussia
   DP: 7
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Open Borders   Relation: -2 (Wary) /  / "Our borders with Prussia are open, but trust remains shallow. A non-aggression pact would formalize the thaw." / Recommendation: Relations must improve before proposals will find purchase. Talleyrand is already at their court, Sire — net +8 a turn. / Talleyrand: "Prussia stands on the Emperor's roads, Sire — The P …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Wary (+8 over 1 turns) — +8 earned; paused 2 turns on your errand]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3).]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Armed Neutrality next (600g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
map: unchanged (56 labels)
```

```
#0090  click Licence  ->  ok
  (clicked at (1825, 566))
view: <run>\frames\0090_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE CABINET ASKS:
   "License Prussia's design against Hanover: no gold, 1 diplomatic point. France blesses it and pledges non-interference for 10 turns. The compact binds France: marching on Prussia before it lapses, or guaranteeing Hanover, is reneging — relations -25 and the strongest casus belli in Europe. License it? (yes / no)"
   controls: [Grant the licence]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1938 of 1938 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► sponsor Prussia against Hanover, 0 gold
   The Cabinet requests clarification...
map: unchanged (56 labels)
```

```
#0091  click Grant the licence  ->  ok
  (clicked at (1829, 524))
view: <run>\frames\0091_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 93 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3189,64)]  [icon: Marshal Murat seeks an audience @(3231,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Austria @(3610,64)]  [icon: Armistice Accepted @(3645,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2027 of 2027 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   > sponsor Prussia against Hanover, 0 gold confirmed
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (56 labels)
```

```
#0092  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0092_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2027 of 2027 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► sponsor Prussia against Hanover, 0 gold
   The Cabinet requests clarification...
   > sponsor Prussia against Hanover, 0 gold confirmed
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (56 labels)
```

```
#0093  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0093_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 449 of 752 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Ottoman Empire  —  Open Borders  |  -17 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Bavaria  —  Alliance  |  +54 (Friendly)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Hesse  —  Non-Aggression  |  0 (Neutral)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2027 of 2027 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► sponsor Prussia against Hanover, 0 gold
   The Cabinet requests clarification...
   > sponsor Prussia against Hanover, 0 gold confirmed
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (56 labels)
```

```
#0094  click Bavaria  ->  ok
  (clicked at (1825, 499))
view: <run>\frames\0094_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 200 px, 0 of 460 px] ──
   THE CABINET — Bavaria
   DP: 6
   TALLEYRAND'S ASSESSMENT — BAVARIA / Status: Alliance   Relation: +54 (Friendly) /  / "Our alliance with Bavaria stands firm. There is little to gain from change, and much to lose." / Recommendation: Talleyrand recommends: Propose Vassal / Talleyrand: "Bavaria stands on the Emperor's roads, Sire — The Protector of the Rhine (The Confederation of the Rhine). Proclaim one in the Cabinet (F1 → The Emp …
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)  —  Uncertain — a counter is likely]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2027 of 2027 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► sponsor Prussia against Hanover, 0 gold
   The Cabinet requests clarification...
   > sponsor Prussia against Hanover, 0 gold confirmed
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (56 labels)
```

```
#0095  click Propose Vassal  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0095_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France demands: /   • Bavaria pays 154 gold per turn to France for as long as the treaty stands /  / Harshness: Moderate / Acceptance estimate: ~40% (COUNTER expected) / Key obstacle: insufficient concessions / DP cost: 3 /  / "Sire, regarding the Vassalage proposal to Bavaria, I have prepared terms that reflect the current diplomatic climate."
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 93 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2072 of 2072 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose vassalization to Bavaria
map: unchanged (56 labels)
```

```
#0096  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0096_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France concedes: /   • France pays 142 gold to Bavaria /  / Harshness: Low / Acceptance estimate: ~49% (COUNTER expected) / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Bavaria."
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2094 of 2094 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (56 labels)
```

```
#0097  click Even more generous  ->  ok
  (clicked at (1829, 674))
view: <run>\frames\0097_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France concedes: /   • France pays 213 gold to Bavaria /   • France cedes 1 AP per turn to Bavaria for as long as the treaty stands /  / Harshness: Low / Acceptance estimate: ~68% (ACCEPT) / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Bavaria. We are offering everything short of the crown itself. Any more and we negotiate from our knees …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2116 of 2116 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (56 labels)
```

```
#0098  click Less generous  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0098_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France concedes: /   • France pays 142 gold to Bavaria /  / Harshness: Low / Acceptance estimate: ~49% (COUNTER expected) / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Bavaria."
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2138 of 2138 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: less generous
map: unchanged (56 labels)
```

```
#0099  click Send these terms  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0099_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 3/7
   Threat 93 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Austria @(3442,64)]  [icon: Armistice Accepted @(3484,64)]  [icon: Treaty with Hesse @(3526,64)]  [icon: Treaty with Papal States @(3568,64)]  [+9]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2204 of 2204 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Bavarian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
map: unchanged (56 labels)
```

```
#0100  click Generals (G) (1)  ->  ok
  (clicked at (228, 18))
view: <run>\frames\0100_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 6592 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  / SEEKS AN AUDIENCE — Murat /   / [5] Murat    [Cavalry]  France / The Cavalry Reserve - screening the Black Forest feint while the army wheels north of the Danube. / Aggressive: +15% attack, +5% more in aggressive stance. Fortify capped at 10%. Grows restless if idle too long. / Cava …
   controls: [Pin]  [icon @(2213,236)]  <Hear him — he seeks an audience>  <Fortify>  <Drill>  <Hold (2 AP)>  <▸ the doctrine>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (1 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2204 of 2204 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: modify generous
   Directing Talleyrand: less generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Bavarian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
map: unchanged (56 labels)
```

```
#0101  click Hear him  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0101_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   MURAT — Marshal Murat seeks an audience
   Give him a command is closed — Tyrol is held in force — sending him there needs an order of its own.
   "Sire — I have earned better than to watch Davout take the field while I hold a road." /  / Sire, Murat has expressed... displeasure about Davout's recent recognition. He requests a command worthy of his talents. /  / What each answer does / • Let it stand (Free) — Free, and it fixes nothing. For 2 more turns he brings NONE of his 20,150 men to any battle Davout leads, and the quarrel may harden f …
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Give him a command   [2 AP]](disabled: Tyrol is held in force — sending him there needs an order of its own.)  [Later (he will return)]
── TopBar (layer 75) [under a modal]: unchanged
── MarshalManagement (layer 50) [under a modal] [scrolled 0 of 6592 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2204 of 2204 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: modify generous
   Directing Talleyrand: less generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Bavarian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
map: unchanged (56 labels)
```

```
#0102  click Promise Glory  ->  ok
  (clicked at (1755, 702))
view: <run>\frames\0102_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 3/7
   Threat 93 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3220,64)]  [icon: Treaty with Austria @(3262,64)]  [icon: Armistice Accepted @(3304,64)]  [icon: Treaty with Hesse @(3346,64)]  [icon: Treaty with Papal States @(3388,64)]  [Talleyrand at Prussia — Improving Relations]
── MarshalManagement (layer 50) [scrolled 0 of 6524 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  /   OUR DOCTRINE — The Corps System  ▸ the doctrine /  /   THE EMPEROR /   / [8] Napoleon  [Infantry]  France / In the field at Franconia — The Presence goes where he stands. /   ★ The Presence  +10% here at Franconia  Every French corps fighting in the Emperor's province gains +10% a …
   controls: [Pin]  [icon @(2213,236)]  <▸ the doctrine>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (1 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2271 of 2271 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Murat bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
map: unchanged (56 labels)
```

```
#0103  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0103_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:3
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2271 of 2271 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Bavarian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
   Murat bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
map: unchanged (56 labels)
```

```
#0104  type Soult, fortify  ->  ok
  (typed and Enter)
view: <run>\frames\0104_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1829 of 1829 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   1,423 (+886 next turn)
   Inf:
   86,561
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Lannes — Franconia — 13,810 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franconia — 9,928 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Napoleon — Franconia — 7,779 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, two turns running.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 19,046 [confirmed]
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Supply cost you 2,113 men, at Franconia and Swabia.
   Switzerland loyalty 96 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Bernadotte appears envious of Davout's laurels — he has grown cold and withholding.
   Berthier reports that Massena resents Ney's laurels again, 2 turns after the last — he has grown loud at the staff table about who is given the honours.
   Massena is eyeing Archduke John's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Mack, our prisoner, is released for his ransom and returns to Vienna — an Austrian commander back in the field.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   Talleyrand has departed for the court of Austria.
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Austria have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 3 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — Austria is bound by Britain's bond not to sign alone; a peace with her runs through the table, where the bond is priced. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 7 French corps stand on Bavarian soil under the truce.
   Talleyrand returns from Austria with a response.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
   ► sponsor Prussia against Hanover, 0 gold
   The Cabinet requests clarification...
   > sponsor Prussia against Hanover, 0 gold confirmed
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► propose vassalization to Bavaria
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
   Directing Talleyrand: less generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Bavarian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
   Murat bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   ► Soult, fortify
   [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
   [1/4 actions remaining]
map: unchanged (56 labels)
```

```
#0105  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0105_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 641 px] ──
   ENEMY PHASE - Turn 4
   AUSTRIA / ──────────────────────────── / - Archduke John abandons fortified position / - Archduke John attacks Munich /     Assault on the garrison of Munich /       Garrison: 5,000 lost, 5,000 still under arms /       The assault cost them 3,404. / - Archduke John attacks Munich /     The garrison of Munich is destroyed. /     Region captured: Munich (was Bavaria) (secured) / - Archduke John atta …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 91 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,455 (+1,003 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   Talleyrand has departed for the court of Austria.
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Austria have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +39 for France (5 battles, 2 decisives kept); the war is 3 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — Austria is bound by Britain's bond not to sign alone; a peace with her runs through the table, where the bond is priced. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 7 French corps stand on Bavarian soil under the truce.
   Talleyrand returns from Austria with a response.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States. The Papal States paid 105 gold into the treasury.
   ► sponsor Prussia against Hanover, 0 gold
   The Cabinet requests clarification...
   > sponsor Prussia against Hanover, 0 gold confirmed
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► propose vassalization to Bavaria
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
   Directing Talleyrand: less generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Bavarian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
   Murat bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   ► Soult, fortify
   [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
   [1/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 5 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -368g | Other: +1574g | Upkeep: -2674g | Net: +1032g
   Treasury: 2,455g
   Actions refreshed: 4/4
   Soult's fortifications strengthen: +7% defense (max 12%)
   Supply shortage at Swabia: Ney loses 822 troops — 111 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Davout loses 912 troops — 124 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Murat loses 849 troops — 114 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Archduke John loses 341 troops
   Supply shortage at Munich: Massena loses 479 troops
   Supply shortage at Munich: Deroy loses 223 troops
   Garrison at Munich reinforced: 0 -> 2,000
   Kingdom of Italy loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 94 (-2): satellite drift
   Teulie's contingent comes home — 7,500 of 7,500 men.
   Talleyrand returns from Bavaria with a counter-proposal. They could not accept our terms, but offer an alternative:
   Vassalage between France and Bavaria
   - France offers 142 gold
   - France offers 100 gold
   Britain subsidizes Austria with 200 gold.
   Murat's resentment of Davout is set aside. He holds you to your word.
   Massena meant to go at the enemy on his own initiative, but no enemy stood within his reach when the moment came — he stands where he was, and his orders are unchanged.
   Berthier reports that Murat resents Davout's laurels again, 2 turns after the last — he has grown restless for glory.
   Murat presses his grievance against Davout again — but he holds to the Emperor's word, and the quarrel goes no further for now.
   Ney is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
   Davout is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
   Murat is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2025,479)  Archduke Charles(2043,451)  Lannes(1930,451)  Bernadotte(1971,425)  Napoleon(1964,399)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Davout(1847,438)  Murat(1872,375)  Archduke John(1872,349)  Soult(1753,436)  Massena(1889,535)  Deroy(1913,561)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,323)  ?(1959,372)  2k(1901,591)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  ?(1910,645)
```

```
#0106  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0106_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 91 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Prussia @(3186,64)]  [icon: Bavaria petitions over settlement scope @(3228,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: The Moniteur is out @(3607,64)]  [icon: Treaty with Austria @(3643,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   -2 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Swabia]  [War for Swabia — Austria, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2335 of 2335 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,455 (+1,003 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Massena meant to go at the enemy on his own initiative, but no enemy stood within his reach when the moment came — he stands where he was, and his orders are unchanged.
   Berthier reports that Murat resents Davout's laurels again, 2 turns after the last — he has grown restless for glory.
   Murat presses his grievance against Davout again — but he holds to the Emperor's word, and the quarrel goes no further for now.
   Ney is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
   Davout is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
   Murat is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 5
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Munich has been taken by Austria.
   • Sire — Swabia has been taken by Austria.
   • Sire — Ney, Davout and Murat stand 53,293 men at Swabia, which feeds 32,000. 21,293 too many. 3,722 men lost in 2 turns. Living off the land: this stripped country feeds a French army 80%. The Train des Équipages would lift it, but the Train des Équipages costs 3,500 gold; the treasury holds 2,455. No depot may be laid at Swabia — not controlled by France. Rhineland can feed 60,000 more and Franche-Comte can feed 52,500 more — a corps marched there ends it.
   • Sire — St Petersburg now pays London 300 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 2,455g (+1,032 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Munich — 32,708 — Awaiting orders.
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   > Davout — Swabia — 18,809 — Moving to Franche-Comte — arrives next turn.
   ⚠ Starving — supply has failed at Swabia two turns running.
   > Murat — Swabia — 17,528 — Moving to Franche-Comte — arrives next turn.
   ⚠ Starving — supply has failed at Swabia two turns running.
   > Ney — Swabia — 16,956 — Moving to Franche-Comte — arrives next turn.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Lannes — Franconia — 13,810 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franconia — 9,928 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Napoleon — Franconia — 7,779 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, two turns running.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Munich — 15,214 [confirmed]
   Archduke John — Swabia — 10,452 [confirmed]
   Archduke Charles — Bohemia — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +7% defense (max 12%)
   Supply cost you 3,062 men, at Swabia and Munich.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Murat's resentment of Davout is set aside. He holds you to your word.
   Massena meant to go at the enemy on his own initiative, but no enemy stood within his reach when the moment came — he stands where he was, and his orders are unchanged.
   Berthier reports that Murat resents Davout's laurels again, 2 turns after the last — he has grown restless for glory.
   Murat presses his grievance against Davout again — but he holds to the Emperor's word, and the quarrel goes no further for now.
   Mack, our prisoner, is released for his ransom and returns to Vienna — an Austrian commander back in the field.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   Talleyrand has departed for the court of Bavaria.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Munich passes from Bavaria to Austria.
   Massena stands on Munich, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   Swabia passes from Bavaria to Austria.
   Ney, Davout and Murat stand on Swabia, now Austria's soil — an armistice stands between us: they may march out, but no corps of ours may enter it again.
   Munich passes from Austria to Bavaria.
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Teulie's contingent comes home — 7,500 of 7,500 men.
   Talleyrand returns from Bavaria with a response.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Bavaria — Vassalage
   - Prussia — Non-Aggression Pact
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0107  click Envoys (2)  ->  ok
  (clicked at (3379, 18))
view: <run>\frames\0107_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Bavaria
   Counter Response
   Turn 5
   Counter response: Vassalage
   Terms: You pay Bavaria 142 gold at the signing · You pay Bavaria 100 gold at the signing
   A counter-offer is accepted or rejected in full — open to read the revised terms.
   WAITING
   Prussia
   Proposal
   Turn 4
   Incoming proposal: Non-Aggression Pact
   Terms: Proposal: Non-Aggression Pact · Prussia pays you 137 gold at the signing
   A great court's letter is answered in full — open to accept, haggle or refuse.
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2335 of 2335 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0108  click#1 Open  ->  ok
  (clicked at (2191, 294))
view: <run>\frames\0108_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   COUNTER-OFFER / Montgelas (Schemer) of Bavaria /  / In response to your Vassalage proposal, Bavaria offers modified terms: /  / Revised Terms: /   - You pay Bavaria 142 gold at the signing /   - You pay Bavaria 100 gold at the signing /  / Montgelas, coolly reckoning the gains: "Bavaria has marked where the weight of Europe now settles, and a prudent state places itself beside the rising power, ne …
   controls: [Accept Terms]  [Reject Terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2335 of 2335 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,455 (+1,003 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0109  click Accept Terms  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0109_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Non-Aggression Pact (agree not to attack) - up to +150 gold a turn in trade; breaking it costs 1 DP, -30 relation with the other signer and -10 with every other court / Terms: /   - Proposal: Non-Aggression Pact /   - Prussia pays you 137 gold at the signing /  / Hardenberg, stiffly: "Prussia's interest is the Rhine at peace and the ar …
   controls: [Accept]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 96 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2400 of 2400 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,213 (+1,474 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
map: unchanged (54 labels)
```

```
#0110  click Accept  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0110_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 96 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3186,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: The Moniteur is out @(3565,64)]  [icon: Treaty with Bavaria @(3607,64)]  [icon: Diplomatic Action Accepted @(3643,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   -2 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Swabia]  [War for Swabia — Austria, truce 4t]
── BottomLeftUI (layer 0) [scrolled 1694 of 1695 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,350 (+1,469 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   MARSHAL STATUS
   - Massena — Munich — 32,708 — Awaiting orders.
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   > Davout — Swabia — 18,809 — Moving to Franche-Comte — arrives next turn.
   ⚠ Starving — supply has failed at Swabia two turns running.
   > Murat — Swabia — 17,528 — Moving to Franche-Comte — arrives next turn.
   ⚠ Starving — supply has failed at Swabia two turns running.
   > Ney — Swabia — 16,956 — Moving to Franche-Comte — arrives next turn.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Lannes — Franconia — 13,810 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franconia — 9,928 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Napoleon — Franconia — 7,779 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, two turns running.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Munich — 15,214 [confirmed]
   Archduke John — Swabia — 10,452 [confirmed]
   Archduke Charles — Bohemia — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +7% defense (max 12%)
   Supply cost you 3,062 men, at Swabia and Munich.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Murat's resentment of Davout is set aside. He holds you to your word.
   Massena meant to go at the enemy on his own initiative, but no enemy stood within his reach when the moment came — he stands where he was, and his orders are unchanged.
   Berthier reports that Murat resents Davout's laurels again, 2 turns after the last — he has grown restless for glory.
   Murat presses his grievance against Davout again — but he holds to the Emperor's word, and the quarrel goes no further for now.
   Mack, our prisoner, is released for his ransom and returns to Vienna — an Austrian commander back in the field.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   Talleyrand has departed for the court of Bavaria.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Munich passes from Bavaria to Austria.
   Massena stands on Munich, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   Swabia passes from Bavaria to Austria.
   Ney, Davout and Murat stand on Swabia, now Austria's soil — an armistice stands between us: they may march out, but no corps of ours may enter it again.
   Munich passes from Austria to Bavaria.
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Teulie's contingent comes home — 7,500 of 7,500 men.
   Talleyrand returns from Bavaria with a response.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Bavaria — Vassalage
   - Prussia — Non-Aggression Pact
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0111  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0111_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0112  click Britain  ->  ok
  (clicked at (1825, 605))
view: <run>\frames\0112_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 508 px, 0 of 357 px] ──
   THE CABINET — Britain
   DP: 7
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War for Swabia   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Sire, the field reads -2 and no road carries. Open Settlement with Britain alone comes nearest at 9 of 50; Britain's consent (settlement legitimacy) is the weight (- …
   Cooldown: 2 turns
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Doubtful — may counter]  [Open Settlement — the whole table: Britain and Russia]  [Propose White Peace — the whole table: Britain and Russia]  [Propose Peace (3 DP)](disabled: Cooldown: 2 turns)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,350 (+1,469 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0113  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0113_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0114  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0114_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 225 of 751 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -77 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +36 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -16 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0115  click Austria  ->  ok
  (clicked at (1825, 483))
view: <run>\frames\0115_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 398 px, 0 of 325 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Swabia   Relation: -77 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Sire, the truce with Austria has 4 turns to run and the ledger stands: the war score reads +37 for France (5 battles, 2 decisives kept); the war is 4 turns old a …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1248g to buy off in turn).]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured.]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0116  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0116_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 398 px, 252 of 319 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Swabia   Relation: -77 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Sire, the truce with Austria has 4 turns to run and the ledger stands: the war score reads +37 for France (5 battles, 2 decisives kept); the war is 4 turns old a …
   Talleyrand is at Prussia's court — F1 → Prussia → Cancel
   Talleyrand is at Prussia's court — F1 → Prussia → Cancel
   Talleyrand is at Prussia's court — F1 → Prussia → Cancel
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn](disabled: Talleyrand is at Prussia's court — F1 → Prussia → Cancel)  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback](disabled: Talleyrand is at Prussia's court — F1 → Prussia → Cancel)  [Gather Intel (1 DP)  —  3 turns, then full intel for 5](disabled: Talleyrand is at Prussia's court — F1 → Prussia → Cancel)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0117  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0117_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 398 px, 146 of 303 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Swabia   Relation: -77 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Sire, the truce with Austria has 4 turns to run and the ledger stands: the war score reads +37 for France (5 battles, 2 decisives kept); the war is 4 turns old a …
   Talleyrand is at Prussia's court — F1 → Prussia → Cancel
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1248g to buy off in turn).]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured.]  [Propose Peace (2 DP)  —  Unlikely]  [Improve Relations (1 DP)  —  +8 relation/turn](disabled: Talleyrand is at Prussia's court — F1 → Prussia → Cancel)  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback](disabled: Talleyrand is at Prussia's court — F1 → Prussia → Cancel)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0118  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0118_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0119  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0119_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 225 of 751 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -77 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +36 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -16 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0120  click Prussia  ->  ok
  (clicked at (1825, 523))
view: <run>\frames\0120_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 266 px, 0 of 624 px] ──
   THE CABINET — Prussia
   DP: 7
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Non-Aggression   Relation: +3 (Neutral) /  / "We have Prussia's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: Relations must improve before proposals will find purchase. Talleyrand is already at their court, Sire — net +7 a turn. / Talleyrand: "Prussia stands on the Emperor's roads, Si …
   The compact already stands.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Wary → Neutral (+13, 1 turns) — +8 earned, +5 from our sponsorship; paused 3 turns on your errand]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3).](disabled: The compact already stands.)  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Armed Neutrality next (600g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1694 of 1695 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
map: unchanged (54 labels)
```

```
#0121  click Cancel: Improve Relations  ->  ok
  (clicked at (1825, 462))
view: <run>\frames\0121_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 96 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3351,64)]  [icon: The Moniteur is out @(3393,64)]  [icon: Treaty with Bavaria @(3435,64)]  [icon: Diplomatic Action Accepted @(3477,64)]  [icon: Treaty with Prussia @(3519,64)]  [icon: Gift of Friendship Accepted @(3561,64)]  [+10]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1783 of 1783 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,350 (+1,469 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (54 labels)
```

```
#0122  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0122_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1783 of 1783 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (54 labels)
```

```
#0123  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0123_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 225 of 751 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -77 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +36 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -16 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1783 of 1783 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (54 labels)
```

```
#0124  click Austria  ->  ok
  (clicked at (1825, 483))
view: <run>\frames\0124_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 233 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Swabia   Relation: -77 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Permit me to observe, Sire, that a truce is a clock, not a treaty: 4 turns, relations -77, and the ledger stands: the war score reads +37 for France (5 battles,  …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1248g to buy off in turn).]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured.]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1783 of 1783 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,350 (+1,469 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (54 labels)
```

```
#0125  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0125_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 152 of 242 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Swabia   Relation: -77 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Permit me to observe, Sire, that a truce is a clock, not a treaty: 4 turns, relations -77, and the ledger stands: the war score reads +37 for France (5 battles,  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured.]  [Propose Peace (2 DP)  —  Unlikely]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1783 of 1783 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (54 labels)
```

```
#0126  click Improve Relations  ->  ok
  (clicked at (1825, 559))
view: <run>\frames\0126_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Austria /  / "Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 96 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1828 of 1828 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,350 (+1,469 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► improve relations with Austria
map: unchanged (54 labels)
```

```
#0127  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0127_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 96 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3351,64)]  [icon: The Moniteur is out @(3393,64)]  [icon: Treaty with Bavaria @(3435,64)]  [icon: Diplomatic Action Accepted @(3477,64)]  [icon: Treaty with Prussia @(3519,64)]  [icon: Gift of Friendship Accepted @(3561,64)]  [+10]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   -2 →
   T:4
   controls: [THIRD COALITION  ▸]  [War for Swabia]  [War for Swabia — Austria, truce 4t]
── BottomLeftUI (layer 0) [scrolled 1893 of 1893 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,350 (+1,469 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (54 labels)
```

```
#0128  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0128_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1893 of 1893 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (54 labels)
```

```
#0129  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0129_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 225 of 751 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -77 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +36 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -16 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1893 of 1893 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (54 labels)
```

```
#0130  click Spain  ->  ok
  (clicked at (1825, 563))
view: <run>\frames\0130_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 178 px, 0 of 572 px] ──
   THE CABINET — Spain
   DP: 7
   TALLEYRAND'S ASSESSMENT — SPAIN / Status: Alliance   Relation: +36 (Friendly) /  / "Our alliance with Spain holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Our alliance with Spain frays, Sire — relations stand at 36, short of the 40 it holds on. Reassure Ally is shut while Talleyrand is at Austria's court — recall Talleyrand from Austria first (the …
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1893 of 1893 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,350 (+1,469 next turn)
   Inf:
   88,498
   Cav:
   22,000
   Art:
   12,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (54 labels)
```

```
#0131  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0131_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1893 of 1893 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (54 labels)
```

```
#0132  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0132_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 5
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1852 of 1854 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,488 (+1,995 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   TURN EVENTS
   Soult's fortifications strengthen: +7% defense (max 12%)
   Supply cost you 3,062 men, at Swabia and Munich.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Murat's resentment of Davout is set aside. He holds you to your word.
   Massena meant to go at the enemy on his own initiative, but no enemy stood within his reach when the moment came — he stands where he was, and his orders are unchanged.
   Berthier reports that Murat resents Davout's laurels again, 2 turns after the last — he has grown restless for glory.
   Murat presses his grievance against Davout again — but he holds to the Emperor's word, and the quarrel goes no further for now.
   Mack, our prisoner, is released for his ransom and returns to Vienna — an Austrian commander back in the field.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   Talleyrand has departed for the court of Bavaria.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Munich passes from Bavaria to Austria.
   Massena stands on Munich, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   Swabia passes from Bavaria to Austria.
   Ney, Davout and Murat stand on Swabia, now Austria's soil — an armistice stands between us: they may march out, but no corps of ours may enter it again.
   Munich passes from Austria to Bavaria.
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Teulie's contingent comes home — 7,500 of 7,500 men.
   Talleyrand returns from Bavaria with a response.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Bavaria — Vassalage
   - Prussia — Non-Aggression Pact
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Responding to Bavaria's proposal: accepted
   You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. You paid Bavaria 242 gold from the treasury.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia. Prussia paid 137 gold into the treasury.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
   ► end turn
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -22g | Admiralty: -90g | Blockade: -328g | Other: +1716g | Upkeep: -1728g | Net: +2138g
   Treasury: 4,488g
   Actions refreshed: 4/4
   Soult's fortifications strengthen: +9% defense (max 12%)
   Supply shortage at Franche-Comte: Ney loses 342 troops
   Supply shortage at Franche-Comte: Davout loses 380 troops
   Supply shortage at Franche-Comte: Murat loses 354 troops
   Supply shortage at Munich: Massena loses 463 troops
   Supply shortage at Munich: Deroy loses 215 troops
   Garrison at Munich reinforced: 2,000 -> 4,000
   Kingdom of Italy loyalty 96 (-2): satellite drift
   Switzerland loyalty 92 (-2): satellite drift
   Bavaria loyalty 62 (+2): the garrison's presence, relations with the lord
   Britain subsidizes Austria with 300 gold.
   Bernadotte's resentment of Davout has cooled with time.
   Massena's resentment of Ney has cooled with time.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2043,451)  ?(2045,479)  Archduke John(2032,375)  Lannes(1930,451)  Bernadotte(1971,425)  Napoleon(1964,399)  ?(1959,325)  Brunswick(1958,287)  Soult(1753,436)  Ney(1800,497)  Davout(1813,471)  Murat(1825,445)  Massena(1889,535)  Deroy(1913,561)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,322)  ?(1945,372)  4k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  ?(1910,645)
```

```
#0133  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0133_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from the Kingdom of Italy @(3185,64)]  [icon: Davout arrived @(3227,64)]  [icon: Murat arrived @(3269,64)]  [icon: Ney arrived @(3311,64)]  [icon: Bavaria petitions over settlement scope @(3353,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War for Swabia]  [War for Swabia — Austria, truce 3t]
── BottomLeftUI (layer 0) [scrolled 1961 of 1961 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,488 (+1,995 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Supply shortage at Franche-Comte: Murat loses 354 troops
   Supply shortage at Munich: Massena loses 463 troops
   Supply shortage at Munich: Deroy loses 215 troops
   Garrison at Munich reinforced: 2,000 -> 4,000
   Kingdom of Italy loyalty 96 (-2): satellite drift
   Switzerland loyalty 92 (-2): satellite drift
   Bavaria loyalty 62 (+2): the garrison's presence, relations with the lord
   Britain subsidizes Austria with 300 gold.
   Bernadotte's resentment of Davout has cooled with time.
   Massena's resentment of Ney has cooled with time.
   --- Strategic Order Updates ---
   Davout: Davout arrives at Franche-Comte. Davout: "Accomplished as ordered. The army is intact."
   Murat: Murat arrives at Franche-Comte. Murat: "Done — and I trust the next order has more fire in it."
   Ney: Ney arrives at Franche-Comte.
   Franche-Comte feeds 52,500; the 53,293 men standing there would lose ~1,076 a turn to short supply. Ney: "Accomplished. The men want a battle, not another road."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Massena and Deroy stand 47,244 men at Munich, which feeds 37,500. 9,744 too many. 1,157 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the province. Milan can feed 75,000 more and Franconia can feed 28,483 more — a corps marched there ends it.
   • Sire — the war with Bavaria and Prussia is over. Davout, Murat and Ney hold under your own orders and were not moved — the treaty offers a road, it does not overrule the Emperor. Their passage lapses with the corridor.
   SITUATION
   France holds 28 regions. Treasury: 4,488g (+2,138 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Munich — 32,245 — Awaiting orders.
   ⚠ Starving — supply has failed at Munich two turns running.
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Davout — Franche-Comte — 18,429 — Awaiting orders.
   - Murat — Franche-Comte — 17,174 — Awaiting orders.
   - Ney — Franche-Comte — 16,614 — Awaiting orders.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   ⚠ Starving — supply has failed at Munich two turns running.
   - Lannes — Franconia — 13,810 — 3 turns idle.
   - Bernadotte — Franconia — 9,928 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,779 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +9% defense (max 12%)
   Supply cost you 1,754 men, at Franche-Comte and Munich.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Bavaria loyalty 62 (+2): the garrison's presence, relations with the lord
   Bernadotte's resentment of Davout has cooled with time.
   Massena's resentment of Ney has cooled with time.
   DIPLOMATIC EVENTS
   Bavaria has been established under the protection of France.
   Sire — France and Bavaria have signed the Vassalage.
   Sire — Prussia and France have signed the Non-Aggression Pact.
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -66. 1 DP a turn, 1 so far.
   An envoy from the Kingdom of Italy has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0134  click Envoys (1)  ->  ok
  (clicked at (3377, 18))
view: <run>\frames\0134_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Marescalchi (Loyalist) of Kingdom of Italy /  / The petition: /   - Grant it, and the Kingdom of Italy's tribute of 375g a turn is remitted for 8 collections (3000g forgone): loyalty +4 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and the Kingdom of Italy loses 10 loyalty and its bond with us falls 20 (0  …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1961 of 1961 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,488 (+1,995 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0135  click Grant  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0135_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Davout arrived @(3185,64)]  [icon: Murat arrived @(3227,64)]  [icon: Ney arrived @(3269,64)]  [icon: Bavaria petitions over settlement scope @(3311,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,488 (+1,620 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (56 labels)
```

```
#0136  type Massena, move to Franconia  ->  ok
  (typed and Enter)
view: <run>\frames\0136_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena moves from Munich to Franconia (967 lost to march)
Franconia feeds 60,000; the 62,795 men standing there would lose ~1,925 a turn to short supply.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2159 of 2159 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,488 (+1,628 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, move to Franconia
   → Massena moves from Munich to Franconia (967 lost to march)
   Franconia feeds 60,000; the 62,795 men standing there would lose ~1,925 a turn to short supply.
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(2017,467)  Archduke John(2032,376)  Lannes +3(1943,441)  ?(1959,325)  Brunswick(1958,287)  Soult(1753,436)  Ney(1800,497)  Davout(1813,471)  Murat(1825,445)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,322)  ?(2068,435)  ?(1945,376)  4k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  ?(1910,645)
```

```
#0137  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0137_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Massena, move to Franconia
   → Massena moves from Munich to Franconia (967 lost to march)
   Franconia feeds 60,000; the 62,795 men standing there would lose ~1,925 a turn to short supply.
   [3/4 actions remaining]
map: unchanged (52 labels)
```

```
#0138  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0138_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 225 of 751 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -66 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +35 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -15 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Massena, move to Franconia
   → Massena moves from Munich to Franconia (967 lost to march)
   Franconia feeds 60,000; the 62,795 men standing there would lose ~1,925 a turn to short supply.
   [3/4 actions remaining]
map: unchanged (52 labels)
```

```
#0139  click Austria  ->  ok
  (clicked at (1825, 483))
view: <run>\frames\0139_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 398 px, 0 of 381 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Swabia   Relation: -66 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: If I may, Sire — 3 turns of quiet remain with Austria; the ledger stands: the war score reads +35 for France (5 battles, 2 decisives kept); the war is 5 turns ol …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile (+11 over 1 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1248g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,488 (+1,628 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Massena, move to Franconia
   → Massena moves from Munich to Franconia (967 lost to march)
   Franconia feeds 60,000; the 62,795 men standing there would lose ~1,925 a turn to short supply.
   [3/4 actions remaining]
map: unchanged (52 labels)
```

```
#0140  scroll 1828 500 down 6  ->  ok
  (scrolled down 6 at (1828, 500))
view: <run>\frames\0140_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 398 px, 146 of 357 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Swabia   Relation: -66 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: If I may, Sire — 3 turns of quiet remain with Austria; the ledger stands: the war score reads +35 for France (5 battles, 2 decisives kept); the war is 5 turns ol …
   Talleyrand is at Austria's court — F1 → Austria → Cancel
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1248g to buy off in turn).]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured.]  [Propose Peace (2 DP)  —  Unlikely]  [Improve Relations (1 DP)  —  +8 relation/turn](disabled: Talleyrand is at Austria's court — F1 → Austria → Cancel)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2159 of 2159 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Massena, move to Franconia
   → Massena moves from Munich to Franconia (967 lost to march)
   Franconia feeds 60,000; the 62,795 men standing there would lose ~1,925 a turn to short supply.
   [3/4 actions remaining]
map: unchanged (52 labels)
```

```
#0141  click Propose Peace  ->  ok
  (clicked at (1825, 566))
view: <run>\frames\0141_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 662 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms / Mutual: /   • Peace Treaty (end state of war) — France and Austria /  / Assessment: GENEROUS / The manner of this peace: none — it brings Austria to no terms the Emperor's designs read (two of her own provinces or her capital, her vassalage, or a compensated cession). /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the w …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2204 of 2204 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,488 (+1,628 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose peace with Austria
map: unchanged (52 labels)
```

```
#0142  click Adjust terms  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0142_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 420 px] ──
   This draft will not carry as it stands. / the War for Swabia — the table with Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria (no terms can move them). / Treasury 4,488 gold: committed 0 / reserve 500 / remaining 3,988 / Sire, this settlement of the War for Swabia — the table with …
   The table /   * Austria ▸ - Holding out White peace /       Blocker: Holding out /       Metternich has no standing to settle Austria here — there is no live quarrel between us to close. /       + Add demand — No terms can move Austria while no live war score binds them, Sire — set that court aside instead. / Austria is the holdout. / ▸ Austria cannot accept any terms in this settlement right now. …
   Austria:
   Coverage:
   Sire, a white peace for the War for Swabia — the table with Austria cannot be sealed as it stands: no single dominant pressure. Author terms or hold until the field shifts. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent. A separate peace with Austria: press her alone. It costs 2 diplomatic points; you have 5. /  / White Peace — on the held line: …
   controls: <Austria ▸>  [Ease Austria]  [Bring Britain to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,488 (+1,628 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: adjust terms
map: unchanged (52 labels)
```

```
#0143  click Back Out  ->  ok
  (clicked at (2250, 969))
view: <run>\frames\0143_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Davout arrived @(3185,64)]  [icon: Murat arrived @(3227,64)]  [icon: Ney arrived @(3269,64)]  [icon: Bavaria petitions over settlement scope @(3311,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War for Swabia]  [War for Swabia — Austria, truce 3t]
── BottomLeftUI (layer 0) [scrolled 1652 of 1652 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,488 (+1,628 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   France holds 28 regions. Treasury: 4,488g (+2,138 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Munich — 32,245 — Awaiting orders.
   ⚠ Starving — supply has failed at Munich two turns running.
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Davout — Franche-Comte — 18,429 — Awaiting orders.
   - Murat — Franche-Comte — 17,174 — Awaiting orders.
   - Ney — Franche-Comte — 16,614 — Awaiting orders.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   ⚠ Starving — supply has failed at Munich two turns running.
   - Lannes — Franconia — 13,810 — 3 turns idle.
   - Bernadotte — Franconia — 9,928 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,779 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +9% defense (max 12%)
   Supply cost you 1,754 men, at Franche-Comte and Munich.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Bavaria loyalty 62 (+2): the garrison's presence, relations with the lord
   Bernadotte's resentment of Davout has cooled with time.
   Massena's resentment of Ney has cooled with time.
   DIPLOMATIC EVENTS
   Bavaria has been established under the protection of France.
   Sire — France and Bavaria have signed the Vassalage.
   Sire — Prussia and France have signed the Non-Aggression Pact.
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -66. 1 DP a turn, 1 so far.
   An envoy from the Kingdom of Italy has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Kingdom of Italy — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► Massena, move to Franconia
   → Massena moves from Munich to Franconia (967 lost to march)
   Franconia feeds 60,000; the 62,795 men standing there would lose ~1,925 a turn to short supply.
   [3/4 actions remaining]
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (52 labels)
```

```
#0144  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0144_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 750 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1652 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (52 labels)
```

```
#0145  click Britain  ->  ok
  (clicked at (1825, 605))
view: <run>\frames\0145_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 530 px, 0 of 382 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War for Swabia   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — the court sees no reason to sign at -2: Propose Peace stands at 12 of 50; it wants deep-seated hostility (-10). A payment of 975 gold to Britain wou …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Doubtful — may counter]  [Open Settlement — the whole table: Britain and Russia]  [Open Settlement with Britain alone  —  opens with 975 gold to Britain staged — the sum that carries her]  [Propose White Peace — the whole table: Britain and Russia]  [Propose Peace (3 DP)](disabled: Cooldown: 1 turns)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1652 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,488 (+1,628 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (52 labels)
```

```
#0146  click Open Settlement with Britain alone  ->  ok
  (clicked at (1825, 550))
view: <run>\frames\0146_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 178 px] ──
   Settlement of the War for Swabia — the table with Britain — every court consents; submit it for review / the War for Swabia — the table with Britain - Separate settlement / Covered enemies: Britain / Still at war: Austria, Russia / Will carry as drafted — every court at or above 50. / Treasury 4,488 gold: committed 975 / reserve 500 / remaining 3,013 / Sire, this settlement of the War for Swabia — …
   The table /   * Britain ▸ - Will sign (50/50) Conceded: 975g /       Castlereagh signals that Britain will sign the settlement of the War for Swabia — the table with Britain. /       Conceded · France pays 975 gold (yours)  [-][+]  Remove /       + Add demand / This peace carries.
   Britain:
   Coverage:
   Sire, the settlement of the War for Swabia — the table with Britain stands ready for ratification. Acceptance reads as Will sign; what weighs heaviest: no single dominant pressure. /  / Allies and Standing /   * Austria - Seat at settlement (The Third Coalition) /   * France - Seat at settlement (France, war leader) /   * Bavaria - Consulted ally (France) /   * Britain - Seat at settlement (The Th …
   controls: <Britain ▸>  <Remove>  <+ Add demand>  [Demand more of Britain]  [Ease Britain]  [Separate peace with Britain](disabled: A recent proposal cooldown is still active for this court.)  [Bring Austria to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,488 (+1,628 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose common peace with Britain  (sent from the diplomacy screen — typed, this line would open the whole table without the sum staged)
map: unchanged (52 labels)
```

```
#0147  click Submit for Review  ->  ok
  (clicked at (1970, 969))
view: <run>\frames\0147_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Settlement of the War for Swabia — the table with Britain — ready for ratification / the War for Swabia — the table with Britain - Separate settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Britain / Still at war: Austria, Russia / Will carry as drafted — every court at or above 50. / Sire, this settlement of the War for Swabia — the ta …
   The table /   * Britain - Will sign (50/50) Conceded: 975g /       Castlereagh signals that Britain will sign the settlement of the War for Swabia — the table with Britain. / This peace carries.
   Sire, the settlement of the War for Swabia — the table with Britain stands ready for ratification. Acceptance reads as Will sign; what weighs heaviest: no single dominant pressure. /  / Allies and Standing /   * Austria - Seat at settlement (The Third Coalition) /   * France - Seat at settlement (France, war leader) /   * Bavaria - Consulted ally (France) /   * Britain - Seat at settlement (The Th …
   controls: [Ratify Settlement]  [Open War Detail]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1719 of 1719 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,488 (+1,628 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: submit settlement for review
map: unchanged (52 labels)
```

```
#0148  click Ratify Settlement  ->  ok
  (clicked at (1455, 879))
view: <run>\frames\0148_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3185,64)]  [icon: Davout arrived @(3227,64)]  [icon: Murat arrived @(3269,64)]  [icon: Ney arrived @(3311,64)]  [icon: Bavaria petitions over settlement scope @(3353,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]
── DiplomaticLedger (layer 50) [scrolled 0 of 1454 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Austria
   DP: 5/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (4 turns ago) /  / Naples ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (4 turns ago) /  / Prussia ↔ France: Non Aggression /   Clauses: Gold payment: 137 (Prussia -> France) /   Duration: permanent   C …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Settlement of the War for Swabia — the table with Britain: Gold indemnity: 975 gold from France to Britain.>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1873 of 1873 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,513 (+2,021 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: confirm settlement
   Settlement Ratified: the War for Swabia — the table with Britain (3 pairs resolved).
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0149  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0149_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Russia
   0 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with Russia]  [War for Swabia — Austria, truce 3t]
── BottomLeftUI (layer 0) [scrolled 1873 of 1873 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0150  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0150_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 766 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (1)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1873 of 1873 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0151  click Russia  ->  ok
  (clicked at (1825, 605))
view: <run>\frames\0151_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 376 px, 0 of 403 px] ──
   THE CABINET — Russia
   DP: 5
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: At War — the War for Swabia   Relation: -80 (Hostile) /  / "The war with Russia grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Permit me to observe, Sire, that a level war is the dearest kind to end: Propose Peace reads 24 of 50; it wants deep-seated hostility (-10). A payment of 950 gold to R …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Doubtful — may counter]  [Open Settlement — with Russia  —  opens with 950 gold to Russia staged — the sum that carries her]  [Propose White Peace — with Russia]  [Propose Peace (3 DP)  —  Unlikely]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1873 of 1873 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,513 (+2,021 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0152  click Open Settlement  ->  ok
  (clicked at (1825, 506))
view: <run>\frames\0152_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 178 px] ──
   Settlement of the War for Swabia — the table with Russia — every court consents; submit it for review / the War for Swabia — the table with Russia - Separate settlement / Covered enemies: Russia / Still at war: Austria / Will carry as drafted — every court at or above 50. / Treasury 3,513 gold: committed 950 / reserve 500 / remaining 2,063 / Sire, this settlement of the War for Swabia — the table  …
   The table /   * Russia ▸ - Will sign (50/50) Conceded: 950g /       Czartoryski signals that Russia will sign the settlement of the War for Swabia — the table with Russia. /       Conceded · France pays 950 gold (yours)  [-][+]  Remove /       + Add demand / This peace carries.
   Russia:
   Coverage:
   Sire, the settlement of the War for Swabia — the table with Russia stands ready for ratification. Acceptance reads as Will sign; what weighs heaviest: no single dominant pressure. /  / Allies and Standing /   * Austria - Seat at settlement (The Third Coalition, war leader) /   * France - Seat at settlement (France, war leader) /   * Bavaria - Consulted ally (France) /   * Kingdom of Italy - No set …
   controls: <Russia ▸>  <Remove>  <+ Add demand>  [Demand more of Russia]  [Ease Russia]  [Separate peace with Russia — alone: 33 (Doubtful — may counter)]  [Bring Austria to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1919 of 1919 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,513 (+2,021 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose common peace with Russia  (sent from the diplomacy screen — typed, this line would open the whole table without the sum staged)
map: unchanged (52 labels)
```

```
#0153  click Submit for Review  ->  ok
  (clicked at (1970, 969))
view: <run>\frames\0153_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Settlement of the War for Swabia — the table with Russia — ready for ratification / the War for Swabia — the table with Russia - Separate settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Russia / Still at war: Austria / Will carry as drafted — every court at or above 50. / Sire, this settlement of the War for Swabia — the table with Ru …
   The table /   * Russia - Will sign (50/50) Conceded: 950g /       Czartoryski signals that Russia will sign the settlement of the War for Swabia — the table with Russia. / This peace carries.
   Sire, the settlement of the War for Swabia — the table with Russia stands ready for ratification. Acceptance reads as Will sign; what weighs heaviest: no single dominant pressure. /  / Allies and Standing /   * Austria - Seat at settlement (The Third Coalition, war leader) /   * France - Seat at settlement (France, war leader) /   * Bavaria - Consulted ally (France) /   * Kingdom of Italy - No set …
   controls: [Ratify Settlement]  [Open War Detail]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1940 of 1940 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,513 (+2,021 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: submit settlement for review
map: unchanged (52 labels)
```

```
#0154  click Ratify Settlement  ->  ok
  (clicked at (1455, 879))
view: <run>\frames\0154_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 47 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified (x2) @(3185,64)]  [icon: Davout arrived @(3227,64)]  [icon: Murat arrived @(3269,64)]  [icon: Ney arrived @(3311,64)]  [icon: Bavaria petitions over settlement scope @(3353,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]
── DiplomaticLedger (layer 50) [scrolled 0 of 1784 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Austria
   DP: 5/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (4 turns ago) /  / Naples ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (4 turns ago) /  / Prussia ↔ France: Non Aggression /   Clauses: Gold payment: 137 (Prussia -> France) /   Duration: permanent   C …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Settlement of the War for Swabia — the table with Russia: Gold indemnity: 950 gold from France to Russia.>  <v Settlement of the War for Swabia — the table with Britain: Gold indemnity: 975 gold from France to Britain.>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2094 of 2094 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   2,563 (+2,187 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: confirm settlement
   Settlement Ratified: the War for Swabia — the table with Russia (1 pair resolved).
   Settlement Ratified
   1 hostile pair resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 1
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0155  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0155_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War for Swabia — Austria, truce 3t]
── BottomLeftUI (layer 0) [scrolled 2094 of 2094 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Settlement Ratified
   1 hostile pair resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 1
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0156  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0156_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -66 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2094 of 2094 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   1 hostile pair resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 1
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0157  click Austria  ->  ok
  (clicked at (1825, 605))
view: <run>\frames\0157_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 376 px, 0 of 381 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Swabia   Relation: -66 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Sire, the truce with Austria has 3 turns to run and the ledger stands: the war score reads +35 for France (5 battles, 2 decisives kept); the war is 5 turns old a …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile (+11 over 1 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1056g) (1 DP + 1056g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1056g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2094 of 2094 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   2,563 (+2,187 next turn)
   Inf:
   90,335
   Cav:
   23,750
   Art:
   13,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   1 hostile pair resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 1
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0158  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0158_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2094 of 2094 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Settlement Ratified
   1 hostile pair resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 1
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0159  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0159_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 6
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 46 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1679 of 1680 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,837 (+2,176 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   Responding to the Kingdom of Italy's proposal: accepted
   The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► Massena, move to Franconia
   → Massena moves from Munich to Franconia (967 lost to march)
   Franconia feeds 60,000; the 62,795 men standing there would lose ~1,925 a turn to short supply.
   [3/4 actions remaining]
   ► propose peace with Austria
   Directing Talleyrand: adjust terms
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► propose common peace with Britain  (sent from the diplomacy screen — typed, this line would open the whole table without the sum staged)
   Directing Talleyrand: submit settlement for review
   Directing Talleyrand: confirm settlement
   Settlement Ratified: the War for Swabia — the table with Britain (3 pairs resolved).
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   ► propose common peace with Russia  (sent from the diplomacy screen — typed, this line would open the whole table without the sum staged)
   Directing Talleyrand: submit settlement for review
   Directing Talleyrand: confirm settlement
   Settlement Ratified: the War for Swabia — the table with Russia (1 pair resolved).
   Settlement Ratified
   1 hostile pair resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 1
   Opening diplomatic ledger to settlement…
   ► end turn
   Your unratified settlement draft with Austria (1 clause) was set aside at turn's end.
   ═══════════════════════════════════════
   TURN 7 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -24g | Other: +1346g | Upkeep: -1638g | Net: +2274g
   Treasury: 4,837g
   Actions refreshed: 4/4
   Soult's fortifications strengthen: +11% defense (max 12%)
   Supply shortage at Franconia: Lannes loses 423 troops
   Supply shortage at Franconia: Bernadotte loses 304 troops
   Supply shortage at Franconia: Massena loses 960 troops
   Supply shortage at Franconia: Napoleon loses 238 troops
   Crowded at Franche-Comte: Ney loses 332 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Davout loses 368 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 343 troops to the press of 3 corps on one province's roads
   Garrison at Munich reinforced: 4,000 -> 6,000
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 90 (-2): satellite drift
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: Open Borders → Peace.
   Russia and Naples have signed a Non-Aggression Pact.
   Murat's resentment of Davout has cooled with time.
   Berthier reports that Bernadotte resents Davout's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   The rivalry between Bernadotte and Davout has become entrenched. The wound will not close on its own.
   Berthier notes that Massena has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(2017,467)  Archduke John(2032,376)  Lannes +3(1943,441)  ?(1959,325)  Brunswick(1958,287)  ?(1501,602)  Paget(1501,564)  Soult(1753,436)  Ney(1800,497)  Davout(1813,471)  Murat(1825,445)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(2068,435)  ?(1945,376)  6k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  ?(1910,645)
```

```
#0160  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0160_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['marshal_petition', 'war_status_panel (not modal)'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   BERNADOTTE — Marshal Bernadotte demands to be heard
   Give him a command is closed — There is no enemy within his reach to send him against.
   "My corps is in good order, Sire. It has been in good order for some time now." /  / Sire, Bernadotte submitted a summary of his corps' service this season. It is accurate, and it is longer than it needed to be. The breach between them has become entrenched; he presses the point with unusual heat. /  / What each answer does / • Let it stand (Free) — Free, and it fixes nothing. For 2 more turns he  …
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Give him a command   [2 AP]](disabled: There is no enemy within his reach to send him against.)  [Later (he will return)]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 46 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Holland @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Settlement Ratified (x2) @(3477,64)]  [icon: Davout arrived @(3519,64)]  [icon: Murat arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   controls: [War for Swabia — Austria, truce 2t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1851 of 1851 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,837 (+2,176 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier reports that Bernadotte resents Davout's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   The rivalry between Bernadotte and Davout has become entrenched. The wound will not close on its own.
   Berthier notes that Massena has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 7
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — the war with Britain is over. The peace grants safe passage home.
   • Sire — our peace binds Britain for 4 more turns and Russia for 4 more turns; then each may join a league (relations −89 and −79).
   SITUATION
   France holds 28 regions. Treasury: 4,837g (+2,274 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Franconia — 30,318 — Awaiting orders.
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Murat — Franche-Comte — 16,831 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Ney — Franche-Comte — 16,282 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   ⚠ Starving — supply has failed at Munich two turns running.
   - Lannes — Franconia — 13,387 — 4 turns idle.
   - Bernadotte — Franconia — 9,624 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,541 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   Paget — Gascony — screening force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +11% defense (max 12%)
   Supply cost you 2,968 men, at Franconia and Franche-Comte.
   2 satellites drifted — Holland and Switzerland.
   Murat's resentment of Davout has cooled with time.
   Berthier reports that Bernadotte resents Davout's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   The rivalry between Bernadotte and Davout has become entrenched. The wound will not close on its own.
   Berthier notes that Massena has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Settlement of the War for Swabia — the table with Britain: Gold indemnity: 975 gold from France to Britain.
   The coalition against France has dissolved.
   Settlement of the War for Swabia — the table with Russia: Gold indemnity: 950 gold from France to Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -55. 1 DP a turn, 2 so far.
   An envoy from Holland has arrived with a petition.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
   The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
   And Sardinia stirs at its own design.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. Held by our truce: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0161  click Promise Glory  ->  ok
  (clicked at (1755, 702))
view: <run>\frames\0161_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Schimmelpenninck (Loyalist) of Holland /  / The petition: /   - Grant it, and Holland's tribute of 337g a turn is remitted for 8 collections (2696g forgone): loyalty +2 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Holland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loya …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 46 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1916 of 1916 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,837 (+2,176 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
map: unchanged (53 labels)
```

```
#0162  click Grant  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0162_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 46 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Settlement Ratified (x2) @(3435,64)]  [icon: Davout arrived @(3477,64)]  [icon: Murat arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War for Swabia — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 1982 of 1982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,837 (+1,839 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0163  click Diplomacy (D)  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0163_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 3065 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Austria
   DP: 5/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  /   Britain [Neutral] — PEACE  Relation: -89 (Hostile) /   Laws: the Orders in Council and the Militia Transfer (300 gold a turn) /   Doctrine: The Line Holds; flaw: Irreplaceable (uncured — the Militia Transfer would end it once the Horse Guards R …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1982 of 1982 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,837 (+1,839 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0164  click BALANCE OF EUROPE  ->  ok
  (clicked at (1665, 273))
view: <run>\frames\0164_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 662 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Austria
   DP: 5/7
   BALANCE OF EUROPE / ──────────────── / The courts are recovering from the last coalition. Cooldown: 4 turns. Europe's alarm stands at 46; no new coalition gathers below 60. /  / THE EMPEROR'S DESIGNS / No road is proclaimed. Three roads — one proclamation, and it cannot be undone. /   Road I — The Protector of the Rhine /     • The Confederation of the Rhine — 1 of 3 courts under the Emperor's pro …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [BALANCE OF EUROPE](disabled: You are reading this book)  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1982 of 1982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0165  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0165_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War for Swabia — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 1982 of 1982 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0166  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0166_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -55 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1982 of 1982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0167  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0167_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 727 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -55 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +34 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -14 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1982 of 1982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0168  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0168_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 544 of 744 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (4)
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Bavaria  —  Vassal  |  +53 (Friendly)]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Britain  —  Peace  |  -89 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1982 of 1982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0169  click Britain  —  Peace  ->  ok
  (clicked at (1825, 627))
view: <run>\frames\0169_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 548 px] ──
   THE CABINET — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: Peace   Relation: -89 (Hostile) /  / "Relations with Britain remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. Improve Relations is shut while Talleyrand is at Austria's court — recall Talleyrand from Austria first (t …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1116g) (1 DP + 1116g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. No other design wakes after it.]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured.]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1982 of 1982 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0170  click Buy Off Their Design  ->  ok
  (clicked at (1825, 551))
view: <run>\frames\0170_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE CABINET ASKS:
   "Buy off Britain's design — The Low Countries: 1,116 gold and 1 diplomatic point. The treasury holds 4,837 gold and would hold 3,721 after. The want sleeps 15 turns; it does not die — marching on Britain inside the term is reneging, and it returns the heavier: their will against us +15, relations -25 and the strongest casus belli in Europe. No other design wakes after it. Buy it off? (yes / no)"
   controls: [Buy it off]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 46 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2049 of 2049 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,837 (+1,839 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► buy off Britain
   The Cabinet requests clarification...
map: unchanged (53 labels)
```

```
#0171  click Buy it off  ->  ok
  (clicked at (1829, 549))
view: <run>\frames\0171_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 46 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Settlement Ratified (x2) @(3435,64)]  [icon: Davout arrived @(3477,64)]  [icon: Murat arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War for Swabia — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 2137 of 2137 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,721 (+1,887 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   > buy off Britain, 1116 gold confirmed
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (53 labels)
```

```
#0172  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0172_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -55 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2137 of 2137 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Britain
   The Cabinet requests clarification...
   > buy off Britain, 1116 gold confirmed
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (53 labels)
```

```
#0173  scroll 1828 500 down 20  ->  ok
  (scrolled down 20 at (1828, 500))
view: <run>\frames\0173_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 687 of 727 px] ──
   THE CABINET
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Britain  —  Peace  |  -84 (Hostile)]  [Russia  —  Peace  |  -79 (Hostile)]  [Sweden  —  Peace  |  -54 (Hostile)]  [Naples  —  Peace  |  -24 (Wary)]  [Hanover  —  Peace  |  -44 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2137 of 2137 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Britain
   The Cabinet requests clarification...
   > buy off Britain, 1116 gold confirmed
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (53 labels)
```

```
#0174  click Russia  —  Peace  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0174_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 68 px, 0 of 602 px] ──
   THE CABINET — Russia
   DP: 4
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Peace   Relation: -79 (Hostile) /  / "Relations with Russia remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. Improve Relations is shut while Talleyrand is at Austria's court — recall Talleyrand from Austria first (the …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Sweden — gold flows, the compact binds both ends (§3.3).]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [↳ 400g a turn]  [Buy Off Their Design (1152g) (1 DP + 1152g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. No other design wakes after it.]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2137 of 2137 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,721 (+1,887 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Britain
   The Cabinet requests clarification...
   > buy off Britain, 1116 gold confirmed
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (53 labels)
```

```
#0175  click Buy Off Their Design  ->  ok
  (clicked at (1825, 638))
view: <run>\frames\0175_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE CABINET ASKS:
   "Buy off Russia's design — The Gulf and the Straits: 1,152 gold and 1 diplomatic point. The treasury holds 3,721 gold and would hold 2,569 after. The want sleeps 15 turns; it does not die — marching on Russia inside the term is reneging, and it returns the heavier: their will against us +15, relations -25 and the strongest casus belli in Europe. No other design wakes after it. Buy it off? (yes / n …
   controls: [Buy it off]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 46 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2204 of 2204 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   3,721 (+1,887 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► buy off Russia
   The Cabinet requests clarification...
map: unchanged (53 labels)
```

```
#0176  click Buy it off  ->  ok
  (clicked at (1829, 549))
view: <run>\frames\0176_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 3/7
   Threat 46 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Settlement Ratified (x2) @(3435,64)]  [icon: Davout arrived @(3477,64)]  [icon: Murat arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+25]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War for Swabia — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 1718 of 1718 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   2,569 (+1,937 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   ⚠ Starving — supply has failed at Munich two turns running.
   - Lannes — Franconia — 13,387 — 4 turns idle.
   - Bernadotte — Franconia — 9,624 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,541 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   Paget — Gascony — screening force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +11% defense (max 12%)
   Supply cost you 2,968 men, at Franconia and Franche-Comte.
   2 satellites drifted — Holland and Switzerland.
   Murat's resentment of Davout has cooled with time.
   Berthier reports that Bernadotte resents Davout's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   The rivalry between Bernadotte and Davout has become entrenched. The wound will not close on its own.
   Berthier notes that Massena has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Settlement of the War for Swabia — the table with Britain: Gold indemnity: 975 gold from France to Britain.
   The coalition against France has dissolved.
   Settlement of the War for Swabia — the table with Russia: Gold indemnity: 950 gold from France to Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -55. 1 DP a turn, 2 so far.
   An envoy from Holland has arrived with a petition.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
   The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
   And Sardinia stirs at its own design.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. Held by our truce: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► buy off Britain
   The Cabinet requests clarification...
   > buy off Britain, 1116 gold confirmed
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   The Cabinet requests clarification...
   > buy off Russia, 1152 gold confirmed
   Russia's design — The Gulf and the Straits — is bought off for 1152 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (53 labels)
```

```
#0177  type Ney, move to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0177_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins marching to Rhineland (distance: 2). Moved to Lorraine. Route: Lorraine -> Rhineland.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1829 of 1829 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   2,569 (+1,937 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, move to Rhineland
   Ney begins marching to Rhineland (distance: 2). Moved to Lorraine. Route: Lorraine -> Rhineland.
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(2017,467)  Archduke John(2032,376)  Lannes +3(1943,441)  ?(1959,325)  Brunswick(1958,287)  ?(1501,602)  Paget(1501,564)  Ney(1740,436)  Soult(1785,418)  Davout(1801,497)  Murat(1825,471)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(2068,435)  ?(1945,376)  6k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1698,420)  ?(1910,645)
```

```
#0178  type Murat, move to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0178_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves from Franche-Comte to Rhineland
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   2,569 (+1,937 next turn)
   Inf:
   92,172
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, move to Rhineland
   → Murat moves from Franche-Comte to Rhineland
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(2017,467)  Archduke John(2032,376)  Lannes +3(1943,441)  ?(1959,325)  Brunswick(1958,287)  Murat(1827,397)  ?(1501,602)  Paget(1501,564)  Ney(1740,436)  Soult(1785,423)  Davout(1813,497)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(2068,435)  ?(1945,376)  6k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1698,420)  ?(1910,645)
```

```
#0179  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0179_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 7
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1876 of 1878 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,569 (+1,914 next turn)
   Inf:
   94,009
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Settlement of the War for Swabia — the table with Russia: Gold indemnity: 950 gold from France to Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -55. 1 DP a turn, 2 so far.
   An envoy from Holland has arrived with a petition.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
   The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
   And Sardinia stirs at its own design.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. Held by our truce: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Bernadotte bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   [3/4 actions remaining]
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► buy off Britain
   The Cabinet requests clarification...
   > buy off Britain, 1116 gold confirmed
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   The Cabinet requests clarification...
   > buy off Russia, 1152 gold confirmed
   Russia's design — The Gulf and the Straits — is bought off for 1152 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► Ney, move to Rhineland
   Ney begins marching to Rhineland (distance: 2). Moved to Lorraine. Route: Lorraine -> Rhineland.
   [1/4 actions remaining]
   ► Murat, move to Rhineland
   → Murat moves from Franche-Comte to Rhineland
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 8 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -24g | Other: +1012g | Upkeep: -1578g | Net: +2000g | Spent: 2268g
   Treasury: 4,569g
   Actions refreshed: 4/4
   Soult's fortifications strengthen: +12% defense (MAX)
   Supply shortage at Franconia: Lannes loses 404 troops
   Supply shortage at Franconia: Bernadotte loses 290 troops
   Supply shortage at Franconia: Massena loses 916 troops
   Supply shortage at Franconia: Napoleon loses 227 troops
   Garrison at Munich reinforced: 6,000 -> 8,000
   Switzerland loyalty 88 (-2): satellite drift
   Territorial rivalry between Russia and Austria grows.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been. He holds you to your word.
   Berthier reports that Bernadotte resents Davout's laurels for the third time — he has grown quiet in the way the staff have learned to read.
   Bernadotte presses his grievance against Davout again — but he holds to the Emperor's word, and the quarrel goes no further for now.
   Berthier reports that Murat resents Davout's laurels for the third time — he has grown loud at the staff table about who is given the honours.
   The staff report 2 further matters among the marshals — the Generals screen has the particulars.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(2017,467)  Archduke John(2032,376)  Lannes +3(1943,441)  ?(1959,325)  Brunswick(1958,287)  Murat(1827,397)  Ney(1740,436)  Soult(1785,423)  Davout(1813,497)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(2068,435)  ?(1945,376)  8k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1698,420)  ?(1910,645)
```

```
#0180  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0180_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3351,64)]  [icon: A Moment of History: The Bavarian Match @(3393,64)]  [icon: European Courts Concerned @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: Settlement Ratified (x2) @(3519,64)]  [icon: Davout arrived @(3561,64)]  [+27]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War for Swabia — Austria, truce 1t]
── BottomLeftUI (layer 0) [scrolled 1850 of 1850 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,569 (+1,914 next turn)
   Inf:
   94,009
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Supply shortage at Franconia: Bernadotte loses 290 troops
   Supply shortage at Franconia: Massena loses 916 troops
   Supply shortage at Franconia: Napoleon loses 227 troops
   Garrison at Munich reinforced: 6,000 -> 8,000
   Switzerland loyalty 88 (-2): satellite drift
   Territorial rivalry between Russia and Austria grows.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been. He holds you to your word.
   Berthier reports that Bernadotte resents Davout's laurels for the third time — he has grown quiet in the way the staff have learned to read.
   Bernadotte presses his grievance against Davout again — but he holds to the Emperor's word, and the quarrel goes no further for now.
   Berthier reports that Murat resents Davout's laurels for the third time — he has grown loud at the staff table about who is given the honours.
   The staff report 2 further matters among the marshals — the Generals screen has the particulars.
   --- Strategic Order Updates ---
   Ney: Ney is marching to Rhineland (2 turns remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 8
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Austria enacts the Landwehr — infantry manpower returns 25% faster.
   • Sire — relations with Austria have improved significantly (+11 this turn).
   • Sire — an envoy from Switzerland has arrived with a petition.
   SITUATION
   France holds 28 regions. Treasury: 4,569g (+2,000 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Franconia — 29,402 — Awaiting orders.
   ⚠ Starving — supply has failed at Franconia two turns running.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Murat — Rhineland — 16,831 — Awaiting orders.
   > Ney — Lorraine — 16,282 — Moving to Rhineland — arrives next turn.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franconia — 12,983 — 5 turns idle.
   ⚠ Starving — supply has failed at Franconia two turns running.
   - Bernadotte — Franconia — 9,334 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Starving — supply has failed at Franconia two turns running.
   - Napoleon — Franconia — 7,314 — Awaiting orders.
   ⚠ Starving — supply has failed at Franconia two turns running.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +12% defense (MAX)
   Supply cost you 1,837 men, at Franconia.
   Switzerland loyalty 88 (-2): satellite drift
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been. He holds you to your word.
   Berthier reports that Bernadotte resents Davout's laurels for the third time — he has grown quiet in the way the staff have learned to read.
   Bernadotte presses his grievance against Davout again — but he holds to the Emperor's word, and the quarrel goes no further for now.
   Berthier reports that Murat resents Davout's laurels for the third time — he has grown loud at the staff table about who is given the honours.
   The staff report 2 further matters among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -44. 1 DP a turn, 3 so far.
   An envoy from Switzerland has arrived with a petition.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: 5 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. Held by our truce: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0181  click Envoys (2)  ->  ok
  (clicked at (3391, 18))
view: <run>\frames\0181_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Routine letters from the lesser courts answer in place; every other letter opens in full. Select a row, or press its Open, to reopen or activate it.
   ACTIVE
   Switzerland
   Proposal
   Turn 8
   Incoming proposal: Client's Petition
   Terms: Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. · Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now +0); nothing is charged. · Left unanswered at the turn's end, the petition lapses — an …
   A client's petition is granted or refused in full — open to decide.
   WAITING
   The Cabinet
   Moment
   Turn 8
   A Moment of History: The Bavarian Match
   A moment of history is answered in full — open the letter to choose.
   controls: {ACTIVE}  [Open ▸]  {WAITING}  [Open ▸]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1850 of 1850 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: 5 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. Held by our truce: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0182  click#2 Open  ->  ok
  (clicked at (2191, 473))
view: <run>\frames\0182_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A MOMENT OF HISTORY — Early January 1806 / The Bavarian Match — The Cabinet lays a letter before the Emperor. / A moment of history, Sire: a decision the record sets before you — two answers, each priced below, or Not Now to set it aside. It waits this turn and the next; left unanswered, it takes the second answer for you. / Eugène, adopted by Napoleon, wed Augusta of Bavaria at Munich (historical …
   controls: [Seal the match]  [Let Baden keep her]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1850 of 1850 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,569 (+1,914 next turn)
   Inf:
   94,009
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: 5 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. Held by our truce: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0183  click Seal the match  ->  ok
  (clicked at (1678, 878))
view: <run>\frames\0183_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 48 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1938 of 1938 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,569 (+1,957 next turn)
   Inf:
   94,009
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Answering The Bavarian Match: Seal the match
   The Bavarian Match — Seal the match: 2 diplomatic points (you hold 6); 1,000 gold (the treasury holds 4,569); Bavaria's goodwill 53 → 73; Bavaria's loyalty as your vassal 62 → 77; Europe's alarm 45 → 48 (A Bonaparte match).
map: unchanged (51 labels)
```

```
#0184  click Grant  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0184_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 3/7
   Threat 48 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3351,64)]  [icon: The blockade on our ports lifts @(3393,64)]  [icon: Settlement Ratified (x2) @(3435,64)]  [icon: Davout arrived @(3477,64)]  [icon: Murat arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+26]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War for Swabia — Austria, truce 1t]
── BottomLeftUI (layer 0) [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,569 (+1,732 next turn)
   Inf:
   94,009
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (51 labels)
```

```
#0185  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0185_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -44 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Answering The Bavarian Match: Seal the match
   The Bavarian Match — Seal the match: 2 diplomatic points (you hold 6); 1,000 gold (the treasury holds 4,569); Bavaria's goodwill 53 → 73; Bavaria's loyalty as your vassal 62 → 77; Europe's alarm 45 → 48 (A Bonaparte match).
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (51 labels)
```

```
#0186  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0186_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 727 px] ──
   THE CABINET
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Austria  —  Armistice  |  -44 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +33 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -13 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Answering The Bavarian Match: Seal the match
   The Bavarian Match — Seal the match: 2 diplomatic points (you hold 6); 1,000 gold (the treasury holds 4,569); Bavaria's goodwill 53 → 73; Bavaria's loyalty as your vassal 62 → 77; Europe's alarm 45 → 48 (A Bonaparte match).
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (51 labels)
```

```
#0187  click Austria  ->  ok
  (clicked at (1825, 444))
view: <run>\frames\0187_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 376 px, 0 of 381 px] ──
   THE CABINET — Austria
   DP: 3
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War for Swabia   Relation: -44 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Permit me to observe, Sire, that a truce is a clock, not a treaty: 1 turns, relations -44, and the ledger stands: the war score reads +31 for France (5 battles,  …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile (+33 over 3 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1056g) (1 DP + 1056g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1008g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,569 (+1,732 next turn)
   Inf:
   94,009
   Cav:
   27,250
   Art:
   14,200
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Answering The Bavarian Match: Seal the match
   The Bavarian Match — Seal the match: 2 diplomatic points (you hold 6); 1,000 gold (the treasury holds 4,569); Bavaria's goodwill 53 → 73; Bavaria's loyalty as your vassal 62 → 77; Europe's alarm 45 → 48 (A Bonaparte match).
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (51 labels)
```

```
#0188  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0188_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Answering The Bavarian Match: Seal the match
   The Bavarian Match — Seal the match: 2 diplomatic points (you hold 6); 1,000 gold (the treasury holds 4,569); Bavaria's goodwill 53 → 73; Bavaria's loyalty as your vassal 62 → 77; Europe's alarm 45 → 48 (A Bonaparte match).
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (51 labels)
```

```
#0189  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0189_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 8
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 47 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1895 of 1896 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,547 (+1,954 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   France holds 28 regions. Treasury: 4,569g (+2,000 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Franconia — 29,402 — Awaiting orders.
   ⚠ Starving — supply has failed at Franconia two turns running.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Murat — Rhineland — 16,831 — Awaiting orders.
   > Ney — Lorraine — 16,282 — Moving to Rhineland — arrives next turn.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franconia — 12,983 — 5 turns idle.
   ⚠ Starving — supply has failed at Franconia two turns running.
   - Bernadotte — Franconia — 9,334 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Starving — supply has failed at Franconia two turns running.
   - Napoleon — Franconia — 7,314 — Awaiting orders.
   ⚠ Starving — supply has failed at Franconia two turns running.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +12% defense (MAX)
   Supply cost you 1,837 men, at Franconia.
   Switzerland loyalty 88 (-2): satellite drift
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been. He holds you to your word.
   Berthier reports that Bernadotte resents Davout's laurels for the third time — he has grown quiet in the way the staff have learned to read.
   Bernadotte presses his grievance against Davout again — but he holds to the Emperor's word, and the quarrel goes no further for now.
   Berthier reports that Murat resents Davout's laurels for the third time — he has grown loud at the staff table about who is given the honours.
   The staff report 2 further matters among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -44. 1 DP a turn, 3 so far.
   An envoy from Switzerland has arrived with a petition.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client's Petition
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+39)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: 5 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. Held by our truce: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Answering The Bavarian Match: Seal the match
   The Bavarian Match — Seal the match: 2 diplomatic points (you hold 6); 1,000 gold (the treasury holds 4,569); Bavaria's goodwill 53 → 73; Bavaria's loyalty as your vassal 62 → 77; Europe's alarm 45 → 48 (A Bonaparte match).
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► end turn
   ═══════════════════════════════════════
   TURN 9 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -18g | Other: +932g | Upkeep: -1526g | Net: +1978g | Spent: 1000g
   Treasury: 5,547g
   Actions refreshed: 4/4
   Crowded at Franconia: Lannes loses 389 troops to the press of 4 corps on one province's roads
   Crowded at Franconia: Bernadotte loses 280 troops to the press of 4 corps on one province's roads
   Crowded at Franconia: Massena loses 882 troops to the press of 4 corps on one province's roads
   Crowded at Franconia: Napoleon loses 219 troops to the press of 4 corps on one province's roads
   Garrison at Munich reinforced: 8,000 -> 10,000
   The armistice between Austria and France has concluded. Peace declared — signed on the held line.
   Austria and France are at peace — Talleyrand is home.
   Territorial rivalry between Russia and Sweden grows.
   Berthier notes that Massena has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(2017,467)  Archduke John(2032,376)  Lannes +3(1943,441)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Murat(1839,371)  Soult(1753,436)  Davout(1813,497)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(2068,435)  ?(1945,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  ?(1910,645)
```

```
#0190  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0190_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 47 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Ney arrived (x2) @(3393,64)]  [icon: European Courts Concerned @(3435,64)]  [icon: Settlement Ratified (x2) @(3477,64)]  [icon: Davout arrived @(3519,64)]  [icon: Murat arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 1784 of 1784 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,547 (+1,954 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Treasury: 5,547g
   Actions refreshed: 4/4
   Crowded at Franconia: Lannes loses 389 troops to the press of 4 corps on one province's roads
   Crowded at Franconia: Bernadotte loses 280 troops to the press of 4 corps on one province's roads
   Crowded at Franconia: Massena loses 882 troops to the press of 4 corps on one province's roads
   Crowded at Franconia: Napoleon loses 219 troops to the press of 4 corps on one province's roads
   Garrison at Munich reinforced: 8,000 -> 10,000
   The armistice between Austria and France has concluded. Peace declared — signed on the held line.
   Austria and France are at peace — Talleyrand is home.
   Territorial rivalry between Russia and Sweden grows.
   Berthier notes that Massena has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Ney: Ney arrives at Rhineland. Ney: "Done — and I trust the next order has more fire in it."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 9
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — peace with Austria is signed. The truce has ripened into peace, signed on the held line.
   • Sire — our peace binds Austria for 5 more turns; then she may join a league (relations −33).
   • Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
   SITUATION
   France holds 28 regions. Treasury: 5,547g (+1,978 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Franconia — 28,520 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   - Murat — Rhineland — 16,831 — Awaiting orders.
   - Ney — Rhineland — 16,282 — Awaiting orders.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franconia — 12,594 — 6 turns idle.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 1,770 men, at Franconia.
   Berthier notes that Massena has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -33.
   Swabia — left with Austria by the peace, titled to them by treaty.
   The armistice between Austria and France has concluded. Peace declared.
   Austria and France are at peace — Talleyrand is home.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the war come, having been asked.
   Relations with Austria have improved significantly (+11 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   COALITION THREAT
   Threat: 47/100 [Murmurs]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0191  type Massena, move to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0191_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Massena begins marching to Rhineland (distance: 2). Moved to Frankfurt. Route: Frankfurt -> Rhineland.
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1894 of 1894 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   5,547 (+1,984 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, move to Rhineland
   Massena begins marching to Rhineland (distance: 2). Moved to Frankfurt. Route: Frankfurt -> Rhineland.
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2043,451)  ?(2045,479)  Archduke John(2032,375)  Lannes(1930,451)  Bernadotte(1971,425)  Napoleon(1964,399)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Murat(1839,371)  Soult(1753,436)  Davout(1813,497)  Deroy(1901,535)  Massena(1893,345)  ?(1551,403)  Castanos(1551,364)  ?(1945,372)  10k(1901,591)  10k(1875,446)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  ?(1910,645)
```

```
#0192  type Lannes, move to Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0192_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Lannes begins marching to Franche-Comte (distance: 2). Moved to Munich. Route: Munich -> Franche-Comte.
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   5,547 (+1,984 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, move to Franche-Comte
   Lannes begins marching to Franche-Comte (distance: 2). Moved to Munich. Route: Munich -> Franche-Comte.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2061,451)  ?(2045,479)  Archduke John(2032,376)  Bernadotte(1930,451)  Napoleon(1964,425)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Murat(1839,371)  Soult(1753,436)  Davout(1813,497)  Lannes(1888,535)  Deroy(1913,561)  Massena(1893,345)  ?(1551,403)  Castanos(1551,364)  ?(1945,376)  10k(1901,591)  10k(1857,446)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  ?(1910,645)
```

```
#0193  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0193_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +32 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [2/4 actions remaining]
   ► Lannes, move to Franche-Comte
   Lannes begins marching to Franche-Comte (distance: 2). Moved to Munich. Route: Munich -> Franche-Comte.
   [0/4 actions remaining]
map: unchanged (55 labels)
```

```
#0194  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0194_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 727 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +32 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -12 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [2/4 actions remaining]
   ► Lannes, move to Franche-Comte
   Lannes begins marching to Franche-Comte (distance: 2). Moved to Munich. Route: Munich -> Franche-Comte.
   [0/4 actions remaining]
map: unchanged (55 labels)
```

```
#0195  click Prussia  ->  ok
  (clicked at (1825, 444))
view: <run>\frames\0195_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 266 px, 0 of 511 px] ──
   THE CABINET — Prussia
   DP: 6
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Non-Aggression   Relation: +3 (Neutral) /  / "We have Prussia's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Prussia stands on the Emperor's roads, Sire …
   The compact already stands.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3).](disabled: The compact already stands.)  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Armed Neutrality next (600g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   5,547 (+1,984 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [2/4 actions remaining]
   ► Lannes, move to Franche-Comte
   Lannes begins marching to Franche-Comte (distance: 2). Moved to Munich. Route: Munich -> Franche-Comte.
   [0/4 actions remaining]
map: unchanged (55 labels)
```

```
#0196  click Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0196_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Prussia /  / "Sire, I shall begin efforts to improve relations with Prussia. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 47 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2051 of 2051 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   5,547 (+1,984 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► improve relations with Prussia
map: unchanged (55 labels)
```

```
#0197  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0197_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 47 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Ney arrived (x2) @(3393,64)]  [icon: European Courts Concerned @(3435,64)]  [icon: Settlement Ratified (x2) @(3477,64)]  [icon: Davout arrived @(3519,64)]  [icon: Murat arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 2117 of 2117 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   5,547 (+1,984 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (55 labels)
```

```
#0198  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0198_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +3 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +32 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2117 of 2117 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (55 labels)
```

```
#0199  scroll 1828 500 down 20  ->  ok
  (scrolled down 20 at (1828, 500))
view: <run>\frames\0199_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 687 of 727 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Britain  —  Peace  |  -82 (Hostile)]  [Russia  —  Peace  |  -72 (Hostile)]  [Austria  —  Peace  |  -33 (Hostile)]  [Sweden  —  Peace  |  -52 (Hostile)]  [Naples  —  Peace  |  -22 (Wary)]  [Hanover  —  Peace  |  -42 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2117 of 2117 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (55 labels)
```

```
#0200  click Austria  —  Peace  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0200_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 548 px] ──
   THE CABINET — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -33 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. Improve Relations is shut while Talleyrand is at Prussia's court — recall Talleyrand from Prussia first (t …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1008g) (1 DP + 1008g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1008g to buy off in turn).]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the pledge being honoured.]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2117 of 2117 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   5,547 (+1,984 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (55 labels)
```

```
#0201  click Buy Off Their Design  ->  ok
  (clicked at (1825, 551))
view: <run>\frames\0201_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE CABINET ASKS:
   "Buy off Austria's design — Redeem Italy: 1,008 gold and 1 diplomatic point. The treasury holds 5,547 gold and would hold 4,539 after. The want sleeps 15 turns; it does not die — marching on Austria inside the term is reneging, and it returns the heavier: their will against us +15, relations -25 and the strongest casus belli in Europe. Buying it wakes Primacy in Germany next (1,008g to buy off in  …
   controls: [Buy it off]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 47 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2183 of 2183 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   5,547 (+1,984 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► buy off Austria
   The Cabinet requests clarification...
map: unchanged (55 labels)
```

```
#0202  click Buy it off  ->  ok
  (clicked at (1829, 549))
view: <run>\frames\0202_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 47 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Ney arrived (x2) @(3393,64)]  [icon: European Courts Concerned @(3435,64)]  [icon: Settlement Ratified (x2) @(3477,64)]  [icon: Davout arrived @(3519,64)]  [icon: Murat arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 2272 of 2272 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   4,539 (+1,996 next turn)
   Inf:
   96,509
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   > buy off Austria, 1008 gold confirmed
   Austria's design — Redeem Italy — is bought off for 1008 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0203  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0203_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 9
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 46 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2031 of 2031 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,539 (+1,976 next turn)
   Inf:
   99,009
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   SITUATION
   France holds 28 regions. Treasury: 5,547g (+1,978 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Franconia — 28,520 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   - Murat — Rhineland — 16,831 — Awaiting orders.
   - Ney — Rhineland — 16,282 — Awaiting orders.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franconia — 12,594 — 6 turns idle.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 1,770 men, at Franconia.
   Berthier notes that Massena has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -33.
   Swabia — left with Austria by the peace, titled to them by treaty.
   The armistice between Austria and France has concluded. Peace declared.
   Austria and France are at peace — Talleyrand is home.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the war come, having been asked.
   Relations with Austria have improved significantly (+11 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   COALITION THREAT
   Threat: 47/100 [Murmurs]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
   ► Massena, move to Rhineland
   Massena begins marching to Rhineland (distance: 2). Moved to Frankfurt. Route: Frankfurt -> Rhineland.
   [2/4 actions remaining]
   ► Lannes, move to Franche-Comte
   Lannes begins marching to Franche-Comte (distance: 2). Moved to Munich. Route: Munich -> Franche-Comte.
   [0/4 actions remaining]
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
   ► buy off Austria
   The Cabinet requests clarification...
   > buy off Austria, 1008 gold confirmed
   Austria's design — Redeem Italy — is bought off for 1008 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -30g | Other: +936g | Upkeep: -1496g | Net: +2000g | Spent: 1008g
   Treasury: 6,539g
   Actions refreshed: 4/4
   Bavaria loyalty 81 (+3): relations with the lord, the garrison's presence
   Territorial rivalry between Russia and Prussia grows.
   Murat's resentment of Davout has cooled. The quarrel has flared 3 times.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
map: unchanged (55 labels)
```

```
#0204  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0204_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 46 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Ney arrived (x2) @(3393,64)]  [icon: European Courts Concerned @(3435,64)]  [icon: Settlement Ratified (x2) @(3477,64)]  [icon: Davout arrived @(3519,64)]  [icon: Murat arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 2189 of 2189 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,539 (+1,976 next turn)
   Inf:
   99,009
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
   ► Massena, move to Rhineland
   Massena begins marching to Rhineland (distance: 2). Moved to Frankfurt. Route: Frankfurt -> Rhineland.
   [2/4 actions remaining]
   ► Lannes, move to Franche-Comte
   Lannes begins marching to Franche-Comte (distance: 2). Moved to Munich. Route: Munich -> Franche-Comte.
   [0/4 actions remaining]
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
   ► buy off Austria
   The Cabinet requests clarification...
   > buy off Austria, 1008 gold confirmed
   Austria's design — Redeem Italy — is bought off for 1008 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -30g | Other: +936g | Upkeep: -1496g | Net: +2000g | Spent: 1008g
   Treasury: 6,539g
   Actions refreshed: 4/4
   Bavaria loyalty 81 (+3): relations with the lord, the garrison's presence
   Territorial rivalry between Russia and Prussia grows.
   Murat's resentment of Davout has cooled. The quarrel has flared 3 times.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   --- Strategic Order Updates ---
   Lannes: Lannes is marching to Franche-Comte (2 turns remaining).
   Massena: Massena is marching to Rhineland (2 turns remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
   SITUATION
   France holds 28 regions. Treasury: 6,539g (+2,000 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   > Massena — Frankfurt — 27,749 — Moving to Rhineland — arrives next turn.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   - Murat — Rhineland — 16,831 — Awaiting orders.
   - Ney — Rhineland — 16,282 — Awaiting orders.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   > Lannes — Munich — 12,343 — Moving to Franche-Comte — arrives next turn.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Bavaria loyalty 81 (+3): relations with the lord, the garrison's presence
   Murat's resentment of Davout has cooled. The quarrel has flared 3 times.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 10. 1 DP a turn, 1 so far.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   The court of Austria takes up a new design: Primacy in Germany.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0205  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0205_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +10 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +31 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2189 of 2189 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0206  click the terms  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0206_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 999 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▾ hide the terms /     ✓ 1 administrative action (you have 2) /     • 45 titled provinces (37 of 45) /     ✓ Paris held /     ✓ the Emperor free /     ✓ no satellite on the brink of rebellion /     ✓ Europe's alarm below 80 (now 46 — falling 1 a turn: our bloc's weight in Europe +1, the designs we deny +1 against 3 of decay (one, plus one for each court at …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▾ hide the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2189 of 2189 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0207  click hide the terms  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0207_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +10 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +31 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2189 of 2189 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0208  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0208_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 426 of 730 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (4)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Hesse  —  Non-Aggression  |  0 (Neutral)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Bavaria  —  Vassal  |  +73 (Loyal)]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2189 of 2189 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0209  click Hesse  ->  ok
  (clicked at (1825, 419))
view: <run>\frames\0209_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 288 px, 0 of 583 px] ──
   THE CABINET — Hesse
   DP: 6
   TALLEYRAND'S ASSESSMENT — HESSE / Status: Non-Aggression   Relation: 0 (Neutral) /  / "We have Hesse's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: Our non-aggression pact with Hesse stands on its line, Sire — relations at 0, the 0 it holds on, and the first slide takes it under. Improve Relations is shut while Talleyrand is at …
   Relations with Hesse stand at 0; a Defensive Alliance needs 20.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Defensive Alliance (2 DP)  —  Uncertain](disabled: Relations with Hesse stand at 0; a Defensive Alliance needs 20.)  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Break Treaty (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2189 of 2189 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,539 (+1,976 next turn)
   Inf:
   99,009
   Cav:
   30,000
   Art:
   15,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0210  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0210_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2189 of 2189 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0211  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0211_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 10
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1943 of 1945 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,549 (+1,986 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -30g | Other: +936g | Upkeep: -1496g | Net: +2000g | Spent: 1008g
   Treasury: 6,539g
   Actions refreshed: 4/4
   Bavaria loyalty 81 (+3): relations with the lord, the garrison's presence
   Territorial rivalry between Russia and Prussia grows.
   Murat's resentment of Davout has cooled. The quarrel has flared 3 times.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   --- Strategic Order Updates ---
   Lannes: Lannes is marching to Franche-Comte (2 turns remaining).
   Massena: Massena is marching to Rhineland (2 turns remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
   SITUATION
   France holds 28 regions. Treasury: 6,539g (+2,000 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   > Massena — Frankfurt — 27,749 — Moving to Rhineland — arrives next turn.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   - Murat — Rhineland — 16,831 — Awaiting orders.
   - Ney — Rhineland — 16,282 — Awaiting orders.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   > Lannes — Munich — 12,343 — Moving to Franche-Comte — arrives next turn.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   ⚠ Crowded — Franconia carries more corps than its roads can bear, three turns running.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Bavaria loyalty 81 (+3): relations with the lord, the garrison's presence
   Murat's resentment of Davout has cooled. The quarrel has flared 3 times.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 10. 1 DP a turn, 1 so far.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   The court of Austria takes up a new design: Primacy in Germany.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -54g | Other: +940g | Upkeep: -1466g | Net: +2010g
   Treasury: 8,549g
   Actions refreshed: 4/4
   Supply shortage at Rhineland: Ney loses 329 troops
   Supply shortage at Rhineland: Murat loses 340 troops
   Supply shortage at Rhineland: Massena loses 560 troops
   Relations between Austria and Russia are deteriorating. Alliance may collapse in 2 turns.
   Territorial rivalry between Russia and Austria grows.
   Prussia declares war on Hanover — The Hanoverian Prize; declaring Hanover.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2061,451)  ?(2045,479)  Archduke John(2032,376)  Bernadotte(1930,451)  Napoleon(1964,425)  ?(1959,325)  Brunswick(1958,287)  Ney(1814,397)  Murat(1827,371)  Massena(1839,345)  Soult(1753,436)  Davout(1801,497)  Lannes(1825,471)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(1945,376)  10k(1901,591)  ?(1893,373)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  ?(1910,645)
```

```
#0212  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0212_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+29]
── BottomLeftUI (layer 0) [scrolled 2097 of 2097 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,549 (+1,986 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Bavaria loyalty 81 (+3): relations with the lord, the garrison's presence
   Murat's resentment of Davout has cooled. The quarrel has flared 3 times.
   Bernadotte's resentment of Davout has cooled for now. What was settled between them at the staff table has not been.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 10. 1 DP a turn, 1 so far.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   The court of Austria takes up a new design: Primacy in Germany.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: 5 lesser courts would march. Bound for now by a fresh peace: Britain, Russia and Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -54g | Other: +940g | Upkeep: -1466g | Net: +2010g
   Treasury: 8,549g
   Actions refreshed: 4/4
   Supply shortage at Rhineland: Ney loses 329 troops
   Supply shortage at Rhineland: Murat loses 340 troops
   Supply shortage at Rhineland: Massena loses 560 troops
   Relations between Austria and Russia are deteriorating. Alliance may collapse in 2 turns.
   Territorial rivalry between Russia and Austria grows.
   Prussia declares war on Hanover — The Hanoverian Prize; declaring Hanover.
   --- Strategic Order Updates ---
   Lannes: Lannes arrives at Franche-Comte. Lannes: "Done — and I trust the next order has more fire in it."
   Massena: Massena arrives at Rhineland.
   Rhineland feeds 60,000; the 60,862 men standing there would lose ~1,229 a turn to short supply. Massena: "Done — and I trust the next order has more fire in it."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 11
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain and Russia would now join a league against us (relations −80 and −70). The Balance of Europe names the price to keep each out.
   • Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   SITUATION
   France holds 28 regions. Treasury: 8,549g (+2,010 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Rhineland — 27,189 — Awaiting orders.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   - Murat — Rhineland — 16,491 — 3 turns idle.
   - Ney — Rhineland — 15,953 — Awaiting orders.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 12,343 — Awaiting orders.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 1,229 men, at Rhineland.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 2 (+16 earned, -15 from Prussia's declaration on Hanover, drift -2). 1 DP a turn, 2 so far.
   Prussia has declared war on Hanover — relations with every court, France's included, fall 15.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0213  click Diplomacy (D)  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0213_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 3043 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Prussia
   DP: 6/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  /   Britain [Neutral] — PEACE  Relation: -80 (Hostile) /   Laws: the Horse Guards Reforms, the Orders in Council and the Militia Transfer (600 gold a turn) /   Doctrine: The Line Holds; flaw: Irreplaceable (cured since turn 8) /   Diplomat: Castler …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,549 (+1,986 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0214  click BALANCE OF EUROPE  ->  ok
  (clicked at (1665, 273))
view: <run>\frames\0214_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 728 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Prussia
   DP: 6/7
   BALANCE OF EUROPE / ──────────────── / French-led alignment holds 39% of active European bloc power. / Power score: 111 / 285. / This counts France's direct allies and vassal bloc against all active courts. Alliance networks can overlap; the headline shows the current largest alignment. / Bloc members: Bavaria, France, Holland, Kingdom of Italy, Spain, Switzerland. / Warning bands: 33% noticed, 50 …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [BALANCE OF EUROPE](disabled: You are reading this book)  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0215  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0215_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0216  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0216_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +30 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0217  click Formable Nations  ->  ok
  (clicked at (1825, 542))
view: <run>\frames\0217_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 256 px] ──
   THE CABINET — FORMABLE NATIONS
   DP: 6
   "The map of Europe is not finished, Sire. These states could yet exist — each names what its existence would require."
   States not yet on the map, Sire; each row names what its birth requires. One carved at the table is born your client — it pays tribute and marches when you call; one that forms by conquest rises free.
   Duchy of Warsaw — client state at the settlement table /     • at war with Prussia /     • Posen held at the settlement table (currently Prussia-held)
   Duchy of Normandy — client state at the settlement table /     • carved from France's own provinces — a clause only a victorious enemy may put before you
   Roman Republic — client state at the settlement table /     • at war with Papal States /     • Rome held at the settlement table (currently Papal States-held) /     • a decisive victory over Papal States — erasing a state entirely needs war score 90 (currently 0)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0218  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0218_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +30 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0219  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0219_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 727 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +30 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0220  click Prussia  ->  ok
  (clicked at (1825, 444))
view: <run>\frames\0220_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 266 px, 0 of 624 px] ──
   THE CABINET — Prussia
   DP: 6
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Non-Aggression   Relation: +2 (Neutral) /  / "We have Prussia's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: Relations must improve before proposals will find purchase. Talleyrand is already at their court, Sire — net +8 a turn. / Talleyrand: "Prussia stands on the Emperor's roads, Si …
   The compact already stands.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Neutral (-1 over 2 turns) — +16 earned, -15 from Prussia's declaration on Hanover, drift -2]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends (§3.3).](disabled: The compact already stands.)  [Buy Off Their Design (1344g) (1 DP + 1344g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. No other design wakes after it.]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0221  click Cancel: Improve Relations  ->  ok
  (clicked at (1825, 462))
view: <run>\frames\0221_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+29]
── BottomLeftUI (layer 0) [scrolled 2184 of 2184 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,549 (+1,986 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (55 labels)
```

```
#0222  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0222_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)]  [Spain  —  Alliance  |  +30 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2184 of 2184 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (55 labels)
```

```
#0223  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0223_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 426 of 730 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (4)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Hesse  —  Non-Aggression  |  0 (Neutral)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Bavaria  —  Vassal  |  +73 (Loyal)]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2184 of 2184 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (55 labels)
```

```
#0224  click Hesse  ->  ok
  (clicked at (1825, 419))
view: <run>\frames\0224_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 266 px, 0 of 514 px] ──
   THE CABINET — Hesse
   DP: 6
   TALLEYRAND'S ASSESSMENT — HESSE / Status: Non-Aggression   Relation: 0 (Neutral) /  / "We have Hesse's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: Our non-aggression pact with Hesse stands on its line, Sire — relations at 0, the 0 it holds on, and the first slide takes it under. Talleyrand recommends: Improve Relations — +8 a  …
   Relations with Hesse stand at 0; a Defensive Alliance needs 20.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Propose Defensive Alliance (2 DP)  —  Uncertain](disabled: Relations with Hesse stand at 0; a Defensive Alliance needs 20.)  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2184 of 2184 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,549 (+1,986 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (55 labels)
```

```
#0225  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0225_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 266 px, 243 of 478 px] ──
   THE CABINET — Hesse
   DP: 6
   TALLEYRAND'S ASSESSMENT — HESSE / Status: Non-Aggression   Relation: 0 (Neutral) /  / "We have Hesse's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: Our non-aggression pact with Hesse stands on its line, Sire — relations at 0, the 0 it holds on, and the first slide takes it under. Talleyrand recommends: Improve Relations — +8 a  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Downgrade (1 DP)]  [Send Ultimatum (2 DP)]  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn](disabled: No alliance to undermine)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2184 of 2184 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (55 labels)
```

```
#0226  click Court Nation  ->  ok
  (clicked at (1825, 551))
view: <run>\frames\0226_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Hesse /  / "Sire, I shall begin efforts to court and charm Hesse. This will cost 2 DP per turn." /  / DP cost: 2/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2229 of 2229 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,549 (+1,986 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► court Hesse
map: unchanged (55 labels)
```

```
#0227  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0227_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+29]
── BottomLeftUI (layer 0) [scrolled 1722 of 1723 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,549 (+1,986 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -54g | Other: +940g | Upkeep: -1466g | Net: +2010g
   Treasury: 8,549g
   Actions refreshed: 4/4
   Supply shortage at Rhineland: Ney loses 329 troops
   Supply shortage at Rhineland: Murat loses 340 troops
   Supply shortage at Rhineland: Massena loses 560 troops
   Relations between Austria and Russia are deteriorating. Alliance may collapse in 2 turns.
   Territorial rivalry between Russia and Austria grows.
   Prussia declares war on Hanover — The Hanoverian Prize; declaring Hanover.
   --- Strategic Order Updates ---
   Lannes: Lannes arrives at Franche-Comte. Lannes: "Done — and I trust the next order has more fire in it."
   Massena: Massena arrives at Rhineland.
   Rhineland feeds 60,000; the 60,862 men standing there would lose ~1,229 a turn to short supply. Massena: "Done — and I trust the next order has more fire in it."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 11
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain and Russia would now join a league against us (relations −80 and −70). The Balance of Europe names the price to keep each out.
   • Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   SITUATION
   France holds 28 regions. Treasury: 8,549g (+2,010 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Rhineland — 27,189 — Awaiting orders.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   - Murat — Rhineland — 16,491 — 3 turns idle.
   - Ney — Rhineland — 15,953 — Awaiting orders.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 12,343 — Awaiting orders.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 1,229 men, at Rhineland.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 2 (+16 earned, -15 from Prussia's declaration on Hanover, drift -2). 1 DP a turn, 2 so far.
   Prussia has declared war on Hanover — relations with every court, France's included, fall 15.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
   ► court Hesse
   Directing Talleyrand: start mission
   Talleyrand begins efforts to court and charm Hesse. (2 DP/turn)
map: unchanged (55 labels)
```

```
#0228  type Murat, drill  ->  ok
  (typed and Enter)
view: <run>\frames\0228_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Murat begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 13.
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1833 of 1833 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   8,549 (+1,986 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, drill
   Murat begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 13.
   [3/4 actions remaining]
map: unchanged (55 labels)
```

```
#0229  type Massena, drill  ->  ok
  (typed and Enter)
view: <run>\frames\0229_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Massena begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 13.
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1944 of 1944 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   8,549 (+1,986 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, drill
   Massena begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 13.
   [2/4 actions remaining]
map: unchanged (55 labels)
```

```
#0230  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0230_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 11
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1744 of 1746 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,590 (+2,016 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Sire — Britain and Russia would now join a league against us (relations −80 and −70). The Balance of Europe names the price to keep each out.
   • Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   SITUATION
   France holds 28 regions. Treasury: 8,549g (+2,010 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Rhineland — 27,189 — Awaiting orders.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   - Murat — Rhineland — 16,491 — 3 turns idle.
   - Ney — Rhineland — 15,953 — Awaiting orders.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 12,343 — Awaiting orders.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 1,229 men, at Rhineland.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 2 (+16 earned, -15 from Prussia's declaration on Hanover, drift -2). 1 DP a turn, 2 so far.
   Prussia has declared war on Hanover — relations with every court, France's included, fall 15.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
   ► court Hesse
   Directing Talleyrand: start mission
   Talleyrand begins efforts to court and charm Hesse. (2 DP/turn)
   ► Murat, drill
   Murat begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 13.
   [3/4 actions remaining]
   ► Massena, drill
   Massena begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 13.
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -78g | Other: +943g | Upkeep: -1414g | Net: +2041g
   Treasury: 10,590g
   Actions refreshed: 4/4
   Soult's fortifications decay: 12% → 11%
   Murat is now locked in intensive drill. Cannot receive orders until training completes.
   Massena is now locked in intensive drill. Cannot receive orders until training completes.
   Crowded at Rhineland: Ney loses 319 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Murat loses 329 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Massena loses 543 troops to the press of 3 corps on one province's roads
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Territorial rivalry between Russia and Sweden grows.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2061,451)  ?(2045,479)  Archduke John(2032,376)  Bernadotte(1930,451)  Napoleon(1964,425)  ?(1959,325)  Yorck(1958,287)  Ney(1814,397)  Murat(1827,371)  Massena(1839,345)  ?(1831,316)  Brunswick(1830,278)  Soult(1753,436)  Davout(1801,497)  Lannes(1825,471)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(1945,376)  10k(1901,591)  ?(1893,373)  25k(1595,494)  12k(1551,454)  ?(1769,580)  7k(1777,335)  12k(1705,420)  ?(1910,645)
```

```
#0231  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0231_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+29]
── BottomLeftUI (layer 0) [scrolled 1878 of 1878 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,590 (+2,016 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Directing Talleyrand: start mission
   Talleyrand begins efforts to court and charm Hesse. (2 DP/turn)
   ► Murat, drill
   Murat begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 13.
   [3/4 actions remaining]
   ► Massena, drill
   Massena begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 13.
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -78g | Other: +943g | Upkeep: -1414g | Net: +2041g
   Treasury: 10,590g
   Actions refreshed: 4/4
   Soult's fortifications decay: 12% → 11%
   Murat is now locked in intensive drill. Cannot receive orders until training completes.
   Massena is now locked in intensive drill. Cannot receive orders until training completes.
   Crowded at Rhineland: Ney loses 319 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Murat loses 329 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Massena loses 543 troops to the press of 3 corps on one province's roads
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Territorial rivalry between Russia and Sweden grows.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   SITUATION
   France holds 28 regions. Treasury: 10,590g (+2,041 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   * Massena — Rhineland — 26,646 — Drilling.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, two turns running.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   * Murat — Rhineland — 16,162 — Drilling.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, two turns running.
   - Ney — Rhineland — 15,634 — 3 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, two turns running.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 12,343 — Awaiting orders.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Brunswick — large force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 12% → 11%
   Murat is now locked in intensive drill. Cannot receive orders until training completes.
   Massena is now locked in intensive drill. Cannot receive orders until training completes.
   Supply cost you 1,191 men, at Rhineland.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
   Brunswick passes from Hanover to Prussia.
   Intelligence reports Prussia has raised Yorck to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 8. 2 DP a turn, 2 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0232  click Ledger (T)  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0232_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 794 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early March 1806 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / ═══ THE CABINET ═══ /   Talleyrand → Hesse │ COURTING  +8 a turn, drift +0, net +8 /     Relations 8 (Neutral) · 4 funded turns to the full +10; the favour holds while he stays · 2 DP a turn   [Recall] /     …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1878 of 1878 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,590 (+2,016 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0233  click LAWS  ->  ok
  (clicked at (2123, 283))
view: <run>\frames\0233_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 816 px] ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Early March 1806 / The laws of the Empire — what each does, its price, its upkeep, and whether we may enact it now. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / Laws are acts of state, Sire: bought once, then paid in gold every turn. When the chest cannot pay, the heaviest upkeep lapses first; a lapsed law returns within 10 turns at half its price plus the arrea …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)  <Enact>  <Enact>  <Enact>  <Enact>  <Enact>  <Enact>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1878 of 1878 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0234  click#6 Enact  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0234_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=['ledger'], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE COUNCIL OF STATE ASKS:
   "The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1 loyalty a turn in every one. 15 authority now, then 100 gold a turn. Authority 100 → 85 — the marshals' calm holds above 70. The treasury holds 10,590 gold. Enact it? (yes / no)"
   controls: [Enact the Code Abroad]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1943 of 1943 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,590 (+2,016 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► enact the Code Abroad
   The Council of State requests clarification...
map: unchanged (58 labels)
```

```
#0235  click Enact the Code Abroad  ->  ok
  (clicked at (1829, 524))
view: <run>\frames\0235_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+29]
── StrategicLedger (layer 50) [scrolled 0 of 816 px] ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Early March 1806 / The laws of the Empire — what each does, its price, its upkeep, and whether we may enact it now. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / Laws are acts of state, Sire: bought once, then paid in gold every turn. When the chest cannot pay, the heaviest upkeep lapses first; a lapsed law returns within 10 turns at half its price plus the arrea …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)  <Enact>  <Enact>  <Enact>  <Enact>  <Enact>  <Repeal>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2031 of 2031 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   10,590 (+1,891 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > enact the Code Abroad confirmed
   The Code Abroad is in force — enacted for 15 authority. It costs 100 gold a turn from now on. Authority 100 → 85 — the marshals' calm holds above 70.
   [4/4 actions remaining]
map: unchanged (58 labels)
```

```
#0236  click#1 Enact  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0236_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=['ledger'], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE COUNCIL OF STATE ASKS:
   "The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day. 9,000 gold now, then 300 gold a turn; one more order each day from the next refill. The treasury holds 10,590 gold. Enact it? (yes / no)"
   controls: [Enact the Grand Quartier Général]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2099 of 2099 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   10,590 (+1,891 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► enact the Grand Quartier Général
   The Council of State requests clarification...
map: unchanged (58 labels)
```

```
#0237  click Enact the Grand Quartier  ->  ok
  (clicked at (1829, 524))
view: <run>\frames\0237_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+29]
── StrategicLedger (layer 50) [scrolled 0 of 728 px] ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Early March 1806 / The laws of the Empire — what each does, its price, its upkeep, and whether we may enact it now. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / Laws are acts of state, Sire: bought once, then paid in gold every turn. When the chest cannot pay, the heaviest upkeep lapses first; a lapsed law returns within 10 turns at half its price plus the arrea …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)
── BottomLeftUI (layer 0) [under a modal] [scrolled 2187 of 2187 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   0/2
   Gold:
   1,590 (+1,669 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > enact the Grand Quartier Général confirmed
   The Grand Quartier Général is in force — enacted for 9,000 gold. It costs 300 gold a turn from now on. From the next refill, one more order each day.
   [4/4 actions remaining]
map: unchanged (58 labels)
```

```
#0238  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0238_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2187 of 2187 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   The Council of State requests clarification...
   > enact the Grand Quartier Général confirmed
   The Grand Quartier Général is in force — enacted for 9,000 gold. It costs 300 gold a turn from now on. From the next refill, one more order each day.
   [4/4 actions remaining]
map: unchanged (58 labels)
```

```
#0239  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0239_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 12
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 13 — Late March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2053 of 2053 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   3,293 (+1,738 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Massena is now locked in intensive drill. Cannot receive orders until training completes.
   Crowded at Rhineland: Ney loses 319 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Murat loses 329 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Massena loses 543 troops to the press of 3 corps on one province's roads
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Territorial rivalry between Russia and Sweden grows.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   SITUATION
   France holds 28 regions. Treasury: 10,590g (+2,041 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   * Massena — Rhineland — 26,646 — Drilling.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, two turns running.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   * Murat — Rhineland — 16,162 — Drilling.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, two turns running.
   - Ney — Rhineland — 15,634 — 3 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, two turns running.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 12,343 — Awaiting orders.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Brunswick — Brunswick — large force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 12% → 11%
   Murat is now locked in intensive drill. Cannot receive orders until training completes.
   Massena is now locked in intensive drill. Cannot receive orders until training completes.
   Supply cost you 1,191 men, at Rhineland.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
   Brunswick passes from Hanover to Prussia.
   Intelligence reports Prussia has raised Yorck to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 8. 2 DP a turn, 2 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
   ► enact the Code Abroad
   The Council of State requests clarification...
   > enact the Code Abroad confirmed
   The Code Abroad is in force — enacted for 15 authority. It costs 100 gold a turn from now on. Authority 100 → 85 — the marshals' calm holds above 70.
   [4/4 actions remaining]
   ► enact the Grand Quartier Général
   The Council of State requests clarification...
   > enact the Grand Quartier Général confirmed
   The Grand Quartier Général is in force — enacted for 9,000 gold. It costs 300 gold a turn from now on. From the next refill, one more order each day.
   [4/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 13 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Laws: -400g | Other: +897g | Upkeep: -1384g | Net: +1703g | Spent: 9000g
   Treasury: 3,293g
   Actions refreshed: 5/5
   Soult's fortifications decay: 11% → 10%
   DRILL COMPLETE: Murat's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   DRILL COMPLETE: Massena's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   Crowded at Rhineland: Ney loses 312 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Murat loses 323 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Massena loses 532 troops to the press of 3 corps on one province's roads
   Garrison at Hanover reinforced: 0 -> 2,000
   Bavaria loyalty 85 (+2): relations with the lord, the Code Abroad
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2061,451)  ?(2045,479)  Archduke John(2032,376)  Bernadotte(1930,451)  Napoleon(1964,425)  ?(1959,325)  Yorck(1958,287)  Ney(1814,397)  Murat(1827,371)  Massena(1839,345)  Soult(1753,436)  Davout(1801,497)  Lannes(1825,471)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(1945,376)  10k(1901,591)  ?(1893,373)  25k(1595,494)  12k(1551,454)  ?(1769,580)  2k(1777,335)  12k(1705,420)  ?(1910,645)
```

```
#0240  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0240_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+30]
── BottomLeftUI (layer 0) [scrolled 1897 of 1897 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   3,293 (+1,738 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 13 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Laws: -400g | Other: +897g | Upkeep: -1384g | Net: +1703g | Spent: 9000g
   Treasury: 3,293g
   Actions refreshed: 5/5
   Soult's fortifications decay: 11% → 10%
   DRILL COMPLETE: Murat's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   DRILL COMPLETE: Massena's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   Crowded at Rhineland: Ney loses 312 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Murat loses 323 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Massena loses 532 troops to the press of 3 corps on one province's roads
   Garrison at Hanover reinforced: 0 -> 2,000
   Bavaria loyalty 85 (+2): relations with the lord, the Code Abroad
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 13
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   • Sire — Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
   • Sire — Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   SITUATION
   France holds 28 regions. Treasury: 3,293g (+1,703 by the accounts) — the chest could enact the Artillery Reserve — 3,000g (the Laws tab: T, then 8)   Open the Laws
   THE STAFF: The Grand Quartier Général is established — one more order of the day, from today.
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Rhineland — 26,114 — Awaiting orders.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, three turns running.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   - Murat — Rhineland — 15,839 — 5 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, three turns running.
   - Ney — Rhineland — 15,322 — 4 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, three turns running.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 12,343 — Awaiting orders.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 11% → 10%
   DRILL COMPLETE: Murat's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   DRILL COMPLETE: Massena's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   Supply cost you 1,167 men, at Rhineland.
   Bavaria loyalty 85 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   THE LAWS: Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Russia brings the Divisional System into force beside its Staff — Slow to concentrate is over; its army gathers as ours does.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 16. 2 DP a turn, 4 so far.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Hesse may be ready to discuss improved relations. The diplomatic winds favor us.
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 9 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Murat grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0241  type Ney, drill  ->  ok
  (typed and Enter)
view: <run>\frames\0241_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Ney begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 15.
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2007 of 2007 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   3,293 (+1,738 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, drill
   Ney begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 15.
   [4/5 actions remaining]
map: unchanged (56 labels)
```

```
#0242  type Davout, drill  ->  ok
  (typed and Enter)
view: <run>\frames\0242_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Davout begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 15.
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2118 of 2118 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   3,293 (+1,738 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, drill
   Davout begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 15.
   [3/5 actions remaining]
map: unchanged (56 labels)
```

```
#0243  type Lannes, drill  ->  ok
  (typed and Enter)
view: <run>\frames\0243_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 15.
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2229 of 2229 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   3,293 (+1,738 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, drill
   Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 15.
   [2/5 actions remaining]
map: unchanged (56 labels)
```

```
#0244  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0244_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 13
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2161 of 2161 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   5,135 (+2,195 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Sire — relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   • Sire — Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
   • Sire — Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   SITUATION
   France holds 28 regions. Treasury: 3,293g (+1,703 by the accounts) — the chest could enact the Artillery Reserve — 3,000g (the Laws tab: T, then 8)   Open the Laws
   THE STAFF: The Grand Quartier Général is established — one more order of the day, from today.
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Rhineland — 26,114 — Awaiting orders.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, three turns running.
   - Davout — Franche-Comte — 18,061 — Awaiting orders.
   - Murat — Rhineland — 15,839 — 5 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, three turns running.
   - Ney — Rhineland — 15,322 — 4 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, three turns running.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 12,343 — Awaiting orders.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 11% → 10%
   DRILL COMPLETE: Murat's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   DRILL COMPLETE: Massena's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   Supply cost you 1,167 men, at Rhineland.
   Bavaria loyalty 85 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   THE LAWS: Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Russia brings the Divisional System into force beside its Staff — Slow to concentrate is over; its army gathers as ours does.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 16. 2 DP a turn, 4 so far.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Hesse may be ready to discuss improved relations. The diplomatic winds favor us.
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 9 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia and 4 lesser courts would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Murat grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► Ney, drill
   Ney begins intensive drill exercises at Rhineland. Troops will be locked in training next turn, bonus ready turn 15.
   [4/5 actions remaining]
   ► Davout, drill
   Davout begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 15.
   [3/5 actions remaining]
   ► Lannes, drill
   Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 15.
   [2/5 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 14 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -15g | Laws: -400g | Other: +1021g | Upkeep: -1354g | Net: +1842g
   Treasury: 5,135g
   Actions refreshed: 5/5
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   Davout is now locked in intensive drill. Cannot receive orders until training completes.
   Soult's fortifications decay: 10% → 9%
   Lannes is now locked in intensive drill. Cannot receive orders until training completes.
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Crowded at Rhineland: Ney loses 306 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Murat loses 316 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Massena loses 522 troops to the press of 3 corps on one province's roads
   Garrison at Hanover reinforced: 2,000 -> 4,000
   Bavaria loyalty 87 (+2): relations with the lord, the Code Abroad
   Peace concluded between Hanover and Prussia without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2061,451)  ?(2045,479)  Archduke John(2032,376)  Bernadotte(1930,451)  Napoleon(1964,425)  ?(1959,325)  Yorck(1958,287)  Ney(1814,397)  Murat(1827,371)  Massena(1839,345)  Soult(1753,436)  Davout(1801,497)  Lannes(1825,471)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(1945,376)  10k(1901,591)  ?(1893,373)  25k(1595,494)  12k(1551,454)  ?(1769,580)  4k(1777,319)  12k(1705,420)  ?(1910,645)
```

```
#0245  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0245_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+30]
── BottomLeftUI (layer 0) [scrolled 1787 of 1787 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   5,135 (+2,195 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 14 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -15g | Laws: -400g | Other: +1021g | Upkeep: -1354g | Net: +1842g
   Treasury: 5,135g
   Actions refreshed: 5/5
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   Davout is now locked in intensive drill. Cannot receive orders until training completes.
   Soult's fortifications decay: 10% → 9%
   Lannes is now locked in intensive drill. Cannot receive orders until training completes.
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Crowded at Rhineland: Ney loses 306 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Murat loses 316 troops to the press of 3 corps on one province's roads
   Crowded at Rhineland: Massena loses 522 troops to the press of 3 corps on one province's roads
   Garrison at Hanover reinforced: 2,000 -> 4,000
   Bavaria loyalty 87 (+2): relations with the lord, the Code Abroad
   Peace concluded between Hanover and Prussia without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 14
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Austria would now join a league against us — relations −23. The price to keep her out: Talleyrand brings her to −10 in 2 turns (2 DP); buying off her design costs 1,008 gold and shortens the road to 1 turn.
   • Sire — Hanover and Prussia have made peace without us.
   SITUATION
   France holds 28 regions. Treasury: 5,135g (+1,842 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Rhineland — 25,592 — 3 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, four turns running.
   * Davout — Franche-Comte — 18,061 — Drilling.
   - Murat — Rhineland — 15,523 — 6 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, four turns running.
   * Ney — Rhineland — 15,016 — Drilling.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, four turns running.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   * Lannes — Franche-Comte — 12,343 — Drilling.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   Davout is now locked in intensive drill. Cannot receive orders until training completes.
   Soult's fortifications decay: 10% → 9%
   Lannes is now locked in intensive drill. Cannot receive orders until training completes.
   Supply cost you 1,144 men, at Rhineland.
   Bavaria loyalty 87 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Westphalia passes from Hanover to Prussia.
   East Frisia passes from Hanover to Prussia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 24. 2 DP a turn, 6 so far.
   THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   The court of Prussia takes up a new design: Armed Neutrality.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0246  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0246_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)]  [Spain  —  Alliance  |  +27 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1787 of 1787 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0247  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0247_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 426 of 730 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (4)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Hesse  —  Non-Aggression  |  +24 (Neutral)  [MISSION]]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Bavaria  —  Vassal  |  +73 (Loyal)]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1787 of 1787 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0248  click Hesse  ->  ok
  (clicked at (1825, 419))
view: <run>\frames\0248_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 222 px, 0 of 583 px] ──
   THE CABINET — Hesse
   DP: 5
   TALLEYRAND'S ASSESSMENT — HESSE / Status: Non-Aggression   Relation: +24 (Neutral) /  / "We have Hesse's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: Talleyrand recommends: Propose Defensive Alliance / Talleyrand: "Hesse stands on the Emperor's roads, Sire — The Protector of the Rhine (The Confederation of the Rhine). Proclaim  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Court Nation  —  Neutral (+24 over 3 turns)]  [Propose Defensive Alliance (2 DP)  —  Favorable]  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Break Treaty (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1787 of 1787 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   5,135 (+2,195 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0249  click Propose Defensive Alliance  ->  ok
  (clicked at (1825, 500))
view: <run>\frames\0249_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 68 px] ──
   DIPLOMATIC PROPOSAL — Hesse /  / Mutual: /   • Mutual open borders between France and Hesse /  / Harshness: Low / Acceptance estimate: ~64% (ACCEPT) / Key obstacle: the weight of the bloc pressing against them / DP cost: 2 /  / Political Context: /   • Hesse's court sees the French-led alignment consolidating across Europe and will resist a cross-bloc agreement. Spain is the decisive non-France sl …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1832 of 1832 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   5,135 (+2,195 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose defensive alliance with Hesse
map: unchanged (56 labels)
```

```
#0250  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0250_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 90 px] ──
   DIPLOMATIC PROPOSAL — Hesse /  / France concedes: /   • France pays 500 gold to Hesse / Mutual: /   • Mutual open borders between France and Hesse /  / Harshness: Low / Acceptance estimate: ~69% (ACCEPT) / Key obstacle: the weight of the bloc pressing against them / DP cost: 2 /  / Political Context: /   • Hesse's court sees the French-led alignment consolidating across Europe and will resist a cr …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   5,135 (+2,195 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (56 labels)
```

```
#0251  click Send these terms  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0251_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 3/7
   Threat 45 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 1919 of 1919 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   5,135 (+2,195 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Hessian court with your Defensive Alliance proposal. Expect a response by next turn. (2 DP spent)
map: unchanged (56 labels)
```

```
#0252  type Murat, move to Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0252_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Murat moves from Rhineland to Franche-Comte
Franche-Comte feeds 52,500; the 45,927 men standing there would lose ~917 a turn to crowding — too many corps on one province.
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2053 of 2053 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   5,135 (+2,195 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, move to Franche-Comte
   → Murat moves from Rhineland to Franche-Comte
   Franche-Comte feeds 52,500; the 45,927 men standing there would lose ~917 a turn to crowding — too many corps on one province.
   [4/5 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2061,451)  ?(2045,479)  Archduke John(2032,376)  Bernadotte(1930,451)  Napoleon(1964,425)  ?(1959,325)  Yorck(1958,287)  Ney(1814,397)  Massena(1839,371)  Soult(1753,436)  Davout(1801,497)  Lannes(1813,471)  Murat(1825,445)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(1945,376)  10k(1901,591)  ?(1901,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  4k(1777,319)  12k(1705,420)  ?(1910,645)
```

```
#0253  type Massena, move to Lorraine  ->  ok
  (typed and Enter)
view: <run>\frames\0253_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok Massena moves from Rhineland to Lorraine
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2164 of 2164 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   5,135 (+2,195 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, move to Lorraine
   → Massena moves from Rhineland to Lorraine
   [3/5 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2061,451)  ?(2045,479)  Archduke John(2032,376)  Bernadotte(1930,451)  Napoleon(1964,425)  ?(1959,325)  Yorck(1958,287)  Ney(1826,397)  Soult(1741,436)  Massena(1765,462)  Davout(1801,497)  Lannes(1813,436)  Murat(1835,462)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(1945,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  4k(1777,319)  12k(1693,420)  ?(1910,645)
```

```
#0254  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0254_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 14
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 45 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2098 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,870 (+2,545 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Austria would now join a league against us — relations −23. The price to keep her out: Talleyrand brings her to −10 in 2 turns (2 DP); buying off her design costs 1,008 gold and shortens the road to 1 turn.
   • Sire — Hanover and Prussia have made peace without us.
   SITUATION
   France holds 28 regions. Treasury: 5,135g (+1,842 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Rhineland — 25,592 — 3 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, four turns running.
   * Davout — Franche-Comte — 18,061 — Drilling.
   - Murat — Rhineland — 15,523 — 6 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, four turns running.
   * Ney — Rhineland — 15,016 — Drilling.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, four turns running.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   * Lannes — Franche-Comte — 12,343 — Drilling.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   Davout is now locked in intensive drill. Cannot receive orders until training completes.
   Soult's fortifications decay: 10% → 9%
   Lannes is now locked in intensive drill. Cannot receive orders until training completes.
   Supply cost you 1,144 men, at Rhineland.
   Bavaria loyalty 87 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Westphalia passes from Hanover to Prussia.
   East Frisia passes from Hanover to Prussia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 24. 2 DP a turn, 6 so far.
   THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   The court of Prussia takes up a new design: Armed Neutrality.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► propose defensive alliance with Hesse
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Hessian court with your Defensive Alliance proposal. Expect a response by next turn. (2 DP spent)
   ► Murat, move to Franche-Comte
   → Murat moves from Rhineland to Franche-Comte
   Franche-Comte feeds 52,500; the 45,927 men standing there would lose ~917 a turn to crowding — too many corps on one province.
   [4/5 actions remaining]
   ► Massena, move to Lorraine
   → Massena moves from Rhineland to Lorraine
   [3/5 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -31g | Laws: -400g | Other: +900g | Upkeep: -1324g | Net: +1735g
   Treasury: 6,870g
   Actions refreshed: 5/5
   DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   Soult's fortifications decay: 9% → 8%
   DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Crowded at Franche-Comte: Davout loses 361 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 246 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 310 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 89 (+2): relations with the lord, the Code Abroad
   Talleyrand returns from Hesse with excellent news: they have accepted our proposal! The decisive factor was natural willingness to negotiate.
   Treaty signed: Non-Aggression → Defensive Alliance with Hesse. You paid Hesse 500 gold from the treasury.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2061,451)  ?(2045,479)  Archduke John(2032,376)  Bernadotte(1930,451)  Napoleon(1964,425)  ?(1959,325)  Yorck(1958,287)  Ney(1826,397)  Soult(1741,436)  Massena(1765,462)  Davout(1801,497)  Lannes(1813,436)  Murat(1835,462)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(1945,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  ?(1777,319)  12k(1693,420)  ?(1910,645)
```

```
#0255  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0255_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 45 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 1676 of 1676 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,870 (+2,545 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -31g | Laws: -400g | Other: +900g | Upkeep: -1324g | Net: +1735g
   Treasury: 6,870g
   Actions refreshed: 5/5
   DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   Soult's fortifications decay: 9% → 8%
   DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Crowded at Franche-Comte: Davout loses 361 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 246 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 310 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 89 (+2): relations with the lord, the Code Abroad
   Talleyrand returns from Hesse with excellent news: they have accepted our proposal! The decisive factor was natural willingness to negotiate.
   Treaty signed: Non-Aggression → Defensive Alliance with Hesse. You paid Hesse 500 gold from the treasury.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 15
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
   • Sire — Sire — France and Hesse have signed the Defensive Alliance.
   • Sire — Europe has watched us 11 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 6,870g (+2,235 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — Awaiting orders.
   - Davout — Franche-Comte — 17,700 — Awaiting orders.
   - Murat — Franche-Comte — 15,213 — Awaiting orders.
   - Ney — Rhineland — 15,016 — 6 turns idle.
   ⚠ Crowded — Rhineland carries more corps than its roads can bear, four turns running.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Lannes — Franche-Comte — 12,097 — 4 turns idle.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — small force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   Soult's fortifications decay: 9% → 8%
   DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 95).
   Supply cost you 917 men, at Franche-Comte.
   Bavaria loyalty 89 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Hesse.
   THE LAWS: Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Hesse have signed the Defensive Alliance.
   Talleyrand returns from Hesse with a response.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0256  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0256_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)]  [Spain  —  Alliance  |  +26 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1676 of 1676 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0257  scroll 1828 500 down 5  ->  ok
  (scrolled down 5 at (1828, 500))
view: <run>\frames\0257_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 727 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)]  [Spain  —  Alliance  |  +26 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1676 of 1676 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0258  scroll 1828 500 down 10  ->  ok
  (scrolled down 10 at (1828, 500))
view: <run>\frames\0258_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 568 of 728 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Bavaria  —  Vassal  |  +73 (Loyal)]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Britain  —  Peace  |  -76 (Hostile)]  [Russia  —  Peace  |  -66 (Hostile)]  [Austria  —  Peace  |  -22 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1676 of 1676 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0259  click Hesse  ->  ERROR: no visible control's text holds "Hesse"
view: <run>\frames\0259_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 568 of 728 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1676 of 1676 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0260  scroll 1828 500 up 4  ->  ok
  (scrolled up 4 at (1828, 500))
view: <run>\frames\0260_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 385 of 728 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (4)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Hesse  —  Defensive Alliance  |  +24 (Neutral)  [MISSION]]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Bavaria  —  Vassal  |  +73 (Loyal)]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1676 of 1676 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0261  click Hesse  —  Defensive Alliance  ->  ok
  (clicked at (1825, 460))
view: <run>\frames\0261_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 244 px, 0 of 548 px] ──
   THE CABINET — Hesse
   DP: 7
   TALLEYRAND'S ASSESSMENT — HESSE / Status: Defensive Alliance   Relation: +24 (Neutral) /  / "Our alliance with Hesse holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Relations must improve before proposals will find purchase. Talleyrand is already at their court, Sire — net +8 a turn. / Talleyrand: "Hesse stands on the Emperor's roads, Sire — The Pr …
   Relations with Hesse stand at 24; an Alliance needs 40.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Court Nation  —  Neutral (+24 over 3 turns) — +24 earned; paused 1 turn on your errand]  [Propose Alliance (2 DP)  —  Favorable](disabled: Relations with Hesse stand at 24; an Alliance needs 40.)  [Propose Vassal (3 DP)  —  Unlikely]  [Declare War (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1676 of 1676 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,870 (+2,545 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   18,400
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0262  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0262_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1676 of 1676 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0263  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0263_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 15
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2118 of 2118 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   9,457 (+2,781 next turn)
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
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -58g | Laws: -400g | Other: +1741g | Upkeep: -1286g | Net: +2587g
   Treasury: 9,457g
   Actions refreshed: 5/5
   Soult's fortifications decay: 8% → 7%
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Crowded at Franche-Comte: Davout loses 354 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 241 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 304 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 91 (+2): relations with the lord, the Code Abroad
map: unchanged (56 labels)
```

```
#0264  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0264_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 1678 of 1678 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   9,457 (+2,781 next turn)
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
   [...earlier messages trimmed...]
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -58g | Laws: -400g | Other: +1741g | Upkeep: -1286g | Net: +2587g
   Treasury: 9,457g
   Actions refreshed: 5/5
   Soult's fortifications decay: 8% → 7%
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Crowded at Franche-Comte: Davout loses 354 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 241 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 304 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 91 (+2): relations with the lord, the Code Abroad
   ════════════════════════════════════
   MORNING DISPATCH — Turn 16
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march.
   SITUATION
   France holds 28 regions. Treasury: 9,457g (+2,587 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — Awaiting orders.
   - Davout — Franche-Comte — 17,346 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Ney — Rhineland — 15,016 — 7 turns idle.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 14,909 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Lannes — Franche-Comte — 11,856 — 5 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, two turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 8% → 7%
   Supply cost you 899 men, at Franche-Comte.
   Bavaria loyalty 91 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   THE LAWS: Russia enacts Arakcheev's Artillery — artillery levies cost 15% less (×0.85).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 32. 2 DP a turn, 8 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Naples may be ready to discuss improved relations. The diplomatic winds favor us.
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 12 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0265  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0265_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 16
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 17 — Late May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2120 of 2120 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   12,264 (+2,773 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -89g | Laws: -400g | Other: +1970g | Upkeep: -1264g | Net: +2807g
   Treasury: 12,264g
   Actions refreshed: 5/5
   Soult's fortifications decay: 7% → 6%
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Crowded at Franche-Comte: Davout loses 346 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 237 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 298 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 93 (+2): relations with the lord, the Code Abroad
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(2017,479)  Archduke Charles(2061,451)  ?(2045,479)  Archduke John(2032,376)  Bernadotte(1930,451)  Napoleon(1964,425)  ?(1959,325)  Yorck(1958,287)  Ney(1826,397)  Soult(1741,436)  Massena(1765,462)  Davout(1801,497)  Lannes(1813,436)  Murat(1835,462)  Deroy(1901,535)  ?(1551,403)  Castanos(1551,364)  ?(1945,376)  10k(1901,591)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  ?(1910,645)
```

```
#0266  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0266_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 2163 of 2163 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   12,264 (+2,773 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 8% → 7%
   Supply cost you 899 men, at Franche-Comte.
   Bavaria loyalty 91 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   THE LAWS: Russia enacts Arakcheev's Artillery — artillery levies cost 15% less (×0.85).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 32. 2 DP a turn, 8 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Naples may be ready to discuss improved relations. The diplomatic winds favor us.
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 12 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -89g | Laws: -400g | Other: +1970g | Upkeep: -1264g | Net: +2807g
   Treasury: 12,264g
   Actions refreshed: 5/5
   Soult's fortifications decay: 7% → 6%
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Crowded at Franche-Comte: Davout loses 346 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 237 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 298 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 93 (+2): relations with the lord, the Code Abroad
   ════════════════════════════════════
   MORNING DISPATCH — Turn 17
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Europe has watched us 13 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 12,264g (+2,807 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — Awaiting orders.
   - Davout — Franche-Comte — 17,000 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Ney — Rhineland — 15,016 — 8 turns idle.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 14,611 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Lannes — Franche-Comte — 11,619 — 6 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — large force [partial]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 7% → 6%
   Supply cost you 881 men, at Franche-Comte.
   Bavaria loyalty 93 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 40. 2 DP a turn, 10 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0267  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0267_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 37 titled provinces — 45 are needed (8 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)]  [Spain  —  Alliance  |  +24 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0268  scroll 1828 500 down 11  ->  ok
  (scrolled down 11 at (1828, 500))
view: <run>\frames\0268_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 466 of 746 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (4)
   Neutral (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Hesse  —  Defensive Alliance  |  +40 (Friendly)  [MISSION]]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Bavaria  —  Vassal  |  +73 (Loyal)]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2163 of 2163 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0269  click Hesse  —  Defensive Alliance  ->  ok
  (clicked at (1825, 379))
view: <run>\frames\0269_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 200 px, 0 of 505 px] ──
   THE CABINET — Hesse
   DP: 5
   TALLEYRAND'S ASSESSMENT — HESSE / Status: Defensive Alliance   Relation: +40 (Friendly) /  / "Our alliance with Hesse holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Talleyrand recommends: Propose Alliance / Talleyrand: "Hesse stands on the Emperor's roads, Sire — The Protector of the Rhine (The Confederation of the Rhine). Proclaim one in the Cabi …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Court Nation  —  Neutral → Friendly (+40, 5 turns) — +40 earned; paused 1 turn on your errand]  [Propose Alliance (2 DP)  —  Almost Certain]  [Propose Vassal (3 DP)  —  Unlikely]  [Declare War (1 DP)]  [Break Treaty (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2163 of 2163 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   12,264 (+2,773 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0270  click Propose Vassal  ->  ok
  (clicked at (1825, 556))
view: <run>\frames\0270_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Hesse /  / France demands: /   • Hesse pays 175 gold per turn to France for as long as the treaty stands /  / Harshness: Moderate / Acceptance estimate: ~28% (REJECT) / Key obstacle: personal opposition from their diplomat / DP cost: 3 /  / "Sire, regarding the Vassalage proposal to Hesse, I have prepared terms that reflect the current diplomatic climate."
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 17 — Late May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2207 of 2207 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   12,264 (+2,773 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose vassalization to Hesse
map: unchanged (55 labels)
```

```
#0271  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0271_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Hesse /  / France concedes: /   • France pays 500 gold to Hesse /  / Harshness: Low / Acceptance estimate: ~42% (COUNTER expected) / Key obstacle: personal opposition from their diplomat / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Hesse."
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2228 of 2228 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   12,264 (+2,773 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (55 labels)
```

```
#0272  click Even more generous  ->  ok
  (clicked at (1829, 674))
view: <run>\frames\0272_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Hesse /  / France concedes: /   • France pays 750 gold to Hesse /   • France cedes 1 AP per turn to Hesse for as long as the treaty stands /  / Harshness: Low / Acceptance estimate: ~62% (ACCEPT) / Key obstacle: personal opposition from their diplomat / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Hesse. We are offering everything short of the crown  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1678 of 1678 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   12,264 (+2,773 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -89g | Laws: -400g | Other: +1970g | Upkeep: -1264g | Net: +2807g
   Treasury: 12,264g
   Actions refreshed: 5/5
   Soult's fortifications decay: 7% → 6%
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Crowded at Franche-Comte: Davout loses 346 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 237 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 298 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 93 (+2): relations with the lord, the Code Abroad
   ════════════════════════════════════
   MORNING DISPATCH — Turn 17
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Europe has watched us 13 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 12,264g (+2,807 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — Awaiting orders.
   - Davout — Franche-Comte — 17,000 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Ney — Rhineland — 15,016 — 8 turns idle.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 14,611 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Lannes — Franche-Comte — 11,619 — 6 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — large force [partial]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 7% → 6%
   Supply cost you 881 men, at Franche-Comte.
   Bavaria loyalty 93 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 40. 2 DP a turn, 10 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► propose vassalization to Hesse
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
map: unchanged (55 labels)
```

```
#0273  click Less generous  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0273_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Hesse /  / France concedes: /   • France pays 500 gold to Hesse /  / Harshness: Low / Acceptance estimate: ~42% (COUNTER expected) / Key obstacle: personal opposition from their diplomat / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Hesse."
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1700 of 1700 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   12,264 (+2,773 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: less generous
map: unchanged (55 labels)
```

```
#0274  click Send these terms  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0274_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 2/7
   Threat 45 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 1767 of 1767 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   12,264 (+2,773 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Hessian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
map: unchanged (55 labels)
```

```
#0275  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0275_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 17
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1787 of 1788 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   15,048 (+2,751 next turn)
   Inf:
   100,000
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
   Sire — Europe has watched us 13 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 12,264g (+2,807 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — Awaiting orders.
   - Davout — Franche-Comte — 17,000 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Ney — Rhineland — 15,016 — 8 turns idle.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 14,611 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Lannes — Franche-Comte — 11,619 — 6 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, three turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — large force [partial]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 7% → 6%
   Supply cost you 881 men, at Franche-Comte.
   Bavaria loyalty 93 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Hesse continue. Relations now at 40. 2 DP a turn, 10 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 26 and declare on turn 29: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► propose vassalization to Hesse
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
   Directing Talleyrand: less generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Hessian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
   ► end turn
   ═══════════════════════════════════════
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -123g | Laws: -400g | Other: +1973g | Upkeep: -1256g | Net: +2784g
   Treasury: 15,048g
   Actions refreshed: 5/5
   Soult's fortifications decay: 6% → 5%
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Bohemia: Archduke Charles loses 534 troops
   Supply shortage at Bohemia: Archduke John loses 221 troops
   Crowded at Franche-Comte: Davout loses 340 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 232 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 292 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 95 (+2): relations with the lord, the Code Abroad
   Talleyrand returns from Hesse with a counter-proposal. They could not accept our terms, but offer an alternative:
   Vassalage between France and Hesse
   - France offers 500 gold
   - France offers 800 gold
map: unchanged (55 labels)
```

```
#0276  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0276_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 1942 of 1942 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   15,048 (+2,751 next turn)
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
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
   Directing Talleyrand: less generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Hessian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
   ► end turn
   ═══════════════════════════════════════
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -123g | Laws: -400g | Other: +1973g | Upkeep: -1256g | Net: +2784g
   Treasury: 15,048g
   Actions refreshed: 5/5
   Soult's fortifications decay: 6% → 5%
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Bohemia: Archduke Charles loses 534 troops
   Supply shortage at Bohemia: Archduke John loses 221 troops
   Crowded at Franche-Comte: Davout loses 340 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 232 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 292 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 95 (+2): relations with the lord, the Code Abroad
   Talleyrand returns from Hesse with a counter-proposal. They could not accept our terms, but offer an alternative:
   Vassalage between France and Hesse
   - France offers 500 gold
   - France offers 800 gold
   ════════════════════════════════════
   MORNING DISPATCH — Turn 18
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Europe has watched us 14 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia, Austria and 4 lesser courts would march. The cheapest court to keep out of it is Austria: Talleyrand brings her to −10 in 1 turn (1 DP); buying off her design costs 1,008 gold.
   SITUATION
   France holds 28 regions. Treasury: 15,048g (+2,784 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — 3 turns idle.
   - Davout — Franche-Comte — 16,660 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, four turns running.
   - Ney — Rhineland — 15,016 — 9 turns idle.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 14,319 — 3 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, four turns running.
   - Lannes — Franche-Comte — 11,387 — 7 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, four turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — large force [partial]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 6% → 5%
   Supply cost you 864 men, at Franche-Comte.
   Bavaria loyalty 95 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Hesse.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand returns from Hesse with a response.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Hesse — Vassalage
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 14 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0277  click Envoys (1)  ->  ok
  (clicked at (3401, 18))
view: <run>\frames\0277_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   COUNTER-OFFER / Chancery of Hesse (Dove) of Hesse /  / In response to your Vassalage proposal, Hesse offers modified terms: /  / Revised Terms: /   - You pay Hesse 500 gold at the signing /   - You pay Hesse 800 gold at the signing /  / Hesse, wishing to go unnoticed: "Hesse counts what a quarrel with France would cost and what an understanding would return, and finds his councillors of one mind." …
   controls: [Accept Terms]  [Reject Terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1942 of 1942 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   15,048 (+2,751 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — a letter stands unanswered: the Cabinet stays shut until it is answered)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 14 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0278  click Accept Terms  ->  ok
  (clicked at (1679, 878))
view: <run>\frames\0278_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 50 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Hesse]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 2007 of 2007 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   13,748 (+2,992 next turn)
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
   Responding to Hesse's proposal: accepted
   You have accepted Hesse's counter-proposal. Treaty signed: Defensive Alliance → Vassal with Hesse. You paid Hesse 1,300 gold from the treasury.
map: unchanged (55 labels)
```

```
#0279  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0279_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 39 titled provinces — 45 are needed (6 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)]  [Spain  —  Alliance  |  +23 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2007 of 2007 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   Responding to Hesse's proposal: accepted
   You have accepted Hesse's counter-proposal. Treaty signed: Defensive Alliance → Vassal with Hesse. You paid Hesse 1,300 gold from the treasury.
map: unchanged (55 labels)
```

```
#0280  scroll 1828 500 down 11  ->  ok
  (scrolled down 11 at (1828, 500))
view: <run>\frames\0280_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 466 of 746 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (5)
   Neutral (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Bavaria  —  Vassal  |  +73 (Loyal)]  [Hesse  —  Vassal  |  +40 (Friendly)  [MISSION]]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2007 of 2007 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   Responding to Hesse's proposal: accepted
   You have accepted Hesse's counter-proposal. Treaty signed: Defensive Alliance → Vassal with Hesse. You paid Hesse 1,300 gold from the treasury.
map: unchanged (55 labels)
```

```
#0281  click Hesse  —  Vassal  ->  ok
  (clicked at (1825, 482))
view: <run>\frames\0281_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 90 px, 0 of 112 px] ──
   THE CABINET — Hesse
   DP: 7
   TALLEYRAND'S ASSESSMENT — HESSE / Status: Vassal   Relation: +40 (Friendly) / Loyalty: 60 ↑   Autonomy: Satellite   Tribute: 262g /  / "Hesse serves faithfully. Tribute flows, the garrison keeps order. A reliable vassal." / Recommendation: No urgent action needed / Talleyrand: "Hesse stands on the Emperor's roads, Sire — The Protector of the Rhine (The Confederation of the Rhine). Proclaim one in  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Court Nation  —  Neutral → Friendly (+40, 5 turns) — +40 earned; paused 2 turns on your errand]  [Invest in Vassal (1 DP + 200g)]  [Increase Autonomy (1 DP)  —  loyalty 60 → 70; its autonomy drift -2 → +1 a turn; tribute 75% → 50% (-87 gold a turn); the ports shut against Britain stay 0 of 26]  [Decrease Autonomy (1 DP)  —  loyalty 60 → 45; its autonomy drift -2 → -4 a turn; tribute 75% → 100% (+88 gold a turn); the ports shut against Britain stay 0 of 26]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2007 of 2007 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   13,748 (+2,992 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   Responding to Hesse's proposal: accepted
   You have accepted Hesse's counter-proposal. Treaty signed: Defensive Alliance → Vassal with Hesse. You paid Hesse 1,300 gold from the treasury.
map: unchanged (55 labels)
```

```
#0282  click Cancel: Court Nation  ->  ok
  (clicked at (1825, 462))
view: <run>\frames\0282_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 50 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   13,748 (+2,992 next turn)
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
   ► Talleyrand, cancel mission with Hesse
   Talleyrand's mission to Hesse has been cancelled.
map: unchanged (55 labels)
```

```
#0283  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0283_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 39 titled provinces — 45 are needed (6 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)]  [Spain  —  Alliance  |  +23 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Hesse's proposal: accepted
   You have accepted Hesse's counter-proposal. Treaty signed: Defensive Alliance → Vassal with Hesse. You paid Hesse 1,300 gold from the treasury.
   ► Talleyrand, cancel mission with Hesse
   Talleyrand's mission to Hesse has been cancelled.
map: unchanged (55 labels)
```

```
#0284  scroll 1828 500 down 20  ->  ok
  (scrolled down 20 at (1828, 500))
view: <run>\frames\0284_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 687 of 727 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Britain  —  Peace  |  -73 (Hostile)]  [Russia  —  Peace  |  -63 (Hostile)]  [Austria  —  Peace  |  -19 (Wary)]  [Sweden  —  Peace  |  -43 (Hostile)]  [Naples  —  Peace  |  -13 (Wary)]  [Hanover  —  Peace  |  -33 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Hesse's proposal: accepted
   You have accepted Hesse's counter-proposal. Treaty signed: Defensive Alliance → Vassal with Hesse. You paid Hesse 1,300 gold from the treasury.
   ► Talleyrand, cancel mission with Hesse
   Talleyrand's mission to Hesse has been cancelled.
map: unchanged (55 labels)
```

```
#0285  click Austria  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0285_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 310 px, 0 of 422 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -19 (Wary) /  / "Austria maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. Courting Austria would be quicker — ≈3 turns again …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purchase.](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1008g) (1 DP + 1008g)  —  The design sleeps while the bargain stands — and waking it by betrayal is the strongest casus belli in Europe. Buying it wakes The Eastern Question next (1008g to buy off in turn).]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   13,748 (+2,992 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Hesse's proposal: accepted
   You have accepted Hesse's counter-proposal. Treaty signed: Defensive Alliance → Vassal with Hesse. You paid Hesse 1,300 gold from the treasury.
   ► Talleyrand, cancel mission with Hesse
   Talleyrand's mission to Hesse has been cancelled.
map: unchanged (55 labels)
```

```
#0286  click Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0286_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Austria /  / "Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 50 / 100
   Turn 18 — Early June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2141 of 2141 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   13,748 (+2,992 next turn)
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
   ► improve relations with Austria
map: unchanged (55 labels)
```

```
#0287  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0287_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 50 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 2206 of 2206 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   13,748 (+2,992 next turn)
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
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (55 labels)
```

```
#0288  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0288_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 39 titled provinces — 45 are needed (6 more to win and )  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Prussia  —  Non-Aggression  |  +2 (Neutral)]  [Spain  —  Alliance  |  +23 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Talleyrand's mission to Hesse has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (55 labels)
```

```
#0289  scroll 1828 500 down 11  ->  ok
  (scrolled down 11 at (1828, 500))
view: <run>\frames\0289_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 466 of 746 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (5)
   Neutral (7)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Bavaria  —  Vassal  |  +73 (Loyal)]  [Hesse  —  Vassal  |  +40 (Friendly)]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Talleyrand's mission to Hesse has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (55 labels)
```

```
#0290  click Hesse  —  Vassal  ->  ok
  (clicked at (1825, 482))
view: <run>\frames\0290_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 90 px, 0 of 68 px] ──
   THE CABINET — Hesse
   DP: 7
   TALLEYRAND'S ASSESSMENT — HESSE / Status: Vassal   Relation: +40 (Friendly) / Loyalty: 60 ↑   Autonomy: Satellite   Tribute: 262g /  / "Hesse serves faithfully. Tribute flows, the garrison keeps order. A reliable vassal." / Recommendation: No urgent action needed / Talleyrand: "Hesse stands on the Emperor's roads, Sire — The Protector of the Rhine (The Confederation of the Rhine). Proclaim one in  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Invest in Vassal (1 DP + 200g)]  [Increase Autonomy (1 DP)  —  loyalty 60 → 70; its autonomy drift -2 → +1 a turn; tribute 75% → 50% (-87 gold a turn); the ports shut against Britain stay 0 of 26]  [Decrease Autonomy (1 DP)  —  loyalty 60 → 45; its autonomy drift -2 → -4 a turn; tribute 75% → 100% (+88 gold a turn); the ports shut against Britain stay 0 of 26]  [Release Vassal (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   13,748 (+2,992 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Esc: menu · click to type)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Talleyrand's mission to Hesse has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (55 labels)
```

```
#0291  click Invest in Vassal  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0291_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE CABINET ASKS:
   "Invest in Hesse: 200 gold and 1 diplomatic point. Her loyalty rises +10 (60 → 70), and Hesse cannot be invested in again for 3 turns. The treasury holds 13,748 gold and would hold 13,548 after. Invest? (yes / no)"
   controls: [Invest]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 50 / 100
   Turn 18 — Early June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2273 of 2273 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   13,748 (+2,992 next turn)
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
   ► invest in Hesse
   The Cabinet requests clarification...
map: unchanged (55 labels)
```

```
#0292  click Invest  ->  ok
  (clicked at (1829, 509))
view: <run>\frames\0292_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 50 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 1787 of 1787 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   13,548 (+2,994 next turn)
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
   Crowded at Franche-Comte: Lannes loses 232 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 292 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 95 (+2): relations with the lord, the Code Abroad
   Talleyrand returns from Hesse with a counter-proposal. They could not accept our terms, but offer an alternative:
   Vassalage between France and Hesse
   - France offers 500 gold
   - France offers 800 gold
   ════════════════════════════════════
   MORNING DISPATCH — Turn 18
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Europe has watched us 14 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia, Austria and 4 lesser courts would march. The cheapest court to keep out of it is Austria: Talleyrand brings her to −10 in 1 turn (1 DP); buying off her design costs 1,008 gold.
   SITUATION
   France holds 28 regions. Treasury: 15,048g (+2,784 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — 3 turns idle.
   - Davout — Franche-Comte — 16,660 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, four turns running.
   - Ney — Rhineland — 15,016 — 9 turns idle.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 14,319 — 3 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, four turns running.
   - Lannes — Franche-Comte — 11,387 — 7 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, four turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — large force [partial]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications decay: 6% → 5%
   Supply cost you 864 men, at Franche-Comte.
   Bavaria loyalty 95 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Hesse.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand returns from Hesse with a response.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Hesse — Vassalage
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 14 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia, Austria and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Ney grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   Responding to Hesse's proposal: accepted
   You have accepted Hesse's counter-proposal. Treaty signed: Defensive Alliance → Vassal with Hesse. You paid Hesse 1,300 gold from the treasury.
   ► Talleyrand, cancel mission with Hesse
   Talleyrand's mission to Hesse has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
   ► invest in Hesse
   The Cabinet requests clarification...
   > invest in Hesse confirmed
   Invested in Hesse: +10 loyalty (60 → 70). Cost: 1 DP + 200g. Cooldown: 3 turns.
map: unchanged (55 labels)
```

```
#0293  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0293_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 18
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 48 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2274 of 2274 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   16,568 (+2,984 next turn)
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
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -138g | Laws: -400g | Other: +2202g | Upkeep: -1234g | Net: +3020g | Spent: 200g
   Treasury: 16,568g
   Actions refreshed: 5/5
   Soult's men maintain minimal defenses. (5% - stable)
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Bohemia: Archduke Charles loses 589 troops
   Supply shortage at Bohemia: Archduke John loses 230 troops
   Crowded at Franche-Comte: Davout loses 333 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 227 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 286 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 97 (+2): relations with the lord, the Code Abroad
map: unchanged (55 labels)
```

```
#0294  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0294_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 48 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 1787 of 1787 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   16,568 (+2,984 next turn)
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
   The Cabinet requests clarification...
   > invest in Hesse confirmed
   Invested in Hesse: +10 loyalty (60 → 70). Cost: 1 DP + 200g. Cooldown: 3 turns.
   ► end turn
   ═══════════════════════════════════════
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -138g | Laws: -400g | Other: +2202g | Upkeep: -1234g | Net: +3020g | Spent: 200g
   Treasury: 16,568g
   Actions refreshed: 5/5
   Soult's men maintain minimal defenses. (5% - stable)
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Bohemia: Archduke Charles loses 589 troops
   Supply shortage at Bohemia: Archduke John loses 230 troops
   Crowded at Franche-Comte: Davout loses 333 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 227 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 286 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 97 (+2): relations with the lord, the Code Abroad
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Sire — France and Hesse have signed the Vassalage.
   • Sire — Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
   • Sire — Europe has watched us 15 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia and 4 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 16,568g (+3,020 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — 4 turns idle.
   - Davout — Franche-Comte — 16,327 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, five turns running.
   - Ney — Rhineland — 15,016 — 10 turns idle.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 14,033 — 4 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, five turns running.
   - Lannes — Franche-Comte — 11,160 — 8 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, five turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — large force [partial]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's men maintain minimal defenses. (5% - stable)
   Supply cost you 846 men, at Franche-Comte.
   Bavaria loyalty 97 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Hesse has been established under the protection of France.
   Sire — France and Hesse have signed the Vassalage.
   THE LAWS: Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -10. 1 DP a turn, 1 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 39 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 48/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0295  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0295_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 19
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 46 / 100
   Turn 20 — Early July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1720 of 1722 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   19,592 (+2,987 next turn)
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
   Bavaria loyalty 97 (+2): relations with the lord, the Code Abroad
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Sire — France and Hesse have signed the Vassalage.
   • Sire — Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
   • Sire — Europe has watched us 15 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia and 4 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 16,568g (+3,020 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — 4 turns idle.
   - Davout — Franche-Comte — 16,327 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, five turns running.
   - Ney — Rhineland — 15,016 — 10 turns idle.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 14,033 — 4 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, five turns running.
   - Lannes — Franche-Comte — 11,160 — 8 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, five turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — large force [partial]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's men maintain minimal defenses. (5% - stable)
   Supply cost you 846 men, at Franche-Comte.
   Bavaria loyalty 97 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Hesse has been established under the protection of France.
   Sire — France and Hesse have signed the Vassalage.
   THE LAWS: Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -10. 1 DP a turn, 1 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 39 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 48/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -174g | Laws: -400g | Other: +2204g | Upkeep: -1196g | Net: +3024g
   Treasury: 19,592g
   Actions refreshed: 5/5
   Soult's fortifications strengthen: +7% defense (max 12%)
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Bohemia: Archduke Charles loses 572 troops
   Supply shortage at Bohemia: Archduke John loses 223 troops
   Crowded at Franche-Comte: Davout loses 326 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 223 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 280 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 99 (+2): relations with the lord, the Code Abroad
map: unchanged (55 labels)
```

```
#0296  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0296_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 46 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3351,64)]  [icon: Lannes arrived @(3393,64)]  [icon: Massena arrived @(3435,64)]  [icon: Ney arrived (x2) @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Settlement Ratified (x2) @(3561,64)]  [+31]
── BottomLeftUI (layer 0) [scrolled 1767 of 1767 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   19,592 (+2,987 next turn)
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
   Threat: 48/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -174g | Laws: -400g | Other: +2204g | Upkeep: -1196g | Net: +3024g
   Treasury: 19,592g
   Actions refreshed: 5/5
   Soult's fortifications strengthen: +7% defense (max 12%)
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Bohemia: Archduke Charles loses 572 troops
   Supply shortage at Bohemia: Archduke John loses 223 troops
   Crowded at Franche-Comte: Davout loses 326 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 223 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 280 troops to the press of 3 corps on one province's roads
   Bavaria loyalty 99 (+2): relations with the lord, the Code Abroad
   ════════════════════════════════════
   MORNING DISPATCH — Turn 20
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia and 4 lesser courts would march.
   SITUATION
   France holds 28 regions. Treasury: 19,592g (+3,024 by the accounts) — the chest could enact the Train des Équipages — 3,500g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   # Soult — Lorraine — 30,000 — Fortified at Lorraine.
   - Massena — Lorraine — 25,592 — 5 turns idle.
   - Davout — Franche-Comte — 16,001 — Awaiting orders.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, 6 turns running.
   - Ney — Rhineland — 15,016 — 11 turns idle.
   - Deroy — Munich — 14,999 — Awaiting orders. Trust:40
   - Murat — Franche-Comte — 13,753 — 5 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, 6 turns running.
   - Lannes — Franche-Comte — 10,937 — 9 turns idle.
   ⚠ Crowded — Franche-Comte carries more corps than its roads can bear, 6 turns running.
   - Bernadotte — Franconia — 9,054 — Awaiting orders. Trust:40 Morale:46%
   - Napoleon — Franconia — 7,095 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — large force [partial]
   Archduke John — Bohemia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Yorck — Berlin — small force [partial]
   TURN EVENTS
   Soult's fortifications strengthen: +7% defense (max 12%)
   Supply cost you 829 men, at Franche-Comte.
   Bavaria loyalty 99 (+2): relations with the lord, the Code Abroad
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -2. 1 DP a turn, 2 so far.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 39 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 16 quiet turns. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0297  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0297_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 20
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 21 — Late July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2230 of 2230 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   21
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   22,609 (+2,981 next turn)
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
   TURN 21 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -211g | Laws: -400g | Other: +2204g | Upkeep: -1166g | Net: +3017g
   Treasury: 22,609g
   Actions refreshed: 5/5
   Soult's fortifications decay: 7% → 6%
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Lannes has +20% shock bonus ready - use it in your next attack!
   REMINDER: Murat has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Bohemia: Archduke Charles loses 629 troops
   Supply shortage at Bohemia: Archduke John loses 231 troops
   Crowded at Franche-Comte: Davout loses 320 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 218 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 275 troops to the press of 3 corps on one province's roads
map: unchanged (55 labels)
```

```
#0298  quit  ->  ok
  (the engine quits)
view: <run>\frames\0298_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2230 of 2230 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Supply shortage at Bohemia: Archduke John loses 231 troops
   Crowded at Franche-Comte: Davout loses 320 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Lannes loses 218 troops to the press of 3 corps on one province's roads
   Crowded at Franche-Comte: Murat loses 275 troops to the press of 3 corps on one province's roads
map: unchanged (55 labels)
```

