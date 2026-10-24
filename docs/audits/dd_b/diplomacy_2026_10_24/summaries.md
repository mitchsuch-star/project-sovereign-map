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
   Horace Vernet — The Battle of Jena  ·  public domain
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
   J. M. W. Turner — The Battle of Trafalgar  ·  public domain
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
#0004  click Diplomacy  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0004_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 3017 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 5/5
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 40% of the continent's weight. /   The courts believe he will go as far as war (alarm 70). /   They think he is coming for Hesse — his corps stand against their soil. /  / The Emperor's …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
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
#0005  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0005_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
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
#0006  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 150 of 836 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   Treaties (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Cancel]
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
#0007  click Austria  ->  ok
  (clicked at (1825, 605))
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
#0008  scroll 1800 560 down 10  ->  ok
  (scrolled down 10 at (1800, 560))
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 308 of 355 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Sire, the field reads +0 and no road carries. Propose Peace comes nearest at -1 of 50; her loyalty to the league — she has no reason of her own to brea …
   France is at war with this court.
   France is at war with this court.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal i](disabled: France is at war with this court.)  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the](disabled: France is at war with this court.)  [Subjugate  —  make her France's vassal by conquest — she must be beaten first](disabled: Austria still stands — Vienna is its own and 3 of its corps are in the field (its war scor)  [Back]  [Cancel]
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
#0009  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
#0010  click the terms  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 1077 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Any court may be treated with here, Sire — ally, neutral or foe. Each act is priced in diplomatic points (DP), which return every turn; I read the court and name the price before you choose.
   The Congress of Paris — 7 of 8 terms met  ▾ hide the terms /     ✓ 1 administrative action (you have 2) /     • 45 titled provinces (35 of 45) /     ✓ Paris held /     ✓ the Emperor free /     ✓ no satellite on the brink of rebellion /     ✓ Europe's alarm below 80 (now 70 — falling 2 a turn: our bloc's weight in Europe +1 against 3 of decay (one, plus one for each court at peace with us, at most  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▾ hide the terms>  [Cancel]
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
#0011  scroll 1800 560 down 6  ->  ok
  (scrolled down 6 at (1800, 560))
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 229 of 1058 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▾ hide the terms /     ✓ 1 administrative action (you have 2) /     • 45 titled provinces (35 of 45) /     ✓ Paris held /     ✓ the Emperor free /     ✓ no satellite on the brink of rebellion /     ✓ Europe's alarm below 80 (now 70 — falling 2 a turn: our bloc's weight in Europe +1 against 3 of decay (one, plus one for each court at peace with us, at most  …
   The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and settle).
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▾ hide the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Cancel]
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
#0012  click hide the terms  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 191 of 837 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Cancel]
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
#0013  scroll 1800 560 down 10  ->  ok
  (scrolled down 10 at (1800, 560))
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
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
#0014  click Prussia  ->  ok
  (clicked at (1825, 482))
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 310 px, 0 of 474 px] ──
   THE CABINET — Prussia
   DP: 5
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: -10 (Wary) /  / "Prussia maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. Courting Prussia would be quicker — ≈4 turns again …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal i](disabled: Their price is 1128g — the treasury holds 800g.)  [Back]  [Cancel]
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
#0015  click Improve Relations  ->  ok
  (clicked at (1825, 458))
view: <run>\frames\0015_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Prussia /  / "Sire, I shall begin efforts to improve relations with Prussia. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1500 of 1500 px] ──
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
── BottomLeftUI (layer 0) [scrolled 1565 of 1565 px] ──
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
#0017  click THIRD COALITION  ->  ERROR: 2 controls match "THIRD COALITION" — pick one with click#N
  candidates: #1 [THIRD COALITION  ▸] on WarStatusPanel @(3429,965) | #2 [War with the Third Coalition] on WarStatusPanel @(3429,996)
view: <run>\frames\0017_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1565 of 1565 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0018  click#1 THIRD COALITION  ->  ok
  (clicked at (3429, 965))
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
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
   Leader: Britain   Posture: Aggressive /  /   Britain  WE:0  Unknown  — leads the coalition /   Austria  WE:0  ~125,000 men /   Russia  WE:0  Unknown /  / Coordination /   Britain-Austria: Good /   Britain-Russia: Good /   Austria-Russia: Good /  / Weak link: Britain (highest WE)
   controls: [icon @(3139,276)]  [Open Whole-War Settlement]  [Target Austria]  [Target Russia]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1565 of 1565 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
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
── BottomLeftUI (layer 0) [scrolled 1565 of 1565 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0020  type what can I do  ->  ok
  (typed and Enter)
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
── BottomLeftUI (layer 0) [scrolled 1257 of 1257 px] ──
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
#0021  type Ney, scout Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney scouts Swabia: Controlled by Bavaria. Terrain: Plains. Enemy forces: Mack (Austria): ~52,000 troops
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1898 of 1898 px] ──
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
   ► Ney, scout Swabia
   👁 Ney scouts Swabia: Controlled by Bavaria. Terrain: Plains. Enemy forces: Mack (Austria): ~52,000 troops
   [3/4 actions remaining]
map: unchanged (53 labels)
```

```
#0022  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 180 px] ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Mack attacks Swabia /     Region captured: Swabia (was Bavaria) (secured) / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 5,197 casualties, 48,803 remaining /     Massena: 4,960 casualties, 37,040 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Mass …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2318 of 2318 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,444 (+892 next turn)
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
   ► end turn
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -248g | Other: +1295g | Upkeep: -2684g | Net: +644g
   Treasury: 1,444g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,434 troops
   Supply shortage at Tyrol: Archduke John loses 588 troops
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,464)  Ney(1814,397)  Davout(1839,371)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1825,436)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,648)
```

```
#0023  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   42,000 → 37,040
   54,000 → 48,803
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3233,64)]  [icon: Envoy from Prussia @(3275,64)]  [icon: Envoy from Ottoman Empire @(3317,64)]  [icon: Envoy from Portugal @(3359,64)]  [Talleyrand at Prussia — Improving Relations]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   0 →
   T:1
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,444 (+892 next turn)
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
   ► Ney, scout Swabia
   👁 Ney scouts Swabia: Controlled by Bavaria. Terrain: Plains. Enemy forces: Mack (Austria): ~52,000 troops
   [3/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -248g | Other: +1295g | Upkeep: -2684g | Net: +644g
   Treasury: 1,444g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,434 troops
   Supply shortage at Tyrol: Archduke John loses 588 troops
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
   France holds 28 regions. Treasury: 1,444g (+892 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 68% of French forces (an estimate — 2 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 37,040 — Awaiting orders.
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
   Mack — Swabia — 52,000 [confirmed]
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
   Talleyrand's efforts in Prussia continue. Relations now at -2.
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
map: unchanged (57 labels)
```

```
#0024  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Massena ◆' (PanelContainer, layer 121))
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   AUSTRIA LOSSES
   4,960
   5,197
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 37,040
   54,000 → 48,803
   Berthier: “Stalemate. Massena and Archduke Charles glare at each other across the field.” / Archduke Charles: "France pays full price for every Austrian mile now."
   THE GREAT BATTLE OF MILAN
   MILAN · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0025  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,444 (+892 next turn)
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
map: unchanged (57 labels)
```

```
#0026  click Envoys  ->  ok
  (clicked at (3387, 18))
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Open ▸
   Turn 1
   Incoming proposal: Open Borders Agreement
   THE COURTS WRITE (2)
   Ottoman Empire and Portugal write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
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
   controls: {ACTIVE}  {WAITING}  [Accept]  [Decline]  {WAITING}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0027  click Open  ->  ERROR: no visible control's text holds "Open"
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0028  click_at 1400 205  ->  ok
  (clicked at (1400, 205) on VBoxContainer 'PENDING ENVOYS (3)' (VBoxContainer, layer 119))
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0029  click_at 1828 278  ->  ok
  (clicked at (1828, 278) on @PanelContainer@921 'ACTIVE' (PanelContainer, layer 119))
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders /  / Hardenberg, stiffly: "Prussia's interest is the Rhine at peace and the army at home; Berlin signs where those two meet. Open the borders." /  / An unexpected overture. There may be hidden motives worth examining. /  / This offer will  …
   controls: [Accept]  [Let Talleyrand haggle (1 DP)]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2096 of 2096 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,444 (+892 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0030  click Accept  ->  ok
  (clicked at (1574, 687))
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   DP: 6/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3254,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Prussia @(3633,64)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2162 of 2162 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,444 (+911 next turn)
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
map: unchanged (57 labels)
```

```
#0031  click#1 Accept  ->  ok
  (clicked at (1433, 465))
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   DP: 6/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3254,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Prussia @(3633,64)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2184 of 2184 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,444 (+911 next turn)
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
map: unchanged (57 labels)
```

```
#0032  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3254,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Prussia @(3633,64)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2206 of 2206 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,444 (+911 next turn)
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
map: unchanged (57 labels)
```

```
#0033  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
map: unchanged (57 labels)
```

```
#0034  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 767 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (5)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +39 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
map: unchanged (57 labels)
```

```
#0035  click Russia  ->  ERROR: 2 controls match "Russia" — pick one with click#N
  candidates: #1 [Russia  —  At War  |  -80 (Hostile)] on DiplomacyWizard @(1825,484) | #2 [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]] on DiplomacyWizard @(1825,587)
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 767 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
map: unchanged (57 labels)
```

```
#0036  click#1 Russia  ->  ok
  (clicked at (1825, 484))
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 354 px, 0 of 313 px] ──
   THE CABINET — Russia
   DP: 6
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: At War — the War for Swabia   Relation: -80 (Hostile) /  / "The war with Russia grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — the court sees no reason to sign at +0: Propose Peace stands at 6 of 50; it wants her loyalty to the league — she has no reason of her own to break ra …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Unlikely]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2206 of 2206 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
map: unchanged (57 labels)
```

```
#0037  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 530 px] ──
   ARMISTICE PREVIEW - Russia /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Russia /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 1 turn old and stays so; exhaustion holds. No territory or gold changes hands until it ends. / …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2252 of 2252 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,504 (+930 next turn)
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
   ► propose armistice with Russia
map: unchanged (57 labels)
```

```
#0038  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 552 px] ──
   ARMISTICE PREVIEW - Russia /  / Proposed Terms / France concedes: /   • France pays 150 gold per turn to Russia for as long as the treaty stands / Mutual: /   • Armistice (cease hostilities temporarily) — France and Russia /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1674 of 1674 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,504 (+930 next turn)
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
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,444g (+892 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 68% of French forces (an estimate — 2 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 37,040 — Awaiting orders.
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
   Mack — Swabia — 52,000 [confirmed]
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
   Talleyrand's efforts in Prussia continue. Relations now at -2.
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
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
   ► propose armistice with Russia
   Directing Talleyrand: modify generous
map: unchanged (57 labels)
```

```
#0039  click Even more generous  ->  ok
  (clicked at (1829, 674))
view: <run>\frames\0039_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 552 px] ──
   ARMISTICE PREVIEW - Russia /  / Proposed Terms / France concedes: /   • France pays 225 gold per turn to Russia for as long as the treaty stands /   • France cedes 1 AP per turn to Russia for as long as the treaty stands / Mutual: /   • Armistice (cease hostilities temporarily) — France and Russia /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger sta …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1696 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,504 (+930 next turn)
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
   Directing Talleyrand: modify generous
map: unchanged (57 labels)
```

```
#0040  click Not Now  ->  ok
  (clicked at (2056, 727))
view: <run>\frames\0040_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3212,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Prussia @(3591,64)]  [icon: Open Borders Agreement Accepted @(3633,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   0 →
   T:1
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [scrolled 1762 of 1762 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,504 (+930 next turn)
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (57 labels)
```

```
#0041  type who am I fighting  ->  ok
  (typed and Enter)
view: <run>\frames\0041_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +0 (evenly matched), in its 2nd turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the war banner on the left (click the war); every court's design in the Diplomatic Ledger (press D).
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1895 of 1895 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,504 (+930 next turn)
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
   ► who am I fighting
   We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +0 (evenly matched), in its 2nd turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the war banner on the left (click the war); every court's design in the Diplomatic Ledger (press D).
map: unchanged (57 labels)
```

```
#0042  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0042_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (52,000 men) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  Swabia feeds 40,000 — the whole muster standing there would lose ~6,000 men a turn to short supply.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   18,000 → 16,905
   Murat
   22,000 → 21,465
   Davout
   26,000 → 24,735
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 22,052 → 21,741 after the advance
   52,000 → 32,023
   marched to the guns
   marched to the guns
   +2 corps in reserve — 486 lost
   Soult — awaits explicit orders
   THE GREAT BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3212,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Prussia @(3591,64)]  [icon: Open Borders Agreement Accepted @(3633,64)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War for Swabia
   +18 →
   T:1
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1950 of 1950 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,238 (+1,171 next turn)
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
   War Purpose: Defense vs Austria (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   War Purpose: Defense vs Russia (War for Swabia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
   ► propose armistice with Russia
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► who am I fighting
   We are at war with the Third Coalition (Britain, Austria and Russia), Sire — war score +0 (evenly matched), in its 2nd turn. Our purpose: the defense of the homeland — 28 of 28 provinces held. Their designs: Britain pursues The Low Countries; Austria pursues Redeem Italy; Russia pursues Arbiter of Europe. Each war is on the war banner on the left (click the war); every court's design in the Diplomatic Ledger (press D).
   ► Ney, attack Mack
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (52,000 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10) — and will stand at Swabia
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Swabia
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   Swabia feeds 40,000 — the whole muster standing there would lose ~6,000 men a turn to short supply.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 100,000 we muster) would cost ~750g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney's forces advance steadily. Ney gains the advantage over Mack. Casualties: Ney's army 5,329, Mack 19,977. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -266g, Austria -998g. Our treasury stands at 1,238 gold. Ney advances into Swabia. (311 lost to march)
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
   His supporting allies lost 3,381 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 1,948 | Mack 19,977
   Strength: Ney 24,000 → 22,052 → 21,741 after the advance | Mack 52,000 → 32,023
   Berthier: "Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2024,508)  France(1596,525)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1871,360)  Ney +4(1847,444)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,590)  Archduke John(2017,563)  Soult(1753,436)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0043  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Ney ◆' (PanelContainer, layer 121))
view: <run>\frames\0043_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   5,329
   19,977
   Lannes
   18,000 → 16,905
   Murat
   22,000 → 21,465
   Davout
   26,000 → 24,735
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 22,052 → 21,741 after the advance
   52,000 → 32,023
   marched to the guns
   marched to the guns
   +2 corps in reserve — 486 lost
   Soult — awaits explicit orders
   Berthier: “Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire.” / Mack: "A temporary derangement of the arithmetic. Vienna will understand."
   THE GREAT BATTLE OF SWABIA
   SWABIA · TURN 2
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1950 of 1950 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0044  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0044_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1950 of 1950 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0045  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0045_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1950 of 1950 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0046  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0046_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 767 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (5)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +39 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1950 of 1950 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0047  click Austria  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0047_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 402 px] ──
   THE CABINET — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War for Swabia   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Permit me to observe, Sire, that a level war is the dearest kind to end: Propose Peace reads 18 of 50; it wants her loyalty to the league — she has no reason of her  …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Unlikely]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Unlikely]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1950 of 1950 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0048  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0048_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1950 of 1950 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0049  type what if Ney attacks Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0049_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Were you to give the order, Sire:
MUSTER — Ney (21,741; expect about 105,220 with the corps likely to arrive) vs Mack (32,023 men) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: stands on the field and will fight beside him
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL JOIN — Lannes: stands on the field and will fight beside him
  WILL JOIN — Murat: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Napoleon: stands on the field and will fight beside him
  The Emperor commands in person — every corps on this field fights +10% harder.
  Swabia feeds 32,000 — the whole muster standing there would lose ~5,659 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 94,360 we muster) would cost ~708g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
  Napoleon shares the field at Swabia — his men will absorb part of 
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2397 of 2397 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,238 (+1,171 next turn)
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
   ► what if Ney attacks Mack
   Were you to give the order, Sire:
   MUSTER — Ney (21,741; expect about 105,220 with the corps likely to arrive) vs Mack (32,023 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Swabia feeds 32,000 — the whole muster standing there would lose ~5,659 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 94,360 we muster) would cost ~708g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Nothing has been ordered, and nothing spent.
map: unchanged (52 labels)
```

```
#0050  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0050_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok MUSTER — Ney (21,741; expect about 105,220 with the corps likely to arrive) vs Mack (32,023 men) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: stands on the field and will fight beside him
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL JOIN — Lannes: stands on the field and will fight beside him
  WILL JOIN — Murat: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Napoleon: stands on the field and will fight beside him
  The Emperor commands in person — every corps on this field fights +10% harder.
  Swabia feeds 32,000 — the whole muster standing there would lose ~5,659 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 94,360 we muster) would cost ~708g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
  Napoleon shares the field at Swabia — his men will absorb part of any losses.
Ask 'what if Ney attac
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Ney has taken Swabia
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+600 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3170 of 3170 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,151 (+1,111 next turn)
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
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,381 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 1,948 | Mack 19,977
   Strength: Ney 24,000 → 22,052 → 21,741 after the advance | Mack 52,000 → 32,023
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
   MUSTER — Ney (21,741; expect about 105,220 with the corps likely to arrive) vs Mack (32,023 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Swabia feeds 32,000 — the whole muster standing there would lose ~5,659 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 94,360 we muster) would cost ~708g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Nothing has been ordered, and nothing spent.
   ► Ney, attack Mack
   ⚔ Second Battle of Swabia ⚔
   MUSTER — Ney (21,741; expect about 105,220 with the corps likely to arrive) vs Mack (32,023 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Swabia feeds 32,000 — the whole muster standing there would lose ~5,659 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 94,360 we muster) would cost ~708g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   Ney holds them at Swabia while allies attack from Rhineland! (+1 coordination)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Alert] Ney's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney's forces press forward aggressively. Ney decisively defeats Mack! Mack's army is destroyed. Ney's army suffered 1,753 casualties.
   [Materiel] Guns, horses and stores lost with the fallen: France -87g, Austria -1779g. Our treasury stands at 1,151 gold. Mack's army is destroyed! Swabia has been captured by France!
   [Alarm] Europe's alarm rises +10 — Conquered territory +2, Won a battle +3, Won a decisive battle +5.
   Your forces have taken Swabia. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ★ Enemy army destroyed! ★
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
   Ney fought with Davout, Lannes, Murat and Napoleon beside him — massed effective strength: 21,741 (lead) + 83,479 committed (Davout, Lannes, Murat, Napoleon) = 105,220.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Ney's supporting allies lost 1,129 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%, Exhaustion -10%, Flanking +1%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 624 | Mack 32,023
   Strength: Ney 21,741 → 21,117 | Mack 32,023 → 0
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1613,523)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney +4(1847,444)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,579)  Archduke John(2039,511)  Soult(1753,436)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,492)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0051  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0051_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   16,905 → 16,544
   Murat
   21,465 → 21,282
   Davout
   24,735 → 24,312
   ⚔
   Ney ◆
   Mack ◆
   21,741 → 21,117
   32,023 → 0
   +2 corps in reserve — 162 lost
   Soult — awaits explicit orders
   SECOND BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3212,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]  [icon: Treaty with Prussia @(3591,64)]  [icon: Open Borders Agreement Accepted @(3633,64)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   +38 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3796 of 3796 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,151 (+1,111 next turn)
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
map: unchanged (52 labels)
```

```
#0052  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Ney ◆' (PanelContainer, layer 121))
view: <run>\frames\0052_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A DECISIVE VICTORY
   FRANCE LOSSES
   AUSTRIA LOSSES
   1,753
   32,023
   Swabia falls to France.
   Lannes
   16,905 → 16,544
   Murat
   21,465 → 21,282
   Davout
   24,735 → 24,312
   ⚔
   Ney ◆
   Mack ◆
   21,741 → 21,117
   32,023 → 0
   +2 corps in reserve — 162 lost
   DESTROYED
   Soult — awaits explicit orders
   Berthier: “Bernadotte failed to arrive in time. Ney's army fought without expected support.”
   SECOND BATTLE OF SWABIA
   SWABIA · TURN 2
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3796 of 3796 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (52 labels)
```

```
#0053  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0053_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3796 of 3796 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,151 (+1,111 next turn)
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
map: unchanged (52 labels)
```

```
#0054  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0054_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 3796 of 3796 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (52 labels)
```

```
#0055  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0055_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 767 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (5)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +39 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3796 of 3796 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (52 labels)
```

```
#0056  click Austria  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0056_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 402 px] ──
   THE CABINET — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." / Recommendation: Permit me to observe, Sire, that every door is shut by arithmetic, not by malice: Propose Peace reads 40 of 50. H …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Uncertain — a counter is likely]  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Uncertain — a counter is likely]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3796 of 3796 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (52 labels)
```

```
#0057  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0057_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 640 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (2 battles, 2 decisives kept); the war is 1 turn old and stays so; exhaustion holds. No territory or gold changes hands until it ends. …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2621 of 2621 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,151 (+1,111 next turn)
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
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 1,948 | Mack 19,977
   Strength: Ney 24,000 → 22,052 → 21,741 after the advance | Mack 52,000 → 32,023
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
   MUSTER — Ney (21,741; expect about 105,220 with the corps likely to arrive) vs Mack (32,023 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Swabia feeds 32,000 — the whole muster standing there would lose ~5,659 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 94,360 we muster) would cost ~708g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Nothing has been ordered, and nothing spent.
   ► Ney, attack Mack
   ⚔ Second Battle of Swabia ⚔
   MUSTER — Ney (21,741; expect about 105,220 with the corps likely to arrive) vs Mack (32,023 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Swabia feeds 32,000 — the whole muster standing there would lose ~5,659 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 94,360 we muster) would cost ~708g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   Ney holds them at Swabia while allies attack from Rhineland! (+1 coordination)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Alert] Ney's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney's forces press forward aggressively. Ney decisively defeats Mack! Mack's army is destroyed. Ney's army suffered 1,753 casualties.
   [Materiel] Guns, horses and stores lost with the fallen: France -87g, Austria -1779g. Our treasury stands at 1,151 gold. Mack's army is destroyed! Swabia has been captured by France!
   [Alarm] Europe's alarm rises +10 — Conquered territory +2, Won a battle +3, Won a decisive battle +5.
   Your forces have taken Swabia. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ★ Enemy army destroyed! ★
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
   Ney fought with Davout, Lannes, Murat and Napoleon beside him — massed effective strength: 21,741 (lead) + 83,479 committed (Davout, Lannes, Murat, Napoleon) = 105,220.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Ney's supporting allies lost 1,129 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%, Exhaustion -10%, Flanking +1%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 624 | Mack 32,023
   Strength: Ney 21,741 → 21,117 | Mack 32,023 → 0
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
   ► propose armistice with Austria
map: unchanged (52 labels)
```

```
#0058  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0058_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 662 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / France concedes: /   • France pays 115 gold per turn to Austria for as long as the treaty stands / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (2 battles, 2 decisives kept); the  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2643 of 2643 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,151 (+1,111 next turn)
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
   Directing Talleyrand: modify generous
map: unchanged (52 labels)
```

```
#0059  scroll 1800 450 down 15  ->  ok
  (scrolled down 15 at (1800, 450))
view: <run>\frames\0059_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 638 of 662 px] ──
   ARMISTICE PREVIEW - Austria /  / Proposed Terms / France concedes: /   • France pays 115 gold per turn to Austria for as long as the treaty stands / Mutual: /   • Armistice (cease hostilities temporarily) — France and Austria /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (2 battles, 2 decisives kept); the  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2643 of 2643 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
   ► propose armistice with Austria
   Directing Talleyrand: modify generous
map: unchanged (52 labels)
```

```
#0060  click Send these terms  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0060_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3220,64)]  [icon: Treaty with Prussia @(3262,64)]  [icon: Open Borders Agreement Accepted @(3304,64)]  [icon: Treaty with Ottoman @(3346,64)]  [icon: Treaty with Portugal @(3388,64)]  [Talleyrand at Prussia — Improving Relations]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   +38 →
   T:1
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 2709 of 2709 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,151 (+1,111 next turn)
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
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (52 labels)
```

```
#0061  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0061_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 749 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2709 of 2709 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose armistice with Austria
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (52 labels)
```

```
#0062  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0062_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 767 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (3)
   Treaties (5)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +39 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2709 of 2709 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose armistice with Austria
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (52 labels)
```

```
#0063  click#1 Russia  ->  ok
  (clicked at (1825, 484))
