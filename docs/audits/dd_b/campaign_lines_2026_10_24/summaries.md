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
   ✓ The war office answers.  ·  127.0.0.1:8007
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
#0002  click Begin the 1805 Campaign  ->  ok
  (clicked at (490, 439))
view: <run>\frames\0002_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
#0003  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0003_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
#0004  click The Emperor  ->  ok
  (clicked at (1825, 572))
view: <run>\frames\0004_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 1880 px] ──
   THE CABINET — THE EMPEROR'S DESIGNS
   DP: 5
   "Three roads, Sire — what the Empire will be. One proclamation decides it, and it cannot be undone."
   Your own aims, Sire, not the courts'. A road asks a construction, then a seal; hold both and the peace that seals it can be the Decisive Peace. Proclaiming costs 2 DP and 1 administrative action and cannot be undone.
   No road is proclaimed. Three roads — one proclamation, and it cannot be undone.
   Road I — The Protector of the Rhine (The Act of Confederation) /     ✓ Bavaria must stand with France /     Proclaiming takes 2 diplomatic points and 1 administrative action; Europe's alarm +8; relations: Austria −10, Prussia −10. /     • The Confederation of the Rhine (the construction) — 0 of 3 courts under the Emperor's protection; to be held 4 end turns /         Three of Bavaria, Hesse, Saxon …
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Proclaim Road I — The Act of Confederation]  [Proclaim Road II — The Schönbrunn Proclamation]  [Proclaim Road III — The Blockade of the British Isles]  [Back]  [Cancel]
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
#0005  click Back  ->  ok
  (clicked at (1774, 740))
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
#0006  click Formable Nations  ->  ok
  (clicked at (1825, 612))
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
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
#0007  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
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
#0008  click War with the Third Coalition  ->  ok
  (clicked at (3429, 996))
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) [scrolled 0 of 442 px] ──
   WAR WITH THE THIRD COALITION
   BR
   0
   FR
   The ledger of one war — its score, its fronts, and the price of peace. Negotiate opens the table, where every court signs for itself. /  / The War with the Third Coalition: nothing taken yet on either side. / With: Britain + Austria + Russia /  / Score Breakdown   trend = stable /   Territory:  0/40 /   Battles:    0/15 /   Decisive:   0/15 /   Capital:    0/30 /   Campaign:   0/10 /   Blood:      …
   controls: [icon @(3139,276)]  [Negotiate with Britain]  [Negotiate with Austria]  [Negotiate with Russia]  [Open Settlement]  [Request Terms](disabled: No court names terms this early in a war, Sire. (2 turns remaining.))
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
#0009  click Open Settlement  ->  ok
  (clicked at (2791, 784))
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 91 px, 0 of 486 px] ──
   This draft will not carry as it stands. / the War with the Third Coalition — the table with Austria + Britain + Russia - Whole-war settlement / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria -8/50, Britain -8/50, Russia -8/50. / Treasury 800 gold: committed 0 / reserve 500 / remaining 300 / Sire, this settlement of the War wi …
   The table /   * Austria ▸ - Holding out (-8/50) White peace /       Blocker: Settlement legitimacy /       Metternich regrets that Austria must remain… unconvinced — it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. /       + Add demand /   * Britain ▸ - Holding out (-8/50) White peace /       Blocker: Settlement legitimacy /       …
   Austria:
   Britain:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, a white peace for the War with the Third Coalition — the table with Austria + Britain + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still n …
   controls: <Austria ▸>  <+ Add demand>  <Britain ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Drop Austria]  [Demand more of Britain]  [Ease Britain]  [Drop Britain]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  <Grant>  <Decline>  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1477 of 1477 px] ──
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
   Opening settlement review for Britain
map: unchanged (53 labels)
```

```
#0010  click Back Out  ->  ok
  (clicked at (2250, 969))
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with the Third Coalition
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
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
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0011  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1543 of 1543 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Opening settlement review for Britain
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0012  key T  ->  ok
  (pressed T)
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 618 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Late September 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1543 of 1543 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Opening settlement review for Britain
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0013  click LAWS  ->  ok
  (clicked at (2123, 283))
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 750 px] ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Late September 1805 / The laws of the Empire — what each does, its price, its upkeep, and whether we may enact it now. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / Laws are acts of state, Sire: bought once, then paid in gold every turn. When the chest cannot pay, the heaviest upkeep lapses first; a lapsed law returns within 10 turns at half its price plus the ar …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)  <Enact>  <Enact>  <Enact>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1543 of 1543 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Opening settlement review for Britain
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0014  click ADMIRALTY  ->  ok
  (clicked at (2049, 283))
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 816 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late September 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). / The camp, Sire: 40,000 men on the Channel coast, 2 turns at war with Britain, stage a descent — no order. Britain recalls her fleet and her blockade on you lifts; a won Diversion can open the Strait for up to 2 turns …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1543 of 1543 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Opening settlement review for Britain
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
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
   0 →
   T:0
   controls: [THIRD COALITION  ▸]  [War with the Third Coalition]