view: <run>\frames\0063_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 376 px, 0 of 357 px] ──
   THE CABINET — Russia
   DP: 5
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Russia grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Sire, the field reads +0 and no road carries. Propose Peace comes nearest at 6 of 50; her loyalty to the league — she has no reason of her own to break r …
   Talleyrand in transit
   Talleyrand in transit
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Unlikely](disabled: Talleyrand in transit)  [Open Settlement — the whole table: Britain, Austria and Russia]  [Propose White Peace — the whole table: Britain, Austria and Russia]  [Propose Peace (3 DP)  —  Hopeless](disabled: Talleyrand in transit)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2709 of 2709 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose armistice with Austria
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (52 labels)
```

```
#0064  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0064_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2709 of 2709 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► propose armistice with Austria
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (52 labels)
```

```
#0065  type Davout, move to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0065_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Swabia to Rhineland
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2820 of 2820 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   1,151 (+1,111 next turn)
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
   ► Davout, move to Rhineland
   → Davout moves from Swabia to Rhineland
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1613,523)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney +3(1847,454)  Davout(1830,397)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,579)  Archduke John(2039,511)  Soult(1753,436)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  ?(1893,372)  25k(1595,492)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0066  type Murat, move to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0066_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves from Swabia to Rhineland
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2930 of 2930 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   1,151 (+1,111 next turn)
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
   ► Murat, move to Rhineland
   → Murat moves from Swabia to Rhineland
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1613,523)  Bavaria(1933,501)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Lannes(1845,438)  Napoleon(1871,375)  Davout(1830,401)  Murat(1839,349)  ?(1951,590)  Archduke Charles(1940,537)  ?(1979,579)  Archduke John(2039,511)  Soult(1753,436)  Dumonceau(1755,323)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,376)  ?(1901,617)  25k(1595,492)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0067  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0067_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 685 px] ──
   ENEMY PHASE - Turn 2
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Second Battle of Milan /     Archduke Charles: 4,867 casualties, 42,502 remaining /     Massena's army: 4,683 casualties — Massena's own corps: 32,864 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%)  …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 82 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2879 of 2881 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,407 (+709 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Nothing has been ordered, and nothing spent.
   ► Ney, attack Mack
   ⚔ Second Battle of Swabia ⚔
   MUSTER — Ney (21,741; expect about 105,220 with the corps likely to arrive) vs Mack (32,023 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him — but he and Ney are at odds; expect about half his weight
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   Swabia feeds 32,000 — the whole muster standing there would lose ~5,659 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 94,360 we muster) would cost ~708g.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him.
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Ask 'what if Ney attacks Mack' to read the muster before you commit — it costs nothing.
   Ney holds them at Swabia while allies attack from Rhineland! (+1 coordination)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Alert] Ney's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney's forces press forward aggressively. Ney decisively defeats Mack! Mack's army is destroyed. Ney's army suffered 1,753 casualties.
   [Materiel] Guns, horses and stores lost with the fallen: France -87g, Austria -1779g. Our treasury stands at 1,151 gold. Mack's army is destroyed! Swabia has been captured by France!
   [Alarm] Europe's alarm rises +10 — Conquered territory +2, Won a battle +3, Won a decisive battle +5.
   Your forces have taken Swabia. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ★ Enemy army destroyed! ★
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
   Ney fought with Davout, Lannes, Murat and Napoleon beside him — massed effective strength: 21,741 (lead) + 83,479 committed (Davout, Lannes, Murat, Napoleon) = 105,220.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Ney's supporting allies lost 1,129 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%, Exhaustion -10%, Flanking +1%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 624 | Mack 32,023
   Strength: Ney 21,741 → 21,117 | Mack 32,023 → 0
   Berthier: "Bernadotte failed to arrive in time. Ney's army fought without expected support."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
   ► propose armistice with Austria
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
   ► Davout, move to Rhineland
   → Davout moves from Swabia to Rhineland
   [1/4 actions remaining]
   ► Murat, move to Rhineland
   → Murat moves from Swabia to Rhineland
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -281g | Materiel: -453g | Other: +1218g | Upkeep: -2728g | Net: +256g
   Treasury: 1,407g
   Actions refreshed: 4/4
   Bavaria completes a market at Franconia.
   Supply shortage at Franconia: Archduke Charles loses 531 troops
   Crowded at Swabia: Ney loses 422 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Lannes loses 330 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Napoleon loses 187 troops to the press of 3 corps on one province's roads
   Talleyrand returns from Austria with excellent news: they have accepted our proposal! The decisive factor was our military dominance.
   Treaty signed: At War → Armistice with Austria.
   Britain subsidizes Austria with 200 gold.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Lannes(1845,438)  Davout(1830,397)  Murat(1839,371)  ?(1951,590)  Archduke John(1948,537)  Soult(1753,436)  ?(1880,562)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,404)  ?(1901,617)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0068  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0068_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Teulie
   7,500 → 6,993
   ⚔
   Massena ◆
   Archduke Charles ◆
   37,040 → 32,864
   47,369 → 42,502
   THE GREAT SECOND BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 82 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Envoy from Denmark @(3231,64)]  [icon: Envoy from Saxony @(3273,64)]  [icon: Marshal Murat seeks an audience @(3315,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
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
   1,407 (+709 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Bavaria completes a market at Franconia.
   Supply shortage at Franconia: Archduke Charles loses 531 troops
   Crowded at Swabia: Ney loses 422 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Lannes loses 330 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Napoleon loses 187 troops to the press of 3 corps on one province's roads
   Talleyrand returns from Austria with excellent news: they have accepted our proposal! The decisive factor was our military dominance.
   Treaty signed: At War → Armistice with Austria.
   Britain subsidizes Austria with 200 gold.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — General Mack of Austria is destroyed at Swabia — his corps annihilated, his name struck from their order of battle.
   • Sire — Marshal Ney has destroyed Mack's corps at Swabia. No enemy formation remains in that field.
   • Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
   • Sire — London now pays Vienna 200 gold a turn against us. The coalition has its paymaster; it lacks only its armies.
   SITUATION
   France holds 28 regions. Treasury: 1,407g (+709 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Massena — Milan — 29,621 — Hunted by Archduke Charles on consecutive turns — holds Milan with 29,621 men.
   - Davout — Rhineland — 24,312 — Awaiting orders.
   - Murat — Rhineland — 21,282 — Awaiting orders.
   - Ney — Swabia — 20,695 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Lannes — Swabia — 16,214 — Awaiting orders.
   - Napoleon — Swabia — 9,165 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   - Teulie — Milan — 5,844 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Franconia — 35,343 [confirmed]
   Deroy — Munich — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 939 men, at Swabia.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 29).
   War exhaustion grows — Austria nears breaking point (exhaustion: 49).
   Talleyrand has departed for the court of Austria.
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Austria have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +38 for France (2 battles, 2 decisives kept); the war is 2 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -80 and will thaw to -65, short of -60; the ledger and the war's age come back with it. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 1 French corps stands on Bavarian soil under the truce.
   Talleyrand returns from Austria with a response.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0069  look  ->  ok
  (a fresh frame)
view: <run>\frames\0069_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   3,543
   3,682
   Teulie
   7,500 → 6,993
   ⚔
   Massena ◆
   Archduke Charles ◆
   37,040 → 32,864
   47,369 → 42,502
   THE GREAT SECOND BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 2
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0070  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Massena ◆' (PanelContainer, layer 121))
view: <run>\frames\0070_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   AUSTRIA LOSSES
   4,683
   4,867
   Teulie
   7,500 → 6,993
   ⚔
   Massena ◆
   Archduke Charles ◆
   37,040 → 32,864
   47,369 → 42,502
   Berthier: “An inconclusive affair. Both sides bloodied but unbroken.” / Archduke Charles: "Your Emperor needs quick victories. I need only deny them."
   THE GREAT SECOND BATTLE OF MILAN
   MILAN · TURN 2
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0071  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0071_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2026 of 2026 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,407 (+709 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0072  click Envoys  ->  ok
  (clicked at (3391, 18))
view: <run>\frames\0072_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2026 of 2026 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0073  click#1 Accept  ->  ok
  (clicked at (1433, 421))
view: <run>\frames\0073_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   Threat 82 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Envoy from Denmark @(3231,64)]  [icon: Envoy from Saxony @(3273,64)]  [icon: Marshal Murat seeks an audience @(3315,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2048 of 2048 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,407 (+709 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
map: unchanged (53 labels)
```

```
#0074  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0074_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 82 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3189,64)]  [icon: Envoy from Denmark @(3231,64)]  [icon: Envoy from Saxony @(3273,64)]  [icon: Marshal Murat seeks an audience @(3315,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2070 of 2070 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,407 (+709 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (53 labels)
```

```
#0075  click Dispatch  ->  ok
  (clicked at (425, 18))
view: <run>\frames\0075_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1785 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 3 — Late October 1805 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — General Mack of Austria is destroyed at Swabia — his corps annihilated, his name struck from their order of battle. /   • Sire — Marsh …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (2)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2070 of 2070 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (53 labels)
```

```
#0076  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0076_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 2070 of 2070 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (53 labels)
```

```
#0077  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0077_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2070 of 2070 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (53 labels)
```

```
#0078  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0078_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 769 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (2)
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +38 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2070 of 2070 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (53 labels)
```

```
#0079  look  ->  ok
  (a fresh frame)
view: <run>\frames\0079_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 769 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2070 of 2070 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (53 labels)
```

```
#0080  click Austria  ->  ok
  (clicked at (1825, 545))
view: <run>\frames\0080_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 486 px, 0 of 325 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Permit me to observe, Sire, that a truce is a clock, not a treaty: 5 turns, relations -80, and the ledger stands: the war score reads +38 for Franc …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2070 of 2070 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (53 labels)
```

```
#0081  scroll 1800 560 down 5  ->  ok
  (scrolled down 5 at (1800, 560))
view: <run>\frames\0081_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 486 px, 129 of 344 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Permit me to observe, Sire, that a truce is a clock, not a treaty: 5 turns, relations -80, and the ledger stands: the war score reads +38 for Franc …
   Mission already active
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Peace (2 DP)  —  Unlikely]  [Improve Relations (1 DP)  —  +8 relation/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2070 of 2070 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (53 labels)
```

```
#0082  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0082_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2070 of 2070 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (53 labels)
```

```
#0083  click Recall  ->  ok
  (clicked at (3635, 64))
view: <run>\frames\0083_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 82 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Austria @(3442,64)]  [icon: Armistice Accepted @(3484,64)]  [icon: Treaty with Denmark @(3526,64)]  [icon: Treaty with Saxony @(3568,64)]  [+5]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2158 of 2158 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,489 (+736 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (53 labels)
```

```
#0084  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0084_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 2158 of 2158 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (53 labels)
```

```
#0085  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0085_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 769 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (2)
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)]  [Spain  —  Alliance  |  +38 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2158 of 2158 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (53 labels)
```

```
#0086  click Austria  ->  ok
  (clicked at (1825, 545))
view: <run>\frames\0086_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 0 of 233 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: If I may, Sire — 5 turns of quiet remain with Austria; the ledger stands: the war score reads +38 for France (2 battles, 2 decisives kept); the war …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2158 of 2158 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (53 labels)
```

```
#0087  scroll 1800 560 down 5  ->  ok
  (scrolled down 5 at (1800, 560))
view: <run>\frames\0087_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 464 px, 129 of 215 px] ──
   THE CABINET — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: If I may, Sire — 5 turns of quiet remain with Austria; the ledger stands: the war score reads +38 for France (2 battles, 2 decisives kept); the war …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Peace (2 DP)  —  Unlikely]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2158 of 2158 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (53 labels)
```

```
#0088  click Improve Relations  ->  ok
  (clicked at (1825, 583))
view: <run>\frames\0088_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Austria /  / "Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 82 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2204 of 2204 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,489 (+736 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► improve relations with Austria
map: unchanged (53 labels)
```

```
#0089  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0089_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 82 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Blockade — Britain closes our ports @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Austria @(3442,64)]  [icon: Armistice Accepted @(3484,64)]  [icon: Treaty with Denmark @(3526,64)]  [icon: Treaty with Saxony @(3568,64)]  [+5]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1695 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,489 (+736 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Massena — Milan — 29,621 — Hunted by Archduke Charles on consecutive turns — holds Milan with 29,621 men.
   - Davout — Rhineland — 24,312 — Awaiting orders.
   - Murat — Rhineland — 21,282 — Awaiting orders.
   - Ney — Swabia — 20,695 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Lannes — Swabia — 16,214 — Awaiting orders.
   - Napoleon — Swabia — 9,165 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   - Teulie — Milan — 5,844 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Franconia — 35,343 [confirmed]
   Deroy — Munich — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   TURN EVENTS
   Supply cost you 939 men, at Swabia.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 29).
   War exhaustion grows — Austria nears breaking point (exhaustion: 49).
   Talleyrand has departed for the court of Austria.
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Austria have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +38 for France (2 battles, 2 decisives kept); the war is 2 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -80 and will thaw to -65, short of -60; the ledger and the war's age come back with it. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 1 French corps stands on Bavarian soil under the truce.
   Talleyrand returns from Austria with a response.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0090  look  ->  ok
  (a fresh frame)
view: <run>\frames\0090_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1695 of 1696 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0091  click Generals  ->  ok
  (clicked at (228, 18))
view: <run>\frames\0091_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 6568 px] ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  / SEEKS AN AUDIENCE — Murat /   / [5] Murat    [Cavalry]  France / The Cavalry Reserve - screening the Black Forest feint while the army wheels north of the Danube. / Aggressive: +15% attack, +5% more in aggressive stance. Fortify capped at 10%. Grows restless if idle too long. / Cava …
   controls: [Pin]  [icon @(2213,236)]  <Hear him — he seeks an audience>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (1 AP)>  <Commission a Marshal…>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (1 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>  <Fortify>  <Drill>  <Hold (2 AP)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1695 of 1696 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0092  click Hear him  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0092_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   MURAT — Marshal Murat seeks an audience
   Give him a command is closed — There is no enemy within his reach to send him against.
   "Sire — I have earned better than to watch Ney take the field while I hold a road." /  / Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a command worthy of his talents. /  / What each answer does / • Let it stand (Free) — Free, and it fixes nothing. For 4 more turns he brings NONE of his 21,282 men to any battle Ney leads, and the quarrel may harden further. / …
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Give him a command   [2 AP]](disabled: There is no enemy within his reach to send him against.)  [Later (he will return)]
── TopBar (layer 75) [under a modal]: unchanged
── MarshalManagement (layer 50) [under a modal] [scrolled 0 of 6568 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1695 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,489 (+736 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0093  click Later  ->  ok
  (clicked at (1829, 746))
view: <run>\frames\0093_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) [scrolled 0 of 6568 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1695 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,489 (+736 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0094  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0094_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -1 →
   T:2
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 5t]
── BottomLeftUI (layer 0) [scrolled 1695 of 1696 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (53 labels)
```

```
#0095  type Lannes, move to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0095_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes moves from Swabia to Rhineland
Rhineland feeds 60,000; the 61,808 men standing there would lose ~1,263 a turn to short supply.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1828 of 1828 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,489 (+928 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, move to Rhineland
   → Lannes moves from Swabia to Rhineland
   Rhineland feeds 60,000; the 61,808 men standing there would lose ~1,263 a turn to short supply.
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Napoleon(1834,438)  Davout(1830,397)  Lannes(1829,371)  Murat(1839,345)  ?(1951,590)  Archduke John(1948,537)  Soult(1753,436)  ?(1880,562)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,404)  ?(1901,617)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0096  type Napoleon, move to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0096_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Swabia to Rhineland
Rhineland feeds 60,000; the 70,973 men standing there would lose ~2,322 a turn to short supply.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1962 of 1962 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,489 (+1,036 next turn)
   Inf:
   84,625
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, move to Rhineland
   → Napoleon moves from Swabia to Rhineland
   Rhineland feeds 60,000; the 70,973 men standing there would lose ~2,322 a turn to short supply.
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,376)  ?(1959,325)  Brunswick(1958,287)  Ney(1859,464)  Davout +3(1832,350)  ?(1951,590)  Archduke John(1948,537)  Soult(1753,436)  ?(1880,562)  Dumonceau(1755,322)  Massena(1898,589)  Teulie(1922,563)  ?(2068,435)  ?(1959,404)  ?(1901,617)  ?(1857,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0097  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0097_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 224 px] ──
   ENEMY PHASE - Turn 3
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Franconia /     Region captured: Franconia (was Bavaria) (secured) / - Archduke Charles attacks Deroy /     Battle of Munich /     Archduke Charles: 1,765 casualties, 33,578 remaining /     Deroy: 4,431 casualties, 13,627 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) /     ⚔ View the field /     - …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 81 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1921 of 1922 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,648 (+1,122 next turn)
   Inf:
   86,750
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 29).
   War exhaustion grows — Austria nears breaking point (exhaustion: 49).
   Talleyrand has departed for the court of Austria.
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Sire — France and Austria have signed the Armistice.
   A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +38 for France (2 battles, 2 decisives kept); the war is 2 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -80 and will thaw to -65, short of -60; the ledger and the war's age come back with it. Bavaria stays at war with Austria — an ally, not a client: her war runs on, and 1 French corps stands on Bavarian soil under the truce.
   Talleyrand returns from Austria with a response.
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
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their order of battle is one commander shorter — permanently, Sire. Press the advantage while their line is headless."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
   ► Lannes, move to Rhineland
   → Lannes moves from Swabia to Rhineland
   Rhineland feeds 60,000; the 61,808 men standing there would lose ~1,263 a turn to short supply.
   [3/4 actions remaining]
   ► Napoleon, move to Rhineland
   → Napoleon moves from Swabia to Rhineland
   Rhineland feeds 60,000; the 70,973 men standing there would lose ~2,322 a turn to short supply.
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -329g | Other: +1298g | Upkeep: -2310g | Net: +1159g
   Treasury: 2,648g
   Actions refreshed: 4/4
   Supply shortage at Franconia: Bernadotte loses 211 troops
   Supply shortage at Rhineland: Davout loses 796 troops
   Supply shortage at Rhineland: Lannes loses 530 troops
   Supply shortage at Rhineland: Murat loses 696 troops
   Supply shortage at Rhineland: Napoleon loses 300 troops
   Garrison at Munich reinforced: 5,000 -> 7,000
   Switzerland loyalty 96 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Teulie's contingent comes home — 5,844 of 7,500 men.
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier reports that Massena appears envious of Ney's laurels — he has grown restless for glory.
   Bernadotte is on the wrong side of the frontier at Franconia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 5 turns of safe passage.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2058,562)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Bavaria(1872,518)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  31(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Archduke Charles(1955,477)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Deroy(1850,438)  Davout +3(1832,361)  ?(1501,602)  Castanos(1501,564)  ?(1965,579)  Archduke John(1948,547)  Soult(1753,436)  Dumonceau(1755,322)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  7k(1860,560)  ?(1900,373)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0098  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0098_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 81 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Hesse @(3189,64)]  [icon: Envoy from Papal States @(3231,64)]  [icon: Marshal Murat seeks an audience @(3273,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]  [icon: Treaty with Austria @(3645,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franconia
   -1 →
   T:3
   controls: [THIRD COALITION  ▸]  [War for Franconia]  [War for Franconia — Austria, truce 4t]
── BottomLeftUI (layer 0) [scrolled 1784 of 1784 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,648 (+1,122 next turn)
   Inf:
   86,750
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Supply shortage at Rhineland: Murat loses 696 troops
   Supply shortage at Rhineland: Napoleon loses 300 troops
   Garrison at Munich reinforced: 5,000 -> 7,000
   Switzerland loyalty 96 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Teulie's contingent comes home — 5,844 of 7,500 men.
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier reports that Massena appears envious of Ney's laurels — he has grown restless for glory.
   Bernadotte is on the wrong side of the frontier at Franconia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 5 turns of safe passage.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Franconia has been taken by Austria.
   • Sire — under the truce with Austria. Bernadotte is on the wrong side of the frontier at Franconia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 5 turns of safe passage.
   • Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
   • Sire — London now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1,368 gold and shortens the road to 5 turns.
   SITUATION
   France holds 28 regions. Treasury: 2,648g (+1,159 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Massena — Milan — 29,621 — Hunted by Archduke Charles on consecutive turns — holds Milan with 29,621 men.
   - Davout — Rhineland — 23,516 — Awaiting orders.
   - Ney — Swabia — 20,695 — Awaiting orders.
   - Murat — Rhineland — 20,586 — Awaiting orders.
   > Bernadotte — Franconia — 16,789 — Moving to Franche-Comte — 2 turns out. Trust:40
   - Lannes — Rhineland — 15,684 — Awaiting orders.
   - Napoleon — Rhineland — 8,865 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Swabia — 7,969 [confirmed]
   Archduke Charles — Franconia — 29,527 [confirmed]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Supply cost you 2,533 men, at Franconia and Rhineland.
   Switzerland loyalty 96 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Massena appears envious of Ney's laurels — he has grown restless for glory.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   Franconia passes from Bavaria to Austria.
   Bernadotte stands on Franconia, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   War exhaustion grows — Austria nears breaking point (exhaustion: 60).
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -69.
   Teulie's contingent comes home — 5,844 of 7,500 men.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non-Aggression Pact
   - Papal States — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franconia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Franconia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War for Franconia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 81/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0099  look  ->  ok
  (a fresh frame)
view: <run>\frames\0099_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1784 of 1784 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 81/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0100  click Envoys  ->  ok
  (clicked at (3375, 18))
view: <run>\frames\0100_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 81/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0101  click#1 Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0101_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   DP: 6/7
   Threat 81 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Hesse @(3189,64)]  [icon: Envoy from Papal States @(3231,64)]  [icon: Marshal Murat seeks an audience @(3273,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]  [icon: Treaty with Austria @(3645,64)]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,648 (+1,122 next turn)
   Inf:
   86,750
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
map: unchanged (53 labels)
```

```
#0102  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0102_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 81 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Hesse @(3189,64)]  [icon: Envoy from Papal States @(3231,64)]  [icon: Marshal Murat seeks an audience @(3273,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]  [icon: Treaty with Austria @(3645,64)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1828 of 1828 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,648 (+1,122 next turn)
   Inf:
   86,750
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (53 labels)
```

```
#0103  click Dispatch  ->  ok
  (clicked at (425, 18))
view: <run>\frames\0103_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1609 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 4 — Early November 1805 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Franconia has been taken by Austria. /   • Sire — under the truce with Austria. Bernadotte is on the wrong side of the frontier at F …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (2)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1828 of 1828 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (53 labels)
```

```
#0104  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0104_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Franconia
   -1 →
   T:3
   controls: [THIRD COALITION  ▸]  [War for Franconia]  [War for Franconia — Austria, truce 4t]
── BottomLeftUI (layer 0) [scrolled 1828 of 1828 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (53 labels)
```

```
#0105  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0105_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 1828 of 1828 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (53 labels)
```

```
#0106  scroll 1800 560 down 12  ->  ok
  (scrolled down 12 at (1800, 560))
view: <run>\frames\0106_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 489 of 752 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Bavaria  —  Alliance  |  +57 (Friendly)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Hesse  —  Non-Aggression  |  0 (Neutral)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1828 of 1828 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (53 labels)
```

```
#0107  scroll 1800 560 down 15  ->  ok
  (scrolled down 15 at (1800, 560))
view: <run>\frames\0107_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 687 of 767 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (4)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Sweden  —  Peace  |  -57 (Hostile)]  [Naples  —  Peace  |  -27 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1828 of 1828 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (53 labels)
```

```
#0108  click Sweden  ->  ok
  (clicked at (1825, 587))
view: <run>\frames\0108_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 24 px, 0 of 525 px] ──
   THE CABINET — Sweden
   DP: 6
   TALLEYRAND'S ASSESSMENT — SWEDEN / Status: Peace   Relation: -57 (Hostile) /  / "Relations with Sweden remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase.
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1368g) (1 DP + 1368g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1828 of 1828 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (53 labels)
```

```
#0109  click Buy Off Their Design  ->  ok
  (clicked at (1825, 551))
view: <run>\frames\0109_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 81 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Murat seeks an audience @(3189,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]  [icon: Treaty with Hesse @(3569,64)]  [icon: Treaty with Papal States @(3611,64)]  [icon: Treaty with Austria @(3645,64)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1938 of 1938 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,385 (+1,182 next turn)
   Inf:
   86,750
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► buy off Sweden
   Sweden's design — Scourge of the Usurper — is bought off for 1368 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (53 labels)
```

```
#0110  look  ->  ok
  (a fresh frame)
view: <run>\frames\0110_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1938 of 1938 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   ► buy off Sweden
   Sweden's design — Scourge of the Usurper — is bought off for 1368 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (53 labels)
```

```
#0111  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0111_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 157 px] ──
   ENEMY PHASE - Turn 4
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Deroy /     Third Battle of Swabia /     Archduke Charles: 235 casualties, 29,292 remaining /     Deroy: 4,525 casualties, 3,444 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) — and advances into Swabia /     Swabia CAPTURED! (was Bavaria) (secured) /     Deroy forced to retreat! /     ⚔ View the f …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1873 of 1875 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,646 (+1,221 next turn)
   Inf:
   88,750
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Massena — Milan — 29,621 — Hunted by Archduke Charles on consecutive turns — holds Milan with 29,621 men.
   - Davout — Rhineland — 23,516 — Awaiting orders.
   - Ney — Swabia — 20,695 — Awaiting orders.
   - Murat — Rhineland — 20,586 — Awaiting orders.
   > Bernadotte — Franconia — 16,789 — Moving to Franche-Comte — 2 turns out. Trust:40
   - Lannes — Rhineland — 15,684 — Awaiting orders.
   - Napoleon — Rhineland — 8,865 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Swabia — 7,969 [confirmed]
   Archduke Charles — Franconia — 29,527 [confirmed]
   Archduke John — Tyrol — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   TURN EVENTS
   Supply cost you 2,533 men, at Franconia and Rhineland.
   Switzerland loyalty 96 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Massena appears envious of Ney's laurels — he has grown restless for glory.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   Franconia passes from Bavaria to Austria.
   Bernadotte stands on Franconia, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   War exhaustion grows — Austria nears breaking point (exhaustion: 60).
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -69.
   Teulie's contingent comes home — 5,844 of 7,500 men.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non-Aggression Pact
   - Papal States — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Franconia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War for Franconia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War for Franconia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 81/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   ► buy off Sweden
   Sweden's design — Scourge of the Usurper — is bought off for 1368 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► end turn
   ═══════════════════════════════════════
   TURN 5 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -320g | Other: +1289g | Upkeep: -2208g | Net: +1261g | Spent: 1368g
   Treasury: 2,646g
   Actions refreshed: 4/4
   Supply shortage at Swabia: Ney loses 741 troops — 128 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Bernadotte loses 595 troops — 102 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Archduke Charles loses 610 troops
   Supply shortage at Rhineland: Davout loses 756 troops
   Supply shortage at Rhineland: Lannes loses 504 troops
   Supply shortage at Rhineland: Murat loses 662 troops
   Supply shortage at Rhineland: Napoleon loses 285 troops
   Garrison at Munich reinforced: 0 -> 2,000
   Switzerland loyalty 94 (-2): satellite drift
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Ney is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
   Bernadotte is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Bernadotte(1859,438)  Archduke Charles(1875,376)  Davout +3(1832,350)  Soult(1753,436)  Archduke John(1901,535)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,322)  Massena(1910,589)  ?(2068,435)  ?(1976,376)  2k(1901,617)  ?(1932,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0112  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0112_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   AUSTRIA LOSSES
   BAVARIA LOSSES
   0
   0
   ⚔
   Archduke Charles ◆
   Deroy ◆
   29,527 → 29,292 → 28,455 after the advance
   7,969 → 3,444
   THIRD BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 4
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria Eliminated! @(3189,64)]  [icon: Marshal Murat seeks an audience @(3231,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]  [icon: The Moniteur is out @(3611,64)]  [icon: Treaty with Hesse @(3645,64)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   War with the Third Coalition
   -2 →
   T:4
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 3t]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1983 of 1983 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,646 (+1,221 next turn)
   Inf:
   88,750
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Supply shortage at Swabia: Archduke Charles loses 610 troops
   Supply shortage at Rhineland: Davout loses 756 troops
   Supply shortage at Rhineland: Lannes loses 504 troops
   Supply shortage at Rhineland: Murat loses 662 troops
   Supply shortage at Rhineland: Napoleon loses 285 troops
   Garrison at Munich reinforced: 0 -> 2,000
   Switzerland loyalty 94 (-2): satellite drift
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Ney is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
   Bernadotte is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte marches to Swabia. 1 region to Rhineland.
   Swabia feeds 32,000; the 65,772 men standing there would lose ~1,336 a turn to short supply.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 5
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Davout, Lannes, Murat and Napoleon stand 66,444 men at Rhineland, which feeds 60,000. 6,444 too many. 4,529 men lost in 2 turns. A supply depot at Rhineland would ease it; Frankfurt can feed 50,000 more and Lorraine can feed 30,000 more — a corps marched there ends it.
   • Sire — the war with Hesse and Papal States is over. 1 corps stands on the wrong side of the new frontier. Berthier has given them the road home — Bernadotte to Rhineland. They have safe passage for 5 turns while they march. Bernadotte holds under your own orders and was not moved — the treaty offers a road, it does not overrule the Emperor. Their passage lapses with the corridor.
   • Sire — under the truce with Austria. Ney is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 turns of safe passage.
   • Sire — St Petersburg now pays London 300 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 2,646g (+1,261 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Massena — Milan — 29,621 — Hunted by Archduke Charles on consecutive turns — holds Milan with 29,621 men.
   - Davout — Rhineland — 22,760 — Awaiting orders.
   ⚠ Starving — supply has failed at Rhineland two turns running.
   > Ney — Swabia — 19,954 — Moving to Franche-Comte — arrives next turn.
   - Murat — Rhineland — 19,924 — Awaiting orders.
   ⚠ Starving — supply has failed at Rhineland two turns running.
   > Bernadotte — Swabia — 16,027 — Moving to Franche-Comte — arrives next turn. Trust:40
   - Lannes — Rhineland — 15,180 — Awaiting orders.
   ⚠ Starving — supply has failed at Rhineland two turns running.
   - Napoleon — Rhineland — 8,580 — Awaiting orders.
   ⚠ Starving — supply has failed at Rhineland two turns running.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 27,845 [confirmed]
   Archduke John — Munich — 16,147 [confirmed]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 3,543 men, at Swabia and Rhineland.
   Switzerland loyalty 94 (-2): satellite drift
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Swabia passes from Bavaria to Austria.
   Ney stands on Swabia, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   Munich passes from Bavaria to Austria.
   Sire — Bavaria has been eliminated from the war.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -58.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the war come, having been asked.
   Relations with Austria have improved significantly (+11 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 80/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0113  click Dispatch  ->  ERROR: no visible control's text holds "Dispatch"
view: <run>\frames\0113_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   AUSTRIA LOSSES
   BAVARIA LOSSES
   180
   3,483
   ⚔
   Archduke Charles ◆
   Deroy ◆
   29,527 → 29,292 → 28,455 after the advance
   7,969 → 3,444
   ROUTED
   THIRD BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 4
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1983 of 1983 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0114  look  ->  ok
  (a fresh frame)
view: <run>\frames\0114_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   AN INDECISIVE ACTION
   AUSTRIA LOSSES
   BAVARIA LOSSES
   235
   4,525
   Swabia changes hands.
   ⚔
   Archduke Charles ◆
   Deroy ◆
   29,527 → 29,292 → 28,455 after the advance
   7,969 → 3,444
   ROUTED
   Berthier: “Deroy's army has been badly mauled. Archduke Charles proved the stronger force today. And Deroy was taken on that field — Austria holds him.”
   THIRD BATTLE OF SWABIA
   SWABIA · TURN 4
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1983 of 1983 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0115  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0115_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1983 of 1983 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,646 (+1,221 next turn)
   Inf:
   88,750
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0116  click Dispatch  ->  ok
  (clicked at (425, 18))
view: <run>\frames\0116_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1587 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 5 — Late November 1805 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Davout, Lannes, Murat and Napoleon stand 66,444 men at Rhineland, which feeds 60,000. 6,444 too many. 4,529 men lost in 2 turns. A su …
   controls: [Pin]  [icon @(2143,296)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1983 of 1983 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0117  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0117_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -2 →
   T:4
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 3t]
── BottomLeftUI (layer 0) [scrolled 1983 of 1983 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0118  type Davout, move to Frankfurt  ->  ok
  (typed and Enter)
view: <run>\frames\0118_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Rhineland to Frankfurt (353 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2092 of 2092 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   2,646 (+979 next turn)
   Inf:
   88,750
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Frankfurt
   → Davout moves from Rhineland to Frankfurt (353 lost to march)
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Bernadotte(1859,438)  Archduke Charles(1875,376)  Lannes(1829,402)  Murat(1827,350)  Napoleon(1838,324)  Soult(1753,436)  Archduke John(1901,535)  Davout(1893,352)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1741,324)  Massena(1910,589)  ?(2068,435)  ?(1976,376)  2k(1901,617)  10k(1934,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0119  type Murat, move to Frankfurt  ->  ok
  (typed and Enter)
view: <run>\frames\0119_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves from Rhineland to Frankfurt (199 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2203 of 2203 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   2,646 (+751 next turn)
   Inf:
   88,750
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, move to Frankfurt
   → Murat moves from Rhineland to Frankfurt (199 lost to march)
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Bernadotte(1859,438)  Archduke Charles(1875,376)  Lannes(1829,402)  Napoleon(1838,350)  Soult(1753,436)  Archduke John(1901,535)  Davout(1881,324)  Murat(1912,350)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,324)  Massena(1910,589)  ?(2068,435)  ?(1976,376)  2k(1901,617)  10k(1934,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0120  type Lannes, move to Lorraine  ->  ok
  (typed and Enter)
view: <run>\frames\0120_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes moves from Rhineland to Lorraine
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2314 of 2314 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   2,646 (+751 next turn)
   Inf:
   88,750
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, move to Lorraine
   → Lannes moves from Rhineland to Lorraine
   [1/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Bernadotte(1859,438)  Archduke Charles(1875,376)  Napoleon(1830,350)  Soult(1741,436)  Lannes(1764,462)  Archduke John(1901,535)  Davout(1881,324)  Murat(1905,350)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,324)  Massena(1910,589)  ?(2068,435)  ?(1976,376)  2k(1901,617)  10k(1934,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,648)
```

```
#0121  type Napoleon, move to Lorraine  ->  ok
  (typed and Enter)
view: <run>\frames\0121_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Rhineland to Lorraine
Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1741 of 1742 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   2,646 (+751 next turn)
   Inf:
   88,750
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   SITUATION
   France holds 28 regions. Treasury: 2,646g (+1,261 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Massena — Milan — 29,621 — Hunted by Archduke Charles on consecutive turns — holds Milan with 29,621 men.
   - Davout — Rhineland — 22,760 — Awaiting orders.
   ⚠ Starving — supply has failed at Rhineland two turns running.
   > Ney — Swabia — 19,954 — Moving to Franche-Comte — arrives next turn.
   - Murat — Rhineland — 19,924 — Awaiting orders.
   ⚠ Starving — supply has failed at Rhineland two turns running.
   > Bernadotte — Swabia — 16,027 — Moving to Franche-Comte — arrives next turn. Trust:40
   - Lannes — Rhineland — 15,180 — Awaiting orders.
   ⚠ Starving — supply has failed at Rhineland two turns running.
   - Napoleon — Rhineland — 8,580 — Awaiting orders.
   ⚠ Starving — supply has failed at Rhineland two turns running.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 27,845 [confirmed]
   Archduke John — Munich — 16,147 [confirmed]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 3,543 men, at Swabia and Rhineland.
   Switzerland loyalty 94 (-2): satellite drift
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Swabia passes from Bavaria to Austria.
   Ney stands on Swabia, now Austria's soil — an armistice stands between us: he may march out, but no corps of ours may enter it again.
   Munich passes from Bavaria to Austria.
   Sire — Bavaria has been eliminated from the war.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -58.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the war come, having been asked.
   Relations with Austria have improved significantly (+11 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-1)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 80/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
   ► Davout, move to Frankfurt
   → Davout moves from Rhineland to Frankfurt (353 lost to march)
   [3/4 actions remaining]
   ► Murat, move to Frankfurt
   → Murat moves from Rhineland to Frankfurt (199 lost to march)
   [2/4 actions remaining]
   ► Lannes, move to Lorraine
   → Lannes moves from Rhineland to Lorraine
   [1/4 actions remaining]
   ► Napoleon, move to Lorraine
   → Napoleon moves from Rhineland to Lorraine
   Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  32(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Ney(1847,464)  Bernadotte(1859,438)  Archduke Charles(1875,376)  Soult(1741,436)  Lannes(1752,462)  Napoleon(1830,350)  Archduke John(1901,535)  Davout(1881,324)  Murat(1905,350)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,324)  Massena(1910,589)  ?(2068,435)  ?(1976,376)  2k(1901,617)  10k(1934,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,648)
```

```
#0122  look  ->  ok
  (a fresh frame)
view: <run>\frames\0122_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1741 of 1742 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Napoleon, move to Lorraine
   → Napoleon moves from Rhineland to Lorraine
   Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
map: unchanged (53 labels)
```

```
#0123  click_at 3441 64  ->  ok
  (clicked at (3441, 64) on @Button@3488 'Talleyrand at Austria — Improving Relati' (Button, layer 75))
view: <run>\frames\0123_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   Imperial Box
   Talleyrand: Improving Relations - Austria
   Relations with Austria -58, net +11 a turn. ≈25 turns to +100 at the present rate. 1 DP a turn.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria Eliminated! @(3189,64)]  [icon: Marshal Murat seeks an audience @(3231,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]  [icon: The Moniteur is out @(3611,64)]  [icon: Treaty with Hesse @(3645,64)]  [Recall Talleyrand]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1741 of 1742 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Napoleon, move to Lorraine
   → Napoleon moves from Rhineland to Lorraine
   Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
map: unchanged (53 labels)
```

```
#0124  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0124_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px] ──
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1742 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, move to Lorraine
   → Napoleon moves from Rhineland to Lorraine
   Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
map: unchanged (53 labels)
```

```
#0125  look  ->  ok
  (a fresh frame)
view: <run>\frames\0125_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1742 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, move to Lorraine
   → Napoleon moves from Rhineland to Lorraine
   Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
map: unchanged (53 labels)
```

```
#0126  scroll 1800 560 down 6  ->  ok
  (scrolled down 6 at (1800, 560))
view: <run>\frames\0126_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 227 of 712 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -58 (Hostile)  [MISSION]]  [Prussia  —  Open Borders  |  -2 (Wary)]  [Spain  —  Alliance  |  +36 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -16 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1742 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, move to Lorraine
   → Napoleon moves from Rhineland to Lorraine
   Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
map: unchanged (53 labels)
```

```
#0127  click Prussia  ->  ok
  (clicked at (1825, 522))
view: <run>\frames\0127_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 244 px, 0 of 622 px] ──
   THE CABINET — Prussia
   DP: 6
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Open Borders   Relation: -2 (Wary) /  / "Our borders with Prussia are open, but trust remains shallow. A non-aggression pact would formalize the thaw." / Recommendation: Relations must improve before proposals will find purchase. / Talleyrand: "Prussia stands on the Emperor's roads, Sire — The Protector of the Rhine (A German Crown Brought to Terms). Pro …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [↳ 400g a turn]  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1742 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Napoleon, move to Lorraine
   → Napoleon moves from Rhineland to Lorraine
   Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
map: unchanged (53 labels)
```

```
#0128  click Licence  ->  ok
  (clicked at (1825, 510))
view: <run>\frames\0128_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 80 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria Eliminated! @(3189,64)]  [icon: Marshal Murat seeks an audience @(3231,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]  [icon: The Moniteur is out @(3611,64)]  [icon: Treaty with Hesse @(3645,64)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1853 of 1853 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   2,646 (+751 next turn)
   Inf:
   88,750
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► sponsor Prussia against Hanover, 0 gold
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (53 labels)
```

```
#0129  look  ->  ok
  (a fresh frame)
view: <run>\frames\0129_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1853 of 1853 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
   ► sponsor Prussia against Hanover, 0 gold
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (53 labels)
```

```
#0130  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0130_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 5
   AUSTRIA / ──────────────────────────── / - Archduke Charles abandons fortified position / - Archduke Charles detaches a garrison /  / ──────────────────────────── / Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 79 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2229 of 2229 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,860 (+1,132 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -40g | Admiralty: -90g | Blockade: -320g | Other: +1294g | Upkeep: -2220g | Net: +1214g
   Treasury: 3,860g
   Actions refreshed: 4/4
   Crowded at Lorraine: Soult loses 600 troops to the press of 3 corps on one province's roads
   Crowded at Lorraine: Lannes loses 303 troops to the press of 3 corps on one province's roads
   Crowded at Lorraine: Napoleon loses 171 troops to the press of 3 corps on one province's roads
   Garrison at Munich reinforced: 2,000 -> 4,000
   Switzerland loyalty 92 (-2): satellite drift
   Britain subsidizes Austria with 300 gold.
   Massena's resentment of Ney has cooled with time.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Soult(1741,436)  Lannes(1746,462)  Napoleon(1809,418)  Ney(1800,497)  Bernadotte(1825,521)  Archduke John(1901,547)  Davout(1881,352)  Murat(1905,326)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,322)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  3k(1899,519)  4k(1901,617)  10k(1893,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,648)
```

```
#0131  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0131_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 79 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3351,64)]  [icon: Envoy from Prussia @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Ney arrived @(3477,64)]  [icon: Bavaria Eliminated! @(3519,64)]  [icon: Marshal Murat seeks an audience @(3561,64)]  [+13]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 2119 of 2119 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,860 (+1,132 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► Napoleon, move to Lorraine
   → Napoleon moves from Rhineland to Lorraine
   Lorraine feeds 60,000; the 53,760 men standing there would lose ~1,074 a turn to crowding — too many corps on one province.
   [0/4 actions remaining]
   ► sponsor Prussia against Hanover, 0 gold
   The licence is granted: France blesses Prussia's design against Hanover and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► end turn
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -40g | Admiralty: -90g | Blockade: -320g | Other: +1294g | Upkeep: -2220g | Net: +1214g
   Treasury: 3,860g
   Actions refreshed: 4/4
   Crowded at Lorraine: Soult loses 600 troops to the press of 3 corps on one province's roads
   Crowded at Lorraine: Lannes loses 303 troops to the press of 3 corps on one province's roads
   Crowded at Lorraine: Napoleon loses 171 troops to the press of 3 corps on one province's roads
   Garrison at Munich reinforced: 2,000 -> 4,000
   Switzerland loyalty 92 (-2): satellite drift
   Britain subsidizes Austria with 300 gold.
   Massena's resentment of Ney has cooled with time.
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte arrives at Franche-Comte. Bernadotte: "It is done. I took the liberty of posting pickets."
   Ney: Ney arrives at Franche-Comte. Ney: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
   SITUATION
   France holds 28 regions. Treasury: 3,860g (+1,214 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — Hunted by Archduke Charles on consecutive turns — holds Milan with 29,621 men.
   - Soult — Lorraine — 29,400 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — Awaiting orders.
   - Murat — Frankfurt — 19,725 — Awaiting orders.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Lorraine — 14,877 — Awaiting orders.
   - Napoleon — Lorraine — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 24,845 [confirmed]
   Archduke John — Munich — 16,147 [confirmed]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 1,074 men, at Lorraine.
   Switzerland loyalty 92 (-2): satellite drift
   Massena's resentment of Ney has cooled with time.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -47.
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Non-Aggression Pact
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 79/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0132  click Envoys  ->  ok
  (clicked at (3377, 18))
view: <run>\frames\0132_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Open ▸
   Turn 5
   Incoming proposal: Non-Aggression Pact
   WAITING
   Switzerland
   Proposal
   Open ▸
   Turn 6
   Incoming proposal: Client's Petition
   controls: {ACTIVE}  {WAITING}  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2119 of 2119 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 79/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0133  click_at 1828 283  ->  ok
  (clicked at (1828, 283) on @PanelContainer@3725 'ACTIVE' (PanelContainer, layer 119))
view: <run>\frames\0133_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Non-Aggression Pact / Terms: /   - Proposal: Non-Aggression Pact /   - Offer: Gold payment - 150 /  / Hardenberg, stiffly: "Berlin will not pretend otherwise: France stands too near the Rhine. Prussia would fix that line in ink before she fixes it in blood. Sign the pact of non-aggression." /  / An interesting proposal. I shall study t …
   controls: [Accept]  [Let Talleyrand haggle (1 DP)]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2119 of 2119 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   3,860 (+1,132 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 79/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0134  click Accept  ->  ok
  (clicked at (1574, 687))
view: <run>\frames\0134_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +8 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a  …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 79 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2185 of 2185 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,010 (+1,127 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
map: unchanged (54 labels)
```

```
#0135  look  ->  ok
  (a fresh frame)
view: <run>\frames\0135_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2185 of 2185 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
map: unchanged (54 labels)
```

```
#0136  look  ->  ok
  (a fresh frame)
view: <run>\frames\0136_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2185 of 2185 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
map: unchanged (54 labels)
```

```
#0137  click Refuse  ->  ok
  (clicked at (1829, 687))
view: <run>\frames\0137_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 79 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte arrived @(3185,64)]  [icon: Ney arrived @(3227,64)]  [icon: Bavaria Eliminated! @(3269,64)]  [icon: Marshal Murat seeks an audience @(3311,64)]  [Talleyrand at Austria — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 1652 of 1653 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,010 (+1,127 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte arrives at Franche-Comte. Bernadotte: "It is done. I took the liberty of posting pickets."
   Ney: Ney arrives at Franche-Comte. Ney: "It is done. Point me at something that shoots back, Sire."
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
   SITUATION
   France holds 28 regions. Treasury: 3,860g (+1,214 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — Hunted by Archduke Charles on consecutive turns — holds Milan with 29,621 men.
   - Soult — Lorraine — 29,400 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — Awaiting orders.
   - Murat — Frankfurt — 19,725 — Awaiting orders.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Lorraine — 14,877 — Awaiting orders.
   - Napoleon — Lorraine — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 24,845 [confirmed]
   Archduke John — Munich — 16,147 [confirmed]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 1,074 men, at Lorraine.
   Switzerland loyalty 92 (-2): satellite drift
   Massena's resentment of Ney has cooled with time.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -47.
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Non-Aggression Pact
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 79/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (54 labels)
```

```
#0138  click Dispatch  ->  ok
  (clicked at (425, 18))
view: <run>\frames\0138_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1389 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 6 — Early December 1805 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Prussia moves toward war with Hanover. The design is open; the timing is not. /  / SITUATION /   France holds 28 regions. Treasury:  …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (2)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1653 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (54 labels)
```

```
#0139  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0139_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 1652 of 1653 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (54 labels)
```

```
#0140  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0140_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1653 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (54 labels)
```

```
#0141  scroll 1800 560 down 6  ->  ok
  (scrolled down 6 at (1800, 560))
view: <run>\frames\0141_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 227 of 712 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -47 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +35 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -15 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1653 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (54 labels)
```

```
#0142  click Austria  ->  ok
  (clicked at (1825, 482))
view: <run>\frames\0142_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 381 px] ──
   THE CABINET — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Armistice — the War with the Third Coalition   Relation: -47 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Austria, though they will demand terms." / Recommendation: Sire, the truce with Austria has 2 turns to run and the ledger stands: the war score reads +38 for France (2 battles, 2 decisives kept); the war is …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile (+33 over 3 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1653 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (54 labels)
```

```
#0143  click Cancel: Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0143_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 79 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte arrived @(3351,64)]  [icon: Ney arrived @(3393,64)]  [icon: Bavaria Eliminated! @(3435,64)]  [icon: Marshal Murat seeks an audience @(3477,64)]  [icon: The Marshalate awaits @(3519,64)]  [icon: Treaty with Prussia @(3561,64)]  [+12]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1741 of 1741 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,010 (+1,127 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (54 labels)
```

```
#0144  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0144_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1741 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (54 labels)
```

```
#0145  scroll 1800 560 down 6  ->  ok
  (scrolled down 6 at (1800, 560))
view: <run>\frames\0145_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 227 of 712 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -47 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +35 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -15 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1741 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (54 labels)
```

```
#0146  click Prussia  ->  ok
  (clicked at (1825, 522))
view: <run>\frames\0146_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 266 px, 0 of 511 px] ──
   THE CABINET — Prussia
   DP: 6
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Non-Aggression   Relation: +3 (Neutral) /  / "We have Prussia's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Prussia stands on the Emperor's roads, Sire …
   The compact already stands.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends](disabled: The compact already stands.)  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1741 of 1741 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (54 labels)
```

```
#0147  click Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0147_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Prussia /  / "Sire, I shall begin efforts to improve relations with Prussia. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 79 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1786 of 1786 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,010 (+1,127 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► improve relations with Prussia
map: unchanged (54 labels)
```

```
#0148  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0148_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 79 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte arrived @(3351,64)]  [icon: Ney arrived @(3393,64)]  [icon: Bavaria Eliminated! @(3435,64)]  [icon: Marshal Murat seeks an audience @(3477,64)]  [icon: The Marshalate awaits @(3519,64)]  [icon: Treaty with Prussia @(3561,64)]  [+12]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -2 →
   T:5
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War with Austria — Austria, truce 2t]
── BottomLeftUI (layer 0) [scrolled 1851 of 1851 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,010 (+1,127 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (54 labels)
```

```
#0149  look  ->  ok
  (a fresh frame)
view: <run>\frames\0149_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1851 of 1851 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Talleyrand's mission to Austria has been cancelled.
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
map: unchanged (54 labels)
```

```
#0150  type Lannes, move to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0150_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes moves from Lorraine to Rhineland
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1962 of 1962 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,010 (+1,127 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, move to Rhineland
   → Lannes moves from Lorraine to Rhineland
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Lannes(1829,397)  Soult(1741,436)  Napoleon(1809,423)  Ney(1800,497)  Bernadotte(1825,521)  Archduke John(1901,547)  Davout(1881,352)  Murat(1905,326)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,322)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  3k(1899,519)  4k(1901,617)  10k(1893,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,648)
```

```
#0151  type Napoleon, move to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0151_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Lorraine to Rhineland
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2073 of 2073 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,010 (+1,127 next turn)
   Inf:
   90,650
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, move to Rhineland
   → Napoleon moves from Lorraine to Rhineland
   [2/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Lannes(1814,418)  Napoleon(1838,376)  Soult(1753,436)  Ney(1800,497)  Bernadotte(1825,521)  Archduke John(1901,547)  Davout(1881,352)  Murat(1905,326)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,322)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  3k(1899,519)  4k(1901,617)  10k(1893,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,648)
```

```
#0152  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0152_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 6
   AUSTRIA / ──────────────────────────── / - Archduke Charles holds position /  / ──────────────────────────── / Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 78 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2008 of 2010 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Napoleon — Lorraine — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 24,845 [confirmed]
   Archduke John — Munich — 16,147 [confirmed]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 1,074 men, at Lorraine.
   Switzerland loyalty 92 (-2): satellite drift
   Massena's resentment of Ney has cooled with time.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -47.
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   Relations with Austria have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Non-Aggression Pact
   - Switzerland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 79/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
   Responding to Switzerland's proposal: declined
   Switzerland's petition for relief is refused: loyalty −10 (92 → 82); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
   ► improve relations with Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Prussia. (1 DP/turn)
   ► Lannes, move to Rhineland
   → Lannes moves from Lorraine to Rhineland
   [3/4 actions remaining]
   ► Napoleon, move to Rhineland
   → Napoleon moves from Lorraine to Rhineland
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 7 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Contributions: -110g | Charges of Empire: -192g | Admiralty: -90g | Blockade: -328g | Other: +1310g | Upkeep: -2220g | Net: +960g
   Treasury: 4,970g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 4,000 -> 6,000
   Switzerland loyalty 79 (-3): satellite drift, relations with the lord
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: OPEN_BORDERS → PEACE.
   Prussia declares war on Hanover — The Hanoverian Prize; declaring Hanover.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Massena resents Ney's laurels again, 3 turns after the last — he has grown loud at the staff table about who is given the honours.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Bernadotte's resentment of Ney has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Lannes(1814,418)  Napoleon(1838,376)  ?(1501,602)  Paget(1501,564)  Soult(1753,436)  Ney(1800,497)  Bernadotte(1825,521)  ?(1901,540)  Archduke John(1901,496)  Davout(1881,352)  Murat(1905,326)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,322)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  3k(1859,549)  ?(1937,560)  10k(1893,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1705,420)  10k(1910,645)
```

```
#0153  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0153_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 78 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3186,64)]  [icon: Marshal Massena seeks an audience @(3228,64)]  [icon: Bernadotte arrived @(3270,64)]  [icon: Ney arrived @(3312,64)]  [icon: Bavaria Eliminated! @(3354,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Leon
   -3 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Leon]  [War for Leon — Austria, truce 1t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1808 of 1808 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ═══════════════════════════════════════
   TURN 7 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Contributions: -110g | Charges of Empire: -192g | Admiralty: -90g | Blockade: -328g | Other: +1310g | Upkeep: -2220g | Net: +960g
   Treasury: 4,970g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 4,000 -> 6,000
   Switzerland loyalty 79 (-3): satellite drift, relations with the lord
   Britain subsidizes Austria with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: OPEN_BORDERS → PEACE.
   Prussia declares war on Hanover — The Hanoverian Prize; declaring Hanover.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Massena resents Ney's laurels again, 3 turns after the last — he has grown loud at the staff table about who is given the honours.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Bernadotte's resentment of Ney has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 7
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Paget has crossed into Gascony. No French corps stands in his path.
   • Sire — Leon has been taken by Britain.
   • Sire — St Petersburg now pays Vienna 200 gold a turn against us. The coalition has its paymaster; it lacks only its armies.
   SITUATION
   France holds 28 regions. Treasury: 4,970g (+960 by the accounts)
   The courts at war hold 22 regions. Estimated enemy strength: 1% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 5 turns idle.
   - Soult — Lorraine — 29,400 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — Awaiting orders.
   - Murat — Frankfurt — 19,725 — Awaiting orders.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — Awaiting orders.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 24,845 [confirmed]
   Archduke John — Munich — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   Paget — Gascony — screening force [partial]
   TURN EVENTS
   Switzerland loyalty 79 (-3): satellite drift, relations with the lord
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Massena resents Ney's laurels again, 3 turns after the last — he has grown loud at the staff table about who is given the honours.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Bernadotte's resentment of Ney has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Non-Aggression Pact.
   Leon passes from Spain to Britain.
   Intelligence reports Britain has raised Wellesley to high command.
   Intelligence reports Spain has raised Cuesta to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 10.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   Prussia has declared war on Hanover.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Leon) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Leon) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War for Leon) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0154  click Dispatch  ->  ok
  (clicked at (425, 18))
view: <run>\frames\0154_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1279 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 7 — Late December 1805 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Paget has crossed into Gascony. No French corps stands in his path. /   • Sire — Leon has been taken by Britain. /   • Sire — St Pete …
   controls: [Pin]  [icon @(2143,296)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1808 of 1808 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0155  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0155_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Leon
   -3 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Leon]  [War for Leon — Austria, truce 1t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1808 of 1808 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0156  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0156_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1808 of 1808 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0157  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0157_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (2)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -44 (Hostile)]  [Prussia  —  Non-Aggression  |  -5 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +34 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1808 of 1808 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0158  click Britain  ->  ok
  (clicked at (1825, 442))
view: <run>\frames\0158_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 313 px] ──
   THE CABINET — Britain
   DP: 6
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War for Leon   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Permit me to observe, Sire, that a level war is the dearest kind to end: Propose Peace reads 17 of 50; it wants deep-seated hostility (-10). A payment of 975 gold to B …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Uncertain — a counter is likely]  [Open Settlement — the whole table: Britain and Russia]  [Propose White Peace — the whole table: Britain and Russia]  [Propose Peace (3 DP)  —  Unlikely]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1808 of 1808 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0159  click Propose Peace  ->  ok
  (clicked at (1825, 588))
view: <run>\frames\0159_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 376 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 17 - REJECT / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / The War for Leon: Britain holds Leon of ours. / War score: -3 -> / Settlement: White Peace / Objective: Defense - the homeland — …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 78 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1853 of 1853 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose peace with Britain
map: unchanged (57 labels)
```

```
#0160  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0160_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 398 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / France concedes: /   • France pays 497 gold per turn to Britain for as long as the treaty stands / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 32 - COUNTER expected / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / The War for Leon: B …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1874 of 1874 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (57 labels)
```

```
#0161  click Less generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0161_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 376 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 17 - REJECT / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / The War for Leon: Britain holds Leon of ours. / War score: -3 -> / Settlement: White Peace / Objective: Defense - the homeland — …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1896 of 1896 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: less generous
map: unchanged (57 labels)
```

```
#0162  click Adjust terms  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0162_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Britain /  /  / "Shall we discuss concessions, Sire?"
   controls: [Yes, discuss territory]  [No territory — offer gold]  [Offer Action Points]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1918 of 1918 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: adjust terms
map: unchanged (57 labels)
```

```
#0163  click No territory  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0163_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Britain /  /  / "I suggest offering 90 gold per turn."
   controls: [Offer 90 gold]  [Offer more]  [Offer less]  [Skip gold]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1941 of 1941 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: territory no gold
map: unchanged (57 labels)
```

```
#0164  click Offer 90 gold  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0164_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Britain /  /  / "Offering an Action Point is extraordinary — an entire extra action each turn. Worth 18 acceptance points, more than ceding a province."
   controls: [Offer the AP]  [Too costly]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1963 of 1963 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: offer gold
map: unchanged (57 labels)
```

```
#0165  click Too costly  ->  ok
  (clicked at (1834, 727))
view: <run>\frames\0165_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 354 px] ──
   PEACE PREVIEW - Britain /  / Proposed Terms / France concedes: /   • France pays 90 gold per turn to Britain for as long as the treaty stands / Mutual: /   • Peace Treaty (end state of war) — France and Britain /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 19 - REJECT / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / The War for Leon: Britain hold …
   controls: [icon: Close (Esc) @(2151,292)]  [Send]  [Start over]  [Reconsider]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1985 of 1985 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: skip ap
map: unchanged (57 labels)
```

```
#0166  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0166_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 78 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3186,64)]  [icon: Marshal Massena seeks an audience @(3228,64)]  [icon: Bernadotte arrived @(3270,64)]  [icon: Ney arrived @(3312,64)]  [icon: Bavaria Eliminated! @(3354,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Leon
   -3 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Leon]  [War for Leon — Austria, truce 1t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2052 of 2052 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (57 labels)
```

```
#0167  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0167_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2052 of 2052 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: offer gold
   Directing Talleyrand: skip ap
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (57 labels)
```

```
#0168  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0168_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (2)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  Armistice  |  -44 (Hostile)]  [Prussia  —  Non-Aggression  |  -5 (Wary)  [MISSION]]  [Spain  —  Alliance  |  +34 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2052 of 2052 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: offer gold
   Directing Talleyrand: skip ap
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (57 labels)
```

```
#0169  click Britain  ->  ok
  (clicked at (1825, 442))
view: <run>\frames\0169_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 313 px] ──
   THE CABINET — Britain
   DP: 6
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: At War — the War for Leon   Relation: -90 (Hostile) /  / "The war with Britain grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: If I may, Sire — the court sees no reason to sign at -3: Propose Peace stands at 17 of 50; it wants deep-seated hostility (-10). A payment of 975 gold to Britain would …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Uncertain — a counter is likely]  [Open Settlement — the whole table: Britain and Russia]  [Propose White Peace — the whole table: Britain and Russia]  [Propose Peace (3 DP)  —  Unlikely]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2052 of 2052 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: offer gold
   Directing Talleyrand: skip ap
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (57 labels)
```

```
#0170  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0170_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 618 px] ──
   ARMISTICE PREVIEW - Britain /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Britain /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads -2 for France (0 battles, 0 decisives kept); the war is 6 turns old and stays so; exhaustion holds. No territory or gold changes hands until it end …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 78 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose armistice with Britain
map: unchanged (57 labels)
```

```
#0171  click Not Now  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0171_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 78 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Prussia Declares War! @(3186,64)]  [icon: Marshal Massena seeks an audience @(3228,64)]  [icon: Bernadotte arrived @(3270,64)]  [icon: Ney arrived @(3312,64)]  [icon: Bavaria Eliminated! @(3354,64)]  [Talleyrand at Prussia — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Leon
   -3 →
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War for Leon]  [War for Leon — Austria, truce 1t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2162 of 2162 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (57 labels)
```

```
#0172  type what if Soult attacks Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0172_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult stands at Lorraine, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1696 of 1696 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   • Sire — Leon has been taken by Britain.
   • Sire — St Petersburg now pays Vienna 200 gold a turn against us. The coalition has its paymaster; it lacks only its armies.
   SITUATION
   France holds 28 regions. Treasury: 4,970g (+960 by the accounts)
   The courts at war hold 22 regions. Estimated enemy strength: 1% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 5 turns idle.
   - Soult — Lorraine — 29,400 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — Awaiting orders.
   - Murat — Frankfurt — 19,725 — Awaiting orders.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — Awaiting orders.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — 24,845 [confirmed]
   Archduke John — Munich — substantial force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Normandy — small force [partial]
   Paget — Gascony — screening force [partial]
   TURN EVENTS
   Switzerland loyalty 79 (-3): satellite drift, relations with the lord
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Berthier reports that Massena resents Ney's laurels again, 3 turns after the last — he has grown loud at the staff table about who is given the honours.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Bernadotte's resentment of Ney has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Non-Aggression Pact.
   Leon passes from Spain to Britain.
   Intelligence reports Britain has raised Wellesley to high command.
   Intelligence reports Spain has raised Cuesta to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 10.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   Prussia has declared war on Hanover.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War for Leon) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-2)
   War Purpose: Defense vs Austria (War for Leon) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Favorable Terms (+38)
   War Purpose: Defense vs Russia (War for Leon) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► propose peace with Britain
   Directing Talleyrand: modify generous
   Directing Talleyrand: less generous
   Directing Talleyrand: adjust terms
   Directing Talleyrand: territory no gold
   Directing Talleyrand: offer gold
   Directing Talleyrand: skip ap
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► propose armistice with Britain
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► what if Soult attacks Paget
   Soult stands at Lorraine, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
map: unchanged (57 labels)
```

```
#0173  type Soult, pursue Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0173_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult pursues Paget (at Gascony). Moves to Orleanais. "Soult, pursue Paget." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1829 of 1829 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,970 (+859 next turn)
   Inf:
   92,450
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, pursue Paget
   Soult pursues Paget (at Gascony). Moves to Orleanais. "Soult, pursue Paget." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1258,796)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Britain(1385,353)  Papal States(1869,731)  Portugal(1216,764)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  33(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1959,325)  Brunswick(1958,287)  Archduke Charles(1859,464)  Lannes(1814,418)  Napoleon(1838,376)  ?(1501,602)  Paget(1501,564)  Ney(1800,497)  Bernadotte(1825,521)  ?(1901,540)  Archduke John(1901,496)  Soult(1695,440)  Davout(1881,352)  Murat(1905,326)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,322)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  3k(1859,549)  ?(1937,560)  10k(1893,434)  25k(1595,494)  12k(1551,454)  ?(1769,580)  10k(1755,420)  12k(1684,411)  10k(1910,645)
```

```
#0174  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0174_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 7
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 78 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2185 of 2185 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,827 (+770 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 8 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Contributions: -150g | Charges of Empire: -260g | Admiralty: -90g | Blockade: -328g | Other: +1315g | Upkeep: -2220g | Net: +857g
   Treasury: 5,827g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 6,000 -> 8,000
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Switzerland loyalty 76 (-3): satellite drift, relations with the lord
   The armistice between Austria and France has concluded. Peace declared — signed on the held line.
   Britain subsidizes Russia with 300 gold.
   Berthier: Enemy forces spotted near Paris! Paget (4,613 troops) at Berry.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2075,313)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Hanover(1710,338)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  34(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Paget(1525,465)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1831,316)  Brunswick(1830,278)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Soult(1695,440)  Davout(1881,352)  Murat(1905,326)  ?(1551,403)  Castanos(1551,364)  Dumonceau(1755,310)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,494)  12k(1551,436)  ?(1769,580)  7k(1777,336)  10k(1755,420)  12k(1684,411)  10k(1910,645)
```

```
#0175  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0175_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 78 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Marshal Massena seeks an audience @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+15]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -3 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1899 of 1899 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,827 (+770 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► what if Soult attacks Paget
   Soult stands at Lorraine, beyond reach of Paget at Gascony this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
   ► Soult, pursue Paget
   Soult pursues Paget (at Gascony). Moves to Orleanais. "Soult, pursue Paget." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 8 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Contributions: -150g | Charges of Empire: -260g | Admiralty: -90g | Blockade: -328g | Other: +1315g | Upkeep: -2220g | Net: +857g
   Treasury: 5,827g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 6,000 -> 8,000
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Switzerland loyalty 76 (-3): satellite drift, relations with the lord
   The armistice between Austria and France has concluded. Peace declared — signed on the held line.
   Britain subsidizes Russia with 300 gold.
   Berthier: Enemy forces spotted near Paris! Paget (4,613 troops) at Berry.
   --- Strategic Order Updates ---
   Soult: Soult is pursuing Paget.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 8
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Paget has crossed into Berry. No French corps stands in his path.
   • Sire — peace with Austria is signed. The truce has ripened into peace, signed on the held line.
   • THE SUN OF AUSTERLITZ — Talleyrand: "Austria has bent, Sire — now say what the Empire is for. The roads wait in the Cabinet (F1 → The Emperor's Designs)."
   SITUATION
   France holds 28 regions. Treasury: 5,827g (+857 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 1% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 6 turns idle.
   > Soult — Orleanais — 29,400 — Pursuing Paget. (to the letter)
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — Awaiting orders.
   - Murat — Frankfurt — 19,725 — Awaiting orders.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — Awaiting orders.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Brunswick — Brunswick — large force [partial]
   Castanos — Normandy — small force [partial]
   Paget — Berry — screening force [partial]
   TURN EVENTS
   Switzerland loyalty 76 (-3): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   Brunswick passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 3.
   The armistice between Austria and France has concluded. Peace declared.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0176  click Dispatch  ->  ok
  (clicked at (425, 18))
view: <run>\frames\0176_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1037 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 8 — Early January 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Paget has crossed into Berry. No French corps stands in his path. /   • Sire — peace with Austria is signed. The truce has ripened in …
   controls: [Pin]  [icon @(2143,296)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0177  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0177_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -3 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0178  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0178_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0179  click The Emperor's Designs  ->  ok
  (clicked at (1825, 502))
view: <run>\frames\0179_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 1943 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Your own aims, Sire, not the courts'. A road asks a construction, then a seal; hold both and the peace that seals it can be the Decisive Peace. Proclaiming costs 2 DP and 1 administrative action and cannot be undone.
   No road is proclaimed. Three roads — one proclamation, and it cannot be undone.
   Road I — The Protector of the Rhine (The Act of Confederation) /     • Bavaria must stand with France /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Austria −10, Prussia −10. /     • The Confederation of the Rhine (the construction) — 0 of 3 courts under the Emperor's protection; to be held 4 end turns /         Three of Bavaria, Hesse, Saxon …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Proclaim Road I — The Act of Confederation](disabled: The Protector of the Rhine: Bavaria must stand with France.)  [Proclaim Road II — The Schönbrunn Proclamation]  [Proclaim Road III — The Blockade of the British Isles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0180  scroll 1800 560 down 10  ->  ok
  (scrolled down 10 at (1800, 560))
view: <run>\frames\0180_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 379 of 1960 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Road I — The Protector of the Rhine (The Act of Confederation) /     • Bavaria must stand with France /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Austria −10, Prussia −10. /     • The Confederation of the Rhine (the construction) — 0 of 3 courts under the Emperor's protection; to be held 4 end turns /         Three of Bavaria, Hesse, Saxon …
   The Protector of the Rhine: Bavaria must stand with France.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [↳ Hesse]  [↳ Saxony]  [↳ Hanover]  [↳ Austria]  [↳ Prussia]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0181  scroll 1800 560 down 8  ->  ok
  (scrolled down 8 at (1800, 560))
view: <run>\frames\0181_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 662 of 1943 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Road II — The Crowns of Italy (The Schönbrunn Proclamation) /     ✓ the Kingdom of Italy must be France's /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Naples −10, Spain −10. /     • The Throne of Naples (the construction) — 0 of 1 province titled to the Empire /         Naples titled to the Empire — her court France's satellite at loyalty 4 …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0182  scroll 1800 560 down 10  ->  ok
  (scrolled down 10 at (1800, 560))
view: <run>\frames\0182_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 1042 of 1943 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 6
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Road III — The Continental System (The Blockade of the British Isles) /     ✓ France must be at war with the mistress of the seas /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Denmark −15, Portugal −15. /     • The Blockade of the British Isles (the construction) — 10 of 26 ports shut to Britain — 13 needed; to be held 6 end turns /          …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0183  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0183_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0184  scroll 1800 560 down 6  ->  ok
  (scrolled down 6 at (1800, 560))
view: <run>\frames\0184_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 227 of 712 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +33 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -13 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0185  scroll 1800 560 down 15  ->  ok
  (scrolled down 15 at (1800, 560))
view: <run>\frames\0185_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 671 of 711 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (5)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Austria  —  Peace  |  -41 (Hostile)]  [Sweden  —  Peace  |  -48 (Hostile)]  [Naples  —  Peace  |  -23 (Wary)]  [Hanover  —  Peace  |  -43 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0186  click Austria  ->  ok
  (clicked at (1825, 523))
view: <run>\frames\0186_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 90 px, 0 of 548 px] ──
   THE CABINET — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -41 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. / Talleyrand: "Austria stands on the Emperor's roads, Sire — The Protector of the Rhine (A German Crown Br …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1248g) (1 DP + 1248g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1899 of 1899 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (58 labels)
```

```
#0187  click Buy Off Their Design  ->  ok
  (clicked at (1825, 551))
view: <run>\frames\0187_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 78 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Marshal Massena seeks an audience @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+15]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2009 of 2009 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (58 labels)
```

```
#0188  look  ->  ok
  (a fresh frame)
view: <run>\frames\0188_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2009 of 2009 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (58 labels)
```

```
#0189  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0189_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2009 of 2009 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (58 labels)
```

```
#0190  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0190_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (2)
   Treaties (8)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +33 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -13 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2009 of 2009 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (58 labels)
```

```
#0191  click Russia  ->  ERROR: 2 controls match "Russia" — pick one with click#N
  candidates: #1 [Russia  —  At War  |  -80 (Hostile)] on DiplomacyWizard @(1825,482) | #2 [Prussia  —  Non-Aggression  |  +3 (Neutral)  [MISSION]] on DiplomacyWizard @(1825,545)
view: <run>\frames\0191_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2009 of 2009 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (58 labels)
```

```
#0192  look  ->  ok
  (a fresh frame)
view: <run>\frames\0192_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2009 of 2009 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (58 labels)
```

```
#0193  click#1 Russia  ->  ok
  (clicked at (1825, 482))
view: <run>\frames\0193_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 332 px, 0 of 313 px] ──
   THE CABINET — Russia
   DP: 5
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Russia grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Permit me to observe, Sire, that a level war is the dearest kind to end: Propose Peace reads 31 of 50; it wants deep-seated hostility (-10). A payment of …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Doubtful — may counter]  [Open Settlement — the whole table: Britain and Russia]  [Propose White Peace — the whole table: Britain and Russia]  [Propose Peace (3 DP)  —  Doubtful — may counter]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2009 of 2009 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (58 labels)
```

```
#0194  look  ->  ok
  (a fresh frame)
view: <run>\frames\0194_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 332 px, 0 of 313 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2009 of 2009 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (58 labels)
```

```
#0195  click Propose Peace  ->  ok
  (clicked at (1825, 588))
view: <run>\frames\0195_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 332 px] ──
   PEACE PREVIEW - Russia /  / Proposed Terms / Mutual: /   • Peace Treaty (end state of war) — France and Russia /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 31 - COUNTER expected / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / The War with the Third Coalition: nothing taken yet on either side. / War score: 0 -> / Settlement: White Peace / Object …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 78 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2055 of 2055 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose peace with Russia
map: unchanged (58 labels)
```

```
#0196  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0196_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 354 px] ──
   PEACE PREVIEW - Russia /  / Proposed Terms / France concedes: /   • France pays 457 gold per turn to Russia for as long as the treaty stands / Mutual: /   • Peace Treaty (end state of war) — France and Russia /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 45 - COUNTER expected / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / The War with the Third …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2076 of 2076 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (58 labels)
```

```
#0197  click Not Now  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0197_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 78 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Marshal Massena seeks an audience @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+15]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -3 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2143 of 2143 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (58 labels)
```

```
#0198  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0198_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 710 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (2)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2143 of 2143 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Russia
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (58 labels)
```

```
#0199  click#1 Russia  ->  ok
  (clicked at (1825, 644))
view: <run>\frames\0199_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 332 px, 0 of 313 px] ──
   THE CABINET — Russia
   DP: 5
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: At War — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The war with Russia grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Sire, the field reads +0 and no road carries. Propose Peace comes nearest at 31 of 50; deep-seated hostility is the weight (-10). A payment of 950 gold t …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Doubtful — may counter]  [Open Settlement — the whole table: Britain and Russia]  [Propose White Peace — the whole table: Britain and Russia]  [Propose Peace (3 DP)  —  Doubtful — may counter]  [Set War Purpose  —  name what the war is for, and up to 2 articles]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2143 of 2143 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose peace with Russia
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (58 labels)
```

```
#0200  click Propose Armistice  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0200_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 530 px] ──
   ARMISTICE PREVIEW - Russia /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Russia /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 7 turns old and stays so; exhaustion holds. No territory or gold changes hands until it ends.  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 78 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2188 of 2188 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose armistice with Russia