── BottomLeftUI (layer 0) [scrolled 1543 of 1543 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ─────────────────────────────────────
   Opening settlement review for Britain
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (53 labels)
```

```
#0016  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0016_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 136 px] ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 4,503 casualties, 49,497 remaining /     Massena: 5,725 casualties, 36,275 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%) /     Archduke Charles: "France pays …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2008 of 2008 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,436 (+922 next turn)
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
   Your unratified settlement draft with Britain (1 clause) was set aside at turn's end.
   Bavaria's petition over Tyrol lapses with the settlement it was filed against, set aside at turn's end.
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -286g | Other: +1295g | Upkeep: -2654g | Net: +636g
   Treasury: 1,436g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,472 troops
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
   42,000 → 36,275
   54,000 → 49,497
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 1896 of 1896 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,436 (+922 next turn)
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
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -286g | Other: +1295g | Upkeep: -2654g | Net: +636g
   Treasury: 1,436g
   Actions refreshed: 4/4
   Supply shortage at Tyrol: Archduke Charles loses 1,472 troops
   Supply shortage at Tyrol: Archduke John loses 594 troops
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
   France holds 28 regions. Treasury: 1,436g (+922 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 70% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 36,275 — Awaiting orders.
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
#0018  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   4,682
   3,683
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 36,275
   54,000 → 49,497
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 1
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1896 of 1896 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0019  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0019_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   AUSTRIA LOSSES
   5,725
   4,503
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 36,275
   54,000 → 49,497
   Berthier: “Stalemate. Massena and Archduke Charles glare at each other across the field.” / Archduke Charles: "France pays full price for every Austrian mile now."
   THE GREAT BATTLE OF MILAN
   MILAN · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1896 of 1896 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0020  key T  ->  ok
  (pressed T)
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1896 of 1896 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0021  click LAWS  ->  ERROR: no visible control's text holds "LAWS"
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1896 of 1896 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0022  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1896 of 1896 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,436 (+922 next turn)
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
#0023  click_at 3635 18  ->  ok
  (clicked at (3635, 18) on MenuBtn  (Button, layer 75))
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1896 of 1896 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0024  click Save Game  ->  ok
  (clicked at (1829, 407))
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
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
   1,436 (+922 next turn)
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
   Saving game...
   Game saved successfully.
map: unchanged (59 labels)
```

```
#0025  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   THE CABINET
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   An unanswered envoy awaits your reply. Reopen Envoys before starting a new diplomatic action.
   controls: [icon: Close (Esc) @(2075,284)]  [Open Envoys (3)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Saving game...
   Game saved successfully.
map: unchanged (59 labels)
```

```
#0026  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Saving game...
   Game saved successfully.
map: unchanged (59 labels)
```

```
#0027  key T  ->  ok
  (pressed T)
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 838 px] ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early October 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 100 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location: …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Saving game...
   Game saved successfully.
map: unchanged (59 labels)
```

```
#0028  click LAWS  ->  ok
  (clicked at (2123, 283))
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 706 px] ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Early October 1805 / The laws of the Empire — what each does, its price, its upkeep, and whether we may enact it now. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /  / The Grand Quartier Général  Berthier's Imperial Headquarters, expanded 1805–07 /   Berthier's headquarters grown into a true general staff: one more order carried each day. /   • +1 order of the day …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)  <Enact>  <Enact>  <Enact>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Saving game...
   Game saved successfully.
map: unchanged (59 labels)
```

```
#0029  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Swabia
   0 →
   T:1
   controls: [THIRD COALITION  ▸]  [War for Swabia]
── BottomLeftUI (layer 0) [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Saving game...
   Game saved successfully.
map: unchanged (59 labels)
```

```
#0030  click_at 3635 18  ->  ok
  (clicked at (3635, 18) on MenuBtn  (Button, layer 75))
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
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
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Saving game...
   Game saved successfully.
map: unchanged (59 labels)
```

```
#0031  click Load Game  ->  ok
  (clicked at (1829, 461))
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['load', 'war_status_panel (not modal)'], region_panel=no
── LoadDialog (layer 101) ──
   LOAD GAME
   controls: [quicksave (Turn 2)]  [Autosave - Turn 2 (Turn 2)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1962 of 1962 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
   Saving game...
   Game saved successfully.
map: unchanged (59 labels)
```

```
#0032  click quicksave  ->  ok
  (clicked at (1829, 414))
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
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
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,436 (+922 next turn)
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
   Game loaded successfully.
   Loaded: quicksave
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,436g (+922 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 70% of French forces (an estimate — 3 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 36,275 — Awaiting orders.
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
map: unchanged (59 labels)
```

```
#0033  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (59 labels)
```

```
#0034  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,436 (+922 next turn)
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
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (59 labels)
```

```
#0035  key T  ->  ok
  (pressed T)
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: 't' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,436 (+922 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   [Teulie,]  (Tab)
   t
   controls: [+]  [−]  [—]  [Execute]  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (59 labels)
```

```
#0036  click LAWS  ->  ERROR: no visible control's text holds "LAWS"
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: 't' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (59 labels)
```

```
#0037  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: 't' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,436 (+922 next turn)
   Inf:
   82,375
   Cav:
   16,750
   Art:
   10,600
   t
   controls: [+]  [−]  [—]  [Execute]  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (59 labels)
```

```
#0038  quit  ->  ok
  (the engine quits)
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: 't' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (59 labels)
```