map: unchanged (58 labels)
```

```
#0201  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0201_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 552 px] ──
   ARMISTICE PREVIEW - Russia /  / Proposed Terms / France concedes: /   • France pays 457 gold per turn to Russia for as long as the treaty stands / Mutual: /   • Armistice (cease hostilities temporarily) — France and Russia /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2210 of 2210 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (58 labels)
```

```
#0202  click Less generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0202_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 530 px] ──
   ARMISTICE PREVIEW - Russia /  / Proposed Terms / Mutual: /   • Armistice (cease hostilities temporarily) — France and Russia /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 7 turns old and stays so; exhaustion holds. No territory or gold changes hands until it ends.  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2232 of 2232 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: less generous
map: unchanged (58 labels)
```

```
#0203  click Adjust terms  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0203_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Russia /  /  / "Shall we discuss concessions, Sire?"
   controls: [Yes, discuss territory]  [No territory — offer gold]  [Offer Action Points]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1677 of 1677 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier: Enemy forces spotted near Paris! Paget (4,613 troops) at Berry.
   --- Strategic Order Updates ---
   Soult: Soult is pursuing Paget.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 8
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Paget has crossed into Berry. No French corps stands in his path.
   • Sire — peace with Austria is signed. The truce has ripened into peace, signed on the held line.
   • THE SUN OF AUSTERLITZ — Talleyrand: "Austria has bent, Sire — now say what the Empire is for. The roads wait in the Cabinet (F1 → The Emperor's Designs)."
   SITUATION
   France holds 28 regions. Treasury: 5,827g (+857 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 1% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 6 turns idle.
   > Soult — Orleanais — 29,400 — Pursuing Paget. (to the letter)
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — Awaiting orders.
   - Murat — Frankfurt — 19,725 — Awaiting orders.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — Awaiting orders.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Brunswick — Brunswick — large force [partial]
   Castanos — Normandy — small force [partial]
   Paget — Berry — screening force [partial]
   TURN EVENTS
   Switzerland loyalty 76 (-3): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   Brunswick passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 3.
   The armistice between Austria and France has concluded. Peace declared.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► propose peace with Russia
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► propose armistice with Russia
   Directing Talleyrand: modify generous
   Directing Talleyrand: less generous
   Directing Talleyrand: adjust terms
map: unchanged (58 labels)
```

```
#0204  click No territory  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0204_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Russia /  /  / "I suggest offering 80 gold per turn."
   controls: [Offer 80 gold]  [Offer more]  [Offer less]  [Skip gold]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1699 of 1699 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: territory no gold
map: unchanged (58 labels)
```

```
#0205  click Offer more  ->  ok
  (clicked at (1829, 674))
view: <run>\frames\0205_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Russia /  /  / "I suggest offering 120 gold per turn."
   controls: [Offer 120 gold]  [Offer more]  [Offer less]  [Skip gold]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1721 of 1721 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: more gold
map: unchanged (58 labels)
```

```
#0206  click Offer more  ->  ok
  (clicked at (1829, 674))
view: <run>\frames\0206_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Russia /  /  / "I suggest offering 180 gold per turn."
   controls: [Offer 180 gold]  [Offer more]  [Offer less]  [Skip gold]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1743 of 1743 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: more gold
map: unchanged (58 labels)
```

```
#0207  click Offer more  ->  ok
  (clicked at (1829, 674))
view: <run>\frames\0207_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Russia /  /  / "I suggest offering 270 gold per turn."
   controls: [Offer 270 gold]  [Offer more]  [Offer less]  [Skip gold]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1766 of 1766 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: more gold
map: unchanged (58 labels)
```

```
#0208  click Offer more  ->  ok
  (clicked at (1829, 674))
view: <run>\frames\0208_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Russia /  /  / "I suggest offering 405 gold per turn."
   controls: [Offer 405 gold]  [Offer more]  [Offer less]  [Skip gold]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1788 of 1788 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: more gold
map: unchanged (58 labels)
```

```
#0209  click Offer less  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0209_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Russia /  /  / "I suggest offering 283 gold per turn."
   controls: [Offer 283 gold]  [Offer more]  [Offer less]  [Skip gold]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1810 of 1810 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: less gold
map: unchanged (58 labels)
```

```
#0210  click Offer 270  ->  ERROR: no visible control's text holds "Offer 270"
view: <run>\frames\0210_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1810 of 1810 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: more gold
   Directing Talleyrand: more gold
   Directing Talleyrand: more gold
   Directing Talleyrand: less gold
map: unchanged (58 labels)
```

```
#0211  click Too costly  ->  ERROR: no visible control's text holds "Too costly"
view: <run>\frames\0211_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1810 of 1810 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: more gold
   Directing Talleyrand: more gold
   Directing Talleyrand: more gold
   Directing Talleyrand: less gold
map: unchanged (58 labels)
```

```
#0212  look  ->  ok
  (a fresh frame)
view: <run>\frames\0212_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1810 of 1810 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: more gold
   Directing Talleyrand: more gold
   Directing Talleyrand: more gold
   Directing Talleyrand: less gold
map: unchanged (58 labels)
```

```
#0213  click Offer 283  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0213_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Russia /  /  / "Offering an Action Point is extraordinary — an entire extra action each turn. Worth 18 acceptance points, more than ceding a province."
   controls: [Offer the AP]  [Too costly]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1832 of 1832 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: offer gold
map: unchanged (58 labels)
```

```
#0214  click Too costly  ->  ok
  (clicked at (1834, 727))
view: <run>\frames\0214_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 508 px] ──
   ARMISTICE PREVIEW - Russia /  / Proposed Terms / France concedes: /   • France pays 283 gold per turn to Russia for as long as the treaty stands / Mutual: /   • Armistice (cease hostilities temporarily) — France and Russia /  / Assessment: GENEROUS /  / Armistice Terms /   A 5-turn ceasefire: fighting stops. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war …
   controls: [icon: Close (Esc) @(2151,292)]  [Send]  [Start over]  [Reconsider]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1854 of 1854 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: skip ap
map: unchanged (58 labels)
```

```
#0215  click Send  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0215_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 78 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Marshal Massena seeks an audience @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+16]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -3 →
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1920 of 1920 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,579 (+883 next turn)
   Inf:
   94,149
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Russian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (58 labels)
```

```
#0216  look  ->  ok
  (a fresh frame)
view: <run>\frames\0216_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1920 of 1920 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: offer gold
   Directing Talleyrand: skip ap
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Russian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
map: unchanged (58 labels)
```

```
#0217  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0217_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 8
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 77 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1854 of 1855 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,506 (+832 next turn)
   Inf:
   95,749
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — Awaiting orders.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Brunswick — Brunswick — large force [partial]
   Castanos — Normandy — small force [partial]
   Paget — Berry — screening force [partial]
   TURN EVENTS
   Switzerland loyalty 76 (-3): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   Brunswick passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 3.
   The armistice between Austria and France has concluded. Peace declared.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1248 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► propose peace with Russia
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► propose armistice with Russia
   Directing Talleyrand: modify generous
   Directing Talleyrand: less generous
   Directing Talleyrand: adjust terms
   Directing Talleyrand: territory no gold
   Directing Talleyrand: more gold
   Directing Talleyrand: more gold
   Directing Talleyrand: more gold
   Directing Talleyrand: more gold
   Directing Talleyrand: less gold
   Directing Talleyrand: offer gold
   Directing Talleyrand: skip ap
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Russian court with your Armistice proposal. Expect a response by next turn. (1 DP spent)
   ► end turn
   ═══════════════════════════════════════
   TURN 9 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Contributions: -110g | Charges of Empire: -234g | Admiralty: -90g | Blockade: -328g | Other: +1319g | Upkeep: -2220g | Net: +927g | Spent: 1248g
   Treasury: 5,506g
   Actions refreshed: 4/4
   Supply shortage at Burgundy: Soult loses 135 troops
   Garrison at Munich reinforced: 8,000 -> 10,000
   Garrison at Hanover reinforced: 0 -> 2,000
   Switzerland loyalty 73 (-3): satellite drift, relations with the lord
   Talleyrand returns from Russia with a counter-proposal. They could not accept our terms, but offer an alternative:
   Armistice between France and Russia
   - France offers 283 gold per turn for as long as the treaty stands
   - France offers 200 gold
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier reports that Murat resents Ney's laurels again, 6 turns after the last — he has grown restless for glory.
   Berthier reports that Bernadotte resents Ney's laurels again, 6 turns after the last — he has grown quiet in the way the staff have learned to read.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2050,314)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1686,354)
map pieces: 100(1396,395)  45(1354,613)  35(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  ?(1525,504)  Castanos(1525,465)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1501,602)  Paget(1501,564)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  ?(1384,625)  Cuesta(1384,587)  Davout(1881,352)  Murat(1905,326)  Soult(1685,495)  Dumonceau(1755,326)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,494)  12k(1551,436)  ?(1769,580)  2k(1777,297)  10k(1755,420)  12k(1710,420)  10k(1910,645)
```

```
#0218  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0218_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 77 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Marshal Massena seeks an audience @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+16]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -4 →
   T:8
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War for the Hanoverian Prize]
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
   5,506 (+832 next turn)
   Inf:
   95,749
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Garrison at Hanover reinforced: 0 -> 2,000
   Switzerland loyalty 73 (-3): satellite drift, relations with the lord
   Talleyrand returns from Russia with a counter-proposal. They could not accept our terms, but offer an alternative:
   Armistice between France and Russia
   - France offers 283 gold per turn for as long as the treaty stands
   - France offers 200 gold
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier reports that Murat resents Ney's laurels again, 6 turns after the last — he has grown restless for glory.
   Berthier reports that Bernadotte resents Ney's laurels again, 6 turns after the last — he has grown quiet in the way the staff have learned to read.
   --- Strategic Order Updates ---
   Soult: Soult pursues Paget. 2 regions away.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 9
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   • Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
   • Sire — Britain's gold reaches Russia — the subsidy stands at 300 this season.
   SITUATION
   France holds 28 regions. Treasury: 5,506g (+927 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 1% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 7 turns idle.
   > Soult — Burgundy — 29,265 — Pursuing Paget — 2 turns behind him. (to the letter)
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 3 turns idle.
   - Murat — Frankfurt — 19,725 — 3 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — Awaiting orders.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Berry — small force [partial]
   Paget — Gascony — screening force [partial]
   Cuesta — Bordelais — small force [partial]
   TURN EVENTS
   Supply shortage at Burgundy: Soult loses 135 troops
   Switzerland loyalty 73 (-3): satellite drift, relations with the lord
   Berthier reports that Murat resents Ney's laurels again, 6 turns after the last — he has grown restless for glory.
   Berthier reports that Bernadotte resents Ney's laurels again, 6 turns after the last — he has grown quiet in the way the staff have learned to read.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Russia.
   THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand returns from Russia with a response.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Austria takes up a new design: The Eastern Question.
   The court of Hanover takes up a new design: its own survival.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Russia — Armistice
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 77/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0219  click Dispatch  ->  ok
  (clicked at (425, 18))
view: <run>\frames\0219_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1455 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 9 — Late January 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9). /   • Sire — 3 turns now with enemy colours on French so …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1806 of 1806 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 77/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0220  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0220_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   -4 →
   T:8
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1806 of 1806 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 77/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0221  click Envoys  ->  ok
  (clicked at (3395, 18))
view: <run>\frames\0221_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 618 px] ──
   COUNTER-OFFER / Czartoryski (Schemer) of Russia /  / In response to your Armistice proposal, Russia offers modified terms: /  / Revised Terms: / France concedes: /   - France pays 283 gold per turn to Russia for as long as the treaty stands /   - France pays 200 gold to Russia / Mutual: /   - Armistice (cease hostilities temporarily) — France and Russia /  / Assessment: GENEROUS /  / War Summary / …
   controls: [Accept Terms]  [Reject Terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
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
   5,506 (+832 next turn)
   Inf:
   95,749
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 77/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0222  click Accept Terms  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0222_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 77 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Marshal Massena seeks an audience @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+17]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Britain
   -4 →
   T:8
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War with Britain]  [War with Russia — Russia, truce 5t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,306 (+568 next turn)
   Inf:
   95,749
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0223  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0223_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (1)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0224  look  ->  ok
  (a fresh frame)
view: <run>\frames\0224_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0225  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0225_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px] ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (1)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  Armistice  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +32 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -12 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0226  click Russia  ->  ERROR: 2 controls match "Russia" — pick one with click#N
  candidates: #1 [Russia  —  Armistice  |  -80 (Hostile)] on DiplomacyWizard @(1825,505) | #2 [Prussia  —  Non-Aggression  |  +3 (Neutral)  [MISSION]] on DiplomacyWizard @(1825,545)
view: <run>\frames\0226_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0227  look  ->  ok
  (a fresh frame)
view: <run>\frames\0227_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0228  click_at 1829 505  ->  ok
  (clicked at (1829, 505) on @Button@7035 'Russia  —  Armistice  |  -80 (Hostile)' (Button, layer 110))
view: <run>\frames\0228_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 0 of 325 px] ──
   THE CABINET — Russia
   DP: 7
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Armistice — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Russia, though they will demand terms." / Recommendation: Permit me to observe, Sire, that 5 turns of truce remain with Russia, relations -80; the ledger stands: the war score reads 0 for France (0 battles,  …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0229  scroll 1800 560 down 6  ->  ok
  (scrolled down 6 at (1800, 560))
view: <run>\frames\0229_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 420 px, 155 of 311 px] ──
   THE CABINET — Russia
   DP: 7
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Armistice — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Russia, though they will demand terms." / Recommendation: Permit me to observe, Sire, that 5 turns of truce remain with Russia, relations -80; the ledger stands: the war score reads 0 for France (0 battles,  …
   Mission already active
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Peace (2 DP)  —  Hopeless]  [Improve Relations (1 DP)  —  +8 relation/turn](disabled: Mission already active)  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0230  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0230_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0231  click Recall  ->  ERROR: no visible control's text holds "Recall"
view: <run>\frames\0231_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0232  click Talleyrand: Improving  ->  ok
  (clicked at (3230, 18))
view: <run>\frames\0232_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 156 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Prussia
   DP: 7/7
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 7/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Improving Relations → Prussia /   Neutral (+0 over 2 turns) /   Status: Active, Cost: 1 DP/turn /   Effect: +8 relation per turn /   Net +7 a turn · ≈14 turns to +100 at the pre …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (57 labels)
```

```
#0233  click Assess the Situation  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0233_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 200 px] ──
   TALLEYRAND'S ASSESSMENT /  / "Sire — the state of Europe, plainly told. /  /   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1) /  /   Against Britain: the war hangs in the balance (-4) — 0 battles across 8 turns. /     Britain's design: The Low Countries — They will not suffer France's bloc in Flanders. /     Their price: prepared to go as far as war — France stands in the w …
   controls: [icon: Close (Esc) @(2151,292)]  [Seek terms with Britain]  [Thank you]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 77 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1917 of 1917 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,306 (+568 next turn)
   Inf:
   95,749
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Talleyrand, assess our situation
map: unchanged (57 labels)
```

```
#0234  click Seek terms with Britain  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0234_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 77 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Marshal Massena seeks an audience @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+18]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Britain
   -4 →
   T:8
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War with Britain]  [War with Russia — Russia, truce 5t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,306 (+568 next turn)
   Inf:
   95,749
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
map: unchanged (57 labels)
```

```
#0235  look  ->  ok
  (a fresh frame)
view: <run>\frames\0235_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
   ► Talleyrand, assess our situation
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
map: unchanged (57 labels)
```

```
#0236  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0236_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (1)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
   ► Talleyrand, assess our situation
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
map: unchanged (57 labels)
```

```
#0237  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0237_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (1)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  Armistice  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +32 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -12 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
   ► Talleyrand, assess our situation
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
map: unchanged (57 labels)
```

```
#0238  click_at 1829 545  ->  ok
  (clicked at (1829, 545) on @Button@7228 'Prussia  —  Non-Aggression  |  +3 (Neutr' (Button, layer 110))
view: <run>\frames\0238_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 244 px, 0 of 627 px] ──
   THE CABINET — Prussia
   DP: 6
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Non-Aggression   Relation: +3 (Neutral) /  / "We have Prussia's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: Relations must improve before proposals will find purchase. / Talleyrand: "Prussia stands on the Emperor's roads, Sire — The Protector of the Rhine (A German Crown Brought to T …
   Relations with Prussia stand at 3; a Defensive Alliance needs 20.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Neutral (+0 over 2 turns)]  [Propose Defensive Alliance (2 DP)  —  Unlikely](disabled: Relations with Prussia stand at 3; a Defensive Alliance needs 20.)  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
   ► Talleyrand, assess our situation
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
map: unchanged (57 labels)
```

```
#0239  click Cancel: Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0239_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 77 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Marshal Massena seeks an audience @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+18]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2094 of 2094 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,306 (+568 next turn)
   Inf:
   95,749
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (57 labels)
```

```
#0240  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0240_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 726 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   At War (1)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2094 of 2094 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (57 labels)
```

```
#0241  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0241_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 163 of 729 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (1)
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  Armistice  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +32 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -12 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2094 of 2094 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (57 labels)
```

```
#0242  click_at 1829 505  ->  ok
  (clicked at (1829, 505) on @Button@7354 'Russia  —  Armistice  |  -80 (Hostile)' (Button, layer 110))
view: <run>\frames\0242_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 398 px, 0 of 233 px] ──
   THE CABINET — Russia
   DP: 6
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Armistice — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Russia, though they will demand terms." / Recommendation: If I may, Sire — a level war in truce: 5 turns, relations -80; the ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2094 of 2094 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (57 labels)
```

```
#0243  scroll 1800 560 down 6  ->  ok
  (scrolled down 6 at (1800, 560))
view: <run>\frames\0243_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 398 px, 155 of 244 px] ──
   THE CABINET — Russia
   DP: 6
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Armistice — the War with the Third Coalition   Relation: -80 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Russia, though they will demand terms." / Recommendation: If I may, Sire — a level war in truce: 5 turns, relations -80; the ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Peace (2 DP)  —  Hopeless]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2094 of 2094 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
map: unchanged (57 labels)
```

```
#0244  click Improve Relations  ->  ok
  (clicked at (1825, 557))
view: <run>\frames\0244_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Russia /  / "Sire, I shall begin efforts to improve relations with Russia. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 77 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2139 of 2139 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,306 (+568 next turn)
   Inf:
   95,749
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► improve relations with Russia
map: unchanged (57 labels)
```

```
#0245  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0245_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 77 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Concluded @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Marshal Massena seeks an audience @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+18]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Britain
   -4 →
   T:8
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [War with Britain]  [War with Russia — Russia, truce 5t]  [War for the Hanoverian Prize]
── BottomLeftUI (layer 0) [scrolled 2204 of 2204 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,306 (+568 next turn)
   Inf:
   95,749
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Russia. (1 DP/turn)
map: unchanged (57 labels)
```

```
#0246  look  ->  ok
  (a fresh frame)
view: <run>\frames\0246_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2204 of 2204 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Russia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Russia. (1 DP/turn)
map: unchanged (57 labels)
```

```
#0247  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0247_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 113 px] ──
   ENEMY PHASE - Turn 9
   BRITAIN / ──────────────────────────── / - Paget moves to Guyenne /  / SPAIN / ──────────────────────────── / - Castanos attacks Paget /     Battle of Guyenne /     Castanos: 772 casualties, 13,207 remaining /     Paget: 1,350 casualties, 3,126 remaining /     Result: Attacker tactical victory (Castanos victorious) — and advances into Guyenne /     ⚔ View the field /     --- Berthier's Report ---  …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 75 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1985 of 1987 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,879 (+506 next turn)
   Inf:
   97,249
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 7 turns idle.
   > Soult — Burgundy — 29,265 — Pursuing Paget — 2 turns behind him. (to the letter)
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 3 turns idle.
   - Murat — Frankfurt — 19,725 — 3 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — Awaiting orders.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Berry — small force [partial]
   Paget — Gascony — screening force [partial]
   Cuesta — Bordelais — small force [partial]
   TURN EVENTS
   Supply shortage at Burgundy: Soult loses 135 troops
   Switzerland loyalty 73 (-3): satellite drift, relations with the lord
   Berthier reports that Murat resents Ney's laurels again, 6 turns after the last — he has grown restless for glory.
   Berthier reports that Bernadotte resents Ney's laurels again, 6 turns after the last — he has grown quiet in the way the staff have learned to read.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Russia.
   THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
   Hanover passes from Hanover to Prussia.
   Oldenburg passes from Hanover to Prussia.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand returns from Russia with a response.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Austria takes up a new design: The Eastern Question.
   The court of Hanover takes up a new design: its own survival.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Russia — Armistice
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-3)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 77/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's counter-proposal. Treaty signed: At War → Armistice with Russia.
   ► Talleyrand, assess our situation
   Directing Talleyrand: execute suggestion
   I shall ask Britain's chancery to name its terms for the War with the Third Coalition — France + Spain + Holland against Britain, Sire. Expect an answer with the next dispatches.
   ► Talleyrand, cancel mission with Prussia
   Talleyrand's mission to Prussia has been cancelled.
   ► improve relations with Russia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Russia. (1 DP/turn)
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2581g | Contributions: -101g | Charges of Empire: -310g | Admiralty: -90g | Blockade: -328g | Other: +1041g | Upkeep: -2220g | Net: +573g
   Treasury: 5,879g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 10,000 -> 12,000
   Garrison at Hanover reinforced: 2,000 -> 4,000
   Switzerland loyalty 70 (-3): satellite drift, relations with the lord
   Britain subsidizes Russia with 300 gold.
   Russia and Naples have signed a Non-Aggression Pact.
   Peace concluded between Hanover and Prussia without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   Berthier notes that Massena no longer presses the matter — his quarrel with Ney has cooled.
   Massena's resentment of Ney has cooled with time.
   Berthier notes that Davout has grown restless — he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,600)  36(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  Castanos(1422,574)  Paget(1446,548)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Davout(1881,352)  Murat(1905,326)  Dumonceau(1755,322)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  4k(1777,293)  10k(1755,420)  12k(1710,420)  10k(1910,645)
```

```
#0248  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0248_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 75 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement offer from Britain @(3187,64)]  [icon: Prussia Declares War! @(3229,64)]  [icon: Bernadotte arrived @(3271,64)]  [icon: Ney arrived @(3313,64)]  [icon: Bavaria Eliminated! @(3355,64)]  [Talleyrand at Russia — Improving Relations]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Britain
   -4 →
   T:9
   controls: [THIRD COALITION  ▸]  [War with Britain]  [War with Russia — Russia, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2008 of 2008 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,879 (+506 next turn)
   Inf:
   97,249
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2581g | Contributions: -101g | Charges of Empire: -310g | Admiralty: -90g | Blockade: -328g | Other: +1041g | Upkeep: -2220g | Net: +573g
   Treasury: 5,879g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 10,000 -> 12,000
   Garrison at Hanover reinforced: 2,000 -> 4,000
   Switzerland loyalty 70 (-3): satellite drift, relations with the lord
   Britain subsidizes Russia with 300 gold.
   Russia and Naples have signed a Non-Aggression Pact.
   Peace concluded between Hanover and Prussia without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   Berthier notes that Massena no longer presses the matter — his quarrel with Ney has cooled.
   Massena's resentment of Ney has cooled with time.
   Berthier notes that Davout has grown restless — he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Soult: Soult pursues Paget. 2 regions away.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
   • Sire — Leon has been taken by Britain.
   • Sire — a truce with Russia is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
   SITUATION
   France holds 28 regions. Treasury: 5,879g (+573 by the accounts)
   The courts at war hold 11 regions. Estimated enemy strength: 2% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 8 turns idle.
   > Soult — Limousin — 29,265 — Pursuing Paget — 2 turns behind him. (to the letter)
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 4 turns idle.
   - Murat — Frankfurt — 19,725 — 4 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 3 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 13,075 [confirmed]
   Paget — Guyenne — 3,126 [confirmed]
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   TURN EVENTS
   Switzerland loyalty 70 (-3): satellite drift, relations with the lord
   Berthier notes that Massena no longer presses the matter — his quarrel with Ney has cooled.
   Massena's resentment of Ney has cooled with time.
   Berthier notes that Davout has grown restless — he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — France and Russia have signed the Armistice.
   A truce with Russia: the fighting stops for 5 turns. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 8 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -80 and will thaw to -65, short of -60; the ledger and the war's age come back with it.
   Leon passes from Spain to Britain.
   Westphalia passes from Hanover to Prussia.
   East Frisia passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Britain has offered terms to settle the War with the Third Coalition — Britain + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -69.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   The court of Prussia takes up a new design: Armed Neutrality.
   Relations with Russia have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-4)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 75/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0249  look  ->  ok
  (a fresh frame)
view: <run>\frames\0249_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2008 of 2008 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 75/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0250  click Envoys  ->  ok
  (clicked at (3378, 18))
view: <run>\frames\0250_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm', 'war_status_panel (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   SETTLEMENT OFFER FROM BRITAIN /  / the War with the Third Coalition — Britain + Russia /  / "His Majesty's Government offers terms for the War with the Third Coalition — Britain + Russia. No indemnity is asked and none is offered; London proposes only that the guns fall silent." /  / Their proposed terms: /   • Peace /  / Covered enemies: Britain /  / "Sire, Britain has dispatched a settlement of  …
   controls: [Review Settlement Offer]  [Request Revision]  [Reject Offer]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2008 of 2008 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,879 (+506 next turn)
   Inf:
   97,249
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 75/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0251  click Review Settlement Offer  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0251_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Settlement of the War with the Third Coalition — the table with Britain — ready for ratification / the War with the Third Coalition — the table with Britain - Separate settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Britain / Still at war: Russia / Will carry — these are the terms they offered. / Sire, this settlement of the War with  …
   The table /   * Britain - Their own terms White peace /       Blocker: Settlement legitimacy /       Castlereagh for Britain: these are the terms Britain laid before France; Britain does not haggle with its own dispatch. / This peace carries.
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry; the verdict beside each row is that court's own, and the terms before you stand as offered. / Sire, the white peace for the War with the Third Coalition — the table with Britain is ready: no further land changes hands — each side keeps what it holds, now by treaty. Ratify and the fie …
   controls: [Ratify White Peace]  [Open War Detail]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 75 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2029 of 2029 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,879 (+506 next turn)
   Inf:
   97,249
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: accept settlement offer
map: unchanged (53 labels)
```

```
#0252  click Ratify White Peace  ->  ok
  (clicked at (1455, 931))
view: <run>\frames\0252_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 37 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3187,64)]  [icon: Prussia Declares War! @(3229,64)]  [icon: Bernadotte arrived @(3271,64)]  [icon: Ney arrived @(3313,64)]  [icon: Bavaria Eliminated! @(3355,64)]  [Talleyrand at Russia — Improving Relations]  [Recall]
── DiplomaticLedger (layer 50) [scrolled 0 of 1674 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Russia
   DP: 6/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (8 turns ago) /  / Russia ↔ Naples: Non Aggression /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 10 (0 turns ago) /  / Prussia ↔ France: Non Aggression /   Clauses: Gold payment: 150 (Prussia -> France) /   Duration: permanent  …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Sire, the settlement of the War with the Third Coalition — the table with Britain is not a curtain call; it is an acco>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2183 of 2183 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,879 (+1,724 next turn)
   Inf:
   97,249
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: confirm settlement
   Settlement Ratified: the War with the Third Coalition — the table with Britain (3 pairs resolved).
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (53 labels)
```

```
#0253  look  ->  ok
  (a fresh frame)
view: <run>\frames\0253_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 1674 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2183 of 2183 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (53 labels)
```

```
#0254  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0254_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2183 of 2183 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (53 labels)
```

```
#0255  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0255_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1521 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 10 — Early February 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants. /   • Sire — Leon ha …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2183 of 2183 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (53 labels)
```

```
#0256  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0256_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2183 of 2183 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (53 labels)
```

```
#0257  click Diplomacy  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0257_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 2977 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Russia
   DP: 6/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 36% of the continent's weight. /   The courts believe he will go as far as gold (alarm 37). /   They think he is coming for Hesse — his corps stand against their soil. /  / The Emperor' …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2183 of 2183 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (53 labels)
```

```
#0258  click CONGRESS  ->  ok
  (clicked at (2089, 273))
view: <run>\frames\0258_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 640 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Russia
   DP: 6/7
   ═══ THE CONGRESS OF PARIS ═══ / Europe must RECOGNIZE the new order. With 45 titled provinces the Emperor may summon the great powers to Paris; each answers at every end turn, with its reason and its price, and the Congress sits 8 turns. If on the last day every court recognizes, is shut out or is gone, and the hold never broke, the Imperial Peace is proclaimed. /  / THE CONGRESS OF PARIS — 35 of  …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS](disabled: You are reading this book)  <Open the Cabinet at London →>  <Open the Cabinet at St Petersburg →>  <Open the Cabinet at Vienna →>  <Open the Cabinet at Berlin →>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2183 of 2183 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (53 labels)
```

```
#0259  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0259_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 4t]
── BottomLeftUI (layer 0) [scrolled 2183 of 2183 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (53 labels)
```

```
#0260  type cancel Soult's pursuit  ->  ok
  (typed and Enter)
view: <run>\frames\0260_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult awaits further orders.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1718 of 1718 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,879 (+1,724 next turn)
   Inf:
   97,249
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
   • Sire — Leon has been taken by Britain.
   • Sire — a truce with Russia is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
   SITUATION
   France holds 28 regions. Treasury: 5,879g (+573 by the accounts)
   The courts at war hold 11 regions. Estimated enemy strength: 2% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 8 turns idle.
   > Soult — Limousin — 29,265 — Pursuing Paget — 2 turns behind him. (to the letter)
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 4 turns idle.
   - Murat — Frankfurt — 19,725 — 4 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 3 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 13,075 [confirmed]
   Paget — Guyenne — 3,126 [confirmed]
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   TURN EVENTS
   Switzerland loyalty 70 (-3): satellite drift, relations with the lord
   Berthier notes that Massena no longer presses the matter — his quarrel with Ney has cooled.
   Massena's resentment of Ney has cooled with time.
   Berthier notes that Davout has grown restless — he has not seen laurels while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — France and Russia have signed the Armistice.
   A truce with Russia: the fighting stops for 5 turns. The ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 8 turns old and stays so; exhaustion holds. At expiry: the war resumes where it stood — relations stand at -80 and will thaw to -65, short of -60; the ledger and the war's age come back with it.
   Leon passes from Spain to Britain.
   Westphalia passes from Hanover to Prussia.
   East Frisia passes from Hanover to Prussia.
   Leon passes from Britain to Spain.
   Britain has offered terms to settle the War with the Third Coalition — Britain + Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -69.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
   The court of Prussia takes up a new design: Armed Neutrality.
   Relations with Russia have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (-4)
   War Purpose: Defense vs Russia (War with the Third Coalition) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 75/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: confirm settlement
   Settlement Ratified: the War with the Third Coalition — the table with Britain (3 pairs resolved).
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   ► cancel Soult's pursuit
   Soult awaits further orders.
map: unchanged (53 labels)
```

```
#0261  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0261_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -69 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1718 of 1718 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   ► cancel Soult's pursuit
   Soult awaits further orders.
map: unchanged (53 labels)
```

```
#0262  scroll 1800 560 down 15  ->  ok
  (scrolled down 15 at (1800, 560))
view: <run>\frames\0262_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 544 of 704 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -90 (Hostile)]  [Austria  —  Peace  |  -34 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1718 of 1718 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   ► cancel Soult's pursuit
   Soult awaits further orders.
map: unchanged (53 labels)
```

```
#0263  click Switzerland  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0263_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 46 px, 0 of 68 px] ──
   THE CABINET — Switzerland
   DP: 6
   TALLEYRAND'S ASSESSMENT — SWITZERLAND / Status: Vassal   Relation: -20 (Wary) / Loyalty: 70 ↓   Autonomy: Satellite   Tribute: 225g /  / "Switzerland serves faithfully. Tribute flows, the garrison keeps order. A reliable vassal." / Recommendation: No urgent action needed
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Invest in Vassal (1 DP + 200g)]  [Increase Autonomy (1 DP)  —  loyalty 70 → 80; its autonomy drift -2 → +1 a turn; tribute 75% → 50% (-75 gold a turn); th]  [Decrease Autonomy (1 DP)  —  loyalty 70 → 55; its autonomy drift -2 → -4 a turn; tribute 75% → 100% (+75 gold a turn); t]  [Release Vassal (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1718 of 1718 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   ► cancel Soult's pursuit
   Soult awaits further orders.
map: unchanged (53 labels)
```

```
#0264  click Increase Autonomy  ->  ok
  (clicked at (1825, 506))
view: <run>\frames\0264_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 37 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3187,64)]  [icon: Prussia Declares War! @(3229,64)]  [icon: Bernadotte arrived @(3271,64)]  [icon: Ney arrived @(3313,64)]  [icon: Bavaria Eliminated! @(3355,64)]  [Talleyrand at Russia — Improving Relations]  [Recall]
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
   5,879 (+1,649 next turn)
   Inf:
   97,249
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► increase autonomy Switzerland
   Switzerland autonomy changed: Satellite → Autonomous. +10 loyalty (increased autonomy). Tribute rate: 75% → 50% (a permanent income cut).
map: unchanged (53 labels)
```

```
#0265  look  ->  ok
  (a fresh frame)
view: <run>\frames\0265_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1806 of 1806 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► cancel Soult's pursuit
   Soult awaits further orders.
   ► increase autonomy Switzerland
   Switzerland autonomy changed: Satellite → Autonomous. +10 loyalty (increased autonomy). Tribute rate: 75% → 50% (a permanent income cut).
map: unchanged (53 labels)
```

```
#0266  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0266_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 10
   SPAIN / ──────────────────────────── / - Castanos fortifies position /  / ──────────────────────────── / Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 39 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2139 of 2139 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,534 (+1,582 next turn)
   Inf:
   98,749
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2583g | Charges of Empire: -170g | Other: +970g | Upkeep: -1728g | Net: +1655g
   Treasury: 7,534g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 12,000 -> 14,000
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   Russia has downgraded relations with Austria: ALLIANCE → DEFENSIVE_ALLIANCE.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,574)  36(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  Castanos(1434,574)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  ?(1384,625)  Wellesley(1384,600)  Davout(1881,352)  Murat(1905,326)  ?(1551,403)  Paget(1551,364)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  ?(1777,319)  ?(1755,420)  12k(1711,420)  10k(1910,645)
```

```
#0267  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0267_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 39 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Petition from Holland @(3393,64)]  [icon: Diplomatic Tension @(3435,64)]  [icon: The blockade on our ports lifts @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+23]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 3t]
── BottomLeftUI (layer 0) [scrolled 2031 of 2031 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,534 (+1,582 next turn)
   Inf:
   98,749
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► cancel Soult's pursuit
   Soult awaits further orders.
   ► increase autonomy Switzerland
   Switzerland autonomy changed: Satellite → Autonomous. +10 loyalty (increased autonomy). Tribute rate: 75% → 50% (a permanent income cut).
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2583g | Charges of Empire: -170g | Other: +970g | Upkeep: -1728g | Net: +1655g
   Treasury: 7,534g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 12,000 -> 14,000
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   Russia has downgraded relations with Austria: ALLIANCE → DEFENSIVE_ALLIANCE.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 11
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — the war with Britain is over. The peace grants safe passage home.
   • Sire — our peace binds Britain for 4 more turns; then she may join a league (relations −89).
   SITUATION
   France holds 28 regions. Treasury: 7,534g (+1,655 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 9 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 5 turns idle.
   - Murat — Frankfurt — 19,725 — 5 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 4 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 13,075 [confirmed]
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Paget — Normandy — screening force [partial]
   Wellesley — Bordelais — screening force [partial]
   TURN EVENTS
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   The coalition against France has dissolved.
   Sire, the settlement of the War with the Third Coalition — the table with Britain is not a curtain call; it is an accounting. Spain must be read beside reactions from 1 courts, and the largest political cost remains settlement ratified.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -58.
   An envoy from Holland has arrived with a petition.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
   The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
   And Sardinia stirs at its own design.
   Relations with Russia have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 39/100 [Tension]
   Europe has watched us 9 quiet turns. At this pace the courts consult on turn 24 and declare on turn 27: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0268  click Envoys  ->  ok
  (clicked at (3382, 18))
view: <run>\frames\0268_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Schimmelpenninck (Loyalist) of Holland /  / The petition: /   - Grant it, and Holland's tribute of 337g a turn is remitted for 8 collections (2696g forgone): loyalty +2 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Holland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loya …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2031 of 2031 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,534 (+1,582 next turn)
   Inf:
   98,749
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 39/100 [Tension]
   Europe has watched us 9 quiet turns. At this pace the courts consult on turn 24 and declare on turn 27: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0269  click Refuse  ->  ok
  (clicked at (1829, 687))
view: <run>\frames\0269_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 39 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Diplomatic Tension @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── WarStatusPanel (layer 25): unchanged
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
   7,534 (+1,582 next turn)
   Inf:
   98,749
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0270  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0270_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1697 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 11 — Late February 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — the war with Britain is over. The peace grants safe passage home. /   • Sire — our peace binds Britain for 4 more turns; then she ma …
   controls: [Pin]  [icon @(2143,296)]  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0271  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0271_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 3t]
── BottomLeftUI (layer 0) [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0272  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0272_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -58 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0273  scroll 1800 560 down 15  ->  ok
  (scrolled down 15 at (1800, 560))
view: <run>\frames\0273_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 544 of 704 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  -20 (Wary)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -89 (Hostile)]  [Austria  —  Peace  |  -33 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0274  click Britain  ->  ok
  (clicked at (1825, 587))
view: <run>\frames\0274_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 90 px, 0 of 548 px] ──
   THE CABINET — Britain
   DP: 6
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: Peace   Relation: -89 (Hostile) /  / "Relations with Britain remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. / Talleyrand: "Britain stands on the Emperor's roads, Sire — The Continental System (The Blockade of the B …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1116g) (1 DP + 1116g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (55 labels)
```

```
#0275  click Buy Off Their Design  ->  ok
  (clicked at (1825, 551))
view: <run>\frames\0275_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 39 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Diplomatic Tension @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2208 of 2208 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,418 (+1,631 next turn)
   Inf:
   98,749
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0276  look  ->  ok
  (a fresh frame)
view: <run>\frames\0276_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2208 of 2208 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0277  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0277_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -58 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2208 of 2208 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0278  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0278_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 687 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -58 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +12 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2208 of 2208 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0279  click#1 Russia  ->  ok
  (clicked at (1825, 444))
view: <run>\frames\0279_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 332 px, 0 of 381 px] ──
   THE CABINET — Russia
   DP: 5
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Armistice — the War with Russia   Relation: -58 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Russia, though they will demand terms." / Recommendation: If I may, Sire — a level war in truce: 3 turns, relations -58; the ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 10 tu …
   Their design is aimed at France herself.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile (+22 over 2 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1176g) (1 DP + 1176g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2208 of 2208 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0280  look  ->  ok
  (a fresh frame)
view: <run>\frames\0280_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 332 px, 0 of 381 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2208 of 2208 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0281  click Buy Off Their Design  ->  ok
  (clicked at (1825, 594))
view: <run>\frames\0281_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 39 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Diplomatic Tension @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1762 of 1762 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,242 (+1,683 next turn)
   Inf:
   98,749
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   MORNING DISPATCH — Turn 11
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — the war with Britain is over. The peace grants safe passage home.
   • Sire — our peace binds Britain for 4 more turns; then she may join a league (relations −89).
   SITUATION
   France holds 28 regions. Treasury: 7,534g (+1,655 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 9 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 5 turns idle.
   - Murat — Frankfurt — 19,725 — 5 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 4 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Castanos — Guyenne — 13,075 [confirmed]
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Paget — Normandy — screening force [partial]
   Wellesley — Bordelais — screening force [partial]
   TURN EVENTS
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Ney's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   The coalition against France has dissolved.
   Sire, the settlement of the War with the Third Coalition — the table with Britain is not a curtain call; it is an accounting. Spain must be read beside reactions from 1 courts, and the largest political cost remains settlement ratified.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -58.
   An envoy from Holland has arrived with a petition.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
   The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
   And Sardinia stirs at its own design.
   Relations with Russia have improved significantly (+11 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 39/100 [Tension]
   Europe has watched us 9 quiet turns. At this pace the courts consult on turn 24 and declare on turn 27: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0282  look  ->  ok
  (a fresh frame)
view: <run>\frames\0282_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1762 of 1762 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0283  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0283_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -53 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1762 of 1762 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0284  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0284_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 687 px] ──
   THE CABINET
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -53 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +12 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1762 of 1762 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0285  click#1 Spain  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0285_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 156 px, 0 of 516 px] ──
   THE CABINET — Spain
   DP: 4
   TALLEYRAND'S ASSESSMENT — SPAIN / Status: Alliance   Relation: +12 (Neutral) /  / "Our alliance with Spain holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Relations must improve before proposals will find purchase. /  / KEY FACTORS /   + Base willingness (+10) /   + Diplomatic skill advantage (+10) /   + Current relations (+6) /   - Grievance Modif …
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1762 of 1762 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0286  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0286_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1762 of 1762 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0287  click Diplomacy  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0287_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 2977 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Improving Relations → Russia
   DP: 4/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 36% of the continent's weight. /   The courts believe he will go as far as gold (alarm 39). /   They think he is coming for Hesse — his corps stand against their soil. /  / The Emperor' …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [BALANCE OF EUROPE]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1762 of 1762 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0288  click NATIONS  ->  ok
  (the control is disabled; the click did nothing (its reason: You are reading this book))
view: <run>\frames\0288_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 2977 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1762 of 1762 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0289  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0289_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 3t]
── BottomLeftUI (layer 0) [scrolled 1762 of 1762 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (55 labels)
```

```
#0290  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0290_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 11
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 40 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2095 of 2095 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,932 (+1,615 next turn)
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
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2585g | Charges of Empire: -142g | Other: +975g | Upkeep: -1728g | Net: +1690g | Spent: 2292g
   Treasury: 6,932g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 14,000 -> 16,000
   Holland loyalty 85 (-3): satellite drift, relations with the lord
   Relations between Austria and Russia are deteriorating. Defensive Alliance may collapse in 2 turns.
   Russia has downgraded relations with Austria: DEFENSIVE_ALLIANCE → NON_AGGRESSION.
   Territorial rivalry between Russia and Sweden grows.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  36(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1434,578)  Castanos(1434,540)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Davout(1881,352)  Murat(1905,326)  ?(1551,403)  Wellesley(1551,364)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  ?(1777,319)  ?(1755,420)  12k(1711,420)  10k(1910,645)
```

```
#0291  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0291_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 40 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 2t]
── BottomLeftUI (layer 0) [scrolled 2253 of 2253 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,932 (+1,615 next turn)
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
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client's Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 39/100 [Tension]
   Europe has watched us 9 quiet turns. At this pace the courts consult on turn 24 and declare on turn 27: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (98 → 88); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2585g | Charges of Empire: -142g | Other: +975g | Upkeep: -1728g | Net: +1690g | Spent: 2292g
   Treasury: 6,932g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 14,000 -> 16,000
   Holland loyalty 85 (-3): satellite drift, relations with the lord
   Relations between Austria and Russia are deteriorating. Defensive Alliance may collapse in 2 turns.
   Russia has downgraded relations with Austria: DEFENSIVE_ALLIANCE → NON_AGGRESSION.
   Territorial rivalry between Russia and Sweden grows.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   • Sire — relations with Russia have improved significantly (+11 this turn).
   • Sire — the court of Russia takes up a new design: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 6,932g (+1,690 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 10 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 6 turns idle.
   - Murat — Frankfurt — 19,725 — 6 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 5 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   Wellesley — Normandy — screening force [partial]
   TURN EVENTS
   Holland loyalty 85 (-3): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -42.
   The court of Russia takes up a new design: The Gulf and the Straits.
   Relations with Russia have improved significantly (+11 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0292  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0292_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1345 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 12 — Early March 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill. /   • Sire — relations with Russia have improved  …
   controls: [Pin]  [icon @(2143,296)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2253 of 2253 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0293  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0293_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 2t]
── BottomLeftUI (layer 0) [scrolled 2253 of 2253 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0294  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0294_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -42 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2253 of 2253 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0295  click_at 1829 444  ->  ok
  (clicked at (1829, 444) on @RichTextLabel@8320 'The Emperor's Designs — no road proclaim' (RichTextLabel, layer 110))
view: <run>\frames\0295_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2253 of 2253 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0296  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0296_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 687 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -42 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +11 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2253 of 2253 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0297  look  ->  ok
  (a fresh frame)
view: <run>\frames\0297_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 687 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2253 of 2253 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0298  click_at 1829 444  ->  ok
  (clicked at (1829, 444) on @Button@8324 'Russia  —  Armistice  |  -42 (Hostile)  ' (Button, layer 110))
view: <run>\frames\0298_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 332 px, 0 of 423 px] ──
   THE CABINET — Russia
   DP: 6
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Armistice — the War with Russia   Relation: -42 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Russia, though they will demand terms." / Recommendation: Permit me to observe, Sire, that 2 turns of truce remain with Russia, relations -42; the ledger stands: the war score reads 0 for France (0 battles, 0 decisives k …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile (+38 over 3 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Sweden — gold flows, the compact binds both ends (]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [↳ 400g a turn]  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2253 of 2253 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0299  click Licence  ->  ok
  (clicked at (1825, 554))
view: <run>\frames\0299_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 40 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1766 of 1766 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,932 (+1,615 next turn)
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
   ► buy off Russia
   Russia's design — Arbiter of Europe — is bought off for 1176 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2585g | Charges of Empire: -142g | Other: +975g | Upkeep: -1728g | Net: +1690g | Spent: 2292g
   Treasury: 6,932g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 14,000 -> 16,000
   Holland loyalty 85 (-3): satellite drift, relations with the lord
   Relations between Austria and Russia are deteriorating. Defensive Alliance may collapse in 2 turns.
   Russia has downgraded relations with Austria: DEFENSIVE_ALLIANCE → NON_AGGRESSION.
   Territorial rivalry between Russia and Sweden grows.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   • Sire — relations with Russia have improved significantly (+11 this turn).
   • Sire — the court of Russia takes up a new design: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 6,932g (+1,690 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 10 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 6 turns idle.
   - Murat — Frankfurt — 19,725 — 6 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 5 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   Wellesley — Normandy — screening force [partial]
   TURN EVENTS
   Holland loyalty 85 (-3): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -42.
   The court of Russia takes up a new design: The Gulf and the Straits.
   Relations with Russia have improved significantly (+11 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0300  look  ->  ok
  (a fresh frame)
view: <run>\frames\0300_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1766 of 1766 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0301  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0301_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -37 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1766 of 1766 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0302  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0302_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 687 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -37 (Hostile)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +11 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1766 of 1766 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0303  click_at 1829 444  ->  ok
  (clicked at (1829, 444) on @Button@8426 'Russia  —  Armistice  |  -37 (Hostile)  ' (Button, layer 110))
view: <run>\frames\0303_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 332 px, 0 of 381 px] ──
   THE CABINET — Russia
   DP: 5
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Armistice — the War with Russia   Relation: -37 (Hostile) /  / "The guns are silent, but the wound festers. Peace may be achievable with Russia, though they will demand terms." / Recommendation: If I may, Sire — a level war in truce: 2 turns, relations -37; the ledger stands: the war score reads 0 for France (0 battles, 0 decisives kept); the war is 11 tu …
   The compact already stands.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile (+43 over 3 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Sweden — gold flows, the compact binds both ends (](disabled: The compact already stands.)  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1766 of 1766 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0304  click Cancel: Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0304_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 40 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1855 of 1855 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,932 (+1,615 next turn)
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
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (54 labels)
```

```
#0305  look  ->  ok
  (a fresh frame)
view: <run>\frames\0305_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1855 of 1855 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (54 labels)
```

```
#0306  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0306_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -37 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1855 of 1855 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (54 labels)
```

```
#0307  scroll 1800 560 down 15  ->  ok
  (scrolled down 15 at (1800, 560))
view: <run>\frames\0307_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 544 of 704 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  -20 (Wary)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -83 (Hostile)]  [Austria  —  Peace  |  -32 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1855 of 1855 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (54 labels)
```

```
#0308  click Austria  ->  ok
  (clicked at (1825, 627))
view: <run>\frames\0308_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 0 of 487 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -32 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Austria stands on the Emperor's r …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Ottoman Empire — gold flows, the compact binds bot]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [↳ 400g a turn]  [Buy Off Their Design (1080g) (1 DP + 1080g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1855 of 1855 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (54 labels)
```

```
#0309  scroll 1800 560 down 6  ->  ok
  (scrolled down 6 at (1800, 560))
view: <run>\frames\0309_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 208 of 530 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -32 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Austria stands on the Emperor's r …
   Relations with Austria stand at -32; an Open Borders needs -20.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1080g) (1 DP + 1080g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Unlikely](disabled: Relations with Austria stand at -32; an Open Borders needs -20.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1855 of 1855 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (54 labels)
```

```
#0310  scroll 1800 560 up 3  ->  ok
  (scrolled up 3 at (1800, 560))
view: <run>\frames\0310_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 135 of 523 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -32 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Austria stands on the Emperor's r …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [↳ 200g a turn]  [↳ 400g a turn]  [Buy Off Their Design (1080g) (1 DP + 1080g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1855 of 1855 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (54 labels)
```

```
#0311  scroll 1800 560 up 2  ->  ok
  (scrolled up 2 at (1800, 560))
view: <run>\frames\0311_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 41 of 487 px] ──
   THE CABINET — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -32 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Austria stands on the Emperor's r …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Ottoman Empire — gold flows, the compact binds bot]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [↳ 400g a turn]  [Buy Off Their Design (1080g) (1 DP + 1080g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1855 of 1855 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (54 labels)
```

```
#0312  click Licence  ->  ok
  (clicked at (1825, 513))
view: <run>\frames\0312_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 40 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1966 of 1966 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,932 (+1,615 next turn)
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
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0313  look  ->  ok
  (a fresh frame)
view: <run>\frames\0313_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1966 of 1966 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0314  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0314_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -37 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1966 of 1966 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0315  scroll 1800 560 down 15  ->  ok
  (scrolled down 15 at (1800, 560))
view: <run>\frames\0315_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 544 of 704 px] ──
   THE CABINET
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  -20 (Wary)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -83 (Hostile)]  [Austria  —  Peace  |  -27 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1966 of 1966 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0316  click Austria  ->  ok
  (clicked at (1825, 627))
view: <run>\frames\0316_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 0 of 445 px] ──
   THE CABINET — Austria
   DP: 4
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -27 (Wary) /  / "Austria maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Austria stands on the Emperor's roa …
   The compact already stands.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Ottoman Empire — gold flows, the compact binds bot](disabled: The compact already stands.)  [Buy Off Their Design (1080g) (1 DP + 1080g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1966 of 1966 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0317  scroll 1800 560 down 12  ->  ok
  (scrolled down 12 at (1800, 560))
view: <run>\frames\0317_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 252 of 440 px] ──
   THE CABINET — Austria
   DP: 4
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -27 (Wary) /  / "Austria maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Austria stands on the Emperor's roa …
   Relations with Austria stand at -27; an Open Borders needs -20.
   A vassalage of Austria needs a war (a dictated peace) or open borders and above — we stand at Peace.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Open Borders (1 DP)  —  Unlikely](disabled: Relations with Austria stand at -27; an Open Borders needs -20.)  [Propose Vassal (3 DP)](disabled: A vassalage of Austria needs a war (a dictated peace) or open borders and above — we stand)  [Declare War (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1966 of 1966 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0318  scroll 1800 560 up 3  ->  ok
  (scrolled up 3 at (1800, 560))
view: <run>\frames\0318_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 177 of 407 px] ──
   THE CABINET — Austria
   DP: 4
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -27 (Wary) /  / "Austria maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Austria stands on the Emperor's roa …
   Relations with Austria stand at -27; an Open Borders needs -20.
   A vassalage of Austria needs a war (a dictated peace) or open borders and above — we stand at Peace.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Buy Off Their Design (1080g) (1 DP + 1080g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Unlikely](disabled: Relations with Austria stand at -27; an Open Borders needs -20.)  [Propose Vassal (3 DP)](disabled: A vassalage of Austria needs a war (a dictated peace) or open borders and above — we stand)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1966 of 1966 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0319  scroll 1800 560 up 10  ->  ok
  (scrolled up 10 at (1800, 560))
view: <run>\frames\0319_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 0 of 445 px] ──
   THE CABINET — Austria
   DP: 4
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -27 (Wary) /  / "Austria maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Austria stands on the Emperor's roa …
   The compact already stands.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Ottoman Empire — gold flows, the compact binds bot](disabled: The compact already stands.)  [Buy Off Their Design (1080g) (1 DP + 1080g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1966 of 1966 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
map: unchanged (54 labels)
```

```
#0320  click Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0320_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Austria /  / "Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 40 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2012 of 2012 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,932 (+1,615 next turn)
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
   ► improve relations with Austria
map: unchanged (54 labels)
```

```
#0321  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0321_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 40 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: The blockade on our ports lifts @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 2t]
── BottomLeftUI (layer 0) [scrolled 2078 of 2078 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,932 (+1,615 next turn)
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
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (54 labels)
```

```
#0322  look  ->  ok
  (a fresh frame)
view: <run>\frames\0322_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2078 of 2078 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
map: unchanged (54 labels)
```

```
#0323  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0323_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 12
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 41 / 100
   Turn 13 — Late March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1832 of 1834 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,553 (+1,550 next turn)
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
   Sire — Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   • Sire — relations with Russia have improved significantly (+11 this turn).
   • Sire — the court of Russia takes up a new design: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 6,932g (+1,690 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 10 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 6 turns idle.
   - Murat — Frankfurt — 19,725 — 6 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 5 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   Wellesley — Normandy — screening force [partial]
   TURN EVENTS
   Holland loyalty 85 (-3): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -42.
   The court of Russia takes up a new design: The Gulf and the Straits.
   Relations with Russia have improved significantly (+11 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 40/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Austria. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Murat nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
   ► end turn
   ═══════════════════════════════════════
   TURN 13 BEGINS
   ═══════════════════════════════════════
   Income: 2587g | Charges of Empire: -217g | Other: +979g | Upkeep: -1728g | Net: +1621g
   Treasury: 8,553g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 16,000 -> 18,000
   Holland loyalty 82 (-3): satellite drift, relations with the lord
   Russia has downgraded relations with Austria: NON_AGGRESSION → OPEN_BORDERS.
   Murat's resentment of Ney has cooled with time.
   Bernadotte's resentment of Ney has cooled with time.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  36(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1434,578)  Castanos(1434,540)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Davout(1881,352)  Murat(1905,326)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  ?(1755,420)  12k(1711,420)  10k(1910,645)
```

```
#0324  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0324_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 41 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: Prussia Declares War! @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Ney arrived @(3519,64)]  [icon: Bavaria Eliminated! @(3561,64)]  [+22]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 1t]
── BottomLeftUI (layer 0) [scrolled 1902 of 1902 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,553 (+1,550 next turn)
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
   ► sponsor Russia against Sweden, 0 gold
   The licence is granted: France blesses Russia's design against Sweden and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► sponsor Austria against Ottoman, 0 gold
   The licence is granted: France blesses Austria's design against Ottoman and pledges non-interference. Talleyrand: "Consent costs nothing today, Sire. Tomorrow it is the most expensive thing we have sold — entering that war against them would be reneging."
   ► improve relations with Austria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Austria. (1 DP/turn)
   ► end turn
   ═══════════════════════════════════════
   TURN 13 BEGINS
   ═══════════════════════════════════════
   Income: 2587g | Charges of Empire: -217g | Other: +979g | Upkeep: -1728g | Net: +1621g
   Treasury: 8,553g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 16,000 -> 18,000
   Holland loyalty 82 (-3): satellite drift, relations with the lord
   Russia has downgraded relations with Austria: NON_AGGRESSION → OPEN_BORDERS.
   Murat's resentment of Ney has cooled with time.
   Bernadotte's resentment of Ney has cooled with time.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 13
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Austria would now join a league against us — relations −18. Russia pays her 200 gold a turn against us. The price to keep her out: Talleyrand brings her to −10 in 1 turn (1 DP); buying off her design costs 1,080 gold.
   • Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
   SITUATION
   France holds 28 regions. Treasury: 8,553g (+1,621 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 11 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 7 turns idle.
   - Murat — Frankfurt — 19,725 — 7 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 6 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   TURN EVENTS
   Holland loyalty 82 (-3): satellite drift, relations with the lord
   Murat's resentment of Ney has cooled with time.
   Bernadotte's resentment of Ney has cooled with time.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -18.
   THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 6 in hand); or let the war come, having been asked.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 41/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Austria and 4 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0325  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0325_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1235 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 13 — Late March 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Austria would now join a league against us — relations −18. Russia pays her 200 gold a turn against us. The price to keep her out: Tall …
   controls: [Pin]  [icon @(2143,296)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1902 of 1902 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 41/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Austria and 4 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0326  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0326_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [War with Russia — Russia, truce 1t]
── BottomLeftUI (layer 0) [scrolled 1902 of 1902 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 41/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Austria and 4 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0327  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0327_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -34 (Hostile)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1902 of 1902 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 41/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Austria and 4 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0328  scroll 1800 560 down 30  ->  ok
  (scrolled down 30 at (1800, 560))
view: <run>\frames\0328_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 648 of 688 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -82 (Hostile)]  [Austria  —  Peace  |  -18 (Wary)  [MISSION]]  [Sweden  —  Peace  |  -43 (Hostile)]  [Naples  —  Peace  |  -18 (Wary)]  [Hanover  —  Peace  |  -38 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1902 of 1902 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 41/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Austria and 4 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0329  click Hanover  ->  ok
  (clicked at (1825, 643))
view: <run>\frames\0329_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 90 px, 0 of 539 px] ──
   THE CABINET — Hanover
   DP: 6
   TALLEYRAND'S ASSESSMENT — HANOVER / Status: Peace   Relation: -38 (Hostile) /  / "Relations with Hanover remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. / Talleyrand: "Hanover stands on the Emperor's roads, Sire — The Protector of the Rhine (The Confederation …
   Relations with Hanover stand at -38; an Open Borders needs -20.
   A vassalage of Hanover needs a war (a dictated peace) or open borders and above — we stand at Peace.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Open Borders (1 DP)  —  Doubtful](disabled: Relations with Hanover stand at -38; an Open Borders needs -20.)  [Propose Vassal (3 DP)](disabled: A vassalage of Hanover needs a war (a dictated peace) or open borders and above — we stand)  [Declare War (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1902 of 1902 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 41/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Austria and 4 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0330  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0330_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1902 of 1902 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 41/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Austria and 4 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0331  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0331_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 13
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 42 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2211 of 2211 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,321 (+1,747 next turn)
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
   ► end turn
   ═══════════════════════════════════════
   TURN 14 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -78g | Other: +984g | Upkeep: -1728g | Net: +1768g
   Treasury: 10,321g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 18,000 -> 20,000
   Holland loyalty 79 (-3): satellite drift, relations with the lord
   The armistice between France and Russia has concluded. Peace declared — signed on the held line.
   Russia has downgraded relations with Austria: OPEN_BORDERS → PEACE.
map: unchanged (51 labels)
```

```
#0332  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0332_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 42 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Armistice Concluded @(3393,64)]  [icon: Envoy from Austria @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+24]
── BottomLeftUI (layer 0) [scrolled 1722 of 1722 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,321 (+1,747 next turn)
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
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 41/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Austria and 4 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 14 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -78g | Other: +984g | Upkeep: -1728g | Net: +1768g
   Treasury: 10,321g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 18,000 -> 20,000
   Holland loyalty 79 (-3): satellite drift, relations with the lord
   The armistice between France and Russia has concluded. Peace declared — signed on the held line.
   Russia has downgraded relations with Austria: OPEN_BORDERS → PEACE.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 14
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — peace with Russia is signed. The truce has ripened into peace, signed on the held line.
   • Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Russia.
   • Sire — our peace binds Russia for 5 more turns; then she may join a league (relations −31).
   SITUATION
   France holds 28 regions. Treasury: 10,321g (+1,768 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 12 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 8 turns idle.
   - Murat — Frankfurt — 19,725 — 8 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 7 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   TURN EVENTS
   Holland loyalty 79 (-3): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   An envoy from Austria has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -10.
   The armistice between France and Russia has concluded. Peace declared.
   Russia delivers a final demand to Sweden — it is refused. The ladder has one rung left.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Austria — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 42/100 [Murmurs]
   Europe has watched us 12 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0333  click Envoys  ->  ok
  (clicked at (3397, 18))
view: <run>\frames\0333_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Metternich (Schemer) of Austria /  / Proposes: Open Borders Agreement / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders /  / Metternich, with perfect politeness: "Austria offers terms; Vienna trusts France will find them — considered. Open the borders." /  / An unexpected overture. There may be hidden motives worth examining. /  / This offer will lapse a …
   controls: [Accept]  [Let Talleyrand haggle (1 DP)]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1722 of 1722 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,321 (+1,747 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 42/100 [Murmurs]
   Europe has watched us 12 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0334  click Accept  ->  ok
  (clicked at (1574, 687))
view: <run>\frames\0334_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 42 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Armistice Concluded @(3393,64)]  [icon: European Courts Concerned @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── BottomLeftUI (layer 0) [scrolled 1788 of 1788 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,321 (+1,887 next turn)
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
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria.
map: unchanged (51 labels)
```

```
#0335  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0335_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1257 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 14 — Early April 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — peace with Russia is signed. The truce has ripened into peace, signed on the held line. /   • Sire — 8 more quiet turns and the courts …
   controls: [Pin]  [icon @(2143,296)]  <Open the Laws>  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1788 of 1788 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria.
map: unchanged (51 labels)
```

```
#0336  click Open the Laws  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0336_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 816 px] ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Early April 1806 / The laws of the Empire — what each does, its price, its upkeep, and whether we may enact it now. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / Laws are acts of state, Sire: bought once, then paid in gold every turn. When the chest cannot pay, the heaviest upkeep lapses first; a lapsed law returns within 10 turns at half its price plus the arrea …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)  <Enact>  <Enact>  <Enact>  <Enact>  <Enact>  <Enact>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1788 of 1788 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria.
map: unchanged (51 labels)
```

```
#0337  click#6 Enact  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0337_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=['ledger'], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE COUNCIL OF STATE ASKS:
   "The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1 loyalty a turn in every one. 15 authority now, then 100 gold a turn. Authority 100 → 85 — the marshals' calm holds above 70. The treasury holds 10,321 gold. Enact it? (yes / no)"
   controls: [Enact the Code Abroad]  [Not now]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 42 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1855 of 1855 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,321 (+1,887 next turn)
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
   ► enact the Code Abroad
   The Council of State requests clarification...
map: unchanged (51 labels)
```

```
#0338  look  ->  ok
  (a fresh frame)
view: <run>\frames\0338_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (disabled)
open: screens=['ledger'], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── StrategicLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1855 of 1855 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria.
   ► enact the Code Abroad
   The Council of State requests clarification...
map: unchanged (51 labels)
```

```
#0339  click Enact the Code Abroad  ->  ok
  (clicked at (1829, 524))
view: <run>\frames\0339_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 42 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Armistice Concluded @(3393,64)]  [icon: European Courts Concerned @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Bernadotte arrived @(3519,64)]  [icon: Ney arrived @(3561,64)]  [+23]
── StrategicLedger (layer 50) [scrolled 0 of 816 px] ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Early April 1806 / The laws of the Empire — what each does, its price, its upkeep, and whether we may enact it now. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / Laws are acts of state, Sire: bought once, then paid in gold every turn. When the chest cannot pay, the heaviest upkeep lapses first; a lapsed law returns within 10 turns at half its price plus the arrea …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)  <Enact>  <Enact>  <Enact>  <Enact>  <Enact>  <Repeal>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1943 of 1943 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   10,321 (+1,762 next turn)
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > enact the Code Abroad confirmed
   The Code Abroad is in force — enacted for 15 authority. It costs 100 gold a turn from now on. Authority 100 → 85 — the marshals' calm holds above 70.
   [4/4 actions remaining]
map: unchanged (51 labels)
```

```
#0340  look  ->  ok
  (a fresh frame)
view: <run>\frames\0340_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1943 of 1943 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   The Council of State requests clarification...
   > enact the Code Abroad confirmed
   The Code Abroad is in force — enacted for 15 authority. It costs 100 gold a turn from now on. Authority 100 → 85 — the marshals' calm holds above 70.
   [4/4 actions remaining]
map: unchanged (51 labels)
```

```
#0341  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0341_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1943 of 1943 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   The Council of State requests clarification...
   > enact the Code Abroad confirmed
   The Code Abroad is in force — enacted for 15 authority. It costs 100 gold a turn from now on. Authority 100 → 85 — the marshals' calm holds above 70.
   [4/4 actions remaining]
map: unchanged (51 labels)
```

```
#0342  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0342_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 14
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 43 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1677 of 1678 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   12,087 (+1,769 next turn)
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
   MORNING DISPATCH — Turn 14
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — peace with Russia is signed. The truce has ripened into peace, signed on the held line.
   • Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Russia.
   • Sire — our peace binds Russia for 5 more turns; then she may join a league (relations −31).
   SITUATION
   France holds 28 regions. Treasury: 10,321g (+1,768 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 12 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 8 turns idle.
   - Murat — Frankfurt — 19,725 — 8 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 7 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   TURN EVENTS
   Holland loyalty 79 (-3): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   An envoy from Austria has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -10.
   The armistice between France and Russia has concluded. Peace declared.
   Russia delivers a final demand to Sweden — it is refused. The ladder has one rung left.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Austria — Open Borders Agreement
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 42/100 [Murmurs]
   Europe has watched us 12 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: 4 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria.
   ► enact the Code Abroad
   The Council of State requests clarification...
   > enact the Code Abroad confirmed
   The Code Abroad is in force — enacted for 15 authority. It costs 100 gold a turn from now on. Authority 100 → 85 — the marshals' calm holds above 70.
   [4/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -99g | Laws: -100g | Other: +1103g | Upkeep: -1728g | Net: +1766g
   Treasury: 12,087g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 20,000 -> 22,000
   Holland loyalty 77 (-2): satellite drift, relations with the lord
   Relations between France and Spain are deteriorating. Alliance may collapse in 2 turns.
   Russia declares war on Sweden — The Gulf and the Straits; declaring Finland.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  36(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1434,578)  Castanos(1434,540)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Davout(1881,352)  Murat(1905,326)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  12k(1716,420)  10k(1910,645)
```

```
#0343  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0343_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 43 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: Armistice Concluded @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 1680 of 1680 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   12,087 (+1,769 next turn)
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
   Berthier: "A treaty is a breathing space, Sire, not a rest. The next war is already being priced."
   ════════════════════════════════════
   Responding to Austria's proposal: accepted
   You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria.
   ► enact the Code Abroad
   The Council of State requests clarification...
   > enact the Code Abroad confirmed
   The Code Abroad is in force — enacted for 15 authority. It costs 100 gold a turn from now on. Authority 100 → 85 — the marshals' calm holds above 70.
   [4/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -99g | Laws: -100g | Other: +1103g | Upkeep: -1728g | Net: +1766g
   Treasury: 12,087g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 20,000 -> 22,000
   Holland loyalty 77 (-2): satellite drift, relations with the lord
   Relations between France and Spain are deteriorating. Alliance may collapse in 2 turns.
   Russia declares war on Sweden — The Gulf and the Straits; declaring Finland.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 15
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain would now join a league against us — relations −80. The price to keep her out: Talleyrand brings her to −10 in 8 turns (8 DP).
   • Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 12,087g (+1,766 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 13 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 9 turns idle.
   - Murat — Frankfurt — 19,725 — 9 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 8 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   TURN EVENTS
   Holland loyalty 77 (-2): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   Sire — Austria and France have signed the Open Borders Agreement.
   THE LAWS: Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
   THE LAWS: Austria enacts the Jäger Battalions — infantry drafts muster at +10 morale.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -2.
   BLOCKADE: Britain closes Sweden's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
   Relations with Russia have worsened significantly (-14 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 43/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0344  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0344_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1169 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 15 — Late April 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Britain would now join a league against us — relations −80. The price to keep her out: Talleyrand brings her to −10 in 8 turns (8 DP).  …
   controls: [Pin]  [icon @(2143,296)]  <Open the Laws>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1680 of 1680 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 43/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0345  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0345_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1680 of 1680 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 43/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0346  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0346_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1680 of 1680 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 43/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0347  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0347_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 687 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +10 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1680 of 1680 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 43/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0348  click_at 1829 444  ->  ok
  (clicked at (1829, 444) on @Button@9133 'Austria  —  Open Borders  |  -2 (Wary)  ' (Button, layer 110))
view: <run>\frames\0348_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 90 px, 0 of 647 px] ──
   THE CABINET — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Open Borders   Relation: -2 (Wary) /  / "Our borders with Austria are open, but trust remains shallow. A non-aggression pact would formalize the thaw." / Recommendation: Relations must improve before proposals will find purchase. / Talleyrand: "Austria stands on the Emperor's roads, Sire — The Protector of the Rhine (A German Crown Brought to Terms); The …
   The compact already stands.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Wary (+25 over 3 turns)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Ottoman Empire — gold flows, the compact binds bot](disabled: The compact already stands.)  [Buy Off Their Design (1152g) (1 DP + 1152g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1680 of 1680 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 43/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0349  click Cancel: Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0349_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 43 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: Armistice Concluded @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 1767 of 1767 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   12,087 (+1,769 next turn)
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
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (50 labels)
```

```
#0350  look  ->  ok
  (a fresh frame)
view: <run>\frames\0350_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1767 of 1767 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (50 labels)
```

```
#0351  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0351_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -2 (Wary)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1767 of 1767 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (50 labels)
```

```
#0352  scroll 1800 560 down 12  ->  ok
  (scrolled down 12 at (1800, 560))
view: <run>\frames\0352_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 506 of 706 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Hesse  —  Non-Aggression  |  0 (Neutral)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  -20 (Wary)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -80 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1767 of 1767 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (50 labels)
```

```
#0353  scroll 1800 560 up 5  ->  ok
  (scrolled up 5 at (1800, 560))
view: <run>\frames\0353_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 304 of 687 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Spain  —  Alliance  |  +10 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Saxony  —  Open Borders  |  -10 (Wary)]  [Hesse  —  Non-Aggression  |  0 (Neutral)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1767 of 1767 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (50 labels)
```

```
#0354  scroll 1800 560 up 5  ->  ok
  (scrolled up 5 at (1800, 560))
view: <run>\frames\0354_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 99 of 705 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -2 (Wary)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Alliance  |  +10 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1767 of 1767 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (50 labels)
```

```
#0355  scroll 1800 560 down 30  ->  ok
  (scrolled down 30 at (1800, 560))
view: <run>\frames\0355_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 647 of 687 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -80 (Hostile)]  [Russia  —  Peace  |  -45 (Hostile)]  [Sweden  —  Peace  |  -41 (Hostile)]  [Naples  —  Peace  |  -16 (Wary)]  [Hanover  —  Peace  |  -36 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1767 of 1767 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (50 labels)
```

```
#0356  click#1 Russia  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0356_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 46 px, 0 of 468 px] ──
   THE CABINET — Russia
   DP: 6
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Peace   Relation: -45 (Hostile) /  / "Relations with Russia remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate.
   The compact already stands.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Sweden — gold flows, the compact binds both ends (](disabled: The compact already stands.)  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1767 of 1767 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
map: unchanged (50 labels)
```

```
#0357  click Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0357_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Russia /  / "Sire, I shall begin efforts to improve relations with Russia. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 43 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1812 of 1812 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   12,087 (+1,769 next turn)
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
   ► improve relations with Russia
map: unchanged (50 labels)
```

```
#0358  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0358_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 43 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: Armistice Concluded @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 1878 of 1878 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   12,087 (+1,769 next turn)
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
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Russia. (1 DP/turn)
map: unchanged (50 labels)
```

```
#0359  look  ->  ok
  (a fresh frame)
view: <run>\frames\0359_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1878 of 1878 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Talleyrand's mission to Austria has been cancelled.
   ► improve relations with Russia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Russia. (1 DP/turn)
map: unchanged (50 labels)
```

```
#0360  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0360_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 15
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 44 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2145 of 2145 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,861 (+1,753 next turn)
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
   Income: 2590g | Charges of Empire: -121g | Laws: -100g | Other: +1133g | Upkeep: -1728g | Net: +1774g
   Treasury: 13,861g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 22,000 -> 24,000
   Holland loyalty 75 (-2): satellite drift, relations with the lord
map: unchanged (50 labels)
```

```
#0361  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0361_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 44 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+25]
── BottomLeftUI (layer 0) [scrolled 2120 of 2120 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,861 (+1,753 next turn)
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
   INTELLIGENCE
   Archduke Charles — Swabia — substantial force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   TURN EVENTS
   Holland loyalty 77 (-2): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   Sire — Austria and France have signed the Open Borders Agreement.
   THE LAWS: Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
   THE LAWS: Austria enacts the Jäger Battalions — infantry drafts muster at +10 morale.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Austria continue. Relations now at -2.
   BLOCKADE: Britain closes Sweden's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
   Relations with Russia have worsened significantly (-14 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 43/100 [Murmurs]
   Europe has watched us 13 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
   ► improve relations with Russia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Russia. (1 DP/turn)
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -121g | Laws: -100g | Other: +1133g | Upkeep: -1728g | Net: +1774g
   Treasury: 13,861g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 22,000 -> 24,000
   Holland loyalty 75 (-2): satellite drift, relations with the lord
   ════════════════════════════════════
   MORNING DISPATCH — Turn 16
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 13,861g (+1,774 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 14 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 10 turns idle.
   - Murat — Frankfurt — 19,725 — 10 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 9 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — large force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   TURN EVENTS
   Holland loyalty 75 (-2): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   THE LANDING: Wellesley has put 14,545 men ashore at Estonia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -36.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Naples may be ready to discuss improved relations. The diplomatic winds favor us.
   COALITION THREAT
   Threat: 44/100 [Murmurs]
   Europe has watched us 14 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0362  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0362_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1059 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 16 — Early May 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits. /  / SITUATION /   France holds 28 regions. Treasury: 13, …
   controls: [Pin]  [icon @(2143,296)]  <Open the Laws>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2120 of 2120 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 44/100 [Murmurs]
   Europe has watched us 14 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0363  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0363_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2120 of 2120 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 44/100 [Murmurs]
   Europe has watched us 14 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0364  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0364_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 16
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 17 — Late May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1858 of 1860 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   15,568 (+1,687 next turn)
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
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Austria
   Talleyrand's mission to Austria has been cancelled.
   ► improve relations with Russia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Russia. (1 DP/turn)
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -121g | Laws: -100g | Other: +1133g | Upkeep: -1728g | Net: +1774g
   Treasury: 13,861g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 22,000 -> 24,000
   Holland loyalty 75 (-2): satellite drift, relations with the lord
   ════════════════════════════════════
   MORNING DISPATCH — Turn 16
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 13,861g (+1,774 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 14 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 10 turns idle.
   - Murat — Frankfurt — 19,725 — 10 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 9 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — large force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   TURN EVENTS
   Holland loyalty 75 (-2): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   THE LANDING: Wellesley has put 14,545 men ashore at Estonia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -36.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Naples may be ready to discuss improved relations. The diplomatic winds favor us.
   COALITION THREAT
   Threat: 44/100 [Murmurs]
   Europe has watched us 14 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -142g | Laws: -100g | Other: +1087g | Upkeep: -1728g | Net: +1707g
   Treasury: 15,568g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 24,000 -> 25,000
   Holland loyalty 73 (-2): satellite drift, relations with the lord
   Relations between France and Spain have collapsed: Alliance → Defensive Alliance.
   Russia has downgraded relations with Naples: NON_AGGRESSION → OPEN_BORDERS.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1928,114)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  36(1416,737)  20(1971,161)  18(1939,143)  15(2234,635)  12(1593,294)  10(1111,753)  11(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1434,578)  Castanos(1434,540)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Davout(1881,352)  Murat(1905,326)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  12k(1716,420)  10k(1910,645)
```

```
#0365  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0365_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 1877 of 1877 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   15,568 (+1,687 next turn)
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
   TURN EVENTS
   Holland loyalty 75 (-2): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   THE LANDING: Wellesley has put 14,545 men ashore at Estonia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -36.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, I believe Naples may be ready to discuss improved relations. The diplomatic winds favor us.
   COALITION THREAT
   Threat: 44/100 [Murmurs]
   Europe has watched us 14 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -142g | Laws: -100g | Other: +1087g | Upkeep: -1728g | Net: +1707g
   Treasury: 15,568g
   Actions refreshed: 4/4
   Garrison at Munich reinforced: 24,000 -> 25,000
   Holland loyalty 73 (-2): satellite drift, relations with the lord
   Relations between France and Spain have collapsed: Alliance → Defensive Alliance.
   Russia has downgraded relations with Naples: NON_AGGRESSION → OPEN_BORDERS.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 17
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — relations between France and Spain have collapsed: Alliance → Defensive Alliance.
   • Sire — Paget has put 8,080 men ashore at Estonia.
   • Sire — Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 15,568g (+1,707 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 15 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 11 turns idle.
   - Murat — Frankfurt — 19,725 — 11 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 10 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — large force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   TURN EVENTS
   Holland loyalty 73 (-2): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 8,080 men ashore at Estonia.
   Karelia passes from Sweden to Russia.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -27.
   Relations between France and Spain have collapsed: Alliance → Defensive Alliance.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0366  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0366_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1103 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 17 — Late May 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — relations between France and Spain have collapsed: Alliance → Defensive Alliance. /   • Sire — Paget has put 8,080 men ashore at Estonia. …
   controls: [Pin]  [icon @(2143,296)]  <Open the Laws>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1877 of 1877 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0367  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0367_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1877 of 1877 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0368  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0368_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -2 (Wary)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1877 of 1877 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0369  scroll 1800 560 down 4  ->  ok
  (scrolled down 4 at (1800, 560))
view: <run>\frames\0369_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 161 of 687 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -2 (Wary)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Spain  —  Defensive Alliance  |  +2 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -10 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1877 of 1877 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0370  click#1 Spain  ->  ok
  (clicked at (1825, 524))
view: <run>\frames\0370_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 156 px, 0 of 606 px] ──
   THE CABINET — Spain
   DP: 6
   TALLEYRAND'S ASSESSMENT — SPAIN / Status: Defensive Alliance   Relation: +2 (Neutral) /  / "Our alliance with Spain holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Relations must improve before proposals will find purchase. /  / KEY FACTORS /   + Base willingness (+10) /   + Diplomatic skill advantage (+10) /   + Our diplomatic reputation (+4) /    …
   Relations with Spain stand at 2; an Alliance needs 40.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Alliance (2 DP)  —  Hopeless](disabled: Relations with Spain stand at 2; an Alliance needs 40.)  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An defensive alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1877 of 1877 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0371  scroll 1800 560 up 5  ->  ok
  (scrolled up 5 at (1800, 560))
view: <run>\frames\0371_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 156 px, 0 of 606 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1877 of 1877 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0372  look  ->  ok
  (a fresh frame)
view: <run>\frames\0372_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 156 px, 0 of 606 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1877 of 1877 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0373  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0373_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1877 of 1877 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0374  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0374_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 17
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2164 of 2164 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   17,260 (+1,671 next turn)
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
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -162g | Laws: -100g | Other: +1092g | Upkeep: -1728g | Net: +1692g
   Treasury: 17,260g
   Actions refreshed: 4/4
   Holland loyalty 71 (-2): satellite drift, relations with the lord
   Territorial rivalry between Britain and Russia grows.
   Russia has downgraded relations with Naples: OPEN_BORDERS → PEACE.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1858,136)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Britain(1454,251)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  36(1416,737)  20(1971,161)  18(1945,118)  15(2234,635)  12(1593,294)  10(1111,753)  12(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1434,578)  Castanos(1434,540)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Davout(1881,352)  Murat(1905,326)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  12k(1716,420)  10k(1910,645)
```

```
#0375  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0375_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: A Moment of History: The Throne of Holland @(3393,64)]  [icon: Britain Joins Offensive! @(3435,64)]  [icon: Russia Declares War! @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+27]
── BottomLeftUI (layer 0) [scrolled 1744 of 1744 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   17,260 (+1,671 next turn)
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
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 15 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -162g | Laws: -100g | Other: +1092g | Upkeep: -1728g | Net: +1692g
   Treasury: 17,260g
   Actions refreshed: 4/4
   Holland loyalty 71 (-2): satellite drift, relations with the lord
   Territorial rivalry between Britain and Russia grows.
   Russia has downgraded relations with Naples: OPEN_BORDERS → PEACE.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 18
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia.
   SITUATION
   France holds 28 regions. Treasury: 17,260g (+1,692 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 16 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 12 turns idle.
   - Murat — Frankfurt — 19,725 — 12 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 11 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — large force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   TURN EVENTS
   Holland loyalty 71 (-2): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   Uleaborg passes from Sweden to Britain.
   THE LAWS: Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
   Finland passes from Sweden to Russia.
   THE LAWS: Austria enacts the New Infantry Regulations — +5 morale from every drill.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -18.
   REVANCHE: Sweden will not forgive Russia the loss of Uleaborg and 2 more provinces. A new design hardens in their court.
   The court of Sweden takes up a new design: Revanche.
   The court of Russia eases over The Gulf and the Straits — an ultimatum is now the length of its tether.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 16 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0376  click Envoys  ->  ok
  (clicked at (3401, 18))
view: <run>\frames\0376_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 46 px] ──
   A MOMENT OF HISTORY — Early June 1806 / The Throne of Holland — Admiral Ver Huell, for the deputation of the States General lays a letter before the Emperor. / A moment of history, Sire: a decision the record sets before you — two answers, each priced below, or Not Now to set it aside. It waits this turn and the next; left unanswered, it takes the second answer for you. / Historically the Dutch de …
   controls: [Crown Louis]  [Keep the Republic]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1744 of 1744 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   17,260 (+1,671 next turn)
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
   Europe has watched us 16 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0377  click Crown Louis  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0377_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 1832 of 1832 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   17,260 (+1,559 next turn)
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
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 71 → 81; its autonomy drift -2 → +1 a turn; tribute 75% → 50% (-112 gold a turn); the ports shut against Britain stay 2 of 26; 1 diplomatic point (you hold 6).
map: unchanged (50 labels)
```

```
#0378  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0378_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 1301 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 18 — Early June 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 le …
   controls: [Pin]  [icon @(2143,296)]  <Open the Laws>  [Open Envoys (1)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1832 of 1832 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 71 → 81; its autonomy drift -2 → +1 a turn; tribute 75% → 50% (-112 gold a turn); the ports shut against Britain stay 2 of 26; 1 diplomatic point (you hold 6).
map: unchanged (50 labels)
```

```
#0379  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0379_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1832 of 1832 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 71 → 81; its autonomy drift -2 → +1 a turn; tribute 75% → 50% (-112 gold a turn); the ports shut against Britain stay 2 of 26; 1 diplomatic point (you hold 6).
map: unchanged (50 labels)
```

```
#0380  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0380_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 18
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2055 of 2055 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   18,823 (+1,545 next turn)
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
   Income: 2590g | Charges of Empire: -183g | Laws: -100g | Other: +984g | Upkeep: -1728g | Net: +1563g
   Treasury: 18,823g
   Actions refreshed: 4/4
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1856,136)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Britain(1454,251)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  36(1416,737)  20(1971,161)  18(1945,118)  15(2234,635)  12(1593,294)  10(1111,753)  13(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1434,578)  Castanos(1434,540)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Davout(1881,352)  Murat(1905,326)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  12k(1716,420)  10k(1910,645)
```

```
#0381  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0381_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 1876 of 1876 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   18,823 (+1,545 next turn)
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
   TURN EVENTS
   Holland loyalty 71 (-2): satellite drift, relations with the lord
   DIPLOMATIC EVENTS
   Uleaborg passes from Sweden to Britain.
   THE LAWS: Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
   Finland passes from Sweden to Russia.
   THE LAWS: Austria enacts the New Infantry Regulations — +5 morale from every drill.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -18.
   REVANCHE: Sweden will not forgive Russia the loss of Uleaborg and 2 more provinces. A new design hardens in their court.
   The court of Sweden takes up a new design: Revanche.
   The court of Russia eases over The Gulf and the Straits — an ultimatum is now the length of its tether.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - The Cabinet — A Moment of History
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 16 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. Bound for now by a fresh peace: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 71 → 81; its autonomy drift -2 → +1 a turn; tribute 75% → 50% (-112 gold a turn); the ports shut against Britain stay 2 of 26; 1 diplomatic point (you hold 6).
   ► end turn
   ═══════════════════════════════════════
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -183g | Laws: -100g | Other: +984g | Upkeep: -1728g | Net: +1563g
   Treasury: 18,823g
   Actions refreshed: 4/4
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Europe has watched us 17 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 18,823g (+1,563 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 17 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 13 turns idle.
   - Murat — Frankfurt — 19,725 — 13 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 12 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — large force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   DIPLOMATIC EVENTS
   Ostrobothnia passes from Sweden to Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -10.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 17 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0382  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0382_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -2 (Wary)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1876 of 1876 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 17 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0383  scroll 1800 560 down 30  ->  ok
  (scrolled down 30 at (1800, 560))
view: <run>\frames\0383_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 648 of 688 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -76 (Hostile)]  [Russia  —  Peace  |  -10 (Wary)  [MISSION]]  [Sweden  —  Peace  |  -37 (Hostile)]  [Naples  —  Peace  |  -12 (Wary)]  [Hanover  —  Peace  |  -32 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1876 of 1876 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 17 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0384  click#1 Russia  ->  ok
  (clicked at (1825, 523))
view: <run>\frames\0384_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 178 px, 0 of 626 px] ──
   THE CABINET — Russia
   DP: 6
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Peace   Relation: -10 (Wary) /  / "Russia maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: Talleyrand recommends: Propose Open Borders /  / KEY FACTORS /   + Base willingness (+35) /   + Diplomatic skill advantage (+6) /   + Diplomat personality (+5) /   - Curr …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Improve Relations  —  Hostile → Wary (+35, 4 turns)]  [Propose Open Borders (1 DP)  —  Uncertain — a counter is likely]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Ottoman Empire — gold flows, the compact binds bot]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1876 of 1876 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 17 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0385  click Cancel: Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0385_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 1964 of 1964 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   18,823 (+1,545 next turn)
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
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (50 labels)
```

```
#0386  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0386_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -2 (Wary)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1964 of 1964 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (50 labels)
```

```
#0387  scroll 1800 560 down 30  ->  ok
  (scrolled down 30 at (1800, 560))
view: <run>\frames\0387_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 648 of 688 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -76 (Hostile)]  [Russia  —  Peace  |  -10 (Wary)]  [Sweden  —  Peace  |  -37 (Hostile)]  [Naples  —  Peace  |  -12 (Wary)]  [Hanover  —  Peace  |  -32 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1964 of 1964 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (50 labels)
```

```
#0388  click#1 Britain  ->  ok
  (clicked at (1825, 483))
view: <run>\frames\0388_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 112 px, 0 of 447 px] ──
   THE CABINET — Britain
   DP: 6
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: Peace   Relation: -76 (Hostile) /  / "Relations with Britain remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. / Talleyrand: "Britain stands on the Emperor's r …
   Relations with Britain stand at -76; an Open Borders needs -20.
   A vassalage of Britain needs a war (a dictated peace) or open borders and above — we stand at Peace.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Propose Open Borders (1 DP)  —  Hopeless](disabled: Relations with Britain stand at -76; an Open Borders needs -20.)  [Propose Vassal (3 DP)](disabled: A vassalage of Britain needs a war (a dictated peace) or open borders and above — we stand)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1964 of 1964 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
map: unchanged (50 labels)
```

```
#0389  click Improve Relations  ->  ok
  (clicked at (1825, 456))
view: <run>\frames\0389_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Britain /  / "Sire, I shall begin efforts to improve relations with Britain. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2009 of 2009 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   18,823 (+1,545 next turn)
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
   ► improve relations with Britain
map: unchanged (50 labels)
```

```
#0390  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0390_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 2075 of 2075 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   18,823 (+1,545 next turn)
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
   Talleyrand begins efforts to improve relations with Britain. (1 DP/turn)
map: unchanged (50 labels)
```

```
#0391  look  ->  ok
  (a fresh frame)
view: <run>\frames\0391_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2075 of 2075 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Talleyrand's mission to Russia has been cancelled.
   ► improve relations with Britain
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Britain. (1 DP/turn)
map: unchanged (50 labels)
```

```
#0392  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0392_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 19
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 45 / 100
   Turn 20 — Early July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1748 of 1749 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   20,373 (+1,531 next turn)
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
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
   Answering The Throne of Holland: Crown Louis
   The Throne of Holland — Crown Louis: Holland becomes Autonomous: loyalty 71 → 81; its autonomy drift -2 → +1 a turn; tribute 75% → 50% (-112 gold a turn); the ports shut against Britain stay 2 of 26; 1 diplomatic point (you hold 6).
   ► end turn
   ═══════════════════════════════════════
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -183g | Laws: -100g | Other: +984g | Upkeep: -1728g | Net: +1563g
   Treasury: 18,823g
   Actions refreshed: 4/4
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Europe has watched us 17 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 18,823g (+1,563 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 17 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 13 turns idle.
   - Murat — Frankfurt — 19,725 — 13 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 12 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — large force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   DIPLOMATIC EVENTS
   Ostrobothnia passes from Sweden to Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -10.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 17 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► improve relations with Britain
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Britain. (1 DP/turn)
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -201g | Laws: -100g | Other: +989g | Upkeep: -1728g | Net: +1550g
   Treasury: 20,373g
   Actions refreshed: 4/4
   Territorial rivalry between Britain and Russia grows.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1856,136)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Britain(1454,251)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  36(1416,737)  20(1971,161)  18(1945,118)  15(2234,635)  12(1593,294)  10(1111,753)  14(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1434,578)  Castanos(1434,540)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Davout(1881,352)  Murat(1905,326)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  12k(1716,420)  10k(1910,645)
```

```
#0393  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0393_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 45 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 2120 of 2120 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   20,373 (+1,531 next turn)
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
   France holds 28 regions. Treasury: 18,823g (+1,563 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 17 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 13 turns idle.
   - Murat — Frankfurt — 19,725 — 13 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 12 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — large force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   DIPLOMATIC EVENTS
   Ostrobothnia passes from Sweden to Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Russia continue. Relations now at -10.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 17 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► improve relations with Britain
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Britain. (1 DP/turn)
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -201g | Laws: -100g | Other: +989g | Upkeep: -1728g | Net: +1550g
   Treasury: 20,373g
   Actions refreshed: 4/4
   Territorial rivalry between Britain and Russia grows.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 20
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march.
   SITUATION
   France holds 28 regions. Treasury: 20,373g (+1,550 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 18 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 14 turns idle.
   - Murat — Frankfurt — 19,725 — 14 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 13 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — large force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -67.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 18 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0394  click Dispatch  ->  ok
  (clicked at (407, 18))
view: <run>\frames\0394_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=['dispatch'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DispatchView (layer 50) [scrolled 0 of 883 px] ──
   MORNING DISPATCH
   ════════════════════════════════════ /   MORNING DISPATCH — Turn 20 — Early July 1806 /   Chief of Staff Berthier reporting / ════════════════════════════════════ / What changed overnight, before you spend a single order. Press R to reread it any time. /  / Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 le …
   controls: [Pin]  [icon @(2143,296)]  <Open the Laws>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2120 of 2120 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 18 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0395  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0395_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2120 of 2120 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 18 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0396  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0396_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   The Emperor's Designs — no road proclaimed — three roads, one choice that cannot be undone
   Treaties (9)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [The Emperor's Designs — the roads of the Empire]  [Formable Nations — states that could yet exist]  [Austria  —  Open Borders  |  -2 (Wary)]  [Prussia  —  Non-Aggression  |  +3 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2120 of 2120 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 18 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0397  scroll 1800 560 down 30  ->  ok
  (scrolled down 30 at (1800, 560))
view: <run>\frames\0397_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 648 of 688 px] ──
   THE CABINET
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (6)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  -20 (Wary)]  [Britain  —  Peace  |  -67 (Hostile)  [MISSION]]  [Russia  —  Peace  |  -10 (Wary)]  [Sweden  —  Peace  |  -36 (Hostile)]  [Naples  —  Peace  |  -11 (Wary)]  [Hanover  —  Peace  |  -31 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2120 of 2120 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 18 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0398  click Sweden  ->  ok
  (clicked at (1825, 563))
view: <run>\frames\0398_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 24 px, 0 of 579 px] ──
   THE CABINET — Sweden
   DP: 6
   TALLEYRAND'S ASSESSMENT — SWEDEN / Status: Peace   Relation: -36 (Hostile) /  / "Relations with Sweden remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Russia — gold flows, the compact binds both ends (]  [↳ Licence — a free hand, no gold]  [↳ 200g a turn]  [↳ 400g a turn]  [Buy Off Their Design (1152g) (1 DP + 1152g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2120 of 2120 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 18 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0399  click Buy Off Their Design  ->  ok
  (clicked at (1825, 638))
view: <run>\frames\0399_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Improving Relations...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: Prussia Declares War! @(3519,64)]  [icon: Bernadotte arrived @(3561,64)]  [+26]
── BottomLeftUI (layer 0) [scrolled 2230 of 2230 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   19,221 (+1,545 next turn)
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
   ► buy off Sweden
   Sweden's design — Revanche — is bought off for 1152 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (50 labels)
```

```
#0400  look  ->  ok
  (a fresh frame)
view: <run>\frames\0400_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2230 of 2230 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
   ► buy off Sweden
   Sweden's design — Revanche — is bought off for 1152 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (50 labels)
```

```
#0401  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0401_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 1881 of 1882 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   21
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   20,770 (+1,530 next turn)
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
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 17 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Massena grows impatient, Sire. He will require action soon."
   ════════════════════════════════════
   ► Talleyrand, cancel mission with Russia
   Talleyrand's mission to Russia has been cancelled.
   ► improve relations with Britain
   Directing Talleyrand: start mission
   Talleyrand begins efforts to improve relations with Britain. (1 DP/turn)
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -201g | Laws: -100g | Other: +989g | Upkeep: -1728g | Net: +1550g
   Treasury: 20,373g
   Actions refreshed: 4/4
   Territorial rivalry between Britain and Russia grows.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 20
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march.
   SITUATION
   France holds 28 regions. Treasury: 20,373g (+1,550 by the accounts) — the chest could found the Grand Quartier Général — 9,000g (the Laws tab: T, then 8)   Open the Laws
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 85 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 29,621 — 18 turns idle.
   - Soult — Limousin — 29,265 — Awaiting orders.
   - Davout — Frankfurt — 22,407 — Awaiting orders.
   - Ney — Franche-Comte — 19,954 — 14 turns idle.
   - Murat — Frankfurt — 19,725 — 14 turns idle.
   - Bernadotte — Franche-Comte — 16,027 — Awaiting orders. Trust:40
   - Lannes — Rhineland — 14,877 — 13 turns idle.
   - Napoleon — Rhineland — 8,409 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Swabia — large force [partial]
   Archduke John — Munich — substantial force [partial]
   Castanos — Guyenne — small force [partial]
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Britain continue. Relations now at -67.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 18 quiet turns. At this pace the courts consult on turn 25 and declare on turn 28: Britain and 4 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
   ► buy off Sweden
   Sweden's design — Revanche — is bought off for 1152 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► end turn
   ═══════════════════════════════════════
   TURN 21 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -206g | Laws: -100g | Other: +993g | Upkeep: -1728g | Net: +1549g | Spent: 1152g
   Treasury: 20,770g
   Actions refreshed: 4/4
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2032,316)  Spain(1277,819)  Sweden(1856,136)  Saxony(2068,404)  Austria(2035,556)  France(1596,525)  Britain(1454,251)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)  Hanover(1741,350)
map pieces: 100(1396,395)  45(1374,592)  36(1416,737)  20(1971,161)  18(1945,118)  15(2234,635)  12(1593,294)  10(1111,753)  15(1927,239)  5(1804,784)  Archduke Charles(1859,444)  Lannes(1814,418)  Napoleon(1838,376)  ?(1434,578)  Castanos(1434,540)  Soult(1600,497)  Ney(1800,497)  Bernadotte(1825,471)  ?(1901,540)  Archduke John(1901,501)  Davout(1881,352)  Murat(1905,326)  Massena(1910,589)  ?(1959,376)  ?(1862,529)  ?(1937,560)  25k(1595,468)  12k(1551,454)  ?(1769,580)  12k(1716,420)  10k(1910,645)
```

```
#0402  quit  ->  ok
  (the engine quits)
view: <run>\frames\0402_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1881 of 1882 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -206g | Laws: -100g | Other: +993g | Upkeep: -1728g | Net: +1549g | Spent: 1152g
   Treasury: 20,770g
   Actions refreshed: 4/4
map: unchanged (50 labels)
```

